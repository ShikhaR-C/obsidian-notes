# Search Implementation Plan — API (`dzzlo_oms_api`)

Scope: add fast, full-text + field-filter + date-range search for `veh_msts`,
`order_msts`, and `dealer_msts`. All new code lives inside `api_v3/` per the
active dev rule. Prefer MongoDB Atlas Search when the cluster supports it, and
fall back to `$text` / `$regex` compound indexes otherwise.

---

## 1. Existing list / filter patterns (audit)

Relevant files read:

- `dzzlo_oms_api/helpers/advancedResults.js`
  - `renameKeys()` converts `{ gt, gte, lt, lte, in, nin }` -> `$gt, $gte, ...`.
  - `getResults(query, model, populate, isPost)` — the canonical GET helper. Runs
    `find` + `countDocuments` + pagination + `sort`. Used by many endpoints.
  - `calcPagination({ reqpage, reqlimit, total })` — returns
    `{ pagination, startIndex, limit }`.
- `dzzlo_oms_api/api_v3/services/order_msts.js`
  - `getPSOrdersPagination({ query })` (line ~1003) wraps `getResults(query, OrderMaster)`.
  - `getPSOrdersFilter({ body })` (line ~1010) wraps `getResults(restBody, OrderMaster, "", true)` — POST variant for filters.
- `dzzlo_oms_api/api_v3/services/dealer_msts.js`
  - `exports.getMultiple({ query }) => getResults(query, DealerMaster)`.
  - `getDealerPagination` has a hand-rolled `find().skip().limit()` path.
- `dzzlo_oms_api/api_v3/services/veh_msts.js`
  - Currently NO list endpoint. Only `createVehicle` / `deleteVehicle`.
- Routes mount at `dzzlo_oms_api/api_v/api3.js` -> `/api/v3/...`.
  - `veh_msts` routes: `dzzlo_oms_api/api_v3/routes/collections/veh_msts.js`
    (only `POST /`, `DELETE /:id`, `GET /a/test`).
  - `order_msts` routes: `.../order_msts.js` — `GET/POST /a/poso` for list.
  - `dealer_msts` routes: `.../dealer_msts.js` — `GET /`, `POST /app/get`.

### Existing indexes (from models)

- `veh_msts` (`dzzlo_oms_api/models/veh_msts.js`):
  - `{ cust_id: 1 }`, `{ veh_reg_no: 1 }`, `timestamps: true`.
  - Fields: `cust_id`, `veh_reg_no`, `route`.
- `order_msts` (`dzzlo_oms_api/models/order_msts.js`):
  - Compound: `{ cust_id, dealer_id, createdAt, order_status, on_dt }`,
    `{ dealer_id, createdAt }`, `{ cust_id, dealer_id, order_status }`,
    `{ dealer_id, cust_id, order_status, createdAt }`, plus singles.
  - Fields of interest: `dealer_id`, `cust_id`, `order_no`, `order_status`,
    `remarks`, `on_dt`, `createdAt`, `veh_id`, `products[].prod_name`.
- `dealer_msts` (`dzzlo_oms_api/models/dealer_msts.js`):
  - `dealer_name` (unique), `dealer_email` (unique). No explicit text index.
  - Fields of interest: `dealer_name`, `dealer_code`, `dealer_address`, `city`,
    `state`, `district`, `locality`, `pin_code`, `dealer_phone`,
    `dealer_coords` (GeoJSON Point).

### Dependencies already in repo (`dzzlo_oms_api/package.json`)

- `express ^5.2.1`, `mongoose ^9.4.1`, `mongodb ^7.1.1`
- `mongo-sanitize ^1.1.0`
- `express-rate-limit` (see `dzzlo_oms.js` line 19)
- `jest`, `mongodb-memory-server ^11.0.1`

---

## 2. Atlas Search index definitions

Create three Atlas Search indexes via the Atlas UI (Database -> Search ->
Create Index -> JSON editor) or via `mongosh` `createSearchIndex`. Use
`dynamic: false` with explicit field mapping so we stay in control of
facet/filter behavior.

