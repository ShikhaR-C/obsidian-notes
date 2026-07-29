# Phase 2 — Storage, presigned upload & API

**Blocked by:** Phase 1 (schema + approvals).
**Delivers:** an S3 bucket, a CDN, a post-upload worker, and four `api_v3` endpoints. After this phase, an image can be uploaded and read back by an authorised caller — with no app changes yet.

---

## 1. D1 — S3 `ap-south-1` + CloudFront

### 1.1 The comparison, at real prices

AWS figures pulled from the Price List API, `publicationDate 2026-07-28`. Others from vendor docs, same day.

| Provider           | Storage $/GB-mo | PUT /1k | GET /1k | **Egress $/GB** | Presigned POST | India region |
| ------------------ | --------------- | ------- | ------- | --------------- | -------------- | ------------ |
| **S3 ap-south-1**  | 0.025           | 0.005   | 0.0004  | 0.1093          | ✅             | ✅ Mumbai    |
| Cloudflare R2      | **0.015**       | 0.0045  | 0.00036 | **$0.00**       | ❌             | ❌           |
| GCS asia-south1    | 0.020           | 0.005   | 0.0004  | 0.12            | ✅             | ✅           |
| Azure Central India| 0.020           | 0.0055  | 0.00044 | 0.11–0.12       | SAS            | ✅           |
| Backblaze B2       | 0.00695         | free    | free    | free to 3×      | ✅             | ❌ no Asia   |
| DO Spaces BLR1     | $5/mo inc 250GB | free    | free    | 1 TiB inc.      | ✅             | ✅ Bangalore |

**Cost model.** 3 variants/image (thumb 15 KB + view 120 KB + orig 350 KB = **485 KB, 3 objects**); blended delivery 250 KB/image/month; 4 GETs/image/month. Figures at **month 12** of steady intake.

**(a) 5,000 images/month** → 28.4 GB stored, 14.3 GB delivered:

```
S3 storage    28.4 GB × $0.025      = $0.71
PUTs          15,000  × $0.005/1000 = $0.075
CloudFront    14.3 GB               = $0.00   (inside 1 TB always-free)
Requests      240k                  = $0.00   (inside 10M free)
Origin GETs                         = $0.01
                                    ────────
                                      $0.80/mo  (₹69)
```
R2 would be $0.28. **At this volume the difference is ₹45/month. Do not optimise here.**

**(b) 300,000 images/month** → 1,705 GB stored, 858 GB delivered:

```
S3 storage    1,705 GB × $0.025       = $42.63
PUTs          900k     × $0.005/1000  =  $4.50
CloudFront DTO 858 GB                 =  $0.00   (< 1024 GB free tier)
CloudFront req 4.4M × $0.0120/10k     =  $5.28
Origin GETs                           =  $0.58
                                      ────────
                                        $52.98/mo  (₹4,610)
```
R2 + Cloudflare: **$31.75**. S3 without a CDN: **$135.77** (egress alone is $82.85).

### 1.2 Why not R2, given it's cheaper

R2 is genuinely ~$250/year cheaper. Four reasons it still loses:

1. **No India jurisdiction.** R2's Jurisdictional Restrictions support exactly `eu` and `fedramp`. `apac` is a *location hint*, and Cloudflare's own docs say hints *"are a best effort and not a guarantee."* When a dealer's auditor asks where the data is, "somewhere in APAC, best-effort" is a bad answer.
2. **R2 does not support presigned POST** — *"POST (multipart form uploads via HTML forms) is not currently supported."* That breaks D2 outright and costs you server-side size enforcement. This is a security regression, not a preference.
3. **No Object Lock, versioning or tagging** via the S3 API — you need tagging for orphan cleanup (§3.4) and Object Lock for tamper-evident GST retention.
4. **You are already on AWS** (`@aws-sdk/client-sesv2`, and `vsystimages.s3.ap-south-1.amazonaws.com` already hosts the invoice logo). Same account, IAM, region, bill, CloudTrail. Native S3 → EventBridge → Lambda; R2 forces everything through Cloudflare Queues.

