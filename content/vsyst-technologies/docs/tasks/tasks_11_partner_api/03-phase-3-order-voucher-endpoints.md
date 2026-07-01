# Phase 3 — The Two Endpoints: Orders & Vouchers (+ Idempotency)

**Outcome:** `POST /api/v3/partner/orders` and `POST /api/v3/partner/vouchers` are live, calling the **same** create services the app uses, with mandatory `Idempotency-Key` dedupe and a stable partner-safe error contract.

> **Vertical-SaaS lens:** an order or voucher is not a generic row — creating one triggers the domain's real business rules (credit limits, company gates, ledger effects). The only acceptable design is that partner writes flow through the identical service the app uses; a forked "partner version" would silently drift into a weaker second set of business rules. Idempotency is equally domain-driven: a partner's retry must never double-charge a dealer's credit or double-book an order.

---

## 3.1 Contracts (design-first)

`POST /partner/orders` — scope `orders:write`; headers `Authorization: Bearer …`, `Idempotency-Key: <uuid>`:

```jsonc
// request (field list to be finalized from the EXISTING v3 order create service — see 3.2)
{
  "cust_co_id": "…",            // counterparty company (validated against tenant's relations)
  "items": [{ "prod_id": "…", "qty": 2 }],
  "delivery": { "address_id": "…", "notes": "…" },
  "partner_ref": "PO-2026-0091" // partner's own reference, echoed back
}
// 201 response
{
  "success": true,
  "data": { "order_id": "…", "order_no": "…", "status": "…", "partner_ref": "PO-2026-0091" },
  "request_id": "…"
}
```

`POST /partner/vouchers` — scope `vouchers:write`, same envelope, payload mirroring the `voc_msts` create DTO (`voc_type`, `amount`, counterparty, `partner_ref`).

Contract rules:

- **`co_id` is never accepted from the body.** The tenant comes from `req.partner.co_id`; any `co_id`-like field in the payload is rejected as an unknown field. (Top cross-tenant control — see Phase 4 threat T3.)
- Responses expose only partner-safe fields — no internal flags, no populated user objects, no Mongoose internals.

## 3.2 Reuse, don't fork — service extraction

Read the existing v3 order/voucher create controllers first. Two cases:

1. **Logic already in a service** → partner controller calls it directly. Done.
2. **Logic inline in the app controller** → extract to `api_v3/services/orders.service.js` / `vouchers.service.js` as a behavior-neutral refactor, then point **both** the app controller and the partner controller at it. The extraction ships with regression tests on the app path *before* the partner endpoint lands.

```js
// api_v3/controllers/partner/orders.js
exports.createOrder = asyncHandler(async (req, res) => {
  const order = await orderService.create({
    ...req.validatedBody,             // allow-listed fields only (3.4)
    co_id: req.partner.co_id,         // tenant forced from credential
  }, {
    actor: { type: 'api_client', client_id: req.partner.client_id }, // attribution
    source: 'partner_api',
  });
  res.status(201).json({ success: true, data: toPartnerOrderDTO(order), request_id: req.request_id });
});
```

Attribution fields (`created_via: 'partner_api'`, `api_client_id`) are added to the documents **additively** (new optional fields on `order_msts`/`voc_msts`) so support and reporting can distinguish app writes from partner writes.

## 3.3 Idempotency — model + middleware

`api_v3/models/idempotency_keys.js`:

```js
const idempotencySchema = new mongoose.Schema({
  key: { type: String, required: true },
  client_id: { type: String, required: true },
  endpoint: { type: String, required: true },          // 'POST /partner/orders'
  request_hash: { type: String, required: true },      // sha256(canonical body)
  status: { type: String, enum: ['in_flight', 'completed'], default: 'in_flight' },
  response_code: Number,
  response_body: Object,                                // the partner-safe body we returned
  created_at: { type: Date, default: Date.now, expires: 60 * 60 * 48 }, // TTL 48h
});
idempotencySchema.index({ client_id: 1, endpoint: 1, key: 1 }, { unique: true });
```

Middleware flow (`api_v3/middleware/idempotency.js`) — **insert-first** so concurrency is settled by the unique index, not application logic:

