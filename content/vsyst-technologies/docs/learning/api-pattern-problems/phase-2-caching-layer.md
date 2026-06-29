# Phase 2: Caching Layer

**Priority:** P1 | **Timeline:** Week 5-6 | **Impact:** 60%+ cache hit rate, <15ms for cached responses

---

## Research: Caching Best Practices for Node.js + MongoDB

### Cache-Aside Pattern (Recommended)

```
1. Check cache → if hit, return cached data
2. If miss, query DB → store in cache with TTL → return data
3. On write, invalidate cache entry
```

### Redis vs In-Memory Cache

| Feature                     | Redis             | node-cache / LRU    |
| --------------------------- | ----------------- | ------------------- |
| Shared across PM2 instances | Yes               | No                  |
| Persistence across restarts | Yes (optional)    | No                  |
| Memory management           | Dedicated process | Shares Node.js heap |
| TTL support                 | Built-in          | Built-in            |
| Scalability                 | Excellent         | Single-process only |

**Decision:** Use Redis (via `ioredis`) -- required for PM2 cluster mode (Phase 7A).

### Cache Invalidation Strategies

1. **TTL-based:** Set expiry; stale data acceptable for a window
2. **Write-through:** Update cache on every write
3. **Event-based:** Invalidate on specific mutations
4. **Hybrid:** TTL + event-based invalidation

---

## Sub-Phase 2A: Redis Setup + User JWT Cache

### Step 2A-1: Install and Configure Redis

**New file:** `helpers/cache.js`

```js
const Redis = require("ioredis");

const redis = new Redis({
  host: process.env.REDIS_HOST || "127.0.0.1",
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || undefined,
  maxRetriesPerRequest: 3,
  retryStrategy(times) {
    if (times > 3) return null; // stop retrying
    return Math.min(times * 200, 2000);
  },
  lazyConnect: true, // don't connect until first command
});

redis.on("error", (err) => console.error("Redis error:", err.message));
redis.on("connect", () => console.log("Redis connected"));

const CACHE_TTL = {
  USER: 300, // 5 minutes
  PRODUCT: 3600, // 1 hour
  RATE: 1800, // 30 minutes
  DEALER: 600, // 10 minutes
  CUSTOMER: 600, // 10 minutes
  DEALER_CUST: 600, // 10 minutes
};

/**
 * Get from cache or fetch from DB
 * @param {string} key - Cache key
 * @param {number} ttl - TTL in seconds
 * @param {Function} fetchFn - Async function to fetch from DB on cache miss
 */
const cacheOrFetch = async (key, ttl, fetchFn) => {
  try {
    const cached = await redis.get(key);
    if (cached) return JSON.parse(cached);
  } catch (err) {
    // Redis failure: fall through to DB
    console.error("Cache read error:", err.message);
  }

  const data = await fetchFn();

  // Fire-and-forget cache set
  redis
    .set(key, JSON.stringify(data), "EX", ttl)
    .catch((err) => console.error("Cache write error:", err.message));

  return data;
};

/**
 * Invalidate cache keys by pattern
 * @param {string} pattern - Redis key pattern (e.g., "user:*")
 */
const invalidatePattern = async (pattern) => {
  const keys = await redis.keys(pattern);
  if (keys.length > 0) await redis.del(...keys);
};

/**
 * Invalidate specific cache key
 */
const invalidate = async (key) => {
  await redis.del(key);
};

module.exports = {
  redis,
  cacheOrFetch,
  invalidate,
  invalidatePattern,
  CACHE_TTL,
};
```

**Dependencies:**

```bash
yarn add ioredis
```

**Environment variables to add to `.env.*`:**

```
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
```

---

### Step 2A-2: Cache User Data from JWT

**Problem:** `getUserFromToken()` in `helpers/auth.js` queries the DB on every request via the `logging()` middleware (line 123) and `check_user_company_status()` middleware (line 48).

**Current code (`helpers/auth.js:17`):**

```js
exports.getUserFromToken = async (headers) => {
  const tkn = headers.authorization?.split(" ")[1];
  if (!tkn) return null;
  const jwtData = jwt.verify(tkn, process.env.JWT_SECRET);
  const user = await User.findOne({ _id: jwtData.id }); // DB call on EVERY request
  return user;
};
```

