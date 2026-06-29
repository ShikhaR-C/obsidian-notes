# Caching

> Start with zero-infrastructure in-process caching. Redis comes later when justified.
> Each task builds on the previous but can be tested independently.

---

## CACHE-1: Cache `getUserFromToken()` with in-process Map (API)

**Size:** S (30 min)
**File:** `helpers/auth.js`
**Install:** None — uses plain `Map` with TTL, no new package needed. (CACHE-2 uses `lru-cache` instead; see "Why `Map` here, not `lru-cache`" below for the rationale.)

**What:** Add an in-process cache keyed by user ID (from JWT) with a 3-minute TTL.

```js
const userCache = new Map();
const CACHE_TTL = 3 * 60 * 1000; // 3 minutes

const getCached = (key) => {
  const entry = userCache.get(key);
  if (!entry) return undefined;
  if (Date.now() > entry.exp) {
    userCache.delete(key);
    return undefined;
  }
  return entry.val;
};
const setCached = (key, val) =>
  userCache.set(key, { val, exp: Date.now() + CACHE_TTL });

exports.getUserFromToken = async (header) => {
  // ... decode JWT ...
  const cached = getCached(jwtData.id);
  if (cached) return cached;

  const user = await User.findOne({ _id: jwtData.id }).lean();
  if (user) setCached(jwtData.id, user);
  return user;
};
```

**Why:** This is the **single highest-impact caching change**. `getUserFromToken()` runs on EVERY request (logging middleware + company status check). That's ~5,000-10,000 DB queries/day just for logging. With a 3-min TTL, ~95% become cache hits.

**How to verify:**

- API: All endpoints should work identically. Add a console.log on cache hit/miss to verify.
- App: No change needed. Same responses.

**Discussion:** Key by user ID (from decoded JWT), not the raw token string. Multiple tokens for the same user share the cache entry. The 3-min TTL (Time To Live — each entry auto-expires after 3 minutes) means if a user's role changes, it takes at most 3 minutes for the logging middleware to see the update. Since this is just for logging (not authorization), that's completely acceptable.

**Why `Map` here, not `lru-cache`.** CACHE-2 uses `lru-cache` with a byte-based ceiling because its values are heterogeneous response bodies (50 KB–2 MB) and its key space is per-tenant × per-endpoint × per-query-variation, which can blow up. CACHE-1 has the opposite profile on every axis, so plain `Map` is not just acceptable — it's the right call:

| Property                | CACHE-1 (`userCache`)                   | Why plain `Map` works                                                     |
| ----------------------- | --------------------------------------- | ------------------------------------------------------------------------- |
| Key shape               | User ID (24-byte ObjectId)              | Fixed, no query-string explosion, no tenant multiplication                |
| Key space               | Concurrent active users in 3-min window | Self-limiting to business size; TTL handles eviction                      |
| Value size              | Lean user doc, ~500 B–2 KB              | Homogeneous — no "one giant entry eats the cache" risk                    |
| Worst case at 10× scale | 10K users × 2 KB ≈ **~20 MB**           | Well under heap headroom — no ceiling needed                              |
| Attack surface          | No user input in key                    | Can't be poisoned with `?cachebust=X` — the key comes from a verified JWT |

With the 3-min TTL, the Map size tracks concurrent active users and naturally shrinks during quiet periods. `lru-cache` would add a dependency and runtime overhead to enforce a ceiling that isn't needed.

**When to reconsider.** If concurrent active users ever exceed ~10,000 in a 3-minute window (i.e., the Map grows past ~20–30 MB), switch to `lru-cache` with the same `maxSize` pattern CACHE-2 uses. Monitor `userCache.size` via CACHE-3 to catch this early.

**Load balancer note.** With multiple servers, each server gets its own independent in-memory cache. Per-server hit rate drops from ~95% to ~80–90% but still eliminates the majority of redundant DB calls. This is a security advantage over Redis: no external attack surface, no port to secure. Upgrade to Redis (CACHE-5) only when you need shared cache across PM2 workers, not for memory reasons.

---

## CACHE-2: Add in-process cache for reference data GET endpoints (API)

