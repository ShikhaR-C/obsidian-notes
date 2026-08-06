# 5. Pitfalls & FAQ

## Common pitfalls

### Writing the test after the code

The most common failure, and it's usually unconscious — you sketch the implementation "just to think it through", then write a test that confirms whatever you built.

**Why it costs you:** you lose the design pressure (the test can no longer push back on a bad API) and you never see the test fail, so you don't know it works.

**Fix:** if you catch yourself doing it, delete the production code, keep the knowledge, and start from the test. It'll take four minutes.

---

### Tests glued to implementation details

Asserting on private fields, call ordering, or internal structure. Your suite goes red every time you refactor, even when behaviour is unchanged.

**The tell:** "I improved the code and had to fix thirty tests."

**Fix:** assert on outputs and observable effects. See [Writing good tests](03-writing-good-tests.md#test-behaviour-not-implementation).

---

### Steps that are too big

Writing a test for a whole feature, then disappearing for three hours to make it pass.

**The tell:** you've been red for ages and you're debugging.

**Fix:** revert to green, take a smaller bite. The smallest useful test is usually smaller than you think.

---

### Skipping the refactor step

Red, green, red, green, red, green — and six months later the code is a swamp that passes all its tests.

**Fix:** treat refactor as part of the cycle, not a nice-to-have. It's the step that converts tests into long-term speed.

---

### Mock-everything tests

You mock every collaborator, and now your test asserts that your code calls the functions you wrote it to call. It passes even when the feature is completely broken.

**Fix:** mock at real boundaries (network, clock, filesystem, third parties). Use real objects for your own code.

---

### Chasing a coverage number

Coverage targets create tests written to touch lines, not to check behaviour — assertion-free tests, tests of getters, tests nobody reads.

**Fix:** use coverage to _find_ untested areas, then judge whether they matter. 70% meaningful beats 95% theatrical.

---

### Flaky tests left in place

One test fails randomly. Everyone learns to re-run CI. Then a real failure gets re-run too.

**Fix:** treat a flaky test as a broken test. Fix it or delete it today.

---

## FAQ

**Doesn't this take twice as long?**

Writing takes longer. _Finishing_ usually doesn't. You trade time typing tests for time not spent debugging, not spent in manual QA loops, and not spent afraid to change things. Most teams find it roughly neutral in the short term and clearly positive after a few months — and the benefit compounds in code that lives a long time.

The honest caveat: for a throwaway prototype you'll delete on Friday, TDD is often a bad trade. Know which one you're writing.

---

**What if I don't know the design yet?**

That's the good case — TDD is a design tool. Write the test as though the ideal API already existed, and let that shape what you build. If you genuinely need to explore first, do a **spike**: hack freely with no tests, learn what you need, then _throw the spike away_ and rebuild it test-first. Discarding the spike is the part people skip and the part that matters.

---

**How do I test legacy code with no tests?**

Don't try to retrofit the whole thing. Use **characterization tests**: write a test that captures what the code currently does (even if that's wrong), so you have a net. Then refactor under it. Add proper TDD for every _new_ change and every bug fix. The tested area grows around the work you're already doing.

---

**Do I TDD everything?**

No. High value: business logic, calculations, parsing, state machines, anything with edge cases, anything that already broke once. Low value: thin config, generated code, straight-through CRUD with no rules, exploratory UI layout. Use judgement — dogma is not the point.

---

**How do I test UI?**

Push logic out of the view and TDD that part normally. For the view itself, use a lighter touch — a few component or end-to-end tests on critical paths. Trying to unit-test pixel layout is usually a bad investment.

---

**What about databases, HTTP, external services?**

Two tiers. Unit tests stub the boundary and run in milliseconds. A smaller set of integration tests hits a real (local or containerised) database or a recorded API, and runs less often. Both matter; keep them separate so the fast suite stays fast.

---

**My test passed the first time I ran it. Is that bad?**

It's a warning. Either the behaviour already existed (fine — you learned something), or the test isn't asserting what you think. Break the production code deliberately and confirm the test goes red. If it doesn't, the test is broken.

---

**Should a bug fix start with a test?**

Yes — this is TDD's easiest win. Write a test that reproduces the bug and fails. Fix it. Now the test is green _and_ that bug can never silently return.

---

**What's BDD? Is it different?**

Behaviour Driven Development is largely TDD with vocabulary chosen to keep the focus on behaviour and to be readable by non-developers — `given / when / then` instead of `arrange / act / assert`. Same loop, different emphasis. If your `assert`s already describe behaviour rather than internals, you're most of the way there.

---

Next: [Cheat sheet →](06-cheat-sheet.md)
