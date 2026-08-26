# CEO-Docs — Shared Build Spec (read this fully before writing anything)

You are one writer on a team building **CEO-Docs**, a noob-to-expert course for whoever holds the
**Chief Executive Officer seat at VSYST Technologies Pvt. Ltd.** It is the sibling of the finished
**COO-Docs** course in the same vault. Match its quality, depth, voice and conventions exactly.

## Paths

- Vault root for this work: `/Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/obsidian-notes/content/vsyst-technologies`
- Write your files into: `<vault>/sakuradocs/CEO-Docs/` (lessons) or `<vault>/sakuradocs/CEO-Docs/toolkit/` (templates)
- The reference course you must imitate: `<vault>/sakuradocs/COO-Docs/`
- **Before writing, read at least two COO files end to end** to absorb the voice —
  e.g. `COO-Docs/01-what-is-a-coo.md` and `COO-Docs/03-the-coo-core-value-and-the-ceo-coo-contract.md`
  (or, if you are writing a toolkit template, `COO-Docs/toolkit/T30-coo-charter-and-90-day-plan.md`
  and `COO-Docs/toolkit/T05-kpi-scorecard.md`).

## The company (get these facts right — they are load-bearing)

- **VSYST Technologies Pvt. Ltd.**, Raipur, Chhattisgarh. Indian **Private Limited** company.
- **Three founder-directors, family-founded.** A **technical CEO who ships code**, a **domain-expert
  director** (fuel-distribution domain), and a third director. No CFO. No hired executives yet.
- **Newly formed, bootstrapped, pre-revenue.** No outside capital. No board beyond the founder-directors.
- **One product: DZZLO OMS** — a multi-tenant, mobile-first Order Management System for **Indian fuel
  distribution**: petrol-pump dealers, lubricant distributors, bulk-diesel operators. Live on both
  app stores. India-only. Sales-assisted, sold district by district.
- **Who pays:** the **dealer** is the paying tenant; the dealer's B2B customers (transport fleets,
  factories, hospitals, contractors) ride free on the dealer's tenant.
- **The product loop:** rate setting (10 PM–6 AM confirmation window) → order → dispatch with driver
  OTP → three-tier invoice (PRODUCT / CASH_REIMBURSE / GST, TCS auto-added past ₹50L turnover) →
  voucher/payment/reconciliation. Stack: Node/Mongo/AWS, Expo React Native app, Quartz+Obsidian docs,
  GitHub, ERPNext as intended system of record, Figma, WhatsApp.
- **Decided direction (already settled, do not re-litigate):** dealer companies pay **per GSTIN**;
  users are unlimited and free; **billing is web-only** (to avoid app-store commission); the app is
  gated server-side. See `docs/learning/app-store-economics/08-dzzlo-subscription-strategy.md`.
- **Live relationships:** IOCL (oil marketing company) discussions; Easebuzz (payment gateway)
  onboarding. See `<vault>/correspondence/`.
- **Neighbouring docs to link to, never to repeat:**
  - `[[COO-Docs/index|COO Docs]]` — the operating-system course. The CEO course is its mirror.
  - `[[startup-operations-plan|Startup Operations Plan]]`
  - `[[ERPNext-Implementation-Guide|ERPNext Implementation Guide]]`
  - `[[finance/00_README|Finance for Founders]]` — the accounting/finance course (11 phases)
  - `[[company/README|DZZLO Company Building Playbook]]` — GTM, pricing, launch, acquisition research
  - `[[app-store-economics/README|App Store Economics]]` — the subscription/pricing research
  - `[[certification-and-standards-roadmap|Certification and Standards Roadmap]]` — ISO 27001 etc.

## The governing idea of the CEO course

> **The COO's product is the operating system. The CEO's product is the company's direction, its
> capital, its people and its story — and the judgment that allocates all four.**

Fred Wilson's reduction is the spine: a CEO does only three things — **set the vision and strategy
and communicate it; recruit and retain the very best talent; and make sure there is always enough
cash in the bank.** Everything else in this course hangs off those three, plus a fourth that a
founder-CEO of an Indian Pvt Ltd cannot delegate: **the director's legal and governance duty.**

The recurring rule (the CEO course's counterpart to the COO's "mechanisms, not intentions"):

