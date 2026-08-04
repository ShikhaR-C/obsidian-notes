# DZZLO OMS — Product Overview

> Founder reference. What the product is, who it serves, how it works end-to-end, and the surface area a strategy doc needs to reason about. Plain English; no marketing.

---

## 1. What DZZLO OMS is

**One-liner:** DZZLO OMS is a multi-tenant, mobile-first Order Management System for Indian fuel distribution — petrol pump dealers, lubricant distributors, and bulk diesel operators.

**The problem it solves (plain English):**
An Indian fuel dealer today runs his business on a stack of four tools: a paper Daily Sales Register (DSR) for shift accounting, Tally for GST books, WhatsApp for customer orders, and Excel for credit tracking. Rate changes, credit limits, driver movements, tank dips, and invoices live in different places. Nothing is reconciled until month-end, by which time stock variance, credit aging, and GST mismatches have compounded.

DZZLO OMS collapses that stack into a single mobile + API system where:

- The dealer sets daily rates, receives orders, dispatches vehicles, invoices, and records payments in one place.
- The customer views ledgers, places orders, confirms rates, and settles vouchers on a phone.
- GST/TCS/TDS compliance is baked into the invoice pipeline rather than bolted on.
- Tank dip readings, meter reads, and inspection records flow into the same ledger the accountant sees.

It is not "another petrol pump billing app." It is a two-sided transaction platform between the **dealer** (supply side) and his **B2B customers** (demand side), with the compliance rails India requires.

---

## 2. User roles & primary user

DZZLO OMS has **two distinct user worlds** connected by a junction entity.

| Role         | Who they are                                                           | What they do in the app                                                                              | Pays the bill?                     |
| ------------ | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------- |
| **Dealer**   | Petrol pump owner, lubricant distributor, bulk diesel operator         | Owns the tenant. Sets rates, receives orders, invoices, records payments, manages fleet and drivers. | **Yes — primary buyer.**           |
| **Customer** | Dealer's B2B customer (transport fleet, factory, hospital, contractor) | Places orders against a pre-approved credit line, tracks ledger, settles invoices.                   | No — rides on the dealer's tenant. |

**Scope model (see `models/users.js`):** each user sits in a scope — `CPrimary`, `CAdmin`, `COrder`, `CAccount`, `CView` on the customer side; `D*` variants on the dealer side; `SAdmin` for the platform operator. This mirrors the reality that a customer's admin, order-placer, and accountant are often three different people in the same firm.

**Primary user = Dealer.** The dealer is the paying tenant; the customer experience exists to reduce the dealer's reconciliation cost. Design and roadmap decisions weight dealer pain above customer delight.

**Junction: `dealer_custs`** — the many-to-many between dealers and customers, holding per-relationship balance, credit terms, and TCS flags. A single customer firm can be onboarded by multiple dealers with different credit lines.

---

## 3. Core workflow

The system runs on a five-stage loop, and every feature hangs off one of these stages.

1. **Rate setting (dealer, evening).** Dealer opens the rate master, sets next-day rates per product per customer (or uses a default rate). Between **10 PM and 6 AM** the rate is in a **confirmation window** — customers receive push notifications and must confirm; unconfirmed rates auto-lock at 6 AM. This prevents the classic "we didn't agree to that rate" dispute.

2. **Order placement (customer or dealer-on-behalf).** Customer places an `order_mst` against a confirmed rate, typically with a requested delivery date and vehicle. The dealer converts it to a `so_mst` (sales order) when accepted.

3. **Dispatch (dealer).** Dealer assigns a vehicle (`veh_mst`) and driver (`dvr_mst`). Driver receives an OTP (via 2Factor.in) that the customer verifies on delivery. Vehicle movement is logged in `veh_trns`.

4. **Invoice (dealer).** On delivery confirmation, an `inv` is generated. DZZLO supports a **three-tier invoice system**: PRODUCT (the fuel line), CASH_REIMBURSE (on-behalf expenses), and GST (tax-only documents for reconciliation). TCS is auto-added when the customer crosses ₹50L turnover for the year (`lysal`/`lypmt` flags on `dealer_custs`).

