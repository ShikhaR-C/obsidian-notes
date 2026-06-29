# 12. CBDC Integration Guide — How to Integrate Digital Rupee in Your System

## Can We Integrate CBDC Into Our System?

**Yes, but with constraints.** The Digital Rupee is still in pilot phase, so integration is possible through specific channels — not via a general-purpose open API from the RBI.

---

## Integration Paths (5 Options)

### Path 1: Via UPI Interoperability (Easiest — Zero Effort)

**If you already accept UPI payments, you already accept CBDC indirectly.**

- RBI mandated **CBDC-UPI interoperability** — any UPI QR code can accept Digital Rupee payments.
- Customers scan your existing UPI QR code using their Digital Rupee wallet app.
- **No code changes, no new integration, no new QR codes needed.**
- Settlement: Payment arrives as standard UPI credit (in INR) to your bank account.
- Works with any gateway: Razorpay, PayU, Cashfree, etc.

**Limitation:** You receive INR via UPI, not CBDC tokens. The merchant doesn't technically "hold" CBDC unless they also have a CBDC wallet.

---

### Path 2: Via CCAvenue (First Payment Aggregator to Support CBDC)

**CCAvenue became India's first payment aggregator to process CBDC transactions** (January 2023).

- **Zero additional code required** for existing CCAvenue merchants.
- CBDC appears as an automatic payment option on the checkout page.
- Customer sees "CBDC" option → QR code generated → customer scans with bank's Digital Rupee app.
- Phase 1 banks: SBI, ICICI, Yes Bank, IDFC First Bank.
- Phase 2 banks: Bank of Baroda, Union Bank, HDFC, Kotak Mahindra.

**How to enable:**
1. Be an existing CCAvenue merchant (or sign up).
2. CBDC option is auto-enabled on your checkout page.
3. No integration work needed.

**Reference:** https://www.ccavenue.com/central-bank-digital-currency

---

### Path 3: Via HDFC Bank SmartGateway

**HDFC Bank integrated CBDC into its SmartGateway** merchant payment platform (January 2026).

- CBDC payment mode integrated alongside UPI, cards, and net banking.
- **Zero transaction cost** for CBDC payments.
- No core infrastructure changes needed for existing SmartGateway merchants.

**How to enable:**
1. Be an existing HDFC SmartGateway merchant (or onboard).
2. CBDC appears as a payment option automatically.

**Reference:** https://smartgateway.hdfcbank.com

---

### Path 4: Via Bank's Direct Merchant Onboarding

Contact your participating bank directly for CBDC merchant onboarding:

1. Contact your bank's branch or CBDC team (e.g., cbdc@sbi.co.in for SBI).
2. Bank onboards you and confirms via SMS/email.
3. Download the bank's **CBDC Merchant App** (Play Store / App Store).
4. Generate/download a CBDC QR code, display at premises.
5. Receive SMS alerts for all CBDC transactions.
6. End of day: Digital rupees auto-converted to INR and credited to your linked bank account.

**Requirements:**
- Current account or cash credit account with a participating bank.
- Standard bank KYC (no separate CBDC KYC).
- Located in a pilot city (now 13+ cities, expanding).

---

### Path 5: Via RBI CBDC Retail Sandbox (For Fintechs & Developers)

**Launched: October 8, 2025** at Global Fintech Fest.

- Fintechs can join **directly or through partner banks**.
- Provides access to: **APIs, digital wallets, and smart contract frameworks**.
- Build prototypes and test in a secure simulated environment.
- Supports experimentation with: retail payments, cross-border remittances, programmable payments, tokenized loyalty systems.

**How to access:**
1. Apply through **RBI FinTech Portal**: https://fintech.rbi.org.in
2. OR partner with one of the 19 participating banks.

**Reference:** https://inc42.com/buzz/rbi-launches-cbdc-retail-sandbox-for-fintech-players/

---

## Who Can Integrate?

| Entity Type | Can Integrate? | How |
|------------|----------------|-----|
| Any UPI-accepting merchant | Yes (indirectly) | UPI interoperability — no action needed |
| CCAvenue merchants | Yes | Auto-enabled on checkout |
| HDFC SmartGateway merchants | Yes | Auto-enabled on gateway |
| Pilot bank merchants | Yes | Via bank's merchant app/QR |
| Fintech companies | Yes (via sandbox) | RBI CBDC Retail Sandbox (Oct 2025) |
| Non-bank payment apps | Yes (with RBI approval) | Must partner with sponsor bank (e.g., CRED with Yes Bank) |
| General developers/startups | Limited | Must go through sandbox or partner with participating bank |

