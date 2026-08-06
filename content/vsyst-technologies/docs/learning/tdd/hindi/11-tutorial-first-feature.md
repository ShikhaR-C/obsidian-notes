# 11. ट्यूटोरियल — आपका पहला TDD फ़ीचर

एक व्यावहारिक, साथ-साथ करने वाला ट्यूटोरियल। आप लगभग 45–60 मिनट में शून्य से **user signup फ़ीचर** बनाएँगे, test-first।

अंत तक आप चक्र, triangulation, हरे पर refactoring, सीमा पर test doubles, और outside-in डिज़ाइन का अभ्यास कर चुके होंगे — यानी वे चीज़ें जिन्हें बाक़ी दस्तावेज़ सिर्फ़ समझाते हैं।

**भाषा:** Python + pytest। ढाँचा किसी भी भाषा पर सीधे लागू होता है — runner बदलने के लिए देखिए [9. भाषा के अनुसार सेटअप](09-language-setup.md)।

**पूरे ट्यूटोरियल का नियम:** आगे मत कूदिए और अंतिम कोड paste मत कीजिए। सीख _क्रम_ में है।

---

## चरण 0 — सेटअप

**लक्ष्य:** एक test runner जो सही कारण से फेल हो।

### Step 1 — प्रोजेक्ट बनाइए

```bash
mkdir tdd-signup && cd tdd-signup
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pytest pytest-watch
```

### Step 2 — दो फ़ाइलें बनाइए

```
tdd-signup/
├── password.py          # फ़िलहाल ख़ाली
└── test_password.py     # फ़िलहाल ख़ाली
```

### Step 3 — दूसरे terminal में watch mode शुरू कीजिए

```bash
ptw
```

इसे चलता छोड़ दीजिए। स्क्रीन बाँट लीजिए — एक तरफ़ कोड, दूसरी तरफ़ टेस्ट का output। **यह चक्र तभी सुखद है जब feedback तुरंत मिले।**

### Step 4 — साबित कीजिए कि runner चल रहा है

```bash
pytest
```

आपको `no tests ran` दिखना चाहिए। अगर इसकी जगह कोई error दिखे, तो उसे अभी ठीक कीजिए — चक्र के बीच में अपना setup debug करना बहुत कष्टदायक है।

> ✅ **चेकपॉइंट:** pytest चलता है और शून्य टेस्ट बताता है।

---

## चरण 1 — आपका पहला चक्र

**लक्ष्य:** सबसे आसान नियम पर एक बार red → green → refactor महसूस करना।

नियम: _पासवर्ड कम से कम 8 अक्षरों का होना चाहिए।_

### Step 1 — 🔴 फेल होता टेस्ट लिखिए

```python
# test_password.py
import pytest
from password import validate_password

def test_short_password_is_rejected():
    with pytest.raises(ValueError):
        validate_password("abc")
```

### Step 2 — चलाइए और फ़ेल्योर पढ़िए

```
ModuleNotFoundError: No module named 'password'
```

**इसे मत छोड़िए।** जिस टेस्ट को आपने कभी फेल होते देखा ही नहीं, उस पर भरोसा नहीं किया जा सकता। जाँचिए कि संदेश ऐसा है जो शुक्रवार शाम चार बजे आपको कुछ काम की बात बताए।

### Step 3 — 🟢 सबसे बुद्धू तरीक़े से पास कराइए

```python
# password.py
def validate_password(password):
    raise ValueError("too short")
```

```
1 passed ✅
```

हाँ, यह _हर_ पासवर्ड को ठुकरा देता है। हाँ, यह "ग़लत" है। पर आपकी test suite फ़िलहाल ठीक इतनी ही माँग कर रही है, और यही बात है — आपको ऐसा कोड लिखने की छूट नहीं जो किसी टेस्ट ने माँगा ही न हो।

### Step 4 — 🔵 Refactor

साफ़ करने को कुछ नहीं। आगे बढ़िए।

> ✅ **चेकपॉइंट:** एक हरा टेस्ट। आपने एक पूरा फेरा कर लिया।

---

## चरण 2 — Triangulation

**लक्ष्य:** देखिए कि दूसरा उदाहरण नक़ली implementation को कैसे बाहर कर देता है।

### Step 1 — 🔴 उल्टा मामला जोड़िए

```python
def test_long_enough_password_is_accepted():
    validate_password("abcdefgh")      # यह raise नहीं होना चाहिए
```

```
ValueError: too short
```

Hardcoded raise दो उदाहरणों के सामने टिक नहीं सकता। **यही triangulation है** — एक उदाहरण से आप नक़ल कर सकते हैं, दो असली logic को बाहर निकाल देते हैं।

