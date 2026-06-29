# Task Overview — DZZLO-OMS Optimization

> Extracted from `docs/learning/api-pattern-problems/`, `docs/learning/system-design/`, and `docs/learning/systemDesignSolutions/`.
> Filtered for implementability. Ordered smallest-first within each category.
> Each task includes: what, why, how to verify API+App compatibility.

---

## How to Use These Files

1. **Pick a category** based on what you want to improve today
2. **Start from the top** — tasks are ordered smallest-first within each file
3. **Verify after each task** — each task has API + App compatibility checks
4. **Discuss before doing** — each task has a "Discussion" section explaining the reasoning

---

## Category Index

| File                                                             | Focus                                | # Tasks | Smallest Task          |
| ---------------------------------------------------------------- | ------------------------------------ | ------- | ---------------------- |
| [01-quick-wins.md](./01-quick-wins.md)                           | Zero-risk, immediate impact          | 7       | XS (1 line)            |
| [02-security-hardening.md](./02-security-hardening.md)           | P0 vulnerability fixes               | 7       | XS (15 min)            |
| [03-database-optimization.md](./03-database-optimization.md)     | Indexes, TTL, pagination             | 8       | XS (1 line in model)   |
| [04-api-query-performance.md](./04-api-query-performance.md)     | Promise.all, Map lookups             | 6       | XS (5 min)             |
| [05-app-performance.md](./05-app-performance.md)                 | RTK Query, FlatList, FlashList, memo | 8       | XS (1 line per screen) |
| [06-caching.md](./06-caching.md)                                 | In-process + future Redis            | 5       | XS (10 min)            |
| [07-resilience-ops.md](./07-resilience-ops.md)                   | Health, PM2, monitoring              | 8       | XS (5 min)             |
| [08-cloudwatch-setup.md](./08-cloudwatch-setup.md)               | Centralized logging & monitoring     | 7       | XS (5 min)             |
| [09-select-projection-audit.md](./09-select-projection-audit.md) | DB-7 `.select()` audit — all files   | ~184    | XS (1 line per query)  |

**Total: 57 tasks** across 9 categories.

---

## Suggested Sprint Plan

### Sprint 1 — Foundation (1-2 days)

All XS tasks, zero risk, immediate impact:

| Done | Task                       | Category   | Time   |
| ---- | -------------------------- | ---------- | ------ |
| [x]  | QW-1: `.lean()` on reads   | Quick Wins | 1 hr   |
| [x]  | QW-2: Share loggedInUser   | Quick Wins | 5 min  |
| [x]  | QW-5: JSON body limit      | Quick Wins | 1 min  |
| [x]  | QW-6: `trust proxy`        | Quick Wins | 1 min  |
| [x]  | QW-7: Safe meta parse      | Quick Wins | 3 min  |
| [x]  | SEC-1: Timing-safe API key | Security   | 15 min |
| [x]  | SEC-6: DB before listen    | Security   | 15 min |
| [x]  | RES-1: Deep health check   | Resilience | 15 min |
| [ ]  | RES-4: PM2 log rotation    | Resilience | 5 min  |

**Verify:** Run the API, hit several endpoints, confirm app works normally.

### Sprint 2 — Performance + Security (2-3 days)

Small tasks with measurable impact:

| Done | Task                              | Category         | Time   |
| ---- | --------------------------------- | ---------------- | ------ |
| [x]  | QW-3: `keepUnusedDataFor`         | Quick Wins (App) | 5 min  |
| [x]  | QW-4: Response compression        | Quick Wins (API) | 10 min |
| [x]  | SEC-2: Enable rate limiting       | Security         | 15 min |
| [ ]  | SEC-3: Hash OTPs                  | Security         | 30 min |
| [ ]  | SEC-5: Restrict CORS origins      | Security         | 30 min |
| [x]  | SEC-7: Fix logging middleware     | Security         | 30 min |
| [x]  | DB-1 to DB-4: Compound indexes    | Database         | 30 min |
| [ ]  | DB-5 + DB-6: TTL indexes          | Database         | 15 min |
| [x]  | AQP-1: Parallelize balance check  | API Perf         | 5 min  |
| [x]  | AQP-2: Parallelize getOnePO       | API Perf         | 15 min |
| [x]  | CACHE-1: LRU for getUserFromToken | Caching          | 30 min |

