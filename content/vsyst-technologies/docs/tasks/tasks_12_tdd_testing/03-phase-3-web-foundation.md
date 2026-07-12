# Phase 3 — Web Foundation (`dip-web`)

**Outcome:** `yarn test` actually runs a suite (Vitest + RTL + MSW), wired exactly as the repo's own CRA→Vite migration plan Phase 5 prescribed; the highest-risk pages have first tests; no test can reach a network.
**Effort:** 2–4 dev-days.

> **TDD lens:** the repo already decided its runner — `src/docs/plans/cra-to-vite-migration.plan.md` → "Phase 5: Testing (Deferred)" specifies Vitest + jsdom + `src/setupTests.js` and keeps the installed `@testing-library/*` deps. This phase **executes that plan** (reconciled, not reinvented) and adds the missing piece it didn't mention: MSW, because every page speaks RTK Query to absolute remote URLs and the local-only principle forbids real requests.

---

## 3.0 Triage the existing Vitest spike first (added 2026-07-09)

Unmerged remote branch `origin/claude/transaction-tests-issue-10` (tip `1b16244`, "test: add Vitest suite for transaction list CRUD, pagination, filters") already contains +2,261 lines of test scaffolding: a `vite.config.js` test block, `src/setupTests.js` (154 lines), `src/test-utils/renderWithProviders.jsx`, a **hand-rolled** `src/test-utils/mockApi.js` (297 lines), store tests (`src/store/dipApis/{decants,insps,meter_reads}.test.js`), page tests (`InspsList`, `MeterReadList`) and a smoke test.

Before writing anything in §3.1–3.4, spend ≤ half a day reconciling:

