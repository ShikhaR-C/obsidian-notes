# Session 9: Asynchronous Processing & Message Queues

> Phase 3 — Reliability & Scale | 2 hours | Review: 15 min

## What You'll Learn

- The difference between synchronous and asynchronous processing, and when synchronous becomes a liability
- Message queue fundamentals: producer/consumer, delivery guarantees, and failure handling
- How BullMQ works as a Node.js job queue on Redis, and when it earns its place in a stack
- Event-driven architecture patterns and how they differ from request/response
- Which operations in your own system are candidates for async processing and in what order to tackle them

## Why This Matters for DZZLO-OMS

Your system does several things during a request that the user does not need to wait for. Three stand out immediately.

**SMS OTP via 2Factor.in** (`api_v3/controllers/auth/SMSOTP/template/index.js`) — `sendLoginSMSToUserPhone` uses `http.request` to call `2factor.in` inline during login. The function is marked `async` and the caller awaits it. If 2Factor takes 3 seconds to respond, the user stares at a spinner for 3 seconds before seeing "OTP sent." If 2Factor is down, the request fails entirely.

**Push notifications via OneSignal** (`api_v3/controllers/App/notification.js`) — `sendNotifyToExternalIDs` fires an HTTP POST to OneSignal. The caller `await`s it in places like `dealer_custs.js` line 1366. If OneSignal is slow, the business operation (like linking a new customer) is slow. If OneSignal returns an error, the catch block logs it and moves on — but there is no retry. The notification is lost.

**Email via Nodemailer + AWS SES** (`helpers/sendEmail.js`) — `await transporter.sendMail(message)` is fully synchronous within the request handler. The `yearAccEmail` function in `dealer_custs.js` generates an Excel report and emails it in the same request cycle. If SES is slow, the API response is slow.

Beyond these, you have structural gaps:

- **`cr_bill_period`** on `dealer_custs` supports `INSTANT`, `DAILY`, `WEEKLY`, and `MONTHLY` billing. But there is no scheduler, no cron, no background job to trigger billing at those intervals. It is done manually.
- **Invoice PDF generation** (`api_v3/services/invoice/htmlPdf/fileBuffer.js`) uses `html-pdf` to render HTML to a buffer synchronously within the request. For a single invoice this is fast, but batch generation would block the event loop.
- **The `logging()` middleware** (`helpers/middlewares.js` line 169) calls `Logs.create()` with `.catch()` — fire-and-forget without `await`. This is a pragmatic choice, but if the write fails, the log entry is silently lost.
- **Socket.io** code in the codebase is entirely commented out — an earlier attempt at real-time that was removed. A queue-based architecture would give you the reliability that raw Socket.io lacked.

At 130 orders/day, none of this is causing outages. But the patterns are wrong in principle: your request handler's response time is coupled to third-party API latency, and there is no mechanism to retry failed external calls. This session teaches you the architecture that fixes both problems.

---

## Hour 1 — Concepts (60 min)

### Step 1: Synchronous vs Asynchronous Processing (15 min)

