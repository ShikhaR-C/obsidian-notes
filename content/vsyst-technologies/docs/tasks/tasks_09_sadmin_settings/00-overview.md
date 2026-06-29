# Superadmin-Controlled App Settings — Server-Driven Config for `dzzlo_oms_app`

**Status:** Spec'd (2026-06-15). Not yet implemented.
**Owner:** TBD
**Created:** 2026-06-15
**Base branch:** **`v1.5.4` after merging `slave` into it — merge is a precondition (see §0).** `v1.5.4` is the active mainline (27 commits since the `1.5.3` merge-base: AdvDep voucher ledger, `max_cr_lmt` redesign, veh_trns pagination, reports IST, …). `slave` carries only 4 commits — the `diesel_limit`/qty-cap config (the proven precedent this plan generalizes) + a `so-products` hotfix — that have **not** landed on mainline. Do **not** branch from `slave` (it lacks all the v1.5.4 mainline work); merge `slave`'s 4 commits into `v1.5.4`, then build this plan on the merged tree.
**Scope:** Add a single superadmin-controlled settings surface in `dzzlo_oms_api` (v3) — written from the `dip-web` superadmin, read by `dzzlo_oms_app` — so that operational knobs currently **hardcoded in the app** or **hardcoded in the API** can be changed without an app release. First and highest-value consumer: the **app version floor / force-update / maintenance** lever (today a hardcoded constant). Legacy API v1/v2 are intentionally untouched.

---

## 1. The problem

There is **no general config layer** today. Three independent facts make this expensive:

1. **The version floor is a hardcoded constant.** `dzzlo_oms_api/helpers/middlewares.js:123` sets `allowedVersion = Number(1.68)` with a `"1.510"` test bypass, applied globally at `dzzlo_oms.js:75`. Raising the floor, changing the "update from store" copy, or posting a maintenance banner **requires an API redeploy**. Combined with [[app-ota-and-version-gating]] (no CodePush → a store update is the only client fix), this middleware is effectively the **only release-free lever over fielded apps** — and it isn't configurable.

2. **The app is full of hardcoded operational constants** with no way to tune them remotely: `PAGE_SIZE = 15` (`src/screens/Common/Vehicles/index.js`, `src/screens/Customer/Vehicles/index.js`, daily report), `timeout = 10000` / `maxRetries = 2` / `keepUnusedDataFor = 300` (`src/store/apis/createApi.js`), `DEFAULT_MAX_CACHED_ITEMS = 500` (`src/store/apis/paginationHelpers.js`, the low-RAM Android guard — see [[flashlist-v2-mvcp-default-on]]). Tuning any of these for low-end Android needs a store release.

3. **The pattern is already proven on `slave` for one knob — `diesel_limit`.** On `slave`, `api_v3/controllers/sadmin/diesel_limit.js` + `helpers/dieselQtyLimit.js` store config in the `counters` collection (`{ doc_name: "diesel_limit", data: { value, error_message } }`), expose `GET|POST /api/v3/sadmin/all/diesel_limit` (superadmin), are written from the dip-web DB-Actions page (`src/store/apis/sadmin/imp_actions.js:109-126`, `src/pages/superadmin/db/ImpActions.js`), and are **enforced server-side** in `api_v3/services/order_msts.js` (3 call sites) and `so_msts.js` (2 call sites), with tests in `test/api_v3/collections/so_msts/dieselQtyLimit.test.js`. **This is the template to generalize.** What's missing is an **app-readable** config doc (everything below) — `diesel_limit` is server-enforced only, the app never reads it. (Note: on the checked-out `v1.5.4` branch the diesel backend is absent and the dip-web stub looks orphaned — that's a branch artifact; build on `slave`.) Firebase Remote Config is separately wired (`src/utils/firebase.js` `initRemoteConfig`/`getRemoteValue`, called at `src/navigation/AppNavigatorContainer.js:66`) but **no key is ever read** — do not adopt it as a second source.

## 2. The approach (one source of truth)

Build **one** settings store in `dzzlo_oms_api`, owned by the existing dip-web superadmin, with two access tiers:

| Endpoint | Auth | Purpose | Cache |
| --- | --- | --- | --- |
| `PUT /api/v3/sadmin/settings` | superadmin (existing `/sadmin` guard) | write any setting | bust on write |
| `GET /api/v3/settings` | any authenticated user (NOT under `/sadmin`) | app reads config | `refDataCache` |

