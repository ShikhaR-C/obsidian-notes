# T29 — Org Chart and Role Charters

_Toolkit · fills §6–§7 of [[17-delegation-decision-rights-and-org-design|17 — Delegation, Decision Rights and Org Design]] and §2 of [[09-people-operations|09 — People Operations]] · Owner: COO · Cadence: redrawn at every org change; charters re-read at the 90-day review and every quarterly · No workbook tab — the seats appear as columns on the `RACI` tab and rows on the `Headcount Plan` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

An org chart here is not a hierarchy diagram. It is **the list of outcomes with owners, drawn as a tree** — and the unit it is drawn in is the **seat**, not the person. EOS calls its version the accountability chart and insists you design seats before you think about who fills them; at a small company one person holds several seats at once ([EOS Toolbox](https://www.rarebirdinc.com/the-eos-toolbox-six-components-that-work-together/)).

The **role charter** is one seat written down: mission, three to five measurable outcomes, the KPIs, the decision rights, who it reports to, and a named backup. It earns its hour twice. Writing it is the test of whether the role is real — if you cannot name three measurable outcomes and point at the scorecard rows they move, you have a pile of chores, not a seat. Reading it later prevents the small-company failure where a good hire "helps everywhere and owns nothing", and leaves because they could never tell whether they were succeeding.

## When to use

- **Before writing any job ad** — the ad is the charter in public language, never the reverse ([[T10-hiring-scorecard-and-process|T10]]'s scorecard starts from this document).
- **At every hire, exit and reporting-line change**, and whenever a headcount row in [[T21-headcount-plan|T21]] fires.
- **When a scorecard row goes red for capacity reasons two months running** — that is the tell that one seat is carrying two jobs.
- **At the quarterly review**, alongside the RACI ([[T07-raci-matrix|T07]]): a new person is a new column, and half the R's should migrate into it over their first two quarters.

## How to fill (rules)

1. **Seats before people.** Write what the seat owns without a name attached; then write who holds it today — possibly "COO (also holds Finance and People)". Seeing one name in five boxes is the point of the exercise.
2. **Draw the next size, not the size after next.** At three people, draw eight. Designing thirty while you are three produces empty boxes and imaginary problems.
3. **One accountable owner per outcome.** Two names on a box means each waits for the other; shared ownership is no ownership ([[index|the landing page]]'s law).
4. **Span three to five reports, and first-time managers at the low end** — the limit is not theory, it is how many real weekly 1:1s a person can hold ([[T04-one-on-one-template|T04]]).
5. **Split a function only when one person is carrying two jobs that each need full attention.** A premature split manufactures handoffs; the honest trigger is the capacity-red row above.
6. **A charter's KPIs must be existing scorecard rows**, and its decision rights must be existing lines in [[T22-delegation-of-authority-matrix|T22]]. If either doesn't exist yet, create it — a charter is not the place to invent private metrics or private authority.
7. **Every seat names a backup.** "Second person per critical task" is the business-continuity rule ([[13-compliance-calendar-risk-and-insurance|lesson 13]]) applied to the org chart, and it is what makes the two-week holiday test possible ([[20-the-autopilot-test-and-scaling-the-machine|lesson 20]]).
8. **Every reorg is a logged decision** with the trigger written down ([[T09-decision-log-and-adr|T09]]) — the second-order effects of moving a reporting line surface two quarters later, and you will want the reasoning.

## Template (a) — the org tree

Plain text in the vault, one fence per stage, each box a **seat** with the outcomes it owns. VSYST's four stages, from [[17-delegation-decision-rights-and-org-design|lesson 17]] §6:

```
3 PEOPLE — today. No managers; three peers, seven functions.
  CEO / CTO (technical founder)   COO (this seat)              Domain-expert director
  product, code, releases,        operations, finance, people, dealer relationships,
  infrastructure, app stores      compliance, customer ops,    field sales, industry
                                  vendors, the cadence         and OMC channels
  external: CA / CS, lawyer, freelance designers and testers

8 PEOPLE — roughly months 9-18. The first managers appear, all new at managing.
  CEO / CTO --- Developer / QA
  COO -+- Support/Ops Associate -- tickets, dealer onboarding, scorecard fill
       +- Accounts / Admin (part-time, or the CA's staff)
  Domain-expert director --- Field Sales (one district)

15 PEOPLE — functions split; a thin layer of leads.
  CEO --- Engineering Lead -+- 2-3 developers
                            +- QA
  COO -+- Ops Manager / Chief of Staff -+- Support (2)
       |                                +- Ops / Admin (1)
       +- Finance & Compliance (1, with the CA outside)
  Domain-expert director (Revenue) -+- Field Sales (2-3, two districts)
                                    +- Customer Success (1)

30 PEOPLE — you manage managers and stop filling any scorecard row yourself.
  CEO -+- CTO / Engineering (8-10)
       +- COO -+- Ops & Support (6-8)
       |       +- Finance & Compliance (2)
       |       +- People (1)
       +- Revenue -- Sales + Customer Success (8-10)
```

Add a layer **when a manager's exceptions start getting missed** — the symptom is a week where something red went unnoticed for five days — not when headcount crosses a round number.

## Template (b) — the role charter

```
ROLE CHARTER — <seat>          version 1.0 · written <date> · review <date+90d>
Held today by: <name / "vacant" / "COO, also holds …">   Reports to: <seat>
Backup: <seat/name>

MISSION (one sentence: why this seat exists)
OUTCOMES (3-5, measurable, dated — 12-month horizon)
KPIs (existing rows on T05; owner = this seat)
DECISION RIGHTS (existing lines in T22; anything else escalates)
SOPs OWNED (ids from the SOP Index)
NOT THIS SEAT (the two or three things people will assume it owns)
```

## VSYST example — four filled charters

Condensed; outcomes are illustrative and dated from a start month.

**COO.** _Mission:_ build and run the machine that turns the company's promises into kept promises, so the founders can steer instead of push. _Outcomes:_ the operating cadence runs 20 weeks without a skip; every statutory date has an owner and zero are missed; every recurring process has an owner, an SOP and a number by month 12; founder hours on non-product operations trending to the floor agreed in [[T01-ceo-coo-operating-agreement|T01]]. _KPIs:_ the COO scorecard ([[03-the-coo-core-value-and-the-ceo-coo-contract|lesson 03]] §3). _Decision rights:_ the COO rows of T22. _Not this seat:_ product direction, architecture, the code in releases. _Backup:_ CEO. Full version in [[T30-coo-charter-and-90-day-plan|T30]].

**Support/Ops Associate (Raipur).** _Mission:_ take dealer support and onboarding off the technical founder so tickets, WhatsApp and activation run without touching the CEO's day. _Outcomes:_ first response inside the [[T25-customer-support-sop|T25]] SLA on all channels; ≥ 80% of new tenants activated (first customer linked, first invoice) within 14 days; the top-10 FAQ answers written in Hindi and English; by month 6 runs the Monday scorecard fill unaided. _KPIs:_ FRT, % within SLA, CSAT, activation rate. _Decision rights:_ refunds/credit notes ≤ ₹10,000; no access-scope change without the dealer's authorisation. _Not this seat:_ pricing, promises about the roadmap. _Backup:_ COO.

**Field Sales (one district).** _Mission:_ turn dealer conversations in one district into activated tenants, at the counter. _Outcomes:_ an agreed number of qualified demos per week; pipeline stages current in the CRM the same day; every lost deal has a written reason. _KPIs:_ leads → demos → pilots → paid, and the visit log ([[11-revenue-operations-and-partnerships|lesson 11]]). _Decision rights:_ discount ≤ 10% off the quoted rate, logged in the CRM; anything else to the CEO. _Not this seat:_ onboarding delivery (hand off to support), contract terms. _Backup:_ domain-expert director.

**Developer / QA.** _Mission:_ keep DZZLO shipping and stable without the CEO/CTO being the only person who can. _Outcomes:_ bug backlog age under the agreed ratchet; the release gate stays green and every bugfix ships with its failing test first ([[tasks_12_tdd_testing/00-overview|tasks_12]]); on-call shared from month 2. _KPIs:_ deploy frequency, incidents, MTTR, bug-backlog age. _Decision rights:_ emergency hotfix during an incident; production deploys per the T22 row. _Not this seat:_ architecture calls, production data access beyond read-only. _Backup:_ CEO/CTO.

## Related

Lessons [[17-delegation-decision-rights-and-org-design|17]] (org design and the hiring order), [[09-people-operations|09]] (charters before hiring), [[20-the-autopilot-test-and-scaling-the-machine|20]] (seats and the holiday test) · Templates [[T21-headcount-plan|T21]], [[T10-hiring-scorecard-and-process|T10]], [[T07-raci-matrix|T07]], [[T22-delegation-of-authority-matrix|T22]], [[T30-coo-charter-and-90-day-plan|T30]], [[T04-one-on-one-template|T04]] · [[toolkit/index|COO Toolkit]]
