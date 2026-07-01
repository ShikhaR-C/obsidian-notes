# 02 — WebSocket / Socket.io Real-Time Events

> Originally deferred as **Phase 7C** in the learning docs.
> Primary motivator: when a user's company or status changes, every active device of that user should reflect the change **instantly**, not on next screen focus.

---

## TL;DR

Today: when an admin deactivates a user, changes their scope, or blacklists their company, the affected user continues to operate with stale permissions until they pull-to-refresh or the screen remounts. Push notifications via OneSignal cover "delivery-best-effort" cases, but they're not a substitute for a live bidirectional channel and they don't fire while the app is in the foreground.

Target: A Socket.io connection is established right after login, authenticated with the user's JWT. Each connected device joins `user:<userId>` and `company:<companyId>` rooms. When the API mutates a user's status/scope or a company's state, it emits an event to those rooms, and every connected device updates its Redux store in-place. Push notifications remain the fallback for offline devices.

Net effect: the permission/status change propagates to **every active device in < 1 second**, foreground and background, without polling.

---

## 1. Current State (from code research)

### 1.1 API side

| Concern                 | File                                             | Notes                                                                    |
| ----------------------- | ------------------------------------------------ | ------------------------------------------------------------------------ |
| Socket.io installed     | `dzzlo_oms_api/package.json` → `socket.io@4.8.3` | Already in deps, no code using it                                        |
| Socket.io code (legacy) | `helpers/middlewares.js:263-293`                 | **Entire block commented out** — historic attempt on port 8001           |
| Env vars                | `SOCKET_PORT=8031`                               | Defined but unused                                                       |
| Push notifications      | `api_v3/controllers/App/notification.js:1-47`    | OneSignal REST API v1, `include_aliases: {external_id: userIds}`         |
| User status endpoints   | `api_v3/services/users.js:261-345`               | `inActivateUser`, `activateUser`, `removeUser` — today: DB-only, no push |
| User scope update       | `api_v3/services/users.js:92-171` (`updateUser`) | Updates `companies[].scope` — no notification of the change              |
| OTP send                | `api_v3/services/auth.js:212-254`                | OTP created but no device-level event                                    |
| Order create/update     | `api_v3/services/order_msts.js`                  | Already calls OneSignal via helper                                       |

### 1.2 App side

| Concern               | File                                              | Notes                                                                             |
| --------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- |
| Redux auth slice      | `src/store/slices/auth.js`                        | Stores `user`, `company`, `userRole`. No socket reducers.                         |
| User refresh strategy | manual `onRefresh`, `useIsFocused()` in screens   | No polling, no `refetchOnFocus`                                                   |
| socket.io-client      | not in `package.json`                             | Needs install                                                                     |
| OneSignal             | `react-native-onesignal@5.4.1` + native extension | Works for background pushes only                                                  |
| Logout on 401         | `src/utils/API/axiosReqRes.js:91-100`             | Forced logout on 401 — we'll augment this to trigger on `user:removed` events too |

### 1.3 Key observations

1. **Socket.io is already in the API `package.json` but zero code uses it.** This is leftover from an earlier attempt. We're not adding a new dependency — we're activating one.
2. **No device tracking on the User model.** This was also flagged in `01-token-refresh.md`. Both initiatives share the `refreshTokens[]` subschema, which effectively **is** the device list. We reuse it as the source of truth for "which devices should receive events."
3. **OneSignal is the current push layer.** It should stay for offline delivery (app killed, device asleep). Sockets complement it — they handle the foreground/real-time case.
4. **No existing WebSocket infrastructure.** No load balancer sticky sessions, no Redis adapter. For a single-instance PM2 setup (current state), this is fine. Once the API is clustered (`tasks_01/RES-3`), we'll need a Redis adapter or sticky sessions.

---

## 2. Problem Statement

Scenarios that motivate this initiative:

1. **Admin deactivates user B on device X** → user B on device Y continues placing orders for another 30 seconds / 30 minutes / until they close and reopen the app. Customer support tickets result.
2. **Company gets blacklisted** → users of that company continue to see their dashboard with live data until next screen focus, then get confusing 403s mid-session.
3. **Scope changes from `COrder` → `CAdmin`** → user doesn't see their new menu items until they log out and back in.
4. **User gets added to a new sister company** → company switcher dropdown doesn't update.
5. **Order assigned to driver** → driver's "My Orders" screen doesn't update until they pull-to-refresh.
6. **Payment received** → dealer's Accounts screen doesn't reflect the new balance.
7. **OTP sent to a different device** → legitimate user has no way to know someone is trying to log in as them.

