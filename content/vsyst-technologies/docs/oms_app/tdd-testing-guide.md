# TDD Testing Guide — dzzlo_oms_app

> **Status (verified 2026-09-01):** the entire TDD net lives on branch **`app_tdd`** (5 commits ahead of `main`, working tree clean, in sync with origin). **PR #48 is OPEN and unmerged** since 2026-07-10 — `main` has none of this. Suite: **16 files / ~337 tests, ~11 s** (budget ≤ 2 min). Built under tasks_12 (see `../tasks/tasks_12_tdd_testing/`), Phase 4 + 5.
> **PR:** https://github.com/ShikhaR-C/dzzlo_oms_app/pull/48 · **Canonical daily guide in-repo:** `docs/testing.md` (on `app_tdd`)

## 1. What was added (tasks_12, Phases 4–5)

- **Jest 30 harness completed** (preset `react-native` — bare RN 0.84.1, not Expo): `jest.setup.js` now mocks every native module the app imports — Firebase (already there), AsyncStorage, device-info, netinfo, safe-area-context, gesture-handler, `@gorhom/bottom-sheet`, Reanimated v4 (`setUpTests()`), OneSignal. The two **phantom deps** (`react-native-image-picker`, `react-native-permissions` — imported by `src/components/ImagePicker` but deliberately not installed, decision 2026-07-05) are stubbed with `{ virtual: true }`.
- **MSW 2 wired for React Native**: `jest.config.js` redeclares `transform` (adds `.mjs`), maps `msw`/`msw/node` to CJS entries via `moduleNameMapper` (msw's export map declares `"react-native": null`), extends `transformIgnorePatterns`; `jest.resolver.js` composes the Reanimated/worklets resolver. `src/test/msw/server.js` exports one `setupServer()`.
- **Tier 1 — pure-logic unit suites (12 files)**: `src/helpers/Credit` (tri-state max_cr_lmt: null=unlimited / 0=blocked / >0=capped, mirrors the landed tasks_08 API contract), `src/utils/Currency` (Indian grouping, words), `Dates` (fin-year boundaries), `converters/inv_no` (base33 codec + PRNG fuzz), `permissions`, `userLookup`, `validation`, `validators`, `store/slices/auth`, `store/selectors/auth`, `store/apis/paginationHelpers`, `store/apis/preloadedState` (`errorRTK` precedence). Plus `__tests__/App.test.tsx` boot smoke (now has a real assertion).
- **Tier 2 — store-level MSW suites (3 files)**: `auth.endpoints.msw.test.js` (headers + real generated login envelope), `retry.msw.test.js` (4xx fails once, 5xx retries twice), `rtkQueryErrorLogger.msw.test.js` (401 → logout, 403 → company refresh).
- **Tier 3 — RNTL screen tests: deliberately deferred.** `@testing-library/react-native@13` is installed but the render wrapper `src/test/testUtils.js` does not exist yet — it lands with the first screen test (priorities: Login, NewOrder, Payments).
- **Shared fixtures (Phase 5)**: `src/test/fixtures/generated/*.json` are **captured from the API's seeded world** (never hand-edit) — `auth_loginrx`, `auth_updaterx`, `orders_poso`, `dealer_custs_list`, `invoices_list`, `vouchers_list` + `fixtures.meta.json`. Refresh with `yarn fixtures:pull` (copies from `../dzzlo_oms_api/fixtures/api_v3/`). Hand-rolled JSON is allowed only for error bodies (401/403/500), inline in test files.
- **The one production-source change**: `makeStore()` factory exported from `src/store/apis/index.js` (app keeps using the singleton) so every test gets a fresh store.
- **CI**: `.github/workflows/test.yml` — Jest on PRs + pushes to `main`, Node 22, `cp .env.ci .env.testing` then `yarn test`. Plus `.github/PULL_REQUEST_TEMPLATE.md` with the TDD checklist and `docs/testing.md` (233-line runbook).

## 2. How to run

```sh
yarn test                                   # the one command: APP_ENV=testing jest (~11 s)
APP_ENV=testing npx jest --watch inv_no     # watch mode (no test:watch script exists — type it)
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
- **Screen (Tier 3, future)** — first screen test must create `src/test/testUtils.js`: fresh `makeStore()` + `NavigationContainer` + `SafeAreaProvider` + PaperProvider (+ `BottomSheetModalProvider` where needed). Only screens that carry decisions (role/credit/status-conditional rendering) get tests — not pure layout.
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

## 5. Pending / known issues (as of 2026-09-01)

1. **Merge PR #48** — open ~7 weeks; until merged, `main` has zero tests and CI protection.
2. **Tier 3 absent** — RNTL installed but unused; `src/test/testUtils.js` + Login/NewOrder/Payments screen tests are the next build-out.
3. **Fixtures stale by their own rule** — `fixtures.meta.json` says generated 2026-07-09 (> 14-day threshold); `yarn fixtures:pull` prints the STALE warning. Re-run seed + export in the API repo, then pull.
4. **`docs/testing.md` lines ~220–223 are stale** — they warn the test files are untracked; they've been tracked since commit `5f9f586a`. Delete that caveat on the next docs touch.
5. **No `test:watch` script** — worth adding (`"test:watch": "APP_ENV=testing jest --watch"`) since watch mode is the documented TDD loop.
6. `src/notes/Testing/apiTesting.js` is a legacy note, not part of the suite.

## References

- In-repo runbook: `dzzlo_oms_app/docs/testing.md` (branch `app_tdd`) · fixture contract: `src/test/fixtures/generated/README.md`
- Design + implementation record: `../tasks/tasks_12_tdd_testing/04-phase-4-app-foundation.md`, `05-phase-5-shared-fixtures-contract.md`, `07-phase-7-tdd-daily-workflow.md`
- Siblings: [API guide](../oms_api/tdd-testing-guide.md) · [dip-web guide](../dip_web/tdd-testing-guide.md)
