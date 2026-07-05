# Plan: TDD Regression Safety Net — API + App + Web

> **Source prompt:** `../../prompt-tdd-test-suite-3-projects.md`
> **Repos under change:** `dzzlo_oms_api` (reference harness), `dzzlo_oms_app`, `dip-web` — plus this vault for the workflow guide.
> **Status:** Plan drafted 2026-07-02. Step-1 discussion questions **resolved 2026-07-05 — all defaults confirmed as-is** (see `## Open questions`), plus: keep `react-native-image-picker`/`react-native-permissions` virtually stubbed in the app (Phase 4), do not install them yet. This overview is the source of truth.

## Why — the release-confidence framing

The product (fuel-distribution OMS: API + dealer/customer mobile app + DIP web console) has outgrown manual release verification. Two failure modes we must close:

1. **New feature ships broken** — nothing proves it works end-to-end before release.
2. **Old feature silently regresses** — nothing re-checks orders/credit/vouchers/invoices when unrelated code changes.

The fix is a **regression contract**: a ranked list of business flows that must never break, each pinned by automated tests that run locally against **temporary local data only** (the seed/uproot principle already proven in `dzzlo_oms_api`), wrapped in a release gate that blocks shipping when red.

---

## TDD brief — red → green → refactor on this stack

### The loop

1. **Red** — write a small test that describes the behavior you want (or the bug you just reproduced). Run it. It must fail — a test you've never seen fail proves nothing.
2. **Green** — write the least code that makes it pass. Resist gold-plating.
3. **Refactor** — clean up with the test as your safety net. Commit.

### Test-first vs test-after — house policy (✅ Q10 confirmed 2026-07-05)

| Situation | Policy |
| --- | --- |
| **Bugfix** | **Always test-first.** Reproduce the bug as a failing test, then fix. The test stays forever as the regression pin. No exceptions — this is the cheapest habit with the highest payoff. |
| **New API endpoint / service rule** | **Test-first at integration level.** Write the supertest spec from the contract (status, envelope, side effects on Mongo), then implement. The endpoint contract *is* the design artifact. |
| **New screen / component (app, web)** | **Test-with.** Exploratory UI work may run ahead of tests, but the tests land **in the same PR** — pure logic extracted and unit-tested, screen behavior covered with RTL/RNTL where it carries business rules. |
| **Refactor** | No new tests required, but the suite must be green before and after; if you touch uncovered behavior, cover it first (characterization test). |

### The taxonomy — unit / integration ("functional") / feature / e2e

Terminology varies across teams; this is what each term means **here**, per repo:

| Layer | Proves | `dzzlo_oms_api` | `dzzlo_oms_app` | `dip-web` | Speed |
| --- | --- | --- | --- | --- | --- |
| **Unit** | One pure function/reducer/selector is correct. No I/O, no framework, no mocks (or trivial ones). | `helpers/` funcs (`getApplicableRate`, `dieselQtyLimit`, `versionGate`), service calculations | `src/utils/*` (Currency, Dates, validators, permissions, `inv_no` base33), `helpers/Credit`, selectors, slice reducers, `paginationHelpers` | `src/utils/permissions.js`, `errorRTK`, slice reducers, hooks via `renderHook` | ms |
| **Integration** (a.k.a. **functional**) | One endpoint/screen behaves correctly through its **public interface** — real internals, faked edges only. | **The existing `test/api_v3` idiom**: supertest against the in-process Express app + `mongodb-memory-server` + seeded fixtures. This is our backbone. | One screen rendered with RNTL, store + navigation real, **network faked with MSW** | One page rendered with RTL, store/router/theme real, **network faked with MSW** | ~100ms–1s |
| **Feature** | A multi-step **business flow** spanning several resources works end-to-end *within one system*. | `test/api_v3/features/` convention: e.g. order → SO → invoice → voucher → ledger balances | A user journey across screens (login → place order) with MSW | A journey (sign-in → create decant) with MSW | 1–10s |
| **E2E** | Real processes wired together: UI ↔ real API ↔ real (local) DB. | n/a (API *is* the backend) | Maestro/Detox on emulator against a **locally seeded API** — no e2e yet (✅ Q6) | Playwright against Vite build + locally seeded API — no e2e yet (✅ Q6) | minutes |

**How to plan across the four layers:** push every rule as far *down* the table as it can live. A credit-limit formula belongs in a unit test; "POST /order_msts rejects when over limit" belongs in an API integration test; "customer sees the blocked-credit message" belongs in one RNTL screen test; only "the whole stack boots and a login works" belongs in e2e. Never re-prove the same rule at two layers — the upper layer assumes the lower one.

### Shape: trophy, not pyramid

