# Phase 4 — The `fin_txns` posting ledger

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Not started: no `fin_txns` model, composer, flag, backfill or reconciler exists (`git grep fin_txns` → none) — 0 of 6 sections (all ⬜). Two v4 facts matter when it starts: the v4 Customers read model is a second reader of `month_crdrs` with its own FY fold (T13-N2, owned here — row at the end), and an integer-paise rule already exists on the v4 read side (T13-N1). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Outcome:** The "structured DB for better querying" deliverable: an append-only, immutable, validated posting ledger that every financial event writes through (inside the Phase-2 transactions), backfilled from history, proven by reconciliation, and serving statements/TCS-TDS/exports/balances behind a feature flag. `month_crdrs` and `adv_dep` become provably-rebuildable materialized views of it (D4 root fix, D9 closed).

**Effort:** 5–8 dev-days — the largest phase; land it in the four stages below, each independently shippable.

**Pre-requisites:** Phase 2 complete (transactions + money helpers are what `fin_txns` writes ride on). Created in the `oms_fin` namespace from birth (`useDb("oms_fin")`) so Phase 5 never has to move it.

## 4.1 Schema & constraints (stage 1)

**Status (2026-10-01):** ⬜ to do — neither api:`models/fin_txns.js` nor `api_v3/services/fin_txns.js` exists.

`models/fin_txns.js` (additive; registered on the fin namespace handle):

```js
{
  dealer_id, cust_id, rel_id,          // ObjectIds; rel_id = dealer_custs._id
  side:      "DR" | "CR",
  amount_p:  Long,                      // integer paise, > 0 — sign lives in `side`
  src: {
    type:    "INV" | "VOC" | "OB" | "REV" | "GATEWAY",   // OB=opening balance, REV=reversal; GATEWAY reserved (Q4)
    id:      ObjectId,                  // invs._id / voc_msts._id / original fin_txn for REV
    subtype: String,                    // inv_type or voc_type: PRODUCT/GST/CASH_REIMBURSE/DrNote/CrNote/PInv/PAdvice/TCS/TDS/AdvDep/ADVDEP_ADJ
  },
  posting_dt: Date,                     // business effective date (inv_dt / pay_dt / eff_dt)
  fy: "2026-27", month: "2026-07",      // pre-computed keys (IST fin-year, Apr–Mar) — group-bys never do timezone math again
  idem_key: String,                     // sha1(src.type + src.id + side + subtype) — unique
  note: String, created_by: ObjectId, createdAt
}
```

Indexes: `{rel_id:1, posting_dt:1}`, `{dealer_id:1, cust_id:1, fy:1, month:1}`, `{idem_key:1}` unique, `{src.id:1}`.

- [ ] Model + `$jsonSchema` validator (strict on this collection: required fields, `amount_p` integer ≥ 1, enums locked, `additionalProperties: false`).
- [ ] **Immutability**: validator can't block updates, so enforce with (a) code review rule — the model exports no update/delete helpers, (b) the app's DB user on `oms_fin` gets a custom role without `update`/`remove` on `fin_txns` (Phase-5 users make this real; until then, (a) + tests), (c) corrections are `REV` postings referencing the original.
- [ ] Posting composer `api_v3/services/fin_txns.js`: `postingsForInvoice(inv)`, `postingsForVoucher(voc)`, `reversalFor(txn)` — pure functions, unit-tested, single place where business docs map to ledger legs (invoice → DR `inv_total_amt`; approved CREDIT/SALE voucher → CR; DEBIT voucher → DR; AdvDep deposit → CR into the AdvDep sub-stream `subtype:"AdvDep"`; AdvDep adjustment → paired postings per current `advDepBalance` math, `api_v3/services/voc_msts.js:309-329`).

## 4.2 Dual-write behind a flag (stage 2)

**Status (2026-10-01):** ⬜ to do — no `FIN_TXNS_WRITE` flag. The `counters`-doc config pattern has grown (`app_features` joined `diesel_limit` — api:`helpers/appFeatures.js:34`), but `version_gate` exists only on the unmerged branch of API PR #34.

- [ ] Env/`counters`-doc flag `FIN_TXNS_WRITE` (the `counters` collection already serves as the config store — same mechanism as `version_gate`).
- [ ] Inside each Phase-2 transaction, after the business writes: `FinTxns.insertMany(postings, { session })`. Duplicate `idem_key` inside a retried transaction is impossible (aborted txns leave nothing); across accidental double-calls it's the unique index doing its job — treat `E11000` there as idempotent success.
- [ ] Voucher **un-approval/edit/delete** flows (they exist — approval is a Boolean that can flip back): emit `REV` postings rather than deleting, keeping append-only truth. Map every mutation path found in `updateVocStatus`/delete handlers.
- [ ] Ship with flag ON in testing env for a full release cycle; nightly reconciler (§4.4) compares.

## 4.3 Backfill (stage 3)

**Status (2026-10-01):** ⬜ to do — no `scripts/backfill_fin_txns.js` (the only backfill script is `scripts/backfill_advdep_seed_opening.js`); the `calcttl` this section mirrors is now `monthLedgerTotals` (api:`api_v3/services/ledger_window.js:379-414`, `13dcb6f`).

`scripts/backfill_fin_txns.js` — resumable (checkpoints by relation), batched, idempotent by `idem_key`:

