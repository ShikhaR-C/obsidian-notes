# Phase 5 — Namespace split & cluster topology

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Not started: one default and one DIP connection (api:`helpers/db_conn.js:50-64`), no `useDb`, no namespace env vars (api:`.env.example:10-14`); database users are Atlas settings (❔). Of 5 sections: 3 ⬜, 2 ❔. When it starts, moving `month_crdrs` touches the v4 Customers read model too (T13-N2). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Outcome:** Collections live in their target namespaces (`oms_core` / `oms_fin` / `oms_ops`) behind a single-client `useDb()` connection map; per-namespace DB users enforce least privilege; the cluster-sizing decision (stay M10 / M20 / analytics node / ops cluster) is made from Phase-1 evidence and executed. App code paths and API contracts unchanged.

**Effort:** 2–4 dev-days + off-peak cutover windows (Q9 default: short per-group write-freeze).

**Pre-requisites:** Phase 4 (so `fin_txns` was born in `oms_fin` and only *legacy* collections move). Phase-1 census (sizes drive the migration mechanics and the sizing table).

## 5.1 Connection refactor (code first, move nothing yet)

**Status (2026-10-01):** ⬜ to do — no `useDb` anywhere; `DATABASE_URI` and `DIPDB` still name one database each (api:`.env.example:11,14`); api:`test/database.js:5,67` still starts one standalone `MongoMemoryServer`.

- [ ] Rework `helpers/db_conn.js` to the target shape (`02-target-architecture.md` §3): one client, `useDb()` handles, model→namespace registration map. `DATABASE_URI` becomes cluster-only; namespace names come from env (`DB_CORE`, `DB_FIN`, `DB_OPS`) so testing/dev/prod and the memory-server harness can differ safely.
- [ ] Interim state: all three handles point at the *current* DB name (`APP220626`) — a pure refactor release, provable by the full test suite + canary, before any data moves.
- [ ] Fold the DIP client into the same MongoClient via `useDb` (one pool) — optional but this is the natural moment.
- [ ] Update `test/database.js` + seed so the harness creates the three namespaces; cross-namespace transaction test added (memory replset supports it).

## 5.2 Move mechanics (per group, off-peak)

**Status (2026-10-01):** ⬜ to do.

Order: **ops first** (lowest risk, immediately relieves the business namespace), then **fin**, core stays (it keeps the original DB name or moves last — prefer *renaming nothing that doesn't need to move*: if `APP220626` simply *becomes* `oms_core` by moving fin+ops out, the largest group never migrates. Adopt that: core = the existing DB, aliased as `DB_CORE=APP220626`; cosmetic rename deferred indefinitely).

Per collection group:

1. `mongodump --db APP220626 --collection <c>` off-peak, or server-side `db.<c>.aggregate([{ $out: { db: "oms_fin", coll: "<c>" } }])` (same cluster — no network egress; preferred for big collections).
2. Incremental top-up: re-copy docs with `createdAt`/`updatedAt` ≥ T0 (all fin collections have timestamps; `logs` needs none — TTL data can tolerate a gap or simply start fresh in `oms_ops`).
3. Cutover: brief write-freeze on the group's endpoints (maintenance flag or off-peak deploy), final top-up, verify counts + checksums (`dbHash`/`Σ amount_p` for fin), flip the namespace env var, deploy, unfreeze.
4. Old collections renamed `<c>__migrated_<date>` (kept read-only for one release), then dropped.

- [ ] `logs`/`errors` → `oms_ops`: simplest — start writing to the new namespace at deploy time; let TTL drain the old ones; no copy needed. (Do this one first as the dry run of the connection map.)
- [ ] `invs`, `voc_msts`, `month_crdrs`, `pay_trns` → `oms_fin` via `$out` + top-up + freeze window; reconciler runs against **both** locations during the window and must report zero drift post-flip.
- [ ] Rebuild/verify indexes + reapply validators in the new namespaces **before** cutover (`scripts/apply_indexes.js`, `apply_validators.js` are namespace-aware).

## 5.3 Access control (the split's security payoff)

**Status (2026-10-01):** ❔ Atlas database users cannot be seen from the repos.

- [ ] Replace the single all-powerful DB user with: `oms_api` (readWrite on core+fin+ops+dip, minus `update`/`remove` on `fin_txns` via custom role — Phase 4's immutability made real), `oms_readonly` (read on core+fin, for humans/reports), future `partner_api` principal scoped per tasks_11 needs.
- [ ] Rotate credentials out of `.env` files per the runbook's Parameter Store plan (ride-along, don't block on it).

## 5.4 Cluster sizing decision (evidence-gated, costed)

**Status (2026-10-01):** ❔ no sizing decision recorded; the repos state the tier as M10 (api:`helpers/db_conn.js:8`).

Fill with Phase-1/3 numbers and decide:

| Option | When justified | Monthly cost delta |
| --- | --- | --- |
| Stay M10 | working set fits cache after Phase 3/6; CPU/IOPS headroom ≥ 30% | ₹0 |
| M10 → M20 | cache churn on business reads persists after index work | ~2× cluster cost |
| + Analytics node | exports/statements measurably evict OLTP cache (check `readPreference` metrics) | +~1 node |
| `oms_ops` → separate Flex/M10 | telemetry still >20–30% of IOPS after diet+TTL | + small cluster |

- [ ] Record the decision + numbers in `phase-1-findings.md`; execute (Atlas vertical scaling is online; analytics node addition is online).
- [ ] Explicitly reconfirm: sharding stays off the table (revisit note in `02-target-architecture.md` §7).

## 5.5 Config/docs sweep

**Status (2026-10-01):** ⬜ to do.

- [ ] `.env.example` + all env files: `DATABASE_URI` (cluster), `DB_CORE/DB_FIN/DB_OPS`, DIP vars; runbook connection/restore sections; seed scripts; `docs/ARCHITECTURE.md` dual-DB section (already stale — full fix in Phase 7).

## Phase 5 checklist

**Status (2026-10-01):** 0 of 8 done (a mark on each item); none flipped.

- [ ] Connection-map refactor shipped with zero namespace changes (suite green, canary clean) — **2026-10-01:** ⬜
- [ ] Harness + seeds create three namespaces; cross-namespace txn test green — **2026-10-01:** ⬜
- [ ] `logs`/`errors` cut over to `oms_ops` (write-forward, TTL drains old) — **2026-10-01:** ⬜
- [ ] Fin group moved via `$out` + top-up + freeze; counts/checksums verified; reconciler zero-drift before and after — **2026-10-01:** ⬜
- [ ] Core keeps existing DB name (no gratuitous migration); aliased as `DB_CORE` — **2026-10-01:** ⬜
- [ ] Per-namespace users live; `fin_txns` immutability enforced by role; old god-user retired — **2026-10-01:** ❔ Atlas settings; `fin_txns` does not exist
- [ ] Sizing decision recorded + executed with before/after metrics — **2026-10-01:** ❔ none recorded
- [ ] Envs, seeds, runbook, architecture docs updated — **2026-10-01:** ⬜
