# Metrics & KPIs — What to Measure, How Often, and Why

**Purpose:** define the single source of truth for metrics. Every other strategy note references numbers; this doc defines what they mean, how to compute them, and what targets apply at each phase.

---

## Executive summary

1. **Track 12 metrics, not 50.** Founders who track everything track nothing.
2. **Retention is the north star** for SaaS (and especially for Indian SMB where CAC is hard). Acquisition without retention is theatre.
3. **Funnel, financial, and product metrics** each need a weekly cadence at founder level.
4. **Board cadence is monthly; quarterly deep-dive.** Weekly dashboards don't go to the board.
5. **Benchmarks adjust by stage** — compare to Seed-stage vertical SaaS at Phase 1, not to Toast IPO.

---

## 1. The 12 metrics — definitions

### Revenue metrics

1. **MRR / ARR** — Monthly / Annual Recurring Revenue. *Include* subscription fees. *Exclude* one-time setup, unpredictable usage overages until 3+ months stable, one-off services. Break out **New / Expansion / Contraction / Churn** monthly.
2. **NRR — Net Revenue Retention** — (revenue from cohort in month 12) / (revenue from same cohort in month 0), after expansion, contraction, churn. **Target: ≥105% by Phase 1; ≥115% by Phase 2.** Best-in-class VSaaS 120%+ ([Fullview](99_References.md#fullview-nrr); [Rockingweb](99_References.md#rockingweb-saas-2025)).
3. **GRR — Gross Revenue Retention** — NRR without expansion. **Target: ≥85% Phase 1; ≥90% Phase 2.** GRR is the *real* retention signal; NRR can hide churn behind expansion.
4. **Logo churn** — customers churned / customers at start of period. SMB 8.2× enterprise ([Benchmarkit](99_References.md#rockingweb-saas-2025)). Budget 2–4% monthly for SMB.

### Unit economics

5. **ACV / ASP** — Annual Contract Value / Average Selling Price. Target Phase 1: ₹30k–₹1.2L blended.
6. **CAC** — fully loaded S&M ÷ new customers. Track blended + paid-only separately.
7. **LTV** — ACV × gross margin × (1 / logo churn rate). Use conservatively; don't project 3-year LTV at Seed.
8. **LTV:CAC** — target **≥3:1**.
9. **CAC payback** — CAC ÷ (ACV × gross margin). **Target <12 months Phase 1, <18 Phase 2.** Median 2024 US SaaS is ~20 months, down from 25 in 2022 ([ScaleXP 2025](99_References.md#scalexp-cac-payback); [High Alpha](99_References.md#highalpha-benchmarks-2025); [Phoenix Strategy]).
10. **Magic Number** — ΔARR × 4 ÷ prior-quarter S&M. **>0.7 healthy, >1 elite.**

### Efficiency / composite

11. **Rule of 40** — growth rate % + EBITDA margin %. Attractive ≥40, premium >50. Early stage: >20 acceptable, trend toward 40+ by Phase 3 ([High Alpha](99_References.md#highalpha-benchmarks-2025)).
12. **Burn multiple** — net cash burn ÷ net new ARR. **<1 great, <2 good, >3 red flag.**

---

## 2. Funnel metrics (track alongside the 12)

Per-stage CVR; monitor trendline not absolute numbers ([DigitalBloom](99_References.md#digitalbloom-funnel-2025); [Outreach](99_References.md#outreach-pipeline)).

| Stage | Benchmark | DZZLO target Phase 1 |
|---|---|---|
| Visitor → Lead | 1–3% content, 5–10% paid | 3% |
| Lead → MQL | 20–40% | 30% |
| MQL → SQL | 40–60% | 50% |
| SQL → Opportunity | 50–70% | 60% |
| Opp → Closed Won | SMB 30–40% | 35% |
| Pipeline coverage | 2–3× SMB velocity; 3–4× mid-market | 2.5× |
| Cycle time | SMB <$5K ACV = 30–90 days, median 40 | 45 days |

---

## 3. Product metrics (parallel to revenue)

| Metric | Definition | Phase 1 target |
|---|---|---|
| MAU / WAU | Monthly / Weekly Active Users | 60% WAU/MAU ratio |
| Activation rate | % of new accounts completing first meaningful action within 7 days | ≥70% |
| First-week retention | % active in week 1 post-signup | ≥65% |
| Trip-register activation | % of on-platform trucks logging ≥1 trip/week | ≥60% |
| Slip-book submission rate | slips submitted / expected slips | ≥85% for paid dealers |
| Variance alerts triggered (fraud signal) | alerts per truck per month | trending down (indicates fraud actually captured) |
| Average support tickets / dealer / week | | <0.5 |

---

## 4. Phase-by-phase targets

| Metric | Phase 0 | Phase 1 | Phase 2 | Phase 3 |
|---|---|---|---|---|
| Paying dealers | 50 | 100 | 300 | 1,000+ |
| Active transporters | 500 | 2,000 | 8,000 | 40,000+ |
| ARR | ₹24–60L | ₹30–50L | ₹3–5 Cr | ₹15–25 Cr |
| NRR | n/a | 105% | 115% | 120% |
| GRR | 85% | 88% | 90% | 92% |
| CAC blended | ₹3–5k | ₹5–8k | ₹6–10k | ₹8–12k |
| CAC payback | <9 mo | <12 mo | <18 mo | <24 mo |
| Magic Number | n/a | 0.7 | 0.8 | 1.0 |
| Rule of 40 | n/a | 0+ | 20+ | 30+ |
| Fintech revenue % | 0 | 5% | 20% | 35% |

---

## 5. Operating cadence — who reads what when

### Weekly (Monday)

**Founder / sales lead:**
- Pipeline by AE × stage
- New MRR this week
- Churn events this week (escalate any if unclear)
- Top-3 wins + top-3 losses — qualitative
- Marketing dashboard (see `08_Marketing_Strategy.md` §6)

### Monthly

**Founders + CS + Marketing:**
- MRR movement (new / expansion / contraction / churn)
- Cohort retention view (monthly cohorts, 12-month trailing)
- CAC by channel
- NRR / GRR trend
- Product metric review

### Quarterly

**Full team + advisors:**
- Rule of 40, NRR, Magic Number, CAC payback trends
- QBR with top-20 accounts (via CS)
- Hiring scorecard
- Pricing re-examination (changes once/year; data collection always)
- Strategy red-team (see `12_Roadmap_Phases.md` §red-team)

### Board (monthly, once investors are in)

**Standard board pack structure:**

1. Headline: ARR, growth rate, Rule of 40, runway
2. New ARR by segment (fleet / dealer / partner)
3. Pipeline coverage + forecast vs plan
4. NRR / GRR by cohort
5. CAC by channel + payback
6. Top-3 wins, top-3 losses
7. Product roadmap progress vs plan
8. Hiring + org changes
9. Asks from the board

---

## 6. Benchmarks — where DZZLO should sit

| Metric | Early-stage Indian VSaaS median | DZZLO Phase 2 target | World-class VSaaS |
|---|---|---|---|
| NRR | 95–100% | 115% | 120–140% |
| GRR | 80–85% | 90% | 92–95% |
| CAC payback | 12–18 mo | <12 mo | <9 mo |
| LTV:CAC | 2:1 | 3:1 | 4:1+ |
| Logo churn (annual SMB) | 20–25% | 12% | <8% |
| Rule of 40 | 10–20 | 25 | 40+ |
| Fintech attach | 0–5% | 20% | 50%+ (Toast: 80%) |

---

## 7. Dangerous vanity metrics to ignore

Replace these with the metrics above ([MarTech vanity](99_References.md#martech-vanity); [Improvado vanity](99_References.md#improvado-vanity)):

- **Website traffic** without conversion tracking
- **Social media followers** without engagement → paying conversion
- **Blog posts published** without ranking / traffic
- **Leads generated** without SQL rate tracked
- **Demos run** without closed-won rate
- **Email open rate** (many false opens in 2026 due to tracking pixel opt-outs)
- **App downloads** (DZZLO: active users > downloads always)
- **Press mentions** without attribution to revenue

---

## 8. Single-sheet dashboard template

Google Sheet or Notion table. Founder fills weekly; no BI tool needed until Series A.

```
| Week        | 2026-W16 | 2026-W17 | 2026-W18 | 2026-W19 | Goal   |
| MRR (₹)     | 185,000  | 212,000  | 248,000  | 285,000  | 500k  |
| New dealers | 3        | 4        | 5        | 6        | 5/wk  |
| Churn       | 0        | 0        | 1        | 0        | <1/wk |
| SQLs        | 18       | 22       | 25       | 28       | 25    |
| Pilots live | 12       | 15       | 18       | 22       |       |
| Pilots won  | 6        | 7        | 9        | 11       | 50% rate |
| CAC (paid)  | 4,200    | 3,800    | 3,600    | 3,400    | <4k   |
| Youtube subs| 320      | 410      | 505      | 630      |       |
| WA replies  | 85       | 110      | 130      | 165      |       |
```

**When a metric misses goal 2 weeks running, escalate:** analyse bottleneck Wednesday, adjust Friday.

---

## 9. When to introduce a BI tool

- **Phase 0–1:** Google Sheets + Notion
- **Phase 2:** Metabase (free, open-source) + PostHog (product analytics)
- **Phase 3:** Consider Looker / Mode / Tableau

Don't over-engineer early. Founder-read single-sheet beats a beautiful unused BI dashboard.

---

## 10. What to measure that no one else in the category does

Differentiator metrics that could become DZZLO's unique reporting advantage:

- **Parchi digitisation coverage** — % of dealer's credit sales on DZZLO vs total. Targets 95%+.
- **Dispute rate** — (disputes / transactions) before DZZLO vs after. Case-study material.
- **Fuel-fraud $ recovered** per fleet per month.
- **Reconciliation time** — hours/week saved. Qualitative + quantitative.
- **Credit underwriting signal strength** — NPL rate on DZZLO Credit vs generic trucker NPL.
- **Two-sided density index** — dealers × transporters on a corridor segment.

These become pitch-deck money slides *and* product-quality signals.

---

## Cross-references

- Marketing weekly dashboard detail: `08_Marketing_Strategy.md` §6
- Sales pipeline metrics: `09_Sales_Strategy.md` §10
- Funding triggers using these metrics: `11_Funding_and_Budget_Plan.md` §3
- Phase-gate criteria referenced: `12_Roadmap_Phases.md`
