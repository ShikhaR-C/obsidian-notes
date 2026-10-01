# Resilience & Operations

> Make the system harder to break and easier to operate.
> These changes affect how the app starts, stops, recovers, and is deployed.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). RES-1, RES-2 and RES-8 are in the API repo and RES-5 is written into its runbook (4 ✅); RES-3 is skipped on this doc's own advice (⏸); RES-4, RES-6 and RES-7 live on servers and consoles (3 ❔). The API runbook, the v4 limiter and the pool settings all describe two servers while RES-6 below says single instance — `X-OPS-1`. v4 added three safety valves (`QUERY_TIMEOUT`, `UNAVAILABLE`, `RATE_LIMITED`) that the app does not yet word or keep out of its retries — `X-APP-1`. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## RES-1: Deep health check endpoint (API)

**Status (2026-10-01):** ✅ done — `395861f`; `helpers/healthcheck.js:5-23` answers 503 with `status: "degraded"` whenever Mongo's `readyState` is not 1, with uptime and heap MB; the API runbook uses it for triage (`docs/runbook.md:40-47`).

**Size:** XS (15 min)
**File:** `helpers/healthcheck.js`

**What:** Upgrade the current healthcheck to actually check if MongoDB is connected and report memory usage.

```js
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
    },
  };

  if (mongoose.connection.readyState !== 1) {
    health.status = "degraded";
    return res.status(503).json(health);
  }
  res.status(200).json(health);
};
```

**Why:** The current healthcheck just returns 200 regardless of whether the database is connected. If MongoDB goes down, the ALB keeps routing traffic to a server that can't serve any requests. With a 503 on DB failure, the ALB marks the target unhealthy and stops routing to it.

**How to verify:**

- API: `GET /healthcheck` returns 200 with DB status. If you disconnect MongoDB, returns 503.
- App: No change needed. The ALB handles routing automatically.

**Discussion:** This is the foundation for reliable operations. Without it, you can't trust the ALB's health status. The memory info is a bonus — helps spot memory leaks during monitoring.

**Why the current healthcheck is broken:** The current code includes `isDBup` and `dbStateMessage` in the response body, but the HTTP status code is always 200. The `try/catch` on `res.send()` only catches errors from the send itself (e.g., response stream breaking) — it never checks `mongoose.connection.readyState`. So even when `isDBup: 0` and `dbStateMessage: "disconnected"`, the ALB gets a `200 OK`, thinks the server is healthy, and keeps routing traffic to a server that can't serve any requests. The fix adds an actual readyState check and returns `503` when the DB is down, so the ALB correctly marks the target as unhealthy.

---

## RES-2: Graceful shutdown handler (API)

**Status (2026-10-01):** ✅ done — `fab1fe1`, `95c42be`; on SIGTERM / SIGINT `gracefulShutdown` awaits `server.close`, disconnects Mongo and force-exits after 10 s (`dzzlo_oms.js:145-165`). Caveat: a second SIGINT handler (`helpers/db_conn.js:83-89`) and PM2's defaults can cut it short — `T01-N2` below.

**Size:** S (15 min)
**File:** `dzzlo_oms.js`

**What:** Handle `SIGTERM` (what PM2 sends on `pm2 reload`) and `SIGINT` gracefully:

1. Stop accepting new connections
2. Close DB connections
3. Exit

```js
async function gracefulShutdown(signal) {
  console.log(`${signal} received. Shutting down...`);
  server.close(() => console.log("HTTP server closed"));
  try {
    await mongoose.disconnect();
    console.log("Database disconnected");
  } catch (err) {
    console.error("Error closing DB:", err.message);
  }
  process.exit(0);
}

process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
process.on("SIGINT", () => gracefulShutdown("SIGINT"));

// Safety net
setTimeout(() => {
  console.error("Forced exit");
  process.exit(1);
}, 10000);
```

**Why:** Without graceful shutdown, `pm2 reload` kills the process mid-request. In-flight requests get dropped. DB connections leak. With graceful shutdown, active requests complete before the process exits.

