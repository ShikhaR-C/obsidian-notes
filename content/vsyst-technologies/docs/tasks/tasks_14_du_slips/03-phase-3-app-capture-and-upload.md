# Phase 3 — App capture & upload

**Blocked by:** Phase 2 (endpoints must exist).
**Runs alongside:** Phase 5 — the manifest shape and consent flow constrain the library choice, so read that doc before installing anything.

Target app: **RN 0.84.1 / React 19.2.3, New Architecture ON both platforms** (`android/gradle.properties:35 newArchEnabled=true`, `ios/…/Info.plist:61-62 RCTNewArchEnabled=true`). Android `minSdk 24 / compileSdk 36 / targetSdk 36`, `versionName 1.78` / `versionCode 103`. iOS `MARKETING_VERSION 1.78` / build 9, deployment target 15.1.

---

## 1. Starting position

**There is no working native media capability in the app.** Three files reference such libraries — `src/components/ImagePicker/index.js:12,14` (`react-native-image-picker`, `react-native-permissions`) and `src/components/Download/Invoice.js:1` (`rn-fetch-blob`) — and **all three libraries are absent from both `package.json` and `node_modules`**. Grep confirms nothing imports those files. They are dead code that would fail Metro resolution if ever wired up. Treat them as reference sketches, not a foundation — note in particular that the `FormData` snippet at `ImagePicker/index.js:148-181` **omits the auth header entirely**.

Also absent: any share code (`Share` appears only inside commented-out blocks in `src/components/Download/invoiceHTML/ShowInvoice.js:215,284-350`), any download code, and any image caching library. The one live remote-image component is `src/components/ImagePicker/Picture.js` — worth reusing for thumbnails, but note `:25` builds its URL from `API_URL`, **not** `API_URL_V`.

`react-native-html-to-pdf@1.3.0` is installed but **never actually invoked in live code** — the only live import (`src/screens/Common/Reports/TcsTds/Render/index.js:5`) never calls `.convert()`. The real document strategy is HTML inside `react-native-webview`. It is also unmaintained; audit whether it drags `WRITE_EXTERNAL_STORAGE` into the merged manifest at API 36 before it collides with this work.

---

## 2. D5 — capture: system document scanner, not a custom native module

### 2.1 The verdict on building our own

**Don't.** A DU slip is a *document*, and both platforms already ship a first-party document scanner that does edge detection, perspective correction and glare handling for free:

- **Android** — ML Kit Document Scanner (delivered via Google Play services)
- **iOS** — VisionKit `VNDocumentCameraViewController`

Writing a CameraX + AVFoundation module means owning camera API churn, device fragmentation, and Samsung/Xiaomi/Oppo quirks across your entire Indian install base — permanently — to reimplement what the OS gives you. The capability that *would* justify a custom module (document edge detection, auto-capture, glare handling) is precisely what these already provide.

⚠️ **Verify before committing:** whether a single maintained RN wrapper exposes **both** the Android ML Kit Document Scanner and iOS VisionKit, with New-Architecture support on RN 0.84. Candidates to audit: `react-native-document-scanner-plugin`, `@react-native-ml-kit/*`. Check npm weekly downloads, last publish date, open-issue count and Fabric/TurboModule status for each. **If no wrapper is healthy, fall back to §2.2 and revisit later — do not write the module.**

### 2.2 Fallback: `react-native-image-picker`

It is the natural fit for the compliance design (Phase 5): `launchImageLibrary` uses the **Android Photo Picker** and **iOS PHPickerViewController**; `launchCamera` uses `ACTION_IMAGE_CAPTURE`. Both mean **zero Android runtime permissions**.

Two requirements from its README that apply here:
- `androidx.activity:activity:1.9.+` in `android/app/build.gradle` — **mandatory**, because `minSdk 24 < 30` means the Photo Picker backport must be wired (see Phase 5 §1).
- `WRITE_EXTERNAL_STORAGE` manually for `saveToPhotos` on API ≤28 — **the library does not handle it.** Avoid needing it (Phase 5 §1.6).