### 2.1 `veh_msts` — index name: `veh_search`

```json
{
  "name": "veh_search",
  "mappings": {
    "dynamic": false,
    "fields": {
      "veh_reg_no": [
        {
          "type": "autocomplete",
          "tokenization": "edgeGram",
          "minGrams": 2,
          "maxGrams": 12,
          "foldDiacritics": true
        },
        { "type": "string", "analyzer": "lucene.keyword" }
      ],
      "route": { "type": "string", "analyzer": "lucene.standard" },
      "cust_id": { "type": "objectId" },
      "createdAt": { "type": "date" }
    }
  }
}
```

Rationale:

- Vehicle numbers are short, high-signal. `autocomplete` gives instant
  type-as-you-go. A parallel `lucene.keyword` mapping supports exact
  equality search.
- `cust_id` is indexed as `objectId` so it can be used inside the same
  `$search` stage via `compound.filter` — no `$match` hop.

### 2.2 `order_msts` — index name: `order_search`

```json
{
  "name": "order_search",
  "mappings": {
    "dynamic": false,
    "fields": {
      "remarks": { "type": "string", "analyzer": "lucene.standard" },
      "order_no": { "type": "number" },
      "order_status": { "type": "token", "normalizer": "lowercase" },
      "dealer_id": { "type": "objectId" },
      "cust_id": { "type": "objectId" },
      "veh_id": { "type": "objectId" },
      "on_dt": { "type": "date" },
      "createdAt": { "type": "date" },
      "products": {
        "type": "document",
        "dynamic": false,
        "fields": {
          "prod_name": { "type": "string", "analyzer": "lucene.standard" }
        }
      }
    }
  }
}
```

### 2.3 `dealer_msts` — index name: `dealer_search`

```json
{
  "name": "dealer_search",
  "mappings": {
    "dynamic": false,
    "fields": {
      "dealer_name": [
        {
          "type": "autocomplete",
          "tokenization": "edgeGram",
          "minGrams": 2,
          "maxGrams": 15,
          "foldDiacritics": true
        },
        { "type": "string", "analyzer": "lucene.standard" }
      ],
      "dealer_code": { "type": "string", "analyzer": "lucene.keyword" },
      "dealer_address": { "type": "string", "analyzer": "lucene.standard" },
      "locality": { "type": "string", "analyzer": "lucene.standard" },
      "city": { "type": "token", "normalizer": "lowercase" },
      "district": { "type": "token", "normalizer": "lowercase" },
      "state": { "type": "token", "normalizer": "lowercase" },
      "pin_code": { "type": "string", "analyzer": "lucene.keyword" },
      "dealer_verified": { "type": "boolean" },
      "createdAt": { "type": "date" }
    }
  }
}
```

---

## 3. Route additions

### 3.1 Edit `dzzlo_oms_api/api_v3/routes/collections/veh_msts.js`

```js
const {
  CreateVehicle,
  DeleteVehicle,
  SearchVehicles,
  sayHI,
} = require("../../controllers/collections/veh_msts");
const { searchLimiter } = require("../../../helpers/searchRateLimit");

router.get("/search", searchLimiter, SearchVehicles);
```

### 3.2 Edit `dzzlo_oms_api/api_v3/routes/collections/order_msts.js`

```js
const { SearchOrders } = require("../../controllers/collections/order_msts");
router.get("/search", searchLimiter, SearchOrders);
```

### 3.3 Edit `dzzlo_oms_api/api_v3/routes/collections/dealer_msts.js`

```js
const { SearchDealers } = require("../../controllers/collections/dealer_msts");
router.get("/search", searchLimiter, SearchDealers);
```

Final endpoints (after `api_v/api3.js` prefixes with `/api/v3`):

- `GET /api/v3/veh_msts/search?q=&cust_id=&from=&to=&limit=&page=`
- `GET /api/v3/order_msts/search?q=&status=&from=&to=&dealer_id=&cust_id=&limit=&page=`
- `GET /api/v3/dealer_msts/search?q=&city=&state=&verified=&limit=&page=`

