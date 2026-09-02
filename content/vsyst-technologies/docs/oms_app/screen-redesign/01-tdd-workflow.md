# 01 — The TDD workflow and strategy for the screen redesign

**Outcome:** one way of working, written down once, that every screen iteration follows in both repos. It extends the house rules in [[../tdd-testing-guide|app TDD guide]] and [[../../oms_api/tdd-testing-guide|API TDD guide]] to a project where the *contract is being designed*, not just protected.

> The existing TDD net (tasks_12) protects what exists. This project creates new contracts (v4 read models and commands) and new screens. TDD here therefore means **contract-first**: the screen spec produces the first failing tests, and the tests are the design artifact that the API, the design review and the screen all have to satisfy.

---

## 1.1 Seven rules (non-negotiable)

1. **Spec → red test → code. Never code → test.** No `api_v4` route exists before its supertest spec is red. No `src/screens/v2/*` component exists before its decision tests are red. The only exploratory code allowed is layout/styling inside a screen whose decision tests already exist.
2. **Push every rule to the lowest layer that can prove it.** A business rule (credit, diesel limit, closed period) lives in an API integration test. A screen-side decision (what to show for `creditState`) lives in an app util test. The screen test only proves the screen *reacts* to the util's answer. Never prove the same rule at two layers.
3. **Fixtures are the contract between the repos.** Every v4 response the app consumes is captured from the seeded world (`yarn fixtures:export` → `fixtures/api_v4/*.json`) and pulled into the app (`yarn fixtures:pull`). Hand-rolled success bodies are forbidden in app tests; hand-rolled *error* bodies are allowed inline.
4. **Red commit, then green commit.** Each rule lands as two commits: `test(v4/<slug>): pin …` (red, on its own) then `feat(v4/<slug>): …` (green). Reviewers can check out the red commit and watch it fail. Bugs found during the project follow the existing bug-museum ritual (`docs/bug-museum.md` in the API repo).
5. **Mutation smoke is the definition of done for every new suite.** Disable the rule in the source, confirm exactly the expected tests go red, revert, record it in the PR body.
6. **`test:full` certifies the API, not `yarn test`.** A green `yarn test` on a stale seed proves nothing (the so_msts NaN lesson). The app equivalent: `yarn test` must run with the MSW `onUnhandledRequest: "error"` guard in every suite.
7. **v3 is frozen for features.** Redesign work never edits `api_v3/routes` or `api_v3/controllers`; it *calls* `api_v3/services`. Any change a new screen needs inside a v3 service is a separate, test-first PR with its own flow-map row, because it changes behaviour for v1.78 clients too.

---

## 1.2 The layer map for one redesigned screen

| Layer | Proves | Where (API repo) | Where (app repo) | Tool | Speed | Written when |
| --- | --- | --- | --- | --- | --- | --- |
| **Unit** | one pure function: cursor codec, validation schema, read-model shaper, screen-side decision helper | `test/api_v4/unit/**` | `src/utils/**/__tests__`, `src/helpers/**/__tests__` | Jest | ms | first, whenever logic exists outside I/O |
| **Integration (backbone)** | one v4 endpoint through its public interface: status, envelope, tenancy, validation, Mongo side effects | `test/api_v4/screens/<slug>.test.js`, `test/api_v4/commands/<resource>.test.js` | — | Jest + supertest + in-memory mongod (`test/dzzlo_oms_test.js`) | 100 ms – 1 s | before the route/controller exist |
| **Contract** | the envelope the app was built against has not drifted | `test/api_v4/contract/fixtures.test.js` (drift detector over `fixtures/api_v4/`) | `src/test/fixtures/generated/v4_*.json` (pulled) | Jest | ms | after the endpoint is green; re-minted deliberately on every contract change |
| **Store (Tier 2)** | the RTK Query endpoint sends the right headers/body, tags, `transformResponse`, and error mapping | — | `src/store/apis/v4/__tests__/<slug>.msw.test.js` | Jest + MSW + `makeStore()` | ~100 ms | with the endpoint file |
| **Screen (Tier 3)** | the screen renders each *decision* correctly against a real store + navigation + MSW | — | `src/screens/v2/<Name>/__tests__/<Name>.test.js` | RNTL + MSW + `renderScreen()` | ~1 s | red before the component file exists |
| **Feature flow** | a multi-screen journey (e.g. place order → see it in the list) | `test/api_v4/features/**` (API-side journey) | `src/test/flows/**` (MSW journey, optional) | same | 1 – 10 s | only for P0 journeys, after both screens ship |
| **Manual / device** | design fidelity, gestures, font-scale 200 %, dark mode, old build still works on v3 | release checklist | release checklist | device | minutes | every release |

