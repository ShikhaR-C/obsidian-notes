# Plan: Financial Data Structure + Database Split + DB/Network Performance

> **Repo under change:** `dzzlo_oms_api` (Express 5, Mongoose 9, MongoDB Atlas M10). Read-path consumers `dzzlo_oms_app` and `dip-web` are unaffected until Phase 4/6 flags flip (API contracts stay stable throughout).
> **Status:** Plan drafted 2026-07-02 from a full code audit of the live system. The `## Open questions` are **PENDING**; every phase assumes the provisional default recorded there. This overview is the source of truth — update it and the affected phase file when an answer changes a default.
> **Companion guides:** `01-decision-financial-db.md` (should money move to SQL? → no, and why), `02-target-architecture.md` (the target topology this plan builds).

## The two questions this plan answers

**Q1 — "Should we use a structured DB for financial transactions for better querying?"**
**Answer: yes to *structured*, no to *a second database engine*.** Everything "structured" buys — enforced schema, ACID postings, exact money arithmetic, clean queryable ledger — is available inside MongoDB and is currently simply *unused*: the transactions helper exists but no money flow uses it, `$jsonSchema` validation is absent, amounts are floats, and the "ledger" is two collections (`invs` + `voc_msts`) merged in JS at read time. Moving money to PostgreSQL would turn every money flow (invoice creation touches `so_msts` + `invs` + `month_crdrs`; voucher approval touches `voc_msts` + `month_crdrs` + `dealer_custs`) into a cross-engine distributed transaction — strictly worse. Full argument, scorecard, and the explicit triggers that would reopen this decision: `01-decision-financial-db.md`.

**Q2 — "How to split our database?"**
**By workload, as namespaces on the existing cluster** — `oms_core` (operations), `oms_fin` (money), `oms_ops` (logs/errors) — via `useDb()` on a single client so multi-document transactions still span core+fin. Plus the *real* performance split, which is not a split at all: get the request-log firehose out of the business working set (TTL + slim docs + `w:1`, destination decision in Phase 3). A second physical cluster is a Phase-5 decision gate driven by Phase-1 measurements, not an assumption. Full topology: `02-target-architecture.md`.

---

## Current state (audited 2026-07-02)

**Deployment:** 2× EC2 + ALB (canary pattern), PM2 fork mode, Atlas **M10** 3-node replica set (1500-conn limit), IP allowlist `0.0.0.0/0`, no VPC peering (flagged future in `docs/runbook.md`). No Redis, no queue/cron, no CI. In-process LRU cache per instance (`helpers/cacheMiddleware.js` — 10-min TTL, **not shared across the 2 servers**).

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

| # | Defect | Where | Fixed in |
| --- | --- | --- | --- |
| D1 | No money flow is transactional — crash mid `createInvNew` leaves ledger inconsistent until reconciled | `api_v3/services/invs.js:1120-1246`; `.session()` calls commented out in v2 | Phase 2 |
| D2 | `updateCrDr` is read-modify-write (`findOne` → `findByIdAndUpdate`), no `$inc`, no lock — concurrent postings lose updates | `api_v3/services/voc_msts.js:256-301`, duplicated `api_v3/services/invs.js:1007-1050` | Phase 2 |
| D3 | TOCTOU on AdvDep drawdown (guard-read then write) and on order credit-limit check (sum-then-create) | `voc_msts.js:387-479` (`updateVocStatus`), `order_msts.js:786-799` | Phase 2 |
| D4 | Money is float `Number` with `.toFixed(2)` string→float round-trips; no Decimal128/integer-minor-unit anywhere | `models/invs.js:55-115`, `models/dealer_custs.js:9-14` setters | Phase 2 (helpers) + Phase 4 (root fix) |
| D5 | No schema enforcement: `pay_mode` free string, `Mixed` blobs, no `$jsonSchema` validators | `models/voc_msts.js:49-52`, `models/pay_trns.js` | Phase 2 |
| D6 | `logs` written on **every request**, unbounded, no TTL, embeds full user object, `w:majority` — shares cache/IOPS with money data. `errors`, `pay_trns` also unbounded | `helpers/middlewares.js:229-279`, `models/logs.js` | Phase 3 |
| D7 | No TTL on `invites.expirationTime`; DIP collections (incl. high-write `meter_reads`) have **zero indexes** | `models/invites.js`, `models/dip_models/*` | Phase 3 |
| D8 | Every list endpoint runs `countDocuments(queryStr)` per page | `helpers/advancedResults.js:88,196` | Phase 6 |
| D9 | Statement/"account" reads merge `invs` + `voc_msts` in JS per request; TCS/TDS reports re-aggregate raw collections | `dealer_custs.js:584-642`, `TCSTDS/index.js` | Phase 4 (ledger) + 6 |
| D10 | 10-min cached financial reads can be stale across the 2 instances (LRU busts locally only) | `helpers/cacheMiddleware.js` | Phase 3 |
| D11 | No pool tuning, no wire compression, public internet path to Atlas | `helpers/db_conn.js` (no options), runbook | Phase 3 |
| D12 | `month_crdrs` missing uniqueness on `{cust_id, dealer_id, month}` — duplicate rollup rows possible | `models/month_crdrs.js:17` | Phase 2 |

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

- **API contracts frozen**: `/api/v2` and `/api/v3` request/response shapes must not change — app versions 1.68+ are in the field. All reading-path changes are server-internal or feature-flagged.
- **Local-data-only tests** (tasks_12 rule): everything here must be provable in the `mongodb-memory-server` harness. Phase 2 upgrades the harness to `MongoMemoryReplSet` because transactions require a replica set — coordinate with tasks_12 Phase 1.
- **No new infra until measured**: no Redis, no queue, no second cluster, no sharding unless Phase-1/Phase-5 evidence demands it. (Sharding is explicitly out: M10-class working sets are nowhere near it; the escalation path is M10 → M20 → analytics node, in that order.)
- **Reconciliation is the release gate**: every phase that touches money ends with `fin_txns`/`month_crdrs`/statement parity checks reporting **zero drift** before and after cutover (Phase 7 wires this into the tasks_12 release gate).
- Vault convention: this folder mirrors `tasks_11`/`tasks_12` format (no frontmatter, `**Outcome:**`/`**Effort:**` lines, `## N.M` subsections, phase checklists).