Today all of these rely on either (a) the user happening to refocus the right screen, (b) OneSignal push, which is delivery-best-effort and doesn't dispatch to Redux, or (c) nothing at all.

---

## 3. Research & Technical Deep-Dive

### 3.1 Why Socket.io, not raw WebSocket or SSE

| Option                       | Pros                                                                                                                         | Cons                                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Raw `ws` / WebSocket**     | Zero deps, small                                                                                                             | No rooms, no auto-reconnect, no fallback, we'd rebuild Socket.io                            |
| **Server-Sent Events (SSE)** | HTTP-based, proxy-friendly                                                                                                   | One-way (server → client). We may want client → server (typing indicators, presence) later. |
| **Socket.io (chosen)**       | Rooms, auto-reconnect with backoff, auth middleware, already in deps, `socket.io-client` for React Native is well-maintained | Slightly larger bundle, some proxies need WebSocket upgrade enabled                         |

Socket.io is also what the learning doc (Phase 7C) originally called out, and the API already has it installed. The only reason not to use it would be bundle size on the app side — `socket.io-client@4.x` is ~30KB gzipped, which is acceptable for the functionality.

### 3.2 Authentication on the socket

Three common approaches:

1. **Query string token:** `io(url, {query: {token: 'Bearer ...'}})`. Works but tokens end up in access logs.
2. **`auth` object (chosen):** `io(url, {auth: {token: '...'}})`. Socket.io 4.x reserves this for auth. Token is in the handshake, not the URL. Server reads it in a connection middleware.
3. **Cookie-based:** browser-centric, not applicable for React Native.

We'll use option 2. The server-side middleware:

```js
io.use((socket, next) => {
  const token = socket.handshake.auth?.token;
  if (!token) return next(new Error("UNAUTHORIZED"));
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET, {
      clockTolerance: 30, // same verify options as the HTTP middleware
    });
    if (payload.type && payload.type !== "access") {
      return next(new Error("INVALID_TOKEN_TYPE"));
    }
    socket.data.userId = payload.id;
    socket.data.companyId = payload.co_id;
    socket.data.role = payload.role;
    socket.data.tokenExp = payload.exp; // read by the expiry sweep (§3.3)
    next();
  } catch (e) {
    next(new Error("UNAUTHORIZED"));
  }
});
```

Two notes:

- This reads `payload.id` / `payload.co_id` — `01-token-refresh.md` §3.5 deliberately keeps those claim names in the new access token (`getUserFromToken` depends on them too). Extract one shared verify helper for HTTP and socket paths so the options (secret, `clockTolerance`, type check) can't drift.
- Verifying the signature alone trusts a login-time snapshot: a user deactivated after connect keeps a live socket until the expiry sweep catches it. Phase 2 closes that gap with a server-side `disconnectSockets()` on the mutation path (Step 2.7).

### 3.3 Interaction with the refresh token flow (from `01`)

This is the subtle part. With the old 30-day JWT, a socket could stay open for 30 days on one token. With 15-minute access tokens (from `01-token-refresh.md`), the socket's auth token expires mid-session.

**Strategies:**

1. **Re-authenticate on reconnect** — cheap: when the client refreshes its access token (via the HTTP reauth flow), it calls `socket.disconnect()` + `socket.connect()` with the new token. Works but drops in-flight events during the ~200ms reconnect window.

2. **Rolling re-auth on the same socket** — preferred: expose a `socket.emit('auth:refresh', {token: newAccessToken})` event. The server validates and updates `socket.data`. No disconnect, no dropped events.

3. **Server-side token expiry check per-event** — expensive: verify token on every event. Reject if expired. Client catches and triggers HTTP refresh. Overkill.

**Choice:** strategy 2 (rolling re-auth). The client's `tokenStorage.setTokens()` triggers a `socket.emit('auth:refresh', {token})`. If the server says the new token is invalid, the client disconnects cleanly.

The server-side `auth:refresh` handler must (a) verify the JWT with exactly the same options as the connection middleware, (b) **reject any token whose `payload.id !== socket.data.userId`** — the socket's rooms were joined as the original user, so re-auth must never rebind a socket to a different user (ack an error and disconnect instead), and (c) update `socket.data.tokenExp` so the expiry sweep sees the new expiry.

**What if the socket's access token silently expires and the client never notices?** The server has a periodic job (every 1 min) that checks `socket.data.tokenExp`. If expired, it disconnects the socket with reason `TOKEN_EXPIRED`. The client reconnects with a fresh token on the next HTTP refresh cycle.

### 3.4 Rooms and event channels

Socket.io rooms are server-side named groups of sockets. Events emit to a room hit every socket in it.

**Rooms we'll use:**