**How to verify:**

- API: Run `pm2 reload dzzlo-oms`. Active requests should complete without error.
- App: Users shouldn't notice deployments.

**Discussion:** Required prerequisite for zero-downtime deployments. Combined with PM2 cluster mode (RES-3), `pm2 reload` becomes truly zero-downtime.

**How this helps during deploy (disconnect → update → redeploy):**

Without RES-2, when you disconnect a server from traffic and run `pm2 reload`/`pm2 restart`, requests already in-flight are still being processed. PM2 sends `SIGTERM`, the process ignores it, PM2 sends `SIGKILL` after timeout, and those in-flight requests get dropped mid-execution — users see errors. MongoDB connections are also not closed — they leak and linger until Atlas times them out.

With RES-2, when PM2 sends `SIGTERM`, `gracefulShutdown()` fires: `server.close()` stops accepting new connections but lets in-flight requests finish, `mongoose.disconnect()` cleanly closes DB connections (no leaked connections in Atlas), and `process.exit(0)` gives a clean exit. The 10-second safety net force-kills the process if something hangs, preventing a stuck deploy.

Even after you remove a server from the load balancer, there's a window where requests are still mid-execution. RES-2 protects that window — the difference between a hard kill (yank the power cord mid-sentence) and a graceful shutdown (finish what you're saying, hang up the phone, then leave).

---

## RES-3: Enable PM2 cluster mode (API)

**Status (2026-10-01):** ⏸ skipped, as this item advises at ~130 orders/day — `ecosystem.config.js` defines one app in fork mode with no `instances`, `exec_mode`, `kill_timeout` or `max_memory_restart`. Production scales out across two servers instead, per the API runbook — `X-OPS-1`.

**Size:** S (10 min)
**File:** `ecosystem.config.js`

**What:** Change `instances: 1` to `instances: 'max'` and add `exec_mode: 'cluster'`.

```js
module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      instances: "max", // Use all CPU cores
      exec_mode: "cluster", // Enable cluster mode
      kill_timeout: 10000, // 10s for graceful shutdown
      max_memory_restart: "500M", // Restart on memory leak
      merge_logs: true,
    },
  ],
};
```

**Prerequisites:**

- RES-2 (graceful shutdown) should be done first
- No shared in-memory state that can't be lost (check: the `logBuffer` in logging middleware is per-process, which is fine)
- Rate limiting must use Redis store if you need accurate cross-process limits (for now, per-process limits are acceptable)

**Why:** Your t3.small has 2 vCPUs but PM2 runs 1 process — 50% of CPU capacity is wasted. Cluster mode doubles throughput for free. More importantly, it enables zero-downtime `pm2 reload` — PM2 restarts workers one at a time while others keep serving.

**How to verify:**

- API: `pm2 list` should show 2 (or more) instances. All endpoints work.
- App: No change needed.

**Discussion:** This is free performance. The only thing to watch for is any module-level mutable state that would break when multiple workers run. Your app uses JWT (stateless) and MongoDB (external state), so cluster mode is safe.

**Caveat — cluster mode leaves no CPU headroom on t3.small:** `instances: 'max'` uses all CPU cores (2 on t3.small), which means no headroom for:

- **Burst traffic** — a spike pushes CPU to 100% immediately, response times balloon
- **System tasks** — OS, PM2 daemon, MongoDB driver overhead, log rotation compete for the same cores
- **t3.small CPU credits** — sustained 100% burns credits fast; once depleted, you're throttled to baseline (~20% of 2 vCPUs)
- **Graceful reload** — during `pm2 reload`, old + new workers run briefly in parallel, doubling CPU pressure

On a 2-vCPU box, practical choices are: (1) stay at `instances: 1` with lots of headroom and half the throughput, (2) `instances: 2` for 2x throughput but zero headroom (risky on burstable), or (3) upgrade to a non-burstable instance (e.g., t3.medium with managed credits, or m-family) before clustering.

