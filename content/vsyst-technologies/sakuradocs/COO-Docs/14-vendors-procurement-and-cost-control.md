# 14 — Vendors, Procurement and Cost Control

_Phase 3 · Build the Machine · Months 2–6. After this lesson you can run every vendor and tool from one register with renewal alerts that fire 60 days early, onboard a vendor through KYC and a contract checklist, kill unused spend at a quarterly audit, compute VSYST's cost per tenant and cost per employee per month, negotiate like a bootstrapped company (and claim cloud credits), and buy hardware that stays on an asset list._

## 1. The register is the mechanism

At a pre-revenue company, **every rupee that leaves passes through a vendor** — the cloud bill, the SMS balance, the CA's fee, the laptop, the domain. There is no procurement department; there is you, a company card, and a dozen subscriptions each too small to notice and collectively the burn rate. Vendor management is therefore not an admin chore but the COO's half of the cash law: the finance course owns runway; you own the operational causes of spend — what we buy, on what terms, at what price, and whether we could leave.

The whole function hangs off one artefact: the **vendor and tool register**, [[T14-vendor-and-tool-register|T14]], mirrored in the `Vendor & Tool Register` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx). [[07-tools-and-it-foundation|Lesson 07]] already built its first version — the canonical tool table, the six selection rules, the "row created the day a tool is adopted" habit and the cost-per-person number — and this lesson does not repeat that table. What it adds is the **lifecycle around the rows**: how a vendor gets in (§2), how it gets paid (§3), how it renews or dies (§4–5), what it costs per unit of business (§6), how the price improves (§7–8), and how you stay free to leave (§9). One register, one owner, reviewed quarterly — the same mechanism pattern as every other lesson, pointed at the spend side.

Two register rules worth restating because everything below depends on them: **a row exists before the first invoice** (a vendor with no row is unapproved spend), and **renewal date + auto-renew flag are mandatory fields** — a blank renewal cell is how a ₹40,000 annual plan renews itself unnoticed in month eleven.

## 2. Onboarding a vendor

Onboarding is a fifteen-minute checklist, not a ceremony — but skipping it is how you end up paying a vendor whose bank details arrived on WhatsApp, whose invoice can't carry input credit, and whose contract renews itself annually with a 10% escalator nobody read.

**Step 1 — the decision.** For tools, the lesson 07 §2 decision record ([[T09-decision-log-and-adr|T09]]) answers _whether_: one tool per job, cheapest that works, export tested, company-owned admin, SSO/2FA, GST invoice. For services (the CA, a designer, an SMS provider), the same six questions apply with obvious translation. Above the DoA threshold, the decision needs the approval §3 describes.

**Step 2 — vendor KYC, four fields into the register:**

- [ ] **Legal name and PAN** — as they will appear on invoices; TDS on service vendors hangs off the PAN, and no PAN means deduction at the higher of the rate or 20% ([[06-money-rails-and-finance-operations|lesson 06]] §7).
- [ ] **GSTIN, or "unregistered" recorded deliberately** — a registered vendor's invoice must carry our GSTIN for input tax credit; USD-billed foreign tools get the lesson 07 note for the CA (**VERIFY LIVE** the ITC treatment).
- [ ] **Bank details verified out-of-band** — from an invoice or a cancelled cheque, confirmed on a known channel before the first payment; payment-detail changes re-verified the same way (this is the cheapest fraud control that exists).
- [ ] **Udyam status — ask; most vendors have never been asked.** A micro/small supplier triggers the 45-day rule (§3), so the register carries the flag from day one.

**Step 3 — the contract read.** You are not the lawyer; you are the person with the checklist. Seven clauses decide almost everything that later goes wrong:

| Clause                         | What to look for                                                                                                                                                                                                                                                                                                                                         | Red flag                                                              |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Term**                       | Start, end, and what happens at the end                                                                                                                                                                                                                                                                                                                  | Evergreen term with no stated end                                     |
| **Auto-renew & notice window** | Does it renew silently, and how many days' notice does cancellation need? Both go into the register — the §4 alert is set against the notice window, not the renewal date                                                                                                                                                                                | 60–90-day notice buried in an annex                                   |
| **Liability cap**              | Their liability capped at trivial amounts while yours is uncapped; for critical vendors, whether the cap survives data loss                                                                                                                                                                                                                              | "Liability limited to one month's fees" on a vendor holding your data |
| **Data handling / DPDP**       | For any vendor touching personal data: purposes, security safeguards, sub-processors, breach-notice timelines that let you meet DPDP's 72-hour report and CERT-In's 6 hours, deletion on exit — the DPA from lesson 05 §6; DPDP Rule 6 expects contractual controls on processors ([Scrut — DPDP Rules explained](https://www.scrut.io/post/dpdp-rules)) | "We may use your data to improve our services", unqualified           |
| **Exit & data export**         | Format, completeness and time window for getting data out at termination                                                                                                                                                                                                                                                                                 | Export only "on request", format unspecified                          |
| **SLA**                        | Uptime/support commitment and the remedy (credits, termination right) — or the honest register note "free tier, no SLA", which is a [[T15-risk-register\|T15]] input                                                                                                                                                                                     | An SLA with no remedy attached                                        |
| **Price escalators**           | Renewal-price language: fixed, capped (e.g. inflation-linked), or open                                                                                                                                                                                                                                                                                   | "Then-current list price" at renewal                                  |

A vendor that fails the read can still be used — knowingly, with the risk noted in the register and, if it is one of the product-critical five, in the risk register. What is not allowed is _unread_.

## 3. Paying vendors — terms, the 45-day rule and the DoA

[[06-money-rails-and-finance-operations|Lesson 06]] owns the payment rails — the weekly payment run, maker-checker, the vendor payments calendar. This section adds the three vendor-side disciplines that sit on top of them.

**Terms are negotiated, then honoured.** "Pay slow, collect fast" is working-capital sense, and it means _using the full agreed term_, not paying late: take the 30 days you negotiated, pay on day 28 through the weekly run, and never burn a vendor relationship to stretch cash silently — if cash is tight, renegotiate in the open (the §7 conversation, and the no-surprises rule applied outward).

**The one legal exception: MSME vendors, inside 45 days, always.** If a supplier is Udyam-registered micro or small, the MSMED Act's 45-day protection applies to VSYST _as the buyer_, and income-tax s.43B(h) makes late payment a straight hit to taxable profit — amounts are deductible only in the year actually paid ([TaxGuru — MSME thresholds and the 45-day rule](https://taxguru.in/corporate-law/msme-threshold-limit-effective-1st-april-2025.html)); dues beyond 45 days also trigger the half-yearly MSME-1 return on [[13-compliance-calendar-risk-and-insurance|lesson 13]]'s calendar. Lesson 06 §5 has the mechanics; the register's Udyam flag (filled at onboarding, §2) is what makes the rule executable — pay flagged vendors inside 30 for margin. **VERIFY LIVE** the current mechanics with the CA under the ITA 2025.

**Every recurring commitment passes the DoA.** The delegation-of-authority matrix ([[T22-delegation-of-authority-matrix|T22]]) sets who may commit what ₹ — and for subscriptions the threshold is tested against the **annualised** amount, because a ₹3,000/month tool is a ₹36,000 decision. Petty one-offs below the threshold need only the register row; anything above needs the named approver before signup, and the "two-signature above X" rule from lesson 06 applies to vendor contracts exactly as to payments. An auto-renewal is a spend decision repeating silently — §4 exists to drag it back in front of the DoA once a year.

Hygiene that prevents small messes: invoices land at `billing@` (never a personal inbox) and are filed monthly for the CA; subscriptions ride the company card or account, never a personal card; and the payment method is a register column, so a card expiry doesn't become a surprise outage — the OTP balance lesson from [[12-product-and-engineering-operations|lesson 12]] generalises.

## 4. Renewals — the 60-day rule

Renewals are where vendor spend quietly compounds: the price rises a little, the seats drift up, the tool is half-used — and the auto-renew fires anyway. The mechanism is one rule enforced without exception: **every register row has a renewal date and an auto-renew flag, and a calendar alert fires 60 days before** (to `ops@` or your task list — somewhere with an owner, not a personal reminder that leaves with the person).

Why 60: it is enough time to run the three questions, test the export, get a competing quote and still act inside the contract's cancellation-notice window (§2) — 30 days is enough time to sigh and renew. Where a contract's notice window is longer than 60 days, the alert moves earlier: **alert date = notice deadline minus 30 days, or 60 days before renewal, whichever is earlier.**

The alert triggers a ten-minute ritual, not a meeting — three questions written into the register row:

1. **Do we still use it?** Seats active in the last month vs seats paid. If the answer is no, the renewal is a cancellation.
2. **Right tier, right count?** Most tools are over-tiered a year after adoption; downgrade is the most common outcome of the ritual.
3. **Did the price move?** Against last year's invoice and against the §7 leverage (competing quote, startup pricing, annual-vs-monthly). An unexplained increase is a negotiation trigger, not a line item.

The same 60-day rule covers the non-tool renewals that hurt most when missed: the domain, TLS certificates, DSC tokens, the app-store developer accounts and insurance policies — those live on [[13-compliance-calendar-risk-and-insurance|lesson 13]]'s calendar ([[T16-compliance-calendar|T16]]), with the register cross-referencing them so neither list believes the other has it covered.

## 5. The quarterly tool audit

The [[startup-operations-plan|Startup Operations Plan]]'s habit — "review tool subscriptions quarterly and cancel unused ones" — becomes a 45-minute quarterly ritual with a checklist, run in the same calendar slot as lesson 07's quarterly access review, because they walk the same list: every seat is both a cost and an attack surface.

- [ ] **Walk every register row.** Cost from the latest invoice (not from memory), seats paid vs people who actually used it this quarter — **kill unused seats the same day**, in the meeting, not as a follow-up.
- [ ] **Hunt duplicates.** Two tools doing one job violates lesson 07's first rule; pick one, record the decision in [[T09-decision-log-and-adr|T09]], and migrate on a date.
- [ ] **Catch the zombies.** Anything unused for a quarter is cancelled or consciously parked with a written reason; "we might need it" without a name and a scenario is not a reason.
- [ ] **Re-test the export for the product-critical rows** (§9) — an export path that worked at adoption can rot behind a plan change.
- [ ] **Check the flags:** auto-renew flags still correct, payment methods not expiring, MSME flags filled, spend alerts (§8) still armed and pointed at a live inbox.
- [ ] **Recompute the two unit numbers (§6)** and write one line of commentary on each trend for the next weekly business review.

The audit's output is three artefacts: an updated register, a decision-log entry for anything killed or merged, and a rupee number — **spend removed this quarter** — which belongs in the monthly business review, because cost control you cannot quantify is cost control that will not survive a busy quarter.

## 6. Unit cost of operations — cost per tenant, cost per employee

Total spend tells you whether you are dying; **unit cost tells you whether the business model works.** Two numbers, both from the register plus two divisors, both on the scorecard ([[T05-kpi-scorecard|T05]]):

```
cost per tenant / month    = variable serving costs ÷ active dealer tenants
                             (infra + messaging that scale with usage)

cost per employee / month  = total monthly tool & infra spend ÷ people using it
                             (contractors included — lesson 07 §8's number)
```

For DZZLO the **variable lines** — the costs that grow as tenants and their orders grow — are already identifiable in the register:

| Variable line                                      | What drives it                                                                                                                                                                                                                                       | Price basis (**VERIFY LIVE**)                                 |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **2Factor.in SMS/OTP**                             | Login OTPs and one driver-OTP per dispatch                                                                                                                                                                                                           | Per-SMS rate from the panel                                   |
| **WhatsApp Business API** (when the BSP is chosen) | Utility/authentication messages ₹0.115 each, marketing ₹0.8631 each (Meta India, from 1 Jan 2026), plus the BSP's monthly fee ([myOperator — WhatsApp API pricing India 2026](https://myoperator.com/blog/whatsapp-business-api-pricing-india-2026)) | Per message + platform fee                                    |
| **OneSignal push**                                 | Rate-confirmation and order notifications                                                                                                                                                                                                            | Free tier today; the paid threshold is a lesson 12 watch item |
| **AWS EC2 / S3 / CloudFront + MongoDB Atlas**      | Compute, storage and data transfer scale with tenants and documents                                                                                                                                                                                  | Monthly bills                                                 |
| **AWS SES**                                        | Transactional email                                                                                                                                                                                                                                  | Per-mail, from the bill                                       |

The arithmetic is deliberately simple and **illustrative**: a tenant whose month involves 60 OTP SMS and 150 utility WhatsApp messages carries roughly ₹17 of messaging at the utility rate above plus their slice of infra — the point is not the number but that _you can compute it_, watch it monthly, and see which line moves when the product changes. Fixed costs (Workspace, GitHub, the CA) belong in cost per employee, not cost per tenant — mixing them hides both signals.

Where this number goes: the [[app-store-economics/11-cost-model-worksheet|cost-to-serve worksheet]] owns the full model (per-tenant infrastructure, support minutes, payment-gateway take) and feeds the subscription-pricing decision — per-GSTIN pricing that ignores cost-to-serve is a guess. Your job as COO is narrower and weekly: keep the two unit numbers current on the scorecard, with a RAG rule ("amber if cost per tenant rises two months running without a named cause") so drift surfaces as an exception, not an archaeology project.

## 7. Negotiation basics — and startup credits

Nobody at a three-person company negotiates like an enterprise procurement team, and nobody needs to. Five habits capture most of the money:

1. **Monthly first, annual after a quarter of real use** — lesson 07's rule. Annual plans discount meaningfully, but only after usage has proved the tool stays; an annual plan on an unproven tool is a discount on a mistake. When you do go annual, the §4 alert protects the exit.
2. **Ask for startup pricing — out loud.** Many SaaS vendors run unlisted startup, small-team or India tiers; the worst outcome of asking is the list price you already had. DPIIT recognition and the company domain are the credentials that unlock most programmes.
3. **Buy INR where possible, via Indian resellers, for a GST invoice** — the ITC recovers 18% that a USD card payment may not ([Cloudfy — Google Workspace pricing India](https://www.cloudfysystems.com/blog/google-workspace-pricing-plans-india); lesson 07 §2's worked example). **VERIFY LIVE** with the CA.
4. **Negotiate at renewal, with 60 days in hand.** Leverage is real only when the alternative is real: export tested, a competing quote on file, and the calm to walk. A renewal negotiated in the last week is a renewal accepted.
5. **Count seats honestly, both ways.** Don't pay for ghosts (§5), and don't share logins to dodge a seat fee — shared credentials violate the lesson 07 access rules and cost more in risk than they save in fees.

**Cloud credits are the one free lunch — claim them.** Lesson 07 §10 has the full table; the short version for a bootstrapped company: AWS Activate's Founders package (~\$1,000, with a larger Startup India route to **VERIFY**), Google for Startups' MVP tier (~\$2,000), and Microsoft for Startups Founders Hub's self-serve ladder (\$1,000 up to \$150,000 as traction and backing grow) ([Northflank — AWS credits guide](https://northflank.com/blog/how-to-get-free-aws-credits-for-your-startup); [Cloudkompas — Google Cloud for Startups 2026](https://cloudkompas.com/blog/google-cloud-for-startups-2026-credits-guide); [Klymentiev — Microsoft for Startups](https://klymentiev.com/blog/microsoft-for-startups)) — all amounts and conditions **VERIFY LIVE** on the programme pages. Apply with the company-domain email (exercise 12.4). Two cautions: credits have expiry dates — put them on the renewals calendar so the bill's return is planned, not discovered; and credits reduce the bill, never the discipline — §8's budgets and reviews run as if every rupee were cash, because one day it is again.

## 8. Cloud cost hygiene

Cloud spend is the one vendor line that can change by 40% with nobody signing anything — a forgotten test instance, a chatty query pattern, a log bucket growing forever. The controls are cheap and mostly one-time:

- **Budgets and alerts, armed on day one.** An AWS budget alert and an Atlas billing alert at sensible thresholds (say, 120% of the trailing average — pick your own line), delivered to `billing@` and to you — [[12-product-and-engineering-operations|lesson 12]] already lists these among its monitoring basics. An alert that fires is an exception for the weekly meeting; that is management by exception applied to money.
- **The monthly bill review — fifteen minutes, line by line, with the CEO/CTO.** Read the EC2/Atlas/SES/S3 bills like a bank statement: every line either has a name ("the API box", "staging", "backups bucket") or it is a question. New lines get explained or killed. The bill is also where rightsizing shows up — an instance at 10% utilisation is a size too big, and a dev cluster running at 2 a.m. is a scheduler nobody wrote (**VERIFY LIVE** current instance pricing before resizing decisions; the CEO/CTO owns the technical call, you own that the review happens).
- **Storage hygiene:** snapshot and AMI cleanup after infra changes, S3 lifecycle rules on logs and exports, and a yearly look at data-transfer lines — the classic silent growers.
- **Commit only to stable load.** Reserved instances and savings plans trade flexibility for discount; take them only on usage that has been flat for two quarters, and record the commitment in the register with its own renewal row — it is a contract like any other (**VERIFY LIVE** terms).
- **Keep experiments separate.** Tag or account-separate production from experiments so the bill review distinguishes "the product costs this" from "we were trying something" — which is also what makes §6's cost-per-tenant honest.

## 9. Avoiding lock-in

Lock-in is a price you pay later for convenience today, and at a bootstrapped company the interest rate is brutal — a vendor that knows you cannot leave prices accordingly. The defences are all habits you have already met, assembled:

- **The export test, before dependence and again at audit.** Lesson 07's rule — test the export before you depend on the tool — plus §5's quarterly re-test for critical rows. The register's "data exportable?" column is a tested fact, not a brochure claim.
- **The one-module abstraction for swappable vendors.** Lesson 12 §8's engineering rule: OTP and push providers sit behind one code module each, so a swap is a sprint, not a rewrite. The COO's contribution is to keep the swap path written in the register ("what it would take to leave") and researched _before_ the day it is needed — the second SMS provider's onboarding requirements are cheap to learn in peacetime.
- **Exit clauses negotiated at entry (§2).** Data return in a stated format inside a stated window; the moment of maximum leverage over exit terms is before you sign, never after.
- **Open formats as the default posture.** The stack lesson 07 chose already leans this way — markdown in git, ERPNext's full-site backup, `.xlsx`/CSV for the workbook, open-source self-hostable pieces (ERPNext, Frappe apps, Metabase, n8n). Every new tool is measured against that bar.
- **Know the acceptable lock-ins.** Some are unavoidable (the app stores, the GST portal, WhatsApp as the channel dealers actually use) — the point is to _name_ them in the register and the risk register, not to pretend they don't exist.

## 10. Hardware — laptops, test phones and the asset list

Hardware procurement at this size is five rules and one list:

1. **The company buys, the company owns.** Every device on a company invoice with the company GSTIN — the CA decides what input credit and depreciation apply (**VERIFY LIVE**); a director's personal laptop "lent" to the company is exactly the informal related-party arrangement lesson 05 told you to paper properly.
2. **An asset list from device one** — a section of [[T14-vendor-and-tool-register|T14]] or its own sheet: item, serial number, purchase date and invoice link, holder, condition, and return-by event. Devices are issued through the onboarding checklist ([[T12-onboarding-checklist|T12]]) and recovered through offboarding ([[T13-offboarding-checklist|T13]]) — the same mirror-image discipline as accounts.
3. **Every device meets the lesson 07 device policy** before it touches company data: full-disk encryption, screen lock, auto-updates, find-my-device.
4. **Test phones are infrastructure, not spares.** DZZLO is used by dealers, drivers and customer staff on modest Android hardware — keep at least one low-cost Android alongside an iPhone as release-testing devices (lesson 12's store operations depend on them), company-owned, on the asset list. The phone that holds the WhatsApp Business number is a company phone on a company SIM — lesson 07's rule, worth repeating because it is the single most commonly personal-owned "company" asset.
5. **Buy sensibly, not newly.** Refurbished-with-warranty is a legitimate bootstrapped default for laptops; the DoA threshold (§3) applies to hardware exactly as to subscriptions.

## 11. At VSYST — applying this now

- **Finish what lesson 07 started.** Exercise 12.1 there filled the register's rows; this month's pass adds the lifecycle columns — renewal date, auto-renew flag, cancellation-notice window, Udyam status, payment method — and sets the 60-day alerts (exercise 12.1 below). The register is only a mechanism once the alerts exist.
- **Give the product-critical five the full treatment first.** AWS, MongoDB Atlas, OneSignal, 2Factor.in and the WhatsApp channel are the vendors that can stop the product — lesson 12 §8 already demanded their SLAs, credentials, spend alerts and swap paths; confirm those four facts sit in the register, and put the top single-vendor exposure (OTP) into [[T15-risk-register|T15]] if lesson 13's exercise hasn't already.
- **The WhatsApp BSP evaluation is your first real procurement.** Interakt, AiSensy, Wati and Gupshup are under evaluation (lesson 07's table has the fee shapes) — run it through this lesson end-to-end: the §2 checklist including the DPA clauses (a BSP processes dealer and customer phone numbers), per-message + platform-fee maths into the §6 cost model, a T09 decision record, and an exit path tested before committing. It is also the cheapest possible rehearsal for negotiating the payment-gateway agreement when the Easebuzz/UBI conversation matures.
- **Compute both unit numbers now, while the product is free.** Cost per tenant v0 (exercise 12.3) is an input the [[app-store-economics/11-cost-model-worksheet|cost-to-serve worksheet]] and the per-GSTIN subscription pricing need _before_ a price exists; cost per employee per month gives the burn conversation its denominator. Free product, real costs — the earlier the baseline, the more useful every later trend.
- **Apply for one credit programme this week** with the company-domain email (exercise 12.4) — VSYST's DPIIT recognition and 2021 incorporation fit the bootstrapped tiers as researched, **VERIFY LIVE** on the programme pages.
- **Keep the pump and the company separate.** Hardware, SIMs and subscriptions bought through the family petrol-pump business for company use are related-party facts (lesson 05's MBP-1 territory) — buy on the company's own invoices, even when the pump's vendor is more convenient.

## 12. Exercises

**12.1 — Complete the register and arm the alerts (45 min).** In [[T14-vendor-and-tool-register|T14]] / the `Vendor & Tool Register` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx), fill renewal date, auto-renew flag, notice window, Udyam status and payment method for every row; then create the 60-day calendar alerts (earlier where notice windows demand, per §4) in a company-owned calendar. Output: a register with no blank lifecycle cells and an alert per renewing row.

**12.2 — Run the first quarterly tool audit (45 min, with the CEO/CTO).** Walk the §5 checklist end to end. Kill or downgrade at least the obvious candidates, log each decision in [[T09-decision-log-and-adr|T09]], and compute the rupee number: spend removed. Book the next audit into the quarterly slot alongside the access review. Output: an updated register, decision-log entries, and a savings figure for the monthly review.

**12.3 — Compute cost per tenant v0 and cost per employee (30 min).** From the last two months of invoices, split register rows into variable (§6 table) and fixed; divide by active tenants and by people respectively. Add both rows to [[T05-kpi-scorecard|T05]] with an owner and a RAG rule, and send the variable-line breakdown to the [[app-store-economics/11-cost-model-worksheet|cost-to-serve worksheet]]. Output: two scorecard rows with real baselines.

**12.4 — Apply for one cloud-credit programme (30 min).** Pick the programme matching our stack and stage from lesson 07 §10 (AWS Activate is the natural first), gather the asks (company-domain email, DPIIT certificate, incorporation details), submit, and put the expected credit, its expiry and a follow-up date into the register and [[T09-decision-log-and-adr|T09]]. Output: a submitted application with its expiry tracked.

---

**Next:** [[15-sops-and-playbooks|15 — SOPs and Playbooks]] — what an SOP is and isn't, the SOP standard, the "if it happens twice" rule in practice, VSYST's process map and starter SOP list, and how SOPs are versioned, taught and retired.
