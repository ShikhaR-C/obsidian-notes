# Proposal for Internet Payment Gateway Enablement

**VSYST Technologies Pvt. Ltd. — in partnership with Union Bank of India, via Easebuzz**

|             |                                                                                                                                                                                                                  |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **To**      | The Branch Manager / Digital Banking Department, Union Bank of India, ⟨Branch, City⟩                                                                                                                             |
| **From**    | VSYST Technologies Pvt. Ltd., A-2/11, Udaya Society, Tatibandh, Raipur, Chhattisgarh                                                                                                                             |
| **Date**    | 08 July 2026                                                                                                                                                                                                     |
| **Subject** | Request for Internet Payment Gateway enablement for the DZZLO platform — VSYST Technologies as master merchant with petrol pump dealers as sub-merchants, through the Bank's payment-aggregator partner Easebuzz |

---

## 1. Executive Summary

VSYST Technologies Pvt. Ltd. is a DPIIT (Startup India)–recognised technology company that operates **DZZLO OMS**, a credit and order management platform for petrol pump dealers and their bulk-fuel customers (transport companies). The platform is live on the Google Play Store and Apple App Store since June 2021 and currently processes **130+ transactions daily across 130+ users and 2 dealer outlets**.

We request Union Bank of India to enable an **Internet Payment Gateway** for the DZZLO platform through the Bank's payment-aggregator partner **Easebuzz**, with VSYST as the master merchant and each petrol pump dealer onboarded as an individually KYC-verified **sub-merchant**. All settlements flow **directly to each dealer's own bank account**; VSYST does not receive, hold, or route customer funds at any point.

| At a glance               |                                                                                                |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| Request                   | IPG enablement via UBI–Easebuzz (marketplace / sub-merchant model)                             |
| Merchant structure        | VSYST = master merchant (technology layer only); dealers = KYC-verified sub-merchants          |
| Fund custody & settlement | Easebuzz escrow under RBI PA authorisation → direct settlement to each dealer's account at UBI |
| Live traction             | 130+ users, 2 dealers, 130+ transactions daily                                                 |
| Volume per dealer         | ₹10–20 lakh/month today; potential ₹1 crore/month excluding OMC loyalty flows                  |

## 2. Company Profile

| Particular            | Detail                                                          |
| --------------------- | --------------------------------------------------------------- |
| Legal name            | VSYST Technologies Private Limited                              |
| CIN                   | U7200CT2021PTC012283                                            |
| Date of incorporation | 21/10/2021                                                      |
| Registered office     | A-2/11, Udaya Society, Tatibandh, Raipur, Chhattisgarh          |
| PAN / GSTIN           | AAICV3528R / 22AAICV3528R1ZT                                    |
| Recognition           | DPIIT Startup India recognised, ⟨Feb 2022, Cert. No. DIPP97734⟩ |
| Directors             | PARESH CHAWRA, SHIKHAR CHAWRA, SHIKHA CHAWRA                    |
| Product               | DZZLO OMS — Android & iOS, live since June 2021                 |
| Contact               | Paresh Chawra, Director · +919425208228 · info@vsyst.in         |

The company is promoted by a family with **30+ years of petroleum retail dealership experience**. DZZLO was built in-house and proven first at the family-operated retail outlet before being offered to other dealers — the product encodes how fuel-credit business actually runs on the ground.

## 3. The Business and the Problem We Solve

High-sale petrol pumps sell diesel on credit to transport companies. Today this business runs on **chat apps and manual ledgers**: orders arrive as messages, invoices are keyed by hand on both sides, customers pay in unallocated lump sums, and accountants spend days reconciling. The predictable results are disputed entries, unverified vehicles and drivers at the nozzle, pending bills, and ultimately **bad debt**.

DZZLO OMS replaces this with a genuine order-management system. Every order carries a verified company, order manager, driver, and vehicle. Invoices are GST-compliant, and TDS is handled in-platform. Dealer and customer share a **single common ledger — maintained like a bank statement** — and records once escalated **cannot be deleted**, so the books are authentic by construction. The platform enforces **bill-to-bill payment matching** rather than lump-sum payments, shows unpaid invoices by default, and lets dealers set **credit limits per customer, by amount and by period**, keeping exposure controlled.

DZZLO is deliberately **free at this stage** to drive dealer adoption; subscription and API-based monetisation is planned once payment automation is live. VSYST is pre-revenue by design — the commercial substance of this proposal is the **transaction throughput the gateway will carry**, not VSYST's own turnover.

One leg of the loop remains outside the platform: **payment itself**. An Internet Payment Gateway is already module #9 of our published e-ERP product roadmap, and our next phase of product advancements is gated on payment automation. This proposal closes that loop.

## 4. The Opportunity for Union Bank of India

India has roughly **1,00,000 retail fuel outlets. About 3,600 are high-sale outlets**, largely on highways, and together they account for the majority of national diesel sales. At these outlets, **50–60% of transaction value already flows through oil-marketing-company loyalty and fleet-card programs** — proof that this segment adopts digital payment rails when they work. Our target is the **remaining 40–50%**: credit sales settled today by chat-coordinated bank transfers — plus the payments the loyalty programs cannot handle.

