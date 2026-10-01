# Advance Deposit (AdvDep) — Feature Plan & Overview

**Status:** ✅ **2026-10-01:** Phases 1–3 built and shipped (API PR #29 `2bb7eba` → release 1.5.4; app `5e0ee266` … `c5e87820` → 1.78), with three changes from the plan — the balance is re-derived from the voucher ledger, the passbook opens from the Accounts balance header, and an adjustment draws a whole deposit once; Phase 4 🟡 (API tests ✅; app tests ⬜; the production backfill run ❔). — _was:_ Phases 1 & 2 implemented (2026-05-25); Phase 3 spec'd as **v2** (overview synced 2026-05-25)
**Owner:** TBD
**Created:** 2026-05-24
**Scope:** New voucher type `AdvDep` in `dzzlo_oms_api`, customer-initiated from the `PayOnAc` screen, posting to a **separate advance-deposit balance** that does not touch invoice outstanding, plus a linked **adjustment/drawdown** mechanism.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Phases 1–3 ✅ (as built, with the design changes noted in each phase doc), Phase 4 🟡; 3 new tasks (`T07-N1` … `T07-N3`). The v4 layer adds no AdvDep logic of its own: the Customers read model reads the stored `adv_dep` and the v2 credit sheet shows it (`api_v4/readmodels/customers.js:661,735`; `CreditSheet.js:303-305`). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item                                        | Status | What exists now (evidence)                                                                                                                                                                                                                                                                                                                                                  | What is left / next step                                                                  |
| ------------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Phase 1 — `AdvDep` type + customer selector | ✅     | API `voc_text` (`api_v3/services/voc_msts.js:65-66`); app constants (`src/constants/payments.js:20,30,40`) and display maps (`src/utils/Conditional/VoucherType.js`); the selector is the "Adv. Deposit" chip on `Customer/NewPayAck` (`index.js:51-65`) — the standalone `PayOnAc` was removed (`c5e87820`)                                                                | —                                                                                         |
| Phase 2 — balance posting + dealer approval | ✅     | Approval branches on `voc_type` and `ref_voc_id` (`voc_msts.js:306-307`); deposits never enter `month_crdrs`; `persistAdvDep` re-derives `adv_dep` from the vouchers (`:243-253`) instead of the planned increment; approving an AdvDep needs app ≥ 1.78 (`:320-333`); PromptPay branch (`PromptPay.js:141`); the manual editor is gone                                     | —                                                                                         |
| Phase 3 — separate ledger + adjustment      | ✅     | `ref_voc_id` (`models/voc_msts.js:31`); AdvDep kept out of the relationship ledger, three balance paths and the month rebuild (`dealer_custs.js:77,326,400,465`, `ledger_window.js:394`, `order_msts.js:348`); passbook route (`routes/collections/cust_msts.js:81`); app `Common/AdvDepLedger` in both roles' stacks; "Adjust to account" (`VoucherDetailsBSM.js:131-197`) | The three design changes are recorded in the Phase 2 and Phase 3 docs                     |
| Phase 4 — tests, docs, rollout              | 🟡     | Regexes (`helper/collections/voc_msts/index.js:58`, `features/accounts/index.test.js:128,167`); `collections/voc_msts/advdep.test.js` (24 tests); `docs/AI_CONTEXT.md:110-116`; app `AdvDepFilter.test.js` ×2                                                                                                                                                               | `T07-N1` (backfill run ❔), `T07-N2` (passbook and reconcile tests), `T07-N3` (app tests) |
| Built beyond the plan                       | 🆕     | Dealer-created AdvDep on the API (`createDealerVoucher`, `voc_msts.js:770-807`); an unadjusted-deposit lookup for the web voucher page (`routes/collections/voc_msts.js:32`, `ffe7120`)                                                                                                                                                                                     | The app's dealer `NewVoucher` offers no AdvDep (`voucherTypes.js:11-15`)                  |
| 1.79 fixes                                  | ✅     | Passbook dates `DDMMyy` (`84f49ec6` → `dcde2c8b`); the Payments type filter opens with Advance Deposit included (`5e211e0d` → `28cdee36`)                                                                                                                                                                                                                                   | —                                                                                         |

---

## 1. What we are building

**Status (2026-10-01):** ✅ all three flows exist in code: On-Account (`PInv`), Advance Deposit (`AdvDep`) and the linked adjustment (`PInv` + `ref_voc_id`).

Today the customer payment screen `PayOnAc` creates a single kind of payment: an **On-Account payment** (`voc_type: 'PInv'`, `pay_type: 'CREDIT'`, `pay_status: false`). It sits unapproved until a dealer approves it, at which point it credits the customer's running ledger (reduces invoice outstanding).

We are adding a **second category** on the same screen:

| Category                      | voc_type     | Posts to                                             | Effect on approval                                                            |
| ----------------------------- | ------------ | ---------------------------------------------------- | ----------------------------------------------------------------------------- |
| On Account payment (existing) | `PInv`       | `month_crdrs` (running ledger)                       | Credits running balance → reduces invoice outstanding                         |
| **Advance Deposit (new)**     | **`AdvDep`** | **`dealer_custs.adv_dep`** (advance-deposit balance) | Increases the advance-deposit balance; **does NOT touch invoice outstanding** |

And a third, later, flow:

| Flow                      | Mechanism                                                                   | Effect                                                                                                                                 |
| ------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Adjustment / drawdown** | Customer creates an On-Account payment **linked to** a prior AdvDep voucher | On approval: **decrements** `adv_dep` AND **credits** `month_crdrs` → reflects in **both** ledgers, signifying the deposit was applied |

### Business definition (confirmed with product owner, 2026-05-24)

> Advance deposit is a **refundable deposit held against future transactions**. There is a **separate ledger** for advance deposits with its **own balance**. It **does not touch the customer's invoice outstanding**. The customer can later create a "duplicate" on-account payment **linked to an AdvDep voucher**; that adjustment reflects in **both** ledgers, signifying the advance deposit has been adjusted.

---

## 2. Key discovery — the advance-deposit ledger already half-exists

**Status (2026-10-01):** ✅ `dealer_custs.adv_dep` is still the stored balance that the screens and the credit check read — but it is no longer set on its own: every approval and every passbook read re-derives it from the approved vouchers (`api_v3/services/voc_msts.js:215-253`, `api_v3/services/dealer_custs.js:522-566`). The v4 Customers read model reads the same field (`api_v4/readmodels/customers.js:661,735`).

We do **not** need a new collection. An advance-deposit balance is already modelled and displayed:

- **Storage:** `dzzlo_oms_api/models/dealer_custs.js:83` → `adv_dep: { type: Number } // advanced deposit`. A scalar per dealer↔customer relationship.
- **Pre-feature, it was set MANUALLY by the dealer** in the app at `dzzlo_oms_app/src/screens/Dealer/Customers/CustSettings.js` (`handleAdvanceDeposits` → `update_dealer_custs` PUT → `updateDealerCust`). **Phase 2 removed that writer and made the field read-only / voucher-driven** (§6.1); **Phase 3 (v2)** turns the field into a tap target that opens the dedicated advance-deposit ledger.
- **It is already displayed** everywhere:
  - App ledger header `dzzlo_oms_app/src/screens/Common/Accounts/components.js:79` shows an **"Advance Deposits"** column (RED), value = `dealer_cust.adv_dep`.
  - The same component computes `FinalBalance = openingBalance + OutStandingBalance − companyAdvance` (`components.js:33-37`).
  - Excel exports: `api_v3/controllers/features/Accounts/excel/index.js:45-46,112-113` and app `Common/Accounts/Render/xlsxYearAcc.js:96-97,221-222`.
  - Credit-limit checks: `api_v3/services/order_msts.js:790,930` → `balSum = prevBal + finalAmount − AdvanceDeposit`.

**Design consequence:** We make `adv_dep` **voucher-driven** going forward — incremented when an AdvDep voucher is approved, decremented when an adjustment voucher is approved. All existing display, balance math, and credit-limit logic then "just work" with **zero display changes**.

### Why the existing `FinalBalance` formula makes this clean

`FinalBalance = opening + outstanding − advance`

- Approve an **AdvDep** of ₹X → `advance += X` → final balance falls by X (customer is more in credit, money is held). Outstanding untouched. ✅ "does not touch invoice outstanding."
- Approve an **adjustment** of ₹X → `advance −= X` **and** `outstanding −= X` (CREDIT to `month_crdrs`) → `FinalBalance` nets to **no change**; the deposit simply moves from "held" to "applied against dues." ✅ "reflects in both ledgers."

---

## 3. How voucher type currently flows (the mechanics we rely on)

**Status (2026-10-01):** two mechanics changed after this was written: approval now posts by rebuilding the month bucket from the raw documents (`recomputeMonthCrDr`, `voc_msts.js:204-207`) instead of `updateCrDr`, and PromptPay's cascade has the AdvDep branch (`PromptPay.js:141`).

- **Schema has no enum.** `models/voc_msts.js:63-66` — `voc_type` is a free `String`. So storing `'AdvDep'` requires **no model change**. (The comment lists the known types; updating it is optional and is a `models/` edit — see §6.)
- **Creation endpoint is type-agnostic.** App calls `POST voc_msts/a/custvoc` (`add_cust_on_acc_voc_msts`) → `api_v3/services/voc_msts.js:560` `createCustomerOnAcVoucher` → just `VoucherMaster.create(body)`. **No ledger posting at creation.** So an AdvDep voucher is created the same way, with no API change to the create path.
- **Ledger posting happens on dealer approval.** `updateVocStatus` (`api_v3/services/voc_msts.js:295`) flips `pay_status:true` and, today, **always** posts `cd:'CREDIT'` to `month_crdrs` via `updateCrDr` (keyed on `pay_type`, **never** `voc_type`). → **This is the one place we branch** (Phase 2): for `voc_type === 'AdvDep'`, increment `adv_dep` instead of posting to `month_crdrs`.
- **The dealer approval UI has a hard cascade.** `dzzlo_oms_app/src/screens/Dealer/Payments/components/PromptPay.js:93-152`:
  `inv_id` → `order_id` → `invs_adj.length` → `remarks includes 'On account payment.'` → **else `alert('No conditions matched')`**. An AdvDep voucher hits the `else` and **cannot be approved** today → Phase 2 adds an `order.voc_type === 'AdvDep'` branch.
- **The ledger transaction LIST is filtered (Phase 3 v2).** `api_v3/services/dealer_custs.js` `getDealerCustomerAccount` merges `[...invoices, ...vouchers]` (`name = voc_type`). Phase 3 adds `voc_type: { $ne: 'AdvDep' }` to the voucher query, so **AdvDep deposits are hidden** from the relationship ledger (they appear only in the dedicated advance-deposit ledger). **Adjustment** vouchers are `PInv` (not `AdvDep`), so they stay visible as a CREDIT. Only `month_crdrs` drives the running-balance column, and AdvDep never posts there (Phase 2). ✅

### Display label/icon maps (additive — Phase 1)

**Status (2026-10-01):** ✅ all three carry `AdvDep` (`voc_msts.js:65-66`; `src/constants/payments.js:20,30,40`; `VoucherType.js:35-36,79-80,132-133`).

- API: `voc_text()` switch `api_v3/services/voc_msts.js:36-57` (used in notifications/receipts). No `AdvDep` case → returns `""`.
- App constants: `src/constants/payments.js` — `VOC_TYPE`, `VOC_TYPE_LABELS`, `VOC_TYPES_ARRAY`.
- App display: `src/utils/Conditional/VoucherType.js` — `Voucher_type()` (icon), `Voucher_text()` (label), `Voc_Inv_type()` (icon).

---

## 4. Phase map

**Status (2026-10-01):** Phases 1–3 ✅ (API PR #29 → 1.5.4; app → 1.78), Phase 4 🟡 — see the roll-up at the top.

| Phase | File                                                                                   | Goal                                                                                                                                                                                   | Risk                                                   | Ships independently?                                                             |
| ----- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------------------------------- |
| **1** | [`01-phase-1-voctype-and-screen.md`](01-phase-1-voctype-and-screen.md)                 | Register the `AdvDep` label/icon/filter (API + app) **and** add the On-Account vs Advance-Deposit selector to `PayOnAc`. Customer can create an AdvDep voucher; it displays correctly. | **Low** (additive)                                     | Yes — but AdvDep vouchers can't be approved until Phase 2, so ship 1+2 together. |
| **2** | [`02-phase-2-balance-and-approval.md`](02-phase-2-balance-and-approval.md)             | Make approval post AdvDep to the advance-deposit balance (`adv_dep`), not `month_crdrs`; add the dealer-side approval branch.                                                          | **Medium** (touches `updateVocStatus`)                 | Together with Phase 1 = the **MVP**.                                             |
| **3** | [`03-phase-3-adjustment-and-ledger-view.md`](03-phase-3-adjustment-and-ledger-view.md) | **(v2)** Filter AdvDep out of the relationship ledger; **dedicated advance-deposit ledger screen** (opened from `CustSettings`); linked adjustment/drawdown (decrement `adv_dep` + credit `month_crdrs`); "Adjust to account" on the voucher-details BS.                                       | **High** (linkage, two-ledger posting, new screen + endpoint, guardrails) | Builds on 1+2; not independent.                                 |
| **4** | [`04-phase-4-tests-docs-rollout.md`](04-phase-4-tests-docs-rollout.md)                 | Test-regex updates, new tests, docs, app-version gating, rollout runbook.                                                                                                              | Low                                                    | Runs alongside 1–3.                                                              |

**Recommended MVP = Phase 1 + Phase 2** (both implemented 2026-05-25). Phase 3 is the only part with real accounting complexity; it is now being implemented as the **v2** design (filter + dedicated ledger + drawdown). Until it ships, deposits accumulate and display correctly via the `adv_dep` balance; only the separate ledger view and the in-app drawdown wait for Phase 3.

---

## 5. File-change index (full feature)

**Status (2026-10-01):** ✅ every listed change is in code, with two moves: the selector is in `src/screens/Customer/NewPayAck/index.js` (the `PayOnAc` screen was removed, `c5e87820`), and the passbook opens from the Accounts balance header (`src/screens/Common/Accounts/index.js:478-494`, wired at `:930`) rather than from `CustSettings`.

### API (`dzzlo_oms_api`) — all within `api_v3/` (honours the active-development rule), except where flagged

| File                                                           | Phase   | Change                                                                                                                                               |
| -------------------------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_v3/services/voc_msts.js` (`voc_text` ~L36)                | 1       | Add `case "AdvDep": return "Advance Deposit";`                                                                                                       |
| `api_v3/services/voc_msts.js` (`updateVocStatus` ~L295)        | 2       | Select `voc_type`; branch: AdvDep → increment `adv_dep`, skip `month_crdrs`; skip invoice validation. Add `updateAdvDep` helper.                     |
| `api_v3/services/voc_msts.js` (adjustment)                     | 3       | On approval of a linked adjustment voucher: decrement `adv_dep` + credit `month_crdrs`.                                                              |
| `api_v3/services/dealer_custs.js` (`getDealerCustomerAccount`) | 3       | Filter AdvDep from the relationship ledger (`voc_type: { $ne: 'AdvDep' }`); add new `getAdvDepLedger` service + `POST cust_msts/app/advdepledger` controller/route (Steps 3.2, 3.4).                                                                         |
| `models/voc_msts.js`                                           | 3       | Add optional `ref_voc_id: ObjectId` to link adjustment→AdvDep (**resolved**: sanctioned additive exception to the no-`models/`-edit rule; see §6.2). |
| `models/voc_msts.js:65` (comment)                              | 1 (opt) | Append `AdvDep` to the type comment — _optional `models/` edit._                                                                                     |
| `test/api_v3/helper/collections/voc_msts/index.js:57`          | 4       | Add `AdvDep` to the voc_type regex.                                                                                                                  |
| `test/api_v3/features/accounts/index.test.js:128,167`          | 4       | Add `AdvDep` to the ledger/payment regexes.                                                                                                          |

### App (`dzzlo_oms_app`)

| File                                                           | Phase   | Change                                                                          |
| -------------------------------------------------------------- | ------- | ------------------------------------------------------------------------------- |
| `src/constants/payments.js`                                    | 1       | Add `ADVDEP: 'AdvDep'`, label `'Advance Deposit'`, push to `VOC_TYPES_ARRAY`.   |
| `src/utils/Conditional/VoucherType.js`                         | 1       | Add `AdvDep` case to `Voucher_type`, `Voucher_text`, `Voc_Inv_type`.            |
| `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js` | 1       | Add On-Account vs Advance-Deposit selector; set `voc_type` + `remarks` from it. |
| `src/screens/Dealer/Payments/components/PromptPay.js:93-152`   | 2       | Add `order.voc_type === 'AdvDep'` approval branch.                              |
| `src/screens/Dealer/Customers/CustSettings.js:706-716`         | 2       | Make the Advance Deposits input **read-only** (now voucher-driven; §6.1).       |
| `Common/AdvDepLedger` (new) + `SectionalAcc.js` + `Dealer/Main.js` + `CustSettings.js` + `_Voucher_/BS`        | 3       | New advance-deposit ledger screen (deposits=credit, adjustments=debit) opened from `CustSettings`; `get_advdep_ledger` RTK mutation; "Adjust to account" on the voucher-details BS (Steps 3.5–3.8).               |

**No change needed:** the `add_cust_on_acc_voc_msts` RTK mutation (passes the body through unchanged) and the "Advance Deposits" balance display (already wired to `adv_dep`).

---

## 6. Decisions (resolved 2026-05-24, updated 2026-05-25)

**Status (2026-10-01):** 1 ✅ voucher-driven — the manual field is gone, not just read-only; 2 ✅ `ref_voc_id` (`models/voc_msts.js:31`); 3 🟡 pooled on the server (`voc_msts.js:342-354`), but the app allows one adjustment per deposit, for its full amount (`VoucherDetailsBSM.js:136-160`); 4 🆕 the API now accepts a dealer-created AdvDep (`createDealerVoucher`, `voc_msts.js:770-807`), which the app does not offer; 5 ❌ superseded — a dedicated `payment-advdep` glyph exists (`VoucherType.js:36`, added in `1bd79d55`); 6 ✅ with the passbook entry moved to Accounts.

1. **`adv_dep` source of truth → RESOLVED: voucher-driven; manual field read-only.** Keep storing the balance in `dealer_custs.adv_dep` (no model change, reuse all display) and mutate it **only** via voucher approval going forward. The dealer's manual editor in `CustSettings` becomes **read-only** (it displays the voucher-driven balance) — see Phase 2, Step 2.4. Any existing stored value carries forward as the starting balance.

2. **Adjustment→AdvDep linkage field → RESOLVED: add `ref_voc_id`.** Add optional `ref_voc_id: { type: ObjectId, ref: 'voc_msts' }` to `models/voc_msts.js` (Phase 3, Step 3.1). Additive, backward-compatible, changes no legacy behaviour. This is the **one sanctioned exception** to the "no edits to `models/`" rule (AI.md §"Active Development Rule"), justified because it is purely additive. (The remarks-encoding fallback is dropped.)

3. **Per-voucher vs pooled deposit → RESOLVED: pooled (v1).** An adjustment may draw up to the _total_ `adv_dep` balance; the `updateAdvDep` guardrail prevents overdraw. Per-voucher "remaining" traceability is deferred.

4. **Dealer-initiated AdvDep → out of scope for MVP** (customer-initiated only). `Dealer/NewVoucher` would need the same branch in `createDealerVoucher`, which posts to `month_crdrs` immediately.

5. **Icon glyph → RESOLVED: reuse `payment-cash`.** Use the existing `payment-cash` VsystIcons glyph for AdvDep for now. A dedicated `advance-deposit` glyph can be added later without touching call sites beyond `VoucherType.js`.

6. **Phase 3 design → RESOLVED: v2 (2026-05-25).** (a) AdvDep vouchers are **filtered out** of the relationship ledger (`voc_type: { $ne: 'AdvDep' }`). (b) A **dedicated advance-deposit ledger screen is required** (not optional), opened from the read-only "Advance Deposits" field in `CustSettings`, showing deposits (credit) and adjustments (debit) with a running balance that closes at `adv_dep`. (c) The Accounts screen **keeps netting** (`FinalBalance = opening + outstanding − advance`) and credit-limit math is **unchanged** — `adv_dep` equals the advance-deposit ledger balance by construction (voucher-driven only), so both keep reading the scalar. (d) The "Adjust to account" action lives on the voucher-details bottom sheet (`_Voucher_/BS`), shown on every AdvDep voucher. See `03-phase-3-adjustment-and-ledger-view.md`.

---

## 7. Risk register

**Status (2026-10-01):** the five code risks are mitigated in code — AdvDep never reaches `month_crdrs` (pinned by `advdep.test.js:81`), the approval branch exists, manual double-counting cannot happen (editor removed, older builds' writes refused), overdraw is refused before any write, and approval needs app ≥ 1.78. New: the re-derivation resets a legacy manual balance that has no voucher behind it unless the one-off backfill ran (`T07-N1`).

| Risk                                                             | Likelihood              | Impact | Mitigation                                                                                                                |
| ---------------------------------------------------------------- | ----------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| AdvDep accidentally credits `month_crdrs` (pollutes outstanding) | Med                     | High   | Phase 2 branch on `voc_type` in `updateVocStatus`; explicit test asserting `month_crdrs` unchanged after AdvDep approval. |
| AdvDep voucher can't be approved (hits "No conditions matched")  | High if Phase 2 skipped | High   | Phase 2 PromptPay branch; ship Phase 1+2 together.                                                                        |
| Manual + voucher-driven `adv_dep` double-counting                | Med                     | Med    | Resolved §6.1 — manual field is read-only (Phase 2 §2.4).                                                                 |
| Adjustment overdraws the deposit (negative `adv_dep`)            | Med                     | Med    | Guardrail in Phase 3: reject adjustment > available `adv_dep`.                                                            |
| Older app builds send AdvDep with no approval-branch support     | Low                     | Med    | Version-gate the selector; backend tolerates the value regardless.                                                        |
| `models/` edit for `ref_voc_id` crosses the active-dev rule      | —                       | Low    | Resolved §6.2 — sanctioned additive field (`ref_voc_id`), changes no legacy behaviour.                                    |

---

## 8. Glossary

- **On-Account payment** — a credit not tied to a specific invoice; reduces running outstanding on approval. `voc_type: 'PInv'`.
- **Advance Deposit** — refundable money held against future transactions; tracked in `adv_dep`, separate from outstanding. `voc_type: 'AdvDep'`.
- **Adjustment / drawdown** — moving an advance deposit into the running account (decrement `adv_dep`, credit `month_crdrs`).
- **`month_crdrs`** — per-month `{drttl, crttl}` ledger; the running-balance source of truth.
- **`adv_dep`** — scalar advance-deposit balance on `dealer_custs`.
- **`pay_status`** — `false` = pending dealer approval, `true` = approved (posts to ledgers).

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID     | Task                                                                                              | Why (evidence)                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Project | Size | Depends on                            |
| ------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- | ---- | ------------------------------------- |
| T07-N1 | 🆕 ❔ Confirm the one-off `yarn backfill:advdep` ran on production, or run it (`--dry-run` first) | Since `6ae9aff` the balance is re-derived from approved vouchers and written back (`persistAdvDep`, `api_v3/services/voc_msts.js:243-253`; the passbook read writes it too, `api_v3/services/dealer_custs.js:561-566`), so a pre-feature manual `adv_dep` with no voucher behind it is reset to the voucher total on the next approval or passbook read; `scripts/backfill_advdep_seed_opening.js` seeds that difference as an approved AdvDep voucher; nothing in the repos records a run | API     | XS   | Production database access (the user) |
| T07-N2 | 🆕 API tests for the passbook route and the reconcile path                                        | No test calls the passbook route (`routes/collections/cust_msts.js:81`, service `dealer_custs.js:523-568`) — its credit / debit classification, the closing balance equal to `adv_dep`, the write-back — and none runs `checkYearMonth` with an approved AdvDep to pin Phase 3 Step 3.10 (`ledger_window.js:394`, `dealer_custs.js:77`)                                                                                                                                                    | API     | S    | —                                     |
| T07-N3 | 🆕 App tests for the AdvDep paths                                                                 | Only the Payments filter is tested (`src/screens/{Dealer,Customer}/Payments/__tests__/AdvDepFilter.test.js`); untested are `NewPayAck`'s "Adv. Deposit" payload (`index.js:51-65`, `:156-182`), PromptPay's AdvDep branch (`PromptPay.js:141`), `VoucherDetailsBSM`'s `canAdjust` and adjustment payload (`:147-179`) and the passbook screen (`src/screens/Common/AdvDepLedger/index.js`)                                                                                                 | app     | M    | —                                     |
