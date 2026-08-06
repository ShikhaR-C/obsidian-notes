# 12. Tutorial — practice katas

A **kata** is a small problem you solve repeatedly to build muscle memory. The goal isn't the solution — you'll know it after the first attempt. The goal is the **rhythm**: red, green, refactor, small steps, no shortcuts.

Each kata below is laid out in **phases**, and each phase in **numbered steps**. Work them in order; they get harder.

> **The rules for every kata**
>
> 1. Never write production code without a failing test.
> 2. Watch every test fail before you make it pass.
> 3. Write the _dumbest_ code that passes. Hardcoding is allowed.
> 4. Refactor only on green.
> 5. If you're red for 15+ minutes, revert and take a smaller step.

---

## Kata 1 — FizzBuzz

**Difficulty:** ★☆☆☆☆ · **Time:** 15 min · **Teaches:** the raw loop, triangulation

_Return `"Fizz"` for multiples of 3, `"Buzz"` for multiples of 5, `"FizzBuzz"` for multiples of both, otherwise the number as a string._

### Phase 1 — The trivial case

1. 🔴 Write `test_one_returns_1` expecting `"1"`. Run it. Watch it fail.
2. 🟢 Make it pass with `return "1"`. Yes, really.
3. 🔵 Nothing to clean.

### Phase 2 — Force the fake out

1. 🔴 Add `test_two_returns_2`.
2. 🟢 The hardcoded `"1"` dies. Write `return str(n)`.
3. 🔵 Still clean.

### Phase 3 — Fizz

1. 🔴 `test_three_returns_fizz`.
2. 🟢 Add the `if n % 3 == 0` branch.
3. 🔴 `test_six_returns_fizz` — confirms you wrote a rule, not a special case.

### Phase 4 — Buzz, then FizzBuzz

1. 🔴🟢 Repeat phase 3 for 5 → `"Buzz"`.
2. 🔴 `test_fifteen_returns_fizzbuzz`. **This will fail** if you wrote your branches in the wrong order — that's the lesson.
3. 🟢 Fix the ordering.

### Phase 5 — Refactor

1. Collapse the branches into an accumulator (`result = ""` then append), on green.
2. Rewrite the tests as one parameterised table.
3. Run. Still green — you changed shape, not behaviour.

> ✅ **Done when:** the whole suite is one table and the implementation is under 8 lines.

---

## Kata 2 — String Calculator

**Difficulty:** ★★☆☆☆ · **Time:** 30–45 min · **Teaches:** incremental requirements, edge cases, resisting speculation

_Write `add(numbers: str) -> int`._ Requirements arrive **one at a time** — do not read ahead.

### Phase 1 — Empty and single

1. 🔴 `add("")` returns `0`.
2. 🟢 `return 0`.
3. 🔴 `add("1")` returns `1`.
4. 🟢 Real parsing now.

### Phase 2 — Two numbers, then many

1. 🔴 `add("1,2")` returns `3`.
2. 🟢 Split on comma, sum.
3. 🔴 `add("1,2,3,4,5")` returns `15`. **If this already passes, you generalised correctly** — that's fine, note it and move on.

### Phase 3 — Newlines as separators

1. 🔴 `add("1\n2,3")` returns `6`.
2. 🟢 Handle both delimiters.
3. 🔵 Extract a `_split` helper if the parsing is getting noisy.

### Phase 4 — Custom delimiter

_Input may start with `//;\n` to declare `;` as the delimiter._

1. 🔴 `add("//;\n1;2")` returns `3`.
2. 🟢 Parse the header, then delegate to your existing split.
3. 🔵 Notice how much easier this was because phase 3 already isolated the parsing.

### Phase 5 — Errors

1. 🔴 `add("1,-2")` raises with message `"negatives not allowed: -2"`.
2. 🟢 Implement.
3. 🔴 `add("1,-2,-5")` lists **all** negatives: `"negatives not allowed: -2, -5"`.
4. 🟢 Collect, then raise.

### Phase 6 — Ignore large numbers

1. 🔴 `add("2,1001")` returns `2` — numbers over 1000 are ignored.
2. 🟢 Filter.
3. 🔵 Final refactor pass over both test and production code.

> ✅ **Done when:** each requirement took one lap, and you never wrote code for a requirement you hadn't been given yet.

---

## Kata 3 — Roman Numerals

**Difficulty:** ★★★☆☆ · **Time:** 30 min · **Teaches:** letting an algorithm emerge instead of designing it up front

_Convert 1–3999 into Roman numerals._

### Phase 1 — One at a time

1. 🔴🟢 `1` → `"I"`. Hardcode it.
2. 🔴🟢 `2` → `"II"`.
3. 🔴🟢 `3` → `"III"`. Resist writing a loop yet.

### Phase 2 — The first pattern

1. 🔴 `5` → `"V"`.
2. 🟢 Whatever passes.
3. 🔴 `6` → `"VI"`, then `8` → `"VIII"`.
4. 🔵 **Now** a pattern should be visible. Refactor toward a value→symbol table.

### Phase 3 — Subtractive cases

