# Prompt — Phase-wise tutorial to open `api_v3` as a partner (B2B) API

> Paste everything below the line into Claude Code, running inside the
> `dzzlo_oms_api` repo. It asks for a design + implementation tutorial, not a
> one-shot code dump.

---

You are working inside the **DZZLO OMS API** repo (`dzzlo_oms_api`): Node.js +
Express 5, Mongoose 9, MongoDB. Versioned APIs live under `api_v3/` and are
mounted at `/api/v3` by `api_v/api3.js`.

## Goal

We want to **open `api_v3` to external partners** — companies that own their own
software and want to integrate with DZZLO OMS over HTTP. In this first release
partners must be able to:

1. **Place an order** (`order_msts`)
2. **Create a voucher** (`voc_msts`)

These are machine-to-machine calls from a partner's backend — **not** a human
using the mobile app. Treat this as a distinct, sandboxed surface, not just
"expose the existing routes."

## What already exists (read these before proposing anything)

- `dzzlo_oms.js` — global middleware chain: `api_key_v1()`, `logging()`,
  `check_user_version()`, `helmet`, `sanitizeMongo`, `cors`, `compression`.
- `api_v/api3.js` — how v3 routes are aggregated and where `api_key_v3()`,
  `check_user_company_status()` are applied.
- `api_v3/auth.js` — `getUserFromToken`, `protect`, `authorize(...roles)`,
  `scope(...scopes)`, and the per-process `userCache`.
- `helpers/middlewares.js` — `api_key_v3()` (hex key + `timingSafeCompare`),
  `logging()` (writes to the `logs` collection), company-status gate.
- `models/logs.js` — current request-log schema.
- `models/users.js` — `SCOPE_ENUM`, `companies[]`, `co_id`, `role`.
- `api_v3/controllers/open_apis/` + `api_v3/routes/open_apis/` — existing
  pattern for public/unauthenticated endpoints.
- `models/order_msts.js`, `models/voc_msts.js` — the target write models, plus
  their existing v3 controllers/services so partner writes reuse the SAME
  validation and business rules the app uses (do not fork the logic).

## Deliverable

Produce a **step-by-step, phase-wise tutorial** (design doc first, code second).
For each phase give: the objective, the exact files to add/change, code
snippets that match this repo's existing style, and how to test it. Number the
phases. Cover at minimum:

### Phase 1 — Partner identity & credentials

- Design a partner/app-credential model separate from `users` (e.g.
  `api_clients`): `client_id`, hashed `client_secret`, owning `co_id`, allowed
  scopes, allowed IPs, status, rate/quota tier, created/rotated timestamps.
- Decide the auth scheme for partners: signed API key / client-credentials
  (OAuth2 style short-lived token) rather than reusing the mobile JWT. Justify
  the choice and note how it coexists with the current `x-api-key` +
  `getUserFromToken` chain.

### Phase 2 — Auth & authorization middleware

- A `partner_auth` middleware: verify credential, resolve the owning company,
  attach `req.partner`, and enforce **least-privilege scopes** so a key that can
  place orders can't touch anything else. Reuse the `scope()` /
  `check_user_company_status()` patterns where sensible.
- Mount a dedicated partner router (e.g. `/api/v3/partner/...`) so the surface
  is explicit and independently gated.

### Phase 3 — The two endpoints

- `POST /partner/orders` → reuse the `order_msts` create path.
- `POST /partner/vouchers` → reuse the `voc_msts` create path.
- **Idempotency:** require an `Idempotency-Key` header on both so a partner
  retry never double-places an order/voucher. Show how you store & dedupe keys.
- Strict input validation + `sanitizeMongo`; map internal errors to stable,
  partner-safe error codes (don't leak stack/DB details).

### Phase 4 — Security measures (call these out explicitly)

Enumerate the concrete controls and where each is enforced:

- Transport: TLS-only, HSTS.
- Secret handling: store only hashed secrets, `timingSafeCompare`, rotation
  endpoint, never log secrets.
- Per-partner **rate limiting & quotas** (extend `express-rate-limit`, keyed by
  `client_id` not IP), plus optional IP allow-list.
- Request signing / HMAC option and replay protection (timestamp + nonce).
- Scope enforcement, company-status gate, payload size limits, CORS posture for
  server-to-server.
- Abuse handling: lockout / auto-disable on repeated auth failures.
  Give a short threat-model table (threat → control).

### Phase 5 — Usage logging & attribution ("who called what")

- Extend the existing `logging()` + `logs` model (or add a `partner_usage`
  collection) to record, per call: `client_id`, owning `co_id`, endpoint,
  method, status, response_time, request/response byte size, billable unit,
  `Idempotency-Key`, timestamp (IST). Must answer: **which API, how many times,
  by which partner.**
- Show an aggregation query for per-partner, per-endpoint call counts over a
  date range (for billing + a future dashboard).

### Phase 6 — Cost calculation & metering

- Define a pricing model: per-call cost by endpoint (an order write vs a voucher
  write may cost differently), tiers/included quota, overage rate.
- Show how the usage log rolls up into a monthly cost per partner, and where the
  metering hook lives so it can't be bypassed. Note free/sandbox vs paid.

### Phase 7 — Rollout, docs & versioning

- Sandbox vs production keys, a partner onboarding flow, OpenAPI/README for
  partners, versioning/deprecation policy, and a rollback plan.

## Constraints

- Match existing conventions (`asyncHandler`, `ErrorResponse`, `advancedResults`
  where relevant). Reuse existing order/voucher business logic — no forks.
- Don't break the current mobile-app auth path.
- Point out any assumptions and open questions before writing large code blocks.

Start by reading the files listed above, then present the phased plan for my
review **before** implementing.
