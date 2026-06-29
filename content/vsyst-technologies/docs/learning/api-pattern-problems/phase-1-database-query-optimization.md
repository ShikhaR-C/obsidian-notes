# Phase 1: Database & Query Optimization

**Priority:** P0 | **Timeline:** Week 1-2 | **Impact:** 60-80% latency reduction

---

## Sub-Phase 1A: Parallelize Sequential DB Calls with Promise.all()

### Research: Why Sequential Awaits Are Costly

When you `await` multiple independent MongoDB queries sequentially, each query must complete its full roundtrip (network + query execution + response) before the next one starts. With MongoDB Atlas, typical roundtrip is 5-25ms per query. For 8 sequential queries, that's 40-200ms of pure waiting.

**Pattern to follow (from MongoDB best practices):**

```js
// BAD: Sequential (total = sum of all query times)
const a = await ModelA.find(filter1);
const b = await ModelB.find(filter2);
const c = await ModelC.find(filter3);

// GOOD: Parallel (total = max of all query times)
const [a, b, c] = await Promise.all([
  ModelA.find(filter1),
  ModelB.find(filter2),
  ModelC.find(filter3),
]);
```

**Key rule:** Only parallelize queries that are independent of each other's results.

---

### Step 1A-1: multipleOrderRes -- Order List Enrichment

**File:** `api_v3/services/order_msts.js`, lines 393-495
**Endpoint:** `GET /api/v3/order_msts/a/poso`
**Impact:** This is the most-called endpoint in the app (order list screen)

#### Current Code (8 sequential DB calls)

```js
// Line 398: Wave 1 -- need this first because DealerSOrderUser and SODrivers depend on s_odrs
const s_odrs = await SOMaster.find({ _id: { $in: order_soIDs } }).lean();

// Lines 404-406: Depends on s_odrs (needs dealeruserIds from s_odrs)
const DealerSOrderUser = await User.find({ _id: { $in: dealeruserIds } }).select("username").lean();

// Lines 409-411: Depends on s_odrs (needs driversIds from s_odrs)
const SODrivers = await DriverMaster.find({ _id: { $in: driversIds } }).select("_id name phone code").lean();

// Lines 414-416: Independent (uses order_mst.veh_id)
const OrderVehicle = await VehicleMaster.find({ _id: { $in: vehicleIds } }).select("veh_reg_no").lean();

// Lines 422-424: Independent (uses order_mst.cust_user_id)
const OrderUser = await User.find({ _id: { $in: userIds } }).select("username").lean();

// Lines 427-429: Independent (uses order_mst.cust_id)
const OrderCustomer = await CustomerMaster.find({ _id: { $in: customerIds } }).select("cust_name city state").lean();

// Lines 433-435: Independent (uses order_mst.dealer_id)
const OrderDealer = await DealerMaster.find({ _id: { $in: dealerIds } }).select("dealer_name city state").lean();

// Lines 441-446: Independent (uses order_mst dealer/cust IDs)
const OrderDealerCustomer = await DealerCustomer.find({...}).select("cs_reimb dealer_id cust_id dvr_otp cust_type").lean();
```

#### Proposed Solution

Split into 2 waves:

```js
const multipleOrderRes = async ({ orderMst }) => {
  const order_mst = orderMst;

  // Extract all IDs upfront
  const order_soIDs = [
    ...new Set(order_mst.map((a) => a.so_id && `${a.so_id}`)),
  ];
  const vehicleIds = [...new Set(order_mst.map((a) => `${a.veh_id}`))];
  const userIds = [
    ...new Set(order_mst.map((a) => a.cust_user_id && `${a.cust_user_id}`)),
  ];
  const customerIds = [...new Set(order_mst.map((a) => `${a.cust_id}`))];
  const dealerIds = [...new Set(order_mst.map((a) => `${a.dealer_id}`))];

  // WAVE 1: Fetch sales orders + all order-derived lookups in parallel
  const [
    s_odrs,
    OrderVehicle,
    OrderUser,
    OrderCustomer,
    OrderDealer,
    OrderDealerCustomer,
  ] = await Promise.all([
    SOMaster.find({ _id: { $in: order_soIDs } }).lean(),
    VehicleMaster.find({ _id: { $in: vehicleIds } })
      .select("veh_reg_no")
      .lean(),
    User.find({ _id: { $in: userIds } })
      .select("username")
      .lean(),
    CustomerMaster.find({ _id: { $in: customerIds } })
      .select("cust_name city state")
      .lean(),
    DealerMaster.find({ _id: { $in: dealerIds } })
      .select("dealer_name city state")
      .lean(),
    DealerCustomer.find({
      dealer_id: { $in: dealerIds },
      cust_id: { $in: customerIds },
    })
      .select("cs_reimb dealer_id cust_id dvr_otp cust_type")
      .lean(),
  ]);

  if (!s_odrs) throw new ErrorResponse("Sales Orders not found", 404);
  if (!OrderVehicle) throw new ErrorResponse("Vehicle Mst not found", 404);
  if (!OrderCustomer) throw new ErrorResponse("Customer not found", 404);
  if (!OrderDealer) throw new ErrorResponse("Dealer not found", 404);
  if (!OrderDealerCustomer) throw new ErrorResponse("Not found", 404);

  // WAVE 2: Fetch SO-derived lookups (depends on s_odrs)
  const dealeruserIds = [
    ...new Set(s_odrs.map((a) => a.dealer_user_id && `${a.dealer_user_id}`)),
  ];
  const driversIds = [...new Set(s_odrs.map((a) => a.dvr_id && `${a.dvr_id}`))];

  const [DealerSOrderUser, SODrivers] = await Promise.all([
    User.find({ _id: { $in: dealeruserIds } })
      .select("username")
      .lean(),
    DriverMaster.find({ _id: { $in: driversIds } })
      .select("_id name phone code")
      .lean(),
  ]);

  // ... enrichment loop (see Step 1B-1 for Map optimization)
};
```

#### Expected Impact

- **Before:** 8 sequential queries = ~160-240ms
- **After:** 2 parallel waves = ~30-50ms
- **Savings:** ~130-190ms per request

#### Verification

```js
// Add timing instrumentation
const start = process.hrtime.bigint();
// ... function body ...
const elapsed = Number(process.hrtime.bigint() - start) / 1e6;
console.log(`multipleOrderRes: ${elapsed.toFixed(1)}ms`);
```

---

### Step 1A-2: createMstTrn -- Order Creation

**File:** `api_v3/services/order_msts.js`, lines 674-807
**Endpoint:** `POST /api/v3/order_msts`

#### Current Code (12 sequential DB calls)

```
Line 676: DealerCustomer.findOne()      -- needs cust_id, dealer_id
Line 681: DealerMaster.findById()       -- needs dealer_id
Line 684: CustomerMaster.findById()     -- needs cust_id
Line 694: newProdList()                 -- needs products (internal DB call)
Line 738: currentOrderOutstanding()     -- needs dealer_cust (1 DB call)
Line 739: currentSOOutstanding()        -- needs dealer_cust (1 DB call)
Line 740: currentInvoiceBalance()       -- needs dealer_cust (2 DB calls)
Line 755: veh_trns.findOne()            -- needs veh_id, cust_id
Line 763: OrderMaster.create()          -- write (must be after validation)
Line 766: CustomerMaster.findByIdAndUpdate() -- write (must be after create)
Line 771: VehicleMaster.findById()      -- needs veh_id (for notification)
Line 776: User.find()                   -- notification users
Line 797: User.findById()              -- cust_user_id
```

#### Proposed Solution (3 waves)

