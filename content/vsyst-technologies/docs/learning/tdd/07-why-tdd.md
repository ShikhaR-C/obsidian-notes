# 7. Why use TDD?

The case for it — including the parts where it isn't worth it. Written to be handed to a skeptical teammate or manager.

## The one-line version

> TDD isn't mainly about catching bugs. It's about staying fast in code you'd otherwise be afraid to touch.

---

## The six reasons, in order of how much they matter

### 1. You can change code without fear

Every codebase eventually reaches the point where someone says _"don't touch that file, it works."_ That's where projects go to die — the code calcifies because nobody can prove a change is safe, so features get bolted on the outside instead of fixed on the inside.

With a real test suite you make the change and know in three seconds. That is the difference between a codebase that gets better over time and one that only ever gets worse.

**This is the whole argument.** Everything below is a bonus.

### 2. Debugging mostly disappears

When you work in five-minute laps, a failure has exactly one possible cause: the ten lines you just wrote. You never hit _"something broke somewhere in the last 300 lines"_ — which is where the genuinely expensive hours go.

The time you "lose" writing tests is largely time you were going to spend in a debugger anyway, moved earlier and made much cheaper.

### 3. It forces you to define "done" before you start

Writing the test first makes you answer _"how will I know this works?"_ before _"how do I build it?"_

That question surfaces the ambiguity in a requirement while it's still free to fix — not after you've built the wrong thing and shown it to someone.

### 4. Hard-to-test code is badly designed code

If a test needs forty lines of setup, the design is telling you the thing has too many dependencies and does too much.

Test-first means you feel that pain **before** you've built three features on top of it. Test-after means you discover it when fixing it is expensive, so you don't.

### 5. The tests document what the code actually does

Comments drift out of date silently. Wikis rot. Tests **break**.

A test suite is the only documentation that gets automatically invalidated the moment it becomes a lie. A new joiner reads the test names and sees the rules of the system.

### 6. Bugs stop coming back

Every fix starts with a test that reproduces the bug. That bug is now permanently dead — not dead-until-someone-refactors-that-module-in-eight-months.

---

## The economics

The usual objection is "we don't have time." Here's the shape of the trade:

|                         | Without TDD                        | With TDD                            |
| ----------------------- | ---------------------------------- | ----------------------------------- |
| Writing the feature     | Faster                             | Slower (roughly 15–35% more typing) |
| Finding the bug         | Later — QA, staging, or production | Immediately, at your desk           |
| Cost of that bug        | Rises sharply the later it's found | Near zero                           |
| Changing it in 6 months | Slow and scary; often avoided      | Routine                             |
| Onboarding someone      | Read the code and hope             | Read the tests                      |

The cost is **upfront and visible**. The benefit is **spread out and invisible** — nobody files a ticket for the outage that didn't happen. That asymmetry is the entire reason TDD is a hard sell, and it's worth naming directly rather than pretending the upfront cost isn't real.

Research on this is mixed but broadly consistent: teams tend to spend somewhat more time writing, and see meaningfully fewer defects. The effect grows with how long the code lives.

---

## The honest counter-case

TDD is a **bad trade** when:

- **It's a prototype you'll delete.** Tests for throwaway code are throwaway work.
- **You genuinely don't know what you're building.** Explore with a spike first — untested, fast, and thrown away — _then_ rebuild it test-first.
- **The code is trivial.** Config, plumbing, straight CRUD with no rules. Nothing to assert that isn't just restating the code.
- **The output is inherently hard to assert on.** Pixel layout, visual design, feel.

And it has real costs:

- **It's slower for the first few weeks** while the habit forms. That dip is normal and it does end.
- **A bad suite is worse than no suite.** Over-mocked tests coupled to internals will fight every refactor and train the team to distrust red. See [Pitfalls](05-pitfalls-and-faq.md).
- **It doesn't design your architecture.** It gives feedback on the design you're choosing; it won't choose it for you.
- **Green tests are not proof of correctness.** They prove the cases you thought of still work.

---

## The decision rule

Two questions:

1. **How long will this code live?**
2. **How often will it change?**

```
                    changes often
                          ▲
          spike / demo    │    ★ TDD pays back
          (skip it)       │      many times over
                          │
    short-lived ──────────┼────────── long-lived
                          │
          throwaway       │    tests worth having,
          script          │    TDD optional
                          ▼
                    changes rarely
```

Top-right quadrant is where TDD earns its keep, and it's where most real production code sits.

---

## If you're pitching this to a team

Don't ask for a policy. Policies create resentment and coverage-number theatre.

Ask for three narrow, high-value habits instead:

1. **Every bug fix starts with a failing test.** Impossible to argue with, and immediately valuable.
2. **New business logic gets tests first.** Not UI, not config — the rules.
3. **The suite runs in under a minute** and stays green. A slow or flaky suite kills adoption faster than any argument.

That gets you most of the benefit with none of the dogma, and it's much easier to say yes to.

---

Next: [Getting started →](08-getting-started.md)
