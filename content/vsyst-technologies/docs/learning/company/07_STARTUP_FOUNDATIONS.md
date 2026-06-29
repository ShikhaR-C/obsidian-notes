# 07 — Startup Foundations: The 18-Domain Knowledge Map

## Framing

Before a first-time founder writes a pitch deck, sends a cold email, or commits a line of code, there is a body of knowledge to internalize. Tactics rot; fundamentals compound. This document maps the ~18 domains a founder building a B2B SaaS for Indian fuel distributors (or any low-ARPU, high-touch SME category) should be literate in, in a rough learning order.

The sequence matters. Customer discovery precedes pricing. Positioning precedes sales. Unit economics precedes fundraising. You cannot fix a broken MVP with a better pitch deck, and you cannot out-sell a product nobody wants.

Treat this as a knowledge map, not a curriculum. Each domain gets 2–4 sentences, one canonical source, and a single "do this next" action. India-specific sources are preferred where the domain has a local flavour (taxation, fundraising, ESOP, GST). Everything else draws from the global canon.

A prioritization pyramid closes the doc — the five domains you must master in months 1–3, before the rest.

---

## 1. Customer Discovery / The Mom Test / JTBD

Rob Fitzpatrick's core thesis: ask about past behaviour, not opinions or hypotheticals. The moment you describe your solution, the customer becomes a consultant and their feedback becomes noise. Pair this with the Jobs-to-be-Done lens — customers "hire" products to make progress on a specific job in specific circumstances.

For Indian fuel dealers, the burning jobs look like: reconciling daily DSR against bank settlement, tracking credit given to fleet customers, closing shift handover without leakage, and keeping GST filings clean. You will not learn any of this by pitching software.

