# T07 — RACI Matrix

_Toolkit · fills the exercises in [[17-delegation-decision-rights-and-org-design|17 — Delegation, Decision Rights and Org Design]] · Owner: COO · Cadence: review quarterly and at every hire or exit · Workbook tab: `RACI` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

One page that ends "I thought _you_ were doing it" — and its twin, two people doing the same thing differently. RACI and DACI in six lines:

1. **R — Responsible:** does the work. Several Rs per activity are fine.
2. **A — Accountable:** answers for the outcome. **Exactly one per row** — "both" is nobody.
3. **C — Consulted:** gives input _before_ the work or decision; two-way, and expensive.
4. **I — Informed:** told _after_; one-way, cheap.
5. **RACI governs a recurring workstream; DACI decides one decision** — Driver runs the process, one Approver decides, Contributors feed in, Informed hear the result ([Routine — RACI vs DACI vs RAPID](https://routine.co/blog/posts/raci-daci-rapid-decision-framework)).
6. Use the standing RACI below for the operating rhythm, a throwaway DACI (logged in [[T09-decision-log-and-adr|T09]]) for one-off big calls; RAPID only matters once authority is spread across many managers ([Argumentree — RAPID vs DACI vs RACI](https://www.argumentree.com/compare/rapid-vs-daci-vs-raci/)).

At a three-director family company the matrix does one more job: it makes the difference between _helping with_ an activity (R) and _owning_ it (A) explicit — which is the whole "one owner per outcome" law of this course.

## When to use

- **Months 4–6**, once functions exist to allocate ([[17-delegation-decision-rights-and-org-design|lesson 17]]); until then [[T01-ceo-coo-operating-agreement|T01]]'s division-of-labour table carries the load.
- **The moment the same task falls between two people twice** — that is a missing row, not a misunderstanding.
- **At every hire or exit:** a new person takes a column and inherits Rs deliberately; a leaver's letters are reassigned the same day.
- For a single big decision (a partnership clause, a pricing structure), don't stretch RACI — write a five-line DACI in the decision log and move on.

## How to fill (rules)

1. **Exactly one A per row.** The `RACI` tab's Check column flags violations. **A/R** means accountable _and_ does the work — the honest small-team state.
2. **Fill by row, then argue by column.** A column that is nearly all A/R is a bottleneck (usually yours — the COO-as-bottleneck trap); an empty column is either a person who doesn't need to be in the matrix or work you have not yet handed over.
3. **The matrix records what is true now,** not the aspiration. Moving an A is a handover — SOP written ([[T08-sop-template|T08]]), a shadow week done, and the move logged in [[T09-decision-log-and-adr|T09]].
4. **Keep C to two per row.** Every C slows the activity; most people who "should be consulted" only need I.
5. **₹ authority is not here.** RACI says who runs an activity; who may _commit money or sign_ is the DoA matrix ([[T22-delegation-of-authority-matrix|T22]]). The pair together are the delegation system.
6. Review quarterly (with [[T19-quarterly-plan-and-review|T19]]) and re-read after every org change.

## Template

The starter allocation for VSYST's shape today — three directors, a Support/Ops associate, a developer/contractor and the external CA/CS. Identical to the `RACI` tab; edit there and here together. — means no role in that activity.

| Function              | Activity                                                     | CEO/CTO | COO | Domain director | Support/Ops | Developer | CA/CS (ext) |
| --------------------- | ------------------------------------------------------------ | ------- | --- | --------------- | ----------- | --------- | ----------- |
| Governance & planning | Annual plan, budget & headcount                              | A       | R   | C               | I           | I         | C           |
|                       | Quarterly OKRs / rocks and quarterly review                  | A       | R   | C               | C           | C         | —           |
|                       | Weekly ops meeting (scorecard → rocks → issues)              | C       | A/R | R               | R           | R         | —           |
|                       | Board meetings, minutes & statutory registers                | A       | C   | I               | —           | —         | R           |
|                       | Decision log & CEO–COO operating agreement review            | A       | R   | C               | —           | —         | —           |
| Finance               | 13-week cash forecast & runway update                        | C       | A/R | I               | —           | —         | I           |
|                       | Monthly close, budget vs actual & MIS to directors           | I       | A   | I               | —           | —         | R           |
|                       | Vendor payments & bank operations (maker–checker)            | R       | A   | I               | —           | —         | I           |
|                       | Spend approvals above DoA thresholds                         | A       | R   | C               | I           | I         | —           |
| Compliance            | Statutory filings — GST, TDS, ROC, ITR (compliance calendar) | I       | A   | —               | —           | —         | R           |
|                       | DPDP / data-protection obligations & data map                | R       | A   | —               | C           | R         | C           |
|                       | Risk register & insurance review                             | C       | A/R | C               | —           | C         | C           |
| People                | Hiring plan, job scorecards & interviews                     | C       | A/R | C               | —           | C         | —           |
|                       | Onboarding / offboarding & access provisioning               | R       | A   | —               | R           | R         | —           |
|                       | Payroll, PF/ESI/PT/TDS on salaries                           | I       | A   | —               | —           | —         | R           |
|                       | Policies (POSH, leave, expenses, IT/security) & handbook     | C       | A/R | C               | I           | I         | C           |
| Customer              | Dealer onboarding to activation (first invoice in 14 days)   | I       | A   | C               | R           | C         | —           |
|                       | Support tickets, SLA & knowledge base                        | C       | A   | —               | R           | C         | —           |
|                       | Incident comms to dealers (WhatsApp broadcast)               | C       | A   | I               | R           | C         | —           |
|                       | Monthly tenant health & churn-risk review                    | I       | A/R | C               | R           | —         | —           |
| Revenue               | Pipeline review & follow-ups (lead → demo → pilot → paid)    | C       | A   | R               | I           | —         | —           |
|                       | Pricing, discounts & contract terms                          | A       | R   | C               | —           | —         | —           |
|                       | Partnership conversations (IOCL, bank / payment gateway)     | A       | C   | R               | —           | —         | —           |
|                       | Invoicing, collections & dunning                             | I       | A   | C               | R           | —         | I           |
| Product & engineering | Product roadmap & quarterly themes                           | A/R     | C   | C               | C           | C         | —           |
|                       | Release approval & production deploy (release gate)          | A       | I   | —               | I           | R         | —           |
|                       | Incident response, on-call & blameless postmortem            | A       | C   | —               | C           | R         | —           |
|                       | Backups, restore drill & secrets/access hygiene              | A       | C   | —               | —           | R         | —           |
| Operations            | Vendor onboarding, renewals & quarterly tool audit           | I       | A   | —               | R           | C         | —           |
|                       | SOP writing, review & training sign-off                      | C       | A   | R               | R           | R         | —           |

Until the associate and developer exist, their Rs sit with the COO (customer rows) and the CEO/CTO (engineering rows) — write the letters where they will land, do the work yourself meanwhile, and hand each R over with its SOP.

## VSYST example — reading the matrix

Two rows in action. **"Release approval & production deploy": CEO/CTO = A, Developer = R, COO = I.** The COO owns the release _checklist_ ([[T26-release-checklist|T26]]) as an SOP, but does not approve deploys — so when a release slips, the COO raises it as an issue in the ops meeting rather than pushing the button. **"Partnership conversations (IOCL, bank/gateway)": CEO/CTO = A, Domain director = R, COO = C.** The relationship belongs to the founders; the COO is consulted on terms and keeps the tracker and next-step discipline per [[11-revenue-operations-and-partnerships|lesson 11]] — which is why a stalled conversation shows up on the COO's tracker even though the COO doesn't own the call.

## Related

Lessons [[17-delegation-decision-rights-and-org-design|17]], [[03-the-coo-core-value-and-the-ceo-coo-contract|03]], [[08-the-operating-cadence|08]] · Templates [[T01-ceo-coo-operating-agreement|T01]], [[T22-delegation-of-authority-matrix|T22]], [[T29-org-chart-and-role-charters|T29]], [[T09-decision-log-and-adr|T09]] · [[COO-Docs/toolkit/index|COO Toolkit]]