Shape: the trophy from tasks_12 still holds. Most of the new investment goes into **API integration** (contract) and **app unit** (decisions); Tier 3 stays modest and decision-only; nothing here adds e2e.

---

## 1.3 The loop, per step

### Red → green → refactor, with the exact commands

```sh
# API (dzzlo_oms_api) — keep this running in a pane while designing the endpoint
yarn test:watch                                   # jest --watch over test/ (needs a seed on disk: yarn seed once)
yarn test:file test/api_v4/screens/<slug>.test.js # one file
yarn test:full                                    # seed → jest → uproot: the certifying run before every push
yarn fixtures:export                              # after green: re-mint fixtures/api_v4/*, commit them

# App (dzzlo_oms_app)
APP_ENV=testing npx jest --watch <pattern>        # pattern is a regex over the full path; "inv_no" not "src/utils/…"
yarn test                                         # the one command, ~11 s today (budget ≤ 2 min)
yarn fixtures:pull                                # copies ../dzzlo_oms_api/fixtures/api_v4/* into src/test/fixtures/generated/
```

### The API ritual for one v4 read model (from spec §5.1)

1. **Write the suite from the spec.** `test/api_v4/screens/<slug>.test.js` in the house idiom (`db.connect()`, `beforeAllHelper({...})`, `request.post("/api/v4/screens/<slug>").set(auth)`). One `it` per line of the spec's test list: happy path, tenancy (every id the body accepts), validation, role subsets, pagination, partial failure. Run it. **Everything must be red for the right reason** (404 route missing, not a harness error).
2. **Route + controller stub** returning `{ ok: true, data: {} }`. Shape tests stay red, auth/validation tests may go green — that is fine, those are proven by the shared v4 middleware suite from the foundations.
3. **Read model.** `api_v4/readmodels/<slug>.js` composes existing `api_v3/services/*` calls in `Promise.all` / `Promise.allSettled` and projects fields exactly per spec §2. Happy path green.
4. **Tenancy.** Derive `dealer_id`/`cust_id` from the token (`req.loggedInUser`), verify relation membership before sub-queries. Tenancy tests green.
5. **Refactor** with the suite green. Then `yarn test:full`.
6. **Contract.** `yarn fixtures:export`, commit `fixtures/api_v4/screens_<slug>.json` + meta. Drift detector green.
7. **Mutation smoke**, flow-map row in `docs/testing.md` §8, PR with the template checklist. Red commit and green commit visible in the history.

### The API ritual for one v4 command (from spec §5.2)

