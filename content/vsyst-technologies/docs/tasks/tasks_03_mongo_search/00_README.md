# tasks_03 — MongoDB Research Package

> Research package for the DZZLO OMS team covering MongoDB version upgrades,
> search capabilities, and the full potential of MongoDB as a platform.
> Everything the team needs to decide what to upgrade, what to change, and
> what new features to build.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Nothing in this package was built as planned: no Atlas Search, `$text` index or `/search` route exists, and mongoose 9.4.1 / driver 7.1.1 are still the versions the research found. Search shipped another way (escaped `$regex` on four v3 list endpoints and the v1 vehicle lists, an in-memory `q` filter in the v4 Customers read model); next-steps checklist: 2 🟡 · 6 ⬜ · 1 ❌ · 4 ❔, plus 3 new tasks. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item                                      | Status              | What exists now (evidence)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | What is left / next step                                                                                        |
| ----------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Atlas server 7.0.31 → 8.0 (02, 04 Step 1) | ❔                  | Not visible from the repos. 02 dates 7.0's end of life at 2026-08-31 — now past. An in-repo comment still calls the cluster an Atlas M10 (`helpers/db_conn.js:8`). The test suite already runs mongod 8.2.1 (`package.json:23-27`, `.github/workflows/test.yml:25-29`).                                                                                                                                                                                                                                                                                                | User to confirm the cluster version in Atlas; if it is still 7.0, run 04 Steps 1–6 now; then T03-N1.            |
| Mongoose / driver (03, 04 Step 2)         | 🟡                  | mongoose 9.4.1, mongodb 7.1.1, bson 7.2.0, mongodb-memory-server 11.0.1 (`yarn.lock:2425-2426,4448-4466`; `package.json:44-45,54`) — the versions 03 recommended. No lockfile change for them since `e407a29` (2026-04-06).                                                                                                                                                                                                                                                                                                                                            | The Q3 2026 re-check that 03 §10 asked for is due.                                                              |
| 04 code clean-ups (§5, §6, §2 Node pin)   | ⬜                  | Dead `updatePipeline` comment still at `helpers/db_conn.js:4-5`; dead connect block still at `dzzlo_oms.js:44-53`; no `.nvmrc` or `engines` (CI pins Node 22, `.github/workflows/test.yml:18-21`). Already fine: `test/dzzlo_oms_test.js` has no dead block (rewritten by the TDD work). `serverSelectionTimeoutMS` was deliberately left at the driver's 30 s by API-3 (`helpers/db_conn.js:35-40`).                                                                                                                                                                  | One small PR: two comment deletions and a Node pin.                                                             |
| Search — API plan (05–07)                 | ⬜                  | No Atlas Search index, `$search`, `$text`, text index or `/search` route; none of 07's new files. Built instead: escaped, case-insensitive `$regex` on four v3 list endpoints (`api_v3/services/veh_trns.js:355,468`, `dvr_msts.js:426`, `users.js:195`; `7c06b0a` 2026-05-13, `2e4fd0d` 2026-06-18) and the v4 Customers `q` — an escaped `RegExp` over `cust_name`, applied in memory (`api_v4/readmodels/customers.js:72,84-88,787-791`). The 2022 branch `try/search` (api_v2 aggregate paging, no search engine) is unmerged.                                     | Re-target 07 at the v4 read-model pattern (T03-N2). Tenant scope of the v3 searches: see `X-SEC-1` in tasks_01. |
| Search — app plan (08)                    | 🟡                  | None of 08's files exist and no search endpoint is in the store. Built instead: v2 Customers searches server-side (`q`, 300 ms debounce, trimmed — `src/screens/v2/Dealer/Customers/useScreenModel.js:27,92-101`, `src/helpers/Filters/customers.js:135-139`) with cursor paging, a skeleton and a "No customers match" state; the v1 vehicle lists search server-side, debounced, through `veh_trns/paginated` (`src/screens/Customer/Vehicles/index.js:144,179-180`). Orders, Dealers and most other v1 search inputs (36 files hold one) still filter on the phone. | Each redesigned screen brings its own server search (T03-N2); cap the v2 field at 60 characters (T03-N3).       |
| 09 Tier 1 quick wins (checklist below)    | ⬜                  | No TTL index, partial index or change stream (`expireAfterSeconds`, `partialFilterExpression`, `.watch(`: 0 hits in code). API-1 added four compound B-tree indexes instead (see `X-REL-2` in tasks_01). The dealer-dashboard `$facet` is superseded by v4 read models (`api_v4/lib/compose.js` `runParallel`).                                                                                                                                                                                                                                                        | TTL for `logs` is API-5 (see `X-PERF-2` in tasks_01); real-time is tasks_02's websocket plan.                   |
| Research docs 01, 02, 05, 06, 09          | research — no tasks | Banner on each; facts about our code re-checked. Corrected inline: `order_no` is `cust_msts.cust_podgt` + 1, not a `counters` `$inc` (`api_v3/services/order_msts.js:785-786,847`); no TTL index exists (the OTP lives on the user, `models/users.js:114-115`). Atlas tier, region and version: ❔.                                                                                                                                                                                                                                                                    | —                                                                                                               |

