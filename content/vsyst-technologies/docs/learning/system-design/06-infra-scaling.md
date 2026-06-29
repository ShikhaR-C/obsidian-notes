# Session 6: Infrastructure & Scaling

> Phase 3 — Performance | 2 hours | Review: 15 min

## What You'll Learn

- How load balancers work at the protocol level — ALB vs NLB, health checks, target groups, and why the distinction matters
- The difference between horizontal and vertical scaling, and which one is relevant at ~130 orders/day
- How ASG target tracking policies actually decide when to scale — the math behind your 45% CPU threshold
- How to read your own AWS infrastructure's real usage data and make cost-informed decisions
- Whether your current 2-server setup is justified or if you're paying for complexity you don't need

## Why This Matters for DZZLO-OMS

Your infrastructure right now: an ALB splitting traffic 84/16 between a t3.small (in an ASG with CPU target tracking at 45%) and a standalone t3.micro. PM2 runs a single process on each server. You're handling ~130 orders/day — roughly 0.075 req/sec at peak.

Here's the uncomfortable question: **you might be paying for two servers and a load balancer to handle what a single t3.micro could manage with 95% of its capacity still idle.** The ASG is configured to scale at 45% CPU, but at your traffic level, real CPU utilization is likely under 5%. The ASG has probably never scaled out — meaning you're paying for scaling infrastructure that's never been triggered.

This isn't a criticism of the setup. When you deployed this, high availability mattered and the traffic was unknown. But now you have data. This session is about learning to read that data and making infrastructure decisions based on evidence instead of guesses.

By the end, you'll know exactly what you're paying, what you're using, and whether simplifying to a single ASG with t3.small instances makes sense.

## Hour 1 — Concepts (60 min)

### Step 1: Load Balancing Deep Dive (20 min)

