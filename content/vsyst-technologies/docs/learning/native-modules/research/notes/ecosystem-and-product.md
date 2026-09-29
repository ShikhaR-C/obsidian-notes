# React Native device-capability ecosystem (bare RN 0.84, New Architecture) and product value for DZZLO OMS — as of 29 Sep 2026

## 1. For each device capability, which library is the 2026 default for a bare RN 0.84 New-Architecture app, is it healthy, and where is the ecosystem thin enough to build in-house?

### Takeaway
Most capabilities have a healthy New-Architecture library in 2026: TurboModule (codegen), Nitro or Expo-module builds with releases in the last three months. The thin spots are Android 16 Live Updates, iOS Live Activity and WidgetKit UI (Swift is always needed somewhere), App Intents and AppFunctions, Bluetooth ESC/POS printing, system print dialogs, a permission-free contact picker, app-group shared storage and true background upload. Several once-default libraries are now dead: notifee (archived 7 Apr 2026), react-native-fs, react-native-print, react-native-background-upload, react-native-geolocation-service, @react-native-community/geolocation, react-native-quick-actions, react-native-siri-shortcut and react-native-encrypted-storage.

### Cited Findings

**Method and data provenance**
- All version, date, download and issue figures below were pulled on 2026-09-29:
  - npm registry: latest version and date, the count of stable, non-prerelease versions published since 2025-09-29 ("rel/12 mo"), and whether the package ships `codegenConfig` (a TurboModule/Fabric spec).
  - api.npmjs.org "last-week" downloads.
  - GitHub GraphQL: open issues, open PRs, archived flag, last push.
  - reactnative.directory API: `newArchitecture` and `unmaintained` flags.
  - Sources: [npm registry](https://registry.npmjs.org/), [npm downloads API](https://api.npmjs.org/downloads/point/last-week/react-native-share), [React Native Directory](https://reactnative.directory/).
- Expo packages all live in the expo/expo monorepo (286 open issues and 552 open PRs repo-wide on 2026-09-29), so issue counts are not per package — [expo/expo](https://github.com/expo/expo).
- Legend for the tables:
  - **Arch:** TM = ships codegenConfig (TurboModule/Fabric); Nitro = Nitro module (New-Arch only); Expo = Expo module (needs `expo` installed); Old = no codegen and not flagged New-Arch.
  - **Health:** A = release within 3 months; S = 3–12 months; St = more than 12 months; U = flagged unmaintained, deprecated or archived.

**A1. Camera, scanning, OCR**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Open issues / PRs | Health, notes | Source |
|---|---|---|---|---|---|---|---|
| react-native-vision-camera | 5.2.3 (2026-08-20) | Nitro; directory "new-arch-only" | 629,223 | 19 | 25 / 69 | A; 9.6k stars | [npm](https://www.npmjs.com/package/react-native-vision-camera), [GitHub](https://github.com/margelo/react-native-vision-camera) |
| react-native-vision-camera-barcode-scanner | 5.2.3 (2026-08-20) | Nitro (peers: nitro-modules, nitro-image) | 48,384 | 18 | monorepo | A; "Barcode scanning plugin ... powered by ML Kit" | [npm](https://www.npmjs.com/package/react-native-vision-camera-barcode-scanner), [VisionCamera docs](https://visioncamera.margelo.com/docs/barcode-scanner) |
| react-native-nitro-zxing | 0.1.0-alpha.0 (2026-08-26) | Nitro | 1,390 | 0 | — | alpha; zxing-cpp alternative to ML Kit | [GitHub](https://github.com/margelo/react-native-nitro-zxing) |
| expo-camera | 57.0.6 (2026-09-29) | Expo | 2,474,110 | 48 | monorepo | A | [npm](https://www.npmjs.com/package/expo-camera) |
| react-native-camera-kit | 18.0.1 (2026-08-03) | TM | 74,751 | 7 | 83 / 29 | A; teslamotors | [GitHub](https://github.com/teslamotors/react-native-camera-kit) |
| react-native-document-scanner-plugin | 2.0.4 (2026-01-02) | TM | 98,850 | 4 | 47 / 4 | S; Android depends on `play-services-mlkit-document-scanner:16.0.0`; README says Android needs no camera-permission prompt | [GitHub](https://github.com/WebsiteBeaver/react-native-document-scanner-plugin) |
| @infinitered/react-native-mlkit-document-scanner | 5.0.0 (2025-11-17) | — | 473 | 2 | 17 / 2 | S; low adoption | [GitHub](https://github.com/infinitered/react-native-mlkit) |
| @react-native-ml-kit/text-recognition | 2.0.0 (2025-09-01) | Old | 57,534 | 0 | 19 / 7 | St (no release in 12 months) | [GitHub](https://github.com/a7medev/react-native-ml-kit) |
| @react-native-ml-kit/barcode-scanning | 2.0.0 (2025-09-01) | Old | 4,677 | 0 | same repo | St | [npm](https://www.npmjs.com/package/@react-native-ml-kit/barcode-scanning) |
| expo-text-extractor | 2.0.0 (2026-02-28) | Expo (community) | 13,548 | 2 | 3 / 15 | S | [GitHub](https://github.com/pchalupa/expo-text-extractor) |
| react-native-vision-camera-ocr-plus | 2.0.6 (2026-08-20) | frame-processor plugin | 10,007 | 27 | 0 / 3 | A; small (72 stars) | [GitHub](https://github.com/jamenamcinteer/react-native-vision-camera-ocr-plus) |

- VisionCamera V5 is built on Nitro Modules and Nitro Image. Barcode scanning needs a second package, `react-native-vision-camera-barcode-scanner` (ML Kit), which provides `useCodeScanner` and a `<CodeScanner />` view — [Margelo blog](https://margelo.com/blog/react-native-qr-barcode-scanner-visioncamera-v5), [VisionCamera docs](https://visioncamera.margelo.com/docs/barcode-scanner).

**A2. Image picking, compression, EXIF**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Open issues / PRs | Health, notes | Source |
|---|---|---|---|---|---|---|---|
| react-native-image-picker | 8.2.1 (2025-05-04) | TM | 515,089 | 0 | 306 / 44 | St: no release for 16 months (repo push 2026-03-17) | [GitHub](https://github.com/react-native-image-picker/react-native-image-picker) |
| expo-image-picker | 57.0.20 (2026-09-24) | Expo | 4,923,829 | 85 | monorepo | A | [npm](https://www.npmjs.com/package/expo-image-picker) |
| react-native-image-crop-picker | 0.52.0 (2026-09-29) | TM | 242,043 | 2 | 555 / 96 | A release, very large backlog | [GitHub](https://github.com/ivpusic/react-native-image-crop-picker) |
| @baronha/react-native-multiple-image-picker | 2.2.5 (2025-12-10) | Nitro | 4,166 | 1 | 39 / 4 | S | [GitHub](https://github.com/NitrogenZLab/react-native-multiple-image-picker) |
| @bam.tech/react-native-image-resizer | 3.0.11 (2024-11-25) | TM | 110,298 | 0 | 1 / 3 | St release, but repo active (push 2026-09-26) with almost no backlog | [GitHub](https://github.com/bamlab/react-native-image-resizer) |
| react-native-image-resizer | 1.4.5 (2021-06-16) | — | 40,308 | 0 | — | U: npm deprecation says it "has moved to @bam.tech/react-native-image-resizer" | [npm](https://www.npmjs.com/package/react-native-image-resizer) |
| react-native-compressor | 2.0.3 (2026-07-25) | Nitro | 215,425 | 17 | 23 / 6 | A | [GitHub](https://github.com/numandev1/react-native-compressor) |
| expo-image-manipulator | 57.0.20 (2026-09-24) | Expo | 2,523,139 | 82 | monorepo | A | [npm](https://www.npmjs.com/package/expo-image-manipulator) |
| @lodev09/react-native-exify | 1.0.3 (2026-02-22) | TM | 35,186 | 4 | 1 / 0 | S; small (59 stars) | [GitHub](https://github.com/lodev09/react-native-exify) |

**A3. Files, PDF, printing, sharing, background transfer**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Open issues / PRs | Health, notes | Source |
|---|---|---|---|---|---|---|---|
| @react-native-documents/picker | 12.0.2 (2026-07-28) | TM | 344,187 | 8 | 8 / 13 | A | [GitHub](https://github.com/react-native-documents/document-picker) |
| @react-native-documents/viewer | 4.0.1 (2026-07-28) | TM | 35,395 | 8 | same repo | A | [npm](https://www.npmjs.com/package/@react-native-documents/viewer) |
| react-native-document-picker | 9.3.1 (2024-08-22) | — | 169,471 | 0 | — | U: npm deprecation says "the package was renamed" | [npm](https://www.npmjs.com/package/react-native-document-picker) |
| expo-document-picker | 57.0.3 (2026-09-29) | Expo | 2,925,880 | 32 | monorepo | A | [npm](https://www.npmjs.com/package/expo-document-picker) |
| react-native-fs | 2.20.0 (2022-05-04) | Old | 524,253 | 0 | 559 / 71 | U (directory flag) | [GitHub](https://github.com/itinance/react-native-fs) |
| @dr.pogodin/react-native-fs | 2.40.3 (2026-09-12) | TM | 60,524 | 14 | 27 / 1 | A; maintained fork | [GitHub](https://github.com/birdofpreyru/react-native-fs) |
| react-native-file-access | 4.0.4 (2026-09-18) | TM | 44,518 | 5 | 11 / 0 | A | [GitHub](https://github.com/alpha0010/react-native-file-access) |
| expo-file-system | 57.0.7 (2026-09-11) | Expo | 10,549,669 | 61 | monorepo | A | [npm](https://www.npmjs.com/package/expo-file-system) |
| react-native-blob-util | 0.25.1 (2026-09-24) | TM | 957,905 | 16 | 89 / 1 | A | [GitHub](https://github.com/RonRadtke/react-native-blob-util) |
| react-native-background-upload | 6.6.0 (2022-10-07) | Old; directory newArchitecture=false | 7,594 | 0 | 125 / 11 | U | [GitHub](https://github.com/Vydia/react-native-background-upload) |
| @kesha-antonov/react-native-background-downloader | 4.6.3 (2026-09-15) | TM | 20,644 | 26 | 0 / 1 | A | [GitHub](https://github.com/kesha-antonov/react-native-background-downloader) |
| expo-background-task | 57.0.21 (2026-09-29) | Expo | 398,236 | 86 | monorepo | A | [npm](https://www.npmjs.com/package/expo-background-task) |
| react-native-background-fetch | 4.4.2 (2026-04-15) | TM | 86,799 | 5 | 0 / 1 | S; Transistorsoft | [GitHub](https://github.com/transistorsoft/react-native-background-fetch) |
| react-native-share | 12.3.1 (2026-05-04) | TM | 740,975 | 8 | 3 / 9 | S (repo push 2026-08-31) | [GitHub](https://github.com/react-native-share/react-native-share) |
| expo-sharing | 57.0.22 (2026-09-24) | Expo | 2,808,118 | 88 | monorepo | A | [npm](https://www.npmjs.com/package/expo-sharing) |
| react-native-view-shot | 6.0.1 (2026-09-20) | TM | 1,234,169 | 6 | 8 / 5 | A (renders a view to an image, e.g. for sharing a summary) | [GitHub](https://github.com/gre/react-native-view-shot) |
| react-native-html-to-pdf (in DZZLO today) | 1.3.0 (2025-09-04) | TM | 47,865 | 0 | 7 / 3 | S/St boundary: no release in 12 months (repo push 2026-01-29) | [GitHub](https://github.com/christopherdro/react-native-html-to-pdf) |
| react-native-print | 0.11.0 (2023-01-22) | Old | 14,616 | 0 | 2 / 5 | U (directory flag) | [GitHub](https://github.com/christopherdro/react-native-print) |
| expo-print | 57.0.2 (2026-09-11) | Expo | 687,652 | 33 | monorepo | A | [npm](https://www.npmjs.com/package/expo-print) |
| react-native-pdf (viewer) | 7.0.5 (2026-08-13) | TM | 686,370 | 6 | 383 / 3 | A release, very large backlog | [GitHub](https://github.com/wonday/react-native-pdf) |
| react-native-pdf-renderer | 2.3.0 (2025-08-12) | TM | 45,065 | 0 | 4 / 2 | St | [GitHub](https://github.com/douglasjunior/react-native-pdf-renderer) |
| pdf-lib (pure JS) | 1.17.1 (2021-11-06) | JS | 16,663,989 (mostly web/Node) | 0 | 278 / 39 | St | [GitHub](https://github.com/Hopding/pdf-lib) |

**A4. Maps and location**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Open issues / PRs | Health, notes | Source |
|---|---|---|---|---|---|---|---|
| react-native-maps | 1.29.11 (2026-09-27) | TM; directory New-Arch true | 1,305,122 | 28 | 51 / 34 | A; 16k stars | [GitHub](https://github.com/react-native-maps/react-native-maps) |
| @maplibre/maplibre-react-native | 11.4.0 (2026-09-19) | TM | 184,149 | 25 | 25 / 14 | A | [GitHub](https://github.com/maplibre/maplibre-react-native) |
| @rnmapbox/maps | 10.3.5 (2026-07-22) | TM | 257,311 | 15 | 102 / 58 | A | [GitHub](https://github.com/rnmapbox/maps) |
| expo-maps | 57.0.3 (2026-09-11) | Expo | 141,042 | 43 | monorepo | A | [npm](https://www.npmjs.com/package/expo-maps) |
| @react-native-community/geolocation | 3.4.0 (2024-09-01) | TM | 245,296 | 0 | 150 / 20 | U (directory flag) | [GitHub](https://github.com/michalchudziak/react-native-geolocation) |
| react-native-geolocation-service | 5.3.1 (2022-09-23) | Old | 129,015 | 0 | 115 / 17 | U | [GitHub](https://github.com/Agontuk/react-native-geolocation-service) |
| expo-location | 57.0.20 (2026-09-24) | Expo | 2,628,991 | 82 | monorepo | A | [npm](https://www.npmjs.com/package/expo-location) |
| react-native-background-geolocation | 5.7.0 (2026-09-27) | TM | 66,554 | 18 | 20 / 7 | A; Transistorsoft (licence terms not checked) | [GitHub](https://github.com/transistorsoft/react-native-background-geolocation) |

**A5. Push, local notifications, in-app messaging, Live Activities / Live Updates, widgets**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Open issues / PRs | Health, notes | Source |
|---|---|---|---|---|---|---|---|
| react-native-onesignal (in DZZLO today) | 5.5.14 (2026-09-23) | TM | 186,618 | 34 | 15 / 3 | A; README: RN ≥ 0.79 needed for 5.4.x and later (TurboModule registration via `codegenConfig.ios.modulesProvider`) | [GitHub](https://github.com/OneSignal/react-native-onesignal) |
| @notifee/react-native | 9.1.8 (2024-12-20) | Old | 423,776 | 0 | 24 / 5 | U: repo archived; README says "Notifee is no longer actively maintained" and recommends expo-notifications or react-native-notify-kit | [GitHub](https://github.com/invertase/notifee) |
| react-native-notify-kit | 10.8.0 (2026-09-29) | TM, New-Arch only | 46,379 | 46 | 0 open; 214 stars; repo created 2026-03-30 | A. Claims 100% API compatibility with @notifee/react-native, "TurboModules only — no legacy Bridge support", and that Invertase officially archived Notifee on 7 Apr 2026 | [GitHub](https://github.com/marcocrupi/react-native-notify-kit) |
| expo-notifications | 57.0.21 (2026-09-24) | Expo | 5,172,792 | 94 | monorepo | A | [npm](https://www.npmjs.com/package/expo-notifications) |
| @react-native-firebase/messaging | 26.4.0 (2026-09-05) | TM | 993,198 | 26 | 24 / 20 (monorepo) | A | [GitHub](https://github.com/invertase/react-native-firebase) |
| @react-native-firebase/in-app-messaging | 26.4.0 (2026-09-05) | TM | 33,687 | 26 | same | A | [npm](https://www.npmjs.com/package/@react-native-firebase/in-app-messaging) |
| react-native-notifications (Wix) | 5.2.2 (2025-11-16) | Old | 47,664 | 3 | 3 / 6 | S | [GitHub](https://github.com/wix/react-native-notifications) |
| expo-live-activity | 0.4.2 (2025-11-18) | Expo | 20,336 | 2 | archived | U: npm "Package no longer supported"; README "This library is deprecated. Consider other solutions like expo-widgets" | [GitHub](https://github.com/software-mansion-labs/expo-live-activity) |
| voltra (Callstack) | 2.3.2 (2026-09-22) | TM clients (`@use-voltra/android-client` 32,925/wk, `@use-voltra/ios-client` 20,132/wk) | 18,477 | 18 | 35 / 5 | A; 834 stars | [GitHub](https://github.com/callstackincubator/voltra) |
| expo-widgets | 57.0.22 (2026-09-29) | Expo; iOS only | 376,047 | 82 | monorepo | A | [Expo docs](https://docs.expo.dev/versions/latest/sdk/widgets/) |
| react-native-widget-extension | 0.3.0 (2026-05-25) | config plugin | 17,024 | 2 | 3 / 2 | S | [GitHub](https://github.com/bndkt/react-native-widget-extension) |
| @bacons/apple-targets | 5.0.0 (2026-07-17) | config plugin for Xcode targets | 568,297 | 14 | 48 / 25 | A | [GitHub](https://github.com/EvanBacon/expo-apple-targets) |
| react-native-android-widget | 0.22.1 (2026-08-17) | directory New-Arch true | 78,064 | 11 | 2 / 0 | A | [GitHub](https://github.com/sAleksovski/react-native-android-widget) |
| react-native-shared-group-preferences | 1.1.24 (2023-09-18) | Old | 22,690 | 0 | 10 / 6 | U | [GitHub](https://github.com/KjellConnelly/react-native-shared-group-preferences) |

- **expo-widgets:**
  - iOS only: home-screen widgets, Lock Screen widgets, Live Activities with Dynamic Island, and interactive widgets. Android widgets are not supported.
  - Works in bare RN once `expo` is installed.
  - Supports APNs push updates, and push-to-start on iOS 17.2+.
  - Limitation (quoted): "Code inside a 'widget'-marked component runs in an isolated runtime and can only use @expo/ui/swift-ui components, with no React hooks, app state, or asynchronous work."
  - Source: [Expo docs](https://docs.expo.dev/versions/latest/sdk/widgets/).
- **Voltra:**
  - "turns React Native JSX into SwiftUI and Jetpack Compose Glance" for iOS Live Activities, Dynamic Island, iOS widgets and Android home-screen widgets.
  - Supports ActivityKit push tokens (iOS) and FCM (Android).
  - Claims compatibility with Expo Dev Client and bare RN, with config plugins wiring the extension targets.
  - Its docs cover Android "ongoing notifications" with `ProgressStyle` on API 36.
  - Sources: [README](https://github.com/callstackincubator/voltra), [iOS docs tree](https://github.com/callstackincubator/voltra/tree/main/website/docs/v1/ios), [Android ongoing-notification docs](https://github.com/callstackincubator/voltra/blob/main/website/docs/v1/android/development/managing-ongoing-notifications.md).
- **Voltra's Android 16 Live Updates work is merged but unreleased.**
  - ADR 0008 is "Accepted" and covers promotion requests, the status-bar chip, eligibility/error codes and MetricStyle (API 37, "compileSdk 37 floor") — [ADR 0008](https://github.com/callstackincubator/voltra/blob/main/docs/adr/0008-android-ongoing-notification-live-updates-api.md).
  - The implementing PRs #325 and #326 merged on 2026-09-28, after the latest release v2.3.2 (2026-09-22) — [PR #325](https://github.com/callstackincubator/voltra/pull/325), [PR #326](https://github.com/callstackincubator/voltra/pull/326).
- **Contradiction:** the freeCodeCamp "React Native Live Activities Handbook" (Farouq Seriki, 14 Jul 2026) says no third-party library supports Android 16 Live Updates, so a custom Kotlin module is required. It also recommends a custom module over expo-live-activity or Notifee for iOS — [freeCodeCamp](https://www.freecodecamp.org/news/react-native-live-activities-handbook/). Voltra's merges came after that article.
- **Android Live Update requirements** (all quoted from the docs):
  - Permission: the manifest must declare `android.permission.POST_PROMOTED_NOTIFICATIONS`.
  - Style: must be Standard, BigTextStyle, CallStyle, ProgressStyle or MetricStyle.
  - Must be `ongoing`, must have a `contentTitle`, and must request promotion (`setRequestPromotedOngoing(true)`).
  - Must have no custom RemoteViews, must not be colorized, and the channel must not be IMPORTANCE_MIN.
  - They appear "at the top of the notification drawer and the lock screen, and as a chip in the status bar".
  - Appropriate uses include "active food delivery tracking"; inappropriate uses include "Ads, promotions, chat messages, alerts".
  - Source: [Android Developers](https://developer.android.com/develop/ui/views/notifications/live-update).
- **iOS ActivityKit constraints:** 4 KB payload; the system budgets frequent updates (`NSSupportsLiveActivitiesFrequentUpdates`); iOS 16.1 for the Lock Screen and 16.2 for Dynamic Island; push-to-start on iOS 17.2+; a SwiftUI widget extension target is required — [freeCodeCamp](https://www.freecodecamp.org/news/react-native-live-activities-handbook/).
- **OneSignal Live Activities:**
  - `setupDefault` lets the SDK own the ActivityKit lifecycle for its built-in `DefaultLiveActivityAttributes`, "so the only native code you write is the widget layout".
  - `startDefault` starts an activity in-app.
  - Requires react-native-onesignal 5.2.0 or later.
  - OneSignal in-app messages "do not require any code".
  - Sources: [OneSignal cross-platform Live Activity setup](https://documentation.onesignal.com/docs/en/cross-platform-live-activity-setup), [OneSignal Live Activities](https://documentation.onesignal.com/docs/en/live-activities).
- **react-native-android-widget:**
  - "We cannot render React Native views directly to the widget ... [it] render[s] the React Native views to an image", so it must know the exact widget size, and some launchers misreport it.
  - Updates come via `updatePeriodMillis`, on-demand update requests, or clicks.
  - Sources: [limitations](https://github.com/sAleksovski/react-native-android-widget/blob/master/docs/docs/limitations.md), [update docs](https://github.com/sAleksovski/react-native-android-widget/blob/master/docs/docs/update-widget.md).

**A6. Shortcuts, intents, App Clips / instant experiences**

| Library or platform | Latest (date) | Arch | Weekly DL | Health, notes | Source |
|---|---|---|---|---|---|
| react-native-siri-shortcut | 3.2.4 (2023-12-13) | Old | 2,895 | U | [GitHub](https://github.com/Gustash/react-native-siri-shortcut) |
| expo-app-intents | 0.0.1 (2026-06-08) | unknown | 6,538 | npm metadata has no description or repository — provenance unverified | [npm](https://www.npmjs.com/package/expo-app-intents) |
| expo-quick-actions | 6.0.2 (2026-05-27) | Expo | 235,338 | S; covers iOS and Android; "Both Apple and Android recommend a max of 4 items" | [GitHub](https://github.com/EvanBacon/expo-quick-actions) |
| react-native-quick-actions | 0.3.13 (2019-11-24) | Old, archived | 19,552 | U | [GitHub](https://github.com/jordanbyron/react-native-quick-actions) |
| react-native-app-clip | 0.9.1 (2026-06-12) | Expo config plugin | 25,132 | S; "Expo Config Plugin that generates an App Clip for iOS apps built with Expo"; setup runs `npx expo prebuild`; App Clip size limits depend on the deployment target | [GitHub](https://github.com/bndkt/react-native-app-clip) |

- **App Intents:** modern Siri Shortcuts are built with App Intents and "live in native Swift, not JavaScript", so an RN app needs a small native layer — [vp0 blog](https://vp0.com/blogs/siri-shortcuts-integration-react-native-ai), [Medium (sudoplz)](https://medium.com/@sudoplz/ios-app-shortcuts-intents-on-a-react-native-project-to-enable-voice-commands-with-siri-and-95fa9fc29a34).
- **AppFunctions** is an Android 16 platform feature plus a Jetpack library. It lets apps expose functions to agents such as Gemini, described as "the mobile equivalent of tools within the Model Context Protocol" — [Android Developers](https://developer.android.com/ai/appfunctions), [9to5Google, 25 Feb 2026](https://9to5google.com/2026/02/25/android-appfunctions-gemini/).
  - A search summary says Gemini integration was still a private preview with trusted testers as of May 2026 (secondary; not verified on a primary page).
  - No dedicated RN library was found — [search result: example PR](https://github.com/colonelpanic8/mova/pull/13).
- **Google Play Instant is gone.** Google shut down Android Instant Apps in December 2025: publishing and all Play Instant APIs stopped working, and Google points developers to deep links into the regular app — [Android Police](https://www.androidpolice.com/rip-android-instant-apps/), [Android Authority](https://www.androidauthority.com/google-killing-android-instant-apps-3567211/).

**A7. Biometrics, passkeys, secure storage**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Open issues / PRs | Health, notes | Source |
|---|---|---|---|---|---|---|---|
| react-native-biometrics | 3.0.1 (2022-09-06) | Old | 114,114 | 0 | 115 / 12 | St | [GitHub](https://github.com/SelfLender/react-native-biometrics) |
| @sbaiahmed1/react-native-biometrics | 0.16.1 (2026-09-08) | TM | 23,081 | 20 | 2 / 2 | A; small (121 stars) | [GitHub](https://github.com/sbaiahmed1/react-native-biometrics) |
| expo-local-authentication | 57.0.3 (2026-09-11) | Expo | 1,560,310 | 33 | monorepo | A | [npm](https://www.npmjs.com/package/expo-local-authentication) |
| react-native-keychain | 10.0.0 (2025-03-23) | TM | 553,883 | 0 | 166 / 28 | S/St: no release for 18 months (push 2026-04-29) | [GitHub](https://github.com/oblador/react-native-keychain) |
| expo-secure-store | 57.0.4 (2026-09-11) | Expo | 6,896,565 | 32 | monorepo | A | [npm](https://www.npmjs.com/package/expo-secure-store) |
| react-native-mmkv | 4.3.2 (2026-06-22) | Nitro | 1,645,230 | 9 | 4 / 17 | A | [GitHub](https://github.com/margelo/react-native-mmkv) |
| react-native-sensitive-info | 6.1.5 (2026-06-30) | Nitro | 24,110 | 10 | 0 / 25 | A | [GitHub](https://github.com/mCodex/react-native-sensitive-info) |
| react-native-encrypted-storage | 4.0.3 (2022-11-03) | Old, archived | 56,148 | 0 | 28 / 12 | U | [GitHub](https://github.com/emeraldsanto/react-native-encrypted-storage) |
| react-native-passkey | 3.6.2 (2026-09-08) | directory New-Arch true | 135,277 | 10 | 3 / 3 | A | [GitHub](https://github.com/f-23/react-native-passkey) |
| react-native-passkeys | 0.4.2 (2026-08-05) | — | 171,717 | 3 | 12 / 11 | A | [GitHub](https://github.com/peterferguson/react-native-passkeys) |
| react-native-credentials-manager | 0.9.0 (2026-09-17) | TM; Android only | 3,552 | 4 | — | A | [GitHub](https://github.com/benjamineruvieru/react-native-credentials-manager) |

**A8. OTA:** covered in section 3.

**A9. Bluetooth thermal printers**

| Library | Latest (date) | Arch | Weekly DL | Rel/12 mo | Health, notes | Source |
|---|---|---|---|---|---|---|
| react-native-thermal-receipt-printer | 1.2.0-rc.2 (2023-12-06) | Old | 1,248 | 0 | U-like; 80 open issues | [GitHub](https://github.com/HeligPfleigh/react-native-thermal-receipt-printer) |
| react-native-thermal-receipt-printer-image-qr | 0.1.12 (2024-09-16) | Old | 1,206 | 0 | St; 80 open issues | [GitHub](https://github.com/thiendangit/react-native-thermal-receipt-printer-image-qr) |
| react-native-bluetooth-escpos-printer | 0.0.5 (2019-01-05) | Old | 820 | 0 | U | [npm](https://www.npmjs.com/package/react-native-bluetooth-escpos-printer) |
| @haroldtran/react-native-thermal-printer | 1.2.0 (2026-03-04) | — | 613 | 16 | S; 20 stars | [GitHub](https://github.com/phattran1201/react-native-thermal-printer) |
| react-native-esc-pos-printer (Epson ePOS) | 4.5.0 (2025-10-24) | TM | 10,880 | 1 | S; Epson hardware | [GitHub](https://github.com/tr3v3r/react-native-esc-pos-printer) |
| react-native-star-io10 (Star Micronics, official) | 1.14.0 (2026-09-15) | Old | 36,984 | 7 | A; Star hardware | [GitHub](https://github.com/star-micronics/react-native-star-io10) |
| react-native-ble-manager | 12.5.3 (2026-09-21) | TM | 106,253 | 16 | A; generic BLE | [GitHub](https://github.com/innoveit/react-native-ble-manager) |
| react-native-ble-plx | 3.5.1 (2026-02-18) | directory New-Arch true | 212,217 | 1 | S; generic BLE | [GitHub](https://github.com/dotintent/react-native-ble-plx) |
| react-native-bluetooth-classic | 1.73.0-rc.17 (2025-11-19) | Old | 19,552 | 0 | S (RCs only) | [GitHub](https://github.com/kenjdavidson/react-native-bluetooth-classic) |

- "iOS doesn't let apps use Bluetooth Classic SPP unless the accessory is MFi certified, and cheap printers aren't." Android uses Classic SPP/RFCOMM while iOS uses BLE GATT, so a Classic-only printer "will never show up in an iOS scan"; dual-mode printers work on both — [expo-thermal-printer README (search summary)](https://github.com/Ricka7x/expo-thermal-printer).
- Star Micronics Bluetooth receipt printers are "dual chip Apple MFi certified" — [Star Micronics](https://starmicronics.com/bluetooth-receipt-printers-pos-thermal-impact-portable/).

**A10. Contacts, OTP autofill, UPI, clipboard, haptics, permissions, storage**

| Library | Latest (date) | Arch | Weekly DL | Health, notes | Source |
|---|---|---|---|---|---|
| react-native-contacts | 8.0.10 (2026-01-28) | TM | 103,716 | S; full address-book access | [GitHub](https://github.com/morenoh149/react-native-contacts) |
| expo-contacts | 57.0.6 (2026-09-18) | Expo | 612,750 | A | [npm](https://www.npmjs.com/package/expo-contacts) |
| react-native-select-contact | 1.6.3 (2021-06-04) | Old | 16,813 | U | [GitHub](https://github.com/streem/react-native-select-contact) |
| react-native-contact-picker (iOS CNContactPicker wrapper) | 0.0.5 (2017-09-28) | Old | 106 | U | [npm](https://www.npmjs.com/package/react-native-contact-picker) |
| react-native-otp-verify | 1.2.0 (2026-04-03) | directory newArchitecture=false | 36,917 | S; not New-Arch | [GitHub](https://github.com/faizalshap/react-native-otp-verify) |
| @pushpendersingh/react-native-otp-verify | 1.2.0 (2025-10-15) | TM | 5,954 | S; "Zero-permission SMS verification using Google's SMS Retriever API" | [GitHub](https://github.com/pushpender-singh-ap/react-native-otp-verify) |
| react-native-sms-retriever | 1.1.1 (2020-01-02) | Old | 17,276 | U | [npm](https://www.npmjs.com/package/react-native-sms-retriever) |
| react-native-upi-payment | 1.0.5 (2023-10-02) | Old | 38 | U | [npm](https://www.npmjs.com/package/react-native-upi-payment) |
| @react-native-clipboard/clipboard | 1.16.3 (2025-06-28) | TM | 904,899 | St (73 open issues) | [GitHub](https://github.com/react-native-clipboard/clipboard) |
| expo-clipboard | 57.0.2 (2026-09-11) | Expo | 3,561,904 | A | [npm](https://www.npmjs.com/package/expo-clipboard) |
| react-native-haptic-feedback | 3.0.0 (2026-03-29) | TM | 525,257 | S | [GitHub](https://github.com/mkuczera/react-native-haptic-feedback) |
| expo-haptics | 57.0.3 (2026-09-11) | Expo | 4,727,766 | A | [npm](https://www.npmjs.com/package/expo-haptics) |
| react-native-permissions | 5.6.2 (2026-09-14) | TM | 801,263 | A; 6 open issues | [GitHub](https://github.com/zoontek/react-native-permissions) |
| react-native-signature-canvas | 5.1.1 (2026-08-06) | — | 221,366 | A; 82 open issues (proof-of-delivery signatures) | [GitHub](https://github.com/YanYuanFE/react-native-signature-canvas) |
| react-native-nitro-modules | 0.37.1 (2026-08-27) | Nitro runtime | 2,009,523 | A; 50 releases in 12 months | [GitHub](https://github.com/margelo/nitro) |
| @op-engineering/op-sqlite | 18.2.5 (2026-09-20) | TM | 840,046 | A; offline store | [GitHub](https://github.com/OP-Engineering/op-sqlite) |
| expo-sqlite | 57.0.3 (2026-09-11) | Expo | 1,478,651 | A | [npm](https://www.npmjs.com/package/expo-sqlite) |
| @nozbe/watermelondb | 0.28.0 (2025-04-07) | Old | 78,512 | St | [GitHub](https://github.com/Nozbe/WatermelonDB) |

- **Android 17 Contact Picker** (API 37, `Intent.ACTION_PICK_CONTACTS`):
  - Users share only the contacts, and only the fields, they choose.
  - The app gets a temporary session URI.
  - Multi-select is supported.
  - Legacy `ACTION_PICK` intents for contact data are auto-upgraded on Android 17+.
  - Sources: [Android Developers](https://developer.android.com/about/versions/17/features/contact-picker), [Android Developers Blog, Mar 2026](https://android-developers.googleblog.com/2026/03/contact-picker-privacy-first-contact.html).
- **iOS OTP autofill from email:** iOS 17+ autofills one-time codes received in Mail. Apps opt in with `textContentType(.oneTimeCode)` — [Apple Support](https://support.apple.com/guide/iphone/automatically-fill-in-verification-codes-ipha6173c19f/ios), [Cult of Mac](https://www.cultofmac.com/news/ios-17-autofill-verification-codes-safari-mail-app).
- **expo-background-task** uses WorkManager (Android) and BGTaskScheduler (iOS):
  - 15-minute minimum interval on Android.
  - Timing "is not guaranteed".
  - Unavailable on iOS simulators.
  - Tasks stop if the user kills the app.
  - Source: [Expo docs](https://docs.expo.dev/versions/latest/sdk/background-task/).
- **Google Play background location:** apps that access location in the background must be approved through the Play Console permission declaration. Apps targeting Android 14 that use a location foreground service must declare `FOREGROUND_SERVICE_LOCATION` — [Play Console Help](https://support.google.com/googleplay/android-developer/answer/9799150?hl=en), [Play Console Help (FGS)](https://support.google.com/googleplay/android-developer/answer/13392821?hl=en).
- **State of React Native 2025** (3,501 responses; survey ran 9 Dec 2025 – 8 Jan 2026), platform-API usage:

  | API | Share of respondents |
  |---|---|
  | Camera | 69.65% |
  | Push notifications | 66.37% |
  | File system | 57.65% |
  | Location | 47.37% |
  | Maps | 41.04% |
  | Background processing | 31.99% |
  | Local authentication | 29.93% |
  | Live Activities | 11.92% |

  Sources: [State of RN 2025 platform APIs](https://results.stateofreactnative.com/en-US/platform-apis/), [overview](https://results.stateofreactnative.com/en-US/).

### Inferences
Recommendation matrix. Every row covers iOS and Android unless noted. "Own-build cost" figures are opinion, for a JS-first team writing test-first; they include a Jest mock and a codegen spec.

| Capability | 2026 default for DZZLO (bare RN 0.84.1, New Arch) | Verdict | Platform coverage | Why / own-build cost |
|---|---|---|---|---|
| Photo capture of DU slips, meter readings, cheques | react-native-document-scanner-plugin for paper (VisionKit / ML Kit), react-native-image-picker camera mode for plain photos | USE | both | Edge detection plus crop comes for free. Building a scanner is weeks of work; the plugin's Android side needs no camera permission. |
| Custom live camera UI | react-native-vision-camera 5 | USE (only when needed) | both | Healthy and New-Arch-only. Pulls in Nitro plus nitro-image. |
| Barcode / QR (GST IRN QR, UPI QR) | vision-camera 5 + react-native-vision-camera-barcode-scanner (ML Kit) | USE | both | Avoid the stale @react-native-ml-kit/*. Verify IRN signatures server-side (section 7). |
| OCR | none in v1 | SKIP now, WRAP later | both | Accuracy on thermal-printed or handwritten Indian slips is unproven (gap). The OCR plugin ecosystem is small (≤60k/wk). |
| Image picking | react-native-image-picker 8.2.1 | USE, watch | both | TurboModule with 515k/wk, but no release for 16 months. Switch to expo-image-picker if Expo modules are adopted (section 2). |
| Compression / EXIF | @bam.tech/react-native-image-resizer; skip EXIF | USE / SKIP | both | Stamp time and place in the app at capture instead of reading EXIF. @lodev09/react-native-exify if EXIF is ever needed. |
| File pick / save / open | @react-native-documents/picker + @react-native-documents/viewer; react-native-blob-util or react-native-file-access for I/O | USE | both | Never react-native-fs (unmaintained). |
| Share (WhatsApp, share sheet) | react-native-share 12 | USE | both; WhatsApp Business target is Android-only | Section 7. |
| Share a summary as an image | react-native-view-shot 6 | USE | both | 1.2M/wk, active. |
| HTML → PDF | keep react-native-html-to-pdf 1.3.0 | USE, watch | both | Works as a TurboModule but has had no release for 12 months. Fallbacks: expo-print `printToFileAsync` (with Expo), or WRAP WKWebView `createPDF` / Android `PrintedPdfDocument` (~2–3 days). |
| System print (A4) | expo-print (with Expo) or a thin in-house module | WRAP | both | react-native-print is unmaintained. UIPrintInteractionController plus Android PrintManager with a WebView print adapter: ~2 days. |
| PDF viewing | @react-native-documents/viewer (hands off to the OS viewer) | USE | both | react-native-pdf only for in-app rendering (383 open issues). |
| Background upload / download | foreground react-native-blob-util + persisted retry queue with NetInfo; @kesha-antonov/react-native-background-downloader for downloads | SKIP true background upload; USE downloader if needed | both | Vydia's upload library is dead. An iOS URLSession background upload plus Android WorkManager wrapper would take ~1 week. |
| Maps (tanker ETA) | react-native-maps 1.29; v1 = deep link to Google/Apple Maps via `Linking` | USE later | both | Only needed once live tracking exists. |
| Location at capture time | expo-location (with Expo) or a thin in-house module | WRAP | both | The community geolocation libraries are unmaintained. |
| Background location (drivers) | react-native-background-geolocation or custom | defer / BUILD | both | Needs a Play background-location declaration and an Android 14 location FGS type. Licence of the Transistorsoft library unchecked. |
| Push | keep react-native-onesignal 5.5 | USE | both | Already integrated and active. |
| Local notifications + action buttons | react-native-notify-kit (Notifee API) or expo-notifications | USE | both | Do not add @notifee/react-native (archived). |
| In-app messaging | OneSignal in-app messages | USE | both | "No code"; skip Firebase IAM as a duplicate. |
| iOS Live Activity | SwiftUI widget-extension layout + OneSignal `setupDefault`/`startDefault` for lifecycle and push | BUILD (Swift UI) + USE (OneSignal) | iOS | Voltra or expo-widgets can author it in JSX if config-plugin tooling is accepted. ~1–2 weeks including APNs and CI signing. |
| Android Live Update | thin Kotlin module (`NotificationCompat.ProgressStyle` + `setRequestPromotedOngoing`), or wait for Voltra's next release | WRAP | Android | ~3–5 days. Voltra's version is merged but unreleased. |
| Home-screen widget (daily summary) | Android: react-native-android-widget. iOS: SwiftUI WidgetKit extension, or expo-widgets / Voltra | USE (Android) + BUILD (iOS) | both | Needs app-group shared storage. react-native-shared-group-preferences is dead, so WRAP a small module for it. |
| Siri / App Intents; Android AppFunctions | none | SKIP now | both | Swift or Kotlin only; Gemini AppFunctions is in private preview. |
| App shortcuts / quick actions | expo-quick-actions (with Expo), else a thin module | USE / WRAP | both | react-native-quick-actions is archived. A thin module is ~1 day. |
| App Clip / instant app | none | SKIP | — | Play Instant is shut down and App Clips are iOS-only and prebuild-oriented. Use web invoice links instead. |
| Biometric app lock | expo-local-authentication (with Expo), else @sbaiahmed1/react-native-biometrics or react-native-keychain access control | USE | both | Small maintainer risk on the @sbaiahmed1 package. |
| Passkeys | react-native-passkey 3.6 | SKIP for v1 | both | Email OTP works. Passkeys need server WebAuthn plus associated domains / assetlinks. |
| Secure storage | react-native-keychain 10 or expo-secure-store; react-native-mmkv 4 for non-secret cache | USE | both | — |
| OTA updates | Hot Updater (self-hosted) | USE | both | Section 3. |
| Bluetooth receipt printing | JS ESC/POS encoder + react-native-ble-manager (BLE, both platforms) + react-native-bluetooth-classic (Android Classic), or a vendor SDK (Star io10) if hardware is standardised | BUILD | both, but iOS needs BLE or MFi printers | Generic libraries are stale. ~2–3 weeks plus a device matrix. |
| Contact picker (onboard a customer) | thin module: Android `ACTION_PICK` / `ACTION_PICK_CONTACTS`, iOS `CNContactPickerViewController` | WRAP | both | No READ_CONTACTS needed. ~1–2 days. |
| tel: / sms: / WhatsApp / UPI links | core `Linking` | USE core | both | Section 7. |
| OTP autofill | `textContentType="oneTimeCode"` (iOS picks up codes from Mail) | USE core | iOS; SMS Retriever on Android only matters if SMS OTP is added | Email OTP needs no Android library. |
| Clipboard / haptics / permissions | @react-native-clipboard/clipboard (or expo-clipboard), react-native-haptic-feedback, react-native-permissions | USE | both | — |

- Where the ecosystem is thin enough to justify in-house work, it is almost always a thin wrap of one platform API: print dialog, contact picker, app-group storage, Android Live Update, location fix. Each is ~1–5 days per the opinion estimates above. Nitro 0.37 (2.0M/wk) or plain codegen TurboModules are both viable scaffolds.
- The expensive items are extension targets: WidgetKit / ActivityKit on iOS, plus Glance or RemoteViews on Android.

### Gaps
- Per-package open-issue counts for Expo modules are not available (monorepo).
- Not verified this session:
  - Whether expo-camera includes barcode scanning.
  - Whether react-native-share can attach a file when sending to a specific WhatsApp number on iOS.
  - Whether react-native-image-picker uses Android's system Photo Picker. This matters for Play's photo/video permission rules, which were also not checked.
- Licensing of Transistorsoft's react-native-background-geolocation was not checked.
- No evidence found on ML Kit / VisionKit OCR accuracy for Indian thermal-printed or handwritten DU slips.
- Google Maps SDK mobile pricing for 2026 was not verified.
- expo-app-intents provenance is unknown.
- react-native-android-widget and hot-updater declare `expo` as a peer (>=54, >=50). Whether that peer is optional was not checked.

## 2. Which Expo modules work in a bare RN app via expo-modules-core today, and is that a recommended route in 2026?

### Takeaway
Yes. Any Expo SDK module can run in a bare React Native CLI app once `expo` is installed (`npx install-expo-modules@latest`), and Expo documents this as the standard route. EAS Update, expo-widgets and expo-background-task each state they need it. The catch for DZZLO is version alignment: every Expo SDK is pinned to one RN minor, and no SDK targets RN 0.84.

| Expo SDK | Bundled react-native |
|---|---|
| 55 | 0.83.10 |
| 56 | 0.85.3 |
| 57 | 0.86.3 |
| 58 (next) | 0.88.0-rc.3 |

The cleanest path is to adopt Expo modules together with an RN 0.85 or 0.86 upgrade. The alternative is to run SDK 55 packages one minor ahead of their target.

### Cited Findings
- **Installing Expo modules:**
  - `npx install-expo-modules@latest`, which adds `use_expo_modules!` to the Podfile and updates `AppDelegate.swift`.
  - Current docs (written for RN 0.86) set the iOS deployment target to 16.4.
  - Babel and Metro configs change so that Expo CLI does the bundling.
  - "not using Expo CLI for bundling may result in unexpected behavior."
  - The automatic installer may fail if a project "deviates significantly from a default React Native project".
  - Source: [Expo docs: Install Expo modules](https://docs.expo.dev/bare/installing-expo-modules/).
- **SDK-to-RN mapping** from each SDK's `bundledNativeModules.json`: expo 55.0.31 → react-native 0.83.10; 56.0.23 → 0.85.3; 57.0.26 → 0.86.3; 58.0.0 (npm `next`) → 0.88.0-rc.3 — [SDK 55](https://cdn.jsdelivr.net/npm/expo@55.0.31/bundledNativeModules.json), [SDK 56](https://cdn.jsdelivr.net/npm/expo@56.0.23/bundledNativeModules.json), [SDK 57](https://cdn.jsdelivr.net/npm/expo@57.0.26/bundledNativeModules.json), [SDK 58](https://cdn.jsdelivr.net/npm/expo@58.0.0/bundledNativeModules.json).
- The `expo` package declares `react-native: "*"` as a peer for both SDK 55 and 56, so npm does not block installation on RN 0.84 — [npm registry expo@55.0.31](https://registry.npmjs.org/expo/55.0.31), [expo@56.0.23](https://registry.npmjs.org/expo/56.0.23).
- **Expo package versions now track the SDK number** (57.x = SDK 57), and older SDK lines still get patches. For example, expo-updates `sdk-55` shipped 55.0.33 on 2026-09-29, and expo-image-picker `sdk-55` shipped 55.0.24 on 2026-08-25 — [npm expo-updates](https://www.npmjs.com/package/expo-updates?activeTab=versions), [npm expo-image-picker](https://www.npmjs.com/package/expo-image-picker?activeTab=versions).
- **Status of the Expo modules asked about** (npm, 2026-09-29):

  | Module | Latest (date) | SDK-55 line | Weekly DL | Bare-app note | Source |
  |---|---|---|---|---|---|
  | expo-image-picker | 57.0.20 (2026-09-24) | 55.0.24 (2026-08-25) | 4,923,829 | needs `expo` | [npm](https://www.npmjs.com/package/expo-image-picker) |
  | expo-file-system | 57.0.7 (2026-09-11) | 55.0.26 (2026-08-25) | 10,549,669 | needs `expo` | [npm](https://www.npmjs.com/package/expo-file-system) |
  | expo-sharing | 57.0.22 (2026-09-24) | 55.0.24 (2026-08-25) | 2,808,118 | needs `expo` | [npm](https://www.npmjs.com/package/expo-sharing) |
  | expo-document-picker | 57.0.3 (2026-09-29) | 55.0.17 (2026-08-25) | 2,925,880 | needs `expo` | [npm](https://www.npmjs.com/package/expo-document-picker) |
  | expo-local-authentication | 57.0.3 (2026-09-11) | 55.0.18 (2026-08-25) | 1,560,310 | needs `expo` | [npm](https://www.npmjs.com/package/expo-local-authentication) |
  | expo-camera | 57.0.6 (2026-09-29) | 55.0.23 (2026-08-25) | 2,474,110 | needs `expo` | [npm](https://www.npmjs.com/package/expo-camera) |
  | expo-notifications | 57.0.21 (2026-09-24) | 55.0.27 (2026-08-25) | 5,172,792 | needs `expo`; Notifee's README names it as the migration target | [npm](https://www.npmjs.com/package/expo-notifications), [Notifee README](https://github.com/invertase/notifee) |
  | expo-live-activity | 0.4.2 (2025-11-18) | — | 20,336 | DEPRECATED; points to expo-widgets | [GitHub](https://github.com/software-mansion-labs/expo-live-activity) |
  | expo-widgets | 57.0.22 (2026-09-29) | 55.0.20 (2026-05-21) | 376,047 | iOS only; "install expo" first | [Expo docs](https://docs.expo.dev/versions/latest/sdk/widgets/) |
  | expo-updates | 57.0.24 (2026-09-29) | 55.0.33 (2026-09-29) | 4,341,403 | Expo modules are a prerequisite for EAS Update in bare apps | [Expo docs](https://docs.expo.dev/bare/updating-your-app/) |
  | expo-print | 57.0.2 (2026-09-11) | 55.0.19 (2026-08-25) | 687,652 | needs `expo` | [npm](https://www.npmjs.com/package/expo-print) |
  | expo-location | 57.0.20 (2026-09-24) | 55.1.14 (2026-08-25) | 2,628,991 | needs `expo` | [npm](https://www.npmjs.com/package/expo-location) |
  | expo-background-task | 57.0.21 (2026-09-29) | 55.0.22 (2026-08-25) | 398,236 | "make sure to install expo" | [Expo docs](https://docs.expo.dev/versions/latest/sdk/background-task/) |

- **EAS Update in a bare app:**
  - Prerequisite: "Run `npx install-expo-modules@latest` if the project does not have Expo modules".
  - Channels are set by hand through `expo.modules.updates.UPDATES_CONFIGURATION_REQUEST_HEADERS_KEY` metadata in AndroidManifest.xml and Expo.plist.
  - "you can use EAS Update without any other EAS services".
  - Source: [Expo docs](https://docs.expo.dev/bare/updating-your-app/).
- **Config plugins are framed as a CNG mechanism:** "When using Continuous Native Generation (CNG) in a project, native project changes are implemented without directly interacting with the native project files." The page says nothing about bare projects that do not prebuild — [Expo docs: config plugins](https://docs.expo.dev/config-plugins/introduction/).
- **Adoption signal:** `expo` gets 10,426,904 downloads a week and `expo-modules-core` 10,404,714 — [npm expo](https://www.npmjs.com/package/expo), [npm expo-modules-core](https://www.npmjs.com/package/expo-modules-core).

### Inferences
- **Recommended for DZZLO in 2026?** Yes, with conditions (opinion):
  - Take the Expo-modules route when three or more planned capabilities come from Expo, or when the community option is dead. For DZZLO that list is expo-print (react-native-print dead), expo-location (community geolocation dead), expo-quick-actions (react-native-quick-actions archived), expo-widgets (iOS widget / Live Activity in JSX), expo-local-authentication, expo-background-task and expo-updates.
  - Keep healthy community TurboModules as they are: react-native-share, blob-util, documents/picker, maps, permissions, keychain, OneSignal.
- **Sequence:**
  - Preferred: upgrade RN 0.84 → 0.85, adopt SDK 56, then pull in individual Expo modules.
  - Alternative: install the SDK 55 packages on RN 0.84.1 and treat any native build breakage as the cost. Not tested; see Gaps.
- **One-time cost:** Expo CLI bundling (Metro/Babel changes), a Podfile / AppDelegate diff, a possible iOS deployment-target bump (16.4 in the current docs), and Jest mocks for each Expo module. The team's Jest 30 + Testing Library setup will need a mock per module (not verified).
- **Config-plugin libraries** assume `expo prebuild` generates the native projects: Voltra, react-native-app-clip, @bacons/apple-targets and react-native-widget-extension. In DZZLO's hand-maintained `ios/` and `android/` folders, their native changes must be reproduced by hand, or the team must adopt prebuild. This is an inference, since Expo's docs describe plugins only in the CNG context.

### Gaps
- No official Expo statement on RN 0.84 compatibility was found; the table above is derived from `bundledNativeModules.json`.
- Untested whether SDK-55 native code compiles cleanly against RN 0.84.1.
- The iOS deployment target for SDK 55 or 56 in a bare app was not checked (current docs say 16.4 for the RN 0.86 era).
- A Jest 30 mocking strategy for Expo modules in a non-`jest-expo` preset was not researched.

## 3. What replaced CodePush (retired 2025) for bare RN — and what are the store rules?

### Takeaway
Hosted CodePush ended with App Center on 31 Mar 2025. For a bare RN app in 2026 the realistic options are:
- **Hot Updater:** open source and self-hosted, bare-first, New-Arch-ready, ~114 releases in 12 months, 1.0 RC in progress.
- **EAS Update:** needs Expo modules; free up to 50k MAU on the Production plan, then per MAU.
- **CodePush-compatible hosted services:** Revopush, Stallion, Codemagic.

Both stores allow OTA delivery of interpreted JS and assets only if it does not change the app's primary purpose or bypass security. Native code, new native modules and permission changes still need a store build.

### Cited Findings
- **CodePush retirement:** Microsoft retired App Center, including hosted CodePush, on 31 Mar 2025. The standalone CodePush server Microsoft published was archived and made read-only in May 2025 — [Codemagic blog (search summary)](https://blog.codemagic.io/react-native-ota-tools-in-2026/), [DEV (search summary)](https://dev.to/gfean/react-native-ota-after-codepush-how-to-choose-a-tool-in-2026-46of).
- microsoft/react-native-code-push is archived. Its last release was 9.0.1 (2024-12-19) and it still gets 31,864 downloads a week — [GitHub](https://github.com/microsoft/react-native-code-push), [npm](https://www.npmjs.com/package/react-native-code-push).
- **Hot Updater:**
  - Features: "Self-Hosted", "Web Console", "Bundle Diffing: ... ship compact Hermes patches" (a small Hermes change can go out as "a ~600 KB patch", falling back to the full bundle).
  - Storage plugins: AWS S3, Supabase Storage, Cloudflare R2. Database plugins: Supabase, PostgreSQL, Cloudflare D1. Build plugins: Metro, Re.Pack, Expo.
  - "New Architecture" support; bare apps are configured with `bare({ enableHermes: true })`.
  - Source: [GitHub README](https://github.com/gronxb/hot-updater).
  - npm: hot-updater and @hot-updater/react-native 0.36.16 (2026-09-29), 41,391 and 42,601 downloads a week, 114 stable releases in 12 months, `rc` tag 1.0.0-rc.19. GitHub: 1,743 stars, 18 open issues — [npm](https://www.npmjs.com/package/@hot-updater/react-native).
- **Other OTA SDKs** (npm, 2026-09-29):

  | Package | Latest (date) | Weekly DL | Source |
  |---|---|---|---|
  | expo-updates | 57.0.24 (2026-09-29) | 4,341,403 | [npm](https://www.npmjs.com/package/expo-updates) |
  | @revopush/react-native-code-push | 2.6.2 (2026-09-13) | 12,201 | [npm](https://www.npmjs.com/package/@revopush/react-native-code-push) |
  | react-native-stallion | 2.4.2 (2026-08-08) | 9,040 | [npm](https://www.npmjs.com/package/react-native-stallion) |
  | react-native-update (Pushy) | 10.59.1 (2026-09-29) | 4,965 | [npm](https://www.npmjs.com/package/react-native-update) |

- **Pricing and positioning** (Codemagic, 19 Aug 2026):
  - EAS Update Production plan includes 50,000 MAU; overage tiers are $0.005, $0.00375 and $0.0034 per MAU (≈ $3,774/month at 1M MAU plus bandwidth).
  - Revopush: free to 1,000 MAU; $500/month up to 1M MAU and 5 TB.
  - Stallion: free to 10,000 MAU; Pro $64/month for 100,000 MAU.
  - Codemagic Patch: self-hosted, with pre-generated manifests, CDN delivery, binary diffs and native fingerprinting.
  - Third-party Expo Updates protocol servers must "keep pace with ... SDK changes".
  - Revopush, Stallion and Codemagic Patch support RN 0.76+ on the New Architecture.
  - Source: [Codemagic](https://blog.codemagic.io/react-native-ota-tools-in-2026/).
- **EAS Update in bare** needs Expo modules and manual channel metadata — [Expo docs](https://docs.expo.dev/bare/updating-your-app/).
- **Apple DPLA** (quoted): "Interpreted code may be downloaded to an Application but only so long as such code: (a) does not change the primary purpose of the Application ..., (b) does not create a store or storefront for other code or applications, and (c) does not bypass signing, sandbox, or other security features of the OS."
- **App Review Guideline 2.5.2:** apps may not "download, install, or execute code which introduces or changes features or functionality of the app".
- **Google Play Device and Network Abuse** (quoted): "may not modify, replace, or update itself using any method other than Google Play's update mechanism ... This restriction does not apply to code that runs in a virtual machine or an interpreter where either provides indirect access to Android APIs (such as JavaScript in a webview or browser)."
- Sources for the three policy quotes: [Bitrise, updated 18 Sep 2026](https://bitrise.io/blog/post/what-app-stores-allow-with-ota-updates-apple-and-google-policy-explained).
- **Conflicts to flag:**
  - Bitrise's summary table marks "New JS-only features" as not allowed OTA on iOS but allowed on Android. That is Bitrise's conservative reading, not policy text.
  - Other sources cite the Apple clause as DPLA 3.3.1(B) or "Guideline 3.3.2" — [Bitrise](https://bitrise.io/blog/post/what-app-stores-allow-with-ota-updates-apple-and-google-policy-explained); numbering contradicted by [search summary citing 3.3.2/3.3.1(B)](https://www.appsonair.com/react-native-ota-updates-complete-2026-guide).

### Inferences
- **Default for DZZLO:** Hot Updater, self-hosted (for example R2 or S3 plus Postgres). Map one channel per environment, matching the `slave` / `master` release flow. Key each OTA bundle to a native fingerprint or app version so a JS bundle never reaches a binary that lacks its native modules. A CI check can fail when the native fingerprint changes (opinion).
- **When EAS Update wins:** if section 2's Expo-modules route is taken anyway. DZZLO's likely MAU (dealers + customers) sits inside the 50k MAU included in the Production plan (inference; DZZLO's MAU is unknown).
- **Policy practice:**
  - Ship bug fixes, copy and layout fixes, and small JS-only improvements OTA.
  - Ship anything that adds a native module, permission, extension target (widget, Live Activity) or a new primary capability through the stores.
  - This matches all three policy texts quoted above.

### Gaps
- Hot Updater's own docs on store compliance and on RN 0.84 specifically were not fetched.
- Revopush and Stallion support on RN 0.84 is not verified; Codemagic only says "from RN 0.76".
- Apple's current App Review Guidelines were not fetched directly (quoted via Bitrise).

## 4. What do comparable Indian SMB and fuel-industry apps ship natively, and what do users praise or complain about in reviews?

### Takeaway
- **Indian SMB ledger and billing apps** compete on WhatsApp/SMS sharing of bills and reminders with payment links or QR, Indian-language UI, offline use, thermal printing and barcode scanning.
- **Oil-company dealer apps** (IndianOil For Business, HP Buddy) centre on placing indents with live status, delivery confirmation, and offline delivery-person flows.
- **Pump-management apps** stress DSR, meter and dip readings, credit slips with vehicle and driver photos, and one-tap PDF sharing.
- **Only Zoho (global, iOS-first) ships widgets, Live Activities and Siri shortcuts** among the business apps reviewed; consumer delivery apps (Swiggy, Zomato) use Live Activities for order tracking.
- **Recent Play reviews** praise native WhatsApp sharing and one-tap PDF. They complain about crashes and lag, lost offline mode, a missing fingerprint lock, photo attachments that fail, and payment alerts that do not arrive.

### Cited Findings

**Store listings** (Google Play India, scraped 2026-09-29 with google-play-scraper; figures as displayed on each listing)

| App | Installs | Rating (count) | Last update | What the listing says it ships | Source |
|---|---|---|---|---|---|
| Khatabook | 50,000,000+ | 4.48 (590,814) | 2026-09-24 | Reminder links "via SMS/WhatsApp" ("multiple reminders with one tap"); "Generate GST/non-GST invoices quickly and share via WhatsApp"; "Show your Khatabook QR code for seamless in-store collection"; "all in your language" | [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook) |
| OkCredit | 10,000,000+ | 4.61 (432,496) | 2026-09-24 | "If you can use WhatsApp, you will also be able to use OkCredit very easily"; 11 Indian languages; "Send automatic payment reminders to your customers via WhatsApp or SMS"; "Scan any QR to pay, and show the QR to customer to collect"; "Offline Usage - OkCredit works even when you are offline" | [Play](https://play.google.com/store/apps/details?id=in.okcredit.merchant) |
| Vyapar | 10,000,000+ | 4.82 (194,991) | 2026-09-24 | GST e-invoices, payment reminders | [Play](https://play.google.com/store/apps/details?id=in.android.vyapar) |
| myBillBook | 10,000,000+ | 4.73 (148,886) | 2026-09-08 | "Download, print, or share bills instantly via WhatsApp, email, or SMS"; barcode generation; "Generate e-invoices and e-way bills with a single click"; "built-in WhatsApp & SMS marketing tools" | [Play](https://play.google.com/store/apps/details?id=com.valorem.flobooks) |
| Paytm for Business | 50,000,000+ | 3.89 (668,388) | 2026-09-25 | "Receive instant SMS and push notifications for every successful payment"; "Never miss a payment with instant voice alerts"; "Create payment links ... through WhatsApp, SMS, or email" | [Play](https://play.google.com/store/apps/details?id=com.paytm.business) |
| PhonePe Business | 100,000,000+ | 3.98 (488,145) | 2026-09-29 | QR payments, Smart Speaker (Soundbox), dynamic QR, "Real-Time Payment Tracking" | [Play](https://play.google.com/store/apps/details?id=com.phonepe.app.business) |
| Google Pay for Business | 50,000,000+ | 4.22 (292,283) | 2026-09-15 | SoundPod "loud audio notifications instantly, on receiving a payment, in the language of your choice" | [Play](https://play.google.com/store/apps/details?id=com.google.android.apps.nbu.paisa.merchant) |
| Zoho Invoice / Zoho Books | 1,000,000+ / 5,000,000+ | 4.7 (32,394) / 4.7 (30,628) | 2026-09-23 | Invoices "as a PDF instantly", customer portal, automated reminders, e-invoice via GSP | [Play Invoice](https://play.google.com/store/apps/details?id=com.zoho.invoice), [Play Books](https://play.google.com/store/apps/details?id=com.zoho.books) |
| IndianOil For Business | 1,000,000+ | 4.29 (30,824) | 2026-09-28 | For distributorships on IndianOil's ePIC platform. Partners: "Place an indent Order with 2 clicks and get live status". Delivery person: digital cash memos, "Confirm Delivery", "Call customer or navigate to his address directly from app", collect payment, create cash memo at the doorstep, "Works in Offline mode also". Mechanic: "Priority notification for leakage complaints" | [Play](https://play.google.com/store/apps/details?id=px.indianoil.in) |
| IndianOil ONE (consumer) | 10,000,000+ | 4.29 (1,095,762) | 2026-09-28 | LPG booking and tracking, nearest petrol pump, XTRAREWARDS | [Play](https://play.google.com/store/apps/details?id=cx.indianoil.in) |
| HP Buddy (HPCL) | 100,000+ | 3.64 (445) | not shown | "Dealers can efficiently place and track the indents"; delivery confirmation; RSP (retail selling price) history; stock updates; "Shortage Acknowledgement" | [Play](https://play.google.com/store/apps/details?id=com.hpcl.salesapp) |
| HPCL Merchant App | 100,000+ | 4.16 (273) | 2026-04-24 | Dynamic and static QR, Paycode, settlement view | [Play](https://play.google.com/store/apps/details?id=com.hpclmerchant) |
| PetroByte (pump management) | 1,000+ | 4.49 (56) | 2026-09-23 | Shift and tank management, lorry and bowser management, credit billing with reminders, DSR export "in PDF, Excel, and CSV formats" | [Play](https://play.google.com/store/apps/details?id=com.beanbyte.petrobyte) |
| SCUBE "PETROL PUMP SOFTWARE" | 10,000+ | 3.9 (40) | not shown | "Daily SMS of transactions", "Meter readings", "Dip reading", "Tanker entry", DSR, Tally integration, "Manage your Credit Customer Slip Entry With Vehicle, MPD, Driver Photo" | [Play](https://play.google.com/store/apps/details?id=com.petroprime.dsmapp) |
| Repos (doorstep diesel, customer app) | 10,000+ | 4.31 (266) | 2026-09-18 | "Live Fuel Level Monitoring"; "Verified Order Tracking ... GPS-based fueling locations, and instant delivery confirmations"; "Predictive Refill Alerts"; "Orders, GPS logs, and readings are auto-synced once connectivity is restored" | [Play](https://play.google.com/store/apps/details?id=com.reposenergy.customer) |
| FuelBuddy (doorstep diesel) | 100,000+ | 1.81 (149) | 2026-09-24 | Doorstep diesel in 180+ cities; IoT and cloud products | [Play](https://play.google.com/store/apps/details?id=in.fuelbuddy.app) |

**Pump-software vendor pages**
- Vyapar's petrol-pump page promotes "automated customer ledgers for credit customers and timely payment reminders via SMS and WhatsApp alerts" — [Vyapar (search summary)](https://vyaparapp.in/free/small-business-accounting-software/petrol-pump).
- petroMunim "automatically sends WhatsApp invoice messages to customers after every transaction" — [Keshav Solutions (search summary)](https://keshavsolutions.com/petrol-pump-software/).
- PetroPulse360 advertises "nozzle-wise meter readings, cash reconciliation, credit management ... from mobile phones" — [PetroPulse360 (search summary)](https://petropulse360.com/petrol-pump-credit-management).
- Vyapar and myBillBook both market thermal-printer billing, barcode scanning and offline use — [Vyapar thermal](https://vyaparapp.in/free/billing-software-for-retail-shop/thermal-printer), [myBillBook thermal](https://mybillbook.in/s/billing-software-for-retail-shop/thermal-printer/).

**Zoho's Apple-platform features**
- iOS 16: Zoho Books and Zoho Invoice added Lock Screen widgets and Live Activities — [Zoho blog, iOS 16](https://www.zoho.com/blog/general/take-your-work-to-the-next-level-with-zoho-apps-in-ios-16.html).
- iOS 18: a Control Center widget for creating transactions, and App Shortcuts in Spotlight runnable "using Siri commands" — [Zoho Books iOS 18 blog](https://www.zoho.com/blog/books/ios-updates-for-zoho-books.html).

**Consumer delivery apps (Live Activities)**
- Swiggy: "After a user places a food order, Swiggy sends 5 notifications, but with the live activity widget all updates can be handled in a single widget." Search snippet only; the page returned HTTP 403 — [Swiggy Design (Medium)](https://medium.com/swiggydesign/designing-with-constraints-live-activity-and-dynamic-island-71271c454bcb).
- Zomato: "On average, a customer opens the Zomato app 3-5 times after placing an order to check their order status." This is a designer's Behance case study, not official Zomato data — [Behance](https://www.behance.net/gallery/157101731/Zomato-Live-Activities).

**Recent Play reviews**
Method: the newest 1,000 reviews per app, keyword-filtered, fetched 2026-09-29. Hindi and Hinglish reviews are quoted as written, or paraphrased where marked.
- **Native WhatsApp share, praise:** "Thanks for Implementing the native whatsapp share option now it is working good and automatically contact is selected" — Vyapar, 5★, 2026-08-26 — [Play](https://play.google.com/store/apps/details?id=in.android.vyapar).
- **Image and PDF choice:**
  - "invoice jb share kary tu picture shere ho pdf hoti ha phir screen shot lina parta ha dono option dy picture and pdf" — Vyapar, 5★, 2026-09-19. The reviewer wants both an image and a PDF option — [Play](https://play.google.com/store/apps/details?id=in.android.vyapar).
  - "When I send a bill from Khatabook via WhatsApp, it automatically converts to PDF; how can I stop this?" — Khatabook, 3★, 2026-09-23 — [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook).
- **One-tap PDF:** "share PDF to customers in just one click is a great feature" — PetroByte, 5★, 2026-04-24 — [Play](https://play.google.com/store/apps/details?id=com.beanbyte.petrobyte).
- **Invoice links:** "after creating invoice via message and whatsapp Costomer getting a link for download their invoice" — myBillBook, 5★, 2026-05-01 — [Play](https://play.google.com/store/apps/details?id=com.valorem.flobooks).
- **Biometric lock requests:**
  - "Not yet received fingerprint app lock ... still waiting for fingerprint app lock" — Khatabook, 1★, 2026-08-16.
  - "the biometric lock functionality wasn't actually included. Instead, I'm left with only a standard pin lock" — Khatabook, 3★, 2026-08-13.
  - Source: [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook).
- **Offline demand:**
  - Paraphrase of a Hinglish review: "before buying premium I could enter data even offline; now offline doesn't work at all" — OkCredit, 1★, 2026-09-11 — [Play](https://play.google.com/store/apps/details?id=in.okcredit.merchant).
  - "the app cannot be used when there is no network connectivity ... I suggest that this app be designed to function in both offline and online modes" — myBillBook, 5★, 2026-04-15 — [Play](https://play.google.com/store/apps/details?id=com.valorem.flobooks).
- **Photo evidence matters for collections:**
  - Paraphrase of a Hindi review: photos uploaded to a customer ledger go blank later, "so the customer didn't pay me because they asked for the photo of the goods" — Khatabook, 1★, 2026-09-05 — [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook).
  - "Add amount with Bill image facility" is praised — OkCredit, 5★, 2026-09-11 — [Play](https://play.google.com/store/apps/details?id=in.okcredit.merchant).
- **Thermal printing:** "I'm using a thermal printer with Vyapar. Bills print perfectly, but ... there is no Thermal Print option [for Delivery Challan]" — Vyapar, 3★, 2026-07-26 — [Play](https://play.google.com/store/apps/details?id=in.android.vyapar).
- **Payment alerts not arriving:**
  - "voice alert setting for transactions is enabled ... I have not been receiving any voice alert notifications" — PhonePe Business, 1★, 2026-09-28.
  - "notifications also not coming ... lock screen notification is also not coming for every transaction" — 1★, 2026-09-04.
  - Source: [Play](https://play.google.com/store/apps/details?id=com.phonepe.app.business).
- **OTP friction:** "The app logs me out whenever there's an internet issue ... forcing me to verify again with OTP. This happens almost 10 times a month" — PhonePe Business, 1★, 2026-09-23 — [Play](https://play.google.com/store/apps/details?id=com.phonepe.app.business).
- **Permission distrust:** "new update is demanding sms permision even when the app is not running" — Khatabook, 1★, 2026-09-24 — [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook).
- **Crude keyword counts** (newest 1,000 reviews, reviews over 60 characters) show "slow/crash/hang/freeze" as the largest theme:

  | App | Slow / crash / hang / freeze |
  |---|---|
  | Khatabook | 17 |
  | Vyapar | 11 |
  | OkCredit | 11 |
  | myBillBook | 23 |
  | PhonePe Business | 47 |

  WhatsApp/share hits were 4 / 12 / 2 / 5 / 0 respectively — [Play listings above](https://play.google.com/store/apps/details?id=in.android.vyapar).

### Inferences
- The shared Indian SMB baseline is WhatsApp-first document sharing plus collections (links or QR) in Indian languages, working on low-end Android and patchy networks. "Delight" surfaces such as widgets, Live Activities and Siri appear only in Zoho's iOS apps and consumer delivery apps.
- DZZLO's dealers already use oil-company apps in which "place indent → live status → confirm delivery or acknowledge shortage" is standard (IndianOil For Business, HP Buddy). Their credit customers will likely expect the same order-status loop from DZZLO (inference).
- In these reviews, reliability outweighs novelty. Crash, lag and "alert didn't come" complaints far outnumber feature requests, so any native feature DZZLO adds must be testable and robust (inference, consistent with the team's test-first practice).

### Gaps
- No DZZLO user research or DZZLO store reviews were available.
- Not analysed:
  - iOS App Store reviews.
  - BPCL dealer apps, IndianOil XTRAPOWER fleet, Tally on mobile.
  - A "Petrosoft" app: only its vendor blog was found — [Petrosoft blog](https://petrolbunksoftware.com/blog/mobile-app-for-your-petrol-pump).
- Keyword counts are crude: "share" also matches non-WhatsApp text.
- FuelBuddy's 1.81 rating was not investigated.
- Swiggy's primary article could not be fetched.
- No data found on Live Activity adoption by any Indian B2B or fuel app.

## 5. Which native-powered features would dealers, their staff, customers and tanker drivers actually value, and why? (product-value ranking)

### Takeaway
The ranking is evidence-weighted and partly opinion:
1. One-tap WhatsApp share of invoices and statements (PDF and image).
2. Reminders carrying UPI pay links or QR.
3. Reliable order-status push with actions, then Live Activity / Live Update for deliveries.
4. Offline-first entry with background sync.
5. Photo or scan evidence for credit and DU slips and meter readings.
6. Biometric app lock and quick re-auth.
7. iOS Mail OTP autofill.
8. Thermal printing (demand-dependent).
9. Daily-summary widget.
10. Maps navigation now, live tanker tracking later.

Contact picker, IRN-QR scan, quick actions and in-app messages are cheap extras. Siri/Gemini, App Clips and OCR have little evidence behind them for this user base yet.

### Cited Findings
Each row's evidence comes from the sources cited in sections 1, 4 and 7. Key sources are repeated inline.

| Rank | Feature | Who values it | Evidence |
|---|---|---|---|
| 1 | Share invoice / statement / daily summary to the customer's WhatsApp, as PDF or image | Dealer, dealer staff; customer receives | Khatabook, myBillBook and OkCredit listings feature WhatsApp sharing — [Khatabook](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook), [myBillBook](https://play.google.com/store/apps/details?id=com.valorem.flobooks). Vyapar review praising native WhatsApp share with the contact auto-selected; reviews asking for picture and PDF — [Vyapar](https://play.google.com/store/apps/details?id=in.android.vyapar). PetroByte "share PDF ... in just one click" — [PetroByte](https://play.google.com/store/apps/details?id=com.beanbyte.petrobyte). petroMunim auto WhatsApp invoices — [Keshav](https://keshavsolutions.com/petrol-pump-software/). |
| 2 | Payment reminders with UPI link or QR | Dealer → credit customer | Khatabook reminder links and QR — [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook). OkCredit automatic WhatsApp/SMS reminders and QR — [Play](https://play.google.com/store/apps/details?id=in.okcredit.merchant). Paytm payment links over WhatsApp — [Play](https://play.google.com/store/apps/details?id=com.paytm.business). |
| 3 | Order-status push with actions (confirm / acknowledge), then a Live Activity (iOS) or Live Update (Android) while a tanker is en route | Customer; dealer | IndianOil For Business "indent ... get live status" — [Play](https://play.google.com/store/apps/details?id=px.indianoil.in). HP Buddy indent tracking and delivery confirmation — [Play](https://play.google.com/store/apps/details?id=com.hpcl.salesapp). Swiggy collapsed 5 notifications into one Live Activity — [Swiggy Design](https://medium.com/swiggydesign/designing-with-constraints-live-activity-and-dynamic-island-71271c454bcb). Android names "active food delivery tracking" as a proper Live Update use — [Android](https://developer.android.com/develop/ui/views/notifications/live-update). Merchants complain when alerts fail — [PhonePe Business](https://play.google.com/store/apps/details?id=com.phonepe.app.business). |
| 4 | Offline-first entry with auto-sync | Forecourt staff, delivery drivers | IndianOil For Business "Works in Offline mode" — [Play](https://play.google.com/store/apps/details?id=px.indianoil.in). Repos auto-sync "once connectivity is restored" — [Play](https://play.google.com/store/apps/details?id=com.reposenergy.customer). OkCredit offline praise and removal complaint — [Play](https://play.google.com/store/apps/details?id=in.okcredit.merchant). myBillBook offline request — [Play](https://play.google.com/store/apps/details?id=com.valorem.flobooks). |
| 5 | Camera or document-scan capture of credit / DU slips, meter and dip readings, cheques | Forecourt staff, drivers, dealer | SCUBE credit slips "With Vehicle, MPD, Driver Photo" and meter/dip readings — [Play](https://play.google.com/store/apps/details?id=com.petroprime.dsmapp). Khatabook dispute over a missing goods photo — [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook). OkCredit "Bill image facility" praise — [Play](https://play.google.com/store/apps/details?id=in.okcredit.merchant). |
| 6 | Biometric app lock and quick re-auth instead of repeated OTP | Dealer owner | Khatabook fingerprint-lock requests — [Play](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook). PhonePe Business re-OTP complaint — [Play](https://play.google.com/store/apps/details?id=com.phonepe.app.business). |
| 7 | OTP autofill (iOS Mail codes) | All iOS users | Apple — [Apple Support](https://support.apple.com/guide/iphone/automatically-fill-in-verification-codes-ipha6173c19f/ios). |
| 8 | Bluetooth thermal slip / cash-memo printing | Forecourt staff | Vyapar and myBillBook thermal support plus a review — [Vyapar](https://vyaparapp.in/free/billing-software-for-retail-shop/thermal-printer), [Play](https://play.google.com/store/apps/details?id=in.android.vyapar). IndianOil delivery person "Create Cash Memo at the customers doorstep" — [Play](https://play.google.com/store/apps/details?id=px.indianoil.in). |
| 9 | Home-screen widget: today's litres, amounts, cash | Dealer owner | Zoho Books / Invoice widgets and Control Center — [Zoho](https://www.zoho.com/blog/books/ios-updates-for-zoho-books.html). Indirect: payment apps invest in instant, glanceable payment alerts (voice, SoundPod) — [GPay for Business](https://play.google.com/store/apps/details?id=com.google.android.apps.nbu.paisa.merchant). |
| 10 | Navigate to the delivery address now; live tanker tracking and ETA later | Drivers; customers | IndianOil "navigate to his address directly from app" — [Play](https://play.google.com/store/apps/details?id=px.indianoil.in). Repos GPS-verified deliveries — [Play](https://play.google.com/store/apps/details?id=com.reposenergy.customer). Background-location policy cost — [Play Console Help](https://support.google.com/googleplay/android-developer/answer/9799150?hl=en). |
| 11 | Contact-picker onboarding of customers | Dealer staff | Android 17 picker exists; no user-demand evidence found — [Android](https://developer.android.com/about/versions/17/features/contact-picker). |
| 12 | E-invoice IRN QR scan and verify | Dealer (B2B) | Signed QR is a verifiable JWT; no demand evidence found — [Masters India](https://www.mastersindia.co/blog/signed-qr-code-e-invoicing-system/). |
| 13 | Quick actions ("New order", "Today") and in-app messages (price revisions, holidays) | Dealer, customer | Cheap (section 1); no demand evidence. |
| 14 | Siri / Gemini "what's my balance" | Dealer owner | Zoho ships Siri App Shortcuts — [Zoho](https://www.zoho.com/blog/books/ios-updates-for-zoho-books.html). Gemini AppFunctions was reported in private preview (search summary) — [Android](https://developer.android.com/ai/appfunctions). |
| 15 | App Clip / instant invoice view | Customer | Play Instant is shut down — [Android Police](https://www.androidpolice.com/rip-android-instant-apps/). myBillBook users praise plain invoice download links — [Play](https://play.google.com/store/apps/details?id=com.valorem.flobooks). |

### Inferences
- **Customers (credit buyers)** value receipts and statements arriving in WhatsApp, easy UPI payment, and knowing when fuel will arrive. DZZLO's HTML → PDF invoice pipeline already exists, so rank 1 is mostly wiring (opinion).
- **Dealer owners** value collections and control: reminders with pay links, the daily summary at a glance, and security (biometric lock).
- **Forecourt staff and tanker drivers** value offline capture and photo evidence, since disputes over slips and quantities recur in reviews and in pump-software feature lists.
- **Payment-received alerts:** Paytm, PhonePe and GPay "payment received" voice alerts are highly valued by merchants (the heavy investment shows it), but they apply to DZZLO only if DZZLO ever handles collections. Billing is web-only today (inference).
- **Deprioritise for now:** Siri/Gemini, App Clips, OCR and live GPS tracking. Evidence among Indian SMB and fuel users is weak, and the cost and policy burden is high (opinion).

### Gaps
- No direct interviews with DZZLO dealers, staff, drivers or customers.
- The iOS share of DZZLO's users is unknown; the brief says the base is "Android-heavy". This matters because Live Activities, App Clips and Siri are iOS-only.
- No evidence found for demand for daily-summary widgets among Indian SMB users specifically.
- No evidence found on tanker-driver app usage at DZZLO's dealers.

## 6. Which features are cheap (JS-only or one library) versus expensive (extension targets on both platforms)? — cost/value grid

### Takeaway
The quick wins are cheap and well evidenced: WhatsApp share of PDF and image, UPI links and QR, iOS OTP autofill, biometric lock, document-scan photo evidence, notification actions and OTA. Two strategic bets are expensive but valued: offline-first sync, and live order status through Live Activities / Live Updates. Thermal printing, live GPS tracking, widgets on iOS, and Siri/Gemini are costly and should wait for demand.

### Cited Findings
- **Cost drivers from platform docs:**
  - iOS Live Activities need a SwiftUI widget-extension target, APNs pushes of 4 KB or less, and iOS 16.1+ — [freeCodeCamp](https://www.freecodecamp.org/news/react-native-live-activities-handbook/).
  - Android Live Updates need specific notification styles, promotion flags and a permission — [Android](https://developer.android.com/develop/ui/views/notifications/live-update).
  - The iOS widget runtime is isolated, with "no React hooks, app state, or asynchronous work" — [Expo](https://docs.expo.dev/versions/latest/sdk/widgets/).
  - Android widgets built from RN views are rendered as images — [react-native-android-widget](https://github.com/sAleksovski/react-native-android-widget/blob/master/docs/docs/limitations.md).
  - Background location needs Play declarations — [Play Console Help](https://support.google.com/googleplay/android-developer/answer/9799150?hl=en).
  - iOS Bluetooth printing needs BLE or MFi hardware — [expo-thermal-printer (search summary)](https://github.com/Ricka7x/expo-thermal-printer).
  - Background tasks are not guaranteed and run at 15-minute minimum intervals on Android — [Expo](https://docs.expo.dev/versions/latest/sdk/background-task/).
- **Cheap paths from library facts:**
  - `Share.shareSingle` supports WhatsApp on both platforms and WhatsApp Business on Android, with a `whatsAppNumber` option — [react-native-share docs](https://github.com/react-native-share/react-native-share/blob/main/website/docs/share-single.mdx).
  - OneSignal's `setupDefault` reduces the Live Activity work to the widget layout — [OneSignal](https://documentation.onesignal.com/docs/en/cross-platform-live-activity-setup).
  - react-native-document-scanner-plugin needs no camera-permission prompt on Android — [GitHub](https://github.com/WebsiteBeaver/react-native-document-scanner-plugin).
  - expo-quick-actions covers iOS and Android — [GitHub](https://github.com/EvanBacon/expo-quick-actions).

### Inferences
Grid. The tier and effort columns are opinion; value comes from section 5.

| Feature | Value (evidence) | Cost tier | Rough effort, both platforms | Suggested wave |
|---|---|---|---|---|
| WhatsApp share of invoice PDF and summary image (react-native-share + view-shot) | High | T1 one library | 2–4 days | 1 |
| UPI pay link or QR in reminders and on invoices (Linking or server HTML; QR rendering) | High | T0 JS/server | 2–3 days | 1 |
| iOS OTP autofill (`textContentType`) | Medium | T0 | < 0.5 day | 1 |
| Biometric app lock / re-auth | Medium-High | T1 | 2–3 days | 1 |
| Photo / scan evidence for slips (doc scanner + resizer + upload) | High | T1 | 1 week | 1–2 |
| Push with action buttons (OneSignal / notify-kit) | High | T1 | 3–5 days | 2 |
| OTA updates (Hot Updater) | High for the team (faster fixes) | T1 + hosting | 1 week | 1 |
| In-app messages (OneSignal IAM) | Low-Medium | T0 (config) | 1 day | any |
| Quick actions (expo-quick-actions or thin module) | Low | T1/T2 | 1–2 days | any |
| Contact picker (thin module) | Medium | T2 thin wrap | 1–2 days | 2 |
| System print dialog (thin module or expo-print) | Medium | T2 | 2 days | 2 |
| Android Live Update for "tanker on the way" | High (customer) | T2 Kotlin module | 3–5 days | 3 |
| iOS Live Activity (SwiftUI extension + OneSignal / APNs) | High on iOS; iOS share unknown | T3 extension target | 1–2 weeks | 3 |
| Offline-first capture + sync (op-sqlite / MMKV + queue + NetInfo + background task) | High (staff, drivers) | T3 architecture | 3–6 weeks | 2–3 |
| Daily-summary widget (Android lib + iOS WidgetKit + app-group storage) | Medium | T3 (iOS) + T1 (Android) | 2–3 weeks | 3–4 |
| Bluetooth thermal printing (ESC/POS + BLE / Classic) | Medium, demand-dependent | T3 hardware matrix | 2–3 weeks | on demand |
| Navigation deep link to Google / Apple Maps | Medium | T0 | < 1 day | 1 |
| Live tanker GPS tracking + map ETA | Medium-High (customer) | T3 + policy + backend | 4–8 weeks | later |
| IRN QR scan + server verify | Low-Medium | T1 + server | 3–5 days | later |
| Siri App Intents / Gemini AppFunctions | Low (in this market) | T3 | 1–2 weeks per platform | skip for now |
| App Clip / instant app | Low | T3; Android impossible | — | skip (web link instead) |
| OCR of slips | Unknown (accuracy gap) | T2/T3 | 1–3 weeks | skip until a spike proves accuracy |

Tier key: T0 = JS or core APIs only; T1 = one maintained library; T2 = a thin in-house Turbo Module per platform; T3 = extension targets, heavy native, or cross-cutting architecture on both platforms.

### Gaps
- Effort figures are opinion, not measured against DZZLO's codebase.
- The iOS/Android user split, which drives the value of Live Activities and widgets, is unknown.
- No data on how many DZZLO dealers own thermal printers, or which models.

## 7. WhatsApp and UPI deep links in 2026: what are the options, what are the rules, and what needs native code?

### Takeaway
Both rails work from JavaScript with React Native's `Linking` and share APIs; the only native work is declarations in Info.plist and AndroidManifest.
- **WhatsApp chat links** (`https://wa.me/<number>?text=`) are pure links. Sending a PDF to a specific chat needs the share sheet or react-native-share. Automated order-status messages need the server-side WhatsApp Business Platform, which has charged per message since July 2025; India utility is about ₹0.115 plus GST, and sources disagree.
- **UPI intents** follow NPCI's `upi://pay` linking spec: generic intent chooser on Android, app-specific schemes on iOS. Confirm payment status server-side, never from the intent result. P2P collect requests ended on 1 Oct 2025; merchant collect continues.

### Cited Findings
- **wa.me links:** `https://wa.me/<full international number>?text=<url-encoded text>`, with the number written "without the plus sign (+) or spaces" and omitting "any zeroes, brackets, or dashes" — [BusinessChat help](https://help.businesschat.io/en/articles/6517838-how-to-build-a-whatsapp-click-to-chat-url-wa-me), [Chatfuel](https://chatfuel.com/blog/create-whatsapp-link). WhatsApp's own FAQ could not be fetched; see Gaps.
- **react-native-share `shareSingle`:**
  - `social: Share.Social.WHATSAPP` with `whatsAppNumber: "9199999999" // country code + phone number`.
  - Support table: WHATSAPP on Android and iOS; WHATSAPPBUSINESS on Android only.
  - Source: [react-native-share docs](https://github.com/react-native-share/react-native-share/blob/main/website/docs/share-single.mdx).
- **WhatsApp Business Platform pricing:**
  - Per-message pricing replaced 24-hour conversation pricing in July 2025.
  - India rates: marketing ₹0.8631; utility ₹0.1150 (effective 1 Jul 2026); authentication ₹0.1150; plus 18% GST.
  - Utility templates delivered inside the customer-service window are free.
  - Sources: [ChatMaxima India pricing](https://chatmaxima.com/whatsapp-api-pricing/india/), [WATI](https://www.wati.io/en/blog/whatsapp-api-pricing-guide/).
  - Conflicting figure: utility ₹0.145 per message — [AiSensy](https://aisensy.com/pricing), [MyOperator](https://myoperator.com/blog/whatsapp-business-api-pricing-india-2026) (the search summary did not attribute which of these two said which).
- **NPCI UPI Linking Specification 1.6** (Nov 2017):
  - Format `upi://pay?pa=...&pn=...`, with parameters pa (VPA), pn (payee name), mc (merchant code), tid, tr (transaction reference), tn (note), am (amount), mam (minimum amount), cu (currency), url.
  - "All PSP applications must mandatorily implement listening to 'UPI' links".
  - Sources: [NPCI spec PDF (third-party host)](https://www.labnol.org/files/linking.pdf), [spec summary](https://github.com/bgagan911/RandomDocs/wiki/NPCI-UPI---Specifications-for-Deep-Linking).
- **Google Pay India intent rules:**
  - Parameters: pa, pn, mc, tr, tn, am, cu, url. Package: `com.google.android.apps.nbu.paisa.user`.
  - "If the Google Pay response status is Submitted or Succeeded, you must check with your PSP or payment aggregators to ensure that the correct order amount is paid."
  - "NPCI requires that you support the generic intent call in all cases."
  - Source: [Google Pay for India developers](https://developers.google.com/pay/india/api/android/in-app-payments).
- **P2P collect discontinued:**
  - An NPCI circular of 29 Jul 2025 said P2P collect requests would stop being processed from 1 Oct 2025.
  - Merchant collect requests continue, with explicit user approval and a UPI PIN.
  - Users still pay by entering a UPI ID or scanning a QR.
  - Sources: [MediaNama](https://www.medianama.com/2025/08/223-npci-p2p-collect-payments-oct-1-what-it-means/), [Business Standard](https://www.business-standard.com/finance/personal-finance/upi-collect-requests-to-end-from-october-here-s-how-it-will-affect-you-125081500774_1.html).
- **iOS UPI:**
  - Apps must declare `LSApplicationQueriesSchemes` for the UPI app schemes they open (for example tez, phonepe, paytmmp, bhim, credpay); SDKs target specific apps on iOS — [PayU RN UPI SDK](https://docs.payu.in/docs/react-native-upi-sdk), [Cashfree UPI intent](https://www.cashfree.com/docs/payments/online/mobile/misc/upi_intent_support_js_sdk).
  - Paytm's iOS flow lists supported apps "Paytm, PhonePe, and GooglePay" and confirms the order through the backend "Transaction Status API" — [Paytm Payments iOS](https://www.paytmpayments.com/docs/integration-steps-for-ios/).
- **Prior art in comparable apps:** Khatabook, OkCredit and Paytm for Business send payment links and reminders over WhatsApp/SMS and show QR codes in-store — [Khatabook](https://play.google.com/store/apps/details?id=com.vaibhavkalpe.android.khatabook), [OkCredit](https://play.google.com/store/apps/details?id=in.okcredit.merchant), [Paytm for Business](https://play.google.com/store/apps/details?id=com.paytm.business).
- **UPI helper libraries on npm are abandoned:** react-native-upi-payment 1.0.5 (2023, 38 downloads a week); react-native-upi-pay 1.0.8 (2020, 24 a week) — [npm](https://www.npmjs.com/package/react-native-upi-payment), [npm](https://www.npmjs.com/package/react-native-upi-pay).

### Inferences
- **Native code needed: none.**
  - `Linking.openURL('https://wa.me/...')`, `Linking.openURL('upi://pay?...')`, `tel:` and `sms:` all work from JS.
  - react-native-share (already a TurboModule) covers "send this PDF to this WhatsApp number". Its WhatsApp-Business target is Android-only.
  - Configuration only: iOS `LSApplicationQueriesSchemes` for `whatsapp` and the UPI app schemes; Android `<queries>` entries so the app can resolve `upi` and WhatsApp packages. The Android package-visibility detail is an inference; the Android docs were not fetched.
- **Recommended pattern for DZZLO invoices and reminders:**
  - Put a UPI QR (a `upi://pay` string with the dealer's merchant VPA, `tr` = invoice number, `am`, `cu=INR`) and a "Pay" link into the HTML invoice or reminder.
  - Share the PDF and a text summary via react-native-share.
  - Reconcile payments from the dealer's bank or PSP data, never from the client (opinion, consistent with Google's server-verification rule).
- **Automated order-status messages to customers:** use WhatsApp Business Platform utility templates from the API server, not from the app. At about ₹0.115 plus GST per message, a few updates per order stay cheap. They are free if the customer messaged within the service window (inference from the pricing sources).
- **Risk to check:** whether PSP apps restrict prefilled-amount intents to non-merchant (personal) VPAs, which many small dealers may use. Not verified; see Gaps.

### Gaps
- WhatsApp's official Click-to-Chat FAQ could not be fetched (HTTP 400 / truncation); wa.me rules above come from third-party help pages — [WhatsApp FAQ](https://faq.whatsapp.com/5913398998672934).
- Not verified: whether `whatsapp://send` supports file attachments. Generally it does not; the share sheet is needed.
- No 2025–2026 NPCI circular on intent signing, or on P2M intent requirements for small merchants, was found. The public linking spec found is v1.6 from 2017.
- Not verified whether Google Pay or PhonePe block or limit P2P (personal-VPA) intents with prefilled amounts.
- Current India WhatsApp utility rate is contested (₹0.115 vs ₹0.145); Meta's official rate card was not fetched.
