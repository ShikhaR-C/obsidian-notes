# MongoDB Search Guide — The Three Ways to Search

> A deep dive for developers new to searching in MongoDB, written for the DZZLO OMS project.
> We need to search **vehicles** (`veh_msts`), **orders** (`order_msts`), and **dealers** (`dealer_msts`) by free text, by field, and by date range.

---

## Table of contents

1. [Why searching in MongoDB is different](#why-searching-in-mongodb-is-different)
2. [Method 1 — `$regex` (basic substring search)](#method-1--regex-basic-substring-search)
3. [Method 2 — Text Indexes + `$text` (built-in full-text)](#method-2--text-indexes--text-built-in-full-text)
4. [Method 3 — Atlas Search (Lucene-powered, modern choice)](#method-3--atlas-search-lucene-powered-modern-choice)
5. [Decision matrix — which one do I use?](#decision-matrix--which-one-do-i-use)
6. [Filter patterns you need every day](#filter-patterns-you-need-every-day)
7. [Pagination strategies](#pagination-strategies)
8. [DZZLO OMS worked examples](#dzzlo-oms-worked-examples)
9. [Checklist before you ship](#checklist-before-you-ship)

---

## Why searching in MongoDB is different

Coming from SQL you may think "I just do `LIKE '%smith%'` and I'm done." MongoDB can do something similar with `$regex`, but there are **three fundamentally different** ways to search documents, and they solve different problems:

| Method       | What it is                                      | Needs an index?            | Typo tolerance | Ranking     |
| ------------ | ----------------------------------------------- | -------------------------- | -------------- | ----------- |
| `$regex`     | Pattern matching on a field                     | Works without, faster with | No             | No          |
| `$text`      | Built-in full-text indexing (per collection)    | Yes (text index)           | No             | Basic       |
| Atlas Search | Lucene-powered search service, managed by Atlas | Yes (search index)         | Yes (fuzzy)    | Rich (BM25) |

You will use **all three** in real projects. The trick is knowing which one to pick.

---

## Method 1 — `$regex` (basic substring search)

### How it works

`$regex` runs a regular expression against string fields.

```js
// Find any vehicle whose registration number contains "KA01"
db.veh_msts.find({
  veh_reg_no: { $regex: "KA01", $options: "i" }, // 'i' = case insensitive
});
```

In Mongoose:

```js
const Vehicle = mongoose.model("veh_msts", vehSchema);

const results = await Vehicle.find({
  veh_reg_no: { $regex: req.query.q, $options: "i" },
}).limit(20);
```

### Important: anchored vs unanchored regex

MongoDB can use a **regular B-tree index** on a field — but **only if the regex is anchored to the start** with `^`, and is **case sensitive**.

```js
// GOOD: uses the index on veh_reg_no, very fast
{ veh_reg_no: { $regex: /^KA01/ } }

// BAD: full collection scan, slow on big collections
{ veh_reg_no: { $regex: /KA01/, $options: "i" } }
```

- `^smith` + no `$options: "i"` → **index used** (prefix scan)
- `smith` → **no index used** (scans every doc)
- `^smith` + `$options: "i"` → **no index used** (case insensitivity breaks it)

Rule of thumb: if you want a case-insensitive substring match, use a **case-insensitive collation** on the index, or move to `$text` or Atlas Search.

### Case-insensitive prefix — the collation trap

You might expect a case-insensitive collation index to solve this:

```js
// ⚠️ DOES NOT WORK for $regex
db.dealer_msts.createIndex(
  { dealer_name: 1 },
  { collation: { locale: "en", strength: 2 } },
);

db.dealer_msts
  .find({ dealer_name: { $regex: "^smith" } })
  .collation({ locale: "en", strength: 2 });
```

It doesn't. Per the MongoDB docs, the `$regex` implementation is **not
collation-aware**: a case-insensitive collation index cannot back a regex
query, and the collation doesn't change what the regex matches either
(`^smith` still won't match `Smith` without `$options: "i"`). Collation
indexes help *equality* and *sort*, not `$regex`.

What actually works for an indexed, case-insensitive prefix search:

```js
// Store a normalized shadow field and search that instead
// { dealer_name: "Smith Fuels", dealer_name_lc: "smith fuels" }
db.dealer_msts.createIndex({ dealer_name_lc: 1 });

const q = escapeRegex(req.query.q).toLowerCase();
db.dealer_msts.find({ dealer_name_lc: { $regex: `^${q}` } }); // anchored + case-sensitive → index used
```

…or move to `$text` / Atlas Search (autocomplete), which are
case-insensitive by design.

### Escaping user input

**Never** pass raw user input into a regex without escaping it — otherwise a user can send `.*` and blow up your query, or worse, inject a catastrophic backtracking pattern (ReDoS).

```js
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

const q = escapeRegex(req.query.q);
const dealers = await Dealer.find({
  dealer_name: { $regex: `^${q}`, $options: "i" },
});
```

### Pros and cons

**Pros**

- Zero setup. Works on any field today.
- Simple mental model.
- Prefix searches can use an index.

**Cons**

- No relevance ranking.
- Case-insensitive substring search is **always a collection scan**.
- No tokenization — searching for `"red truck"` won't find `"Red Trucks"` the way you'd expect.
- No typo tolerance.
- No stemming (searching `"run"` won't find `"running"`).

### When to use it

- Simple admin-panel filters where the dataset is small (< 100k docs).
- Prefix searches (`^abc`) on indexed fields.
- Prototypes where you need search "right now" and can swap it out later.

---

## Method 2 — Text Indexes + `$text` (built-in full-text)

### What's a text index?

A **text index** is a special MongoDB index that tokenises the content of string fields, removes stopwords, stems the tokens, and stores them in an inverted index. It's the same idea as Lucene but much simpler.

### Creating a text index

```js
// Single-field text index on dealer name
db.dealer_msts.createIndex({ dealer_name: "text" });

// Compound text index across many fields
db.order_msts.createIndex({
  order_no: "text",
  remarks: "text",
  "customer.name": "text",
});
```

Notice the special `"text"` string instead of `1` or `-1`. It tells MongoDB "tokenise this field."

### Weights — making some fields count more

You can tell MongoDB "matches in the title are worth 10x matches in the description":

```js
db.products.createIndex(
  { name: "text", description: "text", tags: "text" },
  {
    name: "ProductTextIndex",
    weights: { name: 10, tags: 5, description: 1 },
    default_language: "english",
  },
);
```

### Querying with `$text`

```js
// Simple full-text search
db.products.find({ $text: { $search: "coffee" } });

// Multi-word — OR by default
db.products.find({ $text: { $search: "coffee mug" } });

// Require exact phrase with quotes inside the string
db.products.find({ $text: { $search: '"french press"' } });

// Exclude a word with -
db.products.find({ $text: { $search: "coffee -decaf" } });

// Switch language (affects stemming + stopwords)
db.products.find({
  $text: { $search: "cafe", $language: "french" },
});
```

### Ranking results with `$meta: "textScore"`

By itself, `$text` returns matching docs but not in any particular order. To rank them by relevance:

```js
db.products
  .find(
    { $text: { $search: "espresso machine" } },
    { score: { $meta: "textScore" } },
  )
  .sort({ score: { $meta: "textScore" } })
  .limit(10);
```

The `score` field is added to each result. The higher it is, the better the match.

### Combining `$text` with regular filters

```js
db.order_msts.find({
  $text: { $search: "urgent delivery" },
  status: "pending",
  order_date: { $gte: new Date("2026-01-01") },
});
```

MongoDB will use the text index for the `$text` part and then apply the other filters after.

### Limitations — read these carefully

These are the reasons teams outgrow `$text`:

1. **You can only have ONE text index per collection.** You can put multiple fields in it, but you can't have two separate text indexes. If you try, MongoDB will refuse.
2. **No partial-word matching.** Searching for `"cof"` will **not** find `"coffee"`. The whole token has to match (after stemming).
3. **No typo tolerance.** `"mongodb"` will not match `"monogdb"`.
4. **Stemming is dumb.** It's rule-based, not smart like Atlas Search or Elastic.
5. **Relevance ranking is basic.** It's not BM25, it's a simpler weighting scheme.
6. **No facets, no highlighting, no autocomplete.**

### Mongoose example on `dealer_msts`

```js
// models/DealerMst.js
const dealerSchema = new mongoose.Schema({
  dealer_code: { type: String, unique: true },
  dealer_name: String,
  dealer_gst: String,
  dealer_address: String,
  dealer_city: String,
  remarks: String,
});

// Compound text index across searchable fields
dealerSchema.index(
  {
    dealer_name: "text",
    dealer_code: "text",
    dealer_gst: "text",
    dealer_city: "text",
    remarks: "text",
  },
  {
    weights: { dealer_name: 10, dealer_code: 8, dealer_city: 3, remarks: 1 },
    name: "DealerSearchIndex",
  },
);

module.exports = mongoose.model("dealer_msts", dealerSchema);
```

Usage:

```js
const Dealer = require("./models/DealerMst");

exports.searchDealers = async (req, res) => {
  const q = req.query.q;
  const results = await Dealer.find(
    { $text: { $search: q } },
    { score: { $meta: "textScore" } },
  )
    .sort({ score: { $meta: "textScore" } })
    .limit(25)
    .lean();
  res.json(results);
};
```

### When to use `$text`

- Single-collection full-text search on a fixed set of fields.
- You're not on Atlas and can't use Atlas Search.
- You're OK with no typo tolerance or autocomplete.
- You only need basic ranking.

For DZZLO OMS, since you're on Atlas, prefer Atlas Search for production. Keep `$text` in your toolbox for quick wins and small side collections.

---

## Method 3 — Atlas Search (Lucene-powered, modern choice)

### What it actually is

Atlas Search is **Apache Lucene** running as a managed service next to your Atlas cluster. Lucene is the same engine that powers Elasticsearch and Solr, so you get enterprise-grade full-text search without running a second database.

Some key things to understand:

- Atlas Search indexes are **separate** from your regular MongoDB indexes.
- They're stored outside the document data and kept in sync automatically.
- You query them via a new aggregation stage called `$search`.
- Only available on **Atlas clusters** (works on M0 free tier, with limits).

Since DZZLO OMS runs on Atlas 7.0, **all of this is available today**.

### The `$search` aggregation stage

`$search` must be the **first stage** of an aggregation pipeline. You then chain more stages (`$match`, `$lookup`, `$project`, etc.) after it.

```js
db.dealer_msts.aggregate([
  {
    $search: {
      index: "dealer_default", // name of the search index
      text: {
        query: "sharma",
        path: "dealer_name",
        fuzzy: { maxEdits: 1 },
      },
    },
  },
  { $limit: 20 },
  { $project: { dealer_code: 1, dealer_name: 1, dealer_city: 1 } },
]);
```

### Search index JSON definitions

You create an Atlas Search index through the Atlas UI, CLI, or API, and pass it a JSON definition. The heart of that JSON is the **mappings**.

#### Dynamic mapping — index everything automatically

```json
{
  "mappings": {
    "dynamic": true
  }
}
```

Atlas will figure out field types itself and index every field in every document. Easy to start with, but:

- Uses more storage.
- You can't fine-tune analyzers per field.
- Schema drift will silently index junk.

#### Static mapping — explicit fields

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "dealer_name": {
        "type": "string",
        "analyzer": "lucene.standard"
      },
      "dealer_code": {
        "type": "string",
        "analyzer": "lucene.keyword"
      },
      "dealer_city": { "type": "string" },
      "created_at": { "type": "date" }
    }
  }
}
```

You tell Atlas exactly which fields to index and how. This is the recommended approach for production.

#### Hybrid — dynamic plus overrides

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "dealer_name": [
        { "type": "string" },
        { "type": "autocomplete", "tokenization": "edgeGram" }
      ]
    }
  }
}
```

Note: a single field can have **multiple index types** — here `dealer_name` is indexed both as text and as autocomplete, so you can do both kinds of query on the same field.

### The operators you'll actually use

| Operator       | What it does                                                     |
| -------------- | ---------------------------------------------------------------- |
| `text`         | Full-text search with analyzers, stemming, fuzzy matching        |
| `autocomplete` | Query-as-you-type using edge n-grams                             |
| `phrase`       | Exact phrase or ordered sequence                                 |
| `wildcard`     | `*` and `?` patterns                                             |
| `regex`        | Regular expressions (careful, can be slow)                       |
| `range`        | Numeric and date ranges                                          |
| `near`         | Geospatial or "closest to a value" queries                       |
| `equals`       | Exact match on boolean, ObjectId, number, date                   |
| `compound`     | Combine multiple operators with must / should / mustNot / filter |
| `exists`       | Field presence                                                   |
| `moreLikeThis` | Find similar documents                                           |

### Example — simple text search

```js
db.veh_msts.aggregate([
  {
    $search: {
      index: "vehicle_default",
      text: {
        query: "tata ace",
        path: ["veh_make", "veh_model"],
      },
    },
  },
  { $limit: 20 },
]);
```

Searches both `veh_make` and `veh_model` in one call.

### Example — compound with must, should, mustNot, filter

This is the pattern you'll use most in real apps.

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      compound: {
        must: [
          // must match — affects score
          { text: { query: "urgent", path: "remarks" } },
        ],
        should: [
          // optional — boost score
          { text: { query: "priority", path: "remarks" } },
        ],
        mustNot: [
          // exclude
          { equals: { value: "cancelled", path: "status" } },
        ],
        filter: [
          // narrow down without affecting score
          {
            range: {
              path: "order_date",
              gte: ISODate("2026-01-01"),
              lte: ISODate("2026-04-30"),
            },
          },
        ],
      },
    },
  },
  { $limit: 25 },
]);
```

Key mental model:

- **must** = AND, counts toward score
- **should** = OR-ish, counts toward score
- **mustNot** = NOT, no score effect
- **filter** = AND, no score effect (fast)

### Example — autocomplete on vehicle registration

```js
db.veh_msts.aggregate([
  {
    $search: {
      index: "vehicle_autocomplete",
      autocomplete: {
        query: "KA01A",
        path: "veh_reg_no",
        tokenOrder: "sequential",
        fuzzy: { maxEdits: 1, prefixLength: 3 },
      },
    },
  },
  { $limit: 10 },
  { $project: { veh_reg_no: 1, veh_make: 1, veh_model: 1 } },
]);
```

Behind the scenes this requires an `autocomplete` field type on `veh_reg_no` in the index definition.

### Scoring with `searchMeta` and `$meta: "searchScore"`

```js
db.dealer_msts.aggregate([
  {
    $search: {
      index: "dealer_default",
      text: { query: "sharma", path: "dealer_name" },
    },
  },
  {
    $project: {
      dealer_name: 1,
      dealer_city: 1,
      score: { $meta: "searchScore" },
    },
  },
  { $sort: { score: -1 } },
  { $limit: 20 },
]);
```

### Highlighting — show users why something matched

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      text: { query: "delayed", path: "remarks" },
      highlight: { path: "remarks" },
    },
  },
  {
    $project: {
      order_no: 1,
      remarks: 1,
      highlights: { $meta: "searchHighlights" },
    },
  },
]);
```

`searchHighlights` returns an array of the matched snippets with positions — perfect for bolding matches in the UI.

### Facets — filter counts for the UI

```js
db.order_msts.aggregate([
  {
    $searchMeta: {
      index: "order_default",
      facet: {
        // text.query must be NON-EMPTY — an empty string is invalid. For
        // "facets over everything" use a range/exists operator instead
        // (see orderFacets in 06_atlas_search_deep_dive.md).
        operator: { text: { query: "urgent", path: "remarks" } },
        facets: {
          statusFacet: {
            type: "string",
            path: "status",
          },
          monthFacet: {
            type: "date",
            path: "order_date",
            boundaries: [
              ISODate("2026-01-01"),
              ISODate("2026-02-01"),
              ISODate("2026-03-01"),
              ISODate("2026-04-01"),
            ],
          },
        },
      },
    },
  },
]);
```

This gives you the counts per facet bucket — the same data Amazon uses to show "Shoes (342), Shirts (128)" next to filter checkboxes.

### Analyzers — how text is chopped up

| Analyzer                                    | What it does                                                |
| ------------------------------------------- | ----------------------------------------------------------- |
| `lucene.standard`                           | Default. Lowercases, tokenises on whitespace + punctuation  |
| `lucene.simple`                             | Lowercases and tokenises on non-letters                     |
| `lucene.keyword`                            | Does **not** tokenise — treats the whole value as one token |
| `lucene.whitespace`                         | Splits only on whitespace, keeps case                       |
| `lucene.english`                            | Standard + English stemming + stopwords                     |
| `lucene.french` / `german` / `arabic` / ... | Language-specific stemming                                  |
| Custom                                      | Chain tokenisers + filters yourself                         |

Rule of thumb:

- Product names, dealer names, descriptions → `lucene.standard` or `lucene.english`
- Codes like `veh_reg_no`, `order_no`, status strings → `lucene.keyword`
- Free-text notes in English → `lucene.english`

### Atlas Search vs Elasticsearch — the honest comparison

| Dimension          | Atlas Search                    | Elasticsearch                                  |
| ------------------ | ------------------------------- | ---------------------------------------------- |
| Runs where         | Inside Atlas, next to your DB   | Separate cluster you manage (or Elastic Cloud) |
| Data sync          | Automatic, real-time            | You build it (Logstash, Kafka, app code)       |
| Query language     | MongoDB aggregation (`$search`) | Elastic DSL (JSON)                             |
| Relevance engine   | Lucene (BM25)                   | Lucene (BM25)                                  |
| Cost               | Included with paid Atlas tiers  | Separate infra + licensing                     |
| Features           | Most of what you need, not all  | More advanced (ML, anomaly detection, etc.)    |
| Operational burden | Near zero                       | High if self-hosted                            |

For DZZLO OMS: **use Atlas Search**. You already pay for Atlas, the data sync is free, and the feature set covers everything your app needs.

---

## Decision matrix — which one do I use?

| Use case                                                       | Best method                 | Why                                                |
| -------------------------------------------------------------- | --------------------------- | -------------------------------------------------- |
| "Starts with" search on an indexed field (`veh_reg_no` prefix) | `$regex` `^`                | Uses existing B-tree index, zero setup             |
| Case-insensitive substring on a small collection               | `$regex` + `$options: "i"`  | Collection scan — fine only while data stays small (collation does NOT help `$regex`) |
| Search on one collection, one set of fields, basic ranking     | `$text`                     | Built in, no extra infra, one-line index creation  |
| Production search UI with autocomplete, typos, ranking, facets | Atlas Search                | Only option that gives you all of these            |
| Full-text search across many fields with different weights     | Atlas Search                | `$text` also does weights, but Atlas scales better |
| Search dealers by name with tolerance for typos                | Atlas Search                | `fuzzy: { maxEdits: 2 }`                           |
| Faceted sidebar with counts (status, city, date bucket)        | Atlas Search                | `$searchMeta` + `facet`                            |
| Exact field match (status == "pending")                        | `$match` / `find`           | No text engine needed                              |
| Date range filter on a list                                    | `$match` with `$gte`/`$lte` | Or Atlas Search `range` inside filter              |

---

## Filter patterns you need every day

These are the bread and butter of list endpoints in DZZLO OMS. They don't need a search engine at all — they're regular Mongo query operators.

### Exact match

```js
db.order_msts.find({ status: "pending" });
```

### $in — any of these values

```js
db.order_msts.find({
  status: { $in: ["pending", "processing", "packed"] },
});
```

### $nin — none of these

```js
db.order_msts.find({
  status: { $nin: ["cancelled", "returned"] },
});
```

### Numeric range ($gte, $lte, $gt, $lt)

```js
// Orders worth 10k to 50k
db.order_msts.find({
  order_total: { $gte: 10000, $lte: 50000 },
});
```

### Date range — the important one

Always pass real `Date` objects, never strings.

```js
const start = new Date("2026-01-01T00:00:00.000Z");
const end = new Date("2026-02-01T00:00:00.000Z"); // exclusive

db.order_msts.find({
  order_date: { $gte: start, $lt: end },
});
```

With Mongoose:

```js
const { from, to } = req.query;
const filter = {};
if (from || to) {
  filter.order_date = {};
  if (from) filter.order_date.$gte = new Date(from);
  if (to) filter.order_date.$lte = new Date(to);
}
const orders = await Order.find(filter).sort({ order_date: -1 }).limit(50);
```

**Timezone gotcha:** MongoDB stores dates in UTC. If your user picks "1 Jan" in IST, convert that to UTC before querying, or you'll miss 5h30m of data.

### Combining filters with $and / $or

Multiple fields at the top level are implicit AND:

```js
db.order_msts.find({
  status: "pending",
  dealer_id: dealerId,
  order_date: { $gte: start, $lt: end },
});
```

Explicit `$or`:

```js
db.dealer_msts.find({
  $or: [{ dealer_city: "Bangalore" }, { dealer_city: "Mumbai" }],
});
```

Mixing AND + OR:

```js
db.order_msts.find({
  $and: [
    { status: "pending" },
    {
      $or: [{ priority: "high" }, { order_total: { $gte: 100000 } }],
    },
  ],
});
```

### $exists — field presence

```js
db.veh_msts.find({ insurance_expiry: { $exists: true } });
db.veh_msts.find({ driver_id: { $exists: false } });
```

### $ne — not equal

```js
db.order_msts.find({ status: { $ne: "cancelled" } });
```

### Array filters — $all, $elemMatch, $size

```js
// Orders that contain both SKU "A1" and "B2"
db.order_msts.find({ "items.sku": { $all: ["A1", "B2"] } });

// Orders with at least one line item over 10k
db.order_msts.find({
  items: { $elemMatch: { price: { $gte: 10000 } } },
});

// Orders with exactly 5 items
db.order_msts.find({ items: { $size: 5 } });
```

### Combining a search with filters — aggregation pipeline

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      compound: {
        must: [{ text: { query: "urgent", path: "remarks" } }],
        filter: [
          { equals: { path: "status", value: "pending" } },
          {
            range: {
              path: "order_date",
              gte: ISODate("2026-01-01"),
              lte: ISODate("2026-04-30"),
            },
          },
        ],
      },
    },
  },
  { $sort: { order_date: -1 } },
  { $skip: 0 },
  { $limit: 25 },
]);
```

---

## Pagination strategies

### Offset pagination — `$skip` + `$limit`

The obvious one:

```js
const page = 3;
const pageSize = 25;

