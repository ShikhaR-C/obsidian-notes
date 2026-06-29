# Database Optimization

> Index improvements and query structure changes. Each task is independent.
> Run `explain("executionStats")` before and after each index change to verify impact.

---

## DB-1: Add compound index on `dealer_custs` (API — Mongo)

**Size:** XS (1 line in model file + verify)
**File:** `models/dealer_custs.js`

**What:** Add `dealer_cust__mst_Schema.index({ dealer_id: 1, cust_id: 1 }, { unique: true })`.

Currently there are separate single-field indexes on `cust_id` and `dealer_id`. Queries like `DealerCustomer.findOne({ cust_id, dealer_id })` can't use a single efficient index.

**Why:** This collection is hit on nearly every order operation — create, process, list enrichment. A compound index means MongoDB scans the index once instead of intersecting two indexes (which is always slower). The `unique: true` also prevents duplicate dealer-customer pairs.

**How to verify:**

- Run `db.dealer_custs.find({ dealer_id: ObjectId("..."), cust_id: ObjectId("...") }).explain("executionStats")` — should show `IXSCAN`, not `COLLSCAN`.
- App: No change needed. Same queries, faster results.

**Discussion:** The compound index covers queries on `dealer_id` alone (leftmost prefix rule) AND `{dealer_id, cust_id}` together. You can remove the separate `dealer_id: 1` index after adding this.

---

## DB-2: Add compound index on `invs` for balance calculation (API — Mongo)

**Size:** XS (1 line)
**File:** `models/invs.js`

**What:** Add `invSchema.index({ dealer_id: 1, cust_id: 1, inv_dt: -1 })`.

**Why:** `currentInvoiceBalance()` queries `invs` by `{dealer_id, cust_id, inv_dt: {$gte, $lte}}`. Without this index, MongoDB scans the entire collection. The ESR rule (Equality-Sort-Range) puts `dealer_id` and `cust_id` first (equality), then `inv_dt` (range).

**How to verify:**

- Run explain on the balance query. Should show IXSCAN.
- App: Balance calculations return faster.

---

## DB-3: Add compound index on `voc_msts` (API — Mongo)

**Size:** XS (1 line)
**File:** `models/voc_msts.js`

**What:** Add `voc_mst_Schema.index({ dealer_id: 1, cust_id: 1, pay_status: 1, pay_dt: -1 })`.

**Why:** Same reason as DB-2 — `currentInvoiceBalance()` also queries vouchers by `{dealer_id, cust_id, pay_status: true, pay_dt}`. This is part of the credit limit check during order creation.

---

## DB-4: Add compound index on `order_msts` for status queries (API — Mongo)

**Size:** XS (1 line)
**File:** `models/order_msts.js`

**What:** Add `order_mst_Schema.index({ dealer_id: 1, cust_id: 1, order_status: 1, createdAt: -1 })`.

**Why:** `currentOrderOutstanding()` queries by `{dealer_id, cust_id, order_status: {$in: ["PENDING", "PROCESSING"]}}`. Also, order list queries filter by dealer/customer + status + sort by date. One compound index serves both patterns.

**How to verify:**

- Check Atlas Performance Advisor — this index should match or improve on its suggestions.

---

## DB-5: Add TTL index on `logs` collection (API — Mongo)

**Size:** XS (1 command in mongosh)
**File:** `models/logs.js` (or run directly in mongosh)

**What:** `db.logs.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 7776000 })` (90 days).

**Why:** The `logs` collection has 1.4M+ records and grows ~5K docs/day with no cleanup strategy. Old logs are never queried. TTL auto-deletes docs older than 90 days, preventing unbounded growth.

**Important:** If a non-TTL index on `createdAt` already exists, drop it first. The first run will delete ~1M+ old docs — do this during off-hours.

**How to verify:**

- Run `db.logs.countDocuments()` before and after (after waiting for the background thread).
- App: No impact — logs are write-only from the app's perspective.

**Discussion:** This is one of the highest-impact database maintenance tasks. Unbounded collection growth degrades query performance across the entire database, not just the logs collection.

---

## DB-6: Add TTL index on `errors` collection (API — Mongo)

**Size:** XS (1 command)

**What:** `db.errors.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 2592000 })` (30 days).

**Why:** Same as DB-5. The errors collection grows without bounds. Error data older than 30 days has no diagnostic value.

---

## DB-7: Add `.select()` to queries missing field projection (API)

**Size:** S (audit + add selects)
**Files:** `api_v3/services/order_msts.js` (lines 509, 550, 811, 908, 1024)

**What:** Add `.select()` to queries that currently return all fields when only a few are needed.

| Line | Query                                    | Fix                                                                        |
| ---- | ---------------------------------------- | -------------------------------------------------------------------------- |
| 509  | `OrderMaster.findOne({ _id: body._id })` | `.select('order_no order_status products cust_id dealer_id veh_id so_id')` |
| 550  | `DriverMaster.findOne({ veh_id })`       | `.select('name phone code email')`                                         |
| 811  | `OrderMaster.findById(id)`               | `.select()` with needed fields                                             |

**Why:** Without `.select()`, MongoDB returns all document fields including embedded arrays, history, etc. Field projection reduces:

- Data transferred over the network (10-30% reduction)
- Memory usage on the Node.js side
- Serialization time

**How to verify:**

- API: Response should contain the same data (only the fields the code actually uses).
- App: No change — the enrichment/mapping code only reads specific fields anyway.

---

## DB-8: Combine `countDocuments` + `find` into `$facet` in advancedResults (API)

**Size:** M (careful refactor of shared pagination helper)
**File:** `helpers/advancedResults.js`

**What:** Replace the 2-query pagination pattern (line 87: `countDocuments` + line 105: `find`) with a single `$facet` aggregation.

**Why:** Every paginated endpoint makes 2 DB roundtrips — one to count total docs, one to fetch the page. `$facet` does both in a single query, cutting pagination overhead in half (~15-30ms saved per paginated request, affecting 15+ endpoints).

**Caveat:** `$facet` doesn't use indexes for `$sort` inside the facet. The `$match` must come BEFORE `$facet`. If `populate` is needed, either use `$lookup` in the pipeline or fall back to the 2-query approach.

**How to verify:**

- API: Test every paginated endpoint. Response shape (count, pagination, data) must be identical.
- App: Pagination behavior (next/prev pages) must work identically.

**Discussion:** This is the most impactful but also highest-risk DB task. The `advancedResults` helper is used by many endpoints. Test thoroughly. Consider doing it behind a feature flag or as a new function that can be swapped in per-endpoint.

---

## Summary

| Task                                | Size | Impact                           | Risk                         |
| ----------------------------------- | ---- | -------------------------------- | ---------------------------- |
| DB-1: `dealer_custs` compound index | XS   | High — hit on every order op     | Zero — additive              |
| DB-2: `invs` compound index         | XS   | Medium — balance checks          | Zero — additive              |
| DB-3: `voc_msts` compound index     | XS   | Medium — balance checks          | Zero — additive              |
| DB-4: `order_msts` status index     | XS   | High — order list + outstanding  | Zero — additive              |
| DB-5: TTL on `logs`                 | XS   | High — prevents unbounded growth | Low — deletes old data       |
| DB-6: TTL on `errors`               | XS   | Medium — same pattern            | Low — deletes old data       |
| DB-7: Add `.select()`               | S    | Medium — less data transferred   | Low — verify all fields used |
| DB-8: `$facet` pagination           | M    | High — halves pagination queries | Medium — shared helper       |
