# Package Update Plan

**Branch:** `chore/update-packages`
**Created:** 2026-04-06

---

## Phase 1 — Patch/Minor Updates (No Breaking Changes)

These packages have minor or patch updates with stable APIs. Update all at once and run tests.

### 1A. Zero-risk updates (no active usage or CLI-only)

| Package | Current | Target | Notes |
|---------|---------|--------|-------|
| nodemon | ^3.1.0 | ^3.1.14 | CLI-only dev tool, no code imports |
| socket.io | ^4.8.1 | ^4.8.3 | Commented out — not actively used |

**Files to change:** `package.json` only
**Validation:** `yarn install` succeeds, `yarn dev` starts

### 1B. Low-risk middleware updates

| Package | Current | Target | Files Using It |
|---------|---------|--------|----------------|
| cookie-parser | ^1.4.5 | ^1.4.7 | `dzzlo_oms.js`, `test/dzzlo_oms_test.js` |
| cors | ^2.8.5 | ^2.8.6 | `dzzlo_oms.js`, `test/dzzlo_oms_test.js` |
| morgan | ^1.10.0 | ^1.10.1 | `dzzlo_oms.js`, `test/dzzlo_oms_test.js` |
| helmet | ^8.0.0 | ^8.1.0 | `dzzlo_oms.js`, `test/dzzlo_oms_test.js` |

**Files to change:** `package.json` only
**Validation:** `yarn install`, `yarn test`, confirm app starts

### 1C. Low-risk library updates

| Package | Current | Target | Files Using It |
|---------|---------|--------|----------------|
| bcryptjs | ^3.0.0 | ^3.0.3 | `models/users.js` (genSalt, hash, compare) |
| jsonwebtoken | ^9.0.2 | ^9.0.3 | `models/users.js`, `helpers/auth.js` (sign, verify) |
| dotenv | ^17.0.0 | ^17.4.1 | `dzzlo_oms.js` + 40 other files (`.config()`) |
| express | ^5.0.0 | ^5.2.1 | `dzzlo_oms.js` + 30 route files (Router, json, static) |

**Files to change:** `package.json` only
**Validation:** `yarn install`, `yarn test`, confirm login/auth flows work

### 1D. Low-risk ORM and test tool updates

| Package | Current | Target | Files Using It |
|---------|---------|--------|----------------|
| mongoose | ^9.2.0 | ^9.4.1 | `helpers/db_conn.js` + 85 model/controller files |
| supertest | ^7.0.0 | ^7.2.2 | 126+ test files |

**Files to change:** `package.json` only
**Validation:** `yarn install`, full `yarn test` pass

---

## Phase 2 — Dependent Updates (Minor Breaking, Require Code Review)

These are major version bumps but with low actual usage in this codebase.

### 2A. express-rate-limit (^7.2.0 → ^8.3.2)

**Risk:** MODERATE
**Active usage in 2 files:**
- `api_v3/routes/open_apis/contact_email.js` (lines 3-9, 17)
- `api_v2/routes/open_apis/contact_email.js` (lines 3-9, 17)

**Current config pattern:**
```js
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});
```
Also accesses `req.rateLimit` object (line 20).

**Changes required:**
- [ ] Check v8 changelog for `standardHeaders` / `legacyHeaders` option renames
- [ ] Verify `req.rateLimit` object structure is unchanged
- [ ] Update config in `api_v3/routes/open_apis/contact_email.js`
- [ ] Update config in `api_v2/routes/open_apis/contact_email.js`
- [ ] Remove commented-out rate-limit code in `dzzlo_oms.js` (line 78-82) and `test/dzzlo_oms_test.js` (line 53-57) if desired

**Validation:** Hit `/contact_us` endpoint repeatedly, confirm rate limiting works and headers are correct

### 2B. mongodb (^6.6.2 → ^7.1.1)

**Risk:** LOW (despite being a major bump)
**Active usage:** None — only commented-out code in `test/database.js`
**Indirect dependency:** Mongoose uses the MongoDB driver internally

**Changes required:**
- [ ] Verify mongoose ^9.4.1 is compatible with mongodb ^7.x (check mongoose release notes)
- [ ] If compatible: update `package.json` only
- [ ] If NOT compatible: hold this update until mongoose officially supports mongodb 7

**Validation:** Full `yarn test` pass (mongoose operations exercise the driver)

---

## Phase 3 — Major Updates (Breaking Changes, Thorough Testing Needed)

