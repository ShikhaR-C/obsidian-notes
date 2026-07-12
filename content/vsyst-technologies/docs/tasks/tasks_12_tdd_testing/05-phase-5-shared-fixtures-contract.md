# Phase 5 — Shared Fixtures / Contract Layer

**Outcome:** web and app MSW fixtures are **generated from the API's seeded world**, not hand-written — so front-end mocks cannot drift from real API shapes, killing the classic "mocks pass, prod breaks" failure mode.
**Effort:** 2–3 dev-days. Depends on Phases 2 (seed extensions) and 3 (web MSW in place); the app side additionally on Phase 4.

> **TDD lens:** a mock is a _claim_ about the API. Unverified claims rot. This phase makes every claim mechanically derived from the same seed world the API's own tests run against — one source of truth (✅ Q7 confirmed 2026-07-05; the alternative, front-end suites booting a locally seeded API, is rejected: it couples three repos' test runs and is 10–100× slower; the locally seeded API is reserved for the optional e2e smoke in Phase 6).

---

## 5.1 Why raw seed JSON is not enough

`test/api_v3/temp/seed/data/v3_*/` holds **collection dumps** (what's _in Mongo_). Clients never see that: they see **response envelopes** — `advancedResults` pagination wrappers, `{ success, ... }` shapes, populated refs, presenter shims (`legacy_credit_presenter` rewrites `max_cr_lmt` on the wire for old clients). Fixtures must therefore be **captured responses**, not copied documents.

## 5.2 The exporter — `dzzlo_oms_api/test/api_v3/temp/seed/export_fixtures.js` (new)

Runs like a factory: connect memory server → re-hydrate the seeded snapshot via `beforeAllHelper` → replay a curated list of requests through the in-process app (supertest + `db.dheader`, bearer where the real client uses one) → write each response body to `fixtures/api_v3/<name>.json` + a `fixtures/api_v3/fixtures.meta.json` stamp (seed snapshot date, git SHA, generation time).

```js
// test/api_v3/temp/seed/export_fixtures.js — sketch, house idiom
const supertest = require("supertest")
const app = require("../../../dzzlo_oms_test")
const request = supertest(app)
const db = require("../../../database")

const CAPTURES = [
  { name: "auth_loginrx", run: (r) => r.post("/api/v3/auth/loginrx").send(SEEDED_CREDS) },
  {
    name: "orders_poso",
    run: (r) =>
      r.get("/api/v3/order_msts/a/poso").query({
        /* seeded co */
      }),
  },
  { name: "so_list", run: (r) => r.get("/api/v3/so_msts") },
  { name: "invs_list", run: (r) => r.get("/api/v3/invs") },
  { name: "voc_list", run: (r) => r.get("/api/v3/voc_msts") },
  { name: "dealer_custs_list", run: (r) => r.get("/api/v3/dealer_custs") },
  // + the DIP dealer envelope dip-web's useDealerData needs (until Phase 2b, captured from a hand-maintained handler — marked in meta)
]
```

`package.json`: `"fixtures:export": "NODE_ENV=development node ./test/api_v3/temp/seed/export_fixtures.js"` (documented to run after `yarn seed`). Start with the ~6–8 envelopes the existing web/app tests consume; grow on demand — no speculative captures.

## 5.3 The consumers — `yarn fixtures:pull` in web and app

Repos are siblings inside the versioned workspace folder (currently `v1_79/`), so a relative copy is enough — no registry, no submodule:

```json
// dip-web/package.json + dzzlo_oms_app/package.json
"fixtures:pull": "node ./scripts/pull_fixtures.js"
```

`scripts/pull_fixtures.js`: copy `../dzzlo_oms_api/fixtures/api_v3/*.json` into `src/test/fixtures/generated/` (web) / `src/test/fixtures/generated/` (app), fail loudly if the source dir is missing or `fixtures.meta.json` is older than N days (staleness guard). Generated fixtures are **committed** in each front-end repo, so tests run without the API checkout present; the pull refreshes them.

MSW handlers switch from hand-rolled JSON to the generated files; hand-rolled fixtures remain only for error cases (401/403/500 bodies) and are marked as such.

## 5.4 The drift detector

Two mechanisms, both cheap:

1. **API side**: a contract spec `test/api_v3/features/contract/fixtures.test.js` that regenerates the captures in-memory and deep-compares against the committed `fixtures/api_v3/*.json` (ignoring volatile fields: `_id` timestamps, dates — normalize via a scrub function). If an endpoint's envelope changes, the API's own suite goes red until `yarn fixtures:export` is rerun and committed — making the contract change _visible and deliberate_.
2. **Release gate**: Phase 6's checklist includes `fixtures:export` → `fixtures:pull` → front-end suites green, so a deliberate contract change propagates before shipping, not after.

## 5.5 Verification — how we know Phase 5 is done

- `yarn seed && yarn fixtures:export` produces stable output on repeated runs (after scrubbing volatile fields).
- Web + app suites pass using only generated fixtures for happy paths.
- Deliberately change one response field in an API controller → API contract spec goes red; after re-export + pull, the corresponding front-end test sees the new shape (drift demonstrated end-to-end once, recorded in the PR).

## Phase 5 checklist

- [x] `export_fixtures.js` + `fixtures:export` script + `fixtures/api_v3/` with `fixtures.meta.json` (6 envelopes)
- [x] `pull_fixtures.js` + `fixtures:pull` in dip-web and dzzlo_oms_app; generated fixtures written to each tree
- [x] MSW handlers consume generated fixtures — **app** swaps its login mock to the generated `auth_loginrx.json`; error cases stay hand-rolled. **dip-web** wires the plumbing only (see notes)
- [x] Contract spec (drift detector) in the API suite — `test/api_v3/features/contract/fixtures.test.js`
- [x] Drift demonstrated once end-to-end (§5.5) — recorded below
- [x] Q7 confirmed: MSW-from-seed (already recorded in overview)

## Phase 5 — implementation notes (executed 2026-07-10, agent team)

**Result — all green, nothing committed:** API `yarn test` **668** (662 + 6 contract), app **337**, web **32**. Each repo's only production touch remains the authorized `makeStore()` (Phases 3–4); Phase 5 added only `test/`, `fixtures/`, `scripts/`, and one `package.json` script line per repo.

**Split forced by the DIP constraint (recon-confirmed):**

- **App** (`dzzlo_oms_app`) talks `/api/v3` exclusively → it is the **full contract participant**. The exporter produces exactly what it consumes; its login test now asserts against the real generated envelope.
- **dip-web** talks `/api/dip/v1` exclusively, and DIP is **not mountable** in the v3 test app (Phase 2 §2.6) → it has **zero v3-backed fixtures**. It wires the `fixtures:pull` plumbing + commits the generated dir for the future, and its DIP fixtures stay **hand-rolled** (marked in `src/test/fixtures/README.md`). This matches §5.2's own "hand-maintained until Phase 2b" note.

**Fixtures generated** (`fixtures/api_v3/`, from seed `v3_2026-07-08`): `auth_loginrx` (bare `{success,token,user,company,expiresIn}`), `auth_updaterx` (bare `{success,user,company}`), `orders_poso` / `invoices_list` / `vouchers_list` (`{success,count,pagination,data}`), `dealer_custs_list` (`{success,count,data}`), + `fixtures.meta.json` (seed date, git SHA, gen time, capture names). A shared `fixtures.captures.js` module drives BOTH the exporter and the contract spec (DRY). **Endpoint corrections found while building:** `/api/v3/dealer_custs` (GetMultiple, needs `?dealer_id=`) is served by `dealer_custs_v1.js` (the `dealer_custs.js` routes mount at `/relations`); invoices list = `GET /invs/app/get`; vouchers list = `POST /voc_msts/app/get`.

**Drift detector:** the contract spec re-runs the captures in-memory and deep-compares against the committed fixtures after a `scrub()` that normalizes everything which legitimately varies between runs, then compares **envelope shape** (keys, structure, types, stable content) — not per-seed identity. A real shape/content drift (renamed/added/removed key, changed non-id scalar) still turns the API suite red until `fixtures:export` is re-run.

> **Correction (2026-07-10, found by Phase 6):** the scrub originally normalized only `token`/`iat`/`exp`/`expiresIn`/`createdAt`/`updatedAt`/`__v`/ISO-dates and deliberately **kept `_id`s**, on the assumption they were deterministic. They are **not** — the seed builds the world through real API calls, so every `yarn seed` mints fresh ObjectIds (`_id`, `dealer_id`, `cust_id`, …, incl. the compound `_id:{dealer_id,cust_id}`) and fresh base33 document numbers (`inv_no`). The contract spec therefore passed under `yarn test` (persisted snapshot the fixtures were exported from) but went **red under `yarn test:full`** (which re-seeds) — which is exactly what the release gate runs. Fixed by extending `scrub()` to also normalize any 24-hex ObjectId value + `inv_no`, and to compare arrays **order-insensitively** (canonical-sort of scrubbed elements, since server-side sorts often key on the now-scrubbed `_id`/date). `chq_no` and other hand-set factory values are **not** scrubbed — they remain contract-guarded content. Teeth re-verified: a changed `count`, a changed nested `dealer_name`, and an added key each still fail. Net: the contract now survives a fresh seed while keeping its teeth. _(Lesson: "green" under `yarn test` ≠ green under `test:full`; the gate must be what certifies the API.)_

**End-to-end drift demo (§5.5), performed & reverted 2026-07-10:** added `driftDemo` to the `sendTokenResponse` envelope (`api_v3/controllers/auth/index.js`) → contract spec `auth_loginrx` went **red** with the exact `+ "driftDemo"` diff (other 5 green) → `yarn fixtures:export` regenerated → contract **green** → `yarn fixtures:pull` in the app → the app's generated `auth_loginrx.json` gained the field and the app login test consumed the new shape (green). Then reverted the controller (`git checkout`), re-exported, re-pulled app **and** web → verified no `driftDemo` residue in any repo; all suites back to baseline. (Lesson recorded: generated fixtures are untracked, so restore them by re-running `fixtures:export`/`:pull`, not `git checkout`; and run each repo's pull from that repo's own dir.)

**`pull_fixtures.js` contract (both repos):** copies `../dzzlo_oms_api/fixtures/api_v3/*.json` → `src/test/fixtures/generated/`; **hard-fails** (exit 1, "run `yarn fixtures:export`" hint) if the source dir / `fixtures.meta.json` is missing; **loud warn** (no fail) if `generatedAt` > 14 days.
