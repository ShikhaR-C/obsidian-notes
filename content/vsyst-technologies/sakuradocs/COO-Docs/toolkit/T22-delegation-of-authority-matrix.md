# T22 — Delegation of Authority Matrix

_Toolkit · fills §5 of [[17-delegation-decision-rights-and-org-design|17 — Delegation, Decision Rights and Org Design]] and the payment approvals in [[06-money-rails-and-finance-operations|06 — Money Rails and Finance Operations]] · Owner: CEO + COO write it, the board ratifies it · Cadence: written in Days 8–30; reviewed quarterly; re-ratified annually or whenever headcount doubles · Workbook tab: `DoA Matrix` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

A **delegation-of-authority matrix (DoA)** answers one question for every kind of commitment the company can make: **who may decide this alone, up to what limit, who must be told, and where it is recorded.** The standard shape is category × threshold × approver × second approver × documentation ([Tallyfy — delegation-of-authority matrix](https://tallyfy.com/delegation-of-authority-matrix-template/); [approval limits matrix](https://tallyfy.com/approval-limits-matrix-template/)).

It is the single most effective anti-bottleneck device in this course. Without it, "check with me first" is the default for everything and the COO becomes the queue ([[02-how-a-coo-thinks|lesson 02]] §4's negative leverage); with it, a person moves at their own speed inside a boundary agreed in advance — which is what delegation actually is. Its quieter job: it is the control your bank, your auditor and any future investor expect to see, and it lets you say "the matrix says so" instead of having a personal argument in a family founding team.

## When to use

- **Days 8–30 of the seat** — right after the bank account has maker–checker on it ([[06-money-rails-and-finance-operations|lesson 06]]) and before the first vendor contract is signed.
- **Whenever the same "should I ask you first?" happens twice** about the same kind of decision — that is a missing row, not a personality problem ([[T01-ceo-coo-operating-agreement|T01]]).
- **Before every hire and at every org change** — a new seat is a new column of authority, or an explicit note that it has none yet ([[T29-org-chart-and-role-charters|T29]] role charters point at rows here).
- **At the quarterly review**, alongside the access and vendor audits ([[08-the-operating-cadence|lesson 08]] §7); re-ratified annually or whenever headcount doubles.
- **Before any board meeting** that approves spend, hiring or a partnership — the matrix is what the resolution refers to.

## How to fill (rules)

1. **Every rupee figure is illustrative until your board ratifies it.** Set the lines from your runway, not from a template: a generic guide puts a bootstrapped startup's first approval line near \$5,000 ([Tallyfy](https://tallyfy.com/delegation-of-authority-matrix-template/)) — yours is wherever you would genuinely not want to be asked. A limit so low that everything crosses it is a matrix that does nothing.
2. **Two signatures above the line, always, for money leaving the company.** Below the line one person moves fast; above it two people are on the hook. Separately and regardless of amount, every bank payment is **maker–checker** — one person prepares, a different person releases (lesson 06).
3. **Every row names who is informed and where the decision is recorded** — the weekly note, the CRM, [[T09-decision-log-and-adr|T09]], or the board minute. An approval nobody can find three months later is not a control.
4. **Some rows are never delegated.** Statutory filings, anything signed for the company, and access to restricted personal data stay with the directors, whatever the amount.
5. **One emergency clause.** Anyone may act outside the matrix to stop harm — a live outage, a safety issue, a payment about to bounce — provided they say so within 24 hours and log it in T09. Without the clause, people either freeze or ignore the matrix entirely.
6. **Ratify it in a board meeting and minute it.** Until then it is a suggestion; once minuted it is the company's rule ([[05-legal-and-governance-foundation|lesson 05]]). Put the version, the ratification date and the next review date at the top of the file.
7. **The one-hat variant — the seat decides, not the person.** At a three-director company one director may hold both the CEO and COO hats on different days ([[03-the-coo-core-value-and-the-ceo-coo-contract|lesson 03]]; [[T01-ceo-coo-operating-agreement|T01]]'s calendar-by-hat ritual). The matrix still binds, and a "CEO + COO" row still means **two humans**: the second signature moves to the third director, and the decision is logged in T09 the same day. Wearing both hats never converts two signatures into one — that is the exact failure the matrix exists to prevent.
8. **VERIFY LIVE any threshold that touches a statutory limit** — cash-payment limits, TDS applicability on contractor payments, what needs a board resolution under the Companies Act — with the CA/CS before ratifying, and re-check each April ([[T16-compliance-calendar|T16]]).

## Template

Copy this note, fill the header, then work down the nine families. The table is identical to the `DoA Matrix` tab in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) — keep the tab as the live copy and this note as the narrative the board reads.

```
DELEGATION OF AUTHORITY — <company>        version 1.0
Ratified by board resolution on: ____________   Minute ref: ____________
Next review: ____________ (quarterly read, annual re-ratification)
Emergency clause: anyone may act outside this matrix to stop harm, provided
they say so within 24 hours and log it in T09.
```

| Decision | Threshold | Decides alone | Second signature | Informed | Recorded where |
| -------- | --------- | ------------- | ---------------- | -------- | -------------- |

**The nine families every row must fall into** — if a decision doesn't fit one, you have found a missing row: **spend** (operating and capital) · **hire and fire** · **contracts and MoUs** · **pricing and discounts** · **refunds and credit notes** · **production deploys and hotfixes** · **data access** · **public and dealer-wide comms** · **legal and statutory**.

## VSYST example (illustrative)

The starter matrix from [[17-delegation-decision-rights-and-org-design|lesson 17]] §5, extended with the recording column. **Every rupee figure is a proposal for the board to ratify, not a fact.**

| Decision                                                                  | Threshold (illustrative)          | Decides alone                    | Second signature           | Informed                   | Recorded where                                            |
| ------------------------------------------------------------------------- | --------------------------------- | -------------------------------- | -------------------------- | -------------------------- | --------------------------------------------------------- |
| Operating spend (tools, vendors)                                          | ≤ ₹5,000/month                    | COO                              | —                          | CEO                        | Weekly note + [[T14-vendor-and-tool-register\|T14]] row   |
| Operating spend                                                           | ₹5,000–25,000/month               | —                                | COO + CEO                  | Board next meeting         | [[T09-decision-log-and-adr\|T09]]                         |
| Operating spend                                                           | > ₹25,000/month or > ₹3 lakh/year | —                                | Board decision, minuted    | All directors              | Board minute                                              |
| Capital purchase (laptop, test phone)                                     | ≤ ₹50,000/item                    | COO                              | CEO                        | —                          | T14 + asset list                                          |
| Any payment out of the bank                                               | Any amount                        | Nobody alone — **maker–checker** | COO prepares, CEO releases | —                          | Bank + ERPNext                                            |
| Any payment out of the bank                                               | > ₹1 lakh                         | —                                | Two directors              | Board next meeting         | Board minute                                              |
| Hire a contractor already in [[T21-headcount-plan\|T21]]                  | Within planned monthly cost       | COO                              | —                          | CEO                        | T21 status + T09                                          |
| Hire an employee, or any role not in T21                                  | Any                               | —                                | CEO + COO                  | Board                      | Board minute                                              |
| Discount off the quoted rate                                              | ≤ 10%                             | COO / field sales                | —                          | COO weekly                 | CRM (ERPNext)                                             |
| Discount > 10%, free pilot beyond 60 days, non-standard term              | Any                               | —                                | CEO                        | Board                      | T09                                                       |
| Refund or credit note                                                     | ≤ ₹10,000                         | Support/Ops                      | —                          | COO weekly                 | ERPNext credit note                                       |
| Refund or credit note                                                     | > ₹10,000                         | —                                | COO                        | CEO                        | T09                                                       |
| Vendor contract, standard terms                                           | < ₹1 lakh/year                    | COO                              | —                          | CEO                        | T14 + contract file                                       |
| Any contract with liability, IP, data or exclusivity clauses              | Any                               | —                                | CEO + a legal read         | Board                      | Board minute                                              |
| MoU or partnership (IOCL, bank, gateway — all in discussion)              | Any                               | —                                | Board resolution           | All directors              | Board minute                                              |
| Production deploy                                                         | Planned release                   | CEO/CTO                          | —                          | COO before the dealer note | [[T26-release-checklist\|T26]] log                        |
| Emergency hotfix during an incident                                       | Any                               | On-call engineer                 | —                          | Everyone within 24 h       | [[T17-incident-postmortem\|T17]]                          |
| Production data access                                                    | Read-only                         | CEO/CTO grants                   | —                          | Quarterly access review    | Access matrix                                             |
| Restricted personal data (dealer/customer records)                        | Any                               | Nobody by default                | CEO + written need         | COO                        | Access log ([[07-tools-and-it-foundation\|lesson 07]] §9) |
| Dealer-wide broadcast on pricing, an outage over 1 hour, or a partnership | Any                               | —                                | CEO approves wording       | Board                      | T09 + the sent message                                    |
| Statutory filing, legal notice, anything signed for the company           | Any                               | **Never delegated**              | CEO with CA/CS             | Board                      | [[T16-compliance-calendar\|T16]] + binder                 |

Two notes on reading it. The bottom lines are **deliberately generous** — raise them each quarter as evidence accumulates rather than setting them defensively low. And the matrix removes the _obligation_ to ask, never the ability: nothing here stops anyone checking in.

## Related

Lessons [[17-delegation-decision-rights-and-org-design|17]] (the thinking behind it), [[06-money-rails-and-finance-operations|06]] (maker–checker and payment approvals), [[05-legal-and-governance-foundation|05]] (board ratification), [[14-vendors-procurement-and-cost-control|14]] (spend approvals in practice) · Templates [[T01-ceo-coo-operating-agreement|T01]], [[T09-decision-log-and-adr|T09]], [[T07-raci-matrix|T07]], [[T21-headcount-plan|T21]], [[T29-org-chart-and-role-charters|T29]] · [[toolkit/index|COO Toolkit]]
