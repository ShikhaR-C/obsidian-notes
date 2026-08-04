# 03 — Aadhaar verification (dealer staff / driver users), direct from government

**Researched:** 2026-08-05. **Constraint:** no paid aggregators.
**Legal reality first:** a private company cannot simply call UIDAI's authentication API. Online Aadhaar auth/e-KYC is a licensed, statutorily gated ecosystem. But **two fully legal, direct, ₹0 routes exist today** — offline verification as an **OVSE** (QR / new Aadhaar app), and the **DigiLocker e-Aadhaar consent pull** — and both are API-shaped and work in-app. June 2025 is also a cautionary tale: MeitY **blocked Zoop, Surepass and Digitap** for unauthorised Aadhaar/PAN access — the no-aggregator instinct is correct here.

---

## 1. Routes ranked for us

| #   | Route                                                                                     | Legal basis                                                                         | Cost                                                                 | Timeline                                                 | Verdict                                                                                        |
| --- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1   | **Secure QR scan of e-Aadhaar / app-to-app with the new Aadhaar app, registered as OVSE** | Offline verification under Aadhaar Act + Amendment Regulations 09-12-2025 (Reg 13A) | UIDAI tools free; OVSE fees announced but amounts **unpublished** ⚠️ | integration days–weeks; OVSE registration weeks–2 months | ✅ **Primary** — proof-of-presence, suits driver identity checks (face verification supported) |
| 2   | **DigiLocker e-Aadhaar pull via API Setu**                                                | DigiLocker Requester (consent + Aadhaar OTP)                                        | ₹0                                                                   | inside the one-time onboarding, ~2–8 weeks               | ✅ **Digital-onboarding flow** ([[05-apisetu-digilocker-onboarding]])                          |
| 3   | Paperless Offline e-KYC XML (ZIP + share code)                                            | Offline verification                                                                | ₹0                                                                   | days to integrate                                        | Backup — clunky UX (user must self-download from myaadhaar.uidai.gov.in)                       |
| 4   | Sub-AUA/Sub-KUA under a licensed KUA                                                      | **Still requires our own eligibility** (see §5)                                     | KUA pass-through + margin                                            | gated by §5                                              | ❌ Not a bypass — application form forces us into a legal category                             |
| 5   | Own AUA/KUA licence via SWIK/MeitY route                                                  | Good-Governance Rules as amended 31-01-2025                                         | ₹5–20 lakh/2 yr + per-txn + heavy infra                              | **6–18+ months, uncertain**                              | Park — only with OMC/ministry sponsorship                                                      |

## 2. Route 1 — OVSE + Secure QR / new Aadhaar app

- **What:** every e-Aadhaar/mAadhaar/PVC card carries a **UIDAI-signed Secure QR** (photo + demographics + last-4 digits). UIDAI FAQ explicitly permits _"any User/Service Agencies like Banks, AUAs, KUAs, Hotels etc"_ to use it for offline verification. An app can embed QR parsing + UIDAI signature validation at zero UIDAI cost.
- **New Aadhaar app** (launched 28-01-2026): QR + **face verification** + selective/AVC (Aadhaar Verifiable Credential) sharing, designed for **app-to-app intent** flows — the modern in-app UX.
- **OVSE registration is now formal:** the Aadhaar (Authentication and Offline Verification) **Amendment Regulations, notified 09-12-2025**, insert **Regulation 13A** — application to UIDAI, scrutiny, approval/rejection with 30-day reconsideration, and **power to levy registration and per-verification fees (amounts not yet published ⚠️)**. Live registration page: uidai.gov.in/en/ovse-registration.html — asks for org name, logo (SVG), domain, callback URL, public certificate, Android/iOS app IDs (for app-to-app with the Aadhaar app). Listed target sectors explicitly include **gig economy, facility management, recruitment, fintech**.
- ⚠️ Commentaries differ on whether plain QR-scan verification is exempt from mandatory registration (Ikigai reads registration as mandatory for app-based offline e-KYC/AVC, exempt for QR/physical) — **register anyway**; it is where UIDAI is pushing everyone, and a **photocopy ban** is being phased in (UIDAI CEO: private entities must register and use QR/API/app instead of photocopies).
- **Obligations (Dec-2022 OVSE guidelines, still baseline):** explicit informed consent with auditable logs; purpose limitation; **never collect/store the Aadhaar number**; any retained copy masked to last-4 and irretrievable; prefer QR over photocopies. Violations attract Aadhaar Act ss. 29(2)–(4), 37.

