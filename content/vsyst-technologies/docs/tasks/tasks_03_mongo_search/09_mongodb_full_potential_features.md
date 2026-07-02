# MongoDB Full Potential Features for DZZLO OMS

> A brainstorm document covering MongoDB capabilities beyond basic CRUD that
> DZZLO OMS can leverage to become faster, smarter, and more operationally
> efficient. Each feature is paired with a concrete, DZZLO-specific use case,
> an implementation sketch, and a rough effort rating.

---

## Table of Contents

1. [Why this document exists](#why-this-document-exists)
2. [Section A — Data-layer power features](#section-a--data-layer-power-features)
3. [Section B — Search, AI, and Intelligence](#section-b--search-ai-and-intelligence)
4. [Section C — Operations & Platform features](#section-c--operations--platform-features)
5. [Section D — Mobile & offline features](#section-d--mobile--offline-features)
6. [Priority ranking — "If you only do 3 things"](#priority-ranking--if-you-only-do-3-things)
7. [Cost considerations](#cost-considerations)
8. [Roadmap by quarter](#roadmap-by-quarter)

---

## Why this document exists

DZZLO OMS currently uses MongoDB as a "fancy JSON store" — documents in,
documents out, a few indexes, and Mongoose for validation. This is fine, but
MongoDB Atlas 7.0 / 8.0 ships with a *huge* amount of built-in functionality
that can replace entire chunks of application code, reduce infrastructure,
and unlock new product features.

This document brainstorms 20+ MongoDB capabilities and maps each one to a
real DZZLO use case. Not every feature should be adopted — the goal is to
make the team aware of what's possible, then pick the highest-ROI items.

Collections referenced throughout:
- `veh_msts` (vehicles)
- `order_msts` (orders)
- `dealer_msts` (dealers / gas stations)
- `cust_msts` (customers)
- `prod_msts` (products — fuel types, lubes, etc.)
- `dvr_msts` (drivers)
- `so_msts` (sales orders)
- `invs` (invoices)
- `pay_trns` (payment transactions)
- `rate_msts` (price / rate masters)
- `voc_msts` (vouchers)
- `veh_reqs` (vehicle requests)
- `veh_trns` (vehicle transactions / fuel dispensing)

---

## Section A — Data-layer power features

These are features built into the MongoDB server itself. No Atlas add-ons
required (except where noted). They mostly replace app-layer code.

### A1. Change Streams — real-time reactive backend

**What it is:**
A tailable cursor on the oplog that emits a document every time a collection
(or database) changes. Available on replica sets and sharded clusters.
Lets you subscribe to inserts, updates, deletes, and replaces without
polling.

**DZZLO use case:**
When a customer places a new order (`order_msts` insert), the dealer's
dashboard should update *live* — no refresh, no polling every 5 seconds.
Same for driver location updates, payment confirmations, and vehicle
dispensing events. Push notifications to the RN app fire off the same
stream.

**Implementation sketch:**

```js
// services/changeStreams/orderStream.js
const Order = require('../../models/order_mst');
const { sendPush } = require('../push');
const { io } = require('../socket');

function startOrderStream() {
  const pipeline = [
    { $match: { operationType: { $in: ['insert', 'update'] } } },
  ];

  const stream = Order.watch(pipeline, {
    fullDocument: 'updateLookup',
    resumeAfter: loadLastResumeToken(), // persisted across restarts
  });

  stream.on('change', async (evt) => {
    saveResumeToken(evt._id);
    const order = evt.fullDocument;

    if (evt.operationType === 'insert') {
      // notify dealer's web dashboard
      io.to(`dealer:${order.dealer_id}`).emit('order:new', order);
      // push to dealer's mobile app
      await sendPush({
        topic: `dealer_${order.dealer_id}`,
        title: 'New order',
        body: `Order #${order.order_no} from ${order.cust_name}`,
        data: { orderId: order._id.toString() },
      });
    }

    if (evt.operationType === 'update' && order.status === 'DELIVERED') {
      io.to(`cust:${order.cust_id}`).emit('order:delivered', order);
    }
  });

  stream.on('error', (err) => {
    console.error('order stream error', err);
    setTimeout(startOrderStream, 2000); // auto-reconnect
  });
}

module.exports = { startOrderStream };
```

**Benefits:**
- Kills all polling code (huge CPU savings on both client and server).
- Resume tokens mean you don't miss events during restarts.
- Scales to multiple API pods if you use a distributed resume-token store
  (Redis, a Mongo collection, or a leader-election lock).

Security note: keep push payloads minimal (ids over names/amounts where the
UX allows) — notification content transits Google/Apple infrastructure.

**Effort:** Medium. Infra-level work (resume token persistence, reconnect
logic, scaling across pods), but once the framework exists, adding new
streams is trivial.

---

### A2. Transactions (multi-document ACID)

**What it is:**
MongoDB has supported multi-document ACID transactions since 4.0 (4.2 for
sharded clusters). A transaction spans multiple writes across multiple
collections and either commits atomically or rolls back entirely.

**DZZLO use case:**
Placing an order touches several collections at once:
1. Insert into `order_msts`
2. Decrement `prod_msts.stock` (or update `dealer_inventory`)
3. Insert a `pay_trns` pending row
4. Increment `cust_msts.total_orders`
5. Possibly generate a voucher entry in `voc_msts`

If step 3 fails and the stock was already decremented, you've corrupted
inventory. Transactions prevent this.

**Implementation sketch:**

```js
// services/orders/placeOrder.js
const mongoose = require('mongoose');

async function placeOrder(payload) {
  const session = await mongoose.startSession();
  try {
    let order;
    await session.withTransaction(async () => {
      order = await Order.create([payload], { session });

      const product = await Product.findOneAndUpdate(
        { _id: payload.prod_id, stock: { $gte: payload.qty } },
        { $inc: { stock: -payload.qty } },
        { session, new: true },
      );
      if (!product) throw new Error('INSUFFICIENT_STOCK');

      await PayTrn.create([{
        order_id: order[0]._id,
        amount: payload.amount,
        status: 'PENDING',
      }], { session });

      await Customer.updateOne(
        { _id: payload.cust_id },
        { $inc: { total_orders: 1 } },
        { session },
      );
    }, {
      readConcern: 'snapshot',
      writeConcern: { w: 'majority' },
    });
    return order[0];
  } finally {
    session.endSession();
  }
}
```

**Where to use them:**
- Order placement (above)
- Payment settlement (mark invoice paid + create ledger entry + close
  outstanding)
- Vehicle assignment (lock vehicle + create request + update driver state)
- Voucher redemption (debit wallet + mark voucher used + create trn)

**Where NOT to use them:**
- Single-document updates (already atomic, no session needed).
- Analytics writes / append-only logs.
- Anything high-throughput with low consistency requirements (use
  eventual consistency instead).

**Effort:** Low per transaction once a helper is written. Medium if
introducing transactions for the first time — requires understanding of
read/write concerns and retryable writes.

---

### A3. Aggregation Pipeline — built-in analytics engine

**What it is:**
A stage-based data-processing pipeline that runs inside MongoDB. Stages
include `$match`, `$group`, `$lookup`, `$facet`, `$bucket`, `$unwind`,
`$project`, `$addFields`, `$setWindowFields`, `$graphLookup`, and many
more. Anything SQL can do, aggregation can do (plus things SQL can't).

**DZZLO use case:**
Dealer dashboard — a single API call that returns:
- Today's total sales
- Top 5 customers this month
- Revenue by product category
- Vehicle utilization (average orders per vehicle)
- Outstanding receivables
- Month-over-month growth

Doing this with N separate queries is slow and chatty. One aggregation
pipeline with `$facet` runs them all in parallel inside Mongo.

**Implementation sketch:**

```js
// services/analytics/dealerDashboard.js
async function dealerDashboard(dealerId) {
  const now = new Date();
  const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
  const startOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  return Order.aggregate([
    { $match: { dealer_id: dealerId, created_at: { $gte: startOfMonth } } },
    {
      $facet: {
        todaysSales: [
          { $match: { created_at: { $gte: startOfDay } } },
          { $group: { _id: null, total: { $sum: '$amount' }, count: { $sum: 1 } } },
        ],
        topCustomers: [
          { $group: { _id: '$cust_id', revenue: { $sum: '$amount' }, orders: { $sum: 1 } } },
          { $sort: { revenue: -1 } },
          { $limit: 5 },
          { $lookup: {
              from: 'cust_msts',
              localField: '_id',
              foreignField: '_id',
              as: 'customer',
          }},
          { $unwind: '$customer' },
        ],
        byProduct: [
          { $group: { _id: '$prod_id', revenue: { $sum: '$amount' } } },
          { $lookup: { from: 'prod_msts', localField: '_id', foreignField: '_id', as: 'product' } },
          { $unwind: '$product' },
        ],
        vehicleUtil: [
          { $group: { _id: '$veh_id', orders: { $sum: 1 }, revenue: { $sum: '$amount' } } },
          { $sort: { orders: -1 } },
        ],
        outstanding: [
          { $match: { payment_status: { $ne: 'PAID' } } },
          { $group: { _id: null, amount: { $sum: '$amount' } } },
        ],
        growth: [
          { $group: {
              _id: { y: { $year: '$created_at' }, m: { $month: '$created_at' } },
              revenue: { $sum: '$amount' },
          }},
          { $sort: { '_id.y': 1, '_id.m': 1 } },
        ],
      },
    },
  ]).allowDiskUse(false);
}
```

**Performance tips:**
- Put `$match` as early as possible to prune documents.
- Follow `$match` with an index-backed sort when possible.
- `$facet` runs its sub-pipelines in parallel but shares the input — use
  it when all facets operate on the same filtered set.
- Create supporting indexes: `{ dealer_id: 1, created_at: -1 }`.

**Effort:** Low-medium per pipeline. High the first time you internalize
the aggregation mental model.

---

### A4. Time Series Collections

**What it is:**
Special collection type (since 5.0, matured in 6.0+) that automatically
buckets time-ordered measurements for massive storage compression (5-10x)
and fast range queries. Transparent to app code — you insert and query
like a normal collection.

**DZZLO use case:**
Every fuel dispensing event, meter reading, and price change is
time-series data:

- **Meter readings** — every time a vehicle refuels, log odometer +
  dispensed litres. Plot fuel efficiency trends over months.
- **Fuel price history** — `rate_msts` changes over time. Time-series
  collection gives you "price at 2pm on 15-Mar-2025" in O(log n).
- **Pump dispensing rate** — raw sensor data from dispensers (litres per
  second) for detecting leaks or malfunctions.
- **Order velocity** — orders per hour per dealer for heat-map / ML
  forecasting.

**Implementation sketch:**

```js
// models/veh_meter_ts.js
db.createCollection('veh_meter_readings', {
  timeseries: {
    timeField: 'ts',
    metaField: 'veh_id',
    granularity: 'minutes',
  },
  expireAfterSeconds: 60 * 60 * 24 * 365 * 2, // 2-year auto-delete
});

// write
await db.collection('veh_meter_readings').insertOne({
  ts: new Date(),
  veh_id: 'VEH123',
  odometer: 45321,
  fuel_level: 12.3,
  dispensed_litres: 48.5,
  location: { type: 'Point', coordinates: [77.21, 28.61] },
});

// query — average litres dispensed per day in last 30 days
db.collection('veh_meter_readings').aggregate([
  { $match: { veh_id: 'VEH123', ts: { $gte: thirtyDaysAgo } } },
  { $group: {
      _id: { $dateTrunc: { date: '$ts', unit: 'day' } },
      total_litres: { $sum: '$dispensed_litres' },
  }},
  { $sort: { _id: 1 } },
]);
```

**Benefits:**
- Automatic bucketing — typically 5-10x less storage than raw inserts.
- Columnar-like compression for numeric fields.
- Purpose-built indexes (metaField + time).
- Works seamlessly with `$dateTrunc`, `$setWindowFields`, and Atlas
  Charts.

**Effort:** Low. Creating the collection is one command. Harder part is
deciding the granularity (seconds / minutes / hours) — choose carefully:
you can *increase* granularity later via `collMod`, but never decrease it,
and `timeField` / `metaField` are fully immutable.

---

### A5. Geospatial queries

**What it is:**
Native support for geographic data via 2dsphere indexes. Supports
`$geoNear`, `$geoWithin`, `$geoIntersects`, polygon queries, and
radius searches. Works with GeoJSON Point, LineString, Polygon, etc.

**DZZLO use case:**
DZZLO is a *gas station* OMS — location is core.
- **Nearest dealer** — when a customer opens the app, show the 5 closest
  gas stations.
- **Delivery zones** — each dealer serves a polygon; automatically
  route orders to the right dealer.
- **Route optimization** — group orders along a driver's route.
- **Geofencing** — alert when a vehicle leaves its assigned area.
- **Heat maps** — where are most orders coming from today?

**Implementation sketch:**

```js
// models/dealer_mst.js
DealerSchema.add({
  location: {
    type: { type: String, enum: ['Point'], default: 'Point' },
    coordinates: { type: [Number], required: true }, // [lng, lat]
  },
  delivery_zone: {
    type: { type: String, enum: ['Polygon'] },
    coordinates: [[[Number]]],
  },
});
DealerSchema.index({ location: '2dsphere' });
DealerSchema.index({ delivery_zone: '2dsphere' });

// nearest 5 dealers to customer
async function nearestDealers(lng, lat, maxKm = 10) {
  return Dealer.aggregate([
    {
      $geoNear: {
        near: { type: 'Point', coordinates: [lng, lat] },
        distanceField: 'distance_m',
        maxDistance: maxKm * 1000,
        spherical: true,
        query: { active: true },
      },
    },
    { $limit: 5 },
    { $addFields: { distance_km: { $divide: ['$distance_m', 1000] } } },
  ]);
}

// which dealer serves this address?
async function dealerForPoint(lng, lat) {
  return Dealer.findOne({
    delivery_zone: {
      $geoIntersects: {
        $geometry: { type: 'Point', coordinates: [lng, lat] },
      },
    },
  });
}
```

**Effort:** Low. Core Mongo feature, well-documented. The "hard" part is
collecting good coordinate data in the first place.

---

### A6. Schema validation via $jsonSchema

**What it is:**
Even though Mongoose validates at the application layer, MongoDB can
validate at the *server* layer with `$jsonSchema` or the older `validator`
option on `createCollection`. This catches bad writes from any source —
the Mongo shell, Compass, Atlas Data API, or buggy code that bypasses
Mongoose.

**DZZLO use case:**
Production safety net. If a dev ever runs a manual `updateOne` in Compass
that sets `amount: "five hundred"` instead of `500`, the write is
rejected. Protects against schema drift over years of evolution.

**Implementation sketch:**

```js
db.runCommand({
  collMod: 'order_msts',
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['order_no', 'dealer_id', 'cust_id', 'amount', 'status'],
      properties: {
        order_no: { bsonType: 'string', pattern: '^ORD-[0-9]{6}$' },
        dealer_id: { bsonType: 'objectId' },
        cust_id: { bsonType: 'objectId' },
        amount: { bsonType: 'double', minimum: 0 },
        status: {
          enum: ['PENDING', 'CONFIRMED', 'DISPATCHED', 'DELIVERED', 'CANCELLED'],
        },
        items: {
          bsonType: 'array',
          items: {
            bsonType: 'object',
            required: ['prod_id', 'qty', 'rate'],
            properties: {
              prod_id: { bsonType: 'objectId' },
              qty: { bsonType: 'double', minimum: 0 },
              rate: { bsonType: 'double', minimum: 0 },
            },
          },
        },
      },
    },
  },
  validationLevel: 'moderate',     // don't fail old docs
  validationAction: 'error',       // or 'warn' for gentler rollout
});
```

**Effort:** Low. A few hours to translate Mongoose schemas to JSON Schema.
Roll out with `validationAction: 'warn'` first to catch existing bad data.

> ⚠️ The sketch above is illustrative and does **not** match the real
> `order_msts` schema (`order_no` is a `Number` from the counters collection,
> the status field is `order_status`, and line items live in `products`, not
> `items`). Applying it verbatim with `validationAction: 'error'` would
> reject every legitimate write. Derive the validator from the actual
> Mongoose schema before running `collMod`.

---

### A7. TTL indexes

**What it is:**
A special single-field index with `expireAfterSeconds`. Mongo deletes
documents whose indexed date field is older than the TTL. Runs every
~60 seconds in a background task.

**DZZLO use case:**

| Collection | Purpose | TTL |
|---|---|---|
| `otp_tokens` | SMS OTP for login | 5 min |
| `dealer_invites` | One-time dealer signup links | 7 days |
| `sessions` | Rolling session records | 30 days |
| `push_notification_log` | Push delivery audit | 90 days |
| `temp_uploads` | Image upload staging | 24 h |
| `draft_orders` | Unsent order drafts | 48 h |
| `change_stream_resume` | Old resume tokens | 24 h |

**Implementation sketch:**

```js
// models/otp_token.js
const OtpSchema = new Schema({
  phone: { type: String, required: true, index: true },
  code: { type: String, required: true },
  created_at: { type: Date, default: Date.now },
});
OtpSchema.index({ created_at: 1 }, { expireAfterSeconds: 300 });
```

**Effort:** Very low. Five minutes per collection. Huge operational win —
you never have to write a cleanup cron again.

---

### A8. Partial indexes

**What it is:**
An index that only covers documents matching a filter expression. Since
you're indexing a subset, the index is smaller, faster to write, and uses
less memory.

**DZZLO use case:**

- Index **only active dealers** — most dealers are active, but historical
  inactive ones bloat the index. `{ active: true }`.
- Index **only unpaid invoices** — the unpaid set is small; the paid set
  is huge. Makes "list my outstanding invoices" instant.
- Index **only pending orders** — hot path for dealer dashboards.
- Index **only vehicles in service** — `{ status: 'ACTIVE' }`.

**Implementation sketch:**

```js
// Only unpaid invoices get indexed by due_date
InvoiceSchema.index(
  { dealer_id: 1, due_date: 1 },
  { partialFilterExpression: { payment_status: { $ne: 'PAID' } } },
);

