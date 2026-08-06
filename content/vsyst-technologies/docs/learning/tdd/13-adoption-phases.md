# 13. Adoption phases

A staged roadmap for going from _"I've read about TDD"_ to _"this is just how we work."_

Each phase has a **goal**, **steps**, a **mini-project**, an **exit criterion**, and the **failure mode** that stalls most people there. Don't jump ahead — every phase is load-bearing for the next.

The mini-projects are the point. Reading a phase takes two minutes; the phase isn't done until the mini-project has produced something you can point at.

```
Phase 0 ──▶ Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5 ──▶ Phase 6
Ground-     Personal    Bug         New         Legacy      Team        Sustain
work        fluency     fixes       code        code        adoption
 1 day       1 week      2 weeks     1 month     ongoing     3 months    forever
◀──────── you, alone ────────▶ ◀─── your work ───▶ ◀──── everyone ────▶
```

---

## Phase 0 — Groundwork

**Goal:** remove the friction that kills the habit before it forms.
**Time:** a day, at most.

### Steps

1. **Get a runner working from one command.** Not an IDE button — a command, so CI can run it too. See [9. Language setup](09-language-setup.md).
2. **Get watch mode running.** Split-screen: code one side, results the other.
3. **Measure your current suite.** If it takes more than 60 seconds, fixing that _is_ phase 0. A slow suite defeats everything downstream.
4. **Make one test fail deliberately.** Confirm the failure message is useful and that you trust the tooling.

### 🛠 Mini-project — the starter kit

_Build a repo you can clone every time you want to try something. ~2 hours._

1. New empty repo. Add a runner and one test file with a single passing assertion ([9. Language setup](09-language-setup.md)).
2. Add **one** command that runs everything — a `Makefile` target, an npm script, a `justfile`. Name it `test`. Nobody should ever need to remember flags.
3. Add a second command, `test:watch`, and leave it running in a split pane while you do the rest.
4. Write a test that asserts `2 + 2 == 5`. Read the failure output. Can you tell _what_ failed, _where_, and _expected vs actual_ without scrolling? If not, fix the reporter config now — you'll read this output thousands of times.
5. Time a full run and put the number in the README. This is your budget for phase 6.
6. Wire the same one command into CI so local and CI can never disagree.
7. Tag it, or make it a template repo.

**Deliverable:** a `tdd-starter` repo, one command, watch mode, sub-second run, useful failure output.

**Proves:** the friction is gone. Every later mini-project starts by cloning this.

### ✅ Exit criterion

You can go from saving a file to seeing red or green in **under 5 seconds**.

### ⚠️ What stalls people here

Trying to start TDD on a codebase where the test suite takes 11 minutes. You will not build the habit. Fix the feedback loop first, even if that takes a week.

---

## Phase 1 — Personal fluency

**Goal:** make the loop automatic, away from the pressure of real work.
**Time:** about a week, 30 minutes a day.

### Steps

