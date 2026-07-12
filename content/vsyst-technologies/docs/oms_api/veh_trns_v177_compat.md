---
name: veh_trns_v177_compat
status: ready
overview: >
  Restore previous-version (v1.77) compatibility for vehicle data after the
  veh_trns pagination feature. Confirmed setup: the released v1.77 app talks to
  the updated API (this feature branch) at /api/v3. The legacy GET /veh_trns
  path (getMultiple) — the only veh_trns list call the v1.77 app makes — must
  always return a clean { success, data, requestCount } and never 500/empty, so
  the old client's unguarded `response.requestCount` read keeps working "as
  before". Scope: api_v3 only (per AI.md); one optional app-side follow-up.
todos:
  - Harden getMultiple against orphaned/missing refs (primary)
  - Validate cust_id in listPaginated + getVehReqCount (defensive)
  - (App, optional) swallow aborts in SelectVehicle (Symptom #1, new build)
  - Runtime-capture the exact v1.77 response, then verify before/after
---

# Problem

Two symptoms, from **two different clients** (confirmed with the user):

1. **Symptom #2 — primary, released v1.77 app.** Vehicles screen first load shows
   **"Cannot read property 'requestCount' of undefined"**. The v1.77 app (commit
   `44656be1`) calls only `GET /api/v3/veh_trns?cust_id=X&showReqCount=true` (via
   `fetch_veh_trns_other`) and reads `response.requestCount` with **no** optional
   chaining (`Customer/Vehicles/index.js:269`). It does **not** call `/paginated` or
   `/req-count` (they did not exist at v1.77). So compatibility must live entirely in the
   legacy `GET /veh_trns` handler — `getMultiple`.
2. **Symptom #1 — secondary, NEW feature-branch app.** `SelectVehicle.js` first
   "load more" shows **"Network error. Please check your connection."** Load-more did not
   exist in v1.77, so this is the new build. The string maps to `FETCH_ERROR`
   (request aborted / no HTTP response) in `store/apis/preloadedState.js`.

User's ask: "create dzzlo_oms_api updates to have v1.77 support as it did before."

# Confirmed facts

- Setup: **old v1.77 app → updated API on `feature/veh-trns-pagination`, `/api/v3`,
  server current/restarted.**
- v1.77 `createApi.js` is **byte-identical** to the current one (same `responseHandler`
  that returns `response.json()`/`response.text()`, same retry, same 10s timeout). So the
  client side did not change — Symptom #2 is entirely about what the server returns.
- v1.77 client read (`@44656be1 Customer/Vehicles/index.js`, lines ~256-271):
  ```js
  const response = await fetch_veh_trns_other({ comp_id: customerId, showReqCount: true }).unwrap()
  const reqCnt = response.requestCount // throws if response is undefined
  setVehReqCnt(reqCnt)
  ```
  When that line throws, it is caught and `errorRTK(err)` returns `err.message`, so the
  literal Hermes string "Cannot read property 'requestCount' of undefined" renders on the
  `<Error>` screen. The current branch already fixed the client side
  (`reqCountRes?.requestCount ?? 0` + a dedicated `/req-count` query) — but that does not
  help the **already-released** v1.77 binary, which is why the fix must be server-side.
- `getMultiple` (`api_v3/services/veh_trns.js`) is **byte-identical** before/after the
  feature, and its `meta.version` gate (`Number(version) <= 1.71` → embed the full vehicle
  object into `veh_id`) is unchanged — so v1.77 gets the same `veh_id` shape it always did.
  **No gate change is needed.**

# Root cause

`getMultiple` is the **only** veh_trns list function still **unguarded** against orphaned /
missing references; its siblings `listPaginated` (`api_v3/services/veh_trns.js:517-531`)
and `getAllVehicles` (`:357-388`) already guard the same spots. Against the dev DB's data,
these unguarded reads make `GET /veh_trns` fail, so the v1.77 client's `response` is not the
clean object it expects:

- `:150` `return \`${vmst.cust_id}\`;`— throws if a`veh_trn.veh_id`has no`veh_mst`.
- `:186` `Customers.find(i => \`${i._id}\` === \`${vmst.cust_id}\`)` — same.
- `:197` `vT.cust_name = cust.cust_name;` — throws if the customer is missing.
- `:205` `vT.veh_reg_no = ... : vmst.veh_reg_no;` — same.

The fix is to make `getMultiple` as defensive as its siblings so the endpoint **always**
returns `200 { success:true, data, requestCount }`.

# Solution / Files to change

## 1. Harden `getMultiple` — `api_v3/services/veh_trns.js` (primary, behavior-preserving)

**a. `customerIdsA` builder** (~lines 146-153) — guard + filter:

```js
const customerIdsA = [
  ...new Set(
    veh_trn.map((a) => {
      const vmst = Vehs.find((vm) => `${vm._id}` === `${a.veh_id}`)
      return vmst ? `${vmst.cust_id}` : null
    }),
  ),
].filter(Boolean)
```

**b. inside the `Promise.all` map** (~lines 185-205) — optional-chain the master/customer:

```js
const vmst = Vehs.find((vm) => `${vm._id}` === `${vT.veh_id}`)
const cust = Customers.find((i) => `${i._id}` === `${vmst?.cust_id}`)
const hirer = Customers.find((i) => `${i._id}` === `${vT.cust_id}`)
// ...
vT.cust_name = cust ? cust.cust_name : ""
// ...
if (!!version && !!isntTestv && !!olderversion && vmst) {
  vT.veh_id = vmst
}
vT.veh_reg_no = vT.veh_reg_no || vmst?.veh_reg_no
```

Healthy data is unaffected; orphaned data no longer 500s. This is exactly the guard
pattern already used in `listPaginated`/`getAllVehicles` — reuse, not new logic.

## 2. Validate `cust_id` — `api_v3/services/veh_trns.js` (defensive; helps the NEW app)

**`listPaginated`** (~line 422, before building the ObjectId/match):

```js
if (!mongoose.isValidObjectId(cust_id)) {
  return { data: [], pagination: { page: pageNum, limit: lim, total: 0, hasMore: false } }
}
const match = { cust_id: new mongoose.Types.ObjectId(cust_id) }
```

**`getVehReqCount`** (~line 400, symmetry):

```js
exports.getVehReqCount = async ({ cust_id }) => {
  if (!mongoose.isValidObjectId(cust_id)) return { requestCount: 0 }
  const requestCount = await VehReq.countDocuments({
    $or: [{ cust_id }, { oth_cust_id: cust_id }],
    req_status: "PENDING",
  })
  return { requestCount }
}
```

A missing/transient company id now yields an empty page / `{ requestCount: 0 }` instead of a
500 (BSONError) the new app would surface as a connection/server error. (`mongoose` is
already imported at the top of the file.)

## 3. (App, optional — Symptom #1, NEW build) `dzzlo_oms_app/.../SelectVehicle.js`

`SelectVehicle` uses the **auto** `useFetch_veh_trns_paginatedQuery` and does NOT suppress
aborts, unlike the Vehicles screens which `.catch(swallowAbort)` (`utils/rtkAbort.js`). The
first load-more abort surfaces as `FETCH_ERROR`. Fix: ignore `AbortError`/`FETCH_ERROR` in
the `isError` effect (~line 116), or migrate to the lazy-query + `swallowAbort` pattern the
Vehicles screens use. Outside the API scope the user named — implement only if wanted.

# Diagnostic (read-only) — confirm the exact trigger

With the API running, capture what the v1.77 request actually returns (needs a real
`cust_id` + auth token) and watch server logs:

```
curl -i 'localhost:8030/api/v3/veh_trns?cust_id=<id>&showReqCount=true' \
  -H 'authorization: Bearer <token>' -H 'x-api-key: <key>' \
  -H 'meta:{"version":"1.77","deviceBrand":"Apple"}'
```

Expect `200 {success:true,data:[...],requestCount:N}`. A 500 / empty / different shape pins
the trigger; change #1 should make it a clean 200.

# Verification

- Find/seed an orphaned `veh_trn` (veh_id → deleted veh_mst); `GET /veh_trns` returns 200
  (not 500) after change #1.
- Old v1.77 build: Vehicles screen loads, request badge shows, no "requestCount" crash.
- `GET /veh_trns/paginated?page=1&limit=15` with no `cust_id` → empty page (not 500) after #2.
- New build: SelectVehicle load-more appends page 2 with no "check your connection";
  Vehicles infinite scroll + search still work.
- `cd dzzlo_oms_api && yarn test --testPathPattern=veh_trns` if a suite exists.

# Notes

- All API edits stay inside `api_v3/` (AI.md compliant). v1.77 uses `/api/v3`, so no
  `api_v2/` change is required.
- Optional follow-up (not required here): the `meta.version` gate uses `Number("1.77")`
  float parsing — fragile for multi-segment versions (e.g. "1.7.10" → NaN). Consider a real
  version comparison if more gated behavior is added later.
