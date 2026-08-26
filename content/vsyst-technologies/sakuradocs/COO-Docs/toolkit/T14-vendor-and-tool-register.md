# T14 — Vendor and Tool Register

_Toolkit · fills exercise 12.1 in [[07-tools-and-it-foundation|07 — Tools and IT Foundation]] and the audits in [[14-vendors-procurement-and-cost-control|14 — Vendors, Procurement and Cost Control]] · Owner: COO · Cadence: a row the day a tool is adopted; renewals on 60-day alerts; full audit quarterly · Workbook tab: `Vendor & Tool Register` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx) — pre-filled with the VSYST stack._

## Purpose

The register is **the single list of every subscription, contract and renewal the company depends on** — what it does, who owns it, what it costs, when it renews, and how we would leave it. It exists so that costs stay visible, nothing auto-renews unnoticed, no account is owned by a personal Gmail, and the five vendors that can stop the product ([[12-product-and-engineering-operations|lesson 12]] §8) are known by name. Compliance checklists prescribe the same artefact as a vendor/DPA registry — every third party processing data, listed, with terms noted ([PolicyOwn — startup compliance checklist 2026](https://policyown.com/blog/startup-compliance-checklist-2026)). The number the register produces monthly is **cost per person per month** = total tool and infrastructure spend ÷ people using it, contractors included ([[07-tools-and-it-foundation|lesson 07]] §8).

## When to use

- **The day a tool or vendor is adopted** — the row is part of adopting, alongside the decision record in [[T09-decision-log-and-adr|T09]].
- **Monthly**, when invoices land at `billing@`: fill blank cost cells from the invoice, check the GSTIN is on it (input credit — [[06-money-rails-and-finance-operations|lesson 06]] §7).
- **On every 60-day renewal alert** — renewal is a decision, not a surprise.
- **Quarterly**, for the full audit (checklist below), riding the [[08-the-operating-cadence|lesson 08]] quarterly ring.
- **Before signing any vendor contract** — run the contract review checklist below against the paper.

## How to fill (rules)

1. **A row on adoption day, no exceptions.** A tool without a row is a cost and a risk nobody is watching.
2. **Renewal date and auto-renew flag are mandatory cells**; the 60-day-before calendar alert is created when the row is.
3. **Owner is a role, not a name** — and the account's admin email is a company alias, never a person ([[07-tools-and-it-foundation|lesson 07]] §4).
4. **"Data exportable?" is tested, not assumed** — run the export once before you depend on the tool; note the date.
5. **Udyam/MSME status per vendor**, asked at onboarding: micro/small suppliers must be paid inside 45 days (s.43B(h) makes late payment a tax hit — [TaxGuru — MSME thresholds and the 45-day rule](https://taxguru.in/corporate-law/msme-threshold-limit-effective-1st-april-2025.html), and see lesson 06 §5) — **VERIFY LIVE** with the CA.
6. **Note the data-processing terms** for any vendor touching personal data (cloud, SMS/OTP, push, WhatsApp BSP) — the DPA column feeds the DPDP work ([[05-legal-and-governance-foundation|lesson 05]] §6).
7. **Criticality is honest**: Critical = the product or the company stops; High = a function stops; Medium/Low = inconvenience. Critical rows get the lesson 12 §8 treatment — SLA noted, credentials location, spend alert, swap path.

## Template

**Register columns** (identical to the `Vendor & Tool Register` tab, which computes days-to-renewal):

> Vendor/tool · Function · Owner · Users/seats · Cost/mo (₹) · Billing cycle · Renewal date · Auto-renew? · Payment method · Contract link · Data exportable? (tested when) · Criticality · Notes (incl. Udyam/MSME status, DPA, SLA)

**Contract review checklist** — run before signing, and again at each renewal:

- [ ] **Term and notice**: how long, and how many days' notice to exit? Diarise the notice window, not just the renewal date
- [ ] **Auto-renew**: present? Can it be switched off? If not, the alert moves to the notice window
- [ ] **Liability cap**: theirs and yours; anything uncapped goes to the lawyer
- [ ] **Data / DPDP**: what personal data they touch, processing terms, breach-notice timelines compatible with your 72-hour and 6-hour clocks (lesson 05 §6)
- [ ] **Exit and export**: data returned/exportable in an open format, deletion on exit, transition help
- [ ] **SLA**: uptime/support promise, or the honest note "free tier — no SLA" (a [[T15-risk-register|T15]] input for critical vendors)
- [ ] **Price escalators**: renewal-price caps, index clauses, "then-current list price" traps
- [ ] Billing entity and GSTIN — INR invoice from an Indian entity/reseller where possible (lesson 07 §2)

**Quarterly audit checklist** (60 minutes, quarterly ring):

- [ ] Walk every row: still used? Kill unused tools and shrink unused seats
- [ ] Renewals inside the next 90 days reviewed as decisions
- [ ] Recompute **cost per person per month**; explain any jump in one line
- [ ] Owner email still a company alias; 2FA still enforced; no new personal-account adoptions
- [ ] One export actually re-tested (rotate through the critical rows)
- [ ] MSME flags and payment terms current; DPA column current
- [ ] New tools adopted this quarter all have rows and decision records

## VSYST example (illustrative)

The tab ships pre-filled with the in-use stack; extract (costs blank — enter from invoices, **VERIFY LIVE**):

| Vendor/tool                                                | Function                 | Owner         | Cost/mo | Auto-renew?  | Data exportable?       | Criticality                    |
| ---------------------------------------------------------- | ------------------------ | ------------- | ------- | ------------ | ---------------------- | ------------------------------ |
| GitHub (3 repos, Actions)                                  | Code, CI, PRs            | CEO/CTO       | —       | Y            | Y (mirror clone)       | Critical                       |
| AWS (EC2, SES)                                             | Backend hosting, email   | CEO/CTO       | —       | Y (usage)    | Y (snapshots)          | Critical                       |
| MongoDB Atlas                                              | Database                 | CEO/CTO       | —       | Y (usage)    | Y (mongodump, drilled) | Critical                       |
| Expo / EAS · Play Console · App Store Connect              | Mobile build and stores  | CEO/CTO       | —       | Apple annual | Partial                | Critical                       |
| 2Factor.in                                                 | SMS / OTP                | CEO/CTO       | —       | N (prepaid)  | Partial (panel logs)   | Critical — balance floor alert |
| OneSignal                                                  | Push                     | CEO/CTO       | —       | Y            | Partial                | High                           |
| WhatsApp Business                                          | Dealer comms and support | COO           | —       | —            | Partial                | High                           |
| ERPNext (Frappe Cloud/Docker)                              | Books, CRM, HR, tickets  | COO           | —       | —            | Y (site backup)        | High                           |
| Google Workspace                                           | Identity, mail, Drive    | COO           | —       | Y            | Y (Takeout)            | Critical                       |
| Mixpanel / Firebase                                        | Analytics                | CEO/CTO       | —       | Y            | Y / partial            | Medium                         |
| Figma / Canva · Zoom/Meet · AI tools (Claude Code, Cursor) | Design, meetings, AI     | per row       | —       | Y            | Y                      | Medium                         |
| Tally (with the CA)                                        | CA-side books            | CA (external) | —       | —            | Partial                | Medium                         |

## Related

Lessons [[07-tools-and-it-foundation|07]], [[14-vendors-procurement-and-cost-control|14]], [[06-money-rails-and-finance-operations|06]], [[12-product-and-engineering-operations|12]] · Templates [[T02-company-binder-checklist|T02]], [[T09-decision-log-and-adr|T09]], [[T15-risk-register|T15]], [[T22-delegation-of-authority-matrix|T22]] · [[COO-Docs/toolkit/index|COO Toolkit]]
