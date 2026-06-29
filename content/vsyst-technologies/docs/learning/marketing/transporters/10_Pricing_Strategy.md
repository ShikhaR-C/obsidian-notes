# Pricing Strategy

**Purpose:** move DZZLO from "free forever" (pre-PMF phase) to a pricing model that monetises fairly, supports unit economics, and leaves room for a compound fintech layer.

---

## Executive summary

1. **Keep dealer side free (or near-free) in Phase 0–1.** Dealers are your supply side of the network; charging them slows density. Transporters pay.
2. **Pricing axis: per-truck subscription + usage meter + fintech take-rate** (the Toast / Shopify three-layer stack).
3. **Price ladder for transporters:** ₹0 (owner-driver 1–4 trucks) / ₹499 per truck/mo (5–20 trucks) / ₹999 per truck/mo (21–100) / Enterprise custom (100+).
4. **Run Van Westendorp** on 30 prospects each side before locking v1 prices.
5. **Fintech layer (DZZLO Card / Pay / Credit) is where revenue compounds** — 2–5× uplift per customer per a16z and Fractal.
6. **Re-evaluate at every ₹50L ARR milestone.** Prices decay; founder attention must refresh them.

---

## 1. Frameworks

### 1.1 Three approaches to pricing

- **Cost-plus** — safe v1, leaves money on the table fast
- **Competitor-based** — dangerous anchor in fragmented markets; Indian pump software range is ₹4,800–21,600/yr/seat, too wide to be useful
- **Value-based** ⭐ — north star. ProfitWell/Price Intelligently: companies using customer-informed pricing grow ~30% faster; 1% pricing improvement lifts profit ~11%

### 1.2 Van Westendorp Price Sensitivity Meter