5. **Payment & reconciliation.** Customer issues a voucher (`voc_mst`) — NEFT, RTGS, cheque, card, fleet card, or cash — against one or more invoices. A `pay_trn` links voucher to invoice(s). Unallocated balances roll into `month_crdrs` (monthly credit/debit aggregation) for month-end reports.

The entire loop is auditable because every document (order, SO, invoice, voucher, payment) retains its lineage.

---

## 4. Fifteen key features

Grouped by the role that uses them.

### Dealer-side (supply)

1. **Daily rate master with confirmation window** — per-customer daily pricing, 10 PM–6 AM confirmation gate.
2. **Three-tier invoicing** — PRODUCT / CASH_REIMBURSE / GST invoices distinguished at the schema level.
3. **TCS auto-trigger at ₹50L** — system monitors year-to-date sales/receipts on `dealer_custs` and flips `lysal`/`lypmt` to require TCS collection.
4. **Vehicle fleet & driver management** — `veh_msts`, `veh_reqs`, `dvr_msts`, with Indian registration validation.
5. **Voucher management** — six payment modes mapped to `voc_msts`, each with its own validation (cheque number, NEFT UTR, fleet card ID).
6. **Monthly credit/debit aggregation** — `month_crdrs` collapses a month of transactions into one reconciled row per customer.

### Customer-side (demand)

7. **Rate confirmation with push notifications** — OneSignal-driven, tied to the 10 PM–6 AM window.
8. **Mobile order placement** — React Native app, minimum-typing UX for low-literacy staff.
9. **Ledger and statement view** — live balance, aged receivables, downloadable PDF statements.
10. **Multi-user scopes inside one customer firm** — admin, order-placer, accountant, view-only.

### Common (both sides)

11. **Driver OTP delivery verification** — 2Factor.in OTP binding the dispatch to a confirmed delivery event.
12. **Multi-dealer customer support** — one customer firm, many dealer relationships, each with its own credit terms.
13. **Invite flow** — `invites` model, phone-OTP onboarding rather than email/password.

### DIP (tank monitoring) module

14. **Tank dipstick readings (`meter_reads`, `insps`, `decants`)** — physical stock reconciliation: dip, density, temperature, decant events.
15. **Inspection log** — Legal Metrology-style audit trail linking physical readings to invoice-side stock movement.

---

## 5. Core entities (plain English)

| Model          | What it is                                                                               |
| -------------- | ---------------------------------------------------------------------------------------- |
| `cust_msts`    | Customer firm master — one row per B2B customer, PAN/GSTIN/address.                      |
| `dealer_msts`  | Dealer (tenant) master — one row per paying dealer.                                      |
| `dealer_custs` | Junction: which dealer sells to which customer, with credit limit, terms, and TCS flags. |
| `order_msts`   | Customer order — intent to buy at a confirmed rate.                                      |
| `so_msts`      | Sales order — dealer's accepted, allocated version of the order.                         |
| `invs`         | Invoice — PRODUCT / CASH_REIMBURSE / GST subtypes.                                       |
| `voc_msts`     | Voucher — payment instrument (NEFT/RTGS/cheque/card/fleetcard/cash).                     |
| `pay_trns`     | Payment transaction — links vouchers to invoices.                                        |
| `veh_msts`     | Vehicle master — truck/bowser/tanker with Indian registration.                           |
| `veh_trns`     | Vehicle transaction — movement/dispatch event.                                           |
| `veh_reqs`     | Vehicle request — customer-side request for a specific vehicle.                          |
| `dvr_msts`     | Driver master — name, licence, linked phone for OTP.                                     |
| `psocs`        | Product supplier catalog — Petrol / Diesel / Lubes / Grease categories.                  |
| `prod_msts`    | Product master — dealer-specific SKUs.                                                   |
| `rate_msts`    | Rate master — daily per-customer per-product pricing with confirmation state.            |
| `month_crdrs`  | Monthly credit/debit roll-up per customer.                                               |
| `invites`      | Phone-OTP invitation flow for onboarding.                                                |
| `users`        | User accounts with scope enum (CPrimary/CAdmin/COrder/CAccount/CView + D\* + SAdmin).    |
| `meter_reads`  | DIP: periodic tank meter readings.                                                       |
| `insps`        | DIP: inspection log (Legal Metrology-style).                                             |
| `decants`      | DIP: decanting event — fuel received into tank.                                          |

