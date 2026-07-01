# Phase 1 — Partner Identity & Credentials

**Outcome:** a first-class machine identity (`api_clients`) separate from `users`, credential issuance/storage rules, and a decided + justified auth scheme. No routes ship yet — this phase is pure model + design, safe to merge independently.

> **Vertical-SaaS lens:** in a multi-tenant system of record, the credential *is* the tenant boundary. Everything downstream (isolation, metering, billing, audit) hangs off this one document, so it carries the tenant binding, the scopes, the pricing tier, and the abuse counters — one place to suspend a partner and everything stops.

---

## 1.1 Why a separate `api_clients` model (not `users`)

| Dimension | Human user (`users`) | Partner machine identity |
| --- | --- | --- |
| Authenticates with | password/OTP → mobile JWT | `client_id` + secret → short-lived token |
| Lifecycle | signup, password reset, roles | issue → rotate → revoke; no "reset flow" |
| Blast radius | one person's session | every order the partner's system places |
| Needs | profile, companies[], push tokens | scopes, IP pin, rate tier, quota, env |
| Billing | seat-based | usage-based per call |

Overloading `users` with machine identities would leak app assumptions (OTP, `check_user_version()`, `userCache` shape) into the partner path and widen the app's attack surface. A dedicated collection keeps the trust domains physically separate — non-negotiable #4 in the overview.

## 1.2 `api_clients` model

`api_v3/models/api_clients.js` (Mongoose 9, matching repo model style):

```js
const SECRET_STATE = ['active', 'retiring']; // rotation overlap (Phase 4)
const PARTNER_SCOPES = ['orders:write', 'vouchers:write']; // aligned with SCOPE_ENUM vocabulary

const apiClientSchema = new mongoose.Schema(
  {
    // Identity — public id is prefixed + env-marked, e.g. dzl_live_9f2c…, dzl_test_…
    client_id: { type: String, required: true, unique: true, index: true },
    name: { type: String, required: true, trim: true },          // "Acme ERP — Sharma Fuels"
    partner_org: { type: String, required: true, trim: true },   // legal/company name of the integrator
    contact_email: { type: String, required: true },

    // Tenant binding — exactly ONE tenant in v1 (aggregators = v2)
    co_id: { type: mongoose.Schema.ObjectId, ref: 'companies', required: true, index: true },

    // Secrets — hashes only, max 2 concurrently valid (rotation overlap)
    secrets: [{
      hash: { type: String, required: true },      // sha256(secret) — see 1.3
      last4: { type: String, required: true },     // display-only fingerprint
      state: { type: String, enum: SECRET_STATE, default: 'active' },
      created_at: { type: Date, default: Date.now },
      expires_at: { type: Date },                  // set when retiring
    }],

    // Authorization
    scopes: [{ type: String, enum: PARTNER_SCOPES, required: true }],
    allowed_ips: [{ type: String }],               // optional CIDR/IP allow-list (Phase 4)

    // Environment & lifecycle
    env: { type: String, enum: ['sandbox', 'production'], required: true },
    status: { type: String, enum: ['active', 'suspended', 'revoked'], default: 'active', index: true },

    // Commercial (Phase 6)
    tier: { type: String, enum: ['sandbox', 'starter', 'growth', 'scale'], default: 'sandbox' },
    rate_per_min: { type: Number, default: 60 },   // burst ceiling (Phase 4)
    monthly_quota: { type: Number, default: 1000 },// included calls (Phase 6)

    // Abuse containment (Phase 4)
    failed_auth_count: { type: Number, default: 0 },
    lock_until: { type: Date },

    // Optional request-signing secret (Phase 4 HMAC) — hash only
    hmac_secret_hash: { type: String },

    created_by: { type: mongoose.Schema.ObjectId, ref: 'users' }, // the internal admin
    last_used_at: { type: Date },
    rotated_at: { type: Date },
  },
  { timestamps: true }
);

apiClientSchema.index({ co_id: 1, status: 1 });
module.exports = mongoose.model('api_clients', apiClientSchema);
```

Design notes:

