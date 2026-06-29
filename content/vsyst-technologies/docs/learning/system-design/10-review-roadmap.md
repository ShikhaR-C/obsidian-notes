# Session 10: Full System Review & Improvement Roadmap

> Phase 5 — Advanced & Roadmap | 2 hours | Review: 15 min

## What You'll Learn

- How to audit your own system against a structured checklist covering security, reliability, data, operations, and code quality
- How to categorize improvements by urgency and effort so nothing critical gets lost in a backlog
- How to create a concrete, time-bound roadmap that a solo developer can actually execute
- How to establish a recurring review habit that keeps the system healthy over time

## Why This Matters for DZZLO-OMS

You have spent nine sessions building a deep understanding of your system — from the request lifecycle and database performance through API design, security, caching, infrastructure, monitoring, CI/CD, and async patterns. Every session surfaced specific problems: SSH open to all IPs, MongoDB Atlas with no IP restriction, rate limiting commented out, express-validator installed but unused, 1.4M log records with no TTL, no CloudWatch alarms, no deploy script, no runbook, bus factor of 1.

The danger now is that all of those insights stay as notes and never become action. This session converts learning into a prioritized plan. You will walk through a full audit checklist, categorize every improvement by urgency, pick three things to do this week, and schedule the rest. When you finish, you will have a roadmap you can execute against — not a wish list.

---

## Hour 1 — Full System Review (60 min)

### Step 1: Re-read system-design.md (15 min)

Open `docs/strategy/system-design.md` and read it end to end with fresh eyes. You wrote parts of it before these sessions, and you have been updating it after each one. Now read it as if you were a new team member trying to understand the system.

**While reading, note:**

- Sections that feel incomplete or vague after what you have learned
- Numbers that have changed (instance count, order volume, collection sizes)
- Decisions you made during sessions 1-9 that are not reflected in the document yet
- Anything that would confuse someone reading it for the first time

**Goal:** By the end of this step, your system design doc should be a complete, current, accurate picture of DZZLO-OMS. If it is not, mark the gaps — you will fix them after this session.

---

### Step 2: Audit Checklist (45 min)

Walk through every category below. For each item, mark it done, not done, or not applicable. Do not fix anything yet — just assess.

#### Security Audit

- [ ] SSH restricted to known IPs or replaced with AWS SSM Session Manager?
- [ ] MongoDB Atlas IP whitelist tightened to VPC only (VPC Peering)?
- [ ] Rate limiting enabled on `/auth/login` and `/auth/otp` endpoints?
- [ ] API key validation logic reviewed — keys rotatable, not hardcoded?
- [ ] OTP storage reviewed — is the OTP stored as plaintext in the database?
- [ ] WAF enabled on ALB with managed rule groups?
- [ ] CORS origins restricted to known domains (not `*`)?
- [ ] Helmet or equivalent security headers configured?
- [ ] JWT secret strength and rotation strategy documented?
- [ ] Dependencies audited for known vulnerabilities (`npm audit`)?

#### Reliability Audit

- [ ] CloudWatch alarms configured (CPU, memory, 5xx rate, ALB latency, disk)?
- [ ] Atlas alerts configured (connections, oplog lag, replication lag)?
- [ ] Health check endpoint (`/health`) monitored by ALB and externally?
- [ ] Graceful shutdown: server closes connections and drains requests on SIGTERM?
- [ ] Database connection: server only starts listening after DB connects?
- [ ] PM2 configured with restart limits to prevent crash loops?
- [ ] ALB target group deregistration delay set for graceful drain?
- [ ] ASG health checks use ELB health, not just EC2 status?

#### Data Audit

- [ ] TTL index on `logs` collection (e.g., 90 days)?
- [ ] `explain()` run on the top 5 most frequent queries?
- [ ] Atlas Performance Advisor reviewed for index suggestions?
- [ ] Data archival strategy defined for old orders and logs?
- [ ] Backup and restore process tested (not just assumed Atlas handles it)?
- [ ] Collection sizes and growth rates documented?