- [ ] Emit `OB` postings from each relation's earliest `cust_bal` snapshot (`dealer_custs.cust_bal[]`).
- [ ] Walk `invs` (all statuses that post today — mirror `calcttl`'s inclusion rules exactly, `api_v3/services/dealer_custs.js:105-126`) and **approved** `voc_msts` in `posting_dt` order, composing through the same `postingsForInvoice/Voucher` functions as live writes — one mapping, zero drift-by-construction.
- [ ] Amounts: `toPaise()` on stored 2-dp floats — the Phase-1 precision scan already confirmed/cleaned sub-paise anomalies.
- [ ] Run on testing env against a prod snapshot first; record row counts + total DR/CR paise per relation.

## 4.4 Reconciliation proves the ledger (gate for stage 4)

**Status (2026-10-01):** ⬜ to do — no `scripts/reconcile_fin.js`.

Extend `scripts/reconcile_fin.js`:

- [ ] Per relation: `Σ fin_txns` grouped by month **==** recomputed-from-source `month_crdrs` math **==** stored `month_crdrs`; AdvDep stream balance **==** `advDepBalance()` **==** stored `adv_dep`; FY-end cumulative **==** next FY's `cust_bal` opening.
- [ ] Statement parity: for N sampled relations, old JS-merge statement vs ledger statement — identical rows/amounts/running balance.
- [ ] **Zero drift across two consecutive nightly runs with dual-write ON = the gate** to flip reads.

## 4.5 Read paths flip (stage 4, flag `FIN_TXNS_READ`)

**Status (2026-10-01):** ⬜ to do — the read paths are unchanged (`getDealerCustomerAccount`, api:`api_v3/services/dealer_custs.js:443-501`); add the v4 Customers read model (`ledgerByCust`, `openingBalance`) to the list (T13-N2).

- [ ] `getDealerCustomerAccount` (`dealer_custs.js:584-642`) → single indexed range scan + running balance in one pass.
- [ ] `getCurrBalance`/`calcFYCumulativeBal` → ledger `$group` on `{fy, month}` keys (or keep reading `month_crdrs` — now a proven view; either way delete the JS float folds).
- [ ] TCS/TDS reports (`TCSTDS/index.js`) → `$group` over `subtype: TCS|TDS` on `fy`/`month` keys — the `$month`+timezone pipelines retire.
- [ ] Excel/PDF exports (`Accounts/excel`, Puppeteer templates) read the same statement service — screens, exports, emails can no longer disagree.
- [ ] `month_crdrs` maintenance: keep the Phase-2 `$inc` (cheap, transactional) but nightly rebuild-from-ledger comparison continues; `adv_dep`/`persistAdvDep` recompute now sources the ledger stream.
- [ ] API responses stay byte-compatible (rupee numbers via `toRupees`) — contract tests from tasks_12 fixtures pin this.

## 4.6 Cutover & cleanup

**Status (2026-10-01):** ⬜ to do.

- [ ] Flag rollout: testing (2 weeks dual-run) → prod canary instance → both instances; old read path stays flag-recoverable for one full release, then dead code is removed.
- [ ] Retire the duplicated `updateCrDr` in `invs.js` (Phase 2 already unified; here its callers all post through the composer).
- [ ] Document the ledger contract in `dzzlo_oms_api/docs/` (fields, immutability, how to add a new posting type — the Q4 gateway will use `src.type:"GATEWAY"` + `idem_key` = gateway txn id).

## Phase 4 checklist

**Status (2026-10-01):** 0 of 7 done (a mark on each item); none flipped.

- [ ] `fin_txns` model + strict validator + indexes live in `oms_fin`; immutability enforced (role plan + no-update API + tests) — **2026-10-01:** ⬜
- [ ] Posting composer pure-functions unit-tested against every inv/voc subtype incl. reversals — **2026-10-01:** ⬜
- [ ] Dual-write ON in testing; transactional insert with idempotent `E11000` handling — **2026-10-01:** ⬜
- [ ] Backfill run: counts + DR/CR totals recorded; re-runnable proven — **2026-10-01:** ⬜
- [ ] Reconciler extended; two consecutive zero-drift nights before read flip — **2026-10-01:** ⬜
- [ ] Statements, balances, TCS/TDS, exports on ledger reads behind `FIN_TXNS_READ`; response parity pinned by fixture tests — **2026-10-01:** ⬜
- [ ] Canary → full rollout; old path removed after one stable release; ledger contract documented — **2026-10-01:** ⬜

## New tasks — from the app v2 / API v4 review (2026-10-01)

Rows owned by this doc; the folder's full table is in [00-overview.md](./00-overview.md).

| ID     | Task                                                                                                                                                                                                                                                                                                                                      | Why (evidence)                                                                                                                                                                                        | Project | Size | Depends on        |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | ----------------- |
| T13-N2 | 🆕 Put the v4 read models on this plan's read-path list: the Customers read model reads `month_crdrs` directly and keeps its own FY fold, opening balance and outstanding-order aggregates, so Phase 2's unique-index clean-up, Phase 4's read flip and Phase 5's move of `month_crdrs` to `oms_fin` must include it and its parity tests | api:`api_v4/readmodels/customers.js:270-347` (`ledgerByCust`, `$first` per IST month), `:476-570` (outstanding orders, opening balance); parity suites in api:`test/api_v4/screens/customers.test.js` | API     | S    | X-V4-2 (tasks_02) |
