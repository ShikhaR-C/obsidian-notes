# Search Implementation Plan — API (`dzzlo_oms_api`)

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Not started: none of the 9 files to create exists and none of the 12 edit targets has search code from this plan (§12) — no `/search` route, Atlas Search index, `_search/buildSearchStage.js`, `helpers/searchRateLimit.js`, `ATLAS_SEARCH` toggle or search test. Search arrived another way — escaped `$regex` on four v3 list endpoints (`7c06b0a`, `2e4fd0d`) and an in-memory `q` in `POST /api/v4/screens/customers` — so the plan should be re-targeted at the v4 read-model pattern (T03-N2 in 00_README); sections: 2 🟡 · 8 ⬜, and the §1 audit re-checked. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

Scope: add fast, full-text + field-filter + date-range search for `veh_msts`,
`order_msts`, and `dealer_msts`. All new code lives inside `api_v3/` per the
active dev rule. Prefer MongoDB Atlas Search when the cluster supports it, and
fall back to `$text` / `$regex` compound indexes otherwise.

---

## 1. Existing list / filter patterns (audit)

**Re-checked (2026-10-01):** still accurate, with moved lines — `getPSOrdersPagination` / `getPSOrdersFilter` are at `api_v3/services/order_msts.js:1085,1092`, and `veh_msts` still has no list route (`api_v3/routes/collections/veh_msts.js:9-11`). New since: escaped `$regex` search on `GET /api/v3/veh_trns/paginated` (`api_v3/services/veh_trns.js:463-468`, with a `$facet` data/meta page at `:511`), the driver list (`dvr_msts.js:419-426`), the user list (`users.js:188-195`) and the sadmin vehicle list (`veh_trns.js:349-355`); `order_msts` gained `v4_dealer_cust_status_ondt` (`models/order_msts.js:82-85`); `express-rate-limit` is imported at `dzzlo_oms.js:19`, but the global limiter is commented out (`:87-95`).

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

**Status (2026-10-01):** ⬜ no search index definition in the repo (no `createSearchIndex`, no `scripts/search/*.json`) and no code queries one (`$search`: 0 hits).

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

**Status (2026-10-01):** ⬜ no `/search` route in any API version; no `helpers/searchRateLimit.js` (3.4) — the per-user limiter that exists covers `/api/v4/screens/*` only (`api_v4/lib/rateLimit.js:30-52`). The security note still applies to v3: its routes apply no `protect` (see `X-SEC-1` in tasks_01).

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

> **SECURITY — authorization is mandatory on these routes.** Mount them behind
> the same auth middleware chain the other `api_v3` routes use (API key + user
> auth), and scope results server-side: `dealer_id` / `cust_id` must be
> **derived from the authenticated user**, never trusted from the query string
> alone. Otherwise an authenticated customer can search every order in the
> database, or pass another customer's id (IDOR / cross-tenant data leak).
> The service sketches in §5 take `user` for exactly this; see also §7.

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

**Status (2026-10-01):** ⬜ no `SearchVehicles` / `SearchOrders` / `SearchDealers` controller exists.

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
  const result = await searchVehicles({ query: req.query, user: req.user });
  res.status(200).json({ success: true, ...result });
});
```

### 4.2 Edit `dzzlo_oms_api/api_v3/controllers/collections/order_msts.js`

```js
const { searchOrders } = require("../../services/order_msts");

exports.SearchOrders = asyncHandler(async (req, res) => {
  const result = await searchOrders({ query: req.query, user: req.user });
  res.status(200).json({ success: true, ...result });
});
```

### 4.3 Edit `dzzlo_oms_api/api_v3/controllers/collections/dealer_msts.js`

```js
const { searchDealers } = require("../../services/dealer_msts");

