# Phase 7 — Rollout, Partner Docs & Versioning

**Outcome:** the partner API becomes a product: sandbox→production onboarding with a certification gate, partner-facing docs (OpenAPI + quickstart), an explicit versioning/deprecation policy, a feature-flagged rollout with a one-switch rollback, and the security runbooks Phase 4 promised.

> **Vertical-SaaS lens:** in a vertical, the partner ecosystem is the moat — every ISV certified against our API makes DZZLO harder to displace as the system of record. That only compounds if onboarding is smooth for small industry ISVs and our versioning promises are conservative enough that integrations built once keep working for years. Docs and deprecation policy are product surface, not afterthoughts.

---

## 7.1 Environments & credentials

| | Sandbox | Production |
| --- | --- | --- |
| `client_id` prefix | `dzl_test_…` | `dzl_live_…` |
| Bound tenant | dedicated seeded test company (realistic products, rates, relations, credit limits) | partner's real tenant `co_id` |
| Billing | never billable | metered from first call |
| Issued when | onboarding start | after certification (7.2) |
| Rate ceiling | low (30/min) | per tier |

Same codebase, same URL, `env` on the credential (Phase 1) — a test key physically cannot write production data because it is bound to the test tenant. Sandbox tenant gets a periodic reset job so partner test data doesn't rot.

## 7.2 Partner onboarding flow

1. **Agreement** — commercial terms incl. tier, plus security expectations (secret storage, no client-side use, breach notification).
2. **Create sandbox credential** — internal super-admin script (Phase 1); scopes limited to what the partner bought; secret delivered via a secure channel (never email/chat plaintext), shown once.
3. **Partner integrates against sandbox** — docs (7.3) are self-serve; support channel established.
4. **Certification gate** (we verify from sandbox `partner_usage` + a short live session):
   - [ ] Token flow correct: caches tokens, refreshes before expiry, no per-request `/oauth/token` hammering.
   - [ ] Sends `Idempotency-Key` on every write; **retries reuse the same key** (we check replay counts > 0 in their test traffic — proof their retry path actually works).
   - [ ] Handles `RATE_LIMITED` with backoff honoring `Retry-After`.
   - [ ] Handles domain errors (`CREDIT_LIMIT_EXCEEDED`, `VALIDATION_FAILED`) without blind retry.
   - [ ] Secret handling attested: server-side only, env/secret-manager storage, rotation contact named.
   - [ ] Optional: static egress IPs supplied → allow-list enabled (Phase 4 D).
5. **Issue production credential** — new `dzl_live_` client bound to the real tenant, tier set, quota set; sandbox credential stays alive for their ongoing testing.
6. **Go-live watch** — first 48 h on elevated monitoring (7.5); tenant confirms first real order/voucher attribution looks right.

## 7.3 Partner-facing docs

Kept in the repo (`docs/partner-api/`), published however VSYST docs ship:

1. **OpenAPI 3.1 spec** — source of truth; partners generate clients from it:

```yaml
openapi: 3.1.0
info: { title: DZZLO OMS Partner API, version: 1.0.0 }
servers: [{ url: https://<host>/api/v3/partner }]
security: [{ bearerAuth: [] }]
paths:
  /oauth/token: { post: { … } }          # client_credentials
  /orders:
    post:
      parameters: [{ name: Idempotency-Key, in: header, required: true, … }]
      responses: { '201': …, '400': …, '401': …, '403': …, '409': …, '422': …, '429': … }
  /vouchers: { post: { … } }
  /credentials/rotate: { post: { … } }
components:
  securitySchemes: { bearerAuth: { type: http, scheme: bearer } }
  schemas: { Order, Voucher, Error }      # Error = the Phase 3 envelope, verbatim
```

