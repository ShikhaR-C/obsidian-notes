# Phase 6 — Read-path & reporting performance

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Partly done for the v4 read paths only: four named indexes for the two v4 screens (API-1), `.select()` + `.lean()` + `maxTimeMS` on every v4 read, and no counts in v4 — nothing yet for the v3 lists, statements, exports or archival. Of 6 sections: 3 🟡 (§6.1–6.3), 3 ⬜ (§6.4–6.6); API-9's stored rollups are deferred (X-PERF-3, owned here — row at the end). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Outcome:** Query latency earned the honest way: evidence-driven indexes (add *and* drop), the `countDocuments`-per-page tax removed (D8), `lean()`/projection on hot lists, statement reads that stay fast at year scale, heavy exports off the OLTP path, and an archival decision. Every change is measured against the Phase-1 endpoint baseline.

**Effort:** 2–4 dev-days, incremental — safe to interleave with other phases once Phase-1 evidence exists (ledger-dependent items marked ⛓4).

## 6.1 Evidence-driven index program

**Status (2026-10-01):** 🟡 four indexes were added from measured plans, not Profiler captures — api:`models/so_msts.js:63-66`, `models/order_msts.js:82-85`, `models/month_crdrs.js:24-27`, `models/prod_msts.js:38-41` (numbers in api:`docs/v4-performance.md:178-293`); a fifth was measured and left out (api:`models/order_msts.js:86-89`) and another, `so_msts {dealer_id, inv_id, gst_inv_id}`, is an open call (X-PERF-2 in tasks_01); whether they exist on Atlas is unverifiable (X-REL-2 in tasks_01). No drops; the v3 candidates listed are ⬜ (no `ref_voc_id` index — api:`models/voc_msts.js:83-85`). The `pendingPOlist` covering index is moot for v4 (Customers stopped calling it — api:`api_v4/readmodels/customers.js:512-546`), but `pendingPOlist` still serves v3 (api:`api_v3/services/dealer_custs.js:205,684`).

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

**Status (2026-10-01):** 🟡 v4 never counts (api:`api_v4/lib/cursor.js:29-30`); v3's per-page `countDocuments` is unchanged (api:`helpers/advancedResults.js:88,196`), and `estimatedDocumentCount` is used nowhere.

`helpers/advancedResults.js:88,196` runs `countDocuments(queryStr)` on every list call.

- [ ] Unfiltered lists → `estimatedDocumentCount()` (metadata read, ~free).
- [ ] Filtered lists → cache the count per `{co_id, collection, filter-hash}` for 30–60s in the existing LRU (list pages 1..N reuse it), or return `hasMore` (fetch `limit+1`) where clients only need next-page existence — audit which of the app's infinite-scroll screens actually render totals before choosing per endpoint.
- [ ] Add the choice as an option flag in `advancedResults` so it rolls out per-route, not big-bang. (`helpers/` change — governance exception Q7, or an `api_v3` wrapper.)

## 6.3 `lean()` + projection sweep on hot GETs

**Status (2026-10-01):** 🟡 every v4 read is `.select()` + `.lean()` + `maxTimeMS` (api:`api_v4/readmodels/customers.js:655-716`, api:`api_v4/lib/limits.js:23-42`); the v3 top-10 sweep belongs with tasks_01's projection audit (doc 09) — see there.

- [ ] Top-10 read endpoints from Phase-1: add `.lean()` (skips hydration; these are serialize-and-return paths) and explicit field projections (drop embedded arrays not used by list screens — e.g. order/SO `products[]` in list views if the apps only render summaries — verify against app/web usage first).
- [ ] Confirm no code depends on Mongoose doc methods on those paths (tests catch it — this is why the tasks_12 fixture contract exists).

## 6.4 Statement & report scale (⛓4)

**Status (2026-10-01):** ⬜ to do (⛓4) — no summary collection; API-9's stored rollups are deferred (X-PERF-3).