---

## Goal of this research package

The user asked four questions:

1. **Can we update our server to the latest MongoDB / Mongoose version? Is
   it safe?** — What's new, what breaks, how risky is the upgrade.
2. **What files do we need to change in the dzzlo_oms_api project?** — A
   concrete, file-by-file change list.
3. **What features do we get?** — Both from the version bump and from
   MongoDB capabilities we aren't using yet.
4. **Can we implement search through MongoDB?** — Teach the team about
   MongoDB search options and plan concrete implementations in both the
   Node API and the React Native app.

This package is organized into 10 files (including this index). Each file
addresses one slice of the overall question so the team can read in any
order without getting overwhelmed.

---

## Files in this folder

| #   | File                                    | Topic                                                           |
| --- | --------------------------------------- | --------------------------------------------------------------- |
| 00  | `00_README.md`                          | This index                                                      |
| 01  | `01_mongodb_overview.md`                | MongoDB fundamentals teaching guide                             |
| 02  | `02_mongodb_version_history.md`         | MongoDB 7.0 vs 8.0, upgrade safety                              |
| 03  | `03_mongoose_driver_upgrade.md`         | Mongoose + Node driver upgrade research                         |
| 04  | `04_api_upgrade_file_changes.md`        | File-by-file changes for the dzzlo_oms_api upgrade              |
| 05  | `05_mongodb_search_guide.md`            | MongoDB search teaching guide (`$regex`, `$text`, Atlas Search) |
| 06  | `06_atlas_search_deep_dive.md`          | Atlas Search deep dive                                          |
| 07  | `07_search_implementation_api.md`       | API implementation plan (vehicles, orders, dealers)             |
| 08  | `08_search_implementation_app.md`       | React Native app implementation plan                            |
| 09  | `09_mongodb_full_potential_features.md` | Brainstorm of advanced MongoDB features                         |

---

## TL;DR of each file

### 01 — MongoDB overview

A teaching guide that explains MongoDB's document model, BSON, replica
sets, the aggregation pipeline, indexes, and how Mongoose fits on top.
Read this first if you're new to MongoDB or want to understand concepts
referenced throughout the rest of the package.

### 02 — Version history (7.0 vs 8.0)

Walks through what changed between MongoDB 7.0 (currently on 7.0.31)
and MongoDB 8.0. Covers new features, breaking changes, performance
improvements, and an upgrade-safety assessment specifically for DZZLO.
Answers: "Is it safe to jump to 8.0?"

### 03 — Mongoose + driver upgrade

Covers the Mongoose ODM (currently 9.4.1) and the underlying Node.js
MongoDB driver. Lists breaking changes from older versions, the minimum
Node.js version required, and Mongoose-specific caveats (strict mode
changes, query projection behavior, etc.). Answers the Node-layer half
of the upgrade question.

### 04 — API file changes for the upgrade

