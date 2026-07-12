# IPG Proposal Plan — Working File

Staging area for the bank proposal (UBI → Internet Payment Gateway, likely via Easebuzz). Raw points go under "Inbox", then get grouped topic-wise, then we finalize the outline. See CLAUDE.md for the full workflow.

## Status

- [~] Step 1: Content gathered / business understood — **in progress, user providing more content**
- [ ] Step 2: Points grouped topic-wise
- [ ] Step 3: Document structure agreed
- [ ] Step 4: Final 3–4 page document drafted

## Inbox (raw points from user — unsorted)

**2026-07-07 (message 1):**
- Proposal is for a **Union Bank of India ↔ VSYST Technologies collaboration**.
- Petrol pump dealers have to manage credit for their business. By using our application they see:
  - Faster fund rolling
  - Decreased credit cycle
  - Reduced reminders to their customers
  - Least reconciliations
  - Lesser fraud
  - Lesser debt

**2026-07-07 (message 2):**
- UBI gets an **early-bird benefit** by enrolling dealers as merchants that can accept payments.
- Petrol pump payment flows could be heavy once significant conversion is achieved.
- Market size: out of ~1,00,000 petrol pumps in India, **~3,600 are high-sale petrol pumps**.
- These 3,600 account for the **majority of diesel sales** — mostly located on highways.
- These 3,600 have **50–60% of transactions through loyalty programs** run by oil marketing companies (OMCs).
- We promise: actual correct data, smooth transactions between petrol pump and their customers.
- We provide a **real order management system** replacing the **chat apps currently used** for transactions.

**2026-07-07 (message 3):**
- Confirmed: remaining 40–50% is our target flow — **plus the part of payments that loyalty programs could not handle**.
- We provide a **shared ledger between petrol pump and their customer, similar to a bank's**.
- **Data once escalated cannot be deleted** — ensures authenticity (immutable audit trail).
- We promote **bill-to-bill payments, not lump-sum payments** which lead to long reconciliations.
- We **filter paid and unpaid invoices right in the app** for better clarity.
- **Pending bills caused bad debt** (the core problem).
- DZZLO OMS introduces **amount-wise and period-wise credit limits per individual customer** to manage credit for the business.
- **Many further advancements planned once we get traction by automating payments through the IPG.**

**2026-07-07 (message 4 — answers to open questions):**
- Q1 (legal/KYC): use **dummy placeholder data**; user will substitute real data afterwards.
- Q2 (financials): no financial traction yet — user asks if we can drop financials. _(Claude recommendation: reframe as "Current Traction & Projected Volumes" rather than drop — see notes below.)_
- Q3 (merchant structure): **VSYST = merchant (master/platform), petrol pumps = sub-merchants.** Dealer payments settle **directly to each dealer's own linked bank account, never to VSYST**.
- Q5 (roles): **UBI = collaborating bank; Easebuzz = payment gateway/aggregator partnered with the bank; settlement at UBI account.**
- Q6 → becomes a **question TO the bank**: can a dealer's existing account connect to this service, or must a new account be created?
- Q7 (refunds/chargebacks): all refunds and chargebacks are **initiated by the dealer**, processed in the DZZLO OMS platform and the Easebuzz payment gateway.
- Q8 (compliance pages): VSYST charges nothing for web/app, so user believes not needed — asked Claude to advise on compliance docs for petrol pump dealers on the platform. _(Claude: still needed — see notes below.)_
- Q9 (traction): **130+ users, 2 dealers, 130+ daily transactions.**
- Q4 (volumes/ticket size) and Q10 (security) — user will answer later.