### 3.4 Create `dzzlo_oms_api/helpers/searchRateLimit.js`

```js
const rateLimit = require("express-rate-limit");

exports.searchLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 60, // 60 searches / minute / IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { success: false, error: "Too many searches, slow down." },
});
```

---

## 4. Controller methods

### 4.1 Edit `dzzlo_oms_api/api_v3/controllers/collections/veh_msts.js`

```js
const asyncHandler = require("../../../helpers/async");
const {
  sayHI: svcSayHI,
  createVehicle,
  deleteVehicle,
  searchVehicles,
} = require("../../services/veh_msts");

// ... existing exports ...

exports.SearchVehicles = asyncHandler(async (req, res) => {
  const result = await searchVehicles({ query: req.query });
  res.status(200).json({ success: true, ...result });
});
```

### 4.2 Edit `dzzlo_oms_api/api_v3/controllers/collections/order_msts.js`

```js
const { searchOrders } = require("../../services/order_msts");

exports.SearchOrders = asyncHandler(async (req, res) => {
  const result = await searchOrders({ query: req.query });
  res.status(200).json({ success: true, ...result });
});
```

### 4.3 Edit `dzzlo_oms_api/api_v3/controllers/collections/dealer_msts.js`

```js
const { searchDealers } = require("../../services/dealer_msts");

exports.SearchDealers = asyncHandler(async (req, res) => {
  const result = await searchDealers({ query: req.query });
  res.status(200).json({ success: true, ...result });
});
```

---

## 5. Service methods (aggregation pipelines)

Create `dzzlo_oms_api/api_v3/services/_search/buildSearchStage.js` with a shared
helper. Then add service methods to each existing service file.

### 5.1 `dzzlo_oms_api/api_v3/services/_search/buildSearchStage.js` (new)

```js
const mongoSanitize = require("mongo-sanitize");
const mongoose = require("mongoose");

// Whether Atlas Search is available in this environment.
// Flipped from env var so tests / local Mongo can fall back automatically.
exports.atlasSearchEnabled = () =>
  String(process.env.ATLAS_SEARCH || "").toLowerCase() === "true";

exports.sanitizeQ = (q) => {
  const raw = mongoSanitize(q == null ? "" : String(q));
  return raw.trim().slice(0, 128); // cap length
};

exports.toObjectId = (v) => {
  if (!v) return null;
  try {
    return new mongoose.Types.ObjectId(String(v));
  } catch {
    return null;
  }
};

exports.parseDate = (v) => {
  if (!v) return null;
  const d = new Date(v);
  return Number.isNaN(+d) ? null : d;
};

exports.parsePage = ({ page, limit }) => {
  const p = Math.max(1, parseInt(page, 10) || 1);
  const l = Math.min(50, Math.max(1, parseInt(limit, 10) || 20));
  return { page: p, limit: l, skip: (p - 1) * l };
};

exports.buildFacet = (skip, limit) => ({
  $facet: {
    data: [{ $skip: skip }, { $limit: limit }],
    meta: [{ $count: "total" }],
  },
});

exports.unwrapFacet =
  ({ page, limit }) =>
  (facetResult) => {
    const data = facetResult[0]?.data || [];
    const total = facetResult[0]?.meta?.[0]?.total || 0;
    const pagination = {};
    if (page * limit < total) pagination.next = { page: page + 1, limit };
    if (page > 1) pagination.prev = { page: page - 1, limit };
    return { count: total, pagination, data };
  };
```

### 5.2 Edit `dzzlo_oms_api/api_v3/services/veh_msts.js`

