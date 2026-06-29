# Phase 3: API Consolidation & BFF Pattern

**Priority:** P2 | **Timeline:** Week 7-8 | **Impact:** Reduce API calls per screen from 3-4 to 1

---

## Research: Backend For Frontend (BFF) Pattern

### Why BFF for Mobile Apps?

Mobile clients face unique constraints:

- **High latency** per request (cellular networks: 50-200ms RTT)
- **Battery drain** from multiple connections
- **Data plans** punish over-fetching

A BFF layer creates mobile-optimized composite endpoints that aggregate multiple internal service calls into a single response tailored to each screen's needs.

### REST Best Practices for Mobile

1. **One API call per screen** -- aggregate related data server-side
2. **Field selection** -- return only what the screen needs
3. **Cursor-based pagination** -- performant for infinite scroll
4. **Response compression** -- gzip/brotli for JSON payloads
5. **Partial responses** -- `?fields=name,email` support

---

## Sub-Phase 3A: Composite Endpoints

### Step 3A-1: Order Detail Composite -- GET /order_msts/:id/full

**Problem:**
The app's order detail screen needs:

1. Order data (from `order_msts`)
2. Vehicle info (from `veh_msts`)
3. Driver info (from `dvr_msts`)
4. Customer name (from `cust_msts`)
5. Dealer name (from `dealer_msts`)
6. Dealer-customer settings (from `dealer_custs`)
7. Product rates (from `rate_msts`)

Currently the app calls `GET /order_msts/a/po` which internally assembles most of this (Step 1A-4 already parallelizes this). But product rates require a separate call.

**Proposed:** Extend `getOnePO` to optionally include product rates:

```js
// New route in api_v3/routes/collections/order_msts.js
router.get(
  "/full/:id",
  asyncHandler(async (req, res) => {
    const order = await orderService.getOnePOFull({ id: req.params.id });
    res.status(200).json({ success: true, data: order });
  }),
);
```

```js
// In api_v3/services/order_msts.js
exports.getOnePOFull = async ({ id }) => {
  const order = await OrderMaster.findById(id).lean();
  if (!order) throw new ErrorResponse("Order not found", 404);

  const [vehicle, driver, user, customer, dealer, dealerCust, rates] =
    await Promise.all([
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
        .select("cs_reimb dvr_otp otp_order_note_dlr cust_type")
        .lean(),
      // NEW: Include product rates in same call
      Promise.all(
        order.products.map((p) =>
          RateMaster.findOne({
            prod_id: p.prod_id,
            dealer_id: order.dealer_id,
            effective_from: { $lte: new Date() },
          })
            .sort({ effective_from: -1 })
            .select("rate effective_from")
            .lean(),
        ),
      ),
    ]);

  // Enrich products with rates
  order.products.forEach((p, i) => {
    p.current_rate = rates[i];
  });

  return {
    ...order,
    vehicle,
    driver,
    user: user || { username: "Automatic" },
    customer,
    dealer,
    dealerCust,
  };
};
```

**App-side RTK Query endpoint:**

```js
fetch_order_full: builder.query({
  query: ({ id }) => ({ url: `order_msts/full/${id}` }),
  transformResponse: (response) => response.data,
  providesTags: (result, error, { id }) => [{ type: 'orders', id }],
}),
```

**Impact:** Order detail screen: 2-3 API calls -> 1 API call

---

### Step 3A-2: Dashboard Composite -- GET /dashboard/summary

**Problem:** Dashboard screen potentially needs:

- Pending order count
- Today's SO total
- Unread notification count
- Recent activity

**Proposed:**