#### Operations Audit

- [ ] Deploy process documented step by step?
- [ ] Emergency runbook exists (what to do when the system is down)?
- [ ] `.env` file backed up securely (not just on the EC2 instance)?
- [ ] At least 1 other person has access to deploy and restart the system?
- [ ] CI/CD pipeline or at minimum a `deploy.sh` script exists?
- [ ] Rollback process documented and tested?
- [ ] On-call expectations documented (who gets paged, when, how)?

#### Code Quality Audit

- [ ] Input validation active on all write endpoints (POST, PUT, PATCH)?
- [ ] `express-validator` integrated and enforced, not just installed?
- [ ] Unused v1 routes cleaned up or clearly deprecated?
- [ ] Error handling consistent — no unhandled promise rejections leaking?
- [ ] Response format standardized across all endpoints?
- [ ] No business logic in route files — separated into service/controller layers?

---

**Scoring:** Count how many items are checked vs. unchecked. This is your system's current health score. You do not need a perfect score — you need to know exactly where the gaps are.

---

## Hour 2 — Prioritized Roadmap (60 min)

### Step 3: Categorize Improvements (30 min)

Every unchecked item from the audit goes into one of four buckets. The criteria are urgency and effort.

#### P0 — Do This Week (< 4 hours each)

These are high-risk items that require minimal effort. There is no reason to delay them.

| #   | Item                                                                                                       | Effort   | Why P0                                                                                                                                                   |
| --- | ---------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Set up 5 CloudWatch alarms (CPU > 80%, 5xx > 10/min, ALB latency > 2s, disk > 80%, healthy host count < 2) | ~2 hours | You currently have zero visibility into production. If an instance dies or disk fills up, you will not know until a user complains.                      |
| 2   | Set up 3 Atlas alerts (connections > 80%, oplog window < 24h, replication lag > 10s)                       | ~1 hour  | Same problem on the database side. Atlas has built-in alerts — you just need to enable them.                                                             |
| 3   | Write an emergency runbook                                                                                 | ~2 hours | Bus factor is 1. If you are unavailable and someone else needs to restart the system, they need a document that says exactly what to do.                 |
| 4   | Restrict SSH in Security Group to your IP only                                                             | ~15 min  | SSH is currently open to all IPs. This is the single highest-risk security issue and the single easiest fix.                                             |
| 5   | Enable rate limiting on `/auth/login`                                                                      | ~30 min  | `express-rate-limit` is already installed and the code is commented out. Uncomment it, configure 5 requests per minute per IP on auth endpoints, deploy. |
| 6   | Write `deploy.sh` script                                                                                   | ~2 hours | Your deploy process is currently a series of SSH commands you run from memory. A script makes it repeatable and shareable.                               |

#### P1 — Do This Month (1-3 days each)

Important improvements that require some planning or testing but should not wait longer than a month.

| #   | Item                                                                  | Effort  | Why P1                                                                                                                                                                                          |
| --- | --------------------------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | TTL index on `logs` collection (90-day retention)                     | ~1 day  | 1.4M records growing ~5K/day. Without TTL, this collection grows forever. The TTL index is a single command, but you should verify log queries still work and communicate the retention policy. |
| 2   | Document deploy process and share `.env` with a trusted backup person | ~1 day  | Directly addresses bus factor. The runbook from P0 tells someone what to do; this gives them the ability to actually do it.                                                                     |
| 3   | Basic GitHub Actions: lint + test on push                             | ~2 days | You do not have CI/CD. Starting with "run tests on every push" is the smallest useful step. Even if your test coverage is low, it establishes the pipeline you will build on.                   |
| 4   | Integrate `express-validator` on Create Order and Create User         | ~2 days | These are your highest-traffic write endpoints. Validation is installed but not wired in. Start with these two, then expand.                                                                    |
| 5   | Review Atlas Performance Advisor and act on top suggestion            | ~1 day  | You have never checked it. There may be an obvious missing index that cuts query time significantly.                                                                                            |
| 6   | Run `npm audit` and fix critical/high vulnerabilities                 | ~1 day  | Dependency vulnerabilities accumulate silently. A single `npm audit fix` pass catches the easy ones.                                                                                            |

