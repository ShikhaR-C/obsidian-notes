# Phase 6 — OCR: auto-fill & cross-check

**Blocked by:** Phase 4. **Ships as a separate release from the photo feature** — see Phase 5 §3f (Apple 5.1.2(ii) requires re-consent when data collected for one purpose is repurposed).

**This phase is genuinely optional.** The feature is complete and useful without it. Everything below assumes you've decided it's worth doing.

---

## 1. The finding that reframes the whole decision

**A mid-tier vision LLM now does structured field extraction for less than raw OCR costs, and 10–15× less than the purpose-built receipt APIs.**

Cost per 1,000 DU slips, *including* field extraction (arithmetic in §3):

| Approach | $/1,000 | Structured fields? |
| --- | --- | --- |
| Gemini 2.5 Flash-Lite (VLM) | **~$0.27** | Yes |
| Gemini 3.1 Flash-Lite (VLM) | **~$0.66** ($0.72 asia-south1) | Yes |
| gpt-5-mini (VLM) | ~$1.05 | Yes |
| Cloud Vision `DOCUMENT_TEXT_DETECTION` | $1.50 | **No — raw text** |
| Azure DI Read / Textract `DetectDocumentText` | $1.50 | **No — raw text** |
| Claude Haiku 4.5 (VLM) | ~$3.32 (batch $1.66) | Yes |
| Mistral OCR 4 | $4.00 | Partially |
| Claude Sonnet 5 (intro) | ~$7.10 (batch $3.55) | Yes |
| **Textract `AnalyzeExpense`** | **$10.00** | Yes — *retail* schema |
| **Azure DI `prebuilt-receipt`** | **$10.00** | Yes — retail schema + `receipt.gas` |
| Claude Opus 5 | ~$17.75 | Yes |
| Azure DI Custom / Google Custom Extractor | $30.00 + hosting | Yes |
| Google Doc AI Expense parser | ~$100.00 ⚠️ | Yes |

**In 2026 "OCR → regex" is not the cheap option; it is the expensive *and* less accurate one.** Everything below follows from that.

### 1.1 The accuracy evidence, which points the same way

arXiv 2509.04469 — 8 models, 1,850 documents:

| Dataset | Native image → LLM | OCR text → LLM |
| --- | --- | --- |
| **ICDAR-2019 SROIE (scanned receipts, n=1,000)** | **87.46%** | **47.00%** |
| Scanned invoices (n=350) | 92.71% | 64.03% |
| Clean synthetic invoices (n=500) | 96.50% | 85.14% |

On receipts, converting to text first **destroys nearly half the accuracy** — and the gap is *largest on the low-quality documents*, which is exactly your case. Once layout is gone, the parser cannot tell which number is litres and which is rate.

**One documented failure mode to design around:** unstructured alphanumeric identifiers degrade far worse than typed fields, with characteristic **0↔O** and **1↔I** confusion. For DU slips that hits **vehicle registration numbers** hardest (`MH01AB1234`). Treat vehicle number as the least trustworthy field on the slip.

### 1.2 Why the receipt APIs lose despite being purpose-built

Both model a **retail** document. Azure `prebuilt-receipt` returns `MerchantName, TransactionDate, Total, Subtotal, TotalTax, Tip, Items[{Description, Quantity, Price, TotalPrice}]`. Textract `AnalyzeExpense` normalises `ITEM/QUANTITY/PRICE` and dumps anything untypable into a generic `EXPENSE_ROW` string.

A DU slip is not a retail receipt: one product, a rate per litre, a nozzle/DU number, sometimes a preset mode and attendant ID, and no tax line. You'd be mapping `QUANTITY→litres`, `PRICE→rate`, `TotalPrice→amount` and hoping line-item segmentation holds on a narrow dot-matrix strip the model never saw in training. **There is no field at all for nozzle number** — that lands in `EXPENSE_ROW`/`OTHER` and you're back to regex.

Azure does have a `receipt.gas` sub-type — but it reuses the generic thermal-receipt schema. **No `PricePerLitre`, no `FuelGrade`, no `PumpNumber`, no `Odometer`.** It classifies; it doesn't extract fuel fields.

