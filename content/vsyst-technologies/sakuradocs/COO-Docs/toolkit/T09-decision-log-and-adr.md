# T09 — Decision Log and ADR

_Toolkit · fills the exercises in [[02-how-a-coo-thinks|02 — How a COO Thinks]] and [[08-the-operating-cadence|08 — The Operating Cadence]] · Owner: COO keeps the log; whoever decides writes the entry · Cadence: continuous; review dates checked in the weekly ops meeting · Workbook tab: `Decision Log` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

A **decision log** is the company's memory of _what was decided, by whom, from which options, and what happened next_ — one row per decision. Three directors from one family will remember the same decision three different ways within a month; the log replaces those three memories with one record, and its **review date** column turns every entry into the company's cheapest learning loop ([[08-the-operating-cadence|lesson 08]] §12).

The log's most useful column is the **door type**. Bezos split decisions into Type 1 — **one-way doors**, irreversible or nearly, to be made "methodically, carefully, slowly" — and Type 2 — **two-way doors**, reversible, which "most decisions" are and which should be decided fast by small groups ([Two-way doors](https://growthmethod.com/two-way-doors/); [Type 1 vs Type 2 decisions](https://ashikuzzaman.com/2025/03/03/amazons-type-1-vs-type-2-decisions-a-framework-for-effective-decision-making/)). Typing the door as you log it forces the right speed: slow and written for one-way, fast with a 30-day review for two-way.

