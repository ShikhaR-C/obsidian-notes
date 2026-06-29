# Phase 4: Security Hardening

**Priority:** P0 (4A-4C, 4F) + P2 (4D-4E) | **Timeline:** Week 1-2 + Week 7-8

---

## Research: OWASP Top 10 for APIs (2023)

| #   | Vulnerability                                   | Status in DZZLO OMS                                   |
| --- | ----------------------------------------------- | ----------------------------------------------------- |
| 1   | Broken Object Level Authorization               | Partial -- co_id checks exist but not per-resource    |
| 2   | Broken Authentication                           | Token refresh missing; loose API key comparison       |
| 3   | Broken Object Property Level Authorization      | No input validation; extra fields accepted            |
| 4   | Unrestricted Resource Consumption               | Rate limiting DISABLED                                |
| 5   | Broken Function Level Authorization             | Role checks exist via middleware                      |
| 6   | Unrestricted Access to Sensitive Business Flows | Order creation lacks idempotency                      |
| 7   | Server Side Request Forgery                     | Low risk (no URL params that trigger server requests) |
| 8   | Security Misconfiguration                       | CORS wide open; helmet defaults only                  |
| 9   | Improper Inventory Management                   | v1/v2/v3 API versions all active                      |
| 10  | Unsafe Consumption of APIs                      | 2Factor.in SMS API called without TLS validation      |

---

## Sub-Phase 4A: Enable and Configure Rate Limiting (P0)

### Problem

**File:** `dzzlo_oms.js`, lines 82-86

```js
// const limiter = rateLimit({
//   windowMs: 10 * 60 * 1000,  // 10 minutes
//   max: 100,
// });
// app.use(limiter);
```

Rate limiting is **completely disabled**. The system is vulnerable to:

- Brute force login attacks
- DDoS via order creation spam
- API scraping
- Resource exhaustion

### Proposed Solution: Tiered Rate Limiting

```js
const rateLimit = require("express-rate-limit");

// Tier 1: Global -- all endpoints
const globalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 200, // 200 requests per minute per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many requests. Please try again later." },
  keyGenerator: (req) => {
    // Use X-Forwarded-For behind nginx/load balancer
    return req.headers["x-forwarded-for"]?.split(",")[0] || req.ip;
  },
});

// Tier 2: Auth endpoints -- brute force protection
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // 10 attempts per 15 min
  message: {
    error: "Too many login attempts. Please try again after 15 minutes.",
  },
  skipSuccessfulRequests: true, // only count failures
});

// Tier 3: Write endpoints -- prevent spam
const writeLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 30, // 30 writes per minute
  message: { error: "Write rate limit exceeded." },
});

// Apply in dzzlo_oms.js
app.use(globalLimiter);
// In api_v/api2.js and api3.js:
app.use("/api/v2/auth", authLimiter);
app.use("/api/v3/auth", authLimiter);
// In route files for POST/PUT:
router.post("/", writeLimiter, createHandler);
router.put("/:id", writeLimiter, updateHandler);
```

### For Production with Redis Store (after Phase 2A):

```js
const RedisStore = require("rate-limit-redis");
const { redis } = require("./helpers/cache");

const globalLimiter = rateLimit({
  store: new RedisStore({ sendCommand: (...args) => redis.call(...args) }),
  windowMs: 60 * 1000,
  max: 200,
});
```

**Impact:** Prevents brute force, DDoS, and API abuse.

---

## Sub-Phase 4B: Restrict CORS (P0)

### Problem

**File:** `dzzlo_oms.js`, line 94

```js
app.use(cors()); // Allows ALL origins, ALL methods, ALL headers
```

Any website can make authenticated requests to the API using stolen tokens.

### Proposed Solution

```js
const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = [
      process.env.CORS_ORIGIN_1, // Production web app (if any)
      process.env.CORS_ORIGIN_2, // Staging
    ].filter(Boolean);

    // Allow requests with no origin (mobile apps, curl, server-to-server)
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error("Not allowed by CORS"));
    }
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
  maxAge: 86400, // Cache preflight for 24 hours
};

app.use(cors(corsOptions));
```

