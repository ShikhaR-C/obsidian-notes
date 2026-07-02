# Guide: Target database & network architecture

The topology this plan builds, and the reasoning for each choice. Diagrams first, mechanics after.

## 1. Current vs target

**Current** (audited): one Atlas M10 cluster `dzzlooms.kyfdo`, two logical DBs that are namespaces on the *same* nodes — so the "dual DB" isolates nothing physically. Two mongoose clients (= two connection pools). Everything from money postings to the per-request log firehose competes for the same RAM/IOPS.

```
2× EC2 (PM2 fork) ── client A (mongoose.connect, default opts) ──► APP220626   (all 22 OMS collections)
                  └─ client B (createConnection)              ──► Dip_web170426 (4 DIP collections, 0 indexes)
   public internet path, allowlist 0.0.0.0/0, no compression, w:majority for everything incl. logs
```

**Target:**

```
2× EC2 (PM2)
   │  ONE MongoClient (compressors=zstd, explicit pool, VPC-peered/private endpoint)
   │
   ├── useDb("oms_core")  users, cust_msts, dealer_msts, dealer_custs, order_msts, so_msts,
   │                      prod_msts, psocs, rate_msts, veh_msts, veh_reqs, veh_trns, dvr_msts,
   │                      invites(TTL), counters, contact_us
   ├── useDb("oms_fin")   fin_txns ★NEW, invs, voc_msts, month_crdrs(derived), pay_trns(dormant)
   ├── useDb("oms_ops")   logs(TTL 90d, slim, w:1), errors(TTL 180d)
   └── useDb("Dip_…")     dealers, meter_reads(+indexes), insps, decants   [second client OK too — see §3]

   One session ⇒ transactions span oms_core + oms_fin (same replica set).
   Optional later, evidence-gated: analytics node (heavy exports), ops → separate cheap cluster.
```

## 2. Namespace placement — collection by collection, with the *why*

| Namespace | Collections | Why here |
| --- | --- | --- |
| `oms_core` | users, cust_msts, dealer_msts, dealer_custs, order_msts, so_msts, prod/rate/psocs, veh_*, dvr_msts, invites, counters, contact_us | The operational graph. `dealer_custs` stays in core *despite* holding credit terms/`adv_dep` because it's the relationship root joined by everything; its money fields become derived-from-ledger in Phase 4. |
| `oms_fin` | **fin_txns**, invs, voc_msts, month_crdrs, pay_trns | The money spine: one namespace to grant/audit/restore as a unit. Same cluster as core ⇒ cross-namespace transactions keep working. |
| `oms_ops` | logs, errors | The firehose. Isolated so retention, write-concern, and (if ever needed) relocation to a cheap cluster never touch business namespaces. |
| DIP (existing name) | dealers, meter_reads, insps, decants | Already separate; gains indexes in Phase 3. Move only if the census (Q10) says its volume matters. |

**Honesty box — what a same-cluster namespace split does and does not give you:**
- ✅ Access control: per-namespace DB users (API user; read-only analyst on `oms_fin`; future partner-API principal with no `oms_ops` access). Fixes "one user sees everything".
- ✅ Selective restore/download of a namespace from cluster snapshots; per-namespace migration/archival; the option to relocate one namespace to its own cluster later *without app changes* (connection map is one file).
- ✅ Clean mental model + per-namespace metrics via Atlas namespace insights.
- ❌ **Not** resource isolation — same nodes, same cache. Physical isolation is exactly what the Phase-5 decision gate evaluates (ops cluster) once Phase-1 numbers exist. Do not claim perf wins from the namespace split itself; the perf wins come from Phase 3 (firehose diet) and Phase 6 (read path).

## 3. Connection mechanics (Phase 5 implements)

One client, many namespace handles — sessions are client-scoped, so this is what keeps `oms_core`+`oms_fin` transactions legal:

```js
// helpers/db_conn.js (target shape)
const conn = await mongoose.connect(CLUSTER_URI, {
  compressors: ["zstd"],            // + `yarn add @mongodb-js/zstd`
  maxPoolSize: 50, minPoolSize: 5,  // per process; 2 EC2 × 50 ≪ 1500 Atlas limit
  maxIdleTimeMS: 60_000,
});
const dbCore = conn.connection.useDb("oms_core", { useCache: true });
const dbFin  = conn.connection.useDb("oms_fin",  { useCache: true });
const dbOps  = conn.connection.useDb("oms_ops",  { useCache: true });
// models register on their namespace handle: dbFin.model("fin_txns", FinTxnSchema)
```

