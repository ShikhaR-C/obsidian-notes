# Government verification & compliance APIs — direct from government, no aggregators

**Status:** Research complete (2026-08-05). **Not started — no repo code changes until explicit go-ahead.**
**Created:** 2026-08-05
**Scope:** In-app verification of **dealer-company PAN + GSTIN**, **user Aadhaar**, **vehicle RC**, **driver DL** — plus in-app **GST return filing**, **e-way bill** and **e-invoice** generation — using government-direct APIs only. Hard constraint from the founder: **no per-call fees to third-party aggregators.**

---

## 1. The one-paragraph answer

Four government gateways cover the entire wishlist, and **every route we recommend has ₹0 in government fees**: (1) **DigiLocker Requester via the API Setu partners portal** — one onboarding, ~2–8 weeks, yields consent-based in-app pulls of **e-Aadhaar, PAN, Driving Licence and Vehicle RC** signed by the issuing departments; (2) **UIDAI OVSE registration** — QR-scan / new-Aadhaar-app verification with face-match for proof-of-presence driver checks; (3) **NIC "registered ERP" status** — ~3–6 weeks, one credential set for **e-way bill + e-invoice APIs** for every dealer GSTIN (each dealer self-links in minutes), which also unlocks the **Get-GSTIN-details** API, closing the GSTIN-verification gap; (4) **GSTN** — the one closed door: returns APIs are GSP-only over MPLS, so GST filing ships as a free portal/offline-JSON flow now, with **become-a-GSP** (₹50 lakh turnover bar, no fee, window currently closed) as the strategic watch item. Optional fifth: a **MoRTH NTR policy** application for consent-less backend RC/DL lookups.

## 2. Per-item summary

| #   | What                    | Direct government route (portal)                                                                                                                            | Gov fee                                 | Realistic timeline                                     | Doc                                                                     |
| --- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------- |
| 1   | Company/individual PAN  | DigiLocker **PANCR** pull via partners.apisetu.gov.in; Protean OPV (₹14,160/yr) exists but eligibility excludes us                                          | **₹0**                                  | inside the one DigiLocker onboarding, ~2–8 wks         | [[01-pan-verification]]                                                 |
| 2   | GSTIN                   | No open govt API exists. Checksum+PAN cross-check in code now; **NIC Get-GSTIN-details** once ERP creds exist; manual portal search                         | **₹0**                                  | with #6                                                | [[02-gstin-verification]]                                               |
| 3   | Aadhaar (users/drivers) | **OVSE registration** (uidai.gov.in/en/ovse-registration.html) → QR / new Aadhaar app with face verification; DigiLocker e-Aadhaar pull as the digital flow | **₹0** today (OVSE fee schedule TBA ⚠️) | integration days–weeks; OVSE weeks–2 months            | [[03-aadhaar-verification]]                                             |
| 4   | Vehicle RC + Driver DL  | DigiLocker **RVCER/DRVLC** pulls (MoRTH publisher); **NTR policy** application for backend lookups                                                          | **₹0** (NTR policy states no fees)      | same onboarding; NTR months, discretionary             | [[04-vehicle-rc-driving-licence]], [[05-apisetu-digilocker-onboarding]] |
| 5   | GST return filing       | **GSP-only** — no direct route exists. Ship free offline-JSON + guided portal filing; watch GSP batch-6 window (₹50 L bar, no fee, demo-gated)              | **₹0**                                  | portal flow now; GSP 4–9 months _after_ a window opens | [[06-gst-return-filing]]                                                |
| 6   | E-way bill + e-invoice  | **NIC registered-ERP** (einv-apisandbox.nic.in, category ERP) + optional IRIS/Clear IRP integrator lane; dealers self-create API users bound to us          | **₹0**                                  | **3–6 weeks** to production; minutes per dealer        | [[07-ewaybill-einvoice]]                                                |

## 3. What it actually costs