Because the API is the system of record and both clients are thin views over RTK Query, the biggest investment is the **API integration/feature layer** (fast, local, already idiomatic here), flanked by cheap unit tests everywhere, a modest set of RTL/RNTL screen tests, and a *tiny* optional e2e smoke. Roughly:

```
        e2e smoke        (0–10 tests, release gate only — deferred, ✅ Q6)
   app/web screen tests  (dozens)
  ████ API integration ████  (hundreds — the backbone)
     unit tests           (hundreds, milliseconds, run on save)
```

### What "TDD-type test cases" realistically means per repo

- **API** — integration-level TDD: the failing test is a supertest spec against a seeded in-memory Mongo. You design the endpoint by writing its contract first. Unit TDD applies to helpers/services with real logic.
- **App** — unit TDD on the rich pure layer (`utils/`, `helpers/`, selectors, slices); screen tests are test-with, not test-first.
- **Web** — same as app, with Vitest+RTL; RTK Query endpoint behavior is exercised through the page that uses it, against MSW.

---

## Critical flows — the regression contract (ranking confirmed 2026-07-05 — ✅ Q1)

Coverage today: ✅ covered in `test/api_v3` · 🟡 partial · ❌ none. "Verify" = confirm depth during Phase 2.

| # | Tier | Flow | Lives in | Coverage today |
| --- | --- | --- | --- | --- |
| 1 | P0 | Auth & session: OTP login, redux auth, forgot/reset, verify email/phone | `api_v3/routes/auth`, app Login, web SignIn | ✅ API · ❌ app/web |
| 2 | P0 | **Role/scope/bearer enforcement** (`protect`/`authorize`/`scope`, `userCache`) | `api_v3/auth.js`, route guards | ❌ — tests run on `x-api-key` only; no bearer-token path is tested |
| 3 | P0 | Company status gates (`NOT_IN_COMPANY`/`COMPANY_INACTIVE`/`COMPANY_REMOVED`, `x-co-id`, multi-company switch) | `helpers/middlewares.js`, features/multiple_companies | 🟡 helper unit + multi-company tests; route-level gate verify |
| 4 | P0 | Orders (PO) lifecycle: create (credit + diesel checks), status transitions, delete-status, delivery OTP | `order_msts` routes/services | 🟡 (`a/poso` + collections; delivery-OTP depth verify) |
| 5 | P0 | Sales orders: create, edit/backdate reprice, diesel qty limit, slip numbering | `so_msts` | ✅ strong |
| 6 | P0 | Invoices: PRODUCT/CASH_REIMBURSE/GST, numbering, UNPAID→PARTPAID→FULLPAID, tax/TCS | `invs` | ✅ (GST/TCS depth verify) |
| 7 | P0 | Vouchers & payments: PInv/DrNote/CrNote/TCS/TDS/**AdvDep**, approval, ledger effects | `voc_msts`, `month_crdrs` | ✅ incl. `advdep.test.js` (drawdown = tasks_07 v2, conditional) |
| 8 | P0 | **Credit engine**: `max_cr_lmt` semantics (tasks_08 null/0/>0 redesign pending), `cr_bill_lmt`, `max_cr_days`, `adv_dep` balance, `legacy_credit_presenter` (≤1.77 shim) | `dealer_custs`, services, `helpers/middlewares.js` | 🟡 — blocking-path & presenter tests missing |
| 9 | P1 | Accounts/ledger: month/year ledgers, opening/current balances, fin-year rollover | features/accounts, sadmin | ✅ (rollover parity verify) |
| 10 | P1 | Products/rates: PSOC import, dealer rates, `getApplicableRate`, discounts | `prod_msts`, `psocs`, `rate_msts` | ✅/🟡 (rate LIST endpoints are dead code — not a gap) |
| 11 | P1 | Vehicles/drivers/deliveries: requests accept/reject, transfers, driver OTP | `veh_*`, `dvr_msts` | ✅ |
| 12 | P1 | Invites/users: invite→accept, scope assignment, cache busting | `invites`, `users` | ✅ |
| 13 | P1 | App version gate (`version_gate` counters doc, soft/hard block) | `check_user_version`, `versionGate.js` | ❌ |
| 14 | P2 | DIP flows: decants, meter reads, inspections (`/api/dip/v1`, separate `db_dip` connection) | `dip_api_v1`, dip-web pages | ❌ — **not even mountable in the test app today** (see Phase 2 §2.6) |
| 15 | P2 | Partner API (tasks_11) | not yet implemented | n/a — add to contract when it lands |

**Q1 resolved (2026-07-05):** table confirmed as ranked; DIP stays P2; frozen `/api/v2` gets no new tests (suite stays frozen-ignored per Q4).

---

## What already exists (verified 2026-07-02 — do NOT rebuild)

**`dzzlo_oms_api`** — the harness is healthier than the prompt assumed:
- Jest 30 + supertest 7 + **`mongodb-memory-server` 11**: every test file gets its **own ephemeral in-memory mongod** (`test/database.js`), so the suite is parallel-safe and can never touch a shared/cloud DB. `test/dzzlo_oms_test.js` exports the Express app in-process (no `.listen`).
- Seed (`yarn seed`) builds the full world (2 customer + 2 dealer companies, relations, vehicles/drivers, products, orders, SOs, invoices, vouchers, users/invites, SA) **mostly through real API calls** and snapshots 16 collections to `test/api_v3/temp/seed/data/v3_<date>/*.json`. Tests re-hydrate per-describe via `helper/beforeAll` (`insertMany`). `yarn uproot` just deletes the data dir; `test:full` always uproots (`seed && test; code=$?; uproot; exit $code`). Crash-safety is already structural: the DB is in-memory, so orphaned server data is impossible.
- Legacy suites `api_v1_test/`, `api_v1/`, `api_v2/`, `202405_v2/` are ignored via `testPathIgnorePatterns`. Triage verdicts: Phase 1 §1.4. ⚠️ `api_v1_test` connects to the **real remote `DATABASE_URI`** — one more reason it must go.
- Gaps: the test app **skips the production middleware chain** (`api_key_v1`, `logging()` → so `protect` has no `req.loggedInUser`, `check_user_version`), meaning role/scope/bearer and version-gate behavior are untested (flows #2, #13).

**`dzzlo_oms_app`** — RN 0.84 / React 19 / RTK Query (18 `injectEndpoints` files) / AsyncStorage tokens. Jest works but only Firebase is mocked in `jest.setup.js`; `@testing-library/react-native` not installed; `__tests__/App.test.tsx` is a render-only smoke. Rich, immediately-testable pure layer under `src/utils`, `src/helpers`, `src/store`. ⚠️ `src/components/ImagePicker` imports `react-native-image-picker` + `react-native-permissions` which are **not in package.json**. ⚠️ `yarn test` runs `APP_ENV=testing` whose `.env.testing` points at the **remote staging URL** — harmless only if tests never hit the network (Phase 4 enforces this with MSW `onUnhandledRequest: 'error'`).

**`dip-web`** — the "see Phase 5" mystery is solved: it refers to `src/docs/plans/cra-to-vite-migration.plan.md` → **"Phase 5: Testing (Deferred)"**, which already prescribes **Vitest + jsdom + `src/setupTests.js`** and keeps the installed RTL deps. Phase 3 of this plan executes exactly that (plus MSW). Single `createApi` (`dip-api`), 21 `injectEndpoints` files (~120 endpoints, 89 mutations), tokens in localStorage, roles dealer/superadmin with `dip.<resource>.<action>` permissions, JSX-in-`.js` (esbuild loader — Vitest inherits it via `vite.config.js`). No Vite proxy; all env API URLs are remote → MSW must intercept everything.

**Vault** — `tasks_11_partner_api` format copied here: no frontmatter, `00-overview.md` + `NN-phase-N-slug.md`, `**Outcome:**` line, `## N.M` subsections, `## Phase N checklist`. Deviation (required by the source prompt): each phase file adds an `**Effort:**` estimate line. Related plans to honor: tasks_07 (AdvDep — seed factory suggestions), tasks_08 (max_cr_lmt semantics — will change credit tests/seed), tasks_02 `05-cicd-github-actions.md` (existing CI plan to reconcile in Phase 6), tasks_10/tasks_11 per-phase testing sections.

---

## Architecture (target)

```
dzzlo_oms_api/
  test/api_v3/                    ← backbone: integration + feature suites (Phase 1–2)
    temp/seed/                    ← seed/uproot, extended factories (Phase 2)
  fixtures/api_v3/                ← NEW: exported response envelopes (Phase 5)
  scripts/release_gate.sh         ← NEW: cross-repo gate runner (Phase 6)
  docs/testing.md                 ← NEW: runbook (Phase 1, extended Phase 7)

dip-web/
  vite.config.js  + test block    ← Phase 3 (per cra-to-vite plan Phase 5)
  src/setupTests.js               ← NEW (Phase 3)
  src/test/{testUtils,msw}/       ← NEW render helpers + MSW server (Phase 3)
  src/test/fixtures/              ← pulled from API fixtures (Phase 5)

dzzlo_oms_app/
  jest.setup.js  + native mocks   ← Phase 4
  src/**/__tests__/               ← unit + RNTL suites (Phase 4)
  src/test/{msw,fixtures}/        ← MSW server + pulled fixtures (Phase 4–5)
