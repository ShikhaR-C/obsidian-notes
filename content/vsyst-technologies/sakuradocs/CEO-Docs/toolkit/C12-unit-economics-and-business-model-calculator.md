# C12 — Unit Economics and Business-Model Calculator

_Toolkit · fills the business-model and pricing exercises in [[06-strategy-ii-moats-positioning-and-the-business-model|06 — Strategy II: Moats, Positioning and the Business Model]] · Owner: CEO — nobody else may own the arithmetic that decides whether the company can exist · Cadence: rebuilt at every price change; the cost lines re-measured every quarter from real bills · Workbook tab: `Unit Economics` in [vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)._

## Purpose

A business model is not a diagram. It is four numbers, and this sheet computes them: **gross margin per paying customer**, **CAC payback in months**, **LTV on a gross-margin basis**, and **the number of paying firms at which the company stops needing anybody's permission to exist**. Everything else on the canvas — the value proposition, the channels, the key partners — is commentary on those four.

The format is the standard SaaS metrics stack ([For Entrepreneurs — SaaS Metrics 2.0](https://www.forentrepreneurs.com/saas-metrics-2/), 2013), pulled down to the size of a three-person, pre-revenue company in Raipur. Two disciplines are borrowed and enforced here. From a16z: CAC must be the _full_ cost of acquiring a customer, and LTV must never be computed on revenue — "a common mistake is to estimate the LTV as a present value of revenue … instead of calculating it as net profit" ([a16z — 16 Startup Metrics](https://a16z.com/16-startup-metrics/), 2015). From Paul Graham: the only question that matters before you have money in the bank is whether current revenue growth and current expenses get you to profitability on the cash you have left — **default alive or default dead** ([Paul Graham — Default Alive or Default Dead?](https://www.paulgraham.com/aord.html), 2015). That is why the last row of this sheet is a count of dealers, not a ratio.

The sheet exists mostly to stop you lying to yourself in a specific, predictable way. Founder-led sales feels free because the founder is not paid, so CAC looks like zero; support feels free because the CEO answers WhatsApp at 11 PM, so cost-to-serve looks like the AWS bill. Price both at a real loaded rate and the picture changes completely — usually for the worse, and usefully so. **Every rupee in this template is illustrative and every one of them is VERIFY LIVE** against your own bills, your own bank statement and your own close rate.

## When to use

- **First fill: before the first price is quoted to a dealer.** The per-GSTIN price decided in [[C11-pricing-and-packaging-decision-sheet|C11]] is an input here, and this sheet tells you whether that price survives contact with the cost of serving a fuel dealer who sends OTPs all day.
- **Re-measure the cost lines quarterly**, from actual AWS, Atlas, SMS and gateway invoices divided by actual active tenants — never from memory or from a vendor's calculator.
- **Re-run CAC after every ten closed or lost deals.** Close rate is the single most volatile input and the one founders round up.
- **Before any hire, any ad spend, any partnership that costs money** — the payback number is the test of whether the motion is worth scaling.
- **Feeds directly into** [[C13-runway-burn-and-scenario-planner|C13]] (revenue per firm, variable cost per firm) and into the raise story in [[C15-investor-narrative-and-deck-outline|C15]].

## How to fill (rules)

1. **Use list price, not the deal you actually did.** Discounts are a CAC problem, not a pricing problem. Price per GSTIN × GSTINs per firm = ARPA. VSYST bills per GSTIN with unlimited free users and web-only billing — that decision is settled ([[app-store-economics/README|App Store Economics]]); this sheet only tests whether it works.
2. **Cost to serve is measured, never estimated.** Total monthly bill ÷ active tenants, per vendor. AWS publishes no flat SaaS price — use your invoice and the [AWS Pricing Calculator](https://calculator.aws/) for forward estimates ([AWS — Pricing](https://aws.amazon.com/pricing/)). MongoDB Atlas dedicated clusters start at roughly **\$0.08/hour** and shared tiers well below that ([MongoDB — Pricing](https://www.mongodb.com/pricing)) — **VERIFY LIVE**, and re-check after every schema change, because per-tenant document growth is what actually moves this line.
3. **SMS/OTP is the line that scales with your customer's business, not with yours.** Driver OTPs and 10 PM–6 AM rate confirmations are per-transaction. A dealer doing three times the volume costs you three times as much and pays you the same. Model it per message, not per tenant. Push via Firebase Cloud Messaging is free on both the Spark and Blaze plans ([Firebase — Pricing](https://firebase.google.com/pricing)) — so push is the cheap channel and SMS is the expensive one, and that is a product decision as much as a cost one.
4. **Payment-gateway fees are a real subtraction from ARPA.** Easebuzz publishes no standard rate card and prices per merchant ([Easebuzz — Pricing](https://easebuzz.in/pricing/)) — so put your own signed rate in the cell and mark it **VERIFY LIVE** with the date of the agreement. Also remember GST on your own SaaS invoice is not margin: it is collected and remitted ([India Briefing — GST compliance for SaaS](https://www.india-briefing.com/news/gst-compliance-for-saas-and-cloud-computing-in-india-explained-39021.html/)).
5. **Price support minutes even when the founder does them free.** Support hours × a loaded hourly rate ÷ active tenants. This is the line that decides whether the business scales, and it is the only line that gets worse as you add non-technical dealers.
6. **CAC for a founder-led motion has one formula and you must use it:**
   `CAC = (founder days per deal × loaded founder day rate + travel & hospitality + collateral) ÷ close rate`
   Count travel to the district, the second and third visits, the demo device, the association fee and the dealer's tea. Loaded day rate = annual cost of that founder ÷ working days, **even if no salary is being drawn**. An unpaid founder-day is still the scarcest input the company owns.
7. **LTV is computed on gross margin, never on revenue.** `LTV = monthly gross margin per firm × expected lifetime`, where expected lifetime = 1 ÷ monthly logo churn. Revenue-based LTV is arithmetic that flatters you ([a16z — 16 Startup Metrics](https://a16z.com/16-startup-metrics/)).
8. **Below roughly 30 paying customers, LTV/CAC is noise — trust payback.** Churn measured on five dealers is not a churn rate, it is an anecdote, and lifetime = 1 ÷ churn magnifies that anecdote by fifty. **CAC payback in months is the number to run the company on**, because it needs only two inputs you can actually observe this quarter: what a deal cost you, and what a deal earns you per month. Skok's guidance is that the best SaaS businesses recover CAC in 5–7 months and that stretching past 12 makes profitability "anemic" ([For Entrepreneurs](https://www.forentrepreneurs.com/saas-metrics-2/)); Bessemer's benchmark data puts the average CAC payback at **15 months** for cloud companies between \$1–10M ARR, with **under 12 months** the expectation for SMB-focused businesses ([Bessemer — Scaling to \$100 Million](https://www.bvp.com/atlas/scaling-to-100-million)). VSYST sells to SMBs. Use 12. **VERIFY LIVE** — benchmarks drift.
9. **Gross margin below 60% is a red flag, not a rounding error.** Bessemer's cloud cohort averages **65–70%**, with the middle 50% between 60% and 80% ([Bessemer](https://www.bvp.com/atlas/scaling-to-100-million)). If DZZLO's margin sits under 60%, the cause will be SMS or support, not price — attack those first.
10. **End with a count of dealers, not a ratio.** `Paying firms to default alive = total monthly operating cost ÷ monthly gross margin per firm`. Write that number on the wall. It is the only number in this course that a three-person company can hold in its head.
11. **Date-stamp every input.** Each cell gets "last tested on". At pre-revenue every figure here is a hypothesis; an untested hypothesis older than one quarter is a lie with a spreadsheet around it.

## Template

**A. Revenue**

| Input                               | Value              | Unit  | How to get it honestly                                                                                                                                                                       |
| ----------------------------------- | ------------------ | ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Price per GSTIN per month           |                    | ₹     | List price from [[C11-pricing-and-packaging-decision-sheet\|C11]] — currently **₹1,799** (Growth tier, ex-GST), illustrative. C11 owns this number; never re-derive it here. **VERIFY LIVE** |
| GSTINs per paying firm              |                    | count | Actual average across signed dealers, not the aspiration                                                                                                                                     |
| **ARPA (monthly revenue per firm)** | `= price × GSTINs` | ₹     | Computed                                                                                                                                                                                     |
| Annual revenue per firm             | `= ARPA × 12`      | ₹     | Feeds [[C13-runway-burn-and-scenario-planner\|C13]]                                                                                                                                          |

**B. Cost to serve one dealer tenant, per month**

| Cost line                                         | ₹/tenant/month           | Basis                                 | Note                                         |
| ------------------------------------------------- | ------------------------ | ------------------------------------- | -------------------------------------------- |
| AWS compute + storage + bandwidth                 |                          | total AWS ÷ active tenants            | Falls with scale; re-measure quarterly       |
| MongoDB Atlas                                     |                          | cluster cost ÷ active tenants         | Watch per-tenant document growth             |
| SMS / OTP (2Factor) — driver + rate confirmations |                          | messages × rate                       | Scales with the dealer's transaction volume  |
| Push notifications (Firebase FCM)                 |                          | flat                                  | Free on Spark and Blaze                      |
| Payment-gateway fee on subscription collection    |                          | % of ARPA                             | Your signed Easebuzz rate — **VERIFY LIVE**  |
| Support (human minutes)                           |                          | support hours × loaded cost ÷ tenants | The line that decides scalability            |
| Onboarding, amortised over 24 months              |                          | onboarding cost ÷ 24                  | Or put it in CAC — be consistent, never both |
| **Total cost to serve**                           | `= sum`                  | ₹                                     |                                              |
| **Gross margin per firm per month**               | `= ARPA − cost to serve` | ₹                                     |                                              |
| **Gross margin %**                                | `= GM ÷ ARPA`            | %                                     | Target ≥ 70%; below 60% = investigate        |

**C. Cost to acquire one dealer (founder-led, district by district)**

| Input                                                                       | Value                                                | Unit  |
| --------------------------------------------------------------------------- | ---------------------------------------------------- | ----- |
| Founder days per closed deal (incl. travel, demos, follow-ups, paperwork)   |                                                      | days  |
| Loaded cost of a founder day                                                |                                                      | ₹     |
| Travel + hospitality per deal                                               |                                                      | ₹     |
| Marketing / collateral per deal                                             |                                                      | ₹     |
| Close rate (deals closed ÷ qualified conversations, over 20+ conversations) |                                                      | ratio |
| **CAC per closed dealer**                                                   | `= (days × rate + travel + collateral) ÷ close rate` | ₹     |

**D. The four numbers that decide the business**

| Metric                            | Formula                                     | Target | Reading                                                                   |
| --------------------------------- | ------------------------------------------- | ------ | ------------------------------------------------------------------------- |
| Gross margin %                    | `GM ÷ ARPA`                                 | ≥ 70%  | Below target → attack SMS and support before price                        |
| **CAC payback (months)**          | `CAC ÷ monthly GM`                          | ≤ 12   | **The number to trust.** Over 24 means the motion is wrong, not the price |
| LTV (gross-margin basis)          | `monthly GM ÷ monthly churn`                | —      | Gross margin, never revenue                                               |
| LTV ÷ CAC                         | `LTV ÷ CAC`                                 | ≥ 3    | **Noise below ~30 customers.** Report it, do not steer by it              |
| **Paying firms to default alive** | `total monthly operating cost ÷ monthly GM` | —      | Write it on the wall                                                      |

## Worked example — VSYST (illustrative)

**Pass one — the honest, unflattering version.** Price **₹1,799** per GSTIN per month — the Growth-tier list price, taken from [[C11-pricing-and-packaging-decision-sheet|C11]] and not invented here; 1.3 GSTINs per firm → ARPA **₹2,339/month** (₹2,338.70 before rounding), **₹28,065/year**. Cost to serve: AWS ₹120 + Atlas ₹90 + SMS/OTP ₹210 + Firebase ₹15 + gateway ₹40 (1.7% of ARPA) + support ₹400 + amortised onboarding ₹250 = **₹1,125**. Gross margin **₹1,214/month = 51.9%** — _below_ the bottom of Bessemer's 60–80% middle band, which is rule 9 firing, and rule 9 also says where to look: support plus SMS are **54%** of the cost stack and neither of them is a server.

CAC: 6 founder days × ₹4,000 loaded + ₹3,500 travel + ₹500 collateral = ₹28,000 per _closed_ attempt; at a 20% close rate, **CAC = ₹1,40,000**. Payback = 1,40,000 ÷ 1,214 = **115 months**. At 2% monthly churn, lifetime 50 months, LTV = ₹60,700, LTV/CAC = **0.43** — and with fewer than 30 customers that 0.43 is not a measurement, it is a rumour. The number that is real is 115 months. **At these inputs DZZLO does not have a business model; it has a hobby with servers.** Default-alive count at ₹1,50,000 monthly operating cost: 1,50,000 ÷ 1,214 = **124 paying firms**.

**Pass two — what the arithmetic tells you to change.** Nothing above says "raise the price". It says the acquisition motion and two cost lines are wrong.

- Sell to a dealers' association meeting instead of one pump at a time: founder days per deal fall to 2, travel per deal to ₹1,500, collateral ₹300, close rate rises to 35% because the room pre-qualifies itself. CAC = (2 × 4,000 + 1,500 + 300) ÷ 0.35 = **₹28,000** — five times cheaper, and the change was in the channel, not the price ([[C10-founder-led-sales-pipeline-and-script|C10]]).
- Move rate confirmations from SMS to push (FCM is free) and keep SMS only for driver OTP where a phone may be offline: SMS ₹210 → ₹90. Cut support ₹400 → ₹200 by fixing the three tickets that generate 60% of the volume ([[T25-customer-support-sop|COO T25]]).
- New cost to serve **₹805**, gross margin **₹1,534 = 65.6%** — back inside Bessemer's band and on its 65–70% average, though still under the 70% target. Payback = 28,000 ÷ 1,534 = **18.3 months**: a channel change and two cost lines removed **97 of the 115 months** and cleared the 24-month line where the motion itself is wrong, without reaching the under-12 SMB expectation. The remaining gap closes the same way it opened — support minutes and SMS — not with a higher price. Default alive falls to 1,50,000 ÷ 1,534 = **98 firms**.

Ninety-eight dealers, in a country with more than a lakh of retail outlets ([PPAC — retail outlets](https://ppac.gov.in/infrastructure/retail-outlets)), is a number three people can name districts against. That is the whole point of the sheet: it converted "are we a business?" into "which ninety-eight dealers, and by when?" — a question [[C13-runway-burn-and-scenario-planner|C13]] can schedule. All figures illustrative; **VERIFY LIVE** every one against real invoices before a single decision turns on them.

## Common mistakes

| Mistake                                               | Why it happens                               | The fix                                                                                        |
| ----------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| CAC excludes founder time                             | Nobody is drawing a salary, so it feels free | Loaded day rate on every founder day, always                                                   |
| CAC computed on closed deals only                     | Losses are invisible in the accounting       | Divide by close rate — you paid for the losses too                                             |
| LTV on revenue                                        | It is the bigger, nicer number               | Gross margin only; a16z is explicit                                                            |
| Steering by LTV/CAC at eight customers                | It looks like a real metric                  | Below ~30 customers, steer on payback                                                          |
| Onboarding cost counted in both CAC and cost-to-serve | Two sheets, two authors                      | Pick one. Write which, at the top of the tab                                                   |
| Cost-to-serve taken from a vendor pricing page        | Faster than opening the invoice              | Actual bill ÷ actual active tenants                                                            |
| GST treated as revenue                                | It arrives in the same bank credit           | It is collected and remitted, not earned                                                       |
| Benchmarks quoted without a date                      | They were true when you read them            | Every benchmark carries **VERIFY LIVE** and a year                                             |
| The sheet is built once and never re-measured         | It stops being fun once it is honest         | Quarterly re-measure is a calendar item in [[C27-ceo-weekly-template-and-calendar-audit\|C27]] |

## Related

Lessons [[06-strategy-ii-moats-positioning-and-the-business-model|06]], [[07-customers-markets-and-founder-led-sales|07]], [[08-capital-runway-and-fundraising|08]], [[17-the-numbers-a-ceo-watches|17]] · Templates [[C11-pricing-and-packaging-decision-sheet|C11]], [[C13-runway-burn-and-scenario-planner|C13]], [[C10-founder-led-sales-pipeline-and-script|C10]], [[C06-market-map-sizing-and-segments|C06]], [[C15-investor-narrative-and-deck-outline|C15]] · COO [[T05-kpi-scorecard|T05]], [[T20-budget-vs-actual-and-cash-forecast|T20]] · [[finance/09-phase-9-business-and-financial-model|Finance Phase 9]] · [[CEO-Docs/toolkit/index|CEO Toolkit]]
