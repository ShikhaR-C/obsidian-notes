# Phase 4 — App Foundation (`dzzlo_oms_app`)

**Outcome:** the app suite grows past the assertion-free `App.test.tsx`: native-module mocks complete in `jest.setup.js`, the pure business-logic layer unit-tested, RTK Query layer tested against MSW with a hard no-network guard, and the first RNTL screen tests on money-path screens.
**Effort:** 3–5 dev-days.

> **TDD lens:** the app has an unusually rich pure layer (currency words, financial-year dates, credit-state machine, base33 invoice codec, permission predicates, pagination cache logic). That's where unit TDD pays off immediately — no emulator, no mocks, milliseconds. Screens come second, e2e is deliberately out of scope (⏳ Q6).

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). 🟡 Tiers 1 and 2 are complete and have grown (v4 MSW suites for Customers, Daily Summary, features and ping); the Tier 3 wrapper this phase deferred now exists as `renderScreen`, built by the screen redesign and used by 35 test files, 14 of them v1 screens. Of the three first screens, Login and Payments approval are partly covered and NewOrder not at all; one new task (`X-APP-7`). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## 4.1 Dependencies, mocks, and config

**Status (2026-10-01):** ✅ done — RNTL 13 and msw 2 in devDependencies; `jest.setup.js` mocks async-storage, device-info, netinfo, gesture-handler, bottom-sheet, reanimated and OneSignal (`:50-224`) and keeps the two phantom deps as virtual mocks (`:248-255`; still not installed); msw is pinned through `jest.config.js` `moduleNameMapper` (`:22-23`); `__tests__/App.test.tsx` asserts the large boot spinner.

Add (devDependencies): `@testing-library/react-native@^13` (React 19-compatible), `msw@^2`.

`jest.config.js` — extend, keeping the preset:

```js
module.exports = {
  preset: "react-native",
  setupFiles: ["<rootDir>/jest.setup.js"],
  transformIgnorePatterns: [
    "node_modules/(?!(react-native|@react-native|@react-navigation|@react-native-firebase|@react-native-community|@react-native-async-storage|react-native-.*|@gorhom|@shopify/flash-list)/)",
  ],
}
```

`jest.setup.js` — additions in the existing style (Firebase mocks already present, keep them):

```js
// storage / device / network
jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock"),
)
jest.mock("react-native-device-info", () =>
  require("react-native-device-info/jest/react-native-device-info-mock"),
)
jest.mock("@react-native-community/netinfo", () =>
  require("@react-native-community/netinfo/jest/netinfo-mock.js"),
)

// UI natives
require("react-native-gesture-handler/jestSetup")
jest.mock("@gorhom/bottom-sheet", () => require("@gorhom/bottom-sheet/mock"))
require("react-native-reanimated").setUpTests() // reanimated v4 testing setup — confirm exact call per v4 docs

// push
jest.mock("react-native-onesignal", () => ({
  OneSignal: {
    initialize: jest.fn(),
    Notifications: { requestPermission: jest.fn() },
    InAppMessages: {},
    User: {},
  },
}))

// phantom deps — imported by src/components/ImagePicker but NOT installed (flagged to team):
jest.mock(
  "react-native-image-picker",
  () => ({ launchImageLibrary: jest.fn(), launchCamera: jest.fn() }),
  { virtual: true },
)
jest.mock(
  "react-native-permissions",
  () => ({ request: jest.fn(), check: jest.fn(), PERMISSIONS: {}, RESULTS: {} }),
  { virtual: true },
)
```

The two `virtual: true` mocks are the confirmed approach (2026-07-05) — keep them stubbed for now rather than installing the real packages; revisit later.

**Env note:** `yarn test` → `APP_ENV=testing` → `react-native-dotenv` inlines `.env.testing` (**remote staging URL**) into `@env` imports. That is acceptable _only because_ every network path is intercepted: MSW's `onUnhandledRequest: 'error'` (§4.3) turns any real request attempt into a test failure — the local-only principle, enforced mechanically. If this ever chafes, add `.env.jest` + a `test:jest` script; not needed now.

