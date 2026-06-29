# 03 — Composite / BFF (Backend-For-Frontend) Endpoints

> Originally deferred as **Phase 3A** in the learning docs.
> Goal: collapse the 3-5 parallel requests fired by heavy screens into a single composite endpoint shaped for the exact screen that consumes it.

---

## TL;DR

Today: the `Customer/NewOrder` screen fires 4-5 parallel HTTP requests on mount (vehicles, product rates, dealer list, relation balance, optional order detail). The `Common/Accounts` screen fires 3-4. The `Common/CompanyUsers` screen fires 4. Each request has its own round-trip, its own JWT verification, its own Mongoose hydration, and its own response parsing.

Target: every heavy screen has a **dedicated composite endpoint** like `POST /api/v3/screens/new-order` that returns all the data that screen needs in a single JSON payload, shaped exactly for that screen. The generic list endpoints (`GET /veh_trns_other`, `POST /prod_rates`, etc.) keep working unchanged — BFF is purely additive.

Net effect: the 5 heaviest screens go from 3-5 requests each to 1. On a 200ms-RTT 4G connection, that's a **400-800ms faster first paint** per screen, plus less JWT overhead on the API.

---

## 1. What Is a BFF Endpoint?

A **Backend-For-Frontend** endpoint is a server-side composition layer that exists solely to serve one specific client screen. Instead of the client orchestrating 5 calls and stitching the results together in JavaScript, the server does the orchestration in one request.

**Generic REST endpoint** (today):

```
GET  /api/v3/veh_trns/other
GET  /api/v3/prod_msts/rate?dealer_id=X
POST /api/v3/relations/dealer/customers
POST /api/v3/relations/bal
GET  /api/v3/order_msts/a/poso/:id
```

Client fires all 5 in parallel, waits for all, combines.

**BFF endpoint** (target):

```
POST /api/v3/screens/new-order
Body: { orderId?: "<for edit mode>", dealerId: "...", custId: "..." }
Response: {
  vehicles: [...],
  productRates: [...],
  dealers: [...],
  relationBalance: {...},
  order: {...} | null
}
```

One request. Server runs the 5 queries in parallel internally (`Promise.all`). Client consumes one payload.

---

## 2. Why BFF Instead of "Just Use Promise.all in the Client"?

The client **already** uses `Promise.all` via RTK Query's hooks firing in parallel. The network ping-pong is still the problem:

| Concern                    | Client-side `Promise.all`                         | Server-side BFF                                             |
| -------------------------- | ------------------------------------------------- | ----------------------------------------------------------- |
| Number of HTTP round-trips | 5                                                 | 1                                                           |
| TLS handshakes             | Already multiplexed (HTTP/2), so minor            | Same                                                        |
| JWT verify                 | 5× (one per request)                              | 1×                                                          |
| Express middleware chain   | 5×                                                | 1×                                                          |
| Headers overhead           | 5× ~800 bytes                                     | 1× ~800 bytes                                               |
| Latency (sum)              | max(RTT × 5 queries)                              | RTT × 1 (queries run in parallel on the server)             |
| Race conditions            | 5 independent errors, partial data possible       | One atomic success/failure                                  |
| Payload shape              | Client does `[v, r, d, b, o] = await Promise.all` | Server returns `{vehicles, rates, dealers, balance, order}` |
| Can drop unneeded fields   | No (endpoints return full shape)                  | Yes — BFF projects only what the screen needs               |

On a 4G connection with 150-300ms RTT, the HTTP overhead isn't just the network — it's the **serialized tail latency**. If all 5 requests finish in 100ms each but arrive back over a jittery cell network, the slowest one determines the "screen is usable" moment. Cutting to 1 request tightens that distribution significantly.

**The field-projection win is even bigger.** Several of the current list endpoints return 20+ fields per item when the screen only shows 4. A BFF can `.select('name dealer_code toGrt')` and cut the payload by 80%.

---

## 3. Current State (from code research)

### 3.1 Screens mapped with > 2 concurrent requests on mount

The full mapping is in the agent research; here's the high-value subset:

