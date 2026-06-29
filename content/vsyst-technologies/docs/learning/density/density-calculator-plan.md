# Density Calculator for Diesel & Petrol — Plan

Planning document for a density module inside the dzzloOMS DIP stack. Goal: capture, correct, and validate product density during tank-truck (TT) decantation at a retail outlet (RO) so that stock reconciliation is mass-correct and adulteration / short-supply is detectable.

Owner: TBD. Related model: [`dzzlo_oms_api/models/dip_models/decants.js`](../../../dzzlo_oms_api/models/dip_models/decants.js). Current date: 2026-04-16.

---

## 0. TL;DR

1. Every TT load of MS/HSD carries an **invoice density at 15 °C** printed on the tanker challan. At the RO, the dealer draws a top sample, measures **observed density** and **observed temperature** with a hydrometer + thermometer (IS 1448 P:16 / ASTM D1298), corrects to 15 °C, and compares with invoice density.
2. We do **not** need a per-product density _chart_ in the old "printed lookup" sense — each TT has its own density (per batch / supply location / season). What we need is:
   - A **correction formula** (ASTM D1250-80 / IS 1448 P:16) to move observed → 15 °C.
   - A **per-product acceptable range** (IS 2796 for MS, IS 1460 for HSD) to flag physically implausible values.
   - A **per-decant tolerance** (typically ±3 kg/m³) against the _invoice_ density to flag short-supply/adulteration.
3. Yes, a formula exists — two are usable:
   - **Linear field approximation**: `ρ₁₅ = ρₜ × [1 + α × (t − 15)]` with α≈0.00112/°C for petrol, ≈0.00083/°C for diesel. Good to ±0.5 kg/m³.
   - **ASTM D1250-80 closed-form** (iterative, converges in 2–4 passes, accurate to ±0.1 kg/m³). This is what invoice densities are computed with and what we should use in code.
4. Decants schema needs three new things per tank entry: `observed_density`, `observed_temp`, `density_15c` (derived), plus invoice-side `inv_density_15c`. A new master (`prod_density_specs`) holds the IS-2796/IS-1460 acceptable range per product.
5. Volume-at-15 °C (via **VCF**) is a second-order benefit: optional in Phase 1, mandatory before we claim stock accuracy.

---

## 1. Domain research — how density works in Indian fuel retail

### 1.1 Decantation flow (what actually happens on the ground)

Per IOCL Marketing Discipline Guidelines (MDG 2024) and BPCL Industry Quality Control Manual (IQCM 2019):

1. TT arrives at RO with a **Tanker Lorry Invoice / Delivery Challan** that carries:
   - `inv_no`, `tt_no`, compartment-wise quantity (observed and at 15 °C), **density at 15 °C**, observed density, observed temperature at loading.
2. Dealer / attendant breaks the seal, does a **top-sample draw** from each compartment into a 500 ml glass jar (density kit).
3. **Hydrometer** (IS 3104 / IS 1448 P:16 range-specific — one for MS ~700-750, one for HSD ~800-850) is floated in the jar; **thermometer** (IS 4825) measures sample temperature simultaneously.
4. Reading: observed density `ρₜ` at temperature `t`.
5. **Correct to 15 °C** using either IS 1448 P:16 tables (paper) or ASTM D1250 / API MPMS Ch 11.1 equations (software).
6. Compare `ρ₁₅` (RO-measured) against `ρ₁₅` (invoice). If within tolerance → decant. If out of tolerance → seal samples, call OMC rep, do not decant until cleared.
7. Dip tank before & after. Record `start_dip`, `end_dip`, difference vs invoice quantity.
8. Density readings go into the **Dealer Density Register** (statutory — maintained for inspection).

### 1.2 Standards that govern this

