# 09 — Product vs Sales: The Wrong Question, Reframed

## The Wrong Framing

Most first-time founders ask a version of "should I lead with product or sales?" The question is wrong. It assumes product and sales are substitutes, when in practice they are independent axes, and the real strategic decision sits on a different axis entirely: **problem-first vs distribution-first**.

Four quotes anchor the reframe.

Paul Graham: "**Make something people want.**" The primary determinant of outcomes is whether you have found a real, painful, frequent, expensive problem. No amount of product polish or sales motion compensates for its absence.

Peter Thiel, in *Zero to One*: "**Superior sales and distribution by itself can create a monopoly, even with no product differentiation. The converse is not true.**" Distribution is a first-class strategic asset, not a tax on a good product. Founders systematically underweight it because engineers find distribution distasteful.

Andy Rachleff (founder of Benchmark Capital): "**When a great team meets a lousy market, the market wins. When a lousy team meets a great market, the market wins. When a great team meets a great market, something special happens.**" The market — the problem and the people who have it — dominates everything you control.

Naval Ravikant on permissionless leverage: **code and media are the leverage of the new rich** — they scale without gatekeepers. But leverage only compounds when pointed at something people actually want to pay for. Leverage applied to a bad problem produces faster failure, not success.

With those four anchors, the right question is no longer "product or sales?" It is: (1) have you found a real problem, and (2) have you designed distribution into the product from day one?

---

## Arguments for Product-Led (PLG)

