# 16 — Metrics, Dashboards and Scorecards

_Phase 4 · Autopilot · Months 6–18. After this lesson you can grow scorecard v0 into VSYST's full KPI tree with a North Star and its input branches, mark every row leading or lagging with a target, a red line and exactly one owner, name the source query behind each number, run the Monday fill and the written weekly business review, wire alerts so exceptions find you, and refuse vanity metrics and premature dashboards._

## Explain-it-like-I'm-5

A car has thousands of moving parts, but the driver watches a **dashboard with five dials** — speed, fuel, engine temperature, and a couple of warning lights. Nobody drives by opening the bonnet every kilometre; you drive by the dials, and a light interrupts you only when something crosses a line. Running a company is the same trick: pick a handful of numbers that say whether the machine is healthy, look at them at the same time every week, and let the red ones interrupt you. The skill is picking dials that **warn you early** — the fuel gauge tells you about a problem you can still prevent; the odometer only tells you what already happened. This lesson builds VSYST's dashboard: which dials, who reads each one, where its number comes from, and what happens when a light turns red.

## 1. You already have a scorecard — now grow it deliberately

You built the instrument panel's first version in [[08-the-operating-cadence|lesson 08]], exercise 15.4: **scorecard v0 — seven numbers on one sheet**, filled every Monday by 10:00, read in the ops meeting in three minutes. Cash in bank, new leads, demos done, active dealer tenants, rate-confirmation rate, invoices through DZZLO, open support issues — one owner, a goal and a RAG rule each, on the 13-week trailing view in [[T05-kpi-scorecard|T05]] and the `KPI Scorecard` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx). Since then, lessons 10–14 have each added their rows as the mechanisms went live: the four support numbers, the pipeline math, the engineering health metrics, cost per person per month.

That accretion is correct — and it now needs design, or the sheet becomes a junk drawer. This lesson makes two upgrades. First, **the rows stop being a list and become a tree**: every number earns its place by its connection to the one number that defines success, so you can say _why_ each row exists and what moving it moves. Second, **the reading gets a written form and an exception discipline**: the weekly business review narrates the numbers, and alerts plus RAG rules make the exceptions find you, instead of you patrolling for them.

One constraint survives both upgrades: **the weekly sheet stays at 5–15 rows** — EOS's scorecard band, on the same 13-week trailing view ([EOS — Level 10 Meeting](https://www.eosworldwide.com/level-10-meeting)). The KPI tree will contain more numbers than the weekly sheet shows; the tree is the map of what matters, the scorecard is the subset you steer by this quarter. Anything on the sheet that has not driven a decision in a quarter goes back into the tree and off the sheet (T05's retirement rule).

## 2. The KPI tree and the North Star

A **KPI** (key performance indicator) is a number chosen because it indicates whether the company is winning; a **KPI tree** arranges those numbers by causation: one **North Star** at the top — the single output that best captures the value the company creates — and beneath it the **input branches** whose numbers drive it. The tree is how you answer, for any row, "why is this on the sheet?" — because it feeds a branch, which feeds the North Star.

