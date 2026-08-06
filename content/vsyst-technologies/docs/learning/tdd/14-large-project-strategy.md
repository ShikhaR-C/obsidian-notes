# 14. TDD in a large project

Everything up to here has been TDD in the small: one function, one file, one kata. This section is about the other problem — **keeping the loop fast when the system is big**.

The running example for docs 14–18 is a real-shaped stack:

```
                      ┌──────────────────────┐
   React web app ────▶│                      │
   Vanilla JS/HTML ──▶│   Node/Express API   │──▶ MongoDB (Mongoose)
   React Native app ─▶│                      │──▶ 3rd-party APIs
                      └──────────────────────┘
```

Four deployables, three of them clients, one database, some outbound network. The thing that kills TDD at this size is never the writing of tests — it's **feedback latency and flakiness**. Both come from the same root cause: tests that reach across boundaries they didn't need to.

---

## The one rule that makes the rest possible

> **Business rules must be runnable without a server, a database, a browser, or a network.**

If pricing, eligibility, sync-conflict resolution and validation live inside Express handlers, Mongoose models and React components, then every test of a business rule needs a running system — and you're back to a 12-minute suite nobody runs.

So the shape is boring and deliberate:

```
packages/
├── domain/         pure business rules. Zero dependencies. Zero I/O.
├── contracts/      shared request/response schemas (Zod). No logic.
├── api/            Express + use cases + Mongoose adapters
├── web/            React app
├── admin/          vanilla JS + HTML pages
├── mobile/         React Native app
└── test-support/   builders, fakes, fixtures, MSW handlers
```

`domain` and `contracts` are imported by everyone and import nothing. Everything slow lives at the edges, behind an interface the domain defines. That single constraint is what lets 80% of your tests run in milliseconds.

---

## The tiers

Not "unit vs integration" — those words mean different things to everyone. Define tiers by **what they're allowed to touch**, and hold each to a runtime budget.

| Tier                  | Touches                                          | Typical count           | Budget          | Runs                |
| --------------------- | ------------------------------------------------ | ----------------------- | --------------- | ------------------- |
| **T0 — domain**       | Nothing. Pure functions and in-memory fakes.     | thousands               | **< 5 s total** | on every save       |
| **T1 — module**       | Real Mongo (in-memory), real Mongoose, no HTTP   | hundreds                | < 60 s          | pre-push            |
| **T2 — API contract** | The whole API process via supertest + real DB    | ~1 per endpoint × cases | < 2 min         | every PR            |
| **T3 — client**       | jsdom / RN test renderer + MSW. No real network. | hundreds                | < 90 s          | every PR            |
| **T4 — E2E smoke**    | Real browser / device, real deployed stack       | **5–15, no more**       | < 10 min        | merge to main       |
| **T5 — canary**       | Third-party APIs, staging, live network          | a handful               | untimed         | nightly, non-gating |

The counts matter as much as the runtimes. **T4 is a budget, not a goal.** Every team that lets end-to-end tests grow unbounded ends up with a suite that takes 40 minutes and fails 15% of the time for reasons nobody investigates.

```
        /\          T4  E2E smoke        5–15      slow, flaky, high confidence
       /  \         T3  client           ~300      fast, jsdom + MSW
      /    \        T2  API contract     ~150      one process, real DB
     /      \       T1  module           ~400      real Mongo, no HTTP
    /________\      T0  domain          ~1500      milliseconds
```

---

## What each tier is _for_

Tiers are not "the same test at different sizes". Each one exists to catch a class of bug the tier below **cannot** catch:

- **T0** — is the rule right? (`a 12-month plan cancelled in month 3 refunds 9/12 of the annual price, rounded to the customer's favour`)
- **T1** — does it survive persistence? Unique indexes, query correctness, schema validation, transactions.
- **T2** — is the HTTP surface right? Status codes, error envelopes, auth, pagination, the response shape three clients depend on.
- **T3** — does the UI do the right thing with that response? Loading, empty, error, success. Optimistic updates. Form validation.
- **T4** — is it actually wired together and deployed? Config, CORS, auth cookies, build output.
- **T5** — did a third party change on us overnight?

If you can't say which tier a new test belongs to, that's a design smell: the behaviour probably isn't isolated.

**Write each test at the lowest tier that can fail for the reason you care about.** A rounding rule tested through a browser is a rounding rule you'll be too scared to change.

---

## Test-support: the package that decides whether this scales

At small size everyone hand-rolls test data. At large size that's why suites rot — 400 tests each constructing a `User` literal, and adding a required field breaks all of them.

Build one package, own it properly:

```js
// packages/test-support/builders/user.js
const base = () => ({
  email: "ada@example.com",
  name: "Ada Lovelace",
  plan: "free",
  createdAt: new Date("2026-01-01T00:00:00Z"),
  verified: true,
})

export const aUser = (overrides = {}) => ({ ...base(), ...overrides })

export const anAdmin = (overrides = {}) =>
  aUser({ role: "admin", permissions: ["billing:write"], ...overrides })
```