1. Work through [11. Your first TDD feature](11-tutorial-first-feature.md) end to end. Don't skip the phases.
2. Do [Kata 1 (FizzBuzz)](12-tutorial-katas.md#kata-1--fizzbuzz) three times on three different days. Repetition is the point.
3. Do [Kata 2 (String Calculator)](12-tutorial-katas.md#kata-2--string-calculator) once.
4. Deliberately hit the wall: try [Bowling](12-tutorial-katas.md#kata-5--bowling-game) and attempt strikes and spares in one leap. Feel it fail. That's the lesson about step size, and reading about it doesn't transfer.

### 🛠 Mini-project — the receipt splitter

_Something bigger than a kata, small enough to finish. Pure logic, no I/O. ~90 minutes, or three sittings._

Split a restaurant bill between people. Requirements arrive in order — **don't read ahead**, and take one lap per line.

1. 🔴🟢 A bill with one item and one person: that person owes the item price.
2. 🔴🟢 Two people, two items, each assigned to one person.
3. 🔴🟢 A shared item splits evenly between the people it's assigned to.
4. 🔴🟢 A tip percentage applies to everyone, proportional to their subtotal.
5. 🔴🟢 Rounding: totals are in whole cents, and the sum of everyone's share must equal the bill **exactly** — someone absorbs the leftover cent. Pin which one with a test.
6. 🔴🟢 An item assigned to nobody raises an error naming the item.
7. 🔵 Refactor to `Bill`, `Item`, `Share` (or your language's equivalent) — on green, with the tests untouched.

**Deliverable:** ~12 commits, each one lap. Skim `git log --oneline` afterwards: it should read as the requirements list, in order.

**Proves:** you can hold the loop for an hour without dropping into implementation-first. Step 5 is the one that pays — the rounding rule is nearly impossible to get right without a test, and everyone who writes it first gets it wrong.

### ✅ Exit criterion

You can complete a full red → green → refactor lap **without thinking about the order**, and writing the test first no longer feels backwards.

### ⚠️ What stalls people here

Trying to learn TDD _and_ ship a deadline feature at the same time. You'll fall back to old habits under pressure and conclude TDD doesn't work. Learn it on toy problems where nothing is at stake.

---

## Phase 2 — Bug fixes only

**Goal:** apply it to real work at the lowest-risk entry point.
**Time:** about two weeks, or your next 5–10 bugs.

### Steps

1. **Every bug, no exceptions:** reproduce it as a failing test _before_ you fix anything.
2. Commit the failing test on its own, then commit the fix. The two-commit diff shows exactly what was broken.
3. If you can't reproduce it in a test, that's information — the code needs a seam. Note where, but don't fix it yet.
4. Keep a tally. After ten bugs you'll have ten permanent regression tests and a feel for where the codebase resists testing.

### 🛠 Mini-project — the bug museum

_A running log, kept over your next ten bugs. ~15 minutes per bug, on top of the fix you were doing anyway._

1. Create `docs/bug-museum.md` in the real repo (or a private note if the team isn't there yet).
2. For every bug, before touching the fix, write the failing test and commit it alone: `test: reproduce #1234 — discount applied twice on renewal`.
3. Commit the fix separately. Two commits, always.
4. Add one row to the museum: **bug**, **the assertion that would have caught it**, **why no test existed**, **minutes to reproduce**.
5. When you _can't_ write the reproduction, that's the interesting case. Log it in a `SEAMS.md` list — file, what's hardcoded (clock, DB, HTTP, global), and the smallest change that would make it substitutable. Don't fix it. This list is phase 4's backlog.
6. After ten bugs, read the "why no test existed" column top to bottom and group the answers.

**Deliverable:** ten two-commit pairs, a ten-row table, and a `SEAMS.md` with three to six entries.

**Proves:** the value is no longer theoretical — you have ten regression tests that exist because of this habit, and the grouped column tells you exactly which part of the codebase is generating your bugs.

### ✅ Exit criterion

Ten bugs fixed test-first, and **you no longer have to remind yourself** to write the test.

### ⚠️ What stalls people here

Skipping it for "obvious one-line fixes." Those are exactly the ones that regress, because nobody remembers them six months later.

> This phase alone delivers a large share of TDD's value. If you adopt nothing else, adopt this.

---

## Phase 3 — New code

**Goal:** write new logic test-first by default.
**Time:** about a month.

### Steps

1. **Start with pure logic** — calculations, validators, parsers. No database, no network. Highest value, lowest difficulty.
2. **Add collaborators next.** Practise fakes for what you own and spies only at real boundaries ([11, Phase 4](11-tutorial-first-feature.md#phase-4--a-collaborator-and-test-doubles)).
3. **Try outside-in once.** Pick a ticket, write the acceptance test first, let it stay red while you drive inward ([11, Phase 5](11-tutorial-first-feature.md#phase-5--outside-in)).
4. **Refactor something under test, deliberately.** Restructure code you have tests for and feel the difference. This is the moment TDD stops being an argument and becomes obvious.
5. **Explicitly decide what to skip.** Config, thin plumbing, generated code, pixel layout. Deciding _not_ to TDD something is part of doing it well.

### 🛠 Mini-project — one real feature, outside-in

_A whole ticket from your actual backlog, done properly. Half a day to two days._

Pick a real ticket with **business rules and at least one collaborator** — a database, an HTTP client, a clock. Not a CRUD passthrough; there has to be a decision in it. Good candidates: a pricing or discount rule, an eligibility check, a notification-scheduling rule, an import validator.

1. Write the **acceptance test first**, at the outermost seam you can run fast (service method or HTTP handler, not the browser). Let it stay red for the whole feature — that's the target ([11, Phase 5](11-tutorial-first-feature.md#phase-5--outside-in)).
2. Drive inward. Every unit you need gets its own red → green → refactor lap.
3. Fake what you own — an in-memory repository, an injected `clock`. Spy only at the real boundary, and assert on the message you send, not on the calls in between ([11, Phase 4](11-tutorial-first-feature.md#phase-4--a-collaborator-and-test-doubles)).
4. When the last unit lands, the acceptance test goes green on its own. Do not touch it to make it pass.
5. **Now refactor under the tests.** Rename, extract, move things across files for ten minutes. Re-run after each move. This is step 4 of the phase, and skipping it skips the whole point.
6. Write a `NOT-TDD.md` note for this feature: what you deliberately didn't test-drive, and why. Two or three lines.

**Deliverable:** the ticket shipped, one acceptance test plus a handful of unit tests, and a refactor commit that changed structure with zero test edits.

**Proves:** the whole thing works together on real code with real dependencies — not just on katas. Step 5 is the one people remember.

### ✅ Exit criterion

Writing the implementation first now feels uncomfortable — like driving without a seatbelt.

### ⚠️ What stalls people here

Dogma. Trying to TDD absolutely everything, hitting something genuinely awkward (a UI animation, a framework integration), and giving up on the whole practice. Skip the bad fits.

---

## Phase 4 — Legacy code

**Goal:** make untested code workable without a rewrite project.
**Time:** ongoing, forever.

### Steps

1. **Do not attempt a retrofit project.** Blanket-testing an existing codebase is a huge effort with no visible progress and it always stalls.
2. **Pin behaviour with characterization tests** before you change anything — capture what the code does _today_, even if today is wrong ([8. Getting started](08-getting-started.md#step-1--pin-the-current-behaviour)).
3. **Find the seam.** Usually the blocker is a hardcoded database, clock, or HTTP call. Make the smallest change that lets you substitute it — pass it in as a parameter.
4. **Apply the rule going forward only:** bug fixes and new logic are test-first. Untouched code stays untested, and that's fine.
5. **Let coverage follow the work.** After a few months the parts that change most — the parts that matter — are the parts with tests.

### 🛠 Mini-project — rescue the scariest file

_One file. Not the codebase. One to three days, spread across whatever you were already doing there._

Take the top entry from the `SEAMS.md` you built in phase 2 — or run `git log --format=%n --name-only | sort | uniq -c | sort -rn | head` and pick the most-churned file with no tests.

1. **Pin it before you touch it.** Write characterization tests that capture what it does _today_, bugs included. Mark the wrong-looking ones `# characterization: current behaviour, probably wrong` ([8. Getting started](08-getting-started.md#step-1--pin-the-current-behaviour)).
2. If you can't call it at all, use a **golden-master** test: feed it 20–50 realistic inputs, dump the outputs to a file, assert the file doesn't change. Ugly and completely legitimate.
3. **Cut one seam.** The smallest possible change — promote the hardcoded clock/DB/HTTP call to a constructor or function parameter, defaulting to the current value so no caller changes. Commit that alone.
4. Now replace the golden master with a handful of real, readable tests that use the seam.
5. Make the change you actually came here to make — test-first, on top of the pinned behaviour.
6. Add three lines to `SEAMS.md`: what the seam was, how long it took, what it unblocked. This is the evidence for phase 5.

**Deliverable:** one previously-untestable file with a seam and a real test suite, and a change shipped through it.

**Proves:** legacy code isn't a different discipline — it's this discipline plus one pinning step. Repeat on the next file whenever work takes you there; never as a project of its own.

### ✅ Exit criterion

You can make a change in the scariest file in the repo without a knot in your stomach.

### ⚠️ What stalls people here

Waiting for permission to "do it properly." There's never a quarter set aside for it. The tested area has to grow around the work you were already doing.

---

## Phase 5 — Team adoption

**Goal:** make it a team habit rather than your personal one.
**Time:** about three months. Slower than you want.

### Steps

1. **Demonstrate, don't mandate.** Ship a few things visibly faster and more calmly. Let people ask.
2. **Pair for an hour.** TDD transfers far better by watching someone than by reading — including by reading these docs.
3. **Propose three narrow habits, not a policy:**
   - Every bug fix starts with a failing test
   - New business logic is written test-first
   - The suite runs in under a minute and stays green
4. **Change code review.** Read test names first. If they don't explain the change, ask for better ones.
5. **Own the build.** A permanently-red main branch trains everyone to ignore failures. Green is the top priority over new work.
6. **Kill flaky tests the day they appear.** Tolerated flakiness is how a real failure gets ignored.
7. **Run a team kata once a month.** 45 minutes, ping-pong pairing, no production pressure.

### 🛠 Mini-project — the four-week trial

_Not a proposal document. A time-boxed experiment with a number at each end. Four weeks plus prep._

1. **Measure first, quietly.** Before you propose anything, record for the last month: suite runtime, number of bugs reopened after a "fix", CI red-time on main, and how many PRs shipped with no test. You need a before.
2. **Run one 45-minute team kata.** [FizzBuzz](12-tutorial-katas.md#kata-1--fizzbuzz), ping-pong pairs, projector, no production code. Cheap, non-threatening, and it does more than any slide deck.
3. **Propose a four-week trial, not a policy** — the three narrow habits from step 3 above, with an explicit end date and an agreement to review the numbers and drop it if they don't move.
4. **Change the review template** for those four weeks: the first checklist line is "read the test names — do they explain the change?"
5. **Fix the build ritual.** Red main is the top of the queue, ahead of feature work. Whoever broke it fixes or reverts within the hour.
6. **At week four, publish the same four numbers**, before and after, with no spin. Then ask the team whether to keep going. Let them decide — a habit they voted for survives your holiday, a mandate doesn't.

**Deliverable:** a before/after table on four metrics, one kata run, and a team decision on record.

**Proves:** it works _here_, on this codebase, with these people — which is the only argument that ever actually lands.

### ✅ Exit criterion

Someone who isn't you asks _"where are the tests?"_ in a code review, unprompted.

### ⚠️ What stalls people here

Mandating a coverage percentage. It reliably produces tests written to touch lines rather than check behaviour, and it poisons the team against the practice. Use coverage to find gaps, never as a target.

---

## Phase 6 — Sustaining

**Goal:** stop the suite decaying into a liability.
**Time:** forever. This phase has no exit.

### Steps

1. **Guard suite speed like a budget.** When the fast tier creeps past a minute, treat it as a bug and fix it.
2. **Delete tests that have stopped paying rent** — commented out, assertion-free, duplicated. A smaller suite you trust beats a big one you don't.
3. **Watch for the coupling smell.** "I improved the code and had to fix thirty tests" means the tests assert on internals. Fix them or they'll block every future refactor.
4. **Quarantine flakes immediately**, out of the gating suite, then fix or delete within the week.
5. **Re-teach on every new hire.** The practice is one departure away from decaying if it lives in one person's head.
6. **Revisit the exceptions.** Areas you decided to skip may have grown real business rules since.

### 🛠 Mini-project — the suite health report

_Automate the thing nobody remembers to do. A day to build, ten minutes a month to read._

1. Write a script — `tools/suite-health` — that prints, from one command:
   - total runtime of the fast tier, and **pass/fail against the budget** you wrote down in phase 0
   - the **10 slowest tests**, with times
   - tests with **no assertions**, and tests that are skipped or commented out, with the date they were disabled
   - **flake rate** per test from the last 200 CI runs (same commit, different result)
2. Run it against the suite today and fix the worst item. Just one.
3. Add a CI job that **fails the build** if the fast tier exceeds the budget. A soft warning gets ignored within a month; that's the whole reason this phase exists.
4. Add a quarantine path: a flake gets tagged out of the gating suite the day it's spotted, and the tag carries an owner and a date. Anything still quarantined after 14 days gets deleted.
5. Put the report on a monthly calendar invite with the team, 10 minutes. One decision per finding: fix, delete, or accept.
6. Once a quarter, re-read `NOT-TDD.md` from phase 3 — the skipped areas — and check whether any has grown real business rules.

**Deliverable:** a checked-in script, a build that fails on a slow suite, and a dated 10-minute monthly review.

**Proves:** decay is now visible before it's painful. This phase has no exit criterion because the report never stops being worth reading.

### ⚠️ What stalls people here

Success. The suite works, nobody thinks about it, it slowly gets slower and flakier, and eighteen months later people are re-running CI hoping for a different result.

---

## The mini-projects at a glance

| Phase | Mini-project                 | Effort                   | You end up with                                            |
| ----- | ---------------------------- | ------------------------ | ---------------------------------------------------------- |
| 0     | The starter kit              | ~2 hrs                   | A clonable repo: one command, watch mode, sub-second run   |
| 1     | The receipt splitter         | ~90 min                  | ~12 commits, one per lap, all pure logic                   |
| 2     | The bug museum               | 15 min × 10 bugs         | 10 regression tests, a causes table, `SEAMS.md`            |
| 3     | One real feature, outside-in | ½–2 days                 | A shipped ticket, acceptance + unit tests, a free refactor |
| 4     | Rescue the scariest file     | 1–3 days                 | One legacy file with a seam and real tests                 |
| 5     | The four-week trial          | 4 weeks                  | Before/after numbers and a team decision                   |
| 6     | The suite health report      | 1 day, then 10 min/month | A script, a budget-enforcing CI job, a monthly review      |

They chain: phase 0's repo hosts phase 1's project, phase 2's `SEAMS.md` picks phase 4's target, phase 5's argument runs on phase 2–4's evidence, and phase 6 polices the budget phase 0 set.

---

## Where are you now?

| Signal                                                    | You're in   |
| --------------------------------------------------------- | ----------- |
| Suite takes minutes; nobody runs it locally               | **Phase 0** |
| You understand TDD but revert to old habits on real work  | **Phase 1** |
| You test-first sometimes, when it's convenient            | **Phase 2** |
| Bug fixes are always test-first; new code sometimes       | **Phase 3** |
| You test-first by default but the old code is untouchable | **Phase 4** |
| You do it well; the rest of the team doesn't              | **Phase 5** |
| The team does it, and the suite is getting slower         | **Phase 6** |

---

## Realistic timeline

| Month | What's true                                                                         |
| ----- | ----------------------------------------------------------------------------------- |
| 1     | You're slower. This is the dip. It's normal and it ends.                            |
| 2     | Bug fixes are test-first automatically. Debugging is noticeably down.               |
| 3     | You refactor without fear. Break-even on time.                                      |
| 6     | Onboarding is cheaper. The test names are the spec.                                 |
| 12+   | The codebase is still pleasant to work in — the benefit that dwarfs all the others. |

The costs are **upfront and visible**. The benefits are **spread out and invisible** — nobody files a ticket for the outage that didn't happen. Expect to have to make that case out loud more than once.

---

Related: [7. Why use TDD?](07-why-tdd.md) · [8. Getting started](08-getting-started.md) · [10. The benefits](10-benefits.md) · [11. Tutorial](11-tutorial-first-feature.md)
