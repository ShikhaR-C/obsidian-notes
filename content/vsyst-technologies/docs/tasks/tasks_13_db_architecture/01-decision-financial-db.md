# Guide: Should financial transactions move to a structured (SQL) database?

**Decision: No engine change. Build the structure inside MongoDB.** This document is the full argument, the honest scorecard, the precision policy, and — importantly — the written list of triggers that would make us reopen this decision. Keep it; it is the answer to "why didn't we use Postgres?" two years from now.

## 1. What people actually mean by "structured DB", mapped to what we'd do in Mongo

"Use SQL for money" is shorthand for five real requirements. Each has a first-class MongoDB mechanism — all five are currently unused in our codebase, which is why money *feels* unstructured today:

| Requirement | SQL mechanism | MongoDB mechanism | Our status today |
| --- | --- | --- | --- |
| Enforced schema on money rows | DDL + column types | `$jsonSchema` collection validators (`collMod`), enums in Mongoose | ❌ none — `pay_mode` is a free string, `pay_res` is `Mixed` |
| Atomic multi-row postings | ACID transactions | Multi-document transactions on a replica set (we run Atlas 3-node — supported since 4.0) | ❌ helper exists (`helpers/transactions.js`), used only for `veh_reqs` |
| Exact money arithmetic | `NUMERIC(12,2)` | Integer minor units (paise) or `Decimal128` | ❌ float `Number` + `.toFixed(2)` round-trips |
| A queryable ledger ("give me every financial event for relation X in FY Y, in order") | A `postings` table | An append-only posting collection with compound indexes | ❌ statements merge `invs` + `voc_msts` in JS per request (`api_v3/services/dealer_custs.js:584-642`) |
| Constraints (uniqueness, one-adjustment-per-deposit) | UNIQUE / FK / CHECK | Unique + partial indexes, validators, conditional `findOneAndUpdate` | 🟡 a few unique indexes; the AdvDep "one adjustment" rule is a JS set-membership check |

Conclusion of the mapping: **the gap is discipline, not engine.** Phases 2 and 4 install exactly these five mechanisms.

## 2. Why *not* PostgreSQL (specific to this system, not ideology)

1. **Atomicity would get worse, not better.** Money never moves alone here: `createInvNew` writes `so_msts` (link) + `invs` + `month_crdrs`; voucher approval writes `voc_msts` + `month_crdrs` + `dealer_custs.adv_dep`; order creation reads credit exposure across three collections. Inside one Mongo replica set, one transaction covers all of it (even across the `oms_core`/`oms_fin` namespaces — sessions span databases on the same cluster). With the ledger in Postgres, every one of these becomes a two-engine distributed write needing outbox/saga machinery and a reconciliation story for *partial* failure. We would be importing the hardest problem in distributed systems to solve a schema-discipline problem.
2. **Operational surface doubles for a team that runs lean.** Today: one Atlas cluster, PM2, no queue, no Redis, no CI. Postgres adds provisioning, backups/PITR, upgrades, monitoring, connection pooling (pgbouncer), a second driver/ORM, and a second security model — permanently.
3. **The entire test strategy just standardized on Mongo.** tasks_12 built the regression harness on `mongodb-memory-server` with seeded fixtures across three repos. A SQL ledger forks the harness (containers or embedded PG), the seed system, and the fixtures contract on day one.
4. **The queries we struggle with are not relational-shaped.** Statements, TCS/TDS summaries, balances, exports are *time-ordered scans and group-bys over one logical stream per relation* — exactly what a posting collection + compound index + aggregation `$group`/`$merge` serve. There is no many-way ad-hoc JOIN workload here; the joins we do (`$lookup` ×10 in the codebase) are narrow and index-backed.
5. **Migration risk with zero user-visible payoff.** Dual-run + backfill + cutover of the money spine across 3 client apps, for query capabilities we can have in-place. The payoff column is empty until one of the §5 triggers fires.

## 3. Scorecard (kept honest — SQL wins some cells)

