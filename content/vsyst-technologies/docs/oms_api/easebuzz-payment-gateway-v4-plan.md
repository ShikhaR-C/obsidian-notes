# Easebuzz payment gateway in API v4 — safety measures and the open endpoint

> **Status (2026-09-17):** Plan only. No code, model, helper, test or config file was changed to write it. Nothing starts until the decisions in §12 are answered and the user says "start phase N".
> **Scope:** exactly the files present in `EaseBuzz/paywitheasebuzz-nodejs-lib/Easebuzz_NodeJS_kit` — eight gateway calls and the return handler. The kit's README also advertises a Seamless (merchant-hosted card) module, but `initiate_seamless_payment.js` and its view are not in the folder, so it is out of scope. Webhooks have no file in the kit either — see §6.6.
> **Builds on:** [04-payment-flow](../../correspondence/IPG_Easebuzz/onboarding/04-payment-flow.md) (the agreed functional flow) · [02-foundations](../oms_app/screen-redesign/02-foundations.md) (the v4 contract) · [tasks_11 phase 4](../tasks/tasks_11_partner_api/04-phase-4-security-measures.md) (external-surface security) · [tasks_13 overview](../tasks/tasks_13_db_architecture/00-overview.md) Q4 (the reserved `GATEWAY` door) · [DZZLOOMS_backend_AWS](./DZZLOOMS_backend_AWS.md) (hosting).

---

## 1. The answer on one page

Two things were asked: how we keep the integration safe, and which of the payment-gateway APIs have to be open.

**Open APIs: one.** Of everything in the kit, only the return URL (`surl` / `furl`) must be reachable without our API key and Bearer — because it is the payer's browser, sent there by Easebuzz, that posts to it, and that browser holds neither. Every other call in the kit (initiate, transaction, transaction-by-date, refund, refund status, payout, easy collect) is _our server calling Easebuzz_. The app reaches those only through ordinary closed v4 routes behind `api_key_v3 → protect → check_user_company_status → requireRole`.

**And that one open endpoint cannot move money.** It checks the reverse hash, records what arrived as a hint in `pay_trns`, and answers a static page. It makes no call to Easebuzz and never touches a voucher, an invoice or the ledger. Money moves in exactly one function — `settle(txnid)` — which asks Easebuzz server-to-server what really happened, and which is reachable only from closed routes and the internal sweep.

The rest, in six lines:

1. **The server owns every money field.** The client sends invoice ids. Amount, `txnid`, `surl`, `furl`, payer name/email/phone and `sub_merchant_id` are never read from a request body.
2. **The return POST is a hint; `transaction/v2/retrieve` is the truth.** The agreed flow already says so: "confirms with a status check".
3. **One door to the ledger**, claimed atomically, safe to re-enter after a crash, and built on the existing v3 voucher services — no forked, weaker path.
4. **Integer paise inside**; a decimal string exists only at the Easebuzz boundary.
5. **Every exchange with Easebuzz is stored in `pay_trns`**, redacted — no hash, no key, no card, bank or UPI identifiers.
6. **Default OFF.** A kill switch that stops _starting_ payments and never stops _finishing_ them.

The kit itself is a demo: we copy its hash recipes and leave its architecture (§2).

---

## 2. What is in the kit — what we take, what we leave

### 2.1 File by file

| File (present in the folder)                 | What it does                                                                                                 | Take                                                                                                                 | Leave                                                                                                                                                                                                                                                                                                     |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `easebuzz-lib/utils.js`                      | Hash recipes, test/prod URL table, validation, two HTTP helpers                                              | The eight hash sequences (as test vectors); the four base URLs (as constants); `maxRedirects: 0`; the field patterns | `js-sha512` and `axios` — `node:crypto` and the built-in `fetch` do both, so the integration adds **zero dependencies**. `_getConfig()` falling back to a generic `ENV` variable and then silently to `test`. `_sanitizeParams()` silently truncating a field to 500 characters — we reject instead       |
| `easebuzz-lib/initiate_payment.js`           | `payment/initiateLink` → `access_key` → redirect to the hosted checkout                                      | The call. This is the Phase-3 flow                                                                                   | Every field — amount, `txnid`, `surl`, `furl` included — arriving from a form                                                                                                                                                                                                                             |
| `easebuzz-lib/initiate_payment_iframe.js`    | The same call; hands `{ key, access_key, env }` to the browser for Easebuzz's checkout script                | Later, for a web client only (§5)                                                                                    | Trusting the script's `onResponse` callback in the browser                                                                                                                                                                                                                                                |
| `easebuzz-lib/transaction.js`                | Status of one `txnid`                                                                                        | **The truth call** — everything in §7 turns on it                                                                    | —                                                                                                                                                                                                                                                                                                         |
| `easebuzz-lib/transaction_date.js`           | Every transaction of the merchant account in a date range                                                    | Daily reconciliation                                                                                                 | Proxying it to anyone: VSYST is the master merchant, so one response lists **every dealer's** payments and payers                                                                                                                                                                                         |
| `easebuzz-lib/refund.js`, `refund_status.js` | Raise a refund; read its state                                                                               | Phase 5                                                                                                              | —                                                                                                                                                                                                                                                                                                         |
| `easebuzz-lib/payout.js`                     | Settlement report by date, optionally per `sub_merchant_id`                                                  | The daily settlement match the agreed flow asks for                                                                  | —                                                                                                                                                                                                                                                                                                         |
| `easebuzz-lib/easy_collect.js`               | Creates a payment link Easebuzz sends by SMS / email / WhatsApp                                              | Last phase                                                                                                           | Phone and email typed into a form                                                                                                                                                                                                                                                                         |
| `response.js`                                | The `surl`/`furl` handler: reverse hash, `crypto.timingSafeEqual`, an allow-list of fields, a one-time token | The reverse-hash check, the constant-time compare, the allow-list idea                                               | The in-memory `Map` and its `setInterval`: production is a standalone box plus an ASG fleet behind one ALB, so the POST and the follow-up read land on different machines; a restart loses everything; and the timer keeps Jest open                                                                      |
| `index.js`                                   | One unauthenticated `POST /easebuzz?api_name=…` that dispatches to **every** call, refund included           | The hardcoded checkout base URLs (no open redirect)                                                                  | The dispatcher — whoever can reach it can refund. It also `require()`s a handler keyed by a request parameter (a prototype key such as `__proto__` passes its existence check and only fails inside `require`). v4 has one route per capability and no dynamic dispatch. Its CSP allows `'unsafe-inline'` |
| `views/*.html`, `public/*`                   | Demo forms, one per call                                                                                     | The field patterns (§2.3)                                                                                            | Everything else                                                                                                                                                                                                                                                                                           |
| `.env`, `.gitignore`                         | Key, salt, environment                                                                                       | The variable names                                                                                                   | **`.env` is tracked by git in the kit** — its `.gitignore` lists only `node_modules/`. We never copy that habit                                                                                                                                                                                           |
| `package.json`                               | express 4, axios, js-sha512, dotenv, helmet, express-rate-limit                                              | Nothing                                                                                                              | All of it                                                                                                                                                                                                                                                                                                 |
| _(README only)_ Seamless payment             | Not in the folder                                                                                            | —                                                                                                                    | Out of scope — and it is the one flow that would put card numbers on our server. Hosted checkout keeps the promise in 04-payment-flow §C: "VSYST stores no card numbers, bank credentials or UPI PINs"                                                                                                    |