The concrete, file-by-file change list for the `dzzlo_oms_api` project.
`package.json` bumps, connection-option removals, deprecated API
replacements, any Mongoose schema tweaks, and tests to run post-upgrade.
Everything a developer needs to open a PR.

### 05 — MongoDB search teaching guide

Explains the three main ways to search in MongoDB: `$regex`, the legacy
`$text` index, and Atlas Search. Compares them on features, performance,
relevance ranking, and cost. Answers "Teach me about MongoDB search."

### 06 — Atlas Search deep dive

A detailed look at Atlas Search — the Lucene-based full-text engine
built into MongoDB Atlas. Covers index definitions, query operators,
autocomplete, fuzzy matching, highlighting, faceting, and relevance
tuning. Builds on file 05.

### 07 — Search implementation plan (API)

A concrete implementation plan for adding Atlas Search to the
`dzzlo_oms_api` backend. Covers the search index definitions for
vehicles, orders, and dealers; the new Express routes; the aggregation
pipelines; and how to wire it into the existing controllers.

### 08 — Search implementation plan (React Native app)

The mobile-side companion to file 07. Covers the unified search screen,
debounced input, result rendering for different entity types, result
highlighting, and caching strategy. Wraps up the "search in the app"
question.

### 09 — MongoDB full potential features

A brainstorm of advanced MongoDB capabilities DZZLO isn't using yet —
change streams, transactions, time series, geospatial, triggers,
vector search, etc. Each entry includes a DZZLO-specific use case, a
code sketch, and an effort rating. Ends with a "if you only do 3
things" priority list.

---

## Which file answers which question?

A quick lookup for the original questions the user asked:

| Question                                                  | Files                                                                                       |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| "Can we update our server to latest version? Is it safe?" | **02** (version diff) + **03** (Mongoose/driver) + **04** (file changes)                    |
| "What files do we need to change in the api project?"     | **04** (API upgrade) + **07** (API search implementation)                                   |
| "What features do we get from upgrading?"                 | **02** (version features) + **09** (untapped platform features)                             |
| "Can we implement search through MongoDB?"                | **05** (teaching) + **06** (Atlas Search deep dive) + **07** (API impl) + **08** (app impl) |
| "Teach me about MongoDB search"                           | **05** + **06**                                                                             |
| "Integrate MongoDB search in the app"                     | **07** + **08**                                                                             |
| "What else can we do with MongoDB?"                       | **09**                                                                                      |

---

## Reading order

### For beginners (new to MongoDB)

1. **01** — MongoDB overview (concepts)
2. **05** — Search teaching guide (`$regex`, `$text`, Atlas Search)
3. **02** — What's new in 8.0
4. **06** — Atlas Search deep dive
5. **09** — Full potential features (skim for ideas)
6. **03** — Mongoose upgrade details
7. **04** — API file changes
8. **07** + **08** — Implementation plans

### For experienced Node + Mongoose devs

1. **02** — What's new, what breaks (skim 8.0 release notes)
2. **03** — Mongoose/driver changes you need to know
3. **04** — Concrete file changes (this is the PR checklist)
4. **06** — Atlas Search deep dive (skip 05 if you already know `$regex`/`$text`)
5. **07** + **08** — Implementation plans
6. **09** — Brainstorm of advanced features

### For product / non-technical stakeholders

1. **00** — This README (overview)
2. **02** — Version features (what the team will unlock)
3. **09** — Full potential features (the "wow" list, especially the
   "if you only do 3 things" section at the end)
4. Skim **07** and **08** for the search feature's scope

### For the developer actually doing the upgrade

1. **02** — Understand what changes between versions
2. **03** — Understand what changes in Mongoose / driver
3. **04** — Follow the file-by-file checklist
4. Run tests, deploy to staging, monitor, promote to production
5. Afterwards: read **09** and pick 1-3 quick wins for the next sprint

---

## Next steps checklist

After reading this package, the team should:

