# 4. A worked example

Let's build a shopping cart, one failing test at a time. Watch how the design emerges instead of being decided up front.

Examples are Python + pytest, but the rhythm is identical in any language.

---

## Lap 1 — an empty cart

### 🔴 Red

```python
# test_cart.py
from cart import Cart

def test_empty_cart_total_is_zero():
    assert Cart().total() == 0
```

```
ModuleNotFoundError: No module named 'cart'
```

Failing for the right reason. Good.

### 🟢 Green

The dumbest thing that works:

```python
# cart.py
class Cart:
    def total(self):
        return 0
```

```
1 passed ✅
```

### 🔵 Refactor

Nothing to clean yet. Move on.

---

## Lap 2 — one item

### 🔴 Red

```python
def test_cart_with_one_item_totals_that_item():
    cart = Cart()
    cart.add("pen", 3)
    assert cart.total() == 3
```

```
AttributeError: 'Cart' object has no attribute 'add'
```

Notice: **the test just designed the API.** We decided `add(name, price)` by writing how we wanted to call it, not by guessing in the implementation file.

### 🟢 Green

The hardcoded `0` can't survive. Real logic gets forced out:

```python
class Cart:
    def __init__(self):
        self._items = []

    def add(self, name, price):
        self._items.append((name, price))

    def total(self):
        return sum(price for _, price in self._items)
```

```
2 passed ✅
```

Both tests green — the first one still holds, because an empty list sums to 0.

---

## Lap 3 — quantities

### 🔴 Red

```python
def test_quantity_multiplies_the_price():
    cart = Cart()
    cart.add("pen", 3, quantity=4)
    assert cart.total() == 12
```

```
TypeError: add() got an unexpected keyword argument 'quantity'
```

### 🟢 Green

```python
    def add(self, name, price, quantity=1):
        self._items.append((name, price, quantity))

    def total(self):
        return sum(price * qty for _, price, qty in self._items)
```

```
3 passed ✅
```

The default of `1` keeps the earlier tests passing. That's the safety net doing its job — we changed a signature and knew instantly that nothing broke.

---

## Lap 4 — rejecting bad input

### 🔴 Red

```python
import pytest

def test_negative_quantity_is_rejected():
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add("pen", 3, quantity=-1)
```

```
Failed: DID NOT RAISE <class 'ValueError'>
```

### 🟢 Green

```python
    def add(self, name, price, quantity=1):
        if quantity < 1:
            raise ValueError(f"quantity must be at least 1, got {quantity}")
        self._items.append((name, price, quantity))
```

```
4 passed ✅
```

---

## Lap 5 — the discount rule

_"Orders over £100 get 10% off."_

### 🔴 Red

Start with the boundary, because boundaries are where bugs live:

```python
def test_no_discount_at_exactly_100():
    cart = Cart()
    cart.add("desk", 100)
    assert cart.total() == 100

def test_ten_percent_off_over_100():
    cart = Cart()
    cart.add("desk", 200)
    assert cart.total() == 180
```

The first passes already; the second fails. Both are worth keeping — the passing one pins down the boundary so nobody "fixes" it to `>=` later.

### 🟢 Green

```python
    def total(self):
        subtotal = sum(price * qty for _, price, qty in self._items)
        if subtotal > 100:
            return subtotal * 0.9
        return subtotal
```

```
5 passed ✅
```

### 🔵 Refactor

Now `total()` is doing two jobs, and there's a magic number. Clean it up — **on green**, with the tests watching:

```python
DISCOUNT_THRESHOLD = 100
DISCOUNT_RATE = 0.10

class Cart:
    def __init__(self):
        self._items = []

    def add(self, name, price, quantity=1):
        if quantity < 1:
            raise ValueError(f"quantity must be at least 1, got {quantity}")
        self._items.append((name, price, quantity))

    def subtotal(self):
        return sum(price * qty for _, price, qty in self._items)

    def total(self):
        subtotal = self.subtotal()
        return subtotal * (1 - DISCOUNT_RATE) if self._qualifies(subtotal) else subtotal

    def _qualifies(self, subtotal):
        return subtotal > DISCOUNT_THRESHOLD
```

```
5 passed ✅
```

Same behaviour, better shape. We know it's the same behaviour because the tests said so — not because we squinted at it.

---

## What just happened

Look back at what we never did:

- We never designed the `Cart` class up front. **Each test pulled the next piece of design out.**
- We never wrote code we didn't need. No `remove()`, no `Item` class, no currency handling — because nothing asked for them.
- We never debugged. When something went red, the cause was the ten lines we'd just written.
- We refactored twice with total confidence.

And we finished with five tests that document the rules in plain language:

```
test_empty_cart_total_is_zero
test_cart_with_one_item_totals_that_item
test_quantity_multiplies_the_price
test_negative_quantity_is_rejected
test_no_discount_at_exactly_100
test_ten_percent_off_over_100
```

That list _is_ the spec.

---

Next: [Pitfalls & FAQ →](05-pitfalls-and-faq.md)
