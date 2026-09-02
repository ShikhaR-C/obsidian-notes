# 02 — Foundations: the one-time groundwork in both repos

**Outcome:** after this doc is executed, a screen iteration ([[03-per-screen-playbook]]) touches only additive folders (`api_v4/…`, `test/api_v4/…`, `src/screens/v2/…`, `src/store/apis/v4/…`) and never has to build infrastructure. Every foundation piece is itself built **red → green → refactor**; none of it plans or builds a screen.
**Effort:** Phase 1 (API) 3–5 dev-days · Phase 2 (app) 4–6 dev-days. Sequential: Phase 2's proof is a real `/api/v4/ping` from a dev build against staging.
**Prerequisite:** Phase 0 in [[00-overview#Phase 0 — Prerequisites|00 §Phase 0]] (the three tasks_12 PRs merged, fixtures re-exported, D7/D10 decided).
**Approvals:** listed per step and collected in [[00-overview#Governance|00 §Governance]]. Nothing starts before the user says "start phase 1" / "start phase 2".

---

## Phase 1 — API foundations

Repo `dzzlo_oms_api`, branch `api_v4_foundations` from `master` (after PR #35 is merged). One PR for the phase, one commit pair (red, green) per step.

### Target layout

```
api_v4/
  index.js            router hub — api_key_v3() → protect → check_user_company_status() → routes → v4 error handler
  routes/             one file per screen group or resource; router.use(authorize(...)) at the top of each
  controllers/        thin: validate → read model / command → respond
  readmodels/         one file per screen: compose(api_v3 services + presenters) + project fields per spec §2
  commands/           one file per resource: precondition → api_v3 service call → invalidation hint
  schemas/            request schemas per route (body / query / params)
  lib/
    respond.js        ok(res, data, { page, meta })   fail(next, error_code, status, details)
    errors.js         ApiError + the error_code catalogue
    validate.js       validate({ body, query, params }) middleware
    tenancy.js        tenantOf(req) · assertRelation({ dealer_id, cust_id }) · scopeFilter(req)
    cursor.js         encode / decode · paginate(query, { cursor, limit, sort })
    compose.js        runParallel(map) · runSettled(map, { optional, timeoutMs }) · timing header (non-prod)
api_v/api4.js         mount hub (mirrors api_v/api3.js)                       ⚠️ approval
dzzlo_oms.js          + app.use("/api/v4", api_v4) after the v3 line          ⚠️ approval
test/dzzlo_oms_test.js  same one line, so the in-process test app mounts v4  ⚠️ approval
test/api_v4/
  harness/            mount.test.js · chain.test.js
  lib/                one unit file per lib module
  contract/           fixtures.test.js (drift detector over fixtures/api_v4/)
  temp/               fixtures.captures.js (CAPTURES = [] until the first screen)
  screens/ commands/  empty until the first screen
fixtures/api_v4/      fixtures.meta.json + one JSON per capture
```

`/auth` and `/contact` stay on v3: login is not part of the first screens and the token it issues works for v4 as-is. If a login screen is ever redesigned, its v4 routes mount **before** `protect` in `api_v4/index.js`, exactly as `api_v/api3.js` does.

### F-API-1 — Mount and middleware chain ⚠️ approval (3 files outside `api_v4/`)

- **Red.** `test/api_v4/harness/mount.test.js`, house idiom (`db.connect()`, `beforeAllHelper`, `db.dheader`, the bearer helper the `harness/middleware_chain` suite already uses):
  - `GET /api/v4/ping` with api key + valid bearer → `200 { success: true, data: { version: "v4", now } }`
  - without bearer → `401`, `error_code: "UNAUTHENTICATED"`
  - bearer for a user whose addressed company is INACTIVE / REMOVED / not a member → `403` with the existing `COMPANY_INACTIVE` / `COMPANY_REMOVED` / `NOT_IN_COMPANY` codes (reuse the `features/company_status` scenario setup)
  - missing / wrong `x-api-key` → whatever `api_key_v3()` does today, pinned
  - `chain.test.js`: a route registered without `authorize` is impossible — the hub's `routes/` loader asserts every router file exports its roles (fail fast at boot; the test boots the hub with a fixture router lacking roles and expects a throw)
- **Green.** `api_v4/index.js` (chain above, `GET /ping` as a real route), `api_v/api4.js`, the two mount lines. Confirm `jest.config.js` picks up `test/api_v4/**` without changes (only `testPathIgnorePatterns` exists today).
- **Done when** the four mount cases and the boot assertion are green under `yarn test:full` and no v3 test changed.

### F-API-2 — Envelope, errors, validation ⚠️ approval (new dependency: zod recommended, D7)

- **Red.** `test/api_v4/lib/respond.test.js`, `errors.test.js`, `validate.test.js` (unit) plus a probe route `GET|POST /api/v4/__probe/validate` mounted **only** in `test/dzzlo_oms_test.js` (the `__smoke/whoami` precedent):
  - `ok()` → `{ success: true, data, page?, meta: { generatedAt } }`
  - `ApiError("NOT_FOUND", 404)` through the v4 error handler → `{ success: false, error: <message>, error_code: "NOT_FOUND" }`; unknown errors → `500 INTERNAL` with no stack in the body
  - `validate`: unknown body key → `400 VALIDATION` with `details: [{ path, message }]`; malformed ObjectId → `400`; `limit: "1000"` → coerced and clamped to 100 with `meta.limit` echoing the clamp; `$`-prefixed keys never reach the schema (sanitizeMongo runs earlier — pin it)
- **Green.** The three lib modules and a router-level error handler at the end of `api_v4/index.js` (so `helpers/error.js` stays untouched).
- **Done when** every envelope the app will ever see from v4 is pinned by a test.

### F-API-3 — Tenancy helpers

- **Red.** Unit tests plus probe routes `GET /api/v4/__probe/tenant` (returns `tenantOf(req)`) and `POST /api/v4/__probe/relation` (calls `assertRelation` on the body):
  - dealer token → `{ role: "dealer", co_id, dealer_id: co_id }`; customer token → `cust_id`; the company comes from `x-co-id` resolved the way `check_user_company_status` resolves it
  - `assertRelation`: dealer A + a customer A serves → passes; dealer A + a customer only B serves → `403 FORBIDDEN`; non-existent pair → `403` (not 404 — do not reveal existence)
  - `authorize("dealer")` on a customer token → `403 FORBIDDEN_ROLE`; superadmin on a screens route → `403` (v4 has no superadmin screens until one is specified)
  - `scopeFilter(req)` → `{ dealer_id }` or `{ cust_id }` by role, never both, never empty
- **Green.** `lib/tenancy.js` reusing `api_v3/auth.js` primitives and the unique `{ dealer_id, cust_id }` index on `dealer_custs` for the membership check (one indexed `exists`).
- **Done when** the IDOR pattern documented in the v3 survey is impossible to write in v4 without deleting a helper call — and the mutation smoke proves it (remove `assertRelation` from the probe → exactly the two 403 tests go red).

### F-API-4 — Cursor pagination

- **Red.** `lib/cursor.test.js` (codec round-trip; malformed cursor → `400 VALIDATION`) and a probe list `GET /api/v4/__probe/orders?cursor&limit` over seeded `order_msts` scoped by `scopeFilter`:
  - default `limit` 25, max 100 (clamped, echoed in `meta.limit`); never `limit = 0`
  - page 1 and page 2 are disjoint and ordered `-createdAt, -_id`; inserting a newer document between the two requests leaves page 2 unchanged (the drift bug offset paging has)
  - `page.next` is `null` on the last page; `hasMore` uses the `limit + 1` probe, never a `countDocuments`
- **Green.** `lib/cursor.js` with an opaque base64url cursor over `{ k, _id }` and a `$or` seek condition.
- **Done when** the probe passes and the doc states the rule: **v4 never calls `advancedResults.getResults`.**

### F-API-5 — Compose runner

- **Red.** `lib/compose.test.js` with fake promises: `runParallel` rejects on the first failure; `runSettled` returns `null` for an optional key that threw or timed out and `errors: { key: "TIMEOUT" | "UNAVAILABLE" }` (enum, never `err.message`); a critical key failing rejects the whole call; timing header `X-V4-Timing` present when `NODE_ENV !== "production"` and absent when it is (probe read model composing two seeded queries).
- **Green.** `lib/compose.js`.
- **Done when** a read model author cannot serialise sub-queries by accident: the only sanctioned way to fan out is through these two helpers, and `docs/testing.md` says so.

### F-API-6 — The v4 contract set ⚠️ approval (shared tooling touched)

- **Red.** `test/api_v4/contract/fixtures.test.js` with a single probe capture (`ping`) → green after `yarn fixtures:export:v4`, then a manual teeth check: change the envelope, watch it go red, revert, record.
- **Green.** `test/api_v4/temp/fixtures.captures.js` (`CAPTURES`, `REQUIRED_COLLECTIONS`), `export_fixtures.js` generalised to a `--set v4` argument writing `fixtures/api_v4/` + `fixtures.meta.json`, the compare/scrub logic extracted from the v3 detector into `test/helper/contract.js` so both detectors share it, `scripts/check_fixtures_fresh.js` iterating both sets, and — in the app repo, in F-APP-1 — `scripts/pull_fixtures.js` copying both sets (v4 files land as `v4_<name>.json` + `v4_fixtures.meta.json` beside the v3 ones, so no existing import moves).
- **Done when** `bash scripts/release_gate.sh` checks freshness of both sets.

### F-API-7 — Docs, governance, CI ⚠️ approval (`AI.md`, versioning agent)

- `docs/testing.md`: a "v4" section (idiom, probe routes, the two rules above, fixture commands) and a v4 block in the flow map (harness rows only for now).
- `AI.md` Active Development Rule → "New contracts are written inside `api_v4/`. `api_v3/` changes only as test-first bugfix PRs. `api_v2/`, `api_v1/`, `models/`, `helpers/` unchanged." `.ai/agents/versioning-agent.md` gains the `/api/v4` row (Active — screen read models + commands). `docs/ARCHITECTURE.md`'s three stale statements are corrected while there.
- `.github/PULL_REQUEST_TEMPLATE.md`: one added line — "v4: one tenancy test per id the body accepts".
- CI: no change (`test:full` already runs everything).
- **Phase 1 done when:** `yarn test:full` green with the new harness/lib/contract suites; staging serves `GET /api/v4/ping` to a bearer; the release gate passes with two fixture sets; no v3 test changed; the PR body records every mutation smoke.

---

## Phase 2 — App foundations

Repo `dzzlo_oms_app`, branch `app_v4_foundations` from `main` (after PR #48 is merged). One PR for the phase.

### Target layout

```
src/utils/API/index.js         + export API_URL_V4 = `${API_URL}${API_VERSION_PATH_V4}`
src/store/apis/v4/
  base.js                      v4Url(path) → absolute URL · shared v4 tag names
  index.js                     injectEndpoints: v4_ping
  __tests__/ping.msw.test.js
src/test/
  testUtils.js                 renderScreen(ui, { preloadedState, route, params, handlers })
  msw/handlers/v4.js           v4Ok(slug, fixture) · v4Fail(slug, status, error_code)
  fixtures/generated/v4_*.json (pulled)
src/theme/
  tokens/{palette,typography,spacing,radii,elevation}.js
  themes/{light,dark,index}.js
  adapters/{toPaperTheme,toNavigationTheme}.js
  provider/{ThemeProvider,useAppTheme}.js
src/components/v2/             AppText · Box · Screen  (MoneyText, StatusChip only when a spec needs them)
src/navigation/screenRegistry.js · useScreenFlag.js
src/screens/v2/                empty until the first screen
.env.development/.testing/.production/.ci/.example   + API_VERSION_PATH_V4=/api/v4   ⚠️ approval
```

### F-APP-1 — The v4 client ⚠️ approval (five env files)

- **Red.** `src/store/apis/v4/__tests__/ping.msw.test.js` on a fresh `makeStore()` with `server.listen({ onUnhandledRequest: "error" })`:
  - `api.endpoints.v4_ping.initiate()` hits **exactly** `<API_URL>/api/v4/ping` (absolute; not `${baseUrl}/ping`) with `authorization`, `x-co-id`, `x-api-key`, `meta`
  - 5xx retried twice, 4xx not (mirror `retry.msw.test.js`)
  - `data` is unwrapped from `{ success, data }`; a `403 { error_code }` reaches `errorRTK` with the code preserved (extend `preloadedState.test.js`)
- **Green.** The env var in all five files, `API_URL_V4`, `base.js`, `index.js`, `pull_fixtures.js` extended for the v4 set (see F-API-6). `fetchBaseQuery` leaves absolute URLs alone — the test proves it rather than assuming it.
- **Done when** the suite is green and a dev build against staging logs the ping response once at boot (visible only in the dev-only Demo/Redux screen — no production screen changes).

### F-APP-2 — The Tier 3 harness

- **Red.** `src/test/__tests__/testUtils.test.js` renders a probe component (reads a selector, navigates, fires `v4_ping` through MSW) and asserts the text, the navigation call and that the request was seen.
- **Green.** `testUtils.js` wrapping `makeStore()` + `NavigationContainer` + `SafeAreaProvider` (with initial metrics) + `PaperProvider` + `BottomSheetModalProvider`; `withMsw(handlers)` lifecycle helper that hard-codes the unhandled-request guard; `msw/handlers/v4.js`; `"test:watch": "APP_ENV=testing jest --watch"` added to `package.json` (open item #5 in the app guide).
- **Done when** the probe test is green and `docs/testing.md` documents `renderScreen` as the only way to write a Tier 3 test.

### F-APP-3 — Design tokens, theme, primitives (tasks_04 Phases 1–3, scoped) ⚠️ approval if restyle is installed

- **Step 0 — re-validate restyle.** Check `@shopify/restyle`'s current release against RN 0.84 / React 19 (peer deps, last publish date, open issues). Record the verdict in this doc's log. Fallback if it fails: plain token objects + Paper MD3 theme + `AppText`/`Box` written on `StyleSheet` — same API surface for screens, no new dependency.
- **Red.** `src/theme/__tests__/`:
  - **parity:** `toPaperTheme(themes.light)` deep-equals the colours of the legacy `Light` export in `src/utils/Colors/index.js`, and dark likewise — the tokens reproduce today's look exactly on day one, so old and new screens never look like two apps
  - `typography` exposes the 15 MD3 variants with numeric `lineHeight` and `letterSpacing`
  - `AppText` applies the variant, never sets `allowFontScaling={false}` or a `maxFontSizeMultiplier` (uncapped scaling per tasks_04)
  - `Box`/`Screen` map spacing tokens; `Screen` provides safe-area insets
  - ESLint: `no-restricted-syntax` forbidding hex/rgb literals and numeric `fontSize`, scoped by `overrides` to `src/screens/v2/**`, `src/components/v2/**`, `src/theme/**` — enforced by the existing lint job (verify the app has a lint script; add one if not)
- **Green.** Tokens (palette lifted from `Colors/index.js`, fixed brand tokens from `SVG/psoc`), themes, adapters, `ThemeProvider` mounted **around** the existing `PaperProvider` in `AppNavigatorContainer` (legacy `useTheme` callers unaffected because the adapter yields the same Paper object), the three primitives.
- **Deliberately not:** restyling any existing screen; custom fonts; neon theme; redux-persist for theme (tasks_04 Phase 6 items stay deferred).
- **Done when** parity tests are green and the app looks pixel-identical before/after on the device (screenshot pair in the PR).

### F-APP-4 — Screen registry and cutover

- **Red.** `src/navigation/__tests__/screenRegistry.test.js`: `resolveScreen("Orders")` → the v1 component when nothing is registered; v2 when registered and the flag is on; v1 when the flag is off; unknown route throws in `__DEV__`. `useScreenFlag(slug)` returns `true` when Remote Config is unavailable, throws, or times out (default-on, 5 s), and reads the cached value otherwise.
- **Green.** `screenRegistry.js` (`register(route, { v1, v2 })`, `resolveScreen`) and `useScreenFlag.js` (Remote Config adapter behind an interface, or a static map if D10 is decided as release-only). Navigators are **not** rewritten now — a navigator file is switched to `resolveScreen` only for the route whose v2 screen is being shipped. Verify the `@react-native-firebase/remote-config` mock in `jest.setup.js` and that Remote Config is initialised at boot (it is a dependency; initialisation is unverified).
- **Done when** the registry has zero entries, the tests are green, and flipping the flag on staging is documented.

### F-APP-5 — Strings and error-code mapping

- **Red.** `src/utils/__tests__/errorCodes.test.js`: every v4 `error_code` in the catalogue maps to user copy; unknown codes fall back to the existing `errorRTK` message; precedence with network errors unchanged.
- **Green.** `src/utils/errorCodes.js`; `errorRTK` consults it; the convention `src/screens/v2/<Name>/strings.js` documented (the app has no i18n layer — one file per screen keeps copy testable and later translatable).

### F-APP-6 — Docs

- `docs/testing.md`: Tier 3 section, v4 fixtures, `test:watch`; delete the stale "untracked files" caveat (open item #4 in the app guide). Vault: update `../tdd-testing-guide.md` §5 (Tier 3 no longer absent) and `../../oms_api/tdd-testing-guide.md` §1 (v4 contract set).
- `.github/PULL_REQUEST_TEMPLATE.md`: "Tier 3 decision tests written red-first" line.
- **Phase 2 done when:** `yarn test` green inside 2 minutes; `renderScreen` proven; parity screenshots attached; registry and flag tests green; a dev build pings `/api/v4` on staging; release gate PASS.

---

## Foundations decision log

| Date | Item | Decision |
| --- | --- | --- |
| 2026-09-03 | Layouts above | drafted; awaiting "start phase 1" |
| — | restyle re-validation (F-APP-3 step 0) | pending |
| — | D7 validation library | pending (zod recommended) |
| — | D10 kill-switch | pending (Remote Config recommended) |