| Standard                                      | Scope                                                                                                                                             |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **IS 1448 Part 16** (1990 / 2014)             | Test method for density by hydrometer, and the correction-to-15 °C procedure. The Indian mirror of ASTM D1298 + ASTM D1250 tables.                |
| **IS 2796** (2017)                            | MS / Petrol product spec. Density at 15 °C: **720 – 775 kg/m³**.                                                                                  |
| **IS 1460**                                   | HSD / Diesel product spec. Density at 15 °C: typical **820 – 845 kg/m³** (BS VI). Some references cite 820–860 or 820–870 across BS stages.       |
| **ASTM D1298 / IP 160**                       | International equivalent of IS 1448 P:16 (hydrometer method).                                                                                     |
| **ASTM D1250 / API MPMS Ch 11.1**             | Petroleum Measurement Tables — how to correct observed → 15 °C (or 60 °F). Recognises three commodity groups: crude, refined products, lube oils. |
| **OISD-225**                                  | Decantation procedure checklist reference.                                                                                                        |
| **IOCL MDG 2024 / BPCL IQCM 2019 / HPCL MDG** | Operational SOPs for dealers, including density-register and out-of-tolerance handling.                                                           |

### 1.3 Product density ranges (for input-validation only)

| Product                      | IS spec range @ 15 °C (kg/m³)                                          |
| ---------------------------- | ---------------------------------------------------------------------- |
| MS / Petrol (IS 2796)        | 720 – 775                                                              |
| XP / Premium MS              | same envelope as MS (branded variants stay inside IS 2796)             |
| HSD / Diesel (IS 1460)       | 820 – 845 (BS VI)                                                      |
| Ethanol-blended MS (E10/E20) | slightly higher than plain MS; E20 typically 735–780 (verify with OMC) |
| SKO / Kerosene               | 780 – 810                                                              |
| ATF                          | 775 – 840                                                              |

These ranges are **product-level plausibility guards**, not per-batch. The _actual_ invoice density for a given TT varies within this envelope.

### 1.4 Do we need a density chart per product? — NO, but we need two reference tables

- **Per-product acceptable range** (IS 2796 / IS 1460) — to reject typos and grossly implausible readings. Stored once per product.
- **Per-product thermal expansion coefficient (α)** and/or **ASTM D1250 K-constants (K0, K1)** — to compute the 15 °C correction. Stored once per product group (gasoline, kerosene/jet, diesel, lube).

We do **not** need, and should not store, a pre-computed chart of ρ vs T for every product. That's what the formula is for.

### 1.5 Tolerance limits (Density Variation Allowance, DVA)

- **Invoice ρ₁₅ vs RO-measured ρ₁₅** — field practice at Indian OMCs: **±3 kg/m³** (0.003 g/mL) is the commonly cited acceptable band. Beyond this triggers sample retention + OMC notification.
- **Per-product IS range** — any reading outside IS 2796 (720–775) or IS 1460 (820–845) is physically suspect — block the decant.
- _These exact numbers should be verified against the RO's binding OMC SOP before being hard-coded as block-level constants._

### 1.6 Density as a fraud / loss signal

- **Diesel density too low** (e.g. 800 kg/m³ instead of 830) → probable kerosene adulteration.
- **Petrol density too high** (e.g. 790 kg/m³ instead of 745) → possibly water / heavier contaminant.
- **Petrol density higher than invoice by > tolerance** → likely evaporation loss in transit (MS is volatile) or measurement error.
- **Density trending across TTs from the same supply location** → supply-side issue.

Academic note: density alone is an imperfect adulteration indicator at low adulteration levels (see PMC 2024 literature); it's good for gross checks, not trace contamination. The module should flag but not quarantine on density alone.

---

## 2. The math

### 2.1 Observed vs standard density

- `ρₜ` — observed density (kg/m³) at observed temperature `t` (°C). Ambient is 25–40 °C in India.
- `ρ₁₅` — density at 15 °C. **This is the value on invoices and in all statutory records.**
- Conversion: use ASTM D1250 or its linear approximation.

### 2.2 Linear field approximation

```
ρ₁₅ = ρₜ × [1 + α × (t − 15)]
```

| Product      | α (per °C) |
| ------------ | ---------- |
| MS / Petrol  | 0.00112    |
| HSD / Diesel | 0.00083    |
| SKO          | 0.00090    |
| ATF          | 0.00095    |

Accuracy: ±0.5 kg/m³ over 10–45 °C. Acceptable for field/UI pre-calc, not for statutory records.

### 2.3 ASTM D1250-80 closed-form (recommended for persisted values)

```
α₁₅ = (K0 / ρ₁₅²) + (K1 / ρ₁₅)
VCF = exp[ −α₁₅ × ΔT × (1 + 0.8 × α₁₅ × ΔT) ]
ρ₁₅ = ρₜ / VCF             (iterate until Δρ₁₅ < 0.05 kg/m³)
```