**Note:** React Native mobile apps don't send `Origin` headers, so the `!origin` check allows mobile through. This primarily protects against malicious web pages.

---

## Sub-Phase 4C: Per-Endpoint Input Validation (P0)

### Problem

No request body is validated. `express-validator` is imported but unused.

**Example vulnerability** (`api_v3/services/order_msts.js:674`):

```js
const { cust_id, dealer_id, cs_reimb_amt } = body;
// What if cust_id = { "$gt": "" }?  -- NoSQL injection (partially mitigated by mongo-sanitize)
// What if cs_reimb_amt = -999999?    -- Negative amount manipulation
// What if products = []?             -- Empty order created
```

### Proposed Solution: Zod Validation

**Install:**

```bash
yarn add zod
```

**New file:** `api_v3/validators/order_msts.js`

```js
const { z } = require("zod");

const objectId = z.string().regex(/^[a-f\d]{24}$/i, "Invalid ObjectId");

const productSchema = z.object({
  prod_id: objectId,
  quantity: z.number().min(0).optional(),
  is_full_tank: z.boolean().optional(),
  p_ctgy: z.string().optional(),
  rate: z.number().min(0).optional(),
});

exports.createOrderSchema = z.object({
  cust_id: objectId,
  dealer_id: objectId,
  veh_id: objectId,
  dvr_id: objectId.optional(),
  products: z.array(productSchema).min(1, "At least one product required"),
  cs_reimb_amt: z.number().min(0).default(0),
  notify: z.boolean().default(true),
  order_note: z.string().max(500).optional(),
});

exports.updateOrderSchema = z.object({
  products: z.array(productSchema).min(1).optional(),
  cs_reimb_amt: z.number().min(0).optional(),
  order_note: z.string().max(500).optional(),
});

exports.processOrderSchema = z.object({
  _id: objectId,
  cust_id: objectId,
  dealer_id: objectId,
  otp_to: z.enum(["driver", "customer"]).optional(),
});
```

**New file:** `api_v3/validators/validate.js`

```js
/**
 * Express middleware factory for Zod validation
 * @param {z.ZodSchema} schema - Zod schema to validate against
 * @param {"body" | "query" | "params"} source - Request property to validate
 */
exports.validate =
  (schema, source = "body") =>
  (req, res, next) => {
    const result = schema.safeParse(req[source]);
    if (!result.success) {
      const errors = result.error.issues.map((i) => ({
        field: i.path.join("."),
        message: i.message,
      }));
      return res.status(400).json({ success: false, errors });
    }
    req[source] = result.data; // Replace with sanitized data
    next();
  };
```

**Usage in routes:**

```js
// api_v3/routes/collections/order_msts.js
const { validate } = require("../../validators/validate");
const {
  createOrderSchema,
  processOrderSchema,
} = require("../../validators/order_msts");

router.post("/", validate(createOrderSchema), asyncHandler(createOrder));
router.put(
  "/process/:id",
  validate(processOrderSchema),
  asyncHandler(processOrder),
);
```

### Additional Validators to Create

| File                        | Schemas                                          |
| --------------------------- | ------------------------------------------------ |
| `validators/auth.js`        | loginSchema, registerSchema, resetPasswordSchema |
| `validators/users.js`       | createUserSchema, updateUserSchema               |
| `validators/cust_msts.js`   | createCustomerSchema, updateCustomerSchema       |
| `validators/dealer_msts.js` | createDealerSchema, updateDealerSchema           |
| `validators/voc_msts.js`    | createVoucherSchema                              |
| `validators/invs.js`        | createInvoiceSchema                              |

---

## Sub-Phase 4D: Implement Token Refresh (P2)

### Problem

**Current flow:**

1. Login returns JWT with 30-day expiry
2. Token stored in AsyncStorage
3. On 401, app forces full re-login
4. No refresh token mechanism

**Risk:** Long-lived tokens (30 days) are a security risk. If stolen, attacker has 30-day access.

