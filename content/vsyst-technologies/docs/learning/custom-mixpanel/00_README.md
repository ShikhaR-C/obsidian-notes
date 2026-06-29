# Custom Mixpanel Analytics System

## Overview

DZZLO OMS currently has zero analytics/event tracking across its two projects (dzzlo_oms_api backend + dzzlo_oms_app React Native mobile). This plan creates a complete custom Mixpanel-like analytics platform with a **third project** — a Next.js dashboard webapp.

## Architecture

```
dzzlo_oms_app (React Native)     dzzlo_oms_api (Express+MongoDB)     dzzlo_analytics (Next.js)
  [Event SDK]  ──────────────>     [Ingestion + Query APIs]     <────────  [Dashboard UI]
                                   [MongoDB Storage]
                                   [Aggregation Jobs]
```

## Phase Index

| #   | Phase                          | File                                                             | Deliverable                            | Depends On |
| --- | ------------------------------ | ---------------------------------------------------------------- | -------------------------------------- | ---------- |
| 1   | Event Storage + Ingestion API  | [01_event_storage_ingestion.md](./01_event_storage_ingestion.md) | MongoDB schemas + batch endpoint       | —          |
| 2   | Frontend Analytics SDK         | [02_frontend_sdk.md](./02_frontend_sdk.md)                       | Event queue, sessions, offline support | Phase 1    |
| 3   | Business Event Instrumentation | [03_business_events.md](./03_business_events.md)                 | Track orders, invoices, payments, auth | Phase 2    |
| 4   | Query APIs                     | [04_query_apis.md](./04_query_apis.md)                           | Funnels, retention, DAU/MAU endpoints  | Phase 1    |
| 5   | Pre-Computed Aggregations      | [05_aggregations.md](./05_aggregations.md)                       | Daily rollup jobs for performance      | Phase 4    |
| 6   | Next.js Dashboard Project      | [06_nextjs_dashboard.md](./06_nextjs_dashboard.md)               | New webapp with charts, funnels, grids | Phase 4+5  |
| 7   | Cross-Project Correlation      | [07_correlation_advanced.md](./07_correlation_advanced.md)       | User timeline, error correlation       | Phase 5+6  |

## Phase Dependencies

```
Phase 1 (Backend Storage + Ingestion)
  ├──> Phase 2 (Frontend SDK) ──> Phase 3 (Business Events)
  │                                        │
  └──> Phase 4 (Query APIs) <──────────────┘
            │
            v
       Phase 5 (Pre-Computed Aggs)
            │
            v
       Phase 6 (Next.js Dashboard)
            │
            v
       Phase 7 (Correlation + Advanced)
```

Phases 2+3 can be developed in parallel with Phase 4 by different developers.

## Key Technical Decisions

| Decision         | Choice                       | Rationale                                                          |
| ---------------- | ---------------------------- | ------------------------------------------------------------------ |
| Event DB         | MongoDB (same as OMS)        | Already in stack, no new infra needed                              |
| Event TTL        | 90 days auto-cleanup         | TTL index prevents unbounded growth                                |
| SDK Pattern      | Singleton module (not Redux) | Must be callable from non-React code (interceptors, thunks)        |
| Batching         | 20 events / 30s flush        | Prevents N+1 API calls per session                                 |
| Sessions         | Client-generated UUID        | Works offline, no server roundtrips                                |
| Dashboard        | Separate Next.js webapp      | Rich visualizations, charts, tables — not constrained by mobile UI |
| Access           | SuperAdmin only              | Analytics dashboard restricted to admin role                       |
| New Dependencies | Minimal                      | uuid on backend; no new deps for frontend SDK core                 |

## Existing Infrastructure Leveraged

- **Request logging middleware** (`helpers/middlewares.js:119-174`) — already captures method, URL, response time, status, user, device metadata to MongoDB `logs` collection
- **Device metadata** — already collected on every request via `meta` header (appName, version, deviceBrand, deviceOS, etc.)
- **Error boundary** (`components/Error/ErrorBoundary.js`) — already reports crashes to backend
- **Auth system** — JWT with user roles, company context, scopes
- **OneSignal** — push notification events available for tracking
- **RTK Query** — existing API pattern for new analytics endpoints
- **Axios interceptors** — hook point for automatic API call tracking

## Project Scope

| Project               | Role                                                       | Tech                                 |
| --------------------- | ---------------------------------------------------------- | ------------------------------------ |
| dzzlo_oms_api         | Event storage, ingestion, query APIs, aggregation jobs     | Node.js + Express + MongoDB          |
| dzzlo_oms_app         | Event SDK, screen tracking, business event instrumentation | React Native + Redux Toolkit         |
| dzzlo_analytics (NEW) | Dashboard webapp with visualizations                       | Next.js + Tailwind + Tremor/Recharts |
