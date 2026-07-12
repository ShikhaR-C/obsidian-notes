# 02 — Discriminative AI Features (Prediction, Scoring, Anomaly Detection)

> Discriminative AI answers: _given what we know, what is this — and what happens next?_ Every feature below follows the same recipe: **start as a Mongo aggregation + threshold (heuristic v0), surface it in the app, log outcomes, then train a real model** (logistic regression / gradient-boosted trees — nothing exotic) on the outcomes. Format per feature: what it does → data inputs → approach → where it surfaces → KPIs.

Personas: **D# = dealer-facing**, **T# = transporter-facing**, **P# = platform/both**.

---

## Dealer-Facing (petrol pump)

Dealers extend lakhs of rupees of credit on informal trust. Their two nightmares: **customers who don't pay** and **fuel that disappears**. D1–D7 attack both.

### D1 — Dzzlo Credit Score ⭐ flagship

**What:** A 0–100 score + A–E grade per `dealer_custs` relation predicting the probability of >15-day-late payment in the next billing cycle, with plain-language reason codes.

**Inputs (all existing):** days-to-pay history (`invs.inv_dt` vs settling `voc_msts.pay_dt` via `invs_adj[]`), aging buckets, utilization trajectory (`month_crdrs` + `max_cr_lmt` + `adv_dep`), payment-mode mix (cheque share), voucher reversals, order cadence changes, relationship age, `cust_blacklist`, `lysal/lypmt` turnover flags, opening balances (`cust_bal[]`).

**Approach:** v0 = weighted scorecard over §3 features from doc 01 (transparent, tunable). v1 = logistic regression → gradient-boosted trees once we have ~6 months of labeled cycles in `ai_outcomes`. Always emit top-3 reason codes; never a bare number.

**Surfaces:** grade chip on `Customers` list + `RelationList` credit bottom-sheet (app already renders credit donuts — `helpers/Credit/`); OneSignal alert on grade drop; feeds D2/D3/G4.

**KPIs:** default rate among "A" vs "E" relations (calibration); % of credit extended to A/B grades; dealer adoption (grade views before limit changes).

### D2 — Credit Limit & Terms Recommender

**What:** Recommends `max_cr_lmt`, `max_cr_days`, `cr_bill_period`, and advance-deposit ask per relation: "Based on 8 months of behavior, safe limit for Sharma Transport is ₹2.5L (currently ₹5L)" — or the opposite: "This A-grade customer is capped; raising to ₹4L could grow volume."

**Inputs:** D1 score + realized monthly volumes (`month_crdrs.drttl`), peak outstanding, seasonality, dealer's own risk appetite (learned from their past limit settings once `cr_limit_history[]` exists — doc 01 gap #9).

**Approach:** constrained optimization on top of D1's probability (expected margin on volume − expected loss). v0: quantile rules ("limit = 1.3 × p95 monthly purchase for grade ≥ B").

**Surfaces:** suggestion card inside `CustSettings` / `CreditLimitBS` where dealers already set limits; weekly digest email (SES) "3 limit reviews suggested".

**KPIs:** suggestion acceptance rate; bad-debt ₹ per ₹ credit extended, before vs after.

### D3 — Collections Prioritization

**What:** Every morning, a ranked worklist: "Collect these first" — invoices ordered by (amount at risk × probability of slipping past `max_cr_days`), with one-tap reminder send (pairs with G4).

**Inputs:** open `invs` (UNPAID/PARTPAID) aging, D1 score, customer's historical response to reminders (once G4 logs them), promised-pay dates if captured.

**Approach:** v0 needs no ML at all: `amount × age × (relation's late-rate)`. Survival model (time-to-payment) later.

**Surfaces:** new "Collections" section on dealer `Payments`/`Reports`; daily OneSignal digest at 10:00 IST.

**KPIs:** DSO (days sales outstanding) per dealer; % of 30+ day invoices; reminder→payment conversion.

### D4 — Pump Demand Forecast & Tank Refill Planner

**What:** 7-day demand forecast per product per pump; converts to "order your next tanker by Thursday" using DIP tank levels — prevents both dry-outs (lost sales, angry fleet customers) and over-holding (working capital, evaporation).

