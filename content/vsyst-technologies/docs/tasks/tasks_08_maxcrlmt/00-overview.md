# Max Credit Limit (`max_cr_lmt`) — Semantic Redesign: `0 = blocked`, `unset = unlimited`

**Status:** 🟡 **2026-10-01:** Phases 1, 3 and 4 ✅ in the two assessed repos (API `bf063d4` → release 1.5.4; app consumers in 1.78; tests now pin the contract in the API, the app and v4); Phase 2's production migration run is still ❔. — _was:_ Spec'd (2026-05-29). **Implemented in code across all three repos (doc synced 2026-07-09 — this line had gone stale while the work shipped):**

- **Phase 1 (backend)** — landed in `dzzlo_oms_api` as `bf063d4` (2026-06-20, "feat(credit): adopt null/0/>0 max_cr_lmt semantics with legacy client shim"): v3 order create+update enforcement, `createDC` version-gated default (`legacyCredit ? null : 0`), v2 write coercion, `legacy_credit_presenter` wired into `api_v/api2.js` + `api_v/api3.js`. Test seed adjusted in `1169ceb` (seeded relations forced to `null`/unlimited).
- **Phase 2 (migration/rollout)** — `scripts/migrate_max_cr_lmt.js` is committed; ⚠️ whether it has been **executed against production data** is not verifiable from the repo — confirm and record here before treating Phase 2 as closed.
- **Phase 3 (setting screen)** — landed in `dzzlo_oms_app` v1.78: `CustSettings.js` Unlimited/Fixed-Limit control with blocked handling; tri-state helper `src/helpers/Credit/index.js` (`creditState`/`isUnlimited`/`isBlocked`/`isCapped`); `creditUtilization` counts adv_dep as spending power (`6a8109a8`).
- **Phase 4 (consumers/web/tests)** — dip-web landed `fix/maxcrlmt` (PR #18, "distinguish unlimited vs blocked credit limit") + shared `computeCreditProgress` util, shipped v1.4.5+. ~~**Automated tests pinning the contract are still missing**~~ **2026-10-01: they exist** — API `test/api_v3/features/credit/index.test.js` and `collections/dealer_custs/index.test.js:90-178`, app `src/helpers/Credit/__tests__/index.test.js` (24 tests), v4 `test/api_v4/lib/customersModel.test.js:159-206` — they are owned by tasks_12 (Phase 2 §2.2.3 API credit suite, Phase 4 §4.2 app Credit helper suite).

**Owner:** TBD
**Created:** 2026-05-29
**Scope:** Re-define the meaning of `dealer_custs.max_cr_lmt` **system-wide** (app + `dzzlo_oms_api` v3 + `dip-web`), replace the bare numeric input on `CustSettings` with an explicit control, and migrate all existing data — **while staying compatible with the live v1.77 app** via a server-side version gate (decision 4). **Legacy API v1/v2 are intentionally NOT touched** (decision below).

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Phases 1, 3 and 4 ✅ for the API and the app (dip-web parts not assessed), Phase 2 🟡 (script committed, production run ❔); Phase 4's grep gates run clean on the app except one hit in dead code; 2 new tasks (`T08-N1`, `T08-N2`). The v4 Customers read model keeps `null` and `0` apart and carries a parity-tested copy of v3's credit ratio (`api_v4/readmodels/customers.js:129-148,731-735`); the v2 screen draws the three states (`CreditAvatar`, `CreditSheet`). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item                             | Status       | What exists now (evidence)                                                                                                                                                                                                                                                                                                                                                                                                     | What is left / next step                                                                                                        |
| -------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1 — backend                | ✅           | Order create and edit check only a numeric limit (`api_v3/services/order_msts.js:827-837`, `:963-974`); `createDC` and `updateDealerCust` version-gated (`api_v3/services/dealer_custs.js:1318-1320`, `:1479-1494`); controllers pass `meta` (`dealer_custs_v1.js:30-46`); presenter in `api_v/api2.js:20`, `api_v/api3.js:19`; model comment `models/dealer_custs.js:84`; every acceptance line pinned by a test (Phase 1 §6) | —                                                                                                                               |
| Phase 2 — migration and rollout  | 🟡           | `scripts/migrate_max_cr_lmt.js` (counts and `VERIFY=1` only, `8d0a6d9`)                                                                                                                                                                                                                                                                                                                                                        | The production `mongosh` steps and the `VERIFY=1` pass ❔ — the user confirms; the rollback note is not in `docs/runbook.md` ⬜ |
| Phase 3 — `CustSettings` control | ✅           | "Unlimited" / "Fixed Limit" chips + amount (`src/screens/Dealer/Customers/CustSettings.js:92-510`, `:881-963`); builds past 1.77 (now 1.79 / Android 105)                                                                                                                                                                                                                                                                      | No test of the control (`T08-N1`); simulator checks ❔                                                                          |
| Phase 4 — consumers, web, tests  | ✅ app + API | The seven listed app consumers import `helpers/Credit`; the API suites pin the contract; the grep gates find one hit, in dead code                                                                                                                                                                                                                                                                                             | `T08-N2`; dip-web rows — not assessed; device and web checks ❔                                                                 |
| v2 / v4 (new since the plan)     | ✅ 🆕        | The v4 `credit` block keeps `null` and `0` apart (`api_v4/readmodels/customers.js:731-735`, `:759-760`, `:830-831`) with a parity-tested copy of the ratio (`:129-148`; `test/api_v4/lib/customersModel.test.js:159-206`, `screens/customers.test.js:357,1068-1090,1693-1747`); app `CreditAvatar` (CAPPED arc / BLOCKED full ring / UNLIMITED dotted, 10 tests) and `CreditSheet` (14 tests)                                  | Where the rule should live — see `X-V4-2` in tasks_02                                                                           |

---

## 1. The problem

**Status (2026-10-01):** ✅ fixed at the source — a stored `0` now blocks (`api_v3/services/order_msts.js:827-837`); the `(0,1)` sentinel survives only as the wire shim for ≤ 1.77 builds (`legacy_credit_presenter`, `helpers/middlewares.js:167`).

`CustSettings.js:788` exposes a bare numeric `TextInput` that writes `dealer_custs.max_cr_lmt`. Today the value is overloaded with a **backwards** convention:

| Value today               | Effective meaning today                       |
| ------------------------- | --------------------------------------------- |
| `0` / `null` / `""`       | **Unlimited** credit (server skips the check) |
| `0 < x < 1` (e.g. `0.01`) | **Blocked** (sentinel; any order exceeds it)  |
| `>= 1`                    | Capped at amount                              |

A dealer who types `0` to mean _"no credit"_ actually grants **unlimited** credit. That's the [`0`-means-unlimited footgun]. The root cause is an anti-pattern: an **in-domain value** (`₹0`) is used to mean an **out-of-domain concept** (`∞`/unlimited).

## 2. The new contract (type-correct)

**Status (2026-10-01):** ✅ enforced (Phase 1) and displayed (Phase 4); the v4 read model keeps `null` and `0` apart too (`api_v4/readmodels/customers.js:731-735`).

`max_cr_lmt` is a **quantity of money** (the most credit a customer may carry). `0` is the natural floor of that scale (`₹0` credit = blocked); "unlimited" is the **absence** of a limit, which is correctly the **absence of a value** (`null`/unset).

| `max_cr_lmt`          | Meaning                 | Server behavior                                       |
| --------------------- | ----------------------- | ----------------------------------------------------- |
| `null` / unset / `""` | **Unlimited**           | check skipped                                         |
| `0`                   | **Blocked** (₹0 credit) | any order with `balSum > 0` → "Credit Limit Exceeded" |
| `> 0`                 | **Capped** at amount    | enforced normally                                     |

`typeof max_cr_lmt === "number"` now reads cleanly as _"a limit is set"_ (true for `0` and positives; false for `null`/`undefined`). The old `(0,1)` sentinel is **retired**.

> ⚠️ **Core hazard:** `0` and `null` are both falsy. The codebase is littered with truthiness checks (`!max_cr_lmt`, `?? 0`, `x ? x : 0`, `Number(null) === 0`) that bucket them together. Under the new contract they mean **opposites** (blocked vs unlimited). **Every such site must become an explicit `== null` / `=== 0` / `> 0` test.** Missing one = a blocked customer silently shows/behaves as unlimited (or vice-versa). This is the bulk of Phase 4.

## 3. Confirmed decisions

**Status (2026-10-01):** 1 ✅ (a blocked relation whose deposit covers the order can order: `test/api_v3/features/credit/index.test.js:196`); 2 ✅ (`createDC` defaults to `0` for ≥ 1.78: `api_v3/services/dealer_custs.js:1318-1320`, tests `:480-550` of the credit suite); 4 ✅ (write gate `:1479-1494`, tests `collections/dealer_custs/index.test.js:126-149`); 3 ❌ in part — `bf063d4` also moved `api_v2`'s order checks to the new contract (`api_v2/controllers/collections/order_msts.js:342-359`, `:527-545`), and `/api/v1` is not mounted (`dzzlo_oms.js:107`).

1. **Advance deposit + blocked:** a blocked customer (`0`) **can still order against prepaid advance deposit.** → The existing formula `balSum = prevBal + amount − adv_dep` already yields this (when `adv_dep` covers the order, `balSum ≤ 0`, so `0 < balSum` is false → allowed). **No special handling needed.**
2. **New-relationship default = blocked.** New `dealer_custs` rows default `max_cr_lmt` to `0` — gated to `>= 1.78` clients (decision 4). Implemented **server-side in `createDC`** (not via a Mongoose schema `default`, which `.save()` could silently re-apply to migrated-unset rows). See Phase 1 §3.
3. **Do NOT touch API v1/v2.** Only v3 enforcement is changed. Residual risk in Phase 1 §5.
4. **Compatible with the live v1.77 release.** The v1.77 app (bare `TextInput`, `0` = unlimited) hits the same backend. **Version-gate the two write funnels** using the existing `req.headers.meta` → `version` idiom (as in `order_msts.js`): a `0` written by a `<= 1.77` client is stored as `null` (unlimited, old meaning); a `0` from `>= 1.78` is stored as blocked. Order **enforcement** stays uniform (un-gated) — after migration + the write-gate, every stored `0` is a deliberate v1.78 block. v1.77 **display** of a blocked customer shows "no limit" (read-only skew; server still enforces). See Phase 1 §2–§3.

## 4. UI (the new control on `CustSettings`)

**Status (2026-10-01):** ✅ built with the chips "Unlimited" / "Fixed Limit" — the label note was taken up, though not as "Set limit" (`CustSettings.js:92`); the helper note under the chips still says "Fixed Credit" (`:952`, `T08-N2`).

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

**Status (2026-10-01):** ✅ the API and app files changed as listed (evidence in Phases 1, 3 and 4); dip-web rows — not assessed.

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

**Status (2026-10-01):** Phases 1, 3 and 4 ✅; whether the migration ran in the required order (Phase 2) is not recorded in the repos ❔.

1. **Phase 1 — Backend** (enforcement + write normalization + create default).
2. **Phase 2 — Migration & rollout** — _order-sensitive and partly interleaved with the Phase 1 deploy._ Read before deploying anything.
3. **Phase 3 — App setting screen** (`CustSettings` new control).
4. **Phase 4 — All other consumers** (app display + dip-web + tests + verification).

> **Critical rollout order** (full detail in Phase 2): **(a)** run migration step 1 (`0 → $unset`) under OLD code → **(b)** deploy Phase 1 backend → **(c)** run migration steps 2–3 (`(0,1) → 0`, `<0 → 0`). This sequence has **no window** where a customer is mis-classified. Deploying Phase 1 _before_ migrating would instantly block every currently-unlimited (`0`) customer.

## 7. Risk summary

**Status (2026-10-01):** the missed-truthiness risk was re-checked with Phase 4's grep gates on the app — one hit, in an unused component (`T08-N2`); every render site draws the three states (blocked prints `0` rather than "Blocked"). The migration risk stays ❔; the version-skew display risk is closed by the presenter (`test/api_v3/features/credit/index.test.js:403-470`).

- **Irreversible migration** — `0` means opposite things pre/post. Requires DB backup + dry-run counts (Phase 2).
- **Missed truthiness site** — any un-converted `!max_cr_lmt`/`?? 0` shows blocked as unlimited. Phase 4 must be exhaustive; grep gate provided.
- **Mobile version skew** — old app builds in the field interpret `0` as "no limit" (display only; server still enforces blocked). Acceptable; noted in Phase 2 §4.
- **Scope vs the sentinel alternative** — this is ~10× the surface of a `0.01`-sentinel approach (which needed ~2 files, no migration, no enforcement change). Chosen for the cleaner end-state. If scope needs cutting, the sentinel approach delivers the identical dealer UX.

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID     | Task                                                                                                                                                                                                                                                                                    | Why (evidence)                                                                                                                                                                                                                                                                                                | Project | Size | Depends on |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | ---------- |
| T08-N1 | 🆕 Tier 3 test for the v1 `CustSettings` credit-limit control: "Unlimited" sends `max_cr_lmt: null` (never `undefined`), "Fixed Limit" sends `0`, a typed amount sends the 2-dp number, a re-tap sends nothing                                                                          | The control (`src/screens/Dealer/Customers/CustSettings.js:92-510`) has no test — the screen's suites cover its tax and opening-balance sections only (`__tests__/CustSettings.tax.test.js`, `CustSettings.openingBal.test.js`); Phase 1 §2 names the `null`-not-`undefined` hazard, which the API cannot see | app     | S    | —          |
| T08-N2 | 🆕 Two small clean-ups on the credit screens: delete the unused `AccountDetails` in `src/screens/Customer/Dealers/DealerSettings/components.js:58` (it holds the only Gate A hit, `visible={!!maxCrLmt}` at `:165`), and make CustSettings' helper note say "Fixed Limit" like its chip | Grep gate run 2026-10-01; `DealerSettings/index.js:54` imports only `AboutThem` from `./components` and renders its own `AccountDetails` (`:351`, defined at `:943`); the note says "Fixed Credit" (`CustSettings.js:952`) while the chip says "Fixed Limit" (`:92`)                                          | app     | XS   | —          |
