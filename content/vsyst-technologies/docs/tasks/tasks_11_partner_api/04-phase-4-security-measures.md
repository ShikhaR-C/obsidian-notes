# Phase 4 — Security Measures (Deep-Dive)

**Outcome:** the complete, explicit control catalog for the partner surface — each control named with *where it is enforced* — plus a threat-model table and a security test plan that goes into CI. **Gate rule: no external partner is onboarded before this phase ships.**

> **Vertical-SaaS lens:** tenants trust DZZLO as their system of record for commercially sensitive data — orders, credit limits, payment flows between real dealers and customers. On a multi-tenant partner API, one weak control is not "a bug," it is a potential **cross-tenant incident** affecting every company on the platform, and in an industry vertical, reputational damage travels fast between the exact customers we sell to. Security here is a product feature we will put in the partner docs, not an internal afterthought.

---

## 4.1 Control catalog (control → where enforced)

### A. Transport

| Control | Enforcement point |
| --- | --- |
| TLS-only, TLS ≥ 1.2 | LB/reverse proxy (ALB/nginx) — port 80 redirects, no plaintext listener on the app |
| HSTS (`max-age` ≥ 1y, includeSubDomains) | `helmet.hsts()` — already global via `dzzlo_oms.js`; verify config values |
| No secrets in URLs | design rule: credentials/tokens travel only in headers/body — query strings land in proxy logs |

### B. Secret handling & rotation

| Control | Enforcement point |
| --- | --- |
| Hashes only at rest (`sha256`, show-once issuance) | `api_clients.secrets[].hash` (Phase 1) |
| Constant-time comparison | `timingSafeCompare` in token endpoint (Phase 2) — never `===` on secrets |
| **Rotation with overlap** | `POST /partner/credentials/rotate` (below) |
| Redaction in all logging | `logging()` + `partner_usage` writer strip `authorization`, `client_secret`, `x-dzzlo-signature` |
| Separate signing domains | `PARTNER_JWT_SECRET` ≠ app JWT secret; `aud`/`iss` pinned (Phase 1/2) |
| Secrets in env/secret manager, never in repo | deployment config; `.env.example` documents names only |

Rotation endpoint (scope-independent, authenticated client only):

```js
// POST /api/v3/partner/credentials/rotate  → new secret returned ONCE
// current 'active' secret → state:'retiring', expires_at = now + 72h (overlap window)
// new secret pushed as 'active'; max 2 valid at any moment (Phase 1 schema)
// → partner deploys the new secret within 72h with zero downtime; old one dies on schedule
```

Also: an **internal revoke** path (super-admin sets `status:'revoked'`) for compromise response — takes effect within the Phase-2 cache TTL (≤60 s).

### C. Rate limiting & quotas (per-client, not per-IP)

Two layers, both keyed by `client_id` (post-auth) — IP-keying is useless for B2B (one partner = one NAT) and dangerous (shared egress = collateral damage):

```js
// api_v3/middleware/partner_rate_limit.js — extend express-rate-limit (already a repo dep)
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: (req) => req.partner.client.rate_per_min,        // per-client tier ceiling (Phase 1)
  keyGenerator: (req) => req.partner.client_id,          // NOT req.ip
  standardHeaders: true,                                 // RateLimit-* response headers
  handler: (req, res) => res.status(429).json({ success: false,
    error: { code: 'RATE_LIMITED', message: 'Rate limit exceeded.', request_id: req.request_id } }),
});
```

- **Burst limit** (above): hard 429, `Retry-After` header.
- **Monthly quota**: cheap `$inc` counter per `client_id` per IST-month (Phase 6 collection). v1 semantics: **soft** — over-quota calls succeed and bill as overage; hard-block is a per-client flag for free-tier/sandbox.
- **Multi-instance caveat:** the default in-memory store limits per process. If the API runs >1 instance, use a shared store (`rate-limit-mongo` or Redis) — open question #6 in the overview; do not ship multi-instance with in-memory limits and believe the ceiling.
- Token endpoint keeps its own stricter pre-auth limiter (Phase 2), keyed IP+client_id.