db.order_msts
  .find(filter)
  .sort({ order_date: -1 })
  .skip((page - 1) * pageSize)
  .limit(pageSize);
```

**Downside:** `$skip` makes Mongo walk through every skipped document. On page 1000 that's 25,000 docs tossed out. Fine for admin UIs, painful at scale.

### Range (keyset) pagination

Instead of skipping, remember the last value and ask "give me the next 25 after this."

```js
// First page
const firstPage = await Order.find({ status: "pending" })
  .sort({ order_date: -1, _id: -1 })
  .limit(25);

// Next page — pass the cursor of the last item
const lastItem = firstPage[firstPage.length - 1];
const nextPage = await Order.find({
  status: "pending",
  $or: [
    { order_date: { $lt: lastItem.order_date } },
    {
      order_date: lastItem.order_date,
      _id: { $lt: lastItem._id },
    },
  ],
})
  .sort({ order_date: -1, _id: -1 })
  .limit(25);
```

This uses the index on `order_date + _id` and is constant time regardless of page depth. Use it for mobile-style infinite scroll.

### Pagination inside `$search`

Use `$skip` + `$limit` after the search stage, or use the `searchAfter` cursor token that Atlas Search returns:

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      text: { query: "urgent", path: "remarks" },
      searchAfter: previousPageToken, // cursor from the last result
    },
  },
  { $limit: 25 },
]);
```

