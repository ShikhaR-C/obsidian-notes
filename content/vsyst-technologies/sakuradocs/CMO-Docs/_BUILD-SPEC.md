# CMO-Docs — Shared Build Spec (read this fully before writing anything)

You are one writer on a team building **CMO-Docs**, a **short, hands-on mini-course** that takes someone who
**knows nothing about marketing or sales** to the point where they can plan, run and measure marketing
campaigns for **DZZLO OMS**, and eventually launch large multi-district campaigns. It is the third sibling of
the finished **COO-Docs** and **CEO-Docs** courses in the same vault. Match their **voice and conventions**
exactly — but NOT their length. The owner's brief is explicit: **"keep the tutorial short and to the point."**

## Paths

- Vault root: `/Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/obsidian-notes/content/vsyst-technologies`
- Write into: `<vault>/sakuradocs/CMO-Docs/` (lessons) or `<vault>/sakuradocs/CMO-Docs/toolkit/` (templates)
- Reference courses to imitate for voice: `<vault>/sakuradocs/COO-Docs/` and `<vault>/sakuradocs/CEO-Docs/`
- **Before writing, read for voice:** `COO-Docs/01-what-is-a-coo.md` (first ~120 lines is enough) and, if you
  are writing a template, `COO-Docs/toolkit/T05-kpi-scorecard.md` (first ~80 lines).
- **Existing research you MUST read (the parts relevant to your lesson) and link to, never repeat:**
  - `<vault>/docs/learning/company/` — the DZZLO Company Building Playbook (14 docs, research date 2026-04-15).
    Most relevant: `00_OVERVIEW.md` (product facts), `11_EDUCATION_GAP.md` (two-sided cold start),
    `12_OWNER_ACQUISITION.md` (dealer persona, channel ranking, 90-day playbook), `06_REFERRAL_PROGRAM.md`
    ("Dealer Dost"), `04_LEAD_MAGNETS.md`, `03_LAUNCH_CHECKLIST.md`, `09_PRODUCT_VS_SALES.md`,
    `13_REVENUE_GENERATION.md` (§7 when to hire sales), `05_COLD_EMAIL_SEQUENCE.md`, `RESEARCH_SOURCES.md`.
  - `<vault>/docs/learning/marketing/transporters/` — the transporter-side marketing & strategy vault (April 2026):
    `02_Marketing_Tutorial.md`, `04_Target_Customer_Transporters.md`, `05_Beachhead_and_Expansion.md`,
    `06_Brand_Architecture.md`, `07_Positioning_and_Messaging.md`, `08_Marketing_Strategy.md`,
    `09_Sales_Strategy.md`, `12_Roadmap_Phases.md`, `13_Metrics_and_KPIs.md`, `99_References.md`.
  - `<vault>/docs/learning/app-store-economics/08-dzzlo-subscription-strategy.md` — the DECIDED pricing direction.
  - `<vault>/correspondence/IOCL_Amey_31072026/discussion-document.md` — the live OMC (IOCL) conversation.
  - `<vault>/sakuradocs/CEO-Docs/07-customers-markets-and-founder-led-sales.md` and toolkit `C06`, `C08`, `C09`,
    `C10`, `C11` — the CEO course already covers ICP theory, discovery interviews, positioning canvas, the
    founder-led sales pipeline in depth. This course is the **practical, do-it-this-week layer on top**; link there
    for depth.
  - **Do not edit anything** under `docs/learning/marketing/VSYST Technologies Pvt. Ltd./` (read-only vault).

## The company (get these right — they are load-bearing)

- **VSYST Technologies Pvt. Ltd.**, Raipur, Chhattisgarh. Indian Private Limited company. Three founder-directors,
  family-founded: a **technical CEO who ships code**, a **domain-expert director** (fuel distribution), a third
  director. **No marketing person, no sales person, no CMO. Nobody on the team has done marketing.**
