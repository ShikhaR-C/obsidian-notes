# Session 13: Database Strategy & Polyglot Persistence

> Phase 6 — Deep Dives | 2 hours | Review: 15 min

## What You'll Learn

- When to use each database type (relational, document, key-value, time-series, search)
- Where MongoDB is the right choice for DZZLO-OMS and where it's being stretched
- Why Redis is the most impactful database addition for your system
- Whether PostgreSQL would improve financial data handling
- The polyglot persistence pattern — right database for each data type

## Why This Matters for DZZLO-OMS

You're running everything on MongoDB — transactional chains (order→SO→invoice→payment), master data, financial calculations, logs, relationships. MongoDB handles most of this well, but some patterns are being forced. Understanding database types helps you make better architectural decisions as you grow.

---

## Hour 1 — Database Types (60 min)

### Step 1: Database Types Overview (25 min)

| Type            | Best For                                                    | Examples                          | DZZLO Data That Fits                                  |
| --------------- | ----------------------------------------------------------- | --------------------------------- | ----------------------------------------------------- |
| **Document**    | Flexible schemas, embedded data, rapid iteration            | MongoDB, CouchDB                  | Orders (with embedded products), user profiles        |
| **Relational**  | ACID transactions, complex joins, financial data, reporting | PostgreSQL, MySQL                 | Invoice→payment reconciliation, financial reports     |
| **Key-Value**   | Fast lookups, caching, sessions, queues                     | Redis, DynamoDB                   | JWT caching, session store, rate limiting, job queues |
| **Time-Series** | Logs, metrics, IoT sensor data                              | TimescaleDB, InfluxDB, MongoDB TS | API request logs, DIP meter readings                  |
| **Search**      | Full-text search, fuzzy matching, faceted search            | Elasticsearch, Atlas Search       | Search across orders, invoices, customers             |
| **Graph**       | Complex relationships, recommendations                      | Neo4j                             | Dealer-customer networks (not needed at your scale)   |

### Step 2: Where MongoDB Is Right for DZZLO (10 min)

**Strong fits:**

| Data                                    | Why MongoDB Works                                                           |
| --------------------------------------- | --------------------------------------------------------------------------- |
| `order_msts` with embedded `products[]` | Document model — order + line items in one document. No joins needed.       |
| `users` with embedded `companies[]`     | Flexible per-company data. Polymorphic references (`refPath`).              |
| `dealer_custs` with composite `_id`     | Custom \_id pattern works well in MongoDB.                                  |
| `prod_msts`, `dealer_msts`, `cust_msts` | Simple CRUD master data. Schema flexibility helps during rapid development. |
| DIP models (separate DB)                | Clean domain separation with `createConnection()`.                          |

**Where MongoDB is being stretched:**

| Data                                           | The Stretch                                                                                                                                            |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Order → SO → Invoice → Payment chain           | Fundamentally relational. 4 collections linked by references. No foreign key enforcement. Orphaned records possible.                                   |
| Invoice calculations (tax, discount, rounding) | Financial math with precision. MongoDB uses IEEE 754 doubles. `(Math.round(v * 100) / 100).toFixed(2)` pattern throughout — manual precision handling. |
| `logs` collection (1.4M records)               | Time-series data treated as regular collection. No TTL, no compaction, no time-based partitioning.                                                     |
| Balance reconciliation                         | `cust_bal[]` balance tracking across multiple invoices and vouchers — would benefit from transactions/constraints.                                     |

### Step 3: Should You Add PostgreSQL? (10 min)

**For financial reporting — maybe, but not now.**

