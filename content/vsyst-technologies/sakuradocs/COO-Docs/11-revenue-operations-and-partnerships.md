# 11 — Revenue Operations and Partnerships

_Phase 3 · Build the Machine · Months 2–6. After this lesson you can name the six stages of DZZLO's sales pipeline and the exit criterion of each, run the CRM in ERPNext from lead to invoice, hold a 20-minute weekly pipeline review, collect what you invoice with a dunning ladder and a DSO number, operate pricing that is quoted but never published, run field sales in one district on visit logs, and track every partnership conversation with one owner and a written next step._

## 1. Revenue operations is a machine, not a hero

DZZLO is sold, not downloaded. The [[company/README|Company Playbook]]'s GTM verdict is blunt: this buyer is **sales-assisted, product-retained** — a fuel dealer will not self-serve through a website, and no amount of ads closes him without a human somewhere in the chain. The [[12_OWNER_ACQUISITION|owner-acquisition research]] goes further: the first 100 customers are founder-led, visited personally, and they are R&D, not revenue.

None of that is the COO's problem to change. The COO's problem is what founder-led selling always becomes without a mechanism: deals living in one person's head and WhatsApp scrollback, follow-ups that happen when someone remembers, quotes that differ from pump to pump because nobody wrote the last one down, invoices raised late and chased never, and three partner conversations that all feel "promising" and none of which has moved in six weeks.

**Revenue operations** (RevOps) is the machine around the selling: the pipeline with defined stages, the CRM where every deal lives, the weekly review that moves them, the quote-to-onboarding handoff, the invoicing-and-collections loop, the pricing rules, and the partnership tracker. The CEO and the domain-expert director will do most of the actual selling for the first year — your job is that **every conversation is recorded, every deal has a next step with a date, and every promise to invoice turns into cash**. Same law as everywhere in this course: good intentions don't work; mechanisms do.

One boundary to draw on day one: revenue _operations_ is not revenue _strategy_. Which segments, which district, which channel, what the product promises — that is the playbook and the CEO's call. You own that the chosen motion runs on rails and produces honest numbers.

## 2. The pipeline — six stages, each with an exit criterion

A **pipeline** is the list of every potential customer, sorted by how close they are to paying. Its entire value depends on one discipline: **a stage is a fact, not a feeling.** Each stage has an exit criterion — a checkable event — and a deal moves only when the event has happened. "He seemed interested" moves nothing.

DZZLO's sales-assisted motion has six stages:

