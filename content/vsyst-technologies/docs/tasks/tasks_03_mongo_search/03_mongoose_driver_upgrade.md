# 03 — Mongoose and MongoDB Node Driver: Version Audit and Upgrade Assessment

**Date:** 2026-04-11
**Scope:** `dzzlo_oms_api` — Node.js backend connecting to MongoDB Atlas
**Prepared by:** Agent 2 (API upgrade research)

---

## 1. Executive Summary

The `dzzlo_oms_api` project is already running on the **current `latest` tag** of both `mongoose` and the `mongodb` native driver. The Mongoose 8 → 9 migration is complete (see `dzzlo_oms_api/docs/strategy/mongoose_9_upgrade_plan_61daa006.strategy.md`) and `updatePipeline: true` has been wired in globally. There is **no major version bump pending**. The remaining work is a routine minor-version refresh to pick up patch fixes published since 9.4.1 / 7.1.1 and, more importantly, to plan the MongoDB server upgrade from Atlas 7.0.31 → 8.0 so the stack aligns on MongoDB 8.

| Package    | Installed (package.json) | Current `latest` on npm | Action              |
|------------|---------------------------|-------------------------|---------------------|
| `mongoose` | `^9.4.1`                  | `9.4.1` (2026-04-03)    | Already at latest   |
| `mongodb`  | `^7.1.1`                  | `7.1.1`                 | Already at latest   |

Verdict: **Safe to keep the caret range as-is and run `yarn upgrade mongoose mongodb` to refresh the lockfile.** The biggest risk isn’t the Node packages — it’s the Atlas 7 → 8 server upgrade, which is what actually unlocks MongoDB 8 features.

---

## 2. Current State (verified from repo)

From `dzzlo_oms_api/package.json` (lines 30–32):

```json
"mongodb": "^7.1.1",
"mongoose": "^9.4.1",
```

Also relevant:

- `dzzlo_oms_api/helpers/db_conn.js` uses both `mongoose.connect(databaseURI)` and `mongoose.createConnection(database_dip)` — dual-DB setup.
- `dzzlo_oms_api/dzzlo_oms.js` (line 12) imports mongoose only for `mongoose.disconnect()` during graceful shutdown.
- `updatePipeline: true` was the Mongoose 9 migration hook. It is now declared in-line on each `api_v2/controllers/dbUpdates/**` call (see grep below) rather than globally; the global `mongoose.set("updatePipeline", true)` line in `helpers/db_conn.js:5` is currently commented out. This is consistent with AI.md line 91 noting the migration is complete, but the global set was moved to per-call opts.
- `dzzlo_oms_api/docs/strategy/mongoose_9_upgrade_plan_61daa006.strategy.md` records the 8 → 9 migration as fully `completed`.
- Runtime: `node --version` on this machine reports `v24.14.1`. Mongoose 9 / driver 7 require Node **≥ 20.19.0**, so runtime is well above floor.
- Atlas server: **7.0.31** (per task brief).

---

## 3. Latest Versions on npm (as of 2026-04-11)

| Package    | Latest  | Published   | Engines (node) |
|------------|---------|-------------|----------------|
| `mongoose` | `9.4.1` | 2026-04-03  | `>=20.19.0`    |
| `mongodb`  | `7.1.1` | ~2026-04    | `>=20.19.0`    |

Sources:
- `https://registry.npmjs.org/mongoose/latest` → confirms 9.4.1, deps include `mongodb: ~7.1`, `bson`, `kareem 3.2.0`, `mquery 6.0.0`, `mpath 0.9.0`, `sift 17.1.3`.
- `https://registry.npmjs.org/mongodb/latest` → confirms 7.1.1, deps include `bson ^7.1.1`, `@mongodb-js/saslprep ^1.3.0`, `mongodb-connection-string-url ^7.0.0`.
- `https://github.com/Automattic/mongoose/blob/master/CHANGELOG.md` → confirms 9.4.1 is the latest published release.

**Mongoose 10.x:** Not released yet. No 10.0.0 entry in the CHANGELOG and no announced timeline as of April 2026. The 9.x line is still the active release train and receives features (9.4.0 added union schema validation and populated-doc TS improvements on 2026-04-03).

**MongoDB driver 8.x:** Not released yet. 7.1.x is the current line. The v7 major was the most recent driver break (raised Node floor to 20.19, bumped `bson`/`mongodb-connection-string-url` to 7.0).

---

## 4. Changelog Highlights — 9.x Line (since the project adopted 9)

Pulled from the Mongoose CHANGELOG:

