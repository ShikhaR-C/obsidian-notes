# Phase 4 — Images and Scanning: Capture, Pick, Read, Upload

> Level: Intermediate → Advanced | Time: ~1.5 h to read; 3–5 weeks to build §2–§7 on both platforms _(est.)_ | Outcome: a dealer scans a DU slip or cheque, photographs a meter, or scans the IRN QR on a GST e-invoice; photos are picked without a permission prompt, shrunk and stripped, and uploaded in a way that survives a locked phone — `NativeDocScanner` and `NativeUpload` built test-first, VisionCamera only where a live camera is needed.

---

## 1. The One Idea

A photo in a credit business is **evidence**, and evidence is what gets a bill paid. The reviews say so (Play, newest 1,000 per app, fetched 2026-09-29):

- Khatabook 1★ (2026-09-05, Hindi, paraphrased by the researcher): photos uploaded to a customer's ledger later went blank, "so the customer didn't pay me because they asked for the photo of the goods".
- OkCredit 5★ (2026-09-11) praises "Add amount with Bill image facility".
- A pump app, SCUBE, sells "Credit Customer Slip Entry With Vehicle, MPD, Driver Photo"; Repos, a doorstep-diesel app, promises "Verified Order Tracking … instant delivery confirmations".
- The product research ranks "camera or document-scan capture of credit / DU slips, meter and dip readings, cheques" 5th of 15 features.

| DZZLO use case | Who | Capture | Status |
|---|---|---|---|
| DU slip (the dispensing unit's printed delivery slip) on a sales order | dealer staff | document scan | spec'd in the DU-slips spec (tasks_14, 2026-07-29) — not started |
| Meter / totaliser reading | forecourt staff | photo or scan | proposal |
| Cheque on a payment | dealer | document scan | proposal |
| IRN QR on a supplier's GST e-invoice | dealer (B2B) | QR scan | proposal; no demand evidence found (rank 12) |

**Where the app starts** — `release/v1_79`, audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30):

- No camera, photo, picker or upload library in `package.json`; `Info.plist` has **no** camera or photo purpose strings and the iOS project has no `.lproj` folders.
- A parked `src/components/ImagePicker/index.js` — dead code for profile and company avatars — imports two packages that are not installed (`:12,14`), asks for three permissions up front including `READ_EXTERNAL_STORAGE` and `WRITE_EXTERNAL_STORAGE` (`:85-87`), compresses at `quality: 0.001` (`:97`) and saves every photo to the camera roll (`:101`). Its two packages are kept as virtual mocks in `jest.setup.js:245-256` — "confirmed team decision 2026-07-05: keep them stubbed, do not install". Installing either one **reverses that recorded decision**: the user's word first, and the dead component and both mocks go in the same PR ([[02-phase-2-dependency-diet]]).
- The API has no upload code at all — no `multer`, `busboy`, `@aws-sdk/client-s3` or presign (`dzzlo_oms_api` HEAD `9690be9`, 2026-09-29).

The [[vsyst-technologies/docs/tasks/tasks_14_du_slips/00-overview|DU-slips spec]] already decided three things this phase must respect: **D5** — the system document scanner, and "**Do not write a native module**" unless no maintained wrapper is healthy; **D6** — zero Android permissions; **D7** — foreground uploads with `XMLHttpRequest`. Where this course's newer research (2026-09-29) re-opens one of them, the section says so and the user decides.

| Capability | Platform API (since) | Library (version, date) | New Arch | Verdict |
|---|---|---|---|---|
| Capture a photo | Android `ACTION_IMAGE_CAPTURE`; iOS camera (levels not captured) | react-native-vision-camera 5.2.3 (2026-08-20) | Nitro, new-arch-only | USE only for a live in-app camera (§2) |
| Scan a document | `VNDocumentCameraViewController` (13.0); ML Kit Document Scanner (Play services) | react-native-document-scanner-plugin 2.0.4 (2026-01-02) | ⚠️ contested | USE if the audit passes, else BUILD `NativeDocScanner` (§3) |
| Pick photos | `PHPickerViewController` (14.0); Photo Picker (13+, backported) | react-native-image-picker 8.2.1 (2025-05-04) | TurboModule | USE, with the user's word (§4) |
| Compress, strip EXIF | re-encode on the phone | @bam.tech/react-native-image-resizer 3.0.11 (2024-11-25) | TurboModule | USE (§5) |
| Store | app sandbox | — | — | BUILD — a JS queue (§5) |
| Upload in the background | `URLSession` background (8.0); WorkManager | react-native-background-upload 6.6.0 (2022-10-07) | ❌ dead | BUILD `NativeUpload`, later (§6) |
| Download | Photos add-only; `DownloadManager` (API 9 believed, unconfirmed) | @kesha-antonov/react-native-background-downloader 4.6.3 (2026-09-15) | TurboModule | share-sheet save first (§7) |
| OCR | Vision (13.0 / 26.0); ML Kit Text Recognition v2 | @react-native-ml-kit/text-recognition 2.0.0 (2025-09-01) | ❌ | SKIP now, WRAP later (§8) |
| QR | VisionCamera barcode package; Google code scanner (API 23+); `DataScannerViewController` (16.0, A12+) | react-native-vision-camera-barcode-scanner 5.2.3 (2026-08-20) | Nitro | USE, or the no-permission route (§2) |

## 2. Capture and QR — react-native-vision-camera 5.2.3

### 2.1 Decide first: does DZZLO need an in-app camera?

VisionCamera v5 (5.2.3, 2026-08-20) is a full rewrite on **Nitro Modules** — new-architecture-only, with `react-native-nitro-modules` (0.37.1, 2026-08-27) and `react-native-nitro-image` as peers; treat it "as a new API, not an incremental upgrade" (secondary source). Barcodes come from a second package, `react-native-vision-camera-barcode-scanner` 5.2.3 ("powered by ML Kit"), which provides `useCodeScanner` and a `<CodeScanner />` view.

