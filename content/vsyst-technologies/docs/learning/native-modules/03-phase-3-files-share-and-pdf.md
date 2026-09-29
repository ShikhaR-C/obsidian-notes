# Phase 3 — Files, Sharing and PDF: The Invoice Leaves the Phone

> Level: Intermediate | Time: ~1 h to read; 6–11 working days to build on both platforms _(est.)_ | Outcome: a dealer turns the invoice on screen into an A4 PDF, sends it to the customer's WhatsApp or any app, prints it, previews it, and exports a TCS/TDS CSV to a place they choose — two in-house modules (`NativePdf`, `NativePrint`) built test-first, maintained libraries for the rest.

---

## 1. The One Idea

An invoice in DZZLO today is **a string of HTML painted into a WebView**. The phone can show it; the phone cannot hand it to anyone. This whole phase is one pipeline: invoice data → HTML (exists today) → a PDF file (`NativePdf`) → share, print, save or preview.

What the app does today — read on `dzzlo_oms_app` `release/v1_79`, audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30):

| Evidence | Where |
|---|---|
| Product, GST and payment-advice invoices are built as HTML by the helpers in `src/helpers/Download/`, then shown in `<WebView originWhitelist={['*']} source={{ html }} />` | `src/screens/Common/_Invoice_/Render.js:5-11` (imports), `:35-80` (which helper), `:92-95` (WebView) |
| Receipt vouchers and the TCS/TDS month summary go the same way | `src/screens/Common/_Voucher_/HTML/Render.js:5-6,35-37`; `src/screens/Common/Reports/TcsTds/Render/index.js:46-49` |
| `react-native-html-to-pdf` is imported and never called | `TcsTds/Render/index.js:5` — nothing in lines 10–54 uses it |
| A save/share flow was built once and abandoned; no live file imports `Share` or `PermissionsAndroid` (census, 2026-09-29) | `src/components/Download/RNhtmlpdf.js:14-16` (`convert` → `Alert.alert(file.filePath)`), `Download/invoiceHTML/index.js:28-38`, `ShowInvoice.js` (a commented-out `Share.share` stuffing a base64 `data:` URL into `url`), `Download/Invoice.js:1` (`rn-fetch-blob`, not installed; asks for `WRITE_EXTERNAL_STORAGE` at `:69-71`) — all dead code |
| The only way out is **Email**, and the server does it | `_Invoice_/index.js:59` (`useEmail_invMutation`, sheet in `EmailBS.js`) → `store/apis/dzzlooms/invs.js:66` (`invs/a/email`); vouchers `voc_msts.js:191`; TCS/TDS `balance/SectionalAcc.js:98` |

That last row matters. The API already **renders PDFs**: `dzzlo_oms_api` `api_v3/services/invoice/htmlPdf/fileBuffer.js:39-58` drives puppeteer (`headless: "shell"`, `page.setContent(html, { waitUntil: "networkidle0" })` at `:51`), and `api_v3/controllers/App/email.js:140-146` attaches the result to an email (API `release/v1_79`, HEAD `9690be9`, read 2026-09-29). No route returns that PDF to the phone, and its page is **30 × 42.4 cm** (`htmlTemplates/index.js:251-252`) — about A3, not A4. So the first decision is the user's:

| | Server PDF (a new endpoint returning what email already renders) | Device PDF (`NativePdf`, this phase) |
|---|---|---|
| Works at a pump with no signal | No | Yes |
| One template for email and share | Yes | No — the app's `src/helpers/Download/*` and the API's `htmlTemplates/*` are separate copies that drift |
| Paper | 30 × 42.4 cm today | A4 (house choice) |
| API change | Yes — needs approval | None |

This phase builds the device path: it is the native-module lesson and it works offline. The server path stays open; [[10-capstones]] puts the two PDFs side by side.

### The four verbs

| Verb | What a dealer does | iOS building block (since) | Android building block (since) | Route |
|---|---|---|---|---|
| **Create** | invoice → PDF; TCS/TDS → CSV | `UIPrintPageRenderer` (4.2) drawn into `UIGraphicsPDFRenderer` (10.0) | WebView print adapter, `createPrintDocumentAdapter(jobName)` (API 21 form) | BUILD `NativePdf`; CSV in JS |
| **Share** | send to the customer's WhatsApp, or any app | `UIActivityViewController` (6.0) | `ACTION_SEND` + AndroidX `FileProvider` (levels not captured in the research) | USE react-native-share |
| **Import** | pick a PDF, CSV or image | `UIDocumentPickerViewController` (8.0) | SAF `ACTION_OPEN_DOCUMENT` (API 19) | USE @react-native-documents/picker |
| **Export / print** | save to Files or a folder; AirPrint / office printer | `init(forExporting:asCopy:)` (14.0); `UIPrintInteractionController` (4.2) | SAF `ACTION_CREATE_DOCUMENT` (API 19), `MediaStore.Downloads` (API 29); `PrintManager` (level not captured) | picker (export ⚠️ unverified) + BUILD `NativePrint` |

Everything above sits at or below the iOS 15.1 deployment target and minSdk 24, except `MediaStore.Downloads` (API 29), which gets a gate in §5.2.

### Library or in-house module?

Versions and dates from npm and the React Native Directory, verified 2026-09-29.

| Library | Version (date) | New Arch | Health | Verdict |
|---|---|---|---|---|
| react-native-share | 12.3.1 (2026-05-04) | ✅ TurboModule | repo push 2026-08-31; 740,975/wk | **USE** (§2) |
| @react-native-documents/picker | 12.0.2 (2026-07-28) | ✅ TurboModule | active; 344,187/wk | **USE** for import (§5) |
| @react-native-documents/viewer | 4.0.1 (2026-07-28) | ✅ TurboModule | active | **USE** for preview (§5.5) |
| react-native-view-shot | 6.0.1 (2026-09-20) | ✅ TurboModule | active; 1.2M/wk | **USE** for "share as image" (§2.5) |
| react-native-file-access | 4.0.4 (2026-09-18) | ✅ TurboModule | active | **USE** to write CSVs (§5.4) |
| react-native-html-to-pdf | 1.3.0 (2025-09-04) | ⚠️ Directory: TurboModule; a 2026 guide doubts it | no release in 12 months | **REMOVE** — [[02-phase-2-dependency-diet]] |
| react-native-print | 0.11.0 (2023-01-22) | ❌ | unmaintained | **SKIP** |
| expo-print · expo-sharing | 57.0.2 · 57.0.22 | Expo modules | active | optional track (§6) |

