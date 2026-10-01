# Plan: Partner (B2B) Open API on `api_v3` — Vertical-SaaS Platform Expansion

> **Source prompt:** `../../prompt-open-api-v3-partner-tutorial.md` (paste that into Claude Code inside `dzzlo_oms_api` when implementing). This folder is the phase-wise **design plan** that prompt asks for — design doc first, code second — following the workspace convention of `tasks_09_sadmin_settings` / `tasks_10_analytics_events`.
>
> **Repo under change:** `dzzlo_oms_api` (Node.js + Express 5, Mongoose 9, MongoDB). Versioned APIs live under `api_v3/`, mounted at `/api/v3` by `api_v/api3.js`. This plan lives in the notes vault; snippets are written in that repo's idiom (`asyncHandler`, `ErrorResponse`, `timingSafeCompare`) and must be validated against the real files when implementing.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Nothing is built: all 7 phases are ⬜ — no partner router, `api_clients`, idempotency store, usage meter or OpenAPI spec exists (grep at `6d41ce5`). The plan targets `api_v3`, which the API's own rule has frozen for features since 2026-09-04 (`AI.md:85-86`), and it designs from scratch pieces that `api_v4/lib` now provides — 8 new tasks at the end, and open question 8 (mount on v4 instead of v3?) is for the user. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item | Status | What exists now (evidence) | What is left / next step |
| --- | --- | --- | --- |
| Phase 1 — partner identity & credentials | ⬜ | No `api_clients` schema, issuance script or `PARTNER_JWT_SECRET` (`git grep` at `6d41ce5` → 0). `timingSafeCompare` exists but is module-private (`helpers/middlewares.js:6-13`) | Settle question 8 (T11-N1); the schema goes in `models/`, which needs approval (T11-N7) |
| Phase 2 — auth middleware + isolated router | ⬜ | No token endpoint, `partner_auth`, partner gate or router. The v4 hub runs `api_key_v3 → protect → check_user_company_status` before every module and has no pre-auth slot (`api_v4/index.js:12,72-74`) | Mount point ahead of the app chain (T11-N2); tenant helper for a machine principal (T11-N3); a company-level "active" notion (T11-N8) |
| Phase 3 — order + voucher endpoints, idempotency | ⬜ | Create logic already lives in services: `createMstTrn` (`api_v3/services/order_msts.js:755`) and three voucher creators (`api_v3/services/voc_msts.js:700,764,848`), all taking the tenant ids as input. No Idempotency-Key handling anywhere (`api_v4/controllers/users.js:26` says so for v4) | Build on the v4 validator and envelope (T11-N4); the idempotency store as planned |
| Phase 4 — security measures | ⬜ | The only principal-keyed limiter is the v4 screens valve — per user, in memory, per process (`api_v4/lib/rateLimit.js:23-52`). No global rate limit and an open CORS policy yet (tasks_01 SEC-2, SEC-5) | Shared limiter store (T11-N5); the tasks_01 hardening items in the go-live gate (T11-N6) |
| Phase 5 — usage logging & attribution | ⬜ | No `partner_usage`. `logging()` writes `logs` only in production (`helpers/middlewares.js:220`), with the whole user document (`:250`) and a wall-clock-shifted `timeIST` (`:255-257`); `models/logs.js` has no index or TTL | As planned; IST windows from the ledger's helpers (question 7) |
| Phase 6 — cost metering | ⬜ | No price book, quota counters, roll-up job or reconciliation; no scheduler dependency in `package.json` | Choose a scheduler; prices are commercial (not assessed) |
| Phase 7 — rollout, docs, versioning | ⬜ | No OpenAPI/swagger, sandbox tenant, `PARTNER_API_ENABLED` flag or partner docs. `docs/testing.md:245` holds a flow-map placeholder: "Partner API (tasks_11) — not yet implemented" | A partner version path independent of the app's `/api/v4` (T11-N1) |
| Source prompt (`prompt-open-api-v3-partner-tutorial.md`, this folder) | ⬜ | Written 2026-07 for v3; lists v3 files only | Re-point it to v4 if question 8 goes that way |