| Room name                             | Who joins                                             | What's emitted                                                                         |
| ------------------------------------- | ----------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `user:<userId>`                       | Every socket owned by that user (across devices)      | `user:updated`, `user:removed`, `user:scope_changed`, `user:force_logout`              |
| `company:<companyId>`                 | Every socket of every user in that company            | `company:updated`, `company:blacklisted`, `company:user_added`, `company:user_removed` |
| `order:<orderId>`                     | Users watching a specific order (order detail screen) | `order:updated`, `order:status_changed`, `order:processed`                             |
| `dealer:<dealerId>` + `cust:<custId>` | Users with that relation                              | `relation:balance_changed`, `relation:invoice_added`, `relation:payment_received`      |

**Room lifecycle:**

- On connect: auto-join `user:<userId>` and `company:<companyId>`.
- On screen mount (Order Detail): client emits `subscribe` with `{resource: 'order', id: '...'}`. Server joins `order:<id>`. On unmount, `unsubscribe`.
- On company switch (for users with multiple companies): leave old `company:<oldId>`, join `company:<newId>` — after the server verifies from the DB that the user actually belongs to the target company. Never join a room from a client-asserted company id alone.

### 3.5 Event naming convention

Events are namespaced: `<resource>:<action>`.

- `user:updated`, `user:removed`, `user:scope_changed`, `user:force_logout`
- `company:updated`, `company:blacklisted`, `company:user_added`, `company:user_removed`
- `order:created`, `order:updated`, `order:status_changed`, `order:processed`, `order:cancelled`
- `invoice:created`, `invoice:updated`, `invoice:emailed`
- `voucher:created`, `voucher:attached`, `voucher:status_changed`
- `relation:balance_changed`, `relation:first_balance_set`
- `invite:received`, `invite:accepted`, `invite:declined`

**Every event payload has the shape:**

```json
{
  "id": "<resource _id>",
  "at": 1712345678,
  "by": "<actor userId>",
  "data": {
    /* minimal diff, not the full doc */
  }
}
```

Small payloads keep the socket cheap and force the client to decide whether to refetch (via RTK Query invalidation) or patch optimistically.

### 3.6 Client-side: react-native-specific concerns

1. **Background state:** when the app is backgrounded, iOS kills WebSocket connections within ~30 seconds. Android is more lenient but also disconnects under battery saver.
   - **Mitigation:** on `AppState` → `background`, call `socket.disconnect()`. On `AppState` → `active`, reconnect. This is cleaner than relying on Socket.io's built-in reconnect, which can leak state.
2. **Foreground notifications:** when the app is in the foreground and a socket event arrives, we should NOT show an OneSignal notification (it would be duplicate). Use OneSignal's `notificationOpenedHandler` + `inForeground` check.
3. **Reconnect storms:** after a brief network blip, Socket.io reconnects with exponential backoff. Default config is fine; don't tune.

### 3.7 Scaling considerations (not blocking but worth knowing)

- **Single-instance PM2 (current):** Socket.io works out of the box. No Redis adapter needed.
- **PM2 cluster mode (`tasks_01/RES-3`):** Each worker has its own Socket.io instance. A `users.js` controller running on worker 1 can't emit to a socket held by worker 2. **Fix:** add `@socket.io/redis-adapter` + Redis. All workers publish events to Redis, all subscribe. Each emit is fanned out to every worker.
- **Load balancer (AWS ALB):** ALB supports WebSockets natively. Configure sticky sessions (target group cookie) so a client hits the same instance each time. Without sticky sessions, reconnects land on random workers and re-auth works fine, but any server-held per-socket state is lost.

For this initiative, we plan for single-instance. When `tasks_01/RES-3` (cluster) ships, we add the Redis adapter as a follow-up.

---

## 4. Target Architecture

### 4.1 High-level

```
┌────────────────────┐                       ┌──────────────────────┐
│  Mobile Device A   │                       │                      │
│  (iPhone - logged  │◄──── WebSocket ──────►│                      │
│   in as user U)    │                       │                      │
└────────────────────┘                       │                      │
                                              │                      │
┌────────────────────┐                       │   Express + Socket.io │
│  Mobile Device B   │                       │        (PM2)          │
│  (tablet - logged  │◄──── WebSocket ──────►│                      │
│   in as user U)    │                       │                      │
└────────────────────┘                       │   rooms:              │
                                              │   - user:U            │
┌────────────────────┐                       │   - company:C         │
│  Mobile Device C   │                       │                      │
│  (another user V   │◄──── WebSocket ──────►│                      │
│   in company C)    │                       │                      │
└────────────────────┘                       └──────────┬───────────┘
                                                          │
                                         admin endpoint   │  inActivateUser(U)
                                         PUT /users/a/    │
                                         inactivate ──────┘
                                                          │
                                                          ▼
                                              io.to(`user:U`).emit(
                                                'user:removed',
                                                {at, by, reason}
                                              )
                                              →  Device A receives
                                              →  Device B receives
                                              →  Device C does NOT
                                                 (not in user:U room)
```

