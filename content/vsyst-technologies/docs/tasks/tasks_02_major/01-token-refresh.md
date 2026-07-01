# 01 — Token Refresh (Access + Refresh Token Pattern)

> Originally deferred as **Phase 4D** in `docs/learning/api-pattern-problems/phase-4-security-hardening.md`.
> Fixes the "30-day JWT blast radius" problem while preserving the existing OTP-based login UX.

---

## TL;DR

Today: A user logs in via OTP, receives a single JWT that is valid for **30 days**, and stores it in AsyncStorage. If that token leaks, an attacker has a month of unrestricted access. There is no way to revoke a session short of rotating `JWT_SECRET` globally.

Target: A user logs in via OTP, receives a **15-minute access token** plus a **7-day refresh token**. The app silently rotates the access token in the background using `async-mutex` to serialize concurrent refresh attempts, so normal 401s never reach the UI. Refresh tokens are rotated on every use (detected reuse = session kill).

Net effect: stolen access-token exposure window drops from **30 days → 15 minutes**, refresh tokens can be revoked per-device via a DB write, and OTP friction does not increase.

---

## 1. Current State (from code research)

### 1.1 API side

| Concern                 | File                                                           | Notes                                                                              |
| ----------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Active version          | `api_v3` (v2 fallback, v1 disabled)                            | `dzzlo_oms.js:107-117`                                                             |
| JWT signing             | `models/users.js:143-157` (`getSignedJwtToken`)                | Claims: `id, email, username, co_id, role`. Expiry: `process.env.JWT_EXPIRE` (30d) |
| Token issue on login    | `api_v3/controllers/auth/index.js:38-45` (`sendTokenResponse`) | Returns `{success, token, user, company, expiresIn: 30*24*60*60}`                  |
| OTP login flow          | `api_v3/services/auth.js:212-287`                              | Two-step: credential verify → OTP verify → token                                   |
| Token verify middleware | `helpers/auth.js:23-46` (`getUserFromToken`)                   | 3-min in-memory cache by user id                                                   |
| Protect middleware      | `helpers/auth.js:50-64` (`exports.protect`)                    | Reads `req.loggedInUser` set by global logging middleware                          |
| Logout                  | `api_v3/controllers/auth/index.js:6-12`                        | Clears cookie; **does NOT invalidate token server-side**                           |
| User schema             | `models/users.js:54-130`                                       | No `refreshToken`, no `devices`, no `sessions` field                               |

### 1.2 App side

| Concern              | File                                                            | Notes                                                                     |
| -------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Token storage        | `src/store/slices/auth.js:22-33`                                | AsyncStorage key `'userData'`, JSON: `{userId, token, expiryDate, ...}`   |
| RTK Query base       | `src/store/apis/createApi.js:20-37`                             | `prepareHeaders` reads AsyncStorage, sets `Authorization: Bearer <token>` |
| Axios fallback       | `src/utils/API/axiosReqRes.js:9-67` and `index.js:17-24`        | Request interceptor attaches bearer; response interceptor logs out on 401 |
| Smart retry          | `src/store/apis/createApi.js:48-53` (`baseQueryWithSmartRetry`) | 2 retries, exponential up to 8s, **does NOT retry 4xx**                   |
| Login screen         | `src/screens/Login/AuthNavigator/Login.js:124-248`              | Credential-verify → OTP → `logInSlice(result)`                            |
| Logout thunk         | `src/store/slices/auth.js:7-15`                                 | `GET /auth/logout`, removes `userData` and `currentUser`                  |
| Startup expiry check | `src/screens/StartupScreen.js:18-64`                            | Compares stored `expiryDate` → logout if expired                          |

### 1.3 What exists that we can reuse

- OTP flow works end-to-end. Refresh tokens are **added on top** — the OTP login still mints a refresh token the first time.
- The 3-minute `getUserFromToken` cache in `helpers/auth.js` means short access tokens don't hammer MongoDB.
- `baseQueryWithSmartRetry` is already a wrapper around `fetchBaseQuery`, so intercepting 401s to trigger refresh is a small surgical change — no need to swap out the base query entirely.

---

## 2. Problem Statement

1. **Blast radius:** a 30-day JWT that leaks (via logs, device compromise, network MITM on a misconfigured proxy) gives an attacker a full month of access. Industry standard is 5–15 minutes.
2. **No revocation:** the only way to invalidate a stolen token today is rotating `JWT_SECRET`, which logs out **every user on every device simultaneously**. That's unusable as an incident response tool.
3. **No per-device control:** if a user loses a phone, there's no "log out this one device" button — because the API has no concept of a device.
4. **UX regression on expiry:** when a token expires today, the app logs the user out and forces them through the OTP flow again. Short access tokens would make this happen **every 15 minutes** unless we add refresh.
5. **401 cascading:** the current axios interceptor catches a 401 and immediately dispatches `logoutUser()`. If the backend ever briefly returns a 401 under load, every active user is logged out.

Phase 4D calls out the exact same issues (see `phase-4-security-hardening.md:273-434`). The plan below is the implementation.

---

## 3. Research & Technical Deep-Dive

### 3.1 Why access + refresh (and not just "longer JWTs" or "shorter JWTs")

