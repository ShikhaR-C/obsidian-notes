# 05 — Our Own Support Agent: RAG over Company Docs, Code & Business Logic

> **The question:** can we build and deploy our own AI agent that learns the business logic we provide, understands our screens/pages/APIs from company docs and project code, and answers customer (dealer + transporter) support queries?
>
> **The answer: yes — and the architecture is: pre-trained LLM + a knowledge base we derive from our own repos + live tool calls + a feedback loop.** The agent's "learning" happens in the knowledge base and the evaluation loop, not by training model weights. This doc is the how. It is the deep-dive behind **G1 (Dzzlo Sathi)** and **G9 (support copilot)** from [doc 03](03-generative-ai-features.md).

---

## 1. What "an agent that learns" actually means

A common misconception first: we do **not** teach the model our business by fine-tuning it on our code. Fine-tuning bakes knowledge into weights — it goes stale on every release, can't cite sources, hallucinates confidently, and costs GPU money to refresh. Instead, the agent "learns" through three channels that are all **updatable in minutes, auditable, and versioned in git**:

| Channel                    | What it teaches                                                  | How it updates                           |
| -------------------------- | ---------------------------------------------------------------- | ---------------------------------------- |
| **Knowledge base (RAG)**   | Product how-to, business rules, error explanations, policies     | Re-ingest on every release / doc edit    |
| **Tools (function calls)** | The user's _live account state_ — their orders, balances, limits | Always current (reads `api_v3` services) |
| **Feedback loop**          | What users actually ask, where answers fail                      | Weekly gap-mining → new KB articles      |

The model itself (Claude, or self-hosted — §6) stays frozen. That's a feature: no catastrophic forgetting, no retraining pipeline, and a one-line rollback (point the retriever at the previous KB version).

**Why RAG alone is not enough for DZZLO support:** half of real support queries are not answerable from documentation. "Why can't I place an order?" has a _personal_ answer — the relation is at its credit limit, or the dealer hasn't set today's rate, or the user's scope is `CView`. So the agent needs **RAG for the rules + tools for the user's state**, and the generation step combines both: _"Aapka order block hai kyunki Verma Fuels ke saath outstanding ₹2.9L hai aur limit ₹3L (rule: orders block at limit — [article]). ₹85k ka invoice due hai; payment hone par order ja payega."_ This is exactly the tool layer G1 builds — the support agent reuses it.

---

## 2. What the agent must know, and where it lives in our repos

Three knowledge types, three extraction strategies:

### A. Product how-to ("how do I add a driver?")

| Source                                                                              | What we extract                                                                                                                           |
| ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `dzzlo_oms_app/src/screens/**` + navigation files (`navigation/{Customer,Dealer}/`) | Screen inventory, per-role menu structure, step-by-step paths ("Drawer → Vehicles → Add Driver")                                          |
| `src/utils/Conditional/Scopes.js` + `api_v3/auth.js` scope guards                   | **Permission matrix**: which of the 12 scopes (`CPrimary…DView`) sees/does what — answers the entire "why can't I see X?" question family |
| App `docs/`, `AI.md`, Help/FAQ content, this obsidian vault                         | Curated explanations, policies, onboarding guides                                                                                         |

### B. Business rules ("why was TCS charged?" / "when do orders block?")

