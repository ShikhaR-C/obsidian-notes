# Phase 6: Automation & Monitoring

**Priority:** P3 | **Timeline:** Week 11-12

---

## Research: Production Monitoring for Node.js + MongoDB

### Three Pillars of Observability

1. **Metrics** -- quantitative measurements (latency, throughput, error rate)
2. **Logs** -- discrete events with context
3. **Traces** -- request flow through the system

### Key Metrics to Monitor

| Category   | Metric                      | Target     |
| ---------- | --------------------------- | ---------- |
| Latency    | p50, p95, p99 response time | p95 < 50ms |
| Throughput | Requests per second         | > 200 RPS  |
| Errors     | 5xx rate                    | < 0.1%     |
| Saturation | CPU, Memory, Connections    | < 70%      |
| MongoDB    | Slow queries (> 100ms)      | 0          |
| Redis      | Hit rate                    | > 80%      |
| App        | JS thread FPS               | > 58       |

---

## Sub-Phase 6A: Enhanced Health Checks

### Step 6A-1: Comprehensive Health Endpoint

**Current:** `helpers/healthcheck.js` -- minimal ping

**Proposed:** `GET /health` with deep checks

```js
// helpers/healthcheck.js
const mongoose = require("mongoose");
const { redis } = require("./cache");

exports.healthCheck = async (req, res) => {
  const checks = {};
  const start = process.hrtime.bigint();

  // 1. MongoDB check
  try {
    const mongoStart = process.hrtime.bigint();
    checks.mongodb = {
      status: mongoose.connection.readyState === 1 ? "healthy" : "degraded",
      readyState: mongoose.connection.readyState,
      latencyMs: 0,
    };
    // Probe query
    await mongoose.connection.db.admin().ping();
    checks.mongodb.latencyMs =
      Number(process.hrtime.bigint() - mongoStart) / 1e6;
  } catch (err) {
    checks.mongodb = { status: "unhealthy", error: err.message };
  }

  // 2. Redis check
  try {
    const redisStart = process.hrtime.bigint();
    await redis.ping();
    checks.redis = {
      status: "healthy",
      latencyMs: Number(process.hrtime.bigint() - redisStart) / 1e6,
    };
  } catch (err) {
    checks.redis = { status: "unhealthy", error: err.message };
  }

  // 3. Memory check
  const mem = process.memoryUsage();
  checks.memory = {
    heapUsedMB: Math.round(mem.heapUsed / 1024 / 1024),
    heapTotalMB: Math.round(mem.heapTotal / 1024 / 1024),
    rssMB: Math.round(mem.rss / 1024 / 1024),
    status: mem.heapUsed / mem.heapTotal < 0.85 ? "healthy" : "warning",
  };

  // 4. Uptime
  checks.uptime = {
    seconds: Math.round(process.uptime()),
    pid: process.pid,
  };

  const overall = Object.values(checks).every((c) => c.status === "healthy")
    ? "healthy"
    : Object.values(checks).some((c) => c.status === "unhealthy")
      ? "unhealthy"
      : "degraded";

  const totalMs = Number(process.hrtime.bigint() - start) / 1e6;

  res.status(overall === "unhealthy" ? 503 : 200).json({
    status: overall,
    totalMs: totalMs.toFixed(1),
    checks,
    timestamp: new Date().toISOString(),
  });
};
```

**Route:** Add before auth middleware (public endpoint):

```js
app.get("/health", healthCheck);
```

### Step 6A-2: Readiness vs Liveness Probes

```js
// Liveness -- is the process alive?
app.get("/healthz", (req, res) => res.status(200).json({ status: "alive" }));

// Readiness -- can the process serve traffic?
app.get("/readyz", async (req, res) => {
  const mongoReady = mongoose.connection.readyState === 1;
  const redisReady = redis.status === "ready";
  if (mongoReady && redisReady) {
    res.status(200).json({ status: "ready" });
  } else {
    res
      .status(503)
      .json({ status: "not ready", mongo: mongoReady, redis: redisReady });
  }
});
```

---

## Sub-Phase 6B: Slow Query Detection

### Step 6B-1: Mongoose Query Timing Plugin

```js
// helpers/queryTimer.js
const mongoose = require("mongoose");

const SLOW_QUERY_THRESHOLD_MS = 100;

mongoose.plugin((schema) => {
  // Track find, findOne, findOneAndUpdate, aggregate, etc.
  const operations = [
    "find",
    "findOne",
    "findOneAndUpdate",
    "findOneAndDelete",
    "countDocuments",
    "aggregate",
  ];

  operations.forEach((op) => {
    schema.pre(op, function () {
      this._queryStartTime = Date.now();
    });

    schema.post(op, function () {
      if (this._queryStartTime) {
        const elapsed = Date.now() - this._queryStartTime;
        if (elapsed > SLOW_QUERY_THRESHOLD_MS) {
          const collection =
            this.model?.collection?.name ||
            this.mongooseCollection?.name ||
            "unknown";
          const filter = JSON.stringify(this.getQuery ? this.getQuery() : {});
          console.warn(
            `[SLOW QUERY] ${collection}.${op} took ${elapsed}ms | filter: ${filter}`,
          );

          // Optionally: send to monitoring service
          // metricsClient.histogram('db.query.duration', elapsed, { collection, operation: op });
        }
      }
    });
  });
});

module.exports = {}; // Just importing this file activates the plugin
```

**Add to `dzzlo_oms.js` (before routes):**

```js
require("./helpers/queryTimer");
```

### Step 6B-2: MongoDB Atlas Performance Advisor

Enable in Atlas dashboard:

- **Performance Advisor** -- suggests missing indexes
- **Real-Time Performance Panel** -- shows current operations
- **Profiler** -- captures slow operations

