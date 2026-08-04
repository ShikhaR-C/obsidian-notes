# 06 — In-app GST return filing (GSTR-1 / GSTR-3B / 2A / 2B), direct from government

**Researched:** 2026-08-05. **Constraint:** no paid aggregators.
**One-line answer:** the GST System's returns APIs are reachable **only through an empanelled GSP over MPLS — there is no direct internet route, no self-service signup, no exemption**. The three lawful options are: become a GSP (feasible on paper, window currently closed), ride a GSP as an ASP (= the paid-third-party model we're rejecting), or the **free portal/offline-tool flow** (works today, last mile is manual).

---

## 1. What the government returns APIs are

Official spec portal: https://developer.gst.gov.in/apiportal/ (GSTN; specs behind a free developer login). Catalog groups (live nav, 2026-08-05): **Taxpayer API** (Authentication, Registration, FO, Payment, **Returns**, **Ledger**, E-Invoice, SRM), **Public API**, **IRP API**. The returns set covers: GSTR-1 SAVE/SUBMIT/FILE + section-wise GETs, GSTR-3B save/offset/file, GSTR-2A section-wise GET, **GSTR-2B single-shot GET (API v4.0 mandatory since Nov-2024; rate-wise tax break-up removed)**, cash/ITC/liability ledgers, registration, Search Taxpayer, Track Return. ⚠️ Sandbox `developer.gstsystem.co.in` was unreachable from outside India — likely geo-fenced; verify from here.

## 2. The access model — why "no GSP" means "no returns API"

- GSP Implementation Framework V3.0 (official, gstn.org.in), verbatim: _"GST System will provide API only through MPLS to the GSPs. This is to ensure controlled access of APIs."_ Each GSP gets a **unique license key** and can mint **sub-license keys** for its ASP partners. TaxPro's docs put it plainly: _"GST Server is not directly accessible over Internet but would be accessible only through authorized GST Suvidha Providers."_
- There is **no** "direct integration" category for returns, no large-ERP exemption — the Framework says large software players "will be themselves GSP" (which is exactly what Tally, Zoho, ClearTax, Cygnet did). The only self-service taxpayer API credential in the whole GST ecosystem is **NIC e-invoice for AATO > ₹500 crore** — not returns, and no petroleum dealer meets it (see [[07-ewaybill-einvoice]]).
- **Per-dealer consent model** (rides on top of whichever GSP channel): the taxpayer enables **My Profile → Manage API Access** on gst.gov.in (OTP-free session 6 h–30 days) → OTP request → authtoken → API calls; the final **FILE** step needs EVC (another OTP) or DSC. GSTN advisory 29-09-2025: taxpayers are getting a portal view of **active ASP consents ("Active Tokens"), revocation, and access logs** — design for revocable consent.

## 3. Which calls need the dealer's OTP vs not

| Class                      | APIs                                                                         | Auth                                                                              |
| -------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| Public (still GSP-routed!) | Search Taxpayer, Track Return                                                | no taxpayer auth                                                                  |
| Taxpayer-session           | GSTR-1 save/submit/file, GSTR-3B, 2A/2B fetch, ledgers, registration profile | Manage-API-Access + OTP authtoken (6 h–30 d session); filing additionally EVC/DSC |

Even "public" APIs are only served through the GSP pipe — this is why [[02-gstin-verification]] concludes there's no free GSTIN API.

## 4. Becoming a GSP — the only truly direct route

**Current status ⚠️:** batches were 34 (2016-17) → 42 (2017) → 10 (Nov-2019) → window closed Apr-2021 → **GSP 5.0 (FY 2023-24) → 62 GSPs empanelled today** (secondary source, Sep-2025). **No batch-6 window found open as of 2026-08-05** — announced only on gstn.org.in (JS site, check manually/periodically).

**Batch-5 eligibility (official PDF, gstn.org.in):**