- [ ] Decide whether to upgrade MongoDB server to 8.0 (informed by **02**) — **2026-10-01:** ❔ not visible from the repos; 7.0's end of life (2026-08-31) has passed — user to confirm in Atlas.
- [ ] Decide whether to upgrade Mongoose/driver (informed by **03**) — **2026-10-01:** 🟡 stayed on 9.4.1 / 7.1.1 as 03 advised (`yarn.lock:4456-4466`); the Q3 2026 re-check is due.
- [ ] Open a PR in `dzzlo_oms_api` for the upgrade (using the checklist in **04**) — **2026-10-01:** ⬜ no such PR; 04's clean-ups still open (`helpers/db_conn.js:4-5`, `dzzlo_oms.js:44-53`).
- [ ] Test the upgrade on a staging cluster before touching production — **2026-10-01:** ❔ Atlas-side; the Jest suite already runs mongod 8.2.1 (`package.json:23-27`).
- [ ] Back up the production database before the upgrade — **2026-10-01:** ❔ Atlas-side.
- [ ] Decide whether to adopt Atlas Search (informed by **05** + **06**) — **2026-10-01:** ⬜ not adopted and no decision recorded; search is escaped `$regex` (v3) and an in-memory filter (v4).
- [ ] Scope the API + app search work as a sprint (using **07** + **08**) — **2026-10-01:** 🟡 search came piecemeal (v3 lists 2026-05/06, v4 Customers 2026-09); 07/08 themselves not started — see T03-N2.
- [ ] Pick 1-3 quick-win items from **09** Tier 1 to bundle with the upgrade: — **2026-10-01:** ⬜ none picked.
  - [ ] TTL indexes on OTP / session / draft collections — **2026-10-01:** ⬜ no TTL index anywhere; OTPs sit on the user document (`models/users.js:114-115`).
  - [ ] Partial indexes on unpaid invoices / active dealers / pending orders — **2026-10-01:** ⬜ none (`partialFilterExpression`: 0 hits).
  - [ ] Aggregation `$facet` for the dealer dashboard — **2026-10-01:** ❌ superseded — v4 builds one read model per screen from parallel reads (`api_v4/lib/compose.js`).
  - [ ] Change streams for live order notifications — **2026-10-01:** ⬜ none (`.watch(`: 0 hits); `socket.io` is in `package.json` but unused.
- [ ] Review the roadmap in **09** and put the Tier 2/3 items on the backlog — **2026-10-01:** ❔ a planning step, not visible in the repos.

---

## Errata — correctness & security review (2026-07-02)

A review pass was applied across the package. The load-bearing fixes, in case
you read an older copy elsewhere:

- **02 — versions**: MongoDB 7.0's EOL corrected to **Aug 31, 2026** (an
  earlier draft said 2027) — re-verify on the lifecycle page; the upgrade is
  near-term work, not deferrable. `$rankFusion` is 8.1+ (rapid), not 8.0 GA.
- **02/04 — rollback**: Atlas does **not** support in-place major-version
  downgrades; the production rollback plan is restore-from-snapshot. The
  upgrade-rehearsal cluster must be M10+ (shared tiers can't restore
  snapshots or pin versions).
- **05 — regex**: collation indexes do **not** make `$regex` case-insensitive
  (`$regex` is not collation-aware) — that section was rewritten with a
  working alternative (lowercased shadow field, or `$text`/Atlas Search).
- **06 — Atlas Search types**: `equals`/`in` on strings requires the
  **`token`** field type; `stringFacet` is facet-only (map filter+facet
  fields with both types). Tier table updated — M2/M5/Serverless were
  replaced by Flex, and Search was never available on Serverless.
- **07 — security**: routes must sit behind auth with **server-side tenant
  scoping** (dealer/customer ids derived from `req.user`, not the query
  string — IDOR otherwise); `city`/`state` now regex-escaped; statuses
  lowercased to match the token normalizer; numeric `order_no` handled on
  the Atlas path; empty compound clauses pruned; `page` clamped; trust-proxy
  note for the rate limiter; unused fallback `$text` indexes replaced with
  the B-tree indexes the code actually uses; `DATABASE_URI` env-var fix;
  order responses must exclude OTP/token fields.
