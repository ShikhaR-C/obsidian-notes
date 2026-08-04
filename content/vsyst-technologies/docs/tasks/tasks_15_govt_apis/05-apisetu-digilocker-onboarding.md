# 05 — API Setu + DigiLocker Requester onboarding (one gateway → Aadhaar, PAN, DL, RC)

**Researched:** 2026-08-05, primary documents read in full: API Setu consumer SOP v02/2024, DigiLocker Partner-Organisation Onboarding SOP (NeGD, 05-06-2024), Requester Terms of Use (02-06-2025), onboarding FAQ (updated 24-03-2025), Requester API Spec v1.12 (Oct-2023).
**Why this doc matters most:** this is the **only** government onboarding a private company can complete today that yields production APIs for **e-Aadhaar, PAN (PANCR), Driving Licence (DRVLC) and Vehicle RC (RVCER)** — all consent-based, all **₹0**.

---

## 1. What it is

- **API Setu** (apisetu.gov.in — MeitY / Digital India Corporation / NeGD): the directory + gateway. Consumers register once, then subscribe per-API; each subscription needs the **publisher's** approval (ITD for PAN, MoRTH for transport, etc.).
- **DigiLocker** is the consent rail behind the KYC-relevant APIs: the citizen signs in (Meri Pehchaan SSO), consents, and the requester receives the **issuer-signed document** (XML + PDF) from the source database. 70+ crore users, 900+ crore issued docs.
- Key mental model: **API Setu does not sell consent-less database lookups.** Its KYC APIs are citizen-consent pulls. "Restricted API" rejections happen when private companies ask for consent-less access — which isn't on the menu anyway.

## 2. Eligibility & documents

- Eligibility list (Partners SOP §3) explicitly includes **"All private Organizations"** (MCA/MSME/Startup-India/partnership/proprietorship/society/trust registrations all acceptable). Requirements: demonstrable experience providing online services to Indian citizens, a **functional website**, **digital signature capability (DSC)**, **official-domain email** (personal Gmail-type IDs are an explicit rejection reason). Foreign firms: Indian mobile number + India-located server mandatory.
- Documents at signup (SOP verbatim): **Proof of Identity, Authority Letter, Organization PAN, GST registration certificate, Certificate of Incorporation.** "Only one request will be entertained from one organization."
- Org identity is then verified through **Entity Locker**: the nodal officer authenticates by Aadhaar OTP; **CIN, GSTIN, PAN and Udyam numbers are verified** in the process.

## 3. Process, step by step (SOP)

1. Sign up at partners.apisetu.gov.in/signup with the use case, from the domain email (the DigiLocker partner portal partners.digilocker.gov.in is the same front door — official FAQ: "register on the API Setu platform").
2. Telephonic verification meeting with the DigiLocker/API Setu team.
3. Details verification; **Entity Locker** org verification (nodal officer Aadhaar OTP).
4. Review available APIs; **submit a use case per API** you want (for us: e-Aadhaar, PANCR, DRVLC, RVCER — and opportunistically the GSTN taxpayers listing, see [[02-gstin-verification]] §3).
5. Submit final application (auto-email confirmation).
6. **Two-step approval:** Business-Development Manager review → **Onboarding Committee (weekly meetings**; BD Head + Legal Compliance Manager) → **final approval by CEO**.
7. Sign the Agreement / click-through **Terms of Use** (Requester version, June 2025).
8. Integrate with issued client credentials (client_id/client_secret; callback-URL changes by email to partners@digitalindia.gov.in citing your Client ID).
9. **Demo your flow + test data to the team before go-live.** Note: _"No requests of temporary access for any testing purpose etc. will be entertained"_ and, for DigiLocker APIs, **"APIs are the same, there is no separate environment"** — there is no DigiLocker sandbox; you get production credentials post-approval and prove the flow in a demo. (The open sandbox at sandbox.api-setu.in covers directory APIs generally, without signup.)
10. Go-live with launch support.

**Housekeeping deadlines:** unverified accounts **auto-deleted after 3 months**; verified-but-inactive accounts **auto-disabled after 3 months** — don't onboard until we're ready to integrate.

## 4. Fees