exports.SearchDealers = asyncHandler(async (req, res) => {
  const result = await searchDealers({ query: req.query, user: req.user });
  res.status(200).json({ success: true, ...result });
});
```

---

## 5. Service methods (aggregation pipelines)

**Status (2026-10-01):** ⬜ no `_search/buildSearchStage.js` and no `search*` service; the nearest shipped code is this plan's fallback shape — an escaped `$regex` `$or` plus a `$facet` data/meta page in `listPaginated` (`api_v3/services/veh_trns.js:463-468,511`) — without the Atlas branch.

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
  // clamp page too — an unbounded page forces a huge $skip scan (cheap DoS)
  const p = Math.min(1000, Math.max(1, parseInt(page, 10) || 1));
  const l = Math.min(50, Math.max(1, parseInt(limit, 10) || 20));
  return { page: p, limit: l, skip: (p - 1) * l };
};

// Escape user input before it reaches a RegExp / $regex — prevents ReDoS and
// wildcard injection. Use for EVERY user-supplied string, not just `q`.
exports.escapeRegex = (s) =>
  String(s).replace(/[-/\\^$*+?.()|[\]{}]/g, "\\$&");

// $search rejects a compound with no usable clauses; drop empty clause arrays
exports.pruneCompound = (compound) => {
  for (const k of Object.keys(compound)) {
    if (Array.isArray(compound[k]) && compound[k].length === 0) {
      delete compound[k];
    }
  }
  return compound;
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
  escapeRegex,
  pruneCompound,
} = require("./_search/buildSearchStage");

exports.searchVehicles = async ({ query, user }) => {
  const q = sanitizeQ(query.q);
  // SECURITY: customers may only search their own vehicles — derive the scope
  // from the authenticated user (adapt role/field names to the project's auth
  // shape); only privileged roles may pass cust_id via the query string.
  const cust_id =
    user?.role === "customer"
      ? toObjectId(user.cust_id)
      : toObjectId(query.cust_id);
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
      { $search: { index: "veh_search", compound: pruneCompound(compound) } },
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
    const safe = escapeRegex(q);
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
  escapeRegex,
  pruneCompound,
} = require("./_search/buildSearchStage");

exports.searchOrders = async ({ query, user }) => {
  const q = sanitizeQ(query.q);
  // SECURITY: force tenant scope from the authenticated user — never trust
  // dealer_id / cust_id from the query string alone (IDOR). Adapt role/field
  // names to the project's auth shape.
  const dealer_id =
    user?.role === "dealer"
      ? toObjectId(user.co_id)
      : toObjectId(query.dealer_id);
  const cust_id =
    user?.role === "customer"
      ? toObjectId(user.cust_id)
      : toObjectId(query.cust_id);
  const from = parseDate(query.from);
  const to = parseDate(query.to);
  // DB stores statuses UPPERCASE (used by the fallback $in); the Atlas token
  // index normalizes to lowercase, so the Atlas filter lowercases them below.
  const statuses = (query.status || "")
    .toString()
    .split(",")
    .map((s) => s.trim().toUpperCase())
    .filter(Boolean);
  const { page, limit, skip } = parsePage(query);

  if (atlasSearchEnabled() && (q || from || to || statuses.length)) {
    const compound = { must: [], should: [], filter: [] };
    if (q) {
      const textClause = {
        text: {
          query: q,
          path: ["remarks", "products.prod_name"],
          fuzzy: { maxEdits: 1, prefixLength: 2 },
        },
      };
      const asNum = Number(q);
      if (!Number.isNaN(asNum)) {
        // numeric q: match order_no exactly OR free text — mirrors the
        // fallback path (text alone can't match the number-typed order_no)
        compound.should.push(textClause, {
          equals: { path: "order_no", value: asNum },
        });
        compound.minimumShouldMatch = 1;
      } else {
        compound.must.push(textClause);
      }
    }
    if (dealer_id) {
      compound.filter.push({ equals: { path: "dealer_id", value: dealer_id } });
    }
    if (cust_id) {
      compound.filter.push({ equals: { path: "cust_id", value: cust_id } });
    }
    if (statuses.length) {
      compound.filter.push({
        // the token index normalizes to lowercase — query values must match
        // the stored (normalized) form, or the filter returns zero results
        in: { path: "order_status", value: statuses.map((s) => s.toLowerCase()) },
      });
    }
    if (from || to) {
      const range = { path: "createdAt" };
      if (from) range.gte = from;
      if (to) range.lte = to;
      compound.filter.push({ range });
    }
    const pipeline = [
      { $search: { index: "order_search", compound: pruneCompound(compound) } },
      { $addFields: { score: { $meta: "searchScore" } } },
      { $sort: { score: -1, createdAt: -1 } },
      buildFacet(skip, limit),
    ];
    const out = await OrderMaster.aggregate(pipeline);
    const res = unwrapFacet({ page, limit })(out);
    // SECURITY: ensure the response shape excludes OTP / token fields on
    // orders (models/order_msts.js carries OTP state — see getOTPToken).
    // Add a $project allowlist to the pipeline or strip inside multipleOrderRes.
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
    const safe = escapeRegex(q);
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
  escapeRegex,
  pruneCompound,
} = require("./_search/buildSearchStage");

exports.searchDealers = async ({ query, user }) => {
  // Dealer directory is visible to any authenticated user — no tenant scope
  // needed, but the route must still sit behind auth (see §3 note).
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
      { $search: { index: "dealer_search", compound: pruneCompound(compound) } },
      { $addFields: { score: { $meta: "searchScore" } } },
      { $sort: { score: -1, dealer_name: 1 } },
      buildFacet(skip, limit),
    ];
    const out = await DealerMaster.aggregate(pipeline);
    return unwrapFacet({ page, limit })(out);
  }

  // Fallback
  const match = {};
  // SECURITY: city/state are user input too — unescaped they allow regex
  // injection (".*" matches everything) and ReDoS patterns
  if (city) match.city = new RegExp(`^${escapeRegex(city)}$`, "i");
  if (state) match.state = new RegExp(`^${escapeRegex(state)}$`, "i");
  if (verified !== null) match.dealer_verified = verified;
  if (q) {
    const safe = escapeRegex(q);
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

## 6. Fallback indexes (when `ATLAS_SEARCH !== "true"`)

**Status (2026-10-01):** ⬜ none of these indexes: `veh_msts` still has only `cust_id` and `veh_reg_no` (`models/veh_msts.js:31-32`); `dealer_msts` has no `city` / `state` index.

The fallback path in §5 searches with **escaped `$regex`** (substring
semantics), not `$text` — so do **not** create `$text` indexes for it: they
would never be queried and would only add write/storage overhead. What the
fallback actually needs are B-tree indexes matching its filters and sorts:

`dzzlo_oms_api/models/veh_msts.js`:

```js
// already has: { cust_id: 1 }, { veh_reg_no: 1 }
veh_mst_Schema.index({ createdAt: -1 }); // fallback sort
```

`dzzlo_oms_api/models/order_msts.js`:

```js
// existing compounds ({ dealer_id, createdAt }, { cust_id, ... }) already
// cover the dealer/cust/status/date filters + sort. No new index required.
```

`dzzlo_oms_api/models/dealer_msts.js`:

```js
dealer_mst_Schema.index({ city: 1 });
dealer_mst_Schema.index({ state: 1 });
// dealer_name already has a unique index (backs the fallback sort)
```

Be aware the unanchored case-insensitive `$regex` `$or` is a **collection
scan** — acceptable for the fallback's intended contexts (local dev,
self-hosted, small datasets), but not a production search path. If a
production deployment can't use Atlas Search, switch the fallback's `q`
branch to `$text` and only then add the text index, e.g. for dealers:

```js
// ONLY if the fallback code is changed to query { $text: { $search: q } }:
dealer_mst_Schema.index(
  { dealer_name: "text", dealer_code: "text", dealer_address: "text", locality: "text" },
  { weights: { dealer_name: 10, dealer_code: 8, dealer_address: 2, locality: 2 } },
);
// remember: max ONE $text index per collection — extend it via weights,
// never by adding a second text index
```

---

## 7. Validation, sanitization + authorization

**Status (2026-10-01):** 🟡 met by the one search in v4 — tenant from the token (`scopeFilter`), `q` limited to 1–60 characters by the house validator (`api_v4/schemas/customers.js:48`), escaped before it becomes a `RegExp` (`api_v4/readmodels/customers.js:72,87`), id keys refused in the body. The v3 list searches escape their input too, but predate the v4 auth, tenant-scoping and input rules — see `X-SEC-1` in tasks_01.

- **Authorization (most important):** all three routes sit behind the existing
  `api_v3` auth middleware, and the services force tenant scope from
  `req.user` (dealer → own `dealer_id`, customer → own `cust_id`).
  Query-string ids are honoured only for privileged roles. Without this,
  search is a cross-tenant IDOR.
- **Response shaping:** order results must exclude OTP / token / internal
  fields (`models/order_msts.js` carries OTP state) — use a `$project`
  allowlist or strip them in `multipleOrderRes`.
- `sanitizeQ` in `_search/buildSearchStage.js` runs every `q` through
  `mongo-sanitize` (already in `package.json`) AND caps length at 128 chars.
  The `String()` casts also neutralise object/array values that Express 5's
  extended query parser can produce (e.g. `?q[$ne]=x`).
- `toObjectId` returns `null` for malformed IDs (the filter is skipped, not
  injected).
- `parseDate` rejects NaN dates.
- `parsePage` clamps `limit` to `[1, 50]` and `page` to `[1, 1000]` (deep
  `$skip` scans are a cheap DoS otherwise).
- `escapeRegex` is applied to **every** user string that reaches a regex —
  `q`, `city`, and `state` — to prevent ReDoS and accidental special-char
  matching.

---

## 8. Rate limiting

**Status (2026-10-01):** 🟡 the v4 screens limiter keys on the user, as suggested here (`api_v4/lib/rateLimit.js:32-36`; 300 a minute, counted per process — see `X-OPS-1` in tasks_01), and covers the Customers search; the v3 list searches have no limiter, and the global one this section relies on does not exist (corrected below).

`helpers/searchRateLimit.js` exposes `searchLimiter` (60 req/min per IP).
It is mounted only on the three `/search` routes — ~~existing global
`rateLimit` in `dzzlo_oms.js` still applies~~ **(2026-10-01: there is no global limiter — it has been commented out since `892c33a`, 2026-04-08, `dzzlo_oms.js:87-95`; see SEC-2 in tasks_01)**. For authenticated routes consider
keying on user id:

```js
keyGenerator: (req) => req.user?._id?.toString() || req.ip,
```

If the API runs behind a load balancer / reverse proxy, per-IP keying only
works when Express's `trust proxy` setting is configured correctly for that
topology — otherwise every client shares the proxy's IP (or can spoof
`X-Forwarded-For`). Verify `app.set("trust proxy", …)` matches the deployment
before relying on the limiter.

---

## 9. Index creation / deploy steps

**Status (2026-10-01):** ⬜ no `scripts/createSearchIndexes.js` and no `ATLAS_SEARCH` env toggle (`.env.example` has none). The index script that does exist, `scripts/perf/atlas-indexes.js`, builds the four v4 B-tree indexes and runs under mongosh (see `X-REL-2` in tasks_01).

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
     await mongoose.connect(process.env.DATABASE_URI); // same env var the app uses (api_constants.js)
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

**Status (2026-10-01):** ⬜ no `search.test.js`; the searches that shipped are tested — the v4 `q` (`test/api_v4/screens/customers.test.js:536-543,889`, `test/api_v4/lib/customersModel.test.js:73-79`) and the v3 lists (`test/api_v3/collections/vehs/veh_trns.test.js`, `test/api_v3/features/sadmin/index.test.js`). The test mongod is now 8.2.1 (`package.json:23-27`) and still has no `$search`.

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

Add ~1 day buffer for Atlas cluster tier verification (Atlas Search itself
works from the free/Flex tiers with index-count limits; dedicated **Search
Nodes** require M10+), index backfill wait time, and staging smoke tests.

---

## 12. Files to create / edit (quick index)

**Status (2026-10-01):** ⬜ none of the 9 files to create exists, and none of the 12 edit targets carries search code from this plan.

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
