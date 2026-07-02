# tasks_03 — MongoDB Research Package

> Research package for the DZZLO OMS team covering MongoDB version upgrades,
> search capabilities, and the full potential of MongoDB as a platform.
> Everything the team needs to decide what to upgrade, what to change, and
> what new features to build.

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

- [ ] Decide whether to upgrade MongoDB server to 8.0 (informed by **02**)
- [ ] Decide whether to upgrade Mongoose/driver (informed by **03**)
- [ ] Open a PR in `dzzlo_oms_api` for the upgrade (using the checklist in **04**)
- [ ] Test the upgrade on a staging cluster before touching production
- [ ] Back up the production database before the upgrade
- [ ] Decide whether to adopt Atlas Search (informed by **05** + **06**)
- [ ] Scope the API + app search work as a sprint (using **07** + **08**)
- [ ] Pick 1-3 quick-win items from **09** Tier 1 to bundle with the upgrade:
  - [ ] TTL indexes on OTP / session / draft collections
  - [ ] Partial indexes on unpaid invoices / active dealers / pending orders
  - [ ] Aggregation `$facet` for the dealer dashboard
  - [ ] Change streams for live order notifications
- [ ] Review the roadmap in **09** and put the Tier 2/3 items on the backlog

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
