# TDD Testing Guide — dzzlo_oms_app

> **Status (verified 2026-09-03):** **PR #48 is MERGED into `slave`** (2026-09-03, merge commit `a7c32d7`; the user retargeted the PR from `main` to `slave` the same day, so `slave` leads `main` by 10 commits until the next release merge). Suite on `slave`: **16 files / 337 tests, ~10 s** locally (CI 1m16s; budget ≤ 2 min). Generated fixtures refreshed from API seed `v3_2026-09-03` (`9bb942f3`); cross-repo `release_gate.sh` printed **PASS** on 2026-09-03. Branch `app_v4_foundations` = `slave` + 11 commits = **draft PR #49 → `slave`** (screen-redesign Phase 2, 2026-09-04: v4 client on the shared slice, Tier 3 harness `renderScreen`/`withMsw`, error-code copy, theme tokens + `AppText`/`Box`/`Screen` with a parity test against the legacy `Light`/`Dark`, screen registry + toggle hooks; suite 337 → **626 in ~3 s**; v4 fixture set pulled as `v4_*.json`) — awaiting the user's merge, never merged by Fable. Built under tasks_12 (see `../tasks/tasks_12_tdd_testing/`), Phase 4 + 5.
> **PR:** https://github.com/ShikhaR-C/dzzlo_oms_app/pull/48 · **Canonical daily guide in-repo:** `docs/testing.md` (on `app_tdd`)

## 1. What was added (tasks_12, Phases 4–5)

