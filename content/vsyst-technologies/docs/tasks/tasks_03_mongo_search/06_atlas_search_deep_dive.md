# Atlas Search Deep Dive

> The focused playbook for adding production-grade search to DZZLO OMS using Atlas Search.
> This file assumes you've read `05_mongodb_search_guide.md` and decided Atlas Search is the right tool.

---

## Table of contents

1. [Why Atlas Search fits DZZLO OMS](#why-atlas-search-fits-dzzlo-oms)
2. [Creating a search index](#creating-a-search-index)
3. [Anatomy of an index JSON definition](#anatomy-of-an-index-json-definition)
4. [Static vs dynamic mappings](#static-vs-dynamic-mappings)
5. [Field types cheat sheet](#field-types-cheat-sheet)
6. [The `$search` aggregation stage](#the-search-aggregation-stage)
7. [Operators by example](#operators-by-example)
8. [Highlighting](#highlighting)
9. [Faceted search for filter UIs](#faceted-search-for-filter-uis)
10. [Combining `$search` with `$match`, `$lookup`, `$project`](#combining-search-with-match-lookup-project)
11. [DZZLO OMS real-world examples](#dzzlo-oms-real-world-examples)
12. [Pricing and tier limits](#pricing-and-tier-limits)
13. [Performance and warming](#performance-and-warming)
14. [Troubleshooting](#troubleshooting)

---

## Why Atlas Search fits DZZLO OMS

Atlas Search is **Apache Lucene** packaged as a managed service inside MongoDB Atlas. It brings the search engine next to your data, so:

- **No second database.** You don't spin up an Elasticsearch cluster or write sync code.
- **Real-time sync.** Writes to MongoDB are reflected in the search index within seconds (change stream replication under the hood).
- **One query language.** You use the same aggregation pipeline you already use, with a new `$search` stage.
- **Full Lucene power.** BM25 relevance, fuzzy matching, autocomplete, faceted navigation, synonyms, custom analyzers.

For DZZLO OMS — where you need vehicle / order / dealer search with typo tolerance, autocomplete, and dashboards with filter counts — it's the right call.

---

## Creating a search index

You can create a search index four ways:

### 1. Atlas UI

1. Go to your cluster → **Search** tab → **Create Search Index**.
2. Choose **Visual Editor** (click-through) or **JSON Editor** (paste JSON).
3. Pick the database and collection (e.g. `dzzlo_oms.dealer_msts`).
4. Give the index a name — this is the `index` value you pass in `$search` stages. A common convention: `dealer_default`, `order_default`, `vehicle_autocomplete`.
5. Paste the JSON definition (see below).
6. Click **Create**. Atlas will build the index — a few seconds on small collections, longer on millions of docs. Status goes from **Building** → **Active**.

### 2. Atlas CLI

```bash
# Install once
brew install mongodb-atlas-cli
atlas auth login

# Create the index
atlas clusters search indexes create \
  --clusterName dzzlo-cluster \
  --file ./atlas-search/dealer_default.json
```

Where `dealer_default.json` contains:

```json
{
  "name": "dealer_default",
  "database": "dzzlo_oms",
  "collectionName": "dealer_msts",
  "mappings": {
    "dynamic": false,
    "fields": {
      "dealer_name": { "type": "string", "analyzer": "lucene.standard" },
      "dealer_code": { "type": "string", "analyzer": "lucene.keyword" },
      "dealer_city": { "type": "string" },
      "created_at":  { "type": "date" }
    }
  }
}
```

### 3. Atlas Administration API

```bash
curl --user "$PUBLIC:$PRIVATE" --digest \
  --header "Content-Type: application/json" \
  --request POST \
  --data @dealer_default.json \
  "https://cloud.mongodb.com/api/atlas/v2/groups/$PROJECT_ID/clusters/$CLUSTER/fts/indexes"
```

### 4. Directly from the driver (Mongo 7+)

In your mongosh or Node driver:

```js
db.dealer_msts.createSearchIndex({
  name: "dealer_default",
  definition: {
    mappings: {
      dynamic: false,
      fields: {
        dealer_name: { type: "string", analyzer: "lucene.standard" },
        dealer_code: { type: "string", analyzer: "lucene.keyword" },
        dealer_city: { type: "string" },
        created_at: { type: "date" },
      },
    },
  },
});
```

For DZZLO OMS, we recommend: **commit the JSON definitions to your repo** (e.g. `backend/atlas-search/*.json`) and apply them via CI with the Atlas CLI. That way the search schema is versioned like regular migrations.

---

## Anatomy of an index JSON definition

A complete definition has four top-level sections:

```json
{
  "name": "order_default",
  "mappings": { ... },
  "analyzers": [ ... ],
  "storedSource": { ... }
}
```

| Field         | Purpose                                                                            |
| ------------- | ---------------------------------------------------------------------------------- |
| `name`        | The index name used in `$search`                                                   |
| `mappings`    | Which fields are indexed and how                                                   |
| `analyzers`   | Optional custom analyzers (tokenizer + filters)                                    |
| `storedSource`| Which fields to store inline so projections don't need an extra Mongo lookup       |

### storedSource — big performance trick

By default, Atlas Search stores only the `_id` in the index, so projecting any other field requires a round-trip to the main collection. You can change that:

```json
{
  "storedSource": {
    "include": [
      "dealer_name",
      "dealer_code",
      "dealer_city"
    ]
  }
}
```

Now those fields come back directly from the index. Use this on fields that are in almost every search response.

---

## Static vs dynamic mappings

This is the single most important decision you'll make per index.

### Dynamic — "index everything"

```json
{ "mappings": { "dynamic": true } }
```

- Atlas indexes **every field in every document** with sensible defaults.
- Pro: one line, works immediately, great for prototypes.
- Con: larger index, slower builds, you can't tune per-field analyzers.

### Static — "index only what I list"

```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "order_no":    { "type": "string", "analyzer": "lucene.keyword" },
      "customer_name": { "type": "string", "analyzer": "lucene.standard" },
      "remarks":     { "type": "string", "analyzer": "lucene.english" },
      "status":      { "type": "string", "analyzer": "lucene.keyword" },
      "order_date":  { "type": "date" },
      "order_total": { "type": "number" }
    }
  }
}
```

- Explicit, auditable, smaller, faster.
- You must update the definition when you add a searchable field.
- This is the **recommended approach for production** in DZZLO OMS.

### Hybrid — the best of both

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "dealer_name": [
        { "type": "string", "analyzer": "lucene.standard" },
        { "type": "autocomplete", "tokenization": "edgeGram" }
      ]
    }
  }
}
```

Note that `dealer_name` is an **array** of two index definitions. Atlas indexes it in two ways — as a searchable string AND as an autocomplete field — so you can do either query on the same underlying data.

### Rule of thumb

- **Prototype / demo** → `dynamic: true`
- **Production on a real collection** → `dynamic: false` + explicit fields
- **Field needs both text and autocomplete** → array of mappings
- **New field shows up in docs but not in search** → you forgot to add it to `fields`

---

## Field types cheat sheet

| Type            | Used for                                         | Key options                                       |
| --------------- | ------------------------------------------------ | ------------------------------------------------- |
| `string`        | Free text, codes, names                          | `analyzer`, `searchAnalyzer`, `store`, `indexOptions` |
| `autocomplete`  | As-you-type search boxes                         | `tokenization` (`edgeGram`, `rightEdgeGram`, `nGram`), `minGrams`, `maxGrams`, `foldDiacritics` |
| `date`          | Timestamps, order dates                          | —                                                 |
| `number`        | Prices, counts, scores                           | `representation` (`int64`, `double`)             |
| `boolean`       | Flags                                            | —                                                 |
| `objectId`      | `_id` references                                 | —                                                 |
| `geo`           | Lat/lng                                          | `indexShapes`                                     |
| `embeddedDocuments` | Arrays of sub-documents that you need to search as a unit | `dynamic`, `fields`                |
| `document`      | Regular nested object                            | `dynamic`, `fields`                              |
| `token`         | Like keyword — no tokenisation, fast equality    | `normalizer`                                      |

---

## The `$search` aggregation stage

Golden rules:

1. `$search` must be the **first stage** of the pipeline. Not second, not third, first.
2. You can only use **one search index per stage**, but you can have multiple search indexes on the same collection.
3. `$search` returns results sorted by **relevance score** by default. Add `$sort` yourself if you need a different order.
4. Use `$searchMeta` (not `$search`) when you only want metadata like facets or count.

### Basic shape

```js
db.collection.aggregate([
  {
    $search: {
      index: "my_index_name", // defaults to "default"
      <operator>: { ... },
      highlight: { ... },    // optional
      count: { type: "total" }, // optional
      returnStoredSource: true, // optional
    },
  },
  // ...more stages
]);
```

---

## Operators by example

### `text` — the workhorse

```js
db.dealer_msts.aggregate([
  {
    $search: {
      index: "dealer_default",
      text: {
        query: "sharma motors",
        path: ["dealer_name", "dealer_trade_name"],
      },
    },
  },
  { $limit: 20 },
]);
```

Options:
- `query` — the search string
- `path` — the field(s) to search, single string or array
- `fuzzy` — typo tolerance (see below)
- `score` — boost or reshape scoring

### Phrase search

```js
{
  $search: {
    index: "order_default",
    phrase: {
      query: "cash on delivery",
      path: "remarks",
      slop: 2, // allow up to 2 words between
    },
  },
}
```

`slop: 0` = exact phrase. Higher values allow words in between.

### Wildcard

```js
{
  $search: {
    index: "vehicle_default",
    wildcard: {
      query: "KA01*",
      path: "veh_reg_no",
      allowAnalyzedField: true,
    },
  },
}
```

Use `?` for a single character, `*` for any number.

### Regex

```js
{
  $search: {
    index: "vehicle_default",
    regex: {
      query: "KA(01|02|03).*",
      path: "veh_reg_no",
      allowAnalyzedField: true,
    },
  },
}
```

Slower than `wildcard`. Prefer `wildcard` when possible.

### Range — numbers and dates

```js
{
  $search: {
    index: "order_default",
    range: {
      path: "order_date",
      gte: ISODate("2026-01-01"),
      lte: ISODate("2026-04-30"),
    },
  },
}
```

Also works on numbers:

```js
{
  range: {
    path: "order_total",
    gte: 10000,
    lt: 50000,
  },
}
```

### Equals — exact match

Use `equals` (not `text`) when you want a precise match on boolean / ObjectId / number / date.

```js
{
  equals: {
    path: "is_active",
    value: true,
  },
}
```

### Autocomplete with edge n-grams

First, define the field as `autocomplete` in the index:

```json
{
  "mappings": {
    "fields": {
      "veh_reg_no": {
        "type": "autocomplete",
        "tokenization": "edgeGram",
        "minGrams": 2,
        "maxGrams": 15,
        "foldDiacritics": true
      }
    }
  }
}
```

Then query it:

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
]);
```

Tokenization options:
- `edgeGram` — indexes the start of the word: `K`, `KA`, `KA0`, `KA01`, `KA01A`...
- `rightEdgeGram` — indexes the end of the word
- `nGram` — every substring (larger index, matches anywhere)

### Fuzzy / typo tolerance

```js
{
  text: {
    query: "manogdb",         // typo
    path: "description",
    fuzzy: {
      maxEdits: 2,            // 0, 1, or 2 (2 is the max)
      prefixLength: 2,        // first 2 chars must match exactly
      maxExpansions: 50,      // limit how many variations to try
    },
  },
}
```

Guidance:
- `maxEdits: 1` is usually plenty for dealer / customer names.
- `maxEdits: 2` for freeform text where users mistype more.
- Always set `prefixLength` to 1 or 2 to avoid expensive searches.

### Compound — the pattern you'll use most

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      compound: {
        must: [
          {
            text: {
              query: "urgent",
              path: "remarks",
              fuzzy: { maxEdits: 1 },
            },
          },
        ],
        should: [
          {
            text: {
              query: "priority",
              path: "remarks",
              score: { boost: { value: 2 } },
            },
          },
        ],
        mustNot: [
          { equals: { path: "status", value: "cancelled" } },
        ],
        filter: [
          {
            range: {
              path: "order_date",
              gte: ISODate("2026-01-01"),
              lte: ISODate("2026-04-30"),
            },
          },
          { equals: { path: "dealer_id", value: ObjectId("...") } },
        ],
        minimumShouldMatch: 0,
      },
    },
  },
  { $limit: 25 },
]);
```

The mental model to burn into your brain:

| Clause    | Logic       | Affects score? |
| --------- | ----------- | -------------- |
| `must`    | AND         | Yes            |
| `should`  | OR (soft)   | Yes (boosts)   |
| `mustNot` | NOT         | No             |
| `filter`  | AND (hard)  | No (fast path) |

Put any exact-match filter (status, date range, dealer id, boolean) in `filter`. Only put text queries in `must` / `should`.

### `moreLikeThis`

Find documents similar to an example document. Great for "related orders" widgets.

```js
{
  moreLikeThis: {
    like: { remarks: "bulk delivery cash on delivery urgent" },
  },
}
```

---

## Highlighting

Show users *why* a result matched.

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      text: { query: "delayed shipment", path: "remarks" },
      highlight: {
        path: "remarks",
        maxCharsToExamine: 500000,
        maxNumPassages: 3,
      },
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

`searchHighlights` returns an array like:

```json
[
  {
    "path": "remarks",
    "texts": [
      { "value": "package was ", "type": "text" },
      { "value": "delayed", "type": "hit" },
      { "value": " due to weather", "type": "text" }
    ],
    "score": 3.14
  }
]
```

In the front-end, iterate `texts`, and wrap `type: "hit"` spans in `<mark>` tags.

---

## Faceted search for filter UIs

Facets = the little counts next to sidebar filters ("Pending (124), Completed (312)"). You get them with `$searchMeta`.

```js
db.order_msts.aggregate([
  {
    $searchMeta: {
      index: "order_default",
      facet: {
        operator: {
          text: { query: "urgent", path: "remarks" },
        },
        facets: {
          statusFacet: {
            type: "string",
            path: "status",
            numBuckets: 10,
          },
          cityFacet: {
            type: "string",
            path: "dealer_city",
          },
          monthFacet: {
            type: "date",
            path: "order_date",
            boundaries: [
              ISODate("2026-01-01"),
              ISODate("2026-02-01"),
              ISODate("2026-03-01"),
              ISODate("2026-04-01"),
              ISODate("2026-05-01"),
            ],
            default: "other",
          },
          totalFacet: {
            type: "number",
            path: "order_total",
            boundaries: [0, 1000, 10000, 100000, 1000000],
          },
        },
      },
    },
  },
]);
```

The response looks like:

```json
{
  "count": { "lowerBound": 412 },
  "facet": {
    "statusFacet": {
      "buckets": [
        { "_id": "pending", "count": 124 },
        { "_id": "shipped", "count": 200 },
        { "_id": "delivered", "count": 88 }
      ]
    },
    "monthFacet": {
      "buckets": [
        { "_id": "2026-01-01T00:00:00Z", "count": 98 },
        { "_id": "2026-02-01T00:00:00Z", "count": 132 }
      ]
    }
  }
}
```

Call `$search` for the list and `$searchMeta` for the sidebar in parallel.

---

## Combining `$search` with `$match`, `$lookup`, `$project`

Atlas Search returns a document set. Downstream stages treat it like any other pipeline.

```js
db.order_msts.aggregate([
  {
    $search: {
      index: "order_default",
      compound: {
        must: [{ text: { query: "urgent", path: "remarks" } }],
        filter: [
          {
            range: {
              path: "order_date",
              gte: ISODate("2026-01-01"),
            },
          },
        ],
      },
    },
  },
  // Extra filter that the index can't handle
  { $match: { "items.0": { $exists: true } } },

  // Join dealer info
  {
    $lookup: {
      from: "dealer_msts",
      localField: "dealer_id",
      foreignField: "_id",
      as: "dealer",
    },
  },
  { $unwind: "$dealer" },

  // Shape the response
  {
    $project: {
      order_no: 1,
      status: 1,
      order_date: 1,
      "dealer.dealer_name": 1,
      "dealer.dealer_city": 1,
      score: { $meta: "searchScore" },
    },
  },

  { $sort: { score: -1 } },
  { $skip: 0 },
  { $limit: 25 },
]);
```

Tips:
- Prefer Atlas Search `filter` clauses over a later `$match` — they're indexed.
- Do `$lookup` **after** `$limit` whenever possible, or you'll join every matched doc unnecessarily.
- Use `storedSource` for hot fields to avoid a post-lookup to the main collection.

---

## DZZLO OMS real-world examples

### 1. Vehicle autocomplete on `veh_reg_no`

**Index definition** (`vehicle_autocomplete.json`):

```json
{
  "name": "vehicle_autocomplete",
  "mappings": {
    "dynamic": false,
    "fields": {
      "veh_reg_no": [
        { "type": "string", "analyzer": "lucene.keyword" },
        {
          "type": "autocomplete",
          "tokenization": "edgeGram",
          "minGrams": 2,
          "maxGrams": 15,
          "foldDiacritics": true
        }
      ],
      "veh_make": { "type": "string" },
      "veh_model": { "type": "string" },
      "veh_status": { "type": "string", "analyzer": "lucene.keyword" }
    }
  },
  "storedSource": {
    "include": ["veh_reg_no", "veh_make", "veh_model", "veh_status"]
  }
}
```

**Pipeline**:

```js
// GET /api/vehicles/autocomplete?q=KA01A
exports.vehicleAutocomplete = async (req, res) => {
  const q = (req.query.q || "").trim();
  if (q.length < 2) return res.json([]);

  const items = await Vehicle.aggregate([
    {
      $search: {
        index: "vehicle_autocomplete",
        autocomplete: {
          query: q,
          path: "veh_reg_no",
          tokenOrder: "sequential",
          fuzzy: { maxEdits: 1, prefixLength: 2 },
        },
      },
    },
    { $limit: 10 },
    {
      $project: {
        _id: 1,
        veh_reg_no: 1,
        veh_make: 1,
        veh_model: 1,
        veh_status: 1,
        score: { $meta: "searchScore" },
      },
    },
  ]);

  res.json(items);
};
```

### 2. Dealer search with typo tolerance

**Index** (`dealer_default.json`):

```json
{
  "name": "dealer_default",
  "mappings": {
    "dynamic": false,
    "fields": {
      "dealer_name": { "type": "string", "analyzer": "lucene.standard" },
      "dealer_code": { "type": "string", "analyzer": "lucene.keyword" },
      "dealer_city": { "type": "string", "analyzer": "lucene.keyword" },
      "dealer_gst":  { "type": "string", "analyzer": "lucene.keyword" },
      "is_active":   { "type": "boolean" },
      "created_at":  { "type": "date" }
    }
  }
}
```

**Pipeline**:

```js
// GET /api/dealers?q=sharmah&city=Bangalore
exports.searchDealers = async (req, res) => {
  const { q, city, active = "true", page = 1, limit = 25 } = req.query;

  const must = [];
  const filter = [
    { equals: { path: "is_active", value: active === "true" } },
  ];
  if (city) filter.push({ equals: { path: "dealer_city", value: city } });

  if (q && q.trim()) {
    must.push({
      text: {
        query: q,
        path: ["dealer_name", "dealer_code", "dealer_gst"],
        fuzzy: { maxEdits: 2, prefixLength: 1 },
      },
    });
  }

  const pipeline = [
    {
      $search: {
        index: "dealer_default",
        compound: {
          ...(must.length ? { must } : {}),
          filter,
        },
        highlight: { path: "dealer_name" },
      },
    },
    { $skip: (Number(page) - 1) * Number(limit) },
    { $limit: Number(limit) },
    {
      $project: {
        dealer_code: 1,
        dealer_name: 1,
        dealer_city: 1,
        highlights: { $meta: "searchHighlights" },
        score: { $meta: "searchScore" },
      },
    },
  ];

  const items = await Dealer.aggregate(pipeline);
  res.json({ items });
};
```

Note: when `q` is empty we still want the dealer list to work, so we only add the `must` clause if there's a query.

### 3. Orders — date range + text + status filter + facets

**Index** (`order_default.json`):

```json
{
  "name": "order_default",
  "mappings": {
    "dynamic": false,
    "fields": {
      "order_no":      { "type": "string", "analyzer": "lucene.keyword" },
      "customer_name": { "type": "string", "analyzer": "lucene.standard" },
      "remarks":       { "type": "string", "analyzer": "lucene.english" },
      "status":        { "type": "stringFacet" },
      "dealer_id":     { "type": "objectId" },
      "dealer_city":   { "type": "stringFacet" },
      "order_date":    { "type": "date" },
      "order_total":   { "type": "number" }
    }
  }
}
```

`stringFacet` is a faceted variant of string — lets you use it inside `$searchMeta` facets.

**List pipeline**:

```js
// GET /api/orders?q=urgent&status=pending&from=2026-01-01&to=2026-04-30
exports.listOrders = async (req, res) => {
  const {
    q,
    status,
    from,
    to,
    dealer_id,
    page = 1,
    limit = 25,
  } = req.query;

  const filter = [];
  if (status) filter.push({ equals: { path: "status", value: status } });
  if (dealer_id)
    filter.push({
      equals: { path: "dealer_id", value: new ObjectId(dealer_id) },
    });
  if (from || to)
    filter.push({
      range: {
        path: "order_date",
        ...(from ? { gte: new Date(from) } : {}),
        ...(to ? { lte: new Date(to) } : {}),
      },
    });

  const must = [];
  if (q && q.trim()) {
    must.push({
      text: {
        query: q,
        path: ["remarks", "order_no", "customer_name"],
        fuzzy: { maxEdits: 1 },
      },
    });
  }

  const pipeline = [
    {
      $search: {
        index: "order_default",
        compound: {
          ...(must.length ? { must } : {}),
          filter,
        },
      },
    },
    { $sort: { order_date: -1 } },
    { $skip: (Number(page) - 1) * Number(limit) },
    { $limit: Number(limit) },
    {
      $project: {
        order_no: 1,
        status: 1,
        order_date: 1,
        customer_name: 1,
        order_total: 1,
      },
    },
  ];

  const items = await Order.aggregate(pipeline);
  res.json({ items, page, limit });
};
```

**Facets pipeline** (called in parallel for the sidebar counts):

```js
exports.orderFacets = async (req, res) => {
  const { q, from, to } = req.query;

  const facetOperator = q
    ? { text: { query: q, path: ["remarks", "order_no", "customer_name"] } }
    : { exists: { path: "_id" } };

  const result = await Order.aggregate([
    {
      $searchMeta: {
        index: "order_default",
        facet: {
          operator: facetOperator,
          facets: {
            statusFacet: { type: "string", path: "status" },
            cityFacet: { type: "string", path: "dealer_city" },
            dateFacet: {
              type: "date",
              path: "order_date",
              boundaries: [
                new Date("2026-01-01"),
                new Date("2026-02-01"),
                new Date("2026-03-01"),
                new Date("2026-04-01"),
                new Date("2026-05-01"),
              ],
            },
          },
        },
      },
    },
  ]);

  res.json(result[0] || { count: { lowerBound: 0 }, facet: {} });
};
```

### 4. "More like this" — related orders for a given order

```js
const order = await Order.findById(id).lean();

const related = await Order.aggregate([
  {
    $search: {
      index: "order_default",
      moreLikeThis: {
        like: {
          remarks: order.remarks,
          customer_name: order.customer_name,
        },
      },
    },
  },
  { $match: { _id: { $ne: order._id } } },
  { $limit: 5 },
]);
```

---

## Pricing and tier limits

At the time of writing (Atlas 2025-2026):

| Tier      | Atlas Search available? | Limits                                              |
| --------- | ----------------------- | --------------------------------------------------- |
| M0 (free) | **Yes**                 | 3 search indexes total per cluster, slower builds   |
| M2 / M5   | Yes (shared)            | Small indexes only                                  |
| M10+      | Yes (dedicated)         | No index-count hard cap, better performance         |
| Serverless| Yes                     | RPU-based pricing, scales to zero                   |

Atlas Search on dedicated tiers (M10+) runs in a separate `mongot` process per node — you don't pay for a standalone service, but it does consume some of the node's CPU / RAM. For heavy search workloads Atlas offers **Search Nodes**, which are dedicated search-only VMs you can add to the cluster.

**For DZZLO OMS on M10/M20**, start with no search nodes. If search latency becomes a bottleneck at scale, add 1-2 search nodes sized to your index.

---

## Performance and warming

### 1. Use `filter` instead of `must` for exact-match conditions

```js
// Slow — status contributes to scoring even though it's an exact match
compound: {
  must: [
    { text: { query: "urgent", path: "remarks" } },
    { equals: { path: "status", value: "pending" } },
  ],
}

// Fast — status is a filter, no scoring work
compound: {
  must: [{ text: { query: "urgent", path: "remarks" } }],
  filter: [{ equals: { path: "status", value: "pending" } }],
}
```

### 2. Limit early

```js
// Good
[
  { $search: { ... } },
  { $limit: 25 },
  { $lookup: { ... } },
]

// Bad — lookup happens on every match
[
  { $search: { ... } },
  { $lookup: { ... } },
  { $limit: 25 },
]
```

### 3. Use `storedSource` for hot fields

Projecting a field that isn't stored triggers a round-trip to the main collection per result. Put frequently-projected fields in `storedSource.include`.

### 4. Avoid wildcard / regex on analyzed fields

They are much slower than `text` or `autocomplete` equivalents. Only use them when nothing else works.

### 5. Warm the cache

After a restart or an index rebuild, the first few queries are slow because Lucene has to load segments into memory. On a busy production system this isn't an issue, but if you have traffic spikes, you can warm the index by running a representative query on deploy:

```js
// in your startup script
await Order.aggregate([
  { $search: { index: "order_default", text: { query: "warmup", path: "remarks" } } },
  { $limit: 1 },
]);
```

### 6. Monitor with `explain`

```js
db.order_msts.aggregate(
  [{ $search: { index: "order_default", text: { query: "urgent", path: "remarks" } } }],
  { explain: true },
);
```

This returns the query plan from `mongot`. Look for slow operators and the doc count touched.

### 7. Keep index definitions in source control

Treat them like migrations. Store them in `backend/atlas-search/*.json` and apply via CI.

---

## Troubleshooting

### "No matches when I know there should be some"

- Did you add the field to `mappings.fields`? (If `dynamic: false`, you must.)
- Is the analyzer right? `lucene.keyword` treats the whole string as one token, so partial matches will fail.
- Is the index still **Building**? Give it a minute and check the Atlas UI.
- Is the case right? Autocomplete is case-sensitive unless you set `foldDiacritics: true` and / or use a lowercasing analyzer.

### "Results are slow"

- Are you doing `$lookup` before `$limit`? Move `$limit` up.
- Are you using `filter` for exact matches? (See above.)
- Is the collection huge and the index unstored? Add `storedSource`.
- Are you using wildcard or regex when `text` would do?

### "Fuzzy is matching too much"

- Drop `maxEdits` to 1.
- Increase `prefixLength` so the first few chars must match exactly.

### "`$search` must be the first stage" error

- You accidentally put a `$match` or `$project` before `$search`. Move `$search` to the top.

### "I need to update an index definition"

- Atlas Search indexes are **immutable** in the old API. You `dropSearchIndex` and create a new one. In Atlas 7+ you can call `updateSearchIndex` to change mappings in place.

---

That's the full Atlas Search playbook for DZZLO OMS. Pair this with the index JSONs in `backend/atlas-search/` and you have a production-ready search layer without running a single extra service.
