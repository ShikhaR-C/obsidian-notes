# 3. Writing good tests

A test suite is an asset until it becomes a liability. The difference is craft.

## Structure: Arrange, Act, Assert

Every test has three beats. Keep them visually separate.

```python
def test_discount_applies_to_orders_over_100():
    # Arrange — set up the world
    cart = Cart()
    cart.add(Item("desk", price=120))

    # Act — do the one thing under test
    total = cart.total()

    # Assert — check the outcome
    assert total == 108  # 10% off
```

If your **Arrange** block is enormous, that's a design smell — the thing under test probably needs too much to exist.

If you have **multiple Acts**, you probably have multiple tests hiding in one.

## Naming

The name should say what breaks when it goes red, so you can read the CI output and not open the file.

| ❌ Bad          | ✅ Good                                     |
| --------------- | ------------------------------------------- |
| `test_cart`     | `test_empty_cart_total_is_zero`             |
| `test_1`        | `test_expired_coupon_is_rejected`           |
| `test_it_works` | `test_negative_quantity_raises_value_error` |

A pattern that holds up: **`test_<situation>_<expected outcome>`**.

## One reason to fail

Each test should check one behaviour. Not one assertion necessarily — one _reason to fail_.

```python
# Fine: several assertions, one behaviour
def test_new_user_starts_with_empty_profile():
    user = User("ada")
    assert user.name == "ada"
    assert user.posts == []
    assert user.verified is False
```

```python
# Not fine: three unrelated behaviours in one test
def test_user_stuff():
    assert User("ada").name == "ada"
    assert login("ada", "wrong") is False
    assert delete_user("ada") is True
```

When the second one goes red, you don't know what's broken until you read the whole thing.

## Test behaviour, not implementation

This is the single biggest lever on whether your suite ages well.

```python
# ❌ Coupled to internals — breaks when you rename a private field
def test_add_item():
    cart = Cart()
    cart.add(Item("pen", 2))
    assert cart._items[0]._price == 2

# ✅ Coupled to behaviour — survives refactoring
def test_add_item():
    cart = Cart()
    cart.add(Item("pen", 2))
    assert cart.total() == 2
```

**The test:** if you rewrite the internals but keep the behaviour identical, do your tests still pass? If they all break, they were testing the wrong thing — and they'll fight you every time you try to improve the code.

## What to test

**Do test:**

- Business rules and calculations
- Edge cases — empty, zero, one, many, negative, null, huge
- Error paths — what happens when it's given garbage
- Bugs you've fixed (write the failing test first, _then_ fix — that's TDD too)

**Don't bother testing:**

- The language or the standard library
- Third-party frameworks (test _your_ use of them, not them)
- Trivial getters and setters with no logic
- Exact wording of log messages nobody asserts on

## Keep tests fast

Slow tests get skipped. Skipped tests are worthless.

Aim for a unit suite that runs in **seconds**. Reach for real databases, network calls, and `sleep()` only when you're genuinely testing integration — and keep those in a separate, slower tier you run less often.

```
      /\        few, slow, high confidence
     /  \       End-to-end
    /----\
   /      \     Integration
  /--------\
 /          \   Unit — many, fast, cheap
/____________\
```

You don't have to be religious about the exact shape, but the principle holds: most of your feedback should come from the fast layer.

## Tests must be deterministic

A test that fails one run in twenty is worse than no test — it trains everyone to ignore red.

Usual culprits:

- Real clocks (`now()`) → inject the time
- Random values → seed them, or assert on properties not exact values
- Shared state between tests → each test sets up its own world
- Test order dependence → tests must pass in any order, and alone
- Real network → stub the boundary

## Don't over-mock

Mocks are useful at genuine boundaries: the network, the filesystem, the clock, payment providers.

Mock everything else and you end up asserting that your code calls the functions you wrote it to call — a test that passes no matter how broken the real behaviour is.

> Rule of thumb: mock things you **don't own**. Use the real thing for things you do.

---

Next: [A worked example →](04-worked-example.md)