| Volume & ticket profile               |                                                            |
| ------------------------------------- | ---------------------------------------------------------- |
| Current volume per dealer             | ₹10–20 lakh per month                                      |
| Potential per dealer                  | up to ₹1 crore per month (excluding loyalty-program flows) |
| UPI ticket size                       | avg ₹5,000 (range ₹1,000 – ₹50,000)                        |
| Net-banking / NEFT / RTGS ticket size | avg ₹1,00,000 (range ₹5,000 – ₹5,00,000)                   |

For the Bank, this is an **early-bird position** on an underbanked, high-value merchant segment. Each dealer enrolled as a UBI merchant brings their entire customer base onto the Bank's payment rails; settlement accounts held with UBI add current-account balances and float; and volumes compound as outlet coverage grows toward the 3,600 high-sale pumps.

## 5. Payment Architecture and Fund Flow

```
Customer (transporter) pays a DZZLO invoice in-app
        → Easebuzz collects into its escrow account (RBI-authorised payment aggregator, UBI partner)
        → T+1 split settlement DIRECTLY into the respective dealer's current account (proposed: at UBI)
```

- **VSYST never receives, holds, or routes customer funds.** It is purely the technology layer; fund custody sits entirely within Easebuzz's RBI payment-aggregator authorisation. There is no commingling of platform and merchant funds at any point.
- **Refunds and chargebacks** are initiated only by the dealer, processed inside DZZLO OMS, and executed on Easebuzz rails — an unbroken, auditable trail from invoice to payment to refund. Because payments are made against delivered fuel on verified orders, chargeback exposure is inherently low, and any dispute is resolved against the immutable shared ledger.

_(to check)_

- **Two collection rails.** (a) Gateway checkout — UPI, cards, net-banking — for regular tickets; (b) **Uni e-Collect virtual account numbers** for high-value RTGS/NEFT transfers, so the customer never types a real account number and every credit auto-reconciles to its invoice via MIS/API integration.

## 6. Risk Management and Compliance

**The trust problem this gateway solves.** Dealers today hesitate to circulate their bank account details owing to online-fraud risk; customers hesitate to push large transfers to a typed account number — one mistyped digit on a ₹5 lakh RTGS is a serious incident, and these payments recur weekly. The gateway removes both fears: no raw account details are exchanged, payment is made against a specific invoice, and both sides receive instant confirmation.

**Transaction-risk controls built into the platform:**

| Control                                                     | Effect                                            |
| ----------------------------------------------------------- | ------------------------------------------------- |
| Verified counterparties (company, manager, driver, vehicle) | No anonymous or repudiated orders                 |
| Per-customer credit limits — amount-wise and period-wise    | Capped, controlled exposure                       |
| Bill-to-bill settlement                                     | No unallocated lump sums; clean audit trail       |
| Immutable escalated records                                 | Books cannot be rewritten                         |
| Unpaid invoices visible by default                          | Pending dues acted on before they become bad debt |
| GST / TDS-compliant documentation                           | Tax-clean transactions end to end                 |

_(to check)_
**Onboarding and regulatory discipline.** Every dealer will be KYC-verified before activation as a sub-merchant: business PAN, GSTIN, bank account proof, address proof, dealership licence, and a signed sub-merchant agreement. The platform will publish Terms of Service, a Privacy Policy aligned to the DPDP Act 2023, a Refund & Cancellation Policy, and a named grievance contact. Card-data security (PCI-DSS) and fund custody remain within Easebuzz's RBI-authorised scope; VSYST stores no card or banking credentials.

## 7. Requests to Union Bank of India

1. **Enable the Internet Payment Gateway** for the DZZLO platform — VSYST as master merchant, petrol pump dealers as KYC-verified sub-merchants — through the Bank's payment-aggregator partner Easebuzz, with settlement routed to dealer accounts at UBI.
2. **Confirm the Bank–Easebuzz partnership in writing** for this program, and permit dealer-facing onboarding material to carry the Bank's name (e.g., _"Payments via Easebuzz, in partnership with Union Bank of India"_). Dealer adoption depends on the Bank's name visibly standing behind the gateway; we would also welcome joint dealer-onboarding sessions with branch officials.
3. **Extend Uni e-Collect** to the platform: virtual account numbers per dealer for high-value collections, with MIS/API integration so receipts auto-reconcile into DZZLO.
4. **Clarify account linkage**: whether dealers' existing current accounts can be linked for sub-merchant settlement, or dedicated accounts with UBI are required. We are open to encouraging dealers to open or shift current accounts to UBI as part of onboarding.

## 8. Rollout Plan and Closing

| Phase                    | Scope                                                                               | Outcome for the Bank                  |
| ------------------------ | ----------------------------------------------------------------------------------- | ------------------------------------- |
| 1 — Pilot (Months 0–3)   | 2 live dealers, 130+ users, existing 130+ daily transactions moved onto the gateway | End-to-end validation at minimal risk |
| 2 — Region (Months 3–12) | Raipur and Chhattisgarh dealer network                                              | Repeatable onboarding playbook        |
| 3 — Scale (Year 1+)      | High-sale highway outlets nationally (~3,600 target segment)                        | Compounding merchant and CASA growth  |

We request the Bank's approval to commence the Phase-1 pilot. We would be glad to demonstrate the live platform and our current transaction flows at the Bank's convenience.

For **VSYST Technologies Pvt. Ltd.**

Paresh Chawra, Director
+919425208228 · info@vsyst.in · vsyst.in