where ΔT = t − 15 (°C) and K-constants are:

| Commodity group             | ρ₁₅ range (kg/m³) | K0       | K1     |
| --------------------------- | ----------------- | -------- | ------ |
| Gasolines / naphthas (MS)   | 653 – 770.5       | 346.4228 | 0.4388 |
| Jet / kerosenes (SKO, ATF)  | 770.5 – 788       | 594.5418 | 0      |
| Diesel / heating oils (HSD) | 788 – 839         | 186.9696 | 0.4862 |
| Crude oil                   | 610.6 – 1075      | 341.0957 | 0      |
| Lube oils                   | 839 – 1075        | 0        | 0.6278 |

Reference JS implementation (~30 LOC, no deps):

```js
// dzzlo_oms_api/helpers/density.js  (proposed)
const K = {
  MS: { K0: 346.4228, K1: 0.4388 }, // gasoline band
  HSD: { K0: 186.9696, K1: 0.4862 }, // diesel band
  SKO: { K0: 594.5418, K1: 0 },
  ATF: { K0: 594.5418, K1: 0 },
};

function correctTo15C(rhoT, tCelsius, group = "HSD") {
  const { K0, K1 } = K[group];
  const dT = tCelsius - 15;
  let rho15 = rhoT;
  for (let i = 0; i < 6; i++) {
    const alpha = K0 / (rho15 * rho15) + K1 / rho15;
    const vcf = Math.exp(-alpha * dT * (1 + 0.8 * alpha * dT));
    const next = rhoT / vcf;
    if (Math.abs(next - rho15) < 0.01) {
      rho15 = next;
      break;
    }
    rho15 = next;
  }
  const alpha = K0 / (rho15 * rho15) + K1 / rho15;
  const vcf = Math.exp(-alpha * dT * (1 + 0.8 * alpha * dT));
  return { rho15: +rho15.toFixed(1), vcf: +vcf.toFixed(5) };
}

module.exports = { correctTo15C };
```

### 2.4 Volume Correction Factor (VCF)

Same `α₁₅` as above, but applied to volume:

```
V₁₅  = Vₜ × VCF            (volume at 15 °C = observed × VCF)
ρ₁₅  = ρₜ / VCF
Mass = V₁₅ × ρ₁₅ = Vₜ × ρₜ   (sanity check — mass conserved)
```

For t > 15 °C, VCF < 1 (fuel shrinks when cooled to 15 °C). Use VCF when we want stock reported in 15 °C litres (the OMC-facing number) vs observed litres (the customer-facing dispenser number).

### 2.5 Worked examples

**A. Diesel** — ρₜ = 820 kg/m³ at 32 °C, group=HSD:

- α₁₅ ≈ 0.000871 /°C → VCF ≈ 0.98513 → **ρ₁₅ ≈ 832.3 kg/m³** (converges in 2 iterations)
- Linear check: 820 × (1 + 0.00083×17) = 831.6 — off by 0.7.

**B. Petrol** — ρₜ = 735 kg/m³ at 28 °C, group=MS:

- α₁₅ ≈ 0.001238 /°C → VCF ≈ 0.98384 → **ρ₁₅ ≈ 747.0 kg/m³**
- Linear check: 745.7 — off by 1.3.

**C. Diesel low-ΔT** — ρₜ = 835 at 20 °C:

- α₁₅ ≈ 0.000850 → VCF ≈ 0.99574 → **ρ₁₅ ≈ 838.6 kg/m³**

---

## 3. Codebase audit — where this lands

### 3.1 Current `decants` schema (as of 2026-04-16)

File: `dzzlo_oms_api/models/dip_models/decants.js`

```js
decants: {
  dealer_id, decan_dt, inv_no, inv_dt, tt_no, rcvd_qty,
  tanks:   [{ tank_id, prod_id, serial_no, rcvd_qty,
              start_dip, start_time, end_dip, end_time, diff }],
  nozzles: [{ nzl_id, du_id, tank_id, prod_id, before_decan, after_decan }],
}
```

No density, no temperature, no 15 °C correction.

### 3.2 Related models (existing)

