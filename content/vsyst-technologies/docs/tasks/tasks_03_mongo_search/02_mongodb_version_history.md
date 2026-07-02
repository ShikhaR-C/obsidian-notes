# MongoDB Version History & Upgrade Guide (for DZZLO OMS)

> Current state of DZZLO OMS:
>
> - **Server**: MongoDB Atlas running **7.0.31**
> - **Backend driver**: `mongodb` **^7.1.1**
> - **ODM**: `mongoose` **^9.4.1**
>
> This document traces MongoDB's version history from 4.x through 8.x, deep-dives into what 7.0 and 8.0 bring, explains what it takes to upgrade our Atlas cluster safely, and gives a clear recommendation.

---

## Table of Contents

1. [Why Version Matters](#1-why-version-matters)
2. [Release Cadence and Support Policy](#2-release-cadence-and-support-policy)
3. [Timeline: 4.x → 5.0 → 6.0 → 7.0 → 8.0 → 8.2](#3-timeline-4x--50--60--70--80--82)
4. [What's in MongoDB 7.0 (Where We Are Today)](#4-whats-in-mongodb-70-where-we-are-today)
5. [What's New in MongoDB 8.0](#5-whats-new-in-mongodb-80)
6. [MongoDB 8.0 Performance Benchmarks](#6-mongodb-80-performance-benchmarks)
7. [Breaking Changes Between 7.0 and 8.0](#7-breaking-changes-between-70-and-80)
8. [Driver & Mongoose Compatibility Matrix](#8-driver--mongoose-compatibility-matrix)
9. [Is It Safe to Upgrade Atlas from 7.0.31 to 8.0?](#9-is-it-safe-to-upgrade-atlas-from-7031-to-80)
10. [Atlas Upgrade Path — Step by Step](#10-atlas-upgrade-path--step-by-step)
11. [Pre-Upgrade Checklist](#11-pre-upgrade-checklist)
12. [Recommendation](#12-recommendation)
13. [Sources](#13-sources)

---

## 1. Why Version Matters

MongoDB major versions are **not just bug fixes**. Each one ships new query operators, new aggregation stages, new storage / replication / sharding behaviours, performance rewrites, and sometimes schema-affecting changes. A version that is one year out of date is usually fine; one that is three years out of date often means you are missing major throughput improvements, have fallen off the security-patch window, or can no longer use modern drivers.

For an order management system that runs 24/7 against Atlas, the two reasons to care about version are:

1. **Security patches** — once a major release goes End-of-Life (EOL), it no longer receives fixes. Running EOL software in production is a compliance / audit problem.
2. **Performance** — 8.0 specifically is billed as a performance-focused release, and for a workload like ours (many reads, many writes, time-series-ish order stream, aggregation-heavy dashboards) the gains are real money.

---

## 2. Release Cadence and Support Policy

MongoDB ships in two tracks:

- **Major releases** — one per year. MongoDB's stated policy is ~30 months of support from GA, but the published EOL dates have run closer to **36 months** (6.0: 36 mo, 7.0: 36 mo) — always confirm against the official lifecycle page. These are the versions you run on-prem or pin in Atlas. Examples: 5.0, 6.0, 7.0, 8.0.
- **Rapid releases** — shipped every ~quarter in Atlas only, used as a preview/staging ground for features that will roll into the next major. Examples: 7.1, 7.2, 7.3, 8.1, 8.2. You do not run these on-prem, and you should not pin them long-term on Atlas.

In practice: once a major hits GA, you have roughly three years before you are pushed to upgrade — but check the exact published date per release rather than assuming.

---

## 3. Timeline: 4.x → 5.0 → 6.0 → 7.0 → 8.0 → 8.2

| Major version   | GA release         | End of life (security support) | Status (April 2026)         | Notable themes                                                                                                                                       |
| --------------- | ------------------ | ------------------------------ | --------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **4.0**         | July 2018          | April 2022                     | EOL                         | First multi-document ACID transactions (replica sets)                                                                                                |
| **4.2**         | August 2019        | April 2023                     | EOL                         | Distributed transactions (sharded), on-disk encryption, wildcard indexes                                                                             |
| **4.4**         | July 2020          | February 2024                  | EOL                         | Hedged reads, refinable shard keys, union `$unionWith`, compound hashed shard keys                                                                   |
| **5.0**         | July 13, 2021      | October 31, 2024               | EOL                         | Native time-series collections, window functions, resharding, versioned API, client-side field-level encryption (CSFLE) GA                           |
| **6.0**         | July 19, 2022      | July 31, 2025                  | EOL                         | Queryable encryption (preview), change-stream pre/post-images, cluster-to-cluster sync, time-series secondary indexes, column store index (preview)  |
| **7.0**         | August 15, 2023    | **August 31, 2026** (verify on lifecycle page) | **Supported — EOL near**    | Queryable encryption GA, approximate percentiles, compound wildcard indexes, shard key resharding on live workloads, large initial sync improvements |
| **8.0**         | October 2, 2024    | ~October 2027 (est. 36 mo; verify) | **Supported, latest major** | Huge performance rewrite, range-queryable encryption, faster sharding, new `bulkWrite`, block processing for time-series, explain v2                 |
| **8.2** (rapid) | September 17, 2025 | July 31, 2026                  | Atlas-only                  | Incremental improvements on top of 8.0                                                                                                               |

> **Note on 4.x**: 4.0, 4.2 and 4.4 are _all_ EOL. If you ever see an older Mongo somewhere in the org, upgrade aggressively.
> **Note on 5.0 and 6.0**: as of late 2024 / mid 2025 respectively, they no longer receive security patches. Anything still on 5.0/6.0 is living on borrowed time.
> **Our cluster**: 7.0.31 — a patch release of 7.0, supported until **August 31, 2026** per MongoDB's published lifecycle (verify before planning). That is much closer than it sounds — treat the 8.0 upgrade as near-term scheduled work, not a someday item.

### Atlas-only "rapid" versions

Atlas sometimes exposes versions such as 7.1, 7.2, 7.3 or 8.1, 8.2. These are **rapid releases**: they preview features that will ship in the next major. They are not supported for on-prem use and should not be used for long-term production pinning; think of them as early access.

---

## 4. What's in MongoDB 7.0 (Where We Are Today)

We run 7.0.31, the 31st patch release of the 7.0 line. The important features you can already use today:

### Security & encryption

- **Queryable Encryption (GA)** — encrypt individual fields with keys held client-side and still perform **equality** queries on them. The server only ever sees ciphertext. Use case for us: customer mobile numbers, GSTIN.
- **OIDC authentication** — federated login via identity providers.
- **Kerberos and LDAP** refinements.

### Query & aggregation

- **`$percentile` and `$median`** aggregation operators — approximate percentiles computed in a single pass. Great for dashboards ("p95 order value").
- **Compound wildcard indexes** — combine a wildcard field (`"attributes.$**"`) with known fields (e.g. `cust_id`). Previously wildcard indexes had to stand alone.
- **`$changeStreamSplitLargeEvent`** — handle change-stream events whose payload exceeds 16 MB.
- **Approximate count improvements** — `$count` and `countDocuments` faster on large collections.

### Sharding & replication

- **Resharding on live workloads** — reshape the shard key without a maintenance window.
- **Initial sync from backup** — a new replica set member can bootstrap from a snapshot instead of the oplog, dramatically cutting the onboarding time for a replacement node.
- **Chunk migrations in parallel** across multiple shards.

### Storage

- **WiredTiger improvements**: smaller indexes, better compression defaults, faster range scans.

### Driver / API

- **Stable API v1** refinements (`serverApi: { version: "1" }`), so driver code tied to the stable API keeps working across server upgrades.

We already benefit from all of the above. Everything below is what we would _gain_ by moving to 8.0.

---

## 5. What's New in MongoDB 8.0

MongoDB 8.0 went GA on **October 2, 2024**. MongoDB positions it as its "most performant and scalable release ever", and the benchmarks (see §6) back the marketing. The highlights:

### 5.1 Performance (the headline)

Internal rearchitecting of query execution, WiredTiger internals, replication, sharding, and time-series led to large improvements that are essentially free when you upgrade — you do not have to rewrite any queries.

Highlights claimed by MongoDB Inc. (vs 7.0 on identical hardware):

- **~36% higher read throughput**
- **~56% faster bulk writes**
- **~20% faster concurrent writes during replication**
- **Up to 200% faster handling of high-volume time-series workloads**
- **~54% faster bulk inserts**
- **~60% faster aggregations on time-series data**
- **~25% better throughput and latency across broadly mixed workloads**

These numbers are discussed more in §6.

### 5.2 Queryable Encryption — range queries

7.0 made Queryable Encryption GA with _equality_ queries. 8.0 adds **range** query support:

```js
// On an encrypted "balance" field you can now do:
Customer.find({
  balance: { $gt: 10_000, $lte: 50_000 },
});
```

Under the hood the driver builds a query structure the server can traverse without ever decrypting. Operators supported on encrypted fields: `$lt`, `$lte`, `$gt`, `$gte` (plus the existing `$eq`/`$in`).

### 5.3 New `bulkWrite` command (multi-collection)

Before 8.0, `bulkWrite` was scoped to a single collection. From 8.0 a new top-level command accepts a mixed batch that targets **many collections at once**, in one round-trip:

```js
await db.command({
  bulkWrite: 1,
  ops: [
    { insert: 0, document: { _id: 1, v: "a" } },
    { update: 1, filter: { _id: 2 }, updateMods: { $set: { v: "b" } } },
    { delete: 2, filter: { _id: 3 } },
  ],
  nsInfo: [
    { ns: "dzzlo_oms.order_msts" },
    { ns: "dzzlo_oms.counters" },
    { ns: "dzzlo_oms.pay_trns" },
  ],
});
```

This is a genuine throughput win for request handlers that currently do 3 separate `updateOne` calls against different collections.

### 5.4 Time-series enhancements

Time-series collections were introduced in 5.0 and have gotten better every major since. 8.0 delivers the biggest jump so far:

- **Block processing** — aggregations over time-series data operate on compressed column blocks instead of exploded documents, skipping entire blocks whose min/max bounds cannot match the query. This is the source of the 200% / 60% improvements.
- **Partial indexes on time-series** collections with richer predicates.
- **`$shardedDataDistribution` view** for time-series.
- Reshaping (resharding / refining key) on time-series collections.

Our current order stream could plausibly be modelled as a time-series collection if we wanted analytics-style queries to fly, though that is a separate design decision.

### 5.5 Sharding improvements

- **Up to 50× faster** to distribute data across new shards during initial balancing.
- **Up to 50% lower starting cost** because you can begin sharded with fewer resources and grow.
- **Resharding** is itself significantly faster, cutting the wall-clock time of a migration.
- **`moveCollection`** — move an entire unsharded collection to another shard without going through `shardCollection` first.

### 5.6 Query engine and operators

- **Explain v2** with richer per-stage statistics and a clearer winning-plan representation.
- **Faster `$lookup`** for the common "left join then $unwind" pattern — the planner fuses the stages.
- **`$rankFusion`** for hybrid search scoring (combine vector + text) — note: this shipped in the 8.1/8.2 **rapid** releases, not in 8.0 GA; a cluster pinned to the 8.0 major does not get it.
- Extended expressions: richer `$dateDiff`, new `$median`/`$percentile` optimisations, improved `$setWindowFields` memory usage.

### 5.7 Operational quality of life

- **Index build progress visible in `currentOp`** more granularly.
- **Faster `listCollections`** on databases with thousands of collections.
- **Improved `compact`** with concurrent chunking.
- **Log-line structured output** includes better planning information.

### 5.8 Rapid releases already building on 8.0

MongoDB 8.1 and 8.2 (rapid, Atlas only) continue to iterate — expect more vector search and query-engine work. If you stay on the major 8.0 line you will miss these features until 9.0, but that is the normal tradeoff for running a supported LTS-style release.

---

## 6. MongoDB 8.0 Performance Benchmarks

The numbers in §5.1 come from MongoDB Inc.'s published benchmarks and InfoQ / BigDATAwire coverage of the 8.0 launch (October 2024). Summarised in one table:

| Workload                             | Improvement (vs 7.0) |
| ------------------------------------ | -------------------- |
| Read throughput (mixed OLTP)         | **+36%**             |
| Bulk inserts                         | **+54%**             |
| Bulk writes (mixed ops)              | **+56%**             |
| Concurrent writes during replication | **+20%**             |
| Aggregations on time-series data     | **+60%**             |
| High-volume time-series ingest       | **+200%**            |
| Overall throughput / latency (mixed) | **+25%**             |
| Sharding data distribution           | **up to 50× faster** |

### How to read these numbers

- These are **MongoDB's own benchmarks on reference hardware**, with workloads designed to highlight the improvements. Your mileage will vary. Do not expect every query to be 36% faster.
- Time-series numbers assume you actually use **time-series collections**, not regular collections that happen to hold timestamps. We don't today, so the 200% figure does not apply until we adopt them.
- Write throughput gains are real under load but may be invisible on a lightly-loaded cluster (you were already well under capacity, so "faster" reads as "same wall-clock time, lower CPU").
- The **most reliable everyday win** is the WiredTiger + query-executor improvements — lower CPU, lower latency at p95/p99, smoother burst behaviour.

For DZZLO OMS specifically the most relevant wins are:

1. **Bulk writes** — invoice posting, batch order imports, end-of-day settlement.
2. **Aggregations** — dashboards and reports.
3. **Concurrent writes during replication** — every write today replicates to two secondaries on Atlas; any speedup there shows up as lower client-visible commit latency.

---

## 7. Breaking Changes Between 7.0 and 8.0

A major upgrade is not just "turn it on and collect the perf". There are real behaviour changes. The ones that matter most for our stack:

### 7.1 Query semantics

- **`null` vs `undefined` equality**: starting in 8.0, equality match against `null` no longer matches `undefined` values. Previously a document `{ x: undefined }` (rare but possible via the driver) would match `{ x: null }` and vice-versa. Now they are distinct.

  Impact for us: **minimal**. Mongoose stores missing fields as absent rather than `undefined`, so this rarely bites application code — but worth grepping for queries that deliberately rely on the old behaviour.

- **Geospatial queries reject malformed input**: 7.0 accepted certain malformed GeoJSON objects and returned no results. 8.0 returns an explicit error.

  Impact for us: **none today** (no geospatial queries), but keep in mind if we ever add driver GPS tracking.

- **Aggregation against non-existent databases on `mongos`** now returns a validation error instead of an empty cursor (this change actually landed in 7.2/7.3 already, so we would get it on the 8.0 upgrade).

### 7.2 Removed / deprecated server features

- **`storeFindAndModifyImagesInSideCollection` server parameter** is removed.
- **`numInitialChunks` option** on `shardCollection` is removed (since 7.2). We are not sharded, so this does not affect us.
- **Legacy opcodes** (`OP_QUERY`, `OP_GET_MORE`, `OP_KILL_CURSORS`) that were deprecated long ago continue to be removed from the wire protocol. Any driver older than ~2020 will stop working. Our driver is 7.1.1 — modern and safe.

### 7.3 Concurrent admin commands

- **Concurrent `compact`** on the same collection now errors. Before 8.0 you could fire two, and the second would quietly wait/fail in inconsistent ways.

### 7.4 Index builds

- **Rolling index builds** now coordinate more strictly across the replica set; extremely large indexes may surface new errors instead of silently hanging.

### 7.5 Feature Compatibility Version (FCV)

After bumping the binary to 8.0 you **must** bump FCV from `7.0` to `8.0` for the 8.0-only features (range-encrypted queries, multi-collection `bulkWrite`, etc.) to be enabled. Atlas has a UI checkbox for this. Keep FCV at 7.0 for a day or two to prove the upgrade is stable, then promote.

> **Gotcha seen in the wild** (LibreChat discussion #10309 on GitHub): people upgrading via Docker sometimes skip the FCV bump, and the next major (8.2) refuses to start because FCV is still 7.0. Don't leave FCV behind indefinitely.

### 7.6 Upgrade path constraint

**You cannot skip majors.** To land on 8.0 you must currently be on 7.0. We are on 7.0.31, so we are eligible. If you were on 6.0 you would first upgrade to 7.0 and only then to 8.0. Atlas enforces this rule in the UI.

---

## 8. Driver & Mongoose Compatibility Matrix

The short answer: **we are already on versions that fully support MongoDB 8.0.** Details:

### 8.1 Mongoose ↔ MongoDB server

According to the Mongoose docs (mongoosejs.com/docs/compatibility.html):

| Mongoose version | MongoDB 6.x | MongoDB 7.x | MongoDB 8.x |
| ---------------- | :---------: | :---------: | :---------: |
| 6.5+             |    yes\*    |   partial   |     no      |
| 7.0 – 7.3        |     yes     |   partial   |     no      |
| 7.4+             |     yes     |   **yes**   |     no      |
| 8.0 – 8.6        |     yes     |     yes     |   partial   |
| **8.7+**         |     yes     |     yes     |   **yes**   |
| **9.0+**         |     yes     |     yes     |   **yes**   |

_\*Some newer 7.x server features are not exposed in 6.x Mongoose._

We use **Mongoose 9.4.1**, which is fully compatible with MongoDB 8.x. No ODM upgrade is required before upgrading the server.

### 8.2 Node.js driver ↔ MongoDB server

MongoDB supports the current driver minor against at least two previous server majors. The driver version we use (`mongodb` **7.1.1**) fully supports 7.0, 8.0 and the 8.x rapid releases.

| `mongodb` driver | 6.0 | 7.0 |            8.0             |
| ---------------- | :-: | :-: | :------------------------: |
| 5.x              | yes | yes | partial (pre-8.0 features) |
| 6.x              | yes | yes |      yes (6.10+ only)      |
| **7.x** (us)     | yes | yes |          **yes**           |

In short: **we are already on a driver / ODM combination that officially supports MongoDB 8.0.** Upgrading the server does not require any `package.json` changes to light up the core 8.0 behaviour.

### 8.3 What upgrading Mongoose would add later

Even though 9.4.1 is compatible, specific 8.0 features (e.g. the new multi-collection `bulkWrite`) may only be surfaced cleanly through even newer minor releases. Before depending on such a feature:

1. Check Mongoose's changelog (`CHANGELOG.md`) for the first minor that adds an API for it.
2. If it is not there yet, use `mongoose.connection.db.command({ bulkWrite: 1, ... })` directly — same connection, raw driver.

---

## 9. Is It Safe to Upgrade Atlas from 7.0.31 to 8.0?

**Short answer: yes, with the normal precautions.** This is one of the smoother major upgrades MongoDB has shipped — there are very few behaviour regressions, our driver and Mongoose versions are already 8.0-ready, and Atlas performs the upgrade as a rolling, zero-downtime operation.

Longer answer broken down by risk area:

### 9.1 Atlas operational safety

- Atlas upgrades dedicated clusters by **rolling each replica set member one at a time**: upgrade a secondary, wait for it to catch up, step down the primary, upgrade the old primary. Clients fail over in seconds.
- Atlas automatically takes a **pre-upgrade snapshot**. If something looks wrong, rollback means **restoring that snapshot** (into a 7.0 cluster) — Atlas has no in-place major-version downgrade (see §10.3).
- The process is available via the Atlas UI ("Edit Configuration" → MongoDB version → pick 8.0) and via the Atlas Admin API.
- **Downtime**: practically zero. Expect a few seconds of elevated latency during the primary step-down.

### 9.2 Driver & ODM

Already covered in §8: we are on `mongodb@7.1.1` and `mongoose@9.4.1`, both of which support 8.0. No code changes are required to keep the app running.

### 9.3 Application semantics

- **`null`/`undefined` equality change** (§7.1): grep the codebase for queries that rely on `{ field: null }` matching `undefined`. We don't intentionally do this. Fix if found.
- **No removed aggregation stages or operators** that we use.
- **No index behaviour changes** that affect existing indexes.
- **No wire-protocol removals** that affect our modern driver.

### 9.4 Performance

- 8.0 is **faster on essentially every workload** we run. There is no realistic regression scenario for our shape of data.
- Expect **lower CPU and p95 latency** after the upgrade. Capture baselines before and after (see §11).

### 9.5 Risks that still exist

- **FCV bump forgotten** — the cluster runs happily but 8.0-only features are silently disabled. Not dangerous; just anti-climactic.
- **Third-party integrations** — any tool reading directly from Mongo (BI connectors, backup scripts, observability agents) needs its own version check. List all of them before starting.
- **Custom aggregation edge cases** — a pipeline that unintentionally relied on a bug that was fixed in 8.0. Rare, but the reason we test.

Overall risk: **low**. The upgrade is well within the boundaries of a routine major upgrade.

---

## 10. Atlas Upgrade Path — Step by Step

Atlas exposes major upgrades as a cluster configuration change. The mechanics:

### 10.1 Supported upgrade direction

You can only upgrade from the **immediately previous major**. So:

```
5.0 → 6.0 → 7.0 → 8.0
```

We are on 7.0.31, which is the latest 7.0 patch, so we are at the ideal starting point. Atlas will present 8.0 as an available target.

### 10.2 UI flow

1. Atlas → Database → our cluster → **Edit Configuration**.
2. Scroll to **Additional Settings** → **MongoDB version**.
3. Change from `7.0` to `8.0`.
4. Review the confirmation screen — Atlas will show:
   - Estimated time.
   - Driver compatibility warnings (should be none for us).
   - A note that the cluster will perform a rolling restart.
5. Click **Review Changes** → **Apply Changes**.
6. Atlas rolls each member in turn. Monitor under **Metrics** for:
   - Replication lag on the member being upgraded.
   - Client connection errors (should be zero with a modern driver).
   - CPU spikes.
7. After all members show 8.0, Atlas displays the cluster as `8.0.x`.

### 10.3 Bumping FCV

After the upgrade, the cluster is on 8.0 binaries but **FCV is still 7.0** by default. Atlas shows a banner/button to "Update featureCompatibilityVersion" when you are ready. Recommended approach:

1. **Day 0**: upgrade binaries to 8.0. Leave FCV at 7.0.
2. **Day 0 – 2**: run application tests, monitor metrics, verify nothing regressed.
3. **Day 2+**: click "Update FCV to 8.0" in Atlas.
4. **Stable period**: confirm 8.0-only features (e.g. encrypted range queries) light up.

Leaving FCV at 7.0 for a few days gives you a safety net — but understand its limits. The "downgrade binaries while FCV is held back" path applies to **self-managed** deployments; **Atlas does not offer in-place major-version downgrades at all**. On Atlas, going back means restoring the pre-upgrade snapshot into a 7.0 cluster (possibly support-assisted). Holding FCV at 7.0 still matters: it keeps 8.0-only on-disk format changes off and preserves the widest recovery options. Once FCV = 8.0, restore-from-backup is the only way back anywhere.

### 10.4 Rolling upgrade vs maintenance window

Atlas M10+ dedicated tiers use rolling upgrades automatically. Shared tiers (M0/M2/M5) perform in-place upgrades with brief downtime; DZZLO OMS is on a dedicated tier, so this is not a concern.

### 10.5 Via the Atlas Admin API (for automation)

If you script it, the same operation is a `PATCH` on the cluster document:

```bash
curl -u "PUBLIC_KEY:PRIVATE_KEY" --digest \
  -H "Content-Type: application/json" \
  -X PATCH "https://cloud.mongodb.com/api/atlas/v2/groups/{GROUP_ID}/clusters/{CLUSTER_NAME}" \
  -d '{ "mongoDBMajorVersion": "8.0" }'
```

Not needed for a one-off; useful if we ever manage multiple clusters via Terraform / Atlas CLI.

---

## 11. Pre-Upgrade Checklist

Run through this list **before** you click Apply in Atlas production. Check every box.

### 11.1 Inventory & backups

- [ ] **Confirm current version is 7.0.x** (Atlas → cluster → version). We are on 7.0.31.
- [ ] **Confirm continuous cloud backup is enabled** and the last snapshot is less than 24 hours old.
- [ ] **Trigger a manual on-demand snapshot** just before starting. Label it `pre-8.0-upgrade`.
- [ ] **Know how to restore** into a new cluster from that snapshot — actually try it on a throwaway cluster at least once.

### 11.2 Test environment upgrade first

- [ ] **Spin up a clone of production** (Atlas → Clusters → Create Cluster from Snapshot) or use the existing `staging` cluster.
- [ ] **Upgrade the clone to 8.0** using the same UI flow.
- [ ] **Point `dzzlo_oms_api` (staging config) at the 8.0 clone** and run the full API test suite (`jest`).
- [ ] **Run any known slow / heavy aggregation pipelines** against the clone and record timings.
- [ ] **Exercise the mobile app** against staging for at least a day of realistic use.
- [ ] **Bump FCV to 8.0 on the clone** and re-test, particularly any features you plan to adopt soon.

### 11.3 Application compatibility

- [ ] **Driver version check** — `grep "mongodb" package.json`. Must be `>= 5.x`. We are on 7.1.1. ✅
- [ ] **Mongoose version check** — must be `>= 8.7` (ideally 9.x). We are on 9.4.1. ✅
- [ ] **Third-party integrations** — list every tool that connects to Atlas (backup exporters, BI connectors, monitoring, data pipelines). Check each one's "minimum MongoDB server" docs.
- [ ] **Custom scripts** — any `scripts/*.js` files that use the driver directly need the same version check.
- [ ] **CI environment** — make sure CI uses a driver compatible with 8.0 so tests are meaningful.

### 11.4 Query semantic review

- [ ] Grep the code for **`{ <field>: null }`** queries that might rely on matching `undefined`. Fix if found.
- [ ] Grep for **`$where`** usage (deprecated anyway). Replace with native operators.
- [ ] Grep for any geospatial queries. None today, but worth the 5 seconds.
- [ ] Review any **custom indexes** that currently have unusual options (`storageEngine`, `collation`, etc.) against the 8.0 docs.

### 11.5 Observability baselines

- [ ] Capture **30 days** of Atlas metrics before the upgrade: p50/p95/p99 latency, ops/sec, CPU, memory, replication lag. Export as CSV if needed.
- [ ] Note the **slowest aggregation pipelines** (Atlas Performance Advisor → slow queries) and their baseline timings.
- [ ] Make sure alerts for replication lag, connection count, and primary election are configured and routed to someone who will be awake.

### 11.6 Scheduling

- [ ] Pick a **low-traffic window**. For DZZLO OMS this is roughly 01:00–04:00 local.
- [ ] Notify stakeholders (ops, support, on-call) that a rolling upgrade is happening — even if zero downtime is expected.
- [ ] Have a **rollback plan** written down, even if rollback means "restore from snapshot" (it does, once FCV advances).

### 11.7 Post-upgrade verification

- [ ] **Application smoke tests** pass against production.
- [ ] **Scheduled jobs** (cron, background workers) complete at least one cycle without errors.
- [ ] **Mobile app** login, order creation, order list, vehicle list all work.
- [ ] **Atlas Performance Advisor** shows no new slow queries relative to the baseline.
- [ ] After 1–2 days of clean running: **bump FCV to 8.0**.
- [ ] After another 1–2 days: close the ticket.

---

## 12. Recommendation

**Yes — upgrade Atlas from 7.0.31 to 8.0.** Conditions:

1. Do it in **staging first** — clone production, upgrade the clone, run the API + mobile app against it for at least 24–48 hours.
2. **Keep FCV at 7.0 for the first 1–2 days** in production — it keeps 8.0-only on-disk changes off and preserves the widest recovery options (on Atlas, rollback is restore-from-snapshot either way; see §10.3).
3. Do it in a **low-traffic window** even though the upgrade is rolling.
4. Capture performance baselines **before and after** so you can actually quantify the 8.0 gains on our workload.
5. **Monitor for the first 48 hours** — specifically p95 latency, CPU, connection churn, and any new error patterns.

### Why "yes"

- **We are already on the latest driver and Mongoose**. Zero package updates required.
- **7.0 is still supported** but will be surpassed in newness every week. Upgrading now gets us on the release train early without the "we're running EOL" pressure.
- **The performance improvements are real**, especially for bulk writes and aggregations — both of which our dashboard and end-of-day settlement rely on.
- **Future features** we want — multi-collection `bulkWrite`, time-series block processing, range queryable encryption — are only reachable on 8.0.
- **The rollout mechanism is battle-tested**: zero-downtime rolling upgrade on dedicated Atlas tiers.

### Why "not immediately" (optional caution)

If timing is inconvenient, note the deadline carefully: 7.0's published EOL is **August 31, 2026** (verify on the MongoDB lifecycle page — an earlier draft of this doc said 2027, which was wrong). That leaves only a few months of security support, so there **is** urgency: the upgrade should be treated as near-term work, not deferred to late 2026.

A reasonable compromise if you want to play it safe:

1. **Now**: upgrade a staging clone, build confidence, measure gains.
2. **Within 1–3 months**: upgrade production during a planned maintenance window.
3. **Long term**: track the 9.0 release (not yet GA as of this research — check the MongoDB release notes page for the current status) and plan to upgrade from 8.0 → 9.0 once it matures.

---

## 13. Sources

- MongoDB 8.0 release announcement — https://www.mongodb.com/products/updates/version-release
- MongoDB 8.0 "Raising the Bar" blog — https://www.mongodb.com/company/blog/mongodb-8-0-raising-the-bar
- MongoDB 8.0 release notes — https://www.mongodb.com/docs/manual/release-notes/8.0/
- MongoDB 8.0 compatibility changes — https://www.mongodb.com/docs/manual/release-notes/8.0-compatibility/
- MongoDB 8.0 upgrade from 7.0 — https://www.mongodb.com/docs/manual/release-notes/8.0-upgrade/
- MongoDB 8.0 changelog — https://www.mongodb.com/docs/manual/release-notes/8.0-changelog/
- MongoDB lifecycle / support policy — https://www.mongodb.com/legal/support-policy/lifecycles
- MongoDB version history — https://www.mongodb.com/resources/products/mongodb-version-history
- endoflife.date MongoDB — https://endoflife.date/mongodb
- MongoDB 8.0 migration guide — https://medium.com/mongodb/mongodb-8-0-migration-guide-what-you-need-to-know-before-upgrading-9fc577ab02e6
- Mongoose compatibility matrix — https://mongoosejs.com/docs/compatibility.html
- Mongoose 7.x → 8.x migration — https://mongoosejs.com/docs/migrating_to_8.html
- MongoDB Node.js driver release notes — https://www.mongodb.com/docs/drivers/node/current/reference/release-notes/
- MongoDB driver compatibility tables — https://www.mongodb.com/docs/drivers/compatibility/
- InfoQ: MongoDB 8.0 performance — https://www.infoq.com/news/2024/10/mongodb-80-performances/
- BigDATAwire: MongoDB 8.0 release — https://www.bigdatawire.com/2024/10/04/mongodb-8-0-release-raises-the-bar-for-database-performance/
- SD Times: MongoDB 8.0 performance — https://sdtimes.com/data/mongodb-8-0-offers-significant-performance-improvements-to-read-throughput-bulk-writes-and-more/
- Mydbops: What's New in MongoDB 8.0 — https://www.mydbops.com/blog/unveiling-expected-features-in-mongodb-8-0

---

_File: `docs/tasks/tasks_03_mongo_search/02_mongodb_version_history.md`_
