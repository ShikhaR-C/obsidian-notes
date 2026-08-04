# 01 — PAN verification (dealer companies + individuals), direct from government

**Researched:** 2026-08-05 (all sources fetched live that day). **Constraint:** no paid third-party aggregators — government channels only.
**One-line answer:** the only direct-government PAN API a normal private company can actually obtain today is the **DigiLocker "PAN Verification Record" (PANCR) consent pull via API Setu — ₹0** ([[05-apisetu-digilocker-onboarding]]). The official bulk channel (Protean OPV) has a closed eligibility list that excludes an unregulated SaaS.

---

## 1. The four official channels at a glance

| Channel                             | What it is                                                     | Can VSYST get it?                              | Price                                                | Verdict                                                                           |
| ----------------------------------- | -------------------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Protean OPV** (ex-NSDL e-Gov)     | ITD-appointed bulk/API PAN verification                        | ❌ closed eligibility list (see §2)            | ₹12,000/yr + GST, then per-PAN slabs                 | Park — revisit only if we ever have SFT obligations or >500 TDS deductees/quarter |
| **UTIITSL "PAN Bulk Verification"** | the other ITD-appointed processor                              | ⚠️ opaque — login-gated portal, no public docs | reportedly same ₹12,000 + GST model (**unverified**) | Ignore                                                                            |
| **e-filing "Verify Your PAN"**      | free manual check on incometax.gov.in                          | ✅ anyone                                      | ₹0                                                   | Manual spot-checks only — no API                                                  |
| **DigiLocker PANCR via API Setu**   | consent-based pull of the ITD-issued _PAN Verification Record_ | ✅ private companies expressly eligible        | **₹0** (no platform charges)                         | ✅ **Our route**                                                                  |

## 2. Protean OPV — the official bulk service (and why we don't qualify)

Portal: https://tinpan.proteantech.in/services/online-pan-verification/pan-verification-overview.html (old `protean-tinpan.com` / `tin-nsdl.com` URLs 302-redirect here).

**Eligibility** (~35 named categories on the authorisation page): banks, NBFCs, insurers, SEBI/IRDAI/PFRDA-regulated entities, depositories, credit bureaus, KRAs/CKYC, exchanges, GSTN, ONDC, government agencies… The only routes a normal company could use:

- **"Companies and Government deductors (required to file TDS/TCS returns)"** — but only with **>500 deductees/collectees per quarter** shown on TDS provisional receipts (vetted at application).
- Catch-all: **"Any other entity required to furnish AIR/SFT"** — i.e. the catch-all is a Statement-of-Financial-Transactions obligation, **not** "any entity ITD approves".
- Every registration is individually **subject to Income Tax Department approval**; Protean's own FAQ on approval time is verbatim _"It is at the discretion of ITD."_ No SLA exists.

**Process (if ever eligible):** apply online at onlineservices.tin.egov.proteantech.in → pay → courier signed docs (T&C, NDA, authorization letter, DSC screenshots ×1 copy; Certificate of Incorporation, entity PAN, regulatory licence, declaration, balance sheet + P&L, ITR-V, business-information sheet ×2 copies) → Protean forwards to ITD → on approval an 8-digit user ID is emailed. **DSC mandatory** (Class II/III); **API mode additionally needs a Document Signer Certificate (soft PFX) + hardware e-token**. Fee refunded only if ITD rejects.