`__tests__/App.test.tsx` stays as the boot smoke (it's the one test that catches provider-wiring breakage), but gains one assertion (e.g. startup screen testID) so it can actually fail.

## 4.2 Tier 1 — pure-logic unit suites (TDD-ready, zero native deps)

**Status (2026-10-01):** ✅ every module in the table has a suite at `ea7e7222` (e.g. `src/helpers/Credit/__tests__/index.test.js`, 24 tests; `src/utils/converters/__tests__/inv_no.test.js`); Tier 1 has since grown with the redesign's and 1.79's helpers (`helpers/Filters`, `helpers/DateRange`, `helpers/DailySummary`, `helpers/Auth`, `helpers/Invoice`, `helpers/Tax`).

One `__tests__/` folder next to each module; all paths verified to exist:

| Module                                                 | What to pin                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/utils/Currency/index.js`                          | `formatCurrency`/`formatQty` Indian grouping; `roundDecimal`; `price_in_words`/`amtWords` (lakh/crore words — classic regression magnet)                                                                                                                                                                                                                                               |
| `src/utils/Dates/index.js`                             | `getCurrentFinancialYear`/`getLastFinYY` around April boundary (mock system time), `msToHMS`, `DateIST`                                                                                                                                                                                                                                                                                |
| `src/utils/validators.js` + `src/utils/validation.js`  | email/phone/password/name acceptance tables                                                                                                                                                                                                                                                                                                                                            |
| `src/utils/permissions.js` + `src/utils/userLookup.js` | owner/admin predicates, `canEditUser`/`canDeleteUser`, company lookup/enrichment                                                                                                                                                                                                                                                                                                       |
| `src/utils/converters/inv_no.js`                       | base33 encode/decode round-trip property (`de_base33_id(en_id_base33(x)) === x`), `trimInvNo`                                                                                                                                                                                                                                                                                          |
| `src/helpers/Credit/index.js`                          | `creditState`/`isUnlimited`/`isBlocked`/`isCapped`/`creditUtilization` — mirrors the **landed** tasks_08 API contract (null=unlimited, 0=blocked, >0=capped; amended 2026-07-09). Pin it as-is, incl. `creditUtilization`'s adv_dep-as-spending-power pool (`pool = max_cr_lmt + adv_dep`, `6a8109a8`) and the `pool === 0` → fully-utilised edge, in lockstep with API Phase 2 §2.2.3 |
| `src/store/apis/paginationHelpers.js`                  | `serializeQueryArgs`/`merge` sliding-window dedupe, `forceRefetch`                                                                                                                                                                                                                                                                                                                     |
| `src/store/apis/preloadedState.js`                     | `errorRTK` status→message mapping precedence                                                                                                                                                                                                                                                                                                                                           |
| `src/store/selectors/auth.js`                          | representative selectors against a fixture state                                                                                                                                                                                                                                                                                                                                       |
| `src/store/slices/auth.js`                             | reducer paths (`authenticate`, `setCredentials`, `logout`) — module imports AsyncStorage + `createApi`, both now mocked in setup                                                                                                                                                                                                                                                       |

## 4.3 Tier 2 — RTK Query layer against MSW

**Status (2026-10-01):** ✅ `src/store/apis/__tests__/{auth.endpoints,retry}.msw.test.js`, `src/store/middleware/__tests__/rtkQueryErrorLogger.msw.test.js`, plus the v4 suites `src/store/apis/v4/__tests__/{customers,daily_summary,features,ping}.msw.test.js`. The retry suite pins "a 5xx is retried twice" (`retry.msw.test.js:50`), which `X-APP-1` in tasks_01 wants changed for `QUERY_TIMEOUT`.

`src/test/msw/server.js` mirrors the web setup (`msw/node`; Node ≥ 22 has fetch). A store-level integration test per critical endpoint family, no rendering:

- Build a fresh store (export a `makeStore()` factory from `src/store/apis/index.js`, same move as web Phase 3 §3.3).
- `store.dispatch(api.endpoints.auth_login.initiate({...}))` against an MSW fixture → assert fulfilled data shape, `prepareHeaders` sent `x-api-key`/`x-co-id`/Bearer (MSW request assertion).
- `rtkQueryErrorLogger` middleware: MSW returns 401 on a non-auth endpoint → `logoutUser` dispatched; 403 with `error_code: COMPANY_INACTIVE` → `updateCurr_User_Comp` refresh latch.
- Retry wrapper: 4xx does **not** retry (`retry.fail`), 5xx retries twice — assert via MSW handler call counts.

Server lifecycle in each suite (or a shared setup): `server.listen({ onUnhandledRequest: 'error' })` — the no-cloud guard.

## 4.4 Tier 3 — RNTL screen tests (small, money-path first)

**Status (2026-10-01):** 🟡 the wrapper exists — `renderScreen` in `src/test/testUtils.js:277-376` (Redux → Language → SafeArea → Paper → BottomSheetModal → Navigation), with MSW, window, font-scale, keyboard and language options. First screens: Login 🟡 (`src/screens/Login/AuthNavigator/__tests__/Login.resume.test.js`, `ForgotPassword.resume.test.js` — resume and success paths on a hand-built provider stack, no error-path case); NewOrder ⬜ (no test under `src/screens/Customer/NewOrder`); Payments approval 🟡 (`src/screens/Dealer/Payments/__tests__/PromptPay.tds.test.js` approves a TDS Note on account, `PromptPay.invoiceTap.test.js`; no invoice or AdvDep approval case and no list-refresh assertion).

Wrapper `src/test/testUtils.js`: fresh store Provider + `NavigationContainer` + `SafeAreaProvider` + PaperProvider (+ `BottomSheetModalProvider` where needed). First screens:

1. **Login** (`src/screens/Login/AuthNavigator/Login.js`) — credential verify → OTP step → success dispatches `logInSlice`; error path renders `errorRTK` message.
2. **NewOrder** (`src/screens/Customer/NewOrder/`) — happy path submits expected payload (MSW request assertion); credit-blocked response renders the blocking message (pairs with API Phase 2 §2.2.3).
3. **Payments approval** (`src/screens/Dealer/Payments/` or `Common/Payments/`) — voucher approve action fires the right mutation and updates the list via tag invalidation.

Everything deeper (PDF render, WebView flows, Paytm, camera, push, drawer gestures) is classified e2e-only and stays out until Q6 is answered.

## 4.5 Verification — how we know Phase 4 is done

**Status (2026-10-01):** 🟡 the no-network guard holds (`withMsw` listens with `onUnhandledRequest: 'error'`, `src/test/testUtils.js:200`) and `App.test.tsx` can fail; runtime is the open point — the only recorded full-suite times are CI's, 128.8–171.3 s (runs 36760183167, 36708907732, 36779552256), against a 2-min budget set for local runs (`X-CI-2` in tasks_02).

- `yarn test` green with Tiers 1–2 complete and ≥ 2 Tier-3 screens; runtime ≤ 2 min (⏳ Q10).
- Deliberately un-mock one handler → suite fails with MSW unhandled-request error (proves no staging/cloud contact is possible).
- `App.test.tsx` can fail (assertion added).
- Mutation smoke (Phase 2 §2.5 ritual) on `creditState` and `inv_no` suites.

## Phase 4 checklist

**Status (2026-10-01):** 6 ✅, 1 🟡 — marks at the end of each line.

- [x] `@testing-library/react-native` + `msw` installed; `transformIgnorePatterns` extended (+ a `jest.resolver.js` for MSW's export map) — **2026-10-01:** ✅.
- [x] `jest.setup.js`: async-storage, device-info, netinfo, gesture-handler, bottom-sheet, reanimated, OneSignal mocks; virtual mocks for the two phantom deps (kept stubbed — not installed) — **2026-10-01:** ✅ (`jest.setup.js:50-255`).
- [x] Tier 1 unit suites for all §4.2 modules — **2026-10-01:** ✅.
- [x] `makeStore()` factory + Tier 2 store/MSW suites (headers, 401/403 middleware, retry policy) — **2026-10-01:** ✅.
- [~] Tier 3: **deferred** — Login/NewOrder/Payments screens carried to a follow-up (Tier 1+2 are the phase's value). _Correction (2026-07-10): no RNTL wrapper `src/test/testUtils.js` was created — `@testing-library/react-native@13` is installed but the wrapper lands with the first screen test, not before. Only `src/test/msw/server.js` + `src/test/fixtures/generated/` exist under `src/test/`._ — **2026-10-01:** 🟡 the wrapper now exists (`renderScreen`, `src/test/testUtils.js:277-376`, built by the redesign's Phase 2); NewOrder ⬜, Login and Payments 🟡 (§4.4).
- [x] `App.test.tsx` gains a real assertion (asserts ≥1 large spinner on boot) — **2026-10-01:** ✅.
- [x] No-network guard demonstrated (§4.5) — **2026-10-01:** ✅.

## Phase 4 — implementation notes (executed 2026-07-09/10, branch `app_tdd`)

**Status (2026-10-01):** the untracked-files caveat no longer applies — the suites were committed (app PR #48, merged into `slave` 2026-09-03, now in `main`).

**Result:** `yarn test` (= `APP_ENV=testing jest`) green — **16 suites / 337 tests**, ~11s (≪ 2-min budget). Only production touch: `makeStore()` in `src/store/apis/index.js` (singleton preserved). Tiers 1 (pure logic: Currency, Dates, validators, validation, permissions, userLookup, inv_no, Credit, paginationHelpers, preloadedState, selectors/auth, slices/auth) and 2 (MSW store-level: `auth.endpoints`, `rtkQueryErrorLogger` 401/403, `retry` 4xx/5xx) complete.

**Verification performed 2026-07-10:**

- **Mutation smoke (§4.5 / §2.5):** broke `creditState` (0→BLOCKED rule) → 6 Credit tests red; broke `inv_no` base33 modulo (33→32) → 11 red; both restored → green. Confirms the suites have teeth.
- **No-network guard:** all MSW suites use `server.listen({ onUnhandledRequest: "error" })`; breaking a handler path made the request unhandled → MSW "intercepted a request without a matching request handler" → suite red. Restored.
- ⚠️ Note for future mutation smokes: these test files are **untracked**, so `git checkout --` cannot restore an edited one — reverse edits manually or from a backup copy.

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID      | Task                                                                                                                                                                                                                                     | Why (evidence)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Project | Size | Depends on |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- | ---- | ---------- |
| X-APP-7 | 🆕 Tier 3 harness drift: mount the v2 `ThemeProvider` in `renderScreen` (or correct `useAppTheme`'s hint), decide whether Tier 3 now covers v1 screens and say so in `AI.md`, and refresh two stale lines in the app's `docs/testing.md` | `renderScreen` wraps Redux → Language → SafeArea → Paper → BottomSheetModal → Navigation with no `ThemeProvider` (`src/test/testUtils.js:346-372`), so every v2 suite adds its own (`Customers.test.js:381`, `DailySummary.test.js:171`), while `src/theme/provider/useAppTheme.js:19-24` says "use renderScreen()"; `AI.md:34` scopes Tier 3 to `src/screens/v2/**` though 14 v1 suites use `renderScreen`; `docs/testing.md:182` ("43 suites, 925 cases") and `:1121` ("single-language today") are stale | app     | S    | —          |

The same row is listed in `00-overview.md`.
