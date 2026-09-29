# Writer brief — house style for the native-modules course

This folder (`research/`) is published with the course on purpose (user decision 2026-09-30; it was `_research/` during the build). It holds the six research notes and this writer brief. The course files live one level up.

## Where the course lives

`obsidian-notes/content/vsyst-technologies/docs/learning/native-modules/`

Sibling courses to imitate: `../comfyui/` and `../google-flow/` (phased, hands-on, written against the real install), `../tdd/` (the house testing doctrine — every change is red → green).

## File naming (fixed)

```
00_README.md                          course front page
01-phase-1-<slug>.md … NN-phase-N-<slug>.md   one file per phase
NN-capstones.md                       end-to-end projects
NN-reference.md                       matrices, versions, sources, glossary, troubleshooting
```

Lower-case kebab slugs. Links between course files are Obsidian wikilinks to the file stem, e.g. `[[03-phase-3-files-share-and-pdf]]`, optionally with a section, e.g. `[[11-reference]] §4`. Never use relative `.md` links. Never link to `research/` (unpublished).

## Voice and shape (copied from the sibling courses)

- H1 = `# Phase N — Title: Subtitle`. Right under it a one-line blockquote: `> Level: Easy | Time: ~45 min | Outcome: …` (the README uses `> Audience: … | Status: written & web-verified 2026-09-29 against … | …`). Then `---`.
- Numbered H2 sections: `## 1. The One Idea`, `## 2. …`. Sub-steps as H3 or numbered lists. Every phase ends with `## N. Exercises` (numbered **N.1 — Title.** bold lead-ins, each producing a file, a test result, a screenshot or a device observation) and, where relevant, a `## Lab Notes` section that records what was actually observed, dated.
- Explain-it-simply first, then the exact procedure. Tables for anything comparative. Code blocks for every command, file path, spec, Swift/Kotlin/JS snippet, plist/manifest fragment. ASCII pipelines are welcome.
- Concrete over generic: every claim about THIS app cites a file path (and line where useful) from `dzzlo_oms_app` as of 2026-09-29; every claim about a platform API names the OS version that introduced it; every library gets its version and date. Numbers are either measured/verified (mark ✅ or "verified 2026-09-29") or estimates (mark _(est.)_).
- Be honest and opinionated the way the ComfyUI README is ("Four Things Wrong With This Install"): call out dead permission strings, unused dependencies, misleading defaults, App Review traps.
- House rules to weave in where they apply, stated plainly rather than as a lecture: (1) test-first — a native module gets its Jest red test (JS side, mocked spec) and its native unit test before the implementation; (2) parity — a feature ships on iOS and Android together or the phase says explicitly what Android/iOS gets instead; (3) 320 dp × fontScale 1 is the width baseline for any UI, en + hi; (4) colours come from `src/theme` tokens; (5) nothing is committed, merged, pushed or published without the user's word; (6) money is whole paise, half-up.
- British-leaning spelling as in the sibling courses (colour, optimise), Indian context (₹, GST, UPI, WhatsApp, IST).
- No em-dash overuse in body prose is fine; the siblings use " — " liberally, so match them.
- Length: README 250–400 lines; each phase 250–500 lines; reference as long as it needs to be. Dense, not padded.

## Non-negotiables

- Do not invent APIs, versions, or library names. If a research note marks something unverified, the course says so too.
- Do not paste secrets (API keys, GoogleService plist values, .env values).
- Do not edit anything under `dzzlo_oms_app/` — the course describes what to do; the user starts the build separately.
- Cite sources by title + URL in the reference file's Sources section; phases may carry short inline "Source:" lines.

## Draft outline (12 files) — DRAFT, pending the user's choices