### Proposed Solution: Access + Refresh Token Pattern

#### API Changes

**File:** `models/users.js` -- add refresh token field:

```js
refreshToken: { type: String, select: false },
refreshTokenExpiry: { type: Date, select: false },
```

**New endpoint:** `POST /auth/refresh`

```js
// api_v3/controllers/auth/refresh.js
exports.refreshToken = async (req, res) => {
  const { refreshToken } = req.body;
  if (!refreshToken)
    return res.status(401).json({ error: "Refresh token required" });

  const user = await User.findOne({
    refreshToken,
    refreshTokenExpiry: { $gt: new Date() },
  }).select("+refreshToken +refreshTokenExpiry");

  if (!user)
    return res.status(401).json({ error: "Invalid or expired refresh token" });

  // Generate new tokens
  const accessToken = user.getSignedJwtToken(); // 15-minute expiry
  const newRefreshToken = crypto.randomBytes(40).toString("hex");
  const refreshExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7 days

  // Rotate refresh token (invalidates old one)
  user.refreshToken = newRefreshToken;
  user.refreshTokenExpiry = refreshExpiry;
  await user.save();

  // Invalidate user cache
  await invalidateUserCache(user._id);

  res.status(200).json({
    success: true,
    token: accessToken,
    refreshToken: newRefreshToken,
    expiresIn: 15 * 60, // 15 minutes in seconds
  });
};
```

**Update login endpoint** to return both tokens:

```js
// In loginrx handler
const accessToken = user.getSignedJwtToken(); // Change JWT_EXPIRE to 15m
const refreshToken = crypto.randomBytes(40).toString("hex");
user.refreshToken = refreshToken;
user.refreshTokenExpiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
await user.save();

res.json({
  success: true,
  token: accessToken,
  refreshToken,
  expiresIn: 15 * 60,
  user,
  company,
});
```

#### App Changes

**File:** `src/store/apis/createApi.js` -- add auto-refresh:

```js
import { fetchBaseQuery } from "@reduxjs/toolkit/query/react";
import { Mutex } from "async-mutex";

const mutex = new Mutex();

const baseQuery = fetchBaseQuery({
  baseUrl: API_URL_V,
  prepareHeaders: async (headers) => {
    const userData = await AsyncStorage.getItem("userData");
    const parsed = userData && JSON.parse(userData);
    if (parsed?.token) headers.set("authorization", `Bearer ${parsed.token}`);
    headers.set("x-api-key", X_API_KEY);
    headers.set("meta", JSON.stringify(STATIC_DEVICE_INFO));
    return headers;
  },
  timeout: 10000,
});

const baseQueryWithReauth = async (args, api, extraOptions) => {
  // Wait if refresh is in progress
  await mutex.waitForUnlock();

  let result = await baseQuery(args, api, extraOptions);

  if (result.error && result.error.status === 401) {
    if (!mutex.isLocked()) {
      const release = await mutex.acquire();
      try {
        const userData = await AsyncStorage.getItem("userData");
        const parsed = userData && JSON.parse(userData);

        if (parsed?.refreshToken) {
          const refreshResult = await baseQuery(
            {
              url: "auth/refresh",
              method: "POST",
              body: { refreshToken: parsed.refreshToken },
            },
            api,
            extraOptions,
          );

          if (refreshResult.data) {
            // Store new tokens
            await AsyncStorage.setItem(
              "userData",
              JSON.stringify({
                ...parsed,
                token: refreshResult.data.token,
                refreshToken: refreshResult.data.refreshToken,
                expiryDate: new Date(
                  Date.now() + refreshResult.data.expiresIn * 1000,
                ).toISOString(),
              }),
            );
            // Retry original request
            result = await baseQuery(args, api, extraOptions);
          } else {
            api.dispatch(logoutUser());
          }
        } else {
          api.dispatch(logoutUser());
        }
      } finally {
        release();
      }
    } else {
      await mutex.waitForUnlock();
      result = await baseQuery(args, api, extraOptions);
    }
  }

  return result;
};
```

