# Phase 1 — Baseline & measurement

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Not done as written: no production census, profiler baseline, log share, RTT or integrity scan is in the repos. Partial overlap: API-0 (api:`scripts/perf/*`, `yarn perf:baseline`, api:`docs/v4-performance.md`) measured the two v4 screens on a local scale seed. Of 7 sections: 1 🟡 (§1.5), 5 ⬜, 1 ❔ (§1.1). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Outcome:** Hard numbers before any knob is turned: collection census, cluster metrics over one normal week, log-firehose share, network RTT, and a money-integrity scan. Ends with a findings doc that sets SLOs and pre-answers the go/no-go inputs used by Phases 3, 5, and 6.

**Effort:** 1–2 dev-days active work, plus ~1 week of passive metric collection.

## 1.1 Turn on the telemetry (Atlas console, 30 min)

**Status (2026-10-01):** ❔ Atlas console settings (profiler, advisor, alerts) cannot be seen from the repos; the runbook names one CloudWatch alarm (api:`docs/runbook.md:38`).

- [ ] Enable **Query Profiler** (Atlas → cluster → Profiler) and **Performance Advisor**; note the slow-query threshold (default 100ms is fine).
- [ ] Open **Metrics** and screenshot/record current steady state: cache activity (read into / dirty), IOPS, CPU, connections, oplog GB/hour, disk usage.
- [ ] Set alerts if absent: connections > 500, cache dirty sustained, disk > 70%, replication lag.
- [ ] Record cluster region and confirm the EC2 region from the runbook — same region? (Feeds §1.4.)

## 1.2 Collection census script

**Status (2026-10-01):** ⬜ to do — no `scripts/db_census.js` (`scripts/` holds `perf/*`, `release_gate.sh`, `check_fixtures_fresh.js` and two data scripts). API-0 records `explain` plans on a local seed, not production `$indexStats`.

New `scripts/db_census.js` (read-only; `scripts/` is outside the frozen dirs). For each collection in the OMS + DIP namespaces emit: document count, `avgObjSize`, `storageSize`, `totalIndexSize`, index list with `$indexStats` usage counters, and oldest/newest `createdAt`. Output a markdown table committed to this folder as `phase-1-census-<date>.md`.

```js
// core of it
const stats = await db.collection(name).aggregate([{ $collStats: { storageStats: {} } }]).next();
const usage = await db.collection(name).aggregate([{ $indexStats: {} }]).toArray();
```

- [ ] Run against production (read-only user) off-peak; commit the table.
- [ ] Flag in the table: the 3 largest collections, any index with `accesses.ops == 0` (drop candidates for Phase 6), collections with no index beyond `_id` (expected: the four DIP ones — D7).

## 1.3 Quantify the log firehose (D6 sizing)

**Status (2026-10-01):** ⬜ to do — not measured; API-0 left its `logs` finding unmeasured, "deferred with API-5" (api:`docs/v4-performance.md:146`).

- [ ] From the census: `logs` count, avg doc size, total size vs total data size — the "% of the database that is request logs" number.
- [ ] Write rate: `db.logs.countDocuments({createdAt: {$gte: <24h ago>}})` → logs/day; × avgObjSize → bytes/day; compare to oplog GB/hour to get the share of *all* writes that are telemetry.
- [ ] Grep one recent `logs` doc: confirm it embeds the full `user` object + `appInfo` (`helpers/middlewares.js:229-279`) and measure how much of the doc that is — sets the Phase-3 diet target.
- [ ] Decision input for Q2: does anyone query `logs` older than 90 days? (Ask support/ops; check `logs` read patterns in Profiler.)

## 1.4 Network RTT & path

**Status (2026-10-01):** ⬜ to do — no RTT record; API-0 ran on loopback by design (api:`scripts/perf/safety.js:2-36` refuses any non-local host). The driver settings to record have changed: pool 75 with a 3 s wait (api:`helpers/db_conn.js:44-47`).

- [ ] From each EC2 instance: `mongosh <URI> --eval 'for(let i=0;i<20;i++){const t=Date.now();db.adminCommand({ping:1});print(Date.now()-t)}'` → record p50/p95 RTT.
- [ ] Confirm whether traffic rides the public internet (it does today — allowlist `0.0.0.0/0`, no peering per runbook). Record as the Phase-3 §3.6 justification.
- [ ] Record current driver settings for the before/after: no compressors, default pool (100), `w:majority` everywhere.

## 1.5 Endpoint latency baseline

