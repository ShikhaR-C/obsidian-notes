# 04 — Vehicle RC (VAHAN) & Driving Licence (SARATHI) verification, direct from government

**Researched:** 2026-08-05. **Constraint:** no paid aggregators.
**One-line answer:** consent-based RC + DL pulls are available **today, free, to private companies** via DigiLocker/API Setu (publisher: MoRTH) — that covers in-app onboarding of tank-trucks and drivers. Consent-less backend lookups now have a formal direct channel too: **MoRTH's NTR Data Sharing Policy (18-08-2025)** — application-based, no fees stated, but discretionary and slower.

---

## 1. Two distinct needs, two routes

| Need                                                                      | Route                                       | Cost                                                  | Timeline                                             |
| ------------------------------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------- | ---------------------------------------------------- |
| Onboarding-time verification with the truck owner / driver present in-app | **DigiLocker consent pull** (RVCER + DRVLC) | ₹0                                                    | inside the one-time DigiLocker onboarding (~2–8 wks) |
| Backend re-verification / bulk checks without the user in the loop        | **NTR policy application → NIC NAPIX APIs** | no fees stated in policy ⚠️ MoU-level fees unverified | months, discretionary                                |

## 2. DigiLocker consent route (live today)

- API Setu's `transport` collection (checked live 2026-08-05) is published by **MoRTH, "Provided by: DigiLocker"**: **Driving License (DRVLC)** and **Registration of Vehicles (RVCER)**, plus Fitness Certificate, Vehicle Insurance Certificate, Vehicle Tax Receipt — and ~36 state transport-department collections.
- Request inputs (per the OpenAPI spec — ⚠️ from a 2021-22 mirror, re-verify field-level details in the requester portal): DL pull needs `dlno + DOB + FullName + UID + consentArtifact`; RC pull needs `reg_no + chasis_no + FullName + UID + consentArtifact`. Response: the issuer-signed record as **XML + PDF**, straight from SARATHI/VAHAN.
- These are **legally valid documents** — MoRTH has notified DigiLocker/mParivahan virtual RC & DL as valid (NTR policy §3.4). A real private-sector precedent exists: **HDFC Ergo** retrieves DLs as a DigiLocker requester (official onboarding FAQ).
- Flow for us: driver/fleet-owner signs in with DigiLocker in-app → consents → we receive signed RC/DL XML → parse and store the verification result. Onboarding mechanics in [[05-apisetu-digilocker-onboarding]].

## 3. Direct backend access — the NTR Data Sharing Policy (18-08-2025)

The **"Policy for Data Sharing from the National Transport Repository"**, MoRTH, 18-08-2025 (52 pp; official PDF at parivahan.gov.in/sites/default/files/policy/data-sharing-policy.pdf) replaced the scrapped Bulk Data Sharing Policy 2019 (killed mid-2020 over privacy).

- **NTR** = VAHAN (39 cr vehicles) + SARATHI (22 cr DLs) + eChallan + eDAR + FASTag, under ss. 25A/62B MV Act. Every recipient becomes a **Data Fiduciary under the DPDP Act 2023**.
- **Eligible private categories:** "Transport Service Providing Agencies" — insurers, scheduled banks, HSRP/VLTD vendors, **transporters**, STUs, OEMs, component makers, **motor-vehicle aggregators**, associations — and **"Private Sector Entities providing Authentication Services for EOL/EODB"** (the policy explicitly contemplates _"DL as an authentication service on similar lines as Aadhaar Authentication"_). A logistics OMS is not named but plausibly fits either bucket. ⚠️ **No public example of a logistics SaaS approved under it was found.**
- **Access modes:** **API via NIC's NAPIX gateway** (preferred; napix.gov.in hosts a "Parivahan" domain with 773 NIC-published APIs — currently terms say "internal departmental use", domain-owner approval required), portal login, bulk (exceptional — only 5 government agencies ever; requests only from GoI Joint-Secretary rank).
- **Privacy mechanics:** PII to private recipients **only after data-principal consent via Aadhaar-authenticated OTP to the mobile number on record**; API responses come **masked** otherwise. Search keys: RC by registration no. OR chassis no. OR engine no.; **DL by DL number AND date of birth**.
- **Application process (manual/email until an online platform ships):** Annexure-I application to Deputy Secretary/Director (MVL), Transport Bhawan, New Delhi, with parameter-wise justification, DPDP s.7 grounding, a **Memorandum of Data Compliances**, and a **CERT-In-empanelled security-audit certificate** → MoRTH approval → NIC issues Client ID + secret → 1 whitelisted IP for testing, max 4 in production → **1-year validity, annual renewal + fresh audit**; India-only storage; **no sub-granting/resale**; per-recipient daily query caps.
- **Fees: the policy text specifies none at all** (grep of full text; Khaitan & Co's Sep-2025 note concurs). ⚠️ Whether individual MoUs levy charges is unverified.

## 4. Free citizen-facing checks (manual, capped — spot-checks only)

- **VAHAN "Know Your Vehicle Details"** (citizen login + mobile OTP + captcha): limited, partially masked data — **owner name masked**; under NTR the citizen service is capped at **3 queries/day**, non-PII. ⚠️ The legacy `vahan.parivahan.gov.in/nrservices` login page now instructs users to **migrate to the new NTR portal `services.parivahan.gov.in/ntr` before 15-08-2026**.
- **SARATHI DL search** ("Know Your Licence Details"): DL number + DOB + captcha → status/validity, issuing authority, class-of-vehicle; holder name masked.
- Browser-only (captcha/OTP), masked, rate-capped — unusable for fleet onboarding at scale, and scraping breaches the policy/ToS.

## 5. Bottom line

- **Do now:** DigiLocker requester onboarding — one application covers **RC + DL** (plus Aadhaar + PAN, see [[05-apisetu-digilocker-onboarding]]); ₹0; consented, signed, court-valid documents pulled live from VAHAN/SARATHI.
- **File in parallel if backend re-verification becomes a requirement** (e.g., periodic revalidation of fleet RCs, DL-expiry sweeps): an NTR Annexure-I application to MoRTH positioning DZZLO as a transport-service/authentication-service provider. Budget months and a CERT-In audit; no fee per the policy.
- **Skip:** scraping citizen portals; paid VAHAN resellers (the NTR policy's no-resale clause makes several aggregator sourcing claims suspect anyway).
