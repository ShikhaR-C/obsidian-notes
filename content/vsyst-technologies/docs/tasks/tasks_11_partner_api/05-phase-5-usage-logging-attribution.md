# Phase 5 — Usage Logging & Attribution ("who called what")

**Outcome:** every partner call — success, failure, or replay — lands as one `partner_usage` document via a router-level meter hook, and saved aggregations answer **which API, how many times, by which partner** over any date range. This is the data source for billing (Phase 6), the partner dashboard (future), abuse alerts (Phase 4), and the audit trail.

> **Vertical-SaaS lens:** usage data is triple-duty in a vertical SaaS: (1) it is the **billing meter** — expansion revenue is computed from it, so it must be complete and tamper-evident; (2) it is the **audit trail** industry customers ask for ("which system placed this order?"); (3) it is **product analytics** for the platform motion — which partners are ramping, which endpoint to build next.

---

## 5.1 Decision: new collection vs extending `logs`

**Decision: a dedicated `partner_usage` collection**, while the existing global `logging()` → `logs` keeps running for ops parity.

| | extend `logs` | new `partner_usage` ✅ |
| --- | --- | --- |
| Retention | ops logs rotate short | billing needs ≥ 13 months |
| Indexes | tuned for debugging | tuned for `(client_id, ts)` roll-ups |
| Schema | request-shaped | billing-shaped (billable flags, units) |
| Risk | billing fields bloat every app log | zero impact on existing collection |

One write path, one hook (5.3) — not scattered `.create()` calls in controllers.

## 5.2 `partner_usage` model

`api_v3/models/partner_usage.js`:

```js
const partnerUsageSchema = new mongoose.Schema({
  // Attribution — the "who"
  client_id: { type: String, required: true },
  co_id: { type: mongoose.Schema.ObjectId, ref: 'companies', required: true },
  env: { type: String, enum: ['sandbox', 'production'], required: true },

  // The "what"
  endpoint: { type: String, required: true },   // route PATTERN: 'POST /partner/orders' — never raw URL
  method: { type: String, required: true },
  status_code: { type: Number, required: true },

  // The "how much"
  response_time_ms: Number,
  req_bytes: Number,                            // content-length in
  res_bytes: Number,                            // bytes out

  // Billing semantics (Phase 6 reads these)
  billable: { type: Boolean, required: true },  // 2xx && production && !replay
  billable_unit: { type: String, enum: ['order_write', 'voucher_write', null], default: null },
  idempotency_key: String,
  replay: { type: Boolean, default: false },    // idempotent replay → never billable

  // Tracing
  request_id: { type: String, required: true },
  ip: String,
  ts: { type: Date, default: Date.now },        // stored UTC; rendered/rolled up in IST (see 5.4)
}, { versionKey: false });

partnerUsageSchema.index({ client_id: 1, ts: -1 });
partnerUsageSchema.index({ co_id: 1, ts: -1 });
partnerUsageSchema.index({ endpoint: 1, ts: -1 });
partnerUsageSchema.index({ ts: 1 }, { expireAfterSeconds: 60 * 60 * 24 * 400 }); // ~13 months
```

Security note (T10): this schema stores the idempotency **key name** a partner chose (needed for billing disputes) but never tokens, secrets, or signatures; request/response **bodies are not stored** — sizes only. Order contents are already in `order_msts` with attribution fields (Phase 3).

## 5.3 The meter hook — `partner_meter`

Mounted **router-level** in Phase 2's chain (after `partner_auth`, before routes) so no partner route can exist without it — this same middleware is Phase 6's un-bypassable metering point:

```js
// api_v3/middleware/partner_meter.js
const BILLABLE_UNITS = { 'POST /partner/orders': 'order_write', 'POST /partner/vouchers': 'voucher_write' };

exports.partner_meter = (req, res, next) => {
  const started = process.hrtime.bigint();
  res.on('finish', () => {                       // fires for EVERY outcome incl. 4xx/429
    const endpoint = `${req.method} ${req.baseUrl}${req.route?.path || ''}`.replace(/\/$/, '');
    const replay = res.getHeader('Idempotent-Replay') === 'true';
    const ok = res.statusCode >= 200 && res.statusCode < 300;
    PartnerUsage.create({
      client_id: req.partner.client_id, co_id: req.partner.co_id, env: req.partner.env,
      endpoint, method: req.method, status_code: res.statusCode,
      response_time_ms: Number((process.hrtime.bigint() - started) / 1000000n),
      req_bytes: Number(req.headers['content-length'] || 0),
      res_bytes: Number(res.getHeader('content-length') || 0),
      billable: ok && !replay && req.partner.env === 'production' && !!BILLABLE_UNITS[endpoint],
      billable_unit: ok && !replay ? (BILLABLE_UNITS[endpoint] || null) : null,
      idempotency_key: req.headers['idempotency-key'], replay,
      request_id: req.request_id, ip: req.ip, ts: new Date(),
    }).catch(err => console.error('[partner_meter] write failed', req.request_id, err)); // never block the response
  });
  next();
};
```

Properties: fire-and-forget (a metering hiccup must never fail a partner's order); records failures too (`billable:false`) so abuse/error-rate alerts have data; `endpoint` is the route pattern, keeping cardinality flat.

## 5.4 The headline query — *which API, how many times, by which partner*

Per-partner, per-endpoint counts over a date range (all boundaries computed in **IST**, stored UTC):

```js
// e.g. June 2026 IST: [2026-05-31T18:30:00Z, 2026-06-30T18:30:00Z)
db.partner_usage.aggregate([
  { $match: { ts: { $gte: fromUtc, $lt: toUtc }, env: 'production' } },
  { $group: {
      _id: { client_id: '$client_id', co_id: '$co_id', endpoint: '$endpoint' },
      calls: { $sum: 1 },
      billable_calls: { $sum: { $cond: ['$billable', 1, 0] } },
      errors: { $sum: { $cond: [{ $gte: ['$status_code', 400] }, 1, 0] } },
      avg_ms: { $avg: '$response_time_ms' },
      p_bytes_out: { $sum: '$res_bytes' },
  }},
  { $sort: { '_id.client_id': 1, calls: -1 } },
])
```

Variants (same index, different `$group`): daily series per client (`$dateTrunc` with `timezone: 'Asia/Kolkata'`) for the dashboard; error-rate per client for Phase 4 alerts; top tenants by partner volume for the platform-adoption metric.

## 5.5 Testing

- Hook writes exactly one doc per request: 201, 400, 403, 429, and replay cases — assert field correctness for each (esp. `billable` truth table: only 2xx + production + non-replay + priced endpoint).
- Fire-and-forget: metering write forced to throw → response still 201; error logged with `request_id`.
- Aggregation: fixture set spanning an IST month boundary → counts land in the correct month.
- Redaction: no doc contains an `authorization` value or secret material.

## Phase 5 checklist

- [ ] `partner_usage` model + four indexes + 400-day TTL.
- [ ] `partner_meter` mounted router-level (Phase 2 chain) — every partner route covered.
- [ ] Billable truth table implemented and unit-tested.
- [ ] Headline aggregation + daily-series variant saved (script or admin endpoint).
- [ ] IST boundary handling verified against repo time-helper convention (open question #7).
- [ ] Redaction verified — no secret material in any usage doc.
