# Session 1: Request Lifecycle & Fundamentals

> Phase 1 — Foundations | 2 hours | Review: 15 min

## What You'll Learn

- How an HTTP request travels from browser to server and back, and what happens at every hop in between
- The latency cost of each layer (network, TLS, application code, database) and which ones dominate
- How to do back-of-envelope math to estimate whether your system can handle its load
- Where your own middleware pipeline spends time — and where it wastes it

## Why This Matters for DZZLO-OMS

Your system has a clear, traceable request path: **ALB -> EC2 (Express + PM2) -> MongoDB Atlas**. That path runs through an 18-step middleware pipeline on every single request — from the healthcheck shortcut at the top down through `api_key`, `logging`, `version_check`, `security`, `company_status`, and finally the route handler.

The most immediate thing you'll notice once you trace this: your `logging()` middleware calls `getUserFromToken()` on every request. That means a JWT decode plus a MongoDB lookup happens before the request even reaches your business logic — just to write a log entry. At ~~130 orders/day (~~0.002 req/sec peak), this isn't killing your system today. But it's the kind of thing that matters when you start reasoning about where time goes, and it's a concrete example of why understanding the request lifecycle is the foundation for everything else in system design.

By the end of this session, you'll be able to look at any request to your system and say exactly how long each phase takes and why.

## Hour 1 — Concepts (60 min)

### Step 1: How Systems Handle Requests (20 min)

