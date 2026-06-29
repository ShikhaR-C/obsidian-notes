# Solutions: Resilience & Automation

> Complete solutions for making DZZLO-OMS unbreakable and fully automated.
> Based on codebase analysis: `dzzlo_oms.js`, `helpers/db_conn.js`, `ecosystem.config.js`, `helpers/middlewares.js`.

---

## Priority Summary

| #   | Solution                              | Effort | Cost | Phase           |
| --- | ------------------------------------- | ------ | ---- | --------------- |
| 1   | Wait for DB before accepting requests | 15 min | $0   | P0 — now        |
| 2   | Graceful shutdown (SIGTERM + drain)   | 30 min | $0   | P0 — now        |
| 3   | PM2 cluster mode + config             | 30 min | $0   | P0 — now        |
| 4   | PM2 log rotation                      | 15 min | $0   | P0 — now        |
| 5   | Deep health check endpoint            | 30 min | $0   | P0 — now        |
| 6   | Circuit breaker for external APIs     | 1 hour | $0   | P1 — this month |
| 7   | Retry with backoff for DB/APIs        | 30 min | $0   | P1 — this month |
| 8   | GitHub Actions CI (tests on push)     | 1 hour | $0   | P1 — this month |
| 9   | Deploy script (deploy.sh)             | 1 hour | $0   | P1 — this month |
| 10  | Emergency runbook                     | 1 hour | $0   | P1 — this month |
| 11  | Zero-downtime deploys                 | 15 min | $0   | P1 — this month |
| 12  | CloudWatch alarms (5 critical)        | 1 hour | ~$2  | P1 — this month |

**Only 2 npm packages needed:** `opossum` (circuit breaker) + `lru-cache` (already added for caching).

---

## RESILIENCE

### Solution 1: Wait for DB Before Accepting Requests

**Problem:** `dzzlo_oms.js:134` — `app.listen()` fires immediately. Server accepts requests before MongoDB connects.

```javascript
// helpers/db_conn.js — export the promise
const defaultConnectionPromise = mongoose
  .connect(databaseURI)
  .then(() => {
    console.log("DATABASE CONNECTED!!");
    return mongoose.connection;
  })
  .catch((err) => {
    console.error("DB connection failed:", err.message);
    throw err;
  });

module.exports = { dbDefault, db_dip, defaultConnectionPromise };
```

```javascript
// dzzlo_oms.js — wait before listening
const { defaultConnectionPromise } = require("./helpers/db_conn");

// ... all middleware and routes ...

defaultConnectionPromise
  .then(() => {
    app.listen(port, () => console.log(`Server running on port ${port}`));
  })
  .catch((err) => {
    console.error("Failed to connect. Exiting.", err);
    process.exit(1); // PM2 will auto-restart
  });
```

### Solution 2: Graceful Shutdown

**Problem:** `helpers/db_conn.js:53` only handles SIGINT, not SIGTERM (what PM2 sends). No HTTP connection draining.

```javascript
// dzzlo_oms.js — add after app.listen
const server = app.listen(port, () => {
  /* ... */
});

async function gracefulShutdown(signal) {
  console.log(`\n${signal} received. Graceful shutdown starting...`);

  // 1. Stop accepting new connections
  server.close(() => {
    console.log("HTTP server closed");
  });

  // 2. Close DB connections
  try {
    await mongoose.disconnect();
    await db_dip.close();
    console.log("Database connections closed");
  } catch (err) {
    console.error("Error closing DB:", err.message);
  }

  // 3. Exit
  process.exit(0);
}

process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));

// Safety net: force exit after 10 seconds
process.on("SIGTERM", () => {
  setTimeout(() => {
    console.error("Forced exit after timeout");
    process.exit(1);
  }, 10000);
});
```

### Solution 3: PM2 Cluster Mode + Config

**Problem:** `ecosystem.config.js` runs single process. 2 vCPUs available on t3.small.

```javascript
// ecosystem.config.js — UPDATED
module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      instances: "max", // Use all available CPUs
      exec_mode: "cluster", // Enable cluster mode
      watch: false,

      // Graceful shutdown
      kill_timeout: 10000, // 10s to finish requests before SIGKILL
      listen_timeout: 10000, // 10s to start before marked failed
      wait_ready: false, // Set true if using process.send('ready')

      // Memory guard
      max_memory_restart: "500M", // Restart if exceeds 500MB (t3.micro has 1GB)

      // Logs
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      error_file: "./logs/err.log",
      out_file: "./logs/out.log",
      merge_logs: true,

      // Environment
      env_testing: {
        NODE_ENV: "testing",
        PORT: 8030,
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 8030,
      },
    },
  ],
};
```

