# T28 — Weekly Business Review

_Toolkit · fills exercise 10.3 in [[16-metrics-dashboards-and-scorecards|16 — Metrics, Dashboards and Scorecards]]; installed by [[08-the-operating-cadence|08 — The Operating Cadence]] · Owner: the COO writes it; the CEO and directors read it · Cadence: weekly, Friday, same hour · No workbook tab — it reads the `KPI Scorecard` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) and links to it._

## Purpose

The scorecard says **what**; the weekly business review says **why** — and it is written, because writing is where sloppy explanations go to die. One page, every Friday: the scorecard snapshot, what changed and why, the top three issues, decisions taken or needed, and next week's three priorities.

The discipline is Amazon's. Its WBR is a standing mechanism — a fixed set of input and output metrics walked in a fixed order at a fixed hour, so the _data_ sets the agenda rather than whoever talks loudest ([Commoncog — the Amazon weekly business review](https://commoncog.com/the-amazon-weekly-business-review/); [the WBR as a mechanism](https://medium.com/@fergusb/amazon-mechanism-weekly-business-review-24087e953c58)). Operating-cadence practice converges on the same weekly shape: graded scorecard → at-risk flags → slips → this week's priorities → the one decision ([Fairview — operating cadence](https://getfairview.com/blog/operating-cadence)). The first rule gives this template its motto: **numbers before narrative.**

## When to use

- **Every Friday**, from the week the scorecard has enough trailing data to have a trend — four weeks is enough.
- **Before the monthly business review and the monthly update** — four WBRs read end to end are most of [[T23-board-and-investor-update|T23]] already written.
- **At the quarterly planning half-day**, where a quarter of WBRs read in order is the cheapest honest quarter review that exists ([[T19-quarterly-plan-and-review|T19]]).
- **At three people, write it anyway.** It feels like writing to yourself; it is the institutional memory the future team inherits, and the first draft of an investor update you have not been asked for yet.

## How to fill (rules)

1. **Numbers before narrative.** The snapshot goes at the top, unedited, before a single sentence of explanation. If the sheet is not filled, the WBR does not get written — fix the fill, not the prose.
2. **Every non-green row gets exactly one line**: what happened, why (your best current theory), what is being done, and who owns it. A red row with no line is the worst thing this document can contain — it means the sheet is being filled and not read.
3. **The narrative may not introduce numbers the scorecard doesn't carry.** "Dealers seem happier" is either the CSAT row or it is an anecdote. A new number worth tracking becomes a new row — at quarterly planning, not mid-week ([[T05-kpi-scorecard|T05]]).
4. **Say "I don't know yet" when you don't.** A named unknown with an owner and a date is a fine WBR line; a confident wrong theory is not, and it is much harder to unpick two months later.
5. **End with one decision** — made or needed. A WBR that never produces decisions is a diary; anything decided goes to [[T09-decision-log-and-adr|T09]], anything needed goes to the CEO with a date.
6. **Three priorities for next week, no more.** They must be things a person could finish, with a name on each. Last week's three are marked done or carried, with the reason, before the new three are set.
7. **One page, same hour, same place in the vault** (`wbr/YYYY-MM-DD.md`), posted in the ops channel with the scorecard link. Length is the discipline: an update nobody finishes is a file, not a communication.
8. **It is read, not presented.** Nobody schedules a meeting for it. Comments go back in writing before Monday, where they become the ops meeting's issues list.

## How it differs from the weekly ops meeting

They look similar and do opposite jobs — run both.

|                  | [[T03-weekly-ops-meeting-agenda\|T03]] — the ops meeting | **T28 — the WBR**                                                           |
| ---------------- | -------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Purpose**      | To **solve**: identify, discuss, solve the top issues    | To **think**: one person explains the week in writing                       |
| **Form**         | 90 minutes, everyone in a room (or a call), spoken       | One page, written by one person, read async                                 |
| **Day**          | Monday — it opens the week                               | Friday — it closes it                                                       |
| **Output**       | To-dos with owners and dates; decisions logged           | A record: what happened, why, what was decided                              |
| **Failure mode** | Talking instead of deciding                              | Narrating instead of explaining — writing "activation dipped" without a why |

The Monday meeting reads numbers as on-track/off-track only and drops exceptions into the issues list; the Friday WBR is where those exceptions get their explanation. Written on Friday, the WBR is also the meeting's prep: the issues list arrives already argued.

## Template

```
# WBR — week ending YYYY-MM-DD          written by: COO      read by: CEO, directors

## 1. Scorecard snapshot          (paste; link the KPI Scorecard tab)
| Metric | Owner | Goal | This week | Last week | RAG |

## 2. What changed and why        (one line per non-green row — no exceptions)
- <metric>: <what happened>. Why: <best theory>. Doing: <action> (<owner>, <date>).

## 3. Top 3 issues                (the ones that will still matter in a month)
1. <issue> — impact: <...> — proposed: <...>
2. ...

## 4. Decisions
Taken: <decision> -> logged in T09 as <id>
Needed: <decision> — from <who> — by <date>

## 5. Next week — three priorities
1. <priority> (<owner>)   2. ...   3. ...
Last week's three: <done / carried, why>
```

Nothing else belongs in it. Longer thinking goes in its own note and gets linked; status updates go in the daily check-in; feelings go in the 1:1 ([[T04-one-on-one-template|T04]]).

## VSYST example (illustrative)

A WBR from the first months, condensed — numbers invented to show the shape:

> **Snapshot.** Active tenants 14 (flat) · new tenants activated in 14 days 2 of 4 (amber) · rate-confirmation rate 61% (red, goal 75%) · invoices raised 212 (up 9%) · FRT median 26 min (green) · runway 11 months (green).
>
> **What changed and why.** _Rate-confirmation rate 61%:_ two tenants onboarded last month have stopped confirming — both are the ones trained on a phone call rather than at the counter. Doing: counter visit for both this week (domain-expert director, by Wednesday); onboarding SOP amended so remote training requires a follow-up visit inside 7 days (COO, done). _Activation 2 of 4:_ one dealer's customer numbers were entered wrong, one never intended to switch — logged as a pipeline lesson, not a support failure.
>
> **Top 3 issues.** (1) Remote-district onboarding produces half the activation of counter onboarding — decide whether to sell outside the district at all this quarter. (2) The OTP vendor has no failure alert separate from the delivery-rate row. (3) `support@` is still forwarding to a personal inbox.
>
> **Decisions.** Taken: onboarding SOP now requires a 7-day follow-up visit (logged T09-014). Needed: whether field sales opens a second district before activation is fixed — CEO, by the quarterly.
>
> **Next week.** 1. Counter visits to the two amber tenants (domain-expert director). 2. OTP failure alert live (CEO/CTO). 3. `support@` moved onto the company alias (COO).

Read it back and notice what it prevents: the activation dip has a cause, an action and an owner four weeks before it would have shown up as churn — which is the entire argument for writing one page on a Friday.

## Related

Lessons [[16-metrics-dashboards-and-scorecards|16]] (the scorecard and KPI tree it reads), [[08-the-operating-cadence|08]] (where it sits in the week), [[19-planning-okrs-and-the-quarterly-rhythm|19]] (how it feeds the monthly and the quarterly) · Templates [[T05-kpi-scorecard|T05]], [[T03-weekly-ops-meeting-agenda|T03]], [[T09-decision-log-and-adr|T09]], [[T23-board-and-investor-update|T23]], [[T19-quarterly-plan-and-review|T19]] · [[toolkit/index|COO Toolkit]]
