# Session 7: Monitoring & Alerting

> Phase 4 — Operations | 2 hours | Review: 15 min

## What You'll Learn

- The Four Golden Signals from Google's SRE handbook and how they map to your system
- The difference between metrics worth monitoring and conditions worth alerting on
- How to set up CloudWatch alarms for your EC2 instances and ALB
- How to configure Atlas alerts for your MongoDB cluster
- Whether your custom `logs` collection (1.4M records) is worth keeping or should move to CloudWatch Logs

## Why This Matters for DZZLO-OMS

Right now you have **zero alarms** configured. Zero CloudWatch alarms, zero Atlas alerts, zero automated notifications of any kind. Your `/healthcheck` endpoint exists and the ALB pings it, but if it starts failing, no human finds out — the ALB just marks the target unhealthy and you discover the problem when users complain.

Here is a concrete picture of what you're missing:

- **MongoDB goes down** -> Express starts returning timeout errors -> users see failures -> someone calls you -> you SSH in and check PM2 logs -> you realize Mongo has been down for 40 minutes. With a single alarm on ALB 5xx responses, you'd know in 5 minutes.
- **SMS delivery via 2Factor.in fails** -> OTP messages stop arriving -> users can't log in -> support tickets pile up -> you find out hours later. Your code in `api_v2/controllers/methods/2Factor/index.js` has no error reporting beyond writing to the `errors` collection, and nobody monitors that collection.
- **OneSignal push notifications fail silently** -> `api_v3/controllers/App/notification.js` fires and forgets -> users miss order updates -> you never know unless someone tells you.
- **EC2 instance runs out of CPU credits** (you're on t3.small/t3.micro burstable instances) -> performance degrades gradually -> everything feels "slow" but nothing breaks -> you have no visibility.
- **Your `logs` collection has 1.4 million records in MongoDB** -> it's taking up storage and IOPS on Atlas -> nobody queries it regularly -> it's costing you money for data that provides no operational value in its current form.

The gap is simple: you have data (PM2 logs, MongoDB `logs` collection, MongoDB `errors` collection, the healthcheck endpoint) but no system that watches that data and tells you when something is wrong. By the end of this session, you'll have 8 working alarms covering the most critical failure modes.

## Hour 1 — Concepts (60 min)

### Step 1: The Four Golden Signals (20 min)

**Read:** [Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — Chapter 6 of the Google SRE book.

Read the full chapter, but **focus on the "The Four Golden Signals" section.** The four signals are:

1. **Latency** — how long requests take to serve. Distinguish between successful requests and failed requests (a fast 500 error shouldn't improve your latency metrics).
2. **Traffic** — how much demand is hitting your system. For DZZLO-OMS, this is HTTP requests per second to your ALB.
3. **Errors** — the rate of failed requests. This includes explicit failures (HTTP 5xx), implicit failures (a 200 response that returns wrong data), and policy failures (any response slower than a threshold you set).
4. **Saturation** — how "full" your service is. For you, this means EC2 CPU utilization, MongoDB connection count relative to the limit, and disk usage on Atlas.

**Map each signal to DZZLO-OMS:**


| Signal     | What to measure                            | Where the data lives today                                    | Current visibility                                     |
| ---------- | ------------------------------------------ | ------------------------------------------------------------- | ------------------------------------------------------ |
| Latency    | Response time per request                  | `logs` collection (`response_time` field) and ALB access logs | None — you'd have to query MongoDB manually            |
| Traffic    | Requests per second / minute               | ALB metrics (RequestCount) and `logs` collection              | None — CloudWatch has it but nobody looks              |
| Errors     | 5xx responses, unhandled exceptions        | ALB metrics (HTTPCode_Target_5XX_Count), `errors` collection  | None — errors collection exists but nobody monitors it |
| Saturation | CPU %, memory %, MongoDB connections, disk | CloudWatch (EC2), Atlas metrics                               | None — all available but no alarms configured          |


The key takeaway: you already have most of this data being generated. The problem is that nothing watches it and nothing alerts you.

**Also skim:** The [SRE Book Table of Contents](https://sre.google/sre-book/table-of-contents/) to see where monitoring fits in the broader SRE picture. Chapters 4 (Service Level Objectives), 6 (Monitoring), and 11 (Being On-Call) form a coherent story. You don't need to read 4 and 11 now, but know they exist.

### Step 2: What to Monitor vs. What to Alert On (20 min)

Not everything that's worth monitoring deserves an alarm. This is the most common mistake: you set up 50 alarms, get alert fatigue in a week, and start ignoring all of them.

**The rule of thumb from the SRE book:** Every alert should require a human to take action. If the alert fires and the correct response is "do nothing, it'll fix itself," remove that alert.

**Three tiers for DZZLO-OMS:**

**Tier 1 — Alert immediately (email/SMS):** Something is broken or about to break. A human must act.

- ALB returning 5xx errors (your app is crashing)
- No healthy targets behind the ALB (your app is completely down)
- EC2 status check failed (instance is unreachable)
- MongoDB connections approaching the limit (about to hit a hard wall)
- Atlas disk usage > 80% (you will run out of space)

**Tier 2 — Alert on a daily digest or dashboard check:** Something is degraded but not urgent.

- ALB response time trending upward
- EC2 CPU sustained above 70%
- MongoDB replication lag (if you have a replica set)
- Error rate above normal but not spiking

**Tier 3 — Monitor on a dashboard, never alert:** Useful for debugging and trend analysis, but not actionable in real time.

- Request count per minute
- Response time percentiles (p50, p95, p99)
- Individual endpoint latencies
- MongoDB query execution times

**Exercise:** Look at your `errors` collection schema in `models/errors.js`:

```js
{
  error_res: { type: Mixed },   // the error object
  error_time: { type: String },  // timestamp as string
}
```

This captures errors but provides no notification. Ask yourself: if the error rate doubled tomorrow, how would you know? Answer: you wouldn't, not until users told you. That's the gap this session closes.

### Step 3: CloudWatch Basics for EC2 + ALB (20 min)

**Read:** [Creating CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)

Read through the "Creating a CloudWatch alarm" section. Focus on understanding these concepts:

**Key concepts you need:**

1. **Namespace** — the category of metrics. You'll use `AWS/EC2` for instance metrics and `AWS/ApplicationELB` for ALB metrics.
2. **Metric** — the specific measurement (e.g., `CPUUtilization`, `HTTPCode_Target_5XX_Count`).
3. **Statistic** — how the metric is aggregated over the period (Average, Sum, Maximum).
4. **Period** — the time window for each data point (e.g., 300 seconds = 5 minutes).
5. **Threshold** — the value that triggers the alarm.
6. **Evaluation periods** — how many consecutive periods must breach the threshold before the alarm fires. Setting this to 1 means "fire immediately on first breach." Setting it to 3 means "fire only if it's been bad for 3 consecutive periods."
7. **SNS Topic** — where the alarm sends its notification. You'll create one SNS topic and subscribe your email to it.

**The metrics CloudWatch gives you for free (no agent needed):**


| Metric                    | Namespace          | What it measures               | Period |
| ------------------------- | ------------------ | ------------------------------ | ------ |
| CPUUtilization            | AWS/EC2            | CPU % usage                    | 5 min  |
| StatusCheckFailed         | AWS/EC2            | Instance reachability          | 1 min  |
| RequestCount              | AWS/ApplicationELB | Total requests                 | 1 min  |
| HTTPCode_Target_5XX_Count | AWS/ApplicationELB | 5xx from your targets          | 1 min  |
| TargetResponseTime        | AWS/ApplicationELB | Time to first byte from target | 1 min  |
| HealthyHostCount          | AWS/ApplicationELB | Targets passing health checks  | 1 min  |
| UnHealthyHostCount        | AWS/ApplicationELB | Targets failing health checks  | 1 min  |


**What CloudWatch does NOT give you for free:** Memory utilization, disk usage on EC2, and custom application metrics. You'd need the CloudWatch Agent for memory/disk, and custom `PutMetricData` calls for application-level metrics. You don't need these today — the free metrics cover your critical alarms.

## Hour 2 — Hands-On: Set Up 8 Alarms (60 min)

### Step 4: Set Up 5 CloudWatch Alarms (30 min)

You'll create one SNS topic first, then five alarms. All done through the AWS Console.

#### Prerequisite: Create an SNS Topic

1. Open the **AWS Console** -> **SNS** (Simple Notification Service)
2. Click **Topics** -> **Create topic**
3. Type: **Standard**
4. Name: `dzzlo-oms-critical-alarms`
5. Click **Create topic**
6. On the topic detail page, click **Create subscription**
7. Protocol: **Email**
8. Endpoint: your email address
9. Click **Create subscription**
10. **Check your email** and confirm the subscription (you must click the confirmation link or alarms won't reach you)

#### Alarm 1: EC2 CPU > 80% for 5 Minutes

This catches runaway processes, infinite loops, or a spike in traffic that your t3 instance can't handle.

1. Open **CloudWatch** -> **Alarms** -> **Create alarm**
2. Click **Select metric**
3. Navigate: **AWS/EC2** -> **Per-Instance Metrics**
4. Find your instance, select `CPUUtilization`
5. Click **Select metric**
6. Configure:
  - Statistic: **Average**
  - Period: **5 minutes**
  - Threshold type: **Static**
  - Whenever CPUUtilization is: **Greater than 80**
7. Additional configuration:
  - Datapoints to alarm: **1 out of 1** (fire on first breach)
  - Missing data treatment: **Treat missing data as breaching** (if we stop getting CPU data, something is very wrong)
8. Actions:
  - Alarm state trigger: **In alarm**
  - Select SNS topic: `dzzlo-oms-critical-alarms`
9. Name: `dzzlo-oms-ec2-cpu-high`
10. Click **Create alarm**

**Repeat for your second EC2 instance** (the t3.micro). Name it `dzzlo-oms-ec2-micro-cpu-high`.

> **Why 80% and not 90%?** On burstable t3 instances, sustained high CPU burns through your CPU credit balance. By the time you hit 90%, you may have already exhausted credits and the instance is being throttled. 80% gives you a window to investigate before performance degrades.

#### Alarm 2: ALB 5xx Count > 10 in 5 Minutes

This catches application crashes, unhandled exceptions, and MongoDB connection failures — the situations that currently go unnoticed until users complain.

1. **CloudWatch** -> **Alarms** -> **Create alarm** -> **Select metric**
2. Navigate: **AWS/ApplicationELB** -> **Per AppELB Metrics**
3. Find your ALB, select `HTTPCode_Target_5XX_Count`
4. Configure:
  - Statistic: **Sum**
  - Period: **5 minutes**
  - Threshold: **Greater than 10**
5. Additional configuration:
  - Missing data treatment: **Treat missing data as not breaching** (no 5xx data means no 5xx errors — that's good)
6. Actions: select `dzzlo-oms-critical-alarms`
7. Name: `dzzlo-oms-alb-5xx-high`
8. Create.

> **Why 10 and not 1?** A single 5xx can happen for transient reasons (a MongoDB connection hiccup, a momentary timeout). 10 in 5 minutes means something is systematically wrong. Adjust this down later if you find your baseline is truly zero 5xx errors.

#### Alarm 3: ALB Healthy Host Count < 2

This is your "the app is partially or fully down" alarm. You run 2 EC2 instances behind the ALB. If healthy hosts drops below 2, you've lost at least one instance.

1. **CloudWatch** -> **Alarms** -> **Create alarm** -> **Select metric**
2. Navigate: **AWS/ApplicationELB** -> **Per AppELB, per TG Metrics**
3. Find your target group, select `HealthyHostCount`
4. Configure:
  - Statistic: **Minimum**
  - Period: **1 minute** (you want to know fast)
  - Threshold: **Less than 2**
5. Additional configuration:
  - Datapoints to alarm: **2 out of 3** (require 2 consecutive bad readings out of 3 to avoid flaps during deployments)
  - Missing data treatment: **Treat missing data as breaching**
6. Actions: select `dzzlo-oms-critical-alarms`
7. Name: `dzzlo-oms-alb-healthy-hosts-low`
8. Create.

> **Note:** During deployments, healthy host count may briefly dip. The "2 out of 3" datapoint setting prevents false alarms during rolling deploys. If you're still getting false alarms during deploys, increase to "3 out of 5."

#### Alarm 4: ALB Target Response Time > 5 Seconds

This catches slow responses that technically succeed (HTTP 200) but indicate something is wrong — a slow MongoDB query, a hanging external API call (2Factor.in, OneSignal), or a resource bottleneck.

1. **CloudWatch** -> **Alarms** -> **Create alarm** -> **Select metric**
2. Navigate: **AWS/ApplicationELB** -> **Per AppELB Metrics**
3. Find your ALB, select `TargetResponseTime`
4. Configure:
  - Statistic: **Average**
  - Period: **5 minutes**
  - Threshold: **Greater than 5** (seconds)
5. Additional configuration:
  - Missing data treatment: **Treat missing data as not breaching**
6. Actions: select `dzzlo-oms-critical-alarms`
7. Name: `dzzlo-oms-alb-response-time-high`
8. Create.

> **Why 5 seconds?** Your typical request should complete in under 500ms. A 5-second average means something is drastically wrong. Once you have baseline data, tighten this to 2 seconds. The point today is to catch catastrophic slowdowns, not optimize p99 latency.

#### Alarm 5: EC2 Status Check Failed

This catches hardware failures, network issues, and instances that have become unreachable. AWS runs these checks automatically every minute.

1. **CloudWatch** -> **Alarms** -> **Create alarm** -> **Select metric**
2. Navigate: **AWS/EC2** -> **Per-Instance Metrics**
3. Find your instance, select `StatusCheckFailed`
4. Configure:
  - Statistic: **Maximum**
  - Period: **1 minute**
  - Threshold: **Greater/Equal than 1**
5. Additional configuration:
  - Datapoints to alarm: **2 out of 3**
  - Missing data treatment: **Treat missing data as breaching**
6. Actions: select `dzzlo-oms-critical-alarms`
7. Name: `dzzlo-oms-ec2-status-check-failed`
8. Create.

**Repeat for your second EC2 instance.**

**Checkpoint:** You should now have 5 CloudWatch alarms (7 if you count the duplicates for both EC2 instances). Go to **CloudWatch** -> **Alarms** and verify they all show state **OK** (green). If any shows **INSUFFICIENT_DATA**, wait a few minutes for data to populate.

### Step 5: Set Up 3 Atlas Alerts (20 min)

Atlas has its own alerting system, separate from CloudWatch. These cover what CloudWatch can't see — the internals of your MongoDB cluster.

**Read first:** [Configure and Resolve Alerts](https://www.mongodb.com/docs/atlas/alerts/) — skim the page to understand how Atlas alerts work.

#### Atlas Alert 1: Connections > 80% of Limit

When your connection count approaches the limit, new connections get rejected and your app starts throwing errors. Your Express app uses Mongoose with a default pool size of 5 per process. With PM2 running 1 process per instance and 2 instances, you use roughly 10 connections. Your Atlas tier has a connection limit (check your tier — M10 allows 350, M0/M2/M5 allows 500). This alert catches connection leaks or misconfigured pool sizes.

1. Log in to **MongoDB Atlas** -> select your project
2. Click **Alerts** in the left sidebar
3. Click **Create Alert** (or **Add Alert** depending on your Atlas version)
4. Configure:
  - Alert target: **Host**
  - Condition: **Connections** is greater than **80%** of the configured limit
  - Notification: **Email** -> your email address
5. Save.

#### Atlas Alert 2: Disk Usage > 80%

Your `logs` collection has 1.4M records. If you're on a shared tier (M0/M2/M5), you have limited storage. Even on a dedicated tier, disk filling up means writes start failing.

1. **Alerts** -> **Create Alert**
2. Configure:
  - Alert target: **Host**
  - Condition: **Disk Partition % Used on Data Partition** is greater than **80%**
  - Notification: **Email** -> your email address
3. Save.

> **This alert ties directly to the decision in Step 6.** If your `logs` collection is a significant portion of your disk usage, this alarm will eventually fire because of it.

#### Atlas Alert 3: Replication Lag > 10 Seconds (if Replica Set)

If you're on a dedicated Atlas tier (M10+), you have a replica set. Replication lag means secondaries are falling behind the primary — reads from secondaries return stale data, and failover would lose recent writes.

1. **Alerts** -> **Create Alert**
2. Configure:
  - Alert target: **Replica Set**
  - Condition: **Replication Oplog Window** is less than **1 hour** (alternatively, **Replication Lag** is greater than **10 seconds**)
  - Notification: **Email** -> your email address
3. Save.

> **If you're on M0/M2/M5 (shared tier):** You don't control the replica set configuration, and Atlas manages replication for you. Skip this alert — the first two are more important for your tier. But know that you'd add this when you upgrade.

**Also explore:** Open the [Atlas Performance Advisor](https://www.mongodb.com/docs/atlas/performance-advisor/) page and check if it's available for your tier. The Performance Advisor suggests indexes based on your actual slow queries — it's directly useful and worth bookmarking. On shared tiers it may not be available, but on M10+ it's included.

### Step 6: Decision — Keep the `logs` Collection or Move to CloudWatch Logs? (10 min)

Your `logs` collection in MongoDB stores 1.4 million records. Each record looks like this (from `models/logs.js`):

```js
{
  method: String,        // "GET", "POST", etc.
  url: String,           // the request path
  api_v: String,         // API version
  response_time: Number, // milliseconds
  status: Number,        // HTTP status code
  statusMessage: String,
  content_str_length: Number,
  timeIST: String,       // timestamp as string
  user: Mixed,           // user info from JWT decode + DB lookup
  appInfo: Mixed,        // app metadata
}
```

**The problem:** This data lives in your production database. Every API request writes a log document, which means:

- Extra write load on MongoDB for every single request
- Storage consumed on your Atlas tier (directly relevant to the disk usage alert you just set up)
- The data is only useful if someone queries it manually, and nobody does

**Three options:**


| Option                         | Effort    | Cost                                         | Benefit                                                                    |
| ------------------------------ | --------- | -------------------------------------------- | -------------------------------------------------------------------------- |
| **A: Keep as-is**              | None      | Ongoing storage cost, ongoing write overhead | Familiar, already works                                                    |
| **B: Add a TTL index**         | 5 minutes | Reduces storage, keeps write overhead        | Logs auto-delete after N days, keeps recent data queryable                 |
| **C: Move to CloudWatch Logs** | 2-4 hours | CloudWatch Logs ingestion cost (~$0.50/GB)   | Proper log search, dashboards, metric filters, alarms based on log content |


**Recommendation for right now: Option B.**

Add a TTL index to auto-expire logs older than 30 days. This is a 5-minute fix that immediately stops unbounded growth:

```js
// Run this in mongosh connected to your Atlas cluster:
db.logs.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 2592000 }) // 30 days
```

This works because your schema has `{ timestamps: true }`, which means Mongoose adds a `createdAt` field to every document.

**Do the same for the `errors` collection:**

```js
db.errors.createIndex({ "createdAt": 1 }, { expireAfterSeconds: 2592000 }) // 30 days
```

**Option C (CloudWatch Logs) is the right long-term answer** but it requires replacing your logging middleware with one that writes to CloudWatch instead of (or in addition to) MongoDB. That's a meaningful code change — save it for when you're ready to invest a session in centralized logging. The TTL index solves the immediate storage problem today.

**Exercise:** Check your current storage usage in Atlas. Go to your cluster -> **Metrics** -> look at **Data Size** and **Storage Size**. How much of it is the `logs` collection? Run this in mongosh:

```js
db.logs.stats().size       // data size in bytes
db.logs.stats().storageSize // storage on disk in bytes
db.logs.count()            // total documents
```

If `logs` is more than 30% of your total data size, Option B becomes urgent — set up that TTL index before moving on.

## 15-Minute Review — Verify Your Alarms

You should now have **8 alarms** running (5 CloudWatch + 3 Atlas). Verify each one.

### CloudWatch Verification

1. Open **CloudWatch** -> **Alarms** -> **All alarms**
2. Confirm these 5 alarms exist and show state **OK** (green):


| #   | Alarm Name                          | Expected State |
| --- | ----------------------------------- | -------------- |
| 1   | `dzzlo-oms-ec2-cpu-high`            | OK             |
| 2   | `dzzlo-oms-alb-5xx-high`            | OK             |
| 3   | `dzzlo-oms-alb-healthy-hosts-low`   | OK             |
| 4   | `dzzlo-oms-alb-response-time-high`  | OK             |
| 5   | `dzzlo-oms-ec2-status-check-failed` | OK             |


1. **Test the SNS notification:** Go to the `dzzlo-oms-critical-alarms` SNS topic and click **Publish message**. Send a test message. Confirm you receive the email. If you don't receive it, check that you confirmed the subscription (Step 4 prerequisite).

### Atlas Verification

1. Open **Atlas** -> **Alerts**
2. Confirm these 3 alerts are active:


| #   | Alert                           | Expected State      |
| --- | ------------------------------- | ------------------- |
| 1   | Connections > 80% of limit      | Active (no trigger) |
| 2   | Disk usage > 80%                | Active (no trigger) |
| 3   | Replication lag (if applicable) | Active (no trigger) |


### Review Questions

Answer these five questions. If you can't answer one, go back and check.

1. **Which of the Four Golden Signals does your healthcheck endpoint cover?** Hint: the ALB checks it for traffic routing, but does the healthcheck tell you anything about latency, error rate, or saturation? (Answer: it covers almost nothing — it checks that the process is alive and MongoDB is connected, but that's binary. It tells you nothing about how fast or how well the system is performing.)
2. **Your `logs` collection records `response_time` for every request. Could you build a latency alarm from this data?** How would you query for "average response time in the last 5 minutes > 5 seconds"? (Think about why this is harder than the ALB `TargetResponseTime` alarm you just set up — you'd need to continuously query MongoDB, which is what CloudWatch Logs Insights would solve for you.)
3. **If your 2Factor.in SMS API starts returning errors, which of your 8 new alarms would fire?** (Answer: the ALB 5xx alarm would fire only if your code propagates the error as a 500 response. If your code catches the SMS error and returns a 200 with an error message in the body, none of your alarms would catch it. This is a gap you'll want to close later — either by making SMS failures return 5xx, or by adding a custom CloudWatch metric for SMS failure rate.)
4. **What's the difference between "Treat missing data as breaching" and "Treat missing data as not breaching"?** Why did you use different settings for different alarms? (Think about what "missing data" means for each metric. Missing CPU data means the instance might be down — that's bad. Missing 5xx data means there were zero 5xx errors — that's good.)
5. **You set the healthy host count alarm to "2 out of 3" datapoints. What would happen if you set it to "1 out of 1" and then deployed your code?** (Answer: during a rolling deploy, the ALB briefly shows fewer healthy hosts while the new code starts up. A "1 out of 1" alarm would fire on every deployment, causing alert fatigue and teaching you to ignore this alarm — exactly what the SRE book warns against.)

## What's Still Missing (Future Sessions)

This session set up reactive alerting — you get notified after something goes wrong. Here's what you'll want eventually:

- **Centralized logging** (CloudWatch Logs or a dedicated logging service) — replace the MongoDB `logs` collection with proper structured logging
- **APM (Application Performance Monitoring)** — per-endpoint latency tracking, database query tracing, dependency maps (tools: AWS X-Ray, Datadog, New Relic)
- **Dashboards** — a single CloudWatch dashboard showing all four golden signals at a glance
- **Alerting for third-party dependencies** — SMS delivery rate, push notification delivery rate, payment gateway health
- **Runbooks** — for each alarm, a documented procedure for what to check and what to do (covered in Session 8)
- **Graceful degradation** — when MongoDB is slow, return cached data instead of timing out; when SMS fails, queue and retry instead of silently dropping

## Resources


| Resource                                         | URL                                                                                                                                                                                | Used In    |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Google SRE Book — Monitoring Distributed Systems | [https://sre.google/sre-book/monitoring-distributed-systems/](https://sre.google/sre-book/monitoring-distributed-systems/)                                                         | Step 1     |
| Google SRE Book — Table of Contents              | [https://sre.google/sre-book/table-of-contents/](https://sre.google/sre-book/table-of-contents/)                                                                                   | Step 1     |
| CloudWatch Alarms Documentation                  | [https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html) | Steps 3, 4 |
| MongoDB Atlas Alerts                             | [https://www.mongodb.com/docs/atlas/alerts/](https://www.mongodb.com/docs/atlas/alerts/)                                                                                           | Step 5     |
| Atlas Performance Advisor                        | [https://www.mongodb.com/docs/atlas/performance-advisor/](https://www.mongodb.com/docs/atlas/performance-advisor/)                                                                 | Step 5     |


