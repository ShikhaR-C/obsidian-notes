# References & verification register — tasks_14 DU slips

Every external source behind the eight phase docs. **All fetched 2026-07-29** by the research agents unless noted. Prices, quotas and store policies drift — anything load-bearing should be re-checked against these at build time, and everything in §10 (the verification register) was **not** confirmed and must be verified before acting on it.

Repo-internal evidence (file:line anchors into `dzzlo_oms_api`, `dzzlo_oms_app`, `dip-web`) is cited inline in each phase doc and not repeated here.

---

## 1. Cloud storage & CDN pricing (Phase 2 §1)

| Source | Used for | Notes |
| --- | --- | --- |
| [AWS Price List API — S3 ap-south-1](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/ap-south-1/index.json) | S3 storage/PUT/GET/egress rates, IA tiers | Machine-readable feed, `publicationDate 2026-07-28` — authoritative, not a blog |
| [Azure Retail Prices API](https://prices.azure.com/api/retail/prices) | Azure Blob Central India + Document Intelligence `centralindia` meters (incl. INR) | Live API query; the human pricing pages render `$-` placeholders via JS |
| GCS pricing page — cloud.google.com/storage/pricing | asia-south1 storage + egress | Scraped live |
| Cloudflare R2 docs — developers.cloudflare.com/r2/ | R2 rates, **no presigned POST**, Jurisdictional Restrictions = `eu`/`fedramp` only, `apac` hint "best effort" | Vendor docs, fetched same day |
| Backblaze B2 pricing — backblaze.com | $0.00695/GB, **no Asia region** (US×2, EU Amsterdam, Canada) | Disqualified on region |
| DigitalOcean Spaces pricing — digitalocean.com | BLR1 $5/mo incl. 250 GiB + 1 TiB egress | — |
| E2E Networks EOS | ₹2.5/GB storage, ₹3.0/GB egress | ⚠️ **Secondary sources only**; price revision announced effective 1 Jul 2026 — get a written quote |
| CloudFront pricing — aws.amazon.com/cloudfront/pricing/ | 1 TB/mo + 10M requests **always-free** on pay-as-you-go; $0.109/GB above (India) | 🔴 The whole $53/mo estimate depends on staying on **pay-as-you-go**, not the Nov-2025 flat-rate plans (whose "Free" shows only 100 GB) |
| `CachingOptimized` managed policy `658327ea-f89d-4fab-a63d-7e88639e58f6` — CloudFront docs | Query strings excluded from cache key → signed URLs cache perfectly | Phase 4 §1.2 |

## 2. Image optimisation buy-vs-build (Phase 2 §4)

| Source | Used for |
| --- | --- |
| [ImageKit plans](https://imagekit.io/plans/) | Free tier: **20 GB bandwidth/mo, 3 GB storage, 2 users**; Lite $9 / Pro $89; billing = output bandwidth only. ⚠️ No INR pricing page exists despite being an Indian company |
| Cloudinary pricing — cloudinary.com/pricing | Free 25 credits / Plus $99 (225) / Advanced $249 (600); 1 credit = 1k transformations *or* 1 GB storage *or* 1 GB bandwidth; ⚠️ no published overage for fixed tiers |
| Cloudflare Images pricing — developers.cloudflare.com/images/ | $5/100k stored + $1/100k delivered; transformations $0.50/1k unique, **re-billed monthly** (cost tracks archive size) |
| imgproxy — imgproxy.net | OSS free; Pro $49/mo. HMAC signing **off by default** |
| Thumbor — github.com/thumbor/thumbor | Release cadence: 7.7.0 Oct 2023 → 7.8.0 May 2026 (2.5-year gap) — skip |
| AWS Dynamic Image Transformation (ex–Serverless Image Handler) — aws.amazon.com/solutions/ | AWS's own smallest-tier estimate ≈ **$290/mo floor** (CloudFront $200 + ECS $72 + ALB $17) — skip |

## 3. S3 upload architecture (Phase 2 §2–3)

| Source | Used for |
| --- | --- |
| AWS docs — [Creating a POST policy (SigV4)](https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-HTTPPOSTConstructPolicy.html) | `content-length-range`, `eq`/`starts-with` conditions, `expiration`; **`file` must be the last form field** |
| AWS docs — [S3 actions/condition keys reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html) | Full condition-key enumeration: **no `s3:content-length`, no content-type** → IAM cannot cap upload size; `s3:signatureAge` exists |
| AWS docs — presigned URLs | *"You can use the presigned URL **multiple times**, up to the expiration date and time"* → leaked PUT URL = overwrite primitive |
| AWS docs — [S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/EventNotifications.html) | *"designed to be delivered **at least once**"*, *"typically … seconds but can sometimes take a minute or longer"* → idempotent handler mandatory |

## 4. React Native — capture, transport, offline (Phase 3)

### 4.1 Verified in RN 0.84.1 source (paths are the citation)

| Path (in `react-native@0.84.1`) | Finding |
| --- | --- |
| `Libraries/Network/convertRequestBody.js` | `{uri: string, ...}` is a first-class `RequestBody` type — deliberate pass-through, not a fall-through |
| `ReactAndroid … NetworkingModule.kt` + `RequestBodyUtil.kt` | `{uri}` body → `Okio.source(inputStream)` streaming; `contentLength()` = `inputStream.available()` (line 143) — the "EntityTooLarge on a 300 KB file" mechanism for `content://` streams |
| `ReactAndroid … BlobModule.kt` | Blob body = whole file as `ByteArray` in native heap (`HashMap<String, ByteArray>`) |
| `Libraries/Network/RCTNetworking.mm` | iOS `{uri}` documented in source comment; buffers via nested `RCTNetworkTask` → `NSData` |
| `whatwg-fetch` 3.6.20 (RN's unmodified polyfill) | Unrecognised body object → local `"[object Object]"` + default `text/plain` Content-Type **while still sending the correct `{uri}` body** → silent presigned-403 unless Content-Type set explicitly |

### 4.2 Packages & ecosystem

| Source | Used for |
| --- | --- |
| [react-native-blob-util #479](https://github.com/RonRadtke/react-native-blob-util/issues/479) | Open bridgeless/New-Arch cold-start crash (module-scope `NativeEventEmitter`), opened 2026-07-21 — demoted |
| [react-native-image-picker](https://github.com/react-native-image-picker/react-native-image-picker) | README: Photo Picker + PHPicker + `ACTION_IMAGE_CAPTURE`; the CAMERA-in-manifest caveat; `androidx.activity:activity:1.9.+` at minSdk<30; `saveToPhotos` needs manual `WRITE_EXTERNAL_STORAGE` ≤API 28 |
| [react-native-permissions](https://github.com/zoontek/react-native-permissions) | ⚠️ 5.6.1 (~2026-07-24) — probably unneeded with picker-first design; re-check before pinning |
| npm: `@bam.tech/react-native-image-resizer` | Android two-stage downscale verified in source: `calculateInSampleSize()` (area-averaging) + bilinear residual ≤2× — correct for dot-matrix; iOS = CoreGraphics default (eyeball it) |
| npm: `@kesha-antonov/react-native-background-downloader` 4.5.9 (2026-07-24) | Does raw-binary uploads (omit `fieldName`/`parameters` → `setFixedLengthStreamingMode`); iOS half textbook, Android half best-effort in-process → deferred, not adopted |
| [RTK #1610](https://github.com/reduxjs/redux-toolkit/issues/1610) | RTK Query offline mutation queue: closed 2023, nothing shipped |
| [RTK #5180](https://github.com/reduxjs/redux-toolkit/issues/5180) | redux-persist effectively dead; `redux-remember` 6.0.2 proposed successor |
| redux-offline — github.com/redux-offline/redux-offline | **Archived 2026-04-01** |
| TanStack Query v5 docs | Only mainstream data layer with a real offline mutation queue (`networkMode:'offlineFirst'`, `resumePausedMutations()`) — comparison point, not a migration |
| AsyncStorage docs | Android SQLite backend **6 MB default cap** (`AsyncStorage_db_size_in_MB` gradle prop) |
| Apple URLSession docs | *"If the user terminates the app from the multitasking screen, the system cancels all of the session's background transfers"* |
| Android 15/16 behavior docs | `dataSync` FGS capped 6 h/24 h (`Service.onTimeout()`); Android 16 FGS-launched jobs under normal quotas |

### 4.3 Capture / document scanning

| Source | Used for |
| --- | --- |
| ML Kit Document Scanner — developers.google.com/ml-kit | Android first-party scanner via Play services (edge detection, perspective, glare) |
| VisionKit `VNDocumentCameraViewController` — developer.apple.com/documentation/visionkit | iOS first-party equivalent |
| ML Kit Text Recognition v2 — developers.google.com/ml-kit/vision/text-recognition/v2 | On-device gate; bundled-vs-unbundled distribution; *"try asking the user to recapture"* guidance. ⚠️ Per-element confidence believed absent — verify |
| Apple Vision `VNRecognizeTextRequest` — developer.apple.com/documentation/vision | `.accurate` mode returns per-candidate `confidence`; 🔴 set `usesLanguageCorrection = false` for receipts |

## 5. OCR / resolution research (Phases 1 §4, 3 §4, 6)

| Source | Finding used |
| --- | --- |
| [Textract hard limits](https://docs.aws.amazon.com/textract/latest/dg/limits-document.html) + FAQ | **15 px min text height** ("8 pt at 150 DPI"); max 10,000 px/side; **JPEG/PNG/PDF/TIFF only — no WebP/AVIF** (forces JPEG archival variant) |
| [Azure DI service limits](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/service-limits) + [receipt model](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/receipt) | **12 px min text height** @1024×768; 50×50→10,000×10,000 px |
| Google Cloud Vision docs | Recommends **1024×768** for OCR — *"OCR requires more resolution to detect characters"* |
| Tesseract docs — [ImproveQuality](https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html) | *"works best on images which have a DPI of at least 300 dpi"* — the design target |
| "Text-Aware Single Image Specular Highlight Removal" (PRCV 2021) | Glare removal on real photos: recall **64.85% → 78.50%** (+13.65 pts) → capture-time glare gate is the highest-leverage build |
| KORIE receipt benchmark — MDPI *Mathematics* 14(1):187 (17,587 real receipt crops) | CER **PaddleOCR 15.84% / EasyOCR 17.36% / Tesseract 25.43%**, persisting at 300 dpi scan — human validation is permanent |
| Tesseract mailing list (dot-matrix threads) | Higher resolution *fragments* dot-matrix glyphs → downscale filter choice (area/Lanczos) matters, not capture resolution |
| GDELT blog (binarization side-by-sides) | Sauvola helps some channels, *"prevents any text from being recognized at all"* in others → don't binarize (asymmetric risk — **no controlled benchmark exists**) |
| n=1020 dot-matrix comparison (community, single test) | Textract "1 wrong character in 1020" zero-config vs Tesseract ~80% with tuning — ⚠️ single data point |
| [arXiv 2509.04469](https://arxiv.org/html/2509.04469v1) — vision vs OCR-text parsing, 1,850 docs | **SROIE receipts: native image 87.46% vs OCR-text 47.00%**; 0↔O/1↔I worst on alphanumeric IDs (vehicle numbers) |
| [arXiv 2606.24420](https://arxiv.org/pdf/2606.24420) — confidence beyond logprobs | Logprobs **saturate >0.999 under constrained JSON decoding**; evidence-grounding (Hunter–Mapper) 0.928 AUC; ~165 samples to calibrate |
| [ICDAR 2019 SROIE](https://rrc.cvc.uab.es/?ch=13) | The receipt benchmark behind the 87.46% anchor |
| [Fuel bill format requirements](https://www.freefuelbill.in/resources/fuel-bill-format-requirements) | Indian pump receipts: 80 mm thermal roll context |
| ESC/POS Font A geometry (printer spec) | 12×24 dot cell @180 dpi → ~2.3 mm cap height — 🔴 the one **assumed** number; measure a real slip (Phase 1 §4) |
| [Landing.ai HITL review workflows](https://landing.ai/llms/building-human-in-the-loop-review-workflows-for-document-ai) | Human-in-the-loop patterns |

## 6. OCR providers — pricing, regions, data terms (Phase 6)

### AWS Textract

| Source | Used for |
| --- | --- |
| [Pricing](https://aws.amazon.com/textract/pricing/) + [Price List API region index](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonTextract/current/region_index.json) | DetectDocumentText $1.50/1k, **AnalyzeExpense $10/1k** — ap-south-1 == us-west-2 to the last decimal |
| [Endpoints & quotas](https://docs.aws.amazon.com/general/latest/gr/textract.html) + [regional services table](https://api.regional-table.region-services.aws.a2z.com/index.json) | Mumbai only (no ap-south-2); 🔴 **AnalyzeExpense 1 TPS default in Mumbai** vs 5 in us-east-1 |
| [AnalyzeExpense fields](https://docs.aws.amazon.com/textract/latest/dg/invoices-receipts.html) + [response objects](https://docs.aws.amazon.com/textract/latest/dg/expensedocuments.html) | Retail schema; first-class `VENDOR_GST_NUMBER`/`PAN`; **no nozzle/rate-per-litre field** → `EXPENSE_ROW` |
| [Textract FAQs](https://aws.amazon.com/textract/faqs/) | 🔴 **Trains on inputs by default**; English-only for receipts; *"may store such content in an AWS Region outside of the AWS Region where you are using the service"* |
| [AI services opt-out policies](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out.html) + [covered services](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_ai-opt-out_all.html) | The Organizations opt-out (also deletes historical copies) — attach **before** the first call |

### Azure AI Document Intelligence

| Source | Used for |
| --- | --- |
| [Pricing (US)](https://azure.microsoft.com/en-us/pricing/details/ai-document-intelligence/) / [India INR](https://azure.microsoft.com/en-in/pricing/details/ai-document-intelligence/) + Retail Prices API | Read $1.50/1k (₹141.59), prebuilt $10/1k (₹943.94), custom $30/1k, training $3/hr (10 h/mo free). ⚠️ `S0 Query Pages` $200/1k vs `query fields` $10/1k anomaly unresolved |
| Retail Prices API region probe | **Central India + Jio India West only** — zero DI meters in southindia/westindia (not missing data: other AI meters exist there) |
| [Receipt schema 2024-11-30-GA](https://github.com/Azure-Samples/document-intelligence-code-samples/blob/main/schema/2024-11-30-ga/receipt.md) + [prebuilt receipt](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/receipt) | `receipt.gas` sub-type exists but reuses the generic schema — no fuel fields |
| [Language support](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/language-support/prebuilt) | ~110 languages incl. Hindi/Marathi/Tamil/Punjabi |
| [Accuracy & confidence](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/accuracy-confidence?view=doc-intel-4.0.0) | Field+word confidence 0–1; *"not all document fields return a confidence score"* |
| [Data privacy & security](https://learn.microsoft.com/en-us/legal/cognitive-services/document-intelligence/data-privacy-security) + [FAQ](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/faq) | Same-region processing; 24 h retention + delete API. ⚠️ No-training claim rests on a MS-employee Q&A answer, not a formal policy doc |
| [Troubleshoot latency](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept/troubleshoot-latency) | No latency SLA; >15 s/page sustained = "address the issue"; async-only (202 + poll) |
| [Custom neural](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/train/custom-neural?view=doc-intel-4.0.0) | Region list incl. Central India; model Copy API |

### Google

| Source | Used for |
| --- | --- |
| [Cloud Vision pricing](https://cloud.google.com/vision/pricing) | Both TEXT features $1.50/1k (1,001–5M); requesting both bills twice |
| [Cloud Vision REST reference](https://docs.cloud.google.com/vision/docs/reference/rest) | 🔴 Single global endpoint — **cannot** be pinned to India |
| [Document AI regions](https://docs.cloud.google.com/document-ai/docs/regions) | asia-south1: OCR, Form, Layout, Custom Extractor, CE-with-GenAI (Preview); **Expense/Invoice parser absent** |
| [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) | 2.5 Flash-Lite $0.10/$0.40 → **$0.27/1k slips**; 3.1 Flash-Lite → $0.66; 🔴 paid tier no-training, **free/AI-Studio tier trains** |
| [Gemini image understanding](https://ai.google.dev/gemini-api/docs/image-understanding) | 2.5-series tiling: 258 tok/tile, crop unit `floor(min(w,h)/1.5)` → 6 tiles for 1000×1400. ⚠️ Gemini 3 `media_resolution` ≈1,120 tok — medium confidence |

### Anthropic / OpenAI / Mistral

| Source | Used for |
| --- | --- |
| [Claude vision](https://platform.claude.com/docs/en/build-with-claude/vision) | `⌈w/28⌉ × ⌈h/28⌉` patches → 1,800 tok @1000×1400; high-res tier (4.7+) 2,576 px / 4,784 tok; Haiku 4.5 standard tier caps 1,568 |
| [Claude pricing](https://platform.claude.com/docs/en/about-claude/pricing) | Haiku 4.5 $1/$5 → $3.32/1k; Sonnet 5 intro $2/$10 to 2026-08-31 then $3/$15; Opus 5 $5/$25; batch = half; `inference_geo:"us"` ×1.1 |
| [Claude structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) | Grammar-constrained decoding; unsupported keywords (`minimum`/`pattern`/…); `anyOf` nullable; ~500 ms first-schema compile, 24 h cache; 🔴 schema cached separately from message content — no customer data in schemas; `temperature`/`top_p`/`top_k` → 400 on Opus 5/Sonnet 5 |
| [Claude data residency](https://platform.claude.com/docs/en/manage-claude/data-residency) | 🔴 `inference_geo` = `"us"` \| `"global"` only — **no India geo**; India path = Vertex/Bedrock |
| [Claude API data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention) | *"Retained data is never used for model training without your express permission"*; ZDR on request |
| [OpenAI pricing](https://developers.openai.com/api/docs/pricing) + [images & vision](https://developers.openai.com/api/docs/guides/images-vision) | `⌈w/32⌉ × ⌈h/32⌉` = 1,408 patches; gpt-5-mini ×1.62 multiplier → ~$1.05/1k. ⚠️ Full-size multiplier unpublished (1.0 assumed) |
| [Mistral pricing](https://mistral.ai/pricing/api) + [Mistral OCR news](https://mistral.ai/news/mistral-ocr-3/) | OCR 4 $4/1k ($2 batch). ⚠️ Residency/DPA unverified |

## 7. Google Play & Android (Phase 5 §1–2)

| Source | Used for |
| --- | --- |
| [Target SDK requirements](https://developer.android.com/google/play/requirements/target-sdk) + [deadline answer](https://support.google.com/googleplay/android-developer/answer/11926878) | API 36 from 31 Aug 2026 (extension to 1 Nov 2026) — repo already compliant |
| [Photo Picker](https://developer.android.com/training/data-storage/shared/photopicker) | *"No runtime permissions are required"*; `ModuleDependencies` backport service (mandatory at minSdk 24) |
| [Permissions & sensitive-info APIs](https://support.google.com/googleplay/android-developer/answer/16558241) + [Photo & Video Permissions policy](https://support.google.com/googleplay/android-developer/answer/14115180) + [required actions](https://support.google.com/googleplay/android-developer/answer/15800983) | `READ_MEDIA_*` only *"if system pickers are not sufficient"*; *"custom pickers are not automatically qualified"*; full compliance mandatory since 28 May 2025 |
| [Declaration form process](https://support.google.com/googleplay/android-developer/answer/9214102) | Reviews "may require up to several weeks" |
| [User Data policy](https://support.google.com/googleplay/android-developer/answer/10144311) + [Prominent disclosure](https://support.google.com/googleplay/android-developer/answer/11150561) | In-app, before use, Why/What/How, two options ("Agree", not "Allow access") |
| 🔴 [Policy announcement 15 Jul 2026](https://support.google.com/googleplay/android-developer/answer/17134731) | *"User Data requirements also apply to **third-party AI integrations**"* — compliance ~14 Aug 2026 |
| [Announcement 15 Apr 2026](https://support.google.com/googleplay/android-developer/answer/16926792) | Contact-picker mandate + location button, effective 28 Oct 2026 — direction of travel |
| [Data safety form](https://support.google.com/googleplay/android-developer/answer/10787469) | "Collect"/"Share" definitions; service-provider carve-out; automated AAB pre-review checks |
| [Account deletion](https://support.google.com/googleplay/android-developer/answer/13327111) | In-app path + web URL (no reinstall); delete propagation to service providers; disclosed retention carve-out |
| [Partial photo/video access](https://developer.android.com/about/versions/14/changes/partial-photo-video-access) · [uses-feature](https://developer.android.com/guide/topics/manifest/uses-feature-element) · [package visibility](https://developer.android.com/training/package-visibility/declaring) · [FileProvider](https://developer.android.com/training/secure-file-sharing/setup-sharing) · [requesting permissions](https://developer.android.com/training/permissions/requesting) · [Android 16 changes](https://developer.android.com/about/versions/16/behavior-changes-16) | Manifest block details; CAMERA implicit `uses-feature` trap; `<queries>` for `resolveActivity()`; permanent-denial rule; *"Don't link to system settings in an effort to convince the user"* |
| [Google Search — blocking indexing](https://developers.google.com/search/docs/crawling-indexing/block-indexing) | `X-Robots-Tag` on non-HTML; 🔴 noindex requires the path **not** be robots.txt-blocked |

## 8. Apple (Phase 5 §3)

| Source | Used for |
| --- | --- |
| [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) + [update news 13 Nov 2025](https://developer.apple.com/news/?id=ey6d8onl) | 🔴 5.1.2(i): *"…including with **third-party AI**, and obtain explicit permission"*; 5.1.2(ii) repurposing → re-consent; 5.1.2(iv) no contact database from Photos; 5.1.1(iii) *"use the out-of-process picker"* |
| [PHPickerViewController](https://developer.apple.com/documentation/photokit/phpickerviewcontroller) + [enhanced privacy](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app) + [selecting photos](https://developer.apple.com/documentation/PhotoKit/selecting-photos-and-videos-in-ios) | *"The user doesn't need to explicitly authorize your app to select photos"* — no prompt, no plist key (NSItemProvider-only) |
| [Requesting access to protected resources](https://developer.apple.com/documentation/uikit/requesting-access-to-protected-resources) | ITMS-90683: purpose string required if **any pod** references the API |
| [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files) + [reason codes](https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitype) + [adding a manifest](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk) + [enforcement news](https://developer.apple.com/news/?id=3d8a9yyh) | ITMS-91053 since 1 May 2024; ITMS-91061 since 12 Feb 2025; DiskSpace `E174.1` vs `85F4.1` distinction |
| [Third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/) | Firebase + OneSignal on the mandatory list (their manifests confirmed on disk in Pods) |
| [App privacy details](https://developer.apple.com/app-store/app-privacy-details/) | Nutrition label: `Photos or Videos`, Linked = Yes; "collect" spans third-party partners |
| [Offering account deletion](https://developer.apple.com/support/offering-account-deletion-in-your-app/) | 5.1.1(v) since 30 Jun 2022; delete the record, in-app initiation |

## 9. India — DPDP, CERT-In, GST, Companies Act (Phases 1 §4.3, 5 §4, 6 §6)

| Source | Used for |
| --- | --- |
| 🔴 [DPDP Rules 2025 — G.S.R. 846(E) Gazette PDF](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf) | Primary source, text extracted. Commencement: Rules 3, 5–16, 22–23 **+18 months** (≈13–14 May 2027); Rule 4 +12 months. Rule 3 notice, Rule 6 safeguards (encryption named; 1-yr logs; processor flow-down), Rule 7 breach (without delay + 72 h), Rule 8(3) 1-yr minimum retention, Rule 9 contact, Rule 14 90-day grievance, Rule 15/13(4) cross-border. *Fetch note: meity.gov.in blocks default clients — use a browser UA* |
| [PIB DPDP explainer](https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf) | Corroboration; "22 scheduled languages" note behind the Rule 3 i18n flag |
| DPDP Act 2023 (statute) | s.5 notice, s.7 legitimate uses, s.8(2) processor contract, s.8(7) erasure vs other-law retention, **s.16 blacklist (zero countries notified)**, s.33 + Schedule penalties (₹250 cr / ₹200 cr / ₹50 cr) |
| 🔴 [CERT-In Directions 28 Apr 2022](https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf) | Primary PDF: **6-hour incident reporting** (incl. cloud-server attacks), 180-day ICT logs, NTP to NIC/NPL, PoC designation; s.70B(7) penalty |
| CERT-In FAQs (May 2022), Q35 — cert-in.org.in | *"The logs **may be stored outside India** also as long as the obligation to produce logs to CERT-In is adhered to"* — producibility, not residency (several law-firm notes state the opposite; they are wrong) |
| CGST Act s.35–36 + Rules 55–57, 56(8)/(15)/(16) (CBIC consolidated text) | 72-month retention from annual-return due date (→ plan 7 years; FY 2024-25 ≈ 31 Dec 2031); electronic records expressly permitted; **no server-location requirement**; duty sits on the *registered person* (the dealer) |
| Companies (Accounts) Rules, Rule 3(5) as amended by G.S.R. 624(E), 5 Aug 2022 | Daily India-located backup — binds **your own books of account**, not customer slip photos; audit-trail/edit-log for FYs from 1 Apr 2023 (⚠️ perimeter question for the OCR decision log — counsel) |
| RBI Storage of Payment System Data (6 Apr 2018) + PA/PG Guidelines 2020 | Binds authorised payment operators — **not you**; merchants must not store card data |
| MeitY notification F. No. 2(1)/2026-Pers.I (6 May 2026) | Data Protection Board still being staffed — no functioning enforcement body yet |

---

## 10. Verification register — ⚠️ NOT confirmed; check before acting

Consolidated from every phase doc's uncertainty flags. Ordered roughly by how much rides on them.

| # | Item | Where used | Risk if wrong |
| --- | --- | --- | --- |
| 1 | 🔴 **Real DU slip cap-height (~2.0–2.3 mm assumed)** | Phase 1 §4, Phase 3 §4 | Every pixel/upload-size target scales linearly. Measure first — 5 minutes |
| 2 | 🔴 **CloudFront pay-as-you-go 1 TB free tier still intact** (vs Nov-2025 flat-rate plans) | Phase 2 §1 | The $53/mo estimate collapses to ~$135 without it |
| 3 | Document-scanner RN wrapper health (`react-native-document-scanner-plugin`, `@react-native-ml-kit/*`) — New-Arch on RN 0.84 | Phase 3 §2.1 | Falls back to `react-native-image-picker` (already planned) |
| 4 | `@bam.tech/react-native-image-resizer` New-Arch status | Phase 3 §4.2 | Need an alternative resizer |
| 5 | ML Kit Text Recognition v2 per-element **confidence absent** | Phase 6 §2 | Load-bearing for "gate only, never extract" on Android |
| 6 | Vertex AI `asia-south1`: Gemini model list, +10% premium, per-model residency guarantees | Phase 6 §3/§6 | The India-resident extractor path |
| 7 | Gemini 3 `media_resolution` ≈1,120 tokens/image | Phase 6 §3.1 | Cost arithmetic (2.5-series tiling is verified) |
| 8 | GPT-5.6 full-size patch multiplier (1.0 assumed) | Phase 6 §3.1 | OpenAI cost row |
| 9 | OpenAI India residency; Mistral DPA/residency | Phase 6 §6.1 | Provider shortlist |
| 10 | Azure `S0 Query Pages` $200/1k vs `query fields` $10/1k anomaly | Phase 6 §1 | 20× cost surprise if Query Fields bills at the wrong meter |
| 11 | Azure DI v4.0 `2024-11-30` GA enabled in Central India (no per-region API-version matrix) | Phase 6 §1 | Test with a throwaway resource first |
| 12 | Azure no-training claim = MS-employee Q&A answer, not formal policy | Phase 6 §6.1 | Get it in the DPA |
| 13 | `receipt.gas` enum string (`receipt.gas` vs `Fuel&Energy.Gas`) inconsistent in docs | Phase 6 §1.2 | Don't hardcode before a live response |
| 14 | Google Doc AI per-processor prices (Expense ~$100/1k, CE hosting ~$438/yr) | Phase 6 §1 | Shelf option only |
| 15 | Cloud OCR latency 2–4 s/page (no vendor publishes p50/p99) | Phase 6 §4/§8 | The 8-second sync budget — measure from Mumbai day one |
| 16 | E2E Networks EOS pricing (secondary sources; 1 Jul 2026 revision) | Phase 2 §1 | Not on the recommended path |
| 17 | Cloudinary cost at scale (extrapolated; no published overage) | Phase 2 §4 | Not on the recommended path |
| 18 | ImageKit INR/GST invoicing (site is USD-only) | Phase 2 §4.2 | Only if the free-tier shortcut is taken |
| 19 | `react-native-permissions` 5.6.1 version/date | Phase 5 §5.3 | Probably not needed at all |
| 20 | ITMS-91053 exact wording (trigger condition solid; string community-sourced) | Phase 5 §3c | Cosmetic |
| 21 | 🔴 DPDP **Act** commencement notification (G.S.R. 843(E)) — Rules verified, Act's section-by-section not | Phase 5 §4.1 | **Counsel** |
| 22 | SPDI Rules 2011 / IT Act s.43A status (whether DPDP s.44 commenced) | Phase 5 §7 | **Counsel** |
| 23 | Rule 3 notice language set (Eighth Schedule / "22 languages") | Phase 5 §4.5 | **Counsel** — real product cost (i18n scaffolding hedges it) |
| 24 | Any s.16 / Rule 15 cross-border order naming a vendor jurisdiction | Phase 6 §6 | Re-check at go-live; provider-behind-interface hedges it |
| 25 | Companies Act audit-trail perimeter over the OCR extraction/decision logs | Phase 6 §7.3 | Auditor — would make append-only a *legal* requirement |
| 26 | Statutory retention perimeter for slip images as GST supporting docs (duty is the dealer's; your exposure contractual) | Phase 1 §4.3 | Auditor |
| 27 | Play Console UI flow for the declarations (pages reshuffle frequently) | Phase 5 §7 | Verify in console at submission |
| 28 | Apple guidelines are a living document (no last-updated stamp) | Phase 5 §7 | Re-check developer.apple.com/news before each submission |
| 29 | Data Protection Board appointment status (still advertising 6 May 2026) | Phase 5 §7 | Context only |
| 30 | Binarization-hurts-cloud-OCR has **no benchmark** (asymmetric-risk argument only) | Phase 2 §4.3 | Recommendation unchanged; don't cite a benchmark that doesn't exist |
| 31 | Textract ≫ Tesseract on dot-matrix (single n=1020 community test) | Phase 6 §2 | Directional only |

**Standing rule:** anything from §1–§2 (prices) older than a quarter, and anything from §7–§8 (store policy) older than a release cycle, gets re-fetched before it's used to justify a decision.