**Proposed:**

```js
const { cacheOrFetch, invalidate, CACHE_TTL } = require("./cache");

exports.getUserFromToken = async (headers) => {
  const tkn = headers.authorization?.split(" ")[1];
  if (!tkn) return null;

  try {
    const jwtData = jwt.verify(tkn, process.env.JWT_SECRET);
    return await cacheOrFetch(`user:${jwtData.id}`, CACHE_TTL.USER, () =>
      User.findOne({ _id: jwtData.id }).lean(),
    );
  } catch (err) {
    return null;
  }
};

// Call this on user update/logout
exports.invalidateUserCache = async (userId) => {
  await invalidate(`user:${userId}`);
};
```

**Invalidation points:**

- `api_v3/services/users.js` -- on user update
- `api_v3/services/auth.js` -- on logout
- `api_v3/services/auth.js` -- on password change

**Expected Impact:**

- Eliminates 2 DB calls per request (logging middleware + company status check)
- Saves ~10-20ms per API call across ALL endpoints

---

## Sub-Phase 2B: Cache Product & Rate Master Data

### Step 2B-1: Cache Product Masters

**Problem:** `helpers/newProdList.js:10` calls `ProdMst.find({ _id: { $in: prod_ids } })` on every order create/update. Products change very infrequently (daily at most).

**Proposed:**

```js
// In helpers/newProdList.js
const { cacheOrFetch, CACHE_TTL } = require("./cache");

const newProdList = async ({ products }) => {
  const prod_ids = products.map((p) => p.prod_id);

  // Cache all products for this set (keyed by sorted IDs)
  const cacheKey = `prods:${prod_ids.sort().join(",")}`;
  const dbProds = await cacheOrFetch(cacheKey, CACHE_TTL.PRODUCT, () =>
    ProdMst.find({ _id: { $in: prod_ids } }).lean(),
  );

  // ... existing merge logic ...
};
```

**Invalidation:** On product create/update endpoints:

```js
// In api_v3/controllers/collections/prod_msts.js
const { invalidatePattern } = require("../../../helpers/cache");
// After product update:
await invalidatePattern("prods:*");
```

### Step 2B-2: Cache Rate Matrices

**Problem:** `helpers/methods.js` `latestRateFromIST` queries rates per product during order creation.

**Proposed:**

```js
const getRate = async (prod_id, dealer_id) => {
  const cacheKey = `rate:${dealer_id}:${prod_id}`;
  return cacheOrFetch(cacheKey, CACHE_TTL.RATE, () =>
    RateMaster.findOne({
      prod_id,
      dealer_id,
      effective_from: { $lte: new Date() },
    })
      .sort({ effective_from: -1 })
      .lean(),
  );
};
```

**Invalidation:** On rate create/update.

---

## Sub-Phase 2C: Cache Dealer/Customer Reference Data

### Step 2C-1: Cache Dealer Master

```js
const getDealer = async (dealer_id, selectFields) => {
  const cacheKey = `dealer:${dealer_id}`;
  return cacheOrFetch(cacheKey, CACHE_TTL.DEALER, () =>
    DealerMaster.findById(dealer_id).select(selectFields).lean(),
  );
};
```

### Step 2C-2: Cache Customer Master

```js
const getCustomer = async (cust_id, selectFields) => {
  const cacheKey = `cust:${cust_id}`;
  return cacheOrFetch(cacheKey, CACHE_TTL.CUSTOMER, () =>
    CustomerMaster.findById(cust_id).select(selectFields).lean(),
  );
};
```

### Step 2C-3: Cache Dealer-Customer Relation

```js
const getDealerCust = async (dealer_id, cust_id, selectFields) => {
  const cacheKey = `dc:${dealer_id}:${cust_id}`;
  return cacheOrFetch(cacheKey, CACHE_TTL.DEALER_CUST, () =>
    DealerCustomer.findOne({ dealer_id, cust_id }).select(selectFields).lean(),
  );
};
```

