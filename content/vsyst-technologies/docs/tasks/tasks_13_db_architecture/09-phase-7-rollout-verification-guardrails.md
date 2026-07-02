# Phase 7 — Rollout, verification & guardrails

**Outcome:** Every risky change in Phases 2–6 ships through the same disciplined path: canary on the existing 2-instance ALB pattern, reconciliation-gated cutovers, alerts that notice regressions before users do, corrected documentation, and a written rollback for each flip. This phase starts alongside Phase 2 and runs continuously; its checklist closes last.

**Effort:** 1–2 dev-days spread across the initiative.

## 7.1 Release mechanics per phase

| Change class | Rollout path | Rollback |
| --- | --- | --- |
| Config-grade (TTL, compression, pools, cache TTLs — Phase 3) | testing env → prod both instances (low risk) | revert config, redeploy; TTL indexes droppable |
| Write-path transactions (Phase 2) | testing full cycle → prod **canary instance** (ALB 1-of-2) 48h → both | deploy previous release; data is compatible both ways (same collections) |
| Dual-write + read flips (Phase 4) | flags: testing 2 weeks → prod canary → both; old path retained one release | flip `FIN_TXNS_READ` off (instant); dual-write may stay on |
| Namespace cutovers (Phase 5) | per-group freeze windows off-peak; ops group first as dry run | flip namespace env var back (old collections intact until post-verify drop) |

- [ ] Confirm the canary procedure in the runbook matches this table (it already documents 2-instance canary deploys); add the flag-flip steps.

## 7.2 Reconciliation as the release gate

- [ ] `scripts/reconcile_fin.js --dry-run` (zero-drift assertion) runs: nightly (Phase 2 crontab), **before and after every** money-path deploy, namespace cutover, and backfill — non-zero blocks the release.
- [ ] Wire into the tasks_12 release-gate script (its Phase 6) as a required step for `dzzlo_oms_api` releases.
- [ ] Keep the Phase-1 integrity scan runnable as the deep-audit variant (orphans, precision, duplicates) — run before each phase closes.

## 7.3 Monitoring & alert baseline (persists after the project)

- [ ] Atlas alerts (from Phase 1) reviewed against post-change steady state: connections, cache dirty, oplog rate, disk, replication lag; add namespace-level data-size alerts for `oms_ops` (TTL working) and `oms_fin` (growth rate sanity).
- [ ] CloudWatch: p95 per endpoint dashboards for the Phase-1 top-10 + statement endpoints; PM2 restart-count alarm (Puppeteer memory guard).
- [ ] Weekly 15-min metrics review during the initiative; monthly after.

## 7.4 Documentation debt (some of it pre-existing)

- [ ] **Fix stale `docs/ARCHITECTURE.md`**: it says v2 is active and v3 unrouted — reality is inverted (v3 mounted via `api_v/api3.js`). Rewrite the Databases section for the namespace map + connection design; add the ledger contract pointer.
- [ ] Runbook: new env vars, per-namespace users, restore procedure (namespace-selective restore from cluster snapshots), reconcile/backfill script usage, freeze-window procedure.
- [ ] `AI.md`: record the amended Active Development Rule (Q7 — additive schema changes allowed), the money-path rules ("all money mutations go through `withMoneyTxn` + posting composer; `fin_txns` is append-only; never hand-edit rollups"), and point agents at this plan folder.
- [ ] This vault folder: mark each phase file's status line as phases land (the tasks_12 convention).

## 7.5 Definition of done (whole initiative)

- [ ] All D1–D12 defects closed with the fix verified in prod (each has an owner phase; tick them in `00-overview.md`'s table).
- [ ] Two consecutive weeks of: zero reconciliation drift, zero money-path transaction-retry exhaustion in logs, SLOs met on the Phase-1 endpoint set.
- [ ] `logs` share of writes and data size at/below the Phase-3 target; TTL confirmed cycling.
- [ ] Statement/TCS-TDS/exports/balance served from the ledger in prod for a full month-close, including one FY-boundary test in the testing env (rollover math parity).
- [ ] Rollback playbooks exercised at least once in testing (flag-off drill + namespace flip-back drill).
- [ ] Open questions in `00-overview.md` all answered or explicitly accepted-as-default; `01-decision-financial-db.md` §5 triggers reviewed and dated "none fired".

## Phase 7 checklist

- [ ] Rollout table confirmed against runbook; canary + flag procedures documented
- [ ] Reconciler gating live: nightly, pre/post deploy, wired into tasks_12 release gate
- [ ] Alerts + dashboards tuned to post-change steady state; review cadence running
- [ ] ARCHITECTURE.md corrected; runbook + AI.md updated; phase files status-marked
- [ ] Definition-of-done list fully ticked; initiative retrospective note added to this folder
