# Phase 5 — Shared Fixtures / Contract Layer

**Outcome:** web and app MSW fixtures are **generated from the API's seeded world**, not hand-written — so front-end mocks cannot drift from real API shapes, killing the classic "mocks pass, prod breaks" failure mode.
**Effort:** 2–3 dev-days. Depends on Phases 2 (seed extensions) and 3 (web MSW in place); the app side additionally on Phase 4.

> **TDD lens:** a mock is a *claim* about the API. Unverified claims rot. This phase makes every claim mechanically derived from the same seed world the API's own tests run against — one source of truth (✅ Q7 confirmed 2026-07-05; the alternative, front-end suites booting a locally seeded API, is rejected: it couples three repos' test runs and is 10–100× slower; the locally seeded API is reserved for the optional e2e smoke in Phase 6).

---

## 5.1 Why raw seed JSON is not enough

`test/api_v3/temp/seed/data/v3_*/` holds **collection dumps** (what's *in Mongo*). Clients never see that: they see **response envelopes** — `advancedResults` pagination wrappers, `{ success, ... }` shapes, populated refs, presenter shims (`legacy_credit_presenter` rewrites `max_cr_lmt` on the wire for old clients). Fixtures must therefore be **captured responses**, not copied documents.

## 5.2 The exporter — `dzzlo_oms_api/test/api_v3/temp/seed/export_fixtures.js` (new)

Runs like a factory: connect memory server → re-hydrate the seeded snapshot via `beforeAllHelper` → replay a curated list of requests through the in-process app (supertest + `db.dheader`, bearer where the real client uses one) → write each response body to `fixtures/api_v3/<name>.json` + a `fixtures/api_v3/fixtures.meta.json` stamp (seed snapshot date, git SHA, generation time).

```js
// test/api_v3/temp/seed/export_fixtures.js — sketch, house idiom
const supertest = require("supertest");
const app = require("../../../dzzlo_oms_test");
const request = supertest(app);
const db = require("../../../database");

const CAPTURES = [
  { name: "auth_loginrx",      run: (r) => r.post("/api/v3/auth/loginrx").send(SEEDED_CREDS) },
  { name: "orders_poso",       run: (r) => r.get("/api/v3/order_msts/a/poso").query({ /* seeded co */ }) },
  { name: "so_list",           run: (r) => r.get("/api/v3/so_msts") },
  { name: "invs_list",         run: (r) => r.get("/api/v3/invs") },
  { name: "voc_list",          run: (r) => r.get("/api/v3/voc_msts") },
  { name: "dealer_custs_list", run: (r) => r.get("/api/v3/dealer_custs") },
  // + the DIP dealer envelope dip-web's useDealerData needs (until Phase 2b, captured from a hand-maintained handler — marked in meta)
];
```

`package.json`: `"fixtures:export": "NODE_ENV=development node ./test/api_v3/temp/seed/export_fixtures.js"` (documented to run after `yarn seed`). Start with the ~6–8 envelopes the existing web/app tests consume; grow on demand — no speculative captures.

## 5.3 The consumers — `yarn fixtures:pull` in web and app

Repos are siblings inside the versioned workspace folder (`v1_78/`), so a relative copy is enough — no registry, no submodule:

```json
// dip-web/package.json + dzzlo_oms_app/package.json
"fixtures:pull": "node ./scripts/pull_fixtures.js"
```

`scripts/pull_fixtures.js`: copy `../dzzlo_oms_api/fixtures/api_v3/*.json` into `src/test/fixtures/generated/` (web) / `src/test/fixtures/generated/` (app), fail loudly if the source dir is missing or `fixtures.meta.json` is older than N days (staleness guard). Generated fixtures are **committed** in each front-end repo, so tests run without the API checkout present; the pull refreshes them.

MSW handlers switch from hand-rolled JSON to the generated files; hand-rolled fixtures remain only for error cases (401/403/500 bodies) and are marked as such.

## 5.4 The drift detector

Two mechanisms, both cheap:

1. **API side**: a contract spec `test/api_v3/features/contract/fixtures.test.js` that regenerates the captures in-memory and deep-compares against the committed `fixtures/api_v3/*.json` (ignoring volatile fields: `_id` timestamps, dates — normalize via a scrub function). If an endpoint's envelope changes, the API's own suite goes red until `yarn fixtures:export` is rerun and committed — making the contract change *visible and deliberate*.
2. **Release gate**: Phase 6's checklist includes `fixtures:export` → `fixtures:pull` → front-end suites green, so a deliberate contract change propagates before shipping, not after.

## 5.5 Verification — how we know Phase 5 is done

- `yarn seed && yarn fixtures:export` produces stable output on repeated runs (after scrubbing volatile fields).
- Web + app suites pass using only generated fixtures for happy paths.
- Deliberately change one response field in an API controller → API contract spec goes red; after re-export + pull, the corresponding front-end test sees the new shape (drift demonstrated end-to-end once, recorded in the PR).

## Phase 5 checklist

- [ ] `export_fixtures.js` + `fixtures:export` script + `fixtures/api_v3/` with `fixtures.meta.json`
- [ ] `pull_fixtures.js` + `fixtures:pull` in dip-web and dzzlo_oms_app; generated fixtures committed
- [ ] MSW handlers consume generated fixtures; hand-rolled ones limited to error cases
- [ ] Contract spec (drift detector) in the API suite
- [ ] Drift demonstrated once end-to-end (§5.5)
- [ ] Q7 answer recorded in overview (default assumed: MSW-from-seed)
