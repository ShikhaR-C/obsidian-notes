# Easebuzz Merchant Onboarding — Document Plan

Working file. Easebuzz's merchant-onboarding checklist (received 2026-08-21) asks VSYST Technologies Pvt. Ltd. for eight documents that do not exist today: business model, use case of the payment gateway, payment flow, highlight of mandatory policies, cancellation & refund policy, terms & conditions, about us (with contact), and governing law & dispute resolution. This plan holds the boilerplate for those eight; each is then filled from the live projects in `v1_79` and from facts the user supplies.

Everything else on Easebuzz's checklist (PESO licence, board resolution, UBO declaration, sales invoices, CPV contact, ERP URL with sample login, integration URLs) has **already been provided by the user** and is out of scope here.

**Writing rule.** Keep every document short. VSYST is pre-revenue: where a number or a process is not yet real, write it as an **assumption or expectation**, labelled as such — never as a commitment or a current fact. Nothing is invented; every ⟨placeholder⟩ is sourced from code/vault or left for the user.

Prior fact base (verified with the user, Jul 2026): `../20260708/IPG_Proposal_UBI_VSYST.md` (company profile, fund flow), `../20260708/proposalplan.md` (bank Q&A), `../problem-statement.md` (why an IPG, rails, verification APIs).

**Facts settled 2026-08-21:** app on the stores since **June 2021**; company incorporated **21 Oct 2021**; the app is **not publicly launched — access is by referral only** (controlled rollout). About Us and Business Model say exactly this.

## Easebuzz's wording → deliverable

| Easebuzz asked for                      | File                                     | Notes                                                                                                                                                                            |
| --------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| About us · Contact us                   | `01-about-us.md`                         | Two page-ready sections; carries legal name and address **as per GST**                                                                                                           |
| Business model                          | `02-business-model.md`                   |                                                                                                                                                                                  |
| Use case of payment gateway             | `03-payment-gateway-use-case.md`         |                                                                                                                                                                                  |
| Payment flow                            | `04-payment-flow.md`                     | Current flow in `dzzlo_oms_app` (from code), then expected flow with Easebuzz                                                                                                    |
| Highlight mandatory policies            | `05-mandatory-policies.md`               | One table in Easebuzz's A–F order: policy → where published → status                                                                                                             |
| A) Cancellation and refund policy       | `06-cancellation-refund-policy.md`       | Page-ready                                                                                                                                                                       |
| B) Terms and conditions                 | `07-terms-and-conditions.md`             | Page-ready                                                                                                                                                                       |
| E) Governing law and dispute resolution | `08-governing-law-dispute-resolution.md` | Follows Easebuzz's example: _"These terms shall be governed by the laws of India. Any disputes will be subject to the jurisdiction of courts located in India…"_; reused in A, B |
| F) Business name and address as per GST | footer line on `01`, `06`, `07`          | Same text everywhere: "VSYST Technologies Private Limited, ⟨address as on GST certificate⟩, GSTIN 22AAICV3528R1ZT"                                                               |