- **Bootstrapped, pre-revenue.** No outside capital. Marketing budget is founder time plus **₹30–50k/month**.
- **One product: DZZLO OMS** — multi-tenant, mobile-first Order Management System for Indian fuel distribution:
  petrol-pump dealers, lubricant distributors, bulk-diesel operators. Live on both app stores. India-only.
- **Two user worlds, one product.** The **dealer** (petrol pump owner) owns the tenant and pays. The dealer's
  **B2B customers** (transport fleets, factories, hospitals, contractors, mines) use the same app free — they
  confirm rates, place orders, see their ledger, settle vouchers. **The product is only useful when both sides use
  it** (the rate-confirmation window, order flow and shared ledger need the customer to participate); but it must
  and does deliver **single-player value** to the dealer alone (invoicing, GST/TCS, credit ledger, DIP tank
  reconciliation, driver OTP dispatch).
- **The product loop:** dealer sets next-day rates → customer confirms in the **10 PM–6 AM window** (unconfirmed
  rates auto-lock at 6 AM) → order → dispatch with **driver OTP** → three-tier invoice (PRODUCT / CASH_REIMBURSE /
  GST; **TCS auto-added past ₹50L** turnover) → voucher/payment/reconciliation. DIP module: tank dips, density,
  decants, inspection log. Onboarding is **phone-OTP invite**, not email/password.
- **Customer-side reality today:** the customer uses the same React Native app via the invite flow (roles
  CPrimary/CAdmin/COrder/CAccount/CView). The **WhatsApp-first, zero-install customer flow** recommended in
  `11_EDUCATION_GAP.md` §7–8 is the intended direction, **not built yet**. Say so honestly wherever it matters.
- **Decided pricing direction (2026-07-29, do not re-litigate):** every company pays **per GSTIN**; users, staff,
  drivers are **unlimited and free**; **billing is web-only** (no app-store commission), app gated server-side;
  customer firms ride free for core trading now, may pay later for fleet features. Tier sheet under sign-off:
  **₹599 / ₹1,799 / ₹4,999 + Enterprise, ex-GST, 14-day no-card trial** — always flag **VERIFY LIVE (owner
  sign-off pending)**. **Never quote the older "₹999–2,499/mo hybrid" numbers** from `company/README.md`.
- **Brand:** **DZZLO** = product/customer-facing brand; **VSYST Technologies** = corporate. (Transporters vault Q4.)
- **Live relationships:** **IOCL** (oil marketing company) discussions via a contact named Amey — see
  correspondence; **Easebuzz** payment-gateway onboarding in progress. Both are marketing assets.
- **Geography:** beachhead = **Raipur district** (pumps within ~60 km), then the **NH-53 corridor Raipur → Nagpur**
  (transporters vault Q2), then other Chhattisgarh districts, then neighbouring states.
- **Stack the marketer will actually touch:** WhatsApp Business, Google Business Profile, a landing page,
  Play Store / App Store listings, YouTube (Hindi demos), ERPNext CRM (intended system of record; a Google Sheet
  until then), Figma/Canva, this Obsidian/Quartz vault.

## House calls (every writer uses these; do not contradict them)

- **HC1 — Hire or DIY?** **Founders do marketing and sales themselves for the first 100 dealers.** Do **not** hire a
  CMO. The first 100 customers are R&D, not revenue; a CMO without a proven channel builds brand nobody asked for
  and costs the whole runway. Hire a **field sales / marketing associate** (Raipur, roughly ₹20–35k/month —
  VERIFY LIVE) when **all three** hold: ≥10 paying dealers, one channel has produced ≥3 of them repeatably, and
  founders' selling time exceeds ~15 h/week. Hire a **marketing lead** around **₹50L–1 Cr ARR** or after a seed
  round. A **CMO title** is a post-Series-A / ₹5 Cr+ ARR question. Lesson 01 states this as the house answer;
  lesson 12 details the hiring ladder.
