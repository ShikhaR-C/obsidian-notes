# T17 — Incident and Postmortem

_Toolkit · fills exercise 14.1 in [[12-product-and-engineering-operations|12 — Product and Engineering Operations]] and the escalation protocol in [[10-customer-operations-support-and-success|10 — Customer Operations]] · Owner: COO owns the process; the on-call person owns each incident · Cadence: used at every SEV1/SEV2; postmortem within five working days; the on-call rota lives on the `Cadence Calendar` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

The difference between a company that handles incidents and one that survives them by luck is **written in advance**: severity levels nobody debates at 2 AM, a rota with one name on it, comms templates ready to paste, and a postmortem habit that turns each failure into fixes. The postmortem is **blameless** — Google's SRE practice, which "focuses on identifying the contributing causes of the incident without indicting any individual or team for bad or inappropriate behavior" ([Google SRE Book — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)); the practical craft of running one well is documented at [incident.io — postmortem best practices](https://incident.io/blog/sre-incident-postmortem-best-practices). In a family founding team, blamelessness is not a nicety — it is the only way the record stays honest ([[12-product-and-engineering-operations|lesson 12]] §5).

## When to use

- **The moment a SEV1 or SEV2 is declared** (table below) — the timeline log starts with the declaration.
- **A suspected data breach is automatically SEV1**, and it starts two legal clocks: CERT-In within 6 hours, DPDP intimation without delay plus a 72-hour report — the breach one-pager in lesson 12 §9 names who calls whom; **VERIFY LIVE** with the lawyer.
- **The postmortem follows every SEV1/2 within five working days.** SEV3s go to the normal ticket queue ([[10-customer-operations-support-and-success|lesson 10]]) — no ceremony.

## How to fill (rules)

1. **Severity is decided by the table, not the adrenaline.** Argue edge cases in the calm (exercise 14.1), never mid-outage.
2. **One incident, one owner** — the on-call person until they explicitly hand over. The rota gives "who is watching?" exactly one answer, every week.
3. **Roles split during SEV1/2**: the CEO/CTO fixes; the COO (or support owner) runs comms and keeps the timestamped log. The log becomes the postmortem's spine.
4. **Stabilise before diagnosing** — roll back first, understand later.
5. **Comms promise the next update time, never a fix time you don't have.** Dealers punish silence, not outages. Every dealer message carries: what's affected, what still works, when the next update comes.
6. **Blameless means causes, not culprits** — write "the deploy lacked a rollback plan", never "X pushed a bad build".
7. **Action items get owners and dates and are read at the weekly ops meeting until closed** — an incident whose actions never land repeats on schedule. MTTR and incident counts feed the scorecard ([[T05-kpi-scorecard|T05]]).
8. **Review rule:** the finished postmortem is read at the next ops meeting, and its lessons update this template, the alerts, or an SOP the same week.

## Template

**Severity table** (from [[12-product-and-engineering-operations|lesson 12]] §5 — re-argue the DZZLO examples with the CEO/CTO and keep the agreed version here):

| Sev      | Definition                                          | DZZLO examples                                                                                                           | Response                                                                            |
| -------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| **SEV1** | Core loop down or data at risk for many tenants     | **API down in the 10 PM–6 AM rate window**; OTP delivery dead during dispatch hours; data corruption or suspected breach | Page on-call now; all hands; dealer comms within 60 min; fix before everything else |
| **SEV2** | Major function degraded, or one tenant hard-blocked | Rate-confirmation pushes failing; invoice generation broken; a tenant locked out                                         | Work within hours; affected dealers informed; fix or workaround same day            |
| **SEV3** | Annoying, not blocking                              | Cosmetic bugs; one user's how-to confusion                                                                               | Ticket queue, normal SLA                                                            |

**Incident timeline log** (start at declaration; timestamps as events happen):

```
INC-YYYY-MM-DD-NN · SEV_ · declared HH:MM by <name>
What's broken (one line): …            Tenants affected: …
Owner (on-call): …    Fixing: …    Comms & log: …

HH:MM  detected via <alert / dealer report>
HH:MM  declared SEV_; roles split
HH:MM  <action> → <observed result>
HH:MM  dealer comms #1 sent (template below)
HH:MM  rolled back / mitigated — service state: …
HH:MM  resolved; monitoring continues
Next: postmortem owner <name>, due <date +5 wd>
```

**Comms templates**

_Internal (chat, at declaration):_ `SEV1 declared HH:MM — <what's broken>. <CTO> fixing, <COO> comms+log. War channel: here. Next internal update HH:MM.`

_Dealer-facing WhatsApp (plain English + one Hindi line; name the sender):_

```
DZZLO update: <what's affected — e.g. new orders and invoices are not
working right now>. Your data is safe. <What still works — e.g. you can
still see rates, ledgers and old invoices>. We are fixing it.
Next update by <time>.
App mein abhi dikkat aa rahi hai — aapka data surakshit hai,
hum theek kar rahe hain. Agla update <time> tak.
— <name>, VSYST support
```

_Resolution:_ `Fixed at <time>: <what was wrong, one plain line>. Everything is working; please message us if anything still looks off. Sab theek ho gaya hai — koi dikkat ho to yahin message karein. — <name>`

**Blameless postmortem skeleton** (one vault note per SEV1/2, `postmortems/INC-….md`):

```
# Postmortem INC-YYYY-MM-DD-NN — <title>       status: draft / final
Summary      3 lines: what broke, for how long, for whom.
Impact       Tenants affected · duration · deliveries/invoices blocked ·
             SLA misses · ₹ estimate if meaningful.
Timeline     Pasted from the incident log, cleaned.
Root causes  The contributing causes (usually several). Ask "why" until
             the answer is a mechanism, not a person.
What went well   Detection, rollback, comms — keep doing these.
Action items
| # | Action | Owner | Due | Status |
| --- | --- | --- | --- | --- |
Read at ops meeting on: <date> · Lessons folded into: <T17/T25/T26/alerts/SOP-…>
```

## VSYST example (illustrative)

9:40 PM: the scorecard's OTP row was already amber; now three dealers message "driver OTP not aaya" within ten minutes — the on-call declares SEV1 (dispatches blocked, rate window opening). 9:48: internal alert posted; CEO/CTO confirms the SMS vendor's panel shows failures; log started. 9:55: dealer comms #1 goes to affected dealers — deliveries paused, data safe, ledger and rates still visible, next update 10:30. 10:10: the documented fallback for confirming deliveries is relayed to the two dealers with vehicles standing. 10:40: vendor recovers; synthetic OTP verified; resolution message sent. Postmortem (five days later, 40 minutes): root causes — single SMS vendor, no balance/failure alert distinct from the delivery-rate row; actions — vendor-failure alert (Developer, dated), second-route onboarding docs (Developer, dated), fallback macro added to [[T25-customer-support-sop|T25]]; [[T15-risk-register|T15]] row 6 re-scored. Total paperwork: two pages. Total argument: none.

## Related

Lessons [[12-product-and-engineering-operations|12]], [[10-customer-operations-support-and-success|10]], [[13-compliance-calendar-risk-and-insurance|13]] · Templates [[T25-customer-support-sop|T25]], [[T15-risk-register|T15]], [[T26-release-checklist|T26]], [[T08-sop-template|T08]] · [[toolkit/index|COO Toolkit]]