- **`secrets` is an array (max 2)** so rotation can overlap: new secret issued, old one `retiring` with `expires_at`, then dropped. No partner downtime during rotation (Phase 4 owns the endpoint).
- **`env` on the credential**, not the URL: sandbox and production are different documents with different `co_id`s (sandbox binds to a seeded test tenant). A test key physically cannot write production data.
- **Tier/quota live here** so one read gives auth + limits + billing context; the per-process cache (Phase 2) keeps it hot.

## 1.3 Credential issuance & storage rules

1. **Generate:** `client_id = dzl_<env>_<24 hex>` (from `crypto.randomBytes`), `client_secret = dzs_<48 hex>` (256-bit entropy).
2. **Show once:** the plaintext secret appears only in the issuance response/script output. We store `sha256(secret)` + `last4`. This mirrors the repo's existing `api_key_v3()` hex-key pattern.
   - SHA-256 (not bcrypt) is deliberate: the secret is machine-generated with 256-bit entropy, so brute-force via fast hashing is not a threat the way low-entropy human passwords are; comparison stays `timingSafeCompare(sha256(presented), stored_hash)` — constant-time, same helper the repo already uses.
3. **Never logged:** the `logging()` middleware and any partner logging must redact `Authorization`, `client_secret`, and signature headers (enforced in Phase 4/5).
4. **Issuance path (v1):** an internal super-admin script (`scripts/create_api_client.js`) or a super-admin-only endpoint. No self-serve. Phase 7 defines the human workflow around it.

## 1.4 Auth scheme decision

| Scheme | How | Pros | Cons |
| --- | --- | --- | --- |
| **A. Static API key per call** | `client_id` + secret headers on every request | trivial partner DX; matches existing `api_key_v3` idiom | long-lived bearer secret on every wire call; revocation = hard cut; no expiry |
| **B. OAuth2 client-credentials** ✅ | `POST /partner/oauth/token` with id+secret → short-lived (15 min) signed access token; Bearer on data calls | secret only travels to one endpoint; tokens self-expire (stolen token ≤15 min); scopes/tenant snapshot in token; industry-standard M2M — partners' HTTP clients already speak it | one extra call + caching for partners |
| **C. Full HMAC request signing** | per-request signature over method+path+body+timestamp | strongest: replay-proof, secret never travels | hardest DX for small industry ISVs |

**Recommendation: B as the baseline, C as an opt-in hardening layer (Phase 4) for high-assurance partners.** Rationale for a vertical SaaS: partner integrators are often small industry ISVs — client-credentials is the best security-to-DX ratio, and the short TTL gives us revocation semantics a static key can't.

Token shape (signed with a **dedicated** `PARTNER_JWT_SECRET`, never the app's JWT secret):

```js
{
  iss: 'dzzlo-oms',           // issuer
  aud: 'partner-api',         // audience — app `protect` never accepts this
  sub: client_id,
  co_id, env, scopes,         // snapshot for fast authz
  exp: now + 900               // 15 minutes
}
```

**Coexistence with the current chain** (`x-api-key` + `getUserFromToken`):

- App tokens carry no `aud: 'partner-api'` → rejected by `partner_auth`. Partner tokens fail `getUserFromToken` (different secret + audience) → rejected on app routes. The two surfaces cannot cross even if a token leaks between them.
- Partner traffic does not carry the internal app `x-api-key`; `/api/v3/partner` is exempted from `api_key_v1()`/`api_key_v3()` and fully gated by its own chain (wiring in Phase 2 — verify `dzzlo_oms.js` mount order allows the exemption).

## 1.5 Testing

- Model unit tests: enum/required validation, unique `client_id`, max-2 secrets guard, defaults.
- Issuance script test: response contains plaintext secret exactly once; DB holds only `hash`+`last4`; hash verifies via `timingSafeCompare`.
- Static check: grep CI guard that no `console.log`/logger call in partner code references `client_secret`.

## Phase 1 checklist

- [ ] `api_v3/models/api_clients.js` created (schema above, indexes included).
- [ ] `scripts/create_api_client.js` issuance script (show-once secret, sha256 storage).
- [ ] `PARTNER_JWT_SECRET` added to env/config (distinct from app JWT secret) — documented in `.env.example`.
- [ ] Auth scheme decision (B + optional C) recorded and confirmed with team.
- [ ] Unit tests above green; no plaintext secret persisted anywhere.