**Dependencies:**

```bash
# App
yarn add async-mutex
```

---

## Sub-Phase 4E: Secure Token Storage (P2)

### Problem

**File:** `src/store/slices/auth.js`, lines 26-46

```js
await AsyncStorage.setItem('userData', JSON.stringify({ userId, token, ... }));
```

`AsyncStorage` stores data in plain text:

- **Android:** `/data/data/<package>/databases/RKStorage` (SQLite, unencrypted)
- **iOS:** Uses Keychain access by default (more secure)

On rooted Android devices, any app can read AsyncStorage.

### Proposed Solution

**Install:**

```bash
yarn add react-native-keychain
cd ios && pod install
```

**New utility:** `src/utils/Auth/secureStorage.js`

```js
import * as Keychain from "react-native-keychain";
import { Platform } from "react-native";

const SERVICE = "com.dzzlooms.auth";

export const secureStore = {
  async setTokens({ token, refreshToken, expiryDate, userId, userRole }) {
    const data = JSON.stringify({
      token,
      refreshToken,
      expiryDate,
      userId,
      userRole,
    });
    await Keychain.setGenericPassword("authTokens", data, { service: SERVICE });
  },

  async getTokens() {
    const credentials = await Keychain.getGenericPassword({ service: SERVICE });
    if (!credentials) return null;
    return JSON.parse(credentials.password);
  },

  async clearTokens() {
    await Keychain.resetGenericPassword({ service: SERVICE });
  },
};
```

**Migration:** On app startup, check if old AsyncStorage tokens exist, migrate to Keychain, then clear AsyncStorage:

```js
// In StartupScreen or App.js initialization
const migrateTokenStorage = async () => {
  const oldData = await AsyncStorage.getItem("userData");
  if (oldData) {
    const parsed = JSON.parse(oldData);
    await secureStore.setTokens(parsed);
    await AsyncStorage.removeItem("userData");
  }
};
```

---

## Sub-Phase 4F: API Key Security (P0)

### Problem 1: Loose Equality

**File:** `helpers/middlewares.js`, lines 12-14

```js
const match =
  API_KEY_HEADER == process.env.X_API_KEY ||
  API_KEY_HEADER == process.env.X_API_KEY_3;
```

`==` allows type coercion. While unlikely to be exploitable with string-to-string comparison, it's a code quality issue.

### Problem 2: Timing Attack Vulnerability

String comparison with `===` is vulnerable to timing attacks -- an attacker can determine correct characters by measuring response times.

### Proposed Solution

```js
const crypto = require("crypto");

const timingSafeCompare = (a, b) => {
  if (!a || !b) return false;
  const bufA = Buffer.from(a);
  const bufB = Buffer.from(b);
  if (bufA.length !== bufB.length) return false;
  return crypto.timingSafeEqual(bufA, bufB);
};

exports.api_key_v1 = () => (req, res, next) => {
  const isRunLocally = req.headers.host.includes("localhost");
  const API_KEY_HEADER = req.headers["x-api-key"] || "";

  const matchV2 = timingSafeCompare(API_KEY_HEADER, process.env.X_API_KEY);
  const matchV3 = timingSafeCompare(API_KEY_HEADER, process.env.X_API_KEY_3);

  if (!!API_KEY_HEADER && !matchV2 && !matchV3) {
    return res.status(403).json({ error: "Unauthorized access" });
  }

  next();
};
```

### Problem 3: No Key Rotation

**Proposed:** Add a `X_API_KEY_PREV` env var for grace period during rotation:

```js
const keys = [
  process.env.X_API_KEY,
  process.env.X_API_KEY_3,
  process.env.X_API_KEY_PREV,
].filter(Boolean);
const match = keys.some((key) => timingSafeCompare(API_KEY_HEADER, key));
```

---

## Sub-Phase 4G: Fix Logging Middleware (P1)

### Problem

**File:** `helpers/middlewares.js`, lines 128-141

