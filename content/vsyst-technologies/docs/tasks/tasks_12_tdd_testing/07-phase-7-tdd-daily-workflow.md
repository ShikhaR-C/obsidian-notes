# Phase 7 — TDD Daily Workflow (per repo)

**Outcome:** every developer knows exactly what to do when starting a feature, fixing a bug, refactoring, and preparing a release — per repo, with exact commands; the PR checklist enforces it; the suite stays fast enough that nobody routes around it.
**Effort:** 1 dev-day (writing + team walkthrough). Final phase; consolidates Phases 1–6 into habit.

> **TDD lens:** a safety net nobody uses is decoration. The workflow below is deliberately small — three rituals per repo — because rules that fit on one screen get followed.

---

## 7.1 `dzzlo_oms_api` — daily guide

**Starting a feature (endpoint/service):**

1. `yarn seed` once (idempotent), keep `yarn test:watch` running on the new spec file.
2. Write the supertest spec first — route, envelope, Mongo side effects — in `test/api_v3/` idiom (Phase 2 §2.4). Red.
3. Implement route → controller → service (v3 layering). Green. Refactor.
4. If the feature adds a business flow, add a row to the flow→test map (Phase 2 §2.1) in the same PR. If it needs seed data, extend a factory + re-run `yarn seed`.

**Fixing a bug:** reproduce as a failing test _before touching the fix_ — name it after the symptom, reference the report in the test description (`it("does not double-charge TCS on part-paid invoice (bug 2026-07-xx)")`). Then fix. The test never gets deleted. **This is mandatory** (⏳ Q10 confirmation).

**Refactor:** `yarn test` green before and after; no behavior change means no assertion change — if you _must_ edit assertions, it wasn't a refactor.

**Preparing a release:** `yarn test:full`, then the cross-repo gate (Phase 6 §6.1). Contract changed? `yarn fixtures:export` + front-end pulls in the same release.

## 7.2 `dip-web` — daily guide

**Feature (page/hook/endpoint):** extract logic into a hook/util and unit-test it (`yarn test:watch`); page behavior gets an RTL test with MSW fixtures (generated ones for happy paths, `server.use(...)` for errors); new RTK Query endpoints follow the tag rules (`docs/rtk-query-conventions.md`) and the test asserts invalidation-driven refetch where the UI depends on it.

**Bugfix:** failing test first — component-level if visual/behavioral, hook/util-level if logic. Same permanence rule.

**Release prep:** `yarn lint && yarn test`; if the API contract moved this release, `yarn fixtures:pull` first and commit the refreshed fixtures.

## 7.3 `dzzlo_oms_app` — daily guide

**Feature (screen/flow):** business rules go in `src/utils`/`src/helpers`/slices **first**, unit-tested TDD-style (they run in ms — `yarn test:watch`); the screen gets an RNTL test only if it carries decisions (conditional rendering by role/credit/status), not for pure layout; new endpoints get a Tier-2 store/MSW test if they carry headers/error semantics beyond the default.

**Bugfix:** failing test first at the lowest layer that reproduces it (most app bugs reproduce in a util/selector/slice test; screen-level only if the bug _is_ the wiring).

**Release prep:** `yarn test` (runs `APP_ENV=testing`; MSW guard guarantees no staging contact), then the cross-repo gate.

## 7.4 PR checklist (add to each repo's PR template)

```
- [ ] Bugfix PRs contain the regression test, written first (link the red run if CI history shows it)
- [ ] New business flow → row added to the flow→test map (API) / screen-risk note (web, app)
- [ ] No test deleted or .skip'd without a written verdict in the PR description
- [ ] Suite runtime budget respected (api ≤ 5 min, web ≤ 1 min, app ≤ 2 min — ⏳ Q10)
- [ ] API contract changed? fixtures:export committed + front-end pull noted for the release
```

## 7.5 Keeping the suite fast (the anti-rot rules)