| #   | Stage         | The deal enters when…                                                                                                                     | Exit criterion — moves on only when…                                                                                                                                                                                                                                           |
| --- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | **Lead**      | We identify a named dealer/owner with a phone number and record the **source** (referral, association, OMC contact, field visit, inbound) | A real two-way conversation has happened — a call answered, a WhatsApp reply, a visit where the owner talked. A broadcast message sent is not contact.                                                                                                                         |
| 2   | **Contacted** | That first two-way conversation exists                                                                                                    | A **demo is done** with the decision-maker present — at the pump, on our phone or browser (never demand an app install first — [[12_OWNER_ACQUISITION\|owner-acquisition research]]), and the owner's actual pain (stock variance, credit book, compliance) named in our notes |
| 3   | **Demo**      | Demo delivered, pain and fit confirmed                                                                                                    | A **pilot is agreed with a start date**: tenant created, onboarding visit scheduled, the owner knows what "using it daily" means                                                                                                                                               |
| 4   | **Pilot**     | The tenant exists and real transactions are entering                                                                                      | **Activation reached** (lesson 10's definition: ≥1 customer linked and ≥1 invoice within 14 days) **and** the quote is accepted **and** the first payment has arrived. No advance, no paid — the [[startup-operations-plan\|Startup Operations Plan]]'s oldest rule.           |
| 5   | **Paid**      | Money received against our GST invoice                                                                                                    | Four consecutive weeks of steady use — rates confirmed, orders and invoices flowing — then handed to the success cadence                                                                                                                                                       |
| 6   | **Active**    | The four-week bar is met                                                                                                                  | Stays here; watched for the churn signals lesson 10 defines (rate confirmations dropping, no invoices in 14 days, support silence)                                                                                                                                             |

Two terminal states complete the picture: **Lost** (record a reason — price, timing, no pain, competitor, went silent; mandatory field, because lost reasons are your cheapest market research) and **Churned** (an Active tenant that stopped; triggers the churn postmortem from lesson 10). Note the deliberate gap between Paid and Active: a dealer who paid but never activated is a refund and a bad reference waiting to happen, so the pipeline refuses to call him "won" until the product is in daily use.

## 3. The CRM lives in ERPNext

A **CRM** (customer relationship management system) is just the pipeline made durable — every prospect a record, every conversation a note, every stage change a timestamp. VSYST does not buy one: ERPNext's built-in sales cycle is the CRM, on the same login as the books, exactly as the [[ERPNext-Implementation-Guide|ERPNext guide]] lays out in its Phase 4 sequence — **Lead → Opportunity → Quotation → Sales Order → Sales Invoice → Payment Entry** (the Delivery Note step in the middle is for goods; a subscription skips it).

Map the six stages onto those documents:

| Our stage        | ERPNext document                  | What you record there                                                                |
| ---------------- | --------------------------------- | ------------------------------------------------------------------------------------ |
| Lead / Contacted | **Lead** (status Open → Replied)  | Name, pump, phone, **source** (mandatory), territory, notes from each touch          |
| Demo / Pilot     | **Opportunity**                   | Pain named, demo date, pilot start date, expected close                              |
| Quote accepted   | **Quotation**                     | The plan quoted, validity date, GST — every quote lives here, never only in WhatsApp |
| Committed        | **Sales Order**                   | The accepted subscription order — the document the invoice is raised from            |
| Paid             | **Sales Invoice + Payment Entry** | Our GST invoice and the money against it — from here the books build themselves      |

Four rules make it work at VSYST's size:

1. **Every prospect becomes a Lead the day of first contact** — the field-visit log (§8) feeds it the same evening, not "when I get time".
2. **One owner per deal.** The owner is whoever holds the next step, and their name is on the record.
3. **Source and lost-reason fields are mandatory.** Without source you cannot compute which channel works (§11); without lost reasons you learn nothing from losing.
4. **No parallel spreadsheet.** The ERPNext guide's go-live rule — dual systems kill adoption — applies to the pipeline exactly as it does to invoices. The scorecard (§11) carries _counts_ from ERPNext; it is not a second pipeline.

Standing this up is one evening of configuration (exercise 13.2), and it is deliberately early in the ERPNext adoption order: the guide has the sales cycle as the _first_ workflow to turn on, weeks 2–3.

## 4. The weekly pipeline review

The pipeline is reviewed **every week, same day, 20 minutes**, either as a fixed slot inside the weekly ops meeting ([[T03-weekly-ops-meeting-agenda|T03]]) or immediately after it. The [[company/README|Company Playbook]]'s own cadence sheet asks for a weekly "pipeline velocity scan — lead → demo, demo → paid"; this is that scan, with an agenda:

1. **Numbers first (5 min).** This week vs last: new leads, demos done, pilots started, paid, active; conversion rates from §11. Read from ERPNext, entered on the scorecard before the meeting.
2. **What moved (5 min).** Stage changes since last week — celebrate motion, not talk.
3. **Stuck deals (7 min).** Anything with **no next step, or a next step older than two weeks**, gets one of three verdicts on the spot: a new next step with an owner and a date, a downgrade, or Lost with a reason. Zombie deals are how pipelines rot into fiction.
4. **Decisions (3 min).** Discount asks (against the DoA in [[T22-delegation-of-authority-matrix|T22]]), pause-service calls, anything needing the CEO — decided or scheduled, and logged in [[T09-decision-log-and-adr|T09]] if it sets a precedent.

Three rules of conduct: **review the pipeline, not the person** (the numbers judge the machine, not the seller — this matters double when the sellers are your co-founders); **every open deal leaves the meeting with a next step, an owner and a date**; and **clean as you go** — a 30-row honest pipeline beats a 90-row flattering one.

## 5. Quote → contract → onboarding: the handoff

The most common leak in a young SaaS is not losing deals — it is **winning them and then fumbling the first two weeks**. Sold-but-never-activated is a refund, a churn statistic and an anti-reference all at once. So the moment a dealer says yes, a fixed sequence runs:

1. **Quote** — from ERPNext, with a validity date, the plan and quantity basis spelled out, GST shown, and nothing verbal that isn't written on it. One page. Sent the same day as the yes (the [[startup-operations-plan|Startup Operations Plan]]'s 48-hour proposal rule, tightened).
2. **Order form / agreement** — the signed page that makes it real: parties and GSTINs, plan and term, price and payment terms, start date, a liability cap, DPDP data-processing clauses (lesson 05 owns the template with the lawyer), termination and export-of-data terms. E-signed per lesson 07's e-sign decision; signed PDF filed in Drive and the counterparty folder.
3. **First invoice + payment** — before onboarding begins for a paid tenant. Advance first is the house rule.
4. **Handoff to onboarding** — a five-line note to whoever runs lesson 10's dealer-onboarding SOP: who was sold, what was promised, which anxiety drove the purchase (stock variance? credit book? compliance?), the named contacts on both the owner and staff side, and the pilot/activation target date. The promise made at the demo is the onboarding brief.

