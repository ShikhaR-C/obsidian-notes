# Database Optimization

> Index improvements and query structure changes. Each task is independent.
> Run `explain("executionStats")` before and after each index change to verify impact.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). DB-1…4 and DB-7 are done (5 ✅); DB-5 is deferred inside API-5 (⏸); DB-6 and DB-8 are still to do (2 ⬜). The v4 work declared four more named indexes for its screens; whether they were built on Atlas, and whether API 1.5.5 is deployed, cannot be seen from the repos (`X-REL-2` below). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## DB-1: Add compound index on `dealer_custs` (API — Mongo)

**Status (2026-10-01):** ✅ done — `90f052f`; `{ dealer_id: 1, cust_id: 1 }` unique at `models/dealer_custs.js:123`, the index v4's `assertRelation` walks (`api_v4/lib/tenancy.js:121-138`). The optional drop of the single-field `dealer_id` index was not taken (`:122`).

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

**Status (2026-10-01):** ✅ done — `90f052f`; `{ dealer_id: 1, cust_id: 1, inv_dt: -1 }` at `models/invs.js:122`.

**Size:** XS (1 line)
**File:** `models/invs.js`

**What:** Add `invSchema.index({ dealer_id: 1, cust_id: 1, inv_dt: -1 })`.

**Why:** `currentInvoiceBalance()` queries `invs` by `{dealer_id, cust_id, inv_dt: {$gte, $lte}}`. Without this index, MongoDB scans the entire collection. The ESR rule (Equality-Sort-Range) puts `dealer_id` and `cust_id` first (equality), then `inv_dt` (range).

**How to verify:**

- Run explain on the balance query. Should show IXSCAN.
- App: Balance calculations return faster.

---

## DB-3: Add compound index on `voc_msts` (API — Mongo)

**Status (2026-10-01):** ✅ done — `90f052f`; `{ dealer_id: 1, cust_id: 1, pay_status: 1, pay_dt: -1 }` at `models/voc_msts.js:85`.

**Size:** XS (1 line)
**File:** `models/voc_msts.js`

**What:** Add `voc_mst_Schema.index({ dealer_id: 1, cust_id: 1, pay_status: 1, pay_dt: -1 })`.

**Why:** Same reason as DB-2 — `currentInvoiceBalance()` also queries vouchers by `{dealer_id, cust_id, pay_status: true, pay_dt}`. This is part of the credit limit check during order creation.

---

## DB-4: Add compound index on `order_msts` for status queries (API — Mongo)

**Status (2026-10-01):** ✅ done — `90f052f`; `{ dealer_id: 1, cust_id: 1, order_status: 1, createdAt: -1 }` at `models/order_msts.js:73`. v4's Customers open-order read walks it (`docs/v4-performance.md:194-203`); the Daily Summary Purchase tab got its own `v4_dealer_cust_status_ondt` (`:82-85`).

**Size:** XS (1 line)
**File:** `models/order_msts.js`

**What:** Add `order_mst_Schema.index({ dealer_id: 1, cust_id: 1, order_status: 1, createdAt: -1 })`.

**Why:** `currentOrderOutstanding()` queries by `{dealer_id, cust_id, order_status: {$in: ["PENDING", "PROCESSING"]}}`. Also, order list queries filter by dealer/customer + status + sort by date. One compound index serves both patterns.

**How to verify:**

- Check Atlas Performance Advisor — this index should match or improve on its suggestions.

---

## DB-5: Add TTL index on `logs` collection (API — Mongo)

**Status (2026-10-01):** ⏸ deferred — no TTL anywhere in code (`models/logs.js` declares no index); the `logs` TTL is part of API-5 (slim rows + TTL), which the user deferred on 2026-09-21 — `X-PERF-2` in [04](./04-api-query-performance.md). A TTL built by hand on Atlas is ❔ (`db.logs.getIndexes()` tells).

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

