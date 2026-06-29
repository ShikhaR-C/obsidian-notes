# Resilience Patterns for DZZLO-OMS

> Research document. Covers 12 resilience topics with Node.js/Express/MongoDB implementation details, tailored to the DZZLO-OMS codebase.

---

## Table of Contents

1. [Circuit Breaker Pattern](#1-circuit-breaker-pattern)
2. [Retry with Exponential Backoff](#2-retry-with-exponential-backoff)
3. [Graceful Shutdown](#3-graceful-shutdown)
4. [Database Connection Resilience](#4-database-connection-resilience)
5. [Server Startup Order](#5-server-startup-order)
6. [Fallback Strategies](#6-fallback-strategies)
7. [Deep Health Checks](#7-deep-health-checks)
8. [Dead Letter Queues](#8-dead-letter-queues)
9. [Disk Space Management](#9-disk-space-management)
10. [Zero-Downtime Deploys](#10-zero-downtime-deploys)
11. [Chaos Engineering Basics](#11-chaos-engineering-basics)
12. [Bulkhead Pattern](#12-bulkhead-pattern)

---

## 1. Circuit Breaker Pattern

### Problem it solves

When 2Factor.in SMS, OneSignal push, or AWS SES email services go down, the app currently waits for timeouts on every request, causing cascading slowdowns. There is no mechanism to "stop trying" a dead service.

### Recommended package

- **opossum** v8.x — the de-facto Node.js circuit breaker, maintained by Red Hat/NodeShift
- npm: `npm install opossum@^8.1.4`
- Docs: https://nodeshift.dev/opossum/
- GitHub: https://github.com/nodeshift/opossum

### How a circuit breaker works

```
CLOSED (normal) ──── failures exceed threshold ───→ OPEN (reject immediately)
     ↑                                                    │
     │                                              after timeout
     │                                                    │
     └──── success ──── HALF-OPEN (allow one test call) ←─┘
```

- **Closed**: Requests flow normally. Failures are counted.
- **Open**: Requests are immediately rejected (fail-fast). No network call made.
- **Half-Open**: After a cooldown period, one test request is allowed. If it succeeds, circuit closes. If it fails, circuit re-opens.

### Configuration parameters

| Parameter                  | Meaning                                        | Recommended for DZZLO    |
| -------------------------- | ---------------------------------------------- | ------------------------ |
| `timeout`                  | Max time for a single call (ms)                | 10000 (10s for SMS/push) |
| `errorThresholdPercentage` | % failures to trip circuit                     | 50                       |
| `resetTimeout`             | How long to stay OPEN before trying again (ms) | 30000 (30s)              |
| `rollingCountTimeout`      | Window for counting failures (ms)              | 10000                    |
| `rollingCountBuckets`      | Buckets within the window                      | 10                       |
| `volumeThreshold`          | Min requests before tripping                   | 5                        |

### Implementation for DZZLO-OMS

**New file: `helpers/circuitBreaker.js`**

```js
const CircuitBreaker = require("opossum");

/**
 * Create a circuit breaker wrapping an async function.
 * @param {Function} asyncFn - The async function to protect
 * @param {Object} opts - opossum options override
 * @returns {CircuitBreaker}
 */
function createBreaker(asyncFn, opts = {}) {
  const defaults = {
    timeout: 10000, // 10s before timing out a single call
    errorThresholdPercentage: 50, // open circuit after 50% failures
    resetTimeout: 30000, // try again after 30s
    rollingCountTimeout: 10000, // 10s rolling window
    volumeThreshold: 5, // need at least 5 calls in the window
  };

  const breaker = new CircuitBreaker(asyncFn, { ...defaults, ...opts });

  // Logging — replace with structured logger in production
  breaker.on("open", () =>
    console.warn(`[CIRCUIT OPEN] ${asyncFn.name || "anonymous"}`),
  );
  breaker.on("halfOpen", () =>
    console.info(`[CIRCUIT HALF-OPEN] ${asyncFn.name || "anonymous"}`),
  );
  breaker.on("close", () =>
    console.info(`[CIRCUIT CLOSED] ${asyncFn.name || "anonymous"}`),
  );
  breaker.on("fallback", () =>
    console.info(`[CIRCUIT FALLBACK] ${asyncFn.name || "anonymous"}`),
  );
  breaker.on("timeout", () =>
    console.warn(`[CIRCUIT TIMEOUT] ${asyncFn.name || "anonymous"}`),
  );
  breaker.on("reject", () =>
    console.warn(
      `[CIRCUIT REJECT] ${asyncFn.name || "anonymous"} — circuit is open`,
    ),
  );

  return breaker;
}

module.exports = { createBreaker };
```

**Wrapping OneSignal (modifying `api_v3/controllers/App/notification.js`):**

```js
const fetch = require("node-fetch");
const { createBreaker } = require("../../../helpers/circuitBreaker");

// The raw async function
async function _sendPush({ userIds, jsonData, headingData, contentData }) {
  const headers = {
    accept: "application/json",
    "content-type": "application/json; charset=utf-8",
    Authorization: `Basic ${process.env.ONESIGNAL_REST_API_ID}`,
  };

  const res = await fetch(
    `https://${process.env.ONESIGNAL_HOST}/api/v1/notifications`,
    {
      method: "POST",
      headers,
      body: JSON.stringify({
        app_id: process.env.ONESIGNAL_APP_ID,
        include_aliases: { external_id: userIds },
        target_channel: "push",
        data: jsonData,
        headings: { en: headingData },
        contents: { en: `${contentData}` },
      }),
    },
  );

  if (!res.ok) throw new Error(`OneSignal HTTP ${res.status}`);
  return res.json();
}

// Create circuit breaker for push notifications
const pushBreaker = createBreaker(_sendPush, {
  timeout: 8000,
  resetTimeout: 60000, // OneSignal: wait 60s before retrying
});

// Fallback: log failed notification for later retry (dead letter queue)
pushBreaker.fallback(({ userIds, headingData }) => {
  console.error(
    `[PUSH FALLBACK] Queued for retry — users: ${userIds}, heading: ${headingData}`,
  );
  // TODO: Write to a failed_notifications collection for retry
  return { fallback: true, queued: true };
});

exports.sendNotifyToExternalIDs = async ({
  userIds,
  jsonData,
  headingData,
  contentData,
  notify,
}) => {
  if (!notify) return;
  return pushBreaker.fire({ userIds, jsonData, headingData, contentData });
};
```

**Wrapping 2Factor SMS:**

```js
const { createBreaker } = require("../../../helpers/circuitBreaker");

// Extract the raw SMS-sending logic into an async function
async function _sendSMS({ driver_phone, var1, var2 }) {
  // ... existing http.request logic, but promisified (see Section 2)
}

const smsBreaker = createBreaker(_sendSMS, {
  timeout: 15000, // SMS APIs can be slow
  resetTimeout: 60000,
  errorThresholdPercentage: 40,
});

smsBreaker.fallback(({ driver_phone, var1, var2 }) => {
  console.error(`[SMS FALLBACK] Queued — phone: ${driver_phone}`);
  // Write to failed_sms collection
  return { fallback: true };
});
```

### Monitoring circuit state

opossum exposes a `/stats` stream and a Prometheus-compatible metrics export:

```js
const { PrometheusMetrics } = require("opossum-prometheus");
// npm install opossum-prometheus
const metrics = new PrometheusMetrics({ circuits: [pushBreaker, smsBreaker] });
// Expose via /metrics endpoint for Prometheus/Grafana
```

### Links

- opossum docs: https://nodeshift.dev/opossum/
- opossum GitHub: https://github.com/nodeshift/opossum
- Martin Fowler's circuit breaker article: https://martinfowler.com/bliki/CircuitBreaker.html
- Microsoft's circuit breaker pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/circuit-breaker

---

## 2. Retry with Exponential Backoff

### Problem it solves

Transient failures (network blip, DNS hiccup, MongoDB replica set election) cause immediate errors. Retrying with progressive delays allows recovery without overwhelming the target.

### Recommended packages

- **p-retry** v6.x — Promise-based retry with exponential backoff
  - `npm install p-retry@^6.2.0`
  - Docs: https://github.com/sindresorhus/p-retry
- **async-retry** v1.x — Alternative, callback/promise compatible
  - `npm install async-retry@^1.3.3`
  - Docs: https://github.com/vercel/async-retry

### p-retry vs async-retry comparison

| Feature        | p-retry                       | async-retry    |
| -------------- | ----------------------------- | -------------- |
| ESM-only (v6+) | Yes (v6), CJS available in v5 | No (CJS)       |
| Built on       | p-timeout                     | none           |
| Abort support  | Yes (AbortError)              | Yes (bail)     |
| Used by        | sindresorhus ecosystem        | Vercel/Next.js |

**Recommendation**: Use **async-retry** since DZZLO-OMS uses CommonJS (`require()`). p-retry v6 is ESM-only and would require import() or migrating to ESM.

### Exponential backoff formula

```
delay = min(baseDelay * 2^attempt + jitter, maxDelay)
```

Jitter prevents "thundering herd" where all retries hit at the same time.

### Implementation

**New file: `helpers/retry.js`**

```js
const retry = require("async-retry");

/**
 * Retry an async operation with exponential backoff.
 *
 * @param {Function} fn - Async function to retry. Receives (bail, attemptNumber).
 *                        Call bail(err) to stop retrying for non-transient errors.
 * @param {Object} opts - Override default options
 * @returns {Promise}
 */
async function withRetry(fn, opts = {}) {
  const defaults = {
    retries: 3, // 3 retries = 4 total attempts
    factor: 2, // exponential factor
    minTimeout: 1000, // 1s initial delay
    maxTimeout: 10000, // 10s max delay
    randomize: true, // add jitter
    onRetry: (err, attempt) => {
      console.warn(`[RETRY] Attempt ${attempt} failed: ${err.message}`);
    },
  };

  return retry(fn, { ...defaults, ...opts });
}

module.exports = { withRetry };
```

**Retrying SMS sends:**

```js
const { withRetry } = require("../../../helpers/retry");

exports.sendSMSToDriverPhone = async (
  onResult,
  { driver_phone, var1, var2, notify },
) => {
  if (!notify) return;

  try {
    const result = await withRetry(
      async (bail, attempt) => {
        console.log(`[SMS] Attempt ${attempt} to ${driver_phone}`);
        const response = await sendSMSRaw({ driver_phone, var1, var2 });

        // Don't retry on 4xx errors (bad request, invalid number)
        if (response.status >= 400 && response.status < 500) {
          bail(new Error(`SMS client error: ${response.status}`));
          return;
        }

        if (response.status >= 500) {
          throw new Error(`SMS server error: ${response.status}`);
        }

        return response;
      },
      { retries: 3, minTimeout: 2000, maxTimeout: 15000 },
    );
    onResult(result);
  } catch (err) {
    console.error(
      `[SMS] All retries exhausted for ${driver_phone}:`,
      err.message,
    );
    // Queue to dead letter for manual retry
  }
};
```

**Retrying email sends:**

```js
const { withRetry } = require("./retry");

const sendEmail = async (options) => {
  return withRetry(
    async (bail) => {
      const transporter = nodemailer.createTransport(
        ses({
          /* ... */
        }),
      );
      const info = await transporter.sendMail(message);
      return info;
    },
    {
      retries: 2,
      minTimeout: 3000,
      onRetry: (err, attempt) => {
        console.warn(
          `[EMAIL] Retry ${attempt} for ${options.email}: ${err.message}`,
        );
      },
    },
  );
};
```

### Combining with circuit breaker

The circuit breaker wraps the retry logic (not the other way around). This way, when the circuit is open, retries are not attempted at all:

```
Request → Circuit Breaker → Retry Logic → Actual API Call
          (fail-fast if open)  (retry if transient)
```

```js
const { createBreaker } = require("./circuitBreaker");
const { withRetry } = require("./retry");

async function sendSMSWithRetry(params) {
  return withRetry(
    async () => {
      return await sendSMSRaw(params);
    },
    { retries: 2 },
  );
}

const smsBreaker = createBreaker(sendSMSWithRetry);
```

### Links

- async-retry: https://github.com/vercel/async-retry
- p-retry: https://github.com/sindresorhus/p-retry
- AWS article on exponential backoff: https://docs.aws.amazon.com/general/latest/gr/api-retries.html
- Jitter explanation: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/

---

## 3. Graceful Shutdown

### Problem it solves

Currently, `helpers/db_conn.js` only handles SIGINT. PM2 sends SIGTERM for restarts/reloads. Without proper SIGTERM handling:

- In-flight requests get terminated mid-response
- Database writes can be half-completed
- WebSocket connections (socket.io) drop without warning
- PM2 force-kills the process after timeout

### Current state in DZZLO-OMS

`db_conn.js` has:

```js
process.on("SIGINT", async () => {
  await mongoose.disconnect();
  await db_dip.close();
  process.exit(0);
});
```

Missing: SIGTERM, HTTP server drain, socket.io cleanup, unhandled rejection/exception handlers.

### Implementation

**New file: `helpers/gracefulShutdown.js`**

```js
const mongoose = require("mongoose");

let isShuttingDown = false;

/**
 * Register graceful shutdown handlers.
 * Call this AFTER app.listen() and pass the HTTP server instance.
 *
 * @param {http.Server} server - The HTTP server from app.listen()
 * @param {Object} opts
 * @param {mongoose.Connection[]} opts.connections - Additional mongoose connections to close
 * @param {number} opts.forceTimeout - Force exit after this many ms (default: 15000)
 */
function registerGracefulShutdown(server, opts = {}) {
  const { connections = [], forceTimeout = 15000 } = opts;

  async function shutdown(signal) {
    if (isShuttingDown) return;
    isShuttingDown = true;

    console.log(
      `\n[SHUTDOWN] Received ${signal}. Starting graceful shutdown...`,
    );

    // 1. Force-exit safety net
    const forceTimer = setTimeout(() => {
      console.error("[SHUTDOWN] Forced exit — timeout exceeded");
      process.exit(1);
    }, forceTimeout);
    forceTimer.unref(); // Don't keep process alive just for this timer

    try {
      // 2. Stop accepting new connections
      console.log("[SHUTDOWN] Closing HTTP server (draining connections)...");
      await new Promise((resolve, reject) => {
        server.close((err) => {
          if (err) reject(err);
          else resolve();
        });
      });
      console.log("[SHUTDOWN] HTTP server closed.");

      // 3. Close database connections
      console.log("[SHUTDOWN] Closing MongoDB connections...");
      await mongoose.disconnect();
      for (const conn of connections) {
        await conn.close();
      }
      console.log("[SHUTDOWN] All MongoDB connections closed.");

      // 4. Exit cleanly
      console.log("[SHUTDOWN] Graceful shutdown complete.");
      process.exit(0);
    } catch (err) {
      console.error("[SHUTDOWN] Error during graceful shutdown:", err);
      process.exit(1);
    }
  }

  // Handle both SIGTERM (PM2, Docker, Kubernetes) and SIGINT (Ctrl+C)
  process.on("SIGTERM", () => shutdown("SIGTERM"));
  process.on("SIGINT", () => shutdown("SIGINT"));

  // Catch unhandled errors — log and exit (PM2 will restart)
  process.on("unhandledRejection", (reason, promise) => {
    console.error(
      "[FATAL] Unhandled Rejection at:",
      promise,
      "reason:",
      reason,
    );
    // Don't exit immediately — let the error handler log it
    // But do exit eventually to avoid zombie state
    shutdown("unhandledRejection");
  });

  process.on("uncaughtException", (err) => {
    console.error("[FATAL] Uncaught Exception:", err);
    shutdown("uncaughtException");
  });
}

/**
 * Middleware that returns 503 during shutdown.
 * Mount this BEFORE all routes.
 */
function shutdownGuard() {
  return (req, res, next) => {
    if (isShuttingDown) {
      res.set("Connection", "close");
      return res.status(503).json({
        error: "Server is shutting down",
        retryAfter: 5,
      });
    }
    next();
  };
}

module.exports = { registerGracefulShutdown, shutdownGuard };
```

**Modifying `dzzlo_oms.js`:**

```js
const {
  registerGracefulShutdown,
  shutdownGuard,
} = require("./helpers/gracefulShutdown");
const { db_dip } = require("./helpers/db_conn");

// Mount shutdown guard as the FIRST middleware
app.use(shutdownGuard());

// ... all other middleware and routes ...

const server = app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

// Register graceful shutdown — AFTER app.listen()
registerGracefulShutdown(server, {
  connections: [db_dip],
  forceTimeout: 15000,
});
```

**Remove the SIGINT handler from `db_conn.js`** — it is now centralized in `gracefulShutdown.js`.

### PM2 configuration for graceful shutdown

Update `ecosystem.config.js`:

```js
module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      cwd: __dirname,
      time: true,

      // Graceful shutdown
      kill_timeout: 15000, // Wait 15s for graceful shutdown before SIGKILL
      listen_timeout: 10000, // Wait 10s for app to be "ready" on reload
      shutdown_with_message: false,
      wait_ready: true, // Wait for process.send('ready') before considering "up"

      env: { NODE_ENV: "testing" },
      env_testing: { NODE_ENV: "testing" },
      env_production: { NODE_ENV: "production" },
    },
  ],
};
```

When using `wait_ready: true`, signal PM2 from `dzzlo_oms.js`:

```js
const server = app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  // Tell PM2 we're ready to accept connections
  if (process.send) process.send("ready");
});
```

### Links

- PM2 graceful shutdown: https://pm2.keymetrics.io/docs/usage/signals-clean-restart/
- Node.js `server.close()` docs: https://nodejs.org/api/net.html#serverclosecallback
- Lightship (Kubernetes graceful shutdown): https://github.com/gajus/lightship

---

## 4. Database Connection Resilience

### Problem it solves

Current `db_conn.js` connects once and logs the error, but:

- No automatic reconnection strategy
- No connection pool sizing
- No command buffering control
- No server selection timeout tuning
- If Atlas has a primary election (rolling restart, scaling), the app gets stuck

### Mongoose 9 connection options

Mongoose 9 (which DZZLO-OMS uses) is built on the MongoDB Node.js Driver v6. Key options:

```js
mongoose.connect(databaseURI, {
  // -- Connection Pool --
  maxPoolSize: 10, // Max connections in the pool (default: 100, 10 is fine for single PM2 instance)
  minPoolSize: 2, // Keep 2 connections warm
  maxIdleTimeMS: 30000, // Close idle connections after 30s

  // -- Timeouts --
  serverSelectionTimeoutMS: 5000, // Wait 5s to find a server (default: 30s — too long)
  connectTimeoutMS: 10000, // 10s to establish initial connection
  socketTimeoutMS: 45000, // 45s for operations (default: 0 = no timeout)
  heartbeatFrequencyMS: 10000, // Check server health every 10s (default: 10s)

  // -- Buffering --
  bufferCommands: true, // Queue operations while disconnected (default: true)
  // Mongoose 9: bufferTimeoutMS replaces bufferMaxEntries
  // Operations will fail after this timeout if still disconnected:
  // Set on individual schemas or globally via mongoose.set('bufferTimeoutMS', 20000)

  // -- Write Concern --
  w: "majority", // Wait for majority acknowledgment
  retryWrites: true, // Automatically retry failed writes (default: true)
  retryReads: true, // Automatically retry failed reads (default: true)

  // -- Atlas-specific --
  compressors: ["zstd", "snappy"], // Enable compression for Atlas over WAN
});
```

### Reconnection event handling

```js
const db = mongoose.connection;

db.on("connected", () => {
  console.log("[MongoDB] Connected");
});

db.on("disconnected", () => {
  console.warn("[MongoDB] Disconnected — driver will auto-reconnect");
});

db.on("reconnected", () => {
  console.info("[MongoDB] Reconnected");
});

db.on("error", (err) => {
  console.error("[MongoDB] Connection error:", err.message);
  // The driver handles reconnection automatically — DO NOT call mongoose.connect() again
  // The MongoDB driver uses exponential backoff internally
});

// For topology changes (replica set elections)
db.on("serverHeartbeatFailed", (event) => {
  console.warn("[MongoDB] Heartbeat failed:", event);
});
```

### Important: MongoDB driver handles reconnection automatically

Unlike older versions, Mongoose 9 / MongoDB driver v6 automatically retries connections with exponential backoff. You do NOT need to manually implement reconnection logic. The driver will:

1. Keep trying to reconnect to the replica set
2. Buffer operations during brief disconnections (if `bufferCommands: true`)
3. Reject operations after `serverSelectionTimeoutMS` if no server is available

### Manual reconnection wrapper (for initial connection only)

If the database is down when the app starts, you want to retry initial connection:

```js
const { withRetry } = require("./retry");

async function connectWithRetry() {
  return withRetry(
    async (bail) => {
      try {
        await mongoose.connect(databaseURI, connectionOptions);
        console.log("[MongoDB] Initial connection established");
      } catch (err) {
        // Don't retry on authentication errors
        if (err.message.includes("Authentication failed")) {
          bail(err);
          return;
        }
        throw err; // Will be retried
      }
    },
    {
      retries: 10,
      factor: 2,
      minTimeout: 2000,
      maxTimeout: 30000,
      onRetry: (err, attempt) => {
        console.warn(
          `[MongoDB] Connection attempt ${attempt} failed: ${err.message}`,
        );
      },
    },
  );
}
```

### Links

- Mongoose connection options: https://mongoosejs.com/docs/connections.html
- MongoDB Node.js driver connection: https://www.mongodb.com/docs/drivers/node/current/fundamentals/connection/
- MongoDB connection pool: https://www.mongodb.com/docs/manual/administration/connection-pool-overview/

---

## 5. Server Startup Order

### Problem it solves

Currently, `dzzlo_oms.js` calls `require('./helpers/db_conn')` (fire-and-forget) and immediately calls `app.listen()`. If the DB is slow to connect, the app starts accepting HTTP requests that will all fail because Mongoose hasn't connected yet.

### Current code (problematic)

```js
require("./helpers/db_conn");  // async connection, not awaited
// ... middleware setup ...
app.listen(port, () => { ... }); // listens immediately
```

### Solution: Wait for DB, then listen

The commented-out `defaultConnectionPromise` pattern in `db_conn.js` was the right idea. Here is the corrected approach:

**Modified `helpers/db_conn.js`:**

```js
const mongoose = require("mongoose");
const { databaseURI, database_dip } = require("../api_v/api_constants");

const connectionOptions = {
  maxPoolSize: 10,
  minPoolSize: 2,
  serverSelectionTimeoutMS: 5000,
  connectTimeoutMS: 10000,
  socketTimeoutMS: 45000,
  retryWrites: true,
  retryReads: true,
  w: "majority",
};

// Export a promise that resolves when ALL connections are ready
async function connectAll() {
  // 1. Default connection
  await mongoose.connect(databaseURI, connectionOptions);
  console.log("[MongoDB] Default DB connected");

  // 2. DIP connection
  const db_dip = mongoose.createConnection(database_dip, connectionOptions);
  await db_dip.asPromise(); // Wait for connection
  console.log("[MongoDB] DIP DB connected");

  // Event handlers for ongoing monitoring
  const dbDefault = mongoose.connection;
  dbDefault.on("disconnected", () =>
    console.warn("[MongoDB] Default DB disconnected"),
  );
  dbDefault.on("reconnected", () =>
    console.info("[MongoDB] Default DB reconnected"),
  );
  dbDefault.on("error", (err) =>
    console.error("[MongoDB] Default DB error:", err.message),
  );

  db_dip.on("disconnected", () =>
    console.warn("[MongoDB] DIP DB disconnected"),
  );
  db_dip.on("reconnected", () => console.info("[MongoDB] DIP DB reconnected"));
  db_dip.on("error", (err) =>
    console.error("[MongoDB] DIP DB error:", err.message),
  );

  return { dbDefault, db_dip };
}

module.exports = { connectAll };
```

**Modified `dzzlo_oms.js`:**

```js
const { connectAll } = require("./helpers/db_conn");
const {
  registerGracefulShutdown,
  shutdownGuard,
} = require("./helpers/gracefulShutdown");

// ... express app setup, middleware, routes ...

async function start() {
  try {
    // Step 1: Connect to databases
    const { dbDefault, db_dip } = await connectAll();

    // Step 2: Start accepting connections
    const server = app.listen(port, () => {
      console.log(`Server running in ${process.env.NODE_ENV} on port ${port}`);
      if (process.send) process.send("ready"); // Signal PM2
    });

    // Step 3: Register shutdown handlers
    registerGracefulShutdown(server, { connections: [db_dip] });
  } catch (err) {
    console.error("[STARTUP] Failed to start:", err);
    process.exit(1);
  }
}

start();
```

### Startup order sequence

```
1. Load env vars (dotenv)
2. Create Express app
3. Register middleware
4. Register routes
5. Connect to MongoDB (await) ← BLOCKS until ready
6. app.listen()               ← Only after DB is ready
7. process.send('ready')      ← Tell PM2 we're healthy
8. Register shutdown handlers
```

### Links

- Mongoose connection: https://mongoosejs.com/docs/connections.html#multiple_connections
- PM2 wait_ready: https://pm2.keymetrics.io/docs/usage/signals-clean-restart/#graceful-start

---

## 6. Fallback Strategies

### Problem it solves

When any external service fails, the current system either crashes, returns a 500, or silently drops the notification. There is no degraded-but-functional mode.

### Strategy per service

#### 6a. SMS fails (2Factor.in)

**Priority: Critical** — SMS OTPs block the order flow.

Fallback chain:

1. **Retry** (3 attempts with exponential backoff)
2. **Queue for background retry** (write to MongoDB `failed_sms` collection)
3. **Alternative delivery** (if a backup SMS provider is configured)
4. **Return error to client** with a user-friendly message ("OTP delivery delayed, please retry in 30 seconds")

```js
// models/failed_sms.js
const mongoose = require("mongoose");

const failedSMSSchema = new mongoose.Schema({
  phone: { type: String, required: true },
  payload: { type: mongoose.Schema.Types.Mixed },
  error: { type: String },
  attempts: { type: Number, default: 0 },
  maxAttempts: { type: Number, default: 5 },
  nextRetryAt: { type: Date },
  status: {
    type: String,
    enum: ["pending", "retrying", "delivered", "failed_permanent"],
    default: "pending",
  },
  createdAt: { type: Date, default: Date.now },
});

failedSMSSchema.index({ status: 1, nextRetryAt: 1 }); // For retry worker queries
module.exports = mongoose.model("FailedSMS", failedSMSSchema);
```

```js
// helpers/smsWithFallback.js
const FailedSMS = require("../models/failed_sms");

async function sendSMSWithFallback({ driver_phone, var1, var2 }) {
  try {
    // Attempt direct send (through circuit breaker + retry)
    return await smsBreaker.fire({ driver_phone, var1, var2 });
  } catch (err) {
    // All retries exhausted or circuit is open — queue for background retry
    console.error(`[SMS] Queuing failed SMS for ${driver_phone}`);
    await FailedSMS.create({
      phone: Array.isArray(driver_phone)
        ? driver_phone.join(",")
        : driver_phone,
      payload: { var1, var2 },
      error: err.message,
      nextRetryAt: new Date(Date.now() + 60000), // retry in 1 minute
    });
    return { queued: true, message: "SMS queued for retry" };
  }
}
```

#### 6b. Push notification fails (OneSignal)

**Priority: Medium** — Push failures shouldn't block order flow.

```js
// The circuit breaker fallback (shown in Section 1) handles this:
pushBreaker.fallback(async (params) => {
  // Log to a notifications_dead_letter collection
  await DeadLetterNotification.create({
    type: "push",
    payload: params,
    error: "Circuit open or call failed",
    createdAt: new Date(),
  });
  return { fallback: true };
});

// The order/business logic should NOT await push notifications:
async function completeOrder(orderData) {
  // Critical path — synchronous
  const order = await OrderMst.findByIdAndUpdate(/* ... */);

  // Non-critical — fire and forget, don't block response
  sendNotifyToExternalIDs({
    userIds: [order.customerId],
    headingData: "Order Complete",
    contentData: `Order ${order.orderNo} delivered`,
    notify: true,
  }).catch((err) => {
    // Already handled by circuit breaker + fallback
    console.warn(
      "[PUSH] Fire-and-forget failed (already queued):",
      err.message,
    );
  });

  return order; // Return immediately — don't wait for push
}
```

#### 6c. Email fails (AWS SES)

**Priority: Low-Medium** — Emails are confirmations, not blocking.

- Retry 2x with backoff
- Queue to `failed_emails` collection
- Background job retries every 5 minutes

#### 6d. MongoDB timeout

**Priority: Critical** — Core data store.

There is no "cache and serve stale" option for a write-heavy OMS system. The strategy is:

1. **Connection resilience** (Section 4) — driver auto-reconnects
2. **Operation timeouts** — fail fast instead of hanging
3. **Return 503 with Retry-After header** — tell the client to retry
4. **Health check turns red** — ALB stops routing traffic to this instance

```js
// Middleware: catch MongoDB timeout errors
function mongoTimeoutHandler(err, req, res, next) {
  if (
    err.name === "MongooseServerSelectionError" ||
    err.name === "MongoTopologyClosedError" ||
    err.message?.includes("buffering timed out")
  ) {
    return res.status(503).json({
      error: "Database temporarily unavailable",
      retryAfter: 5,
    });
  }
  next(err);
}
```

### Links

- Fallback pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction
- Queue-based load leveling: https://learn.microsoft.com/en-us/azure/architecture/patterns/queue-based-load-leveling

---

## 7. Deep Health Checks

### Problem it solves

Current `/healthcheck` returns 200 + mongoose readyState. An ALB health check will think the app is healthy even if:

- DB is in "connecting" state (readyState === 2)
- Disk is 99% full
- Memory is exhausted
- External services are all failing

### Implementation

**Rewrite `helpers/healthcheck.js`:**

```js
const express = require("express");
const mongoose = require("mongoose");
const os = require("os");
const { execSync } = require("child_process");
const router = express.Router();

// Quick check (for ALB health checks — called every 10-30s)
router.get("/", async (_req, res) => {
  const dbState = mongoose.connection.readyState;
  // readyState: 0=disconnected, 1=connected, 2=connecting, 3=disconnecting
  if (dbState !== 1) {
    return res.status(503).json({
      status: "unhealthy",
      reason: `Database state: ${mongoose.STATES[dbState]}`,
    });
  }

  res.json({
    status: "healthy",
    uptime: process.uptime(),
    timestamp: Date.now(),
  });
});

// Deep check (for monitoring dashboards — called every 1-5 minutes)
router.get("/deep", async (_req, res) => {
  const checks = {};
  let overallHealthy = true;

  // 1. Database check — actually ping the DB
  try {
    const start = Date.now();
    await mongoose.connection.db.admin().ping();
    checks.database = {
      status: "healthy",
      latencyMs: Date.now() - start,
      readyState: mongoose.STATES[mongoose.connection.readyState],
    };
  } catch (err) {
    overallHealthy = false;
    checks.database = {
      status: "unhealthy",
      error: err.message,
    };
  }

  // 2. Memory check
  const memUsage = process.memoryUsage();
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  const memUsedPercent = (((totalMem - freeMem) / totalMem) * 100).toFixed(1);
  const heapUsedPercent = (
    (memUsage.heapUsed / memUsage.heapTotal) *
    100
  ).toFixed(1);

  checks.memory = {
    status: heapUsedPercent > 90 ? "warning" : "healthy",
    heapUsedMB: Math.round(memUsage.heapUsed / 1024 / 1024),
    heapTotalMB: Math.round(memUsage.heapTotal / 1024 / 1024),
    heapUsedPercent: `${heapUsedPercent}%`,
    rssMB: Math.round(memUsage.rss / 1024 / 1024),
    systemMemUsedPercent: `${memUsedPercent}%`,
  };

  if (heapUsedPercent > 95) overallHealthy = false;

  // 3. Disk check
  try {
    // Works on Linux/macOS
    const dfOutput = execSync("df -k / | tail -1 | awk '{print $5}'", {
      encoding: "utf8",
      timeout: 5000,
    }).trim();
    const diskUsedPercent = parseInt(dfOutput.replace("%", ""), 10);

    checks.disk = {
      status:
        diskUsedPercent > 90
          ? "critical"
          : diskUsedPercent > 80
            ? "warning"
            : "healthy",
      usedPercent: diskUsedPercent,
    };

    if (diskUsedPercent > 95) overallHealthy = false;
  } catch (err) {
    checks.disk = { status: "unknown", error: "Could not check disk" };
  }

  // 4. Event loop lag (indicates CPU pressure)
  const eventLoopLag = await measureEventLoopLag();
  checks.eventLoop = {
    status: eventLoopLag > 500 ? "warning" : "healthy",
    lagMs: eventLoopLag,
  };

  // 5. Process info
  checks.process = {
    pid: process.pid,
    uptime: Math.round(process.uptime()),
    nodeVersion: process.version,
    env: process.env.NODE_ENV,
  };

  res.status(overallHealthy ? 200 : 503).json({
    status: overallHealthy ? "healthy" : "unhealthy",
    timestamp: new Date().toISOString(),
    checks,
  });
});

// Measure event loop lag
function measureEventLoopLag() {
  return new Promise((resolve) => {
    const start = process.hrtime.bigint();
    setImmediate(() => {
      const lag = Number(process.hrtime.bigint() - start) / 1e6; // nanoseconds to ms
      resolve(Math.round(lag * 100) / 100);
    });
  });
}

module.exports = router;
```

### Sample deep health response

```json
{
  "status": "healthy",
  "timestamp": "2026-04-04T10:30:00.000Z",
  "checks": {
    "database": {
      "status": "healthy",
      "latencyMs": 12,
      "readyState": "connected"
    },
    "memory": {
      "status": "healthy",
      "heapUsedMB": 87,
      "heapTotalMB": 256,
      "heapUsedPercent": "34.0%",
      "rssMB": 120,
      "systemMemUsedPercent": "62.3%"
    },
    "disk": {
      "status": "healthy",
      "usedPercent": 47
    },
    "eventLoop": {
      "status": "healthy",
      "lagMs": 1.23
    },
    "process": {
      "pid": 12345,
      "uptime": 86400,
      "nodeVersion": "v20.11.0",
      "env": "production"
    }
  }
}
```

### ALB health check configuration

```
Target Group > Health Checks:
  Path: /healthcheck          (NOT /healthcheck/deep — that's too expensive)
  Interval: 15 seconds
  Timeout: 5 seconds
  Healthy threshold: 2
  Unhealthy threshold: 3
```

### Links

- Kubernetes liveness vs readiness probes (same concept as ALB): https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- AWS ALB health checks: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html
- Terminus (health check library): https://github.com/godaddy/terminus

---

## 8. Dead Letter Queues

### Problem it solves

When SMS, push, or email fails even after retries, the notification is lost forever. There is no record of what failed or mechanism to retry later.

### Lightweight MongoDB-based DLQ (no Redis/SQS needed)

For a solo-dev operation, a full message queue (RabbitMQ, SQS) is overkill. MongoDB + a simple retry worker achieves the same result.

**Model: `models/dead_letter.js`**

```js
const mongoose = require("mongoose");

const deadLetterSchema = new mongoose.Schema(
  {
    // What type of message failed
    type: {
      type: String,
      enum: ["sms", "push", "email"],
      required: true,
      index: true,
    },

    // Original payload
    payload: {
      type: mongoose.Schema.Types.Mixed,
      required: true,
    },

    // Error details
    error: { type: String },
    errorStack: { type: String },

    // Retry tracking
    attempts: { type: Number, default: 0 },
    maxAttempts: { type: Number, default: 5 },
    nextRetryAt: { type: Date, index: true },

    // Status
    status: {
      type: String,
      enum: ["pending", "processing", "delivered", "exhausted"],
      default: "pending",
      index: true,
    },

    // Metadata
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now },
    deliveredAt: { type: Date },
  },
  {
    timestamps: true,
  },
);

// Compound index for the retry worker query
deadLetterSchema.index({ status: 1, nextRetryAt: 1, type: 1 });

// TTL index: auto-delete delivered messages after 30 days
deadLetterSchema.index(
  { deliveredAt: 1 },
  { expireAfterSeconds: 30 * 24 * 60 * 60 },
);

module.exports = mongoose.model("DeadLetter", deadLetterSchema);
```

**Helper: `helpers/deadLetter.js`**

```js
const DeadLetter = require("../models/dead_letter");

/**
 * Queue a failed message for retry.
 *
 * @param {'sms'|'push'|'email'} type
 * @param {Object} payload - Original message data
 * @param {Error|string} error - The error that caused failure
 * @param {Object} opts - { maxAttempts, retryDelayMs }
 */
async function queueForRetry(type, payload, error, opts = {}) {
  const { maxAttempts = 5, retryDelayMs = 60000 } = opts;

  return DeadLetter.create({
    type,
    payload,
    error: typeof error === "string" ? error : error.message,
    errorStack: error?.stack,
    maxAttempts,
    nextRetryAt: new Date(Date.now() + retryDelayMs),
  });
}

/**
 * Process pending dead letters of a given type.
 * Called by a setInterval worker or cron job.
 *
 * @param {'sms'|'push'|'email'} type
 * @param {Function} processor - async function that sends the message
 */
async function processDeadLetters(type, processor) {
  const messages = await DeadLetter.find({
    type,
    status: { $in: ["pending", "processing"] },
    nextRetryAt: { $lte: new Date() },
    $expr: { $lt: ["$attempts", "$maxAttempts"] },
  })
    .sort({ nextRetryAt: 1 })
    .limit(10); // Process 10 at a time

  for (const msg of messages) {
    try {
      msg.status = "processing";
      msg.attempts += 1;
      await msg.save();

      await processor(msg.payload);

      msg.status = "delivered";
      msg.deliveredAt = new Date();
      await msg.save();
      console.log(`[DLQ] Delivered ${type} message ${msg._id}`);
    } catch (err) {
      console.error(`[DLQ] Retry failed for ${msg._id}:`, err.message);

      if (msg.attempts >= msg.maxAttempts) {
        msg.status = "exhausted";
        console.error(
          `[DLQ] EXHAUSTED ${type} message ${msg._id} after ${msg.attempts} attempts`,
        );
      } else {
        msg.status = "pending";
        // Exponential backoff: 1min, 2min, 4min, 8min, 16min
        const delay = 60000 * Math.pow(2, msg.attempts - 1);
        msg.nextRetryAt = new Date(Date.now() + delay);
      }
      msg.error = err.message;
      await msg.save();
    }
  }
}

module.exports = { queueForRetry, processDeadLetters };
```

**Background retry worker (start after DB connection):**

```js
const { processDeadLetters } = require("./helpers/deadLetter");

// Run every 60 seconds
const DLQ_INTERVAL = 60000;

function startDeadLetterWorker() {
  setInterval(async () => {
    try {
      await processDeadLetters("sms", async (payload) => {
        await sendSMSRaw(payload);
      });
      await processDeadLetters("push", async (payload) => {
        await _sendPush(payload);
      });
      await processDeadLetters("email", async (payload) => {
        await sendEmailRaw(payload);
      });
    } catch (err) {
      console.error("[DLQ Worker] Error:", err.message);
    }
  }, DLQ_INTERVAL);

  console.log(`[DLQ Worker] Started — polling every ${DLQ_INTERVAL / 1000}s`);
}
```

### When to upgrade to a real queue (SQS/BullMQ)

- When message volume exceeds ~1000/minute
- When you need guaranteed ordering
- When you have multiple consumers/workers
- When you need visibility into in-flight messages

**BullMQ** (Redis-backed, if you add Redis later):

- npm: `npm install bullmq@^5.0.0`
- Docs: https://docs.bullmq.io/
- Features: delayed jobs, retries, rate limiting, concurrency, dashboard (Bull Board)

### Links

- Dead letter queue pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers
- BullMQ: https://docs.bullmq.io/
- AWS SQS DLQ: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html

---

## 9. Disk Space Management

### Problem it solves

PM2 logs grow unbounded. When disk fills, the OS can't write, PM2 can't log, and the app crashes. The server needs manual cleanup, which means downtime.

### PM2 Log Rotation

**Install pm2-logrotate module globally:**

```bash
pm2 install pm2-logrotate
```

**Configure pm2-logrotate:**

```bash
# Max size per log file before rotation
pm2 set pm2-logrotate:max_size 50M

# Keep last 10 rotated files
pm2 set pm2-logrotate:retain 10

# Enable compression of rotated logs
pm2 set pm2-logrotate:compress true

# Rotate even if file hasn't hit max_size (daily)
pm2 set pm2-logrotate:rotateInterval '0 0 * * *'

# Date format for rotated file names
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss

# Rotate on PM2 start
pm2 set pm2-logrotate:workerInterval 30
```

This means: each log file can grow to max 50MB, then it's rotated and compressed. Only the 10 most recent rotated files are kept. So max disk usage from PM2 logs is approximately `50MB * 10 files * 2 (out + err)` = ~1GB max.

### Ecosystem config with log paths

```js
module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      cwd: __dirname,
      time: true,

      // Explicit log paths
      output: "./logs/pm2/out.log",
      error: "./logs/pm2/error.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",

      // Merge stdout and stderr into one file (optional — simplifies log reading)
      // merge_logs: true,

      // Max memory before PM2 restarts the process (prevents OOM)
      max_memory_restart: "500M",

      // Graceful shutdown
      kill_timeout: 15000,
      wait_ready: true,

      env: { NODE_ENV: "testing" },
      env_testing: { NODE_ENV: "testing" },
      env_production: { NODE_ENV: "production" },
    },
  ],
};
```

### Automated disk cleanup script

Save as `scripts/cleanup-disk.sh`:

```bash
#!/bin/bash
# Automated disk cleanup for DZZLO-OMS server
# Add to crontab: 0 3 * * * /path/to/cleanup-disk.sh >> /var/log/cleanup.log 2>&1

echo "=== Disk Cleanup $(date) ==="

# 1. Clean PM2 logs older than 7 days
find ~/.pm2/logs -name "*.log" -mtime +7 -delete 2>/dev/null
echo "Cleaned old PM2 logs"

# 2. Clean system journal (systemd)
if command -v journalctl &> /dev/null; then
  journalctl --vacuum-time=7d --vacuum-size=100M 2>/dev/null
  echo "Cleaned journald"
fi

# 3. Clean /tmp files older than 3 days
find /tmp -type f -mtime +3 -delete 2>/dev/null
echo "Cleaned /tmp"

# 4. Clean node_modules/.cache if it exists
if [ -d "node_modules/.cache" ]; then
  rm -rf node_modules/.cache
  echo "Cleaned node_modules/.cache"
fi

# 5. Report disk usage
df -h / | tail -1
echo "=== Done ==="
```

### Disk space monitoring in health check

Already included in Section 7's deep health check. If disk > 90%, the health check returns "critical" and can trigger an alert.

### Links

- pm2-logrotate: https://github.com/keymetrics/pm2-logrotate
- PM2 log management: https://pm2.keymetrics.io/docs/usage/log-management/
- Linux logrotate: https://man7.org/linux/man-pages/man8/logrotate.8.html

---

## 10. Zero-Downtime Deploys

### Problem it solves

Current deploy process (likely `git pull && pm2 restart`) causes:

- Connections dropped mid-request
- Brief window where no process is accepting connections
- If the new code fails, no fast rollback

### PM2 Graceful Reload (single server)

**Deploy script: `scripts/deploy.sh`:**

```bash
#!/bin/bash
set -euo pipefail

APP_DIR="/path/to/dzzlo_oms_api"
APP_NAME="dzzlo-oms"
LOG_FILE="$APP_DIR/logs/deploy.log"

echo "=== Deploy started: $(date) ===" | tee -a "$LOG_FILE"

cd "$APP_DIR"

# 1. Save current commit for rollback
PREV_COMMIT=$(git rev-parse HEAD)
echo "Previous commit: $PREV_COMMIT" | tee -a "$LOG_FILE"

# 2. Pull latest code
git fetch origin master
git reset --hard origin/master
echo "Pulled: $(git rev-parse HEAD)" | tee -a "$LOG_FILE"

# 3. Install dependencies (only if package.json changed)
if git diff "$PREV_COMMIT" HEAD --name-only | grep -q "package.json"; then
  echo "package.json changed — installing dependencies..." | tee -a "$LOG_FILE"
  npm ci --production
fi

# 4. Graceful reload (zero-downtime)
# PM2 starts a new process, waits for 'ready' signal, then kills the old one
pm2 reload ecosystem.config.js --env production
echo "PM2 reload complete" | tee -a "$LOG_FILE"

# 5. Wait and verify
sleep 5
HEALTH=$(curl -sf http://localhost:8000/healthcheck || echo '{"status":"failed"}')
echo "Health check: $HEALTH" | tee -a "$LOG_FILE"

# 6. Rollback if unhealthy
if echo "$HEALTH" | grep -q '"status":"unhealthy"' || echo "$HEALTH" | grep -q '"status":"failed"'; then
  echo "UNHEALTHY! Rolling back to $PREV_COMMIT" | tee -a "$LOG_FILE"
  git reset --hard "$PREV_COMMIT"
  npm ci --production
  pm2 reload ecosystem.config.js --env production
  echo "ROLLED BACK" | tee -a "$LOG_FILE"
  exit 1
fi

# 7. Save PM2 process list (survives server reboot)
pm2 save

echo "=== Deploy successful: $(date) ===" | tee -a "$LOG_FILE"
```

### How `pm2 reload` achieves zero downtime

```
1. PM2 spawns a NEW process
2. New process runs startup code, connects to DB
3. New process calls process.send('ready')
4. PM2 marks new process as "online"
5. PM2 sends SIGTERM to OLD process
6. Old process runs graceful shutdown (drains connections)
7. Old process exits
8. Traffic seamlessly moves from old → new
```

Requires these ecosystem.config.js settings:

```js
wait_ready: true,        // Wait for process.send('ready')
listen_timeout: 10000,   // Max wait for 'ready' signal
kill_timeout: 15000,     // Max wait for graceful shutdown
```

### ALB connection draining (if using AWS ALB)

```
Target Group > Attributes:
  Deregistration delay: 30 seconds
```

This tells the ALB to wait 30s for in-flight requests to complete before removing a target.

### Blue-Green alternative (for critical releases)

For breaking changes, run two PM2 apps:

```bash
# Deploy new version as "dzzlo-oms-green"
pm2 start ecosystem.green.config.js --env production

# Verify health
curl http://localhost:8001/healthcheck

# If healthy, swap Nginx upstream
# If unhealthy, kill green and keep blue running
```

### Links

- PM2 zero-downtime reload: https://pm2.keymetrics.io/docs/usage/cluster-mode/#reload
- PM2 deploy: https://pm2.keymetrics.io/docs/usage/deployment-system/
- AWS ALB connection draining: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-target-groups.html#deregistration-delay

---

## 11. Chaos Engineering Basics

### Problem it solves

You can't know if your resilience patterns work unless you test them. For a solo dev, this means simple, manual tests — not Netflix's Chaos Monkey.

### Test scenarios

#### 11a. Simulate MongoDB outage

```bash
# Option 1: Block MongoDB Atlas traffic with iptables (Linux)
sudo iptables -A OUTPUT -d <atlas-host-ip> -j DROP

# Verify: app should return 503, not crash
curl http://localhost:8000/healthcheck
# Should return: { "status": "unhealthy", "reason": "Database state: disconnected" }

# Restore:
sudo iptables -D OUTPUT -d <atlas-host-ip> -j DROP
# App should auto-reconnect within 10-30s
```

```bash
# Option 2: Change connection string to invalid host temporarily
# In .env.production:
# DATABASE_URI=mongodb+srv://invalid-host.example.com/test
# Then: pm2 reload dzzlo-oms
# App should fail to start, PM2 should restart, health check should fail
```

#### 11b. Kill the process

```bash
# Simulate crash — PM2 should auto-restart
pm2 kill
# or
kill -9 $(pm2 pid dzzlo-oms)

# Verify: PM2 restarts within seconds
pm2 status
```

#### 11c. Simulate full disk

```bash
# Create a large file to fill disk (BE CAREFUL)
# Use a separate partition/volume to be safe
dd if=/dev/zero of=/tmp/fillup bs=1M count=5000  # Creates 5GB file

# Verify: health check should report disk critical
curl http://localhost:8000/healthcheck/deep

# Clean up:
rm /tmp/fillup
```

#### 11d. Simulate external service failure

```bash
# Block OneSignal
sudo iptables -A OUTPUT -d onesignal.com -j DROP

# Verify: push notifications should fail gracefully, circuit breaker opens
# Orders should still complete (push is non-blocking)
# Dead letters should appear in the dead_letter collection

# Restore:
sudo iptables -D OUTPUT -d onesignal.com -j DROP
```

#### 11e. Simulate high memory

```js
// Temporary test endpoint (REMOVE AFTER TESTING)
app.get("/chaos/memory-leak", (req, res) => {
  const leak = [];
  for (let i = 0; i < 1000000; i++) {
    leak.push(Buffer.alloc(1024)); // Allocate 1KB * 1M = ~1GB
  }
  res.send("leaking");
});
// PM2 should restart when max_memory_restart (500M) is exceeded
```

#### 11f. Simulate slow event loop

```js
// Temporary test endpoint (REMOVE AFTER TESTING)
app.get("/chaos/slow-event-loop", (req, res) => {
  // Block event loop for 5 seconds
  const start = Date.now();
  while (Date.now() - start < 5000) {}
  res.send("blocked");
});
// Deep health check should show high event loop lag
```

### Chaos engineering checklist (manual, monthly)

```
[ ] Kill PM2 process — verify auto-restart
[ ] Change DB password — verify error handling, then restore
[ ] Block SMS API — verify circuit breaker opens, DLQ captures
[ ] Block push API — verify fire-and-forget doesn't crash order flow
[ ] Fill disk to 90% — verify health check warns
[ ] Send 100 concurrent requests — verify no memory spike
[ ] Deploy bad code — verify rollback script works
[ ] Restart server — verify PM2 startup (pm2 save + pm2 startup)
```

### Links

- Principles of chaos engineering: https://principlesofchaos.org/
- Netflix chaos engineering: https://netflixtechblog.com/tagged/chaos-engineering
- Gremlin (chaos engineering SaaS): https://www.gremlin.com/community/tutorials/chaos-engineering-the-history-principles-and-practice

---

## 12. Bulkhead Pattern

### Problem it solves

If OneSignal is slow (but not failing), all Express worker threads/connections get tied up waiting for push notifications, leaving none available for actual order processing. The bulkhead pattern isolates failure domains so one slow dependency doesn't consume all resources.

### What is a bulkhead?

Named after ship compartments — if one compartment floods, the others stay dry. In software:

- Each external service gets its own limited resource pool (connections, concurrent calls)
- When that pool is exhausted, only calls to THAT service fail — everything else continues

### Implementation approaches for Node.js

#### 12a. Concurrency limiting with p-limit

```bash
npm install p-limit@^5.0.0
```

Note: p-limit v5 is ESM-only. For CJS, use p-limit v4.0.0 or use the approach below.

**Manual concurrency limiter (CJS-compatible):**

```js
// helpers/bulkhead.js

/**
 * Create a concurrency-limited wrapper.
 * Only N calls can be in-flight simultaneously.
 * Additional calls are queued.
 *
 * @param {number} maxConcurrent - Max simultaneous calls
 * @param {number} maxQueue - Max waiting queue size (0 = unlimited)
 * @returns {Function} - limit(fn) wraps a function with concurrency control
 */
function createBulkhead(maxConcurrent, maxQueue = 0) {
  let active = 0;
  const queue = [];

  function next() {
    if (active >= maxConcurrent || queue.length === 0) return;
    active++;
    const { fn, resolve, reject } = queue.shift();
    fn()
      .then(resolve)
      .catch(reject)
      .finally(() => {
        active--;
        next();
      });
  }

  return function limit(fn) {
    return new Promise((resolve, reject) => {
      if (maxQueue > 0 && queue.length >= maxQueue) {
        reject(new Error("Bulkhead queue full"));
        return;
      }
      queue.push({ fn, resolve, reject });
      next();
    });
  };
}

module.exports = { createBulkhead };
```

**Usage — isolate each service:**

```js
const { createBulkhead } = require("../helpers/bulkhead");

// Each service gets its own concurrency limit
const smsBulkhead = createBulkhead(3, 50); // Max 3 concurrent SMS calls, queue up to 50
const pushBulkhead = createBulkhead(5, 100); // Max 5 concurrent push calls, queue up to 100
const emailBulkhead = createBulkhead(2, 20); // Max 2 concurrent email calls, queue up to 20

// Usage in notification code:
async function sendPushBulkheaded(params) {
  return pushBulkhead(() => pushBreaker.fire(params));
}

async function sendSMSBulkheaded(params) {
  return smsBulkhead(() => smsBreaker.fire(params));
}
```

#### 12b. Separate HTTP agents per service

Node.js uses a global HTTP agent with a connection pool. If one service is slow, it can consume all connections. Use separate agents:

```js
const http = require("http");
const https = require("https");

// Each external service gets its own agent with limited connections
const smsAgent = new http.Agent({
  maxSockets: 5, // Max 5 simultaneous TCP connections to 2factor.in
  maxTotalSockets: 10,
  keepAlive: true,
  keepAliveMsecs: 30000,
  timeout: 15000,
});

const pushAgent = new https.Agent({
  maxSockets: 10, // Max 10 TCP connections to OneSignal
  maxTotalSockets: 20,
  keepAlive: true,
  timeout: 10000,
});

const emailAgent = new https.Agent({
  maxSockets: 3, // Max 3 TCP connections to AWS SES
  keepAlive: true,
  timeout: 10000,
});

// Pass agent to fetch/http calls:
fetch("https://onesignal.com/api/v1/notifications", {
  ...params,
  agent: pushAgent, // node-fetch supports this
});
```

#### 12c. Architecture-level bulkhead: Separate processes

For maximum isolation, run notification processing in a separate PM2 process:

```js
// ecosystem.config.js
module.exports = {
  apps: [
    {
      name: "dzzlo-oms-api",
      script: "dzzlo_oms.js",
      // ... API server config
    },
    {
      name: "dzzlo-oms-worker",
      script: "workers/notification_worker.js",
      // Handles DLQ processing, scheduled notifications
      // If this crashes, API server is unaffected
      max_memory_restart: "200M",
      cron_restart: "0 */4 * * *", // Restart every 4 hours (prevent memory leaks)
    },
  ],
};
```

This is the strongest bulkhead: if the notification worker gets stuck or crashes, the API server continues serving orders without interruption.

### Links

- Bulkhead pattern: https://learn.microsoft.com/en-us/azure/architecture/patterns/bulkhead
- Node.js http.Agent: https://nodejs.org/api/http.html#class-httpagent
- p-limit: https://github.com/sindresorhus/p-limit

---

## Summary: Complete Resilience Stack

### NPM packages to add

```json
{
  "opossum": "^8.1.4",
  "async-retry": "^1.3.3"
}
```

That's it. Only 2 new dependencies. Everything else is built with Node.js standard library and Mongoose features.

### Files to create

| File                          | Purpose                                                 |
| ----------------------------- | ------------------------------------------------------- |
| `helpers/circuitBreaker.js`   | Circuit breaker factory using opossum                   |
| `helpers/retry.js`            | Exponential backoff retry wrapper using async-retry     |
| `helpers/gracefulShutdown.js` | Centralized SIGTERM/SIGINT handler, connection draining |
| `helpers/bulkhead.js`         | Concurrency limiter for external services               |
| `helpers/deadLetter.js`       | Queue/process failed notifications                      |
| `models/dead_letter.js`       | MongoDB schema for dead letter queue                    |
| `scripts/deploy.sh`           | Zero-downtime deploy with auto-rollback                 |
| `scripts/cleanup-disk.sh`     | Automated disk cleanup cron job                         |

### Files to modify

| File                                          | Changes                                                                      |
| --------------------------------------------- | ---------------------------------------------------------------------------- |
| `helpers/db_conn.js`                          | Export `connectAll()` promise, add connection options, remove SIGINT handler |
| `helpers/healthcheck.js`                      | Add deep health check (/deep endpoint), DB ping, disk, memory                |
| `dzzlo_oms.js`                                | Await DB before listen, register graceful shutdown, add shutdown guard       |
| `ecosystem.config.js`                         | Add log rotation paths, `wait_ready`, `kill_timeout`, `max_memory_restart`   |
| `api_v3/controllers/App/notification.js`      | Wrap with circuit breaker + retry + fire-and-forget                          |
| `api_v2/controllers/methods/2Factor/index.js` | Promisify HTTP calls, wrap with circuit breaker + retry                      |
| `helpers/sendEmail.js`                        | Wrap with retry                                                              |

### Implementation priority (by impact)

```
Phase 1 (Week 1) — Stop the bleeding:
  1. Server startup order (Section 5) — prevents serving requests before DB ready
  2. Graceful shutdown (Section 3) — clean restarts, no dropped connections
  3. PM2 config updates (Section 9 + 10) — log rotation, max_memory_restart
  4. Deep health check (Section 7) — see problems before they crash you

Phase 2 (Week 2) — External service resilience:
  5. Circuit breaker (Section 1) — for SMS, push, email
  6. Retry with backoff (Section 2) — transient failure recovery
  7. DB connection resilience (Section 4) — connection pool, timeout tuning

Phase 3 (Week 3) — Recovery mechanisms:
  8. Dead letter queue (Section 8) — never lose a notification
  9. Fallback strategies (Section 6) — graceful degradation
  10. Bulkhead (Section 12) — failure isolation

Phase 4 (Ongoing):
  11. Zero-downtime deploys (Section 10) — deploy script
  12. Chaos engineering (Section 11) — monthly verification
```

### How each failure mode is now handled

| Failure Mode            | Before                                  | After                                                                                      |
| ----------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------ |
| MongoDB Atlas goes down | Full outage, timeout errors             | Driver auto-reconnects; health check turns red; ALB stops routing; buffered commands retry |
| 2Factor SMS goes down   | Order flow blocked                      | Circuit breaker opens after 5 failures; SMS queued to DLQ; retried when service recovers   |
| OneSignal goes down     | Push notifications silently fail        | Circuit breaker + fallback; DLQ captures; order flow unaffected (fire-and-forget)          |
| Server disk full        | PM2 logs crash app                      | pm2-logrotate caps at 50MB/file; cleanup cron; deep health check warns at 80%              |
| Bad deploy              | Minutes of downtime                     | `pm2 reload` = zero-downtime; auto-rollback on failed health check                         |
| Developer unavailable   | Complete paralysis                      | PM2 auto-restart on crash; max_memory_restart; self-healing patterns; structured logs      |
| No graceful degradation | Binary: works or crashes                | Per-service circuit breakers; fallback chains; non-critical services fire-and-forget       |
| No retry logic          | First failure = permanent failure       | async-retry with exponential backoff + jitter; DLQ for exhausted retries                   |
| Shallow health check    | ALB thinks app is healthy when it isn't | Deep check: DB ping, disk %, memory %, event loop lag                                      |
