# 02 — Foundations: the one-time groundwork in both repos

**Outcome:** after this doc is executed, a screen iteration ([[03-per-screen-playbook]]) touches only additive folders (`api_v4/…`, `test/api_v4/…`, `src/screens/v2/…`, `src/store/apis/v4/…`) and never has to build infrastructure. Every foundation piece is itself built **red → green → refactor**; none of it plans or builds a screen.
**Effort:** Phase 1 (API) 3–5 dev-days · Phase 2 (app) 4–6 dev-days. Sequential: Phase 2's proof is a real `/api/v4/ping` from a dev build against staging.
**Prerequisite:** Phase 0 in [[00-overview#Phase 0 — Prerequisites|00 §Phase 0]] (the three tasks_12 PRs merged, fixtures re-exported; D7 and D10 were both decided 2026-09-03 — house validator, house screen toggles, no new dependencies).
**Approvals:** listed per step and collected in [[00-overview#Governance|00 §Governance]]. Nothing starts before the user says "start phase 1" / "start phase 2".

---

## Phase 1 — API foundations

Repo `dzzlo_oms_api`, branch `api_v4_foundations` — equals `slave` @ `2ca0301` since Phase 0 (PR #35 merged there on 2026-09-03; the PR for this phase targets `slave`, not `master`). One PR for the phase, one commit pair (red, green) per step.

### Target layout

```
api_v4/
  index.js            router hub — api_key_v3() → protect → check_user_company_status() → routes → v4 error handler
  routes/             one file per screen group or resource; router.use(authorize(...)) at the top of each
    app.js            GET /app/features — the screen-toggle read, all roles (F-API-8)
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
- **Built 2026-09-04** — see the F-API-2 note below. Route-module contract: `{ path, roles, router }`, the loader throws at boot on a missing/empty `roles`; `requireRole` is v4's own three-line check raising `FORBIDDEN_ROLE` (v3 `authorize` is not reused because its only signal is message text). The test app mounts `buildV4({ probes })` so probe routes sit inside the real chain and cannot exist in production.

### F-API-2 — Envelope, errors, validation (D7: house validator, no dependency)

The validator is written in-house (D7, decided 2026-09-03). It is a small schema DSL, ~100–150 lines, plain objects in, `details` array out. **Rule:** v4 never imports a third-party validation library; when a route needs a shape the DSL cannot express, the DSL gains that rule test-first in the same PR.

- **Red.** `test/api_v4/lib/respond.test.js`, `errors.test.js`, `validate.test.js` (unit) plus a probe route `GET|POST /api/v4/__probe/validate` mounted **only** in `test/dzzlo_oms_test.js` (the `__smoke/whoami` precedent):
  - `ok()` → `{ success: true, data, page?, meta: { generatedAt } }`
  - `ApiError("NOT_FOUND", 404)` through the v4 error handler → `{ success: false, error: <message>, error_code: "NOT_FOUND" }`; unknown errors → `500 INTERNAL` with no stack in the body
  - `validate.test.js`, one test per rule of the DSL: types `string` / `number` / `boolean` / `date` / `objectId` / `enum` / `array` / `object`; `required` vs optional (absent optional keys are simply absent in the output, never `undefined` placeholders); `min` / `max` as length for strings and arrays and as value for numbers and dates; `enum` membership; `items` for arrays (each element validated, path reported as `lines[2].qty`); `fields` for nested objects; **unknown keys rejected at every level**, not just the top; query-string coercion (`"1000"` → `1000`, `"true"` → `true`, `"2026-09-03"` → Date) applied to `query` and `params` only, never to `body`; an empty schema accepts `{}` and rejects any key; a schema is frozen after definition (`Object.freeze`) so a controller cannot mutate it
  - through the probe route: unknown body key → `400 VALIDATION` with `details: [{ path, message }]` listing **every** failure, not just the first; malformed ObjectId → `400`; `limit: "1000"` → coerced and clamped to 100 with `meta.limit` echoing the clamp; `$`-prefixed keys never reach the schema (sanitizeMongo runs earlier — pin it)
- **Green.** `lib/validate.js` (the DSL and the `validate({ body, query, params })` middleware), `lib/respond.js`, `lib/errors.js`, and a router-level error handler at the end of `api_v4/index.js` (so `helpers/error.js` stays untouched). `schemas/` files are plain objects built from the DSL, one export per route, so the app fixture author and the reviewer can read a route's contract without running anything.
- **Done when** every envelope the app will ever see from v4 is pinned by a test and the mutation smoke proves the validator: delete the unknown-key check, exactly the unknown-key tests go red.
- **Built 2026-09-04** (commits `98e8957` red → `76c22d1` green; F-API-1 `6b86fc8` → `5c5f4f5`): 143 tests (mount 13 · chain 9 · envelope 24 · respond 10 · errors 43 · validate 44). DSL as specified plus `default` and `clamp` (needed by F-API-4). Two facts pinned as-is: `api_key_v3` and `check_user_company_status` answer with their v3 bodies (no `success` key) because they reply directly, not through the v4 handler; and `type: "date"` is **query/params only** — a JSON body cannot carry a Date and body coercion stays off. **Decision (Fable, 2026-09-04):** body dates are ISO-8601 strings; the DSL gains an explicit `isoDate` rule test-first in the first PR whose spec carries a body date (no Phase-1 spec does). Mutation smokes: unknown-key loop → exactly 8 red; `protect` removed → the five 401s red (plus 24 collateral, since nothing else sets `req.user`).

### F-API-3 — Tenancy helpers

- **Red.** Unit tests plus probe routes `GET /api/v4/__probe/tenant` (returns `tenantOf(req)`) and `POST /api/v4/__probe/relation` (calls `assertRelation` on the body):
  - dealer token → `{ role: "dealer", co_id, dealer_id: co_id }`; customer token → `cust_id`; the company comes from `x-co-id` resolved the way `check_user_company_status` resolves it
  - `assertRelation`: dealer A + a customer A serves → passes; dealer A + a customer only B serves → `403 FORBIDDEN`; non-existent pair → `403` (not 404 — do not reveal existence)
  - `authorize("dealer")` on a customer token → `403 FORBIDDEN_ROLE`; superadmin on a screens route → `403` (v4 has no superadmin screens until one is specified)
  - `scopeFilter(req)` → `{ dealer_id }` or `{ cust_id }` by role, never both, never empty
- **Green.** `lib/tenancy.js` reusing `api_v3/auth.js` primitives and the unique `{ dealer_id, cust_id }` index on `dealer_custs` for the membership check (one indexed `exists`).
- **Done when** the IDOR pattern documented in the v3 survey is impossible to write in v4 without deleting a helper call — and the mutation smoke proves it (remove `assertRelation` from the probe → exactly the two 403 tests go red).
- **Built 2026-09-04** (`66531c7` → `3608e0f`): 48 tests. `tenantOf` returns **string** ids, `scopeFilter` returns ObjectId instances and throws `FORBIDDEN_ROLE` for superadmin (an empty filter would read as "all tenants"); `assertRelation` answers not-related and does-not-exist with the same 403 body (no existence oracle), malformed ids 400. Smoke: probe without `assertRelation` → 7 red (five 403s + the customer-side twin + the 400).

### F-API-4 — Cursor pagination

- **Red.** `lib/cursor.test.js` (codec round-trip; malformed cursor → `400 VALIDATION`) and a probe list `GET /api/v4/__probe/orders?cursor&limit` over seeded `order_msts` scoped by `scopeFilter`:
  - default `limit` 25, max 100 (clamped, echoed in `meta.limit`); never `limit = 0`
  - page 1 and page 2 are disjoint and ordered `-createdAt, -_id`; inserting a newer document between the two requests leaves page 2 unchanged (the drift bug offset paging has)
  - `page.next` is `null` on the last page; `hasMore` uses the `limit + 1` probe, never a `countDocuments`
- **Green.** `lib/cursor.js` with an opaque base64url cursor over `{ k, _id }` and a `$or` seek condition.
- **Done when** the probe passes and the doc states the rule: **v4 never calls `advancedResults.getResults`.**
- **Built 2026-09-04** (`b168cc1` → `bf3b287`): 71 tests + `test/api_v4/lib/conventions.test.js` (scans `api_v4/` for `advancedResults` → the rule is enforced, not just documented). Wire format: unpadded base64url of `{ k, _id, t?: "date" }`, opaque to clients. `paginate` adds the sort key to a projection that omits it. Smokes: drop the `_id` tie-breaker → 7 red (all in the lib suite, which manufactures a four-row tie — the seed has none); fetch `limit` instead of `limit + 1` → 23 red.

### F-API-5 — Compose runner

- **Red.** `lib/compose.test.js` with fake promises: `runParallel` rejects on the first failure; `runSettled` returns `null` for an optional key that threw or timed out and `errors: { key: "TIMEOUT" | "UNAVAILABLE" }` (enum, never `err.message`); a critical key failing rejects the whole call; timing header `X-V4-Timing` present when `NODE_ENV !== "production"` and absent when it is (probe read model composing two seeded queries).
- **Green.** `lib/compose.js`.
- **Done when** a read model author cannot serialise sub-queries by accident: the only sanctioned way to fan out is through these two helpers, and `docs/testing.md` says so.
- **Built 2026-09-04** (`1a1de89` → `b40b6ea`): 39 tests; the conventions test now also fails on a bare `Promise.all(`/`allSettled(` under `readmodels/` or `commands/`. Tasks are thunks; `timings` ride non-enumerably on the result; a critical timeout → `UNAVAILABLE 503`, a critical throw → the original error. The production-silent header case is a unit test with a fake `res` (toggling `NODE_ENV` around a live request makes `logging()` write Logs docs and races teardown). Fix-up commit `ef933f9`: harness ids are resolved at runtime from `test/api_v4/harness/fixtures/identities.js` (`d1/d2/c1/c2/sa` by email) — never literal seeded ObjectIds.

#### Seed facts for v4 tests (found 2026-09-04)

- `yarn seed` mints fresh ObjectIds every run and `test:full` re-seeds: a literal seeded id in a test passes under `yarn test` and fails silently-shaped under the gate ("expected 16, got 0"). Resolve identities by email through `identities.js`.
- The seed relates **both dealers to both customers** (all four `dealer_custs` pairs) — there is no seeded unrelated pair; manufacture one with `insertMany` (skips the `pre("save")` counter hook) or use an id that exists nowhere.
- Orders: Dealer One 18, Dealer Two 16, Customer One 16, Customer Two 18; every `createdAt` is distinct, so tie-breaking must be exercised with manufactured rows.
- Multi-company users: `dealertwo@vsyst.in` (DView on Dealer One) and `customertwo@vsyst.in` (CView on Customer One) — the fixtures for anything `x-co-id`.
- `X-V4-Timing` is not in the CORS `exposedHeaders`, so a browser cannot read it; it is a dev-only affordance.

### F-API-6 — The v4 contract set ⚠️ approval (shared tooling touched)

- **Red.** `test/api_v4/contract/fixtures.test.js` with a single probe capture (`ping`) → green after `yarn fixtures:export:v4`, then a manual teeth check: change the envelope, watch it go red, revert, record.
- **Green.** `test/api_v4/temp/fixtures.captures.js` (`CAPTURES`, `REQUIRED_COLLECTIONS`), `export_fixtures.js` generalised to a `--set v4` argument writing `fixtures/api_v4/` + `fixtures.meta.json`, the compare/scrub logic extracted from the v3 detector into `test/helper/contract.js` so both detectors share it, `scripts/check_fixtures_fresh.js` iterating both sets, and — in the app repo, in F-APP-1 — `scripts/pull_fixtures.js` copying both sets (v4 files land as `v4_<name>.json` + `v4_fixtures.meta.json` beside the v3 ones, so no existing import moves).
- **Done when** `bash scripts/release_gate.sh` checks freshness of both sets.
- **Built 2026-09-04** (`6e89734` → `d5f0a78` → `43b7b07`): 22 tests (scrub 19, v4 detector 3). Shared scrub `test/helper/contract.js` (v3 volatile set + `generatedAt`), the v3 detector refactored onto it with byte-identical assertions; `export_fixtures.js --set v3|v4` (default v3), script `fixtures:export:v4`; `check_fixtures_fresh.js` iterates both sets — the v4 front-end meta is `dzzlo_oms_app/src/test/fixtures/generated/v4_fixtures.meta.json` (app only; dip-web has no v4 screens) and warn-and-skips until Phase 2 pulls it. `fixtures/api_v4/{ping,app_features,fixtures.meta}.json` committed (seed `v3_2026-09-03`). Teeth: an extra key on ping → detector red. Note: the meta `gitSha` is always one commit behind (fixtures are exported before they can be committed); the gate compares API vs front-end, not vs HEAD.

### F-API-7 — Docs, governance, CI ⚠️ approval (`AI.md`, versioning agent)

- `docs/testing.md`: a "v4" section (idiom, probe routes, the two rules above, fixture commands) and a v4 block in the flow map (harness rows only for now).
- `AI.md` Active Development Rule → "New contracts are written inside `api_v4/`. `api_v3/` changes only as test-first bugfix PRs. `api_v2/`, `api_v1/`, `models/`, `helpers/` unchanged." `.ai/agents/versioning-agent.md` gains the `/api/v4` row (Active — screen read models + commands). `docs/ARCHITECTURE.md`'s three stale statements are corrected while there.
- `.github/PULL_REQUEST_TEMPLATE.md`: one added line — "v4: one tenancy test per id the body accepts".
- CI: no change (`test:full` already runs everything).
- **Phase 1 done when:** `yarn test:full` green with the new harness/lib/contract suites; staging serves `GET /api/v4/ping` and `GET /api/v4/app/features` to a bearer; the release gate passes with two fixture sets; no v3 test changed; the PR body records every mutation smoke.
- **Built 2026-09-04** (`4409d4b`, `6e86c6d`): `docs/testing.md` §11 "API v4" + a v4-harness block in the §8 flow map; `AI.md` Active Development Rule → `api_v4/` (helpers may only gain additive, approved files — precedent `helpers/appFeatures.js` on the `dieselQtyLimit.js` pattern; note: `helpers/versionGate.js` exists only on the unmerged `feature/db-driven-version-gate` branch); versioning-agent map gains `/api/v4` and records the approved mount lines; `ARCHITECTURE.md` request flow, directory map and active-versions list corrected; PR template line added.

**Phase 1 closed on the API side 2026-09-04 — PR #39 → `slave`** (18 commits, 373 new tests, `test:full` 778 → 1151, release gate PASS with both sets, CI green per push). Left for the user: merge PR #39 and run the staging verification listed in its body (`GET /api/v4/ping`, `GET /api/v4/app/features`, the sadmin pair). Follow-ups found, not in scope: `AI.md` line 23 still shows a `202405_v2` test-path example (matches nothing); `AI.md` Commands block lacks `test:full` / `fixtures:export*`; `ARCHITECTURE.md` middleware-stack text is still v2-era; the versioning agent does not yet describe v4's `readmodels/ commands/ schemas/ lib/` layering (add once the first read model exists).

### F-API-8 — Screen toggles (D10) ⚠️ approval (two additive v3 sadmin routes)

Executes before F-API-7 so the docs step can describe it. Follows the DB-driven version gate on local branch `feature/db-driven-version-gate` line for line: config in a `counters` doc, an in-process 60-second cache with an invalidate hook, superadmin `GET/POST /sadmin/all/<name>`. If that branch is merged first, reuse its helper shape; if not, the toggle helper is written the same way so the two can share a base later.

- **Red.**
  - `test/api_v4/lib/appFeatures.test.js` (unit, over `helpers/appFeatures.js`): missing doc → `{}`; a doc `{ doc_name: "app_features", data: { screen_v2_dealer_orders: false } }` → that map; non-boolean values dropped; DB error → last cached value, else `{}`; cache honoured for 60 s and dropped by `invalidateAppFeaturesCache()`.
  - `test/api_v4/screens/app_features.test.js` (house idiom): `GET /api/v4/app/features` with a dealer bearer → `200 { success: true, data: { features: { … }, updatedAt } }`; customer bearer → `200`; no bearer → `401`; a superadmin bearer → `200` (the one v4 route every role may read); after `POST /sadmin/all/app_features { screen_v2_dealer_orders: false }` the next v4 read returns `false` (proves the invalidate hook); unknown or `$`-prefixed keys in the POST body → `400`.
  - `test/api_v3/collections/sadmin/app_features.test.js`: `GET/POST /sadmin/all/app_features` behave like the existing `diesel_limit` pair (same auth, same envelope) — pinned as current sadmin behaviour, not redesigned.
  - Capture `app_features` in `test/api_v4/temp/fixtures.captures.js` so the app's Tier 2 test reads the real shape.
- **Green.** `helpers/appFeatures.js` (`getAppFeatures`, `invalidateAppFeaturesCache`, `APP_FEATURES_DOC`), `api_v4/routes/app.js` + `controllers/app.js` (`authorize("dealer", "customer", "superadmin")`), `api_v3/controllers/sadmin/app_features.js` + the two router lines. Keys are validated against `^screen_v2_(dealer|customer)_[a-z0-9_]+$` (extend when a non-screen toggle is ever specified) so the doc cannot become a junk drawer.
- **Deliberately not:** per-company or per-role targeting (the read is behind the bearer, so it can be added later without a new mechanism); any toggle that is not a screen; touching `helpers/middlewares.js`.
- **Done when** the v4 read, the sadmin write and the invalidate path are green under `yarn test:full`, the fixture is exported, and staging answers `GET /api/v4/app/features` with `{ features: {} }` before any screen is registered.
- **Built 2026-09-04** (`b7e2686` → `d0b742e`): 44 tests (helper 16 · v4 read 15 · sadmin pair 22). Doc `{ doc_name: "app_features", data: { <key>: <bool> }, updated_at }` (`updated_at` top-level, off-schema, written with `strict:false`, read with `.lean()`); both verbs answer `{ features, updatedAt }`; POST is **merge** (`$set` per key, whole body validated first, 400 on an unknown key / non-boolean / empty body — a `$`-prefixed body degrades to empty via `sanitizeMongo`); switching a screen back on = POST the key `true`; absent = on; only well-formed booleans survive the read. Extra export `readAppFeatures` (uncached) so the admin page shows Mongo, not the minute-old cache. Smokes: drop the invalidate hook → 4 red; drop the regex → 6 red. Staging check is the user's step.

---

## Phase 2 — App foundations

Repo `dzzlo_oms_app`, branch `app_v4_foundations` — equals `slave` @ `a7c32d7` since Phase 0 (PR #48 merged there on 2026-09-03; the PR for this phase targets `slave`, not `main`). One PR for the phase. F-WEB-1 goes on a new `web_v4_foundations` from dip-web `slave_dev` (`23ac5b0`), PR → `slave_dev`.

### Target layout

```
src/utils/API/index.js         + export API_URL_V4 = `${API_URL}${API_VERSION_PATH_V4}`
src/store/apis/v4/
  base.js                      v4Url(path) → absolute URL · shared v4 tag names
  index.js                     injectEndpoints: v4_ping · v4_features (F-APP-4)
  __tests__/ping.msw.test.js · features.msw.test.js
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
src/navigation/screenRegistry.js · useScreenFlag.js   (toggle-driven cutover, F-APP-4)
src/screens/v2/<Role>/         empty until the first screen (Dealer/…, Customer/… — the role segment mirrors src/screens/{Role}/)
.env.development/.testing/.production/.ci/.example   + API_VERSION_PATH_V4=/api/v4   ⚠️ approval
```

### F-APP-1 — The v4 client ⚠️ approval (five env files)

- **Red.** `src/store/apis/v4/__tests__/ping.msw.test.js` on a fresh `makeStore()` with `server.listen({ onUnhandledRequest: "error" })`:
  - `api.endpoints.v4_ping.initiate()` hits **exactly** `<API_URL>/api/v4/ping` (absolute; not `${baseUrl}/ping`) with `authorization`, `x-co-id`, `x-api-key`, `meta`
  - 5xx retried twice, 4xx not (mirror `retry.msw.test.js`)
  - `data` is unwrapped from `{ success, data }`; a `403 { error_code }` reaches `errorRTK` with the code preserved (extend `preloadedState.test.js`)
- **Green.** The env var in all five files, `API_URL_V4`, `base.js`, `index.js`, `pull_fixtures.js` extended for the v4 set (see F-API-6). `fetchBaseQuery` leaves absolute URLs alone — the test proves it rather than assuming it.
- **Done when** the suite is green and a dev build against staging logs the ping response once at boot (visible only in the dev-only Demo/Redux screen — no production screen changes).
- **Committed 2026-09-04** (`32617385` red → `0565aa9f` green, on `app_v4_foundations`, unpushed at the session cut; the agent's report did not arrive — re-verify with `yarn test`). The dev-build ping log is deferred to F-APP-4's `__DEV__` effect.

### F-APP-2 — The Tier 3 harness

- **Red.** `src/test/__tests__/testUtils.test.js` renders a probe component (reads a selector, navigates, fires `v4_ping` through MSW) and asserts the text, the navigation call and that the request was seen.
- **Green.** `testUtils.js` wrapping `makeStore()` + `NavigationContainer` + `SafeAreaProvider` (with initial metrics) + `PaperProvider` + `BottomSheetModalProvider`; `withMsw(handlers)` lifecycle helper that hard-codes the unhandled-request guard; `msw/handlers/v4.js`; `"test:watch": "APP_ENV=testing jest --watch"` added to `package.json` (open item #5 in the app guide).
- **Done when** the probe test is green and `docs/testing.md` documents `renderScreen` as the only way to write a Tier 3 test.
- **Committed 2026-09-04** (`1f4af8b1` red → `da243353` green; same caveat as F-APP-1). The docs line lands in F-APP-6.

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
- **Built 2026-09-04** (`cc5413c7` red → `87bde4f9` green), **no restyle** (rejected, see log): `src/theme/{tokens,themes,adapters,provider}`, barrel `src/theme/index.js`; `src/components/v2/{AppText,Box,Screen}` on `StyleSheet`; `ThemeProvider` mounted around `PaperProvider` in `AppNavigatorContainer.js`, which now feeds Paper a **memoised** `toPaperTheme(theme)` (a fresh identity would re-render all 241 `useTheme` callers). Parity test deep-equals the legacy `Light`/`Dark`; typography = the 15 MD3 variants; spacing/radii reuse `src/constants/designTokens.js`; ESLint `no-restricted-syntax` override scoped to `src/screens/v2/**`, `src/components/v2/**`, `src/theme/**` (tokens and `__tests__` exempt), pinned by a test that runs ESLint programmatically. Brand tokens skipped (the PSOC svgs hold hundreds of illustration hexes, no clean list). Smokes: one palette value → 3 parity red; `allowFontScaling={false}` in AppText → 16 red. Device screenshot pair is the user's step.

### F-APP-4 — Screen registry and toggle-driven cutover (D10)

The toggles come from the house API (F-API-8), not Firebase Remote Config. The app fetches them once after login and again on every foreground; the navigator never waits for that fetch.

- **Red.**
  - `src/store/apis/v4/__tests__/features.msw.test.js` (Tier 2): `v4_features` hits `<API_URL>/api/v4/app/features` with the bearer headers, unwraps `data.features` from the pulled `v4_app_features.json` fixture, tag `Features`; a 5xx retries twice and then leaves the previous data in place (never replaces a good map with an error).
  - `src/navigation/__tests__/screenRegistry.test.js` (Tier 1): `resolveScreen("Dealer/Orders")` → the v1 component when nothing is registered; v2 when registered and `screen_v2_dealer_orders` is `true` **or absent** (default on); v1 when it is `false`; unknown route throws in `__DEV__`.
  - `src/navigation/__tests__/useScreenFlag.test.js`: returns `true` before any fetch has completed, `true` when the last fetch failed and nothing is cached, the cached value otherwise; re-fetch is triggered on `AppState` `active` and is de-duplicated within 60 s.
- **Green.** `screenRegistry.js` (`register(roleRoute, { v1, v2 })`, `resolveScreen(roleRoute, features)` — keys are `<Role>/<Route>` such as `Dealer/Customers`, because `Orders`/`Invoices`/`Payments` are route names in both role trees), `useScreenFlag.js` (a selector over the `v4_features` cache — no new slice, no new storage), one `useEffect` in `AppNavigatorContainer` that dispatches `v4_features.initiate()` after login and on foreground. Navigators are **not** rewritten now — a navigator file is switched to `resolveScreen` only for the route whose v2 screen is being shipped.
- **Deliberately not:** persisting the map across cold starts (default-on plus a fetch in the first seconds after login is enough for a kill-switch; revisit only if a real incident shows the gap); removing the dead `initRemoteConfig({})` call in `AppNavigatorContainer.js`, the `@react-native-firebase/remote-config` dependency and its `jest.setup.js` mock — that is a separate, gated deletion PR once D10 is live.
- **Done when** the registry has zero entries, the tests are green, a dev build logs the fetched map once after login, and the runbook line "flip `screen_v2_<role>_<slug>` off on the superadmin DB-Actions page, foreground the app, the v1 screen renders" is written in `docs/testing.md` and proven once against staging with a throwaway key.
- **Built 2026-09-04** (`6449a7cf` → `94d63ad6`): `v4_features` endpoint (tag `v4_features`, unwrap, previous data kept on a failed refetch), `src/store/apis/v4/selectors.js`, `src/navigation/screenRegistry.js` (`register`/`resolveScreen`/`toggleKeyFor`/`entries`/`reset`, ships empty, both v1 and v2 required, duplicate throws, unknown key throws in `__DEV__`), `src/navigation/useScreenFlag.js` (`useScreenFlag` default true; `useFeaturesRefresh` on token + `AppState` active, 60-s dedupe matching the server cache, one live RTKQ subscription so the entry is never evicted). `AppNavigatorContainer.js` calls `useFeaturesRefresh()` and, in `__DEV__` only, logs `[v4] ping …` after login and `[v4] features …` on change. Smokes: absent → off → 8 red; drop the dedupe → 3 red. The runbook line and the staging proof are F-APP-6 / the user's step.

### F-APP-5 — Strings and error-code mapping

- **Red.** `src/utils/__tests__/errorCodes.test.js`: every v4 `error_code` in the catalogue maps to user copy; unknown codes fall back to the existing `errorRTK` message; precedence with network errors unchanged.
- **Green.** `src/utils/errorCodes.js`; `errorRTK` consults it; the convention `src/screens/v2/<Role>/<Name>/strings.js` documented (the app has no i18n layer — one file per screen keeps copy testable and later translatable).
- **Built 2026-09-04** (`6d79149d` red → `71f44d04` green; the first agent stalled between the two, a second finished it): `messageForCode` covers the 8 catalogue codes + the 3 company-gate codes; a known `error_code` wins over `data.error` (the code is the contract, the wording may change); v3 bodies unchanged. Smoke: drop the branch → 13 red. `strings.js` convention lands in F-APP-6's docs.

### F-APP-6 — Docs

- `docs/testing.md`: Tier 3 section, v4 fixtures, `test:watch`; delete the stale "untracked files" caveat (open item #4 in the app guide). Vault: update `../tdd-testing-guide.md` §5 (Tier 3 no longer absent) and `../../oms_api/tdd-testing-guide.md` §1 (v4 contract set).
- `.github/PULL_REQUEST_TEMPLATE.md`: "Tier 3 decision tests written red-first" line.
- **Phase 2 done when:** `yarn test` green inside 2 minutes; `renderScreen` proven; parity screenshots attached; registry and toggle tests green; a dev build pings `/api/v4` on staging and logs the features map; F-WEB-1 merged; release gate PASS.
- **Built 2026-09-04** (`0b8b757a`): `docs/testing.md` 233 → 401 lines (Tier 3 = `renderScreen` only; two fixture sets; `test:watch`; the untracked-files caveat removed; new "v4 screens" section with the rollback runbook), PR-template line, `src/screens/v2/README.md`. Certification: `yarn test` 626 in 3.4 s; `yarn lint` adds no error (one pre-existing `exhaustive-deps` in `AppNavigatorContainer.js`); release gate **PASS** with all three fixture contracts fresh (v3 web + app, v4 app). Finding: app `AI.md` still says v3 primary / v1 legacy and has no `src/screens/v2/` — follow-up.

**Phase 2 closed on the build side 2026-09-04 — app PR #49 → `slave`** (11 commits, +289 tests, 337 → 626) ready for review, plus dip-web PR #27 → `slave_dev` (F-WEB-1). Left for the user: merge #39, #27, #49 (in that order — the app's v4 pull and the web toggle page assume the API set); the device checks in #49's body (`[v4] ping` / `[v4] features` in Metro after login against staging, light/dark parity screenshots, a throwaway toggle flipped on the superadmin page and seen on foreground). Next gate after that: the `01b` filter-sheet session (closes O‑2), then "start API for customers".

### F-APP-7 — Type scale and accessible layout ("accessibility for zoom", 2026-09-06, "start" given)

**Why.** The first iOS device run of screen 01 (2026-09-06, simulator at RN `fontScale` 2.143 = iOS "Accessibility Large", the step nearest 200 %) showed the text scaling exactly as tasks_04 demands — `AppText` never caps — while the boxes around it did not: filter chips at a fixed 28 pt clipped their labels, the money tiles at 32 pt clipped the amounts to a fragment, the header card's captions and values clipped, and in the credit sheet "Close" ran into the title, the panel numbers wrapped and the `available` figure fell off the card. Uncapped text inside fixed boxes is worse than capped text: it is the one setting the user chose, and it breaks the screen. Every v2 screen must be readable at the OS's accessibility sizes.

**The rule — text sets the box.** A container that holds text has no `height`. It has vertical padding and, at most, a `minHeight` derived from its type role's line height at the current scale. Widths that hold text flex or wrap. **Digits never wrap** (`numberOfLines={1}`, `flexShrink: 0`); when they no longer fit beside something, the pair stacks and the label yields (ellipsises), never the number. Things that hold no text keep their fixed size — glyphs, the 44 pt touch minimum, hairlines, bars, radii — and **spacing does not scale** (Apple's own guidance: bigger type, same rhythm).

**Mechanisms.**

1. `src/theme/scale.js` (pure): `ACCESSIBILITY_FONT_SCALE = 1.786`, `isAccessibilitySize(fontScale)`, `lineHeightAt(typography, role, fontScale)` = `ceil(lineHeight × fontScale)`, `boxHeight(typography, role, fontScale, padV)` = line height + 2·padV. At 1× these reproduce today's numbers exactly — chip `labelMedium`+6 → 28, tile `titleSmall`+6 → 32, status chip `labelSmall`+1 → 18, sheet header `titleMedium`+10 → 44, caption 16, balance line 24, tag line 12 — so the signed-off design is unchanged at the default size and only *grows* with the setting.
2. `useTypeScale()` (in `src/theme/provider/`): `{ fontScale, isAccessibilitySize, lineHeight(role), boxHeight(role, padV) }` from `useWindowDimensions().fontScale` and the theme's typography. Screens size text boxes through it and nothing else.
3. **The accessibility breakpoint.** `fontScale ≥ 1.786` is where iOS's accessibility categories begin (RN's iOS table: AX‑M 1.786, AX‑L 2.143, AX‑XL 2.643, AX‑XXL 3.143, AX‑XXXL 3.571; Android's 2.0 maximum lands above it too). At and above it, side-by-side **text pairs stack**: the row's two money tiles become two full-width tiles, the header card becomes three rows (caption left, value right — it is still the legend, by colour), the credit sheet's two panels become one column, `used / pool` and `available` take two lines, the balance band stacks its label over its value, and the sheet's Close slot is sized by its own text with the title allowed two lines. Below the breakpoint nothing moves; only the derived heights grow.
4. **Harness.** `renderScreen(ui, { fontScale })` and the same option on component renders. RN's Jest preset has always reported `fontScale: 2`, so every Tier 3 test has been running at 2× without saying so; the option makes the scale a stated input, and decision tests run at `1` and `2.143` (and the layout equation at `1, 1.353, 1.786, 2.143, 3.571`).
5. **Docs and contract.** `AI.md` non-negotiable ("text sets the box"), `docs/testing.md` "Type scale" subsection, the vault TDD guide. Not lint-able (a `height` literal is right on a glyph and wrong on a chip), so it is a test-list rule: every text container's decision test asserts `minHeight`/padding and the absence of `height`.
6. **A change of text size remounts the screen** (added 2026-09-07 from the device). React Native does send the dimensions event on a font-scale change (`RCTDeviceInfo.mm`, unconditionally) and `useWindowDimensions` subscribers re-render — but Fabric measures text when a shadow node is *created*, and a component that re-renders to the same element with the same props keeps its node and its old measurement: the glyphs draw at the new size inside the old box. On the simulator, going from 2.143× back to 1× left 47 pt chips and 55 pt tiles around 1× text; the one chip that was toggled (new props → new node) fixed itself, the others did not. So the `Screen` primitive keys the wrapper of its children on `fontScale`: a size change unmounts and remounts everything inside the screen — the fresh-mount layout that is verified at every size — while the screen component above it keeps its model, preferences and search text. Scroll position and an open sheet are lost, acceptably, on an event this rare.

**Known caps outside the app's hands.** react-native-paper's `Menu.Item` caps its title at 1.5× unless `titleMaxFontSizeMultiplier` is passed — pass it (uncapped) and derive the menu width. React Navigation's native header title (v1 chrome, "Customers" clipped at 2.143×) is outside v2 scope; noted for the header restyle.

**Work packages** (Fable plans, Opus builds at high effort; parallel where independent):

| WP | Scope | Depends on |
| -- | ----- | ---------- |
| A | Screen 01 list behaviour from the device run: return to top on a filter/sort/search change (decision 65); keyboard — taps go through, dismiss on drag / sheet open / navigation / chrome tap (decision 66) | — |
| B | This foundation: `scale.js`, `useTypeScale`, harness `fontScale`, `layout.js` as functions of `fontScale`, docs | — |
| C | Screen 01 chrome and row at every scale (decision 67): chips, search pill, header card, tiles, status chip, sort menu | B |
| D | Screen 01 credit sheet at every scale (decision 68) | B |

**Done when:** the suite is green at the default 2× and the new tests at 1 and 2.143; the simulator at Accessibility Large shows no clipped label, no wrapped digit and no collision on the Customers screen or its sheet; the screen at 1× is pixel-identical to the signed-off design; the rule is in `AI.md`.

**Built 2026-09-06/07 on app PR #51** (head `d77c2106`, 49 suites / 984 tests, CI green, not merged). B `3385ec2a`/`e3dc36fd` → `48c7aa00`/`8f541bf7`/`9287f4d1`: `src/theme/scale.js` (`ACCESSIBILITY_FONT_SCALE = 1.786`, `isAccessibilitySize`, `lineHeightAt`, `boxHeight`), `useTypeScale()`, the harness options, `layout.js` helpers by scale, the rule in `AI.md` and `docs/testing.md`. D `a4d74380` → `011be469` and D2 `d221beb0` → `8648dbd2` (sheet). C `38dbe59f` → `3b6f81d2` and C3 `f07e3074` → `312996ef` (chrome + row). Three amendments the device forced on the plan above: (1) the row's two money tiles and the header card stack by **width, not by the breakpoint** — on a 390 pt phone the row is full at 1× (`32 + 66 + 12 + 132 + 8 + 140 = 390`), so `tilesStack(fontScale, windowWidth)` in `layout.js` decides for both (390 stacks from 1.118×, 430 from AX‑M, RN's 750 pt Jest window never), and the harness gained `withWindow({ fontScale, width }, fn)` / `renderScreen(ui, { fontScale, width })` because the preset width can never trip it; (2) the sheet's `used / pool` + `available` line and the balance band **wrap by content** (`flexWrap` + `marginLeft: 'auto'`) — they overflowed from 1.118×, long before the breakpoint; (3) the ring leaves the sheet's identity row above the breakpoint. The breakpoint itself still governs the sheet's panels (one column) and the ring. Paper's `Menu.Item` needed `titleMaxFontSizeMultiplier={0}` to follow the OS. Two cautions for the next screen: a declared `lineHeight` is multiplied natively — derive **container** boxes only, never pass a scaled line height into a text style; and verify text sizes on a **fresh mount** — a live size change can leave stale text boxes until the screen re-renders. Verified on the simulator: the sheet at 1 / 1.353 / 2.143, the chrome at 1 / 1.353 / 2.143 on fresh mounts, the list at the top after every replaced page, one tap with the keyboard up. Mechanism 6 (C4 `e171d278` → `1bf9dce6` → `46cb83d2`, merged `dcee66ec`, 986 tests): a live change 1× → 2.143× → 1× with no reload now re-lays out the screen both ways.

### F-APP-8 — Bottom inset ownership (DEFERRED by the user, 2026-09-06: "we will tackle inset.bottom in future. not now")

`AppNavigatorContainer.js` pads the whole role navigator by `insets.bottom` (all four insets, in fact). Both bottom-tab navigators rely on it explicitly (`safeAreaInsets={{ bottom: 0 }}` in `Dealer/TrnTab.js:375` and `Customer/TrnTab.js:346`), and a v1 survey found the clearance is the only one most screens have: `bottom: 0` in 20 files, `justifyContent: 'flex-end'` in 31, `KeyboardAvoidingView` in 7, in-tree `Snackbar` 2, `FAB` 2, and 96 list screens whose last row would sit under the home indicator — on Android 15+ under the navigation bar itself, since `targetSdkVersion 36` enforces edge-to-edge whatever `edgeToEdgeEnabled` says. Bottom sheets and Paper portals live outside the padded view and are unaffected. Consequence for v2 today: the Customers list pads `insets.bottom + spacing.md` on top of the root's inset (a double inset) and its surface cannot pass under the indicator; the runbook line is amended to say so. When this is picked up: move the inset into the v1 navigators' `contentStyle`, drop the two tab-bar overrides, give the drawer content its own inset, and let v2 routes own it through `Screen edges` — test-first, one PR, ideally before the second v2 screen ships.

### F-APP-9 — Orientation and large screens (2026-09-07, "plan them and add them")

> **See also [[04-orientation-decisions]]** — the 2026-09-10 questions answered with the measurements: why the v1 portrait pin cannot simply be removed (133 module-scope `Dimensions.get` files, 518 consumption sites, no test that would notice), why screens get one general width-class design rather than a per-orientation redesign, and where a two-pane list/filter layout would sit.

**Facts.** Both platforms are portrait-locked today — iOS `UISupportedInterfaceOrientations` lists Portrait only (while `TARGETED_DEVICE_FAMILY = 1,2` already ships to iPad), Android `screenOrientation="portrait"` — and no screen in the app reads its orientation. The Customers v2 screen already lays out from `useWindowDimensions()` (F-APP-7: `tilesStack(fontScale, width)`, `sortMenuWidth`), so it is width-aware but has never been shown a width above 430.

**Decisions.**
1. **Per-screen orientation through what the app already has — no new package.** `@react-navigation/native-stack` (7.14) exposes a per-screen `orientation` option (`'all' | 'portrait' | …`), implemented natively by `react-native-screens` (4.24); both are dependencies today. The native config lists every orientation so that screens may choose (iOS `UISupportedInterfaceOrientations` Portrait + both landscapes, all four under `~ipad`; Android `screenOrientation` removed / `unspecified`, `resizeableActivity="true"` for foldables and multi-window; the existing `configChanges` keeps the activity alive across rotation and fold, so React Native re-emits dimensions and v2 screens re-lay out without a remount). Every v1 stack's `sharedScreenOptions` sets `orientation: 'portrait'` — **v1 is unchanged** — and a v2 screen sets `orientation: 'all'` through the registry's route options, so the cutover flag flips orientation along with the screen. (Superseded the same day: the first draft unlocked app-wide and let v1 rotate; the user asked whether a package would help, and the answer was that the right one was already installed. `react-native-orientation-locker` would duplicate it; `react-native-device-info`'s `isTablet()` is the wrong rule — width classes cover a rotated phone and a Fold alike.)
2. **Window classes, not device names.** `useWindowClass()` in `src/theme/provider/`: `{ width, height, isLandscape, sizeClass, compactHeight }` with Material's window size classes on WIDTH — `compact` < 600, `medium` 600–839, `expanded` ≥ 840 (dp/pt) — and `compactHeight` = height < 500 (a phone on its side). Tokens in `src/theme/layout.js`: `BREAKPOINTS`, `READABLE_WIDTH = 640`, `COMPACT_HEIGHT = 500`. A large phone in landscape (844 × 390) is **`expanded` + `compactHeight`** by the numbers (the builder corrected the plan's "medium": 844 is past 840, and what makes it a phone is its height — the written-down reason height is a separate signal, not a third width class); an iPhone SE on its side (667 × 375) is `medium` + `compactHeight`; an unfolded Fold (~673 wide) is `medium`; iPad and a landscape tablet are `expanded`. Built as O1 (`ac20f33b`/`85cc692b` → `a7ecb372` → `2bbbc876`; 986 → 1103 tests): `screenOptionsFor(roleRoute, features)` in the registry gives a v2 screen `{ orientation: 'all' }` and a rolled-back one `{ orientation: 'portrait' }`; all eight native stacks carry `orientation: 'portrait'`, pinned by a file-reading test (importing the navigators drags `react-native-webview`'s TurboModule into Jest). `UIRequiresFullScreen` stays `true` — iPad Split View is a separate decision.
3. **Wide screens are contained, not stretched.** A `Container` primitive (`src/components/v2/Container.js`) centres its children at `maxWidth: READABLE_WIDTH` from `medium` up and is `width: 100%` in `compact`. A list row designed for 390 pt is not improved by 1024 pt of width; it is improved by a readable column and quiet margins. Two-pane layouts (list + detail) are a later, per-screen design decision, not a foundation.
4. **Height is a dimension too.** In `compactHeight` a screen's chrome yields rows: for Customers the chips row and the header card share one line from `medium` up (chips left, card right), which is also the natural use of a tablet's width.
5. **Sheets are contained the same way.** A bottom sheet on a wide window is centred at `READABLE_WIDTH` (gorhom `style` margins from the window width), never edge to edge.
6. **Tests state the window.** The harness's `withWindow({ fontScale, width, height })` / `renderScreen(ui, { …, height })` gains `height`; decision tests run at 390 × 844, 844 × 390 and 1024 × 768. Two config pins read `Info.plist` and `AndroidManifest.xml` in Jest so a rollback of the unlock fails a test.
7. Layout comes from `useWindowDimensions()` at render — never `Dimensions.get` at module level, never a portrait assumption; `AI.md` says so.

**Work packages:** O1 foundation (native unlock + pins, `useWindowClass`, tokens, `Container`, harness `height`, docs) → O2 Customers (Container around the body, chips + card sharing a row from `medium`, the sheet contained; spec decision 70). Device check: iPhone rotated (844 × 390), iPad Pro 11 simulator (expanded).

### F-APP-10 — Language: English and Hindi (2026-09-07)

**Facts.** The app has no i18n — no library, no Hindi glyph anywhere in `src`, no language setting; the Settings screen offers only the theme, which is a server-side user field. The v2 screens keep every user-facing string in a per-screen `strings.js` (F-APP-5), which is the right shape for a second language.

**Decisions.**
1. **Language is a device setting, like text size.** Default `SYSTEM`: the app follows the OS locale (`hi*` → Hindi, anything else → English), read from React Native itself — iOS `SettingsManager` (`AppleLocale` / `AppleLanguages`), Android `I18nManager.localeIdentifier` — no dependency. An in-app override (`SYSTEM` / `ENGLISH` / `हिन्दी`) lives in the Settings screen beside the theme and is persisted **locally** in AsyncStorage (`@dzzlo/language`): it must apply before login and offline, which a server field cannot. Both platforms register the two locales (`CFBundleLocalizations`, `locales_config.xml` + `android:localeConfig`) so the OS's per-app language switch works and `SYSTEM` follows it.
2. **One provider, one hook.** `LanguageProvider` (in `src/i18n/`, mounted with the theme) exposes `{ language: 'en' | 'hi', setting, setSetting }`; `useStrings({ en, hi })` returns the active table with a **deep fallback to English** for any key Hindi lacks — a missing translation shows English, never `undefined`. A screen's `strings.js` stays the English table (tests keep importing it); Hindi sits beside it in `strings.hi.js` with the same shape.
3. **Hindi copy is written with the English, by the same hand, never "later".** Numerals stay Latin and money keeps the Indian grouping (`₹ 1,05,769.39`); business abbreviations (`CR` `DR` `OTP`) stay as they are; sort labels are looked up by key at render, never carried as frozen `label`s.
4. **Devanagari needs a taller line.** The type roles' `lineHeight` (≈ 1.33 × size) clips Devanagari's matras. `scale.js` gains `scriptLineHeightFactor(language)` — 1 for `en`, **1.2 for `hi`** (to be verified on the device and tuned once) — applied in `AppText` to the role's `lineHeight` and in `useTypeScale`'s `lineHeight`/`boxHeight`, so text and box agree in both languages. `Screen` keys its children on `${fontScale}:${language}` — a language change remounts exactly as a size change does (mechanism 6).
5. **No literal copy in v2.** An ESLint `no-restricted-syntax` selector bans JSX text with two or more letters under `src/screens/v2/**` and `src/components/v2/**`; punctuation and numerals pass.
6. **Tests state the language.** `renderScreen(ui, { language: 'hi' })` / `withLanguage('hi', fn)`; a screen's decision tests run the copy-bearing cases in both languages; the fallback is pinned (a key present in `en` and absent in `hi` renders English).
7. **Library or house (asked 2026-09-07).** House hook now. What `i18next` + `react-i18next` (pure JS, no native risk) would add is interpolation, ICU plurals, translator-facing JSON resources and missing-key tooling — none of which the first screens need (a 20-line `format()` covers parameters, Hindi plurals are one/other, money formatting is fixed by decision, Hermes ships `Intl`). `react-native-localize` is needed only for currency/timezone/RTL data, not for the locale. **Trigger to adopt i18next:** the first screen whose copy needs plurals or interpolation beyond `format()`, or the first translator who is not a developer. The per-screen `{ en, hi }` tables port 1:1 to i18next namespaces, so starting house wastes nothing.

**Work packages:** L1 foundation (`src/i18n/`, provider + hook + device locale + persistence, Settings row, `scale.js` factor + `AppText` + `useTypeScale` + `Screen` key, lint guard, harness `language`, native locale registration, docs) → L2 Customers (`strings.hi.js` for every string including the credit sheet, the reset Alert and the sort labels; the header title through `setOptions`; spec decision 69). Device check: Hindi at 1× and 2.143×, matras intact, no clipped line.

**Built 2026-09-07 on app PR #51.** L1 `4ca16d02` → `90e376cf` → `c1f2b7cd` (merged after O1; +104 tests): `src/i18n` (`LANGUAGES`, `resolveLanguage`, `getDeviceLocale` from RN core, `LanguageProvider initialSetting`, `useLanguage`, `useStrings` with deep fallback — the builder's own test caught its first merge returning English for every leaf), `SCRIPT_LINE_HEIGHT { en: 1, hi: 1.2 }` through `AppText` and `useTypeScale`, `Screen` keyed on `fs:${fontScale}:${language}`, the Settings row (`language-<VALUE>` testIDs), the JSX-literal copy guard (nothing in v2 tripped it), `withLanguage('hi', fn)` / `renderScreen(ui, { language })` (forces the DEVICE LOCALE so the SYSTEM resolution is what runs), `CFBundleLocalizations` + `locales_config.xml`. L2 `723a3e18` → `af56f8eb` (merged `41cddd7c`, 64 suites / 1241 tests): `strings.hi.js` key for key with a completeness test, every component on `useStrings(table)`, sort labels / captions / tags by key, the reset Alert in Hindi; builder-written extras for review — `empty.noMatch` कुछ नहीं मिला, `credit.ring.unlimited` क्रेडिट सीमा नहीं, `credit.ring.used` "क्रेडिट ${pct} उपयोग", and the retired filter-sheet keys. **Device 2026-09-07:** Settings → हिन्दी switches the screen without a restart; chips, sort chip, captions, the six menu labels and the whole credit sheet in Hindi with matras intact at 1× and 2.143× (chips 32 pt, as the factor says); money and `CR · DR · OTP` unchanged. One gap found and fixed the same day: the route supplies `headerTitle` as a string, which React Navigation prefers over `title`, so the header stayed "Customers" until the screen also sets `headerTitle: s.title` (the test that pinned `title` alone had lied by omission). Out of scope, recorded: the screen's error text comes from the store's `errorRTK` mapper and cannot be translated from a screen; the sort button's `accessibilityLabel` is the raw key (`createdAt`) — a v2 bug for the next pass; `helpers/Filters/customers.js` imports strings from a screen folder.

**Amendment 2026-09-08 — Android 15+ lays Hindi text out wider than React Native measures it (mechanism 7).** On the Pixel 10 Pro Fold emulator (Android 17; the app targets SDK 36) the excluded filter chip rendered "बिना" and hid "लेन-देन" at 390 dpi while rendering whole at 320 dpi; on iOS every size was fine. Cause, read out of `ReactAndroid/.../TextLayoutManager.kt` and Android 15's TextView change: React Native sizes a text from the font's ADVANCE widths (`Layout.getDesiredWidth`), but since Android 15 a TextView in an app targeting SDK 35+ breaks lines by glyph BOUNDS (`useBoundsForWidth`), and Devanagari clusters carry ink past their advances — so the last cluster wraps onto a second line the one-line frame never shows. Not a clip at the right edge, and not a bigger Hindi font: the tail is on an invisible line, and whether it fits is density rounding, which is the "some devices" the user saw. **Tried and rejected:** RN 0.84's feature flag `fixTextClippingAndroid15useBoundsForWidth` (via `dangerouslyForceOverride` after `loadReactNative`, delegating to RN's stable overrides — a plain `override` crashes at launch either before `loadReactNative` (SoLoader not initialised) or after it (RN's loader already overrode once)). It measures by bounds but derives the width from `getLineRight − getLineLeft` of an already-wrapped layout, so at every non-integer px/dp scale (390 and 420 dpi wrapped; 320 and 480 were clean) the excluded chip and the sort chip became two-line chips. **Landed instead:** the app theme routes `android:textViewStyle` to a style with `android:useBoundsForWidth=false` (`tools:targetApi="35"`, one definition), so every RN Text on Android 15+ lays out from advances exactly as React Native measures — the Android 14 behaviour, which never wrapped or hid a tail; the overhang draws a pixel or two past the frame, as on iOS. `MainApplication.kt` stays the plain 0.84 template. Pinned by `src/i18n/__tests__/androidText.config.test.js` (theme routing, the attribute, the parent style, the manifest, and that the Kotlin carries no feature flag). Rejected: end padding or a trailing space on Hindi text — padding cannot stop a wrap that happens inside the measurement itself. **Open, platform-level:** Android's Bold Text accessibility setting (`fontWeightAdjustment`) — React Native's Android measurement has no handling of it at all, so the platform draws heavier text than was measured and tails clip on EVERY screen, v1 included ("Process" for Process Order, "Und" for Undo on the Orders screen); no config switch exists; it needs an RN-level change (measure with the configuration's weight adjustment) or an upstream fix.

### F-WEB-1 — Toggle control on the superadmin DB-Actions page (repo `dip-web`, own PR)

The only dip-web work in this project. Runs in parallel with Phase 2 once F-API-8 is on staging; must be merged before the first screen ships (Step 5 of the playbook flips a toggle on staging).

- **Red.** RTL + MSW per the web TDD guide: `src/pages/superadmin/db/ImpActions.test.js` (or a sibling `AppFeatures.test.js` if the page is split) renders the toggle list from a mocked `GET /sadmin/all/app_features`, shows every `screen_v2_*` key with its current value, and a switch change issues `POST /sadmin/all/app_features` with the full map; a failed POST keeps the previous state and shows the existing error toast; a superadmin-only render (the page is already behind the superadmin route guard — pin, do not add).
- **Green.** Two endpoints in `store/apis/sadmin/imp_actions.js` beside the `diesel_limit` pair; the list on `pages/superadmin/db/ImpActions.js` (or the version-gate card if that branch lands first — same page). Keys are read from the API, never hard-coded in the web, so a new screen needs no web change: registering a screen's key happens in the app PR, the superadmin sees it as soon as the API doc contains it, and the app's default-on covers the window in between.
- **Done when** the web suite is green, the page flips a throwaway key on staging, and `GET /api/v4/app/features` reflects it within 60 s.
- **Built 2026-09-04** — dip-web **PR #27** `web_v4_foundations` → `slave_dev` (`3b14992` red → `a80e467` green), CI green, **not merged** (user rule). 8 tests in `src/pages/superadmin/db/AppFeatures.test.js` (suite 7 files / 54 tests / 1.3 s). Own component `AppFeatures.js` mounted as a section of `ImpActions.js`; endpoints `fetch_app_features` / `update_app_features` (tag `app_features`). Two deliberate departures from the text above: a flip POSTs **only the changed key** (the API merges; posting the full map would overwrite a concurrent edit), and an **"Add toggle" row** exists so a key that has never been written can be switched off — without it the kill switch could not reach a brand-new screen. No optimistic update: the list re-renders from the invalidated query, so a refused write needs no rollback. Smokes: neuter the key regex → 1 red; drop `invalidatesTags` → 2 red. Finding: the superadmin route table in `src/App.js` is gated by a plain `role === "superadmin"` branch with no per-route wrapper and **no test over that branch** — flagged, out of scope. Staging flip + the 60-s check remain the user's step.

---

## Foundations decision log

| Date       | Item                                   | Decision                                                                                                                                 |
| ---------- | -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-09-03 | Layouts above                          | drafted; "start phase 1" given 2026-09-04 (built, PR #39); "start phase 2" given 2026-09-04                                              |
| 2026-09-04 | restyle re-validation (F-APP-3 step 0) | **No restyle.** `@shopify/restyle` latest is 2.4.5, published 2025-03-19 (17+ months without a release as of 2026-09); peer deps are wildcards (`react: *`, `react-native: *`), so RN 0.84 / React 19 support is unverified upstream. Under the house rule (no new dependency unless it buys runtime efficiency) the fallback applies: plain token objects + Paper MD3 theme + `AppText`/`Box`/`Screen` on `StyleSheet`, same API surface for screens |
| 2026-09-03 | D7 validation library                  | **decided by user:** house validator (`lib/validate.js` schema DSL), no third-party library → F-API-2; the zod approval row is withdrawn |
| 2026-09-03 | D10 kill-switch                        | **decided by user:** house screen toggles from the superadmin website, no Firebase Remote Config → F-API-8, F-APP-4, F-WEB-1             |
| 2026-09-07 | F-APP-9 / F-APP-10                     | **decided by user ("two more accessibility for v2 screens … orientation … and language"):** orientation unlock is app-wide (v1 rotates during the cutover; per-screen locking would need a native module), wide windows are contained at 640 pt, window classes by width; language is a device setting (SYSTEM / EN / HI, local, follows the OS locale), Hindi copy ships with the English, Devanagari gets a taller line, no literal copy in v2 |
| 2026-09-06 | F-APP-7 type scale                     | **decided by user ("we need accessibility for zoom"):** text sets the box — no fixed heights on text containers, heights derived from the type role's line height × `fontScale`, digits never wrap, pairs stack at `fontScale ≥ 1.786`; spacing does not scale; harness takes `fontScale`. Triggered by the 2026-09-06 iOS device run of screen 01 |
