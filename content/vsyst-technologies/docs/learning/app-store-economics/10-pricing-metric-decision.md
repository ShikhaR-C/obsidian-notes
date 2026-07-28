# 10. Pricing Strategy — What Should the Subscription Be On?

_Planning discussion 2026-07-29. The candidates on the table: per user, fixed monthly per company, per order placed, per litre dispensed, per app usage._

## What Makes a Good Value Metric (for this market)

Four tests, all must pass:

1. **Tracks the value the customer receives** — a bigger dealer pays more only because they get more.
2. **Predictable for the buyer** — the Indian SMB mental model is a fixed monthly bill (Tally, Zoho, electricity). Surprise bills kill trust.
3. **Cheap to enforce, hard to game** — no policing, no audits, no fights.
4. **Never taxes the behaviour we need maximised** — DZZLO's product _is_ the complete ledger; any meter that makes a dealer think "this entry costs money" pushes orders back to phone calls and destroys the data completeness that is the value.

Plus the hard constraint from `../company/10_AFFORDABILITY_PROBLEM.md`: a pump nets ₹1.5–4L/month, so the entry price must sit well under 1% of operating profit — **ATP (ability to pay), not WTP, is binding**.

## Scoring the Candidates

| Metric                       | Value alignment                             | Predictable | Enforceable                          | Gaming risk                              | Verdict                                                                                                                                                                                                                                                |
| ---------------------------- | ------------------------------------------- | ----------- | ------------------------------------ | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Per user**                 | Weak (users = the network, not the value)   | Yes         | Terrible (login sharing is cultural) | High                                     | ❌ Already decided against — never                                                                                                                                                                                                                     |
| **Flat monthly per company** | Weak alone (small pump pays like a big one) | Perfect     | Perfect                              | None                                     | ✅ **The base — fix value-scaling with tiers, not meters**                                                                                                                                                                                             |
| **Per order placed**         | Medium                                      | Poor        | OK                                   | High — dealers ration entries            | ❌ as a price. ✔ only as a _generous_ fair-use tier boundary                                                                                                                                                                                           |
| **Per litre dispensed**      | Good on paper (industry's native unit)      | Poor        | Poor (self-reported volumes)         | High — under-recording breaks the ledger | ❌ for the SaaS fee — dealer commission is a **fixed ₹/litre**, so a per-litre software fee reads as a margin tax, the most hated framing in this trade. ✔ later as a _payments/lending_ take-rate (bps on money moved, where the industry accepts it) |
| **App usage (calls/time)**   | None                                        | Worst       | Opaque                               | —                                        | ❌ Creates fear of opening the app. Only correct for the partner API (`tasks_11` already designed call-tiers — the buyer there is a tech company)                                                                                                      |

## The Sizing Metrics That Actually Work Here

The trick is: don't meter _activity_, tier on _size_ — using units the trade already thinks in, that are physical or self-evidencing:

- **Outlets/branches under the GSTIN** — "I have 3 pumps" is how dealers describe themselves. Physical, verifiable, ungameable.
- **Active credit customers** (`dealer_custs` relationships) — the credit book **is** the product's value driver; it grows exactly as the dealer grows; and pruning it to save money means giving up the ledger benefit — self-defeating, so nobody games it.
- **Transactions/month** — only as a high fair-use line that maybe 5% of a tier ever touches, never as a live meter.

## Recommended Architecture — Three Layers

### Layer 1 (now): flat monthly per company, three published tiers + Enterprise

Per GSTIN (each sister company its own subscription — decided), unlimited users always, ex-GST pricing from `../company/02_PRICING_STRATEGY.md` as the starting sheet:

|                            | **Starter** ₹599                             | **Growth** ₹1,799 (hero)                               | **Pro** ₹4,999 (anchor)                            | **Enterprise** quote           |
| -------------------------- | -------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------- | ------------------------------ |
| Outlets/branches           | 1                                            | up to 3                                                | unlimited                                          | multi-GSTIN group              |
| Active credit customers    | ~25                                          | ~150                                                   | unlimited                                          | unlimited                      |
| Transactions/mo (fair use) | 500                                          | 5,000                                                  | unlimited                                          | unlimited                      |
| Features                   | Core OMS, ledger, GST invoices, delivery OTP | + WhatsApp automation, reports/analytics, bulk exports | + DIP module, advanced analytics, priority support | + API, OMC reconciliation, SLA |

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
- **Anchors for the sales pitch**: TallyPrime ~₹750/mo, Zoho Books Professional ₹1,499/mo (Growth deliberately sits next to it), a munim at ₹12–25k/mo, and the killer: _one bad-debt write-off costs more than a decade of DZZLO_.

## How to Set the Actual Numbers

Owner direction (2026-07-29): **premium-leaning, cost-modelled, finalized later** — a mix of "position above Zoho" and "decide after real sales". The process:

1. **Build the cost model first (price floor)** — fill-in worksheet with formulas, scenario grid, and data-gathering checklist: [[11-cost-model-worksheet]]. Estimate monthly/yearly cost to serve, then set rates against a target earning. Inputs to gather:
   - _Variable per tenant_: SMS/OTP (2Factor.in per-message), WhatsApp Business API conversation charges, push (OneSignal tier), storage/compute share (AWS + Mongo), SES email, support minutes per dealer per month.
   - _Fixed_: salaries, infra base, PSO/BD travel, CA/compliance, office.
   - Floor = (fixed ÷ target tenant count + variable per tenant) × margin multiple; sanity-check the tier sheet against it (₹599/₹1,799/₹4,999 stay **placeholders** until this exists).
2. **Quote, don't publish, during the first sales phase.** Early deals are negotiated (premium anchor ~₹2,499+ thinking), every objection/discount logged; publish the sheet only once ~50 deals have validated it.
3. Two health numbers once selling: **% of paying dealers on Growth or above** (target > 40% — if everyone lands on Starter the _boundaries_ are wrong, not the price) and **churn by tier**.

## Decisions Taken (2026-07-29)

1. ✅ **Value metric = size proxies**: outlets/branches + active credit customers + generous fair-use transactions. No per-user, per-order, per-litre, or usage metering, ever.
2. ✅ **DIP module is included in Pro** — the anchor tier is "the full pump operating system", and DIP is the Growth→Pro upgrade trigger.

## Still Open (discussion pending)

1. **Price points** — via the cost model + premium positioning + quoted early sales, per the process above.
2. **Trial policy** — real tension identified by the owner: onboarding is inherently slow (a dealer must add customers, and _both_ sides need time to learn the app), so a 14-day clock is probably too short; but free-forever expectations are a real risk. Candidate resolutions to discuss:
   - **Activation-based clock**: the trial timer starts not at signup but at an activation milestone (e.g., first 5 customers linked or first 50 orders) — slow ramp-up doesn't eat the trial, yet there's always a clock.
   - **Calendar 30–45 days**: long enough to cover one full month-end + GST cycle.
   - **Milestone extensions**: 14-day base, auto-extended when usage milestones are hit (rewards engagement, expires on the disengaged).
   - **Pilot cohort with a signed end date**: free hand-held quarter for the first dealers, but against a letter that names the go-paid date and price — references without free-forever drift.
   - Whichever wins: the trial must end in a **state change** (downgrade to Starter features), never in data loss.
3. Tier boundary numbers (the ~25/~150 credit-customer lines are proposals), annual discount size, launch-cohort grandfathering duration.

## Related

[[08-dzzlo-subscription-strategy]] · [[07-upselling-without-a-buy-button]] · `../company/02_PRICING_STRATEGY.md` · `../company/10_AFFORDABILITY_PROBLEM.md` · `../company/13_REVENUE_GENERATION.md` · `../../tasks/tasks_11_partner_api/`