**At ~130 orders/day, skip RES-3 for now.** The throughput is not needed, and the CPU-contention tradeoff on a burstable 2-vCPU instance is real. Revisit when traffic grows or when you upgrade the instance type. RES-3's other benefit — zero-downtime `pm2 reload` via rolling workers — is nice but not worth the emergency-headroom cost at this scale.

---

## RES-4: PM2 log rotation (API — Ops)

**Status (2026-10-01):** ❔ not verifiable from the repos — nothing in them installs `pm2-logrotate`, the sprint table leaves this unchecked, and the API runbook says "Already rotated by RES-4" (`docs/runbook.md:340`). `pm2 conf pm2-logrotate` on each server settles it — `X-OPS-1`.

**Size:** XS (5 min)
**Command:**

```bash
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 5
pm2 set pm2-logrotate:compress true
```

**Why:** PM2 logs grow without bounds. On a t3.small with 8GB EBS, unchecked log growth will eventually fill the disk and crash the server. Log rotation keeps logs at a fixed size.

**How to verify:**

- Check `ls -la ~/.pm2/logs/` — log files should rotate when they hit 10MB.

---

## RES-5: Use `pm2 reload` instead of `pm2 restart` in deploys (Ops)

**Status (2026-10-01):** ✅ documented — the API runbook makes `pm2 reload dzzlo-oms` the daily driver and keeps `restart --update-env` for env changes (`docs/runbook.md:57-60,143-144,594-596`), with a server-by-server canary (`:125-167`); whether each deploy follows it is ❔.

**Size:** XS (update deploy script/habit)

**What:** Always use `pm2 reload dzzlo-oms` instead of `pm2 restart dzzlo-oms`.

**Why:** `restart` kills all workers simultaneously — every in-flight request is dropped. `reload` starts new workers first, waits for them to be ready, then gracefully kills old workers. Zero downtime.

**Prerequisites:** RES-2 (graceful shutdown) + RES-3 (cluster mode).

**Discussion — `pm2 restart` vs `pm2 reload`:**

**`pm2 restart`** — hard restart:

1. Sends `SIGINT`/`SIGKILL` to the worker immediately
2. Worker dies (in-flight requests dropped)
3. New worker starts
4. During startup gap (~1-3s), requests get connection errors

**`pm2 reload`** — graceful restart:

1. Sends `SIGTERM` to worker
2. The graceful shutdown handler (RES-2) runs: `server.close()` stops accepting new requests, in-flight requests finish, DB disconnects cleanly
3. Worker exits
4. New worker starts
5. With cluster mode (RES-3): new worker is ready _before_ old one dies → zero downtime

**What happens if you use `restart`:**

- In-flight requests dropped mid-execution → users see 502/connection reset
- MongoDB connections not closed cleanly → leaked connections lingering in Atlas until timeout
- Any pending writes mid-transaction could be inconsistent
- The RES-2 graceful shutdown work is bypassed

**What happens if you use `reload`:**

- In-flight requests complete
- DB closes cleanly
- With 1 instance: a brief downtime window still exists (new worker must start before serving), but no dropped requests
- With cluster mode: true zero-downtime

**When is `restart` still needed?** Only when `reload` can't do the job:

- **Changing env vars** — `reload` doesn't always pick up new `process.env`. Use `pm2 restart --update-env`.
- **Worker is hung/unresponsive** — graceful shutdown won't fire, `restart` force-kills it
- **PM2 config changes** (`ecosystem.config.js`) — sometimes needs a full restart
- **Memory/resource recovery** after a crash loop

**Recommendation:** `pm2 reload dzzlo-oms` is the daily driver — it serves the purpose with RES-2 in place, even without RES-3. Keep `pm2 restart` as the "break glass" tool for env var updates (`--update-env`) and stuck processes.

**Note on current state:** Even without RES-3 (cluster mode), adopt `pm2 reload` as the habit now. With RES-2 already done, `reload` at least lets in-flight requests finish and closes DB connections cleanly before the swap. When RES-3 is eventually enabled, no habit change is needed.

