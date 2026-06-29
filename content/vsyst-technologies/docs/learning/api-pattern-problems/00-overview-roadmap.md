# DZZLO OMS Optimization Roadmap

## System Overview

| Component                 | Stack                                              | Key Stats                               |
| ------------------------- | -------------------------------------------------- | --------------------------------------- |
| **API** (`dzzlo_oms_api`) | Node.js, Express 4.19, MongoDB Atlas, Mongoose 9.2 | 80+ endpoints, 22 collections, JWT auth |
| **App** (`dzzlo_oms_app`) | React Native 0.81, Redux Toolkit 2.8, RTK Query    | 204 screens, 29 API slice files         |

## Current Performance Profile

| Endpoint                              | Current DB Calls | Current Latency | Target |
| ------------------------------------- | ---------------- | --------------- | ------ |
| `GET /order_msts/a/poso` (order list) | 9 sequential     | ~200-320ms      | <50ms  |
| `POST /order_msts` (create order)     | 10-12 sequential | ~250-400ms      | <80ms  |
| `PUT /order_msts/process/:id` (OTP)   | 9 sequential     | ~200-300ms      | <50ms  |
| `GET /order_msts/a/po` (single order) | 8 sequential     | ~180-250ms      | <30ms  |
| Any paginated list                    | 2 (count + find) | ~40-80ms        | <20ms  |

## Critical Issues Summary

### Performance

1. **Sequential DB calls** everywhere -- Promise.all() can cut 60-80% latency
2. **O(n\*m) array lookups** in enrichment loops -- Map() for O(1)
3. **Double-query pagination** -- $facet for single query
4. **Missing compound indexes** -- full scans on common queries
5. **Zero caching** -- no Redis, no in-memory, every request hits DB
6. **Logging serializes every response body** -- unnecessary memory + CPU

### Security

1. **Rate limiting DISABLED** (`dzzlo_oms.js:82-86`)
2. **CORS allows all origins** (`dzzlo_oms.js:94`)
3. **No input validation** per endpoint
4. **API key uses `==`** loose comparison (`middlewares.js:12-14`)
5. **No token refresh** -- forced re-login on expiry
6. **AsyncStorage** for tokens (unencrypted on Android)

### App

1. **Dual HTTP clients** (Axios + RTK Query) with different error handling
2. **No RTK Query retry** -- fails immediately on network error
3. **No offline support** -- NetInfo installed but unused
4. **FlatList** missing virtualization props
5. **Re-render cascades** from broad useSelector

## Phase Summary

| Phase | Focus                         | Priority | Timeline       | Key Files                                                     |
| ----- | ----------------------------- | -------- | -------------- | ------------------------------------------------------------- |
| **1** | Database & Query Optimization | P0       | Week 1-2       | `api_v3/services/order_msts.js`, `helpers/advancedResults.js` |
| **2** | Caching Layer (Redis)         | P1       | Week 5-6       | `helpers/auth.js`, new `helpers/cache.js`                     |
| **3** | API Consolidation & BFF       | P2       | Week 7-8       | Route files, `advancedResults.js`                             |
| **4** | Security Hardening            | P0+P2    | Week 1-2, 7-8  | `dzzlo_oms.js`, `helpers/middlewares.js`                      |
| **5** | App Performance               | P1+P2    | Week 3-4, 9-10 | `createApi.js`, `auth.js` slice, all screens                  |
| **6** | Automation & Monitoring       | P3       | Week 11-12     | New monitoring infrastructure                                 |
| **7** | Scalability Architecture      | P2+P3    | Week 9-12      | `ecosystem.config.js`, new queue workers                      |

## Expected Outcomes

| Metric                   | Before     | After Phase 1-2 | After All Phases |
| ------------------------ | ---------- | --------------- | ---------------- |
| Order list latency       | ~300ms     | ~30ms           | <15ms (cached)   |
| Order creation latency   | ~350ms     | ~80ms           | <50ms            |
| DB calls per order list  | 9          | 2 waves         | 1 (cached)       |
| API calls per screen     | 3-4        | 2-3             | 1 (composite)    |
| Security vulnerabilities | 6 critical | 2 remaining     | 0                |
| Cache hit rate           | 0%         | 60%+            | 85%+             |

## File Index

- [Phase 1: Database & Query Optimization](phase-1-database-query-optimization.md)
- [Phase 2: Caching Layer](phase-2-caching-layer.md)
- [Phase 3: API Consolidation & BFF](phase-3-api-consolidation-bff.md)
- [Phase 4: Security Hardening](phase-4-security-hardening.md)
- [Phase 5: App Performance](phase-5-app-performance.md)
- [Phase 6: Automation & Monitoring](phase-6-automation-monitoring.md)
- [Phase 7: Scalability Architecture](phase-7-scalability-architecture.md)