### 2.2 The hash recipes (from `utils.js`)

SHA-512, lowercase hex, fields joined with `|`:

```
initiate          key|txnid|amount|productinfo|firstname|email|udf1|…|udf10|SALT
return (reverse)  SALT|status|udf10|…|udf1|email|firstname|productinfo|amount|txnid|key
transaction       key|txnid|SALT
transaction_date  key|merchant_email|start_date|end_date|SALT
refund            key|merchant_refund_id|easebuzz_id|refund_amount|SALT
refund_status     key|easebuzz_id|SALT
payout            merchant_key|start_date|end_date|SALT
easy_collect      key|merchant_txn|name|email|phone|amount|udf1|…|udf5|message|SALT
```

Three things follow from the recipes themselves:

- **The reverse hash covers** `status`, `udf1–10`, `email`, `firstname`, `productinfo`, `amount`, `txnid`, `key` — and **nothing else**. Easebuzz's own transaction id, the payment mode and the bank reference in a return POST are unauthenticated. We never read them from there; they come from `transaction/v2/retrieve`.
- **`sub_merchant_id` is in no hash.** It decides whose bank account is settled, and only TLS protects it — one more reason the initiate call is server-to-server and never a form assembled on the device.
- **`|` is the separator, and the kit's own patterns allow `|` inside `txnid` and `productinfo`.** `("a|b","c")` and `("a","b|c")` hash alike. Rule: no value we send may contain `|` (S-5).

### 2.3 Field rules worth keeping (from the kit's forms)

| Field                        | Rule in the kit                                                       |
| ---------------------------- | --------------------------------------------------------------------- |
| `txnid`, `merchant_txn`      | `^[a-zA-Z0-9_\-/]{1,40}$` (the kit also allows a pipe — we do not)    |
| `amount`, `refund_amount`    | Decimal string, at most 2 decimals, a decimal point required, `>= 1`  |
| `productinfo`                | Letters, digits, space, `_`, `-`; 1–45 characters                     |
| `firstname`, `name`          | Letters, digits and `& ' . _ ( ) / , @ -` and space; 1–150 characters |
| `phone`                      | Optional `+cc-`, then 5–20 digits                                     |
| `udf1–7`                     | Letters, digits and `. / \ , _ # @ - = + &` and whitespace; up to 300 |
| `sub_merchant_id`            | Letters, digits, `-`; up to 15                                        |
| `start_date`, `end_date`     | `DD-MM-YYYY`                                                          |
| `expiry_date` (easy collect) | `DD-MM-YYYY` or `DD-MM-YYYY HH:MM:SS AM/PM`                           |

### 2.4 Where the kit disagrees with itself

| File               | Header comment says                      | Code does                  |
| ------------------ | ---------------------------------------- | -------------------------- |
| `transaction.js`   | JSON POST                                | form-encoded (`_curlCall`) |
| `refund.js`        | JSON POST                                | form-encoded (`_curlCall`) |
| `refund_status.js` | form-encoded POST                        | JSON (`_curlCallJson`)     |
| `easy_collect.js`  | "boolean fields must be actual booleans" | sends them as strings      |

Also: `response.js` allow-lists Easebuzz's transaction id as `easebuzz_id` — the name the refund call uses — which may not be the name a payment response uses. **The sandbox is the referee.** Before a parser is written, each call's real request and response is captured once and committed as a scrubbed transport fixture (PG-0). The kit is a reference, not a contract.

---

## 3. What can go wrong

| #   | Threat                                                                                                     | What stops it                                                                                                                                                         |
| --- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1  | A forged "success" posted to the open URL                                                                  | Reverse hash — and even a valid one only records a hint. Money moves on `transaction/v2/retrieve` alone (S-3)                                                         |
| T2  | The amount changed on the way                                                                              | The client never sends an amount (S-1); it is inside both hashes; `settle` compares Easebuzz's amount with ours in integer paise (S-4)                                |
| T3  | Replay or double credit — a return replayed, the sweep and the app racing, a retry after a timeout         | Unique `txnid`; an atomic claim before settling; find-or-create on the voucher; v3's own "Voucher is already approved" guard (S-6). Bug museum #1 is this failure     |
| T4  | Cross-tenant — paying or reading for a pair you are not part of; a dealer seeing another dealer's payments | Ids come from the token; `assertRelation` before any read; `udf` binding inside the hash; the by-date and payout reports are never proxied (S-2, S-10)                |
| T5  | Money settled to the wrong dealer's bank                                                                   | `sub_merchant_id` from the superadmin-written map only; unique per dealer; snapshotted on the attempt; checked again at settle if Easebuzz echoes it (S-9)            |
| T6  | The salt leaks — repo, logs, AMI, client                                                                   | One module reads it; never logged, stored or sent to a device; dummy values in `.env.ci`; SSM before go-live (§9)                                                     |
| T7  | The salt is guessed offline                                                                                | See the note below. S-3 makes a guessed salt useless for crediting; Q2 asks Easebuzz to pin the dashboard APIs to our IPs                                             |
| T8  | Open redirect or SSRF                                                                                      | `surl`, `furl`, the checkout base and all four Easebuzz hosts are constants; no URL is ever built from input or from the `Host` header (S-8)                          |
| T9  | Test and production mixed up — real payers sent to the sandbox, or a test box charging real money          | `EASEBUZZ_ENV` is exactly `test` or `prod`, anything else disables the feature; `prod` only with `NODE_ENV=production`, and the reverse (S-8)                         |
| T10 | PII or secrets in logs and in the database                                                                 | POST only, no query string (the production `logs` collection stores `originalUrl`); allow-list and deny-list before anything reaches `pay_trns` (§8)                  |
| T11 | Refund abuse — wrong role, over-refund, double refund, a retried timeout                                   | Dealer only; an atomic `refundable_paise` reservation; `merchant_refund_id` is our own document id; a timeout is answered with `refund_status`, never a resend (§7.5) |
| T12 | Flooding the open endpoint                                                                                 | Small body limit, a rate limit, hash before any database work, no outbound call from that endpoint (§6)                                                               |
| T13 | A crash between two writes — no money path in this codebase uses a transaction today                       | Ordering plus idempotent re-entry: every step can be repeated, and the sweep repeats it (§7.4)                                                                        |
| T14 | Easebuzz slow or down                                                                                      | 10 s timeout; a timeout is never read as "failed"; `pending` stays pending; clients get `UNAVAILABLE`                                                                 |
| T15 | Something reflected into the return page                                                                   | The page is static and carries no request data; `no-store`; its own strict CSP                                                                                        |
| T16 | A new dependency turning hostile                                                                           | There are none (S-12)                                                                                                                                                 |