---

## RES-6: CloudWatch alarms — 5 critical alerts (AWS)

**Size:** S (1 hour in AWS Console)
**Where:** AWS Console — CloudWatch

**Status:** ❔ **2026-10-01:** console state is not verifiable from the repos. The API runbook names the 5xx alarm (`docs/runbook.md:38`) and describes two servers behind the ALB, one in an ASG and one static (`docs/runbook.md:265-279`), so "currently single-instance" below may be stale and the Healthy Hosts alarm may now apply — `X-OPS-1`. — _was:_ 4 of 5 alarms done. **Healthy Hosts Low deferred** — revisit once there is more than one host behind the ALB (currently single-instance, so the alarm would always be in-alarm).

**What:** Set up these 5 alarms with an SNS topic that emails you:

| Alarm               | Metric                    | Threshold       | Status      |
| ------------------- | ------------------------- | --------------- | ----------- |
| CPU High            | EC2 CPUUtilization        | > 80% for 5 min | Done        |
| ALB 5xx             | HTTPCode_Target_5XX_Count | > 10 in 5 min   | Done        |
| Healthy Hosts Low   | HealthyHostCount          | < 2             | Deferred    |
| Slow Response       | TargetResponseTime        | > 5 sec avg     | Done        |
| Status Check Failed | StatusCheckFailed         | > 0             | Done        |

**Why:** You currently have zero alarms. If MongoDB goes down, if your server crashes, if response times spike — nobody finds out until users complain. These 5 alarms cover the most critical failure modes.

**How to verify:**

- Each alarm should show state "OK" (green) in CloudWatch.
- Test the SNS topic by publishing a test message — verify email arrives.

---

### Steps to Complete RES-6: CloudWatch Alarms

**Prep (5 min):**

1. AWS Console → **SNS** → Create topic (e.g. `dzzlo-oms-alerts`) → Create email subscription → confirm from inbox.

**Create 5 alarms** (CloudWatch → Alarms → Create alarm → select metric → set threshold → notify SNS topic → name it):

| #   | Alarm Name                               | Namespace → Metric                           | Dimension                 | Condition                             |
| --- | ---------------------------------------- | -------------------------------------------- | ------------------------- | ------------------------------------- |
| 1   | `dzzlo-oms-prod-ec2-cpu-high`            | EC2 → `CPUUtilization`                       | InstanceId (your EC2)     | > 80% for 5 min (1 datapoint / 5 min) |
| 2   | `dzzlo-oms-prod-alb-5xx-elevated`        | ApplicationELB → `HTTPCode_Target_5XX_Count` | LoadBalancer              | Sum > 10 in 5 min                     |
| 3   | `dzzlo-oms-prod-alb-healthy-hosts-low`   | ApplicationELB → `HealthyHostCount`          | TargetGroup, LoadBalancer | Avg < 2 for 1 min _(deferred — single-host setup)_ |
| 4   | `dzzlo-oms-prod-alb-response-slow`       | ApplicationELB → `TargetResponseTime`        | LoadBalancer              | Avg > 5 sec for 5 min                 |
| 5   | `dzzlo-oms-prod-ec2-status-check-failed` | EC2 → `StatusCheckFailed`                    | InstanceId                | Sum > 0 for 1 min                     |

For each: Actions → **"In alarm"** → send to `dzzlo-oms-alerts` SNS topic.

**Verify:**

- All 5 alarms show green **OK** state.
- SNS → topic → Publish test message → confirm email arrives.
- Optional: temporarily lower CPU threshold to 1% to confirm alarm fires and emails, then reset to 80%.

**Tip:** Use a missing-data treatment of `notBreaching` for ALB 5xx (no traffic ≠ problem) and `breaching` for `StatusCheckFailed` (missing data on EC2 = bad).

---

**Alarm names & descriptions:**