| Rank | Screen                      | File                                                 | Current requests                                                                           | Top BFF payoff |
| ---- | --------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------- |
| 1    | `Customer/NewOrder`         | `src/screens/Customer/NewOrder/index.js`             | `veh_trns_other`, `prod_msts_rate`, `dealer list`, `rel_bal`, (optional `one_order_by_so`) | ★★★★★          |
| 2    | `Common/Accounts` (ledger)  | `src/screens/Common/Accounts/index.js`               | `one_dealer_customer`, `year_month_acc`, `year_ob`, (lazy `month_acc`)                     | ★★★★★          |
| 3    | `Common/CompanyUsers`       | `src/screens/Common/CompanyUsers/index.js`           | `company_users`, `invites`, `sister_cust_msts`, `sister_dealer_msts`                       | ★★★★           |
| 4    | `Common/SisterCompanies`    | `src/screens/Common/SisterCompanies/index.js`        | `sister_cust_msts`, `sister_dealer_msts`, `invites`                                        | ★★★★           |
| 5    | `Customer/NewPayment`       | `src/screens/Customer/NewPayment/index.js`           | `invs_POST`, `one_dealer_customer`, `rel_bal`                                              | ★★★            |
| 6    | `Common/_Invoice_` (detail) | `src/screens/Common/_Invoice_/index.js`              | `one_invs`, `order_msts_by_so`, `one_dealer_customer_Q`                                    | ★★★            |
| 7    | `Common/Vehicles`           | `src/screens/Common/Vehicles/index.js`               | `veh_trns_other`, `dvr_msts_by_custid`                                                     | ★★             |
| 8    | `Dealer/NewInvoice`         | `src/screens/Dealer/NewInvoice/index.js`             | `dealer_custs_psocs`, `order_msts_so`                                                      | ★★             |
| 9    | `Home / Dashboard` (if any) | TBD — likely shows metrics from multiple collections | TBD                                                                                        | ★★★★           |

### 3.2 Composite endpoints that already exist (partial wins available)

- `fetch_invs_POST` — batch invoice fetch with filters
- `fetch_order_so_POST` — batch order fetch with filters
- `fetch_voc_inv_POST` — batch voucher fetch
- `fetch_dealer_customersList` — customer list with relation data (already partial BFF)
- `fetch_prods_rate_mstsquery` — batch product rates (already batches)
- `fetch_dealer_custs_psocs` — customer list with PSOC data (already partial BFF)

These are good signs: the API codebase is already comfortable with POST-body filter endpoints. Adding BFF endpoints on top is idiomatic.

### 3.3 Identified N+1 patterns (from agent research)

Worth fixing alongside BFF:

1. `Customer/NewOrder` — rates fetched per product selection
2. `Dealer/Products` — rate lookup per product
3. `Dealer/ProductDates` — historical rates per product
4. `Customer/Dealers` — per-dealer rate fetches
5. `Common/Accounts` — month detail loads per month selection
6. `Common/Reports/TcsTds` — per-month, per-company fetches

Several of these are solved _as a side effect_ of the BFF design. E.g., the NewOrder BFF returns product rates for all selectable products in one go, killing the per-product N+1.

---

## 4. Research & Technical Deep-Dive

### 4.1 BFF design principles

1. **One endpoint per screen, not per resource.** Don't build `GET /composite/vehicles+rates` (that's just a generic union). Build `POST /screens/new-order` — the endpoint name tells you which screen owns it, and if the screen changes, only this endpoint changes.
2. **POST, not GET.** BFFs take structured bodies (filters, IDs, permissions context). POST is the idiomatic choice for RPC-style calls and avoids URL length limits. The existing API already uses POST for filtered lists.
3. **Parallel queries on the server.** Each sub-query is a Mongoose call inside `Promise.all` or `Promise.allSettled`. Total latency = max(sub-query latency), not sum.
4. **Project fields aggressively.** Use `.lean()` (already enabled via `tasks_01/QW-1`) and `.select('field1 field2')` per query (part of `tasks_01/DB-7`). BFF responses should be ~50% smaller than the sum of the generic endpoints they replace.
5. **Minimal business logic.** A BFF is a **data fetcher and shaper**. It should not contain domain logic. If it needs to compute something (e.g. credit available = limit - balance), that logic should exist in a shared helper used by both the BFF and the generic endpoints.
6. **Graceful partial failure.** Use `Promise.allSettled` for non-critical sub-queries so one slow/failing collection doesn't tank the whole screen. Return `{vehicles: [...], productRates: null, productRatesError: 'timeout'}` and let the screen decide.
7. **Share auth / tenancy filters.** Every sub-query must respect the same user/company scope. Build a helper `buildTenancyFilter(req)` and pass it to every sub-query.
8. **Cacheable at the edge (optional).** Some BFF responses (dashboards) are safe to cache for 30 seconds. Use `Cache-Control` headers + the existing in-process cache from `tasks_01/CACHE-*`.