- Read: [The Mom Test — Rob Fitzpatrick](https://www.momtestbook.com); [Looppanel customer interviews guide](https://www.looppanel.com/blog/customer-interviews)
- Do: 20 recorded interviews before any code.

## 2. Problem / Solution Fit and Product-Market Fit

Sean Ellis's 40% test: ask existing users "how would you feel if you could no longer use this product?" If ≥40% say "very disappointed," you have early PMF signal. Rahul Vohra operationalised the survey at Superhuman, systematically moving their score from 22% to 58% over two quarters by doubling down on the "very disappointed" segment.

Pre-PMF, everything is a leading indicator — retention curves, organic referrals, WTP, NPS movement. Post-PMF, growth becomes the lagging indicator.

- Read: [First Round Review — Superhuman PMF Engine](https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/); [Sean Ellis on Medium](https://medium.com/growthhackers/using-product-market-fit-to-drive-sustainable-growth-58e9124ee8db)
- Do: Run the Sean Ellis survey quarterly from day 30 onwards.

## 3. MVP Methodology / Lean Startup

Eric Ries's build-measure-learn loop reframes product work as scientific experimentation. Each release tests a hypothesis; the output is validated learning, not features. "Pivot or persevere" becomes a structured decision instead of a gut call.

The trap: optimising a product no one wants. More iterations of a bad MVP will not manufacture PMF. Identify the single leap-of-faith hypothesis (the assumption your entire business depends on) and design the cheapest possible test — often a WhatsApp concierge, a landing page, or a manual ops flow — before you build.

- Read: Eric Ries, *The Lean Startup*
- Do: Write down your one leap-of-faith hypothesis and design the cheapest test that can disprove it in 2 weeks.

## 4. Lean Canvas / Business Model Canvas

Ash Maurya adapted Alex Osterwalder's Business Model Canvas into the 9-box Lean Canvas — replacing "Key Partners" and "Key Activities" with "Problem" and "Solution" for startup realities. It is a single page that forces you to connect Problem → Customer Segment → Unique Value Proposition → Channels → Revenue in one coherent story.

Use it as a diagnostic, not a pitch asset. If any box feels weak, you have found your next research priority.

- Read: [Shortform on Lean Canvas](https://www.shortform.com/blog/ash-maurya-lean-canvas/); [Miro — Lean vs Business Model Canvas](https://miro.com/strategic-planning/lean-canvas-vs-business-model-canvas/)
- Do: Fill out the canvas in one hour, then walk 3 prospective customers through it for sanity check.

## 5. Unit Economics (CAC, LTV, Payback, Gross Margin, Rule of 40)

The 2026 B2B SaaS benchmarks any founder should know by heart: LTV:CAC ≥ 4:1, CAC payback < 12 months, Net Revenue Retention > 100%, annual gross churn < 3.5% for best-in-class, and Rule of 40 (growth % + FCF margin %) above 40%. Companies clearing Rule of 60 trade at 2–3× the valuation multiple of peers.

For low-ARPU Indian SME SaaS, the constraint is usually CAC payback — a ₹500–5,000/month ARPU means you cannot afford a ₹20,000 sales cost without a self-serve or referral-assisted motion.

- Read: [Phoenix Strategy — 2026 SaaS KPIs](https://www.phoenixstrategy.group/blog/benchmarking-saas-kpis-industry-standards-2026); [Abacum — Rule of 40 redefined](https://www.abacum.ai/blog/the-rule-of-40-redefined-framework-for-saas-finance); [Growthspree — LTV:CAC 2026](https://www.growthspreeofficial.com/blogs/b2b-saas-ltv-cac-ratio-guide-calculate-benchmark-improve-2026)
- Do: Calculate cohort unit economics every month from month 1 — even on a spreadsheet with 3 customers.

## 6. Pricing

Value-based pricing anchors to the economic benefit the buyer receives, not your cost or your competitor's list price. Cost-plus sets a floor; competitive pricing sets a ceiling; value sets your ambition. In SME India specifically, WTP is low but sticky — get the first price right and you can hold it for years.

Cross-link: see `02_PRICING_STRATEGY.md` for the DZZLO OMS-specific pricing model (SaaS tiers vs transaction-based vs embedded finance).

- Do: Quote three different prices to three similar prospects in week 1 of selling, then read the reaction before locking a sheet.

## 7. GTM: Inbound vs Outbound vs Product-Led

There is no single "right" GTM. Most mature B2B companies run a hybrid — product-led sales (PLS) — where a self-serve product surfaces qualified accounts to a human sales team. Pure PLG works only when self-serve value lands in under 10 minutes and the buyer is the user. Pure outbound works when ACV > ₹2L/yr and the buyer is a committee.

For Indian fuel dealers, outbound field sales dominates initial acquisition, but the product must retain without hand-holding — a hybrid GTM from day one.

- Read: [McKinsey — From PLG to PLS](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/from-product-led-growth-to-product-led-sales-beyond-the-plg-hype); [Lenny — GTM motions](https://www.lennysnewsletter.com/p/gtm-motions)
- Do: Run the Bullseye framework (see domain 11) to pick the 3 channels to test first.

## 8. Positioning (April Dunford)

Dunford's five components: (1) competitive alternatives the customer is actually weighing, (2) your unique attributes, (3) the value those attributes create — with proof, (4) the customers who care most about that value, and (5) the market category you choose to play in. Positioning is built bottom-up from your best customers, not top-down from market size decks.

For DZZLO OMS, the competitive alternative is often not another SaaS — it is Excel, a paper register, Tally, or the manager's memory.

- Read: [April Dunford site](https://www.aprildunford.com/); [Lenny — April Dunford summary](https://www.lennysnewsletter.com/p/summary-april-dunford-on-product)
- Do: Write a one-page positioning doc using the 5 components; test the one-line "what do we do?" on 10 prospects and count how many paraphrase it back correctly.

## 9. Branding & Narrative (StoryBrand)

Donald Miller's framework: the customer is the hero of the story, not your product. You are the guide (Gandalf, not Frodo). Clarify the problem they face, paint the picture of life after purchase, and give them a simple plan to get there. If the customer has to do cognitive work to understand why they should care, you lose.

- Read: Donald Miller, *Building a StoryBrand*
- Do: Rewrite your landing page headline in the format "We help [who] do [what] so that [outcome]" — no adjectives.

## 10. Sales Fundamentals (SPIN / MEDDIC / Challenger)

Three complementary methodologies, each solving a different sales problem. SPIN (Situation, Problem, Implication, Need-payoff) is a discovery questioning framework. MEDDIC (Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion) is an enterprise deal-qualification lens. Challenger teaches the rep to challenge the buyer's status quo through teaching, tailoring, and taking control.

Top-performing teams combine all three — SPIN for the first call, Challenger for differentiation, MEDDIC for forecasting.

- Read: [Gong — sales methodologies compared](https://www.gong.io/blog/sales-methodologies); [Sales Performance — SPIN vs Challenger vs MEDDIC](https://salesperformance.com.au/spin-challenger-meddic-comparison/)
- Do: Build a founder-led discovery script using the four SPIN question types before your next demo.

## 11. AARRR Pirate Metrics + Traction Bullseye

Dave McClure's AARRR — Acquisition, Activation, Retention, Referral, Revenue — is the minimum viable instrumentation for any product. Each stage has its own conversion rate, its own leaks, and its own optimisation levers.

Pair with Weinberg & Mares's Bullseye framework from *Traction*: brainstorm all 19 channels, rank into an outer (plausible), middle (promising) and inner (current focus) ring, and run cheap tests across the middle ring to find your one dominant channel.

- Read: [Amplitude — AARRR](https://amplitude.com/blog/pirate-metrics-framework); [PostHog — AARRR pirate funnel](https://posthog.com/product-engineers/aarrr-pirate-funnel); [99signals — Traction book](https://www.99signals.com/marketing-lessons-traction-weinberg-mares/); [Brian Balfour — Bullseye framework](https://brianbalfour.com/essays/traction-the-bullseye-framework)
- Do: Sketch the AARRR funnel on paper with your current numbers (even if most are zero) — the act of drawing reveals the next instrumentation gap.

## 12. Product Management (Marty Cagan + Teresa Torres)

Cagan's *Inspired* defines modern product work: empowered teams of a PM, designer, and engineer owning outcomes not outputs, running continuous discovery alongside delivery. Torres's *Continuous Discovery Habits* adds the mechanics — weekly customer touchpoints, opportunity-solution trees, and assumption tests built into the cadence.

For an early founder, you *are* the triad. The non-negotiable is the weekly customer conversation — not monthly, not "when we have time."

- Read: [SVPG — INSPIRED 2nd ed.](https://www.svpg.com/books/inspired-how-to-create-tech-products-customers-love-2nd-edition/); [Product Talk — Teresa Torres](https://www.producttalk.org/)
- Do: Book 3 customer touchpoints every week, starting this week. Put them on the calendar before planning features.

## 13. Design / UX for B2B India

UX conventions from SF-native SaaS (dense dashboards, keyboard shortcuts, hover menus) do not survive contact with an Indian petrol pump. Expect: multi-language UI (Hindi, Marathi, Gujarati, Tamil, Kannada as a starter set), intermittent 3G/4G bandwidth, small Android screens (often ₹8,000 devices), voice-first data entry, fat-finger-proof buttons, and the lowest possible typing burden.

Vyapar, Khatabook, and OkCredit are the benchmark — study their onboarding flows. Every unnecessary field is a churn driver.

- Do: Record yourself using your product on a 4-inch Android at 3G-throttled bandwidth. Fix the top 3 friction points before anything else.

## 14. Fundraising (India)

The Indian early-stage ecosystem as of Q1 2026 — Peak XV (ex-Sequoia India) led the league with 16 deals in the quarter, followed by Accel India at 13, then Blume, Z47 (formerly Matrix India), Together Fund, and Neon Fund for B2B SaaS. Common instruments at seed: SAFE, CCPS (Compulsorily Convertible Preference Shares — the Indian equivalent of preferred stock), and convertible notes. CCPS is standard for priced seed rounds; SAFEs are increasingly accepted but still less common than in the US.

For a low-ARPU SME product, many Indian SaaS companies bootstrap to ₹1–3 Cr ARR before raising — the market rewards capital efficiency.

- Read: [Inc42 — Top Indian investors Q1 2026](https://inc42.com/buzz/meet-the-top-10-indian-startup-investors-of-q1-2026/); [Shizune — SaaS investors India](https://shizune.co/investors/saas-investors-india)
- Do: Build a 30-name target list in a spreadsheet with thesis fit, cheque size, portfolio overlap, and warm-intro path for each.

## 15. Legal / Company Formation (India)

Incorporate as a Private Limited company (Pvt Ltd) — the only form most institutional investors will fund. Immediately apply for DPIIT (Department for Promotion of Industry and Internal Trade) Startup India recognition — free, done online, unlocks material benefits: a 3-year income tax holiday exercisable within the first 10 years, Section 56(2)(viib) angel tax exemption on share premium, IPR fast-tracking with an 80% patent fee rebate, and self-certification under 6 labour laws and 3 environmental laws.

Eligibility: entity less than 10 years old, turnover under ₹100 Cr in any year, working on innovation / improvement / scalability / employment generation.

- Read: [StartupIndia — DPIIT recognition](https://www.startupindia.gov.in/content/sih/en/startupgov/startup_recognition_page.html); [ClearTax — Startup India tax exemptions](https://cleartax.in/s/startup-india-tax-exemptions-eligibility)
- Do: File DPIIT the week you incorporate. Do not wait until "product is ready."

## 16. Accounting / Finance / Taxation (India)

GST registration is mandatory once turnover crosses ₹20 lakh (₹10 lakh in special category states — Arunachal, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura, Uttarakhand). B2B SaaS delivered to Indian buyers attracts 18% GST. Sales to foreign customers qualify as zero-rated export of services (with LUT filed). For cross-border digital services to non-business consumers, OIDAR (Online Information and Database Access or Retrieval) rules apply. TDS applies on payments to contractors (10% under 194J for professional services). Minimum Alternate Tax (MAT) at 15% applies unless you are inside the DPIIT tax holiday.

- Read: [ClearTax — GST for startups](https://cleartax.in/s/start-ups-benefit-under-gst); [India Briefing — GST SaaS compliance](https://www.india-briefing.com/news/gst-compliance-for-saas-and-cloud-computing-in-india-explained-39021.html/)
- Do: Onboard a CA with SaaS experience before you bill your first customer. Set up Zoho Books or Tally from day 1.

## 17. Hiring / ESOP / Team

The Indian standard ESOP grant: 4-year vesting, 1-year cliff — the 1-year cliff is effectively mandated by the Companies Act 2013, which requires a minimum 1-year vesting period before the first tranche vests. Create a seed-stage ESOP pool of 10–15% at incorporation, refreshed at each priced round.

Exercise price and taxation: ESOPs taxed at exercise (as perquisite) and again at sale (as capital gains). DPIIT-recognised startups can defer tax on exercise for up to 5 years from exercise — a meaningful cash-flow benefit for early employees.

- Read: [Qapita — ESOPs in India basic guide](https://www.qapita.com/in/blog/basic-guide-to-esops-in-india); [Treelife — vesting in India](https://treelife.in/legal/vesting-in-india/)
- Do: Set up a cap table (Qapita, Carta, or a clean Google Sheet) on day 1 with ESOP pool modelled.

## 18. Leadership & Founder Psychology

Ben Horowitz in *The Hard Thing About Hard Things*: "the toughest challenges of leadership aren't strategic; they're psychological." The cold sweats, sleepless nights, and imposter-syndrome spirals are not signs you are failing — they are the job. Paul Graham's research on YC founders consistently points to determination, not intelligence, as the top predictor of outcome. Michael Seibel's advice boils down to: ship, talk to users, ignore everyone else, and keep going longer than is reasonable.

You will be wrong about most things. The moat is staying in the game long enough to learn and correct.

- Read: [a16z — The Hard Thing About Hard Things](https://a16z.com/books/the-hard-thing-about-hard-things/); [Paul Graham essays](https://www.paulgraham.com/articles.html); [Michael Seibel — YC's essential startup advice](https://www.michaelseibel.com/blog/yc-s-essential-startup-advice)
- Do: Set up a monthly 1:1 with one other founder 1–2 stages ahead of you. Founder loneliness is a solvable problem; solve it early.

---

## The Prioritization Pyramid (Months 1–3)

You cannot learn 18 domains in a quarter, and you do not need to. Five dominate the outcome for a first-time founder in months 1–3. The rest can be learned as you hit them.

| Rank | Domain | Why it comes first |
|------|--------|-------------------|
| 1 | Customer Discovery / The Mom Test / JTBD (§1) | Every other decision — product, pricing, GTM, positioning — is downstream of whether you correctly understand the problem. Get this wrong and nothing else matters. |
| 2 | Unit Economics (§5) | Low-ARPU Indian SME SaaS fails on CAC payback, not product quality. If the math does not work at 10 customers, it does not work at 10,000. |
| 3 | Positioning (§8) | You will be asked "what do you do?" 50 times in month 1. A weak answer kills every conversation. Dunford's framework compresses weeks of struggle into days. |
| 4 | GTM / Sales Mechanics (§7 + §10) | You are the first AE. Founder-led sales through the first 10–20 customers is non-delegable. SPIN + Challenger are learnable in a weekend. |
| 5 | Founder Psychology (§18) | Everything above presumes you are still in the chair 12 months from now. The single highest-leverage investment is your own resilience. |

Everything else — Lean Canvas, fundraising, GST, ESOP, design, PM — is load-bearing but second-order. Learn them when you hit the corresponding moment: design when you sketch v0, fundraising when you start writing the deck, GST when you are about to cross ₹20 lakh.

The failure pattern is the opposite: founders spend months 1–3 on legal structure, pitch decks, and design systems while skipping discovery and unit economics. That is how you arrive at month 12 with a polished product nobody wants.

---

Sources → [RESEARCH_SOURCES.md](./RESEARCH_SOURCES.md)