```js
const {
  atlasSearchEnabled,
  sanitizeQ,
  toObjectId,
  parseDate,
  parsePage,
  buildFacet,
  unwrapFacet,
} = require("./_search/buildSearchStage");

exports.searchVehicles = async ({ query }) => {
  const q = sanitizeQ(query.q);
  const cust_id = toObjectId(query.cust_id);
  const from = parseDate(query.from);
  const to = parseDate(query.to);
  const { page, limit, skip } = parsePage(query);

  if (atlasSearchEnabled() && q) {
    const compound = {
      must: [
        {
          autocomplete: {
            query: q,
            path: "veh_reg_no",
            fuzzy: { maxEdits: 1, prefixLength: 2 },
          },
        },
      ],
      should: [{ text: { query: q, path: "route" } }],
      filter: [],
    };
    if (cust_id) {
      compound.filter.push({ equals: { path: "cust_id", value: cust_id } });
    }
    if (from || to) {
      const range = { path: "createdAt" };
      if (from) range.gte = from;
      if (to) range.lte = to;
      compound.filter.push({ range });
    }

    const pipeline = [
      { $search: { index: "veh_search", compound } },
      { $addFields: { score: { $meta: "searchScore" } } },
      { $sort: { score: -1, createdAt: -1 } },
      buildFacet(skip, limit),
    ];
    const out = await VehicleMaster.aggregate(pipeline);
    return unwrapFacet({ page, limit })(out);
  }

  // Fallback: regex + field filter
  const match = {};
  if (q) {
    const safe = q.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
    match.$or = [
      { veh_reg_no: { $regex: safe, $options: "i" } },
      { route: { $regex: safe, $options: "i" } },
    ];
  }
  if (cust_id) match.cust_id = cust_id;
  if (from || to) {
    match.createdAt = {};
    if (from) match.createdAt.$gte = from;
    if (to) match.createdAt.$lte = to;
  }

  const [total, data] = await Promise.all([
    VehicleMaster.countDocuments(match),
    VehicleMaster.find(match)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .lean(),
  ]);
  const pagination = {};
  if (page * limit < total) pagination.next = { page: page + 1, limit };
  if (page > 1) pagination.prev = { page: page - 1, limit };
  return { count: total, pagination, data };
};
```

### 5.3 Edit `dzzlo_oms_api/api_v3/services/order_msts.js`

Add near `exports.getPSOrdersPagination`:

```js
const {
  atlasSearchEnabled,
  sanitizeQ,
  toObjectId,
  parseDate,
  parsePage,
  buildFacet,
  unwrapFacet,
} = require("./_search/buildSearchStage");

exports.searchOrders = async ({ query }) => {
  const q = sanitizeQ(query.q);
  const dealer_id = toObjectId(query.dealer_id);
  const cust_id = toObjectId(query.cust_id);
  const from = parseDate(query.from);
  const to = parseDate(query.to);
  const statuses = (query.status || "")
    .toString()
    .split(",")
    .map((s) => s.trim().toUpperCase())
    .filter(Boolean);
  const { page, limit, skip } = parsePage(query);

  if (atlasSearchEnabled() && (q || from || to || statuses.length)) {
    const compound = { must: [], should: [], filter: [] };
    if (q) {
      compound.must.push({
        text: {
          query: q,
          path: ["remarks", "products.prod_name"],
          fuzzy: { maxEdits: 1, prefixLength: 2 },
        },
      });
    }
    if (dealer_id) {
      compound.filter.push({ equals: { path: "dealer_id", value: dealer_id } });
    }
    if (cust_id) {
      compound.filter.push({ equals: { path: "cust_id", value: cust_id } });
    }
    if (statuses.length) {
      compound.filter.push({
        in: { path: "order_status", value: statuses },
      });
    }
    if (from || to) {
      const range = { path: "createdAt" };
      if (from) range.gte = from;
      if (to) range.lte = to;
      compound.filter.push({ range });
    }
    const pipeline = [
      { $search: { index: "order_search", compound } },
      { $addFields: { score: { $meta: "searchScore" } } },
      { $sort: { score: -1, createdAt: -1 } },
      buildFacet(skip, limit),
    ];
    const out = await OrderMaster.aggregate(pipeline);
    const res = unwrapFacet({ page, limit })(out);
    const orders = await multipleOrderRes({ orderMst: res.data });
    return { ...res, data: orders };
  }

  // Fallback
  const match = {};
  if (dealer_id) match.dealer_id = dealer_id;
  if (cust_id) match.cust_id = cust_id;
  if (statuses.length) match.order_status = { $in: statuses };
  if (from || to) {
    match.createdAt = {};
    if (from) match.createdAt.$gte = from;
    if (to) match.createdAt.$lte = to;
  }
  if (q) {
    const safe = q.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
    match.$or = [
      { remarks: { $regex: safe, $options: "i" } },
      { "products.prod_name": { $regex: safe, $options: "i" } },
    ];
    const asNum = Number(q);
    if (!Number.isNaN(asNum)) match.$or.push({ order_no: asNum });
  }
  const [total, rawData] = await Promise.all([
    OrderMaster.countDocuments(match),
    OrderMaster.find(match)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .lean(),
  ]);
  const pagination = {};
  if (page * limit < total) pagination.next = { page: page + 1, limit };
  if (page > 1) pagination.prev = { page: page - 1, limit };
  const orders = await multipleOrderRes({ orderMst: rawData });
  return { count: total, pagination, data: orders };
};
```

