# T21 — Headcount Plan

_Toolkit · fills §2 of [[09-people-operations|09 — People Operations]] and §8 of [[17-delegation-decision-rights-and-org-design|17 — Delegation, Decision Rights and Org Design]] · Owner: COO (the CEO signs each row before it opens) · Cadence: written once, re-based every quarter, read at every hiring conversation · Workbook tab: `Headcount Plan` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) — it computes loaded monthly cost._

## Purpose

The headcount plan is **the list of seats the company intends to fill over the next eighteen months, each with the metric that opens it and the true monthly cost of filling it.** It exists to answer two questions that otherwise get answered by mood: _are we allowed to hire yet?_ and _what does this person actually cost?_

Both answers are cash answers. At a bootstrapped, pre-revenue company **every fixed salary is runway** ([[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]]), so the plan is really a spending plan wearing a people label — which is why it belongs next to the budget and the 13-week cash forecast ([[T20-budget-vs-actual-and-cash-forecast|T20]]) and not in a folder of job descriptions.

## When to use

- **Written once in Months 2–3**, alongside the first role charters ([[T29-org-chart-and-role-charters|T29]]) — before any role is discussed with a candidate.
- **Re-based every quarter** at the planning half-day ([[T19-quarterly-plan-and-review|T19]]): what fired, what slipped, what the next two quarters look like now.
- **Every time the founders feel busy.** That is precisely the moment the plan earns its keep — you read the trigger, and it has either fired or it hasn't.
- **In the annual plan and budget**, where the headcount line is one of the three numbers the year turns on ([[19-planning-okrs-and-the-quarterly-rhythm|lesson 19]] §2).
- **Before any offer**, because the offer must sit inside the row's planned loaded cost or go back to the CEO and the board ([[T22-delegation-of-authority-matrix|T22]]).

## How to fill (rules)

