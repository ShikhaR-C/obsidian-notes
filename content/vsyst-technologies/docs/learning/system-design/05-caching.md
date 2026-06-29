# Session 5: Caching

> Phase 3 — Performance | 2 hours | Review: 15 min

## What You'll Learn

- Where caching can happen in a web architecture (client, CDN, application, database) and the trade-offs at each layer
- The four major cache patterns (cache-aside, write-through, write-behind, refresh-ahead) and which ones fit read-heavy reference data
- What Redis and AWS ElastiCache are, what they cost, and when they're actually justified
- How to identify hot data paths in your own system and do an honest cost-benefit analysis before adding any caching infrastructure

## Why This Matters for DZZLO-OMS

Your system has zero caching. Every request hits MongoDB directly — not just for business data, but for infrastructure concerns too. The `logging()` middleware calls `getUserFromToken()` on every single request, which means a JWT decode plus a MongoDB user lookup runs before your route handler even starts. Collections like `dealer_custs` (commercial terms), `rate_msts` (pricing), and `prod_msts` (products) are queried on every order even though they change rarely.

Here's the tension: you're running at ~130 orders/day. That's ~0.002 req/sec. Your MongoDB isn't sweating. Your EC2 instances aren't sweating. Adding Redis or ElastiCache would cost money, add operational complexity (another thing to monitor, another thing that can fail), and create cache invalidation headaches — all to save milliseconds that nobody notices.

But there's one exception. The `getUserFromToken()` DB call in the logging middleware is pure waste. It runs on every request, the data it fetches doesn't change between requests for the same token, and the fix requires zero new infrastructure — just a simple in-process cache with a TTL. That's the kind of caching that's worth it at any scale.

By the end of this session, you'll know exactly which caching patterns exist, why most of them are premature for your system, and which single optimization is actually worth implementing today.

## Hour 1 — Concepts (60 min)

### Step 1: Caching Fundamentals (20 min)