| Criterion | A. Structured-in-Mongo (this plan) | B. Hybrid: PG ledger + Mongo ops | C. Full move to PG |
| --- | --- | --- | --- |
| Cross-entity atomic postings | ✅ one txn, one engine | ❌ saga/outbox across engines | ✅ (after total rewrite) |
| Query power for our actual reports | ✅ indexed single-stream + aggregation | ✅ SQL, but data split across engines | ✅ |
| Ad-hoc SQL for analysts | 🟡 Atlas SQL / Charts / BI connector | ✅ | ✅ |
| Money precision | ✅ integer paise (policy §4) | ✅ NUMERIC | ✅ NUMERIC |
| Schema enforcement | ✅ validators + unique/partial indexes | ✅ | ✅ |
| Ops burden added | ~0 | ++ (second engine, saga infra) | ++ then + |
| Test harness (tasks_12) | ✅ unchanged (needs replset mode) | ❌ forked | ❌ rebuilt |
| Migration risk to a working money system | Low (additive, reconciler-gated) | High | Very high |
| Team/stack fit (3 repos, all Mongoose) | ✅ | 🟡 | ❌ |
| Fit if a full accounting module (CoA, P&L, trial balance) becomes product scope | 🟡 possible (double-entry in Mongo is done in industry) but re-evaluate | ✅ | ✅ |

**Choice: A.** B is the worst of both worlds at this scale. C is a rewrite justified only by triggers below.

## 4. Precision policy (the D4 fix)

Today every money field is a float with a setter `v => (Math.round(v*100)/100).toFixed(2)` — note `.toFixed(2)` returns a **string** Mongoose casts back to a float (`models/invs.js:55-115`). Sums of many 2-dp floats accumulate sub-paise error; the reconcilers currently paper over it.

**Policy (default, pending Q6):**
- **API boundary unchanged**: JSON continues to carry rupees as numbers (`1234.56`). No client app changes.
- **New internal arithmetic in integer paise**: a tiny `api_v3/services/money.js` — `toPaise(rs)`, `toRupees(p)`, `addRs(...xs)`, `mulRsQty(rate, qty, roundingMode)` — used by Phase-2 rewrites of `calcttl`/`updateCrDr` and everything Phase 4 touches. Integer add/subtract in JS is exact up to 2^53 paise (₹90 trillion) — comfortably beyond > ₹50-lakh-turnover B2B fuel accounts.
- **`fin_txns.amount_p` stored as integer paise** (`int`), with the `$jsonSchema` validator enforcing `bsonType: "long"`/`"int"` and `>= 0` plus a `side: DR|CR` field — sign lives in the side, not the number.
- **Legacy fields untouched** (`inv_total_amt` etc. stay 2-dp floats): they are display/document values; the ledger becomes the arithmetic source of truth. Rounding residue at invoice level already has a home (`inv_round_amt`).

*Why not Decimal128*: it fixes storage but not JS arithmetic (still needs a decimal library on every `+`), it makes every read a `.toString()` conversion in three client repos, and Mongoose ergonomics around it are poor. Integer paise fixes the arithmetic itself with native operators. Revisit only if sub-paise precision (e.g. per-litre micro-rates) becomes a requirement — rates today are 2-dp and quantity×rate rounding is explicitly policy (`inv_round_amt`).

## 5. Triggers that reopen this decision (write the date next to any that fires)

1. Finance/BI analysts need **daily ad-hoc SQL** joins and Atlas SQL/Charts demonstrably can't serve them.
2. Product scope grows a **true accounting module** — chart of accounts, journal + trial balance, P&L/balance-sheet statements. (Then evaluate: double-entry in Mongo vs an accounting subsystem in PG behind an internal API.)
3. A **statutory/audit requirement** mandates relational tooling or immutable WORM storage beyond what validators + reversal-only corrections provide.
4. Reconciliation aggregation pipelines exceed maintainability — e.g. a report that genuinely needs 4+ way joins across large collections, rewritten twice and still slow.
5. Sustained scale where Mongo economics break: working set for *money* collections alone exceeding an M30-class node after archival — implausible for B2B fuel khata volumes, but recorded.

## 6. What "better querying" concretely becomes (preview of Phase 4/6)

| Today | After |
| --- | --- |
| Statement = fetch invoices + fetch approved vouchers + merge/sort in JS per request | `fin_txns.find({dealer_id, cust_id, posting_dt: {$gte, $lt}}).sort({posting_dt: 1})` — one indexed scan, running balance computable in one pass |
| Balance = FY opening + cumulative `month_crdrs` scan − recomputed `adv_dep` (3 queries + JS) | same formula but every term is a ledger `$group` (or the maintained `month_crdrs` view, now provably rebuildable) |
| TCS/TDS = separate aggregations over `invs` and `voc_msts` with `$month`+timezone math | one `$group` over `fin_txns` on pre-computed `fy`/`month` keys filtered by `src.subtype` |
| Excel/PDF exports re-derive everything | exports read the same ledger stream — statement, export, and balance can no longer disagree |
| "Why does the balance say X?" → run reconciler, compare three sources | every paisa traces to an immutable posting row with `src` back-pointer |