- **HC2 — Sell to the dealer, seed the customer.** The dealer is the buyer and the channel to the customer. **Never
  market to transporters/factories cold in a district where no dealer is live.** The customer-side pitch is
  delivered **by the dealer, with our material** ("your supplier is on DZZLO — confirm tomorrow's rate, see your
  ledger, no more rate disputes, no more 'we never agreed to that'"). Customer-side marketing becomes a direct
  motion only once several dealers in a district are live (the traveling-customer flywheel).
- **HC3 — Atomic network.** Saturate Raipur district (target ~60% of ICP pumps within 60 km) before the next
  district. "Huge campaigns" are the district playbook repeated in N districts at once — never before one district
  has a measured CAC and a repeatable script.
- **HC4 — Channel order** (from `12_OWNER_ACQUISITION.md` §5): **referral > OMC territory-manager / IOCL
  relationship > dealer association > CA/tax-consultant > field visits > WhatsApp community > content/SEO >
  paid ads.** No paid ads before ~50 dealers and a landing page with real proof. Cold email/LinkedIn are for
  second-generation owners only.
- **HC5 — The message.** Lead with **fear of loss + a rupee number + dealer-next-door proof**, not features.
  Owners buy protection: rate disputes, unbilled credit, shortage/variance, GST/TCS mistakes, receivables ageing.
  Hindi (and Chhattisgarhi where natural) + English. "The son influences; the father signs" — write for both.
- **HC6 — Segment × message × channel.** The owner's question "how do we clearly tell which business from where
  so that they opt for our product" is answered with a **matrix**: for each segment (petrol-pump dealer,
  bulk-diesel operator, lubricant distributor, transporter fleet, factory/plant, contractor/mine, hospital/
  institution) — their pain in their words, the one line we say, the proof we show, the channel we reach them
  through, and who must say yes (father/son/accountant/fleet manager). Lessons 03 and 04 build it; M02/M04 hold it.
- **HC7 — Budget** ₹30–50k/month bootstrap marketing spend; founder time is the main cost. Every campaign has a
  brief, a budget, a number it moves and a post-mortem (M12).
- **HC8 — The marketing scorecard** (weekly, 8 numbers, M13): pump visits, demos, trials started, dealers
  activated (≥1 customer linked + ≥1 invoice in 14 days), customers activated per dealer, referrals asked/received,
  WhatsApp reply rate, CAC by channel. This is the **marketing** scorecard; the company scorecard is the COO's
  ([[T05-kpi-scorecard|T05]]) — the marketing rows feed it.
- **HC9 — The campaign ladder:** 1 dealer → 10 dealers (the founding ten) → 100 (Raipur district) → corridor
  (NH-53) → state → multi-state. Each rung has an entry test and a template.
- **HC10 — Sales-assisted, product-retained.** Pure product-led growth will not work for Indian fuel SMEs; pure
  sales without activation will churn. Marketing owns the funnel **through activation of both sides**.

## What this course owns vs. the neighbours (never contradict them)

| Owns                                                                                         | Course                          |
| -------------------------------------------------------------------------------------------- | ------------------------------- |
| Strategy kernel, ICP theory, positioning canvas, pricing decision, founder-led sales theory | CEO-Docs (05–07, C04–C12)       |
| Operating cadence, CRM/ERPNext, support SOP, hiring process, scorecard mechanics, RACI       | COO-Docs (08–11, 16, T05, T10)  |
| **Demand generation, messaging in the field, channels, the pump-visit motion, onboarding both sides, referrals/partners, content & WhatsApp, campaigns, marketing metrics, marketing hiring** | **CMO-Docs (this course)** |

Where the courses meet, say which artefact lives where (e.g. "the ICP definition is [[C09-icp-and-customer-discovery-guide|C09]]; M02 is the one-page field card you carry to the pump").

## The governing idea

