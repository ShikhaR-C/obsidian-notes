# 04 — `dzzlo_oms_api` Upgrade Plan: File-by-File Changes

**Date:** 2026-04-11
**Scope:** Upgrade MongoDB Atlas 7.0.31 → 8.0 and refresh the Node-side driver + Mongoose to the current latest.
**Companion:** [`03_mongoose_driver_upgrade.md`](./03_mongoose_driver_upgrade.md)
**Active dev rule:** Write new code only under `dzzlo_oms_api/api_v3/`. This plan touches infra files (package.json, db_conn.js) and audits `api_v1`/`api_v2` for legacy patterns; it does NOT modify legacy feature code.

---

## 1. Context (read first)

Files actually inspected for this plan:

- **`dzzlo_oms_api/package.json`** — declares `"mongoose": "^9.4.1"` (line 32), `"mongodb": "^7.1.1"` (line 31), `"mongodb-memory-server": "^11.0.1"` (dev line 41). Yarn is the package manager (`yarn.lock` present; `feedback_package_manager.md` confirms).
- **`dzzlo_oms_api/helpers/db_conn.js`** — exports `dbDefault`, `db_dip`, `defaultConnectionPromise`. Uses `mongoose.connect(databaseURI)` for the default and `mongoose.createConnection(database_dip)` for the DIP auxiliary DB. Line 5 has a commented `mongoose.set("updatePipeline", true)` leftover from the 8 → 9 migration.
- **`dzzlo_oms_api/dzzlo_oms.js`** — entry point. Imports `defaultConnectionPromise` from `helpers/db_conn.js`, `app.listen()`s only after the promise resolves, and calls `mongoose.disconnect()` on SIGTERM/SIGINT. Lines 45–53 still carry a commented-out legacy connection block with `useNewUrlParser` / `useUnifiedTopology` / `useCreateIndex` / `useFindAndModify`.
- **`dzzlo_oms_api/api_v/api_constants.js`** — reads `process.env.DATABASE_URI` and `process.env.DIPDB`; chooses an API base URL per `NODE_ENV`.
- **`dzzlo_oms_api/models/cust_msts.js`** — representative model. Uses `pre("save")` without `next()` (Mongoose 9 style already applied), `updateOne` with `upsert: true`, plain `mongoose.Schema` and `ObjectId` refs.
- **`dzzlo_oms_api/models/order_msts.js`** — 6 compound indexes on `order_mst_Schema`, subdocument `order_trn_Schema`. `getOTPToken` already refactored off the callback API.
- **`dzzlo_oms_api/api_v3/controllers/collections/cust_msts.js`** — thin HTTP controller that delegates to `api_v3/services/cust_msts.js`. All handlers use `asyncHandler` + `async/await`. No callback-based calls.
- **`dzzlo_oms_api/docs/strategy/mongoose_9_upgrade_plan_61daa006.strategy.md`** — prior migration record, all TODOs marked `completed`.

**Takeaway:** the last Mongoose major migration is fully done. This plan is about (a) aligning the Atlas server with the already-installed Node packages (7.0.31 → 8.0) and (b) keeping the Node stack current with a lockfile refresh.

---

## 2. Pre-upgrade Checklist