**Inputs:** OMS sales series (`so_msts`/`invs` daily litres), DIP `meter_reads` (per-tank `c_dip`, per-nozzle `c_mtr` — actual dispensed volumes), `decants` (replenishment lead times), tank `capacity`/`deadwood`, day-of-week/festival calendar, local rate changes.

**Approach:** v0 = seasonal moving average per weekday. v1 = classical time-series (ETS/Prophet-style) per pump-product; reorder point = forecast over lead time + safety stock. This is textbook inventory optimization, not deep learning.

**Surfaces:** dealer dashboard card "HSD: ~4.2 days of stock left"; OneSignal alert at reorder point; DIP web (`dip-web`) gets the full planner view.

**KPIs:** stockout-days per pump; forecast MAPE; dealer retention on DIP module.

### D5 — DIP Shrinkage / Pilferage Detection ⭐ flagship

**What:** Flags abnormal stock variance per tank/nozzle: pilferage, meter drift, short decants (tanker delivered less than invoiced), leaks. "Tank 2 (HSD): cumulative variance −0.42%/day over 9 days — 3× your normal. Check nozzle 5 calibration and last decant."

**Inputs:** `insps` reconciliation (book vs physical dip), `meter_reads` (`c_test` — test pours, `c_mtr`), `decants` (invoiced `rcvd_qty` vs dip-measured received, before/after nozzle totals), nozzle stamping/renewal dates, temperature seasonality (diesel expands ~0.08%/°C — naive dips mis-read in summer).

**Approach:** statistical process control (CUSUM/EWMA control charts per tank) — deliberately _not_ a black box, because accusations of theft need defensible math. Classify variance signatures: step change after a decant = short delivery; gradual drift on one nozzle = calibration; overnight drops = pilferage window.

**Surfaces:** DIP inspection screen + severity-ranked alert feed; weekly variance report email.

**KPIs:** confirmed-incident rate on flags (precision); ₹ variance recovered; false-alarm rate < 1/pump/month (alert fatigue kills this feature).

### D6 — Order Fraud & Anomaly Guard

**What:** Real-time checks at order placement and OTP verification: quantity way above vehicle's historical fill or (once captured) tank capacity; duplicate order for same vehicle within hours; unusual hour; full-tank abuse patterns; OTP repeatedly sent to "emergency" path; a vehicle fueling at two distant dealers the same day.

**Inputs:** `order_msts` history per `veh_id`, per-vehicle fill distribution (doc 01 §3), `otp_by.personType/response`, dealer/customer coords, `veh_trns` status.

**Approach:** pure rules + per-vehicle z-scores in v0, running inside the existing `canTransact()`/order-create path in `api_v3/services/order_msts.js` as **soft warnings** (never hard blocks initially). Isolation-forest style scoring later if rule precision is proven.

**Surfaces:** inline warning in the app's `NewOrder`/dealer order screen ("This is 2.7× MH12AB1234's usual fill — confirm?"); flags on `OneOrder` detail; audit trail feeds `ai_outcomes`.

**KPIs:** confirmed-anomaly precision; disputed/deleted-order rate on flagged vs unflagged.

### D7 — Customer Churn Early-Warning

**What:** Flags relations whose order cadence is decaying ("Gupta Roadlines: 12 orders/month → 3; last order 19 days ago; likely moved to another pump") with a win-back suggestion (pair with D2 limit raise or discount review).

**Inputs:** order frequency/recency/volume trends per relation, app activity from `logs` (customer stopped opening the app vs stopped buying _here_), rate competitiveness (P1), credit friction events (orders blocked at limit).

**Approach:** v0 = RFM decay rules; v1 = survival/hazard model. The interesting signal is _why_: blocked-at-limit events preceding churn → the fix is D2, not marketing.

**Surfaces:** "At risk" section in dealer `Customers`; monthly business review (G5) narrative.

**KPIs:** win-back rate on flagged relations; revenue retention.

---

## Transporter-Facing (truck owners / fleet operators)

Transporters' #1 leak is **fuel theft/misuse** (industry folklore says 5–15% of fuel spend); #2 is credit opacity across multiple pumps. T1–T5 are the fleet-intelligence suite — and a genuine differentiator: DZZLO sees _purchases at the pump with OTP-verified delivery_, which telematics-only tools don't.