- **Jest 30 harness completed** (preset `react-native` — bare RN 0.84.1, not Expo): `jest.setup.js` now mocks every native module the app imports — Firebase (already there), AsyncStorage, device-info, netinfo, safe-area-context, gesture-handler, `@gorhom/bottom-sheet`, Reanimated v4 (`setUpTests()`), OneSignal. The two **phantom deps** (`react-native-image-picker`, `react-native-permissions` — imported by `src/components/ImagePicker` but deliberately not installed, decision 2026-07-05) are stubbed with `{ virtual: true }`.
- **MSW 2 wired for React Native**: `jest.config.js` redeclares `transform` (adds `.mjs`), maps `msw`/`msw/node` to CJS entries via `moduleNameMapper` (msw's export map declares `"react-native": null`), extends `transformIgnorePatterns`; `jest.resolver.js` composes the Reanimated/worklets resolver. `src/test/msw/server.js` exports one `setupServer()`.
- **Tier 1 — pure-logic unit suites (12 files)**: `src/helpers/Credit` (tri-state max_cr_lmt: null=unlimited / 0=blocked / >0=capped, mirrors the landed tasks_08 API contract), `src/utils/Currency` (Indian grouping, words), `Dates` (fin-year boundaries), `converters/inv_no` (base33 codec + PRNG fuzz), `permissions`, `userLookup`, `validation`, `validators`, `store/slices/auth`, `store/selectors/auth`, `store/apis/paginationHelpers`, `store/apis/preloadedState` (`errorRTK` precedence). Plus `__tests__/App.test.tsx` boot smoke (now has a real assertion).
- **Tier 2 — store-level MSW suites (3 files)**: `auth.endpoints.msw.test.js` (headers + real generated login envelope), `retry.msw.test.js` (4xx fails once, 5xx retries twice), `rtkQueryErrorLogger.msw.test.js` (401 → logout, 403 → company refresh).
- **Tier 3 — RNTL screen tests: harness landed 2026-09-04 (PR #49, screen-redesign F-APP-2).** `src/test/testUtils.js` exports `renderScreen(ui, { preloadedState, route, params, handlers })` (fresh `makeStore(preloadedState)` + `SafeAreaProvider` + `PaperProvider` + `BottomSheetModalProvider` + a one-screen `NavigationContainer`) and `withMsw(handlers)` (hard-codes the unhandled-request guard); `src/test/msw/handlers/v4.js` has `v4Ok`/`v4Fail`. Template: `src/test/__tests__/testUtils.test.js`. Decision-only tests, for `src/screens/v2/**`.
- **Shared fixtures (Phase 5)**: `src/test/fixtures/generated/*.json` are **captured from the API's seeded world** (never hand-edit) — `auth_loginrx`, `auth_updaterx`, `orders_poso`, `dealer_custs_list`, `invoices_list`, `vouchers_list` + `fixtures.meta.json`. Refresh with `yarn fixtures:pull` (copies from `../dzzlo_oms_api/fixtures/api_v3/`). Hand-rolled JSON is allowed only for error bodies (401/403/500), inline in test files.
- **The one production-source change**: `makeStore()` factory exported from `src/store/apis/index.js` (app keeps using the singleton) so every test gets a fresh store.
- **CI**: `.github/workflows/test.yml` — Jest on PRs + pushes to `main`, Node 22, `cp .env.ci .env.testing` then `yarn test`. Plus `.github/PULL_REQUEST_TEMPLATE.md` with the TDD checklist and `docs/testing.md` (233-line runbook).

## 2. How to run

```sh
yarn test                                   # the one command: APP_ENV=testing jest (~11 s)
yarn test:watch                             # watch mode (script added 2026-09-04, PR #49)
APP_ENV=testing npx jest Credit             # one file; pattern is a REGEX over the FULL path
yarn fixtures:pull                          # refresh generated fixtures from the API repo
```

Gotchas (all real, all documented in `docs/testing.md`):

- **`APP_ENV` must be set** — otherwise dotenv loads `.env.development` and can throw (`allowUndefined: false`).
- Path patterns include `/__tests__/`: `npx jest src/utils/converters/inv_no` matches **nothing**; use `inv_no`.
- `.env.testing` points at **remote staging** — safe only because every MSW suite runs `server.listen({ onUnhandledRequest: "error" })`: any real network attempt fails the test. Keep that guard in every new MSW suite.
- No coverage script/thresholds exist (coverage is observability-only per tasks_12 Q9; the app never even wired it).

## 3. How to write tests here

- **Unit (Tier 1)** — colocate in `__tests__/` next to the module. No native deps, no mocks beyond what `jest.setup.js` already provides. This layer is where TDD pays off: milliseconds per run.
- **Store/MSW (Tier 2)** — build a fresh store with `makeStore()`, dispatch `api.endpoints.X.initiate(...)` against MSW handlers, assert data shape / headers / middleware effects. Own the server lifecycle per suite with the unhandled-request guard.
- **Screen (Tier 3)** — `renderScreen` from `src/test/testUtils.js` is the only way to render a screen in a test (PR #49); pass `handlers` for the v4 responses (`v4Ok`/`v4Fail`) and `preloadedState` for auth. Only screens that carry decisions (role/credit/status-conditional rendering) get tests — not pure layout.
- **One layer per rule**: don't re-prove an API rule in a screen test; assert the screen _reacts_ to the API's answer.
- **Mutation smoke** (teeth check for any new suite): temporarily break the rule in the source (e.g. flip `creditState`'s 0→BLOCKED), watch the suite go red, revert. Record it in the PR.

## 4. How to tackle changes (the playbook)

| Change                        | What to do                                                                                                                                                                                                                                                                                                            |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **New feature (screen/flow)** | Put the business rules in `src/utils` / `src/helpers` / slices **first**, unit-test them TDD-style (red → green → refactor, watch mode running). Screen gets an RNTL test only if it carries decisions. New RTK Query endpoints get a Tier-2 store/MSW test if they carry headers/error semantics beyond the default. |
| **Bugfix**                    | **Mandatory test-first, no exceptions.** Reproduce as a failing test at the _lowest_ layer that shows it (most app bugs reproduce in a util/selector/slice test; screen-level only if the bug _is_ the wiring). Name it after the symptom, reference the report. Fix. The test is never deleted.                      |
| **Refactor**                  | `yarn test` green before and after; no behavior change ⇒ no assertion change. If you must edit assertions, it wasn't a refactor.                                                                                                                                                                                      |
| **API contract changed**      | In the API repo: `yarn seed && yarn fixtures:export`, commit. Here: `yarn fixtures:pull`, commit the refreshed `src/test/fixtures/generated/`, suites green — all **within the same release**.                                                                                                                        |
| **New native package**        | Add its mock to `jest.setup.js` (use the package's shipped jest mock if it has one); if it ships ESM, extend `transformIgnorePatterns`.                                                                                                                                                                               |
| **Touching credit logic**     | `src/helpers/Credit` tests pin the tasks_08 contract in lockstep with the API's `features/credit` suite — change both sides together or the release gate catches you.                                                                                                                                                 |
| **Release prep**              | `yarn test` here, then the cross-repo gate: `bash dzzlo_oms_api/scripts/release_gate.sh` from the `v1_79/` workspace. Green gate or no release.                                                                                                                                                                       |

PR checklist (enforced by the PR template): bugfix PRs contain the regression test written first · no test deleted/`.skip`'d without a written verdict · runtime budget respected (≤ 2 min) · fixtures refreshed if the API contract moved.

## 5. Pending / known issues (as of 2026-09-03)

1. ~~Merge PR #48~~ — **done 2026-09-03** into `slave` (`a7c32d7`). `main` receives it at the next release merge; until then `main` itself still has no tests or CI protection.
2. ~~Tier 3 absent~~ — **`renderScreen` exists since 2026-09-04** (`src/test/testUtils.js`, PR #49): real store, navigation, providers, MSW via `withMsw`; template `src/test/__tests__/testUtils.test.js`. Decision-only screen tests for `src/screens/v2/**`; legacy Login/NewOrder/Payments screen tests remain a possible later build-out.
3. ~~Fixtures stale~~ — **done 2026-09-03** (`9bb942f3`: pulled from API seed `v3_2026-09-03`; gate PASS).
4. ~~`docs/testing.md` untracked-files caveat~~ — removed in PR #49 (F-APP-6).
5. ~~No `test:watch` script~~ — added in PR #49 (`APP_ENV=testing jest --watch`).
6. `src/notes/Testing/apiTesting.js` is a legacy note, not part of the suite.

## References

- In-repo runbook: `dzzlo_oms_app/docs/testing.md` (on `slave` since 2026-09-03) · fixture contract: `src/test/fixtures/generated/README.md`
- Design + implementation record: `../tasks/tasks_12_tdd_testing/04-phase-4-app-foundation.md`, `05-phase-5-shared-fixtures-contract.md`, `07-phase-7-tdd-daily-workflow.md`
- Siblings: [API guide](../oms_api/tdd-testing-guide.md) · [dip-web guide](../dip_web/tdd-testing-guide.md)
