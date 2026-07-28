# 11. Cost-to-Serve Model — Worksheet & Boilerplate

_Feeds the open price-point decision in [[10-pricing-metric-decision]]. Fill the blanks from real bills — the data-gathering checklist at the bottom is one afternoon of work. Copy the tables into Google Sheets for live formulas; this note stays the source of truth for the structure._

## The Whole Model in Six Lines

| Symbol             | Meaning                                               | Formula             |
| ------------------ | ----------------------------------------------------- | ------------------- |
| **F**              | Fixed monthly costs (exist even with 0 tenants)       | Worksheet A         |
| **V**              | Variable cost per active tenant per month             | Worksheet B         |
| **C(N)**           | Cost to serve one tenant when we have N tenants       | `F ÷ N + V`         |
| **P_gross**        | Gross-margin price floor (SaaS health: 75–80% margin) | `V ÷ (1 − 0.8)`     |
| **N_be(P)**        | Tenants needed to break even at price P               | `F ÷ (P − V)`       |
| **N_target(P, T)** | Tenants needed to earn target profit T/month          | `(F + T) ÷ (P − V)` |

**The key insight to expect:** V will come out tiny (this is why SaaS works). So the floor almost never binds — the real output of this model is **N_target: how many paying dealers each candidate price demands** to cover payroll plus the profit we want. Price and dealer-count are the same decision seen from two sides.

---

## Worksheet A — Fixed Monthly Costs (F)

| Item                                                                                               | Where to get the number                        | ₹/month    |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------- | ---------- |
| Salaries + founder draw (dev, support, BD)                                                         | Payroll                                        | \_\_\_     |
| AWS (EC2/PM2 servers, S3, bandwidth, SES base)                                                     | AWS billing console — average of last 3 months | \_\_\_     |
| MongoDB Atlas                                                                                      | Atlas invoice, last 3 months average           | \_\_\_     |
| Apple Developer Program                                                                            | $99/yr ≈ ₹8,300 → ÷ 12                         | ~₹700      |
| Google Play ($25 one-time) + domain + SSL + misc SaaS (GitHub, OneSignal plan if paid, monitoring) | Card statements — list them all once           | \_\_\_     |
| CA / GST filings / compliance / accounting                                                         | CA invoice                                     | \_\_\_     |
| Office share (rent, internet, electricity)                                                         | Actuals                                        | \_\_\_     |
| Baseline marketing/BD retainer (non-deal-specific)                                                 | Actuals                                        | \_\_\_     |
| **Contingency buffer**                                                                             | +10% of the above                              | \_\_\_     |
| **F =**                                                                                            |                                                | **\_\_\_** |

## Worksheet B — Variable Cost per Tenant (V)

Method: **unit rate × measured monthly volume per average active dealer**. Volumes come from production data (`logs` collection, Firebase Analytics, 2Factor dashboard) — _measure, don't guess_. Unit rates below are ballparks from mid-2026; **confirm every rate card before relying on it**.

| Driver                                                            | Unit rate (confirm!)                                                    | Units / tenant / month (from prod data) | ₹ / tenant / mo |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------- | --------------- |
| SMS OTP — logins, delivery OTPs, invites (2Factor)                | ~₹0.15–0.25 per SMS                                                     | \_\_\_                                  | \_\_\_          |
| WhatsApp Business API — reminders, digests (planned)              | Utility ~₹0.12–0.35 per message — check Meta's current India card       | \_\_\_                                  | \_\_\_          |
| Push notifications (OneSignal)                                    | ₹0 on free tier — note the threshold where it turns paid                | \_\_\_                                  | ~0              |
| Email (SES)                                                       | ~₹0.009 per mail — usually ₹1–5/tenant                                  | \_\_\_                                  | \_\_\_          |
| Marginal infra (compute/storage growth per added tenant)          | (ΔAWS+Atlas over last 6 mo) ÷ (Δ tenants)                               | —                                       | \_\_\_          |
| Subscription collection — e-mandate/NACH per-debit or gateway fee | From Easebuzz/UBI terms; ₹5–15/debit typical                            | 1                                       | \_\_\_          |
| PDF/Excel generation compute                                      | Fold into marginal infra unless measurable                              | —                                       | ~0              |
| **Support time** — often the biggest early-stage line             | (minutes/tenant/mo from call history) × (loaded ₹/min of support staff) | \_\_\_                                  | \_\_\_          |
| **V =**                                                           |                                                                         |                                         | **\_\_\_**      |

