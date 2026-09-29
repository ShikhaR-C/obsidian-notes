# Phase 10 — Capstones

> Level: Capstone | Three projects, one per wave of the course. Each is a feature a dealer or customer would notice, not an exercise. Build them in order — B and C reuse what A proves: the spec → facade → native → device loop, the XCTest bundle and JUnit set-up, and the config pins.

---

## 1. Before You Start

All three capstones assume [[01-phase-1-foundations]] and [[02-phase-2-dependency-diet]] are done:

- `package.json` has a `codegenConfig`, `specs/` exists, and `NativeAppInfo` is live — so the pattern (TypeScript spec → codegen → Objective-C++ adapter + Swift on iOS → Kotlin + `BaseReactPackage` on Android → JS facade in `src/native/` with a Jest mock of the spec) has been walked once, and `src/native/__tests__/appInfo.config.test.js` pins the wiring.
- The app has a unit-test bundle in Xcode (`dzzlo_oms_appTests`) and `testImplementation` for JUnit in `android/app/build.gradle` — neither exists on 2026-09-29; Robolectric joins in [[05-phase-5-notifications-and-live-status]] §6.6.
- `react-native-html-to-pdf` and its dead importers are gone, the manifest has its `<queries>`, and the archive's `APP_ENV` is pinned by a test.

Each capstone is a string of **test-first pairs**: the red test is named first, then what turns it green. The names below are the ones the phases use, so a capstone is the phases' pieces joined end to end. Nothing in CI compiles native code, so every native step ends with a recorded device run. The work waits for the user's "start", and nothing is committed, merged or pushed without the user's word.

| Capstone | Wave | Phases | Our code | Effort _(est.)_ |
| --- | --- | --- | --- | --- |
| A — Invoice → native PDF → WhatsApp | 1 | 1–3 | `NativePdf`, `NativePrint`, `shareDocument` | Phase 3: 6–11 working days; the notes' separate figures sum to ≈ 8–14 |
| B — Order status → push → Live Activity + Live Update | 2 | 5, 8 | `DzzloWidgets` (Live Activity), Kotlin `NotificationServiceExtension`, the link map | ≈ 12–20 days in the app + API work (Phase 5 in full: 3–5 weeks) |
| C — Daily Summary widget + "outstanding balance" intent | 4 | 6 | `NativeSharedStore`, `NativeShortcuts`, `DzzloWidgets` (widget + intent), `DailySummaryWidget` | ≈ 15–27 days + the intent (Phase 6 in full: 4–7 weeks) |

---

## 2. Capstone A — Invoice → Native PDF → WhatsApp

**Deliverable:** from an invoice, voucher or TCS/TDS summary the app already renders, a dealer taps **Share** and picks **PDF** or **Image**, or taps **Print**. The customer receives an A4 `INVOICE-<number>.pdf` (or a PNG) in WhatsApp; the office printer gets the same pages. On Android the customer's chat opens pre-selected; on iOS the share sheet opens with WhatsApp in it and the dealer picks the chat.

This is rank 1 in the product ranking ([[00_README]]): Indian SMB apps compete on WhatsApp sharing, and reviews ask for **both** a picture and a PDF. Today the app can view these documents and ask the server to **email** them (`useEmail_invMutation` → `invs/a/email`), but it cannot share, save or print them — `react-native-html-to-pdf` was imported and never called, and no live file imports `Share`.

### Server PDF or device PDF — side by side

The API already renders invoice PDFs: puppeteer in `dzzlo_oms_api` `api_v3/services/invoice/htmlPdf/fileBuffer.js`, on a 30 × 42.4 cm page (`api_v3/services/invoice/htmlTemplates/index.js`), attached to that email (`api_v3/controllers/App/email.js`). No route returns the PDF to the phone. ([[03-phase-3-files-share-and-pdf]] read this on API `release/v1_79`, HEAD `9690be9`; re-checked read-only for this capstone.) So the first decision is the user's:

| | Server PDF — a new endpoint returning what the email already renders | Device PDF — `NativePdf` (this capstone) |
| --- | --- | --- |
| Works at a pump with no signal | no | yes |
| One template for email and share | yes | no — the app's `src/helpers/Download/*` and the API's `htmlTemplates/*` are separate copies that drift |
| Paper | 30 × 42.4 cm today (about A3) | A4 (house choice) |
| API change | yes — needs the user's approval | none |
| Native code in the app | none | `NativePdf` on both platforms |

The capstone builds the device path, as Phase 3 does: it works offline and is the native-module lesson. If the user chooses one template instead, steps 3–5 below become an endpoint plus a download into the same cache folder — and the share, print, preview and clean-up steps stay exactly as they are.

### Pipeline

```
Render.js:35-80 ─lift─► src/helpers/Download/pickInvoiceHtml.js     pure; the WebView and the PDF share it
        │  HTML — amounts as the builders format them today
        ▼
src/native/pdf.js     createInvoicePdf({ html, fileName, generatedLine, pageLabel })
        │               checks the name, appends one IST "Generated …" line
        ▼
specs/NativePdf.ts    createPdf(html, { fileName, marginMm, pageLabel }) → { uri, pages, bytes }
   ├─ iOS      HtmlPdfWriter.swift   UIPrintPageRenderer (4.2) → UIGraphicsPDFRenderer (10.0), A4
   └─ Android  HtmlPdfWriter.kt      off-screen WebView → print adapter (API 21 form) → cache file
        ▼
file:///…/cache/pdf/INVOICE-<no>.pdf
        ├─► Share PDF ─── shareDocument({ uri, mime, filename, phone })     src/helpers/Share/shareDocument.js
        │                   Android: react-native-share shareSingle, WHATSAPP + whatsAppNumber → chat pre-selected
        │                   iOS: the share sheet (UIActivityViewController, iOS 6.0) → the dealer picks the chat
        ├─► Share image ─ react-native-view-shot 6.0.1 → PNG in the cache → the same shareDocument()
        ├─► Print ─────── NativePrint printHtml(): UIPrintInteractionController (iOS 4.2) · PrintManager
        ├─► Preview ───── @react-native-documents/viewer 4.0.1 (Quick Look / the OS viewer)
        └─► deletePdf(uri) afterwards, plus a sweep of cache/pdf/ at app start
```