**Size:** S (30 min)
**Files:** New `helpers/cacheMiddleware.js`, route files for all cached collections (see list below)
**Install:** `yarn add lru-cache` — needed for the response-body cache. See rationale below for why plain `Map` is insufficient here even though CACHE-1 uses one.

**What:** Create a simple Express middleware that caches GET responses in an `LRUCache` with a hard byte-based memory ceiling. **All responses in this project are company-scoped**, so the cache key MUST include `co_id` from the authenticated user to prevent cross-tenant data leaks:

```js
const { LRUCache } = require("lru-cache");

const refDataCache = new LRUCache({
  // Primary ceiling: bytes. Self-balances across mixed response sizes —
  // many small entries OR a few large ones, never more than 50 MB total.
  maxSize: 50 * 1024 * 1024,
  sizeCalculation: (val) => JSON.stringify(val).length,

  // Belt-and-suspenders: absolute entry-count cap. Catches the pathological
  // case of millions of tiny entries (which `maxSize` would happily accept).
  // 10,000 entries comfortably covers N companies × ~30 endpoint variations.
  max: 10000,

  ttl: 10 * 60 * 1000, // default TTL — overridable per-entry on set()
  allowStale: false,
  updateAgeOnGet: false,
});

// Lightweight hit/miss counters surfaced by CACHE-3's stats endpoint.
refDataCache.stats = { hits: 0, misses: 0 };

const cacheMiddleware =
  (ttlSeconds = 300) =>
  (req, res, next) => {
    if (req.method !== "GET") return next();

    // SECURITY: fail closed. Without a co_id we do not cache at all —
    // prevents any shared "anon:" bucket that would mix tenants.
    const coId = req.loggedInUser?.co_id;
    if (!coId) return next();

    const key = `${coId}:${req.originalUrl}`;
    const cached = refDataCache.get(key);
    if (cached !== undefined) {
      refDataCache.stats.hits++;
      return res.status(200).json(cached);
    }
    refDataCache.stats.misses++;

    const originalJson = res.json.bind(res);
    res.json = (body) => {
      if (res.statusCode === 200) {
        refDataCache.set(key, body, { ttl: ttlSeconds * 1000 });
      }
      return originalJson(body);
    };
    next();
  };

module.exports = { cacheMiddleware, refDataCache };
```

**Route ordering is critical:** the cache middleware MUST be registered AFTER the auth middleware that sets `req.loggedInUser` (see `helpers/middlewares.js:135`). If it runs first, `co_id` is undefined and every request short-circuits past the cache — or worse, if the fail-closed guard is removed, tenants would share one bucket.

```js
// dzzlo_oms.js attaches logging() globally, which sets req.loggedInUser.
// By the time a route handler runs, req.loggedInUser is already populated.
router.get("/", cacheMiddleware(600), GetMultiple);
```

Apply to rarely-changing, company-scoped collections:

| Collection     | Route                  | TTL    | Rationale                                  |
| -------------- | ---------------------- | ------ | ------------------------------------------ |
| `prod_msts`    | `GET /`                | 10 min | Products change infrequently               |
| `dealer_msts`  | `GET /`                | 30 min | Very stable master data                    |
| `rate_msts`    | `GET /`                | 2 min  | Changes daily; short TTL for freshness     |
| `cust_msts`    | `GET /`                | 5 min  | Customer master — moderate churn           |
| `cust_msts`    | `GET /a/getsister/:id` | 30 min | Sister-company relationships rarely change |
| `dvr_msts`     | `GET /a/withvehicle`   | 10 min | Driver roster is stable                    |
| `dvr_msts`     | `GET /one/withvehicle` | 10 min | Single driver + vehicle lookup             |
| `veh_msts`     | `GET /`                | 15 min | Vehicle master — very stable               |
| `dealer_custs` | `GET /app/dcpsoc`      | 5 min  | Dealer-customer mapping with PSOC          |
| `users`        | `GET /a/company`       | 5 min  | Company user list — semi-stable            |

**Do NOT cache transactional collections** (`order_msts`, `invs`, `voc_msts`, `so_msts`, `pay_trns`, `veh_trns`) — these change with every operation and would serve stale data to the order-taking UI.