### T1 — Vehicle Fuel-Consumption Anomaly (fuel-theft detection) ⭐ flagship

**What:** Per-vehicle consumption baseline + outlier alerts: "MH12AB1234 consumed ₹18,400 of diesel this week — 46% above its 12-week baseline for similar order cadence. 2 fill-ups look abnormal (list)." With odometer capture (doc 01 gap #1) this upgrades to true km/l mileage tracking per vehicle and per driver.

**Inputs:** `order_msts` per `veh_id` (litres, ₹, `on_dt`, `is_full_tank`), assigned driver (`dvr_id` on SO), `veh_trns` (OWN/HIRED/SHARED), later `odometer` + `tank_capacity`.

**Approach:** v0 = per-vehicle EWMA of litres/day and fill-size z-scores; flag > 2.5σ. v1 with odometer = regression of consumption on km/route/load class; residuals are the theft signal. Full-tank orders (qty 0) handled via `delivered_qty` (doc 01 gap #4).

**Surfaces:** vehicle detail (`InfoVehicle` bottom sheet → new "Fuel Health" tab); weekly fleet digest push; anomaly list with driver + pump context.

**KPIs:** fuel ₹/vehicle/month trend after adoption; % anomalies confirmed by owner; feature-driven retention (this is a feature transporters would _pay_ for).

### T2 — Refuel Prediction & Smart Reorder

**What:** Predicts each truck's next refuel window ("MH12AB1234 likely needs diesel tomorrow") and offers a pre-filled order draft (vehicle, usual pump, usual quantity) — one tap to place. Reduces the 6-step `NewOrder` flow to a confirmation for routine fills.

**Inputs:** inter-order intervals per vehicle, weekday patterns, route (when structured), credit headroom (T4).

**Approach:** v0 = per-vehicle median cadence timer; v1 = gradient-boosted classifier "will refuel within 24h". Precision matters less here — it's a convenience nudge, not an alarm.

**Surfaces:** OneSignal push with deep link into pre-filled `NewOrder`; "due for refuel" badges on `Vehicles`.

**KPIs:** % orders placed via prediction; order-placement time; push opt-out rate (guardrail).

### T3 — Best-Pump Recommendation on Route

**What:** For a vehicle/route, ranks the transporter's connected dealers (and discoverable verified dealers — P2) by effective cost + convenience: today's rate (`rate_msts`), per-product discounts on the relation, credit headroom, highway proximity (`highway_no`, coords), and reliability (OTP/dispute history).

**Approach:** deterministic scoring function first (it's a ranking over ~5–20 options, not a learning problem until we have click/selection feedback). Learning-to-rank later from selection logs.

**Surfaces:** `SelectDealer` bottom-sheet in `NewOrder` gets a "recommended" sort + "₹0.35/L cheaper than your usual" chips.

**KPIs:** recommendation take-rate; ₹ saved shown vs realized.

### T4 — Credit Headroom Forecast

**What:** "At current pace you'll hit your ₹3L limit with Verma Fuels around July 9 — 2 invoices totaling ₹85k due before that; pay by July 7 to keep ordering." Prevents the worst UX in the product: a truck stranded at a pump because the order was blocked at the credit limit.

**Inputs:** outstanding + open orders (the same math as the existing credit check in `order_msts` service), spend velocity, upcoming `inv_term` due dates, historical payment cadence.

**Approach:** v0 = linear burn-rate projection — deliberately simple and explainable. It's the _packaging_ (proactive push before the block happens) that's new.

**Surfaces:** `CreditProgressORDER` panel (already in `NewOrder`), relation credit sheet, proactive OneSignal at T-3 days.

**KPIs:** blocked-order attempts (should fall); on-time payment rate (dealers benefit too — this feature sells to both sides).

### T5 — Driver Reliability Score

**What:** Per-driver rollup: OTP response success/latency (`otp_by.response`), involvement in T1 anomalies, order-deletion rate on their fills, cadence regularity. Not a surveillance tool — a shortlist aid for assigning drivers to hired/shared vehicles (`veh_reqs` marketplace) where the owner doesn't know the driver.

**Approach:** transparent scorecard only. No black-box scoring of individuals; show the components, let the owner judge. (See fairness notes, doc 01 §5.)

**Surfaces:** `InfoDriver` bottom sheet; optional badge in the hire/rent marketplace flow.

**KPIs:** anomaly rate on high-score vs low-score drivers; marketplace conversion.

---

## Platform / Both Sides

### P1 — Fuel Rate Intelligence

**What:** For dealers: "your HSD rate is ₹0.40 above district median; you lost 2 high-volume customers' orders on rate-sensitive days." For transporters: rate trend sparkline per dealer and "rates in your district rose ₹0.25 this week." Note: bulk/pump diesel pricing in India is OMC-influenced but dealer-variant — the _relative_ benchmark is the value, not absolute prediction.

**Inputs:** `rate_msts` across dealers (aggregated with k-anonymity ≥ 5 dealers per benchmark — doc 01 §5), geo (`district`, `highway_no`), order volumes around rate changes.

**Approach:** pure aggregation + simple elasticity regression (volume response to relative rate). Sparklines render fine in the app's custom SVG (no chart lib needed).

**Surfaces:** dealer `RateSetter` screen (benchmark chip at the moment of setting the daily rate — perfect placement); transporter dealer-list.

**KPIs:** rate-setting engagement; volume-weighted competitiveness of dealers on platform.

### P2 — Dealer ↔ Transporter Matchmaking

**What:** Recommends new verified connections: transporters whose routes/geo cluster near a dealer ("14 verified transporters operate on NH-48 near you; 5 match your credit profile"), and vice versa. Extends the existing invite/relation flow and the vehicle hire/share marketplace into a discovery engine — this is the network-effects play for DZZLO growth.

**Inputs:** coords, `highway_no`, order volumes, D1 grades (shared as coarse bands with consent, never raw history), `veh_reqs` graph.

**Approach:** geo + graph heuristics (collaborative filtering once the graph is dense enough).

**Surfaces:** "Discover" section in `Dealers`/`Customers` screens; invite suggestions.

**KPIs:** new verified relations per month attributable to suggestions; GMV of suggested relations.

### P3 — Platform Ops Anomaly Detection (internal)

**What:** For VSYST: anomaly detection over the `logs` collection (error-rate spikes per endpoint, latency regressions per app version, OTP delivery failures per telecom circle via `otp_by.response`) and abuse detection (credential stuffing, scraping). Cheap to build, protects everything else.

**Approach:** EWMA thresholds per endpoint/version; alert to superadmin email/console. Pairs with the version-gate machinery for targeted force-updates.

---

## Summary Table

| Feature              | v0 (weeks, no ML)       | v1 (with ML)                  | Blocking data gap                        |
| -------------------- | ----------------------- | ----------------------------- | ---------------------------------------- |
| D1 Credit Score      | weighted scorecard      | GBT classifier                | none (labels accrue via `ai_outcomes`)   |
| D2 Limit Recommender | quantile rules          | expected-value optimization   | `cr_limit_history` (gap 9)               |
| D3 Collections       | amount×age×late-rate    | survival model                | none                                     |
| D4 Demand/Refill     | seasonal averages       | time-series model             | OMS↔DIP link (gap 6)                     |
| D5 Shrinkage         | control charts          | variance-signature classifier | none (DIP has it)                        |
| D6 Order Guard       | rules + z-scores        | isolation forest              | tank capacity (gap 2)                    |
| D7 Churn             | RFM decay               | hazard model                  | analytics events (gap 7)                 |
| T1 Fuel Anomaly      | EWMA + z-scores         | mileage regression            | odometer (gap 1) ← _start capturing now_ |
| T2 Refuel Predict    | cadence timer           | 24h-refuel classifier         | none                                     |
| T3 Pump Ranking      | scoring function        | learning-to-rank              | structured route (gap 3)                 |
| T4 Headroom Forecast | burn-rate projection    | — (simple is right)           | none                                     |
| T5 Driver Score      | transparent scorecard   | — (keep transparent)          | none                                     |
| P1 Rate Intelligence | aggregation + benchmark | elasticity regression         | none                                     |
| P2 Matchmaking       | geo/graph heuristics    | collaborative filtering       | none                                     |

**Next: [03 — Generative AI Features](03-generative-ai-features.md)** — where these scores and forecasts get voices, explanations, and hands.
