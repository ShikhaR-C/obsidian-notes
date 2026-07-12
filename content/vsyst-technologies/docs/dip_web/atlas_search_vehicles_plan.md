# Atlas Search for Vehicles — `dip-web` Superadmin

> Implementation plan to replace the client-side substring filter in
> `dip-web/src/pages/superadmin/vehicles/VehList.js` with a server-driven
> Atlas Search query, end-to-end across `dzzlo_oms_api` and `dip-web`.
>
> Source research: `docs/tasks/tasks_03_mongo_search/` (especially
> `07_search_implementation_api.md` and `08_search_implementation_app.md`).

---

## Why

Today `VehList.js` (lines 39-44) does:

```js
return vehData.data.filter((item) => {
  if (!search) return true
  return item.veh_reg_no && item.veh_reg_no.toLowerCase().includes(search.toLowerCase())
})
```

This is a `String.includes` over whatever pages have already been loaded.
Fine for tens of vehicles; useless once data spans pages, and it does not
match `route` or any other field. Atlas Search lets us query the server
with typo-tolerant autocomplete and get the full corpus back ranked.

---

## Adapting the research package

The plan in `tasks_03_mongo_search/07-08` targets the React Native app and
the generic `/api/v3/veh_msts/search` route. Two adaptations are needed
for `dip-web`:

1. The current screen calls `/api/v3/sadmin/all/vehicles`, which enriches
   each vehicle with `veh_trn` (cust_name, hirer_name, driver) inside
   `services/veh_trns.js:319 getAllVehicles`. The search endpoint must
   return the same enriched shape so the existing table renders unchanged.
2. The mobile components (`@gorhom/bottom-sheet`, `react-native-paper`)
   translate to React Bootstrap (`Form.Control`, `Spinner`, `Alert`).

---

## A. Backend — `dzzlo_oms_api`

All changes inside `api_v3/` per the active dev rule. New code; no edits
to existing list endpoints.

### A1. New shared helper — `api_v3/services/_search/buildSearchStage.js` (NEW)

Exactly per `07_search_implementation_api.md` §5.1. Exports:
`atlasSearchEnabled()`, `sanitizeQ()`, `toObjectId()`, `parseDate()`,
`parsePage()`, `buildFacet()`, `unwrapFacet()`. Reused by orders/dealers
when those follow.

### A2. New rate limiter — `api_v3/helpers/searchRateLimit.js` (NEW)

60 req/min/IP per docs §3.4.

> Note: the doc places it under `helpers/`. Active-dev rule forbids
> editing `helpers/`, so put it in `api_v3/helpers/searchRateLimit.js`
> instead.

### A3. Search service — `api_v3/services/veh_msts.js` (EDIT)

Add `searchVehicles({ query })` per docs §5.2, but **wrap the result
with the `veh_trn` enrichment that `getAllVehicles` already does today**.

Cleanest refactor: extract the enrichment block from
`services/veh_trns.js:319-396` into a helper
`enrichVehiclesWithTrn(vehs)` and call it from both `getAllVehicles` and
`searchVehicles`.

- Atlas branch returns ranked `veh_msts._id`s → enrich.
- Fallback branch (`ATLAS_SEARCH !== "true"`) → regex on `veh_reg_no` +
  `route` → enrich.
- Same response shape as today: `{ success, count, pagination, data }`.

### A4. Search controller — `api_v3/controllers/sadmin/veh_msts.js` (NEW)

```js
const asyncHandler = require("../../../helpers/async")
const { searchVehicles } = require("../../services/veh_msts")

exports.SearchAllVehicles = asyncHandler(async (req, res) => {
  const result = await searchVehicles({ query: req.query })
  res.status(200).json({ success: true, ...result })
})
```

(Place under `controllers/sadmin/` because the screen is sadmin-scoped.)

### A5. Sadmin route — `api_v3/routes/sadmin/index.js` (EDIT)

```js
const { SearchAllVehicles } = require("../../controllers/sadmin/veh_msts")
const { searchLimiter } = require("../../helpers/searchRateLimit")

router.get("/search/vehicles", searchLimiter, SearchAllVehicles)
```