**VSYST's North Star is paying, active dealer tenants.** Both words are load-bearing. _Paying_ because the monetisation decision is made — a company-level subscription per GSTIN, billed on the web ([[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]) — and a free user base is not a business. _Active_ because a paying-but-idle tenant is churn that hasn't been invoiced yet: for a new tenant, active starts at **activation — ≥1 customer linked and ≥1 invoice raised within 14 days of signup** ([[10-customer-operations-support-and-success|lesson 10]] §7's definition, unchanged); thereafter it means the tenant transacted this week. A North Star that counted only signups would reward the wrong motion; one that counted only revenue would hide silent drift back to paper and Tally.

The tree, top to bottom — outputs at the top, controllable inputs below:

```
                    PAYING, ACTIVE DEALER TENANTS   ← North Star
                       │
   ┌───────────┬───────┴────┬─────────────┬──────────────┐
   Pipeline    Activation   Retention &   Reliability     Economics
   │           & usage      revenue       & support       & team
   │           │            │             │               │
   leads       activation   logo churn    uptime,         burn, runway
   demos       rate         MRR / ARPA*   incidents       cost-to-serve
   pilots      weekly       collections,  FRT,            headcount,
   → paid      active       DSO*          resolution      open roles,
               tenants;                   OTP & push      eNPS
               invoices                   delivery
               & GMV; rate-
               confirmation
```

\* once priced / once invoicing — the rows exist from day one, the targets wait.

Every branch is a mechanism you have already built: pipeline is [[11-revenue-operations-and-partnerships|lesson 11]]'s stages, activation and usage are lesson 10's onboarding and success cadence, reliability is [[12-product-and-engineering-operations|lesson 12]]'s monitoring, economics is [[06-money-rails-and-finance-operations|lesson 06]] and [[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]]. The tree does not invent numbers; it arranges the machine's existing gauges by what drives what.

The arranging principle is **leading versus lagging** ([[02-how-a-coo-thinks|lesson 02]] §8 introduced it): lagging rows are results — paying tenants, cash, churn — real, and unactionable this week; leading rows are the **controllable inputs** that predict them — demos booked, tenants activated inside 14 days, the rate-confirmation rate, tickets answered inside SLA. Amazon's weekly business review is built deliberately on controllable input metrics ([Commoncog — the Amazon WBR](https://commoncog.com/the-amazon-weekly-business-review/)), and 4DX's second discipline says the same in one line — act on lead measures ([4DX — Perdoo](https://www.perdoo.com/resources/online-guides/4dx)). The tree makes the discipline structural: the North Star and the top of each branch are lagging; everything below is leading, and **the weekly sheet is weighted toward the leading rows**, because those are the ones a Monday meeting can act on. A scorecard that is all lagging numbers is a history book.

## 3. VSYST's KPI tree in full

Row by row — this is the v1 already sitting in the `KPI Scorecard` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx) (goals and history there are illustrative), plus the quarterly people row. **Lead/Lag** is the §2 classification; **Owner** is the one person who enters the number.

| Branch                | Metric                                                                | Lead/Lag | Owner           | Source                                                                   |
| --------------------- | --------------------------------------------------------------------- | -------- | --------------- | ------------------------------------------------------------------------ |
| Pipeline              | New leads (dealers) this week                                         | Leading  | Domain director | ERPNext CRM — Lead list                                                  |
| Pipeline              | Demos done                                                            | Leading  | Domain director | ERPNext CRM — Opportunity list                                           |
| Pipeline              | Pilots started                                                        | Leading  | COO             | ERPNext CRM / onboarding sheet                                           |
| **North Star**        | **Paying dealer tenants (cumulative)**                                | Lagging  | COO             | Mongo: tenants where plan = paid                                         |
| Activation & usage    | Weekly active tenants (≥1 order or invoice in the week)               | Leading  | COO             | Mongo: orders/invoices by tenant                                         |
| Activation & usage    | Activation rate (≥1 customer linked & ≥1 invoice within 14 days)      | Leading  | Support/Ops     | Mongo: new-tenant cohort query                                           |
| Activation & usage    | Invoices through DZZLO this week — count, and their ₹ value (**GMV**) | Leading  | Support/Ops     | Mongo: invoices collection (count + sum)                                 |
| Activation & usage    | Rate-confirmation rate (10 PM–6 AM window)                            | Leading  | Support/Ops     | Mongo: confirmations ÷ active dealers                                    |
| Retention & revenue   | Logo churn (tenants inactive 30+ days)                                | Lagging  | COO             | Mongo: last-activity query                                               |
| Retention & revenue   | MRR (₹) — _once priced; no target until then_                         | Lagging  | CEO/CTO         | ERPNext subscriptions / invoices                                         |
| Retention & revenue   | Collections this week (₹)                                             | Leading  | COO             | Bank statement / ERPNext payments                                        |
| Retention & revenue   | DSO (days sales outstanding) — _once invoicing_                       | Lagging  | COO             | ERPNext AR ageing                                                        |
| Reliability & support | Support first-response time (median, hours)                           | Leading  | Support/Ops     | Frappe Helpdesk report                                                   |
| Reliability & support | Support resolution time (median, hours)                               | Leading  | Support/Ops     | Frappe Helpdesk report                                                   |
| Reliability & support | API uptime %                                                          | Lagging  | CEO/CTO         | UptimeRobot / Better Stack                                               |
| Reliability & support | Incidents (P1 + P2) this week                                         | Lagging  | CEO/CTO         | Incident log ([[T17-incident-postmortem\|T17]])                          |
| Reliability & support | OTP delivery rate                                                     | Leading  | Developer       | 2Factor.in dashboard                                                     |
| Reliability & support | Push delivery rate                                                    | Leading  | Developer       | OneSignal dashboard                                                      |
| Economics & team      | Net burn this month (₹)                                               | Lagging  | COO             | `Runway & 13-Week Cash` tab                                              |
| Economics & team      | Runway (months)                                                       | Lagging  | COO             | `Runway & 13-Week Cash` tab                                              |
| Economics & team      | Cost-to-serve per active tenant (₹/month)                             | Leading  | COO             | [[app-store-economics/11-cost-model-worksheet\|cost-to-serve worksheet]] |
| Economics & team      | Headcount (employees + contractors)                                   | Lagging  | COO             | `Headcount Plan` tab                                                     |
| Economics & team      | Open roles                                                            | Leading  | COO             | `Hiring Pipeline` tab                                                    |
| Economics & team      | eNPS — _quarterly, not weekly_                                        | Lagging  | COO             | Quarterly two-question pulse ([[09-people-operations\|lesson 09]])       |

Reading notes, where the table compresses too much:

- **MRR and ARPA.** MRR (monthly recurring revenue) and ARPA (average revenue per account = MRR ÷ paying tenants) become real the day pricing is decided — until then the rows sit at zero with no target, which is information, not embarrassment. When they wake, **never treat the placeholder tiers in the pricing doc as facts**; the numbers come from ERPNext, nowhere else.
- **Invoices and GMV travel together.** The count says whether the habit is alive; the ₹ value (gross merchandise value flowing through DZZLO) says how much dealer business trusts the ledger — the number the fintech ambitions of the [[00_OVERVIEW|Product Overview]] will one day be underwritten by. Same query, two outputs.
- **Rate-confirmation rate is the tree's most DZZLO-specific dial.** It is the front door of the core loop — when it drops for a tenant, churn is usually three weeks behind (lesson 10 §9), which is exactly what a leading indicator is for.
- **eNPS** ("how likely are you to recommend working here", scored −100 to +100, plus "why") is measured quarterly with the survey rhythm, and the _trend_ matters more than the score at a team this small — with five respondents, one bad quarter of noise is not a crisis, but two falling quarters is a conversation. Team turnover and its cousins are classic COO-owned numbers ([Cowen Partners — COO performance metrics](https://cowenpartners.com/coo-performance-metrics-how-to-measure-the-effectiveness-of-your-coo/)).
- **The weekly sheet is a subset.** Twenty-four rows exceed the 5–15 band; quarterly planning picks which rows ride the weekly sheet this quarter (the leading rows of whichever branches are this quarter's rocks), and the rest are filled monthly or quarterly in the same tab. The tree is the map; the sheet is the route.

## 4. Targets, RAG and the rules of the sheet

A number without a threshold is trivia. Every row carries three cells — **direction** (higher or lower is better), **goal** (the green line) and **red line** — and the sheet computes the colour: green at or better than goal, red at or worse than the red line, amber between. The rules that keep the colours honest, consolidated from [[T05-kpi-scorecard|T05]]:

1. **Targets are set at quarterly planning** ([[T19-quarterly-plan-and-review|T19]]), from your own trailing baseline — not from SaaS benchmark posts written about companies that are not a fuel-distribution SaaS in Chhattisgarh. First quarter: run four weeks with no targets, then set goal ≈ "good week we've actually had" and red line ≈ "week that should trigger action". A mid-quarter change is a logged decision ([[T09-decision-log-and-adr|T09]]), not an edit.
2. **One owner enters each number — personally, by Monday 10:00.** The owner of the metric, not a scribe; a number late twice means the owner is wrong or the query is too hard — fix one of them. No sheet, no meeting ([[T03-weekly-ops-meeting-agenda|T03]]'s rule). This is the whole "one sheet, one owner, every Monday 10:00" contract: one place, named people, a deadline the heartbeat depends on.
3. **No metric without a source query** (§5). If nobody can name the query, the row is an opinion.
4. **The five-second read.** Anyone glancing at the sheet can tell whether the company is winning — 4DX's scoreboard bar ([4DX — Perdoo](https://www.perdoo.com/resources/online-guides/4dx)). That is what the colour column is for, and why the sheet stays at 5–15 weekly rows.
5. **In the meeting: on track / off track only.** Discussion is what the issues list is for; **red two weeks running escalates automatically** — it becomes a top-3 issue without needing a vote.
6. **History is never overwritten.** Weeks fill left to right; a wrong number is corrected with a note, not silently. The 13-week view exists so trends are visible — one bad week is weather, three is climate.

## 5. Data sources — the query behind every number

The Source column is a promise: **the exact, runnable query behind the row** — a saved Mongo aggregation, an ERPNext report name, a dashboard URL, a sheet formula. The promise matters for three reasons: the number survives its owner (anyone can re-run it), disputes end ("what counts as active?" is answered by the pipeline's `$match`, in writing), and [[18-automation-and-ai-in-operations|lesson 18]]'s first automation — the scorecard auto-fill — is only possible for rows whose queries already exist.

Where VSYST's numbers come from, system by system:

| System                   | Rows it feeds                                                                                                 | The query note says                                                                                                                                                                |
| ------------------------ | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MongoDB** (production) | Paying tenants, weekly active, activation cohort, invoices + GMV, rate-confirmation rate, churn/last-activity | The exact aggregation pipeline, saved and version-controlled; read-only credentials (the COO's Atlas access is read-only by design — [[07-tools-and-it-foundation\|lesson 07]] §4) |
| **ERPNext**              | Leads, demos, collections, AR ageing/DSO, MRR once billing runs                                               | The report name and filters (Lead list, Opportunity list, Accounts Receivable, Payment Entry) per the [[ERPNext-Implementation-Guide\|guide]]'s sales cycle                        |
| **Frappe Helpdesk**      | FRT, resolution time, tickets per tenant                                                                      | The report and the severity filter                                                                                                                                                 |
| **Vendor dashboards**    | Uptime (UptimeRobot/Better Stack), OTP (2Factor.in), push (OneSignal)                                         | The dashboard URL and which widget/number to read                                                                                                                                  |
| **Mixpanel / Firebase**  | Funnel and engagement detail _behind_ the usage rows, once events are instrumented                            | Which event names; treat as diagnostic depth, not scorecard truth, until the event plan is verified against Mongo                                                                  |
| **The workbook**         | Burn, runway, cost-to-serve, headcount, open roles                                                            | The tab and cell (`Runway & 13-Week Cash`, `Headcount Plan`, `Hiring Pipeline`; cost-to-serve from the [[app-store-economics/11-cost-model-worksheet\|worksheet]])                 |
| **Quarterly pulse**      | eNPS                                                                                                          | The two questions, the send date, the scoring rule                                                                                                                                 |

Keep the full notes in one vault page — `coo-workbook/metric-sources.md` (a live company record, so it lives beside the filled workbook, not in this course folder) — one block per row: definition in one sentence, the query verbatim, the last test-run date. Exercise 10.2 writes it. And one honesty rule: **when two systems disagree, name the system of record for that row** — tenant activity is Mongo's truth, money is ERPNext's, and Mixpanel is never the referee (lesson 07 §1's rule applied to numbers).

## 6. The weekly business review — numbers before narrative

Numbers say _what_; the weekly business review says _why_ — and it is written, because writing is where sloppy explanations go to die. Every Friday the COO writes the one-page WBR ([[T28-weekly-business-review|T28]], installed by [[08-the-operating-cadence|lesson 08]] §5): the scorecard snapshot, what changed and why, the top three issues, decisions taken, next week's one thing. It is read async; it is not the ops meeting (the meeting solves in a room; the WBR forces one person to think in writing); and its first rule gives this section its name: **numbers before narrative**.

The discipline is Amazon's. The WBR there is a standing mechanism — a deck of input and output metrics walked in a fixed order at a fixed hour, so that the _data_ sets the agenda rather than whoever talks loudest ([Commoncog — the Amazon WBR](https://commoncog.com/the-amazon-weekly-business-review/); [Amazon's WBR as a mechanism](https://medium.com/@fergusb/amazon-mechanism-weekly-business-review-24087e953c58)), and EOS's scorecard segment applies the same order at small-company scale — numbers reported on-track/off-track first, discussion after, elsewhere ([EOS — Level 10 Meeting](https://www.eosworldwide.com/level-10-meeting)). Operating-cadence practice converges on the same weekly shape: graded scorecard → at-risk flags → slips → this week's priorities → the one decision ([Fairview — operating cadence](https://getfairview.com/blog/operating-cadence)).

Three writing rules keep VSYST's WBR honest:

1. **Every non-green row gets exactly one line**: what happened, why (best current theory), what is being done, owner. A red row with no line is the worst thing a WBR can contain — it means the sheet is being filled and not read.
2. **The narrative may not introduce numbers the scorecard doesn't carry.** "Dealers seem happier this week" is either the CSAT row or it is an anecdote; anecdote-management is precisely what the sheet exists to replace. (New number worth tracking? Add the row — at quarterly planning.)
3. **End with one decision.** Made or needed. A WBR that never produces decisions is a diary; the review-then-decide shape is the point.

At three people this feels like writing to yourself. Write it anyway — it is the institutional memory the monthly review reads, the discipline the future team inherits, and, one day, the first draft of the investor update ([[T23-board-and-investor-update|T23]]).

## 7. Managing by exception — alerts and the reading habit

**Management by exception** is the operating principle the whole apparatus serves: people and systems work independently and surface only variances from plan; the manager's attention goes to the largest deviations ([AccountingTools — management by exception](https://www.accountingtools.com/articles/what-is-management-by-exception.html); [Indeed — management by exception](https://www.indeed.com/career-advice/career-development/management-by-exception)). This is what "**the COO reads the scorecard, not inboxes**" means in practice — the inbox is sorted by who wrote last; the scorecard is sorted by what matters. An inbox-driven operation is accident-driven management with better typography ([[08-the-operating-cadence|lesson 08]] §1).

The exception ladder, from calm to loud:

| Level             | Trigger                         | What happens                                                                             |
| ----------------- | ------------------------------- | ---------------------------------------------------------------------------------------- |
| **Green**         | At or better than goal          | Zero airtime. Nobody discusses green rows — that is the reward for the mechanism working |
| **Amber**         | Between goal and red line       | One line in the WBR; the owner watches it; no meeting time unless trending down          |
| **Red**           | At or worse than the red line   | Drops to the ops meeting's issues list; owner arrives with a proposed fix                |
| **Red × 2 weeks** | Same row red twice running      | Auto-escalates to a top-3 issue — no vote needed (T05's rule)                            |
| **Alert**         | A machine notices before Monday | A human is paged/messaged now, not at the next fill                                      |

The last level is the difference between a weekly review and an operations system. Some numbers cannot wait for Monday, and for those the threshold lives in a machine: the uptime monitor pages the CEO/CTO the minute the API drops; the AWS billing alert fires at the budget line ([[07-tools-and-it-foundation|lesson 07]]); OTP delivery below its red line lands in the ops channel the same evening, because a dealer's stranded vehicle will not wait for the scorecard ([[12-product-and-engineering-operations|lesson 12]] owns the monitoring; [[18-automation-and-ai-in-operations|lesson 18]] builds the digests). The design rule connecting them: **the alert threshold is the scorecard's red line, wired into a machine** — one definition of "bad", whether a human or a cron job notices it. And the guard-rail that keeps the week livable: every alert is actionable and owned; an alert channel that cries wolf trains everyone to mute it, which is worse than no alerts at all.

## 8. Dashboards later; vanity metrics never

**Dashboards: later, deliberately.** [[07-tools-and-it-foundation|Lesson 07]] already made the call — Metabase (open source, self-hosted, reads Mongo and ERPNext directly) is the recommended dashboard layer, adopted **month 6 or later**, with a decision record. The sheet graduates when at least two of these are true: the Monday fill still costs more than 30 minutes after lesson 18's automation; the sheet has more regular readers than fillers; or questions arrive at a daily grain the weekly sheet cannot answer ("did activations move after Tuesday's release?"). Until then, the sheet is not the embarrassing interim — it is the correct tool: cheap, visible, and forcing a human through the numbers weekly.

Two rules survive graduation. **A dashboard visualises the §5 source queries — it never gets its own definitions.** The moment a Metabase card computes "active tenant" differently from the saved aggregation, the truth forks and every review starts with reconciliation. And **the scorecard row keeps its owner even when a robot draws the chart**: dashboards are telescopes, the scorecard is the log book — the anti-pattern [[20-the-autopilot-test-and-scaling-the-machine|lesson 20]] names is dashboards nobody reads, and the cure is that a named human still answers for each number every Monday.

**Vanity metrics: never.** A vanity metric is a number that flatters without informing — typically cumulative (it can only go up), unowned (nobody could move it on purpose), or unconnected (it feeds no branch of the tree). Downloads and sign-ups are vanity; paying, active tenants and cash are truth ([[02-how-a-coo-thinks|lesson 02]] §8). DZZLO's specific temptations, named so they stay refused:

- **App downloads** — the customer side rides the dealer relationship by design ([[company/README|Company Playbook]]: dealer = powered-on side, customer = WhatsApp-first); downloads measure the dealer's push, not your business.
- **Registered tenants** — a login is not a dealer; activation is the number (lesson 10). Registered-but-never-activated is a _diagnostic_ worth watching in the funnel, not a headline.
- **Cumulative anything** — "total invoices ever" rises during a death spiral. The North Star is the one allowed cumulative row, and it is kept honest by the churn row beside it.
- **WhatsApp group sizes, site visits, demo-video views** — none feeds a branch.

The three-question test for any proposed row: _Can a named owner move it this week? Does it change a Monday decision? Which branch of the tree does it feed?_ Three yeses or it stays off the sheet.

## 9. At VSYST — applying this now

- **Build the tree in the order the mechanisms went live.** The usage and reliability branches are measurable today from Mongo and the vendor dashboards; the support rows arrive with the Helpdesk (lesson 10); pipeline rows with the CRM habit (lesson 11); MRR, ARPA and DSO sleep until pricing and billing wake them. An empty revenue branch on the sheet is a feature — it keeps the pricing decision visible every Monday without stating prices that don't exist.
- **Point the Company Playbook's research rhythms at the tree.** The [[company/README|Company Playbook]]'s cadence — five customer interviews and the Sean Ellis survey weekly, the cohort retention curve weekly for the first six months, NPS and the churn post-mortem monthly — is where the _qualitative_ truth behind the numbers comes from. The scorecard tells you activation fell; the five interviews tell you why. Same rhythm, two instruments; the cohort curve and survey results file into the monthly review beside the sheet.
- **Instrument Mixpanel with the CEO before trusting it.** The custom events plan exists; until events are implemented and cross-checked against Mongo, funnel numbers are hypotheses. The scorecard's usage rows run on Mongo queries from day one — the database does not misremember.
- **The COO fills, then delegates, then reads.** Today you run most queries yourself (thirty minutes, per SOP-OPS-002 — [[15-sops-and-playbooks|lesson 15]]); within months the owners in §3's table enter their own rows; lesson 18's auto-fill retires the mechanical half entirely. The end state is the [[01-what-is-a-coo|lesson 01]] calendar at 50 people: Monday morning, you _read_ a scorecard someone (or something) else filled, and spend your attention on the exceptions.
- **What not to do:** no Metabase this quarter; no 25-row weekly sheet; no row without a query; no targets imported from benchmark blogposts; no second scorecard in anyone's private sheet — one sheet is the mechanism, and a parallel one is how companies come to hold two truths.

## 10. Exercises

**10.1 — Build KPI tree v1 with owners and RAG rules (60 min, with the CEO).** Take §3's table into [[T05-kpi-scorecard|T05]] and the `KPI Scorecard` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx): confirm each row's owner face to face (an owner who didn't say yes is a blank cell with a name in it), set direction, goal and red line per row from your last four weeks of history — illustrative until the first quarterly planning ratifies them — and mark each row Leading or Lagging in the Notes column. Pick the 5–15 rows that ride the weekly sheet this quarter; every v0 row you drop gets one line in [[T09-decision-log-and-adr|T09]] saying why.

**10.2 — Write the metric-sources note (60 min, the Mongo half with the CEO/CTO).** Create `coo-workbook/metric-sources.md`: one block per row — the one-sentence definition, the exact query (aggregation pipeline, ERPNext report name and filters, dashboard URL, or tab and cell), and today's date as the last test-run. Actually run each query once and paste the value it returned; two rows will surprise you, and that is the exercise working. Update the Source column of the tab to match.

**10.3 — Run the first written WBR (30 min, this Friday).** Write one page in [[T28-weekly-business-review|T28]]'s shape from the current sheet: scorecard snapshot, one line per non-green row (what, why, what's being done, owner), top three issues, decisions taken or needed, next week's one thing. Numbers before narrative; no number that isn't on the sheet. Send it to the CEO, file it in the vault as `wbr/YYYY-MM-DD.md`, and put the Friday slot on the calendar as immovable — the second WBR is the one that makes it a mechanism.

---

**Next:** [[17-delegation-decision-rights-and-org-design|17 — Delegation, Decision Rights and Org Design]] — the delegation ladder, RACI and the DoA matrix with ₹ thresholds, one DRI per outcome, role charters, and org design as the team grows from 3 to 30 — handing the founders' tasks over one SOP at a time.