### 5.4 Edit `dzzlo_oms_api/api_v3/services/dealer_msts.js`

```js
const {
  atlasSearchEnabled,
  sanitizeQ,
  parseDate,
  parsePage,
  buildFacet,
  unwrapFacet,
} = require("./_search/buildSearchStage");

exports.searchDealers = async ({ query }) => {
  const q = sanitizeQ(query.q);
  const city = query.city ? String(query.city).toLowerCase() : null;
  const state = query.state ? String(query.state).toLowerCase() : null;
  const verified =
    typeof query.verified === "undefined"
      ? null
      : String(query.verified) === "true";
  const { page, limit, skip } = parsePage(query);

  if (atlasSearchEnabled() && (q || city || state || verified !== null)) {
    const compound = { should: [], must: [], filter: [] };
    if (q) {
      compound.must.push({
        compound: {
          should: [
            {
              autocomplete: {
                query: q,
                path: "dealer_name",
                fuzzy: { maxEdits: 1, prefixLength: 2 },
                score: { boost: { value: 4 } },
              },
            },
            { text: { query: q, path: "dealer_name" } },
            { text: { query: q, path: ["dealer_address", "locality"] } },
            { text: { query: q, path: "dealer_code" } },
          ],
        },
      });
    }
    if (city) compound.filter.push({ equals: { path: "city", value: city } });
    if (state)
      compound.filter.push({ equals: { path: "state", value: state } });
    if (verified !== null) {
      compound.filter.push({
        equals: { path: "dealer_verified", value: verified },
      });
    }

    const pipeline = [
      { $search: { index: "dealer_search", compound } },
      { $addFields: { score: { $meta: "searchScore" } } },
      { $sort: { score: -1, dealer_name: 1 } },
      buildFacet(skip, limit),
    ];
    const out = await DealerMaster.aggregate(pipeline);
    return unwrapFacet({ page, limit })(out);
  }

  // Fallback
  const match = {};
  if (city) match.city = new RegExp(`^${city}$`, "i");
  if (state) match.state = new RegExp(`^${state}$`, "i");
  if (verified !== null) match.dealer_verified = verified;
  if (q) {
    const safe = q.replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");
    match.$or = [
      { dealer_name: { $regex: safe, $options: "i" } },
      { dealer_code: { $regex: safe, $options: "i" } },
      { dealer_address: { $regex: safe, $options: "i" } },
      { locality: { $regex: safe, $options: "i" } },
    ];
  }
  const [total, data] = await Promise.all([
    DealerMaster.countDocuments(match),
    DealerMaster.find(match)
      .sort({ dealer_name: 1 })
      .skip(skip)
      .limit(limit)
      .lean(),
  ]);
  const pagination = {};
  if (page * limit < total) pagination.next = { page: page + 1, limit };
  if (page > 1) pagination.prev = { page: page - 1, limit };
  return { count: total, pagination, data };
};
```