| File | Working title | Draws on notes |
| --- | --- | --- |
| `00_README.md` | Native Modules for DZZLO OMS — what to build, what to drop, and how | all |
| `01-phase-1-foundations.md` | New Architecture mental model; Turbo vs Nitro vs Expo decision; toolchain as measured; test-first workflow for native code; first module walk-through (`NativeAppInfo` replacing react-native-device-info, fixing the uniqueId Promise bug) | rn-native-module-tech, app-audit |
| `02-phase-2-dependency-diet.md` | Remove / replace / repair: @react-navigation/stack, 75 unreachable files + 4 uninstalled imports, html-to-pdf (never called), moment → house helpers, linear-gradient → svg, prop-types, CODEPUSH_* env, compat-layer packages, location-string wording, `<queries>`, iOS archive APP_ENV, R8/AAB | app-audit, rn-native-module-tech |
| `03-phase-3-files-share-and-pdf.md` | Share sheet → WhatsApp with a file, document picker, native PDF module (A4 pagination), print, Files/SAF export (CSV/XLSX), Quick Look | ios, android, ecosystem |
| `04-phase-4-images-and-scanning.md` | VisionCamera 5 + QR (IRN), document scanner (ML Kit / VisionKit), photo picker without permission, compress/EXIF, sandbox storage, background upload module, download, OCR option | ios, android, ecosystem |
| `05-phase-5-notifications-and-live-status.md` | OneSignal deeper (categories, channels, POST_NOTIFICATIONS, interruption levels, in-app messages), local notifications, iOS Live Activities via OneSignal + Widget Extension, Android 16 Live Updates via Kotlin NSE with < 16 fallback, OEM battery killers | ios, android, ecosystem |
| `06-phase-6-widgets-shortcuts-and-intents.md` | WidgetKit + Glance widgets over an App-Group snapshot, Controls / Quick Settings tile, quick actions, App Intents + Shortcuts + Spotlight in Swift, Android App Shortcuts + AppFunctions, what Siri / Gemini really do in 2026 | ios, android, ecosystem |
| `07-phase-7-maps-and-location.md` | Whether maps are needed, react-native-maps, Maps SDK free caps, location tiers + purpose strings, tanker tracking = foreground service, deferral verdict | ios, android, ecosystem |
| `08-phase-8-instant-experiences-and-links.md` | Universal / App Links, deep links into orders and invoices, App Clip "view / pay this invoice" (15 MB, Swift-native), Android substitute = web + UPI intent, wa.me / upi:// via Linking + query schemes | ios, android, ecosystem |
| `09-phase-9-security-privacy-and-release.md` | Biometric lock, Keychain, passkeys, OTP autofill, privacy manifest, Play Data safety, purpose strings that pass review, review-clause map, extension provisioning, OTA after CodePush, secrets in gradle.properties, release checklist | ios, android, ecosystem, app-audit |
| `10-capstones.md` | A: invoice → native PDF → WhatsApp · B: order status → push → Live Activity + Live Update · C: Daily Summary widget + "outstanding balance" intent | all |
| `11-reference.md` | Library matrix (USE / WRAP / BUILD / SKIP), versions as measured, effort table, review-policy map, glossary, troubleshooting, sources | all |

Packaging default: in-app local modules (`specs/` + `ios/` + `android/` inside dzzlo_oms_app, autolinked), not a separate package.

## Decisions taken by the user (2026-09-29)

- **Outline:** as drafted above (12 files, that order). English only — no Hindi folder.
- **Spec typing:** TypeScript only inside `specs/` (`NativeFoo.ts`); the rest of the app stays JavaScript. TypeScript 6 is already a devDependency.
- **RN version:** the app is 0.84.1 today and the user will upgrade to the latest release soon (0.87.1 on 2026-09-29). Write every step against 0.84 as measured, and add a short callout box `> **After the upgrade to 0.87:** …` wherever a step changes (Jest preset `@react-native/jest-preset` from 0.85; AGP 9 + compileSdk 37 in 0.87; `<React/…>` framework-style imports if SPM). Never write a step that only works on one of the two without saying which.
- **Module technology:** see the line below once the user answers (Turbo Modules recommended; Expo modules as an optional third-party-library track after the upgrade, only on an Expo-paired RN version; Nitro as a later hot-path option).
- **Module technology (decided 2026-09-29):** own modules = official Turbo Modules (TypeScript spec + codegen; Swift behind a thin Objective-C++ adapter on iOS; Kotlin + `BaseReactPackage` on Android; Fabric components for native views). Nitro = a later option for a measured hot path only. Expo = ONE optional track ("After the upgrade: Expo modules for third-party packages and EAS Update"), taken only on an Expo-paired RN version (SDK 56 ↔ 0.85, 57 ↔ 0.86, 58 preview ↔ 0.88; nothing pairs with 0.84 or 0.87), never for authoring our own modules. Hot Updater is the no-Expo OTA route.

## Shared canon (every writer uses these exact facts; all verified 2026-09-29 in the notes)