| Factor                   | MongoDB (Current)                                 | PostgreSQL (If Added)                                  |
| ------------------------ | ------------------------------------------------- | ------------------------------------------------------ |
| Invoice amount precision | `(Math.round(v * 100) / 100).toFixed(2)` — manual | `NUMERIC(10,2)` — native decimal precision             |
| Tax calculations         | In application code                               | Could use SQL `SUM`, `ROUND` with precision guarantees |
| Payment reconciliation   | Multiple queries + application logic              | Single JOIN query with aggregation                     |
| Monthly reports          | Aggregation pipelines (complex)                   | SQL queries (simpler for reporting)                    |
| ACID transactions        | Supported since MongoDB 4.0                       | Native, battle-tested                                  |
| Development effort       | Already built, working                            | Rewrite controllers + add ORM (Knex/Prisma)            |
| Operational cost         | Already paying for Atlas                          | ~$15-50/month for RDS PostgreSQL                       |

**Verdict:** Not worth it at 130 orders/day with a solo developer. The financial precision issues are manageable with the existing `toFixed(2)` pattern. PostgreSQL becomes worth considering when you need complex financial reports (e.g., GST filings, audit reports) or when data volume makes MongoDB aggregation pipelines slow.

### Step 4: Why Redis Is the #1 Database to Add (15 min)

Redis solves **5 separate problems** for DZZLO-OMS with a single addition:

| Problem                                         | Redis Solution                            |
| ----------------------------------------------- | ----------------------------------------- |
| `getUserFromToken()` DB lookup on every request | **Cache** decoded JWT → user mapping      |
| Rate limiting not shared across 2 servers       | **Shared store** for express-rate-limit   |
| No background job queue (SMS, email, push)      | **BullMQ** runs on Redis                  |
| No session store for DIP web app                | **connect-redis** for express-session     |
| Reference data cache not shared across servers  | **Shared cache** for prod_msts, rate_msts |

**One dependency, five solutions.** This is why Redis is called the "Swiss Army knife" of databases.

**Cost:** Redis on EC2 (t3.micro) ~$8/month, or ElastiCache ~$12/month, or Upstash free tier (10K commands/day — enough for 130 orders).

---

## Hour 2 — Applied (60 min)

### Step 5: Time-Series Strategy for Logs (15 min)

Your `logs` collection (1.4M records, 114 MB, growing 5K/day) is time-series data:

**Option A: MongoDB TTL Index (Simplest — Do This)**

```javascript
// One-time command in mongosh:
db.logs.createIndex({ createdAt: 1 }, { expireAfterSeconds: 7776000 }); // 90 days
```

Automatic cleanup, zero maintenance. Run during off-hours (first run deletes ~1M+ old docs).

**Option B: MongoDB Time-Series Collection (Better)**

Available on Atlas. Optimized storage, compression, time-based bucketing:

```javascript
db.createCollection("logs_ts", {
  timeseries: {
    timeField: "createdAt",
    metaField: "method",
    granularity: "minutes",
  },
  expireAfterSeconds: 7776000, // 90 days
});
```

~10x storage reduction for time-series data. Requires migration from existing `logs` collection.

**Option C: CloudWatch Logs (Offload Entirely)**

Send logs to CloudWatch instead of MongoDB. Use CloudWatch Insights for querying.

- Pro: No MongoDB storage growth, built-in dashboards
- Con: $0.50/GB ingested, different query language
- Best when you want to completely separate operational logs from business data

**Recommendation:** Option A now (5 minutes, zero cost). Consider Option B when logs grow past 1 GB.

### Step 6: MongoDB Atlas Features You're Not Using (15 min)

**Atlas Search** — Full-text search without Elasticsearch:

```javascript
// Search across order remarks, customer names, invoice numbers
const results = await OrderMst.aggregate([
  { $search: { text: { query: "diesel delivery", path: "remarks" } } },
  { $limit: 10 },
]);
```

Available on your dedicated plan. No extra cost.

**Atlas Charts** — Dashboards without code:

- Connect to your collections, drag-and-drop charts
- Orders per day, revenue trends, top customers
- Accessible from Atlas Console

**Atlas Online Archive** — Move old data to cheap storage:

- Archive orders older than 2 years to S3-backed storage
- Still queryable via Atlas Data Federation
- Reduces primary cluster storage

