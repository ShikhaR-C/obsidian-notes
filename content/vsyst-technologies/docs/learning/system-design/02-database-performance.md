# Session 2: Database & MongoDB Performance

> Phase 1 — Foundations | 2 hours | Review: 15 min

## What You'll Learn

- How MongoDB schema design patterns affect query speed and storage cost
- Whether your existing compound indexes are actually being used
- How to read `explain()` output and spot full collection scans
- When a TTL index makes sense and how to add one safely
- The real trade-offs between SQL and NoSQL for an order management system

## Why This Matters for DZZLO-OMS

You have two MongoDB connections (OMS: 22 collections, DIP: 4 collections) running on Atlas dedicated. Your `logs` collection is at 1.4M records / 114 MB and growing ~5K docs/day with no TTL and no archival strategy — that is roughly 1.8M new docs per year piling up indefinitely. Your `order_msts` compound index covers five fields but you have never verified whether queries actually hit it. The Performance Advisor has been available since you moved to a dedicated plan, but it has never been checked. This session fixes all of that.

---

## Hour 1 — Concepts (60 min)

### Step 1: MongoDB Schema Design Patterns (30 min)

**Read:** [Building with Patterns: A Summary](https://www.mongodb.com/blog/post/building-with-patterns-a-summary)
**Reference:** [Official Data Modeling Patterns](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/)

Focus on three patterns and how they map to your data:


| Pattern                | What It Solves                    | Your Use Case                                                                                                                                                                                            |
| ---------------------- | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Subset**             | Embedding grows unbounded         | `cust_bal[]` is pushed ~1x/year, so it is fine now. But if balance entries ever become frequent, you would subset recent balances into the customer doc and archive the rest.                            |
| **Bucket**             | Too many small documents          | `logs` — 5K docs/day could be bucketed into hourly or daily summary docs for analytics while keeping raw docs for recent data only.                                                                      |
| **Extended Reference** | Frequent joins across collections | `order_msts` → `so_msts` → `invs` chain. Each lookup is a separate query. Embedding the customer name + dealer name directly into the order doc (extended reference) eliminates the most common lookups. |


**Exercise:** Open your `order_msts` schema. List every field that comes from a referenced collection (customer name, dealer name, etc.). For each one, decide: is the join worth it, or should you denormalize?

### Step 2: Indexing Deep Dive (15 min)

**Read:** [MongoDB Indexing Strategies](https://www.mongodb.com/docs/manual/applications/indexes/)

Key concepts to understand:

- **Compound index order matters.** Your `order_msts` index is `{cust_id, dealer_id, createdAt, order_status, on_dt}`. A query filtering only on `dealer_id` will NOT use this index efficiently because `dealer_id` is the second field. The index is only useful when the query includes `cust_id` as the first filter (leftmost prefix rule).
- **Covered queries** return results entirely from the index without touching the document. If your query only needs `cust_id` and `order_status`, and both are in the index, MongoDB can skip the document fetch.
- **Index intersection** lets MongoDB combine two single-field indexes, but it is almost always slower than one compound index that covers your query.

**Exercise:** Write down the three most common queries your API makes against `order_msts`. For each one, check whether the existing compound index supports it by applying the leftmost prefix rule.

### Step 3: SQL vs NoSQL Trade-offs (15 min)

**Read:** [System Design Primer — SQL or NoSQL](https://github.com/donnemartin/system-design-primer#sql-or-nosql)

Think about these questions for DZZLO-OMS:

- **Your polymorphic references:** `user.co_id` uses Mongoose `refPath` to point to different collections depending on user type. This is a pattern that is natural in MongoDB but would require joins or union types in SQL. It is a valid reason to stay on MongoDB.
- **Your `dealer_custs` composite `_id`:** `{dealer_id, cust_id}` as the `_id` field is a MongoDB-specific trick that gives you a unique constraint and a compound index for free. In SQL you would need a separate unique constraint.
- **Invoice numbering:** You moved to random IDs, which eliminated the auto-increment race condition. In SQL you would have used `SERIAL` or `AUTO_INCREMENT` with built-in atomicity. This is a case where SQL would have been simpler.
- **Where MongoDB hurts you:** Multi-collection transactions (order → sales order → invoice) are supported but slower than SQL transactions. If you ever need cross-collection consistency guarantees, this is the friction point.

**Exercise:** For each collection in your OMS DB, write one sentence on whether it benefits from being in MongoDB or would be simpler in SQL. You do not need to migrate anything — this is about understanding the trade-off for future decisions.

---

## Hour 2 — Hands-On with Your Database (60 min)

### Step 4: Atlas Performance Advisor (20 min)

**Docs:** [Performance Advisor](https://www.mongodb.com/docs/atlas/performance-advisor/) | [Analyze Slow Queries](https://www.mongodb.com/docs/atlas/analyze-slow-queries/)

Walk through these steps:

1. Log into Atlas → select your dedicated cluster
2. Click **Performance Advisor** in the left sidebar
3. Set the time range to the last 7 days
4. Look at two things:
  - **Suggested Indexes:** Atlas analyzes your query patterns and recommends indexes. Write down every suggestion. Do NOT create them yet — just record them.
  - **Slow Queries:** Any query taking >100ms is flagged. Note which collection and which operation (find, aggregate, update).
5. Click into the **Real-Time Performance** panel. Check the current read/write ratio and active connections.

**Record your findings.** You will use them in Step 5.

### Step 5: explain() Your Queries (20 min)

**Docs:** [Explain Results](https://www.mongodb.com/docs/manual/reference/explain-results/)

Connect to your Atlas cluster via `mongosh` or the Atlas Data Explorer shell. Run `explain("executionStats")` on your most common queries. Here are the specific ones to test:

**Query 1: Orders by dealer_id**

```javascript
db.order_msts.find({ dealer_id: ObjectId("YOUR_DEALER_ID") })
  .sort({ createdAt: -1 })
  .limit(20)
  .explain("executionStats")
```

Check `executionStats.executionStages.stage`. If it says `COLLSCAN`, the compound index is not being used for this query (expected — `dealer_id` is not the leftmost field).

**Query 2: Invoices by cust_id**

```javascript
db.invs.find({ cust_id: ObjectId("YOUR_CUST_ID") })
  .sort({ createdAt: -1 })
  .explain("executionStats")
```

Check whether `invs` has an index on `cust_id`. If not, this is a full collection scan every time a customer views their invoices.

**Query 3: Logs listing (most recent)**

```javascript
db.logs.find({})
  .sort({ createdAt: -1 })
  .limit(50)
  .explain("executionStats")
```

With 1.4M docs, this query should use the existing `createdAt` index. If `totalDocsExamined` is much larger than `nReturned`, something is wrong.

**What to look for in the output:**


| Field                   | Good Value           | Bad Value                    |
| ----------------------- | -------------------- | ---------------------------- |
| `executionStages.stage` | `IXSCAN`             | `COLLSCAN`                   |
| `totalKeysExamined`     | Close to `nReturned` | Much larger than `nReturned` |
| `totalDocsExamined`     | Close to `nReturned` | Much larger than `nReturned` |
| `executionTimeMillis`   | < 50ms               | > 200ms                      |


**Exercise:** Run all three queries. For each one, write down: (1) the stage type, (2) docs examined vs returned, (3) execution time. If any query is doing a COLLSCAN, note what index would fix it.

### Step 6: TTL Index Strategy (20 min)

**Docs:** [TTL Indexes](https://www.mongodb.com/docs/manual/core/index-ttl/) | [Expire Data Tutorial](https://www.mongodb.com/docs/manual/tutorial/expire-data/)

Your `logs` collection: 1.4M docs, 114 MB, growing at ~5K docs/day. At this rate:

- **In 1 year:** ~3.2M docs, ~260 MB
- **In 3 years:** ~6.9M docs, ~560 MB
- **Storage cost is low**, but query performance degrades as the collection grows, and none of this old data is being used.

**Decision framework for TTL:**


| Question                                          | Answer for `logs`                            |
| ------------------------------------------------- | -------------------------------------------- |
| Do you ever query logs older than 90 days?        | Probably not                                 |
| Is there a compliance requirement to keep them?   | No (internal operational logs)               |
| Would losing old logs cause any business problem? | No — orders/invoices are the source of truth |
| Does the collection have a `createdAt` field?     | Yes (Mongoose timestamps)                    |


If the answer to all four is what is shown above, a 90-day TTL makes sense.

**How TTL works:**

- MongoDB runs a background thread every 60 seconds that checks for expired documents
- It deletes documents where `createdAt + expireAfterSeconds < now`
- Deletions happen in small batches, so they do not block your application

**How to create the TTL index:**

```javascript
db.logs.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 7776000 })
```

`7776000` seconds = 90 days.

**WARNING:** If you already have a non-TTL index on `createdAt`, you must drop it first — MongoDB will not convert an existing index to a TTL index. And when you first create this TTL index, the background thread will immediately start deleting all documents older than 90 days. With 1.4M docs and ~5K/day growth, roughly **1M+ documents** could be deleted in the first pass. This is safe but generates load. **Do it during off hours.**

**Steps to apply:**

1. Check for existing index: `db.logs.getIndexes()`
2. If a non-TTL `createdAt` index exists: `db.logs.dropIndex("createdAt_1")` (or whatever the index name is)
3. Create the TTL index: `db.logs.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 7776000 })`
4. Verify: `db.logs.getIndexes()` — confirm the new index shows `expireAfterSeconds: 7776000`
5. Monitor: Check `db.logs.countDocuments()` over the next hour to see deletions happening

**Exercise:** Do steps 1 and 2 only (check and record current indexes). Do NOT create the TTL index yet if you are not in a maintenance window.

---

## 15-Minute Review

Answer these without looking back:

1. What is the leftmost prefix rule for compound indexes, and why does it mean your `order_msts` index does not help queries that filter only on `dealer_id`?
2. What does `COLLSCAN` in explain output mean, and why is it bad for a collection with 1M+ documents?
3. How often does the TTL background thread run, and what happens the first time you add a TTL index to a collection with a lot of expired data?
4. Name one schema pattern from Step 1 that you could apply to your `order_msts` → `so_msts` → `invs` chain and explain why.
5. Your `dealer_custs` uses `{dealer_id, cust_id}` as the `_id`. What two things does this give you for free?

**Concrete next steps:**

- Review Performance Advisor findings and decide which suggested indexes to create
- Fix any COLLSCAN queries found in Step 5 by adding targeted indexes
- Schedule a maintenance window to add the TTL index on `logs` (if you decided to proceed)
- Revisit the `order_msts` compound index — consider whether `dealer_id` should be the first field based on your actual query patterns

---

## Resources

**Schema Design:**

- [Building with Patterns: A Summary](https://www.mongodb.com/blog/post/building-with-patterns-a-summary)
- [Official Data Modeling Patterns](https://www.mongodb.com/docs/manual/data-modeling/design-patterns/)

**Indexing & Performance:**

- [MongoDB Indexing Strategies](https://www.mongodb.com/docs/manual/applications/indexes/)
- [Explain Results Reference](https://www.mongodb.com/docs/manual/reference/explain-results/)
- [Atlas Performance Advisor](https://www.mongodb.com/docs/atlas/performance-advisor/)
- [Analyze Slow Queries](https://www.mongodb.com/docs/atlas/analyze-slow-queries/)

**TTL & Data Lifecycle:**

- [TTL Indexes](https://www.mongodb.com/docs/manual/core/index-ttl/)
- [Expire Data Tutorial](https://www.mongodb.com/docs/manual/tutorial/expire-data/)

**SQL vs NoSQL:**

- [System Design Primer — SQL or NoSQL](https://github.com/donnemartin/system-design-primer#sql-or-nosql)

