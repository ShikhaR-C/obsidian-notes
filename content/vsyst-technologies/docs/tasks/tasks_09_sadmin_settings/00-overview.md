# Superadmin-Controlled App Settings — Server-Driven Config for `dzzlo_oms_app`

**Status:** 🟡 **2026-10-01:** not built on master in this plan's shape — the floor is still the hardcoded `1.68` (`helpers/middlewares.js:123`); the D10 house toggles cover screen v1/v2 switches only; the DB-driven gate sits on unmerged, conflicting PRs (API #34, app #47); Phase 4's Firebase clean-up is done (tasks_17). — _was:_ Spec'd (2026-06-15). Not yet implemented.
**Owner:** TBD
**Created:** 2026-06-15
**Base branch:** ❌ **2026-10-01:** obsolete — the diesel limit reached the mainline through PR #33 (`3c011df`, 2026-06-12) and master is now 1.5.5 (`6d41ce5`); branch from `master`. — _was:_ **`v1.5.4` after merging `slave` into it — merge is a precondition (see §0).** `v1.5.4` is the active mainline (27 commits since the `1.5.3` merge-base: AdvDep voucher ledger, `max_cr_lmt` redesign, veh_trns pagination, reports IST, …). `slave` carries only 4 commits — the `diesel_limit`/qty-cap config (the proven precedent this plan generalizes) + a `so-products` hotfix — that have **not** landed on mainline. Do **not** branch from `slave` (it lacks all the v1.5.4 mainline work); merge `slave`'s 4 commits into `v1.5.4`, then build this plan on the merged tree.
**Scope:** Add a single superadmin-controlled settings surface in `dzzlo_oms_api` (v3) — written from the `dip-web` superadmin, read by `dzzlo_oms_app` — so that operational knobs currently **hardcoded in the app** or **hardcoded in the API** can be changed without an app release. First and highest-value consumer: the **app version floor / force-update / maintenance** lever (today a hardcoded constant). Legacy API v1/v2 are intentionally untouched.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). 🟡 Of the five phases, Phase 0 is moot (✅ — the diesel limit is on master), Phases 1–3 are ⬜ on master and Phase 4 is 🟡 (its Firebase clean-up was done by tasks_17; the dip-web form was not assessed); the settings catalogue is 10 ⬜ + 1 🟡. The D10 house toggles do not supersede the settings store — the API keeps only `screen_v2_<role>_<slug>` booleans, leaves non-screen toggles out on purpose (`helpers/appFeatures.js:31-38`) and serves them only to a bearer — so the operational knobs, the version floor and maintenance still need Phases 1–3 or PR #34's shape (`T09-N1`, `X-APP-5`). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item | Status | What exists now (evidence) | What is left / next step |
| --- | --- | --- | --- |
| Phase 0 — merge `slave` into `v1.5.4` (§5b) | ✅ | moot: the diesel limit reached the mainline via PR #33 (`3c011df`, 2026-06-12) — `helpers/dieselQtyLimit.js`, routes `api_v3/routes/sadmin/index.js:63-64`, enforced at `api_v3/services/order_msts.js:841,978,1023` and `so_msts.js:33,254`, test `test/api_v3/collections/so_msts/dieselQtyLimit.test.js` | none — branch from `master` (1.5.5) |
| Phase 1 — settings store | ⬜ | no `app_settings` doc, `settingsCache` or settings routes (git grep: 0); the cached-`counters` reader exists twice already — `helpers/appFeatures.js:40-106` (D10) and PR #34's `helpers/versionGate.js` (unmerged) | decide the shape (`T09-N1`); superadmin endpoints require a superadmin bearer (see `X-SEC-2` in tasks_01) |
| Phase 2 — version gate + maintenance | ⬜ | master: `Number(1.68)`, the test-build exemption and two literal messages (`helpers/middlewares.js:112-141`, mounted `dzzlo_oms.js:75`), pinned by `test/api_v3/features/version_gate/index.test.js`; an alternative on PR #34 (OPEN, CONFLICTING) | `X-APP-5`, `T09-N4` |
| Phase 3 — app consumption | ⬜ | `meta` header on every request (`src/store/apis/createApi.js:10-20,45`); hard update = store button on the 403 text (`src/components/Error/index.js:68`); screen flags `src/navigation/useScreenFlag.js:40-104` (token + foreground, 60 s dedupe, absent = ON); the §4 constants still hardcoded; soft banner only on PR #47 | build on the D10 client pattern — `X-APP-5`, `T09-N2` |
| Phase 4 — dip-web form, tests, rollout | 🟡 | ✅ Remote Config removed by tasks_17 (`ad40ed71`; `package.json:35-38`); ⬜ settings tests; the dip-web form was not assessed | tests with Phases 1–3 |
| Settings catalogue (§4, 11 keys) | 🟡 | `feature_flags` 🟡 (D10 covers screen v1/v2 switches only); the other 10 keys ⬜ — per row in §4 | `T09-N1` |
| Open PRs — API #34, app #47 | ⬜ | both OPEN and `CONFLICTING` (`gh pr view`, 2026-10-01), untouched since 2026-06-29 | rebase or re-cut — `X-APP-5` |

