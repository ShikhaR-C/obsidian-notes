# C11 — Pricing and Packaging Decision Sheet

_Toolkit · fills the pricing and packaging exercises in [[06-strategy-ii-moats-positioning-and-the-business-model|06 — Strategy II: Moats, Positioning and the Business Model]] · Owner: CEO — the only approver of any price, discount or tier boundary until there is a sales team · Cadence: reviewed quarterly; amended only by the procedure in §6 of the record · Workbook tab: prices feed `Unit Economics` in [vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)._

## Purpose

**This sheet does not decide the pricing metric. It records the one already decided, the reasoning behind it, and the procedure by which it may be changed.** DZZLO OMS bills **per GSTIN**; users are **unlimited and free**; billing is **web-only**, with the app gated server-side. That is settled ([[app-store-economics/README|App Store Economics]]; `docs/learning/app-store-economics/08-dzzlo-subscription-strategy.md`). What this document exists to prevent is the slow, unminuted erosion of that decision — the exception granted on a Tuesday call, the "just for this one group" seat price, the tier boundary that moved because a dealer pushed. Those are how a pricing model dies: never by a decision, always by drift.

A price is the highest-leverage number a founder controls. Marn and Rosiello's classic finding is that a 1% improvement in price realisation lifts operating profit by far more than the same move in volume or cost ([HBR — Managing Price, Gaining Profit](https://hbr.org/1992/09/managing-price-gaining-profit), 1992) — **VERIFY LIVE** the exact multiplier before quoting it, because the number is repeated at several different values. The corollary is uncomfortable: a 1% erosion works just as hard in the other direction, and erosion is what an unlogged discount is.

The format is a **decision record**, not a pricing worksheet. It borrows its shape from the architecture-decision-record discipline — context, decision, consequences, supersession — because the failure is the same one: a choice made carefully once, then quietly re-made by people who never saw the reasoning. Every field carries a version, a date, a decider and a minute reference, and a change to the _metric_ is a **one-way door** that goes to the board and to [[C29-decision-journal-and-one-way-door-log|C29]] before it goes to a customer. The research that _would_ reopen the price level — Van Westendorp with 60–80 dealers, a Gabor-Granger ladder, then ten paid pilots ([Monetizely — Van Westendorp vs Gabor-Granger](https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose)) — belongs in [[06-strategy-ii-moats-positioning-and-the-business-model|lesson 06]] §7 and [[company/02_PRICING_STRATEGY|the pricing strategy note]]. This sheet consumes its output; it does not run it.

## When to use

- **First fill: now, before the first dealer is quoted a number in writing.** A price quoted before it is recorded becomes the price, permanently, because the dealer will repeat it to the next dealer.
- **Before every quote that deviates from list** — the discount authority table in the template is the approval, and filling it _is_ the approval step.
- **Quarterly**, as a fifteen-minute review: did anything drift, what did discounts actually cost this quarter, has any reopen trigger fired.
- **Before any price increase**, using the §6 runbook — which is a 60–90 day process, not an email.
- **Feeds** [[C12-unit-economics-and-business-model-calculator|C12]] (list price is its first input), [[C10-founder-led-sales-pipeline-and-script|C10]] (the quote and the objection bank) and [[C15-investor-narrative-and-deck-outline|C15]] (the business-model slide).

## How to fill (rules)