### 4.2 App-side Redux integration

```
Socket event arrives
      │
      ▼
socketMiddleware (Redux)
      │
      ▼
dispatch corresponding action:
  'user:removed'     → authSlice.forceLogout()
  'user:scope_changed' → authSlice.updateScope() + api.util.invalidateTags([...])
  'order:status_changed' → api.util.invalidateTags([{type: 'order_msts', id}])
  'relation:balance_changed' → api.util.invalidateTags([{type: 'relations', id}])
```

RTK Query's `api.util.invalidateTags()` is the key: it triggers an automatic refetch of any subscribed query matching that tag. The socket becomes a **cache invalidation bus**, not a full data sync layer. That's much simpler and much safer than trying to patch each screen's state in place.

---

## 5. Phased Rollout

### Phase 1 — API: Socket.io bootstrap (connect/disconnect only, no events)

**Goal:** get Socket.io running side-by-side with Express. No business events yet. Verify the connection lifecycle works.

#### Step 1.1 — Create socket module

- New file: `helpers/socket.js`
- Exports: `initSocket(httpServer)`, `getIo()`, `emitToUser(userId, event, payload)`, `emitToCompany(companyId, event, payload)`, `emitToRoom(room, event, payload)`.

#### Step 1.2 — Attach to HTTP server

- File: `dzzlo_oms.js` (entry)
- After `const server = http.createServer(app)`, add `initSocket(server)`.
- Socket.io runs on the **same port** as Express (4.x supports this via HTTP upgrade). Drop the old `SOCKET_PORT=8031` plan.

#### Step 1.3 — CORS for sockets

- Socket.io 4.x has its own CORS config, separate from Express CORS.
- Mirror the Express CORS origins.

#### Step 1.4 — Connection middleware

- Reject connections without a valid JWT in `socket.handshake.auth.token`.
- Log (INFO): `socket connected userId=X deviceId=Y transport=Z`.
- Log (INFO): `socket disconnected userId=X reason=...`.

#### Step 1.5 — Auto-join user and company rooms

- In the `connection` handler: `socket.join(`user:${userId}`)` and `socket.join(`company:${companyId}`)`.

#### Step 1.6 — Health check endpoint

- Extend the existing `/health` endpoint (from `tasks_01/RES-1`) to also report `io.engine.clientsCount`.

**Definition of Done:**

- `curl http://localhost:8030/health` returns `{ ..., sockets: {connected: 0} }`.
- A simple test script using `socket.io-client` can connect with a valid JWT, sees the disconnect log, and the health count increments/decrements.
- Unauthorized connection is rejected with `UNAUTHORIZED` error.
- Existing HTTP routes are unaffected (run the existing Jest suite, all 239 tests should still pass).

---

### Phase 2 — API: Emit `user:*` events on user mutations

**Goal:** the three existing status endpoints now emit socket events.

#### Step 2.1 — `inActivateUser` → `user:removed`

- File: `api_v3/services/users.js:261-286`
- After the DB update, call `emitToUser(targetUserId, 'user:removed', {at: Date.now(), by: req.user._id, companyId})`.
- The event causes the target user's devices to force-logout.
- Do NOT block the HTTP response on the emit — `emit` is synchronous in Socket.io anyway.

#### Step 2.2 — `activateUser` → `user:reactivated`

- File: `api_v3/services/users.js:288-316`
- Emit `user:reactivated`. Client refetches current user.

#### Step 2.3 — `removeUser` → `user:removed`

- File: `api_v3/services/users.js:318-345`
- Emit `user:removed` with reason `REMOVED`.

#### Step 2.4 — `updateUser` → `user:scope_changed`

- File: `api_v3/services/users.js:92-171`
- If `req.body.scope` changed, emit `user:scope_changed` with `{newScope, companyId}`.
- Do not emit on no-op updates (e.g. name change). Diff the fields first.

#### Step 2.5 — Invalidate `getUserFromToken` cache on these mutations

- File: `helpers/auth.js`
- Add `invalidateUserCache(userId)` export.
- Call it from each of the services above so the 3-min cache doesn't serve stale user data.

#### Step 2.6 — `company:user_added` / `company:user_removed`

- When a user joins or leaves a company (e.g. accept invite, be removed), emit to `company:<companyId>` so admins of that company see the list update.

#### Step 2.7 — Server-side enforcement (don't trust the client to log itself out)

