# Session 11: Session-Based Auth vs JWT

> Phase 6 — Deep Dives | 2 hours | Review: 15 min

## What You'll Learn

- The fundamental difference between stateless (JWT) and stateful (session) authentication
- Why sessions give you immediate revocation and simpler security
- Why JWT is better for mobile apps and multi-server setups
- The hybrid approach (short-lived JWT + server-side refresh tokens) — best of both
- How to implement session auth at scale with Node.js/Express behind ALB

## Why This Matters for DZZLO-OMS

Your current auth has a critical gap: JWT tokens expire in 30 days with **no revocation**. If an employee is fired, their token works for up to 30 days. You can't force logout. You can't kill stolen tokens. This session teaches you the alternatives.

---

## Hour 1 — Concepts (60 min)

### Step 1: JWT vs Session — Head-to-Head Comparison (20 min)

| Aspect                 | JWT (Your Current Setup)                         | Session-Based                                                     |
| ---------------------- | ------------------------------------------------ | ----------------------------------------------------------------- |
| **State**              | Stateless — token contains all info              | Stateful — server stores session data                             |
| **Storage**            | Client stores token (AsyncStorage, localStorage) | Server stores session (DB/Redis), client stores session ID cookie |
| **Revocation**         | **Cannot revoke** until expiry (your problem)    | **Instant** — delete session from store                           |
| **Scalability**        | No server-side storage needed                    | Needs shared session store for multi-server                       |
| **Performance**        | CPU cost (JWT verify on every request)           | Network cost (session lookup from store)                          |
| **Payload size**       | Large (~800 bytes with your payload)             | Small (~32 byte session ID)                                       |
| **Mobile apps**        | Easy — just store and send token                 | Harder — need to handle cookies or custom headers                 |
| **Multi-server**       | Works natively (stateless)                       | Needs shared store (Redis/MongoDB) or sticky sessions             |
| **Security on theft**  | Attacker has full access until expiry            | Attacker has access until session deleted                         |
| **Offline access**     | Token works offline (contains claims)            | Requires server reachability                                      |
| **CSRF vulnerability** | Not vulnerable (token in header)                 | Vulnerable if using cookies (need CSRF token)                     |

### Step 2: Why Sessions Can Be Better (15 min)

**Immediate revocation:**

```
Session: Fire employee → delete session → instant lockout
JWT:     Fire employee → token valid for 30 more days
```

**Server-side control:**

- See all active sessions for a user
- Force logout from all devices
- Track session metadata (IP, device, last active)
- Limit concurrent sessions (e.g., max 3 devices)

**Smaller over-the-wire payload:**

- Session ID: `s%3A...` (~100 bytes in cookie)
- Your JWT: `eyJhbG...` (~800 bytes in Authorization header)
- Every request sends this — adds up on mobile networks

**No token theft risk from client storage:**

- JWT stored in AsyncStorage/localStorage can be extracted
- Session cookie with `httpOnly` flag cannot be read by JavaScript

### Step 3: Why JWT Can Be Better (15 min)

**Stateless — no shared storage needed:**

- Your 2 EC2s behind ALB work with JWT without any shared state
- Sessions need Redis or MongoDB session store shared across servers

**Mobile-first design:**

- React Native handles JWT easily (store in SecureStore, send in header)
- Cookies in React Native are tricky (WebView vs fetch, cross-domain issues)
- Your mobile app already uses JWT — migration has cost

**Microservice-friendly:**

- JWT can be verified by any service without calling the auth server
- Sessions require every service to query the session store

**No CSRF concern:**

- JWT in `Authorization` header is immune to CSRF
- Session cookies need CSRF protection

### Step 4: The Hybrid Approach — Best of Both (10 min)

**Short-lived JWT access token (15 min) + server-side refresh token (30 days):**

```
Login:
  → Server issues: access token (JWT, 15 min) + refresh token (random, stored in DB)
  → Client stores both

API Request:
  → Client sends access token in Authorization header
  → Server verifies JWT (fast, no DB lookup)
  → If expired → client calls /auth/refresh with refresh token

Refresh:
  → Server validates refresh token against DB
  → If valid → issue new access token + rotate refresh token
  → If invalid → force re-login

Revocation:
  → Delete all refresh tokens for user → they can't get new access tokens
  → Existing access tokens expire in ≤15 minutes
  → Maximum exposure: 15 minutes (vs 30 days currently)
```

**This is the recommended approach for DZZLO-OMS** — keeps JWT for mobile compatibility, adds server-side control through refresh tokens.

---

## Hour 2 — Implementation (60 min)

### Step 5: Hybrid Auth Implementation for DZZLO (30 min)

**Refresh Token Model:**

```javascript
// models/refresh_tokens.js
const mongoose = require("mongoose");
const crypto = require("crypto");

const RefreshTokenSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: "users", required: true },
  token: { type: String, required: true, unique: true },
  expiresAt: { type: Date, required: true, index: { expireAfterSeconds: 0 } },
  revoked: { type: Boolean, default: false },
  device: { type: String }, // "iPhone 14", "Chrome Windows"
  ip: { type: String },
  createdAt: { type: Date, default: Date.now },
});

module.exports = mongoose.model("refresh_tokens", RefreshTokenSchema);
```

