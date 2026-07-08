# Phase 4 — App Foundation (`dzzlo_oms_app`)

**Outcome:** the app suite grows past the assertion-free `App.test.tsx`: native-module mocks complete in `jest.setup.js`, the pure business-logic layer unit-tested, RTK Query layer tested against MSW with a hard no-network guard, and the first RNTL screen tests on money-path screens.
**Effort:** 3–5 dev-days.

> **TDD lens:** the app has an unusually rich pure layer (currency words, financial-year dates, credit-state machine, base33 invoice codec, permission predicates, pagination cache logic). That's where unit TDD pays off immediately — no emulator, no mocks, milliseconds. Screens come second, e2e is deliberately out of scope (⏳ Q6).

---

## 4.1 Dependencies, mocks, and config

Add (devDependencies): `@testing-library/react-native@^13` (React 19-compatible), `msw@^2`.

`jest.config.js` — extend, keeping the preset:

```js
module.exports = {
  preset: 'react-native',
  setupFiles: ['<rootDir>/jest.setup.js'],
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|@react-navigation|@react-native-firebase|@react-native-community|@react-native-async-storage|react-native-.*|@gorhom|@shopify/flash-list)/)',
  ],
};
```

`jest.setup.js` — additions in the existing style (Firebase mocks already present, keep them):

```js
// storage / device / network
jest.mock('@react-native-async-storage/async-storage', () =>
  require('@react-native-async-storage/async-storage/jest/async-storage-mock'),
);
jest.mock('react-native-device-info', () =>
  require('react-native-device-info/jest/react-native-device-info-mock'),
);
jest.mock('@react-native-community/netinfo', () =>
  require('@react-native-community/netinfo/jest/netinfo-mock.js'),
);

// UI natives
require('react-native-gesture-handler/jestSetup');
jest.mock('@gorhom/bottom-sheet', () => require('@gorhom/bottom-sheet/mock'));
require('react-native-reanimated').setUpTests(); // reanimated v4 testing setup — confirm exact call per v4 docs

// push
jest.mock('react-native-onesignal', () => ({
  OneSignal: { initialize: jest.fn(), Notifications: { requestPermission: jest.fn() }, InAppMessages: {}, User: {} },
}));

// phantom deps — imported by src/components/ImagePicker but NOT installed (flagged to team):
jest.mock('react-native-image-picker', () => ({ launchImageLibrary: jest.fn(), launchCamera: jest.fn() }), { virtual: true });
jest.mock('react-native-permissions', () => ({ request: jest.fn(), check: jest.fn(), PERMISSIONS: {}, RESULTS: {} }), { virtual: true });
```

The two `virtual: true` mocks are the confirmed approach (2026-07-05) — keep them stubbed for now rather than installing the real packages; revisit later.

**Env note:** `yarn test` → `APP_ENV=testing` → `react-native-dotenv` inlines `.env.testing` (**remote staging URL**) into `@env` imports. That is acceptable *only because* every network path is intercepted: MSW's `onUnhandledRequest: 'error'` (§4.3) turns any real request attempt into a test failure — the local-only principle, enforced mechanically. If this ever chafes, add `.env.jest` + a `test:jest` script; not needed now.

