# Phase 1 — Decisions & data model

**Blocks:** everything.
**Gated on:** (a) explicit approval to edit `models/so_msts.js`, `package.json` and the `.env` files in `dzzlo_oms_api`; (b) one physical measurement of a real DU slip.

---

## 1. The `models/` problem — read this before writing any code

`dzzlo_oms_api/AI.md:83-87` and `docs/strategy/api_v3_refactor_plan.md:18` both say: **"Write ONLY inside `api_v3/` — no edits to `api_v2/`, `api_v1/`, `models/`, or `helpers/`."**

I checked whether there's a legal way around it. There isn't:

- `api_v3/` contains exactly three subdirectories — `controllers/`, `routes/`, `services/`. No `models/`, no `middleware/`.
- `grep -rn "new mongoose.Schema\|new Schema(" api_v3/ api_v/ helpers/` → **zero hits**. Every schema in the process lives in `models/` (22 files) + `models/dip_models/` (4).
- `so_mst_Schema` (`models/so_msts.js:24-45`) has **no `strict:false`, no discriminator, no `Schema.Types.Mixed`**. Mongoose silently drops unknown keys, so both write paths — the `...rest` spread at `api_v3/services/so_msts.js:53` and the `updateSO` whitelist at `:256` — go through strict schema casting.

**Therefore: a field not declared in `models/so_msts.js` cannot be persisted on a Sales Order at all.**

The rule is routinely relaxed with permission, and there's a documented process: `docs/strategy/api_v3_refactor_plan.md:38-47` — files outside `api_v3/` *"must be touched to register the new version. **Require explicit user approval before editing.**"* Recent precedent:

| Commit | Shared file touched |
| --- | --- |
| `9b5a996` feat(voc): AdvDep voucher type | `models/voc_msts.js` (+7) alongside 5 `api_v3/` files |
| `7b6861c` feat(orders): Diesel qty cap | `helpers/dieselQtyLimit.js` (new, +52) |
| `adc4a54` | `models/dealer_custs.js` — `ftank_amt` added |

`docs/strategy/cross_version_edits_plan.md` (status: *Draft — not yet started*) is the standing home for this; its **Phase 4.2** already schedules an edit to `models/so_msts.js`. Register this change there.

**The change is additive-only — a new optional array — so risk to `/api/v2` and `/api/v1` is nil.** That's the same shape as the two precedents above.

> ### ACTION REQUIRED
> Confirm approval to edit, in `dzzlo_oms_api`:
> 1. `models/so_msts.js` — the `du_slips` subdoc array + one index
> 2. `package.json` — `@aws-sdk/client-s3`, `@aws-sdk/s3-request-presigner`, `@aws-sdk/cloudfront-signer`
> 3. `.env.example` + `.env.development` + `.env.testing` + `.env.production` — bucket/region/CDN/key-pair vars
>
> **Not** requested: `dzzlo_oms.js`. The presigned-upload design (Phase 2 D2) means image bytes never pass through Express, so `express.json({limit:"1mb"})` at `dzzlo_oms.js:59` stays untouched. This was a design goal, not a coincidence.

---

## 2. D4 — the schema

### 2.1 Shape

```js
// models/so_msts.js — insert beside so_trn_Schema (currently :7-22)

const du_slip_Schema = new mongoose.Schema(
  {
    // ── storage identity ───────────────────────────────────────────
    // Content-addressed base key. Variants are derived, not stored:
    //   `${key}/orig.jpg` | `${key}/view.webp` | `${key}/thumb.webp`
    // NEVER store a URL here — see Phase 4 §3.
    key: { type: String, required: true },
    sha256: { type: String, required: true },
    bytes: { type: Number },
    width: { type: Number },
    height: { type: Number },
    mime: { type: String, default: "image/jpeg" },

    // ── lifecycle ─────────────────────────────────────────────────
    // pending  → presign issued, nothing uploaded yet
    // claimed  → client says it uploaded (NOT trusted)
    // committed→ S3 event confirmed it; bytes/sha256 above are authoritative
    // failed   → magic-byte mismatch, size violation, or sweeper timeout
    state: {
      type: String,
      enum: ["pending", "claimed", "committed", "failed"],
      default: "pending",
      required: true,
    },

    // ── provenance ────────────────────────────────────────────────
    uploaded_by: { type: ObjectId, ref: "users" },
    captured_at: { type: Date },   // device clock at capture
    uploaded_at: { type: Date },   // server clock at commit
    source: { type: String, enum: ["camera", "gallery", "scanner"] },

    // ── soft delete (never hard-delete: GST retention, Phase 5 §4) ──
    deleted_at: { type: Date },
    deleted_by: { type: ObjectId, ref: "users" },
  },
  { _id: true, timestamps: true }
);
```