```js
exports.createMstTrn = async ({ body, meta }) => {
  const { cust_id, dealer_id, cs_reimb_amt } = body;

  // WAVE 1: All independent lookups (5 parallel)
  const [dealer_cust, dealer, customer, nps, veh_trn] = await Promise.all([
    DealerCustomer.findOne({ cust_id, dealer_id })
      .select(
        "cust_bal cust_id dealer_id _id cust_verified dealer_verified hidden max_cr_lmt adv_dep cs_reimb ftank_amt",
      )
      .lean(),
    DealerMaster.findById(dealer_id)
      .select("dealer_verified dealer_name city state")
      .lean(),
    CustomerMaster.findById(cust_id)
      .select("cust_verified cust_name city state cust_podgt")
      .lean(),
    newProdList({ products: body.products }),
    veh_trns.findOne({ veh_id: body.veh_id, cust_id }).lean(),
  ]);

  // Validation (unchanged)
  const errorState = canTransact({ dealer, customer, dealer_cust });
  if (!!errorState) throw new ErrorResponse(errorState, 404);
  if (!veh_trn) throw new ErrorResponse("Vehicle not found", 404);
  if (veh_trn.veh_status === "notuse")
    throw new ErrorResponse("Vehicle not in use", 404);

  // ... version check, amount calculation (unchanged) ...

  // WAVE 2: Balance checks (3 parallel) -- only if credit limit exists
  if (
    typeof dealer_cust.max_cr_lmt === "number" &&
    Number(dealer_cust.max_cr_lmt) !== 0
  ) {
    const [OrderSum, SOsum, invSum] = await Promise.all([
      currentOrderOutstanding(dealer_cust),
      currentSOOutstanding(dealer_cust),
      currentInvoiceBalance({ dealer_cust, providedDate: new Date() }),
    ]);
    const AdvanceDeposit = dealer_cust.adv_dep ? +dealer_cust.adv_dep : 0;
    const prevBal = +OrderSum + +SOsum + +invSum;
    const balSum = +prevBal + +finalAmount - +AdvanceDeposit;
    if (
      !!dealer_cust.max_cr_lmt &&
      Number(dealer_cust.max_cr_lmt) < Number(balSum)
    ) {
      throw new ErrorResponse("Credit Limit Exceeded", 404);
    }
  }

  // WAVE 3: Write operations (sequential -- order matters)
  const order_mst = await OrderMaster.create({ ...r, order_no, products: nps });
  if (!order_mst) throw new ErrorResponse("Some error occurred", 404);

  // WAVE 4: Post-create enrichment + notification (3 parallel)
  const [updatecust, vehicle, u, user] = await Promise.all([
    CustomerMaster.findByIdAndUpdate(cust_id, { cust_podgt: order_no }),
    VehicleMaster.findById(order_mst.veh_id).select("veh_reg_no"),
    User.find({
      role: "dealer",
      companies: {
        $elemMatch: {
          co_id: dealer_id,
          notif: { $in: ["NewOrder"] },
          status: "ACTIVE",
        },
      },
    }).select("_id"),
    User.findById(order_mst.cust_user_id).select("username"),
  ]);

  // ... notification + return (unchanged) ...
};
```

#### Expected Impact

- **Before:** 12 sequential = ~250-400ms
- **After:** 4 waves (5 || 3 || 1 || 4) = ~80-120ms
- **Savings:** ~170-280ms per order creation

---

### Step 1A-3: processOrder -- OTP Flow

**File:** `api_v3/services/order_msts.js`, lines 498-652
**Endpoint:** `PUT /api/v3/order_msts/process/:id`

#### Current: 9 sequential calls

Lines 509, 543, 550, 553, 556, 560, 580, 610-635 (SMS), notification users

#### Proposed: 2 waves

```js
// WAVE 1: Fetch order (needed for conditionals)
const order = await OrderMaster.findOne({ _id: body._id }).lean();

// WAVE 2: All dependent lookups in parallel
const [vehicle, driverOrUser, dealer, dealer_cust] = await Promise.all([
  VehicleMaster.findOne({ _id: order.veh_id }).select("veh_reg_no").lean(),
  otp_to === "driver"
    ? DriverMaster.findOne({ veh_id: order.veh_id })
        .select("name phone code email")
        .lean()
    : User.findById(otpUserId).select("username phone email").lean(),
  DealerMaster.findOne({ _id: order.dealer_id })
    .select("dealer_name dealer_code oil_co oil_do")
    .lean(),
  DealerCustomer.findOne({ cust_id: order.cust_id, dealer_id: order.dealer_id })
    .select("dvr_otp")
    .lean(),
]);
```

#### Expected Impact: ~100ms savings

---

### Step 1A-4: getOnePO -- Single Order Detail

**File:** `api_v3/services/order_msts.js`, lines 1017-1066
**Endpoint:** `GET /api/v3/order_msts/a/po`

#### Current: 8 sequential calls after order fetch

#### Proposed: Single Promise.all

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

#### Expected Impact: ~150ms savings

---

### Step 1A-5: currentInvoiceBalance -- Internal Parallelization

