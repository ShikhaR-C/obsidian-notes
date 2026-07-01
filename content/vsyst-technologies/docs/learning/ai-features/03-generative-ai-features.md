# 03 — Generative AI Features (Assistants, Voice, Content, Documents)

> Generative AI gives DZZLO a *conversational and multilingual surface* over data the platform already serves through structured endpoints — and hands: drafting messages, filling forms, reading documents. Our users (pump dealers, truck owners, drivers) are often more comfortable **speaking Hindi/Hinglish/regional languages than navigating English UI** — the app is English-only today with no i18n. GenAI leapfrogs that gap: the LLM can converse in any language *now*, without translating a single UI string.

**The iron rule for everything below:** the LLM **never computes or recalls financial figures from its own head**. Every number (outstanding, rate, quantity, due date) comes from a **tool call into existing `api_v3` services**, and every write action goes through the same validated endpoints with the user's own JWT + scopes. The LLM is a language layer, not a ledger. (Details in §Grounding.)

---

## G1 — "Dzzlo Sathi" Conversational Assistant ⭐ flagship, build first

**What:** A chat (and later voice) assistant inside the app answering natural-language questions over the user's own data, in their language:

- *Dealer:* "Sharma Transport ka kitna outstanding hai?" → "₹1,42,300 outstanding — 2 invoices: ₹85,000 (due 4 din mein) aur ₹57,300 (12 din overdue). Reminder bhejein?" (hands off to G4)
- *Dealer:* "Aaj kitna diesel bika?" → today's `so_msts` totals per product
- *Transporter:* "Is mahine sabse zyada diesel kis truck ne liya?" → per-vehicle rollup; "Verma Fuels mein kitna credit bacha hai?" → live headroom (same math as T4)
- Either: "GST invoice kya hota hai / TCS kyon kata?" → grounded explainer (docs + relation's `taxStatus`)

**Why first:** highest value-to-effort of the entire plan. It needs **zero new data** — the endpoints exist (`/cust_msts/app/currbal`, `/order_msts/a/poso`, statements, rates), the auth/scoping exists, and it makes every later feature more valuable (scores and forecasts become *conversations*). It's also the wedge for voice (G2) and WhatsApp (G3).

**How:**
- Claude with **tool use**: define ~12–20 read-only tools that wrap existing v3 service functions (`get_relation_balance`, `list_orders`, `get_invoice`, `get_rates`, `get_vehicle_consumption`, `get_statement`…). Tools enforce `x-co-id` + scope exactly like HTTP routes — the model literally cannot see another tenant's data because the tools won't return it.
- Role/scope-aware system prompt (a `CView` accountant gets read-only framing; drivers aren't users, so no driver persona in-app — that's G3's job).
- New `api_v3/services/ai/assistant.js` + one streaming endpoint; chat UI as a new screen with the app's existing bottom-sheet patterns. Log every conversation + tool trace to `ai_conversations` for evaluation.
- Model tiering: Haiku-class for routine Q&A, Sonnet-class for multi-step queries — router on intent.

**KPIs:** weekly active assistant users; % questions resolved without a tool error; deflected support contacts (`ContactUs`); follow-through on suggested actions.

## G2 — Voice-First Order Placement

**What:** The transporter (or their munshi) speaks: *"Kal subah ke liye MH12 AB 1234 mein 400 litre diesel, Verma Fuels se"* → the assistant parses to a structured draft: vehicle (fuzzy-matched to `veh_msts.veh_reg_no`), dealer (verified relations only), product + quantity, shows the same review screen as `NewOrder` with rate and credit check applied → user taps confirm → normal `POST /order_msts` path (OTP flow unchanged).

**Why it matters:** the 6-step `NewOrder` builder is thorough but heavy for a daily routine task, and typing is the barrier for many users. Voice + confirmation collapses it to ~15 seconds. Combined with T2's pre-filled drafts, routine ordering becomes near-zero-effort — this is the retention feature.

**How:** on-device speech-to-text (Android `SpeechRecognizer`, free, works with Hindi/Hinglish) → text to Claude with a strict JSON schema (structured output) + tools for vehicle/dealer/product lookup → **always a visual confirm step, never auto-submit**. Ambiguity (two matching trucks) → one clarifying question. Every parse logged with the final submitted order as the label — free training data for intent accuracy.

**KPIs:** voice-order share; parse-to-confirm edit rate (target < 20%); order abandonment.

## G3 — WhatsApp AI Agent (the app-less surface)

**What:** A WhatsApp Business number where dealers and transporters can do G1 + G2 (query balances, place/track orders, receive invoices as PDFs — Puppeteer PDFs already exist), and — the unlock — **drivers**, who are *not app users*, interact for the first time: receive OTP + order details, send back the odometer photo / dispensed-quantity slip photo (feeding doc-01 gaps #1/#4 via G6's vision parsing).

**Why:** India's B2B SMB reality — WhatsApp *is* the OS. Dealers already forward PDFs manually. This extends DZZLO to users who will never install the app, and it's a moat: order-on-WhatsApp with OTP-verified delivery and instant ledger answers.

**How:** WhatsApp Business API (Meta BSP e.g. Gupshup/Twilio — we already integrate 2Factor for SMS, similar vendor motion). Phone-number → `users`/`dvr_msts` identity mapping with strict verification; session tokens per conversation; same tool layer as G1. Template messages for proactive pushes (mirrors OneSignal events: NewOrder, ApprovedPayment…). This is Phase 3 — biggest lift (BSP onboarding, template approvals, identity), biggest reach.

**KPIs:** MAU on WhatsApp surface vs app; driver photo-submission rate (fuels T1); order share via WhatsApp.

## G4 — Smart Collections Messaging

**What:** For each invoice D3 flags, auto-draft a **polite, personalized, culturally-calibrated reminder** in the customer's language — firmness graded by aging and relationship history (first nudge friendly; 45-day overdue references the `max_cr_days` terms), always **dealer-approves-then-sends** (SMS/email now, WhatsApp later). Collections is *the* awkward conversation in Indian trade credit — drafting is exactly what LLMs are for; the dealer keeps the relationship judgment.

**How:** Claude with invoice/relation context (numbers injected from tools, D1 reason codes optional); templates constrained to DLT-approved SMS formats where SMS is the channel; send + response logged to `ai_outcomes` (label source for D3's reminder-response model).

**KPIs:** reminder→payment conversion vs manual baseline; DSO; % drafts sent unedited.

## G5 — Narrated Business Reports

**What:** The existing reports (`DailyReport` totals, TCS/TDS, ledgers) get a plain-language layer: a **monthly business review** per company — "June: sales ₹18.2L (+12% MoM). Top customer Gupta Roadlines slowed payments 9→16 days. Diesel margin thinned ₹0.18/L after your June 14 rate cut. 3 customers idle 3+ weeks (list)." Plus inline explainers: "TCS @0.1% applied because this relation crossed ₹50L turnover (`lysal`)."

**Why:** dealers/owners are businesspeople, not analysts — tables don't tell them *what changed and what to do*. This is the cheapest genuinely-loved feature: pure summarization over aggregates we already compute, delivered as push + email (SES) + in-app card.

**How:** monthly cron → aggregate pack per company (JSON) → Claude with a tight template → render. Numbers come only from the pack (§Grounding); the LLM contributes selection, comparison, and language. Hindi/English per user pref.

**KPIs:** open/read rate; actions taken from review (limit changes, reminders sent); NPS mentions.

## G6 — Document Intelligence (vision)

**What:** Camera → structured data, killing the highest-friction forms:
- **Vehicle RC** → `veh_reg_no`, vehicle class, fuel type, tank capacity → auto-fill `AddVehicle` (and fill doc-01 gap #2 retroactively for the whole fleet)
- **Driver licence** → `AddDriver` fields
- **Fuel slip / DU display photo** → `delivered_qty` at delivery (gap #4), odometer photo → km (gap #1)
- **Tanker invoice at decant** (DIP) → invoiced litres vs dip-measured, feeding D5's short-delivery check
- **Legacy paper ledgers** → opening-balance import at onboarding (today's `cust_bal[]` entry is manual and error-prone)

**How:** Claude vision with per-document JSON schemas + validation (plate regex already exists in `veh_msts`; cross-check RC number vs claimed plate). Human-confirm screen always. ImageKit already hosts images. Start with RC + fuel slip (highest volume × highest downstream value).

**KPIs:** onboarding time per vehicle/driver; % fields auto-filled correctly; delivered-qty capture rate.

## G7 — Dispute Evidence Pack

**What:** One tap on any order/invoice → chronological narrative + document bundle: PO placed (time, user, device), OTP sent to driver X (2Factor delivery receipt from `otp_by.response`), verified at HH:MM, SO, invoice, payments — as a shareable PDF. Turns "hamne yeh order diya hi nahi" disputes from hour-long phone fights into a 30-second forward.

**How:** deterministic data assembly (all joins exist — `multipleOrderRes` does most of it) + LLM narration + existing Puppeteer PDF pipeline. Trivial build, outsized trust dividend — the OTP audit trail is DZZLO's core differentiator; this feature *showcases* it.

## G8 — Semantic Search → Structured Filters

**What:** The search bars become natural-language: "pichhle mahine ke full-tank orders jo abhi tak invoice nahi hue" → the assistant translates to the exact filter params the list endpoints already accept (`order_status`, date range, `is_full_tank`, dealer). No new query engine — LLM as filter compiler, results render in the existing FlashList screens. Cheap (Haiku-class), delightful, and teaches users what filters exist.

## G9 — Onboarding & Support Copilot

**What:** Guided conversational setup for new companies (dealer: products → daily-rate habit → credit policy per customer; transporter: fleet → drivers → dealer connections) plus an always-on "how do I…" help bot grounded on our docs/FAQ + screen context. Attacks activation drop-off — a dealer who never sets rates or verifies relations never transacts. Reuses G1's chassis with a different toolset (`setup_product`, `invite_customer`…) and RAG over help content.

## G10 — Superadmin Analytics Copilot (internal, week-one candidate)

**What:** For VSYST ops: natural language → MongoDB aggregation over the platform (read-only replica): "WoW GMV by state", "dealers with falling order counts", "OTP failure rate by telecom circle this month". Zero end-user risk, immediate internal value, and it builds the team's tool-use muscle before user-facing launches. Guardrails: read-only connection, query allowlist/review, result-size caps.

---

## Grounding & Safety Rules (apply to every G-feature)

1. **Numbers only from tools.** System prompts forbid arithmetic on financial values; assistants call `get_*` tools and quote results verbatim. If a tool fails → "abhi data nahi mila" — never an estimate. Evaluation suite asserts every ₹ figure in output matches a tool-trace value.
2. **Writes are proposals.** Order placement, reminders, limit changes: LLM drafts → deterministic validation (same service-layer guards: `canTransact`, credit check, diesel qty cap) → **human confirms** → existing endpoint executes. The model holds no write authority of its own.
3. **Identity & tenancy.** Tools execute with the caller's JWT/scopes/`x-co-id`; the model layer adds no privilege. WhatsApp adds phone-verification binding before any data access.
4. **Prompt injection**: user-supplied text (remarks, product names, scanned documents) is data, not instructions — delimit and instruct accordingly; tool results are typed JSON, not prose the model re-interprets.
5. **PII minimization** to external APIs: send IDs and aggregates, not raw phone/GST/PAN unless the task requires the field (doc 01 §5, DPDP).
6. **Language**: detect from user input; respond in kind (Hinglish in ↔ Hinglish out). Numerals stay Indian-formatted (₹1,42,300; lakh/crore terms).
7. **No advice liability**: tax/GST explainers describe *what the system did and why* (rules from our own logic), never "tax advice"; disclaim and link to CA guidance for edge cases.
8. **Cost control**: Haiku-tier for G1 routine/G8/G4 drafts; Sonnet-tier for multi-step reasoning; batch API for G5 monthly runs. Budget guardrail: per-user daily token caps via Remote Config.

## Model & Cost Sketch (order-of-magnitude)

| Feature | Model tier | Est. tokens/interaction | At 10k MAU doing 20 interactions/mo |
|---|---|---|---|
| G1/G8 routine Q&A | Haiku-class | ~2–4k in / 300 out | low hundreds of $/mo |
| G2 voice parse | Haiku + STT on-device | ~1k | tens of $/mo |
| G4/G5/G7 drafts & reports | Sonnet-class, batched | ~5–10k | low hundreds of $/mo |
| G6 vision | Sonnet-class vision | ~2–5k/image | scales with scan volume |

Rule of thumb: **genAI runtime cost is a rounding error next to one prevented bad debt or one recovered fuel-theft incident.** The real costs are engineering time and evaluation discipline.

**Next: [04 — Roadmap & Architecture](04-roadmap-and-architecture.md)**
