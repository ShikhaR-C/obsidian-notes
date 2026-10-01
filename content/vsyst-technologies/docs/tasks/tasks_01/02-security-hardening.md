# Security Hardening

> P0 security fixes. These address real vulnerabilities found in the codebase.
> Ordered by effort (smallest first). Each includes why and what to verify.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Of the seven items, 3 are done (SEC-1, SEC-6, SEC-7), 2 only partly (SEC-2 — the global limiter was removed the day it landed; SEC-4 — validation exists only in v4), 1 is deferred (SEC-3) and 1 is still to do (SEC-5). v4 already works the way these items aim for (bearer on every route, tenant from the token, a house validator, a per-user limiter, scrubbed errors); v3 predates that pattern, and the review adds six v3 tasks — `X-SEC-1`…`X-SEC-4`, `T01-N5` and `T01-N6`, with `X-SEC-2` the most urgent. Security findings are written here at class level only; the specifics are in the review team's private report. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## SEC-1: Fix API key `==` to timing-safe comparison (API)

**Status (2026-10-01):** ✅ done — `3fec109`; one timing-safe comparison in `helpers/middlewares.js`, used by all three key checks. Where the key check applies is `X-SEC-4` below.

**Size:** XS (15 min)
**File:** `helpers/middlewares.js`

**What:** Replace all `==` API key comparisons with `crypto.timingSafeEqual()`.

```js
const crypto = require("crypto");

function timingSafeCompare(a, b) {
  if (typeof a !== "string" || typeof b !== "string") return false;
  if (a.length !== b.length) {
    crypto.timingSafeEqual(Buffer.from(b), Buffer.from(b)); // constant time even on length mismatch
    return false;
  }
  return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
```

Apply to: `api_key_v1()`, `api_key()`, `api_key_v3()`.

**Why:** `==` comparison is vulnerable to timing attacks — an attacker can determine correct characters by measuring response time differences. `crypto.timingSafeEqual` takes the same time regardless of how many characters match.

**How to verify:**

- API: All existing endpoints should work exactly as before (same keys accepted/rejected).
- App: No change needed. App sends the same `x-api-key` header.

**Discussion:** This is a code-quality fix with zero behavior change for legitimate users. The vulnerability is theoretical at your scale, but the fix is trivial and follows Node.js security best practices.

**Why it matters:** The `==` operator compares strings character-by-character and returns `false` as soon as the first mismatch is found. This means comparing `"AAAA"` against `"AXXX"` is faster than comparing against `"AAAX"` — because the first fails at character 2 while the second fails at character 4. An attacker can exploit this by trying keys one character at a time, measuring response times to determine which character is correct, and building up the full key. `crypto.timingSafeEqual` always compares every byte, so the time is constant regardless of how many characters match — no information leaks.

---

## SEC-2: Enable rate limiting (API)

**Status (2026-10-01):** 🟡 partly — only route-level limiters are active (auth, contact form, v4 screens — the last 300 a minute per user, `api_v4/lib/rateLimit.js`); there is no global limiter: the one added in `34dc1ac` was removed the same day by `892c33a`. See `T01-N5`, `X-OPS-1`.

**Size:** XS (15 min — uncomment + configure)
**File:** `dzzlo_oms.js`, auth route files

**What:**

1. Uncomment the existing rate limiter in `dzzlo_oms.js:81-86`
2. Add stricter per-endpoint limits for auth routes

```js
// Global: 100 requests per 15 min per IP
const limiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 });
app.use(limiter);

// Auth: 10 attempts per 15 min per IP
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 10 });
// Apply to login routes
```

**Prerequisite:** QW-6 (`trust proxy`) must be done first, otherwise all requests look like the same IP.

**Why:** Currently, there's nothing stopping brute-force login attacks or API abuse. The package `express-rate-limit` is already installed.

**How to verify:**

- API: Send >100 requests in 15 min from same IP. Requests 101+ should get 429 status.
- App: Normal usage (~650 req/day) is well under limits. No impact.

**Discussion:** Start conservative. You can always increase limits later. The auth limiter (10/15min) protects against password brute-force specifically.

---

## SEC-3: Hash OTPs before storing in DB (API)

