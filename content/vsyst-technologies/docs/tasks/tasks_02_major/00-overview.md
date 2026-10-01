# Task Overview — tasks_02 — Deferred Strategic Initiatives

> Five strategic initiatives previously deferred from `tasks_01/00-overview.md` ("What Was Intentionally Deferred" table).
> These are larger, cross-cutting changes that impact both `dzzlo_oms_api` and `dzzlo_oms_app` and often require coordinated rollout.
>
> Unlike `tasks_01` (which is a punch list of small, independent optimizations), `tasks_02` is a set of **multi-phase initiatives**. Each file defines an initiative, its phases, and the smaller steps inside each phase.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Of the five initiatives, 03 (BFF) is done in a different form for two screens — the screen redesign's `/api/v4/screens/*` read models — while its six planned v3 screens are untouched; 04 (cursor paging) and 05 (CI/CD) are partly done (v4 only; CI yes, CD no); 01 (token refresh) and 02 (websockets) are not started (roll-up: 3 🟡, 2 ⬜). Six new tasks: four from the team registry (X-V4-1, X-V4-2, X-CI-1, X-CI-2) and two of this folder's own (T02-N1, T02-N2). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item                                                              | Status | What exists now (evidence)                                                                                                                                                                                                                                                                                                                                         | What is left / next step                                                                                                                                                                                                                             |
| ----------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [01 Token refresh](./01-token-refresh.md)                         | ⬜     | Nothing of the plan: no refresh route or token field (API code has no refresh logic); tokens still last 30 days (api:`.env.example:28`, api:`api_v3/controllers/auth/index.js:38-44`); the app keeps token + `expiryDate` in AsyncStorage (app:`src/store/slices/auth.js:22-38`) and logs out on any 401 (app:`src/store/middleware/rtkQueryErrorLogger.js:30-34`) | All 7 phases (Step 5.4 ❌ — axios is gone). The v4 routes use the same bearer, so the flag flip must cover `/api/v4`; T02-N1 as an interim fix                                                                                                       |
| [02 WebSocket](./02-websocket-realtime.md)                        | ⬜     | `socket.io ^4.8.3` is an API dependency (api:`package.json:50`) with commented code only (api:`helpers/middlewares.js:340-386`); no app client (app:`src/screens/Demo/Dashboard/index.js:30` holds a commented import). The v2 lists refresh on refocus and pull only                                                                                              | All 8 phases. If production is two servers (X-OPS-1 in tasks_01), rooms need the Redis adapter or sticky sessions from day one; for v2 lists the socket bus would invalidate `relations/CUSTOMERS_LIST` and `order_msts_POST/LIST`                   |
| [03 BFF endpoints](./03-bff-composite-endpoints.md)               | 🟡     | The pattern shipped as v4 read models (redesign D2): `POST /api/v4/screens/customers` (11 reads, constant in N) and `POST /api/v4/screens/daily-summary` (7 / 6 round trips) plus one command, `PUT /api/v4/users/prefs/:screen` (api:`api_v4/routes/screens.js:30-48`); Phase 1's conventions exist in `api_v4/lib/*`                                             | The six planned screens (NewOrder, Accounts, CompanyUsers, SisterCompanies, NewPayment, Invoice detail) are still v1 on v3 — each would become a v4 read model under the redesign's per-screen loop; X-V4-1, X-V4-2, T02-N2                          |
| [04 Cursor pagination](./04-cursor-pagination-infinite-scroll.md) | 🟡     | v4 keyset paging, no counts (api:`api_v4/lib/cursor.js`), on the two v2 lists at 12 rows a page; app next pages via app:`src/store/apis/v4/nextPage.js` and app:`src/screens/v2/shared/useNextPage.js`                                                                                                                                                             | v3 is still `skip`/`limit` with a count per page and the `limit = 0` default (api:`helpers/advancedResults.js:49,88,106`); every v1 list is offset-paged. Phases 2, 5, 7 (dual-mode v3) look superseded by v3's feature freeze — the user to confirm |
| [05 CI/CD](./05-cicd-github-actions.md)                           | 🟡     | CI in both repos — API `.github/workflows/test.yml` (`yarn test:full`, since `f31d1f6`, 2026-07-10), app `.github/workflows/test.yml` (Jest, since `1630f5cf`); the manual release gate api:`scripts/release_gate.sh`; a manual canary in api:`docs/runbook.md:121-156`                                                                                            | No lint, type-check or build in CI; no CD; no branch protection (waits on a GitHub plan decision); `slave` pushes get no run — X-CI-1, X-CI-2. Master's red month-end run is X-REL-1 in tasks_12                                                     |

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
- Token helper: `/helpers/auth.js` `getUserFromToken()` ~~has 3-min in-memory cache~~ **2026-10-01:** has no cache — `d6ad454` moved it to `api_v3/auth.js` (30 s), which the global per-request path does not use (X-PERF-1 in tasks_01)
- Socket.io: present in `package.json`, **all code commented out** in `/helpers/middlewares.js:263-293` (**2026-10-01:** still commented out, now at `:340-386`)
- Push: OneSignal (not FCM direct), via `/api_v3/controllers/App/notification.js`
- Pagination: offset-based everywhere via `/helpers/advancedResults.js`, **default limit = 0 (returns all!)** — this is a latent bug
- ~~No GitHub Actions, no Dockerfile, no CI.~~ **2026-10-01:** GitHub Actions CI since 2026-07-10 (`f31d1f6`); still no Dockerfile. Deploy = SSH + `git pull` + `pm2 restart`
- 239 Jest test files in `test/`, `mongodb-memory-server` ready to use
- PM2 config: `ecosystem.config.js` (single app, no cluster mode yet)

