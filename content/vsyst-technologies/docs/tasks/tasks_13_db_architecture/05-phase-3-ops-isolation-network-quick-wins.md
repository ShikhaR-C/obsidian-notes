# Phase 3 — Ops-data isolation & network quick wins

**Outcome:** The telemetry firehose stops competing with money data (D6, D7 closed), and the EC2↔Atlas path is tuned (D10, D11): TTLs, slim log docs, `w:1` telemetry writes, wire compression, explicit pooling, private networking. Almost entirely config-grade changes with immediate, measurable effect against the Phase-1 baseline.

**Effort:** 1–2 dev-days. Independent of Phase 2 — can ship first.

## 3.1 Log document diet (D6)

The logging middleware (`helpers/middlewares.js:229-279`) embeds the full `user` object and `appInfo` per request.

- [ ] Reduce to: `user_id`, `co_id`, `role`, `route` (mounted path pattern, not raw URL), `method`, `status`, `duration_ms`, `app_version`, `ip`, `createdAt`. Drop bodies, headers, and the embedded user document. (Middleware edit — `helpers/` frozen-dir exception per Q7, or relocate the middleware to `api_v3` if governance prefers.)
- [ ] Confirm `/healthcheck` stays outside logging (it bypasses the stack — verify no other high-frequency no-value routes are logged, e.g. static/updates polling).
- [ ] Expected effect vs Phase-1 numbers: log bytes/day should drop by the measured embed share (often 60–80%).

## 3.2 TTLs — telemetry expires, money never does (D6, D7)

- [ ] `logs.createdAt` TTL **90d** (Q2 default), `errors.createdAt` TTL **180d**, `invites` TTL on `expirationTime` (`expireAfterSeconds: 0`).
- [ ] Apply via `scripts/apply_indexes.js` (idempotent, committed, run per env) **and** declare in the models so the memory-server harness matches prod (additive `index({createdAt:1},{expireAfterSeconds:...})`).
- [ ] **No TTL on any financial collection** — statutory retention; archival is a Phase-6 decision instead.
- [ ] First-run note: TTL deletion of a large backlog is itself I/O — if census shows `logs` in the tens of GB, pre-trim off-peak in batches (`deleteMany` on date ranges) before creating the TTL index.

## 3.3 Telemetry write concern (D6)

- [ ] `Logs.create(...)` / `Errors.create(...)` calls get `{ writeConcern: { w: 1, j: false } }` — fire-and-forget telemetry stops paying majority-ack round trips. Business writes keep `w:majority` (URI default).

## 3.4 Wire compression (D11)

- [ ] `yarn add @mongodb-js/zstd`; add `compressors: ["zstd"]` to both connections (or URI `?compressors=zstd`).
- [ ] Verify negotiation: `db.serverStatus().network.compression` / driver log; re-run the §1.4 RTT + a list-endpoint payload timing to record the delta.

## 3.5 Explicit pooling (D11)

- [ ] `maxPoolSize: 50`, `minPoolSize: 5`, `maxIdleTimeMS: 60000` on both clients (`helpers/db_conn.js`). Budget: 2 EC2 × (50+50 for the two clients) = ≤200 of the 1500-conn M10 limit, with headroom for PM2 cluster mode later.
- [ ] Add `serverSelectionTimeoutMS: 10000` so a node failover fails fast to the ALB health check rather than hanging requests.

## 3.6 Private network path + allowlist (D11 + security ride-along)

- [ ] Set up VPC peering (or private endpoint) between the EC2 VPC and Atlas, same region — runbook already flags this as future work; this phase executes it.
- [ ] Cut the IP allowlist from `0.0.0.0/0` to the VPC/NAT + office IPs.
- [ ] Re-measure §1.4 RTT; update the runbook's connection instructions.

## 3.7 Obvious missing indexes (zero-risk subset of Phase 6)

- [ ] DIP (D7): `meter_reads {dealer_id:1, createdAt:-1}`, `decants {dealer_id:1, createdAt:-1}`, `insps {dealer_id:1, createdAt:-1}`, `dealers {dealer_id:1}` (or actual query keys per `dip_api_v1` controllers — verify with Profiler before creating).
- [ ] Build with `{ background: true }` semantics (default in current server versions), off-peak.

## 3.8 Financial cache staleness policy (D10)

The per-instance LRU (10-min TTL) means instance B serves stale balances up to 10 minutes after instance A posts money.

- [ ] Exclude or short-TTL (≤60s) the financial GETs in `helpers/cacheMiddleware.js`: `/app/currbal`, `/app/allRelationCurrBal`, statement endpoints, AdvDep ledger.
- [ ] Leave master-data GETs (products, rates, relations) on the 10-min TTL — they're what the cache is good at.
- [ ] Explicitly record: **no Redis** — a shared cache enters the picture only if post-Phase-6 metrics show primary read pressure that projection/indexes didn't fix.

## 3.9 Logs destination decision (Q2 — record it)

With diet+TTL+`w:1` in place, decide and write down (in `phase-1-findings.md`):
- **(a) stay in the OMS DB** (default if firehose share drops below ~15% of writes) — later relocated to `oms_ops` namespace by Phase 5 regardless;
- **(b) `oms_ops` on a separate cheap cluster** — only if share stays high;
- **(c) ship request logs to CloudWatch** (infrastructure already in use) and keep only a thin audit trail in Mongo — the strategic direction if request analytics ever becomes a product need.

## Phase 3 checklist

- [ ] Log docs slimmed; healthcheck & polling routes confirmed unlogged
- [ ] TTLs live on `logs`/`errors`/`invites` (backlog pre-trimmed if large); none on financial collections
- [ ] Telemetry writes at `w:1,j:false`; business writes unchanged at majority
- [ ] zstd compression negotiated and measured against baseline
- [ ] Pool sizes + timeouts explicit on both clients
- [ ] VPC peering/private endpoint live; allowlist closed; RTT re-measured
- [ ] DIP indexes created (query-key-verified)
- [ ] Financial endpoints excluded/short-TTL'd in LRU cache
- [ ] Logs-destination decision recorded with the supporting numbers
