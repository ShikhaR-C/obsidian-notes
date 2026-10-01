# 03 — Composite / BFF (Backend-For-Frontend) Endpoints

> Originally deferred as **Phase 3A** in the learning docs.
> Goal: collapse the 3-5 parallel requests fired by heavy screens into a single composite endpoint shaped for the exact screen that consumes it.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). The BFF pattern shipped, but as the screen redesign's v4 read models (redesign D2) at `/api/v4/screens/*` rather than `/api/v3/screens/*`, and for two screens this plan did not list — Dealer Customers and Daily Summary. Of 9 phases: Phase 1 ✅ in v4 form, Phase 9 🟡, Phases 2–7 (the six planned screens) ⬜, Phase 8 ⏸ as the plan itself says; three new tasks — X-V4-1, X-V4-2, T02-N2 (rows at the end). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## TL;DR

Today: the `Customer/NewOrder` screen fires 4-5 parallel HTTP requests on mount (vehicles, product rates, dealer list, relation balance, optional order detail). The `Common/Accounts` screen fires 3-4. The `Common/CompanyUsers` screen fires 2 (its sister-company hooks are commented out — see §3.1). Each request has its own round-trip, its own JWT verification, its own Mongoose hydration, and its own response parsing.

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

**Status (2026-10-01):** all eight mapped screens are still v1 on v3 (files present at app `ea7e7222`; `src/screens/v2/` holds only `Dealer/Customers` and `Common/DailySummary`). Several of their reads are v3 reads issued as mutations — `get_month_acc`, `get_year_month_acc`, `get_year_ob`, `fetch_one_dealer_customer` and `get_rel_bal` are among 16 read-named mutations of the app's 132 v3 endpoints (32 queries, 100 mutations; app:`src/store/apis/dzzlooms/*`, `balance/SectionalAcc.js`).

The full mapping is in the agent research; here's the high-value subset:

| Rank | Screen                      | File                                                 | Current requests                                                                           | Top BFF payoff |
| ---- | --------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------- |
| 1    | `Customer/NewOrder`         | `src/screens/Customer/NewOrder/index.js`             | `veh_trns_paginated`, `prod_msts_rate`, `customer_dealers`, `rel_bal`, (optional `one_order_by_so`) | ★★★★★          |
| 2    | `Common/Accounts` (ledger)  | `src/screens/Common/Accounts/index.js`               | `one_dealer_customer`, `year_month_acc`, `year_ob`, (lazy `month_acc`)                     | ★★★★★          |
| 3    | `Common/CompanyUsers`       | `src/screens/Common/CompanyUsers/index.js`           | `company_users`, `invites` — **only 2 fire**; the sister hooks are commented out (lines 37-38) | ★★             |
| 4    | `Common/SisterCompanies`    | `src/screens/Common/SisterCompanies/index.js`        | `invites` + one of `sister_cust_msts`/`sister_dealer_msts` (picked by `user.role`, lines 124-139) — **2 fire, not 3** | ★★             |
| 5    | `Customer/NewPayment`       | `src/screens/Customer/NewPayment/index.js`           | `invs_POST`, `one_dealer_customer`, `rel_bal`                                              | ★★★            |
| 6    | `Common/_Invoice_` (detail) | `src/screens/Common/_Invoice_/index.js`              | `one_invs`, `order_msts_by_so`, `one_dealer_customer_Q`                                    | ★★★            |
| 7    | `Common/Vehicles`           | `src/screens/Common/Vehicles/index.js`               | `veh_trns_paginated`, `veh_trns_reqCount`, `dvr_msts_by_custid`                            | ★★             |
| 8    | `Dealer/NewInvoice`         | `src/screens/Dealer/NewInvoice/index.js`             | `dealer_custs_psocs`, `order_msts_so`                                                      | ★★             |
| 9    | `Home / Dashboard`          | **Does not exist** — only `Demo/Dashboard` in the guest flow (`src/navigation/Guest/Main.js:10`) | N/A — see Phase 8                                                                          | N/A            |

### 3.2 Composite endpoints that already exist (partial wins available)

**Status (2026-10-01):** v3 still has the split screens that redesign D2 names — `POST so_msts/app/section1` + `section2` (api:`api_v3/routes/collections/so_msts.js:31-32`) and `order_msts/a/poso` GET + POST (api:`api_v3/routes/collections/order_msts.js:51-52`); v4 read models replace such pairs one screen at a time.

- `fetch_invs_POST` — batch invoice fetch with filters
- `fetch_order_so_POST` — batch order fetch with filters
- `fetch_voc_inv_POST` — batch voucher fetch
- `fetch_dealer_customersList` — customer list with relation data (already partial BFF)
- `fetch_prods_rate_msts` (in `prod_msts.js`) — batch product rates (already batches)
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