**Read:** [System Design Primer — Cache](https://github.com/donnemartin/system-design-primer#cache)

**Focus on:** the four layers where caching can happen and what each one buys you.

**The four cache layers:**


| Layer           | What It Caches                         | Latency                              | Example                                         |
| --------------- | -------------------------------------- | ------------------------------------ | ----------------------------------------------- |
| **Client**      | HTTP responses, assets                 | 0 ms (no network)                    | Browser cache via `Cache-Control` headers, ETag |
| **CDN**         | Static assets, sometimes API responses | 1-50 ms (edge PoP)                   | CloudFront in front of ALB                      |
| **Application** | Computed results, DB query results     | <1 ms (in-process) or 1-5 ms (Redis) | Node.js `Map` with TTL, Redis                   |
| **Database**    | Query results, index pages             | Managed internally                   | MongoDB WiredTiger cache, query plan cache      |


**Map each layer to DZZLO-OMS:**

- **Client caching:** Your API serves JSON to business clients. You're not setting `Cache-Control` headers on API responses. For an order management system where data changes with every order, client-side caching of API responses is risky — stale order data is worse than a slow response. This layer is mostly irrelevant for you.
- **CDN caching:** You don't serve static assets through your API. If you had a frontend, CloudFront would help there. For API responses, CDN caching is dangerous — the same URL returns different data per user/company. Skip this.
- **Application caching:** This is where the action is. You can cache at two levels:
  - **In-process** (a JavaScript `Map` or `lru-cache` in your Node.js process): Fastest possible, but each EC2 instance has its own cache. With 2 instances behind ALB, they won't share cached data.
  - **External cache** (Redis/ElastiCache): Shared across instances, survives deploys, but adds a network hop and another service to operate.
- **Database caching:** MongoDB's WiredTiger storage engine already caches frequently accessed documents and indexes in memory. This is automatic — you don't manage it. Your MongoDB Atlas instance likely has enough RAM to keep your hot working set entirely in memory already.

**Key insight for your system:** MongoDB is already caching at the database layer. The question is whether application-level caching buys you anything *on top of* that, given your traffic.

### Step 2: Cache Patterns (20 min)

**Read:** [System Design Primer — When to Update the Cache](https://github.com/donnemartin/system-design-primer#when-to-update-the-cache)

**Focus on:** understanding the four patterns and which one matches read-heavy, rarely-changing data like `dealer_custs`.

**The four cache update patterns:**

**1. Cache-Aside (Lazy Loading)**

```
Read: Check cache → miss → read from DB → write to cache → return
Write: Write to DB → invalidate cache (or let it expire via TTL)
```

- **Best for:** Read-heavy data that you can tolerate being slightly stale. This is the most common pattern.
- **Downside:** First request after a miss is always slow (cold start). Cache and DB can drift if invalidation is missed.
- **DZZLO-OMS fit for `dealer_custs`:** Good fit. Commercial terms are read on every order but change rarely. A cache-aside with a 5-minute TTL means at worst you serve terms that are 5 minutes stale — which is fine for pricing/discount data that changes once a month.

**2. Write-Through**

```
Read: Check cache → hit → return (always in cache)
Write: Write to cache → cache writes to DB → return
```

- **Best for:** Data where you can't tolerate any cache misses and writes are infrequent.
- **Downside:** Every write pays the latency of both cache and DB. Cache fills with data that may never be read.
- **DZZLO-OMS fit:** Overkill. Your write volume is tiny and the complexity isn't justified.

**3. Write-Behind (Write-Back)**

```
Read: Check cache → hit → return
Write: Write to cache → return immediately → async write to DB later
```

- **Best for:** Write-heavy systems where you want to batch DB writes.
- **Downside:** Data loss risk — if the cache dies before flushing to DB, writes are lost.
- **DZZLO-OMS fit:** Absolutely not. You can't risk losing order data. This pattern is for things like analytics counters, not financial transactions.

**4. Refresh-Ahead**

```
Cache proactively refreshes entries before they expire, based on predicted access patterns.
```

- **Best for:** Data with predictable access patterns where you want zero-latency reads.
- **Downside:** Complex to implement. Wastes resources refreshing data nobody reads.
- **DZZLO-OMS fit:** Way too complex for your scale. Skip this entirely.

**Bottom line for DZZLO-OMS:** If you ever add caching for `dealer_custs`, `rate_msts`, or `prod_msts`, use **cache-aside with TTL**. It's the simplest, most battle-tested pattern, and it matches your read-heavy, write-rare data perfectly.

### Step 3: Redis Basics and AWS ElastiCache (20 min)

**Read:** [Redis Getting Started](https://redis.io/docs/latest/develop/get-started/) — read just the introduction and overview, not the full tutorial.

**Skim:** [AWS ElastiCache for Redis — Getting Started](https://docs.aws.amazon.com/elasticache/latest/red-ug/GettingStarted.html) — focus on the architecture diagram and pricing, not the setup steps.

**What Redis gives you:**

- An in-memory key-value store with sub-millisecond reads
- Data structures beyond simple key-value: hashes, lists, sets, sorted sets
- Built-in TTL (time-to-live) on keys — set it and forget it
- Pub/sub for cache invalidation across multiple app servers
- Persistence options (RDB snapshots, AOF log) so data survives restarts

**What AWS ElastiCache gives you on top of Redis:**

- Managed infrastructure: AWS handles patching, failover, backups
- Multi-AZ for high availability
- CloudWatch metrics out of the box
- VPC integration (your EC2 instances can reach it on the private network)

**What it costs:**


| Option                       | Monthly Cost (approx) | Effort                            | Shared Across Instances?  |
| ---------------------------- | --------------------- | --------------------------------- | ------------------------- |
| In-process `Map` with TTL    | $0                    | 10 lines of code                  | No (each EC2 has its own) |
| Redis on EC2 (self-managed)  | ~$15-30 (t3.micro)    | Medium (install, monitor, backup) | Yes                       |
| ElastiCache `cache.t3.micro` | ~$12-25               | Low (managed)                     | Yes                       |
| ElastiCache `cache.t3.small` | ~$25-50               | Low (managed)                     | Yes                       |


**The honest question for your system:** Is it worth $15-50/month plus operational overhead to cache data that MongoDB is already serving in single-digit milliseconds? At 130 orders/day, the answer is almost certainly no.

**When it becomes worth it:**

- When you have multiple app servers and need shared state (session store, rate limiting counters)
- When your MongoDB query latency becomes a problem (p99 > 100 ms)
- When you're doing expensive computations that you want to cache (report generation, aggregation pipelines)
- When you grow to ~10,000+ requests/day and want to reduce DB connection pressure

**Write down:** At what order volume would you add Redis? What would be the trigger — latency, cost, or reliability?

## Hour 2 — Applied to Your System (60 min)

### Step 4: Identify Hot Data Paths (20 min)

**Exercise:** Go through your codebase and identify every piece of data that gets fetched repeatedly across requests. For each one, answer: how often does it change, how often is it read, and how bad is it if the cache serves stale data?

**Hot data path analysis for DZZLO-OMS:**


| Data                                     | Read Frequency           | Change Frequency                         | Stale Data Risk                                                                           | Cache Candidate?                       |
| ---------------------------------------- | ------------------------ | ---------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------- |
| **User from token** (`getUserFromToken`) | Every request (~650/day) | Rarely (user profile updates)            | Low — used for logging, not authorization decisions                                       | **Yes — strongest candidate**          |
| `**dealer_custs`** (commercial terms)    | Every order (~130/day)   | Very rarely (monthly updates)            | Low — stale terms for 5 minutes won't cause wrong pricing if rates are checked separately | Maybe — but DB is fast enough          |
| `**rate_msts`** (pricing)                | Every order (~130/day)   | Occasionally (weekly/monthly)            | **Medium** — stale rates could mean wrong prices on orders                                | Maybe — but needs careful invalidation |
| `**prod_msts`** (products)               | Every order (~130/day)   | Rarely (new products added infrequently) | Low — product list doesn't change mid-order                                               | Maybe — but DB is fast enough          |
| **Company/tenant config**                | Every request (~650/day) | Very rarely                              | Low                                                                                       | Maybe — similar to user from token     |


**Key observation:** The only data path that's genuinely wasteful is `getUserFromToken()`. It runs on *every* request (not just order-related ones), it hits MongoDB *just to write a log*, and the data it fetches is stable for the lifetime of a JWT token. Everything else is queried at low enough frequency that MongoDB handles it fine.

### Step 5: Cost-Benefit Analysis (20 min)

**Exercise:** For each caching option, calculate the real cost (money + complexity) vs. the real benefit (latency saved + DB load reduced).

**Option A: Redis on EC2 (self-managed)**

- Cost: ~$15-30/month for a t3.micro + your time to install, configure, monitor, handle failures, patch security updates
- Benefit: Shared cache across both EC2 instances, sub-ms reads
- Complexity: Need to add `ioredis` or `redis` client to your app, handle connection failures gracefully, add health checks, add to your deployment process
- **Verdict at 130 orders/day:** Not worth it. You're adding a third service to monitor and a new failure mode for negligible latency improvement.

**Option B: AWS ElastiCache**

- Cost: ~$12-50/month depending on instance size
- Benefit: Same as Redis but AWS manages it — patches, failover, backups
- Complexity: Still need the client library and application code changes. VPC/security group config needed.
- **Verdict at 130 orders/day:** Not worth it. Same reasoning as Option A but with less operational burden. Save this for when you actually need shared cache.

**Option C: In-process cache (no new infrastructure)**

- Cost: $0/month. ~30 minutes to implement.
- Benefit: Eliminates the MongoDB user lookup from the logging middleware on every request. With a 5-minute TTL, the first request per user per 5 minutes hits MongoDB; the rest get the cached result in <0.1 ms.
- Complexity: A single file with a `Map`, a TTL check, and maybe 20-30 lines of code. Or use the `lru-cache` npm package.
- Limitation: Each EC2 instance has its own cache. With 2 instances behind ALB, a user might hit both and each one caches independently. At your scale, this is completely fine — the "waste" is 2 DB lookups instead of 1 per TTL window.
- **Verdict at 130 orders/day:** Worth it. This is the only caching change that has a favorable cost-benefit ratio right now.

**The math:**

- `getUserFromToken()` runs ~650 times/day (all API calls, not just orders)
- Each call takes ~5-10 ms (JWT decode + MongoDB query)
- Total DB time wasted: ~3-6.5 seconds/day
- With a 5-min TTL in-process cache, assuming ~20 unique users: ~20 cache misses per 5 minutes = ~5,760 cache hits/day (saving ~5,760 x 7.5 ms = ~43 seconds of DB time)
- The savings in absolute terms are tiny. The real win is *correctness of architecture* — logging middleware shouldn't be making DB calls.

### Step 6: The Cheapest Win — In-Process Cache for getUserFromToken (20 min)

**Exercise:** Design (don't implement yet) an in-process cache for the user lookup in `getUserFromToken()`.

**What you need:**

1. A `Map` (or `lru-cache` instance) keyed by JWT token (or the user ID extracted from the token)
2. Each entry stores the user object and a timestamp
3. On lookup: if the key exists and the timestamp is less than TTL old, return the cached value
4. On miss: query MongoDB, store the result in the cache with the current timestamp, return it
5. A maximum size limit so the cache doesn't grow unbounded (100 entries is more than enough for ~20 active users)

**Pseudocode:**

```javascript
const LRU = require('lru-cache');

const userCache = new LRU({
  max: 100,          // max entries
  ttl: 5 * 60 * 1000 // 5 minutes in ms
});

async function getUserFromToken(token) {
  const decoded = jwt.verify(token, secret);
  const userId = decoded.userId;

  const cached = userCache.get(userId);
  if (cached) return cached;

  const user = await User.findById(userId).lean();
  if (user) userCache.set(userId, user);
  return user;
}
```

**Design considerations:**

- **Key choice:** Use `userId` from the decoded JWT, not the raw token string. Multiple tokens for the same user should share the cache entry.
- **TTL choice:** 5 minutes is conservative. The user's name or role won't change within 5 minutes. You could go up to 15-30 minutes safely.
- `**.lean()`:** If you're not already using `.lean()` on this query, add it. It returns a plain JavaScript object instead of a Mongoose document, which is smaller and faster to cache.
- **Cache invalidation:** For the logging use case, you don't need explicit invalidation. TTL expiry is sufficient. If a user changes their profile, the worst case is that logs show the old name for up to 5 minutes.
- **Memory:** 100 user objects at ~1 KB each = ~100 KB. Negligible.
- **No sharing needed:** With 2 EC2 instances, each one caches independently. Both might do the initial DB lookup for the same user. At your scale, this duplication is free — 2 queries instead of 1, once every 5 minutes, is nothing.

**What about the other collections?**

You *could* apply the same in-process cache pattern to `dealer_custs`, `rate_msts`, and `prod_msts`. But ask yourself:

- How many times per day are these queried? ~130 for order-related calls. That's nothing.
- What's the risk if the cache serves stale data? For pricing and terms, even 5-minute staleness could theoretically cause a wrong price on an order placed right after a rate change.
- What's the benefit? Saving ~130 x 7.5 ms = ~1 second of DB time per day.
- **Verdict:** Not worth the invalidation complexity. Let MongoDB handle it.

## 15-Minute Review — Apply to DZZLO-OMS

Answer these questions in writing. Be honest about what your system actually needs vs. what sounds technically interesting.

1. **At 130 orders/day, which of the four cache layers (client, CDN, application, database) would actually help your system?** For each one, write one sentence explaining why it would or wouldn't help.
2. **If you were to cache `dealer_custs` with cache-aside and a 5-minute TTL, what's the worst-case scenario?** Think about: a dealer's terms are updated, and an order is placed 4 minutes later using the old terms. Is that acceptable for your business? What would your operations team say?
3. **What's the total monthly cost of the simplest Redis setup (ElastiCache `cache.t3.micro`) as a percentage of your current AWS bill?** Is that cost justified by the performance gain at current traffic?
4. **The in-process cache for `getUserFromToken()` doesn't share data across your 2 EC2 instances. Why is this acceptable?** What would have to change about your architecture for this to become a problem?
5. **At what scale (orders/day or requests/second) would you actually add Redis?** Write down a specific number and the specific trigger (latency threshold, DB connection count, or something else). This is your "cache trigger" — don't add Redis until you hit it.

**The bottom line for today:** The only caching worth implementing right now is an in-process LRU cache for `getUserFromToken()` in the logging middleware. Everything else — Redis, ElastiCache, caching `dealer_custs` or `rate_msts` — is premature optimization that adds complexity without meaningful benefit at your current scale. Revisit this decision when you hit ~1,000 orders/day or when MongoDB query latency becomes a measurable problem.

## Resources


| Resource                              | URL                                                                                                                                                          | Used In |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| System Design Primer — Cache          | [https://github.com/donnemartin/system-design-primer#cache](https://github.com/donnemartin/system-design-primer#cache)                                       | Step 1  |
| System Design Primer — Cache Patterns | [https://github.com/donnemartin/system-design-primer#when-to-update-the-cache](https://github.com/donnemartin/system-design-primer#when-to-update-the-cache) | Step 2  |
| Redis Getting Started                 | [https://redis.io/docs/latest/develop/get-started/](https://redis.io/docs/latest/develop/get-started/)                                                       | Step 3  |
| AWS ElastiCache for Redis             | [https://docs.aws.amazon.com/elasticache/latest/red-ug/GettingStarted.html](https://docs.aws.amazon.com/elasticache/latest/red-ug/GettingStarted.html)       | Step 3  |
| npm lru-cache                         | [https://www.npmjs.com/package/lru-cache](https://www.npmjs.com/package/lru-cache)                                                                           | Step 6  |