**Read:** [What Happens When You Type a URL](https://github.com/alex/what-happens-when)

Skim the full document, but **focus on these sections:**

- DNS lookup
- TCP connection and TLS handshake
- HTTP request/response cycle
- Server-side processing

**Skip:** the extremely low-level detail on keyboard interrupts, GPU rendering, and CSS parsing. You're here to understand the network and server parts.

**While reading, map each step to DZZLO-OMS:**

- DNS: your ALB's DNS name resolves to an IP
- TLS: ALB terminates TLS, so your EC2 instances receive plain HTTP
- Server processing: Express receives the request and runs it through all 18 middleware steps
- Response: JSON back through ALB to the client

### Step 2: Latency Numbers (20 min)

**Read:** [Latency Numbers Every Programmer Should Know](https://github.com/donnemartin/system-design-primer#latency-numbers-every-programmer-should-know)

**Key takeaways to internalize:**

- **Memory reference:** ~100 ns — this is what reading a variable costs
- **SSD random read:** ~150 us — 1,500x slower than memory
- **Round trip within same datacenter:** ~500 us — this is your EC2-to-MongoDB-Atlas round trip (roughly, assuming same AWS region)
- **Round trip CA to Netherlands:** ~150 ms — this is what your users experience if they're far from your AWS region

**Exercise:** Write down your best guess for these DZZLO-OMS-specific numbers:

1. Time for ALB to route a request to your EC2 instance
2. Time for Express to run through the 18 middleware steps (no DB calls)
3. Time for `getUserFromToken()` in the logging middleware (JWT decode + MongoDB query)
4. Time for the actual route handler to query MongoDB and return data

You'll verify these guesses in Hour 2.

### Step 3: Back-of-Envelope Calculations (20 min)

**Read:** [Back-of-the-Envelope Estimations](https://github.com/donnemartin/system-design-primer#back-of-the-envelope-estimations)

**Focus on:** the process of estimation, not memorizing exact numbers. The point is to get comfortable doing rough math quickly.

**Practice exercise — estimate for DZZLO-OMS:**

1. **Requests per second:** 130 orders/day. Each order likely involves ~5 API calls (list, create, update, fetch, confirm). That's 650 requests/day = ~0.0075 req/sec average. Peak might be 10x = ~0.075 req/sec. Your system is nowhere near capacity.
2. **Storage per year:** If each order document is ~2 KB in MongoDB, that's 130 x 365 x 2 KB = ~95 MB/year of order data. Tiny.
3. **Bandwidth:** 650 requests/day x ~5 KB average response = ~3.25 MB/day. Negligible.

Write these numbers down. They're your baseline. Every future design decision should be checked against them.

## Hour 2 — Applied to Your System (60 min)

### Step 4: Trace a DZZLO Request (30 min)

**Hands-on exercise:** Trace a "Create Order" POST request through your entire system. Open your codebase and follow the path.

For each of the 18 middleware steps, write down:

1. **What it does** (one sentence)
2. **Does it hit the database?** (yes/no)
3. **Estimated time** (use the latency numbers from Step 2)
4. **Could it short-circuit?** (does it ever return early and skip the rest?)

Your trace should look something like this (fill in the actual details from your code):

| #   | Middleware     | DB Call?     | Est. Time | Notes                                                                        |
| --- | -------------- | ------------ | --------- | ---------------------------------------------------------------------------- |
| 1   | healthcheck    | No           | <1 ms     | Returns 200 immediately for `/health`, skips everything else                 |
| 2   | api_key        | Yes (likely) | 2-5 ms    | Validates API key — check if it hits DB or uses in-memory lookup             |
| 3   | logging        | **Yes**      | 5-15 ms   | `getUserFromToken()` — JWT decode (~~1 ms) + MongoDB user lookup (~~5-10 ms) |
| 4   | version_check  | Maybe        | 1-5 ms    | Check what this actually does in your code                                   |
| 5   | security       | No (likely)  | <1 ms     | Helmet/CORS type headers                                                     |
| 6   | company_status | Yes (likely) | 2-5 ms    | Checks if the company is active                                              |
| ... | ...            | ...          | ...       | ...                                                                          |
| 18  | route handler  | Yes          | 10-50 ms  | The actual Create Order logic                                                |

**The key finding you should arrive at:** How many of those 18 steps hit MongoDB? Multiply that count by ~5-10 ms each. That's your middleware overhead per request, before your business logic even runs.

### Step 5: Calculate Your System's Load (30 min)

**Exercise:** Open a terminal and gather real numbers from your system.

**1. Database connections:**

- How many connections does your Express app open to MongoDB Atlas? (Check your Mongoose connection config.)
- With PM2 running 1 process per EC2 instance, and 2 instances, you have 2 connection pools.
- What's the pool size? Default Mongoose is 5. So you're using ~10 connections total out of MongoDB Atlas's limit.

**2. Request timing:**

- Add `console.time('request')` and `console.timeEnd('request')` around a test request, or check your existing logs.
- How long does a typical Create Order request take end-to-end?
- How much of that is middleware vs. route handler?

**3. The `getUserFromToken()` cost:**

- This is the most concrete optimization you'll find today.
- It runs on EVERY request, just for logging purposes.
- Estimate: if it takes ~10 ms per call, and you get 650 requests/day, that's 6.5 seconds/day of pure waste. Not a crisis — but it's the principle that matters.
- **Alternatives to consider (don't implement yet, just note them):**
  - Decode the JWT without hitting MongoDB (the user ID is in the token)
  - Cache the user lookup result for the duration of the request (other middleware might need it too)
  - Move the DB lookup to only happen when the log level actually needs the full user object

**4. EC2 capacity check:**

- Your t3.small has 2 vCPUs and 2 GB RAM. At 0.075 req/sec peak, you're using maybe 0.1% of its capacity for request handling.
- The real constraint on t3 instances is CPU credits. Check your CloudWatch for CPU credit balance — if it's staying full, you're fine.
- Your t3.micro (16% of traffic) has 1 vCPU and 1 GB RAM. Same story — way under capacity.

## 15-Minute Review — Apply to DZZLO-OMS

Answer these five questions in writing. If you can't answer one, go back and find the answer in your codebase.

1. **How many MongoDB queries happen before your route handler even starts?** Count every middleware step that touches the database. Is the total more than you expected?
2. **What is the estimated total middleware overhead (in milliseconds) for a single request?** Add up your estimates from the trace table. How does this compare to the time spent in the actual route handler?
3. **The `logging()` middleware calls `getUserFromToken()` on every request. What information does it actually need from that call?** Could you get the same information from just decoding the JWT (no DB hit)? What would you lose?
4. **Your system handles ~0.075 req/sec at peak. What request rate would actually stress your current setup?** Think about: MongoDB connection pool limits, EC2 CPU/memory, Express single-threaded event loop. Which would break first?
5. **If you added 10x more businesses tomorrow (1,200 instead of 120), what's the first thing that would need to change?** Hint: it's probably not your servers.

## Resources

| Resource                                     | URL                                                                                                                                                                                                  | Used In       |
| -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| What Happens When You Type a URL             | [https://github.com/alex/what-happens-when](https://github.com/alex/what-happens-when)                                                                                                               | Step 1        |
| System Design Primer                         | [https://github.com/donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)                                                                                           | Steps 2-3     |
| Latency Numbers Every Programmer Should Know | [https://github.com/donnemartin/system-design-primer#latency-numbers-every-programmer-should-know](https://github.com/donnemartin/system-design-primer#latency-numbers-every-programmer-should-know) | Step 2        |
| Back-of-the-Envelope Estimations             | [https://github.com/donnemartin/system-design-primer#back-of-the-envelope-estimations](https://github.com/donnemartin/system-design-primer#back-of-the-envelope-estimations)                         | Step 3        |
| ByteByteGo (YouTube)                         | [https://www.youtube.com/@ByteByteGo](https://www.youtube.com/@ByteByteGo)                                                                                                                           | Supplementary |