### Why each choice

- **Keep the HTML.** The invoice, GST invoice, payment advice, receipt voucher and TCS/TDS builders already exist and already render in `<WebView source={{ html }} />` (`screens/Common/_Invoice_/Render.js:5-11,75,92-94`). `NativePdf` prints that string; native code never parses or recomputes a number.
- **Be honest about the money upstream.** The PDF shows what the builders produce, and some of them still compute line amounts with floating-point `toFixed(2)` (`src/helpers/Download/invoiceHTML/htmlInvoice.js:36-37`, `gstInvHTML/index.js:131`) — not the house rule of whole paise, half-up. Moving them to that rule is its own red → green change; here the check is only that the PDF matches the screen to the paisa.
- **A4 on purpose.** A4 is 595.28 × 841.89 pt with one 12 mm margin (house choice). iOS draws with `UIPrintPageRenderer` into a `UIGraphicsPDFRenderer` context, Phase 3's choice, because whether `WKWebView.createPDF` (iOS 14.0) paginates to A4 or makes one tall page is unverified — and defaults are not A4 anyway (`expo-print` defaults to 612 × 792 pt).
- **Page numbers differ.** iOS draws "Page n of total" (`"पृष्ठ {n} / {total}"` in Hindi) on every page; Android's print adapter supports none, so Android v1 has none. That is a recorded parity gap, not an oversight.
- **WhatsApp differs by platform.** `shareSingle` supports `Share.Social.WHATSAPP` with a `whatsAppNumber` on both platforms per the library's docs, but an open iOS issue (#1699) says a file cannot go straight to a WhatsApp contact, and another (#1556) reports PDFs arriving without an extension in release builds. So: `shareSingle` on Android, the share sheet on iOS. WhatsApp Business is an Android-only target.
- **The image.** `react-native-view-shot` captures the invoice view to a PNG. Whether it captures a WebView's content on both platforms is **not verified** (Phase 3, Exercise 7.8); if it doesn't, share a summary card drawn in React Native now, or add a page-to-image method to `NativePdf` later.

### Draws on

[[01-phase-1-foundations]] (spec, codegen, facade, test targets) · [[02-phase-2-dependency-diet]] (html-to-pdf removed, `<queries>`) · [[03-phase-3-files-share-and-pdf]] (every name below). Stretch: [[08-phase-8-instant-experiences-and-links]] for a UPI QR on the invoice.

### Build order (test-first)