### D. IP allow-list (optional, per client)

- `api_clients.allowed_ips[]` (Phase 1), enforced inside `partner_auth` (Phase 2).
- **Proxy trust:** derive caller IP via Express `trust proxy` configured to the actual LB hop count — never read `x-forwarded-for` naively (trivially spoofable if misconfigured). Verify the repo's existing `trust proxy` setting.
- Recommended-not-required for partners with static egress; recorded in onboarding (Phase 7).

### E. Request signing (HMAC) + replay protection — opt-in hardening

For partners handling high-value flows, an additional per-request signature (this is scheme C from Phase 1, layered on top of the bearer token):

```
headers:  X-DZZLO-Timestamp: <unix seconds>
          X-DZZLO-Nonce:     <uuid>
          X-DZZLO-Signature: hex(hmac_sha256(hmac_secret,
                               `${timestamp}\n${nonce}\n${method}\n${path}\n${sha256(body)}`))
checks:   |now - timestamp| ≤ 300s                    → else 401 SIGNATURE_EXPIRED
          nonce unseen for this client_id             → else 401 REPLAY_DETECTED
          timingSafeCompare(sig, expected)            → else 401 BAD_SIGNATURE
storage:  nonce cache: { client_id, nonce } with 10-min TTL index (own collection or in-proc + TTL)
```

Enforced by an optional middleware slotted after `partner_auth`, active when the client has `hmac_secret_hash` set. Body-hash binding means a captured request can't be replayed *or* mutated.

### F. Authorization recap (enforced in Phases 2–3, listed for completeness)

- Scope per route (`partner_scope`) — least privilege.
- Tenant forced from credential; `co_id` in payload rejected.
- Tenant-status gate — suspended company blocks its partners.
- Idempotency records scoped `(client_id, endpoint, key)` — no cross-client replay/probing.

### G. Payload & parser hygiene

- `express.json({ limit: '100kb' })` on the partner router (Phase 2) — orders/vouchers are small; a 5 MB body is an attack, not a use case.
- `sanitizeMongo` global (already in `dzzlo_oms.js`) + allow-list validation (Phase 3) → NoSQL-operator injection dies twice.
- Reject non-JSON content types on write endpoints (415).

### H. CORS posture

Server-to-server surface: **no CORS allowances at all** for `/partner/*` — no partner origins added to the app's CORS config, no preflight support. A browser calling the partner API is by definition a leaked credential (secrets don't belong in front-ends); absence of CORS keeps browser-based misuse loudly broken.

### I. Abuse handling — lockout & auto-disable

On the token endpoint (extends `registerAuthFailure` from Phase 2):

| Failed attempts (rolling) | Action |
| --- | --- |
| 5 in 15 min | `lock_until = now + 15 min` (401, uniform body) |
| 3 lockouts in 24 h | `status: 'suspended'` (auto-disable) + ops alert + partner-contact email |

Counters are atomic `$inc`/`$set` on `api_clients` — no read-modify-write races. Data-endpoint anomalies (sustained 429s, error-rate spikes, geo-novel IPs) alert ops via Phase 5 usage data rather than auto-blocking (billing data ≠ trigger-happy availability decisions).

## 4.2 Threat model