> **Do NOT add Firebase Remote Config as a second config system.** One authenticated source of truth (our own DB, already reachable via the `meta`-header'd client) is simpler to reason about and keeps app + dip-web + middleware agreeing. The unused `firebase.js` remote-config helpers can be left dormant or deleted in Phase 4.

**Storage — reuse the `counters` collection (decision 1).** `units`, `hsncodes` (`api_v3/controllers/sadmin/units_hsns.js`) and `diesel_limit` (slave's `helpers/dieselQtyLimit.js`) already live as `counters` docs keyed by `doc_name` with a free-form `data` subdocument. Add **one** doc `{ doc_name: "app_settings", data: { ...settings } }` for the app-read config. No new model, no migration, identical to the proven `diesel_limit` precedent. (Alternative: a dedicated `settings` model — cleaner typing, more infra. Not chosen; see §6.)

**Client contract — server-driven with client fallback (decision 2).** Every consumed setting keeps its current hardcoded value as the **fallback** (`settings.page_size ?? 15`). The app must work fully if `GET /settings` fails or returns partial data — config is an *override*, never a *dependency*. This keeps the app offline-first and makes rollout risk-free.

## 3. Confirmed decisions

1. **Storage = `counters` doc `app_settings`** (reuse the proven `diesel_limit`/`units` pattern; no new model/migration).
2. **Every setting has a client-side fallback.** Server config overrides; never blocks. App is fully functional with `GET /settings` unreachable.
3. **Read endpoint is NOT superadmin-gated.** `GET /api/v3/settings` must be reachable by every authenticated dealer/customer app. Only the **write** (`PUT /sadmin/settings`) sits behind the superadmin guard. (The orphaned diesel stub put *read* under `/sadmin` — that would have been unreadable by the app; do not copy it.)
4. **Version floor migrates from constant → setting, but keeps the constant as a hard floor.** `min_app_version` is read from settings; if settings are unreachable the middleware falls back to the compiled-in `1.68`. A superadmin can only **raise** the floor above the compiled default, never silently drop below it (guards against a bad write locking nobody out / letting everybody in). See Phase 2.
5. **Do NOT touch API v1/v2.** v1 is already disabled (`dzzlo_oms.js:107` commented). Version middleware is global, so the floor still applies to v2 traffic — fine. New settings endpoints are v3-only.
6. **Leave `diesel_limit` as-is; do NOT migrate it.** It already works on `slave` (own `counters` doc, own `/sadmin/all/diesel_limit` route, server-enforced in `order_msts`/`so_msts`, tested). It's server-enforced only — the app never reads it — so there's no benefit to folding it into `app_settings`, and doing so would churn working, tested code. The new `app_settings` doc is **additive**, for the app-read keys in §4. New future knobs go into `app_settings`; the established `diesel_limit` doc stays its own thing. (Both follow the identical `counters` pattern — consistency without a risky migration.)

## 4. Settings catalogue (initial keys)

`data` shape on the `app_settings` doc. All optional; absent key → app/middleware fallback.

| Key | Type | Consumer | Fallback | Phase |
| --- | --- | --- | --- | --- |
| `min_app_version` | number | version middleware | `1.68` (compiled) | 2 |
| `update_msg_ios` | string | version middleware | existing literal | 2 |
| `update_msg_android` | string | version middleware | existing literal | 2 |
| `maintenance_mode` | bool | app launch + middleware | `false` | 2/3 |
| `maintenance_msg` | string | app launch | "" | 2/3 |
| `force_update` | bool | app launch | `false` | 3 |
| `page_size` | number | list screens | `15` | 3 |
| `api_timeout_ms` | number | `createApi.js` | `10000` | 3 |
| `cache_keep_unused_s` | number | `createApi.js` | `300` | 3 |
| `max_cached_items` | number | `paginationHelpers.js` | `500` | 3 |
| `feature_flags` | object | screens (gate UI) | `{}` | 3 |

> `feature_flags` is an open object (e.g. `{ advdep_entry: true, otp_login: true }`). Candidates: AdvDep ledger entry points ([[advdep-ui-entry-points]]), OTP login toggle, incident screen hides. Each flag is read as `flags.x ?? <compiled default>`.
>
> **`diesel_limit` is intentionally absent** from this catalogue — it keeps its own `counters` doc + `/sadmin/all/diesel_limit` route on `slave` (decision 6). Listed here only for awareness as the precedent.

## 5. Blast radius — file inventory

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

This plan cannot start until the diesel/qty-cap backend (on `slave`) is merged into the mainline (`v1.5.4`). Today they've diverged from merge-base `1.5.3`:

- **`v1.5.4`** (+27): AdvDep voucher type & ledger, `max_cr_lmt` redesign + v1.77 gate, veh_trns pagination/req-count/search, reports IST fixes, prod_disc guards.
- **`slave`** (+4): `feat(orders): add configurable per-line Diesel quantity cap` (+ its merge), `fix(so): reject empty-product SOs and slim prodRate payload` (+ its merge).

**Action:** merge `slave` → `v1.5.4` (bring the 4 slave commits onto mainline). **Single expected conflict:** `api_v3/services/order_msts.js` — touched on both sides (slave inserts `assertDieselQtyLimit(...)` calls at create/edit/process; v1.5.4 reworked the same credit/order area for AdvDep + `max_cr_lmt`). Resolve by keeping the v1.5.4 logic **and** re-inserting the three `assertDieselQtyLimit` calls (slave call sites: `order_msts.js:802, 944, 989`; also `so_msts.js:33, 254`). No other file overlaps, so the rest should merge clean.

**Verify after merge:** diesel qty-cap test green (`test/api_v3/collections/so_msts/dieselQtyLimit.test.js`), AdvDep + maxcrlmt order tests still green, and `helpers/dieselQtyLimit.js` + `controllers/sadmin/diesel_limit.js` + the `/sadmin/all/diesel_limit` routes are present on the merged tree. Only then begin Phase 1.

## 6. Phases & ordering

0. **Phase 0 — PRECONDITION:** merge `slave` → `v1.5.4` (§5b). Must complete before Phase 1.
1. **Phase 1 — Backend settings store** (`counters` doc + read/write endpoints + cached reader). Ship-able alone; no behavior change until something consumes it.
2. **Phase 2 — Version gate & maintenance via settings** (migrate the hardcoded `1.68`; add force-update/maintenance signals). **Order-sensitive:** seed the `app_settings` doc *before* switching the middleware to read it.
3. **Phase 3 — App consumption** (fetch on launch + slice; replace hardcoded constants; force-update/maintenance UI; feature-flag gates).
4. **Phase 4 — dip-web Settings UI, tests, rollout** (superadmin form for the new keys; `diesel_limit` already shipped via the Phase 0 merge; retire dead Firebase config).

> **Critical ordering (Phase 2):** the version middleware must keep working if settings are missing. Deploy the settings-reading middleware with the compiled `1.68` floor as fallback (§ decision 4), seed the `app_settings` doc, *then* set `min_app_version`. Never make the middleware hard-depend on a DB read in the request path of every call — it reads from the cached `settingsCache` (Phase 1), refreshed on an interval, so a DB blip can't 403 the whole fleet.

## 7. Risk summary

- **Fleet lockout via bad `min_app_version` write.** Mitigated by decision 4 (constant is a hard floor; superadmin can only raise) + a dip-web confirm dialog showing how many active versions would be blocked.
- **Settings read in the hot path.** The version middleware runs on *every* request. It must read from an in-process **cached** snapshot (`settingsCache`, TTL like the existing `refDataCache`), never a per-request DB query. See Phase 1 §3.
- **Two-source config drift.** Avoided by decision (no Firebase). Single `app_settings` doc is canonical.
- **Read endpoint accidentally gated.** `GET /settings` must sit **outside** the `/sadmin` guard (decision 3) or the app can't read it. Acceptance test covers a dealer token hitting it.
- **Scope creep into a full feature-flag platform.** Keep `feature_flags` a flat object read with compiled fallbacks; resist per-user/% rollout targeting in v1.

## 8. Relationship to existing work

- Complements [[maxcrlmt-redesign]] and [[advdep-feature-design]]: both rely on the `meta`→version gate idiom this plan also uses, and both add policy (`feature_flags.advdep_entry`, credit defaults) that can live here once stable.
- Honors [[scope-cut-over-conditional-complexity]]: the per-knob fallback means any single setting can be dropped from scope without branching the consumers.
- Built for the [[two-session-implementation-workflow]]: each phase file below is paste-ready for an implementer session.