### 3A. nodemailer (^7.0.0 → ^8.0.4) ✅ DONE

**Risk:** MODERATE
**Files directly affected:**
- `helpers/sendEmail.js` — AWS SES transport (`nodemailer.createTransport({ SES: { ses, aws } })`)
- `helpers/sendEmailnaAWS.js` — SMTP transport (`nodemailer.createTransport({ host, port, secure, auth })`)

**Indirectly used in 34+ controller/service files** (all go through the helpers above).

**Changes required:**
- [x] Review nodemailer v8 changelog for transport API changes
- [x] Check if AWS SES transport format (`{ SES: { ses, aws: { SendRawEmailCommand } } }`) is still supported — **NO, legacy format rejected since v7**
- [x] Check if SMTP transport options are unchanged — **yes, unchanged**
- [x] Update `helpers/sendEmail.js` — migrated from `@aws-sdk/client-ses` to `@aws-sdk/client-sesv2` (`SESv2Client` + `SendEmailCommand`)
- [x] `helpers/sendEmailnaAWS.js` — no changes needed (SMTP transport unchanged)
- [ ] Test email sending (invoice, OTP, contact form, password reset)

**Note:** Also replaced `@aws-sdk/client-ses` with `@aws-sdk/client-sesv2` in `package.json` (SES v2 is the newer, recommended API).

**Validation:** Send test emails via both SES and SMTP paths

### 3B. mongodb-memory-server (^9.2.0 → ^11.0.1) ✅ DONE

**Risk:** MODERATE-HIGH (skipping v10 entirely)
**Files directly affected:**
- `test/database.js` (lines 39, 47, 57, 70) — `MongoMemoryServer.create()`, `.getUri()`, `.stop()`

**Indirectly affects:** All 126+ test files (they all use `test/database.js` for setup/teardown)

**Changes required:**
- [x] Review v10 and v11 changelogs for API changes
- [x] Verify `MongoMemoryServer.create()` still works (or find replacement) — **unchanged**
- [x] Verify `.getUri()` method still exists — **unchanged**
- [x] Verify `.stop()` method still exists — **unchanged** (boolean arg removed in v10, but code uses no-arg form)
- [x] Update `test/database.js` if any API changed — **no changes needed**
- [x] Ensure compatible with mongodb ^7.x driver and mongoose ^9.x — **v11 uses mongodb ^7.0.0 internally, fully aligned**

**Note:** v11 requires Node.js >= 20.19.0 (project uses v22.2.0). Default mongod binary changed to 8.2.x.

**Validation:** Full `yarn test` — 29 suites passed, 488 tests passed ✅

### 3C. jest (^29.7.0 → ^30.3.0) ✅ DONE

**Risk:** LOW-MODERATE
**Files directly affected:**
- `jest.config.js` — config: `testEnvironment`, `verbose`, `testPathIgnorePatterns`, `testTimeout`
- 126+ test files using: `describe`, `it`, `beforeAll`, `afterAll`, `expect`, `describe.skip`, `xit`

**Changes required:**
- [x] Review jest v30 changelog for config option changes — **all config options unchanged**
- [x] Verify `testTimeout` and `testPathIgnorePatterns` are still valid — **yes, unchanged**
- [x] Check for any deprecated assertion methods — **none used in codebase** (removed aliases like `.toBeCalled()`, `.toThrowError()` not present)
- [x] Update `jest.config.js` if needed — **no changes needed**
- [x] Fix `jest.setSystemTime(new Date(...))` → `.getTime()` in `test/api_v3/helper/getApplicableRate.test.js` — Jest 30's `@sinonjs/fake-timers` requires numeric timestamps

**Note:** Jest 30 requires Node.js ^18.14 || ^20 || ^22 (project uses v22.2.0). Removed matcher aliases (`.toBeCalled()`, `.toThrowError()`, etc.) not used in codebase.

**Validation:** Full `yarn test` — 29 suites passed, 488 tests passed ✅

---

## Recommended Execution Order

```
Phase 1A  →  Phase 1B  →  Phase 1C  →  Phase 1D
   ↓ (commit after each phase passes tests)
Phase 2B (mongodb — check mongoose compat first)
   ↓
Phase 2A (express-rate-limit — small code changes)
   ↓
Phase 3A (nodemailer — review changelog, update helpers)
   ↓
Phase 3B (mongodb-memory-server — test infra, run full suite)
   ↓
Phase 3C (jest — test runner itself, run full suite last)
```

**After each phase:** run `yarn install && yarn test`, commit if green.