**App (`dzzlo_oms_app`):**

- RN 0.84.1, React 19.2.3, new arch enabled (Hermes + TurboModules + Fabric)
- Token stored in `AsyncStorage` as `'userData'` JSON (plain-text on Android)
- RTK Query base: `/src/store/apis/createApi.js`, custom `baseQueryWithSmartRetry` (2 retries, not for 4xx)
- ~~Axios fallback: `/src/utils/API/index.js` — logout on any 401, no refresh attempt~~ **2026-10-01:** axios was removed on 2026-04-14 (`0bfdd36f`); the logout on 401 now lives in `src/store/middleware/rtkQueryErrorLogger.js`
- 18 API slices, ~120 endpoints, ~45 screens mapped
- Pagination helpers exist (`/src/store/apis/paginationHelpers.js`) with merge + serializeQueryArgs ~~**but infinite scroll is not wired** on any screen yet~~ **2026-10-01:** a few v1 surfaces already paged by `page` (see doc 04), and the two v2 lists page by cursor
- FlashList rolled out (APP-8 P1/P2/P3 done per `tasks_01`)
- Android: keystore `dzzlooms-upload-key.keystore`, package `in.vsyst.dzzlooms`, ~~versionCode 100, versionName "1.76"~~ **2026-10-01:** versionCode 105, versionName "1.79"
- iOS: CocoaPods, OneSignal service extension, no Fastlane
- 238 Jest test files, ESLint 9 configured
- CodePush: env vars present, code commented out
- Firebase: config files present, ~~code disabled~~ **2026-10-01:** analytics, crashlytics and perf are live (`@react-native-firebase/*` 24.0.0)

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

## New tasks — from the app v2 / API v4 review (2026-10-01)

Canonical IDs (`X-…`) come from the team registry; `T02-N…` are this folder's own. The linked doc owns the row and repeats it. Rows for tasks another folder owns are only referenced in the docs: X-SEC-1, X-PERF-1, X-PERF-2, X-OPS-1, X-REL-2, X-APP-2, X-APP-3 (tasks_01) and X-REL-1 (tasks_12).

