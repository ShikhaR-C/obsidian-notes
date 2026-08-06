# 9. Language setup

Getting from nothing to a failing test, in the major languages. Same example everywhere: an empty cart totals zero.

---

## Python — pytest

```bash
pip install pytest pytest-watch
```

```
project/
├── cart.py
└── test_cart.py        # files must start with test_
```

```python
# test_cart.py
from cart import Cart

def test_empty_cart_total_is_zero():
    assert Cart().total() == 0
```

```bash
pytest                  # run all
pytest -k discount      # run matching
pytest --lf             # rerun last failures
pytest -x -q            # stop at first failure, quiet
ptw                     # watch mode
```

**Expecting an error:**

```python
import pytest

def test_negative_quantity_rejected():
    with pytest.raises(ValueError, match="at least 1"):
        Cart().add("pen", 3, quantity=-1)
```

**Table-driven:**

```python
@pytest.mark.parametrize("subtotal,expected", [
    (50, 50), (100, 100), (200, 180),
])
def test_discount(subtotal, expected):
    assert apply_discount(subtotal) == expected
```

---

## JavaScript / TypeScript — Vitest

```bash
npm install -D vitest
```

```json
// package.json
{ "scripts": { "test": "vitest", "test:run": "vitest run" } }
```

```
project/
├── cart.ts
└── cart.test.ts
```

```typescript
import { describe, it, expect } from "vitest"
import { Cart } from "./cart"

describe("Cart", () => {
  it("totals zero when empty", () => {
    expect(new Cart().total()).toBe(0)
  })
})
```

```bash
npm test                # watch mode by default
npm test -- -t discount # run matching
npm run test:run        # single run, for CI
```

**Expecting an error:**

```typescript
it("rejects negative quantity", () => {
  expect(() => new Cart().add("pen", 3, -1)).toThrow(/at least 1/)
})
```

**Table-driven:**

```typescript
it.each([
  [50, 50],
  [100, 100],
  [200, 180],
])("discount(%i) === %i", (subtotal, expected) => {
  expect(applyDiscount(subtotal)).toBe(expected)
})
```

> Jest works essentially identically — same `describe / it / expect`. Vitest is faster and needs less config, so prefer it for new projects.

---

## Go — the standard library

No install needed.

```
project/
├── cart.go
└── cart_test.go        # must end in _test.go
```

```go
package cart

import "testing"

func TestEmptyCartTotalIsZero(t *testing.T) {
    got := New().Total()
    if got != 0 {
        t.Errorf("Total() = %d, want 0", got)
    }
}
```

```bash
go test ./...                   # all packages
go test -run TestDiscount       # run matching
go test -v                      # verbose
go test -race ./...             # catch data races
```

**Table-driven** — this is idiomatic Go and worth using by default:

```go
func TestDiscount(t *testing.T) {
    tests := []struct {
        name     string
        subtotal int
        want     int
    }{
        {"below threshold", 50, 50},
        {"at threshold", 100, 100},
        {"above threshold", 200, 180},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := ApplyDiscount(tt.subtotal); got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

---

## C# — xUnit

```bash
dotnet new xunit -o Cart.Tests
dotnet add Cart.Tests reference Cart/Cart.csproj
```

```csharp
using Xunit;

public class CartTests
{
    [Fact]
    public void EmptyCart_TotalIsZero()
    {
        Assert.Equal(0, new Cart().Total());
    }
}
```

```bash
dotnet test
dotnet test --filter Discount
dotnet watch test               # watch mode
```

**Expecting an error:**

```csharp
[Fact]
public void NegativeQuantity_Throws()
{
    Assert.Throws<ArgumentException>(() => new Cart().Add("pen", 3, -1));
}
```

**Table-driven:**

```csharp
[Theory]
[InlineData(50, 50)]
[InlineData(100, 100)]
[InlineData(200, 180)]
public void Discount(int subtotal, int expected)
{
    Assert.Equal(expected, Pricing.ApplyDiscount(subtotal));
}
```

---

## Java — JUnit 5

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <scope>test</scope>
</dependency>
```

```java
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class CartTest {
    @Test
    void emptyCartTotalIsZero() {
        assertEquals(0, new Cart().total());
    }
}
```

```bash
mvn test
mvn test -Dtest=CartTest
./gradlew test --continuous      # watch mode with Gradle
```

**Table-driven:**

```java
@ParameterizedTest
@CsvSource({"50,50", "100,100", "200,180"})
void discount(int subtotal, int expected) {
    assertEquals(expected, Pricing.applyDiscount(subtotal));
}
```

---

## Rust — built in

```
src/
└── lib.rs
```

```rust
pub fn total(items: &[u32]) -> u32 {
    items.iter().sum()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_cart_total_is_zero() {
        assert_eq!(total(&[]), 0);
    }

    #[test]
    #[should_panic(expected = "at least 1")]
    fn negative_quantity_rejected() {
        add("pen", 3, 0);
    }
}
```

```bash
cargo test
cargo test discount
cargo watch -x test
```

---

## Whatever your language

The three things you need before you start:

1. **A runner you can invoke in one command** — no IDE clicking, so CI can run it too
2. **Watch mode** — reruns on save
3. **A fast subset** — some way to run just the tests you're working on (`-k`, `-t`, `-run`, `--filter`)

Everything else is detail.

---

Back to the [README](README.md) · [Cheat sheet](06-cheat-sheet.md)
