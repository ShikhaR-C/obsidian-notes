# 13. Requirements Checklist — Everything Needed to Use/Integrate CBDC

## For Individual Users (Retail e-₹)

### Mandatory Requirements
- [ ] Indian citizen or resident
- [ ] Age 18+ (bank account eligibility)
- [ ] Bank account at a participating bank (SBI, ICICI, HDFC, Yes Bank, Kotak, etc.)
- [ ] Smartphone (Android or iOS)
- [ ] Registered mobile number linked to bank account
- [ ] Completed bank KYC (Aadhaar + PAN)

### Process
1. Download bank's Digital Rupee wallet app (or CRED/MobiKwik for non-bank wallets)
2. Register with mobile number → OTP verification
3. Link bank account
4. Set wallet PIN
5. Load funds from bank account

### Limits (Individual)

| Wallet Type | Holding Limit | Per-Transaction | Daily Limit |
|------------|---------------|-----------------|-------------|
| Full KYC (bank wallet) | ₹2,00,000 | ₹2,00,000 | ₹2,00,000 |
| Basic KYC (bank wallet) | ₹1,00,000 | ₹50,000 | Bank-defined |
| Non-bank wallet (CRED/MobiKwik) | ₹1,00,000 | ₹10,000 | ₹50,000 (or 20 transfers) |

---

## For Merchants (Accepting CBDC)

### Mandatory Requirements
- [ ] Registered business entity
- [ ] Current account or cash credit account with a participating bank
- [ ] Standard bank KYC completed
- [ ] Located in a pilot city (13+ cities, expanding)
- [ ] Android or iOS device for merchant app

### Recommended (Not Mandatory)
- [ ] GST registration (required for payment gateway onboarding, not specifically for CBDC)
- [ ] PAN card for business

### Onboarding Process
1. Contact participating bank's branch or CBDC team
2. Submit merchant application
3. Bank verifies and onboards
4. Download CBDC Merchant App
5. Generate CBDC QR code
6. Display at premises
7. Start accepting payments

### Alternative: Use Existing UPI
- If you already accept UPI, CBDC customers can already pay you.
- No additional setup required.

---

## For Online Businesses (E-Commerce)

### Option A: CCAvenue (Easiest)
- [ ] CCAvenue merchant account
- [ ] No additional code or integration needed
- [ ] CBDC auto-enabled as checkout option

### Option B: HDFC SmartGateway
- [ ] HDFC Bank merchant account
- [ ] SmartGateway integration
- [ ] CBDC auto-enabled in gateway

### Option C: UPI Interoperability (Zero Effort)
- [ ] Any UPI payment gateway (Razorpay, PayU, Cashfree, etc.)
- [ ] No action needed — CBDC wallets can pay via your UPI checkout

---

## For Fintech Companies / Developers

### Requirements
- [ ] Registered entity (company/LLP/startup)
- [ ] Partnership with a participating bank OR
- [ ] Application to **RBI CBDC Retail Sandbox** (launched Oct 2025)
- [ ] For non-bank wallet: RBI approval + sponsor bank partnership

### Sandbox Access
- Apply via: https://fintech.rbi.org.in
- Provides: APIs, digital wallets, smart contract frameworks
- Can build: retail payments, cross-border remittances, programmable payments, tokenized loyalty

### What You CAN'T Do (Yet)
- [ ] ~~Call a public open API from RBI~~ — Does not exist
- [ ] ~~Programmatically create wallets for users~~ — Users must self-onboard
- [ ] ~~Process B2B high-value transactions~~ — Retail caps apply
- [ ] ~~Build on programmable money features~~ — Still in early testing

---

## For Wholesale CBDC (Banks/Financial Institutions Only)

### Requirements
- [ ] Must be a scheduled commercial bank or authorized financial institution
- [ ] RBI approval to participate in e₹-W pilot
- [ ] Technical infrastructure to connect to RBI's DLT platform
- [ ] Dedicated team for settlement operations

### Current Use Case
- Settlement of secondary market government securities
- Participating banks: SBI, Bank of Baroda, Union Bank, HDFC, ICICI, Kotak, Yes Bank, IDFC First, HSBC

---

## Technology Requirements Summary

### For Users
| Requirement | Specification |
|------------|---------------|
| Device | Smartphone (Android 6.0+ / iOS 12+) |
| Connectivity | Internet (offline NFC under pilot) |
| Storage | ~50-100 MB for wallet app |
| Security | Device lock/PIN required |

### For Merchants
| Requirement | Specification |
|------------|---------------|
| Device | Android or iOS smartphone/tablet |
| Connectivity | Internet (for standard transactions) |
| QR Code | Generated via merchant app |
| Settlement | Auto-credited to linked bank account (end of day) |

### For Developers
| Requirement | Specification |
|------------|---------------|
| API Access | Via CCAvenue / HDFC SmartGateway / RBI Sandbox |
| Languages | JavaScript, Python, PHP (PayAid SDKs) |
| Testing | RBI CBDC Retail Sandbox (simulated environment) |
| Production | Through bank partnership only |

---

## 19 Participating Banks (as of 2025-26)

| # | Bank |
|---|------|
| 1 | State Bank of India (SBI) |
| 2 | ICICI Bank |
| 3 | Yes Bank |
| 4 | IDFC First Bank |
| 5 | Bank of Baroda |
| 6 | Union Bank of India |
| 7 | HDFC Bank |
| 8 | Kotak Mahindra Bank |
| 9 | Punjab National Bank (PNB) |
| 10 | Canara Bank |
| 11 | Axis Bank |
| 12 | IndusInd Bank |
| 13 | Federal Bank |
| 14 | Karnataka Bank |
| 15 | Indian Bank |
| 16 | IDBI Bank |
| 17 | UCO Bank |
| 18 | Bank of Maharashtra |
| 19 | Bank of India |

**Non-Bank Entities:** CRED, MobiKwik (via Yes Bank partnership)

---

*Sources: RBI, CCAvenue, HDFC SmartGateway, Inc42, Business Standard*