## Why — the vertical-SaaS framing

DZZLO OMS is a **vertical SaaS**: the system of record for a specific industry's dealer ↔ customer supply-chain operations — orders, invoices, payments/vouchers, credit limits, vehicles/OTP-verified deliveries. Vertical SaaS companies win a category by owning the workflow; the natural second act is becoming the **platform**: letting the rest of a tenant's software stack write into the system of record instead of humans re-keying data in the app.

Concretely, "partners" are:

| Partner type | Example | v1? |
| --- | --- | --- |
| Tenant's own in-house software | A dealer's custom ERP posting orders it takes on its website | ✅ primary |
| Industry ISVs integrating on a tenant's behalf | Accounting/ERP vendors (Tally-class), storefronts, WMS/TMS | ✅ (one credential per tenant) |
| Aggregators / marketplaces spanning many tenants | Industry marketplace placing orders into many companies | ❌ v2 (needs per-tenant consent/grant model) |

This is also an **expansion-revenue** motion: API usage is metered per partner per endpoint and billed (Phase 6), folded into the tenant's existing subscription invoice — the classic vertical-SaaS monetization ladder (seats → workflow add-ons → platform/API usage).

## Goal (v1 scope)

Machine-to-machine calls from a partner backend — **not** a human on the mobile app. Partners must be able to:

1. **Place an order** → `order_msts`
2. **Create a voucher** → `voc_msts`

The surface is a distinct, sandboxed router (`/api/v3/partner/...`), independently gated — **not** a re-export of existing app routes.

**Non-goals (v1):** read/list APIs, webhooks to partners, self-serve partner signup UI, multi-tenant grants for one credential, any change to the mobile-app auth path.

## Vocabulary

| Term | Meaning here |
| --- | --- |
| **Tenant** | A company in DZZLO (`co_id` → `companies`). The unit of data isolation. |
| **Partner** | The external organization whose software calls the API. |
| **API client** | One credential record (`api_clients` doc): `client_id` + hashed secret, bound to exactly **one** tenant in v1. |
| **Scope** | Least-privilege grant on a client: `orders:write`, `vouchers:write`. |
| **Env** | `sandbox` (free, test tenant) vs `production` (billable). Separate credentials. |
| **Billable unit** | One successful (2xx), non-replay call to a priced endpoint. |

## Security posture — non-negotiables

Security is the headline requirement of this plan. In a multi-tenant vertical SaaS, a partner-API breach is a **cross-tenant data incident** for industry companies that trust us as their system of record. These invariants hold across every phase; Phase 4 is the deep-dive:

1. **Tenant isolation is absolute.** `co_id` is always taken from the verified credential — never from the request payload. A partner credential can only ever write into its own tenant.
2. **Least privilege by default.** Scopes are explicit grants; an orders-only key cannot touch vouchers, and no partner credential can reach any app route.
3. **No long-lived plaintext secrets.** Secrets are shown once, stored only as hashes, compared with `timingSafeCompare`, rotatable with overlap, and never logged.
4. **Separate trust domains.** Partner tokens use a different signing secret + `aud`/`iss` than the mobile JWT — an app token fails on partner routes and vice-versa. A bug in one surface must not widen the other.
5. **Same domain rules as the app.** Partner writes go through the **existing** order/voucher services (credit checks, company-status gates, validation) — no forked, weaker path.
6. **Everything attributable.** Every call is logged with `client_id` + tenant + endpoint + outcome (Phase 5) — the billing meter doubles as the audit trail.
7. **Abuse is contained automatically.** Per-client rate limits and quotas, replay protection, failed-auth lockout, auto-suspend.

## What already exists (read before implementing — do NOT rebuild)