An **ADR — architecture decision record** — is the fuller sibling for technical and structural decisions: title, status, context, decision, consequences. It is the lightweight standard the software world already uses ([adr.github.io](https://adr.github.io/)), and MADR is its most practical template ([MADR](https://adr.github.io/madr/)). VSYST uses the row for business decisions and row + ADR for technical ones — same log, two depths.

## When to use

The rule, from [[02-how-a-coo-thinks|lesson 02]] §7 and enforced by the cadence in [[08-the-operating-cadence|lesson 08]] §12 — log:

- **Every one-way door**, always.
- **Every spend above the DoA threshold** ([[T22-delegation-of-authority-matrix|T22]]).
- **Anything two directors might remember differently in six months** — partnership terms, pricing direction, who owns what.
- Two-way doors when they are cross-functional or above a materiality line (the workbook tab uses **> ₹25k, illustrative**).
- An **ADR in addition to the row** for technical/structural operations decisions: an OTP-provider abstraction, a hosting move, a data-retention rule.

Not logged: routine to-dos (they live in the meeting's to-do list), matters an SOP already governs, and personal preferences that bind nobody. A log that records everything gets read by no one.

## How to fill (rules)

1. **Write the row in the meeting, not after it.** The ops meeting's conclude segment, the 1:1's decisions section and the quarterly session all end with the scribe entering the row before anyone leaves ([[T03-weekly-ops-meeting-agenda|T03]]). A log written from memory on Friday is fiction.
2. **Options include the rejected ones, honestly stated.** "Options: (a) the thing we did" is not a record; the value at review time is knowing what you turned down and why.
3. **Type the door when logging.** Test: if reversing would cost clearly more than deciding did, it is one-way — run a pre-mortem first (lesson 02 §7) and sleep on it. Everything else is two-way: decide today, set a near review date.
4. **Review dates are mandatory** — 30–90 days for two-way doors, the natural checkpoint for one-way ones. The ops meeting's to-do review includes "decision reviews due this week"; in the workbook tab, a past review date with an empty outcome turns amber. Fill **Outcome** at review — that closes the loop.
5. **Decided by names the hat, not just the person.** At a company where one director wears CEO and COO hats on different days, tag entries CEO-hat / COO-hat ([[03-the-coo-core-value-and-the-ceo-coo-contract|lesson 03]] §5.7).
6. **IDs and homes.** Log rows are numbered in the `Decision Log` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) (the source of truth). ADRs are `ADR-NNN-<slug>.md` in a `decisions/` folder in the vault, linked from the row's Link column; number them once, never reuse. Emergency decisions made outside the rhythm are logged within 24 hours with the reason ([[06-money-rails-and-finance-operations|lesson 06]] §3).

## Template

**The decision log** — identical columns to the `Decision Log` tab; the tab is the working copy, this table is the master:

| #   | Date | Decision | Context (why now) | Options considered | Decided by | Type (door)       | Review date | Outcome / what happened | Link (ADR / memo) |
| --- | ---- | -------- | ----------------- | ------------------ | ---------- | ----------------- | ----------- | ----------------------- | ----------------- |
|     |      |          |                   |                    |            | one-way / two-way |             |                         |                   |

**The ADR skeleton** — copy into `decisions/ADR-NNN-<slug>.md`; add the log row first:

```
# ADR-NNN — <title, an active sentence: "Put the OTP provider behind an interface">

status: proposed | accepted | superseded by ADR-MMM
date: YYYY-MM-DD · deciders: <names/hats> · log row: #NN

## Context
What forces this decision now — the problem, the constraint, the deadline.

## Options considered
1. <option> — main upside / main downside
2. <option> — ...

## Decision
What we chose, in one sentence, and the door type.

## Consequences
Good: what this buys us. Bad: what we accept. What would make us revisit.
```

If even that feels heavy, MADR's one-line "Y-statement" form is enough: _In the context of <use case>, facing <concern>, we decided <option> to achieve <quality>, accepting <downside>_ ([MADR](https://adr.github.io/madr/)).

## VSYST example (illustrative)

The three starter rows already in the `Decision Log` tab, condensed (dates and review windows illustrative):

| #   | Decision                                                                                                                                             | Decided by                 | Door    | Review    | Link                                                                             |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------- | --------- | -------------------------------------------------------------------------------- |
| 1   | Monetisation direction: company-level subscription per GSTIN, unlimited users, billing on the web, app gated server-side; prices to be decided later | Founders (all 3 directors) | One-way | +6 months | [[app-store-economics/08-dzzlo-subscription-strategy\|subscription strategy]]    |
| 2   | Adopt the workbook in Google Sheets as the scorecard/OKR/cash system until a Metabase dashboard is justified                                         | COO                        | Two-way | +90 days  | [[16-metrics-dashboards-and-scorecards\|lesson 16]] / [[T05-kpi-scorecard\|T05]] |
| 3   | Standardise on ERPNext for accounting + CRM; hosting (Frappe Cloud vs self-hosted) decided after a 30-day trial                                      | CEO/CTO + COO              | Two-way | +30 days  | [[ERPNext-Implementation-Guide\|ERPNext guide]]                                  |

And one illustrative ADR, in the skeleton's shape: **ADR-001 — Put the SMS/OTP provider behind an interface.** Context: driver-OTP delivery is a single point of failure on one vendor. Options: (a) integrate the vendor's SDK directly everywhere; (b) one internal interface with the vendor behind it (chosen); (c) two live providers with failover now. Decision: (b), a two-way door — (c) becomes cheap later because of it. Consequences: one extra layer to maintain; provider swap or failover no longer touches product code. Review: when OTP delivery rate first appears on the scorecard ([[T05-kpi-scorecard|T05]]).

## Related

Lessons [[02-how-a-coo-thinks|02]] (doors, the log as hygiene), [[08-the-operating-cadence|08]] (the log as ritual), [[17-delegation-decision-rights-and-org-design|17]] (who may decide) · Templates [[T22-delegation-of-authority-matrix|T22]] (the ₹ thresholds that trigger logging), [[T07-raci-matrix|T07]] (a DACI for one big decision gets logged here), [[T03-weekly-ops-meeting-agenda|T03]], [[T19-quarterly-plan-and-review|T19]] (decisions-needed section feeds the log) · [[COO-Docs/toolkit/index|COO Toolkit]]
