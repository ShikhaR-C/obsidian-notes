# Phase 2 — Financial write-path hardening

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Partly done by a different route: API PR #36 (merged 2026-08-31) replaced the read-modify-write poster with one idempotent recompute-from-source rebuild and made duplicate month rows harmless without an index. None of this phase's own mechanisms exists yet — no transactions, `post_seq`, unique index, validators, replica-set harness or reconciler script. Of 7 sections: 3 🟡 (§2.2, §2.4, §2.7), 4 ⬜; two new tasks owned here, T13-N1 and T13-N3 (rows at the end). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Outcome:** Every money mutation is atomic, serialized per relation, race-free, and schema-validated — defects D1–D5, D12 closed. The existing reconcilers demote from "repair crew" to "guardrail that proves zero drift". No new collections yet (that's Phase 4); no API contract changes.

**Effort:** 3–5 dev-days (about half is tests).

**Pre-requisites:** Phase-1 integrity scan dispositions (drift/duplicates must be cleaned or explained before unique indexes land). Governance default Q7 (additive `models/` changes allowed).

## 2.1 Test harness gains a replica set (coordinate with tasks_12)

**Status (2026-10-01):** ⬜ to do — api:`test/database.js:5,67` still starts a standalone `MongoMemoryServer`; two TRANSACTIONAL suites stay `describe.skip` (api:`test/api_v3/collections/so_msts/index.test.js:438`, api:`test/api_v3/collections/vehs/veh_reqs.test.js:389`).

Transactions require a replica set; the tasks_12 harness uses standalone `mongodb-memory-server` per file.

- [ ] In `test/database.js`, switch to `MongoMemoryReplSet.create({ replSet: { count: 1 } })` (single-node replset — transactions work, startup cost ~equal).
- [ ] Run the existing api_v3 suite green before proceeding; upstream this change to the tasks_12 plan (its Phase 1 §"harness hardening" is the natural home).

## 2.2 Money helpers — `api_v3/services/money.js` (D4, arithmetic layer)

**Status (2026-10-01):** 🟡 a paise module exists on the v4 read side only (api:`api_v4/lib/money.js`); `api_v3/services/money.js` does not exist, and v3's month totals still sum floats with `toFixed(2)` (api:`api_v3/services/ledger_window.js:400-413`). `calcttl` itself is gone — folded into `monthLedgerTotals` by `13dcb6f`. See T13-N1.

- [ ] Implement + unit-test: `toPaise(rs)` (validates ≤2dp, returns int), `toRupees(p)`, `addRs(...xs)` / `subRs(a,b)` (via paise), `mulRateQty(rate, qty)` (documented rounding mode matching current invoice behavior — `Math.round` at total, residue to `inv_round_amt`, see `api_v3/services/invs.js:284-287`).
- [ ] Rewrite float arithmetic in `calcttl` (`api_v3/services/dealer_custs.js:105-126`), `updateCrDr` amount math, cumulative-balance folds (`calcFYCumulativeBal:56-73`) to route through these helpers. Storage stays rupees; the *arithmetic* becomes exact.

## 2.3 Transactional posting core (D1, D3)

**Status (2026-10-01):** ⬜ to do — no `api_v3/services/tx.js` and no `post_seq` (grep → none); `runInTransaction` is used only by `veh_reqs` (api:`api_v3/services/veh_reqs.js:249`). The order-create path named here also takes its order number by read-then-write (T13-N3).

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

**Status (2026-10-01):** 🟡 one shared rebuild replaced the three copies (`13dcb6f`), but it recomputes the month from source and `$set`s it rather than `$inc` (api:`api_v3/services/ledger_window.js:439-481`), outside any transaction. Duplicate rows are collapsed on each rebuild and read once (`:453-461`, `6375f86`), yet the unique index is still absent (api:`models/month_crdrs.js:17,24-27`), as is any `ref_voc_id` index or constraint (api:`models/voc_msts.js:83-85`).

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

**Status (2026-10-01):** ⬜ to do — no `$jsonSchema`, `collMod` or `scripts/apply_validators.js`; `pay_mode` is a free `String` (api:`models/voc_msts.js:49-52`).

- [ ] `$jsonSchema` validators via `collMod` on `invs`, `voc_msts`, `month_crdrs`, `dealer_custs`: required money fields `bsonType: ["double","int"]` + range ≥ 0 where business-true, `voc_type`/`pay_type`/`inv_status`/`cust_type` enums locked, `pay_mode` enum (cash/cheque/card/fleetcard/neft/rtgs/upi — confirm list from data first: `db.voc_msts.distinct("pay_mode")`).
- [ ] `validationLevel: "moderate"` (legacy docs readable; all new/updated docs must comply), `validationAction: "error"`.
- [ ] Apply via a committed `scripts/apply_validators.js` (idempotent, per-env) so dev/testing/prod and the memory-server harness (run it in test setup) stay identical.
- [ ] Mirror the enums in the Mongoose schemas (additive `enum:` on existing fields) so validation errors surface in code, not just at the server.

## 2.6 Reconciler becomes a scheduled guardrail

**Status (2026-10-01):** ⬜ to do — no `scripts/reconcile_fin.js`; the release gate runs fixtures freshness and the three suites only (api:`scripts/release_gate.sh`). The recompute logic lives on as service code (`checkMonthDRCR` → `rebuildMonthBucket`, api:`api_v3/services/dealer_custs.js:95-96`).

