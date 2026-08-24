---
title: Certification and Standards Roadmap
---

# Certification and Standards Roadmap — Which ISO VSYST Actually Needs

_Written 2026-08-24 for **VSYST Technologies Pvt. Ltd.** (Raipur), maker of DZZLO OMS. Answers one question: which ISO — and ISO-adjacent — certification could be **required of us**, by whom, on what eligibility terms, at what cost, on what lead time, and which to ignore. §6 carries the cost, time and eligibility numbers. A companion to [[07-tools-and-it-foundation|lesson 07]] (the twelve controls, which are the groundwork) and [[13-compliance-calendar-risk-and-insurance|lesson 13]] (the calendar, which is where the triggers live). Every price and every date is **VERIFY LIVE**._

> **The one-line answer:** ISO/IEC 27001 is the only certification anyone is likely to demand of us, and our own files already contain a hard trigger for it. Everything else is either commercially optional, sequenced behind 27001, or not applicable to a software company. Do not buy any certificate before the control it certifies exists.

## 1. The frame — nothing in this document is legally required

Two categories get confused constantly, and confusing them is how a small company spends money in the wrong order.

**Legally binding on us today**, regardless of size, customer or certificate:

- **DPDP Act 2023 + DPDP Rules 2025** — substantive obligations bite **13 May 2027** ([[13-compliance-calendar-risk-and-insurance|lesson 13]] §2.3 carries the phase dates).
- **CERT-In Directions 2022** — 6-hour incident reporting, 180-day ICT logs held in India, a named point of contact. **No size exemption.**
- **IT Act s.43A + SPDI Rules 2011** — reasonable security practices, until DPDP fully supersedes them.

**Commercially required** — a counterparty's precondition to signing, enforced by a procurement checklist rather than a statute: that is what ISO certification is, in every row below.

So this document is organised by **who asks**, not by standard number. And one rule governs the whole thing:

> **Never buy a certificate before the control exists.** A certificate is evidence of a working system. A body that issues one without the system has sold you a liability, not an asset — §8 is about exactly that trap, which is unusually common in India.

Read this alongside [[startup-operations-plan|Startup Operations Plan]] (the business-level habits) and [[12-product-and-engineering-operations|lesson 12]] (which owns the product-side DPDP and app-store work). This doc adds only the certification layer on top.

## 2. The register — ranked by the odds of anyone actually asking

| Standard | What it certifies | Who at VSYST would be asked | Indicative cost / effort | Verdict |
| --- | --- | --- | --- | --- |
| **ISO/IEC 27001:2022** (+ Amd 1:2024) | Information Security Management System (ISMS) | IOCL / PSU vendor security review; enterprise transporter contracts; bank & gateway partners; **the GSP route explicitly** | ₹1–4 lakh all-in; **3–6 months** | **The one that will be demanded.** Trigger-based project — §3 |
| **ISO/IEC 27701:2025** | Privacy Information Management System (PIMS) | DPDP-conscious enterprise customers; contracts where we are a Processor for dealers' customer data | Cheapest as an integrated audit with 27001; standalone now possible | Build the documents now, certify on demand — §4 |
| **ISO 9001** (**:2015** → **:2026**) | Quality Management System (QMS) | PSU tender pre-qualification criteria; IOCL vendor enlistment | **₹25,000–75,000**, up to **75% MSME-reimbursable**; 2–4 months | Only if tenders are real — **and there is a timing window right now**, §5 |
| **ISO/IEC 27017 / 27018** | Cloud security controls / PII in public cloud | Rarely asked standalone | Small increment on a 27001 audit | Add as scope extensions **after** 27001, never before |
| **ISO/IEC 20000-1:2018** | IT service management (ITSM) | Occasionally a very large enterprise with SLA language | Comparable to 27001 | Wait for a named ask. We already do the substance |
| **ISO 22301:2019** | Business continuity (BCM) | BFSI-grade counterparties | Comparable to 27001 | Wait for a named ask. [[07-tools-and-it-foundation|Lesson 07]] §5 (RPO/RTO + restore drills) is the substance |
| **ISO/IEC 42001:2023** | AI management system (AIMS) | Nobody, yet | — | Watch item only. Revisit if DZZLO ships AI that **decides** things about users or credit |
| **ISO 14001 / ISO 45001** | Environmental / occupational health & safety | Boilerplate lines in some PSU checklists | — | **Skip.** Not meaningful for a software firm; argue the exclusion rather than buy the certificate |