| ID     | Task                                                                                                                                                                                                                                                                                                                        | Why (evidence)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Project   | Size | Depends on                             |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | ---- | -------------------------------------- |
| X-V4-1 | 🆕 [03](./03-bff-composite-endpoints.md) — Close the v4 foundation gaps: a JSON `NOT_FOUND` / 405 answer for unknown paths and methods inside `/api/v4`, a v4-shaped answer (with `error_code`) for a malformed JSON body, and a `maxTimeMS` on the app-features read                                                       | `buildV4` mounts only the modules and `errorHandler` (api:`api_v4/index.js:69-84`), so an unknown path falls through to Express's HTML 404; a malformed body fails in the global `express.json` and is answered by the v3 handler, which sends no `error_code` (api:`dzzlo_oms.js:59,136`, api:`helpers/error.js:31-34`; inferred, no test); `NOT_FOUND` / `CONFLICT` are catalogued but never raised (api:`api_v4/lib/errors.js:27-34`); `counters.findOne` has no `maxTimeMS` (api:`helpers/appFeatures.js:70`) | API       | S    | —                                      |
| X-V4-2 | 🆕 [03](./03-bff-composite-endpoints.md) — Decide where business rules live. The v4 Customers read model holds its own copies — credit ratio, FY ledger fold, outstanding PO/SO aggregates, opening balance — plus a new integer-paise money rule, each held to v3 by parity tests. A question for the user, not a decision | api:`api_v4/readmodels/customers.js:108-148,270-347,476-570`, api:`api_v4/lib/money.js:1-22` against api:`.ai/agents/versioning-agent.md:68` ("read models compose `api_v3/services`, they do not re-implement rules"), redesign D1 and this plan's principle 5 (§4.1)                                                                                                                                                                                                                                            | API       | M    | user decision                          |
| X-CI-1 | 🆕 [05](./05-cicd-github-actions.md) — Run CI on pushes to the integration branch `slave` (today only PRs and `master` pushes run), and either add a deploy workflow or record that deploys stay manual                                                                                                                     | api:`.github/workflows/test.yml:3-7`, app:`.github/workflows/test.yml:3-7`; PR #46's merge into `slave` (`86083ca`, 2026-09-30 23:08Z) produced no run (`gh run list --commit`); neither repo has a deploy workflow — the API deploys by the manual canary in api:`docs/runbook.md:121-156`                                                                                                                                                                                                                       | app + API | S    | X-OPS-1 (tasks_01) for the deploy half |
| X-CI-2 | 🆕 [05](./05-cicd-github-actions.md) — Give app CI a lint job (and a type-check or build job), set a `timeout-minutes`, and bring the Jest run back under the house "app ≤ 2 min" budget — or change the budget                                                                                                             | app:`.github/workflows/test.yml` runs `yarn test` only, on PRs and pushes to `main`; Jest took 128.8 s, 157.5 s and 171.3 s in runs 36760183167, 36779552256, 36708907732, against app:`.github/PULL_REQUEST_TEMPLATE.md:13` and app:`AI.md:89`; `yarn lint` exists (app:`package.json:25`) but CI never runs it                                                                                                                                                                                                  | app       | S    | —                                      |
| T02-N1 | 🆕 [01](./01-token-refresh.md) — Make the 401 logout latch hold until the logout has finished, pinned by a Tier 2 test (a burst of parallel 401s dispatches one `logoutUser`)                                                                                                                                               | The latch is set, the async thunk dispatched and the latch cleared in the same tick (app:`src/store/middleware/rtkQueryErrorLogger.js:30-34`), so every rejected action of a burst passes the check — several logouts per burst (inferred from the code, not observed). 01 Phase 5's mutex replaces this path; this is the interim fix                                                                                                                                                                            | app       | XS   | —                                      |
| T02-N2 | 🆕 [03](./03-bff-composite-endpoints.md) — Enforce field-level authorization on the server for the permission-gated fields of the v4 read models, or record that gating them in the app is accepted                                                                                                                         | §11 item 6 asks for server-side field authorization; the v4 Customers read model kept v3's model, in which the membership permission is applied only in the app (app:`src/helpers/Permissions/index.js:1-31` — "These decide what is _rendered_"), so v4 neither widened nor narrowed access                                                                                                                                                                                                                      | API       | S    | user decision                          |