**File:** `api_v3/services/order_msts.js`, lines 310-346

#### Current

```js
const Invoice = await invs
  .find({ dealer_id, cust_id, inv_dt: { $gte, $lte } })
  .select("inv_total_amt")
  .lean();
// ... calculate ...
const Vouchers = await voc_msts
  .find({ dealer_id, cust_id, pay_status: true, pay_dt: { $gte, $lte } })
  .select("amount pay_type")
  .lean();
```

#### Proposed

```js
const [Invoice, Vouchers] = await Promise.all([
  invs
    .find({ dealer_id, cust_id, inv_dt: { $gte: stdate, $lte: eddate } })
    .select("inv_total_amt")
    .lean(),
  voc_msts
    .find({
      dealer_id,
      cust_id,
      pay_status: true,
      pay_dt: { $gte: stdate, $lte: eddate },
    })
    .select("amount pay_type")
    .lean(),
]);
```

#### Expected Impact: ~20ms savings per balance check

---

## Sub-Phase 1B: Replace array.find() with Map() for O(1) Lookups

### Research: Array.find() vs Map.get()

`Array.find()` is O(n) per call. In a loop over `m` orders, calling `.find()` on `n`-element arrays 8 times = O(8*m*n). For 100 orders with 50 vehicles, that's 40,000 string comparisons with template-literal coercion (`${a._id}` === `${b._id}`).

`Map.get()` is O(1) per call. Build the Map once (O(n)), then look up in O(1). Total: O(n + m) instead of O(m\*n).

---

### Step 1B-1: multipleOrderRes Enrichment Loop

**File:** `api_v3/services/order_msts.js`, lines 449-493

#### Current Code (O(n\*m) lookups)

```js
await Promise.all(
  order_mst.map(async (order) => {
    const dealerCust = OrderDealerCustomer.find(
      (dC) =>
        `${dC.dealer_id}` === `${order.dealer_id}` &&
        `${dC.cust_id}` === `${order.cust_id}`,
    );
    const sOdr = s_odrs.find((s) => `${order.so_id}` === `${s._id}`);
    // ... 6 more .find() calls ...
    const veh = OrderVehicle.find((v) => `${order.veh_id}` === `${v._id}`);
    let user = OrderUser.find((u) => `${order.cust_user_id}` === `${u._id}`);
    const cust = OrderCustomer.find((c) => `${c._id}` === `${order.cust_id}`);
    const dlr = OrderDealer.find((d) => `${d._id}` === `${order.dealer_id}`);
  }),
);
```

#### Proposed Solution

```js
// Build Maps ONCE (O(n) total)
const vehicleMap = new Map(OrderVehicle.map((v) => [String(v._id), v]));
const userMap = new Map(OrderUser.map((u) => [String(u._id), u]));
const customerMap = new Map(OrderCustomer.map((c) => [String(c._id), c]));
const dealerMap = new Map(OrderDealer.map((d) => [String(d._id), d]));
const soMap = new Map(s_odrs.map((s) => [String(s._id), s]));
const soUserMap = new Map(DealerSOrderUser.map((u) => [String(u._id), u]));
const soDriverMap = new Map(SODrivers.map((d) => [String(d._id), d]));
// Dealer-Cust needs composite key
const dcMap = new Map(
  OrderDealerCustomer.map((dc) => [`${dc.dealer_id}:${dc.cust_id}`, dc]),
);

// Use Maps in loop (O(1) per lookup)
order_mst.forEach((order) => {
  const dealerCust = dcMap.get(`${order.dealer_id}:${order.cust_id}`);
  const sOdr = soMap.get(String(order.so_id));

  if (sOdr) {
    let duser = soUserMap.get(String(sOdr.dealer_user_id));
    let cdriver = soDriverMap.get(String(sOdr.dvr_id));
    // ...
  }

  const veh = vehicleMap.get(String(order.veh_id));
  let user = userMap.get(String(order.cust_user_id));
  if (!user) user = { username: "Automatic" };
  const cust = customerMap.get(String(order.cust_id));
  const dlr = dealerMap.get(String(order.dealer_id));
  // ...
});
```

**Also note:** The loop can now be synchronous (`forEach` instead of `async map` with `Promise.all`) since there are no async operations left.

#### Expected Impact

