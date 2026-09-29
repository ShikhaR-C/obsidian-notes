# DZZLO OMS app (`dzzlo_oms_app`, branch `release/v1_79`): native-module surface, dependency inventory and platform configuration (repo facts as of 2026-09-29)

Reading conventions for every section below. Repo citations link to files under `/Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app` and put `path:line` in the link text. Line numbers are from the working tree as read on 2026-09-29; `Info.plist` and `project.pbxproj` carry uncommitted edits, so a few of their line numbers differ from HEAD by up to about 12. "Live" means reachable from `index.js` by a static import walk; "dead" means not reachable. Registry facts come from `npm view` (queried 2026-09-29). New Architecture flags come from the React Native Directory API (queried 2026-09-29). No secrets were copied: env values, the OneSignal app id, Firebase/Google client ids and signing passwords are withheld.

## 1. What baseline was audited, and which facts in the brief need correcting?

### Takeaway
The audit covers HEAD `4d3ad441` (committed 2026-09-29 00:34 +0530) plus a working tree with 20 uncommitted files, all read-only. Two facts in the brief are wrong for this checkout. First, CocoaPods is installed with **static libraries**, not `use_frameworks! :linkage => :dynamic`. Second, `SceneDelegate` is a class **inside** `AppDelegate.swift`, not a separate file. Everything else in the brief was confirmed.

### Cited Findings
- HEAD is `4d3ad441` on `release/v1_79`, committed 2026-09-29 00:34 +0530 ("fix(auth): the sign-in step survives the app being killed …"). `git status` on 2026-09-29 shows 20 modified files: `ios/dzzlo_oms_app.xcodeproj/project.pbxproj`, `ios/dzzlo_oms_app/Info.plist` and 18 Daily Summary / DateRange JS files — [repo root](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/)
- The uncommitted `Info.plist` edit only reorders keys (`RCTNewArchEnabled`, `UIAppFonts`, `UIBackgroundModes`). The uncommitted `project.pbxproj` edit bumps the app's `CURRENT_PROJECT_VERSION` from 1 to 2 and reformats `inputPaths`/`outputPaths`/`OTHER_LDFLAGS` — [Info.plist](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/Info.plist), [project.pbxproj](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app.xcodeproj/project.pbxproj)
- The Podfile turns on frameworks only when an env var is set: `linkage = ENV['USE_FRAMEWORKS']; if linkage != nil … use_frameworks! :linkage => linkage.to_sym` ([Podfile:11-15](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile)). Nothing in README, `docs/`, `scripts/`, `.github/` or `AI.md` sets it (grep, 0 hits).
- The installed `Pods/Pods.xcodeproj` holds 40 `com.apple.product-type.library.static` targets, 17 resource bundles and **0 framework targets**. The only frameworks the embed script installs are prebuilt XCFrameworks: `hermesvm`, `React` (React-Core-prebuilt), `ReactNativeDependencies`, and 10 OneSignal frameworks (OneSignalFramework, Core, Extension, InAppMessages, LiveActivities, Location, Notifications, OSCore, Outcomes, User) — [Pods-dzzlo_oms_app-frameworks.sh](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Pods/Target%20Support%20Files/Pods-dzzlo_oms_app/Pods-dzzlo_oms_app-frameworks.sh)
- Firebase pods are pinned static: `$RNFirebaseAsStaticFramework = true`, plus a `pre_install` hook that sets `Pod::BuildType.static_library` on every `RNFB*` pod. The comment explains why: a global `use_frameworks! :linkage => :static` "breaks react-native-worklets / react-native-reanimated on RN 0.84" — [Podfile:20-43](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile)
- `class SceneDelegate: UIResponder, UIWindowSceneDelegate` is declared at `AppDelegate.swift:41-58`. The comment above it says iOS 27 SDK apps "must adopt the UIScene life cycle". No file `ios/dzzlo_oms_app/SceneDelegate.swift` exists — [AppDelegate.swift](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/AppDelegate.swift)
- Confirmed versions:
  - `react-native` 0.84.1 and `react` 19.2.3 ([package.json:48-49](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/package.json)); the installed `node_modules/react-native` is 0.84.1.
  - Kotlin 2.1.20, minSdk 24, compile/target 36, buildTools 36.0.0, NDK 27.1.12297006 ([android/build.gradle:3-8](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/build.gradle)).
  - AGP 8.12.0, from the RN Gradle plugin's version catalog ([libs.versions.toml](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/@react-native/gradle-plugin/gradle/libs.versions.toml)).
  - Gradle wrapper 9.0.0 ([gradle-wrapper.properties](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/gradle/wrapper/gradle-wrapper.properties)).
  - CocoaPods 1.15.2 ([Podfile.lock tail](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile.lock)).
  - Jest ^30.3.0, `@testing-library/react-native` ^13, msw ^2, Node >= 22.11.0 ([package.json:76-91](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/package.json)).
- Source census on 2026-09-29: 855 `.js` and 2 `.ts/.tsx` files (`src/types/env.d.ts`, `__tests__/App.test.tsx`) across `src/`, `App.js`, `index.js` and `__tests__/`. The static import walk from `index.js` (relative `import`, `export … from`, `require`, `import()`, `.native/.ios/.android` extensions, index files) reaches 603 files. **75 of the 674 non-test `src` files are unreachable** — [src/](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/), [index.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/index.js)
- Which sensitive files git tracks:
  - `android/gradle.properties` is **tracked** and contains the values of `MYAPP_UPLOAD_STORE_PASSWORD` and `MYAPP_UPLOAD_KEY_PASSWORD` (lines 46-49; values not reproduced here) — [gradle.properties](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/gradle.properties)
  - The upload keystore `android/app/dzzlooms-upload-key.keystore` is untracked (`.gitignore`: `*.keystore`, `!debug.keystore`).
  - `debug.keystore`, `google-services.json`, `ios/GoogleService-Info.plist`, `.env.ci` and `.env.example` are tracked.
  - `.env.development`, `.env.testing` and `.env.production` are untracked — [.gitignore](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/.gitignore)

### Inferences
- A course that says "this app uses dynamic frameworks" would be wrong for this checkout. `USE_FRAMEWORKS=dynamic bundle exec pod install` is possible, but the Podfile comment records that static frameworks broke worklets on 0.84, and RNFB is pinned static. Changing linkage is therefore a risky change in its own right, not a side effect of adding a module.
- Upload-key passwords committed in a tracked file are a credential-hygiene problem, separate from any native work. The usual fix is to move them to `~/.gradle/gradle.properties` or CI secrets and rotate them if the repo has ever been shared.

### Gaps
- I did not check whether a remote clone's history ever contained the upload keystore.
- The static walk cannot see dynamic `require(variable)` calls. None were found, and Metro resolves statically too.

## 2. (a) Every dependency: what it does here, whether it is native, installed vs latest version, New Architecture status, verdict

### Takeaway
The app declares 32 runtime dependencies ([package.json:31-62](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/package.json)). Eighteen ship native code, plus `react-native` itself. Six native packages have **no `codegenConfig`**, so on 0.84 they run through the New-Architecture interop layer: the four `@react-native-firebase/*` packages at 24.0.0, `react-native-device-info` 15.0.2 and `react-native-linear-gradient` 2.8.3. Clear removal or replacement candidates:
- `@react-navigation/stack` (unused).
- `react-native-html-to-pdf` (imported, never called).
- `moment` (7 live files; the house already writes its own date helpers).
- `react-native-linear-gradient` (3 live files; `react-native-svg` is already present).
- `react-native-device-info`, a candidate for a small in-house TurboModule rewrite. It is about 10 constant getters, and the rewrite would also fix a real `uniqueId` bug.

### Cited Findings
- Native code: a folder check of `node_modules/<pkg>` for `android/`, `ios/`/`apple/`, `*.podspec` and `codegenConfig` (2026-09-29) found:
  - **With `codegenConfig` (Codegen/TurboModule/Fabric):** async-storage, datetimepicker, netinfo, gesture-handler, html-to-pdf, onesignal, reanimated, safe-area-context, screens, svg, webview, worklets, react-native.
  - **Native without `codegenConfig`:** `@react-native-firebase/{app,analytics,crashlytics,perf}`, `react-native-device-info`, `react-native-linear-gradient`.
  - **JS-only:** `@gorhom/bottom-sheet`, all six `@react-navigation/*`, `@reduxjs/toolkit`, `@shopify/flash-list`, `moment`, `react`, `react-native-paper`, `react-redux`.
  - Source: [node_modules](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/)
