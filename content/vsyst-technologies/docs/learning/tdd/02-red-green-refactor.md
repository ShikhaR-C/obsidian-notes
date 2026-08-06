# 2. Red, Green, Refactor

The loop. Three steps, repeated forever, each one small.

```
   ┌─────────────────────────────────────────┐
   │                                         │
   ▼                                         │
🔴 RED          →     🟢 GREEN     →    🔵 REFACTOR
```

---

## 🔴 RED — write a failing test

Write one small test for behaviour that doesn't exist yet. Run it. **Watch it fail.**

```python
def test_empty_cart_costs_nothing():
    assert Cart().total() == 0
```

Right now there's no `Cart` at all, so this blows up. That's the point.

### Why watching it fail matters

This is the step people skip, and it's the one that earns the most. A test you've never seen fail is a test you can't trust. Maybe it's testing nothing. Maybe there's a typo in the assertion. Maybe the test runner isn't even picking up the file.

**Also check the failure message.** Is it clear? Would it tell a colleague at 4pm on a Friday what went wrong? If the message is `AssertionError: False is not True`, fix the test now — you'll be reading that message for years.

> 🔑 **Rule:** never write production code until you have a failing test asking for it.

---

## 🟢 GREEN — make it pass, the dumbest way possible

Write the _least_ code that turns the test green. Not the elegant version. Not the general version. The embarrassing version is fine.

```python
class Cart:
    def total(self):
        return 0
```

Yes, that's hardcoded. Yes, it's "wrong". It's also **green**, and that's the goal of this step.

### "But that's cheating!"

It isn't, and this is the most counter-intuitive part of TDD. The hardcoded return is honest: your test suite currently only demands that much. The next test will demand more, and the fake will be forced out.

This has a name: **triangulation**. One example lets you fake it. Two or three examples force the real logic to emerge.

The discipline here is to resist writing code you _imagine_ you'll need. Speculative code is where bugs and dead weight come from.

---

## 🔵 REFACTOR — clean it up

Now the tests are green, improve the code without changing what it does.

- Remove duplication (in production code **and** in the tests)
- Rename things now that you understand them better
- Extract a function, collapse a needless layer, simplify a conditional

Run the tests after each change. They're your seatbelt — this is exactly the moment they pay for themselves.

### The rules of refactoring

1. **Only refactor on green.** Never restructure while a test is failing; you won't know which change broke what.
2. **Don't add behaviour.** If you find yourself wanting new functionality, stop — that's a new RED.
3. **Refactor the tests too.** Test code is real code. It gets read more often than production code.

Refactoring is not optional. Skip it consistently and you get a codebase that passes all its tests and is miserable to work in.

---

## How big should a lap be?

**Minutes.** Ideally two to ten. If a full cycle takes an afternoon, your test was too ambitious — split it.

A useful check: if you've been red for more than ~15 minutes, revert to the last green and take a smaller bite. This feels like losing work. It's usually faster.

## The rhythm

Once it clicks, it feels like this:

```
fail → pass → tidy → fail → pass → tidy → fail → pass → tidy
 30s    2m     1m     45s    3m     0m     20s    1m     2m
```

Short, tight, low-drama. You're never more than a couple of minutes from working code, which means you're never debugging a mystery — the only thing that changed is the thing you just typed.

---

Next: [Writing good tests →](03-writing-good-tests.md)