**Login — issue both tokens:**

```javascript
const crypto = require("crypto");
const RefreshToken = require("../models/refresh_tokens");

async function issueTokenPair(user, req, res) {
  // Short-lived access token (15 min)
  const accessToken = user.getSignedJwtToken(); // Change JWT_EXPIRE to 15m

  // Long-lived refresh token (30 days, opaque, hashed in DB)
  const refreshPlaintext = crypto.randomBytes(40).toString("hex");
  const refreshHashed = crypto
    .createHash("sha256")
    .update(refreshPlaintext)
    .digest("hex");

  await RefreshToken.create({
    user: user._id,
    token: refreshHashed,
    expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
    device: req.headers.meta
      ? JSON.parse(req.headers.meta).deviceBrand
      : "unknown",
    ip: req.ip,
  });

  return { accessToken, refreshToken: refreshPlaintext };
}
```

**Refresh endpoint:**

```javascript
// POST /auth/refresh
exports.refreshToken = asyncHandler(async (req, res, next) => {
  const { refreshToken } = req.body;
  if (!refreshToken) return next(new ErrorResponse("No refresh token", 401));

  const hashed = crypto.createHash("sha256").update(refreshToken).digest("hex");

  const stored = await RefreshToken.findOne({
    token: hashed,
    revoked: false,
    expiresAt: { $gt: new Date() },
  });

  if (!stored)
    return next(new ErrorResponse("Invalid or expired refresh token", 401));

  // Rotate: revoke old, issue new
  stored.revoked = true;
  await stored.save();

  const user = await User.findById(stored.user);
  if (!user) return next(new ErrorResponse("User not found", 401));

  const tokens = await issueTokenPair(user, req, res);
  res.status(200).json({ success: true, ...tokens });
});
```

**Revoke all sessions (fire employee):**

```javascript
await RefreshToken.updateMany({ user: userId }, { revoked: true });
```

### Step 6: Session Auth with express-session (If Going Full Sessions) (15 min)

For the DIP web app (browser-based), sessions may be more appropriate:

```javascript
const session = require("express-session");
const MongoStore = require("connect-mongo");

app.use(
  session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    store: MongoStore.create({
      mongoUrl: process.env.DATABASE_URI,
      collectionName: "sessions",
      ttl: 24 * 60 * 60, // 1 day
    }),
    cookie: {
      secure: true, // HTTPS only
      httpOnly: true, // Can't read from JavaScript
      sameSite: "strict", // CSRF protection
      maxAge: 24 * 60 * 60 * 1000, // 1 day
    },
  }),
);
```

**With Redis (for multi-server):**

```javascript
const RedisStore = require("connect-redis").default;
const redis = require("./helpers/redisClient");

app.use(
  session({
    store: new RedisStore({ client: redis }),
    // ... same options
  }),
);
```

### Step 7: ALB Session Handling (15 min)

**With shared session store (Redis/MongoDB):**

- No sticky sessions needed
- Any server can validate any session
- ALB distributes freely

**Without shared store (in-memory sessions):**

- Need ALB sticky sessions (session affinity)
- AWS Console: Target Group > Attributes > Stickiness > Enable (duration-based, 1 day)
- Not recommended — if a server dies, all its sessions are lost

**Your recommended architecture:**

```
Mobile App (React Native)           Web App (DIP)
    │                                    │
    │ JWT access token                   │ Session cookie
    │ + refresh token                    │ (httpOnly, secure)
    ▼                                    ▼
ALB (no sticky sessions needed)
    │
    ▼
EC2 instances (shared refresh token store in MongoDB)
    │
    ▼
MongoDB Atlas (refresh_tokens collection + sessions collection)
```

---

## 15-Minute Review — Apply to DZZLO-OMS

1. **Decision:** Which approach for the mobile app? (Recommended: hybrid JWT + refresh tokens)
2. **Decision:** Which approach for the DIP web app? (Recommended: express-session + connect-mongo)
3. **Migration plan:** Can you run both old JWT (30-day) and new hybrid (15-min + refresh) simultaneously during transition?
4. **React Native change needed:** Store refresh token in SecureStore, add refresh logic when 401 received
5. **Env change:** `JWT_EXPIRE=30d` → `JWT_EXPIRE=15m`

## Resources

| Resource                 | URL                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------- |
| express-session          | https://www.npmjs.com/package/express-session                                            |
| connect-mongo            | https://www.npmjs.com/package/connect-mongo                                              |
| connect-redis            | https://www.npmjs.com/package/connect-redis                                              |
| OWASP Session Management | https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html       |
| OWASP JWT Cheat Sheet    | https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html  |
| ALB Sticky Sessions      | https://docs.aws.amazon.com/elasticloadbalancing/latest/application/sticky-sessions.html |
