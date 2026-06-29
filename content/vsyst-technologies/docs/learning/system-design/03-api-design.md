# Session 3 — API Design, Validation & Versioning

> Phase 2: API & Security (1 of 2)
> Estimated time: 2 hours
> Prerequisites: Sessions 1–2 (request lifecycle, database performance)

---

## Hour 1 — Concepts (60 min)

### Step 1 — REST API Design Principles (20 min)

**Goal:** Understand what a well-designed REST API looks like, then compare against DZZLO-OMS.

**Read these (skim — focus on the sections called out below):**

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines) — read the sections on URL structure, HTTP methods, error responses, and versioning
- [System Design Primer: REST](https://github.com/donnemartin/system-design-primer#representational-state-transfer-rest) — concise summary of REST constraints
- [Stripe API docs](https://docs.stripe.com/api) — open any resource (e.g., Customers, Charges) and study:
  - How resources are named (plural nouns, no verbs in paths)
  - How errors are structured (type, code, message, param)
  - How list endpoints handle pagination (cursor-based)
  - How they version (`/v1/` prefix, backward-compatible changes)

**Core principles to internalise:**


| Principle                   | Good                                 | DZZLO-OMS Today                                  |
| --------------------------- | ------------------------------------ | ------------------------------------------------ |
| Resources are nouns         | `GET /orders`                        | `GET /order_msts` (collection name leaked)       |
| Actions via HTTP verbs      | `DELETE /orders/:id`                 | `PUT /order_msts/deletestatus/:id` (verb in URL) |
| Consistent naming           | `/customers`, `/invoices`            | `/cust_msts`, `/invs`, `/voc_msts`               |
| Sub-resources for relations | `GET /orders/:id/items`              | `/order_msts/a/poso` (cryptic)                   |
| Standard error shape        | `{ error: { type, message, code } }` | `{ success: false, error: "string" }`            |
| Pagination                  | cursor or offset+limit               | `advancedResults` helper (offset-based)          |


**Key insight for DZZLO-OMS:** The MongoDB collection names (`order_msts`, `voc_msts`, `cust_msts`) are implementation details. They leaked into the URL because routes were auto-generated from model names. This is not a crisis — your mobile app is your only client and the mapping is 1:1 — but it means v3 has a chance to fix naming if you want cleaner URLs. The bigger problem is verbs in URLs (`/deletestatus/:id`, `/checkprocess/:id`), which break REST conventions and make the API harder to reason about.

**Self-check:** Open `api_v2/routes/collections/order_msts.js`. Count how many routes use a verb in the URL path (e.g., `/process/:id`, `/deletestatus/:id`, `/fulltank/:id`). What would the RESTful alternative be?

---

### Step 2 — OWASP API Security Top 10 (2023) (20 min)

**Goal:** Learn the most common API security risks and map them to DZZLO-OMS.

**Read:** [OWASP API Security Top 10 — 2023 Edition](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)

Focus on these three (the rest are covered in Session 4):

#### API1:2023 — Broken Object Level Authorization (BOLA)

The most common API vulnerability. Happens when an API exposes object IDs and does not check whether the requesting user owns that object.

**DZZLO-OMS exposure:**

- `PUT /order_msts/:id` — does the controller verify that the order belongs to the requesting user's company (`co_id`)?
- `GET /voc_msts/:id` — `GetOneVoucher` takes an `_id` param. If a user from Company A sends Company B's voucher ID, what happens?
- The `co_id` header is sent by the client. Is it verified server-side against the JWT, or is it trusted as-is?

**Exercise:** Trace the `UpdateOrder` controller in `api_v2/controllers/collections/order_msts.js`. Does it check `co_id` ownership before updating? If not, that is a BOLA vulnerability.

#### API4:2023 — Unrestricted Resource Consumption

No rate limiting, no request size limits, no pagination caps = a single client can exhaust your server.

**DZZLO-OMS exposure:**

- No rate limiter is configured (no `express-rate-limit` in `package.json`)
- The `advancedResults` helper paginates, but is there a maximum page size enforced?
- `POST /order_msts` — can a single request contain 10,000 products in the `products` array? What happens to memory?
- `POST /voc_msts/a/email` — can an attacker trigger unlimited email sends?

#### API8:2023 — Security Misconfiguration

Default configs, unnecessary HTTP methods enabled, verbose error messages in production, missing security headers.

**DZZLO-OMS exposure:**

- Is `helmet` configured? (Check `dzzlo_oms.js` or `helpers/middlewares.js`)
- Are stack traces returned in error responses in production?
- CORS — is it set to `*` or restricted to your app domain?
- [Express security best practices](https://expressjs.com/en/advanced/best-practice-security.html) — compare against your setup

**Self-check:** Pick any one of the three OWASP risks above. Write down one concrete change you would make to DZZLO-OMS to mitigate it. You will revisit this in the 15-min review.

---

### Step 3 — Input Validation with express-validator (20 min)

**Goal:** Learn how express-validator works. It is already in your `package.json` but not used anywhere in `api_v2`.

**Read:**

- [express-validator: Getting Started](https://express-validator.github.io/docs/guides/getting-started/) — follow the whole guide, it is short
- [express-validator docs](https://express-validator.github.io/docs/) — skim the API reference for `body()`, `param()`, `query()`, `validationResult()`

**Key concepts:**

```
Request → [validator chain] → [validation middleware] → Controller
                                      ↓
                              400 { success: false, error: "..." }
```

1. **Validator chain** — declares rules: `body("email").isEmail()`, `body("quantity").isInt({ min: 1 })`
2. **Validation middleware** — collects errors from the chain, returns 400 if any exist
3. **Sanitisation** — `trim()`, `escape()`, `toInt()` transform values after validation

**The pattern you already planned for v3** (from your journal entry `2026-02-20_input-validation-plan-api-v3.md`):

```js
// api_v3/middleware/validate.js — shared error collector
const { validationResult } = require("express-validator");
const ErrorResponse = require("../../helpers/ErrorResponse");

const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const msg = errors.array().map((e) => e.msg).join(", ");
    return next(new ErrorResponse(msg, 400));
  }
  next();
};

module.exports = validate;
```

```js
// Route file — validators defined inline per route
const { body, param } = require("express-validator");
const validate = require("../../middleware/validate");

const createOrderValidators = [
  body("cust_id").isMongoId().withMessage("cust_id must be a valid ID"),
  body("dealer_id").isMongoId().withMessage("dealer_id must be a valid ID"),
  body("products").isArray({ min: 1 }).withMessage("At least one product required"),
  validate,  // ← last in the array
];

router.post("/", createOrderValidators, CreateMstTrn);
```

**Why this matters now:** In `api_v2`, the `CreateMstTrn` controller destructures `req.body` on line 1 (`const { cust_id, dealer_id, cs_reimb_amt } = req.body`) with zero type checking. If `cust_id` is `undefined`, the Mongoose query `DealerCustomer.findOne({ cust_id })` silently matches nothing and the error propagates as a confusing business-logic failure rather than a clear "cust_id is required" 400 response.

**Self-check:** What is the difference between `body("qty").isInt()` and `body("qty").isInt({ min: 1 })`? Why does `min: 1` matter for an order quantity?

---

## Hour 2 — Applied to DZZLO-OMS (60 min)

### Step 4 — Audit 3 Endpoints for Missing Validation (20 min)

Open these three controllers in `api_v2/controllers/collections/` and document every field that is destructured from `req.body` without any type or format check before being used. Mark each field with its risk level.

#### Endpoint 1: Create Order (`POST /order_msts`)

**File:** `api_v2/controllers/collections/order_msts.js` — `exports.CreateMstTrn`

Fields from `req.body`:


| Field             | Used As                          | Validated?                         | Risk   |
| ----------------- | -------------------------------- | ---------------------------------- | ------ |
| `cust_id`         | MongoDB `.findById()`            | No — invalid ID crashes Mongoose   | HIGH   |
| `dealer_id`       | MongoDB `.findById()`            | No                                 | HIGH   |
| `cs_reimb_amt`    | Number in calculation            | No — `"abc"` produces `NaN`        | MEDIUM |
| `products`        | Array, iterated with map/forEach | No — non-array crashes             | HIGH   |
| `products[].qty`  | Number in calculation            | No — negative qty? Zero qty?       | HIGH   |
| `products[].rate` | Number in calculation            | No — string `"abc"` produces `NaN` | HIGH   |
| `products[].p_id` | MongoDB lookup                   | No                                 | MEDIUM |


Also: `req.headers.meta` is `JSON.parse()`-d without a try/catch — malformed JSON crashes the request.

#### Endpoint 2: Create User (`POST /users`)

**File:** `api_v2/controllers/collections/users.js` — `exports.CreateOne`

Fields from `req.body`:


| Field             | Used As                           | Validated?                                               | Risk        |
| ----------------- | --------------------------------- | -------------------------------------------------------- | ----------- |
| `co_id`           | Company reference                 | No — not checked against JWT                             | HIGH (BOLA) |
| `scope`           | String, used in permission logic  | No — arbitrary scope injection?                          | HIGH        |
| `role`            | `"customer"` or `"dealer"` branch | No — what if `role: "admin"`?                            | HIGH        |
| `email`           | Duplicate check, then stored      | Partial — existence check, but no format validation      | MEDIUM      |
| `phone`           | Duplicate check, then stored      | Partial — existence check, no format validation          | MEDIUM      |
| `isEmailVerified` | Boolean flag                      | No — client can send `true` to bypass email verification | HIGH        |
| `isPhoneVerified` | Boolean flag                      | No — same issue                                          | HIGH        |
| `companies`       | Array                             | No — length check only (`companies.length == 0`)         | MEDIUM      |


Critical finding: `isEmailVerified` and `isPhoneVerified` are accepted from the client request body. A malicious user could send `{ isEmailVerified: true }` and skip verification entirely.

#### Endpoint 3: Create Customer Voucher (`POST /voc_msts`)

**File:** `api_v2/controllers/collections/voc_msts.js` — `exports.CreateCustomerVoucher`

Fields from `req.body`:


| Field       | Used As                       | Validated?                                                              | Risk   |
| ----------- | ----------------------------- | ----------------------------------------------------------------------- | ------ |
| `dealer_id` | MongoDB lookup                | No — invalid ID                                                         | HIGH   |
| `amount`    | Number, financial calculation | Partial — checks `!Number(req.body.amount)`, but `amount: -5000` passes | HIGH   |
| `inv_id`    | MongoDB lookup                | No — invalid ObjectId crashes                                           | MEDIUM |
| `invs_adj`  | Array of `{ inv_id, amount }` | No — not validated as array, items not validated                        | HIGH   |
| `notify`    | Boolean-ish flag              | No                                                                      | LOW    |


Critical finding: `amount` can be negative. The check `!Number(req.body.amount)` only catches `NaN` and `0` — it passes `-5000`, which would create a negative payment. Financial endpoints need `{ min: 0.01 }` or similar.

**Your task:** Pick one of these three endpoints and actually read through the full controller function. Confirm or correct the findings above. Add any fields you find that are missing from the table.

---

### Step 5 — Write Validation Middleware for Create Order (20 min)

Using the pattern from Step 3, write a complete validation chain for `POST /order_msts`. This is a hands-on exercise — write the code yourself before looking at the reference below.

**Requirements:**

1. `cust_id` — required, valid MongoDB ObjectId
2. `dealer_id` — required, valid MongoDB ObjectId
3. `products` — required, non-empty array
4. `products.*.p_id` — required for each product, valid ObjectId
5. `products.*.qty` — required, integer, minimum 0 (0 is valid for full-tank orders)
6. `products.*.rate` — required, numeric, minimum 0
7. `cs_reimb_amt` — optional, numeric, minimum 0

**Reference implementation** (check your work against this):

```js
// api_v3/routes/collections/order_msts.js
const { body } = require("express-validator");
const validate = require("../../middleware/validate");

const createOrderValidators = [
  body("cust_id")
    .notEmpty().withMessage("cust_id is required")
    .isMongoId().withMessage("cust_id must be a valid ObjectId"),

  body("dealer_id")
    .notEmpty().withMessage("dealer_id is required")
    .isMongoId().withMessage("dealer_id must be a valid ObjectId"),

  body("products")
    .isArray({ min: 1 }).withMessage("products must be a non-empty array"),

  body("products.*.p_id")
    .notEmpty().withMessage("Each product must have a p_id")
    .isMongoId().withMessage("p_id must be a valid ObjectId"),

  body("products.*.qty")
    .notEmpty().withMessage("Each product must have qty")
    .isInt({ min: 0 }).withMessage("qty must be a non-negative integer"),

  body("products.*.rate")
    .notEmpty().withMessage("Each product must have a rate")
    .isFloat({ min: 0 }).withMessage("rate must be a non-negative number"),

  body("cs_reimb_amt")
    .optional()
    .isFloat({ min: 0 }).withMessage("cs_reimb_amt must be a non-negative number"),

  validate,
];

router.post("/", createOrderValidators, CreateMstTrn);
```

**Key decisions explained:**

- `isMongoId()` prevents invalid ObjectIds from reaching Mongoose — Mongoose would throw a CastError, which is caught by the global error handler but returns a confusing 500 instead of a clear 400.
- `products.*.qty` uses `isInt({ min: 0 })` not `min: 1` because DZZLO-OMS has "full tank" orders where `qty` is 0 and the actual quantity is determined at delivery.
- `products.*.rate` uses `isFloat()` not `isInt()` because rates can have decimal values (e.g., 86.50 per litre).
- `cs_reimb_amt` is `optional()` because not all orders involve reimbursement.
- `validate` is the last element in the array — it runs after all chains and collects errors into one response.

**Think about:** What happens if someone sends `products: []` (empty array)? The `isArray({ min: 1 })` check catches it. What about `products: "not an array"`? Also caught. What about `products: null`? Also caught — `isArray()` rejects non-arrays.

---

### Step 6 — API Versioning: The v3 Decision (20 min)

DZZLO-OMS currently has three versions:

- **v1** — dead, but still mounted. Some v2 routes import from v1 (`contact_us`, `pay_trns`, `payment`)
- **v2** — production. Mobile app uses this
- **v3** — fully scaffolded, service layer refactored, not yet used by clients

**Read:** The v3 refactor plan at `docs/strategy/api_v3_refactor_plan.md` (you wrote this — re-read with fresh eyes).

**Key versioning questions to answer:**

**1. What does v3 give you that v2 does not?**


| Improvement      | v2                                                    | v3                                             |
| ---------------- | ----------------------------------------------------- | ---------------------------------------------- |
| Service layer    | Business logic in controllers                         | Extracted to `api_v3/services/`                |
| Input validation | None                                                  | Planned (express-validator middleware)         |
| Error handling   | Inconsistent (`next(new ErrRes(...))` mixed patterns) | Standardised `throw ErrorResponse` in services |
| Dead code        | Comments, unused routes                               | Planned cleanup (deferred)                     |


**2. Migration strategy — how do clients move from v2 to v3?**

Options (pick one and justify):

- **A. Hard cutover** — deprecate v2, force all clients to v3 at once
  - Risk: if v3 has a bug, all users are affected. You have one mobile app — a bad release means emergency hotfix
- **B. Parallel run, gradual migration** — both v2 and v3 are live. New features go to v3 only. Existing clients migrate endpoint by endpoint
  - This is what you are doing. Lower risk. But you must maintain two codebases indefinitely
- **C. URL versioning with feature flags** — v3 endpoints are identical to v2 but with validation middleware added. Mobile app switches per-endpoint based on `meta.version`
  - Pragmatic for a solo developer. No separate codebase — v3 routes call v3 controllers which are already wrappers around services

**3. What about v1?**

v1 is dead but still mounted. Three v2 routes import from v1:

```
api_v1/routes/collections/contact_us.js
api_v1/routes/collections/pay_trns.js
api_v1/routes/collections/payment.js
```

Decision: these should be copied into v2 (or v3) so v1 can be fully unmounted. This eliminates confusion about which version is "real."

**Your task:** Write down your decision in 2-3 sentences. Which migration strategy (A, B, or C) are you following? What is the trigger for turning off v2?

---

## 15-Minute Review — Tied to DZZLO-OMS Decisions

Answer these questions in writing (in `docs/strategy/system-design.md` or a scratch file). The goal is to commit to concrete decisions, not just absorb concepts.

### Question 1 — Validation Priority

You audited three endpoints in Step 4. Rank them by risk if left unvalidated:

1. _________________________ (highest risk — why?)
2. _________________________
3. _________________________ (lowest risk — why?)

### Question 2 — First Validation Win

The `validate.js` middleware from your February journal entry is already designed. What is stopping you from adding it to `api_v3/` today?

Write the concrete next step (file path, function name, what it validates).

### Question 3 — OWASP Action Item

From Step 2, you identified at least one concrete OWASP risk in DZZLO-OMS. Write it as a one-line action item:

> "Add __________ to mitigate OWASP API__:2023 (_______________)"

Example: "Add `co_id` ownership check in `UpdateOrder` to mitigate OWASP API1:2023 (Broken Object Level Authorization)"

### Question 4 — Versioning Commitment

What is your v3 migration strategy? When does v2 get turned off?

> Strategy: ___
> v2 sunset trigger: ___

---

## Resources Used in This Session


| Resource                                                                                                               | Section                                   |
| ---------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)                                           | URL structure, error responses            |
| [Stripe API](https://docs.stripe.com/api)                                                                              | Resource naming, error format, pagination |
| [OWASP API Security Top 10 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)                            | API1, API4, API8                          |
| [express-validator: Getting Started](https://express-validator.github.io/docs/guides/getting-started/)                 | Full guide                                |
| [express-validator docs](https://express-validator.github.io/docs/)                                                    | API reference                             |
| [System Design Primer: REST](https://github.com/donnemartin/system-design-primer#representational-state-transfer-rest) | REST constraints                          |
| [Express security best practices](https://expressjs.com/en/advanced/best-practice-security.html)                       | Helmet, CORS, error handling              |


**DZZLO-OMS files referenced:**

- `api_v2/routes/collections/order_msts.js` — route definitions
- `api_v2/routes/collections/users.js` — route definitions
- `api_v2/routes/collections/voc_msts.js` — route definitions
- `api_v2/controllers/collections/order_msts.js` — `CreateMstTrn` (create order)
- `api_v2/controllers/collections/users.js` — `CreateOne` (create user)
- `api_v2/controllers/collections/voc_msts.js` — `CreateCustomerVoucher` (create voucher)
- `helpers/middlewares.js` — API key check, `meta` header parsing
- `docs/strategy/api_v3_refactor_plan.md` — v3 migration status
- `docs/journal/2026-02-20_input-validation-plan-api-v3.md` — validation middleware design

---

**Next session:** [04-auth-security.md](./04-auth-security.md) — JWT hardening, rate limiting, AWS WAF, SSH/MongoDB access control