**Why:** Reference data like products and dealer info is queried frequently but changes rarely. Even a short TTL eliminates redundant DB queries during bursts (e.g., 10 users loading the same product list within 2 minutes).

**How to verify:**

- API: First request populates cache. Second request (within TTL) is instant. After TTL, data refreshes from DB.
- App: Data should always be correct. At worst, stale by the TTL duration.

**Multi-tenant scoping (critical).** All collections in this project are company-scoped — services filter by `req.loggedInUser.co_id` internally, but `req.originalUrl` does NOT include the company ID. Keying the cache by URL alone would return company A's data to company B. The key MUST be `${co_id}:${originalUrl}`. The fail-closed guard (`if (!coId) return next()`) ensures unauthenticated requests never populate or read the cache, so there is no shared bucket that could leak across tenants. Per-tenant hit rate is still excellent: within one company, the same URL gets hit repeatedly (e.g., 10 users all loading the product list within the TTL window).

**Why `lru-cache` here but plain `Map` in CACHE-1.** The two caches have fundamentally different memory profiles and that drives the choice:

|                     | CACHE-1 (`userCache`)                   | CACHE-2 (`refDataCache`)                            |
| ------------------- | --------------------------------------- | --------------------------------------------------- |
| Key space           | Concurrent active users (self-limiting) | companies × endpoints × query-string variations     |
| Value size          | Lean user object, ~1–2 KB (homogeneous) | Full JSON list response, 50 KB–2 MB (heterogeneous) |
| Worst case at scale | 10K users × 2 KB ≈ **~20 MB**           | 500 companies × 10 endpoints × 50 KB ≈ **~750 MB**  |
| Ceiling needed?     | No — naturally bounded                  | Yes — needs hard cap                                |

CACHE-2's worst case can approach or exceed Node's heap. A plain `Map` would grow unbounded until TTLs expire, and a cachebust-style attack (`?_=<random>`) could OOM the process. `lru-cache` with `maxSize: 50 * 1024 * 1024` enforces a 50 MB byte-based ceiling: when full, least-recently-used entries are evicted in O(1). Hot keys stay, cold keys drop, memory stays constant regardless of traffic. That's exactly what you want for response-body caching and exactly what plain `Map` cannot give you.

CACHE-1 doesn't need this because its key space is naturally bounded by concurrent active users, its values are homogeneous and small, and even at 10× current scale it caps at ~20 MB. If concurrent users ever exceed ~10,000 in a 3-minute window, revisit and apply the same `lru-cache` + `maxSize` pattern.

**Why both `maxSize` AND `max`?** The two ceilings guard against opposite failure modes:

- **`maxSize: 50 MB`** is the primary ceiling. It caps the cache in the unit you actually care about — bytes of heap — and self-balances across mixed response sizes (many small entries OR a few huge ones). This is what a plain `max: N` entry cap cannot give you: with `max: 500` and 2 MB responses you'd accept up to 1 GB; with tiny responses you'd waste 99% of the capacity.
- **`max: 10000`** is a sanity fuse. `maxSize` alone would happily accept millions of tiny entries (each costing tens of bytes but adding up in Map/lru-cache bookkeeping overhead). `max` prevents that pathological case. 10,000 entries covers realistic scale (hundreds of companies × ~30 endpoint-variations each) with headroom.

Whichever ceiling is hit first triggers LRU eviction. In practice `maxSize` will bind for this workload; `max` is cheap insurance.

**Tuning the ceiling.** 50 MB is a conservative starting point. Monitor `calculatedSize` via CACHE-3 and adjust based on real hit rate and memory headroom. If you see constant evictions (hit rate dropping over time), increase to 100 MB. If memory is tight, decrease and accept a lower hit rate.

**Defense-in-depth mitigations for query-string explosion.** Even with LRU, consider:

- Normalize the cache key — strip or whitelist query params instead of using raw `originalUrl` (e.g., drop unknown params so `?cachebust=X` collapses to the canonical key).
- Skip caching requests with suspicious query shapes (e.g., unknown params, very long query strings).

---

## CACHE-3: Add cache stats monitoring endpoint (API)