| # | Threat | Attack looks like | Controls (where) |
| --- | --- | --- | --- |
| T1 | Stolen `client_secret` | leaked env file / repo commit on partner side | show-once + hash-at-rest (B); short-lived tokens limit window (Phase 1); rotation w/ overlap (B); revoke ≤60 s (B); IP allow-list (D); lockout on guessing (I) |
| T2 | Stolen access token | intercepted / logged bearer | TLS+HSTS (A); 15-min TTL (Phase 1); `aud` pinning — useless on app routes (Phase 2); optional HMAC binds requests to a second secret (E) |
| T3 | **Cross-tenant write** | payload carries another company's `co_id` | tenant from credential only; unknown-field rejection; forcing test in CI (Phase 3) |
| T4 | Scope escalation | orders key posting vouchers | `partner_scope` per route (Phase 2); scopes snapshot in signed token |
| T5 | Replay of captured request | resend same signed call | idempotency dedupe (Phase 3); HMAC timestamp ± 300 s + nonce cache (E) |
| T6 | Brute-force credentials | hammering `/oauth/token` | strict pre-auth limiter (Phase 2); uniform errors; lockout → auto-suspend (I) |
| T7 | NoSQL injection | `{"qty": {"$gt": 0}}` | `sanitizeMongo` (G); allow-list typed validation (Phase 3) |
| T8 | Flood / DoS | high-rate calls, huge bodies | per-client burst limit (C); 100 kb body cap (G); quotas (C); LB-level protections |
| T9 | Token forgery / cross-surface | app JWT on partner route or vice-versa | separate signing secrets + `aud`/`iss` (Phase 1/2); cross-surface tests in CI (Phase 2) |
| T10 | Secrets in logs | secret/token in `logs` or console | redaction list (B); CI grep guard (Phase 1); `partner_usage` stores key names never values (Phase 5) |
| T11 | Partner misbehavior (over-calling, scraping-by-write) | quota abuse, junk orders | metering + anomaly alerts (Phase 5); quotas (C); suspend switch (B); idempotency stops accidental storms (Phase 3) |
| T12 | Replay via idempotency probing | guessing another client's keys to read stored responses | keys scoped to `client_id` (Phase 3) — other clients' keys are invisible by index design |
| T13 | Insider mis-issuance | over-scoped credential created internally | issuance requires super-admin + `created_by` audit (Phase 1); scopes enumerated, no wildcard |

## 4.3 Security test plan (lands in CI)

- [ ] Cross-tenant forcing: 20+ payload variants (`co_id`, `company`, nested) → all 400, doc `co_id` always credential's.
- [ ] Cross-surface tokens: app JWT ↔ partner routes both directions → 401.
- [ ] Replay: same HMAC-signed request twice → second 401 `REPLAY_DETECTED`; stale timestamp → `SIGNATURE_EXPIRED`.
- [ ] Rate limit: burst to 429, `RateLimit-*` + `Retry-After` present; second client unaffected (key isolation).
- [ ] Lockout: 5 bad secrets → locked; correct secret during lock → still 401; auto-suspend after 3 lockouts.
- [ ] Rotation: old secret valid through overlap, dead after `expires_at`; revoke effective ≤ cache TTL.
- [ ] Injection: `$`-operator payloads on every field → 400, nothing persisted.
- [ ] Oversize body (>100 kb) → 413; wrong content-type → 415.
- [ ] Log hygiene: run full suite, then grep test-run logs/DB for any issued secret/token → zero hits (automated assertion).
- [ ] Error opacity: forced 500 returns only `INTERNAL_ERROR` + `request_id`; stack retrievable internally by that id.

## 4.4 Operational security

- Alerts (wired via Phase 5 data + existing ops tooling): auth-failure spikes per client, 429 sustained >5 min, error-rate >5%, calls from unlisted IPs when allow-list set, first call from a new client in production.
- Runbooks (written in Phase 7): compromised partner secret, compromised `PARTNER_JWT_SECRET` (rotate signing key → all tokens die in ≤15 min), emergency surface kill via `PARTNER_API_ENABLED=false`.
- Review cadence: quarterly credential audit — unused clients (`last_used_at` > 90 d) flagged for revocation.

## Phase 4 checklist

- [ ] HSTS/TLS posture verified at LB + helmet config.
- [ ] Rotation endpoint (72 h overlap) + internal revoke path; redaction list applied to all log writers.
- [ ] `partner_rate_limit` per-client burst limiter + headers; shared store decision resolved for multi-instance.
- [ ] IP allow-list enforcement + correct `trust proxy` verified.
- [ ] Optional HMAC + nonce/timestamp replay protection behind per-client flag.
- [ ] Body cap, content-type gate; CORS untouched for `/partner/*`.
- [ ] Lockout/auto-suspend with atomic counters + ops alert.
- [ ] Threat-model table reviewed with team; every row has a CI test or an explicit accepted-risk note.
- [ ] Security test plan (4.3) automated and green.