The price on Android is the **CAMERA trap** ([[vsyst-technologies/docs/tasks/tasks_14_du_slips/05-phase-5-store-compliance|DU-slips spec, Phase 5 §1.3]]): once `CAMERA` appears anywhere in the merged manifest, the system camera intent throws `SecurityException` until the permission is granted, and the implied `android.hardware.camera` features filter devices off Play unless marked `required="false"`. That ends D6.

| Route | Android | iOS | Use it for |
|---|---|---|---|
| **(a) VisionCamera** | `CAMERA` runtime permission + `uses-feature required="false"` | `NSCameraUsageDescription` | a live viewfinder: framing guides, continuous QR, custom UI |
| **(b) System UIs** | **no permission**: the ML Kit scanner for slips (§3), the Google code scanner (`GmsBarcodeScanning`, API 23+, its UI runs inside Play services) for a QR, the camera intent for a plain photo | `NSCameraUsageDescription` for any camera use; `VNDocumentCameraViewController`; `DataScannerViewController` (16.0, A12 Bionic or later) | slips, cheques, one-off QR scans |

**Recommendation: (b)** for every use case in §1, which keeps D6. Take (a) when a written product need asks for a live viewfinder. The rest of this section is route (a), step by step.

### 2.2 Install

```bash
cd /Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app
npm view react-native-vision-camera@5.2.3 peerDependencies   # read the Nitro peer ranges first
yarn add react-native-vision-camera@5.2.3 react-native-vision-camera-barcode-scanner@5.2.3 react-native-nitro-modules react-native-nitro-image
(cd ios && bundle exec pod install)
```