### Step 2 — 🟢 असली नियम लिखिए

```python
MIN_LENGTH = 8

def validate_password(password):
    if len(password) < MIN_LENGTH:
        raise ValueError(f"password must be at least {MIN_LENGTH} characters")
```

```
2 passed ✅
```

### Step 3 — 🔴 सीमा को कील ठोंकिए

बग सीमाओं पर रहते हैं। इसे बाँध दीजिए ताकि बाद में कोई `<` को `<=` में "ठीक" न कर दे:

```python
def test_exactly_eight_characters_is_accepted():
    validate_password("abcdefgh")

def test_seven_characters_is_rejected():
    with pytest.raises(ValueError):
        validate_password("abcdefg")
```

पहला पहले से पास है — फिर भी रखिए। उसका काम है कि अगर कोई नियम बदले तो वह फेल हो जाए।

> ✅ **चेकपॉइंट:** 4 हरे टेस्ट, और नक़ल की जगह असली implementation।

---

## चरण 3 — नियम बढ़ाना

**लक्ष्य:** चक्र अपने दम पर दोहराइए, और अपने पहले refactor से मिलिए।

### Step 1 — 🔴🟢 एक अंक (digit) अनिवार्य कीजिए

Red:

```python
def test_password_without_digit_is_rejected():
    with pytest.raises(ValueError):
        validate_password("abcdefghij")
```

Green:

```python
    if not any(c.isdigit() for c in password):
        raise ValueError("password must contain a digit")
```

### Step 2 — 🔴🟢 एक बड़ा अक्षर (uppercase) अनिवार्य कीजिए

आगे पढ़ने से पहले यह ख़ुद कीजिए। पहले Red।

<details>
<summary>हल</summary>

```python
def test_password_without_uppercase_is_rejected():
    with pytest.raises(ValueError):
        validate_password("abcdefgh1")
```

```python
    if not any(c.isupper() for c in password):
        raise ValueError("password must contain an uppercase letter")
```

</details>

### Step 3 — दोहराव पर ध्यान दीजिए

आपके टेस्ट अब चार बार ऐसे दिखते हैं:

```python
def test_x_is_rejected():
    with pytest.raises(ValueError):
        validate_password("...")
```

**टेस्ट कोड भी असली कोड है।** इसे refactor कीजिए — हरे पर:

```python
import pytest
from password import validate_password

@pytest.mark.parametrize("password,reason", [
    ("abcdefg",     "too short"),
    ("abcdefghij",  "no digit"),
    ("abcdefgh1",   "no uppercase"),
])
def test_invalid_passwords_are_rejected(password, reason):
    with pytest.raises(ValueError):
        validate_password(password)

def test_valid_password_is_accepted():
    validate_password("Abcdefg1")
```

Suite चलाइए। अब भी हरी — आपने टेस्टों का _आकार_ बदला, यह नहीं कि वे क्या जाँचते हैं।

### Step 4 — Production code refactor कीजिए

```python
MIN_LENGTH = 8

class PasswordError(ValueError):
    """Raised when a password fails the strength rules."""

def validate_password(password):
    if len(password) < MIN_LENGTH:
        raise PasswordError(f"password must be at least {MIN_LENGTH} characters")
    if not any(c.isdigit() for c in password):
        raise PasswordError("password must contain a digit")
    if not any(c.isupper() for c in password):
        raise PasswordError("password must contain an uppercase letter")
```

`PasswordError`, `ValueError` का subclass है, इसलिए हर मौजूदा टेस्ट बिना छेड़े पास होता रहता है। यह जान-बूझकर लिया गया फ़ैसला है — आपने डिज़ाइन सुधारा बिना पूरी suite को घसीटे।

> ✅ **चेकपॉइंट:** हरी suite, सुथरे टेस्ट, सुथरा कोड। अब नियम #4 जोड़ने में 60 सेकंड लगेंगे।

---

## चरण 4 — एक सहयोगी (collaborator), और test doubles

**लक्ष्य:** ऐसे कोड को टेस्ट करना जो दूसरी चीज़ों पर निर्भर है, बिना हर दिखने वाली चीज़ को mock किए।

अब असली फ़ीचर: **user रजिस्टर करना** — पासवर्ड जाँचिए, उसे स्टोर कीजिए, स्वागत ईमेल भेजिए।

### Step 1 — 🔴 वह टेस्ट लिखिए जो आप लिखना _चाहते_ हैं

`test_signup.py` बनाइए। ध्यान दीजिए कि आप API को बुलाकर ही डिज़ाइन कर रहे हैं:

```python
# test_signup.py
from signup import SignupService

def test_registering_stores_the_user():
    users = FakeUserStore()
    service = SignupService(users, FakeMailer())

    service.register("ada@example.com", "Abcdefg1")

    assert users.exists("ada@example.com")
```

Constructor का signature `SignupService(users, mailer)` अभी-अभी _टेस्ट ने_ तय किया। Dependencies बाहर से आती हैं — इसी वजह से यह टेस्ट करने लायक़ है।

### Step 2 — Test doubles बनाइए

जान-बूझकर दो अलग क़िस्में:

```python
# test_signup.py (फ़ाइल के ऊपर)
class FakeUserStore:
    """A real working implementation — just in memory."""
    def __init__(self):
        self._users = {}

    def exists(self, email):
        return email in self._users

    def add(self, email, password):
        self._users[email] = password


class FakeMailer:
    """A spy — records what it was asked to do."""
    def __init__(self):
        self.sent_to = []

    def send_welcome(self, email):
        self.sent_to.append(email)
```

> 🔑 **नियम:** जो चीज़ें आपकी हैं (store, repository) उनके लिए **fake** इस्तेमाल कीजिए, और **spy या mock** सिर्फ़ उन असली सीमाओं पर जो आपकी नहीं हैं (ईमेल, network, payments, घड़ी)।
>
> सब कुछ mock कर दीजिए और आपके टेस्ट बस यह जाँचेंगे कि आपका कोड उन्हीं functions को बुलाता है जिन्हें बुलाने के लिए लिखा गया था — असली व्यवहार कितना भी टूटा हो, वे पास होते रहेंगे।

### Step 3 — 🟢 पास कराइए

```python
# signup.py
from password import validate_password

class SignupService:
    def __init__(self, users, mailer):
        self._users = users
        self._mailer = mailer

    def register(self, email, password):
        validate_password(password)
        self._users.add(email, password)
```

```
green ✅
```

ध्यान दीजिए कि अभी ईमेल वाला कोड है ही नहीं — किसी टेस्ट ने माँगा नहीं।

### Step 4 — 🔴🟢 अब ईमेल की माँग कीजिए

```python
def test_registering_sends_a_welcome_email():
    users, mailer = FakeUserStore(), FakeMailer()
    SignupService(users, mailer).register("ada@example.com", "Abcdefg1")

    assert mailer.sent_to == ["ada@example.com"]
```

```python
        self._mailer.send_welcome(email)
```

### Step 5 — 🔴🟢 डुप्लिकेट ठुकराइए

```python
import pytest
from signup import SignupService, DuplicateEmail

def test_duplicate_email_is_rejected():
    users = FakeUserStore()
    service = SignupService(users, FakeMailer())
    service.register("ada@example.com", "Abcdefg1")

    with pytest.raises(DuplicateEmail):
        service.register("ada@example.com", "Zyxwvu9A")
```

```python
class DuplicateEmail(Exception):
    pass
```

```python
    def register(self, email, password):
        validate_password(password)
        if self._users.exists(email):
            raise DuplicateEmail(email)
        self._users.add(email, password)
        self._mailer.send_welcome(email)
```

### Step 6 — 🔴 वह टेस्ट जो लोग भूल जाते हैं

_असफल_ signup पर क्या होता है? अनुपस्थिति पर assert कीजिए:

```python
def test_weak_password_sends_no_email(...):
    users, mailer = FakeUserStore(), FakeMailer()
    with pytest.raises(PasswordError):
        SignupService(users, mailer).register("ada@example.com", "abc")

    assert mailer.sent_to == []
    assert not users.exists("ada@example.com")
```

यह पहले से पास होना चाहिए, क्योंकि validation पहले चलता है। **फिर भी इसे रखिए** — अब कोई उन लाइनों का क्रम बदले तो suite को पता चले बिना यह मुमकिन नहीं।

> ✅ **चेकपॉइंट:** सहयोगियों वाला असली फ़ीचर, milliseconds में टेस्ट होता है, न कोई database न कोई SMTP server।

---

## चरण 5 — Outside-in

**लक्ष्य:** एक फेल होते acceptance test को "पूरा हुआ" की परिभाषा बनाइए।

अब तक आपने नीचे-से-ऊपर काम किया। असली tickets आमतौर पर उल्टी दिशा में चलते हैं।

### Step 1 — पहले acceptance test लिखिए

अगली requirement — _"नया user रजिस्टर करते ही सीधे लॉग इन कर सके"_ — के लिए सबसे बाहरी दिखने वाले व्यवहार से शुरू कीजिए:

```python
def test_new_user_can_log_in_immediately():
    app = build_app()                                  # अभी मौजूद नहीं है
    app.register("ada@example.com", "Abcdefg1")

    assert app.login("ada@example.com", "Abcdefg1") is True
```

### Step 2 — इसे लाल रहने दीजिए

यह एक टेस्ट तब तक लाल रहेगा जब तक काम पूरा नहीं होता। यही अपेक्षित है — **यह आपकी "पूरा हुआ" की परिभाषा है**, कोई फेरा नहीं।

### Step 3 — तेज़ unit चक्रों से भीतर की ओर बढ़िए

एक स्तर नीचे उतरिए। `login`, password hashing, जो भी चाहिए — उसके लिए छोटे red-green-refactor फेरे लिखिए, हर एक सेकंडों का।

### Step 4 — Acceptance test को हरा होते देखिए

जब यह पलटे, ticket पूरा हो गया। हाथ से क्लिक करके जाँचने की ज़रूरत नहीं।

> यह है **double-loop TDD**: एक धीमा बाहरी चक्र जो "पूरा हुआ" तय करता है, और एक तेज़ भीतरी चक्र जो आपको वहाँ पहुँचाता है।

---

## चरण 6 — इसे अपने workflow में बैठाइए

**लक्ष्य:** चक्र को commits और CI में बदलिए।

### Step 1 — हरे पर commit कीजिए, लाल पर कभी नहीं

```bash
git commit -m "test: reject passwords under 8 chars"
git commit -m "feat: password strength rules"
git commit -m "refactor: extract PasswordError"
```

### Step 2 — एक ही commit में refactor और व्यवहार कभी मत मिलाइए

Review करने वाला शुद्ध-refactor वाला diff दस सेकंड में देख सकता है और शुद्ध-व्यवहार वाला diff ध्यान से पढ़ सकता है। दोनों मिले हों तो उसे हर लाइन पढ़नी पड़ेगी — और चीज़ें छूट जाएँगी।

### Step 3 — हर commit हरा रखिए

इसी से `git bisect` काम करता है और revert सुरक्षित रहते हैं।

### Step 4 — CI जोड़िए

```yaml
- run: pytest --tb=short -q
```

दो चीज़ों पर समझौता नहीं: **जल्दी फेल हो** (unit suite धीमे चरणों का द्वार बने) और **अस्थिर टेस्टों पर auto-retry नहीं** — retries ही वह तरीक़ा है जिससे असली फ़ेल्योर चुपचाप निगल लिया जाता है।

### Step 5 — जब अटक जाएँ, reset कीजिए

~15 मिनट से ज़्यादा लाल हैं और बात बिगड़ रही है? पिछले हरे पर `git reset --hard` कीजिए और छोटा निवाला लीजिए। लगता है जैसे काम गया, पर लगभग हमेशा यही तेज़ है।

---

## चरण 7 — आगे कहाँ जाएँ

### Step 1 — असली बग पर दोबारा कीजिए

अगला बग मिले: **पहले** उसे फेल होते टेस्ट के रूप में दोहराइए, फिर ठीक कीजिए। सबसे आसान जीत, और जिससे बहस करना किसी के लिए मुमकिन नहीं।

### Step 2 — चक्र का जान-बूझकर अभ्यास कीजिए

[12. अभ्यास katas](12-tutorial-katas.md) पूरे कीजिए — छोटे अभ्यास जो असली codebase के भटकाव के बिना लय बनाते हैं।

### Step 3 — जो सीखा उसे दोहराइए

| चरण | सीख                                                                           |
| --- | ----------------------------------------------------------------------------- |
| 1   | इसे फेल होते देखिए। जिस टेस्ट को कभी फेल होते नहीं देखा, वह भरोसे लायक़ नहीं। |
| 2   | Triangulation — दो उदाहरण नक़ल को बाहर कर देते हैं।                           |
| 3   | टेस्ट कोड को भी refactor कीजिए, हरे पर।                                       |
| 4   | जो आपका है उसके लिए fakes; असली सीमाओं पर ही mocks।                           |
| 5   | Outside-in: acceptance test ही "पूरा हुआ" की परिभाषा है।                      |
| 6   | हरे पर commit; refactor और व्यवहार कभी मत मिलाइए।                             |

---

आगे: [अभ्यास katas →](12-tutorial-katas.md) · संबंधित: [2. Red, Green, Refactor](02-red-green-refactor.md) · [3. अच्छे टेस्ट लिखना](03-writing-good-tests.md)