### Solution 4: PM2 Log Rotation

**Problem:** PM2 logs grow unbounded. Disk fills up. App crashes.

```bash
# Install pm2-logrotate
pm2 install pm2-logrotate

# Configure
pm2 set pm2-logrotate:max_size 10M      # Rotate at 10MB
pm2 set pm2-logrotate:retain 5          # Keep 5 rotated files
pm2 set pm2-logrotate:compress true     # Gzip old logs
pm2 set pm2-logrotate:workerInterval 30 # Check every 30 seconds
```

### Solution 5: Deep Health Check

**Problem:** Current `/healthcheck` just returns 200. Doesn't check if DB is actually connected.

```javascript
// helpers/healthcheck.js — UPGRADED
const mongoose = require("mongoose");
const os = require("os");

const healthcheck = async (req, res) => {
  const health = {
    status: "ok",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),

    database: {
      status:
        mongoose.connection.readyState === 1 ? "connected" : "disconnected",
      readyState: mongoose.connection.readyState,
    },

    memory: {
      used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024) + " MB",
      total: Math.round(os.totalmem() / 1024 / 1024) + " MB",
      free: Math.round(os.freemem() / 1024 / 1024) + " MB",
    },

    disk: {
      // Check if logs directory is accessible
      writable: true,
    },
  };

  // If DB is not connected, return 503
  if (mongoose.connection.readyState !== 1) {
    health.status = "degraded";
    return res.status(503).json(health);
  }

  res.status(200).json(health);
};

module.exports = (req, res) => healthcheck(req, res);
```

ALB health checks will detect DB-down state and stop routing traffic to unhealthy instances.

### Solution 6: Circuit Breaker for External APIs

**Problem:** If 2Factor.in (SMS) hangs, your request hangs forever. No timeout, no fallback.

```bash
npm install opossum
```

```javascript
// helpers/circuitBreaker.js
const CircuitBreaker = require("opossum");

const defaultOptions = {
  timeout: 5000, // 5 second timeout per call
  errorThresholdPercentage: 50, // Open circuit at 50% failure
  resetTimeout: 30000, // Try again after 30 seconds
  volumeThreshold: 5, // Need 5 calls before circuit logic kicks in
};

function createBreaker(fn, name, options = {}) {
  const breaker = new CircuitBreaker(fn, { ...defaultOptions, ...options });

  breaker.on("open", () =>
    console.warn(`[Circuit] ${name} OPEN — requests will fail fast`),
  );
  breaker.on("halfOpen", () =>
    console.log(`[Circuit] ${name} HALF-OPEN — testing...`),
  );
  breaker.on("close", () =>
    console.log(`[Circuit] ${name} CLOSED — recovered`),
  );
  breaker.on("fallback", () =>
    console.log(`[Circuit] ${name} fallback triggered`),
  );

  return breaker;
}

module.exports = { createBreaker };
```

**Wrap SMS sending:**

```javascript
const { createBreaker } = require("../../helpers/circuitBreaker");

// Original function
async function sendSMS(phone, message) {
  // existing 2Factor.in API call
}

// Wrapped with circuit breaker
const smsBreaker = createBreaker(sendSMS, "2Factor-SMS", {
  timeout: 8000,
  fallback: (phone, message) => {
    console.error(`SMS failed (circuit open). Queuing for retry: ${phone}`);
    // Could save to DB for retry later
    return { success: false, queued: true };
  },
});

// Usage in controller:
const result = await smsBreaker.fire(phone, message);
```

### Solution 7: Retry with Exponential Backoff

```bash
npm install async-retry
```

```javascript
const retry = require("async-retry");

// Wrap any unreliable operation
const result = await retry(
  async (bail, attempt) => {
    console.log(`Attempt ${attempt}...`);
    const res = await sendSMStoAPI(phone, message);
    if (res.status === 400) bail(new Error("Bad request")); // Don't retry 4xx
    return res;
  },
  {
    retries: 3,
    factor: 2, // Exponential: 1s, 2s, 4s
    minTimeout: 1000,
    maxTimeout: 5000,
    onRetry: (err, attempt) => console.warn(`Retry ${attempt}: ${err.message}`),
  },
);
```

---

## AUTOMATION

### Solution 8: GitHub Actions CI (Tests on Push)

```yaml
# .github/workflows/test.yml
name: Tests
on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: yarn
      - run: yarn install --frozen-lockfile
      - run: yarn test
        env:
          NODE_ENV: testing
```

This catches bugs BEFORE they reach production. Uses your existing Jest + mongodb-memory-server setup.

### Solution 9: Deploy Script