Two jobs have no maintained New-Architecture wrapper for a bare 0.84 app: **HTML → paginated PDF** without Expo, and the **system print dialog**. They become `NativePdf` and `NativePrint`, built with the recipe from [[01-phase-1-foundations]].

## 2. Share — react-native-share 12.3.1

### 2.1 Install

```bash
cd /Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app
yarn add react-native-share@12.3.1 && (cd ios && bundle exec pod install)
```

> Nothing in this course is committed, merged, pushed or published without the user's word. The lesson describes; the user says "start".

### 2.2 Declarations

iOS `canOpenURL` sees only the schemes you list; Android 11+ sees only the packages you query — without a matching `<queries>` entry `Linking.canOpenURL` resolves `false` there (RN's docs say it may reject). Add the Android entries to the `<queries>` block that [[02-phase-2-dependency-diet]] creates for `https`:

```xml
<!-- ios/dzzlo_oms_app/Info.plist -->
<key>LSApplicationQueriesSchemes</key>
<array><string>whatsapp</string></array>

<!-- android/app/src/main/AndroidManifest.xml, inside <manifest> -->
<queries>
  <package android:name="com.whatsapp" />
  <package android:name="com.whatsapp.w4b" />
  <intent><action android:name="android.intent.action.SEND" /><data android:mimeType="application/pdf" /></intent>
</queries>
```

⚠️ The research marks the WhatsApp `<queries>` entries as an **inference** (Android's docs were not fetched). `com.whatsapp.w4b` appears in the notes as WhatsApp Business; `com.whatsapp` is the consumer app's well-known id — confirm both with `adb shell pm list packages | grep -i whatsapp`. The `SEND` entry follows the DU-slips spec's rule that libraries call `queryIntentActivities()` before launching, so without it "nothing happens" on Android 11+ ([[vsyst-technologies/docs/tasks/tasks_14_du_slips/05-phase-5-store-compliance|DU-slips spec, Phase 5 §1.4]]).

### 2.3 A file to a WhatsApp number — `shareSingle`

The documented option: `social: Share.Social.WHATSAPP` with `whatsAppNumber` ("country code + phone number"); `WHATSAPP` works on Android and iOS, `WHATSAPPBUSINESS` on Android only. Source: https://github.com/react-native-share/react-native-share/blob/main/website/docs/share-single.mdx

| What the research could not verify | Status (2026-09-29) |
|---|---|
| Android: file + number opens that chat with the PDF attached | documented option; not device-verified |
| iOS: a file straight to one contact | ❌ open issue #1699, "It is not possible to send a file directly to a WhatsApp contact" — **plan the share sheet on iOS** |
| PDFs arriving without `.pdf` in release builds | open issue #1556, not re-checked against 12.3.1 |
| Android 18 stops granting URI access on `ACTION_SEND` implicitly (Android 17 docs) | check the library sets `FLAG_GRANT_READ_URI_PERMISSION` |

wa.me numbers carry no `+`, spaces, leading zeroes, brackets or dashes (third-party guides; WhatsApp's own FAQ could not be fetched). One pure helper, one facade — the only file that knows the library:

```js
// src/helpers/Share/whatsAppNumber.js
export const toWhatsAppNumber = raw => {
  const digits = String(raw ?? '').replace(/\D/g, '').replace(/^0+/, '');
  if (/^[6-9]\d{9}$/.test(digits)) return `91${digits}`; // Indian mobile (house rule)
  return /^91[6-9]\d{9}$/.test(digits) ? digits : null;
};

// src/helpers/Share/shareDocument.js
import { Platform } from 'react-native';
import Share from 'react-native-share';
import { toWhatsAppNumber } from './whatsAppNumber';
export const shareDocument = ({ uri, mime, filename, phone }) => {
  const number = toWhatsAppNumber(phone);
  const file = { url: uri, type: mime, filename }; // ⚠️ option names not captured in the notes: confirm in the 12.3.1 docs
  if (number && Platform.OS === 'android') {
    return Share.shareSingle({ ...file, social: Share.Social.WHATSAPP, whatsAppNumber: number });
  }
  return Share.open(file); // generic sheet — the iOS path because of #1699
};
```

### 2.4 The generic share sheet

`Share.open` is the library's generic-sheet call (its option list was not captured in the notes). On iOS it is `UIActivityViewController` (6.0) — WhatsApp, Mail, Drive, **Save to Files**; on Android the chooser. It is also the right "download" button: the DU-slips spec makes the share sheet the default save route because it needs **zero** Android permissions ([[vsyst-technologies/docs/tasks/tasks_14_du_slips/04-phase-4-view-download-share|DU-slips spec, Phase 4 §2.3]]).

### 2.5 "Image and PDF both"

The reviews are specific. Vyapar 5★ (2026-09-19): _"invoice jb share kary tu picture shere ho pdf hoti ha phir screen shot lina parta ha dono option dy picture and pdf"_ — give both. Khatabook 3★ (2026-09-23): _"When I send a bill from Khatabook via WhatsApp, it automatically converts to PDF; how can I stop this?"_ — don't choose for them. Vyapar 5★ (2026-08-26) praises native WhatsApp share because _"automatically contact is selected"_ — that is `whatsAppNumber`. Rank 1 in the product research is exactly this.

So the invoice screen gets one **Share** action opening a v2 `Sheet` (`src/components/v2/Sheet.js`) with **PDF** and **Image**: labels from `useStrings` (en + hi), arrangement held at 320 dp × fontScale 1, colours from `src/theme` tokens. The image is react-native-view-shot capturing the invoice view to a PNG in the cache, then the same `shareDocument`. ⚠️ Whether view-shot captures a WebView's content on both platforms is **not verified** (Exercise 7.8); the fallback is a page-to-image method on `NativePdf` later.

### 2.6 Jest: mock, red, green

```js
// jest.setup.js — beside the OneSignal stub
jest.mock('react-native-share', () => ({ __esModule: true, default: {
  open: jest.fn(() => Promise.resolve({ success: true })), shareSingle: jest.fn(() => Promise.resolve({ success: true })),
  Social: { WHATSAPP: 'whatsapp', WHATSAPPBUSINESS: 'whatsappbusiness' } } }));

// src/helpers/Share/__tests__/shareDocument.test.js — Tier 1 (swap Platform.OS per case, as deviceLocale.test.js does)
it('Android with a mobile: straight to that chat', async () => {
  Platform.OS = 'android';
  await shareDocument({ uri: 'file:///c/pdf/INVOICE-2417.pdf', mime: 'application/pdf', filename: 'INVOICE-2417', phone: '+91 98765-43210' });
  expect(Share.shareSingle).toHaveBeenCalledWith(expect.objectContaining({ whatsAppNumber: '919876543210' }));
});

// src/helpers/Share/__tests__/share.config.test.js — pinned off disk, like the five *.config.test.js suites
const read = p => require('fs').readFileSync(require('path').join(__dirname, '../../../..', p), 'utf8');
it('declares WhatsApp on both platforms', () => {
  // Info.plist can hold secrets: assert a boolean, so a red run never prints the file (Phase 2 §1)
  expect(/LSApplicationQueriesSchemes[\s\S]*?<string>whatsapp<\/string>/.test(read('ios/dzzlo_oms_app/Info.plist'))).toBe(true);
  expect(read('android/app/src/main/AndroidManifest.xml')).toMatch(/<package android:name="com\.whatsapp" \/>/);
});
```

Add the iOS case (`Share.open` called, `shareSingle` never) and a `whatsAppNumber.test.js` for `'098765 43210'`, `'(+91) 98765 43210'`, a Delhi landline (`'011 2345 6789'` → `null`) and `undefined`. Digits alone cannot tell a landline whose STD code starts with 6–9 (Bhopal's 0755) from a mobile — the customer record should say which number is the mobile. Run `APP_ENV=testing npx jest share whatsAppNumber`: red first, then the helper, the facade and the two declarations.

## 3. Native PDF — `NativePdf`

### 3.1 Why not the ready-made options

- **react-native-html-to-pdf 1.3.0** — never called, no release since 2025-09-04, and the sources conflict on New Architecture (the Directory says TurboModule; a 2026 guide calls it slowly maintained, with base64-only images and inconsistent iOS/Android margins). [[02-phase-2-dependency-diet]] removes it.
- **expo-print 57.0.2** — maintained, and on Android it uses the same WebView print adapter as this phase. But it needs `expo` installed, and no Expo SDK pairs with RN 0.84 or 0.87; the user decided (2026-09-29) that Expo is an optional track on an Expo-paired version only (§6). The Android research had ranked "expo-print in place of html-to-pdf" fourth; that decision supersedes it.

### 3.2 iOS options

| Option | Since | Pagination | Page numbers | Status |
|---|---|---|---|---|
| `UIPrintPageRenderer` + `UIMarkupTextPrintFormatter`, drawn into a `UIGraphicsPDFRenderer` context | 4.2 · formatter: version not captured · 10.0 | A4 pages from the paper rect you set | yes — drawn in the footer | **recommended**; whether the formatter honours the invoice CSS is unverified (Exercise 7.4) |
| `WKWebView.createPDF(configuration:completionHandler:)` | 14.0 | ⚠️ **unverified** — may be one tall page | no | spike only (Exercise 7.5) |

### 3.3 Android options

| Option | Since | Pagination | Page numbers | Caveat |
|---|---|---|---|---|
| Off-screen `WebView` → `createPrintDocumentAdapter(jobName)` → written to a file | API 21 form | the print engine's; honours `@media print` | **no** — Android's docs: no headers, footers or page numbers | writing **without the dialog** means driving the adapter's layout/write steps yourself; their callback objects are not constructible from the public SDK, and the usual workaround leans on non-public API. Isolate it (§3.9). Not verified by this course's research |
| The same adapter → `PrintManager.print()` → the user picks "Save as PDF" | API 21 form | same | no | public API, but the user must pick a printer — right for print, wrong for "share to WhatsApp" |
| `PdfDocument` + Canvas, paginated by hand | API 19 believed, **not confirmed** | yours | yes | rewrites the layout (5–10 days _(est.)_), ignores `@media print` |

expo-print writes its Android PDF through the first row's adapter, so the file route is proven in a maintained library — read its Android source before writing `PdfFileSink`. `PrintedPdfDocument`, named in the notes as a fallback, was not researched further.

### 3.4 The design

```
Render.js:35-80 ─lift─→ src/helpers/Download/pickInvoiceHtml.js    (pure; the viewer and the PDF share it)
      ▼ HTML — amounts already formatted
src/native/pdf.js    createInvoicePdf({ html, fileName, generatedLine, pageLabel })   checks name, appends IST line
      ▼
specs/NativePdf.ts   createPdf(html, { fileName, marginMm, pageLabel }) → { uri, pages, bytes }
   ├─ iOS      HtmlPdfWriter.swift   UIPrintPageRenderer → UIGraphicsPDFRenderer        (main thread)
   └─ Android  HtmlPdfWriter.kt      off-screen WebView → print adapter → cache file    (main thread)
      ▼ file:///…/cache/pdf/INVOICE-2417.pdf → shareDocument() · NativePrint · viewer · deletePdf()
```

- **HTML in, file URL out.** Native code never parses or changes numbers. **Money rule:** amounts arrive already rounded — whole paise, half-up — and the PDF never recomputes them. Be honest about upstream: today's builders still compute some line amounts with floating-point `toFixed(2)` (`src/helpers/Download/invoiceHTML/htmlInvoice.js:36-37`, `gstInvHTML/index.js:131`), which is not half-up in whole paise and can land a paisa off. Fix that test-first in the helpers, as its own task; `NativePdf` can neither cause nor cure it.
- **A4** = 210 × 297 mm = 595.28 × 841.89 pt; one 12 mm margin (house choice); the invoice CSS handles the inside.
- **IST timestamp:** the facade appends one line — "Generated 29 Sep 2026, 11:14 PM IST" — built with the house helpers (`formatDate`, `formatClock` in `src/helpers/DateRange/format.js:66,77`). No time-zone code in Swift or Kotlin.
- **Page numbers:** `pageLabel` comes from `useStrings` (`"Page {n} of {total}"` / `"पृष्ठ {n} / {total}"`); native code substitutes only the two tokens. **Parity:** iOS draws it on every page; **Android v1 has none** (the adapter supports none). Exercise 7.6 tries a CSS page counter (unverified); the `PdfDocument` path is the fallback.
- **The print CSS already exists:** `src/helpers/Download/invoiceHTML/components.js:390-402` sets row-safe `@media print` breaks and repeats `thead` on every page — the print-engine paths honour it, the Canvas path doesn't. The rule at `:386` (`tr.print-friendly td,  {`) is malformed and every engine drops it; don't copy it.
- **The logo is remote** (`components.js:26-27`): offline, the PDF has a hole (the server's puppeteer render waits on remote images too — `networkidle0`). Embed it as a `data:` URI at build time (house choice).
- **Files live in the cache** under `pdf/`, go to share/print/preview, then `deletePdf` (plus a sweep at app start). **Threads:** UIKit printing and the Android `WebView` are main-thread work, and Android must keep the WebView referenced until the file is written.

### 3.5 The spec

```ts
// specs/NativePdf.ts — TypeScript only here; the rest of the app stays JS
import type {TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';
export type PdfOptions = {
  fileName: string;  // "INVOICE-2417": letters, digits, dashes; no extension
  marginMm: number;  // 12 (house choice)
  pageLabel: string; // "Page {n} of {total}" from useStrings; Android v1 ignores it
};
export type PdfResult = {uri: string; pages: number; bytes: number};

export interface Spec extends TurboModule {
  createPdf(html: string, options: PdfOptions): Promise<PdfResult>;
  deletePdf(uri: string): Promise<boolean>; // only inside cache/pdf/
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativePdf');
```

```jsonc
// package.json → codegenConfig.ios.modulesProvider (everything else stays as Phase 1 set it)
"modulesProvider": { "NativeAppInfo": "RCTNativeAppInfo", "NativePdf": "RCTNativePdf", "NativePrint": "RCTNativePrint" }
```

### 3.6 Red, part 1 — Jest

```js
// jest.setup.js — in-house specs call getEnforcing, which throws in Jest unless mocked
jest.mock('./specs/NativePdf', () => ({ __esModule: true, default: { createPdf: jest.fn(), deletePdf: jest.fn(() => Promise.resolve(true)) } }));

// src/native/pdf.js
import NativePdf from '../../specs/NativePdf';
export const PDF_MARGIN_MM = 12;
const SAFE_NAME = /^[A-Za-z0-9][A-Za-z0-9-]{0,63}$/;
const escapeHtml = s => s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
export const createInvoicePdf = ({ html, fileName, generatedLine, pageLabel }) => {
  if (!SAFE_NAME.test(fileName)) return Promise.reject(new Error(`pdf: unsafe file name "${fileName}"`));
  const line = `<p class="dzzlo-generated">${escapeHtml(generatedLine)}</p>`;
  const withLine = html.includes('</body>') ? html.replace('</body>', `${line}</body>`) : html + line;
  return NativePdf.createPdf(withLine, { fileName, marginMm: PDF_MARGIN_MM, pageLabel });
};

// src/native/__tests__/pdf.test.js — Tier 1
it('passes the invoice HTML through untouched, plus one IST line', async () => {
  const html = '<html><body><td class="align_right">1,23,456.50</td></body></html>';
  NativePdf.createPdf.mockResolvedValue({ uri: 'file:///c/pdf/INVOICE-2417.pdf', pages: 2, bytes: 48213 });
  await createInvoicePdf({ html, fileName: 'INVOICE-2417', generatedLine: 'Generated 29 Sep 2026, 11:14 PM IST', pageLabel: 'Page {n} of {total}' });
  const [sent, options] = NativePdf.createPdf.mock.calls[0];
  expect(sent).toBe(html.replace('</body>', '<p class="dzzlo-generated">Generated 29 Sep 2026, 11:14 PM IST</p></body>'));
  expect(options).toEqual({ fileName: 'INVOICE-2417', marginMm: 12, pageLabel: 'Page {n} of {total}' });
});
```

The second case: `fileName: '../x'` rejects with "unsafe file name" and never reaches native code. The first case is the money rule as code: the viewer's HTML and the PDF's differ by one timestamp line and nothing else.

### 3.7 Red, part 2 — native tests

A known HTML with two forced breaks must give **three A4 pages**. If the iOS test stays red after the implementation, the formatter is ignoring CSS page breaks — swap `UIMarkupTextPrintFormatter` for the web view's own print formatter on the same renderer. That is what the red test is for. (Phase 1's test target has no host app; if UIKit printing will not render there, give this one test a hosted target — unverified.)

```swift
// ios/dzzlo_oms_appTests/HtmlPdfWriterTests.swift — the unit-test target added in Phase 1
import XCTest // HtmlPdfWriter.swift is a member of the app and of dzzlo_oms_appTests — Phase 1's hostless target

final class HtmlPdfWriterTests: XCTestCase {
  let threePages = #"<div style="page-break-after: always">1</div><div style="page-break-after: always">2</div><div>3</div>"#
  func testForcedBreaksGiveThreeA4Pages() throws {
    let out = try HtmlPdfWriter().write(html: threePages, fileName: "T-3", marginMm: 12, pageLabel: "Page {n} of {total}")
    let doc = try XCTUnwrap(CGPDFDocument(try XCTUnwrap(URL(string: out["uri"] as? String ?? "")) as CFURL))
    XCTAssertEqual(doc.numberOfPages, 3)
    XCTAssertEqual(try XCTUnwrap(doc.page(at: 1)).getBoxRect(.mediaBox).width, 595.28, accuracy: 0.5) // A4, not Letter
  }
}
```

A JVM test has no real WebView, so Android splits in two: pure rules under plain JUnit, as in Phase 1 (`PdfRequestTest`: 12 mm becomes 472 mils; `"../x"` throws `IllegalArgumentException`), and the page count as an **instrumented** test on the emulator:

```kotlin
// android/app/src/androidTest/java/in/vsyst/dzzlooms/pdf/HtmlPdfWriterTest.kt
@RunWith(AndroidJUnit4::class)
class HtmlPdfWriterTest {
  @Test fun forcedBreaksGiveThreePages() {
    val inst = InstrumentationRegistry.getInstrumentation(); val done = CountDownLatch(1); var file: File? = null
    inst.runOnMainSync { HtmlPdfWriter(inst.targetContext).write(THREE_PAGES, PdfRequest.of("T-3", 12.0),
      onDone = { f, _ -> file = f; done.countDown() }, onError = { throw it }) }
    assertTrue(done.await(20, TimeUnit.SECONDS))
    PdfRenderer(ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)).use { assertEquals(3, it.pageCount) }
  }
}
```

```bash
cd /Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app
xcodebuild test -workspace ios/dzzlo_oms_app.xcworkspace -scheme dzzlo_oms_app -destination 'platform=iOS Simulator,id=<UDID>' -only-testing:dzzlo_oms_appTests/HtmlPdfWriterTests
(cd android && ./gradlew :app:testDebugUnitTest --tests '*PdfRequestTest' && ./gradlew :app:connectedDebugAndroidTest)
```

The instrumented test needs the AndroidX test runner in `app/build.gradle` (`testInstrumentationRunner` and `androidTestImplementation` entries; versions not captured in this course's research). CI runs Jest only, so native results go into the PR description, and screenshots and logs stay in your local evidence folder, outside every repo.

### 3.8 Green — Swift behind the Objective-C++ adapter

```swift
// ios/dzzlo_oms_app/Pdf/HtmlPdfWriter.swift — all the logic; Swift 5 mode like the target; main thread only
import UIKit

@objcMembers public final class HtmlPdfWriter: NSObject {
  public static let a4 = CGRect(x: 0, y: 0, width: 595.28, height: 841.89)
  static func pt(_ mm: Double) -> CGFloat { CGFloat(mm / 25.4 * 72) }
  public func write(html: String, fileName: String, marginMm: Double, pageLabel: String) throws -> NSDictionary {
    let m = Self.pt(marginMm)
    let renderer = LabelledRenderer(paper: Self.a4, margins: UIEdgeInsets(top: m, left: m, bottom: m, right: m), pageLabel: pageLabel)
    renderer.addPrintFormatter(UIMarkupTextPrintFormatter(markupText: html), startingAtPageAt: 0)
    let pages = renderer.numberOfPages
    renderer.prepare(forDrawingPages: NSRange(location: 0, length: pages))
    let data = UIGraphicsPDFRenderer(bounds: Self.a4).pdfData { ctx in
      for page in 0..<pages { ctx.beginPage(); renderer.drawPage(at: page, in: Self.a4) }
    }
    let dir = FileManager.default.temporaryDirectory.appendingPathComponent("pdf", isDirectory: true)
    try FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
    let url = dir.appendingPathComponent("\(fileName).pdf")
    try data.write(to: url, options: .atomic)
    return ["uri": url.absoluteString, "pages": pages, "bytes": data.count]
  }
}

final class LabelledRenderer: UIPrintPageRenderer {
  private let paper: CGRect, printable: CGRect, pageLabel: String
  init(paper: CGRect, margins: UIEdgeInsets, pageLabel: String) {
    self.paper = paper; printable = paper.inset(by: margins); self.pageLabel = pageLabel
    super.init(); footerHeight = HtmlPdfWriter.pt(6)
  }
  override var paperRect: CGRect { paper }
  override var printableRect: CGRect { printable }
  override func drawFooterForPage(at index: Int, in rect: CGRect) {
    let text = pageLabel.replacingOccurrences(of: "{n}", with: "\(index + 1)").replacingOccurrences(of: "{total}", with: "\(numberOfPages)")
    (text as NSString).draw(in: rect, withAttributes: [.font: UIFont.systemFont(ofSize: 8)])
  }
}
```

```objc
// ios/dzzlo_oms_app/Pdf/RCTNativePdf.mm — thin; RCTNativePdf.h declares <NativePdfSpec>
#import "RCTNativePdf.h"
#import <React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h> // before the Swift header, as in Phase 1 §5.6
#import "dzzlo_oms_app-Swift.h" // generated Swift header; name as confirmed in Phase 1
@implementation RCTNativePdf { HtmlPdfWriter *_writer; }
- (instancetype)init { if ((self = [super init])) { _writer = [HtmlPdfWriter new]; } return self; } // no UIKit here
+ (NSString *)moduleName { return @"NativePdf"; }
+ (BOOL)requiresMainQueueSetup { return YES; } // Phase 1's rule; UIKit work happens only in the main-queue block below
- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:(const facebook::react::ObjCTurboModule::InitParams &)params {
  return std::make_shared<facebook::react::NativePdfSpecJSI>(params);
}
// Paste the exact selector from the generated NativePdfSpec protocol (build/generated/ios/) — codegen owns it.
- (void)createPdf:(NSString *)html options:(JS::NativePdf::PdfOptions &)options
          resolve:(RCTPromiseResolveBlock)resolve reject:(RCTPromiseRejectBlock)reject {
  NSString *name = options.fileName(); NSString *label = options.pageLabel(); double margin = options.marginMm();
  dispatch_async(dispatch_get_main_queue(), ^{ // values copied out first: `options` does not outlive this call
    NSError *error = nil;
    NSDictionary *out = [self->_writer writeWithHtml:html fileName:name marginMm:margin pageLabel:label error:&error];
    out ? resolve(out) : reject(@"E_PDF", error.localizedDescription, error);
  });
}
@end
```

`deletePdf:` has the same shape and refuses any path outside `tmp/pdf/`. The adapter stays logic-free, so everything worth testing sits in the Swift class XCTest drives.

### 3.9 Green — Kotlin and `BaseReactPackage`

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/pdf/NativePdfModule.kt
package `in`.vsyst.dzzlooms.pdf // `in` is a Kotlin keyword — backticks, as in MainApplication.kt:1

import `in`.vsyst.dzzlooms.specs.NativePdfSpec // generated into Phase 1's javaPackageName; other imports elided
class NativePdfModule(context: ReactApplicationContext) : NativePdfSpec(context) {
  private val writer = HtmlPdfWriter(context)
  override fun getName() = NAME
  override fun createPdf(html: String, options: ReadableMap, promise: Promise) {
    val req = try { PdfRequest.of(options.getString("fileName") ?: "", options.getDouble("marginMm")) }
              catch (e: IllegalArgumentException) { promise.reject("E_PDF_ARGS", e.message, e); return }
    Handler(Looper.getMainLooper()).post { // WebView is main-thread only
      writer.write(html, req,
        onDone = { file, pages -> promise.resolve(Arguments.createMap().apply {
          putString("uri", Uri.fromFile(file).toString()); putInt("pages", pages); putDouble("bytes", file.length().toDouble()) }) },
        onError = { e -> promise.reject("E_PDF", e.message, e) })
    }
  }
  override fun deletePdf(uri: String, promise: Promise) = promise.resolve(PdfRequest.deleteIfOurs(reactApplicationContext.cacheDir, uri))
  companion object { const val NAME = "NativePdf" }
}

// android/app/src/main/java/in/vsyst/dzzlooms/pdf/HtmlPdfWriter.kt
class HtmlPdfWriter(private val context: Context) {
  private var live: WebView? = null // Android: hold the WebView until the job is written
  fun write(html: String, req: PdfRequest, onDone: (File, Int) -> Unit, onError: (Throwable) -> Unit) {
    val view = WebView(context).also { live = it }
    view.webViewClient = object : WebViewClient() {
      override fun onPageFinished(v: WebView, url: String?) {
        val out = File(File(context.cacheDir, "pdf").apply { mkdirs() }, "${req.fileName}.pdf")
        PdfFileSink.write(v.createPrintDocumentAdapter(req.fileName), req, out,
          onDone = { pages -> live = null; onDone(out, pages) }, onError = { e -> live = null; onError(e) })
      }
    }
    view.loadDataWithBaseURL(null, html, "text/html", "utf-8", null)
  }
}
```

`PdfFileSink` is the **only** class that drives the adapter's layout and write steps into a `ParcelFileDescriptor` for `out`, with ISO A4 attributes and `req.marginMils` — the one home of §3.3's non-public caveat. Keep it under a hundred lines and under the instrumented test, so an Android or WebView update that breaks it fails a test, not a dealer. `NativePdfPackage` is Phase 1's `BaseReactPackage` shape with `NativePdfModule.NAME` (`isTurboModule = true`). In-app modules are not autolinked: in `MainApplication.kt`, inside `PackageList(this).packages.apply { … }`, add `add(NativePdfPackage())` and `add(NativePrintPackage())` next to `add(NativeAppInfoPackage())`, and add `src/native/__tests__/pdf.config.test.js` in the shape of Phase 1's `appInfo.config.test.js` to pin both registrations and both `modulesProvider` entries — red before either exists.

### 3.10 The DZZLO invoice flow

1. **Characterise, then lift.** Pin today's `Render.js:35-80` choice (`PRODUCT` × `Normal`/`Detailed`/`Excel`, `GST` × `Normal`/`Detailed`, and `CASH_REIMBURSE` keeping only orders with `cs_reimb_amt > 0`) in a Tier 1 test, then move it into `src/helpers/Download/pickInvoiceHtml.js`. `Render.js` and the share action both call it, so the viewer and the PDF can only differ by the IST line.
2. **Add the actions** on the invoice screen (`src/screens/Common/_Invoice_/index.js`): **Share** (the PDF/Image sheet of §2.5) and **Print** (§4), beside the existing Email sheet, wired `pickInvoiceHtml` → `createInvoicePdf` → `shareDocument` (or `printFile`, or preview) → `deletePdf` when the sheet closes. Tokens, not hex — `Render.js:25` still defaults `iconColor = '#3568f6'`.
3. **Device run** on the iOS simulator and the Android emulator: open the PDF in the viewer and check page count, A4 size, margins, repeated table headers, the logo, the IST line and — on iOS — "Page n of N". Then a real phone with WhatsApp for §2.3.

## 4. Print — `NativePrint`

react-native-print 0.11.0 (2023-01-22) is unmaintained and not New-Architecture, and expo-print waits for the Expo track. The platform work is about 2 days _(est.)_, so it is its own small module on the same recipe.

```ts
// specs/NativePrint.ts
import type {TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';
export interface Spec extends TurboModule {
  printFile(uri: string, jobName: string): Promise<void>;  // a PDF from NativePdf
  printHtml(html: string, jobName: string): Promise<void>; // straight from the invoice HTML
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativePrint');
```

**The contract:** the promise resolves once the system has the job or has shown its dialog; a cancel is not an error; the app **never** says "Printed" — neither platform reports a finished print reliably (expo-print's docs say its own dialog call resolves as soon as the dialog appears). The facade `src/native/print.js` builds the job name (`INVOICE-2417`) and refuses anything that is not a `file://` URI inside the app's cache.

**iOS — AirPrint.** `ios/dzzlo_oms_app/Print/Printer.swift` (an `@objcMembers` class behind `RCTNativePrint.mm`, like §3.8) sets up a `UIPrintInfo` (`jobName`, `outputType = .general`), hands the PDF's file URL to `UIPrintInteractionController.shared` (4.2) as its `printingItem`, and presents it on the main thread. The app ships for iPad too (`TARGETED_DEVICE_FAMILY = "1,2"`), where the print UI is a popover anchored to a view — check it on the iPad simulator.

**Android — `PrintManager`** (it needs the current `Activity`, not the application context):

- `printHtml`: off-screen `WebView`, wait for `onPageFinished`, hand `createPrintDocumentAdapter(jobName)` to `PrintManager.print()`, keep the WebView referenced until the job exists. Android's documented path — public API end to end, with "Save as PDF" among the printers.
- `printFile`: a small `PdfFilePrintAdapter : PrintDocumentAdapter` that reports one document and copies the PDF's bytes into the destination the system passes to `onWrite`. Here the **system** constructs the callbacks, so §3.3's caveat does not apply: printing is public API; only the dialog-free file write is not.

**Tests:** Jest for the facade (job name, refused URIs, cancel resolves); a plain-JUnit test for the pure `copy(InputStream, OutputStream)` helper the adapter calls, with temp files; the dialogs are a device check — the iOS simulator's print sheet, the emulator's "Save as PDF", one real office printer on Wi-Fi.

### 4.1 Deferred: Bluetooth thermal receipt printers

Forecourt slips on 58/80 mm printers are a real ask — a Vyapar 3★ (2026-07-26) wants a thermal option for delivery challans, and IndianOil's delivery app prints cash memos at the doorstep. The constraints:

| | iOS | Android |
|---|---|---|
| Radio | Classic SPP only with **MFi-certified** accessories, and cheap printers aren't — a Classic-only printer "will never show up in an iOS scan"; dual-mode BLE printers work (Star Micronics sells "dual chip Apple MFi certified" models) | Classic RFCOMM (SPP) or BLE |
| Permissions | a Bluetooth purpose string (5.1.1(ii)) | 12+: `BLUETOOTH_SCAN` (with `neverForLocation`) and `BLUETOOTH_CONNECT`; 11 and below: legacy `BLUETOOTH`/`BLUETOOTH_ADMIN` (`maxSdkVersion="30"`) plus `ACCESS_FINE_LOCATION` to scan; `CompanionDeviceManager` (API 26+) pairs through system UI with no location permission |
| When targeting Android 17 (API 37) | — | RFCOMM `InputStream.read()` returns −1 when the link drops; LAN printers need the new `ACCESS_LOCAL_NETWORK` unless a system device picker is used |
| Bytes | ESC/POS from a JS encoder | same |

Libraries, 2026-09-29: react-native-earl-thermal-printer 2.0.1 (2026-08-10, TurboModule, BLE, 63 downloads/wk); react-native-star-io10 1.14.0 (2026-09-15, old architecture, Star hardware only); react-native-esc-pos-printer 4.5.0 (2025-10-24, TurboModule, Epson only); react-native-ble-manager 12.5.3 (2026-09-21, TurboModule, generic BLE); react-native-bluetooth-classic 1.73.0-rc.17 (release candidates only, not New-Arch).

**Verdict: defer.** Nothing says which printers DZZLO's dealers own. When one is named, build against that model: a JS ESC/POS encoder plus BLE on both platforms, and an own RFCOMM module on Android for Classic-only printers (that most cheap 58/80 mm printers are Classic-only is itself unverified) — 2–3 weeks plus a device matrix _(est.)_.

## 5. Import and export

### 5.1 Import — @react-native-documents/picker 12.0.2

The system picker on both platforms (`UIDocumentPickerViewController`, iOS 8.0; SAF `ACTION_OPEN_DOCUMENT`, API 19), with no permission, and it lists Files and iCloud Drive — what App Review 2.5.15 asks for. Use it to attach a supplier PDF or a bank CSV. Its call names were not captured in the notes, so they live in one wrapper, `src/helpers/Files/documents.js`; screen tests mock that wrapper, never the library.

### 5.2 Export

| Target | iOS | Android |
|---|---|---|
| A place the user picks | export picker, `init(forExporting:asCopy:)` (14.0) | SAF `ACTION_CREATE_DOCUMENT` (API 19) — "doesn't require any system permissions" |
| Downloads | — | `MediaStore.Downloads`, **API 29+**: no permission for files the app owns; write with `IS_PENDING` and `RELATIVE_PATH` |
| Downloads on API 24–28 | — | legacy `WRITE_EXTERNAL_STORAGE` with `android:maxSdkVersion="28"` — or route 24–28 through SAF or the share sheet (house choice: the latter) |

⚠️ **Unverified:** whether @react-native-documents/picker 12.0.2 can **export or save** in its free MIT build, and which features are sponsor-only — its docs pages did not render the API for the researcher. Exercise 7.7 answers it; if it cannot, the fallback is one more thin module on this recipe, named when the audit says so. Don't revive `Download/Invoice.js`'s runtime `WRITE_EXTERNAL_STORAGE` request. If our own code ever fires `ACTION_SEND` for an app file, it needs an AndroidX `FileProvider` (`exported="false"`, `grantUriPermissions="true"`, a paths XML with `cache-path`); the merged manifest already holds `RNCWebViewFileProvider` from react-native-webview, so ours gets its own authority, `${applicationId}.fileprovider`.

### 5.3 The Files app on iOS

```xml
<!-- ios/dzzlo_oms_app/Info.plist — only if dealers should browse kept exports in Files -->
<key>LSSupportsOpeningDocumentsInPlace</key><true/>  <!-- iOS 2.0 -->
<key>UIFileSharingEnabled</key><true/>               <!-- iOS 3.2 -->
```

Together these are the usual way to show the app's `Documents/` folder under "On My iPhone" (confirm on a device). Only what the dealer chose to keep goes in `Documents/` — never caches, never tokens. `UTExportedTypeDeclarations` (5.0) is for apps that own a file type; DZZLO doesn't.

### 5.4 CSV and XLSX

**CSV: JS, not native** — string building, a pure Tier 1 helper:

```js
// src/helpers/Files/csv.js — RFC 4180 quoting; amounts go in exactly as the API sent them
const cell = v => { const s = v == null ? '' : String(v); return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
export const toCsv = (columns, rows) =>
  '\uFEFF' + [columns.map(c => cell(c.title)), ...rows.map(r => columns.map(c => cell(r[c.key])))]
    .map(line => line.join(',')).join('\r\n');
```

The `\uFEFF` byte-order mark is a house choice so Excel on Windows reads ₹ and Hindi names as UTF-8 (Excel behaviour, not from the research). Money columns are the API's formatted strings — never re-rounded with float arithmetic. Write the string into the cache with react-native-file-access 4.0.4 (its write call per its README — not captured in the notes), then share or export it.

**XLSX: a JS library, with a size warning.** The research evaluated no XLSX library, so this is a spike: measure the release bundle before and after (`npx react-native bundle --platform android --dev false …`), and prefer CSV for anything Excel opens anyway. Today's "Excel" (`xlsxInvSummary`, `xlsxTCSTDS_month_Summary`) is **HTML tables** in a WebView, not files. PetroByte, a pump-software competitor, exports its DSR "in PDF, Excel, and CSV formats" — CSV first is not behind the market.

### 5.5 Preview — Quick Look

@react-native-documents/viewer 4.0.1 hands the file to `QLPreviewController` (iOS 4.0) and to the installed viewer on Android (`ACTION_VIEW`). Use it before sending — the dealer sees what the customer gets — and in the device run of §3.10. An in-app Android viewer (androidx.pdf 1.0.0-beta01 per search results, partly unverified) can wait.

### 5.6 Permissions, App Review and Play Data safety

| Feature | iOS | Android manifest | Play Data safety |
|---|---|---|---|
| Share (§2) | `LSApplicationQueriesSchemes` only | `<queries>` entries | nothing new |
| Import (§5.1) | none | none (SAF) | "Files and docs" **only if** the file is uploaded to DZZLO |
| Export / save (§5.2) | none | none (SAF; MediaStore on 29+) | files kept on the phone are probably not "collected" (inference) |
| PDF, print (§3, §4) | none | none | nothing new |
| Thermal printer (deferred) | Bluetooth purpose string | `BLUETOOTH_SCAN` / `BLUETOOTH_CONNECT` | none found |

This phase adds **no** runtime permission on either platform — the point of system pickers and share sheets.

## 6. After the upgrade to 0.87 / optional Expo track

> **After the upgrade to 0.87:** the Jest preset becomes `@react-native/jest-preset` (from 0.85) — the `jest.setup.js` mocks above stay, the `preset` line in `jest.config.js` changes. AGP 9 and compileSdk 37 arrive with 0.87: rebuild the Kotlin modules and re-run the instrumented PDF test first, because a WebView or print change shows up there before anywhere else. With SwiftPM (experimental in 0.87) the `.mm` adapters must use framework-style `#import <React/…>` includes. The strict TypeScript API makes deep `react-native/Libraries/*` imports a type error; these specs import only from `'react-native'`.

> **Optional Expo track (only on an Expo-paired React Native version):** `expo-print` 57.0.2 would replace `NativePdf` and `NativePrint` — `printToFileAsync()` writes a PDF to the cache through the same Android WebView adapter (default 612 × 792 pt, i.e. US Letter: pass A4's 595 × 842), honours CSS `@page` margins and can return base64; `printAsync()` resolves as soon as the dialog appears. `expo-sharing` 57.0.22 would replace the generic sheet (react-native-share stays for WhatsApp-by-number). **Why not now:** Expo modules need `expo` installed (`npx install-expo-modules@latest` edits the Podfile and `AppDelegate.swift`, moves bundling to Expo CLI, and the current docs set iOS 16.4 as the deployment target), and no SDK pairs with 0.84 or 0.87 — SDK 56 ↔ 0.85.3, 57 ↔ 0.86.3, 58 ↔ 0.88 RC. Our own modules never move to Expo.

## 7. Exercises

**7.1 — Pin the starting point.** Re-check every file:line of §1 against the current HEAD with `grep -n` and save the output to a file in your local evidence folder, outside every repo. _Anything that moved goes into the Lab Notes._

**7.2 — Share, red → green.** Write `whatsAppNumber.test.js`, `shareDocument.test.js` and `share.config.test.js` first and watch them fail; then add the helper, the facade and the declarations. _The red and green runs go in the PR description._

**7.3 — WhatsApp on real phones.** On Android, share a test PDF to your own number: does the chat open with the file attached? On an iPhone, confirm #1699's behaviour and that the share-sheet path works. _A dated observation in the Lab Notes._

**7.4 — `NativePdf`, red → green.** The Jest facade test, then XCTest and both Android tests (all red), then the Swift, Objective-C++ and Kotlin. Green = three pages from the forced-break fixture on both platforms. _If iOS stays red, swap the formatter and record which one passed._

**7.5 — Settle a research gap.** Spike `WKWebView.createPDF` (iOS 14.0) on a three-page invoice: one tall page, or A4 pages? _The answer removes an "unverified" from this course._

**7.6 — Android page numbers.** Print a test HTML with a CSS page counter through the WebView adapter on an Android 16 emulator. _Numbers appear → Android v1 gains them and §3.4's parity note changes; none → the gap stays, stated._

**7.7 — The picker export audit.** Read the 12.0.2 package source, not the website: does the free build expose export or save on both platforms? _Yes/no plus the file you read — it decides whether a thin export module is needed._

**7.8 — Image and PDF.** Capture the invoice screen with react-native-view-shot on both platforms. _WebView content or a blank box? Keep the screenshot pair in your local evidence folder._

**7.9 — The paisa hunt.** A Tier 1 characterisation test that feeds `htmlInvoice` a quantity × rate landing on a half paisa and compares `toFixed(2)` with whole-paise half-up. _A red test handed to the helpers task, not fixed here._

## Lab Notes

**Verified by reading, 2026-09-29** — no build, no install, nothing changed in either repo. App `release/v1_79`, audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30): every file:line in §1; `package.json` has `react-native` 0.84.1, `react-native-html-to-pdf` ^1.3.0, `react-native-webview` ^13.16.1 and no `codegenConfig`; `Info.plist` has no `LSApplicationQueriesSchemes`; `AndroidManifest.xml` declares only `INTERNET` and no `<queries>`; `MainApplication.kt` is `` package `in`.vsyst.dzzlooms `` with the template `add(MyReactNativePackage())` comment; print CSS at `components.js:390-402`, remote logo at `:26-27`. API `release/v1_79` HEAD `9690be9`: puppeteer PDFs in `api_v3/services/invoice/htmlPdf/fileBuffer.js`, used only for email attachments; invoice pages 30 × 42.4 cm; no PDF-download or upload route.

**Open — not verified by this course's research:** react-native-share's file-to-number on Android (7.3), its file option names and #1556 in 12.3.1; the WhatsApp `<queries>` entries (inference); `WKWebView.createPDF` pagination (7.5); `UIMarkupTextPrintFormatter`'s version and CSS fidelity (7.4); the dialog-free adapter write's reliance on non-public API (re-test on every Android release); `PdfDocument`'s API level (believed 19); picker export in the free build (7.7); view-shot on a WebView (7.8); and the member names used in the skeletons (`drawFooterForPage`, `footerHeight`, `CGPDFDocument`, `PdfRenderer`, `UIPrintInfo`, `printingItem`, `loadDataWithBaseURL`) — the compile and the device run settle those.
