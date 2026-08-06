# 11. Tutorial — your first TDD feature

A hands-on, follow-along tutorial. You'll build a **user signup feature** from nothing, test-first, in about 45–60 minutes.

By the end you'll have practised the loop, triangulation, refactoring on green, test doubles at a boundary, and outside-in design — the things the rest of these docs only describe.

**Language:** Python + pytest. The structure maps directly onto any language — see [9. Language setup](09-language-setup.md) to swap runners.

**Rule for the whole tutorial:** don't skip ahead and don't paste the final code. The _order_ is the lesson.

---

## Phase 0 — Setup

**Goal:** a test runner that fails for the right reason.

### Step 1 — Make the project

```bash
mkdir tdd-signup && cd tdd-signup
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install pytest pytest-watch
```

### Step 2 — Create the two files

```
tdd-signup/
├── password.py          # empty for now
└── test_password.py     # empty for now
```

### Step 3 — Start watch mode in a second terminal

```bash
ptw
```

Leave it running. Split your screen — code on one side, test output on the other. **The loop is only comfortable when feedback is instant.**

### Step 4 — Prove the runner works

```bash
pytest
```

You should see `no tests ran`. If you see an error instead, fix that now — debugging your setup mid-loop is miserable.

> ✅ **Checkpoint:** pytest runs and reports zero tests.

---

## Phase 1 — Your first loop

**Goal:** feel red → green → refactor once, on the simplest possible rule.

The rule: _passwords must be at least 8 characters._

### Step 1 — 🔴 Write the failing test

```python
# test_password.py
import pytest
from password import validate_password

def test_short_password_is_rejected():
    with pytest.raises(ValueError):
        validate_password("abc")
```

### Step 2 — Run it and read the failure

```
ModuleNotFoundError: No module named 'password'
```

**Don't skip this.** A test you've never seen fail is a test you can't trust. Check the message is one that would tell you something useful at 4pm on a Friday.

### Step 3 — 🟢 Make it pass the dumbest way

```python
# password.py
def validate_password(password):
    raise ValueError("too short")
```

```
1 passed ✅
```

Yes, that rejects _every_ password. Yes, it's "wrong". It is also exactly what your test suite currently demands, and that's the point — you don't get to write code no test asked for.

### Step 4 — 🔵 Refactor

Nothing to clean. Move on.

> ✅ **Checkpoint:** one green test. You've done a full lap.

---

## Phase 2 — Triangulation

**Goal:** watch a fake implementation get forced out by a second example.

### Step 1 — 🔴 Add the opposite case

```python
def test_long_enough_password_is_accepted():
    validate_password("abcdefgh")      # should not raise
```

```
ValueError: too short
```

The hardcoded raise can't survive two examples. **This is triangulation** — one example lets you fake it, two force the real logic out.

### Step 2 — 🟢 Write the real rule

```python
MIN_LENGTH = 8

def validate_password(password):
    if len(password) < MIN_LENGTH:
        raise ValueError(f"password must be at least {MIN_LENGTH} characters")
```

```
2 passed ✅
```

### Step 3 — 🔴 Pin the boundary

Bugs live at boundaries. Lock this one down so nobody "fixes" `<` into `<=` later:

```python
def test_exactly_eight_characters_is_accepted():
    validate_password("abcdefgh")

def test_seven_characters_is_rejected():
    with pytest.raises(ValueError):
        validate_password("abcdefg")
```

The first passes already — keep it anyway. Its job is to fail if someone changes the rule.

> ✅ **Checkpoint:** 4 green tests, and a real implementation rather than a fake.

---

## Phase 3 — Growing the rules

**Goal:** repeat the loop under your own steam, and meet your first refactor.

### Step 1 — 🔴🟢 Require a digit

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

### Step 2 — 🔴🟢 Require an uppercase letter

Do this one yourself before reading on. Red first.

<details>
<summary>Solution</summary>

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

### Step 3 — Notice the duplication

Your tests now look like this, four times over:

```python
def test_x_is_rejected():
    with pytest.raises(ValueError):
        validate_password("...")
```

**Test code is real code.** Refactor it — on green:

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

Run the suite. Still green — you changed the tests' _shape_, not what they check.

### Step 4 — Refactor the production code

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

`PasswordError` subclasses `ValueError`, so every existing test still passes untouched. That's a deliberate choice — you improved the design without dragging the suite along with it.

> ✅ **Checkpoint:** green suite, tidy tests, tidy code. Adding rule #4 now takes 60 seconds.

---

## Phase 4 — A collaborator, and test doubles

**Goal:** test code that depends on other things, without mocking everything in sight.

Now the real feature: **registering a user** — validate the password, store them, send a welcome email.

### Step 1 — 🔴 Write the test you _wish_ you could write

Create `test_signup.py`. Notice you're designing the API by calling it:

```python
# test_signup.py
from signup import SignupService

def test_registering_stores_the_user():
    users = FakeUserStore()
    service = SignupService(users, FakeMailer())

    service.register("ada@example.com", "Abcdefg1")

    assert users.exists("ada@example.com")
```

The constructor signature `SignupService(users, mailer)` was just decided _by the test_. Dependencies come in from outside — that's what makes this testable at all.

### Step 2 — Build the test doubles

Two different kinds, on purpose:

```python
# test_signup.py (top of file)
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

> 🔑 **The rule:** use a **fake** for things you own (a store, a repository) and a **spy or mock** only at genuine boundaries you don't own (email, network, payments, the clock).
>
> Mock everything and your tests just assert that your code calls the functions you wrote it to call — they'll pass no matter how broken the real behaviour is.

### Step 3 — 🟢 Make it pass

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

Note there's no email code yet — no test asked for it.

### Step 4 — 🔴🟢 Now demand the email

```python
def test_registering_sends_a_welcome_email():
    users, mailer = FakeUserStore(), FakeMailer()
    SignupService(users, mailer).register("ada@example.com", "Abcdefg1")

    assert mailer.sent_to == ["ada@example.com"]
```

```python
        self._mailer.send_welcome(email)
```

### Step 5 — 🔴🟢 Reject duplicates

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

### Step 6 — 🔴 The test people forget

What happens on a _failed_ signup? Assert the absence:

```python
def test_weak_password_sends_no_email(...):
    users, mailer = FakeUserStore(), FakeMailer()
    with pytest.raises(PasswordError):
        SignupService(users, mailer).register("ada@example.com", "abc")

    assert mailer.sent_to == []
    assert not users.exists("ada@example.com")
```

This should already pass, because validation runs first. **Keep it anyway** — it's now impossible for someone to reorder those lines without the suite noticing.

> ✅ **Checkpoint:** a real feature with collaborators, tested in milliseconds, no database and no SMTP server.

---

## Phase 5 — Outside-in

**Goal:** use a failing acceptance test as your definition of done.

So far you worked bottom-up. Real tickets usually run the other way.

### Step 1 — Write the acceptance test first

For the next requirement — _"a new user can log in straight after registering"_ — start at the outermost observable behaviour:

```python
def test_new_user_can_log_in_immediately():
    app = build_app()                                  # doesn't exist yet
    app.register("ada@example.com", "Abcdefg1")

    assert app.login("ada@example.com", "Abcdefg1") is True
```

### Step 2 — Let it stay red

This one test stays red for as long as the work takes. That's expected — **it's your definition of done**, not a lap.

### Step 3 — Drive inward with fast unit loops

Drop down a level. Write small red-green-refactor laps for `login`, password hashing, whatever's needed — each one seconds long.

### Step 4 — Watch the acceptance test go green

When it flips, the ticket is done. No manual click-through required.

> This is **double-loop TDD**: a slow outer loop that defines done, and a fast inner loop that gets you there.

---

## Phase 6 — Fit it into your workflow

**Goal:** turn the loop into commits and CI.

### Step 1 — Commit on green, never on red

```bash
git commit -m "test: reject passwords under 8 chars"
git commit -m "feat: password strength rules"
git commit -m "refactor: extract PasswordError"
```

### Step 2 — Never mix refactor and behaviour in one commit

A reviewer can skim a pure-refactor diff in ten seconds and read a pure-behaviour diff carefully. Mixed together, they have to read every line — and will miss things.

### Step 3 — Keep every commit green

That's what makes `git bisect` work and reverts safe.

### Step 4 — Wire up CI

```yaml
- run: pytest --tb=short -q
```

Two non-negotiables: **fail fast** (unit suite gates the slower stages) and **no auto-retry on flaky tests** — retries are how a real failure gets silently swallowed.

### Step 5 — When you get stuck, reset

Red for more than ~15 minutes and going badly? `git reset --hard` to the last green and take a smaller bite. It feels like losing work. It's almost always faster.

---

## Phase 7 — Where to go next

### Step 1 — Do it again on a real bug

Next bug you get: reproduce it as a failing test **first**, then fix it. Easiest possible win, and impossible for anyone to argue with.

### Step 2 — Practise the loop deliberately

Work through [12. Practice katas](12-tutorial-katas.md) — short exercises designed to build the rhythm without the distraction of a real codebase.

### Step 3 — Review what you learned

| Phase | The lesson                                                     |
| ----- | -------------------------------------------------------------- |
| 1     | Watch it fail. A test you've never seen fail is untrustworthy. |
| 2     | Triangulation — two examples force out a fake.                 |
| 3     | Refactor test code too, on green.                              |
| 4     | Fakes for what you own; mocks only at real boundaries.         |
| 5     | Outside-in: the acceptance test is your definition of done.    |
| 6     | Commit on green; never mix refactor with behaviour.            |

---

Next: [Practice katas →](12-tutorial-katas.md) · Related: [2. Red, Green, Refactor](02-red-green-refactor.md) · [3. Writing good tests](03-writing-good-tests.md)
