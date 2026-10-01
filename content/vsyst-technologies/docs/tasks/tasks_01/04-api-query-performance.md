# API Query Performance

> Parallelize sequential DB calls and optimize enrichment loops.
> These are the highest-latency-impact changes. Each targets a specific endpoint.
> Do them one at a time. Test the specific endpoint + corresponding app screen after each.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). All six items are in `api_v3/services/order_msts.js` (5 ✅); AQP-1 is 🟡 because the second copy of `currentInvoiceBalance`, in `api_v3/services/dealer_custs.js`, still runs its two finds in series. Separately, the v4 performance work (API-0…3, API PR #43) took the Customers screen from 1,525 to 134 ms median on a 2,000-relation / 300,000-order seed (`docs/v4-performance.md:253`); what it left is deferred — `X-PERF-2` below. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## AQP-1: Parallelize `currentInvoiceBalance` — 2 independent queries (API)

**Status (2026-10-01):** 🟡 partly — `f9f1d26`; `currentInvoiceBalance` in `api_v3/services/order_msts.js:326` runs both finds in one `Promise.all` (`:331`); the copy in `api_v3/services/dealer_custs.js:379-415` (reached through `:1553`) still awaits them in series (`:384`, `:396`).

**Size:** XS (5 min)
**File:** `api_v3/services/order_msts.js`, lines 310-346

**What:** Wrap the `invs.find()` and `voc_msts.find()` calls in `Promise.all()`.

```js
// BEFORE: sequential
const Invoice = await invs.find({...}).select('inv_total_amt').lean();
const Vouchers = await voc_msts.find({...}).select('amount pay_type').lean();

// AFTER: parallel
const [Invoice, Vouchers] = await Promise.all([
  invs.find({...}).select('inv_total_amt').lean(),
  voc_msts.find({...}).select('amount pay_type').lean(),
]);
```

**Why:** These two queries are completely independent — invoices and vouchers don't depend on each other. Running them in parallel saves ~10-20ms per balance check. This function is called during order creation (credit limit check).

**How to verify:**

- API: Create an order for a customer with credit limits. Balance calculation should produce identical results.
- App: Order creation flow works identically. No UI change.

**Discussion:** This is the safest possible `Promise.all` change — only 2 queries, both read-only, both already returning the same data types.

---

## AQP-2: Parallelize `getOnePO` — single order detail (API)

**Status (2026-10-01):** ✅ done — `67de6e0`; `getOnePO` at `api_v3/services/order_msts.js:1104`, its lookups in one parallel wave (`:1112`).

**Size:** S (15 min)
**File:** `api_v3/services/order_msts.js`, lines 1017-1066

**What:** After fetching the order, wrap all 6 enrichment lookups in a single `Promise.all()`.

```js
const order = await OrderMaster.findById(id).lean();
const [vehicle, driver, user, customer, dealer, dealerCust] = await Promise.all(
  [
    VehicleMaster.findById(order.veh_id).select("veh_reg_no").lean(),
    DriverMaster.findOne({ veh_id: order.veh_id })
      .select("name phone code")
      .lean(),
    User.findById(order.cust_user_id).select("username").lean(),
    CustomerMaster.findById(order.cust_id)
      .select("cust_name city state otp_mgr")
      .lean(),
    DealerMaster.findById(order.dealer_id)
      .select("dealer_name city state")
      .lean(),
    DealerCustomer.findOne({
      dealer_id: order.dealer_id,
      cust_id: order.cust_id,
    })
      .select("cs_reimb dealer_id cust_id dvr_otp otp_order_note_dlr")
      .lean(),
  ],
);
```

**Why:** 8 sequential queries become 1 fetch + 1 parallel wave. Saves ~150ms per request. This endpoint powers the single order detail screen — one of the most viewed screens in the app.

**How to verify:**

- API: `GET /order_msts/a/po` with a valid order ID. Response shape must be identical.
- App: Open any order detail screen. All fields (vehicle, driver, customer, dealer info) should display correctly.

**Discussion:** The key insight is that all enrichment lookups only depend on the order document (fetched in step 1), not on each other. That's why they can all run in parallel.

**Does parallelizing impose more load on the DB?** No — the same queries run either way. Total DB work is identical; only concurrency changes (up to 6 queries arrive at once instead of sequentially). This is safe because:

1. MongoDB handles concurrent reads trivially — it's designed for thousands of concurrent connections,
2. these are all read-only, indexed `findById`/`findOne` lookups — the cheapest possible MongoDB operations, and
3. the app server already handles concurrent requests — 10 users hitting this screen simultaneously already produces 60 concurrent queries from 10 sequential handlers. Parallelizing within one request doesn't meaningfully change peak concurrency. Keeping queries sequential doesn't protect the DB — it just makes users wait ~150ms instead of ~30ms for no benefit.

---

## AQP-3: Parallelize `processOrder` — OTP flow (API)

**Status (2026-10-01):** ✅ done — `54c551f`; `processOrder` at `api_v3/services/order_msts.js:545`, the dependent lookups in one wave (`:601`).

**Size:** S (20 min)
**File:** `api_v3/services/order_msts.js`, lines 498-652

**What:** Split into 2 waves:

- Wave 1: Fetch the order (needed for conditionals)
- Wave 2: All dependent lookups in parallel (vehicle, driver/user, dealer, dealer_cust)

**Why:** 9 sequential calls become 2 waves. Saves ~100ms per OTP request. This is the order processing/OTP endpoint — called every time a driver needs an OTP.

**How to verify:**

- API: Process an order via OTP. The OTP should be generated, SMS sent, status updated.
- App: Full OTP flow — request OTP, receive SMS, enter OTP, complete delivery.

**Discussion:** Be careful with the conditional logic — `otp_to === "driver"` determines whether to fetch driver or user. Use a ternary inside `Promise.all()` to pick the right query.

---

## AQP-4: Parallelize `multipleOrderRes` — order list enrichment (API)

**Status (2026-10-01):** ✅ done — `49d0174`; `multipleOrderRes` at `api_v3/services/order_msts.js:421`, wave 1 at `:443`, wave 2 at `:480`.

**Size:** M (30 min)
**File:** `api_v3/services/order_msts.js`, lines 393-495

**What:** Split 8 sequential queries into 2 waves:

- Wave 1: `SOMaster.find()` + all order-derived lookups (Vehicle, User, Customer, Dealer, DealerCustomer) in parallel
- Wave 2: SO-derived lookups (DealerSOrderUser, SODrivers) in parallel — these depend on `s_odrs` from Wave 1

**Why:** This is the **most-called endpoint** in the app (order list screen). 8 sequential queries (~200-320ms) become 2 parallel waves (~30-50ms). That's a 60-80% latency reduction on the screen every user sees first.

**How to verify:**

- API: `GET /order_msts/a/poso` or the POST variant. Response must have all enriched fields (vehicle reg no, customer name, dealer name, driver name, etc.).
- App: Order list screen — every row should show all info correctly. Check both dealer and customer views.

**Discussion:** This is the highest-impact single change. But it touches the most complex function. Double-check the dependency graph: Wave 2 queries need IDs extracted from Wave 1 results.

---

## AQP-5: Replace `Array.find()` with `Map()` in enrichment loop (API)

**Status (2026-10-01):** ✅ done — `0c0cb06`; the Maps are built once at `api_v3/services/order_msts.js:490-499`.

**Size:** S (20 min)
**File:** `api_v3/services/order_msts.js`, lines 449-493

**What:** Build `Map` objects from the lookup results ONCE, then use `Map.get()` in the loop instead of `Array.find()`.

```js
// Build Maps ONCE (O(n) total)
const vehicleMap = new Map(OrderVehicle.map((v) => [String(v._id), v]));
const customerMap = new Map(OrderCustomer.map((c) => [String(c._id), c]));
// ... etc

// Use in loop (O(1) per lookup)
order_mst.forEach((order) => {
  const veh = vehicleMap.get(String(order.veh_id));
  const cust = customerMap.get(String(order.cust_id));
  // ...
});
```

**Also:** Change the `async map` + `Promise.all` to a synchronous `forEach` since there are no async operations left in the loop.

**Why:** With 100 orders and 8 lookups per order, `Array.find()` does 40,000 string comparisons (O(n\*m)). `Map.get()` does 800 lookups (O(1) each). Saves 5-15ms CPU for large result sets. More importantly, it makes the code cleaner and the loop synchronous.

**How to verify:**

- API: Same endpoint as AQP-4. Response must be identical field-by-field.
- App: Order list screen — no visual difference.

**Discussion:** Best done immediately after AQP-4 since you're already touching the same function. The Map approach is also more readable — you can see at a glance which field maps to which collection.

---

## AQP-6: Parallelize `createMstTrn` — order creation (API)

**Status (2026-10-01):** ✅ done — `5e8475c`; `createMstTrn` at `api_v3/services/order_msts.js:755`, parallel waves at `:759`, `:828` and `:846`, the write kept in sequence between them.

**Size:** M (30 min)
**File:** `api_v3/services/order_msts.js`, lines 674-807

**What:** Split 12 sequential queries into 4 waves:

- Wave 1: Independent lookups (dealer_cust, dealer, customer, products, vehicle) — 5 parallel
- Wave 2: Balance checks (OrderOutstanding, SOOutstanding, InvoiceBalance) — 3 parallel (only if credit limit exists)
- Wave 3: Write (OrderMaster.create) — sequential, must be after validation
- Wave 4: Post-create enrichment + notification lookups — 4 parallel

**Why:** 12 sequential queries (~250-400ms) become 4 waves (~80-120ms). This is order creation — the most critical write path. Faster creation = better UX for customers placing orders.

**How to verify:**

- API: Create a full order with products, credit limit check, notifications. Must succeed and produce correct order.
- App: Full order creation flow — select products, submit, see confirmation. Check that notifications fire, credit limit enforcement works, and the order appears in list.

**Discussion:** This is the most complex parallelization because it mixes reads and writes with validation in between. Wave 3 (the write) MUST stay sequential after validation. Test edge cases: credit limit exceeded, invalid vehicle, missing customer.

---

## Summary

| Task                           | Size | Latency Savings             | Risk                     |
| ------------------------------ | ---- | --------------------------- | ------------------------ |
| AQP-1: `currentInvoiceBalance` | XS   | ~20ms per balance check     | Zero                     |
| AQP-2: `getOnePO`              | S    | ~150ms per detail view      | Low                      |
| AQP-3: `processOrder`          | S    | ~100ms per OTP flow         | Low                      |
| AQP-4: `multipleOrderRes`      | M    | ~130-190ms per order list   | Medium — test thoroughly |
| AQP-5: Map lookups             | S    | ~5-15ms CPU for large lists | Low                      |
| AQP-6: `createMstTrn`          | M    | ~170-280ms per order create | Medium — test edge cases |

**Recommended order:** AQP-1 → AQP-2 → AQP-5 → AQP-3 → AQP-4 → AQP-6
(Start with safest, build confidence, then tackle the complex ones.)

---

## New tasks — from the app v2 / API v4 review (2026-10-01)

**What the v4 work added here** (API-0…3 of the redesign's optimisation plan, API PR #43, now on master through PR #39): a scale seed and probe (`scripts/perf/*`, `yarn perf:baseline`) with before / after numbers in `docs/v4-performance.md`; four indexes (see [03](./03-database-optimization.md)); the Customers read model moved off v3's `pendingPOlist` / `uninvoicedSOlist`, whose O(N²) grouping blocked the event loop for 1,285 ms a request (`api_v4/readmodels/customers.js:456-587`, `docs/v4-performance.md:124-133`); `maxTimeMS`, a pool wait limit and a per-user limiter (see [07](./07-resilience-ops.md)). v4 read models fan out only through `runParallel` / `runSettled` (`api_v4/lib/compose.js`); `test/api_v4/lib/conventions.test.js` forbids a bare `Promise.all` in them.

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-PERF-2 | ⏸ Deferred v4 performance items: API-5 (slim `logs` + TTL), API-6 (one "today" aggregate), API-7 (`Server-Timing`), API-8 (chip debounce / summary cache / Customers memo), and the fifth index `so_msts {dealer_id, inv_id, gst_inv_id}` | Deferred by the user on 2026-09-21 (redesign plan 08 §8c). API-5: `logs` stores the whole user doc per production request and has no index or TTL (`helpers/middlewares.js:250,261`, `models/logs.js`); API-6: `csToday` + `ptToday` are still two aggregates (`api_v4/readmodels/customers.js:697-699`); API-7: `timingHeader` exists but has no caller (`api_v4/lib/compose.js:201-214`); API-8: no cache in `api_v4/`; the fifth index measured 134 → 103 ms, not declared (`docs/v4-performance.md:278-293`) | API (API-8 debounce = app) | M | The user's go-ahead; API-5 also closes DB-5 |

Related: API-4 is re-scoped as `X-PERF-1` in [06](./06-caching.md) (the per-request user lookup in `logging()`); API-9 (stored rollups) is `X-PERF-3` in tasks_13. The full list is in [00-overview](./00-overview.md).