---

## 6. Fallback compound indexes (when `ATLAS_SEARCH !== "true"`)

Add to each model file (only if missing):

`dzzlo_oms_api/models/veh_msts.js`:

```js
veh_mst_Schema.index({ veh_reg_no: "text", route: "text" });
// already has: { cust_id: 1 }, { veh_reg_no: 1 }
```

`dzzlo_oms_api/models/order_msts.js`:

```js
order_mst_Schema.index({ remarks: "text", "products.prod_name": "text" });
// existing compound { dealer_id, createdAt } already helps dealer+date filter.
```

`dzzlo_oms_api/models/dealer_msts.js`:

```js
dealer_mst_Schema.index({
  dealer_name: "text",
  dealer_code: "text",
  dealer_address: "text",
  locality: "text",
});
dealer_mst_Schema.index({ city: 1 });
dealer_mst_Schema.index({ state: 1 });
```

Note: a collection can only host one `$text` index at a time — keep the one
defined above and add/remove fields via `weights:` rather than creating more.

---

## 7. Validation + sanitization

- `sanitizeQ` in `_search/buildSearchStage.js` runs every `q` through
  `mongo-sanitize` (already in `package.json`) AND caps length at 128 chars.
- `toObjectId` returns `null` for malformed IDs (the filter is skipped, not
  injected).
- `parseDate` rejects NaN dates.
- `parsePage` clamps `limit` to `[1, 50]`.
- Regex escape function used for the fallback path to prevent ReDoS and
  accidental special-char matching.

---

## 8. Rate limiting

`helpers/searchRateLimit.js` exposes `searchLimiter` (60 req/min per IP).
It is mounted only on the three `/search` routes — existing global
`rateLimit` in `dzzlo_oms.js` still applies. For authenticated routes consider
keying on user id:

```js
keyGenerator: (req) => req.user?._id?.toString() || req.ip,
```

---

## 9. Index creation / deploy steps

### Atlas Search (recommended)

1. In Atlas UI -> `dzzlooms` cluster -> Database -> Search -> Create Search Index
   -> JSON Editor. Paste each of the three JSONs from Section 2.
2. Alternatively, one-off script `dzzlo_oms_api/scripts/createSearchIndexes.js`:

   ```js
   // node scripts/createSearchIndexes.js
   require("dotenv").config();
   const mongoose = require("mongoose");

   const indexes = [
     { coll: "veh_msts", def: require("./search/veh_search.json") },
     { coll: "order_msts", def: require("./search/order_search.json") },
     { coll: "dealer_msts", def: require("./search/dealer_search.json") },
   ];

   (async () => {
     await mongoose.connect(process.env.MONGO_URI);
     for (const { coll, def } of indexes) {
       try {
         await mongoose.connection.db.collection(coll).createSearchIndex(def);
         console.log(`Created ${def.name} on ${coll}`);
       } catch (e) {
         console.error(`Failed ${def.name}:`, e.message);
       }
     }
     await mongoose.disconnect();
   })();
   ```

3. Set env var in deploy: `ATLAS_SEARCH=true`.

### Fallback (local / self-hosted)

1. Keep `ATLAS_SEARCH=false`.
2. Run `node scripts/syncIndexes.js` (or let mongoose auto-index on boot)
   — the `.index(...)` declarations in Section 6 take care of it.

---

## 10. Unit test strategy

`mongodb-memory-server` does NOT support Atlas Search (`$search`). Tests must
exercise the fallback path. Strategy:

1. Set `process.env.ATLAS_SEARCH = "false"` in
   `dzzlo_oms_api/test/api_v3/helper/beforeAll/index.js`.
2. Write tests under:
   - `dzzlo_oms_api/test/api_v3/collections/vehs/search.test.js`
   - `dzzlo_oms_api/test/api_v3/collections/order_msts/search.test.js`
   - `dzzlo_oms_api/test/api_v3/collections/dealer_msts/search.test.js`
3. Each test seeds 3–10 documents, then hits the endpoint with `supertest` and
   asserts `data.length` and pagination metadata.