**T7 in full.** The salt is the only secret in the scheme, it is typically a short alphanumeric string, and every payer legitimately sees one valid `(fields, hash)` pair in their own browser when Easebuzz posts them back to us — enough to test guesses offline. Two consequences. A valid reverse hash must never be sufficient to credit money (S-3), so a guessed salt cannot forge a payment. But the same key and salt also sign refund calls made _directly to Easebuzz_, which nothing in our code can stop — hence Q2.

---

## 4. The safety rules

Numbered so that tests, PRs and reviews can point at them.

- **S-1 — The server owns every money field.** `POST /api/v4/payments` accepts `companyId` and `invoiceIds` and nothing else. The v4 validator already rejects unknown keys at every level, so a client that sends `amount` gets `VALIDATION 400`. Payer name, email and phone come from `req.user`; `productinfo` is a constant; `txnid` is 32 hex characters from `crypto.randomBytes(16)`.
- **S-2 — Tenancy comes from the token.** `tenantOf(req)` and `scopeFilter(req)` only; `assertRelation` runs before the first read of any id the body names; one tenancy test per id the body accepts (PR template). The attempt's id, `dealer_id` and `cust_id` travel as `udf1–3` — inside both hashes — and must match the stored document on the way back.
- **S-3 — The return POST is a hint; `transaction/v2/retrieve` is the truth.** No state that means "paid" is ever set from anything the payer's browser carried.
- **S-4 — Integer paise inside.** `amount_paise` through `api_v4/lib/money.js`. The decimal string exists only at the boundary: out as `"<rupees>.<2 digits>"` built from the integer; in through a strict decimal-string parser (`^\d+(\.\d{1,2})?$`), never `parseFloat(x) * 100`. Comparisons are integer to integer. The reverse hash is computed over the **exact string Easebuzz sent**, not a reformatted one. `voc_msts.amount` is written as `rupees(amount_paise)`.
- **S-5 — One hash module.** `node:crypto` SHA-512. The kit's sequences are its test vectors. Every value must be a string (a repeated form field parses to an array — rejected), and no value we send contains `|`. Comparison is constant-time, the way `timingSafeCompare` in `helpers/middlewares.js:6-13` does it.
- **S-6 — One door to the ledger.** `settle(txnid)` is the only function that creates or approves a voucher for a gateway payment, and every path — the app's verify call, the sweep, reconciliation, later the webhook — calls it. Bug museum 5–8 ("the same rule written more than once") and 9–11 ("not every caller reaches it") are the two ways this fails, so the suite has one test per caller asserting the same ledger truth from raw documents.
- **S-7 — Same domain rules as the app.** Vouchers are created and approved through `api_v3/services/voc_msts.js` (`createCustomerVoucher` / `createCustomerOnAcVoucher`, then `updateVocStatus`). That is what rebuilds `month_crdrs`, moves `adv_dep`, sets the invoice statuses and notifies both sides. The dead Paytm handler wrote its own voucher and never posted to the ledger — the cautionary example. v4 already imports v3 services (`api_v4/readmodels/customers.js`); v3 is called, not edited.
- **S-8 — Constants, not inputs.** The four Easebuzz hosts, the checkout base URL and our return URL are configuration. `surl` and `furl` are never built from `req.headers.host`. `EASEBUZZ_ENV` is parsed strictly and paired with `NODE_ENV`.
- **S-9 — `sub_merchant_id` is safety-critical data.** Written only by a superadmin through a fully gated route, format-checked, unique across dealers, snapshotted onto the attempt at initiate, and compared at settle if Easebuzz echoes it (Q3).
- **S-10 — No raw proxying.** No Easebuzz response is handed to a client. Read models project named fields; Easebuzz's error text goes to `pay_trns`, and the client gets a catalogue code.
- **S-11 — `pay_trns` is evidence.** `events[]` is push-only, redacted before it is written, capped in size and count; no route accepts a `pay_trns` document from a client or returns one raw (§8).
- **S-12 — No new runtime dependencies.** Transport and clock are injectable from day one (`SEAMS.md` in the API repo lists hardcoded clocks and HTTP calls among the things that make bugs unreproducible here); CI stays hermetic. Every date crossing the boundary is formatted and parsed as IST explicitly (SEAMS §4).
- **S-13 — Default OFF, and OFF never strands money.** The switch blocks initiate, refunds and links. It never blocks the return endpoint, verify, the sweep or reconciliation.
- **S-14 — Captured money always lands.** If a confirmed payment cannot be applied to its invoices any more (they were paid another way meanwhile), it posts as an on-account voucher and is flagged for the dealer — never dropped. This is the refund policy's own rule for a duplicate payment ([06 §6](../../correspondence/IPG_Easebuzz/onboarding/06-cancellation-refund-policy.md)).

---

## 5. The v4 surface

Closed routes — one new module `api_v4/routes/payments.js`, exporting `{ path: "/payments", roles: ["dealer", "customer", "superadmin"], router }`; every route narrows with its own `requireRole` placed before `validate`:

| #   | Route                                                | Roles            | Kit file                           | What it does                                                                                                       | Phase |
| --- | ---------------------------------------------------- | ---------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ----- |
| 1   | `GET`, `PUT /api/v4/payments/config`                 | superadmin       | —                                  | The kill switch and the dealer → `sub_merchant_id` map (§10)                                                       | PG-1  |
| 2   | `POST /api/v4/payments`                              | customer         | `initiate_payment.js`              | Creates the attempt, calls `initiateLink`, answers `{ paymentId, checkoutUrl, expiresAt }`                         | PG-3  |
| 3   | `POST /api/v4/payments/:id/verify`                   | customer, dealer | `transaction.js`                   | Runs `settle` now and answers our status                                                                           | PG-3  |
| 4   | `GET /api/v4/payments/:id`, and a cursor list        | customer, dealer | —                                  | Our own records, projected (`lib/cursor`, never `advancedResults`)                                                 | PG-3  |
| 5   | `POST /api/v4/payments/reconcile`                    | superadmin       | `transaction_date.js`, `payout.js` | Runs the daily match on demand; answers counts only                                                                | PG-4  |
| 6   | `POST /api/v4/payments/:id/refunds`                  | dealer           | `refund.js`                        | Raises a refund against a settled payment                                                                          | PG-5  |
| 7   | `POST /api/v4/payments/:id/refunds/:refundId/verify` | dealer           | `refund_status.js`                 | Reads the refund's state from Easebuzz                                                                             | PG-5  |
| 8   | `POST /api/v4/payments/links`                        | dealer           | `easy_collect.js`                  | A payment link for a related customer; phone and email from our records                                            | PG-6  |
| 9   | Web checkout variant of #2                           | customer         | `initiate_payment_iframe.js`       | Answers the `access_key` (and the public merchant key) for Easebuzz's checkout script; success still comes from #3 | PG-6  |

Open routes — above the gates:

| Route                               | Authenticated by                    | Kit file      | What it does                            | Phase |
| ----------------------------------- | ----------------------------------- | ------------- | --------------------------------------- | ----- |
| `POST /api/v4/open/easebuzz/return` | The reverse hash — and nothing else | `response.js` | Records the hint; answers a static page | PG-2  |

That is the whole list. `surl` and `furl` both point at it, as in the kit: what happened comes from the verified payload and the status check, not from which URL was hit.