1. 🔴 `4` → `"IV"`.
2. 🟢 The trick: add `4 → "IV"` as an entry in the same table. No special case needed.
3. 🔴 `9` → `"IX"`. Same move.

### Phase 4 — Scale up

1. 🔴🟢 `40`, `90`, `400`, `900`, `1000`.
2. 🔴 `1994` → `"MCMXCIV"`.
3. 🔵 The implementation should now be a table plus a five-line greedy loop.

> ✅ **Done when:** there are no `if` statements branching on specific numbers — just the table.
>
> 💡 **The lesson:** almost nobody designs the table up front. It _emerges_ around phase 2 if you take small enough steps.

---

## Kata 4 — Bank Account

**Difficulty:** ★★★☆☆ · **Time:** 45 min · **Teaches:** state, invariants, test doubles at a boundary

_Deposit, withdraw, print a statement._

### Phase 1 — Balance

1. 🔴 New account has balance `0`.
2. 🔴🟢 `deposit(100)` → balance `100`.
3. 🔴🟢 `withdraw(30)` → balance `70`.

### Phase 2 — Invariants

1. 🔴 `withdraw` more than the balance raises `InsufficientFunds`.
2. 🔴 `deposit(-5)` raises `ValueError`.
3. 🔴 `deposit(0)` — decide the rule, then write the test that pins it.
4. 🔵 Extract the validation.

### Phase 3 — The clock is a boundary

Statements need dates, and a real clock makes tests non-deterministic.

1. 🔴 Write `test_statement_shows_transaction_date` — it needs a _fixed_ date.
2. 🟢 Inject the clock: `Account(clock=lambda: date(2026, 1, 15))`.
3. 🔵 Note what you did — you replaced an uncontrollable dependency with a parameter. That's the standard move for time, randomness, and IDs.

### Phase 4 — Statement formatting

1. 🔴 Empty account prints only the header row.
2. 🔴 One deposit prints one line, correctly formatted.
3. 🔴 Multiple transactions print in **reverse chronological** order.
4. 🔵 Split "what happened" (the transaction list) from "how it looks" (the formatter). Two objects, tested separately.

> ✅ **Done when:** every test is deterministic — no `date.today()`, no `random`, and the suite passes at any hour of any day.

---

## Kata 5 — Bowling Game

**Difficulty:** ★★★★☆ · **Time:** 45–60 min · **Teaches:** working in tiny steps through genuinely tricky logic

_Score a game of ten-pin bowling. Strikes and spares carry bonuses forward._

### Phase 1 — The gutter game

1. 🔴 20 rolls of `0` scores `0`.
2. 🟢 `return 0`.

### Phase 2 — All ones

1. 🔴 20 rolls of `1` scores `20`.
2. 🟢 Sum the rolls.

### Phase 3 — One spare

1. 🔴 `5, 5, 3` then all zeros scores `16`.
2. 🟢 **Do not** try to handle strikes at the same time. One rule per lap.
3. 🔵 Introduce frame-based iteration if the index arithmetic is getting hard to read.

### Phase 4 — One strike

1. 🔴 `10, 3, 4` then all zeros scores `24`.
2. 🟢 Add the strike branch.

### Phase 5 — The perfect game

1. 🔴 12 rolls of `10` scores `300`.
2. 🟢 This is the one that catches off-by-one errors in the tenth frame.
3. 🔵 Final cleanup — extract `_is_strike`, `_is_spare`, `_frame_score`.

> ✅ **Done when:** the perfect game passes and the code reads like the rules of bowling.
>
> ⚠️ **The trap:** almost everyone tries to solve strikes and spares in one leap around phase 3, gets stuck for 40 minutes, and learns why small steps exist. Let yourself hit it once.

---

## How to practise

### Phase 1 — First run

1. Pick Kata 1. Follow the phases exactly as written.
2. Time yourself. Don't optimise for speed — optimise for **never skipping a red**.

### Phase 2 — Repeat with constraints

Redo a kata you've already solved, with one added rule:

| Constraint                                         | What it trains                 |
| -------------------------------------------------- | ------------------------------ |
| **No `if` statements**                             | Polymorphism and lookup tables |
| **Every method ≤ 3 lines**                         | Extracting relentlessly        |
| **Revert on red after 2 min**                      | Genuinely small steps          |
| **No mouse**                                       | Fluency in your editor         |
| **Ping-pong** (one writes red, other writes green) | Pairing                        |

### Phase 3 — Make it a habit

1. One kata a week, 30 minutes.
2. Rotate through them — repetition is the point, not novelty.
3. Once a month, do one in a **language you don't know well**. It exposes how much of your speed is habit versus understanding.

---

## Where to find more

- **codingdojo.org** — the original catalogue of katas
- **cyber-dojo.org** — run katas in the browser, any language, no setup
- **exercism.io** — exercises with mentor feedback
- _Test Driven Development: By Example_ — Kent Beck. The first half is one long kata, worked properly.

---

Back to: [11. Your first TDD feature](11-tutorial-first-feature.md) · [6. Cheat sheet](06-cheat-sheet.md) · [README](README.md)