- `models/prod_msts.js` — product master. Has `name, unit, hsn, gst_rate`. **No density fields.**
- `models/dip_models/dealers.js` — holds `tanks_Schema` (tank geometry: dia, length, deadwood, capacity) and `nozzles_Schema`. No calibration/dip-chart curve.
- `models/dip_models/insps.js`, `meter_reads.js` — track `c_dip` (computed dip) and `c_rcvd` but no density/temp.
- `models/invs.js` — billing invoice, separate from TT invoice. Does **not** carry density.
- No standalone TT / challan model; TT info is flattened into `decants.{inv_no, inv_dt, tt_no, rcvd_qty}`.

### 3.3 Gaps identified

1. No observed / reference density at decant time.
2. No invoice-side density anchor to compare against.
3. No temperature at time of measurement.
4. No per-product plausibility range (IS 2796 / IS 1460) anywhere.
5. No dip-chart / tank calibration table → volume-at-15 °C reconciliation is not currently possible, only qualitative diff against invoice quantity.
6. No density register / audit log.

### 3.4 Project conventions to follow (from `dzzlo_oms_api/AI.md`)

- `snake_case` field names, `ObjectId` for refs, `{ timestamps: true }` at top level, `{ _id: false }` on subdocs.
- DIP models live under `models/dip_models/` and use `db_dip` connection.
- Controllers wrap in `asyncHandler`, errors via `next(new ErrorResponse(...))`, permissions via `checkDipPerm(entity, action)`.
- **Active development goes in `api_v3/` with the services layer** — do not extend `api_v1/` or `api_v2/`. DIP currently still routes through `dip_api_v1/`.
- Validation is schema-level (Mongoose `runValidators: true`); no Joi.
- Numbers often rounded via setter `v => Math.round(v*100)/100`.

---

## 4. Proposed data-model changes

### 4.1 Extend `decants.tanks[]` subdoc

```js
tanks: [
  {
    ...existing,
    // invoice side (what OMC printed on the challan for this compartment)
    inv_density_15c: { type: Number }, // kg/m³
    inv_observed_density: { type: Number }, // kg/m³ (optional, sometimes printed)
    inv_observed_temp: { type: Number }, // °C (optional)
    inv_qty_15c: { type: Number }, // litres (optional — OMC corrected qty)

    // RO-measured side (what the dealer observed at decant time)
    obs_density: { type: Number, min: 600, max: 900 }, // kg/m³ at obs_temp
    obs_temp: { type: Number, min: -5, max: 60 }, // °C
    density_15c: { type: Number }, // derived from obs_density + obs_temp
    vcf: { type: Number }, // derived
    rcvd_qty_15c: { type: Number }, // derived from rcvd_qty × VCF

    // audit & variance
    density_variance: { type: Number }, // density_15c − inv_density_15c
    density_status: { type: String, enum: ["OK", "WARN", "REJECT", "PENDING"] },
  },
];
```

All `density_*` / `vcf` / `rcvd_qty_15c` should be computed server-side in the controller (or a `decants.service.js`) rather than accepted from the client — this is the job of the density helper (§2.3).

### 4.2 New master: `prod_density_specs`

Keeps per-product validation envelope + correction constants. One row per product (or per product group, linked by `prod_id`).

```js
// models/prod_density_specs.js   (new, non-DIP — product metadata)
{
  prod_id:       { type: ObjectId, ref: 'prod_msts', required: true, unique: true },
  group:         { type: String, enum: ['MS','HSD','SKO','ATF','LUBE','CRUDE'], required: true },
  min_density_15c: { type: Number, required: true },  // e.g. 720 for MS
  max_density_15c: { type: Number, required: true },  // e.g. 775 for MS
  is_spec_ref:   { type: String },   // e.g. 'IS 2796:2017' / 'IS 1460'
  alpha:         { type: Number },   // linear-approx α (optional, display only)
  K0:            { type: Number },   // ASTM D1250 constants
  K1:            { type: Number },
  source_note:   { type: String },
}
```

Seeded (not user-edited) from a fixture in `test/api_v3/temp/seed/...` or a one-off script.

### 4.3 Extend `prod_msts` (optional, lighter alternative)

If we don't want a new collection, add `density_group: String` (enum MS/HSD/...) directly to `prod_msts` and keep the K0/K1 table in code (`helpers/density.js`). Recommended for v1 — cheaper, fewer moving parts.