**Errors** use the existing frozen catalogue — no new codes: `UNAVAILABLE` (switch off, Easebuzz down or slow), `CONFLICT` (a payment for these invoices is already in flight; a refund exceeds what is refundable), `VALIDATION`, `FORBIDDEN`, `NOT_FOUND`.

**New files**, all inside `api_v4/`: `lib/easebuzz/{config,hash,transport,client}.js`, `lib/paymentSwitch.js`, `schemas/payments.js`, `commands/payments.js`, `readmodels/payments.js`, `controllers/payments.js`, `routes/payments.js`, `open/{index,easebuzzReturn}.js`.

---

## 6. The one open endpoint

### 6.1 Why it has to be open

After checkout, Easebuzz sends the payer's browser to `surl` or `furl` with an `application/x-www-form-urlencoded` POST. That browser has no `x-api-key` and no Bearer. `buildV4()` puts `api_key_v3()` and `protect` in front of everything (`api_v4/index.js:72-74`) and the loader throws at boot on a module without `roles` — so today there is nowhere for this route to live.

### 6.2 Where it mounts ⚠️ approval

[02-foundations](../oms_app/screen-redesign/02-foundations.md) already names the mechanism: an unauthenticated v4 route mounts **before** the gates in `api_v4/index.js`, "exactly as `api_v/api3.js` does". Proposed:

```js
function buildV4({ probes = [] } = {}) {
  const router = express.Router()
  router.use("/open", buildOpen()) // the ONLY line above the gates
  router.use(api_key_v3())
  router.use(protect)
  // …unchanged
```

with a boot-time contract mirroring the roles one: an open module exports `{ path, guard, router }`, where `guard` names the check that authenticates it (`"easebuzz-reverse-hash"`); a module without a guard is a boot failure. Building it inside `buildV4` means the test app — which mounts `buildV4({ probes })` — gets the same routes as production.

`test/api_v4/harness/mount.test.js` pins "v4 is deliberately CLOSED". That sentence changes on purpose, red then green, to: **the open router contains exactly the listed routes, and every other v4 path still answers 401/403 without a Bearer.** The list is asserted by enumerating the router, so adding an open route without editing the test fails the suite.

### 6.3 What the request passes on its way in

| Middleware (in `dzzlo_oms.js` order)    | Effect on a gateway return                                                                                                          |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `express.json({ limit: "1mb" })` `:59`  | Skips a form-encoded body. No global `urlencoded` parser exists, so the body is `undefined` until our router parses it              |
| `api_key_v1()` `:71`                    | Lets a request with **no** key through — it rejects only a wrong one (`helpers/middlewares.js:25`)                                  |
| `logging()` `:73`                       | In production writes `originalUrl` and the user to the `logs` collection — never the body. So: POST only, and no query string, ever |
| `check_user_version()` `:75`            | Passes when there is no `meta` header (`:128`)                                                                                      |
| `sanitizeMongo()`, `helmet()`, `cors()` | Strip `$` keys; default headers; `*` — harmless here, the response carries no data and no credentials                               |

### 6.4 The handler, cheapest check first

1. `POST` only; `Content-Type` must be `application/x-www-form-urlencoded`, anything else is 415.
2. `express.urlencoded({ extended: false, limit: "16kb", parameterLimit: 60 })` on **this router only** — the precedent is the per-router parser in `api_v3/routes/auth/index.js:47`. The global parser is not widened.
3. A per-IP rate limit (`express-rate-limit` is already a dependency).
4. Shape: every value is a string of at most 300 characters; an array (a repeated field) is rejected.
5. `key` equals our merchant key, compared in constant time.
6. Reverse hash, compared in constant time — **before any database work**, so junk costs us nothing but CPU.
7. Look up `pay_trns` by `txnid`. It must exist, be an Easebuzz payment row, and its `udf1–3` must equal the stored attempt id, `dealer_id`, `cust_id`.
8. `paise(amount)` equals the stored `amount_paise`.
9. One atomic update: push the redacted event; move `initiated → returned`. Any later state is left alone — a replayed return adds an event at most.
10. Answer.

### 6.5 What it never does, and what it answers

It never calls Easebuzz, so it cannot be used to make us hammer them. It never creates or approves a voucher and never sets a state that means "paid".

Its answer is always the same: one static HTML page — "Your payment is being confirmed. You can return to the app." — with status 200 whether the hash matched or not, no request data in it, `Cache-Control: no-store`, and its own `Content-Security-Policy: default-src 'none'`. No oracle, nothing to reflect. Failures are counted internally — hash mismatch, key mismatch, unknown `txnid`, amount mismatch, array field — as one log line each, without the payload.

**In the app** (`react-native-webview` is already installed; no deep-link scheme is needed): the WebView loads `checkoutUrl`, with no JS bridge (`onMessage` and `injectedJavaScript` unused) because it will render bank pages we do not control. When it sees a navigation to the return URL it closes, and the app calls `POST /api/v4/payments/:id/verify`. **The app never decides that a payment succeeded — it asks.**

### 6.6 The webhook

04-payment-flow step 6 names a webhook. The kit has no webhook file, so it is outside this plan's scope — and the design does not depend on it: the status check that step 6 also requires ("and confirms with a status check"), the app's verify call and the sweep give the same guarantee, a little slower when the payer closes the app mid-checkout. When Easebuzz's webhook specification is in hand it becomes the second entry in the open router under the same contract: hash → record → `settle(txnid)` (D8).

### 6.7 What the hosting means for this endpoint

From [DZZLOOMS_backend_AWS](./DZZLOOMS_backend_AWS.md) and `docs/runbook.md` in the API repo:

- **The instances accept HTTP from `0.0.0.0/0` today.** A request sent straight to an instance skips the ALB and TLS and can set its own `X-Forwarded-For`; with `trust proxy: 1` that makes `req.ip` forgeable. Until the instance security group admits only the ALB, every IP-based control is advisory. The hash is the control; the rate limit is cost control (Q6).
- **`express-rate-limit`'s default store is per process**, and production is several processes. The effective ceiling is the limit times the number of targets — tasks_11 already warns about this. Acceptable for cost control; never the thing that keeps money safe.
- **During a blue/green deploy two code versions serve at once** (weights 1 : 5). The return route must exist on every target before initiate is switched on — the kill switch gives that ordering — and `pay_trns` changes stay additive.
- **The API's public hostname is not recorded anywhere in the vault** (Q1).

---

## 7. The payment lifecycle

### 7.1 Sequence

