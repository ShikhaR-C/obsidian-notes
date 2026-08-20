# T05 — KPI Scorecard

_Toolkit · fills the exercises in [[16-metrics-dashboards-and-scorecards|16 — Metrics, Dashboards and Scorecards]] · Owner: COO (the sheet); one named owner per metric · Cadence: filled every Monday by 10:00, read in the weekly ops meeting · Workbook tab: `KPI Scorecard` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

The scorecard is **the company's weekly instrument panel**: a handful of numbers, each with one owner, a goal and a red line, filled every Monday and read in the ops meeting. The form is EOS's weekly Scorecard — **5–15 numbers on a 13-week trailing view** ([EOS — Level 10 Meeting](https://www.eosworldwide.com/level-10-meeting)); the discipline behind it is Amazon's Weekly Business Review, built on **controllable input metrics** rather than outcomes you can only watch ([Commoncog — the Amazon WBR](https://commoncog.com/the-amazon-weekly-business-review/)); the usability bar is 4DX's scoreboard rule — anyone can tell **in five seconds** whether the company is winning ([4DX — Perdoo](https://www.perdoo.com/resources/online-guides/4dx)). What the sheet buys you is **managing by exception**: green rows get no meeting time, attention goes to the largest deviations ([AccountingTools — management by exception](https://www.accountingtools.com/articles/what-is-management-by-exception.html)). This is what "the COO reads dashboards, not inboxes" means in practice.

## When to use

- **v0 from Day 8 of the seat:** the seven numbers below, on one sheet, before you have read [[16-metrics-dashboards-and-scorecards|lesson 16]]. A rough scorecard this Monday beats a perfect one next month.
- **v1 when the functions exist:** the full VSYST KPI tree (below) as support, revenue and release mechanisms come alive in Months 2–6. The `KPI Scorecard` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) already carries the v1 rows.
- **Read weekly, changed quarterly.** Goals and rows change at quarterly planning ([[T19-quarterly-plan-and-review|T19]]); a mid-quarter change is a logged decision ([[T09-decision-log-and-adr|T09]]). Retire any row that has not driven a decision in a quarter.

## How to fill (rules)

1. **Filled by Monday 10:00.** The ops meeting reads the sheet; it never builds it. No sheet, no meeting ([[T03-weekly-ops-meeting-agenda|T03]]).
2. **One owner enters each number — personally.** The owner of the metric, not a scribe. If a number is late twice, the owner is wrong or the query is too hard — fix one of them.
3. **No metric without a source query.** The exact Mongo aggregation, ERPNext report name, dashboard URL or sheet formula is written in the Source column. If nobody can name the query, it is an opinion, not a metric.
4. **5–15 rows, no more** (EOS). v0 is seven. Every row you add dilutes the five-second read.
5. **13-week trailing view:** fill weeks left to right, never overwrite history; percentages as fractions (0.6 = 60%). The tab computes Last/Trend/Status.
6. **RAG comes from three cells:** Direction (higher/lower is better), Goal (green) and Red line. Green = at or better than goal; red = at or worse than the red line; amber = between. Agree all three per row at quarterly planning.
7. **Majority leading.** Most rows must be inputs you control this week (demos, activation, confirmations, response time) — lagging rows (paying tenants, cash) tell you what already happened ([Commoncog — WBR](https://commoncog.com/the-amazon-weekly-business-review/)).
8. **In the meeting: on track / off track only.** Off track drops to the issues list; **red two weeks running escalates automatically** — it becomes a top-3 issue without a vote.

## Template

Columns (identical to the `KPI Scorecard` tab — W4…W13 omitted here for width; the tab holds all thirteen plus computed Last/Trend/Status):

**VSYST scorecard v0 — the first seven numbers** (goals and red lines illustrative until the first quarterly planning):

| #   | Metric                                                                   | Owner           | Source (query / tool)                 | Goal (green) | Red line | W1  | W2  | W3  | …   |
| --- | ------------------------------------------------------------------------ | --------------- | ------------------------------------- | ------------ | -------- | --- | --- | --- | --- |
| 1   | Runway (months)                                                          | COO             | `Runway & 13-Week Cash` tab           | ≥ 9          | 6        |     |     |     |     |
| 2   | Demos done this week                                                     | Domain director | ERPNext CRM (Opportunity)             | 2            | 1        |     |     |     |     |
| 3   | New tenants activated (≥1 customer linked and ≥1 invoice within 14 days) | Support/Ops     | Mongo cohort query                    | 1            | 0        |     |     |     |     |
| 4   | Weekly active tenants (≥1 order or invoice in the week)                  | COO             | Mongo: orders/invoices by tenant      | 6            | 3        |     |     |     |     |
| 5   | Rate-confirmation rate (10 PM–6 AM window)                               | Support/Ops     | Mongo: confirmations ÷ active dealers | ≥ 90%        | 70%      |     |     |     |     |
| 6   | Invoices through DZZLO this week                                         | Support/Ops     | Mongo: invoices collection            | 40           | 20       |     |     |     |     |
| 7   | Support first-response time (median, hours)                              | Support/Ops     | Helpdesk / WhatsApp log               | ≤ 2          | 6        |     |     |     |     |

**VSYST scorecard v1 — the KPI tree** (the rows already sitting in the workbook tab; add them as the mechanisms go live, lesson 16):

| Group                 | Rows (owner)                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pipeline              | New leads (Domain director) · Demos done (Domain director) · Pilots started (COO) · **Paying dealer tenants — the North Star, cumulative** (COO)                                      |
| Activation & usage    | Weekly active tenants (COO) · Activation rate (Support/Ops) · Invoices through DZZLO (Support/Ops) · Rate-confirmation rate (Support/Ops) · Logo churn, 30+ days inactive (COO)       |
| Revenue & cash        | MRR — once priced, no target until then (CEO/CTO) · Collections ₹/week (COO) · DSO — once invoicing (COO)                                                                             |
| Support & reliability | First-response time (Support/Ops) · Resolution time (Support/Ops) · API uptime (CEO/CTO) · Incidents P1+P2 (CEO/CTO) · OTP delivery rate (Developer) · Push delivery rate (Developer) |
| Burn, cost & team     | Net burn ₹/month (COO) · Runway months (COO) · Cost-to-serve per active tenant (COO) · Headcount (COO) · Open roles (COO)                                                             |

## VSYST example (illustrative)

Monday 2026-08-24, 09:55 — the associate posts the filled v0 in the ops channel. Runway 9.0 (green). Demos 1 (amber — one rescheduled). New tenants activated 1 (green). Weekly active tenants 3 (**red line — second week flat → issues list automatically**). Rate-confirmation 80% (amber). Invoices 28 (amber). First-response time 3.5 h (amber — the queue backed up on Saturday). The 10:00 meeting spends zero time on rows 1–3, votes weekly-active and response time into IDS, and solves both with owners and dates ([[T03-weekly-ops-meeting-agenda|T03]]). Total scorecard airtime: three minutes.

## Related

Lessons [[16-metrics-dashboards-and-scorecards|16]], [[08-the-operating-cadence|08]], [[02-how-a-coo-thinks|02]] · Templates [[T03-weekly-ops-meeting-agenda|T03]], [[T28-weekly-business-review|T28]], [[T06-okr-planning-sheet|T06]], [[T09-decision-log-and-adr|T09]], [[T20-budget-vs-actual-and-cash-forecast|T20]] · [[toolkit/index|COO Toolkit]]
