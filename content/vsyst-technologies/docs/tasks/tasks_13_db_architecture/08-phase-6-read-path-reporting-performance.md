# Phase 6 — Read-path & reporting performance

**Outcome:** Query latency earned the honest way: evidence-driven indexes (add *and* drop), the `countDocuments`-per-page tax removed (D8), `lean()`/projection on hot lists, statement reads that stay fast at year scale, heavy exports off the OLTP path, and an archival decision. Every change is measured against the Phase-1 endpoint baseline.

**Effort:** 2–4 dev-days, incremental — safe to interleave with other phases once Phase-1 evidence exists (ledger-dependent items marked ⛓4).

## 6.1 Evidence-driven index program

Inputs: Phase-1 `$indexStats` dump, Profiler COLLSCAN/`docsExamined≫nReturned` offenders, Performance Advisor suggestions.

- [ ] **Drop** indexes with zero `accesses.ops` over a full business cycle (each unused index taxes every write; the census table lists candidates).
- [ ] **Add** — validate each against a Profiler-captured real query first; expected candidates from code reading:
  - `invs {dealer_id:1, cust_id:1, inv_status:1, inv_dt:-1}` — unpaid/aging scans currently filter `inv_status` after the date index.
  - `voc_msts {dealer_id:1, cust_id:1, voc_type:1, eff_dt:-1}` — TCS/TDS pipelines match on `voc_type`+`eff_dt` (retires with ⛓4 ledger reads; skip if Phase 4 lands first).
  - `voc_msts {ref_voc_id:1}` partial — AdvDep adjustment lookups (may already exist from Phase 2 §2.4).
  - `order_msts` covering index for `pendingPOlist`'s `$match`+`$lookup` keys (`api_v3/services/dealer_custs.js:355-398`).
  - `fin_txns` — created with its indexes in Phase 4; verify `$indexStats` confirms usage patterns.
- [ ] Re-run the baseline endpoint timings; record deltas in the findings doc.

## 6.2 Kill the per-page count tax (D8)

`helpers/advancedResults.js:88,196` runs `countDocuments(queryStr)` on every list call.

- [ ] Unfiltered lists → `estimatedDocumentCount()` (metadata read, ~free).
- [ ] Filtered lists → cache the count per `{co_id, collection, filter-hash}` for 30–60s in the existing LRU (list pages 1..N reuse it), or return `hasMore` (fetch `limit+1`) where clients only need next-page existence — audit which of the app's infinite-scroll screens actually render totals before choosing per endpoint.
- [ ] Add the choice as an option flag in `advancedResults` so it rolls out per-route, not big-bang. (`helpers/` change — governance exception Q7, or an `api_v3` wrapper.)

## 6.3 `lean()` + projection sweep on hot GETs

- [ ] Top-10 read endpoints from Phase-1: add `.lean()` (skips hydration; these are serialize-and-return paths) and explicit field projections (drop embedded arrays not used by list screens — e.g. order/SO `products[]` in list views if the apps only render summaries — verify against app/web usage first).
- [ ] Confirm no code depends on Mongoose doc methods on those paths (tests catch it — this is why the tasks_12 fixture contract exists).

## 6.4 Statement & report scale (⛓4)

- [ ] Year-statement and `allRelationCurrBal` endpoints: verify single-pass ledger reads post-Phase-4; for the "all relations" superadmin views add pagination or a `$merge`-maintained summary collection (`stmt_month_cache`) refreshed by the nightly reconciler run — *only if* baseline shows these endpoints hot; do not pre-build.
- [ ] Month-close emails/exports batched off-peak via the existing crontab pattern.

## 6.5 Heavy reads off the OLTP path

- [ ] Excel/PDF/email statement generation + TCS/TDS reports: `readPreference: "secondaryPreferred"` on those service reads (session-level option), keeping OLTP on primary. Balance-after-posting endpoints explicitly stay primary (read-your-writes).
- [ ] Puppeteer PDF generation: cap concurrency (simple in-process semaphore) so bursts can't stack Chromium instances against the 500M PM2 restart limit — an availability guard that also protects DB connection churn from restart loops.
- [ ] If §5.4 added an analytics node: switch these reads to the analytics `readPreference` tag instead.

## 6.6 Archival decision (money never TTLs; it may *move*)

- [ ] With census + ledger in hand decide: leave closed FYs in place (default — `month_crdrs`/`fy` keys already keep hot queries off them; likely fine for years at khata volumes) vs Atlas **Online Archive** on `fin_txns`/`invs` by `posting_dt`/`inv_dt` older than N FYs vs an `oms_archive` namespace.
- [ ] Whatever the choice: statements for archived FYs must still be producible (Online Archive keeps them queryable via federated endpoint — slower is acceptable for old-FY exports). Record the decision + retention statement (statutory: GST records ≥ 6 years — confirm with the accountant before archiving anything out of the primary cluster).

## Phase 6 checklist

- [ ] Unused indexes dropped; new indexes added only with Profiler-verified query shapes; write-latency unharmed
- [ ] `countDocuments` strategy live per route (estimated / cached / hasMore); list p95 delta recorded
- [ ] `lean()` + projections on top-10 GETs; fixture-contract tests green
- [ ] Statement/report endpoints verified single-pass on ledger; summary cache only if evidence demanded
- [ ] Exports/reports on secondary reads; PDF concurrency capped; OLTP stays primary
- [ ] Archival decision recorded with statutory retention confirmed
- [ ] Endpoint baseline re-measured; SLO table updated in `phase-1-findings.md`
