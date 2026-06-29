# Database Deep Dive: Types, Trade-offs, and DZZLO-OMS Recommendations

> Research document. Covers database types, when to use each, and specific recommendations for the DZZLO-OMS project based on its current data patterns, scale, and architecture.

---

## Table of Contents

1. [Database Types Overview](#1-database-types-overview)
2. [MongoDB Strengths and Weaknesses for DZZLO-OMS](#2-mongodb-strengths-and-weaknesses-for-dzzlo-oms)
3. [Would PostgreSQL Be Better for Any DZZLO-OMS Data?](#3-would-postgresql-be-better-for-any-dzzlo-oms-data)
4. [Redis for DZZLO-OMS](#4-redis-for-dzzlo-oms)
5. [Time-Series Database for Logs](#5-time-series-database-for-logs)
6. [Search Capabilities](#6-search-capabilities)
7. [Polyglot Persistence Pattern](#7-polyglot-persistence-pattern)
8. [MongoDB Atlas Features Being Underused](#8-mongodb-atlas-features-being-underused)
9. [DynamoDB as an Alternative](#9-dynamodb-as-an-alternative)
10. [Practical Recommendations for DZZLO-OMS](#10-practical-recommendations-for-dzzlo-oms)
11. [Multi-Database Architecture in Node.js](#11-multi-database-architecture-in-nodejs)
12. [Data Migration Strategies](#12-data-migration-strategies)

---

## 1. Database Types Overview

### 1.1 Relational Databases (PostgreSQL, MySQL)

**What they solve best:** Structured data with well-defined relationships, ACID transactions across tables, complex joins, data integrity enforcement via constraints.

**Core traits:**

- Fixed schema with tables, rows, columns
- Foreign keys enforce referential integrity
- SQL query language with powerful JOIN, GROUP BY, window functions
- ACID transactions are native and battle-tested
- Vertical scaling (bigger machine); read replicas for read scaling

**When to use:**

- Financial data requiring referential integrity and precision (NUMERIC/DECIMAL types)
- Data with deep relational chains (order -> invoice -> payment -> balance)
- Complex reporting and analytics (window functions, CTEs, materialized views)
- Multi-table transactions that must be atomic
- Regulatory/compliance-sensitive data

**When NOT to use:**

- Rapidly evolving schemas where columns change weekly
- Deeply nested or polymorphic document structures
- Write-heavy workloads requiring horizontal scaling beyond a single server
- Semi-structured data where each record has different fields

**PostgreSQL vs MySQL:**


| Aspect             | PostgreSQL                                                      | MySQL                                |
| ------------------ | --------------------------------------------------------------- | ------------------------------------ |
| JSON support       | Native JSONB with indexing                                      | JSON type, less performant           |
| Data types         | NUMERIC (arbitrary precision), arrays, ranges, UUID, geospatial | Fewer advanced types                 |
| Extensions         | PostGIS, TimescaleDB, pg_trgm, etc.                             | Limited                              |
| Concurrency        | MVCC, no read locks                                             | InnoDB MVCC, but historically weaker |
| Horizontal scaling | Citus extension, or app-level sharding                          | MySQL Cluster, Vitess                |
| Ecosystem          | Supabase, Neon, AWS Aurora, Render                              | PlanetScale, Vitess, Aurora          |


**Verdict for DZZLO-OMS:** PostgreSQL is the stronger candidate if DZZLO were to adopt a relational database, because of superior JSON support (useful during migration), NUMERIC precision for financial data, and the PostGIS extension for geospatial queries on dealer_coords/cust_coords.

**Cost:**

- Self-hosted on EC2: ~$15-40/mo for a t3.medium with EBS
- AWS RDS PostgreSQL: ~$30-80/mo for db.t3.medium (single-AZ)
- Supabase free tier: 500 MB, then $25/mo for Pro
- Neon serverless: free tier with 512 MB, then pay-per-use

**Documentation:**

- [https://www.postgresql.org/docs/current/](https://www.postgresql.org/docs/current/)
- [https://www.mysql.com/products/community/](https://www.mysql.com/products/community/)

---

### 1.2 Document Databases (MongoDB)

**What they solve best:** Flexible schemas, nested/embedded documents, rapid iteration, horizontal scaling via sharding.

**Core traits:**

- Schema-flexible: each document in a collection can have different fields
- BSON format supports rich types (ObjectId, Decimal128, Date, Binary)
- Embedding related data in a single document avoids joins
- Horizontal scaling via sharding (automatic data distribution)
- Multi-document ACID transactions (since MongoDB 4.0)

**When to use:**

- Content management, catalogs, user profiles
- Data where the "shape" varies between records (e.g., different product types with different fields)
- Rapid prototyping and iterating on schema
- Embedding child records inside parent documents (orders with products array)
- Geospatial queries (native 2dsphere indexes)

**When NOT to use:**

- Deep relational chains requiring foreign key enforcement
- Complex multi-collection joins (aggregation $lookup is expensive)
- Financial calculations requiring database-level decimal precision enforcement
- Heavy analytical queries with GROUP BY across multiple collections

**Relevance to DZZLO-OMS:** MongoDB is currently the sole database. It handles the document model well (orders with embedded products, dealers with embedded tanks/nozzles). It struggles with the relational chain (order -> SO -> invoice -> voucher -> balance) and financial precision.

**Documentation:** [https://www.mongodb.com/docs/manual/](https://www.mongodb.com/docs/manual/)

---

### 1.3 Key-Value Stores (Redis, DynamoDB)

**What they solve best:** Ultra-fast reads/writes by key, caching, session storage, rate limiting, real-time counters, message queues.

**Redis:**

- In-memory data structure store (strings, hashes, lists, sets, sorted sets, streams)
- Sub-millisecond latency for reads and writes
- Pub/sub messaging, Lua scripting, transactions
- Persistence options: RDB snapshots, AOF append-only file
- Use cases: cache, session store, rate limiter, leaderboard, job queue (BullMQ)

**DynamoDB:**

- Serverless, fully managed by AWS
- Key-value + document model
- Pay-per-request or provisioned capacity
- Single-digit millisecond latency at any scale
- DynamoDB Streams for change data capture
- Use cases: session store, user preferences, IoT data, high-throughput logs

**When to use:**

- Caching frequently-read, rarely-changed data (dealer master data, rate cards, product lists)
- Session management (replacing JWT payload storage with server-side sessions)
- Rate limiting across multiple server instances
- Job queues for background processing (invoice PDF generation, email sending)
- Real-time counters (online users, active orders)

**When NOT to use:**

- Complex queries, joins, or aggregations
- Data requiring relational integrity
- Primary storage for business-critical transactional data (unless DynamoDB with careful design)

**Cost:**

- Redis (ElastiCache): ~$13-25/mo for cache.t3.micro single-AZ
- Redis (self-hosted on EC2): ~$8-15/mo on t3.micro
- Upstash Redis (serverless): free tier 10K commands/day, then pay-per-request
- DynamoDB: free tier 25 GB + 25 WCU/RCU, then ~$1.25 per million write requests

**Documentation:**

- [https://redis.io/docs/](https://redis.io/docs/)
- [https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)

---

### 1.4 Time-Series Databases (TimescaleDB, InfluxDB)

**What they solve best:** Data that arrives as timestamped events -- metrics, logs, sensor readings, financial tick data. Optimized for time-range queries, downsampling, and retention policies.

**TimescaleDB:**

- Extension on top of PostgreSQL (full SQL compatibility)
- Hypertables automatically partition data by time
- Compression: 90-98% storage reduction for older data
- Continuous aggregates (materialized views that auto-update)
- Retention policies (auto-delete data older than N days)
- Can run alongside regular PostgreSQL tables

**InfluxDB:**

- Purpose-built time-series database
- Flux query language (not SQL, learning curve)
- Built-in retention policies, downsampling, alerting
- InfluxDB Cloud (serverless) or self-hosted OSS
- Best for metrics/monitoring, IoT sensor data

**MongoDB Time Series Collections:**

- Available since MongoDB 5.0
- Optimized storage for time-series data within MongoDB
- Automatic bucketing by time field
- Supports secondary indexes
- No schema change needed -- stays in the same MongoDB cluster
- TTL indexes for automatic data expiration

**When to use:**

- API request logs (DZZLO's `logs` collection: 1.4M records, growing ~5K/day)
- Sensor/meter readings (DIP meter_reads collection)
- Financial price history (rate changes over time)
- System metrics (CPU, memory, response times)

**When NOT to use:**

- General-purpose application data
- Data requiring complex joins or updates to historical records
- Small datasets where a regular table/collection is sufficient

**Cost:**

- TimescaleDB Cloud: free tier 25 MB compressed, then $0.09/GB/mo
- InfluxDB Cloud: free tier 30-day retention, then $0.002/MB writes
- MongoDB Time Series: no extra cost (uses existing Atlas cluster)

**Documentation:**

- [https://docs.timescale.com/](https://docs.timescale.com/)
- [https://docs.influxdata.com/influxdb/](https://docs.influxdata.com/influxdb/)
- [https://www.mongodb.com/docs/manual/core/timeseries-collections/](https://www.mongodb.com/docs/manual/core/timeseries-collections/)

---

### 1.5 Graph Databases (Neo4j)

**What they solve best:** Data where relationships ARE the primary query target. Traversing connected data -- social networks, recommendation engines, fraud detection, knowledge graphs.

**Core traits:**

- Nodes (entities) and edges (relationships) as first-class citizens
- Cypher query language for pattern matching
- Traversals are O(1) per hop (vs. O(N) joins in relational)
- Excellent for "friends of friends," shortest path, influence analysis

**When to use:**

- Social networks, recommendation engines
- Fraud detection (finding suspicious transaction patterns)
- Supply chain / logistics optimization
- Knowledge graphs and taxonomies

**Relevance to DZZLO-OMS:** **LOW**. DZZLO's relationships are hierarchical (dealer -> customer -> orders) not graph-like (no "friends of friends" queries). The dealer-customer relationship is a simple many-to-many junction, not a complex network. A graph database would be massive over-engineering.

**Verdict:** Not needed. Skip entirely.

---

### 1.6 Search Engines (Elasticsearch, Atlas Search, Algolia)

**What they solve best:** Full-text search with relevance ranking, faceted search, autocomplete, fuzzy matching, and analytics over text data.

**Elasticsearch:**

- Distributed, RESTful search engine built on Apache Lucene
- Full-text search, aggregations, geospatial queries
- Kibana for visualization
- Requires separate cluster management
- Self-hosted or AWS OpenSearch Service

**MongoDB Atlas Search:**

- Lucene-based search integrated into MongoDB Atlas
- No separate cluster -- runs on existing Atlas nodes
- Queried via aggregation pipeline ($search stage)
- Supports fuzzy matching, autocomplete, faceting, scoring
- Available on M10+ dedicated clusters

**Algolia:**

- Managed search-as-a-service (SaaS)
- Extremely fast (1-20ms responses)
- Easy to integrate, great developer experience
- Expensive at scale ($1/1000 search requests after free tier)
- Best for customer-facing search bars

**Relevance to DZZLO-OMS:** MODERATE. Searching across orders, invoices, customers by name/number could benefit from Atlas Search. Currently, find queries with regex are likely handling this. At 120 businesses and 130 orders/day, full-text search is a "nice to have" not a "must have."

**Cost:**

- Elasticsearch (self-hosted): ~$30-60/mo on EC2 (needs dedicated instances)
- AWS OpenSearch: ~$50-100/mo minimum
- Atlas Search: included with M10+ Atlas cluster (no extra charge for basic usage)
- Algolia: free tier 10K searches/mo, then $1/1K requests

---

### 1.7 Column-Family Databases (Cassandra, ScyllaDB)

**What they solve best:** Extremely high write throughput, time-series data at massive scale, multi-datacenter replication with tunable consistency.

**Core traits:**

- Distributed, no single point of failure
- Write-optimized (log-structured merge trees)
- CQL (Cassandra Query Language, SQL-like)
- Tunable consistency (ONE, QUORUM, ALL)
- Best at >100K writes/second across multiple regions

**When to use:**

- IoT telemetry at massive scale (millions of devices)
- Messaging platforms (billions of messages)
- Time-series data at extreme volume (>1M events/minute)
- Multi-region deployments requiring low-latency writes everywhere

**Relevance to DZZLO-OMS:** **NONE**. At 130 orders/day and 5K logs/day, DZZLO is 4-5 orders of magnitude below where Cassandra makes sense. This is a technology for Netflix, Discord, and Apple -- not for a 120-business OMS.

**Verdict:** Not needed. Skip entirely.

---

### Summary Comparison Table


| Database Type           | Best For                                     | DZZLO Relevance                 | Add Now?                            |
| ----------------------- | -------------------------------------------- | ------------------------------- | ----------------------------------- |
| **PostgreSQL**          | Financial data, relational chains, reporting | HIGH (order-to-cash flow)       | Not yet -- see Section 10           |
| **MongoDB**             | Documents, flexible schema, embedded data    | HIGH (already in use)           | Keep as primary                     |
| **Redis**               | Caching, sessions, rate limiting, queues     | HIGH (multiple use cases)       | YES -- highest ROI                  |
| **TimescaleDB**         | Time-series at scale                         | LOW (logs not big enough yet)   | No                                  |
| **MongoDB Time Series** | Time-series within MongoDB                   | MEDIUM (easy logs optimization) | Yes -- low effort                   |
| **Atlas Search**        | Full-text search                             | MEDIUM                          | Worth exploring (free on dedicated) |
| **Elasticsearch**       | Full-text search (dedicated)                 | LOW                             | Over-engineering                    |
| **Neo4j**               | Graph traversals                             | NONE                            | No                                  |
| **Cassandra**           | Extreme write throughput                     | NONE                            | No                                  |
| **DynamoDB**            | Serverless key-value                         | LOW-MEDIUM                      | Maybe for logs                      |
| **Algolia**             | Customer-facing search                       | LOW                             | No                                  |


---

## 2. MongoDB Strengths and Weaknesses for DZZLO-OMS

### 2.1 Where MongoDB Is the Right Choice

**Order documents with embedded products:**
The `order_msts` schema embeds products as a sub-document array. This is textbook MongoDB -- a single read fetches the entire order with all its line items. No joins needed.

```javascript
// Current schema -- perfect for MongoDB
const order_mst_Schema = new mongoose.Schema({
  dealer_id: { type: ObjectId, ref: "dealer_msts" },
  cust_id: { type: ObjectId, ref: "cust_msts" },
  products: [order_trn_Schema],  // embedded array -- one read
  // ...
});
```

**DIP dealer configuration:**
The `dealers` DIP model embeds tanks, nozzles, dispensing units, and products. This hierarchical document is what MongoDB was designed for.

```javascript
// Perfect document model
const dealers_Schema = new mongoose.Schema({
  dealer_id: { type: ObjectId },
  products: [products_Schema],   // embedded
  tanks: [tanks_Schema],         // embedded
  dus: [dus_Schema],             // embedded
  nzls: [nozzles_Schema],        // embedded
});
```

**Flexible master data:**
Dealer and customer schemas have varying fields (some dealers have GST, some don't; some customers have coordinates, some don't). MongoDB handles this naturally without NULL columns.

**Geospatial queries:**
MongoDB's native 2dsphere indexes work well with dealer_coords and cust_coords Point types. No need for a separate geospatial database.

**Rapid development:**
As a solo developer, schema changes in MongoDB require zero migrations, no ALTER TABLE downtime, no DBA coordination. Add a field to the Mongoose schema and deploy.

### 2.2 Where MongoDB Is Being Stretched

**The order-to-cash relational chain:**

```
order_msts → so_msts → invs → voc_msts → dealer_custs.cust_bal
```

This is fundamentally relational data. Currently:

- `so_msts.inv_id` references `invs._id` (foreign key without enforcement)
- `voc_msts.inv_id` references `invs._id` (same)
- `order_msts.so_id` references `so_msts._id` (same)
- Balance calculation requires querying 3 collections and summing in application code

There is NO database-level enforcement that an invoice references a valid sales order, or that a payment references a valid invoice. If application code has a bug, orphaned references can silently enter the database.

**Financial precision:**
The current approach uses JavaScript floating-point with manual rounding:

```javascript
// Current approach in invs.js -- fragile
inv_amt: {
  type: Number,
  set: function (v) {
    return (Math.round(v * 100) / 100).toFixed(2);
  },
},
```

Problems:

1. `Number` in MongoDB is IEEE 754 double-precision float (same as JavaScript). `0.1 + 0.2 = 0.30000000000000004`.
2. The setter calls `.toFixed(2)` which returns a **string**, but the field is `type: Number`. Mongoose coerces it back to a float, potentially re-introducing precision errors.
3. MongoDB supports `Decimal128` (128-bit decimal floating point) which would be more appropriate, but the current schema does not use it.

PostgreSQL's `NUMERIC(12,2)` would handle this at the database level with arbitrary precision.

**Complex aggregation pipelines:**
Looking at `api_v3/services/dealer_custs.js` and `api_v3/services/invs.js`, the codebase has extensive aggregation pipelines with `$lookup`, `$group`, `$match`, and `$unwind`. These are essentially SQL JOINs and GROUP BY operations expressed as verbose JSON arrays.

Example comparison -- getting unpaid invoices with customer details:

```javascript
// MongoDB aggregation (current pattern, ~30 lines)
const sales_Orders = await SalesOrder.aggregate([
  { $match: { dealer_id: ObjectId(dealer_id), inv_id: { $exists: false } } },
  { $lookup: {
      from: "cust_msts",
      localField: "cust_id",
      foreignField: "_id",
      as: "customer"
  }},
  { $lookup: {
      from: "dealer_msts",
      localField: "dealer_id",
      foreignField: "_id",
      as: "dealer"
  }},
  { $unwind: "$customer" },
  { $group: { _id: "$cust_id", countSO: { $sum: 1 } } },
]);
```

```sql
-- PostgreSQL equivalent (~5 lines)
SELECT c.cust_name, COUNT(so.id) as count_so
FROM so_msts so
JOIN cust_msts c ON so.cust_id = c.id
WHERE so.dealer_id = $1 AND so.inv_id IS NULL
GROUP BY c.cust_name;
```

**Balance calculation in application code:**
The `currentInvoiceBalance` function in `helpers/Balance/index.js` fetches invoices and vouchers, then sums them in JavaScript. This is:

- Vulnerable to race conditions (two concurrent requests could read stale data)
- Slower than a database-side calculation
- Duplicated logic across multiple endpoints

In PostgreSQL, this would be a VIEW or a stored function with guaranteed consistency.

**No cascading deletes/updates:**
Several Mongoose pre-delete hooks are commented out (`invSchema.pre("deleteOne")`, `cust_mst_Schema.pre("deleteOne")`). The comments say "deleting data will not give details in past orders. better to assign a blocked field." This is a sign that application-level referential integrity is hard to maintain. PostgreSQL would handle this with `ON DELETE SET NULL` or `ON DELETE RESTRICT`.

### 2.3 Assessment


| Data Category                              | MongoDB Fit | Notes                                      |
| ------------------------------------------ | ----------- | ------------------------------------------ |
| Orders (with embedded products)            | EXCELLENT   | Perfect document model                     |
| DIP dealer config (tanks, nozzles, DUs)    | EXCELLENT   | Hierarchical embedded data                 |
| Master data (dealers, customers, products) | GOOD        | Flexible schema helps                      |
| Geospatial (coordinates)                   | GOOD        | Native 2dsphere support                    |
| Logs                                       | ADEQUATE    | Time-series collection would improve it    |
| SO -> Invoice -> Payment chain             | POOR        | Relational chain without FK enforcement    |
| Financial calculations                     | POOR        | Float precision, application-side math     |
| Balance tracking                           | POOR        | Race conditions, no DB-side aggregation    |
| Reporting/analytics                        | POOR        | Aggregation pipelines are verbose and slow |
| dealer_custs (junction table)              | POOR        | Composite _id is an anti-pattern in Mongo  |


---

## 3. Would PostgreSQL Be Better for Any DZZLO-OMS Data?

### 3.1 The Order-to-Cash Flow

The transactional chain `order -> SO -> invoice -> voucher -> balance` is textbook relational data. Here is what PostgreSQL would provide that MongoDB does not:

**Foreign key enforcement:**

```sql
CREATE TABLE so_msts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dealer_id UUID NOT NULL REFERENCES dealer_msts(id),
  cust_id UUID NOT NULL REFERENCES cust_msts(id),
  inv_id UUID REFERENCES invs(id) ON DELETE SET NULL,
  -- Cannot insert a SO referencing a non-existent dealer or customer
);
```

Currently in MongoDB, nothing prevents inserting a `so_msts` document with a `dealer_id` that does not exist in `dealer_msts`.

**Decimal precision:**

```sql
CREATE TABLE invs (
  inv_amt NUMERIC(12,2) NOT NULL,    -- exact decimal, no floating-point errors
  inv_tax_amt NUMERIC(12,2),
  inv_tcs_amt NUMERIC(12,2),
  inv_total_amt NUMERIC(12,2) NOT NULL,
  -- The database guarantees 2-decimal precision. No application-side rounding.
);
```

**Balance as a database VIEW:**

```sql
-- Replace 200+ lines of JavaScript balance calculation with a view
CREATE VIEW current_balances AS
SELECT
  dc.dealer_id,
  dc.cust_id,
  dc.last_bal_value,
  dc.last_bal_date,
  COALESCE(SUM(i.inv_total_amt), 0) AS invoiced_since,
  COALESCE(SUM(CASE
    WHEN v.pay_type = 'DEBIT' THEN -v.amount
    ELSE v.amount
  END), 0) AS paid_since,
  dc.last_bal_value
    + COALESCE(SUM(i.inv_total_amt), 0)
    - COALESCE(SUM(CASE
        WHEN v.pay_type = 'DEBIT' THEN -v.amount
        ELSE v.amount
      END), 0) AS current_balance
FROM dealer_custs dc
LEFT JOIN invs i ON i.dealer_id = dc.dealer_id
  AND i.cust_id = dc.cust_id
  AND i.inv_dt >= dc.last_bal_date
LEFT JOIN voc_msts v ON v.dealer_id = dc.dealer_id
  AND v.cust_id = dc.cust_id
  AND v.pay_status = true
  AND v.pay_dt >= dc.last_bal_date
GROUP BY dc.dealer_id, dc.cust_id, dc.last_bal_value, dc.last_bal_date;
```

This replaces `currentInvoiceBalance`, `bal_open_inv_pay`, and `currentInvOutstanding` -- three separate functions totaling 200+ lines of JavaScript with race-condition vulnerabilities.

**Complex reporting with window functions:**

```sql
-- Monthly revenue trend per dealer with running total (impossible in MongoDB without $setWindowFields)
SELECT
  dealer_id,
  DATE_TRUNC('month', inv_dt) AS month,
  SUM(inv_total_amt) AS monthly_revenue,
  SUM(SUM(inv_total_amt)) OVER (
    PARTITION BY dealer_id
    ORDER BY DATE_TRUNC('month', inv_dt)
  ) AS cumulative_revenue
FROM invs
GROUP BY dealer_id, DATE_TRUNC('month', inv_dt)
ORDER BY dealer_id, month;
```

### 3.2 MongoDB Aggregation Pipeline vs PostgreSQL Joins

**The current `dealer_custs.js` balance calculation pattern:**

In `api_v3/services/dealer_custs.js`, the code runs multiple sequential aggregation pipelines:

1. `Invoices.aggregate(unPaidInvPipeline)` -- get unpaid invoice sums
2. `SOMaster.aggregate(getCsSum(...))` -- get cash reimbursement sums
3. `SOMaster.aggregate(getPtSum(...))` -- get product total sums
4. `VoucherMaster.aggregate(unApprovedVocPipeline)` -- get unapproved voucher sums

That is 4 separate database round trips, each involving `$match` and `$group`. In PostgreSQL:

```sql
-- Single query, single round trip
SELECT
  COALESCE(inv_sums.unpaid_total, 0) AS unpaid_invoices,
  COALESCE(cs_sums.cs_total, 0) AS cash_reimburse,
  COALESCE(pt_sums.pt_total, 0) AS product_total,
  COALESCE(voc_sums.unapproved_total, 0) AS unapproved_vouchers
FROM dealer_custs dc
LEFT JOIN LATERAL (
  SELECT SUM(inv_total_amt) AS unpaid_total
  FROM invs WHERE dealer_id = dc.dealer_id AND cust_id = dc.cust_id
  AND inv_status IN ('UNPAID', 'PARTPAID')
) inv_sums ON true
LEFT JOIN LATERAL (
  SELECT SUM(cs_reimb_amt) AS cs_total
  FROM so_msts WHERE dealer_id = dc.dealer_id AND cust_id = dc.cust_id
  AND cs_reimb_amt IS NOT NULL
) cs_sums ON true
-- ... similar for pt_sums and voc_sums
WHERE dc.dealer_id = $1 AND dc.cust_id = $2;
```

### 3.3 The Honest Trade-off

**Arguments FOR adding PostgreSQL to DZZLO-OMS:**

- Foreign key enforcement prevents orphaned data
- NUMERIC type eliminates floating-point financial bugs
- SQL is more concise for reporting queries
- Views and materialized views for pre-computed balances
- Transactions are simpler (no session management needed)
- Better tooling for financial audits

**Arguments AGAINST adding PostgreSQL to DZZLO-OMS right now:**

- Solo developer maintaining two databases is double the operational burden
- Migration is risky for a running production system
- The current MongoDB setup works (even if imperfect)
- 120 businesses and 130 orders/day do not stress MongoDB
- Mongoose schemas provide "soft" validation that is sufficient for now
- Adding PostgreSQL means learning Prisma/Knex, SQL optimization, migrations
- Money: additional $30-80/mo for managed PostgreSQL

**Verdict:** PostgreSQL would be a better fit for the financial chain, but the operational cost of dual databases outweighs the benefits at current scale. The higher-ROI move is to fix MongoDB's weaknesses in-place:

1. Switch financial fields to `Decimal128`
2. Add MongoDB schema validation rules for referential checks
3. Use MongoDB transactions for multi-document operations (already in `helpers/transactions.js`)
4. Consider PostgreSQL when DZZLO hits 500+ businesses or adds formal accounting/reporting features

---

## 4. Redis for DZZLO-OMS

Redis is the single highest-ROI addition DZZLO could make. It solves 4-5 distinct problems with a single piece of infrastructure.

### 4.1 Use Case 1: Rate Limiting Across Multiple Instances

**Current state:** `express-rate-limit` with default in-memory store. If PM2 runs multiple instances, each instance has its own counter -- a user could hit instance A 99 times and instance B 99 times without triggering a 100-request limit.

**Solution:** `rate-limit-redis` package with Redis store.

```javascript
// dzzlo_oms.js
const rateLimit = require("express-rate-limit");
const { RedisStore } = require("rate-limit-redis");
const Redis = require("ioredis");

const redisClient = new Redis({
  host: process.env.REDIS_HOST || "127.0.0.1",
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  // TLS for ElastiCache
  // tls: {},
});

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({
    sendCommand: (...args) => redisClient.call(...args),
  }),
});

app.use("/api/", apiLimiter);
```

### 4.2 Use Case 2: Caching Frequently-Read Data

**What to cache:**

- Dealer master data (changes rarely, read on every API call for auth middleware)
- Product lists per dealer (changes when admin updates products)
- Rate cards (changes once daily when fuel prices change)
- DIP dealer configuration (tanks, nozzles -- changes very rarely)

```javascript
// helpers/cache.js
const Redis = require("ioredis");
const redis = new Redis(process.env.REDIS_URL);

const CACHE_TTL = {
  DEALER_MASTER: 3600,    // 1 hour
  PRODUCT_LIST: 1800,     // 30 minutes
  RATE_CARD: 300,         // 5 minutes (changes daily)
  DIP_CONFIG: 7200,       // 2 hours
};

exports.getOrSet = async (key, ttl, fetchFn) => {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const data = await fetchFn();
  await redis.setex(key, ttl, JSON.stringify(data));
  return data;
};

exports.invalidate = async (pattern) => {
  const keys = await redis.keys(pattern);
  if (keys.length > 0) await redis.del(...keys);
};

// Usage in a controller
const { getOrSet, invalidate } = require("../helpers/cache");

// Read with cache
const dealer = await getOrSet(
  `dealer:${dealer_id}`,
  CACHE_TTL.DEALER_MASTER,
  () => DealerMaster.findById(dealer_id).lean()
);

// Invalidate on update
await DealerMaster.findByIdAndUpdate(dealer_id, updateData);
await invalidate(`dealer:${dealer_id}`);
```

**Estimated impact:** For endpoints that currently hit MongoDB on every request for dealer/product data, Redis caching could reduce MongoDB load by 50-70% and improve response times by 10-50ms.

### 4.3 Use Case 3: Session Store

**Current state:** JWT tokens with payload containing user data. Stateless authentication.

**If DZZLO ever needs server-side session features:**

- Force-logout a user (revoke session)
- Track active sessions per user
- Single-device enforcement

```javascript
// Only if needed -- JWT is fine for now
const session = require("express-session");
const RedisStore = require("connect-redis").default;

app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { secure: true, maxAge: 86400000 },
}));
```

**Note:** This is lower priority. JWT works well for mobile apps. Consider adding a Redis-based token blacklist for logout functionality instead of full session management.

### 4.4 Use Case 4: BullMQ Job Queue

**Current state:** Invoice PDF generation and email sending appear to happen synchronously in the request cycle.

**Background job candidates:**

- Invoice PDF generation (`html-pdf` package)
- Email sending via AWS SES (`nodemailer-ses-transport`)
- OTP SMS sending via 2Factor.in
- Monthly balance summary calculations
- Excel report generation (`exceljs` package)

```javascript
// workers/queues.js
const { Queue, Worker } = require("bullmq");
const Redis = require("ioredis");

const connection = new Redis(process.env.REDIS_URL, { maxRetriesPerRequest: null });

// Define queues
const emailQueue = new Queue("email", { connection });
const pdfQueue = new Queue("pdf-generation", { connection });

// Enqueue a job (in controller)
await emailQueue.add("send-invoice", {
  to: customer.email,
  invoiceId: invoice._id,
  dealerId: dealer._id,
}, {
  attempts: 3,
  backoff: { type: "exponential", delay: 5000 },
});

// Worker (separate process or same process)
const emailWorker = new Worker("email", async (job) => {
  const { to, invoiceId, dealerId } = job.data;
  // Generate PDF, send email
  const invoice = await Inv.findById(invoiceId);
  const pdf = await generatePDF(invoice);
  await sendEmail({ to, subject: `Invoice ${invoice.inv_no}`, attachment: pdf });
}, { connection, concurrency: 2 });
```

### 4.5 Use Case 5: Real-Time Features

If DZZLO adds real-time features (currently uses Socket.io 2.4.1):

- Redis Pub/Sub as the Socket.io adapter for multi-instance deployment
- Real-time order status updates across connected clients

```javascript
const { createAdapter } = require("@socket.io/redis-adapter");
const { createClient } = require("redis");

const pubClient = createClient({ url: process.env.REDIS_URL });
const subClient = pubClient.duplicate();
await Promise.all([pubClient.connect(), subClient.connect()]);

io.adapter(createAdapter(pubClient, subClient));
```

### 4.6 Cost and Setup


| Option                           | Cost/Month                      | Latency                       | Management    |
| -------------------------------- | ------------------------------- | ----------------------------- | ------------- |
| AWS ElastiCache (cache.t3.micro) | ~$13 single-AZ                  | <1ms from EC2                 | Managed       |
| Self-hosted on EC2 (t3.micro)    | ~$8 (included in instance)      | <1ms                          | Manual        |
| Upstash Redis (serverless)       | Free tier, then ~$0.2/100K cmds | ~5-10ms (if different region) | Fully managed |
| Redis on same EC2 as app         | $0 extra                        | <0.1ms                        | Manual        |


**Recommendation:** Start with Redis on the same EC2 instance as the application (zero extra cost). If DZZLO moves to multi-instance deployment, upgrade to ElastiCache.

**Documentation:**

- [https://redis.io/docs/latest/](https://redis.io/docs/latest/)
- [https://docs.bullmq.io/](https://docs.bullmq.io/)
- [https://www.npmjs.com/package/rate-limit-redis](https://www.npmjs.com/package/rate-limit-redis)
- [https://www.npmjs.com/package/ioredis](https://www.npmjs.com/package/ioredis)

---

## 5. Time-Series Database for Logs

### 5.1 Current State

The `logs` collection stores API request logs:

```javascript
const logs_Schema = new mongoose.Schema({
  method: { type: String },         // GET, POST, PUT, DELETE
  url: { type: String },            // /api/v2/order_msts
  api_v: { type: String },          // v2, v3
  response_time: { type: Number },  // milliseconds
  status: { type: Number },         // 200, 404, 500
  statusMessage: { type: String },
  content_str_length: { type: Number },
  timeIST: { type: String },        // string representation
  user: { type: Mixed },            // user info
  appInfo: { type: Mixed },         // app metadata
}, { timestamps: true });
```

**Size:** 1.4M documents, growing ~5K/day = ~1.8M/year = ~150K/month.

**Queries performed on logs (likely):**

- "Show me all requests in the last hour" (time range)
- "Show me all 500 errors today" (time range + filter)
- "What's the average response time for /api/v2/order_msts?" (aggregation over time)
- "Which endpoints are slowest?" (GROUP BY + AVG over time window)

### 5.2 Option A: MongoDB Time Series Collection (RECOMMENDED)

**Zero new infrastructure.** Convert the existing `logs` collection to a time-series collection.

```javascript
// Migration: create new time-series collection, copy data, swap names
// In MongoDB shell or migration script:

db.createCollection("logs_ts", {
  timeseries: {
    timeField: "createdAt",        // the timestamp field
    metaField: "meta",             // optional: fields for grouping
    granularity: "minutes",        // expected interval between measurements
  },
  expireAfterSeconds: 7776000,     // 90 days TTL -- auto-delete old logs
});

// Updated Mongoose schema
const logs_Schema = new mongoose.Schema({
  createdAt: { type: Date, default: Date.now },  // timeField
  meta: {                                         // metaField
    method: { type: String },
    api_v: { type: String },
    url: { type: String },
  },
  response_time: { type: Number },
  status: { type: Number },
  statusMessage: { type: String },
  content_str_length: { type: Number },
  timeIST: { type: String },
  user: { type: Mixed },
  appInfo: { type: Mixed },
});
```

**Benefits:**

- 2-5x storage compression (columnar storage for measurements)
- Faster time-range queries (automatic time-based bucketing)
- TTL auto-expiration (no manual cleanup needed)
- No new infrastructure, no new connection, same Mongoose
- Included in existing Atlas pricing

**Limitations:**

- Cannot update individual documents (append-only)
- Cannot use `$lookup` in time-series aggregations (but rarely needed for logs)
- Must define the time field and meta fields at collection creation

### 5.3 Option B: CloudWatch Logs + S3

**Ship logs to CloudWatch instead of MongoDB.**

```javascript
// Replace MongoDB log writing with CloudWatch Logs
const { CloudWatchLogsClient, PutLogEventsCommand } = require("@aws-sdk/client-cloudwatch-logs");

const cwClient = new CloudWatchLogsClient({ region: "ap-south-1" });

const logToCloudWatch = async (logData) => {
  await cwClient.send(new PutLogEventsCommand({
    logGroupName: "/dzzlo-oms/api-requests",
    logStreamName: `${new Date().toISOString().split('T')[0]}`,
    logEvents: [{
      timestamp: Date.now(),
      message: JSON.stringify(logData),
    }],
  }));
};
```

**Benefits:**

- Fully managed, auto-scaling
- CloudWatch Insights for querying
- S3 archival for long-term storage
- Alarms and metrics built in
- Removes 1.4M documents from MongoDB (reduces Atlas storage costs)

**Costs:**

- CloudWatch Logs ingestion: $0.50/GB
- CloudWatch Logs storage: $0.03/GB/month
- At 5K logs/day * ~500 bytes/log = ~2.5 MB/day = ~75 MB/month = ~$0.04/month
- Extremely cheap at current scale

**Limitations:**

- CloudWatch Insights query language has a learning curve
- 5-second query latency (not real-time)
- Vendor lock-in to AWS

### 5.4 Option C: TimescaleDB

**Only if DZZLO adds PostgreSQL for other data.**

If PostgreSQL is adopted for financial data (Section 3), TimescaleDB is a free extension that converts a regular PostgreSQL table into a time-series hypertable:

```sql
CREATE TABLE api_logs (
  time TIMESTAMPTZ NOT NULL,
  method TEXT,
  url TEXT,
  api_version TEXT,
  response_time_ms DOUBLE PRECISION,
  status_code INTEGER,
  user_id TEXT,
  content_length INTEGER
);

-- Convert to hypertable (automatic time-based partitioning)
SELECT create_hypertable('api_logs', 'time');

-- Add compression policy (compress chunks older than 7 days)
ALTER TABLE api_logs SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'url,method'
);
SELECT add_compression_policy('api_logs', INTERVAL '7 days');

-- Add retention policy (delete data older than 90 days)
SELECT add_retention_policy('api_logs', INTERVAL '90 days');
```

### 5.5 Option D: InfluxDB

**Over-engineering for DZZLO's scale.** InfluxDB is purpose-built for metrics/monitoring at massive scale (millions of data points per second). At 5K logs/day, DZZLO is using roughly 0.06 writes/second. InfluxDB would be like buying a semi-truck to deliver a letter.

### 5.6 Recommendation

**Option A (MongoDB Time Series Collection)** is the clear winner:

- Zero new infrastructure
- Zero new dependencies
- 10-minute migration
- Immediate storage savings and query improvements
- TTL auto-expiration solves the "ever-growing logs" problem

Do Option A now. Consider Option B (CloudWatch) later if logs grow beyond 50K/day or if DZZLO wants log-based alerting.

---

## 6. Search Capabilities

### 6.1 What DZZLO Might Search


| Data                 | Search Type  | Current Approach                                      |
| -------------------- | ------------ | ----------------------------------------------------- |
| Customers by name    | Prefix/fuzzy | MongoDB `$regex` or `find({ cust_name: /pattern/i })` |
| Orders by order_no   | Exact        | `findOne({ order_no: 12345 })`                        |
| Invoices by inv_no   | Exact/prefix | `find({ inv_no: /DZ400/ })`                           |
| Dealers by name/city | Prefix/fuzzy | MongoDB `$regex`                                      |
| Products by name     | Prefix       | MongoDB `$regex`                                      |


### 6.2 MongoDB Atlas Search

**Available on dedicated M10+ clusters (which DZZLO uses).**

Atlas Search uses Apache Lucene under the hood. It integrates directly into the aggregation pipeline via the `$search` stage.

```javascript
// Create a search index on the Atlas UI or via API
// Index name: "customer_search"
// Collection: cust_msts
// Fields: cust_name (string), cust_phone (string), city (string)

// Query with autocomplete
const results = await CustMst.aggregate([
  {
    $search: {
      index: "customer_search",
      compound: {
        should: [
          {
            autocomplete: {
              query: searchTerm,
              path: "cust_name",
              fuzzy: { maxEdits: 1 },
            },
          },
          {
            text: {
              query: searchTerm,
              path: "cust_phone",
            },
          },
        ],
      },
    },
  },
  { $limit: 20 },
  { $project: { cust_name: 1, cust_phone: 1, city: 1, score: { $meta: "searchScore" } } },
]);
```

**Pros:**

- No extra infrastructure
- Included with Atlas dedicated cluster (no extra charge for basic usage)
- Fuzzy matching, autocomplete, relevance scoring
- Same Mongoose connection

**Cons:**

- Slight latency overhead vs regular queries (~10-50ms more)
- Search indexes consume additional storage
- Not as feature-rich as dedicated Elasticsearch

### 6.3 Elasticsearch / OpenSearch

**Over-engineering for DZZLO.** With 120 businesses and a few thousand customers/invoices per business, MongoDB regex and Atlas Search cover all realistic search needs. Elasticsearch requires a separate cluster, operational management, and data synchronization.

### 6.4 Algolia

**Over-engineering and expensive.** Algolia is designed for customer-facing e-commerce search (autocomplete in a search bar). DZZLO's search is internal (dealers/customers searching their own data). Not worth the cost.

### 6.5 Recommendation

1. **Now:** MongoDB regex queries are fine for current scale
2. **If search needs grow:** Enable Atlas Search indexes on `cust_msts.cust_name`, `dealer_msts.dealer_name`, `invs.inv_no`. Zero infrastructure, 15 minutes to set up.
3. **Skip:** Elasticsearch, Algolia, OpenSearch

---

## 7. Polyglot Persistence Pattern

### 7.1 The Theory

"Use the right database for each type of data." Instead of forcing all data into one database, use specialized databases for specialized data types.

### 7.2 Ideal Architecture for DZZLO-OMS (Future State)

```
┌────────────────────────────────────────────────────────┐
│                  Node.js / Express API                   │
└─────┬──────────┬──────────┬──────────┬─────────────────┘
      │          │          │          │
      ▼          ▼          ▼          ▼
┌──────────┐ ┌────────┐ ┌───────┐ ┌──────────────────┐
│ MongoDB  │ │ Redis  │ │ Cloud │ │ PostgreSQL       │
│ Atlas    │ │        │ │ Watch │ │ (FUTURE, if      │
│          │ │        │ │ Logs  │ │  financial needs  │
│ - Orders │ │ Cache  │ │       │ │  outgrow MongoDB) │
│ - SOs    │ │ Rate   │ │ API   │ │                   │
│ - Invs   │ │ Limit  │ │ Logs  │ │ - Reporting views │
│ - Vocs   │ │ Jobs   │ │       │ │ - Financial       │
│ - DIP    │ │ PubSub │ │       │ │   aggregates      │
│ - Users  │ │        │ │       │ │                   │
│ - Masters│ │        │ │       │ │                   │
└──────────┘ └────────┘ └───────┘ └──────────────────┘
```

### 7.3 Realistic Architecture for DZZLO-OMS (Next 12 Months)

```
┌────────────────────────────────────────────────────────┐
│                  Node.js / Express API                   │
└─────┬──────────────────────────────┬───────────────────┘
      │                              │
      ▼                              ▼
┌──────────────────┐          ┌──────────┐
│ MongoDB Atlas    │          │ Redis    │
│                  │          │          │
│ - All business   │          │ - Cache  │
│   collections    │          │ - Rate   │
│ - DIP collections│          │   Limit  │
│ - Logs (as TS    │          │ - BullMQ │
│   collection)    │          │   Jobs   │
│ - Atlas Search   │          │          │
│   (if needed)    │          │          │
└──────────────────┘          └──────────┘
```

**This is the pragmatic path:**

- MongoDB stays as the primary database (avoid migration risk)
- Redis adds caching, rate limiting, and job queues (highest ROI)
- Logs converted to time-series collection (within existing MongoDB)
- Atlas Search enabled if search needs grow (within existing Atlas)
- PostgreSQL deferred until there is a compelling financial/reporting need

### 7.4 When to Add PostgreSQL

Add PostgreSQL when any of these become true:

- DZZLO builds a formal accounting module (ledger, trial balance, P&L)
- Financial auditors require database-level referential integrity
- Reporting queries become a performance bottleneck
- DZZLO scales to 500+ businesses with complex cross-business analytics
- A BI/analytics tool (Metabase, Superset) is added that prefers SQL

---

## 8. MongoDB Atlas Features Being Underused

DZZLO is on a dedicated Atlas plan. Several features are available but not being used:

### 8.1 Time Series Collections

**Status:** Not used. The `logs` collection is a standard collection.
**Action:** Convert to time-series collection (see Section 5).
**Effort:** Low (1-2 hours).

### 8.2 Atlas Search

**Status:** Not used. Searches likely use `$regex` or exact match.
**Action:** Create search indexes on customer names, invoice numbers, product names.
**Effort:** Low (30 minutes to create indexes, 1-2 hours to integrate `$search` into endpoints).
**Available on:** M10+ dedicated clusters.

### 8.3 Atlas Charts

**Status:** Not used (likely).
**What it does:** Embedded dashboards and charts directly from MongoDB data. No BI tool needed.
**Use cases for DZZLO:**

- Daily order volume dashboard
- Revenue per dealer chart
- Payment outstanding trends
- Response time monitoring from logs
**Available on:** All Atlas clusters.
**Cost:** Free for basic usage (included with Atlas).

### 8.4 Atlas Data Federation

**Status:** Not used.
**What it does:** Query data across Atlas clusters, S3 buckets, and HTTP endpoints using the MongoDB query language.
**Use case:** If logs are archived to S3, Data Federation can query both live MongoDB data and archived S3 data seamlessly.
**Available on:** Dedicated clusters.

### 8.5 Online Archive

**Status:** Not used.
**What it does:** Automatically moves infrequently-accessed data (e.g., old logs, old orders) to cheaper cloud object storage. Data remains queryable through the standard MongoDB connection.
**Use case:** Archive logs older than 90 days, old completed orders older than 1 year.
**Cost:** $0.25/GB/month for archived data (vs ~$0.50-1.50/GB for hot storage on Atlas).
**Available on:** M10+ dedicated clusters.

### 8.6 Schema Validation

**Status:** Partially used (Mongoose validation, but not MongoDB-level).
**What it does:** JSON Schema validation at the database level. Even if application code has a bug, the database rejects invalid documents.

```javascript
// Apply via MongoDB shell or admin script
db.runCommand({
  collMod: "invs",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["dealer_id", "cust_id", "inv_no", "inv_total_amt"],
      properties: {
        inv_total_amt: {
          bsonType: "decimal",  // enforce Decimal128
          description: "must be a decimal and is required"
        },
        inv_status: {
          enum: ["UNPAID", "PARTPAID", "FULLPAID", "UNAPPROVED"],
          description: "must be a valid status"
        }
      }
    }
  },
  validationLevel: "moderate"  // only validate inserts and updates
});
```

### 8.7 Atlas Triggers (Realm/App Services)

**Status:** Not used.
**What it does:** Serverless functions triggered by database changes (insert, update, delete) or on a schedule (cron).
**Use cases:**

- Send notification when invoice is created
- Calculate monthly summary on the 1st of each month
- Alert when balance exceeds credit limit
**Note:** Atlas Triggers / App Services are being evolved; check current Atlas documentation for exact feature availability.

### 8.8 Recommendations for Atlas Features


| Feature                               | Priority | Effort    | Impact                                 |
| ------------------------------------- | -------- | --------- | -------------------------------------- |
| Time Series Collections (logs)        | HIGH     | 2 hours   | Storage savings, faster log queries    |
| Schema Validation (financial fields)  | HIGH     | 2 hours   | Data integrity                         |
| Online Archive (old logs, old orders) | MEDIUM   | 1 hour    | Storage cost savings                   |
| Atlas Charts                          | MEDIUM   | 2-4 hours | Business visibility                    |
| Atlas Search                          | LOW      | 2 hours   | Better search UX                       |
| Data Federation                       | LOW      | --        | Only if using S3 archives              |
| Atlas Triggers                        | LOW      | --        | Alternative to BullMQ for simple tasks |


---

## 9. DynamoDB as an Alternative

### 9.1 DynamoDB Overview

DynamoDB is AWS's serverless key-value and document database. It auto-scales, requires no server management, and charges per read/write or on-demand.

### 9.2 Could It Replace Any MongoDB Collection?


| Collection            | DynamoDB Fit | Why/Why Not                                             |
| --------------------- | ------------ | ------------------------------------------------------- |
| `logs`                | GOOD         | Simple writes, time-based reads, TTL built-in           |
| `users`               | POOR         | Need flexible queries (by email, by phone, by co_id)    |
| `orders`              | POOR         | Embedded products, complex status queries, need lookups |
| `invs`                | POOR         | Complex aggregation, financial data, relational chain   |
| `dealer_custs`        | POOR         | Composite key, balance arrays, complex queries          |
| `sessions` (if added) | GOOD         | Simple key-value, TTL built-in                          |
| `rate_msts`           | MODERATE     | Simple reads by date + dealer + product                 |


### 9.3 DynamoDB for Logs

```javascript
// DynamoDB table design for API logs
// Partition key: api_version (e.g., "v2", "v3", "dip_v1")
// Sort key: timestamp (ISO string or epoch)
// TTL attribute: expireAt

const { DynamoDBClient, PutItemCommand, QueryCommand } = require("@aws-sdk/client-dynamodb");
const client = new DynamoDBClient({ region: "ap-south-1" });

// Write a log
await client.send(new PutItemCommand({
  TableName: "dzzlo_api_logs",
  Item: {
    api_version: { S: "v2" },
    timestamp: { S: new Date().toISOString() },
    method: { S: "GET" },
    url: { S: "/api/v2/order_msts" },
    status: { N: "200" },
    response_time: { N: "45" },
    expireAt: { N: String(Math.floor(Date.now() / 1000) + 90 * 86400) }, // 90 days TTL
  },
}));

// Query logs for the last hour
await client.send(new QueryCommand({
  TableName: "dzzlo_api_logs",
  KeyConditionExpression: "api_version = :v AND #ts > :since",
  ExpressionAttributeNames: { "#ts": "timestamp" },
  ExpressionAttributeValues: {
    ":v": { S: "v2" },
    ":since": { S: new Date(Date.now() - 3600000).toISOString() },
  },
}));
```

**Cost at DZZLO's scale:**

- 5K writes/day = 150K writes/month
- On-demand pricing: $1.25 per million write request units
- 150K writes/month = ~$0.19/month
- 25 GB free tier covers log storage easily
- Essentially free

**BUT:** MongoDB Time Series Collections achieve the same thing with zero new infrastructure and zero AWS SDK integration. DynamoDB would only make sense if DZZLO wanted to completely remove logs from MongoDB to reduce Atlas storage costs.

### 9.4 Verdict

DynamoDB is not worth adding for DZZLO-OMS. The benefits do not justify the added complexity of managing another database connection and learning the DynamoDB data modeling paradigm (partition keys, sort keys, GSIs). MongoDB Time Series covers the only viable use case (logs) with less effort.

---

## 10. Practical Recommendations for DZZLO-OMS

Given: 120 businesses, 130 orders/day, solo developer, production system, limited operational bandwidth.

### 10.1 Priority Tier 1: Do Now (This Month)

These are low-effort, high-impact changes that require no new infrastructure:

**1. Convert `logs` to MongoDB Time Series Collection**

- Effort: 2 hours
- Impact: Storage savings, faster time-range queries, automatic TTL cleanup
- Risk: Low (logs are non-critical data)
- See Section 5.2

**2. Switch financial fields to Decimal128**

- Effort: 3-4 hours (schema changes + test all financial endpoints)
- Impact: Eliminates floating-point precision bugs in invoice amounts
- Risk: Medium (test thoroughly, the `.toFixed(2)` setter needs removal)

```javascript
// Before (fragile)
inv_amt: {
  type: Number,
  set: function (v) {
    return (Math.round(v * 100) / 100).toFixed(2);
  },
},

// After (precise)
inv_amt: {
  type: mongoose.Schema.Types.Decimal128,
  get: (v) => v ? parseFloat(v.toString()) : null,  // convert for JSON
},
```

**3. Add MongoDB Schema Validation for financial collections**

- Effort: 2 hours
- Impact: Database-level enforcement of required fields and types
- Risk: Low (set `validationLevel: "moderate"` to only validate new writes)
- See Section 8.6

### 10.2 Priority Tier 2: Do Soon (This Quarter)

**4. Add Redis**

- Effort: 4-8 hours (install, configure, integrate rate-limiter + caching)
- Cost: $0/month if co-located on same EC2, $13/month for ElastiCache
- Impact: Fixes multi-instance rate limiting, reduces MongoDB read load, enables future job queues
- See Section 4

**5. Implement BullMQ for background jobs (requires Redis)**

- Effort: 8-12 hours
- Impact: Invoice PDF generation and email sending no longer block API responses
- See Section 4.4

**6. Enable Atlas Online Archive for old data**

- Effort: 1 hour (Atlas UI configuration)
- Impact: Reduce hot storage costs by archiving old logs and completed orders
- See Section 8.5

### 10.3 Priority Tier 3: Consider Later (Next 6-12 Months)

**7. Atlas Search for customer/order lookup**

- Effort: 2-4 hours
- When: When dealers complain about search accuracy, or when customer base exceeds 10K per dealer
- See Section 6

**8. Atlas Charts for business dashboards**

- Effort: 4-8 hours
- When: When DZZLO wants to offer dealers analytics/reporting features

### 10.4 Priority Tier 4: Future / If Needed

**9. PostgreSQL for financial reporting**

- Effort: 40-80 hours (schema design, data migration, dual-write setup, new query layer)
- When: When DZZLO adds accounting module, or when financial aggregation queries become a bottleneck
- See Section 3

**10. Polyglot persistence (MongoDB + PostgreSQL + Redis)**

- When: 500+ businesses, or when a dedicated analytics/BI layer is needed
- See Section 7

### 10.5 What NOT to Do (Over-Engineering)

At 130 orders/day and 120 businesses, the following would be over-engineering:

- **Do NOT add Elasticsearch.** Atlas Search or MongoDB regex handles all search needs.
- **Do NOT add Cassandra or ScyllaDB.** These are for millions of writes/second.
- **Do NOT add Neo4j.** The data model is hierarchical, not graph-like.
- **Do NOT add DynamoDB.** MongoDB Time Series handles logs better with less complexity.
- **Do NOT add InfluxDB.** Purpose-built for monitoring at massive scale.
- **Do NOT migrate to PostgreSQL as the primary database.** The migration risk and effort outweigh the benefits at current scale.
- **Do NOT adopt a microservices architecture.** The monolith is the right choice for a solo developer.

---

## 11. Multi-Database Architecture in Node.js

DZZLO already manages dual MongoDB connections. Here is how to extend this pattern.

### 11.1 Current Pattern (Dual MongoDB)

```javascript
// helpers/db_conn.js (existing)
const mongoose = require("mongoose");
const dbDefault = mongoose.connection;                    // OMS database
const db_dip = mongoose.createConnection(database_dip);   // DIP database
module.exports = { dbDefault, db_dip };
```

This works well. Models on the default connection use `mongoose.model()`. DIP models use `db_dip.model()`.

### 11.2 Adding Redis (ioredis)

```javascript
// helpers/redis.js
const Redis = require("ioredis");

let redis = null;

const connectRedis = () => {
  if (redis) return redis;

  redis = new Redis({
    host: process.env.REDIS_HOST || "127.0.0.1",
    port: parseInt(process.env.REDIS_PORT) || 6379,
    password: process.env.REDIS_PASSWORD || undefined,
    retryStrategy: (times) => Math.min(times * 50, 2000),
    maxRetriesPerRequest: 3,
    lazyConnect: true,
  });

  redis.on("connect", () => console.log("REDIS CONNECTED"));
  redis.on("error", (err) => console.error("Redis Error:", err.message));

  return redis;
};

// Graceful shutdown
process.on("SIGINT", async () => {
  if (redis) {
    await redis.quit();
    console.log("Redis connection closed.");
  }
});

module.exports = { connectRedis, getRedis: () => redis };
```

```javascript
// In dzzlo_oms.js
const { connectRedis } = require("./helpers/redis");
const redis = connectRedis();
redis.connect().catch(console.error);
```

### 11.3 Adding PostgreSQL (if needed in the future)

**Option A: pg (raw SQL) -- lightest weight**

```javascript
// helpers/pg.js
const { Pool } = require("pg");

const pool = new Pool({
  connectionString: process.env.PG_DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
});

pool.on("connect", () => console.log("POSTGRESQL CONNECTED"));
pool.on("error", (err) => console.error("PG Pool Error:", err.message));

// Graceful shutdown
process.on("SIGINT", async () => {
  await pool.end();
  console.log("PostgreSQL pool closed.");
});

module.exports = pool;
```

```javascript
// Usage in a service
const pg = require("../helpers/pg");

exports.getBalance = async (dealerId, custId) => {
  const { rows } = await pg.query(
    `SELECT current_balance FROM current_balances
     WHERE dealer_id = $1 AND cust_id = $2`,
    [dealerId, custId]
  );
  return rows[0]?.current_balance ?? 0;
};
```

**Option B: Knex.js (query builder) -- moderate abstraction**

```javascript
// helpers/pg.js
const knex = require("knex")({
  client: "pg",
  connection: process.env.PG_DATABASE_URL,
  pool: { min: 2, max: 10 },
  migrations: { directory: "./migrations" },
});

module.exports = knex;
```

```javascript
// Usage
const knex = require("../helpers/pg");

exports.getBalance = async (dealerId, custId) => {
  const [row] = await knex("current_balances")
    .where({ dealer_id: dealerId, cust_id: custId })
    .select("current_balance");
  return row?.current_balance ?? 0;
};
```

**Option C: Prisma (ORM) -- heaviest, best DX**

```prisma
// prisma/schema.prisma
datasource db {
  provider = "postgresql"
  url      = env("PG_DATABASE_URL")
}

model Invoice {
  id         String   @id @default(uuid())
  dealerId   String   @map("dealer_id")
  custId     String   @map("cust_id")
  invNo      String   @map("inv_no")
  invAmt     Decimal  @map("inv_amt") @db.Decimal(12, 2)
  invStatus  String   @map("inv_status")
  createdAt  DateTime @default(now()) @map("created_at")

  dealer     Dealer   @relation(fields: [dealerId], references: [id])
  customer   Customer @relation(fields: [custId], references: [id])
  vouchers   Voucher[]

  @@map("invs")
}
```

**Recommendation:** If PostgreSQL is added, start with raw `pg` or Knex.js. Prisma adds significant overhead (code generation, migration management, schema duplication) and is overkill for a focused reporting layer.

### 11.4 Connection Management Architecture

```javascript
// helpers/connections.js -- unified connection management
const mongoose = require("mongoose");
const Redis = require("ioredis");
// const { Pool } = require("pg");  // uncomment when adding PostgreSQL

const connections = {
  mongo: null,
  mongoDip: null,
  redis: null,
  // pg: null,
};

exports.connectAll = async () => {
  // MongoDB (default)
  await mongoose.connect(process.env.DATABASE_URI);
  connections.mongo = mongoose.connection;
  console.log("MongoDB OMS connected");

  // MongoDB (DIP)
  connections.mongoDip = mongoose.createConnection(process.env.DATABASE_DIP);
  console.log("MongoDB DIP connected");

  // Redis
  connections.redis = new Redis({
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT,
    password: process.env.REDIS_PASSWORD,
    lazyConnect: true,
  });
  await connections.redis.connect();
  console.log("Redis connected");

  // PostgreSQL (future)
  // connections.pg = new Pool({ connectionString: process.env.PG_DATABASE_URL });
  // await connections.pg.query("SELECT 1");
  // console.log("PostgreSQL connected");
};

exports.disconnectAll = async () => {
  await mongoose.disconnect();
  if (connections.mongoDip) await connections.mongoDip.close();
  if (connections.redis) await connections.redis.quit();
  // if (connections.pg) await connections.pg.end();
  console.log("All database connections closed.");
};

exports.getConnection = (name) => connections[name];
```

---

## 12. Data Migration Strategies

### 12.1 Migrating Logs to MongoDB Time Series

This is the most likely near-term migration.

**Strategy: Create New Collection, Copy Data, Swap Names**

```javascript
// scripts/migrate-logs-to-timeseries.js
const mongoose = require("mongoose");

async function migrateLogs() {
  await mongoose.connect(process.env.DATABASE_URI);
  const db = mongoose.connection.db;

  // Step 1: Create time-series collection
  await db.createCollection("logs_ts", {
    timeseries: {
      timeField: "createdAt",
      metaField: "meta",
      granularity: "minutes",
    },
    expireAfterSeconds: 90 * 86400, // 90 days
  });

  console.log("Time-series collection created");

  // Step 2: Transform and copy data in batches
  const oldLogs = db.collection("logs");
  const newLogs = db.collection("logs_ts");
  const batchSize = 5000;
  let processed = 0;

  const cursor = oldLogs.find({}).batchSize(batchSize);

  let batch = [];
  for await (const doc of cursor) {
    batch.push({
      createdAt: doc.createdAt || new Date(),
      meta: {
        method: doc.method,
        url: doc.url,
        api_v: doc.api_v,
      },
      response_time: doc.response_time,
      status: doc.status,
      statusMessage: doc.statusMessage,
      content_str_length: doc.content_str_length,
      user: doc.user,
      appInfo: doc.appInfo,
    });

    if (batch.length >= batchSize) {
      await newLogs.insertMany(batch);
      processed += batch.length;
      console.log(`Migrated ${processed} documents`);
      batch = [];
    }
  }

  if (batch.length > 0) {
    await newLogs.insertMany(batch);
    processed += batch.length;
  }

  console.log(`Migration complete: ${processed} documents`);

  // Step 3: Rename collections (do this during maintenance window)
  // await db.collection("logs").rename("logs_old");
  // await db.collection("logs_ts").rename("logs");

  await mongoose.disconnect();
}

migrateLogs().catch(console.error);
```

**Rollback:** Keep `logs_old` for 30 days. If issues arise, rename back.

### 12.2 Migrating Financial Fields to Decimal128

**Strategy: In-Place Update with Script**

```javascript
// scripts/migrate-decimal128.js
const mongoose = require("mongoose");
const { Decimal128 } = mongoose.Types;

async function migrateToDecimal128() {
  await mongoose.connect(process.env.DATABASE_URI);
  const db = mongoose.connection.db;

  const collections = ["invs", "so_msts", "dealer_custs"];
  const decimalFields = {
    invs: ["inv_amt", "inv_disc_amt", "inv_tcs_amt", "inv_round_amt", "inv_total_amt", "disc_products_amt"],
    so_msts: [],  // products.rate is embedded
    dealer_custs: [],  // cust_bal.bal_value is embedded
  };

  for (const collName of collections) {
    const coll = db.collection(collName);
    const fields = decimalFields[collName];

    if (fields.length === 0) continue;

    const updateOps = {};
    fields.forEach((field) => {
      // This requires iterating and converting -- no bulk $convert in standard updates
    });

    // Use aggregation pipeline update (MongoDB 4.2+)
    const setStage = {};
    fields.forEach((field) => {
      setStage[field] = {
        $convert: {
          input: `$${field}`,
          to: "decimal",
          onError: Decimal128.fromString("0.00"),
          onNull: null,
        },
      };
    });

    const result = await coll.updateMany({}, [{ $set: setStage }]);
    console.log(`${collName}: updated ${result.modifiedCount} documents`);
  }

  await mongoose.disconnect();
}

migrateToDecimal128().catch(console.error);
```

**Important:** After running the migration script, update the Mongoose schemas to use `Decimal128` type and remove the `.toFixed(2)` setters. Test all financial endpoints thoroughly.

### 12.3 Migrating Data to PostgreSQL (If/When Needed)

This is a major undertaking. Here is the general strategy:

**Phase 1: Schema Design (1-2 weeks)**

- Design PostgreSQL schema for financial tables (invs, voc_msts, so_msts, dealer_custs)
- Create migration scripts (using Knex migrations or raw SQL)
- Set up the PostgreSQL instance

**Phase 2: Dual-Write Pattern (2-4 weeks)**

- Modify write operations to write to BOTH MongoDB AND PostgreSQL
- MongoDB remains the source of truth
- PostgreSQL receives copies for validation

```javascript
// Example dual-write pattern
exports.createInvoice = async (invoiceData) => {
  const session = await mongoose.startSession();
  session.startTransaction();

  try {
    // Write to MongoDB (source of truth)
    const invoice = await Inv.create([invoiceData], { session });

    // Write to PostgreSQL (copy for validation)
    try {
      await pg.query(
        `INSERT INTO invs (id, dealer_id, cust_id, inv_no, inv_total_amt, inv_status, created_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7)`,
        [invoice[0]._id.toString(), invoiceData.dealer_id, invoiceData.cust_id,
         invoiceData.inv_no, invoiceData.inv_total_amt, invoiceData.inv_status, new Date()]
      );
    } catch (pgError) {
      console.error("PG dual-write failed (non-fatal):", pgError.message);
      // Log but don't fail the MongoDB transaction
    }

    await session.commitTransaction();
    return invoice[0];
  } catch (error) {
    await session.abortTransaction();
    throw error;
  } finally {
    session.endSession();
  }
};
```

**Phase 3: Validation (1-2 weeks)**

- Compare data between MongoDB and PostgreSQL periodically
- Run reconciliation scripts to find discrepancies
- Fix any dual-write bugs

**Phase 4: Cutover for Reads (1 week)**

- Point reporting/analytics queries to PostgreSQL
- Point balance calculations to PostgreSQL views
- MongoDB remains source of truth for writes

**Phase 5: Full Migration (optional, much later)**

- Point all reads to PostgreSQL
- Make PostgreSQL the source of truth for financial data
- Keep MongoDB for non-financial data (orders, DIP, users, masters)

**Warning:** This is a 2-3 month project for a solo developer. Only undertake it if there is a clear business reason (accounting module, regulatory requirement, severe performance issues with MongoDB aggregations).

### 12.4 MongoDB to PostgreSQL Data Transfer

**Tool option: MongoDB Relational Migrator**
MongoDB provides a free tool that helps design the relational schema from MongoDB documents and automates data migration. It can generate SQL DDL, map MongoDB fields to columns, and handle embedded arrays (normalizing them into child tables).

**URL:** [https://www.mongodb.com/docs/relational-migrator/](https://www.mongodb.com/docs/relational-migrator/)

**Manual approach:**

```javascript
// scripts/sync-to-postgres.js
const mongoose = require("mongoose");
const { Pool } = require("pg");

const mongo = mongoose.connect(process.env.DATABASE_URI);
const pg = new Pool({ connectionString: process.env.PG_DATABASE_URL });

async function syncInvoices() {
  const Inv = require("../models/invs");
  const invoices = await Inv.find({}).lean();

  for (const inv of invoices) {
    await pg.query(
      `INSERT INTO invs (id, dealer_id, cust_id, inv_no, inv_amt, inv_total_amt, inv_status, inv_dt, created_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
       ON CONFLICT (id) DO UPDATE SET
         inv_status = EXCLUDED.inv_status,
         inv_total_amt = EXCLUDED.inv_total_amt`,
      [
        inv._id.toString(),
        inv.dealer_id?.toString(),
        inv.cust_id?.toString(),
        inv.inv_no,
        parseFloat(inv.inv_amt || 0),
        parseFloat(inv.inv_total_amt || 0),
        inv.inv_status,
        inv.inv_dt,
        inv.createdAt,
      ]
    );
  }

  console.log(`Synced ${invoices.length} invoices to PostgreSQL`);
}
```

---

## Appendix: Key Documentation Links


| Technology                   | Documentation                                                                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| MongoDB Manual               | [https://www.mongodb.com/docs/manual/](https://www.mongodb.com/docs/manual/)                                                                 |
| MongoDB Time Series          | [https://www.mongodb.com/docs/manual/core/timeseries-collections/](https://www.mongodb.com/docs/manual/core/timeseries-collections/)         |
| MongoDB Atlas Search         | [https://www.mongodb.com/docs/atlas/atlas-search/](https://www.mongodb.com/docs/atlas/atlas-search/)                                         |
| MongoDB Atlas Online Archive | [https://www.mongodb.com/docs/atlas/online-archive/](https://www.mongodb.com/docs/atlas/online-archive/)                                     |
| MongoDB Schema Validation    | [https://www.mongodb.com/docs/manual/core/schema-validation/](https://www.mongodb.com/docs/manual/core/schema-validation/)                   |
| MongoDB Decimal128           | [https://www.mongodb.com/docs/manual/reference/bson-types/#decimal128](https://www.mongodb.com/docs/manual/reference/bson-types/#decimal128) |
| Mongoose Decimal128          | [https://mongoosejs.com/docs/api/schema.html#Schema.Types.Decimal128](https://mongoosejs.com/docs/api/schema.html#Schema.Types.Decimal128)   |
| Redis Documentation          | [https://redis.io/docs/latest/](https://redis.io/docs/latest/)                                                                               |
| ioredis (Node.js client)     | [https://github.com/redis/ioredis](https://github.com/redis/ioredis)                                                                         |
| BullMQ                       | [https://docs.bullmq.io/](https://docs.bullmq.io/)                                                                                           |
| rate-limit-redis             | [https://www.npmjs.com/package/rate-limit-redis](https://www.npmjs.com/package/rate-limit-redis)                                             |
| connect-redis (sessions)     | [https://www.npmjs.com/package/connect-redis](https://www.npmjs.com/package/connect-redis)                                                   |
| PostgreSQL Documentation     | [https://www.postgresql.org/docs/current/](https://www.postgresql.org/docs/current/)                                                         |
| Knex.js (query builder)      | [https://knexjs.org/guide/](https://knexjs.org/guide/)                                                                                       |
| Prisma (ORM)                 | [https://www.prisma.io/docs/](https://www.prisma.io/docs/)                                                                                   |
| pg (Node.js PostgreSQL)      | [https://node-postgres.com/](https://node-postgres.com/)                                                                                     |
| TimescaleDB                  | [https://docs.timescale.com/](https://docs.timescale.com/)                                                                                   |
| MongoDB Relational Migrator  | [https://www.mongodb.com/docs/relational-migrator/](https://www.mongodb.com/docs/relational-migrator/)                                       |
| AWS ElastiCache Redis        | [https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/)                 |
| AWS DynamoDB                 | [https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/)       |
| AWS CloudWatch Logs          | [https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/)                       |


---

## Appendix: Cost Summary at DZZLO's Scale


| Service                            | Monthly Cost | What It Provides                     |
| ---------------------------------- | ------------ | ------------------------------------ |
| MongoDB Atlas (current, dedicated) | ~$57+ (M10)  | Primary database                     |
| Redis (same EC2)                   | $0           | Caching, rate limiting, job queue    |
| Redis (ElastiCache t3.micro)       | ~$13         | Managed Redis if multi-instance      |
| Redis (Upstash serverless)         | ~$0-5        | If usage is light                    |
| PostgreSQL (RDS t3.micro)          | ~$15-30      | Financial reporting (future)         |
| CloudWatch Logs                    | ~$0.04       | Log storage (alternative to MongoDB) |
| DynamoDB (logs)                    | ~$0.19       | Log storage (not recommended)        |
| Atlas Search                       | $0           | Included with dedicated cluster      |
| Atlas Online Archive               | ~$0.25/GB    | Archived data storage                |
| Atlas Charts                       | $0           | Basic dashboards included            |


**Total recommended addition:** Redis on same EC2 = $0/month. Everything else can wait.