| Concern | Where | Reuse how |
| --- | --- | --- |
| Global middleware chain | `dzzlo_oms.js` — `api_key_v1()`, `logging()`, `check_user_version()`, `helmet`, `sanitizeMongo`, `cors`, `compression` | Partner router keeps `helmet`/`sanitizeMongo`/`compression`; is **exempted** from app-key/JWT gates (Phase 2). |
| v3 route aggregation | `api_v/api3.js` — applies `api_key_v3()`, `check_user_company_status()` | Mount `partnerRouter` here with its own gate chain. |
| App auth | `api_v3/auth.js` — `getUserFromToken`, `protect`, `authorize`, `scope()`, per-process `userCache` | Do **not** reuse the JWT path; **do** mirror the `scope()` and cache patterns. |
| Key check + logging | `helpers/middlewares.js` — `api_key_v3()` (hex key + `timingSafeCompare`), `logging()` → `logs`, company-status gate | Reuse `timingSafeCompare`; partner variants of logging/status gates. |
| Request-log schema | `models/logs.js` | Ops logging stays; billing-grade `partner_usage` added (Phase 5). |
| User model | `models/users.js` — `SCOPE_ENUM`, `companies[]`, `co_id`, `role` | Vocabulary alignment for partner scopes. |
| Public endpoint pattern | `api_v3/{controllers,routes}/open_apis/` | Model the partner controller/route layout on this. |
| Target write models | `models/order_msts.js`, `models/voc_msts.js` + their v3 controllers/services | **Reuse the same create logic** — extract to a shared service if currently inline; never fork. |

**Note (2026-10-01):** this table predates `api_v4/`. One correction: `timingSafeCompare` is not exported (`helpers/middlewares.js:6-13`), so reuse means an export (a `helpers/` edit, approval per `AI.md:87-90`) or a partner-local copy. One addition: the global chain now also mounts `/api/v4` (`dzzlo_oms.js:121`). Reusable from `api_v4/lib/` if question 8 allows: `validate.js` (house validator, D7), `errors.js` + `respond.js` (envelope and frozen error catalogue, D6), `roles.js`, `tenancy.js` (`tenantOf`, `scopeFilter`, `assertRelation`, D5), `cursor.js`, `compose.js` (`runParallel`, `runSettled`), `limits.js` (`maxTimeMS`), `rateLimit.js` (per user, in memory, per process) — see T11-N2 to T11-N5.

## Architecture

```
api_v3/
  models/
    api_clients.js            ← NEW  partner credential + tenant binding + tier   (Phase 1)
    idempotency_keys.js       ← NEW  retry-dedupe store                           (Phase 3)
    partner_usage.js          ← NEW  per-call metering/audit record               (Phase 5)
    partner_pricing.js        ← NEW  versioned price book + tiers                 (Phase 6)
  middleware/
    partner_auth.js           ← NEW  token verify → req.partner                   (Phase 2)
    partner_scope.js          ← NEW  least-privilege gate                         (Phase 2)
    partner_rate_limit.js     ← NEW  per-client burst limit + monthly quota       (Phase 4)
    idempotency.js            ← NEW  Idempotency-Key handling                     (Phase 3)
    partner_meter.js          ← NEW  usage + billing hook (unbypassable)          (Phase 5/6)
  controllers/partner/
    token.js orders.js vouchers.js credentials.js
  routes/partner/
    index.js                  ← assembles the gated router
api_v/api3.js                 ← EDIT mount partnerRouter at /partner
```

Request lifecycle for a partner call:

```
TLS → helmet/HSTS → body-size limit → sanitizeMongo
   → partner_auth        (Bearer token → api_client, env, tenant)
   → tenant status gate  (owning co_id active?)
   → partner_rate_limit  (burst by client_id) → quota check
   → partner_scope       ('orders:write' | 'vouchers:write')
   → partner_meter       (arms res.on('finish') usage write)
   → idempotency         (dedupe on Idempotency-Key)
   → controller → EXISTING order/voucher create service
   → partner-safe error envelope (stable codes, request_id, no internals)
```