1. **Record the metric and the metrics you rejected, with the reason for each.** The rejections are the valuable half. Future-you, under pressure from a dealer who wants to pay per user, needs to read _why_ that was already refused, not re-derive it at 9 PM.
2. **A GSTIN is countable, verifiable and stable; a seat is none of those.** The dealer's staff churn constantly — drivers, salesmen, the munim's nephew. Per-user pricing makes the dealer ration logins, and rationing logins destroys the exact behaviour the product needs: the driver taking the OTP, the salesman raising the order, the owner seeing the ledger. **Never charge for the thing you need the customer to do more of.**
3. **Per-transaction was rejected because it taxes the dealer's growth and makes VSYST's revenue swing with fuel prices.** It is also un-budgetable — an Indian SMB owner will not sign a bill he cannot predict — and it invites gaming (batching orders, raising invoices outside the system) that costs data integrity worth more than the fee.
4. **Where the metric is weak, the tiers do the work.** A 400 KL pump and a 60 KL pump both hold one GSTIN and would pay the same, which under-monetises the large one. That is fixed inside the tier by metering **outlets, active credit customers and monthly transactions** — units the dealer already uses to describe himself — not by inventing a second metric. Gate scale low, gate power high ([Orb — feature gating in SaaS](https://www.withorb.com/blog/feature-gating-saas)).
5. **Web-only billing is a margin decision with a number attached.** Apple's standard commission is 30%, reduced to 15% under the Small Business Program for developers under USD 1M in prior-year proceeds; Google Play charges 15% on auto-renewing subscriptions from day one, and India's CCI order permits third-party billing at a reduced rate ([SplitMetrics — Google Play and App Store fees](https://splitmetrics.com/blog/google-play-apple-app-store-fees/); [RevenueCat — the 15% App Store fee](https://www.revenuecat.com/blog/engineering/small-business-program)) — **VERIFY LIVE** all of these, they move with litigation and regulation. On a sales-assisted B2B product where no purchase ever originates in the app, paying any of it is a donation. Collect on the web through the gateway; gate entitlement server-side.
6. **Publish ex-GST and say the ITC sentence out loud.** SaaS in India attracts 18% GST under SAC 998434 ([Lemon Squeezy — Indian GST for SaaS](https://www.lemonsqueezy.com/blog/indian-sales-tax-gst-saas); [India Briefing](https://www.india-briefing.com/news/gst-compliance-for-saas-and-cloud-computing-in-india-explained-39021.html/)). Every dealer worth acquiring is GST-registered and reclaims it. Quoting inclusive of GST silently raises your price 18% in the buyer's head for no revenue.
7. **Set the annual prepay discount at two months free and never negotiate it.** The industry-standard annual discount is ~16.7%, framed as "twelve months for the price of ten", with the acceptable band 15–20% ([Monetizely — annual vs monthly pricing psychology](https://www.getmonetizely.com/articles/why-annual-vs-monthly-pricing-psychology-matters-for-saas-revenue-leaders); [InnerTrends — analysing 100 SaaS companies' yearly discounts](https://www.innertrends.com/blog/saas-pricing-strategies); [Heap — how much to discount prepaid contracts](https://www.heap.io/blog/how-much-should-i-discount-for-prepaid-saas-contracts)). A fixed, published number is a negotiation you never have to hold. For a pre-revenue company the cash matters more than the discount costs: twelve months collected in month one is the cheapest capital in [[C13-runway-burn-and-scenario-planner|C13]].
8. **Paid pilot, not free trial — and write down why.** Self-serve trial-to-paid medians sit around 8% overall, and B2B enterprise trials convert in the low-to-high teens ([ChartMogul — SaaS conversion report](https://chartmogul.com/reports/saas-conversion-report/); [Userpilot — free trial conversion benchmarks](https://userpilot.com/blog/saas-average-conversion-rate/)) — **VERIFY LIVE**, these benchmarks are restated annually. Those numbers describe products a stranger can adopt alone. DZZLO cannot be: it needs the customer ledger, the rate masters and the outstanding balances migrated before it does anything at all. An untended free trial produces an empty tenant and a dealer who has now "tried it and it didn't work". Worse, free extends the ₹0 anchor you are trying to break ([[06-strategy-ii-moats-positioning-and-the-business-model|lesson 06]] §7.1). A paid pilot with a fee, a scope, a start and end date and a written success criterion is the instrument.
9. **The floor price is a number, it is written down, and the CEO cannot go below it either.** Set it at the price where [[C12-unit-economics-and-business-model-calculator|C12]]'s CAC payback crosses 18 months. Below the floor you are not selling, you are buying logos with the founders' runway.
10. **Every discount buys something nameable and carries an end date.** Annual prepay, an association endorsement, a named case study with a vernacular video, a multi-GSTIN group, a founding-cohort commitment. "Founding price" with no end date is a permanent price cut you have not admitted to. Log it in the pipeline and, if it sets a precedent, in [[C29-decision-journal-and-one-way-door-log|C29]].
11. **Amend by version, never by edit.** A new list price creates v2 with a date and a supersession line; v1 stays readable. Metric changes additionally require a board minute ([[C17-board-pack-agenda-and-minutes|C17]]).

## Template

```
PRICING & PACKAGING DECISION RECORD — DZZLO OMS
Version v___ · decided <date> · decider CEO · minute ref ______ · supersedes v___
Next scheduled review: ______ (quarterly)
Change class: [ ] METRIC (one-way door — board + C29)  [ ] list price  [ ] tier boundary
              [ ] discount policy  [ ] term / billing  [ ] trial policy  [ ] floor price

1. THE VALUE METRIC — what one unit of "paying" means
   Metric ............. one GSTIN of the dealer company
   Users .............. unlimited, free, all roles (owner, munim, salesman, driver)
   Billing channel .... web only; entitlement enforced server-side; app never sells
   Currency / tax ..... ₹, quoted ex-GST; 18% GST added on the invoice (SAC 998434)
   REJECTED, and why:
     per user ......... <reason>          per transaction ... <reason>
     per outlet ....... <reason>          per KL / % of GMV . <reason>
   REOPEN TRIGGER (written before you need it):
     "<e.g. 3 of the next 10 lost deals cite the metric itself, not the price>"

2. TIERS — list price per GSTIN per month, ex-GST
   <tier name>  ₹____   outlets ___  credit customers ___  txns/month ___  includes ___
   ... (3 public tiers + 1 quoted tier; 2–3× gap between tiers)
   NEVER GATED AT ANY TIER: GST invoicing · the ledger · the order flow
   QUOTA BREACH BEHAVIOUR: nudge -> grace ___ days -> pause premium extras.
     It never blocks an order.  <— this line is not negotiable

3. TERM AND PREPAY
   Default term ______   Monthly ______   Annual prepay discount ____% (= __ months free)
   Multi-year ______   Auto-renew ______   Notice to cancel ______   Refund policy ______

4. TRIAL / PILOT POLICY
   Free trial: [ ] none  [ ] ___ days, credit-card/mandate required
   Paid pilot: fee ₹______ · scope ______ · duration ______ ·
     written success criterion ______ · credited against year 1? Y/N · converts on ______

5. DISCOUNT AUTHORITY  (see table below — this table IS the approval)
   FLOOR PRICE ₹______ per GSTIN per month. Nobody may go below it, including the CEO.

6. PRICE-CHANGE PROCEDURE  (see runbook below)

7. WHAT WOULD MAKE THIS DECISION WRONG
   <2–3 falsifiable statements, e.g. "if median dealer runs 2.4 GSTINs, per-GSTIN
    over-charges groups and we will need a group price">
```

**Metric decision table — keep this filled; it is what you read when a dealer pushes back**

| Candidate metric | Aligns with value?            | Predictable for the dealer? | Grows with him?         | Gameable?                     | Verdict                                     |
| ---------------- | ----------------------------- | --------------------------- | ----------------------- | ----------------------------- | ------------------------------------------- |
| **Per GSTIN**    | Partly — tiers carry the rest | Yes — he knows his GSTINs   | Yes — new firm, new fee | No — public on the GST portal | **Chosen**                                  |
| Per user / seat  | Weakly                        | Yes                         | Yes                     | Yes — shared logins           | Rejected — taxes adoption                   |
| Per transaction  | Yes                           | **No**                      | Too fast                | Yes — off-system invoices     | Rejected — un-budgetable                    |
| Per outlet       | Partly                        | Yes                         | Yes                     | Mildly                        | Rejected as _primary_; kept as a tier meter |
| % of fuel value  | Yes                           | No                          | Uncontrollably          | —                             | Rejected — you are not a broker             |

**Discount authority**

| Discount off list   | What it must buy                                                | Who approves              | Where it is logged                                            | Expiry                        |
| ------------------- | --------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------- | ----------------------------- |
| 0%                  | —                                                               | Nobody                    | Pipeline                                                      | —                             |
| Up to 16.7%         | Annual prepay only                                              | CEO (standing authority)  | Pipeline                                                      | With the term                 |
| 17–30%              | Named case study + vernacular video, or association endorsement | CEO, in writing, per deal | Pipeline + [[C29-decision-journal-and-one-way-door-log\|C29]] | Written end date, ≤ 24 months |
| 31%+ or below floor | Nothing. It is refused                                          | —                         | —                                                             | —                             |
| Free (₹0)           | Design partner, ≤ 3 tenants ever, contract says so              | CEO + one co-director     | [[C29-decision-journal-and-one-way-door-log\|C29]]            | Hard end date in the contract |

**Price-increase runbook (§6)**

| Day | Step                                                                                                                                           | Owner |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| −90 | Decide the new list price. New version of this record. Model churn cost in [[C13-runway-burn-and-scenario-planner\|C13]]                       | CEO   |
| −90 | Confirm nothing shipped badly this quarter — never raise in the same quarter as an outage or data incident                                     | CEO   |
| −75 | New price live for **new logos only**. Existing tenants untouched                                                                              | CEO   |
| −60 | Written notice to existing tenants, in Hindi and English, naming the date and what shipped since they joined                                   | CEO   |
| −30 | Reminder + the annual-prepay-at-old-price offer (this converts objection into cash)                                                            | CEO   |
| 0   | New price effective on renewal, not mid-term                                                                                                   | —     |
| +30 | Measure **logo churn and revenue churn separately** — in SMB they diverge ([Growigami](https://growigami.com/blog/saas-churn-rate-benchmarks)) | CEO   |

## Worked example — VSYST (illustrative)

**Version 1, recorded before the first quote. Every rupee below is illustrative and inherits the placeholder status of the tier sheet in [[06-strategy-ii-moats-positioning-and-the-business-model|lesson 06]] §7.3 — VERIFY LIVE against the cost model and the first ten paid pilots before any of it reaches a website.** Metric: one GSTIN. Users unlimited and free. Web-only billing. Quoted ex-GST.

Tiers, per GSTIN per month: **Starter ₹599** (1 outlet, ~25 active credit customers, 500 txns), **Growth ₹1,799** (up to 3 outlets, ~150 credit customers, 5,000 txns — the hero), **Pro ₹4,999** (unlimited, DIP module, priority support — the anchor), **Enterprise** quoted (multi-GSTIN group, API, OMC reconciliation, SLA). Three tiers with a deliberate anchor is the standard shape, and the 2–3× gap between them is the empirical band ([Monetizely — the decoy effect](https://www.getmonetizely.com/articles/decoy-effect-saas-pricing); [Artisan Strategies — tier gap ratios](https://www.artisanstrategies.com/insights/saas-pricing-tier-gap)). Growth at ₹1,499/month on annual prepay lands on a number every Indian SME accountant already recognises from Zoho Books.

Annual prepay: **16.7% — two months free**. ₹1,799 × 12 = ₹21,588 becomes **₹17,988 collected in month one**. Floor price: **₹1,200 per GSTIN per month**, set where C12's payback crosses 18 months at the current cost-to-serve. Nothing below it, ever.

Trial policy: **no free trial. Paid pilot only** — ₹9,000 for 60 days, fully credited against the first annual invoice, covering ledger migration for up to 40 credit customers and rate-master setup, with one written success criterion agreed on day zero (_"the November party ledger closes from DZZLO without the munim's parallel register"_). A dealer who will not pay ₹9,000 will not pay ₹21,588 either, and finding that out in week one is worth more than the ₹9,000.

Why per-GSTIN survived contact with the first objection: a three-pump dealer asked to pay for "just the office, two users". Per-user would have said yes and produced a tenant where the drivers never take OTPs, the ledger stays half-empty and the product visibly fails in ninety days. Per-GSTIN said: **one price, put everyone on it, that is how it works.** The dealer bought Growth for one GSTIN and added the second four months later. The rejection block in the record is what made that conversation two minutes long instead of a renegotiation.

Anchoring, recorded so it is said the same way every time: never compare DZZLO to software. Compare it to the munim (₹15,000–25,000/month), to one bad-debt write-off, to ten days of DSO on a ₹40 lakh receivable book. Lead with rate disputes and the DSO arithmetic, both of which the dealer supplies the inputs for. **Never lead with the shortage line** — it is the biggest number and the least believable.

## Common mistakes

| Mistake                                   | Why it happens                           | The fix                                                                                                  |
| ----------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Quoting a price before recording it       | The dealer asked, you answered           | Fill the record first. The first quote sets the market price in a district                               |
| Reopening the metric in a deal room       | One buyer pushes hard and is persuasive  | The metric changes only by board minute. Read him the rejection block                                    |
| "Founding price" with no end date         | It sounds generous and closes the deal   | Rule 10 — every discount carries a written expiry                                                        |
| Charging per user "just for this group"   | It looks like more revenue on one deal   | It is a second pricing model. Two models is no model                                                     |
| Free trial because "everyone offers one"  | Copying self-serve SaaS                  | Rule 8. Untended trials in a migration-heavy product produce empty tenants and lost dealers              |
| Selling through the app to "make it easy" | Nobody costed the commission             | 15–30% of every rupee, forever, on a product no one buys in-app                                          |
| A floor price the CEO overrides           | The CEO wrote it, so the CEO can move it | Then it was never a floor. Put the number in this record and in [[C03-decision-rights-matrix\|C03]]      |
| Raising prices by email, next month       | It feels decisive                        | 60–90 days, in writing, in his language, paired with something shipped                                   |
| Discounts nobody counts                   | Each one felt small                      | Quarterly review: total discount ₹ as a % of list. If it exceeds 10%, the price is wrong or the pitch is |
| Blocking orders to collect a subscription | It is the strongest lever available      | It ends the relationship and the district. Nudge, grace, pause extras — never block an order             |

## Related

Lessons [[06-strategy-ii-moats-positioning-and-the-business-model|06]] (§7 pricing against a ₹0 anchor — the reasoning behind this record), [[07-customers-markets-and-founder-led-sales|07]], [[17-the-numbers-a-ceo-watches|17]] · Templates [[C12-unit-economics-and-business-model-calculator|C12]] (does the price survive the cost of serving?), [[C10-founder-led-sales-pipeline-and-script|C10]], [[C08-positioning-and-messaging-canvas|C08]], [[C13-runway-burn-and-scenario-planner|C13]], [[C29-decision-journal-and-one-way-door-log|C29]], [[C03-decision-rights-matrix|C03]] · [[app-store-economics/README|App Store Economics]] · [[company/02_PRICING_STRATEGY|DZZLO Pricing Strategy]] · [[CEO-Docs/toolkit/index|CEO Toolkit]]