---

## DZZLO OMS worked examples

> Field names below (`created_at`, `status`, `order_date`) are illustrative.
> The real DZZLO schema uses `createdAt` (Mongoose timestamps), `order_status`,
> and `on_dt` — see `07_search_implementation_api.md` for pipelines against
> the actual field names.

### Vehicles list with search + filters

Requirements:

- Search by `veh_reg_no` (prefix, fast)
- Filter by `veh_status`
- Filter by `created_at` date range
- Sort by `created_at` desc, paginate

```js
exports.listVehicles = async (req, res) => {
  const { q, status, from, to, page = 1, limit = 25 } = req.query;

  const filter = {};

  if (q) {
    const safe = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    // reg numbers are stored uppercase — uppercase the query and keep the
    // regex case-SENSITIVE so the B-tree index on veh_reg_no is used
    // (adding $options: "i" would force a collection scan)
    filter.veh_reg_no = { $regex: `^${safe.toUpperCase()}` };
  }
  if (status) filter.veh_status = status;
  if (from || to) {
    filter.created_at = {};
    if (from) filter.created_at.$gte = new Date(from);
    if (to) filter.created_at.$lte = new Date(to);
  }

  const skip = (Number(page) - 1) * Number(limit);
  const [items, total] = await Promise.all([
    Vehicle.find(filter)
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(Number(limit))
      .lean(),
    Vehicle.countDocuments(filter),
  ]);

  res.json({ items, total, page: Number(page), limit: Number(limit) });
};
```

