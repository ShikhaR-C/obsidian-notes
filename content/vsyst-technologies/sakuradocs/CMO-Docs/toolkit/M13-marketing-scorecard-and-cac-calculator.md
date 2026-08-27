# M13 — Weekly Marketing Scorecard and CAC / Payback Calculator

_Toolkit · fills the exercises in [[11-metrics-budget-and-the-marketing-scorecard|11 — Metrics, Budget, CAC and the Marketing Scorecard]] · Owner: CEO owns the sheet and the `CAC & Payback` tab; one named owner per row · Cadence: filled Monday before the COO ops meeting — rows by 09:30, huddle 09:40, ops meeting 10:00 · Workbook tabs: `Marketing Scorecard` and `CAC & Payback` in [vsyst-cmo-workbook.xlsx](vsyst-cmo-workbook.xlsx)._

## Purpose

Two instruments. The **scorecard** is marketing's weekly instrument panel — eight numbers (HC8), one owner each, thirteen weeks trailing, deliberately the same shape as the company scorecard [[T05-kpi-scorecard|T05]]: a second visual language for one company makes numbers harder to read. The form is EOS's weekly Scorecard of five to fifteen numbers ([EOS](https://www.eosworldwide.com/level-10-meeting)), read as Amazon reads its WBR — arguing about **controllable input metrics**, not outputs you can only watch ([Commoncog](https://commoncog.com/the-amazon-weekly-business-review/)). The **calculator** turns cash and founder hours into CAC per channel and payback in months.

## When to use

- **Open both tabs the week you have a pipeline sheet**, before the queries behind rows 4, 5 and 8 exist. A blank cell with a reason beats a filled cell with a guess.
- **Scorecard every Monday; channel review the first Monday of the month.** Goals, red lines and the imputed rate move only at quarterly planning ([[T19-quarterly-plan-and-review|T19]]).
- **M13 is the standing sheet**; per-campaign budgets and post-mortems live in [[M12-campaign-brief-budget-and-post-mortem|M12]].

## How to fill (rules)

1. **Filled by Monday 09:30.** The 09:40 huddle reads the sheet, never builds it. No sheet, no huddle.
2. **One owner enters each number personally**, not a scribe. Late twice means the owner is wrong or the query too hard.
3. **No metric without a source** — the Mongo aggregation, tab or stats screen, named in the Source column. Otherwise it is an opinion.
4. **Eight rows, no more** (HC8); **thirteen weeks trailing**, history never overwritten. **RAG comes from three cells:** Direction, Goal, Red line. Rows 1–7 are inputs you control this week; row 8 is the lagging row the rest exist for.
5. **On track / off track only. Red two weeks running escalates automatically** onto the COO's issues list for the 10:00 ops meeting ([[T03-weekly-ops-meeting-agenda|T03]]).
6. **The feed into T05 is mechanical: row 2 *is* T05 row 2, row 4 *is* T05 row 3, row 5 feeds T05 rows 4 and 5** — entered once here, read there. Row 8 goes up quarterly into [[C12-unit-economics-and-business-model-calculator|C12]].
7. **Ownership.** This course owns the **marketing** scorecard, CAC by channel and the budget lines; COO-Docs owns the **company** scorecard and the mechanics ([[16-metrics-dashboards-and-scorecards|COO 16]]); CEO-Docs owns the **binding definitions** ([[17-the-numbers-a-ceo-watches|CEO 17]] §6.6). **If the two disagree, CEO 17 wins and M13 is wrong.**

## Template

### A. `Marketing Scorecard` tab

W4…W13 omitted for width. Goals and red lines illustrative — **VERIFY LIVE** at quarterly planning.

| # | Metric (HC8) | Owner | Source | Dir. | Goal | Red | W1 | W2 | W3 | … |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Pump visits | Domain dir. | [[M07-sales-pipeline-tracker\|M07]] Visit Log | higher | 8 | 4 | | | | |
| 2 | Demos done | Domain dir. | M07, stage `Demo done` | higher | 5 | 2 | | | | |
| 3 | Trials started | Third dir. | Mongo `dealer_msts` | higher | 3 | 1 | | | | |
| 4 | Dealers activated (≥1 customer linked + ≥1 invoice, 14 days) | Third dir. | Saved Mongo aggregation | higher | 2 | 0 | | | | |
| 5 | Customers activated per activated dealer | Third dir. | `dealer_custs` × `rate_msts` | higher | ≥3 | 1 | | | | |
| 6 | Referrals asked / received | Domain dir. | `Referral Tracker`, [[M09-referral-program-one-pager\|M09]] | higher | 5 / 2 | 2 / 0 | | | | |
| 7 | WhatsApp reply rate | Third dir. | WhatsApp Business → Stats | higher | ≥40% | 20% | | | | |
| 8 | CAC by channel (rolling 90 days) | CEO | `CAC & Payback` tab | **lower** | best ≤ ₹8,000 | ₹20,000 | | | | |

Rows 4 and 5 need an aggregation only the technical CEO can write, breaking rule 2. Do not reassign the row — save the query as a named script.

### B. `CAC & Payback` tab — inputs

One row per channel per quarter; never a row called "marketing." **Cash spend ₹** (one channel only) · **founder hours**, time-boxed, logged same day · **travel & fuel ₹**, kept separate so channels compare · **new paying dealers** from that channel ([[M07-sales-pipeline-tracker|M07]] source field; invoice raised **and** money received).

> **Imputed rate — house rule ₹400/hour.** (₹30,000 salary + ~₹8,000 travel/phone for the field associate we would hire instead) ÷ 22 days ÷ 8 h ≈ ₹216, **doubled** because the founder also demos, prices and closes. **VERIFY LIVE** against Raipur associate comp (HC1). Set once a year, never mid-quarter, or CAC moves for reasons unrelated to marketing ([Tango](https://www.tango.vc/p/early-cac)).

### C. `CAC & Payback` tab — outputs and formulas

| Output | Formula | Assumption |
| --- | --- | --- |
| Total channel cost | cash + (hours × ₹400) + travel | — |
| **CAC (channel)** | total cost ÷ paying dealers from it | Real at **≥3 dealers** |
| Blended CAC | Σ cost ÷ Σ paying dealers | Sanity check only — it "doesn't inform how well your paid campaigns are working" ([a16z](https://a16z.com/16-startup-metrics/)) |
| ARPA ₹/month | MRR ÷ paying GSTINs | ≈ **₹1,500** ex-GST on a mid-skewed mix of **₹599 / ₹1,799 / ₹4,999 + Enterprise** — **VERIFY LIVE, sign-off pending** ([[08-dzzlo-subscription-strategy\|pricing]]) |
| Gross margin | (revenue − cost to serve) ÷ revenue | **80%** (OTP, hosting, support) |
| Gross profit / dealer / mo | ARPA × gross margin | **₹1,200** |
| **Payback (months)** | CAC ÷ (ARPA × gross margin) | Bar: CAC recovered **under 12 months** ([Skok](https://www.forentrepreneurs.com/saas-metrics-2/)) |
| Free months given | added to **payback**, not CAC | They cut gross profit, not acquisition cost |

### D. Monthly channel review — first Monday, 45 minutes

| Channel | Spend ₹ (cash + hours × ₹400 + travel) | Dealers | CAC ₹ | Verdict |
| --- | --- | --- | --- | --- |
| | | | | kill / keep / scale |

**Kill** after two months above 2× blended CAC with no improving trend; **keep** at parity; **scale** only after two consecutive reviews beating blended *and* ≥3 paying dealers — raise capped at **+50% of that line**, one channel at a time. Write the reason in the cell note: a killed channel with a reason can be revisited; one that quietly stopped cannot.

### E. Budget lines — the ₹30–50k/month envelope (HC7), at the midpoint

| Line | ₹/mo | Cut order |
| --- | --- | --- |
| Contingency / channel experiment | 3,000 | **1st — cut first** |
| Tools (Canva, landing page, hosting), [[M11-content-and-whatsapp-calendar\|M11]] | 3,000 | 2nd |
| Dealer Day / association | 8,000 | 3rd |
| WhatsApp API + BSP fee | 3,000 | 4th |
| Printing (leaflets, booklet, standee) | 4,000 | 5th |
| Video / creative (Hindi demo) | 5,000 | 6th |
| Fuel & travel (2 field days/week) | 8,000 | 7th |
| Referral payouts (Dealer Dost) | 6,000 | **8th — never cut** |
| **Cash total** | **₹40,000** | |
| **Founder time, non-cash** (45 h/wk × ₹400) | **≈78,000** | Reallocated, never cut |

**Cut whatever is furthest from a live conversation with an owner, first.** The WhatsApp line is real money — about **₹0.86 per marketing message, ₹0.115 per utility**, plus a BSP markup of ₹0.10–0.30 and 18% GST on both ([MyOperator, 2026](https://myoperator.com/blog/whatsapp-business-api-pricing-india-2026)), **VERIFY LIVE**. Any line moving over ₹5,000 needs a dated CEO sign-off and a line in [[T09-decision-log-and-adr|T09]]; the envelope is a runway call ([[C13-runway-burn-and-scenario-planner|C13]]).

## Worked example — VSYST (illustrative)

Monday 09:28. Domain director enters 12 visits, 4 demos, 4 referrals asked / 1 received; third director enters 2 trials and 40% reply rate, leaving rows 4 and 5 blank, noted *"aggregation not saved — CEO, this week."* Row 1 is red a second week, so pump visits goes onto the ops issues list automatically. At 10:00 the ops meeting reads T05 rows 2, 4 and 5, already filled here.

Channel review, last full quarter. **Referral:** ₹6,000 bounties + 24 h × ₹400 + ₹1,250 travel = ₹16,850 ÷ 3 dealers = **CAC ₹5,617**, payback 4.7 months (6.7 after two free months). **OMC intro (IOCL TM):** ₹32,900 ÷ 2 = **₹16,450**, payback 13.7. **Field:** ₹31,400 ÷ 2 = **₹15,700**, payback 13.1. Blended is ₹81,150 ÷ 7 = **₹11,593** — above referral, below OMC, flattering the expensive channel and punishing the cheap one. Verdicts: referral **scale** (line 8 up ₹3,000, nothing else moves); OMC and field **keep**.

## Common mistakes

- **Leaving founder hours out.** The cheapest-looking channel is usually the one that ate 68 hours.
- **Deciding on blended CAC.** It moves when the *mix* moves — a quarter with more referrals looks like a quarter where you got better at marketing.
- **Calling a channel proven at one dealer**, or moving the ₹400 rate mid-quarter.
- **Inventing a second activation definition.** Row 4 is [[T05-kpi-scorecard|T05]] row 3, ratified in [[17-the-numbers-a-ceo-watches|CEO 17]] §6.6.
- **Estimating rows 4, 5 or 8** because a blank looks bad — or letting installs and views onto this sheet.

## Related

Lesson [[11-metrics-budget-and-the-marketing-scorecard|11]] · [[M07-sales-pipeline-tracker|M07]], [[M09-referral-program-one-pager|M09]], [[M12-campaign-brief-budget-and-post-mortem|M12]] · [[T05-kpi-scorecard|T05]], [[T03-weekly-ops-meeting-agenda|T03]], [[T19-quarterly-plan-and-review|T19]], [[T09-decision-log-and-adr|T09]] · [[17-the-numbers-a-ceo-watches|CEO 17]], [[C12-unit-economics-and-business-model-calculator|C12]] · [[CMO-Docs/toolkit/index|CMO Toolkit]]