4. For the Atlas path, add a small integration test guarded by
   `describe.skipIf(!process.env.ATLAS_TEST_URI)` that runs against a real
   Atlas test cluster in CI only.
5. Mock helper: `dzzlo_oms_api/test/api_v3/helper/mocks/atlasSearch.js` that
   stubs `VehicleMaster.aggregate` to return a deterministic shape — useful
   for controller-layer tests that don't care about ranking.

Example skeleton (`search.test.js`):

```js
const request = require("supertest");
const app = require("../../../../dzzlo_oms");

describe("GET /api/v3/veh_msts/search", () => {
  it("matches by partial veh_reg_no (fallback regex)", async () => {
    await Veh.create([
      { veh_reg_no: "KA01AB1234", cust_id },
      { veh_reg_no: "KA01CD5678", cust_id },
    ]);
    const res = await request(app)
      .get("/api/v3/veh_msts/search?q=AB12")
      .set("x-api-key", process.env.X_API_KEY_3);
    expect(res.status).toBe(200);
    expect(res.body.data).toHaveLength(1);
    expect(res.body.data[0].veh_reg_no).toBe("KA01AB1234");
  });
});
```

---

## 11. Estimated effort

| Entity                                                | Atlas index | Service + controller                     | Routes | Tests | Total                  |
| ----------------------------------------------------- | ----------- | ---------------------------------------- | ------ | ----- | ---------------------- |
| `veh_msts`                                            | 0.5 d       | 0.5 d                                    | 0.1 d  | 0.5 d | 1.6 d                  |
| `order_msts`                                          | 0.5 d       | 1.0 d (populate + multipleOrderRes glue) | 0.1 d  | 0.5 d | 2.1 d                  |
| `dealer_msts`                                         | 0.5 d       | 0.5 d                                    | 0.1 d  | 0.5 d | 1.6 d                  |
| Shared helpers (`_search/*`, `searchRateLimit`, docs) | —           | 0.5 d                                    | —      | —     | 0.5 d                  |
| **Total**                                             |             |                                          |        |       | **~5.8 engineer-days** |

Add ~1 day buffer for Atlas cluster tier verification (Search requires M10+),
index backfill wait time, and staging smoke tests.

---

## 12. Files to create / edit (quick index)

Create:

- `dzzlo_oms_api/api_v3/services/_search/buildSearchStage.js`
- `dzzlo_oms_api/helpers/searchRateLimit.js`
- `dzzlo_oms_api/scripts/createSearchIndexes.js` (optional)
- `dzzlo_oms_api/scripts/search/veh_search.json`
- `dzzlo_oms_api/scripts/search/order_search.json`
- `dzzlo_oms_api/scripts/search/dealer_search.json`
- `dzzlo_oms_api/test/api_v3/collections/vehs/search.test.js`
- `dzzlo_oms_api/test/api_v3/collections/order_msts/search.test.js`
- `dzzlo_oms_api/test/api_v3/collections/dealer_msts/search.test.js`

Edit:

- `dzzlo_oms_api/api_v3/routes/collections/veh_msts.js`
- `dzzlo_oms_api/api_v3/routes/collections/order_msts.js`
- `dzzlo_oms_api/api_v3/routes/collections/dealer_msts.js`
- `dzzlo_oms_api/api_v3/controllers/collections/veh_msts.js`
- `dzzlo_oms_api/api_v3/controllers/collections/order_msts.js`
- `dzzlo_oms_api/api_v3/controllers/collections/dealer_msts.js`
- `dzzlo_oms_api/api_v3/services/veh_msts.js`
- `dzzlo_oms_api/api_v3/services/order_msts.js`
- `dzzlo_oms_api/api_v3/services/dealer_msts.js`
- `dzzlo_oms_api/models/veh_msts.js` (fallback text index)
- `dzzlo_oms_api/models/order_msts.js` (fallback text index)
- `dzzlo_oms_api/models/dealer_msts.js` (fallback text index)