**Note:** Balance-related fields in dealer_cust (`cust_bal`, `max_cr_lmt`, `adv_dep`) change with transactions. Use short TTL (5 min) or invalidate after order/voucher mutations.

---

## Sub-Phase 2D: ETags for Conditional Requests

### Research: ETag + If-None-Match

ETags allow the client to send the last-known hash; if unchanged, the server returns 304 with no body, saving bandwidth and serialization.

### Implementation

**New middleware:** `helpers/etag.js`

```js
const crypto = require("crypto");

const generateETag = (data) => {
  return crypto.createHash("md5").update(JSON.stringify(data)).digest("hex");
};

const etagMiddleware = (req, res, next) => {
  const originalJson = res.json.bind(res);

  res.json = (body) => {
    const etag = `"${generateETag(body)}"`;
    res.set("ETag", etag);

    if (req.headers["if-none-match"] === etag) {
      return res.status(304).end();
    }

    return originalJson(body);
  };

  next();
};

module.exports = etagMiddleware;
```

**Usage in `dzzlo_oms.js`:**

```js
const etagMiddleware = require("./helpers/etag");
app.use(etagMiddleware);
```

**Expected Impact:** 30-70% bandwidth savings for unchanged list responses.

---

## Sub-Phase 2E: RTK Query Cache Optimization (App Side)

### Step 2E-1: Add keepUnusedDataFor

**File:** `src/store/apis/createApi.js`

```js
export const api = createApi({
  reducerPath: 'dzzlo-oms-api',
  baseQuery: fetchBaseQuery({ ... }),
  keepUnusedDataFor: 300, // 5 minutes -- keeps cache alive during navigation
  tagTypes: [ ... ],
  endpoints: () => ({}),
});
```

**Impact:** Screens that navigate away and back within 5 minutes use cached data instead of refetching.

### Step 2E-2: Unify GET/POST Cache Tags

**Problem:** `order_msts` has separate tags `order_msts` (GET) and `order_msts_POST` (POST), leading to cache fragmentation.

**Fix:** Use a single tag type and have both variants provide/invalidate the same tags:

```js
// In order_msts.js endpoints
fetch_order_msts_so: builder.query({
  // GET variant
  providesTags: (result) => [
    ...(result?.data?.map(({ _id }) => ({ type: 'orders', id: _id })) || []),
    { type: 'orders', id: 'LIST' },
  ],
}),
fetch_order_so_POST: builder.query({
  // POST variant -- same tags
  providesTags: (result) => [
    ...(result?.data?.map(({ _id }) => ({ type: 'orders', id: _id })) || []),
    { type: 'orders', id: 'LIST' },
  ],
}),
```

### Step 2E-3: Add ETag Support to RTK Query

When the API returns ETags, RTK Query can send `If-None-Match` headers:

```js
prepareHeaders: async (headers, { getState }) => {
  // ... existing auth headers ...
  // ETag support is automatic with fetchBaseQuery when server sends ETag headers
  return headers;
},
```

---

## Cache Architecture Diagram

```
                    ┌─────────────────┐
                    │  React Native   │
                    │   RTK Query     │
                    │  (memory cache) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Express API   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     Redis       │
                    │  (shared cache) │
                    │                 │
                    │ user:{id} (5m)  │
                    │ prod:{ids} (1h) │
                    │ rate:{d}:{p}    │
                    │ dealer:{id}     │
                    │ cust:{id}       │
                    │ dc:{d}:{c}      │
                    └────────┬────────┘
                             │ cache miss
                    ┌────────▼────────┐
                    │   MongoDB Atlas │
                    └─────────────────┘
```

## Verification

1. **Cache hit rate:** `redis.info("stats")` -- monitor `keyspace_hits` / `keyspace_misses`
2. **Memory usage:** `redis.info("memory")` -- ensure < 50MB for this workload
3. **Latency:** Compare p50/p95 before/after caching
4. **Correctness:** Write integration tests that:
   - Verify fresh data on first request
   - Verify cached data on second request (no DB call)
   - Verify cache invalidation on update
   - Verify graceful fallback when Redis is down
