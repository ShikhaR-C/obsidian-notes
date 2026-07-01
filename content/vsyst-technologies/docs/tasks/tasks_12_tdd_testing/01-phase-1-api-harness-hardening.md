# Phase 1 — API Harness Hardening

**Outcome:** `yarn test:full` in `dzzlo_oms_api` is deterministic, documented, and trustworthy as the backbone of the release gate; the test app exercises the same middleware chain as production; every legacy suite has a written verdict.
**Effort:** 1–2 dev-days.

> **TDD lens:** before writing more tests, make the harness one you'd bet a release on. Most of this phase is *verifying and documenting* what already works, then fixing the three real weaknesses found in review (middleware divergence, unpinned mongod binary, dangerous legacy suite).

---

## 1.1 What already works — keep it, write it down

Verified 2026-07-02 (do not "fix" these):

- **Isolation**: `test/database.js` spins up a fresh `mongodb-memory-server` per test file (per Jest worker process); each `describe` re-hydrates its own fixtures via `helper/beforeAll`. Parallel workers are safe by construction; fixtures are read-only during `yarn test`.
- **Crash-safety**: seed data lives only in the in-memory mongod (dies with the process) + JSON snapshots on disk. `test:full` (`yarn seed && yarn test; code=$?; yarn uproot; exit $code`) always uproots, even after failures. A `kill -9` mid-run leaves at worst a stale `temp/seed/data/` dir, which the next `uproot`/`seed` clears.
- **No cloud contact**: the test app graph (`test/dzzlo_oms_test.js` → `api_v/api2.js` + `api_v/api3.js`) never requires `helpers/db_conn.js` (the remote Atlas/DIP connections); outbound email/SMS is suppressed via `notify: false`.

These facts go into the new runbook (§1.5) so nobody re-litigates them.

## 1.2 Close the test-app ↔ production middleware divergence

**Finding:** `dzzlo_oms.js` mounts `api_key_v1()` → `logging()` → `check_user_version()` globally, but `test/dzzlo_oms_test.js` mounts only the routers. Consequences:

- `protect` depends on `req.loggedInUser` set by `logging()` — with it absent, **no bearer-token/role/scope path is testable** (regression-contract flow #2).
- `check_user_version()` / `legacy_credit_presenter()` behavior (flow #13, credit shim) is untestable end-to-end.
- We cannot simply import `dzzlo_oms.js` in tests: it requires `helpers/db_conn.js` at line ~22, which connects to remote Atlas **at import time**.

**Change (design):** extend `test/dzzlo_oms_test.js` to mirror the production chain, minus `db_conn`/listen:

`test/dzzlo_oms_test.js` (additions in repo idiom):

```js
// mirror production middleware order — keep in sync with dzzlo_oms.js
const { api_key_v1, logging, check_user_version } = require("../helpers/middlewares");

app.set("query parser", "extended");
app.use(express.json({ limit: "1mb" }));
app.use(api_key_v1());
app.use(logging());            // sets req.loggedInUser from Bearer JWT → protect works
app.use(check_user_version()); // version-gate behavior becomes testable
// ...existing api_v2 / api_v3 mounts unchanged...
app.use(errorHandler);         // helpers/error.js, mounted last like production
```

Notes: confirm `logging()`'s response-`finish` log write is harmless under memory-server (it is a normal collection write); if log noise bothers assertions, gate it with `if (process.env.NODE_ENV !== "test-quiet")` rather than forking behavior. Existing api_v3 tests keep passing because they already send `x-api-key` (`db.dheader`), which `api_key_v1` accepts (`X_API_KEY_3` allowed).

**Verify:** all existing suites still green; a new throwaway test can log in via OTP, call a `protect`-gated route with `Authorization: Bearer <jwt>` and get 200, and get 401 without it. (The real authorization suite lands in Phase 2.)

## 1.3 Determinism & ergonomics fixes

1. **Pin the mongod binary** so every machine/CI run uses the same engine and works offline after first download. Add `.mongodb-memory-server/mongodb-memory-server.config.js` (or `mongodb-memory-server` key in `package.json`) pinning `version` to the team standard; document the binary cache (`~/.cache/mongodb-binaries`) in the runbook.
2. **Make `yarn seed` idempotent** — today a same-day re-seed silently overwrites into `data/v3_<date>/`; a *different-day* re-seed leaves two dirs (harmless — loader picks latest — but confusing). Change:

   `package.json`:
   ```json
   "seed": "yarn uproot && NODE_ENV=development node ./test/api_v3/temp/seed/index.js"
   ```
   and wrap the seed body in `try/finally` so `db.close()` always runs:
   ```js
   // test/api_v3/temp/seed/index.js
   const CreateDir = async () => {
     await db.connect();
     try {
       /* ...existing factory sequence unchanged... */
     } finally {
       await db.close();
     }
   };
   ```
3. **Convenience scripts** (`package.json`):
   ```json
   "test:watch": "NODE_ENV=development jest --watch",
   "test:file": "NODE_ENV=development jest --runTestsByPath",
   "test:coverage": "NODE_ENV=development jest --coverage"
   ```
   (Coverage is observability, not a gate — ⏳ Q9.)
4. **Optional, only if a Phase-2 test needs it**: add a `counters` branch to `helper/beforeAll/index.js` — `counters.json` is written by seed but currently never re-hydrated (relevant for version-gate and numbering tests).

## 1.4 Legacy suite triage — verdicts (⏳ PENDING Q4 for deletion approval)

| Suite | Facts | Verdict | Rationale / what (if anything) to port |
| --- | --- | --- | --- |
| `test/202405_v2/` (~29 test files, ~18.6k LOC total) | Direct predecessor of api_v3; every test file has a same-named api_v3 counterpart | **Retire & delete** | Strict subset — contributes zero unique coverage. Safe immediately. |
| `test/api_v1_test/` (28 files, ~5.3k LOC) | Targets unmounted `/api/v1`; **connects to the real remote `DATABASE_URI`** and *writes* to it | **Retire & delete — priority** | Violates the local-only principle outright; endpoints dead. Nothing to port. |
| `test/api_v1/` (16 test files + own 2021-era fixtures) | Memory-server based but targets unmounted `/api/v1`; covers order list/get-one and `rate_msts` list — endpoints that are commented-out/"NOT USED" in v3 | **Retire & delete** | Its unique flows test **dead API surface**. If order list/get-one ever returns to v3, write fresh tests then. |
| `test/api_v2/` (18 test files) | Targets **live, frozen** `/api/v2` (still serving app versions 1.68–1.77); currently broken anyway — `db.dheader` sends `X_API_KEY_3` but v2 validates `X_API_KEY` → 401s | **Keep ignored & frozen** until the app's min supported version reaches ≥ 1.78, then delete | v2 is change-frozen policy-wise, so regression risk is low; reviving costs a header fix + fixture rework. Not worth it unless a v2 hotfix is ever needed (decision recorded here if so). ⏳ Q1/Q4 |

Actions in this phase: add the verdict table to `docs/testing.md`; leave `testPathIgnorePatterns` as-is until deletion is approved (the ignore entries are load-bearing).

## 1.5 Runbook — `dzzlo_oms_api/docs/testing.md` (new)

Outline (repo `docs/` already exists):

1. **Quick start**: `yarn test:full` — what it does, expected runtime, exit-code semantics.
2. **How the harness works**: memory-server per file, seed→snapshot→rehydrate diagram, why tests can't touch Atlas.
3. **Running one file / debugging**: `yarn test:file test/api_v3/collections/so_msts/index.test.js`, `--watch`, reading the `beforeAllHelper` "run seed first" error.
4. **Seed system**: factory order, where snapshots land, how to add a factory (Phase 2 shows a worked example), same-day re-seed semantics.
5. **Auth in tests**: `db.dheader` (`x-api-key`) vs bearer-token flow (post-§1.2).
6. **Legacy suites**: the verdict table.
7. **Env matrix**: tests run `NODE_ENV=development` (loads `.env.development` for keys/ports only — DB is always in-memory); `.env.testing` is for the deployed staging server, not Jest.

## 1.6 Verification — how we know Phase 1 is done

- `yarn test:full` green **twice consecutively** on a clean checkout (proves idempotent seed + no inter-run state).
- `yarn test` without seed data fails fast with the actionable "run the seed command first" error.
- `kill -9` a mid-run `yarn test`; the next `yarn test:full` passes with no manual cleanup.
- A bearer-token smoke test passes against the extended test app (§1.2).
- `docs/testing.md` exists; a teammate who has never run the suite follows it successfully.

## Phase 1 checklist

- [ ] `test/dzzlo_oms_test.js` mirrors production middleware chain (`api_key_v1`, `logging`, `check_user_version`, `errorHandler`)
- [ ] mongod binary version pinned + cache documented
- [ ] `seed` script made idempotent (`uproot &&` prefix) + `try/finally` around factory run
- [ ] `test:watch` / `test:file` / `test:coverage` scripts added
- [ ] (optional) `counters` re-hydration branch in `helper/beforeAll/index.js`
- [ ] Legacy verdict table written into `docs/testing.md`; deletion PR prepared but **not merged until Q4 answered**
- [ ] `docs/testing.md` runbook committed
- [ ] Verification steps in §1.6 all pass
