# Task Overview — tasks_02 — Deferred Strategic Initiatives

> Five strategic initiatives previously deferred from `tasks_01/00-overview.md` ("What Was Intentionally Deferred" table).
> These are larger, cross-cutting changes that impact both `dzzlo_oms_api` and `dzzlo_oms_app` and often require coordinated rollout.
>
> Unlike `tasks_01` (which is a punch list of small, independent optimizations), `tasks_02` is a set of **multi-phase initiatives**. Each file defines an initiative, its phases, and the smaller steps inside each phase.

---

## Why These 5 Were Picked

The user selected these from the deferred list in `tasks_01/00-overview.md`:

| #   | Initiative                                | Originally Deferred From | Why It Matters Now                                                                                                                   |
| --- | ----------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Token Refresh (access+refresh)            | Phase 4D                 | 30-day JWTs are a stolen-token blast-radius problem. Short access tokens + refresh rotation is the industry standard.                |
| 2   | WebSocket / Socket.io                     | Phase 7C                 | Real-time company/status changes across all active devices of a user; foundation for future push features.                           |
| 3   | Composite / BFF Endpoints                 | Phase 3A                 | Heavy screens (NewOrder, Accounts, CompanyUsers) fire 3-5 parallel requests. BFF collapses them into one.                            |
| 4   | Cursor-Based Pagination + Infinite Scroll | Phase 3D                 | Offset pagination drifts on inserts, gets slower as pages grow. Cursor pagination + FlashList infinite scroll is the modern pattern. |
| 5   | CI/CD Pipeline (GitHub Actions)           | Phase 6D                 | Currently manual SSH + `pm2 restart`. Bus-factor = 1. No automated tests before deploy. Highest operational risk.                    |

---

## Category Index

| File                                                                                 | Initiative                          | Scope          | Risk   | Coordination Required                        |
| ------------------------------------------------------------------------------------ | ----------------------------------- | -------------- | ------ | -------------------------------------------- |
| [01-token-refresh.md](./01-token-refresh.md)                                         | Access + Refresh token auth         | API + App      | High   | Yes — must deploy API first, then App        |
| [02-websocket-realtime.md](./02-websocket-realtime.md)                               | Socket.io real-time events          | API + App      | Medium | Yes — graceful fallback if socket down       |
| [03-bff-composite-endpoints.md](./03-bff-composite-endpoints.md)                     | Screen-specific BFF endpoints       | API + App      | Low    | Yes — additive, old endpoints keep working   |
| [04-cursor-pagination-infinite-scroll.md](./04-cursor-pagination-infinite-scroll.md) | Cursor pagination + RTK Query merge | API + App      | Medium | Yes — additive, old pagination keeps working |
| [05-cicd-github-actions.md](./05-cicd-github-actions.md)                             | CI/CD for both API and App          | Infrastructure | Medium | No — infra only, no runtime changes          |

---

## Cross-Initiative Dependency Graph

```
                    ┌──────────────────────┐
                    │  05 CI/CD            │ ◄──── FOUNDATIONAL. Set up first so every
                    │  (GitHub Actions)    │       subsequent change goes through a
                    └──────────┬───────────┘       tested pipeline instead of SSH-pushes.
                               │
                               ▼
        ┌──────────────────────────────────────────────┐
        │                                              │
        ▼                                              ▼
┌───────────────────┐                        ┌───────────────────┐
│ 01 Token Refresh  │                        │ 04 Cursor Paging  │
│   (P0 security)   │                        │  + Infinite Scroll│
└─────────┬─────────┘                        └─────────┬─────────┘
          │                                            │
          │  provides                                  │ provides
          │  stable auth                               │ the list UX
          │  for long-lived                            │ that BFF and
          │  sockets                                   │ sockets rely on
          ▼                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│   02 WebSocket / Socket.io (real-time company/status events)    │
└─────────┬───────────────────────────────────────────────────────┘
          │  provides
          │  push channel
          │  for BFF cache invalidation
          ▼
┌─────────────────────────────────────┐
│   03 BFF / Composite Endpoints      │
└─────────────────────────────────────┘
```

**Recommended order of execution:**

1. **`05 CI/CD`** first — nothing else should be shipped without it. Even if the other 4 initiatives slip, CI/CD alone pays for itself.
2. **`01 Token Refresh`** second — security fix, and a prerequisite for robust long-lived WebSocket connections (a 30-day JWT socket is a bigger footgun than a 30-day HTTP JWT).
3. **`04 Cursor Pagination`** third — a self-contained API + App change with immediate UX win (infinite scroll) and performance win (no more `skip()` over 10k docs).
4. **`02 WebSocket`** fourth — builds on `01` (refresh tokens keep sockets alive) and can invalidate `04`'s cached pages via server-pushed events.
5. **`03 BFF Endpoints`** last — synthesizes everything. Needs `02` to invalidate its denormalized responses cleanly.