// Only active vehicles get indexed for geo queries
VehicleSchema.index(
  { location: '2dsphere' },
  { partialFilterExpression: { status: 'ACTIVE' } },
);
```

**Effort:** Very low. Just add the option to existing `.index()` calls.

---

### A9. Materialized views via $merge / $out

**What it is:**
At the end of an aggregation pipeline, `$merge` writes the result into
another collection (or the same one). Combined with a scheduled job
or Atlas Trigger, you get pre-computed materialized views.

**DZZLO use case:**
Instead of recomputing the dealer dashboard on every page load, run a
nightly aggregation that populates a `dealer_daily_summary` collection.
Front-end reads from that — sub-millisecond, no pipeline.

**Implementation sketch:**

```js
// Run nightly at 2am IST
async function buildDailySummary() {
  const yesterday = dateUtil.startOfYesterdayIST();
  const today = dateUtil.startOfTodayIST();

  await Order.aggregate([
    { $match: { created_at: { $gte: yesterday, $lt: today } } },
    { $group: {
        _id: { dealer: '$dealer_id', date: yesterday },
        order_count: { $sum: 1 },
        revenue: { $sum: '$amount' },
        unique_customers: { $addToSet: '$cust_id' },
        products_sold: { $push: { prod: '$prod_id', qty: '$qty' } },
    }},
    { $project: {
        _id: 0,
        dealer_id: '$_id.dealer',
        date: '$_id.date',
        order_count: 1,
        revenue: 1,
        unique_customer_count: { $size: '$unique_customers' },
        products_sold: 1,
    }},
    { $merge: {
        into: 'dealer_daily_summary',
        on: ['dealer_id', 'date'],
        whenMatched: 'replace',
        whenNotMatched: 'insert',
    }},
  ]);
}
```

**Effort:** Medium — needs a scheduler (Atlas Triggers or app cron) and
careful handling of late-arriving data.

---

## Section B — Search, AI, and Intelligence

### B1. Atlas Search

Atlas Search is covered in detail in file `06_atlas_search_deep_dive.md`
and the implementation plans in `07_search_implementation_api.md` and
`08_search_implementation_app.md`. See those files.

**Short version:** Atlas Search embeds Apache Lucene directly in your
Atlas cluster. You get full-text search, fuzzy matching, autocomplete,
highlighting, facets, and BM25 relevance ranking — without running
Elasticsearch or OpenSearch. Use it for cross-entity search across
vehicles, orders, dealers, customers.

**Effort:** Medium.

---

### B2. Atlas Vector Search — semantic search & AI

**What it is:**
Atlas Search can also index dense vectors (embeddings) and do k-nearest-
neighbor queries with cosine / euclidean / dot-product similarity. This
is what powers RAG (retrieval-augmented generation), semantic search,
"more like this" recommendations, and chatbots over your own data.

**DZZLO use case:**

1. **"Find orders like this one"** — a dealer has a weird order dispute.
   Vectorize the order's items + customer notes + amount, then find the
   5 most similar past orders to see how they were resolved.

2. **Semantic product search** — customer types "diesel for my truck"
   and gets matched to the right `prod_mst` entry even though the
   product name is "HSD Bulk 2000L".

3. **AI support chatbot** — embed all invoices, orders, and customer
   history for a given dealer. Build a chatbot that can answer
   "How much did Kumar Transports owe me in March?" in natural
   language.

4. **Fraud detection** — vectorize each transaction's context; flag
   outliers from the cluster of normal transactions.

**Implementation sketch:**

```js
// 1. Generate embeddings (OpenAI, Voyage, or self-hosted)
const { OpenAI } = require('openai');
const openai = new OpenAI();
async function embed(text) {
  const r = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  });
  return r.data[0].embedding; // 1536 floats
}