| Option                                       | Pros                                                                                                                                                   | Cons                                                                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| **Just shorten JWT to 15 min**               | Minimal code change                                                                                                                                    | User is re-prompted for OTP every 15 min. Unusable.                                |
| **Stateful sessions (session ID in cookie)** | Trivial revocation                                                                                                                                     | Requires DB/Redis lookup on every request. Breaks the current 3-min JWT cache win. |
| **Long-lived access token + blacklist**      | Keeps JWT stateless                                                                                                                                    | Blacklist grows forever; needs Redis; doesn't solve the leaked-token window.       |
| **Access + refresh (chosen)**                | 15-min access stays stateless (JWT claim check), refresh is stateful only on refresh endpoint. Revocation is per-device. Token rotation detects reuse. | Two tokens, slightly more client complexity.                                       |

The chosen pattern is what Auth0, Okta, Supabase, Firebase Auth, and basically every modern provider ship. It's well-understood, and async-mutex on the client side is a known-good solution to the concurrent-401 race.

### 3.2 Refresh token rotation (detection of reuse)

**Rule:** every time the client presents a refresh token to `/auth/refresh`, the server issues a **new refresh token** and invalidates the old one. If the server ever sees the **old** (invalidated) refresh token presented again, it's evidence that somebody cloned it. Response: **kill all sessions for that user** (not just the offending one), because the honest client and the attacker are racing and the server can't tell who's who.

This is the [OAuth 2.0 refresh token rotation](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics) recommendation (RFC 6819 / BCP for native apps).

**Invalidated ≠ deleted.** Reuse detection only works if the server can still *recognize* a rotated token. If rotation simply removes the entry from `refreshTokens[]`, a replayed old token is indistinguishable from random garbage and the reuse path never fires. So rotation **marks** the old entry (`revokedAt`, `replacedByHash` — see §3.6) and keeps it until its natural 7-day expiry, after which it can be pruned (an expired token fails the expiry check anyway, so retention past that point buys nothing).

**Benign-reuse grace window.** One honest failure mode must not nuke every session: the client calls `/auth/refresh`, the server rotates, and the response is lost (timeout, network drop). Any retry now presents the just-invalidated token. Two defenses, both required: (1) the client never auto-retries the refresh call (Phase 5), and (2) the server treats reuse of a token revoked **< 60 seconds ago** as a soft failure — 401 `TOKEN_EXPIRED`, log a warning, do **not** kill sessions; the client falls back to OTP login. Reuse of a token revoked ≥ 60s ago is treated as hostile: revoke everything, 401 `TOKEN_REUSE`.

**Storage choice:** store refresh tokens hashed with **SHA-256** (not bcrypt) in Mongo, not in plaintext — if the DB leaks, refresh tokens don't. SHA-256 specifically because `/auth/refresh` has no user context and must find the owner via `findOne({'refreshTokens.tokenHash': hash})`; bcrypt's per-hash salt makes that indexed lookup impossible, and its slow-hash protection is pointless for a 384-bit random value (unguessable by construction). Access tokens stay fully stateless (JWT signature is the only check).

### 3.3 Client-side concurrency: async-mutex

**The race:** the app has ~5 RTK Query hooks that fire on mount. The access token expires. All 5 get a 401 at almost the same moment. Without synchronization, all 5 would try to refresh, creating 5 concurrent `/auth/refresh` calls. The first one rotates the refresh token; the other 4 present the now-invalidated refresh token → all 4 trigger the reuse-detection path → all 5 get logged out.

**The fix:** wrap the refresh call in a mutex (`async-mutex` npm package, <3kB, zero native code). First 401 acquires the lock and actually refreshes. The other 4 await the lock; by the time they acquire it, the access token has already been rotated, and they retry their original requests. (Server-side, the 60-second soft-fail window from §3.2 keeps this race from killing sessions — but the four losing requests would still fail without the mutex; the mutex is what makes them succeed.)

```
Request A (401) ────┐
Request B (401) ────┤
Request C (401) ────┼──► acquire(mutex) ──► refresh ──► release(mutex) ──► all retry
Request D (401) ────┤
Request E (401) ────┘
```