> **Marketing is finding the people whose problem you solve, saying it in their words where they already are,
> and making it easy to say yes. Sales is the conversation that finishes it. For a two-sided product: sell to
> the dealer, seed the customer, and count both.**

The recurring rule (the CMO course's counterpart to the COO's "mechanisms, not intentions" and the CEO's
"decide it, write down why"):

```
Nobody has bought it yet      -> go to the pump yourself, this week      (lesson 06)
One has bought it             -> get the proof and the referral           (lesson 08)
Ten have bought it            -> write the script down, measure the channel (lessons 10–11)
A hundred have bought it      -> hire, repeat the district, then go big   (lesson 12)
And in every case             -> both sides live, or it doesn't count     (lessons 02, 07)
```

## Non-negotiable conventions (copy the COO/CEO courses exactly)

1. **No YAML frontmatter on lessons or toolkit files.** Start with `# NN — Title`. Only `index.md` files carry
   `---\ntitle: ...\n---`.
2. **Second line of a lesson** is an italic one-paragraph outcome statement:
   `_Phase N · <phase name> · <when>. After this lesson you can <concrete capabilities>._`
3. **Every lesson has an `## Explain-it-like-I'm-5` section** as the second heading, 2–3 short paragraphs, using a
   concrete Indian small-business image. **Do not reuse the dhaba** (COO) — use fresh images (a kirana, a
   sabzi mandi stall, a tempo stand, a mobile-recharge shop, a tractor dealer, a wedding band, a tiffin service…).
4. **Numbered `## N. Section` headings** after that. **Last section is `## N. Exercises`**, preceded by
   `## N. At VSYST — applying this now`. Exercises are numbered `N.1`, `N.2`…, each **10–45 minutes**, each
   producing a **real artefact** (a filled toolkit template, a list, a script, a workbook tab, a sent message) and
   stating that artefact explicitly. 2–4 exercises per lesson.
5. **Dense tables are the primary teaching device.** Most sections contain at least one table with a "Fit at VSYST
   today" / "What it means for DZZLO" / "Do this" column.
6. **Real citations, inline, as markdown links** — `([Source name](https://real-url), year)`. Every non-obvious
   claim, framework, statistic or book gets one. Do web research (`ToolSearch("select:WebSearch,WebFetch")`) and
   **verify the URLs exist and say what you claim**. Target **8–15 distinct real sources per lesson**, 3–6 per
   template. Reuse sources already verified in `company/RESEARCH_SOURCES.md` and `transporters/99_References.md`
   freely. **Never invent a URL.** Cite Indian sources where they exist (PPAC, MoPNG, AIPDA/FAIPT, OMC sites,
   Meta/WhatsApp Business India pages, SaaSBoomi, Inc42, YourStory).
7. **`**VERIFY LIVE**`** on every specific number a decision would turn on — prices, salaries, CAC estimates,
   association fees, ad costs, pump counts, WhatsApp API pricing. Say who/what to verify with.
8. **Wiki-links use the bare basename** with a pipe alias: `[[03-who-exactly-icp-personas-and-the-target-list|lesson 03]]`,
   `[[M04-positioning-and-message-house|M04]]`, `[[C09-icp-and-customer-discovery-guide|C09]]`,
   `[[T05-kpi-scorecard|T05]]`, `[[12_OWNER_ACQUISITION|Owner Acquisition]]`, `[[08_Marketing_Strategy|transporters 08]]`,
   `[[08-dzzlo-subscription-strategy|subscription strategy]]`, `[[CEO-Docs/index|CEO Docs]]`, `[[COO-Docs/index|COO Docs]]`,
   `[[company/README|Company Building Playbook]]`, `[[00_README|transporters vault]]` (for the transporters index use
   `[[transporters/00_README|transporters vault]]` to disambiguate). Cross-link generously.