```

Fixture flow (one source of truth): `yarn seed` world → `export_fixtures.js` captures real response envelopes → `fixtures/api_v3/*.json` → web/app `yarn fixtures:pull` → MSW handlers serve them. Mocks can only drift as far as the last pull, and the pull is part of the release gate.

---

## Phases

| Phase | File | Outcome | Effort |
| --- | --- | --- | --- |
| 1 | `01-phase-1-api-harness-hardening.md` | `test:full` bulletproof + documented; test app matches prod middleware; legacy suites triaged with written verdicts | 1–2 dev-days |
| 2 | `02-phase-2-api-regression-suite.md` | Every P0/P1 flow pinned by an api_v3-idiom test; seed gaps filled; flow→test map = the release checklist | 4–8 dev-days |
| 3 | `03-phase-3-web-foundation.md` | Vitest+RTL+MSW wired per the repo's own Phase-5 plan; `yarn test` really runs; first high-risk page tests | 2–4 dev-days |
| 4 | `04-phase-4-app-foundation.md` | Native mocks + RNTL installed; pure-logic suites; first screen tests; no-network guard | 3–5 dev-days |
| 5 | `05-phase-5-shared-fixtures-contract.md` | API-exported response envelopes feed web/app MSW; drift detector in API suite | 2–3 dev-days |
| 6 | `06-phase-6-release-gate.md` | One command gates all three repos; block-on-red policy; bug→failing-test→fix rule; CI path | 1–2 dev-days (+CI 1–2) |
| 7 | `07-phase-7-tdd-daily-workflow.md` | Per-repo daily TDD guide, PR checklist, speed budgets, onboarding | 1 dev-day |

Each phase is independently landable — the gate gets stricter release by release; nothing waits on a big-bang rollout. Order 1→2 is firm (2 builds on 1); 3 and 4 can run in parallel after 1; 5 needs 2+3 (app part needs 4); 6 consumes whatever exists and tightens over time.

---

## Open questions — ✅ RESOLVED 2026-07-05 (all defaults confirmed as-is)

1. **Critical flows** — table confirmed as ranked; DIP = P2; frozen `/api/v2` gets no new tests, suite stays frozen-ignored.
2. **Test database** — keep `mongodb-memory-server`; pin the mongod binary version + document the offline binary cache. No Docker, no shared local mongod.
3. **Seed evolution** — keep JSON-snapshot + factories (no factory-library rewrite). New factories needed: credit-capped/blocked relations, approved AdvDep (+drawdown pair), version_gate counters doc; partner tenant later.
4. **Legacy suites** — verdicts in Phase 1 §1.4 approved (delete `202405_v2` + `api_v1_test` + `api_v1`; keep `api_v2` ignored-frozen until min supported app ≥1.78, then delete). Deletion itself still waits for a separate explicit go-ahead before any `git rm` is executed — not yet given.
5. **Web runner** — Vitest confirmed (already the repo's own migration-plan decision). Upgrade `user-event` 13→14 and `jest-dom` 5→6 (RTL 13 stays for React 18); add `msw@2`, `vitest@3`, `jsdom`.
6. **App depth** — no e2e yet; Phase 6 leaves a marked slot for Maestro (preferred over Detox) later.
7. **Mocking strategy for web/app** — MSW with fixtures generated from the API seed (Phase 5) for all test suites; a locally seeded API is used only by the optional e2e smoke.
8. **Release gate location & release mechanics** — local script first (in `dzzlo_oms_api/scripts/`, runs sibling repos); GitHub Actions per-repo test workflows as the follow-up (reconciling tasks_02's CI plan).
9. **Coverage philosophy** — flows-covered checklist gates the release; % coverage is observability only (no numeric gate initially); revisit a ratchet after Phase 2.
10. **Team workflow** — confirmed: every bugfix starts with a failing regression test (mandatory); endpoint work is test-first; UI is test-with (same PR). Local runtime budgets: API `test:full` ≤ 5 min, web ≤ 1 min, app ≤ 2 min.

Also resolved from findings: keep `react-native-image-picker`/`react-native-permissions` **virtually stubbed** in Jest (Phase 4 §`jest.setup.js`) rather than installed for real — deferred to a later decision.

---

## Constraints

- **Local-data-only is non-negotiable**: no test in any repo may reach cloud/shared servers or production data. API already complies (in-memory Mongo); web/app enforce it via MSW `onUnhandledRequest: 'error'`.
- Legacy suites are triaged with rationale, never rewritten wholesale.
- Match each repo's conventions: `NODE_ENV` env-file loading (API), `APP_ENV` + `react-native-dotenv` (app), `env-cmd`/Vite env (web); code idioms `asyncHandler`/`ErrorResponse`/`advancedResults` (API), `injectEndpoints` + tag rules (web/app).
- Plan files follow the vault `tasks_NN` convention (this folder mirrors `tasks_11_partner_api`, plus `**Effort:**` lines).
- **Design first**: no implementation code lands in any repo until this plan is approved.
