# Reference — Matrices, Versions, Policies, Sources

> Level: Reference | Everything the phases point at: the library matrix, versions as measured, effort, the review and policy map, a Turbo Module recipe card, troubleshooting, a glossary and every source. Verified 2026-09-29 unless marked; estimates marked _(est.)_.

---

## 1. The Library Matrix

Every library the research notes assessed, grouped by capability, with the course's verdict. Versions and dates from the npm registry; New-Architecture flags from the React Native Directory API; health from npm release history and GitHub — all queried 2026-09-29.

**Legend.**

- **Arch** — TM = ships a `codegenConfig` (TurboModule / Fabric); Nitro = Nitro module (New-Architecture only); Expo = Expo module (needs `expo` installed, and no Expo SDK pairs with RN 0.84 or 0.87); Old = no codegen and not flagged New-Arch; "—" = not stated in the notes.
- **Health** (the ecosystem note's scale) — A = a release within 3 months; S = 3–12 months; St = more than 12 months; U = flagged unmaintained, deprecated or archived. "/wk" = npm downloads last week.
- **Verdict** — **USE** a maintained library as it is; **WRAP** a thin module of ours over one platform API; **BUILD** our own extension target or native surface; **SKIP** not now (dead, no demand, or Expo-only until the upgrade). "alt." marks an acceptable alternative that is not the default; "Expo track" means available on the optional Expo track after an upgrade to an Expo-paired RN version.

### 1.1 The verdict per capability

The ecosystem note's recommendation matrix, with the course's verdict beside it. Where they differ, the last column says why.

| Capability | 2026 default in the ecosystem note | Note's verdict | Course verdict | Covers | Why · cost _(est.)_ |
| --- | --- | --- | --- | --- | --- |
| Photo capture of DU slips, meter readings, cheques | `react-native-document-scanner-plugin` for paper; `react-native-image-picker` camera mode for plain photos | USE | USE the plugin if an audit of 2.0.4 finds a plain TurboModule, else **WRAP** `NativeDocScanner`; image-picker as the fallback | both | the plugin's module type is disputed (§2.7); the DU-slips spec says no scanner module while a healthy wrapper exists; a thin ML Kit wrap is ~1 day on Android |
| Custom live camera UI | VisionCamera 5 | USE when needed | USE when needed | both | New-Arch-only; brings Nitro and nitro-image |
| Barcode / QR (GST IRN, UPI) | VisionCamera 5 + barcode-scanner (ML Kit) | USE | USE | both | verify IRN signatures on the server |
| OCR | none in v1 | SKIP now, WRAP later | SKIP until a spike proves accuracy | both | small plugin ecosystem; no accuracy data on Indian slips |
| Image picking | `react-native-image-picker` 8.2.1 | USE, watch | USE, watch | both | no release in 16 months; whether it uses Android's Photo Picker is unverified |
| Compression / EXIF | `@bam.tech/react-native-image-resizer`; skip EXIF | USE / SKIP | USE / SKIP | both | stamp time and place at capture instead of reading EXIF |
| File pick / save / open | documents picker + viewer; blob-util or file-access for I/O | USE | USE | both | never `react-native-fs` (unmaintained) |
| Share (WhatsApp, share sheet) | `react-native-share` 12 | USE | USE | both; WhatsApp Business Android-only | iOS cannot send a file straight to a WhatsApp contact (#1699) |
| Share a summary as an image | `react-native-view-shot` 6 | USE | USE | both | 1.2M/wk, active |
| HTML → PDF | keep `react-native-html-to-pdf` 1.3.0 | USE, watch | **WRAP** `NativePdf`; remove html-to-pdf | both | never called in live code, no release in 12 months; the note's own fallback was this 2–3-day wrap; a server-rendered PDF is the alternative ([[10-capstones]] §2) |
| System print (A4) | `expo-print` (with Expo) or a thin module | WRAP | **WRAP** `NativePrint` | both | `react-native-print` unmaintained; ~2 days |
| PDF viewing | `@react-native-documents/viewer` | USE | USE | both | `react-native-pdf` only for in-app rendering (383 open issues) |
| Background upload / download | foreground blob-util + a persisted retry queue; background-downloader if needed | SKIP true background upload | **WRAP** `NativeUpload`, later — foreground `XMLHttpRequest` uploads first (DU-slips spec D7) | both | the iOS and Android notes both route true background upload in-house; ~1 week for both |
| Maps (tanker ETA) | `react-native-maps` 1.29; v1 = a navigation deep link | USE later | USE later | both | [[07-phase-7-maps-and-location]] |
| Location at capture time | `expo-location` (with Expo) or a thin module | WRAP | WRAP only if a location feature ships | both | the community geolocation libraries are unmaintained |
| Background location (drivers) | `react-native-background-geolocation` or custom | defer / BUILD | SKIP now | both | Play declaration, a location FGS type, a paid licence |
| Push | keep OneSignal 5.5 | USE | USE | both | already integrated |
| Local notifications + action buttons | `react-native-notify-kit` or `expo-notifications` | USE | USE notify-kit | both | never `@notifee/react-native` (archived) |
| In-app messaging | OneSignal in-app messages | USE | USE | both | "no code"; Firebase IAM would duplicate it |
| iOS Live Activity | SwiftUI widget-extension layout + OneSignal `setupDefault` / `startDefault` | BUILD + USE | **BUILD** `DzzloWidgets` + USE OneSignal | iOS | 1–2 weeks incl. APNs and CI signing |
| Android Live Update | a thin Kotlin module, or Voltra's next release | WRAP | **BUILD** the Kotlin `NotificationServiceExtension` (a OneSignal extension class, not a Turbo Module) | Android | 3–5 days; Voltra's support is merged but unreleased |
| Home-screen widget (daily summary) | Android `react-native-android-widget`; iOS SwiftUI, or expo-widgets / Voltra | USE (Android) + BUILD (iOS) | **BUILD** both: `DailySummaryWidget` (Glance) + `DzzloWidgets` | both | the JSX library renders RN views to an image and is v0.x; Glance 1.2.0 is stable (it brings Compose) |
| App-group shared storage | a small module (`react-native-shared-group-preferences` is dead) | WRAP | **WRAP** `NativeSharedStore` | both | 1–2 days |
| Siri / App Intents; Android AppFunctions | none | SKIP now | **BUILD** one App Shortcut intent (iOS 16.0+); SKIP free-form Siri AI; AppFunctions only as a debug-only spike behind a flag | iOS (Android: spike only) | App Shortcut phrases need no Apple Intelligence; AppFunctions + Gemini is a private preview |
| App shortcuts / quick actions | `expo-quick-actions` (with Expo), else a thin module | USE / WRAP | **WRAP** `NativeShortcuts` — dynamic, role-based items over `UIApplicationShortcutItem` (iOS 9.0) and dynamic App Shortcuts (API 25) | both | `react-native-quick-actions` archived, `expo-quick-actions` needs Expo; static items can't know the role; ~1 day per platform |
| App Clip / instant app | none | SKIP | SKIP now; `DzzloClip` later behind a go/no-go | iOS | Play Instant is gone; RN clip tooling is Expo-only and not New-Arch |
| Biometric app lock | `expo-local-authentication` (with Expo), else `@sbaiahmed1/react-native-biometrics` or keychain access control | USE | USE `react-native-keychain` behind `src/native/appLock.js` — no `NativeBiometrics` ([[09-phase-9-security-privacy-and-release]]) | both | no keychain release in 18 months: pin the version, keep every call behind the one facade |
| Passkeys | `react-native-passkey` 3.6 | SKIP for v1 | SKIP for v1 | both | needs server WebAuthn and associated domains / assetlinks |
| Secure storage | `react-native-keychain` 10 or `expo-secure-store`; `react-native-mmkv` 4 for non-secret cache | USE | USE keychain | both | the bearer token leaves plain AsyncStorage ([[09-phase-9-security-privacy-and-release]]) |
| OTA updates | Hot Updater (self-hosted) | USE | USE | both | EAS Update only on the Expo track |
| Bluetooth receipt printing | a JS ESC/POS encoder + `react-native-ble-manager` + `react-native-bluetooth-classic`, or a vendor SDK | BUILD | SKIP until demand | both; iOS needs BLE or MFi | 2–3 weeks + a device matrix |
| Contact picker (onboard a customer) | a thin module over the system pickers | WRAP | WRAP, not scheduled | both | no `READ_CONTACTS`; 1–2 days |
| `tel:` / `sms:` / WhatsApp / UPI links | core `Linking` | USE core | USE core | both | plus `<queries>` and `LSApplicationQueriesSchemes` |
| OTP autofill | `textContentType="oneTimeCode"` (iOS picks up codes from Mail) | USE core | USE core; SMS Retriever only if codes arrive by SMS | iOS (+ Android if SMS) | the notes disagree on the channel (§2.7) |
| Clipboard / haptics / permissions | community libraries | USE | USE when needed | both | installing `react-native-permissions` reverses the 2026-07-05 "keep stubbed, do not install" decision — the user decides |
| Store rating and review prompt | not in the ecosystem note; the store-review note (2026-09-30): our own Turbo Module, with `react-native-store-review` 0.5.0 as the fallback | BUILD | **WRAP** `NativeStoreReview`; the "Rate DZZLO" row is core `Linking` | both | the note's BUILD means "our own module, not a library"; in this legend a thin module over one platform API per side is a WRAP. ~95 lines with boilerplate, ~40 of them logic ([[09-phase-9-security-privacy-and-release]] §9) |

### 1.2 Camera, scanning, OCR

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-vision-camera` | 5.2.3 (2026-08-20) | Nitro, new-arch-only | A · 629k/wk · 19 releases in 12 months | USE when a custom camera is needed | both |
| `react-native-vision-camera-barcode-scanner` | 5.2.3 (2026-08-20) | Nitro (ML Kit) | A · 48k/wk | USE with VisionCamera | both |
| `react-native-nitro-zxing` | 0.1.0-alpha.0 (2026-08-26) | Nitro | alpha | SKIP | both |
| `expo-camera` | 57.0.6 (2026-09-29) | Expo | A · 2.47M/wk | SKIP · Expo track (SDK 58 adds `CameraView.scanDocumentAsync`) | both |
| `react-native-camera-kit` | 18.0.1 (2026-08-03) | TM | A · 75k/wk | alt. | both |
| `react-native-document-scanner-plugin` | 2.0.4 (2026-01-02) | TM per npm; "built as an Expo module" per the Directory — conflict | S · 99k/wk | alt. to `NativeDocScanner` | both |
| `@infinitered/react-native-mlkit-document-scanner` | 5.0.0 (2025-11-17) | — | S · 473/wk | SKIP | Android |
| `@react-native-ml-kit/text-recognition` | 2.0.0 (2025-09-01) | Old | St · 58k/wk | SKIP | both |
| `@react-native-ml-kit/barcode-scanning` | 2.0.0 (2025-09-01) | Old | St · 4.7k/wk | SKIP | both |
| `expo-text-extractor` | 2.0.0 (2026-02-28) | Expo (community) | S · 14k/wk | SKIP | both |
| `react-native-vision-camera-ocr-plus` | 2.0.6 (2026-08-20) | frame-processor plugin | A · 10k/wk, small | SKIP (OCR deferred) | both |
| VisionKit `VNDocumentCameraViewController` (iOS 13.0) · ML Kit Document Scanner (Play services, no CAMERA permission) | platform | — | — | **WRAP** → `NativeDocScanner`, only if the plugin audit fails | both |
| `DataScannerViewController` (iOS 16.0, A12 or later) · Google code scanner (API 23+, no permission) | platform | — | — | alt. for QR without a custom camera | both |
| Vision `RecognizeDocumentsRequest` (iOS 26.0) / `VNRecognizeTextRequest` (iOS 13.0) · ML Kit Text Recognition v2 (reads Devanagari) | platform | — | — | SKIP until the OCR spike | both |

### 1.3 Image picking, compression, EXIF

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-image-picker` | 8.2.1 (2025-05-04) | TM | St · 515k/wk · 306 open issues | USE, watch | both |
| `expo-image-picker` | 57.0.20 (2026-09-24) | Expo | A · 4.9M/wk | SKIP · Expo track | both |
| `react-native-image-crop-picker` | 0.52.0 (2026-09-29); the Android note read 0.51.1 (2025-10-21) | TM | A release · 555 open issues | alt. | both |
| `@baronha/react-native-multiple-image-picker` | 2.2.5 (2025-12-10) | Nitro | S | SKIP | both |
| `@bam.tech/react-native-image-resizer` | 3.0.11 (2024-11-25) | TM | St release, active repo (push 2026-09-26) | USE | both |
| `react-native-image-resizer` | 1.4.5 (2021-06-16) | — | U (moved to the `@bam.tech` package) | SKIP | — |
| `react-native-compressor` | 2.0.3 (2026-07-25) | Nitro | A · 215k/wk | alt. | both |
| `expo-image-manipulator` | 57.0.20 (2026-09-24) | Expo | A | SKIP · Expo track | both |
| `@lodev09/react-native-exify` | 1.0.3 (2026-02-22) | TM | S, small | SKIP | both |
| `PHPickerViewController` (iOS 14.0) · Photo Picker (built in on Android 13; Play-services backport for 4.4–12) | platform | — | — | the permission-free path the libraries should use | both |

### 1.4 Files, PDF, printing, sharing, background transfer

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `@react-native-documents/picker` | 12.0.2 (2026-07-28) | TM | A · 344k/wk | USE | both |
| `@react-native-documents/viewer` | 4.0.1 (2026-07-28) | TM | A | USE (Quick Look / the OS viewer) | both |
| `react-native-document-picker` | 9.3.1 (2024-08-22) | — | U (renamed) | SKIP | — |
| `expo-document-picker` | 57.0.3 (2026-09-29) | Expo | A | SKIP · Expo track | both |
| `react-native-fs` | 2.20.0 (2022-05-04) | Old | U | SKIP | — |
| `@dr.pogodin/react-native-fs` | 2.40.3 (2026-09-12) | TM | A | alt. | both |
| `react-native-file-access` | 4.0.4 (2026-09-18) | TM | A | alt. | both |
| `expo-file-system` | 57.0.7 (2026-09-11) | Expo | A · 10.5M/wk | SKIP · Expo track (SDK 58 adds `File.preview()`) | both |
| `react-native-blob-util` | 0.25.1 (2026-09-24) | TM | A · 958k/wk | USE | both |
| `react-native-background-upload` | 6.6.0 (2022-10-07) | Old | U | SKIP | — |
| `rn-background-upload` | 0.1.0 (2026-02-11) | New-Arch (Directory) | too new · 45/wk | SKIP | — |
| `@kesha-antonov/react-native-background-downloader` | 4.6.3 (2026-09-15) | TM | A | USE if background downloads are needed | both |
| `expo-background-task` | 57.0.21 (2026-09-29) | Expo | A | SKIP · Expo track | both |
| `react-native-background-fetch` | 4.4.2 (2026-04-15) | TM | S (Transistorsoft) | SKIP — periodic tasks, not uploads | both |
| `react-native-share` | 12.3.1 (2026-05-04) | TM | S (repo push 2026-08-31) · 741k/wk; open iOS issues #1699, #1556 | USE | both |
| `expo-sharing` | 57.0.22 (2026-09-24) | Expo | A | SKIP · Expo track | both |
| `react-native-view-shot` | 6.0.1 (2026-09-20) | TM | A · 1.23M/wk | USE | both |
| `react-native-html-to-pdf` (installed) | 1.3.0 (2025-09-04) | TM | S/St boundary · 48k/wk | SKIP — removed in [[02-phase-2-dependency-diet]] | both |
| `react-native-print` | 0.11.0 (2023-01-22) | Old | U | SKIP | — |
| `expo-print` | 57.0.2 (2026-09-11) | Expo | A · 688k/wk | SKIP · Expo track (`printToFileAsync` defaults to 612×792 pt) | both |
| `react-native-pdf` | 7.0.5 (2026-08-13) | TM | A release · 383 open issues | SKIP unless in-app rendering is needed | both |
| `react-native-pdf-renderer` | 2.3.0 (2025-08-12) | TM | St | SKIP | both |
| `pdf-lib` | 1.17.1 (2021-11-06) | JS | St | SKIP | — |
| `WKWebView.createPDF` (iOS 14.0) or `UIPrintPageRenderer` (iOS 4.2) · WebView print adapter (API 21 form) | platform | — | — | **WRAP** → `NativePdf` | both |
| `UIPrintInteractionController` (iOS 4.2) · `PrintManager` | platform | — | — | **WRAP** → `NativePrint` | both |
| background `URLSession` (iOS 8.0; uploads from a file only) · WorkManager (+ user-initiated data transfer jobs, Android 14) | platform | — | — | **WRAP** → `NativeUpload`, later | both |
| SAF (`ACTION_CREATE_DOCUMENT`, API 19) · `MediaStore.Downloads` (API 29) · androidx `FileProvider` | platform | — | — | configuration + tiny helpers | Android |

### 1.5 Maps and location

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-maps` | 1.29.11 (2026-09-27) | TM | A · 1.3M/wk · 16k stars | USE later — Apple Maps on iOS needs no key | both |
| `@maplibre/maplibre-react-native` | 11.4.0 (2026-09-19) | TM | A | alt. | both |
| `@rnmapbox/maps` | 10.3.5 (2026-07-22) | TM | A | alt. | both |
| `expo-maps` | 57.0.3 (2026-09-11) | Expo (alpha) | A | SKIP | both |
| `mappls-map-react-native` | 2.0.x | not in the Directory | New-Arch unknown | SKIP until verified | both |
| `@react-native-community/geolocation` | 3.4.0 (2024-09-01) | TM | U | SKIP | — |
| `react-native-geolocation-service` | 5.3.1 (2022-09-23) | Old | U | SKIP | — |
| `expo-location` | 57.0.20 (2026-09-24) | Expo | A | SKIP · Expo track | both |
| `react-native-background-geolocation` | 5.7.0 (2026-09-27) | TM | A — Android release builds need a licence ($399 iOS + Android) | SKIP now | both |
| core `Linking` to Google / Apple Maps | core | — | — | USE — the navigation deep link | both |

### 1.6 Push, local notifications, in-app messaging, Live Activities / Live Updates, widgets

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-onesignal` (installed 5.4.1) | 5.5.14 (2026-09-23) | TM | A · 187k/wk | USE; upgrade | both |
| `@notifee/react-native` | 9.1.8 (2024-12-20) | Old | U — archived 2026-04-07 | SKIP | — |
| `react-native-notify-kit` | 10.8.0 (2026-09-29); the Android note read 10.7.2 (2026-09-23) | TM, New-Arch only | A · 46k/wk | USE | both |
| `expo-notifications` | 57.0.21 (2026-09-24) | Expo | A · 5.2M/wk | SKIP · Expo track | both |
| `@react-native-firebase/messaging` | 26.4.0 (2026-09-05) | TM | A | SKIP — OneSignal owns push | both |
| `@react-native-firebase/in-app-messaging` | 26.4.0 (2026-09-05) | TM | A | SKIP — duplicates OneSignal IAM, forces RNFirebase 24 → 26 | both |
| `react-native-notifications` (Wix) | 5.2.2 (2025-11-16) | Old | S | SKIP | — |
| `expo-live-activity` | 0.4.2 (2025-11-18) | Expo | U — repo archived 2026-06-01 | SKIP | iOS |
| `voltra` | 2.3.2 (2026-09-22) | TM clients | A · Android Live Updates merged 2026-09-28 (PRs #325, #326), unreleased | SKIP now · watch | both |
| `expo-widgets` | 57.0.22 (2026-09-29) | Expo; iOS only (Android from SDK 58) | A | SKIP · Expo track | iOS |
| `react-native-widget-extension` | 0.3.0 (2026-05-25) | config plugin | S | SKIP (assumes prebuild) | iOS |
| `@bacons/apple-targets` | 5.0.0 (2026-07-17) | config plugin | A | SKIP (assumes prebuild) | iOS |
| `react-native-android-widget` | 0.22.1 (2026-08-17) | Directory New-Arch true | A · 78k/wk; renders RN views to an image | alt. to Glance | Android |
| `react-native-shared-group-preferences` | 1.1.24 (2023-09-18) | Old | U | SKIP → `NativeSharedStore` | iOS |
| ActivityKit (iOS 16.1; push-to-start 17.2) + WidgetKit (iOS 14.0) | platform | — | — | **BUILD** → `DzzloWidgets` | iOS |
| OneSignal `INotificationServiceExtension` → `ProgressStyle` (API 36) / `NotificationCompat` below | platform | — | — | **BUILD** → Kotlin `NotificationServiceExtension` | Android |
| Jetpack Glance 1.2.0 (2026-08-26) | platform | — | — | **BUILD** → `DailySummaryWidget` | Android |

### 1.7 Shortcuts, intents, App Clips

| Library or platform | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-siri-shortcut` | 3.2.4 (2023-12-13) | Old | U | SKIP | iOS |
| `expo-app-intents` | 0.0.1 — "published 2026-09-29, alpha" (iOS note) vs "2026-06-08, no description or repo" (ecosystem note) | — | alpha; provenance disputed | SKIP | iOS |
| `expo-quick-actions` | 6.0.2 (2026-05-27) | Expo | S · 235k/wk | SKIP · Expo track | both |
| `@rn-org/react-native-shortcuts` | 0.2.0 (2026-02-15) | New-Arch (GitHub-detected) | 1k/wk | SKIP | — |
| `react-native-quick-actions` | 0.3.13 (2019-11-24) | Old, archived | U | SKIP | — |
| `react-native-app-clip` | 0.9.1 (2026-06-12) | Expo config plugin; `newArchitecture: false` | S | SKIP (needs `npx expo prebuild`) | iOS |
| `AppIntent` + `AppShortcutsProvider` (iOS 16.0) | platform | — | — | **BUILD** — one "outstanding balance" intent | iOS |
| Quick actions `UIApplicationShortcutItem` (iOS 9.0) · App Shortcuts, static and dynamic (API 25), pinned (API 26) | platform | — | — | **WRAP** → `NativeShortcuts` (dynamic, role-based) | both |
| `ControlWidgetButton` (iOS 18.0) · `TileService` (API 24; add-tile prompt API 33) | platform | — | — | **BUILD** a "New order" Control in `DzzloWidgets`; Android gets an App Shortcut, and a tile only if dealers ask ([[06-phase-6-widgets-shortcuts-and-intents]]) | both |
| AppFunctions (API 36; `androidx.appfunctions` alpha) | platform | Kotlin + KSP | Gemini access in private preview | SKIP — at most a debug-only spike behind a flag | Android |
| App Clip target `.Clip` | platform | Swift-native | — | **BUILD later** → `DzzloClip` | iOS |
| Google Play Instant | — | — | shut down Dec 2025 | SKIP | Android |

### 1.8 Biometrics, passkeys, secure storage, sign-in, integrity

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-biometrics` | 3.0.1 — dated 2022-09-06 (ecosystem) and 2025-12-12 (iOS note) | Old | St | SKIP | — |
| `@sbaiahmed1/react-native-biometrics` | 0.16.1 (2026-09-08) | TM (ecosystem, Android notes); "Expo module" (iOS note) — conflict | A · 23k/wk, 121 stars | USE candidate | both |
| `expo-local-authentication` | 57.0.3 (2026-09-11) | Expo | A · 1.56M/wk | SKIP · Expo track | both |
| `react-native-keychain` | 10.0.0 (2025-03-23) | TM | S/St — no release in 18 months · 554k/wk | USE (token storage, biometric access control) | both |
| `expo-secure-store` | 57.0.4 (2026-09-11) | Expo | A | SKIP · Expo track | both |
| `react-native-mmkv` | 4.3.2 (2026-06-22) | Nitro | A · 1.65M/wk | alt. for non-secret cache | both |
| `react-native-sensitive-info` | 6.1.5 (2026-06-30) | Nitro | A | alt. | both |
| `react-native-encrypted-storage` | 4.0.3 (2022-11-03) | Old, archived | U | SKIP | — |
| `react-native-passkey` | 3.6.2 (2026-09-08) | Directory New-Arch true | A · 135k/wk | SKIP for v1 | both |
| `react-native-passkeys` | 0.4.2 (2026-08-05) | — | A | SKIP | both |
| `react-native-credentials-manager` | 0.9.0 (2026-09-17) | TM; Android only | A | SKIP | Android |
| `@invertase/react-native-apple-authentication` | 2.5.1 (2026-03-31) | New-Arch | — | SKIP (guideline 4.8 is not triggered by OTP login) | iOS |
| `@react-native-google-signin/google-signin` | 16.1.5 (2026-09-03) | New-Arch (Directory) | the free "Original" build uses the deprecated legacy SDK | SKIP (would trigger 4.8) | both |
| `@expo/app-integrity` | 57.0.2 (2026-09-11) | Expo | — | SKIP · Expo track (App Attest / Play Integrity) | both |
| `LAContext` (iOS 8.0) · `BiometricPrompt` (androidx.biometric) | platform | — | — | not wrapped — Phase 9 uses `react-native-keychain` behind `src/native/appLock.js` | both |

### 1.9 OTA updates

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `hot-updater` / `@hot-updater/react-native` | 0.36.16 (2026-09-29); `rc` tag 1.0.0-rc.19 | New Arch; `bare({ enableHermes: true })` | A · 114 releases in 12 months · 1,743 stars | USE ([[09-phase-9-security-privacy-and-release]]) | both |
| `expo-updates` (EAS Update) | 57.0.24 (2026-09-29); `sdk-55` line 55.0.33 | Expo | A · 4.3M/wk | SKIP · Expo track | both |
| `@revopush/react-native-code-push` | 2.6.2 (2026-09-13) | CodePush-compatible (hosted) | 12k/wk | alt. | both |
| `react-native-stallion` | 2.4.2 (2026-08-08) | CodePush-compatible (hosted) | 9k/wk | alt. | both |
| `react-native-update` (Pushy) | 10.59.1 (2026-09-29) | — | 5k/wk | SKIP | both |
| `react-native-code-push` | 9.0.1 (2024-12-19) | no New Arch | U — archived; hosted service retired 2025-03-31 | SKIP | — |

### 1.10 Bluetooth thermal printers

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-thermal-receipt-printer` | 1.2.0-rc.2 (2023-12-06) | Old | U-like · 80 open issues | SKIP | — |
| `react-native-thermal-receipt-printer-image-qr` | 0.1.12 (2024-09-16) | Old | St | SKIP | — |
| `react-native-bluetooth-escpos-printer` | 0.0.5 (2019-01-05) | Old | U | SKIP | — |
| `@haroldtran/react-native-thermal-printer` | 1.2.0 (2026-03-04) | — | S · 20 stars | SKIP | — |
| `react-native-esc-pos-printer` | 4.5.0 (2025-10-24) | TM | S — Epson TM printers only | SKIP until hardware is chosen | both |
| `react-native-star-io10` (Star Micronics, official) | 1.14.0 (2026-09-15) | Old | A — Star hardware (dual-chip MFi) | SKIP until hardware is chosen | both |
| `react-native-ble-manager` | 12.5.3 (2026-09-21) | TM | A — generic BLE | SKIP until demand | both |
| `react-native-ble-plx` | 3.5.1 (2026-02-18) | Directory New-Arch true | S — BLE only | SKIP until demand | both |
| `react-native-bluetooth-classic` | 1.73.0-rc.17 (2025-11-19) | Old | S (release candidates only) | SKIP until demand | Android |
| `react-native-earl-thermal-printer` | 2.0.1 (2026-08-10) | TM | 63/wk | SKIP | both |

Cheap printers are usually Bluetooth Classic (SPP/RFCOMM), which iOS apps cannot use unless the accessory is MFi-certified — a Classic-only printer never shows up in an iOS scan (search summary).

### 1.11 Contacts, OTP, UPI, clipboard, haptics, permissions, storage, look

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-contacts` | 8.0.10 (2026-01-28) | TM | S — full address-book access | SKIP | both |
| `expo-contacts` | 57.0.6 (2026-09-18) | Expo | A | SKIP · Expo track | both |
| `react-native-select-contact` | 1.6.3 (2021-06-04) | Old | U | SKIP | — |
| `react-native-contact-picker` | 0.0.5 (2017-09-28) | Old | U | SKIP | — |
| Android 17 Contact Picker `ACTION_PICK_CONTACTS` (API 37; legacy `ACTION_PICK` auto-upgraded) · the iOS system contact picker | platform | — | — | WRAP, not scheduled | both |
| `react-native-otp-verify` | 1.2.0 (2026-04-03) | not New-Arch | S | SKIP | Android |
| `@pushpender-singh-ap/react-native-otp-verify` | 1.2.0 (2025-10-15) | TM | S — "zero-permission SMS verification" | alt., only if SMS OTP | Android |
| `@ebrimasamba/react-native-sms-retriever` | 2.1.1 (2026-06-05) | New-Arch (Directory) | 1.8k/wk | USE only if the OTP arrives by SMS | Android |
| `react-native-sms-retriever` | 1.1.1 (2020-01-02) | Old | U | SKIP | — |
| `@eabdullazyanov/react-native-sms-user-consent` | 1.3.0 (2025-11-17) | — | S | SKIP | Android |
| core `textContentType="oneTimeCode"` | core | — | — | USE (iOS 17+ fills codes from Mail) | iOS |
| `react-native-upi-payment` / `react-native-upi-pay` | 1.0.5 (2023-10-02) / 1.0.8 (2020) | Old | U | SKIP — `Linking.openURL('upi://pay?…')` instead | — |
| `@react-native-clipboard/clipboard` | 1.16.3 (2025-06-28) | TM | St · 73 open issues | USE when needed | both |
| `expo-clipboard` / `expo-haptics` | 57.0.2 / 57.0.3 (2026-09-11) | Expo | A | SKIP · Expo track | both |
| `react-native-haptic-feedback` | 3.0.0 (2026-03-29) | TM | S | USE when needed | both |
| `react-native-permissions` | 5.6.2 (2026-09-14) | TM | A · 6 open issues | USE when a permission-gated feature ships — the user reverses the 2026-07-05 decision first | both |
| `react-native-signature-canvas` | 5.1.1 (2026-08-06) | — | A · 82 open issues | SKIP now (proof-of-delivery later) | both |
| `react-native-nitro-modules` | 0.37.1 (2026-08-27) | Nitro runtime | A · 2.0M/wk · 50 releases in 12 months | arrives with VisionCamera 5; SKIP for our own modules | both |
| `@op-engineering/op-sqlite` | 18.2.5 (2026-09-20) | TM | A | offline-first — outside this course | both |
| `expo-sqlite` | 57.0.3 (2026-09-11) | Expo | A | SKIP · Expo track | both |
| `@nozbe/watermelondb` | 0.28.0 (2025-04-07) | Old | St | SKIP | both |
| `react-native-edge-to-edge` | 1.8.2 (2026-09-14) | New-Arch (GitHub-detected) | 555k/wk | not evaluated — v2 screens use `react-native-safe-area-context` | Android |
| `@callstack/liquid-glass` | 0.8.2 (2026-09-16) | TM (iOS) | A | SKIP — Liquid Glass arrives with the iOS 27 SDK anyway | iOS |
| `expo-glass-effect` | 57.0.4 | Expo (iOS) | — | SKIP | iOS |

### 1.12 Store rating and review

Read 2026-09-30 for the store-review note: versions and dates from the npm registry and the published tarballs, New-Architecture flags from the React Native Directory API, downloads for 21–27 Sep 2026. The full comparison is [[09-phase-9-security-privacy-and-release]] §9.3.

| Library | Latest (date) | Arch | Health | Verdict | Covers |
| --- | --- | --- | --- | --- | --- |
| `react-native-store-review` | 0.5.0 (2026-04-15) | TM (`RNStoreReviewSpec`, with an old-arch fallback) | S · 57k/wk · 2 open issues, 0 open PRs; the Android buildscript pins AGP 7.0.4 | alt. — the fallback if we own no native code here | both |
| `react-native-rate-app` | 2.1.3 (2026-09-07) | TM, New-Arch only | A · 7.2k/wk · one maintainer | alt. — its store-link helper needs `canOpenURL` and query declarations | both |
| `react-native-in-app-review` | 4.4.2 (2025-09-03) | Old (legacy bridge, no codegen; Directory New-Arch false) | St · 238k/wk · 31 open issues + 26 open PRs | SKIP | both |
| `expo-store-review` | 57.0.3 (2026-09-11); `next` 58.0.1 (2026-09-29) | Expo (iOS 16.4+ since 56.0.0) | A · 1.12M/wk | SKIP · Expo track | both |
| `react-native-rate` | 1.2.12 (2023-01-23) | Old | U — "unmaintained" (Directory) · 35k/wk | SKIP | — |
| `AppStore.requestReview(in:)` (iOS 16.0), with `SKStoreReviewController.requestReview(in:)` (iOS 14.0, deprecated 18.0) for iOS 15 · Play In-App Review, `com.google.android.play:review` 2.0.2 (2024-10-18) | platform | — | — | **WRAP** → `NativeStoreReview` | both |
| core `Linking` to the store page — `?action=write-review` on iOS; `market://`, then https, on Android | core | — | — | USE — the "Rate DZZLO" row in Help | both |

### 1.13 What we write ourselves

| Name | Kind | iOS API (version) | Android API (level) | Phase | Replaces · enables | Effort _(est.)_ |
| --- | --- | --- | --- | --- | --- | --- |
| `NativeAppInfo` | Turbo Module | bundle and device constants | package and build constants | 1 | replaces `react-native-device-info`; fixes `uniqueId` | ~10 getters, ~60 lines per platform |
| `NativePdf` | Turbo Module | `WKWebView.createPDF` (14.0) or `UIPrintPageRenderer` (4.2) | WebView print adapter (API 21 form) | 3 | replaces `react-native-html-to-pdf`; invoice PDFs | 2–3 d wrap; 4–7 d on iOS with AirPrint |
| `NativePrint` | Turbo Module | `UIPrintInteractionController` (4.2) | `PrintManager` | 3 | replaces `react-native-print` | ~2 d |
| `NativeDocScanner` (only if the plugin audit fails) | Turbo Module | `VNDocumentCameraViewController` (13.0) | ML Kit Document Scanner (Play services) | 4 | slip and meter capture without a CAMERA permission on Android | ~1 d Android; iOS within 4–8 d for scan + QR |
| `NativeUpload` (later) | Turbo Module | background `URLSession` (8.0) + the AppDelegate background-session hook | WorkManager `CoroutineWorker`; user-initiated jobs (Android 14) | 4 | replaces `react-native-background-upload` | ~1 week both |
| `NativeSharedStore` | Turbo Module | App Group container `group.in.vsyst.dzzlooms.shared` | a Kotlin store read by the widget | 6 | replaces `react-native-shared-group-preferences`; feeds widgets and intents | 1–2 d |
| `NativeShortcuts` | Turbo Module | `UIApplicationShortcutItem` (9.0) | dynamic App Shortcuts (API 25) | 6 | replaces `react-native-quick-actions`; role-based quick actions set after sign-in | ~1 d per platform |
| `NativeStoreReview` | Turbo Module | `AppStore.requestReview(in:)` (16.0); `SKStoreReviewController.requestReview(in:)` (14.0) on iOS 15 | Play In-App Review, `review` 2.0.2 (API 21+ with the Play Store) | 9 | replaces a review library (`react-native-store-review` 0.5.0 is the fallback); asks for a rating once, after a win | ~95 lines with boilerplate, ~40 of them logic |
| `DzzloWidgets` | iOS Widget Extension target | ActivityKit (16.1), WidgetKit (14.0), Controls (18.0) | — | 5, 6 | Live Activity; Daily Summary widget; a "New order" Control | 5–8 d (Live Activity) + 8–15 d (first widget) |
| Kotlin `NotificationServiceExtension` | OneSignal extension class | — | `ProgressStyle` (API 36); `NotificationCompat` below | 5 | Android Live Updates | 3–6 d incl. server |
| `DailySummaryWidget` | Glance app widget | — | Glance 1.2.0 (minSdk 23) | 6 | the Android widget | 5–8 d |
| "Outstanding balance" intent | Swift in the app target | `AppIntent`, `AppShortcutsProvider` (16.0) | — | 6 | Siri, Shortcuts, Spotlight | part of a 10–20-day starter set |
| `DzzloClip` (later) | App Clip target | App Clip (`APActivationPayload`, iOS 14.0) | — (no twin) | 8 | "view and pay this invoice" without installing | 10–20 d + web and server |
| App Group `group.in.vsyst.dzzlooms.shared` | entitlement | App Groups | — | 6 | app ↔ `DzzloWidgets` data; OneSignal's group stays untouched | account-holder set-up |

Not built: `NativeBiometrics` — [[09-phase-9-security-privacy-and-release]] found the libraries adequate and puts `react-native-keychain` behind `src/native/appLock.js`.


## 2. Versions as Measured

### 2.1 Toolchain

| Tool | Version | Where it was read |
| --- | --- | --- |
| Xcode | 27.0 (27A266a) ✅ | `xcodebuild -version` |
| Swift toolchain | 6.4 (swiftlang-6.4.0.34.1, clang-2100.3.34.1) ✅ | `swift --version` |
| Swift language mode in the targets | 5.0; no `SWIFT_OBJC_BRIDGING_HEADER` | `project.pbxproj` |
| C++ standard | c++20 / gnu++20 | `project.pbxproj` |
| CocoaPods | 1.15.2; Gemfile `cocoapods >= 1.13, != 1.15.0, != 1.15.1`, `xcodeproj < 1.26.0` | `Podfile.lock`, `Gemfile` |
| Hermes | `hermes-engine` 250829098.0.9 | `Podfile.lock` |
| Node | `engines >= 22.11.0`; CI Node 22; `ios/.xcode.env.local` pins Homebrew node 26.3.0 | `package.json`, `.xcode.env` |
| Kotlin | 2.1.20 | `android/build.gradle` |
| Android Gradle Plugin | 8.12.0 | RN Gradle-plugin `libs.versions.toml` |
| Gradle | 9.0.0 | wrapper |
| NDK | 27.1.12297006 | `android/build.gradle` |
| buildTools / compileSdk / targetSdk / minSdk | 36.0.0 / 36 / 36 / 24 | `android/build.gradle` |
| ABIs | armeabi-v7a, arm64-v8a, x86, x86_64 (`gradle.properties:28`) | `gradle.properties` |
| Firebase Gradle plugins | google-services 4.4.4 · firebase-crashlytics-gradle 3.0.6 · perf-plugin 2.0.2 | `android/build.gradle` |
| OneSignal native SDKs | OneSignalXCFramework 5.5.0 (Complete: InAppMessages, LiveActivities, Location) · `com.onesignal:notifications:5.7.6` | `Podfile.lock`, merged manifest |
| Jest · Testing Library · msw · TypeScript | ^30.3.0 · ^13 · ^2 · ^6.0.2 | `package.json` |
| `@react-native-community/cli` | 20.1.3 | `package.json` |
| RN core's own Android test stack (reference versions for ours) | JUnit 4.13.2 · AssertJ 3.21.0 · mockito-inline 3.12.4 · mockito-kotlin 3.2.0 · Robolectric 4.15.1 | RN 0.84.1 `gradle/libs.versions.toml` |
| Machine | MacBook Pro M5 Max, macOS 27.0 (26A428) | `sw_vers` |

> **After the upgrade to 0.87:** AGP 9 with the opt-outs `android.builtInKotlin=false` and `android.newDsl=false` ("from AGP 10.x these opt-outs will be removed"); compileSdk and buildTools 37 (`minCompileSdk` 34); Kotlin 2.0+ (bundled 2.2.0); Node ≥ 22.13.0; the Jest preset becomes `@react-native/jest-preset` (extracted in 0.85; "must be consumed as package" in 0.87).

### 2.2 App dependencies — installed vs latest

| Package | Installed (date) | Latest (date) | Native | Verdict |
| --- | --- | --- | --- | --- |
| `react-native` | 0.84.1 (2026-02-27) | 0.87.1 (see §2.7 on its date) | core | KEEP; upgrade |
| `react` | 19.2.3 (pinned by RN 0.84) | 19.3.0 on npm | — | KEEP |
| `@gorhom/bottom-sheet` | 5.2.8 (2025-12-04) | 5.2.14 (2026-05-09) | JS | KEEP |
| `@react-native-async-storage/async-storage` | 3.0.2 (2026-03-26) | 3.1.1 (2026-05-29) | codegen | KEEP |
| `@react-native-community/datetimepicker` | 9.1.0 (2026-03-17) | 9.2.1 (2026-09-07) | codegen | KEEP |
| `@react-native-community/netinfo` | 12.0.1 (2026-02-14) | same | codegen | KEEP |
| `@react-native-firebase/{app,analytics,crashlytics,perf}` | 24.0.0 (2026-04-01) | 26.4.0 (2026-09-05) | compat layer | KEEP; upgrade separately |
| `@react-navigation/bottom-tabs` · `drawer` · `elements` · `native` · `native-stack` | 7.15.9 · 7.9.8 · 2.9.14 · 7.2.2 · 7.14.10 | 7.19.2 · 7.14.2 · 2.9.43 · 7.4.1 · 7.19.2 (modified 2026-09-22) | JS | KEEP |
| `@react-navigation/stack` | 7.8.9 (2026-03-28) | 7.11.2 (2026-09-17) | JS | REMOVE — no importer |
| `@reduxjs/toolkit` · `react-redux` | 2.11.2 · 9.2.0 | 2.13.0 (2026-09-29) · 9.3.0 | JS | KEEP |
| `@shopify/flash-list` | 2.3.1 (2026-03-23) | 2.3.2 (2026-06-10) | JS (v2) | KEEP |
| `moment` | 2.30.1 (2023-12-27) | 2.31.0 (2026-09-15) | JS | REPLACE — "a legacy project, now in maintenance mode" |
| `react-native-device-info` | 15.0.2 (2026-02-21) | same | compat layer | REPLACE → `NativeAppInfo` |
| `react-native-gesture-handler` | 2.31.0 (2026-04-02) | 3.3.0 (2026-09-11) | codegen | KEEP; major on its own |
| `react-native-html-to-pdf` | 1.3.0 (2025-09-04) | same | codegen | REMOVE |
| `react-native-linear-gradient` | 2.8.3 (2023-09-06) | same | compat layer | REPLACE → svg |
| `react-native-onesignal` | 5.4.1 (2026-03-25) | 5.5.14 (2026-09-23) | codegen | KEEP; upgrade |
| `react-native-paper` | 5.15.0 (2026-02-04) | 5.15.3 (2026-05-26) | JS | KEEP |
| `react-native-reanimated` · `react-native-worklets` | 4.3.0 (2026-03-25) · 0.8.1 (2026-03-20) | 4.7.0 · 0.13.0 (2026-09-18) | codegen | KEEP; upgrade together |
| `react-native-safe-area-context` | 5.7.0 (2026-02-24) | 5.10.1 (2026-09-29) | codegen | KEEP |
| `react-native-screens` | 4.24.0 (2026-02-23) | 4.28.0 (2026-09-14; the iOS note read 2026-09-28) | codegen | KEEP |
| `react-native-svg` | 15.15.4 (2026-03-18) | 15.15.5 (2026-05-11) | codegen | KEEP |
| `react-native-webview` | 13.16.1 (2026-02-27) | 14.0.1 (2026-06-20) | codegen | KEEP; major on its own |

Compatibility of gesture-handler 3.3.0, webview 14.0.1, reanimated 4.7.0 and worklets 0.13.0 with RN **0.84.1** specifically was not verified; none of these upgrades belongs inside a native-module change.

### 2.3 Operating systems and store deadlines

| Item | Version or date | Notes |
| --- | --- | --- |
| iOS 27 / iPadOS 27 / Xcode 27 | announced 2026-06-08 (WWDC); released 2026-09-14 | dates via news coverage and Wikipedia summaries |
| App Store Connect SDK floor | iOS 26 SDK, since 2026-04-28 | the deployment target stays the developer's choice |
| UIScene life cycle | required when building with the iOS 27 SDK | TN3187 ✅, WWDC26 session 278 ✅ |
| Liquid Glass | `UIDesignRequiresCompatibility` (iOS 26.0) ignored for iOS 27 builds | ✅ |
| Siri AI (iOS 27) | iPhone 15 Pro and later; English (Australia, Canada, Ireland, India, New Zealand, South Africa, UK, US) at launch; not in the EU on iPhone / iPad at launch, not in China | more languages from October (search snippet) |
| Android 16 (API 36) | major release Q2 2025; QPR1 to Pixels from 2025-09-03 (full Live Updates treatment); QPR2 = API 36.1 | minor SDK read via `SDK_INT_FULL` |
| Android 17 (API 37) | stable 2026-06-16, Pixel 6 and later; QPR1 / QPR2 betas = API 37.1 / 37.2 | hub page updated 2026-07-01 |
| Samsung / Xiaomi Live Update surfaces | One UI 8 Now Bar (Android 16); One UI 9 (Android 17) adds MetricStyle categories; HyperOS 3.1 Super Island | secondary reporting |
| Play target API | API 36 for new apps and updates from 2026-08-31; extension to 2026-11-01; Wear / Automotive 35, TV / XR 34 | a 2027 date is not published yet |
| Play 16 KB page sizes | updates blocked from 2027-02-01 (Google's page) | older guidance: 2025-11-01, extendable to 2026-05-31 — §2.7 |
| Play location button | apps targeting 37 whose precise location is one-time must use it from 2027-01-27 | — |
| Android developer verification | enforced 2026-09-30 in Brazil, Indonesia, Singapore, Thailand; global on certified devices in 2027 | secondary for the timeline |
| India Android mix, Aug 2026 (StatCounter) | 16 = 24.11 % · 15 = 23.28 % · 13 = 13.85 % · 14 = 12.14 % · 12 = 9.41 % · 11 = 8.81 % | the remaining ~8.4 % (≤ 10 and 17) not broken out |

### 2.4 React Native releases that matter to native modules

| Release | Date | What changed for module authors |
| --- | --- | --- |
| 0.79 | 2025-04-08 | JavaScriptCore moved to `@react-native-community/javascriptcore` (search summary) |
| 0.80 | 2025-06-12 | Legacy Architecture frozen, with warnings; deep imports deprecated; Strict TypeScript API opt-in |
| 0.81 | 2025-08-12 | targets Android 16 by default; `edgeToEdgeEnabled` Gradle property; built-in `SafeAreaView` deprecated; predictive back on at target 36 |
| 0.82 | 2025-10-08 | New Architecture only; interop layers kept "for the foreseeable future"; Gradle 9.0.0; `JSONArguments` removed; uncaught promise rejections now raise `console.error` |
| 0.83 | 2025-12-10 | "no breaking changes" |
| **0.84** (the app) | 2026-02-11 | Hermes V1 by default; precompiled iOS binaries by default (`RCT_USE_PREBUILT_RNCORE=0` to opt out); legacy architecture left out of iOS builds; 14 legacy Android classes removed (incl. `LazyReactPackage`, `CxxModuleWrapper`, `CallbackImpl`); `TurboModuleProviderFunctionType` deprecated; `RCTImage` observer change; Node 22.11+ |
| 0.85 | 2026-04-07 | new animation backend; Jest preset extracted to `@react-native/jest-preset`; C++ `ShadowNode::Shared` aliases and `CatalystInstanceImpl` removed; duplicate-symbol fix for `React.XCFramework` |
| 0.86 | 2026-06-11 | "no breaking changes" |
| **0.87** (latest) | 2026-08-11 | Strict TypeScript API by default; Metro update; Swift Package Manager (experimental, "do not use it in production yet"); AGP 9 + compileSdk 37; `useTurboModules` flag removed; `RCTTurboModuleEnabled()` deprecated; `UIBlock` deprecated; Node ≥ 22.13.0 |
| 0.88 | release candidate | paired with Expo SDK 58 beta |

A module built only on the documented surface — spec + codegen, `BaseReactPackage`, the generated base classes, `getTurboModule:` / `RCTModuleProvider`, `CodegenTypes.EventEmitter` — survives 0.82 → 0.87 largely untouched; the recurring costs are toolchain bumps, iOS include hygiene (`#import <React/…>`) and a new minor about every two months.

### 2.5 Expo SDK ↔ React Native pairing

| Expo SDK | React Native (from `bundledNativeModules.json`) | React | Min iOS | Min Android | Xcode | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 54 | 0.81 (0.81.5) | 19.1.0 | 15.1+ | — | 16.1+ | — |
| 55 | 0.83 (0.83.10) | 19.2.0 | 15.1+ | — | 26.2+ | `sdk-55` lines still patched (e.g. `expo-updates` 55.0.33 on 2026-09-29) |
| 56 | 0.85 (0.85.3) | 19.2.3 | 16.4+ | 7+ | 26.4+ | first SDK with `expo-widgets` |
| 57 | 0.86 (0.86.3) | 19.2.3 | 16.4+ | 7+ | 26.4+ | npm `latest` 57.0.26 |
| 58 beta (2026-09-15; npm `next` 58.0.0) | 0.88 RC (0.88.0-rc.3) | — | — | — | — | adds Android widgets to `expo-widgets`; `expo-app-intents` alpha |

**Nothing pairs with 0.84 or 0.87.** The `expo` package declares `react-native: "*"` as a peer for SDK 55 and 56, so npm does not block an install on 0.84 — running SDK 55 packages on RN 0.84 is possible but unsupported and untested. The Expo track in this course is taken only after an upgrade to an Expo-paired RN version (0.85 → SDK 56, 0.86 → SDK 57, 0.88 → SDK 58).

### 2.6 Platform SDKs and frameworks

| Item | Version (date) | Notes |
| --- | --- | --- |
| Jetpack Glance | 1.2.0 stable (2026-08-26); 1.3.0-alpha02 (2026-07-01) | minSdk 23 since 1.2.0-beta01; 1.1.0 (Jun 2024) added generated previews and the unit-test library |
| CameraX | 1.6.2 (2026-08-26) | minSdk 23 since 1.5.0-rc01; 1.6.0 (2026-03-25) moved to CameraPipe; `camera-mlkit-vision` 1.7.0-alpha03 (2026-08-12) |
| Maps SDK for Android | 20.0.0 (2026-01-31) | minSdk 21; v20 removed `org.apache.http.legacy` |
| androidx.pdf | 1.0.0-beta01 (2026-08-26) | partly unverified (search results) |
| androidx.appfunctions | alpha | "currently in alpha" (Android 17 launch post) |
| Nitro Modules | 0.37.1 (2026-08-27) | no 1.0; 0.36.2 (2026-07-27) added "React Native 0.87+ support" |
| OneSignal React Native | 5.5.14 (2026-09-23) | README: RN ≥ 0.79 needed for 5.4.x and later; Live Activities need 5.2.0+ |
| React Native Firebase | 26.4.0 (2026-09-05) | whether 26.x adopted `codegenConfig` was not checked |
| Hot Updater | 0.36.16 (2026-09-29); `rc` 1.0.0-rc.19 | licence and RN 0.84 test matrix not captured |

### 2.7 Where the notes disagree

| Topic | One source says | Another says | What the course does |
| --- | --- | --- | --- |
| React Native 0.87.1's date | 0.87 released 2026-08-11 (RN blog) | npm 0.87.1 published 2026-08-26 (audit); npm "latest = 0.87.1 (2026-09-28)" (iOS note, likely the registry's modified time) | "0.87 released 2026-08-11; 0.87.1 is npm latest on 2026-09-29" |
| Play 16 KB deadline | 2027-02-01 for updates (Google's page) | 2025-11-01, extendable to 2026-05-31 (older third-party guidance) | follows Google's page; re-check before shipping |
| Live Update promotion version | "Android 16 QPR1 (API 36.1)" (OneSignal) | API 36.1 is Android 16 **QPR2** (Google) | checks `canPostPromotedNotifications()`, never a version |
| Live Updates settings deep link | `Settings.ACTION_MANAGE_APP_PROMOTED_NOTIFICATIONS` (Google's Live Updates guide, as the Android note read it) | no such constant in the SDK's `api-versions.xml` (36, 36.1, 37); it has `Settings.ACTION_APP_NOTIFICATION_PROMOTION_SETTINGS` (API 36) | codes against the SDK ([[05-phase-5-notifications-and-live-status]] §6.5) |
| `react-native-notify-kit` latest | 10.8.0 (2026-09-29) — iOS and ecosystem notes | 10.7.2 (2026-09-23) — Android note's Directory read | 10.8.0 |
| `react-native-image-crop-picker` latest | 0.52.0 (2026-09-29) | 0.51.1 (2025-10-21) | 0.52.0 (the later read) |
| `react-native-screens` latest date | 4.28.0 (2026-09-14) — audit | 4.28.0 (2026-09-28) — iOS note | version agrees; date unresolved |
| `expo-app-intents` | 0.0.1 published 2026-09-29, alpha, documented for SDK 58 (iOS note) | 0.0.1 dated 2026-06-08, no description or repository (ecosystem note) | SKIP either way |
| `react-native-document-scanner-plugin` | ships a `codegenConfig` (TM) and its Android side depends on `play-services-mlkit-document-scanner` 16.0.0 (ecosystem) | "built as an Expo module" per the Directory (iOS note); Android backend unverified (Android note) | audit 2.0.4 first ([[04-phase-4-images-and-scanning]]): a plain TurboModule is used as it is; only an Expo build makes the course write `NativeDocScanner` |
| A scanner module at all | "Do not write a native module" for capture (DU-slips spec, decision D5) | the course's module list includes `NativeDocScanner` | resolved by the same audit gate — the module exists only if no healthy wrapper does |
| `@sbaiahmed1/react-native-biometrics` | TM / New-Arch (ecosystem, Android) | "Expo module" (iOS note table) | a USE candidate, verified before adoption |
| `react-native-biometrics` 3.0.1's date | 2022-09-06 (ecosystem) | 2025-12-12 (iOS note) | SKIP either way |
| `react-native-html-to-pdf` | New-Arch TurboModule (Directory); "USE, watch" (ecosystem) | slow-moving, doubtful New-Arch support, inconsistent margins (a 2026 guide); never called here (audit) | removed; `NativePdf` |
| WhatsApp to a contact on iOS | `shareSingle` supports WHATSAPP with `whatsAppNumber` on iOS and Android (react-native-share docs) | "It is not possible to send a file directly to a WhatsApp contact" (iOS issue #1699) | share sheet on iOS; `shareSingle` on Android |
| Microsoft's `code-push-server` | published for self-hosting (Microsoft Learn) | archived and read-only since May 2025 (search summary) | not used; Hot Updater |
| Apple's interpreted-code clause | DPLA 3.3.1(B) | "Guideline 3.3.2" | quotes the text, not the number |
| SiriKit | "formally deprecated at WWDC26" (a secondary blog) | no deprecation on Apple's pages on 2026-09-29 | UNVERIFIED; App Intents regardless |
| Android Live Updates from RN | "no third-party library supports them" (freeCodeCamp, 2026-07-14) | Voltra merged support on 2026-09-28, unreleased | own Kotlin extension; watch Voltra |
| iOS pod linkage | "the Podfile builds dynamic frameworks" (the brief; one line of the iOS note) | 40 static-library targets, 0 frameworks; `use_frameworks!` only with `USE_FRAMEWORKS` set (audit) | static, as measured |
| `SceneDelegate` | a separate `SceneDelegate.swift` (the brief) | a class inside `AppDelegate.swift:41-58` (audit) | as measured |
| Incoming URLs | the app "already declares `CFBundleURLTypes`" for `Linking` (iOS note) | the only scheme is Google's reversed client id; nothing handles incoming URLs (audit) | [[08-phase-8-instant-experiences-and-links]] adds links |
| `Linking.canOpenURL` on Android 11+ without a `<queries>` entry | the Promise rejects (RN's Linking docs; the first draft of the brief) | resolves `false` — RN 0.84.1's `IntentModule.kt` rejects only when an exception is thrown ([[02-phase-2-dependency-diet]] §5.3) | "resolves `false`; RN's docs say it may reject" — the `<queries>` fix is the same either way |
| OTP channel | SMS Retriever autofill ranked #2 (Android note, assumes SMS) | "Email OTP works"; SMS Retriever matters only if SMS OTP is added (ecosystem) | the login accepts an email **or** a phone number (`ForgotPassword.js:47`) — confirm the channel before building autofill |
| WhatsApp utility message price (India) | ₹0.1150 + GST (effective 2026-07-01) | ₹0.145 | both recorded; server-side, out of scope |
| Source-file census | 852 `.js` + 1 `.ts` in `src/` (the brief) | 855 `.js` + 2 TS files (audit) | both true: the audit also counts `App.js`, `index.js` and `__tests__/` |
| "Xcode 27 rejects deployment targets below iOS 15" | the team's Podfile comment | not checked against Apple's documentation | stated as the team's note |
| App Review Guidelines page date | no "last updated" date on the page (read 2026-09-29, iOS note) | "Updated: June 8, 2026" (read 2026-09-30, store-review note) | the rating clauses in §4.1 cite the June 8, 2026 page; neither the 13 Nov 2025 nor the 8 Jun 2026 revision touched ratings |
| The App Store clause behind "use the review API" | 1.1.7 (the brief's first draft of the store-review scope) | 5.6.1 App Store Reviews; 1.1.7 is "Harmful concepts which capitalize or seek to profit on recent or current events…" (store-review note, verbatim) | 5.6.1, with 3.2.2 (x), 5.6.3 and the Introduction |
| Hindi in the iOS review sheet | declare `hi` in `CFBundleLocalizations` — "a one-line fix to test" (store-review note) | v1.79 removed the OS-level Hindi registration by the user's decision of 2026-09-25, and `src/i18n/__tests__/locales.config.test.js` pins its absence (repo, read 2026-09-30) | an English sheet for now; the declaration returns with the release that unlocks Hindi |

---

## 3. Effort Table

Every figure is an estimate from the notes for one JS-first engineer working test-first — _(est.)_ throughout, uncalibrated against this codebase. The iOS note's figures include Jest red → green, an XCTest target and device checks at 320 pt × fontScale 1 in en + hi, and exclude App Review waits; the Android note says to add 20–30 % for device checks on Samsung, Xiaomi and a Pixel; the ecosystem note's figures are its authors' opinion. "d" = working days, "wk" = weeks.

| Capability | iOS (iOS note) | Android (Android note) | Both platforms (ecosystem note) | Course home |
| --- | --- | --- | --- | --- |
| Share sheet, export to Files / SAF, Quick Look | 2–4 d | export / save / share 2–3 d | WhatsApp share of PDF + image 2–4 d | Phase 3 · Capstone A |
| Native PDF | 4–7 d with AirPrint | via `expo-print` 1–2 d; fully native `PdfDocument` + Canvas 5–10 d | WKWebView / `PrintedPdfDocument` wrap ~2–3 d | `NativePdf` |
| System print dialog | inside the 4–7 d above | — | ~2 d | `NativePrint` |
| Background export (`BGContinuedProcessingTask`, iOS 26+) | 3–5 d | — | — | Phase 3 stretch |
| Notification categories, interruption levels, threads, badge | 3–5 d (+ server) | notification hardening 2–4 d | push with action buttons 3–5 d | Phase 5 |
| Notification Content Extension | 5–8 d | — | — | skipped |
| In-app messages | 1–3 d | 0.5–2 d | 1 d | Phase 5 |
| Live Activity / Live Update | OneSignal default 5–8 d (+ server); custom attributes + own APNs 10–15 d | 4–6 d incl. server | iOS 1–2 wk; Android 3–5 d | Phase 5 · Capstone B |
| First widget + App Group snapshot + logout wipe | 8–15 d | Glance 5–8 d; JSX library 3–5 d | 2–3 wk both | Phase 6 · Capstone C |
| Each further widget, or a Control / Quick Settings tile | 2–4 d each | tile 1–2 d | — | Phase 6 |
| Widget push reloads (iOS 26+) | 3–5 d | — | — | Phase 6 |
| App Intents starter set (3–5 intents, App Shortcuts, Spotlight entities, shared-Keychain token) | 10–20 d | AppFunctions: 2–3 d spike, 5–8 d full (defer) | Siri / AppFunctions 1–2 wk per platform (skip) | Phase 6 |
| Interactive snippet (iOS 26+) | 3–5 d | — | — | Phase 6 stretch |
| Shortcuts / quick actions | "a few lines in SceneDelegate" | static + dynamic 1–2 d; pinned +0.5–1 d | 1–2 d | `NativeShortcuts` — ~1 d per platform (Phase 6) |
| Assist content (`onProvideAssistContent`) | — | 1 d | — | optional |
| Camera QR (e-invoice) + document scan | 4–8 d | scanner 1–2 d; QR 1–2 d (+1 d server JWT check) | photo / scan evidence 1 wk; IRN QR + server verify 3–5 d | Phase 4 |
| Photo Picker + camera | — | 1 d | — | Phase 4 |
| OCR of DU slips | 8–15 d | 2–4 d | 1–3 wk — skip until a spike | skipped |
| Background upload | 5–8 d | 3–5 d | ~1 wk | `NativeUpload` |
| Customer map | 3–6 d | 2–4 d | navigation deep link < 1 d | Phase 7 |
| Live tanker tracking + geofence | 15–30 d (+ server) | 6–10 d own; 2–3 d with the paid library | 4–8 wk | skipped |
| App Clip | 10–20 d (+ web / server) | App Links 1–2 d in the app (+ the web invoice page) | skip | Phase 8, later |
| Biometric lock | 2–4 d | 1–2 d | 2–3 d | Phase 9 |
| Passkeys | 8–15 d (+ server) | 5–10 d incl. server | skip for v1 | skipped |
| App Attest / Play Integrity | 5–10 d (+ server) | 2–4 d incl. server | — | optional |
| OTP autofill | — | SMS Retriever 1–2 d (+ an SMS template re-approval under India's DLT rules — unverified) | iOS `textContentType` < 0.5 d | Phase 9 |
| Store rating prompt (`NativeStoreReview`, the policy helper, the "Rate DZZLO" row) | — | — | — | Phase 9 §9 — the store-review note sizes the module at ~95 lines with boilerplate, ~40 of them logic; no day figure |
| Bluetooth ESC/POS printing | — | 5–8 d incl. a printer matrix | 2–3 wk | skipped |
| Contact picker | — | — | 1–2 d | not scheduled |
| UPI link / QR on invoices and reminders | — | — | 2–3 d | Phase 8 |
| OTA (Hot Updater) | — | — | ~1 wk | Phase 9 |
| Offline-first capture + sync | — | — | 3–6 wk | outside this course |
| Shared store for native surfaces | — | 1–2 d | — | `NativeSharedStore` |
| OEM "keep Dzzlo OMS running" guide | — | 1–2 d | — | Phase 5 |
| iOS 27 SDK hygiene (Liquid Glass, resizing, orientation) | 2–5 d, yearly | — | — | Phase 9 |

---

## 4. The Review and Policy Map

### 4.1 App Store Review Guidelines

Clause texts as fetched on 2026-09-29 (the page shows no last-updated date). Short paraphrases; the phases quote the lines they depend on.

| Clause | What it says | Where it binds DZZLO |
| --- | --- | --- |
| Introduction | no manipulating reviews or chart rankings "with paid, incentivized, filtered, or fake feedback"; expulsion from the Developer Program is possible (read 2026-09-30) | no reward for a rating; no "Enjoying DZZLO?" question that sends only happy users to the sheet ([[09-phase-9-security-privacy-and-release]] §9) |
| 2.5.1 | only public APIs; run on the currently shipping OS; phase out deprecated frameworks and technologies | every phase — e.g. `CLGeocoder` (deprecated for MapKit), `openAppWhenRun` (deprecated for `supportedModes`) |
| 2.5.2 | self-contained bundles; no downloading code that introduces or changes features | OTA ([[09-phase-9-security-privacy-and-release]]) |
| 2.5.4 | background services only for their intended purposes (VoIP, audio, location, task completion, local notifications…) | `NativeUpload`, background export, any tracking |
| 2.5.11 | (i) sign up only for intents the app can handle alone; (ii) vocabulary and phrases pertain to the app, aliases relate to the app or company name, not generic terms; (iii) resolve directly, no ads between request and fulfilment | the "outstanding balance" intent (Capstone C) |
| 2.5.13 | facial recognition for authentication must use LocalAuthentication | biometric lock |
| 2.5.14 | explicit consent and a clear indication when recording — including any camera use | scanning, photo capture |
| 2.5.15 | file pickers should include the Files app and iCloud documents | document picker, export |
| 2.5.16 (a) | widgets, extensions and notifications relate to the app; every App Clip feature also in the main app; no ads in clips | `DzzloWidgets`, the NSE, `DzzloClip` |
| 3.1.1 | digital unlocks through in-app purchase; no license keys or QR codes to unlock | the web-billed dealer subscription |
| 3.1.3 intro, (c), (e), (f) | no steering away from IAP except the US storefront; enterprise services sold to organisations; physical goods must **not** use IAP; free companions to paid web tools, with no purchasing or calls to action | subscriptions, fuel orders, paying an invoice |
| 3.2.2 (x) | apps "must not force users to rate the app, review the app … in order to access functionality, content, or use of the app" (read 2026-09-30) | nothing waits on a rating: orders, invoices and Help work the same whether anyone rates or not |
| 4.4 | extensions carry some functionality; no marketing, advertising or IAP inside them | widgets, Live Activities |
| 4.5.3 | no spam or unsolicited messages through Apple services, "including … Push Notifications, Live Activities" | Capstone B |
| 4.5.4 | pushes not required to function; no sensitive or confidential information; promotions only after an explicit in-app opt-in, with an in-app opt-out | every push payload (no balances) |
| 4.7 | HTML5 / JavaScript mini apps and similar may run outside the binary | the framing for JS-only OTA |
| 4.8 | a third-party or social primary login needs an equivalent privacy-preserving option | not triggered by OTP on own accounts; Google sign-in would trigger it |
| 5.1.1 (ii) | purpose strings "clearly and completely describe" the use | the three location strings fail it; camera strings must name the use |
| 5.1.1 (iii), (iv) | request only data relevant to the core function; never trick or force consent | permission timing |
| 5.1.1 (v) | account creation implies in-app account deletion | login |
| 5.1.1 (ix) | highly regulated fields (banking, financial services) submitted by a legal entity | ledgers and payments → a company developer account |
| 5.1.2 | disclose and get permission before sharing personal data with third parties, including third-party AI | analytics SDKs, any AI feature |
| 5.1.5 | location only when directly relevant; notify and get consent | maps and tracking ([[07-phase-7-maps-and-location]]) |
| 5.6.1 | "Use the provided API to prompt users to review your app … and we will disallow custom review prompts"; replies to reviews carry no personal information, spam or marketing (read 2026-09-30) | `NativeStoreReview` asks StoreKit for its own sheet; "Rate DZZLO" is a store link, never the API |
| 5.6.3 | "Manipulating any element of the App Store customer experience such as charts, search, reviews, or referrals to your app … is not permitted" (read 2026-09-30) | no incentives, review swaps or paid review services |

**Other Apple submission rules.** Required-reason APIs must be declared in a privacy manifest (since 2024-05-01), with a manifest in every bundle that contains an executable or dynamic library using one; the app's `PrivacyInfo.xcprivacy` declares FileTimestamp (C617.1), UserDefaults (CA92.1, 1C8F.1, C56D.1), SystemBootTime (35F9.1) and DiskSpace (85F4.1) with no collected data. The iOS 26 SDK floor (2026-04-28). A social-media capability declaration for new versions from September 2026. Critical alerts need Apple's approval (health, safety, security, emergency). ITMS-90683 flags missing purpose strings for APIs a linked binary references — the reason the location strings stay. The Developer Program License Agreement allows downloaded interpreted code only if it does not change the app's primary purpose, create a storefront, or bypass signing, sandbox or security (quoted via Bitrise; clause numbering disputed). App Clip binaries: 10 MB (iOS 15 and earlier), 15 MB (iOS 16), 100 MB (iOS 17+, digital invocations only).

### 4.2 Google Play policies

| Policy | Rule and date | Features it touches | DZZLO today |
| --- | --- | --- | --- |
| Target API level | API 36 for new apps and updates from 2026-08-31; extension to 2026-11-01; existing apps must target 35+ to stay available to new users on newer Android versions | all | met ✅ |
| 16 KB page sizes | updates blocked from 2027-02-01 unless 16 KB-ready (apps targeting 35+, 64-bit devices); NDK r28+ and AGP 8.5.1+ align by default | any new `.so` — VisionCamera / Nitro, MMKV, Maps, bundled ML Kit | release APK aligned ✅ |
| Foreground services | per-type declaration in Play Console (description, user impact, video, use case); `dataSync` capped at 6 h in 24 h, with user-initiated jobs as the suggested alternative; `specialUse` reviewed | `NativeUpload` (prefer WorkManager / UIDT), tracking | none declared by the app (WorkManager merges `FOREGROUND_SERVICE`) |
| Background location | core functionality only; Permissions Declaration Form; a video (aim for ≤ 30 s); a prominent in-app disclosure using the word "location" plus a background phrase; one feature at a time | tanker tracking, geofences | deferred |
| Location button | from 2027-01-27, apps targeting 37 whose precise location is one-time and user-initiated must use Android 17's location button | "tag the outlet's GPS" | n/a until target 37 |
| Photo and video permissions | `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` only if system pickers are not enough; occasional use → Photo Picker; Console declaration; full compliance since 2025-05-28 | Phase 4 | use the picker |
| Exact alarms | `USE_EXACT_ALARM` restricted to policy use cases; `SCHEDULE_EXACT_ALARM` not pre-granted on Android 14+ | reminders | stay out — inexact alarms |
| Full-screen intents | default grant only for calling and alarm apps (target 14+); declaration opened 2024-05-31, enforcement 2025-01-22 | none | stay out |
| Battery-optimisation exemption | requesting it directly is prohibited unless the core function breaks; opening `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS` is allowed | the OEM guide | settings link only |
| Data safety | every data type collected or shared, including by SDKs; encryption in transit; deletion requests; mismatches can block updates | all — note `AD_ID` and AdServices from Firebase Analytics | review in Phase 9 |
| Device and Network Abuse | no downloading dex, JAR or `.so` from outside Play; code in a VM or interpreter (JavaScript) exempt | OTA | JS-only OTA |
| Developer verification | 2026-09-30 in four countries; global on certified devices in 2027 | distribution | plan for 2027 |
| Play Integrity quota | 10,000 requests a day by default | optional OTP hardening | — |
| SMS and Call Log permissions | not re-fetched; SMS Retriever avoids it, `READ_SMS` / `RECEIVE_SMS` would trigger it | OTP autofill | — |
| Live Updates | `POST_PROMOTED_NOTIFICATIONS` is a normal permission; no Console form found; usage criteria are platform guidance | Capstone B | — |
| Play Instant | shut down Dec 2025 | App Clip twin | none possible |
| User Ratings, Reviews, and Installs; In-App Review guidelines | no fraudulent or incentivised ratings; no question before or while the card shows ("Do you like the app?"); no button that triggers the API — "redirect the user to the Play Store instead"; the card surfaced as-is, with no overlay; a time-bound quota whose value is unpublished (guides updated 2026-01-30 and 2026-09-16; read 2026-09-30) | the review prompt and the "Rate DZZLO" row ([[09-phase-9-security-privacy-and-release]] §9) | no prompt today |

### 4.3 Feature → policy map, both stores

| Feature (phase) | Apple | Google Play / Android | Privacy label · Data safety | The DZZLO trap |
| --- | --- | --- | --- | --- |
| Share, export, PDF, print (3) | 2.5.15, 5.1.1 | none (SAF, FileProvider, owned MediaStore files) | files kept on the device are probably not "collected" (inference) | pickers must show Files and iCloud Drive |
| Camera, scan, QR, photos (4) | 2.5.14, 5.1.1 (ii)–(iii) | none for the Photo Picker, ML Kit scanner, code scanner or `ACTION_IMAGE_CAPTURE` without `CAMERA`; `CAMERA` runtime for VisionCamera / CameraX | "Photos" (and "Files and docs" for PDFs) **if uploaded** | name the exact use ("scan the QR on a GST e-invoice"); don't declare `CAMERA` unless needed — a declared-but-denied `CAMERA` makes `ACTION_IMAGE_CAPTURE` throw |
| Background upload (4) | 2.5.4 — background `URLSession` is standard networking | WorkManager needs no permission; UIDT needs `RUN_USER_INITIATED_JOBS`; a `dataSync` FGS needs the Console form and a video | photos / files | prefer WorkManager / UIDT over an FGS |
| Push, in-app messages (5) | 4.5.3, 4.5.4, 2.5.16 | `POST_NOTIFICATIONS` runtime from Android 13 | device IDs via OneSignal / Firebase (already applicable) | promotional pushes need an in-app opt-in and opt-out; no balances in payloads |
| Live Activity / Live Update (5) | 4.5.3, 2.5.16, 4.5.4 | `POST_PROMOTED_NOTIFICATIONS`; Google's usage criteria | none new (assumed) | real order events only; never package tracking or price promotions |
| Widgets, Controls, shortcuts, tiles (6) | 2.5.16, 4.4 | none | none | no marketing tiles; no amounts in shortcut metadata; money on the Lock Screen is a decision |
| App Intents / Siri (6) | 2.5.11 (i)–(iii), 2.5.16, 5.1.2 | AppFunctions — no policy text found | — | the phrase names the app; no upsell between request and answer |
| Maps, location (7) | 5.1.5, 2.5.4, 5.1.1 (ii) | FINE / COARSE runtime; location FGS form; background-location form + video + disclosure; location button from 2027-01-27 | approximate / precise location | today's three strings are generic; justify background location in review notes |
| Links, App Clip (8) | 2.5.16 (a), 3.1.3 (e), 5.1.1 | App Links need no form; Play Instant is gone | — | every clip feature also in the app; fuel is never paid by IAP |
| Biometric lock, Keychain (9) | 2.5.13 | none extra (whether `androidx.biometric` merges a permission is unverified) | none new | LocalAuthentication, never a custom face check |
| Login, passkeys, OTP (9) | 4.8, 5.1.1 (v) | SMS Retriever needs no permission | none new | adding Google sign-in triggers 4.8; account deletion in the app |
| OTA (9) | 2.5.2, 4.7, the DPLA | Device and Network Abuse | — | a store build for any native, permission or target change; bump the runtime version whenever `specs/` or native code changes |
| Store rating prompt (9) | 5.6.1, 3.2.2 (x), 5.6.3, the Introduction | the ratings policy; the In-App Review guidelines | none new | no pre-question, no reward, never from a button — the button is a store link |
| Web-billed subscription | 3.1.1, 3.1.3 (c) / (f) | not researched for Play | — | no "buy / renew on the web" calls to action on the Indian storefront (the exception is US-only) |
| Analytics and crash SDKs | privacy manifest; 5.1.2 | Data safety (`AD_ID`, AdServices) | the app manifest's empty collected-data list does not reflect the SDKs | declare them, or remove ads attribution |

---

## 5. The Turbo Module Recipe Card

One page for any in-app module on RN 0.84. `NativeFoo` stands for the module; the full worked example is `NativeAppInfo` in [[01-phase-1-foundations]]. The names are Phase 1's: the codegen library is `DzzloOmsSpec` and generated Java lands in `in.vsyst.dzzlooms.specs`.

```
specs/NativeFoo.ts ──codegen──► iOS:     NativeFooSpec protocol + NativeFooSpecJSI ─► RCTNativeFoo.mm ─► FooCore.swift
        │                       Android: NativeFooSpec base class (Java)            ─► NativeFooModule.kt ─► FooCore.kt
        ▼
src/native/foo.js  ◄── the only file that imports the spec; Jest mocks the spec, screens import the facade
```

**1 · The spec** — `specs/NativeFoo.ts`. TypeScript only here: codegen picks its parser by file extension (a `.js` spec is parsed as Flow), and RN 0.84's iOS podspec generator watches only `Native*.ts` and `*NativeComponent.ts`.

```ts
import type {TurboModule, CodegenTypes} from 'react-native';
import {TurboModuleRegistry} from 'react-native';

export type Result = {id: string; path: string};

export interface Spec extends TurboModule {
  getValue(key: string): string | null;          // sync — runs on the JS thread; keep it tiny
  doWork(input: string): Promise<Result>;        // async — dispatched off the JS thread
  readonly onDone: CodegenTypes.EventEmitter<Result>;
}

export default TurboModuleRegistry.getEnforcing<Spec>('NativeFoo');
```

The file name starts with `Native`. Import from the `react-native` root — deep imports into `react-native/Libraries/*` become type errors under 0.87's Strict TypeScript API. Prefer object-literal types over `Object`. Type mapping: `string` → `String` / `NSString`; `number` → `double` / `NSNumber`; `boolean` → `Boolean` / `NSNumber`; `Promise<T>` → `com.facebook.react.bridge.Promise` / `RCTPromiseResolveBlock` + `RCTPromiseRejectBlock`.

**2 · `codegenConfig`** — one block in the app's `package.json`:

```json
"codegenConfig": {
  "name": "DzzloOmsSpec",
  "type": "modules",
  "jsSrcsDir": "specs",
  "android": { "javaPackageName": "in.vsyst.dzzlooms.specs" },
  "ios": { "modulesProvider": { "NativeFoo": "RCTNativeFoo" } }
}
```

`type` becomes `"all"` (with `componentProvider`) once the app also has Fabric components. Java accepts `in` as a package segment; Kotlin needs it in backticks. Run codegen with:

```bash
cd ios && bundle exec pod install                          # iOS codegen runs here
cd android && ./gradlew generateCodegenArtifactsFromSchema # Android
node node_modules/react-native/scripts/generate-codegen-artifacts.js --path . --outputPath ios/ --targetPlatform ios
```

Output lands in `android/app/build/generated/source/codegen` and `ios/build/generated/ios/`, both under the already git-ignored `build/`. A spec that codegen cannot parse fails the build — the red for spec mistakes.

**3 · iOS — Objective-C++ adapter + Swift.** Swift is supported only behind a thin `.mm` adapter; all logic lives in a plain Swift class that XCTest can reach.

```objc
// ios/dzzlo_oms_app/Foo/RCTNativeFoo.h — one folder per module, as Phase 1's AppInfo/
#import <Foundation/Foundation.h>
#import <DzzloOmsSpec/DzzloOmsSpec.h>   // generated, named after codegenConfig.name
NS_ASSUME_NONNULL_BEGIN
// With an EventEmitter in the spec, the base class is the generated NativeFooSpecBase.
@interface RCTNativeFoo : NativeFooSpecBase <NativeFooSpec>
@end
NS_ASSUME_NONNULL_END
```

```objc
// ios/dzzlo_oms_app/Foo/RCTNativeFoo.mm — compiled as Objective-C++
#import "RCTNativeFoo.h"
// Before the Swift header, as in Phase 1 §5.6: dzzlo_oms_app-Swift.h also declares AppDelegate.swift's
// ReactNativeDelegate, whose superclass lives here — and only @imports it when modules are enabled.
#import <React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>
#import "dzzlo_oms_app-Swift.h"   // the generated Swift header — the name Phase 1 checked in DerivedData

@implementation RCTNativeFoo {
  FooCore *_core;
}
- (instancetype)init { if ((self = [super init])) { _core = [FooCore new]; } return self; } // no UIKit here
+ (NSString *)moduleName { return @"NativeFoo"; }
// Phase 1's rule: YES — RN creates the module and calls -initialize on the main queue, so read UIKit
// there (RCTInitializing), never in -init: the generated provider map also calls [klass new] off the main thread.
+ (BOOL)requiresMainQueueSetup { return YES; }
- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:
    (const facebook::react::ObjCTurboModule::InitParams &)params {
  return std::make_shared<facebook::react::NativeFooSpecJSI>(params);
}
- (NSString * _Nullable)getValue:(NSString *)key { return [_core valueFor:key]; }
// Copy every other signature — the Promise ones take resolve / reject blocks — from the generated protocol.
// Emit events with [self emitOnDone:@{ @"id": …, @"path": … }];
@end
```

```swift
// ios/dzzlo_oms_app/Foo/FooCore.swift — the logic; no React imports
import Foundation

@objcMembers public class FooCore: NSObject {
  public func value(for key: String) -> String? { nil }
}
```

The RN docs also describe an app bridging header (`<app>-Bridging-Header.h` importing `<React-RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>`); the app has none and the adapters need none: Swift here uses nothing from Objective-C, and the `.mm` imports `<React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>` itself, before the generated Swift header (Phase 1 §5.6). Add a bridging header only the day Swift needs an Objective-C type, pointing at that same prebuilt `React_RCTAppDelegate` path. Registration is automatic: `modulesProvider` → the generated provider map → the `RCTAppDependencyProvider` that `AppDelegate.swift` already installs (inferred from the generator source; not tested end-to-end). No `RCT_EXPORT_MODULE`.

**4 · Android — Kotlin + `BaseReactPackage`.** In-app modules are **not** autolinked.

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/foo/NativeFooModule.kt
package `in`.vsyst.dzzlooms.foo

import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import `in`.vsyst.dzzlooms.specs.NativeFooSpec   // the codegenConfig javaPackageName

class NativeFooModule(reactContext: ReactApplicationContext) : NativeFooSpec(reactContext) {
  private val core = FooCore()                    // plain Kotlin — JUnit / Robolectric tests this
  override fun getName() = NAME
  override fun getValue(key: String): String? = core.value(key)
  override fun doWork(input: String, promise: Promise) { /* off the JS thread; resolve or reject */ }
  companion object { const val NAME = "NativeFoo" }
}
```

```kotlin
// NativeFooPackage.kt
class NativeFooPackage : BaseReactPackage() {
  override fun getModule(name: String, reactContext: ReactApplicationContext): NativeModule? =
    if (name == NativeFooModule.NAME) NativeFooModule(reactContext) else null
  override fun getReactModuleInfoProvider() = ReactModuleInfoProvider {
    mapOf(NativeFooModule.NAME to ReactModuleInfo(
      name = NativeFooModule.NAME, className = NativeFooModule.NAME,
      canOverrideExistingModule = false, needsEagerInit = false,
      isCxxModule = false, isTurboModule = true))
  }
}
```

```kotlin
// MainApplication.kt — replace the template's commented line
PackageList(this).packages.apply {
  add(NativeFooPackage())
}
```

**5 · The facade** — `src/native/foo.js`, the only importer of the spec:

```js
import NativeFoo from '../../specs/NativeFoo';

export function getValue(key) {
  return NativeFoo.getValue(key);
}

export async function doWork(input) {
  try {
    return await NativeFoo.doWork(input);
  } catch (e) {
    // One typed error that callers always catch — since RN 0.82 an uncaught rejection raises console.error.
    throw Object.assign(new Error(e?.message ?? 'NativeFoo failed'), {code: e?.code ?? 'E_FOO'});
  }
}
```

Where a JS bundle could reach a binary without the module (OTA to an older build), export `TurboModuleRegistry.get<Spec>(…)` from the spec instead — it returns `null` rather than throwing — and give the facade a fallback, the way `src/i18n/deviceLocale.js` reads native modules at call time.

**6 · Jest** — mock the spec, never the registry; `jest.config.js` already sends `.ts` through babel-jest.

```js
// src/native/__tests__/foo.test.js
jest.mock('../../../specs/NativeFoo', () => ({
  __esModule: true,
  default: {
    getValue: jest.fn(),
    doWork: jest.fn(),
    onDone: jest.fn(() => ({remove: jest.fn()})),
  },
}));
import NativeFoo from '../../../specs/NativeFoo';
import {doWork} from '../foo';

test('maps a native rejection to one typed error', async () => {
  NativeFoo.doWork.mockRejectedValueOnce({code: 'E_IO', message: 'disk full'});
  await expect(doWork('x')).rejects.toMatchObject({code: 'E_IO'});
});
```

Add the same mock to `jest.setup.js` so screens that don't care never reach `getEnforcing` (an unmocked TurboModule throws under Jest), and pin the wiring with a `*.config.test.js` that reads `package.json` and `MainApplication.kt` off disk. Run with `yarn test src/native` — `yarn test` sets `APP_ENV=testing`, and path patterns are regexes over the full path.

**7 · Native unit tests** — new infrastructure; neither platform has a test target on 2026-09-29.

```bash
# iOS: Phase 1 adds a Unit Testing Bundle named dzzlo_oms_appTests (no host application) to the shared scheme's Test action; then
xcodebuild test -workspace ios/dzzlo_oms_app.xcworkspace -scheme dzzlo_oms_app \
  -destination 'platform=iOS Simulator,name=<simulator>'
# Android: testImplementation junit 4.13.2 + robolectric 4.15.1 (RN core's versions), then
cd android && ./gradlew :app:testDebugUnitTest
```

Test `FooCore.swift` and `FooCore.kt`, not the RN shells: whether `ReactApplicationContext` can be constructed under Robolectric on 0.84 is unverified, so the shells stay logic-free and the device run covers them.

**8 · Device run, then the rules that outlive it.**

- Build and exercise on the iOS simulator and the Android emulator, and on a real device where the feature needs one; record the run. Nothing in CI compiles native code.
- Sync methods are JS-thread code — tiny. I/O goes in Promise or void methods. Hop to the main thread for UIKit or Android `View` work. Don't build on the iOS `methodQueue` — RN's own comment marks it backward-compat and possibly going away.
- Events: `CodegenTypes.EventEmitter<T>`; call `sub.remove()` in the effect cleanup. Modules are created lazily; put cleanup in `invalidate()`.
- Kotlin-, Swift- and ObjC-only modules add no `.so`, so 16 KB is a non-issue for them; C++ and Nitro modules add `.so` files.
- Packaging: start in-app (`specs/` + `ios/` + `android/app`); move to a local library (`npx create-react-native-library@latest`, which lands in `modules/<name>` and links with `link:` under Yarn) only when reuse or native-test isolation demands it — a local library is a pod and inherits the Podfile's static linkage.
- Every module change is a store release — bump the OTA runtime / binary version whenever `specs/` or native code changes.

> **After the upgrade to 0.87:** `preset: '@react-native/jest-preset'` (from 0.85; re-check the custom transform and resolver); deep imports are type errors; AGP 9 + compileSdk 37 with the two opt-outs; `useTurboModules` is gone (Turbo Modules always on) and `RCTTurboModuleEnabled()` is deprecated; Swift Package Manager is experimental ("do not use it in production yet") and needs framework-style `#import <React/…>` includes; Node ≥ 22.13.0.

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Jest: "`TurboModuleRegistry.getEnforcing(...): 'NativeFoo' could not be found. Verify that a module by this name is registered in the native binary.`" | Jest has no `__turboModuleProxy`; `getEnforcing` falls back to the mocked `NativeModules`, which lacks the name. RN's `jest/setup.js` has no TurboModule mock | `jest.mock` the spec (§5.6), or add the module to the `NativeModules` mock in `jest.setup.js` |
| A screen test crashes on a library's TurboModule (`react-native-webview`'s throws under Jest) | an unmocked native package | mock it in `jest.setup.js` — or, as the house does for WebView navigators, read the source as text (`src/test/sourceText.js`) |
| Codegen doesn't pick up the spec, or parses it as Flow | codegen finds specs by the basename pattern `Native…` / `…NativeComponent` and picks the parser by extension | `specs/NativeFoo.ts` |
| On an iPhone: "`…'NativeFoo' could not be found…`" although the build succeeded | a `modulesProvider` name that doesn't match the JS name, or `pod install` not re-run after editing the spec | match the names exactly; `cd ios && bundle exec pod install` |
| On Android: the same "could not be found" error | in-app modules are not autolinked | `add(NativeFooPackage())` in `MainApplication.kt`, pinned by a config test |
| Kotlin: "expecting package name" or an import error on `in.vsyst…` | `in` is a Kotlin keyword | backticks — ``package `in`.vsyst.dzzlooms`` (as `MainApplication.kt:1` does) |
| Kotlin rejects the `package` or `import` line of `NativeStoreReviewModule.kt` | `in` is a keyword in every Kotlin package name that starts with it — the module's own sub-package and the import of the generated `in.vsyst.dzzlooms.specs` class alike | ``package `in`.vsyst.dzzlooms.storereview`` and ``import `in`.vsyst.dzzlooms.specs.NativeStoreReviewSpec``; Java needs no backticks ([[09-phase-9-security-privacy-and-release]] §9.4) |
| Build breaks after someone sets `USE_FRAMEWORKS` | the Podfile switches to `use_frameworks!` only when that env var is set; a global static-frameworks build "breaks react-native-worklets / react-native-reanimated on RN 0.84" (Podfile comment); RNFirebase is forced static | leave linkage alone — in-app modules avoid the question entirely |
| Swift 6 diagnostics such as "Static property 'shared' is not concurrency-safe" | the toolchain is Swift 6.4 but the targets are Swift 5 mode; Swift 6 mode turns on complete concurrency checking | keep new Swift compiling cleanly in Swift 5 mode with warnings visible, or opt one target into Swift 6 deliberately; no shared mutable state in adapters (RN calls in from arbitrary queues) |
| "`dzzlo_oms_app-Swift.h` not found" | the Swift class isn't in the app target, or the adapter isn't compiled as Objective-C++ (`.mm`) | check the Swift file's target membership and the `.mm` extension; the header name itself was checked by Phase 1 |
| "cannot find interface declaration for 'RCTDefaultReactNativeFactoryDelegate', superclass of 'ReactNativeDelegate'" in an adapter `.mm` | `dzzlo_oms_app-Swift.h` also declares `AppDelegate.swift`'s `ReactNativeDelegate`, and only `@import`s its superclass when modules are enabled | `#import <React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>` before `"dzzlo_oms_app-Swift.h"`, as Phase 1 §5.6 does — no bridging header |
| dSYM "Upload Symbols Failed" for `React.framework` / `ReactNativeDependencies.framework` | an artefact of RN 0.84's prebuilt XCFrameworks | non-blocking; or `RCT_USE_RN_DEP=0 RCT_USE_PREBUILT_RNCORE=0 bundle exec pod install` |
| An app built with the iOS 27 SDK does not launch — and so never registers for push | no UIScene life cycle | already fixed here (`SceneDelegate` in `AppDelegate.swift`); any new app-like target (an App Clip) needs its own |
| Unhandled rejections now show as red errors | RN 0.82+ raises `console.error` for uncaught promise rejections | catch in the facade and return one typed error |
| Play warns about 16 KB, or a 16 KB compatibility dialog appears | a `.so` not aligned to 16 KB (release APK was aligned on 2026-09-29; a debug-build dialog on an emulator was not re-examined) | `zipalign -c -P 16 -v 4 app-release.apk`; `check_elf_alignment.sh app-release.apk`; `llvm-objdump -p lib.so \| grep LOAD` (look for `align 2**14`); NDK r28+ aligns by default, for r27 add `-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384` |
| "Update app" does nothing on Android 11+ | `Linking.canOpenURL` resolves `false` without a matching `<queries>` entry (RN's docs say it may reject) | add `<queries>` for the `https` VIEW intent (and `upi`, WhatsApp) — [[02-phase-2-dependency-diet]] |
| Pushes late or missing on Xiaomi, OnePlus, Samsung, Oppo, Vivo | OEM battery managers (dontkillmyapp: Xiaomi, OnePlus, Samsung 5/5; Oppo 4/5; Vivo, realme, Tecno 3/5); Doze delays normal-priority FCM | visible notifications for every event; refresh on resume; an OEM guide linking to `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS`; never request the exemption directly |
| High-priority FCM messages stop waking the device | FCM deprioritises high-priority messages that don't produce user-visible notifications (judged over 7 days) | only use high priority for messages that show a notification |
| App's background work runs once a day | the Restricted standby bucket (after 8 days unused on Android 13+) | an active widget exempts the app; don't depend on background work |
| Live Activity never starts, or ends early | iOS < 16.1; push-to-start needs 17.2; > 8 h active; data > 4 KB; a p12 certificate instead of a `.p8` key; an activity can't fetch the network or location itself | gate with `@available`; start at `dispatched`; keep payloads small; the server computes the ETA |
| Live Activity truncated | taller than 160 pt; minimal-presentation image over 45×36.67 pt | design to the limits |
| Android Live Update shows as a plain notification | a missing rule: `POST_PROMOTED_NOTIFICATIONS`, `setRequestPromotedOngoing(true)`, ongoing, `contentTitle`, an allowed style, no custom `RemoteViews`, not colorized, channel not `IMPORTANCE_MIN` — or the OS / OEM skin doesn't promote | check `canPostPromotedNotifications()` and `hasPromotableCharacteristics()`; below Android 16 plain is the designed fallback |
| Status chip shows only the icon | chip text too long (96 dp max; under 7 characters shown whole) | ≤ 6 characters |
| Widget stale | iOS budget (typically 40–70 refreshes a day); Android `updatePeriodMillis` < 30 min not honoured; WorkManager's 15-minute floor | reload after data changes, not on a timer; iOS 26 `WidgetPushHandler` for server-driven reloads |
| Android 17 widget throws `IllegalArgumentException` | `RemoteViews` bitmaps over 1.5 × screen width × height × 4 bytes (targeting 37) | smaller images, or none |
| App Clip rejected for size | 15 MB limit for physical invocations (QR, NFC, App Clip Codes) on iOS 16; Hermes alone was ~3.2 MB of 15 MB in an older write-up | keep `DzzloClip` Swift-native |
| ITMS-90683 "missing purpose string" | a linked binary (OneSignalLocation) references location APIs | keep the keys; make the text truthful |
| App Store Connect warns about the extension's version | extension `MARKETING_VERSION` differs from the app's (NSE is 1.0, app 1.79) | align every target's version |
| `onBackPressed` no longer called on Android 16 | predictive back is on at target 36 (`BackHandler` is used in 5 live files) | test on Android 16 with gesture navigation; temporary opt-out `android:enableOnBackInvokedCallback="false"` |
| Content under the status or navigation bar on Android 16 | edge-to-edge is enforced at target 36 despite `edgeToEdgeEnabled=false` | check v1 screens on an Android 16 device |
| Portrait lock ignored on a tablet or unfolded Fold | Android 16 ignores orientation limits on sw ≥ 600 dp at target 36 (opt-out removed at 37); iOS 27 treats orientation as a preference when resizable | lay out for any width — the 320 dp baseline rule |
| Share to WhatsApp arrives without `.pdf` (iOS release builds) | react-native-share issue #1556 | the facade returns a path ending in `.pdf`; verify in a Release build |
| From Android 18, shared files open as "permission denied" | `ACTION_SEND` / `ACTION_IMAGE_CAPTURE` stop granting URI permissions automatically | set `FLAG_GRANT_READ_URI_PERMISSION` explicitly |
| `ACTION_IMAGE_CAPTURE` throws `SecurityException` | the manifest declares `CAMERA` but it isn't granted | don't declare `CAMERA` unless a custom camera needs it |
| The review sheet never appears on iOS | a TestFlight build ("this method has no effect"); an iOS seed build — "review requests are not allowed in seed", as a developer relayed Apple's reply (26.5.1 and 26.5.2 reported too); in production, the 3-a-year cap or the person's Settings switch; no foreground-active window scene (`no_scene`) | test with an Xcode development build on a release iOS; read the `review_requested` outcome in Firebase DebugView; never draw a sheet of your own (5.6.1) |
| The review card never appears on Android | not installed from Play (Firebase App Distribution, sideloaded); not the Play Store's primary account; a protected (Workspace) account; already reviewed; the quota; no Play Store (`PLAY_STORE_NOT_FOUND`) | the internal test track with a Gmail tester — "The quota limits are not enforced"; internal app sharing to see it (Submit disabled); `FakeReviewManager` in unit tests |

---

## 7. Glossary

| Term | Meaning here |
| --- | --- |
| AAB | Android App Bundle — Play builds per-device APKs from it; the app scripts only a universal APK today |
| ActivityKit | Apple's Live Activity framework (iOS 16.1) |
| App Clip | a small part of an iOS app that runs without installing (App Clip framework, iOS 14.0); `DzzloClip` here |
| App Group | an Apple entitlement giving the app and its extensions a shared container; `group.in.vsyst.dzzlooms.onesignal` today, `group.in.vsyst.dzzlooms.shared` planned |
| App Intent | a Swift type exposing an action to Siri, Shortcuts, Spotlight, widgets and the Action button (iOS 16.0) |
| App Links / Universal Links | https links verified to open the app — `assetlinks.json` on Android, `apple-app-site-association` (AASA) on iOS |
| App Shortcut | iOS: an App Intent with preset Siri phrases (`AppShortcutsProvider`, iOS 16.0). Android: a launcher long-press shortcut (API 25) |
| AppFunctions | Android 16's API for exposing app functions to agents such as Gemini; Jetpack alpha, Gemini access in private preview |
| APNs | Apple Push Notification service; Live Activities need token-based auth (`.p8` key) |
| `BaseReactPackage` | the Android class that registers Turbo Modules with React Native |
| Codegen | RN's generator that turns `specs/Native*.ts` into native interfaces and JSI glue |
| `codegenConfig` | the `package.json` block that tells codegen where specs are and how to name output |
| Compat (interop) layer | RN code that lets old-architecture native modules run under the New Architecture; kept "for the foreseeable future" |
| Content-state | the dynamic data of a Live Activity, updated by push; static + dynamic ≤ 4 KB |
| Controls | iOS 18 buttons and toggles in Control Center, the Lock Screen or the Action button |
| Doze / standby buckets | Android's idle-time restrictions on network, alarms and jobs |
| DU slip | a delivery / dispensing-unit slip — the notes assume "dispensing unit" |
| Dynamic Island | the iPhone's pill-shaped live area where Live Activities also appear |
| EAS Update | Expo's hosted OTA service; needs Expo modules in a bare app |
| Expo module | a native module written with Expo's Swift / Kotlin DSL; needs `expo` installed |
| Fabric | RN's New-Architecture renderer; a "Fabric component" is a custom native view |
| Facade | our `src/native/<name>.js` wrapper — the only file that imports a spec |
| FCM | Firebase Cloud Messaging — Android's push transport under OneSignal |
| FGS | foreground service — Android background work with a visible notification and a declared type |
| FileProvider | the androidx component that hands out `content://` URIs for sharing files |
| Glance | Jetpack's Compose-based API for Android app widgets (1.2.0 stable 2026-08-26) |
| GSTIN · IRN · IRP | GST identification number · Invoice Reference Number · Invoice Registration Portal (signs the e-invoice QR as a JWT) |
| Hermes | RN's JavaScript engine (V1 by default from 0.84) |
| Hot Updater | a self-hosted, bare-first OTA service — the no-Expo OTA route |
| HSD · MS | high-speed diesel · motor spirit (petrol) |
| HybridObject | Nitro's native object type, written directly in Swift or Kotlin |
| In-app module | a module whose spec and native code live inside the app project — our default |
| In-app review | the store's own rating sheet shown inside the app — `AppStore.requestReview(in:)` (iOS 16.0; `SKStoreReviewController` on iOS 15) and Play In-App Review (`com.google.android.play:review` 2.0.2). The OS decides whether it appears and never tells the app; `NativeStoreReview` here, asked once after a win |
| JSI | the C++ interface between JavaScript and native that Turbo Modules use |
| Live Activity | an iOS Lock Screen / Dynamic Island card for one event with a start and an end |
| Live Update | Android 16's promoted ongoing notification (Standard, BigText, Call, Progress or, from Android 17, Metric style) with a status-bar chip |
| Liquid Glass | the iOS 26 design language; cannot be opted out when building with the iOS 27 SDK |
| ML Kit | Google's on-device vision APIs: document scanner, text recognition v2, barcode / code scanner |
| `modulesProvider` | the `codegenConfig.ios` map from a JS module name to its Objective-C class |
| Nitro | Margelo's JSI module framework with its own codegen (`nitrogen`) — a later option for measured hot paths |
| NSE | Notification Service Extension — iOS code that runs on a push before it is shown (OneSignal's today); the Android "NotificationServiceExtension" is OneSignal's Kotlin equivalent |
| OTA | over-the-air JS / asset updates without a store release; never native code |
| Photo Picker / PHPicker | the system photo pickers that need no library permission (Android 13 built in; iOS 14.0) |
| Play Integrity · App Attest | Google's and Apple's app-integrity attestations |
| Privacy manifest | `PrivacyInfo.xcprivacy` — declares required-reason API use and collected data |
| `ProgressStyle` | the Android 16 notification style for journeys, with segments and points |
| Push-to-start | starting a Live Activity by push, without the app open (iOS 17.2) |
| R8 | Android's code shrinker and obfuscator — off in this app today |
| Robolectric | a JVM-hosted Android test runtime (RN core uses 4.15.1) |
| SAF | Storage Access Framework — Android's system document pickers, no permission needed |
| Spec | `specs/NativeFoo.ts` — the typed interface codegen reads |
| Turbo Module | RN's New-Architecture native module: typed spec, codegen, lazy loading, JSI |
| UIDT | user-initiated data transfer jobs (Android 14) — long, user-started transfers without an FGS |
| UIScene | Apple's scene-based app life cycle, mandatory with the iOS 27 SDK |
| UPI Intent | a `upi://pay?…` link that opens the installed UPI apps; confirm payment on the server |
| WidgetKit | Apple's widget framework (iOS 14.0) |
| XCTest | Apple's unit-test framework — the `dzzlo_oms_appTests` bundle Phase 1 adds is the app's first |
| 16 KB page size | Android devices with 16 KB memory pages; native libraries must be aligned for them |
| 320 dp baseline | the house rule: every layout holds at 320 dp × fontScale 1, in English and Hindi |

---

## 8. Sources

Every web source cited across the six research notes behind this course — 683 links checked on **2026-09-29**, the research date, plus the 52 store-rating pages of §8.6 checked on **2026-09-30**. Repo facts are cited by path in the text and are not repeated here. Where a fact rests on a search summary or a secondary write-up rather than the primary page, the course text says so next to the fact. Titles are the notes' link text where it was descriptive, otherwise the page, package or repository name.

### 8.1 Apple

- **App Review Guidelines** — [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/) — checked 2026-09-29.
- **ActivityKit** — [Activity](https://developer.apple.com/documentation/activitykit/activity) · [frequentPushesEnabled](https://developer.apple.com/documentation/activitykit/activityauthorizationinfo/frequentpushesenabled) · [pushToStartToken](https://developer.apple.com/documentation/activitykit/activity/pushtostarttoken) · [channel(_:)](https://developer.apple.com/documentation/activitykit/pushtype/channel%28_:%29) · [request(…start:)](https://developer.apple.com/documentation/activitykit/activity/request%28attributes:content:pushtype:style:alertconfiguration:start:%29) · [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities) · [Starting and updating Live Activities with ActivityKit push notifications](https://developer.apple.com/documentation/activitykit/starting-and-updating-live-activities-with-activitykit-push-notifications) — checked 2026-09-29.
- **WidgetKit** — [reloadTimelines](https://developer.apple.com/documentation/widgetkit/widgetcenter/reloadtimelines%28ofkind:%29) · [AppIntentConfiguration](https://developer.apple.com/documentation/widgetkit/appintentconfiguration) · [WidgetPushHandler](https://developer.apple.com/documentation/widgetkit/widgetpushhandler) · [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton) · [Controls](https://developer.apple.com/documentation/widgetkit/controls-collection) · [Adding interactivity to widgets and Live Activities](https://developer.apple.com/documentation/widgetkit/adding-interactivity-to-widgets-and-live-activities) · [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date) — checked 2026-09-29.
- **App Intents (1/2)** — [AppIntent](https://developer.apple.com/documentation/appintents/appintent) · [AppEntity](https://developer.apple.com/documentation/appintents/appentity) · [AppShortcutsProvider](https://developer.apple.com/documentation/appintents/appshortcutsprovider) · [AppIntentsExtension](https://developer.apple.com/documentation/appintents/appintentsextension) · [AppIntentsPackage](https://developer.apple.com/documentation/appintents/appintentspackage) · [IndexedEntity](https://developer.apple.com/documentation/appintents/indexedentity) · [SnippetIntent](https://developer.apple.com/documentation/appintents/snippetintent) · [IntentValueQuery](https://developer.apple.com/documentation/appintents/intentvaluequery) · [SemanticContentDescriptor](https://developer.apple.com/documentation/visualintelligence/semanticcontentdescriptor) · [supportedModes](https://developer.apple.com/documentation/appintents/appintent/supportedmodes) · [openAppWhenRun](https://developer.apple.com/documentation/appintents/appintent/openappwhenrun) · [ForegroundContinuableIntent](https://developer.apple.com/documentation/appintents/foregroundcontinuableintent) · [LongRunningIntent](https://developer.apple.com/documentation/appintents/longrunningintent) · [App Intents Testing](https://developer.apple.com/documentation/appintentstesting) — checked 2026-09-29.
- **App Intents (2/2)** — [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai) · [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence) · [App schema domains](https://developer.apple.com/documentation/appintents/app-schema-domains) · [SiriKit](https://developer.apple.com/documentation/sirikit) — checked 2026-09-29.
- **App Clips** — [Offering Live Activities with your App Clip](https://developer.apple.com/documentation/appclip/offering-live-activities-with-your-app-clip) · [APActivationPayload](https://developer.apple.com/documentation/appclip/apactivationpayload) · [App Clips](https://developer.apple.com/documentation/appclip) · [Choosing the right functionality for your App Clip](https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip) · [Creating an App Clip with Xcode](https://developer.apple.com/documentation/appclip/creating-an-app-clip-with-xcode) · [Associating your App Clip with your website](https://developer.apple.com/documentation/appclip/associating-your-app-clip-with-your-website) · [Configuring App Clip experiences](https://developer.apple.com/documentation/appclip/configuring-the-launch-experience-of-your-app-clip) · [Enabling notifications in App Clips](https://developer.apple.com/documentation/appclip/enabling-notifications-in-app-clips) · [Confirming a person's physical location](https://developer.apple.com/documentation/appclip/confirming-a-person-s-physical-location) — checked 2026-09-29.
- **User Notifications** — [UNNotificationCategory](https://developer.apple.com/documentation/usernotifications/unnotificationcategory) · [UNNotificationServiceExtension](https://developer.apple.com/documentation/usernotifications/unnotificationserviceextension) · [UNNotificationContentExtension](https://developer.apple.com/documentation/usernotificationsui/unnotificationcontentextension) · [provisional](https://developer.apple.com/documentation/usernotifications/unauthorizationoptions/provisional) · [UNNotificationInterruptionLevel](https://developer.apple.com/documentation/usernotifications/unnotificationinterruptionlevel) · [setBadgeCount](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter/setbadgecount%28_:withcompletionhandler:%29) · [UNNotificationContent](https://developer.apple.com/documentation/usernotifications/unnotificationcontent) · [Implementing communication notifications](https://developer.apple.com/documentation/usernotifications/implementing-communication-notifications) — checked 2026-09-29.
- **Files, PDF, print, share** — [UIDocumentPickerViewController](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller) · [init(forExporting:asCopy:)](https://developer.apple.com/documentation/uikit/uidocumentpickerviewcontroller/init%28forexporting:ascopy:%29) · [UIActivityViewController](https://developer.apple.com/documentation/uikit/uiactivityviewcontroller) · [QLPreviewController](https://developer.apple.com/documentation/quicklook/qlpreviewcontroller) · [createPDF](https://developer.apple.com/documentation/webkit/wkwebview/createpdf%28configuration:completionhandler:%29) · [UIGraphicsPDFRenderer](https://developer.apple.com/documentation/uikit/uigraphicspdfrenderer) · [UIPrintPageRenderer](https://developer.apple.com/documentation/uikit/uiprintpagerenderer) · [UIPrintInteractionController](https://developer.apple.com/documentation/uikit/uiprintinteractioncontroller) · [UIApplicationShortcutItem](https://developer.apple.com/documentation/uikit/uiapplicationshortcutitem) — checked 2026-09-29.
- **Vision, VisionKit, Photos** — [PHPickerViewController](https://developer.apple.com/documentation/photosui/phpickerviewcontroller) · [PhotosPicker](https://developer.apple.com/documentation/photosui/photospicker) · [Delivering an enhanced privacy experience in your photos app](https://developer.apple.com/documentation/photokit/delivering-an-enhanced-privacy-experience-in-your-photos-app) · [VNDocumentCameraViewController](https://developer.apple.com/documentation/visionkit/vndocumentcameraviewcontroller) · [DataScannerViewController](https://developer.apple.com/documentation/visionkit/datascannerviewcontroller) · [Scanning data with the camera](https://developer.apple.com/documentation/visionkit/scanning-data-with-the-camera) · [ImageAnalyzer](https://developer.apple.com/documentation/visionkit/imageanalyzer) · [VNRecognizeTextRequest](https://developer.apple.com/documentation/vision/vnrecognizetextrequest) · [RecognizeTextRequest](https://developer.apple.com/documentation/vision/recognizetextrequest) · [DetectBarcodesRequest](https://developer.apple.com/documentation/vision/detectbarcodesrequest) · [RecognizeDocumentsRequest](https://developer.apple.com/documentation/vision/recognizedocumentsrequest) — checked 2026-09-29.
- **MapKit, Core Location** — [Map](https://developer.apple.com/documentation/mapkit/map) · [MKLookAroundViewController](https://developer.apple.com/documentation/mapkit/mklookaroundviewcontroller) · [MKMapItemDetailViewController](https://developer.apple.com/documentation/mapkit/mkmapitemdetailviewcontroller) · [MKAddress](https://developer.apple.com/documentation/mapkit/mkaddress) · [MKReverseGeocodingRequest](https://developer.apple.com/documentation/mapkit/mkreversegeocodingrequest) · [CLGeocoder](https://developer.apple.com/documentation/corelocation/clgeocoder) · [PlaceDescriptor](https://developer.apple.com/documentation/geotoolbox/placedescriptor) · [CLLocationUpdate](https://developer.apple.com/documentation/corelocation/cllocationupdate) · [CLMonitor](https://developer.apple.com/documentation/corelocation/clmonitor-2r51v) · [CLBackgroundActivitySession](https://developer.apple.com/documentation/corelocation/clbackgroundactivitysession-3mzv3) · [CLServiceSession](https://developer.apple.com/documentation/corelocation/clservicesession-2ddhd) · [Handling location updates in the background](https://developer.apple.com/documentation/corelocation/handling-location-updates-in-the-background) · [Monitoring the user's proximity to geographic regions](https://developer.apple.com/documentation/corelocation/monitoring-the-user-s-proximity-to-geographic-regions) · [Apple Maps Server API](https://developer.apple.com/documentation/applemapsserverapi) — checked 2026-09-29.
- **Info.plist keys, entitlements, privacy manifests** — [UIDesignRequiresCompatibility](https://developer.apple.com/documentation/bundleresources/information-property-list/uidesignrequirescompatibility) · [UIRequiresFullScreen](https://developer.apple.com/documentation/bundleresources/information-property-list/uirequiresfullscreen) · [NSSupportsLiveActivities](https://developer.apple.com/documentation/bundleresources/information-property-list/nssupportsliveactivities) · [NSSupportsLiveActivitiesFrequentUpdates](https://developer.apple.com/documentation/bundleresources/information-property-list/nssupportsliveactivitiesfrequentupdates) · [App Groups entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups) · [com.apple.developer.usernotifications.critical-alerts](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.usernotifications.critical-alerts) · [NSFaceIDUsageDescription](https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription) · [LSSupportsOpeningDocumentsInPlace](https://developer.apple.com/documentation/bundleresources/information-property-list/lssupportsopeningdocumentsinplace) · [UIFileSharingEnabled](https://developer.apple.com/documentation/bundleresources/information-property-list/uifilesharingenabled) · [UTExportedTypeDeclarations](https://developer.apple.com/documentation/bundleresources/information-property-list/utexportedtypedeclarations) · [Associated Domains entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.associated-domains) · [Supporting associated domains](https://developer.apple.com/documentation/xcode/supporting-associated-domains) · [keychain-access-groups](https://developer.apple.com/documentation/bundleresources/entitlements/keychain-access-groups) · [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api) — checked 2026-09-29.
- **Sign-in, biometrics, integrity** — [Supporting passkeys](https://developer.apple.com/documentation/authenticationservices/supporting-passkeys) · [ASAuthorizationAccountCreationProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationaccountcreationprovider) · [ASCredentialDataManager](https://developer.apple.com/documentation/authenticationservices/ascredentialdatamanager) · [ASCredentialUpdater](https://developer.apple.com/documentation/authenticationservices/ascredentialupdater) · [ASAuthorizationAppleIDProvider](https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidprovider) · [LAContext](https://developer.apple.com/documentation/localauthentication/lacontext) · [DCAppAttestService](https://developer.apple.com/documentation/devicecheck/dcappattestservice) · [DCDevice](https://developer.apple.com/documentation/devicecheck/dcdevice) · [Establishing your app's integrity](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity) — checked 2026-09-29.
- **Background work and transfers** — [BGContinuedProcessingTask](https://developer.apple.com/documentation/backgroundtasks/bgcontinuedprocessingtask) · [Performing long-running tasks on iOS and iPadOS](https://developer.apple.com/documentation/backgroundtasks/performing-long-running-tasks-on-ios-and-ipados) · [background(withIdentifier:)](https://developer.apple.com/documentation/foundation/urlsessionconfiguration/background%28withidentifier:%29) · [Downloading files in the background](https://developer.apple.com/documentation/foundation/downloading-files-in-the-background) — checked 2026-09-29.
- **Guides and news** — [Apple Developer News "Upcoming SDK minimum requirements"](https://developer.apple.com/news/?id=ueeok6yw) · [TN3187](https://developer.apple.com/documentation/technotes/tn3187-migrating-to-the-uikit-scene-based-life-cycle) · [WWDC26 iOS guide](https://developer.apple.com/wwdc26/guides/ios/) · [WWDC26 Apple Intelligence guide](https://developer.apple.com/wwdc26/guides/apple-intelligence/) · [What's new in iOS](https://developer.apple.com/ios/whats-new/) · [Apple Developer News: privacy manifest requirements](https://developer.apple.com/news/?id=r1henawx) · [WWDC26 App Store guide](https://developer.apple.com/wwdc26/guides/app-store/) — checked 2026-09-29.
- **WWDC sessions** — [WWDC26 session 278 "Modernize your UIKit app"](https://developer.apple.com/videos/play/wwdc2026/278/) · [WWDC25 session 275](https://developer.apple.com/videos/play/wwdc2025/275/) · [WWDC26 345](https://developer.apple.com/videos/play/wwdc2026/345/) · [WWDC26 240](https://developer.apple.com/videos/play/wwdc2026/240/) · [WWDC26 223 "Live Activities essentials"](https://developer.apple.com/videos/play/wwdc2026/223/) · [WWDC25 278 "What's new in widgets"](https://developer.apple.com/videos/play/wwdc2025/278/) · [WWDC21 10091](https://developer.apple.com/videos/play/wwdc2021/10091/) · [WWDC26 343](https://developer.apple.com/videos/play/wwdc2026/343/) · [WWDC25 227 "Finish tasks in the background"](https://developer.apple.com/videos/play/wwdc2025/227/) · [WWDC25 272](https://developer.apple.com/videos/play/wwdc2025/272/) — checked 2026-09-29.
- **iOS 27 release coverage and other Apple secondary** — [MacRumors: apple announces ios 27 release date](https://www.macrumors.com/2026/09/09/apple-announces-ios-27-release-date/) · [9to5Mac: apple confirms ios 27 release date september 14](https://9to5mac.com/2026/09/09/apple-confirms-ios-27-release-date-september-14/) · [Wikipedia: iOS 27](https://en.wikipedia.org/wiki/IOS_27) · [Wikipedia: Xcode](https://en.wikipedia.org/wiki/Xcode) · [MacRumors iOS 27 Siri guide](https://www.macrumors.com/guide/ios-27-siri/) · [MacRumors 2026-09-16](https://www.macrumors.com/2026/09/16/siri-ai-new-languages-ios-27-2/) · [9to5Mac 2026-02-11](https://9to5mac.com/2026/02/11/apple-reportedly-pushing-back-gemini-powered-siri-features-beyond-ios-26-4/) · [9to5Mac 2026-03-30](https://9to5mac.com/2026/03/30/ios-26-5-beta-arrives-with-no-gemini-powered-ai-features-as-focus-shifts-to-ios-27/) · [Apple Support](https://support.apple.com/guide/iphone/automatically-fill-in-verification-codes-ipha6173c19f/ios) · [Cult of Mac: ios 17 autofill verification codes safari mail app](https://www.cultofmac.com/news/ios-17-autofill-verification-codes-safari-mail-app) — checked 2026-09-29.

### 8.2 Android and Google Play

- **Android versions and behaviour changes** — [Android 16 behaviour changes](https://developer.android.com/about/versions/16/behavior-changes-16) · [Android 17 hub](https://developer.android.com/about/versions/17) · [Android 16 features](https://developer.android.com/about/versions/16/features) · [Android 17 features](https://developer.android.com/about/versions/17/features) · [Android 17 behaviour changes](https://developer.android.com/about/versions/17/behavior-changes-17) · [Android 14 behaviour changes](https://developer.android.com/about/versions/14/behavior-changes-14) · [Android 15 behaviour changes](https://developer.android.com/about/versions/15/behavior-changes-15) · [Android 17 all-apps changes](https://developer.android.com/about/versions/17/behavior-changes-all) · [Android 17 Contact Picker](https://developer.android.com/about/versions/17/features/contact-picker) — checked 2026-09-29.
- **Notifications, widgets, shortcuts, tiles** — [App shortcuts guide](https://developer.android.com/develop/ui/views/launch/shortcuts) · [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update) · [AppWidgetProviderInfo](https://developer.android.com/reference/android/appwidget/AppWidgetProviderInfo) · [Create an advanced widget](https://developer.android.com/develop/ui/views/appwidgets/advanced) · [Quick Settings tiles](https://developer.android.com/develop/ui/views/quicksettings-tiles) · [Notification permission](https://developer.android.com/develop/ui/views/notifications/notification-permission) — checked 2026-09-29.
- **Assistant, AppFunctions** — [App Actions overview](https://developer.android.com/develop/devices/assistant/overview) · [actions.xml (deprecated)](https://developers.google.com/assistant/app/legacy/action-schema) · [AppFunctions overview](https://developer.android.com/ai/appfunctions) · [Optimizing contextual content for the Assistant](https://developer.android.com/training/articles/assistant) — checked 2026-09-29.
- **Background work, Doze, standby** — [WorkManager: define work](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work) · [App Standby Buckets](https://developer.android.com/topic/performance/appstandby) · [FGS types](https://developer.android.com/develop/background-work/services/fgs/service-types) · [Schedule alarms](https://developer.android.com/develop/background-work/services/alarms/schedule) · [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby) · [UIDT](https://developer.android.com/develop/background-work/background-tasks/uidt) — checked 2026-09-29.
- **Storage, sharing, printing, App Links, Photo Picker** — [Google Play Instant](https://developer.android.com/topic/google-play-instant) · [Verify App Links](https://developer.android.com/training/app-links/verify-android-applinks) · [Configure assetlinks](https://developer.android.com/training/app-links/configure-assetlinks) · [SAF guide](https://developer.android.com/training/data-storage/shared/documents-files) · [MediaStore guide](https://developer.android.com/training/data-storage/shared/media) · [FileProvider setup](https://developer.android.com/training/secure-file-sharing/setup-sharing) · [Photo Picker guide](https://developer.android.com/training/data-storage/shared/photopicker) · [Printing HTML documents](https://developer.android.com/training/printing/html-docs) · [DownloadManager](https://developer.android.com/reference/android/app/DownloadManager) — checked 2026-09-29.
- **Jetpack releases** — [Glance releases](https://developer.android.com/jetpack/androidx/releases/glance) · [androidx.pdf releases](https://developer.android.com/jetpack/androidx/releases/pdf) · [CameraX releases](https://developer.android.com/jetpack/androidx/releases/camera) — checked 2026-09-29.
- **Location, Bluetooth** — [Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions) · [Location permissions](https://developer.android.com/develop/sensors-and-location/location/permissions) · [Geofencing](https://developer.android.com/develop/sensors-and-location/location/geofencing) — checked 2026-09-29.
- **Play requirements** — [Android: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes) · [Android developer verification](https://developer.android.com/developer-verification) · [Play Integrity overview](https://developer.android.com/google/play/integrity/overview) · [Target API requirements](https://developer.android.com/google/play/requirements/target-sdk) — checked 2026-09-29.
- **Identity, biometrics, integrity** — [Minimize permission requests](https://developer.android.com/privacy-and-security/minimize-permission-requests) · [Credential Manager](https://developer.android.com/identity/sign-in/credential-manager) · [Biometric auth](https://developer.android.com/identity/sign-in/biometric-auth) · [SafetyNet discontinuation](https://groups.google.com/g/safetynet-api-clients/c/ac_AmiRCn0U) — checked 2026-09-29.
- **Play policy (Play Console Help)** — [Google Play: Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/9888379) · [Play FGS & FSI requirements](https://support.google.com/googleplay/android-developer/answer/13392821) · [Photo & video permissions policy](https://support.google.com/googleplay/android-developer/answer/14115180) · [Background location policy](https://support.google.com/googleplay/android-developer/answer/9799150) · [Location button policy](https://support.google.com/googleplay/android-developer/answer/16909972) · [Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469) · [Background location — Play Console Help (en)](https://support.google.com/googleplay/android-developer/answer/9799150?hl=en) · [Foreground services and full-screen intents — Play Console Help (en)](https://support.google.com/googleplay/android-developer/answer/13392821?hl=en) — checked 2026-09-29.
- **ML Kit, Maps, SMS Retriever** — [ML Kit Document Scanner](https://developers.google.com/ml-kit/vision/doc-scanner) · [Text Recognition v2](https://developers.google.com/ml-kit/vision/text-recognition/v2) · [Google code scanner](https://developers.google.com/ml-kit/vision/barcode-scanning/code-scanner) · [Maps SDK release notes](https://developers.google.com/maps/documentation/android-sdk/release-notes) · [Maps pricing](https://developers.google.com/maps/billing-and-pricing/pricing) · [Google Maps API pricing explained 2026 (maps.guru)](https://maps.guru/blog/google-maps-api-pricing-explained-2026) · [India pricing](https://developers.google.com/maps/billing-and-pricing/india-overview) · [Maps Platform India](https://mapsplatform.google.com/india/) · [Google Maps India price cuts, 2024 (The Register)](https://www.theregister.com/2024/07/19/google_maps_india_price_cuts_ola_response/) · [SMS Retriever overview](https://developers.google.com/identity/sms-retriever/overview) · [message format](https://developers.google.com/identity/sms-retriever/verify) — checked 2026-09-29.
- **Firebase** — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority) · [Firebase IAM](https://firebase.google.com/docs/in-app-messaging) — checked 2026-09-29.
- **Android Developers Blog** — [Android Developers Blog, 2025-05](https://android-developers.googleblog.com/2025/05/prepare-play-apps-for-devices-with-16kb-page-size.html) · [Android Developers Blog: "Android 17 is here"](https://android-developers.googleblog.com/2026/06/Android-17.html) · [Android Developers Blog, Feb 2026](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html) · [Widgets on lock screen FAQ, Mar 2025](https://android-developers.googleblog.com/2025/03/widgets-on-lock-screen-faq.html) · [Android Developers Blog, Oct 2025](https://android-developers.googleblog.com/2025/10/dynamic-app-links-elevating-your.html) · [Android Developers Blog, Mar 2026](https://android-developers.googleblog.com/2026/03/contact-picker-privacy-first-contact.html) — checked 2026-09-29.
- **Android and OEM news coverage (secondary) (1/2)** — [9to5Google: google android 17 pixel launch](https://9to5google.com/2026/06/16/google-android-17-pixel-launch/) · [9to5Google: android 16 qpr1 pixel](https://9to5google.com/2025/09/03/android-16-qpr1-pixel/) · [9to5Google, 28 Sep 2026: google assistant gemini android](https://9to5google.com/2026/09/28/google-assistant-gemini-android/) · [Business Today, 6 Aug 2026: google assistant to be replaced by gemini starting september on android and wearos 547570 2026 08 06](https://www.businesstoday.in/amp/technology/news/story/google-assistant-to-be-replaced-by-gemini-starting-september-on-android-and-wearos-547570-2026-08-06) · [Android Headlines: google assistant killed android gemini](https://www.androidheadlines.com/2026/09/google-assistant-killed-android-gemini.html) · [Android Authority: gemini screen context 3625824](https://www.androidauthority.com/gemini-screen-context-3625824/) · [Android Authority: android 16 qpr1 live updates 3573399](https://www.androidauthority.com/android-16-qpr1-live-updates-3573399/) · [Android Authority: android 17 live updates metric style template 3669117](https://www.androidauthority.com/android-17-live-updates-metric-style-template-3669117/) · [SamMobile: now bar one ui 9 support three more types third party apps](https://www.sammobile.com/news/now-bar-one-ui-9-support-three-more-types-third-party-apps/) · [Android Authority, 3 Jul 2025: one ui 8 live updates support 3573794](https://www.androidauthority.com/one-ui-8-live-updates-support-3573794/) · [Gizmochina: xiaomi hyperos 3 1 update new features smarter ui eligible device list](https://www.gizmochina.com/2026/01/30/xiaomi-hyperos-3-1-update-new-features-smarter-ui-eligible-device-list/) · [Nokiapoweruser: xiaomi hyperos 3 1 is here whats new who gets it who doesnt](https://nokiapoweruser.com/xiaomi-hyperos-3-1-is-here-whats-new-who-gets-it-who-doesnt/) · [Android Authority: android sideloading changes timeline 3679204](https://www.androidauthority.com/android-sideloading-changes-timeline-3679204/) · [9to5Google, 25 Feb 2026: android appfunctions gemini](https://9to5google.com/2026/02/25/android-appfunctions-gemini/) — checked 2026-09-29.
- **Android and OEM news coverage (secondary) (2/2)** — [Android Police: rip android instant apps](https://www.androidpolice.com/rip-android-instant-apps/) · [Android Authority: google killing android instant apps 3567211](https://www.androidauthority.com/google-killing-android-instant-apps-3567211/) — checked 2026-09-29.
- **OEM background limits** — [dontkillmyapp](https://dontkillmyapp.com/) · [dontkillmyapp: Xiaomi](https://dontkillmyapp.com/xiaomi) — checked 2026-09-29.
- **Other Android secondary** — [Guidance on Google Play's 16 KB page size (Broadcom KB)](https://knowledge.broadcom.com/external/article/411558/guidance-on-google-plays-16-kb-page-size.html) · [Taking photos, not so simply: ACTION_IMAGE_CAPTURE (egorand.dev)](https://www.egorand.dev/taking-photos-not-so-simply-how-i-got-bitten-by-action-image-capture/) — checked 2026-09-29.

### 8.3 React Native core, module technology and OTA

- **React Native core (1/3)** — [React Native 0.84 blog, 2026-02-11](https://reactnative.dev/blog/2026/02/11/react-native-0.84) · [RN View Style Props](https://reactnative.dev/docs/view-style-props) · [RN Linking docs](https://reactnative.dev/docs/linking) · [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction) · [RN blog index](https://reactnative.dev/blog) · [RN 0.82 blog](https://reactnative.dev/blog/2025/10/08/react-native-0.82) · [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87) · [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen) · [facebook/react-native 0.84-stable: combine-js-to-schema.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native-codegen/src/cli/combine/combine-js-to-schema.js) · [Appendix](https://reactnative.dev/docs/appendix) · [iOS guide](https://reactnative.dev/docs/turbo-native-modules-ios) · [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift) · [Android guide](https://reactnative.dev/docs/turbo-native-modules-android) · [Pure C++ modules](https://reactnative.dev/docs/the-new-architecture/pure-cxx-modules) — checked 2026-09-29.
- **React Native core (2/3)** — [Custom events](https://reactnative.dev/docs/the-new-architecture/native-modules-custom-events) · [Lifecycle](https://reactnative.dev/docs/the-new-architecture/native-modules-lifecycle) · [facebook/react-native 0.84-stable: RCTTurboModule.mm](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactCommon/react/nativemodule/core/platform/ios/ReactCommon/RCTTurboModule.mm) · [facebook/react-native 0.84-stable: RCTTurboModuleManager.mm](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactCommon/react/nativemodule/core/platform/ios/ReactCommon/RCTTurboModuleManager.mm) · [facebook/react-native 0.84-stable: JavaTurboModule.cpp](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactCommon/react/nativemodule/core/platform/android/ReactCommon/JavaTurboModule.cpp) · [facebook/react-native 0.84-stable: ReactQueueConfigurationSpec.kt](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactAndroid/src/main/java/com/facebook/react/bridge/queue/ReactQueueConfigurationSpec.kt) · [facebook/react-native 0.84-stable: TurboModuleRegistry.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/Libraries/TurboModule/TurboModuleRegistry.js) · [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction) · [facebook/react-native 0.84-stable: NativeModules.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/jest/mocks/NativeModules.js) · [RN 0.85 blog](https://reactnative.dev/blog/2026/04/07/react-native-0.85) · [facebook/react-native 0.84-stable: build.gradle.kts](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactAndroid/build.gradle.kts) · [facebook/react-native 0.84-stable: libs.versions.toml](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/gradle/libs.versions.toml) · [Create a library](https://reactnative.dev/docs/the-new-architecture/create-module-library) · [facebook/react-native 0.84-stable: helpers.rb](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/scripts/cocoapods/helpers.rb) — checked 2026-09-29.
- **React Native core (3/3)** — [react-native-community/discussions-and-proposals PR #1006 (AGP 9 RFC)](https://github.com/react-native-community/discussions-and-proposals/pull/1006) · [facebook/react-native 0.84-stable: NdkConfiguratorUtils.kt](https://github.com/facebook/react-native/blob/0.84-stable/packages/gradle-plugin/react-native-gradle-plugin/src/main/kotlin/com/facebook/react/utils/NdkConfiguratorUtils.kt) · [Upgrade Helper](https://react-native-community.github.io/upgrade-helper/) · [facebook/react-native #23313 (Lean Core umbrella)](https://github.com/facebook/react-native/issues/23313) · [react-native-community/discussions-and-proposals #6 (Lean Core)](https://github.com/react-native-community/discussions-and-proposals/issues/6) · [RN 0.79 blog](https://reactnative.dev/blog/2025/04/08/react-native-0.79) · [RN discussions #776 — react-native-community/discussions-and-proposals discussions 776](https://github.com/react-native-community/discussions-and-proposals/discussions/776) · [React Native 0.81](https://reactnative.dev/blog/2025/08/12/react-native-0.81) — checked 2026-09-29.
- **Tooling: builder-bob, Robolectric, Swift** — [create-react-native-library prompt.ts](https://raw.githubusercontent.com/callstack/react-native-builder-bob/main/packages/create-react-native-library/src/prompt.ts) · [Robolectric](https://robolectric.org/) · [Getting started](https://robolectric.org/getting-started/) · [builder-bob create docs](https://oss.callstack.com/react-native-builder-bob/create) · [Hacking with Swift: complete concurrency enabled by default](https://www.hackingwithswift.com/swift/6.0/concurrency) · [SwiftLee: Swift 6.2 concurrency changes](https://www.avanderlee.com/concurrency/swift-6-2-concurrency-changes/) — checked 2026-09-29.
- **Nitro** — [What is Nitro](https://nitro.margelo.com/docs/what-is-nitro) · [Nitro comparison](https://nitro.margelo.com/docs/comparison) · [Nitro minimum requirements](https://nitro.margelo.com/docs/minimum-requirements) · [mrousavy/nitro releases](https://github.com/mrousavy/nitro/releases) · [mrousavy/nitro (README)](https://github.com/mrousavy/nitro) · [How to build a Nitro Module](https://nitro.margelo.com/docs/getting-started/how-to-build-a-nitro-module) · [mrousavy/nitro #591 (folly-config.h not found)](https://github.com/mrousavy/nitro/issues/591) — checked 2026-09-29.
- **Expo (1/2)** — [Expo Modules overview](https://docs.expo.dev/modules/overview/) · [Expo SDK versions](https://docs.expo.dev/versions/latest/) · [Expo docs: Install Expo modules](https://docs.expo.dev/bare/installing-expo-modules/) · [Expo Module API](https://docs.expo.dev/modules/module-api/) · [Expo modules: Get started](https://docs.expo.dev/modules/get-started/) · [Expo blog: add native code with Expo Modules](https://expo.dev/blog/how-to-add-native-code-to-your-app-with-expo-modules) · [Mocking native calls in Expo modules](https://docs.expo.dev/modules/mocking/) · [Expo: Updating a bare app](https://docs.expo.dev/bare/updating-your-app/) · [Expo blog: App Store Connect minimum SDK 26](https://expo.dev/blog/app-store-connect-minimum-sdk-26) · [Expo SDK 58 beta changelog](https://expo.dev/changelog/sdk-58-beta) · [unpkg expo@57.0.26/bundledNativeModules.json](https://unpkg.com/expo@57.0.26/bundledNativeModules.json) · [Expo app-intents docs](https://docs.expo.dev/versions/v58.0.0/sdk/app-intents/) · [Expo blog: iOS widgets and Live Activities in Expo](https://expo.dev/blog/ios-widgets-and-live-activities-in-expo) · [Expo widgets docs](https://docs.expo.dev/versions/latest/sdk/widgets/) — checked 2026-09-29.
- **Expo (2/2)** — [Expo maps docs](https://docs.expo.dev/versions/latest/sdk/maps/) · [unpkg bundledNativeModules.json](https://unpkg.com/expo@56.0.23/bundledNativeModules.json) · [expo-print docs](https://docs.expo.dev/versions/latest/sdk/print/) · [expo-background-task docs](https://docs.expo.dev/versions/latest/sdk/background-task/) · [SDK 55](https://cdn.jsdelivr.net/npm/expo@55.0.31/bundledNativeModules.json) · [SDK 56](https://cdn.jsdelivr.net/npm/expo@56.0.23/bundledNativeModules.json) · [SDK 57](https://cdn.jsdelivr.net/npm/expo@57.0.26/bundledNativeModules.json) · [SDK 58](https://cdn.jsdelivr.net/npm/expo@58.0.0/bundledNativeModules.json) · [expo@55.0.31 (registry JSON)](https://registry.npmjs.org/expo/55.0.31) · [expo@56.0.23 (registry JSON)](https://registry.npmjs.org/expo/56.0.23) · [Expo docs: config plugins](https://docs.expo.dev/config-plugins/introduction/) — checked 2026-09-29.
- **OTA after CodePush** — [Microsoft Learn: App Center retirement](https://learn.microsoft.com/en-us/appcenter/retirement) · [microsoft/code-push-server](https://github.com/microsoft/code-push-server) · [Codemagic: React Native OTA tools in 2026](https://blog.codemagic.io/react-native-ota-tools-in-2026/) · [gronxb/hot-updater (README)](https://github.com/gronxb/hot-updater) · [microsoft/react-native-code-push](https://github.com/microsoft/react-native-code-push) · [Bitrise, updated 18 Sep 2026](https://bitrise.io/blog/post/what-app-stores-allow-with-ota-updates-apple-and-google-policy-explained) · [React Native OTA updates: complete 2026 guide (AppsOnAir)](https://www.appsonair.com/react-native-ota-updates-complete-2026-guide) — checked 2026-09-29.
- **How much native (industry)** — [FlashList v2 — Shopify Engineering](https://shopify.engineering/flashlist-v2) · [Five years of React Native at Shopify (2025-01-13)](https://shopify.engineering/five-years-of-react-native-at-shopify) · [Native is now the future of mobile at Shopify (2026-09-10)](https://shopify.engineering/back-to-native) — checked 2026-09-29.

### 8.4 Libraries

- **OneSignal** — [OneSignal/react-native-onesignal #1298 (ITMS-90683)](https://github.com/OneSignal/react-native-onesignal/issues/1298) · [OneSignal/OneSignal-iOS-SDK #1242 (ITMS-90683)](https://github.com/OneSignal/OneSignal-iOS-SDK/issues/1242) · [OneSignal cross-platform Live Activity setup](https://documentation.onesignal.com/docs/en/cross-platform-live-activity-setup) · [OneSignal: Focus modes and interruption levels](https://documentation.onesignal.com/docs/en/ios-focus-modes-and-interruption-levels) · [OneSignal in-app messages setup](https://documentation.onesignal.com/docs/en/in-app-messages-setup) · [OneSignal: Android Live Updates](https://documentation.onesignal.com/docs/en/android-live-notifications) · [OneSignal/react-native-onesignal](https://github.com/OneSignal/react-native-onesignal) · [OneSignal Live Activities](https://documentation.onesignal.com/docs/en/live-activities) — checked 2026-09-29.
- **npm registry pages (1/9)** — [@bacons/apple-targets](https://www.npmjs.com/package/@bacons/apple-targets) · [@callstack/liquid-glass](https://www.npmjs.com/package/@callstack/liquid-glass) · [date-fns](https://www.npmjs.com/package/date-fns) · [dayjs](https://www.npmjs.com/package/dayjs) · [expo](https://www.npmjs.com/package/expo) · [expo-app-intents](https://www.npmjs.com/package/expo-app-intents) · [expo-background-task](https://www.npmjs.com/package/expo-background-task) · [expo-camera](https://www.npmjs.com/package/expo-camera) · [expo-clipboard](https://www.npmjs.com/package/expo-clipboard) · [expo-contacts](https://www.npmjs.com/package/expo-contacts) · [expo-document-picker](https://www.npmjs.com/package/expo-document-picker) · [expo-file-system](https://www.npmjs.com/package/expo-file-system) — checked 2026-09-29.
- **npm registry pages (2/9)** — [expo-haptics](https://www.npmjs.com/package/expo-haptics) · [expo-image-manipulator](https://www.npmjs.com/package/expo-image-manipulator) · [expo-image-picker](https://www.npmjs.com/package/expo-image-picker) · [expo-image-picker (versions)](https://www.npmjs.com/package/expo-image-picker?activeTab=versions) · [expo-live-activity](https://www.npmjs.com/package/expo-live-activity) · [expo-local-authentication](https://www.npmjs.com/package/expo-local-authentication) · [expo-location](https://www.npmjs.com/package/expo-location) · [expo-maps](https://www.npmjs.com/package/expo-maps) · [expo-modules-core](https://www.npmjs.com/package/expo-modules-core) · [expo-modules-test-core](https://www.npmjs.com/package/expo-modules-test-core) · [expo-notifications](https://www.npmjs.com/package/expo-notifications) · [expo-print](https://www.npmjs.com/package/expo-print) — checked 2026-09-29.
- **npm registry pages (3/9)** — [expo-secure-store](https://www.npmjs.com/package/expo-secure-store) · [expo-sharing](https://www.npmjs.com/package/expo-sharing) · [expo-sqlite](https://www.npmjs.com/package/expo-sqlite) · [expo-updates](https://www.npmjs.com/package/expo-updates) · [expo-updates (versions)](https://www.npmjs.com/package/expo-updates?activeTab=versions) · [@expo/app-integrity](https://www.npmjs.com/package/@expo/app-integrity) · [@gorhom/bottom-sheet](https://www.npmjs.com/package/@gorhom/bottom-sheet) · [@hot-updater/react-native](https://www.npmjs.com/package/@hot-updater/react-native) · [@invertase/react-native-apple-authentication](https://www.npmjs.com/package/@invertase/react-native-apple-authentication) · [mappls-map-react-native](https://www.npmjs.com/package/mappls-map-react-native) · [moment](https://www.npmjs.com/package/moment) · [npm downloads API (last-week)](https://api.npmjs.org/downloads/point/last-week/react-native-share) — checked 2026-09-29.
- **npm registry pages (4/9)** — [npm registry (package search)](https://www.npmjs.com/) · [npm registry API](https://registry.npmjs.org/) · [react](https://www.npmjs.com/package/react) · [react-native](https://www.npmjs.com/package/react-native) · [react-native-app-clip](https://www.npmjs.com/package/react-native-app-clip) · [@react-native-async-storage/async-storage](https://www.npmjs.com/package/@react-native-async-storage/async-storage) · [react-native-blob-util](https://www.npmjs.com/package/react-native-blob-util) · [react-native-bluetooth-escpos-printer](https://www.npmjs.com/package/react-native-bluetooth-escpos-printer) · [react-native-code-push](https://www.npmjs.com/package/react-native-code-push) · [@react-native-community/datetimepicker](https://www.npmjs.com/package/@react-native-community/datetimepicker) · [@react-native-community/netinfo](https://www.npmjs.com/package/@react-native-community/netinfo) · [react-native-contact-picker](https://www.npmjs.com/package/react-native-contact-picker) — checked 2026-09-29.
- **npm registry pages (5/9)** — [react-native-device-info](https://www.npmjs.com/package/react-native-device-info) · [react-native-document-picker](https://www.npmjs.com/package/react-native-document-picker) · [@react-native-documents/picker](https://www.npmjs.com/package/@react-native-documents/picker) · [@react-native-documents/viewer](https://www.npmjs.com/package/@react-native-documents/viewer) · [@react-native-firebase/analytics](https://www.npmjs.com/package/@react-native-firebase/analytics) · [@react-native-firebase/app](https://www.npmjs.com/package/@react-native-firebase/app) · [@react-native-firebase/crashlytics](https://www.npmjs.com/package/@react-native-firebase/crashlytics) · [@react-native-firebase/in-app-messaging](https://www.npmjs.com/package/@react-native-firebase/in-app-messaging) · [@react-native-firebase/perf](https://www.npmjs.com/package/@react-native-firebase/perf) · [react-native-gesture-handler](https://www.npmjs.com/package/react-native-gesture-handler) · [react-native-html-to-pdf](https://www.npmjs.com/package/react-native-html-to-pdf) · [react-native-image-picker](https://www.npmjs.com/package/react-native-image-picker) — checked 2026-09-29.
- **npm registry pages (6/9)** — [react-native-image-resizer](https://www.npmjs.com/package/react-native-image-resizer) · [react-native-keychain](https://www.npmjs.com/package/react-native-keychain) · [react-native-linear-gradient](https://www.npmjs.com/package/react-native-linear-gradient) · [react-native-maps](https://www.npmjs.com/package/react-native-maps) · [@react-native-ml-kit/barcode-scanning](https://www.npmjs.com/package/@react-native-ml-kit/barcode-scanning) · [react-native-notify-kit](https://www.npmjs.com/package/react-native-notify-kit) · [react-native-onesignal](https://www.npmjs.com/package/react-native-onesignal) · [react-native-paper](https://www.npmjs.com/package/react-native-paper) · [react-native-passkey](https://www.npmjs.com/package/react-native-passkey) · [react-native-pdf](https://www.npmjs.com/package/react-native-pdf) · [react-native-permissions](https://www.npmjs.com/package/react-native-permissions) · [react-native-reanimated](https://www.npmjs.com/package/react-native-reanimated) — checked 2026-09-29.
- **npm registry pages (7/9)** — [react-native-safe-area-context](https://www.npmjs.com/package/react-native-safe-area-context) · [react-native-screens](https://www.npmjs.com/package/react-native-screens) · [react-native-share](https://www.npmjs.com/package/react-native-share) · [react-native-siri-shortcut](https://www.npmjs.com/package/react-native-siri-shortcut) · [react-native-sms-retriever](https://www.npmjs.com/package/react-native-sms-retriever) · [react-native-stallion](https://www.npmjs.com/package/react-native-stallion) · [react-native-svg](https://www.npmjs.com/package/react-native-svg) · [react-native-update](https://www.npmjs.com/package/react-native-update) · [react-native-upi-pay](https://www.npmjs.com/package/react-native-upi-pay) · [react-native-upi-payment](https://www.npmjs.com/package/react-native-upi-payment) · [react-native-vision-camera](https://www.npmjs.com/package/react-native-vision-camera) · [react-native-vision-camera-barcode-scanner](https://www.npmjs.com/package/react-native-vision-camera-barcode-scanner) — checked 2026-09-29.
- **npm registry pages (8/9)** — [react-native-webview](https://www.npmjs.com/package/react-native-webview) · [react-native-widget-extension](https://www.npmjs.com/package/react-native-widget-extension) · [react-native-worklets](https://www.npmjs.com/package/react-native-worklets) · [@react-navigation/bottom-tabs](https://www.npmjs.com/package/@react-navigation/bottom-tabs) · [@react-navigation/drawer](https://www.npmjs.com/package/@react-navigation/drawer) · [@react-navigation/elements](https://www.npmjs.com/package/@react-navigation/elements) · [@react-navigation/native](https://www.npmjs.com/package/@react-navigation/native) · [@react-navigation/native-stack](https://www.npmjs.com/package/@react-navigation/native-stack) · [@react-navigation/stack](https://www.npmjs.com/package/@react-navigation/stack) · [react-redux](https://www.npmjs.com/package/react-redux) · [@reduxjs/toolkit](https://www.npmjs.com/package/@reduxjs/toolkit) · [@revopush/react-native-code-push](https://www.npmjs.com/package/@revopush/react-native-code-push) — checked 2026-09-29.
- **npm registry pages (9/9)** — [@shopify/flash-list](https://www.npmjs.com/package/@shopify/flash-list) · [voltra](https://www.npmjs.com/package/voltra) — checked 2026-09-29.
- **React Native Directory (1/7)** — [app-integrity (Directory API)](https://reactnative.directory/api/libraries?search=app-integrity) · [apple-targets (Directory)](https://reactnative.directory/?search=apple-targets) · [earl-thermal (Directory API)](https://reactnative.directory/api/libraries?search=earl-thermal) · [expo-location (Directory API)](https://reactnative.directory/api/libraries?search=expo-location) · [expo-print (Directory API)](https://reactnative.directory/api/libraries?search=expo-print) · [expo-quick-actions (Directory API)](https://reactnative.directory/api/libraries?search=expo-quick-actions) · [expo-sharing (Directory API)](https://reactnative.directory/api/libraries?search=expo-sharing) · [expo-widgets (Directory API)](https://reactnative.directory/api/libraries?search=expo-widgets) · [@gorhom/bottom-sheet (Directory API)](https://reactnative.directory/api/libraries?search=%40gorhom%2Fbottom-sheet) · [image-resizer (Directory API)](https://reactnative.directory/api/libraries?search=image-resizer) · [in-app-messaging (Directory)](https://reactnative.directory/?search=in-app-messaging) · [@maplibre/maplibre-react-native (Directory API)](https://reactnative.directory/api/libraries?search=%40maplibre%2Fmaplibre-react-native) — checked 2026-09-29.
- **React Native Directory (2/7)** — [notifee (Directory)](https://reactnative.directory/?search=notifee) · [quick-actions (Directory)](https://reactnative.directory/?search=quick-actions) · [React Native Directory](https://reactnative.directory/) · [react-native-android-widget (Directory API)](https://reactnative.directory/api/libraries?search=react-native-android-widget) · [react-native-app-clip (Directory)](https://reactnative.directory/?search=react-native-app-clip) · [@react-native-async-storage/async-storage (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-async-storage%2Fasync-storage) · [react-native-background-fetch (Directory API)](https://reactnative.directory/api/libraries?search=react-native-background-fetch) · [react-native-background-geolocation (Directory API)](https://reactnative.directory/api/libraries?search=react-native-background-geolocation) · [react-native-background-upload (Directory API)](https://reactnative.directory/api/libraries?search=react-native-background-upload) · [react-native-biometrics (Directory API)](https://reactnative.directory/api/libraries?search=react-native-biometrics) · [react-native-ble-plx (Directory API)](https://reactnative.directory/api/libraries?search=react-native-ble-plx) · [react-native-blob-util (Directory API)](https://reactnative.directory/api/libraries?search=react-native-blob-util) — checked 2026-09-29.
- **React Native Directory (3/7)** — [react-native-bluetooth-classic (Directory API)](https://reactnative.directory/api/libraries?search=react-native-bluetooth-classic) · [react-native-camera-kit (Directory API)](https://reactnative.directory/api/libraries?search=react-native-camera-kit) · [react-native-code-push (Directory API)](https://reactnative.directory/api/libraries?search=react-native-code-push) · [@react-native-community/datetimepicker (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-community%2Fdatetimepicker) · [@react-native-community/geolocation (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-community%2Fgeolocation) · [@react-native-community/netinfo (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-community%2Fnetinfo) · [react-native-compressor (Directory API)](https://reactnative.directory/api/libraries?search=react-native-compressor) · [react-native-device-info (Directory API)](https://reactnative.directory/api/libraries?search=react-native-device-info) · [react-native-document-scanner-plugin (Directory API)](https://reactnative.directory/api/libraries?search=react-native-document-scanner-plugin) · [@react-native-documents/picker (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-documents%2Fpicker) · [react-native-edge-to-edge (Directory API)](https://reactnative.directory/api/libraries?search=react-native-edge-to-edge) · [react-native-file-access (Directory API)](https://reactnative.directory/api/libraries?search=react-native-file-access) — checked 2026-09-29.
- **React Native Directory (4/7)** — [@react-native-firebase/app (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-firebase%2Fapp) · [@react-native-firebase/in-app-messaging (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-firebase%2Fin-app-messaging) · [@react-native-firebase/messaging (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-firebase%2Fmessaging) · [react-native-geolocation-service (Directory API)](https://reactnative.directory/api/libraries?search=react-native-geolocation-service) · [react-native-gesture-handler (Directory API)](https://reactnative.directory/api/libraries?search=react-native-gesture-handler) · [@react-native-google-signin/google-signin (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-google-signin%2Fgoogle-signin) · [react-native-html-to-pdf (Directory API)](https://reactnative.directory/api/libraries?search=react-native-html-to-pdf) · [react-native-html-to-pdf (Directory)](https://reactnative.directory/?search=react-native-html-to-pdf) · [react-native-image-crop-picker (Directory API)](https://reactnative.directory/api/libraries?search=react-native-image-crop-picker) · [react-native-image-picker (Directory API)](https://reactnative.directory/api/libraries?search=react-native-image-picker) · [react-native-keychain (Directory API)](https://reactnative.directory/api/libraries?search=react-native-keychain) · [react-native-linear-gradient (Directory API)](https://reactnative.directory/api/libraries?search=react-native-linear-gradient) — checked 2026-09-29.
- **React Native Directory (5/7)** — [react-native-maps (Directory API)](https://reactnative.directory/api/libraries?search=react-native-maps) · [react-native-maps (Directory)](https://reactnative.directory/?search=react-native-maps) · [@react-native-ml-kit/barcode-scanning (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-ml-kit%2Fbarcode-scanning) · [@react-native-ml-kit/text-recognition (Directory API)](https://reactnative.directory/api/libraries?search=%40react-native-ml-kit%2Ftext-recognition) · [react-native-mmkv (Directory API)](https://reactnative.directory/api/libraries?search=react-native-mmkv) · [react-native-notify-kit (Directory API)](https://reactnative.directory/api/libraries?search=react-native-notify-kit) · [react-native-onesignal (Directory API)](https://reactnative.directory/api/libraries?search=react-native-onesignal) · [react-native-otp-verify (Directory API)](https://reactnative.directory/api/libraries?search=react-native-otp-verify) · [react-native-passkey (Directory API)](https://reactnative.directory/api/libraries?search=react-native-passkey) · [react-native-pdf (Directory API)](https://reactnative.directory/api/libraries?search=react-native-pdf) · [react-native-print (Directory API)](https://reactnative.directory/api/libraries?search=react-native-print) · [react-native-print (Directory)](https://reactnative.directory/?search=react-native-print) — checked 2026-09-29.
- **React Native Directory (6/7)** — [react-native-quick-actions (Directory API)](https://reactnative.directory/api/libraries?search=react-native-quick-actions) · [react-native-reanimated (Directory API)](https://reactnative.directory/api/libraries?search=react-native-reanimated) · [react-native-safe-area-context (Directory API)](https://reactnative.directory/api/libraries?search=react-native-safe-area-context) · [react-native-screens (Directory API)](https://reactnative.directory/api/libraries?search=react-native-screens) · [react-native-share (Directory API)](https://reactnative.directory/api/libraries?search=react-native-share) · [react-native-shared-group-preferences (Directory)](https://reactnative.directory/?search=react-native-shared-group-preferences) · [react-native-shortcuts (Directory API)](https://reactnative.directory/api/libraries?search=react-native-shortcuts) · [react-native-siri-shortcut (Directory)](https://reactnative.directory/?search=react-native-siri-shortcut) · [react-native-sms-retriever (Directory API)](https://reactnative.directory/api/libraries?search=react-native-sms-retriever) · [react-native-svg (Directory API)](https://reactnative.directory/api/libraries?search=react-native-svg) · [react-native-thermal-printer (Directory API)](https://reactnative.directory/api/libraries?search=react-native-thermal-printer) · [react-native-vision-camera (Directory API)](https://reactnative.directory/api/libraries?search=react-native-vision-camera) — checked 2026-09-29.
- **React Native Directory (7/7)** — [react-native-webview (Directory API)](https://reactnative.directory/api/libraries?search=react-native-webview) · [react-native-worklets (Directory API)](https://reactnative.directory/api/libraries?search=react-native-worklets) · [@react-navigation/stack (Directory API)](https://reactnative.directory/api/libraries?search=%40react-navigation%2Fstack) · [@shopify/flash-list (Directory API)](https://reactnative.directory/api/libraries?search=%40shopify%2Fflash-list) · [sms-user-consent (Directory API)](https://reactnative.directory/api/libraries?search=sms-user-consent) · [voltra (Directory API)](https://reactnative.directory/api/libraries?search=voltra) — checked 2026-09-29.
- **Library repositories, issues and PRs (1/9)** — [a7medev/react-native-ml-kit](https://github.com/a7medev/react-native-ml-kit) · [Agontuk/react-native-geolocation-service](https://github.com/Agontuk/react-native-geolocation-service) · [alpha0010/react-native-file-access](https://github.com/alpha0010/react-native-file-access) · [Android ongoing-notification docs — callstackincubator/voltra: managing-ongoing-notifications.md](https://github.com/callstackincubator/voltra/blob/main/website/docs/v1/android/development/managing-ongoing-notifications.md) · [bamlab/react-native-image-resizer](https://github.com/bamlab/react-native-image-resizer) · [benjamineruvieru/react-native-credentials-manager](https://github.com/benjamineruvieru/react-native-credentials-manager) · [birdofpreyru/react-native-fs](https://github.com/birdofpreyru/react-native-fs) · [bndkt/react-native-app-clip](https://github.com/bndkt/react-native-app-clip) · [bndkt/react-native-widget-extension](https://github.com/bndkt/react-native-widget-extension) · [callstackincubator/voltra](https://github.com/callstackincubator/voltra) · [callstackincubator/voltra PR #325](https://github.com/callstackincubator/voltra/pull/325) · [callstackincubator/voltra PR #326](https://github.com/callstackincubator/voltra/pull/326) — checked 2026-09-29.
- **Library repositories, issues and PRs (2/9)** — [callstackincubator/voltra: 0008-android-ongoing-notification-live-updates-api.md](https://github.com/callstackincubator/voltra/blob/main/docs/adr/0008-android-ongoing-notification-live-updates-api.md) · [christopherdro/react-native-html-to-pdf](https://github.com/christopherdro/react-native-html-to-pdf) · [christopherdro/react-native-print](https://github.com/christopherdro/react-native-print) · [codibly/app-clip-instant-app-react-native: Handling-Size-React-Native-AppClip.md](https://github.com/codibly/app-clip-instant-app-react-native/blob/main/Handling-Size-React-Native-AppClip.md) · [colonelpanic8/mova PR #13 (an AppFunctions example found by search)](https://github.com/colonelpanic8/mova/pull/13) · [deprecated repo notice — mappls-api/mapmyindia-restapi-react-native-beta](https://github.com/mappls-api/mapmyindia-restapi-react-native-beta) · [dotintent/react-native-ble-plx](https://github.com/dotintent/react-native-ble-plx) · [douglasjunior/react-native-pdf-renderer](https://github.com/douglasjunior/react-native-pdf-renderer) · [emeraldsanto/react-native-encrypted-storage](https://github.com/emeraldsanto/react-native-encrypted-storage) · [EvanBacon/expo-apple-targets](https://github.com/EvanBacon/expo-apple-targets) · [EvanBacon/expo-quick-actions](https://github.com/EvanBacon/expo-quick-actions) · [expo-continued-task — aermes-ai/expo-continued-task](https://github.com/aermes-ai/expo-continued-task) — checked 2026-09-29.
- **Library repositories, issues and PRs (3/9)** — [expo-thermal-printer README (search summary) — Ricka7x/expo-thermal-printer](https://github.com/Ricka7x/expo-thermal-printer) · [expo/expo](https://github.com/expo/expo) · [expo/expo #37590](https://github.com/expo/expo/issues/37590) · [expo/expo #46664 (Xcode 27 launch crash without UIScene)](https://github.com/expo/expo/issues/46664) · [expo/expo PR #50188](https://github.com/expo/expo/pull/50188) · [f-23/react-native-passkey](https://github.com/f-23/react-native-passkey) · [faizalshap/react-native-otp-verify](https://github.com/faizalshap/react-native-otp-verify) · [gre/react-native-view-shot](https://github.com/gre/react-native-view-shot) · [Gustash/react-native-siri-shortcut](https://github.com/Gustash/react-native-siri-shortcut) · [HeligPfleigh/react-native-thermal-receipt-printer](https://github.com/HeligPfleigh/react-native-thermal-receipt-printer) · [Hopding/pdf-lib](https://github.com/Hopding/pdf-lib) · [infinitered/react-native-mlkit](https://github.com/infinitered/react-native-mlkit) — checked 2026-09-29.
- **Library repositories, issues and PRs (4/9)** — [innoveit/react-native-ble-manager](https://github.com/innoveit/react-native-ble-manager) · [invertase/react-native-firebase](https://github.com/invertase/react-native-firebase) · [iOS docs tree — callstackincubator/voltra: ios](https://github.com/callstackincubator/voltra/tree/main/website/docs/v1/ios) · [itinance/react-native-fs](https://github.com/itinance/react-native-fs) · [ivpusic/react-native-image-crop-picker](https://github.com/ivpusic/react-native-image-crop-picker) · [jamenamcinteer/react-native-vision-camera-ocr-plus](https://github.com/jamenamcinteer/react-native-vision-camera-ocr-plus) · [jordanbyron/react-native-quick-actions](https://github.com/jordanbyron/react-native-quick-actions) · [kenjdavidson/react-native-bluetooth-classic](https://github.com/kenjdavidson/react-native-bluetooth-classic) · [kesha-antonov/react-native-background-downloader](https://github.com/kesha-antonov/react-native-background-downloader) · [KjellConnelly/react-native-shared-group-preferences](https://github.com/KjellConnelly/react-native-shared-group-preferences) · [lodev09/react-native-exify](https://github.com/lodev09/react-native-exify) · [maplibre/maplibre-react-native](https://github.com/maplibre/maplibre-react-native) — checked 2026-09-29.
- **Library repositories, issues and PRs (5/9)** — [margelo/nitro](https://github.com/margelo/nitro) · [margelo/react-native-mmkv](https://github.com/margelo/react-native-mmkv) · [margelo/react-native-nitro-zxing](https://github.com/margelo/react-native-nitro-zxing) · [margelo/react-native-vision-camera](https://github.com/margelo/react-native-vision-camera) · [mCodex/react-native-sensitive-info](https://github.com/mCodex/react-native-sensitive-info) · [michalchudziak/react-native-geolocation](https://github.com/michalchudziak/react-native-geolocation) · [mkuczera/react-native-haptic-feedback](https://github.com/mkuczera/react-native-haptic-feedback) · [morenoh149/react-native-contacts](https://github.com/morenoh149/react-native-contacts) · [mrousavy/react-native-vision-camera releases](https://github.com/mrousavy/react-native-vision-camera/releases) · [NitroBenchmarks — mrousavy/NitroBenchmarks](https://github.com/mrousavy/NitroBenchmarks) · [NitrogenZLab/react-native-multiple-image-picker](https://github.com/NitrogenZLab/react-native-multiple-image-picker) · [Notifee README — invertase/notifee](https://github.com/invertase/notifee) — checked 2026-09-29.
- **Library repositories, issues and PRs (6/9)** — [notify-kit README — marcocrupi/react-native-notify-kit](https://github.com/marcocrupi/react-native-notify-kit) · [Nozbe/WatermelonDB](https://github.com/Nozbe/WatermelonDB) · [numandev1/react-native-compressor](https://github.com/numandev1/react-native-compressor) · [oblador/react-native-keychain](https://github.com/oblador/react-native-keychain) · [OP-Engineering/op-sqlite](https://github.com/OP-Engineering/op-sqlite) · [pchalupa/expo-text-extractor](https://github.com/pchalupa/expo-text-extractor) · [peterferguson/react-native-passkeys](https://github.com/peterferguson/react-native-passkeys) · [phattran1201/react-native-thermal-printer](https://github.com/phattran1201/react-native-thermal-printer) · [pushpender-singh-ap/react-native-otp-verify](https://github.com/pushpender-singh-ap/react-native-otp-verify) · [react-native-android-widget — sAleksovski/react-native-android-widget: limitations.md](https://github.com/sAleksovski/react-native-android-widget/blob/master/docs/docs/limitations.md) · [react-native-clipboard/clipboard](https://github.com/react-native-clipboard/clipboard) · [react-native-continued-task — mahdidavoodi7/react-native-continued-task](https://github.com/mahdidavoodi7/react-native-continued-task) — checked 2026-09-29.
- **Library repositories, issues and PRs (7/9)** — [react-native-documents/document-picker](https://github.com/react-native-documents/document-picker) · [react-native-esc-pos-printer — tr3v3r/react-native-esc-pos-printer](https://github.com/tr3v3r/react-native-esc-pos-printer) · [react-native-image-picker/react-native-image-picker](https://github.com/react-native-image-picker/react-native-image-picker) · [react-native-maps — react-native-maps/react-native-maps: installation.md](https://github.com/react-native-maps/react-native-maps/blob/master/docs/installation.md) · [react-native-maps/react-native-maps](https://github.com/react-native-maps/react-native-maps) · [react-native-screens#4081 — software-mansion/react-native-screens #4081](https://github.com/software-mansion/react-native-screens/issues/4081) · [react-native-share docs — react-native-share/react-native-share: share-single.mdx](https://github.com/react-native-share/react-native-share/blob/main/website/docs/share-single.mdx) · [react-native-share/react-native-share](https://github.com/react-native-share/react-native-share) · [react-native-share/react-native-share #1556](https://github.com/react-native-share/react-native-share/issues/1556) · [react-native-share/react-native-share #1699](https://github.com/react-native-share/react-native-share/issues/1699) · [rnmapbox/maps](https://github.com/rnmapbox/maps) · [RonRadtke/react-native-blob-util](https://github.com/RonRadtke/react-native-blob-util) — checked 2026-09-29.
- **Library repositories, issues and PRs (8/9)** — [RonRadtke/react-native-blob-util #395](https://github.com/RonRadtke/react-native-blob-util/issues/395) · [sAleksovski/react-native-android-widget](https://github.com/sAleksovski/react-native-android-widget) · [sAleksovski/react-native-android-widget: update-widget.md](https://github.com/sAleksovski/react-native-android-widget/blob/master/docs/docs/update-widget.md) · [sbaiahmed1/react-native-biometrics](https://github.com/sbaiahmed1/react-native-biometrics) · [SelfLender/react-native-biometrics](https://github.com/SelfLender/react-native-biometrics) · [software-mansion-labs/expo-live-activity](https://github.com/software-mansion-labs/expo-live-activity) · [star-micronics/react-native-star-io10](https://github.com/star-micronics/react-native-star-io10) · [streem/react-native-select-contact](https://github.com/streem/react-native-select-contact) · [Swif7ify/react-native-earl-thermal-printer](https://github.com/Swif7ify/react-native-earl-thermal-printer) · [teslamotors/react-native-camera-kit](https://github.com/teslamotors/react-native-camera-kit) · [thiendangit/react-native-thermal-receipt-printer-image-qr](https://github.com/thiendangit/react-native-thermal-receipt-printer-image-qr) · [transistorsoft/react-native-background-fetch](https://github.com/transistorsoft/react-native-background-fetch) — checked 2026-09-29.
- **Library repositories, issues and PRs (9/9)** — [transistorsoft/react-native-background-geolocation](https://github.com/transistorsoft/react-native-background-geolocation) · [Vydia/react-native-background-upload](https://github.com/Vydia/react-native-background-upload) · [WebsiteBeaver/react-native-document-scanner-plugin](https://github.com/WebsiteBeaver/react-native-document-scanner-plugin) · [wix/react-native-notifications](https://github.com/wix/react-native-notifications) · [wonday/react-native-pdf](https://github.com/wonday/react-native-pdf) · [YanYuanFE/react-native-signature-canvas](https://github.com/YanYuanFE/react-native-signature-canvas) · [zoontek/react-native-permissions](https://github.com/zoontek/react-native-permissions) — checked 2026-09-29.
- **Library docs, tutorials and secondary write-ups (1/2)** — [Working with different threads in Swift TurboModules (Callstack, 2026-01-19)](https://www.callstack.com/tutorials/working-with-different-threads-in-swift-turbomodules) · [Siri Shortcuts integration in React Native (vp0)](https://vp0.com/blogs/siri-shortcuts-integration-react-native-ai) · [Live Activities and widgets with React: say hello to Voltra (Callstack)](https://www.callstack.com/blog/live-activities-and-widgets-with-react-say-hello-to-voltra) · [Using critical alerts on iOS (Igor Kulman)](https://blog.kulman.sk/using-critical-alerts-on-ios/) · [Critical alerts entitlement (Newly)](https://newly.app/articles/critical-alerts-entitlement) · [Time Sensitive notifications on iOS (Pushwoosh help)](https://help.pushwoosh.com/hc/en-us/articles/27979836066717-How-do-I-configure-and-use-Time-Sensitive-notifications-for-my-iOS-app) · [Notifee is archived — a maintained New-Architecture drop-in (dev.to, fork author)](https://dev.to/marco_crupi/notifee-is-archived-heres-a-maintained-new-architecture-drop-in-replacement-3ib5) · [iOS 26 push changes and the iOS 27 UIScene requirement (Courier)](https://www.courier.com/blog/ios-26-push-notification-changes-uiscene-requirment-ios-27) · [Setup default App Clip experience without a server (Medium)](https://medium.com/@alexander100s124/setup-default-app-clip-experience-without-a-server-6dee3f995c5d) · [HTML to PDF in React (transformy.io guide)](https://transformy.io/guides/html-to-pdf-react/) · [iOS 26: Apple adds native table detection to Vision (Medium)](https://medium.com/@surajkumbhar904/ios-26-apple-adds-native-table-detection-to-vision-framework-142558ab086a) · [VisionCamera v5 with Marc Rousavy (Callstack podcast)](https://www.callstack.com/podcasts/visioncamera-v5-with-marc-rousavy) · [react-native-vision-camera-ocr-plus v2 released (dev.to)](https://dev.to/jamenamcinteer/react-native-vision-camera-ocr-plus-v2-released-with-vision-camera-v5-nitro-modules-compatibility-5c32) · [Privacy manifest SDK list (Singular)](https://www.singular.net/blog/privacy-manifest-sdks/) — checked 2026-09-29.
- **Library docs, tutorials and secondary write-ups (2/2)** — [React Navigation native stack](https://reactnavigation.org/docs/native-stack-navigator/) · [LobeHub skill page for react-native-vision-camera](https://lobehub.com/skills/margelo-react-native-skills-react-native-vision-camera) · [react-native-android-widget docs](https://saleksovski.github.io/react-native-android-widget/) · [What's new in VisionCamera v5 (Margelo)](https://margelo.com/blog/whats-new-in-visioncamera-v5) · [Transistorsoft premium licence (shop)](https://shop.transistorsoft.com/products/react-native-background-geolocation-premium-license) · [React Native Google Sign-In: install docs](https://react-native-google-signin.github.io/docs/install) · [Google Play 16 KB page size requirement — before November 2025 (Medium)](https://medium.com/@ahmetatalay95/google-play-16kb-page-size-requirement-what-you-need-to-do-before-november-2025-9c85831ca11f) · [VisionCamera docs: barcode scanner](https://visioncamera.margelo.com/docs/barcode-scanner) · [QR and barcode scanning with VisionCamera v5 (Margelo blog)](https://margelo.com/blog/react-native-qr-barcode-scanner-visioncamera-v5) · [React Native Live Activities Handbook (freeCodeCamp, 2026-07-14)](https://www.freecodecamp.org/news/react-native-live-activities-handbook/) · [iOS App Shortcuts / Intents on a React Native project (Medium, sudoplz)](https://medium.com/@sudoplz/ios-app-shortcuts-intents-on-a-react-native-project-to-enable-voice-commands-with-siri-and-95fa9fc29a34) · [Star Micronics Bluetooth receipt printers](https://starmicronics.com/bluetooth-receipt-printers-pos-thermal-impact-portable/) · [React Native OTA after CodePush: how to choose a tool in 2026 (DEV)](https://dev.to/gfean/react-native-ota-after-codepush-how-to-choose-a-tool-in-2026-46of) — checked 2026-09-29.
- **Other library docs** — [Moment.js docs, project status](https://momentjs.com/docs/) — checked 2026-09-29.

### 8.5 Indian market and product

- **Market data** — [StatCounter India](https://gs.statcounter.com/android-version-market-share/mobile/india) — checked 2026-09-29.
- **Comparable apps (1/3)** — [State of RN 2025 platform APIs](https://results.stateofreactnative.com/en-US/platform-apis/) · [State of React Native 2025 — overview](https://results.stateofreactnative.com/en-US/) · [Khatabook (Google Play)](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook) · [OkCredit (Google Play)](https://play.google.com/store/apps/details?id=in.okcredit.merchant) · [Vyapar (Google Play)](https://play.google.com/store/apps/details?id=in.android.vyapar) · [myBillBook (Google Play)](https://play.google.com/store/apps/details?id=com.valorem.flobooks) · [Paytm for Business (Google Play)](https://play.google.com/store/apps/details?id=com.paytm.business) · [PhonePe Business (Google Play)](https://play.google.com/store/apps/details?id=com.phonepe.app.business) · [Google Pay for Business (Google Play)](https://play.google.com/store/apps/details?id=com.google.android.apps.nbu.paisa.merchant) · [Zoho Invoice (Google Play)](https://play.google.com/store/apps/details?id=com.zoho.invoice) · [Zoho Books (Google Play)](https://play.google.com/store/apps/details?id=com.zoho.books) · [IndianOil For Business (Google Play)](https://play.google.com/store/apps/details?id=px.indianoil.in) · [IndianOil ONE (Google Play)](https://play.google.com/store/apps/details?id=cx.indianoil.in) · [HP Buddy (HPCL) (Google Play)](https://play.google.com/store/apps/details?id=com.hpcl.salesapp) — checked 2026-09-29.
- **Comparable apps (2/3)** — [HPCL Merchant App (Google Play)](https://play.google.com/store/apps/details?id=com.hpclmerchant) · [PetroByte (Google Play)](https://play.google.com/store/apps/details?id=com.beanbyte.petrobyte) · [SCUBE Petrol Pump Software (Google Play)](https://play.google.com/store/apps/details?id=com.petroprime.dsmapp) · [Repos (doorstep diesel) (Google Play)](https://play.google.com/store/apps/details?id=com.reposenergy.customer) · [FuelBuddy (Google Play)](https://play.google.com/store/apps/details?id=in.fuelbuddy.app) · [Vyapar (search summary)](https://vyaparapp.in/free/small-business-accounting-software/petrol-pump) · [Keshav Solutions (search summary)](https://keshavsolutions.com/petrol-pump-software/) · [PetroPulse360 (search summary)](https://petropulse360.com/petrol-pump-credit-management) · [Vyapar thermal](https://vyaparapp.in/free/billing-software-for-retail-shop/thermal-printer) · [myBillBook thermal](https://mybillbook.in/s/billing-software-for-retail-shop/thermal-printer/) · [Zoho blog, iOS 16](https://www.zoho.com/blog/general/take-your-work-to-the-next-level-with-zoho-apps-in-ios-16.html) · [Zoho Books iOS 18 blog](https://www.zoho.com/blog/books/ios-updates-for-zoho-books.html) · [Swiggy Design: Live Activity and Dynamic Island (Medium; snippet only, page 403)](https://medium.com/swiggydesign/designing-with-constraints-live-activity-and-dynamic-island-71271c454bcb) · [Behance](https://www.behance.net/gallery/157101731/Zomato-Live-Activities) — checked 2026-09-29.
- **Comparable apps (3/3)** — [Petrosoft blog](https://petrolbunksoftware.com/blog/mobile-app-for-your-petrol-pump) — checked 2026-09-29.
- **UPI and payments** — [Razorpay: UPI Intent](https://razorpay.com/docs/payments/payment-methods/upi/upi-intent/) · [Juspay: UPI Intent](https://juspay.io/in/docs/api-reference/docs/express-checkout/upi-intent) · [NPCI spec PDF (third-party host)](https://www.labnol.org/files/linking.pdf) · [Google Pay for India developers](https://developers.google.com/pay/india/api/android/in-app-payments) · [MediaNama](https://www.medianama.com/2025/08/223-npci-p2p-collect-payments-oct-1-what-it-means/) · [Business Standard](https://www.business-standard.com/finance/personal-finance/upi-collect-requests-to-end-from-october-here-s-how-it-will-affect-you-125081500774_1.html) · [PayU RN UPI SDK](https://docs.payu.in/docs/react-native-upi-sdk) · [Cashfree UPI intent](https://www.cashfree.com/docs/payments/online/mobile/misc/upi_intent_support_js_sdk) · [Paytm Payments iOS](https://www.paytmpayments.com/docs/integration-steps-for-ios/) · [NPCI UPI deep-linking spec — summary (GitHub wiki)](https://github.com/bgagan911/RandomDocs/wiki/NPCI-UPI---Specifications-for-Deep-Linking) — checked 2026-09-29.
- **WhatsApp** — [businesschat.io guide](https://help.businesschat.io/en/articles/6517838-how-to-build-a-whatsapp-click-to-chat-url-wa-me) · [Chatfuel](https://chatfuel.com/blog/create-whatsapp-link) · [ChatMaxima India pricing](https://chatmaxima.com/whatsapp-api-pricing/india/) · [WATI](https://www.wati.io/en/blog/whatsapp-api-pricing-guide/) · [AiSensy](https://aisensy.com/pricing) · [MyOperator](https://myoperator.com/blog/whatsapp-business-api-pricing-india-2026) · [WhatsApp FAQ](https://faq.whatsapp.com/5913398998672934) — checked 2026-09-29.
- **GST e-invoice QR** — [Masters India](https://www.mastersindia.co/blog/signed-qr-code-e-invoicing-system/) · [NIC e-invoice API FAQ](https://einv-apisandbox.nic.in/FaqsonAPI.html) · [e-invoice public keys](https://einvoice6.gst.gov.in/content/public-keys/) · [ClearTax verifier app](https://cleartax.in/s/qr-code-verify-app-e-invoicing) — checked 2026-09-29.

### 8.6 Store rating and review

The sixth research note (store rating and review, 2026-09-30) cites 81 links to 52 distinct pages, listed once each below — all checked on **2026-09-30**. Titles are descriptive where the note's link text was not.

- **StoreKit review API (Apple)** — [AppStore.requestReview(in:) (UIWindowScene)](https://developer.apple.com/documentation/storekit/appstore/requestreview%28in:%29-1q8qs) · [AppStore.requestReview(in:) (macOS overload)](https://developer.apple.com/documentation/storekit/appstore/requestreview%28in:%29-4r0y9) · [RequestReviewAction](https://developer.apple.com/documentation/storekit/requestreviewaction) · [SKStoreReviewController.requestReview(in:)](https://developer.apple.com/documentation/storekit/skstorereviewcontroller/requestreview%28in:%29) · [SKStoreReviewController](https://developer.apple.com/documentation/storekit/skstorereviewcontroller) · [SKStoreReviewController.requestReview()](https://developer.apple.com/documentation/storekit/skstorereviewcontroller/requestreview%28%29) · [AppStore](https://developer.apple.com/documentation/storekit/appstore) · [StoreKit updates](https://developer.apple.com/documentation/updates/storekit) · [Requesting App Store reviews (sample)](https://developer.apple.com/documentation/storekit/requesting-app-store-reviews) — checked 2026-09-30.
- **Apple rules, guidance and App Store Connect** — [App Store Review Guidelines ("Updated: June 8, 2026")](https://developer.apple.com/app-store/review/guidelines/) · [Apple Developer News, 8 Jun 2026 (guideline revision)](https://developer.apple.com/news/?id=a233fmpw) · [Apple Developer News, 13 Nov 2025 (guideline revision)](https://developer.apple.com/news/?id=ey6d8onl) · [Apple Developer News, 1 Feb 2021 (guideline revision)](https://developer.apple.com/news/?id=3ozbk628) · [HIG: Ratings and reviews](https://developer.apple.com/design/human-interface-guidelines/ratings-and-reviews) · [Apple: Ratings, reviews, and responses](https://developer.apple.com/app-store/ratings-and-reviews/) · [App Store Connect Help: View ratings and reviews](https://developer.apple.com/help/app-store-connect/monitor-ratings-and-reviews/view-ratings-and-reviews) — checked 2026-09-30.
- **iOS field reports (developers, not Apple)** — [Apple Developer Forums thread 807408 (iOS 26.1 "Not Now" disabled)](https://developer.apple.com/forums/thread/807408) · [Apple Developer Forums thread 821981 (iOS 26.5 development builds)](https://developer.apple.com/forums/thread/821981) · [expo/expo #41116 (iOS 26 sheet)](https://github.com/expo/expo/issues/41116) · [larchwave/flowbaton #43 (iOS 26.2 simulator sheet)](https://github.com/larchwave/flowbaton/issues/43) · [Daring Fireball, 17 Apr 2026](https://daringfireball.net/linked/2026/04/17/apples-developer-guidelines-for-ratings-and-review-prompts) — checked 2026-09-30.
- **Google Play In-App Review** — [In-app reviews overview](https://developer.android.com/guide/playcore/in-app-review) · [Integrate in-app reviews (Kotlin or Java)](https://developer.android.com/guide/playcore/in-app-review/kotlin-java) · [Test in-app reviews](https://developer.android.com/guide/playcore/in-app-review/test) · [ReviewErrorCode reference](https://developer.android.com/reference/com/google/android/play/core/review/model/ReviewErrorCode) · [FakeReviewManager reference](https://developer.android.com/reference/com/google/android/play/core/review/testing/FakeReviewManager) · [com.google.android.play:review maven-metadata.xml](https://dl.google.com/android/maven2/com/google/android/play/review/maven-metadata.xml) · [com.google.android.play:review-ktx maven-metadata.xml](https://dl.google.com/android/maven2/com/google/android/play/review-ktx/maven-metadata.xml) · [Linking to Google Play](https://developer.android.com/distribute/marketing-tools/linking-to-google-play) — checked 2026-09-30.
- **Google Play policy, Play Console and GA4** — [Play Console Help: User Ratings, Reviews, and Installs](https://support.google.com/googleplay/android-developer/answer/9898684) · [Play Console Help: View and analyze your app's ratings and reviews](https://support.google.com/googleplay/android-developer/answer/138230) · [GA4 collection limits](https://support.google.com/analytics/answer/9267744) — checked 2026-09-30.
- **Review libraries (registry, tarballs, repositories)** — [react-native-in-app-review (npm registry JSON)](https://registry.npmjs.org/react-native-in-app-review) · [react-native-in-app-review 4.4.2 tarball](https://registry.npmjs.org/react-native-in-app-review/-/react-native-in-app-review-4.4.2.tgz) · [react-native-store-review (npm downloads API)](https://api.npmjs.org/downloads/point/last-week/react-native-store-review) · [oblador/react-native-store-review (GitHub API)](https://api.github.com/repos/oblador/react-native-store-review) · [oblador/react-native-store-review commits (GitHub API)](https://api.github.com/repos/oblador/react-native-store-review/commits) · [react-native-store-review 0.5.0 tarball](https://registry.npmjs.org/react-native-store-review/-/react-native-store-review-0.5.0.tgz) · [react-native-store-review README](https://github.com/oblador/react-native-store-review) · [react-native-rate-app (React Native Directory API)](https://reactnative.directory/api/libraries?search=react-native-rate-app) · [react-native-rate-app 2.1.3 tarball](https://registry.npmjs.org/react-native-rate-app/-/react-native-rate-app-2.1.3.tgz) · [huextrat/react-native-rate-app README](https://github.com/huextrat/react-native-rate-app) · [expo-store-review 57.0.3 tarball](https://registry.npmjs.org/expo-store-review/-/expo-store-review-57.0.3.tgz) · [expo-store-review CHANGELOG](https://github.com/expo/expo/blob/main/packages/expo-store-review/CHANGELOG.md) — checked 2026-09-30.
- **React Native docs** — [React Native docs: Share](https://reactnative.dev/docs/share) · [React Native docs: Linking](https://reactnative.dev/docs/linking) — checked 2026-09-30.
- **Prompt-timing studies (single apps, self-reported)** — [Phiture: Unlocking the data behind the iOS Rating Prompt (2019)](https://phiture.com/asostack/unlocking-the-data-behind-the-ios-rating-prompt-8e942bfe9134/) · [Appbot: You aren't prompting for app ratings and reviews often enough (2023)](https://appbot.co/blog/app-ratings-reviews-strategy-experiment/) · [Appbot: When to Ask for App Ratings (2025)](https://appbot.co/blog/prompting-for-ratings-prompt-early-or-wait/) · [Jake Lee: Rapidly improving Play Store rating with an Android in-app review prompt (2024)](https://blog.jakelee.co.uk/play-store-rating-prompt/) — checked 2026-09-30.
- **DZZLO's own listings** — [iTunes lookup, India storefront](https://itunes.apple.com/lookup?id=1553062924&country=in) · [DZZLO OMS on Google Play (en_IN)](https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms&hl=en_IN&gl=IN) — checked 2026-09-30.
---

← [[10-capstones]] · [[00_README]]