Requester Terms of Use §9, verbatim: _"**Currently, there are no platform charges applicable.** However, should any such charges be introduced in the future, the Requester Organization will be duly informed in advance… always prospective in nature."_ The consumer SOP mentions no platform fee either. ⚠️ Real internal costs remain: DSC, the STQC/CERT-In audits below, engineering time.

## 5. Compliance obligations (ToS June-2025 + SOP)

| Obligation           | Detail                                                                                                                                       |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Consent              | Explicit informed user consent before any document access; **building the consent-capture mechanism is the consumer's responsibility** (SOP) |
| Data residency       | Data must **not be stored or transmitted outside India**                                                                                     |
| Retention            | No caching/storing documents beyond the permitted duration                                                                                   |
| Breach               | Notify NeGD **within 24 hours**; 7-day rectification window, then suspension/termination                                                     |
| Audits               | **STQC audit report of the application** post-integration; **annual compliance audit by a CERT-In-empanelled auditor**                       |
| Reporting            | Quarterly usage reports                                                                                                                      |
| Branding/credentials | Preserve DigiLocker branding; client_id/secret exposed publicly ⇒ immediate block                                                            |

## 6. Technical integration (Requester API Spec v1.12)

- **OAuth 2.0 authorization-code with PKCE**: fresh `code_verifier` (43–128 chars) per request, SHA-256/base64url `code_challenge`; token at `/oauth2/1/token`; exact-match registered redirect URI; optional HMAC-SHA256(client_secret, client_id, timestamp) with 30-min timestamp validity.
- **Per-document scopes**, e.g. `files.issueddocs`, `partners.PANCR`, `partners.DRVLC`; e-Aadhaar via `…/public/oauth2/3/xml/eaadhaar` (XML/JSON, never PDF — DPDP).
- Doctype codes we care about: **PANCR** (PAN Verification Record, ITD), **DRVLC** (DL, MoRTH/SARATHI), **RVCER** (RC, MoRTH/VAHAN), e-Aadhaar; also fitness/insurance/tax-receipt docs in the transport collection.

## 7. Confirmed pullable documents (each verified individually, 2026-08-05)

| Document                        | Confirmed | Notes                                                             |
| ------------------------------- | --------- | ----------------------------------------------------------------- |
| e-Aadhaar                       | ✅        | XML/JSON only; masked number; "can only verify the last 4 digits" |
| PAN Verification Record (PANCR) | ✅        | ITD-issued; live in the `pan` collection                          |
| Driving Licence (DRVLC)         | ✅        | live in the `transport` collection (HDFC Ergo precedent)          |
| Vehicle RC (RVCER)              | ✅        | live in the `transport` collection + state RTO collections        |
| GST Registration Certificate    | ⚠️        | secondary sources only — verify from inside the portal            |

## 8. Rejection reasons & support

**Official rejection causes (SOP §5):** personal email domains; incorrect/incomplete registration; deviation from the submitted use case; requests for temporary/testing access; duplicate org registrations; missing digital signature.
**Support:** apisetu.support@digitalindia.gov.in · partners@digitalindia.gov.in / partners@digitallocker.gov.in (DigiLocker) · partners.apisetu@digitalindia.gov.in (publisher onboarding). Video-call support is standard practice.

## 9. Timeline

No official SLA anywhere ⚠️. The committee meets **weekly** with CEO sign-off; realistic estimate **2–8 weeks** application→production (unofficial). Plan the STQC/CERT-In audit engagement in parallel so go-live isn't audit-blocked.

## 10. What to prepare before applying (checklist)

- [ ] Official-domain email for the nodal officer (no Gmail)
- [ ] Company PAN, GST certificate, Certificate of Incorporation, authority letter, PoI of signatory
- [ ] Nodal officer with Aadhaar-linked mobile (Entity Locker OTP)
- [ ] Organisation DSC
- [ ] Functional public website describing DZZLO
- [ ] One-page use case per API: e-Aadhaar (user KYC), PANCR (dealer/company KYC), DRVLC (driver onboarding), RVCER (tank-truck onboarding) — consent-based, DPDP-compliant storage design (masked identifiers only)
- [ ] Consent-capture UX spec (our responsibility per SOP)
- [ ] Shortlist of CERT-In-empanelled auditors + STQC audit budget