Then inside `so_mst_Schema`, immediately after `products: [so_trn_Schema]` (`:35`):

```js
    du_slips: [du_slip_Schema],
```

And with the existing indexes (`:47-53`):

```js
so_mst_Schema.index(
  { dealer_id: 1, "du_slips.state": 1 },
  { partialFilterExpression: { "du_slips.0": { $exists: true } } }
);
```

### 2.2 Four design decisions inside that block

**`_id: true`, unlike `so_trn_Schema`.** `so_trn_Schema` sets `{_id: false}` (`:21`) because line items are never individually addressed. Slips are — delete one, mark one's OCR done, share one. Each needs a stable handle.

**`state` on the subdoc, not a separate collection.** The alternative (a `du_slips` collection with `so_id`) buys independent querying but costs a join on every SO read, on a code path that already does five manual `$in` lookups per list page. Slips are strictly owned by one SO, bounded (≤6, §3), and always read with it. Embed.

**No `url` field. Anywhere.** Signed URLs expire — a stored one is a time bomb. The CDN hostname, key-pair ID and TTL are deployment config that *will* change. Store the key; sign on read (~50 µs of ECDSA). Phase 4 §3 argues this fully.

**Soft delete only.** GST s.36 requires invoice-supporting documents for ~7 years (§4.3 below). A hard delete of a slip on an invoiced SO destroys a statutory record. `deleted_at` hides it from the UI; the object stays.

### 2.3 What breaks if you add this field naively

⚠️ **`api_v3/services/invs.js:659-665`** does:

```js
SalesOrder.find({ $or: [{inv_id}, {gst_inv_id}, {cs_reimb_inv_id}] }).lean()
```

— **no `.select()`**. The result is decorated (`:695-732`) and attached as `invoice.salesOrders` (`:732`). So `du_slips` will silently appear in **every invoice-detail API response** and flow into the **puppeteer PDF template data**. Phase 2 §6 fixes this with an explicit exclusion plus a test that pins it.

⚠️ **`helpers/middlewares.js:167-190 legacy_credit_presenter()`** monkey-patches `res.json` and, for clients `<= 1.77`, does `JSON.parse(JSON.stringify(body))` over the **entire** response (`:183`). A fat `du_slips` array on every SO in a paginated list gets double-serialised for those clients. Keep list projections lean (Phase 2 §5).

⚠️ **`api_v3/services/so_msts.js:181-183`** — `editSalesOrder` does a projected read: `.select("_id products remarks on_dt inv_id gst_inv_id")`. It won't see `du_slips`, which is *correct* — but note `:256-265` builds an `updateSO` whitelist that **resets `cs_reimb_amt` to 0 when absent** (`:259`). **Never route slip writes through `editSalesOrder`.** Dedicated endpoints only.

---

## 3. Product rules to confirm

| Rule | Proposed | Rationale |
| --- | --- | --- |
| Max slips per SO | **6** | A DU slip is one delivery. >2 means a multi-nozzle fill or a retake; 6 is generous headroom and bounds the embedded array. Enforce server-side. |
| Slip required? | **No** — optional | Making it mandatory is an invoice-time validation change plus a migration story for existing un-slipped orders. Can be turned on later per-dealer. **Confirm.** |
| Who may attach | `DPrimary` / `DAdmin` | Matches the existing SO edit gate at `src/screens/Dealer/Orders/components/OneOrder.js:209`. |
| Attach window | Until invoiced | Reuse the existing predicate `!!salesOrder.inv_id \|\| !!salesOrder.gst_inv_id` (`OneOrder.js:206`). Same rule the SO edit screen already enforces. |
| Delete window | Until invoiced, `DPrimary`/`DAdmin` only | After invoicing the slip is evidence attached to a GST record. **Confirm.** |
| Post-invoice | View / download / share only | — |

---

## 4. The measurement that gates the capture spec

**Every pixel target in Phase 3 derives from one unmeasured number: the printed cap-height of text on a real DU slip.** The working assumption is ~2.0–2.3 mm, derived from ESC/POS Font A (12×24 dot cell at a 180 dpi head on 58/80 mm thermal roll). If your dealers' dispensers print smaller or larger, every number scales linearly.