- App: react-native 0.84.1 (latest release 0.87.1, 2026-08-11), react 19.2.3, New Architecture on, Hermes, JavaScript (852 .js, 1 .ts), Kotlin 2.1.20, AGP 8.12.0, Gradle 9.0.0, NDK 27.1, minSdk 24, compile/target 36; iOS deployment target 15.1, `SWIFT_VERSION = 5.0` in the targets, no bridging header, pods link STATIC (use_frameworks! only with the USE_FRAMEWORKS env var), prebuilt React.framework; SceneDelegate lives inside AppDelegate.swift; two Xcode targets (app + OneSignalNotificationServiceExtension), App Group `group.in.vsyst.dzzlooms.onesignal`, team YT955YZMZU, no associated domains; Android package `in.vsyst.dzzlooms`; no codegenConfig, no specs/, no XCTest or JUnit targets; CI = Jest only.
- App HEAD: audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30), branch `release/v1_79` — state it in that form wherever a file names the HEAD, and never renumber lines.
- Machine: MacBook Pro M5 Max, macOS 27.0 (26A428) (`sw_vers`, re-checked 2026-09-30), Xcode 27.0 (27A266a), Swift 6.4. iOS 27 + Xcode 27 shipped 2026-09-14; uploads need the iOS 26 SDK since 2026-04-28; UIScene mandatory with the iOS 27 SDK; Liquid Glass cannot be opted out on iOS 27.
- Android 17 (API 37) stable 2026-06-16. Play: target API 36 required from 2026-08-31; 16 KB page size enforcement 2027-02-01 per Google's page (older guidance said Nov 2025 / May 2026 — record the conflict); Play Instant shut down Dec 2025; Google Assistant removed from phones from 2026-09-04; Glance 1.2.0 stable 2026-08-26; India Android mix Aug 2026: 16 = 24.1 %, 15 = 23.3 %, 13 = 13.9 %, 14 = 12.1 %, 12 = 9.4 %, 11 = 8.8 %.
- Libraries: notifee archived 2026-04-07 → react-native-notify-kit 10.8.0; expo-live-activity archived 2026-06-01; expo-widgets iOS-only (Android in SDK 58); Voltra 2.3.2 (2026-09-22) with Android Live Updates merged 2026-09-28 but unreleased; OneSignal SDK ≥ 5.2 runs iOS Live Activities (OneSignalLiveActivities pod already installed); react-native-html-to-pdf last release Sep 2025 and never called in live code; react-native-print unmaintained (Jan 2023); react-native-background-upload dead (2022); react-native-image-picker + react-native-keychain no release in 12+ months; VisionCamera 5.2.3 (New Arch only); react-native-maps 1.29.11; react-native-share 12.3.1; @react-native-documents/picker 12.0.2; OneSignal 5.5.14; RNFirebase 26.4.0 (app on 24.0.0); Nitro 0.37.1 (2026-08-27); CodePush retired 2025-03-31.
- Audit findings the README lists under "things wrong with this install" (details + file:line in app-audit.md): html-to-pdf imported, never called; 75 of 674 source files unreachable, 4 imported packages not installed (code-push, image-picker, permissions, rn-fetch-blob); prop-types used by 13 live files, undeclared; `DeviceInfo.getUniqueId()` is a Promise in v15 so the API `meta` header carries `{}`; three generic location purpose strings (needed because OneSignal's location component is linked, wording fails guideline 5.1.1(ii)); no `<queries>` for https, so `Linking.canOpenURL` resolves `false` on Android 11+ (RN 0.84.1's `IntentModule.kt`; RN's docs say it may reject); iOS archive bundle phase hard-codes `APP_ENV=testing`; `CODEPUSH_*` env values still inlined; R8 off, one ~107 MB universal APK; upload-key passwords tracked in git (never print them); six packages on the compat layer (4 × Firebase 24, device-info, linear-gradient); @react-navigation/stack imported by nothing.

## Scope added by the user 2026-09-30: store app rating and review

Plan the integration of in-app store rating and review prompts (iOS StoreKit `requestReview`, Google Play In-App Review) — research note `research/notes/store-rating-and-review.md`. Placement (orchestrator's call, no renumbering): a new numbered section in `09-phase-9-security-privacy-and-release` ("Store rating and review") before the release checklist; a USE/WRAP/BUILD row + a one-line mention in the README verdict and "What Users Will Notice"; a row in the reference library matrix and the review/policy map (App Store 5.6.1 — use the provided API, no custom prompts; 3.2.2(x); 5.6.3; Play ratings policy — corrected 2026-09-30, the earlier 1.1.7 was wrong); a hook in capstone A (ask after a successful invoice share, subject to the caps). Trigger state lives in AsyncStorage; the "Rate DZZLO" row lives in the Help screen (`src/screens/Common/Help`).