- **9.0.0 (2025-11-21)** — Major. Removed `next()` from pre-middleware, update pipelines behind opt-in (`updatePipeline: true`), `isValidObjectId` rejects numbers, `FilterQuery` → `QueryFilter` (TS), Node 18+ floor (later raised to 20.19 alongside driver 7). This is the release this repo migrated onto.
- **9.0.1 / 9.0.2 (Dec 2025)** — Stability + bug fixes post-9.0.0.
- **9.1.0 (2025-12-29)** — Model enhancements and perf optimizations.
- **9.1.1 – 9.1.6 (Jan–Feb 2026)** — Patch fixes.
- **9.2.0 (2026-02-09)** — Document/model perf improvements, streamlined validation, collection handling.
- **9.2.1 – 9.2.4 (Feb–Mar 2026)** — Patches.
- **9.3.0 (2026-03-10)** — Inline discriminators, new aggregate helper `pipelineForUnionWith()`, improved default handling on upsert.
- **9.3.1 – 9.3.3** — Error handling standardisation and docs.
- **9.4.0 (2026-04-03)** — Perf tweaks, union schema validation, TS improvements for populated docs.
- **9.4.1 (2026-04-03)** — Revert of a setDefaultsOnInsert behavior change from 9.4.0.

**Note on 9.4.1 specifically:** it’s a revert patch — do NOT skip it. Pinning to 9.4.0 would ship the regression.

---

## 5. Breaking Changes That Mattered on 8 → 9 (already handled)

From `https://mongoosejs.com/docs/migrating_to_9.html` and confirmed against `dzzlo_oms_api/docs/strategy/mongoose_9_upgrade_plan_61daa006.strategy.md`:

| Breaking change                                               | Relevance to `dzzlo_oms_api` | Handled? |
|---------------------------------------------------------------|------------------------------|----------|
| Pre middleware: `next()` removed                              | `users.js`, `cust_msts.js`, `dealer_msts.js`, `invs.js` | Yes |
| Update pipelines opt-in (`updatePipeline: true`)              | ~12 files in `api_v2/controllers/dbUpdates/**` | Yes (per-call) |
| `Document.prototype.updateOne` no longer accepts callbacks    | None found                   | N/A |
| `mongoose.isValidObjectId()` rejects numbers                  | None found                   | N/A |
| `background` index option removed                             | None used                    | N/A |
| `skipId` third-arg boolean removed from Model/Document        | Not used                     | N/A |
| `useDb()` `noListener` option removed                         | Not used                     | N/A |
| UUID returns `bson.UUID` instance                             | No UUID schema types         | N/A |
| `FilterQuery` → `QueryFilter` (TS only)                       | Plain JS project             | N/A |
| Node.js ≥ 20.19                                               | Runtime is Node 24.14        | Yes |

The only residual trace from the migration is that `helpers/db_conn.js` line 5 still has the **commented-out** `mongoose.set("updatePipeline", true)`. It’s noise, not a bug.

---

## 6. Mongoose 9 → 10 Breaking Changes

**None to plan for.** Mongoose 10.0.0 has not been released and the repo’s CHANGELOG has no pre-release tag at the time of this writing. Re-check quarterly — if/when 10.0 drops, its migration guide at `mongoosejs.com/docs/migrating_to_10.html` will be the authoritative source.

## 7. MongoDB Node Driver 7 → 8 Breaking Changes

**None to plan for.** Driver 8.0 has not been released. Driver 7 is the current major and is still receiving patches. Re-evaluate if/when 8.0 announcement lands (typically previewed in the `node-mongodb-native` GitHub releases page).

---

## 8. Compatibility Matrix — MongoDB Server 8.0

Sources: `https://mongoosejs.com/docs/compatibility.html` and MongoDB driver docs.

| Component              | Min version for MongoDB 8.0 server |
|------------------------|------------------------------------|
| `mongoose`             | `^8.7.0` or `^9.0.0`               |
| `mongodb` node driver  | `^6.10.0` or any `^7.x`            |
| Node.js runtime        | `>=20.19.0` (driver 7 requirement) |

Our stack: mongoose `^9.4.1` + mongodb `^7.1.1` + Node 24 → **fully compatible with MongoDB 8.0**.

For completeness, both currently installed packages are also fully compatible with the 7.0.31 Atlas cluster we’re running today, so you can bump driver/Mongoose independently of the Atlas upgrade — the order doesn’t matter.

---

## 9. Is It Safe to Bump? — Risk Assessment

**The “bump” is effectively a lockfile refresh**, because we already satisfy `^9.4.1` / `^7.1.1`. Risks:

| Risk                                                                 | Likelihood | Impact | Notes |
|----------------------------------------------------------------------|------------|--------|-------|
| `setDefaultsOnInsert` regression if lockfile was pinned to 9.4.0     | Low        | Medium | Fixed by 9.4.1 — run `yarn upgrade` to pick up the revert. |
| Transitive bump of `bson` affecting BSON serialization of `Decimal128`, `Date`, `ObjectId` | Low | Medium | BSON 7 has been stable through 9.x; our models use plain types — low exposure. |
| Dev dependency `mongodb-memory-server ^11.0.1` downloads a mismatched mongod binary | Low | Low | MMS 11 targets MongoDB 8 by default, aligning with the Atlas upgrade. |
| Mongoose 9.2+ validation tightening catches previously-silent bugs   | Low        | Low    | Our schemas are conservative; run the full Jest suite once. |
| Existing `api_v1` / `api_v2` legacy callback code surfaces a regression | Low     | Low    | `api_v1` is commented out in `dzzlo_oms.js:107`; `api_v2` dbUpdates already carry per-call `updatePipeline: true`. |

**Overall: LOW risk** — this is a routine minor refresh. The real variable is the Atlas 7 → 8 server migration, which is covered in the companion doc `04_api_upgrade_file_changes.md`.

---

## 10. Recommended Target Versions

| Package    | Current caret | Target caret | Concrete version at install time |
|------------|---------------|--------------|----------------------------------|
| `mongoose` | `^9.4.1`      | `^9.4.1`     | `9.4.1`                          |
| `mongodb`  | `^7.1.1`      | `^7.1.1`     | `7.1.1`                          |
| `mongodb-memory-server` (dev) | `^11.0.1` | `^11.0.1` | `11.x` latest |

**Action:** Do not edit `package.json`. Run `yarn upgrade mongoose mongodb mongodb-memory-server` to refresh `yarn.lock`, then `yarn jest` the suite. Commit the lockfile change.

**Do NOT** bump to mongoose 10 or mongodb 8 — they don’t exist yet. Revisit this doc in Q3 2026.

---

## 11. Known Issues / Community Reports

- **9.4.0 `setDefaultsOnInsert` regression** — reverted in 9.4.1. Anyone on 9.4.0 should move to 9.4.1 immediately.
- **Mongoose 8.x End-of-Life** — per `mongoosejs.com/docs/version-support.html`, Mongoose 8.x continues to get features/fixes until at least 2026-02-01, then security-only. We’re already off 8.x, so unaffected.
- **Update pipeline opt-in friction** — community has reported that migrating large `api_v2`-style codebases to per-call `updatePipeline: true` is tedious. Our repo carries this on every call site, which is the officially supported pattern.
- **`isValidObjectId(number)` returning false** — caught historically, fixed by not passing numbers; grep confirms no such call sites in this repo.
- **BSON 7 `Decimal128` JSON serialization** quirks — unchanged in 7.1.x; not observed in our code because we store money as `Number` (`order_msts.js` uses `set: function(v) { return (Math.round(v * 100) / 100).toFixed(2); }`).

---

## 12. Source Links

- `https://registry.npmjs.org/mongoose/latest` — latest mongoose metadata
- `https://registry.npmjs.org/mongodb/latest` — latest mongodb driver metadata
- `https://mongoosejs.com/docs/migrating_to_9.html` — Mongoose 9 migration guide
- `https://mongoosejs.com/docs/compatibility.html` — Mongoose ↔ MongoDB server matrix
- `https://github.com/Automattic/mongoose/blob/master/CHANGELOG.md` — full Mongoose changelog
- `https://github.com/Automattic/mongoose/releases` — Mongoose GitHub releases
- `https://www.mongodb.com/docs/drivers/node/current/reference/release-notes/` — Node driver release notes
- `https://mongoosejs.com/docs/version-support.html` — Mongoose LTS / support policy

## 13. Cross References (this repo)

- `dzzlo_oms_api/package.json` — dependency declarations
- `dzzlo_oms_api/helpers/db_conn.js` — connection setup
- `dzzlo_oms_api/dzzlo_oms.js` — entry point and graceful shutdown
- `dzzlo_oms_api/docs/strategy/mongoose_9_upgrade_plan_61daa006.strategy.md` — prior 8 → 9 migration record
- `dzzlo_oms_api/AI.md` — lines 65, 91 document the Mongoose 9 conventions
- Companion doc: `docs/tasks/tasks_03_mongo_search/04_api_upgrade_file_changes.md` — file-by-file upgrade plan
