# T08 — SOP Template

_Toolkit · fills the exercises in [[15-sops-and-playbooks|15 — SOPs and Playbooks]] · Owner: the standard and the index: COO; each SOP: one named owner · Cadence: written when something happens twice; reviewed every 180 days · Workbook tab: `SOP Index` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

An **SOP — standard operating procedure** — is a recurring task written down so that **someone who is not you can do it correctly without asking**. It is the mechanism form of the course rule: _if it happens twice, write it down_ — runbook writers reach the same law from the technical side: "if you've troubleshot the same problem twice, future responders will benefit from documented steps" ([Upstat — runbook vs SOP](https://upstat.io/blog/runbook-vs-sop)). Know the three cousins apart: an **SOP** covers a routine business process (payroll run, dealer onboarding); a **runbook** is its technical sibling — operating a system step by step, often under time pressure; a **playbook** handles decision-heavy scenarios where judgement branches — an incident, a churn-save, a price objection ([Glyde — runbook vs SOP vs playbook](https://glydehq.com/resources/blog/runbook-vs-sop-vs-playbook)). The minimum viable SOP is small — task, owner, trigger, steps, definition of done ([Notion — SOP template for startups](https://www.notion.com/blog/sop-template-for-startups)) — and SOPs are what make a startup stop depending on any single person's memory ([Whale — SOPs for your startup](https://usewhale.io/blog/sops-for-your-startup/)). **No SOP, no delegation; no delegation, no autopilot.**

## When to use

- **The second time anything is done.** The first time is discovery; the second is a pattern.
- **Before any handover.** The SOP is written by whoever does the task today and proven by the person taking it over.
- **Before any automation.** Eliminate → simplify → standardise → automate — the SOP _is_ the standardise step; never automate a mess ([[18-automation-and-ai-in-operations|lesson 18]]).
- Not for one-offs (a to-do), not for judgement-heavy calls (write a playbook), not for pure reference facts (a vault note).

## How to fill (rules)

1. **Write it while doing the task** — screen open, steps recorded as performed, cleaned up on a second pass. SOPs written from memory skip the steps that matter.
2. **Steps start with a verb, one action each, and every step has a check** — the observable proof it worked ("the message shows two grey ticks", "the tab shows no blank cells").
3. **Write for a reader who has never done it:** exact tool names, menu paths, the saved query, the message template. If a step needs tribal knowledge, the knowledge goes into the step.
4. **Metadata first:** id, owner (one name), version, last reviewed, next review (+180 days), trigger. An SOP without a trigger is a document; with one, it is a mechanism.
5. **Id and home:** `SOP-<FUNC>-<NNN>` — OPS, PPL, CUS, REV, ENG, FIN — filed at `sops/sop-<func>-<nnn>.md` in the vault, one row in the `SOP Index` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx). The index, not the folder, is the source of truth for status and review dates.
6. **Sign-off is a performance, not a signature:** the next person runs the task from the SOP while the author watches silently. Every question they ask is a missing step. Then status flips from Draft to Live.
7. **Review every 180 days** or on any process change; log what changed and why; **kill SOPs nobody runs** — a stale SOP is worse than none.
8. Once the task is practised, **distill a checklist at the end** — the full steps train the new person; the checklist guards the veteran against skipped steps ([Runn — The Checklist Manifesto](https://www.runn.io/blog/the-checklist-manifesto-summary)).

## Template

Copy into `sops/sop-<func>-<nnn>.md`; add the index row before writing step 1.

```
# SOP-<FUNC>-<NNN> — <name>

| id | owner | version | last reviewed | next review | trigger |
| --- | --- | --- | --- | --- | --- |
| SOP-___-___ | <one name> | 1.0 | YYYY-MM-DD | YYYY-MM-DD (+180 d) | <what starts this> |

## Purpose
One sentence: what this produces and why it matters.

## Scope
Covers: ...        Does not cover: ...

## Roles
Runs it: <role> · Backup: <role> · Escalate to: <role>

## Prerequisites
Access, tools and inputs that must exist before step 1.

## Steps
1. <verb ...>                     check: <observable proof>
2. <verb ...>                     check: <...>
3. ...

## Exceptions & escalation
If <condition> -> <do this>. Unresolved by <time> -> escalate to <role> via <channel>.

## Outputs
What exists when done: <document / entry / message / tab row>.

## Metrics
How we know it works: <on-time %, error count, minutes taken>.

## Checklist (for the practised operator)
- [ ] ...

## Change log
| date | version | change | by |
| --- | --- | --- | --- |
```

## VSYST example — SOP-OPS-002 Weekly scorecard update

The worked example already indexed in the `SOP Index` tab (vault path `sops/sop-ops-002.md`), condensed:

```
# SOP-OPS-002 — Weekly scorecard update
id SOP-OPS-002 · owner Support/Ops Associate (backup: COO) · v1.1
last reviewed 2026-08-19 · next review 2027-02-15 · trigger: every Monday 09:00

Purpose   The KPI Scorecard tab is filled by 10:00 so the ops meeting reads
          numbers, not memories (T03, T05).
Scope     Covers the scorecard v0 rows. Does not cover monthly budget-vs-actual.
Prereqs   Workbook edit access · saved Mongo aggregations · ERPNext login ·
          Helpdesk/WhatsApp log sheet.

Steps
1. Open the KPI Scorecard tab; confirm this week's W-column date is today.
                                  check: header date = today
2. Run the four saved Mongo queries (activation, weekly active tenants,
   invoices, rate confirmations); paste values as fractions.
                                  check: no blank cells in rows 3–6
3. Copy runway (months) from the Runway & 13-Week Cash tab.
                                  check: matches Friday's cash check
4. Enter demos done from ERPNext CRM (Opportunity list, last 7 days).
                                  check: Domain director confirms count in chat
5. Enter first-response median from the Helpdesk report.
                                  check: value present, in hours
6. Post the tab link in the ops channel.
                                  check: message timestamp <= 10:00

Exceptions  Source unreachable -> carry last week's value, write "stale" in
            Notes, add an issue to T03's list. Any query failing -> escalate
            to COO by 09:30 on WhatsApp.
Outputs     Filled W column; exceptions listed in the meeting note.
Metrics     Filled-by-10:00 streak; stale-cell count per month.
Change log  1.1 · 2026-08-19 · rate-confirmation query rewritten after schema
            change · COO
```

## Related

Lessons [[15-sops-and-playbooks|15]], [[07-tools-and-it-foundation|07]], [[10-customer-operations-support-and-success|10]] · Templates [[T25-customer-support-sop|T25]] (a filled SOP in this format), [[T26-release-checklist|T26]], [[T12-onboarding-checklist|T12]], [[T17-incident-postmortem|T17]], [[T09-decision-log-and-adr|T09]] · [[COO-Docs/toolkit/index|COO Toolkit]]