`user:removed` / `user:force_logout` are advisory — a tampered client just ignores them and keeps its socket and tokens. On the same mutation path (`inActivateUser`, `removeUser`, company blacklist), after emitting:

1. `revokeAllRefreshTokens(userId)` (helper from `01-token-refresh.md` Phase 1) — stops the refresh flow from minting new access tokens.
2. `invalidateUserCache(userId)` (Step 2.5) — the next HTTP request reloads the now-inactive user and gets rejected, instead of riding the 3-min cache.
3. `io.in('user:<userId>').disconnectSockets(true)` — closes the sockets themselves; any reconnect attempt re-runs the auth middleware against the updated user state.

Residual window: an already-issued access token still verifies cryptographically for up to 15 minutes — accepted in `01-token-refresh.md` §6; steps 1–3 make everything else immediate.

**Definition of Done:**

- API integration test: call `PUT /users/a/inactivate` with a test socket listening on `user:<id>` — assert the event is received.
- Existing tests still pass.
- Graceful degradation: if Socket.io is disabled via a feature flag `SOCKET_IO_ENABLED=false`, the service still works (HTTP response succeeds, emits become no-ops).

---

### Phase 3 — API: Emit `order:*`, `invoice:*`, `voucher:*`, `relation:*`

**Goal:** extend the coverage to all the high-value business events.

This is a batch of small PRs, one per resource. Each follows the same pattern as Phase 2:

1. Identify the service function.
2. After DB write, call `emitToUser` / `emitToCompany` / `emitToRoom`.
3. Invalidate relevant caches.
4. Integration test.

**Events to add:**

| Service file                      | Function              | Event emitted                | Target room                                                |
| --------------------------------- | --------------------- | ---------------------------- | ---------------------------------------------------------- |
| `api_v3/services/order_msts.js`   | `createMstTrn`        | `order:created`              | `user:<custUserId>`, `company:<dealerCoId>`                |
|                                   | `updateOrderStatus`   | `order:status_changed`       | `order:<id>`, `company:<custCoId>`, `company:<dealerCoId>` |
|                                   | `processOrder`        | `order:processed`            | `order:<id>`                                               |
| `api_v3/services/invs.js`         | `addInvs`             | `invoice:created`            | `company:<custCoId>`                                       |
|                                   | `updateInvs`          | `invoice:updated`            | `invoice:<id>`                                             |
| `api_v3/services/voc_msts.js`     | `addVocMsts` variants | `voucher:created`            | `company:<dealerCoId>`, `company:<custCoId>`               |
|                                   | `attachInvoices`      | `voucher:attached`           | `voucher:<id>`, `invoice:<id>`                             |
| `api_v3/services/dealer_custs.js` | `updateFirstBal`      | `relation:first_balance_set` | `company:<dealerCoId>`, `company:<custCoId>`               |
|                                   | `addDealerCust`       | `relation:created`           | both                                                       |
| `api_v3/services/invites.js`      | `addInvite`           | `invite:received`            | `user:<inviteeUserId>`                                     |
|                                   | `acceptInvite`        | `invite:accepted`            | `user:<inviterUserId>`, `company:<companyId>`              |

**Definition of Done:**

- Each emit is covered by at least one integration test.
- Existing push notification (OneSignal) calls remain — both channels fire. OneSignal is for offline/background delivery; sockets are for foreground/real-time.
- Feature flag: `SOCKET_IO_EMIT_<RESOURCE>` per resource so we can disable emits individually if one misbehaves.

---

### Phase 4 — App: Install socket.io-client, set up connection lifecycle

**Goal:** app connects on login, disconnects on logout/background. No event handlers wired yet.

#### Step 4.1 — Install

```bash
cd dzzlo_oms_app
yarn add socket.io-client
cd ios && pod install && cd ..   # no native code, but in case of TurboModule registration
```

`socket.io-client` is pure JS. No native linking needed.

#### Step 4.2 — Create socket service

- New file: `src/services/socket.js`
- Singleton instance. Exports `connectSocket(accessToken)`, `disconnectSocket()`, `getSocket()`, `reauthSocket(newAccessToken)`.
- Uses `io(API_URL_V, {auth: (cb) => cb({token: latestAccessToken()}), transports: ['websocket'], autoConnect: false})`.
  - `transports: ['websocket']` skips long-polling fallback which is unnecessary on mobile.
  - `auth` as a **callback**, not a static object: Socket.io re-invokes it on every reconnect attempt, so reconnects automatically carry the newest access token. A static `{auth: {token}}` freezes the login-time token — after 15 minutes it's expired and every automatic reconnect would be rejected. Keep the latest token mirrored in module memory (`tokenStorage.setTokens` already flows through here per Step 4.5).