Final URL: `GET /api/v3/sadmin/search/vehicles?q=&cust_id=&from=&to=&page=&limit=`

The generic `/veh_msts/search` from docs §3.1 is still useful if other
roles later need vehicle search; out of scope for v1.

### A6. Atlas Search index — `veh_search` on `veh_msts`

Per docs §2.1. Two delivery options:

- **Atlas UI**: Cluster → Search → Create Index → JSON editor → paste the
  JSON from §2.1.
- **Script**: commit JSON to `dzzlo_oms_api/scripts/search/veh_search.json`
  and ship the one-off `scripts/createSearchIndexes.js` from docs §9.

Set `ATLAS_SEARCH=true` in staging/prod env. Leave unset locally — the
fallback path covers dev.

### A7. Fallback `$text` index — `models/veh_msts.js` (EDIT)

```js
veh_mst_Schema.index({ veh_reg_no: "text", route: "text" })
```

Skip if running only on Atlas; needed for unit tests on
`mongodb-memory-server` (which does not support `$search`). This edit
lives outside `api_v3/` — get a one-off active-dev exception or move the
test to a real Atlas test cluster.

### A8. Tests — `test/api_v3/features/sadmin/search_vehicles.test.js` (NEW)

```js
process.env.ATLAS_SEARCH = "false"
// seed 3-5 vehicles
// supertest GET /api/v3/sadmin/search/vehicles?q=KA01
// assert data[0].veh_trn is populated
```

---

## B. Frontend — `dip-web`

### B1. Tag types — `src/store/apis/createApi.js`

No edit. `veh_msts` is already in `tagTypes` (line 64).

### B2. New RTK Query endpoint — `src/store/apis/sadmin/veh_msts.js` (EDIT)

Add `search_sadmin_veh_msts` alongside the existing
`fetch_sadmin_veh_msts`:

```js
search_sadmin_veh_msts: builder.query({
  query: ({ q, cust_id, page = 1, limit = 15 } = {}) => ({
    url: `${API_URL_V_DZZLOOMS}/sadmin/search/vehicles`,
    method: "GET",
    params: {
      q: q || undefined,
      cust_id: cust_id || undefined,
      page,
      limit,
    },
  }),
  providesTags: (result) =>
    result?.data
      ? [
          ...result.data.map(({ _id }) => ({ type: "veh_msts", id: _id })),
          { type: "veh_msts", id: "SEARCH" },
        ]
      : [{ type: "veh_msts", id: "SEARCH" }],
  serializeQueryArgs: ({ queryArgs }) =>
    `${queryArgs?.q || ""}|${queryArgs?.cust_id || ""}`,
  merge: (currentCache, newItems, { arg }) => {
    // page 1 replaces, page N appends — same shape as fetch_sadmin_veh_msts
    if (arg?.page > 1 && currentCache?.data) {
      const ids = new Set(currentCache.data.map((d) => d._id));
      const merged = [
        ...currentCache.data,
        ...newItems.data.filter((d) => !ids.has(d._id)),
      ];
      return { ...currentCache, ...newItems, data: merged };
    }
    return newItems;
  },
  forceRefetch: ({ currentArg, previousArg }) => currentArg !== previousArg,
}),
```

Export `useLazySearch_sadmin_veh_mstsQuery`.

> **Why a new endpoint and not a `q` param on the existing one**: the
> existing `fetch_sadmin_veh_msts` keys cache by `endpointName`, so all
> results merge into one cache entry. A search query needs its own cache
> slot per `q` so the browse list isn't polluted.

### B3. Tiny debounce hook — `src/utils/Hooks/useDebouncedValue.js` (NEW)

```js
import { useEffect, useState } from "react"

export default function useDebouncedValue(value, delay = 300) {
  const [v, setV] = useState(value)
  useEffect(() => {
    const id = setTimeout(() => setV(value), delay)
    return () => clearTimeout(id)
  }, [value, delay])
  return v
}
```

### B4. Screen rewrite — `src/pages/superadmin/vehicles/VehList.js` (EDIT)

Concrete changes:

- Import `useLazySearch_sadmin_veh_mstsQuery` and `useDebouncedValue`.
- Keep `search` state. Add `const debouncedQ = useDebouncedValue(search, 300);`
- Effect on `debouncedQ`: when non-empty, call the search trigger with
  `{ q: debouncedQ, page: 1 }`. Save the returned promise and call
  `promise.abort()` on the next change so stale responses don't override
  fresh ones.
- Mode switch: when `debouncedQ` is non-empty, drive the list (and
  pagination) from `searchData`; when empty, fall back to the existing
  `vehData` (browse mode).
- Remove the client-side `.filter(...)` inside the existing `vehicles`
  `useMemo` (lines 39-44) — the server now decides the result set.
- "Load More" button: in search mode, calls the search trigger with
  the next page; in browse mode, keeps the current
  `fetch_sadmin_veh_msts` call.
- Replace the no-op `<Button variant="outline-primary">Search</Button>`
  with a clear-`X` button when `search` is non-empty (or just remove it
  — debounce makes it redundant).
- Show `<Spinner>` inline in the search `InputGroup` while
  `isSearchFetching && debouncedQ`.

### B5. (Optional) Highlight matched substring

Wrap matched chars in `<mark>` inside the `veh_reg_no` cell (line 155).
Skip if not needed for v1.

---

## C. Deployment / rollout

1. Merge backend behind `ATLAS_SEARCH=false` first → search hits the
   fallback regex path, identical UX, lets you ship the frontend without
   waiting on Atlas.
2. Create the `veh_search` index in Atlas (staging cluster first; M10+
   tier required — verify before promising the feature).
3. Flip `ATLAS_SEARCH=true` in staging, smoke-test typo tolerance
   (`KA01AB123` finds `KA01AB1234`).
4. Promote to prod.

---

## D. File index

| Repo            | File                                                        | Action                                   |
| --------------- | ----------------------------------------------------------- | ---------------------------------------- |
| `dzzlo_oms_api` | `api_v3/services/_search/buildSearchStage.js`               | NEW                                      |
| `dzzlo_oms_api` | `api_v3/helpers/searchRateLimit.js`                         | NEW                                      |
| `dzzlo_oms_api` | `api_v3/services/veh_msts.js`                               | EDIT — add `searchVehicles`              |
| `dzzlo_oms_api` | `api_v3/services/veh_trns.js`                               | EDIT — extract `enrichVehiclesWithTrn`   |
| `dzzlo_oms_api` | `api_v3/controllers/sadmin/veh_msts.js`                     | NEW — `SearchAllVehicles`                |
| `dzzlo_oms_api` | `api_v3/routes/sadmin/index.js`                             | EDIT — mount `/search/vehicles`          |
| `dzzlo_oms_api` | `scripts/search/veh_search.json` + `createSearchIndexes.js` | NEW (optional)                           |
| `dzzlo_oms_api` | `models/veh_msts.js`                                        | EDIT — fallback `$text` index            |
| `dzzlo_oms_api` | `test/api_v3/features/sadmin/search_vehicles.test.js`       | NEW                                      |
| `dip-web`       | `src/store/apis/sadmin/veh_msts.js`                         | EDIT — add `search_sadmin_veh_msts`      |
| `dip-web`       | `src/utils/Hooks/useDebouncedValue.js`                      | NEW                                      |
| `dip-web`       | `src/pages/superadmin/vehicles/VehList.js`                  | EDIT — debounced search + dual-mode list |

---

## E. Effort

| Slice                                             | Days                   |
| ------------------------------------------------- | ---------------------- |
| Backend helpers + service + route + test          | 1.5                    |
| Atlas index + env wiring + smoke test             | 0.5                    |
| Frontend endpoint + debounce hook + screen wiring | 0.5                    |
| **Total**                                         | **~2.5 engineer-days** |

Add ~0.5 day buffer for Atlas tier verification (Search requires M10+)
and index backfill wait time.

---

## F. Suggested rollout order

1. **Frontend-only against fallback** — ship A1-A5 + A8 (regex path) and
   B1-B4. Demo immediately, no Atlas dependency.
2. **Atlas index** — A6 + flip env var in staging.
3. **Polish** — A7 fallback text index (if you keep tests on memory
   server) and B5 highlighting.
