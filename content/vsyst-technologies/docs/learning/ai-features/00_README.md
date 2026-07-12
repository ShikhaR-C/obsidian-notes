# AI Features for DZZLO OMS — Plan & Feature Catalog

> Audience: VSYST product + engineering | Status: Proposal / learning doc | Scope: `dzzlo_oms_api` + `dzzlo_oms_app` (+ DIP module)

## What This Folder Is

A grounded plan for bringing **discriminative AI** (prediction, scoring, classification) and **generative AI** (LLM assistants, content generation, voice) into DZZLO OMS — with every feature tied to data and flows that **already exist** in our codebase, and a phased roadmap to ship them.

## The Product in One Paragraph

DZZLO OMS digitizes credit-based bulk diesel (HSD) sales between **petrol pump dealers** (IOCL/BPCL/HPCL/Shell/Nayara/Jio-BP outlets) and **transporters / truck owners** in India. A transporter places a purchase order for a vehicle, the dealer dispatches fuel against an SMS OTP handed to the driver at the pump, the dealer invoices (GST/TCS/TDS compliant), and payments are recorded as vouchers against per-relationship credit limits, billing periods, and advance deposits. A separate **DIP module** reconciles pump-side physical stock (tank dips, nozzle meter readings, decants). Today the platform has **zero AI/ML** — every behavior is deterministic.

## The Two Families of AI (and what each does for us)

|                     | Discriminative AI                                                                                                                    | Generative AI                                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
| **What it learns**  | P(label \| data) — draws boundaries, scores, forecasts                                                                               | P(data) — produces new text, speech, structured output                                                                                |
| **Typical outputs** | A number, a class, a ranking, an anomaly flag                                                                                        | A sentence, a summary, a conversation, a filled form                                                                                  |
| **DZZLO examples**  | "This customer will pay 12 days late" · "This tank loses 0.4% daily — investigate" · "This fill-up is abnormal for truck MH12AB1234" | "Sharma Transport ka outstanding ₹1.4L hai, 2 invoice pending" · Voice order → structured PO · Auto-drafted payment reminder in Hindi |
| **Data needs**      | Historical labeled/structured data (we have years of it)                                                                             | Mostly pre-trained (Claude/GPT); our data used via tool-calling/RAG                                                                   |
| **Cost profile**    | Cheap to run once built; needs data science effort                                                                                   | Per-token API cost; fast to build, needs guardrails                                                                                   |
| **Failure mode**    | Wrong score (quantifiable, testable)                                                                                                 | Hallucination (must never invent ledger figures)                                                                                      |

The two compound: discriminative models **detect and predict**, generative models **explain and act on** those predictions in the user's language. Example: a credit-risk model flags a customer (discriminative) → the assistant explains _why_ and drafts the reminder message (generative).

## Why DZZLO Is Unusually Well-Positioned

We already collect, per tenant, timestamped and relational:

1. **Full trade history** — `order_msts`, `so_msts`, `invs`, `voc_msts` (quantities, rates, products, payment modes, dates)
2. **Daily fuel price series** per dealer/product — `rate_msts`
3. **Credit behavior** — `dealer_custs` (limits, billing periods, advance deposits), `month_crdrs` (monthly Dr/Cr), invoice aging (`UNPAID → PARTPAID → FULLPAID`), voucher approval latency
4. **Fleet graph** — vehicles ↔ drivers ↔ customers ↔ hire/share relationships (`veh_msts`, `dvr_msts`, `veh_reqs`, `veh_trns`)
5. **Geo data** — GeoJSON coords + highway/city/district on dealers and customers
6. **Pump physical data (DIP)** — tank dips, nozzle meter readings, decants, reconciliation variances
7. **Behavioral logs** — every API request with user, device, response time (`logs`)

And we already have the delivery rails AI needs: OneSignal push (proactive nudges), Firebase Remote Config (feature gating), 2Factor SMS, SES email, and an `api_v3` services layer to host new AI services.

## Feature Index

Full details in docs 02 (discriminative) and 03 (generative). Phases defined in doc 04.

