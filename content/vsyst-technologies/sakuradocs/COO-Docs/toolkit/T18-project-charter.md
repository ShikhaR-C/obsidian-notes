# T18 — Project Charter

_Toolkit · fills the partnership and project discipline of [[11-revenue-operations-and-partnerships|11 — Revenue Operations and Partnerships]] and the "no promise without a charter" rule of [[12-product-and-engineering-operations|12 — Product and Engineering Operations]] · Owner: the project's DRI writes it; the COO keeps the index · Cadence: one page at kickoff, reviewed on its listed dates, closed with an outcome note · Workbook tab: none — charters live in the vault._

## Purpose

A project charter is **one page that stops a project from being a vibe**: the problem, one measurable definition of success, what is in and — more importantly — out of scope, one DRI, the milestones, the budget, and who decides what. It is the small-company version of Amazon's working-backwards habit of writing the artefact before the work ([Commoncog — Working Backwards](https://commoncog.com/working-backwards/)), and it enforces two course rules at once: **one owner per outcome**, and lesson 12's rule that **nothing is promised to a dealer or partner with a date unless a charter exists behind it**. A project that cannot fill this page is not a project yet — it is an issue for the ops meeting.

## When to use

- Any effort likely to take **more than two weeks**, cross functions, or spend above the DoA's routine bands ([[T22-delegation-of-authority-matrix|T22]]).
- Anything that **binds an external promise** — a partner integration, a pilot with dates, the payment-gateway go-live ([[06-money-rails-and-finance-operations|lesson 06]] §11 names that one explicitly).
- **Every quarterly rock** gets at least a mini-charter at planning ([[T19-quarterly-plan-and-review|T19]]).
- Not for routine tasks (a to-do with an owner), recurring work (an SOP, [[T08-sop-template|T08]]) or a whole function (a role charter, [[T29-org-chart-and-role-charters|T29]]).

## How to fill (rules)

1. **One DRI** — directly responsible individual. Team members help; the DRI answers for the outcome.
2. **Success is one measurable number with a date.** "Roll out helpdesk" is activity; "100% of support conversations logged as tickets within two weeks of go-live" is success.
3. **Scope out is written with as much care as scope in** — it is the list of arguments you will not have later.
4. **Milestones: five or fewer**, each observable. More than five means the project is really two.
5. **Budget includes people-time**, not just cash — at three directors, time is the scarcer currency.
6. **Risks: the top three only**, each mirrored to [[T15-risk-register|T15]] if it survives the project.
7. **Decision rights are pre-split**: what the DRI decides alone, what goes to the CEO/COO, what needs the board — thresholds per T22.
8. **Review dates are booked in the calendar at kickoff**, and the charter is **closed with an outcome note** (shipped / killed / absorbed) logged in [[T09-decision-log-and-adr|T09]]. A charter without an outcome stays open — and open charters are read out at the quarterly review.

## Template

Copy into `charters/PRJ-YYYY-NN-<stem>.md`; one page, no more.

```
# PRJ-YYYY-NN — <name>                  status: proposed / active / closed
Problem          What hurts today, in two lines, with a number if possible.
Goal & metric    Success = <one measurable number> by <date>.
Scope — in       …
Scope — out      … (the arguments we are declining to have later)
DRI              <one name>        Team: <names, roles, hours/week>
Milestones       1. <observable> — <date>
                 2–5. …
Budget           Cash ₹… (VERIFY LIVE per vendor) · people-time … hrs/wk
Risks (top 3)    1. … → mitigation …   (mirror to T15 if it survives)
Decision rights  DRI alone: … · CEO+COO: … · Board: … (per T22)
Review dates     <booked in the calendar at kickoff>
Outcome note     (at close) shipped / killed / absorbed — logged in T09
```

## VSYST example — Frappe Helpdesk rollout (illustrative)

```
# PRJ-2026-03 — Frappe Helpdesk rollout                    status: active
Problem          Support lives in the technical founder's personal WhatsApp:
                 nothing is counted, assigned or reusable (lesson 10 §2).
Goal & metric    Success = 100% of support conversations logged as tickets,
                 and FRT measurable on the scorecard, within 2 weeks of go-live.
Scope — in       Helpdesk installed on the ERPNext site (the ERPNext guide's
                 add-on steps); support@ forwarding in; the five core macros
                 (T25); agent training for the founder + associate.
Scope — out      WhatsApp Business API automation; CSAT surveys; a public
                 help-centre site; chatbot anything.
DRI              COO            Team: CEO/CTO (install, ~4 h), Support/Ops
Milestones       1. App installed on the site — <date>
                 2. support@ flowing into the queue — <date>
                 3. Five macros live, WhatsApp log habit running — <date>
                 4. Scorecard rows (FRT, resolution) filling — <date>
Budget           Hosting already paid; incremental ≈ ₹0 (Helpdesk is free,
                 unlimited agents — VERIFY LIVE on frappe.io/helpdesk/pricing)
                 · people-time ~6 h/wk for 3 weeks
Risks            1. Personal-number habit persists → forward-and-reply rule,
                    official number printed everywhere (lesson 10 §2)
                 2. Double entry (WhatsApp + queue) fatigues → 30-second
                    logging macro; API decision trigger written in T09
                 3. Tickets logged but not categorised → category field
                    mandatory at close
Decision rights  DRI: workflow, macros, fields · CEO/CTO: hosting/install ·
                 CEO+COO: any paid tier
Review dates     Weekly in the ops meeting until milestone 4; close review +30 days
Outcome note     —
```

## Related

Lessons [[11-revenue-operations-and-partnerships|11]], [[12-product-and-engineering-operations|12]], [[10-customer-operations-support-and-success|10]], [[19-planning-okrs-and-the-quarterly-rhythm|19]] · Templates [[T09-decision-log-and-adr|T09]], [[T22-delegation-of-authority-matrix|T22]], [[T15-risk-register|T15]], [[T06-okr-planning-sheet|T06]], [[T19-quarterly-plan-and-review|T19]] · [[ERPNext-Implementation-Guide|ERPNext Implementation Guide]] · [[COO-Docs/toolkit/index|COO Toolkit]]