**Status (2026-10-01):** 🟡 for the two v4 screens only, on a local scale seed (one dealer, 2,000 relations, 300,000 SOs): Customers 1,525 → 134 ms median, Daily Summary ≤ 3.1 ms p95 at its preset windows (api:`docs/v4-performance.md:247-276`) — "read the absolute times as a floor" (`:32`). No production p50/p95/p99 for the v3 statement and report endpoints this section names.

- [ ] From ALB/CloudWatch (or the `logs` collection if it stores response times): p50/p95/p99 for the top-10 endpoints by volume, plus specifically: statement endpoints (`/app/year`, `/app/month`, `/app/currbal`, `/app/allRelationCurrBal`), TCS/TDS reports, invoice list, order list. These are the endpoints Phases 4/6 must visibly improve.
- [ ] Record Excel/PDF export timings if available (Puppeteer memory pressure interacts with the 500M PM2 restart limit — note only).

## 1.6 Money-integrity scan (feeds Phases 2 & 4)

**Status (2026-10-01):** ⬜ to do — no `scripts/fin_integrity_scan.js`. PR #36's tests pin rebuild, duplicate and roll-forward behaviour on seeded data (api:`test/api_v3/collections/dealer_custs/month_rebuild.test.js`, `duplicate_buckets.test.js`, `year_rollforward.test.js`), not production data. Add a duplicate PO / SO number count to the scan (T13-N3).

New `scripts/fin_integrity_scan.js` (read-only, sessionless):

- [ ] **Rollup drift**: for every `dealer_custs` relation, recompute each month's dr/cr from `invs` + approved `voc_msts` (same math as `checkMonthDRCR`, `api_v3/services/dealer_custs.js:167-202`) and diff against stored `month_crdrs`. Report count and max |Δ| — this is the D2 lost-update damage estimate.
- [ ] **Duplicate rollups**: `month_crdrs` groups with >1 doc per `{cust_id, dealer_id, month}` (D12 pre-check — must be 0 before the unique index lands).
- [ ] **AdvDep**: recompute `advDepBalance` per relation vs stored `dealer_custs.adv_dep`; list negatives-clamped cases; count AdvDep vouchers with >1 adjustment referencing them (D3 damage).
- [ ] **Precision anomalies**: money fields failing `Math.abs(v*100 - Math.round(v*100)) > 1e-6` (sub-paise floats — D4 evidence); nulls/negatives where business rules forbid them.
- [ ] **Orphans**: `voc_msts.inv_id`/`invs_adj[]`/`ref_voc_id` pointing at missing docs; `invs` without an existing relation.
- [ ] Commit results as `phase-1-integrity-<date>.md`. Every non-zero count gets a one-line disposition: *fix in Phase-2 backdrop cleanup* / *explainable, accept*.

## 1.7 Findings doc, SLOs, go/no-go table

**Status (2026-10-01):** ⬜ to do — no findings doc. API-0's pass mark, p95 < 300 ms server time at production size (api:`docs/v4-performance.md:251`), matches this section's list SLO but covers only the v4 screens.

Commit `phase-1-findings.md` in this folder:

- [ ] SLOs (proposed, adjust to measured reality): p95 ≤ 300ms for list endpoints, ≤ 500ms for statement month-view, zero reconciliation drift, `logs` ≤ 15% of cluster writes after Phase 3.
- [ ] Go/no-go inputs filled: log-firehose share (→ Phase 3 destination option a/b/c), working-set vs M10 RAM (→ Phase 5 sizing table), RTT + region (→ peering priority), drift/duplicate counts (→ Phase 2 cleanup scope), census sizes (→ Q1, Q10).
- [ ] Update `00-overview.md` open questions with any now-answered defaults.

## Phase 1 checklist

**Status (2026-10-01):** 0 of 7 done (a mark on each item); none flipped.

- [ ] Profiler + Performance Advisor on; alerts set; steady-state metrics recorded — **2026-10-01:** ❔ Atlas console
- [ ] `scripts/db_census.js` committed; census table in vault — **2026-10-01:** ⬜ no census script
- [ ] Log firehose quantified (docs/day, bytes/day, % of writes, % of data) — **2026-10-01:** ⬜ not measured
- [ ] RTT measured from both EC2 instances; region parity confirmed/refuted — **2026-10-01:** ⬜ no RTT record
- [ ] Endpoint latency baseline recorded (incl. all statement/report endpoints) — **2026-10-01:** 🟡 v4 screens only, local seed (`docs/v4-performance.md`)
- [ ] `scripts/fin_integrity_scan.js` committed; drift/duplicate/precision/orphan counts recorded with dispositions — **2026-10-01:** ⬜ no scan script
- [ ] `phase-1-findings.md` committed: SLOs + go/no-go inputs; overview defaults updated — **2026-10-01:** ⬜ no findings doc
