# 6. Cheat sheet

## The loop

| Step            | Do                                                              | Don't                                       |
| --------------- | --------------------------------------------------------------- | ------------------------------------------- |
| 🔴 **Red**      | Write one small failing test. Run it. Read the failure message. | Don't write production code yet.            |
| 🟢 **Green**    | Write the simplest thing that passes — hardcoding allowed.      | Don't build for imagined future needs.      |
| 🔵 **Refactor** | Remove duplication, rename, simplify. Tests stay green.         | Don't add behaviour. Don't refactor on red. |

**Target lap time: 2–10 minutes.** Red for 15+ minutes → revert to green, take a smaller bite.

---

## The three laws (Uncle Bob's phrasing)

1. Write no production code until you have a failing test.
2. Write no more of a test than is enough to fail.
3. Write no more production code than is enough to pass.

---

## Test template

```python
def test_<situation>_<expected outcome>():
    # Arrange
    ...
    # Act
    result = ...
    # Assert
    assert result == expected
```

---

## Checklist for any test

- [ ] Did I watch it fail first?
- [ ] Is the failure message useful at 4pm on a Friday?
- [ ] Does the name say what breaks?
- [ ] One reason to fail?
- [ ] Behaviour, not internals?
- [ ] Passes alone, and in any order?
- [ ] Fast — no sleeps, no real network?
- [ ] Deterministic — no real clock, no unseeded randomness?

---

## Edge cases worth a test

`empty` · `zero` · `one` · `many` · `negative` · `null / None` · `duplicate` · `maximum` · `boundary ±1` · `wrong type` · `unicode` · `concurrent`

---

## Smells and what they mean

| Smell                         | Likely cause                                           |
| ----------------------------- | ------------------------------------------------------ |
| Huge Arrange block            | Thing under test needs too much; too many dependencies |
| Test breaks on every refactor | Testing internals, not behaviour                       |
| Lots of mocks                 | Too many collaborators, or mocking your own code       |
| Flaky test                    | Time, randomness, shared state, or test order          |
| Test name is `test_thing_2`   | Two behaviours crammed into one test                   |
| Hard to write a test at all   | The design is telling you something — listen           |

---

## When to reach for TDD

**Yes:** business rules · calculations · parsing · state machines · edge-case-heavy code · bug fixes · anything long-lived

**Probably not:** throwaway prototypes · spikes you'll delete · pixel layout · generated code · trivial config

---

## Handy commands

```bash
# Python
pytest                          # run all
pytest -k "discount"            # run matching tests
pytest --lf                     # rerun last failures
pytest -x                       # stop at first failure
pytest -q --tb=short            # quiet, short tracebacks

# JavaScript / TypeScript
npx vitest --watch              # rerun on save
npx jest --watch
npx jest -t "discount"

# Go
go test ./... -run TestDiscount
```

Run your suite on **watch mode** while doing TDD. The loop is only comfortable when feedback is instant.

---

## Further reading

- _Test Driven Development: By Example_ — Kent Beck (the original; short and readable)
- _Growing Object-Oriented Software, Guided by Tests_ — Freeman & Pryce
- _Working Effectively with Legacy Code_ — Michael Feathers (for code that has no tests yet)
- _Refactoring_ — Martin Fowler (the blue step, in depth)
