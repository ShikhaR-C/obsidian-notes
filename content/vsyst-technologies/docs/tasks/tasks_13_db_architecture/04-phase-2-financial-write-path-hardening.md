# Phase 2 — Financial write-path hardening

**Outcome:** Every money mutation is atomic, serialized per relation, race-free, and schema-validated — defects D1–D5, D12 closed. The existing reconcilers demote from "repair crew" to "guardrail that proves zero drift". No new collections yet (that's Phase 4); no API contract changes.

**Effort:** 3–5 dev-days (about half is tests).

**Pre-requisites:** Phase-1 integrity scan dispositions (drift/duplicates must be cleaned or explained before unique indexes land). Governance default Q7 (additive `models/` changes allowed).

## 2.1 Test harness gains a replica set (coordinate with tasks_12)

Transactions require a replica set; the tasks_12 harness uses standalone `mongodb-memory-server` per file.

- [ ] In `test/database.js`, switch to `MongoMemoryReplSet.create({ replSet: { count: 1 } })` (single-node replset — transactions work, startup cost ~equal).
- [ ] Run the existing api_v3 suite green before proceeding; upstream this change to the tasks_12 plan (its Phase 1 §"harness hardening" is the natural home).

## 2.2 Money helpers — `api_v3/services/money.js` (D4, arithmetic layer)

- [ ] Implement + unit-test: `toPaise(rs)` (validates ≤2dp, returns int), `toRupees(p)`, `addRs(...xs)` / `subRs(a,b)` (via paise), `mulRateQty(rate, qty)` (documented rounding mode matching current invoice behavior — `Math.round` at total, residue to `inv_round_amt`, see `api_v3/services/invs.js:284-287`).
- [ ] Rewrite float arithmetic in `calcttl` (`api_v3/services/dealer_custs.js:105-126`), `updateCrDr` amount math, cumulative-balance folds (`calcFYCumulativeBal:56-73`) to route through these helpers. Storage stays rupees; the *arithmetic* becomes exact.

## 2.3 Transactional posting core (D1, D3)

- [ ] New `api_v3/services/tx.js`: `withMoneyTxn(relationKey, fn)` — wraps `mongoose.startSession()` + `withTransaction` semantics with explicit retry on `TransientTransactionError` / `UnknownTransactionCommitResult` (bounded, e.g. 3 attempts + jitter). (New file in `api_v3` rather than editing frozen `helpers/transactions.js`; that helper keeps serving `veh_reqs` untouched.)
- [ ] **Per-relation serialization**: first statement inside every money transaction:
  ```js
  await DealerCusts.updateOne({ _id: relId }, { $inc: { post_seq: 1 } }, { session });
  ```
  Two concurrent transactions on the same relation now write-conflict; the loser retries and re-evaluates its guards. Add `post_seq: Number` to `models/dealer_custs.js` (additive).
- [ ] Wrap, one flow per PR, passing `session` into **every** contained read/write:
  1. **Invoice creation** `createInvNew` (`api_v3/services/invs.js:1120-1246`): SO link + `invs` insert(s) + rollup update — one transaction (guards D1).
  2. **Voucher approval** `updateVocStatus` (`api_v3/services/voc_msts.js:387-479`): move the AdvDep overdraw guard *inside* the transaction, after the `post_seq` bump; approval flip + rollup + `persistAdvDep` all on the session (kills the D3 TOCTOU).
  3. **Voucher create/delete** paths that post to rollups; **order create** credit check (`api_v3/services/order_msts.js:786-799`): sum-exposure + insert inside the transaction after the `post_seq` bump — concurrent same-relation orders serialize.
- [ ] Read paths (statements, balances) stay sessionless — no read contention.

## 2.4 Atomic rollups + uniqueness (D2, D12)

- [ ] Replace both `updateCrDr` implementations (`voc_msts.js:256-301`, `invs.js:1007-1050`) with one shared, atomic upsert:
  ```js
  await MonthCrdrs.findOneAndUpdate(
    { cust_id, dealer_id, month: monthKey },
    { $inc: { [side === "DR" ? "drttl" : "crttl"]: amtRs } },   // amtRs from money.js
    { upsert: true, session }
  );
  ```
  (Keeps rupee storage for reader compatibility; `$inc` float residue is bounded and the nightly reconciler proves/corrects it until Phase 4 makes rollups fully derived.)
- [ ] Unique index `{ cust_id: 1, dealer_id: 1, month: 1 }` on `month_crdrs` (models addition) — duplicates cleaned first per Phase-1 scan.
- [ ] **One-adjustment-per-deposit as a constraint** (D3's second half): partial unique index on `voc_msts` — `{ ref_voc_id: 1 }`, `partialFilterExpression: { ref_voc_id: { $exists: true } }` (confirm against Phase-1 data whether multi-adjustment is ever legal; if legal-but-bounded, enforce in the transaction instead and index non-uniquely).

## 2.5 Schema validation (D5)

- [ ] `$jsonSchema` validators via `collMod` on `invs`, `voc_msts`, `month_crdrs`, `dealer_custs`: required money fields `bsonType: ["double","int"]` + range ≥ 0 where business-true, `voc_type`/`pay_type`/`inv_status`/`cust_type` enums locked, `pay_mode` enum (cash/cheque/card/fleetcard/neft/rtgs/upi — confirm list from data first: `db.voc_msts.distinct("pay_mode")`).
- [ ] `validationLevel: "moderate"` (legacy docs readable; all new/updated docs must comply), `validationAction: "error"`.
- [ ] Apply via a committed `scripts/apply_validators.js` (idempotent, per-env) so dev/testing/prod and the memory-server harness (run it in test setup) stay identical.
- [ ] Mirror the enums in the Mongoose schemas (additive `enum:` on existing fields) so validation errors surface in code, not just at the server.

## 2.6 Reconciler becomes a scheduled guardrail

- [ ] Wrap the existing recompute logic (`checkMonthDRCR`, `dbpopulatemonthcrdrcollection`, `advDepBalance`) in `scripts/reconcile_fin.js` with `--dry-run` (report only) and `--repair` modes; dry-run exits non-zero on any drift.
- [ ] Schedule nightly dry-run on one EC2 instance via crontab (no queue infra exists — crontab is deliberate minimalism), output to CloudWatch/log file; alert on non-zero. After Phase 2 the expected steady-state is **zero drift** — any hit is a bug report, not noise.
- [ ] Add drift-check invocation to the release-gate script (tasks_12 Phase 6).

## 2.7 Tests (tasks_12 idiom: supertest + seeded memory replset)

- [ ] **Concurrency regression pins**: `Promise.all` of two concurrent voucher approvals drawing the same AdvDep → exactly one succeeds; two concurrent invoice creations same relation/month → rollup equals exact sum; two concurrent orders exhausting one credit limit → second blocked.
- [ ] **Atomicity**: force an abort mid-`createInvNew` (e.g. duplicate-key on second insert) → no invoice, no SO link, no rollup delta (all-or-nothing).
- [ ] **Precision**: property-style test — N random 2dp amounts summed via `money.js` equals paise-exact expectation; validator rejects sub-paise writes.
- [ ] Seed factories: credit-capped relation + approved AdvDep pair already suggested by tasks_07/tasks_12 — reuse, don't fork.

## Phase 2 checklist

- [ ] Test harness on `MongoMemoryReplSet`; suite green; tasks_12 notified
- [ ] `money.js` landed + unit tests; `calcttl`/rollup math routed through it
- [ ] `tx.js` with transient-error retry; `post_seq` serialization field live
- [ ] Invoice-create, voucher-approve/create/delete, order-credit-check wrapped in transactions (one PR each)
- [ ] Shared atomic `updateCrDr` with `$inc` + upsert; duplicate rollups cleaned; unique index `{cust,dealer,month}` live
- [ ] AdvDep one-adjustment constraint enforced (index or in-txn)
- [ ] Validators applied via `scripts/apply_validators.js` in all envs incl. test setup
- [ ] `scripts/reconcile_fin.js` nightly dry-run scheduled + alerting; wired into release gate
- [ ] Concurrency/atomicity/precision regression tests green in CI-less local gate (`yarn test:full`)
