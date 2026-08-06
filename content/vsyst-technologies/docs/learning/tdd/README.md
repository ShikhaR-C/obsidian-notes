# Test Driven Development

A short, practical guide to TDD — starting from "explain it like I'm five" and ending with the stuff that actually trips people up.

🌐 **हिंदी में पढ़ें:** [hi/README.md](hi/README.md)

## Read in this order

| #   | Doc                                              | What it covers                                                |
| --- | ------------------------------------------------ | ------------------------------------------------------------- |
| 1   | [What is TDD?](01-what-is-tdd.md)                | The idea, in plain language. The sandwich analogy.            |
| 2   | [Red, Green, Refactor](02-red-green-refactor.md) | The three-step loop, and what each step is really for.        |
| 3   | [Writing good tests](03-writing-good-tests.md)   | Naming, structure, what to test, what not to test.            |
| 4   | [A worked example](04-worked-example.md)         | Building a shopping cart one failing test at a time.          |
| 5   | [Pitfalls & FAQ](05-pitfalls-and-faq.md)         | Where TDD goes wrong and the honest answers.                  |
| 6   | [Cheat sheet](06-cheat-sheet.md)                 | One page. Print it, pin it.                                   |
| 7   | [Why use TDD?](07-why-tdd.md)                    | The case for it, the economics, and when it isn't worth it.   |
| 8   | [Getting started](08-getting-started.md)         | Your first week. New projects, legacy code, team habits.      |
| 9   | [Language setup](09-language-setup.md)           | Nothing → failing test, in Python, JS/TS, Go, C#, Java, Rust. |
| 10  | [The benefits](10-benefits.md)                   | Full inventory, with the mechanism behind each one.           |

## Tutorials

Hands-on, structured as **phases** with numbered **steps**. Follow along at a keyboard.

| #   | Tutorial                                               | Time           | What you'll practise                                                                                                                                         |
| --- | ------------------------------------------------------ | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 11  | [Your first TDD feature](11-tutorial-first-feature.md) | 45–60 min      | Build a signup feature from nothing across 8 phases — the loop, triangulation, test doubles, outside-in, commit rhythm.                                      |
| 12  | [Practice katas](12-tutorial-katas.md)                 | 15–60 min each | Five graded katas (FizzBuzz → Bowling), each in phases, plus constraints to train specific skills.                                                           |
| 13  | [Adoption phases](13-adoption-phases.md)               | ~3 months      | The staged roadmap: groundwork → fluency → bug fixes → new code → legacy → team → sustaining. Each phase has a **mini-project** with a concrete deliverable. |

## In a big codebase

TDD across a real stack: Node/Express API, MongoDB, a React app, vanilla JS pages, and React Native — all against one backend.

| #   | Doc                                                    | What it covers                                                                                              |
| --- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| 14  | [Large-project strategy](14-large-project-strategy.md) | Test tiers and budgets, repo layout, shared test-support, isolation, what runs when, contract drift.        |
| 15  | [Node backend](15-tdd-node-backend.md)                 | Outside-in from a supertest acceptance test, the app factory, use cases and ports, queues, error contracts. |
| 16  | [MongoDB & Mongoose](16-tdd-mongodb-mongoose.md)       | Never mock Mongoose; the repository port + one contract suite run against in-memory _and_ real Mongo.       |
| 17  | [Frontend — vanilla & React](17-tdd-frontend-web.md)   | Behavioural queries, the four states, MSW instead of module mocks, testable vanilla JS modules.             |
| 18  | [API & network tests](18-tdd-api-network.md)           | One schema for server and clients; timeouts, retries, cancellation, offline, stale responses, canaries.     |
| 19  | [React Native](19-tdd-react-native.md)                 | Push logic off the platform, accessibility props as selectors, native-module adapters, offline sync.        |

## Short on time?

- **Just want the idea?** → [1. What is TDD?](01-what-is-tdd.md)
- **Want the full list of upsides?** → [10. The benefits](10-benefits.md)
- **Need to convince someone?** → [7. Why use TDD?](07-why-tdd.md)
- **Want to actually do it, now?** → [11. Your first TDD feature](11-tutorial-first-feature.md)
- **Ready to try it at work?** → [8. Getting started](08-getting-started.md) + [9. Language setup](09-language-setup.md)
- **Rolling it out to a team?** → [13. Adoption phases](13-adoption-phases.md)
- **Already doing it?** → [6. Cheat sheet](06-cheat-sheet.md) + [12. Katas](12-tutorial-katas.md)
- **Suite is slow and flaky at scale?** → [14. Large-project strategy](14-large-project-strategy.md)
- **Clients keep breaking when the API changes?** → [18. API & network tests](18-tdd-api-network.md)

## The whole thing in one sentence

> Write down how you'll know it works _before_ you build it — then build only enough to make that true.

## The loop

```
   ┌─────────────────────────────────────────┐
   │                                         │
   ▼                                         │
🔴 RED          →     🟢 GREEN     →    🔵 REFACTOR
write a failing      make it pass       clean it up
test                 (simplest way)     (tests still pass)
```

Each trip around the loop should take **minutes, not hours**. If a lap takes an afternoon, your step was too big.