Two structural points about that table. First, the top three are the only rows with a plausible named asker in our pipeline today. Second, the rows are **not** independent: 27001 is the platform, 27017/27018/27701 bolt onto it cheaply, and 9001 is an unrelated track bought for a different reason (tender eligibility, not security).

**§6 carries the full cost, timeline, audit-day and eligibility numbers** for every row above, including the MSME subsidy and the two price floors that signal a fake certificate.

## 3. ISO/IEC 27001 — the only one with a hard trigger already in our files

### 3.1 The trigger we have already written down

From [[06-gst-return-filing|tasks_15 · 06 — GST return filing]] §"Costs & obligations", quoting the GSP agreement draft:

> **ISO 27001 audit by a CERT-In-empanelled auditor before go-live and annually at GSP's cost.**

If a GSP batch-6 window opens — [[02-gstin-verification|02 — GSTIN verification]] records that no window was open as of 2026-08-05 and that empanelment opens episodically — then ISO 27001 stops being a commercial nicety and becomes a **gate with a 3–6 month lead time**. That single sentence is the strongest argument in this document for starting the groundwork before anyone asks.

The other realistic askers, in rough order of likelihood:

- **IOCL**, at the point the [[IOCL_Amey_31072026/discussion-document|Amey discussion]] converts into anything contractual — a PSU's IT security questionnaire is where this surfaces first, usually before commercial terms.
- **Enterprise transporters** — the [[transporters/09_Sales_Strategy|transporter sales strategy]] already lists "ISO 27001 path" on the security one-pager. A prospect asking "are you certified?" and hearing "we're on the path, here is our control set" is survivable exactly once per deal.
- **Banks and payment partners** as the [[problem-statement|Easebuzz]] relationship deepens beyond a standard merchant integration.

### 3.2 What edition, and what it actually involves