Make sure you have:

```js
db.veh_msts.createIndex({ veh_reg_no: 1 });
db.veh_msts.createIndex({ veh_status: 1, created_at: -1 });
db.veh_msts.createIndex({ created_at: -1 });
```

### Orders list with full-text on remarks + filters + date range

Using Atlas Search for the text part:

```js
exports.listOrders = async (req, res) => {
  const { q, status, from, to, page = 1, limit = 25 } = req.query;

  const pipeline = [];

  if (q) {
    pipeline.push({
      $search: {
        index: "order_default",
        compound: {
          must: [
            {
              text: {
                query: q,
                path: ["remarks", "order_no", "customer_name"],
                fuzzy: { maxEdits: 1 },
              },
            },
          ],
          filter: [
            ...(status ? [{ equals: { path: "status", value: status } }] : []),
            ...(from || to
              ? [
                  {
                    range: {
                      path: "order_date",
                      ...(from ? { gte: new Date(from) } : {}),
                      ...(to ? { lte: new Date(to) } : {}),
                    },
                  },
                ]
              : []),
          ],
        },
      },
    });
  } else {
    const match = {};
    if (status) match.status = status;
    if (from || to) {
      match.order_date = {};
      if (from) match.order_date.$gte = new Date(from);
      if (to) match.order_date.$lte = new Date(to);
    }
    if (Object.keys(match).length) pipeline.push({ $match: match });
  }

  pipeline.push({ $sort: { order_date: -1 } });
  pipeline.push({ $skip: (Number(page) - 1) * Number(limit) });
  pipeline.push({ $limit: Number(limit) });

  const items = await Order.aggregate(pipeline);
  res.json({ items });
};
```

