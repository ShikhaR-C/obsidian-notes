# 4. एक पूरा उदाहरण

आइए एक शॉपिंग कार्ट बनाएँ — एक बार में एक फेल होता टेस्ट। ध्यान दीजिए कि डिज़ाइन पहले से तय होने के बजाय ख़ुद उभरता है।

उदाहरण Python + pytest में हैं, पर लय हर भाषा में एक जैसी है।

---

## फेरा 1 — ख़ाली कार्ट

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

सही कारण से फेल हो रहा है। बढ़िया।

### 🟢 Green

सबसे बुद्धू चीज़ जो काम कर जाए:

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

अभी साफ़ करने को कुछ नहीं है। आगे बढ़िए।

---

## फेरा 2 — एक चीज़

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

ग़ौर कीजिए: **टेस्ट ने अभी-अभी API डिज़ाइन कर दी।** हमने `add(name, price)` इसलिए तय किया क्योंकि हमने लिखा कि हम इसे कैसे बुलाना चाहते हैं — implementation फ़ाइल में अंदाज़ा लगाकर नहीं।

### 🟢 Green

Hardcoded `0` अब टिक नहीं सकता। असली logic बाहर आने पर मजबूर हो जाता है:

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

दोनों टेस्ट हरे — पहला भी टिका हुआ है, क्योंकि ख़ाली list का योग 0 होता है।

---

## फेरा 3 — मात्रा (quantity)

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

`1` की default value पुराने टेस्टों को पास रखती है। यही सुरक्षा जाल का काम है — हमने signature बदला और तुरंत जान गए कि कुछ नहीं टूटा।

---

## फेरा 4 — ग़लत input ठुकराना

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

## फेरा 5 — छूट का नियम

_"£100 से ऊपर के ऑर्डर पर 10% छूट।"_

### 🔴 Red

सीमा (boundary) से शुरू कीजिए, क्योंकि बग सीमाओं पर ही रहते हैं:

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

पहला पहले से ही पास है; दूसरा फेल होता है। दोनों रखने लायक़ हैं — पास होने वाला सीमा को कील ठोंककर पकड़ लेता है ताकि बाद में कोई इसे `>=` में "ठीक" न कर दे।

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

अब `total()` दो काम कर रहा है, और एक जादुई संख्या भी है। सफ़ाई कीजिए — **हरे पर**, टेस्टों की निगरानी में:

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

व्यवहार वही, आकार बेहतर। हमें पता है कि व्यवहार वही है क्योंकि टेस्टों ने बताया — इसलिए नहीं कि हमने आँखें सिकोड़कर कोड देखा।

---

## अभी-अभी क्या हुआ

पीछे मुड़कर देखिए कि हमने क्या-क्या _नहीं_ किया:

- हमने `Cart` class पहले से डिज़ाइन नहीं की। **हर टेस्ट ने डिज़ाइन का अगला टुकड़ा बाहर खींचा।**
- हमने ऐसा कोड नहीं लिखा जिसकी ज़रूरत न थी। कोई `remove()` नहीं, कोई `Item` class नहीं, currency संभालना नहीं — क्योंकि किसी ने माँगा ही नहीं।
- हमने debug नहीं किया। जब कुछ लाल हुआ, वजह वही दस लाइनें थीं जो हमने अभी लिखी थीं।
- हमने दो बार पूरे आत्मविश्वास के साथ refactor किया।

और अंत में हमारे पास पाँच टेस्ट हैं जो नियमों को सीधी भाषा में दर्ज करते हैं:

```
test_empty_cart_total_is_zero
test_cart_with_one_item_totals_that_item
test_quantity_multiplies_the_price
test_negative_quantity_is_rejected
test_no_discount_at_exactly_100
test_ten_percent_off_over_100
```

यह सूची _ही_ spec है।

---

आगे: [गलतियाँ और FAQ →](05-pitfalls-and-faq.md)