- 100 orders _ 8 lookups _ ~50 items = **40,000 comparisons -> ~800 Map lookups**
- CPU savings: ~5-15ms for large result sets

---

## Sub-Phase 1C: Combine countDocuments + find into $facet

### Research: MongoDB $facet for Pagination

The `$facet` stage processes multiple aggregation pipelines on the same set of input documents in a single pass. This eliminates the need for separate `countDocuments()` + `find()` calls.

**Performance benefit:**

- Single query instead of two
- MongoDB only scans documents once
- Reduces network roundtrips by 50%

---

### Step 1C-1: advancedResults.getResults()

**File:** `helpers/advancedResults.js`, lines 60-113

#### Current Code

```js
// Line 87: QUERY 1 -- counts all matching documents
const count = await model.countDocuments(queryStr);

// Line 105-110: QUERY 2 -- fetches paginated results
query = query.skip(startIndex).limit(limit);
const results = await query.lean();
```

#### Proposed Solution

```js
exports.getResults = async (req_query, model, populate, isPost = false) => {
  let reqQuery = { ...req_query };
  let queryStr = this.renameKeys(reqQuery, isPost);

  // Build sort object
  let sortObj = { createdAt: -1 };
  if (req_query.sort) {
    sortObj = {};
    req_query.sort.split(",").forEach((field) => {
      if (field.startsWith("-")) sortObj[field.slice(1)] = -1;
      else sortObj[field] = 1;
    });
  }

  // Build select object
  let projectStage = null;
  if (req_query.select) {
    projectStage = {};
    req_query.select.split(",").forEach((f) => {
      projectStage[f.trim()] = 1;
    });
  }

  // Calculate pagination params
  const page = parseInt(req_query.page, 10) || 1;
  const limit = parseInt(req_query.limit, 10) || 0;
  const startIndex = (page - 1) * limit;

  // Single $facet query
  const pipeline = [
    { $match: queryStr },
    {
      $facet: {
        metadata: [{ $count: "total" }],
        data: [
          { $sort: sortObj },
          ...(limit > 0 ? [{ $skip: startIndex }, { $limit: limit }] : []),
          ...(projectStage ? [{ $project: projectStage }] : []),
        ],
      },
    },
  ];

  const [result] = await model.aggregate(pipeline);
  const count = result.metadata[0]?.total || 0;
  const results = result.data;

  // Pagination
  const endIndex = page * limit;
  const pagination = {};
  if (endIndex < count) pagination.next = { page: page + 1, limit };
  if (startIndex > 0) pagination.prev = { page: page - 1, limit };

  return { success: true, count, pagination, data: results };
};
```

#### Caveats

- `$facet` doesn't use indexes for `$sort` inside the facet -- the `$match` stage must come before `$facet` to leverage indexes
- If `populate` is needed, handle it as a `$lookup` stage in the pipeline or do it post-query
- For queries with `populate`, fall back to the 2-query approach or use `$lookup`

#### Expected Impact

- **Before:** 2 roundtrips per paginated request (~30-60ms)
- **After:** 1 roundtrip (~15-30ms)
- **Savings:** ~15-30ms per paginated endpoint (affects 15+ endpoints)

---

### Step 1C-2: advancedResults middleware variant

**File:** `helpers/advancedResults.js`, lines 152-210

Same pattern -- line 195 `countDocuments` + line 197 `find`. Apply identical $facet solution.

---

## Sub-Phase 1D: Add Missing Compound Indexes

### Research: MongoDB Index Strategy

- **Compound indexes** must follow the ESR rule: **E**quality fields first, **S**ort fields next, **R**ange fields last
- A compound index on `{dealer_id: 1, cust_id: 1}` covers queries for `{dealer_id}` alone AND `{dealer_id, cust_id}` together
- Without proper indexes, MongoDB performs **collection scans** (COLLSCAN), examining every document

---

### Step 1D-1: dealer_custs compound index

**Model file:** `models/dealer_custs.js`
**Current indexes (lines 121-122):** `cust_id: 1` and `dealer_id: 1` (separate)

**Queries using `{dealer_id, cust_id}`:**

- `order_msts.js:676` -- `DealerCustomer.findOne({ cust_id, dealer_id })`
- `order_msts.js:441` -- `DealerCustomer.find({ dealer_id: { $in }, cust_id: { $in } })`
- `so_msts.js`, `invs.js`, `voc_msts.js` -- similar patterns