**Status (2026-10-01):** ⏸ deferred (the note at the end of this item) and still not done (`models/users.js`, `models/order_msts.js`). It matters more now — see `X-SEC-2`. Guessing is `T01-N5`.

**Size:** S (30 min)
**Files:** `models/users.js`, `api_v3/services/order_msts.js` (order OTP)

**What:** Hash OTP values with SHA-256 before storing. Return plaintext to send via SMS. Compare hashed values on verification.

```js
// Generate
this.OTP_Value = crypto.createHash("sha256").update(otpPlaintext).digest("hex");
return otpPlaintext; // send via SMS

// Verify
const hashedEntry = crypto
  .createHash("sha256")
  .update(enteredOTP)
  .digest("hex");
return hashedEntry === this.OTP_Value;
```

**Why:** OTPs stored as plaintext in MongoDB. Anyone with DB read access (or a NoSQL injection) gets every active OTP. This follows the same pattern already used for `resetPasswordToken`.

**How to verify:**

- API: Login via OTP flow — should work identically from user's perspective.
- App: No change needed. App sends/receives the same OTP values.

**Discussion:** The pattern already exists in the codebase for password reset tokens. We're just applying it consistently to OTPs.

**⚠ Deferred — revisit later.** Currently, the team relies on reading OTPs directly from MongoDB in emergency scenarios (e.g., SMS delivery failure). Hashing OTPs will break this workflow. Before implementing:

1. Ensure the "Resend OTP" flow is solid and covers all failure cases.
2. Set up SMS delivery monitoring/logs (2Factor provider delivery reports) so support can debug without reading OTP values.
3. Once the above are in place, hashing can be safely enabled — if a user doesn't receive the OTP, they resend rather than support reading it from the DB.

---

## SEC-4: Add input validation to critical endpoints (API)

**Status (2026-10-01):** 🟡 partly — v4 has the house validator on every route that takes input (`api_v4/lib/validate.js:424-446`; unknown keys → 400 `VALIDATION`); v3 routes have no schema validation yet, only `sanitizeMongo` (`helpers/sanitizeMongo.js`) and ad-hoc 400s (`b6e8e0a`); `express-validator` is no longer a dependency.

**Size:** S-M (2-4 hours total, but can be done one endpoint at a time)
**Files:** New `helpers/validators.js` or `api_v3/validators/`, route files

**What:** Add validation middleware to the highest-risk endpoints first:

1. `POST /order_msts` (order creation) — validate `cust_id`, `dealer_id`, `products` array
2. Auth routes — validate email format, password length
3. `POST /voc_msts` (voucher creation) — validate amount is positive

**Why:** Currently zero input validation. Invalid ObjectIds crash with confusing 500 errors instead of clear 400s. Negative amounts pass financial calculations. `express-validator` is already installed but unused.

**How to verify:**

- API: Send malformed data (bad ObjectId, negative amount, empty products). Should get 400 with descriptive errors.
- App: Normal requests with valid data work identically. Invalid data gets clear error messages.

**Discussion:** Don't try to validate everything at once. Start with order creation (highest risk, most fields), then expand. Each endpoint validated is an independent improvement.

---

## SEC-5: Restrict CORS origins (API)

**Status (2026-10-01):** ⬜ to do — CORS is still unrestricted (`dzzlo_oms.js`), for every API version including v4.

**Size:** S (30 min)
**File:** `dzzlo_oms.js`

**What:** Replace `app.use(cors())` with configured CORS that allows specific origins.

```js
const corsOptions = {
  origin: function (origin, callback) {
    // Allow requests with no origin (mobile apps, server-to-server)
    if (!origin) return callback(null, true);
    const allowed = [
      process.env.CORS_ORIGIN_1,
      process.env.CORS_ORIGIN_2,
    ].filter(Boolean);
    if (allowed.includes(origin)) callback(null, true);
    else callback(new Error("Not allowed by CORS"));
  },
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: [
    "Content-Type",
    "Authorization",
    "x-api-key",
    "meta",
    "co_id",
  ],
  credentials: true,
};
app.use(cors(corsOptions));
```