9. **Voice:** direct, second person, plain English, **no marketing jargon without a one-line definition the first
   time** (funnel, ICP, CAC, activation, conversion, positioning, lead, MQL/SQL, churn, NPS…). Short declaratives.
   Name the trap before the technique. Indian context throughout (₹, GST/TCS, WhatsApp as a real channel, Raipur
   distances, the family-business father/son dynamic). Convert foreign benchmarks to VSYST's scale — three people,
   pre-revenue, ₹30–50k/month.
10. **Honesty rule:** where the honest answer is "not yet" (paid ads, PR, brand campaigns, a CMO, SEO), say so and
    give the trigger. Where sources disagree, give both and the house call.
11. **Length — this is the rule that differs from the sibling courses:** a lesson is **1,800–3,000 words** of
    substance (**hard cap 3,200**). A toolkit template is **700–1,200 words**. The reference lesson (13) may run to
    3,500. Cut anything that does not change what the reader does this week. Depth over padding; brevity over depth.
12. **Every lesson answers "what do I do this week?"** in its At-VSYST section, with named owners (CEO / domain
    director / third director) and the template to fill.

## Course structure (so your cross-links resolve)

Lessons in `CMO-Docs/`:

| File                                                              | Title                                                                       | Phase / when              |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------- |
| `index.md`                                                        | CMO Docs — landing page                                                     | 0 · now                   |
| `00-course-map-and-timeline.md`                                   | 00 — Course Map and the 12-Month Marketing Timeline                         | 0 · now                   |
| `01-what-marketing-and-sales-actually-are.md`                     | 01 — What Marketing and Sales Actually Are (and Who Should Do Them Here)    | 1 · Understand · Week 0   |
| `02-the-two-sided-problem-sell-to-the-dealer-seed-the-customer.md`| 02 — The Two-Sided Problem: Sell to the Dealer, Seed the Customer           | 1 · Understand · Week 0   |
| `03-who-exactly-icp-personas-and-the-target-list.md`              | 03 — Who Exactly: ICP, Personas and the Named Target List                   | 2 · Aim · Week 1          |
| `04-the-message-positioning-and-the-one-line-pitch.md`            | 04 — The Message: Positioning, Segment-Specific Pitches and Objections      | 2 · Aim · Week 1          |
| `05-channels-where-to-find-them-and-in-what-order.md`             | 05 — Channels: Where to Find Them, in What Order                            | 3 · Go to Market · Wk 2–12|
| `06-founder-led-sales-the-pump-visit-demo-and-close.md`           | 06 — Founder-Led Sales: The Pump Visit, the Demo and the Close              | 3 · Go to Market · Wk 2–12|
| `07-onboarding-and-activation-getting-both-sides-live.md`         | 07 — Onboarding and Activation: Getting Both Sides Live                     | 3 · Go to Market · Wk 2–12|
| `08-referrals-associations-and-partners-the-warm-engine.md`       | 08 — Referrals, Associations, OMCs and Partners: The Warm Engine            | 3 · Go to Market · Wk 2–12|
| `09-content-whatsapp-and-the-minimum-digital-presence.md`         | 09 — Content, WhatsApp and the Minimum Digital Presence                     | 4 · Scale · Months 3–12   |
| `10-campaigns-planning-running-and-measuring-one.md`              | 10 — Campaigns: Planning, Running and Measuring One (then Ten)              | 4 · Scale · Months 3–12   |
| `11-metrics-budget-and-the-marketing-scorecard.md`                | 11 — Metrics, Budget, CAC and the Marketing Scorecard                       | 4 · Scale · Months 3–12   |
| `12-scaling-hiring-and-launching-the-big-campaign.md`             | 12 — Scaling: Hiring, Agencies, Brand and Launching the Big Campaign        | 4 · Scale · Months 6–18   |
| `13-reference-glossary-reading-list-and-sources.md`               | 13 — Reference: Glossary, Reading List and Sources                          | always                    |