```
Only you can decide it        -> decide it, write down why      (decision journal, 02 / C29)
Someone else could decide it  -> give them the decision + limit (decision rights, 03 / C03)
Nobody can decide it yet      -> run the smallest experiment    (strategy under uncertainty, 05)
And in every case             -> say it out loud, twice         (communication, 12)
```

## Non-negotiable conventions (copy the COO course exactly)

1. **No YAML frontmatter on lessons or toolkit files.** Start with `# NN — Title`.
   (Only `index.md` files carry `---\ntitle: ...\n---`.)
2. **Second line of a lesson** is an italic one-paragraph outcome statement, in the COO's form:
   `_Phase N · <phase name> · <when>. After this lesson you can <concrete capabilities>._`
3. **Every lesson has an `## Explain-it-like-I'm-5` section**, second heading, 2–4 short paragraphs,
   using a concrete Indian small-business image (the COO used a highway dhaba). Use fresh images —
   do not reuse the dhaba.
4. **Numbered `## N. Section` headings** after that, and the **last section is `## N. Exercises`**,
   preceded by a `## N. At VSYST — applying this now` section. Exercises are numbered `N.1`, `N.2`,
   each 10–45 minutes, each producing a real artefact (a filled toolkit template, a decision-log
   entry, a filled workbook tab), each stating its artefact explicitly.
5. **Dense tables are the primary teaching device.** Most sections contain at least one comparison
   table with a "Fit at VSYST today" or "What it means for VSYST" column.
6. **Real citations, inline, as markdown links** — `([Source name](https://real-url), year)`.
   Every non-obvious factual claim, framework attribution, statistic, legal provision and book gets
   one. **Do web research** (WebSearch / WebFetch — load them with
   `ToolSearch("select:WebSearch,WebFetch")`) and verify the URLs you cite actually exist and say
   what you claim. Aim for **20–45 distinct real sources per lesson**. Never invent a URL.
