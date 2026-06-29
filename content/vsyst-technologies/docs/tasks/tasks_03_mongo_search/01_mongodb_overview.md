# MongoDB: A Teaching Guide for JavaScript / Node Developers

> Audience: A developer who is comfortable with JavaScript and Node.js but wants to deeply understand MongoDB and how it is used inside the **DZZLO OMS** project (`dzzlo_oms_api` + `dzzlo_oms_app`).
>
> Goal: By the end of this document, you should be able to reason about documents, collections, indexes, aggregation pipelines, and Mongoose — and map every concept back to the real entities in our codebase (`veh_msts`, `order_msts`, `dealer_msts`, `cust_msts`, `prod_msts`).

---

## Table of Contents

1. [What MongoDB Is (and Is Not)](#1-what-mongodb-is-and-is-not)
2. [BSON, JSON, and Why It Matters](#2-bson-json-and-why-it-matters)
3. [Databases, Collections, Documents, Fields](#3-databases-collections-documents-fields)
4. [`_id` and ObjectId](#4-_id-and-objectid)
5. [Schema-less vs Schema-on-Read (and How Mongoose Adds Schema Back)](#5-schema-less-vs-schema-on-read-and-how-mongoose-adds-schema-back)
6. [CRUD Operations with Concrete Examples](#6-crud-operations-with-concrete-examples)
7. [Indexes — Why They Matter](#7-indexes--why-they-matter)
8. [The Aggregation Pipeline](#8-the-aggregation-pipeline)
9. [Replica Sets & Sharding (Conceptual)](#9-replica-sets--sharding-conceptual)
10. [MongoDB Atlas — The Managed Service](#10-mongodb-atlas--the-managed-service)
11. [When to Use MongoDB vs SQL](#11-when-to-use-mongodb-vs-sql)
12. [Mongoose vs the Native Driver](#12-mongoose-vs-the-native-driver)
13. [Putting It Together — DZZLO OMS Entities](#13-putting-it-together--dzzlo-oms-entities)

---

## 1. What MongoDB Is (and Is Not)

**MongoDB is a document database.** Instead of storing data as rows inside tables with fixed columns (like MySQL/Postgres/SQL Server), it stores data as _documents_ — flexible, JSON-like structures — inside _collections_.

If you have written JavaScript objects like this:

```js
const order = {
  order_no: 1042,
  cust_id: "665f1b3e...",
  products: [
    { prod_name: "PETROL", quantity: 10, rate: 102.5 },
    { prod_name: "DIESEL", quantity: 5, rate: 91.2 },
  ],
  on_dt: new Date("2026-04-10T09:00:00Z"),
};
```

…then you already think in MongoDB's data model. MongoDB essentially lets you save that whole object as a single unit. There is **no need to pre-declare columns**, and nested arrays/objects are first-class.

### Key properties at a glance

| Property         | MongoDB                                           | SQL (Postgres/MySQL)            |
| ---------------- | ------------------------------------------------- | ------------------------------- |
| Storage unit     | Document (BSON)                                   | Row (tuple)                     |
| Container        | Collection                                        | Table                           |
| Schema           | Flexible, enforced by the application             | Rigid, enforced by the database |
| Joins            | `$lookup` (aggregation) or application-side       | `JOIN` (first-class)            |
| Transactions     | Yes (multi-document since 4.0)                    | Yes                             |
| Query language   | JSON-shaped objects + operators (`$gt`, `$in`, …) | SQL text                        |
| Horizontal scale | Native sharding                                   | Add-on / manual                 |

### What MongoDB is NOT

- It is **not** a key-value store (though keys exist). It is a _document_ store that lets you query _inside_ values.
- It is **not** SQL — there is no `SELECT … JOIN …` syntax. You use the **MongoDB Query Language (MQL)**.
- It is **not** schemaless in practice. Most real apps — including this one — use **Mongoose** to enforce shape.

---

## 2. BSON, JSON, and Why It Matters

You write queries in JSON (or JS objects), but MongoDB **stores data as BSON** (Binary JSON). BSON is a binary serialization format that extends JSON with:

- **Types JSON cannot represent**: `ObjectId`, `Date`, `Decimal128`, `Binary`, `Int32`/`Int64`, `Regex`, `Timestamp`.
- **Length-prefixing**: each document knows its size, so MongoDB can skip to the next record without parsing every byte.
- **Ordered keys**: unlike JSON, BSON preserves insertion order of fields.

### Why a Node dev should care

When you do this in our project:

```js
const order = await Order.findOne({ _id: orderId });
console.log(order.on_dt instanceof Date); // true
```

You get a real JavaScript `Date`, not a string — because BSON stored it as a `Date` type and the driver converted it back. The same holds for `ObjectId`. If you try to `JSON.stringify()` a document directly, `ObjectId` becomes a string, but inside MongoDB it remains a 12-byte binary value.

```js
// BSON round-trip preserves types; naive JSON does not
const bad = JSON.parse(JSON.stringify(order)); // dates become strings :(
const good = order.toObject(); // dates stay dates :)
```

---

## 3. Databases, Collections, Documents, Fields

The hierarchy is simple:

```
MongoDB server (replica set / cluster)
 └── Database             e.g.  dzzlo_oms
      └── Collection      e.g.  order_msts
           └── Document   e.g.  { _id, cust_id, products: [...], on_dt }
                └── Field e.g.  "order_no": 1042
```

- A **database** is a namespace for collections. Our project talks to a single logical database on Atlas.
- A **collection** is the equivalent of an SQL table. By convention, names are plural and suffixed with `_msts` (masters) or `_trns` (transactions) in this project: `veh_msts`, `order_msts`, `dealer_msts`, `cust_msts`, `prod_msts`, `veh_trns`, `pay_trns`.
- A **document** is a single JSON-like record. It has a maximum BSON size of **16 MB**.
- A **field** is a key-value pair inside a document. Values can themselves be documents or arrays, producing _embedded documents_.

### Example: `veh_msts` document

Looking at `dzzlo_oms_api/models/veh_msts.js`, a vehicle document looks roughly like this when stored:

```json
{
  "_id":          ObjectId("665f1b3e0a..."),
  "cust_id":      ObjectId("665f1a9a12..."),
  "veh_reg_no":   "KA05MG1234",
  "route":        "North Zone",
  "createdAt":    ISODate("2026-03-01T10:00:00Z"),
  "updatedAt":    ISODate("2026-04-10T08:30:12Z"),
  "__v":          0
}
```

Notice that the `cust_id` field is an `ObjectId` that refers to a document in `cust_msts`. MongoDB does **not** enforce this reference (unlike a foreign key); Mongoose provides the `ref:` hint so we can `populate()` it at query time.

---

## 4. `_id` and ObjectId

Every document in MongoDB must have a field called `_id`. If you don't set one, MongoDB generates an `ObjectId` for you.

### What is an ObjectId?

It is a **12-byte binary value** shaped like this:

```
| 4 bytes: seconds since epoch | 5 bytes: random value | 3 bytes: counter |
```

Important consequences:

1. **It is monotonically (roughly) increasing over time**. You can extract the creation timestamp: `ObjectId("...").getTimestamp()`.
2. **It is globally unique** without needing a centralized sequence. Multiple app servers can mint `ObjectId`s concurrently with negligible collision risk.
3. **It is 12 bytes**, which keeps indexes compact. A SQL `BIGINT` is 8 bytes, a `UUID` is 16 bytes; `ObjectId` sits in between.
4. **Sorting by `_id`** is approximately sorting by insert time — often "good enough" for listing recent records.

```js
// In Mongoose models like dzzlo_oms_api/models/order_msts.js:
const Schema  = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

// Field that references another collection
dealer_id: { type: ObjectId, ref: "dealer_msts" }
```

### Can `_id` be something other than an ObjectId?

Yes. It can be a string, a number, or even an embedded document, as long as it is unique per collection. For `order_msts`, the app uses an auto-incrementing `order_no` field _in addition to_ `_id`, using the `counters` collection (see `models/counters.js`). The `_id` stays an `ObjectId`, and `order_no` is the human-friendly number shown in the app.

---

## 5. Schema-less vs Schema-on-Read (and How Mongoose Adds Schema Back)

### "Schema-less" is a half-truth

The MongoDB _server_ does not require you to define columns. You can insert `{ name: "alpha" }` today and `{ name: "beta", age: 30, tags: ["x"] }` tomorrow into the same collection, and both succeed. This is called **schema-on-read**: the application decides what shape to expect when it reads.

That flexibility is powerful during prototyping but dangerous at scale. Without rules, you end up with:

- Typos (`cust_id` vs `custId` vs `customerId`) coexisting in the same collection.
- Wrong types (`rate: "10.5"` as a string, `rate: 10.5` as a number).
- Missing fields.
- Orphaned references.

### Enter Mongoose

Mongoose is an **ODM** (Object Document Mapper). It sits on top of the native MongoDB driver and lets you declare a schema in your application. DZZLO OMS uses Mongoose `^9.4.1`.

```js
// Simplified form of dzzlo_oms_api/models/veh_msts.js
const mongoose = require("mongoose");
const Schema = mongoose.Schema;
const ObjectId = Schema.Types.ObjectId;

const veh_mst_Schema = new mongoose.Schema(
  {
    cust_id: { type: ObjectId, ref: "cust_msts" },
    veh_reg_no: {
      type: String,
      validate: {
        validator: (v) =>
          /(^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{4}$)|(^\d{2}BH\d{4}[A-Z]{1,2}$)/.test(
            v,
          ),
        message: (props) => `${props.value} is not a valid Vehicle Number!`,
      },
    },
    route: { type: String },
  },
  { timestamps: true }, // auto createdAt / updatedAt
);

veh_mst_Schema.index({ cust_id: 1 });
veh_mst_Schema.index({ veh_reg_no: 1 });

module.exports = mongoose.model("veh_msts", veh_mst_Schema);
```

Mongoose adds back everything the bare server doesn't give you:

| Feature            | Native driver | Mongoose |
| ------------------ | :-----------: | :------: |
| Enforced types     |      no       |   yes    |
| Required fields    |      no       |   yes    |
| Validators         |      no       |   yes    |
| Default values     |      no       |   yes    |
| Virtual fields     |      no       |   yes    |
| Pre/post hooks     |      no       |   yes    |
| `populate()` joins |      no       |   yes    |
| `timestamps: true` |      no       |   yes    |

At query time Mongoose casts types for you (e.g. a string `"665f…"` becomes a real `ObjectId` when you query by `_id`).

### Schema validation at the server level

MongoDB _does_ support JSON-schema-based validation (via `$jsonSchema`) on the collection, independent of Mongoose. It's useful as a final safety net if multiple services write to the same collection. This project currently relies on Mongoose for validation and does not define server-level `$jsonSchema` rules.

---

## 6. CRUD Operations with Concrete Examples

CRUD stands for **Create, Read, Update, Delete**. We'll show each both with the native driver (so you see "what MongoDB really does") and with Mongoose (what the codebase uses).

Assume a collection `order_msts` and a Mongoose model `Order`:

```js
const Order = require("./models/order_msts");
```

### 6.1 Create — `insertOne` / `insertMany`

Native driver:

```js
await db.collection("order_msts").insertOne({
  cust_id: new ObjectId("665f1a9a12..."),
  order_no: 1042,
  products: [{ prod_name: "PETROL", quantity: 10, rate: 102.5 }],
  on_dt: new Date(),
  order_status: "CREATED",
});
```

Mongoose:

```js
await Order.create({
  cust_id: "665f1a9a12...", // cast to ObjectId automatically
  order_no: 1042,
  products: [{ prod_name: "PETROL", quantity: 10, rate: 102.5 }],
  on_dt: new Date(),
  order_status: "CREATED",
});
```

Bulk insert:

```js
await Order.insertMany([order1, order2, order3]);
```

### 6.2 Read — `find`, `findOne`, filter operators

Find all _delivered_ orders for one customer, newest first:

```js
const rows = await Order.find({
  cust_id: "665f1a9a12...",
  order_status: "DELIVERED",
})
  .sort({ on_dt: -1 })
  .limit(20)
  .lean(); // return plain objects (faster) instead of Mongoose docs
```

### Query operators you'll see constantly

```js
// equality
{ status: "DELIVERED" }

// comparison
{ rate: { $gt: 100, $lte: 110 } }

// membership
{ order_status: { $in: ["CREATED", "DISPATCHED"] } }

// negation
{ order_status: { $ne: "CANCELLED" } }

// existence
{ remarks: { $exists: true } }

// regex (indexable if anchored)
{ veh_reg_no: { $regex: /^KA05/ } }

// logical combinations
{
  $and: [
    { on_dt: { $gte: new Date("2026-04-01") } },
    { on_dt: { $lt:  new Date("2026-05-01") } },
  ],
  $or: [
    { "products.prod_name": "PETROL" },
    { "products.prod_name": "DIESEL" },
  ],
}
```

Note how we query into arrays: `products.prod_name` dives into each element of the `products` array. MongoDB does this natively — no JOIN required — which is one of its superpowers.

### Projections — "only these fields please"

```js
Order.find(
  { cust_id: "..." },
  { order_no: 1, on_dt: 1, _id: 0 }, // SELECT order_no, on_dt
);
```

### 6.3 Update — `updateOne`, `updateMany`, `$set`, `$inc`, `$push`

Update operators _mutate in place_, which is safer than reading, mutating in JS, and writing back.

```js
// Mark a single order as delivered
await Order.updateOne(
  { _id: orderId },
  { $set: { order_status: "DELIVERED", delivered_at: new Date() } },
);

// Atomically increment a counter (used for order_no generation)
await Counter.updateOne(
  { _id: "order_no" },
  { $inc: { seq: 1 } },
  { upsert: true },
);

// Add a new line to an array
await Order.updateOne(
  { _id: orderId },
  { $push: { products: { prod_name: "LUBE", quantity: 1, rate: 450 } } },
);

// Update many at once
await Order.updateMany(
  { order_status: "CREATED", on_dt: { $lt: cutoff } },
  { $set: { order_status: "EXPIRED" } },
);
```

#### `findOneAndUpdate` — read + write in one atomic call

```js
const updated = await Order.findOneAndUpdate(
  { _id: orderId, order_status: "CREATED" },
  { $set: { order_status: "DISPATCHED" } },
  { new: true }, // return the updated doc
);
```

This is the MongoDB idiom for _compare-and-swap_: the filter guarantees you only flip to `DISPATCHED` if the order is still `CREATED`, in a single atomic operation.

### 6.4 Delete — `deleteOne`, `deleteMany`

```js
await Order.deleteOne({ _id: orderId });
await Order.deleteMany({ order_status: "CANCELLED", on_dt: { $lt: old } });
```

In practice, many apps prefer **soft deletes** (`is_deleted: true`) so you can audit or restore. Whether to soft-delete is a design choice — the DZZLO OMS mixes both styles across collections.

---

## 7. Indexes — Why They Matter

Without an index, every query becomes a **collection scan**: MongoDB reads every document to decide which match. With 10,000 orders that's fine; with 10 million it will bring your Atlas cluster to its knees.

An **index** is an auxiliary data structure (B-tree) that lets MongoDB find matching documents by key lookup instead of scanning. Every collection automatically has an index on `_id`. You add the rest.

### 7.1 Single-field index

```js
veh_mst_Schema.index({ cust_id: 1 }); // 1 = ascending, -1 = descending
```

Good for queries like `veh_msts.find({ cust_id: someId })`.

### 7.2 Compound index

```js
order_mst_Schema.index({ dealer_id: 1, on_dt: -1 });
```

This supports:

- `Order.find({ dealer_id })` ✅
- `Order.find({ dealer_id }).sort({ on_dt: -1 })` ✅ (no in-memory sort)
- `Order.find({ dealer_id, on_dt: { $gte: d } })` ✅
- `Order.find({ on_dt: { $gte: d } })` ❌ — _cannot_ use this index because it leads with `dealer_id`.

**Rule of thumb — ESR**: **E**quality fields first, then **S**ort fields, then **R**ange fields. A compound index on `{ dealer_id: 1, order_status: 1, on_dt: -1 }` is great for "latest pending orders for dealer X".

### 7.3 Unique index

Prevents duplicate keys:

```js
user_Schema.index({ mobile: 1 }, { unique: true });
```

Attempting to insert a second user with the same `mobile` will throw `E11000 duplicate key error`.

### 7.4 Sparse index

Only indexes documents that _have_ the field.

```js
cust_Schema.index({ gstin: 1 }, { unique: true, sparse: true });
```

Useful when `gstin` is optional: you still want uniqueness among the customers that provided one, while letting thousands of others skip it without colliding on `null`.

### 7.5 Partial index

Stronger than sparse — only indexes documents matching a filter.

```js
order_mst_Schema.index(
  { on_dt: -1 },
  {
    partialFilterExpression: {
      order_status: { $in: ["CREATED", "DISPATCHED"] },
    },
  },
);
```

A query for "active orders sorted by date" hits a tiny index instead of a huge one that contains every historic order.

### 7.6 TTL (Time-To-Live) index

Deletes documents automatically after N seconds:

```js
otp_Schema.index({ createdAt: 1 }, { expireAfterSeconds: 300 });
```

Used in our project for OTPs, invites, session tokens — anything that should self-expire. (Atlas checks once per minute, so don't rely on second-level precision.)

### 7.7 Text index

Enables `$text` search:

```js
prod_Schema.index({ prod_name: "text", description: "text" });

Product.find({ $text: { $search: "petrol diesel" } });
```

This gives basic language-aware tokenization, stemming, and stop-word removal — fine for simple search boxes. For richer search you move to Atlas Search (Lucene-based), which we'll treat separately.

### 7.8 Other index types (quick mentions)

- **Hashed index** — used for sharding and key-based distribution.
- **Geospatial (`2dsphere`)** — for `$near`, `$geoWithin`. Relevant if the mobile app starts tracking vehicle GPS positions.
- **Wildcard index** — when field names are unpredictable (e.g. user-provided attributes).

### 7.9 How to know an index is being used

```js
const explain = await Order.find({ dealer_id, on_dt: { $gte: d } })
  .sort({ on_dt: -1 })
  .explain("executionStats");

console.log(explain.queryPlanner.winningPlan.stage); // IXSCAN is good
console.log(explain.executionStats.totalDocsExamined); // closer to nReturned is better
```

`COLLSCAN` means no index was used — a red flag in production.

---

## 8. The Aggregation Pipeline

If MongoDB's query language is the "WHERE" clause, **aggregation** is the "GROUP BY / JOIN / window function" layer. It is the single most powerful feature in MongoDB and the thing you'll use for dashboards, reports, and complex queries.

### 8.1 Pipeline model

You pass an **array of stages**. Each stage takes documents in, transforms them, and emits documents out. Stages run in order, like `|` in Unix:

```js
Order.aggregate([
  { $match:   { ... } },   // filter
  { $lookup:  { ... } },   // join
  { $unwind:  "$products" },
  { $group:   { ... } },
  { $sort:    { total: -1 } },
  { $project: { ... } },
]);
```

### 8.2 The stages you'll use daily

#### `$match` — filter

Use exactly like a `find()` filter. Put `$match` as _early_ as possible so MongoDB can use indexes and reduce the working set.

```js
{ $match: { dealer_id: new ObjectId("..."), on_dt: { $gte: startOfMonth } } }
```

#### `$group` — aggregate / reduce

```js
{
  $group: {
    _id: "$dealer_id",                     // group key
    total_orders:  { $sum: 1 },            // count
    total_amount:  { $sum: "$net_amount" },
    avg_order:     { $avg: "$net_amount" },
    first_order:   { $min: "$on_dt" },
    last_order:    { $max: "$on_dt" },
  }
}
```

The output document has one row per unique `_id`. Aggregators include `$sum`, `$avg`, `$min`, `$max`, `$push` (collect into an array), `$addToSet`, `$first`, `$last`.

#### `$lookup` — the MongoDB "JOIN"

```js
{
  $lookup: {
    from:         "cust_msts",
    localField:   "cust_id",
    foreignField: "_id",
    as:           "customer",            // result is ALWAYS an array
  }
}
// Typically followed by:
{ $unwind: "$customer" }   // flatten the single-element array
```

Real-world uses in our project include joining `order_msts` → `cust_msts` → `dealer_msts` to produce a single invoice row.

#### `$project` — reshape the output

Think of it as `SELECT a, b, (c + d) AS total`:

```js
{
  $project: {
    _id:          0,
    order_no:     1,
    customer:     "$customer.cust_name",
    dealer:       "$dealer.dealer_name",
    total_amount: { $sum: "$products.amount" },
    month:        { $dateToString: { format: "%Y-%m", date: "$on_dt" } },
  }
}
```

You can also use `$addFields` to _add_ computed fields without removing existing ones.

#### `$unwind` — expand arrays

Given an order with a `products` array of 3 items, `$unwind: "$products"` produces **3 output documents**, each with one product. Use it when you want to aggregate at the line-item level:

```js
[
  { $match: { dealer_id: someDealer } },
  { $unwind: "$products" },
  {
    $group: {
      _id: "$products.prod_name",
      total_qty: { $sum: "$products.quantity" },
      total_amt: {
        $sum: { $multiply: ["$products.rate", "$products.quantity"] },
      },
    },
  },
  { $sort: { total_amt: -1 } },
];
```

#### `$sort`, `$limit`, `$skip`

Exactly what they sound like. Pagination pattern:

```js
{ $sort:  { on_dt: -1 } },
{ $skip:  (page - 1) * pageSize },
{ $limit: pageSize },
```

For large datasets, prefer **keyset pagination** (`$match: { _id: { $lt: lastSeenId } }`) instead of `$skip`, which scans and discards.

#### `$facet` — multiple pipelines in one pass

Run several sub-pipelines against the same input:

```js
{
  $facet: {
    byStatus: [ { $group: { _id: "$order_status", n: { $sum: 1 } } } ],
    byDealer: [ { $group: { _id: "$dealer_id",    n: { $sum: 1 } } } ],
    recent:   [ { $sort: { on_dt: -1 } }, { $limit: 10 } ],
  }
}
```

Perfect for a dashboard that needs "counts by status AND top 10 recent orders AND totals by dealer" in one round-trip.

### 8.3 A complete example — monthly sales per dealer

```js
Order.aggregate([
  // 1. Only this year, only completed
  {
    $match: {
      on_dt: { $gte: new Date("2026-01-01"), $lt: new Date("2027-01-01") },
      order_status: "DELIVERED",
    },
  },

  // 2. Expand each product line
  { $unwind: "$products" },

  // 3. Compute line-level amount
  {
    $addFields: {
      line_amount: { $multiply: ["$products.quantity", "$products.rate"] },
      month: { $dateToString: { format: "%Y-%m", date: "$on_dt" } },
    },
  },

  // 4. Group by dealer + month
  {
    $group: {
      _id: { dealer_id: "$dealer_id", month: "$month" },
      orders: { $addToSet: "$_id" },
      total: { $sum: "$line_amount" },
    },
  },

  // 5. Pull the dealer name in
  {
    $lookup: {
      from: "dealer_msts",
      localField: "_id.dealer_id",
      foreignField: "_id",
      as: "dealer",
    },
  },
  { $unwind: "$dealer" },

  // 6. Final shape
  {
    $project: {
      _id: 0,
      month: "$_id.month",
      dealer_id: "$_id.dealer_id",
      dealer_name: "$dealer.dealer_name",
      order_count: { $size: "$orders" },
      total_amount: 1,
    },
  },

  { $sort: { month: 1, total_amount: -1 } },
]);
```

Read it top-to-bottom like a Unix pipe. Each stage is a well-defined transformation, which makes aggregations easy to debug (comment out later stages and inspect the intermediate output).

---

## 9. Replica Sets & Sharding (Conceptual)

### 9.1 Replica sets — high availability

A **replica set** is a group of MongoDB server processes that keep identical copies of the data:

```
  ┌────── Primary ──────┐
  │        ▲            │
writes     │ oplog replication
  │        ▼            │
  ├── Secondary #1     ─┤
  └── Secondary #2     ─┘
```

- There is **one Primary** that accepts writes.
- **Secondaries** follow along via the **oplog** (operations log) and can serve reads if you choose.
- If the Primary dies, the Secondaries run an election and promote one of themselves, usually within seconds. Your driver (and Mongoose) handle the reconnect transparently.
- A minimum of **3 members** is recommended so elections can always reach a majority.

Benefits:

1. **Zero-downtime failover**.
2. **Data durability** — writes can be acknowledged only after being replicated (`writeConcern: "majority"`).
3. **Read scaling** — you can serve analytical reads from secondaries with `readPreference: "secondaryPreferred"`.

Atlas automatically runs our database as a 3-node replica set, so you get this for free.

### 9.2 Sharding — horizontal scale-out

When one machine can no longer hold or serve the whole dataset, you **shard**: split data across multiple replica sets.

```
                        ┌── Config Servers (metadata) ──┐
                        │                                │
 App ── mongos router ──┼── Shard A (replica set) ───────┤
                        ├── Shard B (replica set) ───────┤
                        └── Shard C (replica set) ───────┘
```

- Each **shard** is itself a replica set.
- The **`mongos` router** is a stateless process your driver talks to. It looks at queries, figures out which shards own the data, routes there, and merges results.
- You choose a **shard key** (e.g. `{ dealer_id: "hashed" }`). MongoDB distributes documents across shards by that key.

Choosing a shard key is the single most important sharding decision — a bad key creates hot shards. Most apps never need sharding; they scale vertically and with indexes first. DZZLO OMS is not sharded today, and at our data volumes probably never needs to be.

---

## 10. MongoDB Atlas — The Managed Service

**MongoDB Atlas** is MongoDB Inc.'s managed cloud service. Our project runs against Atlas on AWS (region configured in `.env`). Instead of installing `mongod` and worrying about backups, you pay a monthly bill and Atlas handles:

- Provisioning replica sets.
- OS patching and security updates.
- Automatic backups and point-in-time restore.
- Monitoring, alerting, slow-query logs.
- One-click major version upgrades.
- Network isolation (VPC peering, private endpoints).
- Role-based access control and TLS.

### 10.1 Tiers

| Tier      | Purpose                        | Replica set | Backups    |
| --------- | ------------------------------ | ----------- | ---------- |
| M0 (Free) | Learning, personal projects    | Shared      | No         |
| M2 / M5   | Small shared clusters          | Shared      | Basic      |
| M10+      | **Dedicated** production nodes | 3 nodes     | Continuous |
| M30 / M40 | Mid-size production            | 3 nodes     | Continuous |
| M50+      | Large production, sharding     | 3+ nodes    | Continuous |

DZZLO OMS runs on a dedicated tier so we get continuous (point-in-time) backups and private networking.

### 10.2 Cluster, server version, FCV

Inside Atlas a **cluster** bundles a MongoDB version, region, tier, and disk size. A cluster has both:

- **Binary version** — the `mongod` process version (e.g. 7.0.31).
- **featureCompatibilityVersion (FCV)** — an internal flag that controls whether new features of the current major are enabled. During a major upgrade, Atlas bumps the binary first and FCV second, so you can roll back if something goes wrong.

### 10.3 Backups

On dedicated tiers Atlas takes **continuous cloud backups** (snapshots + oplog). You can restore the entire cluster or a single collection to any moment within the retention window. Test this at least once before you need it in anger.

---

## 11. When to Use MongoDB vs SQL

There is no "MongoDB is always better" answer. A quick heuristic:

### Pick MongoDB when…

- **The shape of data varies** per record (flexible attributes, user-defined fields).
- **Documents map cleanly to your domain objects** — e.g. an order and its line items fit naturally inside one document.
- **You want horizontal scale** without sharding manually.
- **Your read pattern is mostly "fetch this entity and everything hanging off it"** — because embedding avoids JOINs.
- **You're writing a mobile backend** that often syncs JSON blobs directly.

### Pick a SQL database when…

- **Your data is highly relational** and you frequently need multi-way JOINs.
- **You need complex multi-row transactions** across many tables (though MongoDB now supports this since 4.0, SQL engines are older and more mature here).
- **You need strict schema enforcement at the storage layer** without an application layer.
- **Your team is more comfortable with SQL and analytics tools** (Tableau, PowerBI, Metabase all speak SQL natively).
- **Reporting is the primary workload** — warehouses like Postgres, BigQuery, or Snowflake excel here.

### DZZLO OMS specifically

Orders contain embedded `products[]`, vehicles embed metadata per trip, deliveries carry scanned slips. Mongo's "document per order" model is a natural fit, and Atlas handles operational concerns. SQL was not a wrong choice, but the document model saves us many joins every time we render an order.

---

## 12. Mongoose vs the Native Driver

Both are TypeScript/JavaScript libraries for talking to MongoDB from Node. In this project we use **Mongoose 9.4.1** on top of the native driver **7.1.1**.

### 12.1 The native driver

- Published as `mongodb` on npm.
- Thin, fast, close to the wire.
- Exposes `MongoClient`, `Db`, `Collection`, and raw `find`/`insertOne`/`aggregate` methods.
- You are responsible for types, validation, population, and any convenience helpers.

```js
const { MongoClient } = require("mongodb");
const client = new MongoClient(process.env.MONGO_URI);
await client.connect();
const db = client.db("dzzlo_oms");
const orders = db.collection("order_msts");

const row = await orders.findOne({ order_no: 1042 });
```

### 12.2 Mongoose

- Published as `mongoose` on npm.
- Wraps the native driver and adds schemas, validation, middleware, `populate`, virtuals, and more.
- Slightly slower than raw driver calls because of the casting layer, but the convenience is usually worth it for line-of-business apps.

```js
const mongoose = require("mongoose");
await mongoose.connect(process.env.MONGO_URI);
const row = await Order.findOne({ order_no: 1042 }).populate("cust_id");
```

### 12.3 When to drop to the driver

Even inside a Mongoose app, sometimes you bypass the ODM:

```js
// Access the raw collection — no Mongoose casting, full server operators.
await mongoose.connection.collection("order_msts").bulkWrite(ops);
```

- Very hot paths where 5–10% overhead matters.
- Features the ODM lags on (new aggregation operators, queryable encryption options).
- Admin commands (`createIndex` on the fly, `runCommand`).

### 12.4 Comparison table

| Concern              | Native driver             | Mongoose               |
| -------------------- | ------------------------- | ---------------------- |
| Schemas & validation | None                      | Declarative, rich      |
| Type casting         | None (you do it)          | Automatic              |
| `populate()`         | Not supported             | First-class            |
| Hooks (`pre`/`post`) | None                      | Yes                    |
| Virtuals             | None                      | Yes                    |
| Performance overhead | Minimal                   | Small but measurable   |
| Learning curve       | Small                     | Larger (more concepts) |
| Used in this project | Indirectly (via Mongoose) | **Yes — primary API**  |

---

## 13. Putting It Together — DZZLO OMS Entities

Now let's walk through our real models and connect everything above.

### 13.1 `veh_msts` — vehicles

```js
// dzzlo_oms_api/models/veh_msts.js
{
  cust_id:    { type: ObjectId, ref: "cust_msts" },
  veh_reg_no: { type: String, validate: { ... } },
  route:      { type: String },
  // plus timestamps
}
veh_mst_Schema.index({ cust_id: 1 });
veh_mst_Schema.index({ veh_reg_no: 1 });
```

- `cust_id` is an `ObjectId` reference — it is **not** a database-enforced foreign key; we use `populate("cust_id")` at query time.
- The regex validator runs in _Mongoose_, not in the database.
- Two indexes support the most common lookups ("vehicles for this customer" and "find by registration number").

### 13.2 `order_msts` — orders

The order model demonstrates **embedding** at its best:

```js
const order_trn_Schema = new mongoose.Schema(
  {
    prod_id: { type: ObjectId, ref: "prod_msts" },
    prod_name: { type: String },
    unit: { type: String },
    quantity: { type: Number },
    rate: { type: Number, set: (v) => (Math.round(v * 100) / 100).toFixed(2) },
    p_ctgy: { type: String },
    input_type: { type: String },
    is_full_tank: { type: Boolean },
  },
  { _id: false },
);

const order_mst_Schema = new mongoose.Schema(
  {
    dealer_id: { type: ObjectId, ref: "dealer_msts" },
    cust_id: { type: ObjectId, ref: "cust_msts", required: true },
    order_no: { type: Number, maxlength: 6 },
    so_id: { type: ObjectId, ref: "so_msts" },
    cust_user_id: { type: ObjectId, ref: "users" },
    veh_id: { type: ObjectId, ref: "veh_msts" },
    products: [order_trn_Schema],
    // ...
  },
  { timestamps: true },
);
```

Key observations:

1. **`products` is an embedded array**, not a separate collection. One query pulls an order and its line items in a single round-trip. In SQL you'd need an `orders` table joined to `order_lines`.
2. **`dealer_id`, `cust_id`, `veh_id`** are references (`ObjectId + ref`), because these entities are shared across many orders and must be editable in one place.
3. **`order_no`** is a sequential number generated via the `counters` collection with `$inc`. This is MongoDB's canonical way to implement auto-increment without a database sequence.
4. The `set` on `rate` is a Mongoose feature — it runs _before_ saving, rounding to two decimals.
5. `{ timestamps: true }` gives `createdAt` / `updatedAt` automatically.

### 13.3 A realistic report query

"Total petrol dispatched in April 2026 per dealer":

```js
Order.aggregate([
  {
    $match: {
      on_dt: { $gte: new Date("2026-04-01"), $lt: new Date("2026-05-01") },
      order_status: "DELIVERED",
    },
  },
  { $unwind: "$products" },
  { $match: { "products.prod_name": "PETROL" } },
  {
    $group: {
      _id: "$dealer_id",
      total_qty: { $sum: "$products.quantity" },
      total_amount: {
        $sum: { $multiply: ["$products.quantity", "$products.rate"] },
      },
      order_count: { $addToSet: "$_id" },
    },
  },
  {
    $lookup: {
      from: "dealer_msts",
      localField: "_id",
      foreignField: "_id",
      as: "dealer",
    },
  },
  { $unwind: "$dealer" },
  {
    $project: {
      _id: 0,
      dealer_name: "$dealer.dealer_name",
      total_qty: 1,
      total_amount: 1,
      order_count: { $size: "$order_count" },
    },
  },
  { $sort: { total_amount: -1 } },
]);
```

To make this fast you would add a compound index matching the `$match` pattern:

```js
order_mst_Schema.index({ on_dt: 1, order_status: 1 });
```

Or even a **partial index** keyed on `on_dt` where `order_status = "DELIVERED"` — smaller and faster still.

### 13.4 Indexing recap for this project

| Collection    | Useful index                                             | Why                           |
| ------------- | -------------------------------------------------------- | ----------------------------- |
| `veh_msts`    | `{ cust_id: 1 }`                                         | "All vehicles for a customer" |
| `veh_msts`    | `{ veh_reg_no: 1 }` (unique?)                            | Lookup by number plate        |
| `order_msts`  | `{ dealer_id: 1, on_dt: -1 }`                            | Dealer dashboard              |
| `order_msts`  | `{ cust_id: 1, on_dt: -1 }`                              | Customer order history        |
| `order_msts`  | `{ order_no: 1 }` (unique)                               | Direct lookup by human number |
| `order_msts`  | `{ on_dt: -1, order_status: 1 }` partial `status in […]` | Active orders feed            |
| `dealer_msts` | `{ dealer_code: 1 }` (unique)                            | Dealer onboarding / lookup    |
| `cust_msts`   | `{ mobile: 1 }` (unique)                                 | Login / OTP flow              |
| `prod_msts`   | `{ prod_name: 1 }`                                       | Product pickers               |

This is not what the collection actually has today — it's the ideal model to aim for. Index decisions should be backed by `explain("executionStats")` against real query patterns.

### 13.5 Final mental model

When you touch the database from `dzzlo_oms_api`, remember:

1. **You are sending JS objects** — Mongoose casts them to BSON.
2. **The server stores documents inside collections** — each collection you see in `models/` maps to one collection.
3. **Indexes are your only real performance lever** at the data layer — design them for real queries, not hypothetical ones.
4. **Aggregation pipelines are the hammer for any "group by / join / report" question** — write them stage by stage and use `explain` to verify.
5. **Atlas is your runtime** — backups, failover, and upgrades happen there; trust it, but test restores.
6. **Mongoose gives you schemas back** — embrace them, but know how to drop to the native driver when you need every last feature or millisecond.

Once those six sentences feel obvious to you, you understand MongoDB well enough to build and maintain the DZZLO OMS backend with confidence.

---

_File: `docs/tasks/tasks_03/01_mongodb_overview.md`_
