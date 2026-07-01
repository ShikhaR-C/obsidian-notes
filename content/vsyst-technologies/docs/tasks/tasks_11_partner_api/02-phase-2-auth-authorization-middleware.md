# Phase 2 — Auth & Authorization Middleware + Dedicated Router

**Outcome:** the token endpoint, `partner_auth`, tenant-status gate, and `partner_scope` exist, and a dedicated `/api/v3/partner` router is mounted in isolation from the app chain. After this phase a partner can authenticate and hit a stub endpoint — but only with the right scope, an active credential, and an active tenant.

> **Vertical-SaaS lens:** the router *is* the product boundary. Everything partner-facing lives behind one mount point with one explicit middleware chain — so the security review, the metering, and the docs all describe a single, auditable surface.

---

## 2.1 Token endpoint — `POST /api/v3/partner/oauth/token`

`api_v3/controllers/partner/token.js`:

```js
// grant_type=client_credentials; body: { client_id, client_secret }
exports.token = asyncHandler(async (req, res, next) => {
  const { client_id, client_secret } = req.body || {};
  if (!client_id || !client_secret)
    return next(new ErrorResponse('invalid_request', 400));

  const client = await ApiClients.findOne({ client_id }).select('+secrets.hash');

  // Uniform failure: same code/latency whether the id or the secret is wrong.
  const fail = () => next(new ErrorResponse('invalid_client', 401));
  if (!client || client.status !== 'active') return fail();
  if (client.lock_until && client.lock_until > new Date()) return fail(); // lockout (Phase 4)

  const presented = sha256(client_secret);
  const match = client.secrets.some(
    s => (!s.expires_at || s.expires_at > new Date()) && timingSafeCompare(presented, s.hash)
  );
  if (!match) {
    await registerAuthFailure(client); // $inc counter, maybe lock (Phase 4)
    return fail();
  }

  await ApiClients.updateOne({ _id: client._id }, { failed_auth_count: 0, last_used_at: new Date() });

  const access_token = jwt.sign(
    { sub: client.client_id, co_id: client.co_id, env: client.env, scopes: client.scopes },
    process.env.PARTNER_JWT_SECRET,
    { issuer: 'dzzlo-oms', audience: 'partner-api', expiresIn: '15m' }
  );
  res.status(200).json({ access_token, token_type: 'Bearer', expires_in: 900 });
});
```

