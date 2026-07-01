# 04 — Roadmap & Architecture

> How the catalog in docs 02–03 becomes shipped software: phasing, where the AI lives in our stack, build-vs-buy, and the risks that can sink it.

---

## 1. Prioritization Logic

Three questions rank every feature:

1. **Does it need new data?** If yes (odometer, tank capacity, delivered qty), the *capture* ships now, the feature ships later. If no (credit scoring, assistant, narrated reports), it can ship in weeks.
2. **Wrong answer cost?** A wrong push nudge is free; a wrong credit grade or theft accusation is expensive → those need heuristic-first rollout, reason codes, and confirm loops.
3. **Does it compound?** G1's tool layer is reused by G2/G3/G8/G9; D1's score feeds D2/D3/G4/P2; `ai_outcomes` labels train everything. Build the compounding pieces first.

## 2. Phased Roadmap

### Phase 0 — Foundations (immediately, alongside regular releases)

| Item | What ships | Why now |
|---|---|---|
| Schema additions | `odometer`, `tank_capacity` + `veh_type`, `delivered_qty`, `delete_reason`, `cr_limit_history[]`, `lang` (doc 01 §2) | Data accrues while we build; T1/D6/D2 blocked without it |
| `ai_outcomes` collection | Event-sourced label store | Free training labels from day one |
| Feature-store crons | Nightly aggregations → `ai_features_*` collections (doc 01 §3–4) | Powers every heuristic v0; also improves existing reports |
| Analytics events | The [custom-mixpanel plan](../custom-mixpanel/00_README.md), at least order/payment funnels | Churn features + AI-feature KPIs need it |
| G10 internal copilot | NL → Mongo aggregation for VSYST ops | Team learns tool-use patterns risk-free |

**Exit criteria:** cron-built features refreshing nightly; new fields visible in app forms; first `ai_outcomes` events flowing.

### Phase 1 — Trust the Language Layer (months 1–3)

Read-only genAI + zero-ML heuristics. Nothing here can corrupt a ledger.

- **G1 Dzzlo Sathi** (text, Hindi/English, read-only tools) — the flagship
- **G5 narrated monthly review** (cron + template)
- **G4 collections drafts** + **D3 heuristic worklist** (amount × age × late-rate)
- **D6 order guard v0** (soft warnings in order flow)
- **G7 dispute evidence pack** (deterministic + narration)

**Exit criteria:** assistant weekly-active ≥ 20% of app WAU; zero financial-figure hallucinations in eval suite; D3 worklist used by ≥ 30% of active dealers.

### Phase 2 — Predict & Act (months 3–9)

First trained models (on Phase-0/1 accumulated labels) + first write-path genAI.

- **D1 credit score** (scorecard → GBT) with reason codes; **D2 limit recommender**; **T4 headroom forecast** + proactive pushes
- **T1 fuel anomaly v0→v1** (odometer data from Phase 0 starts paying off); **T2 refuel nudges** with pre-filled drafts
- **D4 demand forecast + refill planner**; **D5 shrinkage control charts** (DIP)
- **G2 voice ordering** (confirm-always); **G6 document intelligence** (RC + fuel slip first); **G8 semantic filters**; **G9 onboarding copilot**; **P1 rate benchmarks**; **D7 churn flags**

**Exit criteria:** D1 calibration (E-grade default rate ≥ 5× A-grade); T1 confirmed-anomaly precision ≥ 60%; voice-order edit rate < 20%; measurable DSO drop in pilot dealers.

### Phase 3 — Ubiquity & Network (months 9–18)

- **G3 WhatsApp agent** (dealers/transporters, then drivers — photos feed T1/G6)
- **T3 best-pump ranking**; **P2 matchmaking** (network growth); **T5 driver scores**
- Model upgrades across D-features from accumulated `ai_outcomes`; regional-language voice
- Pricing/packaging: fleet-intelligence (T1/T2/T5) and credit-intelligence (D1/D2/D3) as **premium tiers** — these are the features with direct, provable ₹ ROI

## 3. Architecture

**Principle: AI is a layer over the existing service layer, never a bypass.** Same Mongo, same auth, same tenancy — new code lives in `api_v3/services/ai/` plus one background worker.

```
┌────────────────────────── clients ──────────────────────────┐
│  dzzlo_oms_app (RN)        dip-web         WhatsApp (Ph. 3) │
│  chat UI · voice · cards   planner/alerts  BSP webhook      │
└──────────────┬──────────────────┬──────────────┬────────────┘
               │ JWT + x-co-id (unchanged)       │
┌──────────────▼──────────────────▼──────────────▼────────────┐
│                dzzlo_oms_api (Express, api_v3)               │
│                                                              │
│  routes/ai/*  ──────────►  services/ai/                      │
│   POST /ai/chat (stream)     assistant.js  (agent loop)      │
│   POST /ai/parse-order       tools/        (wraps existing   │
│   POST /ai/parse-doc         │              services w/ scope│
│   GET  /ai/insights/:type    │              checks — the ONLY│
│                              │              data gateway)    │
│                              prompts/ · guardrails/ · eval/  │
│                                   │                          │
│  existing services/ (order_msts, dealer_custs, invs, …)      │
│  ← tools call THESE, never raw models                        │
└───────┬──────────────────────────────────┬──────────────────┘
        │                                  │ Claude API (Haiku/Sonnet,
┌───────▼────────────┐                     │  tool use · vision · batch)
│  ai-worker (PM2)   │                     ▼
│  nightly features  │            ┌─────────────────┐
│  scores D1–D7,T1..│             │ external: 2Factor│
│  monthly reviews G5│            │ OneSignal · SES  │
│  alerts → OneSignal│            │ WhatsApp BSP     │
└───────┬────────────┘            └─────────────────┘
        ▼
  MongoDB Atlas: existing collections + ai_features_* · ai_outcomes ·
  ai_conversations · ai_insights   (+ DIP DB read access for D4/D5)
```