Two checks before any code. `ios/Podfile:20-23` warns that a global `use_frameworks! :linkage => :static` "breaks react-native-worklets / react-native-reanimated on RN 0.84" — a pod that demands frameworks is a hard stop. And every new `.so` must be 16 KB-aligned (`zipalign -c -P 16`, or `llvm-objdump -p` showing `align 2**14`) before Play enforces it on **2027-02-01** (Google's page; older guidance said Nov 2025 or May 2026).

### 2.3 Permissions and purpose strings that pass review

One iOS key covers every camera use — App Review 2.5.14 (consent for the camera) and 5.1.1(ii) ("clearly and completely describe your use"):

```xml
<!-- ios/dzzlo_oms_app/Info.plist -->
<key>NSCameraUsageDescription</key>
<string>Take photos of delivery slips, meter readings and cheques to attach them to an order or payment, and scan the QR code on a GST e-invoice to check it.</string>
```

It extends the DU-slips spec's string ("Take photos of delivery receipts and invoices to attach them to a sales order.") to this phase's uses — never "to upload images". With no `.lproj` folders, the system prompt is English for everyone; the one-screen rationale shown **before** it carries the Hindi, from `useStrings`.

```xml
<!-- android/app/src/main/AndroidManifest.xml — route (a) only -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
<uses-feature android:name="android.hardware.camera.any" android:required="false" />
<uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />
```

Ask in context — when the dealer taps "Scan QR", after the rationale — with React Native's `PermissionsAndroid.request(PermissionsAndroid.PERMISSIONS.CAMERA)` (the call shape the dead `Download/Invoice.js:69-71` used). `CAMERA` needs no Play Console form; uploaded photos need a Data safety entry (§5).

### 2.4 The capture flow

```
"Add slip photo" → rationale (en/hi) → permission → CameraCapture (the only file importing VisionCamera)
  → JPEG in the app's storage → quality gate (blur, glare) → resize + strip (§5) → queue (§6) → thumbnail
```

v5's capture calls were not captured in the research ("a new API"), so they live in `src/components/v2/Camera/CameraCapture.js` and nowhere else. The **quality gate** is the DU-slips spec's highest-leverage item: removing glare took measured text recall from 64.85 % to 78.50 %, and "no server-side processing recovers clipped pixels" — reject a blurred or glaring frame on the phone and re-prompt ("Move into shade and retake"). The viewfinder frame and buttons use `src/theme` tokens and hold their layout at 320 dp × fontScale 1 in en + hi.

### 2.5 The IRN QR on a GST e-invoice

What the notes say it holds (secondary sources: Masters India, the NIC e-invoice API FAQ):

| Part | Content |
|---|---|
| Format | a **signed JWT** — `header.payload.signature` — issued by the Invoice Registration Portal (IRP) |
| Payload | supplier and recipient GSTIN, invoice number, document type, date, value, line count, IRN |
| Trust | verifiable offline with the IRP's public key; NIC publishes a verifier app |
| Trap | decoding and re-encoding destroys the signature — keep the raw string |
| JSON key names | ⚠️ **not captured** — take them from the NIC API docs before mapping fields |

DZZLO's own invoice HTML carries no IRN or QR (grep of `src/helpers/Download`, 2026-09-29), so this is for **incoming** B2B invoices. Decode on the phone for display; the server verifies the signature (new API work, not yet agreed); the value is shown as decoded, never recomputed. On route (a) the scan is `useCodeScanner` inside `src/components/v2/Camera/QrScanner.js` (options unverified); on route (b) it is the Google code scanner on Android and `DataScannerViewController` on iOS 16+ with an A12 chip (route (a) below that) — neither has a New-Architecture wrapper, so both would sit behind a `scanCode()` method added to `NativeDocScanner` (1–2 days _(est.)_).

```js
// src/helpers/Einvoice/decodeIrnQr.js — for display only; it never says "valid"
const B64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';
const fromBase64Url = seg => {
  const bytes = [];
  for (let i = 0, acc = 0, bits = 0; i < seg.length; i += 1) {
    const v = B64.indexOf(seg[i]);
    if (v < 0) throw new Error('not base64url');
    acc = ((acc << 6) | v) & 0xffff; bits += 6;
    if (bits >= 8) { bits -= 8; bytes.push((acc >> bits) & 0xff); }
  }
  return decodeURIComponent(bytes.map(b => `%${b.toString(16).padStart(2, '0')}`).join('')); // UTF-8
};
export const decodeIrnQr = raw => {
  const text = String(raw ?? '').trim();
  const parts = text.split('.');
  if (parts.length !== 3 || parts.some(p => !p)) return { ok: false, raw: text };
  try { return { ok: true, raw: text, header: JSON.parse(fromBase64Url(parts[0])), payload: JSON.parse(fromBase64Url(parts[1])) }; }
  catch { return { ok: false, raw: text }; }
};
```

```js
// src/helpers/Einvoice/__tests__/decodeIrnQr.test.js — Tier 1; the fixture is built here, not a real invoice
const seg = o => Buffer.from(JSON.stringify(o)).toString('base64url');
it('decodes header and payload and keeps the raw string', () => {
  const raw = `${seg({ alg: 'RS256' })}.${seg({ n: 'INV-1', v: '1,23,456.50' })}.c2ln`;
  expect(decodeIrnQr(raw)).toEqual({ ok: true, raw, header: { alg: 'RS256' }, payload: { n: 'INV-1', v: '1,23,456.50' } });
});
it('refuses what is not a JWT, e.g. a UPI QR', () => expect(decodeIrnQr('upi://pay?pa=x@y').ok).toBe(false));
```

### 2.6 Jest and the device run

Screen tests never load VisionCamera: they mock **our** wrapper, so v5's unverified names never reach Jest.

```js
// in a screen test — the wrapper becomes a pressable stub
jest.mock('../../../components/v2/Camera/CameraCapture', () => {
  const { createElement } = require('react');
  const { Pressable } = require('react-native');
  return { __esModule: true,
    default: ({ onCapture }) => createElement(Pressable, { testID: 'fake-shutter', onPress: () => onCapture({ uri: 'file:///app/pending/cap-1.jpg' }) }) };
});
```

The device run is on physical phones (a simulator camera is not a real camera): the rationale, the prompt, the "don't allow" path, a printed e-invoice QR, and then the merged manifest check of Exercise 9.2. Screenshots and logs go to your local evidence folder, never into a repo.

## 3. Document scanner — `NativeDocScanner`

### 3.1 The decision gate: D5 versus this research

D5 says: use a maintained wrapper for the two system scanners; don't write a module. The obvious wrapper, react-native-document-scanner-plugin 2.0.4 (2026-01-02), has 98,850 downloads/wk, 4 releases in 12 months and 47 open issues; its Android side depends on `play-services-mlkit-document-scanner:16.0.0` and needs no camera-permission prompt. But its **module type is contested**: the ecosystem research found it ships `codegenConfig` (a TurboModule), while the React Native Directory lists it as an **Expo module** — which would pull `expo-modules-core` and need `expo` installed, deferred for this app. The only other candidate found, @infinitered/react-native-mlkit-document-scanner 5.0.0, has 473 downloads/wk.

So audit first (Exercise 9.1): unpack 2.0.4 and look for `codegenConfig` in its `package.json` versus an `expo-module.config.json`. Plain TurboModule → **USE it**, record the decision in the spec, skip to §4. Needs Expo → **BUILD `NativeDocScanner`**. The system still does all the hard work (edges, crop, glare cleanup); the module only presents it and returns files — the spec's reason against a camera module does not apply to one this thin.

### 3.2 What each platform gives

| | Android — ML Kit Document Scanner | iOS — `VNDocumentCameraViewController` (13.0) |
|---|---|---|
| UI | the whole flow: auto-capture, edge detection, rotation, crop, filters, shadow and stain cleanup | system scanner with auto-crop |
| Permission | **none** — "No camera permission is needed from your app" | `NSCameraUsageDescription` |
| Delivery | Google Play services (models too) | in the OS |
| Options | page limit, gallery import, `SCANNER_MODE_BASE` / `_BASE_WITH_FILTER` / `_FULL` | none — cap the pages yourself |
| Floor | fine at minSdk 24; **no Play services → fallback** to the camera intent plus a manual crop | 13.0 is below the 15.1 target: no gate |

**Parity:** Android can import an existing photo inside the scanner; iOS cannot — iPhone users pick existing photos through PHPicker (§4). **Future, unverified:** iOS 26's `RecognizeDocumentsRequest` (26.0) reads document structure — tables, lists, paragraphs, detected data — behind `@available(iOS 26, *)`, with `VNRecognizeTextRequest` (13.0) as the fallback (§8).

### 3.3 Spec, facade, tests

```ts
// specs/NativeDocScanner.ts
import type {TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';
export type ScanOptions = {pageLimit: number; allowGallery: boolean}; // allowGallery: Android only
export type ScanResult = {cancelled: boolean; pages: Array<string>};  // file:// JPEGs in the app's own storage
export interface Spec extends TurboModule {
  isAvailable(): Promise<boolean>; // iOS: the scanner is supported here; Android: Play services can run it
  scan(options: ScanOptions): Promise<ScanResult>;
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativeDocScanner');
```

The facade `src/native/docScanner.js` clamps `pageLimit` to 1–10 (house choice), turns a cancel into `[]` (not an error) and rejects any page that is not `file://` — the DU-slips spec's rule: "Never upload a `content://` URI directly"; copy scanner and picker output to a real file first. Red tests, in order: the Jest facade test with `specs/NativeDocScanner` mocked in `jest.setup.js` (cancel → `[]`, `content://` → error); a plain-JUnit test for the Kotlin `ScanPageCopier` (N input streams → N files in a temp `pending/` folder, safe names; the `ContentResolver` lookup stays in the shell); an XCTest for Swift `ScanPageWriter` (N synthetic `UIImage`s → N non-empty JPEGs; the file is a member of the app and `dzzlo_oms_appTests`, as in Phase 1). Then the green code below, then a real slip under a pump canopy.

### 3.4 Swift and Kotlin skeletons

```swift
// ios/dzzlo_oms_app/DocScanner/DocScanner.swift — main thread; the .mm adapter passes the top view controller
import VisionKit

@objcMembers public final class DocScanner: NSObject, VNDocumentCameraViewControllerDelegate {
  private var limit = 10
  private var done: ((NSDictionary) -> Void)?
  public func scan(from presenter: UIViewController, pageLimit: Int, done: @escaping (NSDictionary) -> Void) {
    limit = pageLimit; self.done = done
    let camera = VNDocumentCameraViewController(); camera.delegate = self
    presenter.present(camera, animated: true)
  }
  public func documentCameraViewController(_ c: VNDocumentCameraViewController, didFinishWith scan: VNDocumentCameraScan) {
    let pages = (0..<min(scan.pageCount, limit)).compactMap { ScanPageWriter.jpeg(scan.imageOfPage(at: $0)) } // file:// strings
    c.dismiss(animated: true) { self.done?(["cancelled": false, "pages": pages]) }
  }
  public func documentCameraViewControllerDidCancel(_ c: VNDocumentCameraViewController) {
    c.dismiss(animated: true) { self.done?(["cancelled": true, "pages": [String]()]) }
  }
}
```

The `RCTNativeDocScanner.mm` adapter — beside `DocScanner.swift` in `ios/dzzlo_oms_app/DocScanner/`, with Phase 1's imports (`<React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>` before `"dzzlo_oms_app-Swift.h"`) — finds the presenting view controller (React Native's `RCTPresentedViewController()` helper — verify the name in `React/RCTUtils.h`), hops to the main queue and resolves with the dictionary; `didFailWithError` rejects.

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/docscanner/NativeDocScannerModule.kt
// dependency: implementation("com.google.android.gms:play-services-mlkit-document-scanner:16.0.0") — the plugin's version, not re-checked
class NativeDocScannerModule(private val ctx: ReactApplicationContext) : NativeDocScannerSpec(ctx), ActivityEventListener {
  private var pending: Promise? = null
  init { ctx.addActivityEventListener(this) }
  override fun getName() = NAME