**Status (2026-10-01):** ⬜ to do — `models/errors.js` declares no index (the schema has `timestamps: true`, so `createdAt` exists); not part of API-5. A TTL built by hand on Atlas is ❔.

**Size:** XS (1 command)

**What:** `db.errors.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 2592000 })` (30 days).

**Why:** Same as DB-5. The errors collection grows without bounds. Error data older than 30 days has no diagnostic value.

---

## DB-7: Add `.select()` to queries missing field projection (API)

**Status (2026-10-01):** ✅ done — `03b8bbf` (2026-04-14) and `1656f16`; every model read in `api_v3/services/order_msts.js` now projects (the lines below have moved). Per-file counts at master are in [09](./09-select-projection-audit.md): 330 of 378 reads in the audited files.

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

**Status (2026-10-01):** ⬜ to do — `getResults` still counts, then runs `find().skip().limit()` (`helpers/advancedResults.js:88,106`), for 25 v3 callers; v4 does neither — a keyset cursor that never counts (`api_v4/lib/cursor.js`). A missing `limit` means no limit — `T01-N3` below.

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

---

## New tasks — from the app v2 / API v4 review (2026-10-01)

**What v4 added here.** Four named indexes, declared in the models — `v4_dealer_cust_ondt` on `so_msts` (`models/so_msts.js:63-66`), `v4_dealer_cust_status_ondt` on `order_msts` (`models/order_msts.js:82-85`), `v4_dealer_cust_month` on `month_crdrs` (`models/month_crdrs.js:24-27`), `v4_dealer_category` on `prod_msts` (`models/prod_msts.js:38-41`) — and a mongosh script that builds them in that collection order, dry run by default (`scripts/perf/atlas-indexes.js`), held equal to the models by `test/api_v4/lib/indexes.test.js`. `autoIndex` is on, so a declaration that reaches production before its Atlas build is built by the app at start-up (`scripts/perf/atlas-indexes.js:3-7`). v4 pages with a keyset cursor and never counts (`api_v4/lib/cursor.js`).

| ID      | Task                                                                                                                                                                                                                                                            | Why (evidence)                                                                                                                                                                                                                                                                                                                                                                                                                                  | Project                              | Size | Depends on                                  |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ---- | ------------------------------------------- |
| X-REL-2 | 🆕 ❔ Deploy API 1.5.5 before app 1.79 reaches users, and build the four Atlas indexes first — with mongosh (`APPLY=1 mongosh "<uri>/<db>" --file scripts/perf/atlas-indexes.js`), not the `node …` commands the v1.5.5 release notes and the PR #43 body print | App 1.79 calls all five v4 routes (`src/store/apis/v4/{index,customers,daily_summary}.js`) and renders v2 whenever a toggle is absent (`src/navigation/screenRegistry.js:145-166`); the script acts only when a mongosh `db` exists (`scripts/perf/atlas-indexes.js:134-139`), so under `node` it silently does nothing; runbook `docs/v4-performance.md:313-403`. Deploy and Atlas state are not verifiable from the repos — the user confirms | API (+ app release order)            | S    | `X-REL-1` (tasks_12) — a green master first |
| T01-N3  | 🆕 Give `getResults` a default and a maximum `limit`                                                                                                                                                                                                            | A missing `limit` means no limit and a sent one has no cap (`helpers/advancedResults.js:49,106`), for all 25 v3 callers; at least one app list sends no `limit` (`src/store/apis/dzzlooms/dealer_msts.js`), so audit the callers first; v4 caps at 25 / 100 (`api_v4/lib/cursor.js:37-38`)                                                                                                                                                      | API (+ app: audit the callers first) | S    | —                                           |

Related: `X-PERF-2` in [04](./04-api-query-performance.md) holds API-5 (slim `logs` rows + the TTL that closes DB-5) and the measured-but-undeclared fifth index `so_msts { dealer_id, inv_id, gst_inv_id }`. The full list is in [00-overview](./00-overview.md).