**Verify:** Test order creation, order detail, order list, OTP flow.

### Sprint 3 — Deeper Optimization (3-5 days)

Medium tasks requiring careful testing:

| Done | Task                                      | Category   | Time   |
| ---- | ----------------------------------------- | ---------- | ------ |
| [x]  | AQP-4 + AQP-5: Order list parallel + Maps | API Perf   | 1 hr   |
| [x]  | AQP-3: Process order parallel             | API Perf   | 20 min |
| [x]  | AQP-6: Create order parallel              | API Perf   | 30 min |
| [x]  | APP-1 + APP-2: useCallback + React.memo   | App Perf   | 1-2 hr |
| [x]  | APP-3: FlatList virtualization            | App Perf   | 1 hr   |
| [x]  | APP-8 P1: FlashList — Orders + Invoices   | App Perf   | 1.5 hr |
| [x]  | APP-5: RTK Query retry                    | App Perf   | 20 min |
| [x]  | SEC-4: Input validation (start)           | Security   | 2-4 hr |
| [x]  | RES-2: Graceful shutdown                  | Resilience | 15 min |
| [ ]  | RES-3: cluster                            | Resilience | 15 min |

**Verify:** Full app regression — all screens, all flows.

### Sprint 4 — Polish (ongoing)

| Done | Task                                             | Category   | Time   |
| ---- | ------------------------------------------------ | ---------- | ------ |
| [x]  | DB-7: Add .select() to queries                   | Database   | 1 hr   |
| [ ]  | DB-8: $facet pagination                          | Database   | 2-3 hr |
| [x]  | APP-4: Fine-grained selectors                    | App Perf   | 1-2 hr |
| [ ]  | APP-6: Unify cache tags                          | App Perf   | 15 min |
| [x]  | APP-8 P2: FlashList — Customers/Dealers/Payments | App Perf   | 1 hr   |
| [x]  | APP-8 P3: FlashList — Secondary                  | App Perf   | 1 hr   |
| [x]  | APP-7: Remove Axios                              | App Perf   | 2-3 hr |
| [x]  | CACHE-2: Reference data cache                    | Caching    | 30 min |
| [x]  | CACHE-3: Cache stats endpoint                    | Caching    | 15 min |
| [ ]  | CACHE-4: ETag middleware                         | Caching    | 30 min |
| [x]  | RES-6 + RES-7: CloudWatch + Atlas alarms         | Resilience | 1.5 hr |
| [x]  | RES-8: Emergency runbook                         | Resilience | 1 hr   |
| [ ]  | CW: CloudWatch agent setup                       | Monitoring | 30 min |

---

## What Was Intentionally Deferred

These items from the learning docs are **not included** because they require significant infrastructure changes, external dependencies, or are premature at current scale (~130 orders/day):

| Item                                         | From               | Why Deferred                                      |
| -------------------------------------------- | ------------------ | ------------------------------------------------- |
| Redis/ElastiCache setup                      | Phase 2, Session 5 | Premature — in-process cache covers current scale |
| Token refresh (access + refresh tokens)      | Phase 4D           | Significant change to both API + App auth flow    |
| Secure token storage (react-native-keychain) | Phase 4E           | Requires native module, pod install, testing      |
| BullMQ job queues (SMS/email)                | Phase 7B           | Requires Redis, worker processes                  |
| WebSocket (Socket.io)                        | Phase 7C           | Requires infrastructure, app client changes       |
| Composite/BFF endpoints                      | Phase 3A           | Requires new routes + app migration               |
| Cursor-based pagination                      | Phase 3D           | Requires app + API coordinated change             |
| CloudFront CDN                               | Solutions-Caching  | Good idea but not urgent at current traffic       |
| VPC Peering for Atlas                        | Solutions-Security | AWS infrastructure change                         |
| AWS WAF                                      | Solutions-Security | ~$12/month, good but not critical yet             |
| SSM Session Manager                          | Solutions-Security | AWS infrastructure change (replaces SSH)          |
| CI/CD pipeline (GitHub Actions)              | Phase 6D           | Good but requires test suite first                |
| Structured logging (pino)                    | Phase 6C           | Nice-to-have, current logging works               |
| Event-driven architecture                    | Phase 7E           | Major refactor, premature at current scale        |

These are all valid improvements. They'll be appropriate when the system grows or when you've completed the simpler tasks and want to tackle bigger projects.