🔴 **The CAMERA trap.** `ACTION_IMAGE_CAPTURE` does **not** require the `CAMERA` permission. But **if `CAMERA` appears anywhere in the merged manifest it becomes mandatory at runtime** and the intent throws `SecurityException` until granted. Declaring it also implicitly adds `android.hardware.camera` + `.autofocus` as *required* features, and Play then filters your app off devices lacking them. So: never declare it, and audit the **merged** manifest, not just yours.

`react-native-vision-camera` is only worth its build complexity if you want live in-frame edge detection — and if you take it, `CAMERA` becomes unavoidable. Only reach for it if the document-scanner wrappers in §2.1 all turn out to be unhealthy.

---

## 3. D7 — upload transport

### 3.1 Use `XMLHttpRequest` with a `{uri}` body

```js
const xhr = new XMLHttpRequest();
xhr.open("POST", presignedUrl);          // presigned POST → FormData, see §3.2
xhr.upload.onprogress = e => onProgress(e.loaded / e.total);
xhr.timeout = 60_000;
xhr.send(formData);
```

For a raw binary PUT the body form is:
```js
xhr.setRequestHeader("Content-Type", "image/jpeg");   // ← mandatory, see below
xhr.send({ uri: filePath });                          // ← NOT a Blob
```

**Why `{uri}` and not a `Blob`.** RN's `convertRequestBody.js` declares `{uri: string, ...}` as a first-class supported body type, and the platforms treat the two very differently:

| Platform | `{uri}` body | `Blob` body |
| --- | --- | --- |
| **Android** | `NetworkingModule.kt` → `RequestBodyUtil.getFileInputStream()` → `Okio.source(inputStream)` + `sink.writeAll(source)` — **true streaming, nothing buffered** | `BlobModule.kt` holds a `HashMap<String, ByteArray>`; `RequestBody.create(mediaType, bytes)` — **entire file in native heap** |
| **iOS** | nested `RCTNetworkTask` reads the file to `NSData`, then `request.HTTPBody = …` — buffers | buffers |

At 300–400 KB neither hurts, but `{uri}` is strictly better on Android and never worse.

**Why XHR and not `fetch`.** `fetch` in RN gives **no upload progress events at all**. `XMLHttpRequest.upload.onprogress` is the only way to show a progress bar.

### 3.2 Three traps, all verified

