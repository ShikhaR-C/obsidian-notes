# 9. भाषा के अनुसार सेटअप

मुख्य भाषाओं में शून्य से एक फेल होते टेस्ट तक पहुँचना। उदाहरण हर जगह एक ही: ख़ाली कार्ट का कुल शून्य होता है।

---

## Python — pytest

```bash
pip install pytest pytest-watch
```

```
project/
├── cart.py
└── test_cart.py        # फ़ाइलों का नाम test_ से शुरू होना चाहिए
```

```python
# test_cart.py
from cart import Cart

def test_empty_cart_total_is_zero():
    assert Cart().total() == 0
```

```bash
pytest                  # सब चलाएँ
pytest -k discount      # मेल खाते चलाएँ
pytest --lf             # पिछले फ़ेल्योर दोबारा चलाएँ
pytest -x -q            # पहले फ़ेल्योर पर रुकें, शांत output
ptw                     # watch mode
```

**किसी error की अपेक्षा:**

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
npm test                # डिफ़ॉल्ट रूप से watch mode
npm test -- -t discount # मेल खाते चलाएँ
npm run test:run        # एक बार चलाएँ, CI के लिए
```

**किसी error की अपेक्षा:**

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

> Jest लगभग बिल्कुल इसी तरह काम करता है — वही `describe / it / expect`। Vitest तेज़ है और कम config माँगता है, इसलिए नए प्रोजेक्ट में उसे प्राथमिकता दीजिए।

---

## Go — standard library

कुछ install करने की ज़रूरत नहीं।

```
project/
├── cart.go
└── cart_test.go        # नाम _test.go पर ख़त्म होना चाहिए
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
go test ./...                   # सभी packages
go test -run TestDiscount       # मेल खाते चलाएँ
go test -v                      # विस्तृत output
go test -race ./...             # data races पकड़ें
```

**Table-driven** — यह Go की मुहावरेदार शैली है और इसे डिफ़ॉल्ट रूप से इस्तेमाल करना चाहिए:

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

**किसी error की अपेक्षा:**

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
./gradlew test --continuous      # Gradle के साथ watch mode
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

## Rust — पहले से मौजूद

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

## आपकी भाषा कोई भी हो

शुरू करने से पहले तीन चीज़ें चाहिए:

1. **एक runner जिसे एक ही command से चलाया जा सके** — IDE में क्लिक नहीं, ताकि CI भी उसे चला सके
2. **Watch mode** — save पर दोबारा चले
3. **एक तेज़ हिस्सा** — सिर्फ़ उन टेस्टों को चलाने का कोई तरीक़ा जिन पर आप काम कर रहे हैं (`-k`, `-t`, `-run`, `--filter`)

बाक़ी सब ब्योरा है।

---

वापस [README](README.md) · [चीट शीट](06-cheat-sheet.md)