// 2. Store on the document
await Order.updateOne(
  { _id: orderId },
  { $set: { embedding: await embed(summarize(order)) } },
);

// 3. Create a vector index in Atlas UI (or via Atlas CLI).
//    NOTE: every field used in $vectorSearch's `filter` must be declared
//    as a "filter" field in the index, alongside the vector:
// {
//   "fields": [
//     {
//       "type": "vector",
//       "path": "embedding",
//       "numDimensions": 1536,
//       "similarity": "cosine"
//     },
//     { "type": "filter", "path": "dealer_id" }
//   ]
// }

// 4. Query
async function similarOrders(order, k = 5) {
  const queryEmbedding = await embed(summarize(order));
  return Order.aggregate([
    {
      $vectorSearch: {
        index: 'order_vector_idx',
        path: 'embedding',
        queryVector: queryEmbedding,
        numCandidates: 100,
        limit: k,
        filter: { dealer_id: order.dealer_id }, // pre-filter
      },
    },
    { $addFields: { score: { $meta: 'vectorSearchScore' } } },
    { $unset: 'embedding' }, // $project can't mix exclusions with computed fields
  ]);
}
```

**Cost considerations:**
- Embedding API calls: ~$0.02 per 1M tokens with `text-embedding-3-small`.
- Vector storage inside Atlas: counts toward your cluster size.
- Re-embedding strategy: re-embed on document change (use a change
  stream to trigger it).

**Effort:** High for the first pipeline. Medium for subsequent use
cases once the embedding infra exists.

---

### B3. Atlas Charts

**What it is:**
A drag-and-drop visualization tool inside Atlas that connects directly
to your collections. Create bar charts, line charts, geospatial maps,
KPI tiles, and then embed them in external apps via signed URLs or
SDKs.

**DZZLO use case:**
- **Internal ops dashboard** — total orders, revenue, active vehicles,
  top dealers. Built in 30 minutes, no front-end code.
- **Dealer-facing embedded dashboards** — embed a sales-trend chart
  inside the dealer's mobile app using the Charts embedding SDK.
  Pre-filtered by dealer_id (using the filter token mechanism).
- **Executive reports** — schedule PDF exports and email them to
  management nightly.

**Implementation sketch:**

```js
// In React Native (or any web view)
import { ChartsEmbedSDK } from '@mongodb-js/charts-embed-dom';