Two further disqualifiers worth knowing:
- 🔴 **Textract trains on your data by default.** The FAQ permits AWS to *"store and use document and image inputs… to improve and develop the quality of Amazon Textract and other Amazon machine-learning technologies"* — **opt-out, not opt-in**. Worse for residency: *"we might store such content in an AWS Region outside of the AWS Region where you are using the service."* **Choosing ap-south-1 does not by itself keep your slips in India.** Opting out requires an AWS Organizations AI services opt-out policy — and it also deletes previously stored copies. **If you touch Textract at all, attach that policy before the first production call.**
- ⚠️ **Textract `AnalyzeExpense` sync default in Mumbai is 1 TPS** (vs 5 in us-east-1). For dealers uploading at shift change that's a real bottleneck needing a quota increase from day one.

### 1.3 Google, briefly

`TEXT_DETECTION` and `DOCUMENT_TEXT_DETECTION` cost the same ($1.50/1k); the former is tuned for sparse scene text, the latter for dense document text and returns the `fullTextAnnotation` hierarchy with confidence populated. **For a DU slip, `DOCUMENT_TEXT_DETECTION`.** Requesting both bills twice.

But: **Cloud Vision cannot be pinned to India** — a single global endpoint, no regional variants. Document AI *can* (`asia-south1`: OCR, Form Parser, Layout Parser, Custom Extractor, CE-with-GenAI in Preview) — but **the Expense/Invoice parser, the one product actually shaped like a receipt, is not available in Mumbai.**

---

## 2. On-device OCR — a gate, not an extractor

> ⚠️ Package versions in this section are **unverified**. Audit each for New-Architecture support and maintenance before committing. The architectural verdict does not depend on them.

**ML Kit Text Recognition v2** — free, on-device, Android + iOS, Latin plus separate Devanagari and CJK script models.
- **Bundle it, don't unbundle it.** The unbundled model downloads via Play Services on first use — and your user's first use is at a forecourt with poor connectivity.
- ⚠️ **It appears not to expose per-element or per-line confidence.** Verify — this is load-bearing. If true, it cannot drive a confidence-gated flow at all.

**Apple Vision `VNRecognizeTextRequest`** (`.accurate`) — genuinely strong, and unlike ML Kit it **does** return `confidence` (0–1) per candidate via `topCandidates(_:)`.
- 🔴 **Set `usesLanguageCorrection = false` for receipts.** Language correction nudges strings toward dictionary words and actively degrades digit accuracy. Single highest-impact setting.

