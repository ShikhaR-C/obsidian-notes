# T12 — Onboarding Checklist

_Toolkit · fills exercise 13.4 in [[09-people-operations|09 — People Operations]] · Owner: COO runs the checklist; every row has its own owner · Cadence: per joiner, starting the day the offer is accepted; the access list re-synced with [[T14-vendor-and-tool-register|T14]] at the quarterly access review · Workbook tab: none — the access list mirrors `Vendor & Tool Register` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

Onboarding decides the first 90 days: a joiner who ships a real task in week 1 and knows exactly what "good at 30/60/90 days" means becomes productive in weeks; a joiner who spends day 1 hunting for logins learns that this company improvises. The checklist also carries the security baseline — accounts, device, MFA and policy acknowledgement land **on day one**, which is precisely what IT-onboarding practice prescribes ([iFeeltech — new-employee IT onboarding checklist](https://ifeeltech.com/blog/new-employee-it-onboarding-security-checklist)), and every access granted here is a line [[T13-offboarding-checklist|T13]] will one day revoke. The number this template owes the scorecard is **time-to-productivity** — days from start to the first unassisted outcome ([[09-people-operations|lesson 09]] §8).

## When to use

- **Every employee**, from the day the offer is accepted — pre-day-1 starts then, not on day 1.
- **Contractors** get the trimmed variant: contract + IP assignment signed ([[T11-offer-letter-and-contract-checklists|T11]]), scoped access only, device rules if they touch company data, no 30-60-90.
- **A director taking on a new function** gets the access rows and the first-week plan — the seat changes even when the person is old.

## How to fill (rules)

1. **Every row has one owner**, named before day 1. "HR does it" is nobody; at VSYST the owners are the COO, the CEO/CTO (technical access) and the buddy.
2. **Access comes from the register, at least privilege.** The provisioning table below mirrors [[T14-vendor-and-tool-register|T14]] and the access matrix of [[07-tools-and-it-foundation|lesson 07]] §4 — grant the role's row, nothing more, and note each grant so the quarterly access review has a trail.
3. **2FA on every account before lunch on day 1.** No shared logins, no personal-Gmail workarounds, device policy signed (disk encryption, screen lock, auto-updates).
4. **A buddy is named pre-day-1** — the person the joiner shadows and asks the questions they won't ask you.
5. **The first-week plan is written before day 1** and ends with one real task shipped by Friday.
6. **30-60-90 comes from the role charter** ([[T29-org-chart-and-role-charters|T29]]): at 30 days "can they do it with help?", at 60 "alone?", at 90 "can they improve it?" — each check-in leaves a short written note.
7. **Mirror every access grant into T13 the day you grant it.** Revocation must be a copy, not a memory test.

## Template

**Pre-day-1** (starts the day the offer is accepted)

| Item                                                                                                                  | Owner   | Done  |
| --------------------------------------------------------------------------------------------------------------------- | ------- | ----- |
| Offer, appointment letter, employment/contractor agreement signed ([[T11-offer-letter-and-contract-checklists\|T11]]) | COO     | - [ ] |
| PAN, Aadhaar, bank details, previous Form 16 collected                                                                | COO     | - [ ] |
| Laptop imaged, disk-encrypted; test phone if the role needs one                                                       | CEO/CTO | - [ ] |
| Workspace account created; added to the right group aliases                                                           | COO     | - [ ] |
| Bitwarden seat; role's shared collections only                                                                        | COO     | - [ ] |
| Tool access per the provisioning table below                                                                          | per row | - [ ] |
| Buddy named and briefed; first-week plan written                                                                      | COO     | - [ ] |
| Desk/SIM/field kit as the role needs                                                                                  | COO     | - [ ] |

**Access provisioning by tool** (grant only the role's row; mirror lesson 07 §4)

| Tool                             | Support/Ops                | Field sales      | Developer (contractor)               | Grant by | Granted on |
| -------------------------------- | -------------------------- | ---------------- | ------------------------------------ | -------- | ---------- |
| Google Workspace                 | User                       | User             | External guest (Drive share)         | COO      |            |
| Bitwarden                        | Support collection         | Sales collection | Infra-dev collection                 | COO      |            |
| GitHub org                       | —                          | —                | Write on assigned repo               | CEO/CTO  |            |
| AWS / MongoDB Atlas              | —                          | —                | Scoped role, dev project, time-boxed | CEO/CTO  |            |
| ERPNext                          | Support agent + Sales user | Sales user       | —                                    | COO      |            |
| Frappe Helpdesk                  | Agent                      | —                | —                                    | COO      |            |
| Play Console / App Store Connect | Customer-support view      | —                | Developer/release role if needed     | CEO/CTO  |            |
| WhatsApp Business phone          | Daily operator             | —                | —                                    | COO      |            |

**Day 1**

- [ ] Welcome by the CEO (30 min); team introductions — _COO_
- [ ] All six policies acknowledged in writing ([[T27-policy-handbook-toc|T27]]); device policy signed — _COO_
- [ ] **2FA enabled on every account before lunch** — _joiner, COO checks_
- [ ] Vault tour: this course, the SOP index, the scorecard, where notes live — _buddy_
- [ ] First-week plan handed over in writing — _COO_

**Week 1**

- [ ] Shadow the buddy on real work (support: sit on the queue; field roles: a day at the pump with the domain-expert director) — _buddy_
- [ ] Read the role's SOPs; every question asked becomes an SOP fix ([[T08-sop-template|T08]]) — _joiner_
- [ ] **One real task shipped by Friday** — _joiner, buddy signs off_
- [ ] End-of-week 1:1; first-week plan reviewed ([[T04-one-on-one-template|T04]]) — _manager_

**30-60-90** (from the role charter's outcomes)

| Check-in | Question                                                                                         | Artefact                    |
| -------- | ------------------------------------------------------------------------------------------------ | --------------------------- |
| Day 30   | Doing the core tasks with help? Access complete? Surprises?                                      | Written note in the 1:1 doc |
| Day 60   | Doing them alone, to the SOP? First metric owned on the scorecard?                               | Written note                |
| Day 90   | Improving them — an SOP edited, a macro added, a number moved? Probation decision per the letter | Written note + decision     |

## VSYST example (illustrative)

First hire, Support/Ops Associate, offer accepted Tuesday. By Friday: agreement e-signed, laptop encrypted, `firstname@` created and added to `support@`, Bitwarden Support collection shared, ERPNext support-agent role, Helpdesk agent seat, customer-support view on the Play Console, and the WhatsApp Business phone scheduled for handover in week 2 (after shadowing). Buddy: the technical founder for the queue, the domain-expert director for day 2 at the pump. First-week plan ends with "close five P3 tickets from macros by Friday". The 30-day note reads against T29's outcome: "runs P3s from macros unaided". Every granted row was copied into T13 the same day.

## Related

Lessons [[09-people-operations|09]], [[07-tools-and-it-foundation|07]], [[10-customer-operations-support-and-success|10]] · Templates [[T13-offboarding-checklist|T13]], [[T14-vendor-and-tool-register|T14]], [[T29-org-chart-and-role-charters|T29]], [[T10-hiring-scorecard-and-process|T10]], [[T04-one-on-one-template|T04]] · [[toolkit/index|COO Toolkit]]