const sdk = new ChartsEmbedSDK({
  baseUrl: 'https://charts.mongodb.com/charts-dzzlo-xxxx',
  getUserToken: async () => fetchSignedChartsTokenFromApi(),
});

const chart = sdk.createChart({
  chartId: 'sales-trend-chart',
  filter: { dealer_id: currentDealerId },
  theme: 'dark',
});

await chart.render(document.getElementById('chart-container'));
```

**Effort:** Low for internal dashboards. Medium for secure embedded
customer-facing charts (need signed tokens from your API).

---

## Section C — Operations & Platform features

### C1. Change Data Capture → analytics warehouse

**What it is:**
Use change streams to pipe every write into a downstream system —
BigQuery, Snowflake, S3, Kafka, etc. Atlas also provides a managed
"Atlas Stream Processing" service for this.

**DZZLO use case:**
Once DZZLO has 100+ dealers and millions of orders, running analytics
directly on the operational cluster is a bad idea (noisy neighbor on
a hot path). CDC pipes every change into a separate warehouse where
data scientists can run heavy queries without touching production.

**Implementation sketch:**

```js
// services/cdc/toBigQuery.js
const stream = Order.watch([], { fullDocument: 'updateLookup' });
stream.on('change', async (evt) => {
  await bigquery
    .dataset('dzzlo_analytics')
    .table('orders_cdc')
    .insert({
      op: evt.operationType,
      doc: evt.fullDocument,
      ts: evt.clusterTime,
    });
});
```

Or, the no-code Atlas-native path: use **Atlas Stream Processing** to
transform and route events directly from MongoDB to Kafka / S3 / etc.

**Effort:** Medium-high.

---

### C2. Atlas Triggers (database + scheduled)

**What it is:**
Serverless functions that fire on database events or on a cron schedule.
Written in Node.js, run in Atlas, no infrastructure. Two types:
- **Database triggers** — fire on insert/update/delete of a collection.
- **Scheduled triggers** — fire on a cron expression.

> Status check: Triggers (and the Functions they invoke) **survived** the
> 2024 App Services deprecation — they remain a supported standalone Atlas
> service. The rest of App Services did not (see C3 / D1).

**DZZLO use case:**

1. **Payment due reminders** (scheduled, daily 9am IST):
   Query invoices due in 3 days, fire off SMS / WhatsApp reminders.
2. **Nightly daily-summary build** (scheduled, daily 2am IST):
   Run the materialized view pipeline from A9.
3. **New dealer welcome flow** (database trigger on `dealer_msts`
   insert): Send welcome email, create default product catalog,
   provision Atlas Search index.
4. **Large order audit** (database trigger on `order_msts` insert
   with `amount > 100000`): Notify manager on Slack.
5. **Stale data archival** (scheduled weekly): Move orders older than
   2 years to Online Archive.

**Implementation sketch:**

```js
// Atlas Scheduled Trigger — payment reminders
exports = async function () {
  const mongodb = context.services.get('mongodb-atlas');
  const invoices = mongodb.db('dzzlo').collection('invs');

  const in3days = new Date();
  in3days.setDate(in3days.getDate() + 3);
  const today = new Date();

  const dueInvoices = await invoices.find({
    due_date: { $gte: today, $lte: in3days },
    payment_status: 'PENDING',
    reminder_sent: { $ne: true },
  }).toArray();

  for (const inv of dueInvoices) {
    await context.http.post({
      url: 'https://api.msg91.com/api/v5/flow/',
      headers: { authkey: [context.values.get('MSG91_KEY')] },
      body: JSON.stringify({
        flow_id: 'payment_reminder',
        mobiles: inv.cust_phone,
        amount: inv.amount,
      }),
    });
    await invoices.updateOne({ _id: inv._id }, { $set: { reminder_sent: true } });
  }
};
```

**Effort:** Low-medium. The triggers themselves are quick; the
integrations (SMS, email, Slack) are the work.

---

### C3. Atlas App Services / Functions — ⚠️ DEPRECATED, do not adopt

**Status:** MongoDB deprecated Atlas App Services in September 2024; HTTPS
Endpoints, the Data API, GraphQL, and standalone hosting reached
**end-of-life on September 30, 2025**. Only **Triggers** (and the functions
they invoke) survive as a supported service — see C2.

**What this means for DZZLO:**
- **Webhook receivers** (payment gateway callbacks) — implement as regular
  Express routes in `dzzlo_oms_api`, or as a small serverless function on
  your cloud provider (Lambda / Cloud Functions) if isolation is wanted.
- **Public quote generator** — same: an Express route or provider-native
  serverless function.
- **Lightweight admin tools** — use Atlas Charts (B3), Compass, or a small
  internal Express-served page.

**Effort:** n/a — struck from the roadmap.

---

### C4. Atlas Data Federation

**What it is:**
Query across multiple Atlas clusters, AWS S3 buckets, and HTTP data
sources using a single MongoDB query interface. Treats external data
as virtual collections.

**DZZLO use case:**
- Archive old orders to **S3 as Parquet** (cheap storage) but still
  query them via Data Federation when needed.
- Join **live order data** in the operational cluster with
  **historical orders** in S3 in a single aggregation.
- Query **reference data** stored in public S3 buckets (e.g.
  government fuel price reference data) without ingesting it.

**Implementation sketch:**
Configured in Atlas UI — create a "federated database instance", point
it at your collections + S3, get a new connection string. Then:

```js
// same API, behind the scenes joins Atlas + S3
const stats = await federatedDb.collection('all_orders').aggregate([
  { $match: { dealer_id, created_at: { $gte: fiveYearsAgo } } },
  { $group: { _id: { $year: '$created_at' }, revenue: { $sum: '$amount' } } },
]);
```

**Effort:** Medium.

---

### C5. Online Archive

**What it is:**
Automatic tiered storage. You define an archival rule ("orders older
than 24 months") and Atlas transparently moves documents to cheap
object storage. They remain queryable via the same connection — just
slower.

**DZZLO use case:**
DZZLO will eventually have tens of millions of old orders, vehicle
transactions, and invoices. Keeping them all hot in RAM is expensive.
Online Archive shrinks the live dataset while preserving query ability
for audits and reports.

Example rule: "Archive `order_msts` documents where
`created_at < now - 24 months` AND `status IN ('DELIVERED', 'CANCELLED')`."

**Benefits:**
- Working set stays small → faster queries, less RAM needed.
- Cheaper — archived data costs ~10% of live data.
- Same connection string — app code unchanged.

**Effort:** Very low. Configure in Atlas UI, done.

---

### C6. Queryable Encryption

**What it is:**
Encrypts specific fields *client-side* with keys you control, but still
lets you run equality (and some range) queries on the encrypted data.
MongoDB never sees the plaintext.

**DZZLO use case:**
Indian regulations around PII (phone numbers, GST numbers, Aadhaar,
PAN) are tightening. Queryable encryption lets you:
- Encrypt customer phone numbers at rest.
- Still search "find customer with phone 9876543210".
- Keep keys in AWS KMS / Azure Key Vault / GCP KMS — not in Atlas.

**Implementation sketch:**

```js
// models/cust_mst.js (using mongodb-client-encryption)
const encryptedFields = {
  fields: [
    {
      path: 'phone',
      bsonType: 'string',
      queries: { queryType: 'equality' },
      keyId: /* kmsKeyId */,
    },
    {
      path: 'gst_no',
      bsonType: 'string',
      queries: { queryType: 'equality' },
      keyId: /* kmsKeyId */,
    },
    {
      path: 'aadhaar_no',
      bsonType: 'string',
      keyId: /* kmsKeyId */, // stored encrypted, not queryable
    },
  ],
};