2. **Quickstart README** — the 15-minute path: mint token (curl), place a sandbox order (curl with `Idempotency-Key`), read the replay behavior by re-running the same command.
3. **Error-code reference** — the Phase 3 table, verbatim; plus rate-limit headers and idempotency semantics (409 vs 422 vs replay).
4. **Security page** — token TTL, rotation endpoint, HMAC option, IP allow-list, our expectations of them (the certification list).
5. **Changelog** — dated, append-only; every additive change announced.

## 7.4 Versioning & deprecation policy

- The partner surface rides `/api/v3/partner` and is treated as **its own compatibility contract**, stricter than the app's v3:
  - **Additive-only within the version**: new optional fields, new endpoints, new error codes (partners are told to tolerate unknown codes/fields from day one — it's in the certification list).
  - **Breaking changes** (field removal/rename, semantics, auth changes) → new surface (`/api/v4/partner` or `/partner/v2`), never in-place.
- **Deprecation:** announced in changelog + direct partner contact ≥ **90 days** ahead; responses gain `Deprecation` + `Sunset` headers; Phase 5 usage data tells us exactly who still calls the old thing — nothing is removed while a certified partner shows traffic without a conversation first.
- App-side freedom preserved: app v3 routes can keep evolving as today; only `/partner/*` carries the stricter promise. (This is why the surface was isolated in Phase 2.)

## 7.5 Observability & alerts (wiring Phase 4/5 outputs)

Dashboard (from `partner_usage`): calls + error-rate + p95 latency per client per endpoint; 429/quota consumption per client; auth-failure trend; new-client first-call events. Alerts: error-rate >5% per client (15 min), auth-failure spike, sustained 429s, reconciliation drift (Phase 6), any call pattern from a prod client with zero prior sandbox traffic.

## 7.6 Rollout & rollback

| Stage | Gate |
| --- | --- |
| 1. Dark deploy — code live, `PARTNER_API_ENABLED=false` | all routes 404; app regression suite green |
| 2. Internal smoke — flag on in staging/prod, internal test client | Phase 4 security suite green **in prod config**; test orders visible with correct attribution; usage docs flowing |
| 3. Pilot — one friendly partner, sandbox → certification → prod | 2 weeks clean: no cross-surface incidents, billing reconciliation clean |
| 4. GA — onboard per 7.2 | quarterly credential audit scheduled (Phase 4.4) |

**Rollback is one switch:** `PARTNER_API_ENABLED=false` unmounts the router — the app path is untouched by design (Phase 2 isolation), and all DB changes are additive collections/optional fields, so no schema rollback exists. Partial rollback: suspend individual clients (`status: 'suspended'`, effective ≤60 s) without touching the surface.

## 7.7 Security runbooks (owed from Phase 4.4)

1. **Partner secret compromised** — suspend client (≤60 s) → investigate usage window via `partner_usage` (`client_id`, IPs, request_ids) → issue new secret via rotation path → tenant notified with affected order/voucher list (attribution fields) → post-mortem in changelog if partner-visible.
2. **`PARTNER_JWT_SECRET` compromised** — rotate env secret + restart → every outstanding token invalid ≤15 min (TTL) with no DB work → partners re-mint automatically (certified token flow handles 401→re-auth) → audit window in usage log.
3. **Surface-level incident** — `PARTNER_API_ENABLED=false` (kill), app unaffected → communicate via status/partner contacts → staged re-enable per 7.6.

## Phase 7 checklist

- [ ] Sandbox tenant seeded + reset job; `dzl_test_`/`dzl_live_` issuance paths.
- [ ] Onboarding flow + certification checklist written into the partner docs.
- [ ] OpenAPI 3.1 spec matches implementation (CI check: spec routes ⊆ router routes).
- [ ] Quickstart, error reference, security page, changelog published.
- [ ] Versioning/deprecation policy published (90-day, Sunset headers, additive-only).
- [ ] Dashboards + alerts live before pilot.
- [ ] Rollout stages executed in order; rollback switch tested in staging (flag off → 404s, app unaffected).
- [ ] Three runbooks reviewed with ops.