The archetype: Figma, Notion, Slack, Dropbox, Loom, Calendly. Free tier or frictionless trial → individual user experiences value → viral spread inside the organisation → enterprise expansion via a seat-based or usage-based pricing flywheel ([Growth Ahoy — PLG vs PLS vs SLG](https://www.growthahoy.com/blog/plg-pls-or-sales-led-what-growth-strategy-fits-your-saas)).

- **Low CAC** — the product does the marketing; you pay for infrastructure, not AEs.
- **Product as marketing** — every user is a micro-demo, every shared artefact is a billboard.
- **Requires self-serve value in under 10 minutes** — if the first session does not produce a tangible "aha," PLG breaks.
- **Needs a horizontal, universal use case** — documents, chats, designs, signatures. If the workflow is vertical-specific or requires configuration, self-serve collapses.
- **Buyer = user** — PLG fails when the person who pays is not the person who derives value.

## Arguments for Sales-Led (SLG)

The archetype: Salesforce in its early years, Palantir, Workday, Oracle, most Indian enterprise SaaS (Zoho Enterprise, Freshworks in its early enterprise motion). Long sales cycles, multi-stakeholder buying committees, custom onboarding, annual contracts with procurement friction.

- **Works when ACV > $50k** (roughly ₹40–50L/yr in India) — the economics support a human AE with quota.
- **Customization is expected** — integrations, SSO, custom fields, white-label, on-prem or private cloud.
- **Relationships and trust gate the deal** — in Indian enterprise and SME, the OMC or dealer association reference often matters more than the feature list.
- **Complex, high-stakes workflows** — finance, compliance, regulated data, mission-critical operations.
- [SandsDX — Product-Led vs Sales-Led](https://sandsdx.com/perspectives/executive/product-led-vs-sales-led/)

## McKinsey's 2024–2026 Verdict

McKinsey's cross-industry research is explicit: "**product-led motions exist on a broad spectrum.**" Pure SLG is increasingly rare in mature B2B. Pure PLG is also rare once companies cross ~$30M ARR and start chasing enterprise accounts. The dominant pattern is **hybrid — product-led sales (PLS)** — where a self-serve product surfaces high-intent accounts, and a human sales team converts and expands them ([McKinsey — From PLG to PLS](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/from-product-led-growth-to-product-led-sales-beyond-the-plg-hype)).

The McKinsey implication for a founder: do not frame the choice as a binary. Frame it as a sequence and a blend. Which motion dominates in year 1, and which auxiliary motion do you layer on by year 2?

---

## What Actually Applies to Indian SME Fuel Dealers

The customer profile for DZZLO OMS is specific and dictates the answer.

**Digital maturity:** low to medium. Tally export is still the gold standard for many dealers. WhatsApp is the default interface. Email is often a dumping ground, not a workflow tool.

**Decision mechanics:** relationship-driven. The owner will sign a contract after a demo in their office, over chai, or at a dealer association event. Cold sign-ups off a landing page are vanishingly rare in this segment.

**Ticket size:** small-to-medium monthly spend — realistically ₹500–5,000/outlet/month for a pure SaaS subscription, extending higher if embedded finance or transaction fees are included.

**Willingness to learn without hand-holding:** low. A dealer will not watch a tutorial video. They expect a human to sit with them for the first 2–3 sessions.

**Verdict: sales-assisted, problem-first.** Pure PLG will not work for this segment in 2026. You need a field or inside sales motion that demos over Zoom / WhatsApp video and closes in the first or second meeting. **But** — and this is where most Indian SME SaaS founders go wrong — the product must still deliver a 5-minute "aha moment" in the first session and retain daily without hand-holding. Otherwise your CAC scales linearly with headcount, and the economics break.

The operating model is **sales-led onboarding, product-led retention**. The sales rep gets the first transaction. The product gets the second, third, and 365th. If the product cannot stand on its own after onboarding, you are running a services business disguised as SaaS.

---

## Decision Framework

| Signal | Product-Led | Sales-Led |
|--------|------------|-----------|
| ACV | < ₹50k / yr | > ₹2L / yr |
| Buyer | Individual, self-serve | Committee, RFP, procurement |
| Time-to-value | < 10 minutes | Weeks |
| Digital maturity of buyer | High | Low |
| Integrations required | Minimal (standalone value) | Heavy (SSO, ERP, custom) |
| Workflow complexity | Horizontal, universal | Vertical, regulated, bespoke |
| Sales cycle | Days | Months |
| Customer success model | Self-serve docs + community | CSM, field engineer |
| **India fuel OMS reality** | Dealer checks WhatsApp first — self-serve does not start the conversation | Owner signs after an in-person or video demo |

Read the table as a diagnostic, not a verdict. Most businesses live between the two columns — the exercise is to identify which row dominates your segment, then design around it.

---

## The Indian SME SaaS Pattern

India's successful SME SaaS cohort — Khatabook, Vyapar, OkCredit, Dukaan, MyBillBook — did not win with PLG in the classical sense. They won with what is better described as **distribution-first + single-player product** ([Strategy Boffins — MyBillBook vs OkCredit vs Khatabook](https://www.strategyboffins.com/start_up_strategy/mybillbook-vs-okcredit-vs-khatabook/)).

The pattern has three components:

1. **Viral WhatsApp / SMS distribution.** When the shopkeeper sends a reminder to a customer, the message carries a signed link that drives customer downloads. Distribution is baked into the core workflow, not bolted on.
2. **Single-player value.** The product delivers utility even if the other party never joins — one shopkeeper can use Khatabook standalone, while any network effect is gravy.
3. **Adjacent financial services for monetization.** The ledger app is free or nearly free; the monetization is payments, credit, insurance, or supply chain finance layered on top of the transactional base.

DZZLO OMS should study this pattern carefully. A pure ₹2,000/month SaaS for fuel dealers faces the same low-WTP dynamics that forced Khatabook and OkCredit into embedded finance. The product must deliver standalone utility, but the monetization may end up on an adjacent axis — fuel financing, OMC receivables, fleet payment capture — not on the subscription line alone.

---

## The Real Sequence (Definitive)

There is a correct order of operations, and it is not "pick product or sales."

1. **Problem-first.** (Graham, Rachleff.) Find a painful, frequent, expensive problem in a specific segment. Everything else is downstream. Without this, nothing works.
2. **Distribution-first thinking.** (Thiel, Naval.) Design the product so at least one scalable channel naturally grows it — viral loop, referral mechanic, community-led adoption, or a clear low-CAC outbound motion. If no distribution hypothesis survives a whiteboard session, the business model is broken and more features will not fix it.
3. **Sales or product as the mechanism.** Match the buyer psychology of the segment. SLG for high-trust, high-ACV, committee-driven, low-digital-maturity buyers. PLG for individual, self-serve, horizontal, digitally-native buyers. Hybrid for the middle, which is most of modern B2B.

For DZZLO OMS and the petrol pump owner specifically: sales-assisted, field-rep-led onboarding, product-led daily retention, with distribution baked in through dealer association partnerships, OMC-adjacent referrals, and regional language WhatsApp outreach.

---

## Common Failure Modes

These are the patterns that kill first-time B2B founders. Name them now so you can catch yourself mid-fall.

- **"Build it and they will come."** No distribution plan → zero traction at launch → 6 months of "we just need more features" → runway exhaustion. The most common failure. Fixable only by doing distribution work *before* the next sprint.
- **Hiring an AE before repeatable process.** You hire the rep "to get sales moving." The rep asks what the script is, what the ICP is, what the objection handling is — and you do not have answers, because you have not sold enough yourself. The rep churns in 4 months. Do not hire an AE before 10–20 founder-led closes.
- **Running 100% sales with a complex product.** Every close requires 8 demos. Every renewal requires a CSM. Headcount scales linearly with revenue. Gross margins collapse below 60%. The business looks like services with a software wrapper. Either simplify the product or raise ACV.
- **Running 100% PLG with enterprise ACVs.** Buyers qualified for ₹20L/yr deals sign up, hit the self-serve ceiling, and quietly bounce because nobody from your side called them. Leaving money on the table. Layer in sales on signals of enterprise intent — domain, seat count, usage pattern.
- **Assuming India = US with lower prices.** Building for India on US UX assumptions. No regional languages, no offline-tolerant flows, no WhatsApp integration. The product looks beautiful in Figma and fails in a Nashik petrol pump.
- **Confusing activity with progress.** Running weekly sprints, closing tickets, shipping features — while the top-of-funnel numbers do not move. Measurable outcome per week, or the week was wasted.

---

## Founder Actions This Week

Close the doc with action, not reflection.

1. **Write your distribution plan before writing more code.** One page. Top 3 channels, expected CAC for each, why this segment responds to this channel. If you cannot fill the page, stop shipping features until you can.
2. **Rank 3 channels by estimated CAC.** Cross-reference with `12_OWNER_ACQUISITION.md` (DZZLO OMS–specific channel math). Pick the cheapest channel that also has a credible scaling path, not just the cheapest.
3. **Decide the minimum viable sales motion.** Months 0–9: founder-led sales, every close. Months 9–12: hire the first AE only after you have a script, an ICP, an objection-handling doc, and 10 repeatable closes to hand over. Earlier than that and you are hiring someone to figure out a process that does not exist yet.

---

## Further Reading

- Peter Thiel, *Zero to One* — the distribution chapter is the single best essay on this subject.
- April Dunford, *Obviously Awesome* — positioning is the prerequisite for any GTM choice.
- Geoffrey Moore, *Crossing the Chasm* — why the early adopter motion cannot be cloned to the mainstream.
- Bob Moesta, *Demand-Side Sales 101* — JTBD applied to sales conversations, particularly useful for SME India.
- [McKinsey — From PLG to PLS](https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights/from-product-led-growth-to-product-led-sales-beyond-the-plg-hype)
- [Growth Ahoy — PLG vs PLS vs SLG](https://www.growthahoy.com/blog/plg-pls-or-sales-led-what-growth-strategy-fits-your-saas)
- [SandsDX — Product-Led vs Sales-Led](https://sandsdx.com/perspectives/executive/product-led-vs-sales-led/)
- [Strategy Boffins — MyBillBook vs OkCredit vs Khatabook](https://www.strategyboffins.com/start_up_strategy/mybillbook-vs-okcredit-vs-khatabook/)
- [KrASIA — Khatabook $60M raise](https://kr-asia.com/indian-digital-ledger-startup-khatabook-raises-usd-60-million-from-b-capital-group)

---

Sources → [RESEARCH_SOURCES.md](./RESEARCH_SOURCES.md)