**Tesseract on mobile — skip.** Dot-matrix defeats its segmentation (it can't distinguish gaps *within* dot-formed glyphs from gaps *between* glyphs), thermal contrast defeats binarisation, RN bindings are unmaintained, and `tesseract.js` under Hermes is impractical.

> ### RECOMMENDATION
> **On-device OCR is a capture-quality gate, never an extractor.** At capture, offline: is there text at all? at least two lines containing digits? in focus? sane exposure? slip inside the frame? → if not, *"Slip unreadable — move into shade and retake"* **before the photo leaves the phone**.
>
> This is the highest-ROI use of on-device OCR: it kills the round trip on garbage captures, works with zero connectivity, costs nothing, and fixes the root cause while the user is still standing at the pump.
>
> **Do not parse values on-device, and do not display any on-device-derived number.** A wrong number shown once anchors the user even after the cloud corrects it. Cloud is not a "fallback" — it is the extractor.

Pair it with the Laplacian-variance blur check and glare check from Phase 3 §4.4, which are cheaper and more predictive than OCR for retake decisions.

---

## 3. The extractor: vision LLM under a strict JSON schema

### 3.1 Cost arithmetic for a ~1000×1400 px slip

**Claude** — visual tokens `= ⌈w/28⌉ × ⌈h/28⌉`:

```
⌈1000/28⌉ = 36 ;  ⌈1400/28⌉ = 50  →  36 × 50 = 1,800 visual tokens
```
High-resolution tier (Claude 4.7+, incl. Opus 5 / Sonnet 5) allows 2,576 px long edge / 4,784 visual tokens → **no downscale, exactly 1,800**. Standard tier (Haiku 4.5) caps at 1,568 → downscaled to ≈1,568.

Budget: image tokens + ~500 prompt/schema in, ~250 JSON out.

| Model | Rate (in/out per MTok) | $/1,000 |
| --- | --- | --- |
| Haiku 4.5 | $1 / $5 | **$3.32** (batch $1.66) |
| Sonnet 5 *(intro, to 2026-08-31)* | $2 / $10 | **$7.10** (batch $3.55) |
| Sonnet 5 *(from 2026-09-01)* | $3 / $15 | $10.65 |
| Opus 5 | $5 / $25 | $17.75 |

`inference_geo: "us"` multiplies by 1.1.

**Gemini** — 2.5-series tiles at 768 px, 258 tokens/tile; crop unit `floor(min(w,h)/1.5)`:
```
crop unit = floor(1000/1.5) = 666
tiles     = ⌈1000/666⌉ × ⌈1400/666⌉ = 2 × 3 = 6
tokens    = 6 × 258 = 1,548
```
Gemini 3 uses fixed tokens per image via `media_resolution` (default ≈1,120) ⚠️ medium confidence.

| Model | Rate | $/1,000 |
| --- | --- | --- |
| Gemini 2.5 Flash-Lite | $0.10 / $0.40 | **$0.27** |
| Gemini 3.1 Flash-Lite | $0.25 / $1.50 | **$0.66** ($0.72 asia-south1, +10% regional premium) |
| Gemini 3.5 Flash-Lite | $0.30 / $2.50 | $0.93 |
| Gemini 3.6 Flash | $1.50 / $7.50 | $3.63 |

**OpenAI** — `⌈w/32⌉ × ⌈h/32⌉` patches; GPT-5.6 with `auto`/omitted `detail` preserves input dimensions:
```
⌈1000/32⌉ × ⌈1400/32⌉ = 32 × 44 = 1,408 patches
```
gpt-5-mini ≈ **$1.05**; GPT-5.6 Luna ≈ $2.91; Terra ≈ $7.27. ⚠️ Full-size patch multipliers aren't published; 1.0 assumed.

**Downsample lever:** 800×1120 → 1,160 Claude tokens (−36%), Sonnet 5 intro → ~$5.82/1k. **Measure legibility before doing this** — heavy compression makes small print unreadable, and the vendor docs warn about exactly this.

### 3.2 Schema design — two decisions that matter more than the model

**1. Emit every numeric as a string *and* a parsed number.**

```jsonc
"volume_litres": {
  "as_printed": "18.52",   // the literal characters on the slip
  "value": 18.52,          // the model's parse
  "legible": true
}
```

A bare JSON `number` destroys the printed representation — you can't distinguish `18.5` from `18.50`, can't tell whether the model *read* it or *normalised* it, and can't diff its parse against your own. With both, `parse(as_printed) === value` is a free consistency check and any mismatch is a strong hallucination signal. Constrained decoding can't enforce decimal places on a `number` anyway.

**2. Give the model an explicit way to abstain.** Every field gets `null` plus `legible: false`. **Hallucination on numbers is overwhelmingly a forced-choice artifact** — a model with no escape hatch invents a plausible digit. This is the cheapest single mitigation available.

Also require a **verbatim substring** per field (what the slip literally shows). If the model can't quote it, it's guessing. This is the cheap version of the evidence-grounding design that achieved 0.928 AUC with 70% lower AURC than logprob-mean on DocILE.

### 3.3 Constrained decoding — the caveats

Claude's `output_config.format` with `json_schema` uses **grammar-constrained decoding**: output is guaranteed valid JSON matching the schema, with no retry loop, even under `max_tokens` truncation. But:

- ❌ **Not supported:** `minimum`/`maximum`, `multipleOf`, `pattern`, `minLength`/`maxLength`, `maxItems`, recursive schemas. **You cannot enforce "amount ≥ 0" or a date regex at the decoder.** Validate client-side.
- Nullable needs `anyOf: [{"type":"string"},{"type":"null"}]`, not `"type": ["string","null"]`.
- First request with a new schema pays grammar compilation (~500 ms+); cached 24 h from last use. Changing the schema invalidates the prompt cache.
- 🔴 **DPDP-relevant:** the schema is cached **separately from message content** and does not receive the same data protections. **Never put dealer names, GSTINs, or vehicle numbers into schema property names, enums, consts, or descriptions.**

### 3.4 Confidence — what does and doesn't work

**Logprobs are a dead end.** Anthropic exposes none. OpenAI hides them when reasoning is on. And where available they **saturate above 0.999 under constrained JSON decoding** (arXiv 2606.24420) — constrained decoding makes every token look certain. Do not build on them.

**Self-reported confidence is badly calibrated.** Models report 74–97% while true risk ranges 3–80%; expected calibration error ranges 0.05 to 0.61 by task. Usable as one weak feature in a blend; never as a probability.

**Self-consistency has a constraint you must know about:** `temperature`, `top_p` and `top_k` are **rejected with a 400** on Opus 5, Sonnet 5 and Opus 4.8/4.7. You cannot get sampling variance by raising temperature. Perturb the *input* instead (different crop, different downsample, ±2° rotation) or use a different model.

**What actually works, best value first:**

| Signal | Cost | Strength |
| --- | --- | --- |
| Arithmetic identity `litres × rate ≈ amount` | **free** | Very high |
| Rate-table cross-check | **free** | Very high |
| Verbatim substring + `as_printed`/`value` agreement | ~free | Medium |
| Range / enum / date sanity | free | Medium |
| **Cross-family** verifier second pass | ~$0.30–1/1,000 | High |
| Self-reported confidence | ~free | Low |

Then **fit a small logistic regression** on `[arith_pass, rate_match, evidence_consistent, verifier_agree, self_reported] → P(correct)` using your labelled set. ~165 in-domain samples sufficed in the published work; use 300+. This gives you a *calibrated* number to threshold on, which no provider will hand you.

**Cross-family beats same-family** for the verifier — correlated errors within a model family defeat the point.

---

## 4. The pipeline

```
┌─ ON DEVICE, at capture (0–300 ms, offline) ──────────────────┐
│ 1. Camera with a slip-shaped guide overlay                   │
│ 2. Blur (Laplacian variance) + glare (clipped-pixel ratio)   │
│ 3. On-device OCR gate: ≥N lines? ≥2 lines with digits?       │
│    └─ fail → "Retake"  (never leaves the phone)              │
│ 4. Downscale, JPEG q82 grayscale, strip EXIF GPS             │
│ 5. Upload → returns extractionId                             │
└──────────────────────────────────────────────────────────────┘
┌─ SERVER, on upload (sync, hard 8 s budget) ──────────────────┐
│ 6. Vision LLM, strict JSON schema                            │
│ 7. Deterministic checks — ALL FREE:                          │
│      • litres × rate ≈ amount,  tol = max(₹1.00, 0.01×rate)  │
│      • rate == dealer's rate table for product+date ±₹0.50   │
│      • date ∈ [SO date − 7d, SO date + 1d]                   │
│      • product ∈ dealer's product enum                       │
│      • nozzle ∈ dealer's registered DU list                  │
│      • volume plausible for the vehicle on the SO            │
│      • duplicate: (DU, datetime, amount) + image pHash       │
│ 8. Composite confidence = calibrated f(checks, verifier, …)  │
│ 9. Append-only extraction record; return suggestions         │
└──────────────────────────────────────────────────────────────┘
┌─ ASYNC WORKER ───────────────────────────────────────────────┐
│ Timeout fallback · retries · verifier pass on high-value     │
│ orders · reprocessing after model/prompt change · nightly    │
│ eval-set regression run                                      │
└──────────────────────────────────────────────────────────────┘
```

**Sync with async fallback, 8-second hard budget.** The dealer is standing at the pump. Past 8 s, hand them the manual form immediately and queue the extraction — when it lands, surface it as a *cross-check* on what they typed, never as a correction. **Never make a human wait on OCR.** Offline captures queue locally with the typed SO and surface as a review item on reconnect.

### 4.1 🔴 Presentation: suggest — not pre-fill, not flag-only

Three candidate designs. Two are wrong.

**Reject pre-fill.** Pre-fill makes the OCR value the default, and defaults get accepted. That's automation bias, and in a financial system it turns a model error into a ledger entry with no human judgment anywhere. Worse, it destroys the audit story: tapping *Save* on a pre-filled form is **indistinguishable in your data** from tapping *Save* while ignoring the number. You cannot later demonstrate a human ever looked. Pre-fill is right for low-stakes convenience; it is wrong for anything that becomes money.

**Adopt suggest as primary.** The field stays empty. The OCR value appears as a tappable chip beside it — *"Slip reads 18.52 L — tap to use"*. One tap accepts, and **that tap is an explicit, timestamped, attributable act you log**. Cost: one extra tap per field. In practice it's no slower — reading and approving a pre-filled value takes the same attention as reading and tapping a chip — and the legal posture is far better.

**Use flag-mismatch on the cross-check path.** When the user already typed values and photographs the slip to verify: show a diff — *"Slip says 18.52 L, you entered 18.25 L"* → **Keep mine / Use slip / Retake**. **Never overwrite.** Overwriting typed input is the worst available behaviour: it destroys the one input you know a human authored.

**At low confidence, show nothing.** Don't show a wrong suggestion with a warning icon — users accept those. Show *no* suggestion plus a neutral line: *"Couldn't read the quantity clearly — please enter it."* An absent suggestion produces a correct manual entry; a low-confidence suggestion produces an accepted wrong one. Show the cropped image region beside the field so the user can read it themselves without hunting.

An "accept all" is permissible **only** if every value is displayed and every check passed — and it must log each field individually.

### 4.2 The arithmetic check, and why the tolerance is what it is

`|volume × rate − amount| ≤ tolerance`

Volume prints to 2 dp (sometimes 3), so true volume differs by up to ±0.005 L → an amount discrepancy of `0.005 × 105 ≈ ₹0.53`. **This does not scale with order size** — a 5,000 L tanker load has the same ±₹0.5 rounding band as a 20 L fill. So:

```
tolerance = max(₹1.00, 0.01 × rate)
```

**Why it's so powerful:** for a digit error to survive, the error must be almost exactly compensated. Misreading `18.52 → 19.52 L` produces a delta of `1.00 × 104.77 = ₹104.77` — ~100× the tolerance. Only errors in the second decimal of the amount slip through. It catches essentially every financially material error and misses only trailing-paisa noise. Exactly the right failure profile.

⚠️ Indian pumps commonly run in **preset-amount mode** (customer asks for ₹500 worth), where amount is exact and volume is the derived, rounded value. Don't use tight equality — you'll flag correct slips. Tune the tolerance on the eval set.

### 4.3 🔴 The rate-table cross-check is your unfair advantage

**DZZLO already knows the dealer's rate for that product on that date.** So rate isn't really an OCR problem: look it up, and use OCR only to *confirm* it (flag if `|ocr_rate − known_rate| > ₹0.50`). If the known rate is trusted, you can derive `volume = amount / rate` and cross-check against the OCR volume — **collapsing a three-unknown problem into one.**

Most teams building this feature don't have that ground truth. You do. **Build the deterministic checks before you tune the model** — they cost nothing and outperform every model-derived signal.

### 4.4 Audit storage

Two **append-only** collections. The SO stores only human-authored final values plus an `extractionId` reference.

```js
// ocr_extractions — append-only. Reprocessing writes a NEW row.
{
  _id, so_id,                            // nullable — extraction may precede the SO
  image: { storageKey, sha256, bytes, width, height,
           capturedAt, deviceModel, appVersion },
  provider, modelId,                     // the exact string sent, e.g. "gemini-3.1-flash-lite"
  modelSnapshotSeenAt,                   // aliases move — record when
  promptVersion, schemaVersion, requestId,
  rawResponse,                           // VERBATIM, unparsed
  normalized: { volume, volumeAsPrinted, rate, rateAsPrinted,
                amount, amountAsPrinted, datetime, product, nozzle },
  fieldStatus: { volume: "read", nozzle: "illegible", … },
  checks: { arithmetic: { passed, deltaInr, toleranceInr },
            rateTable:  { passed, knownRate, ocrRate },
            dateRange, productEnum, duRegistry, duplicate },
  confidence: { perField, composite, calibrationVersion },
  latencyMs, costMicros, createdAt
}

// ocr_field_decisions — one row per field, per human action
{ _id, extraction_id, so_id, field,
  ocrValue, finalValue,
  action,                                // accepted | edited | rejected | ignored | no_suggestion
  actorUserId, actorRole, actorDeviceId, at }
```

**Never mutate either.** Corrections are new rows. Storing `modelId` + `promptVersion` + `schemaVersion` is what lets you answer, six months and two model upgrades later, *"why did the system propose 18.52?"* Without it, an audit question is unanswerable — and you cannot bound the blast radius of a silent provider-side regression.

⚠️ Note this is a **new top-level collection**, so it lands in `models/` — same approval gate as Phase 1 §1.

---

## 5. Accuracy expectations & evaluation

### 5.1 What's realistic

| Condition | Per-field exact match |
| --- | --- |
| Fresh thermal, good light, flat, in focus | 92–97% |
| **Blended production mix** | **85–93%** |
| Faded thermal / dot-matrix / glare / crumpled | 60–85% |

**The number teams forget: all-fields-correct ≈ 60–75%**, because `0.92⁵ ≈ 0.66`. Per-field accuracy is not slip-level accuracy. **Report all-fields-correct, not per-field, in anything said to a dealer.**

Anchor: the best native-image model on SROIE scanned receipts reached **87.46%** — and SROIE is *cleaner* than a forecourt photo. Reject any vendor or internal claim of 99% on this document type; nobody has an independent benchmark for it.

Separately, the KORIE receipt benchmark (17,587 real receipt crops) measured CER of PaddleOCR 15.84%, EasyOCR 17.36%, Tesseract 25.43%, and attributes it to *"thermal paper yields low-contrast strokes, significant ink fading, and printer head banding"* — degradation that **persists even at 300 dpi flatbed scan**. **Field-level human validation is permanent, not a v1 crutch.**

After the deterministic checks the framing changes usefully: **you are no longer trying to be right, you are trying to know when you're right.** Target: of the slips where all checks pass and a suggestion is shown, **≥99% correct**; route the rest to manual. Coverage will start ~55–70% and climb as capture quality improves.

### 5.2 Metrics, in priority order

1. **Silent-error rate** = wrong ∧ checks passed ∧ high confidence. The only metric that maps to "corrupted a financial record." **Make it the release gate: ≪1%.**
2. **Human-override rate**, per field, per week, in production. The real metric — needs no labels, is free, and a step change is your fastest signal of a silent model regression.
3. Per-field exact match (after normalising ₹, separators, dates).
4. Per-field tolerance match (|Δ| ≤ 0.01), reported **separately**, so rounding doesn't masquerade as OCR error.
5. All-fields-correct — the honest headline.
6. Coverage / abstention rate — the business metric.
7. CER on the raw text layer — **diagnostic only, never a KPI.** It doesn't tell you whether the *litres* were right.

### 5.3 Building the set

Sample **real production captures**, not curated ones. Stratify on what actually varies: print tech (thermal / dot-matrix), condition (fresh / faded), lighting (shade / direct sun / night forecourt), angle and crop, product, dealer, and **DU make/model** — dispenser manufacturer is likely your largest single source of layout variance.

**Two independent labellers, adjudicate disagreements.** The inter-labeller disagreement rate is your accuracy ceiling: if humans disagree on 3% of litre readings, no model beats 97% and you should stop optimising. Freeze the set; hold out a second you never tune against.

### 5.4 Sample size

`n ≈ z²p(1−p)/w²`, z = 1.96:

| Target | ±5 pp | ±3 pp | ±2 pp |
| --- | --- | --- | --- |
| p ≈ 0.95 | 73 | **203** | 456 |
| p ≈ 0.90 | 138 | **384** | 864 |

- **300 slips minimum** for a headline number you'd act on
- **500+** to compare two providers and detect a 3–5 pp difference
- **≥50 per stratum** before saying anything about a stratum
- **Rule of three:** 0 failures in *n* → 95% upper bound ≈ 3/n. **0/300 still permits a 1% true error rate.** Never claim "100% accurate" from a clean eval run.

Re-run the frozen eval on **every** model, prompt or schema change — vision-model upgrades are not monotonic improvements on a narrow domain like this. And record `modelId` on every production row so you can detect drift you didn't cause.

---

## 6. DPDP and cross-border, for OCR specifically

Building on Phase 5 §4: the operational obligations bite ~May 2027; s.16 is a negative list with **zero countries notified**; CERT-In permits offshore log storage.

**You have runway, not immunity.** Retrofitting consent, notice and audit plumbing into a *live financial workflow* is far more expensive than building it now, when the incremental cost is close to zero.

**Is a slip personal data?** Mostly no — litres, rate, amount, nozzle are transaction data about a business. Two things drag it in: an incidental **vehicle registration number** (linkable to an identifiable individual for private vehicles) and an **attendant/FCC ID**. Treat the images as *may contain* personal data.

> 🔴 **The cheapest mitigation available: if you don't need the vehicle number, don't extract it.** Omit it from the schema entirely; consider on-device redaction before upload. This materially shrinks the compliance surface for a field that (a) the product may not need and (b) is the least accurate on the slip anyway (§1.1).

### 6.1 In-India processing and training commitments

| Provider | In-India processing? | Trains on your data? |
| --- | --- | --- |
| **AWS Textract** | Yes — `ap-south-1` only (**not** ap-south-2); 1 TPS AnalyzeExpense default | 🔴 **Yes by default.** Must attach an AWS Organizations AI opt-out policy — and note AWS may store content *outside* your region for this purpose |
| **Azure AI Document Intelligence** | Yes — Central India; async-only; same-region processing, 24 h retention, delete API | No ⚠️ (stated by a Microsoft employee on Q&A, **not** in a citable formal policy doc) |
| **Google Document AI** | Yes — `asia-south1`. **Expense/Invoice parser NOT available there** | No (enterprise Cloud terms) |
| **Google Cloud Vision** | ❌ single global endpoint | No |
| **Gemini via Vertex AI** | Partially — `asia-south1` regional endpoint, +10% premium ⚠️ verify per model | Paid tier no. 🔴 **Free / AI Studio tier: yes** |
| **Anthropic Claude first-party API** | ❌ `inference_geo` accepts only `"us"` and `"global"` | **No** — *"retained data is never used for model training without your express permission"*; content not retained by default; **zero data retention available on request** |
| **Claude via Vertex AI / Bedrock** | ✅ inherits the cloud region (`asia-south1` / `ap-south-1`) | The cloud provider is the data processor there |
| **OpenAI** | ⚠️ unverified | API data not used for training by default |
| **Mistral** | ⚠️ EU-centric; no India region found | ⚠️ unverified |

> ### RECOMMENDATION — §6
> **The structural fork, worth deciding before writing code:** if you want *both* a frontier vision LLM *and* India-resident processing, the path is **Gemini or Claude via Vertex AI (`asia-south1`) or Bedrock (`ap-south-1`)** — **not** the first-party Anthropic API, which has no India geo at any price.
>
> Do all of these now, all cheap: (a) drop vehicle number from the schema unless the product needs it; (b) **put the provider behind an interface on day one** — that single decision is your entire hedge against an s.16 notification landing in 2027, and turns a rewrite into a config change; (c) itemised notice + dealer-level consent + per-user toggle; (d) if you touch Textract at all, attach the AWS AI opt-out policy first; (e) **never point production at Gemini's free tier.**
>
> Also: sign the provider's standard DPA and add purpose limitation, no-training, deletion-on-termination, sub-processor notice, and breach notification to you within a fixed window (DPDP Rule 6(f) requires the flow-down; s.8(2) requires a "valid contract" but, unlike GDPR Art. 28, doesn't prescribe clause content).
>
> **Build the extraction log (§4.4) so you can enumerate exactly which images went where, when.** That query is the difference between a controlled breach disclosure and a guess.

