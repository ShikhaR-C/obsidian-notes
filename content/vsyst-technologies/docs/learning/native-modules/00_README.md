# Native Modules for DZZLO OMS — What to Build, What to Drop, and How

> Audience: the DZZLO app team (JS-first, some Swift and Kotlin) | App: dzzlo_oms_app 1.79 on React Native 0.84.1, New Architecture | Status: written & web-verified 2026-09-29 against iOS 27 / Xcode 27, Android 17, RN 0.87.1 (latest) | Nothing here is built yet — the course describes the work; the build starts on the user's word.

---

## What This Folder Is

A nine-phase, hands-on course in writing — and mostly _not_ writing — native code for `dzzlo_oms_app`, with three capstones and a reference. It is also a **decision record**: for every device capability a petroleum-dealer OMS could use, it says whether we take a maintained library (**USE**), write a thin module over one platform API (**WRAP**), own an extension target or native surface (**BUILD**), or leave it alone (**SKIP**) — and why.

It was written against this repo, not a template. Six research notes fed it — five dated 2026-09-29, the sixth 2026-09-30:

1. **Repo audit** — `release/v1_79`, audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30), plus the 20-file working tree, read-only: every dependency, every native file, every manifest line, the release scripts and CI.
2. **React Native module technology** — Turbo Modules on 0.84–0.87, Nitro, Expo modules, Fabric components, native testing, toolchain, packaging, OTA.
3. **iOS platform features** — App Intents to App Clips, each with the iOS version that introduced it (read from Apple's documentation metadata), plus the App Store Review Guidelines.
4. **Android platform features** — the Android twin of each iOS feature, Play policy, and what Indian OEM skins and the Android version mix change.
5. **Ecosystem and product** — every candidate library's health (npm, React Native Directory, GitHub), comparable Indian SMB and fuel apps, their Play reviews, and a value ranking.
6. **Store rating and review** (added 2026-09-30) — StoreKit and Play In-App Review rules quoted verbatim, the library health check, the trigger policy and the "Rate DZZLO" row; it lands in [[09-phase-9-security-privacy-and-release]] §9.

Every number is either measured (✅ or "verified 2026-09-29") or an estimate marked _(est.)_. Where two notes disagree, the course records both and says which it follows — the full list is [[11-reference]] §2.7.

**How to read it.** Phases 1 and 2 come first, in order. Phase 1 pays for every "first" once — the first `codegenConfig`, `specs/` folder, XCTest bundle and Robolectric test in this repo — and Phase 2 removes what should not be carried forward. After that, Phases 3–9 are independent; take them in the wave order under **What Users Will Notice**, or in whatever order the user picks. Every phase ends with exercises that produce a file, a test result, a screenshot or a device observation. [[10-capstones]] ties the phases into three shippable features; [[11-reference]] holds the matrices, versions, policy map, recipe card, troubleshooting, glossary and sources.

Two facts in the original brief turned out wrong for this checkout and are corrected throughout: CocoaPods links **static libraries**, not dynamic frameworks, and `SceneDelegate` is a class **inside** `AppDelegate.swift`, not a file of its own.

## The App as Measured

|                         |                                                                                                                                                                                    |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **App**                 | `dzzlo_oms_app` **1.79** — Android `versionCode 104`, iOS build 1 at HEAD (2 in the working tree); package / bundle id `in.vsyst.dzzlooms`                                         |
| **React Native / React** | **0.84.1** / 19.2.3 — three minors behind 0.87 (0.87.0 released 2026-08-11; 0.87.1 is npm `latest` on 2026-09-29). An upgrade is planned; every phase carries "After the upgrade to 0.87" callouts |
| **Architecture**        | New Architecture only (`newArchEnabled=true`, `RCTNewArchEnabled = true`), Hermes, `RCT_REMOVE_LEGACY_ARCH=1` in the iOS C++ flags                                                 |
| **Language mix**        | JavaScript: 852 `.js` + 1 `.ts` in `src/` (855 `.js` + 2 TS files counting `App.js`, `index.js`, `__tests__/`); 674 non-test `src` files, **603** reachable from `index.js`        |
| **Android toolchain**   | Kotlin **2.1.20**, AGP **8.12.0** (RN Gradle-plugin catalog), Gradle **9.0.0**, NDK **27.1.12297006**, buildTools 36.0.0                                                          |
| **Android levels**      | minSdk **24**, compileSdk / targetSdk **36**; portrait pinned; `edgeToEdgeEnabled=false` (ignored on Android 16 at target 36)                                                      |
| **iOS**                 | deployment target **15.1** (= RN 0.84's `min_ios_version_supported`); iPhone + iPad; portrait-only; `UIRequiresFullScreen = true`                                                  |
| **Swift**               | `SWIFT_VERSION = 5.0` in both targets, **no bridging header** — while the machine runs Xcode 27.0 (27A266a) with Swift **6.4**                                                     |
| **Pods**                | CocoaPods 1.15.2, **static libraries** (40 static-library targets, 0 framework targets); `use_frameworks!` only if a `USE_FRAMEWORKS` env var is set; prebuilt `React.framework`; RNFirebase forced static |
| **Lifecycle**           | Swift `AppDelegate` with `RCTReactNativeFactory`; `SceneDelegate` at `AppDelegate.swift:41-58` — already UIScene, as the iOS 27 SDK requires                                        |
| **Targets**             | two: the app and `OneSignalNotificationServiceExtension`. No test target, widget, App Clip or intent extension                                                                     |
| **App Group, entitlements** | `group.in.vsyst.dzzlooms.onesignal` (app + NSE only); `aps-environment`; team `YT955YZMZU`. No associated domains, keychain sharing or Sign in with Apple                        |
| **Our own native modules** | **none** — no `codegenConfig`, no `specs/`; `MainApplication.kt` still carries the template's `// add(MyReactNativePackage())`                                                  |
| **Tests and CI**        | Jest ^30.3.0 (172 suites ✅; 174 after Phase 1, about 181 after Phase 2 _(est.)_), Testing Library 13, msw 2; CI = GitHub Actions `yarn test` on ubuntu-latest, Node 22. No XCTest, no JUnit/Robolectric, **no native build in CI**                     |
| **Release**             | Android: `build-release-apk.sh` → one universal APK (~107 MB) → Firebase App Distribution; AAB documented, not scripted. iOS: Xcode Archive by hand                               |
| **Machine**             | MacBook Pro M5 Max, macOS 27.0 (26A428), Xcode 27.0 (27A266a), Swift 6.4                                                                                                                      |

**The fact that governs everything else: this app has no native code of its own.** Apart from the React Native template, the only hand-owned native code is OneSignal's Notification Service Extension. So every module in this course is a first, and because CI never compiles iOS or Android, native code is verified only by the test targets we add and by recorded device runs — the same simulator and emulator records the house already keeps.

## What's Installed

32 runtime dependencies (`package.json:31-62`). Eighteen ship native code, plus `react-native` itself. Versions and dates from the npm registry, New-Architecture flags from the React Native Directory, both queried 2026-09-29.

### Native packages

| Package | Installed → latest | New Architecture | What it does here | Verdict |
| --- | --- | --- | --- | --- |
| `react-native` | 0.84.1 → 0.87.1 | core | runtime | KEEP; upgrade planned |
| `@react-native-async-storage/async-storage` | 3.0.2 → 3.1.1 | codegen | token + role (`userData`), auth step, language | KEEP — but the bearer token sits here in plain text ([[09-phase-9-security-privacy-and-release]]) |
| `@react-native-community/datetimepicker` | 9.1.0 → 9.2.1 | codegen | native pickers, 13 live files | KEEP |
| `@react-native-community/netinfo` | 12.0.1 (latest) | codegen | offline banner and screen | KEEP |
| `@react-native-firebase/{app,analytics,crashlytics,perf}` | 24.0.0 → 26.4.0 (two majors) | **compat layer** | crash, analytics, per-request perf | KEEP; upgrade on its own |
| `react-native-device-info` | 15.0.2 (latest) | **compat layer** | the `meta` header on every request, app-info alerts | REPLACE with `NativeAppInfo` ([[01-phase-1-foundations]]); the package itself leaves in [[02-phase-2-dependency-diet]] §4.3, once its three dead importers are deleted |
| `react-native-linear-gradient` | 2.8.3 (2023-09-06, latest) | **compat layer** | 3 live files | REPLACE with `react-native-svg` `<LinearGradient>` |
| `react-native-gesture-handler` | 2.31.0 → 3.3.0 (major) | codegen | root view, drawer, sheets | KEEP; take the major on its own |
| `react-native-html-to-pdf` | 1.3.0 (2025-09-04, latest) | codegen | **nothing** — imported, never called | REMOVE; `NativePdf` replaces the idea |
| `react-native-onesignal` | 5.4.1 → 5.5.14 | codegen | push, in-app messages; pulls OneSignalXCFramework 5.5.0 and `com.onesignal:notifications:5.7.6` | KEEP; upgrade |
| `react-native-reanimated` / `react-native-worklets` | 4.3.0 → 4.7.0 / 0.8.1 → 0.13.0 | codegen; worklets New-Arch-only | animations | KEEP; upgrade as a pair |
| `react-native-safe-area-context` | 5.7.0 → 5.10.1 | codegen | insets | KEEP |
| `react-native-screens` | 4.24.0 → 4.28.0 | codegen | native-stack container | KEEP |
| `react-native-svg` | 15.15.4 → 15.15.5 | codegen | every icon and illustration (160 live files) | KEEP |
| `react-native-webview` | 13.16.1 → 14.0.1 (major) | codegen | invoice, voucher and TCS/TDS HTML; the two manual websites | KEEP |

**Six packages run through the New-Architecture interop ("compat") layer** — the four Firebase packages, `react-native-device-info` and `react-native-linear-gradient`. They are the most legacy-shaped native surface in the app, and two of them are this course's first case studies.

### JS-only packages

| Package | Installed → latest | Live importers | Verdict |
| --- | --- | --- | --- |
| `@gorhom/bottom-sheet` | 5.2.8 → 5.2.14 | 49 | KEEP (the sheet-frame tests rely on the house mock) |
| `@react-navigation/{bottom-tabs, drawer, elements, native, native-stack}` | 7.15.9 → 7.19.2 · 7.9.8 → 7.14.2 · 2.9.14 → 2.9.43 · 7.2.2 → 7.4.1 · 7.14.10 → 7.19.2 | 2 · 5 · 24 · 81 · 8 | KEEP |
| `@react-navigation/stack` | 7.8.9 → 7.11.2 | **0** | REMOVE |
| `@reduxjs/toolkit` / `react-redux` | 2.11.2 → 2.13.0 / 9.2.0 → 9.3.0 | 7 / 110 | KEEP |
| `@shopify/flash-list` | 2.3.1 → 2.3.2 | 15 | KEEP (JS-only in v2; the Directory's "false" flag lags Shopify's own statement) |
| `moment` | 2.30.1 → 2.31.0 | 7 | REPLACE with house date helpers — characterisation tests first, because moment is device-local and the v2 helpers are IST |
| `react-native-paper` | 5.15.0 → 5.15.3 | 208 | KEEP |

### Imported but not installed, or installed but dead

| Package | Where | Status |
| --- | --- | --- |
| `react-native-code-push` | `screens/Common/Settings/Codepush.js:24`, `components/VersionInfo/index.js:25`, `screens/Login/AuthNavigator/BetaUser.js:12` | not installed; all three importers dead; CodePush itself retired 2025-03-31 |
| `react-native-image-picker`, `react-native-permissions` | `components/ImagePicker/index.js` (dead) | not installed; Jest keeps `{ virtual: true }` mocks by the team decision of 2026-07-05 ("keep them stubbed, do not install") |
| `rn-fetch-blob` | `components/Download/Invoice.js:1` (dead) | not installed |
| `react-native-html-to-pdf` | `screens/Common/Reports/TcsTds/Render/index.js:5` (live, never called) + 3 dead files | installed, unused |
| `prop-types` 15.8.1 | 13 live files, e.g. `components/Calender/Calendar.js` | **undeclared** — present only because another package hoists it |
| `@react-navigation/stack` | nobody | declared, unused |

The four phantom imports build only because every file that imports them is unreachable from `index.js`.

## Things Wrong With This Install (found while writing this)

Read off the repo on 2026-09-29. None of them needs a native module to fix; most are the first job of the phase named.

1. **`react-native-html-to-pdf` is imported and never called.** `src/screens/Common/Reports/TcsTds/Render/index.js:5` imports `RNHTMLtoPDF`; the component (lines 10–54) never uses it, nor the `Alert`, `Platform`, `Pressable` and `FAB` it also imports. The other three importers are dead. No live file imports `Share` either — so today a dealer can view an invoice, or have the server email it, but cannot share, save or print it from the phone. Fix: [[02-phase-2-dependency-diet]] removes it; [[03-phase-3-files-share-and-pdf]] builds `NativePdf`.

2. **75 of 674 non-test `src` files are unreachable, and four imported packages are not installed.** Biggest folders: `src/screens/Common` 18, `src/components/SVG` 9, `src/screens/Dealer` 6, `src/components/Download` 4, `src/components/Input` 4. Deleting the phantom-importing files would let Jest drop its two virtual mocks — which reverses the recorded 2026-07-05 team decision, so the user decides. Fix: [[02-phase-2-dependency-diet]].

3. **Every API request carries `"uniqueId":{}`.** `src/store/apis/createApi.js:10-20` builds `STATIC_DEVICE_INFO` at module scope, and line 18 is `uniqueId: DeviceInfo.getUniqueId()` — a **Promise** in device-info 15.0.2 (`getUniqueIdSync` is the sync variant). `JSON.stringify` turns it into `{}`, and line 45 sends that as the `meta` header on every call. The Tier 2 test asserts only `appName` and `deviceOS` (`auth.endpoints.msw.test.js:93-95`). Fix: [[01-phase-1-foundations]] — `NativeAppInfo` returns a string and an MSW test pins the header.

4. **Three generic location purpose strings.** `ios/dzzlo_oms_app/Info.plist:49-54`: all three read "$(PRODUCT_NAME) needs Location access for good user experience!", and no code asks for location. They are needed — `OneSignalXCFramework/OneSignalComplete` embeds `OneSignalLocation.framework`, whose binary references `requestAlwaysAuthorization` / `requestWhenInUseAuthorization` and trips App Store Connect's ITMS-90683 missing-purpose-string check (they were added 2021-03-15 for exactly that). The **wording** is the problem: it fails guideline 5.1.1(ii) ("clearly and completely describe"), and the repo checklist's proposed "delivery checkpoints" text would describe a feature that does not exist. Android declares no location permission. Fix: [[02-phase-2-dependency-diet]] (truthful wording plus a config-pin test that the keys stay while OneSignalLocation is linked); [[07-phase-7-maps-and-location]] if a location feature ever ships.

5. **No `<queries>` for `https`, so "Update app" probably does nothing on Android 11+.** `Linking.canOpenURL('https://…')` guards the update paths in `helpers/OneSignal/index.js:66-68`, `components/Error/ErrorMessage.js:28-37` and `components/Error/index.js:86-87`. Without a `<queries>` entry, `canOpenURL` resolves `false` on Android 11+ (RN 0.84.1's `IntentModule.kt`; React Native's docs say it may reject), and the merged manifest has none for https. No test covers it. Fix: [[02-phase-2-dependency-diet]] (manifest `<queries>` plus a config pin); [[08-phase-8-instant-experiences-and-links]] for links generally.

6. **The iOS archive hard-codes `APP_ENV=testing`.** At HEAD, `project.pbxproj:291` exports `APP_ENV=testing` in the "Bundle React Native code and images" phase, while the README says the repo ships `production` and "Production archives need no edit". An archive cut from HEAD bundles `.env.testing` — the staging API. Fix: [[02-phase-2-dependency-diet]] (a config pin, or env selection moved into a scheme or xcconfig); [[09-phase-9-security-privacy-and-release]] adds it to the release checklist.

7. **CodePush keys are still inlined into the JS bundle.** `src/constants/system.js:1-16` imports and re-exports the four `CODEPUSH_*` names from `@env`; the file is live (the OneSignal helper and `createApi.js` import it), so react-native-dotenv inlines their values into every build. The values were not read. Because dotenv runs `safe: true, allowUndefined: false`, the names must leave all five env files — the tracked `.env.ci` included — in the same change. Fix: [[02-phase-2-dependency-diet]]; the OTA replacement is in [[09-phase-9-security-privacy-and-release]].

8. **R8 is off and Android ships one ~107 MB universal APK.** `android/app/build.gradle:64` sets `enableProguardInReleaseBuilds = false`; `gradle.properties:28` builds all four ABIs; the release APK of 2026-09-29 is 106,793,519 bytes. The good news: all 23 arm64-v8a libraries are already 16 KB-aligned (`p_align = 16384`) ✅. Fix: [[02-phase-2-dependency-diet]] (R8 on, with keep-rules only where a build or device run proves one missing — OneSignal and Firebase are the named risks — then a full device regression; and an AAB or `abiFilters`); [[09-phase-9-security-privacy-and-release]] carries both onto the release checklist.

9. **Upload-key passwords are tracked in git.** `android/gradle.properties:46-49` is a tracked file and holds the values of `MYAPP_UPLOAD_STORE_PASSWORD` and `MYAPP_UPLOAD_KEY_PASSWORD` — deliberately not reproduced anywhere in this course. The keystore itself is untracked. Fix: [[02-phase-2-dependency-diet]] and [[09-phase-9-security-privacy-and-release]] — move them to `~/.gradle/gradle.properties` or CI secrets, rotate both (deleted lines stay in git history), and pin their absence with a config test.

10. **Six packages sit on the compat layer.** RNFirebase ×4 at 24.0.0, `react-native-device-info` 15.0.2 and `react-native-linear-gradient` 2.8.3 have no `codegenConfig`. React Native keeps the interop layer "for the foreseeable future" (0.82 blog), so nothing breaks today — but these are the packages most exposed to the next removal. Fix: [[01-phase-1-foundations]] (device-info → `NativeAppInfo`); [[02-phase-2-dependency-diet]] (§4.3 removes the device-info package once its three dead importers are gone; linear-gradient → svg; RNFirebase 24 → 26 as its own upgrade).

11. **The Notification Service Extension is version 1.0; the app is 1.79.** `project.pbxproj` sets `MARKETING_VERSION = 1.79` for the app (lines 458, 492) and `1.0` for the NSE (537, 581). App Store Connect usually warns when an extension's short version differs from its app _(likely, not verified)_. Fix: [[02-phase-2-dependency-diet]] (one version and one build number for every target, pinned by a config test); [[09-phase-9-security-privacy-and-release]] keeps it on the checklist; every new target (`DzzloWidgets`, `DzzloClip`) starts aligned.

12. **An unused Google OAuth URL scheme.** `Info.plist:25-35` registers the reversed-client-id scheme, but no `src` file uses Google Sign-In. Fix: [[02-phase-2-dependency-diet]] removes it after checking the Firebase settings; [[08-phase-8-instant-experiences-and-links]] gives the app links of its own.

**Also found, smaller:** `OneSignal.Debug.setLogLevel(LogLevel.Verbose)` runs unconditionally and the push prompt fires at first launch rather than in context (`helpers/OneSignal/index.js:14-79` → [[05-phase-5-notifications-and-live-status]]); `lastDayPrevMonth` is computed once at import in `NewVoucher` and `NewPayAck`, so a session that crosses midnight on the 1st uses the month before last (→ Phase 2, with moment); Firebase Analytics merges `AD_ID` and AdServices permissions that Play's Data safety form must declare, and `PrivacyInfo.xcprivacy` declares no collected data although Analytics, Crashlytics and OneSignal collect (→ Phase 9); and the store URLs are hard-coded in three files with mixed storefronts — Singapore to check, the US on the old `itunes.apple.com` host to open (`components/Error/ErrorMessage.js:21-26`, `components/Error/index.js:22-31`, `helpers/OneSignal/index.js:7-12`) — while DZZLO's one App Store rating is on the Indian storefront (→ Phase 9 §9: one `src/constants/storeLinks.js`).

## The Verdict: How Much Native Should We Write?

**In numbers: 14 capabilities come from a maintained library or React Native core, 8 thin modules each wrap one platform API (one only if a library audit fails, one later), 5 native surfaces we own outright (one of them later), and 12 things we deliberately skip.** Effort figures are the notes' own estimates for one engineer working test-first — all _(est.)_.

**USE — a maintained library or React Native core (14):**

| Capability | Library (version, date) | Note |
| --- | --- | --- |
| Share sheet, WhatsApp | `react-native-share` 12.3.1 (2026-05-04) | WhatsApp Business target is Android-only |
| Pick, save, open, Quick Look | `@react-native-documents/picker` 12.0.2 + `viewer` 4.0.1 (2026-07-28) | system pickers show Files and iCloud Drive |
| File I/O, foreground transfer | `react-native-blob-util` 0.25.1 (2026-09-24) | never the unmaintained `react-native-fs` |
| A summary as an image | `react-native-view-shot` 6.0.1 (2026-09-20) | for the "image" half of "PDF and image" |
| Custom camera, QR (IRN, UPI) | `react-native-vision-camera` 5.2.3 + `react-native-vision-camera-barcode-scanner` 5.2.3 (2026-08-20) | only when a custom camera is needed; brings the Nitro runtime |
| Photo picking | `react-native-image-picker` 8.2.1 (2025-05-04) | watch: no release in 16 months |
| Resize before upload | `@bam.tech/react-native-image-resizer` 3.0.11 (2024-11-25) | old release, active repo |
| Push, in-app messages, Live Activity lifecycle | `react-native-onesignal` 5.5.14 (2026-09-23) | already linked; upgrade from 5.4.1 |
| Local notifications, action buttons | `react-native-notify-kit` 10.8.0 (2026-09-29) | the maintained Notifee fork |
| Token storage, biometric app lock | `react-native-keychain` 10.0.0 (2025-03-23) | behind Phase 9's `src/native/appLock.js` — so no `NativeBiometrics`; watch: no release in 18 months |
| Maps, later | `react-native-maps` 1.29.11 (2026-09-27) | Apple Maps on iOS needs no key |
| OTA updates | Hot Updater 0.36.16 (2026-09-29) | self-hosted, bare-first |
| WhatsApp chats, UPI, `tel:`, `sms:`, map navigation | core `Linking` | plus `<queries>` and `LSApplicationQueriesSchemes` |
| OTP autofill on iOS | core `textContentType="oneTimeCode"` | iOS 17 fills codes that arrive in Mail |

**WRAP — thin Turbo Modules, one platform API per side (8):**

| Module | iOS · Android | Phase | Effort _(est.)_ |
| --- | --- | --- | --- |
| `NativeAppInfo` | bundle, version and device constants; replaces `react-native-device-info`, fixes `uniqueId` | 1 | ~10 getters, ~60 lines of native per platform (audit) |
| `NativePdf` | `WKWebView.createPDF` (iOS 14.0) or `UIPrintPageRenderer` (iOS 4.2) for A4 · WebView print adapter (API 21 form) | 3 | 2–3 days (ecosystem); 4–7 days on iOS with AirPrint (iOS note) |
| `NativePrint` | `UIPrintInteractionController` (iOS 4.2) · `PrintManager` | 3 | ~2 days |
| `NativeDocScanner` — **only if needed** | `VNDocumentCameraViewController` (iOS 13.0) · ML Kit Document Scanner (Play services, no CAMERA permission). Built only if an audit shows `react-native-document-scanner-plugin` 2.0.4 needs Expo; the DU-slips spec says not to write a scanner module while a healthy wrapper exists | 4 | ~1 day on Android; iOS inside the 4–8 days for QR + scan |
| `NativeUpload` — **later** | background `URLSession` (iOS 8.0; uploads from a file only) · WorkManager worker (+ user-initiated jobs, Android 14). DU slips upload in the foreground first (`XMLHttpRequest` with a `{uri}` body, the DU-slips spec's D7) | 4 | ~1 week both (ecosystem); 5–8 days iOS, 3–5 days Android |
| `NativeSharedStore` | App Group container `group.in.vsyst.dzzlooms.shared` · a Kotlin store the widget reads | 6 | 1–2 days |
| `NativeShortcuts` | role-based quick actions set after sign-in, cleared at sign-out: `UIApplicationShortcutItem` (iOS 9.0) · dynamic App Shortcuts (API 25) | 6 | ~1 day per platform |
| `NativeStoreReview` | the store's own rating sheet, asked once after a win and never from a button: `AppStore.requestReview(in:)` (iOS 16.0), `SKStoreReviewController.requestReview(in:)` on iOS 15 · Play In-App Review, `com.google.android.play:review` 2.0.2. The research note files it under BUILD — our own module rather than a library | 9 | ~95 lines with boilerplate, ~40 of them logic (store-review note) |

**BUILD — native surfaces that run outside the React Native runtime (5):**

| Target or surface | What it is | Phase | Effort _(est.)_ |
| --- | --- | --- | --- |
| `DzzloWidgets` (iOS Widget Extension) | Live Activity (ActivityKit, iOS 16.1; push-to-start 17.2) + Daily Summary widget (WidgetKit) + a "New order" Control (iOS 18.0) | 5, 6 | Live Activity via OneSignal 5–8 days (+ server); first widget with App Group and logout wipe 8–15 days |
| Kotlin `NotificationServiceExtension` | OneSignal extension that renders Live Updates (`ProgressStyle`, API 36) and an ordinary progress notification below Android 16 | 5 | 4–6 days incl. server (Android note); 3–5 days (ecosystem) |
| `DailySummaryWidget` | Jetpack Glance 1.2.0 home-screen widget | 6 | 5–8 days (3–5 with a JSX widget library instead) |
| "Outstanding balance" App Intent | `AppIntent` + `AppShortcutsProvider` (iOS 16.0) in Swift, with an app-named Siri phrase | 6 | part of a 10–20-day App Intents starter set |
| `DzzloClip` — **later** | App Clip, Swift-native (not RN), behind its own go/no-go | 8 | 10–20 days (+ web and server) |

**SKIP — deliberately not now (12):**

1. **Android Instant Apps** — Play Instant shut down in Dec 2025. Android gets a web invoice page with a UPI button and an App Link into the app instead.
2. **Free-form Siri AI** — no App Intents schema domain covers ordering or finance, and Siri AI needs an Apple Intelligence iPhone (15 Pro and later). Build App Shortcut phrases, which work on any iOS 16 iPhone.
3. **Gemini AppFunctions** — API 36 only, Jetpack alpha, Gemini access in private preview: effectively zero DZZLO users in 2026. Phase 6 keeps at most a debug-only spike behind a flag.
4. **Live GPS tanker tracking and geofences** — 4–8 weeks _(est.)_ plus background-location policy. A navigation deep link now takes under a day.
5. **OCR of slips** — accuracy on thermal-printed and handwritten Indian slips is unproven; spike before building.
6. **Bluetooth thermal printing** — on demand: 2–3 weeks _(est.)_ plus a printer matrix, and iOS needs BLE or MFi printers.
7. **Notification Content Extensions and a Quick Settings tile** — 5–8 days _(est.)_ for order lines inside a notification, later; Android gets "New order" as an App Shortcut rather than a tile unless dealers ask.
8. **Critical alerts and communication notifications** — not eligible (not health or safety); not person-to-person messages.
9. **Full-screen intents, exact alarms, battery-exemption requests** — Play restricts them to app types DZZLO is not.
10. **Passkeys and third-party sign-in for v1** — OTP works; adding Google sign-in would trigger guideline 4.8.
11. **Firebase In-App Messaging** — duplicates OneSignal's, and would force RNFirebase 24 → 26.
12. **Custom Fabric views, Nitro modules and Expo modules for our own code** — see the next two paragraphs.

**The rules behind those verdicts.** Write native only when:

1. a needed platform API has no maintained library;
2. the feature is an OS extension or target (widget, Live Activity, notification service extension, App Clip);
3. a JS↔native hot path is **measured** — per-frame calls, sensor streams, large buffers (none exists in this app);
4. a small, critical library is abandoned and cheaper to own than to replace.

Otherwise: a maintained library, then a JS-only solution, then a feature trade-off. Price every module at its lifetime — two more languages, a native test harness, a review at every React Native minor (about six a year), privacy and store review, and a store release for every change, because OTA can never ship native code. The module-technology note's own inference was "at most one or two thin modules"; the platform notes found more genuine gaps than that, so the course keeps each module to one platform API per side, ships them in waves, and never owns more than the phase in hand.

Shopify's 2026-09-10 announcement that it is moving its major apps back to Swift and Kotlin — because coding agents made "build twice" cheap — is about which stack a large team with native specialists should pick. It is not a reason for a JS-first team to write more modules: agents cut the cost of _writing_ Swift and Kotlin, not of owning it.

**Turbo Modules now, an optional Expo track after the upgrade, Nitro only for a measured hot path.** Our own modules are official Turbo Modules: a TypeScript spec in `specs/NativeX.ts`, codegen, Swift behind a thin Objective-C++ adapter on iOS (the documented path; pure Swift is not supported), Kotlin with a `BaseReactPackage` registered by hand in `MainApplication.kt`, a JS facade in `src/native/<name>.js` that Jest can mock. They are part of core, add no dependency, and the documented surface survived 0.82 → 0.87 largely untouched. Nitro (0.37.1, 2026-08-27) is faster in its own benchmark — 100,000 `addNumbers` calls in 7.27 ms against 115.86 ms for Turbo Modules — but it is still 0.x with no 1.0, adds a runtime dependency and always compiles C++ (so `.so` files and 16 KB checks), and no call in this app is hot enough to care; it arrives anyway as VisionCamera 5's runtime, and stays a later option for a measured hot path. Expo modules have the nicest Swift and Kotlin DSL, but every Expo SDK pairs with exactly one RN minor — SDK 56 ↔ 0.85, 57 ↔ 0.86, 58 preview ↔ 0.88 — and none pairs with 0.84 or 0.87; installing `expo` also changes Metro, Babel, the AppDelegate and the iOS minimum (16.4). So Expo is one optional track — third-party Expo packages and EAS Update, taken only on an Expo-paired RN version — and never the way we author our own modules. Without Expo, OTA is Hot Updater.

## What Users Will Notice

The ranking below weighs the Play listings of 17 comparable Indian SMB and fuel apps and their newest Play reviews (both fetched 2026-09-29), platform documentation and vendor pages. No DZZLO user research or DZZLO store reviews were available, and DZZLO's iOS/Android split is unknown — the brief calls the base "Android-heavy" — which matters because Live Activities, App Clips and Siri are iOS-only.

| Rank | Feature | Who values it | Evidence | Course home |
| --- | --- | --- | --- | --- |
| 1 | One-tap WhatsApp share of invoice, statement and summary — as **PDF and image** | dealer and staff; customer receives | listings (Khatabook, myBillBook, OkCredit); reviews — Vyapar 5★ 2026-08-26 praises native WhatsApp share with the contact auto-selected; a Vyapar review of 2026-09-19 asks for both picture and PDF; PetroByte "share PDF … in just one click" | Phase 3, Capstone A |
| 2 | Payment reminders with a UPI link or QR | dealer → credit customer | listings (Khatabook, OkCredit, Paytm for Business) | Phase 8 (`upi://` via `Linking`) |
| 3 | Order-status push with actions, then a Live Activity / Live Update while the tanker is on the way | customer, dealer | IndianOil For Business "indent … live status"; HP Buddy delivery confirmation; Swiggy collapsed five notifications into one Live Activity (search snippet); Android names delivery tracking as a proper Live Update; merchant reviews complain when alerts fail | Phase 5, Capstone B |
| 4 | Offline-first entry with auto-sync | forecourt staff, drivers | IndianOil "Works in Offline mode"; Repos auto-sync; OkCredit and myBillBook reviews | an architecture plan (op-sqlite / MMKV + queue + NetInfo, 3–6 weeks _(est.)_), not a native module — `NativeUpload` is its only piece here |
| 5 | Photo or scan evidence for credit and DU slips, meter and dip readings | staff, drivers, dealer | SCUBE "Credit Customer Slip Entry With Vehicle, MPD, Driver Photo"; a Khatabook 1★ dispute over a missing goods photo | Phase 4 |
| 6 | Biometric app lock and quick re-auth | dealer owner | Khatabook fingerprint-lock requests (1★ 2026-08-16, 3★ 2026-08-13); a PhonePe Business re-OTP complaint | Phase 9 |
| 7 | OTP autofill | iOS users | Apple Support (Mail codes, iOS 17) | Phase 9 |
| 8 | Bluetooth thermal printing | staff | Vyapar and myBillBook thermal support; a Vyapar review | skipped until demand |
| 9 | Daily-summary widget | dealer owner | Zoho Books / Invoice widgets; indirectly, payment apps' glanceable alerts | Phase 6, Capstone C |
| 10 | Navigate to the delivery address now; live tracking later | drivers, customers | IndianOil "navigate to his address"; Repos GPS-verified deliveries | Phase 7 |

Cheap extras with no demand evidence yet: contact picker, IRN-QR scan, quick actions, in-app messages. Deferred for weak evidence and high cost: Siri / Gemini (rank 14), App Clips (15), OCR, live GPS tracking. In the reviews, **reliability beats novelty**: across the five apps whose newest 1,000 reviews were keyword-counted, "slow / crash / hang / freeze" is the largest complaint theme (PhonePe Business alone: 47) — so every native feature DZZLO adds has to arrive tested and robust.

**Store ratings.** Ratings are how a dealer who has never used DZZLO judges it on the store page — and the App Store India listing shows **1 rating** (v1.78, 5.0; verified 2026-09-30; Play's count could not be read). [[09-phase-9-security-privacy-and-release]] §9 asks for a rating once, after a win, in any wave, and adds a "Rate DZZLO" row to Help.

### Delivery waves — the course's recommendation, for the user to decide

| Wave | What ships | Phases | What users notice | Effort _(est.)_ |
| --- | --- | --- | --- | --- |
| **1** | Dependency diet; `NativeAppInfo` (the `uniqueId` fix); share invoice / voucher / TCS-TDS as PDF or image to WhatsApp; `NativePdf`, `NativePrint`; export to Files / SAF | 1, 2, 3 | "Share" and "Print" on every document; "Update app" works on Android | share 2–4 d; PDF 2–3 d; print ~2 d (+ Phase 1–2 set-up) |
| **2** | Notifications done properly (permission in context, channels, action buttons, interruption levels, OEM guide) + Live Activity (iOS) / Live Update (Android) for dispatched orders; deep links into orders | 5, 8 | order status on the Lock Screen and status bar; a tap opens the order | push actions 3–5 d; Live Activity 5–8 d; Live Update 4–6 d; App Links 1–2 d |
| **3** | Images and scanning: slip photos and scans (the scanner plugin, or `NativeDocScanner` if its audit fails), IRN QR, resize; `NativeUpload` once foreground uploads fall short | 4 | slip photos attached to entries | ~1 week scan evidence; upload ~1 week, later |
| **4** | Widgets and intents: Daily Summary widget on both platforms, the "outstanding balance" App Shortcut phrase, quick actions (`NativeShortcuts`), an iOS "New order" Control | 6 | the day's numbers without opening the app | 2–3 weeks for the widget (ecosystem); Phase 6 in full 4–7 weeks |
| **Later** | Maps (a navigation deep link first), tanker tracking, `DzzloClip` | 7, 8 | — | App Clip 10–20 d; tracking 4–8 weeks |

**Any wave:** biometric lock and iOS OTP autofill (Phase 9), OneSignal in-app messages, quick actions, UPI links on invoices, Hot Updater OTA. The ecosystem note placed photo evidence in wave 1–2 and Live status in wave 3; the course follows that note's own value ranking instead (order status #3, photo evidence #5) and keeps each wave on one platform surface — notifications, then camera, then extensions. Swap waves 2 and 3 if dealers ask for slip photos first; after Phase 2 the phases do not depend on each other.

## Platform Facts That Bound Everything

| Fact | Date | What it means here |
| --- | --- | --- |
| iOS 27 and Xcode 27 shipped | 2026-09-14 | the machine already builds with Xcode 27.0 (27A266a) |
| App Store Connect accepts only iOS 26 SDK builds | since 2026-04-28 | the deployment target stays our choice (15.1 today) |
| UIScene life cycle mandatory with the iOS 27 SDK — without it the app does not launch (TN3187, WWDC26 278) | iOS 27 SDK | done: `SceneDelegate` in `AppDelegate.swift`, commit `b933119f` (2026-09-16) |
| Liquid Glass cannot be opted out: `UIDesignRequiresCompatibility` (iOS 26.0) is ignored when building for iOS 27 | iOS 27 SDK | headers, alerts, share sheets and pickers change look |
| iOS 27: supported orientations are a preference in resizable environments | WWDC26 278 | the portrait pin is not a layout guarantee — the 320 dp baseline rule already covers this |
| Android 17 (API 37) stable | 2026-06-16 | targeting 37 later brings `ACCESS_LOCAL_NETWORK`, widget bitmap caps and the location button |
| Play: new apps and updates must target API 36 | from 2026-08-31 (extension to 2026-11-01) | met — target 36 ✅ |
| Play 16 KB page sizes: updates that don't support them can't be released | 2027-02-01 per Google's page; older guidance said 2025-11-01, extendable to 2026-05-31 (conflict recorded) | release APK aligned ✅; check every new `.so` |
| Play Instant shut down | Dec 2025 | no Android twin for App Clips |
| Google Assistant removal from phones began | 2026-09-04 (news coverage) | App Actions have no voice surface; Gemini + AppFunctions is a private preview |
| India Android mix, Aug 2026 (StatCounter) | 16 = 24.1 % · 15 = 23.3 % · 13 = 13.9 % · 14 = 12.1 % · 12 = 9.4 % · 11 = 8.8 % | ~47 % on 15–16 and ~32 % on 11–13: every API 33 / 34 / 36 feature needs its fallback, built first |
| Expo SDK ↔ React Native | 55 ↔ 0.83 · 56 ↔ 0.85 · 57 ↔ 0.86 · 58 beta (2026-09-15) ↔ 0.88 RC | nothing pairs with 0.84 or 0.87 |
| notifee archived | 2026-04-07 | local notifications via `react-native-notify-kit` 10.8.0 |
| CodePush retired with App Center | 2025-03-31 | OTA = Hot Updater, or EAS Update on the Expo track |
| React Native cadence | 0.84 2026-02-11 · 0.85 04-07 · 0.86 06-11 · 0.87 08-11 | a new minor about every two months — and a module review with each |

## The Phases

| Phase | File | Level |
| ----- | ---- | ----- |
| 1 | [[01-phase-1-foundations]] — the New Architecture mental model, Turbo vs Nitro vs Expo, the toolchain as measured, test-first native work, and the first module: `NativeAppInfo` | Easy → Intermediate |
| 2 | [[02-phase-2-dependency-diet]] — remove, replace, repair: the unused stack navigator, dead files, html-to-pdf, moment, linear-gradient, prop-types, CodePush env, location strings, `<queries>`, the archive's `APP_ENV`, R8 / AAB | Easy |
| 3 | [[03-phase-3-files-share-and-pdf]] — share sheet to WhatsApp with a file, document picker, `NativePdf` (A4), `NativePrint`, Files / SAF export, Quick Look | Intermediate |
| 4 | [[04-phase-4-images-and-scanning]] — VisionCamera 5 and IRN QR, `NativeDocScanner`, photo picking without a permission, compression, `NativeUpload` | Intermediate → Advanced |
| 5 | [[05-phase-5-notifications-and-live-status]] — OneSignal in depth, local notifications, Live Activities in `DzzloWidgets`, Android 16 Live Updates through a Kotlin extension, OEM battery killers | Intermediate → Advanced |
| 6 | [[06-phase-6-widgets-shortcuts-and-intents]] — WidgetKit and Glance over `NativeSharedStore`, Controls and Quick Settings tiles, quick actions, App Intents and App Shortcuts, what Siri and Gemini really do in 2026 | Advanced |
| 7 | [[07-phase-7-maps-and-location]] — whether maps are needed at all, react-native-maps, Maps SDK caps, location tiers and purpose strings, tanker tracking as a foreground service, the deferral verdict | Intermediate |
| 8 | [[08-phase-8-instant-experiences-and-links]] — Universal and App Links, deep links into orders and invoices, the `DzzloClip` App Clip, the Android substitute (web + UPI intent), `wa.me` and `upi://` | Advanced |
| 9 | [[09-phase-9-security-privacy-and-release]] — biometric lock, Keychain, passkeys, OTP autofill, privacy manifest, Data safety, purpose strings that pass review, extension provisioning, OTA after CodePush, secrets, store rating and review, the release checklist | Intermediate |
| 10 | [[10-capstones]] — three end-to-end projects: invoice → WhatsApp, order status → Live Activity + Live Update, Daily Summary widget + intent | Capstone |
| —  | [[11-reference]] — library matrix, versions, effort, the review and policy map, the Turbo Module recipe card, troubleshooting, glossary, sources | Reference |

Start with [[01-phase-1-foundations]].

House rules, everywhere in this course: **test-first** — the Jest red on the JS facade, then the native unit-test red (XCTest / JUnit + Robolectric), then green, then a recorded device run ([[vsyst-technologies/docs/oms_app/tdd-testing-guide|TDD testing guide]]); **parity** — iOS and Android ship together, or the phase says what the other platform gets instead; **320 dp × fontScale 1, en + hi** is the width baseline for any UI; colours come from `src/theme` tokens; money is whole paise, half-up; and nothing is committed, merged, pushed or published without the user's word.