**Why:** `cors()` with no arguments allows ALL origins. Any website can make authenticated requests using stolen tokens. React Native apps don't send `Origin` headers, so the `!origin` check lets mobile through.

**How to verify:**

- App: React Native doesn't send Origin headers — unaffected.
- API: Test from a web browser on an unauthorized domain — should be blocked.

**Discussion:** This primarily matters if you ever add a web frontend. But it's good practice now and costs nothing.

---

## SEC-6: Wait for DB before accepting requests (API)

**Status (2026-10-01):** ✅ done — `bb1fe9c`; `defaultConnectionPromise` (`helpers/db_conn.js:50-59`) resolves before `app.listen` (`dzzlo_oms.js:167-178`), and a failed connect exits the process.

**Size:** S (15 min)
**Files:** `helpers/db_conn.js`, `dzzlo_oms.js`

**What:** Export the mongoose connection promise, await it before `app.listen()`.

**Why:** Currently `app.listen()` fires immediately while `mongoose.connect()` runs async. If a request arrives before DB connects, it gets a confusing error. During restarts/deploys, there's a window where the server is up but DB isn't ready.

**How to verify:**

- API: Restart server. First request should work (no race condition).
- App: No change needed.

**Discussion:** This also helps with PM2 cluster mode and ALB health checks — the server only registers as healthy when it can actually serve requests.

---

## SEC-7: Improve logging middleware — stop capturing response bodies (API)

**Status (2026-10-01):** ✅ done — `d5cc10c` dropped the `res.send` capture (size from `content-length`, `exports.getVersionStringFromURL`, `helpers/middlewares.js:233-237`); `ecdd3ae` writes the row only in production (`:220`). Each row still carries the whole user document (`:250`) — API-5 in `X-PERF-2` ([04](./04-api-query-performance.md)).

**Size:** S (30 min)
**File:** `helpers/middlewares.js`

**What:** Remove the `res.send` monkey-patch that captures entire response bodies. Use `res.getHeader('content-length')` instead of `JSON.stringify(responseBody)`.

**Why:** The current logging middleware:

1. Holds every response body in memory until the `finish` event
2. Re-serializes with `JSON.stringify()` — double serialization
3. Writes a DB record per request

This wastes memory and CPU on every single response. The content-length header gives you the size without capturing the body.

**How to verify:**

- API: Logs should still record method, URL, status, response time. Just no longer the full response body.
- App: No change needed.

**Discussion:**

The current middleware monkey-patches `res.send` to capture every response body in a closure variable (`responseBody`), then on `finish` runs `Buffer.byteLength(JSON.stringify(responseBody))` just to record the response size.

Three costs paid on **every single request**:

1. **Memory** — full response body retained until the `finish` event fires.
2. **CPU (double serialization)** — Express already serialized the response once; `JSON.stringify(responseBody)` serializes it a second time just to measure length.
3. **DB write per request** — `Logs.create(...)` fires one insert per request.

The `Content-Length` response header already carries the size Express computed during the real serialization — free.

**Required changes (file: `dzzlo_oms_api/helpers/middlewares.js`, `logging()` function):**

| Line(s) | Change                                                                                                                                             |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 141–146 | **Delete** — remove `var originalSend = res.send;`, `let responseBody;`, and the `res.send = function(body){...}` override.                        |
| 152–154 | **Replace** — use `res.getHeader("content-length")` in place of `Buffer.byteLength(JSON.stringify(responseBody))`.                                 |
| 158     | **Fix** — `this.getVersionStringFromURL(...)` → `exports.getVersionStringFromURL(...)` (latent bug; `this` is `res` inside the `finish` callback). |

**Other files:** No changes needed elsewhere. The `Logs` model schema stays the same — `content_str_length` still receives a number. App clients are unaffected (pure server-side internal change).

**Optional follow-up:** Consider also batching log writes (collect entries, `insertMany` every 5 seconds) to reduce per-request DB writes. But the response body capture removal alone is a significant improvement.

---

## Summary