1. **Always set `Content-Type` explicitly.** RN's `fetch` is the unmodified `whatwg-fetch` 3.6.20 polyfill: given an unrecognised object it stringifies a local copy to `"[object Object]"` and defaults the header to `text/plain;charset=UTF-8` — **while still sending the correct `{uri}` object as the body**. Against a presigned S3 request where content-type is part of the signature, that is a **silent 403** with a correct-looking body.
2. **Copy picker output to a real file path first.** Android's `RequestBodyUtil.contentLength()` returns `inputStream.available()` — exact for a real `FileInputStream`, only an *estimate* for some `content://` provider streams. Under-reporting means Content-Length shorter than the bytes written → OkHttp `ProtocolException` or S3 `EntityTooLarge`. **This is the mechanism behind "EntityTooLarge on a 300 KB file."** Never upload a `content://` URI directly.
3. **Do not adopt `react-native-blob-util`.** Open bridgeless crash [#479](https://github.com/RonRadtke/react-native-blob-util/issues/479) (opened 2026-07-21, still open at time of writing): it constructs `NativeEventEmitter` at *module scope*, before the TurboModule registers, crashing on New-Arch cold start on iOS. Affects 0.24.10 and master. With the `{uri}` finding above there's little reason to want it anyway.

**Parse S3's XML error body.** A rejected upload returns `EntityTooLarge` or `Policy Condition failed` as XML, not JSON. Without parsing it users see a silent failure.

### 3.3 The shared RTK Query baseQuery is unusable for uploads

`src/store/apis/createApi.js` builds `fetchBaseQuery` (`:21`) → `baseQueryWithPerf` (`:63`) → `retry(…, {maxRetries: 2})` (`:95`). Three blockers:

- **`timeout: 10000` (`:47`)** is hard-coded and global. A 400 KB upload over EDGE will `TIMEOUT_ERROR`.
- **`retry` at `:95-111`** re-sends the full body on 5xx/network errors — 3× bandwidth on exactly the connections that can least afford it.
- **`responseHandler` (`:48-55`)** assumes JSON-or-text; no binary path.

Uploads go **direct to S3** anyway (Phase 2 D2), so they bypass this entirely — use raw XHR. The RTK Query layer only carries the small JSON calls (`presign`, `commit`, `list`, `delete`), for which the shared baseQuery is fine.

**Add the tag types.** `createApi.js:117-127` lists nine `tagTypes` and **`so_msts` is not among them** — `src/store/apis/dzzlooms/so_msts.js` has no `providesTags`/`invalidatesTags` anywhere and relies on manual `refetch`/`isFocused` (`NewSalesOrder/index.js:364-368`). Add `'so_msts'` and `'du_slips'`.

Structural template for the whole feature: **`src/screens/Dealer/Payments/BSheets/AttachInvs.js`** (850 lines) plus its endpoint `voc_msts.js:169-179 attachInvoices` — it is the existing "attach-N-things-to-a-record" bottom sheet, with correct tag invalidation.

---

## 4. Image processing on device

### 4.1 Capture high, downscale in software

**Do not ask the camera for ~1600 px.** Capture at full/high resolution and let the resizer downscale. The reason is specific to your document type:

On dot-matrix print, resolving *too much* detail fragments glyphs — as one Tesseract maintainer put it, *"as you scan these prints at higher resolutions those otherwise indistinct individual dots become isolated… and begin to appear as individual objects by the OCR engine."* A dot-matrix glyph is only ~7 dots tall, so **no capture resolution avoids this**. The fix is a *filter* choice, not a resolution choice: **an area/box or Lanczos downscale low-passes the dot grid and marries the dots back into strokes for free.** Nearest-neighbour or naive bilinear at large scale factors aliases it.

### 4.2 Resizer

**`@bam.tech/react-native-image-resizer`** — and it does the right thing. On Android it runs a correct two-stage pipeline: `calculateInSampleSize()` picks the largest power-of-2 `inSampleSize` for the decode (an area-averaging subsample inside `BitmapFactory`), landing within 2× of target, then `Bitmap.createScaledBitmap(image, w, h, true)` — the `true` is bilinear — for the residual. Bilinear at ≤2× is exactly where it doesn't alias. iOS uses `UIGraphicsBeginImageContextWithOptions` + `drawInRect:` (CoreGraphics default interpolation) — acceptable; eyeball iOS output for crunchiness.

⚠️ Verify its New-Architecture status on RN 0.84 before installing.

### 4.3 Output target

Produce **one** artefact for upload: **2048 px long edge, JPEG q82, grayscale, EXIF stripped (GPS especially)** → ~250–420 KB. The Lambda derives `view` and `thumb` server-side (Phase 2 §4.3) — don't upload three files from a phone on a bad link.

Apply the **≥1,000 px across the receipt's printed width** rule via the crop bounding box; escalate to 2560 px when the box exceeds ~1:3 aspect. ⚠️ **These numbers rest on the unmeasured cap-height assumption in Phase 1 §4 — measure a real slip first.**

### 4.4 🔴 Build the glare/blur gate — this is the highest-leverage thing in the phase

Measured on real photographs, specular-highlight removal moved end-to-end text recall **64.85% → 78.50%** (+13.65 points). **No server-side processing recovers clipped pixels.** Glossy thermal paper under a pump canopy is the worst case for this, and it happens at capture or not at all.

```
Before upload, on-device:
  1. Laplacian variance  → blur score        (cheap, well-understood)
  2. Clipped-pixel ratio → glare score       (% of pixels at/near 255 in a
                                              contiguous region over the slip)
  3. Optional: on-device OCR line count      (see Phase 6 §2)
  → fail any → "Slip is blurry / has glare. Move into shade and retake."
```

Google's own ML Kit guidance endorses the pattern: *"If you aren't getting acceptable results, try asking the user to recapture the image."* Rejecting a bad frame before it leaves the phone saves a round trip, saves the OCR call, and — most importantly — avoids a plausible-but-wrong number entering the system.

---

## 5. Offline queue

The app has `@react-native-community/netinfo` ^12.0.1 in three components (`src/components/Network/index.js`, `NoNetwork/index.js`, `NoNetwork/Undraw.js`) — **all purely presentational. There is no queue, no retry-on-reconnect, no persistence, no offline mutation cache.** The only retry anywhere is RTK Query's in-memory `retry()` at `createApi.js:95-111`, which dies with the process.

⚠️ Also note a real bug to avoid copying: `src/components/Network/index.js:19` discards the `addEventListener` unsubscribe function; cleanup only flips an `isMounted` flag (`:25-27`). Listener leak per mount.

### 5.1 Verdict: hand-roll it

`redux-offline` was **archived 2026-04-01**. RTK Query has no offline mutation queue — issue [#1610](https://github.com/reduxjs/redux-toolkit/issues/1610) was closed in 2023 with nothing shipped, and RTK 3.0 has no persistence API announced. TanStack Query v5 is the only mainstream data layer with a real one (`networkMode:'offlineFirst'`, paused mutations, `resumePausedMutations()`), which is worth *knowing* but not worth migrating for.

```
Queue item: { localId, soId, filePath, sha256, bytes, w, h, capturedAt,
              attempts, state: "queued"|"presigned"|"uploading"|"done"|"failed" }
```

- Persist to **AsyncStorage** (already a dep) or **`react-native-mmkv`** (better long-term). ⚠️ AsyncStorage's Android SQLite backend has a **6 MB default cap** (raisable via the `AsyncStorage_db_size_in_MB` Gradle property) — fine for job metadata, **fatal if anyone ever base64s an image into it**. Store the file path, never the bytes.
- Files live in the app cache directory; the queue holds paths.
- Drain on: app foreground, successful capture, and a NetInfo transition.
- 🔴 **Gate the drain on `isInternetReachable !== false`, not `isConnected`.** Captive-portal Wi-Fi at a pump reports *connected* with no data path, and this is the single largest source of "mystery" upload failures in this environment.
- Exponential backoff with jitter, cap ~5 attempts, then surface a manual "Retry" in the UI.

If you need Redux persistence generally, prefer **`redux-remember`** over redux-persist (the latter is effectively unmaintained; the open RTK docs issue #5180 proposes redux-remember as the successor). Note `src/store/apis/index.js:20` sets `serializableCheck: false`, so non-serialisable upload descriptors in Redux won't trip anything.

### 5.2 Background upload — deliberately out of scope

One credible package exists — `@kesha-antonov/react-native-background-downloader` (uploads despite the name; omit `fieldName`/`parameters` and it sends a raw binary body with `setFixedLengthStreamingMode`, which is exactly a presigned PUT). Its iOS half is textbook `backgroundSessionConfigurationWithIdentifier:`. But its Android half is best-effort in-process, and the OS constraints are decisive:

- Apple: *"If the user terminates the app from the multitasking screen, the system cancels all of the session's background transfers."*
- Android 15 caps `dataSync` foreground services at **6 hours per 24 h** before `onTimeout()`.
- Android 16 subjects FGS-launched jobs to normal quotas.
- Xiaomi / Oppo / Vivo / Realme — most of your Indian install base — kill background work regardless of AOSP semantics.

**Keep uploads foreground + durable retry queue.** If telemetry later shows dealers backgrounding mid-upload, that package is the thing to add.

---

## 6. UI integration

### 6.1 Build EditSalesOrder first

`src/screens/Dealer/EditSalesOrder/index.js` already knows `sorder._id` (from `route.params.sorder`, `:83-84`), so uploads can fire immediately with no staging. It is strictly the simpler of the two flows — ship it, prove the pipeline, then do the create flow.

- **UI slot:** after the remarks `TextInput` block (ends `:702`), before `<OrdersList>` at `:705`.
- **Gate:** reuse `src/screens/Dealer/Orders/components/OneOrder.js:206` — `!!salesOrder.inv_id || !!salesOrder.gst_inv_id` → already alerts *"Sales Order already Invoiced."* Same predicate, same message.
- **Scope gate:** `userScope === 'DPrimary' || 'DAdmin'` (`OneOrder.js:209`).

### 6.2 Then NewSalesOrder — with one required change

`src/screens/Dealer/NewSalesOrder/index.js` currently **discards the created SO's `_id`**:

```js
// :325-336 — today
await add_so_msts({ … }).unwrap();
// :338  await updateCurr_User_Comp().unwrap();
// :341  navigation.goBack();
```

Capture it, then flush the staged photos before the refresh:

```js
const created = await add_so_msts({ … }).unwrap();
await flushStagedSlips(created.data._id);      // ← new
await updateCurr_User_Comp().unwrap();
navigation.goBack();
```

- **UI slot:** after the remarks block (ends `:593`), before `<OrdersList item={order} />` at `:596`.
- Photos captured pre-save are **staged locally** (queue item with `soId: null`) and bound to the real `_id` on success.
- The screen already lazy-renders bottom sheets at `:603-619` — an `AttachDuSlipsBottomSheet` drops in identically.
- ⚠️ Extend the `beforeRemove` guard at `:172-186` (`openedSheetsRef`) for the new sheet, **and** to warn about unsaved staged photos.

### 6.3 New files

```
src/screens/Dealer/_shared/DuSlips/
  DuSlipsRow.js            thumbnail strip + "Add slip" button (both screens)
  AttachDuSlipsBottomSheet.js   camera / gallery choice, guidance, quality gate
  useDuSlipUpload.js       queue binding, progress, retry
src/store/apis/dzzlooms/du_slips.js
src/helpers/DuSlips/{quality.js, resize.js, queue.js}
```

---

## 7. Config gotcha

`babel.config.js:6-15` runs `module:react-native-dotenv` with **`safe: true, allowUndefined: false`**. **Any new `@env` var missing from *any* of `.env.development` / `.env.testing` / `.env.production` / `.env.example` fails the bundle** — not at runtime, at build. Add new vars to all four in the same commit.

Also: `babel-plugin-optional-require` (`babel.config.js:23`) exists solely so `react-native-paper` can skip the un-installed `react-native-vector-icons` (hence the hand-rolled `src/components/SVG/RNVI/*` icon set). It is **not** a general conditional-native-module mechanism — don't plan around it.

iOS pods: `ios/Podfile:20-40` forces RNFirebase pods static (`$RNFirebaseAsStaticFramework = true`) with an explicit comment that a global `use_frameworks! :linkage => :static` **breaks worklets/reanimated on RN 0.84**. If a new pod pushes you toward frameworks, that's a hard stop — pick a different library.

---

## 8. Definition of done

- [ ] Document-scanner wrapper audited (§2.1) and a decision recorded — scanner or `react-native-image-picker` fallback
- [ ] Merged manifest verified to contain **no** `CAMERA` and **no** media permissions (`./gradlew :app:processReleaseManifest`, then read the merged output)
- [ ] `androidx.activity:activity:1.9.+` added (mandatory at `minSdk 24`)
- [ ] Capture → glare/blur gate → resize (2048 px, JPEG q82, grayscale, EXIF stripped) → queue
- [ ] Upload via XHR with a `{uri}` body, explicit `Content-Type`, progress, S3 XML error parsing
- [ ] Picker/camera output copied to a real file path before upload (§3.2 trap 2)
- [ ] Durable queue on AsyncStorage/MMKV; drain gated on `isInternetReachable !== false`
- [ ] `EditSalesOrder` flow working end-to-end (build first)
- [ ] `NewSalesOrder` staged flow, with `created.data._id` captured at `:325`
- [ ] `so_msts` + `du_slips` tagTypes added to `createApi.js:117-127`
- [ ] New `@env` vars present in all four `.env` files
- [ ] Tested on Android 9 / 11 / 13 / 14 / 16 — confirm the Photo Picker backport actually appears on 9/10