```
1. key = req.headers['idempotency-key']
   → missing/malformed (not 1–255 chars) → 400 IDEMPOTENCY_KEY_REQUIRED
2. hash = sha256(canonicalJson(req.body))
3. try insert { key, client_id, endpoint, request_hash: hash, status: 'in_flight' }
   ├─ OK → fresh request: wrap res.json to persist { response_code, response_body,
   │        status:'completed' } on the way out, then continue to controller
   └─ E11000 duplicate → load existing record:
        ├─ request_hash ≠ hash        → 422 IDEMPOTENCY_KEY_REUSED (same key, different payload)
        ├─ status = 'completed'       → replay stored response, header Idempotent-Replay: true
        └─ status = 'in_flight'      → 409 REQUEST_IN_FLIGHT (partner retries with backoff)
```

Notes:

- Scoped `(client_id, endpoint, key)` — one partner's keys can never collide with (or replay) another's.
- Replays are marked so Phase 5 records them `billable: false` — retries are free, by design.
- 48 h TTL matches the longest reasonable partner retry window; Mongo TTL index handles cleanup.
- If the process dies mid-flight, the `in_flight` record blocks the key until TTL — acceptable v1 trade-off; note it in partner docs ("use a new key if you get 409 for >10 min"). A `stale_after` sweep is a v1.1 nicety.

## 3.4 Strict input validation

- **Allow-list** validation per endpoint (use whatever the repo already uses — express-validator/joi/manual — match it): every field explicitly declared with type/range; **unknown fields rejected**, not stripped silently (partners should learn about their bugs at integration time, and internal fields like statuses/rates must be unsettable).
- `sanitizeMongo` is already global — partner router inherits it; validation still re-checks types so operators like `$gt` die at the schema level too.
- Validated output lands on `req.validatedBody`; controllers never touch `req.body` directly.

## 3.5 Partner-safe error contract

Single envelope, stable machine-readable codes, zero internals:

```json
{ "success": false, "error": { "code": "CREDIT_LIMIT_EXCEEDED", "message": "Order exceeds available credit limit.", "request_id": "…" } }
```

| HTTP | `code` | When |
| --- | --- | --- |
| 400 | `VALIDATION_FAILED` (+ `fields[]`) | schema violation, unknown field |
| 400 | `IDEMPOTENCY_KEY_REQUIRED` | header missing/malformed |
| 401 | `UNAUTHENTICATED` / `invalid_client` | Phase 2 |
| 403 | `INSUFFICIENT_SCOPE` / `CLIENT_DISABLED` / `TENANT_SUSPENDED` / `IP_NOT_ALLOWED` | Phase 2/4 |
| 409 | `REQUEST_IN_FLIGHT` | concurrent same-key call |
| 422 | `IDEMPOTENCY_KEY_REUSED` | same key, different payload |
| 422 | `CREDIT_LIMIT_EXCEEDED`, `INVALID_RELATION`, `PRODUCT_UNAVAILABLE`, … | domain rules from the shared service (enumerate while reading it) |
| 429 | `RATE_LIMITED` (+ `Retry-After`) | Phase 4 |
| 500 | `INTERNAL_ERROR` | anything unmapped — logged with `request_id`, never leaked |

A partner-scoped error handler maps `ErrorResponse` instances to this table; unknown/unexpected errors log the stack internally (keyed by `request_id`) and return only `INTERNAL_ERROR`. Mongoose/stack text never reaches a partner.

## 3.6 Testing

- **Happy paths:** both endpoints create documents identical (minus attribution fields) to app-created ones; domain side effects (credit check, ledger) fire — assert against the same fixtures the app tests use.
- **Tenant forcing (critical):** payload smuggling `co_id`/`company` fields → 400; created doc's `co_id` always = credential's.
- **Idempotency:** same key+body twice → one document, second response replayed with `Idempotent-Replay: true`; same key different body → 422; two concurrent same-key requests (Promise.all) → one 201, one 409/replay; different clients same key → two documents.
- **Validation:** unknown field, wrong types, `$gt` payload → 400 with `fields[]`.
- **Error mapping:** force a domain failure (over credit limit) → 422 stable code, no stack text in body.

## Phase 3 checklist

- [ ] Field lists confirmed from existing v3 create services; DTOs documented.
- [ ] Service extraction done (if needed) with app-path regression tests green **first**.
- [ ] `POST /partner/orders`, `POST /partner/vouchers` via shared services; attribution fields added additively.
- [ ] `idempotency_keys` model + middleware (insert-first, TTL, replay marking).
- [ ] Allow-list validation; unknown fields rejected; `req.validatedBody` only.
- [ ] Partner error handler + code table above; 500s carry `request_id` only.
- [ ] Full test suite incl. tenant-forcing and concurrency tests green.