The accountability rule: **the seller stays responsible until activation** — ≥1 customer linked, ≥1 invoice, inside 14 days. Onboarding executes; the seller cannot mark the deal Paid-and-forgotten while the tenant sits empty. The pipeline's Paid → Active gap (§2) enforces this structurally.

## 6. Invoicing and collections

Cash is a fact — and the COO owns its operational causes. For subscription revenue that means three mechanisms:

**Invoice on time, every time.** The GST invoice goes out the day the commitment starts and on the same day each renewal cycle, from ERPNext, numbered and filed. An invoice not yet raised is money nobody owes you.

**Nudge toward annual prepay.** An annual prepayment is twelve collection events collapsed into one, cash in the bank now, and a year of churn risk removed — for a bootstrapped company that trade is almost always worth a discount. How much discount is a pricing decision (§7), recorded in [[T09-decision-log-and-adr|T09]]; the _nudge_ — quoting annual first, monthly as the fallback — is an operations habit that costs nothing.

**Run a dunning ladder.** **Dunning** is the polite, escalating chase of an unpaid invoice, on a schedule, so nobody has to feel awkward about improvising it:

| Day  | Action                                                                                                                                                | Who                           |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| T−7  | WhatsApp reminder: invoice attached, due date, amount                                                                                                 | Support/ops                   |
| T0   | Due date on the invoice                                                                                                                               | —                             |
| T+3  | WhatsApp nudge, offer to help if something is stuck                                                                                                   | Support/ops                   |
| T+7  | Phone call to the owner                                                                                                                               | COO                           |
| T+14 | Director-to-owner call; put the account on the ops-meeting issues list                                                                                | CEO or domain-expert director |
| T+30 | Pause/stop-service decision per the DoA matrix ([[T22-delegation-of-authority-matrix\|T22]]) — a decision, never an automatic cut-off for a live pump | Per DoA                       |

Track the result as **DSO — days sales outstanding**: on average, how many days between invoicing and getting paid (accounts receivable ÷ revenue in the period × days in the period). DSO is a weekly scorecard row ([[T05-kpi-scorecard|T05]]), the AR ageing behind it is lesson 06's weekly habit, and the deeper cash mechanics live in [[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]].