> ### The named revisit trigger
> The whole $53/month figure depends on CloudFront's **1 TB always-free** egress tier, and the blended read model sits at **84%** of it.
>
> | Delivered/mo | S3+CloudFront | R2+CF  | Delta    |
> | ------------ | ------------- | ------ | -------- |
> | ≤1,024 GB    | $52.98        | $31.75 | $21      |
> | 1,500 GB     | $104.87       | $31.75 | $73      |
> | 2,048 GB     | $164.61       | $31.75 | $133     |
> | 5,120 GB     | $499.45       | $31.75 | **$468** |
>
> **Set a CloudWatch alarm on CloudFront `BytesDownloaded` at 800 GB/month.** Sustained >1.5 TB/month → move to R2; the economics invert hard.
>
> ⚠️ Also: **stay on CloudFront pay-as-you-go.** The flat-rate plans launched Nov 2025 show only 100 GB + 1M requests on their "Free" tier. Pay-as-you-go explicitly retains 1 TB DTO + 10M requests always-free. Verify before the distribution is created.

### 1.3 Lifecycle

- **Transition only the archival original** to Standard-IA at 90 days. `105 GB × ($0.025 − $0.0138) = $1.18/mo` saved recurring vs `$0.01/1,000` transition cost — payback ~2.5 months over a 7-year horizon.
- ❌ **Do not transition thumbnails.** IA bills a **128 KB minimum object size**; a 15 KB thumb would be billed at 128 KB — an **8.5× increase**.
- ❌ **Skip Intelligent-Tiering.** Monitoring is $0.0025/1,000 objects/month ≈ $27/month at 10.8M objects, and objects <128 KB are never tiered anyway.
- ✅ **Add `AbortIncompleteMultipartUpload: 1 day` regardless.** Free insurance against a silent bill.
- ✅ **Object Lock, Governance mode**, applied on commit — tamper-evident retention for the GST horizon (Phase 1 §4.3).

### 1.4 Bucket config

```
Bucket:            dzzlo-slips              (ap-south-1)
Block Public Access: ALL ON
Encryption:        SSE-KMS, customer-managed key   (~$0.90/mo at 300k images)
Versioning:        Enabled
Object Lock:       Governance mode, applied at commit
Access:            CloudFront Origin Access Control only
```

SSE-KMS is not decoration — **DPDP Rule 6(1)(a)** names *"encryption, obfuscation, masking or the use of virtual tokens"* as a minimum safeguard, by name. It's the cheapest strong audit story available.

---

## 2. D2 — presigned POST policy

| Option                  | Enforces size? | Round trips | Verdict                                                                                                                        |
| ----------------------- | -------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------ |
| (a) Proxy via Express   | ✅ full control | 2           | Fine at 5k/mo. At 300k/mo it pushes ~145 GB/mo through Express and holds sockets 40 s on dying 3G. Also forces raising the 1 MB body limit. **No.** |
| (b) Presigned PUT       | ❌ **cannot**   | 1           | See below                                                                                                                       |
| (c) **Presigned POST**  | ✅              | 1           | **Recommended**                                                                                                                 |
| (d) Multipart           | ❌              | 3+          | For 300 KB objects: 3× request cost + orphaned-part billing. **No.**                                                             |

**Why PUT fails on security.** There is **no `s3:content-length` IAM condition key.** The full current list is `s3:x-amz-acl`, `s3:x-amz-server-side-encryption`, `s3:x-amz-storage-class`, `s3:x-amz-copy-source`, `s3:x-amz-object-if-match`, `s3:ResourceAccount`, `s3:TlsVersion`, `s3:prefix`, `s3:max-keys`, `s3:VersionId`, `s3:signatureAge`. **No content-length. No content-type.** IAM cannot cap upload size. And AWS documents that *"You can use the presigned URL **multiple times**, up to the expiration date"* — a leaked PUT URL is an overwrite primitive for its whole TTL.

The POST policy is the **only** mechanism S3 enforces server-side for size.

### 2.1 The policy

```json
{
  "expiration": "2026-07-29T10:35:00Z",
  "conditions": [
    { "bucket": "dzzlo-slips" },
    ["starts-with", "$key", "u/d_8891/2026/07/so_44127/01J8XQ2M/"],
    ["content-length-range", 8192, 1048576],
    ["eq", "$Content-Type", "image/jpeg"],
    { "x-amz-server-side-encryption": "aws:kms" },
    { "x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:ap-south-1:…:key/…" },
    { "success_action_status": "201" }
  ]
}
```

Five things that are each load-bearing:

1. **The server generates the entire key**, including a ULID. The client never proposes it. `u/{dealerId}/{yyyy}/{mm}/{soId}/{ulid}/orig.jpg`. Cross-tenant writes become impossible even with a leaked policy.
2. **`content-length-range` 8 KB – 1 MB.** The floor rejects truncated/empty uploads; the ceiling is ~2.5× the 400 KB target — headroom for a bad-light shot, far short of an abuse payload.
3. **`eq` on Content-Type, never `starts-with "image/"`.** `starts-with` admits `image/svg+xml` — a stored-XSS vector aimed straight at the `dip-web` admin.
4. **5-minute TTL.** A 400 KB upload on bad 3G is 20–40 s; 5 min is generous.
5. **`file` must be the LAST form field.** S3 ignores anything after it. This bites everyone once.

### 2.2 Belt-and-braces at the bucket

```json
{ "Sid": "DenyStalePresign", "Effect": "Deny", "Principal": { "AWS": "*" },
  "Action": "s3:*", "Resource": "arn:aws:s3:::dzzlo-slips/*",
  "Condition": { "NumericGreaterThan": { "s3:signatureAge": "600000" } } }
```
(`s3:signatureAge` is a real current condition key; 600000 ms = 10 min.) Add a matching `aws:SecureTransport: false` deny.

