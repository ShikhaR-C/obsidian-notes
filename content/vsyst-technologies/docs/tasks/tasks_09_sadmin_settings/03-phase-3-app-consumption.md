# Phase 3 — App consumption (`dzzlo_oms_app`)

**Repo:** `dzzlo_oms_app`
**Goal:** Fetch `GET /api/v3/settings` once on launch, hold it in a slice, and let consumers read each knob with its existing hardcoded value as fallback. Handle `force_update` / `maintenance_mode` at the entry point. **Config is an override, never a dependency** (overview decision 2) — the app must be fully functional if the fetch fails.

---

## 1. RTK query — `src/store/apis/dzzlooms/settings.js` (new)

Mirror an existing reference-data query (e.g. the v3 collection queries). Endpoint: `GET {API_URL_V}/settings`. The `meta` header (version, device info) is already attached globally in `src/store/apis/createApi.js`.

```js
import { api } from "../createApi";
import { API_URL_V } from "../../../utils/API";

export const settingsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getAppSettings: builder.query({
      query: () => ({ url: `${API_URL_V}/settings`, method: "GET" }),
      transformResponse: (r) => r?.data ?? {},
      keepUnusedDataFor: 600,
    }),
  }),
});

export const { useGetAppSettingsQuery } = settingsApi;
```

---

## 2. Slice / selector — `src/store/slices/settings.js` (new)

Hold the last good settings so non-hook code (`createApi.js`, `paginationHelpers.js`) can read synchronously. Simplest: a tiny slice populated from the query's `fulfilled` action, plus a `getSettingsSnapshot()` plain getter backed by a module variable for non-React reads.

```js
// module-level snapshot for non-React consumers (createApi, paginationHelpers)
let _snapshot = {};
export const getSettingsSnapshot = () => _snapshot;
export const setSettingsSnapshot = (s) => { _snapshot = s || {}; };

// + a normal redux slice holding `settings` for React selectors, updated alongside the snapshot.
```

Wire it so that whenever `getAppSettings` succeeds you call `setSettingsSnapshot(data)` and dispatch the slice update (one `useEffect` in the launch container, §3).

> Keep a single source: the snapshot and the slice are set together. Non-React reads use `getSettingsSnapshot()`; React reads use a selector.

---

## 3. Fetch on launch + gate the app — `src/navigation/AppNavigatorContainer.js`

This file already calls `initRemoteConfig` at line ~66 (Firebase, dead). Add the settings fetch here and **stop calling Firebase remote config** (retired in Phase 4).

```js
const { data: settings } = useGetAppSettingsQuery(undefined, {
  refetchOnMountOrArgChange: true,
});

useEffect(() => {
  if (settings) {
    setSettingsSnapshot(settings);
    dispatch(setSettings(settings));
  }
}, [settings]);
```

Then gate the UI:

- **`settings.maintenance_mode === true`** (or any API response with the Phase 2 `503 { maintenance: true }`) → render a full-screen non-dismissable **Maintenance** view (`maintenance_msg`). The 503 path matters: even before the settings query resolves, a 503 from any request signals maintenance.
- **`settings.force_update === true`** AND the running app version is below `settings.min_app_version` → render a non-dismissable **Update Required** screen with a store deep-link. (The server already 403s old versions in Phase 2; this is the *graceful client* version so users get an in-app prompt instead of opaque request failures.)

> Both screens must be reachable **without** auth state, since version/maintenance gating can apply pre-login. Place the check above the auth navigator switch.

---

## 4. Replace hardcoded constants (each with fallback)

| File | Current | New |
| --- | --- | --- |
| `src/store/apis/createApi.js` | `timeout: 10000` | `getSettingsSnapshot().api_timeout_ms ?? 10000` |
| `src/store/apis/createApi.js` | `keepUnusedDataFor: 300` (default) | `getSettingsSnapshot().cache_keep_unused_s ?? 300` |
| `src/store/apis/paginationHelpers.js` | `DEFAULT_MAX_CACHED_ITEMS = 500` | `getSettingsSnapshot().max_cached_items ?? 500` |
| `src/screens/Common/Vehicles/index.js` | `PAGE_SIZE = 15` | `getSettingsSnapshot().page_size ?? 15` |
| `src/screens/Customer/Vehicles/index.js` | `PAGE_SIZE = 15` | `getSettingsSnapshot().page_size ?? 15` |
| `src/screens/Common/Reports/DailyReport/index.js` | `LIMIT = 15` | `getSettingsSnapshot().page_size ?? 15` |
| `src/screens/Customer/NewOrder/BSheets/SelectVehicle.js` | `PAGE_SIZE = 15` | `getSettingsSnapshot().page_size ?? 15` |

Notes:

- `createApi.js` reads the snapshot at **request build time** (inside the `prepareHeaders`/baseQuery closure or a per-request option), not at module load — so a settings fetch that lands after app start still applies to later requests. If the RTK base query can't read it dynamically, accept that timeout/cache use the snapshot present at store-creation and refine later; **page_size and flags are the higher-value, low-risk ones — do those first** ([[scope-cut-over-conditional-complexity]]).
- Don't let `max_cached_items` go below a safe minimum; clamp: `Math.max(100, settings.max_cached_items ?? 500)` to protect the low-RAM Android guard ([[flashlist-v2-mvcp-default-on]]).

---

## 5. Feature flags

Read flags as `getSettingsSnapshot().feature_flags?.<key> ?? <compiled default>`. Initial candidates (each defaults to today's behavior so an absent flag changes nothing):

- `advdep_entry` — show/hide the AdvDep ledger entry points ([[advdep-ui-entry-points]]). Default `true`.
- `otp_login` — enable OTP login path. Default `true`.
- `<incident_hide_x>` — temporarily hide a screen during an incident. Default `false` (visible).

Add a tiny hook `useFeatureFlag(key, fallback)` selecting from the settings slice for React consumers.

---

## 6. Phase 3 acceptance

- [ ] Cold launch with `GET /settings` reachable → snapshot populated; `page_size` from server used in vehicle list.
- [ ] **Airplane mode / `GET /settings` fails** → app launches and works fully on all fallbacks (no blank screens, no crash).
- [ ] Server `maintenance_mode = true` (or any `503 {maintenance:true}`) → non-dismissable Maintenance screen, even pre-login.
- [ ] `force_update = true` + running version `< min_app_version` → Update Required screen with working store link; not shown when version is current.
- [ ] Set `page_size = 30` server-side → next vehicle-list fetch pages by 30 (within query cache window) without app rebuild.
- [ ] `feature_flags.advdep_entry = false` → AdvDep entry points hidden; absent flag → visible (unchanged).
- [ ] `max_cached_items` set to `10` → clamped to the safe minimum (no OOM regression).
