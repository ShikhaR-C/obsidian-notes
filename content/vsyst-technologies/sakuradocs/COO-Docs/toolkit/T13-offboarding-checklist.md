# T13 — Offboarding Checklist

_Toolkit · fills exercise 13.4 in [[09-people-operations|09 — People Operations]] (the mirror half) · Owner: COO · Cadence: run on every exit — employee, contractor or probation end — starting day 0 · Workbook tab: none — the revocation list is the access list of [[T12-onboarding-checklist|T12]] run in reverse._

## Purpose

Exits are rare, emotional and rushed — exactly the conditions under which access lingers, knowledge walks out undocumented, and a final settlement drags into a dispute. This checklist makes the day mechanical. Its first law is the one lean-team security guides treat as a baseline control: **immediate access revocation on offboarding** ([Sola Security — security for startups and lean teams, 2026](https://sola.security/blog/startup-lean-teams-security-guide/); [PolicyOwn — startup compliance checklist 2026](https://policyown.com/blog/startup-compliance-checklist-2026)). Its second is that the revocation list is **an exact copy of [[T12-onboarding-checklist|T12]]'s provisioning list** — if the two ever disagree, an access grant went unrecorded, and that is the finding.

## When to use

- **Every exit, whatever the flavour**: resignation, non-confirmation at probation, termination, a contractor's engagement ending, even a role change that sheds access.
- **Day 0** is the day the exit becomes definite (resignation accepted, decision made) — not the last working day. For involuntary exits, day 0's access block happens **before** the conversation ends.
- The timeline below assumes a notice period; compress it to hours when there is none.

## How to fill (rules)

1. **Access first, always.** Revocation (or downgrade to read-only during notice, per your call) within 24 hours of day 0; **rotate every shared secret the person could have seen** — Wi-Fi, any shared vault items, API keys in their reach, the WhatsApp phone PIN.
2. **Handover is documents, not conversations.** The exit is complete when their SOPs are updated by them ([[T08-sop-template|T08]]), their tickets/leads/tasks are reassigned in the systems, and the successor has run each recurring task once from the SOP.
3. **F&F runs through the CA** against a written computation the person sees before signing.
4. **The exit interview is 20 minutes, written down**, and read at the next ops meeting — leavers tell you what stayers won't.
5. **Announce once, plainly** — team first, then any dealers the person served, with the new contact. Silence breeds stories.
6. **Close the registers**: T14 seats freed, headcount plan updated, the T12/T13 pair filed in the person's folder in Drive › 03-People.

## Template

**Day 0 — access** (within 24 hours; involuntary: immediately)

| Tool (mirror of T12's list)                  | Action                                                                             | Owner   | Done  |
| -------------------------------------------- | ---------------------------------------------------------------------------------- | ------- | ----- |
| Google Workspace                             | Suspend or downgrade; transfer Drive ownership; set mail forwarding to the manager | COO     | - [ ] |
| Bitwarden                                    | Remove from organisation; **rotate items in their collections**                    | COO     | - [ ] |
| GitHub org                                   | Remove membership; revoke personal access tokens and deploy keys they created      | CEO/CTO | - [ ] |
| AWS / MongoDB Atlas                          | Delete IAM user / project role; rotate any keys in their reach                     | CEO/CTO | - [ ] |
| ERPNext / Frappe Helpdesk                    | Disable user; reassign open tickets and leads                                      | COO     | - [ ] |
| Play Console / App Store Connect             | Remove user                                                                        | CEO/CTO | - [ ] |
| WhatsApp Business phone                      | Retrieve or re-register; change PIN                                                | COO     | - [ ] |
| Bank / gateway (if any view or maker rights) | Remove per board resolution / DoA ([[T22-delegation-of-authority-matrix\|T22]])    | COO     | - [ ] |
| Anything else on their T12 sheet             | Revoke                                                                             | per row | - [ ] |

**Day 1 — device and handover start**

- [ ] Laptop, test phones, SIMs, DSC tokens, keys returned; device wiped after data transfer — _CEO/CTO_
- [ ] Handover list agreed in writing: SOPs to update, tasks to reassign, credentials/contacts to document — _manager_
- [ ] Personal belongings, parking, office access sorted — _COO_

**Week 1 — handover, money, goodbye**

- [ ] SOPs updated by the leaver; successor runs each recurring task once from the SOP — _manager_
- [ ] Tickets, leads, dealers reassigned in ERPNext/Helpdesk; out-of-office and alias routing set — _COO_
- [ ] **F&F computation** with the CA: salary to last day, leave encashment per policy, gratuity if applicable (five years' service, or one year for fixed-term — [[09-people-operations|lesson 09]] §5), reimbursements, recoveries (advances, unreturned kit), TDS; payout date per policy — all **VERIFY LIVE** with the CA
- [ ] Form 16 / final payslip timeline told to the leaver in writing — _CA/COO_
- [ ] **Exit interview** (20 min, written): why leaving, what would have kept you, what should the next person know, what breaks when you go? — _COO_
- [ ] Announcement to the team; dealers the person served messaged with the new contact — _COO_
- [ ] Registers closed: [[T14-vendor-and-tool-register|T14]] seats, `Headcount Plan` tab, T12/T13 pair filed — _COO_

## VSYST example (illustrative)

A developer-contractor's engagement ends on delivery. Day 0: GitHub write access removed, the scoped Atlas dev-project role deleted, the one deploy key he created rotated — fifteen minutes, because his T12 sheet listed all three. Day 1: his written handover updates the deploy notes SOP; the CEO/CTO runs one deploy from the notes with him watching. Week 1: final invoice paid with 194J TDS deducted (CA confirms the section), a two-line thanks in the team chat, T14's seat count drops by one. Nothing to argue about later, because nothing depended on memory.

## Related

Lessons [[09-people-operations|09]], [[07-tools-and-it-foundation|07]] · Templates [[T12-onboarding-checklist|T12]], [[T14-vendor-and-tool-register|T14]], [[T22-delegation-of-authority-matrix|T22]], [[T08-sop-template|T08]] · [[toolkit/index|COO Toolkit]]
