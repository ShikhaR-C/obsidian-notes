# 01 — Data Foundation: What We Have, What's Missing, What to Capture Now

> Every AI feature in this plan stands or falls on data. This doc audits the data we already have in `dzzlo_oms_api` (MongoDB, dual DB: OMS + DIP), the gaps that block specific features, and the **cheap schema additions to make immediately** so that by the time we build models, we have months of history.

---

## 1. Data We Already Have (by collection)

### Trade & money

| Collection | AI-relevant fields | Feeds |
|---|---|---|
| `order_msts` (purchase orders) | `products[] {prod_id, quantity, rate, input_type (AMT/QTY), is_full_tank}`, `veh_id`, `on_dt`, `order_status` (PENDING→PROCESSING→DELIVERED→DELETED), `otp_by {personType, response}`, `cs_reimb_amt`, timestamps | Demand forecasting, ordering-pattern features, fraud detection, OTP deliverability |
| `so_msts` (sales orders) | `slip_no`, `products[]`, `dvr_id`, `veh_id`, links to up to 3 invoices | Dealer-side volume, driver-level activity |
| `invs` (invoices) | `inv_qty`, `inv_amt`, `inv_total_amt`, `inv_type` (PRODUCT/CASH_REIMBURSE/GST), `inv_status` (UNPAID/PARTPAID/FULLPAID/UNAPPROVED), `inv_tcs_amt`, `inv_dt`, `inv_term` | **Invoice aging — the core credit-risk label source** |
| `voc_msts` (payments/vouchers) | `amount`, `pay_mode` (cash/cheque/card/fleetcard/neft/rtgs), `pay_dt`, `eff_dt`, `voc_type` (PInv/PAdvice/CrNote/DrNote/TCS/TDS/AdvDep), `pay_status` (approval), `invs_adj[]`, `tds_amt` | Payment-latency features, payment-mode risk signals, settlement graphs |
| `month_crdrs` | `{cust_id, dealer_id, month, drttl, crttl}` | Monthly exposure trajectory, seasonality |
| `dealer_custs` (the relation) | `cust_type` (CASH/CREDIT), `max_cr_lmt`, `cr_lwr_lmt`, `max_cr_days`, `cr_bill_period`, `adv_dep`, `cust_bal[]` (opening balances), `discount_*`, `taxStatus`, `lysal/lypmt`, `cust_blacklist` (on `cust_msts`), `closed/hidden` | **The credit contract — every risk model keys on this pair** |
| `rate_msts` | `{dealer_id, prod_id, date, rate}` daily | Price time series, rate benchmarking, margin analytics |

### Fleet & people

| Collection | AI-relevant fields | Feeds |
|---|---|---|
| `veh_msts` | `veh_reg_no` (validated Indian plates), `route`, `cust_id` | Per-vehicle consumption baselines; `route` is free-text today (see gaps) |
| `dvr_msts` | `name, phone, code, veh_id, companies[]` | Driver-level behavior scoring |
| `veh_trns` | `veh_status (inuse/notuse)`, `relation (OWN/HIRED/SHARED)` | Fleet utilization |
| `veh_reqs` | hire/share request graph between transporters | Marketplace matchmaking |
| `users` | `role`, `scope`, `companies[]`, `notif[]` prefs | Personalization, notification targeting |

### Location & catalog

| Collection | AI-relevant fields | Feeds |
|---|---|---|
| `dealer_msts` | `dealer_coords` (GeoJSON Point), `highway_no`, `city/district/state/pin_code`, `oil_co` (PSOC), `toGrt` | Geo recommendations, demand mapping, brand-level analytics |
| `cust_msts` | `cust_coords`, address fields, `cust_verified`, `cust_blacklist` | Same |
| `psocs` / `prod_msts` | brand, product categories, HSN, GST rate, `rates[]` snapshot | Product-level segmentation |

### Pump physical (DIP DB)

| Collection | AI-relevant fields | Feeds |
|---|---|---|
| `dealers` (DIP) | `tanks[] {dia, length, deadwood, capacity, prod_id}`, `dus[]`, `nzls[]` (with stamping dates) | Tank capacity context for refill planning |
| `decants` | `decan_dt`, `rcvd_qty`, per-tank start/end dip, per-nozzle before/after | Receipt verification, short-delivery detection |
| `meter_reads` | per-tank `c_dip, c_rcvd`, per-nozzle `c_test, c_mtr`, `isInsp` | **Daily sales & stock series per tank/nozzle** |
| `insps` | reconciliation between two meter reads (cumulative received/test/sale vs dip) | **Shrinkage/variance labels — pilferage detection ground truth** |

### Behavioral

| Collection | AI-relevant fields | Feeds |
|---|---|---|
| `logs` | method, url, `response_time`, status, full `user`, `appInfo` (device, app version) | Churn signals, feature adoption, assistant evaluation, ops anomaly detection |

---

## 2. Gaps That Block Specific Features

Ordered by how much they hurt.