**Privacy policy** (not on Easebuzz's list; user asked): the one live at https://dzzlo-oms.web.app is a Feb-2021 generator template in Paresh Chawra's name (pre-incorporation), Gmail contact, says data is "not collected by me", and does not mention payments. It will need re-issuing in the company's name with a payments clause before go-live — **separate track, not part of this set**.

## Status

Each step is done, then paused for manual checking before the next begins.

- [x] Step 0 — Plan with boilerplate _(2026-08-21)_; scoped to Easebuzz's actual wording _(2026-08-21)_
- [x] Step 1 — About Us + Contact Us (`01`) _(drafted 2026-08-21; awaiting manual check — placeholders: GST address verbatim, traction figures, support hours, grievance officer)_
- [x] Step 2 — Business Model (`02`) _(drafted 2026-08-22; awaiting manual check — placeholders: traction figures, first-phase outlet count)_
- [x] Step 3 — Use Case of the Payment Gateway (`03`) _(drafted 2026-08-22; awaiting manual check — placeholder: web channel)_
- [x] Step 4 — Payment Flow (`04`) _(drafted 2026-08-22 from `api_v3/services/voc_msts.js` + NewPayment / NewPayAck / NewVoucher / Payments screens; awaiting manual check — placeholder: auto-clear window for abandoned gateway payments)_
- [x] Step 5 — Mandatory Policies highlight (`05`) _(drafted 2026-08-22; awaiting manual check — placeholders: site and page URLs, in-app placement, status column to be finalised at Step 9)_
- [x] Step 6 — Cancellation & Refund Policy (`06`) _(drafted 2026-08-22; awaiting manual check — placeholders: date, refund initiation and bank-credit windows, subscription refund stance, grievance officer, courts)_
- [x] Step 7 — Terms & Conditions (`07`) _(drafted 2026-08-22; awaiting manual check — placeholders: date, liability cap, grievance officer and SLAs, courts)_
- [x] Step 8 — Governing Law & Dispute Resolution (`08`) _(drafted 2026-08-22; awaiting manual check — placeholders: date, courts, grievance officer and SLAs)_
- [ ] Step 9 — Read-through; export to `.docx`; create policy pages.
  - [x] 9a Read-through _(2026-08-22: wording aligned across all eight; invoice states now use the app's labels Unpaid / Processing / Paid / Part-paid; screen named "Payment ACK" as in the app; no placeholder filled — those stay for the user)_
  - [x] 9b Export to `.docx` _(2026-08-22: all answers applied and every ⟨placeholder⟩ resolved to final text across `01`–`08`; combined `Easebuzz_Onboarding_VSYST.docx` generated — cover + the eight documents, Georgia/Arial, running header, page numbers. ⚠ "Last updated: 11/02/2021" was applied to `06`–`08` as instructed — it predates incorporation (Oct 2021) and the DPDP Act 2023 cited in the text; recommend the submission date instead. Regenerate after edits: `python3 <scratchpad>/make_docx.py`)_
  - [x] 9c Policy pages generated _(2026-08-22: standalone HTML in `pages/` — about, contact, terms, refund-policy, governing-law .html; self-contained inline CSS, cross-linked nav, GST footer on every page; regenerate after .md edits with `python3 <scratchpad>/make_pages.py`. Upload to vsyst.in and map /about etc. (or keep .html paths and update `05`'s URLs), then flip `05` statuses to Published)_

## Source map

| Fact needed                                                      | Source in `v1_79`                                                                                                                                                                                                                                                                                                                             | Status                                |
| ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Company particulars (CIN, PAN, GSTIN, address, DPIIT, directors) | `../20260708/IPG_Proposal_UBI_VSYST.md` §2                                                                                                                                                                                                                                                                                                    | Verified — address to match GST cert  |
| Founding story, product description                              | `../20260708/proposalplan.md`; `dzzlo_oms_app/AI.md`; `dzzlo_oms_api/docs/ARCHITECTURE.md`                                                                                                                                                                                                                                                    | Available                             |
| Traction, volumes, ticket sizes, rails                           | proposal §1, §4; `../problem-statement.md` §1–2                                                                                                                                                                                                                                                                                               | Available — state as expectations     |
| Revenue model (free now; per-GSTIN dealer subscription planned)  | `docs/learning/app-store-economics/`, `docs/learning/company/`                                                                                                                                                                                                                                                                                | Available — state as plan, no figures |
| Merchant structure, fund flow, refunds principle                 | proposal §5; `proposalplan.md` Q3/Q5/Q7                                                                                                                                                                                                                                                                                                       | Agreed                                |
| **Current in-app payment flow**                                  | App: `Customer/NewPayment/index.js`, `Customer/NewPayAck/index.js`, `Dealer/NewVoucher/index.js`, `Common/Payments/`, `Common/_Voucher_/`. API: `models/voc_msts.js` (`pay_mode` cash/cheque/card/fleetcard/neft/rtgs; `pay_status`; `voc_type`; `invs_adj`), `models/month_crdrs.js` (ledger), `models/pay_trns.js`, `api_v3` voucher routes | Read in Step 4                        |
| Support / grievance contact                                      | `Common/ContactUs/`, `Common/Help/`; proposal contact line                                                                                                                                                                                                                                                                                    | Grievance officer name from user      |

---

## 1. About Us + Contact Us — boilerplate

**About Us (half a page).** Who we are (legal entity, incorporated Oct 2021, registered office, DPIIT) · What we build (DZZLO OMS, one paragraph; on the stores since June 2021; currently referral-only rollout) · Our story (35+ yrs dealership experience, built on the family outlet, founders) · Particulars table (legal name, CIN, date of incorporation, registered office **as per GST**, PAN, GSTIN, DPIIT cert, directors).

**Contact Us (page-ready).** Legal name and address as per GST · support email · phone · hours · grievance officer · in-app route (Help / Contact Us screens).

## 2. Business Model — boilerplate

Half a page, framed as **current state + expectation**.

- What the platform is: vertical SaaS for petrol pump dealers and their credit customers (transport companies). VSYST is the technology layer; dealers sell fuel; VSYST sells no fuel and touches no funds.
- Parties table: Dealer (seller, sub-merchant, future subscriber) · Customer firm (buyer, free) · VSYST (platform, master merchant).
- What is transacted: fuel dispensed at the outlet against a verified order; GST invoice raised in-platform; payment against invoice.
- How VSYST earns — **today: nothing (free, referral-only adoption phase). Expected: subscription to dealer companies per GSTIN, billed on the web; users free; no commission on payments.**
- Scale — **current:** 2 dealers, 130+ users, 130+ txns/day ⟨re-confirm⟩. **Expected:** ₹10–20 lakh/dealer/month, growing with dealer count; labelled projection.

## 3. Use Case of the Payment Gateway — boilerplate

Half a page.

- One line: a transport company pays a dealer's invoice for fuel already dispensed, inside the DZZLO app; the invoice closes in the shared ledger at once.
- Payer → payee: customer firm's bank account → dealer's own account (T+1 via Easebuzz). Post-delivery settlement of a credit invoice; no shipping.
- Expected transaction profile table: net banking avg ₹1 lakh (₹5k–₹5L, core) · UPI avg ₹5k (₹1k–₹50k) · cards (supporting). Recurring, firm-to-firm. **All figures = expectations from observed dealer throughput.**
- What it replaces: manual net-banking transfer outside the app + next-morning statement matching.
- Channels: Android, iOS ⟨, web⟩. Also requested: verification APIs (bank account, PAN, GSTIN, Aadhaar, RC, DL).

## 4. Payment Flow — boilerplate

One page, written from the code — not from memory.

**A. Current flow (live, no gateway).** Order → delivery → invoice → customer raises a payment voucher in-app (dealer, invoices, amount, pay_mode, bank/cheque, TDS) → customer pays the dealer outside the app → dealer confirms receipt (pay_status → true) → ledger updates, invoice closes, credit limit frees. Short voucher-lifecycle diagram with the screen names. Note what the app allows on reversal/edit.

**B. Expected flow (with Easebuzz).** Select invoice → amount pre-filled → Pay → API creates gateway request (order id = voucher id) → checkout → webhook to API (`pay_trns`) → voucher auto-confirmed → ledger closes → T+1 settlement to dealer. Failure/pending handling; refund = dealer-initiated → gateway refund → reversal voucher; daily reconciliation against the settlement report. **Labelled as the intended design, not built yet.**

**C. Data held by VSYST:** voucher, invoice, gateway txn id + status. No card/bank credentials.

No gateway is live today; the documents say so plainly and describe nothing else.

## 5. Mandatory Policies — highlight (boilerplate)

One table in Easebuzz's A–F order: policy → where published (URL + in-app screen) → status. Nothing else.

## 6. Cancellation & Refund Policy — boilerplate

One page, page-ready. Principle agreed: refunds are dealer-initiated, processed in DZZLO, executed on Easebuzz rails; VSYST holds no funds and refunds nothing on a dealer's behalf.

Clauses: Scope · Nature of transactions (fuel already dispensed; no shipment) · Order cancellation (what the app allows before dispensing) · Refunds of payments to dealers (raised by dealer; to original instrument within ⟨X⟩ working days) · Failed / pending transactions (auto-reversal; ticket) · Duplicate payments · Chargebacks (ledger as evidence) · Subscription fees (expected; ⟨stance⟩) · How to request · Contact · Governing law (→ #8) · Footer: legal name and address as per GST.

## 7. Terms & Conditions — boilerplate

Two pages, plain English, page-ready. Clauses: Acceptance · Definitions · Service description (VSYST is a technology provider, not the seller of fuel, not a lender) · Eligibility & registration (business users; OTP; company invite/approval) · Roles of Dealer / Customer / User · Orders, delivery, invoices (delivery at outlet; disputes are between dealer and customer; ledger is the record) · Payments (via RBI-authorised aggregator; VSYST holds no funds) · Platform fees (free today; subscription expected) · Refunds (→ #6) · Ledger & immutability · Credit limits (set by dealer) · Data & privacy (no card/bank credentials stored) · IP · Prohibited use · Suspension & termination (Settings → Delete Account) · Disclaimer & limitation of liability · Indemnity · Third-party services · Changes · Governing law (→ #8) · Grievance officer & contact · Footer: legal name and address as per GST.

## 8. Governing Law & Dispute Resolution — boilerplate

Short; follows Easebuzz's example wording. _"These terms shall be governed by the laws of India. Any disputes will be subject to the exclusive jurisdiction of the courts located in ⟨Raipur, Chhattisgarh⟩, India."_ Then three brief lines: grievance officer first (ack ⟨48 h⟩, resolve ⟨30 days⟩) · dealer–customer disputes are between them, VSYST supplies ledger records · payment grievances go to the payment aggregator's grievance mechanism. Reused verbatim inside #6 and #7.

---

## Open questions — resolved

All placeholders were resolved on 2026-08-22 and the final values now stand in the documents themselves: grievance officer Shikhar Chawra · info@vsyst.in; SLAs 48 hours / 7 days; courts Raipur, Chhattisgarh; address A-2/11, Udaya Society, Tatibandh, Raipur, Chhattisgarh 492099 (align the app's Help → Contact Us screen, which shows "Sector-1…"); traction 2 outlets / 130+ users / 130+ txns/day; refund windows 7 and 5–10 working days; subscription fees not refunded; liability cap = fees paid in prior 12 months or ₹10,000; web channel included; page URLs vsyst.in/{about, contact, terms, refund-policy, governing-law}. ⚠ Policy "Last updated" dates set to 11/02/2021 per user — flagged in Step 9b.

## Inbox (raw points from user — unsorted)

- 2026-08-21: _"keep the document data short. we are still pre-revenue so we are just showing our assumptions and expectations"_ → Writing rule.
- 2026-08-21: Easebuzz checklist pasted in full; items not in the original ask were already provided by the user → out of scope, noted at the top.
- 2026-08-21: _"privacy policy exists in https://dzzlo-oms.web.app. should we need a update there?"_ → answered in one paragraph above; separate track.
- 2026-08-21: _"app started on June 2021 and company registered on Oct 2021. app not yet launch for all public. just few through referrals"_ → Facts settled.
- 2026-08-21: _"stick to the requirements asked before. already provided requirements not listed in my question"_ → plan re-scoped to the eight documents.
- 2026-08-22: policy pages will be published on **vsyst.in**, not dzzlo-oms.web.app → `05` URLs.
- 2026-08-21: legacy gateway code in `api_v1` is dead — **do not mention it anywhere**; documents state only that no gateway is live today.
