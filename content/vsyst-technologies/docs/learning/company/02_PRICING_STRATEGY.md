# 02 — Pricing Strategy

A founder's reference for pricing DZZLO OMS in the Indian fuel-retail SMB market. This document covers the mental model, research methods, tier design, India-specific pricing reality, feature gating, and social-proof placement, and ends with a concrete recommended tier structure.

Pricing is the single highest-leverage lever a SaaS founder controls: McKinsey's work (cited in [NxCode's pricing benchmark](https://www.nxcode.dev/saas-pricing-benchmarks-2025)) finds that **a 1% improvement in price realisation translates to an 11–15% lift in operating profit** — far more than equivalent moves in COGS, volume, or marketing efficiency. Treat this document as a living artifact; re-read before every major pricing decision.

---

## 1. Mental Model: WTP vs ATP, Value-Based vs Cost-Plus

Before you pick a number, separate two questions that founders routinely conflate:

- **Willingness-to-pay (WTP)** — what a dealer _would_ pay if he understood the value clearly and had no friction.
- **Ability-to-pay (ATP)** — what cash a dealer _can actually spare_ this month, given margins, receivables cycles, working capital, and existing SaaS spend.

For Indian fuel dealers these two diverge sharply. A typical pump generates ₹8–15 lakh/month in gross revenue but nets only ₹30k–₹80k in operating profit after OMC commissions and labour; recovering even ₹2–3 lakh of stuck credit/month has enormous WTP, yet ATP for software is anchored to Tally/Zoho bills (₹500–₹1,500/month range). Your tiers need to respect both.

**Cost-plus vs value-based.** [Monetizely's 2025 benchmarks](https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose) show **68% of high-growth SaaS companies use value-based pricing**, and cost-plus is now a minority pattern. Value-based means: anchor price to the economic outcome you create (credit recovered, reconciliation hours saved, OMC deviations caught), not to your cloud bill plus a margin. Cost-plus locks you to commoditised pricing; value-based is how you escape it.

The rest of this document assumes value-based pricing and focuses on how to _measure_ WTP credibly.

---

## 2. Research Methods Before You Set a Price

Never pick a price from inside the building. Four primary methods, each with different strengths:

### 2.1 Van Westendorp Price Sensitivity Meter

Four questions asked to target buyers:

1. At what price would this be **too expensive** to consider?
2. At what price would this be **expensive but you'd still consider** it?
3. At what price would this be **a bargain**?
4. At what price would it be **so cheap you'd question the quality**?

The intersections of the four curves produce an Optimal Price Point (OPP) and a Range of Acceptable Prices (RAP).

[OpenView/Monetizely research](https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose) finds that **62% of new-product launches find Van Westendorp more actionable** than alternatives, because it works even when the buyer has no reference price. Best for novel / zero-to-one products — which describes DZZLO's situation in a market where no SaaS-first fuel OMS has won yet.

### 2.2 Gabor-Granger Price Ladder

Test an ordered ladder of specific prices and measure demand at each. Produces a demand curve and a single "optimum revenue" price. Best for **established categories** where buyers already have a mental reference price, and when you want revenue-maximisation clarity rather than acceptability bounds. See the [Conjointly comparison](https://conjointly.com/blog/gabor-granger-or-van-westendorp/) for a clean walk-through.

### 2.3 Conjoint Analysis

Forces buyers to trade features against price across simulated product bundles. Produces part-worth utilities per feature and a proper demand model. Heaviest to run (n ≥ 200 typically) but the only method that properly informs _tier composition_ and _what to gate_.

### 2.4 Qualitative + Paid Pilots

The cheapest and often most truthful signal: put a price in front of 10 hand-picked buyers and see who actually wires money. Every unpaid "interested" is worth roughly 1/20th of a paid pilot.

### Recommendation for DZZLO

Run them in sequence:

1. **Van Westendorp first** with 60–80 target dealers across 2–3 states (North India heartland + one Southern state for regional validation). Aim for a spread of single-pump owner-operators and small chain operators (2–5 pumps).
2. **Gabor-Granger ladder** around the Van Westendorp optimum to sharpen the specific number (±15%).
3. **10 paid pilots** at the chosen price before locking public pricing. Paid pilots surface ATP friction that surveys miss.

Sources: [Conjointly](https://conjointly.com/blog/gabor-granger-or-van-westendorp/), [Monetizely](https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose), [Synoint](https://www.synoint.com/blog/2025-09-29-van-westendorp-vs-gabor-granger-two-approaches-to-price-sensitivity-testing/).

---

## 3. Tier Design Principles

### 3.1 The Three-Tier Rule

Three is the sweet spot. More tiers fragment the decision; two tiers remove the decoy effect. [Monetizely's "Decoy Effect"](https://www.getmonetizely.com/articles/decoy-effect-saas-pricing) analysis finds **60–70% of buyers choose the middle tier** when three tiers are presented with deliberate anchor-decoy architecture.

### 3.2 Anchor-Decoy Architecture

- **Starter** — the decoy. Deliberately underpowered on the dimensions that matter. Its job is to make the middle look obviously better, not to sell.
- **Growth** — the hero. 60–70% of conversions should land here. Price this at the Van Westendorp optimum.
- **Pro** — the anchor. High enough that Growth looks like a bargain by comparison. A well-placed anchor produces a **40% lift on middle-tier adoption** ([Monetizely Decoy](https://www.getmonetizely.com/articles/decoy-effect-saas-pricing)).

### 3.3 The 2–3x Jump Rule

Between each tier, price should jump by **2–3x**, not 1.5x or 5x. Smaller gaps make Pro look like "just a bit more" (erodes the anchor); larger gaps create a cliff that buyers refuse to step over. [Artisan Strategies' analysis of tier gap ratios](https://www.artisanstrategies.com/insights/saas-pricing-tier-gap) confirms this as the empirical sweet spot.

### 3.4 Annual Discount

Default the billing toggle to **annual** with a **15–20% discount**. [925studios' subscription-billing study](https://www.925studios.com/blog/annual-vs-monthly-subscription-conversion) shows this lifts annual plan adoption by **19%** vs an off-by-default toggle. Annual locks cash, reduces churn, and improves LTV materially for a market with seasonal revenue volatility.

### 3.5 Per-Seat vs Alternatives

[NxCode's 2025 benchmarks](https://www.nxcode.dev/saas-pricing-benchmarks-2025) show **67% of SaaS still use per-seat**, but **hybrid models are projected to reach 61% by 2026**. Per-seat has a specific problem for DZZLO — see Section 4.

---

## 4. Pricing Model Choice for DZZLO

Per-user pricing creates a well-known failure mode in **low-digital-maturity SMB segments**: buyers share logins to avoid paying per seat. Fuel dealers will absolutely do this — a pump owner, his son, the manager, and the counter clerk will all log in from one account unless the system forces otherwise, and _forcing otherwise_ (concurrent session limits, device lockouts) actively hurts adoption in a pen-and-paper-to-software transition.

**Recommended model: per-tenant flat pricing (per dealership) with usage caps.**

- One subscription per dealership (GSTIN-bound).
- Caps on the _usage dimensions that correlate with value_: transactions/month, WhatsApp sends, customer-app logins, branches.
- Users included generously (2 / 10 / unlimited across tiers) — remove login-sharing friction.

The **archetype is Basecamp's $349/month unlimited-users plan**: a single flat fee regardless of team size, with value captured on the work itself. Basecamp's model works precisely because it aligns price to the customer's mental model of "my company" rather than "each staff member".

For DZZLO, the equivalent is: price per dealership, gate on transactions and channels, never on seats.

---

## 5. Trial / Freemium Benchmarks (2026)

Before designing the free-to-paid funnel, calibrate against industry benchmarks:

| Mechanism                   | Median conversion | Top quartile | Notes                                                |
| --------------------------- | ----------------- | ------------ | ---------------------------------------------------- |
| Opt-in free trial (no card) | ~18%              | 35–45%       | Default for self-serve SaaS                          |
| Credit-card-required trial  | ~48%              | 60%+         | ~5x better than opt-in; filters non-buyers           |
| Freemium                    | 3–5%              | 8–12%        | Organic avg 2.6%; heavy top-of-funnel needed         |
| Reverse trial               | 4–12%             | —            | Only ~7% of SaaS use it; outperforms freemium on LTV |

Sources: [1Capture free-trial benchmarks 2025](https://www.1capture.io/blog/free-trial-conversion-benchmarks-2025), [ChartMogul SaaS Conversion Report](https://chartmogul.com/reports/saas-conversion-report/).

For DZZLO specifically, credit-card-required trials are culturally mismatched (Indian SMB buyers resist card pre-authorisation). The better analogue is a **14-day no-card trial followed by a reverse-trial downgrade to a severely limited free tier** — this surfaces real usage intent without forcing a payment method upfront. Reverse trial is also the pattern Notion, Linear and Loom use.

---

## 6. India-Specific Pricing Reality

You are not pricing in a vacuum. Indian SMB buyers have sharp reference prices:

| Product                 | Indian price                 | Role in the landscape              |
| ----------------------- | ---------------------------- | ---------------------------------- |
| Zoho Books Standard     | ₹899/mo ex-GST               | The default SMB accounting anchor  |
| Zoho Books Professional | ₹1,499/mo ex-GST             | The "serious SMB" anchor           |
| Vyapar Silver           | ~₹4,399/yr (~₹366/mo)        | Downmarket GST billing             |
| Tally Prime             | ₹18,000 perpetual + AMC      | The accounting incumbent           |
| PetroSoft India         | ₹15,000 one-time             | Legacy DOS-era POS                 |
| SOFTGUN                 | ~₹21,600/user via Techjockey | Fuel-specific SaaS, high seat cost |

Source for accounting: [Patron Accounting's Zoho Books India pricing breakdown](https://www.patronaccounting.com/blog/zoho-books-pricing-india-2026), [Vyapar pricing](https://vyaparapp.in/pricing).

### PPP and regional discounts

[Monetizely's PPP guide](https://www.getmonetizely.com/articles/purchasing-power-parity-pricing-saas) and [Dodo Payments' regional-pricing playbook](https://www.dodopayments.com/blog/regional-pricing-saas) both converge: **Indian list prices typically run at 15–40% of US list**, and **regional discount programs for India price at 40–60% off parent-market list**. Founders who price India at US parity get unit economics right on paper and zero conversions in practice.

### GST (critical)

- India's GST on SaaS is **18%** under SAC 998434. Sources: [Lemon Squeezy's Indian GST guide](https://www.lemonsqueezy.com/blog/indian-sales-tax-gst-saas), [India Briefing on GST compliance for SaaS](https://www.india-briefing.com/news/gst-compliance-for-saas-and-cloud-computing-in-india-explained-39021.html/).
- **Industry norm is to quote ex-GST.** Add "+ 18% GST" in small print.
- Every fuel dealer worth acquiring is GST-registered and claims Input Tax Credit on SaaS — they **actively prefer ex-GST quotes** because they pay the net number and recover the GST against output liability.
- Your invoice templates must carry GSTIN, SAC 998434, place of supply, and HSN-compliant formatting from day one.

---

## 7. Feature Gating Strategy

### 7.1 The Kano Model Applied

Sort every feature into one of four Kano categories:

| Kano category               | What it is                          | DZZLO examples                                                                             | Gating rule                           |
| --------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------- |
| **Table stakes / basic**    | Expected; absent = dead deal        | GST invoice, customer ledger, customer list, shift book, daily sales entry                 | **Never gate.** Available on Starter. |
| **Performance**             | More is better; linear satisfaction | Transactions/month, WhatsApp sends, user seats, branches                                   | **Usage-gate.** Quotas rise by tier.  |
| **Delighters / excitement** | Unexpected, wows when present       | WhatsApp automation, payment-reminder bots, deep analytics, dashboards, SMS branded sender | **Feature-gate** into Growth/Pro.     |
| **Game-changers**           | Category-redefining                 | Public API, multi-branch, OMC reconciliation, embedded lending                             | **Anchor tier.** Pro/Enterprise only. |

Sources: [Orb on feature gating](https://www.withorb.com/blog/feature-gating-saas), [Pace Pricing](https://www.pacepricing.com/post/feature-gating-strategy), [Demogo](https://demogo.com/blog/saas-feature-gating).

### 7.2 The Gate-Scale-Low, Gate-Power-High Principle

- **Low tiers** — gate _scale_ (volume caps). Keep the feature surface wide so Starter still "feels like the product", just with a ceiling.
- **High tiers** — gate _power_ (advanced features). Pro should feel like a categorically different product, not just more quota.

### 7.3 Avoid Punitive UX

Never show a locked button with a lock icon and "Upgrade to Pro" mid-flow. It poisons the trial. Better: surface upgrade prompts at **breakpoints** (hit quota, try to invite 11th user, etc.), explain the economic upside, and offer one-click upgrade.

---

## 8. Recommended DZZLO Tier Structure

|                     | **Starter** (decoy) | **Growth** (hero, 60–70% target) | **Pro** (anchor)       | **Enterprise** |
| ------------------- | ------------------- | -------------------------------- | ---------------------- | -------------- |
| Monthly             | ₹599                | ₹1,799                           | ₹4,999                 | Contact us     |
| Annual (~17% off)   | ₹499/mo (₹5,988/yr) | ₹1,499/mo (₹17,988/yr)           | ₹3,999/mo (₹47,988/yr) | custom         |
| Transactions/mo     | 500                 | 5,000                            | Unlimited              | Unlimited      |
| Customer app logins | 50                  | 500                              | Unlimited              | Unlimited      |
| WhatsApp sends/mo   | 200                 | 2,000                            | 10,000                 | custom         |
| Staff users         | 2                   | 10                               | Unlimited              | Unlimited      |
| Branches            | 1                   | 3                                | Unlimited              | Unlimited      |

All prices are ex-GST. +18% GST (SAC 998434) applies.

### Design reasoning

- **₹1,499/mo annual on Growth** deliberately matches **Zoho Books Professional**. Every Indian SME accountant recognises that number; landing on it removes a cognitive barrier and positions DZZLO as "the Zoho-priced fuel-native tool".
- **3x jumps** (₹599 → ₹1,799 → ₹4,999) sit cleanly inside the [Artisan Strategies 2–3x rule](https://www.artisanstrategies.com/insights/saas-pricing-tier-gap).
- **Starter at ₹599 with 500 transactions/month** is deliberately decoy-calibrated. A typical single-pump dealer does 300–500 _fuel sale_ transactions per day, let alone per month; Starter blows out within hours. It exists to anchor Growth, not to sustain real operations.
- **Pro at ₹4,999** anchors the page. Most of its value is categorical (unlimited + multi-branch + API), not quantitative.
- **Enterprise** is quote-based, target multi-location chains and OMC-led deals.

### What each tier is for

- **Starter** — single pump, curious owner, wants to test WhatsApp invoicing and GST compliance. Entry point, not destination.
- **Growth** — the real product for 60–70% of single/dual-pump dealers. Full feature set, reasonable caps.
- **Pro** — chain operators (3–10 pumps), OMC franchisees, power users needing analytics + API + multi-branch.
- **Enterprise** — OMC-led rollouts, >10 pumps, custom SLAs, dedicated CS.

### Alternative recommendation: the hybrid model

Consider a **hybrid pricing stack** instead of pure subscription:

1. **Low base subscription** (e.g. ₹499/mo across all tiers) to cover hosting + support economics.
2. **Transaction take-rate** of **0.3–0.5% of GMV** on payments/collections processed through the platform. Fuel dealers intuit this as a "payment fee", not a SaaS bill — ATP barrier is much lower.
3. **Embedded finance** — invoice discounting, credit lines — share **1.5–3%** of the financing economics.

This aligns revenue to customer outcome (they only pay meaningful amounts when they use the platform to make/save money) and is the only model that plausibly reaches ₹1 crore ARPA with a fuel dealer. See cross-reference to `10_AFFORDABILITY_PROBLEM.md` for the full economic case.

---

## 9. Social Proof Placement

[CXL's trust-signal research study](https://cxl.com/research-study/) ranks social-proof types by lift impact, roughly:

1. High-profile client logos
2. Photo-testimonials (face + name + company)
3. Press mentions
4. Usage statistics ("10,000 dealers trust DZZLO")
5. Integration logos

### Placement rules (where each type goes)

| Surface                                 | What belongs there                                                                      | Why                                                                                                                                                     |
| --------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hero**                                | One crisp stat ("Trusted by 500+ fuel dealers") OR a logo strip                         | First fold, 3-second attention.                                                                                                                         |
| **Pricing page, adjacent to each tier** | One testimonial per matching customer size                                              | [The Good's pricing-page research](https://thegood.com/insights/pricing-page-best-practices/) — tier-adjacent social proof lifts conversion materially. |
| **Checkout / signup**                   | Security badges + reassurance microcopy ("Cancel anytime", "No credit card")            | [Baymard's checkout research](https://baymard.com/research) — trust signals at payment step lift 15–30%.                                                |
| **Login screen**                        | Rotating dealer quotes in vernacular                                                    | Highest-return-on-pixel surface; most founders miss it. Returning users see positive reinforcement every day.                                           |
| **Below-fold landing**                  | Case-study snippets with outcome numbers ("Recovered ₹3.2L in stuck credit in 90 days") | Depth, not first-impression.                                                                                                                            |

### Quantity rule

[Baymard](https://baymard.com/research) finds **1–3 trust-signal types on a page produce ~+23% conversion**, but **7+ types produce −8%** (clutter, cognitive load). Pick the 2–3 strongest and remove everything else.

### Video vs text

[Shapo's 2026 testimonial report](https://shapo.io/blog/video-vs-text-testimonials-saas) finds **video testimonials drive 2.9x higher signup** than equivalent text on SaaS landing pages. For DZZLO, a 45-second vernacular video of a real dealer in his office beats ten paragraphs of copy.

### India-specific social proof

**G2 and Capterra badges carry limited weight for Indian SMB fuel dealers.** Those buyers don't read English SaaS review sites. What works instead:

- **Google Business Reviews** for your company entity.
- **Facebook / WhatsApp group endorsements** shared in dealer communities.
- **AIPDA (All India Petroleum Dealers Association) seal** or endorsement.
- **OMC Territory Manager** quotes / endorsements — a TM saying "I've recommended DZZLO to my dealers" converts better than any Gartner quadrant.
- Local language testimonials with district/state specificity ("Rampur's largest HPCL outlet…") build instant regional credibility.

Skip the G2/Capterra spend in year 1.

---

## 10. Pricing Page Design Patterns (2026)

From a synthesis of [HubSpot's pricing-page A/B history](https://www.hubspot.com/marketing-statistics), [Outgrow's interactive-content report](https://outgrow.co/blog/interactive-content-conversion-stats), and [InfluenceFlow's mobile-conversion study](https://influenceflow.com/mobile-saas-conversion-2026):

- **3 tiers, middle highlighted** with "Most Popular" banner.
- **Outcomes > features** in tier headers. "Recover stuck credit" beats "Automated reminders". HubSpot reports a **34% conversion lift** on outcome-led headers.
- **Collapsible full-comparison matrix** below the 3 cards. Keeps above-the-fold clean; power-buyers expand.
- **Annual / monthly toggle, default to annual.**
- **Tier-adjacent testimonial** for each tier.
- **ROI calculator** — [Outgrow](https://outgrow.co/blog/interactive-content-conversion-stats) finds interactive calculators convert at **40%+** vs **2–12%** for static landing pages. This is the single most undervalued element on an Indian SaaS pricing page.
- **FAQ below fold** — 8–12 questions, GST, refund, uptime, data ownership.
- **Mobile-first** — [InfluenceFlow](https://influenceflow.com/mobile-saas-conversion-2026) finds **58% of pricing-page traffic is mobile** in Indian SaaS, with **2.3x better conversion** when the page is genuinely mobile-designed (not responsive-retrofit).

### Exemplars to study

- **Linear** — tier minimalism, crisp copy.
- **Basecamp** — flat-price boldness.
- **Stripe** — usage-pricing clarity.
- **HubSpot** — outcome-led headers.
- **Intercom** — tier-adjacent testimonials.
- **Figma** — free-tier generosity + clear upgrade path.
- **Notion** — reverse-trial architecture.

---

## 11. Zero-to-One Social Proof for DZZLO

You have none of this on day one. Here's how to manufacture it legitimately:

- **"Founding Dealer" program.** Offer **10–20 discounted or free accounts** (6–12 months) to hand-selected dealers across 2–3 states, in exchange for: a **video testimonial** in vernacular, **logo/name rights**, **a post-launch written case study**, and **monthly feedback calls**. Mirrors SaaStr's design-partner playbook.
- **Dealer-association co-branding.** Approach AIPDA and state-level associations with a free pilot for their members + a co-branded landing page. Positions DZZLO as "the association's recommended tool".
- **Vernacular video testimonials per tier.** Three videos — one single-pump Starter/Growth dealer, one 3–5 pump Growth/Pro operator, one chain Enterprise-tier dealer — each in the local language. Place one adjacent to each tier card.
- **ROI calculator: "See how much credit you'd recover monthly"** — single highest-leverage element on the pricing page for skeptical SMB buyers. Inputs: monthly sales, estimated credit outstanding, average DSO. Output: monthly recovery estimate + DZZLO cost → payback period.
- **Skip G2/Capterra spend in year 1.** Spend on video production, AIPDA engagement, and TM-level OMC relationships instead.
- **Login-screen rotating quotes.** Implement a simple rotating-carousel component on the login screen cycling 6–10 real dealer quotes. Cheapest real estate in the product; most founders miss it.

---

## 12. Research Sequence for DZZLO Pre-Launch

Before locking public pricing, run this sequence:

1. **Van Westendorp survey** — 60–80 target dealers across 2–3 states. Use WhatsApp + phone interviews; aim for 60% completion.
2. **Gabor-Granger ladder** — around the Van Westendorp optimum (±15%), tested with 30–50 dealers.
3. **10 paid pilots** at the chosen price. If paid-pilot conversion > 40%, lock the price. If < 20%, pull the price band down or restructure the hybrid offer (Section 8).
4. **Lock public pricing** and freeze for 90 days post-launch (no discounting in the first 90 days — protects anchor integrity).

Iterate quarterly thereafter with usage + churn + win-loss data.

---

## Sources & Further Reading

For the full citation trail and links to every primary source cited above, see `RESEARCH_SOURCES.md` in this directory.

Key sources referenced in this document:

- [Conjointly: Gabor-Granger vs Van Westendorp](https://conjointly.com/blog/gabor-granger-or-van-westendorp/)
- [Monetizely: Van Westendorp vs Gabor-Granger for SaaS](https://www.getmonetizely.com/articles/van-westendorp-vs-gabor-granger-for-saas-which-pricing-methodology-to-choose)
- [Synoint: Price sensitivity testing comparison](https://www.synoint.com/blog/2025-09-29-van-westendorp-vs-gabor-granger-two-approaches-to-price-sensitivity-testing/)
- [Monetizely: Decoy Effect in SaaS pricing](https://www.getmonetizely.com/articles/decoy-effect-saas-pricing)
- [NxCode: SaaS pricing benchmarks 2025](https://www.nxcode.dev/saas-pricing-benchmarks-2025)
- [Artisan Strategies: tier gap ratios](https://www.artisanstrategies.com/insights/saas-pricing-tier-gap)
- [925studios: annual vs monthly subscription](https://www.925studios.com/blog/annual-vs-monthly-subscription-conversion)
- [1Capture: free-trial benchmarks 2025](https://www.1capture.io/blog/free-trial-conversion-benchmarks-2025)
- [ChartMogul: SaaS Conversion Report](https://chartmogul.com/reports/saas-conversion-report/)
- [Patron Accounting: Zoho Books India 2026](https://www.patronaccounting.com/blog/zoho-books-pricing-india-2026)
- [Vyapar pricing](https://vyaparapp.in/pricing)
- [Lemon Squeezy: Indian GST for SaaS](https://www.lemonsqueezy.com/blog/indian-sales-tax-gst-saas)
- [India Briefing: GST compliance for SaaS](https://www.india-briefing.com/news/gst-compliance-for-saas-and-cloud-computing-in-india-explained-39021.html/)
- [Monetizely: PPP pricing](https://www.getmonetizely.com/articles/purchasing-power-parity-pricing-saas)
- [Dodo Payments: regional pricing](https://www.dodopayments.com/blog/regional-pricing-saas)
- [Orb: feature gating in SaaS](https://www.withorb.com/blog/feature-gating-saas)
- [Pace Pricing](https://www.pacepricing.com/post/feature-gating-strategy)
- [Demogo: SaaS feature gating](https://demogo.com/blog/saas-feature-gating)
- [CXL research study on trust signals](https://cxl.com/research-study/)
- [Baymard research](https://baymard.com/research)
- [Shapo: video vs text testimonials](https://shapo.io/blog/video-vs-text-testimonials-saas)
- [Outgrow: interactive content stats](https://outgrow.co/blog/interactive-content-conversion-stats)
- [InfluenceFlow: mobile SaaS conversion](https://influenceflow.com/mobile-saas-conversion-2026)
- [The Good: pricing-page best practices](https://thegood.com/insights/pricing-page-best-practices/)