Same loop, plus: the precondition has a red case *and* a green case, the Mongo side effect is asserted directly (not just the status), the idempotency replay is a no-op test (bug-museum #1 lesson), and the invalidation contract (which read models change) is asserted through a follow-up read in the same test.

### The app ritual for one v2 screen (from spec §6)

1. `yarn fixtures:pull` — the v4 fixture for this screen must exist before any app code.
2. **Tier 1 first.** List every "Derived?" cell in spec §2 and every precondition in §3 that is *evaluated on the client*. Each becomes a pure function under `src/utils` or `src/helpers` with a red test, then green. Watch mode stays on.
3. **Tier 2.** `src/store/apis/v4/<slug>.js` with `getScreen_<Name>` (+ mutations). MSW test asserts URL, method, body, bearer/`x-co-id` headers, tags, and that a 403 maps to the `errorRTK` path.
4. **Tier 3, red first.** `renderScreen(<Name />, { preloadedState, handlers })` from `src/test/testUtils.js`. Write one test per *decision row* (conditional element, precondition true/false, loading/empty/error, navigation on success). The component file does not exist yet, so the suite is red.
5. **Build the screen from the design** (spec §4) until Tier 3 is green. Layout and styling are exploratory here; no test asserts pixels.
6. **Cutover test.** The navigator resolves the v2 component for the route name (and the v1 component when the kill-switch is off, if the project keeps a kill-switch — see [[00-overview#Decisions]]).
7. **Mutation smoke** (flip a decision helper, watch Tier 1 *and* Tier 3 go red), PR with the template checklist.

---

## 1.4 How discussion sessions feed the tests

- Every decision taken in a session is written into the screen spec **as a test name** before it is written as prose. "Customer sees 'credit blocked' banner when `max_cr_lmt` is 0" is a line in §5.3 or §6, not a paragraph.
- An unresolved question becomes `it.todo("<the question>")` in the suite. `it.todo` is allowed only between "spec draft" and "spec agreed"; a PR may not merge with a `todo` in it.
- Feature evolution during development is expected (the user has said features will evolve). The rule: **change the spec, then the test, then the code** — in that order, in the same PR. A test edited without a spec change is a smell reviewers reject.
- Design changes that do not change a decision (colour, spacing, copy) need no test change and no spec change beyond §4.

---

## 1.5 Cross-repo sequencing for one screen

```
API repo                              app repo
─────────────────────────────         ─────────────────────────────
spec §5 → red suite
route/readmodel → green
test:full → fixtures:export ─commit─┐
PR (red+green commits) → merge      │
deploy to staging                   └→ fixtures:pull → commit
                                       Tier 1 red → green
                                       Tier 2 red → green
                                       Tier 3 red → build screen → green
                                       PR → merge
                                       release gate (bash dzzlo_oms_api/scripts/release_gate.sh)
                                       app release vX.Y  (old build keeps working on v3)
```

- The API PR for screen N+1 may start while the app PR for screen N is open. Two *app* PRs for different screens should not be open at once until the team has shipped three screens this way.
- The API is deployed to staging **before** the app PR is opened, so the manual check "one request on screen open" is against a real server, not MSW.

---

## 1.6 What is deliberately not tested

- Pixel layout, colours, fonts, snapshot tests of whole screens (brittle; design fidelity is a review-session item with a screenshot checklist: light, dark, font-scale 200 %).
- v3 endpoints a new screen keeps using unchanged (already pinned by `test/api_v3`).
- Third-party behaviour (Paper, navigation, FlashList).
- Anything a lower layer already proves.

---

## 1.7 Health rules carried over (and two new ones)

| Rule | Value |
| --- | --- |
| API suite budget (`test:full`) | ≤ 5 min |
| App suite budget (`yarn test`) | ≤ 2 min |
| Flaky test | P1 bug in the safety net; fixed or quarantined with a written verdict the same day |
| `describe.skip` / `xit` | only with a written verdict in the PR |
| **New:** `it.todo` | never in a merged PR |
| **New:** fixtures freshness | `fixtures.meta.json` ≤ 14 days old at release time, for `api_v3` *and* `api_v4` sets |

---

## 1.8 Anti-patterns this project has already paid for

| Anti-pattern | What happened | Rule that prevents it |
| --- | --- | --- |
| Asserting only `status 200` | bug-museum #1–#4: buckets drifted while every test stayed green | every command test asserts the Mongo side effect |
| Green under `yarn test`, red under `test:full` | Phase 5/6 ObjectId incident; so_msts NaN | scrub non-deterministic values; certify with `test:full` |
| Guards imported but commented out | `protect`/`authorize`/`scope` unwired on every v3 collection route | v4 mounts them at the router level; a harness test asserts every v4 route rejects a missing bearer |
| Fixing a rule where it was seen | bug-museum #5, #10: the same poster existed in two files | rules live in one service; v4 composes, never copies |
| Feature test written after the feature | the app had one smoke test before tasks_12 | red commit precedes green commit, visible in `git log` |

---

## 1.9 Definition of done — one screen

- [ ] Spec agreed, dated, every ⛔ section filled; discussion notes in §4
- [ ] API: red commit → green commit; tenancy + validation + side-effect tests present; mutation smoke recorded; fixture exported and committed; flow-map row added; `yarn test:full` green; CI green
- [ ] App: fixtures pulled and committed; Tier 1 → Tier 2 → Tier 3 all red-first; no-network guard intact; mutation smoke recorded; `yarn test` green; CI green
- [ ] Device check: one v4 request on screen open; light/dark; font-scale 200 %; a v1.78 build still works against the same API
- [ ] Release gate green; screen row updated in the screens index; old screen scheduled for deletion in the next release