#### Step 4.3 — Wire to login/logout

- File: `src/store/slices/auth.js`
- On `fulfilled` of `loginUser` → `connectSocket(accessToken)`.
- On `logoutUser` → `disconnectSocket()`.
- On startup (already-logged-in): `src/screens/StartupScreen.js:18-64` → `connectSocket(accessToken)`.

#### Step 4.4 — Wire to AppState

- File: `src/services/socket.js`
- Register `AppState` listener.
- `background` → disconnect. `active` → reconnect (if authenticated).

#### Step 4.5 — Wire to token refresh

- File: `src/store/apis/tokenStorage.js` (from `01-token-refresh.md` Phase 5)
- After `setTokens({accessToken, ...})`, call `reauthSocket(accessToken)`.
- `reauthSocket`:
  ```js
  socket.emit("auth:refresh", { token: newAccessToken }, (ack) => {
    if (ack?.error) {
      socket.disconnect();
      // will reconnect on next user action via ensureSocket()
    }
  });
  ```

#### Step 4.6 — Connection status indicator (debug only, optional)

- Tiny pulsing dot in dev builds that shows green/red based on `socket.connected`. Helps QA verify the socket is alive. Hidden in release builds.

**Definition of Done:**

- Fresh login → dev console shows `socket connected userId=...`.
- Swipe to background → `socket disconnected reason=io client disconnect`.
- Swipe to foreground → reconnects.
- Logout → disconnects and stays disconnected until next login.
- No event handlers yet, so no business-logic impact.

---

### Phase 5 — App: Socket event middleware dispatching to Redux

**Goal:** translate socket events into RTK Query cache invalidations and Redux actions.

#### Step 5.1 — Create socket middleware

- New file: `src/store/middleware/socketMiddleware.js`
- A Redux middleware that:
  1. On `auth/loginUser/fulfilled`, attaches listeners to the socket for all known events.
  2. On `auth/logoutUser/fulfilled`, removes all listeners.
  3. Each listener dispatches a corresponding Redux action.

#### Step 5.2 — Register middleware

- File: `src/store/index.js` (or wherever the store is configured)
- Add `socketMiddleware` to the middleware chain.

#### Step 5.3 — Handle `user:*` events

| Event                | Handler                                                                         |
| -------------------- | ------------------------------------------------------------------------------- |
| `user:removed`       | dispatch `logoutUser()` with toast: "Your access has been removed by an admin"  |
| `user:reactivated`   | refetch current user: `dispatch(api.endpoints.updateCurr_User_Comp.initiate())` |
| `user:scope_changed` | refetch current user + invalidate `['relations', 'company_users']`              |
| `user:force_logout`  | dispatch `logoutUser()` with toast: "You have been logged out"                  |

Note: `logoutUser()` here calls `POST /auth/logout` with tokens the server has already revoked (Step 2.7) — the thunk must treat a 401 as success and still clear local state (`01-token-refresh.md` Step 5.6).

#### Step 5.4 — Handle `company:*` events

| Event                  | Handler                                                                     |
| ---------------------- | --------------------------------------------------------------------------- |
| `company:updated`      | refetch current user/company                                                |
| `company:blacklisted`  | dispatch `logoutUser()` if the affected company is the user's current one   |
| `company:user_added`   | invalidate `['company_users']` tag                                          |
| `company:user_removed` | invalidate `['company_users']` tag; if it's the current user → force logout |

#### Step 5.5 — Handle `order:*`, `invoice:*`, `voucher:*`

All of these follow the same pattern: invalidate the corresponding RTK Query tag. The existing tag types are already defined (`order_msts`, `voc_msts`, `relations`, etc.).

```js
socket.on("order:status_changed", (payload) => {
  store.dispatch(
    api.util.invalidateTags([
      { type: "order_msts", id: payload.id },
      "order_msts", // also invalidate the list query
    ]),
  );
});
```

#### Step 5.6 — Handle `relation:balance_changed`

- Invalidate `['relations']` tag.
- If the user is currently on the Accounts screen for that relation, the screen will re-fetch automatically (RTK Query subscribed queries re-run on tag invalidation).

**Definition of Done:**

- Manual test: 2 devices logged in as the same user. On device A, change the user's scope via an admin endpoint. Device B's menu updates within 1 second.
- Manual test: 2 devices. Device A creates an order. Device B's order list (if it's showing) updates in < 1 second.
- Manual test: `user:removed` → device logs out with the toast message.
- Airplane mode test: disable network mid-session, re-enable — socket reconnects without losing login state.

---

### Phase 6 — Screen-level subscriptions (order detail, etc.)

