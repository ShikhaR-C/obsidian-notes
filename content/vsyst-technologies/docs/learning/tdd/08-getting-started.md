# 8. Getting started

How to actually start doing this — on a new project, on an old one, and with a team that hasn't bought in yet.

## Before your first test

Get these two things right or nothing else sticks:

**1. Make the suite fast.** Under a minute for the whole thing, under a second for the tests you're actively working on. Slow suites get skipped; skipped suites are worthless.

**2. Put it on watch mode.** The loop is only comfortable when feedback is instant. Split your screen — code on one side, a test runner rerunning on every save on the other.

```bash
pytest-watch              # Python
npx vitest                # JS/TS (watch is the default)
dotnet watch test         # C#
gotestsum --watch         # Go
```

See [Language setup](09-language-setup.md) for getting a runner working from cold.

---

## Your first week

Don't try to convert your whole workflow. Pick one narrow habit and do it until it's automatic.

### Day 1–2: bug fixes only

Next bug you get, before you fix anything:

1. Write a test that reproduces it. Watch it fail.
2. Fix the bug.
3. Watch it go green.

This is the easiest possible entry point. You already know the expected behaviour, the scope is tiny, and nobody will argue that a regression test was a waste of time.

### Day 3–4: one new function

Pick the next piece of pure logic you have to write — a calculation, a validator, a parser. Something with inputs and outputs and no database.

Do the full loop. Resist the urge to write the implementation first. It will feel slow and slightly stupid. That's normal and it passes.

### Day 5: refactor something under test

Take code you already have tests for and restructure it — extract a function, rename things, collapse a layer. Run the tests.

This is the step where TDD stops being an abstract argument and starts being _obviously worth it_. You need to feel it once.

---

## Starting on a brand-new project

Easiest case. Two rules:

- Write the first test **before the first line of production code** — including before the folder structure. It forces you to set up the runner on day one, when it's cheap.
- Start from the outside: what does a user of this thing want to call? Let the test define the API.

---

## Starting on an existing codebase with no tests

Do **not** try to retrofit tests across the whole thing. It's a huge project with no visible progress, and it always stalls.

Instead, let the tested area grow around the work you're already doing:

### Step 1 — pin the current behaviour

Write **characterization tests**: tests that capture what the code does _right now_, even if what it does is wrong.

```python
# Not asserting this is correct — asserting it's what happens today.
def test_legacy_pricing_current_behaviour():
    assert calculate_price(qty=3, code="LEGACY") == 27.5
```

Now you have a net. You can refactor without silently changing behaviour.

Don't know what it returns? Run it and find out, then paste the value in. That's legitimate here.

### Step 2 — find a seam

The usual blocker is that the code you want to test reaches straight out to a database, a clock, or an HTTP call. Find the smallest change that lets you substitute those — pass it in as an argument, or hide it behind an interface.

### Step 3 — apply the rule going forward

- Every **bug fix** gets a failing test first.
- Every **new** piece of logic is written test-first.
- Code you don't touch stays untested. That's fine.

After a few months, the parts of the codebase that change most often — which are the parts that matter — are the parts with tests.

> 📖 _Working Effectively with Legacy Code_ by Michael Feathers is the whole book on this, and it's worth reading if this is your situation.

---

## What "good" feels like

You'll know it's working when:

- You're rarely more than a few minutes from a green suite
- You open a debugger far less than you used to
- You refactor without a knot in your stomach
- A red test tells you what's wrong from the name alone
- Nobody re-runs CI hoping for a different result

## What "going wrong" feels like

- The suite takes so long you stop running it
- You routinely fix twenty tests after a refactor → [testing internals](03-writing-good-tests.md#test-behaviour-not-implementation)
- Tests fail randomly and everyone shrugs → [flakiness](05-pitfalls-and-faq.md#flaky-tests-left-in-place)
- You write tests after the code to satisfy a coverage gate → the gate is causing harm; talk about removing it

---

## Team practices worth adopting

**Keep the build green.** A permanently-red main branch trains everyone to ignore failures. If it goes red, fixing it is the top priority.

**Review the tests, not just the code.** In a pull request, read the test names first. If they don't tell you what the change does, ask for better ones.

**Delete tests that have stopped paying rent.** Tests are code with a maintenance cost. A test that's been commented out, or that asserts nothing, or that duplicates another — delete it. A smaller suite you trust beats a big one you don't.

**Don't set a coverage target.** Use coverage to find gaps and judge whether they matter. The moment it becomes a number people are measured on, you get tests written to touch lines rather than check behaviour.

**Pair on it early.** TDD is much easier to learn by watching someone do it for an hour than by reading about it — including this document.

---

Next: [Language setup →](09-language-setup.md)