## 3. Route 2 — DigiLocker e-Aadhaar pull

- Requester API endpoint `…/oauth2/3/xml/eaadhaar` returns e-Aadhaar **XML/JSON only — no PDF ("due to DPDP rules", official FAQ)**: name, **masked Aadhaar number**, DOB, gender, address, photo, hashed email/mobile. Given an Aadhaar number, DigiLocker _"can only verify the last 4 digits"_ (FAQ) — i.e. the payload is compliant-by-construction.
- User flow: dealer staff/driver signs in with DigiLocker (Meri Pehchaan) inside our app → Aadhaar OTP → consents → we receive the signed record. Full onboarding/OAuth details in [[05-apisetu-digilocker-onboarding]].

## 4. Route 3 — Paperless Offline e-KYC XML

User self-downloads a UIDAI-signed ZIP from https://myaadhaar.uidai.gov.in/offline-ekyc (choosing a 4-char share code), shares both in-app; we validate UIDAI's signature (public key + sample data on the UIDAI developer pages). Contains name, address, photo, DOB, gender, hashed mobile/email, reference ID with **last-4 digits only**. Free, no CIDR connectivity — but the download step makes it the worst UX of the three; keep as fallback.

## 5. Routes 4–5 — the licensed online-auth club (parked)

- **Who may do online auth at all** (post-2019 Amendment): Sec 4(4)(b)(i) entities permitted under PMLA s.11A (banks etc.) or another Central Act, or Sec 4(4)(b)(ii) entities allowed for "good governance" under the SWIK Rules 2020, **amended by G.S.R. 88(E) dt 31-01-2025** to let **any non-government entity apply** — proposal to the concerned Ministry → MeitY → UIDAI examination → **Gazette notification**. Portal: swik.meity.gov.in (launched ~Feb-Mar 2025).
- **SOP for private entities (v1.0, 11-03-2025, UIDAI PDF):** application needs CIN/TAN/GSTIN, 3-yr turnover, projected volumes (tiers ≤5 lakh / 5–20 lakh / >20 lakh txns/yr), use-case justification, a **mandatory alternate non-Aadhaar ID path**, architecture diagram with **HSM + Aadhaar Data Vault, DC/DR**, and the auth application hosted **on-premise or on Government Community Cloud only**. Annexure-1's indicative use-cases are strikingly close to ours: _"authentication during assigning of delivery partner by service aggregator companies"_, _"cab driver"_, _"staff attendance"_, _"customer onboarding"_ (sponsoring ministries listed: DPIIT, MoRTH…; **MoPNG is not on the indicative list**).
- **Fees once licensed:** licence (Circular 04 of 2023, eff. 01-07-2023): **₹5 L / ₹10 L / ₹20 L per 2-year validity** by volume tier (+ ₹5 L pre-production fee if you fail to go live in 3 months). Per-transaction (Circular 06 of 2023 + Payment-of-Fees Regs 2023): **e-KYC ₹3**, **Yes/No auth ₹0.50** (⚠️ circular PDF unreadable; rates rest on multiple secondary corroborations). Plus Sub-AUA/KUA rules (Circular 2 of 2025): joint undertaking, separate licence key, annual **CERT-In-empanelled audits**, joint & several liability.
- **Reality check:** the SWIK portal's public use-case list showed **418 approvals as of 2026-08-05 — all government entities; no private company visible** (⚠️ private approvals may simply not be published there). Gig/e-commerce platforms are reported still waiting. **Sub-AUA is not a side door** — the application form itself forces the Sub-AUA into an eligible legal category (a MeitY authorisation letter etc.).
- **The one realistic version for us:** an OMC (IOCL) or dealer association sponsors the use-case under SWIK and we ride as Sub-AUA/Sub-KUA. Worth raising in OMC conversations; not a 2026 plan.

## 6. Hard rules regardless of route

1. **Never store a full Aadhaar number** — masked last-4 + reference ID only; no photocopies (ban incoming).
2. Explicit, logged, purpose-limited consent per verification (Aadhaar regs **and** DPDP Act 2023 notice/consent duties stack on top).
3. Aadhaar is **voluntary** for private services — always keep the alternate-ID path (the SWIK SOP mandates it anyway).
