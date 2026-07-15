# Phase 9 — Building DZZLO's Business Model & Financial Model

> Level: Advanced | Time: ~2 hr | Outcome: you can articulate how DZZLO makes money (business model), price it, compute what a customer is worth (unit economics), and build a driver-based 3-year financial model that projects revenue, cost, profit, and runway. This is the phase that closes the gap you named — "pre-revenue, no model set" — and everything in Phases 7–8 and 10 plugs into it.

---

## 1. Three "Models", Don't Blur Them

You said VSYST has no business/financial model yet. First, separate three things people mush together:

| Model | The question it answers | Form |
| --- | --- | --- |
| **Business model** | *How does DZZLO create and capture value?* | A story / canvas (§2) |
| **Revenue model** | *How specifically does money come in?* | Pricing structure (§3) |
| **Financial model** | *What do the numbers do over 3 years?* | A spreadsheet (§6) |

You build them **in that order**: understand the business, choose how it charges, then project the numbers. Jumping to a spreadsheet before you know how DZZLO charges is why financial models feel impossible — you're modelling assumptions you haven't made yet.

## 2. The Business Model Canvas — DZZLO on One Page

The **Business Model Canvas** is 9 boxes that capture a whole business. Here it is, filled for **DZZLO** from what the product already is (a credit & order-management platform for petrol-pump dealers and their bulk-fuel transport customers, where *VSYST never holds funds*):

| Block | DZZLO |
| --- | --- |
| **Customer segments** | Petrol-pump dealers (primary payer); their bulk-fuel transport/credit customers (users) |
| **Value proposition** | One trustworthy shared ledger ("like a bank statement"), enforced per-customer credit limits, immutable records, bill-to-bill matching, in-platform GST/TDS — replacing error-prone diaries & disputes |
| **Channels** | Direct founder sales, referrals within the dealer network, the family's 35-yr petroleum relationships |
| **Customer relationships** | High-touch onboarding, ongoing support, retention via daily-use stickiness |
| **Revenue streams** | **SaaS subscription per dealer** (+ optional setup fee) — *not* transaction fees (VSYST holds no funds) |
| **Key resources** | The DZZLO codebase/IP, the domain trust, you (the team) |
| **Key activities** | Product development, onboarding, support, sales |
| **Key partners** | Possibly IOCL/OMC relationships, channel partners, payment/IPG providers (Easebuzz correspondence) |
| **Cost structure** | Salaries, cloud/hosting, support, sales/marketing, compliance |

Filling this honestly usually exposes the one weak block. For DZZLO the sharp questions are: **who exactly pays — the dealer or the transporter?** and **is the value big enough that they'll pay monthly?** Those are answered by *talking to customers* (§7), not by guessing in a spreadsheet.

## 3. The Revenue Model — How DZZLO Charges

For a SaaS product like DZZLO, the credible options:

| Model | How | Fit for DZZLO |
| --- | --- | --- |
| **Per-account subscription** | Flat ₹/month per dealer | **Strong default** — simple, predictable |
| **Tiered** | Price by volume (customers/orders/pumps managed) | Good — bigger dealers pay more, aligns price with value |
| **Per-seat** | ₹/month per staff login | Weak — dealers have few seats |
| **Per-transaction / % of value** | Cut of each order | **Avoid** — invites payment-aggregator/RBI scope and breaks "never holds funds" (Phase 6 §4) |
| **Freemium** | Free basic, paid advanced | Risky early — free users don't tell the truth (ops plan) |
| **Setup + subscription** | One-time onboarding fee + recurring | Good — setup fee funds high-touch onboarding |

**Recommended shape for DZZLO:** a **tiered per-dealer subscription** (small/medium/large by number of credit customers or order volume), optional **one-time setup fee**, and an **annual-prepay discount** to capture the cash advantage (Phase 7 §5). Keep revenue as a *software service fee* — clean accounting, no fund-holding, no aggregator regulation.

## 4. Pricing — The Highest-Leverage Number You'll Set

Three ways to price; use the third:

- **Cost-plus** (cost × markup) — fine for agencies, *wrong* for software (your marginal cost is ~₹0, so cost-plus leaves enormous value on the table).
- **Competitor-based** — a sanity check, not a strategy.
- **Value-based** — price against *what the outcome is worth to the dealer*. If DZZLO prevents even one ₹50,000 credit dispute a year and saves hours of ledger reconciliation, ₹1,500–3,000/month is trivially justified. **This is the right frame for SaaS.**

Practical pricing moves:
- **Anchor to value, not cost.** Ask dealers what a bad-debt or a reconciliation error costs them today.
- **Charge more than feels comfortable, on new customers first** (ops plan) — underpricing is the more common startup mistake, and it's hard to raise later.
- **Nudge to annual** with a discount (e.g. 2 months free) → the cash superpower.
- **Paying users tell the truth; free users don't** — get to a *paid* price fast, even with your first 3 dealers.

## 5. Unit Economics — What One Customer Is Worth

This is the heart of a SaaS business and the language investors speak. Learn these six:

| Metric | Formula (roughly) | DZZLO illustrative |
| --- | --- | --- |
| **ARPA** (avg revenue per account) | Total MRR ÷ accounts | ₹1,800/month |
| **Gross margin** | (Revenue − cost to *serve*) ÷ revenue | ~85% (software) |
| **CAC** (customer acquisition cost) | Sales+marketing spend ÷ new customers | ₹6,000 |
| **Monthly churn** | Customers lost ÷ customers, per month | 2% |
| **LTV** (lifetime value) | (ARPA × gross margin) ÷ monthly churn | (1,800 × 0.85) ÷ 0.02 = **₹76,500** |
| **LTV : CAC** | LTV ÷ CAC | 76,500 ÷ 6,000 ≈ **12.7×** |
| **CAC payback** | CAC ÷ (ARPA × gross margin) | 6,000 ÷ 1,530 ≈ **4 months** |

**How to read these (the rules investors apply):**
- **LTV : CAC ≥ 3** is healthy; below 1 you *lose money on every customer* — a growth trap. DZZLO's illustrative ~12× (thanks to high margin + low churn from daily-use stickiness) would be *excellent* — **if** those churn and CAC assumptions hold in reality. That "if" is the whole game.
- **CAC payback < 12 months** means customers repay their acquisition cost fast, so growth is self-funding. ~4 months would be strong.
- **Churn is the silent killer.** At 2% monthly churn, average customer life ≈ 50 months; at 5%, only 20 months — a huge LTV difference. A sticky daily-use ledger like DZZLO *should* have low churn; prove it with data.

> **The honesty check:** these numbers are *illustrative*. Your real job in Phase 9 is to **replace every one with a measured figure** from your first paying dealers. A model built on invented unit economics is a fantasy; a model built on 5 real customers' behaviour is a strategy.

## 6. The SaaS Metrics Vocabulary (so investors don't lose you)

| Term | Means |
| --- | --- |
| **MRR / ARR** | Monthly / Annual Recurring Revenue — the SaaS heartbeat (ARR = MRR × 12) |
| **New / Expansion / Churned MRR** | MRR added from new customers / upsells / lost customers |
| **Net Revenue Retention (NRR)** | Revenue from existing customers this year vs last (>100% = you grow even with zero new customers — the SaaS holy grail) |
| **Logo vs revenue churn** | Losing *customers* vs losing *rupees* (a few big accounts leaving hurts revenue more than logos) |

## 7. Building the Financial Model — Structure

A financial model is **not** a fixed prophecy; it's a **driver-based spreadsheet** where you change *assumptions* and watch *outcomes*. Build it **bottom-up** (customers × price), never top-down ("1% of a huge market" — investors dismiss this as vanity). The standard tab structure:

```
① ASSUMPTIONS (the only cells you edit — colour them)
     starting customers, new customers/month, monthly churn,
     ARPA, annual-prepay %, gross margin, headcount plan, salaries,
     hosting/customer, marketing spend, CAC
        │
        ▼
② REVENUE BUILD (customer roll-forward)
     customers[m] = customers[m-1] + new − churned
     MRR = customers × ARPA ;  ARR = MRR × 12
        │
        ▼
③ COST BUILD
     COGS = hosting + support (drives gross margin)
     Opex = salaries (headcount plan) + tools + marketing + compliance
        │
        ▼
④ P&L  (Phase 3 ladder)
     Revenue − COGS = Gross Profit − Opex = EBITDA → profit/(loss)
        │
        ▼
⑤ CASH FLOW  (Phase 3)  ← annual prepay lands cash early!
     + financing (your capital/loans) − capex
        │
        ▼
⑥ OUTPUTS  (the dashboard you actually read)
     monthly cash balance & runway, break-even month,
     cash low-point, ARR at month 36, LTV:CAC
```

The magic is **①**: because every number flows from the assumptions, you can ask *"what if churn is 4% not 2%?"* or *"what if we hire a salesperson in month 6?"* and instantly see runway and break-even move. **That** is what a financial model is *for* — not predicting the future, but pressure-testing decisions before you spend real money on them.

## 8. From Model to Decisions

Once the model runs, it answers the questions that have been abstract until now:

| Question | The model tells you |
| --- | --- |
| **When do we break even?** | The month EBITDA / operating cash flow crosses zero (Phase 10's target) |
| **Can we afford to hire?** | Add the salary in ③, watch runway — can cash survive the dip? |
| **Should we raise? How much?** | If break-even is reachable on customer cash → maybe don't (Phase 8). If a land-grab needs speed → the model sizes the raise & shows the runway it buys |
| **What price do we need?** | Flex ARPA in ① until the model works — reveals the *minimum viable price* |
| **How many customers to survive?** | The customer count where revenue covers burn = your Phase 3 break-even, now dynamic |

## 9. The Pre-Revenue "Find the Model" Playbook

You can't model a business you haven't validated. Before/alongside the spreadsheet:

1. **Talk to 10–15 dealers** — using *The Mom Test* (ops plan reading list): ask about their *current* pain and what it costs them, **not** "would you pay for DZZLO?" (people lie to be nice).
2. **Get 3 paying customers at a real price** — even a small one. *Paying* validates the model; free pilots validate nothing. This single step turns "no model" into "early model."
3. **Measure the real unit economics** (§5) from those first customers — actual ARPA, actual onboarding cost, early churn signal.
4. **Feed reality back into the model.** Now your assumptions are *measured*, and the projection is a strategy, not fiction.
5. **Iterate pricing** with each cohort until LTV:CAC and payback clear the bars in §5.

This is the concrete path out of "pre-revenue, no model": *canvas → price → 3 paying dealers → measured unit economics → model.* Each step is small; together they're the business.

## 10. Exercises

**10.1 — Fill DZZLO's canvas (20 min).** In `finance-workbook/phase9-canvas.md`, complete all 9 boxes from §2 in *your* words. Circle the weakest block and write the one question you'd ask a dealer to resolve it.

**10.2 — Set a real price (15 min).** Design DZZLO's tiered pricing (3 tiers + setup fee + annual discount). For each tier, write the *value justification* (what it saves the dealer). Commit to a number you'd quote your next dealer.

**10.3 — Compute unit economics (20 min).** Using §5's formulas and your *best current guesses*, compute DZZLO's ARPA, LTV, CAC, LTV:CAC and payback. Mark each input "guess" or "measured". Your Phase-9 mission is to convert guesses to measured.

**10.4 — Build the 3-year model (60 min).** In `finance-workbook/phase9-model.xlsx`, build §7's tabs: an assumptions block, a monthly customer roll-forward, MRR/ARR, a cost build with your headcount plan, a P&L, and an outputs row with **runway and break-even month**. Then run three scenarios (base / churn doubles / hire a salesperson at month 6) and note how break-even and cash-low-point move. **This spreadsheet is your CFO cockpit** — you'll live in it in Phase 10.

---

**Next:** [[10-phase-10-pre-revenue-to-profitable]] — the founder-CFO's operating rhythm: the metrics to watch, the monthly/quarterly cadence, and exactly when and how to flip VSYST from burning cash to making money.