1. **Every row carries a metric trigger, not a feeling.** "Founder support hours > 10/week for four consecutive weeks" is a trigger; "we're drowning" is not. Write the trigger _before_ the role feels urgent, when you can still think clearly about it.
2. **Contractors before employees.** Start people on a defined scope and convert on evidence, through the same scorecard and process as any hire ([[T10-hiring-scorecard-and-process|T10]]). "We already know them" is how a mis-hire happens twice.
3. **Cost the row loaded, never as CTC.** Loaded monthly cost = gross monthly pay **+** employer PF **+** employer ESI **+** gratuity accrual **+** statutory bonus accrual **+** insurance ÷ 12 **+** tools and seat cost **+** the device amortised over its life. The thresholds decide which of those apply — EPF at 20+ employees, ESI at 10+ in notified areas, gratuity and maternity at 10+, statutory bonus at 20+ — and **every one of them is VERIFY LIVE with the CA** ([[09-people-operations|lesson 09]] §5 carries the current readings and their sources). Chhattisgarh's Zone A minimum wages are the floor for any role, revised each April and October — **VERIFY LIVE**.
4. **Follow the constraint, not a template, for the order.** VSYST's order is **Support/Ops → Field Sales → Developer/QA → Ops Manager or Chief of Staff**, and lesson 17 §8 defends it: support first because it frees the scarcest person and is the most documentable; field sales second because the constraint then moves to demand; a developer third; the hire that frees _you_ last (Kruze's benchmark for a first dedicated ops hire is roughly 10–12 employees — [Kruze](https://kruzeconsulting.com/blog/startup-operations-hire/)). If the constraint changes, the order changes and the change is logged in [[T09-decision-log-and-adr|T09]].
5. **Eighteen months, decreasing confidence.** Rows in the next two quarters are real; rows beyond twelve months are placeholders that hold the shape of the org, and everyone should say so out loud.
6. **Run the runway test on every row before it opens.** Add the loaded cost to the forecast and check that runway stays above the red line for at least six months after the start date (T20). A row that fails the test is deferred, not shrunk into a badly paid version of itself.
7. **A row is a plan, not permission.** Opening it still follows the DoA: a contractor already in this plan is the COO's call; an employee, or any role not in the plan, needs CEO + COO and a board minute.
8. **One status vocabulary**, so the tab can be read in ten seconds: `Planned → Triggered → Open → Offer → Filled`, plus `Deferred` and `Killed` — and killed rows stay visible with the reason.

## Template

Columns, identical to the `Headcount Plan` tab (which computes the loaded cost and the cumulative monthly people burn):

> Role · Function · Start month (planned) · Type (contractor / employee) · Gross monthly pay (₹) · Statutory add-ons (₹) · Other loaded cost (₹: insurance, tools, device) · **Loaded monthly cost (₹)** · Trigger to open the role (a metric) · Frees whom · Reports to · Status · Notes

Two blocks sit under the table on the tab and should be kept in the note too:

```
RUNWAY TEST (per row, before it opens)
  Cash today: ____   Monthly burn now: ____   Burn after this row: ____
  Months of runway after: ____   Red line: ____   Passes? Y / N

REVIEW
  Last re-based: ______   Next: ______ (quarterly planning day)
  Rows that fired this quarter: ______   Rows deferred, with reason: ______
```

## VSYST example (illustrative)

The first eighteen months at VSYST, in the order lesson 17 §8 defends. **Every rupee figure is blank on purpose — fill it from real quotes and the CG minimum-wage floor, and confirm the statutory add-ons with the CA (VERIFY LIVE).** What is _not_ illustrative is the trigger column: those are the numbers to agree now.

| #   | Role                           | Function     | Start (planned) | Type first                     | Loaded ₹/mo | Trigger to open                                                                      | Frees whom                                        | Status      |
| --- | ------------------------------ | ------------ | --------------- | ------------------------------ | ----------- | ------------------------------------------------------------------------------------ | ------------------------------------------------- | ----------- |
| 1   | Support/Ops Associate (Raipur) | Customer ops | Month 3–4       | Contractor → employee          | —           | Founder support + onboarding hours > 10/week for 4 weeks, **or** > 25 active tenants | Technical founder — tickets, onboarding, WhatsApp | Planned     |
| 2   | Field Sales (one district)     | Revenue      | Month 6–8       | Contractor / commission        | —           | Demo requests exceed founder capacity, **or** first-district pipeline > 30 leads     | Domain-expert director — visits, follow-ups       | Planned     |
| 3   | Developer / QA                 | Engineering  | Month 9–12      | Contractor → employee          | —           | Release cadence slipping two months running, **or** bug-backlog age > 30 days        | CEO/CTO — maintenance, tests, on-call             | Planned     |
| 4   | Accounts / Admin (part-time)   | Finance      | Month 12–15     | Contractor (or the CA's staff) | —           | Monthly close inputs taking the COO > 6 hours, **or** vendor bills > 30/month        | COO — close prep, filings paperwork               | Placeholder |
| 5   | Ops Manager / Chief of Staff   | Operations   | Month 15–18     | Employee                       | —           | Team ≥ 8–10, **or** the COO's calendar audit shows > 50% "doing"                     | COO — the doing column                            | Placeholder |

Three notes on reading it. The **loaded cost of row 1 is the number that decides months 3–6** — it is the company's first recurring people cost and it lands while revenue is still a decision, not a fact ([[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]). Rows 1 and 2 start as contractors because scope, not sentiment, is what makes a first engagement reversible. And row 3's trigger is deliberately about **cognitive load** — three repositories, two app stores, the release gate and the on-call phone are already more than one person holds well ([[12-product-and-engineering-operations|lesson 12]]) — not about ticket volume, which row 1 already absorbs.

## Related

Lessons [[09-people-operations|09]] (the hiring plan in context, statutory thresholds), [[17-delegation-decision-rights-and-org-design|17]] (why this order), [[19-planning-okrs-and-the-quarterly-rhythm|19]] (the annual headcount line), [[10-customer-operations-support-and-success|10]] (the first role's actual job) · Templates [[T10-hiring-scorecard-and-process|T10]], [[T29-org-chart-and-role-charters|T29]], [[T20-budget-vs-actual-and-cash-forecast|T20]], [[T22-delegation-of-authority-matrix|T22]], [[T11-offer-letter-and-contract-checklists|T11]] · [[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]] · [[toolkit/index|COO Toolkit]]
