# Easebuzz Merchant Onboarding — Document Plan

Working file. Easebuzz needs eight documents from VSYST Technologies Pvt. Ltd. before the DZZLO merchant account can be activated. None exist today. This plan holds the boilerplate; each topic is then filled from the live projects in `v1_79` and from facts the user supplies.

**Writing rule.** Keep every document short. VSYST is pre-revenue: where a number or a process is not yet real, write it as an **assumption or expectation**, labelled as such — never as a commitment or a current fact. Nothing is invented; every ⟨placeholder⟩ is sourced from code/vault or left for the user.

Prior fact base (verified with the user, Jul 2026): `../20260708/IPG_Proposal_UBI_VSYST.md` (company profile, fund flow), `../20260708/proposalplan.md` (bank Q&A), `../problem-statement.md` (why an IPG, rails, verification APIs).

## Status

Each step is done, then paused for manual checking before the next begins.

- [x] Step 0 — Plan with boilerplate _(2026-08-21)_
- [ ] Step 1 — About Us
- [ ] Step 2 — Business Model
- [ ] Step 3 — Use Case of the Payment Gateway
- [ ] Step 4 — Payment Flow (current flow in `dzzlo_oms_app`, then expected flow with Easebuzz)
- [ ] Step 5 — Mandatory Policies (highlight list)
- [ ] Step 6 — Cancellation & Refund Policy
- [ ] Step 7 — Terms & Conditions
- [ ] Step 8 — Governing Law & Dispute Resolution
- [ ] Step 9 — Read-through; export to `.docx`/PDF; publish policy pages; send to Easebuzz

## Output

One short markdown file per document, in this folder. #6–#8 are written so the text can be published verbatim as web/app pages; #1–#4 are for Easebuzz's merchant-review team.

| #   | Document                           | File                                     |
| --- | ---------------------------------- | ---------------------------------------- |
| 1   | About Us                           | `01-about-us.md`                         |
| 2   | Business Model                     | `02-business-model.md`                   |
| 3   | Use Case of the Payment Gateway    | `03-payment-gateway-use-case.md`         |
| 4   | Payment Flow — current & expected  | `04-payment-flow.md`                     |
| 5   | Mandatory Policies — highlight     | `05-mandatory-policies.md`               |
| 6   | Cancellation & Refund Policy       | `06-cancellation-refund-policy.md`       |
| 7   | Terms & Conditions                 | `07-terms-and-conditions.md`             |
| 8   | Governing Law & Dispute Resolution | `08-governing-law-dispute-resolution.md` |

## Source map

| Fact needed                                                         | Source in `v1_79`                                                                                                                                                                                                                                                                                                                             | Status                                |
| ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Company particulars (CIN, PAN, GSTIN, address, DPIIT, directors)    | `../20260708/IPG_Proposal_UBI_VSYST.md` §2                                                                                                                                                                                                                                                                                                    | Verified                              |
| Founding story, product description                                 | `../20260708/proposalplan.md`; `dzzlo_oms_app/AI.md`; `dzzlo_oms_api/docs/ARCHITECTURE.md`                                                                                                                                                                                                                                                    | Available                             |
| Traction, volumes, ticket sizes, rails                              | proposal §1, §4; `../problem-statement.md` §1–2                                                                                                                                                                                                                                                                                               | Available — state as expectations     |
| Revenue model (free now; per-GSTIN dealer subscription planned)     | `docs/learning/app-store-economics/`, `docs/learning/company/`                                                                                                                                                                                                                                                                                | Available — state as plan, no figures |
| Merchant structure, fund flow, refunds principle                    | proposal §5; `proposalplan.md` Q3/Q5/Q7                                                                                                                                                                                                                                                                                                       | Agreed                                |
| **Current in-app payment flow**                                     | App: `Customer/NewPayment/index.js`, `Customer/NewPayAck/index.js`, `Dealer/NewVoucher/index.js`, `Common/Payments/`, `Common/_Voucher_/`. API: `models/voc_msts.js` (`pay_mode` cash/cheque/card/fleetcard/neft/rtgs; `pay_status`; `voc_type`; `invs_adj`), `models/month_crdrs.js` (ledger), `models/pay_trns.js`, `api_v3` voucher routes | Read in Step 4                        |
| Legacy Paytm integration                                            | `Customer/NewPayment/Paytm.js`; `api_v1/controllers/Payment/Paytm*`                                                                                                                                                                                                                                                                           | **User to confirm** it is unused      |
| Support / grievance contact                                         | `Common/ContactUs/`, `Common/Help/`; proposal contact line                                                                                                                                                                                                                                                                                    | Grievance officer name from user      |
| Website / policy-page URLs; existing Privacy Policy (store listing) | Not found in repos or vault                                                                                                                                                                                                                                                                                                                   | **User to supply / confirm**          |