Phases: **0 Orientation** (index, 00) · **1 Understand** (01–02, Week 0) · **2 Aim** (03–04, Week 1) ·
**3 Go to Market — the "Raipur 100" campaign** (05–08, Weeks 2–12) · **4 Scale** (09–12, Months 3–18) ·
**Toolkit** (toolkit/index + M01–M14) · **Reference** (13).

Toolkit in `CMO-Docs/toolkit/` (files `MNN-kebab-title.md`; each has: title line, italic line
`_Toolkit · fills the exercises in [[lesson]] · Owner: … · Cadence: … · Workbook tab: …_`, then
`## Purpose`, `## When to use`, `## How to fill (rules)`, `## Template`, `## Worked example — VSYST (illustrative)`,
`## Common mistakes`, `## Related`):

| ID  | File                                                | Title                                                          | Fills lesson |
| --- | --------------------------------------------------- | -------------------------------------------------------------- | ------------ |
| M01 | `M01-marketing-charter-and-90-day-plan.md`          | Marketing Charter, Hire-or-DIY Decision and 90-Day Plan        | 01           |
| M02 | `M02-icp-and-persona-field-cards.md`                | ICP and Persona Field Cards (dealer side + customer side)      | 03           |
| M03 | `M03-target-list-builder.md`                        | The Named Target List (Raipur 100) — sources and columns       | 03           |
| M04 | `M04-positioning-and-message-house.md`              | Positioning Statement and the Segment × Message × Channel Matrix | 04         |
| M05 | `M05-pitch-scripts-and-objection-handling.md`       | Pitch Scripts (30-second, pump visit, WhatsApp opener, phone, customer-side) and Objections | 04, 06 |
| M06 | `M06-demo-flow-and-pilot-offer-sheet.md`            | The 10-Minute Demo Flow and the Pilot Offer Sheet              | 06           |
| M07 | `M07-sales-pipeline-tracker.md`                     | Sales Pipeline Tracker (stages, columns, ERPNext CRM mapping)  | 06           |
| M08 | `M08-onboarding-and-activation-checklist.md`        | Two-Sided Onboarding and Activation Checklist (dealer 14 days + customer invites) | 07 |
| M09 | `M09-referral-program-one-pager.md`                 | "Dealer Dost" Referral Program One-Pager and Ask Script        | 08           |
| M10 | `M10-partner-and-channel-playbook.md`               | Partner Playbook: OMC TM, Association, CA, Hardware Vendor — outreach templates | 05, 08 |
| M11 | `M11-content-and-whatsapp-calendar.md`              | Content and WhatsApp Calendar + Landing-Page Checklist         | 09           |
| M12 | `M12-campaign-brief-budget-and-post-mortem.md`      | One-Page Campaign Brief, Budget and Post-Mortem                | 10           |
| M13 | `M13-marketing-scorecard-and-cac-calculator.md`     | Weekly Marketing Scorecard and CAC / Payback Calculator        | 11           |
| M14 | `M14-marketing-hiring-scorecard-and-role-charters.md`| Marketing Hiring: Role Charters, Comp Bands, Scorecards (field associate → marketing lead → CMO) | 12 |

Workbook: `toolkit/vsyst-cmo-workbook.xlsx` (built last by script) with tabs `Target List`, `Pipeline`,
`Marketing Scorecard`, `CAC & Payback`, `Campaign Budget`, `Content Calendar`, `Referral Tracker`,
`Channel Experiments`. Reference tabs by name in templates where relevant.

## Deliverable check before you finish

- Word count within the band. `wc -w` it.
- Every `[[link]]` you wrote points to a file in the structure tables above or to an existing vault file.
- Every URL you cite was fetched or is in `RESEARCH_SOURCES.md` / `99_References.md`.
- The lesson answers, in its At-VSYST section, what the three founders do **this week** and which template they fill.
- No contradiction with the house calls above.
