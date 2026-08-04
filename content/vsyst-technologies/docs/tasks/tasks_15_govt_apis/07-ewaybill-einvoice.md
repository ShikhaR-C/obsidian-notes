# 07 — E-way bill + e-invoice APIs (NIC/IRP), direct from government

**Researched:** 2026-08-05 (NIC docs fetched live). **Constraint:** no GSP, no paid aggregator.
**One-line answer:** **fully doable, ₹0 in government fees.** The sanctioned pattern: DZZLO registers once as a NIC **"registered ERP"** (sandbox test → test-summary report → IP whitelisting, ~3–6 weeks) and then **each dealer self-creates an API user bound to our ERP in minutes on the portal**. One credential set works on both the e-way-bill and e-invoice systems. Private IRPs (IRIS/Clear) add a fully self-service free lane for IRN generation.

---

## 1. Petroleum reality check first — what's even in scope

- **CGST Rule 138(14), verbatim (CBIC live text):** no e-way bill is required where the goods are _"alcoholic liquor for human consumption, **petroleum crude, high speed diesel, motor spirit (commonly known as petrol), natural gas or aviation turbine fuel**"_ — plus Annexure item 1 (**LPG to household/NDEC customers**), item 2 (**PDS kerosene**), and 138(14)(o) (empty LPG cylinders moved other than for supply).
- **So tank-truck fuel movements need NO e-way bill** (fuel is non-GST). **Commercial/bulk LPG does** need EWB. **E-invoicing (IRN) applies only to GST supplies** — no IRN exists for fuel invoices.
- **The AATO trap that makes this matter anyway:** "aggregate turnover" (s.2(6) + 2(47) — exempt supply _includes_ non-taxable supply) **counts fuel turnover**. Practically every fuel dealer therefore crosses the **₹5 Cr e-invoice mandate** → **their B2B invoices for GST lines (lubricants, AdBlue/DEF, spares, taxable tanker-hire) legally require IRN**, and many cross **₹10 Cr → the 30-day IRN reporting window (from 01-04-2025)** applies.
- Net scope for the OMS: e-invoice APIs for B2B GST-goods invoices/CN/DN; EWB APIs for GST-goods consignments > ₹50,000 (state variations exist); fuel dispatch documents remain outside both systems.
- Mandate status: **₹5 Cr AATO since 01-08-2023 (Notif. 10/2023-CT), unchanged through FY 2026-27**; B2C e-invoicing still a voluntary pilot (54th Council, Sep-2024), no notification as of Aug-2026.

## 2. E-way bill API access modes (and why per-dealer "direct" fails)

Modes on the NIC systems: **Direct** · **Through GSP** · **Through ERP** · **Through sister-concern GSTIN** (same PAN) · through e-commerce operator; e-invoice additionally honours existing EWB-API credentials.