### 2.3 IAM for the signing role

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Sid": "SignUploadsIntoStagingPrefixOnly",
      "Effect": "Allow", "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::dzzlo-slips/u/*",
      "Condition": { "StringEquals": {
        "s3:x-amz-server-side-encryption": "aws:kms",
        "s3:x-amz-server-side-encryption-aws-kms-key-id": "arn:aws:kms:ap-south-1:<acct>:key/<id>" } } },
    { "Sid": "VerifyOnly", "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:GetObjectAttributes"],
      "Resource": "arn:aws:s3:::dzzlo-slips/u/*" }
  ]
}
```

Deliberately absent: `s3:DeleteObject`, `s3:PutObjectAcl`, anything on `img/*`.

**Note the division of labour:** size and content-type are enforced by the **POST policy** (IAM cannot); prefix, encryption and no-delete are enforced by **IAM** (the policy cannot). You need both.

---

## 3. The commit path — and why the client is never trusted

### 3.1 Flow

```
1. POST /api/v3/so_msts/:id/slips/presign   { sha256, bytes, width, height }
   → server: authorize, cap count, mint ULID + key, insert du_slips[] row (state:"pending")
   → returns { slipId, url, fields }
2. client: FormData(...fields, file LAST) → POST to S3         [3 retries, jittered]
3. POST /api/v3/so_msts/:id/slips/:slipId/commit               [UI only, NEVER trusted]
   → state: "claimed"; returns immediately so the UI can move on
4. (async) S3 Event → EventBridge → Lambda
   → verify magic bytes (FFD8FF), read TRUE size + etag from the event
   → generate view + thumb with sharp, write to img/…
   → set state:"committed", write authoritative bytes/sha256/width/height
   → apply Object Lock; remove the state=pending tag
```

**The S3 event is the source of truth. The client callback is a UI affordance.**

### 3.2 Idempotency is mandatory

AWS: S3 notifications are *"designed to be delivered **at least once**"* and *"typically delivered in seconds but can sometimes take a minute or longer."* So the Lambda **must** upsert on key, and the UI **must not block** on `committed`.

Prefer **EventBridge over direct→Lambda**: retries + DLQ, filtering, replay, and fan-out to the thumbnailer + OCR + audit without touching bucket config.

### 3.3 Reconciliation

A sweeper flips `claimed`-with-no-event rows to `failed` after 15 minutes and alerts. `pending` rows older than 24 h are deleted.

### 3.4 Failure modes

| Mode                                             | Consequence                       | Mitigation                                                                            |
| ------------------------------------------------ | --------------------------------- | ------------------------------------------------------------------------------------- |
| **Orphaned object** (upload OK, app dies)        | billed forever, no DB row         | Upload to `u/` tagged `state=pending`; Lambda removes the tag on commit; lifecycle expires tagged-pending at 7 days |
| **Ghost row** (presign issued, never used)       | row with no object                | Sweeper deletes `pending` >24 h                                                        |
| **Lying client**                                 | order looks complete, no slip     | Only the S3 event sets `committed`; size/etag derived server-side                      |
| **Oversize / wrong type**                        | silent failure in the UI          | S3 rejects at the edge — **parse S3's XML error in RN** (`EntityTooLarge`, `Policy Condition failed`) and show a real message |
| **Type spoofing** (JPEG header, SVG body)        | stored XSS in `dip-web`           | Magic-byte sniff in the Lambda; quarantine mismatches; serve from a **cookie-less domain** with strict CSP |
| **Duplicate on retry**                           | 2 objects, 2 rows                 | Key derives from the server-issued ULID → retry overwrites the same key. Idempotent by construction |
| **Replay of a leaked policy**                    | overwrite within TTL              | 5-min expiry + `s3:signatureAge` + versioning + Object Lock post-commit                |

---

## 4. D3 — build the variants, don't buy a service

### 4.1 The comparison at 300k images/month, month 12

| Option                                   | Month 1 | Month 12    | Scales with          |
| ---------------------------------------- | ------- | ----------- | -------------------- |
| **S3 + CloudFront, pre-generated**       | ~$11    | **$53**     | storage only         |
| R2 + Cloudflare, pre-generated           | ~$4     | $32         | storage only         |
| Cloudflare Images (stored + delivered)   | $21     | $186        | **stored count**     |
| ImageKit Pro + S3 origin                 | ~$94    | ~$133       | bandwidth (flat)     |
| Cloudflare Images (transformations)      | ~$450   | **~$1,800** | archive re-reads     |
| Cloudinary                               | ~$517   | ~$1,407     | everything           |
| AWS Dynamic Image Transformation         | $290    | $290        | over-provisioned     |

Two traps worth naming:

- **Cloudflare Images "Transformations" re-bills every calendar month.** Unique transformations reset monthly, so cost tracks *archive size*, not new uploads. Over a 7-year GST retention that's ruinous — at year 6 (~21.6M images) the stored meter alone is ~$1,080/mo vs S3's ~$260/mo.
- **Cloudinary publishes no overage rate for fixed tiers.** They soft-limit then suspend. Your transformation count alone (900 credits/mo) exceeds their largest published plan (600 credits, Advanced $249) — that forces an Enterprise negotiation.

### 4.2 The actual argument

It isn't primarily cost. **You have no transformation problem to solve.** These services sell dynamic, arbitrary-parameter, on-the-fly transformation. You control the client, you compress on-device, you need exactly three fixed sizes, and images never change after upload. You'd pay a recurring premium for elasticity you will never exercise, against an archive that must legally grow for ~7 years.

**Effort delta: ~1 day, once.** Buy ≈ 0.5–1 day (point a URL prefix at the bucket, enable signed URLs). Build ≈ 1 day for ~30 lines of `sharp` inside the Lambda you are *already writing* for the S3 event, plus 0.5 day for CloudFront + OAC + cache policy + key group.

**Legitimate shortcut while small:** at today's ~5k images/month you'd deliver ~1.5 GB/month, inside ImageKit's free tier (**20 GB bandwidth/mo, 3 GB storage, 2 users** — current published limits). Using it while small is fine **only if you follow Phase 4 §3 and store keys, not URLs** — then migrating off is a config change, not a data migration. ⚠️ ImageKit publishes **no INR pricing page** in 2026 despite being an Indian company; confirm GST invoicing with their sales team.

**What would flip this to buy:** user-driven transformations — crop/rotate in the web admin, arbitrary print sizes, PDF composition, background removal. Then buy **ImageKit, not Cloudinary**: it's the only vendor whose meter (output bandwidth) matches actual consumption rather than transformation count, and it has an `ap-south-1` processing region. ⚠️ Caveat for RN: ImageKit's `f-auto` depends on the `Accept` header, which React Native's image loader often doesn't send usefully; UA-based selection is Enterprise-only. You'd hard-code `f-webp`, eroding part of the value.

**Skip entirely:** AWS Dynamic Image Transformation ($290/mo floor for a 1.2M-request workload), Thumbor (7.7.0 Oct 2023 → 7.8.0 May 2026 — a 2.5-year gap), and Next.js image optimisation (`dip-web` is Vite + React, not Next — it does nothing here).

### 4.3 The variant table

| Variant | Long edge  | Format               | Quality | Colour    | Expected size | Purpose                                |
| ------- | ---------- | -------------------- | ------- | --------- | ------------- | -------------------------------------- |
| `thumb` | **320 px** | WebP                 | q65     | grayscale | **8–20 KB**   | list rows, order cards                 |
| `view`  | **1280 px**| WebP                 | q75     | grayscale | **90–160 KB** | full-screen phone view, share sheet    |
| `orig`  | **2048 px**| **JPEG 4:2:0**       | q82     | grayscale | **250–420 KB**| **OCR input**, legal retention, zoom   |

Total per image: **~485 KB across 3 objects** — the figure used in every cost calculation above.

**JPEG for the archival is not a preference.** Textract accepts JPEG/PNG/PDF/TIFF only — **not WebP, not AVIF**. If you ever want AWS OCR, the archival variant must be JPEG. WebP is fine for the two delivery variants, which never go to OCR.

**Grayscale** drops chroma planes for ~20–25% fewer bytes with zero OCR impact — receipts are monochrome. **Do not binarize**: it's lossy and irreversible, applied ahead of models trained on natural photographs. (Honest caveat: no controlled benchmark of raw-vs-binarized through a cloud OCR API appears to exist, and two peer-reviewed papers contradict each other on whether Tesseract even benefits. The argument is *asymmetric risk*, not measured loss. Don't tell the team there's a benchmark behind it.)

Set `sharp`'s `limitInputPixels` in the Lambda as a decompression-bomb guard.

---

## 5. The API surface

Following the local conventions exactly: routes declare bare handlers; controllers are `asyncHandler`-wrapped and call services with a single named-arg object; services throw `ErrorResponse`.

```js
// api_v3/routes/collections/so_msts.js — insert before :34

router.post("/:id/slips/presign",        PresignSlip);
router.post("/:id/slips/:slipId/commit", CommitSlip);
router.get ("/:id/slips",                ListSlips);
router.delete("/:id/slips/:slipId",      DeleteSlip);
```

```js
// api_v3/controllers/collections/so_msts.js — append after :68

exports.PresignSlip = asyncHandler(async (req, res) => {
  const data = await presignSlip({
    id: req.params.id,
    body: req.body,
    headers: req.headers,          // ← token lives here; see §5.1
  });
  res.status(201).json({ success: true, data });
});
```

⚠️ **Note the local error-code convention:** `api_v3/services/so_msts.js` throws **404** for validation failures (`:30` "must have at least one product", `:186` "Can't Edit Invoiced Sales Orders", `:224`, `:830`). Only `App/email.js:25` uses 400. Follow the local convention or break it deliberately and consistently — don't do both.

**Rate-limit these routes.** Collection routes are currently unlimited; the global limiter at `dzzlo_oms.js:88-95` is **commented out**. The two existing per-route limiters are the pattern: `api_v3/routes/auth/index.js:7-16` (15/3 min) and `routes/open_apis/contact_email.js:4-9` (100/15 min). An upload-presign endpoint needs one.

### 5.1 🔴 Authorization — the thing this phase must get right

**Every new slip endpoint must derive `dealer_id` from the token and verify it against `so.dealer_id`.**

The reason is a pre-existing hole, not a new one. Across `api_v3/routes/`, `protect`/`authorize`/`scope` (`api_v3/auth.js:61,78,93`) are imported and **never applied** — every call site is commented out. `req.user` is never populated on collection routes. `api_v3/services/so_msts.js` never reads the token; `dealer_id` comes from the client body (`:299-301`, `:490-491`, `:680-681`, `:42`).

`check_user_company_status()` (`helpers/middlewares.js:65-110`, mounted `api_v/api3.js:33`) only asserts *the caller belongs to the company in `x-co-id`* — it never cross-checks that against the `dealer_id` in the payload, and never looks at `so_msts`.

**Net effect today: with a valid JWT and the shared `X_API_KEY_3`, dealer A can read dealer B's sales orders by passing B's `dealer_id`.**

Do not extend that pattern to a write endpoint that mints S3 credentials. The local precedent for doing it right is `api_v3/controllers/collections/veh_trns.js:39-47`, which derives `cust_id` from `getUserFromToken(req.headers)`.

```js
// api_v3/services/duSlips/index.js
const { getUserFromToken } = require("../../auth");

async function assertSlipAccess({ soId, headers }) {
  const user = await getUserFromToken(headers);
  if (!user) throw new ErrorResponse("Not authorized", 401);

  const so = await SalesOrder.findById(soId).select("_id dealer_id inv_id gst_inv_id du_slips").lean();
  if (!so) throw new ErrorResponse(`Sales Order not found with id ${soId}`, 404);

  // dealer_id from the TOKEN, never from the body
  if (String(so.dealer_id) !== String(user.co_id)) {
    throw new ErrorResponse("Not authorized for this Sales Order", 403);
  }
  return { user, so };
}
```

> **Scope note:** fixing the *general* `so_msts` authorization hole is out of scope here and deserves its own task. But it should be **written down as a known issue** rather than left implicit — recommend filing it separately and linking it from `docs/strategy/`.

### 5.2 Business rules enforced server-side

| Rule                         | Where                                                          |
| ---------------------------- | -------------------------------------------------------------- |
| ≤6 slips per SO              | `presignSlip` — count non-deleted `du_slips` before minting     |
| No attach/delete once invoiced | `presignSlip`, `deleteSlip` — `!!so.inv_id \|\| !!so.gst_inv_id` |
| Delete is soft               | set `deleted_at`/`deleted_by`; the S3 object stays (GST)         |
| `bytes` ≤ 1 MB               | checked at presign **and** enforced by the POST policy           |
| Role gate                    | `DPrimary`/`DAdmin` only                                         |

---

## 6. 🔴 Stop `du_slips` leaking into invoices

`api_v3/services/invs.js:659-665`:

```js
SalesOrder.find({ $or: [{ inv_id }, { gst_inv_id }, { cs_reimb_inv_id }] }).lean()
```

No `.select()`. The result is decorated (`:695-732`) and attached as `invoice.salesOrders` (`:732`). So a new `du_slips` array lands in **every invoice-detail response** and in the **puppeteer PDF template data**.

Fix: add an explicit projection at that call site, and **write the test first**.

```js
.select("-du_slips")
```

Also check `:1128-1131` (already projected — safe) and `helpers/advancedResults.js:60 getResults`, which honours a caller-supplied `select` (`api_v3/services/so_msts.js:363`, `:695`).

**Keep list projections lean** for a second reason: `legacy_credit_presenter()` (`helpers/middlewares.js:167-190`, mounted `api_v/api3.js:19`) does `JSON.parse(JSON.stringify(body))` over the **entire** response for clients ≤1.77 (`:183`). Fat arrays on every row in a paginated list get double-serialised for those clients.

---

## 7. Config

New env vars — add to **all four** files (`.env.example`, `.env.development`, `.env.testing`, `.env.production`):

```
S3_SLIPS_BUCKET=dzzlo-slips
S3_SLIPS_REGION=ap-south-1
S3_SLIPS_KMS_KEY_ARN=arn:aws:kms:ap-south-1:…:key/…
CDN_SLIPS_DOMAIN=cdn.dzzlo.in
CDN_SLIPS_KEYPAIR_ID=K…
CDN_SLIPS_PRIVATE_KEY_PATH=/etc/dzzlo/cf-signer.pem
```

Credentials: the existing pattern is static keys from env, client constructed **per call** — `helpers/sendEmail.js:14-25` uses `ACCESS_KEY`/`ACCESS_SECRET`/`ACCESS_REGION` (= `ap-south-1`), building a new `SESv2Client` inside the function each time. Reuse those credentials or add scoped ones; **do build a module-level singleton `S3Client`** rather than copying the per-call construction.

⚠️ `docs/README.md:41-54` is out of date — it omits `ACCESS_KEY`/`ACCESS_SECRET`/`ACCESS_REGION`, `X_API_KEY_3` and `ONESIGNAL_*`, and names `DATABASE` where the code reads `DATABASE_URI`. **`.env.example` is the accurate list.** Update `docs/README.md` while you're here.

---

## 8. Definition of done

- [ ] Bucket + KMS key + lifecycle rules + Object Lock created in `ap-south-1`
- [ ] CloudFront distribution with OAC, `CachingOptimized` policy, key group for signing, on a **cookie-less** domain
- [ ] CloudWatch alarm on `BytesDownloaded` at 800 GB/month (§1.2)
- [ ] Confirmed the distribution is on **pay-as-you-go**, not a flat-rate plan
- [ ] Post-upload Lambda: magic-byte check → 3 variants via `sharp` → Mongo upsert → Object Lock; idempotent on key
- [ ] EventBridge rule + DLQ
- [ ] Four `api_v3` endpoints, rate-limited, **token-derived `dealer_id`** (§5.1)
- [ ] Orphan sweeper (pending >24 h, claimed >15 min)
- [ ] `.select("-du_slips")` at `invs.js:659-665` **with a test pinning it** (§6)
- [ ] Env vars in all four `.env` files + `.env.example`; `docs/README.md` refreshed
- [ ] Tests per Phase 7 §2 — including presign-then-lie, oversize, wrong-content-type, cross-dealer, and post-invoice rejection