```
Atlas Console > Cluster > Performance Advisor
→ Review suggested indexes
→ Apply high-impact indexes
```

---

## Sub-Phase 6C: Logging Improvements

### Step 6C-1: TTL Index on Logs Collection

Auto-delete logs older than 30 days:

```js
// models/logs.js
logsSchema.index({ createdAt: 1 }, { expireAfterSeconds: 30 * 24 * 60 * 60 });
```

**Impact:** Prevents unbounded collection growth.

### Step 6C-2: Structured Logging

Replace `console.log/warn/error` with structured logger:

```bash
yarn add pino
```

```js
// helpers/logger.js
const pino = require("pino");

const logger = pino({
  level: process.env.LOG_LEVEL || "info",
  transport:
    process.env.NODE_ENV === "development"
      ? { target: "pino-pretty" }
      : undefined,
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },
});

module.exports = logger;
```

**Usage:**

```js
const logger = require("./helpers/logger");
logger.info({ orderId, latencyMs: elapsed }, "Order created successfully");
logger.warn({ queryTime: elapsed, collection }, "Slow query detected");
logger.error({ err, endpoint }, "Request failed");
```

### Step 6C-3: Request Correlation IDs

Add unique ID per request for tracing:

```js
const { v4: uuidv4 } = require("uuid");

app.use((req, res, next) => {
  req.correlationId = req.headers["x-correlation-id"] || uuidv4();
  res.set("x-correlation-id", req.correlationId);
  next();
});
```

---

## Sub-Phase 6D: CI/CD Pipeline

### Step 6D-1: Pre-commit Hooks

```bash
yarn add husky lint-staged --dev
npx husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.js": ["eslint --fix", "prettier --write"]
  }
}
```

### Step 6D-2: CI Workflow (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:7
        ports: [27017:27017]
      redis:
        image: redis:7
        ports: [6379:6379]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 18 }
      - run: yarn install --frozen-lockfile
      - run: yarn lint
      - run: yarn test
        env:
          NODE_ENV: testing
          DATABASE_URI: mongodb://localhost:27017/dzzlo_test

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: yarn audit --groups dependencies
      - uses: aquasecurity/trivy-action@master
        with: { scan-type: fs }
```

### Step 6D-3: Index Validation Script

```js
// scripts/validate-indexes.js
const mongoose = require("mongoose");
const models = require("../models");

async function validateIndexes() {
  await mongoose.connect(process.env.DATABASE_URI);

  for (const [name, model] of Object.entries(models)) {
    const codeIndexes = model.schema.indexes();
    const dbIndexes = await model.collection.indexes();

    for (const [fields] of codeIndexes) {
      const exists = dbIndexes.some(
        (dbIdx) => JSON.stringify(dbIdx.key) === JSON.stringify(fields),
      );
      if (!exists) {
        console.warn(`MISSING INDEX: ${name} -> ${JSON.stringify(fields)}`);
      }
    }
  }

  await mongoose.disconnect();
}

validateIndexes().catch(console.error);
```

---

## Sub-Phase 6E: Load Testing

### Step 6E-1: k6 Load Test Scripts

```bash
# Install k6
brew install k6
```

```js
// tests/load/order-list.js
import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 50 }, // Ramp up to 50 users
    { duration: "1m", target: 200 }, // Ramp up to 200 users
    { duration: "1m", target: 200 }, // Hold at 200
    { duration: "30s", target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<50"], // 95% under 50ms
    http_req_failed: ["rate<0.01"], // <1% error rate
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8030";
const TOKEN = __ENV.AUTH_TOKEN;

export default function () {
  const headers = {
    Authorization: `Bearer ${TOKEN}`,
    "x-api-key": __ENV.API_KEY,
    "Content-Type": "application/json",
  };

  // Order list (most common endpoint)
  const res = http.post(
    `${BASE_URL}/api/v3/order_msts/a/poso`,
    JSON.stringify({
      filterProps: { page: 1, limit: 20 },
      role: "customer",
      comp_id: __ENV.COMP_ID,
    }),
    { headers },
  );

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 50ms": (r) => r.timings.duration < 50,
    "has data": (r) => JSON.parse(r.body).data?.length > 0,
  });

  sleep(1);
}
```

**Run:**

```bash
k6 run --env BASE_URL=https://doms.vsyst.in --env AUTH_TOKEN=xxx tests/load/order-list.js
```

### Step 6E-2: Automated Load Test in CI

Add as a scheduled job (weekly) or on release branches.

---

## Monitoring Dashboard Recommendations

### Option A: Free/Open Source

- **Grafana + Prometheus** for metrics
- **Loki** for log aggregation
- **MongoDB Atlas** built-in monitoring

### Option B: Managed Services

- **Datadog** or **New Relic** for APM
- **Sentry** for error tracking
- **PagerDuty** for alerting

### Key Alerts to Configure

| Alert           | Condition                     | Severity |
| --------------- | ----------------------------- | -------- |
| High error rate | 5xx > 1% in 5 min             | Critical |
| High latency    | p95 > 100ms for 5 min         | Warning  |
| MongoDB down    | readyState !== 1 for 30s      | Critical |
| Redis down      | ping fails for 30s            | Warning  |
| Memory > 85%    | heapUsed/heapTotal > 0.85     | Warning  |
| Slow queries    | > 10 queries > 100ms in 5 min | Warning  |
| Disk space      | < 20% free                    | Warning  |

---

## Verification

1. **Health endpoint:** `curl /health` returns status for all components
2. **Slow query log:** Run load test; verify slow queries are logged
3. **TTL index:** Insert old log entry; verify it's deleted after TTL
4. **CI pipeline:** Push commit; verify lint + test + audit pass
5. **Load test:** Run k6; verify p95 < 50ms at 200 RPS