**Size:** XS (10 min)
**Files:** Route file (e.g., health or admin routes)

**What:** Expose cache hit/miss stats for visibility. The two caches report different fields because they use different backends (plain `Map` for CACHE-1, `lru-cache` for CACHE-2 — see CACHE-2 for the rationale):

```js
const { userCache } = require("./helpers/auth"); // CACHE-1 — plain Map
const { refDataCache } = require("./helpers/cacheMiddleware"); // CACHE-2 — LRUCache

app.get("/admin/cache-stats", (req, res) => {
  const { hits, misses } = refDataCache.stats;
  const total = hits + misses;
  res.json({
    uptime: process.uptime(),

    // CACHE-1: plain Map, bounded naturally by concurrent active users.
    userCache: {
      size: userCache.size,
    },

    // CACHE-2: LRUCache with byte-based ceiling. Rich stats available.
    refDataCache: {
      entries: refDataCache.size,
      bytes: refDataCache.calculatedSize,
      maxBytes: refDataCache.maxSize,
      utilization: refDataCache.maxSize
        ? +(refDataCache.calculatedSize / refDataCache.maxSize).toFixed(3)
        : 0,
      hits,
      misses,
      hitRate: total ? +(hits / total).toFixed(3) : 0,
    },
  });
});
```

**Why:** You can't optimize what you can't measure. This tells you if caching is actually working. The important signals:

- **`refDataCache.hitRate`** — if <50%, TTLs may be too short or key space too large (consider normalizing query params).
- **`refDataCache.utilization`** — if consistently near 1.0, the 50 MB ceiling is too small; expect evictions are hurting hit rate. Raise `maxSize`.
- **`userCache.size`** — should track concurrent active users. If it grows unboundedly (e.g., >50,000), the 3-min TTL isn't keeping pace and CACHE-1 may need to switch to `lru-cache` too.

**How to verify:**

- API: `GET /admin/cache-stats` returns JSON with cache info.
- Hit/miss counters increment as expected across repeated requests.

**Discussion:** Keep this behind auth or restrict to localhost/admin. Don't expose cache internals publicly — `refDataCache.size` leaks rough traffic patterns and the per-tenant key structure. For the same reason, never expose cache keys or values from this endpoint.

---

## CACHE-4: Add ETag support for conditional requests (API)

**Size:** S (30 min)
**File:** New `helpers/etag.js`, `dzzlo_oms.js`

**What:** Middleware that generates an ETag hash of the response body. If the client sends `If-None-Match` with the same ETag, return 304 (Not Modified) with no body.

```js
const crypto = require("crypto");

const etagMiddleware = (req, res, next) => {
  const originalJson = res.json.bind(res);
  res.json = (body) => {
    const etag = `"${crypto.createHash("md5").update(JSON.stringify(body)).digest("hex")}"`;
    res.set("ETag", etag);
    if (req.headers["if-none-match"] === etag) return res.status(304).end();
    return originalJson(body);
  };
  next();
};
```

**Why:** ETags save bandwidth when data hasn't changed. The server still processes the query, but the response body isn't sent over the wire. For a 100KB order list that hasn't changed, the response drops to ~0 bytes. Significant on mobile data.

**How to verify:**

- API: First request returns 200 + ETag header. Second request with `If-None-Match: <etag>` returns 304.
- App: verify a custom baseQuery wrapper is sending `If-None-Match` on refetches and receiving 304 responses (see client-side caveat in Discussion).

**Discussion:** ETags don't reduce server-side work — the query still runs and the full response body is built so it can be hashed. They only reduce bytes on the wire. Combine with CACHE-2 (in-process cache) for server-side savings.

**Client-side caveat (React Native + RTK Query):** `fetchBaseQuery` does NOT automatically handle ETags. RTK Query stores the response body in Redux but ignores the `ETag` header, so every refetch (mount, `keepUnusedDataFor` expiry, tag invalidation, `refetchOnFocus`) goes out without `If-None-Match` and always receives a full 200. React Native's native HTTP cache also won't revalidate unless the server sends `Cache-Control: must-revalidate` alongside the ETag. **Net effect of shipping CACHE-4 as-written on this app: zero bandwidth savings.**