### Step 7: Polyglot Persistence Architecture for DZZLO (15 min)

**Recommended architecture (phased):**

```
Phase 1 (Now):
  MongoDB Atlas ──── Everything (current state)
  + TTL index on logs

Phase 2 (Add Redis):
  MongoDB Atlas ──── Business data (orders, invoices, users, etc.)
  Redis ──────────── JWT cache + rate limiting + BullMQ jobs + sessions
  MongoDB TTL ────── Logs (90-day retention)

Phase 3 (When Needed):
  MongoDB Atlas ──── Business documents
  MongoDB TS ─────── Time-series logs + DIP meter readings
  Redis ──────────── Cache + jobs + sessions
  Atlas Search ───── Full-text search across entities
  (PostgreSQL) ───── Financial reporting (only if complex reports needed)
```

### Step 8: Multi-Database in Node.js (15 min)

You already manage dual MongoDB connections. Adding Redis follows the same pattern:

```javascript
// helpers/redisClient.js
const Redis = require("ioredis");

const redis = new Redis({
  host: process.env.REDIS_HOST || "127.0.0.1",
  port: process.env.REDIS_PORT || 6379,
  maxRetriesPerRequest: 3,
  retryStrategy(times) {
    return Math.min(times * 50, 2000);
  },
});

redis.on("error", (err) => console.error("Redis error:", err.message));
redis.on("connect", () => console.log("Redis connected"));

module.exports = redis;
```

```javascript
// helpers/db_conn.js — add Redis alongside MongoDB
const { dbDefault, db_dip } = require("./db_conn");
const redis = require("./redisClient");

// Graceful shutdown — close all connections
process.on("SIGINT", async () => {
  await mongoose.disconnect();
  await db_dip.close();
  await redis.quit();
  process.exit(0);
});
```

**If adding PostgreSQL later (Knex example):**

```javascript
// helpers/pgClient.js
const knex = require("knex")({
  client: "pg",
  connection: process.env.PG_URI,
  pool: { min: 2, max: 10 },
});

module.exports = knex;

// Usage:
const monthlyRevenue = await knex("invoices")
  .select(knex.raw("DATE_TRUNC('month', inv_dt) as month"))
  .sum("inv_total_amt as total")
  .groupByRaw("DATE_TRUNC('month', inv_dt)")
  .orderBy("month", "desc");
```

---

## 15-Minute Review

1. **Decision:** Add TTL index on logs collection? (Recommended: yes, 90 days)
2. **Decision:** Add Redis? (Recommended: yes, solves 5 problems at once)
3. **Decision:** Explore Atlas Search? (Recommended: try it, it's free on your plan)
4. **Decision:** Add PostgreSQL? (Recommended: not now, revisit at 500+ businesses or when financial reporting becomes complex)
5. **Update** `docs/strategy/system-design.md` with your database decisions

## Resources

| Resource                        | URL                                                                |
| ------------------------------- | ------------------------------------------------------------------ |
| MongoDB Schema Design Patterns  | https://www.mongodb.com/blog/post/building-with-patterns-a-summary |
| MongoDB Time-Series Collections | https://www.mongodb.com/docs/manual/core/timeseries-collections/   |
| MongoDB TTL Indexes             | https://www.mongodb.com/docs/manual/core/index-ttl/                |
| MongoDB Atlas Search            | https://www.mongodb.com/docs/atlas/atlas-search/                   |
| Atlas Online Archive            | https://www.mongodb.com/docs/atlas/online-archive/                 |
| Redis Use Cases                 | https://redis.io/docs/latest/develop/get-started/                  |
| ioredis                         | https://github.com/redis/ioredis                                   |
| BullMQ (Redis job queue)        | https://docs.bullmq.io/                                            |
| Knex.js (SQL query builder)     | https://knexjs.org/                                                |
| AWS ElastiCache Pricing         | https://aws.amazon.com/elasticache/pricing/                        |