  override fun scan(options: ReadableMap, promise: Promise) {
    val activity = currentActivity ?: return promise.reject("E_NO_ACTIVITY", "no activity")
    val client = GmsDocumentScanning.getClient(GmsDocumentScannerOptions.Builder()
      .setPageLimit(options.getInt("pageLimit")).setGalleryImportAllowed(options.getBoolean("allowGallery"))
      .setScannerMode(GmsDocumentScannerOptions.SCANNER_MODE_FULL)
      .setResultFormats(GmsDocumentScannerOptions.RESULT_FORMAT_JPEG).build())
    pending = promise
    client.getStartScanIntent(activity)
      .addOnSuccessListener { sender -> activity.startIntentSenderForResult(sender, REQUEST, null, 0, 0, 0) }
      .addOnFailureListener { e -> pending = null; promise.reject("E_SCANNER", e.message, e) } // e.g. no Play services
  }

  override fun onActivityResult(activity: Activity, requestCode: Int, resultCode: Int, data: Intent?) {
    if (requestCode != REQUEST) return
    val p = pending ?: return; pending = null
    val uris = GmsDocumentScanningResult.fromActivityResultIntent(data)?.pages.orEmpty().map { it.imageUri }
    val files = ScanPageCopier(ctx.filesDir).copy(uris.mapNotNull { ctx.contentResolver.openInputStream(it) }) // streams → named files; plain JUnit
    p.resolve(Arguments.createMap().apply {
      putBoolean("cancelled", resultCode != Activity.RESULT_OK)
      putArray("pages", Arguments.fromList(files.map { Uri.fromFile(it).toString() }))
    })
  }
  override fun onNewIntent(intent: Intent) {}
  companion object { const val NAME = "NativeDocScanner"; const val REQUEST = 4711 }
}
```

Register `NativeDocScannerPackage` (Phase 1's `BaseReactPackage` shape) in `MainApplication.kt`, add `"NativeDocScanner": "RCTNativeDocScanner"` to `codegenConfig.ios.modulesProvider`, and pin both in `src/native/__tests__/docScanner.config.test.js`, shaped like Phase 1's `appInfo.config.test.js`. The ML Kit member names above come from its documentation, not this course's notes — the compile settles them.

## 4. Pick without permission

**iOS — `PHPickerViewController` (14.0)**, or SwiftUI `PhotosPicker` (16.0): a system-owned view that returns the chosen items "without library access". No prompt and no key **as long as** results are read through `NSItemProvider` only; touching `PHAsset` or `PHPhotoLibrary` — including reading EXIF through PhotoKit — brings back the key and the prompt (DU-slips spec, quoting Apple). With a PHPicker-only design the limited-library state (iOS 14) cannot occur, so there is no `.limited` branch to build. App Review 5.1.1(iii) asks for exactly this: "use the out-of-process picker … rather than requesting full access".

**Android — the Photo Picker:** built in from Android 13; backported to 4.4–12 through Google Play services once the manifest declares the `ModuleDependencies` service; launched with `PickVisualMedia` / `PickMultipleVisualMedia` (androidx.activity 1.7.0+; the DU-slips spec pins `androidx.activity:activity:1.9.+`, citing image-picker's README); falls back to `ACTION_OPEN_DOCUMENT` without the picker; no permission; persistable grants capped at 5,000 per app. Android 11 and 12 alone are 18.2 % of Indian phones (StatCounter, Aug 2026), so the backport matters. Android 16 adds an embeddable picker (Jetpack support "forthcoming"). Play allows `READ_MEDIA_IMAGES` only "if system pickers … are not sufficient" (full compliance since 28 May 2025) — never declare it.

```xml
<!-- android/app/src/main/AndroidManifest.xml, inside <application>; needs xmlns:tools on <manifest> -->
<service android:name="com.google.android.gms.metadata.ModuleDependencies"
         android:enabled="false" android:exported="false" tools:ignore="MissingClass">
  <intent-filter><action android:name="com.google.android.gms.metadata.MODULE_DEPENDENCIES" /></intent-filter>
  <meta-data android:name="photopicker_activity:0:required" android:value="" />