```
 App (customer)          API v4 — closed routes            Easebuzz             API v4 — open route
   │ POST /payments            │                               │                       │
   │ {companyId, invoiceIds}   │                               │                       │
   ├──────────────────────────▶│ gates → assertRelation        │                       │
   │                           │ amount = Σ invoices (paise)   │                       │
   │                           │ pay_trns: created             │                       │
   │                           ├── initiateLink (TLS) ────────▶│                       │
   │                           │◀─────────── access_key ───────┤                       │
   │◀── {paymentId,            │ pay_trns: initiated           │                       │
   │     checkoutUrl}          │                               │                       │
   │ WebView → checkoutUrl ────────────────────────────────────▶ payer authenticates   │
   │                           │                               ├── browser POST ──────▶│ reverse hash ✓
   │                           │                               │   (surl = furl)       │ pay_trns: returned
   │◀──────────────────────────────────── static page, no data ────────────────────────┤ no gateway call,
   │ WebView closes            │                               │                       │ no ledger
   │ POST /payments/:id/verify │                               │                       │
   ├──────────────────────────▶│ settle(txnid)                 │                       │
   │                           ├── transaction/v2/retrieve ───▶│                       │
   │                           │◀────── status, amount ────────┤                       │
   │                           │ checks → voucher → approve    │                       │
   │◀── {status: "success"}    │ pay_trns: success             │                       │
                               │                               │
                               │ sweep: the same settle(txnid) for anything still open
```

### 7.2 States

| State                            | Meaning                                                                    | Set by              | In-flight lock |
| -------------------------------- | -------------------------------------------------------------------------- | ------------------- | -------------- |
| `created`                        | Attempt written; Easebuzz not called yet                                   | initiate            | held           |
| `initiated`                      | `access_key` issued; the payer is at checkout                              | initiate            | held           |
| `returned`                       | A hash-verified return arrived. A hint — says nothing about money          | the open endpoint   | held           |
| `pending`                        | Easebuzz says the bank has not answered yet                                | `settle`            | held           |
| `success`                        | Easebuzz confirmed; the voucher exists and is approved                     | `settle` only       | released       |
| `failed`, `cancelled`, `expired` | Easebuzz says not paid / the attempt aged out                              | `settle`, the sweep | released       |
| `mismatch`                       | Easebuzz says success but a check failed (amount, `txnid`, tenant binding) | `settle`            | held + alert   |

`failed`, `cancelled` and `expired` are **not final for money**: if a later status check or the daily reconciliation finds `success` at Easebuzz, `settle` still runs (S-14). Only the literal `success` settles. An unknown status string never settles, and never fails a payment for good without a status check saying so (Q5). Nothing is ever deleted — the agreed flow's "cleared after 24 hours" becomes "expires after 24 hours".

Two attempts cannot hold the same invoices at once: a partial unique index on `{ dealer_id, cust_id, purpose_key }` where `open: true`, with `purpose_key` a hash of the sorted invoice ids. A second initiate inside the window gets the first attempt back if its checkout is still usable, otherwise `CONFLICT`. While an attempt is `pending` at the bank the lock stays held — which is exactly when a retry would become a double payment.

### 7.3 `settle(txnid)` — the one door

1. **Claim.** One `findOneAndUpdate` filtered on the state and on `settle.claimed_at` being unset or older than 10 minutes. One winner; everyone else reads the current state and returns it.
2. **Ask.** `transaction/v2/retrieve`, server-to-server, constant host, 10 s timeout.
3. **Record.** Push the redacted response to `events[]`.
4. **Not `success`?** Map the state, release the claim, stop.
5. **Check.** `txnid`, the merchant key, `paise(amount) === amount_paise`, `udf1–3`, and `sub_merchant_id` if echoed. Any failure → `mismatch`, alert, stop. A mismatch is never settled automatically.
6. **Voucher — find or create.** Look in `voc_msts` for `{ dealer_id, cust_id, pay_mode: "ONLINE", chq_no: <Easebuzz's id> }`; otherwise create through the v3 service — `bank_name: "EASEBUZZ"`, `pay_type: "CREDIT"`, `remarks` = the bank reference, `pay_dt` = the gateway's transaction time parsed as IST. If the invoices can no longer take the payment: the on-account path (S-14). Then set `voc_id` conditionally (`voc_id` absent); the loser of that update removes its own still-unapproved voucher.
7. **Approve** through `updateVocStatus`. Its "Voucher is already approved" answer counts as done.
8. **Close.** `status: "success"`, `pay_res` = the deciding response, `refundable_paise` = `amount_paise`, `open` unset.

`pay_mode` and `voc_type` have no enum in `models/voc_msts.js` (tasks_13 flags this), so `"ONLINE"` needs no model change; the app's mode labels and two v3 test-helper regexes learn the word. When `fin_txns` lands, this function is the single caller that posts `src.type: "GATEWAY"` with `idem_key` = `txnid` ([tasks_13 Q4](../tasks/tasks_13_db_architecture/00-overview.md)).

### 7.4 If the process dies

No money path in this codebase runs inside a MongoDB transaction, and the v3 services take no session, so none can be wrapped around them without editing v3. Safety comes from ordering and from every step being repeatable:

| Dies after                                     | What is true                              | Who repairs it                                  |
| ---------------------------------------------- | ----------------------------------------- | ----------------------------------------------- |
| `created`, before Easebuzz answers             | No payment can exist                      | The sweep expires it                            |
| `initiated`; the payer pays; the app is killed | Money captured; we hold a hint or nothing | The sweep asks Easebuzz and settles             |
| Step 3 of `settle`                             | Evidence stored; nothing posted           | The claim times out; the sweep re-enters        |
| Step 6, voucher created, `voc_id` not set      | An unapproved ONLINE voucher exists       | Re-entry finds it by Easebuzz's id and links it |
| Step 7, approved, state not closed             | The ledger is right; `pay_trns` lags      | Re-entry: "already approved" → close            |

### 7.5 Refunds (PG-5)

Dealer only, against a `success` payment of their own — the agreed flow and the [refund policy](../../correspondence/IPG_Easebuzz/onboarding/06-cancellation-refund-policy.md) both say the dealer decides. The amount is reserved first, with one conditional update — `{ _id, status: "success", refundable_paise: { $gte: amount } }` with `$inc: -amount` — so two concurrent refunds cannot exceed what was captured, no transaction needed; a refund Easebuzz definitively rejects gives the amount back. `merchant_refund_id` is the refund row's own id, which makes a retry the same request. **A timeout is never answered by sending the refund again** — it is answered by `refund_status`. The ledger's reversing entry goes through the existing dealer-voucher service; when it posts is D7.

### 7.6 The sweep and the daily match (PG-4)

- **Every few minutes:** rows with `open: true` older than two minutes → `settle`. After 24 hours without success → `expired`. The events cap (S-11) stops endless polling and raises an alert instead.
- **Daily, for the IST day before:** `transaction/v2/retrieve/date` and `settlements/v1/retrieve`. Success there but not here → `settle`. Success here but not there → alert; it should be impossible. Amount or `sub_merchant_id` differs → alert. Only our own `txnid`s are kept from the response (S-10).
- **Trigger:** an in-process timer, `unref()`'d and off under Jest. It is safe on every instance at once because every row is claimed atomically, and a missed run is harmless. The alternative — a scheduler calling route #5 — needs a long-lived superadmin token stored somewhere, which is one more secret.

---

## 8. `pay_trns` — storing every API response

Decided 2026-09-17: responses are stored in the existing `pay_trns` collection. The onboarding plan had pencilled in the same home ("webhook to API (`pay_trns`)").

### 8.1 What is there today