## Worksheet C — CAC (separate from the floor; feeds payback)

| Item                                                  | ₹ per closed deal |
| ----------------------------------------------------- | ----------------- |
| Field visits / demos (travel, founder time)           | \_\_\_            |
| TM / CA referral or commission                        | \_\_\_            |
| Onboarding hand-holding hours × loaded rate           | \_\_\_            |
| **CAC =** total sales+onboarding spend ÷ deals closed | **\_\_\_**        |

Health checks: **payback months** = CAC ÷ (P − V) → aim under 12. **LTV : CAC ≥ 3**, where LTV ≈ (P − V) × expected months retained.

## Worksheet D — Scenario Grid (fill after A and B)

Use **ARPA** (average revenue per account across the real tier mix), not the hero price alone.

| N tenants | F ÷ N  | C(N) = F/N + V | Profit/mo at ARPA ₹1,500 | at ₹2,000 | at ₹2,500 |
| --------- | ------ | -------------- | ------------------------ | --------- | --------- |
| 25        | \_\_\_ | \_\_\_         | \_\_\_                   | \_\_\_    | \_\_\_    |
| 50        | \_\_\_ | \_\_\_         | \_\_\_                   | \_\_\_    | \_\_\_    |
| 100       | \_\_\_ | \_\_\_         | \_\_\_                   | \_\_\_    | \_\_\_    |
| 250       | \_\_\_ | \_\_\_         | \_\_\_                   | \_\_\_    | \_\_\_    |
| 500       | \_\_\_ | \_\_\_         | \_\_\_                   | \_\_\_    | \_\_\_    |

Profit/mo = `N × (ARPA − V) − F`.

## Worked Example (placeholder numbers — replace every one)

Say F = ₹3,00,000 (team ₹2.4L, infra ₹25k, compliance ₹10k, misc+buffer ₹25k) and V = ₹120 (SMS ₹45, WhatsApp ₹30, collection ₹10, marginal infra ₹20, support ₹15). Then:

- **Gross-margin floor**: 120 ÷ 0.2 = **₹600/mo** — even Starter-level pricing is healthy per-tenant. The floor doesn't bind.
- **Break-even** at ARPA ₹1,799: 3,00,000 ÷ 1,679 ≈ **179 dealers**. At ₹999: ≈ 342. At ₹2,499: ≈ 126.
- **Target earning** T = ₹2,00,000/mo profit at ARPA ₹1,799: (3L + 2L) ÷ 1,679 ≈ **298 dealers** — cross-check against `../company/13_REVENUE_GENERATION.md`'s 500-pumps-by-month-9–15 trajectory.

This is the conversation the model exists to force: _"Are we pricing for 130 dealers or 340?"_ — answer it with the sales capacity you actually have.

## Data-Gathering Checklist (one afternoon)

- [ ] Last 3 AWS bills → monthly average
- [ ] Last 3 MongoDB Atlas invoices → monthly average
- [ ] 2Factor dashboard: SMS sent last month ÷ active dealer tenants
- [ ] `logs` / Firebase: avg orders, OTP events, pushes per active dealer per month
- [ ] Payroll total incl. founder draw
- [ ] One-time list: Apple/Google fees, domain, SSL, misc SaaS subscriptions
- [ ] Easebuzz/UBI draft terms: per-debit or % cost of collecting our own subscription
- [ ] Support call/WhatsApp history: rough minutes per dealer per month
- [ ] Today's count of active dealer tenants (gives current C(N))
- [ ] CA fee, office actuals

## Rules & Cadence

1. Everything **ex-GST** (we claim input credit on our own costs; dealers claim it on our fee).
2. Recompute **quarterly**, and at every doubling of tenant count.
3. Re-run immediately when any unit rate moves >20% (WhatsApp/SMS rate cards do this).
4. When tiers go live, replace ARPA guesses with the real tier mix from billing data.

## Output → back to the pricing discussion

Carry three numbers into the price-point decision of [[10-pricing-metric-decision]]: **V** (per-tenant variable cost), **N_be** at each candidate price, and **N_target** for the profit the owners want. Combine with the premium-positioning anchors (Zoho ₹1,499, munim ₹12–25k) and the quoted-early-sales plan — that closes open question #1.
