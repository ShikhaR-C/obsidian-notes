# DU Slip Images on Sales Orders — capture, store, share, and OCR

**Status:** Spec'd (2026-07-29). **Not started — no repo code changes until explicit go-ahead.**
**Owner:** TBD
**Created:** 2026-07-29
**Scope:** Let a dealer user attach 1..N photographs of the **DU slip** (the delivery invoice printed by a petrol pump's dispensing unit) to a Sales Order (`so_msts`) — during creation or after creation but **before invoicing**. Store them in object storage, link them to the SO, view/download/share them from app and web, expose an optional public share link, and later **OCR** them to pre-fill or cross-check the SO.

Touches all three repos (`dzzlo_oms_api`, `dzzlo_oms_app`, `dip-web`), adds cloud infrastructure that does not exist today (object storage, CDN, a post-upload worker), and adds two store-compliance surfaces (media permissions, third-party AI disclosure) that the apps have never had to satisfy.

---

## 1. Why this is bigger than "add an image field"

Three things make this a multi-phase project rather than a feature ticket:

1. **There is no file-handling infrastructure anywhere in the stack.** Exhaustive grep across `dzzlo_oms_api` for `multer|busboy|formidable|multipart|@aws-sdk/client-s3|presign` returns **zero hits**. The only AWS package is `@aws-sdk/client-sesv2`. `dip-web` has no `FormData`, no `<input type="file">`, no download code. The app has three files referencing `react-native-image-picker` / `react-native-permissions` / `rn-fetch-blob` — **all three libraries are absent from `package.json` and `node_modules`, so those files are dead code**. Everything here is new plumbing.
2. **The Sales Order write path has no per-user authorization.** `api_v3/auth.js:61 protect`, `:78 authorize`, `:93 scope` all exist and are correct, but across the whole of `api_v3/routes/` they are **imported and never applied** — every usage is commented out. `api_v3/services/so_msts.js` never reads the token; `dealer_id`/`cust_id` come straight from the client-supplied body (`:299-301`, `:490-491`, `:680-681`). See §6 — this is a **pre-existing** hole this feature must not widen.
3. **Media capture is the most policy-constrained thing a mobile app can do**, and both stores tightened the rules in the last twelve months specifically around _photos_ and _third-party AI_. Getting the design right (system pickers, not permissions) is the difference between zero permission dialogs and a Play Console declaration that takes "several weeks" to review.

## 2. The headline decisions

Each is argued in the phase doc named in the last column. Where a decision is genuinely close, the runner-up and the trigger to switch are recorded there — not lost.

| #   | Decision              | Choice                                                                                                                           | Phase |
| --- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----- |
| D1  | Where the images live | **AWS S3 `ap-south-1` + CloudFront.** Runner-up Cloudflare R2                                                                    | 2     |
| D2  | Upload mechanism      | **Presigned POST policy**, client → S3 direct. Not proxy, not presigned PUT                                                      | 2     |
| D3  | Image optimisation    | **Build it** — 3 fixed variants in the post-upload Lambda. Not ImageKit, not Cloudinary                                          | 2     |
| D4  | Schema shape          | `du_slips: [du_slip_Schema]` on `models/so_msts.js`, subdoc keeps its `_id`                                                      | 1     |
| D5  | Capture UX            | **System document scanner** (ML Kit / VisionKit) primary, `react-native-image-picker` fallback. **Do not write a native module** | 3     |
| D6  | Android permissions   | **Zero.** Photo Picker for gallery + `ACTION_IMAGE_CAPTURE` for camera, `CAMERA` deliberately absent from the manifest           | 3, 5  |
| D7  | Upload transport      | `XMLHttpRequest` with a `{uri}` body — **not** `fetch`, **not** a `Blob`                                                         | 3     |
| D8  | Retrieval             | Store **keys** in Mongo, sign on read. CloudFront signed URLs, 15-min TTL, batch-issued                                          | 4     |
| D9  | Share link            | Opaque ≥128-bit token, TTL + revoke, `X-Robots-Tag: noindex` on page _and_ images                                                | 4     |
| D10 | OCR posture           | **Never auto-writes a financial value.** Suggest + cross-check only, always human-confirmed                                      | 6     |

## 3. The two decisions that matter most (and why they're not the obvious ones)

**Serving the right _variant_ is worth ~200× more than picking the right cloud.** At 300k images/month, thumbnail-first list views cost **$0/month** in CloudFront egress (inside the always-free 1 TB tier); naively serving full-res on the same screens costs **$412/month**. The storage-vendor choice between S3 and R2 is worth ~$21/month at the same volume. Get the read path right (Phase 4) and the vendor question barely matters.

**Glare, not resolution, is the OCR bottleneck.** Measured on real photographs, specular-highlight removal moved end-to-end text recall from **64.85% → 78.50%** (+13.65 points). No server-side processing recovers clipped pixels. Meanwhile, the KORIE receipt benchmark (17,587 real receipt crops) measured character error rates of **15.8%–25.4%** that _persist even at 300 dpi flatbed scan_, because the damage is in the thermal paper, not the digitisation. So: a **capture-time glare/blur gate that rejects the frame and re-prompts** is the highest-leverage thing to build, and **field-level human validation of OCR output is permanent, not a v1 crutch.**

## 4. Blast radius — file inventory

### `dzzlo_oms_api`

| File                                                     | Anchor                                   | Change                                                                                                                | Phase |
| -------------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | ----- |
| `models/so_msts.js`                                      | after `products` `:35`; indexes `:47-53` | **`du_slips` subdoc array** — ⚠️ outside `api_v3/`, needs explicit approval                                           | 1     |
| `api_v3/services/duSlips/index.js`                       | new                                      | issue presign, commit, list, delete, share-token                                                                      | 2     |
| `api_v3/services/storage/s3.js`                          | new                                      | S3 adapter (presign POST, sign CloudFront, delete)                                                                    | 2     |
| `api_v3/services/so_msts.js`                             | new exports after `:826`                 | attach/list/remove; **do not route through `editSalesOrder`** (`:259` zeroes `cs_reimb_amt`, `:185` blocks invoiced)  | 2     |
| `api_v3/controllers/collections/so_msts.js`              | after `:68`                              | thin `asyncHandler` wrappers                                                                                          | 2     |
| `api_v3/routes/collections/so_msts.js`                   | before `:34`                             | `POST /:id/slips/presign`, `POST /:id/slips/commit`, `GET /:id/slips`, `DELETE /:id/slips/:slipId`                    | 2     |
| `api_v3/routes/open_apis/share.js`                       | new                                      | public `GET /share/:token` — mounted **before** `api_key_v3()`                                                        | 4     |
| `api_v3/services/invs.js`                                | `:659-665`                               | ⚠️ unprojected `SalesOrder.find()` — `du_slips` will silently flow into every invoice payload and PDF unless excluded | 2     |
| `api_v3/services/invoice/htmlPdf/fileBuffer.js`          | `:51`                                    | `waitUntil:"networkidle0"` **fetches remote `<img>`** — private slip URLs will hang the render                        | 4     |
| `package.json`                                           | deps                                     | `@aws-sdk/client-s3`, `@aws-sdk/s3-request-presigner`, `@aws-sdk/cloudfront-signer` — ⚠️ needs approval               | 2     |
| `.env.example` + `.env.{development,testing,production}` | —                                        | bucket/region/CDN/key-pair vars — ⚠️ needs approval                                                                   | 2     |
| `test/api_v3/collections/so_msts/*.test.js`              | new                                      | safe to modify                                                                                                        | 7     |

**Deliberately NOT changed:** `dzzlo_oms.js:59` `express.json({limit:"1mb"})`. Presigned-POST-direct-to-S3 means image bytes never touch Express, so the body limit stays as-is. This is one of the reasons D2 is presigned rather than proxy.

### `dzzlo_oms_app` (currently v1.78 / Android `versionCode 103` / iOS build 9)

| File                                                     | Anchor                                         | Change                                                                                                                                             | Phase |
| -------------------------------------------------------- | ---------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ----- |
| `src/screens/Dealer/NewSalesOrder/index.js`              | UI slot after `:593`; submit `:325-336`        | staged capture; **capture the `_id` that `:325` currently discards**                                                                               | 3     |
| `src/screens/Dealer/EditSalesOrder/index.js`             | UI slot after `:702`; `sorder._id` known       | direct upload — the simpler flow, build this first                                                                                                 | 3     |
| `src/screens/Dealer/Orders/components/OneOrder.js`       | `:206`                                         | reuse `!!inv_id \|\| !!gst_inv_id` as the "before invoicing" gate                                                                                  | 3     |
| `src/store/apis/dzzlooms/du_slips.js`                    | new                                            | RTK Query endpoints                                                                                                                                | 3     |
| `src/store/apis/createApi.js`                            | `:117-127`; new `uploadBaseQuery` beside `:21` | add `so_msts`/`du_slips` tagTypes; **the shared baseQuery is unusable for uploads** — `timeout:10000` at `:47`, `retry` at `:95` re-sends the body | 3     |
| `android/app/src/main/AndroidManifest.xml`               | `:3`                                           | `<queries>`, `FileProvider`, `ModuleDependencies`, `uses-feature` guards — **no new permissions**                                                  | 5     |
| `ios/dzzlo_oms_app/Info.plist`                           | `:49-53`                                       | add `NSCameraUsageDescription`; ⚠️ **fix the 3 existing `NSLocation*` keys**                                                                       | 5     |
| `ios/dzzlo_oms_app/PrivacyInfo.xcprivacy`                | —                                              | add DiskSpace `E174.1`; populate empty `NSPrivacyCollectedDataTypes`                                                                               | 5     |
| `.env.{development,testing,production}` + `.env.example` | —                                              | ⚠️ `babel-plugin-dotenv` runs `safe:true, allowUndefined:false` — a var missing from **any** file fails the bundle                                 | 3     |

### `dip-web` (currently v1.4.7)

`so_msts` has **zero presence** in this repo — no page, no endpoint, no tag type. Everything is new.

| File                                 | Change                                                                                                                  | Phase |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ----- |
| `src/store/apis/dzzlooms/so_msts.js` | new — absolute `/api/v3` URL, per the `voc_msts.js:19-26` pattern                                                       | 4     |
| `src/store/apis/createApi.js:55-72`  | add `so_msts` tag type                                                                                                  | 4     |
| `src/App.js:364-368`                 | public share route **outside** the `isSignedIn` gate; there is currently no `path="*"` fallback for signed-out visitors | 4     |
| `src/components/Modal/index.js`      | reuse as the full-screen slip viewer                                                                                    | 4     |

## 5. Phases

| Phase | Title                                                           | Gate                                                            |
| ----- | --------------------------------------------------------------- | --------------------------------------------------------------- |
| **1** | [[01-phase-1-decisions-and-data-model\|Decisions & data model]] | Needs the `models/` approval + a ruler on a real DU slip        |
| **2** | [[02-phase-2-storage-and-api\|Storage, presigned upload & API]] | Blocked by Phase 1                                              |
| **3** | [[03-phase-3-app-capture-and-upload\|App capture & upload]]     | Blocked by Phase 2                                              |
| **4** | [[04-phase-4-view-download-share\|Viewing, download & sharing]] | Blocked by Phase 3 (app) / Phase 2 (web)                        |
| **5** | [[05-phase-5-store-compliance\|Store & DPDP compliance]]        | Runs alongside 3–4; **gates the release**, not the code         |
| **6** | [[06-phase-6-ocr\|OCR: auto-fill & cross-check]]                | Blocked by Phase 4; **ships as a separate release** — see below |
| **7** | [[07-phase-7-tests-and-rollout\|Tests & rollout]]               | Continuous; release gate                                        |

> **Ship OCR in a separate release, and re-consent.** Apple guideline **5.1.2(ii)**: _"Data collected for one purpose may not be repurposed without further consent."_ If photo upload ships in v1.79 and OCR arrives in v1.80, **every existing user must be re-consented** before their images go to a third-party OCR vendor. Planning for that now costs nothing; discovering it at review costs a release.

## 6. Risk summary

| Risk                                                     | Detail                                                                                                                                                                                                                                                                 | Mitigation                                                                                                                                                                                                                                 |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🔴 **Pre-existing: no tenant isolation on `so_msts`**    | Given a valid JWT + the shared `X_API_KEY_3`, dealer A can already read dealer B's sales orders by passing B's `dealer_id`. `check_user_company_status()` validates `x-co-id` against the caller but **never cross-checks it against the `dealer_id` in the payload**. | Every new slip endpoint **must** derive `dealer_id` from the token (`getUserFromToken(req.headers)`) and verify `so.dealer_id` matches. Precedent: `api_v3/controllers/collections/veh_trns.js:39-47`. Do not trust a body param. Phase 2. |
| 🔴 **Images leak into invoice payloads and PDFs**        | `api_v3/services/invs.js:659-665` does `SalesOrder.find({...})` with **no `.select()`**, and the result is attached as `invoice.salesOrders`. A new `du_slips` array flows straight into every invoice detail response _and_ into the puppeteer PDF template data.     | Explicit `.select()` exclusion at that call site, plus a test that pins it. Phase 2.                                                                                                                                                       |
| 🟠 **Financial corruption via OCR**                      | A hallucinated or misread litre count written into an SO corrupts ledgers, invoices and GST filings downstream.                                                                                                                                                        | D10: OCR never writes. Arithmetic self-check (`litres × rate ≈ amount`) as a free confidence multiplier. Full audit trail. Phase 6.                                                                                                        |
| 🟠 **Third party in the share link**                     | A DU slip typically names the _customer_ — their vehicle number, sometimes phone. The dealer consents to publishing; the customer never did.                                                                                                                           | Per-share confirmation dialog naming what's exposed; TTL + revoke; `noindex`. Flag to counsel. Phase 4.                                                                                                                                    |
| 🟠 **Store rejection on media**                          | Play's Photo & Video Permissions policy (full compliance mandatory since 28 May 2025) and Apple 5.1.1(iii) both mandate system pickers.                                                                                                                                | D6: picker-first ⇒ no declaration needed, zero Android prompts, one iOS prompt. Phase 5.                                                                                                                                                   |
| 🟠 **Retention vs deletion conflict**                    | Both stores require account deletion to delete user data. DPDP Rule 8(3) requires a **1-year minimum** retention of personal data and logs. GST s.36 requires **~7 years** for invoice-supporting documents.                                                           | Deletion = immediate access revocation + soft delete + hard purge at the legal floor, disclosed verbatim in the privacy policy. Phases 4–5.                                                                                                |
| 🟡 **Cost cliff at 1 TB/month CDN egress**               | The $53/month estimate at 300k images/month depends entirely on CloudFront's always-free 1 TB tier; the blended read model sits at **84%** of it.                                                                                                                      | CloudWatch alarm on `BytesDownloaded` at 800 GB/month. Above ~1.5 TB/month the R2 economics invert hard. Phase 2.                                                                                                                          |
| 🟡 **Every pixel target rests on one unmeasured number** | All resolution maths derives from an assumed ~2.0–2.3 mm printed cap height on a DU slip.                                                                                                                                                                              | **Put a ruler on a real slip before locking Phase 1 §4.** Five-minute task; the whole capture pipeline scales linearly off it.                                                                                                             |
| 🟡 **Orphaned objects and lying clients**                | Client uploads then dies → billed bytes with no DB row. Client claims success without uploading → order looks complete with no slip.                                                                                                                                   | S3 Event Notification is the source of truth, never the client callback. Tag-and-expire lifecycle for un-committed objects. Phase 2.                                                                                                       |
| 🟡 **App has effectively no test suite**                 | `__tests__/App.test.tsx` is the only test in the repo; `@testing-library/react-native` is not installed. `dip-web` has no test runner at all.                                                                                                                          | Phase 7 scopes the minimum harness. Don't let this feature be the thing that finally needs it _and_ pays for it under deadline.                                                                                                            |

## 7. Open questions for the user

Listed here rather than buried in phases, because three of them gate work.

1. **Approval to touch `models/so_msts.js`, `package.json`, and the four `.env` files** in `dzzlo_oms_api`. There is no api_v3-local model layer — no `api_v3/models/`, no schema defined anywhere outside `models/`, and `so_mst_Schema` has no `strict:false` escape hatch, so **a field that isn't in `models/so_msts.js` cannot be persisted at all**. Precedent exists (`9b5a996` added a field to `models/voc_msts.js` alongside api_v3 work). **Blocks Phase 1.**
2. **How many slips per SO, and is a slip mandatory before invoicing?** The spec assumes 1..N optional. If it becomes mandatory, that's an invoice-time validation change with a migration story for existing un-slipped orders.
3. **Who may delete a slip, and after invoicing?** Current assumption: `DPrimary`/`DAdmin` only, and never after `inv_id` is set (an invoiced SO's evidence is a GST record). Confirm.
4. **Is the public share link in scope for v1?** It is the single largest compliance surface here and the only part that exposes third-party data. It could be deferred to v2 with no loss to the core feature. **Recommendation: defer it.**
5. **Is OCR (Phase 6) in scope at all, and on which provider posture?** Cost is *not* the fork it used to be — a mid-tier vision LLM now extracts structured fields for **~$0.27–0.66/1,000 slips**, *cheaper than raw OCR* ($1.50/1,000) and 10–15× cheaper than the purpose-built receipt APIs ($10/1,000), so even 50k slips/month is ~$33/month. The real decisions are (a) whether to build Phase 6 at all, and (b) India-resident processing (Vertex AI `asia-south1` / Bedrock `ap-south-1`) vs the marginally simpler US-routed first-party APIs. Phase 6 argues a position; the call is yours.

## 8. Sequencing note

Phases 1 → 2 → 3 are strictly ordered. Phase 5 (compliance) should be worked **in parallel from day one**, not bolted on: the Android manifest shape and the iOS privacy manifest constrain which capture library is viable, and the consent-flow requirement changes the UI. Phase 4's web half only needs Phase 2. Phase 6 is genuinely optional and separable — the feature is complete and useful without it.

## 9. Sources

All external sources (pricing, policy, law, research papers, package health) with fetch dates and an explicit verification register of what was **not** confirmed: [[references|References & verification register]]. Prices and store policies drift — re-check the register's ⚠️ items before acting on a number.
