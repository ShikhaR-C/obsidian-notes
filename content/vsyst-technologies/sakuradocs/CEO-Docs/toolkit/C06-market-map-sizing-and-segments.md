# C06 — Market Map: Sizing, Segments and Alternatives

_Toolkit · fills the exercises in [[05-strategy-i-diagnosis-and-the-strategy-kernel|05 — Strategy I: Diagnosis and the Strategy Kernel]] · Owner: CEO (nobody else may change a universe count) · Cadence: built once in Month 1, refreshed quarterly and before any fundraise or territory decision · Workbook tab: `Market Map` in [vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)._

## Purpose

A market map is four answers on one page: **how many buyers exist**, **which of them you have chosen**, **what you would earn if you won them**, and **what they are using instead of you right now**. It is not a slide. It is the denominator underneath every other CEO number — the pipeline coverage in [[C10-founder-led-sales-pipeline-and-script|C10]], the CAC payback in [[C12-unit-economics-and-business-model-calculator|C12]], the "where to play" choice in [[C05-choice-cascade-worksheet|C05]], and the plausibility of the whole plan in [[C04-strategy-kernel-one-pager|C04]].

The standard vocabulary — TAM (all demand at 100% share), SAM (the slice your distribution reaches), SOM (the share you can realistically take) — is fine ([Total addressable market](https://en.wikipedia.org/wiki/Total_addressable_market)). The **method** is where founders lie to themselves. There are two ways to get a TAM: take an analyst's "Indian fuel-retail software to reach \$X bn by 2030" and multiply by a hoped-for share, or count actual buyers and multiply by the price you will actually charge. The first produces a number nobody can act on; the second tells you how many districts to visit this quarter. This template supports only the second. Rumelt's test applies: a strategy that cannot be turned into "who, how many, at what price, reached how" is fluff, not diagnosis ([_Good Strategy Bad Strategy_, Crown, 2011](https://www.penguinrandomhouse.com/books/91324/good-strategy-bad-strategy-by-richard-rumelt/9780307886231/); [McKinsey — The perils of bad strategy](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/the-perils-of-bad-strategy)).

The fourth panel — **alternatives** — is the one most maps omit and the one that decides whether you win. DZZLO's real competitive set is not other fuel-retail software. It is paper, an accountant, and a WhatsApp group. Customers "hire" something to make progress, and the incumbent is usually a habit rather than a product ([Christensen, Hall, Dillon & Duncan — Know Your Customers' "Jobs to Be Done", HBR, 2016](https://hbr.org/2016/09/know-your-customers-jobs-to-be-done)). If your map does not name the paper DSR, it is describing a market that does not exist.

## When to use

- **Month 1 of the CEO seat, before the strategy kernel is written.** [[05-strategy-i-diagnosis-and-the-strategy-kernel|Lesson 05]]'s diagnosis needs a denominator; [[C04-strategy-kernel-one-pager|C04]] cannot be honest without one.
- **Before any territory decision.** "Raipur first, then Durg" is a market-map claim — make it with counts, not driving time.
- **Before quoting a price**, and refreshed with [[C11-pricing-and-packaging-decision-sheet|C11]] whenever the price moves.
- **Before any fundraise conversation** — it is the backbone of the market slide in [[C15-investor-narrative-and-deck-outline|C15]], and investors interrogate bottom-up numbers while discounting top-down ones.
- **Quarterly**, at planning ([[C28-annual-plan-and-ceo-okr-sheet|C28]]), because counts move and field conversations from [[C09-icp-and-customer-discovery-guide|C09]] keep correcting the segment scores.

## How to fill (rules)

1. **Every universe count carries a source and a date, and is flagged `**VERIFY LIVE**`.** No exceptions, including counts you are sure of. A row reads `240 outlets · PPAC statewise file · downloaded 2026-08-24 · **VERIFY LIVE**`. If you cannot name the file, it belongs in the Guess column. PPAC re-issues its state-wise retail-outlets file through the year ([PPAC — Retail Outlets](https://ppac.gov.in/infrastructure/retail-outlets)).
2. **Bottom-up only, in three factors: universe count × addressable filter × annual price per GSTIN.** If a fourth factor appears you are modelling, not sizing.
3. **Top-down market numbers are for decks, never for plans.** Quote an industry report on a slide to show the category is not a rounding error. Never use one to set a target, a hire or a budget. Keep them in a separate `Top-down (deck only)` block so nobody downstream confuses the two.
4. **Count the billing unit, not the physical unit.** VSYST bills **per GSTIN**, not per pump ([[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]). Three outlets under one GSTIN is one subscription; two sister firms are two. Convert outlets to GSTINs with an explicit stated ratio — itself a **VERIFY LIVE** assumption you test in the field.
5. **The addressable filter must be a rule someone could apply to a list**, not "dealers who are progressive". If the ICP rubric in [[C09-icp-and-customer-discovery-guide|C09]] cannot score it, it is not a filter.
6. **SAM is limited by the sales motion you have, not the one you plan to have.** VSYST's motion is one founder driving to pumps; that caps SAM at districts reachable in a day, and the cap is correct. Moore's beachhead logic agrees — complete the solution for one segment before touching the adjacent one ([Crossing the Chasm](https://en.wikipedia.org/wiki/Crossing_the_Chasm)).
7. **Score segments on four axes and multiply, do not add** — pain × ability to pay × reachability × fit, each 1–5, max 625. A zero on any axis must kill the segment; adding lets one with no ability to pay survive on charm. Ability to pay binds here: a mid-volume pump grossing ₹1.5–2 crore of topline takes home ₹1.5–4 lakh of operating profit ([[company/10_AFFORDABILITY_PROBLEM|affordability problem]]) because dealer commission is a fixed ₹1–3 per litre, not a margin ([Business Standard](https://www.business-standard.com/companies/news/petrol-pump-dealer-commission-raised-retail-prices-remain-unchanged-124103000842_1.html); [Business Today](https://www.businesstoday.in/india/story/pump-commission-rules-explained-how-much-petrol-pump-owners-earn-per-litre-in-india-what-costs-do-they-have-to-manage-and-more-520996-2026-03-18)).
8. **Run penetration at 1% / 3% / 10% and write the field consequence, not just the rupees.** 3% of a district is a number of pumps, which is a number of visits per week, which is a number of months. If that is impossible, the scenario is fiction.
9. **Name every alternative, including "nothing".** Doing nothing leads most SMB categories. Each row gets its real cost to the dealer in ₹ and hours, what it is genuinely good at, and the one thing it cannot do.
10. **Version the map; never overwrite it.** The delta between quarters is the most useful thing in the document, and it belongs in [[C29-decision-journal-and-one-way-door-log|C29]] when it moves a decision.

## Template

**(a) The bottom-up ladder** — copy this block into the `Market Map` tab; the tab computes the right-hand column.

```
BOTTOM-UP MARKET MAP — <product> — built <date> — next refresh <date+90d>
Pricing metric this map is denominated in: ONE SUBSCRIPTION PER GSTIN (C11)

STEP 1  UNIVERSE           count ______  source ____________  as of ____  VERIFY LIVE
        (physical unit, e.g. retail outlets in the geography)

STEP 2  BILLING CONVERSION outlets per GSTIN ______  (assumption; how tested: ______)
        => billable firms   = Step 1 ÷ ratio            = ______

STEP 3  ADDRESSABLE FILTER (a rule you can apply to a list — state it):
          - ___________________________________________
          - ___________________________________________
        pass rate ______%   (source: field sample of ___ dealers, dated ____)
        => SAM firms       = Step 2 × pass rate          = ______

STEP 4  ANNUAL PRICE / GSTIN  ₹______ ex-GST   (blended across tiers, from C11)

        TAM  (all billable firms, geography-wide) = Step 2 × Step 4 = ₹______
        SAM  (reachable by TODAY's sales motion)  = Step 3 × Step 4 = ₹______
        SOM  (see penetration block)                                 = ₹______

PENETRATION SCENARIOS on SAM
  |  1% | firms ____ | ARR ₹______ | visits/week ____ | months to reach ____ |
  |  3% | firms ____ | ARR ₹______ | visits/week ____ | months to reach ____ |
  | 10% | firms ____ | ARR ₹______ | visits/week ____ | months to reach ____ |

TOP-DOWN (DECK ONLY — never used in a plan, a budget or a target)
  <analyst number> <source> <date>              NOT ACTIONABLE
```

**(b) Segment scoring** — 1–5 per axis; product score = pain × pay × reach × fit (max 625).

| Segment                                    | Pain intensity | Ability to pay | Reachability | Product fit | **Product score** | Verdict |
| ------------------------------------------ | -------------- | -------------- | ------------ | ----------- | ----------------- | ------- |
| _e.g._ Pump dealer with a real credit book |                |                |              |             |                   |         |
| Pump dealer, retail-only forecourt         |                |                |              |             |                   |         |
| Lubricant distributor                      |                |                |              |             |                   |         |
| Bulk-diesel / bowser operator              |                |                |              |             |                   |         |
| Transport fleet (dealer's customer)        |                |                |              |             |                   |         |

**(c) Alternatives we are actually replacing** — one row per thing the dealer uses today.

| Alternative | What it costs him today (₹ / hours) | What it is genuinely good at | What it cannot do | How we win against it | Where we lose to it |
| ----------- | ----------------------------------- | ---------------------------- | ----------------- | --------------------- | ------------------- |

## Worked example — VSYST (illustrative)

**Every number below is illustrative and every universe count is a placeholder until the PPAC file is downloaded. `**VERIFY LIVE**`.**

India crossed **1,00,266 retail outlets** as of end-November, with IOC at 41,664, BPCL at 24,605 and HPCL at 24,418 — the three PSU marketers running over 90% of the network ([Energy Watch — India's petrol pump count crosses 1 lakh](https://www.energywatch.in/oil-and-gas/indias-petrol-pump-count-crosses-1-lakh-nearing-us-china-in-network-scale); [Petrosoft — Fuel Retail Trends India 2026](https://petrolbunksoftware.com/blog/fuel-retail-trends-india-2026); [IndianOil media release](https://www.iocl.com/MediaDetails/45687)). That is the **only** number here with a real source. Chhattisgarh has 33 districts, of which Raipur is one ([List of districts of Chhattisgarh](https://en.wikipedia.org/wiki/List_of_districts_of_Chhattisgarh)); the state and district outlet counts must come from PPAC's downloadable state-wise file — **VERIFY LIVE** at [PPAC — Retail Outlets](https://ppac.gov.in/infrastructure/retail-outlets), whose page carried a last-updated date of 24 August 2026 when checked.

```
STEP 1  UNIVERSE (Raipur district retail outlets)   ~240   PLACEHOLDER   VERIFY LIVE (PPAC)
STEP 2  outlets per GSTIN 1.3  (tested: 0 dealers so far — first 10 interviews must test it)
        billable firms      ~185
STEP 3  FILTER: >=15 active B2B credit customers + >=1 delivery vehicle + GST reg
                + owner/son transacting on a phone
        assumed pass rate 40%  (PLACEHOLDER — measure it across the first 25 dealers)
        SAM firms           ~74
STEP 4  annual price/GSTIN  ₹21,600 ex-GST   (₹1,800/mo blended — PLACEHOLDER, C11)

        TAM (Raipur, all billable firms)  185 × ₹21,600 = ₹40.0 lakh ARR
        SAM (today's founder-led motion)   74 × ₹21,600 = ₹16.0 lakh ARR

PENETRATION ON SAM
   1% → 1 firm   → ₹0.22 L ARR → already true after one close
   3% → 2 firms  → ₹0.43 L ARR → this quarter
  10% → 7 firms  → ₹1.51 L ARR → ~7 closes; at a 1-in-6 close rate that is 42 qualified
                   conversations; at 4 pump visits a week that is roughly 3–4 months
```

Read that out loud, because it is the point of the exercise: **one district does not make a company.** ₹16 lakh of SAM in Raipur is a proof-of-motion budget, not a business. The map's real output is the next question — _which second and third districts, and when does the motion stop being a founder in a car?_ That is a [[C05-choice-cascade-worksheet|C05]] question, and the map is what makes it answerable. Chhattisgarh's 33 districts and the national 1,00,266 are why the ceiling is not the concern; the sales motion is.

**Segment scores (illustrative):**

| Segment                                                                                                    | Pain | Pay | Reach | Fit | Score   | Verdict                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------------------------- | ---- | --- | ----- | --- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pump dealer with a real credit book** (bulk diesel + lubes to fleets, factories, hospitals, contractors) | 5    | 3   | 4     | 5   | **300** | **Beachhead.** Pain is reconciliation, not billing; the product was built for this                                                                                                                       |
| Bulk-diesel / bowser operator                                                                              | 5    | 4   | 2     | 5   | **200** | Second wave — best pain and pay, hardest to find from a district list                                                                                                                                    |
| Lubricant distributor                                                                                      | 4    | 3   | 3     | 4   | **144** | Third; the rate window matters less to him                                                                                                                                                               |
| Transport fleet (rides free on the dealer's tenant)                                                        | 4    | 4   | 5     | 3   | **240** | **Not a paying segment today** — free by design, to protect the two-sided network. Paid fleet plans are a Layer-3 decision ([[app-store-economics/10-pricing-metric-decision\|pricing-metric decision]]) |
| Pump dealer, retail-only forecourt, no credit book                                                         | 2    | 3   | 5     | 1   | **30**  | **Disqualify.** He needs a POS; selling to him produces a churn statistic                                                                                                                                |

**Alternatives we are actually replacing (illustrative):**

| Alternative                                                                                                                                                          | Costs him today                                                                                            | Genuinely good at                                                                                                                                                     | Cannot do                                                                                     | How we win                                                                                                                                       | Where we lose                                             |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- |
| **Paper DSR + diary**                                                                                                                                                | ₹0 cash; 1–2 hrs/day; unquantified write-offs                                                              | Zero training; works in a power cut; the pump manager trusts it                                                                                                       | Prove a rate was agreed; age a receivable; survive a dispute six months later                 | Show the rate-confirmation window and the driver-OTP trail — the two moments paper loses money                                                   | The 58-year-old owner who is not the one feeling the pain |
| **Tally + the accountant**                                                                                                                                           | Licence (**VERIFY LIVE** at [Tally Solutions](https://tallysolutions.com)) + ₹12,000–25,000/mo for a munim | GST returns, statutory books, what the CA already accepts                                                                                                             | Per-customer daily rates, dispatch, delivery proof, a ledger the _customer_ sees on his phone | Position _upstream of_ Tally, never as a replacement — transaction in DZZLO, books stay in Tally ([[C08-positioning-and-messaging-canvas\|C08]]) | Wherever the accountant decides and reads us as a threat  |
| **WhatsApp groups**                                                                                                                                                  | ₹0; huge hidden cost in disputes                                                                           | Instant, universal, a genuinely real Indian business channel ([Inc42](https://inc42.com/features/how-whatsapp-business-is-bringing-indias-smes-to-the-digital-fold/)) | Compute a balance; lock a rate; be searchable in month four                                   | Don't fight it — DZZLO must _feed_ it (statements and confirmations forwarded out)                                                               | Any deal that asks his customers to abandon WhatsApp      |
| **Excel credit tracking**                                                                                                                                            | ₹0; one laptop; one corrupt file from disaster                                                             | Flexible; the son already knows it                                                                                                                                    | Multi-user, mobile, auditable, linked to an invoice                                           | Aged receivables and the monthly credit/debit roll-up out of the box                                                                             | The dealer proud of a genuinely good sheet                |
| **ATG / DU-bundled forecourt software** ([Petrosoft India](https://www.softwaresuggest.com/petrosoft-india), [Gilbarco Veeder-Root India](https://www.gilbarco.in/)) | Bundled into hardware AMC                                                                                  | Tank and dispenser telemetry, forecourt automation, metrology records                                                                                                 | The **credit** side — the B2B customer, his ledger, his order, his confirmation               | We are the credit-and-customer layer; DIP is the overlap and a Pro-tier feature, not the pitch                                                   | The dealer whose pain is shrinkage, not receivables       |
| **Doing nothing**                                                                                                                                                    | ₹0                                                                                                         | No decision, no training, no argument with the accountant                                                                                                             | Nothing changes; the write-off recurs next year                                               | Quantify one loss he has already taken, in his numbers, in front of him                                                                          | Any dealer who cannot name a loss — not a prospect yet    |

Two of those rows are also the objection bank's first two entries, which is why [[C10-founder-led-sales-pipeline-and-script|C10]] is built from this table rather than beside it.

## Common mistakes

| Mistake                                          | What it looks like                                                    | Fix                                                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Top-down TAM in a plan**                       | "The Indian fuel-retail software market is \$X bn; 1% is \$Y m"       | Move it to the deck-only block. Targets come from the bottom-up ladder or from nowhere      |
| **The 1% fallacy**                               | Treating 1% of a huge market as easy because it is a small percentage | Convert every scenario into visits per week and months. 1% is not a share, it is a calendar |
| **Sizing on the physical unit**                  | Counting pumps when you bill per GSTIN                                | Convert with a stated ratio and test it in the first ten interviews                         |
| **No date on a count**                           | A number with no provenance                                           | Source + date + `**VERIFY LIVE**`, or it lives in the Guess column                          |
| **Adding segment scores instead of multiplying** | A segment with zero ability to pay survives because pain is 5         | Multiply. A zero must kill the row                                                          |
| **Omitting "doing nothing"**                     | An alternatives table listing only software                           | Paper, the accountant, WhatsApp, Excel and inertia are the competitive set                  |
| **SAM sized on a motion you don't have**         | Counting all 33 districts while one founder sells alone               | Cap SAM at today's motion; expanding it is a logged decision                                |
| **Confusing free riders with the market**        | Counting the dealer's B2B customers in the TAM                        | They ride free by design; they enter TAM only when a fleet plan is priced                   |

## Related

Lessons [[05-strategy-i-diagnosis-and-the-strategy-kernel|05]] (diagnosis), [[06-strategy-ii-moats-positioning-and-the-business-model|06]] (business model), [[07-customers-markets-and-founder-led-sales|07]] (reading the market from the field), [[17-the-numbers-a-ceo-watches|17]] · Templates [[C04-strategy-kernel-one-pager|C04]], [[C05-choice-cascade-worksheet|C05]], [[C08-positioning-and-messaging-canvas|C08]], [[C09-icp-and-customer-discovery-guide|C09]], [[C10-founder-led-sales-pipeline-and-script|C10]], [[C11-pricing-and-packaging-decision-sheet|C11]], [[C12-unit-economics-and-business-model-calculator|C12]], [[C15-investor-narrative-and-deck-outline|C15]] · Vault [[00_OVERVIEW|Product Overview]], [[company/10_AFFORDABILITY_PROBLEM|affordability problem]], [[12_OWNER_ACQUISITION|owner-acquisition research]], [[11_EDUCATION_GAP|education-gap analysis]] · [[CEO-Docs/toolkit/index|CEO Toolkit]]