`__tests__/App.test.tsx` stays as the boot smoke (it's the one test that catches provider-wiring breakage), but gains one assertion (e.g. startup screen testID) so it can actually fail.

## 4.2 Tier 1 — pure-logic unit suites (TDD-ready, zero native deps)

One `__tests__/` folder next to each module; all paths verified to exist:

| Module | What to pin |
| --- | --- |
| `src/utils/Currency/index.js` | `formatCurrency`/`formatQty` Indian grouping; `roundDecimal`; `price_in_words`/`amtWords` (lakh/crore words — classic regression magnet) |
| `src/utils/Dates/index.js` | `getCurrentFinancialYear`/`getLastFinYY` around April boundary (mock system time), `msToHMS`, `DateIST` |
| `src/utils/validators.js` + `src/utils/validation.js` | email/phone/password/name acceptance tables |
| `src/utils/permissions.js` + `src/utils/userLookup.js` | owner/admin predicates, `canEditUser`/`canDeleteUser`, company lookup/enrichment |
| `src/utils/converters/inv_no.js` | base33 encode/decode round-trip property (`de_base33_id(en_id_base33(x)) === x`), `trimInvNo` |
| `src/helpers/Credit/index.js` | `creditState`/`isUnlimited`/`isBlocked`/`isCapped`/`creditUtilization` — mirrors the **landed** tasks_08 API contract (null=unlimited, 0=blocked, >0=capped; amended 2026-07-09). Pin it as-is, incl. `creditUtilization`'s adv_dep-as-spending-power pool (`pool = max_cr_lmt + adv_dep`, `6a8109a8`) and the `pool === 0` → fully-utilised edge, in lockstep with API Phase 2 §2.2.3 |
| `src/store/apis/paginationHelpers.js` | `serializeQueryArgs`/`merge` sliding-window dedupe, `forceRefetch` |
| `src/store/apis/preloadedState.js` | `errorRTK` status→message mapping precedence |
| `src/store/selectors/auth.js` | representative selectors against a fixture state |
| `src/store/slices/auth.js` | reducer paths (`authenticate`, `setCredentials`, `logout`) — module imports AsyncStorage + `createApi`, both now mocked in setup |

## 4.3 Tier 2 — RTK Query layer against MSW

`src/test/msw/server.js` mirrors the web setup (`msw/node`; Node ≥ 22 has fetch). A store-level integration test per critical endpoint family, no rendering:

- Build a fresh store (export a `makeStore()` factory from `src/store/apis/index.js`, same move as web Phase 3 §3.3).
- `store.dispatch(api.endpoints.auth_login.initiate({...}))` against an MSW fixture → assert fulfilled data shape, `prepareHeaders` sent `x-api-key`/`x-co-id`/Bearer (MSW request assertion).
- `rtkQueryErrorLogger` middleware: MSW returns 401 on a non-auth endpoint → `logoutUser` dispatched; 403 with `error_code: COMPANY_INACTIVE` → `updateCurr_User_Comp` refresh latch.
- Retry wrapper: 4xx does **not** retry (`retry.fail`), 5xx retries twice — assert via MSW handler call counts.

Server lifecycle in each suite (or a shared setup): `server.listen({ onUnhandledRequest: 'error' })` — the no-cloud guard.

## 4.4 Tier 3 — RNTL screen tests (small, money-path first)

Wrapper `src/test/testUtils.js`: fresh store Provider + `NavigationContainer` + `SafeAreaProvider` + PaperProvider (+ `BottomSheetModalProvider` where needed). First screens:

1. **Login** (`src/screens/Login/AuthNavigator/Login.js`) — credential verify → OTP step → success dispatches `logInSlice`; error path renders `errorRTK` message.
2. **NewOrder** (`src/screens/Customer/NewOrder/`) — happy path submits expected payload (MSW request assertion); credit-blocked response renders the blocking message (pairs with API Phase 2 §2.2.3).
3. **Payments approval** (`src/screens/Dealer/Payments/` or `Common/Payments/`) — voucher approve action fires the right mutation and updates the list via tag invalidation.

Everything deeper (PDF render, WebView flows, Paytm, camera, push, drawer gestures) is classified e2e-only and stays out until Q6 is answered.

## 4.5 Verification — how we know Phase 4 is done

- `yarn test` green with Tiers 1–2 complete and ≥ 2 Tier-3 screens; runtime ≤ 2 min (⏳ Q10).
- Deliberately un-mock one handler → suite fails with MSW unhandled-request error (proves no staging/cloud contact is possible).
- `App.test.tsx` can fail (assertion added).
- Mutation smoke (Phase 2 §2.5 ritual) on `creditState` and `inv_no` suites.

## Phase 4 checklist

- [ ] `@testing-library/react-native` + `msw` installed; `transformIgnorePatterns` extended
- [ ] `jest.setup.js`: async-storage, device-info, netinfo, gesture-handler, bottom-sheet, reanimated, OneSignal mocks; virtual mocks for the two phantom deps (team decision on installing them recorded)
- [ ] Tier 1 unit suites for all §4.2 modules
- [ ] `makeStore()` factory + Tier 2 store/MSW suites (headers, 401/403 middleware, retry policy)
- [ ] Tier 3: Login, NewOrder, one Payments-approval screen
- [ ] `App.test.tsx` gains a real assertion
- [ ] No-network guard demonstrated (§4.5)