7. **`**VERIFY LIVE**`** flag on every specific number, date, rate, threshold, form number, fee or
   price that a real decision would turn on — Indian statutory numbers and tax/funding rules change
   every Budget. Say who to verify with (CA / CS / lawyer / the vendor's page).
8. **Wiki-links use the bare basename**, Obsidian shortest-path style, with a pipe alias:
   `[[05-strategy-i-diagnosis-and-the-strategy-kernel|lesson 05]]`, `[[C04-strategy-kernel-one-pager|C04]]`.
   Cross-link generously to other CEO lessons, to CEO toolkit templates, and to the COO course.
9. **Voice:** direct, second person ("you"), plain English, no MBA fog, no motivational filler.
   Short declaratives. Name the trap before naming the technique. Indian context assumed throughout
   (₹ not $, GST/TDS/TCS, Companies Act 2013, MCA/ROC, DPIIT, Raipur/Chhattisgarh distances,
   WhatsApp as a real business channel). Convert any foreign benchmark to what it means at VSYST's
   scale — a company of three people, pre-revenue.
10. **Honesty rule:** where the honest answer is "this does not apply to VSYST yet", say so and say
    what the trigger would be. Where advice conflicts in the literature, present both sides with
    citations and then give the house call for VSYST.
11. **Never contradict the COO course.** The COO owns the operating system: cadence, SOPs, scorecard,
    compliance calendar, vendor register, hiring process, RACI/DoA below board level. The CEO course
    must hand those off by reference, and take the seat opposite: direction, capital, the exec team,
    the story, governance, and final judgment. Where the two courses meet (the CEO–COO contract,
    decision rights, the scorecard-vs-dashboard split, planning), say explicitly which course owns
    which artefact.
12. **Length:** a lesson is **7,000–12,000 words** of substance (the COO lessons run 30–70 KB of
    markdown; match that). A toolkit template is **1,200–2,500 words**. Do not pad; add depth.

## The full course structure (so your cross-links resolve)

Lessons, in `CEO-Docs/`:

| File                                                          | Title                                                                       |
| ------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `index.md`                                                    | CEO Docs — landing page                                                     |
| `00-course-map-and-timeline.md`                               | 00 — Course Map and Master Timeline                                         |
| `01-what-is-a-ceo.md`                                         | 01 — What Is a CEO?                                                         |
| `02-how-a-ceo-thinks.md`                                      | 02 — How a CEO Thinks                                                       |
| `03-the-ceo-core-value-and-the-founder-contracts.md`          | 03 — The CEO's Core Value and the Founder Contracts                         |
| `04-how-to-become-a-ceo-in-2026.md`                           | 04 — How to Become a CEO in 2026                                            |
| `05-strategy-i-diagnosis-and-the-strategy-kernel.md`          | 05 — Strategy I: Diagnosis and the Strategy Kernel                          |
| `06-strategy-ii-moats-positioning-and-the-business-model.md`  | 06 — Strategy II: Moats, Positioning and the Business Model                 |
| `07-customers-markets-and-founder-led-sales.md`               | 07 — Customers, Markets and Founder-Led Sales                               |
| `08-capital-runway-and-fundraising.md`                        | 08 — Capital, Runway and Fundraising                                        |
| `09-board-governance-and-the-directors-duties.md`             | 09 — Board, Governance and the Director's Duties                            |
| `10-building-the-team-hiring-equity-and-firing.md`            | 10 — Building the Team: Hiring, Equity and Firing                           |
| `11-culture-and-values-as-a-ceo-instrument.md`                | 11 — Culture and Values as a CEO Instrument                                 |
| `12-communication-the-ceo-as-chief-storyteller.md`            | 12 — Communication: The CEO as Chief Storyteller                            |
| `13-product-and-technology-leadership-for-a-technical-ceo.md` | 13 — Product and Technology Leadership for a Technical CEO                  |
| `14-partnerships-ecosystem-and-founder-relationships.md`      | 14 — Partnerships, Ecosystem and the Relationships Only a Founder Can Hold  |
| `15-the-ceo-operating-cadence-and-calendar.md`                | 15 — The CEO's Operating Cadence and Calendar                               |
| `16-decisions-delegation-and-not-being-the-bottleneck.md`     | 16 — Decisions, Delegation and Not Being the Bottleneck                     |
| `17-the-numbers-a-ceo-watches.md`                             | 17 — The Numbers a CEO Watches                                              |
| `18-risk-crisis-and-the-hard-things.md`                       | 18 — Risk, Crisis and the Hard Things                                       |
| `19-planning-okrs-and-capital-allocation.md`                  | 19 — Planning, OKRs and Capital Allocation                                  |
| `20-the-ceo-own-operating-system-and-succession.md`           | 20 — The CEO's Own Operating System, Succession and What Winning Looks Like |
| `21-reference-glossary-reading-list-and-sources.md`           | 21 — Reference: Glossary, Reading List and Sources                          |

Phases:

- **Phase 0 — Orientation** (`index`, `00`) — now
- **Phase 1 — Understand the Seat** (`01`–`04`) — Week 0
- **Phase 2 — The Outward Job: strategy, customers, capital, governance** (`05`–`09`) — Months 1–3
- **Phase 3 — The Inward Job: team, culture, comms, product, partners** (`10`–`14`) — Months 2–9
- **Phase 4 — Running the Company and Yourself** (`15`–`20`) — Months 6–24
- **Toolkit** (`toolkit/index` + C01–C30) and **Reference** (`21`) — always

Toolkit, in `CEO-Docs/toolkit/` (files are `CNN-kebab-title.md`):

| ID  | File                                                  | Title                                                 |
| --- | ----------------------------------------------------- | ----------------------------------------------------- |
| C01 | `C01-ceo-charter-and-90-day-plan.md`                  | CEO Charter and 90-Day Plan                           |
| C02 | `C02-founders-agreement-and-vesting-checklist.md`     | Founders' Agreement and Vesting Checklist             |
| C03 | `C03-decision-rights-matrix.md`                       | CEO ↔ COO ↔ Board Decision-Rights Matrix              |
| C04 | `C04-strategy-kernel-one-pager.md`                    | Strategy Kernel One-Pager                             |
| C05 | `C05-choice-cascade-worksheet.md`                     | Choice Cascade Worksheet (Where to Play / How to Win) |
| C06 | `C06-market-map-sizing-and-segments.md`               | Market Map: Sizing, Segments and Alternatives         |
| C07 | `C07-moat-and-seven-powers-audit.md`                  | Moat and 7 Powers Audit                               |
| C08 | `C08-positioning-and-messaging-canvas.md`             | Positioning and Messaging Canvas                      |
| C09 | `C09-icp-and-customer-discovery-guide.md`             | ICP and Customer-Discovery Interview Guide            |
| C10 | `C10-founder-led-sales-pipeline-and-script.md`        | Founder-Led Sales Pipeline, Script and Objection Bank |
| C11 | `C11-pricing-and-packaging-decision-sheet.md`         | Pricing and Packaging Decision Sheet                  |
| C12 | `C12-unit-economics-and-business-model-calculator.md` | Unit Economics and Business-Model Calculator          |
| C13 | `C13-runway-burn-and-scenario-planner.md`             | Runway, Burn and Scenario Planner                     |
| C14 | `C14-fundraise-readiness-and-data-room-index.md`      | Fundraise Readiness Checklist and Data-Room Index     |
| C15 | `C15-investor-narrative-and-deck-outline.md`          | Investor Narrative and Deck Outline                   |
| C16 | `C16-term-sheet-decoder-and-cap-table.md`             | Term-Sheet Decoder, Cap Table and Dilution Model      |
| C17 | `C17-board-pack-agenda-and-minutes.md`                | Board Pack, Agenda, Resolutions and Minutes           |
| C18 | `C18-director-duties-and-governance-checklist.md`     | Director Duties and Governance Checklist              |
| C19 | `C19-executive-hiring-scorecard-and-loop.md`          | Executive Hiring Scorecard and Interview Loop         |
| C20 | `C20-compensation-bands-and-esop-design.md`           | Compensation Bands and ESOP Design Sheet              |
| C21 | `C21-values-and-operating-principles-worksheet.md`    | Values and Operating-Principles Worksheet             |
| C22 | `C22-internal-comms-calendar-and-all-hands.md`        | Internal Comms Calendar and All-Hands Template        |
| C23 | `C23-stakeholder-and-investor-update.md`              | Monthly Stakeholder / Investor Update                 |
| C24 | `C24-crisis-comms-and-statement-kit.md`               | Crisis Comms and Incident Statement Kit               |
| C25 | `C25-product-bets-and-the-no-list.md`                 | Product Bets, Roadmap-as-Strategy and the No-List     |
| C26 | `C26-partnership-evaluation-and-mou-checklist.md`     | Partnership Evaluation and MoU Checklist              |
| C27 | `C27-ceo-weekly-template-and-calendar-audit.md`       | CEO Weekly Operating Template and Calendar Audit      |
| C28 | `C28-annual-plan-and-ceo-okr-sheet.md`                | Annual Plan and CEO-Level OKR Sheet                   |
| C29 | `C29-decision-journal-and-one-way-door-log.md`        | Decision Journal and One-Way-Door Log                 |
| C30 | `C30-pre-mortem-crisis-playbook-and-succession.md`    | Pre-Mortem, Crisis Playbook and Succession Plan       |

A workbook `vsyst-ceo-workbook.xlsx` will live in `toolkit/` with tabs named in the toolkit files.
Reference it as `[vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)` from toolkit files and
`[vsyst-ceo-workbook.xlsx](toolkit/vsyst-ceo-workbook.xlsx)` from lessons.
Workbook tab names you may reference: `Strategy Kernel`, `Market Map`, `Unit Economics`,
`Runway & Scenarios`, `Cap Table & Dilution`, `ESOP Pool`, `CEO Dashboard`, `Annual Plan & OKRs`,
`Decision Journal`, `Board Calendar`, `Pipeline`, `Comp Bands`, `Risk & Pre-Mortem`.

## Toolkit template file shape (copy T30/T05 exactly)

```
# CNN — <Title>

_Toolkit · fills exercise N.M in [[NN-lesson-file|NN — Lesson Title]] · Owner: <who> · Cadence: <when> · Workbook tab: `<Tab>` in [vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)._

## Purpose        (2–4 paragraphs: what it is, why it exists, cited provenance of the format)
## When to use    (bulleted triggers, with the VSYST-specific first trigger)
## How to fill (rules)   (numbered, 6–10 opinionated rules, cited where the rule comes from someone)
## Template      (a fenced code block or a markdown table — actually usable, pre-filled with VSYST rows where useful)
## Worked example — VSYST   (fill it in with plausible VSYST numbers, labelled illustrative)
## Common mistakes  (table or bullets)
## Related        (wiki-links to lessons and sibling templates)
```

## Output discipline

- Write the file(s) assigned to you with the Write tool at the exact path given. Create nothing else.
- Do not write a summary file, a README, or a "notes" file.
- Your final message back must be **under 200 words**: the path(s) written, word count of each,
  the number of distinct sources cited, and anything you deliberately left for a sibling lesson.