- **08 — app**: client-side `dealerId`/`custId` args are convenience only;
  the API enforces scoping from the auth token.
- **09 — dead products**: Atlas App Services (HTTPS endpoints / Data API)
  and Atlas Device Sync / Realm reached **EOL Sept 30, 2025** — sections
  C3/D1 rewritten (Triggers survive). `$jsonSchema` sketch flagged as not
  matching the real schema; vector-search filter-field and `$project` fixes;
  time-series storage/granularity claims corrected.

---

## Conventions used in this package

- **Collection names** follow the existing DZZLO schema:
  `veh_msts`, `order_msts`, `dealer_msts`, `cust_msts`, `prod_msts`,
  `dvr_msts`, `so_msts`, `invs`, `pay_trns`, `rate_msts`, `voc_msts`,
  `veh_reqs`, `veh_trns`.
- **Code snippets** are illustrative, not copy-paste-ready. Adapt to
  the actual project layout.
- **Effort ratings** in file 09 are rough: low = hours, medium = days,
  high = weeks.
- **Versions referenced** are current as of the research date
  (2026-04-11).

---

_Maintainers: DZZLO engineering team. Start with whichever file answers
your current question — this package is designed to be read piecewise._

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID     | Task                                                                                                                                                                                                                                                                                                                                    | Why (evidence)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Project   | Size | Depends on                                                                                                         |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- | ------------------------------------------------------------------------------------------------------------------ |
| T03-N1 | 🆕 ❔ Make the test server match production: once the Atlas version is known, pin `config.mongodbMemoryServer.version` and the CI cache key to the production line — or upgrade Atlas to 8.x so the two agree.                                                                                                                          | The suite and the v4 performance probe run mongod 8.2.1 (`package.json:23-27`, `.github/workflows/test.yml:25-29`, `docs/v4-performance.md:28`), while this research recorded Atlas on 7.0.31. 8.0 changed query semantics (02 §7.1), and the probe's F-1 finding is stated for mongod 8.x (`docs/v4-performance.md:152`).                                                                                                                                                                                            | API       | XS   | The Atlas version (❔ — the user can read it in Atlas); ideally 04's upgrade first                                 |
| T03-N2 | 🆕 Re-target 07/08 at the v4 read-model pattern before the next v2 screen that searches a large collection: `q` in the screen's POST body (house validator), tenant from the token, the per-user `/screens` limiter, `maxTimeMS`; per collection, choose an index-backed anchored prefix (e.g. uppercase `veh_reg_no`) or Atlas Search. | v4 Customers loads every relation and runs 8 more reads on each request, then filters `q` in memory (`api_v4/readmodels/customers.js:655-716,787-791`) — fine at today's relation counts (133.8–137.5 ms p95 at 2,000 relations, `docs/v4-performance.md:226`) but not for per-dealer orders or invoices (the perf seed has 300,000 SOs for one dealer, `docs/v4-performance.md:6`). The v3 searches are unanchored `$regex` (`api_v3/services/veh_trns.js:355,468`); v1 still has about 36 files with search inputs. | API + app | M    | The redesign's choice of the next screen that searches (Customer › Dealers, the next one in its backlog, is small) |
| T03-N3 | 🆕 Cap the v2 Customers search at the contract's 60 characters (`maxLength` on `SearchRow`'s input, or a slice in `toRequestBody`) and pin it with a Tier 3 test.                                                                                                                                                                       | The API refuses a 61-character `q` with 400 `VALIDATION` (`api_v4/schemas/customers.js:48`, `api_v4/lib/validate.js:237-238`, `test/api_v4/screens/customers.test.js:536-537`). The app does not limit the field (`src/screens/v2/Dealer/Customers/components/SearchRow.js:104-123`; `src/helpers/Filters/customers.js:138-139` only trims), so a long pasted term shows "Some values aren't valid…" with a Retry that repeats the 400 (`useScreenModel.js:199`, `components/CustomerList.js:128-135`).               | app       | XS   | —                                                                                                                  |
