# Phase 6 — Cost Calculation & Metering

**Outcome:** a versioned price book, per-client tiers with included quotas and overage rates, and a monthly roll-up job that turns `partner_usage` into a draft invoice per partner — with the metering hook placed so it cannot be bypassed.

> **Vertical-SaaS lens:** this is the expansion-revenue engine. Vertical SaaS pricing power comes from owning the workflow: an API order write is worth more than a generic API call because it carries credit checks, ledger effects, and delivery orchestration. Pricing is therefore **per business action** (an order placed, a voucher created), not per HTTP request — and the API line item rolls into the tenant's existing subscription invoice, one bill, which is exactly the convenience that keeps vertical-SaaS churn low.

---

## 6.1 Pricing model

**Unit = one billable business action** (Phase 5's `billable_unit`). Different actions price differently:

| `billable_unit` | Why it can price differently |
| --- | --- |
| `order_write` | heaviest domain flow — credit check, stock, delivery lifecycle |
| `voucher_write` | payment-adjacent, lighter lifecycle |

**Tiers** (per client, assigned on `api_clients.tier` — Phase 1):

| Tier | Included calls / month | Overage | Rate ceiling | Intended for |
| --- | --- | --- | --- | --- |
| `sandbox` | unlimited, **never billable** | — | 30/min | integration & certification |
| `starter` | 1,000 | per-unit list price | 60/min | tenant in-house tools |
| `growth` | 10,000 | discounted overage | 120/min | active ISV integrations |
| `scale` | 50,000 | negotiated | 300/min | high-volume partners |

(₹ figures are a commercial decision — the plan fixes the *mechanics*; actual prices land in the price book below, not in code.)

**Versioned price book** — `api_v3/models/partner_pricing.js`:

```js
const partnerPricingSchema = new mongoose.Schema({
  effective_from: { type: Date, required: true },        // price changes = NEW doc, never edit
  currency: { type: String, default: 'INR' },
  units: {                                               // list price per billable unit
    order_write: { type: Number, required: true },       // e.g. 2.00
    voucher_write: { type: Number, required: true },     // e.g. 1.00
  },
  tiers: {
    starter: { included: Number, overage_multiplier: Number }, // 1.0 = list
    growth:  { included: Number, overage_multiplier: Number }, // e.g. 0.8
    scale:   { included: Number, overage_multiplier: Number },
  },
});
partnerPricingSchema.index({ effective_from: -1 });
```

Append-only by rule: historical invoices stay reproducible because the roll-up picks the price doc effective at the **start of the billing month**. Per-client negotiated overrides go on `api_clients` (v1.1) — the mechanics don't change.

## 6.2 The metering hook — where, and why it can't be bypassed

**There is no separate "billing middleware" to forget.** The meter *is* Phase 5's `partner_meter`, mounted **router-level** in `routes/partner/index.js` before any route (Phase 2 chain). Consequences:

1. Any future partner route added under the router is metered automatically — no per-route opt-in to forget.
2. Billing derives from `partner_usage` **after the fact** — a controller bug can't "skip billing" without also skipping the response.
3. A CI guard makes this structural: a test introspects the partner router's stack and asserts `partner_meter` appears before the first route layer — adding a sibling router without the meter fails the build.
4. Monthly reconciliation (6.4) cross-checks `partner_usage` billable counts against attributed documents (`order_msts` where `created_via: 'partner_api'`) — a drift between the two is an alert, making the meter **tamper-evident**, not just present.

## 6.3 Quota tracking — cheap counters, not per-request aggregations

Running `count()` on `partner_usage` per request would melt under load. Instead a tiny counter collection, atomically incremented by the meter on billable calls:

```js
// partner_quota_counters: { client_id, month: '2026-07' (IST), used: Number }
PartnerQuotaCounters.updateOne(
  { client_id, month: istMonth(ts) },
  { $inc: { used: 1 } },
  { upsert: true }
);
```

- `partner_rate_limit` (Phase 4) reads this counter (cached ~60 s) for quota state.
- **v1 semantics:** soft quota — calls over `included` still succeed and accrue overage; response carries `X-Quota-Remaining` so well-behaved partners self-regulate. Hard-block (429 `QUOTA_EXCEEDED`) is a per-client flag, default **on** only for `sandbox`-tier production credentials (i.e. not-yet-upgraded trials).

## 6.4 Monthly roll-up → draft invoice

A scheduled job (reuse the repo's existing scheduler if present — cron/agenda; open question) on the 1st, 00:30 IST, for the prior **IST calendar month**:

```js
// 1. usage → per-unit counts
db.partner_usage.aggregate([
  { $match: { ts: { $gte: monthStartUtc, $lt: monthEndUtc }, billable: true } },
  { $group: { _id: { client_id: '$client_id', co_id: '$co_id', unit: '$billable_unit' },
              units: { $sum: 1 } } },
])
// 2. price with the price-book doc effective at monthStart + the client's tier:
//    charge = max(0, units_total - tier.included_prorated) × unit_price × tier.overage_multiplier
//    (included quota consumed in ts order across units — cheapest-first is a commercial choice, document it)
// 3. upsert into partner_invoices:
//    { client_id, co_id, month: '2026-06', line_items: [{unit, units, rate, amount}],
//      included_used, overage_units, total, currency, status: 'draft', pricing_ref }
```

- **Idempotent:** upsert keyed `(client_id, month)` — rerunning the job after a crash recomputes, never duplicates.
- **Draft, not charged:** v1 output is a reviewable draft folded into the tenant's subscription invoice by the existing billing process; auto-charging is out of scope.
- **Reconciliation (tamper-evidence, 6.2#4):** same job counts `order_msts`/`voc_msts` docs with `api_client_id` for the month and alerts on mismatch vs metered `order_write`/`voucher_write` counts.

## 6.5 Edge cases (decided now, so billing disputes have answers)

| Case | Ruling |
| --- | --- |
| Idempotent replay | `billable: false` — retries are free (partner-friendly, and Phase 3 marks them) |
| 4xx/5xx | never billable; 429s excluded from everything but abuse metrics |
| Sandbox env | never billable regardless of tier |
| Price change mid-month | price book doc effective at **month start** governs the whole month |
| Tier change mid-month | tier at month **end** governs (simple, partner-favorable if upgrading); document it |
| Month boundary | IST calendar month everywhere (matches usage roll-ups, Phase 5) |
| Clock skew / late writes | roll-up runs at 00:30 IST giving the meter 30 min of settle time |

## 6.6 Testing

- Pricing math: fixture usage docs → expected line items across included/overage boundaries, both units, each tier, `overage_multiplier` applied.
- Idempotent job: run twice → identical single invoice doc.
- Price-book versioning: usage spanning a price change → month billed at month-start price.
- Counter integrity: concurrent billable calls (Promise.all) → counter equals doc count.
- Router-stack CI guard (6.2#3) in place and failing when meter removed.
- Reconciliation alert fires on a manufactured drift (delete one usage doc).

## Phase 6 checklist

- [ ] `partner_pricing` price book (append-only) + initial doc with agreed prices.
- [ ] Tier table confirmed commercially; `api_clients.tier`/`monthly_quota` wired to it.
- [ ] Quota counters + `X-Quota-Remaining`; soft/hard semantics per tier.
- [ ] Monthly roll-up job → `partner_invoices` drafts (idempotent, IST months, pricing_ref pinned).
- [ ] Reconciliation check + alert.
- [ ] CI router-stack guard proving the meter is structural.