**Note (2026-10-01):** `api_v3/` has only `controllers/`, `routes/` and `services/` (tree at `6d41ce5`), and every Mongoose schema lives in `models/` — so the four new models land in `models/` (approval, T11-N7), and the middleware files need a home under `api_v3/routes/partner/` or, on v4, `api_v4/lib/` (question 8). Two lifecycle steps clash with the global chain in `dzzlo_oms.js`: `express.json({ limit: "1mb" })` (`:59`) reads every body before any router, so the router-level 100 kb parser would find the body already consumed and never apply its cap (body-parser behaviour, inferred — not tested here), and the open `cors()` (`:98`) answers every path — both need the partner mount ahead of them or scoped (T11-N2).

## Phases

| Phase | File | Outcome |
| --- | --- | --- |
| 1 | `01-phase-1-partner-identity-credentials.md` | `api_clients` model; credential issuance rules; auth scheme decided (OAuth2 client-credentials) and justified. |
| 2 | `02-phase-2-auth-authorization-middleware.md` | Token endpoint, `partner_auth`, tenant gate, `partner_scope`; dedicated `/api/v3/partner` router mounted in isolation. |
| 3 | `03-phase-3-order-voucher-endpoints.md` | `POST /partner/orders` + `POST /partner/vouchers` reusing existing services; `Idempotency-Key` dedupe; stable error codes. |
| 4 | `04-phase-4-security-measures.md` | **Security deep-dive**: full control catalog, threat-model table, rotation, HMAC + replay protection, lockout, security test plan. |
| 5 | `05-phase-5-usage-logging-attribution.md` | `partner_usage` collection + meter hook; aggregations answering *which API, how many times, by which partner*. |
| 6 | `06-phase-6-cost-metering.md` | Versioned price book, tiers/quotas/overage, monthly roll-up to draft invoices, bypass-proof metering. |
| 7 | `07-phase-7-rollout-docs-versioning.md` | Sandbox→prod onboarding + certification, OpenAPI/quickstart docs, versioning & deprecation policy, feature-flag rollout + rollback, security runbooks. |

Each phase is independently shippable: 1–3 give a working partner surface, 4 hardens it (do **not** onboard a real partner before 4), 5–6 make it billable, 7 productionizes.

## Assumptions & open questions (resolve before large code blocks)

1. **Auth scheme** — plan recommends OAuth2 **client-credentials** (short-lived bearer minted from `client_id`/`client_secret`); static signed API key noted as the simpler fallback. Confirm in Phase 1.
2. **Global `api_key_v1()` gate** — partner traffic won't carry the internal app `x-api-key`. Plan assumes `/api/v3/partner` is explicitly exempted from the app key/JWT gates and protected by its own chain. Verify how `dzzlo_oms.js` ordering allows this.
   - **2026-10-01:** do not rely on the app key checks' current behaviour — give the partner router an explicit exemption and its own gate chain. X-SEC-4 in tasks_01 puts one API-key middleware on every mount, so the exemption has to be written, not assumed. Placement: on v3, ahead of the key check in `api_v/api3.js`; on v4 the hub has no slot before its bearer check (`api_v4/index.js:72-74`) — see T11-N2. The app-version gate applies only to requests that carry the app's device metadata (`helpers/middlewares.js:112-141`).
3. **Payload shape** — partner DTOs mirror the v3 create controllers' validated input minus app-only fields (device/push). Extract the exact required-field list from the existing services during Phase 3.
   - **2026-10-01:** the create paths are already services — orders `createMstTrn({ body, meta })` (`api_v3/services/order_msts.js:755`), vouchers `createCustomerOnAcVoucher` / `createDealerVoucher` / `createCustomerVoucher` (`api_v3/services/voc_msts.js:700,764,848`). Each takes the tenant ids as input, so the partner controller must set them from the credential.