- [ ] Year-statement and `allRelationCurrBal` endpoints: verify single-pass ledger reads post-Phase-4; for the "all relations" superadmin views add pagination or a `$merge`-maintained summary collection (`stmt_month_cache`) refreshed by the nightly reconciler run — *only if* baseline shows these endpoints hot; do not pre-build.
- [ ] Month-close emails/exports batched off-peak via the existing crontab pattern.

## 6.5 Heavy reads off the OLTP path

**Status (2026-10-01):** ⬜ to do — no `readPreference` and no PDF concurrency cap in the code (grep → none).

- [ ] Excel/PDF/email statement generation + TCS/TDS reports: `readPreference: "secondaryPreferred"` on those service reads (session-level option), keeping OLTP on primary. Balance-after-posting endpoints explicitly stay primary (read-your-writes).
- [ ] Puppeteer PDF generation: cap concurrency (simple in-process semaphore) so bursts can't stack Chromium instances against the 500M PM2 restart limit — an availability guard that also protects DB connection churn from restart loops.
- [ ] If §5.4 added an analytics node: switch these reads to the analytics `readPreference` tag instead.

## 6.6 Archival decision (money never TTLs; it may *move*)

**Status (2026-10-01):** ⬜ to do — no archival decision recorded.

- [ ] With census + ledger in hand decide: leave closed FYs in place (default — `month_crdrs`/`fy` keys already keep hot queries off them; likely fine for years at khata volumes) vs Atlas **Online Archive** on `fin_txns`/`invs` by `posting_dt`/`inv_dt` older than N FYs vs an `oms_archive` namespace.
- [ ] Whatever the choice: statements for archived FYs must still be producible (Online Archive keeps them queryable via federated endpoint — slower is acceptable for old-FY exports). Record the decision + retention statement (statutory: GST records ≥ 6 years — confirm with the accountant before archiving anything out of the primary cluster).

## Phase 6 checklist

**Status (2026-10-01):** 0 of 7 done, four partly (a mark on each item); none flipped.

- [ ] Unused indexes dropped; new indexes added only with Profiler-verified query shapes; write-latency unharmed — **2026-10-01:** 🟡 four v4 indexes added from measured plans; no drops
- [ ] `countDocuments` strategy live per route (estimated / cached / hasMore); list p95 delta recorded — **2026-10-01:** 🟡 v4 only; v3 unchanged
- [ ] `lean()` + projections on top-10 GETs; fixture-contract tests green — **2026-10-01:** 🟡 v4 reads only; the v3 sweep sits with tasks_01 doc 09
- [ ] Statement/report endpoints verified single-pass on ledger; summary cache only if evidence demanded — **2026-10-01:** ⬜ waits on Phase 4
- [ ] Exports/reports on secondary reads; PDF concurrency capped; OLTP stays primary — **2026-10-01:** ⬜ none
- [ ] Archival decision recorded with statutory retention confirmed — **2026-10-01:** ⬜ none
- [ ] Endpoint baseline re-measured; SLO table updated in `phase-1-findings.md` — **2026-10-01:** 🟡 v4 screens re-measured on a local seed (`docs/v4-performance.md:178-293`)

## New tasks — from the app v2 / API v4 review (2026-10-01)

Rows owned by this doc; the folder's full table is in [00-overview.md](./00-overview.md).

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-PERF-3 | ⏸ API-9: stored per-order totals or per-day rollups for long Daily Summary windows — deferred by the user ("Not now … Reopen only with numbers") | vault `oms_app/screen-redesign/08-v2-optimisation-plan.md:320,322` (API-5…9 deferred 2026-09-21). After API-1 the five-year Sales window reads in 11.7 ms p95 on the scale seed (api:`docs/v4-performance.md:270-276`); API-9's own note warns that a second write path is "the class of bug `month_crdrs` has already produced twice" | API | L | production numbers (Phase 1) |