> ### ACTION REQUIRED — five minutes, before Phase 3
> Put a ruler on a real DU slip and record:
> 1. **Cap-height** of the digits in the amount/volume line, in mm
> 2. **Printed width** of the receipt (58 mm vs 80 mm roll)
> 3. **Print technology** — thermal or dot-matrix (they fail differently; see Phase 3 §4)
> 4. Photograph 5–10 slips from different dealers/DU makes — dispenser manufacturer is likely the **largest single source of layout variance**, and this doubles as the seed of the Phase 6 eval set.

**Why it matters, worked:** OCR practice needs ~300 dpi across the printed width for comfortable margin. At an 80 mm (3.15 in) roll that's `300 × 3.15 ≈ 945 px` across the receipt. If the receipt fills ~80% of the frame, the frame needs `945 ÷ 0.8 ≈ 1,180 px` wide. **Round to 2048 px on the long edge** for headroom against skew and partial fill. If the real cap-height is 1.5 mm rather than 2.3 mm, that 2048 becomes ~3100 and the whole upload budget changes.

**Better rule than a fixed long edge:** target **≥1,000 px across the receipt's printed width**. Receipts are tall and narrow, so sizing by the long edge under-resolves long ones. If the detected bounding box exceeds ~1:3 aspect, escalate the archival variant to 2560 px.

### 4.1 The floors the vendors publish

| Vendor | Documented minimum |
| --- | --- |
| AWS Textract | **15 px** text height — *"At 150 DPI, this would be the same as 8 point font."* Recommends ≥150 DPI. Max 10,000 px/side. |
| Azure Document Intelligence | **12 px** text height on a 1024×768 image (~8 pt @ 150 DPI). Dimensions 50×50 → 10,000×10,000. |
| Google Cloud Vision | Recommends **1024×768** for `DOCUMENT_TEXT_DETECTION` — *"OCR requires more resolution to detect characters."* |
| Tesseract | *"works best on images which have a DPI of at least 300 dpi."* |

Design to Tesseract's 300 dpi, not Textract's 15 px floor. The floor is where it *starts* working, not where it works well.

### 4.2 Format constraint that is load-bearing

**AWS Textract accepts JPEG, PNG, PDF and TIFF only — not WebP, not AVIF.** Azure adds BMP/HEIF but likewise no WebP.

So the **archival variant must be JPEG**, even though WebP would be ~30% smaller. Use WebP only for the two delivery variants (thumb, view), which are never sent to OCR. This single constraint sets the variant table in Phase 2 §4.

### 4.3 Retention floors

| Source | Floor | Note |
| --- | --- | --- |
| **GST — CGST s.36** | *"seventy-two months from the due date of furnishing of annual return"* | FY 2024-25 annual return due 31 Dec 2025 → retain to **31 Dec 2031**. ≈ **6 yr 9 mo from FY end — plan 7 years.** An open appeal/investigation extends it indefinitely. |
| **DPDP Rule 8(3)** | **1 year minimum** for personal data + traffic data + processing logs | Applies to everyone. Runs *against* deletion — see Phase 5 §4. |
| **CERT-In Direction (iv)** | **180 days** rolling ICT logs | Logs, not images. FAQ Q35 expressly permits offshore storage if producible. |

Electronic retention is expressly permitted (CGST s.35(1) proviso; **Rule 56(15)**). **Rule 56(16)** requires records accessible at every related place of business; **Rule 57** requires restorable backup and production *"in hard copy or in any electronically readable format"* on demand. **There is no server-location requirement anywhere in GST law.**

⚠️ Note the duty under s.35/36 is on the **registered person — your dealer customer, not you.** Your exposure is contractual: SLA, retention warranty, export-on-demand. Build the export path.

---

## 5. Definition of done

- [ ] Approval recorded for the three protected-file edits (§1)
- [ ] `du_slips` schema merged into `models/so_msts.js`, additive, with the partial index
- [ ] Change registered in `docs/strategy/cross_version_edits_plan.md` Phase 4
- [ ] `docs/AI_CONTEXT.md` updated (this is what `9b5a996` did)
- [ ] Product rules in §3 confirmed by the user, recorded here
- [ ] Physical slip measurement recorded in §4, and Phase 3's pixel targets adjusted if it disagrees with the 2.0–2.3 mm assumption
- [ ] 5–10 sample slip photos captured and filed as the Phase 6 eval seed
- [ ] A failing test exists asserting `du_slips` is absent from the invoice-detail payload (Phase 2 §6 makes it pass)