</service>
```

| Library that exposes them | Version (date) | New Arch | Uses the system pickers? |
|---|---|---|---|
| react-native-image-picker | 8.2.1 (2025-05-04) — no release in 16 months, 306 open issues, 515,089/wk | TurboModule | ⚠️ **conflict**: this course's research could not confirm whether 8.x launches `PickVisualMedia` or `ACTION_GET_CONTENT` on Android; the DU-slips spec cites its README saying the library picker uses the Android Photo Picker and PHPicker — Exercise 9.5 settles it |
| expo-image-picker | 57.0.20 (2026-09-24), 4.9M/wk | Expo module | optional track (§9) |

Three pitfalls:

- **ITMS-90683.** Apple scans the whole binary, pods included, for protected APIs; the DU-slips spec notes that image-picker and VisionCamera both link `Photos.framework`. Audit the final pod set; if any pod references PhotoKit, ship `NSPhotoLibraryUsageDescription` anyway — and still never request authorisation.
- **HEIC.** ⚠️ Not covered by the research: check what type the picker hands back on an iPhone (Exercise 9.5) and force JPEG in the resize step (§5), so the server, its image worker and Android viewers see one format.
- **`content://`.** Copy picker output into the app's own storage before upload; the DU-slips spec traces "EntityTooLarge on a 300 KB file" to provider streams that mis-report their length.

## 5. Compress, strip, store

**Resize:** @bam.tech/react-native-image-resizer 3.0.11 (2024-11-25; TurboModule; 110,298/wk; stale release, but the repo is active — push 2026-09-26). The DU-slips spec read its pipeline: Android decodes with a power-of-two `inSampleSize`, then scales the remaining ≤ 2× bilinearly — no aliasing of dot-matrix print; iOS uses CoreGraphics ("eyeball iOS output"). The alternative is react-native-compressor 2.0.3 (2026-07-25, Nitro).

**The size budget** — the DU-slips spec's numbers (Phase 3 §4.3), all resting on an **unmeasured** ~2.0–2.3 mm printed cap height; put a ruler on a real slip first:

| Setting | Value | Why |
|---|---|---|
| Upload artefact | one file | the server derives its view and thumbnail variants (D3) — don't send three over a bad link |
| Long edge | 2,048 px; 2,560 px when the crop box is narrower than ~1:3 | ≥ 1,000 px across the printed width |
| Encoding | JPEG q82, grayscale | ~250–420 KB per slip |
| Metadata | EXIF stripped, GPS especially | privacy — re-encoding should drop it; verify (Exercise 9.5) |
| Capture | full resolution, downscale in software | an area filter "marries the dots back into strokes" |

**EXIF:** the ecosystem research says don't read it — "stamp time and place in the app at capture instead"; @lodev09/react-native-exify 1.0.3 (2026-02-22) exists if that ever changes. Store `capturedAt` as epoch milliseconds and show it in IST with the house helpers.

