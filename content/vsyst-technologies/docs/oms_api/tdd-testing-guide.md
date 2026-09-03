# TDD Testing Guide — dzzlo_oms_api

> **Status (verified 2026-09-03):** **PR #35 is MERGED into `slave`** (2026-09-03, merge commit `2ca0301`; the user retargeted the PR from `master` to `slave` the same day, so `slave` now leads `master` by 12 commits until the next release merge). No reconciliation was needed: `api_tdd` already sat on top of master's PR #36 ledger work, so the two test sets simply union. Suite on `slave`: **49 files — 778 passed / 47 skipped / 1 todo under `test:full`** (CI 2m21s). Fixtures re-exported on seed **`v3_2026-09-03`** (`9d5c61e`) and pulled into both front-ends; cross-repo `release_gate.sh` printed **PASS** on 2026-09-03. Branch `api_v4_foundations` == `slave` (screen-redesign Phase 0 done). Built under tasks_12 (see `../tasks/tasks_12_tdd_testing/`), Phases 1, 2, 5, 6.
> **PR:** https://github.com/ShikhaR-C/dzzlo_oms_api/pull/35 · **Canonical runbook in-repo:** `docs/testing.md` (425 lines, on `api_tdd` only)

## 1. What was added (tasks_12)

This repo already had the backbone (Jest + supertest + `mongodb-memory-server`, seed/uproot, ~607 api_v3 tests). tasks_12 hardened it and made it the release authority:

- **Production-parity test app** (`test/dzzlo_oms_test.js`): now mirrors `dzzlo_oms.js`'s middleware chain — `api_key_v1` → `logging` (sets `req.loggedInUser`, so bearer/role/scope became testable) → `check_user_version`, extended query parser, 1 mb JSON limit, `errorHandler` last — plus a harness-only `GET /__smoke/whoami` probe. Still no `.listen()`, no `helpers/db_conn.js` (no Atlas contact possible).
- **Determinism fixes**: mongod engine pinned to **8.2.1** (`package.json` → `config.mongodbMemoryServer`); `yarn seed` made idempotent (`uproot &&` prefix + `try/finally`); **`yarn uproot` fixed** — it was silently a no-op on Node ≥ 22 (`fs.rmdirSync` recursive removed; now `fs.rmSync`).
- **New scripts**: `test:watch`, `test:file` (`--runTestsByPath`), `test:coverage`, `fixtures:export`.
- **New regression suites** (Phase 2, each mutation-smoke verified): `harness/middleware_chain` (Bearer 200 / 401 / 403 matrix), `auth/authorization` (`protect` via probe; `authorize`/`scope` as units — they're unwired on v3 routes, pinned as _current behavior_), `features/company_status` (route-level ACTIVE/INACTIVE/REMOVED/NOT_IN_COMPANY + superadmin bypass), `features/credit` (**the flagship**: max_cr_lmt null=unlimited / 0=blocked / >0=capped per landed tasks_08, reject = 404 "Credit Limit Exceeded", adv_dep as spending power, DC-update normalization), `features/version_gate` (hardcoded `check_user_version` matrix), `collections/order_msts/delivery_otp` (11 tests), `collections/invs/tax_types` (TCS invariants, C_S_UT_GST vs IGST).
- **Contract layer (Phase 5)**: `test/api_v3/temp/seed/export_fixtures.js` + shared `fixtures.captures.js` capture 6 real response envelopes into **committed** `fixtures/api_v3/*.json` + `fixtures.meta.json`; `features/contract/fixtures.test.js` is the **drift detector** — it re-runs the captures in-memory and deep-compares scrubbed envelopes (ObjectIds, `inv_no`, tokens, dates normalized; arrays order-insensitive), so any envelope change turns the suite red until `yarn fixtures:export` is deliberately re-run. Front-ends consume these via their `yarn fixtures:pull`.
- **Release gate (Phase 6)**: `scripts/release_gate.sh` — fixtures-fresh check (`scripts/check_fixtures_fresh.js`) → API `test:full` → dip-web `yarn test` → app `yarn test`; prints `RELEASE GATE: PASS`/`BLOCKED`, exit 0/1. Proven both green and red at build time.
- **CI + docs**: `.github/workflows/test.yml` (PRs + push to `master`, Node 22, mongod binary cache, `cp .env.ci .env.development`, `yarn test:full`, 15-min timeout), `.github/PULL_REQUEST_TEMPLATE.md` with the TDD checklist, and `docs/testing.md` — quick start, harness internals, seed system, auth-in-tests, legacy verdicts, **flow→test map (15 ranked flows, 13 pinned; DIP + Partner API deferred)**, release-gate policy, daily TDD workflow.
- **Zero production-source changes** — only `test/`, `fixtures/`, `scripts/`, `docs/`, `package.json`, CI files.

## 2. How the harness works (the facts that must not be re-litigated)

- Every test file gets its **own ephemeral in-memory mongod** (`test/database.js` `connect()`/`close()`); parallel-safe by construction; a `kill -9` can never leave server data behind.
- `yarn seed` builds the full two-dealer/two-customer world **through real API calls** and snapshots 16 collections to `test/api_v3/temp/seed/data/v3_<date>/` (**gitignored**). Suites rehydrate only what they ask for via `beforeAllHelper({ so_msts_data: true, ... })`, which fails fast with "run the seed command first" when no snapshot exists.
- Auth in tests: `db.dheader` (`x-api-key`) for business routes; bearer flow via the OTP-login helper where needed.
- Env: Jest runs `NODE_ENV=development` (`.env.development` supplies `X_API_KEY_3`/`JWT_SECRET` only — the DB is always in-memory). `.env.testing` is the deployed staging server, **not** Jest. `.env.ci` is the committed CI dummy.
- Legacy suites (`202405_v2`, `api_v1_test`, `api_v1`, `api_v2` — 91 files) are ignored via `testPathIgnorePatterns`. Verdicts: first three approved for deletion (**`git rm` still gated on a separate explicit go-ahead**); `api_v2` stays frozen-ignored until min supported app ≥ 1.78. ⚠️ `api_v1_test` writes to the real remote `DATABASE_URI` — the ignore entries are load-bearing.

## 3. How to run

```sh
yarn test:full        # THE command that certifies the API: seed → jest → uproot (exit code preserved), ~2 min
yarn test             # jest against whatever seed snapshot is on disk (fast, but see the stale-seed trap)
yarn test:watch       # TDD loop
yarn test:file test/api_v3/features/credit/index.test.js
yarn test:coverage    # observability only — no gate, no thresholds (Q9)
yarn seed / yarn uproot
yarn fixtures:export  # re-mint fixtures/api_v3/* (run after yarn seed; commit the result)
bash scripts/release_gate.sh   # cross-repo gate from the v1_79 workspace
```

Gotchas:

- **The stale-seed trap (this is the so_msts "NaN" failure).** `so_msts/index.test.js` aggregates over `getMonth_start_end(new Date())` — the _current_ month. A bare `yarn test` against an old snapshot (currently `v3_2026-07-24`) finds no docs in this month's window and totals come back NaN. **Not a code bug — re-seed (`yarn seed` or just use `test:full`).** Green under `yarn test` ≠ certified; **only `test:full` certifies** (lesson formalized after the Phase 5/6 ObjectId incident). Separate latent issue: `so_msts/index.test.js:260` hardcodes `"2024-05-13T…"` — re-seeding does not fix that one; it needs a code edit.
- **Fixtures freshness**: `fixtures.meta.json` currently records `seedSnapshot: v3_2026-07-08` — stale vs the on-disk seed; the contract spec and `check_fixtures_fresh.js` will complain until `yarn seed && yarn fixtures:export` is re-run (front-ends then `yarn fixtures:pull`).
- 19 `describe.skip`/`xit` blocks exist in the active suite (getAll matrix, TRANSACTIONAL cases, parts of prod_msts) — several without written verdicts; don't add more without one (PR-template rule).

## 4. How to write tests here (house idiom)

Integration-first: supertest against the shared in-process app, seeded world, one memory server per describe:

```js
const request = require("supertest")(require("../../../dzzlo_oms_test"))
const db = require("../../../database")
const { beforeAllHelper } = require("../../helper/beforeAll")

beforeAll(async () => {
  await db.connect()
  ;({ dealer_custs_data } = await beforeAllHelper({ dealer_custs_data: true }))
})
afterAll(async () => {
  await db.close()
})
// auth: .set(db.dheader); scenario setup: direct mongoose writes on rehydrated docs in this suite's beforeAll
```

- **Per-test scenario setup replaced seed factories** (Phase 2 decision): flip the seeded doc with a direct mongoose write (e.g. `dealer_custs.findByIdAndUpdate(rel._id, { max_cr_lmt: 0 })`) inside the suite — keeps the seed's own factories green and each suite self-contained.
- Shape assertions come from `test/api_v3/helper/collections/*`.
- **Mutation smoke** = definition of done for a new suite: temporarily disable the business rule in the service, confirm exactly the expected tests go red, revert, record in the PR.
- Push every rule as far down as it can live; the flow→test map in `docs/testing.md` §8 is the regression contract — new business flows add a row **in the same PR**.

## 5. How to tackle changes (the playbook)

| Change                                  | What to do                                                                                                                                                                                                                                                                                                                       |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **New endpoint / service rule**         | **Test-first at integration level.** Write the supertest spec from the contract (status, envelope, Mongo side effects) in `test/api_v3/` idiom, watch it fail, then implement route → controller → service. The contract _is_ the design artifact. New business flow ⇒ flow-map row + seed/factory extension if needed, same PR. |
| **Bugfix**                              | **Mandatory test-first.** Reproduce as a failing test named after the symptom (`it("does not double-charge TCS on part-paid invoice (bug 2026-…)")`), then fix. The test is never deleted. (The ledger work merged as PR #36 followed exactly this — its `test(ledger): reproduce …` commits are the model.)                     |
| **Refactor**                            | `yarn test` green before and after; assertions unchanged, or it wasn't a refactor.                                                                                                                                                                                                                                               |
| **Response envelope (contract) change** | The drift detector goes red — that's by design. `yarn seed && yarn fixtures:export`, commit; then `yarn fixtures:pull` + green suites in dip-web and the app **within the same release**.                                                                                                                                        |
| **Seed-world change**                   | Extend the factory under `test/api_v3/temp/seed/v3/factories/`, re-run `yarn seed`; keep everything local-only (in-process app or direct mongoose against the memory server).                                                                                                                                                    |
| **Touching legacy `/api/v2`**           | Frozen by policy — no new tests; if a v2 hotfix is ever unavoidable, record the decision in `docs/testing.md` §6 first.                                                                                                                                                                                                          |
| **Release prep**                        | `yarn test:full` here, then `bash scripts/release_gate.sh`. **Green gate or no release — the release date moves, not the bar.** Every gate failure becomes either a regression test (real bug) or a test fix (flake = P1 bug in the safety net).                                                                                 |

## 6. Pending / known issues (as of 2026-09-03)

1. ~~Merge PR #35~~ — **done 2026-09-03** into `slave` (`2ca0301`). `master` receives it at the next release merge; until then `master` itself still has no CI, gate or runbook.
2. ~~Re-seed + re-export~~ — **done 2026-09-03** (`9d5c61e`: seed `v3_2026-09-03`, six envelopes + meta; both front-ends pulled; gate PASS).
3. **Skips without verdicts** (47 skipped + 1 `todo` in the 2026-09-03 gate run) and the hardcoded date at `so_msts/index.test.js:260`.
4. **Legacy deletion** (73 files) approved in principle, still awaiting the explicit `git rm` go-ahead.
5. **DIP (flow #14) untestable** until `helpers/db_conn.js` gets a lazy/injected `db_dip` connection ("Phase 2b") — dip-web mocks DIP via MSW meanwhile.
6. **Stale docs**: `docs/strategy/tdd_strategy.md` (2026-03) predates all of this; `AI.md` still documents the ignored `202405_v2` suite and the renamed `--testPathPattern` flag (master fixed its own copy only).

## References

- In-repo: `docs/testing.md` (on `slave` since 2026-09-03) · `scripts/release_gate.sh` · `fixtures/api_v3/`
- Design + implementation record: `../tasks/tasks_12_tdd_testing/` (00-overview, phases 1, 2, 5, 6, 7)
- Siblings: [app guide](../oms_app/tdd-testing-guide.md) · [dip-web guide](../dip_web/tdd-testing-guide.md)