---

## Current Baseline (from codebase research)

Key facts discovered during planning (full details in each file):

**API (`dzzlo_oms_api`):**

- Active version: `api_v3` (v1 disabled, v2 fallback)
- Auth: JWT only, **30-day expiry**, no refresh token. Stored in `User.password`/`co_id`/`role` claims.
- Token helper: `/helpers/auth.js` `getUserFromToken()` has 3-min in-memory cache
- Socket.io: present in `package.json`, **all code commented out** in `/helpers/middlewares.js:263-293`
- Push: OneSignal (not FCM direct), via `/api_v3/controllers/App/notification.js`
- Pagination: offset-based everywhere via `/helpers/advancedResults.js`, **default limit = 0 (returns all!)** — this is a latent bug
- No GitHub Actions, no Dockerfile, no CI. Deploy = SSH + `git pull` + `pm2 restart`
- 239 Jest test files in `test/`, `mongodb-memory-server` ready to use
- PM2 config: `ecosystem.config.js` (single app, no cluster mode yet)

**App (`dzzlo_oms_app`):**

- RN 0.84.1, React 19.2.3, new arch enabled (Hermes + TurboModules + Fabric)
- Token stored in `AsyncStorage` as `'userData'` JSON (plain-text on Android)
- RTK Query base: `/src/store/apis/createApi.js`, custom `baseQueryWithSmartRetry` (2 retries, not for 4xx)
- Axios fallback: `/src/utils/API/index.js` — logout on any 401, no refresh attempt
- 18 API slices, ~120 endpoints, ~45 screens mapped
- Pagination helpers exist (`/src/store/apis/paginationHelpers.js`) with merge + serializeQueryArgs **but infinite scroll is not wired** on any screen yet
- FlashList rolled out (APP-8 P1/P2/P3 done per `tasks_01`)
- Android: keystore `dzzlooms-upload-key.keystore`, package `in.vsyst.dzzlooms`, versionCode 100, versionName "1.76"
- iOS: CocoaPods, OneSignal service extension, no Fastlane
- 238 Jest test files, ESLint 9 configured
- CodePush: env vars present, code commented out
- Firebase: config files present, code disabled

**Separate git repos:** API and App are sibling directories but have **independent `.git` dirs**. CI/CD (05) must therefore be set up twice.

---

## How to Use These Files

1. **Read `00-overview.md` first** (this file) — understand the ordering and why.
2. **Pick one initiative** — do not interleave phases across initiatives. Each file is designed to be completed end-to-end.
3. **Execute phases in order** — each phase in a file has a "Definition of Done" section. Don't start phase N+1 until phase N is verified in staging.
4. **Use the "Technical deep-dive" sections** — they explain the _why_ behind architectural choices, so future-you (or a teammate) can make judgment calls on edge cases.
5. **Check "Rollback plan" sections** — each initiative has a named rollback strategy. These are cross-cutting changes; know how to back out before you start.

---

## What's NOT Covered Here

From the original deferred list, these remain out of scope for `tasks_02`:

| Item                                           | Why Still Deferred                                                         |
| ---------------------------------------------- | -------------------------------------------------------------------------- |
| Redis / ElastiCache                            | Not yet needed at ~130 orders/day. Revisit when in-process cache thrashes. |
| Secure token storage (`react-native-keychain`) | Worth doing inside `01 Token Refresh` — see Phase 6 optional step.         |
| BullMQ job queues                              | Requires Redis. Defer until scale demands it.                              |
| CloudFront CDN                                 | Not urgent at current traffic.                                             |
| VPC Peering for Atlas                          | AWS infra change. Separate project.                                        |
| AWS WAF                                        | Nice-to-have, not critical.                                                |
| Structured logging (pino)                      | Pre-existing logging works.                                                |
| Event-driven architecture                      | Major refactor, premature.                                                 |

---

## File Conventions Used Across `tasks_02`

Every initiative file follows the same template:

1. **TL;DR** — one-paragraph executive summary.
2. **Current state** — what exists today, with exact file paths and line numbers.
3. **Problem statement** — what's broken or missing, with concrete examples.
4. **Research & technical deep-dive** — patterns, alternatives, why-this-approach.
5. **Target architecture** — the "after" picture with diagrams.
6. **Phased rollout** — P1 → Pn, each phase split into steps with definition-of-done.
7. **Benefits** — quantified where possible (latency, RPS, LoC saved, risk reduced).
8. **Risks & rollback** — what can break, how to back out.
9. **Testing strategy** — unit, integration, manual QA checklist.
10. **Post-launch monitoring** — what to watch in logs/metrics for the first week.

Each phase step is small enough to ship in one PR and testable in isolation.