- **Harvest**: the page/store test _cases_ (they encode real expected behavior for the P2 DIP flows) and any jsdom stubs its `setupTests.js` proved necessary — rebase them onto this phase's structure.
- **Replace**: `mockApi.js` with MSW (§3.2–3.3) — a hand-rolled fetch mock is exactly the drift-prone claim layer Phase 5 exists to kill; do not merge it as-is.
- **Reconcile paths**: the spike uses `src/test-utils/`; this plan specifies `src/test/` — pick one (default: this plan's `src/test/`) and record the verdict here.
- **Verdict per file** goes in the PR that lands §3.2–3.3; the branch is then closed with a pointer to it (no test deleted without a written verdict — Phase 7 §7.4 rule).

## 3.1 Dependencies & scripts

`package.json` (devDependencies to add; ⏳ Q5 for the two upgrades):

```
vitest@^3            jsdom            msw@^2
@testing-library/jest-dom@^6         @testing-library/user-event@^14
```

`@testing-library/react` stays at 13 (React 18 line). Scripts:

```json
"test": "vitest run",
"test:watch": "vitest",
"test:coverage": "vitest run --coverage"
```

The placeholder echo (`No test runner configured — see Phase 5`) is replaced — its referent is now implemented, and `cra-to-vite-migration.plan.md` gets a one-line addendum noting Phase 5 was completed by tasks_12 Phase 3.

## 3.2 Config — `vite.config.js` test block + `src/setupTests.js`

`vite.config.js` (the migration plan's own snippet, extended):

```js
export default defineConfig({
  // ...existing config (react plugin, esbuild jsx-in-.js loader — Vitest inherits both)...
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/setupTests.js",
    css: false,
    restoreMocks: true,
  },
})
```

`src/setupTests.js` (new):

```js
import "@testing-library/jest-dom/vitest"
import { server } from "./test/msw/server"

// jsdom gaps the app relies on
class IO {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.IntersectionObserver = globalThis.IntersectionObserver || IO // infinite-query sentinels
window.matchMedia =
  window.matchMedia || (() => ({ matches: false, addEventListener() {}, removeEventListener() {} }))

beforeAll(() => server.listen({ onUnhandledRequest: "error" })) // local-only principle, enforced
afterEach(() => {
  server.resetHandlers()
  localStorage.clear()
})
afterAll(() => server.close())
```

`onUnhandledRequest: "error"` is the guarantee that no test can silently hit `VITE_API_URL` (all env files point at remote servers and there is no Vite proxy — verified).

## 3.3 Test infrastructure — `src/test/`

```
src/test/
  msw/server.js        ← setupServer(...handlers)
  msw/handlers.js      ← wildcard-origin handlers per endpoint family
  fixtures/            ← hand-rolled now; generated from API seed in Phase 5
  testUtils.js         ← renderWithProviders
```

`src/test/msw/handlers.js` — match by path, not origin, so env URLs don't matter:

```js
import { http, HttpResponse } from "msw"
import login from "../fixtures/auth_loginrx.json"

export const handlers = [
  http.post("*/api/v3/auth/loginrx", () => HttpResponse.json(login)),
  http.get("*/api/dip/v1/dealers/:id", () => HttpResponse.json(/* dealer fixture */)),
  // add per test via server.use(...) for error cases
]
```

`src/test/testUtils.js` — every component needs Provider + Router + Theme (verified render requirements):

```js
import { render } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { Provider } from "react-redux"
import { makeStore } from "../store/apis" // small refactor: export a store factory alongside the singleton
import { ThemeProvider } from "../utils/Hooks/themeContext"

export function renderWithProviders(ui, { route = "/", store = makeStore(), auth = null } = {}) {
  if (auth) localStorage.setItem("userData", JSON.stringify(auth)) // token shape: {userId, ..., token, expiryDate}
  return {
    store,
    ...render(
      <Provider store={store}>
        <ThemeProvider>
          <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
        </ThemeProvider>
      </Provider>,
    ),
  }
}
```

Note the one production touch: `src/store/apis/index.js` exports a `makeStore()` factory (same `configureStore` call it already makes) so each test gets a fresh store — without it, RTK Query cache leaks across tests. The app keeps using the existing singleton.

## 3.4 First tests — highest-risk pages/hooks

Priority order (each is one PR-sized unit):

1. **Auth**: `src/pages/auth/SignIn` — superadmin direct-login branch vs dealer two-step OTP (`loginCredentialVerify` → `loginOTP`); the `transformResponse` rejection `"Only RO Admin Login"` for disallowed role/scope. (Rules from `docs/auth-and-roles.md`.)
2. **Permission gating**: `src/routes/PermissionRoute.js` + `src/utils/Hooks/usePermissions.js` — `DPrimary`/`DAdmin` bypass, `dip.enabled` requirement, `dip.<resource>.<action>` matrix, denial renders Alert (not redirect). Mostly `renderHook` + one route render.
3. **Unit**: `src/utils/permissions.js`, `errorRTK` (message extraction precedence), `networkStatus` slice (FETCH_ERROR → `setNetworkError`, debounced clear — drive via store dispatch with MSW network-error handler).
4. **One master page**: `Products` — renders from the single `useFetch_dealerQuery` (`useDealerData`), inline CRUD modal opens, mutation invalidates and refetches (assert via MSW request log).
5. **One transaction page**: `DecanList` — infinite query renders page 1, IO stub prevents crashes; `mRAdd`-style form page validation smoke.
6. **Auto-login**: `App.js` `tryLogin()` — valid `userData` + future `expiryDate` → authenticated route tree; expired → logout path.

Conventions: tests colocate next to the unit (`src/pages/auth/SignIn/signin.test.js` — lowercase like the component files), store tests snake_case mirroring `docs`' file-placement rules; every test file must pass ESLint (existing `lint.yml` CI covers it).

## 3.5 CI note (⏳ Q8)

`.github/workflows/lint.yml` already exists and is active; when Q8 confirms GitHub Actions, add a sibling `test.yml` running `yarn test` (Phase 6 owns the gate wiring; this phase just keeps the suite CI-compatible — no watch mode, no interactive prompts).

## 3.6 Verification — how we know Phase 3 is done

- `yarn test` runs Vitest and exits non-zero on a deliberately broken assertion (prove the gate can fail).
- All §3.4 items 1–3 landed and green; 4–6 landed or explicitly carried into a follow-up note here.
- Temporarily pointing a fixture handler at a wrong path makes the run **error on unhandled request** (proves the no-network guard).
- Suite runtime ≤ 1 min locally (⏳ Q10).

## Phase 3 checklist

- [x] §3.0 spike triage: `claude/transaction-tests-issue-10` harvested/replaced with written per-file verdicts (`src/docs/plans/tasks12-phase3-spike-triage.md`)
- [x] Deps added: vitest, jsdom, msw@2, jest-dom@6, user-event@14
- [x] `vite.config.js` `test` block (css:false, restoreMocks) — **plus a custom environment** (see notes)
- [x] `src/setupTests.js` with jest-dom, MSW lifecycle, IO/matchMedia stubs, localStorage shim, `onUnhandledRequest: "error"`
- [x] `src/test/` infra: server, handlers, fixtures, `renderWithProviders` (+ `makeStoreWithUser`)
- [x] `makeStore()` factory exported from `src/store/apis/index.js` (singleton preserved)
- [x] `package.json` test scripts replaced (echo removed); migration plan annotated
- [x] First tests: SignIn (4), PermissionRoute/usePermissions (6), errorRTK (6), networkStatus slice (7), permissions units (~14). Master/transaction page + tryLogin **deferred** (infra proven; carry-over below).
- [x] §3.6 verification passes (deliberate-fail → non-zero; unhandled request → MSW error; runtime 1.2s ≪ 1 min)

## Phase 3 — implementation notes (executed 2026-07-09/10, branch `web_tdd`)

**Result:** `yarn test` runs Vitest; **5 files / 32 tests green**, ~1.2s. ESLint clean on all new files (repo `--max-warnings 0` gate). Only production touch: `makeStore()` in `src/store/apis/index.js`.

**The hard problem — jsdom vs Node fetch realm (root-caused & fixed 2026-07-10).** RTK Query's `fetchBaseQuery` builds a `new AbortController()` from the global and hands its signal to `fetch`/`new Request`. Vitest's stock `jsdom` environment installs **jsdom's** `AbortController`/`AbortSignal` over Node's native ones, and Node's fetch (undici, which MSW uses) rejects a jsdom signal with `RequestInit: Expected signal to be an instance of AbortSignal` — so **every** networked test died. The native classes are unrecoverable once jsdom replaces them (probed: `delete` → undefined; no `require`able source; `undici` doesn't export them). Fix: a **custom Vitest environment** `src/test/env/jsdom-fetch.js` that snapshots the native fetch stack (fetch/Request/Response/Headers/AbortController/AbortSignal/Blob/…) from the pristine worker global, runs `builtinEnvironments.jsdom.setup`, then restores the native classes over jsdom's. Referenced by relative path: `environment: "./src/test/env/jsdom-fetch.js"`. The agent's earlier `fetchRealm.js` undici-swap (which missed AbortController) was removed. _This is the reusable pattern for any jsdom + MSW + RTK Query suite._

**Carry-over (deferred, infra proven):** master page (Products), transaction page (DecanList — harvest spike cases), `App.js` tryLogin — all now unblocked by the working env; land in a follow-up PR.