```js
var originalSend = res.send;
let responseBody;
res.send = function (body) {
  responseBody = body;           // Captures ENTIRE response body in memory
  originalSend.apply(res, arguments);
};

res.on("finish", async () => {
  const datalength = responseBody
    ? Buffer.byteLength(JSON.stringify(responseBody))  // Serializes response AGAIN
    : "";
```

Issues:

1. **Memory:** Every response body held in memory until `finish` event
2. **CPU:** `JSON.stringify()` on every response -- double serialization
3. **DB write per request:** `Logs.create()` on line 169

### Proposed Solution

```js
exports.logging = () => async (req, res, next) => {
  const loggedInUser = await getUserFromToken(req.headers);
  const metaData = req.headers.meta ? JSON.parse(req.headers.meta) : null;
  const startHrTime = process.hrtime();

  res.on("finish", () => {
    const elapsedHrTime = process.hrtime(startHrTime);
    const elapsedTimeInMs = elapsedHrTime[0] * 1000 + elapsedHrTime[1] / 1e6;

    // Use Content-Length header instead of serializing response
    const contentLength = res.getHeader("content-length") || 0;

    const logEntry = {
      method: req.method,
      url: req.originalUrl,
      api_v: this.getVersionStringFromURL(req.originalUrl),
      response_time: elapsedTimeInMs,
      status: res.statusCode,
      statusMessage: res.statusMessage,
      content_str_length: contentLength,
      user: loggedInUser
        ? { _id: loggedInUser._id, role: loggedInUser.role }
        : null,
      appInfo: metaData,
      timeIST: new Date(
        new Date().toLocaleString("en-US", { timeZone: "Asia/Kolkata" }),
      ),
    };

    // Buffer logs instead of writing immediately
    logBuffer.push(logEntry);
  });

  next();
};

// Batch write logs every 5 seconds
const logBuffer = [];
setInterval(async () => {
  if (logBuffer.length === 0) return;
  const batch = logBuffer.splice(0, logBuffer.length);
  try {
    if (mongoose.connection.readyState === 1) {
      await Logs.insertMany(batch, { ordered: false });
    }
  } catch (err) {
    console.error("Log batch write failed:", err.message);
  }
}, 5000);
```

**Impact:**

- Eliminates `res.send` monkey-patch (no response body capture)
- Eliminates per-response `JSON.stringify()`
- Reduces MongoDB writes from N/second to 1 batch every 5 seconds
- Log entries are smaller (only user `_id` + `role`, not full user object)

---

## Additional Security Recommendations

### Helmet Configuration Enhancement

```js
// dzzlo_oms.js -- enhance from basic helmet()
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
      },
    },
    hsts: { maxAge: 31536000, includeSubDomains: true },
    referrerPolicy: { policy: "strict-origin-when-cross-origin" },
  }),
);
```

### Add Request Size Limits

```js
app.use(express.json({ limit: "1mb" })); // Prevent large payload attacks
```

### Add Idempotency Keys for Order Creation

```js
// Prevent duplicate orders from network retries
router.post("/", validate(createOrderSchema), async (req, res, next) => {
  const idempotencyKey = req.headers["idempotency-key"];
  if (idempotencyKey) {
    const existing = await redis.get(`idem:${idempotencyKey}`);
    if (existing) return res.status(200).json(JSON.parse(existing));
  }
  // ... create order ...
  if (idempotencyKey) {
    await redis.set(
      `idem:${idempotencyKey}`,
      JSON.stringify(response),
      "EX",
      86400,
    );
  }
});
```

---

## Verification

1. **Rate limiting:** Use `artillery` to send 250 requests in 1 minute; verify 429 responses after 200
2. **CORS:** Test with `fetch()` from unauthorized origin; verify rejection
3. **Validation:** Send malformed bodies; verify 400 with descriptive errors
4. **Token refresh:** Let access token expire; verify automatic refresh
5. **API key:** Verify timing-safe comparison with constant-time measurement
6. **Logging:** Monitor memory usage before/after; verify log batching
7. **OWASP ZAP:** Run automated scan against all endpoints