| Source                                                                                              | What we extract                                                                                                                                                                                   |
| --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api_v3/services/order_msts.js` (`canTransact`, credit check, `assertDieselQtyLimit`, OTP validity) | Order lifecycle rules: verification requirements, credit-block math, diesel qty caps, 10-min OTP expiry, full-tank logic                                                                          |
| `helpers/Credit/index.js` + `dealer_custs` model                                                    | Credit model: UNLIMITED (null) / BLOCKED (0) / CAPPED, advance-deposit math, billing periods                                                                                                      |
| `api_v3/services/dealer_custs.js`, `voc_msts.js`, `invs.js`                                         | Statement/FY logic (April–March, IST), TCS 206C / TDS 194Q (0.1%) conditions, voucher approval flow, FIFO invoice settlement                                                                      |
| **Error catalog** — every `throw`/error response string in `api_v3/services/*.js`                   | The exact texts users see on screen, each mapped to cause → resolution → who can fix it. This single artifact answers the largest share of support tickets ("app bol raha hai _X_ — matlab kya?") |
| `helpers/versionGate.js` + `counters` config                                                        | Update-prompt / force-update behavior per app version                                                                                                                                             |

### C. Live account state ("why can't **I** order **right now**?")

Not KB material — **tools**, same registry as G1: `get_relation_balance`, `get_credit_status`, `list_open_invoices`, `get_todays_rate`, `get_user_scope`, `get_order`, `get_otp_status`. Executed with the caller's JWT + `x-co-id`; tenancy enforced by the service layer, not the prompt.

> **Key design decision:** raw code is _not_ what we embed. Code chunks retrieve badly for end-user questions and leak implementation detail. We run a **derivation pipeline** (code → reviewed articles) and embed the articles. Code is the _source of truth_; articles are the _retrieval surface_.

---

## 3. Knowledge base construction pipeline (code → KB)

```
┌── Extract (deterministic, per release) ─────────────────────────┐
│ route table (api_v/api3.js) · error catalog (grep throws)       │
│ scope matrix (Scopes.js) · enum/limits catalog (models, counters)│
│ screen map (navigation/*) · entity glossary (AI.md)             │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌── Author (LLM-assisted, human-reviewed) ────────────────────────┐
│ Claude drafts persona-split articles from extracted facts +     │
│ code excerpts: one article = one question family                │
│ ("Order blocked at credit limit — why & what to do" ×2 personas)│
│ → PR into obsidian-notes/…/support-kb/ → human review → merge   │
└──────────────┬──────────────────────────────────────────────────┘
               ▼
┌── Index (ingestion worker) ─────────────────────────────────────┐
│ chunk per article section (~300–800 tokens, keep headers)       │
│ metadata: {persona, screens[], feature, error_codes[], lang,    │
│           app_version_range, source_files[], kb_version}        │
│ embed (multilingual model) → upsert MongoDB Atlas Vector Search │
│ + Atlas Search (BM25) index on the same collection              │
└─────────────────────────────────────────────────────────────────┘
```

Notes:

- **The KB lives in git as markdown** (this vault is the natural home: `support-kb/` sibling to these docs). Review = PR review. Every article footer cites its source files, so when `order_msts.js` changes, `git diff` tells the pipeline which articles to regenerate — stale-KB detection is a CI step, not a hope.
- **Persona-split is mandatory.** The same feature reads differently per side (dealer processes the OTP; transporter's driver receives it). Retrieval filters on `persona` from the JWT role — a dealer never retrieves customer-flow steps.
- **Version-aware.** We run version-gated clients (v1.68–v1.78 behave differently, e.g. the legacy credit-limit shim). Chunks carry `app_version_range`; the app already sends its version in the `meta` header on every request — the retriever filters on it.
- **Embeddings:** a multilingual model is non-negotiable (queries arrive in Hinglish/Hindi). Hosted: Voyage `voyage-multilingual`. Self-host option: `bge-m3` on CPU (fine at our KB scale: a few thousand chunks). Atlas Vector Search means **zero new infrastructure** — we're already on Atlas, and hybrid (vector + BM25) needs one extra index, not a new vendor.

---

## 4. The serving pipeline (a query's life)

```
user msg (+ screen context) → /api/v3/ai/support/chat
  1 preprocess: language detect · PII strip · load user role/scope/app-version
  2 route (small model):  HOW_TO | ACCOUNT_STATE | MIXED | BUG_REPORT | ESCALATE
  3a HOW_TO      → hybrid retrieve (vector + BM25, RRF-fused, filtered by
                   persona/version/screen) → rerank → top 3–6 chunks
  3b ACCOUNT_*   → tool calls (G1 registry, caller's JWT)
  4 generate: grounded answer, citations [article-id], numbers verbatim
     from tool JSON, steps as deep links (screen names from KB metadata)
  5 guardrail: no chunk over relevance floor OR model signals uncertainty
     → "I don't know" + one-tap escalate (ContactUs flow + transcript summary)
  6 log to ai_conversations {query, chunks, tools, answer, feedback}
```

Details that make or break quality:

- **Hybrid retrieval, not vector-only.** Support queries are full of exact tokens — error strings, "TDS", "OTP", truck numbers — where BM25 beats embeddings; paraphrased Hinglish questions are where embeddings beat BM25. Fuse both (reciprocal-rank fusion), then rerank (LLM-as-reranker on 20 → 5, or a hosted rerank API).
- **Screen awareness is cheap and powerful.** The app knows its current route (React Navigation state). Send `screen: "NewOrder"` with the query; chunks tagged `screens:["NewOrder"]` get a retrieval boost. "Yeh full tank kya hai?" asked _on the order screen_ resolves instantly. Answers link back: the assistant returns `deeplink: "Vehicles/AddDriver"` and the app renders a "Take me there" button — this is the "understands the screen/page" requirement, solved with metadata rather than vision. (Vision — reading user screenshots — is a Phase-3 nicety via Claude's image input; don't start there.)
- **Escalation is a feature, not a failure.** Deflection targets of 100% produce lying bots. Uncertainty → hand off to the existing `ContactUs` path with an auto-drafted summary (user, screen, query, what the agent tried, relevant account state) — support staff love this even when the bot couldn't answer.
- **The iron rule from doc 03 applies unchanged**: financial figures only from tool JSON; KB text explains _rules_, never _amounts_.

---

## 5. The learning loop (how it gets smarter without retraining)

1. **Feedback capture:** 👍/👎 + optional reason on every answer; implicit signals (user escalated anyway, user repeated the question) — all in `ai_conversations`.
2. **Gap mining (weekly cron + G10 copilot):** cluster unanswered/👎 queries → ranked list of missing articles → LLM drafts them from the relevant code/doc sources → human review PR. The KB grows along the _actual_ demand curve, not our guesses.
3. **Release hook (CI):** on each `dzzlo_oms_api`/`dzzlo_oms_app` release: re-run extractors → diff against KB source-file citations → regenerate stale articles → re-embed changed chunks → bump `kb_version`. The bot never describes last release's UI.
4. **Eval gate:** a golden set (~150 real questions × expected article/answer facets, both personas, EN+HI) runs on every KB change and every prompt change — retrieval hit-rate, groundedness (answer claims ⊆ retrieved chunks + tool results), refusal correctness. Regression blocks the deploy, same discipline as the Jest suites.
5. **(Optional, later) fine-tuning finds its real jobs:** distilling the router onto a tiny model, teaching a self-hosted model our answer style/format. Never for knowledge.

---

## 6. Deployment: how "our own" do we want it?

Three rungs — the moat is the KB + tools + eval data in every case; the weights are a commodity:

|                              | **A. Own agent, hosted LLM** ⭐ recommended | B. Hosted open-weights                                          | C. Fully self-hosted                                                                         |
| ---------------------------- | ------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Model                        | Claude API (Haiku routine / Sonnet complex) | Llama/Qwen-class via Bedrock/managed endpoint (ap-south region) | Open-weights on our GPU box (vLLM/Ollama)                                                    |
| We own                       | KB, retrieval, tools, prompts, evals, logs  | + region/data residency                                         | + the weights & runtime                                                                      |
| Quality (Hinglish, tool use) | Best                                        | Good                                                            | Model-dependent; tool-calling reliability is the usual pain                                  |
| Ops burden                   | None new                                    | Low                                                             | GPU server (~₹1.5–3L/yr for a modest 24GB card cloud/on-prem), patching, scaling, monitoring |
| Cost at our scale            | Low hundreds $/mo (see doc 03 §cost)        | Similar+                                                        | High fixed, low marginal — wins only at very large volume                                    |
| When it's right              | Now → foreseeable future                    | If DPDP posture / a large customer demands residency            | Only if contractually forced or at 100× today's scale                                        |

Start at **A** behind the `services/ai/llm.js` adapter (doc 04) — swapping rungs later is a config change, not a rewrite. PII minimization (doc 01 §5) applies at every rung.

**Where it runs (extends doc 04's diagram, no new services):** ingestion + release hooks in the **ai-worker**; `/ai/support/chat` (SSE) in `api_v3/services/ai/support/`; KB collection + vector/BM25 indexes in the existing Atlas cluster; chat UI = the G1 screen with a "Help" entry point replacing the static `Help` screen; Remote Config gates rollout (internal → beta dealers → all).

---

## 7. Build plan & effort

| Step | Deliverable                                                                                                                   | Effort                               |
| ---- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| 1    | Extractors: error catalog, scope matrix, screen map, rules sheets                                                             | ~1 wk                                |
| 2    | KB v1: ~60–100 reviewed articles (top ticket drivers first: OTP, credit blocks, rate not set, payment approval, verification) | 1–2 wk (LLM-drafted, human-reviewed) |
| 3    | Atlas vector + BM25 indexes, ingestion worker, hybrid retriever + rerank                                                      | ~1 wk                                |
| 4    | Serving endpoint on the G1 chassis (router, grounding, citations, escalation) + chat UI Help entry                            | 1–2 wk                               |
| 5    | Golden-set eval harness in CI; feedback capture                                                                               | ~1 wk                                |
| 6    | Pilot (internal + 10 friendly companies), gap-mining loop running                                                             | 2 wk                                 |

≈ **6–8 engineering weeks to a piloted v1**, riding on Phase-1's G1 work (if G1 ships first, steps 3–4 are halved). KPIs: deflection rate (target 40–60% of `ContactUs` volume within a quarter), groundedness ≥ 99% on eval, CSAT 👍 ≥ 80%, unanswered-rate trending down week-over-week, support time-to-resolution on escalated tickets (the summary should cut it ~half).

## 8. Risks specific to this feature

| Risk                                                                 | Mitigation                                                                                                  |
| -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Stale KB after a release describes old UI                            | CI release hook + source-file citations (§5.3) — staleness is _detected_, not discovered by users           |
| Confident wrong how-to steps                                         | Groundedness eval gate; citations rendered in UI; 👎 fast-path to human                                     |
| Answering across tenant/persona lines                                | Retrieval filters from JWT (persona) + tools already tenancy-scoped; red-team set in eval                   |
| Prompt injection via user text or KB content                         | KB is human-reviewed (trusted); user text delimited as data; tool allowlist per surface (doc 03 §Grounding) |
| Hinglish/code-mixed retrieval quality                                | Multilingual embeddings + BM25 hybrid; golden set includes code-mixed queries from day one                  |
| Bot answers policy questions it shouldn't (refunds, disputes, legal) | Route class `ESCALATE` with an explicit topic blocklist → always human                                      |

---

**Bottom line:** we can absolutely deploy our own support agent, and we should build it as _owned knowledge + owned tools + rented intelligence_: a git-versioned KB derived from our code and docs (so it "understands" every screen, page, API, and rule), Atlas-native hybrid RAG, the G1 tool layer for live account answers, and a feedback loop that turns real user questions into KB growth. The model weights are the least interesting part — everything that makes the agent _ours_ is in the pipeline this doc describes.