### 4.2 BFF vs GraphQL

A frequent question: "isn't GraphQL the real solution to this?" Short answer: GraphQL gives you the same benefits (one round-trip, client-chosen fields) but requires a query-parsing layer, a schema, resolver wiring, and a new mental model. It's **more flexible** but **more expensive** to introduce.

For DZZLO's current scale and team size, BFF endpoints are the pragmatic choice:

- 5-10 hand-written composite endpoints cover 90% of the traffic.
- No new tooling, no client-side GraphQL library, no schema to maintain.
- If in 12 months we have 30+ composite endpoints and they're starting to overlap, _that's_ the moment to reconsider GraphQL. Not before.

### 4.3 RTK Query integration on the client

Each BFF endpoint becomes **one** RTK Query endpoint on the client. The screen migrates from:

```js
// Before
const { data: vehicles } = useGetVehiclesQuery();
const { data: rates } = useGetRatesQuery({ dealerId });
const { data: dealers } = useGetDealersQuery();
const { data: balance } = useGetBalanceQuery({ custId, dealerId });
const isLoading = !vehicles || !rates || !dealers || !balance;
```

to:

```js
// After
const { data, isLoading } = useGetScreen_NewOrderQuery({
  dealerId,
  custId,
  orderId,
});
const { vehicles, productRates, dealers, relationBalance, order } = data ?? {};
```

**Cache tag strategy:** the BFF's `providesTags` lists every underlying resource:

```js
providesTags: (result) => [
  "screen_new_order",
  ...(result?.vehicles?.map((v) => ({ type: "veh_trns", id: v._id })) ?? []),
  ...(result?.productRates?.map((p) => ({ type: "prod_msts", id: p._id })) ??
    []),
  { type: "relations", id: `${arg.dealerId}_${arg.custId}` },
];
```

That way, when a mutation invalidates `{type: 'veh_trns', id: X}`, the BFF re-fetches automatically — the client doesn't need to know it came from a composite endpoint.

### 4.4 Versioning BFF endpoints

BFFs are tightly coupled to screens. If the screen changes shape, the endpoint changes shape. To prevent old app versions from breaking:

1. **Additive changes are free.** Adding a field to the response never breaks old clients. 95% of BFF evolution is additive.
2. **Breaking changes require versioning.** If we remove or rename a field, bump the endpoint path: `POST /api/v3/screens/new-order/v2`. Old app versions keep hitting v1. v1 is retired when analytics shows < 1% of traffic uses it.
3. **Feature flags for risky changes.** If we're unsure a new field is right, add it behind a request header: `X-BFF-Features: extended_credit_info`.

### 4.5 Error handling

A BFF has a subtle failure mode: if one sub-query errors, should the whole response fail?

**Rule of thumb:**

- **Critical sub-queries** (e.g. the current order being edited): use `Promise.all`. If one fails, fail the whole request.
- **Optional sub-queries** (e.g. "recent transactions" panel on a dashboard): use `Promise.allSettled`. Return nulls with error codes. Let the client show a partial screen with a warning banner.

Every BFF documents which sub-queries are critical and which are optional in the controller's JSDoc.

---

## 5. Target Architecture

```
┌────────────────────────────────────────┐
│          Mobile Client (App)           │
│                                        │
│   Screen:NewOrder                      │
│   └─ useGetScreen_NewOrderQuery(args)  │
└────────────────┬───────────────────────┘
                 │
                 │   1 HTTP POST
                 ▼
┌────────────────────────────────────────┐
│   POST /api/v3/screens/new-order       │
│                                        │
│   Express middleware:                  │
│    - auth (getUserFromToken)           │
│    - tenancy filter builder            │
│                                        │
│   Controller:                          │
│   ┌────────────────────────────────┐   │
│   │ const [vehicles, rates, ...]   │   │
│   │   = await Promise.all([        │   │
│   │     getVehicles(filter),       │   │
│   │     getProductRates(filter),   │   │
│   │     getDealers(filter),        │   │
│   │     getRelationBalance(...),   │   │
│   │     orderId ? getOrder() : null│   │
│   │   ]);                          │   │
│   │ return {                       │   │
│   │   vehicles, productRates, ...  │   │
│   │ };                             │   │
│   └────────────────────────────────┘   │
└────────────┬───────────────────────────┘
             │      │      │      │
             ▼      ▼      ▼      ▼
         veh_trns  prod  dealers rel_bal
         (Mongo)  (Mongo)(Mongo) (compute)
```