- RN 0.84 leaves Legacy Architecture code out of iOS builds by default (`RCT_REMOVE_LEGACY_ARCH`), but "the Interop Layer code required for compatibility remains in place". It also deprecates `TurboModuleProviderFunctionType` — [React Native 0.84 blog, 2026-02-11](https://reactnative.dev/blog/2026/02/11/react-native-0.84). The app's C++ flags carry `-DRCT_REMOVE_LEGACY_ARCH=1` in the project-level Debug and Release configs — [project.pbxproj](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app.xcodeproj/project.pbxproj)

Dependency table. "Live files" counts importers reachable from `index.js`. Versions and publish dates are from the npm registry (package links), queried 2026-09-29. New-Architecture flags are from the RN Directory API (link per row). Jest lines point at [jest.setup.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/jest.setup.js).

| Package | What it does in this app (live importers) | Native? | Installed → latest (publish dates) | RN Directory (2026-09-29) | Jest | Verdict · evidence · risk |
|---|---|---|---|---|---|---|
| [@gorhom/bottom-sheet](https://www.npmjs.com/package/@gorhom/bottom-sheet) | Every v1 and v2 bottom sheet: 49 live files, e.g. `components/v2/Sheet.js`, `components/v2/DateRangeSheet/DateRangeSheet.js`, `components/DatePicker/DTBS.js`; provider in `navigation/AppNavigatorContainer.js` | JS on top of Reanimated and Gesture Handler | 5.2.8 (2025-12-04) → 5.2.14 (2026-05-09) | [newArchitecture: true](https://reactnative.directory/api/libraries?search=%40gorhom%2Fbottom-sheet) | Shipped mock plus a house subclass that draws `handleComponent` (lines 157-218) | **KEEP**, patch bump. The sheet-frame tests depend on the house mock |
| [@react-native-async-storage/async-storage](https://www.npmjs.com/package/@react-native-async-storage/async-storage) | Persistence: keys `userData` (token and role), `currentUser`, auth step, day start, language, `IS_BETA_USER`. 9 live files, e.g. `helpers/Auth/authStep.js`, `i18n/LanguageProvider.js`, `store/apis/createApi.js` | Yes, codegen. v3 needs a local Maven repo ([android/build.gradle:25-31](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/build.gradle)) | 3.0.2 (2026-03-26) → 3.1.1 (2026-05-29) | [true, turbo](https://reactnative.directory/api/libraries?search=%40react-native-async-storage%2Fasync-storage) | Shipped `/jest` in-memory mock (52-54); 21 test files use it | **KEEP.** The bearer token sits in plain AsyncStorage, which makes this a secure-storage module candidate (§10) |
| [@react-native-community/datetimepicker](https://www.npmjs.com/package/@react-native-community/datetimepicker) | Native date/time pickers: 13 live files, e.g. `components/v2/DateRangeSheet/pickers.js`, `components/DatePicker/DTBS.js`, `screens/Common/Orders/bottomsheet/dateRange.js` | Yes, codegen | 9.1.0 (2026-03-17) → 9.2.1 (2026-09-07) | [true](https://reactnative.directory/api/libraries?search=%40react-native-community%2Fdatetimepicker) | Not mocked; 10 test files import it | **KEEP** |
| [@react-native-community/netinfo](https://www.npmjs.com/package/@react-native-community/netinfo) | Offline banner and screen: `components/Network/index.js` (`fetch`, `addEventListener`, `isConnected`, `isInternetReachable`), `components/NoNetwork/{index,Undraw}.js` | Yes, codegen | 12.0.1 (2026-02-14), already latest | [true, turbo](https://reactnative.directory/api/libraries?search=%40react-native-community%2Fnetinfo) | Shipped mock (58-60) | **KEEP.** A rewrite (NWPathMonitor / ConnectivityManager) is possible but low value |
| [@react-native-firebase/app](https://www.npmjs.com/package/@react-native-firebase/app), [analytics](https://www.npmjs.com/package/@react-native-firebase/analytics), [crashlytics](https://www.npmjs.com/package/@react-native-firebase/crashlytics), [perf](https://www.npmjs.com/package/@react-native-firebase/perf) | **app:** 0 imports; native `FirebaseApp.configure()` at AppDelegate.swift:16; Gradle plugins at app/build.gradle:5-7. **analytics:** `utils/firebase.js` (setUserProperty `proj_env`, logEvent, logScreenView, setUserId) and `store/middleware/rtkQueryPerfLogger.js` (an `api_call` event per endpoint). **crashlytics:** `rtkQueryErrorLogger.js:66` recordError, `AppNavigatorContainer.js:94` enables collection, test crash/recordError buttons at `screens/Common/Settings/index.js:172,189`. **perf:** an HTTP metric per request (`store/apis/createApi.js:71`) and a `rtkq_<endpoint>` trace | Yes, **no codegenConfig** in 24.0.0 (interop layer) | 24.0.0 (2026-04-01) → 26.4.0 (2026-09-05), two majors | [app: true, turbo](https://reactnative.directory/api/libraries?search=%40react-native-firebase%2Fapp) | Hand mocks (lines 3-47) | **KEEP**; upgrade separately. Perf keeps the `FirebaseRemoteConfig` and `FirebaseABTesting` pods ([Podfile:25-33](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile)). Analytics adds the AD_ID / AdServices permissions (§7) |
| [@react-navigation/bottom-tabs](https://www.npmjs.com/package/@react-navigation/bottom-tabs), [drawer](https://www.npmjs.com/package/@react-navigation/drawer), [elements](https://www.npmjs.com/package/@react-navigation/elements), [native](https://www.npmjs.com/package/@react-navigation/native), [native-stack](https://www.npmjs.com/package/@react-navigation/native-stack) | Navigation: tabs in 2 live files (`navigation/{Dealer,Customer}/TrnTab.js`), drawer 5, elements 24, native 81, native-stack 8 | JS; native parts come from `react-native-screens` | bottom-tabs 7.15.9 → 7.19.2; drawer 7.9.8 → 7.14.2; elements 2.9.14 → 2.9.43; native 7.2.2 → 7.4.1; native-stack 7.14.10 → 7.19.2 (all modified 2026-09-22) | JS libraries | Not mocked | **KEEP** |
| [@react-navigation/stack](https://www.npmjs.com/package/@react-navigation/stack) | **Nothing**: 0 src and 0 test importers | JS | 7.8.9 (2026-03-28) → 7.11.2 (2026-09-17) | [newArchitecture: false (JS)](https://reactnative.directory/api/libraries?search=%40react-navigation%2Fstack) | n/a | **REMOVE** (§3). Risk: none found |
| [@reduxjs/toolkit](https://www.npmjs.com/package/@reduxjs/toolkit) and [react-redux](https://www.npmjs.com/package/react-redux) | Store and RTK Query: 7 and 110 live files | JS | RTK 2.11.2 → 2.13.0 (2026-09-29); react-redux 9.2.0 → 9.3.0 | JS | Real store per test via `makeStore()` | **KEEP** |
| [@shopify/flash-list](https://www.npmjs.com/package/@shopify/flash-list) | Long lists: 15 live files, e.g. `screens/Common/Invoices/components/InvoiceList.js`, `Payments/components/PaymentList.js`, `Customer/Dealers/index.js` | JS-only in v2 | 2.3.1 (2026-03-23) → 2.3.2 (2026-06-10) | [false, note "Compiles and runs, but behavior may not be as expected"](https://reactnative.directory/api/libraries?search=%40shopify%2Fflash-list). Shopify calls v2 "a ground-up rewrite for React Native's New Architecture" that moved to JS-only ([Shopify Engineering](https://shopify.engineering/flashlist-v2)) | Not mocked; 4 test files | **KEEP**. The directory flag lags the vendor's statement |
| [moment](https://www.npmjs.com/package/moment) | Date arithmetic in 7 live files (§4) | JS | 2.30.1 (2023-12-27) → 2.31.0 (2026-09-15) | n/a | 0 test files import it | **REPLACE** with house date helpers, characterisation tests first (§4) |
| [react-native](https://www.npmjs.com/package/react-native) / [react](https://www.npmjs.com/package/react) | Runtime | Core | RN 0.84.1 (2026-02-27) → 0.87.1 (2026-08-26). React 19.3.0 is on npm, but RN pins its React (19.2.3 for 0.84) | — | Preset `react-native` | **KEEP.** Three RN minor versions behind as of 2026-09-29 |
| [react-native-device-info](https://www.npmjs.com/package/react-native-device-info) | Device and app constants: the `meta` header built from 9 getters (`createApi.js:10-20`), app-info alerts in `Settings/index.js` and `Login.js:727-750`, `Help/index.js:56` (getVersion), OneSignal IAM trigger (`helpers/OneSignal/index.js:45`) | Yes, **no codegenConfig** (interop). References `CLLocationManager` class methods ([RNDeviceInfo.m:866,995-998](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/react-native-device-info/ios/RNDeviceInfo/RNDeviceInfo.m)) | 15.0.2 (2026-02-21), already latest | [newArchitecture: true but github.newArchitecture: false; alternative listed: expo-device](https://reactnative.directory/api/libraries?search=react-native-device-info) | Shipped mock (55-57) | **REWRITE candidate:** a small in-house `AppInfo` TurboModule. Fix the `uniqueId` bug first (§10). Risk: the `meta` header on every API call. Tests only assert `appName` and `deviceOS` ([auth.endpoints.msw.test.js:93-95](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/store/apis/__tests__/auth.endpoints.msw.test.js)) |
| [react-native-gesture-handler](https://www.npmjs.com/package/react-native-gesture-handler) | Root view (App.js:4,19), drawer contents, peer of the drawer and bottom-sheet | Yes, codegen | 2.31.0 (2026-04-02) → 3.3.0 (2026-09-11), **major** | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-gesture-handler) | `jestSetup` (151) | **KEEP**. Validate the major bump on its own |
| [react-native-html-to-pdf](https://www.npmjs.com/package/react-native-html-to-pdf) | **Imported by 1 live file that never calls it** (`screens/Common/Reports/TcsTds/Render/index.js:5`), plus 3 dead files | Yes, codegen (turbo) | 1.3.0 (2025-09-04), latest; GitHub last push 2025-09-04 | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-html-to-pdf) | Not mocked | **REMOVE**, or **REPLACE** with an in-house HTML → PDF / print / share module if invoice PDFs become a feature (§4, §10) |
| [react-native-linear-gradient](https://www.npmjs.com/package/react-native-linear-gradient) | 3 live files: `components/Divider/index.js:21-28`, `navigation/Common/DrawerBackground.js`, `screens/Login/AuthNavigator/Welcome.js:101-110` | Yes, **no codegenConfig** (interop) | 2.8.3 (2023-09-06), latest | [true, turbo (repo main branch, pushed 2026-02-20)](https://reactnative.directory/api/libraries?search=react-native-linear-gradient) | Not mocked | **REPLACE** with `react-native-svg` `<LinearGradient>` (svg is already in 160 live files). RN's own `backgroundImage: linear-gradient(…)` is documented as experimental and "should not be used in production" ([RN View Style Props](https://reactnative.dev/docs/view-style-props)). Risk: visual only; no tests |
| [react-native-onesignal](https://www.npmjs.com/package/react-native-onesignal) | Push and in-app messages via `helpers/OneSignal/index.js` (init, permission prompt, click → Redux `setNotification`, IAM `app_version` trigger, `update_app` → store link), called from `navigation/AppNavigatorContainer.js:22`. Native NSE target (§8) | Yes, codegen. Pulls `OneSignalXCFramework` 5.5.0 (iOS) and `com.onesignal:notifications:5.7.6` (Android) | 5.4.1 (2026-03-25) → 5.5.14 (2026-09-23) | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-onesignal) | Hand stub (224-243) | **KEEP**, but fix the log level, prompt timing and location strings (§6, §10); upgrade |
| [react-native-paper](https://www.npmjs.com/package/react-native-paper) | UI kit in 208 live files. `optional-require` avoids installing vector icons ([babel.config.js:16-21](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/babel.config.js)); icons are house SVGs in `components/SVG/RNVI/*` | JS | 5.15.0 (2026-02-04) → 5.15.3 (2026-05-26) | JS | Not mocked | **KEEP** |
| [react-native-reanimated](https://www.npmjs.com/package/react-native-reanimated) and [react-native-worklets](https://www.npmjs.com/package/react-native-worklets) | Animations in 7 live files (e.g. `components/v2/Sheet.js`, `navigation/Common/Details.js`). Worklets has 0 direct imports but is Reanimated 4's runtime: babel plugin (babel.config.js:22), Metro wrapper (metro.config.js:2-4,16-19), Jest resolver, and `pickFirst 'lib/*/libworklets.so'` ([app/build.gradle:120-125](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build.gradle)) | Yes, codegen; worklets is New-Arch-only | reanimated 4.3.0 (2026-03-25) → 4.7.0 (2026-09-18); worklets 0.8.1 (2026-03-20) → 0.13.0 (2026-09-18) | [reanimated true](https://reactnative.directory/api/libraries?search=react-native-reanimated); [worklets new-arch-only](https://reactnative.directory/api/libraries?search=react-native-worklets) | `setUpTests()` (221) plus composed resolver | **KEEP**; upgrade the pair together |
| [react-native-safe-area-context](https://www.npmjs.com/package/react-native-safe-area-context) | Insets in 16 live files (e.g. `components/v2/Screen.js`, App.js:9,20) | Yes, codegen | 5.7.0 (2026-02-24) → 5.10.1 (2026-09-29) | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-safe-area-context) | Shipped mock (148-150) | **KEEP** |
| [react-native-screens](https://www.npmjs.com/package/react-native-screens) | 0 direct imports. It is native-stack's container and needs `super.onCreate(null)` ([MainActivity.kt:28-30](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/main/java/in/vsyst/dzzlooms/MainActivity.kt)) | Yes, codegen | 4.24.0 (2026-02-23) → 4.28.0 (2026-09-14) | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-screens) | Not mocked | **KEEP** (required peer) |
| [react-native-svg](https://www.npmjs.com/package/react-native-svg) | Every icon and illustration: 160 live files, e.g. `components/SVG/RNVI/*`, `components/NoNetwork/*` | Yes, codegen | 15.15.4 (2026-03-18) → 15.15.5 (2026-05-11) | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-svg) | Not mocked | **KEEP.** RN 0.84 changed the `RCTImage` observer declarations, which "may affect dependent libraries such as react-native-svg" ([RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84)) |
| [react-native-webview](https://www.npmjs.com/package/react-native-webview) | Renders JS-built HTML documents (invoices, GST invoice, payment advice, invoice summary, receipt voucher, TCS/TDS month summary) and the two remote user-manual sites: 4 live files (§4) | Yes, codegen | 13.16.1 (2026-02-27) → 14.0.1 (2026-06-20), **major** | [true, turbo](https://reactnative.directory/api/libraries?search=react-native-webview) | **Not mocked.** Its TurboModule throws under Jest, so suites read navigator source instead ([docs/testing.md:226-229](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)) | **KEEP** |

- Relevant devDependencies:
  - `react-native-dotenv` ^3.4.11 inlines `.env.${APP_ENV}` into the bundle ([babel.config.js:6-15](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/babel.config.js)).
  - `babel-plugin-optional-require` ^0.3.1 and `@babel/plugin-transform-dynamic-import` (test env only).
  - `typescript` ^6.0.2; `tsconfig.json` includes only `**/*.ts, **/*.tsx`.
  - `@react-native-community/cli` 20.1.3 and `@react-native/*` 0.84.1 tooling — [package.json:64-88](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/package.json), [tsconfig.json](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/tsconfig.json)
- Candidate replacements, from the registry and directory on 2026-09-29:
  - `react-native-share` 12.3.1 (true, turbo) — [npm](https://www.npmjs.com/package/react-native-share), [RND](https://reactnative.directory/api/libraries?search=react-native-share)
  - `react-native-blob-util` 0.25.1 (2026-09-24; true) — [npm](https://www.npmjs.com/package/react-native-blob-util)
  - `react-native-pdf` 7.0.5 (true, turbo) — [npm](https://www.npmjs.com/package/react-native-pdf)
  - `@react-native-documents/viewer` 4.0.1 (true, turbo) — [npm](https://www.npmjs.com/package/@react-native-documents/viewer)
  - `react-native-print` 0.11.0 (2023-01-22; directory: **unmaintained**, newArchitecture false) — [RND](https://reactnative.directory/api/libraries?search=react-native-print)
  - `react-native-image-picker` 8.2.1 (2025-05-04; true, turbo) — [npm](https://www.npmjs.com/package/react-native-image-picker)
  - `react-native-permissions` 5.6.2 (true, turbo) — [npm](https://www.npmjs.com/package/react-native-permissions)
  - `react-native-vision-camera` 5.2.3 (new-arch-only, Nitro module) — [RND](https://reactnative.directory/api/libraries?search=react-native-vision-camera)
  - `dayjs` 1.11.23 and `date-fns` 4.4.0 — [dayjs](https://www.npmjs.com/package/dayjs), [date-fns](https://www.npmjs.com/package/date-fns)

### Inferences
- The six interop-layer packages (RNFB ×4, device-info, linear-gradient) are the app's most "legacy-shaped" native surface. They are the natural case studies for a course on Turbo Modules: two can be deleted or replaced cheaply (linear-gradient → svg; device-info → roughly 60 lines of native constants per platform); RNFB should just be upgraded.
- The two major upgrades waiting (gesture-handler 3.x, webview 14.x) and the RN 0.84 → 0.87 gap are independent risks. They should not be bundled into a native-module teaching change.

### Gaps
- Whether RNFB 26.x adopted `codegenConfig` / TurboModules was not checked. The directory reports the repo's current state, not 24.0.0's.
- Compatibility of gesture-handler 3.3.0, webview 14.0.1, reanimated 4.7.0 and worklets 0.13.0 with RN **0.84.1** specifically was not verified.
- For JS-only libraries the directory's `newArchitecture` flag means "no native code to assess", not "incompatible". Paper, stack and flash-list are therefore not New-Architecture risks.

## 3. Which dependencies are imported by nothing (or only by dead code), and which imports point at packages that are not installed?

### Takeaway
Only **`@react-navigation/stack`** is both imported by nothing and needed by nothing, so it is safe to remove. Three more have zero direct imports but are load-bearing: `react-native-screens`, `react-native-worklets` and `@react-native-firebase/app`. `react-native-html-to-pdf` is imported only in one live file that never calls it. Four more imports point at packages that are **not installed**, and they build only because every importing file is dead code. `prop-types` is used by 13 live files but is not declared.

### Cited Findings
- Import census on 2026-09-29 over `src/`, `App.js`, `index.js`, `gesture-handler.native.js` and `__tests__/`. These have **0 source and 0 test importers**: `@react-navigation/stack`, `react-native-screens`, `react-native-worklets`, `@react-native-firebase/app` — [src/](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/)
- No installed package depends on `@react-navigation/stack`. The only mention is in `react-native-screens@4.24.0`'s **devDependencies** (`^5.10.0`), and `yarn.lock` has the single app-level entry `"@react-navigation/stack@^7.8.9"` ([yarn.lock:2854-2856](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/yarn.lock)). The dependency is declared at [package.json:44](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/package.json).
- `react-native-worklets` is wired by configuration rather than imports:
  - `'react-native-worklets/plugin'` ([babel.config.js:22](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/babel.config.js));
  - the worklets Jest resolver ([jest.resolver.js:14-27](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/jest.resolver.js));
  - `pickFirst` of `libworklets.so` ([app/build.gradle:120-125](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build.gradle)).
- `@react-native-firebase/app` is used natively: `import FirebaseCore` and `FirebaseApp.configure()` ([AppDelegate.swift:5,16](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/AppDelegate.swift)), and the three other RNFB packages sit on it.
- `react-native-html-to-pdf`: the only live importer is `screens/Common/Reports/TcsTds/Render/index.js`. It imports the module at line 5, and the component (lines 10-54) never references `RNHTMLtoPDF`. The same file also imports `Alert`, `Platform`, `Pressable` and `FAB` without using them. The other three importers are **dead**: `components/Download/RNhtmlpdf.js`, `components/Download/invoiceHTML/ShowInvoice.js`, `components/Download/invoiceHTML/index.js` — [TcsTds/Render/index.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/Reports/TcsTds/Render/index.js)
- **Phantom imports** (absent from `node_modules` on 2026-09-29), each only in an unreachable file:
  - `react-native-code-push`: `components/VersionInfo/index.js:25`, `screens/Common/Settings/Codepush.js:24`, `screens/Login/AuthNavigator/BetaUser.js:12`;
  - `react-native-image-picker` and `react-native-permissions`: `components/ImagePicker/index.js`;
  - `rn-fetch-blob`: `components/Download/Invoice.js:1`.
  - Source: [src/components/ImagePicker](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/ImagePicker/index.js), [Download/Invoice.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Download/Invoice.js)
- Jest keeps `{ virtual: true }` mocks for `react-native-image-picker` and `react-native-permissions`, commented "confirmed team decision 2026-07-05: keep them stubbed, do not install" ([jest.setup.js:245-256](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/jest.setup.js)). The runbook repeats it: "do NOT 'fix' these by installing them" ([docs/testing.md:80-85](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)).
- `prop-types` 15.8.1 is present only as a transitive install but is imported by 13 live files, e.g. `components/Calender/Calendar.js`, `components/Input/BaseInput.js` — [Calendar.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Calender/Calendar.js)
- The 75 dead source files by folder: `src/screens/Common` 18, `src/components/SVG` 9, `src/screens/Dealer` 6, `src/components/Download` 4, `src/components/Input` 4, `src/components/{DatePicker,Pickers,Search}` 3 each, plus 1-2 each in about 20 other folders. This includes `components/ImagePicker`, `components/VersionInfo`, `components/Calender/Example.js`, `screens/Login/AuthNavigator/BetaUser.js` and `src/notes/Testing` (static walk, 2026-09-29) — [src/](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/)

### Inferences
- **Remove `@react-navigation/stack`.** Evidence: no importer, no dependent package. Risk: essentially none. Check with `yarn test` plus a Metro release bundle for both platforms.
- **Remove `react-native-html-to-pdf`.** Delete the unused import (and the unused `Alert/Platform/Pressable/FAB` imports) in `TcsTds/Render/index.js`, `yarn remove`, then `pod install`. Evidence: no call site in live code. Risk: none at runtime today, and no test imports it. The three dead `Download/*` files would stop resolving, so delete them in the same PR.
- **Dead-code sweep.** Deleting the five phantom-importing files would let Jest drop the two virtual mocks. That reverses the recorded 2026-07-05 team decision, so it needs the user's verdict and cannot be a silent cleanup.
- **`prop-types`.** Declare it in `package.json` or remove the PropTypes usages. Today it survives only because another package hoists it.

### Gaps
- The 75 dead files were counted but not reviewed one by one; some may be intentional parking (e.g., demo screens).

## 4. What do `moment`, `react-native-webview` and `react-native-html-to-pdf` actually do here, and could `moment` be replaced by a small helper?

### Takeaway
- **moment** does plain Gregorian arithmetic (start/end of day, month and week; ± days, weeks and months; `YYYY-MM-DD`; days in month) in 7 live v1 files. The house already writes moment-free, Intl-free date helpers, so a small helper module can replace it. First pin today's behaviour, because moment uses **device-local** time while the v2 helpers are **IST**.
- **WebView** displays JS-generated HTML (invoices, receipts, the TCS/TDS summary) and two remote manual websites.
- **html-to-pdf** produces **nothing** in the live app. As of 2026-09-29 there is no PDF export, save, share or print anywhere in live code. The brief's "invoices rendered HTML→PDF" describes dead code.

### Cited Findings
- **moment, live call sites:**
  - `screens/Common/DailySummary/index.js:20-21` and `screens/Common/Reports/DailyReport/index.js:67-68`: `new Date(moment().startOf('day'))` / `endOf('day')` (v1 day bounds).
  - `screens/Dealer/NewVoucher/index.js:52-55` and `screens/Customer/NewPayAck/index.js:75-78`: a **module-scope** `lastDayPrevMonth = moment(new Date()).subtract(1, 'months').endOf('month')`, commented "static per app session".
  - `screens/Dealer/ProductDates/index.js:98-110,218-219,255-286,416-461` and `screens/Common/Products/components/ProductDates.js:81-120,266-283,340`: the rate calendar — month start/end formatted `YYYY-MM-DD` for the query, a ±30-day window, today/tomorrow comparison, and walking `rate_msts` with `isSameOrBefore(d, 'day')`.
  - `components/Calender/Calendar.js`: `startOf('month').day()`, `daysInMonth()`, `add/subtract` month and week, `isoWeekday`, `set('month')`, `date()`.
  - `components/Calender/Example.js` is dead.
  - Sources: [NewVoucher](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Dealer/NewVoucher/index.js), [NewPayAck](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Customer/NewPayAck/index.js), [ProductDates (dealer)](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Dealer/ProductDates/index.js), [ProductDates (common)](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/Products/components/ProductDates.js), [Calendar.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Calender/Calendar.js), [DailySummary v1](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/DailySummary/index.js), [DailyReport](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/Reports/DailyReport/index.js)
- No test file imports `moment` (census, 2026-09-29).
- The house's own helpers state their rule: "IST is fixed +05:30 arithmetic: no `Intl`, moment or local-time getter" ([src/helpers/DateRange/window.js:5](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/helpers/DateRange/window.js)). Siblings are `helpers/DateRange/format.js` and `helpers/DailySummary/format.js`, and a `src/utils/Dates` suite pins financial-year boundaries ([vault TDD guide §1](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/obsidian-notes/content/vsyst-technologies/docs/oms_app/tdd-testing-guide.md)).
- Moment's own docs call it "a legacy project, now in maintenance mode" and say "in most cases, you should not choose Moment for new projects" ([Moment.js docs, project status](https://momentjs.com/docs/)). npm latest 2.31.0 was published 2026-09-15 ([npm](https://www.npmjs.com/package/moment)).
- **WebView, all four live uses:**
  - **Invoice documents:** `screens/Common/_Invoice_/Render.js:5-11,75,92-94` builds HTML with `helpers/Download/invoiceHTML/{htmlInvoice,detailPInv,htmlPaymentAdvice,xlsxInvSummary}` or `helpers/Download/gstInvHTML`, then renders `<WebView originWhitelist={['*']} source={{ html }} />` ([_Invoice_/Render.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/_Invoice_/Render.js)).
  - **Receipt voucher:** `screens/Common/_Voucher_/HTML/Render.js:5-6,35-37` ([Voucher Render](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/_Voucher_/HTML/Render.js)).
  - **TCS/TDS month summary:** an "Excel"-style HTML table via `xlsxTCSTDS_month_Summary`, `TcsTds/Render/index.js:19-22,46-49`, which also reads `Dimensions.get('window')` at module scope (line 4) — a pattern AI.md forbids for new code ([AI.md:77-80](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)).
  - **Help:** `screens/Common/Help/index.js:12-13` defines `PDFURL = 'https://www.manual.vsyst.in'` and `PDFDealerURL = 'https://dealer.manual.vsyst.in'`, loaded as `source={{ uri }}` in a Paper `Modal` (lines 16-44, 130, 154). These are remote websites despite the constant names ([Help/index.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/Help/index.js)).
- **No live sharing, printing or saving.** No live file imports `Share` from `react-native` (census of named `react-native` imports in live files). `Share.share` appears only in commented-out code in the dead `components/Download/invoiceHTML/ShowInvoice.js:288-344` ([ShowInvoice.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Download/invoiceHTML/ShowInvoice.js)).
- **What the dead PDF code used to do:**
  - `RNhtmlpdf.js:10-16`: `RNHTMLtoPDF.convert({fileName:'test', directory:'Documents'})`, then `Alert.alert(file.filePath)`.
  - `invoiceHTML/index.js:31-37`: `fileName: INVOICE-${invNumber}`, `directory: 'Documents'`, then an alert with the path.
  - `ShowInvoice.js:98-118`: the same, with "Downloaded" / "Can't Download in this device" alerts; a commented variant used `directory: 'Download'` and `Share.share`.
  - `components/Download/Invoice.js:24-73`: downloaded a server PDF with `rn-fetch-blob` into `DocumentDir` through Android's DownloadManager, opened it with `RNFetchBlob.ios.openDocument` / `android.actionViewIntent(path, 'application/pdf')`, after requesting `WRITE_EXTERNAL_STORAGE`.
  - Sources: [RNhtmlpdf.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Download/RNhtmlpdf.js), [invoiceHTML/index.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Download/invoiceHTML/index.js), [Download/Invoice.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/components/Download/Invoice.js)
- `react-native-webview` is not mocked in Jest; its TurboModule throws there ([docs/testing.md:226-229](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)).

### Inferences
- **Replacing moment** (evidence: 7 live files, a fixed operation set, no tests). Build about 8-10 pure functions next to the existing date helpers:
  - `startOfLocalDay` / `endOfLocalDay`, `startOfMonth` / `endOfMonth`, `addDays` / `addMonths` / `addWeeks`, `toYmd`, `daysInMonth`, `isoWeekday`, `isSameOrBeforeDay`, `endOfPreviousMonth`.
  - `Intl` is **not** needed: the only format is `YYYY-MM-DD`, and the house deliberately avoids `Intl`.
  - Order of work: Tier 1 characterisation tests that pin moment's current answers (including month-end edge cases such as 31 Mar − 1 month), then swap call sites file by file, with a mutation smoke per helper.
  - Risk: untested v1 flows (rate calendar, payment-date bounds). Any accidental switch from device-local to IST semantics changes behaviour on devices whose time zone is not IST.
- **Latent bug worth pinning while there:** `lastDayPrevMonth` in NewVoucher and NewPayAck is computed once at import. An app session that runs across midnight on the 1st keeps using the month before last.
- **Product gap:** dealers can view an invoice but cannot share or print it from the app, and earlier code shows that was once intended. This is the strongest candidate for a small in-house native module. Suggested shape: HTML → PDF file → share sheet / print dialog, which would also retire `react-native-html-to-pdf`.

### Gaps
- Whether the API can already serve invoice PDFs (which would make on-device PDF generation unnecessary) was not checked. That lives in the API repo.
- Android WebView cannot render a PDF by URL, unlike iOS WKWebView. The Help screen loads websites, not PDFs, so it is unaffected, but I did not verify what those sites serve.

## 5. Is CodePush still wired (Microsoft retired it in 2025), and what other vestiges remain?

### Takeaway
CodePush is **not wired**: the package is not installed, and all three files that import it are dead. Two vestiges remain. First, **four CodePush deployment-key variables** in every env file; the live `src/constants/system.js` imports them, so react-native-dotenv inlines their values into the shipped JS bundle. Second, commented-out imports. Microsoft retired App Center, including CodePush, on 2025-03-31, and the RN client library is archived with no New Architecture support. The other vestiges are listed below.

### Cited Findings
- **The dead CodePush files:**
  - `src/screens/Common/Settings/Codepush.js` (530 lines) imports `codePush, { LocalPackage } from 'react-native-code-push'` (line 24) and the `CODEPUSH_*_DEPLOYMENT_KEY_*` constants (lines 31-35).
  - `components/VersionInfo/index.js` (632 lines, line 25) and `screens/Login/AuthNavigator/BetaUser.js` (389 lines, line 12) do the same.
  - All three are unreachable from `index.js`, and the package is not in `node_modules` — [Codepush.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Common/Settings/Codepush.js)
- `App.js:8` (`// import withCodePush from './codepush';`) and `App.js:31` (`// export default withCodePush(App);`) are commented out, as are `components/Error/ErrorBoundary.js:6` and `components/NoNetwork/Undraw.js:7` — [App.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/App.js)
- **The live leak:** `src/constants/system.js:1-16` imports `CODEPUSH_STAGING_KEY_IOS`, `CODEPUSH_PRODUCTION_KEY_IOS`, `CODEPUSH_STAGING_KEY_ANDROID` and `CODEPUSH_PRODUCTION_KEY_ANDROID` from `@env` and re-exports them. The file is live because `helpers/OneSignal/index.js` and `store/apis/createApi.js` import it ([system.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/constants/system.js)).
- All five env files declare the four `CODEPUSH_*` names; names checked, values not read ([.env.example](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/.env.example), [.env.ci](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/.env.ci)). `react-native-dotenv` runs with `safe: true, allowUndefined: false`, so every imported name must exist in every env file ([babel.config.js:6-15](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/babel.config.js); [AI.md:227-237](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)).
- The repo's release checklist item 8, "CodePush keys present but CodePush disabled", has status "⏳ Deferred" ([PRODUCTION_RELEASE_CHECKLIST.md:269-285](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/todos/PRODUCTION_RELEASE_CHECKLIST.md)).
- **Status outside the repo:**
  - "Visual Studio App Center was retired on March 31, 2025, except for its Analytics and Diagnostics features", CodePush included; a standalone `code-push-server` was published ([Microsoft Learn: App Center retirement](https://learn.microsoft.com/en-us/appcenter/retirement), [microsoft/code-push-server](https://github.com/microsoft/code-push-server)).
  - The RN Directory marks `react-native-code-push` **archived**, **unmaintained** and newArchitecture false, noting "Microsoft no longer maintains this library and has no plans to add New Architect[ure support]". It lists alternatives `@appzung/react-native-code-push`, `@bravemobile/react-native-code-push` and `expo-updates` ([RN Directory API](https://reactnative.directory/api/libraries?search=react-native-code-push)).
  - npm latest is 9.0.1, published 2024-12-19 ([npm](https://www.npmjs.com/package/react-native-code-push)).
- **Remote Config** was removed in 2026-09 ("tasks_17"). A test pins its absence by reading `package.json`, `jest.setup.js` and `Podfile.lock`, while the `FirebaseRemoteConfig` and `FirebaseABTesting` pods stay because Performance depends on them ([firebaseModules.config.test.js:1-23](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/utils/__tests__/firebaseModules.config.test.js); [Podfile:25-33](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile)).
- **Other vestiges:**
  - (a) `Login.js:680,727-750` renders a live `BetaUserComponent`. It is **not** CodePush: after taps it alerts version, build, OS and model, plus `PROJ_ENV` and `API_URL` when not in production ([Login.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/screens/Login/AuthNavigator/Login.js)).
  - (b) The AsyncStorage key `IS_BETA_USER` is still read and written (3+3 call sites in `src`, including dead files).
  - (c) `jscFlavor` / the JSC fallback remains in `app/build.gradle:77,132-136` with `hermesEnabled=true`.
  - (d) The Google OAuth reversed-client-id URL scheme sits in `Info.plist:25-35`, but no `src` file uses Google Sign-In (§8).
  - (e) The NSE file keeps the Xcode template as a commented block (`NotificationService.swift:8-35`).
  - (f) Checklist item 1 still says `crashlytics_debug_enabled: true` / `crashlytics_disable_auto_disabler: true`, but `firebase.json` now has both `false`, so the checklist is stale ([firebase.json](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/firebase.json); [checklist:18-30](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/todos/PRODUCTION_RELEASE_CHECKLIST.md)).

### Inferences
- OTA updates are unavailable today. Re-adding them means choosing a maintained fork plus a self-hosted server or `expo-updates`; the retired library is not an option.
- Removing the CodePush vestige means three changes in one PR, each covered by the env rule in AI.md:
  1. Delete the 4 names from all 5 env files, including the tracked `.env.ci`, or the CI `Test` job fails.
  2. Delete `system.js:1-16` exports.
  3. Delete the dead importers.
  - Risk: a missing name makes Babel throw at transform time; the full Jest run catches it.

### Gaps
- The env values were deliberately not read, so I cannot say whether the four inlined keys are empty strings or real deployment keys.

## 6. Why does `Info.plist` carry three `NSLocation*UsageDescription` strings when no `src` file uses geolocation?

### Takeaway
They are **not dead weight** but they are **badly worded**. The OneSignal iOS SDK bundled by `react-native-onesignal` includes its **Location** module. That binary references `requestAlwaysAuthorization` / `requestWhenInUseAuthorization`, which trips Apple's ITMS-90683 "missing purpose string" check even though the app never asks for location. The strings were added on 2021-03-15 for exactly that reason ("NSLocaiton in iOS was compulsory"). The risk is the vague wording, not their presence. The checklist's proposed replacement ("delivery checkpoints") would describe a feature that does not exist.

### Cited Findings
- `Info.plist:49-54` sets `NSLocationAlwaysAndWhenInUseUsageDescription`, `NSLocationAlwaysUsageDescription` and `NSLocationWhenInUseUsageDescription`, all to "$(PRODUCT_NAME) needs Location access for good user experience!" ([Info.plist](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/Info.plist)).
- `git log -S NSLocationAlwaysUsageDescription` on that file shows `de7b6cfa` on 2021-03-15, "NSLocaiton in iOS was compulsory, …", then touches in `a3dc495c` (2025-04-15) and `679d73f4` (2025-09-07) — [repo history](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/)
- No geolocation package is installed or imported (dependency census, §2). No live file requests location.
- The RN SDK's podspec pins `s.dependency 'OneSignalXCFramework', '5.5.0'`. `Podfile.lock` resolves that to `OneSignalXCFramework/OneSignalComplete`, which includes `OneSignalLocation` and `OneSignalInAppMessages`, and the app embeds `OneSignalLocation.framework` — [react-native-onesignal podspec](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/react-native-onesignal/), [Podfile.lock:192-211](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile.lock)
- `strings` on the embedded `OneSignalLocation.framework/OneSignalLocation` (ios-arm64) finds: `requestAlwaysAuthorization`, `requestWhenInUseAuthorization`, `startUpdatingLocation`, the three `NSLocation…UsageDescription` keys, and the message "Include a privacy NSLocationAlwaysUsageDescription or NSLocationWhenInUseUsageDescription in your info.plist to request location permissions" — [OneSignal_Location xcframework](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Pods/OneSignalXCFramework/iOS_SDK/OneSignalSDK/OneSignal_Location/)
- `react-native-device-info` calls only `CLLocationManager` class-level status methods (`locationServicesEnabled`, `significantLocationChangeMonitoringAvailable`, `headingAvailable`, `isRangingAvailable`) at `RNDeviceInfo.m:866,995-998` and never requests authorization ([RNDeviceInfo.m](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/react-native-device-info/ios/RNDeviceInfo/RNDeviceInfo.m)).
- OneSignal's issue trackers record App Store Connect **ITMS-90683** warnings and rejections for missing location purpose strings in apps that do not use location, even with location sharing off. The issues span iOS, React Native, Flutter and Cordova. Workaround: add the strings ([react-native-onesignal#1298](https://github.com/OneSignal/react-native-onesignal/issues/1298), [OneSignal-iOS-SDK#1242](https://github.com/OneSignal/OneSignal-iOS-SDK/issues/1242)).
- The Android side has **no** location permission in the merged release manifest; OneSignal's Android location module is not pulled (§7).
- Repo checklist item 6 calls the strings "too vague" (status "⏳ Deferred") and proposes "Dzzlo OMS uses your location to capture delivery checkpoints and verify on-site visits" ([PRODUCTION_RELEASE_CHECKLIST.md:196-218](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/todos/PRODUCTION_RELEASE_CHECKLIST.md)).

### Inferences
- **Keep the keys but make the text truthful.** The strings are never shown today, because nothing asks for location. The proposed "delivery checkpoints" text would describe a feature the app lacks, which is itself an App Review risk. `NSLocationAlwaysUsageDescription` is only for very old iOS versions and can probably go, but test against the ITMS check before removing any key.
- The strings only become user-facing if a real location feature ships (e.g., delivery or vehicle tracking; §10). They would then need a specific purpose, and Android would need `ACCESS_*_LOCATION` added deliberately.
- A config-pin test (the house `*.config.test.js` pattern, §9) could assert that the three keys stay present while OneSignalLocation is linked, so a well-meaning cleanup cannot trigger ITMS-90683.

### Gaps
- Whether `react-native-onesignal` 5.x can exclude the Location subspec (to drop the strings entirely) was not verified; the podspec pins the full XCFramework.
- No Apple primary source on ITMS-90683 wording was fetched; the evidence is OneSignal's issue trackers plus the binary's strings.

## 7. Android: what does the build configure, which permissions arrive by manifest merging, and are edge-to-edge, predictive back and 16 KB pages handled?

### Takeaway
- **Native code:** the Android app is the stock RN 0.84 template. `MainApplication.kt` and `MainActivity.kt` have no custom native code except react-native-screens' `onCreate(null)`.
- **Permissions:** the app declares only `INTERNET`. Manifest merging adds 30 more, mainly from OneSignal (push plus 16 launcher-badge permissions), Firebase Analytics (**AD_ID** and AdServices), NetInfo and WorkManager.
- **Build:** R8/ProGuard is **off**, all four ABIs ship in one universal APK (about 107 MB), and the release APK built on 2026-09-29 is **16 KB-aligned**.
- **Edge-to-edge:** `edgeToEdgeEnabled=false`, yet with targetSdk 36 Android 16 devices force edge-to-edge regardless.
- **Predictive back:** predictive back animations are on by default for targetSdk 36 on Android 16. There is no `enableOnBackInvokedCallback` opt-out, and the app uses `BackHandler` in 5 live files.

### Cited Findings
- **Build files:**
  - `app/build.gradle` applies `com.android.application`, `org.jetbrains.kotlin.android`, `com.facebook.react`, `com.google.gms.google-services`, `com.google.firebase.crashlytics` and `com.google.firebase.firebase-perf` (lines 1-7).
  - Its `react { }` block only calls `autolinkLibrariesWithApp()` (lines 13-59, with 58 being the call).
  - `def enableProguardInReleaseBuilds = false` (64) → `minifyEnabled enableProguardInReleaseBuilds` (116), with `proguard-android.txt` plus an empty `proguard-rules.pro` (117).
  - `namespace` and `applicationId` are `in.vsyst.dzzlooms` (84-86); `versionCode 104`, `versionName "1.79"` (89-90).
  - Release signing reads `MYAPP_UPLOAD_*` Gradle properties (99-106).
  - `packagingOptions` sets `pickFirst` on `libworklets.so` for arm64-v8a and armeabi-v7a (120-125).
  - Dependencies: `react-android`, plus `hermes-android` when `hermesEnabled` (128-137).
  - No `abiFilters`, `splits` or `bundle { }` config.
  - Sources: [app/build.gradle](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build.gradle), [proguard-rules.pro](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/proguard-rules.pro)
- `gradle.properties` sets: `org.gradle.jvmargs=-Xmx2048m …` (13), `reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64` (28), `newArchEnabled=true` (35), `hermesEnabled=true` (39), `edgeToEdgeEnabled=false` (44), upload-key properties (46-49) — [gradle.properties](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/gradle.properties)
- `settings.gradle` uses `com.facebook.react.settings` with `autolinkLibrariesFromCommand()` ([settings.gradle:1-6](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/settings.gradle)). The root build adds classpaths `google-services:4.4.4`, `firebase-crashlytics-gradle:3.0.6` and `perf-plugin:2.0.2`, plus an extra Maven repo for async-storage v3 ([android/build.gradle:14-31](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/build.gradle)).
- **Native code (template only):**
  - `MainApplication.kt` uses `getDefaultReactHost(context, PackageList(this).packages.apply { /* add(MyReactNativePackage()) */ })` plus `loadReactNative(this)` ([MainApplication.kt:10-27](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/main/java/in/vsyst/dzzlooms/MainApplication.kt)).
  - `MainActivity.kt` returns `DefaultReactActivityDelegate(this, mainComponentName, fabricEnabled)` and overrides `onCreate` with `super.onCreate(null)` for react-native-screens ([MainActivity.kt:10-31](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/main/java/in/vsyst/dzzlooms/MainActivity.kt)).
  - There are only 2 Kotlin files in the app module, and no `src/test` or `src/androidTest` source sets.
- **Declared manifest:**
  - Declares only `android.permission.INTERNET` (line 3).
  - `<application>`: `android:allowBackup="false"`, theme `@style/AppTheme`, `android:usesCleartextTraffic="${usesCleartextTraffic}"`, `supportsRtl`.
  - One `MainActivity`: `screenOrientation="portrait"`, `configChanges="keyboard|keyboardHidden|orientation|screenLayout|screenSize|smallestScreenSize|uiMode"`, `launchMode="singleTask"`, `windowSoftInputMode="adjustResize"`, `exported="true"`, a MAIN/LAUNCHER filter only.
  - No deep-link or App Link intent filters, no `<queries>`, no `enableOnBackInvokedCallback`, no `localeConfig`.
  - The debug overlay sets `usesCleartextTraffic="true"`.
  - Sources: [AndroidManifest.xml](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/main/AndroidManifest.xml), [debug AndroidManifest.xml](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/debug/AndroidManifest.xml)
- The theme `AppTheme` (`Theme.AppCompat.DayNight.NoActionBar`) points `android:textViewStyle` at `AppTextView` with `android:useBoundsForWidth=false` (API 35+). This turns off Android 15's bounds-based line breaking so Devanagari measures the way Yoga does. It is pinned by `src/i18n/__tests__/androidText.config.test.js` ([styles.xml:4-32](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/main/res/values/styles.xml)).
- **Merged release manifest** (`app/build/intermediates/merged_manifest/release/processReleaseMainManifest/AndroidManifest.xml`, built 2026-09-29 11:11): `versionCode 104`, `minSdk 24` / `targetSdk 36`, `extractNativeLibs="false"`, `usesCleartextTraffic="false"`. Permission origins per the merger blame report ([merged manifest](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build/intermediates/merged_manifest/release/processReleaseMainManifest/AndroidManifest.xml), [manifest-merger-release-report.txt](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build/outputs/logs/manifest-merger-release-report.txt)):
  - `INTERNET`: app manifest, also RNFB analytics.
  - `ACCESS_NETWORK_STATE`, `ACCESS_WIFI_STATE`: `:react-native-community_netinfo` (and RNFB analytics).
  - `WAKE_LOCK`: RNFB analytics and `com.onesignal:notifications:5.7.6`.
  - `${applicationId}.permission.C2D_MESSAGE`, `POST_NOTIFICATIONS`, `com.google.android.c2dm.permission.RECEIVE`, `VIBRATE`, `RECEIVE_BOOT_COMPLETED`: OneSignal notifications 5.7.6 (POST_NOTIFICATIONS and c2dm also from `firebase-messaging:25.0.1`; BOOT_COMPLETED also from `work-runtime:2.8.1`).
  - 16 launcher-badge permissions (Samsung, HTC, Sony, Apex, Solid, Huawei, ZUK `READ_APP_BADGE`, OPPO, EvMe): OneSignal notifications 5.7.6 (ShortcutBadger).
  - `BIND_GET_INSTALL_REFERRER_SERVICE`: `play-services-measurement:23.0.0`.
  - **`com.google.android.gms.permission.AD_ID`**: `play-services-measurement-impl/api:23.0.0`.
  - **`ACCESS_ADSERVICES_ATTRIBUTION`, `ACCESS_ADSERVICES_AD_ID`**: `play-services-measurement-api/sdk-api:23.0.0` (Firebase Analytics).
  - `FOREGROUND_SERVICE`: `androidx.work:work-runtime:2.8.1`.
  - `${applicationId}.DYNAMIC_RECEIVER_NOT_EXPORTED_PERMISSION`: `androidx.core:core:1.17.0`.
- **Merged components:**
  - OneSignal: FCM broadcast receiver; HMS messaging service and `NotificationOpenedActivityHMS` (Huawei); dismiss, boot and upgrade receivers; `SyncJobService`; `PermissionsActivity`.
  - Firebase: messaging service, Crashlytics and App init providers, sessions service, measurement receivers and services.
  - WorkManager and Room services.
  - `com.google.android.gms.auth.api.signin.internal.SignInHubActivity` from `play-services-auth:21.5.0`, which `@react-native-firebase/app` depends on ([RNFB app build.gradle](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/@react-native-firebase/app/android/build.gradle)).
  - `RNCWebViewFileProvider` and `<queries>` for `org.chromium.intent.action.PAY / IS_READY_TO_PAY / UPDATE_PAYMENT_DETAILS`, both from `:react-native-webview` (blame lines 667-688).
- **16 KB pages:**
  - The release APK `android/app/build/outputs/apk/release/app-release.apk` (106,793,519 bytes, 2026-09-29 11:11:57) contains 23 `.so` files × 4 ABIs.
  - Parsing the 23 arm64-v8a libraries' ELF program headers gives PT_LOAD `p_align = 16384` for **all 23**.
  - All are stored uncompressed at **16 KB-aligned zip offsets**.
  - Largest libraries: `libreactnative.so` 6.2 MB, `libhermesvm.so` 2.5 MB, `libsqliteJni.so` 1.9 MB (async-storage v3), `libappmodules.so` 1.8 MB, `libreanimated.so` 1.4 MB, `libcrashlytics-common.so` 0.9 MB.
  - Source: [app-release.apk](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build/outputs/apk/release/app-release.apk)
- Google Play rule: "starting November 1st, 2025, all new apps and updates to existing apps submitted to Google Play and targeting Android 15+ devices must support 16 KB page sizes" ([Android Developers Blog, 2025-05](https://android-developers.googleblog.com/2025/05/prepare-play-apps-for-devices-with-16kb-page-size.html); [Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes)).
- **Android 16 (API 36) behaviour for apps targeting it** ([Android 16 behavior changes](https://developer.android.com/about/versions/16/behavior-changes-16)):
  - `windowOptOutEdgeToEdgeEnforcement` "is deprecated and disabled, and your app can't opt-out of going edge-to-edge".
  - "the predictive back system animations (back-to-home, cross-task, and cross-activity) are enabled by default", "`onBackPressed` is not called and `KeyEvent.KEYCODE_BACK` is not dispatched anymore", with a temporary opt-out `android:enableOnBackInvokedCallback="false"`.
  - "orientation, resizability, and aspect ratio restrictions no longer apply on displays with smallest width >= 600dp". `screenOrientation`, `resizableActivity`, `minAspectRatio`, `maxAspectRatio` and `setRequestedOrientation()` are ignored. Exceptions: games, a user opt-in, and screens < sw600dp. A temporary opt-out is `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`, which "won't apply when targeting API level 37".
- Live `BackHandler` users: 5 files, including `screens/{Dealer,Common,Customer}/Orders/index.js` and `hooks/useBottomSheetBackHandler.js` (census of `react-native` named imports) — [useBottomSheetBackHandler.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/hooks/useBottomSheetBackHandler.js)
- `Linking.canOpenURL('https://…')` is used for the "update app" paths in `helpers/OneSignal/index.js:66-68`, `components/Error/ErrorMessage.js:28-37` and `components/Error/index.js:86-87`. React Native's docs say: "When targeting Android 11 (SDK 30) you must specify the intents for the schemes you want to handle in AndroidManifest.xml", and "The Promise will reject on Android … if you didn't specify the relevant intent queries" ([RN Linking docs](https://reactnative.dev/docs/linking)). The merged manifest has no `https` VIEW query.

### Inferences
- **Edge-to-edge is split by OS version.** On Android 16 devices the app is edge-to-edge whatever `edgeToEdgeEnabled=false` says. On older Android it is not. v2 screens use `SafeAreaProvider` / `Screen edges`, but v1 screens should be checked on an Android 16 device for content under the status and navigation bars.
- **Predictive back needs a device check.** The 5 `BackHandler` sites (Orders screens, bottom-sheet back handling) are exactly what Android 16's change touches. Do a one-time on-device test on Android 16 with gesture navigation. RN's own back integration is not documented here (see Gaps).
- **Portrait pin is ignored on large screens.** The `screenOrientation="portrait"` pin does nothing on sw ≥ 600 dp devices (unfolded Folds, tablets) with targetSdk 36. The opt-out stops working at API 37, so large-screen layout is required long-term.
- **The "update app" CTA is probably broken on Android 11+**, a likely silent bug: without a `<queries>` VIEW/https entry, `canOpenURL` rejects or returns false, so the `update_app` in-app-message button and the error-screen update link do nothing. No test covers it. The fix is a manifest `<queries>` block or skipping `canOpenURL` for `market://`. Pin it with a `*.config.test.js`.
- **Size and ads declarations.** A universal 4-ABI APK wastes about 3× native size. AAB delivery (README) or `abiFilters` would drop x86/x86_64 from phone installs. Firebase Analytics' AD_ID and AdServices permissions must be declared in Play's Data safety form, or removed if ads attribution is not wanted.

### Gaps
- How RN 0.84's `ReactActivity` routes back events under predictive back (OnBackPressedDispatcher vs `onBackPressed`) was not verified from RN sources.
- Project notes mention a "16 KB page size" compatibility dialog on an emulator **debug** build. The 2026-09-29 **release** APK checked here is aligned, so the debug-build finding was not re-examined.
- Play Console's current AAB requirement for this existing app was not checked; the scripts produce only APKs (§11).

## 8. iOS: which targets, capabilities, entitlements, URL schemes, background modes, permission strings, privacy manifest, fonts and linkage exist today?

### Takeaway
- **Targets:** two — the app `in.vsyst.dzzlooms` and a **OneSignal Notification Service Extension**.
- **Capabilities:** Push Notifications (`aps-environment`), an **App Group** (`group.in.vsyst.dzzlooms.onesignal`) shared only between app and NSE, and background mode `remote-notification`. No associated domains, universal links or custom app URL scheme.
- **Lifecycle:** Swift `AppDelegate` with RN 0.84's `RCTReactNativeFactory` and an in-file `SceneDelegate`.
- **Build settings:** deployment target 15.1 (= RN 0.84's minimum), iPhone and iPad, portrait-only, full-screen, Hermes, `RCT_REMOVE_LEGACY_ARCH=1`, prebuilt React core, static pods.
- **Privacy:** the app-level privacy manifest declares 4 required-reason APIs and no collected data.

### Cited Findings
- **Targets and build settings:**
  - Native targets: `dzzlo_oms_app` (`com.apple.product-type.application`) and `OneSignalNotificationServiceExtension` (`com.apple.product-type.app-extension`). There is no test target and no widget, App Clip or intent extension. One shared scheme, `dzzlo_oms_app.xcscheme`.
  - Bundle ids `in.vsyst.dzzlooms` and `in.vsyst.dzzlooms.OneSignalNotificationServiceExtension`.
  - `DEVELOPMENT_TEAM = YT955YZMZU`, `CODE_SIGN_STYLE = Automatic`.
  - `IPHONEOS_DEPLOYMENT_TARGET = 15.1`.
  - App `MARKETING_VERSION = 1.79`, `CURRENT_PROJECT_VERSION = 1` at HEAD (2 in the working tree); NSE `MARKETING_VERSION = 1.0`, `CURRENT_PROJECT_VERSION = 1`.
  - `TARGETED_DEVICE_FAMILY = "1,2"`, `SUPPORTS_MACCATALYST = NO`, `SWIFT_VERSION = 5.0`, `USE_HERMES = true`, `ENABLE_BITCODE = NO`, `INFOPLIST_KEY_LSApplicationCategoryType = "public.app-category.business"`.
  - Build phases: "Bundle React Native code and images", `[CP] Copy Pods Resources`, `[CP] Embed Pods Frameworks`, `[CP-User] [RNFB] Crashlytics Configuration`, `[CP-User] [RNFB] Core Configuration`, `[CP] Check Pods Manifest.lock` ×2.
  - Source: [project.pbxproj](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app.xcodeproj/project.pbxproj)
- `min_ios_version_supported` returns `'15.1'` in RN 0.84.1 ([react-native/scripts/cocoapods/helpers.rb:83-85](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/react-native/scripts/cocoapods/helpers.rb)). The Podfile uses `platform :ios, min_ios_version_supported` and raises every pod target below it, because "Xcode 27 rejects deployment targets below iOS 15" ([Podfile:8,60-69](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile)). Commit `b933119f` (2026-09-16) reads "build with Xcode 27 — adopt the UIScene life cycle, lift pods to iOS 15".
- `AppDelegate.swift` imports `React`, `React_RCTAppDelegate`, `ReactAppDependencyProvider` and `FirebaseCore`. It calls `FirebaseApp.configure()`, builds `RCTReactNativeFactory(delegate:)` with `RCTAppDependencyProvider()`, and returns a `UISceneConfiguration` whose `delegateClass = SceneDelegate.self`. `SceneDelegate` creates the `UIWindow` and calls `factory.startReactNative(withModuleName: "dzzlo_oms_app", in: window, launchOptions: nil)`. `ReactNativeDelegate.bundleURL()` returns Metro in DEBUG and `main.jsbundle` otherwise. There is **no** push or deep-link delegate code; OneSignal handles push itself ([AppDelegate.swift:1-72](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/AppDelegate.swift)).
- **Entitlements:**
  - App: `aps-environment = development` and `com.apple.security.application-groups = [group.in.vsyst.dzzlooms.onesignal]` ([dzzlo_oms_app.entitlements](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/dzzlo_oms_app.entitlements)).
  - NSE: the same app group only ([NSE entitlements](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/OneSignalNotificationServiceExtension/OneSignalNotificationServiceExtension.entitlements)).
  - No associated-domains, keychain-sharing, Sign in with Apple, iCloud or other entitlements.
- **NSE:**
  - `NotificationService: UNNotificationServiceExtension` forwards to `OneSignalExtension.didReceiveNotificationExtensionRequest` and `serviceExtensionTimeWillExpireRequest`. It only runs for `mutable_content` pushes, and it is where rich media and confirmed delivery happen ([NotificationService.swift:37-68](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/OneSignalNotificationServiceExtension/NotificationService.swift)).
  - Its `Info.plist` sets `NSExtensionPointIdentifier = com.apple.usernotifications.service` (plus a stray `RCTNewArchEnabled`).
  - The Podfile gives it its own target: `pod 'OneSignalXCFramework', '>= 5.0.0', '< 6.0'` ([Podfile:73-75](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Podfile)).
- **`Info.plist`** (working tree) — [Info.plist](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/Info.plist):
  - `CFBundleURLTypes` has **one** scheme, `com.googleusercontent.apps.<Google OAuth client id, withheld>` (25-35).
  - `ITSAppUsesNonExemptEncryption = false`.
  - ATS: `NSAllowsArbitraryLoads = false`, `NSAllowsLocalNetworking = true`.
  - The three location strings (49-54, §6); `RCTNewArchEnabled = true`.
  - `UIAppFonts` = `RobotoCondensed_Regular.ttf`, `RCL_Light.ttf`, `OpenSans_Regular.ttf`.
  - Single-scene manifest with `$(PRODUCT_MODULE_NAME).SceneDelegate`.
  - `UIBackgroundModes = [remote-notification]`; `UIRequiredDeviceCapabilities = [arm64]`; `UIRequiresFullScreen = true`; `UISupportedInterfaceOrientations = [Portrait]`.
  - `UIViewControllerBasedStatusBarAppearance = false`; `CADisableMinimumFrameDurationOnPhone = true`.
  - No camera, photo, contacts, microphone or Face ID strings.
- **Privacy manifest:** `PrivacyInfo.xcprivacy` declares `NSPrivacyAccessedAPICategoryFileTimestamp` (C617.1), `…UserDefaults` (CA92.1, 1C8F.1, C56D.1), `…SystemBootTime` (35F9.1) and `…DiskSpace` (85F4.1), with `NSPrivacyCollectedDataTypes = []` and `NSPrivacyTracking = false` ([PrivacyInfo.xcprivacy](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app/PrivacyInfo.xcprivacy)). These pods ship their own `PrivacyInfo.xcprivacy`: FirebaseABTesting, FirebaseCore, FirebaseCoreExtension, FirebaseCoreInternal, FirebaseCrashlytics, FirebaseInstallations, FirebaseRemoteConfig, GoogleDataTransport, GoogleUtilities, nanopb, OneSignalXCFramework, PromisesObjC, PromisesSwift, ReactNativeDependencies (file search in `ios/Pods`, 2026-09-29) — [ios/Pods](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/Pods/)
- **Fonts:** the three TTFs sit in `ios/` (project resources) and in `android/app/src/main/assets/fonts/`. `react-native.config.js` declares `assets: ['./src/assets/fonts/']` ([react-native.config.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/react-native.config.js)).
- **Linkage and Swift:**
  - Static pods with prebuilt RN core (§1).
  - RN 0.84 "ships precompiled binaries on iOS by default"; disable with `RCT_USE_PREBUILT_RNCORE=0` ([RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84)).
  - The README's dSYM note says to reinstall pods with `RCT_USE_RN_DEP=0 RCT_USE_PREBUILT_RNCORE=0` to silence "Upload Symbols Failed" for the prebuilt frameworks ([README.md:290](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/README.md)).
  - The RN docs' app-level Turbo Native Module path is Objective-C++ (`.mm`), registered through `codegenConfig.ios.modulesProvider`; the page does not mention a Swift implementation path ([RN: Turbo Native Modules](https://reactnative.dev/docs/turbo-native-modules-introduction)).

### Inferences
- **A new native module or target has room.** Swift is already compiled in the app target (AppDelegate). An in-house module's iOS side would follow the documented ObjC++ `.mm` entry point, with Swift behind it if wanted.
- **Linkage is unlikely to block new extension targets.** Static pods remove the usual `use_frameworks!` duplicate-symbol and extension-linking traps. A widget or Live Activity target would get its own Podfile `target` block like the NSE, and would need its **own** App Group entry to share Daily Summary data with the app; today's group is OneSignal's. `OneSignalLiveActivities.framework` is already embedded, a head start if Live Activities are wanted.
- **App Store version warning (likely).** The NSE's `MARKETING_VERSION 1.0` differs from the app's 1.79. App Store Connect usually warns when an extension's short version does not match its parent app, so align it in the same release.
- **Google URL scheme looks vestigial.** The reversed-client-id scheme is used only by Google Sign-In, which no `src` file imports, so it can probably go. Confirm with Firebase settings first.
- **Privacy disclosure.** The app manifest's empty `NSPrivacyCollectedDataTypes` does not reflect the SDKs' collection (Analytics, Crashlytics, OneSignal). The App Store privacy label must cover it; the per-SDK manifests above supply part of that.

### Gaps
- Whether Xcode's App Store export rewrites `aps-environment` from the distribution profile was not verified here. The file says `development`, which is normal for Xcode-managed signing.
- My file search found no privacy manifest for `FirebaseAnalytics` / `GoogleAppMeasurement`, `FirebasePerformance` or `FirebaseSessions`. They may embed one inside the binary XCFrameworks; not verified.
- I did not open `LaunchScreen.storyboard` or the asset catalogs.

## 9. How are native modules mocked in Jest today, and what would a test-first in-house Turbo Module need in this repo?

### Takeaway
- **Mocks:** all native mocks live **inline in `jest.setup.js`**, with no `__mocks__` folder. They use the package's shipped mock where one exists (async-storage, device-info, netinfo, safe-area, gesture-handler, bottom-sheet, reanimated) and hand stubs otherwise (Firebase ×4, OneSignal, two virtual phantoms). WebView, html-to-pdf, linear-gradient, datetimepicker, svg and screens are not mocked.
- **Native-read precedent:** `src/i18n/deviceLocale.js` reads native modules through `NativeModules` / `TurboModuleRegistry.get` with fallbacks, and its test swaps fake modules in per test.
- **Config pins:** five `*.config.test.js` suites pin native configuration by reading `Info.plist`, `AndroidManifest.xml`, `styles.xml`, `MainApplication.kt`, Gradle files and `Podfile.lock` off disk.
- **What is missing:** there is **no `codegenConfig`, no `specs/` directory and no in-house native module**, and no native test targets on either platform. CI runs Jest only.

### Cited Findings
- **`jest.config.js`:**
  - `preset: 'react-native'` (2); `setupFiles: ['<rootDir>/jest.setup.js']` (3); `setupFilesAfterEnv: ['<rootDir>/jest.setup.after-env.js']` (5).
  - `resolver: '<rootDir>/jest.resolver.js'` (8), which composes the worklets resolver with RN's.
  - `transform` sends `^.+\.(js|mjs|ts|tsx)$` to `babel-jest` (13-18); `moduleNameMapper` pins `msw` / `msw/node` to CJS (22-25).
  - `transformIgnorePatterns: ['node_modules/(?!(react-native|@react-native|@react-navigation|@react-native-firebase|@react-native-community|@react-native-async-storage|react-native-.*|@gorhom|@shopify/flash-list|react-redux|immer|msw|@mswjs|@open-draft|rettime|until-async|is-node-process|outvariant|strict-event-emitter|headers-polyfill)/)']` (31-33).
  - Source: [jest.config.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/jest.config.js)
- **`jest.setup.js` mocks:**
  - `@react-native-firebase/app`, `analytics`, `crashlytics`, `perf`: hand stubs returning `jest.fn()`s (3-47).
  - async-storage: `require('@react-native-async-storage/async-storage/jest')` (52-54).
  - device-info: the package's `jest/react-native-device-info-mock` (55-57).
  - netinfo: `jest/netinfo-mock.js` (58-60).
  - RN's `useWindowDimensions`, patched by a test override (75-106).
  - The house `useKeyboardInset` (120-126) and `i18n/deviceLocale` override (135-143).
  - safe-area-context: its `jest/mock` (148-150).
  - gesture-handler: `jestSetup` (151).
  - `@gorhom/bottom-sheet`: the shipped mock, subclassed to draw the handle (157-218).
  - Reanimated: `setUpTests()` (221).
  - `react-native-onesignal`: a hand stub covering `initialize`, `login`, `Debug`, `Notifications`, `InAppMessages`, `User` (224-243).
  - Virtual `react-native-image-picker` and `react-native-permissions` (245-256).
  - Source: [jest.setup.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/jest.setup.js)
- The only `__mocks__` directory on disk is inside `.design-sync/web/node_modules/fbjs` (not part of the app) — [repo root](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/)
- `jest.setup.after-env.js` resets font-scale and language overrides after each test and clears ≥ 10 s timers at suite end ([jest.setup.after-env.js:18-36](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/jest.setup.after-env.js)).
- The runbook says react-native-webview's TurboModule "throws under Jest", so some suites read a navigator as text through `stripComments` / `readCode` in `src/test/sourceText.js` instead of importing it ([docs/testing.md:224-262](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)).
- **Native-read precedent:** `src/i18n/deviceLocale.js:48-78` reads `NativeModules.SettingsManager?.getConstants?.()?.settings` on iOS and `TurboModuleRegistry.get('I18nManager')?.getConstants?.()?.localeIdentifier` on Android at **call time**, with `'en'` as the floor ([deviceLocale.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/i18n/deviceLocale.js)). Its test swaps `Platform.OS`, `NativeModules.SettingsManager` and `NativeModules.I18nManager` per case and restores them afterwards. The test's comment notes that in Jest `TurboModuleRegistry.get('I18nManager')` "answers from `NativeModules`" because there is no `__turboModuleProxy` ([deviceLocale.test.js:36-84](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/i18n/__tests__/deviceLocale.test.js)).
- **Config-pin suites** ("config no import graph protects, pinned off disk"):
  - `src/i18n/__tests__/androidText.config.test.js`: `styles.xml`, `AndroidManifest.xml`, `MainApplication.kt`.
  - `src/i18n/__tests__/locales.config.test.js`: manifest, `res/xml/locales_config.xml`, `Info.plist`.
  - `src/theme/__tests__/orientation.config.test.js`: manifest, `Info.plist`.
  - `src/theme/__tests__/keyboard.config.test.js`: manifest, `styles.xml`, `android/build.gradle`, `gradle.properties`.
  - `src/utils/__tests__/firebaseModules.config.test.js`: `package.json`, `jest.setup.js`, `Podfile.lock`.
  - Sources: [androidText.config.test.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/i18n/__tests__/androidText.config.test.js), [firebaseModules.config.test.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/utils/__tests__/firebaseModules.config.test.js)
- **What does not exist yet:**
  - `package.json` has **no `codegenConfig`** (grep count 0); `src` has no `specs/` directory and no `Native*.js/.ts` spec files.
  - `MainApplication.kt` still carries the template placeholder `// add(MyReactNativePackage())` ([MainApplication.kt:16-19](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/src/main/java/in/vsyst/dzzlooms/MainApplication.kt)).
  - `tsconfig.json` includes `**/*.ts, **/*.tsx`, and Jest transforms `.ts` through babel-jest (jest.config.js:14).
- The documented app-level recipe ([RN: Turbo Native Modules](https://reactnative.dev/docs/turbo-native-modules-introduction)):
  - The spec goes in a root `specs/` folder, named with the `Native` prefix (e.g. `specs/NativeLocalStorage.ts`), in TypeScript or Flow. It exports `TurboModuleRegistry.getEnforcing<Spec>('NativeLocalStorage')`.
  - `package.json` gets `"codegenConfig": {"name", "type": "modules", "jsSrcsDir": "specs", "android": {"javaPackageName"}, "ios": {"modulesProvider": {"NativeX": "RCTNativeX"}}}`.
  - The iOS implementation is an Objective-C++ `.mm` class returning a `…SpecJSI`.
  - Android registers a `BaseReactPackage` in `MainApplication`.
  - Codegen runs during `pod install` and via Gradle `generateCodegenArtifactsFromSchema`.
- **House TDD rules that apply to native work:**
  - Red test committed first, then the green commit, then a mutation smoke recorded in the PR; never delete or `.skip` a test without a written verdict ([AI.md:7-26](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)).
  - Tiers: Tier 1 pure logic, Tier 2 store/MSW, Tier 3 screen decisions only ([AI.md:28-37](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)).
  - Suite budget ≤ 2 min, no `sleep`, flakes are P1 ([docs/testing.md:1483-1498](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)).
  - "New native package → Add its mock to `jest.setup.js` (use the package's shipped jest mock if it has one); if it ships ESM, extend `transformIgnorePatterns`" ([vault TDD guide §4](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/obsidian-notes/content/vsyst-technologies/docs/oms_app/tdd-testing-guide.md)).
  - `APP_ENV` must be set for any Jest run, and path patterns are regexes over the full path, including `__tests__/` ([docs/testing.md:38-56](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)).
  - CI runs `yarn test` only, on `ubuntu-latest`, Node 22, after `cp .env.ci .env.testing` ([.github/workflows/test.yml](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/.github/workflows/test.yml)).
  - The Xcode project has no test target, and Android has no `src/test` or `src/androidTest` (§7, §8).

### Inferences
A test-first in-house TurboModule in this repo (worked example: `NativeAppInfo`, replacing device-info) would need, in commit order:
1. **Tier 1 red — facade.** A JS facade such as `src/native/appInfo.js`, tested like `deviceLocale.test.js`: install a fake on `NativeModules.NativeAppInfo` per case and assert the facade's contract (sync constants, fallbacks when the module is missing, `uniqueId` a **string**).
2. **Config-pin red.** A `nativeModules.config.test.js` asserting that `package.json.codegenConfig` exists with `jsSrcsDir: "specs"`, the Android `javaPackageName` and the iOS `modulesProvider` entry, plus the `MainApplication.kt` registration (or autolinking). This is the same shape as `firebaseModules.config.test.js`.
3. **Global mock.** A `jest.mock('<path>/specs/NativeAppInfo', …)` in `jest.setup.js`, so screens that do not care never hit `getEnforcing`. The runbook notes an unmocked TurboModule throws in Jest.
4. **Green.** The spec (`specs/NativeAppInfo.ts`, allowed in this JS repo since Jest and tsconfig handle `.ts`), the ObjC++ `.mm` plus Kotlin implementation, then `pod install`. Nothing in CI compiles native code, so each native change also needs a recorded device check (the house already records simulator/emulator runs).
5. **Native unit tests** (XCTest / JUnit) would be new infrastructure. Neither platform has a test target today.

- Using `TurboModuleRegistry.get` plus fallbacks in the facade, rather than calling `getEnforcing` directly from screens, matches the house's `deviceLocale.js` pattern and keeps screens renderable in Jest.

### Gaps
- Whether `@react-native/codegen` accepts a `specs/` folder at repo root alongside the existing `src/` layout without extra `jsSrcsDir` changes was not tried (read-only brief).
- ESLint's handling of a `.ts` spec (the config is `eslint.config.js`) was not checked.

## 10. (d) Feature map per role, the native capabilities each flow touches today, and flows that would benefit from new native capabilities

### Takeaway
There are two role trees (Dealer, Customer), each a Drawer over a Main stack plus a three-tab "TrnTab" (Orders / Invoices / Payments). Auth and Guest stacks sit alongside them, and a registry swaps v1 ↔ v2 screens (v2 so far: Dealer Customers, Dealer and Customer Daily Summary). Native capabilities touched today:
- push and in-app messages (OneSignal);
- WebView document display;
- native date pickers, bottom sheets, SVG, gradients;
- connectivity, device constants and locale reads;
- Firebase crash, analytics and perf;
- persisted auth state (AsyncStorage).

The flows with the clearest native upside, each backed by repo evidence, are: invoice and voucher **share / print / PDF**, **secure token storage**, **working "update app" links on Android**, **deep links from notifications**, and later **camera capture** (a camera flow was started, then parked) and **Daily Summary widgets**.

### Cited Findings
- **Auth:** routes `Welcome`, `Login`, `ForgotPassword`, then `ValidateUser`. Role gates (`Dealer`, `Customer`) are in `navigation/Auth/index.js` and `Auth/ValidateUser.js`. The sign-in step is persisted in AsyncStorage (`helpers/Auth/authStep.js`, per the HEAD commit message) — [Auth/index.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Auth/index.js)
- **Dealer:**
  - Drawer (`navigation/Dealer/Drawer.js`): `dealerTab`, `dealer`, `dealerCompanyProfile`, `dealerCompany`, `dealerCustomer`, `dealerUser`, `dealerProd`, `dProducts`, `dealerReport`, `details`, `settings`, `help`, `redux`.
  - Main stack (`Dealer/Main.js`): `Profile`, `CompanyProfile`, `Notifications`, `DealerCompany`, `AddEditCompany`, **`Customers` (v1/v2)**, `CustSettings`, **`DailySummary` (v1/v2)**, `Accounts`, `AdvDepLedger`, `Discount`, `Products`, `UpdateProd`, `ProductDates`, `SetProductRate`, `PsocProds`, `DProducts`, `Users`, `AddEditUsers`, `Reports`, `DailyReport`, `TcsTdsReport`.
  - Tabs (`Dealer/TrnTab.js`): Orders (`CustomerOrder`, `NewSalesOrder`, `EditSalesOrder`); Invoices (`Invoices`, `Invoice`, `NewInvoice`, `NewInvoiceSummary`); Payments (`Payments`, `NewVoucher`, `Invoice`, `DPAccounts`, `AdvDepLedger`).
  - Registry calls: `register('Dealer/Customers', { v1, v2 })` at Main.js:53, `register('Dealer/DailySummary', …)` at :63, `resolveScreen(…, features)` at :176 and :204.
  - Sources: [Dealer/Main.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Dealer/Main.js), [Dealer/TrnTab.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Dealer/TrnTab.js), [Dealer/Drawer.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Dealer/Drawer.js)
- **Customer:**
  - Drawer: `customerTab`, `customer`, `customerCompanyProfile`, `customerCompany`, `customerDealer`, `customerUser`, `customerVehicle`, `dProducts`, `customerReport`, `details`, `settings`, `help`, `redux`.
  - Main stack: `Profile`, `CompanyProfile`, `Notifications`, `OTPManager`, `CustomerCompany`, `AddEditCompany`, `Dealers`, `DealerSettings`, `AddDealers`, **`DailySummary` (v1/v2, Main.js:50,206)**, `Accounts`, `AdvDepLedger`, `Discount`, `DProducts`, `ProductDates`, `Vehicles`, `VehicleRequests`, `VehicleReports`, `Users`, `AddEditUsers`, `Reports`, `DailyReport`, `TcsTdsReport`.
  - Tabs: Orders (`DealerOrder`, `NewOrder`, `Vehicles`); Invoices (`Invoices`, `Invoice`); Payments (`Payments`, `NewPayment`, `NewPayAck`, `Invoice`, `CPAccounts`, `AdvDepLedger`).
  - Sources: [Customer/Main.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Customer/Main.js), [Customer/TrnTab.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Customer/TrnTab.js)
- **Guest/demo stack:** `Index`, `Sample`, `Redux`, `Settings`, `DeleteAccount`, `Help`, `ContactUs` ([Guest/Main.js](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/navigation/Guest/Main.js)). v2 screen folders: `src/screens/v2/Dealer/Customers`, `src/screens/v2/Common/DailySummary`.
- **Native touch points today, file-cited:**
  - Push: `OneSignal.initialize` then `Notifications.requestPermission(true)` at first init, a click handler dispatching `setNotification(data)` into Redux, `OneSignal.login(externalUserId)`, IAM trigger `app_version`, and `update_app` → `Linking` to Play / App Store. `OneSignal.Debug.setLogLevel(LogLevel.Verbose)` runs unconditionally ([helpers/OneSignal/index.js:14-79](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/helpers/OneSignal/index.js)).
  - Documents: WebView HTML (§4).
  - Device metadata on **every API request**: header `meta` = JSON of `STATIC_DEVICE_INFO` built **at module scope** from 9 device-info getters, including `uniqueId: DeviceInfo.getUniqueId()` ([createApi.js:9-20,45](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/store/apis/createApi.js)). In device-info 15.0.2 `getUniqueId: () => Promise<string>`, with `getUniqueIdSync` as the sync variant ([privateTypes.d.ts:115-116](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/node_modules/react-native-device-info/lib/typescript/internal/privateTypes.d.ts)). `JSON.stringify` of a Promise field yields `{"uniqueId":{}}` (Node check, 2026-09-29). The Tier 2 test asserts only `appName` and `deviceOS` ([auth.endpoints.msw.test.js:52-95](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/store/apis/__tests__/auth.endpoints.msw.test.js)).
  - Other headers: `authorization: Bearer <token from AsyncStorage>`, `x-co-id`, `x-api-key` (createApi.js:30-44). Persisted keys include `userData` (token and role) and `currentUser` ([AI.md:252](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)).
  - Connectivity: NetInfo (§2).
  - Locale: `NativeModules.SettingsManager` / `TurboModuleRegistry.get('I18nManager')` (§9).
  - Accessibility: `AccessibilityInfo` in `theme/provider/useBoldText.js` and `components/v2/ListStates.js`.
  - Keyboard, AppState and BackHandler through RN core. Named `react-native` imports in live files: Keyboard 65 files, Alert 72, Platform 78, BackHandler 5, AppState 3, Linking 3, NativeModules / TurboModuleRegistry 1, StatusBar 1, InteractionManager 1. **Share, PermissionsAndroid, Clipboard, Vibration and ToastAndroid: 0** (census, 2026-09-29) — [src/](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/src/)
  - Observability: Crashlytics, Analytics and Perf through RTK Query middleware (§2).
  - Orientation: portrait pinned on both platforms (§7, §8).
- **Parked native intent:** a dead `components/ImagePicker/index.js` imports `react-native-image-picker` + `react-native-permissions` (camera/gallery), kept stubbed by the 2026-07-05 decision (§3). Dead invoice-download and PDF code shows a share/save flow was built and dropped (§4).

### Inferences
Candidate native capabilities, strongest evidence first. Each is a candidate "small in-house module" for the course:
1. **Invoice / voucher / TCS-TDS document actions.** Save as PDF, share (e.g., to WhatsApp or email) and print. Evidence: 4 WebView HTML renderers, an unused html-to-pdf dependency, and dead Share and PDF code. One module would cover it (iOS WKWebView → PDF data, `UIActivityViewController`, `UIPrintInteractionController`; Android WebView print adapter or `PdfDocument`, `FileProvider` + `ACTION_SEND`, `PrintManager`). Risk: file-provider and privacy configuration. Testable at Tier 1 through a mocked facade.
2. **`AppInfo` constants module.** Replaces device-info's ~10 getters and fixes the `uniqueId: {}` header bug. Low risk; the header contract can be pinned at Tier 2 with MSW.
3. **Secure credential storage** (Keychain / Android Keystore) for the bearer token now held in plain AsyncStorage `userData`. Medium risk (login persistence, migration of existing installs).
4. **Store / "update app" links and notification deep links.** Add Android `<queries>` or intent-based launching, and optionally App Links / Universal Links. Nothing handles an incoming URL today: no intent filters, associated domains or app URL scheme, and notification clicks only store data in Redux.
5. **In-app browser** (SFSafariViewController / Custom Tabs) for the two remote manual sites instead of a WebView modal.
6. **Camera / document capture** for delivery or dispensing slips and meter photos. Evidence: the parked ImagePicker. This would need new permission strings (Camera / Photo Library) on both platforms.
7. **Daily Summary home-screen widget / Live Activity.** v2 Daily Summary exists and `OneSignalLiveActivities.framework` is already embedded. Needs a new extension target plus its own App Group and data bridge. This is the highest effort item.
8. **Location for vehicle / delivery features** (`Vehicles`, `VehicleRequests`, `VehicleReports` routes exist). Only if the product wants it; it would finally make the location purpose strings truthful (§6).

### Gaps
- The product backlog (e.g., DU-slip work) lives outside this repo and was not read here. The mapping above is evidence from code, not from product specs.
- Whether `Notifications` screens deep-link into orders or invoices from a notification's `additionalData` was not traced beyond the Redux `setNotification` dispatch.

## 11. (e) Release and build process: scripts, APP_ENV / dotenv, CI, version and build numbering

### Takeaway
- **Environment selection:** everything keys off `APP_ENV` → `.env.${APP_ENV}` inlined by react-native-dotenv at Babel time. The default scripts pick **testing**.
- **Android:** a shell script builds a signed **universal APK** (`assembleRelease`) and uploads it to **Firebase App Distribution**. AAB (`bundleRelease`) is documented in the README but not scripted.
- **iOS:** there is no script; it is an Xcode Archive. The bundle phase **hard-codes `APP_ENV=testing` at HEAD**, which contradicts the README's claim that the repo ships `production`.
- **CI:** Jest only. There is no fastlane, EAS or App Center, and no native build in CI.
- **Versions:** 1.79, Android versionCode 104, iOS build 1 at HEAD (2 uncommitted).

### Cited Findings
- **Scripts** ([package.json:5-28](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/package.json)):
  - `start` → `start:test` (`APP_ENV=testing react-native start --reset-cache`).
  - `android` → `android:test`, which runs `run-android --no-packager` and Metro in parallel with `&`; likewise `ios`.
  - `:dev` / `:prod` variants.
  - `test` → `APP_ENV=testing jest`; `fixtures:pull` → `node ./scripts/pull_fixtures.js`.
  - The repo checklist item 2 flags "package.json default scripts point to TESTING env" ([PRODUCTION_RELEASE_CHECKLIST.md:50](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/todos/PRODUCTION_RELEASE_CHECKLIST.md)).
- **dotenv** ([babel.config.js:6-15](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/babel.config.js)):
  - `module:react-native-dotenv` with `moduleName: '@env'`, `path: .env.${process.env.APP_ENV || 'development'}`, `safe: true`, `allowUndefined: false`.
  - Env names (values not read): `PROJ_ENV`, `API_URL`, `API_VERSION_PATH`, `API_VERSION_PATH_V1`, `API_VERSION_PATH_V4`, `X_API_KEY`, `ONESIGNAL_APP_ID`, the four `CODEPUSH_*`, and `FIREBASE_ANDROID_APP_ID` (dev, testing and production only; the scripts read it, the app does not).
  - Only `src/constants/system.js` and `src/utils/API/index.js` import `@env`.
  - AI.md's rule: every `@env` name must exist in every env file, `.env.ci` included ([AI.md:227-237](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)).
  - AI.md says not to keep `X-API-KEY` in `.env` ([AI.md:241](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/AI.md)), yet `X_API_KEY` is an `@env` import in `system.js:6`. That is an internal inconsistency.
- **Android release, `build-release-apk.sh [development|testing|production]`** ([build-release-apk.sh:5-78](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/build-release-apk.sh); [build-install-apk.sh](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/build-install-apk.sh)):
  1. Default `testing`; exports `APP_ENV`; reads `FIREBASE_ANDROID_APP_ID` from `.env.$APP_ENV`.
  2. Kills Metro and runs `yarn reset`.
  3. Runs `./gradlew clean` and `./gradlew assembleRelease` → `app/build/outputs/apk/release/app-release.apk`.
  4. Calls `firebase appdistribution:distribute … --groups ${FIREBASE_GROUPS:-dzzlo-oms-app}`, with release notes from `git log -1`.
  - `build-install-apk.sh` does the same build and then `adb install -r`.
- **AAB:** the README documents `APP_ENV=production yarn reset && cd android && ./gradlew clean && APP_ENV=production ./gradlew bundleRelease` → `app-release.aab` ([README.md:181-210](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/README.md)). Checklist item 5 says "Build script only produces APK, not AAB" ([checklist:175-186](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/todos/PRODUCTION_RELEASE_CHECKLIST.md)).
- **iOS release:**
  - The README says archives come from Xcode Product → Archive, the env is "hardcoded into the Bundle React Native code and images build phase", and warns to verify it before every TestFlight or App Store archive (README.md:230-236).
  - It then says "The repo ships with `export APP_ENV=production` … Production archives need no edit" (README.md:238-244) and gives `sed` commands to switch to testing and back (246-254).
  - **HEAD's `project.pbxproj` has `export APP_ENV=testing`** in that phase: `git show HEAD:…project.pbxproj`, 2026-09-29; phase script at pbxproj:291 ([project.pbxproj](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app.xcodeproj/project.pbxproj); [README.md](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/README.md)).
  - Post-archive: dSYM "Upload Symbols Failed" warnings for the prebuilt `React.framework` / `ReactNativeDependencies.framework` are called non-blocking (README.md:290). The RNFB Crashlytics run-script phase handles dSYMs for the rest (pbxproj build phases).
- **Versioning:**
  - Android: `versionCode 104` / `versionName "1.79"` ([app/build.gradle:89-90](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/android/app/build.gradle)).
  - iOS: `MARKETING_VERSION = 1.79`, `CURRENT_PROJECT_VERSION = 1` at HEAD, set by commit `4b45cc0b` (2026-09-25, "iOS build number starts at 1 for 1.79"); an earlier commit that day, `26e75f5b`, read "bump v1.79 build (android 104, ios 10)". The uncommitted working tree has 2. NSE: 1.0 (1).
  - `package.json` `"version": "0.0.1"` is unused.
  - Sources: [project.pbxproj](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/dzzlo_oms_app.xcodeproj/project.pbxproj), [repo history](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/)
- **CI:** `.github/workflows/test.yml`, job "Jest", runs on `pull_request` (opened, synchronize, reopened) and on `push` to `main`. Steps: `ubuntu-latest`, `actions/setup-node@v5` Node 22 with yarn cache, `yarn install --frozen-lockfile`, `cp .env.ci .env.testing`, `yarn test` ([test.yml:1-29](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/.github/workflows/test.yml)).
  - No `fastlane/`, `eas.json`, `bitrise.yml`, `codemagic.yaml` or App Center config exists (filesystem check, 2026-09-29).
  - The cross-repo release gate is `bash dzzlo_oms_api/scripts/release_gate.sh` ([vault TDD guide §4](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/obsidian-notes/content/vsyst-technologies/docs/oms_app/tdd-testing-guide.md); [docs/testing.md:1465-1474](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/testing.md)).
- **Tooling:** the Gemfile pins `cocoapods >= 1.13, != 1.15.0, != 1.15.1` and `xcodeproj < 1.26.0`, and the README tells you to run `bundle exec pod install` ([Gemfile](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/Gemfile); [README.md:81-120](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/README.md)). `ios/.xcode.env` sets `NODE_BINARY=$(command -v node)`, and a local override pins Homebrew node 26.3.0 ([.xcode.env](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/ios/.xcode.env)).
- **Open release-checklist items** as of its last commit `ad40ed71` (2026-09-27): item 4 "ProGuard / R8 disabled for release builds" (line 86), item 7 "Strip `console.*` from production JS bundle" (222), item 9 "Source maps not uploaded for Crashlytics" (286), plus items 5, 6 and 8 above ([PRODUCTION_RELEASE_CHECKLIST.md](file:///Users/shikhar/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/dzzlo_oms_app/docs/todos/PRODUCTION_RELEASE_CHECKLIST.md)).

### Inferences
- **Highest release risk for any native-module change: the iOS bundle phase.** An archive cut from HEAD bundles `.env.testing` (the staging API) unless someone remembers to edit it, and the README tells them the opposite. A config-pin test on the pbxproj phase would turn this into a failing test. Alternatively, move env selection into a scheme or xcconfig and pin that.
- **Native changes are verified only by hand.** No CI job compiles iOS or Android, so a new TurboModule's native code is checked only on developer machines and devices. A course should either add a CI native build (e.g., `xcodebuild` and `assembleDebug` on macOS runners) or require recorded device runs, as the house already does.
- **R8 off plus a universal APK means a larger app with an unobfuscated bytecode surface.** Turning on R8 needs keep-rules for reflection-heavy SDKs (OneSignal, Firebase) and a full device regression, which checklist item 4 already describes.

### Gaps
- Where the production Play upload happens (manual AAB via README vs APK) and whether TestFlight uploads use Xcode Organizer or Transporter was not documented in the repo beyond the README steps.
- The iOS build-number policy across 1.79 (10 → 1 → 2) was not explained in the commits read; ask the release owner.
