# 10. Pricing Strategy — What Should the Subscription Be On?

*Planning discussion 2026-07-29. The candidates on the table: per user, fixed monthly per company, per order placed, per litre dispensed, per app usage.*

## What Makes a Good Value Metric (for this market)

Four tests, all must pass:

1. **Tracks the value the customer receives** — a bigger dealer pays more only because they get more.
2. **Predictable for the buyer** — the Indian SMB mental model is a fixed monthly bill (Tally, Zoho, electricity). Surprise bills kill trust.
3. **Cheap to enforce, hard to game** — no policing, no audits, no fights.
4. **Never taxes the behaviour we need maximised** — DZZLO's product *is* the complete ledger; any meter that makes a dealer think "this entry costs money" pushes orders back to phone calls and destroys the data completeness that is the value.

Plus the hard constraint from `../company/10_AFFORDABILITY_PROBLEM.md`: a pump nets ₹1.5–4L/month, so the entry price must sit well under 1% of operating profit — **ATP (ability to pay), not WTP, is binding**.

## Scoring the Candidates

| Metric | Value alignment | Predictable | Enforceable | Gaming risk | Verdict |
| --- | --- | --- | --- | --- | --- |
| **Per user** | Weak (users = the network, not the value) | Yes | Terrible (login sharing is cultural) | High | ❌ Already decided against — never |
| **Flat monthly per company** | Weak alone (small pump pays like a big one) | Perfect | Perfect | None | ✅ **The base — fix value-scaling with tiers, not meters** |
| **Per order placed** | Medium | Poor | OK | High — dealers ration entries | ❌ as a price. ✔ only as a *generous* fair-use tier boundary |
| **Per litre dispensed** | Good on paper (industry's native unit) | Poor | Poor (self-reported volumes) | High — under-recording breaks the ledger | ❌ for the SaaS fee — dealer commission is a **fixed ₹/litre**, so a per-litre software fee reads as a margin tax, the most hated framing in this trade. ✔ later as a *payments/lending* take-rate (bps on money moved, where the industry accepts it) |
| **App usage (calls/time)** | None | Worst | Opaque | — | ❌ Creates fear of opening the app. Only correct for the partner API (`tasks_11` already designed call-tiers — the buyer there is a tech company) |

## The Sizing Metrics That Actually Work Here

The trick is: don't meter *activity*, tier on *size* — using units the trade already thinks in, that are physical or self-evidencing:

- **Outlets/branches under the GSTIN** — "I have 3 pumps" is how dealers describe themselves. Physical, verifiable, ungameable.
- **Active credit customers** (`dealer_custs` relationships) — the credit book **is** the product's value driver; it grows exactly as the dealer grows; and pruning it to save money means giving up the ledger benefit — self-defeating, so nobody games it.
- **Transactions/month** — only as a high fair-use line that maybe 5% of a tier ever touches, never as a live meter.

## Recommended Architecture — Three Layers

### Layer 1 (now): flat monthly per company, three published tiers + Enterprise

Per GSTIN (each sister company its own subscription — decided), unlimited users always, ex-GST pricing from `../company/02_PRICING_STRATEGY.md` as the starting sheet:

| | **Starter** ₹599 | **Growth** ₹1,799 (hero) | **Pro** ₹4,999 (anchor) | **Enterprise** quote |
| --- | --- | --- | --- | --- |
| Outlets/branches | 1 | up to 3 | unlimited | multi-GSTIN group |
| Active credit customers | ~25 | ~150 | unlimited | unlimited |
| Transactions/mo (fair use) | 500 | 5,000 | unlimited | unlimited |
| Features | Core OMS, ledger, GST invoices, delivery OTP | + WhatsApp automation, reports/analytics, bulk exports | + DIP module, advanced analytics, priority support | + API, OMC reconciliation, SLA |

Kano floor unchanged: **GST invoicing, the ledger, and order flow are never gated at any tier** — quota breach triggers nudge → grace → pause of premium extras only, never a blocked order.

### Layer 2 (next): monetize the money, not the software

This is where scaling revenue lives without margin-tax optics: a **revenue share / take-rate on the IPG payments leg** (built into the Easebuzz/UBI commercials — 0.1–0.5% or flat ₹ per settlement) and later **1.5–3% of embedded-lending economics**. Basis points on money moved are normal in finance; the same points on litres of software usage are an insult. This layer is also what lets Layer 1 stay cheap enough for the ATP constraint.

### Layer 3 (future): customer-side fleet plans — per vehicle slabs

For transporters, per-vehicle pricing **is** the industry norm (telematics/FMS in India runs ₹200–500/vehicle/month), so the fleet product can tier on fleet size in slabs (≤10 / ≤50 / unlimited vehicles) — flat monthly per slab, not a live per-vehicle meter. Core dealer-trading stays free (network protection — decided/recommended in [[08-dzzlo-subscription-strategy]]).

## India-Specific Mechanics

- **Price ex-GST, +18% (SAC 998434), and say it proudly**: a registered dealer claims the GST back as input credit and deducts the fee as a business expense — effective cost is meaningfully below sticker.
- **Keep every tier under ₹15,000/month** → UPI Autopay/eNACH e-mandates auto-debit without per-cycle authentication. All proposed tiers clear this easily.
- **Annual prepay = ~2 months free** (the corpus's ~17%): upfront cash for a startup, and it deletes 11 collection events a year.
- **Founder pricing** for the first cohort, grandfathered loudly — early dealers become references; the corpus says the CA and the OMC Territory Manager are the real channels, and references are what move them.
- **Anchors for the sales pitch**: TallyPrime ~₹750/mo, Zoho Books Professional ₹1,499/mo (Growth deliberately sits next to it), a munim at ₹12–25k/mo, and the killer: *one bad-debt write-off costs more than a decade of DZZLO*.

## How to Set the Actual Numbers

Don't survey — **sell**. Phase 2 is sales-led precisely so the first ~50 dealer negotiations *are* the price research: publish Starter/Growth/Pro on the website, quote Enterprise, log every objection and every discount given, and revisit the sheet at 50 paying dealers. Raise prices for new cohorts only. Two health numbers: **% of paying dealers on Growth or above** (target > 40% — if everyone lands on Starter the *boundaries* are wrong, not the price) and **churn by tier**.

## Decisions for the Owner

1. Sign off the metric set: outlets + active credit customers + fair-use transactions (or argue an alternative).
2. The boundary numbers per tier (the ~25/~150 credit-customer lines above are proposals).
3. Annual discount size.
4. DIP: included in Pro vs. a separate paid add-on.
5. Launch-cohort price + how long grandfathering lasts.

## Related

[[08-dzzlo-subscription-strategy]] · [[07-upselling-without-a-buy-button]] · `../company/02_PRICING_STRATEGY.md` · `../company/10_AFFORDABILITY_PROBLEM.md` · `../company/13_REVENUE_GENERATION.md` · `../../tasks/tasks_11_partner_api/`
