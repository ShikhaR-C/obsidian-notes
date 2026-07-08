# Max Credit Limit (`max_cr_lmt`) — Semantic Redesign: `0 = blocked`, `unset = unlimited`

**Status:** Spec'd (2026-05-29). **Implemented in code across all three repos (doc synced 2026-07-09 — this line had gone stale while the work shipped):**

- **Phase 1 (backend)** — landed in `dzzlo_oms_api` as `bf063d4` (2026-06-20, "feat(credit): adopt null/0/>0 max_cr_lmt semantics with legacy client shim"): v3 order create+update enforcement, `createDC` version-gated default (`legacyCredit ? null : 0`), v2 write coercion, `legacy_credit_presenter` wired into `api_v/api2.js` + `api_v/api3.js`. Test seed adjusted in `1169ceb` (seeded relations forced to `null`/unlimited).
- **Phase 2 (migration/rollout)** — `scripts/migrate_max_cr_lmt.js` is committed; ⚠️ whether it has been **executed against production data** is not verifiable from the repo — confirm and record here before treating Phase 2 as closed.
- **Phase 3 (setting screen)** — landed in `dzzlo_oms_app` v1.78: `CustSettings.js` Unlimited/Fixed-Limit control with blocked handling; tri-state helper `src/helpers/Credit/index.js` (`creditState`/`isUnlimited`/`isBlocked`/`isCapped`); `creditUtilization` counts adv_dep as spending power (`6a8109a8`).
- **Phase 4 (consumers/web/tests)** — dip-web landed `fix/maxcrlmt` (PR #18, "distinguish unlimited vs blocked credit limit") + shared `computeCreditProgress` util, shipped v1.4.5+. **Automated tests pinning the contract are still missing** — they are owned by tasks_12 (Phase 2 §2.2.3 API credit suite, Phase 4 §4.2 app Credit helper suite).

**Owner:** TBD
**Created:** 2026-05-29
**Scope:** Re-define the meaning of `dealer_custs.max_cr_lmt` **system-wide** (app + `dzzlo_oms_api` v3 + `dip-web`), replace the bare numeric input on `CustSettings` with an explicit control, and migrate all existing data — **while staying compatible with the live v1.77 app** via a server-side version gate (decision 4). **Legacy API v1/v2 are intentionally NOT touched** (decision below).

---

## 1. The problem

`CustSettings.js:788` exposes a bare numeric `TextInput` that writes `dealer_custs.max_cr_lmt`. Today the value is overloaded with a **backwards** convention:

| Value today               | Effective meaning today                       |
| ------------------------- | --------------------------------------------- |
| `0` / `null` / `""`       | **Unlimited** credit (server skips the check) |
| `0 < x < 1` (e.g. `0.01`) | **Blocked** (sentinel; any order exceeds it)  |
| `>= 1`                    | Capped at amount                              |

A dealer who types `0` to mean _"no credit"_ actually grants **unlimited** credit. That's the [`0`-means-unlimited footgun]. The root cause is an anti-pattern: an **in-domain value** (`₹0`) is used to mean an **out-of-domain concept** (`∞`/unlimited).

## 2. The new contract (type-correct)

`max_cr_lmt` is a **quantity of money** (the most credit a customer may carry). `0` is the natural floor of that scale (`₹0` credit = blocked); "unlimited" is the **absence** of a limit, which is correctly the **absence of a value** (`null`/unset).

| `max_cr_lmt`          | Meaning                 | Server behavior                                       |
| --------------------- | ----------------------- | ----------------------------------------------------- |
| `null` / unset / `""` | **Unlimited**           | check skipped                                         |
| `0`                   | **Blocked** (₹0 credit) | any order with `balSum > 0` → "Credit Limit Exceeded" |
| `> 0`                 | **Capped** at amount    | enforced normally                                     |

`typeof max_cr_lmt === "number"` now reads cleanly as _"a limit is set"_ (true for `0` and positives; false for `null`/`undefined`). The old `(0,1)` sentinel is **retired**.

> ⚠️ **Core hazard:** `0` and `null` are both falsy. The codebase is littered with truthiness checks (`!max_cr_lmt`, `?? 0`, `x ? x : 0`, `Number(null) === 0`) that bucket them together. Under the new contract they mean **opposites** (blocked vs unlimited). **Every such site must become an explicit `== null` / `=== 0` / `> 0` test.** Missing one = a blocked customer silently shows/behaves as unlimited (or vice-versa). This is the bulk of Phase 4.

## 3. Confirmed decisions

1. **Advance deposit + blocked:** a blocked customer (`0`) **can still order against prepaid advance deposit.** → The existing formula `balSum = prevBal + amount − adv_dep` already yields this (when `adv_dep` covers the order, `balSum ≤ 0`, so `0 < balSum` is false → allowed). **No special handling needed.**
2. **New-relationship default = blocked.** New `dealer_custs` rows default `max_cr_lmt` to `0` — gated to `>= 1.78` clients (decision 4). Implemented **server-side in `createDC`** (not via a Mongoose schema `default`, which `.save()` could silently re-apply to migrated-unset rows). See Phase 1 §3.
3. **Do NOT touch API v1/v2.** Only v3 enforcement is changed. Residual risk in Phase 1 §5.
4. **Compatible with the live v1.77 release.** The v1.77 app (bare `TextInput`, `0` = unlimited) hits the same backend. **Version-gate the two write funnels** using the existing `req.headers.meta` → `version` idiom (as in `order_msts.js`): a `0` written by a `<= 1.77` client is stored as `null` (unlimited, old meaning); a `0` from `>= 1.78` is stored as blocked. Order **enforcement** stays uniform (un-gated) — after migration + the write-gate, every stored `0` is a deliberate v1.78 block. v1.77 **display** of a blocked customer shows "no limit" (read-only skew; server still enforces). See Phase 1 §2–§3.

## 4. UI (the new control on `CustSettings`)

Two tap-only chips + an amount input revealed under Block (no keyboard for the chip taps; keyboard only when typing a cap):

```
 Credit Limit
 ┌───────────┐  ┌─────────────────┐
 │ Unlimited │  │ ● Block credit  │
 └───────────┘  └─────────────────┘
 Set amount   [ ₹ 50,000 ]   ← shown only when Block credit is active
                               empty = fully blocked (₹0) · a number = capped
 ⓘ Unlimited = no cap.  Block credit = no credit unless you enter an
   amount here to allow up to that limit.  Advance deposit is still usable.
```

State→value mapping: tap **Unlimited** → write `null`; tap **Block credit** → write `0` (reveal field, no keyboard); type an amount + blur → write the number. Switching from a capped amount back to Block keeps the old number greyed in the field as a restore hint and the confirm cites it ("Current limit ₹50,000 will be overridden"), until you navigate away. Full behavior + paste-ready code in Phase 3.

> **Label note (1-line copy decision):** the chip is called "Block credit" per request. Because Block also hosts the cap amount, "Block credit + ₹50,000" technically means _capped_, not blocked — the helper note covers this. If that reads oddly, rename the chip to "Set limit" in one place (Phase 3 §1). Does not affect any stored value.

## 5. Blast radius — file inventory

### Backend (`dzzlo_oms_api`, v3 only)

| File                                                | Lines                                          | Change                                                                 | Phase |
| --------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------- | ----- |
| `api_v3/services/order_msts.js`                     | `781-799`, `920-938`                           | enforcement: drop `&& !== 0` and `!!max_cr_lmt &&` (un-gated)          | 1     |
| `api_v3/services/dealer_custs.js`                   | `updateDealerCust` `~1483`; `createDC` `~1360` | write normalization + create default `0`, both **v1.77 version-gated** | 1     |
| `api_v3/controllers/collections/dealer_custs_v1.js` | `UpdateDealerCust` `~34`; `CreateDC` `~29`     | parse `req.headers.meta` and pass `meta` to the two services           | 1     |
| `models/dealer_custs.js`                            | `84`                                           | doc comment only (NO schema default)                                   | 1     |
| migration script                                    | new                                            | `scripts/migrate_max_cr_lmt.js`                                        | 2     |
| `android/app/build.gradle`, iOS `MARKETING_VERSION` | `versionName`/marketing                        | bump `1.77` → `1.78` (gate activator)                                  | 3     |

### App (`dzzlo_oms_app`)

| File                                                    | Lines                                 | Change                             | Phase |
| ------------------------------------------------------- | ------------------------------------- | ---------------------------------- | ----- |
| `screens/Dealer/Customers/CustSettings.js`              | `289`,`293-323`,`420-429`,`774-799`   | new control (chips + amount)       | 3     |
| `screens/Dealer/Customers/index.js`                     | `32-49`                               | `getProgress` null-vs-0            | 4     |
| `screens/Common/RelationList/RelationCreditBS.js`       | `76-77`,`332-333`,`491`               | null-vs-0 + text display           | 4     |
| `screens/Customer/Dealers/components.js`                | `314-340`                             | null-vs-0                          | 4     |
| `components/Balance/Components.js`                      | `433-458`                             | null-vs-0                          | 4     |
| `screens/Customer/NewOrder/components.js`               | `838-855`                             | null-vs-0 (`CreditProgressORDER`)  | 4     |
| `screens/Customer/Dealers/DealerSettings/index.js`      | `123`,`136-150`,`704-727`,`771`,`892` | display "Unlimited/Blocked/amount" | 4     |
| `screens/Customer/Dealers/DealerSettings/components.js` | `290`                                 | `Field_Value` text display         | 4     |

### Web admin (`dip-web`) — read-only (no write/gate)

| File                                            | Lines                               | Change            | Phase |
| ----------------------------------------------- | ----------------------------------- | ----------------- | ----- |
| `src/pages/superadmin/customers/CustDealers.js` | `122`,`185`,`404`,`442`,`445`       | null-vs-0 display | 4     |
| `src/pages/superadmin/dealers/DlrCusts.js`      | `172`,`277`,`314`,`426`,`437`,`514` | null-vs-0 display | 4     |

### Tests / seeds (`dzzlo_oms_api/test`)

`api_v3/collections/dealer_custs/index.test.js`, `api_v3/helper/.../relations.js`, `api_v3/temp/seed/v3/factories/relateDC_Cash_reimb.js`, plus `202405_v2/*` and `api_v1/*` write tests that assert `0 = no block`. Update in Phase 4 §4.

## 6. Phases & required ordering

1. **Phase 1 — Backend** (enforcement + write normalization + create default).
2. **Phase 2 — Migration & rollout** — _order-sensitive and partly interleaved with the Phase 1 deploy._ Read before deploying anything.
3. **Phase 3 — App setting screen** (`CustSettings` new control).
4. **Phase 4 — All other consumers** (app display + dip-web + tests + verification).

> **Critical rollout order** (full detail in Phase 2): **(a)** run migration step 1 (`0 → $unset`) under OLD code → **(b)** deploy Phase 1 backend → **(c)** run migration steps 2–3 (`(0,1) → 0`, `<0 → 0`). This sequence has **no window** where a customer is mis-classified. Deploying Phase 1 _before_ migrating would instantly block every currently-unlimited (`0`) customer.

## 7. Risk summary

- **Irreversible migration** — `0` means opposite things pre/post. Requires DB backup + dry-run counts (Phase 2).
- **Missed truthiness site** — any un-converted `!max_cr_lmt`/`?? 0` shows blocked as unlimited. Phase 4 must be exhaustive; grep gate provided.
- **Mobile version skew** — old app builds in the field interpret `0` as "no limit" (display only; server still enforces blocked). Acceptable; noted in Phase 2 §4.
- **Scope vs the sentinel alternative** — this is ~10× the surface of a `0.01`-sentinel approach (which needed ~2 files, no migration, no enforcement change). Chosen for the cleaner end-state. If scope needs cutting, the sentinel approach delivers the identical dealer UX.
