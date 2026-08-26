# T01 — CEO–COO Operating Agreement

_Toolkit · fills the exercises in [[03-the-coo-core-value-and-the-ceo-coo-contract|03 — The COO's core value and the CEO–COO contract]] · Owner: CEO and COO jointly · Cadence: sign once in Week 0, re-sign at every quarterly review · Workbook tab: none (the ₹ thresholds live in the `DoA Matrix` tab of [the workbook](vsyst-coo-workbook.xlsx) via [[T22-delegation-of-authority-matrix|T22]])._

## Purpose

One signed page that says **who owns what, who decides what, how you disagree, and how you talk**. CEO–COO failures are "rarely about skill… almost always about clarity" ([COO Alliance](https://cooalliance.com/how-to-build-a-ceo-coo-partnership-that-actually-works/)); the best arrangements show "clear delineation… and high trust", the worst "ambiguity, competition for credit, or different views on priorities" ([Startups.com — COO](https://www.startups.com/lexicon/coo)); in founder-led companies authority gets "formally promised and informally withdrawn" ([Alder Koten](https://charliesolorzano.me/2026/03/17/coo-founder-led-company-failure/)). Writing the rights down and re-reading them quarterly is the mechanism against all three.

## When to use

- **Week 0**, before any other template — every later mechanism assumes the seat has edges.
- When the seat changes hands (a director swaps hats; a COO is hired).
- When the same argument happens twice (a hire, a spend, a promise to a dealer) — that is a missing line here, not a personality problem.
- At every quarterly review ([[T19-quarterly-plan-and-review|T19]]): re-sign or amend.

## How to fill (rules)

1. Fill it **together, in one sitting (60–90 min)**. Nobody drafts alone and sends it for approval.
2. **One owner per function.** "Both" is not an owner. Where a function is genuinely shared (cash), name a Responsible and an Accountable exactly as in [[T07-raci-matrix|T07]].
3. Decision rights use four words only: **decide alone · consult · joint · escalate** (to the board of three directors). Ask the CEO the executive-search diagnostic — "which operational decisions will you stop making once the COO seat is running?" ([Alder Koten](https://charliesolorzano.me/2026/03/17/coo-founder-led-company-failure/)) — and paste the answer into section B verbatim.
4. Money thresholds are **not** repeated here; they live in T22. This page records the principle and links.
5. Copy the no-surprises rule as written; do not soften it.
6. Set the review date **before** signing. Typed names in the vault are enough between directors; a hired COO's version goes through e-sign (Zoho Sign / Leegality — prices **VERIFY LIVE** on the vendor pages).
7. Keep the filled copy in `coo-workbook/`; log the signing in [[T09-decision-log-and-adr|T09]].

## Template

```
CEO–COO OPERATING AGREEMENT — VSYST Technologies Pvt. Ltd.
Version ___ · Signed ______ · Review date ______ (quarterly) · CEO ______ · COO ______
```

**A. Division of labour** (one owner per row)

| Function                                                                      | Owner              | Backup                    | Edges / notes                                                                 |
| ----------------------------------------------------------------------------- | ------------------ | ------------------------- | ----------------------------------------------------------------------------- |
| Vision, strategy, product direction, roadmap                                  | CEO                | COO                       | COO consulted on capacity and sequencing                                      |
| Engineering, architecture, code, releases (the code)                          | CEO/CTO            | Developer                 | COO owns the release _process_ ([[T26-release-checklist\|T26]]), not the code |
| Operating cadence — meetings, scorecard, decision log                         | COO                | CEO                       |                                                                               |
| Finance operations — bank, payments, collections, close inputs, cash forecast | COO                | CEO                       | Books and audit with the CA — [[finance/00_README\|Finance for Founders]]     |
| Legal, governance, compliance calendar (with CA/CS)                           | COO                | CEO                       |                                                                               |
| People — hiring process, contracts, onboarding, policies, payroll             | COO                | CEO                       | Final hire/fire: section B                                                    |
| Customer support and dealer onboarding                                        | COO                | Support/Ops               |                                                                               |
| Revenue operations — pipeline hygiene, collections, pricing ops               | COO                | Domain director           | Field selling and dealer relationships: Domain director                       |
| Partnerships in discussion (IOCL, bank/gateway)                               | CEO (relationship) | COO (tracker, next steps) |                                                                               |
| Vendors, tools, IT, security, access                                          | COO                | Developer                 |                                                                               |
| Founder-only relationships (investors, key OMC contacts)                      | CEO                | —                         |                                                                               |

**B. Decision rights** (decide alone · consult · joint · escalate)

| Decision                                        | CEO                                 | COO                                                                            | Rule / where                                                 |
| ----------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| Product roadmap and priorities                  | decide alone                        | consulted                                                                      |                                                              |
| Architecture, tech stack                        | decide alone                        | informed                                                                       |                                                              |
| Hire / fire an employee                         | joint                               | joint                                                                          | COO recommends via [[T10-hiring-scorecard-and-process\|T10]] |
| Engage / end a contractor within threshold      | informed                            | decide alone                                                                   | threshold in T22                                             |
| Spend                                           | per T22                             | per T22                                                                        | two signatures above the T22 line                            |
| Pricing, discounts, refunds                     | decide alone (until pricing is set) | consulted                                                                      | then T22                                                     |
| Promises to dealers (SLA, features, dates)      | consulted                           | decide alone inside [[T25-customer-support-sop\|T25]] SLA; escalate outside it |                                                              |
| Policies (POSH, leave, expenses, IT)            | consulted                           | decide alone                                                                   | legal read by CA/CS                                          |
| Public statements, dealer broadcasts            | joint                               | joint                                                                          |                                                              |
| Contracts, MoUs, NDAs that bind the company     | joint                               | joint                                                                          |                                                              |
| Vendor and tool selection within budget         | informed                            | decide alone                                                                   | register in [[T14-vendor-and-tool-register\|T14]]            |
| Cash red line, 13-week forecast                 | joint                               | joint                                                                          | [[T20-budget-vs-actual-and-cash-forecast\|T20]]              |
| Any one-way door                                | escalate                            | escalate                                                                       | board of three; log in T09                                   |
| CEO's answer to "decisions I will stop making": |                                     |                                                                                | **\_\_\_\_**                                                 |

**C. Money.** Thresholds, approvers and the two-signature rule live in T22 and the `DoA Matrix` tab. Record here only: "The COO may commit recurring spend up to ₹**\_\_** /month per item and ₹**\_\_** one-off without the CEO; above that, T22 applies." (Illustrative: ₹10,000/month, ₹25,000 one-off. A generic delegation-of-authority guide puts a bootstrapped startup's first line near \$5,000 — [Tallyfy](https://tallyfy.com/delegation-of-authority-matrix-template/) — set yours from the runway, not the guide.)

**D. Weekly CEO–COO 1:1** — 45 min, fixed slot, moved but never cancelled ([Cameron Herold — The Second in Command](https://cameronherold.com/thesecondincommand/)):

```
1. Scorecard exceptions (5)   what is red, what the COO is doing about it
2. Decisions needed (10)      written up beforehand with a recommendation — "writing vs talking"
                              (Mochary: https://blas.com/the-great-ceo-within/)
3. Roadmap <-> capacity (10)  what ops needs from engineering and vice versa
4. People and customers (10)  hires, contractors, dealer escalations, partners
5. Feedback both ways (5)     one thing each
6. Actions and log (5)        owner + date; T09 entries
```

**E. Disagreement and escalation protocol**

1. Argue in private, in writing first: the proposer writes issue → options → recommendation, one page.
2. Decide by table B. If **joint** and still split after two conversations, the tie-break is (choose now): ☐ the third director decides · ☐ the CEO decides and the COO commits ("disagree and commit").
3. One voice outside the room. The COO absorbs the tough calls; the CEO backs the COO publicly ([Herold](https://cameronherold.com/thesecondincommand/)).
4. Two-way-door decisions: decide fast, log, set a review date. One-way doors: slow, joint, board ([Amazon's Type 1 / Type 2 decisions](https://growthmethod.com/two-way-doors/)).
5. Team escalation path: team → COO → CEO. The CEO does not overrule the COO in front of the team; "talk to the COO" — and mean it ([Alder Koten](https://charliesolorzano.me/2026/03/17/coo-founder-led-company-failure/)).

**F. No-surprises rule.** Neither of us learns bad news from someone else. Anything that could hit cash, a customer, a filing, a person or the product's reputation is said the same day — verbally first, written within 24 hours. Bad news early is professionalism; bad news late is betrayal ([[startup-operations-plan|ops plan]], client realities).

**G. Review and signatures.** Review date **\_\_** · CEO **\_\_** (date) · COO **\_\_** (date) · Witness (third director) **\_\_**.

## VSYST example — when one person wears both hats

At a three-director company the CEO and COO seats may sit on one person on different days. The agreement still applies; add rituals that **force the switch**:

- **Calendar by hat.** "COO Monday" (scorecard, ops meeting, cash, compliance) and "CEO Wednesday–Thursday" (roadmap, code, partners). A decision that belongs to the other hat is deferred to its day, not made in the wrong block.
- **The 1:1 becomes a written self-review** (30 min): the COO hat writes the exception report; the CEO hat answers in writing. It feels artificial and it works, because it produces the artefact.
- **"Joint" still means two people:** any joint decision made by one person under both hats needs the domain-expert director consulted and logged in T09.
- Signature lines: the same person signs under both titles; the third director witnesses.

## Related

Lessons [[01-what-is-a-coo|01]], [[03-the-coo-core-value-and-the-ceo-coo-contract|03]], [[17-delegation-decision-rights-and-org-design|17]] · Templates [[T22-delegation-of-authority-matrix|T22]], [[T09-decision-log-and-adr|T09]], [[T04-one-on-one-template|T04]], [[T07-raci-matrix|T07]], [[T30-coo-charter-and-90-day-plan|T30]] · [[COO-Docs/toolkit/index|COO Toolkit]]