### 4.4 Optional: density observation log

If we want a separate audit trail (for inspectors / density register export):

```js
// models/dip_models/density_logs.js   (new)
{
  dealer_id, decan_id (ref: decants),
  tank_id, prod_id,
  measured_by_user_id,
  measured_at,
  obs_density, obs_temp, density_15c, vcf,
  inv_density_15c, variance, status,
  hydrometer_serial, thermometer_serial,
}
```

Deferred to Phase 7. Keeps `decants` the single source of truth in Phase 1.

---

## 5. Phased implementation plan

### Phase 1 — Reference data & the calculator (isolated, low risk)

1.1. Create `helpers/density.js` exporting `correctTo15C(rhoT, t, group)` and `computeVCF(rhoT, t, group)`.
1.2. Ship unit tests (Jest) against the three worked examples in §2.5 plus edge cases (t=15, t=0, convergence failure).
1.3. Add `density_group` to `prod_msts` schema (string, enum) — minimal migration: existing docs default to null, backfill via script for seeded products (MS/HSD).
1.4. Constants table (K0/K1, α, IS ranges) lives in `helpers/density.constants.js`.

### Phase 2 — Schema extension on `decants`

2.1. Edit `models/dip_models/decants.js` — add the new fields from §4.1 to `tanks_Schema`. All optional; no impact on existing data.
2.2. Add Mongoose pre-save hook (or move to service layer) that: if `obs_density` and `obs_temp` are both set but `density_15c` is not → compute. If `inv_density_15c` is set → compute `variance` and `status`.
2.3. No migration required (new fields are optional, unset on legacy docs).

### Phase 3 — DIP API surface (read/write density)

3.1. Extend `dip_api_v1/controllers/decants.js`:

- `AddDecan` / `UpdateDecan` — accept new fields, run through density helper before save.
- `GetOne` / `GetMultiple` — include new fields in projection; populate product spec for UI.
  3.2. Add a helper endpoint `POST /decants/quick-density` that takes `{obs_density, obs_temp, prod_id}` and returns `{density_15c, vcf}` without persisting — for live UI preview as dealer types readings.
  3.3. Validation: if `obs_density` is outside the product's `[min_density_15c, max_density_15c]` corrected envelope, block with 400. If `variance > tolerance`, save with `status='WARN'` but do not block (let dealer confirm / add remarks).

### Phase 4 — `api_v3` parity (per AI.md rule)

4.1. Mirror Phase 3 into `api_v3/controllers/decants/` + `api_v3/services/decants.service.js` + `api_v3/routes/decants.js` so future work stays in v3.
4.2. The service layer is where the density helper is actually called; controller stays thin.
4.3. Unit-test the service against Phase 1's helper.

### Phase 5 — UI wire-up (dzzlo_oms_app)

5.1. Decantation form: add per-tank rows for `obs_density`, `obs_temp`; show live `density_15c` via `/quick-density` endpoint.
5.2. Surface invoice-side fields for the user to type off the challan: `inv_density_15c`, optionally `inv_observed_density/temp`.
5.3. Show **status badge**: OK / WARN / REJECT based on variance + envelope.
5.4. Block "Save" when any tank row has REJECT status unless an override reason is captured.

### Phase 6 — Alerts & reporting

6.1. Daily digest: any decant with `density_status = 'WARN' | 'REJECT'` → email/Slack to dealer + area manager.
6.2. Density-variance trend per supply location (bucket by `inv_dt` + supply origin if we capture it).
6.3. Export: monthly **Dealer Density Register** PDF/CSV — maps to OMC statutory requirement.

### Phase 7 — Volume reconciliation at 15 °C (deeper accuracy)

7.1. New model `tank_calibration.js` — per-tank dip→volume curve. Tank calibration is normally done by OMC with a master measure; we store the resulting curve as `[{dip_mm, volume_l}]` or as the coefficients of the geometric fit.
7.2. `meter_reads` / `insps` get `c_rcvd_15c` and `c_stock_15c` companion fields.
7.3. Reconciliation report: invoice qty @ 15 °C vs dip-derived qty @ 15 °C → proper short-supply detection.

### Phase 8 — Optional density-log audit trail

8.1. Add `density_logs` collection (§4.4).
8.2. Export endpoint for inspection / OMC audit.