1. **Config pin — red.** Add `src/native/__tests__/pdf.config.test.js` (Phase 3 §3.9, in the shape of Phase 1's `appInfo.config.test.js`): `codegenConfig.ios.modulesProvider` maps `NativePdf` → `RCTNativePdf` and `NativePrint` → `RCTNativePrint`; `MainApplication.kt` adds both packages; `react-native-html-to-pdf` is absent from `package.json` and `Podfile.lock`. It stays red until steps 4–7 land.
2. **Lift the picker — Jest red.** `src/helpers/Download/pickInvoiceHtml.js` takes the builder choice out of `Render.js:35-80`, so the WebView and the PDF can never pick different HTML. **Green**, with the WebView switched to it.
3. **Facade — Jest red (Tier 1).** `src/native/__tests__/pdf.test.js` mocks `specs/NativePdf`: `createInvoicePdf({ html, fileName: 'INVOICE-2417', generatedLine, pageLabel })` calls `createPdf` with the HTML plus one IST "Generated …" line and exactly `{ fileName: 'INVOICE-2417', marginMm: 12, pageLabel }`; a bad name is refused before native is called; a native rejection becomes one typed error that callers catch (since RN 0.82 an uncaught rejection raises `console.error`). **Green:** `src/native/pdf.js`.
4. **Swift — XCTest red.** `ios/dzzlo_oms_appTests/HtmlPdfWriterTests.swift`: HTML with two forced page breaks gives **three** pages, and the first page's media box is 595.28 pt wide — A4, not Letter. If it stays red, the formatter is ignoring CSS page breaks; swap `UIMarkupTextPrintFormatter` for the web view's own print formatter on the same renderer (first rule out Phase 3 §3.7's host-less-bundle caveat, unverified). **Green:** `ios/dzzlo_oms_app/Pdf/HtmlPdfWriter.swift` behind `RCTNativePdf.mm` in the same folder.
5. **Kotlin — JUnit red, then an instrumented red.** `PdfRequestTest` (plain JUnit, Phase 1's set-up): 12 mm becomes 472 mils; a `"../x"` file name throws. A JVM test has no real WebView, so the page count is an instrumented test, `android/app/src/androidTest/java/in/vsyst/dzzlooms/pdf/HtmlPdfWriterTest.kt`. **Green:** `HtmlPdfWriter.kt`, its `PdfFileSink`, `NativePdfModule.kt` and `NativePdfPackage.kt`, added in `MainApplication.kt` (in-app modules are not autolinked). The WebView must stay referenced until the print job is created, or printing may fail.
6. **Share — Jest red.** `src/helpers/Share/__tests__/whatsAppNumber.test.js` (`'+91 98765-43210'`, `'098765 43210'`, `'(+91) 98765 43210'` → `'919876543210'`; a landline and `undefined` → `null`) and `shareDocument.test.js` (Android calls `shareSingle` with that number; iOS opens the share sheet and never calls `shareSingle` — swap `Platform.OS` per case, as `deviceLocale.test.js` does). **Green:** `whatsAppNumber.js`, `shareDocument.js`.
7. **Print — Jest red.** `src/native/print.js`'s `printHtml` with `specs/NativePrint` mocked: the job name is the invoice number; the promise resolves when the system dialog is presented — it cannot know whether the dealer actually printed. **Green:** `ios/dzzlo_oms_app/Print/` — `RCTNativePrint.mm` + `Printer.swift` over `UIPrintInteractionController` (iOS 4.2); Kotlin over `PrintManager.print()` with the WebView adapter.
8. **Screen — Tier 3 red.** The invoice screen's **Share** opens a v2 `Sheet` (`src/components/v2/Sheet.js`) with **PDF** and **Image**, next to **Print**; labels from `useStrings` in en and hi; the layout holds at 320 dp × fontScale 1; colours from `src/theme` tokens. **Green.**
9. **Clean-up — Jest red.** After share, print or preview the facade calls `deletePdf(uri)`, and a sweep clears `cache/pdf/` at app start; native `deletePdf` refuses any path outside that folder. **Green.**
10. **Device runs** — the acceptance lists below, recorded the way the house records simulator and emulator runs.
11. **Stretch — UPI on the invoice.** A `upi://pay?pa=…&pn=…&am=…&cu=INR&tr=<invoice no>` QR and a "Pay" link in the HTML, built by Phase 8's `src/helpers/Links/upi.js`. Payment is confirmed from the dealer's PSP or bank data on the server, never from what a UPI app returns to the phone.
12. **Ask for a rating after the third successful share — Jest red.** Once `shareDocument` (step 6) resolves, the invoice screen calls `maybeRequestReview('invoice_shared')` and does not wait for it ([[09-phase-9-security-privacy-and-release]] §9.5). A Tier 3 case with the stored state seeded eight days old: the first two shares ask nothing; the third waits 2 s and calls the mocked `requestStoreReview` exactly once; a fourth share the same day asks nothing — the count starts again after every ask, and this version has had its one. The caps are Phase 9's: at least 3 successes and 7 days since first launch, once per app version, at least 30 days apart, at most 3 asks in 365 days, nothing within 7 days of a user-visible error, and never from a button — the sheet and the card are the OS's, unaltered, with no question before them and no reward. **Green:** the one call in the share handler. This trigger only exists once [[03-phase-3-files-share-and-pdf]] restores sharing — today the only share handler is commented out (`ShowInvoice.js:284-338`) and no live file imports `Share`. On Android a resolved share says little (React Native's own `Share` always reports `sharedAction` there; what react-native-share 12.3.1 resolves was not checked), so there the share counts as one success of three, not a verdict.

### Acceptance checks

**Android** — a real phone with WhatsApp, plus an API 24–28 emulator for the pre-scoped-storage path:

- [ ] The PDF opens in the OS viewer: A4 pages, every line item, no clipped totals.
- [ ] It is `INVOICE-<number>.pdf` under the app's `cache/pdf/`; the merged manifest gains **no** storage permission (config pin).
- [ ] **Share → PDF** opens WhatsApp on the customer's chat with the file attached; WhatsApp Business works too; the receiving phone opens it as a PDF.
- [ ] The share sets `FLAG_GRANT_READ_URI_PERMISSION` explicitly — from Android 18, `ACTION_SEND` stops granting URI permissions automatically. Check whether `react-native-share` 12.3.1's own FileProvider already covers the cache path before declaring another (not verified in the notes).
- [ ] **Print** opens the system dialog, and "Save as PDF" works.
- [ ] Release build, not only debug. A process kill mid-share (`adb shell am kill in.vsyst.dzzlooms`) does not break the next export.
- [ ] `check_elf_alignment.sh` output is unchanged — a Kotlin-only module adds no `.so`.

**iOS** — a real iPhone with WhatsApp, plus the oldest supported iOS (the 15.1 floor):

- [ ] The share sheet lists WhatsApp; after the dealer picks the chat, the file arrives **as a PDF with its extension** in a Release build (the #1556 check).
- [ ] Nobody expects a direct-to-contact file send (#1699): acceptance is "the dealer picks the chat, the PDF arrives".
- [ ] Every page carries "Page n of total", in English and in Hindi.
- [ ] AirPrint opens from **Print**; Quick Look previews before sharing.
- [ ] A screenshot of the share sheet under the iOS 27 SDK (Liquid Glass cannot be opted out).

**Both:**

- [ ] Amounts in the PDF match the screen to the paisa — the same HTML, nothing recomputed.
- [ ] The image option works, or its fallback is recorded in Lab Notes.
- [ ] The Share sheet fits at 320 dp × fontScale 1 in en and hi, and at the largest accessibility size.
- [ ] `yarn test` is green, and the mutation smoke holds: change `marginMm` in `pdf.js` and step 3 goes red.

### Review and policy

- **Apple** — 2.5.15: any picker includes Files and iCloud documents (the system pickers do). 5.1.1: no new data access; sharing is user-initiated, so no purpose string. **Privacy manifest:** only if the Swift code touches a required-reason API — sweeping old exports by file date is `FileTimestamp`, which the app manifest already declares (C617.1).
- **Play** — no permission form: cache files, FileProvider and the system share sheet need none. Data safety: files kept on the device are probably not "collected" (inference) — nothing changes unless a PDF is uploaded.
- **Ratings (step 12)** — Apple 5.6.1: StoreKit's own sheet through the provided API, never a custom review prompt; 3.2.2(x): sharing never waits on a rating; 5.6.3 and the guidelines' Introduction: no paid, incentivised, filtered or fake feedback. Play's "User Ratings, Reviews, and Installs" policy and the In-App Review guidelines: no question before or during the card, no button that triggers it, the card surfaced as-is, no incentive. The Help screen's "Rate DZZLO" row opens the store page instead ([[09-phase-9-security-privacy-and-release]] §9.6).
- **Out of scope:** automated WhatsApp messages from the server (WhatsApp Business Platform utility templates, about ₹0.115 + GST each — sources disagree, one says ₹0.145) are API work.

### Effort _(est.)_

Phase 3 puts its whole build at 6–11 working days on both platforms. The notes' separate figures: share + summary image 2–4 days, PDF wrap 2–3 days and print ~2 days (ecosystem note); PDF + AirPrint 4–7 days on iOS (iOS note); export, save and share 2–3 days on Android (Android note) — summed, **≈ 8–14 working days**, plus 20–30 % for Android device checks on Samsung, Xiaomi and a Pixel.

---

## 3. Capstone B — Order Status → Push → Live Activity + Live Update

**Deliverable:** when a dealer dispatches the tanker for an order, the customer's phone shows the order's progress on the Lock Screen — a Live Activity with Dynamic Island on iOS, a promoted Live Update with a status-bar chip on Android 16 and later — updated by push until delivery, when it ends. Every step is also an ordinary notification that opens the order when tapped. Older phones get the ordinary notifications only.

This is rank 3 in the product ranking: dealers already use oil-company apps where "place indent → live status → confirm delivery" is standard (IndianOil For Business, HP Buddy), and Swiggy collapsed five order notifications into one Live Activity (search snippet).

### The state machine

```
placed ──────► confirmed ──────► dispatched ──────► delivered
  │               │                  │                   │
  │               │                  │                   └─ END the live surface
  │               │                  │                      push "Delivered" → opens the invoice
  │               │                  └─ START the live surface (the tanker is moving)
  │               │                     push-to-start on iOS 17.2+ · event "start" on Android
  │               └─ push to the customer: "Order #… confirmed" (ordinary)
  └─ push to the dealer: "New order #…", time-sensitive

cancelled (any time before delivered) ─► END the live surface if started · ordinary push
```

**Why the live surface starts at `dispatched`, not `confirmed`:** a Live Activity stays active for at most 8 hours (and on the Lock Screen for at most 12), which fits a tanker trip but not a next-day order; Android's Live Update criteria want something ongoing, user-initiated and time-sensitive, and name **package tracking** as inappropriate — an order waiting days for a slot is exactly that. The card still shows all four stages, with placed and confirmed drawn as done: `ProgressStyle` segments on Android (API 36), SwiftUI on iOS. The dynamic state is two fields, `stage` and `etaText`; the ETA is computed on the server, because the card can neither fetch nor locate.

### Pipeline

```
API: order status changes ── the contract below ──► OneSignal
      │                                                  │
      │ iOS: Live Activity push (OneSignal holds the     │ Android: push data carrying `live_notification`
      │      ActivityKit tokens; .p8 key)                │
      ▼                                                  ▼
DzzloWidgets — DzzloOrderLiveActivity.swift       NotificationServiceExtension.kt (OneSignal)
  ActivityKit (iOS 16.1); push-to-start (17.2)      LiveOrderUpdate.parse → LiveOrderNotification.build
  Lock Screen + Dynamic Island                      API 36+: ProgressStyle, promotion requested
  tap URL: DzzloLinks.order(id)                     API 24–35: NotificationCompat progress, same ID
      │                                                  │
      └────────── tap: dzzlooms://orders/<id> ───────────┘
                         │  src/navigation/linking.js (Phase 8): LINK_PREFIXES, linkingConfigFor(role);
                         │  a tap before the role drawer mounts waits in parkLink until replayParkedLink
                         ▼
          the order screen  ◄── ordinary push taps: routeForNotification(data, role) → { kind: 'link', path }
                                → Linking.openURL(`dzzlooms://${path}`), resolved by the same table
```

### The contract the API must implement

The app never sends a push. The API does, through OneSignal — so this table is a contract for the API repo, built and tested there.

| Event | iOS (OneSignal Live Activities) | Android (`live_notification` in the push data) | Ordinary push (both) |
| --- | --- | --- | --- |
| placed | — | — | to the dealer: "New order #…", `ios_interruption_level: "time-sensitive"` |
| confirmed | — | — | to the customer: "Order #… confirmed" |
| dispatched | **start** — push-to-start (iOS 17.2+) via `POST /apps/{app_id}/activities/activity/DefaultLiveActivityAttributes` with `event_attributes` and `event_updates` | **start** — `{ key: "order-<id>", event: "start", event_attributes, event_updates }` | "Tanker dispatched" |
| ETA changes | update (static + dynamic data ≤ 4 KB) | `event: "update"`, same `key` and collapse ID, short `ttl` | none (4.5.3: no spam) |
| delivered | **end** | `event: "end"` → the extension cancels | "Delivered — tap for the invoice" |
| cancelled | end, if started | end, if started | "Order cancelled" |

Rules the API follows:

- **Payload:** order number, product (HSD / MS), litres, `stage`, `etaText` — **no rupee balances** (4.5.4: no sensitive or confidential information in pushes). Ordinary pushes carry the role keys today's drawers read plus the new link, e.g. `{ "dealer": "NewOrder", "orderId": "…", "path": "orders/…" }`, so they keep working before the link map lands.
- **Every change is also a visible notification.** FCM deprioritises high-priority messages that do not end in a user-visible notification (judged over 7 days), and background work is unreliable on the brands that lead in India — Xiaomi, OnePlus and Samsung score 5/5 on dontkillmyapp.
- **APNs:** OneSignal needs a `.p8` key for Live Activities; p12 certificates are not supported. ActivityKit push tokens can change mid-activity — OneSignal's default-attributes route holds them, so the API never touches APNs. A custom `ActivityAttributes` card needs Swift start code and, with the team's own APNs sender, 10–15 days _(est.)_; v1 stays on the default attributes.
- **Not in the notes:** OneSignal's exact update and end calls for Live Activities — read OneSignal's documentation at build time.
- **Android prerequisites:** OneSignal SDK 5.1.14+ and compileSdk 36 — both met (`com.onesignal:notifications:5.7.6`, compileSdk 36).
- **The link in every payload:** a `path` (`orders/<id>`), which the app opens as `dzzlooms://orders/<id>` through Phase 8's `src/navigation/linking.js` — the scheme is fixed in code, so a payload can't send the app to another host. The https form, `https://<links-host>/orders/<id>` (claimed by the AASA and `assetlinks.json` files of [[08-phase-8-instant-experiences-and-links]]; `<links-host>` is a host the user chooses), is for links people share, not for push taps.

### Draws on

[[05-phase-5-notifications-and-live-status]] (every name below) · [[08-phase-8-instant-experiences-and-links]] (`linking.js`, `DzzloLinks`) · [[01-phase-1-foundations]] (test targets) · [[09-phase-9-security-privacy-and-release]] (extension provisioning, the `.p8` key, version alignment).

### Build order (test-first)

1. **Card payload — Jest red (Tier 1).** `src/helpers/OneSignal/orderCardPayload.js`: the stage keys map (`placed | confirmed | dispatched | delivered`); a missing ETA leaves the key out; the serialised JSON stays **under 3,500 bytes** — a margin under the 4 KB limit. **Green.**
2. **Start wrapper — Jest red.** `src/helpers/OneSignal/liveActivity.js`: `startOrderCard(order)` is a no-op on Android and on iOS below 16.1 (swap `Platform.OS` / `Platform.Version` per case, as `src/i18n/__tests__/deviceLocale.test.js` does); `setupLiveStatus()` turns on push-to-start and push-to-update through `OneSignal.LiveActivities.setupDefault`. **Green.**
3. **Tap routing — Jest red.** `src/helpers/OneSignal/routeForNotification.js`: `routeForNotification(data, role)` returns `{ kind: 'link', path }` when the push carries `path`, `{ kind: 'legacy', key }` for today's drawer switch, and `null` for junk. The `link` branch opens `dzzlooms://${path}` and resolves through Phase 8's `src/navigation/linking.js` — `linkingConfigFor(role)` maps `orders/:orderId?` in both role trees, and `buildLinking`'s `filter` parks a link that arrives before the role drawer mounts (`parkLink`) until `replayParkedLink` lands it — which also retires the drawers' 900 ms `setTimeout`. Phase 8's `src/navigation/__tests__/linking.test.js` already pins `orders/<id>`. **Green.**
4. **Permission in context — Jest red.** `src/helpers/OneSignal/permission.js`: `nextPermissionStep({ os, canAsk, granted, role, hasOrdered })` returns `'none' | 'provisional' | 'explain' | 'settings'` — no prompt at launch (today `requestPermission(true)` runs at first init), an explanation sheet after the first order. **Green.** Drop the unconditional `LogLevel.Verbose` in the same change.
5. **Android — JUnit red.** `LiveOrderUpdateTest` (JUnit + Robolectric): `parse` accepts start, update and end, rejects a missing `key`, and maps one `key` to one Android notification ID. Then `LiveOrderNotification.build`: on API 36 a `ProgressStyle` with four segments and promotion requested — ongoing until delivered, a `contentTitle`, not colorized, no custom `RemoteViews`, on the `live_status` channel (not `IMPORTANCE_MIN`); below 36 a `NotificationCompat` progress bar. Whether Robolectric models API 36's `ProgressStyle` is unverified; if not, the device run covers the builder. **Green:** `android/app/src/main/java/in/vsyst/dzzlooms/notifications/NotificationServiceExtension.kt` (OneSignal's `INotificationServiceExtension`) — `notify()` again with the same ID to update, `cancel(id)` to end — plus `POST_PROMOTED_NOTIFICATIONS` in the manifest.
6. **iOS — XCTest red.** `OrderStage(raw:)`: unknown or `nil` → `.placed`; `step` is 0…3; labels resolve in en and hi — a file with no OneSignal import, compiled into both `DzzloWidgets` and the test bundle. **Green:** the `DzzloWidgets` Widget Extension ("Include Live Activity") with `ios/DzzloWidgets/DzzloOrderLiveActivity.swift`, its own Podfile target with `pod 'OneSignalXCFramework/OneSignalLiveActivities', '>= 5.0.0', '< 6.0'`, `NSSupportsLiveActivities = YES` in the app's `Info.plist`, and the tap URL from `DzzloLinks.order(…)` (`ios/Shared/DzzloLinks.swift`, Phase 8).
7. **Config pins — red, then green.** Extend Phase 5's `src/helpers/OneSignal/__tests__/push.config.test.js`: `NSSupportsLiveActivities` in `Info.plist`; `POST_PROMOTED_NOTIFICATIONS` in the manifest; the `DzzloWidgets` bundle id starts with `in.vsyst.dzzlooms.`, its `MARKETING_VERSION` equals the app's (not the NSE's 1.0 mistake), and the Podfile has its target.
8. **The API's side** — its own red/green pairs in the API repo: payload shape, no balances, ≤ 4 KB, one `key` per order.
9. **Device runs** — below.

### Acceptance checks

**Android:**

- [ ] An Android 16 emulator on a **36.1+** image (the promotion setter is 36.1), or a Pixel: dispatch → a promoted Live Update — status-bar chip, top of the shade, lock screen. `NotificationManager.canPostPromotedNotifications()` is true, and `Notification.hasPromotableCharacteristics()` is true for ours.
- [ ] Samsung One UI 8 (Now Bar) and Xiaomi HyperOS 3.1 (Super Island), if devices are available. One UI 8's beta needed a developer toggle; whether the stable release gates third-party Live Updates is unverified.
- [ ] An API 34 emulator: the same pushes give an ordinary ongoing notification whose progress bar updates in place (same ID), without promotion.
- [ ] Android 12 and below (API 24–32): no runtime prompt; the notifications still arrive.
- [ ] Start, update and end still work with the process killed (`adb shell am kill in.vsyst.dzzlooms`) — the extension needs no JavaScript.
- [ ] A dismissed Live Update is never reposted.
- [ ] A tap opens the order, cold and warm, through `dzzlooms://orders/<id>` (reproduce it without a push: `adb shell am start -W -a android.intent.action.VIEW -d "dzzlooms://orders/<id>" in.vsyst.dzzlooms`); a shared `https://<links-host>/orders/<id>` opens it too once `adb shell pm get-app-links in.vsyst.dzzlooms` shows the domain verified.
- [ ] On Xiaomi and Samsung with battery restrictions, the visible notifications still arrive; the OEM guide links to `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS`, never `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`.

**iOS:**

- [ ] A physical iPhone on iOS 17.2+: push-to-start at `dispatched` shows the Lock Screen view and the Dynamic Island (compact, minimal, expanded); updates arrive; the card ends at `delivered`.
- [ ] iOS 16.1–17.1: the app starts the card when the customer opens that order (`startOrderCard`), and it then updates by push.
- [ ] iOS 15.x (the 15.1 floor): no Live Activity code runs (`@available` gating); ordinary notifications only; no crash.
- [ ] All four stages in light and dark, en and hi, portrait and landscape (iOS 27 shows the card in the Dynamic Island in both), and StandBy (the Lock Screen view scaled to 200 %).
- [ ] A trip longer than 8 hours is ended by the system, and the final "Delivered" notification still arrives.
- [ ] A tap opens the order through `DzzloLinks.order(…)` — `dzzlooms://orders/<id>`, which reaches JavaScript once Phase 8 §2.3's SceneDelegate additions forward it (`xcrun simctl openurl booted "dzzlooms://orders/<id>"` reproduces it); a shared `https://<links-host>/orders/<id>` opens it as a Universal Link.

**Both:**

- [ ] The same order shows the same stage on both platforms at the same moment.
- [ ] en and hi labels fit at 320 dp; the Android chip text stays under 7 characters (`"25 min"`, not `"ETA 25 minutes"`), because the chip shows text under 7 characters whole and only the icon when less than half fits.
- [ ] No rupee amount appears in any payload (check the API's fixtures).

### Review and policy

- **Apple** — 4.5.3 (no spam through push or Live Activities — one card per real order, a handful of updates, never a price promotion), 2.5.16 (related to the app), 4.5.4 (minimal payloads; promotional pushes only after an explicit in-app opt-in, with an in-app opt-out), 4.4 (no marketing inside the extension). `.timeSensitive` (iOS 15.0) suits "order awaiting approval" and needs a capability, not Apple's approval (secondary sources); critical alerts are not for this app.
- **Google** — Live Update criteria: ongoing, user-initiated, time-sensitive; not ads, promotions, chat, alerts or package tracking; never repost a dismissed update. `POST_PROMOTED_NOTIFICATIONS` is a normal permission and no Play Console form was found for it.
- **Data safety and privacy label** — no new data type, assuming order data is already declared (not verified — check).
- **Provisioning** — a new App ID and profile for `DzzloWidgets` (Xcode automatic signing can create them); the `.p8` key and OneSignal set-up are account-holder steps. The extension needs its own privacy manifest if it uses a required-reason API.
- **A conflict to know:** OneSignal says promotion needs "Android 16 QPR1 (API 36.1)"; Google's docs say API 36.1 is Android 16 QPR2. The number agrees, the release name does not; the code checks `canPostPromotedNotifications()`, never a version.

### Effort _(est.)_

Live Activity via OneSignal's default attributes 5–8 days plus server calls (iOS note; the ecosystem note says 1–2 weeks including APNs and CI signing); Android Live Update 4–6 days including server (Android note; ecosystem 3–5); notification hardening 2–4 days; App Links 1–2 days in the app. Summed: **≈ 12–20 working days in the app**, plus the API work. Phase 5 in full, server work included, is 3–5 weeks.

---

## 4. Capstone C — Daily Summary Widget + "Outstanding Balance" Intent

**Deliverable:** a dealer adds a **Daily Summary** widget to the home screen — today's ₹ sales, HSD and MS litres, orders and the dealer's outstanding — on iOS and on Android. On an iPhone, "What's my outstanding balance in Dzzlo OMS?" to Siri — or the same intent from Shortcuts or Spotlight — answers from the same snapshot, with the time it was taken. Long-pressing the app icon offers role-based quick actions (**Today**, **Customers**, **New order**) on both platforms.

**Parity, in plain words:** Android gets the widget and the quick actions but **no voice answer** — Google Assistant's removal from phones began on 2026-09-04, and AppFunctions reach Gemini only in a private preview (Phase 6 keeps an AppFunction as a debug-only spike behind a flag). **Scope:** dealers only — a customer's own balance has no v2 read model yet, so its source is an open question for the user before a customer widget.

The app's display name is **Dzzlo OMS** (`CFBundleDisplayName` and `app_name`), so that is what `\(.applicationName)` says inside the phrase.

### The snapshot — Phase 6's `summary.json`, schema 1

JavaScript writes one JSON file; the widget and the intent only read it. Figures illustrative; 06:00 IST is 00:30 UTC.

```json
{
  "v": 1, "writtenAt": "2026-09-29T08:35:00Z", "role": "dealer", "lang": "en",
  "window": { "from": "2026-09-29T00:30:00Z", "to": "2026-09-30T00:30:00Z" },
  "today": { "orders": 42, "salesPaise": 7578420, "salesText": "₹ 75,784.20",
             "dieselText": "3,210.000", "petrolText": "1,050.000" },
  "outstanding": { "customers": 37, "paise": 128000000, "text": "₹ 12,80,000.00" }
}
```

- **Text is final; money also travels as whole paise.** JS formats with the Daily Summary's own `formatMoney` / `formatLitres`, in the user's language, and computes paise once with the rule `src/helpers/DailySummary/totals.js` already applies (`Math.round(number * scale)` — export it, don't copy it), on figures the API has already rounded line by line ([[vsyst-technologies/docs/oms_app/screen-redesign/screens/02-daily-summary|Daily Summary spec]] §5.1: "round every line, then sum"). **Swift and Kotlin never multiply, divide or round money** — they print `salesText` and `outstanding.text`.
- **Where the numbers come from.** `today` from the v2 Daily Summary's page-1 `summary` (`src/screens/v2/Common/DailySummary/useScreenModel.js`); `outstanding` from the v2 Customers summary strip's `totalBalance` (`src/screens/v2/Dealer/Customers/components/SummaryStrip.js`).
- **Only today.** Written only while the Daily Summary shows the current shift window — never after the dealer picks Yesterday, Last 7 days, This month or Custom.
- **The contract is a file.** The golden fixture `src/native/__fixtures__/summary.v1.json` is read by all three test suites — Jest, XCTest and JUnit — so the three languages cannot drift.
- **Nothing after sign-out.** Sign-out deletes the file (and Phase 6's `customers.json` for Spotlight) and reloads every surface; an unknown `v` reads as "Open DZZLO". No token lives in the snapshot — a live answer would need the bearer token in a Keychain item shared through `keychain-access-groups` (iOS 3.0), which first needs Phase 9's move out of plain AsyncStorage.

### Pipeline

```
Daily Summary (v2), page 1 ─► buildSnapshot(previous, { today })          src/helpers/SharedSnapshot/buildSnapshot.js
Customers (v2), summary strip ─► buildSnapshot(previous, { outstanding })   text via formatMoney · paise via totals.js
        │  saveSnapshotSection(section) — only if shouldWriteSnapshot(window, now)      src/native/sharedStore.js
        ▼
specs/NativeSharedStore.ts   writeSnapshot('summary.json', json) · readSnapshot(name) · clearAll()
   ├─ iOS      SharedStore.swift → App Group group.in.vsyst.dzzlooms.shared → WidgetCenter.reloadAllTimelines() (14.0)
   └─ Android  SharedStore.kt → filesDir → a Glance update
        ▼
iOS      DzzloWidgets: SummaryProvider + SummaryView read SummarySnapshot.loadShared()
         OutstandingBalanceIntent (iOS 16.0): BalanceAnswer.dialog(for: SummarySnapshot.loadShared())
Android  DailySummaryWidget (Glance 1.2.0): SummarySnapshot.read(filesDir)
Both     NativeShortcuts: today · customers · new_order — set after sign-in by role
sign-out (logoutUser.fulfilled) ─► clearSharedSnapshots() · NativeShortcuts.setItems([])
```

### Draws on

[[06-phase-6-widgets-shortcuts-and-intents]] (every name below) · [[05-phase-5-notifications-and-live-status]] (`DzzloWidgets` exists after Capstone B) · [[08-phase-8-instant-experiences-and-links]] (`DzzloLinks.dailySummary` for the tap) · [[09-phase-9-security-privacy-and-release]] (App Group provisioning, privacy manifest) · [[01-phase-1-foundations]].

### Build order (test-first)

1. **Snapshot builder — Jest red (Tier 1).** `src/helpers/SharedSnapshot/__tests__/buildSnapshot.test.js`: a known input yields exactly the golden fixture; text equals `formatMoney`; paise are integers — a non-integer is refused, which is how "already rounded" is pinned; a new section merges into the previous snapshot. `shouldWriteSnapshot.test.js`: true only for the current shift window. **Green.**
2. **Facade — Jest red.** `src/native/__tests__/sharedStore.test.js` mocks `specs/NativeSharedStore`: one write per new summary; a rejected write is swallowed, because a widget must never break a screen; sign-out calls `clearAll`. **Green:** `src/native/sharedStore.js` (`saveSnapshotSection`, `clearSharedSnapshots`), registered like `NativeAppInfo` and pinned by `src/native/__tests__/sharedStore.config.test.js` (Phase 6 §2.2).
3. **Wiring — Tier 2 / Tier 3 red.** The Daily Summary's `useScreenModel.js` saves `{ today }` when a page-1 `summary` arrives and `shouldWriteSnapshot` holds; the Customers screen saves `{ outstanding }`; the `logoutUser.fulfilled` path clears. **Green.**
4. **Swift — XCTest red.** `SummarySnapshotTests` decodes the fixture (added to the test bundle by reference); a missing file or `v: 2` gives `nil`; the timeline closes at the window's end. `BalanceAnswer.dialog(for:)` is tested for a missing, a fresh and a schema-2 snapshot. **Green:** `SharedStore.swift`, `SummarySnapshot.swift` (one file in three targets — app, `DzzloWidgets`, test bundle), `SummaryProvider` / `SummaryView`, and `ios/dzzlo_oms_app/Intents/OutstandingBalanceIntent.swift` with an `AppShortcutsProvider` whose phrases are "What's my outstanding balance in `\(.applicationName)`" and "`\(.applicationName)` outstanding balance". On iOS 27, an App Intents Testing (27.0) case runs the intent out-of-process, the way Siri does.
5. **Kotlin — JUnit and Glance red.** `SummarySnapshotTest` decodes the same fixture; `SharedStoreTest` (Robolectric) writes, reads and clears; Glance's unit-test library (`runGlanceAppWidgetUnitTest`, since Glance 1.1.0) checks the widget's text and its tap. **Green:** `SharedStore.kt`, `NativeSharedStoreModule`, `DailySummaryWidget` + `DailySummaryWidgetReceiver` — Glance 1.2.0 with `buildFeatures { compose = true }`, the app's first Compose code, so record the APK-size change.
6. **Quick actions — Jest red.** `src/helpers/Shortcuts/routeForShortcut.js`: `routeForShortcut(type, role)` maps `today`, `customers` and `new_order` (dealer) and `today`, `new_order` (customer) to navigator routes; an unknown type or role gives `null`; the facade sets items after sign-in and `setItems([])` at sign-out; no title carries an amount ("never include sensitive user info in shortcut metadata"). **Green:** `specs/NativeShortcuts.ts` (`setItems`, `getInitialShortcut`, `onShortcut`) over `UIApplicationShortcutItem` (iOS 9.0) and dynamic App Shortcuts (API 25), navigating only once the navigation container is ready.
7. **Config pins.** The app's and `DzzloWidgets`' entitlements both list `group.in.vsyst.dzzlooms.shared` (OneSignal's group stays untouched); the widget receiver is in the merged manifest; `DzzloWidgets` still matches the app's `MARKETING_VERSION`; and Phase 6's `src/theme/__tests__/widgetColours.config.test.js` fails if the extension's colour sets drift from the `src/theme` tokens (the extension cannot import them).
8. **Device runs** — below.

The intent's Swift is in [[06-phase-6-widgets-shortcuts-and-intents]] §7.3. Two facts shape it: the deployment target is iOS 15.1, below every App Intents API (16.0), so everything is `@available`-gated; and on iOS 26 a `SnippetIntent` (26.0) could turn the answer into an interactive snippet — a stretch, 3–5 days _(est.)_.

### Acceptance checks

**iOS** (a 17e and a 17 Pro Max simulator, then a device for Siri):

- [ ] Home Screen small (sales, "Today", snapshot time) and medium (adds litres, orders, outstanding) match the Daily Summary and Customers screens to the paisa (a screenshot pair).
- [ ] Lock Screen rectangular and inline show orders and litres; ₹ appears there only if the dealer opts in (Phase 6's house decision), and every figure sits under `.privacySensitive()` so the system can redact it when locked.
- [ ] Light, dark and the iOS 26 tinted rendering; en and hi; the smallest family at the largest text size — the widget's version of the 320 dp rule.
- [ ] A fresh Daily Summary load updates the widget; reloads are budgeted (typically 40–70 a day for a frequently viewed widget), so reload after a write, never on a timer.
- [ ] "What's my outstanding balance in Dzzlo OMS?" works by voice in English (India) on an iOS 16+ iPhone **without** Apple Intelligence, and from the Shortcuts app and Spotlight.
- [ ] Sign out: the widget falls back to "Open DZZLO", and Siri's answer says so too.
- [ ] iOS 15.x: no intent, no crash.

**Android:**

- [ ] `DailySummaryWidget` shows the same figures; a tap opens Daily Summary.
- [ ] It refreshes after a Daily Summary load and on app open. `updatePeriodMillis` below 30 minutes is not honoured, so no fast polling; at most an hourly WorkManager refresh (15 minutes is WorkManager's floor).
- [ ] Sign-out wipes it; it survives `adb shell am kill in.vsyst.dzzlooms` and a reboot.
- [ ] Long-press offers **Today**, **Customers** and **New order** for a dealer, nothing when signed out; on API 24 (shortcuts start at API 25) nothing shows and nothing crashes.
- [ ] On Xiaomi and Samsung with battery restrictions the widget stays current — and an active widget also keeps the app out of the Restricted standby bucket.
- [ ] No large bitmaps: once the app targets API 37, `RemoteViews` bitmap memory is capped at 1.5 × screen width × height × 4 bytes and going over throws.

**Both:**

- [ ] The widget, the screens and the answer agree on both platforms, in en and hi; colours come from theme tokens (mirrored in the extension and pinned).

### Review and policy

- **Apple** — 2.5.16 and 4.4: the widget shows the user's own data and no marketing. 2.5.11 (i)–(iii): the phrase names the app rather than a generic term, and the intent answers directly with nothing between request and answer. Money on a Lock Screen is a privacy decision (4.5.4's spirit), hence the opt-in.
- **Account set-up** — the App Group is registered on the developer website by the account holder; registered App Groups also act as keychain access groups.
- **Privacy manifest** — the extension reads the shared container; declare any required-reason API in the extension's own manifest.
- **Play** — widgets and shortcuts need no Console form, and the data stays on the device, so Data safety is unchanged.

### Effort _(est.)_

First iOS widget with the App Group snapshot and logout wipe 8–15 days; each further widget or a Control 2–4 days; App Intents — the iOS note prices a 3–5-intent starter set at 10–20 days, and one intent with two phrases is a fraction of that, not separately estimated; Glance widget 5–8 days (3–5 with `react-native-android-widget` instead); `NativeShortcuts` ~1 day per platform; the shared store 1–2 days. Summed: **≈ 15–27 working days plus the intent.** The ecosystem note's whole-feature figure is 2–3 weeks for the widget on both platforms; Phase 6 in full is 4–7 weeks.

---

## 5. What the Three Prove Together

| | A | B | C |
| --- | --- | --- | --- |
| Our modules | `NativePdf`, `NativePrint` | — | `NativeSharedStore`, `NativeShortcuts` |
| Our targets and surfaces | — | `DzzloWidgets` (Live Activity), Kotlin `NotificationServiceExtension` | `DzzloWidgets` (widget + intent), `DailySummaryWidget` |
| Test machinery exercised | Jest facade, XCTest (`dzzlo_oms_appTests`), plain JUnit, an instrumented Android test, config pins | + Robolectric at API 36 (if modelled), API-side contract tests | + one golden fixture read by three test suites, Glance unit tests, App Intents Testing (iOS 27) |
| Platform floor handled | iOS 15.1 · API 24 | below iOS 16.1 and Android 16, plain notifications | below iOS 16 no intent · API 24 no shortcuts |

After all three, the app owns four thin modules (plus Phase 1's `NativeAppInfo`), one iOS extension target with two surfaces, two Android native surfaces, one App Group and a test target on each platform — the most native code this course recommends before a measured need appears.

## 6. Where to Go Next

- **Wave 3 has no capstone** because it is one phase: do [[04-phase-4-images-and-scanning]] for slip photos and scans (the scanner plugin, or `NativeDocScanner` if its audit fails) and, later, `NativeUpload`.
- **The deferred list, with its triggers:** maps once dispatch data exists ([[07-phase-7-maps-and-location]]); tanker tracking once a driver-side flow is designed; `DzzloClip` once the web invoice page proves customers open invoice links ([[08-phase-8-instant-experiences-and-links]]); OCR after a spike proves accuracy on real slips; Bluetooth printing once dealers standardise on hardware; the AppFunction once Gemini access opens.
- **Replace the estimates.** Every _(est.)_ above is uncalibrated. Put the measured days in Lab Notes — that is what turns this from a plan into the team's own reference ([[11-reference]] §3).

## Lab Notes

Nothing built yet (2026-09-29). Record each device run here, dated: platform, OS version, device, build type, result — plus Capstone A's image-capture answer and the user's server-versus-device PDF decision.

---

← [[09-phase-9-security-privacy-and-release]] · [[11-reference]] →
