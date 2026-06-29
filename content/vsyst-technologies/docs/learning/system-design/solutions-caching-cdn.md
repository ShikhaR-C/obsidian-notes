# Solutions: Caching & CDN

> Complete solutions for adding caching layers and CDN to DZZLO-OMS.
> Priority-ordered. Code is copy-paste ready for Node.js/Express.

---

## Priority Summary

| #   | Solution                                  | Effort  | Cost/month | Impact                                     |
| --- | ----------------------------------------- | ------- | ---------- | ------------------------------------------ |
| 1   | Cache getUserFromToken() with lru-cache   | 30 min  | $0         | ~95% fewer auth DB queries                 |
| 2   | Share loggedInUser across middleware      | 10 min  | $0         | Eliminate duplicate DB calls               |
| 3   | Add .lean() to all read queries           | 1 hour  | $0         | 3-5x faster query results                  |
| 4   | CloudFront in front of ALB (pass-through) | 2 hours | ~$0.29     | DDoS protection, HTTP/2+3, compression     |
| 5   | Origin verification (custom header)       | 30 min  | $0         | Prevent ALB bypass                         |
| 6   | Cache-aside on reference data             | 2 hours | $0         | Fewer DB queries for prod/rate/dealer data |
| 7   | Cache monitoring endpoint                 | 30 min  | $0         | Visibility into cache effectiveness        |
| 8   | Cache-Control headers for CloudFront      | 1 hour  | $0         | CDN caches reference data GETs             |
| 9   | Add Redis (when scaling)                  | 2 hours | $8-15      | Shared cache, rate limiting, job queue     |

---

## Solution 1: Cache getUserFromToken() — THE BIGGEST WIN

**Problem:** `helpers/middlewares.js:123` calls `getUserFromToken()` on EVERY request. This does `jwt.verify()` + `User.findOne()` — a DB round-trip just for logging. Then `check_user_company_status()` calls it AGAIN.

**Impact:** ~5,000-10,000 unnecessary User.findOne() queries/day eliminated.

```javascript
// helpers/auth.js — MODIFIED
const jwt = require("jsonwebtoken");
const User = require("../models/users");
const { LRUCache } = require("lru-cache");

// Cache: JWT token → user object (max 200 users, 3-min TTL)
const userTokenCache = new LRUCache({
  max: 200,
  ttl: 3 * 60 * 1000,
});

module.exports.getUserFromToken = async (header) => {
  try {
    const ath = header.authorization || "";
    const tkn = ath && ath.startsWith("Bearer") ? ath.split("Bearer ")[1] : "";
    if (!tkn) return null;

    // Cache hit — skip DB entirely
    const cached = userTokenCache.get(tkn);
    if (cached) return cached;

    // Cache miss — verify + DB lookup
    const jwtData = jwt.verify(tkn, process.env.JWT_SECRET);
    const userDB = await User.findOne({ _id: jwtData.id })
      .select(
        "-resetPasswordToken -resetPasswordExpire -OTP_Value -OTP_Expire -__v",
      )
      .lean();

    if (!userDB) return null;

    const result = { ...userDB, iat: jwtData.iat, exp: jwtData.exp };
    userTokenCache.set(tkn, result);
    return result;
  } catch (err) {
    return null;
  }
};

// Invalidate when user profile changes
module.exports.invalidateUserById = (userId) => {
  for (const [key, value] of userTokenCache.entries()) {
    if (value && String(value._id) === String(userId)) {
      userTokenCache.delete(key);
    }
  }
};
```

Install: `npm install lru-cache`

---

## Solution 2: Share loggedInUser Across Middleware

```javascript
// helpers/middlewares.js — MODIFIED

exports.logging = () => async (req, res, next) => {
  const loggedInUser = await getUserFromToken(req.headers);
  req.loggedInUser = loggedInUser; // Attach for downstream use
  // ... rest of logging code ...
  next();
};

exports.check_user_company_status = () => async (req, res, next) => {
  // Reuse instead of re-fetching
  const loggedInUser =
    req.loggedInUser || (await getUserFromToken(req.headers));
  // ... rest of code unchanged ...
};
```

---

## Solution 3: Add .lean() to All Read Queries

Mongoose `.lean()` returns plain JS objects instead of Mongoose documents — 3-5x faster:

```javascript
// BEFORE
const products = await ProdMaster.find(JSON.parse(queryStr));

// AFTER
const products = await ProdMaster.find(JSON.parse(queryStr)).lean();
```

Add `.lean()` to every `find()`, `findOne()`, `findById()` that doesn't need `.save()` or other document methods. Search your controllers for these patterns and add `.lean()`.

---

## Solution 4: CloudFront in Front of ALB

Even as pure pass-through (no caching), CloudFront gives you:

- **Free DDoS protection** (AWS Shield Standard)
- **HTTP/2 and HTTP/3** support (faster mobile)
- **Brotli compression** (20-30% smaller JSON responses)
- **Edge TLS termination** (faster handshakes for Indian users)
- **5 edge locations in India** (Mumbai, Delhi, Bangalore, Hyderabad, Chennai)

**Cost:** ~$0.29/month at 5K requests/day. Free during AWS free tier year.

### Setup

1. AWS Console → CloudFront → Create Distribution
2. Origin: your ALB DNS name
3. Protocol: HTTPS Only
4. Add custom header: `X-CF-Origin-Verify: <random-secret>`
5. Enable Origin Shield: ap-south-1
6. Default cache behavior: CachingDisabled (pass-through)
7. Allowed methods: ALL (GET, POST, PUT, DELETE, etc.)
8. Alternate domain: `doms.vsyst.in`
9. SSL: Request ACM cert in us-east-1
10. Update DNS CNAME to CloudFront distribution