- `DATABASE_URI` env var stops carrying a DB name; a small connection map (`helpers/db_conn.js`) is the single place a collection's namespace is decided — that's the whole "split" surface area for app code.
- The DIP client can fold into the same client via `useDb` (one pool instead of two) — optional cleanup, not required.
- **Transactions**: `runInTransaction` gets a retry loop for `TransientTransactionError`/`UnknownTransactionCommitResult` labels (Phase 2). All money flows pass the session into every read/write they contain.

## 4. Write-path design (Phase 2/4 implement)

```
order/SO/invoice/voucher service
  └── runInTransaction(async (session) => {
        1. touch dealer_custs {$inc:{post_seq:1}}  ← per-relation serialization: concurrent
           money txns on the same relation write-conflict; loser aborts & retries ⇒ guards
           (AdvDep overdraw, credit limit) are re-evaluated on retry — kills the TOCTOU class
        2. business writes (invs / voc_msts / so_msts links)
        3. fin_txns.insertMany(postings, {session})      ← Phase 4; idempotency key unique index
        4. month_crdrs findOneAndUpdate({cust,dealer,month},{$inc:{drttl,crttl}},{upsert})  ← D2 fix
      })
```

- **Rollups become caches**: `month_crdrs` and `adv_dep` remain for fast reads but are rebuildable from `fin_txns` at any time; the reconciler's new job is proving `rebuild == stored` (zero drift), not repairing races.
- **Immutability**: `fin_txns` allows insert-only (validator + code review + a DB role without update/remove on that collection). Corrections are reversal postings referencing the original.
- **Idempotency**: `idem_key` = deterministic hash of `(src.type, src.id, leg)` with a unique index — retries and double-submits collapse; a future payment-gateway webhook posts through the same door (Q4).

## 5. Read-path design (Phase 4/6 implement)

- **Statements** (`getDealerCustomerAccount`): one indexed range scan of `fin_txns` per relation+window; running balance in one pass. Exports (Excel/PDF) and screens read the same stream — they can no longer disagree.
- **Balances**: FY opening (from ledger `OB` posting or `cust_bal`) + `month_crdrs` view − `adv_dep` view; every term provably rebuildable.
- **Heavy reads** (year exports, TCS/TDS, email statements): `readPreference: "secondaryPreferred"` — acceptable staleness for exports, keeps the primary's cache for OLTP. Balance-after-posting reads stay on primary (read-your-writes). If exports grow, the escalation is an Atlas **analytics node** + `readPreference` tags — still no second engine.
- **Pagination counts** (D8): skip `countDocuments` when no filter (use `estimatedDocumentCount`), cache counts for repeated filters, prefer cursor (range) pagination in app feeds.
- **Caching** (D10): the per-instance LRU stays, but financial GETs (`/app/currbal`, statements) get a short TTL (≤60s) or bypass — cross-instance bust doesn't exist and 10-minute-stale balances are a support-ticket generator. A shared cache (Redis) is *not* planned; revisit only with evidence.

## 6. Network path (Phase 3 implements)

| Change | Effect |
| --- | --- |
| VPC peering or private endpoint EC2↔Atlas (runbook already flags it; also closes allowlist `0.0.0.0/0`) | Removes public-hop latency variance; the security fix rides along |
| `compressors=zstd` on the URI/client | Smaller wire payloads both directions — biggest effect on list endpoints and statement scans |
| Explicit pool (`maxPoolSize` 50, `minPoolSize` 5, `maxIdleTimeMS` 60s) | Predictable conn budget (2×50 vs 1500 limit), warm connections after idle, no thundering reconnects |
| `w:1` (per-operation) for `logs`/`errors` writes | Fire-and-forget telemetry stops paying majority-ack round-trips |
| Same-region check EC2 vs Atlas + RTT measurement (Phase 1) | If regions differ, fixing that dwarfs every other knob in this table |
| Projection + `lean()` on hot lists (Phase 6) | Less BSON on the wire, less hydration CPU |

## 7. Sizing & escalation ladder (in order; each step needs Phase-1/continuing evidence)

1. Phase 3 hygiene (free) → 2. Phase 6 read path (free) → 3. M10→M20 (RAM/IOPS) → 4. Analytics node for exports → 5. `oms_ops` to separate cheap cluster → 6. Online Archive / `oms_archive` for closed FYs. **Not on the ladder**: sharding (wrong scale class for B2B khata data by orders of magnitude), microservices, CQRS infrastructure, Redis-by-default.