One India-specific rail to know before self-serve billing exists: recurring auto-debits (cards, UPI Autopay, e-mandates) run under the RBI e-mandate framework — debits above **₹15,000** need customer authentication each time, and a pre-debit notification at least 24 hours ahead is mandatory ([AMLEGALS — RBI e-mandate framework 2026 compliance checklist](https://amlegals.com/upi-autopay-and-recurring-payments-compliance-checklist-under-rbis-e-mandate-framework-2026/)) — **VERIFY LIVE** with the gateway when the Easebuzz/UBI conversation matures. Until then, collections are manual by design: NEFT against our invoice, recorded in ERPNext (the sales-led v0 in the [[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]).

## 7. Pricing operations — quoted, not published

Price _setting_ is a strategy decision the founders own, and DZZLO's price points are **deliberately undecided**. Price _operations_ — how prices are quoted, recorded, discounted and changed — is yours, and it starts now, because the first quote will go out long before a pricing page exists.

What is already decided (2026-07-29, recorded in the [[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]) and must be quoted consistently:

- **The company subscribes, per GSTIN.** Every company — each sister company too — is its own billable tenant. Dealers pay first; customer firms may pay later for fleet features.
- **Users are unlimited and never charged.** Gate on usage and features if ever needed — never on headcount.
- **All billing happens on the web.** The app stays purchase-silent (lesson 12 carries the store-compliance half of this).

The operating rules on top:

1. **Quoted, not published.** Until the price point is settled, the price exists only inside individual Quotations in ERPNext. That keeps early pricing an experiment you can vary deal by deal, not a public anchor you must defend. Every quote logged is a data point for the eventual decision.
2. **The floor comes from the cost model, not from courage.** The [[app-store-economics/11-cost-model-worksheet|cost-to-serve worksheet]] gives the three numbers every quote must respect: **V** (variable cost per tenant per month), the gross-margin floor (V ÷ 0.2 for a healthy ~80% SaaS margin), and **N_be** (how many paying dealers a candidate price needs to cover fixed costs). Keep the current V and floor written at the top of the pricing note; requote the worksheet quarterly as the fine print asks.
3. **Discounts follow the DoA.** Who may deviate how far from the standard quote is a row in [[T22-delegation-of-authority-matrix|T22]]; anything beyond it is a decision, not a favour, logged in [[T09-decision-log-and-adr|T09]]. No verbal special deals — the dealer community in one district talks, and two neighbours discovering different prices costs more trust than either deal earned.
4. **Never gate the compliance floor.** GST-correct invoices and the core ledger stay in every tier — the strategy doc's Kano-floor rule. A dealer must never be able to say DZZLO held his books hostage.
5. **Grandfathering is decided before the first paid tenant, not after.** Write down now what happens to early free tenants and pilot pricing when list prices land; retrofitting that promise is how early champions become ex-customers.

And the honesty rule of this vault applies to yourself: worked numbers in your pricing notes are illustrative until real bills and real quotes replace them, and this course states no DZZLO price anywhere — because none exists yet.

## 8. Field sales, Raipur edition

The playbook's channel research ([[12_OWNER_ACQUISITION|owner-acquisition research]]) ranks warm, human, vernacular channels — dealer referrals, OMC territory-manager introductions, association sponsorship, the CA channel — far above anything digital for this buyer, and the [[company/README|Company Playbook]]'s wedge is atomic: **saturate one district before touching a second**. VSYST's version of that is unusually concrete: the office sits inside the family's petrol pump, and the domain-expert director has three decades of relationships in exactly the territory the first hundred tenants must come from. Field-sales ops turns that advantage into a machine:

- **Territory: one district.** Write its name down. Every lead outside it is parked, politely, until the district is won. Expansion is a quarterly-planning decision (lesson 19), not an enthusiasm.
- **The visit log is the unit of work.** Every pump visit produces a row, same evening, no exceptions: date · pump and owner met · who was present (owner? second-generation son?) · anxiety discussed (stock variance / credit book / compliance) · artefact left behind · next step **with a date**. The row feeds the ERPNext Lead; a visit without a logged next step is a chai break, not sales.
- **Work the warm channels as named lists, not vibes.** Three short lists, each with an owner: dealers who could refer (§10), association office-bearers and meeting dates, and the OMC/CA contacts who could introduce. Progress on each list is reviewed in the weekly pipeline review.
- **Sell to the family system.** The research's dual-persona choreography — the second-generation son leans in on data and dashboards; the father signs when he sees trust signals (the dealer next door, the CA's nod, a person who shows up) — is a scripting instruction for demos: bring the numbers for one, the references for the other, in the language of their ledger, in an eight-minute pitch that leads with loss avoided, not features.
- **Respect the buyer's phone.** Demo on our device or in the browser; never demand an install before value is shown.

The COO rarely does these visits. The COO makes sure the visits _exist as data_ — logged, followed up, and countable in §11 — and that the founder doing them is spending those hours on the district's highest-value list, not the friendliest one.

## 9. Partnership operations — IOCL and the bank/gateway

VSYST has two partner conversations in flight: discussions with two IOCL contacts, and a Union Bank of India / Easebuzz internet-payment-gateway proposal. Both are **in discussion — which means neither is revenue, a feature, or a fact** until something is signed and live. Partnerships are where small companies burn the most senior time for the least recorded output: months of meetings, warm feelings, and nothing anyone can point to. The fix is the same four mechanisms as everywhere else:

1. **One owner per partnership.** A single named person holds the relationship, the follow-ups and the tracker row. The CEO can be in the meetings; the owner runs the thread.
2. **A tracker — one row per conversation.** Kept in the vault next to the correspondence folder:

| Partner            | What we want | What they want | Owner | Stage                                                | Last touch | Next step (owner · date) | Documents  | Walk-away line |
| ------------------ | ------------ | -------------- | ----- | ---------------------------------------------------- | ---------- | ------------------------ | ---------- | -------------- |
| IOCL contact A     | (fill)       | (fill)         | …     | contact / discussion / proposal / MoU / pilot / live | …          | …                        | notes link | …              |
| IOCL contact B     |              |                |       |                                                      |            |                          |            |                |
| UBI / Easebuzz IPG |              |                |       |                                                      |            |                          |            |                |

3. **Next-step discipline.** No partner meeting ends without a written next step, an owner and a date — and the meeting note lands in the tracker within 24 hours. A partnership with no movement for 30 days gets a verdict at the ops meeting: push (a dated action) or park (moved to a dormant list, guilt-free). "Stalled but hopeful" is not a stage.
4. **Paper hygiene.** NDA before any real data changes hands; remember an **MoU is a statement of intent, not a contract or revenue**; the lawyer reads anything with obligations before signature (lesson 05); signed documents to Drive and the company binder ([[T02-company-binder-checklist|T02]]).

Two escalation artefacts keep partnerships honest as they mature. When a partnership asks for a real commitment — engineering time, exclusivity, revenue share, data access — that is a **decision memo** in [[T09-decision-log-and-adr|T09]]: context, options, one-way or two-way door, decided by whom, review date. And when a partnership becomes work — the gateway integration pilot is the obvious first case — it gets a **project charter** in [[T18-project-charter|T18]]: problem, success metric, scope in/out, DRI, milestones, decision rights. Exercise 13.3 writes both. One forward note for the gateway thread: payment aggregators must run full merchant KYC under RBI's directions, so expect to produce incorporation documents, PAN, GSTIN, a cancelled cheque, director KYC and a live website with terms, privacy, refund and contact pages ([AuthBridge — RBI payment-aggregator master direction, 2025](https://authbridge.com/blog/rbi-payment-aggregator-master-direction-2025/)) — **VERIFY LIVE** the exact list with the gateway; the company binder from lesson 05 is most of it.

The strategic guardrail: **a partnership is a channel, not the strategy.** If the district plan (§8) only works when IOCL says yes, it is not a plan. Partnerships accelerate a machine that already sells; they do not substitute for one.

## 10. The referral programme as an operating routine

The [[06_REFERRAL_PROGRAM|referral programme design]] — "Dealer Dost" — already exists as a designed artefact: double-sided rewards (the referrer earns, the new dealer gets free months), milestone tiers, WhatsApp-native share mechanics, and a fraud-prevention list. Referrals sit at the top of the acquisition ranking for this buyer, so when the paid loop exists this programme is worth running properly. What the design does not include is the operations, and a referral programme with sloppy ops is a trust-destroyer — a dealer who referred a friend and never got paid tells that story at the association meeting. The COO's checklist:

- **Attribution at the source.** The referrer's name/code is captured on the ERPNext Lead the day the referred dealer appears (§3's mandatory source field). Attribution reconstructed later is attribution disputed.
- **Payout on a rule, on a date.** Pay only after the referred dealer is genuinely paying (the design's month-3 rule — its single best anti-fraud lever), on a fixed monthly payout day, by UPI, with a receipt. Every payout logged.
- **Fraud checks before money moves.** Same-GSTIN/PAN self-referrals rejected; unusually prolific referrers reviewed manually; clawback terms disclosed upfront — all per the design.
- **Tax and paper.** Referral payouts to dealers are commission-like income — TDS and GST treatment (and the ₹-threshold where TDS starts) **VERIFY LIVE with the CA** before the first rupee is paid out, and put the programme's terms on one written page a dealer can read.
- **Re-run the economics after pricing.** The design's reward amounts and its share-of-first-year-revenue maths assume an ARPA that does not exist yet (§7). Before launch, recompute the reward ladder against the real quoted prices so the programme cannot pay out more than a customer is worth. Treat every ₹ figure in the design as a proposal until then.
- **Measure it.** Two scorecard rows: referrals submitted, and % of new paid customers that are referral-attributed (the design's target: a quarter of new customers by month 12 — treat as a target to test, not a law).

Launch order matters: the design itself says the dealer-to-dealer loop comes first, run manually, and the partner/affiliate layer (CAs, territory managers) only after the loop demonstrably works. Resist tooling until the manual version creaks.

## 11. Pipeline math on the scorecard

The [[startup-operations-plan|Startup Operations Plan]] states the payoff plainly: learn your pipeline math, because once you know that roughly ten leads make one client, "growth is math, not hope." The math is four conversion rates and one speed:

```
leads → demos      demo rate        (of leads contacted, how many reach a demo?)
demos → pilots     pilot rate       (of demos, how many agree to start?)
pilots → paid      close rate       (of pilots, how many activate and pay?)
paid  → active     activation rate  (of paid, how many reach steady use?)
velocity           median days from first contact to paid
```

With those, planning inverts cleanly: if the quarter's goal is N new paying dealers and the rates say each needs X demos and Y leads, the weekly visit target (§8) stops being a guess. Early on the rates will be noisy — single-digit counts produce wild percentages — so read trends over 4-week windows and resist tuning the machine off one week's numbers.

These live as rows on the KPI scorecard ([[T05-kpi-scorecard|T05]]), entered every Monday from ERPNext by one owner:

| Scorecard row                                       | Source                                            |
| --------------------------------------------------- | ------------------------------------------------- |
| New leads this week (by source)                     | ERPNext Lead count                                |
| Demos done · pilots started · new paid · new active | ERPNext stage changes                             |
| Conversion rates (4-week rolling)                   | Computed from the above                           |
| Referral-attributed % of new paid                   | Lead source field                                 |
| DSO · AR overdue ₹                                  | ERPNext receivables (§6)                          |
| MRR / ARPA                                          | Once priced — until then, count of paying tenants |

One filing note to prevent a predictable mix-up: [the workbook](toolkit/vsyst-coo-workbook.xlsx) has a `Hiring Pipeline` tab — that one is for _hiring_ (lesson 09). The sales pipeline deliberately has no workbook tab of its own: **deals live in ERPNext, and only the counts land on the `KPI Scorecard` tab.** A second pipeline spreadsheet is exactly the parallel system §3 bans.

## 12. At VSYST — applying this now

- **The stage names go up this week.** Agree the §2 table with the CEO and the domain-expert director in one sitting (exercise 13.1) — the exit criteria only work if the people doing the selling accept them as the definition of truth.
- **Seed the pipeline from what already exists.** The district around the family pump, the dealers the domain-expert director already knows, anyone who has ever asked about the app: 20–30 honest Lead rows in ERPNext beats an empty CRM waiting for perfect data. Free-tier tenants using DZZLO today are pipeline too — they are future Paid conversions and belong in it as their own stage-4 cohort when monetisation starts.
- **Billing v0 is sales-led and manual, on purpose.** Per the [[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]], the first paying tenants are handled with an offline-recorded payment and a proper GST invoice — no gateway, no self-serve. Collections discipline (§6) matters _more_ in this mode, not less, because nothing auto-collects.
- **Partnerships get their tracker before their next meeting.** Three rows exist today (two IOCL threads, one gateway thread). Ten minutes of tracker now saves the "wait, what did we agree in May?" archaeology later — and gives the CEO a one-glance answer when a director asks how the IOCL conversation is going.
- **What not to do yet:** no referral tooling, no CRM other than ERPNext, no pricing page, no second district, no partner-revenue assumptions in any plan. Every one of those has a trigger written in this lesson; wait for the trigger.

## 13. Exercises

**13.1 — Write the six exit criteria (30 min, with the CEO and the domain-expert director).** Take the §2 table and rewrite each exit criterion in your own words for VSYST's actual motion — argue about Pilot → Paid especially (does payment come before or after activation for the very first tenants?). Paste the agreed table into a `sales-pipeline` note in the vault and record the agreement as a decision in [[T09-decision-log-and-adr|T09]]. From today, stage changes follow this table or the table gets amended — never silently ignored.

**13.2 — Stand up the sales cycle in ERPNext (60 min).** Following the [[ERPNext-Implementation-Guide|ERPNext guide]]'s Phase 4 sequence: create the Lead sources (referral, association, OMC contact, CA, field visit, inbound), enter your ten most real prospects as Leads with source and owner filled, and run one dry run end-to-end — Lead → Opportunity → Quotation (marked draft/illustrative) — so the path is proven before a live deal needs it. Artefact: ten honest Lead rows and one practice Quotation.

**13.3 — The partnership tracker and the gateway charter (45 min).** Create the §9 tracker with its three real rows — the two IOCL conversations and the UBI/Easebuzz thread — filling owner, stage, last touch and a dated next step for each; write the "walk-away line" for each row and log those three lines in [[T09-decision-log-and-adr|T09]]. Then draft a one-page [[T18-project-charter|T18]] charter for the gateway pilot: the problem it solves, the success metric, scope in/out, the DRI, and the decision rights (who can accept the gateway's commercial terms). Show both to the CEO for edit-or-agree.

**13.4 — Pipeline rows on the scorecard (20 min).** Add the §11 rows to [[T05-kpi-scorecard|T05]] (the `KPI Scorecard` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx)): metric, owner, source query, and a first target where one is honest. Note on the tab that deal-level truth lives in ERPNext and that the `Hiring Pipeline` tab is people, not sales. Set the Monday-morning entry owner — probably you, for now.

---

**Next:** [[12-product-and-engineering-operations|12 — Product and Engineering Operations]] — the process around shipping: release cadence and the release checklist, app-store operations, incidents and blameless postmortems, monitoring and alerting, backups, DPDP for the product, and the four engineering numbers on the scorecard.