All sub-queries use the **existing service-layer functions** that the generic endpoints already call. The BFF controller is a thin orchestration shim.

---

## 6. Phased Rollout

Strategy: ship BFFs **one screen at a time**. Each screen is a self-contained PR:

1. API controller + route.
2. App RTK Query endpoint + screen migration.
3. Tests.
4. Verify old endpoints still work (they should — BFF is additive).

Order by impact (highest-payoff screens first).

### Phase 1 — Infrastructure: BFF conventions and helpers

**Goal:** establish the reusable bits before building the first BFF.

#### Step 1.1 — Create `/api_v3/controllers/screens/` directory

- All BFF controllers live here, one file per screen.
- Route file: `api_v3/routes/screens.js` registers them all under `/api/v3/screens/*`.

#### Step 1.2 — Create a tenancy helper

- New file: `api_v3/helpers/screensHelpers.js`
- Exports:
  - `buildTenancyFilter(req)` → `{co_id: req.user.co_id}` or similar based on role
  - `runParallel(tasks)` → wraps `Promise.all`, logs per-sub-query timing, collects errors
  - `runParallelSettled(tasks)` → wraps `Promise.allSettled` with a uniform result shape
  - `project(fields)` → shorthand for `.select(fields.join(' '))`

#### Step 1.3 — Reuse existing service functions

- Each BFF imports from existing services (`api_v3/services/*.js`), never from controllers.
- Controllers are HTTP adapters; services are the logic. BFFs are just new HTTP adapters that call multiple services.
- If a required query doesn't exist as a service function, factor it out of the controller into a service first.

#### Step 1.4 — BFF-specific middleware

- `api_v3/middleware/bffTiming.js` — adds `X-BFF-Timing: vehicles=34ms,rates=28ms,dealers=15ms` header. Essential for debugging "which sub-query is slow".
- Use the existing `protect` middleware for auth.

**Definition of Done:**

- `api_v3/helpers/screensHelpers.js` exists with unit tests.
- No BFFs yet.
- Existing routes untouched.

---

### Phase 2 — BFF #1: `POST /screens/new-order`

**Goal:** highest-impact screen first. 4-5 requests → 1.

#### Step 2.1 — API controller

- File: `api_v3/controllers/screens/newOrder.js`
- Body schema: `{orderId?: string, dealerId: string, custId: string}`
- Sub-queries (parallel):
  1. `vehTrnsService.listOther(filter)` — vehicles assigned to the customer's company
  2. `prodMstsService.ratesBatchForDealer(dealerId, filter)` — active product rates for this dealer
  3. `dealerCustsService.listDealersForCustomer(custId, filter)` — dealers that serve this customer
  4. `sectionalAccService.getRelationBalance({dealerId, custId})` — current balance for the dealer-customer relation
  5. (conditional) `orderMstsService.getOneByIdForEdit(orderId)` — only if editing an existing order
- Response shape:
  ```json
  {
    "vehicles": [{_id, veh_no, veh_cap, dvr}, ...],
    "productRates": [{_id, prod_id, rate, effective_from}, ...],
    "dealers": [{_id, dealer_name, toGrt, psoc}, ...],
    "relationBalance": {opening, current, credit_limit, available},
    "order": {...} | null
  }
  ```
- Critical: `vehicles`, `dealers`, `relationBalance`, `order` (if orderId given).
- Optional: `productRates` (screen can show a loading state for rates specifically if this fails).

#### Step 2.2 — Register route

- `api_v3/routes/screens.js`: `router.post('/new-order', protect, newOrderCtrl)`.

#### Step 2.3 — RTK Query endpoint

- New file: `src/store/apis/dzzlooms/screens.js`
- Defines a new slice `screensApi` or extends the existing `dzzlo-oms-api` (recommended: extend to share the cache).
- Endpoint: `getScreen_NewOrder: builder.query({query: (body) => ({url: '/screens/new-order', method: 'POST', body}), providesTags: ... })`

#### Step 2.4 — Migrate `Customer/NewOrder/index.js`

