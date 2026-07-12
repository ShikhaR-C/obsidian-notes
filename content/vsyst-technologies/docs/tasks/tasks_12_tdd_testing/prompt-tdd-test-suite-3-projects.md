# Prompt — TDD test suite & release-safety net across API, App, Web

> Paste everything below the line into Claude Code, running at the **workspace
> root** `DZZLO_OMS/v1_78/` (the parent folder that contains all three projects
> and this vault). It asks for a discussion first, a phased plan second, and
> code only after the plan is approved.

---

You are working in the **DZZLO OMS workspace** (`v1_78/`), which contains three
sibling projects that ship together as one product, plus this notes vault:

| Project          | Stack                                                     | Testing today                                                                                                                                                                                          |
| ---------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `dzzlo_oms_api`  | Node.js + Express 5, Mongoose 9, MongoDB                  | Jest works. Active suite in `test/api_v3/`; legacy suites in `test/api_v1*`, `test/api_v2`, `test/202405_v2` are excluded via `testPathIgnorePatterns`. A local **seed/uproot** system exists.         |
| `dzzlo_oms_app`  | React Native (Jest + `jest.setup.js`, `APP_ENV` variants) | Only the default `__tests__/App.test.tsx`. No business-logic or screen tests.                                                                                                                          |
| `dip-web`        | React + Vite + RTK Query                                  | **No test runner configured** — `yarn test` echoes "No test runner configured — see Phase 5". `@testing-library/react`, `jest-dom`, `user-event` are already in devDependencies but nothing runs them. |
| `obsidian-notes` | Quartz vault                                              | Plans live in `content/vsyst-technologies/docs/tasks/tasks_NN_*/` as phase files.                                                                                                                      |

## Problem

The product has grown past the point where we can manually verify a release.
When we add a feature we can no longer tell whether (a) the new feature works
end-to-end and (b) older features still behave according to business logic.
We want a **TDD-style regression safety net**: before every release, a suite
runs across all three projects and proves nothing broke; if something broke,
we fix it **before** release, not after a customer finds it.

## Goal

1. A short, practical **brief on TDD** for our team, adapted to this stack —
   red → green → refactor, test-first vs test-after, unit vs integration vs
   e2e (pyramid/trophy), and what "TDD-type test cases" realistically means
   for an Express + Mongoose API (integration-level TDD against a seeded
   local DB) vs a React Native app vs a Vite/React web app.
2. An **open discussion with us before any plan is written** (see Step 1).
3. A **phase-wise plan as files** in this vault (see Step 2) that takes each
   project from where it is today to a maintained regression suite.
4. A **daily TDD workflow guide** per project: what a developer does when
   starting a feature, fixing a bug, and preparing a release.
5. A defined **release gate**: the exact command(s)/checklist that must pass
   before we ship, and the policy when they fail (release is blocked).

## What already exists (read these before proposing anything)

### `dzzlo_oms_api` — learn from this repo first; it is the reference

- `jest.config.js` — node env, 30s timeout, `testPathIgnorePatterns` hiding
  the legacy suites. Understand exactly what is ignored and why.
- `package.json` scripts — the test lifecycle we like and want to generalize:
  `yarn seed` → `yarn test` → `yarn uproot`, wrapped as `yarn test:full`
  (`yarn seed && yarn test; code=$?; yarn uproot; exit $code`).
- `test/api_v3/temp/seed/index.js` + `uproot.js` + `v3/` + `data/` — the
  **seeding system**: builds a full local world (customer + dealer companies,
  SA, users/invites, vehicles/drivers, specs, products, orders, SOs,
  invoices, vouchers) and writes ids/fixtures to local JSON so tests use
  **temporary local data instead of any cloud/shared server**. This principle
  is non-negotiable and must extend to the other two projects.
- `test/database.js`, `test/dzzlo_oms_test.js` — how tests connect and boot.
- `test/api_v3/` (`auth/`, `collections/`, `features/`, `getAll/`, `helper/`)
  — the current integration-test idiom to follow and extend.
- Legacy: `test/api_v1_test/`, `test/api_v1/`, `test/api_v2/`,
  `test/202405_v2/` — skim enough to say what they covered; they are input
  for triage, not something to resurrect wholesale.
- Repo idiom for any code you later write: `asyncHandler`, `ErrorResponse`,
  `advancedResults`, middleware chain in `dzzlo_oms.js`.

### `dzzlo_oms_app`

- `jest.config.js`, `jest.setup.js`, `__tests__/App.test.tsx` — the entire
  current setup. Note the `APP_ENV` (`development`/`testing`/`production`)
  script convention; tests must respect it.
- Skim `src/` (or the actual source layout) enough to classify what is
  testable pure logic (helpers, reducers/slices, API layer) vs what needs
  React Native Testing Library vs what only an e2e tool could cover.

### `dip-web`

- `package.json` — testing-library deps present, no runner. The `test` script
  literally says "see Phase 5": find what plan that referred to (check
  `docs/`, `REVIEW.md`, the vault) and reconcile with it rather than
  inventing a conflicting one. Vitest is the natural runner for Vite —
  confirm rather than assume.