**Direct-access eligibility (official, two live formulations):** FAQ — _"large taxpayers, who need to generate more than 1000 invoices / e-way bills per day"_; pre-requisites page — _"at least around 10 thousand transactions per month per GSTIN"_, SSL/TLS domain, static IP (max **3** whitelisted for EWB), a pre-production test system. **No rupee-AATO threshold exists for EWB direct** — it's volume-based, and **individual petroleum dealers won't meet it**; NIC-IRP e-invoice **direct** needs **AATO ≥ ₹100 Cr** (option doesn't even appear below that). ⚠️ Text of the login-gated "Registration → For API" portal screen could not be read without a taxpayer login.

## 3. The winning pattern — DZZLO as NIC "registered ERP"

**One-time, SaaS side (~3–6 weeks elapsed, ₹0 fees):**

1. Register on **einv-apisandbox.nic.in** choosing category **ERP** (PAN/GSTIN + OTP). Sandbox needs no IP whitelisting.
2. Build + test **every API — ≥50 success and 50 failure cases each** (e-invoice bar; EWB wants a test summary across all services), interfacing from our real application, not the online test tool.
3. Submit the **Test Summary Report**: e-invoice → **support.einv.api@gov.in**; EWB → **ewaybill.api.helpdesk@gmail.com** (yes, a Gmail address — verbatim from NIC's onboarding page).
4. Submit up to **4 Indian public static IPs** (e-invoice; 3 for EWB) for whitelisting — verification takes ~**4–5 working days**.
5. Receive production **client_id/client_secret** — _the same credentials work on both e-invoice (einvoice1/2) and EWB (1.0/2.0), with interchangeable tokens_ (Jul-2024 integration advisory; EWB 2.0 live since 01-07-2025 with full API parity).

⚠️ **Main execution risk:** ERP approval has **no published criteria** — it's discretionary/manual (this is why ERPNext's India Compliance ships via GSP Adaequare instead). Mitigation: pass the sandbox cycle cleanly and present DZZLO as the dealers' invoicing system of record, which is literally what an ERP category is for.

**Per dealer (minutes, self-service, no IT):** dealer logs into ewaybillgst.gov.in / einvoice1.gst.gov.in → Registration → For GSP / API Registration → **Create API User → select DZZLO's ERP** → sets a per-GSTIN **API username/password** → types them into the OMS. Dealer needs no IPs, no SSL, no sandbox. Prerequisites: EWB-portal registration; for e-invoice the GSTIN must be e-invoice-**enabled** (automatic at ₹5 Cr; self-enablement on einvoice.gst.gov.in if missed).

**Credential model (apicredentials.html, live):** client_id/secret identify the **provider** (ERP/GSP); **username/password are created by each taxpayer per GSTIN**; calls must originate from the provider's whitelisted IPs. Auth token: **6 h** in production (1 h sandbox); RSA-encrypted secrets, AES-256 payloads; firing identical duplicate requests gets the user **blocked ~1 hour**; ⚠️ no numeric rate limit is published.

## 4. E-invoice IRPs — six portals, core APIs free on all

| IRP           | Portal                         | Direct integration                                                                                                                                                              | Notes                             |
| ------------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| NIC-IRP 1 & 2 | einvoice1/einvoice2.gst.gov.in | direct only at **AATO ≥ ₹100 Cr**; else via ERP/GSP/sister/EWB-creds                                                                                                            | our route = ERP (§3)              |
| Cygnet IRP    | einvoice3                      | mirrors NIC's ₹100 Cr direct gate                                                                                                                                               | —                                 |
| **Clear IRP** | einvoice4                      | _"All taxpayers eligible for e-Invoicing can access… no limits imposed"_                                                                                                        | sandbox irp-sandbox.clear.in      |
| EY IRP        | einvoice5                      | turnover verified at Direct-API user creation; volume-based limits                                                                                                              | —                                 |
| **IRIS IRP**  | einvoice6                      | open to **all** enabled taxpayers; _"presently, no set API quota limits"_; self-service **solution-provider/API-integrator** registration; per-GSTIN onboarding via OTP consent | core APIs free; paid VAS optional |

GSTN, verbatim (Nov-2023 IRP guide): _"All the Core e-Invoice APIs are available Free of Cost on the respective Invoice Registration Portals (IRPs)."_

**Limitation:** private IRPs cover **IRN generation** (+ GSTR-1 auto-population + an EWB hand-off via _Generate EWB by IRN_ / `EwbDtls` in Generate IRN). They do **not** expose the full EWB operational surface — **Part-B/vehicle updates, transhipment, consolidated EWB, validity extension live only on NIC's EWB system**. Tank-truck logistics of GST goods therefore still wants §3. ⚠️ Clear/EY/Cygnet 2026 integrator terms not re-verified beyond their live URLs; confirm IRIS IP requirements with support@irisirp.com.

## 5. Compliance caveats (design constraints)

- NIC, verbatim: the service provider (GSP/ERP) _"is not supposed to store the request and response of the tax payers in his system"_ — architect EWB/IRN payload persistence as **the dealer's data store with consent**, not a provider-side archive.
- Direct-registered taxpayers _"should not share the username and password with [their] service provider"_ — another reason the ERP mode (credentials created _for_ our channel) is the correct legal shape, not collecting dealers' direct-mode credentials.
- 180-day document-age limit for EWB generation + 360-day extension cap (since 01-01-2025); the Jul-2026 "EWB closure + mandatory Ship-to GSTIN" changes are **on hold**.

## 6. Bottom line

- **Architecture:** DZZLO as NIC **registered ERP** (one credential set, both systems) + optionally **IRIS/Clear IRP integrator** as a faster self-service lane for IRN. Government fees: **₹0 end-to-end**. Real costs: 3–4 static Indian IPs, TLS endpoint, the sandbox test campaign (50+50 cases per API), engineering.
- **Timeline:** sandbox same-week; testing dominates; whitelisting 4–5 working days; realistic **3–6 weeks** to production. Per dealer thereafter: **minutes**.
- **Bonus:** ERP/EWB credentials give us the NIC **Get GSTIN details** API — closing the GSTIN-verification gap flagged in [[02-gstin-verification]].
- **Doesn't work:** per-dealer NIC direct registration (volume/AATO gates); sister-concern mode (same-PAN only). And fuel movements themselves never need EWB/IRN — set product expectations accordingly.