---

## 1. About Us — boilerplate

Half a page. Who we are (legal entity, incorporation, registered office, DPIIT) · What we build (DZZLO OMS, one paragraph, stores + web) · Our story (35+ yrs dealership experience, built on the family outlet, founders) · Particulars table (legal name, CIN, date of incorporation, registered office, PAN, GSTIN, DPIIT cert, directors) · Contact.

Open: launch date — June 2021 (proposal) vs Oct 2021 (plan notes).

## 2. Business Model — boilerplate

Half a page, framed as **current state + expectation**.

- What the platform is: vertical SaaS for petrol pump dealers and their credit customers (transport companies). VSYST is the technology layer; dealers sell fuel; VSYST sells no fuel and touches no funds.
- Parties table: Dealer (seller, sub-merchant, future subscriber) · Customer firm (buyer, free) · VSYST (platform, master merchant).
- What is transacted: fuel dispensed at the outlet against a verified order; GST invoice raised in-platform; payment against invoice.
- How VSYST earns — **today: nothing (free, adoption phase). Expected: subscription to dealer companies per GSTIN, billed on the web; users free; no commission on payments.**
- Scale — **current:** 2 dealers, 130+ users, 130+ txns/day ⟨re-confirm⟩. **Expected:** ₹10–20 lakh/dealer/month, growing with dealer count; labelled projection.

## 3. Use Case of the Payment Gateway — boilerplate

Half a page.

- One line: a transport company pays a dealer's invoice for fuel already dispensed, inside the DZZLO app; the invoice closes in the shared ledger at once.
- Payer → payee: customer firm's bank account → dealer's own account (T+1 via Easebuzz). Post-delivery settlement of a credit invoice; no shipping.
- Expected transaction profile table: net banking avg ₹1 lakh (₹5k–₹5L, core) · UPI avg ₹5k (₹1k–₹50k) · cards (supporting). Recurring, firm-to-firm. **All figures = expectations from observed dealer throughput.**
- What it replaces: manual net-banking transfer outside the app + next-morning statement matching.
- Channels: Android, iOS, web. Also requested: verification APIs (bank account, PAN, GSTIN, Aadhaar, RC, DL).

## 4. Payment Flow — boilerplate

One page, written from the code — not from memory.

**A. Current flow (live, no gateway).** Order → delivery → invoice → customer raises a payment voucher in-app (dealer, invoices, amount, pay_mode, bank/cheque, TDS) → customer pays the dealer outside the app → dealer confirms receipt (pay_status → true) → ledger updates, invoice closes, credit limit frees. Short voucher-lifecycle diagram. Note what the app allows on reversal/edit.

**B. Expected flow (with Easebuzz).** Select invoice → amount pre-filled → Pay → API creates gateway request (order id = voucher id) → checkout → webhook to API (`pay_trns`) → voucher auto-confirmed → ledger closes → T+1 settlement to dealer. Failure/pending handling; refund = dealer-initiated → gateway refund → reversal voucher; daily reconciliation against the settlement report. **Labelled as the intended design, not built yet.**

**C. Data held by VSYST:** voucher, invoice, gateway txn id + status. No card/bank credentials.

**D. Legacy:** Paytm WebView code exists in `api_v1` — ⟨confirm⟩ not live.

## 5. Mandatory Policies — highlight (boilerplate)

One table. **Verify against Easebuzz's actual checklist before submission.**