- Replace the 4-5 individual `useLazyXxxQuery`/`useXxxMutation` calls with one `useGetScreen_NewOrderQuery`.
- Keep the form-submit mutation (`useAdd_order_mstsMutation` / `useUpdate_order_mstsMutation`) untouched — BFFs are read-side only.
- On mutation success, invalidate the `'screen_new_order'` tag to re-fetch the BFF.
- Leave the existing single-purpose hooks in the codebase — other screens may still use them.

#### Step 2.5 — Tests

- API: integration test that calls the BFF with seed data, asserts all 5 arrays are populated.
- API: partial-failure test — mock `prodMstsService.ratesBatchForDealer` to throw, assert the response still returns `{vehicles, dealers, balance}` and `productRates: null, productRatesError: '...'`.
- App: Jest test that mocks the BFF response and renders the screen.

**Definition of Done:**

- Manual: open NewOrder screen, observe network tab: **1 request** instead of 4-5.
- `X-BFF-Timing` header shows all sub-queries under 200ms total.
- Screen behavior is identical to before (form, credit check, submit all work).

---

### Phase 3 — BFF #2: `POST /screens/accounts`

**Goal:** second-highest payoff. Accounts ledger currently fires 3-4 requests.

#### Step 3.1 — API controller

- File: `api_v3/controllers/screens/accounts.js`
- Body: `{dealerId, custId, year: '2026', month?: '04'}`
- Sub-queries:
  1. `dealerCustsService.getOneRelation({dealerId, custId})` — relation metadata
  2. `sectionalAccService.getYearMonthAcc({dealerId, custId, year})` — 12 months of summary
  3. `sectionalAccService.getYearOpeningBalance({dealerId, custId, year})` — opening balance
  4. (conditional) `sectionalAccService.getMonthDetail({dealerId, custId, year, month})` — if month is given, include detailed lines
- Response:
  ```json
  {
    "relation": {...},
    "yearMonth": [{month, total_inv, total_pay, closing}, ...],
    "openingBalance": {amount, asOf},
    "monthDetail": {invoices: [...], vouchers: [...]} | null
  }
  ```

#### Step 3.2 — RTK Query endpoint + migrate `Common/Accounts/index.js`

- Replace the 4 mutation hooks with one query hook.
- Month selection now triggers `refetch({month: selectedMonth})` instead of a separate mutation. The BFF handles the conditional month detail internally.

#### Step 3.3 — Pagination within month detail

- If `monthDetail.invoices` or `.vouchers` grows large (> 200 rows), do NOT stuff them into the BFF. Instead, return a count and a "click to load more" flag. Link to the existing paginated endpoints (which will be cursor-based after `04-cursor-pagination-infinite-scroll.md`).

**Definition of Done:**

- Accounts screen opens in < 400ms (previously ~700-1000ms on 4G).
- Month detail click fetches via the same hook.

---

### Phase 4 — BFF #3: `POST /screens/company-users`

**Goal:** merge users + invites + sister companies.

#### Step 4.1 — API controller

- File: `api_v3/controllers/screens/companyUsers.js`
- Body: `{}` — scoped by `req.user.co_id`
- Sub-queries:
  1. `usersService.getCompanyUsers(coId)` — users list
  2. `invitesService.getPendingInvites(coId)` — pending invites
  3. `custMstsService.getSisterCompanies(coId)` — if the current company is a customer
  4. `dealerMstsService.getSisterCompanies(coId)` — if the current company is a dealer
- Note: sub-queries 3 and 4 are mutually exclusive based on `onModel`. The controller checks `req.user.onModel` and only fires the relevant one.

#### Step 4.2 — Migrate `Common/CompanyUsers/index.js`

- One query hook replaces 4.
- When invites are accepted/declined, invalidate the `'screen_company_users'` tag (and also the individual `'invites'` tag so other places that use invites also refresh).

---

### Phase 5 — BFF #4: `POST /screens/sister-companies`

**Goal:** the Sister Companies screen currently duplicates part of CompanyUsers.

#### Step 5.1 — API controller

- File: `api_v3/controllers/screens/sisterCompanies.js`
- Body: `{}`
- Sub-queries: same 2-3 as CompanyUsers minus the users list.

**Definition of Done:** screen loads from 3 requests → 1.

---

### Phase 6 — BFF #5: `POST /screens/new-payment`

#### Step 6.1 — API controller