- **Government fees on the recommended stack: zero.** The paid government options are all parked: Protean OPV ₹12,000+GST/yr (we're not eligible anyway), UIDAI AUA/KUA ₹5–20 lakh/2 yr + ₹0.50/auth + ₹3/eKYC (6–18+ months, ministry sponsorship), possible future OVSE/DigiLocker fees (both currently ₹0, both reserve the right).
- **Real internal costs:** organisation DSC; 3–4 Indian static IPs + TLS endpoint; **STQC audit of the app + annual CERT-In-empanelled audits** (DigiLocker, NTR and GSP all require CERT-In-empanelled auditors — one engagement can serve several programs); consent-capture UX (explicitly our responsibility per the SOP); the NIC sandbox test campaign (≥50 success + 50 failure cases per API); India-only data hosting (already true).
- The aggregator route we rejected would have cost roughly ₹1.5–4 per verification (recorded for context in [[references]] §9) — the trade we're making is **weeks of onboarding + audits instead of per-call fees forever**.

## 4. Application sequence (when go-ahead is given)

1. **Prep pack** (see checklist in [[05-apisetu-digilocker-onboarding]] §10): official-domain email, DSC, company PAN + GST cert + COI + authority letter, nodal officer with Aadhaar-linked mobile, public website, one-page use case per API.
2. **Apply: DigiLocker Requester** on partners.apisetu.gov.in → covers PAN + Aadhaar + DL + RC in one approval (weekly committee, CEO sign-off). Don't apply before we're ready to integrate — unverified accounts are auto-deleted after 3 months.
3. **Register: UIDAI OVSE** in parallel (form-based; org name, domain, callback URL, public cert, app IDs).
4. **NIC sandbox**: register as **ERP**, run the test campaign, submit test-summary reports, whitelist IPs → production for EWB + e-invoice + Get-GSTIN.
5. **Ship the GST filing v1** with no application at all: GSTR-1 offline-tool JSON generation + guided portal filing + 2A/2B recon on portal downloads.
6. **Watch**: gstn.org.in GSP section for a batch-6 window; pre-build the 11-capability demo against the sandbox.
7. **Optional**: NTR Annexure-I application to MoRTH (Director MVL, Transport Bhawan) if consent-less backend RC/DL re-verification becomes a product requirement.
8. **Long shot, OMC-sponsored**: SWIK/MeitY Aadhaar-authentication proposal riding IOCL/dealer-association sponsorship ([[03-aadhaar-verification]] §5).

## 5. Rules that shape the product

- **Everything KYC is consent-based.** Government KYC APIs for private companies are consent rails, not database lookups: the user is in the loop (DigiLocker OAuth + Aadhaar OTP; QR presented in person; NTR's Aadhaar-OTP consent for unmasked PII). Design onboarding flows around that; batch silent re-verification mostly doesn't exist legally.
- **Aadhaar:** never store the number; masked last-4 + reference ID only; no photocopies (ban being phased in); always offer a non-Aadhaar alternative.
- **DigiLocker ToS:** India-only data, 24-hour breach notification, quarterly usage reports, STQC + annual CERT-In audits, no caching beyond permitted duration.
- **NIC ERP rule:** the provider must not store request/response payloads — persist compliance data as the **dealer's** store, with consent.
- **Petroleum quirk:** fuel (petrol/HSD/crude/ATF/natural gas) is non-GST → **no e-way bill, no IRN, ever** (Rule 138(14)(f)); household/NDEC LPG and PDS kerosene also EWB-exempt. But **AATO counts fuel turnover**, so dealers still cross the ₹5 Cr e-invoice mandate for their **lubricant/GST B2B lines**, and many cross ₹10 Cr → 30-day IRN window. Set product expectations accordingly.
- **DPDP Act 2023** consent/notice duties sit on top of every route.

## 6. Doc map

[[01-pan-verification]] · [[02-gstin-verification]] · [[03-aadhaar-verification]] · [[04-vehicle-rc-driving-licence]] · [[05-apisetu-digilocker-onboarding]] · [[06-gst-return-filing]] · [[07-ewaybill-einvoice]] · [[references]]
