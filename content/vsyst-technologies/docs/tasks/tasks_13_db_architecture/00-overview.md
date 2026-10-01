# Plan: Financial Data Structure + Database Split + DB/Network Performance

> **Repo under change:** `dzzlo_oms_api` (Express 5, Mongoose 9, MongoDB Atlas M10). Read-path consumers `dzzlo_oms_app` and `dip-web` are unaffected until Phase 4/6 flags flip (API contracts stay stable throughout).
> **Status:** 🟡 **2026-10-01:** no phase has been executed as written. Outside this plan, API PR #36 (ledger hardening, merged 2026-08-31) and PR #41 (IST month and year windows, merged 2026-09-10) reworked the month-bucket write path — D2 and D12 are mitigated — and the v4 work (PRs #39–#44, merged 2026-09-30) made the pool explicit and built v4-only pieces of Phases 1 and 6; the open questions are still PENDING. — _was:_ Plan drafted 2026-07-02 from a full code audit of the live system. The `## Open questions` are **PENDING**; every phase assumes the provisional default recorded there. This overview is the source of truth — update it and the affected phase file when an answer changes a default.
> **Companion guides:** `01-decision-financial-db.md` (should money move to SQL? → no, and why), `02-target-architecture.md` (the target topology this plan builds).

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). No phase has run as written: of the 12 defects none is fixed, 5 are mitigated (🟡 D2, D4, D8, D11, D12 — mostly by API PR #36 and the v4 work), 6 are still open (⬜ D1, D3, D5, D7, D9, D10) and D6 waits on the deferred API-5 (⏸); of the 7 phases, 5 are 🟡 through overlapping work (1, 2, 3, 6, 7) and 2 are ⬜ (4, 5). Four new task rows (X-PERF-3 ⏸, T13-N1, T13-N2, T13-N3); the open questions stay PENDING. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item | Status | What exists now (evidence) | What is left / next step |
| --- | --- | --- | --- |
| [01 Decision guide](./01-decision-financial-db.md) | ✅ | The decision holds: money stayed in MongoDB (no SQL driver in either repo); integer paise is now used on the v4 read side (api:`api_v4/lib/money.js`), the shape of §4's policy | Review the §5 triggers when Phase 7 closes; T13-N1 (one money rule) |
| [02 Target architecture](./02-target-architecture.md) | ⬜ | Not built: two mongoose connections (api:`helpers/db_conn.js:50-64`), no namespaces (`useDb` absent), no `fin_txns`; the pool is explicit but not at §6's values (`:44-47`) | Built by Phases 2–6 |
| [Phase 1 — baseline](./03-phase-1-baseline-measurement.md) | 🟡 | API-0 measured the two v4 screens on a local scale seed (api:`scripts/perf/*`, `yarn perf:baseline`, api:`docs/v4-performance.md`) | The production census, profiler baseline, log share, RTT, integrity scan and findings doc |
| [Phase 2 — write path](./04-phase-2-financial-write-path-hardening.md) | 🟡 | One idempotent recompute-from-source month rebuild replaced the read-modify-write poster (api:`api_v3/services/ledger_window.js:439-481`, PR #36); duplicate month rows no longer inflate balances; a paise module exists on the v4 read side only (api:`api_v4/lib/money.js`) | Transactions, `post_seq`, the unique `month_crdrs` index, validators, a replica-set harness, the reconciler script, concurrency tests; T13-N1, T13-N3 |
| [Phase 3 — ops & network](./05-phase-3-ops-isolation-network-quick-wins.md) | 🟡 | Explicit pool on both connections (`maxPoolSize` 75, `waitQueueTimeoutMS` 3000 — api:`helpers/db_conn.js:44-47`); `/healthcheck` outside logging (api:`dzzlo_oms.js:69,73`) | Log diet and TTLs (API-5, ⏸ deferred by the user 2026-09-21 — X-PERF-2 in tasks_01), `w:1`, compression, DIP indexes, the cache policy; network path ❔ |
| [Phase 4 — `fin_txns`](./06-phase-4-fin-txns-posting-ledger.md) | ⬜ | Nothing (`git grep fin_txns` → none) | All of it, including the v4 read models (T13-N2) |
| [Phase 5 — namespaces](./07-phase-5-namespace-split-topology.md) | ⬜ | Nothing (no `useDb`; one database per URI — api:`.env.example:10-14`) | All of it |
| [Phase 6 — read path](./08-phase-6-read-path-reporting-performance.md) | 🟡 | Four named indexes for the v4 screens (API-1), `.select()` + `.lean()` + `maxTimeMS` on every v4 read, no counts in v4 (api:`api_v4/lib/cursor.js`); whether the indexes exist on Atlas is ❔ (X-REL-2 in tasks_01) | The v3 count tax, index drops, secondary reads, a PDF cap, archival; X-PERF-3 ⏸ |
| [Phase 7 — rollout](./09-phase-7-rollout-verification-guardrails.md) | 🟡 | A manual canary (api:`docs/runbook.md:121-156`), a release gate without a reconcile step (api:`scripts/release_gate.sh`), `docs/ARCHITECTURE.md`'s version map corrected (`4409d4b`) | Reconciliation gating, money-path rules in `AI.md`; alerts ❔ |

## The two questions this plan answers

**Q1 — "Should we use a structured DB for financial transactions for better querying?"**
**Answer: yes to *structured*, no to *a second database engine*.** Everything "structured" buys — enforced schema, ACID postings, exact money arithmetic, clean queryable ledger — is available inside MongoDB and is currently simply *unused*: the transactions helper exists but no money flow uses it, `$jsonSchema` validation is absent, amounts are floats, and the "ledger" is two collections (`invs` + `voc_msts`) merged in JS at read time. Moving money to PostgreSQL would turn every money flow (invoice creation touches `so_msts` + `invs` + `month_crdrs`; voucher approval touches `voc_msts` + `month_crdrs` + `dealer_custs`) into a cross-engine distributed transaction — strictly worse. Full argument, scorecard, and the explicit triggers that would reopen this decision: `01-decision-financial-db.md`.

**Q2 — "How to split our database?"**
**By workload, as namespaces on the existing cluster** — `oms_core` (operations), `oms_fin` (money), `oms_ops` (logs/errors) — via `useDb()` on a single client so multi-document transactions still span core+fin. Plus the *real* performance split, which is not a split at all: get the request-log firehose out of the business working set (TTL + slim docs + `w:1`, destination decision in Phase 3). A second physical cluster is a Phase-5 decision gate driven by Phase-1 measurements, not an assumption. Full topology: `02-target-architecture.md`.

---

## Current state (audited 2026-07-02)

**Status (2026-10-01):** the financial model and "what's already good" still describe master, with moved line numbers — `checkMonthDRCR` is now api:`api_v3/services/dealer_custs.js:95` and delegates to `rebuildMonthBucket`, `dbpopulatemonthcrdrcollection` `:1667`, `persistAdvDep` api:`api_v3/services/voc_msts.js:243`. The defect table's new right-hand column gives each defect's state at master.

**Deployment:** 2× EC2 + ALB (canary pattern), PM2 fork mode, Atlas **M10** 3-node replica set (1500-conn limit), IP allowlist `0.0.0.0/0`, no VPC peering (flagged future in `docs/runbook.md`). No Redis, no queue/cron, ~~no CI~~ **2026-10-01:** CI since 2026-07-10 (`f31d1f6`, tests only). In-process LRU cache per instance (`helpers/cacheMiddleware.js` — 10-min TTL, **not shared across the 2 servers**).

**Financial model (single-entry khata):**

```
current balance = cust_bal[] FY opening (dealer_custs)
                + Σ cumulative (month_crdrs.drttl − crttl)
                − adv_dep (derived from AdvDep vouchers)

DEBIT side  = invs (inv_total_amt) + DEBIT vouchers
CREDIT side = CREDIT/SALE vouchers (posted only when pay_status=true)
```

**What's already good (do not rebuild):**
- Separate top-level collections for all transaction data; line items embedded sensibly.
- `month_crdrs` monthly rollups keep statement reads from scanning full history — this *is* a materialized-view pattern, kept.
- Self-healing reconcilers exist: `checkMonthDRCR` (`api_v3/services/dealer_custs.js:167`), batch `dbpopulatemonthcrdrcollection` (`:1785`), `persistAdvDep` (`api_v3/services/voc_msts.js:337`) — these become the *guardrails* of this plan instead of the safety net for races.
- Collision-free invoice numbering (`en_id_base33` from ObjectId, `api_v3/services/invs.js:37`).
- `runInTransaction` helper exists (`helpers/transactions.js`) — just unused for money.
- Reasonable compound indexes on `order_msts`/`so_msts`/`invs`/`voc_msts`.

**The defects this plan fixes (with file:line evidence):**

| # | Defect | Where | Fixed in | 2026-10-01 |
| --- | --- | --- | --- | --- |
| D1 | No money flow is transactional — crash mid `createInvNew` leaves ledger inconsistent until reconciled | `api_v3/services/invs.js:1120-1246`; `.session()` calls commented out in v2 | Phase 2 | ⬜ open — transactions only in `veh_reqs` (api:`api_v3/services/veh_reqs.js:249`); month buckets now self-heal (D2) |
| D2 | `updateCrDr` is read-modify-write (`findOne` → `findByIdAndUpdate`), no `$inc`, no lock — concurrent postings lose updates | `api_v3/services/voc_msts.js:256-301`, duplicated `api_v3/services/invs.js:1007-1050` | Phase 2 | 🟡 mitigated — each write rebuilds the month from source (api:`api_v3/services/ledger_window.js:439-481`, PR #36); a rebuild race self-heals (inferred) |
| D3 | TOCTOU on AdvDep drawdown (guard-read then write) and on order credit-limit check (sum-then-create) | `voc_msts.js:387-479` (`updateVocStatus`), `order_msts.js:786-799` | Phase 2 | ⬜ open — both guards still read, then write (api:`api_v3/services/voc_msts.js:342-354`, api:`api_v3/services/order_msts.js:826-843`) |
| D4 | Money is float `Number` with `.toFixed(2)` string→float round-trips; no Decimal128/integer-minor-unit anywhere | `models/invs.js:55-115`, `models/dealer_custs.js:9-14` setters | Phase 2 (helpers) + Phase 4 (root fix) | 🟡 v4 read side in integer paise (api:`api_v4/lib/money.js`); v3 storage still float (api:`models/invs.js:57-75`) |
| D5 | No schema enforcement: `pay_mode` free string, `Mixed` blobs, no `$jsonSchema` validators | `models/voc_msts.js:49-52`, `models/pay_trns.js` | Phase 2 | ⬜ open — no `$jsonSchema` anywhere; `pay_mode` a free string (api:`models/voc_msts.js:49-52`) |
| D6 | `logs` written on **every request**, unbounded, no TTL, embeds full user object, `w:majority` — shares cache/IOPS with money data. `errors`, `pay_trns` also unbounded | `helpers/middlewares.js:229-279`, `models/logs.js` | Phase 3 | ⏸ API-5 deferred 2026-09-21 — whole user doc per request, no TTL (api:`helpers/middlewares.js:250,261`); production-only since `ecdd3ae` |
| D7 | No TTL on `invites.expirationTime`; DIP collections (incl. high-write `meter_reads`) have **zero indexes** | `models/invites.js`, `models/dip_models/*` | Phase 3 | ⬜ open — no TTL on `invites` (api:`models/invites.js:14`); `models/dip_models/*` declare no index |
| D8 | Every list endpoint runs `countDocuments(queryStr)` per page | `helpers/advancedResults.js:88,196` | Phase 6 | 🟡 v4 never counts (api:`api_v4/lib/cursor.js:29-30`); v3 still counts per page (api:`helpers/advancedResults.js:88,196`) |
| D9 | Statement/"account" reads merge `invs` + `voc_msts` in JS per request; TCS/TDS reports re-aggregate raw collections | `dealer_custs.js:584-642`, `TCSTDS/index.js` | Phase 4 (ledger) + 6 | ⬜ open — merged in JS (api:`api_v3/services/dealer_custs.js:443-501`); v4 Customers adds a second fold (api:`api_v4/readmodels/customers.js:294-347`) |
| D10 | 10-min cached financial reads can be stale across the 2 instances (LRU busts locally only) | `helpers/cacheMiddleware.js` | Phase 3 | ⬜ open, narrower — statement and balance reads are not cached; one cached relation list carries money fields (api:`api_v3/routes/collections/cust_msts.js:94`) |
| D11 | No pool tuning, no wire compression, public internet path to Atlas | `helpers/db_conn.js` (no options), runbook | Phase 3 | 🟡 pool explicit (api:`helpers/db_conn.js:44-47`, API-3); no compression; network path ❔ |
| D12 | `month_crdrs` missing uniqueness on `{cust_id, dealer_id, month}` — duplicate rollup rows possible | `models/month_crdrs.js:17` | Phase 2 | 🟡 mitigated — reads take one row, each rebuild collapses duplicates (api:`api_v3/services/ledger_window.js:453-461`); unique index still absent |

---

## Target architecture (summary — full detail in `02-target-architecture.md`)

```
                        Atlas cluster "dzzlooms" (M10 → size per Phase-1 data)
                        ├── oms_core   users, cust/dealer_msts, dealer_custs, order/so_msts,
                        │              prod/rate/psocs, veh_*, dvr_msts, invites, counters, contact_us
                        ├── oms_fin    fin_txns (NEW posting ledger), invs, voc_msts,
                        │              month_crdrs (derived), pay_trns (dormant)
                        ├── oms_ops    logs (TTL 90d, slim, w:1), errors (TTL 180d)
                        └── Dip_web…   (existing DIP namespace, gains indexes)
   2× EC2 (PM2) ── one MongoClient, useDb() per namespace ── transactions span core+fin (same session)
   Network: VPC peering/private endpoint, compressors=zstd, explicit pool sizing
```

The one new collection that answers "better querying": **`fin_txns`** — an append-only, immutable, validated posting ledger (one row per financial event, DR/CR direction, integer-paise amount, source-document ref, idempotency key, FY/month keys). Statements, TCS/TDS, exports, and balances become single-collection indexed queries; `month_crdrs` and `adv_dep` become rebuild-from-ledger materializations. Existing `invs`/`voc_msts` stay as the business documents (invoice PDFs, approval workflow) — `fin_txns` is the *financial spine*.

---

## Phases

**Status (2026-10-01):** none executed as written — the state of each is in the roll-up above and in its own file.

| Phase | File | Outcome | Effort | Depends on |
| --- | --- | --- | --- | --- |
| 1 | `03-phase-1-baseline-measurement.md` | Numbers before knobs: collection census, Atlas profiler/metrics, log-write share, RTT, money-integrity scan; SLOs + go/no-go inputs for every later phase | 1–2 dev-days (+1 week passive metrics) | — |
| 2 | `04-phase-2-financial-write-path-hardening.md` | Every money flow atomic (`runInTransaction` + per-relation serialization), `$inc` rollups, integer-paise math helpers, `$jsonSchema` validators, uniqueness constraints, reconciler as scheduled guardrail | 3–5 dev-days | 1 |
| 3 | `05-phase-3-ops-isolation-network-quick-wins.md` | Log firehose tamed (slim+TTL+`w:1`), obvious indexes, wire compression, pool sizing, VPC peering, cache staleness policy | 1–2 dev-days | 1 (can run parallel to 2) |
| 4 | `06-phase-4-fin-txns-posting-ledger.md` | `fin_txns` live: dual-write inside Phase-2 transactions, backfill + reconciliation, statements/TCS-TDS/exports read the ledger behind a flag | 5–8 dev-days | 2 |
| 5 | `07-phase-5-namespace-split-topology.md` | Collections relocated to `oms_core`/`oms_fin`/`oms_ops` with near-zero-downtime cutover; per-namespace users/access; cluster-sizing decision executed | 2–4 dev-days | 4 (fin_txns is born in `oms_fin`) |
| 6 | `08-phase-6-read-path-reporting-performance.md` | Evidence-driven index program, `countDocuments` strategy, `lean()`/projection sweep, materialized statements, read-preference for heavy exports, archival decision | 2–4 dev-days | 1 (evidence), parts need 4 |
| 7 | `09-phase-7-rollout-verification-guardrails.md` | Canary rollout, reconciliation-gated cutovers, monitoring/alerts, docs corrected (ARCHITECTURE.md is stale), rollback playbooks | 1–2 dev-days | all |

Total ≈ **15–27 dev-days**, spread across releases; each phase lands independently and is valuable even if later phases are deferred. Firm ordering: 1 → 2 → 4 → 5. Phase 3 can run any time after 1. Phase 6 is incremental throughout. If you stop after Phase 3 you still get correctness + the biggest perf wins; Phase 4 is where "better querying" is delivered.

---

## Open questions — ⏳ PENDING (defaults in force until answered)

**Status (2026-10-01):** all ten still PENDING — no answer from the user in code or in the redesign's decision logs. Related facts since July: Q6 — the user confirmed an integer-paise rule for the v4 read models (2026-09-15/16, api:`api_v4/lib/money.js:1-6`), consistent with this default but not an answer for ledger storage; Q7 — additive `models/` changes have been approved case by case (the four v4 indexes `a09e28f`, the `user_prefs` model `d2639ee`) while api:`AI.md:85-90` still says `models/` stay unchanged; Q2 — the log diet and TTL (API-5) were deferred by the user on 2026-09-21.

1. **Data volumes** — run the Phase-1 census before sizing anything. *Default: assume low-mid single-digit GB and M10 headroom; no spend until census says otherwise.*
2. **Log retention & purpose** — are `logs` ever used for audit/support lookups older than ~3 months? Do any product features read them? *Default: TTL 90d on `logs`, 180d on `errors`; slim documents; stay in Mongo (option a) until Phase-1 shows contention.*
3. **Budget appetite** — M20 upgrade, analytics node, or second ops cluster are all money. *Default: zero new Atlas spend in Phases 1–4; Phase 5 presents a costed decision table.*
4. **Payment gateway roadmap** — Paytm code is dead in `api_v1`; is online collection planned (esp. with tasks_11 Partner API)? *Default: `fin_txns` schema reserves `src.type: "GATEWAY"` and an idempotency key so a gateway posts cleanly later; no gateway work now.*
5. **BI/SQL consumers** — will accountants/CA firms ever need SQL access or is Excel/PDF export the permanent interface? *Default: exports remain the interface; if SQL is demanded, Atlas SQL/Charts on a secondary — still no engine migration.*
6. **Precision policy** — OK to keep the API boundary in rupees (2-dp JSON numbers) while all *new* internal arithmetic and `fin_txns` storage use integer paise? Legacy fields untouched. *Default: yes (see `01-decision-financial-db.md` §4).*
7. **Governance** — `AI.md` freezes `models/` and `helpers/`. This plan needs *additive* schema changes (new `fin_txns` model, new indexes/validators, TTL). Amend the rule to "additive schema changes via reviewed PR allowed"? *Default: yes for additive changes; zero edits that repurpose existing fields; DB-side `collMod`/`createIndex` used where tests don't need the constraint.*
8. **Concurrency reality** — how often do two users post money to the *same* dealer↔customer relation simultaneously? Affects how hard we lean on per-relation serialization. *Default: implement it anyway (cheap, ~10 lines inside the transaction), because reconcilers currently mask lost updates.*
9. **Downtime tolerance** — Phase-5 namespace moves want a short per-collection write-freeze (minutes, off-peak). Acceptable, or must it be fully online (dual-read window)? *Default: off-peak freeze per collection group.*
10. **DIP trajectory** — is the DIP product growing (meter_reads volume)? *Default: give it indexes in Phase 3, keep its namespace where it is; revisit placement only if census shows real volume.*

---

## Constraints

**Status (2026-10-01):** the frozen-contracts constraint held — v4 is additive at `/api/v4` (redesign D1); the test harness is still a standalone `MongoMemoryServer` (api:`test/database.js:5,67`); the release gate has no reconciliation step yet (api:`scripts/release_gate.sh`).

- **API contracts frozen**: `/api/v2` and `/api/v3` request/response shapes must not change — app versions 1.68+ are in the field. All reading-path changes are server-internal or feature-flagged.
- **Local-data-only tests** (tasks_12 rule): everything here must be provable in the `mongodb-memory-server` harness. Phase 2 upgrades the harness to `MongoMemoryReplSet` because transactions require a replica set — coordinate with tasks_12 Phase 1.
- **No new infra until measured**: no Redis, no queue, no second cluster, no sharding unless Phase-1/Phase-5 evidence demands it. (Sharding is explicitly out: M10-class working sets are nowhere near it; the escalation path is M10 → M20 → analytics node, in that order.)
- **Reconciliation is the release gate**: every phase that touches money ends with `fin_txns`/`month_crdrs`/statement parity checks reporting **zero drift** before and after cutover (Phase 7 wires this into the tasks_12 release gate).
- Vault convention: this folder mirrors `tasks_11`/`tasks_12` format (no frontmatter, `**Outcome:**`/`**Effort:**` lines, `## N.M` subsections, phase checklists).

## New tasks — from the app v2 / API v4 review (2026-10-01)

Canonical IDs (`X-…`) come from the team registry; `T13-N…` are this folder's own. The linked doc owns the row and repeats it. Tasks other folders own are only referenced: X-PERF-2, X-REL-2 (tasks_01), X-V4-2 (tasks_02).

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-PERF-3 | ⏸ [08](./08-phase-6-read-path-reporting-performance.md) — API-9: stored per-order totals or per-day rollups for long Daily Summary windows — deferred by the user ("Not now … Reopen only with numbers") | vault `oms_app/screen-redesign/08-v2-optimisation-plan.md:320,322` (API-5…9 deferred 2026-09-21). After API-1 the five-year Sales window reads in 11.7 ms p95 on the scale seed (api:`docs/v4-performance.md:270-276`); API-9's own note warns that a second write path is "the class of bug `month_crdrs` has already produced twice" | API | L | production numbers (Phase 1) |
| T13-N1 | 🆕 [04](./04-phase-2-financial-write-path-hardening.md) — One money rule: before §2.2 adds `api_v3/services/money.js`, decide a single home for the integer-paise rule the v4 read models already use (an additive `helpers/` file needs the user's approval), and settle the open Daily Summary O-6 decision (amount-entered lines) first | The v4 rule rounds quantity to the millilitre and each line half-up to the paisa (api:`api_v4/lib/money.js:1-22,58-59`), confirmed by the user 2026-09-15/16; v3 rounds each line with float `toFixed(2)` (api:`models/invs.js:57-75`) — a second paise module would recreate the two-rule problem screen spec 02 O-3 found | API | S | O-6 decision (screen spec 02); Q7 |
| T13-N2 | 🆕 [06](./06-phase-4-fin-txns-posting-ledger.md) — Put the v4 read models on this plan's read-path list: the Customers read model reads `month_crdrs` directly and keeps its own FY fold, opening balance and outstanding-order aggregates, so Phase 2's unique-index clean-up, Phase 4's read flip and Phase 5's move of `month_crdrs` to `oms_fin` must include it and its parity tests | api:`api_v4/readmodels/customers.js:270-347` (`ledgerByCust`, `$first` per IST month), `:476-570` (outstanding orders, opening balance); parity suites in api:`test/api_v4/screens/customers.test.js` | API | S | X-V4-2 (tasks_02) |
| T13-N3 | 🆕 [04](./04-phase-2-financial-write-path-hardening.md) — Make PO and SO numbering atomic: take the next number with `findOneAndUpdate({$inc})` before the insert, and add unique indexes on (`cust_id`, `order_no`) and (`dealer_id`, `slip_no`) after a duplicate check on existing data | `order_no` is the customer's `cust_podgt` + 1 — read, incremented in JS and written back with `$set` after the insert (api:`api_v3/services/order_msts.js:768-786,843-847`); `slip_no` works the same way on `dealer_sodgt` (api:`api_v3/services/so_msts.js:43-58`); neither number has a unique index (api:`models/order_msts.js:31`, api:`models/so_msts.js:34`), so two concurrent orders of one customer, or SOs of one dealer, can take the same number. Invoice numbers are collision-free (ObjectId-derived, api:`api_v3/services/invs.js:60,322,483,542`) | API | S | duplicate scan (§1.6 in Phase 1); Q7 |