---

## 1. The problem

**Status (2026-10-01):** ⬜ still true — the floor is hardcoded (`helpers/middlewares.js:123`), and so are the app constants (§4 column); the `counters` pattern now holds five docs (`states`, `units`, `hsns`, `diesel_limit`, `app_features`) and `diesel_limit` is on master.

There is **no general config layer** today. Three independent facts make this expensive:

1. **The version floor is a hardcoded constant.** `dzzlo_oms_api/helpers/middlewares.js:123` sets `allowedVersion = Number(1.68)` with a `"1.510"` test bypass, applied globally at `dzzlo_oms.js:75`. Raising the floor, changing the "update from store" copy, or posting a maintenance banner **requires an API redeploy**. Combined with [[app-ota-and-version-gating]] (no CodePush → a store update is the only client fix), this middleware is effectively the **only release-free lever over fielded apps** — and it isn't configurable.

2. **The app is full of hardcoded operational constants** with no way to tune them remotely: `PAGE_SIZE = 15` (`src/screens/Common/Vehicles/index.js`, `src/screens/Customer/Vehicles/index.js`, daily report), `timeout = 10000` / `maxRetries = 2` / `keepUnusedDataFor = 300` (`src/store/apis/createApi.js`), `DEFAULT_MAX_CACHED_ITEMS = 500` (`src/store/apis/paginationHelpers.js`, the low-RAM Android guard — see [[flashlist-v2-mvcp-default-on]]). Tuning any of these for low-end Android needs a store release.

3. **The pattern is already proven on `slave` for one knob — `diesel_limit`.** On `slave`, `api_v3/controllers/sadmin/diesel_limit.js` + `helpers/dieselQtyLimit.js` store config in the `counters` collection (`{ doc_name: "diesel_limit", data: { value, error_message } }`), expose `GET|POST /api/v3/sadmin/all/diesel_limit` (superadmin), are written from the dip-web DB-Actions page (`src/store/apis/sadmin/imp_actions.js:109-126`, `src/pages/superadmin/db/ImpActions.js`), and are **enforced server-side** in `api_v3/services/order_msts.js` (3 call sites) and `so_msts.js` (2 call sites), with tests in `test/api_v3/collections/so_msts/dieselQtyLimit.test.js`. **This is the template to generalize.** What's missing is an **app-readable** config doc (everything below) — `diesel_limit` is server-enforced only, the app never reads it. ~~(Note: on the checked-out `v1.5.4` branch the diesel backend is absent and the dip-web stub looks orphaned — that's a branch artifact; build on `slave`.)~~ _2026-10-01: the diesel backend is on master since PR #33 (`3c011df`)._ ~~Firebase Remote Config is separately wired (`src/utils/firebase.js` `initRemoteConfig`/`getRemoteValue`, called at `src/navigation/AppNavigatorContainer.js:66`) but **no key is ever read** — do not adopt it as a second source.~~ _2026-10-01: Remote Config was removed from the app on 2026-09-27 (tasks_17, `ad40ed71`)._

## 2. The approach (one source of truth)

**Status (2026-10-01):** ⬜ not built. A second, narrower source now exists — the D10 screen toggles (`helpers/appFeatures.js`, `GET /api/v4/app/features`, `GET/POST /api/v3/sadmin/all/app_features`) — so "one source of truth" now means deciding how the two relate (`T09-N1`).

Build **one** settings store in `dzzlo_oms_api`, owned by the existing dip-web superadmin, with two access tiers:

| Endpoint | Auth | Purpose | Cache |
| --- | --- | --- | --- |
| `PUT /api/v3/sadmin/settings` | superadmin (existing `/sadmin` guard) | write any setting | bust on write |
| `GET /api/v3/settings` | any authenticated user (NOT under `/sadmin`) | app reads config | `refDataCache` |

> **Do NOT add Firebase Remote Config as a second config system.** One authenticated source of truth (our own DB, already reachable via the `meta`-header'd client) is simpler to reason about and keeps app + dip-web + middleware agreeing. The unused `firebase.js` remote-config helpers can be left dormant or deleted in Phase 4.

**Storage — reuse the `counters` collection (decision 1).** `units`, `hsncodes` (`api_v3/controllers/sadmin/units_hsns.js`) and `diesel_limit` (slave's `helpers/dieselQtyLimit.js`) already live as `counters` docs keyed by `doc_name` with a free-form `data` subdocument. Add **one** doc `{ doc_name: "app_settings", data: { ...settings } }` for the app-read config. No new model, no migration, identical to the proven `diesel_limit` precedent. (Alternative: a dedicated `settings` model — cleaner typing, more infra. Not chosen; see §6.)

**Client contract — server-driven with client fallback (decision 2).** Every consumed setting keeps its current hardcoded value as the **fallback** (`settings.page_size ?? 15`). The app must work fully if `GET /settings` fails or returns partial data — config is an *override*, never a *dependency*. This keeps the app offline-first and makes rollout risk-free.

## 3. Confirmed decisions

**Status (2026-10-01):** correction — decision 3 relies on a superadmin guard: superadmin endpoints require a superadmin bearer (see `X-SEC-2` in tasks_01); decision 6's "on `slave`" is now "on master" (PR #33).

1. **Storage = `counters` doc `app_settings`** (reuse the proven `diesel_limit`/`units` pattern; no new model/migration).
2. **Every setting has a client-side fallback.** Server config overrides; never blocks. App is fully functional with `GET /settings` unreachable.
3. **Read endpoint is NOT superadmin-gated.** `GET /api/v3/settings` must be reachable by every authenticated dealer/customer app. Only the **write** (`PUT /sadmin/settings`) sits behind the superadmin guard. (The orphaned diesel stub put *read* under `/sadmin` — that would have been unreadable by the app; do not copy it.)
4. **Version floor migrates from constant → setting, but keeps the constant as a hard floor.** `min_app_version` is read from settings; if settings are unreachable the middleware falls back to the compiled-in `1.68`. A superadmin can only **raise** the floor above the compiled default, never silently drop below it (guards against a bad write locking nobody out / letting everybody in). See Phase 2.
5. **Do NOT touch API v1/v2.** v1 is already disabled (`dzzlo_oms.js:107` commented). Version middleware is global, so the floor still applies to v2 traffic — fine. New settings endpoints are v3-only.
6. **Leave `diesel_limit` as-is; do NOT migrate it.** It already works on `slave` (own `counters` doc, own `/sadmin/all/diesel_limit` route, server-enforced in `order_msts`/`so_msts`, tested). It's server-enforced only — the app never reads it — so there's no benefit to folding it into `app_settings`, and doing so would churn working, tested code. The new `app_settings` doc is **additive**, for the app-read keys in §4. New future knobs go into `app_settings`; the established `diesel_limit` doc stays its own thing. (Both follow the identical `counters` pattern — consistency without a risky migration.)

## 4. Settings catalogue (initial keys)

**Status (2026-10-01):** 🟡 1 of 11 keys partly covered (`feature_flags`, screen switches only, via D10); 10 ⬜ — per row below.

`data` shape on the `app_settings` doc. All optional; absent key → app/middleware fallback.

| Key | Type | Consumer | Fallback | Phase | 2026-10-01 |
| --- | --- | --- | --- | --- | --- |
| `min_app_version` | number | version middleware | `1.68` (compiled) | 2 | ⬜ still `Number(1.68)` (`helpers/middlewares.js:123`); PR #34 reads `version_gate.minVersion` |
| `update_msg_ios` | string | version middleware | existing literal | 2 | ⬜ literal (`helpers/middlewares.js:121-132`) |
| `update_msg_android` | string | version middleware | existing literal | 2 | ⬜ literal (`helpers/middlewares.js:121-137`) |
| `maintenance_mode` | bool | app launch + middleware | `false` | 2/3 | ⬜ absent in both repos (git grep) |
| `maintenance_msg` | string | app launch | "" | 2/3 | ⬜ absent in both repos (git grep) |
| `force_update` | bool | app launch | `false` | 3 | ⬜ the app reacts only to the 403 text (`src/components/Error/index.js:68`) |
| `page_size` | number | list screens | `15` | 3 | ⬜ `PAGE_SIZE = 15` ×3 and `LIMIT = 15` (Phase 3 §4); v4 pages fixed at 12 |
| `api_timeout_ms` | number | `createApi.js` | `10000` | 3 | ⬜ `timeout: 10000` (`src/store/apis/createApi.js:48`) |
| `cache_keep_unused_s` | number | `createApi.js` | `300` | 3 | ⬜ `keepUnusedDataFor: 300` (`src/store/apis/createApi.js:111`) |
| `max_cached_items` | number | `paginationHelpers.js` | `500` | 3 | ⬜ `DEFAULT_MAX_CACHED_ITEMS = 500` (`paginationHelpers.js:11`); v4 lists also cap at 500 |
| `feature_flags` | object | screens (gate UI) | `{}` | 3 | 🟡 screen v1/v2 switches only — D10 `screen_v2_*` booleans (`helpers/appFeatures.js:38`) |

> `feature_flags` is an open object (e.g. `{ advdep_entry: true, otp_login: true }`). Candidates: AdvDep ledger entry points ([[advdep-ui-entry-points]]), OTP login toggle, incident screen hides. Each flag is read as `flags.x ?? <compiled default>`.
>
> **`diesel_limit` is intentionally absent** from this catalogue — it keeps its own `counters` doc + `/sadmin/all/diesel_limit` route on `slave` (decision 6). Listed here only for awareness as the precedent.

## 5. Blast radius — file inventory

**Status (2026-10-01):** ⬜ none of the new files exists (git grep at `6d41ce5` / `ea7e7222`); `helpers/middlewares.js:112-141` is unchanged; the `src/utils/firebase.js` row is ✅ (tasks_17). dip-web rows not re-assessed.

### Backend (`dzzlo_oms_api`, v3 only)

| File | Change | Phase |
| --- | --- | --- |
| `api_v3/controllers/sadmin/settings.js` | **new** — `get_settings` (admin), `update_settings` | 1 |
| `api_v3/controllers/settings.js` | **new** — `get_app_settings` (public-authed read) | 1 |
| `api_v3/routes/sadmin/index.js` | mount `GET|PUT /settings` | 1 |
| `api_v3/routes/collections/settings.js` + v3 router index | mount `GET /settings` (non-sadmin) | 1 |
| `helpers/settingsCache.js` | **new** — cached `getAppSettings()` reader for server-side use | 1 |
| `helpers/middlewares.js:112-141` | `check_user_version` reads `min_app_version` + msgs from settings; constant becomes floor | 2 |
| `models/counters.js` | doc comment only (records `app_settings` doc; `diesel_limit` already noted in slave) | 1 |

### App (`dzzlo_oms_app`)

| File | Change | Phase |
| --- | --- | --- |
| `src/store/apis/dzzlooms/settings.js` | **new** — `getAppSettings` RTK query | 3 |
| `src/store/slices/settings.js` (or context) | **new** — hold fetched settings | 3 |
| `src/navigation/AppNavigatorContainer.js` | fetch settings on launch; handle `force_update`/`maintenance_mode` | 3 |
| `src/store/apis/createApi.js` | `timeout`/`keepUnusedDataFor` read from settings w/ fallback | 3 |
| `src/store/apis/paginationHelpers.js` | `max_cached_items` w/ fallback | 3 |
| `src/screens/Common/Vehicles/index.js`, `src/screens/Customer/Vehicles/index.js`, daily report | `page_size` w/ fallback | 3 |
| relevant screens | `feature_flags` gates | 3 |
| `src/utils/firebase.js` | remove/retire dead remote-config helpers | 4 |

### Web admin (`dip-web`)

| File | Change | Phase |
| --- | --- | --- |
| `src/store/apis/sadmin/imp_actions.js` | add generic `get/update_settings` RTK endpoints (`/sadmin/settings`); leave existing `diesel_limit` endpoints untouched | 4 |
| `src/pages/superadmin/db/ImpActions.js` (or new `Settings` page) | superadmin Settings form (version floor, maintenance, flags). Diesel keeps its existing control | 4 |

## 5b. Phase 0 — PRECONDITION: reconcile `slave` into `v1.5.4`

**Status (2026-10-01):** ✅ moot — the diesel limit merged to the mainline through PR #33 (`3c011df`, 2026-06-12) and is on master 1.5.5 (files and test in the roll-up); nothing to merge.

This plan cannot start until the diesel/qty-cap backend (on `slave`) is merged into the mainline (`v1.5.4`). Today they've diverged from merge-base `1.5.3`:

- **`v1.5.4`** (+27): AdvDep voucher type & ledger, `max_cr_lmt` redesign + v1.77 gate, veh_trns pagination/req-count/search, reports IST fixes, prod_disc guards.
- **`slave`** (+4): `feat(orders): add configurable per-line Diesel quantity cap` (+ its merge), `fix(so): reject empty-product SOs and slim prodRate payload` (+ its merge).

**Action:** merge `slave` → `v1.5.4` (bring the 4 slave commits onto mainline). **Single expected conflict:** `api_v3/services/order_msts.js` — touched on both sides (slave inserts `assertDieselQtyLimit(...)` calls at create/edit/process; v1.5.4 reworked the same credit/order area for AdvDep + `max_cr_lmt`). Resolve by keeping the v1.5.4 logic **and** re-inserting the three `assertDieselQtyLimit` calls (slave call sites: `order_msts.js:802, 944, 989`; also `so_msts.js:33, 254`). No other file overlaps, so the rest should merge clean.

**Verify after merge:** diesel qty-cap test green (`test/api_v3/collections/so_msts/dieselQtyLimit.test.js`), AdvDep + maxcrlmt order tests still green, and `helpers/dieselQtyLimit.js` + `controllers/sadmin/diesel_limit.js` + the `/sadmin/all/diesel_limit` routes are present on the merged tree. Only then begin Phase 1.

## 6. Phases & ordering

**Status (2026-10-01):** Phase 0 ✅ (moot), Phases 1–3 ⬜, Phase 4 🟡 — see the roll-up.

0. **Phase 0 — PRECONDITION:** merge `slave` → `v1.5.4` (§5b). Must complete before Phase 1.
1. **Phase 1 — Backend settings store** (`counters` doc + read/write endpoints + cached reader). Ship-able alone; no behavior change until something consumes it.
2. **Phase 2 — Version gate & maintenance via settings** (migrate the hardcoded `1.68`; add force-update/maintenance signals). **Order-sensitive:** seed the `app_settings` doc *before* switching the middleware to read it.
3. **Phase 3 — App consumption** (fetch on launch + slice; replace hardcoded constants; force-update/maintenance UI; feature-flag gates).
4. **Phase 4 — dip-web Settings UI, tests, rollout** (superadmin form for the new keys; `diesel_limit` already shipped via the Phase 0 merge; retire dead Firebase config).

> **Critical ordering (Phase 2):** the version middleware must keep working if settings are missing. Deploy the settings-reading middleware with the compiled `1.68` floor as fallback (§ decision 4), seed the `app_settings` doc, *then* set `min_app_version`. Never make the middleware hard-depend on a DB read in the request path of every call — it reads from the cached `settingsCache` (Phase 1), refreshed on an interval, so a DB blip can't 403 the whole fleet.

## 7. Risk summary

**Status (2026-10-01):** ⬜ still open, and one risk is sharper than written: a DB-driven floor turns its write into a fleet-wide switch, so that write must be superadmin-only — superadmin endpoints require a superadmin bearer (see `X-SEC-2` in tasks_01).

- **Fleet lockout via bad `min_app_version` write.** Mitigated by decision 4 (constant is a hard floor; superadmin can only raise) + a dip-web confirm dialog showing how many active versions would be blocked.
- **Settings read in the hot path.** The version middleware runs on *every* request. It must read from an in-process **cached** snapshot (`settingsCache`, TTL like the existing `refDataCache`), never a per-request DB query. See Phase 1 §3.
- **Two-source config drift.** Avoided by decision (no Firebase). Single `app_settings` doc is canonical.
- **Read endpoint accidentally gated.** `GET /settings` must sit **outside** the `/sadmin` guard (decision 3) or the app can't read it. Acceptance test covers a dealer token hitting it.
- **Scope creep into a full feature-flag platform.** Keep `feature_flags` a flat object read with compiled fallbacks; resist per-user/% rollout targeting in v1.

## 8. Relationship to existing work

**Status (2026-10-01):** add — the screen redesign's D10 house toggles (screen v1/v2 switches, absent = ON) overlap `feature_flags`; tasks_17 removed Remote Config.

- Complements [[maxcrlmt-redesign]] and [[advdep-feature-design]]: both rely on the `meta`→version gate idiom this plan also uses, and both add policy (`feature_flags.advdep_entry`, credit defaults) that can live here once stable.
- Honors [[scope-cut-over-conditional-complexity]]: the per-knob fallback means any single setting can be dropped from scope without branching the consumers.
- Built for the [[two-session-implementation-workflow]]: each phase file below is paste-ready for an implementer session.

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-APP-5 | 🆕 Rebase or re-cut the DB-driven version gate — API PR #34 (`387072a`) and app PR #47 (`cfd1243e`) — before either merges | Both OPEN and `CONFLICTING` / `DIRTY` (`gh pr view 34`, `47`, 2026-10-01), untouched since 2026-06-29. #47 is based on 1.78 (`7fb8389d`) and both files it edits changed since (`createApi.js`, `AppNavigatorContainer.js`: +117 / −40). Neither PR has a test; #34 hardcodes `DEFAULT_LATEST_VERSION = 1.78` (1.79 has shipped), answers bad input with 404, lets a write drop the floor below 1.68 (decision 4 wants a hard floor), and master's `test/api_v3/features/version_gate/index.test.js` pins the hardcoded gate it replaces; #47's banner text is an English literal (`cfd1243e:src/components/UpdatePrompt/index.js:27`). A floor write is a fleet-wide switch and must be superadmin-only: superadmin endpoints require a superadmin bearer (see `X-SEC-2` in tasks_01) | app + API | M | `X-SEC-2` (tasks_01); `T09-N1` |
| T09-N1 | 🆕 Give non-screen flags and operational knobs a home: build Phase 1's settings store, or widen D10 with a second key family — the D10 toggles do not cover them | D10 keeps only `screen_v2_(dealer\|customer)_[a-z0-9_]+` booleans on read and write and leaves non-screen toggles out on purpose (`helpers/appFeatures.js:31-38,48-57`; `api_v3/controllers/sadmin/app_features.js:43-49`); yet the tasks_05 kill-switches (`push_backend`, `push_send_enabled`, `journey_<id>_enabled`), tasks_10's `analytics_enabled` and tasks_14's DU-slip kill switch (`T14-N3` in tasks_14) have nowhere to live now that Remote Config is gone (tasks_17). The v4 read also needs a bearer (`api_v4/routes/app.js:10-14`), so it cannot serve pre-login settings | API (+ app reader) | M | `X-SEC-2` (tasks_01) |
| T09-N2 | 🆕 Decide which path owns "update available" | Today it is a OneSignal In-App Message on an `app_version` trigger whose `update_app` action opens the store (`src/helpers/OneSignal/index.js:43-79`, console-driven); PR #47 adds a header-driven banner; tasks_05's migration plan (Step C6) moves the prompt to Firebase In-App Messaging. §1 of this plan knows none of them; two live paths would prompt twice | app | XS | `X-APP-5` |
| T09-N3 | 🆕 Use the floor to retire old-client code: raise it once store adoption allows, then delete `legacy_credit_presenter` and the older-client branches | The floor is still 1.68 (`helpers/middlewares.js:123`) while 1.79 is out; `legacy_credit_presenter` rewrites credit for ≤ 1.77 clients and says "Remove this middleware once v1.77 is retired" (`helpers/middlewares.js:143-190`, mounted `api_v/api3.js:19`); 17 places in 10 `api_v3` files read `meta.version` to branch on the client's build | API | M | store adoption figures (❔ — Play Console / App Store Connect, the user); Phase 2 or a one-line floor change |
| T09-N4 | 🆕 Compare app versions part by part, not with `Number(version)` | `Number("1.100")` is 1.1, so a "1.100" build would be blocked by the `<= 1.68` gate (`helpers/middlewares.js:123-128`) and treated as legacy by the credit presenter (`:175`); PR #34 keeps the same arithmetic; the app sends `DeviceInfo.getVersion()` unchanged (`src/store/apis/createApi.js:12,45`) — safe only while minor versions stay at two digits | API | XS | — |