**Pricing (from Protean's own FAQ, fetched 2026-08-05):**

| Item                                                 | Amount                                                                                                                                          |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Registration / annual renewal                        | **₹12,000 + 18% GST = ₹14,160/yr**                                                                                                              |
| Free quota (file & API modes)                        | **750 PANs/day**                                                                                                                                |
| Beyond free quota (prepaid advance, FY-volume slabs) | ≤7.5 lakh PANs → **₹0.30**/PAN (750 free/day) · 7.5–15 lakh → ₹0.25 (1,000/day) · 15–30 lakh → ₹0.15 (1,500/day) · >30 lakh → ₹0.05 (2,500/day) |

**Modes:** screen (5 PANs at a time), file+screen (≤1,000 PANs/file, response in 24 h), software/API (real-time).
**Response fields:** PAN status (valid / not found / deleted / deactivated / **fake**), name-match Y/N, **DOB or date-of-incorporation match Y/N** (works for company PANs), and **Aadhaar–PAN linking status** (operative/inoperative/NA).
⚠️ The dedicated charges sub-page would not render (JS-only); the numbers above come from Protean's official FAQ pages. Protean also resells PAN verification commercially via its "RISE with Protean" marketplace (quote-based) — that is a paid channel, out of scope per our constraint.

## 3. UTIITSL

"PAN Bulk Verification" portal at https://www.pbv.utiitsl.com/pan_dcs/ — login-gated, **no public eligibility, fee or API documentation anywhere on utiitsl.com**. Third-party sources (BankBazaar) describe the same ₹12,000 + GST annual model. ⚠️ Everything about UTIITSL's service is **unverified from official pages**; pursuing it means contacting them directly. Protean is the documented default.

## 4. Income-tax e-filing portal (incometax.gov.in)

- **"Verify Your PAN"** — free, pre-login, **manual, one at a time** (PAN + name + DOB/DOI + mobile OTP): https://eportal.incometax.gov.in/iec/foservices/#/pre-login/verifyYourPAN. Returns active-status + detail match. No API.
- **"Verify Bulk PAN/TAN"** — post-login, restricted verbatim to _"external agencies… Central Government, State Government Departments or undertakings, and recognized autonomous bodies"_ plus RBI-approved banks/FIs. Registration needs a head-of-agency requisition letter + DSC + department approval. **A private SaaS cannot register.**
- A SOAP **PAN Verification API spec** exists (`services.incometax.gov.in/iec/api/CommVerServiceImplService/verifyDetails`, spec PDF Aug-2022) — same external-agency gate.
- **PAN–Aadhaar link status**: free manual pre-login check; no public API. The operative/inoperative flag does come back in Protean OPV and in the DigiLocker/aggregator rails.

## 5. DigiLocker PANCR — the route we can actually use

On API Setu's live directory (checked 2026-08-05) the `pan` collection (https://directory.apisetu.gov.in/api-collection/pan) is published by the **Income Tax Department** ("Provided by: UMANG") with two APIs: **"Track PAN"** and **"PAN Verification Record" (PANCR)** — `POST /pan/v3/pancr/certificate` returning the signed record (XML/PDF) given PAN + name + DOB + gender + consent artifact. This is the DigiLocker issued-document rail: **the dealer/user logs in with DigiLocker and consents; we receive the ITD-signed record**. Free; onboarding, obligations and OAuth mechanics in [[05-apisetu-digilocker-onboarding]].

⚠️ Constraint to design around: it is **consent-based** — perfect for onboarding KYC in-app, not usable for silent batch re-verification of stored PANs.

## 6. Zero-cost corroboration tricks (no API needed)

1. **Every GSTIN embeds the PAN** — characters 3–12 of a dealer's GSTIN are their PAN. GSTIN checksum-validation in code (see [[02-gstin-verification]] §5) therefore sanity-checks the PAN for free.
2. The GST portal's free Search-Taxpayer returns the **legal name** for a GSTIN — cross-check it against the claimed PAN holder name.
3. e-filing "Verify Your PAN" for occasional manual disputes.

## Bottom line

- **Direct-government, in-app, ₹0:** DigiLocker PANCR pull at onboarding (+ GSTIN-embedded-PAN cross-check in code). Timeline = the one-time DigiLocker requester onboarding, ~2–8 weeks ([[05-apisetu-digilocker-onboarding]]).
- **Protean OPV** (₹14,160/yr + slabs) is the only true bulk/backend government API, and we are **not on its eligibility list**; approval is discretionary with no SLA even for those who are.