| #   | Feature                                                            | Persona     | AI type        | Value | Effort | Phase |
| --- | ------------------------------------------------------------------ | ----------- | -------------- | ----- | ------ | ----- |
| D1  | Dzzlo Credit Score (late-payment / default risk)                   | Dealer      | Discriminative | ★★★★★ | M      | 2     |
| D2  | Credit limit & terms recommender                                   | Dealer      | Discriminative | ★★★★  | M      | 2     |
| D3  | Collections prioritization (invoice delinquency)                   | Dealer      | Discriminative | ★★★★  | S      | 1–2   |
| D4  | Pump demand forecast & tank refill planner                         | Dealer      | Discriminative | ★★★★  | M      | 2     |
| D5  | DIP shrinkage / pilferage detection                                | Dealer      | Discriminative | ★★★★★ | M      | 2     |
| D6  | Order fraud & anomaly guard                                        | Both        | Discriminative | ★★★★  | S      | 1     |
| D7  | Customer churn early-warning                                       | Dealer      | Discriminative | ★★★   | S      | 2     |
| T1  | Vehicle fuel-consumption anomaly (fuel theft)                      | Transporter | Discriminative | ★★★★★ | M      | 2     |
| T2  | Refuel prediction & smart reorder                                  | Transporter | Discriminative | ★★★   | S      | 2     |
| T3  | Best-pump recommendation on route                                  | Transporter | Discriminative | ★★★   | M      | 3     |
| T4  | Credit headroom forecast                                           | Transporter | Discriminative | ★★★   | S      | 2     |
| T5  | Driver reliability score                                           | Transporter | Discriminative | ★★★   | S      | 3     |
| P1  | Fuel rate intelligence (trends, benchmarks)                        | Both        | Discriminative | ★★★   | S      | 2     |
| P2  | Dealer ↔ transporter matchmaking                                   | Both        | Discriminative | ★★★   | M      | 3     |
| G1  | "Dzzlo Sathi" conversational assistant (text+voice, Hindi/English) | Both        | Generative     | ★★★★★ | M      | 1     |
| G2  | Voice-first order placement                                        | Transporter | Generative     | ★★★★★ | M      | 2     |
| G3  | WhatsApp AI agent (incl. drivers, no app needed)                   | Both        | Generative     | ★★★★★ | L      | 3     |
| G4  | Smart collections messaging (auto-drafted dunning)                 | Dealer      | Generative     | ★★★★  | S      | 1     |
| G5  | Narrated business reports (monthly review, tax explainers)         | Both        | Generative     | ★★★★  | S      | 1     |
| G6  | Document intelligence (RC / DL / invoice scan onboarding)          | Both        | Generative     | ★★★★  | M      | 2     |
| G7  | Dispute evidence pack generator                                    | Both        | Generative     | ★★★   | S      | 2     |
| G8  | Semantic search → structured filters                               | Both        | Generative     | ★★★   | S      | 2     |
| G9  | Onboarding & support copilot (deep-dive: doc 05)                   | Both        | Generative     | ★★★   | S      | 2     |
| G10 | Superadmin analytics copilot (internal)                            | VSYST       | Generative     | ★★★   | S      | 1     |

Effort: S = weeks, M = 1–2 months, L = a quarter+. Value stars are judgment calls argued in the feature docs.

## Reading Order

1. **[01 — Data Foundation](01-data-foundation.md)** — what we have, what's missing, what to start capturing _now_ (cheap schema additions that unlock everything later)
2. **[02 — Discriminative AI Features](02-discriminative-ai-features.md)** — the prediction/scoring/anomaly catalog
3. **[03 — Generative AI Features](03-generative-ai-features.md)** — the assistant/voice/content catalog + hallucination guardrails
4. **[04 — Roadmap & Architecture](04-roadmap-and-architecture.md)** — phases, where the AI services live, build-vs-buy, costs, risks
5. **[05 — RAG Support Agent](05-rag-support-agent.md)** — deep-dive on building & deploying our own support agent: a knowledge base derived from our code/docs, hybrid RAG on Atlas, live tool calls, and a no-retraining learning loop

## Related

- [Custom Mixpanel analytics plan](../custom-mixpanel/00_README.md) — the event-tracking platform is **Phase 0** of this AI plan; behavioral events feed churn, adoption, and assistant-quality metrics.
- `dzzlo_oms_api/docs/ARCHITECTURE.md` and `docs/AI_CONTEXT.md` — backend patterns the AI services must follow.