**2026-07-07 (message 5 — Q4 & Q10 answers + two asks to UBI):**
- Q4 volumes: **monthly volume per dealer ₹10–20 lakh, potential ₹1 crore/month per dealer** (excluding loyalty-program transactions).
- Ticket sizes: **UPI avg ₹5,000 (range ₹1,000–₹50,000); bank/online payments avg ₹1 lakh (range ₹5,000–₹5,00,000)**.
- Q10 trust/security: dealers today are **afraid to share bank details** with anyone due to online fraud → owning a payment gateway lets them **freely ask anyone to pay** without exposing account details.
- Customers also fear transferring to a typed account number — mistyping risk, "did the amount reach the correct account?" — critical because transactions are **large and regular**.
- The payment gateway solves both fears (no raw account numbers, payment against invoice, instant confirmation).
- User asks: **frame the ask to UBI for guaranteeing/endorsing Easebuzz authenticity** (bank's name behind the gateway).
- User asks: **request UBI's "U-Collect" feature** → verified: actual product name is **"Uni e-Collect"** (UBI Cash Management Services) — digital collections via RTGS/NEFT/IMPS/UPI pooled at CMS Hub using **virtual account numbers** to keep beneficiary details private.

_(more content expected from user)_

## Topic-wise Grouping

_Facts below sourced from the user's Obsidian vault (marketing notes, some dated 2022–2024) — verify current figures with user before using in the final document._

### Business Overview
- **VSYST Technologies Pvt. Ltd.** — started 2021, based in Raipur, Chhattisgarh (office at family-owned petrol pump; Bangalore office planned).
- Founded by siblings Shikhar Chawra (computer engineer, builds the Android/iOS apps) and Shikha Chawra, both left MNC jobs; 3 directors total.
- Business idea from father Paresh Chawra — 30+ years of experience as a petrol pump (RO) dealer; product built and proven first on the family's own pump.
- **Recognized by Startup India** (company started 2021, registered for Startup India Feb 2022).
- Bootstrapped; was in process of applying for ₹20 lakh Startup India Seed Fund grant.
- Vision: **e-ERP** — extended ERP with 12 planned modules (OMS, HR, Accounting, LRMS, Finance, Insurance, etc.). **Module #9 is "Internet Payment Gateway (PGTW)"** — the IPG being requested is a planned, integral part of the product roadmap.

### Products / Services Sold Online (what the IPG is for)
- **DZZLO OMS** — a credit/order management app for **petrol pump (RO) dealers and transport companies** (their credit customers).
- Live on Google Play Store & Apple App Store since Oct 2021.
- Handles: ordering (purchase orders), invoicing, GST/TDS/TCS taxation, party ledgers, payment acknowledgment, reconciliation, vehicle & driver management, real-time reports.
- Dealer's pain: fraud and credit management. App gives verified customers/vehicles/orders, accurate timely bills, automatic common ledger, no suspense accounts.
- **IPG role in product**: "Payment Gateway eliminates & automates approvals" — customer (transporter) pays dealer through the app; future roadmap: 2-way payment (customer→dealer, dealer→anyone). Direct bank payment was a stated dealer-association demand.
- **Roadmap hinges on the IPG**: many further advancements are planned once traction is achieved by automating payments through the payment gateway — the IPG is the unlock for the next product phase.
- Revenue model (from pitch notes, to confirm): free tier for logistics companies; subscription ~₹3,000/month; API monetization ~₹1,000/month per 1 lakh calls.

### Value Proposition (user's core pitch for the collaboration)

**For dealers (merchants):**
- Faster fund rolling for dealers
- Decreased credit cycle
- Reduced payment reminders to customers
- Least/no reconciliations (single shared ledger between dealer & customer)
- Lesser fraud (verified companies, vehicles, drivers, orders)
- Lesser debt / healthy credit limits
- A real order management system replacing chat apps (WhatsApp etc.) currently used to run transactions
- Actual correct data; smooth transactions between petrol pump and customers

**For UBI (the bank):**
- **Early-bird advantage**: first bank to enroll petrol pump dealers as payment-accepting merchants through DZZLO
- Heavy payment flows once significant dealer conversion is achieved (fuel is high-value, high-frequency, recurring spend)

### Market Opportunity (for the UBI-benefit section)
- ~1,00,000 petrol pumps in India; **~3,600 are high-sale pumps**, mostly on highways.
- These 3,600 carry the **majority of national diesel sales**.
- 50–60% of transactions at these 3,600 pumps already flow through **OMC loyalty programs** (fleet cards etc.) — i.e., the segment is proven to adopt cashless/programmatic payment when it works.
- **Target flow for the IPG (confirmed by user):** the remaining 40–50% (credit sales settled via chat + bank transfer today) **plus the part of payments that loyalty programs could not handle**.

### Current Traction & Projected Volumes (replaces "Financials")
- **Live traction (2026): 130+ users, 2 dealers onboarded, 130+ transactions daily** — real in-app data, verifiable.
- VSYST is deliberately pre-revenue: app is free to drive adoption; monetization planned via subscription (~₹3,000/mo) and API access later.
- Framing for the bank: the relevant "financials" are the **transaction throughput** the gateway will carry (dealer turnover), not VSYST's own P&L.
- **Volume per dealer: ₹10–20 lakh/month today, potential ₹1 crore/month** (excluding loyalty-program transactions).
- **Ticket sizes:**
  | Mode | Average | Range |
  |---|---|---|
  | UPI | ₹5,000 | ₹1,000 – ₹50,000 |
  | Bank/online (NEFT/RTGS/net-banking) | ₹1,00,000 | ₹5,000 – ₹5,00,000 |
- Scale math for proposal: even a modest slice of the 3,600 high-sale pumps at ₹10–20 lakh/month each is a substantial, recurring collection flow for UBI.

### Compliance & Registrations
- Startup India / DPIIT recognition (per notes).
- GST-compatible billing built into product; MSME registration discussed in notes for customers.
- Company KYC (CIN, GST, PAN, registered address): **dummy placeholders in draft; user substitutes real data**.
- **Platform compliance docs needed even though app is free** (PA/aggregator onboarding norms):
  - VSYST/DZZLO level: Terms of Service, Privacy Policy (DPDP Act 2023), Refund & Cancellation Policy (describing dealer-initiated flow), grievance/support contact.
  - Per-dealer (sub-merchant KYC, collected via platform): business PAN, GST, bank account proof, address proof, dealership/trade license, signed sub-merchant agreement.

### Risk Mitigation & Credit Discipline (product features banks will like)
- **Shared ledger** between petrol pump and customer — "similar to a bank's"; one source of truth for both sides.
- **Immutability**: data once escalated cannot be deleted — authentic, audit-ready records.
- **Bill-to-bill payments** promoted over lump-sum payments (lump-sum → long reconciliations; bill-to-bill → clean settlement per invoice).
- **Paid/unpaid invoice filtering** built into the app — unpaid invoices visible by default; pending bills are the root cause of bad debt.
- **Credit limits per individual customer — amount-wise AND period-wise** — so dealers extend credit within controlled exposure.
- Traceability: every order tied to company identity, order-manager identity, driver phone number, verified vehicle.
- MSME 45-day payment claims support, TDS/TCS handling.
- **Refunds & chargebacks: initiated by the dealer, processed inside DZZLO OMS, executed via the Easebuzz gateway** — single traceable trail from invoice → payment → refund.

### Technical Readiness & Payment Architecture
- Mobile apps live on both stores since Oct 2021; built in-house (founder is the developer).
- **Merchant structure: VSYST as master merchant / platform; each petrol pump dealer onboarded as a sub-merchant.**
- **Fund flow: customer pays in-app → Easebuzz (RBI-authorized payment aggregator, partnered with UBI) collects into its escrow/nodal account → settles DIRECTLY into each dealer's linked bank account. VSYST never receives, holds, or touches customer funds.**
- Settlement account relationship at UBI.
- Refund/chargeback flow: dealer-initiated in DZZLO OMS → executed through Easebuzz gateway rails.
- _(pending from user — Q10: security posture, data protection, fraud controls)_

### Security & Trust (Q10 — the "why a gateway at all" narrative)
- **Dealer-side fear today**: dealers avoid sharing bank account details with anyone due to online fraud. With their own payment gateway, a dealer can freely ask any customer to pay — account details are never exposed.
- **Customer-side fear today**: paying to a typed account number risks mistyped digits and "did it reach the right account?" anxiety — acute because these payments are **large (up to ₹5 lakh) and regular**.
- **Gateway resolves both**: payment is made against an invoice inside the app, no raw account numbers change hands, both sides get instant confirmation, and every rupee is traceable invoice→payment.
- Technical security (PCI-DSS, encryption, fund handling) rides on Easebuzz's RBI authorisation — VSYST holds no card/bank credentials and no customer funds.

### Requests to UBI (asks section of the proposal)
1. **Endorse the Easebuzz partnership (authenticity guarantee).** Request UBI to formally confirm in writing that Easebuzz is its authorised payment-aggregator partner for this program, and permit dealer-facing onboarding material to carry UBI's name (e.g., "Payments via Easebuzz, in partnership with Union Bank of India"). Rationale to state: dealer adoption hinges on trust — dealers who refuse to share bank details will accept the gateway only when the bank's name visibly stands behind it. Optionally: joint dealer-onboarding sessions with UBI branch officials.
2. **Extend Uni e-Collect to the platform** (user said "U-Collect"; verified product name: **Uni e-Collect**, under UBI Cash Management Services). For high-value settlements (avg ₹1 lakh, up to ₹5 lakh) moving via RTGS/NEFT/IMPS/UPI: each dealer (or dealer–customer pair) gets a **virtual account number**, so customers never type a real account number; collections pool at UBI's CMS hub and auto-reconcile against DZZLO invoices via MIS/API. Two-rail architecture: **Easebuzz gateway for UPI/smaller tickets; Uni e-Collect virtual accounts for large bank transfers.**
3. **Account linkage question**: can a dealer's **existing current account** (at UBI or elsewhere) be linked for sub-merchant settlement, or does UBI require opening a **new dedicated account**? (Proposal can offer: dealers open/shift current accounts to UBI — a CASA win for the bank.)

### Banking Relationship with UBI
- _(pending from user — existing UBI accounts (company/pump), history, why UBI, which branch)_

### Other Relationships / Credibility Signals
- Engagement with IOCL (meeting Jan 2024, integration discussions for dealer/customer data and fleet-card problems).
- Discussions referenced with dealer associations (RPDA) and Ministry of Road Transport & Highways.

## Open Questions a Bank Would Ask — status

1. ~~Legal/KYC~~ — **ANSWERED**: use dummy placeholders (CIN, GST, address); user substitutes real values later.
2. ~~Financials~~ — **ANSWERED**: no revenue traction; reframed as "Current Traction & Projected Volumes" (don't drop — bank needs volume story).
3. ~~Merchant of record~~ — **ANSWERED**: VSYST = master merchant/platform, dealers = sub-merchants, settlement direct to dealer's own account (marketplace model; funds never touch VSYST).
4. ~~Expected volumes~~ — **ANSWERED**: ₹10–20 lakh/month per dealer (potential ₹1 cr, ex-loyalty); UPI avg ₹5k (1k–50k); bank payments avg ₹1 lakh (5k–5 lakh).
5. ~~Easebuzz vs UBI roles~~ — **ANSWERED**: UBI = partner bank, Easebuzz = PG/aggregator partnered with bank, settlement at UBI.
6. ~~UBI relationship~~ — **CONVERTED to a question for UBI**: existing account linkable vs. new account required.
7. ~~Refunds/chargebacks~~ — **ANSWERED**: dealer-initiated, processed in DZZLO OMS + Easebuzz.
8. ~~Compliance pages~~ — **ANSWERED + Claude advice**: platform-level T&C, privacy policy, refund policy still required by PA norms even though app is free; plus sub-merchant KYC per dealer. See "Compliance & Registrations".
9. ~~Traction~~ — **ANSWERED**: 130+ users, 2 dealers, 130+ daily transactions.
10. ~~Security~~ — **ANSWERED (reframed as trust story)**: gateway removes both dealer fear (exposing bank details) and customer fear (mistyped account transfers); technical security rides on Easebuzz's RBI authorisation. See "Security & Trust" section.

**All 10 questions answered. Remaining placeholders: company KYC dummy data to be swapped with real values by user.**

## Agreed Document Outline

_(to be filled in Step 3)_