**Status (2026-10-01):** 🟡 principles 1–4 and 7 hold in the v4 read models — one route per screen (api:`api_v4/routes/screens.js:32-48`), POST bodies, fan-out only through `runParallel` (a conventions test forbids a bare `Promise.all`, api:`test/api_v4/lib/conventions.test.js:50-74`), `.select()` + `.lean()` + `maxTimeMS` on every read, tenancy from the token (api:`api_v4/lib/tenancy.js:64-138`). Principle 5 does not hold (X-V4-2); principle 6's `runSettled` has no caller; principle 8 is not built.

1. **One endpoint per screen, not per resource.** Don't build `GET /composite/vehicles+rates` (that's just a generic union). Build `POST /screens/new-order` — the endpoint name tells you which screen owns it, and if the screen changes, only this endpoint changes.
2. **POST, not GET.** BFFs take structured bodies (filters, IDs, permissions context). POST is the idiomatic choice for RPC-style calls and avoids URL length limits. The existing API already uses POST for filtered lists.
3. **Parallel queries on the server.** Each sub-query is a Mongoose call inside `Promise.all` or `Promise.allSettled`. Total latency = max(sub-query latency), not sum.
4. **Project fields aggressively.** Use `.lean()` (already enabled via `tasks_01/QW-1`) and `.select('field1 field2')` per query (part of `tasks_01/DB-7`). BFF responses should be ~50% smaller than the sum of the generic endpoints they replace.
5. **Minimal business logic.** A BFF is a **data fetcher and shaper**. It should not contain domain logic. If it needs to compute something (e.g. credit available = limit - balance), that logic should exist in a shared helper used by both the BFF and the generic endpoints.
6. **Graceful partial failure.** Use `Promise.allSettled` for non-critical sub-queries so one slow/failing collection doesn't tank the whole screen. Return `{vehicles: [...], productRates: null, productRatesError: 'timeout'}` and let the screen decide.
7. **Share auth / tenancy filters.** Every sub-query must respect the same user/company scope. Build a helper `buildTenancyFilter(req)` and pass it to every sub-query. Derive the scope from `req.user`, never from the request body. Note (code-verified): no index in `models/` involves `co_id` today — real query scoping in this codebase is by `cust_id`/`dealer_id`, so confirm the actual tenancy field and index it before the first BFF ships (see §11 Security).
8. **Cacheable at the edge (optional).** Some BFF responses (dashboards) are safe to cache for 30 seconds. Use `Cache-Control` headers + the existing in-process cache from `tasks_01/CACHE-*`.

### 4.2 BFF vs GraphQL

A frequent question: "isn't GraphQL the real solution to this?" Short answer: GraphQL gives you the same benefits (one round-trip, client-chosen fields) but requires a query-parsing layer, a schema, resolver wiring, and a new mental model. It's **more flexible** but **more expensive** to introduce.

For DZZLO's current scale and team size, BFF endpoints are the pragmatic choice:

- 5-10 hand-written composite endpoints cover 90% of the traffic.
- No new tooling, no client-side GraphQL library, no schema to maintain.
- If in 12 months we have 30+ composite endpoints and they're starting to overlap, _that's_ the moment to reconsider GraphQL. Not before.

### 4.3 RTK Query integration on the client