// queries work normally from authorized clients
await Customer.findOne({ phone: '9876543210' });
```

**Caveats:**
- Significant setup (KMS, client lib, key rotation policy).
- Some query types not supported (regex, text search on encrypted
  fields).
- Query performance is slower than plaintext.
- Requires MongoDB 7.0+ for GA.

**Effort:** High.

---

### C7. Multi-region clusters

**What it is:**
Atlas can spread a replica set across multiple AWS regions. Reads can
be routed to the nearest region for low latency.

**DZZLO use case:**
If DZZLO expands beyond north India to cover Mumbai, Chennai,
Bangalore, and Kolkata, latency from a single Mumbai primary will
start hurting the app. A multi-region cluster with a primary in
Mumbai + read replicas in Chennai and Delhi gives sub-50ms reads
nation-wide.

**Benefits:**
- Lower read latency for geographically distributed users.
- Higher availability — survive a region outage.
- Optional read preference `nearest` for eventual-consistency reads.

**Caveats:**
- Writes still go to the primary region.
- 3x the cost of a single-region cluster.
- Only worth it at scale.

**Effort:** Low (checkbox in Atlas) but high *cost*.

---

## Section D — Mobile & offline features

### D1. Offline-first sync — ⚠️ Atlas Device Sync / Realm is EOL

**Status:** Atlas Device Sync, the Atlas Device SDKs (Realm), and Edge
Server were deprecated in September 2024 and reached **end-of-life on
September 30, 2025**. The Realm SDKs are community/maintenance-only now. Do
**not** build new functionality on them.

**What it was:**
Native mobile SDKs (React Native, iOS, Android, .NET, Kotlin, Swift,
Flutter) providing a local, object-oriented database on the device, paired
with **Device Sync** for automatic bidirectional replication to Atlas.

**DZZLO use case:**
The RN app currently hits the API for everything. If a delivery driver
goes out of signal for 30 minutes on a rural delivery route, the app
is useless. Atlas Device Sync solves this:

- Driver opens orders while online → all assigned orders sync to
  local Realm DB on device.
- Driver loses signal → app still works, reads from local Realm.
- Driver marks an order delivered → written locally, queued for sync.
- Signal comes back → Realm automatically syncs the change to Atlas.

**Implementation sketch (historical — Realm API, now EOL; kept to illustrate the shape):**

```js
// App.tsx
import Realm, { createRealmContext } from 'realm';
import { AppProvider, UserProvider } from '@realm/react';