4. **Who creates partners** — internal super-admin script/endpoint in v1 (no self-serve). Phase 7 covers the flow.
5. **Quota semantics** — hard per-minute rate limit + **soft** monthly quota (bill overage) in v1; confirm whether quota exhaustion should ever hard-block (429).
6. **Shared rate-limit store** — if the API runs multi-instance, `express-rate-limit` needs a shared store (Mongo/Redis). Confirm deployment topology.
   - **2026-10-01:** the repo describes two servers with one PM2 process each (`docs/runbook.md:167`; `api_v4/lib/rateLimit.js:23-26`), and the only principal-keyed limiter uses the in-memory store — so a partner quota needs a shared store, and none is a dependency today (T11-N5; the topology question is X-OPS-1 in tasks_01).
7. **IST convention** — usage docs store UTC `Date` + IST-rendered reports; billing month = IST calendar month. Confirm against the repo's existing `logging()` time handling.
   - **2026-10-01 (answered by the code):** two conventions exist. `logging()` stores `timeIST` as a wall-clock-shifted `Date` (`helpers/middlewares.js:255-257`); the ledger computes IST-anchored instants per request (`api_v3/services/ledger_window.js:67` `istDayEnd`, `:77` `istMonthKey`, `:231` `getFiscalYear`; PR #41), and v4 reuses those. Usage roll-ups should follow the ledger's helpers, not `logging()`.
8. **Mount on v4 instead of v3?** _(added 2026-10-01 — a question for the user, not a decision)_ This plan predates `/api/v4` (mounted 2026-09-30, `dzzlo_oms.js:121`). The API's rule now reads "New contracts are written inside `api_v4/`. `api_v3/` changes only as test-first bugfix PRs" (`AI.md:85-86`), and v4 already has the validator, envelope, error catalogue, token-derived tenancy, `assertRelation`, cursor paging, time limits and a limiter that this plan builds from scratch. Against a plain v4 module: the hub is built for app users (app bearer, company gate, user roles) with no pre-auth slot (`api_v4/index.js:12,69-84`), and a partner contract should not version in step with the app's screen API. Options include (a) `/api/v3/partner` as planned, (b) a partner router beside the v4 hub that reuses `api_v4/lib`, (c) a pre-auth slot inside `buildV4`. See T11-N1.

## Constraints

- Match existing conventions: `asyncHandler`, `ErrorResponse`, `advancedResults` where relevant.
- **Reuse** order/voucher business logic — extract to shared services if inline; no forks.
- **Do not** break the mobile-app auth path; partner middleware must never run on app routes.
- Store only hashed secrets; never log secrets; `timingSafeCompare` everywhere.
- Partner surface explicit and independently gated; additive DB changes only (rollback = unmount router).

**Note (2026-10-01):** these are v3's conventions. If the surface mounts on v4 (question 8), v4's own apply: `ApiError` with the frozen catalogue (`api_v4/lib/errors.js:10-50`), no `advancedResults` and no bare `Promise.all` in read models or commands (enforced by `test/api_v4/lib/conventions.test.js`), cursor paging through `api_v4/lib/cursor.js`. "Additive DB changes only" still holds; each new collection is a `models/` file (approval, `AI.md:87`).

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| T11-N1 | 🆕 Decide where the partner surface mounts (question 8) — `/api/v3/partner` as planned, a partner router beside the v4 hub reusing `api_v4/lib`, or a pre-auth slot in `buildV4` — and give the partner contract a version path of its own (Phase 7.4's "`/api/v4/partner`" now names the app's API) | Plan written 2026-07, before v4; `AI.md:85-86` freezes v3 for features; `/api/v4` mounted at `dzzlo_oms.js:121` | API | XS (user decision) | — |
| T11-N2 | 🆕 Mount the partner router ahead of, or scoped out of, the global parser and CORS: `express.json({ limit: "1mb" })` (`dzzlo_oms.js:59`) consumes every body first, so a router-level 100 kb cap never runs; the global CORS middleware (`:98`) applies to every path; the v3 key check (`api_v/api3.js:14`) and the v4 hub's bearer check (`api_v4/index.js:72-74`) sit in front of everything mounted after them | Phase 2.5 isolation rules 1 and 3 and Phase 4.G–H assume a clean path (body-parser skip on a consumed request inferred from the library) | API | S | T11-N1 |
| T11-N3 | 🆕 Tenant helper for a machine principal: `tenantOf` / `scopeFilter` read `req.user` (`api_v4/lib/tenancy.js:64-102`); add a sibling for `req.partner`, and reuse `assertRelation` (`:121-138` — one indexed `exists`, the same 403 for unrelated and unknown) for Phase 3.1's counterparty check | Non-negotiable 1 is what v4 already enforces for app users | API | S | T11-N1 |
| T11-N4 | 🆕 Amend Phases 3.4–3.5: validate with `api_v4/lib/validate.js` (unknown keys rejected at every level, every failure in `details[]`, `:424-446`) instead of choosing a library; decide whether partners get the v4 envelope `{ success, error, error_code }` (`api_v4/lib/errors.js:105-134`) or the nested one planned, and keep partner codes (`INSUFFICIENT_SCOPE`, `REQUEST_IN_FLIGHT`, `IDEMPOTENCY_KEY_REUSED`, …) in one frozen catalogue | Two envelopes mean two handlers; v4 still has no JSON 404/405 and never raises `NOT_FOUND` / `CONFLICT` (X-V4-1 in tasks_02) | API | S | T11-N1 |
| T11-N5 | 🆕 Shared store for partner rate limits and quotas: the only principal-keyed limiter uses `express-rate-limit`'s MemoryStore per process (`api_v4/lib/rateLimit.js:23-26`), production runs two servers, and no Redis or Mongo store is a dependency — answers question 6 | Billing-grade quotas cannot be counted per process | API | M | T11-N1; X-OPS-1 (tasks_01) |
| T11-N6 | 🆕 Add the tasks_01 hardening items to Phase 4's "no external partner before this ships" gate: X-SEC-1 (extend the v4 auth + tenant-scoping pattern to the v3 routes, which predate it), X-SEC-2 (superadmin endpoints require a superadmin bearer; no response carries secret fields), X-SEC-4 (the API-key check rejects key-less requests on every mount), SEC-2 (global rate limit) and SEC-5 (CORS allow-list) — all owned by tasks_01 | A partner surface shares the process, the key checks and the data with the v3 routes | API | XS (plan) | the tasks_01 items named |
| T11-N7 | 🆕 Put the four new schemas (`api_clients`, `idempotency_keys`, `partner_usage`, `partner_pricing`) in `models/` and get that approval — `api_v3/models/` does not exist and `AI.md:87` keeps `models/` unchanged without it (precedent `models/user_prefs.js`, `d2639ee`) | The Architecture section places them in `api_v3/models/` | API | XS (approval) | T11-N1 |
| T11-N8 | 🆕 Define "tenant active" for a machine client: `check_user_company_status` reads the user's membership status (`helpers/middlewares.js:85-106`), and companies carry no status of their own (`models/dealer_msts.js:19` `dealer_verified`; `models/cust_msts.js:60-61` `cust_verified`, `cust_blacklist`) — Phase 2.3's "reuse the same flags" has nothing to reuse | A partner has no membership | API | S | T11-N1 |

Owned elsewhere and referenced above: X-SEC-1, X-SEC-2, X-SEC-4, X-OPS-1 (tasks_01); X-V4-1, X-V4-2 (tasks_02). X-V4-2 bears on non-negotiable 5: v4 read models now hold business rules of their own, while this plan sends partner writes through the v3 services (Phase 3.2) — keep it that way unless X-V4-2 decides otherwise.