Security notes: this endpoint gets its **own strict rate limit** (e.g. 10/min per IP+client_id — it's the brute-force target), uniform error body, and no distinction between "unknown client" and "bad secret".

## 2.2 `partner_auth` middleware

`api_v3/middleware/partner_auth.js` — mirrors the shape of `getUserFromToken` + `userCache`, but a separate trust domain:

```js
const clientCache = new Map(); // per-process, TTL ~60s — mirrors auth.js userCache pattern

exports.partner_auth = asyncHandler(async (req, res, next) => {
  const auth = req.headers.authorization || '';
  if (!auth.startsWith('Bearer ')) return next(new ErrorResponse('UNAUTHENTICATED', 401));

  let claims;
  try {
    claims = jwt.verify(auth.slice(7), process.env.PARTNER_JWT_SECRET, {
      issuer: 'dzzlo-oms',
      audience: 'partner-api', // app JWTs (different secret+aud) can NEVER pass
    });
  } catch (e) {
    return next(new ErrorResponse('UNAUTHENTICATED', 401));
  }

  // Live client lookup (cached) — catches revocation/suspension inside token TTL
  const client = await getCachedClient(claims.sub); // findOne({ client_id: claims.sub })
  if (!client || client.status !== 'active') return next(new ErrorResponse('CLIENT_DISABLED', 403));

  if (client.allowed_ips?.length && !ipAllowed(req, client.allowed_ips))
    return next(new ErrorResponse('IP_NOT_ALLOWED', 403)); // Phase 4 details proxy trust

  req.partner = {
    client_id: client.client_id,
    client,                       // full doc for tier/quota checks
    co_id: client.co_id,          // ← THE tenant. Controllers use only this.
    env: client.env,
    scopes: claims.scopes,        // scope snapshot from token
  };
  req.request_id = crypto.randomUUID();
  res.set('X-Request-Id', req.request_id);
  next();
});
```

Why check the DB (cached) when the token is already signed? **Revocation.** Suspending a client must take effect in ≤ cache-TTL seconds, not at token expiry. 60 s TTL keeps the hot path at ~zero DB cost — same trade-off `userCache` already makes.

## 2.3 Tenant-status gate

Partner variant of `check_user_company_status()` — the **owning tenant** must be active; a suspended/blocked company blocks its partners too (subscription lapse, fraud hold):

```js
exports.check_partner_company_status = asyncHandler(async (req, res, next) => {
  const ok = await companyIsActive(req.partner.co_id); // reuse the same helper/flags the app gate reads
  if (!ok) return next(new ErrorResponse('TENANT_SUSPENDED', 403));
  next();
});
```

Reuse the exact status flags/helper the existing gate reads — do not invent a parallel notion of "active company."

## 2.4 `partner_scope` — least privilege

Mirrors `scope()` from `api_v3/auth.js`:

```js
exports.partner_scope = (...required) => (req, res, next) => {
  const have = req.partner?.scopes || [];
  if (!required.every(s => have.includes(s)))
    return next(new ErrorResponse('INSUFFICIENT_SCOPE', 403));
  next();
};
```

An orders-only credential gets `scopes: ['orders:write']` and receives a stable 403 on `/partner/vouchers` — least privilege is enforced per route, not per partner.

## 2.5 Router assembly & isolated mount

`api_v3/routes/partner/index.js`:

```js
const router = express.Router();

router.post('/oauth/token', tokenLimiter, token);            // public: only strict-limited endpoint

router.use(partner_auth);                                     // everything below is authenticated
router.use(check_partner_company_status);
router.use(partner_rate_limit);                               // Phase 4
router.use(partner_meter);                                    // Phase 5/6 — router-level: unbypassable
router.use(express.json({ limit: '100kb' }));                 // partner-specific body cap (Phase 4)

router.use('/orders', partner_scope('orders:write'), ordersRouter);     // Phase 3
router.use('/vouchers', partner_scope('vouchers:write'), vouchersRouter);

module.exports = router;
```

Mount in `api_v/api3.js`:

```js
// BEFORE the app-auth chain is applied, or explicitly exempted from it:
router.use('/partner', require('../api_v3/routes/partner'));
```

**Isolation requirements (verify in repo during implementation):**

1. `api_key_v1()` in `dzzlo_oms.js` and `api_key_v3()` in `api_v/api3.js` must **skip** `/api/v3/partner/*` (path-prefix exemption or mount ordering) — partners never hold the internal app key.
2. `getUserFromToken` / `check_user_version()` must not run on partner routes (no user-agent/version semantics for servers).
3. Conversely, no partner middleware runs on app routes. The two chains share only `helmet`, `sanitizeMongo`, `compression`.
4. Feature flag: wrap the mount in `if (process.env.PARTNER_API_ENABLED === 'true')` — rollout/rollback lever for Phase 7.

## 2.6 Testing (supertest matrix)

| Case | Expect |
| --- | --- |
| No/malformed `Authorization` | 401 `UNAUTHENTICATED` |
| Expired partner token | 401 |
| **App JWT on partner route** | 401 (audience/secret mismatch) |
| **Partner token on app route** | app `protect` rejects |
| Valid token, client suspended after issuance | 403 `CLIENT_DISABLED` (≤ cache TTL) |
| Valid token, tenant suspended | 403 `TENANT_SUSPENDED` |
| Orders-scope token → `/partner/vouchers` | 403 `INSUFFICIENT_SCOPE` |
| Token endpoint: wrong id vs wrong secret | identical 401 body |
| Token endpoint hammering | 429 from `tokenLimiter` |
| `PARTNER_API_ENABLED=false` | 404 on all partner routes |

## Phase 2 checklist

- [ ] `POST /partner/oauth/token` with uniform errors + dedicated limiter.
- [ ] `partner_auth` (aud/iss verify, cached live-client check, IP hook, `X-Request-Id`).
- [ ] `check_partner_company_status` reusing existing company-status flags.
- [ ] `partner_scope` gate.
- [ ] Router mounted at `/api/v3/partner`, exempt from app key/JWT chain, behind `PARTNER_API_ENABLED`.
- [ ] Full supertest matrix green, including both cross-surface token rejection tests.