The current edition is **ISO/IEC 27001:2022**, published 25 October 2022, plus **Amendment 1:2024** (February 2024), which requires the organisation to determine whether climate change is a relevant issue in clauses 4.1/4.2 — a documentation line, not a programme ([ISO — 27001:2022/Amd 1:2024](https://www.iso.org/standard/88435.html); [HighTable — Amendment 1 explained](https://hightable.io/iso27001-2022-amendment-1-climate-action-changes-executive-briefing/)).

There is no legacy question for us: **all ISO/IEC 27001:2013 certificates expired on 31 October 2025** at the end of the IAF three-year transition ([A-LIGN — ISO 27001 transition](https://www.a-lign.com/articles/iso-27001-transition); [Hicomply — 2022 vs 2013](https://www.hicomply.com/blog/iso-27001-2022-vs-2013---the-final-countdown-to-transition)). We would certify directly to :2022 + Amd 1. If a consultant quotes anything referencing :2013, that alone disqualifies them.

What a certification body will actually want to see, beyond the twelve controls:

| Artefact | What it is | Do we have it? |
| --- | --- | --- |
| Information security policy | The top-level signed policy | No — [[T27-policy-handbook-toc\|T27]] is the right home |
| Risk assessment + risk treatment plan | Named assets, threats, scored risks, decisions | No — the [[T15-risk-register\|T15]] risk register is the seed, needs an infosec cut |
| **Statement of Applicability (SoA)** | Every Annex A control: applied or excluded, with justification | No — this is the single biggest document |
| Internal audit | Someone audits the ISMS before the CB does | No — a small company usually buys this |
| Management review | Minuted leadership review of the ISMS | Folds into the board/ops cadence ([[08-the-operating-cadence\|lesson 08]]) |
| Supplier security | Data-processing terms per vendor | Partly — [[T14-vendor-and-tool-register\|T14]] already asks for this |
| Secure development | SDLC, code review, release control | Partly — [[T26-release-checklist\|T26]] and [[12-product-and-engineering-operations\|lesson 12]] |
| Evidence of operation | Access reviews, backup restores, incident drills — **run, logged, dated** | This is what [[07-tools-and-it-foundation\|lesson 07]] §6 produces |

The last row is why the sequencing rule matters. An auditor does not certify intentions; they sample **records over a period**. A system that has been running three months audits cleanly; one that was assembled last week does not.

### 3.3 Scope — the sentence customers actually read

Certification is granted to a legal entity **for a defined scope**, and the scope statement is printed on the certificate. Enterprise reviewers read it. Propose something narrow and honest:

> *"Design, development, hosting, and support of the DZZLO OMS platform (API, web and mobile applications), Raipur, India."*

A narrow scope is cheaper to audit, faster to reach, and passes review. A sprawling "all business operations of VSYST Technologies" scope costs more, takes longer, and invites questions we cannot yet answer.

### 3.4 Cost and timeline

| Line item | Indicative | Source |
| --- | --- | --- |
| Consulting / implementation | ₹1–3 lakh | [TCSA — ISO 27001 cost India 2026](https://www.tcsa.in/resources/iso-27001-cost-india-2026) |
| Certification body audit (Stage 1 + Stage 2, billed separately) | ₹0.8–1.2 lakh | same |
| **Total, small Indian company** | **₹1–4 lakh** | same |
| Time, kickoff → certificate | **12–16 weeks** fast track; **3–6 months** typical | [Secureframe — certification timeline](https://secureframe.com/hub/iso-27001/certification-timeline) |
| Stage 1 → Stage 2 gap | typically 6–8 weeks; the ISMS should have run ≥3 months | [Glocert — Stage 1 vs Stage 2](https://www.glocertinternational.com/resources/guides/iso-27001-certification-process/) |
| Ongoing | annual surveillance audits (years 1 and 2), full recertification in year 3 | [ISMS.online — audit cycle](https://www.isms.online/iso-27001/audits/cycle-phases-timelines/) |

**VERIFY LIVE** — all figures are 2026 market estimates from certification vendors, i.e. from parties selling the service. Get three written quotes and compare **three-year totals**, not year-one prices: surveillance audits are where a cheap first year is recovered.

The rupee figure is downstream of **audit days**, which accreditation rules fix rather than the certification body: an ISMS audit at our headcount is roughly **5 days**, against 1.5–2 for a QMS. **§6.2 derives the numbers** and gives the questions to put to any quote. Note also that the MSME certification subsidy (§6.4) does **not** extend to 27001 — budget this one in full.

Budget the recurring line in [[T20-budget-vs-actual-and-cash-forecast|T20]] the moment the project starts, not the year it renews.

### 3.5 The decision rule

> **Start the ISMS when a deal that needs it becomes _probable_ — not when it is signed.** The lead time is the entire point. A customer who asks in March and needs a certificate by June cannot be served by a project started in March.

## 4. ISO/IEC 27701 — privacy, now standalone, and the DPDP clock

The important change: **ISO/IEC 27701:2025**, published **14 October 2025**, is a **standalone management system** — it no longer requires ISO/IEC 27001 certification as a prerequisite ([ISO — 27701:2025](https://www.iso.org/standard/27701); [Neutral Partners — privacy stands alone](https://neutralpartners.com/resources/blog/iso-iec-27701-2025-is-here-privacy-stands-alone)). The 2019 edition was an extension to 27001; the 2025 edition is not. It also widens coverage to biometric data, health data, IoT and AI-related privacy risks.

Why it matters specifically to us: [[07-tools-and-it-foundation|lesson 07]] §6 establishes that **DZZLO is a Data Fiduciary** for its own users, employees and leads **and a Data Processor** for dealers' customer data. The Processor role is the one that shows up as a clause in a customer contract — and the counterparty asking for DPDP warranties is the counterparty who will eventually ask how we evidence them. A PIMS is the standard answer.

One practical caveat: **ISO/IEC 27706:2025** only recently defined the requirements for certification bodies auditing a PIMS, so the pool of **accredited** Indian auditors for 27701:2025 is still thin. ⚠️ **VERIFY LIVE** before promising any customer a certificate on a date.

**Recommendation:** treat the PIMS documentation as part of the **"DPDP-ready" project** that [[13-compliance-calendar-risk-and-insurance|lesson 13]] §2.3 already puts on the calendar with a hard end date of **13 May 2027**. Write the notice, consent, retention, erasure, grievance and breach-response artefacts because the law requires them; the fact that they double as PIMS evidence is the free part. Buy the certificate only when a named customer asks.

## 5. ISO 9001 — only for tenders, and there is a live timing window

ISO 9001 certifies a **quality management system**, not security. Its entire value to us is procurement: PSU and government pre-qualification criteria frequently list it, and IOCL's vendor enlistment runs on well-defined PQC covering financial, commercial and technical capability ([Indian Oil — vendor enlistment process, PDF](https://lakshya-bharat.com/api/ClientUploads/EnlistmentBronchure/Vendor%20enlistment%20process.pdf)). Whether any specific IOCL software tender demands it is tender-by-tender — ⚠️ read the actual PQC of the tender in front of you; do not certify on speculation.

**The window, as of today:** ISO 9001 is being revised. The FDIS approval ballot closed **10 July 2026** and publication of **ISO 9001:2026** is scheduled for **16 September 2026**, with a three-year transition to **September 2029** ([Punyam — publication expected September 2026](https://www.punyam.com/blog/iso-9001-revision-update-publication-expected-in-september-2026/); [SGS — key updates and transition](https://www.sgs.com/en/showcases/iso-9001-2026-key-updates-and-transition-guidance)). The revision adds emphasis on quality culture, ethical conduct, clearer risk-and-opportunity handling, and climate change. **VERIFY LIVE** — a publication date is a schedule until it is history.

| Situation | Do this |
| --- | --- |
| A tender needing ISO 9001 closes **before ~Nov 2026** | Certify to **:2015 now**. The PQC wants a valid accredited certificate; transition later inside the 3-year window |
| Tenders are a **2027 plan** | **Wait.** Certify directly to **:2026** after publication and skip a transition audit entirely |
| No tender pipeline exists | **Do nothing.** ISO 9001 buys us nothing outside procurement |

**The cost changes this decision.** ISO 9001 at our size is a **1.5–2 day** audit costing **₹25,000–75,000** all-in, and the Ministry of MSME reimburses **75% up to ₹75,000** for micro and small enterprises with Udyam registration — 9001 is explicitly in scope for that scheme where 27001 is not (§6.2, §6.4). A near-free certificate that unlocks tender eligibility is a different proposition from a ₹3-lakh one, so the "is the pipeline real?" bar is lower here than anywhere else in this document. It is still not zero: an unused certificate carries annual surveillance audits forever.

## 6. Cost, time and eligibility — the numbers

The three questions a founder actually asks. Taken in that order, because the answer to the third one changes the first two.

### 6.1 Eligibility — are we even allowed to be certified?

**Yes, today.** There is **no minimum turnover, headcount, company age or revenue** for any ISO management-system certification. A registered legal entity with a defined scope and a management system that is genuinely running is eligible. VSYST Pvt Ltd clears that bar now, at three people, pre-revenue.

What gates us is not eligibility, it is **evidence**. A certification body will not proceed to Stage 2 until the system has produced records to sample:

| Prerequisite before Stage 2 | Why | Do we have it? |
| --- | --- | --- |
| A defined, documented scope | It is printed on the certificate (§3.3) | One sentence of work |
| The management system **operating for ~3 months** | The auditor samples records over a period; there is no fixed minimum in the standard, but ~3 months is the working expectation | **No — this is the clock that cannot be bought** |
| **At least one complete internal audit** | ISO 27001 cl. 9.2 / ISO 9001 cl. 9.2 | No — usually outsourced by a small company |
| **At least one management review** | cl. 9.3, minuted | No — folds into the board cadence |
| Risk assessment + treatment plan, and (for 27001) the **SoA** | The core documents an auditor reads first | No — §3.2 lists them |
| Day-to-day operational records | Access reviews, backup restores, incident records, training sign-offs | Partially — this is exactly what [[07-tools-and-it-foundation\|lesson 07]] §6 produces |

Sources for the prerequisite set: [Sprinto — ISO 27001 audit requirements and stages](https://sprinto.com/blog/iso-27001-audit/); [Glocert — Stage 1 vs Stage 2](https://www.glocertinternational.com/resources/guides/iso-27001-certification-process/).

**The eligibility bar that can actually block us is somewhere else.** ISO certification has no entry criteria; the **programmes that demand the certificate** do. From [[02-gstin-verification|02 — GSTIN verification]], GSP 5.0 empanelment required an Indian IT/ITES/BFSI company or MSME with **average turnover ≥ ₹50 lakh** across FY 2020-21 → 2022-23, a technical demo scored **≥70/100**, India-based infrastructure sized for **≥1 lakh GST transactions/month**, a data-privacy policy, an affidavit, and **MPLS connectivity to GSTN within 60 days of signing**. That is a real eligibility test, and we would fail the turnover limb today. Worth knowing before treating the GSP path as available.

### 6.2 Where the cost comes from — audit days, not salesmanship

A certification quote is, at bottom, **audit days × day rate**. The days are not a negotiating position: they are fixed by accreditation rules that bind the certification body.

**ISO 9001 / QMS** — IAF MD 5:2023, Table QMS 1, initial audit (Stage 1 + Stage 2 combined), by *effective number of personnel*:

| Effective personnel | Initial audit days |
| --- | --- |
| **1–5** | **1.5** |
| **6–10** | **2** |
| 11–15 | 2.5 |
| 16–25 | 3 |
| 26–45 | 4 |

**ISO 27001 / ISMS** — ISO/IEC 27006-1 sets a different, higher scale: roughly **5 audit days for an organisation under 10 people**, rising to 14+ around 200 staff ([ISMS.online — ISO 27006](https://www.isms.online/iso-27006/)). At our headcount an ISMS audit is about **three times** a QMS audit, and that ratio — not consultant greed — is why 27001 costs what it does.

The rules around those numbers, all from [IAF MD 5:2023](https://iaf.nu/iaf_system/uploads/documents/IAF_MD5_Issue_4_Version_3_14062023.pdf):

- **Surveillance ≈ 1/3** of the initial audit time, annually. **Recertification ≈ 2/3** of what an initial audit would take today (cl. 5, cl. 6). Neither is normally under one audit day.
- **Effective personnel** includes part-time and partially-in-scope people converted to full-time equivalents (cl. 2.3.3) — so contractors count, and a 3-person company does not become a 1-person audit.
- **Reductions are capped at 30%** of the table figure (cl. 3.9). Three of the standard reduction factors genuinely apply to us (cl. 8 v): *very small site for the number of personnel*, *high level of automation*, and *staff working off-location whose compliance is auditable through records*.
- Days are rounded to the nearest half day (cl. 2.2.3), and remote auditing cannot cut on-site duration below 80% (cl. 4.1).

**The practical use of this section:** ask every quote to state **audit days for Stage 1, Stage 2, surveillance and recertification, separately**. A quote that won't state days is not a quote — and a quoted day-count materially below the table is a certificate that will not survive scrutiny.

### 6.3 The rupee ranges

| What | Audit days at our size | Year-1 all-in | Ongoing | Elapsed time |
| --- | --- | --- | --- | --- |
| **ISO/IEC 27001** | ~5 | **₹1–4 lakh** (consulting ₹1–3 L + CB audit ₹0.8–1.2 L) | Surveillance yr 1 & 2 ≈ 1/3 days each; recertification yr 3 ≈ 2/3 | 12–16 weeks fast track; **3–6 months** typical |
| **ISO 9001** | 1.5–2 | **₹25,000–75,000** for under 25 staff, accredited and all-in — **less after the MSME subsidy, §6.4** | Annual surveillance | 2–4 months |
| **ISO/IEC 27701** | Increment on the ISMS audit | Cheapest as an **integrated audit alongside 27001** — shared clauses are audited once; standalone costs materially more | Folded into the same cycle | Add to the 27001 timeline |
| **CERT-In-empanelled VAPT** | n/a — engagement, not certification | **₹40,000–1.5 lakh** for a typical SaaS web-app scope; ₹1.5–4 lakh at moderate complexity | Annual re-test, renewal-gated for govt programmes | 2–6 weeks |
| **ISO 27017 / 27018** | Small increment | Marginal, as a scope extension on an existing 27001 audit | Same cycle | Same cycle |

Sources: [TCSA — ISO 27001 cost India 2026](https://www.tcsa.in/resources/iso-27001-cost-india-2026); [JS Certification — ISO 9001 cost India 2026](https://jscertification.com/iso-9001-certification-cost-in-india/); [ISMS.online — ISO 27701:2025 certification cost](https://www.isms.online/iso-27701/certification-2025/certification-cost/); [TCSA — VAPT cost India 2026](https://www.tcsa.in/resources/vapt-cost-india-2026). All **VERIFY LIVE** — every figure comes from a party selling the service.

**Two price floors that mean "fake":**

- An **ISO certificate for ₹999–₹5,000** with no audit. Hundreds of Indian outfits sell these; they have no commercial value and fail the §8 checks.
- A **"VAPT" for ₹10,000–₹25,000**. That is an automated tool scan with no manual testing, and it will not satisfy a compliance auditor — which is the only reason we would be buying one.

### 6.4 The subsidy — ISO 9001 can be close to free

The Ministry of MSME runs an **ISO 9001 / ISO 14001 / HACCP certification reimbursement scheme**: **75% of expenditure, capped at ₹75,000** per certification, for permanent-registered micro and small enterprises with Udyam registration ([Ministry of MSME — reimbursement scheme](https://my.msme.gov.in/MyMsmeMob/MsmeScheme/Pages/0_2_2.html); [MSME — FAQ Q.16](https://msme.gov.in/faqs/q16-there-support-available-obtaining-iso-certification)).

Two consequences worth acting on:

1. Against a ₹25,000–75,000 ISO 9001 cost, 75% reimbursement makes the certificate **nearly free** — which lowers the bar in §5 considerably if any tender path is plausible.
2. **The scheme does not cover ISO 27001.** It is written for 9001/14001/HACCP. Do not budget a 27001 project assuming a subsidy. ⚠️ **VERIFY LIVE** with the CA — scheme scope and the Udyam prerequisite both change by notification, and [[05-phase-5-indian-accounting-system|Finance Phase 5]] already tracks our DPIIT/Udyam position.

### 6.5 Where the time actually goes

The elapsed-time figures in §6.3 are dominated by one immovable block. Roughly, for ISO 27001:

| Weeks | What happens | Compressible with money? |
| --- | --- | --- |
| 0–2 | Scope defined, gap analysis against Annex A | Yes |
| 2–8 | Documentation: policy, risk assessment, treatment plan, SoA, procedures | Yes — this is what consultants sell |
| **8–20** | **The ISMS operates and generates records** (~3 months minimum) | **No** |
| ~week 20 | Internal audit + management review completed | Partly |
| ~week 21 | **Stage 1** — documentation review; improvement requests issued | — |
| +6–8 weeks | **Stage 2** — implementation verified, 3–7 days on site depending on scope | Slightly |
| +2–4 weeks | Nonconformities closed, certificate issued | Partly |

Sources: [Secureframe — certification timeline](https://secureframe.com/hub/iso-27001/certification-timeline); [Glocert — Stage 1 vs Stage 2](https://www.glocertinternational.com/resources/guides/iso-27001-certification-process/); [ISMS.online — audit cycle](https://www.isms.online/iso-27001/audits/cycle-phases-timelines/).

> **The one sentence that matters:** the ~3 months of operating evidence is the irreducible floor, and no budget compresses it. That is the entire argument for finishing the twelve controls **now** ([[07-tools-and-it-foundation|lesson 07]] §6) — not because we intend to certify this year, but because it converts a 6-month project into a 6-week one on the day a customer asks.

## 7. The non-ISO asks that will reach us first

In Indian practice these get asked **before** anyone asks for ISO 27001.

| Ask | Where it comes from | Cost / time | Notes |
| --- | --- | --- | --- |
| **CERT-In-empanelled auditor / VAPT certificate** | Recurs across **every** government integration we researched: DigiLocker, NTR/MoRTH, GSP, UIDAI Sub-AUA | **₹40k–1.5 L** typical SaaS web-app scope; 2–6 weeks; annual re-test | [[tasks_15_govt_apis/references\|tasks_15 · references]] concludes it directly: **budget one auditor relationship** — a single engagement can serve several programmes. Most are **annual**, renewal-gated |
| **STQC audit of the application** | DigiLocker / API Setu onboarding, post-integration | ⚠️ quote — not published | [[05-apisetu-digilocker-onboarding\|05 — API Setu / DigiLocker]] §Audits |
| **Annual re-audit + fresh certificate** | NTR/MoRTH: 1-year client-ID validity, annual renewal + fresh audit | Recurring, per above | [[04-vehicle-rc-driving-licence\|04 — Vehicle RC / DL]] |
| **PCI DSS SAQ-A** | If card data ever transits our flow via [[04-payment-flow\|Easebuzz]] | Self-assessment: internal effort + ASV scan | A self-assessment, not an audit — but no longer trivial, see below |
| **SOC 2 Type II** | US / international buyers only | 6–12 months; separate budget | ~80% control overlap with 27001. **Do not run both without a named customer demanding the second** |
| **DPDP compliance** | Statutory | Internal + legal | Not certifiable. Evidence it via §4 |

On **PCI DSS**: SAQ-A covers fully outsourced e-commerce merchants using a redirect or iframe to a compliant gateway — which is the normal Easebuzz shape. Under **v4.0.1**, two requirements now apply to SAQ-A e-commerce merchants that did not before: **6.4.3** (payment-page script management — every script authorised, inventoried with written justification, integrity assured) and **11.6.1** (payment-page tamper detection) ([PCIDSS Dashboard — SAQ-A for hosted checkout](https://pcidss-dashboard.com/blog/saq-a-for-hosted-checkout-pages-what-you-need-to-know/); [Hyperproof — new SAQ A eligibility criteria](https://hyperproof.io/resource/pci-dss-4-0-update-new-saq-a-eligibility-criteria/)). Requirements 2, 6, 8 and 11 also apply to the web server hosting the redirect, and that server must be in the external vulnerability scan scope. Separately, RBI rules prohibit merchants storing CVV and mandate tokenisation for online card storage — ⚠️ **VERIFY LIVE** with Easebuzz which SAQ tier our integration model puts us in, in writing, before go-live.

## 8. Buying it without being sold a fake

India has a large, cheap market in **unaccredited** ISO certificates. They arrive in a week, cost a fraction, and fail the first serious procurement review — the proliferation of fake certificates out of India has reportedly tripled over ten years ([Oxebridge — hotspots for unqualified ISO certificates](https://www.oxebridge.com/emma/top-five-hotspots-for-unqualified-iso-certificates/)). Spending ₹25,000 on a worthless certificate and then ₹3 lakh on a real one is the worst available outcome.

The checks, in order:

1. **The certification body must be accredited by an IAF MLA signatory** — **NABCB** in India (a full IAF member and MLA signatory, [NABCB on IAF CertSearch](https://www.iafcertsearch.org/accreditation-body/26010c7f-faa6-5e5b-9e55-a2e121c45e5d)), or UKAS, ANAB and equivalents.
2. **The certificate must carry both logos** — the certification body's *and* the accreditation body's mark. A certificate with only the CB's logo, or an IAF logo without a real accreditation, is unaccredited ([NABCB — guidance on selecting a certification body, PDF](https://nabcb.qci.org.in/wp-content/uploads/2023/08/BCB-602_Guidance-on-selection-of-CB_NABCB_Sept-2018.pdf); [CCC — how to tell if a certificate is genuine](https://ccc-consultants.org/how-do-you-know-if-your-iso-certificates-are-genuine/)).
3. **Verify the body independently** at [iafcertsearch.org](https://www.iafcertsearch.org/) before signing — not from the body's own website.
4. **Check the accreditation scope covers IT/software**, not just manufacturing. An accredited body outside its scope is the same problem wearing better clothes.
5. **The consultant cannot be the certifier.** Impartiality rules forbid the body that built your ISMS from auditing it. Anyone offering "implementation + certificate, one package" is telling you which kind of certificate it is — walk.
6. **Compare three-year totals** — Stage 1 + Stage 2 + two surveillance audits + recertification, plus audit-day counts. A low year-one price with unspecified audit days is not a quote.

Put the chosen body and its renewal dates in [[T14-vendor-and-tool-register|T14]] like any other vendor, with the 60-day renewal alert from [[14-vendors-procurement-and-cost-control|lesson 14]].

## 9. The trigger table — what starts what

Certification is not a date on the calendar; it is an **event-driven row**, like the ones in [[13-compliance-calendar-risk-and-insurance|lesson 13]] §2.3. Write these into [[T16-compliance-calendar|T16]] as dormant rows with the trigger stated, and the scored version of the risk ("a deal is lost for want of a certificate we cannot obtain in time") into [[T15-risk-register|T15]].

| Trigger event | Action it fires | Owner | Lead time | Budget |
| --- | --- | --- | --- | --- |
| An IOCL / enterprise **security questionnaire** arrives | Answer from the twelve controls; open the ISO 27001 project if the deal is probable | CEO/CTO + COO | 3–6 months | ₹1–4 L |
| **GSP batch-6 window opens** ([[02-gstin-verification\|02]]) | ISO 27001 + CERT-In-empanelled audit become **mandatory before go-live** | CEO/CTO | 3–6 months | ₹1–4 L + annual audit |
| Any **government API** onboarding starts (DigiLocker, NTR, e-way/e-invoice) | Engage the CERT-In-empanelled auditor; STQC where applicable | CEO/CTO | 1–3 months | Per [[tasks_15_govt_apis/00-overview\|tasks_15 overview]] |
| A **PSU tender PQC** lists ISO 9001 | Apply the §5 timing rule | COO | 2–4 months | ₹25k–75k, 75% MSME-reimbursable |
| First enterprise contract with **DPDP / processor clauses** | Complete the PIMS artefacts; certify 27701 only if demanded | COO | Aligned to 13 May 2027 | Incremental |
| **Easebuzz production go-live** | Confirm SAQ tier in writing; close 6.4.3 / 11.6.1 | CEO/CTO | Weeks | Internal effort |
| A **US/international** customer asks | SOC 2 Type II — only then, and reuse the 27001 controls | COO | 6–12 months | Separate |
| DZZLO ships **AI that decides** something about a user | Re-open ISO/IEC 42001 as a real question | CEO/CTO | — | — |

## 10. The next 90 days — with no certificate purchased

1. **Finish the twelve controls in [[07-tools-and-it-foundation|lesson 07]] §6 and keep the evidence** — dated access reviews, a completed restore drill, a signed acceptable-use policy. Evidence over a period is the thing an auditor samples; it cannot be back-dated.
2. **Write four documents we need anyway**: the information security policy ([[T27-policy-handbook-toc|T27]]), an infosec cut of the risk register ([[T15-risk-register|T15]]), a **draft Statement of Applicability**, and data-processing terms per vendor in [[T14-vendor-and-tool-register|T14]]. These are ~70% of a 27001 project and 100% useful without one.
3. **Shortlist two or three CERT-In-empanelled auditors** and get quotes. One relationship, several programmes — this is the single highest-leverage purchase on the page, and it is needed before ISO anything.
4. **Add the dormant rows** from §9 to [[T16-compliance-calendar|T16]], and the certification budget line to [[T20-budget-vs-actual-and-cash-forecast|T20]].
5. **Confirm Udyam registration and the MSME reimbursement route** with the CA (§6.4) — it is the difference between a ₹75,000 ISO 9001 and a ₹19,000 one, and it must be in place *before* the certification spend, not claimed afterwards.
6. **Decide ISO 9001 only against a real tender pipeline** — and if the pipeline is 2027, wait for the September 2026 publication.
7. **Prepare the security one-pager** the [[transporters/09_Sales_Strategy|sales strategy]] already calls for: data residency, DPDP alignment, RBAC, encryption, the twelve controls, and an honest "27001 on trigger" line. It answers the question in most deals without a certificate.

## 11. Standards to implement, not certify

These cost nothing, are never audited, and prevent rework. Worth stating once so nobody re-litigates them per feature.

| Standard | Use in DZZLO |
| --- | --- |
| **ISO 8601** | All stored timestamps — UTC in the API and the database, not only in file naming ([[07-tools-and-it-foundation\|lesson 07]] §7 already mandates ISO dates for documents) |
| **ISO 4217** | Currency codes (`INR`) wherever money is stored or transmitted |
| **ISO 3166-1** | Country codes. ⚠️ Note the trap: **GST state codes are not ISO 3166-2** — they are Indian census codes. Do not map one onto the other |
| **ISO 639-1** | Language codes, if the app localises |
| **ISO 20022** | The direction bank statement and payment messaging is moving. Relevant if voucher reconciliation ever pulls from bank APIs instead of manual entry — worth knowing **before** designing that, not after |
| **ISO/IEC 25010** | Product quality model — a usable non-functional-requirements checklist for the partner API work ([[tasks_11_partner_api/07-phase-7-rollout-docs-versioning\|tasks_11 · phase 7]]). A reference model, not certifiable |

---

_Related: [[07-tools-and-it-foundation|COO 07 — Tools and IT Foundation]] · [[13-compliance-calendar-risk-and-insurance|COO 13 — Compliance Calendar, Risk and Insurance]] · [[12-product-and-engineering-operations|COO 12 — Product and Engineering Operations]] · [[05-legal-and-governance-foundation|COO 05 — Legal and Governance]] · [[tasks_15_govt_apis/00-overview|tasks_15 — Government APIs]] · [[startup-operations-plan|Startup Operations Plan]]_