| File state | iOS | Android | Why |
|---|---|---|---|
| Captured, not yet uploaded | `Application Support/pending/` | `filesDir/pending/` | evidence must survive storage pressure, and the OS may clear caches (general platform behaviour — the DU-slips spec puts its queue files in the cache; settle it with the spec's owner) |
| Uploaded, confirmed by the server | delete | delete | the server holds the original and its variants |
| Exported for share or print | cache, deleted after | cache, deleted after | hand over, then delete (Android research, for budget phones) |
| User tapped "Save to Photos / Downloads" | Photos, add-only | MediaStore | §7 — never by default |

Queue metadata goes in AsyncStorage — paths, never bytes; the DU-slips spec notes its Android store has a 6 MB default cap — or react-native-mmkv 4.3.2 (Nitro) later. At app start, delete every file whose upload the server has confirmed; never delete unconfirmed evidence, however old — list anything past 30 days for the dealer to retry (house choice).

## 6. Upload in the background — `NativeUpload`

### 6.1 Why, and when

A dealer photographs three slips, locks the phone and walks back to the forecourt. iOS suspends the app; Android skins kill background work (dontkillmyapp rates Xiaomi, OnePlus and Samsung 5/5, Oppo 4/5, Vivo, realme and Tecno 3/5). An upload living in JavaScript dies with the process.

**v1 ships without this module.** D7 keeps uploads in the foreground — `XMLHttpRequest` with a `{uri}` body (for upload progress), a durable JS queue, the drain gated on `isInternetReachable !== false` (captive-portal Wi-Fi at pumps), backoff capped near 5 attempts — and adds background upload only "if telemetry later shows dealers backgrounding mid-upload". The ecosystem research agrees. When that trigger fires, nothing maintained fills the gap: react-native-background-upload 6.6.0 is dead; rn-background-upload 0.1.0 (2026-02-11) is too new; react-native-blob-util's `IOSBackgroundTask` is partial, and the spec rejects blob-util over an open bridgeless crash (#479, on 0.24.10 — whether 0.25.1 of 2026-09-24 fixes it was not checked); @kesha-antonov/react-native-background-downloader uploads too, per the spec, but its Android half is best-effort in-process. Hence `NativeUpload`: **Advanced, built when the trigger fires**, draining the same queue. (The shared RTK Query base query cannot carry uploads either: `timeout: 10000` at `src/store/apis/createApi.js:48`, and `retry(…)` at `:96` with `maxRetries: 2` at `:105` re-sends the body.)

### 6.2 The platform rules

| | iOS — `URLSessionConfiguration.background(withIdentifier:)` (8.0) | Android — WorkManager + OkHttp |
|---|---|---|
| Body | **from a file only** — "uploads from data instances or a stream fail after the app exits"; a multipart presigned POST must be written to a file first (inference) | streamed from the file by OkHttp inside a `CoroutineWorker` |
| App killed while suspended | the system relaunches it in the background; recreate the session **with the same identifier** | WorkManager runs the work again |
| User force-quits | "the system cancels all of the session's background transfers" (Apple, quoted in the DU-slips spec) | a swipe from Recents leaves the work scheduled; Settings → Force stop halts it until the next launch (platform behaviour, not from the research); OEM killers aside |
| Scheduling | a rate limiter delays tasks started while in the background | constraints and backoff; expedited work (`setExpedited`) is an expedited job on 12+, and on older versions may run as a foreground service needing `getForegroundInfo()` |
| Wake-up | `application(_:handleEventsForBackgroundURLSession:completionHandler:)` in `AppDelegate` | the worker is the entry point |
| Policy | standard networking, no background mode (2.5.4 is fine) | plain WorkManager needs no form. **Avoid a `dataSync` foreground service** (`FOREGROUND_SERVICE_DATA_SYNC`, a Play declaration with a video when targeting 14+, 6 h per 24 h, no start from `BOOT_COMPLETED` on 15+). User-initiated data transfer jobs (Android 14+: `RUN_USER_INITIATED_JOBS`, `setUserInitiated(true)`, `JobService.setNotification()`, no Jetpack support) are a later option for big user-started batches |
| Newer option | `BGContinuedProcessingTask` (26.0): starts from a person's action, shows progress in a system Live Activity, may use the network — gate `@available(iOS 26, *)`, background session as the fallback | — |

The app already pulls `androidx.work:work-runtime:2.8.1` transitively (merged manifest) — declare your own version on purpose.

**No JavaScript at wake-up.** React Native starts inside `SceneDelegate` (`ios/dzzlo_oms_app/AppDelegate.swift:41-56`), and a background relaunch for session events connects no scene, so no JS runs (inference); Android workers run without JS too. Completions therefore go into a small native **journal** (a JSON file in the app's own storage) that JS drains at start with `takeFinished()`. Live events are a convenience, never the source of truth.

### 6.3 The spec, with typed events

```ts
// specs/NativeUpload.ts
import type {TurboModule, CodegenTypes} from 'react-native';
import {TurboModuleRegistry} from 'react-native';
export type UploadField = {name: string; value: string};
export type UploadRequest = {
  id: string;                 // the slip's UUID, minted at capture: idempotency key and S3 key suffix
  fileUri: string;            // file:// in the app's own storage, never content://
  url: string;                // presigned POST URL from the API
  fields: Array<UploadField>; // the policy fields, in order
  mimeType: string;           // image/jpeg
};
export type UploadProgress = {id: string; sentBytes: number; totalBytes: number};
export type UploadFinished = {id: string; status: number; outcome: string}; // 'done' | 'failed' | 'needsPresign'
export interface Spec extends TurboModule {
  enqueue(request: UploadRequest): Promise<void>; // idempotent on id
  cancel(id: string): Promise<void>;
  takeFinished(): Promise<Array<UploadFinished>>; // drains the native journal
  readonly onProgress: CodegenTypes.EventEmitter<UploadProgress>;
  readonly onFinished: CodegenTypes.EventEmitter<UploadFinished>;
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativeUpload');
```

In JS, `const sub = NativeUpload.onFinished(r => …)` returns a subscription; call `sub.remove()` in the effect cleanup. iOS emits from an adapter built on the generated `NativeUploadSpecBase` (`[self emitOnFinished:@{…}]`); Android calls `emitOnFinished(Arguments.createMap().apply { … })`. The facade `src/native/upload.js` refuses `content://`, and the queue's state machine (`queued → uploading → done | failed | needsPresign`) is a pure Tier 1 module, `src/helpers/DuSlips/queue.js` — the file name the DU-slips spec proposes.

### 6.4 Skeletons

```swift
// ios/dzzlo_oms_app/Upload/BackgroundUploader.swift
import Foundation

@objcMembers public final class BackgroundUploader: NSObject, URLSessionDataDelegate {
  public static let shared = BackgroundUploader()
  public static let identifier = "in.vsyst.dzzlooms.upload"
  public var systemCompletion: (() -> Void)?            // set by the AppDelegate hook below
  public var onEvent: ((String, NSDictionary) -> Void)? // set by RCTNativeUpload.mm while JS is alive
  public lazy var session = URLSession(configuration: .background(withIdentifier: Self.identifier), delegate: self, delegateQueue: nil)

  public func enqueue(id: String, fileURL: URL, url: URL, fields: [Dictionary<String, String>], mimeType: String) throws {
    let body = try MultipartFile.write(fields: fields, file: fileURL, mimeType: mimeType) // pure; XCTest pins its bytes
    var request = URLRequest(url: url); request.httpMethod = "POST"
    request.setValue(body.contentType, forHTTPHeaderField: "Content-Type")
    let task = session.uploadTask(with: request, fromFile: body.url); task.taskDescription = id; task.resume()
  }
  public func urlSession(_ s: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
    let status = (task.response as? HTTPURLResponse)?.statusCode ?? 0
    onEvent?("finished", UploadJournal.append(id: task.taskDescription ?? "", status: status, error: error)) // journal first
  }
  // progress: urlSession(_:task:didSendBodyData:totalBytesSent:totalBytesExpectedToSend:) → onEvent?("progress", …)
  public func urlSessionDidFinishEvents(forBackgroundURLSession s: URLSession) {
    DispatchQueue.main.async { self.systemCompletion?(); self.systemCompletion = nil }
  }
}

// ios/dzzlo_oms_app/AppDelegate.swift — inside class AppDelegate (line 8), not SceneDelegate
func application(_ application: UIApplication, handleEventsForBackgroundURLSession identifier: String,
                 completionHandler: @escaping () -> Void) {
  guard identifier == BackgroundUploader.identifier else { return completionHandler() }
  BackgroundUploader.shared.systemCompletion = completionHandler
  _ = BackgroundUploader.shared.session // recreate the session with the same identifier
}
```

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/upload/UploadWorker.kt
class UploadWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
  override suspend fun doWork(): Result {
    val job = UploadJob.from(inputData) // pure parsing, plain JUnit; progress: setProgress(…) → the module emits onProgress
    val response = try { Http.client.newCall(MultipartRequest.build(job)).execute() } // streams the file
                   catch (e: IOException) { return if (runAttemptCount < 5) Result.retry() else finish(job, 0, "failed") }
    return response.use { r -> when {
      r.isSuccessful -> finish(job, r.code, "done")
      r.code == 403 && S3Error.isExpiredPolicy(r.body?.string()) -> finish(job, r.code, "needsPresign") // S3 errors are XML
      r.code >= 500 && runAttemptCount < 5 -> Result.retry()
      else -> finish(job, r.code, "failed")
    } }
  }
  private fun finish(job: UploadJob, status: Int, outcome: String): Result {
    UploadJournal(applicationContext).append(job.id, status, outcome) // read by takeFinished()
    return if (outcome == "failed") Result.failure() else Result.success()
  }
}

// NativeUploadModule.enqueue — one unique work per slip id, so a second enqueue of the same id is a no-op
WorkManager.getInstance(ctx).enqueueUniqueWork("upload-${req.id}", ExistingWorkPolicy.KEEP,
  OneTimeWorkRequestBuilder<UploadWorker>()
    .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .setInputData(UploadJob.toData(req)).build())
```

**Tests, red first:** Jest for the facade and the queue (a `needsPresign` result sends the slip back to presign; the fifth `failed` shows **Retry**; `takeFinished()` runs at start); XCTest pins `MultipartFile.write`'s exact bytes with an injected boundary and `UploadJournal`'s round-trip; plain-JUnit tests do the same for `MultipartRequest.build`, `UploadJob` and `S3Error` on sample XML; the worker itself runs as an instrumented test on the emulator with WorkManager's test helpers (`work-testing`, version not captured) against a local test server. **Device:** start three uploads, lock the phone for five minutes, unlock — all `done`; stop the app from the IDE mid-upload — the journal reports on the next launch; force-quit on iOS — transfers are cancelled and the JS queue re-enqueues on the next launch.

### 6.5 The retry and idempotency contract — for the API to agree

The API has no upload code today (verified). This is what `NativeUpload` and the JS queue assume — a design the API must agree to, extending the DU-slips spec's D2 (presigned POST, direct to S3) and its rule that "S3 Event Notification is the source of truth, never the client callback":

1. The phone mints `slipId` (a UUID) at capture — the idempotency key and the S3 object-key suffix.
2. `POST /so_msts/:id/slips/presign { slipId, bytes, mime }` is idempotent on `slipId`: asking again returns a **fresh policy for the same key**.
3. The S3 POST may be repeated: same key, same bytes, same result.
4. The S3 event creates the slip row keyed by `slipId`; the app's `commit` call is a hint and idempotent — a second call returns the same slip.
5. An expired policy is `needsPresign`, not `failed`. Native code never re-presigns — it holds no auth token, because a presigned policy carries its own authority; JS re-presigns at the next foreground.
6. Backoff with jitter, about five attempts, then a manual **Retry**; S3's XML error body is parsed and shown.

The route names follow the spec's list (`POST /:id/slips/presign`, `POST /:id/slips/commit`); the request bodies are this course's proposal.

## 7. Download

- **Save to Photos (iOS):** "if your app only adds photos to the library, instead, request add-only access" — `NSPhotoLibraryAddUsageDescription`, only with an explicit "Save to Photos" button (the spec's string: "Save a copy of a receipt image from an order to your Photos library.").
- **Save on Android:** 29+ `MediaStore.Images` with `RELATIVE_PATH=Pictures/DZZLO` and `IS_PENDING`, no permission; 24–28 would need `WRITE_EXTERNAL_STORAGE`, so route those through the share sheet.
- **Downloads:** `DownloadManager` (API level believed 9, not confirmed in the research) retries after failures, connectivity changes and reboots, offers `VISIBILITY_VISIBLE_NOTIFY_COMPLETED`, `setDestinationInExternalPublicDir` / `setDestinationInExternalFilesDir` and the `ACTION_DOWNLOAD_COMPLETE` broadcast; `MediaStore.Downloads` is API 29+. The dead `Download/Invoice.js:24-60` did this with rn-fetch-blob plus a runtime `WRITE_EXTERNAL_STORAGE` request — don't revive it. If a download must continue in the background: @kesha-antonov/react-native-background-downloader 4.6.3 (2026-09-15, TurboModule).
- **Signed URLs expire:** the spec signs slip URLs for 15 minutes (D8) — download promptly or ask again.
- **Default — share after download:** download to the cache → `shareDocument` ([[03-phase-3-files-share-and-pdf]] §2) → the user saves from the sheet → delete. Zero permissions on both platforms.

## 8. OCR — later, after an experiment

| | iOS — Vision | Android — ML Kit |
|---|---|---|
| Text | `VNRecognizeTextRequest` (13.0); Swift `RecognizeTextRequest` (18.0) | Text Recognition v2: Latin, Chinese, **Devanagari**, Japanese, Korean — blocks, lines, elements, symbols, each with a box, confidence and language |
| Documents | `RecognizeDocumentsRequest` (26.0): tables, lists, paragraphs, detected data (26 languages, secondary sources) | — |
| iOS 27 | Foundation Models can call Vision tools on-device | — |
| RN wrappers | @react-native-ml-kit/text-recognition 2.0.0 (2025-09-01) — **not New-Arch**, no release in 12 months; react-native-vision-camera-ocr-plus 2.0.6 (2026-08-20), a small frame-processor plugin | same |

**The accuracy gap is unproven.** No source measured Vision or ML Kit on Indian thermal-printed or handwritten DU slips, or on seven-segment totalisers. What evidence exists points the wrong way: the DU-slips spec cites a receipt benchmark (KORIE, 17,587 crops) whose character error rates of 15.8–25.4 % persist even at 300 dpi, and decides that **OCR never auto-writes a financial value** (D10) — it suggests, a person confirms. Verdict: SKIP now, WRAP later, as its own release with re-consent if images ever go to a third party (App Review 5.1.2(ii), per the spec).

The experiment to run first — a throwaway spike build, never merged:

1. Collect 50 slips and 20 totaliser photos from three pumps with the §3 scanner (house numbers).
2. Type the truth for litres, rate, amount, date and vehicle number.
3. Run Vision on an iPhone and ML Kit v2 on an Android phone; score **field-level exact match**, with and without the glare/blur gate.
4. Fix the bar in writing before any product work (house choice: ≥ 95 % exact on litres and amount, or no feature).

Results and photos stay in your local evidence folder, never in a repo.

## 9. After the upgrade, the optional Expo track — and Exercises

> **After the upgrade to 0.87:** the Jest preset moves to `@react-native/jest-preset` (from 0.85); the mocks stay. AGP 9 and compileSdk 37: rebuild, re-run the instrumented and worker tests, and re-check 16 KB alignment for VisionCamera's and Nitro's `.so` files. SwiftPM (experimental): framework-style `#import <React/…>` in the `.mm` adapters. Raising **targetSdk** to 37 is a separate decision with its own behaviour changes; 0.87 does not make it.

> **Optional Expo track (Expo-paired RN only):** `expo-image-picker` 57.0.20 would replace image-picker; `expo-camera` 57.0.6 — SDK 58 adds `CameraView.scanDocumentAsync`, multi-page scanning on iOS and Android — could replace `NativeDocScanner` (whether expo-camera scans barcodes: not verified); `expo-image-manipulator` 57.0.20 the resizer; `expo-file-system` 57.0.7 the file moves. `expo-background-task` 57.0.21 is **not** an uploader: 15-minute minimum on Android, timing "not guaranteed", unavailable on iOS simulators, stopped when the user kills the app. Why not now: as in [[03-phase-3-files-share-and-pdf]] §6 — `expo` in a bare app, iOS 16.4 in the current docs, and no SDK for 0.84 or 0.87 (SDK 58 ↔ 0.88 RC).

### Exercises

**9.1 — The scanner audit.** Unpack react-native-document-scanner-plugin 2.0.4 (`npm pack react-native-document-scanner-plugin@2.0.4`) and look for `codegenConfig` versus `expo-module.config.json`. _A written USE-or-BUILD decision, added to the DU-slips spec with the user's approval._

**9.2 — The merged manifest.** `(cd android && ./gradlew :app:processReleaseManifest)`, then read the merged output. _Route (b): no `CAMERA`, no `READ_MEDIA_*`. Route (a): `CAMERA` plus three `required="false"` features. Saved to your local evidence folder._

**9.3 — IRN QR, red → green.** Write `decodeIrnQr.test.js` first (`APP_ENV=testing npx jest decodeIrnQr`), then the helper. Add cases for padding characters, a two-segment string and non-UTF-8 bytes. _Red and green runs in the PR description._

**9.4 — `NativeDocScanner`, red → green → a real slip.** Jest, plain JUnit and XCTest red; the skeletons green; then scan a real DU slip in shade and in sun on both platforms. _Page counts and file sizes before and after resize, in the Lab Notes._

**9.5 — The picker and resize audit.** On Android 11 and 12 emulators: does the backported Photo Picker appear, and does image-picker 8.2.1 launch it? On an iPhone: what type comes back, and does the resized JPEG keep any EXIF or GPS? _Three answers that remove three "unverified" labels._

**9.6 — The foreground queue survives.** Capture three slips offline, kill the app, relaunch on captive-portal Wi-Fi, then on real data. _All three upload exactly once; the Wi-Fi without internet causes no attempt._

**9.7 — `NativeUpload` on a locked phone** (only once the trigger of §6.1 has fired). Run the device script of §6.4 on an iPhone and on a Xiaomi or Samsung phone. _A dated table of outcomes per case in the Lab Notes._

**9.8 — The OCR spike (optional).** Run §8's experiment. _A field-level accuracy table and a written go/no-go._

## Lab Notes

**Verified by reading, 2026-09-29** — nothing built, installed or changed. App `release/v1_79`, audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30): the `Info.plist` key list (no camera or photo strings) and no `.lproj` folders; the manifest declares only `INTERNET`; `ImagePicker/index.js:12,14,85-87,97,101`; `jest.setup.js:245-256`; `createApi.js:48,96,105`; `Podfile:11-15,20-23`; `AppDelegate.swift:8,41-56`; no IRN or QR in `src/helpers/Download`. API HEAD `9690be9`: no upload or presign code.

**Open — not verified by this course's research:** the scanner plugin's module type (9.1); whether image-picker 8.x uses the Android Photo Picker (9.5); VisionCamera v5's capture and code-scanner option names; the IRN payload's JSON keys; HEIC output and EXIF stripping (9.5); `DownloadManager`'s API level; whether blob-util 0.25.1 fixes #479; OCR accuracy on DU slips (9.8); and the member names in the skeletons (`imageOfPage`, `pageCount`, `RCTPresentedViewController`, `GmsDocumentScanning`, `getStartScanIntent`, `urlSessionDidFinishEvents`, `enqueueUniqueWork`) — the compile and the device run settle those.