**Read:** [System Design Primer — Load Balancer](https://github.com/donnemartin/system-design-primer#load-balancer)

**Then read:** [AWS ALB Introduction](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)

**Focus on these concepts:**

**ALB vs NLB — when each applies:**

- **ALB (Application Load Balancer):** Layer 7 (HTTP/HTTPS). It understands HTTP — it can route based on URL path, hostname, headers, query strings. It terminates TLS. This is what you use because you need HTTP-aware routing.
- **NLB (Network Load Balancer):** Layer 4 (TCP/UDP). It doesn't inspect HTTP — it just forwards packets. Ultra-low latency (~100 us vs ~1-2 ms for ALB), millions of requests/sec. You'd use this for WebSocket connections, gRPC, or when you need static IPs.
- **For DZZLO-OMS:** ALB is correct. You're serving a REST API over HTTPS. You don't need NLB's raw throughput or Layer 4 features.

**Health checks — how ALB knows your server is alive:**

- ALB sends HTTP requests to a configured health check path (e.g., `/health`) on a regular interval (default: 30 seconds).
- If a target fails the health check threshold (default: 3 consecutive failures), ALB stops routing traffic to it.
- Your healthcheck middleware at the top of the Express pipeline exists for exactly this purpose — it returns 200 immediately without running the rest of the middleware stack.
- **Key question for your system:** Is your health check path configured in the ALB target group? Does it match what your Express healthcheck middleware responds to? A mismatch here means ALB could be running requests through your full 18-middleware pipeline just to check if the server is up.

**Target groups — the connection between ALB and your instances:**

- A target group is a set of instances (or IPs, or Lambda functions) that receive traffic.
- Your ALB has two target groups: one for the t3.small (weight 84), one for the t3.micro (weight 16). This is a weighted target group routing setup.
- The ASG registers/deregisters instances in the t3.small's target group automatically when it scales.
- **The problem with your standalone t3.micro:** It's not in an ASG. If it crashes, nobody replaces it. The ALB will stop routing the 16% of traffic to it (health check failure), and 100% goes to the t3.small. This is a manual recovery scenario.

**While reading, think about:**

- What happens if your t3.small crashes and the ASG hasn't launched a replacement yet? (ALB routes 100% to the t3.micro.)
- What happens if the t3.micro crashes? (ALB routes 100% to the t3.small. Nobody auto-replaces the micro.)
- Is there any scenario where the 84/16 split actually matters at 0.075 req/sec? (Not really. Even the t3.micro alone could handle all your traffic.)

### Step 2: Horizontal vs Vertical Scaling (20 min)

**Read:** [System Design Primer — Scalability](https://github.com/donnemartin/system-design-primer#scalability)

**The two approaches:**

**Vertical scaling (scale up):** Bigger machine. Move from t3.small to t3.medium. More CPU, more RAM.

- Pros: Simple. No code changes. No distributed system problems.
- Cons: There's a ceiling. A single machine can only get so big. Single point of failure.

**Horizontal scaling (scale out):** More machines. Add another t3.small to the ASG.

- Pros: No ceiling (in theory). Fault tolerant — one dies, others keep going.
- Cons: Requires stateless applications, load balancers, distributed coordination.
- Your Express app is already stateless (JWT auth, no server-side sessions), so horizontal scaling is straightforward.

**Which matters at your scale? Neither.**

At ~130 orders/day, your actual compute requirement is negligible. A t3.micro (2 vCPU, 1 GB RAM) could handle your entire workload with resources to spare. The question isn't "how do I scale?" — it's "am I over-provisioned?"

**The real scaling bottleneck for DZZLO-OMS isn't compute — it's operational:**

- Bus factor of 1 (you). If you're sick for a week, the system runs fine but nobody can fix bugs or deploy.
- MongoDB Atlas is your database scaling path. Atlas handles sharding, replicas, backups. You don't manage that.
- PM2 running a single process per instance means you're using 1 of 2 vCPUs. Enabling PM2 cluster mode would double your throughput per instance — that's free vertical scaling on your existing hardware.

**Exercise — calculate your real capacity headroom:**

1. t3.small: 2 vCPU, 2 GB RAM. Single PM2 process. At ~0.075 req/sec peak, CPU per request is probably ~10-50 ms. That means you're using 0.075 x 0.05 = 0.00375 CPU-seconds per second. Out of 2 CPUs available, that's **0.19% utilization.**
2. If you enabled PM2 cluster mode (2 workers), you'd double capacity to ~0.38% utilization. Still laughably low.
3. A single t3.small could theoretically handle ~400 req/sec of simple Express requests. You're at 0.075. You have **5,300x headroom.**
4. At what order volume would you need to think about scaling? If each order generates ~5 API calls, 400 req/sec / 5 = 80 orders/second = 6.9 million orders/day. You're at 130.

### Step 3: ASG Target Tracking Policies (20 min)

**Read:** [AWS ASG Target Tracking Scaling Policies](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html)

**How your ASG is configured:**

- **Metric:** Average CPU utilization across all instances in the group
- **Target value:** 45%
- **What this means:** ASG tries to keep average CPU at or below 45%. If CPU goes above 45%, it launches new instances. If CPU drops well below 45%, it terminates instances (after a cooldown period).

**How the scaling decision actually works:**

1. CloudWatch collects CPU utilization data from all instances in the ASG every 1 minute (detailed monitoring) or 5 minutes (basic monitoring).
2. ASG calculates the average across all instances.
3. If the average exceeds 45% for a sustained period (typically 3 data points over 3 minutes), ASG calculates how many instances it needs to bring the average back to 45%.
4. **Scale-out formula (simplified):** `desired_instances = current_instances x (current_CPU / target_CPU)`. If you have 1 instance at 90% CPU and target is 45%, desired = 1 x (90/45) = 2 instances.
5. **Scale-in is more conservative:** ASG waits longer (default cooldown: 300 seconds) and only scales in when the metric is significantly below target. This prevents flapping (repeatedly scaling in and out).

**Why 45% as a target?**

- Too low (e.g., 20%) = you'll always have excess capacity. More instances running = more cost.
- Too high (e.g., 80%) = by the time ASG launches a new instance (takes 2-5 minutes), your existing instance might be overwhelmed.
- 45% is a reasonable middle ground for general workloads. It gives you roughly 55% headroom for traffic spikes while the new instance boots.

**The problem for DZZLO-OMS:**

- Your CPU utilization is probably under 5%. The 45% target will literally never be hit.
- The ASG's min capacity is likely 1, max is probably 2 or 3. With CPU at 5%, the ASG will always run exactly 1 instance.
- You're paying for ASG infrastructure (the control plane is free, but the instances aren't) that is functionally a static single-server deployment.
- **This isn't wrong** — it means if your t3.small crashes, ASG will auto-replace it. That's valuable. What's questionable is whether you also need the standalone t3.micro.

**Exercise — think through these ASG scenarios:**

1. What happens if someone runs a script that accidentally sends 10,000 requests in 1 minute? Will the ASG scale fast enough? (Calculate: 10,000/60 = ~167 req/sec. Each request takes ~50 ms of CPU. That's 167 x 0.05 = 8.35 CPU-seconds/sec. On a 2-vCPU machine, that's ~417% CPU utilization on one core or ~208% on two. ASG would trigger, but it takes 2-5 min to launch a new instance. The existing instance would be saturated for those minutes.)
2. What if instead of CPU, you tracked ALBRequestCountPerTarget? That reacts to traffic volume, not CPU. Might be more appropriate for your workload since Node.js I/O-bound work doesn't always spike CPU.

## Hour 2 — Hands-on AWS Console (60 min)

### Step 4: Investigate Your Actual Usage (20 min)

**Open the AWS Console and gather real numbers.** Don't guess — look.

**1. ASG Activity History:**

- Go to **EC2 > Auto Scaling Groups** > select your ASG.
- Click the **Activity** tab.
- Look at the activity history going back as far as it goes.
- **Question to answer:** Has the ASG ever launched an additional instance (beyond the minimum)? If the answer is "no" or "only during deployments," then your ASG has never actually scaled due to load. Write down the answer.

**2. CloudWatch CPU Utilization:**

- Go to **CloudWatch > Metrics > EC2 > Per-Instance Metrics**.
- Select **CPUUtilization** for both your t3.small and t3.micro.
- Set the time range to **1 month**.
- Set the period to **1 hour** for a clear view.
- **Numbers to write down:**
  - Average CPU over the past month for each instance
  - Peak CPU over the past month for each instance
  - Typical CPU during business hours (when orders come in)
- **Prediction to check:** Average CPU is under 5%. Peak CPU is under 15% (spikes might be from deployments or log rotation, not traffic).

**3. CloudWatch CPU Credit Balance (important for t3 instances):**

- In the same CloudWatch metrics, find **CPUCreditBalance** for both instances.
- t3.small earns 24 credits/hour, can accumulate up to 576.
- t3.micro earns 12 credits/hour, can accumulate up to 288.
- 1 credit = 1 vCPU at 100% for 1 minute.
- **If your credit balance is at or near the maximum, it confirms you're barely using any CPU.** The credits accumulate because you're not spending them.

**4. ALB Request Count:**

- Go to **CloudWatch > Metrics > ApplicationELB > Per AppELB Metrics**.
- Select **RequestCount**.
- Set the time range to **1 week**, period to **1 hour**.
- **Numbers to write down:**
  - Total requests per day
  - Peak requests per hour
  - Does the pattern match ~130 orders/day x ~5 API calls = ~650 requests/day?
  - Are there other requests (health checks, monitoring, bots) inflating the number?

**5. Cost Explorer:**

- Go to **AWS Cost Explorer** (Billing & Cost Management > Cost Explorer).
- Set the time range to the **last 3 months**.
- Group by **Service**.
- **Numbers to write down:**
  - Monthly cost for EC2 (both instances)
  - Monthly cost for ALB (fixed fee + LCU hours)
  - Monthly cost for data transfer
  - Total monthly AWS bill

### Step 5: Answer the Key Questions (20 min)

With real data in hand, answer these questions:

**1. Has the ASG ever scaled out?**

- If no: the ASG is functioning purely as an auto-replacement mechanism (launches a new instance if the current one terminates). That's useful but doesn't require the 45% CPU target — any target would behave the same at your load.
- Write down: "ASG has / has not scaled out in [timeframe]."

**2. What's the real CPU utilization?**

- Compare your actual numbers to the prediction from Step 2 (Hour 1).
- If CPU is under 5%, calculate what traffic level would push it to 45%: if 0.075 req/sec = 5% CPU, then 45% CPU = 0.075 x (45/5) = 0.675 req/sec = ~11,600 requests/day. You'd need roughly 2,300 orders/day to even approach the scaling threshold.
- Write down: "Average CPU: __%. Would need __ orders/day to trigger ASG scaling."

**3. What are you actually paying monthly?**

- Break down the cost:
  - t3.small on-demand: ~$15/month (us-east-1)
  - t3.micro on-demand: ~$7.50/month (us-east-1)
  - ALB: ~$16/month base + ~$0.50/month LCU (at your traffic level, LCU cost is negligible)
  - Total EC2 + ALB: **~$39/month** (rough estimate — compare to your actual numbers)
- Is $39/month a problem? Probably not. But understanding what you're paying for matters.

**4. Is the t3.micro serving a real purpose?**

- It handles 16% of traffic. At 0.075 req/sec peak, that's 0.012 req/sec going to the micro. One request every 83 seconds.
- It's not in the ASG, so if it dies, it stays dead until you manually intervene.
- It doesn't provide meaningful fault tolerance (the t3.small in the ASG already does that via auto-replacement).
- The only argument for keeping it: if the t3.small ASG is replacing an instance (takes 2-5 min), the micro handles traffic during that window. But at 0.012 req/sec, that's maybe 1 request during the replacement window.

### Step 6: Architecture Simplification Analysis (20 min)

**Compare your current setup vs a simplified one:**

**Current architecture:**

```
ALB (84/16 weighted routing)
  |-- Target Group A: t3.small (ASG, min=1, max=?, CPU target=45%)
  |-- Target Group B: t3.micro (standalone, no ASG)
PM2: 1 process per instance
Estimated cost: ~$39/month
```

**Simplified architecture:**

```
ALB
  |-- Target Group: t3.small (ASG, min=1, max=2, CPU target=45%)
PM2: cluster mode, 2 workers per instance
Estimated cost: ~$31/month (removed t3.micro ~$8/month)
```

**What you gain from simplification:**

- **Fewer things to manage.** One target group, one ASG, one instance type. No weighted routing to think about.
- **Better fault tolerance.** The ASG auto-replaces the t3.small if it dies. The standalone t3.micro had no such protection.
- **PM2 cluster mode** doubles your per-instance capacity for free (uses both vCPUs on the t3.small). At your load this doesn't matter, but it's correct practice.
- **Cleaner deployments.** Deploy to one ASG instead of coordinating between an ASG instance and a standalone instance.
- **Save ~$8/month.** Small, but it removes a component that wasn't adding value.

**What you lose:**

- **Warm standby during ASG replacement.** If the t3.small terminates and ASG is launching a replacement (2-5 min), there's no second instance handling traffic. At 0.075 req/sec, that's ~9 requests dropped during the window.
- **Mitigation:** Set ASG min=2 if you need zero-downtime replacement. This costs the same as your current setup (~$15 x 2 = $30 for EC2, plus ALB ~$16 = $46). But both instances would be in the ASG, auto-managed, and you'd get true high availability instead of the current pseudo-HA setup.

**The real question: do you need high availability?**

- At 130 orders/day, a 5-minute outage means ~0.4 missed requests. Those are probably retried by the client.
- If the answer is "no, 5 minutes of downtime is acceptable occasionally," run min=1 in the ASG and save money.
- If the answer is "yes, we need zero downtime," run min=2 in the ASG and drop the standalone micro. Both instances get auto-replaced, and you don't have to think about the standalone server.

**Exercise — draft a migration plan (on paper, don't execute):**

1. Enable PM2 cluster mode on the t3.small (change `instances: 1` to `instances: 'max'` or `instances: 2` in ecosystem.config.js).
2. Remove the t3.micro from the ALB target group.
3. Delete the t3.micro's target group.
4. Update ALB listener rules to route 100% to the t3.small's target group (remove weighted routing).
5. Terminate the t3.micro instance.
6. Optionally: increase ASG max to 2 or 3 to allow scaling if you ever need it.
7. Update any deployment scripts that reference the t3.micro.

## 15-Minute Review — Infrastructure Decision

This review is different from the others. You're not just answering questions — you're making a decision.

**Write down your answers to these:**

1. **What is your actual average CPU utilization across both instances?** (From CloudWatch.) How does this compare to the 45% ASG target? How many more orders/day would you need before the ASG would even consider scaling?
2. **What is your total monthly AWS cost for EC2 + ALB?** Is this reasonable for 130 orders/day? What's your cost per order? (Monthly cost / monthly orders.)
3. **Has the ASG ever scaled out due to load?** If not, is the ASG providing value beyond auto-replacement? Is auto-replacement alone worth the configuration complexity?
4. **Decision: Should you remove the standalone t3.micro?** Write a one-paragraph justification. Consider: fault tolerance value, cost savings, operational simplicity, risk of the migration.
5. **Decision: Should you enable PM2 cluster mode?** This is lower-risk than the infrastructure change. What's the downside? (Answer: you need to make sure your app doesn't use in-memory state that can't be shared across workers. Since you're using JWT auth and MongoDB, you're likely fine.)

**After this review, update `docs/strategy/system-design.md` with:**

- Your actual CPU utilization numbers
- Your monthly AWS cost breakdown
- Your decision on infrastructure simplification (and the timeline to execute it, if any)

## Resources


| Resource                             | URL                                                                                                                                                                                          | Used In |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| System Design Primer — Load Balancer | [https://github.com/donnemartin/system-design-primer#load-balancer](https://github.com/donnemartin/system-design-primer#load-balancer)                                                       | Step 1  |
| System Design Primer — Scalability   | [https://github.com/donnemartin/system-design-primer#scalability](https://github.com/donnemartin/system-design-primer#scalability)                                                           | Step 2  |
| AWS ALB Documentation                | [https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/introduction.html)               | Step 1  |
| AWS ASG Target Tracking              | [https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scaling-target-tracking.html)               | Step 3  |
| AWS t3 Instance CPU Credits          | [https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html) | Step 4  |
| PM2 Cluster Mode                     | [https://pm2.keymetrics.io/docs/usage/cluster-mode/](https://pm2.keymetrics.io/docs/usage/cluster-mode/)                                                                                     | Step 6  |


