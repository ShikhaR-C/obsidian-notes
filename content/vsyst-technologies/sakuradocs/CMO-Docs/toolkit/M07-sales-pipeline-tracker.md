# M07 — Sales Pipeline Tracker

_Toolkit · fills the exercises in [[06-founder-led-sales-the-pump-visit-demo-and-close|06 — Founder-Led Sales: The Pump Visit, the Demo and the Close]] · Owner: domain director owns the sheet; one internal owner per row · Cadence: Monday 10-minute pipeline review · Workbook tab: `Pipeline` in [vsyst-cmo-workbook.xlsx](vsyst-cmo-workbook.xlsx)._

## Purpose

One sheet, answering three questions every Monday: **where is every named pump, what happens next, and how many will be paying by week 12.** Without it, visits are anecdotes and [[M13-marketing-scorecard-and-cac-calculator|M13]] has nothing to count. With it, the largest loss in B2B selling becomes visible: **40–60% of an average pipeline ends in "no decision"** — not lost to a rival, gone quiet ([Matthew Dixon, via 6sense](https://6sense.com/talkingsense/sellers-are-losing-up-to-60-of-pipeline-to-no-decision-heres-how-to-fix-that/)). The sheet makes quiet rows loud.

## When to use

- **The same evening as every visit**, in the car, five rows at a time. A visit logged three days later is fiction.
- **Every Monday, ten minutes**, all three founders, before the ops meeting.
- **Until ERPNext goes live** (§D). Then the sheet dies — no parallel spreadsheet.

## How to fill (rules)

1. **A row is a pump**, carried from [[M03-target-list-builder|M03]] with the same pump and owner names.
2. **A stage moves only on its exit test.** A verbal yes, a _"WhatsApp pe bhej dijiye"_, a meeting with the manager: none of these move anything.
3. **Never slide back quietly.** A cold `Trial started` row becomes `Lost` with a reason, not `Demoed` again.
4. **Every row carries a next action and a date.** No date, no row.
5. **Objection heard is verbatim, in his language** — it feeds [[M05-pitch-scripts-and-objection-handling|M05]]. A paraphrase feeds nothing.
6. **Money cells are flagged:** plan/tier and MRR carry **VERIFY LIVE — owner sign-off pending**; never the older ₹999–2,499 numbers.

## Template

**A. Stages and exit tests** — the eight from [[06-founder-led-sales-the-pump-visit-demo-and-close|lesson 06]] §1, plus Lost. Do not add a stage.

| Stage | Exit test — the checkable event |
| --- | --- |
| **Target** | Named pump, owner, phone, source, ICP score in [[M03-target-list-builder\|M03]] |
| **Contacted** | A **two-way** exchange. A broadcast is not contact |
| **Visited** | You stood at his pump and the **owner** was there |
| **Demoed** | Ten minutes on **his** customers and **his** rupee figures, decision-maker present ([[M06-demo-flow-and-pilot-offer-sheet\|M06]]) |
| **Trial started** | Tenant created, balances entered, start and day-14 dates in his thread |
| **Paying** | Money received against a VSYST GST invoice |
| **Activated (both sides)** | ≥1 customer firm linked **and** ≥1 invoice within 14 days |
| **Referring** | A **named** introduction that reached a two-way conversation |
| **Lost** | A no, or a next date blank for 30 days. Reason verbatim |

**B. The `Pipeline` tab — fourteen columns, in order**

`Pump` · `Owner (dealer)` · `Segment` · `Source channel` · `Stage` · `Last touch` · `Next action + date` · `Objection heard` · `Trial start` · `Activation date` · `Plan / tier` · `MRR` · `Referral asked?` · `Owner (ours)`

Six need a rule. **Segment**: pump dealer / bulk diesel / lubricant distributor. **Source channel**: referral / OMC TM / association / CA / field visit / WhatsApp / inbound — mandatory, the only input to CAC by channel. **Last touch**: over 14 days is stalled. **Plan / tier**: ₹599 / ₹1,799 / ₹4,999 / Enterprise, ex-GST, per GSTIN, billing web-only — **VERIFY LIVE**. **Referral asked?**: Y/N and a date, asked at activation, never at signature. **Owner (ours)**: one name — CEO, domain or third director, never "us".

**C. The Monday review — ten minutes, in this order**

1. **Stalled rows first** (last touch >14 days): each gets a decision — a next action with a date, or `Lost`. Nothing leaves "still thinking" — this is the whole defence against the 40–60%.
2. **Blank next actions** — fill or kill.
3. **Stage moves since last Monday**, read aloud against the exit test.
4. **The five counts** to the scorecard: visits, demos, trials, paying, activated ([[M13-marketing-scorecard-and-cac-calculator|M13]] → [[T05-kpi-scorecard|T05]]).
5. **Conversion math**, off your own rows:

| Ratio | Formula | Benchmark |
| --- | --- | --- |
| Demo → trial | trial started ÷ demoed | 40–50% (lesson 06 §1) |
| **Demo → paying** | paying ÷ demoed | ~32% SMB ([Optifai](https://optif.ai/learn/questions/demo-to-close-conversion-rate/)) |
| Trial → paying | paying ÷ trial started | 35–45%; beat the unassisted 18.2% ([First Page Sage](https://firstpagesage.com/seo-blog/saas-free-trial-conversion-rate-benchmarks/)) |
| Paying → activated | activated ÷ paying | 60–75% — the rung marketing owns alone (HC10) |
| Touches per win | follow-ups ÷ paying | five ([Cirrus Insight](https://www.cirrusinsight.com/blog/sales-follow-up-statistics)) |

After 20 demos, replace every benchmark with your own. **VERIFY LIVE.**

**D. ERPNext mapping — Lead → Opportunity → Customer**

| Sheet stage | ERPNext |
| --- | --- |
| Target, Contacted | **Lead**, walking Lead → Open → Replied ([ERPNext](https://docs.frappe.io/erpnext/lead)) |
| Visited, Demoed, Trial started | **Opportunity**, raised against the Lead ([ERPNext](https://docs.frappe.io/erpnext/opportunity)) |
| Paying | **Customer** + Sales Invoice + Payment Entry; the Lead reads `Converted` |
| Activated, Referring | No equivalent — marketing-only columns |

[[11-revenue-operations-and-partnerships|COO lesson 11]] owns the CRM mechanics — validation, lost reasons, the no-parallel-spreadsheet rule. Marketing owns only what ERPNext lacks: source channel, activation date, referral asked, objection heard.

## Worked example — VSYST (illustrative)

**All five rows are fictional.**

| Pump | Source | Stage | Last touch | Next action + date | Objection heard |
| --- | --- | --- | --- | --- | --- |
| Maa Danteshwari Fuels | referral | **Paying** ₹1,799 **VL** | 25 Aug | Activation check — 29 Aug | — |
| Highway Auto Centre | OMC TM | **Trial started** | 26 Aug | Day-14 meeting — 09 Sep | _"munim ko sikhana padega"_ |
| Shree Balaji Filling | CA | **Demoed** | 21 Aug | Re-demo with the son — 02 Sep | _"beta dekhega"_ |
| Ring Road Fuels | field visit | **Visited** | 08 Aug | *(blank)* | _"abhi Tally theek hai"_ |
| City Point Petroleum | field visit | **Lost** | 04 Aug | — | _"malik Dubai mein hain"_ |

Row 4 is the point: 19 days stale, no next action — Monday books a date or writes `Lost`, and never discusses it a third time. Row 1 is half won; `Paying` is not `Activated`, and the 29 Aug check decides whether it counts on [[M13-marketing-scorecard-and-cac-calculator|M13]]. Across the five, demo → paying is 33% — respectable, on a sample far too small to believe.

## Common mistakes

| Mistake | The fix |
| --- | --- |
| Updating on Sunday, from memory | Same evening, in the car |
| Nursing a stalled row for months | Over 14 days: decide or drop |
| Paraphrasing the objection | Verbatim, or [[M05-pitch-scripts-and-objection-handling\|M05]] never improves |
| Counting `Paying` as the finish | Both sides live, or it does not count (HC10) |
| Blank source channel | Then CAC by channel is unknowable |

## Related

Lesson [[06-founder-led-sales-the-pump-visit-demo-and-close|06]] · [[M05-pitch-scripts-and-objection-handling|M05]], [[M06-demo-flow-and-pilot-offer-sheet|M06]], [[M13-marketing-scorecard-and-cac-calculator|M13]] · [[C10-founder-led-sales-pipeline-and-script|C10]] · [[11-revenue-operations-and-partnerships|COO 11]], [[T05-kpi-scorecard|T05]] · [[CMO-Docs/toolkit/index|CMO Toolkit]]