**Goal:** for screens watching a specific resource (Order Detail, Invoice Detail), emit `subscribe` on mount and `unsubscribe` on unmount. This scopes server-pushed events to users who actually have the screen open, instead of broadcasting to everyone.

#### Step 6.1 — API-side handlers

- File: `helpers/socket.js`
- Add `socket.on('subscribe', ({resource, id}, ack) => {...})` and `socket.on('unsubscribe', ...)`.
- **Allowlist `resource`** (`order` | `invoice` | `voucher` | `relation`) and build the room name server-side from that allowlist. Never `socket.join()` anything derived from a raw client string — otherwise `subscribe({resource: 'user', id: '<victimUserId>'})` joins another user's `user:` room and silently receives their events.
- Validate the id (`ObjectId.isValid`) and validate that the user has permission to subscribe, **per resource type** — for `order:<id>`, the user is either cust_user_id or dealer_user_id on that order; equivalent ownership checks for invoice, voucher, relation. Ack an error otherwise.
- Cap subscriptions per socket (e.g. 20 rooms) and rate-limit `subscribe` events so a buggy or hostile client can't join unbounded rooms.
- Permissions are re-checked on every re-subscribe after reconnect — access may have been revoked mid-session.

#### Step 6.2 — App-side hook

- New file: `src/hooks/useRealtimeSubscription.js`
- Usage: `useRealtimeSubscription('order', orderId)` → emits subscribe on mount, unsubscribe on unmount.
- Handles reconnect: re-emits subscribe after socket reconnects.

#### Step 6.3 — Wire into detail screens

- `src/screens/Common/_Invoice_/index.js` → `useRealtimeSubscription('invoice', inv._id)`
- Order Detail screens → `useRealtimeSubscription('order', orderId)`
- Accounts (per relation) → `useRealtimeSubscription('relation', relationId)`

**Definition of Done:**

- Subscribe/unsubscribe logs visible in API log when mounting/unmounting detail screens.
- Two devices on the same order detail: one updates status, the other sees the change without pull-to-refresh.

---

### Phase 7 — OneSignal de-duplication

**Goal:** when the app is foregrounded AND a socket event arrives for an action that also sent a push, suppress the OS-level notification (it would be a duplicate).

#### Step 7.1 — App-side OneSignal foreground handler

- Option A — suppress all foreground banners: `OneSignal.Notifications.addEventListener('foregroundWillDisplay', (event) => event.preventDefault())`. One listener, no coordination with the API.
- Option B — selective: the API tags each push with the matching socket event id; the app shows the banner only if no matching socket event arrived in the last few seconds. More precise, but more moving parts.

**Recommendation:** Option A. Suppress all foreground pushes by default and let the socket handle the foreground. If a foreground push turns out to have no socket equivalent, that's a Phase 3 coverage gap — fix it there rather than building Option B's matching machinery.

**Definition of Done:**

- Test: app in foreground, trigger an action that would push → no notification banner. Socket event still dispatches normally.
- App in background → push still appears.

---

### Phase 8 — Monitoring & rollout

#### Step 8.1 — Per-event metrics

- Log counter: `socket.emits.<event_name>` (each emit increments).
- Log counter: `socket.receives.<event_name>` (client-side, optional, via analytics).
- Log gauge: `socket.active_connections` (total sockets in the io namespace).

#### Step 8.2 — Rollout plan

1. Flag: `SOCKET_IO_ENABLED=true` on staging for 1 week.
2. Exercise all screens manually; check the metrics dashboard.
3. Flip on for 10% of production (if you have an A/B flag mechanism; otherwise whole-hog).
4. Monitor for 48 hours: CPU, memory, connection count.
5. Flip on for 100% if healthy.

#### Step 8.3 — Emergency kill switch

- Set `SOCKET_IO_ENABLED=false` and `pm2 restart`. The helper returns early on every emit, and the client-side `connectSocket` is a no-op. Everything gracefully falls back to pull-to-refresh + OneSignal pushes.

---

## 6. Benefits

| Benefit                                         | Before                                  | After                                              |
| ----------------------------------------------- | --------------------------------------- | -------------------------------------------------- |
| Time for status/scope change to propagate       | Until next screen focus (minutes–hours) | < 1 second                                         |
| Foreground order status updates                 | Pull-to-refresh required                | Instant                                            |
| Multi-device coherence (same user)              | No                                      | Yes                                                |
| Blast radius of a "kick this user" admin action | 30-day JWT until it expires             | Immediate force-logout                             |
| Extra HTTP requests per user per hour           | N/A                                     | 1 (socket keeps alive)                             |
| Battery / data cost                             | N/A                                     | Negligible (idle WebSocket)                        |
| Foundation for future features                  | N/A                                     | Typing indicators, presence, live dashboards, chat |

