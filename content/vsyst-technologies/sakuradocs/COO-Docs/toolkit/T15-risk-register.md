# T15 — Risk Register

_Toolkit · fills the exercises in [[13-compliance-calendar-risk-and-insurance|13 — Compliance Calendar, Risk and Insurance]] · Owner: COO (the register); one named owner per risk · Cadence: reviewed quarterly in the [[08-the-operating-cadence|lesson 08]] ring; re-scored after any incident or near-miss · Workbook tab: `Risk Register` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) — pre-filled with the twelve risks below._

## Purpose

The risk register is **the ranked list of things that could badly hurt or kill the company**, each with a score (likelihood × impact), one owner, a written mitigation, and an early-warning trigger. Its job is to convert background anxiety into a short list the directors actually work: the top three risks get attention _before_ they happen, and everything else is consciously accepted and monitored. Worry without a register is carried in heads; with one, it becomes owners, actions and review dates ([[13-compliance-calendar-risk-and-insurance|lesson 13]] owns the method; the register is [[02-how-a-coo-thinks|lesson 02]]'s managing-by-exception applied to existential questions).

## When to use

- **Build v1 in the first months of the seat** — the twelve pre-filled risks below are VSYST's honest starting set; re-score them rather than starting blank.
- **Quarterly**, in the [[08-the-operating-cadence|lesson 08]] review ring: re-score every row, check whether any trigger has fired, update mitigations, close what is closed.
- **After any incident, near-miss or audit finding** — every [[T17-incident-postmortem|T17]] postmortem and restore drill either updates a row or adds one.
- When a director says "what if…" twice — that is a row, not a conversation.

## How to fill (rules)

1. **Score = likelihood (1–5) × impact (1–5)**, using the guide below so two directors score the same way. **≥15 red — act this month, owner reports weekly at the ops meeting; 8–14 amber — mitigation plan with dates; <8 green — accept and monitor.**
2. **One owner per risk** — the person who drives the mitigation, not the person to blame.
3. **Mitigation is actions, not adjectives.** "Backups tested quarterly, last drill 2026-08-12" mitigates; "be careful with data" does not. Cite the evidence (drill dates, signed deeds, alert screenshots).
4. **Trigger is observable** — tied to a scorecard row or an alert wherever possible, so the early warning fires without anyone remembering to worry.
5. **Every row has a review date and a status** (Open / Mitigating / Closed). A register with no dates is a mood board.
6. **Keep it to 10–15 rows.** Merge or park the tail; operational annoyances live on the issues list, not here.

## Template

**Columns** (identical to the `Risk Register` tab):

> Risk · Category · Likelihood (1–5) · Impact (1–5) · Score · Owner · Mitigation · Trigger / early warning · Review date · Status

**Scoring guide** (agree it once; the tab carries the same):

| Likelihood | Meaning                                | Impact | Meaning (illustrative ₹ bands)                                   |
| ---------- | -------------------------------------- | ------ | ---------------------------------------------------------------- |
| 1          | Rare — not expected in 2 years         | 1      | Negligible — < ₹25k or < 1 day lost                              |
| 2          | Unlikely — maybe once in 2 years       | 2      | Minor — ₹25k–1 lakh, a few days, no customer harm                |
| 3          | Possible — could happen this year      | 3      | Moderate — ₹1–5 lakh, a week, some dealers affected              |
| 4          | Likely — expected this year            | 4      | Major — ₹5–25 lakh, a month, many dealers affected               |
| 5          | Almost certain — happening or imminent | 5      | Severe — company-threatening: cash-out, mass churn, legal action |

**The top-12 startup risks, pre-filled** (scores illustrative — re-score in your first review; the tab carries fuller mitigation text):

| #   | Risk                                                                   | Category   | L×I | Owner           | Mitigation (sketch)                                                                                                                            | Trigger / early warning                                      |
| --- | ---------------------------------------------------------------------- | ---------- | --- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| 1   | Key-person dependency — one technical founder holds the code and infra | People     | 4×5 | COO             | Credentials in the shared vault + break-glass; written deploy/restore notes drilled by the non-builder; second person per critical task        | Any deploy or incident only one person could handle          |
| 2   | Cash runway shortfall                                                  | Financial  | 3×5 | COO             | 13-week forecast weekly ([[T20-budget-vs-actual-and-cash-forecast\|T20]]); red line rule; cost control                                         | Runway below the red line anywhere in the 13 weeks           |
| 3   | Single-client / single-channel concentration                           | Strategic  | 3×4 | Domain director | ≥3 channels; no tenant/channel > 30% of pipeline                                                                                               | One tenant or channel > 30% of pipeline or revenue           |
| 4   | Data breach — dealer and customer data                                 | Security   | 2×5 | CEO/CTO         | Least privilege, 2FA everywhere, breach one-pager with the 6-hour and 72-hour clocks ([[12-product-and-engineering-operations\|lesson 12]] §9) | Failed access review; unusual DB egress                      |
| 5   | Server/API outage in the 10 PM–6 AM rate window                        | Technology | 3×4 | CEO/CTO         | Uptime alerts to two phones; on-call rota; restore drills                                                                                      | Uptime < 99.9% in a week; > 1 P1/month                       |
| 6   | OTP/SMS vendor outage (single vendor)                                  | Technology | 3×4 | Developer       | Provider behind one module; second route researched; prepaid balance floor alert                                                               | OTP delivery < 95%; "OTP not received" ticket spike          |
| 7   | Compliance miss — GST/TDS/ROC deadline                                 | Compliance | 3×3 | COO             | [[T16-compliance-calendar\|T16]] run weekly with owners; April re-confirmation with the CA                                                     | Any calendar row red inside 45 days of due                   |
| 8   | IP ownership gaps — contractor code unassigned                         | Legal      | 3×4 | COO             | Signed IP deeds from founders and every past contributor ([[T11-offer-letter-and-contract-checklists\|T11]])                                   | Any contributor without a signed assignment                  |
| 9   | Founder conflict / unclear decision rights                             | People     | 2×5 | CEO/CTO         | Signed T01 operating agreement; DoA matrix; decision log                                                                                       | Decisions re-litigated; escalations outside the agreed lanes |
| 10  | Hiring mistakes in the first hires                                     | People     | 3×3 | COO             | Scorecard-first hiring ([[T10-hiring-scorecard-and-process\|T10]]); paid work samples; probation used                                          | Missed 30-day outcomes; repeated re-hiring                   |
| 11  | App-store rejection or account action                                  | Technology | 2×4 | CEO/CTO         | Release checklist with store-policy audit ([[T26-release-checklist\|T26]]); purchase-silent posture                                            | Rejection notice; policy-update email                        |
| 12  | Regulatory change — GST/e-invoicing/DPDP/OMC rules                     | Compliance | 3×3 | COO             | Quarterly review with CA/CS; watch OMC/GSTN notifications                                                                                      | A new notification touching fuel retail or SaaS billing      |

## VSYST example (illustrative)

Row 6 worked end to end. _Risk:_ 2Factor.in outage blocks login and delivery OTPs — the sharpest single-vendor risk for a dispatch product. _Score:_ 3×4 = 12, amber → mitigation plan with dates. _Owner:_ Developer. _Mitigation:_ delivery-rate row on the scorecard; low-balance alert set 2026-08; OTP calls isolated behind one module; a second SMS provider's onboarding requirements documented in the vault in advance. _Trigger:_ OTP delivery < 95% on the scorecard, or an "OTP not received" spike in the helpdesk. _Review:_ next quarterly ring. When the second route is tested end to end, the score drops to 2×4 and the row goes green — that movement, written down, is the register doing its job.

## Related

Lessons [[13-compliance-calendar-risk-and-insurance|13]], [[12-product-and-engineering-operations|12]], [[08-the-operating-cadence|08]] · Templates [[T16-compliance-calendar|T16]], [[T17-incident-postmortem|T17]], [[T14-vendor-and-tool-register|T14]], [[T20-budget-vs-actual-and-cash-forecast|T20]] · [[COO-Docs/toolkit/index|COO Toolkit]]
