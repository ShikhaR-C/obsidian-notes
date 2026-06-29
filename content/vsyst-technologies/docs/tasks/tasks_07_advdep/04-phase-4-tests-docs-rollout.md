# Phase 4 — Tests, docs & rollout

**Goal:** Keep the test suite green with the new `AdvDep` type, add coverage for the new accounting behaviour, document the type, and roll out safely. Runs **alongside** Phases 1–3 (write each test with its phase).

**Risk:** Low.

---

## Step 4.1 — Update voc_type validation regexes (do this with Phase 1)

These test validators whitelist the known `voc_type` values; AdvDep must be added or AdvDep-bearing responses will fail validation.

**File:** `dzzlo_oms_api/test/api_v3/helper/collections/voc_msts/index.js:57`

```js
// before: /^DrNote|CrNote|PInv|PAdvice|TCS|TDS$/
/^DrNote|CrNote|PInv|PAdvice|TCS|TDS|AdvDep$/;
```

**File:** `dzzlo_oms_api/test/api_v3/features/accounts/index.test.js`

```js
// ~L127-129 (ledger transaction types):
/^PRODUCT|CASH_REIMBURSE|PAdvice|PInv|DrNote|CrNote|TCS|TDS|AdvDep$/
// ~L166-168 (payment voc_types):
/^PAdvice|PInv|DrNote|CrNote|TCS|TDS|AdvDep$/
```

> There is a mirror copy at `test/202405_v2/helper/collections/voc_msts/index.js:57`. That tree is the legacy v2 suite; update it only if it's still run in CI. (Per AI.md, active work is api_v3.)

---

## Step 4.2 — New API tests (with Phases 2 & 3)

Add to `dzzlo_oms_api/test/api_v3/collections/voc_msts/index.test.js` (which already creates DrNote/PInv vouchers ~L113-115) and/or the accounts feature suite.

**Phase 2 — AdvDep approval:**

- Create an AdvDep voucher (`POST /voc_msts/a/custvoc`, `voc_type:'AdvDep'`, `pay_status:false`) → asserts it persists with `voc_type:'AdvDep'`.
- Approve it (`updateVocStatus`, `pay_status:true`) → assert:
  - `dealer_custs.adv_dep` increased by the amount.
  - `month_crdrs` for the period is **unchanged** (the key regression guard).
- Regression: approve a normal on-account (`PInv`) voucher → `month_crdrs.crttl` increases; `adv_dep` unchanged.

**Phase 3 — adjustment:**

- Seed an approved AdvDep (so `adv_dep = 1000`). Create a linked adjustment (`voc_type:'PInv'`, `ref_voc_id` set, remarks contains `"On account payment."`), approve it →
  - `adv_dep` decreased by the amount.
  - `month_crdrs.crttl` increased by the amount.
- Overdraw: adjustment amount > `adv_dep` → expect 400 `"Adjustment exceeds available advance deposit"`.

**Factory:** `test/api_v3/temp/seed/v3/factories/createSeedvouchers.js` doesn't hardcode `voc_type`, so no change is required; pass `voc_type:'AdvDep'` from the test where needed. Optionally add an `advDepVoucher` factory helper.

Run a focused suite:

```bash
yarn test --testPathPattern="test/api_v3/collections/voc_msts"
yarn test --testPathPattern="test/api_v3/features/accounts"
```

---

## Step 4.3 — App checks

- `yarn lint` and `yarn test` in `dzzlo_oms_app`.
- Manual simulator passes per the Verification sections in Phases 1–3.
- Confirm no snapshot/label tests assume the closed set of voc_types.

---

## Step 4.4 — Docs

- `dzzlo_oms_api/docs/AI_CONTEXT.md` (and/or a `docs/MODELS` entry if present): document `AdvDep` and that approval routes it to `dealer_custs.adv_dep`, not `month_crdrs`.
- Optional `models/voc_msts.js:65` comment: append `AdvDep` to the type list (a `models/` edit — batch with any other approved comment touch-ups; see overview §6).
- Consider a `/journal` or `/strategy` entry per the repo's `.ai/commands` convention summarizing the advance-deposit accounting model.

---

## Step 4.5 — Rollout / version gating

- **Backend tolerates the value regardless of app version** (no enum; create path is type-agnostic). Deploy API (Phases 1–2) **before** the app build that adds the selector.
- The `PayOnAc` selector is the only customer-visible change; the dealer approval branch (Phase 2, Step 2.3) must be in the **same or earlier** app build the dealer runs — otherwise a dealer on an old build sees "No conditions matched" for AdvDep vouchers. Gate the customer-side selector behind a min-app-version check if dealer and customer builds roll out independently.
- Order of deploy: **API (1+2) → dealer app (approval branch) → customer app (selector).**

---

## Step 4.6 — Rollback

- Phases 1–2 are additive and branch-isolated. Rollback = revert the app build (hide the selector); any AdvDep vouchers already created remain valid data and can be approved once the dealer branch is present. No data migration to undo.
- If `adv_dep` was wrongly mutated, it's a single scalar per relation — correctable via the existing `CustSettings` manual edit.

---

## Out of scope (candidates for a follow-up)

- Dealer-initiated AdvDep via `Dealer/NewVoucher` (needs the same branch in `createDealerVoucher`, which posts to `month_crdrs` immediately — overview §6.4).
- Per-deposit "remaining amount" traceability (Phase 3, Decision B).
- Refund/return of an advance deposit (decrement `adv_dep` with a DEBIT-style record) — not requested.
- Interest/expiry on held deposits.

---

## Done = MVP

**Phase 1 + Phase 2 + Steps 4.1–4.5** delivers: a customer creates an Advance Deposit, a dealer approves it, it appears in the advance-deposit balance and is held apart from invoice outstanding, with tests guarding the `month_crdrs` isolation. Phase 3 adds the adjustment/drawdown when prioritized.