---

## 7. Risks & Rollback

| Risk                                                            | Likelihood            | Impact | Mitigation                                                                                                           |
| --------------------------------------------------------------- | --------------------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| Socket.io consumes too many file descriptors at scale           | Low (single instance) | Medium | Monitor `ulimit`; move to cluster + Redis adapter when approaching 5k conns                                          |
| PM2 cluster mode breaks socket state (from `tasks_01/RES-3`)    | Medium                | High   | Either defer RES-3 until socket Redis adapter is added, OR add adapter first                                         |
| Load balancer drops WebSocket upgrade                           | Low                   | High   | ALB has native WS support. Verify `target group idle timeout > 60s`                                                  |
| Event flood from a buggy loop                                   | Low                   | High   | Rate-limit emits per-user per-second at the emit helper layer                                                        |
| Client subscribes to rooms it shouldn't (cross-user data leak)  | Medium                | High   | Resource allowlist + per-resource authz + subscription cap (Step 6.1)                                                |
| Client-side memory leak from orphaned event listeners           | Medium                | Medium | Always add listeners in middleware (bounded lifetime), not in components                                             |
| Race: socket event arrives before HTTP mutation response        | Medium                | Low    | RTK Query de-dupes concurrent fetches; worst case is one extra fetch                                                 |
| Silent failure: socket disconnects but client thinks it's alive | Medium                | High   | Heartbeat: Socket.io has built-in ping/pong, but verify `pingInterval`/`pingTimeout` are sane (defaults are 25s/20s) |

### Rollback plan

**Level 1 — misbehaving event:** disable the specific resource emit via `SOCKET_IO_EMIT_ORDER=false` env var and restart.

**Level 2 — API perf issue:** set `SOCKET_IO_ENABLED=false` and restart. Client-side `connectSocket()` becomes a no-op. App falls back to pull-to-refresh + OneSignal push.

**Level 3 — app-side crash loop:** ship an app hotfix (CodePush preferred) that gates the entire socket service behind `if (__DEV__ || remoteFlag) { connectSocket(...) }`. Remote flag defaults to off.

---

## 8. Testing Strategy

### 8.1 API tests

- `test/api_v3/socket/auth.test.js`: connect without token → rejected. Connect with expired token → rejected. Connect with valid → joined `user:` and `company:` rooms. `auth:refresh` with a token belonging to a **different user** → rejected + disconnected.
- `test/api_v3/socket/emit.test.js`: for each resource mutation endpoint, assert a socket listener in the relevant room receives the expected event.
- `test/api_v3/socket/subscribe.test.js`: non-allowlisted resource → rejected; order the user isn't a party to → rejected; subscription cap enforced.
- `test/api_v3/socket/enforce.test.js`: `inActivateUser` → target's sockets are disconnected and refresh tokens revoked (Step 2.7).
- Feature-flag test: `SOCKET_IO_ENABLED=false` → emit calls are no-ops, mutation still succeeds.

### 8.2 Manual QA checklist

- [ ] Two devices, same user: scope change propagates in < 1 s
- [ ] Two devices, same user: inactivate → both log out with toast
- [ ] Two devices, same user: new order created on A → order list on B updates
- [ ] Airplane mode: connect, disable wifi, re-enable, reconnects
- [ ] Background: swipe away, open again, reconnects
- [ ] Token refresh mid-session: socket stays connected (rolling re-auth)
- [ ] Kill API process with PM2, restart: app reconnects within 10 s
- [ ] OneSignal: background push still works; foreground does not show banner

---

## 9. Post-launch Monitoring (week 1)

- `socket.active_connections` time series (should roughly match DAU during active hours)
- `socket.emits.<event>` per hour by event type
- `socket.connect.errors` (should be near zero)
- `socket.disconnect.reasons` histogram (transport_close, client_disconnect, ping_timeout)
- API process memory (socket connections hold file handles + small per-conn state — watch for leaks)
- Average event latency (measure on client: time between emit on A and receive on B)

---

## 10. Open Questions

1. **Heartbeat tuning:** Socket.io default is 25s ping, 20s pong timeout. On mobile with spotty 4G, should we relax to 40/30? Decision: start with defaults, tune if disconnect noise is high.
2. **Do we want typing indicators / presence?** Not in this phase. Room for the architecture but not building it.
3. **Should the API emit events on bulk operations (import 1000 rows)?** No — emit one `collection:bulk_updated` instead of 1000 individual events.
4. **Should we emit on every `prod_msts` price change?** Probably yes, since dealers watch this. Add to Phase 3.
5. **Handling admin impersonation (superadmin logs in as another user)?** Out of scope for this phase.