- File: `api_v3/controllers/screens/newPayment.js`
- Body: `{dealerId, custId}`
- Sub-queries:
  1. `invsService.getUnpaidInvoices({dealerId, custId})` — invoices eligible for payment
  2. `dealerCustsService.getOneRelation({dealerId, custId})` — relation detail
  3. `sectionalAccService.getRelationBalance(...)` — balance
- Response fits in one screen.

---

### Phase 7 — BFF #6: `POST /screens/invoice-detail`

#### Step 7.1 — API controller

- File: `api_v3/controllers/screens/invoiceDetail.js`
- Body: `{invoiceId}`
- Sub-queries:
  1. `invsService.getOne(invoiceId)` — invoice detail
  2. `orderMstsService.getBySoIds(invoice.order_ids)` — related orders
  3. `dealerCustsService.getOneRelation({dealerId, custId})` — relation info for ledger link

- Critical: invoice. Optional: related orders, relation.

---

### Phase 8 — BFF #7: `POST /screens/home` (Dashboard)

**Goal:** if there's a home/dashboard screen (TBD from screen audit), give it a dedicated BFF. Dashboards are the canonical BFF use case because they combine unrelated data sources.

#### Step 8.1 — Audit the home screen

- Find the home screen (likely `src/screens/Home/` or wired into the root stack).
- List everything it displays: recent orders, pending invoices, balance summary, notifications, etc.

#### Step 8.2 — API controller

- File: `api_v3/controllers/screens/home.js`
- Body: `{}` (pure tenancy scope)
- Sub-queries (all optional, parallelSettled):
  1. Recent orders (top 5)
  2. Unpaid invoices count + total amount
  3. Net balance across all relations
  4. Pending notifications count
  5. Recent activity feed

#### Step 8.3 — Caching

- Dashboard BFF responses can be cached for 30 seconds in-process (reuses `tasks_01/CACHE-*` infra). Cache key = userId.
- Add `Cache-Control: private, max-age=30` header.
- WebSocket events from `02-websocket-realtime.md` can also bust this cache via `invalidateCacheByUser(userId)`.

**Definition of Done:**

- Home screen open time drops from whatever it is today to a single RTT.

---

### Phase 9 — Monitoring & rollout

#### Step 9.1 — Log per-BFF metrics

For each BFF endpoint, log:

- P50, P95, P99 latency
- Per-sub-query timing (from `X-BFF-Timing`)
- Error rate, by sub-query
- Request rate
- Payload size (bytes)

#### Step 9.2 — Compare against pre-BFF baseline

Screen-level metric: "time from screen mount to first data-backed render". Client-side `performance.now()` around the first `isLoading → false` transition.

Collect this for 1 week before Phase 2 ships, then again after. Target: 30-50% reduction.

#### Step 9.3 — Keep old endpoints alive

Do not retire the generic endpoints (`fetch_veh_trns_other`, etc.) as part of this initiative. They're still needed by:

- Other non-BFF screens
- Admin tooling
- API v2 fallback
- Any future integration

BFFs are purely additive.

---

## 7. Benefits

| Benefit                                               | Before (Customer/NewOrder) | After                                |
| ----------------------------------------------------- | -------------------------- | ------------------------------------ |
| HTTP requests per screen open                         | 4-5                        | 1                                    |
| Sum of JWT verify operations                          | 4-5                        | 1                                    |
| Worst-case latency (4G, 300ms RTT)                    | ~1200-1500 ms              | ~400-500 ms                          |
| Payload size (with field projection)                  | ~80 KB                     | ~30-40 KB                            |
| Client-side orchestration code (lines of JS)          | ~40                        | ~5                                   |
| Race conditions (partial data)                        | Possible                   | Eliminated                           |
| Cache coherency (invalidating 1 tag refreshes screen) | Manual, error-prone        | Automatic via RTK Query providesTags |

Across the 5-7 heaviest screens, this is a meaningful perceived-performance win. On a flaky 3G connection, the difference is dramatic.

---

## 8. Risks & Rollback