- [ ] Wrap the existing recompute logic (`checkMonthDRCR`, `dbpopulatemonthcrdrcollection`, `advDepBalance`) in `scripts/reconcile_fin.js` with `--dry-run` (report only) and `--repair` modes; dry-run exits non-zero on any drift.
- [ ] Schedule nightly dry-run on one EC2 instance via crontab (no queue infra exists — crontab is deliberate minimalism), output to CloudWatch/log file; alert on non-zero. After Phase 2 the expected steady-state is **zero drift** — any hit is a bug report, not noise.
- [ ] Add drift-check invocation to the release-gate script (tasks_12 Phase 6).

## 2.7 Tests (tasks_12 idiom: supertest + seeded memory replset)

**Status (2026-10-01):** 🟡 idempotency, duplicate and roll-forward pins exist (api:`test/api_v3/collections/dealer_custs/month_rebuild.test.js`, `duplicate_buckets.test.js`, `year_rollforward.test.js`, api:`test/api_v3/collections/voc_msts/advdep.test.js`, api:`test/api_v3/collections/order_msts/credit_window.test.js`); no concurrency or atomicity test (grep → none); the only precision test is the v4 rule's (api:`test/api_v4/lib/money.test.js`).

- [ ] **Concurrency regression pins**: `Promise.all` of two concurrent voucher approvals drawing the same AdvDep → exactly one succeeds; two concurrent invoice creations same relation/month → rollup equals exact sum; two concurrent orders exhausting one credit limit → second blocked.
- [ ] **Atomicity**: force an abort mid-`createInvNew` (e.g. duplicate-key on second insert) → no invoice, no SO link, no rollup delta (all-or-nothing).
- [ ] **Precision**: property-style test — N random 2dp amounts summed via `money.js` equals paise-exact expectation; validator rejects sub-paise writes.
- [ ] Seed factories: credit-capped relation + approved AdvDep pair already suggested by tasks_07/tasks_12 — reuse, don't fork.

## Phase 2 checklist

**Status (2026-10-01):** 0 of 9 done, two partly (a mark on each item); none flipped.

- [ ] Test harness on `MongoMemoryReplSet`; suite green; tasks_12 notified — **2026-10-01:** ⬜ standalone mongod (`test/database.js:5`)
- [ ] `money.js` landed + unit tests; `calcttl`/rollup math routed through it — **2026-10-01:** 🟡 v4-only `api_v4/lib/money.js`; `calcttl` folded into `monthLedgerTotals`
- [ ] `tx.js` with transient-error retry; `post_seq` serialization field live — **2026-10-01:** ⬜ neither exists
- [ ] Invoice-create, voucher-approve/create/delete, order-credit-check wrapped in transactions (one PR each) — **2026-10-01:** ⬜ no transactions on these paths
- [ ] Shared atomic `updateCrDr` with `$inc` + upsert; duplicate rollups cleaned; unique index `{cust,dealer,month}` live — **2026-10-01:** 🟡 one shared idempotent rebuild (`$set`, not `$inc`); duplicates collapsed per rebuild; no unique index
- [ ] AdvDep one-adjustment constraint enforced (index or in-txn) — **2026-10-01:** ⬜ no constraint
- [ ] Validators applied via `scripts/apply_validators.js` in all envs incl. test setup — **2026-10-01:** ⬜ no validators
- [ ] `scripts/reconcile_fin.js` nightly dry-run scheduled + alerting; wired into release gate — **2026-10-01:** ⬜ no reconciler script
- [ ] Concurrency/atomicity/precision regression tests green in CI-less local gate (`yarn test:full`) — **2026-10-01:** ⬜ no concurrency or atomicity tests; the gate is no longer CI-less (`.github/workflows/test.yml`)

## New tasks — from the app v2 / API v4 review (2026-10-01)

Rows owned by this doc; the folder's full table is in [00-overview.md](./00-overview.md).

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| T13-N1 | 🆕 One money rule: before §2.2 adds `api_v3/services/money.js`, decide a single home for the integer-paise rule the v4 read models already use (an additive `helpers/` file needs the user's approval), and settle the open Daily Summary O-6 decision (amount-entered lines) first | The v4 rule rounds quantity to the millilitre and each line half-up to the paisa (api:`api_v4/lib/money.js:1-22,58-59`), confirmed by the user 2026-09-15/16; v3 rounds each line with float `toFixed(2)` (api:`models/invs.js:57-75`) — a second paise module would recreate the two-rule problem screen spec 02 O-3 found | API | S | O-6 decision (screen spec 02); Q7 |
| T13-N3 | 🆕 Make PO and SO numbering atomic: take the next number with `findOneAndUpdate({$inc})` before the insert, and add unique indexes on (`cust_id`, `order_no`) and (`dealer_id`, `slip_no`) after a duplicate check on existing data | `order_no` is the customer's `cust_podgt` + 1 — read, incremented in JS and written back with `$set` after the insert (api:`api_v3/services/order_msts.js:768-786,843-847`); `slip_no` works the same way on `dealer_sodgt` (api:`api_v3/services/so_msts.js:43-58`); neither number has a unique index (api:`models/order_msts.js:31`, api:`models/so_msts.js:34`), so two concurrent orders of one customer, or SOs of one dealer, can take the same number. Invoice numbers are collision-free (ObjectId-derived, api:`api_v3/services/invs.js:60,322,483,542`) | API | S | duplicate scan (§1.6 in Phase 1); Q7 |