```js
// the test only states what matters to it
const user = aUser({ plan: "pro" })
```

Rules that keep it useful:

1. **A builder's defaults must be valid.** Every test that doesn't care about a field gets a working value for free.
2. **Tests state only the fields they depend on.** If a test sets `verified: true` and the assertion has nothing to do with verification, delete the line — it's noise that hides the real input.
3. **Add a required field → change one file.** That's the whole return on the investment.
4. Also ship: a `fixedClock()`, an `InMemoryEventBus`, seeded ID generators, and the shared MSW handlers from [18. API & network tests](18-tdd-api-network.md).

---

## Isolation, or: why your suite is flaky

Almost all flakiness in a big suite is one of four things. Fix them structurally, not with retries.

| Cause                          | Symptom                                           | Fix                                                                                                    |
| ------------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Shared state between tests** | Passes alone, fails in the suite; order-dependent | One DB per worker, truncate between tests. See [16](16-tdd-mongodb-mongoose.md#setup-in-memory-mongo). |
| **Real time**                  | Fails at midnight, at month end, in CI's timezone | Inject a clock. Never call `new Date()` in domain code.                                                |
| **Real network**               | Fails when the office wifi hiccups                | MSW with `onUnhandledRequest: 'error'`. Real network only in T5.                                       |
| **Waiting by sleeping**        | Passes locally, fails on a loaded CI box          | `waitFor` / `findBy` on a condition. Never `setTimeout(500)`.                                          |

Prove isolation deliberately: run the suite with a randomised order (`vitest --sequence.shuffle`) in CI once a day. If shuffling breaks it, you have shared state — that's a bug in your tests, and it's the one that will eventually hide a real failure.

> **Retries are not a fix.** A test that passes on attempt two is a test that told you something and got ignored. Quarantine it out of the gating suite the same day, with an owner and a date, then fix or delete it within two weeks.

---

## What runs when

```
save file        → T0 in watch mode                        < 1 s
pre-push hook    → T0 + T1 for changed packages            < 60 s
pull request     → T0 T1 T2 T3, sharded, in parallel       < 5 min wall clock
merge to main    → the above + T4 smoke against staging    < 15 min
nightly          → T5 canaries, shuffled order, full E2E   untimed, non-gating
```

Two non-negotiables, both from [11, Phase 6](11-tutorial-first-feature.md#phase-6--fit-it-into-your-workflow):

- **Fail fast.** T0 gates T1 gates T2. Don't spend eight minutes on E2E to discover a domain unit test was red.
- **No auto-retry in the gating suite.** See above.

Shard by tier, not by file count — the tiers have wildly different setup costs, and a shard that boots Mongo has no business also running pure functions.

---

## Cross-boundary drift: the failure mode unique to this size

With three clients on one API, the bug that will actually hurt you is nobody's fault locally: the API renames `total_cents` to `totalCents`, every API test passes, every React test passes against its own hand-written mock, and the React Native app breaks in production.

The fix is that **the mock and the server must come from the same source**:

1. Define the response shape once, in `packages/contracts`, as a Zod schema.
2. The API's T2 tests assert real responses **parse** against that schema.
3. Every client's T3 tests build their MSW handlers **from** that schema.

Now a rename fails the API test _and_ every client test at once, at commit time. Details and code in [18. API & network tests](18-tdd-api-network.md#contract-first).

---

## Onboarding a big existing codebase

You do not retrofit. [13, Phase 4](13-adoption-phases.md#phase-4--legacy-code) applies unchanged, with two large-project additions:

- **Establish the tiers before writing tests.** Otherwise everything lands in T2 or T4, where it's slow, and the suite is unsalvageable within a year.
- **Extract `domain` incrementally.** Each time you test-drive a rule, move it out of the handler or component into the pure package. After six months the valuable logic is in a package that runs in 4 seconds.

---

## 🛠 Mini-project — the skeleton

_Stand up the structure before there's anything to put in it. One day._

1. Create the monorepo layout above with `domain`, `contracts`, `test-support` — empty but wired, with one passing test each.
2. Add one real rule to `domain`, test-first. No imports from anywhere.
3. Add tier scripts: `test:t0`, `test:t1`, `test:t2`, `test:t3`. Each independently runnable, each printing its runtime.
4. Write the first builder in `test-support` and use it from a `domain` test.
5. Add a CI job per tier with the budget from the table **enforced as a failure**, not a warning.
6. Add the nightly shuffled run.
7. Put the tier table in the repo README, with the current count and runtime per tier.

**Deliverable:** a repo where `npm run test:t0` is under 5 seconds on an empty project, and CI fails if any tier exceeds budget.

**Proves:** the constraint is in place before the pressure is. Retrofitting tiers onto 2,000 existing tests is a quarter of work; setting them up on day one is a day.

---

Next: [15. Node backend →](15-tdd-node-backend.md) · Related: [13. Adoption phases](13-adoption-phases.md) · [3. Writing good tests](03-writing-good-tests.md)
