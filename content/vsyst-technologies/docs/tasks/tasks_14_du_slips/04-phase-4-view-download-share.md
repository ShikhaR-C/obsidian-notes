# Phase 4 — Viewing, download & sharing

**Blocked by:** Phase 2 (web half) / Phase 3 (app half).
**Delivers:** slip thumbnails and a full-screen viewer in both clients, download + share of a slip, and — if approved — a public share link for an SO plus its slips.

---

## 1. D8 — the read path

```
RN <Image> / <img>  →  CloudFront (signed URL, 15-min TTL)
                    →  Origin Access Control
                    →  private S3 bucket (Block Public Access ON)
```

Served from a **separate cookie-less domain** (`cdn.dzzlo.in`, not `app.dzzlo.in`) — this is what contains the stored-XSS blast radius if a spoofed content-type ever slips past the magic-byte check.

### 1.1 Immutable, content-addressed keys

```
img/{dealerId}/{soId}/{sha256[0:16]}/{variant}.{ext}
```

Bytes at a key never change, so set at PUT time:

```
Cache-Control: public, max-age=31536000, immutable
```

Because keys are immutable you **never need CloudFront invalidations** (which cost $0.005/path beyond 1,000/month). A "changed" image is a new key.

### 1.2 The signed-URL vs CDN-caching conflict — and why it doesn't apply to you

This trips up most teams, and the answer is asymmetric:

- **S3 presigned GET URLs behind a CDN are a caching disaster.** The SigV4 params (`X-Amz-Signature`, `X-Amz-Date`, `X-Amz-Credential`…) are part of the URL, and Cloudflare's default cache key includes the full query string → every user and every re-sign is a distinct cache key → ~0% hit rate → you pay origin egress on every view. (Granular query-string cache-key control is Enterprise-only there.)
- **CloudFront signed URLs do not have this problem.** CloudFront *consumes* `Expires`/`Signature`/`Key-Pair-Id`/`Policy` itself for authorisation; the cache key is governed by the cache policy. The managed **`CachingOptimized`** policy (`658327ea-f89d-4fab-a63d-7e88639e58f6`) sets **"Query strings included in the cache key: None"**, max TTL 365 days. **Two viewers with different signatures hit the same cached object.**

**So with CloudFront there is no caching penalty for short TTLs.** Use 15 minutes and stop worrying about the trade-off. It only exists if you put S3 presigned URLs behind a CDN — which you should not do.

Signed *cookies* would let one signature cover a whole prefix, but **React Native's `<Image>` does not share a cookie jar with `fetch` reliably** on either platform. **Practical answer: batch-issue short-TTL signed URLs** — one API call returns signed URLs for the visible page. Simpler than fighting cookie jars, and CloudFront caches perfectly either way.

### 1.3 🔴 Store keys in Mongo, sign on read. Never store URLs.

Four reasons:
1. Signed URLs expire — a stored one is a time bomb.
2. The CDN hostname, key-pair ID and TTL are deployment config that **will** change (custom domain, key rotation, a future move to R2). A stored URL means rewriting millions of documents.
3. The raw key lets you re-derive the S3 ARN for lifecycle/Object Lock and re-point the CDN in one config change.
4. Signing is ~50 µs of ECDSA. It's free.

This is also what keeps the "use ImageKit's free tier while small" shortcut (Phase 2 §4.2) reversible — with keys stored, switching is a config change; with URLs stored, it's a data migration.

### 1.4 Thumbnail-first — the single biggest cost lever in this project

Delivered bytes at 3.6M images, 4 reads each:

| Read strategy               | Delivered/mo | CloudFront cost |
| --------------------------- | ------------ | --------------- |
| thumb-only (15 KB × 4)      | 206 GB       | **$0**          |
| **blended (recommended)**   | 858 GB       | **$0**          |
| view-first (120 KB × 4)     | 1,648 GB     | $68             |
| naive full-res (350 KB × 4) | 4,807 GB     | **$412**        |

The rule:
- **List / row views:** request `thumb` only (~15 KB). 20 rows = 300 KB. With `immutable`, the client cache never revalidates.
- **Full screen:** load `view` (1280 px, ~120 KB) for instant render.
- **`orig`:** only when the user pinch-zooms past ~1.5×, or for OCR, or on download.
- **Prefetch** `view` for the top 3 rows when a list renders.

---

## 2. App: viewer, download, share

### 2.1 Thumbnails