To actually benefit, wrap `rawBaseQuery` in `dzzlo_oms_app/src/store/apis/createApi.js` with a custom baseQuery (~40 lines) that:

1. Keeps an in-memory `Map<cacheKey, etag>` — **store only the ETag, NOT the response data**. Let RTK Query keep owning the data via its Redux cache.
2. On GET: injects `If-None-Match` when an ETag exists for that cache key.
3. On response: reads `meta.response.headers.get('etag')` and stores it against the cache key.
4. On 304: returns the current data from RTK Query's state (via `api.getState()`) so RTK sees a successful result.

**Integration rules (important):**

- Place the wrapper **outside** `baseQueryWithRetry` so retries don't replay with stale ETags and only the final success updates the stored ETag.
- Key the Map by **full URL + query string** (or RTK Query's own cacheKey) — `/orders?status=open` and `?status=closed` must not share an ETag.
- Only apply to `method === 'GET'`. Skip mutations and non-JSON responses (file uploads, images).
- Bound the Map with `lru-cache` or clear it on logout to avoid unbounded growth.
- If RTK evicts data (`keepUnusedDataFor: 300`) but the Map still has the ETag, a 304 would have no data to return — drop the Map entry when RTK evicts, or check state has the entry before sending `If-None-Match`.

**Correctness notes:**

- Tag invalidation still works: when the live response genuinely differs, the hash differs, and the wrapper receives a normal 200 with fresh data. A 304 only happens when the server's current response is byte-identical.
- Redux Persist: RTK cache survives restarts but the in-memory Map does not → first request per endpoint after restart sends no `If-None-Match` and gets a full 200. Not broken, just one wasted round-trip per endpoint per cold start.
- Redux DevTools will show "fulfilled" actions on 304 responses — mildly confusing when debugging.

**Alternative:** Server also sends `Cache-Control: private, must-revalidate` alongside the ETag so the native HTTP cache (NSURLSession / OkHttp) handles revalidation transparently. Less client code, but RTK Query still won't know about 304s, and you lose observability into when revalidation actually helps.

---

## CACHE-5: Redis setup for shared caching (API) — FUTURE

**Size:** M-L (2-4 hours)
**Files:** New `helpers/cache.js` (Redis client), `.env` updates

**When to do this:** When you hit ONE of these triggers:

- 500+ orders/day
- PM2 cluster mode with multiple workers needing shared cache
- Adding BullMQ for background jobs (SMS/email queues)
- Adding a web frontend that needs session store

**What:** Install `ioredis`, create a Redis client, implement `cacheOrFetch()` helper. Replace the in-process LRU cache with Redis for shared-across-instances caching.

**Why:** In-process cache (CACHE-1/2) works great for a single PM2 process. But with cluster mode (multiple workers), each worker has its own cache. Redis provides a single shared cache that all workers use.

**How to verify:**

- API: Same endpoints, same responses. Cache hits now come from Redis instead of in-process memory.
- Check with `redis-cli monitor` to see cache reads/writes.

**Discussion:** Don't add Redis until you actually need it. The in-process cache covers your current scale. Redis adds operational complexity (another service to monitor, another thing that can fail). The learning docs estimate your current scale doesn't justify Redis until ~1,000+ orders/day.

---

## Summary

| Task                                       | Size | Impact                              | Infrastructure   |
| ------------------------------------------ | ---- | ----------------------------------- | ---------------- |
| CACHE-1: Map cache for `getUserFromToken`  | S    | ~95% fewer auth DB queries          | $0 — no package  |
| CACHE-2: LRU cache for reference data GETs | S    | Fewer DB queries for master data    | $0 — `lru-cache` |
| CACHE-3: Cache stats endpoint              | XS   | Visibility into cache effectiveness | $0               |
| CACHE-4: ETag middleware                   | S    | 30-70% bandwidth savings            | $0               |
| CACHE-5: Redis (future)                    | M-L  | Shared cache for cluster mode       | ~$12-25/month    |

**Recommended order:** CACHE-1 → CACHE-2 → CACHE-3 → CACHE-4 → CACHE-5 (only when needed)