Four questions per prospect ([Wikipedia Van Westendorp](99_References.md#wiki-van-westendorp); [Monetizely VW](99_References.md#monetizely-van-westendorp)):

1. At what price would it be so cheap that you'd doubt the quality? (Too cheap)
2. At what price would you consider it a bargain? (Cheap)
3. At what price would it start feeling expensive? (Expensive)
4. At what price would you refuse to buy? (Too expensive)

Plot cumulative curves; intersections give Point of Marginal Cheapness (floor), Optimal Price Point (target), Indifference Price Point, Point of Marginal Expensiveness (ceiling).

**DZZLO action:** run two separate Van Westendorp studies — one for transporters, one for dealers — via WhatsApp / Google Forms in Hindi. Sample size: 30–50 each. Re-run every 12–18 months.

Supplement with **Gabor-Granger** (direct willingness-to-pay at set prices) to validate specific tier levels.

---

## 2. Pricing models for fintech-adjacent SaaS

A pure subscription leaves ~70% of potential revenue unrealized ([a16z](99_References.md#a16z-fintech-scales-vsaas); [Fractal](99_References.md#fractal-vsaas-fintech-playbook); [Aperture](99_References.md#medium-aperture-vsaas-fintech)). Rails relevant to DZZLO:

| Model | DZZLO applicability | Mechanic |
|---|---|---|
| Per-seat | Pump (cashier/manager users) | ₹X/user/mo |
| **Per-outlet** | Dealer groups | ₹Y/outlet/mo, group discounts |
| **Per-truck / per-vehicle** | Fleet operators | ₹Z/truck/mo, tiered |
| Per-transaction | Digital fuel settlements, driver payouts | Flat ₹ or bps |
| GMV % | Fuel-card spend, supplier payments | 20–100 bps |
| **Interchange rebates** | Co-branded fleet card (DZZLO Card) | 70/30 split of ~100–240 bps blended interchange ([Synctera](99_References.md#synctera-interchange)) |
| Float income | Driver wallet, fleet prepay | NIM on float |
| **Subscription + usage hybrid** ⭐ | Base fee + metered overages | Stability + expansion |
| Freemium | 1–4 truck owner-drivers only | Upgrade path |

**DZZLO's three-layer stack:**

1. **Base SaaS subscription** — per-truck or per-outlet, predictable
2. **Usage meter** — transactions, litres reconciled, API calls, e-invoices
3. **Fintech take-rate** — bps on fleet card / payouts / interchange (Phase 2+)

Start (1) + (2); add (3) once 500+ active outlets + banking/BaaS partner.

**Adoption trend:** ~67% of SaaS has a usage component; 77% of large software uses consumption pricing for expansion; top performers with value-aligned meters hit 115–125% NRR ([Flexera](99_References.md#flexera-saas-consumption); [Growth Unhinged](99_References.md#growth-unhinged-usage); [Ordway usage](99_References.md#ordway-usage-pricing)).

---

## 3. Packaging

### 3.1 Good-Better-Best (G-B-B)

([Simon-Kucher](99_References.md#simonkucher-g-b-b); [Monetizely G-B-B](99_References.md#monetizely-gbb)) 20–50% revenue lift when executed well; middle tier captures 60–70%. Top tier serves as anchor/decoy — lifts mid-tier selection by up to 85%.

### 3.2 DZZLO v1 tiers — transporter side

| Plan | Starter | Growth ⭐ | Pro |
|---|---|---|---|
| **Price** | **Free** | **₹499/truck/mo** | **₹999/truck/mo** |
| Trucks | Up to 4 | 5–20 | 21–100 |
| Fleet registration | ✓ | ✓ | ✓ |
| WhatsApp-based parchi | ✓ | ✓ | ✓ |
| Driver OTP fill | ✓ | ✓ | ✓ |
| Multi-pump ledger | — | ✓ | ✓ |
| GST-compliant invoice stream | — | ✓ | ✓ |
| TDS auto-calc | — | ✓ | ✓ |
| Consumption variance alerts | — | ✓ | ✓ |
| Multi-driver management | — | ✓ | ✓ |
| API / integrations (Tally, etc.) | — | — | ✓ |
| Dedicated CSM | — | — | ✓ |
| Priority support | — | — | ✓ |
| DZZLO Card (fleet card, 0 platform fee, bps revenue) | — | Add-on | ✓ included |

**Enterprise (custom):** 100+ trucks; custom API, SLA, dedicated AE.

### 3.3 DZZLO v1 tiers — dealer side

Phase 0–1: **free** for dealers to drive two-sided network density. Monetisation emerges through transaction fees on DZZLO Pay and interchange on DZZLO Card, not per-seat SaaS.

Phase 2+ (optional subscription):

| Plan | Bunk Lite | Bunk Pro ⭐ | Bunk Enterprise |
|---|---|---|---|
| **Price** | **Free** | **₹2,499/outlet/mo** | **₹4,999/outlet/mo** |
| Digital parchi + shared ledger | ✓ | ✓ | ✓ |
| GST invoicing | ✓ | ✓ | ✓ |
| DSR + tank-dip + shift | — | ✓ | ✓ |
| Multi-outlet dashboard | — | — | ✓ |
| Fleet-card acquiring (bps on TPV) | — | Add-on | ✓ included |
| OMC integration (IOCL/BPCL/HPCL) | — | ✓ | ✓ |
| Dedicated CSM | — | — | ✓ |

### 3.4 Add-ons (à la carte)

Decouple high-cost features from tiers:

- **FASTag reconciliation** — ₹99/truck/mo
- **E-invoicing module** — ₹499/outlet/mo
- **Insurance attach** — 0 platform fee + commission from insurer
- **Driver payout rail** — 0.5% of disbursement

### 3.5 Annual prepay

**12 months prepay = 10 months charged** ("2 months free") = effective ~17% discount. Indian SMB responds to "10 pay, 12 get." Keep monthly open; forced annual kills velocity.

---

## 4. Psychological pricing

- **Charm pricing:** ₹499, ₹999, ₹2,499, ₹4,999, ₹9,999. Left-digit effect strong in rupee markets.
- **Anchoring:** pricing page leads with "Pro" tier visible (right-most or centre-highlighted).
- **Decoy effect:** Pro tier delivers best value-per-feature ratio — funnels customers there.
- **GST-inclusive display:** always show "₹999/mo (incl. 18% GST)" or "+ GST" clearly. SMB loses trust when billed higher than quoted.
- **Round numbers leave room to negotiate:** list at ₹9,999 so reps can "give" ₹999 off and land at ₹8,999.
- **Reciprocity:** open with a named give (free onboarding, free first-month POC, free 30-day extension) before a discount is asked.

---

## 5. Indian SMB price points that work

Empirical traction from Zoho, Razorpay, Freshworks, Vyapar, Chargebee pricing pages + founder discourse ([Paddle Zoho Freshworks](99_References.md#paddle-zoho-freshworks); [Razorpay charges](99_References.md#softwaresuggest-razorpay); [EximPe INR](99_References.md#eximpe-inr-pricing); [Tunguz pricing](99_References.md#tunguz-pricing-guide)):

- **₹499/mo** — "my first SaaS," single-user SMB entry
- **₹999/mo** — canonical SMB sweet spot
- **₹2,499/mo** — small-team, feature depth
- **₹4,999/mo** — professional SMB, multi-user
- **₹9,999/mo** — upper SMB / lower mid-market
- **₹24,999 / ₹49,999 / ₹99,999** — mid-market → enterprise entry

Annual multipliers: multiply monthly × 12 then discount 2 months — ₹4,990 / ₹9,990 / ₹24,990 / ₹49,990.

### Willingness-to-pay benchmarks (fleet/fuel, estimated for DZZLO pending Van Westendorp)

- Single-truck owner: ₹200–500/mo max; usually won't pay → **Free**
- Small fleet (5–20 trucks): **₹300–800/truck/mo ceiling** → **₹499 justified**
- Mid fleet (20–100): **₹500–1,200/truck/mo** → **₹999 justified**, especially with ROI proof
- Single petrol outlet: **₹800–2,500/mo total ceiling** → **₹2,499 Bunk Pro in range**
- Multi-outlet dealer (5+): ₹1,500–4,000/outlet/mo with dashboard → **₹4,999 Enterprise**
- **Add transactional bps on top** without raising SaaS fee — buyers don't feel bps.

### Discount norms

- Default ask: 15–25%.
- Acceptable: 10–25% for annual prepay + multi-outlet.
- 30%+ only for lighthouse / referenceable customers.
- Always concede in exchange for term or case-study rights.

---

## 6. Evolution roadmap

| Version | ARR band | Model | What changes |
|---|---|---|---|
| **v1** (0–₹1Cr ARR) | Flat tiers | Per-truck / per-outlet only. One price axis. Iterate quarterly. |
| **v2** (₹1–5Cr ARR) | +Usage meter | Metered overages on top of subscription; enterprise tier gated on SE + contract |
| **v3** (₹5–20Cr ARR) | +Fintech bps | DZZLO Card interchange + DZZLO Pay take-rate; reprice base using v1/v2 cohort data |
| **v4** (₹20Cr+ ARR) | Multi-dimensional | Industry tiers, usage-based primary on some modules, annual-only on enterprise |

### Price increases without churn

([Chargebee playbook]; [Bessemer revamped pricing](99_References.md#bessemer-revamped-pricing))

- **Grandfather** existing customers for 12 months, then 90-day notice
- **Increase list price first;** existing-base increase comes later with feature additions to justify
- **Bundle a new feature** into the increase ("we added driver payouts — price is now ₹1,299")
- **Announce via personal email/WhatsApp from the CSM**, not a mass blast
- Offer **annual lock-in at old price** as a release valve

---

## 7. Monetisation lessons from Indian SaaS that scaled

| Company | Lesson for DZZLO |
|---|---|
| **Zoho** | Bundle ruthlessly. Zoho One at ~$37/user/mo replaced 40+ individual SaaS bills. Indian buyers love all-in-one. |
| **Freshworks** | Free tier at the bottom, premium at top. Glass-transparent pricing pages won inbound. |
| **Razorpay** | Pay-as-you-go (2% MDR, no setup, no AMC). Zero-friction landing. Monetise *breadth* (RazorpayX, Capital, Cards) once core relationship exists. |
| **BrowserStack** | Developer-first self-serve PLG. Per-parallel pricing that scales with team. Land $29/mo, expand $5K/mo. |
| **Postman** | Freemium for individuals, team plans for orgs; Postbot usage-based on top ([Chargebee Postman](99_References.md#chargebee-postman)). |
| **Chargebee** | Hybrid pricing (subscription + usage) from day one. Mid-market focus vs Zuora. |
| **ClearTax** | Vertical compliance SaaS — per GSTIN; expand to e-invoicing, TDS, supply-chain credit. Land narrow on a regulatory forcing function. |
| **Vyapar** | Pure SMB flat annual price (~₹1,999–3,999/yr). High volume, low ARPU. Tally-alternative positioning. |

**Distilled for DZZLO:** one clear price axis at v1, charge modestly but consistently (Razorpay's 2%, Zoho's per-user), add fintech bps as the moat once distribution is won. **Don't try to be Vyapar — that race is run.**

---

## 8. Special pricing programs (first 24 months)

- **Founding Customer Program (first 50 dealers):** 50% off Bunk Pro for 12 months + lifetime case-study rights
- **Association Program:** CGPDA / state PDA members get 25% off Bunk Pro if 20+ members onboard
- **AIMTC Member Offer:** transporters get Growth tier at ₹299/truck/mo (vs ₹499 list) for 12 months
- **Startup India Accelerator Offer:** if a startup incubator endorses us, members get 3 months free
- **Student / owner-driver:** free forever for 1–4 trucks (supply-side density)

All special programs sunset after 24 months; never perpetual discounts.

---

## 9. Pricing page design principles

(Applies whenever you build the pricing page — currently not published)

- **3 tiers visible** (Starter / Growth ⭐ / Pro); Enterprise is "Contact sales"
- **Hindi + English toggle** (default Hindi for Indian IPs)
- **Monthly / annual toggle** at top; annual pre-selected ("Save 17%")
- **Social proof under pricing** — dealer / transporter count, association badges
- **FAQ accordion** addressing: "Is GST included?", "Can I cancel?", "Do you take cards?", "ट्रायल फ्री है?"
- **Sticky WhatsApp CTA** on every scroll position

---

## 10. Red flags to watch

- Average discount >25% across deals → pricing is too high or sales team is weak
- Average discount <5% → pricing is too low or you're leaving money on the table
- Free-tier-to-paid conversion <5% → tier design wrong
- Churn concentrated in any one plan → that plan is mispriced or mispackaged
- Expansion revenue <20% of new revenue → not selling modules; NRR at risk

---

## Cross-references

- Sales discount policy: `09_Sales_Strategy.md` §9
- Revenue plan per phase: `11_Funding_and_Budget_Plan.md`
- NRR / GRR targets: `13_Metrics_and_KPIs.md`
- Fintech compound layer logic: `01_Vertical_SaaS.md` §6