Extend `src/components/ImagePicker/Picture.js` (the app's only remote-image component) or write a sibling. ⚠️ Note `:25` builds `${API_URL + img}` — using `API_URL`, **not** `API_URL_V`. Slip URLs are absolute CDN URLs, so bypass that construction entirely.

**There is no image caching library in the app** — no `react-native-fast-image`, no `expo-image`. Bare `<Image>` uses Fresco's default disk cache on Android and `NSURLCache` on iOS, with no explicit control, priority, or placeholder. With `immutable` cache headers that's adequate for thumbnails. Revisit only if list scrolling shows flicker.

### 2.2 Full-screen viewer

The app's existing "document" pattern is HTML in a `WebView` (`src/screens/Common/_Invoice_/Render.js:82-97`, `src/components/VersionInfo/index.js:519-527`). **Don't use it here** — WebView is a poor image gallery. Use a Paper `Portal` + `Modal` (the pattern at `VersionInfo/index.js:544-596`) with a pinch-zoom image, loading `view` first and swapping to `orig` on zoom.

### 2.3 Download and share

Neither exists in the app today. **Prefer the share sheet over a gallery save** — it's better UX *and* it drops `WRITE_EXTERNAL_STORAGE` entirely, keeping the feature at zero Android runtime permissions (Phase 5 §1.6):

| API | Save-to-gallery mechanism | Permission |
| --- | --- | --- |
| 29+ | `MediaStore.Images` insert, `RELATIVE_PATH=Pictures/DZZLO`, `IS_PENDING` | none |
| 24–28 | direct write to a public dir | `WRITE_EXTERNAL_STORAGE` (runtime prompt) |
| **all** | write to app cache → `FileProvider` → `ACTION_SEND` / `ACTION_VIEW` → **user saves from the share sheet** | **none** ✅ |

Android specifics: `FLAG_GRANT_READ_URI_PERMISSION` on the `ACTION_SEND` intent; `setClipData(ClipData.newUri(...))` for multi-image shares; always a `content://` URI via `FileProvider.getUriForFile()` — a `file://` URI across a package boundary throws `FileUriExposedException` on API 24+.

iOS: `UIActivityViewController` via RN's built-in `Share`. `NSPhotoLibraryAddUsageDescription` is needed **only** if you ship an explicit "Save to Photos" button.

### 2.4 ⚠️ The PDF renderer will try to fetch slip images

`api_v3/services/invoice/htmlPdf/fileBuffer.js:51` calls `page.setContent(html, { waitUntil: "networkidle0" })`. That means **puppeteer actually fetches every remote `<img>` during render**. If slip images are ever added to an invoice or SO PDF template:

- a **public** URL works,
- a **presigned/signed** URL works only while unexpired,
- a **private** URL **hangs the render until the network-idle timeout, then produces a blank box**.

If slips go into a PDF, generate a long-TTL signed URL (or fetch the bytes server-side and inline as a data URI) **explicitly for that render**. Don't let the general 15-minute TTL leak into a PDF path.

---

## 3. dip-web

**`so_msts` has zero presence in `dip-web`.** No page, no endpoint, no tag type, no permission resource. The three existing references are all to a pre-aggregated scalar `item.uninvoicedSOs` used in credit math (`src/pages/superadmin/customers/CustDealers.js:186`, `src/pages/superadmin/dealers/DlrCusts.js:653`). Everything here is new.

Stack, for the record: **Vite 6 + React 18.3.1 + react-router-dom 7 (BrowserRouter) + RTK Query + react-bootstrap**, currently v1.4.7. No TypeScript, no test runner (`package.json:20` → `"test": "echo 'No test runner configured'"`), no CSP in-repo, no deploy config in-repo (most likely DigitalOcean App Platform, per the `catchall_document` note in `CLAUDE.md:39`).

### 3.1 What to build

| Item | Where | Pattern to copy |
| --- | --- | --- |
| Endpoints | `src/store/apis/dzzlooms/so_msts.js` (new) | `voc_msts.js:19-26` — absolute `/api/v3` URL overriding the DIP baseUrl |
| Tag type | `src/store/apis/createApi.js:55-72` | add `so_msts` |
| List page | `src/pages/transactions/…` | `DecanList/decanList.js` + `TransactionListLayout` (`shared.js:108-188`) + `useInfiniteScroll` |
| Mobile card | — | `src/components/Table/ResponsiveDecan/index.js` |
| Viewer | reuse `src/components/Modal/index.js` (focus trap `:35-50`, Escape `:21-32`) | via `src/utils/Hooks/useModal.js` |
| Thumbnail w/ fallback | `src/components/Navbar/Avatar.js:36-44` | `<Image>` + `onError` initials fallback — good prior art |
| Permission resource | `src/utils/permissions.js:11-23` | ⚠️ must mirror `dzzlo_oms_api/helpers/dipPermissions.js` |

There is **no file/blob/download primitive anywhere in `dip-web`** — no `FormData`, no `<input type="file">`, no `URL.createObjectURL`. Download is `<a download>` against a signed CDN URL; share is `navigator.share` with an `<a>` fallback.

**CSP:** none in-repo (`index.html` has no meta CSP, no helmet). Adding the CDN origin needs no repo change — **but confirm whether the host injects CSP externally**; if so, `img-src` must be updated there.

---

## 4. D9 — the public share link

> ### RECOMMENDATION: defer this to v2.
> It is the single largest compliance surface in the project and the only part that exposes **third-party** data — a DU slip typically names the *customer*: vehicle number, sometimes phone, sometimes address. The dealer consents to publishing; the customer never did. The core feature is complete and useful without it. If it ships, everything below is mandatory, not optional.

### 4.1 Server side

`dip-web` has **no public route pattern at all**: `src/App.js:363-419` is one `<Routes>` block gated on `isSignedIn` (`:274`), and signed-out visitors get exactly one route — `<Route path="/" element={<SignInPage />} />` (`:364-368`) — with **no `path="*"` fallback**, so any other URL renders blank. Two changes are needed: a route **outside** the auth gate, and an opt-out from the app shell (`Navbar`, `PullToRefresh`, `CompanyScrollHint`, `NoNetworkBanner` render around every route at `:349-360`).

On the API side, anything mounted **before** `api_key_v3()` (`api_v/api3.js:14`) is unauthenticated. Existing precedents: `/api/v3/contact` (`api_v/api3.js:9`, own rate limiter 100/15 min) and `/api/v3/auth` (`:11`, `authLimiter` 15/3 min). The closest structural precedent for a token-in-URL flow is password reset — `api_v3/controllers/auth/forgot_reset_pass.js:24-43` takes an opaque `:resettoken` path param and returns HTML via `res.send`.

⚠️ Note also `dzzlo_oms.js:100 app.use(express.static("public"))` — a `public/` directory would be served unauthenticated. It doesn't currently exist; don't accidentally create one.

RTK Query on the web side needs no change for this: `prepareHeaders` (`createApi.js:12-19`) attaches `x-api-key` always but `Authorization` only when `userData` exists — so a token-in-URL public endpoint works through the existing baseQuery.

### 4.2 Non-negotiables if it ships

- [ ] **≥128-bit CSPRNG token** (22-char base62 or UUIDv4). Not the order ID, not sequential, not an HMAC of the slip number.
- [ ] **Default TTL** 7–30 days, expiry shown in-app.
- [ ] **In-app revoke** that hard-404s immediately; auto-revoke on SO delete and on account delete.
- [ ] **Separately short-lived signed image URLs**, so an image URL scraped off the page dies independently of the page token.
- [ ] **`X-Robots-Tag: noindex, nofollow` on the page AND on every image response** — the header is the only method that works for non-HTML resources — plus `<meta name="robots" content="noindex">` on the page.
- [ ] 🔴 **Do NOT `Disallow` the path in `robots.txt`.** Google: *"For the `noindex` rule to be effective, the page or resource must not be blocked by a robots.txt file"* — a blocked crawler never sees the noindex and the URL can still surface. (`dip-web/public/robots.txt` is currently `Disallow:` i.e. allow-all — leave it.)
- [ ] `Referrer-Policy: no-referrer`; `Cache-Control: private, no-store` on the HTML.
- [ ] **Visible abuse/report contact** on the page — satisfies Apple guideline 1.2's "published contact information".
- [ ] **Access audit log** — link creation, each access, revocation.
- [ ] **Share-time confirmation dialog** naming exactly what is exposed: *"This creates a link anyone with the URL can open. It shows the order and its receipt images."* **That dialog is your Apple 5.1.2(i) permission.**

### 4.3 Is it a "sharing" disclosure in the Play data-safety form?

**No — but for a subtle reason worth recording.** Google excludes transfers "based on a specific action that you initiate, where you reasonably expect the data to be shared", and excludes service providers. More fundamentally, publishing on *your own* server isn't a transfer to a third party at all. So answer **Shared = No** for the link mechanism.

**But it is a mandatory privacy-policy disclosure** under Play's User Data policy (*"comprehensively disclose how your app… shares user data"*) and Apple 5.1.1(i). See Phase 5 §5.

---

## 5. Definition of done

- [ ] CloudFront signed-URL issuance endpoint, batch-capable, 15-min TTL
- [ ] `CachingOptimized` cache policy confirmed on the distribution (query strings **not** in the cache key)
- [ ] App: thumbnail strip on both SO screens; full-screen viewer with zoom; `view` → `orig` escalation
- [ ] App: share sheet working on both platforms; no new Android permission in the merged manifest
- [ ] Web: `so_msts` endpoints + tag type + list surface + slip viewer; permission resource mirrored in `dipPermissions.js`
- [ ] Web: confirmed whether the host injects CSP; if so, `img-src` updated for the CDN origin
- [ ] `waitUntil:"networkidle0"` implication (§2.4) documented wherever a slip image could enter a PDF template
- [ ] **Share link: explicit go/no-go recorded.** If go, every box in §4.2 ticked.