Naming convention: `{app}-{env}-{resource}-{condition}` — keeps alarms grouped and scannable in the CloudWatch list, and makes the SNS email subject self-explanatory. CloudWatch renders markdown in the alarm description on the detail page and in the SNS email — use bold for the headline condition, inline code for metrics/commands, and a runbook link so on-call has next steps in one click.

### 1. `dzzlo-oms-prod-ec2-cpu-high`

```md
**EC2 CPU > 80% for 5 min.**

Sustained high CPU indicates a **runaway process**, **expensive query**, or **undersized instance**.
If ignored, the event loop stalls and requests start timing out.

- Check: `pm2 monit`, `top`, recent deploys
- Metric: `AWS/EC2` → `CPUUtilization`
- Runbook: `docs/runbook.md#cpu-high`
```

### 2. `dzzlo-oms-prod-alb-5xx-elevated`

```md
**ALB target 5xx > 10 in 5 min.**

Backend errors are reaching users — typically **crashes**, **unhandled exceptions**, or **upstream failures** (MongoDB, 2Factor.in).

- Check: `pm2 logs --err`, recent deploys (`git log --oneline -10`)
- Metric: `AWS/ApplicationELB` → `HTTPCode_Target_5XX_Count`
- Runbook: `docs/runbook.md#5xx-errors`
```

### 3. `dzzlo-oms-prod-alb-healthy-hosts-low` _(deferred — revisit when running >1 host)_

```md
**Healthy hosts < 2 in target group.**

Running _below redundancy_ — the next failure causes a **full outage**.

- Check: ASG activity, EC2 health checks, target group health
- Possible causes: failing deploy, bad health-check path, instance crash
- Metric: `AWS/ApplicationELB` → `HealthyHostCount`
- Runbook: `docs/runbook.md#healthy-hosts-low`
```

### 4. `dzzlo-oms-prod-alb-response-slow`

```md
**ALB `TargetResponseTime` avg > 5 sec.**

Users are seeing _severe latency_. Most common causes:

1. Slow MongoDB queries (missing index)
2. Blocked event loop (sync operation in hot path)
3. Saturated connection pool

- Check: Atlas → Profiler, `pm2 logs`, ALB access logs
- Metric: `AWS/ApplicationELB` → `TargetResponseTime`
- Runbook: `docs/runbook.md#slow-response`
```

### 5. `dzzlo-oms-prod-ec2-status-check-failed`

```md
**EC2 `StatusCheckFailed` > 0.**

Instance-level failure — AWS cannot reach the instance (**hardware**, **network**, or **OS**).
_Unrecoverable without intervention._