| Task                          | Size | Urgency | Risk                                 |
| ----------------------------- | ---- | ------- | ------------------------------------ |
| SEC-1: Timing-safe API key    | XS   | P0      | Zero — same behavior                 |
| SEC-2: Enable rate limiting   | XS   | P0      | Low — conservative limits            |
| SEC-3: Hash OTPs              | S    | P0      | Low — same user flow                 |
| SEC-4: Input validation       | S-M  | P1      | Low — adds 400s, doesn't change 200s |
| SEC-5: Restrict CORS          | S    | P1      | Zero — mobile unaffected             |
| SEC-6: DB before listen       | S    | P0      | Zero — correct startup order         |
| SEC-7: Fix logging middleware | S    | P1      | Low — logs are thinner               |

---

## New tasks — from the app v2 / API v4 review (2026-10-01)

**What v4 already does** — the bar for the v3 rows below. Every `/api/v4` route needs a bearer: `api_key_v3` → `protect` → company status → a role gate per module (`api_v4/index.js:72-81`, `api_v4/lib/roles.js`). The tenant comes only from the token (`tenantOf` / `scopeFilter`, `api_v4/lib/tenancy.js:64-102`); request bodies accept no `dealer_id` / `cust_id` (unknown keys → 400); the one body id, Daily Summary's `companyId`, is checked by `assertRelation` before any read, and "not related" and "does not exist" get the same 403 (`api_v4/lib/tenancy.js:121-138`); `/screens/*` has a per-user limiter; an `INTERNAL` error carries no message or stack (`api_v4/lib/errors.js:105-134`). v3 predates this pattern — `X-SEC-1`.

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-SEC-2 | 🆕 **Highest priority.** Superadmin endpoints require a superadmin bearer; every response carries only the fields its caller needs — default projections, secret fields hidden at the model level | Found in this review; the specifics are kept out of this public note. Pairs with SEC-3 (hash OTPs) | API (dip-web's superadmin pages must then send the bearer — web not assessed) | M | — |
| X-SEC-1 | 🆕 Extend the v4 auth + tenant-scoping pattern to the v3 routes — a bearer on every route, the tenant derived from the token, membership checks on any id a request names; v3 predates it | v4 has the pattern (`api_v4/index.js:72-81`, `api_v4/lib/tenancy.js`); the v3 routes and services were written before it (`api_v3/routes/`, `api_v3/services/`); the specifics are in the review team's private report, not in this public note | API | XL | A route-by-route plan and a staged rollout; the app already sends the bearer and `x-co-id` (`src/store/apis/createApi.js:24-47`) |
| X-SEC-3 | 🆕 Outbound SMS-provider calls over TLS, with credentials out of URLs | The 2Factor client predates this (`api_v3/services/order_msts.js`, `api_v3/controllers/auth/SMSOTP/template/index.js`, and the `api_v2` copies) | API | S | Do with `T01-N4` ([07](./07-resilience-ops.md)) |
| X-SEC-4 | 🆕 One API-key middleware, applied the same way on every mount | The key checks predate v4 (`helpers/middlewares.js`, `api_v/`); the specifics are kept out of this public note | API (dip-web callers not assessed) | S | — |
| T01-N5 | 🆕 Brute-force protection for OTP checks — an attempt counter per OTP, a limiter on every route that verifies one, OTPs drawn from a CSPRNG (`crypto.randomInt`) | OTP handling predates these controls (`models/users.js`, `models/order_msts.js`, `api_v3/services/auth.js`, `api_v3/routes/auth/index.js`); unlike SEC-3 this keeps the support workflow of reading an OTP | API | S | `X-OPS-1` ([07](./07-resilience-ops.md)) — IP-keyed limits need the right `trust proxy` hops |
| T01-N6 | 🆕 Pin JWT handling — verify with a fixed algorithm, audience and issuer, and sign tokens with the same claims | Token signing and verification set no audience or issuer and do not pin the algorithm (`models/users.js`, `helpers/auth.js`, `api_v3/auth.js`); the specifics are in the review team's private report | API | S | Accept unpinned tokens until they expire (30-day tokens) or reissue them; fits with tasks_02 `01-token-refresh` |

Related rows elsewhere in this folder: `X-OPS-1` and `T01-N4` in [07](./07-resilience-ops.md); the full list is in [00-overview](./00-overview.md).