```js
// New route: api_v3/routes/collections/dashboard.js
router.get(
  "/summary",
  asyncHandler(async (req, res) => {
    const { co_id, role } = req.user;
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const filterField = role === "dealer" ? "dealer_id" : "cust_id";

    const [pendingOrders, todaySOs, recentOrders] = await Promise.all([
      OrderMaster.countDocuments({
        [filterField]: co_id,
        order_status: { $in: ["PENDING", "PROCESSING"] },
      }),
      SOMaster.countDocuments({
        [filterField]: co_id,
        createdAt: { $gte: today },
      }),
      OrderMaster.find({ [filterField]: co_id })
        .sort({ createdAt: -1 })
        .limit(5)
        .select("order_no order_status createdAt products")
        .lean(),
    ]);

    res.status(200).json({
      success: true,
      data: { pendingOrders, todaySOs, recentOrders },
    });
  }),
);
```

**Impact:** Dashboard: 3-4 API calls -> 1 API call

---

### Step 3A-3: Sales Order with Invoice -- GET /so_msts/:id/with-invoice

**Problem:** App fetches SO headers and details separately (`so_msts/app/section1` and `so_msts/app/section2`).

**Proposed:** Single endpoint returning SO + linked invoice if exists:

```js
exports.getSOWithInvoice = async ({ id }) => {
  const so = await SOMaster.findById(id).lean();
  if (!so) throw new ErrorResponse("Sales order not found", 404);

  const invoice = so.inv_id ? await InvMaster.findById(so.inv_id).lean() : null;

  return { ...so, invoice };
};
```

---

## Sub-Phase 3B: Eliminate Duplicate GET/POST Endpoints

### Step 3B-1: Standardize on POST for Filtered Lists

**Problem:** Multiple endpoints exist as both GET and POST:

| Resource | GET Route                   | POST Route                | File                                            |
| -------- | --------------------------- | ------------------------- | ----------------------------------------------- |
| Orders   | `GET /order_msts/a/poso`    | `POST /order_msts/a/poso` | `api_v3/routes/collections/order_msts.js:51-52` |
| Vouchers | `GET /voc_msts/voucher/inv` | `POST /voc_msts/app/get`  | `api_v3/routes/collections/voc_msts.js`         |
| Invoices | `GET /invs/app/get`         | `POST /invs/app/get`      | `api_v3/routes/collections/invs.js`             |

This causes RTK Query cache fragmentation because `fetch_order_msts_so` (GET) and `fetch_order_so_POST` (POST) have different cache keys.

**Proposed:**

1. Keep POST as the standard for filtered lists (supports complex nested filters)
2. Deprecate GET variants (add deprecation header, log usage)
3. Update app to use only POST variants
4. Remove GET after migration period

```js
// Deprecation middleware
const deprecated = (message) => (req, res, next) => {
  res.set("Deprecation", "true");
  res.set("Link", `<${message}>; rel="successor-version"`);
  console.warn(`DEPRECATED: ${req.method} ${req.originalUrl}`);
  next();
};

// In routes
router.get("/a/poso", deprecated("Use POST /a/poso instead"), getHandler);
router.post("/a/poso", postHandler);
```

---

## Sub-Phase 3C: Response Compression

### Step 3C-1: Add gzip/brotli Compression

**Problem:** `dzzlo_oms.js` has no compression middleware. Order list responses with 50+ items can be 50-200KB of JSON.

**Install:**

```bash
yarn add compression
```

**Add to `dzzlo_oms.js` (before routes):**

```js
const compression = require("compression");
app.use(
  compression({
    threshold: 1024, // Only compress responses > 1KB
    level: 6, // Balanced speed vs compression ratio
    filter: (req, res) => {
      if (req.headers["x-no-compression"]) return false;
      return compression.filter(req, res);
    },
  }),
);
```

**Expected Impact:**

- JSON compresses very well: 70-85% size reduction
- 100KB response -> ~15-20KB compressed
- Significant on mobile data connections

---

## Sub-Phase 3D: Cursor-Based Pagination

### Research: Offset vs Cursor Pagination

| Feature                  | Offset (`skip/limit`)           | Cursor (`_id > last_id`) |
| ------------------------ | ------------------------------- | ------------------------ |
| Deep pages (page 100+)   | Slow (MongoDB skips N docs)     | Constant time            |
| Real-time data (inserts) | Pages shift (duplicate/missing) | Stable                   |
| Random page access       | Yes                             | No (sequential only)     |
| Implementation           | Simple                          | Moderate                 |