---

## Solution 5: Origin Verification

Prevent attackers from bypassing CloudFront and hitting ALB directly:

```javascript
// helpers/cfOriginVerify.js
const cfOriginVerify = () => (req, res, next) => {
  if (process.env.NODE_ENV === "development") return next();
  if (req.path === "/healthcheck") return next();

  const cfHeader = req.headers["x-cf-origin-verify"];
  if (cfHeader !== process.env.CF_ORIGIN_SECRET) {
    return res.status(403).json({ error: "Direct access forbidden" });
  }
  next();
};
module.exports = cfOriginVerify;
```

Also restrict ALB security group to CloudFront IPs only using AWS managed prefix list.

---

## Solution 6: Cache-Aside for Reference Data

```javascript
// helpers/cache.js
const { LRUCache } = require("lru-cache");

let stats = { hits: 0, misses: 0 };

const refDataCache = new LRUCache({
  max: 500,
  ttl: 5 * 60 * 1000, // 5 min default
});

const originalGet = refDataCache.get.bind(refDataCache);
refDataCache.get = function (key) {
  const result = originalGet(key);
  result !== undefined ? stats.hits++ : stats.misses++;
  return result;
};

const getCacheStats = () => {
  const total = stats.hits + stats.misses;
  return {
    hits: stats.hits,
    misses: stats.misses,
    hitRate: total > 0 ? ((stats.hits / total) * 100).toFixed(1) + "%" : "N/A",
    size: refDataCache.size,
    maxSize: refDataCache.max,
  };
};

module.exports = { refDataCache, getCacheStats };
```

```javascript
// Express middleware for cacheable GET endpoints
// helpers/cacheMiddleware.js
const { refDataCache } = require("./cache");

const cacheMiddleware =
  (ttlSeconds = 300) =>
  (req, res, next) => {
    if (req.method !== "GET") return next();
    const key = req.originalUrl;
    const cached = refDataCache.get(key);
    if (cached) return res.status(200).json(cached);

    const originalJson = res.json.bind(res);
    res.json = (body) => {
      if (res.statusCode === 200)
        refDataCache.set(key, body, { ttl: ttlSeconds * 1000 });
      return originalJson(body);
    };
    next();
  };
module.exports = cacheMiddleware;
```

**Apply to routes:**

```javascript
const cacheMiddleware = require("../../helpers/cacheMiddleware");
router.get("/", cacheMiddleware(600), controller.GetMultiple); // 10 min cache
```

**Which collections to cache:**

| Collection   | TTL          | Worth It?                 |
| ------------ | ------------ | ------------------------- |
| prod_msts    | 10 min       | Yes — rarely changes      |
| dealer_msts  | 30 min       | Yes — very stable         |
| rate_msts    | 2 min        | Yes — changes daily       |
| dealer_custs | 10 min       | Yes — terms change rarely |
| order_msts   | Never        | No — constantly changing  |
| invs         | Never (list) | No — frequently created   |

---

## Solution 7: Cache Monitoring

```javascript
// Add to admin routes
const { getCacheStats } = require("./helpers/cache");

app.get("/admin/cache-stats", (req, res) => {
  res.json({ uptime: process.uptime(), cache: getCacheStats() });
});

// Log stats every 5 min
setInterval(
  () => {
    const s = getCacheStats();
    console.log(
      `[Cache] Hit: ${s.hitRate} | ${s.hits}/${s.hits + s.misses} | Size: ${s.size}/${s.maxSize}`,
    );
  },
  5 * 60 * 1000,
);
```

---

## Solution 8: Cache-Control Headers for CloudFront

```javascript
// helpers/cacheHeaders.js
const cacheableResponse =
  (maxAge = 300) =>
  (req, res, next) => {
    if (req.method === "GET") {
      res.set(
        "Cache-Control",
        `public, max-age=${maxAge}, s-maxage=${maxAge}, stale-while-revalidate=60`,
      );
    }
    next();
  };

const noCacheResponse = () => (req, res, next) => {
  res.set("Cache-Control", "no-store, no-cache, must-revalidate, private");
  next();
};

module.exports = { cacheableResponse, noCacheResponse };
```

Apply `noCacheResponse()` to auth routes. Apply `cacheableResponse(300)` to prod_msts, rate_msts GET routes.

---

## Solution 9: Add Redis (When Scaling)

```javascript
// helpers/redisClient.js
const Redis = require("ioredis");

const redis = new Redis({
  host: process.env.REDIS_HOST || "127.0.0.1",
  port: process.env.REDIS_PORT || 6379,
  maxRetriesPerRequest: 3,
  retryStrategy: (times) => Math.min(times * 50, 2000),
});

redis.on("error", (err) => console.error("Redis error:", err.message));
module.exports = redis;
```

**When to add Redis:**

- At 500+ orders/day, OR
- When you add the DIP web app (need session store), OR
- When you enable BullMQ for background jobs, OR
- When cache inconsistency across 2 servers becomes noticeable

**Cost:** t3.micro on EC2 ~$8/month, ElastiCache ~$12/month, Upstash free tier for testing.

---

## Multi-Layer Architecture (Future State)

```
Request
  │
  ▼
CloudFront Edge (India) ── Cache-Control header → cache/pass-through
  │
  ▼
ALB → EC2 (Node.js/Express)
  │
  ├── L1: lru-cache (in-process, ~0ms)
  │     └── getUserFromToken, reference data
  │
  ├── L2: Redis (shared, ~1-2ms) ← add when scaling
  │     └── sessions, rate limiting, job queue, shared cache
  │
  └── L3: MongoDB Atlas (source of truth, ~5-50ms)
```

---

_Total cost of all solutions: ~$0.29/month (CloudFront). Everything else is free npm packages._