```js
// Add to models/dealer_custs.js
dealer_cust__mst_Schema.index({ dealer_id: 1, cust_id: 1 }, { unique: true });
// Remove individual indexes (compound covers single-field queries on dealer_id)
```

### Step 1D-2: invs compound index

**Model file:** `models/invs.js`

```js
// For currentInvoiceBalance: { dealer_id, cust_id, inv_dt: { $gte, $lte } }
invSchema.index({ dealer_id: 1, cust_id: 1, inv_dt: -1 });
```

### Step 1D-3: voc_msts compound index

**Model file:** `models/voc_msts.js`

```js
// For currentInvoiceBalance: { dealer_id, cust_id, pay_status: true, pay_dt: { $gte, $lte } }
voc_mst_Schema.index({ dealer_id: 1, cust_id: 1, pay_status: 1, pay_dt: -1 });
```

### Step 1D-4: so_msts compound index

**Model file:** `models/so_msts.js`

```js
// For currentSOOutstanding: { dealer_id, cust_id, inv_id: { $exists: false } }
so_mst_Schema.index({ dealer_id: 1, cust_id: 1 });
```

### Step 1D-5: users notification index

**Model file:** `models/users.js`

```js
// For notification queries: { role, companies.co_id, companies.status }
UserSchema.index({ role: 1, "companies.co_id": 1, "companies.status": 1 });
```

### Step 1D-6: order_msts status index

**Model file:** `models/order_msts.js`

```js
// For currentOrderOutstanding: { dealer_id, cust_id, order_status: { $in: ["PENDING", "PROCESSING"] } }
order_mst_Schema.index({
  dealer_id: 1,
  cust_id: 1,
  order_status: 1,
  createdAt: -1,
});
```

#### Verification for All Indexes

```js
// Run in mongo shell or via script
db.dealer_custs
  .find({ dealer_id: ObjectId("..."), cust_id: ObjectId("...") })
  .explain("executionStats");
// Check: stage should be "IXSCAN" not "COLLSCAN"
// Check: totalKeysExamined should be close to nReturned
```

#### Expected Impact

- Queries on indexed fields: **10-50ms -> 1-5ms**
- Most dramatic on balance calculations (invs, voc_msts, so_msts)

---

## Sub-Phase 1E: Add .select() to All Read Queries

### Step 1E-1: Audit Missing .select() Calls

| File            | Line | Query                                    | Missing Fields                   |
| --------------- | ---- | ---------------------------------------- | -------------------------------- |
| `order_msts.js` | 509  | `OrderMaster.findOne({ _id: body._id })` | Returns all fields including OTP |
| `order_msts.js` | 550  | `DriverMaster.findOne({ veh_id })`       | Returns all driver fields        |
| `order_msts.js` | 811  | `OrderMaster.findById(id)`               | Returns all fields               |
| `order_msts.js` | 908  | `OrderMaster.findById(id)`               | Returns all fields               |
| `order_msts.js` | 1024 | `DriverMaster.findOne({ veh_id })`       | Returns all driver fields        |

**Proposed:** Add `.select()` with only the fields needed by the calling code.

**Expected Impact:** 10-30% reduction in data transfer from MongoDB per query.

---

## Summary of Phase 1 Expected Results

| Metric                        | Before                            | After                                 |
| ----------------------------- | --------------------------------- | ------------------------------------- |
| Order list (multipleOrderRes) | 8 sequential queries, ~200-320ms  | 2 parallel waves, ~30-50ms            |
| Order creation (createMstTrn) | 12 sequential queries, ~250-400ms | 4 waves (5\|\|3\|\|1\|\|4), ~80-120ms |
| Order process (processOrder)  | 9 sequential, ~200-300ms          | 2 waves, ~50-80ms                     |
| Single order (getOnePO)       | 8 sequential, ~180-250ms          | 1 wave, ~30-40ms                      |
| Paginated lists               | 2 queries, ~40-80ms               | 1 $facet query, ~15-30ms              |
| Enrichment loop (100 orders)  | O(40,000) comparisons             | O(800) Map lookups                    |
| Index scans                   | COLLSCAN on many queries          | IXSCAN on all                         |