- Action: replace instance via ASG, or reboot from EC2 Console
- Metric: `AWS/EC2` → `StatusCheckFailed`
- Runbook: `docs/runbook.md#status-check-failed`
```

---

## RES-7: Atlas alerts — 3 database alarms (MongoDB Atlas)

**Status (2026-10-01):** ❔ Atlas console — not verifiable from the repos; the API runbook points to this doc's Atlas procedures (`docs/runbook.md:212`). The v4 pool settings assume an M10 with 1,500 connections (`helpers/db_conn.js:7-22`).

**Size:** XS (15 min in Atlas Console)
**Where:** MongoDB Atlas Console — Alerts

**What:**

1. **Connections > 80% of limit** — catches connection leaks
2. **Disk usage > 80%** — catches unbounded collection growth (logs, errors)
3. **Replication lag > 10 seconds** (if on dedicated tier) — catches replication issues

**Why:** Same reason as RES-6. Database problems are invisible until they cascade to the application layer. These alerts catch problems at the source.

**Optional bonus alerts (still free, high-signal):**

- **Query Targeting: Scanned Objects / Returned > 1000** — catches missing indexes before they tank performance. Collection scans show up here first.
- **Primary Election (any)** — catches failovers you'd otherwise miss. A silent failover can cause a few seconds of write errors; you want to know it happened.
- **Page Faults > 10/sec** (WiredTiger) — working set has exceeded RAM. Precursor to slow queries and the need to scale up the tier.
- **CPU Usage > 80% for 10 min** — sustained high CPU usually means an expensive query or missing index, not real load.

---

## RES-8: Create emergency runbook (Documentation)

**Status (2026-10-01):** ✅ done — API `docs/runbook.md` (627 lines; `60b539f` 2026-04-15, `8c70aa7` 2026-05-03) covers the five failure cases below plus disk-full and the two-server setup; its own follow-up list (`:615-627`) is still open.

**Size:** S (1 hour)
**File:** New `docs/runbook.md`

**What:** Document the procedures for common failures:

- 502/504 errors — how to check PM2, MongoDB, restart
- Bad deploy rollback — git checkout, pm2 reload
- MongoDB Atlas down — what to do (wait), status page URL
- Server unreachable — check EC2, ASG activity
- OTP/SMS not working — check 2Factor.in status, error logs

**Why:** Bus factor of 1. If you're unavailable, someone else (or future-you at 3am) needs to know what to check and in what order. A runbook turns a panic into a checklist.

**Atlas alert response procedures (from RES-7):**

### Alert: Connections > 80% of limit

1. **Check current connections** — Atlas → Metrics → `Connections` chart. Is it climbing steadily (leak) or spiking (load)?
2. **If climbing steadily (leak):**
   - SSH to EC2 → `pm2 logs` — look for "MongoNetworkError" or unclosed cursors.
   - Check recent deploys (`git log --oneline -10`) for new DB code that may not be closing connections.
   - Short-term fix: `pm2 reload all` to reset the pool.
3. **If spiking (real load):**
   - Check ALB request count — is traffic actually up?
   - Consider scaling Atlas tier (M10 → M20) if sustained.
4. **Escalation:** If connections hit 100% → app will throw "connection pool exhausted" → `pm2 reload all` immediately, then investigate.

### Alert: Disk usage > 80%

1. **Identify the biggest collections** — Atlas → Collections tab, sort by Size.
2. **Usual suspects:** `logs`, `errors`, `sessions`, `otps`, audit trails.
3. **Immediate relief:**
   - Drop old data: `db.logs.deleteMany({ createdAt: { $lt: ISODate("YYYY-MM-DD") } })`
   - Or add a TTL index: `db.logs.createIndex({ createdAt: 1 }, { expireAfterSeconds: 2592000 })` (30 days).
4. **Medium-term:** Scale storage in Atlas (cluster → Configuration → Storage).
5. **Escalation:** At 95%+ Atlas throttles writes → app writes start failing silently. Act before then.

### Alert: Replication lag > 10 seconds

1. **Check Atlas status page** — https://status.mongodb.com/ — known incident?
2. **Check the secondary's metrics** — Atlas → Metrics → select secondary node → look at `Opcounters`, `Network`, `CPU`.
3. **Common causes:**
   - Long-running write on primary (bulk import, schema migration).
   - Network blip between AZs.
   - Secondary undersized for write volume.
4. **Action:** Usually resolves on its own in 1–2 min. If persistent > 5 min → open Atlas support ticket. Do not manually failover.
5. **Read concern impact:** Reads with `readPreference: secondary` may return stale data during the lag window — note this for any affected features.

---

## Summary

| Task                      | Size | Impact                              | Risk |
| ------------------------- | ---- | ----------------------------------- | ---- |
| RES-1: Deep health check  | XS   | ALB detects real failures           | Zero |
| RES-2: Graceful shutdown  | S    | No dropped requests on deploy       | Low  |
| RES-3: PM2 cluster mode   | S    | 2x throughput, zero-downtime reload | Low  |
| RES-4: PM2 log rotation   | XS   | Prevents disk-full crash            | Zero |
| RES-5: `pm2 reload` habit | XS   | Zero-downtime deploys               | Zero |
| RES-6: CloudWatch alarms  | S    | Know when things break              | Zero |
| RES-7: Atlas alerts       | XS   | Know when DB is stressed            | Zero |
| RES-8: Emergency runbook  | S    | Bus factor reduction                | Zero |

**Recommended order:** RES-1 → RES-4 → RES-2 → RES-3 → RES-5 → RES-6 → RES-7 → RES-8

---

## New tasks — from the app v2 / API v4 review (2026-10-01)

**What the v4 work added here** (API-3, now on master). Every v4 read has a server time limit — 5 s a find, 8 s an aggregate — answered as 503 `QUERY_TIMEOUT` (`api_v4/lib/limits.js:23`, `api_v4/lib/errors.js:40-43,110-113`); both Mongo pools cap at 75 sockets and give up after a 3 s wait, answered as 503 `UNAVAILABLE` (`helpers/db_conn.js:44-47`, `api_v4/lib/errors.js:95-117`); `/api/v4/screens/*` allows 300 requests a minute per user, answered as 429 `RATE_LIMITED` with `Retry-After` (`api_v4/lib/rateLimit.js:30-52`); server selection stays at the driver's 30 s to ride out an election (`helpers/db_conn.js:35-40`). The numbers and reasons are in the API's `docs/v4-performance.md`.

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-OPS-1 | 🆕 ❔ Settle the production topology and align what depends on it: the RES-6 status, the `trust proxy` hop count, per-process limits and caches, RES-4 | This plan says single instance (RES-6 status); the API runbook has one ASG and one static server behind the ALB (`docs/runbook.md:265-279`), and the v4 limiter and pool comments say one PM2 fork process on each of two servers (`api_v4/lib/rateLimit.js:23-26`, `helpers/db_conn.js:18-20`, `docs/v4-performance.md:130-133`). So the in-memory v4 limiter allows up to 600 a minute per user; caches and busts are per server; `trust proxy` is 1 hop (`dzzlo_oms.js:57`) behind ALB + nginx (`docs/runbook.md:4,341`), and the hop count decides which address IP-keyed limits see (depends on the nginx config, not in the repo); the runbook says "Already rotated by RES-4" (`docs/runbook.md:340`). The user confirms | API (ops) | S | — |
| X-APP-1 | 🆕 App copy (en + hi) for `QUERY_TIMEOUT` (503) and `RATE_LIMITED` (429), and keep them out of the global retry | The API sends both (`api_v4/lib/errors.js:40-49`, `api_v4/lib/rateLimit.js:51`); the app catalogue has 8 v4 codes and 3 company codes, not these (`src/utils/errorCodes.js:18-56`), so the server's English text shows; the retry short-circuits only 4xx (`src/store/apis/createApi.js:96-108`), so a 503 `QUERY_TIMEOUT` — the server shedding load — is attempted three times, 2 s and 4 s apart (`src/store/apis/retryBackoff.js:4-7`); the same holds for a pool-wait `UNAVAILABLE` | app | S | — |
| T01-N2 | 🆕 Make RES-2's graceful shutdown hold under PM2's defaults | PM2 stops and reloads with `SIGINT` and kills after 1.6 s unless `kill_timeout` is set (PM2's documented defaults, not repo code); `ecosystem.config.js` sets neither `kill_timeout` nor `kill_signal`; `helpers/db_conn.js:83-89` adds a second `SIGINT` handler that disconnects Mongo and calls `process.exit(0)` without waiting for `server.close` (`dzzlo_oms.js:145-165`) — in-flight requests can still be dropped (inferred, not observed) | API | XS | — |
| T01-N4 | 🆕 The SMS-provider client fails safely — request errors caught, replies parsed defensively, calls time out — so a provider outage cannot take the API process down | The 2Factor client predates this (`api_v3/services/order_msts.js`, `api_v3/controllers/auth/SMSOTP/template/index.js`); the runbook lists a hanging external API as a 504 cause (`docs/runbook.md:33`). The tests' live-call flake is tracked in tasks_12 | API | S | Do with `X-SEC-3` ([02](./02-security-hardening.md)) |

The full list is in [00-overview](./00-overview.md).