#### P2 — Do This Quarter (1-2 weeks each)

Meaningful architectural improvements that require dedicated focus time.

| #   | Item                                                                  | Effort   | Why P2                                                                                                                                                 |
| --- | --------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Move secrets from `.env` files to AWS Systems Manager Parameter Store | ~1 week  | `.env` files are manually managed, not backed up, and different across instances. Parameter Store centralizes secrets and integrates with IAM.         |
| 2   | Set up AWS SSM Session Manager and close port 22                      | ~1 week  | Eliminates SSH as an attack surface entirely. Requires IAM role configuration and SSM agent setup on EC2.                                              |
| 3   | VPC Peering for MongoDB Atlas                                         | ~1 week  | Removes MongoDB Atlas from the public internet. Traffic stays on AWS private network. Requires Atlas configuration and VPC route table changes.        |
| 4   | Centralized logging with CloudWatch Logs                              | ~1 week  | PM2 logs currently live on individual EC2 instances. If an instance is terminated, logs are lost. CloudWatch Logs centralizes them and enables search. |
| 5   | Full CI/CD pipeline: GitHub Actions + AWS CodeDeploy                  | ~2 weeks | Builds on the basic GitHub Actions from P1. Adds automated deployment to EC2 via CodeDeploy with blue/green or rolling strategy.                       |
| 6   | Input validation on all remaining write endpoints                     | ~1 week  | Extends the P1 work on Create Order and Create User to every POST/PUT/PATCH endpoint.                                                                  |

#### P3 — When It Hurts (varies)

These are real improvements, but they solve problems you do not have yet at ~130 orders/day. Do them when the need becomes concrete.

| #   | Item                                                          | Trigger                                                           | Effort   |
| --- | ------------------------------------------------------------- | ----------------------------------------------------------------- | -------- |
| 1   | Redis cache for `getUserFromToken()`                          | Token lookup latency shows up in traces or you exceed ~1K req/min | ~1 week  |
| 2   | Background job queue (BullMQ + Redis) for SMS/email           | SMS/email sending causes noticeable request latency or failures   | ~2 weeks |
| 3   | WAF on ALB with managed rules                                 | You see bot traffic, scraping, or attack patterns in logs         | ~1 week  |
| 4   | Infrastructure right-sizing (consolidate t3.small + t3.micro) | Monthly AWS bill becomes a concern or you need to scale up        | ~1 week  |
| 5   | v3 API migration with proper versioning                       | You need breaking changes and have external API consumers         | ~4 weeks |
| 6   | Read replicas or sharding for MongoDB                         | Query performance degrades despite proper indexing                | ~2 weeks |

---

### Step 4: Create Action Items (30 min)

#### This Week — Pick Your Top 3 P0 Items

Do not try to do all six P0 items in one week. Pick three and finish them. Suggested order based on risk reduction per hour spent:

1. **Restrict SSH to your IP** (15 min) — highest risk, lowest effort, do it right now
2. **Enable rate limiting on /auth/login** (30 min) — uncomment, configure, deploy
3. **Set up CloudWatch alarms** (2 hours) — gives you visibility for everything else

The remaining P0 items (Atlas alerts, runbook, deploy script) go into next week.

#### This Month — Schedule P1 Items

Block 4 working sessions over the next 4 weeks:

| Week   | Item                                                      | Notes                      |
| ------ | --------------------------------------------------------- | -------------------------- |
| Week 1 | Remaining P0 items (Atlas alerts, runbook, deploy.sh)     | Clear the P0 backlog first |
| Week 2 | TTL index on logs + Atlas Performance Advisor review      | Database health            |
| Week 3 | Document deploy process + share access with backup person | Bus factor                 |
| Week 4 | express-validator on Create Order + Create User           | Input safety               |

GitHub Actions (P1 #3) and npm audit (P1 #6) can be done in spare time between these.

#### This Quarter — Add P2 to Planning

P2 items do not need specific dates yet. Add them to whatever planning tool you use (even if that is a text file) so they surface during quarterly review. The suggested order:

1. SSM Session Manager + close port 22 (pairs with SSH restriction from P0)
2. Parameter Store for secrets (pairs with deploy documentation from P1)
3. VPC Peering for Atlas (pairs with Atlas alert setup from P0)
4. CI/CD pipeline (builds on GitHub Actions from P1)
5. Centralized logging (builds on CloudWatch alarms from P0)
6. Remaining validation endpoints (extends express-validator work from P1)

---

## 15-Minute Review — Final

This is the last review across all 10 sessions. Spend it locking things in.

**1. Confirm your P0 commitment (5 min)**

Write down the 3 P0 items you will do this week, with the specific day and time block for each. If they are not scheduled, they will not happen.

**2. Establish a monthly system health review (5 min)**

Add a recurring monthly calendar event: "System Health Review." During that 30 minutes:

- Re-read `docs/strategy/system-design.md` — is it still accurate?
- Check CloudWatch alarms — any that fired? Any thresholds to adjust?
- Check Atlas alerts — same questions
- Review the P1/P2 roadmap — anything to promote or demote?
- Run `npm audit` — any new vulnerabilities?
- Check `logs` collection size — is the TTL working?

**3. Acknowledge what you've built (5 min)**

After 10 sessions and 20 hours, you now understand:

- How every request flows through your system and where time is spent (Session 1)
- How your database performs and where indexes matter (Session 2)
- How to design APIs that are safe and evolvable (Session 3)
- How authentication and security layers protect your system (Session 4)
- When and how caching helps — and when it does not (Session 5)
- How your infrastructure scales and what it costs (Session 6)
- How to monitor a system and get alerted before users notice (Session 7)
- How CI/CD eliminates manual deployment risk (Session 8)
- How async patterns decouple work and improve resilience (Session 9)
- How to audit your system and prioritize improvements systematically (Session 10)

Most solo developers never reach this level of clarity about their own systems. The system design document you have been building is not a theoretical exercise — it is a living operational document for DZZLO-OMS.

---

## Resources

### From This Session

- [The Checklist Manifesto (summary)](https://fs.blog/the-checklist-manifesto/) — Why checklists work for complex systems
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) — The full framework behind the audit categories above
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — How to set targets for reliability

### Consolidated from Sessions 1-9

| Resource                                                                               | Sessions    |
| -------------------------------------------------------------------------------------- | ----------- |
| [System Design Primer](https://github.com/donnemartin/system-design-primer)            | 1, 2, 5, 6  |
| [Google SRE Book](https://sre.google/sre-book/table-of-contents/)                      | 7, 10       |
| [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) | 3, 4        |
| [MongoDB Official Docs](https://www.mongodb.com/docs/)                                 | 2, 7        |
| [AWS Documentation](https://docs.aws.amazon.com/)                                      | 6, 7, 8, 10 |
| [The Twelve-Factor App](https://12factor.net/)                                         | 8           |
| [ByteByteGo YouTube](https://www.youtube.com/@ByteByteGo)                              | 1, 5, 9     |
| [Express Validator Docs](https://express-validator.github.io/docs/)                    | 3           |
| [BullMQ Docs](https://docs.bullmq.io/)                                                 | 9           |

### Your System Design Document

`docs/strategy/system-design.md` — Keep this updated. It is the single source of truth for how DZZLO-OMS works.

---

_Session 10 of 10 — System Design Learning Plan Complete_
