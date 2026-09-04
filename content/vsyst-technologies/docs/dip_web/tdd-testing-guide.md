# TDD Testing Guide — dip-web

> **Status (verified 2026-09-03):** **PR #23 is MERGED into `slave_dev`** (2026-09-03, merge commit `23ac5b0`; the user retargeted the PR to `slave_dev` and merged `slave` into `web_tdd` beforehand, so `slave_dev` now leads `main`/`slave` by 7 commits until the next release merge). The `istDayEnd` credit-window fix (`b513fba`, PR #26) finally has its regression test — `src/utils/ledgerCheck.test.js` (`2b5efec`, 14 cases, teeth-checked). **PR #27** (`web_v4_foundations` → `slave_dev`, 2026-09-04, screen-redesign F-WEB-1: superadmin screen-toggle section `AppFeatures.js` + 8 tests) is open, CI green, awaiting the user's merge. Suite on `slave_dev`: **6 files / 46 tests, ~1.2 s** (7 / 54 with PR #27) (CI: Vitest 51 s + ESLint + Review Commits; budget ≤ 1 min). Generated fixtures refreshed from API seed `v3_2026-09-03` (`5d289a9`); cross-repo `release_gate.sh` printed **PASS** on 2026-09-03. Built under tasks_12 (see `../tasks/tasks_12_tdd_testing/`), Phase 3 + 5.
> **PR:** https://github.com/ShikhaR-C/dip-web/pull/23 · **Canonical runbook in-repo:** `docs/testing.md` (on `web_tdd`)

## 1. What was added (tasks_12, Phases 3 + 5)