class Order extends Realm.Object {
  static schema = {
    name: 'Order',
    primaryKey: '_id',
    properties: {
      _id: 'objectId',
      order_no: 'string',
      status: 'string',
      amount: 'double',
      cust_name: 'string',
      delivery_address: 'string',
      dealer_id: 'objectId',
      driver_id: 'objectId?',
    },
  };
}

const { RealmProvider, useQuery, useRealm } = createRealmContext({
  schema: [Order],
});

// Flexible Sync — sync only orders for this driver
<AppProvider id="dzzlo-app-xyz">
  <UserProvider fallback={<LoginScreen />}>
    <RealmProvider
      sync={{
        flexible: true,
        initialSubscriptions: {
          update: (subs, realm) => {
            subs.add(realm.objects(Order).filtered('driver_id == $0', userId));
          },
        },
      }}
    >
      <App />
    </RealmProvider>
  </UserProvider>
</AppProvider>
```

**Caveats:**
- The MongoDB-native option no longer exists — if offline-first becomes a
  requirement, evaluate the replacements the ecosystem converged on:
  **PowerSync**, **Ditto**, **WatermelonDB / RxDB + a custom sync endpoint**,
  or SQLite with a hand-rolled queue-and-replay against the existing API.
- The hard problems are vendor-independent: schema kept in sync with
  Mongoose, a second data model to maintain, and conflict-resolution rules
  designed carefully (what happens if the driver marks an order delivered
  offline but a dispatcher cancelled it meanwhile?).

**Effort:** Very high. Only pursue if offline-first is a clear product
requirement — and budget a vendor evaluation first, since Device Sync's EOL
removed the default choice.

---

## Priority ranking — "If you only do 3 things"

Sorted by **ROI**: value delivered vs effort required, based on
DZZLO's current state and likely 12-month roadmap.

### Tier 1 — Do this quarter (high value, low-medium effort)

1. **TTL indexes + Partial indexes** (A7, A8) — Hours of work, immediate
   win. Smaller indexes, no cleanup crons, faster queries.
2. **Aggregation Pipeline for dashboards** (A3) — Replace N separate
   queries with one `$facet` pipeline. Dealer dashboards become 10x
   faster.
3. **Change Streams for real-time** (A1) — Kill polling, unlock live
   dashboards and push notifications. Foundation for many other
   features.

### Tier 2 — Do next quarter (high value, medium effort)

4. **Atlas Search** (B1) — Already being planned in files 06/07/08.
5. **Geospatial queries** (A5) — Core to the gas station product.
   Nearest dealer, delivery zones, route grouping.
6. **Atlas Triggers for automation** (C2) — Payment reminders, nightly
   reports, welcome flows. Kills lots of bespoke cron code.
7. **Schema validation via $jsonSchema** (A6) — Production safety net.
   Hours of work, years of peace.
8. **Time Series Collections** (A4) — For meter readings, dispensing
   rates, and price history. Low effort, huge storage savings later.

### Tier 3 — Do when the data grows (medium-to-high value, higher cost)

9. **Online Archive** (C5) — Kick in once the live set exceeds ~100 GB.
10. **Materialized views** (A9) — When dashboards start getting slow.
11. **Atlas Charts** (B3) — Quick wins for internal ops dashboards.
12. **Atlas Vector Search** (B2) — When AI features enter the roadmap.

### Tier 4 — Strategic / far future (high cost or high commitment)

13. **CDC to warehouse** (C1) — When data team wants independent analytics.
14. **Queryable Encryption** (C6) — When regulatory requirements demand.
15. **Multi-region clusters** (C7) — When DZZLO goes truly pan-India.
16. **Offline-first sync** (D1) — Only if offline-first becomes a product
    requirement. Note: Atlas Device Sync itself is EOL (Sept 2025) — this
    now means a third-party stack (PowerSync / Ditto / WatermelonDB).

### The "only 3 things" answer

If the team has literally 1 sprint of bandwidth for MongoDB
optimization, do these three:

1. **TTL + Partial indexes** (1 day) — free performance.
2. **Aggregation `$facet` for dealer dashboard** (2-3 days) — replaces
   the slowest endpoint in the API.
3. **Change Streams for live order notifications** (3-5 days) — a
   visible, marketable product improvement.

Total: one 2-week sprint, measurable impact on perf and UX.

---

## Cost considerations

A quick mental model of what costs what:

| Feature | Added cost | Notes |
|---|---|---|
| Change Streams | Free | Included in replica sets |
| Transactions | Free | Slight write overhead |
| Aggregation Pipeline | Free | CPU on your primary |
| Time Series Collections | Free | Actually *reduces* storage |
| Geospatial | Free | |
| Schema validation | Free | |
| TTL indexes | Free | |
| Partial indexes | Free | |
| $merge / $out | Free | |
| Atlas Search | Included up to limits | Extra nodes on bigger clusters |
| Atlas Vector Search | Counts toward Search | Embedding API calls extra |
| Atlas Charts | Free tier + paid | Viewer-based pricing |
| Atlas Triggers | Free tier + paid | Per invocation |
| Atlas App Services | — | Deprecated; EOL Sept 30, 2025 (Triggers survive) |
| Data Federation | Paid | Per query / data transfer |
| Online Archive | Paid | Much cheaper than live storage |
| Queryable Encryption | Infra + KMS costs | |
| Multi-region clusters | ~2-3x cluster cost | |
| Device Sync | — | EOL Sept 30, 2025 — use a third-party sync stack instead |

**Rule of thumb for DZZLO now (small/medium scale):** All the free,
server-level features in Section A are pure wins. Pick them up first.
Only start paying for Atlas-only features once you've measured the
need.

---

## Roadmap by quarter

A suggested rollout order, assuming the team has ~1 person spending
20% of their time on MongoDB optimization.

### Q1 — Foundations
- TTL indexes on all ephemeral collections
- Partial indexes on hot queries
- `$jsonSchema` validation on core collections (`order_msts`,
  `invs`, `pay_trns`)
- Aggregation `$facet` pipeline for the dealer dashboard API

### Q2 — Real-time + Location
- Change Streams for new order notifications
- Geospatial indexes + nearest-dealer endpoint
- Atlas Search (files 06-08) begins
- Time Series collection for meter readings

### Q3 — Automation + Analytics
- Atlas Triggers for payment reminders + nightly jobs
- Materialized views for dealer monthly summaries
- Atlas Charts embedded in the dealer app
- Online Archive rules configured (activate when dataset grows)

### Q4 — Intelligence
- Atlas Vector Search for "similar order" lookup
- Chatbot PoC using vector search + RAG
- CDC pipeline to BigQuery (if data team exists)
- Review and revisit the roadmap

---

## Appendix — Further reading

- MongoDB Docs: <https://www.mongodb.com/docs/manual/>
- Atlas Docs: <https://www.mongodb.com/docs/atlas/>
- Change Streams: <https://www.mongodb.com/docs/manual/changeStreams/>
- Aggregation: <https://www.mongodb.com/docs/manual/aggregation/>
- Time Series: <https://www.mongodb.com/docs/manual/core/timeseries-collections/>
- Atlas Search: <https://www.mongodb.com/docs/atlas/atlas-search/>
- Atlas Vector Search: <https://www.mongodb.com/docs/atlas/atlas-vector-search/>
- Atlas Triggers: <https://www.mongodb.com/docs/atlas/app-services/triggers/>
- Device Sync: <https://www.mongodb.com/docs/atlas/app-services/sync/>

---

*End of document. Companion files: 00 through 08 in the same directory.*