**Status (2026-10-01):** ✅ in v2 form — one v4 endpoint per screen on the shared `dzzlo-oms-api` instance (app:`src/store/apis/v4/customers.js`, `daily_summary.js`; redesign D9). Tags are coarse: Customers provides `relations/CUSTOMERS_LIST` (invalidated by five v1 writes), Daily Summary `order_msts_POST/LIST`, and no SO or invoice write invalidates Daily Summary (X-APP-3 in tasks_01).

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
providesTags: (result, error, arg) => [
  "screen_new_order",
  ...(result?.vehicles?.map((v) => ({ type: "veh_trns", id: v._id })) ?? []),
  ...(result?.productRates?.map((p) => ({ type: "prod_msts", id: p._id })) ??
    []),
  { type: "relations", id: `${arg.dealerId}_${arg.custId}` },
];
```

That way, when a mutation invalidates `{type: 'veh_trns', id: X}`, the BFF re-fetches automatically — the client doesn't need to know it came from a composite endpoint.

### 4.4 Versioning BFF endpoints

**Status (2026-10-01):** ✅ realised differently — a version path (`/api/v4`) instead of `/screens/<name>/v2`, and a per-screen server toggle for rollback: `screen_v2_<role>_<slug>` served by `GET /api/v4/app/features` (api:`helpers/appFeatures.js:34-101`; app:`src/navigation/screenRegistry.js:145-166`), with the v1 screen kept in the tree.

BFFs are tightly coupled to screens. If the screen changes shape, the endpoint changes shape. To prevent old app versions from breaking:

1. **Additive changes are free.** Adding a field to the response never breaks old clients. 95% of BFF evolution is additive.
2. **Breaking changes require versioning.** If we remove or rename a field, bump the endpoint path: `POST /api/v3/screens/new-order/v2`. Old app versions keep hitting v1. v1 is retired when analytics shows < 1% of traffic uses it.
3. **Feature flags for risky changes.** If we're unsure a new field is right, add it behind a request header: `X-BFF-Features: extended_credit_info`.

### 4.5 Error handling

**Status (2026-10-01):** 🟡 both helpers exist — `runParallel` (all-or-nothing) and `runSettled` (optional keys come back as `TIMEOUT` / `UNAVAILABLE` enums) in api:`api_v4/lib/compose.js` — but both read models use only `runParallel`; each read has a time limit that answers 503 `QUERY_TIMEOUT` (api:`api_v4/lib/limits.js:23-57`).

A BFF has a subtle failure mode: if one sub-query errors, should the whole response fail?

**Rule of thumb:**

- **Critical sub-queries** (e.g. the current order being edited): use `Promise.all`. If one fails, fail the whole request.
- **Optional sub-queries** (e.g. "recent transactions" panel on a dashboard): use `Promise.allSettled`. Return nulls with error codes. Let the client show a partial screen with a warning banner.

Every BFF documents which sub-queries are critical and which are optional in the controller's JSDoc.

---

## 5. Target Architecture

**Status (2026-10-01):** realised at `/api/v4/screens/*` (api:`api_v/api4.js`, api:`api_v4/index.js:69-84`) with v3's `protect` plus v4's own `requireRole` (not v3 `authorize`), the house validator and a per-user rate limit; the read models query the models directly and keep their own copies of several v3 rules rather than calling v3 services (X-V4-2).

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

**Status (2026-10-01):** ✅ done in v4 form (`api_v4/`, not `api_v3/`) — `lib/tenancy.js`, `lib/compose.js`, `lib/validate.js` (house DSL, redesign D7), `lib/errors.js`, `lib/respond.js`, `lib/roles.js`, `lib/limits.js`, `lib/rateLimit.js`; merged with PR #39 (api `6d41ce5`, 2026-09-30).

**Goal:** establish the reusable bits before building the first BFF.

#### Step 1.1 — Create `/api_v3/controllers/screens/` directory

**Status (2026-10-01):** ✅ as api:`api_v4/controllers/screens.js` + api:`api_v4/routes/screens.js`, mounted at `/api/v4/screens` (api:`api_v4/index.js:26-31`).

- All BFF controllers live here, one file per screen.
- Route file: `api_v3/routes/screens.js` registers them all under `/api/v3/screens/*`.

#### Step 1.2 — Create a tenancy helper

**Status (2026-10-01):** ✅ as api:`api_v4/lib/tenancy.js:64-138` — `tenantOf`, `scopeFilter` (`{dealer_id}` / `{cust_id}` ObjectIds from the token, which settles the `co_id` question) and `assertRelation`; `runParallel` / `runSettled` in `lib/compose.js`; no `project()` — each read `.select()`s.

- New file: `api_v3/helpers/screensHelpers.js`
- Exports:
  - `buildTenancyFilter(req)` → the caller's scope filter derived from `req.user`, branched by role. Caution: `{co_id: ...}` is unverified — no index anywhere involves `co_id`, and the codebase scopes queries by `cust_id`/`dealer_id`. Pin the real field down here and index it
  - `runParallel(tasks)` → wraps `Promise.all`, logs per-sub-query timing, collects errors
  - `runParallelSettled(tasks)` → wraps `Promise.allSettled` with a uniform result shape
  - `project(fields)` → shorthand for `.select(fields.join(' '))`

#### Step 1.3 — Reuse existing service functions

**Status (2026-10-01):** 🟡 dates reuse shared code (api:`api_v3/services/ledger_window.js` helpers), but the Customers read model re-implements v3 rules instead of calling services (api:`api_v4/readmodels/customers.js:108-148,270-347,476-570`) — X-V4-2.

- Each BFF imports from existing services (`api_v3/services/*.js`), never from controllers.
- Controllers are HTTP adapters; services are the logic. BFFs are just new HTTP adapters that call multiple services.
- If a required query doesn't exist as a service function, factor it out of the controller into a service first.

#### Step 1.4 — BFF-specific middleware

**Status (2026-10-01):** 🟡 auth ✅ (`protect` + `requireRole` per module and route, api:`api_v4/index.js:72-79`) and validation ✅ (api:`api_v4/lib/validate.js`, unknown keys → 400 `VALIDATION`); the timing header exists as `timingHeader` (`X-V4-Timing`, silent in production) but has no caller (api:`api_v4/lib/compose.js:201-216`; API-7 is deferred — X-PERF-2 in tasks_01).

- `api_v3/middleware/bffTiming.js` — adds `X-BFF-Timing: vehicles=34ms,rates=28ms,dealers=15ms` header. Essential for debugging "which sub-query is slow". **Emit it only outside production** (or gate to admin users) — per-sub-query timings leak internal architecture and create a timing side-channel.
- Auth: apply `protect` **and** `authorize(...)` on every screens route. Mechanics (code-verified): `protect` (`api_v3/auth.js:61`) does not verify the JWT itself — the global `logging()` middleware does that via `getUserFromToken` (`helpers/middlewares.js:233`) and sets `req.loggedInUser`; `protect` just 401s when it's absent. Existing collection routes import `protect`/`authorize` but mostly leave them commented out — BFF routes must not copy that pattern.
- Validation: the API currently has **no input-validation library**. Add one (Joi/celebrate or zod) in this phase and give every BFF a body schema — ObjectId format checks, unknown fields rejected (see §11).

**Definition of Done:**

- `api_v3/helpers/screensHelpers.js` exists with unit tests.
- No BFFs yet.
- Existing routes untouched.

---

### Phase 2 — BFF #1: `POST /screens/new-order`

**Status (2026-10-01):** ⬜ to do — Customer/NewOrder is still v1 (app:`src/screens/Customer/NewOrder/index.js`) and api:`api_v4/routes/screens.js` has no new-order route.

**Goal:** highest-impact screen first. 4-5 requests → 1.

#### Step 2.1 — API controller

**Status (2026-10-01):** ⬜ to do.

- File: `api_v3/controllers/screens/newOrder.js`
- Body schema: `{orderId?: string, dealerId: string, custId: string}` — validated (ObjectId formats, unknown fields rejected). IDOR guard: for customer-role callers derive `custId` from `req.user` instead of trusting the body, and verify the `{dealerId, custId}` relation belongs to the caller before firing sub-queries (see §11).
- Sub-queries (parallel):
  1. `vehTrnsService.listForCustomer(filter)` — vehicles for the customer (the screen consumes `fetch_veh_trns_paginated` today, not `veh_trns_other` — mirror that query)
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

**Status (2026-10-01):** ⬜ to do — it would be `POST /api/v4/screens/new-order` with `requireRole` + `validate`, as the two v4 routes are (api:`api_v4/routes/screens.js:33-48`).

- `api_v3/routes/screens.js`: `router.post('/new-order', protect, authorize('customer'), validate(newOrderSchema), newOrderCtrl)`.

#### Step 2.3 — RTK Query endpoint

**Status (2026-10-01):** ⬜ to do — the v4 pattern is a module under app:`src/store/apis/v4/` on the shared instance, not `dzzlooms/screens.js`.

- New file: `src/store/apis/dzzlooms/screens.js`
- Defines a new slice `screensApi` or extends the existing `dzzlo-oms-api` (recommended: extend to share the cache).
- Endpoint: `getScreen_NewOrder: builder.query({query: (body) => ({url: '/screens/new-order', method: 'POST', body}), providesTags: ... })`

#### Step 2.4 — Migrate `Customer/NewOrder/index.js`

**Status (2026-10-01):** ⬜ to do.

- Replace the 4-5 individual `useLazyXxxQuery`/`useXxxMutation` calls with one `useGetScreen_NewOrderQuery`.
- Keep the form-submit mutation (`useAdd_order_mstsMutation` / `useUpdate_order_mstsMutation`) untouched — BFFs are read-side only.
- On mutation success, invalidate the `'screen_new_order'` tag to re-fetch the BFF.
- Leave the existing single-purpose hooks in the codebase — other screens may still use them.

#### Step 2.5 — Tests

**Status (2026-10-01):** ⬜ to do.

- API: integration test that calls the BFF with seed data, asserts all 5 arrays are populated.
- API: partial-failure test — mock `prodMstsService.ratesBatchForDealer` to throw, assert the response still returns `{vehicles, dealers, balance}` and `productRates: null, productRatesError: '...'`.
- App: Jest test that mocks the BFF response and renders the screen.

**Definition of Done:**

- Manual: open NewOrder screen, observe network tab: **1 request** instead of 4-5.
- `X-BFF-Timing` header shows all sub-queries under 200ms total.
- Screen behavior is identical to before (form, credit check, submit all work).

---

### Phase 3 — BFF #2: `POST /screens/accounts`

**Status (2026-10-01):** ⬜ to do — Common/Accounts is still v1 and still reads through four read-named mutations (`fetch_one_dealer_customer`, `get_year_month_acc`, `get_year_ob`, `get_month_acc`).

**Goal:** second-highest payoff. Accounts ledger currently fires 3-4 requests.

#### Step 3.1 — API controller

**Status (2026-10-01):** ⬜ to do.

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

**Status (2026-10-01):** ⬜ to do.

- Replace the 4 mutation hooks with one query hook.
- Month selection now triggers `refetch({month: selectedMonth})` instead of a separate mutation. The BFF handles the conditional month detail internally.

#### Step 3.3 — Pagination within month detail

**Status (2026-10-01):** ⬜ to do — v4 keyset paging now exists for such a list (api:`api_v4/lib/cursor.js`).

- If `monthDetail.invoices` or `.vouchers` grows large (> 200 rows), do NOT stuff them into the BFF. Instead, return a count and a "click to load more" flag. Link to the existing paginated endpoints (which will be cursor-based after `04-cursor-pagination-infinite-scroll.md`).

**Definition of Done:**

- Accounts screen opens in < 400ms (previously ~700-1000ms on 4G).
- Month detail click fetches via the same hook.

---

### Phase 4 — BFF #3: `POST /screens/company-users`

**Status (2026-10-01):** ⬜ to do — app:`src/screens/Common/CompanyUsers/index.js` is still v1.

**Goal:** merge users + invites + sister companies.

#### Step 4.1 — API controller

**Status (2026-10-01):** ⬜ to do.

> **Corrected scope (code-verified):** the screen fires only **2** requests today — `company_users` and `invites`; the sister-company hooks in `CompanyUsers/index.js` are commented out (lines 37-38). Sister-company data belongs to the `SisterCompanies` screen (Phase 5). This BFF is a 2 → 1 merge with a correspondingly smaller payoff — consider shipping it in the same PR as Phase 5.

- File: `api_v3/controllers/screens/companyUsers.js`
- Body: `{}` — scoped entirely from `req.user`, nothing client-supplied
- Sub-queries:
  1. `usersService.getCompanyUsers(coId)` — users list
  2. `invitesService.getPendingInvites(coId)` — pending invites

#### Step 4.2 — Migrate `Common/CompanyUsers/index.js`

**Status (2026-10-01):** ⬜ to do.

- One query hook replaces 2.
- When invites are accepted/declined, invalidate the `'screen_company_users'` tag (and also the individual `'invites'` tag so other places that use invites also refresh).

---

### Phase 5 — BFF #4: `POST /screens/sister-companies`

**Status (2026-10-01):** ⬜ to do — app:`src/screens/Common/SisterCompanies/index.js` is still v1.

**Goal:** merge the Sister Companies screen's two mount requests into one. (Code-verified: sister-company data lives only on this screen — the copies in CompanyUsers are commented out.)

#### Step 5.1 — API controller

**Status (2026-10-01):** ⬜ to do.

- File: `api_v3/controllers/screens/sisterCompanies.js`
- Body: `{}`
- Sub-queries: `invites` + **one** sister-company list. The screen picks the sister query by `user.role` (`SisterCompanies/index.js:124-139` — `customer` → `sister_cust_msts`, `dealer` → `sister_dealer_msts`; the other trigger is a no-op). The controller branches on `req.user.role` the same way.

**Definition of Done:** screen loads from 2 requests → 1.

---

### Phase 6 — BFF #5: `POST /screens/new-payment`

**Status (2026-10-01):** ⬜ to do — app:`src/screens/Customer/NewPayment/index.js` is still v1.

#### Step 6.1 — API controller

**Status (2026-10-01):** ⬜ to do.

- File: `api_v3/controllers/screens/newPayment.js`
- Body: `{dealerId, custId}`
- Sub-queries:
  1. `invsService.getUnpaidInvoices({dealerId, custId})` — invoices eligible for payment
  2. `dealerCustsService.getOneRelation({dealerId, custId})` — relation detail
  3. `sectionalAccService.getRelationBalance(...)` — balance
- Response fits in one screen.

---

### Phase 7 — BFF #6: `POST /screens/invoice-detail`

**Status (2026-10-01):** ⬜ to do — app:`src/screens/Common/_Invoice_/index.js` is still v1.

#### Step 7.1 — API controller

**Status (2026-10-01):** ⬜ to do.

- File: `api_v3/controllers/screens/invoiceDetail.js`
- Body: `{invoiceId}`
- Sub-queries — **two-stage, not fully parallel**: 2 and 3 need values from the fetched invoice (`order_ids`, `dealer_id`, `cust_id`), so fetch the invoice first, then `Promise.allSettled` the rest.
  1. `invsService.getOne(invoiceId)` — invoice detail. Must be **tenancy-scoped in the query itself** — a bare `findById` here is an IDOR letting any authenticated user read any invoice (see §11).
  2. `orderMstsService.getBySoIds(invoice.order_ids)` — related orders
  3. `dealerCustsService.getOneRelation({dealerId, custId})` — relation info for ledger link (IDs from the fetched invoice, never the request body)

- Critical: invoice. Optional: related orders, relation.

---

### Phase 8 — BFF #7: `POST /screens/home` (Dashboard)

**Status (2026-10-01):** ⏸ deferred by the plan itself — there is still no real dashboard, only the guest-flow `src/screens/Demo/Dashboard`.

**Goal (code-verified: currently moot):** no Home/Dashboard screen exists for real users — the only dashboard is `src/screens/Demo/Dashboard`, used exclusively by the guest flow (`src/navigation/Guest/Main.js:10`); Customer/Dealer navigation opens straight into the transaction tabs. **Skip this phase** unless a real dashboard gets built; the steps below are the blueprint for that day, because dashboards are the canonical BFF use case (they combine unrelated data sources).

#### Step 8.1 — Audit the home screen

**Status (2026-10-01):** ⏸ deferred with Phase 8.

- Find the home screen (likely `src/screens/Home/` or wired into the root stack).
- List everything it displays: recent orders, pending invoices, balance summary, notifications, etc.

#### Step 8.2 — API controller

**Status (2026-10-01):** ⏸ deferred with Phase 8.

- File: `api_v3/controllers/screens/home.js`
- Body: `{}` (pure tenancy scope)
- Sub-queries (all optional, parallelSettled):
  1. Recent orders (top 5)
  2. Unpaid invoices count + total amount
  3. Net balance across all relations
  4. Pending notifications count
  5. Recent activity feed

#### Step 8.3 — Caching

**Status (2026-10-01):** ⏸ deferred with Phase 8.

- Dashboard BFF responses can be cached for 30 seconds in-process (reuses `tasks_01/CACHE-*` infra). Cache key = userId.
- Add `Cache-Control: private, max-age=30` header.
- WebSocket events from `02-websocket-realtime.md` can also bust this cache via `invalidateCacheByUser(userId)`.

**Definition of Done:**

- Home screen open time drops from whatever it is today to a single RTT.

---

### Phase 9 — Monitoring & rollout

**Status (2026-10-01):** 🟡 measured for the two v4 screens, not per BFF in production (steps below).

#### Step 9.1 — Log per-BFF metrics

**Status (2026-10-01):** 🟡 client side only — a Firebase Performance trace `rtkq_<endpoint>` per request (app:`src/store/middleware/rtkQueryPerfLogger.js:25`) and an HTTP metric per attempt (app:`src/store/apis/createApi.js:59-94`), where `v4_screen_*` names separate the v4 calls; no server-side per-route metrics (Server-Timing is API-7, deferred).

For each BFF endpoint, log:

- P50, P95, P99 latency
- Per-sub-query timing (from `X-BFF-Timing`)
- Error rate, by sub-query
- Request rate
- Payload size (bytes)

#### Step 9.2 — Compare against pre-BFF baseline

**Status (2026-10-01):** 🟡 before/after measured once, on a local scale seed — Customers 1,525 → 134 ms median server time (api:`docs/v4-performance.md:247-257`) — not on devices over a week.

Screen-level metric: "time from screen mount to first data-backed render". Client-side `performance.now()` around the first `isLoading → false` transition.

Collect this for 1 week before Phase 2 ships, then again after. Target: 30-50% reduction.

#### Step 9.3 — Keep old endpoints alive

**Status (2026-10-01):** ✅ the v3 endpoints stay, and the v1 screens stay as the registry's fallback (app:`src/navigation/screenRegistry.js:145-166`).

Do not retire the generic endpoints (`fetch_veh_trns_paginated`, `fetch_veh_trns_other`, etc.) as part of this initiative. They're still needed by:

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

**Level 2:** remove the BFF route from `routes/screens.js`, redeploy API. **Caution — this alone breaks migrated clients:** RTK Query does not retry 404s by default and no graceful-degradation branch exists in the app. Only safe after the Level 1 flag/fallback has shipped in the client; treat this as post-rollback server cleanup, not a rollback mechanism.

**Level 3:** revert the client migration. Old hooks are still in the codebase (we never deleted them); the screen just stops calling the BFF.

Because BFFs are additive and the old endpoints never go away, rollback is always cheap.

---

## 9. Testing Strategy

### 9.1 API tests

**Status (2026-10-01):** ✅ for the two v4 screens — tenancy and 403 for an unrelated or unknown company (api:`test/api_v4/screens/daily-summary.test.js`), shape through the v4 fixtures drift detector (api:`test/api_v4/contract/fixtures.test.js`), constant round trips (api:`test/api_v4/screens/customers.test.js:2147-2234`); partial-failure tests exist only for the lib's `runSettled` (api:`test/api_v4/lib/compose.test.js`), and no p95 test (performance is measured by `scripts/perf/*`).

For each BFF:

- Happy-path integration test: seed DB, call endpoint, assert response shape + content.
- Partial-failure test: mock one sub-query to throw, assert `allSettled` behavior returns the rest.
- Tenancy test: call as user A, assert you can't see user B's company data.
- IDOR test, per body parameter: call as customer A passing customer B's `custId` / another relation's `dealerId` / another company's `invoiceId`/`orderId` — assert 403/404 and zero foreign data in the payload. Every ID the body accepts gets one of these.
- Performance test: assert p95 under 300ms with seeded dataset.
- Shape test: JSON schema validation of response.

### 9.2 Client tests

**Status (2026-10-01):** ✅ for the two v2 screens — Tier 3 suites (e.g. app:`src/screens/v2/Dealer/Customers/__tests__/Customers.test.js`, app:`src/screens/v2/Common/DailySummary/__tests__/DailySummary.test.js`) and Tier 2 MSW suites (app:`src/store/apis/v4/__tests__/customers.msw.test.js`, `daily_summary.msw.test.js`).

For each migrated screen:

- Jest test mocking the BFF response, rendering the screen, asserting all displayed fields come from the mock.
- Test the invalidation flow: fire a form submit, assert the BFF refetches.

### 9.3 Manual QA checklist per screen

**Status (2026-10-01):** ❔ device runs for the two screens are recorded in app:`docs/screens/customers-v2.md` and `docs/screens/daily-summary-v2.md`; not verifiable from code.

- [ ] Open on fresh launch → screen renders fully
- [ ] Open while offline → cached data shown, refetch on reconnect
- [ ] Open while a related mutation is running → eventually converges
- [ ] Inspect network tab: **one** BFF request, no parallel single-resource requests

---

## 10. Open Questions

**Status (2026-10-01):** Q1 and Q4 are settled as proposed — v4 is HTTP+JSON on the shared `dzzlo-oms-api` instance (redesign D9; app:`src/store/apis/v4/base.js:43-45`); Q2, Q3 and Q5 are open (the v4 client has no type definitions).

1. **Should BFFs be gRPC or HTTP+JSON?** HTTP+JSON, same as the rest of the API. Consistency > theoretical efficiency.
2. **GraphQL eventually?** Only if BFF count grows beyond ~15 and overlap becomes painful. Not a near-term concern.
3. **Should dashboard BFF be cached in Redis?** Not yet — in-process cache is enough at current scale. Revisit when `tasks_02/05-cicd-github-actions.md` Phase 2 gives us easy Redis provisioning.
4. **One API slice or multiple?** Extend the existing `dzzlo-oms-api` slice; keeps the cache coherent. Separate `screensApi` slice if we ever need a different base URL, which we don't.
5. **Auto-generate BFF types from Mongoose?** Nice-to-have. For now, inline TypeScript interfaces in each RTK Query endpoint file.

---

## 11. Security Requirements

**Status (2026-10-01):** for v4, items 1–5 and 7 hold: bearer and role on every route (api:`api_v4/index.js:72-79`), the one body id membership-checked before any read (api:`api_v4/readmodels/dailySummary.js:319-326`), unknown keys rejected, a per-user limiter on the screen routes (api:`api_v4/lib/rateLimit.js`), `INTERNAL` errors scrubbed, the timing header silent in production. Item 6 (field-level authorization) is T02-N2; item 8 has no cache to govern. For the v3 routes see the security items in tasks_01 (X-SEC-1).

Current posture, code-verified in `dzzlo_oms.js`: helmet (`:85`), global `sanitizeMongo()` / mongo-sanitize (`:82`), `express.json({ limit: "1mb" })` (`:59`), JWT verified in the global `logging()` middleware via `getUserFromToken`, `authLimiter` on auth routes. Gaps this initiative must not inherit: **no input-validation library anywhere**, per-route `protect`/`authorize` mostly commented out, global rate limiter commented out (`dzzlo_oms.js:88-95`), `cors()` fully open (relevant because `dip-web` is a browser client).

Every BFF endpoint must satisfy all of:

1. **AuthN + AuthZ on the route.** `router.post('/x', protect, authorize(<roles>), validate(schema), ctrl)` — no exceptions, no commented-out middleware.
2. **IDOR guards.** Any ID accepted in the body (`custId`, `dealerId`, `orderId`, `invoiceId`) is either derived from `req.user` instead, or verified to belong to the caller **before** sub-queries run — the unique `{dealer_id, cust_id}` index on `dealer_custs` (model lines 121-123) makes relation membership a cheap existence check. Fetch-by-id sub-queries include the tenancy filter in the query itself — never a bare `findById`.
3. **Input validation.** Schema-validate every body: ObjectId formats, types, unknown fields rejected. `sanitizeMongo` strips `$`-operators but not non-`$` garbage (`custId: {a: 1}` → CastError 500s without validation).
4. **Rate limiting.** One BFF request fans out to ~5 DB queries — add a per-user `express-rate-limit` on `/api/v3/screens/*` (the dependency is already installed).
5. **Error hygiene.** Partial-failure fields (`productRatesError`) are enum codes (`'timeout' | 'unavailable'`), never raw `err.message`/Mongo errors.
6. **Field-level authorization.** Financial fields (`relationBalance.credit_limit`, `available`) go only to roles entitled to them; enforce in the shared service helper so the BFF and generic endpoints agree.
7. **`X-BFF-Timing` disabled in production** (or admin-gated).
8. **Caching (if Phase 8 ever ships):** in-process cache keyed by `userId` + role/company; `Cache-Control: private, max-age=30`; never cacheable by shared proxies.

---

## Appendix A — Screen-to-BFF mapping quick reference

**Status (2026-10-01):** ⬜ all six rows (the screens are still v1, no route exists); built instead: `POST /api/v4/screens/customers` (Dealer Customers) and `POST /api/v4/screens/daily-summary` (Dealer and Customer Daily Summary).

| Screen                            | BFF Endpoint                     | Replaces (# old hooks) |
| --------------------------------- | -------------------------------- | ---------------------- |
| `Customer/NewOrder/index.js`      | `POST /screens/new-order`        | 4-5                    |
| `Common/Accounts/index.js`        | `POST /screens/accounts`         | 3-4                    |
| `Common/CompanyUsers/index.js`    | `POST /screens/company-users`    | 2                      |
| `Common/SisterCompanies/index.js` | `POST /screens/sister-companies` | 2                      |
| `Customer/NewPayment/index.js`    | `POST /screens/new-payment`      | 3                      |
| `Common/_Invoice_/index.js`       | `POST /screens/invoice-detail`   | 3                      |
| `Home/index.js` (does not exist)  | `POST /screens/home`             | skip — no such screen  |

## Appendix B — Naming convention

**Status (2026-10-01):** ❌ superseded by the redesign's conventions — `POST /api/v4/screens/<kebab-slug>`, read model `api_v4/readmodels/<camelCase>.js`, RTK endpoints `v4_screen_<snake>` and `v4_screen_<snake>_next`, v3 tag types shared (redesign D2, D9).

- Route: `POST /api/v3/screens/{kebab-case-screen-name}`
- Controller file: `api_v3/controllers/screens/{camelCaseScreenName}.js`
- RTK Query endpoint: `getScreen_{PascalCaseScreenName}`
- Cache tag: `'screen_{snake_case_screen_name}'`

Consistency makes code review trivial.

## New tasks — from the app v2 / API v4 review (2026-10-01)

Rows owned by this doc; the folder's full table is in [00-overview.md](./00-overview.md).

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-V4-1 | 🆕 Close the v4 foundation gaps: a JSON `NOT_FOUND` / 405 answer for unknown paths and methods inside `/api/v4`, a v4-shaped answer (with `error_code`) for a malformed JSON body, and a `maxTimeMS` on the app-features read | `buildV4` mounts only the modules and `errorHandler` (api:`api_v4/index.js:69-84`), so an unknown path falls through to Express's HTML 404; a malformed body fails in the global `express.json` and is answered by the v3 handler, which sends no `error_code` (api:`dzzlo_oms.js:59,136`, api:`helpers/error.js:31-34`; inferred, no test); `NOT_FOUND` / `CONFLICT` are catalogued but never raised (api:`api_v4/lib/errors.js:27-34`); `counters.findOne` has no `maxTimeMS` (api:`helpers/appFeatures.js:70`) | API | S | — |
| X-V4-2 | 🆕 Decide where business rules live. The v4 Customers read model holds its own copies — credit ratio, FY ledger fold, outstanding PO/SO aggregates, opening balance — plus a new integer-paise money rule, each held to v3 by parity tests. A question for the user, not a decision | api:`api_v4/readmodels/customers.js:108-148,270-347,476-570`, api:`api_v4/lib/money.js:1-22` against api:`.ai/agents/versioning-agent.md:68` ("read models compose `api_v3/services`, they do not re-implement rules"), redesign D1 and this plan's principle 5 (§4.1) | API | M | user decision |
| T02-N2 | 🆕 Enforce field-level authorization on the server for the permission-gated fields of the v4 read models, or record that gating them in the app is accepted | §11 item 6 asks for server-side field authorization; the v4 Customers read model kept v3's model, in which the membership permission is applied only in the app (app:`src/helpers/Permissions/index.js:1-31` — "These decide what is *rendered*"), so v4 neither widened nor narrowed access | API | S | user decision |
