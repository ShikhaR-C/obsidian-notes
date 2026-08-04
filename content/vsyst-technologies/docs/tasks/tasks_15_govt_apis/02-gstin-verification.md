# 02 — GSTIN verification, direct from government

**Researched:** 2026-08-05. **Constraint:** no paid aggregators.
**Blunt answer:** there is **no open government API for GSTIN lookup that a private SaaS can subscribe to**. GSTN's architecture deliberately routes all machine access through commercial **GSPs** (GST Suvidha Providers). What still works direct-and-free: (a) checksum + format validation in code, (b) the **NIC e-way-bill / e-invoice "Get GSTIN details" API using each dealer's own API credentials** (see [[06-gst-filing-ewaybill-einvoice]]), (c) the captcha-gated manual portal search, (d) an API Setu application (outcome unproven — flagged below).

---

## 1. The free public search (manual only)

https://services.gst.gov.in/services/searchtp — no login, but **captcha per query**, so human-only. Pre-login it returns: GSTIN/UIN, **legal name**, trade name, registration date, constitution of business, principal place of business, taxpayer type, **status (active/cancelled + date)**, and recent returns-filed details (official manual: tutorial.gst.gov.in → "Search Taxpayer"). There is **no official API for this tool**; cheap "GST verification APIs" that aren't GSP-backed generally scrape this captcha page — not government-authorized, don't build on that.

## 2. Why there's no direct API: the GSP architecture

- All GST System APIs (developer.gst.gov.in — Taxpayer, Public, IRP categories) are reachable **only through an empaneled GSP** holding GSTN license keys + an MPLS link into GSTN.
- **Becoming a GSP** (the only "direct" path GSTN offers): latest empanelment (GSP 5.0, official eligibility PDF on gstn.org.in) required an Indian IT/ITES/BFSI company or MSME with **average turnover ≥ ₹50 lakh (FY 2020-21 → 2022-23)**, a **technical demo scored ≥70/100** (GSTR-1 upload, IRN handling, 2A reconciliation, DSC, security, load), India-based infra sized for **≥1 lakh GST transactions/month**, a data-privacy policy, an affidavit not to use GST data to sell financial products, and **MPLS connectivity to GSTN within 60 days of signing**.
- **62 GSPs** are currently empaneled (batch 5; secondary source Sep-2025). ⚠️ **No batch-6 window was found open as of 2026-08-05** — empanelment opens episodically; treat as closed until GSTN advertises.
- GSTN→GSP charges: the standard GSP agreement provides a **2-year fee moratorium from first API opening, extendable at GSTN's sole discretion**; current charging status is **not publicly verifiable**. GSPs' costs to ASPs are commercial (market ~₹0.33–1/call on annual packs — recorded in [[references]] for context only; out of scope per our constraint).
- Assessment for us: the ₹50 lakh turnover bar is passable, but the demo + 1-lakh-txn/month infra + MPLS line + a window that isn't open make become-a-GSP disproportionate for GSTIN checks. Re-evaluate only if [[06-gst-filing-ewaybill-einvoice]] concludes we need full returns APIs at scale.

## 3. API Setu — conflicting observations, worth one application ⚠️

- A **"GSTN Tax Payer API V2"** listing exists on the partners directory (https://partners.apisetu.gov.in/directory/api/taxpayers/1673347455_gstn-v2, listing created ~Jan 2023) — login-gated; publisher terms/eligibility **could not be read**.
- The **public** directory checked live 2026-08-05 returns **"No API Collection Found!"** for `gstn`/`gst` collections.
- Net: GSTN is not meaningfully on API Setu the way MoRTH/ITD are. Since API Setu costs nothing, file a subscription request for the taxpayers listing during our onboarding ([[05-apisetu-digilocker-onboarding]]) and let the publisher decide — but **do not plan around it**.
- DigiLocker: GST Registration Certificate pull is asserted by secondary sources only — **not confirmed** against an official issuer list; verify from inside the requester portal once onboarded.

## 4. The direct-government API we _can_ get: NIC "Get GSTIN details"

Both NIC compliance systems expose a GSTIN-validation endpoint that returns registration data straight from the GST system:

- e-invoice: einv-apisandbox.nic.in → "Get GSTIN Details" — returns GSTIN, legal/trade name, address, state code, taxpayer type, **status (ACT/CNL/INA/PRO)**, and e-way-bill-block flag.
- e-way bill: docs.ewaybillgst.gov.in → "GET GSTIN details" (same shape).

Access model: direct client-credentials only for GSPs, e-commerce operators, and very large taxpayers — **but every dealer who registers for e-way-bill/e-invoice API access gets these calls with their own credentials**, and our OMS can be the system making them. That makes GSTIN verification a **free by-product of the e-way-bill integration** — full access mechanics, eligibility thresholds and per-dealer setup in [[06-gst-filing-ewaybill-einvoice]].

## 5. Zero-cost, zero-API validation layer (build first, catches most junk)

Validate in code before any network call:

1. **Format:** `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$` — 15 chars.
2. **State code** (chars 1–2) ∈ 01–38 valid state/UT codes, and matches the dealer's claimed state.
3. **Embedded PAN** (chars 3–12) — structurally valid PAN; 4th char of the PAN should be `C` for companies / `P` for proprietors etc.; cross-check against the PAN collected in [[01-pan-verification]].
4. **Check digit** (char 15) — mod-36 checksum over the first 14 chars (alternating ×1/×2 weights on char values 0–35, sum of quotient+remainder, 36 − (total mod 36) mod 36). Catches typos instantly.

This is deterministic and free; only existence/active-status needs a live source (§1 or §4).

## Bottom line

- **Now, ₹0:** checksum + PAN-cross-check in code at onboarding; manual portal search by ops for the handful of new dealers a week; legal-name match against the portal result.
- **Soon, ₹0 and automated:** once dealers' e-way-bill API credentials exist ([[06-gst-filing-ewaybill-einvoice]]), call NIC Get-GSTIN-details server-side at onboarding — direct government data, no aggregator.
- **Parked:** GSP (window closed, infra-heavy), API Setu GSTN listing (apply opportunistically, unproven).
