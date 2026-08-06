# 1. What is TDD?

## The five-year-old version

Imagine you're making a peanut butter sandwich for your friend. 🥪

**The normal way:** You make the sandwich, then ask "is this right?" Your friend says "I hate crusts!" Oops. Start over.

**The TDD way:** _Before_ you make anything, you write the rules on a sticky note:

- ✅ Must have peanut butter
- ✅ No crusts
- ✅ Cut in triangles

Now you make the sandwich and check your note. Every rule ticked? You got it right the first time.

That's it. **The sticky note is the test. You write it first.**

## The grown-up version

Test Driven Development is a discipline where you write an automated test that fails, then write the smallest amount of production code that makes it pass, then clean up — and you repeat that cycle in very small steps.

The important word is **discipline**, not _testing_. TDD is a way of designing software where tests happen to be the by-product. You end up with a test suite, but that's not the main prize.

## What you actually get

**A safety net.** Change something scary, and if you break it, a test yells at you in two seconds — instead of a customer yelling at you in two weeks.

**You can't forget to test.** You literally can't. The test came first.

**Better design, almost by accident.** Code that's hard to test is usually code that's badly designed — too many dependencies, doing too much, tangled up in global state. Writing the test first makes you feel that pain _before_ you've built on top of it.

**Living documentation.** A new person reads your tests and sees exactly what the code is supposed to do. Unlike comments, tests can't quietly go out of date — they break.

**Permission to refactor.** Most people are scared to clean up working code. With good tests, you're not guessing whether you broke something. You know in seconds.

## What TDD is _not_

- ❌ **Not "write lots of tests."** It's about _order_ — test first, code second.
- ❌ **Not 100% coverage as a goal.** Coverage is a symptom, not a target.
- ❌ **Not a replacement for thinking.** It won't design your architecture for you.
- ❌ **Not all-or-nothing.** Plenty of good teams use it for tricky logic and skip it for boilerplate.
- ❌ **Not only unit tests.** You can drive from an integration or acceptance test too.

## The mental shift

Before TDD, you ask: _"How do I build this?"_

With TDD, you ask first: _"How will I know this works?"_

Answering the second question well usually makes the first one much easier, because you've been forced to define "done" before you start.

---

Next: [Red, Green, Refactor →](02-red-green-refactor.md)