| Risk                                                                 | Likelihood | Impact | Mitigation                                                                                                    |
| -------------------------------------------------------------------- | ---------- | ------ | ------------------------------------------------------------------------------------------------------------- |
| BFF becomes a "god endpoint" stuffed with every possible field       | Medium     | Medium | Rule: only include fields the screen _actually renders_. Code review.                                         |
| Coupling BFFs to screen shape forces frequent changes                | Medium     | Low    | Version the endpoint path (`/v2`) for breaking changes. Additive is free.                                     |
| One slow sub-query ruins the whole response                          | Medium     | Medium | `Promise.allSettled` for optional sub-queries; per-sub-query timeouts                                         |
| Duplicated business logic between BFF and generic endpoint           | Medium     | Medium | BFF calls service functions, not controllers. Services are the source of truth.                               |
| Client caches get out of sync between BFF and single-resource views  | Medium     | Medium | Rich `providesTags` so BFF participates in the same tag graph as generic endpoints                            |
| Performance regression if the sub-queries are serialized by accident | Low        | High   | Enforce `Promise.all[Settled]` via a lint rule or helper (`runParallel`). Timing header catches it in review. |

### Rollback plan

**Level 1:** if a specific BFF misbehaves, set a feature flag `BFF_NEW_ORDER_ENABLED=false`. The client falls back to a special branch that uses the old hooks. Ship as a client-side setting loadable at startup.

**Level 2:** remove the BFF route from `routes/screens.js`, redeploy API. Client gets 404; its RTK Query endpoint retries; eventually falls back to old behavior if the app has graceful degradation logic.

**Level 3:** revert the client migration. Old hooks are still in the codebase (we never deleted them); the screen just stops calling the BFF.

Because BFFs are additive and the old endpoints never go away, rollback is always cheap.

---

## 9. Testing Strategy

### 9.1 API tests

For each BFF:

- Happy-path integration test: seed DB, call endpoint, assert response shape + content.
- Partial-failure test: mock one sub-query to throw, assert `allSettled` behavior returns the rest.
- Tenancy test: call as user A, assert you can't see user B's company data.
- Performance test: assert p95 under 300ms with seeded dataset.
- Shape test: JSON schema validation of response.

### 9.2 Client tests

For each migrated screen:

- Jest test mocking the BFF response, rendering the screen, asserting all displayed fields come from the mock.
- Test the invalidation flow: fire a form submit, assert the BFF refetches.

### 9.3 Manual QA checklist per screen

- [ ] Open on fresh launch → screen renders fully
- [ ] Open while offline → cached data shown, refetch on reconnect
- [ ] Open while a related mutation is running → eventually converges
- [ ] Inspect network tab: **one** BFF request, no parallel single-resource requests

---

## 10. Open Questions

1. **Should BFFs be gRPC or HTTP+JSON?** HTTP+JSON, same as the rest of the API. Consistency > theoretical efficiency.
2. **GraphQL eventually?** Only if BFF count grows beyond ~15 and overlap becomes painful. Not a near-term concern.
3. **Should dashboard BFF be cached in Redis?** Not yet — in-process cache is enough at current scale. Revisit when `tasks_02/05-cicd-github-actions.md` Phase 2 gives us easy Redis provisioning.
4. **One API slice or multiple?** Extend the existing `dzzlo-oms-api` slice; keeps the cache coherent. Separate `screensApi` slice if we ever need a different base URL, which we don't.
5. **Auto-generate BFF types from Mongoose?** Nice-to-have. For now, inline TypeScript interfaces in each RTK Query endpoint file.

---

## Appendix A — Screen-to-BFF mapping quick reference

| Screen                            | BFF Endpoint                     | Replaces (# old hooks) |
| --------------------------------- | -------------------------------- | ---------------------- |
| `Customer/NewOrder/index.js`      | `POST /screens/new-order`        | 4-5                    |
| `Common/Accounts/index.js`        | `POST /screens/accounts`         | 3-4                    |
| `Common/CompanyUsers/index.js`    | `POST /screens/company-users`    | 4                      |
| `Common/SisterCompanies/index.js` | `POST /screens/sister-companies` | 3                      |
| `Customer/NewPayment/index.js`    | `POST /screens/new-payment`      | 3                      |
| `Common/_Invoice_/index.js`       | `POST /screens/invoice-detail`   | 3                      |
| `Home/index.js` (TBD)             | `POST /screens/home`             | N (dashboard)          |

## Appendix B — Naming convention

- Route: `POST /api/v3/screens/{kebab-case-screen-name}`
- Controller file: `api_v3/controllers/screens/{camelCaseScreenName}.js`
- RTK Query endpoint: `getScreen_{PascalCaseScreenName}`
- Cache tag: `'screen_{snake_case_screen_name}'`

Consistency makes code review trivial.