---

## Payment Gateway CBDC Support Status

| Payment Gateway | Direct CBDC Support | Indirect (via UPI) |
|----------------|--------------------|--------------------|
| **CCAvenue** | **YES** — First PA in India | Yes |
| **HDFC SmartGateway** | **YES** — Integrated Jan 2026 | Yes |
| **Razorpay** | No direct support | Yes (UPI interop) |
| **PayU** | No direct support | Yes (UPI interop) |
| **Cashfree** | No direct support | Yes (UPI interop) |
| **Paytm** | No direct support | Yes (UPI interop) |
| **PayAid** | Claims CBDC support (API + SDKs) | Yes |

**Key insight:** If you use Razorpay/PayU/Cashfree for UPI, your customers can already pay with CBDC wallets — you just won't see it labeled as "CBDC" in your settlement.

---

## Non-Bank Wallet Integration (New — 2025)

Since April 2024, RBI expanded eligibility to non-banking entities:

- **CRED** — launched e-Rupee wallet (Jan 2025) via Yes Bank partnership.
- **MobiKwik** — launched e-Rupee wallet (Jan 2025) via Yes Bank partnership.
- Non-bank wallets have stricter limits: ₹10,000 per transfer, ₹50,000 daily, ₹1 lakh wallet cap.

---

## Developer Resources

### Official Resources

| Resource | URL |
|----------|-----|
| RBI FAQ on Digital Rupee | https://www.rbi.org.in/commonman/English/scripts/FAQs.aspx?Id=3686 |
| Indian Banks Association CBDC Hub | https://www.iba.org.in/cbdc/index.html |
| RBI FinTech Portal (Sandbox) | https://fintech.rbi.org.in |
| CCAvenue CBDC Page | https://www.ccavenue.com/central-bank-digital-currency |
| HDFC SmartGateway Docs | https://smartgateway.hdfcbank.com |

### Bank Contact for CBDC Onboarding

| Bank | Contact |
|------|---------|
| SBI | cbdc@sbi.co.in |
| HDFC Bank | Via SmartGateway portal |
| Others | Contact home branch or digital banking team |

### Third-Party Developer Tools

| Provider | Offering |
|----------|----------|
| PayAid | Claims CBDC orchestration API with SDKs (JavaScript, Python, PHP) |
| | https://payaidpayments.com/api-developer-kits/ |

### Important: No Open Public API from RBI
There is **no publicly documented open REST/GraphQL API from the RBI** that any developer can sign up for and call directly. All programmatic access is mediated through:
1. Participating banks' own systems
2. RBI CBDC Retail Sandbox (application-based)
3. Payment aggregators (CCAvenue)
4. Payment orchestrators (PayAid)

---

## Current Limitations for Integration

| Limitation | Details |
|-----------|---------|
| **No Open API** | Unlike UPI (well-documented NPCI APIs), no open CBDC API exists |
| **Bank Dependency** | All integration requires a participating bank — no bank-agnostic path |
| **Transaction Limits** | ₹50,000 daily / ₹1 lakh wallet cap limits high-value use |
| **No Programmatic Wallet Creation** | Cannot create CBDC wallets for users via API |
| **Limited PA Support** | Only CCAvenue and HDFC SmartGateway have explicit CBDC support |
| **Geographic Restrictions** | Pilot in 13+ cities, not nationwide |
| **Low User Adoption** | ~7 million users — tiny fraction of potential customer base |
| **Programmable Features Nascent** | Purpose-bound / time-bound payments in early testing only |
| **Settlement Complexity** | UPI interop payments settle as regular UPI if merchant lacks CBDC wallet |

---

## Decision Matrix: What Should You Do Today?

| Your Situation | Recommendation |
|---------------|----------------|
| Already accept UPI | **Do nothing** — CBDC customers can already pay you |
| Use CCAvenue | **Check your checkout** — CBDC option may already be live |
| Want explicit CBDC branding | **Integrate CCAvenue** or **HDFC SmartGateway** |
| Building fintech product | **Apply to RBI CBDC Retail Sandbox** |
| Need full programmatic control | **Wait** — no open API available yet |
| Want B2B/high-value CBDC | **Not feasible** — retail CBDC caps are too low |

---

*Sources: CCAvenue, HDFC Bank SmartGateway, RBI FinTech Portal, Inc42, Business Standard, Atlantic Council CBDC Tracker*