---

## 6. Unique / differentiating capabilities

A generic OMS (Zoho, Tally, Busy, a regional petrol pump billing tool) can issue an invoice and track a ledger. It **cannot**:

- Model the **10 PM–6 AM rate confirmation window** and auto-lock stale rates.
- Distinguish **PRODUCT vs CASH_REIMBURSE vs GST** invoices natively — in generic ERPs this is a manual document-type hack.
- **Auto-trigger TCS at ₹50L** using year-to-date turnover flags on a two-party junction, correctly separating the sales-crossing (`lysal`) from the payment-crossing (`lypmt`) thresholds.
- Bind a **driver OTP** to a delivery event so the invoice is unforgeable.
- Ingest **tank dip readings, density, and decant events** into the same ledger the accountant uses.
- Handle **litre-based volume discounts** (as opposed to rupee-based) which is how fuel actually trades.
- Run **per-customer daily rate masters** at the granularity Indian petrol pump dealers need.

These seven are the moat, not features to be copied by a generic player in a sprint.

---

## 7. Tech & quality signals

| Signal               | Status                                                                               |
| -------------------- | ------------------------------------------------------------------------------------ |
| Backend              | Node.js / Express / MongoDB                                                          |
| Mobile               | React Native (one codebase, dealer + customer apps)                                  |
| API versioning       | `api_v1`, `api_v2`, `api_v3` — versioned route trees, not `?v=` params               |
| Tests                | 121+ automated tests (unit + integration)                                            |
| Deploy               | PM2 process manager, zero-downtime reload                                            |
| Notifications        | OneSignal (push) + 2Factor.in (SMS/OTP)                                              |
| Security             | Middleware stack for auth, rate-limiting, scope enforcement                          |
| Multi-tenancy        | Tenant = dealer; all queries scoped by `dealer_id`. No shared-customer data leakage. |
| Production readiness | MVP in production with paying tenants                                                |

The code quality is above the category average. Regional petrol pump software is usually a single-version Windows desktop binary with an AMC-based upgrade model. DZZLO's versioned, tested, containerised stack is a structural advantage for enterprise and fintech conversations.

---

## 8. Geography & compliance

DZZLO OMS is **India-only by design**, not by accident. Baking India into the schema is a moat, not a limitation.

| Vector               | DZZLO's stance                                                                                       |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| Currency             | INR only.                                                                                            |
| Phone                | 10-digit Indian mobile, OTP via 2Factor.in.                                                          |
| Tax IDs              | GSTIN, PAN, TAN validated at schema level.                                                           |
| Vehicle registration | Indian RTO format (`MH-12-AB-1234`).                                                                 |
| GST compliance       | CGST/SGST/IGST split, HSN codes, invoice numbering rules.                                            |
| TCS                  | Auto-trigger at ₹50L per customer per FY.                                                            |
| TDS                  | Handled at voucher level for applicable customers.                                                   |
| e-Invoicing (IRP)    | Architected for IRP push (mandatory >₹5Cr turnover; >₹10Cr must push within 30 days as of Apr 2025). |

Internationalising would mean re-doing half the data model. Competitors that start global and try to localise India always ship a thin GST veneer on top of a US/EU schema; DZZLO is the inverse.

---

## 9. Why this matters for strategy

The reason this overview exists first, before any strategy document, is that every subsequent analysis — market sizing, competition, pricing, go-to-market, fintech layering — turns on a clear-eyed view of **what the product actually is** and **who actually pays**.

- The primary user is the **dealer**, not the customer. This re-orients every GTM conversation.
- The moat is **compliance + domain depth + mobile-first**, not UI polish.
- The platform is **two-sided**, which opens embedded finance (lending to customers against dealer invoice data, factoring dealer receivables) well beyond SaaS ARPU.
- The tech quality is **enterprise-grade**, which supports moving up-market toward OMC and large distributor conversations.
- The **India-only** posture is a feature, not a bug, given the regulatory forcing functions coming through 2025–2026.

---

**Read this next:** [`01_IDEA_VALIDATION.md`](./01_IDEA_VALIDATION.md) — first-principles validation of the market, competition, and build/no-build verdict.