- [ ] **Atlas backup** — From Atlas UI → Project → Backups, trigger an on-demand snapshot of the production cluster (source DB + `db_dip` DB). Confirm snapshot completes before starting.
- [ ] **Download point-in-time snapshot locally** — `mongodump --uri "$DATABASE_URI"` and `mongodump --uri "$DIPDB"` on a secure workstation as a belt-and-braces offline copy. Store encrypted. (Security note: prefer a `--config` file for the credentialed URI — even via an env var, the expanded argument is visible in `ps` output while the dump runs.)
- [ ] **Create a throwaway Atlas test cluster** on **M10+** seeded from the latest snapshot. (Not M0/Flex: snapshots can't be restored into shared tiers, and shared tiers don't let you pin/choose the MongoDB major version, so an upgrade rehearsal isn't possible there.) Run the upgrade rehearsal here first.
- [ ] **Pin Node.js** — project runs fine on Node 22/24 (Mongoose 9 floor is 20.19). Add a `.nvmrc` with `20.19.0` (minimum supported) or `22.x` (LTS at time of writing). Current dev machine reports `v24.14.1`.
- [ ] **Confirm `yarn.lock` committed** — mandatory, Yarn is the package manager (`feedback_package_manager.md`).
- [ ] **Capture baseline metrics** — response times for hot `api_v3` routes (list customers, orders by dealer), current `db.serverStatus()`, current `db.currentOp()` patterns. Needed for before/after comparison.
- [ ] **Freeze schema/index changes** during the upgrade window.
- [ ] **Notify on-call & business stakeholders** of the maintenance window.
- [ ] **Review `.env.production` / `.env.testing`** — confirm `DATABASE_URI` and `DIPDB` still point to the correct cluster; SRV strings should already use `mongodb+srv://`.

---

## 3. Step 1 — Upgrade Atlas Cluster 7.0.31 → 8.0

MongoDB Atlas supports in-place major version upgrades once the cluster reaches the latest 7.0.x patch. The cluster is already on 7.0.31 so no interstitial patching required.

### 3.1 Dev / Test cluster first

1. Atlas UI → **Project** → **Database** → select the test cluster → **…** menu → **Edit Configuration**.
2. Under **MongoDB Version**, switch from `7.0` to `8.0`. Atlas will show a warning banner about feature compatibility version (FCV).
3. Confirm — Atlas performs a rolling upgrade: secondary → secondary → primary stepdown. Expect ~5–15 minutes on an M10.
4. After the cluster status returns to **Active**, connect via `mongosh` and confirm: `db.version()` → `8.0.x`, `db.adminCommand({ getParameter: 1, featureCompatibilityVersion: 1 })` → `{ version: "8.0" }`. If FCV is still `"7.0"`, run `db.adminCommand({ setFeatureCompatibilityVersion: "8.0", confirm: true })` after bake-in.
5. Boot `dzzlo_oms_api` against the upgraded test cluster (`NODE_ENV=testing yarn start:test`). Smoke test: health check, auth flow, customer list, order create, dip endpoints.

### 3.2 Production cluster

Repeat the exact sequence on the production cluster during the maintenance window. Do **not** set FCV to `8.0` immediately — leave at `7.0` for 24–48 hours, then promote once the app is stable. Setting FCV=8.0 is a one-way door. (Note: even with FCV held back, Atlas has no in-place downgrade — see §8.2 — but holding FCV keeps 8.0-only on-disk changes off and preserves the cleanest recovery options.)

### 3.3 db_dip cluster

If `db_dip` lives on a separate cluster (check the `DIPDB` URI in `.env.production`), repeat the same upgrade flow there. If it’s a second database on the same cluster, it upgrades automatically with the host.

---

## 4. Step 2 — Refresh Node Packages

Both packages already satisfy latest-on-npm (`mongoose 9.4.1`, `mongodb 7.1.1`). The change is a lockfile refresh, not a `package.json` edit.

### 4.1 package.json — no manual edits required

If the team wants explicitness, the target lines stay identical:

```jsonc
// dzzlo_oms_api/package.json (lines 30–32, unchanged)
"mongo-sanitize": "^1.1.0",
"mongodb": "^7.1.1",
"mongoose": "^9.4.1",
```

Only modify if the `yarn.lock` resolves to a version below the latest published one — in that case bump the caret to the literal latest (e.g. `"mongoose": "^9.4.1"` if it was previously `"^9.4.0"`).

### 4.2 Commands

```bash
cd dzzlo_oms_api
yarn upgrade mongoose mongodb mongodb-memory-server
yarn install --immutable   # verify lockfile is clean
yarn jest                  # run the suite
```

**Do not** use `npm install` — this project is Yarn-only. The `feedback_package_manager.md` note is authoritative.

### 4.3 Expected lockfile deltas

- `mongoose` resolves to `9.4.1` exactly.
- `mongodb` resolves to `7.1.1` exactly.
- Transitives: `bson@^7.1`, `@mongodb-js/saslprep@^1.3`, `mongodb-connection-string-url@^7.0`, `kareem@3.2.0`, `mquery@6.0.0`, `mpath@0.9.0`, `sift@17.1.3`.
- `mongodb-memory-server@^11.x` may pull a fresh MongoDB 8.x binary for tests.

---

## 5. Step 3 — `dzzlo_oms_api/helpers/db_conn.js` Changes

Current state inspected at lines 1–49. No functional changes required to support MongoDB 8 or driver 7.1.1. **Cosmetic cleanup** only:

### 5.1 Remove the dead `updatePipeline` comment

```diff
  const mongoose = require("mongoose");
  const { databaseURI, database_dip } = require("../api_v/api_constants");

- // Enable update pipelines globally (required for Mongoose 9)
- // mongoose.set("updatePipeline", true);
-
  // Default Connection (Global) — export promise so app can wait before listening
```

Reason: the migration settled on per-call `{ updatePipeline: true }` (see `api_v2/controllers/dbUpdates/**` grep). Leaving a commented set-statement is stale noise.

### 5.2 Nothing else changes

`mongoose.connect(databaseURI)` and `mongoose.createConnection(database_dip)` are still the correct Mongoose 9 / driver 7 APIs. No options object required — SRV strings carry auth, read preference, retry writes etc. The event handlers (`on("error")`, `once("open")`) and `SIGINT` graceful shutdown are unchanged in Mongoose 9.

### 5.3 Optional hardening (recommended, not required)

Consider adding a `serverSelectionTimeoutMS` to fail fast during outages:

```js
const defaultConnectionPromise = mongoose
  .connect(databaseURI, { serverSelectionTimeoutMS: 10_000 })
  .then(() => mongoose.connection);
```

Not required for the upgrade itself; file as a follow-up ticket.

---

## 6. Step 4 — Deprecated API Audit

Grep was run for every known-deprecated pattern from the Mongoose 9 migration guide. Results:

### 6.1 `useNewUrlParser` / `useUnifiedTopology` / `useCreateIndex` / `useFindAndModify`

Live occurrences:

- **`dzzlo_oms_api/dzzlo_oms.js` lines 47–50** — inside a commented-out block (the old `mongoose.connect` attempt). Cosmetic. Delete the whole comment block during this pass:

```diff
  app.set("query parser", "extended");
- // // db
- // mongoose
- //   .connect(databaseURI, {
- //     // useNewUrlParser: true,
- //     // useUnifiedTopology: true,
- //     // useCreateIndex: true,
- //     // useFindAndModify: false,
- //   })
- //   .then(() => console.log("DATABASE CONNECTED!!"))
- //   .catch((err) => console.log("Database error is ", err));
-
  // middlewares
```

- **`dzzlo_oms_api/test/dzzlo_oms_test.js` lines 26–30** — same kind of dead comment. Clean up.
- **`dzzlo_oms_api/test/api_v1_test/**/*.test.js`** — ~40 call sites in the legacy `api_v1` test tree actively pass `useNewUrlParser`/`useCreateIndex`/`useUnifiedTopology`/`useFindAndModify` as live `mongoose.connect` options. These tests target the deprecated `api_v1` code path. **Do NOT rewrite them** — the active-dev rule says `api_v1`/`api_v2` are frozen. Mongoose 9 silently ignores these legacy options (they don’t throw), so the test suite will still execute. If a test starts failing after the upgrade because a legacy option is finally rejected, mark the suite `.skip()` and file a ticket.

### 6.2 `.remove()` and `.update()` (document-level)

Found exclusively under `api_v1/controllers/collections/*.js` (veh_trns, rate_msts, voc_msts, dealer_custs, pay_trns, contact_us, invs, order_msts, veh_msts, dvr_msts, so_msts, dealer_msts, cust_msts, users, prod_msts). These use the removed `doc.remove()` pattern. **Action: none** — `api_v1` is disabled in `dzzlo_oms.js:107` (`app.use("/api/v1", api_v1)` is commented out). The files are dead code.

All other `.update(` hits in `api_v3/services/auth.js`, `api_v2/controllers/auth/**`, `models/users.js` and the Paytm payment helper are `crypto.createHash(...).update(...)` (Node crypto stream API, unrelated to Mongoose). No action.

### 6.3 Callback-style `findOneAndUpdate` / `findByIdAndUpdate`

Grep of `api_v3/services/**` shows all `findOneAndUpdate` calls are awaited and pass `{ new: true, runValidators: true }` style options — no callbacks. Same for `api_v3/controllers/**`. `order_msts.getOTPToken` was already refactored (confirmed in the 8 → 9 migration strategy doc, `order_msts.js:118` now uses `async/await`).

### 6.4 Middleware `next()`

Previously removed from `models/users.js`, `models/cust_msts.js`, `models/dealer_msts.js`, `models/invs.js`. Confirmed clean in `cust_msts.js:68` (read today).

### 6.5 `isValidObjectId(number)`

Grep: no matches. Safe.

**Net effect for Step 4:** one file edit (`dzzlo_oms.js` comment removal), one file edit (`db_conn.js` comment removal), one optional edit (`test/dzzlo_oms_test.js` comment removal). No behavioural changes.

---

## 7. Step 5 — Test Strategy

### 7.1 Unit / integration

```bash
cd dzzlo_oms_api
yarn test   # jest, runs the full suite (see package.json scripts line 10)
```

This spins `mongodb-memory-server@^11` (now pulling a MongoDB 8 binary) so the test harness actually exercises the upgraded server version in-process. Compare pass/fail counts against the last green CI run.

If any `api_v1` legacy suite fails because of a newly-enforced option, `.skip()` the suite and log a ticket — do not patch legacy code as part of this upgrade.

### 7.2 Manual route smoke test against the upgraded Atlas 8 test cluster

Set `NODE_ENV=testing` and boot `yarn start:test`. Exercise, at minimum, one route per resource in `api_v3/controllers/collections/`:

- `POST /api/v3/auth/login` and refresh
- `GET /api/v3/cust_msts` (list with pagination), `POST /api/v3/cust_msts` (create with counter pre-hook)
- `GET /api/v3/order_msts?dealer_id=…` (hits the compound indexes defined in `models/order_msts.js:57–73`)
- `POST /api/v3/order_msts` (create + counter side effect)
- `POST /api/v3/psocs` flows (these `findOneAndUpdate` hotspots per `api_v3/services/psocs.js`)
- `GET /api/v3/dealer_custs` (large query surface)
- `GET /api/v3/invs`, `POST /api/v3/invs` (invoice generation uses aggregation)
- A `/api/dip/v1/**` route — this exercises the **`db_dip` secondary connection** from `helpers/db_conn.js:22` and the `models/dip_models/*` schemas. Critical: if the DIP URI points to a separate Atlas cluster, it must be upgraded too.

### 7.3 Dual-DB verification

`helpers/db_conn.js` creates two connections (`dbDefault` via `mongoose.connect`, `db_dip` via `mongoose.createConnection`). After the upgrade, start the app and confirm **both** log lines appear:

- `✅ Default DB Connected: …`
- `✅ Connected to db_dip: …`

If only one logs, the `db_dip` cluster hasn’t been upgraded or its SRV string is wrong.

### 7.4 Performance sanity

Run the same `k6`/`ab`/curl-loop script used for baseline metrics. MongoDB 8 generally improves aggregation and index-intersection performance; a 5–15% improvement on list endpoints is plausible but not guaranteed. Watch P95 latency on `GET /api/v3/order_msts` and `GET /api/v3/invs`.

---

## 8. Step 6 — Rollback Plan

### 8.1 If the app breaks after the package refresh (pre-Atlas upgrade)

1. `git revert` the lockfile commit.
2. `yarn install --immutable`.
3. Restart. State is fully restored — no DB side-effects.

### 8.2 If the app breaks after the Atlas upgrade but FCV is still 7.0

**Correction (2026-07 review):** Atlas does **not** support in-place major-version downgrades — Edit Configuration will not offer `7.0` once the cluster runs `8.0`, regardless of FCV. The realistic rollback is:

1. Restore the `pre-8.0-upgrade` snapshot (or a point-in-time restore from just before the incident) into a **new 7.0 cluster** (Atlas → Backups → Restore).
2. Flip `DATABASE_URI` / `DIPDB` in the production `.env` to the restored cluster's SRV string and restart the app.
3. Accept the write-loss window between the restore point and cutover (continuous backup keeps this small). Open an Atlas support case in parallel — a support-assisted rollback may be possible while FCV is still 7.0.
4. No code changes needed — driver 7.1.1 and Mongoose 9.4.1 talk to MongoDB 7.0 just as well as to 8.0 (see compat matrix in `03_mongoose_driver_upgrade.md` §8).

### 8.3 If the app breaks after FCV has been promoted to 8.0

1. Point the app at the snapshot from the pre-upgrade backup (Atlas → **Backups** → **Restore** → new cluster on 7.0).
2. Flip `DATABASE_URI` / `DIPDB` in the production `.env` to the restored cluster’s SRV string.
3. Restart the app. Accept the data loss window since the FCV promotion.
4. **This is why FCV is promoted 24–48h after the binary upgrade** — the whole window is the rollback guarantee.

### 8.4 Hard rollback artifacts required

- Atlas on-demand snapshot from the Pre-upgrade Checklist.
- Offline `mongodump` from the checklist.
- The previous `yarn.lock` (via git).
- The previous `.env.production` (store in the secret manager with a date-stamped version).

---

## 9. Rollout Order

1. **Local dev machine** — `yarn upgrade`, `yarn jest`, smoke against a local `mongodb-memory-server` (MongoDB 8 binary).
2. **Dev Atlas cluster** — upgrade to 8.0, point dev app at it, run smoke tests.
3. **Test Atlas cluster** (the one `.env.testing` points to) — upgrade, run `yarn start:test`, full manual route pass.
4. **Staging / pre-prod** if available.
5. **Production Atlas cluster** — maintenance window, snapshot, upgrade, leave FCV=7.0, bake 24–48h, promote FCV=8.0.
6. **db_dip cluster** — if separate, repeat the staged rollout in the same order.

Gates between stages:

- Dev → Test: all Jest suites green, no regression in smoke tests.
- Test → Prod: 24h of manual QA clean, no new error-log entries, P95 latency unchanged or improved.
- Prod binary → Prod FCV: 24–48h of production stability, on-call sign-off.

---

## 10. Specific Files to Review (and What to Look For)

| File                                                                 | What to check                                                                                   |
|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| `dzzlo_oms_api/package.json`                                         | `mongoose` / `mongodb` / `mongodb-memory-server` satisfy latest; no stray npm-ism.              |
| `dzzlo_oms_api/yarn.lock`                                            | `mongoose 9.4.1`, `mongodb 7.1.1`, `bson ^7.1.1` present; no duplicates.                        |
| `dzzlo_oms_api/helpers/db_conn.js`                                   | Remove dead `updatePipeline` comment; connections still event-handled; dual-DB intact.          |
| `dzzlo_oms_api/dzzlo_oms.js`                                         | Remove dead `useNewUrlParser` comment block (lines 45–53); `defaultConnectionPromise` gate kept. |
| `dzzlo_oms_api/api_v/api_constants.js`                               | `DATABASE_URI` and `DIPDB` env vars still point where expected.                                 |
| `dzzlo_oms_api/models/order_msts.js`                                 | 6 compound indexes still defined; no callback APIs; `getOTPToken` is async.                     |
| `dzzlo_oms_api/models/cust_msts.js`                                  | `pre("save")` has no `next` param.                                                              |
| `dzzlo_oms_api/models/dip_models/*.js`                               | DIP schemas still register against the `db_dip` connection.                                     |
| `dzzlo_oms_api/api_v3/services/psocs.js`                             | Heavy `findOneAndUpdate` user — smoke test its endpoints.                                       |
| `dzzlo_oms_api/api_v3/services/dealer_custs.js`                      | Another `findOneAndUpdate` hotspot (lines 202, 212, 767, 1414+).                                 |
| `dzzlo_oms_api/api_v3/services/users.js`                             | 10+ `findOneAndUpdate` calls; exercise login / profile endpoints.                               |
| `dzzlo_oms_api/api_v2/controllers/dbUpdates/**`                      | Keep `{ updatePipeline: true }` on every call — do not remove them.                              |
| `dzzlo_oms_api/test/dzzlo_oms_test.js`                               | Clean up dead comment; run once to confirm Jest boots.                                          |
| `dzzlo_oms_api/.env.production`, `.env.testing`, `.env.development`  | Confirm URIs; add backup of prior version before editing.                                       |

---

## 11. Effort and Risk Estimate

| Phase                                         | Effort        | Risk   |
|-----------------------------------------------|---------------|--------|
| Pre-upgrade checklist + backups               | 2 hours       | Low    |
| `yarn upgrade` + lockfile refresh             | 30 minutes    | Low    |
| `helpers/db_conn.js` + `dzzlo_oms.js` cleanup | 30 minutes    | Low    |
| Jest suite + investigate any fallout          | 2–4 hours     | Low-Med |
| Dev Atlas cluster 7 → 8 upgrade + smoke       | 1–2 hours     | Low    |
| Test cluster upgrade + manual route pass      | 3–4 hours     | Medium |
| Production maintenance window                 | 2 hours (incl. 30-min buffer) | Medium |
| 24–48h bake + FCV promotion                   | 15 minutes of active work | Medium |
| **Total active engineering time**             | **~1.5–2 days** across ~4 calendar days | **Overall: Low–Medium** |

**Biggest risk factor:** the Atlas 7 → 8 server upgrade, not the Node packages. The Node side is a lockfile refresh. The Atlas side is where a rollback could be needed, which is why FCV is held at 7.0 for the bake window.

---

## 12. Cross-References

- Companion research: `docs/tasks/tasks_03_mongo_search/03_mongoose_driver_upgrade.md`
- Prior migration record: `dzzlo_oms_api/docs/strategy/mongoose_9_upgrade_plan_61daa006.strategy.md`
- Project conventions: `dzzlo_oms_api/AI.md` (lines 65, 91 for Mongoose 9 specifics)
- Memory: `~/.claude/projects/.../memory/feedback_package_manager.md` (yarn, not npm)