**Read:** [System Design Primer — Asynchronism](https://github.com/donnemartin/system-design-primer#asynchronism)

Focus on the core idea: **if the user does not need the result of an operation to see a response, that operation should not block the response.**

**The spectrum of async patterns, from simplest to most robust:**

| Pattern                            | How It Works                                                       | Retry? | Example in DZZLO                                                |
| ---------------------------------- | ------------------------------------------------------------------ | ------ | --------------------------------------------------------------- |
| **Fire-and-forget**                | Call the function, do not await it                                 | No     | `Logs.create().catch(...)` in logging middleware                |
| **Fire-and-forget with try/catch** | Same, but catch errors                                             | No     | `sendNotifyToExternalIDs` — catches errors, logs them, moves on |
| **Async with no queue**            | `await` the call, but no retry if it fails                         | No     | `sendEmail` in request handler — blocks response, no retry      |
| **Background job queue**           | Push a job to a queue, a worker picks it up and retries on failure | Yes    | What you should be doing for SMS, email, and push               |

**When does synchronous become a problem?**

It becomes a problem when any of these are true:

1. **Third-party latency varies.** 2Factor.in might respond in 200ms or 3 seconds. You cannot control it.
2. **Third-party availability is not 100%.** If 2Factor is down for 5 minutes, every login attempt during that window fails — even though your system is fine.
3. **The operation is not needed for the response.** The user needs to know "we will send you an OTP." They do not need to know "the OTP has been delivered to your phone" before the API responds.
4. **You need retry logic.** If an email fails, you want to try again in 30 seconds, not tell the user "something went wrong."

**Exercise:** For each of the six operations listed in the "Why This Matters" section, answer: does the user need the result before the API responds? Write yes or no and one sentence explaining why.

### Step 2: Message Queue Fundamentals (20 min)

**Read:** [System Design Primer — Message Queues](https://github.com/donnemartin/system-design-primer#message-queues)

A message queue decouples producers (the code that creates work) from consumers (the code that does the work). The key concepts:

**Producer/Consumer pattern:**

```
[Express Route Handler]  --push job-->  [Queue]  --pull job-->  [Worker Process]
     (producer)                        (Redis)                   (consumer)
```

The route handler responds to the user immediately after pushing the job. The worker picks it up and does the slow work (call 2Factor, send email, etc.) independently.

**Delivery guarantees — the three options:**

| Guarantee         | Meaning                                                                                                                           | Trade-off                                                                              | When to Use                                    |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **At-most-once**  | The message is delivered zero or one time. If the consumer crashes mid-processing, the message is lost.                           | Fast, no duplicates, but can lose messages                                             | Logging, analytics, non-critical notifications |
| **At-least-once** | The message is delivered one or more times. If the consumer crashes, the message is redelivered. Consumer might process it twice. | No lost messages, but consumer must handle duplicates                                  | SMS OTP, email, push notifications, billing    |
| **Exactly-once**  | The message is delivered exactly one time.                                                                                        | Extremely hard to achieve. Usually implemented as at-least-once + idempotent consumer. | Financial transactions, invoice generation     |

**For DZZLO-OMS, at-least-once is the right default.** If an OTP is sent twice, the user gets two SMS messages — annoying but not harmful. If a billing job runs twice, you need idempotency (check if the invoice already exists before creating it). The pragmatic approach: use at-least-once delivery and make your consumers idempotent.

**Key queue concepts to understand:**

- **Job:** A unit of work with a payload (e.g., `{ type: "sms", phone: "9876543210", otp: "123456" }`)
- **Worker:** A process that picks up jobs and executes them
- **Dead letter queue (DLQ):** Where jobs go after exhausting all retries — you review these manually
- **Backpressure:** When producers add jobs faster than consumers process them — the queue grows, and you need to monitor it
- **Concurrency:** How many jobs a single worker processes in parallel

**Exercise:** Draw a diagram (on paper or whiteboard) showing your login OTP flow today (synchronous) and what it would look like with a queue in between. Label which part blocks the API response in each version.

### Step 3: BullMQ — Node.js Job Queue on Redis (15 min)

**Read:** [BullMQ Quick Start](https://docs.bullmq.io/readme-1)
**Reference:** [BullMQ Documentation](https://docs.bullmq.io/)
**Code:** [BullMQ GitHub](https://github.com/taskforcesh/bullmq)

BullMQ is the standard job queue for Node.js. It uses Redis as the backing store. Here is why it fits your stack:

**What BullMQ gives you:**

- **Persistent jobs** — jobs survive process restarts (they are in Redis, not in memory)
- **Automatic retries** — configure retry count and backoff strategy per job or per queue
- **Delayed jobs** — schedule a job to run in the future (e.g., "send a reminder email in 24 hours")
- **Rate limiting** — limit how many jobs per time window (useful for 2Factor API rate limits)
- **Prioritization** — OTP jobs can jump ahead of notification jobs
- **Repeatable jobs** — cron-like scheduling (e.g., "run billing every day at 6 AM IST")
- **Dashboard** — Bull Board or Arena gives you a UI to see queues, failed jobs, and retry them

**How it works, simplified:**

```javascript
// producer (in your route handler)
const { Queue } = require("bullmq");
const smsQueue = new Queue("sms", {
  connection: { host: "localhost", port: 6379 },
});

// When user requests OTP:
await smsQueue.add("send-otp", {
  phone: "9876543210",
  otp: "482910",
  template: "iDzzloLoginOTP",
});
// Returns immediately — user sees "OTP sent" in < 100ms

// worker (separate process or same process)
const { Worker } = require("bullmq");
const smsWorker = new Worker(
  "sms",
  async (job) => {
    // This is where your existing 2Factor HTTP call goes
    await send2FactorSMS(job.data.phone, job.data.otp, job.data.template);
  },
  {
    connection: { host: "localhost", port: 6379 },
    attempts: 3,
    backoff: { type: "exponential", delay: 5000 },
  },
);
```

**What you need to run BullMQ:**

- Redis (or a Redis-compatible service like AWS ElastiCache or Upstash)
- `bullmq` npm package
- A worker process (can be the same Node.js process, or a separate one via PM2)

**Cost of adding Redis to your stack:**

- **AWS ElastiCache (Redis):** `cache.t3.micro` is ~$12/month. Sufficient for your volume.
- **Upstash (serverless Redis):** Free tier handles 10K commands/day. Your 130 orders/day would generate maybe 500-1000 queue commands/day. Free tier covers it.
- **Self-hosted on your EC2:** Free, but you manage it. Not recommended for production.

**Exercise:** Read the BullMQ Quick Start page. Note how `Queue`, `Worker`, and `QueueEvents` interact. Write down what happens when a worker throws an error — how does BullMQ know to retry?

### Step 4: Event-Driven Architecture Patterns (10 min)

**Read:** [Event-Driven Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven)

Focus on two distinctions:

**Events vs Commands:**

|                               | Event                                      | Command                                                |
| ----------------------------- | ------------------------------------------ | ------------------------------------------------------ |
| **Meaning**                   | "Something happened"                       | "Do this thing"                                        |
| **Example**                   | `order.created`                            | `send-sms`                                             |
| **Producers know consumers?** | No — they just emit the event              | Yes — they explicitly tell a specific queue what to do |
| **Multiple consumers?**       | Yes — many services can react to one event | Usually one — the command has a specific handler       |

Your current needs are better served by **commands** (job queues), not events. You know exactly what needs to happen: send this SMS, send this email, generate this PDF. You are not building a system where unknown future services need to react to "order created."

**Pub/Sub pattern:**
In pub/sub, publishers emit messages to a topic, and all subscribers receive them. This is what Socket.io was attempting for real-time updates. BullMQ does not do pub/sub — it does job queues. If you ever need pub/sub (e.g., "notify all connected dashboards when an order is created"), that is a different tool (Redis pub/sub, or Socket.io done properly, or AWS SNS).

**The practical takeaway for DZZLO-OMS:** Start with job queues (BullMQ). Consider pub/sub only if you revive the real-time dashboard feature. Do not try to do both at once.

---

## Hour 2 — Applied to Your System (60 min)

### Step 5: Identify DZZLO Operations That Benefit from Async (20 min)

Walk through each candidate operation. For each one, assess the current behavior, what would change, and the priority.

**Operation 1: SMS/OTP Delivery**

Current code (`SMSOTP/template/index.js`):

```javascript
// sendLoginSMSToUserPhone uses http.request to 2factor.in
// The caller awaits this function
// If 2factor.in is slow → user waits
// If 2factor.in is down → login flow breaks (even though OTP was generated and saved to DB)
```

What async gives you:

- API responds in < 100ms with "OTP sent" — the actual SMS delivery happens in the background
- If 2Factor is down, the job retries automatically (3 attempts with exponential backoff)
- If all retries fail, the job lands in the dead letter queue for manual review

Priority: **HIGH.** This directly affects user-facing login latency.

**Operation 2: Push Notifications (OneSignal)**

Current code (`App/notification.js`):

```javascript
// sendNotifyToExternalIDs does a fetch() POST to OneSignal
// Caller awaits it in dealer_custs.js and other services
// On error: catch + console.log — notification is lost forever
```

What async gives you:

- The business operation (linking a customer, updating an order) completes instantly
- Notification delivery is retried if OneSignal is temporarily down
- Failed notifications are tracked in the dead letter queue instead of silently lost

Priority: **HIGH.** Notifications are being silently lost today.

**Operation 3: Email Sending**

Current code (`helpers/sendEmail.js`):

```javascript
// await transporter.sendMail(message) — fully synchronous
// yearAccEmail generates Excel + sends email in the same request
```

What async gives you:

- Account report generation and email sending happen in the background
- The API responds immediately with "Report will be emailed shortly"
- Retry on SES transient errors

Priority: **MEDIUM.** Email is less latency-sensitive than OTP, but the account report flow is particularly slow because it generates an Excel file AND sends an email in one request.

**Operation 4: Invoice PDF Generation**

Current code (`invoice/htmlPdf/fileBuffer.js`):

```javascript
// html-pdf renders HTML to a buffer synchronously (CPU-bound)
// Fine for a single invoice, but batch generation blocks the event loop
```

What async gives you:

- Batch PDF generation moves to a worker process — the event loop stays free
- Individual PDF generation is fast enough to stay synchronous for now

Priority: **LOW** at current scale. Revisit if you add batch invoice generation.

**Operation 5: Scheduled Billing by `cr_bill_period`**

Current state: `cr_bill_period` exists as a field with values `INSTANT`, `DAILY`, `WEEKLY`, `MONTHLY` — but there is no automated system that triggers billing on those schedules. It is done manually.

What a queue gives you:

- BullMQ repeatable jobs: define a cron schedule that runs billing daily at a specific time
- The job checks all `dealer_custs` where `cr_bill_period === 'DAILY'` and creates invoices
- Separate jobs for weekly (every Monday) and monthly (1st of each month)
- Each job is logged, retried on failure, and visible in the dashboard

Priority: **MEDIUM-HIGH.** This is a missing feature, not just an optimization. Manual billing is error-prone.

**Operation 6: Log Cleanup / Data Archival**

Current state: Session 2 covered adding a TTL index on `logs`. But for more complex archival (e.g., moving old orders to a cold collection, generating monthly summaries), you need scheduled jobs.

What a queue gives you:

- A repeatable job that runs nightly to archive old data
- Explicit tracking of whether the job succeeded or failed

Priority: **LOW.** TTL index handles log cleanup. Archival is a future concern.

**Exercise:** Rank these six operations by the ratio of (benefit gained) to (effort to implement). Write your ranking and one sentence per item justifying it.

### Step 6: Design a Queue Architecture for DZZLO (20 min)

Here is a concrete architecture using BullMQ that fits your current setup.

**Queue topology — three queues to start:**

```
Queue: "notifications"
  ├── Job: send-sms     { phone, templateName, vars, notify }
  ├── Job: send-push    { userIds, heading, content, jsonData }
  └── Job: send-email   { to, subject, html, attachments }

Queue: "billing"
  └── Job: generate-invoices  { billPeriod: "DAILY"|"WEEKLY"|"MONTHLY", date }

Queue: "reports"
  └── Job: generate-pdf       { invoiceId, dealerCustId }
  └── Job: account-report     { dealerCustId, email, month, year }
```

**Why three queues instead of one?**

- Different retry strategies: SMS needs fast retries (5s, 15s, 45s), billing needs slower retries with manual review
- Different concurrency: notifications can run 5 at a time, billing should run 1 at a time to avoid race conditions
- Different priority: OTP should never wait behind a batch report job

**Worker design:**

```javascript
// workers/notifications.js
const { Worker } = require("bullmq");
const connection = { host: process.env.REDIS_HOST, port: 6379 };

const worker = new Worker(
  "notifications",
  async (job) => {
    switch (job.name) {
      case "send-sms":
        return await handleSMS(job.data);
      case "send-push":
        return await handlePush(job.data);
      case "send-email":
        return await handleEmail(job.data);
    }
  },
  {
    connection,
    concurrency: 5,
    limiter: { max: 10, duration: 1000 }, // max 10 jobs per second (respects 2Factor rate limits)
  },
);

worker.on("failed", (job, err) => {
  console.error(`Job ${job.id} failed: ${err.message}`);
  // Could also write to your logs collection here
});
```

**Where workers run:**

Option A — **Same process, different module.** Workers run inside your Express app. Simplest to deploy. The worker shares the event loop with your API, which is fine at your scale.

Option B — **Separate PM2 process.** Add a `worker` entry to your `ecosystem.config.js`. The worker is a standalone Node.js script that imports your existing service functions. It runs alongside your API but crashes independently.

**Recommendation:** Start with Option A. Move to Option B only if worker processing starts affecting API response times.

**How existing code changes:**

Before (synchronous):

```javascript
// In your login route handler
await sendLoginSMSToUserPhone({ user_phone, var1, var2, var3, notify });
res.status(200).json({ success: true, message: "OTP sent" });
```

After (with queue):

```javascript
// In your login route handler
await smsQueue.add("send-sms", {
  phone: user_phone,
  template: "login",
  vars: { var1, var2, var3 },
  notify,
});
res.status(200).json({ success: true, message: "OTP sent" });
// Actual SMS delivery happens in the worker, with retries
```

The `sendLoginSMSToUserPhone` function does not change — it moves from being called in the route handler to being called in the worker. The existing code is reused entirely.

**Scheduled jobs for billing:**

```javascript
// On app startup, register repeatable jobs
await billingQueue.add(
  "generate-invoices",
  { billPeriod: "DAILY" },
  { repeat: { cron: "30 0 * * *" } }, // 6:00 AM IST (UTC+5:30)
);

await billingQueue.add(
  "generate-invoices",
  { billPeriod: "WEEKLY" },
  { repeat: { cron: "30 0 * * 1" } }, // Monday 6:00 AM IST
);

await billingQueue.add(
  "generate-invoices",
  { billPeriod: "MONTHLY" },
  { repeat: { cron: "30 0 1 * *" } }, // 1st of month 6:00 AM IST
);
```

**Exercise:** Write the producer code for `sendNotifyToExternalIDs` — what goes into `job.data`? Write the worker handler that calls the existing OneSignal function. How do you handle the case where OneSignal returns a non-200 status?

### Step 7: Cost-Benefit at Current Scale (20 min)

This is the honest analysis. Adding a queue means adding Redis, adding BullMQ, adding worker code, and adding monitoring. Is it worth it?

**What you gain:**

| Benefit                                                    | Impact at 130 orders/day                            | Impact at 1,000 orders/day                                  |
| ---------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------- |
| Faster API responses (decouple from 2Factor/OneSignal/SES) | Noticeable — login feels 1-3s faster                | Significant — every request benefits                        |
| Retry on failure                                           | Prevents silent notification loss (happening today) | Critical — more orders = more notifications = more failures |
| Scheduled billing                                          | Enables a missing feature                           | Required — manual billing does not scale                    |
| Observability (job dashboard)                              | Nice to have                                        | Essential — you need to see what failed and why             |

**What it costs:**

| Cost                                                              | Estimate                                |
| ----------------------------------------------------------------- | --------------------------------------- |
| Redis (ElastiCache `cache.t3.micro` or Upstash free tier)         | $0-12/month                             |
| BullMQ npm package                                                | Free, MIT license                       |
| Bull Board (dashboard)                                            | Free, MIT license                       |
| Development time to set up queues + workers                       | ~2-3 days                               |
| Development time to migrate existing SMS/email/push to use queues | ~1-2 days per operation                 |
| Operational complexity (one more thing to monitor)                | Low — Redis is stable, BullMQ is mature |

**The verdict:**

At current scale (130 orders/day), BullMQ is **not required for survival** — your system works. But it is **worth adding for three reasons:**

1. **Silent notification loss is a bug, not a scale problem.** Your push notifications are being lost today when OneSignal fails. A queue with retries fixes this regardless of scale.

2. **Scheduled billing is a missing feature.** `cr_bill_period` exists but does nothing automatically. A queue with repeatable jobs is the cleanest way to implement this. The alternative (an external cron job that hits an API endpoint) is fragile and harder to monitor.

3. **The investment is small.** Setting up BullMQ with Redis takes 2-3 days. You are not adding Kafka or RabbitMQ — this is a lightweight, Node.js-native solution. The operational burden is minimal.

**When NOT to add BullMQ:**

- If you are the only developer and will not maintain it — an unmaintained queue is worse than no queue
- If your deployment pipeline cannot handle Redis — if adding ElastiCache to your infrastructure is blocked by cost or permissions, do not force it
- If you are about to rewrite the system — do not optimize what you are about to throw away

**The scale tipping point:**

| Scale                | Queue Status                                                                    |
| -------------------- | ------------------------------------------------------------------------------- |
| < 500 orders/day     | Optional but recommended for reliability                                        |
| 500-2,000 orders/day | Strongly recommended — synchronous external calls will cause noticeable latency |
| 2,000+ orders/day    | Required — you also need to think about worker scaling and queue monitoring     |

**Exercise:** Open your AWS console. Check the cost of adding a `cache.t3.micro` ElastiCache Redis instance in your region. Compare it with Upstash's free tier. Which makes more sense for your setup?

---

## 15-Minute Review

Answer these without looking back:

1. What is the difference between at-least-once and at-most-once delivery? Which one does DZZLO-OMS need for SMS OTP, and why?

2. Your `sendNotifyToExternalIDs` function catches errors and logs them. Why is this worse than a dead letter queue?

3. BullMQ uses Redis as its backing store. What happens to queued jobs if your Node.js process crashes and restarts?

4. You have three queues: notifications, billing, reports. Why not put everything in one queue?

5. `cr_bill_period` supports DAILY, WEEKLY, and MONTHLY. Write the BullMQ cron expression for a job that runs every Monday at 6:00 AM IST (hint: IST is UTC+5:30).

**Priority ranking for making operations async:**

Based on the cost-benefit analysis, here is the recommended order:

| Priority | Operation                      | Reason                                                                |
| -------- | ------------------------------ | --------------------------------------------------------------------- |
| 1        | Push notifications (OneSignal) | Lowest effort, highest impact — notifications are silently lost today |
| 2        | SMS/OTP delivery (2Factor)     | Directly improves login UX, adds retry for a critical auth flow       |
| 3        | Scheduled billing              | Enables a missing feature that customers expect from `cr_bill_period` |
| 4        | Email sending (SES)            | Less user-facing than SMS/push, but still blocks request handlers     |
| 5        | Invoice PDF generation         | Only matters for batch operations, which you do not do yet            |
| 6        | Log cleanup / archival         | TTL index already handles most of this                                |

**Concrete next steps:**

- [ ] Decide on Redis hosting: ElastiCache vs Upstash vs local Redis on EC2
- [ ] Install `bullmq` and set up a single "notifications" queue as a proof of concept
- [ ] Migrate `sendNotifyToExternalIDs` to use the queue — this is the lowest-risk first target
- [ ] Add Bull Board for visibility into job status and failures
- [ ] Once notifications work, migrate SMS OTP to the queue
- [ ] Design the billing worker for `cr_bill_period` scheduled jobs

---

## Resources

**Async & Queue Concepts:**

- [System Design Primer — Asynchronism](https://github.com/donnemartin/system-design-primer#asynchronism)
- [System Design Primer — Message Queues](https://github.com/donnemartin/system-design-primer#message-queues)
- [Event-Driven Architecture](https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/event-driven)

**BullMQ:**

- [BullMQ Documentation](https://docs.bullmq.io/)
- [BullMQ Quick Start](https://docs.bullmq.io/readme-1)
- [BullMQ GitHub](https://github.com/taskforcesh/bullmq)

**Related Tools:**

- [Bull Board (Dashboard UI)](https://github.com/felixmosh/bull-board)
- [AWS ElastiCache Pricing](https://aws.amazon.com/elasticache/pricing/)
- [Upstash (Serverless Redis)](https://upstash.com/)