### Dealers autocomplete

```js
exports.dealerAutocomplete = async (req, res) => {
  const q = (req.query.q || "").trim();
  if (!q) return res.json([]);

  const items = await Dealer.aggregate([
    {
      $search: {
        index: "dealer_autocomplete",
        autocomplete: {
          query: q,
          path: "dealer_name",
          fuzzy: { maxEdits: 1 },
        },
      },
    },
    { $limit: 10 },
    {
      $project: {
        dealer_code: 1,
        dealer_name: 1,
        dealer_city: 1,
      },
    },
  ]);
  res.json(items);
};
```

---

## Checklist before you ship

- [ ] Every list endpoint has a **sensible default sort** (usually `created_at: -1`).
- [ ] Every `find(filter)` has an **index that matches the filter + sort shape**.
- [ ] Regex queries are either **anchored with `^`** or running against a small collection.
- [ ] User input going into `$regex` is **escaped**.
- [ ] Date filters use `new Date(...)`, **not strings**, and time zones are handled.
- [ ] `$text` indexes have **weights** set so the right fields win.
- [ ] Atlas Search indexes use **static mappings** for anything production-critical.
- [ ] Compound queries separate **must/should** (affects score) from **filter** (fast).
- [ ] Pagination on deep pages uses **range pagination**, not `$skip`.
- [ ] You've run `explain("executionStats")` on your slow queries at least once.

That's the whole mental model. Move on to `06_atlas_search_deep_dive.md` for the full Atlas Search playbook.
