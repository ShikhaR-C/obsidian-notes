# Phase 4 — dip-web Settings UI, tests, rollout

**Repos:** `dip-web`, `dzzlo_oms_api` (tests), `dzzlo_oms_app` (cleanup)
**Goal:** Give the superadmin a real Settings form for the new keys, add backend + app tests, retire the dead Firebase remote-config wiring, and roll out safely.

---

## 1. dip-web superadmin Settings UI

The existing `diesel_limit` control on the DB-Actions page (`src/pages/superadmin/db/ImpActions.js`, RTK in `src/store/apis/sadmin/imp_actions.js`) **stays as-is** — its backend route is live once the Phase 0 merge lands. Add a sibling **App Settings** section (same page or a new `/settings` superadmin route).

### 1a. RTK endpoints — `src/store/apis/sadmin/imp_actions.js` (or a new `settings.js`)

```js
get_app_settings: builder.query({
  query: () => ({ url: `${API_URL_V_DZZLOOMS}/sadmin/settings`, method: "GET" }),
  providesTags: [{ type: "app_settings", id: "DOC" }],
}),
update_app_settings: builder.mutation({
  query: (body) => ({ url: `${API_URL_V_DZZLOOMS}/sadmin/settings`, method: "PUT", body }),
  invalidatesTags: [{ type: "app_settings", id: "DOC" }],
}),
```

Register the `app_settings` tag in `createApi.js` `tagTypes` (next to the existing `diesel_limit` tag).

### 1b. Form fields

Group by the catalogue (overview §4): **App version** (`min_app_version`, `update_msg_ios`, `update_msg_android`), **Availability** (`maintenance_mode`, `maintenance_msg`, `force_update`), **Tuning** (`page_size`, `api_timeout_ms`, `cache_keep_unused_s`, `max_cached_items`), **Feature flags** (key/value editor for `feature_flags`).

### 1c. The lockout confirm guard (from Phase 2 §4)

Before submitting a raised `min_app_version`, show a confirm dialog naming the consequence:

> "Setting the minimum version to **1.78** will block every device on 1.77 or older until they update from the store. Continue?"

Submit only on confirm. (Server still rejects values below the compiled floor as a backstop.)

---

## 2. Backend tests — `dzzlo_oms_api/test`

Model on the existing `test/api_v3/collections/so_msts/dieselQtyLimit.test.js` (the diesel precedent's tests).

- `test/api_v3/collections/settings/index.test.js` (new):
  - superadmin `PUT /sadmin/settings` partial `$set` (no clobber); unknown-key `400`; non-superadmin `403`.
  - `GET /settings` readable by a dealer token; `401` without auth.
  - `min_app_version` below compiled floor → `400`.
- `test/api_v3/middleware/version_gate.test.js` (new or extend): floor from settings, compiled fallback, `503` maintenance, `1.510` bypass, DB-down degrades to compiled floor.

---

## 3. App cleanup — retire dead Firebase remote config

- `src/utils/firebase.js`: remove `initRemoteConfig` / `getRemoteValue` (or leave the file but delete the unused exports) now that `app_settings` is the single source (overview decision §2).
- `src/navigation/AppNavigatorContainer.js`: remove the `initRemoteConfig` call (~line 66) replaced by the settings fetch in Phase 3.
- Keep Firebase Crashlytics/Analytics/Performance — only the **remote config** piece is retired.

---

## 4. App tests

- Settings slice/snapshot: `getAppSettings` success populates snapshot + slice; failure leaves fallbacks.
- Gate rendering: `maintenance_mode` → Maintenance screen; `force_update` + low version → Update Required; neither → normal app.
- `max_cached_items` clamp to safe minimum.

---

## 5. Rollout sequence (whole feature)

1. **API:** deploy Phase 1 + Phase 2 (on the Phase 0 merged `v1.5.4`+`slave` tree). No behavior change (no `app_settings` doc → compiled fallbacks). Verify version gate unchanged in prod.
2. **dip-web:** ship the Settings UI. Seed `app_settings` with current-equivalent values (`min_app_version: 1.68`, `maintenance_mode: false`). Still no behavior change.
3. **App:** ship the Phase 3 build that reads settings (with fallbacks) and handles maintenance/force-update. Until enough users are on this build, server-side gates (Phase 2) remain the enforcement; the app screens are the graceful layer.
4. **Operate:** use the dip-web form for version floor bumps, maintenance windows, low-RAM Android tuning, and feature-flag toggles — no redeploys.

> Each step is independently shippable and reversible. No migration anywhere (additive doc). Honors [[scope-cut-over-conditional-complexity]]: any single setting can be dropped without touching its consumers (they fall back).

---

## 6. Phase 4 acceptance

- [ ] Superadmin can read & write all catalogue keys from dip-web; non-superadmin cannot reach the form's endpoints.
- [ ] Raising `min_app_version` shows the lockout confirm before writing.
- [ ] `diesel_limit` control still works unchanged (no regression from the additive settings doc).
- [ ] Backend + app test suites green, including the version-gate fallback cases.
- [ ] Firebase remote-config code removed; Crashlytics/Analytics/Performance intact.
- [ ] Full prod rollout produces zero behavior change until a setting is deliberately changed.