- **Budgets** (⏳ Q10): API `test:full` ≤ 5 min, web ≤ 1 min, app ≤ 2 min locally. A PR that blows the budget must pay it back (split files — memory-server parallelism scales per file; narrow `beforeAllHelper` requests to only the tables the suite reads).
- **No sleeping** in tests — poll or use the app's own cache-bust/settle mechanisms.
- **One layer per rule** (overview taxonomy): don't re-prove an API rule in a screen test; assert the screen _reacts_ to the API's answer, not that the answer is right.
- **Flakes are P1 bugs** against the safety net — fix or quarantine-with-verdict within a day; a gate people don't trust is worse than none.

## 7.6 How new hires learn it

1. Read `docs/testing.md` in the API repo (Phase 1) + this folder's `00-overview.md` TDD brief.
2. Run `yarn test:full` locally on day one; break a credit test on purpose and watch it fail (the mutation smoke as a teaching tool).
3. First ticket is a bugfix, pair-done, test-first — the ritual is learned by doing it once with someone who already has it.

## 7.7 Verification — how we know Phase 7 is done

- The three per-repo guides exist in each repo's `docs/` (API: extended `docs/testing.md`; web/app: new `docs/testing.md`) and match this file.
- PR templates updated in all three repos.
- Two consecutive releases used the full workflow (gate + checklist) without ad-hoc exceptions — then this plan's status flips to "operational" in the overview.

## Phase 7 checklist

- [x] Per-repo `docs/testing.md` daily guides written (api extends its runbook §10; web + app new files) — _committing is the user's call_
- [x] PR templates added with §7.4 checklist (`.github/PULL_REQUEST_TEMPLATE.md` ×3)
- [x] Speed budgets recorded in every guide (api `test:full` ≤5min, web ≤1min, app ≤2min — all with huge headroom today: ~2min / ~1.5s / ~11s)
- [x] Mandatory bugfix-TDD rule written into all three guides (team ratification still ⏳ Q10 — a human sign-off)
- [x] Onboarding path (§7.6) added to the API runbook (§10.6) incl. the mutation-smoke teaching drill
- [ ] Overview status flips to "operational" once **two real releases** have run the workflow — a future milestone, not code

## Phase 7 — implementation notes (executed 2026-07-10, agent team, doc-only)

**Result:** three per-repo daily-TDD guides + PR templates, nothing but docs touched (verified: zero non-doc files modified across all three repos). Each agent verified every command/path against its own repo and **corrected three inaccuracies in the brief** — a healthy sign the guides match reality, not the plan's assumptions:

| Repo            | Guide                                           | Corrections the agent caught                                                                                                                                                                                                     |
| --------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `dzzlo_oms_api` | `docs/testing.md` §10 (10.1–10.6) + PR template | none — kept `fixtures:pull` framed as a front-end-only command (not in API package.json)                                                                                                                                         |
| `dip-web`       | new `docs/testing.md` + PR template             | **no `yarn lint` script** — ESLint runs via husky pre-commit + CI `lint.yml`; release ritual written around that                                                                                                                 |
| `dzzlo_oms_app` | new `docs/testing.md` + PR template             | MSW export-map fix lives in `jest.config.js moduleNameMapper`, **not** `jest.resolver.js` (that's for Reanimated); **`src/test/testUtils.js` does not exist** → Tier 3 documented as genuinely deferred (see Phase 4 correction) |

Each guide encodes the same three rituals (feature / bugfix-test-first-MANDATORY / refactor) + release prep + the §7.5 anti-rot rules + §7.4 PR checklist, adapted to the repo's real runner (API supertest+seed, web Vitest+jsdom-fetch+MSW, app Jest+RNTL+MSW) and its actual quirks (API mutation-smoke drill; web's custom-env do-not-revert warning; app's `APP_ENV` + jest path-pattern gotchas + untracked-test caveat).