`models/pay_trns.js`: `inv_id` (ObjectId, **required**), `pay_res` (Mixed), `pay_status` (Mixed), timestamps; no tenancy fields, no `txnid`, no indexes. It was the dead Paytm integration's store — some legacy rows carry an order id in `inv_id`. Its generic CRUD routes (`create(req.body)`, `findByIdAndUpdate(id, req.body)`, `deleteMany(<query string>)`) are unmounted today: `dzzlo_oms.js:107`, `api_v/api2.js:65`, `api_v/api3.js:65`.

With Mongoose's default strict mode, any field not in the schema is silently dropped, and `inv_id` is required — so as it stands the model cannot hold an on-account or advance-deposit payment, a `txnid`, or a tenant.

### 8.2 Proposed shape ⚠️ approval (D1)

Additive only — nothing removed, nothing renamed, legacy rows stay valid:

```js
{
  // legacy — kept
  inv_id,        // required → optional (on-account and advance-deposit payments have no invoice)
  pay_res,       // the ONE response that decided the final state, redacted — same meaning as in Paytm days
  pay_status,    // left exactly as it is; new code neither reads nor writes it

  // new
  gateway,       // "easebuzz" — legacy rows have none, so every reader filters on it
  kind,          // "payment" | "refund" | "link" | "report"
  txnid,         // 32 hex; unique
  easepayid,     // Easebuzz's own id, taken from transaction/v2 only
  dealer_id, cust_id, user_id,   // from the token, never from a body
  purpose,       // "invoices" | "on_account" | "adv_dep"
  inv_ids, purpose_key, open,    // the in-flight lock
  amount_paise, refundable_paise,   // integers
  sub_merchant_id,               // snapshot at initiate
  status,        // the state machine — a typed enum, the single source of truth
  voc_id,        // set by settle
  parent_id,     // refund → its payment
  req,           // what we sent, minus key and hash
  events,        // [{ api, at, http_status, ok, res }] — push-only
  settle,        // { claimed_at, attempts, done_at }
  expires_at,
}
```

Indexes: `{ txnid }` unique, partial on `gateway: "easebuzz"` · `{ dealer_id, cust_id, purpose_key }` unique, partial on `open: true` · `{ open, updatedAt }` for the sweep · `{ dealer_id, createdAt }` and `{ cust_id, createdAt }` for the lists.

Why one document per attempt with the exchanges inside it, rather than one document per exchange: state and evidence then change in a **single atomic update**, which is what stands in for the transactions this codebase does not use on money paths.

Rejected: binding a second model to the same collection from inside `api_v4/`, to avoid touching `models/`. Two schemas for one collection is bug museum 5–8 waiting to happen, and it hides a schema change from the one folder people look in.

### 8.3 What is stored, and what never is

| Source                                          | Rule                                                                                                                                                                                                                        |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The browser return (untrusted)                  | **Allow-list:** `txnid`, `status`, `amount`, `productinfo`, `mode`, `payment_source`, `bank_ref_num`, Easebuzz's id, `udf1–3`. Strings only, 300 characters at most. Anything else is dropped                               |
| Server-to-server responses (TLS, constant host) | Stored whole **minus a deny-list**: `hash`, `key`; card, bank-account and UPI identifiers; payer name, email, phone — we already hold the payer as `user_id`. Capped at 16 KB; a larger body is stored truncated and marked |
| The report calls (`transaction_date`, `payout`) | A run summary — range, counts, mismatches — plus only the rows whose `txnid` is ours. These responses list every dealer's payers                                                                                            |
| What we send (`req`)                            | As sent, minus `key` and `hash`                                                                                                                                                                                             |

Never stored, anywhere: the salt, any hash in either direction, card numbers, bank credentials, UPI PINs or handles. That keeps the statement in 04-payment-flow §C true.

### 8.4 Rules around the collection

- `events[]` only ever receives `$push`. At most 50 per document; past that the sweep stops polling and raises an alert.
- No route accepts a `pay_trns` document from a client or returns one raw. Reads go through `api_v4/readmodels/payments.js`, which projects named fields and scopes by `scopeFilter(req)`.
- A conventions test pins that nothing mounts `api_v1/routes/collections/pay_trns` or `api_v1/routes/Payment/paytm` again.
- Not cached (`tasks_01/06-caching.md` already lists `pay_trns` among the collections that must not be).
- tasks_13 flags `pay_trns` as unbounded. Retention is Q9 — a finance decision, not a default we pick.

---

## 9. Secrets and configuration

| Variable                | Rule                                                                                                                                   |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `EASEBUZZ_MERCHANT_KEY` | An identifier rather than a secret, but still never sent to a device in the hosted flow                                                |
| `EASEBUZZ_SALT`         | The only secret. Read by exactly one module                                                                                            |
| `EASEBUZZ_ENV`          | Exactly `test` or `prod`. Anything else: the feature reports `UNAVAILABLE` and logs loudly. It never falls back to `test` like the kit |
| `EASEBUZZ_RETURN_URL`   | The absolute https URL of §6, per environment. Never derived from the request                                                          |

- **Pairing:** `prod` only when `NODE_ENV=production`, and production only with `prod`. The testing server can never charge a real account; production can never send a real payer to the sandbox.
- **One reader:** `api_v4/lib/easebuzz/config.js`. A conventions test greps that `EASEBUZZ_SALT` appears in no other source file.
- **A bad value disables payments, not the API.** The rest of the app keeps serving.
- ⚠️ approval: `.env.example` gains the block, and so does `.env.ci` with dummy values — `.env.ci` is committed (`.gitignore` does not list it), so it must never hold a real value. CI never reaches the network.
- **Before go-live (D9):** today secrets sit in `.env` on the instance, and every baked AMI snapshots that file ([DZZLOOMS_backend_AWS](./DZZLOOMS_backend_AWS.md), Security item 4). The salt should be in SSM Parameter Store and fetched at boot through the instance role before it is a production salt.
- **Rotation:** regenerate in the Easebuzz dashboard → update every target → `pm2 reload`. Returns signed with the old salt fail the reverse hash and are dropped — and nothing is lost, because `settle` asks Easebuzz with the new salt. S-3 is what makes rotation safe.

---

## 10. Kill switch, limits, and calling Easebuzz

**The switch.** One `counters` document, `doc_name: "payment_gateway"` — the same counters-doc pattern as `helpers/appFeatures.js`, with two deliberate differences:

1. **Absent or unreadable means OFF.** `appFeatures` says "absent means on" because a screen fails safe when it is shown. A payment fails safe when it is stopped.
2. **The writer sits behind the full v4 chain with `requireRole(["superadmin"])`.** The v3 `/sadmin` routes are behind the API key only (`api_v/api3.js:22` sits above any user check) — acceptable for a diesel limit, not for turning money on. Reader and writer both live in `api_v4/lib/paymentSwitch.js`, so neither `helpers/` nor v3 changes (Q8 asks whether dip-web's DB-Actions page can send a Bearer).

```js
data: {
  enabled: false,           // master switch
  refunds: false, links: false,
  max_amount_paise: <Q10>,  // ceiling per payment
  dealers: { "<dealer_id>": { enabled: true, sub_merchant_id: "…" } },
}
```

The reader caches for 60 s per process, so a flip reaches the whole fleet within a minute. The writer validates everything before writing anything, refuses a `sub_merchant_id` another dealer already holds (S-9), `$set`s per dotted key, and reads back rather than echoing.

**Limits** — starting points, and cost control only: the return endpoint per IP; initiate per user, plus the in-flight lock; verify per payment; refunds per user.

**Calling Easebuzz** — `api_v4/lib/easebuzz/client.js`:

- Hosts are constants: `pay.easebuzz.in` / `testpay.easebuzz.in` for `initiateLink`; `dashboard.easebuzz.in` / `testdashboard.easebuzz.in` for the rest.
- Built-in `fetch`; `AbortSignal.timeout(10_000)`; `redirect: "error"`; a response size cap; JSON parsing guarded — a non-JSON body is an `UNAVAILABLE`, stored as text in the event.
- Retries: reads (`transaction`, `refund_status`) retry with backoff. `initiateLink` and `refund` never retry blindly — a timeout is followed by the matching read.
- The transport is a constructor argument. Tests pass a fake that replays the sandbox captures; the suite never opens a socket.

---

## 11. Exposures outside this plan that payments inherit

Not caused by this work, but it posts money into the same ledger, so they are listed rather than left implicit. Each wants its own small, test-first change.

| #   | What                                                                                                                                                                                                                                                                                                          | Where                                                     |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| E1  | **v3 money routes need only the app's API key — no Bearer.** `protect` appears in `api_v3/routes` only in commented-out lines, and `check_user_company_status` lets a request with no user straight through. `/api/v3/voc_msts/*` takes `dealer_id` and `cust_id` from the body. The key ships inside the app | `helpers/middlewares.js:69-71`, `api_v/api3.js`           |
| E2  | The instances accept HTTP from anywhere, bypassing the ALB and TLS                                                                                                                                                                                                                                            | DZZLOOMS_backend_AWS, Security item 3                     |
| E3  | Secrets live in `.env` on disk and are baked into AMIs                                                                                                                                                                                                                                                        | DZZLOOMS_backend_AWS, Security item 4                     |
| E4  | `cors()` allows every origin (SEC-5 still open)                                                                                                                                                                                                                                                               | [tasks_01/02](../tasks/tasks_01/02-security-hardening.md) |
| E5  | The `logs` collection stores the whole user document and the full URL on every request, with no TTL                                                                                                                                                                                                           | tasks_13 D6                                               |
| E6  | No static egress IP — the same gap [tasks_15](../tasks/tasks_15_govt_apis/00-overview.md) already budgets for                                                                                                                                                                                                 | DZZLOOMS_backend_AWS                                      |

E1 matters most here: an online payment is only as trustworthy as the ledger it lands in.

---

## 12. Decisions and questions

### Decisions for the user — all PENDING

| #   | Decision                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Recommendation                                                                                                                                                                                           |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | ⚠️ The additive change to `models/pay_trns.js` (§8.2). `AI.md` freezes `models/`, so this needs an explicit yes                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Yes. Without it the model cannot hold a tenant, a `txnid`, or a payment with no invoice                                                                                                                  |
| D2  | **When the voucher is created.** 04-payment-flow step 4 says a _pending_ voucher is created at "Pay now", keyed to the voucher id. That leaves an unpaid ONLINE voucher in the dealer's approval queue, where v3 lets it be approved by hand (credit freed, no money); the customer can delete it mid-checkout (the flow's own "what can be changed"); an abandoned checkout holds the invoices in Processing; and a 24-hour job has to delete rows from the money collection. The alternative: the attempt lives in `pay_trns`, and the voucher is created **and** approved inside `settle` | The alternative. Steps 6–8 of the agreed flow are unchanged; step 4's wording is design intent. Keeping the letter of step 4 needs a test-first v3 guard so an ONLINE voucher cannot be approved by hand |
| D3  | ⚠️ The open-module contract in `api_v4/index.js` and the rewritten sentence in `mount.test.js` (§6.2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Yes — it is the mechanism 02-foundations already names                                                                                                                                                   |
| D4  | The switch inside v4, superadmin-gated, default OFF (§10)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Yes                                                                                                                                                                                                      |
| D5  | Where the dealer → `sub_merchant_id` map lives: inside the switch document (no model change, uniqueness checked by the writer) or a new unique field on `dealer_msts` (enforced by the database; ⚠️ model change)                                                                                                                                                                                                                                                                                                                                                                            | The switch document now; revisit when dealers are many                                                                                                                                                   |
| D6  | First purpose: selected invoices paid in full — the amount is fully derived, the client sends none. On-account and advance deposit follow (the client proposes an amount; the server bounds it)                                                                                                                                                                                                                                                                                                                                                                                              | As written                                                                                                                                                                                               |
| D7  | Refunds: which dealer scopes may raise one (v4 reads `role`, not `scope`, today), and whether the reversing entry posts when Easebuzz accepts the refund or when it reports it completed                                                                                                                                                                                                                                                                                                                                                                                                     | Needs your call before PG-5                                                                                                                                                                              |
| D8  | The webhook as the second open route (§6.6)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Right after PG-4, once the spec is in hand                                                                                                                                                               |
| D9  | The salt in SSM Parameter Store before go-live (§9)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Yes — a go-live gate                                                                                                                                                                                     |
| D10 | Optional ⚠️: a partial unique index on `voc_msts` `{ dealer_id, pay_mode, chq_no }` where `pay_mode: "ONLINE"` — the database's own no to a duplicate voucher                                                                                                                                                                                                                                                                                                                                                                                                                                | Worth having; not blocking — `settle` is safe without it                                                                                                                                                 |

### Questions for Easebuzz and for ops

| #   | Question                                                                                                                                                                    | Why it matters                   |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| Q1  | What is the API's public hostname, and does Easebuzz register or pin the return URL per merchant?                                                                           | §6, S-8                          |
| Q2  | Can the dashboard APIs (refund, transaction, payout) be restricted to our IPs? We have no static egress today                                                               | T7, E6                           |
| Q3  | Sub-merchant or split settlement — which field(s) does our account use, and does `transaction/v2` echo `sub_merchant_id`?                                                   | S-9, T5                          |
| Q4  | Sandbox captures of all eight calls: content type, response shape, the name of Easebuzz's transaction id                                                                    | §2.4                             |
| Q5  | The full list of `status` values, and how long an `access_key` stays valid                                                                                                  | §7.2                             |
| Q6  | Can the instance security group be closed to everything but the ALB — and is nginx in the path (one hop or two, against `trust proxy: 1`)?                                  | §6.7, E2                         |
| Q7  | TDS: may a customer deduct it on an online payment? Today's voucher has `tds_amt`                                                                                           | How the amount in S-1 is derived |
| Q8  | Can dip-web's DB-Actions page send a superadmin Bearer?                                                                                                                     | D4                               |
| Q9  | How long are `pay_trns` rows kept?                                                                                                                                          | §8.4                             |
| Q10 | The ceiling per payment. [03-payment-gateway-use-case](../../correspondence/IPG_Easebuzz/onboarding/03-payment-gateway-use-case.md) gives an expected range up to ₹5,00,000 | `max_amount_paise`               |
| Q11 | Chargebacks arrive outside these APIs — who records them, and how?                                                                                                          | The refund policy's §7           |

---

## 13. Phases

Every step is a red commit then a green commit (`test(v4/payments): …` then `feat(v4/payments): …`), followed by the mutation smoke with its count in the PR body — the v4 definition of done in `docs/testing.md` §11. `it.todo` never merges. New response shapes get a capture in `test/api_v4/temp/fixtures.captures.js` and a committed fixture.

### PG-0 — Pre-flight (no code)

Answer D1–D6 and Q1–Q6. Get sandbox credentials. Capture all eight calls once and commit them as scrubbed transport fixtures.
**Done when:** §12 has no PENDING row that a later phase depends on, and every call has a fixture.

### PG-1 — Foundations: nothing can move yet ⚠️ approval (`models/pay_trns.js`, `.env.example`, `.env.ci`)

- **Red:** hash vectors for all eight sequences; an array value, a non-string and a `|` in a value are each refused; constant-time compare; `paise ↔ amount-string` round trips, including `"125.5"`, `"125.50"`, `"125"`, and refusals for `"1e3"`, `"12.345"`, `"-1"`; strict `EASEBUZZ_ENV` and the `NODE_ENV` pairing; the transport times out and refuses redirects; the redactor drops `hash` and `key` at any depth; the switch is OFF when its document is absent, unreadable or malformed; the writer refuses a duplicate `sub_merchant_id` and refuses a non-superadmin; legacy `pay_trns` rows still load; conventions — no `axios` or `js-sha512` under `api_v4/`, and `EASEBUZZ_SALT` read in exactly one file.
- **Green:** `lib/easebuzz/*`, `lib/paymentSwitch.js`, the model change, route #1.
- **Mutation smoke:** swap two fields in the reverse sequence → exactly the reverse-hash vectors go red. Make an absent switch document read as ON → exactly the default-OFF tests go red.
- **Done when:** nothing a client can call changes any money state.

### PG-2 — The open router and the return endpoint ⚠️ approval (`api_v4/index.js` contract, `mount.test.js`)

- **Red:** `mount.test.js` — the open list is exactly one route, and every other path still needs a Bearer; an open module with no `guard` throws at boot. The return endpoint — a forged hash writes nothing; a valid hash for an unknown `txnid` writes nothing; amount mismatch; key mismatch; a repeated field; a JSON body is 415; an oversized body is 413; `GET` is refused; the answer is byte-identical for good and bad input and contains no request data; a replayed return adds an event and changes no state; **no outbound call is made** (the fake transport records zero calls); `returned` never makes a voucher; the endpoint still works with the switch OFF.
- **Green:** `open/index.js`, `open/easebuzzReturn.js`.
- **Mutation smoke:** delete the hash check → exactly the forged-return tests go red.

### PG-3 — Initiate, verify, `settle`

- **Red:** one tenancy test per id the body accepts (`companyId`, each of `invoiceIds`) — a dealer you are not related to, an invoice of another pair, an invoice that is not `UNPAID`; `amount` in the body is a `VALIDATION`; the amount sent to Easebuzz equals Σ invoice totals in paise; a second initiate while one is open; switch OFF → `UNAVAILABLE`; the dealer not enabled → `UNAVAILABLE`. `settle` — success creates one voucher and approves it, and **the month bucket equals its documents** (the museum's `bucketTruth` style, recomputed from raw rows, not a status code); the amount differs → `mismatch`, no voucher; the tenant binding differs → `mismatch`; a timeout leaves the state alone; two concurrent `settle` calls → one voucher; death after each step of §7.3 (the fake transport or a stubbed service throws) → the next call finishes the job; invoices paid another way meanwhile → an on-account voucher; one test per caller of `settle`.
- **Green:** `schemas/`, `commands/`, `readmodels/`, `controllers/`, `routes/payments.js`.
- **Mutation smoke:** delete the amount comparison → exactly the tampered-amount tests go red. Delete the state filter from the claim → exactly the concurrency test goes red.

### PG-4 — The sweep and the daily match

- **Red:** an open row older than two minutes is settled with no client call; 24 hours → `expired`; an `expired` row that Easebuzz later calls a success still settles; two sweeps at once claim disjoint rows; the daily match finds success-there-not-here and settles it; success-here-not-there alerts and changes nothing; rows that are not ours are not stored; dates go out as IST `DD-MM-YYYY` whatever the process `TZ` is.
- **Green:** the sweep, `reconcile`, route #5.

### PG-5 — Refunds

Blocked on D7. **Red:** a customer is refused; another dealer is refused; more than `refundable_paise` is refused; two concurrent refunds cannot exceed the capture; a timeout triggers `refund_status` and not a second refund; a definitive rejection returns the reserved amount; the reversing entry makes the ledger equal its documents.

### PG-6 — Later

Payment links (`easy_collect.js`), the web checkout variant (`initiate_payment_iframe.js`), the webhook (D8).

---

## 14. Go-live gate

- [ ] Every ⚠️ item was approved and merged red → green, with its mutation count recorded.
- [ ] Every flow in 04-payment-flow §B was exercised in the sandbox — including a success, a failure, and a payment left pending.
- [ ] The instance security group admits only the ALB (Q6).
- [ ] The salt is in SSM Parameter Store, not in an AMI (D9).
- [ ] The dashboard-API IP restriction is answered (Q2).
- [ ] The return URL is recorded and, if Easebuzz pins it, registered (Q1).
- [ ] The switch document exists with `enabled: false`; the first dealer is turned on alone.
- [ ] The first production payment is a small real one, and its voucher, its month bucket and the next day's settlement report were each checked by a person.
- [ ] `docs/runbook.md` has a "Payments" section: how to switch off, how to read a `mismatch`, how to rotate the salt.

---

## 15. Decision log

| Date       | Item           | Decision                                                                                                                                                                 |
| ---------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-09-17 | Process        | Plan document only — no file changed besides this one (user)                                                                                                             |
| 2026-09-17 | Scope          | Only the files present in the kit folder; Seamless is not among them (user)                                                                                              |
| 2026-09-17 | Storage        | Gateway API responses are stored in the existing `pay_trns` collection (user, asked directly after an ambiguous `pa_trns`)                                               |
| earlier    | Merchant model | VSYST is the master merchant, dealers are sub-merchants, VSYST touches no funds ([02-business-model](../../correspondence/IPG_Easebuzz/onboarding/02-business-model.md)) |
| earlier    | Approval       | On confirmed success the voucher is approved automatically, "exactly as a dealer would today" (04-payment-flow §B step 7)                                                |
| earlier    | Truth          | "No invoice is marked paid until the payment gateway confirms success" (refund policy §5); "confirms with a status check" (04-payment-flow §B step 6)                    |
| earlier    | Refunds        | Raised only by the dealer, to the original instrument, recorded as a reversing entry (04-payment-flow §B)                                                                |
| earlier    | Data held      | No card numbers, bank credentials or UPI PINs (04-payment-flow §C)                                                                                                       |