- `vite.config.js`, `docs/rtk-query-conventions.md`, `docs/auth-and-roles.md`,
  `docs/component-patterns.md` — conventions any tests must follow.

### Vault conventions (where the plan lives)

- `obsidian-notes/content/vsyst-technologies/docs/tasks/tasks_11_partner_api/`
  — the format to copy: `00-overview.md` + `NN-phase-N-slug.md`, one file per
  phase, each with objective, exact files to add/change, snippets in the
  repo's idiom, and how to verify the phase.

## Step 1 — Open discussion (do this first; do NOT write the plan yet)

Present a one-page summary of what you found in the three repos, then ask us
your open questions and **wait for answers**. Cover at least:

1. **Critical flows:** propose your ranked list of business flows that must
   never break (orders, vouchers/payments, invoices, credit limits,
   auth/roles/scopes, company status gates, deliveries…) and ask us to
   correct/rank it. This list drives everything.
2. **Test database:** local `mongod` vs `mongodb-memory-server` vs Docker;
   one shared DB per run vs per-worker isolation; how `yarn test:full`
   behaves when a run crashes mid-way (orphaned seed data).
3. **Seed system evolution:** keep the JSON-file + seed/uproot approach as-is,
   or refactor toward factories? What new features (advance deposits, max
   credit limit, analytics events, partner API) are missing from seed data?
4. **Legacy tests:** for each ignored suite, revive / port to v3 style /
   retire — and does anything they cover lack a v3 equivalent today?
5. **Web runner:** confirm Vitest (+ RTL + MSW) and clarify what the
   "see Phase 5" note referred to.
6. **App depth:** how far do we go — pure logic only, component tests with
   RNTL, or also e2e (Detox/Maestro)? What device/emulator constraints exist?
7. **Mocking the API for web/app:** MSW fixtures generated **from the API
   seed data** (single source of truth) vs hitting a locally seeded API —
   trade-offs and your recommendation.
8. **Release gate location:** CI (which provider?) vs a local pre-release
   script first; what our release cadence and versioning flow is
   (the `v1_77/` → `v1_78/` folders are a hint — ask how releases work).
9. **Coverage philosophy:** flows-covered checklist vs % line coverage;
   what number, if any, gates a release.
10. **Team workflow:** who writes tests, when TDD is mandatory (proposal:
    every bugfix starts with a failing regression test — confirm), and how
    much suite runtime we tolerate locally.

## Step 2 — Deliverable: phase-wise plan files

After the discussion, write the plan to
`obsidian-notes/content/vsyst-technologies/docs/tasks/tasks_12_tdd_testing/`
following the `tasks_11_partner_api` format. `00-overview.md` must contain the
TDD brief (Goal #1), the agreed critical-flow list, and the phase map. Cover
at minimum — renumber/split as the discussion dictates:

- **Phase 1 — API harness hardening:** make `test:full` bulletproof (DB
  isolation, crash-safe uproot, parallelism decision), document how to run
  and debug it, triage the legacy suites with a written verdict per suite.
- **Phase 2 — API regression suite:** integration tests (existing
  `test/api_v3` idiom) for every agreed critical flow, seeded locally; gaps
  in seed data filled. This is the backbone of "nothing breaks."
- **Phase 3 — Web foundation:** wire the runner + RTL + API mocking, first
  tests on the highest-risk screens/hooks, `yarn test` actually runs.
- **Phase 4 — App foundation:** grow beyond `App.test.tsx` — native-module
  mocks in `jest.setup.js`, pure business logic first, then key screens.
- **Phase 5 — Shared fixtures / contract layer:** one source of truth so
  web/app mocks cannot drift from real API shapes (seed JSON reuse, or
  schema-derived fixtures) — prevents the classic "mocks pass, prod breaks."
- **Phase 6 — Release gate:** the cross-project pre-release run (script or
  CI), smoke/e2e decision, the block-release policy, and the bug → failing
  regression test → fix → release rule.
- **Phase 7 — TDD daily workflow:** per-repo guide (new feature, bugfix,
  refactor), PR checklist, keeping the suite fast, and how new hires learn it.

Each phase file: objective, exact files to add/change per repo, code snippets
in that repo's idiom, how to verify the phase is done, and an estimate of
effort. Phases must be independently landable — the suite gets stricter
release by release rather than blocking on a big-bang rollout.

## Constraints

- Tests must never touch cloud/shared servers or production data — the
  seed/uproot local-data principle extends to all three projects.
- Do not rewrite the legacy suites wholesale; triage them with rationale.
- Match each repo's existing conventions and env-selection mechanisms
  (`NODE_ENV` in the API, `APP_ENV` in the app, `env-cmd` files in web).
- Plan files follow the vault's `tasks_NN` convention exactly.
- Design first: no implementation code in any repo until we approve the plan.
- Point out assumptions and open questions as you go; when the discussion
  changes a decision, update `00-overview.md` so it stays the source of truth.

Start by reading the files listed above, then open the Step 1 discussion. Do
not proceed to Step 2 until we have answered.