### Phase 9 — Migration & backfill

9.1. One-off script `scripts/seed_prod_density_group.js` — sets `density_group` on every existing `prod_mst` based on product name.
9.2. No backfill of historical `decants` — legacy docs keep null density; only new decants carry values.

### Phase 10 — Testing & documentation

10.1. Jest: `helpers/density.test.js`, `decants.service.test.js`, controller integration tests.
10.2. Update `docs/AI_CONTEXT.md` with new fields and the helper's contract.
10.3. Update `docs/ARCHITECTURE.md` with the Phase 7 calibration story.
10.4. Add `docs/learning/density/` notes linking here for onboarding.

---

## 6. Open questions (need to confirm before coding)

1. **Tolerance hard-coding** — is ±3 kg/m³ the actual DVA in the RO's OMC SOP? Confirm by reading the binding MDG clause and have the number as a config constant, not a literal.
2. **Reference temperature** — 15 °C is industry default. Any legacy invoices still quoting 29.5 °C / 30 °C? If so we need a mode flag.
3. **Per-compartment density** — TTs usually have 3–4 compartments, each potentially a different product/batch. Our `tanks[]` array already models per-compartment; confirm invoice printing matches this.
4. **Premium branded products** (XP95, Speed, Power) — same IS 2796 envelope or tighter spec from the brand owner?
5. **Ethanol blending** — with E20 rollout, does MS density spec widen? Confirm current IS 2796 revision.
6. **Who owns density_group seeding** — ops team, or part of product master creation flow?
7. **Override flow** — if dealer sees WARN/REJECT but OMC verbally clears the decant, do we allow save-with-remark or strictly block? (Statutory implications — prefer save-with-remark + audit log.)
8. **Dip-chart ownership** (Phase 7) — OMC supplies tank calibration; we just store it. Agree a CSV import format per tank.

---

## 7. References

Open standards & regulatory:

- Bureau of Indian Standards — **IS 1448 Part 16 (1990)**, Methods of test for petroleum and its products: Density, Relative Density or API Gravity by Hydrometer. [law.resource.org mirror](https://law.resource.org/pub/in/bis/S11/is.1448.16.1990.pdf) · [BIS preview](https://standardsbis.bsbedge.com/BIS_Preview.aspx?id=1448_16) · [Internet Archive](https://archive.org/details/gov.in.is.1448.16.1990)
- BIS — **IS 1448 Part 16 : 2014** revision. [SAI Global catalog entry](https://infostore.saiglobal.com/en-us/standards/bis-is-1448-16-2014-185508_saig_bis_bis_446262/)
- ASTM — **D1298** Standard Test Method for Density, Relative Density, or API Gravity of Crude Petroleum and Liquid Petroleum Products by Hydrometer Method. [store.astm.org](https://store.astm.org/standards/d1298)
- ASTM — **D1250-19** / API MPMS Ch 11.1 Standard Guide for the Use of the Petroleum Measurement Tables. [store.astm.org/d1250-19e01.html](https://store.astm.org/d1250-19e01.html) · [historical D1250-04](https://www.astm.org/DATABASE.CART/HISTORICAL/D1250-04.htm)
- Transport Policy India — Diesel & Gasoline standards (Bharat Stage density ranges). [transportpolicy.net](https://www.transportpolicy.net/standard/india-fuels-diesel-and-gasoline/)
- Petroleum Planning & Analysis Cell (PPAC), MoPNG — product spec FAQs. [ppac.gov.in/faqs](https://ppac.gov.in/faqs)

OMC operational documents:

- Indian Oil — **Marketing Discipline Guidelines (MDG) 2024**, Ver. 1 / 24.10.2024. [iocl.com PDF](https://iocl.com/uploads/Marketing_Discipline_Guideline_2024_24_10_2024.pdf) · [earlier 2022 Ver. 7](<https://www.hindustanpetroleum.com/documents/pdf/Retail_Marketing_Discipline_Guidelines_(MDG)_2012.pdf>) · [2014 Ver. 3](https://iocl.com/uploads/MDG_22122014.pdf) · [2013 version](https://iocl.com/uploads/MDG_11jan2013.pdf) · [2012 version](https://iocl.com/download/MDG_2012.pdf)
- Bharat Petroleum — **Industry Quality Control Manual 2019** (IQCM). [mirror PDF](https://mrblendapp.s3.ap-south-1.amazonaws.com/documents/BPCL+IQCM+2019.pdf) · [BPCL MDG 2012](https://www.bharatpetroleum.in/pdf/mdg2012.pdf)
- Bharat Petroleum — **HSD Oil Normal Test Method Specification** (density @ 15 °C). [bharatpetroleum.in PDF](https://www.bharatpetroleum.in/pdf/mrl_high%20speed%20diesel%20oil.pdf)
- Hindustan Petroleum — Retail Outlet overview. [hindustanpetroleum.com PDF](https://hindustanpetroleum.com/documents/pdf/Retail.pdf)
- Indian Oil — corporate brochure. [iocl.com PDF](https://iocl.com/download/Brochure-24112018-Eng.pdf)
- Bharat Coking Coal Ltd — **SOP for indenting, receipt, storage, handling and issue of HSD oil** (derivative of OMC SOPs). [bcclweb.in PDF](https://www.bcclweb.in/HqrDepartment/Excv/SOP_Indenting-Receipt-Storage_&_Handling-Issue_of_HSD_Oil.pdf)
- OISD-225 — TT decantation checklist (circulated copy on Scribd). [scribd.com](https://www.scribd.com/document/514172346/OISD-225-TT-Decantation-Procedure-Check-List) · Generic [TT decantation procedure](https://www.scribd.com/document/629528504/TT-decantation-procedure-2) · [Decantation Checklist](https://www.scribd.com/document/496118567/Decantation-Checklist)

Equipment & field guidance:

- Uniforms India — **Petroleum Density Kit with NABL Certificate** (hydrometer + thermometer + jar set used at ROs). [uniforms.org.in](https://www.uniforms.org.in/product-page/petroleum-density-kit-with-nabl-certificate) · [blog post on density kit for petrol pumps](https://www.uniforms.org.in/post/density-kit-for-petrol-pump)
- SMC Insurance — Petrol Density Range in India (explainer on 720–775 kg/m³ and daily display). [smcinsurance.com](https://www.smcinsurance.com/motor-insurance/articles/petrol-density-range-india)
- Car Blog India — Best density petrol for vehicles (consumer-side view). [carblogindia.com](https://www.carblogindia.com/best-petrol-density-for-car-bike-india/)
- Team-BHP — Fuel density discussion for different fuels. [team-bhp.com thread](https://www.team-bhp.com/forum/technical-stuff/15812-fuel-density-what-should-different-fuels.html)
- Engineering Toolbox — Fuels: densities and specific volumes. [engineeringtoolbox.com](https://www.engineeringtoolbox.com/fuels-densities-specific-volumes-d_166.html)
- Lube-Oil.in — Density & relative density test method overview. [lube-oil.in](https://lube-oil.in/density-of-liquids-lube-oil-testing.php)
- Rofa Products — ASTM D1250 pocket implementation notes. [rofa-products.com PDF](http://www.rofa-products.com/download/ASTM1250_ppc.pdf)

Adulteration / density as a quality signal:

- FuelBuddy — How to detect & prevent fuel adulteration. [fuelbuddy.in](https://www.fuelbuddy.in/fuel-adulteration-how-to-detect-prevent-it/)
- PMC / NCBI — Evaluation of physicochemical parameters as indicators of diesel adulteration (2024). [pmc.ncbi.nlm.nih.gov/PMC11402756](https://pmc.ncbi.nlm.nih.gov/articles/PMC11402756/)
- ScienceDirect — FTIR-ATR detection of adulterated gasoline fuel in India (2024). [sciencedirect.com](https://www.sciencedirect.com/science/article/abs/pii/S1350449524000033)
- Springer — Kerosene as an adulterant in diesel (chromatography & HRMS). [link.springer.com](https://link.springer.com/article/10.1007/s42452-019-0637-7)

Reference values quoted above (α for MS/HSD, ASTM D1250 K0/K1 per commodity group, ±3 kg/m³ DVA band, IS product ranges) are consistent across the citations above but **should be re-verified against the binding OMC SOP and the current IS 2796 / IS 1460 revisions before any value is hard-coded as a block-level constant.** See Open Question #1 in §6.