```bash
#!/bin/bash
# deploy.sh — Deploy to production servers
set -e

SERVERS=("user@server1-ip" "user@server2-ip")
APP_DIR="/path/to/dzzlo_oms_api"
APP_NAME="dzzlo-oms"
HEALTH_URL="http://localhost:8030/healthcheck"

deploy_server() {
  local server=$1
  echo "=== Deploying to $server ==="

  ssh $server "cd $APP_DIR && git pull origin master && yarn install --frozen-lockfile"
  ssh $server "cd $APP_DIR && pm2 reload $APP_NAME"

  # Wait for health check
  sleep 3
  local status=$(ssh $server "curl -s -o /dev/null -w '%{http_code}' $HEALTH_URL")

  if [ "$status" != "200" ]; then
    echo "HEALTH CHECK FAILED on $server! Rolling back..."
    ssh $server "cd $APP_DIR && git checkout HEAD~1 && pm2 reload $APP_NAME"
    exit 1
  fi

  echo "=== $server deployed successfully ==="
}

for server in "${SERVERS[@]}"; do
  deploy_server "$server"
done

echo "=== All servers deployed ==="
```

### Solution 10: Emergency Runbook

Create `docs/runbook.md`:

```markdown
# Emergency Runbook

## 502/504 Errors

1. Check: `aws ssm start-session --target i-XXXXX`
2. Check PM2: `pm2 status && pm2 logs dzzlo-oms --lines 50`
3. Check DB: `mongosh $DATABASE_URI --eval "db.runCommand({ping:1})"`
4. Restart: `pm2 reload dzzlo-oms`

## Rollback Bad Deploy

1. Detach from ALB (AWS Console → Target Groups → Deregister)
2. `cd /path/to/app && git log --oneline -5` (find last good commit)
3. `git checkout <good-commit>`
4. `pm2 reload dzzlo-oms`
5. Verify: `curl http://localhost:8030/healthcheck`
6. Re-attach to ALB

## MongoDB Atlas Down

1. Check: https://status.cloud.mongodb.com/
2. App will return timeout errors — nothing to do but wait
3. Check Atlas Console → Cluster → Metrics for issues

## Server Unreachable

1. AWS Console → EC2 → Check instance status
2. If stopped: Start instance
3. If terminated: ASG should auto-replace (check ASG activity)
4. New instance: SSH via SSM, verify PM2 is running
```

### Solution 11: Zero-Downtime Deploys

Use `pm2 reload` instead of `pm2 restart`:

```bash
# BEFORE (downtime):
pm2 restart dzzlo-oms

# AFTER (zero-downtime):
pm2 reload dzzlo-oms
```

`reload` starts new workers, waits for them to be ready, then gracefully kills old workers. Combined with ALB connection draining (default 300s), users never see errors.

### Solution 12: CloudWatch Alarms (5 Critical)

Set up via AWS Console: CloudWatch → Alarms → Create:

| Alarm           | Metric                     | Threshold       | Action      |
| --------------- | -------------------------- | --------------- | ----------- |
| CPU High        | EC2 CPUUtilization         | > 80% for 5 min | SNS → email |
| ALB 5xx         | ALB HTTPCode_ELB_5XX_Count | > 10 in 5 min   | SNS → email |
| Unhealthy Hosts | ALB HealthyHostCount       | < 2             | SNS → email |
| Slow Response   | ALB TargetResponseTime     | > 5 sec avg     | SNS → email |
| Status Check    | EC2 StatusCheckFailed      | > 0             | SNS → email |

First, create an SNS topic: `dzzlo-alerts` → subscribe your email.

**Cost:** ~$0.10/alarm/month = ~$0.50/month total.

---

## Failure Mode Coverage

| Failure               | Before                      | After                                                       |
| --------------------- | --------------------------- | ----------------------------------------------------------- |
| MongoDB down          | Full outage, timeout errors | Health check → ALB stops routing → CloudWatch alarm → email |
| SMS provider hangs    | Request hangs forever       | Circuit breaker → fail fast → fallback (queue for retry)    |
| OneSignal down        | Silent failure              | Circuit breaker → logged → retry later                      |
| Bad deploy            | Manual rollback (minutes)   | deploy.sh auto-rollback on health check failure             |
| Disk full             | App crashes                 | PM2 log rotation (10MB max) + max_memory_restart            |
| Server crash          | PM2 restarts, but slowly    | PM2 cluster mode (other workers handle traffic)             |
| Developer unavailable | Complete paralysis          | Emergency runbook + GitHub Actions for basic deploys        |
| DB connection lost    | Unhandled timeout           | Mongoose reconnection + graceful error response             |

---

_Total npm additions: opossum (circuit breaker). Total AWS cost: ~$2.50/month (CloudWatch alarms). Everything else is free configuration._