| # | Gap | What it blocks | Fix |
|---|-----|----------------|-----|
| 1 | **No odometer / km reading at fill-up** | T1 fuel-theft detection can only reason in ₹/litres per day, not km/l (mileage) — the metric transporters actually trust | Add optional `odometer` to `order_msts` at order or OTP-verification time; nudge via app UI. Even 30% fill coverage builds baselines |
| 2 | **No vehicle tank capacity / vehicle class** | Can't flag "ordered 400L into a 250L tank" (classic diversion); weakens T1/T2 and D6 | Add `tank_capacity`, `veh_type` (truck/tipper/bus/…), `fuel_type` to `veh_msts`. Backfillable from reg-no via VAHAN-style lookups or G6 document scan |
| 3 | **`route` is free text** | T3 best-pump-on-route, route benchmarking | Structured route: origin/destination (city or pincode pair) + optional `highway_no[]`. Migrate lazily: G8/G6 can parse existing free text |
| 4 | **No delivered-vs-ordered quantity** | Short-delivery detection; forecast accuracy (full-tank orders have `quantity: 0`) | Add `delivered_qty` per product line on SO/at OTP verification; dealer keys in the dispensed reading (they have it on the DU display) |
| 5 | **No labels for "why deleted / disputed"** | Fraud model training, dispute analytics | Add enum `delete_reason` / `dispute_flag` to `order_msts`; one bottom-sheet picker in app |
| 6 | **OMS ↔ DIP not linked** | Cross-checking OTP-verified sales vs nozzle meter movement (the strongest anti-fraud signal we could own) | Shared `dealer_id` mapping table + timestamp alignment; no schema change in DIP needed initially |
| 7 | **No in-app behavioral events** | Churn features, funnel/adoption metrics, assistant quality loops | The [custom-mixpanel plan](../custom-mixpanel/00_README.md) — this is why it's Phase 0 |
| 8 | **English-only app, no i18n scaffolding** | Multilingual assistant/voice needs language prefs per user | Add `lang` to `users`; genAI can *respond* in any language regardless, but UI strings need i18n eventually |
| 9 | **No historical snapshot of credit-limit changes** | D2 limit-recommender can't learn from past limit adjustments | Append-only `cr_limit_history[]` on `dealer_custs` (or an events collection) — write on every change from now |

**The theme:** none of these are ML projects. They are **small schema + UI additions**. Do them in the next regular release and the data accumulates for free while we build Phase 1.

---

## 3. Feature Engineering We Can Do Today (no new data)

Concrete derived features, all computable with Mongo aggregations over existing collections:

### Payment behavior (per `dealer_custs` relation)
- **Days-to-pay distribution**: for each `FULLPAID` invoice, `pay_dt − inv_dt` of its settling vouchers (via `invs_adj[]`) → mean, p90, trend
- **Aging curve**: share of outstanding in 0–15 / 16–30 / 31–60 / 60+ day buckets
- **Payment-mode mix**: cheque-heavy relations behave differently from NEFT/RTGS relations (and cheques can bounce — `pay_status` reversals)
- **Utilization trajectory**: outstanding ÷ (`max_cr_lmt` + `adv_dep`) sampled weekly — slope matters more than level
- **Approval friction**: mean time from voucher creation to dealer approval (`pay_status` flip)

### Demand (per dealer, per relation, per vehicle)
- Daily/weekly litres by product category (`p_ctgy`), share of `is_full_tank` orders
- Inter-order interval per vehicle (`on_dt` deltas) → refuel cadence
- Seasonality: day-of-week, month, festival/harvest cycles (India-specific calendar features)

### Vehicle baselines
- Litres/day and ₹/day per `veh_id`, split by OWN/HIRED/SHARED (`veh_trns.relation`)
- Fill-size distribution per vehicle → z-score any new order against it (D6/T1 v0 without odometer)

### Price
- Dealer's rate vs district median rate per product per day (`rate_msts` join on geo) → competitiveness index

> Rule of thumb: **every model in doc 02 starts as one of these aggregations + a threshold.** Ship the heuristic, log its hits/misses, then train the model on the logged outcomes.

---

## 4. Storage & Pipeline Plan (minimal viable)

- **Feature store = MongoDB collections** (`ai_features_relation`, `ai_features_vehicle`, `ai_features_dealer_daily`), recomputed by **nightly cron jobs** (PM2 or node-cron in a worker process — same pattern as existing report generation). No new infra for Phase 1–2.
- **Time series**: `rate_msts` and `meter_reads` are already time-shaped; add compound indexes on `{dealer_id, date}` / `{cust_id, month}` as needed (follow `docs/ARCHITECTURE.md` indexing patterns).
- **Financial-year awareness**: all aggregations must respect the April–March FY and IST day boundary (18:30 UTC) exactly as `api_v3/services/dealer_custs.js` does — reuse those helpers, don't reimplement.
- **Labels**: create an `ai_outcomes` collection now (event-sourced: `{type: 'invoice_late' | 'voucher_bounced' | 'order_deleted' | 'anomaly_confirmed', refs, at, meta}`). Cheap to write, gold for training later.

---

## 5. Privacy, Tenancy & Compliance Guardrails

1. **Tenant isolation is non-negotiable.** Every AI query/feature is scoped by `dealer_id`/`cust_id` exactly like existing endpoints (`x-co-id` + membership checks). Cross-tenant learning (e.g., district rate benchmarks, credit-score priors) must use **aggregates only** — never expose one company's raw data to another. Benchmarks need k-anonymity (e.g., only show district median rate if ≥ 5 dealers contribute).
2. **DPDP Act 2023**: phone numbers (drivers!), addresses, and financial behavior are personal data. Consent language for AI processing goes into onboarding; driver phone numbers never leave our systems to third-party model APIs un-redacted.
3. **LLM data boundary**: when calling external LLM APIs (Claude), send **only the minimum context** for the task (see doc 03 §Grounding). Prefer IDs + aggregate numbers over raw PII; redact phone/GST/PAN where the task doesn't need them.
4. **Credit-score fairness & transparency**: scores affect livelihoods. Every score must ship with reason codes ("late on 4 of last 6 invoices", "utilization rose 3 weeks straight") — which conveniently is what makes them useful to dealers anyway.
5. **Retention**: `logs` grows unboundedly today; define TTL/archival before using it as a feature source (also an ops win).

---

## Next: [02 — Discriminative AI Features](02-discriminative-ai-features.md)
