# Plan: Partner (B2B) Open API on `api_v3` — Vertical-SaaS Platform Expansion

> **Source prompt:** `../../prompt-open-api-v3-partner-tutorial.md` (paste that into Claude Code inside `dzzlo_oms_api` when implementing). This folder is the phase-wise **design plan** that prompt asks for — design doc first, code second — following the workspace convention of `tasks_09_sadmin_settings` / `tasks_10_analytics_events`.
>
> **Repo under change:** `dzzlo_oms_api` (Node.js + Express 5, Mongoose 9, MongoDB). Versioned APIs live under `api_v3/`, mounted at `/api/v3` by `api_v/api3.js`. This plan lives in the notes vault; snippets are written in that repo's idiom (`asyncHandler`, `ErrorResponse`, `timingSafeCompare`) and must be validated against the real files when implementing.

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
3. **Payload shape** — partner DTOs mirror the v3 create controllers' validated input minus app-only fields (device/push). Extract the exact required-field list from the existing services during Phase 3.
4. **Who creates partners** — internal super-admin script/endpoint in v1 (no self-serve). Phase 7 covers the flow.
5. **Quota semantics** — hard per-minute rate limit + **soft** monthly quota (bill overage) in v1; confirm whether quota exhaustion should ever hard-block (429).
6. **Shared rate-limit store** — if the API runs multi-instance, `express-rate-limit` needs a shared store (Mongo/Redis). Confirm deployment topology.
7. **IST convention** — usage docs store UTC `Date` + IST-rendered reports; billing month = IST calendar month. Confirm against the repo's existing `logging()` time handling.

## Constraints

- Match existing conventions: `asyncHandler`, `ErrorResponse`, `advancedResults` where relevant.
- **Reuse** order/voucher business logic — extract to shared services if inline; no forks.
- **Do not** break the mobile-app auth path; partner middleware must never run on app routes.
- Store only hashed secrets; never log secrets; `timingSafeCompare` everywhere.
- Partner surface explicit and independently gated; additive DB changes only (rollback = unmount router).