- **Vitest 3 wired for real** — `yarn test` used to be a placeholder echo. Now: `vitest run` with the test block inside `vite.config.js` (`globals: true`, `css: false`, `restoreMocks: true`, inert `VITE_*` values), executing the repo's own CRA→Vite migration plan "Phase 5: Testing (Deferred)". Deps: `vitest@3`, `jsdom`, `msw@2`, `@testing-library/react@13` (React 18 line), `jest-dom@6`, `user-event@14`.
- **The custom environment — the sharp edge, do not revert.** `src/test/env/jsdom-fetch.js` snapshots Node's native fetch stack (fetch/Request/Response/Headers/AbortController/AbortSignal/Blob/…) before jsdom setup and restores it after. Without it, RTK Query's `fetchBaseQuery` hands a jsdom `AbortSignal` to undici and **every networked test dies** with "Expected signal to be an instance of AbortSignal". Switching `environment` back to plain `"jsdom"` breaks the suite. (This is the reusable pattern for any jsdom + MSW + RTK Query setup.)
- **`src/setupTests.js`**: jest-dom matchers, MSW lifecycle with **`onUnhandledRequest: "error"`** (the local-only guarantee — all env API URLs are remote and there is no Vite proxy, so any un-mocked request fails the test), RTL cleanup, `localStorage.clear()`, shims for `IntersectionObserver`/`matchMedia`, and an in-memory `MemoryStorage` (works around Node 25's stub localStorage).
- **Test infra** under `src/test/`: `msw/server.js` + `msw/handlers.js` (5 path-matched wildcard-origin DIP handlers: loginrx, loginCredentialVerify, loginOTP, dealers/:id, decants), `testUtils.js` with `renderWithProviders(ui, {route, store, auth})` (Redux Provider + ThemeProvider + MemoryRouter; `auth` seeds `localStorage("userData")`) and `makeStoreWithUser()`.
- **First suites (32 tests)**: `pages/auth/SignIn/signin.test.js` (superadmin direct login vs dealer two-step OTP, non-DIP-user rejection, local validation before network), `routes/PermissionRoute.test.js` (`dip.enabled`, `dip.<resource>.<action>` matrix, bypass scopes, denial alerts), `utils/permissions.test.js` (11 pure-unit cases), `store/apis/errorRTK.test.js` (message-extraction precedence), `store/slices/networkStatus.test.js`.
- **The one production-source change**: `makeStore()` factory exported from `src/store/apis/index.js` (singleton preserved) — fresh RTK Query cache per test.
- **Fixtures, two kinds** (Phase 5): hand-rolled DIP JSON in `src/test/fixtures/` (DIP can't be captured from the API test app yet — awaiting "Phase 2b" DIP mounting), and generated `/api/v3` envelopes in `src/test/fixtures/generated/` pulled via `yarn fixtures:pull` from `../dzzlo_oms_api/fixtures/api_v3/` (plumbing wired; currently imported by nothing, by design).
- **Spike triage**: the old `claude/transaction-tests-issue-10` Vitest spike (PR #15) was harvested/superseded with per-file verdicts in `src/docs/plans/tasks12-phase3-spike-triage.md`; its hand-rolled `mockApi.js` was rejected in favor of MSW.
- **CI + docs**: `.github/workflows/test.yml` ("Vitest", Node 20, PRs + push to `main`), PR template with the TDD checklist, `docs/testing.md` runbook. Note: ESLint runs via husky `lint-staged` + `lint.yml` CI — **there is no `yarn lint` script**; the exact CI command is `npx eslint src/ --ext .js,.jsx --max-warnings 0`.

## 2. How to run

```sh
yarn test                                       # full run (vitest run), ~1.5 s
yarn test:watch                                 # TDD loop
npx vitest run src/utils/permissions.test.js    # single file
npx vitest run -t "permission"                  # by test name
npx vitest list                                 # enumerate without running
yarn fixtures:pull                              # refresh generated /api/v3 fixtures from the API repo
yarn test:coverage                              # ⚠️ BROKEN — @vitest/coverage-v8 not installed
```

Gotchas:

- Every test file must pass ESLint at `--max-warnings 0` (CI gate).
- Husky `pre-commit`/`pre-push` **test** lines are commented out — only CI runs tests automatically; run `yarn test` yourself before pushing.
- Node prints an `ExperimentalWarning` about localStorage per worker — noise, handled by the `MemoryStorage` shim.

## 3. How to write tests here

- **Colocate** `*.test.js` next to the unit (lowercase like component files; store tests snake_case per the repo's file-placement rules).
- **Pages**: `renderWithProviders(<SignIn />, { route, auth })`; happy paths use fixtures via the default handlers, error cases override per-test with `server.use(http.post("*/api/dip/v1/…", () => HttpResponse.json({...}, { status: 403 })))`. Handlers match by **path with wildcard origin** so env URLs never matter.
- **Hooks/logic**: extract into a hook/util and unit-test it (`renderHook` for hooks); this is the TDD-fast layer.
- **RTK Query endpoints**: follow the tag rules (`docs/rtk-query-conventions.md`); where the UI depends on invalidation-driven refetch, assert it.
- **One layer per rule**: don't re-prove an API rule here — assert the page _reacts_ to the API's answer.
- **Mutation smoke** for new suites: break the rule in source, confirm the test goes red, revert, record in the PR.

## 4. How to tackle changes (the playbook)

| Change                               | What to do                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **New feature (page/hook/endpoint)** | Extract logic into a hook/util and unit-test it first (`yarn test:watch`); page behavior gets an RTL test with MSW fixtures (generated for happy paths once DIP capture exists, `server.use(...)` for errors); tests land **in the same PR**.                                                                                                                                                                    |
| **Bugfix**                           | **Mandatory test-first** — component-level if visual/behavioral, hook/util-level if logic. The test is never deleted. Worked example: the `istDayEnd`/`ledgerCheck.js` fix (`b513fba`, PR #26) shipped with **no test**; the regression test was added afterwards as `src/utils/ledgerCheck.test.js` (`2b5efec`, 2026-09-03) — it pins the IST day/month/FY boundaries and one `computeLedgerCheck` case where an invoice stamped 23:59:59 IST today counts in the raw window while one dated tomorrow does not. |
| **Refactor**                         | `yarn test` green before and after; assertions unchanged.                                                                                                                                                                                                                                                                                                                                                        |
| **API contract changed**             | API repo: `yarn seed && yarn fixtures:export`, commit. Here: `yarn fixtures:pull`, commit refreshed `src/test/fixtures/generated/`, suites green — same release. (DIP-endpoint changes: update the hand-rolled fixtures in `src/test/fixtures/` and mark them, until Phase 2b makes them capturable.)                                                                                                            |
| **New RTK Query endpoint family**    | Add a path-matched MSW handler + fixture; keep `onUnhandledRequest: "error"` — never silence it.                                                                                                                                                                                                                                                                                                                 |
| **Release prep**                     | `yarn test` (ESLint rides husky/CI), plus `yarn fixtures:pull` first if the API contract moved; then the cross-repo gate `bash dzzlo_oms_api/scripts/release_gate.sh`.                                                                                                                                                                                                                                           |

PR checklist (template): bugfix PRs contain the regression test written first · screen-risk note for new flows · no test deleted/`.skip`'d without a written verdict · runtime budget ≤ 1 min · fixtures refreshed on contract change.

## 5. Pending / known issues (as of 2026-09-03)

1. ~~Merge PR #23~~ — **done 2026-09-03** into `slave_dev` (`23ac5b0`). `main` receives it at the next release merge; until then `main` itself still has zero tests, no test CI, no runbook.
2. ~~`istDayEnd` untested~~ — **done 2026-09-03** (`2b5efec`, `src/utils/ledgerCheck.test.js`).
3. **`yarn test:coverage` broken** — add `@vitest/coverage-v8` as a devDependency.
4. **Carried-over tests never shipped**: Products master page, DecanList transaction page (+ the harvested spike cases for decants/insps/meter_reads stores and InspsList/MeterReadList pages), `App.js` `tryLogin()` — infra is proven, these are the next build-out.
5. ~~Generated fixtures stale~~ — **refreshed 2026-09-03** (`5d289a9`, seed `v3_2026-09-03`); still unused, and `src/test/fixtures/factories.js` stays dead code until the transaction tests land.
6. **Husky test hooks commented out** — decide: re-enable `yarn test` on pre-push (1.5 s suite makes this cheap) or rely on CI only.
7. **Docs gaps**: `docs/README.md` reading order omits `testing.md`; `CLAUDE.md`/AI context has no testing section (AI agents get no signal a suite exists); `docs/auth-and-roles.md` still says "Only RO Admin Login" (code/tests use "DIP access not enabled for this user") — flagged, deliberately unfixed.

## References

- In-repo: `docs/testing.md`, `src/docs/plans/tasks12-phase3-spike-triage.md`, `src/test/fixtures/README.md` (branch `web_tdd`)
- Design + implementation record: `../tasks/tasks_12_tdd_testing/03-phase-3-web-foundation.md`, `05-phase-5-shared-fixtures-contract.md`, `07-phase-7-tdd-daily-workflow.md`
- Siblings: [API guide](../oms_api/tdd-testing-guide.md) · [app guide](../oms_app/tdd-testing-guide.md)