**Decision:** Cursor-based for infinite scroll endpoints (orders, vouchers). Keep offset for admin dashboards that need random page access.

### Step 3D-1: Implement Cursor Pagination in advancedResults

```js
exports.getCursorResults = async (req_query, model, isPost = false) => {
  let reqQuery = { ...req_query };
  let queryStr = this.renameKeys(reqQuery, isPost);

  const limit = parseInt(req_query.limit, 10) || 20;
  const cursor = req_query.cursor; // _id of last item
  const direction = req_query.direction || "next"; // "next" or "prev"

  if (cursor) {
    queryStr._id =
      direction === "next"
        ? { $lt: cursor } // newer items first (sorted by -createdAt usually means newer _id)
        : { $gt: cursor };
  }

  const sortDir = direction === "next" ? -1 : 1;

  const results = await model
    .find(queryStr)
    .sort({ _id: sortDir })
    .limit(limit + 1) // fetch one extra to check hasMore
    .lean();

  const hasMore = results.length > limit;
  if (hasMore) results.pop(); // remove the extra

  return {
    success: true,
    data: results,
    cursor: {
      next: results.length > 0 ? results[results.length - 1]._id : null,
      hasMore,
    },
  };
};
```

**App-side update:**

```js
// In paginationHelpers.js
export const createCursorPaginatedConfig = (dataKey = "data") => ({
  serializeQueryArgs: ({ endpointName, queryArgs }) => {
    const { cursor, ...rest } = queryArgs || {};
    return `${endpointName}(${JSON.stringify(rest)})`;
  },
  merge: (currentCache, newItems) => {
    if (currentCache[dataKey]) {
      const ids = new Set(currentCache[dataKey].map((d) => d._id));
      const merged = [
        ...currentCache[dataKey],
        ...newItems[dataKey].filter((d) => !ids.has(d._id)),
      ];
      return { ...newItems, [dataKey]: merged };
    }
    return newItems;
  },
  forceRefetch: ({ currentArg, previousArg }) => currentArg !== previousArg,
});
```

---

## Sub-Phase 3E: Field Selection via Query Params

### Step 3E-1: Document and Validate ?fields= Support

`advancedResults.js` already supports `?select=field1,field2` (line 72-74). But:

1. It's undocumented
2. No validation (user could select sensitive fields)
3. App doesn't use it

**Proposed:**

1. Rename to `?fields=` for REST convention
2. Add a whitelist per model:

```js
const ALLOWED_FIELDS = {
  order_msts: [
    "order_no",
    "order_status",
    "products",
    "cust_id",
    "dealer_id",
    "createdAt",
    "veh_id",
  ],
  cust_msts: ["cust_name", "cust_email", "cust_phone", "city", "state"],
  dealer_msts: ["dealer_name", "dealer_email", "city", "state"],
};

// In advancedResults
if (req_query.fields) {
  const requested = req_query.fields.split(",").map((f) => f.trim());
  const allowed = ALLOWED_FIELDS[model.collection.name] || [];
  const validated = requested.filter((f) => allowed.includes(f));
  if (validated.length > 0) query = query.select(validated.join(" "));
}
```

3. Use in app for list screens that only need a few fields:

```js
fetch_order_msts_so: builder.query({
  query: (params) => ({
    url: 'order_msts/a/poso',
    params: { ...params, fields: 'order_no,order_status,createdAt,cust_id,dealer_id' },
  }),
}),
```

---

## Verification

1. **Composite endpoints:** Compare screen load time before/after (should halve network waterfall)
2. **Compression:** Check `Content-Encoding: gzip` header in responses; measure payload sizes
3. **Cursor pagination:** Test with 10K+ records; verify constant query time regardless of page depth
4. **Field selection:** Verify reduced payload size with `?fields=` param
5. **Cache unification:** Verify RTK Query cache entries are shared between GET/POST variants