| Policy / page                        | Mandatory?   | Where published                                      | Doc       |
| ------------------------------------ | ------------ | ---------------------------------------------------- | --------- |
| Terms & Conditions                   | Yes          | vsyst.in/⟨terms⟩ + in-app                            | #7        |
| Privacy Policy (DPDP Act 2023)       | Yes          | vsyst.in/⟨privacy⟩ + store listings                  | ⟨exists?⟩ |
| Cancellation & Refund Policy         | Yes          | vsyst.in/⟨refunds⟩                                   | #6        |
| Shipping / Delivery                  | Usually      | clause in #7 — fuel dispensed at outlet, no shipping | #7        |
| Contact Us / About Us                | Yes          | vsyst.in + in-app                                    | #1        |
| Pricing                              | Usually      | vsyst.in/⟨pricing⟩ — "free; subscription planned"    | #2        |
| Governing Law & Dispute Resolution   | Yes (clause) | inside #6, #7                                        | #8        |
| Grievance officer (name, email, SLA) | Yes          | inside #7 + Contact                                  | ⟨user⟩    |

KYC documents on the same checklist (not policies): incorporation certificate, MOA/AOA, board resolution, PAN, GST certificate, cancelled cheque, director KYC, address proof, store listing links, website URL.

## 6. Cancellation & Refund Policy — boilerplate

One page. Principle agreed: refunds are dealer-initiated, processed in DZZLO, executed on Easebuzz rails; VSYST holds no funds and refunds nothing on a dealer's behalf.

Clauses: Scope · Nature of transactions (fuel already dispensed; no shipment) · Order cancellation (what the app allows before dispensing) · Refunds of payments to dealers (raised by dealer; to original instrument within ⟨X⟩ working days) · Failed / pending transactions (auto-reversal; ticket) · Duplicate payments · Chargebacks (ledger as evidence) · Subscription fees (expected; ⟨stance⟩) · How to request · Contact · Governing law (→ #8).

## 7. Terms & Conditions — boilerplate

Two pages, plain English. Clauses: Acceptance · Definitions · Service description (VSYST is a technology provider, not the seller of fuel, not a lender) · Eligibility & registration (business users; OTP; company invite/approval) · Roles of Dealer / Customer / User · Orders, delivery, invoices (delivery at outlet; disputes are between dealer and customer; ledger is the record) · Payments (via RBI-authorised aggregator; VSYST holds no funds) · Platform fees (free today; subscription expected) · Refunds (→ #6) · Ledger & immutability · Credit limits (set by dealer) · Data & privacy (DPDP; no card/bank credentials stored) · IP · Prohibited use · Suspension & termination (Settings → Delete Account) · Disclaimer & limitation of liability · Indemnity · Third-party services · Changes · Governing law (→ #8) · Grievance officer & contact.

## 8. Governing Law & Dispute Resolution — boilerplate

Half a page; reused inside #6 and #7. Governing law: India (IT Act 2000, DPDP Act 2023; PSS Act 2007 for the aggregator) · Jurisdiction: courts at ⟨Raipur, Chhattisgarh⟩ · Ladder: grievance officer (ack ⟨48 h⟩, resolve ⟨30 days⟩) → negotiation ⟨30 days⟩ → arbitration, Arbitration and Conciliation Act 1996, sole arbitrator, seat ⟨Raipur⟩, English · Dealer–customer disputes are between them; VSYST supplies ledger records · Payment grievances escalate to the aggregator, then RBI Integrated Ombudsman where applicable.

---

## Open questions for the user

1. Easebuzz's actual checklist — paste it so §5 matches exactly.
2. Where will policy pages live (vsyst.in? a DZZLO domain?) — exact URLs.
3. Does a Privacy Policy already exist for the store listings?
4. Launch date: June 2021 or Oct 2021?
5. Traction figures as of Aug 2026.
6. Paytm code in `api_v1` — dead? OK to state "no gateway live today"?
7. Grievance officer: name, email, SLA.
8. Refund window (days); subscription refund stance.
9. Jurisdiction/seat Raipur? Sole arbitrator, ad hoc?

## Inbox (raw points from user — unsorted)

- 2026-08-21: _"keep the document data short. we are still pre-revenue so we are just showing our assumptions and expectations"_ → became the Writing rule at the top.
