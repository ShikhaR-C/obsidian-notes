# T25 — Customer Support SOP

_Toolkit · fills exercise 13.1 in [[10-customer-operations-support-and-success|10 — Customer Operations: Support and Success]] · Owner: the support owner — the technical founder in the founder-first phase, then the Support/Ops Associate · Cadence: live from the day the official channels open; macros edited weekly; full review every 180 days · Written in [[T08-sop-template|T08]]'s standard shape; the metrics rows live on the `KPI Scorecard` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

This is **the document that lets anyone competent run the DZZLO support queue** — channels, hours, SLAs, triage, the five tickets every week brings, the macros, escalation and the numbers. Not guidance about support: a **filled SOP**, ready to copy and edit, because support is the first function VSYST hands over and a handover without a document is a brain transplant ([[10-customer-operations-support-and-success|lesson 10]] §1). Runbook practice sets its threshold — troubleshoot the same problem twice and the steps belong in the document ([Upstat — runbook vs SOP](https://upstat.io/blog/runbook-vs-sop)).

Its second job is to make support **countable**: a conversation that lives only in a chat thread cannot be assigned, escalated, measured or learned from — a ticket can.

## When to use

- **From the day the official channels open** — the company WhatsApp Business number and the `support@` alias, both feeding Frappe Helpdesk ([[ERPNext-Implementation-Guide|ERPNext guide]]'s add-on section).
- **On every message**, from the founder-first phase onwards — the founder answering tickets is the company's best product research, and this SOP is what makes each answer leave a macro or an FAQ entry behind.
- **At each hand-off stage** (lesson 10 §10): the associate runs P3s, then P2s, then owns the queue — each stage is this document plus a shadowing week.
- **Reviewed every 180 days**, and edited the same week any postmortem ([[T17-incident-postmortem|T17]]) produces a new fallback or macro.

## How to fill (rules)

1. **Agree the SLA before you publish it, then beat it.** The table below is a starting point, not a promise VSYST has made — set coverage hours you will genuinely staff and targets you can beat, record the decision in [[T09-decision-log-and-adr|T09]], and publish it in the FAQ and the outside-hours auto-reply.
2. **The clock starts when the message lands on any official channel**, not when someone noticed it.
3. **Every WhatsApp message becomes a ticket** — copy-paste with the dealer name and phone, thirty seconds — until an API integration does it automatically. Messages to personal numbers get a polite forward-and-reply-from-the-queue, every time, until the habit moves.
4. **Severity is decided by the triage table, not by the tone of the message.** An angry P3 is still a P3; a calm "invoices ka total galat hai" from three tenants is a P1.
5. **Macros are living and bilingual.** Every macro carries an English line and a natural Hindi line (dealers forward these to their own staff), names the person replying, and never blames the user. Edit them weekly in the founder-first phase — a macro that answers imprecisely generates the next ticket.
6. **Support keeps the dealer conversation even when engineering fixes.** Escalation carries a fixed payload (below); it never hands the relationship over.
7. **Close with a category and a product-area tag** — thirty seconds, and the categories become the monthly themes that feed the roadmap (lesson 10 §10).
8. **No metric without a source query.** The four numbers come from the helpdesk's own reports, entered by the person on the queue, Monday by 10:00 ([[T05-kpi-scorecard|T05]]).

## Template — SOP-CUS-002 Customer support

Copy to `sops/sop-cus-002.md`, add the row to the `SOP Index` tab, then edit every bracketed field.

| id          | owner                           | version | last reviewed | next review | trigger                                    |
| ----------- | ------------------------------- | ------- | ------------- | ----------- | ------------------------------------------ |
| SOP-CUS-002 | \<support owner\> (backup: COO) | 1.0     | YYYY-MM-DD    | +180 days   | Any message on an official support channel |

**Purpose.** Answer every dealer and customer message inside the published SLA, resolve it or escalate it correctly, and leave the queue countable.

**Scope.** Covers dealer and customer support on all official channels, triage, escalation and the weekly numbers. Does not cover dealer onboarding (`SOP-CUS-001`), incidents once declared ([[T17-incident-postmortem|T17]]) or releases ([[T26-release-checklist|T26]]).

**Roles.** Runs it: support owner · Backup: COO · Escalates to: CEO/CTO for engineering, COO for money and policy.

**Prerequisites.** Access to Frappe Helpdesk, the WhatsApp Business number and phone, the `support@` alias, the 2Factor.in and OneSignal panels (read), ERPNext (read), the FAQ asset folder on the support phone.

**Channels and hours.** One company **WhatsApp Business number** (published in the app, on invoice PDFs, in both store listings, on the visiting card) and one **`support@` alias**, both feeding one Frappe Helpdesk queue. Coverage: P1s 07:00–22:00 daily via the on-call phone; P2/P3 09:00–19:00 Mon–Sat. The outside-hours auto-reply states the hours and the P1 path.

**SLA table** (illustrative — agree yours, then publish it):

| Severity                                             | First response  | Resolution target         | Coverage             |
| ---------------------------------------------------- | --------------- | ------------------------- | -------------------- |
| **P1** — many tenants blocked, or money-trust broken | 30 min          | 4 hours, workaround first | 07:00–22:00 all days |
| **P2** — one tenant blocked, or wrong but contained  | 2 working hours | 1 working day             | 09:00–19:00 Mon–Sat  |
| **P3** — how-to, cosmetic, feature ask               | 4 working hours | 3 working days            | 09:00–19:00 Mon–Sat  |

**Triage decision tree** — read top to bottom, stop at the first yes:

```
Is the core loop down for MANY tenants, or is money/ledger data wrong?
  YES -> P1. Declare the incident (T17), call — do not message — the CEO/CTO,
         send dealer comms within 30 min, start the timeline log.
  NO  -> Is ONE tenant blocked from a core-loop step (rate, order, dispatch,
         invoice, voucher), or is one account's number disputed?
           YES -> P2. Work in queue order; run the first checks below; if the
                  checks do not resolve it, escalate with the payload below.
           NO  -> Is it a how-to, a cosmetic complaint or a feature ask?
                    YES -> P3. Answer from a macro or an FAQ asset.
                           Feature asks: log with the dealer's name, never promise.
                    NO  -> Ask one clarifying question, then re-run this tree.
```

**Steps** (each with its check): 1. Acknowledge on the arriving channel, by name, inside the FRT `check: reply timestamp inside SLA`. 2. Create or update the ticket with the fields below `check: no blank mandatory field`. 3. Triage with the tree; set severity `check: severity set`. 4. Run the first checks for the matching case (below) `check: checks recorded in the ticket`. 5. Resolve from a macro, or escalate with the payload `check: dealer told what happens next, and when`. 6. Confirm the fix and ask the CSAT question `check: yes/no captured`. 7. Close with category and product-area tags `check: both present`.

**Ticket fields.** Tenant (dealer) · user and phone · channel · severity · category · product area (rate window / dispatch–OTP / invoices / payments–ledger / statements / invites–access / performance / feature ask) · first-response time · resolution time · linked GitHub issue · CSAT.

**Escalation payload to engineering** — a ticket crosses only with: tenant, user and phone; the exact action and the error (screenshot); the time window; what the first checks already ruled out. It becomes a GitHub issue linked to the ticket; **support keeps the dealer conversation**.

**Exceptions.** Outside coverage hours a P1 goes to the on-call phone; a P2 gets the auto-reply and its clock starts at open. Changing a user's access scope is the **dealer's** call, never support's. A suspected money discrepancy is never hand-edited in the database — it is a P2 to engineering.

**Outputs.** A closed, tagged ticket; any new macro or FAQ asset it produced; the weekly metric rows.

**Metrics** (rows on [[T05-kpi-scorecard|T05]] / the `KPI Scorecard` tab, read at the Monday meeting): **FRT** median (green ≤ 30 min), **% resolved within SLA** by severity (green ≥ 90%), **CSAT** = % positive of the yes/no replies (green ≥ 85%), **tickets per active tenant per week** (watch the trend — near-zero with low usage is disengagement, not health). Severity mix is read next to the totals: twenty P3s are a training gap; three P2s on invoices are a fire.

**Change log.** `| date | version | change | by |`

## VSYST example — the five macros

The five tickets DZZLO's core loop generates ([[10-customer-operations-support-and-success|lesson 10]] §5). Replace `<name>`; keep the Hindi line — dealers forward these to their own staff.

**1. OTP not received.** _Checks: right number on the record? 2Factor.in delivery status? One user or many — many means P1._

```
Namaste <dealer>. I see the OTP request at <time> to <number>; the network
is delaying it. Please wait 2 minutes and tap Resend ONCE. If it still
doesn't arrive I will confirm the delivery another way so your vehicle
is not held up.
OTP network se der ho rahi hai. 2 minute ruk kar ek baar Resend dabaiye —
phir bhi na aaye to hum doosre tareeke se confirm kar denge.
— <name>, VSYST support
```

**2. Rate confirmation missed.** _Checks: did the push arrive (OneSignal)? Was the customer's app logged in? Which user scope tried? Repeated misses for one tenant are a churn signal, not just a ticket._

```
Rates for <date> locked at 6 AM because they were not confirmed in the
10 PM-6 AM window. Tonight's rate is open now — the confirm button is the
top card on the customer's home screen. May I walk your order-placer
through it once? Two minutes.
Kal ka rate 6 baje lock ho gaya tha. Aaj raat ka rate ab khula hai —
main aapke order-placer ko ek baar phone par dikha deta hoon.
— <name>, VSYST support
```

**3. Invoice mismatch.** _Checks: which invoice type against what (PRODUCT / CASH_REIMBURSE / GST)? Payments allocated correctly? Did TCS switch on mid-year? A real discrepancy is P2 to engineering — never a hand-edit._

```
I have opened the ledger for <customer>, <month>. The ₹<amount>
difference is the reimbursement invoice, which is separate from the
product invoice — the two together match your book. Sending the
statement with both lines marked.
Antar reimbursement wale bill ka hai, product bill se alag. Dono jodne
par aapka hisaab milta hai; statement bhej raha hoon.
— <name>, VSYST support
```

**4. Invite / login issue.** _Checks: invite sent to the right number? Already used? Is the person in the scope they think? Scope changes need the dealer's authorisation._

```
The invite went to <number> on <date> and is still unused. Sending a
fresh one now — open it on the same phone and enter the OTP. To let
<person> raise orders too (not just view), message me from the owner's
number and I will change it today.
Naya invite bhej raha hoon — usi phone par kholiye aur OTP daaliye.
Access badalna ho to owner ke number se message kar dijiye.
— <name>, VSYST support
```

**5. Statement PDF.** _Checks: which period? App version? Does the on-screen ledger load? Repeat generation failures go to engineering._

```
Statement for <customer>, <period>, attached. You can also download it
any time: Ledger -> the month -> Download. Sending a 60-second video of
those three taps — keep it for your accountant.
Statement bhej diya hai. Aage khud bhi nikaal sakte hain: Ledger ->
mahina -> Download. Chhota video bhi bhej raha hoon.
— <name>, VSYST support
```

## Related

Lessons [[10-customer-operations-support-and-success|10]] (the whole customer-ops system), [[12-product-and-engineering-operations|12]] (what happens after escalation), [[15-sops-and-playbooks|15]] (the SOP library this joins), [[16-metrics-dashboards-and-scorecards|16]] (the support rows in the KPI tree) · Templates [[T08-sop-template|T08]] (the standard shape), [[T17-incident-postmortem|T17]] (P1s), [[T05-kpi-scorecard|T05]], [[T09-decision-log-and-adr|T09]], [[T21-headcount-plan|T21]] (the trigger that hires the support owner) · [[COO-Docs/toolkit/index|COO Toolkit]]