This pattern is documented in the official RTK Query docs: ["Automatic Re-authorization by extending fetchBaseQuery"](https://redux-toolkit.js.org/rtk-query/usage/customizing-queries#automatic-re-authorization-by-extending-fetchbasequery) — the Redux team maintains a working snippet using `async-mutex`.

### 3.4 Token storage on the device

AsyncStorage is plaintext on Android (on rooted devices or with backups). For refresh tokens, that's a real risk because a stolen refresh token = 7 days of session-minting.

**Options:**

- Keep using AsyncStorage (easy, current behavior, accepted risk).
- Upgrade to `react-native-keychain` — stores in iOS Keychain + Android EncryptedSharedPreferences.

**Recommendation for this phase:** keep AsyncStorage for the access token, put the refresh token in `react-native-keychain`. The access token is short-lived enough that plaintext storage is acceptable; the refresh token isn't.

If `react-native-keychain` pod install or TurboModules compatibility becomes a blocker, we ship Phase 6 with AsyncStorage first, then add keychain as an optional follow-up (Phase 7).

### 3.5 Token payload design

**Access token (JWT, 15 min):**

```json
{
  "id": "<user_id>",
  "co_id": "<company_id>",
  "role": "dealer|customer|superadmin",
  "scope": "CAdmin|CPrimary|...",
  "type": "access",
  "iat": 1712345678,
  "exp": 1712346578
}
```

Keep the existing claim names (`id`, `co_id`, `role`) — `getUserFromToken` in `helpers/auth.js` does `User.findOne({_id: jwtData.id})`, and the socket auth middleware (`02-websocket-realtime.md` §3.2) reads `payload.id` / `payload.co_id`. Renaming to the standard `sub` would silently break every consumer; add `sub` as a duplicate claim later if standards-compliance matters.

**Refresh token (opaque random, 7 days):**

- Generate with `crypto.randomBytes(48).toString('base64url')` — 64-char URL-safe string.
- Not a JWT. Stateful lookup. Stored hashed in `users.refreshTokens[]`.

**Why not make the refresh token a JWT too?** Because we want revocation on every use. JWTs are stateless by design; making them stateful defeats the purpose.

### 3.6 Multi-device considerations

A user on an iPhone and a tablet needs two independent refresh tokens. We store them as an array on the user document:

```js
// users.js schema addition
refreshTokens: [
  {
    tokenHash: String, // sha256 hash
    deviceId: String, // from react-native-device-info
    deviceName: String, // e.g. "iPhone 14 Pro"
    createdAt: Date,
    lastUsedAt: Date,
    revokedAt: Date, // set on rotation/logout; kept (not deleted) for reuse detection — §3.2
    replacedByHash: String, // successor token's hash — rotation audit trail
    userAgent: String,
    ip: String,
  },
];
```

Max 5 **active** (`revokedAt == null`) refresh tokens per user — evicting the oldest means marking it revoked, not deleting it. Entries older than the 7-day refresh lifetime are pruned on write. This also seeds the device-tracking feature needed by `02-websocket-realtime.md` — both initiatives share the same `devices` concept.

---

## 4. Target Architecture

### 4.1 Login flow (new)

```
App                                       API
 │                                         │
 ├── POST /auth/loginCredentialVerify ────►│
 │      {email, password}                  │
 │◄──────────── 200 OK ────────────────────┤  (OTP sent)
 │                                         │
 ├── POST /auth/loginOTP ──────────────────►│
 │      {email, otp, deviceId, deviceName} │
 │◄──────────── 200 OK ────────────────────┤
 │  { accessToken (15m), refreshToken (7d), user, company, expiresIn: 900 }
 │                                         │
 │  Store accessToken in AsyncStorage      │
 │  Store refreshToken in Keychain         │
```

### 4.2 Refresh flow (new)

```
App                                              API
 │                                                │
 ├── GET /someProtectedEndpoint ─────────────────►│
 │      Authorization: Bearer <expired>           │
 │◄──────────────── 401 ──────────────────────────┤
 │                                                │
 │  acquire mutex                                 │
 │                                                │
 ├── POST /auth/refresh ─────────────────────────►│
 │      {refreshToken, deviceId}                  │
 │                                                │  verify hash matches, not revoked, not expired
 │                                                │  rotate: generate new pair, invalidate old refreshToken,
 │                                                │  append new one to user.refreshTokens[]
 │◄──────────── 200 OK ───────────────────────────┤
 │   { accessToken, refreshToken }                │
 │                                                │
 │  release mutex                                 │
 │                                                │
 ├── GET /someProtectedEndpoint (retry) ─────────►│
 │      Authorization: Bearer <new>               │
 │◄──────────── 200 OK ───────────────────────────┤
```

### 4.3 Reuse detection (attacker presenting invalidated refresh token)

```
Attacker                                          API
 │                                                │
 ├── POST /auth/refresh ─────────────────────────►│
 │      {refreshToken: <already-rotated>}         │
 │                                                │  hash lookup: entry found in user.refreshTokens[]
 │                                                │  with revokedAt set (was rotated earlier)
 │                                                │  ⚠️  REUSE DETECTED
 │                                                │  revoked < 60s ago → 401 TOKEN_EXPIRED only
 │                                                │    (benign lost-response retry — no kill)
 │                                                │  revoked ≥ 60s ago → clear users.refreshTokens[]
 │                                                │    ← logs all devices out; log incident
 │◄──────────── 401 TOKEN_REUSE ──────────────────┤
```

### 4.4 Logout flow (new)

- **Single-device logout (default):** `POST /auth/logout` with the current refresh token body. Server removes that one entry from `user.refreshTokens[]`.
- **All-devices logout:** `POST /auth/logoutAll`. Server clears `user.refreshTokens[]`. Useful after "change password" or "I lost my phone" UI.

---

## 5. Phased Rollout

Each phase is a separate PR. Ship them **in order**, verify staging after each, do not bundle.

### Phase 1 — API: Schema & feature flag (no behavior change)

**Goal:** lay the DB groundwork without changing user-visible behavior. Zero risk.

#### Step 1.1 — Add `refreshTokens[]` to User schema

- File: `models/users.js`
- Add subschema and field (including `revokedAt` and `replacedByHash` — see §3.6). Default `[]`.
- Add Mongoose index on `refreshTokens.tokenHash` (sparse, **non-unique**). A unique multikey index enforces uniqueness across the whole collection, not "per user" — and neither is needed: 48 random bytes make collisions a non-issue. The index exists purely to make `findOne({'refreshTokens.tokenHash': hash})` fast.
- Run migration locally: `db.users.updateMany({}, {$set: {refreshTokens: []}})` — safe because the field is optional.

#### Step 1.2 — Add env vars

- `.env.example` (and all `.env.*` copies):
  ```
  JWT_ACCESS_EXPIRE=15m
  JWT_REFRESH_EXPIRE=7d
  REFRESH_TOKEN_BYTES=48
  MAX_REFRESH_TOKENS_PER_USER=5
  REFRESH_REUSE_GRACE_SECONDS=60   # benign-reuse soft-fail window (§3.2)
  TOKEN_REFRESH_ENABLED=false   # feature flag
  ```
- Keep the existing `JWT_EXPIRE=30d` for now — we'll gate on `TOKEN_REFRESH_ENABLED`.

#### Step 1.3 — Helper module for refresh token CRUD

- New file: `helpers/refreshTokens.js`
- Functions:
  - `generateRefreshToken()` → opaque string
  - `hashRefreshToken(raw)` → sha256 hex
  - `findUserByRefreshToken(raw)` → indexed `findOne({'refreshTokens.tokenHash': hash})`. The refresh endpoint has no authenticated user context — this lookup is its entry point, so it must be an indexed query, never a collection scan.
  - `addRefreshToken(userId, rawToken, deviceMeta)` → pushes to `User.refreshTokens[]`, marks oldest active entry revoked if > 5 active, prunes entries past the 7-day lifetime
  - `verifyRefreshToken(user, rawToken)` → returns the matching entry plus its state: `active | revoked | expired | unknown`
  - `rotateRefreshToken(userId, oldRaw, newRaw, deviceMeta)` → **atomic**: a single `findOneAndUpdate` that matches the old hash *with `revokedAt: null`*, sets `revokedAt` + `replacedByHash` on it, and pushes the new entry. Returns `null` if another request already rotated it — the caller treats that as the reuse path. This is the server-side answer to concurrent refreshes; no server mutex needed.
  - `revokeRefreshToken(userId, rawToken)` → marks one entry revoked
  - `revokeAllRefreshTokens(userId)` → marks every entry revoked

**Definition of Done:**

- Unit tests in `test/api_v3/helpers/refreshTokens.test.js` covering every exported function.
- No changes to any controller. API behavior identical to before.
- `git diff` touches only `models/users.js`, `helpers/refreshTokens.js`, `.env.*`, test files.

---

### Phase 2 — API: `/auth/refresh` and `/auth/logoutAll` endpoints (behind flag)

**Goal:** add the new endpoints. Still gated by `TOKEN_REFRESH_ENABLED=false`. Existing login still issues 30-day JWTs.

#### Step 2.1 — New routes

- File: `api_v3/routes/auth.js` (or wherever auth routes are registered)
  - `POST /api/v3/auth/refresh`
  - `POST /api/v3/auth/logoutAll`

#### Step 2.2 — Controller: `refreshToken`

- File: `api_v3/controllers/auth/refresh.js`
- Accepts `{refreshToken, deviceId}` in body.
- The route is **public** — no `protect` middleware (the caller's access token is expired by definition). Verify the global logging middleware tolerates an absent/expired bearer on this path.
- Steps:
  1. `findUserByRefreshToken(raw)` — indexed hash lookup (Step 1.3), never a scan.
  2. Not found → 401 UNKNOWN_TOKEN.
  3. Found with `revokedAt` set → reuse:
     - revoked **< 60s ago** → 401 TOKEN_EXPIRED, log a warning, sessions untouched (benign lost-response retry — see §3.2).
     - revoked **≥ 60s ago** → `revokeAllRefreshTokens(userId)`, log incident, 401 TOKEN_REUSE.
  4. Found but past the 7-day lifetime → 401 TOKEN_EXPIRED (client falls back to login).
  5. **Account still usable?** User must be active/not removed and the company not blacklisted. If not: `revokeAllRefreshTokens(userId)` and 401. Without this check, a deactivated user keeps minting fresh access tokens for up to 7 days.
  6. Generate new access token and new refresh token.
  7. `rotateRefreshToken(userId, old, new, deviceMeta)` — a `null` return means another request won the race; treat exactly as step 3.
  8. Return `{accessToken, refreshToken, accessExpiresIn: 900}`.
- Rate limit: **not per-IP alone** — mobile carriers CGNAT thousands of users behind one IP, so `10/min per IP` locks out legitimate users. Key primarily on the presented token hash (e.g. 10/min per token), with a much higher per-IP ceiling as a backstop.

#### Step 2.3 — Controller: `logoutAll`

- File: `api_v3/controllers/auth/logout.js`
- Requires access token (uses existing `protect` middleware).
- Calls `revokeAllRefreshTokens(req.user._id)`.
- Also **invalidates the getUserFromToken cache entry** (3-min cache in `helpers/auth.js`) — otherwise a revoked session could linger for up to 3 min.
- The same two calls (`revokeAllRefreshTokens` + cache invalidation) must also fire from account-state mutations — `inActivateUser`, `removeUser`, company blacklist (`api_v3/services/users.js`). Otherwise a deactivated user's device keeps a working refresh token for up to 7 days. `02-websocket-realtime.md` Phase 2 touches the same functions; wire both there.

#### Step 2.4 — Update `sendTokenResponse`

- File: `api_v3/controllers/auth/index.js:38-45`
- When `process.env.TOKEN_REFRESH_ENABLED === 'true'`:
  - Generate access token (15 min) via new method `user.getSignedAccessToken()`
  - Generate refresh token, store hash, return both
  - Response: `{success, token, expiresIn: 30*24*60*60, accessToken, refreshToken, accessExpiresIn: 900, user, company}`
  - **The legacy `token` (30-day JWT) and the legacy `expiresIn` value stay in the flag-on response until Step 6.4.** Old app versions read `token` + `expiresIn`; if `expiresIn` suddenly became `900` they would compute a 15-minute `expiryDate` and `StartupScreen` would force re-login every 15 minutes. The new app reads `accessToken` + `accessExpiresIn` and ignores `token`.
  - Mint and return the refresh pair only when the login request includes a `deviceId` (the new-app signal). Legacy logins without device fields must not fail validation, and there's no point storing refresh tokens a client will discard.
  - Be explicit about the consequence: while the legacy field ships, a captured login response still yields a 30-day token — the blast-radius win only fully lands at Step 6.4 when `token` is dropped.
- Otherwise: existing 30-day `token` behavior.

This dual-mode response lets us ship the API change before the app change. The app won't know what to do with `accessToken`/`refreshToken` yet, so we leave the flag off.

**Definition of Done:**

- Integration tests in `test/api_v3/auth/refresh.test.js`:
  - happy path
  - expired refresh token → 401
  - reused refresh token, revoked ≥ 60s ago → 401 TOKEN_REUSE + all tokens cleared
  - reused refresh token, revoked < 60s ago → 401 TOKEN_EXPIRED, tokens NOT cleared
  - refresh for a deactivated user → 401 + all tokens cleared
  - wrong device id → 401 (optional, defense in depth)
  - concurrent refresh with same token → atomic `rotateRefreshToken` picks one winner; losers hit the soft-fail path
- Flag stays `false` in production env. Staging gets `true` for the next phase.

---

### Phase 3 — API: Wire OTP login to emit both tokens (staging flag on)

**Goal:** on staging with `TOKEN_REFRESH_ENABLED=true`, the login response includes both tokens. Production still off.

#### Step 3.1 — Update OTP verify path

- File: `api_v3/services/auth.js:256-287` (loginOTP)
- On success, call the updated `sendTokenResponse` (which now branches on the flag).

#### Step 3.2 — Update credentialless-verified path

- File: `api_v3/controllers/auth/app_redux.js:12-18` and related "special users" direct login
- Same change.

#### Step 3.3 — Update `protect` middleware to reject non-access tokens

- File: `helpers/auth.js`
- When decoding JWT, reject with 401 only when `payload.type` is **present and not `'access'`**. Legacy 30-day JWTs minted before the flip carry no `type` claim and must keep working until Step 6.4 removes them — a strict `payload.type === 'access'` check would 401 every existing session the moment this deploys.
- Tighten to the strict check as part of Step 6.4, once no legacy tokens can still be in circulation.
- (In our design refresh tokens are opaque, so this is a belt-and-suspenders guard in case a refresh token is ever mistakenly signed as a JWT.)

#### Step 3.4 — Smoke test on staging

- Enable `TOKEN_REFRESH_ENABLED=true` on staging.
- Use Postman/curl to:
  1. Log in, receive both tokens.
  2. Call a protected endpoint with access token — 200.
  3. Wait 16 minutes (or set `JWT_ACCESS_EXPIRE=1m` temporarily and wait 2 min) — access token expired.
  4. Call protected endpoint — 401.
  5. Call `/auth/refresh` — 200 with new tokens.
  6. Call protected endpoint with new access token — 200.
  7. Call `/auth/refresh` again with the **old** refresh token immediately — expect a soft 401 (TOKEN_EXPIRED, sessions intact: you're inside the 60s benign-retry window).
  8. Wait > 60 seconds, call `/auth/refresh` with the old token again — expect 401 TOKEN_REUSE and all sessions cleared.

**Definition of Done:**

- Staging flag on, Postman collection exercised, all 8 steps pass.
- Production flag still off — existing app keeps working because the dual-mode response still includes the old `token` field when the flag is off.

---

### Phase 4 — App: Install `async-mutex` and `react-native-device-info` (if not present)

**Goal:** add dependencies. No runtime behavior change.

#### Step 4.1 — Add packages

```bash
cd dzzlo_oms_app
yarn add async-mutex
# react-native-device-info is already in package.json (15.0.2) per research
```

#### Step 4.2 — iOS pod install

```bash
cd ios && pod install && cd ..
```

No native config needed for `async-mutex` (pure JS).

**Definition of Done:**

- Build succeeds on Android and iOS.
- App runs identically to before.
- `package.json` + `yarn.lock` + `ios/Podfile.lock` are the only changes.

---

### Phase 5 — App: Refactor baseQuery with auto-reauth

**Goal:** the RTK Query base query now transparently refreshes access tokens on 401.

#### Step 5.1 — New helper: token storage abstraction

- New file: `src/store/apis/tokenStorage.js`
- Exports:
  - `getAccessToken()` → reads from AsyncStorage
  - `getRefreshToken()` → reads from AsyncStorage (Phase 7 swaps to Keychain)
  - `getDeviceId()` → uses `react-native-device-info`
  - `setTokens({accessToken, refreshToken})`
  - `clearTokens()`

All RTK + Axios code should go through this helper — no more direct AsyncStorage reads for auth.

#### Step 5.2 — Update `createApi.js` `prepareHeaders`

- File: `src/store/apis/createApi.js:20-37`
- Replace the inline AsyncStorage read with `await getAccessToken()`.

#### Step 5.3 — Add mutex-protected re-auth wrapper

Following the [RTK Query official pattern](https://redux-toolkit.js.org/rtk-query/usage/customizing-queries#automatic-re-authorization-by-extending-fetchbasequery):

```js
// src/store/apis/createApi.js (sketch)
import { Mutex } from "async-mutex";

const mutex = new Mutex();

const baseQueryWithReauth = async (args, api, extraOptions) => {
  await mutex.waitForUnlock();
  let result = await baseQueryWithSmartRetry(args, api, extraOptions);

  if (result.error && result.error.status === 401) {
    if (!mutex.isLocked()) {
      const release = await mutex.acquire();
      try {
        // plain rawBaseQuery, NOT baseQueryWithSmartRetry: if the server
        // rotates the token but the response is lost, an automatic retry
        // would present the just-invalidated token and trip reuse detection
        const refreshResult = await rawBaseQuery(
          {
            url: "/auth/refresh",
            method: "POST",
            body: {
              refreshToken: await getRefreshToken(),
              deviceId: await getDeviceId(),
            },
          },
          api,
          extraOptions,
        );

        if (refreshResult.data?.accessToken) {
          await setTokens(refreshResult.data);
          // retry the original request
          result = await baseQueryWithSmartRetry(args, api, extraOptions);
        } else if ([401, 403].includes(refreshResult.error?.status)) {
          // definitive rejection → hard logout
          api.dispatch(logoutUser());
        }
        // any other failure (5xx, network): keep tokens, surface the original
        // error — the next 401 retries the refresh. Logging out here would
        // recreate the 401-cascade problem this project exists to fix (§2.5)
      } finally {
        release();
      }
    } else {
      // another request is already refreshing; wait then retry
      await mutex.waitForUnlock();
      result = await baseQueryWithSmartRetry(args, api, extraOptions);
    }
  }

  return result;
};
```

- Swap `createApi({baseQuery: baseQueryWithSmartRetry, ...})` → `baseQuery: baseQueryWithReauth`.
- **Never auto-retry the `/auth/refresh` POST** (hence `rawBaseQuery` above — the un-wrapped `fetchBaseQuery` instance). The server's 60-second soft-fail window (§3.2) is the backstop for a lost response, not the primary defense.
- Hard-logout only on a definitive 401/403 from `/auth/refresh` — never on 5xx or network errors (see §7 risk table: backend downtime must not log users out).
- Watch the circular import: `createApi.js` dispatching `logoutUser` from `slices/auth.js` while the slice's consumers import the api. The RTK docs pattern dispatches a plain action type instead; do that (e.g. `api.dispatch({type: 'auth/forceLogout'})`) or lazy-import.

#### Step 5.4 — Update axios interceptor to use the same flow

- File: `src/utils/API/axiosReqRes.js:91-100`
- Instead of logging out on 401, do the same refresh dance. Share the same mutex instance exported from `createApi.js`.
- **Important:** axios and RTK Query must share one mutex, otherwise two concurrent refresh attempts can happen (one from each).

#### Step 5.5 — Update `loginUser` thunk to store both tokens

- File: `src/store/slices/auth.js:17-44`
- Accept `accessToken` and `refreshToken` in the login response, and read `accessExpiresIn` (not the legacy `expiresIn`, which stays at the 30-day value for old clients — Step 2.4).
- Backward compatible: if the response has **only** the old `token` field (flag off in prod), treat it as the access token with long expiry and skip refresh token storage. Refresh flow won't fire because the access token lasts 30 days. When both are present, prefer `accessToken`.

#### Step 5.6 — Update `logoutUser` thunk

- Add a call to `POST /auth/logout` with `{refreshToken}` body so the server can revoke it.
- Best-effort: if the call fails (offline, or the user was already removed server-side → 401), still clear both tokens locally.

#### Step 5.7 — Update the startup expiry check

- File: `src/screens/StartupScreen.js:18-64`
- Today it logs out whenever the stored `expiryDate` has passed. With a 15-minute access token that fires on nearly every cold start — the user would be re-prompted for OTP constantly, defeating the whole design.
- New logic: access token expired **but a refresh token exists** → proceed into the app and let the first API call refresh via the Step 5.3 flow (or refresh eagerly on startup). Log out only when the refresh is definitively rejected (401/403). Offline: keep the session.

**Definition of Done:**

- Manual test on staging (with API flag on):
  - Fresh login works, both tokens stored.
  - Force-expire the access token (Debug menu: "Invalidate access token" → writes a known-bad token to storage).
  - Next API call silently refreshes — no user-visible error, no re-login.
  - Fire 5 parallel queries (e.g. open Accounts screen which fires 3-4 concurrent calls). Inspect network tab: exactly **one** `/auth/refresh` call, followed by retries of the originals.
  - Cold start after > 15 min idle: app stays logged in (Step 5.7 path), no OTP re-prompt.
- Automated test: Jest test for the reauth wrapper using `msw` or a mocked fetch.

---

### Phase 6 — Production rollout

**Goal:** flip the flag on, monitor, keep the old code path as a one-line rollback.

#### Step 6.1 — Deploy API with flag on

- Set `TOKEN_REFRESH_ENABLED=true` in production `.env`.
- `pm2 restart dzzlo-oms`.
- Existing app users continue to work — they still have 30-day JWTs minted before the flip, and the flag only affects **new** logins.

#### Step 6.2 — Ship app update

- Bump versionCode 100 → 101, versionName "1.76" → "1.77".
- Release via Play Store / TestFlight.
- The new app version will receive `accessToken` + `refreshToken` on its next OTP login.
- Older app versions on `TOKEN_REFRESH_ENABLED=true` need the old fields — **verify `sendTokenResponse` still returns the legacy `token` (30-day JWT) and the legacy 30-day `expiresIn` value alongside the new ones** (Step 2.4). If `expiresIn` shrinks to 900, old apps force re-login every 15 minutes.

#### Step 6.3 — Monitor

- Dashboard/logs for the first 72 hours:
  - Count of `/auth/refresh` calls per hour (expected: roughly DAU × (active hours / 0.25))
  - Count of `401 TOKEN_REUSE` responses (expected: ~0, any nonzero is worth investigating)
  - Login success rate (should not drop)
  - 401 rate on protected endpoints (should stay flat — refresh should be invisible to users)

#### Step 6.4 — Drop legacy `token` field (T+30 days)

Once Play Store + TestFlight rollout reaches ~99% adoption (track by `User-Agent` / app version header):

- Remove the `token` field from `sendTokenResponse`.
- Remove the 30-day JWT branch entirely.
- Reduce `MAX_REFRESH_TOKENS_PER_USER` to 3 if telemetry shows users rarely use > 3 devices.

**Definition of Done:**

- Flag on, app shipped, no increase in login-failure rate after 1 week.
- TOKEN_REUSE count is 0 or explained.
- Legacy `token` field removed after adoption threshold hit.

---

### Phase 7 — Optional: Secure refresh token storage (`react-native-keychain`)

**Goal:** move the refresh token out of AsyncStorage into the iOS Keychain / Android EncryptedSharedPreferences.

This is a separate PR because `react-native-keychain` requires pod install and native module verification.

#### Step 7.1 — Install

```bash
yarn add react-native-keychain
cd ios && pod install && cd ..
```

#### Step 7.2 — Update `tokenStorage.js`

- `getRefreshToken` / `setTokens` → use `Keychain.setGenericPassword('refreshToken', value, {service: 'dzzlo_oms'})` and `Keychain.getGenericPassword`.
- Access token stays in AsyncStorage (it's short-lived, less valuable).

#### Step 7.3 — Migration

- On first launch of the keychain-enabled version, migrate any existing refresh token from AsyncStorage → Keychain and delete from AsyncStorage.
- Guard with a migration flag in AsyncStorage so it only runs once.

**Definition of Done:**

- On iOS, verify the value round-trips through `Keychain.getGenericPassword` (debug-menu action) and that the AsyncStorage copy is deleted after migration. (macOS `security find-generic-password` can't inspect an iOS device/simulator keychain, so verify in-app.)
- On Android, refresh token is no longer readable via `adb shell run-as in.vsyst.dzzlooms cat /data/data/.../AsyncStorage`.

---

## 6. Benefits (quantified where possible)

| Benefit                                               | Before                           | After                                                |
| ----------------------------------------------------- | -------------------------------- | ---------------------------------------------------- |
| Stolen access token exposure window                   | 30 days                          | 15 minutes                                           |
| Ability to revoke one user's session                  | No (rotate secret = log out all) | Yes (one DB write)                                   |
| Ability to revoke one device of one user              | No                               | Yes                                                  |
| Reuse-detection → kill session if token cloned        | No                               | Yes (OAuth BCP)                                      |
| Stateless fast path on normal requests                | Yes (JWT + 3m cache)             | Yes (identical)                                      |
| User-visible re-login frequency                       | 1× / 30 days                     | 1× / 7 days                                          |
| Extra DB queries per protected request                | 0 (cached)                       | 0 (cached)                                           |
| Extra DB queries per 15 min (refresh)                 | 0                                | 1 (per device)                                       |
| Cost at 1000 DAU × 8 active hrs / 15 min              | —                                | ~32k refresh calls/day — trivial at Mongo Atlas M10+ |
| Foundation for "sessions" UI (list/revoke per device) | N/A                              | Ready (just needs a screen)                          |

Revocation caveat: revoking refresh tokens does **not** invalidate already-issued access tokens — a killed session can keep calling the API for up to 15 minutes (access TTL) plus up to 3 minutes of `getUserFromToken` cache unless the cache entry is invalidated (Step 2.3). Both windows are part of the accepted design; anything needing instant cutoff is what the force-disconnect in `02-websocket-realtime.md` is for.

---

## 7. Risks & Rollback

| Risk                                                             | Likelihood | Impact | Mitigation                                                                 |
| ---------------------------------------------------------------- | ---------- | ------ | -------------------------------------------------------------------------- |
| Refresh flow has a race → all users logged out                   | Low        | High   | `async-mutex` on client; DB-level atomic rotation on server; staging soak  |
| Lost refresh response → honest retry looks like token reuse      | Low        | High   | Client never auto-retries `/auth/refresh`; server 60s soft-fail window     |
| Clock skew between device and server → access token rejected     | Medium     | Medium | 30-second leeway in JWT verify (`jsonwebtoken` `clockTolerance` option)    |
| Old app (pre-refresh) breaks when flag flips                     | Low        | High   | Dual-mode `sendTokenResponse` keeps the old `token` field for ~30 days     |
| Mongo `refreshTokens[]` array grows unbounded                    | Low        | Medium | Eviction at `MAX_REFRESH_TOKENS_PER_USER`                                  |
| Attacker steals refresh token from AsyncStorage on rooted device | Medium     | High   | Phase 7 moves it to Keychain                                               |
| Refresh endpoint becomes a DDOS vector                           | Low        | Medium | Rate limit keyed on presented token (10/min) + high per-IP ceiling (CGNAT) |
| Backend downtime during refresh → app logs user out              | Low        | High   | `baseQueryWithSmartRetry` already retries 5xx; don't trigger logout on 5xx |

### Rollback plan

**Level 1 — minor issue:** set `TOKEN_REFRESH_ENABLED=false` in API `.env`, `pm2 restart`. Existing refresh tokens continue to work until they expire (7 days), but no new ones are minted. Login returns the old-style 30-day JWT.

**Level 2 — app-side bug:** publish a hotfix via CodePush (if wired up per `tasks_02/05-cicd-github-actions.md` Phase 7) to fall back to the old base query. Users on older app versions are unaffected.

**Level 3 — nuclear:** revert the API commit and `pm2 restart`. The schema additions (`refreshTokens[]`) are additive and don't need to be rolled back.

---

## 8. Testing Strategy

### 8.1 API unit tests

- `test/api_v3/helpers/refreshTokens.test.js`:
  - hashRefreshToken determinism
  - addRefreshToken evicts oldest when at limit
  - verifyRefreshToken returns null for expired / rotated
- `test/api_v3/auth/refresh.test.js`:
  - happy path: issue → refresh → receive new pair
  - expired refresh → 401
  - reused refresh, revoked ≥ 60s ago → 401 TOKEN_REUSE + `refreshTokens[]` cleared
  - reused refresh, revoked < 60s ago → 401 TOKEN_EXPIRED, sessions intact
  - refresh for deactivated user / blacklisted company → 401 + all revoked
  - unknown refresh → 401
  - missing device id → 400
  - concurrent refresh with same raw token (simulate with 5 parallel requests) → exactly one succeeds (atomic rotation); the rest hit the < 60s soft-fail path, sessions intact

### 8.2 App unit tests

- Jest test for `baseQueryWithReauth`:
  - Mock fetch: first call returns 401, refresh call returns 200, original retried → 200
  - 5 parallel 401s → exactly 1 refresh call
  - Refresh fails → `logoutUser` dispatched

### 8.3 Manual QA

- Staging soak: 24h with `JWT_ACCESS_EXPIRE=1m` so refresh happens constantly. Use the app normally; nothing should feel off.
- "Log out everywhere" test: log in on two emulators, call `/auth/logoutAll` via Postman, verify both emulators log out on next request.
- Airplane mode test: turn on airplane mode mid-session, turn off, verify session resumes without re-login.
- Re-install test: fresh install → login → kill app → reopen → still logged in (refresh token retrieved).

---

## 9. Post-launch Monitoring (week 1)

- Log every `/auth/refresh` with `{userId, deviceId, outcome: success|reuse|expired|unknown}`.
- Dashboard panels (CloudWatch or whatever is wired in `tasks_01/08-cloudwatch-setup.md`):
  - Refresh calls / minute
  - Refresh success rate (should be > 99.9%)
  - TOKEN_REUSE count (alert if > 0)
  - Login → first-refresh latency (should be ~15 minutes ±30s)
  - P99 latency of `/auth/refresh` (should be < 200ms)

---

## 10. Open Questions (resolve before Phase 3)

1. **Refresh token in body or cookie?** Body is simpler for mobile. If a future web client needs it, cookies (httpOnly, SameSite=strict) are stronger. Decision: body for now.
2. **Should `/auth/refresh` itself be rate-limited?** Yes — keyed on the presented token hash (10/min per token) with a high per-IP ceiling on top; per-IP alone breaks under carrier CGNAT. Implement via existing `express-rate-limit` with a custom `keyGenerator` (rate limit is re-enabled per `tasks_01/SEC-2`).
3. **Do we invalidate the `getUserFromToken` 3-min cache when a token refreshes?** No — a refresh doesn't change the user document, and the cache is keyed by user id, not by token. Invalidation is required where the *user's state* changes: `logoutAll`, deactivate/remove, scope change (Step 2.3 here and `02-websocket-realtime.md` Step 2.5).
4. **Do we want sliding expiry (refresh extends absolute lifetime) or absolute expiry (7 days hard cap)?** Recommendation: absolute. Sliding lets a stolen refresh token be used forever. Absolute forces re-login every 7 days even on active devices.
5. **Keychain in Phase 6 or Phase 7?** Phase 7 (optional) — keeps Phase 6 rollout focused on the auth flow, not native module debugging.