> ### RECOMMENDATION — §3 (extractor choice)
> **Start on Gemini 3.1 Flash-Lite (~$0.66/1k) via Vertex AI `asia-south1` as the primary extractor**, with **Claude Haiku 4.5 (~$3.32/1k) as the cross-family verifier** on high-value orders — or invert if your eval says so.
>
> **Reserve Sonnet 5 / Opus 5 for a measured accuracy gap, not by default.** At ~$7–18/1k they must earn it against a $0.66 baseline.
>
> At even 50,000 slips/month the primary path is **~$33/month**. **Cost is not the constraint here; silent-error rate is.** Optimise for that, then take the cheapest model clearing the bar.

---

## 7. Product guardrails

### 7.1 The bright line

**OCR may never cause a financial value to be persisted without an explicit, attributable human act.** Not "with a warning." Not "if confidence is high." Never.

**ALWAYS requires human confirmation:**
- quantity / litres
- rate per litre
- total amount
- transaction date & time
- product
- **vehicle registration number** — the documented 0↔O / 1↔I failure mode makes it the least trustworthy field on the slip
- anything that posts to a ledger, adjusts stock, triggers an invoice, or moves a balance

**MAY be auto-populated** (non-financial conveniences only):
- attaching the image to the SO
- the capture timestamp (device clock, **not** the slip's)
- the extraction record itself
- pre-selecting the DU **only if** the read matches exactly one registered DU — and even then as a *highlighted* selection, not a silent one

**NEVER, at any confidence:**
- auto-approve or auto-post an SO from OCR
- auto-generate an invoice
- auto-adjust stock
- an "Accept all" that commits financial fields without displaying each value
- silently correct a value the user typed
- describe OCR output as "verified" or "confirmed" in UI copy — the correct phrasing is **"read from slip"**

### 7.2 Make it a server invariant, not a UI convention

> **The SO write endpoint must reject any financial field whose value did not arrive with a matching `ocr_field_decisions` row** (`action: accepted | edited`).
>
> A UI rule gets bypassed by the next refactor, a bulk-import path, or an API client. A server invariant does not.

### 7.3 Framing and telemetry

Call it **"Scan to fill"**, never "auto-entry". Show once in onboarding: *"Scanning helps you enter faster. You're responsible for the values you save — always check them against the slip."* Keep the source image one tap away from every field it informed.

**One metric on the ops dashboard: % of financial fields saved with `action: "accepted"` and near-zero dwell time.** If that climbs, users are rubber-stamping and your control has quietly stopped working — regardless of what the accuracy numbers say.

**Free and worth shipping:** a per-dealer monthly "Scan assist" report — suggestions shown / accepted / edited / overridden. Gives the dealer transparency and gives you override-rate monitoring (§5.2) at no extra cost.

⚠️ **Flag for counsel:** Indian companies keeping books in electronic form face audit-trail/edit-log requirements (Companies Act s.128 + Rule 3, audit trail mandatory for FYs from 1 Apr 2023). Confirm whether the extraction and decision records fall inside that perimeter — if they do, "append-only" becomes a **legal requirement**, not an engineering preference.

---

## 8. Open items before committing

1. **On-device RN package audit** — `@react-native-ml-kit/text-recognition`, VisionCamera text plugins, `@infinitered/react-native-mlkit-*`: New-Architecture support, last publish, maintenance. The "gate only" verdict doesn't depend on it, but the implementation does.
2. **Whether ML Kit Text Recognition v2 exposes per-element confidence.** Load-bearing for §2.
3. **Vertex AI `asia-south1` Gemini model list and pricing** — the +10% regional premium and per-model availability were not confirmed.
4. **Gemini 3 image-token constant (≈1,120)** — medium confidence; the 2.5-series tiling rule is verified.
5. **GPT-5.6 full-size patch multiplier** — assumed 1.0; only mini/nano multipliers are published.
6. **OpenAI India data residency** and **Mistral DPA/residency terms** — unverified.
7. **Statutory retention perimeter** for the extraction records (§7.3) — auditor/counsel.
8. **Latency** — no provider publishes p50/p99 for these APIs. 2–4 s is a planning assumption. **Measure it yourself from Mumbai on day one**, because the 8-second budget in §4 depends on it.