Key decisions:

| Decision | Choice | Rationale |
|---|---|---|
| Where does AI code live? | Inside `dzzlo_oms_api` (`api_v3/services/ai/` + separate PM2 worker process), not a new microservice | Reuses auth/tenancy/service layer; team is one codebase-fluent unit; extract later if load demands |
| Model serving for D-features | **No model server.** v0 heuristics = aggregation code; v1 models = train offline (Python/scikt-learn or XGBoost in a notebook/repo), export coefficients/trees to JSON, score in Node inside the worker | Logistic/GBT scoring is trivial arithmetic; avoids Python service ops on our 2-EC2 footprint |
| LLM provider | Claude API (Haiku default, Sonnet for complex/vision, Batch API for G5) via `services/ai/llm.js` adapter | Tool-use quality, vision, Hindi fluency; adapter keeps us swappable |
| Streaming | SSE on `/ai/chat` | RN fetch-stream friendly; no socket infra (socket.io is dormant) |
| Feature flags | Firebase Remote Config (app) + `counters` config docs (API) — both exist | Staged rollouts per company/version; kill switches per AI feature |
| Conversation state | `ai_conversations` (messages + tool traces + feedback), TTL for raw content, aggregates retained | Evaluation, debugging, and DPDP-compliant retention |
| Evaluation | `eval/` suite: golden Q&A set per tool, ₹-figure == tool-trace assertion, jailbreak set; runs in CI like existing Jest suites | The hallucination guarantee is a *test*, not a hope |

## 4. Build vs Buy

| Capability | Verdict | Notes |
|---|---|---|
| LLM | **Buy** (Claude API) | Never self-host for our scale |
| Speech-to-text | **Platform** (Android SpeechRecognizer / iOS Speech) first; hosted STT only if quality forces it | Free, offline-capable, Hindi support |
| Credit scoring | **Build** | Our data moat; scorecard math is not vendor-worthy |
| Time-series forecasting | **Build** (classical methods) | Prophet-class problems |
| WhatsApp | **Buy** BSP (Gupshup/Twilio/Meta direct) | Compliance + template machinery |
| OCR/doc parsing | **Buy** (Claude vision) | vs. dedicated OCR vendors: one API for parse+reason |
| Analytics/events | **Build** (custom-mixpanel plan already decided) | — |
| Vector DB / RAG infra | **Defer** | Only G9 help-RAG needs embeddings; Mongo Atlas Vector Search when needed — no new vendor |

## 5. Risks & Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Hallucinated financial figures destroy trust in one screenshot | Fatal | Iron rule + eval assertions (doc 03 §Grounding); numbers rendered from tool JSON, not model prose, wherever UI allows |
| Wrong theft/fraud accusation (T1/D5/T5) damages a livelihood | High | Language discipline: "unusual pattern — worth checking", never "theft"; evidence always attached; transparent math (control charts, z-scores) over black boxes |
| Credit score becomes self-fulfilling (low grade → less credit → business dies) | High | Reason codes + "how to improve" path; dealer sets limits, we only inform; monitor grade-migration fairness quarterly |
| Alert fatigue (D3/D6/T1/T2 all push) | Medium | Unified notification budget per user/day; digest-first defaults; per-feature opt-outs in existing `notif[]` prefs |
| Cost blowout on LLM tokens | Medium | Tier routing, per-user caps via Remote Config, Batch API for crons, monthly cost dashboards (G10 can report on itself) |
| DPDP / data-to-third-party exposure | High | PII minimization to LLM APIs; DPA with provider; consent copy at onboarding; driver phone redaction |
| Prompt injection via remarks/documents/WhatsApp | Medium | Data-vs-instruction delimiting, tool allowlists per surface, no tool that dumps raw collections |
| Team bandwidth (small team, big catalog) | High | The phasing *is* the mitigation: Phase 1 is ~2 engineer-quarters of work; every phase ships standalone value even if the plan stops there |
| Low-end devices / patchy connectivity | Medium | Server-side inference only; streaming text degrades gracefully; voice uses on-device STT; WhatsApp surface (Ph. 3) is the ultimate low-end fallback |

## 6. What Success Looks Like (12–18 months)

- **For dealers:** bad-debt ₹ per ₹ credit extended down measurably in pilot cohort; DSO down 15–20%; refill stockouts near zero on DIP pumps; "the app that warns me before a customer goes bad."
- **For transporters:** fuel ₹/vehicle/month down 5%+ from anomaly detection alone; zero stranded-truck credit blocks (T4); routine orders placed in under 20 seconds by voice; "the app that caught my diesel leak."
- **For VSYST:** AI features drive the premium tier; assistant deflects majority of support load; the `ai_outcomes` dataset itself becomes the defensible asset — nobody else has OTP-verified fuel-transaction + credit-behavior data at this granularity.

The sequencing bet, in one line: **ship the language layer first (it needs nothing new and wins hearts), capture the missing data in parallel, then let the scores and forecasts arrive on data that's been quietly accumulating since day one.**
