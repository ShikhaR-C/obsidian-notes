# System Design Learning Plan — 20 Hours

> Tailored for a solo developer running DZZLO-OMS (Node.js/Express/MongoDB, ~120 businesses, ~130 orders/day, AWS EC2+ALB, bus factor of 1). Every session maps directly to your system's real problems.

---

## Structure

**5 Phases, 10 Sessions, 2 hours each.** Each session has its own file with resources, exercises, and a 15-min review tied to DZZLO-OMS.

```
Phase 1: Foundations          → Understand what you have
Phase 2: API & Security       → Harden what's exposed
Phase 3: Performance          → Optimize what's slow
Phase 4: Operations           → Automate what's manual
Phase 5: Advanced & Roadmap   → Plan what's next
```

---

## File Index

### Phase 1 — Foundations (Sessions 1–2)

- [01-request-lifecycle.md](./01-request-lifecycle.md) — How a request flows through your system, latency budgets, back-of-envelope math
- [02-database-performance.md](./02-database-performance.md) — MongoDB indexing, explain(), Atlas Performance Advisor, TTL indexes

### Phase 2 — API & Security (Sessions 3–4)

- [03-api-design.md](./03-api-design.md) — REST contracts, validation, versioning, OWASP API Top 10
- [04-auth-security.md](./04-auth-security.md) — JWT hardening, rate limiting, AWS WAF, SSH/MongoDB access control

### Phase 3 — Performance (Sessions 5–6)

- [05-caching.md](./05-caching.md) — Cache patterns, Redis/ElastiCache, when caching is worth it
- [06-infra-scaling.md](./06-infra-scaling.md) — ALB, ASG, EC2 sizing, cost optimization, load testing

### Phase 4 — Operations (Sessions 7–8)

- [07-monitoring-alerting.md](./07-monitoring-alerting.md) — Golden signals, CloudWatch alarms, Atlas alerts, centralized logging
- [08-cicd-deployment.md](./08-cicd-deployment.md) — CI/CD pipelines, CodeDeploy, secrets management, runbooks

### Phase 5 — Advanced & Roadmap (Sessions 9–10)

- [09-async-queues.md](./09-async-queues.md) — Message queues, BullMQ, background jobs, event-driven patterns
- [10-review-roadmap.md](./10-review-roadmap.md) — Full system review, prioritized improvement roadmap (P0–P3)

### Phase 6 — Deep Dives (Sessions 11–13)

- [11-session-auth.md](./11-session-auth.md) — Session vs JWT comparison, session auth at scale, hybrid approach, migration
- [12-vpc-networking.md](./12-vpc-networking.md) — VPC fundamentals, subnets, peering, PrivateLink, ideal network architecture
- [13-database-strategy.md](./13-database-strategy.md) — Database types, polyglot persistence, Redis/PostgreSQL/TimeSeries for DZZLO

### Solutions — Actionable Fixes

- [solutions-security.md](./solutions-security.md) — 11 security problems with copy-paste fixes, priority-ordered
- [solutions-caching-cdn.md](./solutions-caching-cdn.md) — Multi-layer caching, Redis, CloudFront CDN, implementation code
- [solutions-resilience-automation.md](./solutions-resilience-automation.md) — Circuit breakers, CI/CD, zero-downtime deploys, self-healing

---

## Schedule

Suggested pace: **2 sessions/week.**


| Week | Phase          | Sessions       | Focus                               |
| ---- | -------------- | -------------- | ----------------------------------- |
| 1    | Foundations    | 1, 2           | Request flow + Database             |
| 2    | API & Security | 3, 4           | API design + Auth hardening         |
| 3    | Performance    | 5, 6           | Caching + Infrastructure            |
| 4    | Operations     | 7, 8           | Monitoring + CI/CD                  |
| 5    | Advanced       | 9, 10          | Async patterns + Final roadmap      |
| 6    | Deep Dives     | 11, 12         | Session auth + VPC networking       |
| 7    | Deep Dives     | 13 + Solutions | Database strategy + Implement fixes |


After each session, spend 5 minutes updating `docs/strategy/system-design.md` with anything new you learned or decided.

---

## Resources Quick Reference


| Resource                                                                               | Type               | Used In                |
| -------------------------------------------------------------------------------------- | ------------------ | ---------------------- |
| [System Design Primer](https://github.com/donnemartin/system-design-primer)            | GitHub (free)      | Sessions 1, 2, 5, 6    |
| [Google SRE Book](https://sre.google/sre-book/table-of-contents/)                      | Online book (free) | Session 7              |
| [OWASP API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) | Guide (free)       | Sessions 3, 4          |
| [MongoDB Docs](https://www.mongodb.com/docs/)                                          | Official docs      | Sessions 2, 7, 13      |
| [AWS Documentation](https://docs.aws.amazon.com/)                                      | Official docs      | Sessions 6, 7, 8, 12   |
| [The Twelve-Factor App](https://12factor.net/)                                         | Guide (free)       | Session 8              |
| [ByteByteGo YouTube](https://www.youtube.com/@ByteByteGo)                              | Videos             | Sessions 1, 5, 9       |
| [Express Validator Docs](https://express-validator.github.io/docs/)                    | Official docs      | Session 3              |
| [BullMQ Docs](https://docs.bullmq.io/)                                                 | Official docs      | Session 9              |
| [AWS VPC Docs](https://docs.aws.amazon.com/vpc/latest/userguide/)                      | Official docs      | Session 12             |
| [MongoDB Atlas Security](https://www.mongodb.com/docs/atlas/security/)                 | Official docs      | Sessions 12, Solutions |
| [express-session Docs](https://www.npmjs.com/package/express-session)                  | npm                | Session 11             |


---

*Created: 2026-04-04 | Updated: 2026-04-04 (added Phase 6 + Solutions)*