| Requirement    | Bar                                                                                                                                                                                                                                                                                                                                                   |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Entity         | Indian IT/ITES/BFSI company, partnership/LLP, or Govt/PSU                                                                                                                                                                                                                                                                                             |
| Financial      | **average turnover ≥ ₹50 lakh over last 3 audited FYs; MSMEs relaxed further** (vs Batch 1's ₹5 Cr capital + ₹10 Cr turnover)                                                                                                                                                                                                                         |
| Infra          | India-located backend sized for **≥1 lakh GST transactions/month**; published data-privacy policy                                                                                                                                                                                                                                                     |
| Technical demo | **100 marks, pass = ≥60% per section AND ≥70% overall**, against the sandbox: GSTR-1 upload/delta (10), e-invoice JSON→IRN (10), QR/Rule-46 invoice PDF (5), 2A-vs-purchase-register recon + GSTR-1 filing + draft 3B (10), multi-GSTIN/multi-role (5), DSC signing (5), UI/UX (5), mobile (5), alerts (5), security design (10), **scale/load (30)** |
| Post-selection | GSP agreement + **affidavit never to use GST data to sell financial products**; **MPLS connectivity to GSTN within 60 days**                                                                                                                                                                                                                          |

**Costs & obligations (official agreement draft):** no empanelment fee appears in any official document (inferred zero ⚠️). GSTN's own API charges sit behind a **2-year moratorium "extendable at GSTN's sole discretion"** — no evidence GSTN has ever activated charges ⚠️. Real obligations: **ISO 27001 audit by a CERT-In-empanelled auditor before go-live and annually at GSP's cost**; **7-year retention** of full transaction/audit logs (incl. sub-license key of each requester); GSTN may audit without notice on fraud apprehension; liability cap = 12 months' charges except IP/confidentiality/data-breach (uncapped). Market-estimate run-rate (unofficial ⚠️): MPLS ₹2–6 L/yr + annual audit ₹2–5 L + DC/DR ⇒ **order of ₹10–25 lakh/year, near-zero payable to GSTN itself**.

**Timeline:** gated entirely on a window opening (cadence suggests 2026-27 plausible, unverified); once open, ~**4–9 months** (screening → invited demo → LOI → agreement → MPLS in 60 days → pre-commencement audit) if the demo build is ready.

**Assessment for VSYST:** the demo checklist is ~80% of an OMS compliance module we'd want anyway (GSTR-1 upload, recon, 3B draft, DSC, mobile). The ₹50 lakh bar and zero fees make this the first genuinely plausible "become the channel" option — but it's a company-level strategic bet (MPLS line, audits, 1-lakh-txn infra), not a feature ticket.

## 5. The free, sanctioned, no-API path that still works in-product

Everything on gst.gov.in is free: online GSTR-1/IFF and 3B forms, the **Returns Offline Tool** (V3.2.4 — collate + upload invoices for GSTR-1), the Matching Offline Tool for 2B-vs-purchase-register recon, and portal Excel/JSON downloads of 2A/2B. The sanctioned zero-cost architecture:

1. OMS generates the dealer's sales data as **offline-tool-compatible GSTR-1 JSON** (we already hold every invoice).
2. Dealer uploads it on the portal and files with EVC OTP (2 minutes of manual last-mile).
3. Dealer drops their downloaded 2A/2B JSON/Excel back into the app; recon runs in-product.

Fully legal, ₹0, no intermediary, shippable now — the filing click just can't happen inside the app.

## 6. Bottom line & watch-list

- **Ship now:** §5 JSON-generation + guided-filing + recon flow.
- **Watch:** gstn.org.in GSP section for a batch-6 window (only announcement channel); `developer.gstsystem.co.in` sandbox from an India IP.
- **Pre-build:** the 11-capability demo checklist (§4) against the sandbox so a window can be answered inside its deadline.
- **Alternative if time-to-market ever dominates:** JV with / acquire one of the 62 existing GSP licensees — still not a per-call aggregator fee, but a company-level decision.
