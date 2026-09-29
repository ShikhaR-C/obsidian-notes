# Phase 9 — Security, Privacy, Review and Release: Shipping Extensions Without Getting Rejected

> Level: Intermediate | Time: ~2 h reading, plus the fixes | Outcome: you can list every entitlement, purpose string, manifest permission and store declaration the earlier phases add; lock the app with biometrics without storing a password; fill in the privacy manifest and Data safety honestly; sign four targets; keep the release build lean and 16 KB-aligned; ship JS fixes over the air without ever shipping native code that way — and run one checklist from the Jest gate to store submission.

---

## 1. The One Idea

Every native surface leaves a paper trail: a manifest entry, a purpose string, a Data safety row, an entitlement, a capability on a provisioning profile. App Review and Play policy read **all** of it — including the parts a library added for you. Most rejections in this area aren't about code; they're about a string that doesn't say what the app does, or a permission nobody can explain.

The map of what this course adds. Nothing below is built; "today" means the repo on 2026-09-29.

| Feature (phase) | iOS keys / entitlements | Android permissions / declarations | App Review clause | Play policy |
| --- | --- | --- | --- | --- |
| Push + in-app messages (today) | `aps-environment`; App Group `group.in.vsyst.dzzlooms.onesignal`; `UIBackgroundModes: remote-notification` | `INTERNET` declared; 30 more merged in (OneSignal incl. `POST_NOTIFICATIONS` and 16 launcher-badge permissions; Firebase; NetInfo; WorkManager) | 4.5.3, 4.5.4 | Data safety: device IDs via OneSignal / Firebase |
| Firebase Analytics (today) | the SDKs' own privacy manifests (none found on disk for FirebaseAnalytics — §4) | **`AD_ID`**, `ACCESS_ADSERVICES_ATTRIBUTION`, `ACCESS_ADSERVICES_AD_ID` (merged manifest lines 63–65) | 5.1.2 | Data safety: declare, or remove |
| Location strings (today, never shown) | three `NSLocation…` strings, needed while `OneSignalLocation` is linked | none | 5.1.1(ii) | — |
| Files, share, PDF ([[03-phase-3-files-share-and-pdf]]) | none for the system pickers | none (SAF, `FileProvider`); explicit URI grants from Android 18 | 2.5.15 | "Files and docs" row if uploaded |
| Camera, scan, photos ([[04-phase-4-images-and-scanning]]) | `NSCameraUsageDescription`; add-only Photos access if saving | `CAMERA` only with a custom camera; the Photo Picker needs none | 2.5.14, 5.1.1(ii)–(iii) | photo/video permissions policy; "Photos" row if uploaded |
| Notifications + live status ([[05-phase-5-notifications-and-live-status]]) | `NSSupportsLiveActivities`; Time Sensitive capability (key not confirmed on an Apple page); `DzzloWidgets` target + App Group `group.in.vsyst.dzzlooms.shared`; a `.p8` APNs key | `POST_PROMOTED_NOTIFICATIONS` (normal, no prompt) | 4.5.3, 4.5.4, 2.5.16 | Live Update usage guidance |
| Widgets, shortcuts, intents ([[06-phase-6-widgets-shortcuts-and-intents]]) | widget extension; `keychain-access-groups` if Swift reads the token | widget receiver; `BIND_QUICK_SETTINGS_TILE` for a tile | 2.5.16, 4.4, 2.5.11 | none found |
| Location ([[07-phase-7-maps-and-location]]) | honest strings; the `location` background mode only for tracking | COARSE/FINE; `FOREGROUND_SERVICE_LOCATION`; background location avoided | 5.1.5, 2.5.4, 5.1.1(ii) | background-location form; FGS declaration; location button from 2027-01-27 |
| Links, App Clip ([[08-phase-8-instant-experiences-and-links]]) | associated domains (`applinks:`, `appclips:`); `LSApplicationQueriesSchemes`; `DzzloClip` + three App Clip entitlements | `autoVerify` intent filters; `<queries>` | 2.5.16(a), 3.1.3(e) | none |
| Biometric lock, passkeys (this phase) | `NSFaceIDUsageDescription`; `webcredentials:` | a biometric permission via `androidx.biometric` (unverified) | 2.5.13, 4.8, 5.1.1(v) | none |
| Store rating and review (this phase, §9) | none — the StoreKit call needs no key or entitlement | none of ours; diff what `com.google.android.play:review` 2.0.2 merges into the release manifest (not checked) | 5.6.1, 3.2.2(x), 5.6.3, Introduction | "User Ratings, Reviews, and Installs"; the In-App Review guidelines |

Keep this table next to the release checklist (§10); every row a release touches is re-read before submission.

## 2. Biometric Lock and Keychain

**The evidence.** Indian users ask for it in reviews: "Not yet received fingerprint app lock ... still waiting for fingerprint app lock" (Khatabook, 1★, 2026-08-16); "the biometric lock functionality wasn't actually included. Instead, I'm left with only a standard pin lock" (Khatabook, 3★, 2026-08-13). And they resent repeated OTPs: "The app logs me out whenever there's an internet issue ... forcing me to verify again with OTP" (PhonePe Business, 1★, 2026-09-23). Biometric lock and quick re-auth rank **6th** of 15 in the value table — T1, 2–3 days _(est.)_.

**The platform pieces.**

- **iOS:** `LAContext` (LocalAuthentication, iOS 8.0) evaluates Face ID, Touch ID or the passcode. `NSFaceIDUsageDescription` (iOS 11.0) "is required if your app uses APIs that access Face ID" — the app has none today. Guideline **2.5.13**: face authentication goes through LocalAuthentication, never a home-made face check. App Clips can't use Face ID.
- **Android:** `androidx.biometric`'s `BiometricPrompt` accepts `BIOMETRIC_STRONG` (Class 3), `BIOMETRIC_WEAK` (Class 2) and `DEVICE_CREDENTIAL`. `DEVICE_CREDENTIAL` alone and `BIOMETRIC_STRONG | DEVICE_CREDENTIAL` aren't supported on API 29 and lower — use `KeyguardManager.isDeviceSecure()` there. The platform `BiometricPrompt` arrived in Android 9 (API 28); on API 24–27 the AndroidX prompt falls back to the older fingerprint path (API levels from the platform docs, not re-verified in this course's research). Keystore keys can demand user authentication (`setUserAuthenticationRequired`, `setUserAuthenticationParameters`).

**A library, not a module.** The ecosystem has maintained options, so this course adds **no `NativeBiometrics`**:

| Library | Version (date) | Arch | Health | Fit on RN 0.84 |
| --- | --- | --- | --- | --- |
| `react-native-keychain` | 10.0.0 (2025-03-23) | TurboModule | no release for 18 months (repo push 2026-04-29); 166 open issues; 553,883/week | **USE** — keeps the token in Keychain/Keystore and gates it with biometrics: both jobs, one library |
| `@sbaiahmed1/react-native-biometrics` | 0.16.1 (2026-09-08) | TurboModule per the ecosystem research; an Expo module per the iOS research — **the notes disagree** | active (20 releases in 12 months), small (121 stars) | alternative for the prompt; read its `package.json` first — if it needs `expo`, it's blocked on 0.84 |
| `react-native-sensitive-info` | 6.1.5 (2026-06-30) | Nitro | active | maintained alternative for storage; Nitro adds `.so` files (16 KB check) |
| `expo-local-authentication` / `expo-secure-store` | 57.0.3 / 57.0.4 | Expo modules | active | the pair to move to on the Expo track (RN 0.85/0.86 only) |
| `react-native-biometrics` | 3.0.1 | old architecture | stale (the notes disagree on its date: 2022-09-06 vs 2025-12-12) | skip |

What "no release in 18 months" means in practice: `react-native-keychain` works today — a New-Architecture TurboModule in heavy use — but when an RN minor, an iOS 27.x or an Android 17 change breaks it, there is no upstream release to take. So pin the exact version, keep every call behind one facade (`src/native/appLock.js`) so it can be swapped, and list it in the upgrade checklist (§10).

**The lock design.**

- **Move the token first.** The bearer token sits in plain AsyncStorage under `userData` (`src/store/apis/createApi.js:26-30`). Move it into the Keychain/Keystore through the facade: read the old key once, write the secure item, delete the old key — and test a fresh install *and* an upgraded one, because a failed migration signs everyone out.
- **Relock after N minutes in the background**, and on a cold start with a stored session. N is a product decision; five minutes is a starting proposal.
- **Unlock** with biometrics or the device passcode. On a device with no screen lock at all there is nothing to check against — skip the lock and say so once.
- **Never store the password.** The house rule from the OTP-restart fix: `src/helpers/Auth/authStep.js` writes down the sign-in step — "Never the password, never the OTP" — and Login asks for the password again on return. The lock's fallback is **Sign out**, then a normal OTP sign-in; never a saved password.
- The lock screen follows the UI rules: 320 dp × fontScale 1, en and hi, colours from `src/theme` tokens.

**Tests, red first.** The relock decision is pure, so it's Tier 1:

```js
// src/helpers/Auth/__tests__/relock.test.js
import { shouldRelock } from '../relock';

const GRACE = 5 * 60 * 1000;

test('relocks only once the grace period in the background has passed', () => {
  expect(shouldRelock({ backgroundedAt: 0, now: GRACE - 1, graceMs: GRACE })).toBe(false);
  expect(shouldRelock({ backgroundedAt: 0, now: GRACE, graceMs: GRACE })).toBe(true);
});

test('a clock that moved backwards locks — the age is unknowable', () => {
  expect(shouldRelock({ backgroundedAt: 10_000, now: 5_000, graceMs: GRACE })).toBe(true);
});

test('never backgrounded, never locked by time', () => {
  expect(shouldRelock({ backgroundedAt: null, now: 1e12, graceMs: GRACE })).toBe(false);
});
```

Then a Tier 3 test of the lock gate with the facade mocked (`jest.mock('../../native/appLock')`); the facade's own test mocks the library — name only the calls you read in its README. Device checks: enrol a fingerprint on the AVD and Face ID on the simulator, then walk background → wait → return, cancel, and sign-out on both platforms.

## 3. Passkeys and OTP Autofill

**Passkeys — not for v1.** iOS: `ASAuthorizationPlatformPublicKeyCredentialProvider` (iOS 15.0) needs a `webcredentials:` associated domain; iOS 26 adds `ASAuthorizationAccountCreationProvider`. Android: Credential Manager (`androidx.credentials`) needs Android 9 (API 28)+ through Play services, plus Digital Asset Links. Libraries: `react-native-passkey` 3.6.2 (2026-09-08, Directory New-Arch ✅, 135,277/week), `react-native-passkeys` 0.4.2 (2026-08-05), `react-native-credentials-manager` 0.9.0 (Android only). The ecosystem verdict is **SKIP for v1**: email OTP works, and passkeys need server-side WebAuthn plus the AASA / `assetlinks.json` work from [[08-phase-8-instant-experiences-and-links]] — 8–15 days on iOS or 5–10 days on Android, server included _(est.)_ — while API 24–27 devices stay on OTP either way.

**iOS OTP autofill — half a day.** iOS 17+ fills one-time codes that arrive in Mail when the field opts in with `textContentType="oneTimeCode"` (an iOS-only `TextInput` prop). No OTP field sets it today (grep, 2026-09-29); the fields are `src/screens/Login/AuthNavigator/Login.js:552` and `ForgotPassword.js:430-431`, both `keyboardType="number-pad"`.

```js
// Login.js / ForgotPassword.js — the OTP TextInput
<TextInput
  label="Enter OTP"
  keyboardType="number-pad"
  textContentType="oneTimeCode"
  /* …existing props… */
/>
```

Test first: a Tier 3 render test that finds the OTP field and asserts `textContentType === 'oneTimeCode'`. The device check needs a real iPhone with Mail set up — the simulator has no Mail app. **The house rule holds throughout: OTP runs use an email identifier, never a phone number** — which is also the path Mail autofill covers.

**Android SMS Retriever — only if SMS OTP is real.** The sign-in screens accept a phone number or an email (`isPhoneLogin`, `Login.js:470`). If the API sends phone OTPs by SMS, the SMS Retriever API reads them with "no extra app permissions": the message must be at most 140 bytes and include the code plus an 11-character hash derived from the package name and the signing certificate. Libraries: `@ebrimasamba/react-native-sms-retriever` 2.1.1 (2026-06-05, New-Arch ✅) or `@pushpendersingh/react-native-otp-verify` 1.2.0 (2025-10-15, TurboModule); `react-native-otp-verify` 1.2.0 isn't New-Arch. **Android 17** protects OTPs: for apps targeting 37, "standard SMS OTP messages withheld for 3 hours; apps must migrate to SMS_RETRIEVER or SMS User Consent", and for all apps, WebOTP-format messages are delayed 3 hours for apps without the receive permission. DZZLO reads no SMS today, so nothing breaks, and SMS Retriever keeps it that way. **Unverified:** the hash changes the SMS text, and India's TRAI DLT template registration probably means a newly approved template with the SMS provider (2factor.in) before this can ship.

## 4. Privacy Manifests and Data Safety

**What the app declares today** — `ios/dzzlo_oms_app/PrivacyInfo.xcprivacy`, the only non-pod privacy manifest in the project (the NSE has none):

| Category | Reason codes |
| --- | --- |
| `NSPrivacyAccessedAPICategoryFileTimestamp` | C617.1 |
| `NSPrivacyAccessedAPICategoryUserDefaults` | CA92.1, 1C8F.1, C56D.1 |
| `NSPrivacyAccessedAPICategorySystemBootTime` | 35F9.1 |
| `NSPrivacyAccessedAPICategoryDiskSpace` | 85F4.1 |

Plus `NSPrivacyCollectedDataTypes = []` and `NSPrivacyTracking = false`. Since **1 May 2024** App Store Connect rejects apps "that don't describe their use of required reason API"; third-party SDKs must ship their own manifests; and "for each executable or dynamic library … the bundle that includes the executable or dynamic library needs to include a privacy manifest file". Fourteen pods ship one today (FirebaseABTesting, FirebaseCore, FirebaseCoreExtension, FirebaseCoreInternal, FirebaseCrashlytics, FirebaseInstallations, FirebaseRemoteConfig, GoogleDataTransport, GoogleUtilities, nanopb, OneSignalXCFramework, PromisesObjC, PromisesSwift, ReactNativeDependencies). None was found for FirebaseAnalytics / GoogleAppMeasurement, FirebasePerformance or FirebaseSessions — they may carry one inside their binaries (unverified). Apple's commonly-used-SDK list, which requires a manifest and a signature, includes four OneSignal SDKs and about a dozen Firebase SDKs (secondary sources).
Source: https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api

**What each new piece adds.** An extension is its own executable, so the rule above reads as "one manifest per target" — an inference, and a cheap one to honour:

| New piece | Likely category | Status |
| --- | --- | --- |
| `NativeAppInfo` ([[01-phase-1-foundations]]) | SystemBootTime / DiskSpace only if it reads uptime or disk space | today's 35F9.1 and 85F4.1 probably serve `react-native-device-info`'s getters — keep them until Phase 1's getters are final |
| `NativeSharedStore` ([[06-phase-6-widgets-shortcuts-and-intents]]) | UserDefaults if it uses App Group defaults; FileTimestamp if it reads file dates | RN's own Swift example uses UserDefaults, "believed to be a required-reason API; verify" — **unverified** |
| `DzzloWidgets` target | its own manifest; UserDefaults if it reads the snapshot from defaults | inference |
| `DzzloClip` target | its own manifest if it uses any required-reason API | inference |
| OneSignal NSE (today) | none declared; add one if its code ever touches a listed API | the NSE ships no manifest today |

Pick every reason code from Apple's list at the moment you add it — this course's research didn't capture what the codes mean.

**The privacy label is not the manifest.** An empty `NSPrivacyCollectedDataTypes` doesn't mean the app collects nothing: Analytics, Crashlytics and OneSignal do. The App Store privacy label has to cover what the SDKs collect.

**Play Data safety.** Declare every data type collected or shared — location, photos and videos, files and docs, contacts, app activity, device or other IDs, crash logs and diagnostics — including data collected "through any third-party libraries or SDKs", plus encryption in transit and whether users can request deletion. Discrepancies can block updates or remove the app. For this app today: device IDs (OneSignal, Firebase), app activity (Analytics), crash logs and diagnostics (Crashlytics, Performance), and the **advertising ID** — the merged release manifest carries `com.google.android.gms.permission.AD_ID` from `play-services-measurement` 23.0.0 and the two AdServices permissions (lines 63–65). Declare it, or remove it if ads attribution isn't wanted; confirm the removal method in Firebase's docs, which this research didn't cover.
Source: https://support.google.com/googleplay/android-developer/answer/10787469

**Two policies that later phases trigger:**

- **Photo and video permissions.** Apps targeting 33+ "may only request the `READ_MEDIA_IMAGES` and `READ_MEDIA_VIDEO` permissions if system pickers … are not sufficient"; occasional use means the Photo Picker; a Play Console declaration is required (full compliance mandatory since 28 May 2025). [[04-phase-4-images-and-scanning]] stays on the Photo Picker, so no declaration.
- **Background location** — the form, the ≤ 30 s video and the prominent disclosure ([[07-phase-7-maps-and-location]] §3). The recommended design avoids it.

## 5. Purpose Strings and Review Clauses

App Store Review Guidelines as fetched on 2026-09-29 (the page showed no "last updated" date):

| Clause | What it says (short) | Where it bites DZZLO |
| --- | --- | --- |
| 2.5.1 | public APIs only; "phase out any deprecated features" | `UIRequiresFullScreen` is deprecated (§7) |
| 2.5.2 | no downloaded code that "introduces or changes features or functionality" | OTA (§8) |
| 2.5.4 | background services only for their intended purposes | tanker tracking, background upload |
| 2.5.11 | Siri/Shortcuts phrases tied to the app, no generic terms, no ads before fulfilment | App Intents (Phase 6) |
| 2.5.13 | face authentication through LocalAuthentication | biometric lock (§2) |
| 2.5.14 | explicit consent and a clear indication when recording user activity — "This includes any use of the device camera" | camera (Phase 4) |
| 2.5.15 | file pickers include Files and iCloud documents | document picker (Phase 3) |
| 2.5.16 | widgets, extensions and notifications related to the app; (a) every App Clip feature in the main app, no ads in clips | `DzzloWidgets`, `DzzloClip` |
| 3.1.1 / 3.1.3(c), (e), (f) | digital unlocks use IAP; enterprise sales, physical goods and free companion apps are the exceptions | web-billed dealer subscriptions fit 3.1.3(c); fuel is a physical good (e); no "buy on the web" calls to action on the Indian storefront |
| 4.4 | extensions carry no marketing, ads or IAP | widgets, NSE |
| 4.5.3 / 4.5.4 | no spam through push or Live Activities; promotions only with an in-app opt-in and opt-out; no sensitive data in pushes | balances in notifications, price-revision pushes |
| 4.7 | HTML5 / JavaScript mini apps allowed | OTA framing (§8) |
| 4.8 | a third-party primary login needs an equivalent option | OTP on own accounts doesn't trigger it; adding Google sign-in later would |
| 5.1.1(ii)–(v), (ix) | truthful purpose strings; data minimisation; no manipulation; in-app account deletion; regulated finance submitted by a legal entity | every string; `DeleteAccount` sits in the `SettingsNavigator` both role drawers mount (`src/navigation/Guest/Main.js:102-103`); a company developer account is the safe choice (no ruling found either way) |
| 5.1.2 | disclose third-party sharing, including with AI | analytics SDKs |
| 5.1.5 | location only when directly relevant, with consent | Phase 7 |

**What passes 5.1.1(ii).** "Clearly and completely": name the feature, the data and the moment.

| Fails | Passes |
| --- | --- |
| "$(PRODUCT_NAME) needs Location access for good user experience!" | "DZZLO uses your location while a delivery is in progress, so your customer can see when the tanker will arrive." — only once that feature exists |
| "Camera access is required." | "DZZLO uses the camera to scan the QR code on a GST e-invoice and to photograph delivery slips you attach to an order." |
| "Face ID is used for security." | "DZZLO uses Face ID to unlock the app, so only you can open your ledger and invoices." |

Each passing string describes a real, shipping feature. A string for a feature that doesn't exist is as risky as a vague one.

**Play's forms and limits:**

- **Foreground-service types:** apps targeting 14+ declare each type in Play Console — description, impact if deferred, **video link**, use case. `dataSync` is capped at 6 h in every 24 h and can't start from `BOOT_COMPLETED` on 15+ (Play suggests user-initiated data-transfer jobs instead); `specialUse` is reviewed.
- **Full-screen intents:** from Android 14 only calling and alarm apps get `USE_FULL_SCREEN_INTENT` by default (the declaration opened 31 May 2024; enforcement from 22 Jan 2025). DZZLO doesn't qualify — stay out.
- **Exact alarms:** `SCHEDULE_EXACT_ALARM` isn't pre-granted on fresh Android 14+ installs, and `USE_EXACT_ALARM` is restricted by policy. Stay out: inexact reminders, and `setExact` with an `OnAlarmListener` only while the app is alive.
- **Target API:** since 31 Aug 2026 new apps and updates must target API 36 (an extension to 1 Nov 2026 exists) — the app already does.

## 6. Extension Targets and Signing

**Targets and bundle ids.** An extension's bundle id must start with the host app's.

| Target | Bundle id | App Groups | Status |
| --- | --- | --- | --- |
| App | `in.vsyst.dzzlooms` | `group.in.vsyst.dzzlooms.onesignal`; `group.in.vsyst.dzzlooms.shared` from Phase 5 | today (+ Phase 5) |
| OneSignal NSE | `in.vsyst.dzzlooms.OneSignalNotificationServiceExtension` | `group.in.vsyst.dzzlooms.onesignal` | today |
| `DzzloWidgets` | `in.vsyst.dzzlooms.DzzloWidgets` | `group.in.vsyst.dzzlooms.shared` | [[05-phase-5-notifications-and-live-status]] |
| `DzzloClip` | `in.vsyst.dzzlooms.Clip` | its own decision ([[08-phase-8-instant-experiences-and-links]] §4) | optional |

All sign with team `YT955YZMZU`; the NSE sets `CODE_SIGN_STYLE = Automatic` (`project.pbxproj:520, 563`). Automatic signing generates each target's App ID and profile, but **App Groups, the APNs `.p8` key, broadcast channels and App Clip experiences are account-level steps the account holder does by hand**. App Groups are registered on the developer site (Apple guarantees uniqueness) and double as keychain access groups.

**The version oddity.** The NSE's `MARKETING_VERSION` is `1.0` (`project.pbxproj:537, 581` in the working tree) while the app's is `1.79` (`:458, 492`). App Store Connect usually warns when an extension's short version differs from its parent's: align every extension with the app in the release that adds a target, and pin it with a config test so the next target can't drift.

**TestFlight.** Every extension ships inside the app archive — one upload. Test the NSE, widgets and clip from the TestFlight build, not only from a debug run: signing, App Groups and push environments differ. The entitlements file says `aps-environment = development`; whether Xcode's export rewrites it from the distribution profile wasn't verified — check the archived app's entitlements once.

**Android signing — the passwords must leave the repo.** `android/gradle.properties` is **tracked by git** and holds the upload-key values at lines 46–49 (`MYAPP_UPLOAD_STORE_FILE`, `MYAPP_UPLOAD_KEY_ALIAS`, `MYAPP_UPLOAD_STORE_PASSWORD`, `MYAPP_UPLOAD_KEY_PASSWORD`). Never print them, never paste them into a ticket or a PR. The fix, which the repo's own checklist asks for (item 14):

```bash
# ~/.gradle/gradle.properties — outside every repo; Gradle reads it for all builds
MYAPP_UPLOAD_STORE_FILE=<path to the keystore>
MYAPP_UPLOAD_KEY_ALIAS=<alias>
MYAPP_UPLOAD_STORE_PASSWORD=<new password>
MYAPP_UPLOAD_KEY_PASSWORD=<new password>
```

1. Put the four properties in `~/.gradle/gradle.properties` on each build machine (or in CI secrets), then delete lines 46–49 from the tracked file. `android/app/build.gradle:99-106` already reads them as Gradle properties, so nothing else changes.
2. **Rotate.** The keystore file itself is untracked (`.gitignore`: `*.keystore`), so what leaked is the passwords — change them with the JDK's `keytool`. If the keystore file could ever have left the machine (the audit didn't check remote history), ask Play Console for an upload-key reset instead.
3. Pin it: a config test fails if `android/gradle.properties` contains `MYAPP_UPLOAD_` — asserting a boolean (`expect(/MYAPP_UPLOAD_/.test(text)).toBe(false)`), so a red run prints `true`, never the file ([[02-phase-2-dependency-diet]] §5.6).
4. Whether to rewrite git history is the user's decision, like every push.

**Play App Signing** is the model the repo checklist assumes ("Verify the upload key matches what the Play Console expects"): Google holds the app-signing key, you sign uploads with the upload key, and a lost or leaked upload key can be reset through Play Console (Play-side detail, not from this course's research). Separately, Android developer verification starts on 30 Sep 2026 in Brazil, Indonesia, Singapore and Thailand and goes global on certified devices in 2027; how it will treat the Firebase App Distribution APKs testers sideload is an open question to settle before then.

## 7. Build Hygiene

| Item | Today (verified 2026-09-29) | Do |
| --- | --- | --- |
| R8 / ProGuard | off: `enableProguardInReleaseBuilds = false` (`android/app/build.gradle:64`), empty `proguard-rules.pro` | turn it on with keep rules for reflection-heavy SDKs (OneSignal, Firebase) and a full device regression — repo checklist item 4 describes the rollout |
| APK vs AAB | `build-release-apk.sh:39` runs `assembleRelease`: one universal APK of **106,793,519 bytes** carrying 23 `.so` × 4 ABIs (`reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64`, `gradle.properties:28`); no `splits`, `abiFilters` or `bundle {}` | ship an AAB to Play (`./gradlew bundleRelease`, README:181-210, not scripted); keep the APK for App Distribution testers |
| 16 KB pages | the 2026-09-29 release APK: **all 23 arm64-v8a libraries** have `p_align = 16384` and sit uncompressed at 16 KB-aligned offsets | re-check every release that adds a native library (below) |
| Edge-to-edge | `edgeToEdgeEnabled=false` (`gradle.properties:44`) | ignored on Android 16 with targetSdk 36 — check v1 screens on an Android 16 device for content under the bars |
| Predictive back | on by default for targetSdk 36 on Android 16: `onBackPressed()` isn't called, `KEYCODE_BACK` isn't dispatched | 5 live files use `BackHandler`: the three `Orders/index.js` screens, `hooks/useBottomSheetBackHandler.js`, `hooks/useBSMBackHandler.js` — test each with gesture navigation on Android 16; the temporary opt-out is `android:enableOnBackInvokedCallback="false"` |
| iOS archive env | the bundle phase hard-codes `export APP_ENV=testing` (`project.pbxproj:291`, at HEAD and in the working tree) while README:238-244 says the repo ships `production` | a config test that pins the phase, or env selection moved into a scheme/xcconfig ([[02-phase-2-dependency-diet]]) |

**16 KB, precisely.** Google's page: "Starting February 1, 2027, if your app updates don't support 16 KB memory page sizes, you won't be able to release these updates" — for apps targeting API 35+ on 64-bit devices. Older messaging said 1 Nov 2025, and search results cite an extension to 31 May 2026; the current page supersedes both, so re-check it before any release near the date. AGP 8.5.1+ and NDK r28+ align by default; the app is on AGP 8.12.0 and NDK 27.1, and RN's Gradle plugin adds `-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON` to CMake builds. Kotlin- and Swift-only modules add no `.so`; Nitro modules and C++ Turbo Modules do.

```bash
zipalign -c -P 16 -v 4 android/app/build/outputs/apk/release/app-release.apk
# or: check_elf_alignment.sh app-release.apk
# or, per library: llvm-objdump -p libfoo.so | grep LOAD    → expect "align 2**14"
```

A 16 KB dialog once seen on an emulator **debug** build wasn't re-examined; the release build is what Play checks.

**The iOS floor.** Since **28 Apr 2026** App Store Connect accepts only apps built with the iOS 26 SDK or later. With the iOS 27 SDK (Xcode 27, shipped 14 Sep 2026) the UIScene life cycle is mandatory — the app already has its `SceneDelegate`, inside `AppDelegate.swift`. `UIDesignRequiresCompatibility` is ignored "when you build for iOS 27", so Liquid Glass can't be opted out of: native-stack headers, alerts, date pickers and keyboards change look. `UIRequiresFullScreen` (`Info.plist:90-91`) is deprecated; on iPhone in resizable environments iOS 27 turns it into discrete resizing that honours the supported orientations. And from September 2026 App Store Connect asks whether an app has social-media capabilities before a new version can be submitted.

## 8. OTA Updates After CodePush

**CodePush is gone.** Microsoft retired App Center, CodePush included, on **31 Mar 2025**; `react-native-code-push` is archived (last release 9.0.1, 2024-12-19) with no New-Architecture support. The app isn't wired to it — all three importers are dead files and the package isn't installed — but four `CODEPUSH_*` env names still reach the live bundle through `src/constants/system.js:1-16`; [[02-phase-2-dependency-diet]] removes them.

**What the stores allow:**

- **Apple 2.5.2:** "Apps should be self-contained in their bundles … nor may they download, install, or execute code which introduces or changes features or functionality of the app". **4.7** allows "HTML5 and JavaScript mini apps and mini games". The Developer Program License Agreement (quoted via Bitrise) allows downloaded interpreted code only if it "(a) does not change the primary purpose of the Application …, (b) does not create a store or storefront for other code or applications, and (c) does not bypass signing, sandbox, or other security features of the OS".
- **Google Play:** an app "may not download executable code (such as dex, JAR, .so files) from a source other than Google Play. This restriction does not apply to code that runs in a virtual machine or an interpreter where either provides indirect access to Android APIs (such as JavaScript in a webview or browser)."
- **Conflicts on record:** sources number the Apple clause differently (DPLA 3.3.1(B) vs "3.3.2"), and Bitrise's summary table conservatively marks new JS-only features as not allowed over the air on iOS — its reading, not policy text. Industry practice treats JS bug fixes as fine and feature changes as a review risk.

Source: https://bitrise.io/blog/post/what-app-stores-allow-with-ota-updates-apple-and-google-policy-explained

**The consequence for this course: OTA never ships native code, a new native module or a new permission — so every phase in this course is a store release.** And a JS bundle that calls a new or changed spec must only reach binaries that contain that native code: bump the runtime/binary version whenever `specs/` or anything under `ios/` or `android/` changes.

**Route 1 — Hot Updater (no Expo; the default).** Self-hosted, bare-first, New-Architecture support. `@hot-updater/react-native` 0.36.16 (2026-09-29): 42,601 downloads a week, 114 releases in 12 months, `1.0.0-rc.19` on the `rc` tag, 1,743 stars, 18 open issues. Storage plugins for AWS S3, Supabase Storage and Cloudflare R2; database plugins for Supabase, PostgreSQL and Cloudflare D1; a `bare({ enableHermes: true })` build plugin; bundle diffing that can ship a small Hermes change as "a ~600 KB patch". Its licence and RN 0.84 test matrix weren't captured — read both first. The steps in outline (take the exact commands from its README at the version you pin):

1. Choose storage + database (R2 or S3 plus Postgres, say) and stand them up outside the app repos.
2. Add the SDK and the `bare({ enableHermes: true })` build plugin; mock the SDK in `jest.setup.js` before any code imports it.
3. One channel per environment (testing, production), matching the `slave` / `master` release flow.
4. Key every bundle to the app version or a native fingerprint; a CI check fails when the fingerprint changes without a version bump.
5. Device check: install a release build, publish a JS-only fix to the testing channel, watch it arrive, then roll it back.

**Route 2 — EAS Update (the Expo track only).** In a bare app it needs Expo modules: `npx install-expo-modules@latest`, `npx expo install expo-updates`, `npx pod-install`; then `expo.modules.updates.EXPO_UPDATE_URL` / `…EXPO_RUNTIME_VERSION` meta-data in `AndroidManifest.xml`, `EXUpdatesURL` / `EXUpdatesRuntimeVersion` in `Expo.plist`, and channels through `UPDATES_CONFIGURATION_REQUEST_HEADERS_KEY`. "You can use EAS Update without any other EAS services." Pricing (Codemagic, 2026-08-19): 50,000 MAU included on the Production plan, then per MAU. Every Expo SDK pairs with one RN minor — SDK 56 ↔ 0.85, 57 ↔ 0.86, 58 (preview) ↔ 0.88 — and **nothing pairs with 0.84 or 0.87**.

> **After the upgrade to 0.87:** the Expo track still isn't open — no SDK pairs with 0.87. It opens on 0.85 or 0.86 (SDK 56/57, which also need iOS 16.4+) or on 0.88 with SDK 58. Hot Updater doesn't depend on the pairing.

## 9. Store Rating and Review: Ask Once, After a Win

**The idea, simply.** Both stores have a built-in rating sheet: stars and an optional review, without leaving the app. The app may *ask* for it; the operating system decides whether it actually appears, and never tells the app either way. So the whole job is choosing the moment — after something went right, rarely, never from a button — and giving Help a plain link to the store page for anyone who wants to rate on their own.

**Where DZZLO stands** (read-only, `release/v1_79` at `e29f0e5d`, 2026-09-30):

- **One rating.** The App Store India listing shows version 1.78 (released 2026-06-24) with **1 rating**, average 5.0; the Singapore and US storefronts show none. The Play listing ("Updated on 23 Jun 2026", Business) carried no rating count in the fetched page.
- **Nothing asks.** No review library is installed (`package.json`), no screen asks, and Help has no rating row.
- **Store URLs, three copies, mixed storefronts:** `src/components/Error/ErrorMessage.js:21-26`, `src/components/Error/index.js:22-31` (`STORE_URLS`) and `src/helpers/OneSignal/index.js:7-12`. The iOS "open" URL is `itms-apps://itunes.apple.com/us/app/apple-store/id1553062924?mt=8/` — old host, US storefront, a wrong slug, a trailing slash; the "check" URL is `https://apps.apple.com/sg/app/dzzlo-oms/id1553062924` (Singapore). The one rating is on the Indian storefront.
- **No invoice sharing yet.** The only share handler ever written is commented out (`src/components/Download/invoiceHTML/ShowInvoice.js:284-338`) and no live file imports `Share`, so the "invoice shared" trigger arrives with [[03-phase-3-files-share-and-pdf]].
- **Hindi.** The sheet's words come from the OS, which follows the languages the app *declares*. DZZLO declares only English — on purpose: v1.79 removed the OS-level Hindi registration by the user's decision of 2026-09-25, and `src/i18n/__tests__/locales.config.test.js` pins the absence of `CFBundleLocalizations`. So a Hindi-first iPhone user will probably see an English sheet _(unverified — device check D2)_; Android's card follows the Play Store's language _(unverified)_. The declaration returns with the release that unlocks Hindi, not with this feature.

### 9.1 The rules, verbatim

**Apple** — App Store Review Guidelines, read 2026-09-30, when the page showed "Updated: June 8, 2026" (§5's read a day earlier saw no date — [[11-reference]] §2.7). Neither the 13 Nov 2025 nor the 8 Jun 2026 revision touched ratings.

| Clause | The text | What it means here |
| --- | --- | --- |
| 5.6.1 App Store Reviews | "Use the provided API to prompt users to review your app; this functionality allows customers to provide an App Store rating and review without the inconvenience of leaving your app, and we will disallow custom review prompts." | StoreKit's own sheet and nothing home-made: no look-alike, no star picker of ours |
| 3.2.2(x) | "Apps must not force users to rate the app, review the app, download other apps, or other store-related actions in order to access functionality, content, or use of the app." | nothing waits on a rating — orders, invoices and Help work the same whether anyone rates or not |
| 5.6.3 Discovery Fraud | "Manipulating any element of the App Store customer experience such as charts, search, reviews, or referrals to your app erodes customer trust and is not permitted." | no review swaps, no paid review services |
| Introduction | "If we find that you have attempted to manipulate reviews, inflate your chart rankings with paid, incentivized, filtered, or fake feedback, or engage with third-party services to do so on your behalf, we will take steps to preserve the integrity of the App Store, which may include expelling you from the Apple Developer Program." | no reward for a rating, and no filter that sends only happy users to the sheet |

**Google Play** — the policy "User Ratings, Reviews, and Installs" bars "inflating product ratings, reviews, or install counts by illegitimate means, such as fraudulent or incentivized reviews and ratings"; its examples include asking for a rating while offering an incentive (the research fetch summarised that example — re-read the page before quoting it). The In-App Review guidelines (overview last updated 2026-01-30) add three rules:

- **No question first.** "Your app shouldn't ask the user any questions before or while presenting the rating button or card, including questions about their opinion (such as "Do you like the app?") or predictive questions (such as "Would you rate this app 5 stars")."
- **No button.** "…you should not have a call-to-action option (such as a button) to trigger the API, as a user might have already hit their quota and the flow won't be shown, presenting a broken experience to the user. For this use case, redirect the user to the Play Store instead."
- **Don't touch the card.** "Surface the card as-is, without tampering or modifying the existing design in any way, including size, opacity, shape, or other properties." And: "Don't add any overlay on top of the card or around the card."

**So: no pre-prompt on either platform, and no reward of any kind.** Android forbids the "Enjoying DZZLO?" question outright. On iOS, "a pre-question is fine as long as it doesn't gate the API" is developer lore, not Apple text — no current Apple page says it either way — and a Yes/No question that sends "No" to a feedback form and only "Yes" to the sheet is exactly the "filtered … feedback" the Introduction names. Apple's sheet already opens with `Enjoying <App>?` (as an iOS 26.2 simulator shows it in a public bug report). Parity settles it: neither platform gets one. An unhappy dealer reaches the team through Help → Contact Us, which Apple asks apps to keep easy to find. Never a discount, a trial extension or a subscription benefit for a rating: Play's example, Apple's "incentivized" and 3.2.2(x) all say no. Replies to reviews in App Store Connect and Play Console follow the same line — no personal information, spam or marketing (5.6.1), and never a request for a higher rating (Play).

### 9.2 What the platforms do

| | iOS | Android |
| --- | --- | --- |
| The call | `AppStore.requestReview(in: UIWindowScene)` — StoreKit, iOS 16.0, `@MainActor`. On iOS 15: `SKStoreReviewController.requestReview(in:)` (iOS 14.0, deprecated in 18.0: "Use AppStore.requestReview(in:).") | Play In-App Review, `com.google.android.play:review:2.0.2` (Maven, 2024-10-18; still the latest on 2026-09-30): `ReviewManagerFactory.create(context)` → `requestReviewFlow()` (`Task<ReviewInfo>`) → `launchReviewFlow(activity, reviewInfo)` (`Task<Void>`) |
| Who can get it | DZZLO's floor is iOS 15.1, so the module carries **both** branches until the floor reaches 16.0 | Android 5.0 (API 21)+ with the Play Store — every Play install (minSdk 24) |
| How often | "a maximum of three times within a 365-day period" per device for someone who hasn't rated; after a rating, only for a new version and after 365 days; people can switch the prompts off for all apps | "a time-bound quota" — "The specific value of the quota is an implementation detail, and it can be changed by Google Play without any notice"; two calls in "less than a month" may show nothing |
| What the app learns | nothing — "this method may not present an alert", and it returns nothing | nothing — "The API does not indicate whether the user reviewed or not, or even whether the review dialog was shown"; on an error, "do not inform the user or change your app's normal flow" |
| From a tap? | "don't call requestReview() or requestReview(in:) in response to a button tap or other user action" | no — the "No button" rule |

SwiftUI's `RequestReviewAction` (iOS 16.0) works only inside SwiftUI; DZZLO's screens are React Native views hosted in UIKit, so the module uses the scene call with the foreground-active `UIWindowScene`, found through `UIApplication.connectedScenes` (both iOS 13.0 in the iOS 27.0 SDK headers). The Android `ReviewInfo` "is only valid for a limited amount of time", so the module requests it right before launching, never ahead.

**By build type** — the table that saves a day of "it doesn't work":

| Build | iOS | Android |
| --- | --- | --- |
| Development (Xcode run, local build) | "StoreKit always displays the rating and review request view" — development-*signed*, not `__DEV__` _(inference)_ — except on iOS seed (beta) builds, below | only if this Google account installed the app once from the **internal test track**; after that "you can deploy new versions of the app locally to that device" |
| Beta | TestFlight: "this method has no effect" | Firebase App Distribution: the app isn't in the tester's Play library, so nothing _(inferred from Google's troubleshooting table)_ |
| Play test tracks | — | internal test track: shows, and "The quota limits are not enforced"; internal app sharing: shows, but "reviews can't be submitted" — Submit is disabled |
| Production | at most 3 a year per device, unless switched off | the unpublished quota |
| Unit tests | nothing to observe — test the scene choice, not the sheet | `FakeReviewManager`: "No UI is shown and no review is performed" |

**iOS 26 and 27 — developer reports, not Apple statements:**

- **iOS 26.1:** the sheet's "Not Now" button was disabled — "there is no way to opt out, unless the user taps on the stars first" (Apple Developer Forums thread 807408; Apple DTS could not reproduce it; a developer reported it fixed in 26.2). The same report against `expo-store-review` (expo#41116) was closed as "a change in iOS". One more reason to ask only at a happy moment.
- **iOS 26.5:** development builds on the 26.5 betas stopped showing the sheet; the poster relayed Apple's reply that "review requests are not allowed in seed", and another developer saw nothing on 26.5.1 and 26.5.2 either (thread 821981). Test on a release iOS and treat the 26.5.x reports as open.
- **iOS 27** (released 2026-09-14): nothing found from Apple or developers (searched 2026-09-30). Record what a development build does on it in the PR.

### 9.3 Library or module?

| Package | Latest (date) | Downloads, 21–27 Sep 2026 | Architecture | Health (2026-09-30) | Verdict |
| --- | --- | --- | --- | --- | --- |
| `react-native-store-review` | 0.5.0 (2026-04-15; before it 0.4.3, 2023-10-26) | 57,067 | Turbo Module (`RNStoreReviewSpec`) with an old-arch fallback | 780★, 2 open issues, 0 open PRs; Android buildscript pins AGP 7.0.4, defaults to `review` 2.0.1 | **the fallback** — correct iOS calls, but a `void` API and log-only failures give analytics nothing |
| `react-native-rate-app` | 2.1.3 (2026-09-07) | 7,171 | New-Architecture-only Turbo Module, Kotlin, `review` 2.0.2 | 258★, 2 issues + 3 PRs, one maintainer | acceptable, not chosen — Galaxy Store, AppGallery and Amazon extras DZZLO doesn't need, and its store-link helper calls `canOpenURL` (so `LSApplicationQueriesSchemes` plus `<queries>`) |
| `react-native-in-app-review` | 4.4.2 (2025-09-03) | 237,509 | legacy bridge (`RCT_EXTERN_MODULE`, `ReactContextBaseJavaModule`), no `codegenConfig` | 728★, 31 open issues + 26 open PRs, last commit 2025-09-03 | **SKIP** — the compat layer, plus `play-services-base` 17.5.0 and Huawei code |
| `react-native-rate` | 1.2.12 (2023-01-23) | 35,162 | legacy | "unmaintained" (React Native Directory) | **SKIP** |
| `expo-store-review` | 57.0.3 (2026-09-11, SDK 57); `next` 58.0.1 (2026-09-29) | 1,120,167 | Expo module | active (expo/expo) | Expo track only (below) |

**Verdict: write our own `NativeStoreReview` — a WRAP in this course's terms** (the research note calls it BUILD, meaning "ours, not a library"). Every package above wraps the same two OS calls in 20–40 lines of native logic. The research note sizes ours at about 95 lines with the boilerplate, about 40 of them logic _(est.)_; the version in §9.4, split so both native cores can be unit-tested, prints at about 105 lines of code. It returns an outcome string analytics can use; it builds under the app's own Gradle and CocoaPods settings, not a third-party buildscript pinned to AGP 7 when 0.87 brings AGP 9; and its one new dependency is `com.google.android.play:review:2.0.2` — the core artifact, not `review-ktx`, whose coroutine helpers a promise-based module doesn't need. If the team would rather own no native code here, put `react-native-store-review` 0.5.0 behind the same facade.

### 9.4 `NativeStoreReview`, test-first

Phase 1's recipe and names ([[01-phase-1-foundations]] §5, card in [[11-reference]] §5), in its order: Jest red → native red → green → device. The spec is `specs/NativeStoreReview.ts`, the iOS files live in `ios/dzzlo_oms_app/StoreReview/`, the Kotlin package is `` `in`.vsyst.dzzlooms.storereview ``, and the facade is `src/native/storeReview.js`.

**The contract** — one method that resolves with what the app can observe and never rejects:

```ts
// specs/NativeStoreReview.ts
import type {TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';

export interface Spec extends TurboModule {
  /**
   * Asks the OS for its store review sheet. Resolves with what the app can see:
   * 'requested' | 'no_scene' | 'no_activity' | 'error:<ReviewErrorCode>'.
   */
  requestReview(): Promise<string>;
}

export default TurboModuleRegistry.getEnforcing<Spec>('NativeStoreReview');
```

Add `"NativeStoreReview": "RCTNativeStoreReview"` to the `ios.modulesProvider` map of the one `codegenConfig` Phase 1 created. **Checked 2026-09-30** by running RN 0.84.1's codegen CLIs from the app's `node_modules` on a scratch copy of this spec: iOS gets `@protocol NativeStoreReviewSpec <RCTBridgeModule, RCTTurboModule>` with `- (void)requestReview:(RCTPromiseResolveBlock)resolve reject:(RCTPromiseRejectBlock)reject;` and `NativeStoreReviewSpecJSI`; Android gets `in.vsyst.dzzlooms.specs.NativeStoreReviewSpec` with `public abstract void requestReview(Promise promise);`.

**Red 1 — Jest.** The facade's test, the global mock and the wiring pin:

```js
// src/native/__tests__/storeReview.test.js — Tier 1; the spec is mocked (Jest has no __turboModuleProxy)
jest.mock('../../../specs/NativeStoreReview', () => ({
  __esModule: true, default: { requestReview: jest.fn() },
}));
import NativeStoreReview from '../../../specs/NativeStoreReview';
import { requestStoreReview } from '../storeReview';

it('hands back what the OS let us observe', async () => {
  NativeStoreReview.requestReview.mockResolvedValueOnce('no_scene');
  await expect(requestStoreReview()).resolves.toBe('no_scene');
});
it('never rejects — Google: "do not inform the user or change your app\'s normal flow"', async () => {
  NativeStoreReview.requestReview.mockRejectedValueOnce({ code: 'E_GONE' });
  await expect(requestStoreReview()).resolves.toBe('error:E_GONE');
});
```

```js
// jest.setup.js — beside NativeAppInfo's mock
jest.mock('./specs/NativeStoreReview', () => ({
  __esModule: true,
  default: { requestReview: jest.fn(() => Promise.resolve('requested')) },
}));

// src/native/__tests__/storeReview.config.test.js — the shape of Phase 1's appInfo.config.test.js
import fs from 'fs';
import path from 'path';
import { readCode } from '../../test/sourceText';

const ROOT = path.resolve(__dirname, '../../..');
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

it('wires NativeStoreReview on both platforms and mocks the spec', () => {
  expect(JSON.parse(read('package.json')).codegenConfig.ios.modulesProvider)
    .toMatchObject({ NativeStoreReview: 'RCTNativeStoreReview' });
  expect(read('android/app/src/main/java/in/vsyst/dzzlooms/MainApplication.kt'))
    .toMatch(/^\s*add\(NativeStoreReviewPackage\(\)\)/m);
  expect(read('android/app/build.gradle')).toContain('com.google.android.play:review:2.0.2');
  expect(read('jest.setup.js')).toContain("jest.mock('./specs/NativeStoreReview'");
});
it('Help never calls the review API — its row opens the store (§9.6)', () => {
  expect(readCode(path.join(ROOT, 'src/screens/Common/Help/index.js')))
    .not.toMatch(/NativeStoreReview|native\/storeReview|maybeRequestReview/);
});
```

**Red 2 — native.** The decision sits in plain classes the test targets reach: on iOS, "pick the foreground-active scene, ask once"; on Android, the Play flow with an injected `ReviewManager`. Both suites fail to compile until the cores exist — as in Phase 1, the one time a build failure counts as red.

```swift
// ios/dzzlo_oms_appTests/StoreReviewCoreTests.swift
import XCTest

final class StoreReviewCoreTests: XCTestCase {
  private struct FakeScene: Equatable { let name: String; let active: Bool }

  func testNoForegroundSceneMeansNoRequest() {
    var asked = 0
    let asker = ReviewAsker(scenes: { [FakeScene(name: "background", active: false)] },
                            isForegroundActive: { $0.active }, request: { _ in asked += 1 })
    XCTAssertEqual(asker.ask(), "no_scene")
    XCTAssertEqual(asked, 0)
  }

  func testAsksOnceOnTheForegroundActiveScene() {   // iPad, two windows
    let left = FakeScene(name: "left", active: false), right = FakeScene(name: "right", active: true)
    var asked: [FakeScene] = []
    let asker = ReviewAsker(scenes: { [left, right] }, isForegroundActive: { $0.active },
                            request: { asked.append($0) })
    XCTAssertEqual(asker.ask(), "requested")
    XCTAssertEqual(asked, [right])
  }
}
```

```kotlin
// android/app/src/test/java/in/vsyst/dzzlooms/storereview/StoreReviewCoreTest.kt
package `in`.vsyst.dzzlooms.storereview

import android.app.Activity
import android.os.Looper
import com.google.android.play.core.review.testing.FakeReviewManager
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.Robolectric
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.Shadows.shadowOf

@RunWith(RobolectricTestRunner::class)   // FakeReviewManager needs a real Context
class StoreReviewCoreTest {
  private val core = StoreReviewCore(FakeReviewManager(RuntimeEnvironment.getApplication()))

  @Test fun noActivityMeansNoRequest() {
    val outcomes = mutableListOf<String>()
    core.requestReview(activity = null) { outcomes += it }
    assertEquals(listOf("no_activity"), outcomes)
  }

  @Test fun aCompletedFakeFlowReportsRequestedOnce() {
    val activity = Robolectric.buildActivity(Activity::class.java).setup().get()
    val outcomes = mutableListOf<String>()
    core.requestReview(activity) { outcomes += it }
    shadowOf(Looper.getMainLooper()).idle()        // whether the Task listeners need this: unverified
    assertEquals(listOf("requested"), outcomes)
  }
}
```

`FakeReviewManager` is "completely self-contained and does not interact with the Play Store"; it "only fakes the API method result by always providing a fake ReviewInfo object and returning a success status", and is "intended for unit-tests and early development iterations only". The test needs Phase 1's JUnit line plus Robolectric 4.15.1 from [[05-phase-5-notifications-and-live-status]] §6.6 (add those two lines here if this phase comes first). **Unverified:** whether `FakeReviewManager`'s tasks complete under Robolectric without idling the main looper; the app has no JVM test run yet. If Robolectric fights back, keep the two tests and prove the flow on D5–D7 below.

**Green, iOS.** Target membership as in Phase 1: `StoreReviewCore.swift` → app **and** `dzzlo_oms_appTests`; `RCTNativeStoreReview.mm` → app; the `.h` → none.

```swift
// ios/dzzlo_oms_app/StoreReview/StoreReviewCore.swift — the logic; no React imports
import StoreKit
import UIKit

/// The whole decision, with no UIKit in it: pick the foreground-active scene, ask once.
/// Generic because a host-less test bundle can't make a UIWindowScene; XCTest uses a stand-in.
struct ReviewAsker<Scene> {
  let scenes: () -> [Scene]
  let isForegroundActive: (Scene) -> Bool
  let request: (Scene) -> Void

  /// "requested" means StoreKit was asked; never that a sheet appeared.
  func ask() -> String {
    guard let scene = scenes().first(where: isForegroundActive) else { return "no_scene" }
    request(scene)
    return "requested"
  }
}

public final class StoreReviewCore: NSObject {
  /// UIKit and StoreKit, so main thread only: the adapter hops to the main queue first.
  @MainActor
  @objc public static func requestReview() -> String {
    ReviewAsker<UIWindowScene>(
      scenes: { UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene } },
      isForegroundActive: { $0.activationState == .foregroundActive },
      request: { scene in
        if #available(iOS 16.0, *) {
          AppStore.requestReview(in: scene)                  // iOS 16.0+, @MainActor
        } else {
          SKStoreReviewController.requestReview(in: scene)   // iOS 14.0 API: the iOS 15 branch; deprecated in 18.0
        }
      }
    ).ask()
  }
}
```

`RCTNativeStoreReview.h` is Phase 1's header with the names swapped — `#import <Foundation/Foundation.h>` and `#import <DzzloOmsSpec/DzzloOmsSpec.h>`, then `@interface RCTNativeStoreReview : NSObject <NativeStoreReviewSpec>` between `NS_ASSUME_NONNULL_BEGIN` and `NS_ASSUME_NONNULL_END` — and is imported only from `.mm` files. The adapter:

```objc
// ios/dzzlo_oms_app/StoreReview/RCTNativeStoreReview.mm
#import "RCTNativeStoreReview.h"

// Before the Swift header, as in Phase 1 §5.6: it also declares AppDelegate.swift's
// ReactNativeDelegate, whose superclass lives here.
#import <React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>
#import "dzzlo_oms_app-Swift.h"

@implementation RCTNativeStoreReview

+ (NSString *)moduleName { return @"NativeStoreReview"; }
// Phase 1's rule. Nothing UIKit happens at set-up; the one call below hops to the main queue itself.
+ (BOOL)requiresMainQueueSetup { return YES; }

- (void)requestReview:(RCTPromiseResolveBlock)resolve reject:(RCTPromiseRejectBlock)reject
{
  // Promise methods arrive on the module's own queue; StoreKit and UIKit want the main one.
  dispatch_async(dispatch_get_main_queue(), ^{
    resolve([StoreReviewCore requestReview]);   // never rejects: "no_scene" is an outcome, not an error
  });
}

- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:(const facebook::react::ObjCTurboModule::InitParams &)params
{ return std::make_shared<facebook::react::NativeStoreReviewSpecJSI>(params); }

@end
```

Then `cd ios && bundle exec pod install` and `grep -n 'NativeStoreReview' build/generated/ios/ReactCodegen/RCTModuleProviders.mm`. **Checked 2026-09-30, outside the repo:** `swiftc -typecheck` passes `StoreReviewCore.swift` and its XCTest against the iOS 27.0 simulator SDK at a 15.1 target, in Swift 5 mode (and in Swift 6 mode), with no deprecation warning for the iOS 15 branch; the emitted header declares `+ (NSString * _Nonnull)requestReview`. `clang -fsyntax-only` passes the `.h`/`.mm` against the Pods' public headers, the scratch-generated spec header and a `dzzlo_oms_app-Swift.h` from DerivedData with `StoreReviewCore` added. Two mutations prove the check bites: delete the promise method and clang warns "method 'requestReview:reject:' in protocol 'NativeStoreReviewSpec' not implemented"; drop the `React_RCTAppDelegate` import and Phase 1's "cannot find interface declaration for 'RCTDefaultReactNativeFactoryDelegate'" comes back. A full Xcode build and the device run are still the proof.

**Green, Android.** One dependency, a plain core, a thin module, a package, one registration line:

```groovy
// android/app/build.gradle → dependencies { }
implementation("com.google.android.play:review:2.0.2")
```

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/storereview/StoreReviewCore.kt
package `in`.vsyst.dzzlooms.storereview

import android.app.Activity
import com.google.android.play.core.review.ReviewException
import com.google.android.play.core.review.ReviewManager

/** Play In-App Review with no React Native in it, so JUnit can hand it a FakeReviewManager. */
class StoreReviewCore(private val manager: ReviewManager) {
  /** Calls [done] once: "requested" (Play was asked — never whether the card showed),
   *  "no_activity", or "error:<ReviewErrorCode>". */
  fun requestReview(activity: Activity?, done: (String) -> Unit) {
    if (activity == null) return done("no_activity")
    manager.requestReviewFlow().addOnCompleteListener { request ->
      if (!request.isSuccessful) {
        done("error:${(request.exception as? ReviewException)?.errorCode ?: "unknown"}")
        return@addOnCompleteListener
      }
      manager.launchReviewFlow(activity, request.result)
        .addOnCompleteListener { done("requested") }   // Google: the result says nothing about display
    }
  }
}
```

```kotlin
// NativeStoreReviewModule.kt — same package
package `in`.vsyst.dzzlooms.storereview

import com.facebook.react.bridge.Promise
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.UiThreadUtil
import com.google.android.play.core.review.ReviewManagerFactory
import `in`.vsyst.dzzlooms.specs.NativeStoreReviewSpec   // backticks here too: `in` is a Kotlin keyword

class NativeStoreReviewModule(reactContext: ReactApplicationContext) : NativeStoreReviewSpec(reactContext) {
  private val core by lazy { StoreReviewCore(ReviewManagerFactory.create(reactApplicationContext)) }

  override fun getName() = NAME

  // Never rejects. Starts on the main thread, as an activity would.
  override fun requestReview(promise: Promise) {
    UiThreadUtil.runOnUiThread {
      core.requestReview(reactApplicationContext.currentActivity) { promise.resolve(it) }
    }
  }

  companion object { const val NAME = "NativeStoreReview" }
}
```

```kotlin
// NativeStoreReviewPackage.kt — Phase 1's BaseReactPackage shape
package `in`.vsyst.dzzlooms.storereview

import com.facebook.react.BaseReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.module.model.ReactModuleInfo
import com.facebook.react.module.model.ReactModuleInfoProvider

class NativeStoreReviewPackage : BaseReactPackage() {
  override fun getModule(name: String, reactContext: ReactApplicationContext): NativeModule? =
    if (name == NativeStoreReviewModule.NAME) NativeStoreReviewModule(reactContext) else null

  override fun getReactModuleInfoProvider() = ReactModuleInfoProvider {
    mapOf(NativeStoreReviewModule.NAME to ReactModuleInfo(
      name = NativeStoreReviewModule.NAME, className = NativeStoreReviewModule.NAME,
      canOverrideExistingModule = false, needsEagerInit = false,
      isCxxModule = false, isTurboModule = true,
    ))
  }
}
```

```kotlin
// MainApplication.kt — in-app modules are not autolinked
import `in`.vsyst.dzzlooms.storereview.NativeStoreReviewPackage
// …
        PackageList(this).packages.apply {
          add(NativeAppInfoPackage())
          add(NativeStoreReviewPackage())
        },
```

The Kotlin was **not compiled here** (no `review` 2.0.2 artifact on this machine). What was read in RN 0.84.1's sources on 2026-09-30: `ReactContext.getCurrentActivity()` is a Java getter, so `reactApplicationContext.currentActivity` works from Kotlin, and `UiThreadUtil` is a Kotlin `object` with `runOnUiThread(Runnable)`.

**Green, JavaScript** — the facade:

```js
// src/native/storeReview.js
/**
 * The only importer of specs/NativeStoreReview.ts. Never rejects: a review request is a
 * nicety, and Google's rule is that an error must not change the app's flow.
 */
import NativeStoreReview from '../../specs/NativeStoreReview';

export async function requestStoreReview() {
  try {
    return await NativeStoreReview.requestReview(); // 'requested' | 'no_scene' | 'no_activity' | 'error:<code>'
  } catch (e) {
    return `error:${e?.code ?? 'unknown'}`;
  }
}
```

Like every module, this one is a store release: bump the OTA runtime version when `specs/` or native code changes (§8).

### 9.5 When to ask — `maybeRequestReview`

The rules, as starting values to tune from the numbers _(est.)_:

| Rule | Starting value | Why |
| --- | --- | --- |
| Only after a success | `order_placed` — the customer's order goes through (`add_order_msts`, `src/screens/Customer/NewOrder/index.js:87`); `order_delivered` — the dealer's status update to `DELIVERED` resolves (`src/screens/Dealer/Orders/components/OneOrder.js:261`); `invoice_shared` — from Phase 3's share (Capstone A) | Apple: ask "at the end of a sequence of events that they successfully complete" |
| Seen enough | ≥ 3 successes since the last ask **and** ≥ 7 days since first launch | the HIG's "demonstrated engagement"; Apple's sample waits for "at least four" completions — "This number is arbitrary" |
| Once per version | never twice for the same app version | Apple's sample |
| Spacing | ≥ 30 days between asks | the HIG: "at least a week or two"; Play's quota example: "less than a month" |
| Yearly cap | ≤ 3 asks in any 365 days | Apple's display cap — a fourth call wastes a good moment |
| Quiet after a problem | nothing within 7 days of a user-visible error | Keepsafe's 7-day crash suppression gave "a small but significant increase in avg. rating" (Phiture, 2019; one app, self-reported) |
| Pause | 2 s after the success screen appears, and only if the person is still there | Apple's sample waits 2 s; Google wants the card on the top layer |
| Never | first launch, onboarding, login and OTP, mid-entry, error screens, offline | the HIG, Apple's sample, Google |

**The state** — one JSON value per install (not per user or company: both quotas are per device and account), under `dzzlo.storeReview.v1` in the default AsyncStorage that 33 files already use and `jest.setup.js:50-53` already mocks. `promptsInLast365` holds timestamps, trimmed to the last 365 days on every read:

```json
{ "firstLaunchAt": 1790000000000, "successCount": 2, "lastPromptAt": null,
  "lastPromptVersion": null, "promptsInLast365": [], "lastErrorAt": null }
```

**The red tests** (`now` = 1 Oct 2026; the app version is 1.80):

| # | Given | Expect |
| --- | --- | --- |
| R1 | 2 successes | `too_few_successes` |
| R2 · R3 | first launch 6 days ago · exactly 7 | `too_new` · `ask` |
| R4 · R5 | an error 6 days ago · exactly 7 | `recent_error` · `ask` |
| R6 | already asked in 1.80 | `asked_this_version` |
| R7 · R8 | a new version, last ask 29 days ago · exactly 30 | `asked_recently` · `ask` |
| R9 · R10 | three asks inside 365 days · the oldest exactly 365 days old | `yearly_cap` · `ask` |
| R11 | the clock moved backwards | `too_new` — a broken clock never asks |
| R12 | the third success on day 8 | waits 2 s, asks once, logs `review_requested`, count back to 0 |
| R13 | the person left during the 2 s | `left_screen`, no ask |
| R14 | corrupt JSON in storage | starts again (`too_few_successes`), nothing throws |
| R15 | a trigger that isn't a success (`app_opened`) | `not_a_success`, nothing stored |

```js
// src/helpers/Review/__tests__/maybeRequestReview.test.js (the R1–R11 table and R12; R13–R15 follow the same shape)
jest.mock('../../../native/storeReview', () => ({ requestStoreReview: jest.fn(() => Promise.resolve('requested')) }));
jest.mock('../../../native/appInfo', () => ({ getAppInfo: () => ({ version: '1.80' }) }));
jest.mock('../../../utils/firebase', () => ({ logEvent: jest.fn() }));
import AsyncStorage from '@react-native-async-storage/async-storage';
import { requestStoreReview } from '../../../native/storeReview';
import { logEvent } from '../../../utils/firebase';
import { maybeRequestReview, shouldRequestReview, STORAGE_KEY } from '../maybeRequestReview';

const DAY = 86_400_000;
const NOW = Date.UTC(2026, 9, 1, 6, 30); // 1 Oct 2026, 12:00 IST
const ago = days => NOW - days * DAY;
const base = { firstLaunchAt: ago(10), successCount: 3, lastPromptAt: null,
  lastPromptVersion: null, promptsInLast365: [], lastErrorAt: null };
const older = { lastPromptVersion: '1.79', lastPromptAt: ago(40), promptsInLast365: [ago(40)] };

it.each([
  ['R1 two successes are not enough', { successCount: 2 }, 'too_few_successes'],
  ['R2 day 6 since first launch', { firstLaunchAt: ago(6) }, 'too_new'],
  ['R3 day 7 exactly', { firstLaunchAt: ago(7) }, 'ask'],
  ['R4 an error 6 days ago', { lastErrorAt: ago(6) }, 'recent_error'],
  ['R5 an error 7 days ago', { lastErrorAt: ago(7) }, 'ask'],
  ['R6 already asked in this version', { ...older, lastPromptVersion: '1.80' }, 'asked_this_version'],
  ['R7 new version, last ask 29 days ago', { ...older, lastPromptAt: ago(29), promptsInLast365: [ago(29)] }, 'asked_recently'],
  ['R8 new version, last ask 30 days ago', { ...older, lastPromptAt: ago(30), promptsInLast365: [ago(30)] }, 'ask'],
  ['R9 three asks inside 365 days', { ...older, promptsInLast365: [ago(300), ago(200), ago(40)] }, 'yearly_cap'],
  ['R10 the oldest of three is 365 days old', { ...older, promptsInLast365: [ago(365), ago(200), ago(40)] }, 'ask'],
  ['R11 the clock moved backwards', { firstLaunchAt: NOW + DAY }, 'too_new'],
])('%s', (_, patch, expected) => {
  expect(shouldRequestReview({ ...base, ...patch }, { now: NOW, appVersion: '1.80' })).toBe(expected);
});

beforeEach(async () => { await AsyncStorage.clear(); jest.clearAllMocks(); });

it('R12 the third success on day 8: waits 2 s, asks once, logs, resets the count', async () => {
  await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify({ ...base, firstLaunchAt: ago(8), successCount: 2 }));
  const wait = jest.fn(() => Promise.resolve());
  // RN's Jest AppState mock has no string currentState, so the "still here" check is injected.
  await expect(maybeRequestReview('invoice_shared', { now: NOW, wait, stillHere: () => true }))
    .resolves.toBe('requested');
  expect(wait).toHaveBeenCalledWith(2000);
  expect(requestStoreReview).toHaveBeenCalledTimes(1);
  expect(logEvent).toHaveBeenCalledWith('review_requested',
    { trigger: 'invoice_shared', outcome: 'requested', app_version: '1.80' });
  expect(JSON.parse(await AsyncStorage.getItem(STORAGE_KEY))).toMatchObject(
    { successCount: 0, lastPromptAt: NOW, lastPromptVersion: '1.80', promptsInLast365: [NOW] });
});
```

**Green:**

```js
// src/helpers/Review/maybeRequestReview.js
/**
 * When DZZLO asks the store for a rating: once, after a win. The rules are one pure
 * function; the rest is one AsyncStorage value, a 2-second pause and a log line.
 * Never throws — a review request must never change the app's flow.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AppState } from 'react-native';
import { getAppInfo } from '../../native/appInfo';
import { requestStoreReview } from '../../native/storeReview';
import { logEvent } from '../../utils/firebase';

const DAY = 24 * 60 * 60 * 1000;
export const STORAGE_KEY = 'dzzlo.storeReview.v1';
export const REVIEW_TRIGGERS = ['order_delivered', 'invoice_shared', 'order_placed'];
export const REVIEW_RULES = Object.freeze({ minSuccesses: 3, minDaysSinceFirstLaunch: 7,
  minDaysBetween: 30, maxPer365Days: 3, quietDaysAfterError: 7, delayMs: 2000 });

const freshState = now => ({ firstLaunchAt: now, successCount: 0, lastPromptAt: null,
  lastPromptVersion: null, promptsInLast365: [], lastErrorAt: null });
const save = state => AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(state)).catch(() => {});

/** Pure. 'ask', or the first rule that says no. A clock that went backwards never asks. */
export function shouldRequestReview(s, { now, appVersion }) {
  const R = REVIEW_RULES;
  const age = t => now - t; // negative when the clock moved back, so every wait below holds
  if (s.successCount < R.minSuccesses) return 'too_few_successes';
  if (age(s.firstLaunchAt) < R.minDaysSinceFirstLaunch * DAY) return 'too_new';
  if (s.lastErrorAt !== null && age(s.lastErrorAt) < R.quietDaysAfterError * DAY) return 'recent_error';
  if (s.lastPromptVersion === appVersion) return 'asked_this_version';
  if (s.lastPromptAt !== null && age(s.lastPromptAt) < R.minDaysBetween * DAY) return 'asked_recently';
  if (s.promptsInLast365.filter(t => age(t) < 365 * DAY).length >= R.maxPer365Days) return 'yearly_cap';
  return 'ask';
}

/** Call once at app start as well: the first call stamps firstLaunchAt. */
export async function loadReviewState(now = Date.now()) {
  let state = null;
  try {
    const saved = JSON.parse(await AsyncStorage.getItem(STORAGE_KEY));
    if (Number.isFinite(saved?.firstLaunchAt)) state = { ...freshState(now), ...saved };
  } catch { /* corrupt JSON: start again */ }
  if (!state) { state = freshState(now); await save(state); }
  const kept = Array.isArray(state.promptsInLast365) ? state.promptsInLast365 : [];
  return { ...state, promptsInLast365: kept.filter(t => now - t < 365 * DAY) };
}

/** A user-visible error: nothing is asked for the next 7 days. */
export async function recordReviewProblem(now = Date.now()) {
  await save({ ...(await loadReviewState(now)), lastErrorAt: now });
}

/** Right after a success screen appears. Resolves the reason it didn't ask, or the native outcome. */
export async function maybeRequestReview(trigger, { now = Date.now(),
  stillHere = () => AppState.currentState === 'active', // a screen can add navigation.isFocused()
  wait = ms => new Promise(resolve => setTimeout(resolve, ms)) } = {}) {
  if (!REVIEW_TRIGGERS.includes(trigger)) return 'not_a_success';
  const state = await loadReviewState(now);
  state.successCount += 1;
  const appVersion = getAppInfo().version;
  const verdict = shouldRequestReview(state, { now, appVersion });
  if (verdict !== 'ask') return save(state).then(() => verdict);
  await wait(REVIEW_RULES.delayMs);
  if (!stillHere()) return save(state).then(() => 'left_screen');
  const outcome = await requestStoreReview();
  await save({ ...state, successCount: 0, lastPromptAt: now, lastPromptVersion: appVersion,
    promptsInLast365: [...state.promptsInLast365, now] });
  logEvent('review_requested', { trigger, outcome, app_version: appVersion });
  return outcome;
}
```

**Run on 2026-09-30** in a scratch folder with the app's Jest 30, RN preset and AsyncStorage v3 mock (the app's `appInfo` and `firebase` modules stubbed): red on `Cannot find module '../maybeRequestReview'`, then 19 of 19 green across the three suites of §9.4–§9.6, and ESLint clean under the app's `eslint.config.js`. Mutation smokes: `<` → `<=` in the 30-day rule turns R8 red; deleting the once-per-version line turns R6 red.

**Where the calls go.** `loadReviewState()` once at app start (`App.js`), so `firstLaunchAt` means the first launch of the release that ships this. `maybeRequestReview('order_placed')` / `('order_delivered')` / `('invoice_shared')` right after each success UI renders — never awaited by the screen. `recordReviewProblem()` wherever a user-visible error is shown (`src/components/Error/ErrorMessage.js` renders them today). For device runs, seed `dzzlo.storeReview.v1` from a `__DEV__`-only action (first launch 8 days back, two successes); never ship a bypass.

**Android's "shared" is weak.** React Native's core `Share.share()` on Android "returns a Promise which will always be resolved with action being `Share.sharedAction`"; what react-native-share 12.3.1 resolves once WhatsApp takes the file wasn't checked. So on Android an invoice share counts as one of three, and the order triggers carry the weight; if the data shows the share trigger firing on cancelled shares, stop counting it on Android. The research also offers three rules left out of this starting set: production `PROJ_ENV` only, a remote kill switch, and no automatic ask within 365 days of someone opening "Rate DZZLO".

**Measure around the silence.** Neither API reports anything, so:

- **Events** through the app's wrapper, `logEvent` (`src/utils/firebase.js:21`): `review_requested` {trigger, outcome, app_version} and `review_link_opened` {source, opened}; a sampled `review_skipped` {reason} if the funnel needs it. GA4's app limits: names up to 40 characters, 25 parameters per event, values up to 100 characters.
- **Per release:** new ratings in App Store Connect (Ratings and Reviews, filtered to India and to the version) and in Play Console (ratings by app version, country, language, Android version, device), divided by `review_requested` per platform. From one iOS rating, the count is the first number that moves; resetting the summary rating (a HIG option) makes no sense at this volume.

### 9.6 The "Rate DZZLO" row in Help

Both stores endorse a link for the button, never the API. Apple: "you may include a persistent link to your App Store product page in your app's settings or configuration screens. Append the query parameter action=write-review to your product page URL to automatically open the App Store page where users can write a review." Google: "redirect the user to the Play Store instead".

| | Opens | Why |
| --- | --- | --- |
| iOS | `https://apps.apple.com/app/id1553062924?action=write-review` | Apple's documented form; no storefront in the path, which sidesteps the `/sg/` vs `/us/` question (whether the App Store honours a storefront in the URL is unverified) |
| Android | `market://details?id=in.vsyst.dzzlooms`, and `https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms` when nothing takes it | the Play Store app where there is one, a browser otherwise. Google's linking page (updated 2026-08-07) documents the https URL — from native code with `setPackage("com.android.vending")` — and no longer lists `market://details`; there is no documented link straight to Play's review form |

No `canOpenURL`, so no query declarations: RN 0.84.1's `openURL` calls `startActivity` and rejects when nothing handles the intent (`IntentModule.kt:113-129` and `:251-275`, read 2026-09-30), and the fallback hangs on that rejection. The `<queries>` entries of Phases 2 and 3 exist for other reasons.

```js
// src/constants/storeLinks.js — the one home for DZZLO's store URLs
export const IOS_APP_ID = '1553062924';
export const ANDROID_PACKAGE = 'in.vsyst.dzzlooms';

export const STORE_LINKS = Object.freeze({
  iosWriteReview: `https://apps.apple.com/app/id${IOS_APP_ID}?action=write-review`,
  androidPlayApp: `market://details?id=${ANDROID_PACKAGE}`,
  androidPlayWeb: `https://play.google.com/store/apps/details?id=${ANDROID_PACKAGE}`,
});
```

```js
// src/helpers/Review/openStoreForReview.js
import { Linking, Platform } from 'react-native';
import { STORE_LINKS } from '../../constants/storeLinks';

export async function openStoreForReview() {
  if (Platform.OS === 'ios') {
    await Linking.openURL(STORE_LINKS.iosWriteReview);
    return 'ios_write_review';
  }
  try {
    await Linking.openURL(STORE_LINKS.androidPlayApp);
    return 'android_play_app';
  } catch {
    await Linking.openURL(STORE_LINKS.androidPlayWeb);
    return 'android_play_web';
  }
}

// src/helpers/Review/__tests__/openStoreForReview.test.js — written first
import { Linking, Platform } from 'react-native';
import { openStoreForReview } from '../openStoreForReview';

// RN's Jest set-up already makes Linking.openURL a jest.fn — reset it per case.
beforeEach(() => Linking.openURL.mockReset().mockResolvedValue(true));

it('iOS: the write-review page, no storefront in the URL', async () => {
  Platform.OS = 'ios';
  await expect(openStoreForReview()).resolves.toBe('ios_write_review');
  expect(Linking.openURL).toHaveBeenCalledWith('https://apps.apple.com/app/id1553062924?action=write-review');
});
it('Android: the Play Store app, then the web listing if nothing takes market://', async () => {
  Platform.OS = 'android';
  Linking.openURL.mockRejectedValueOnce(new Error('No Activity found to handle Intent'));
  await expect(openStoreForReview()).resolves.toBe('android_play_web');
  expect(Linking.openURL.mock.calls.map(([url]) => url)).toEqual([
    'market://details?id=in.vsyst.dzzlooms',
    'https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms',
  ]);
});
```

The row sits next to "Contact Us" (`src/screens/Common/Help/index.js:162-170`) and reuses the existing `ItemSetting` (`src/screens/Common/Settings/index.js:219`), which already takes its colours from `useTheme()`:

```js
// src/screens/Common/Help/strings.js
export const strings = Object.freeze({
  en: { rateApp: 'Rate DZZLO' },
  hi: { rateApp: 'DZZLO को रेटिंग दें' }, // Hindi copy for the team to confirm
});

// src/screens/Common/Help/index.js
import { useStrings } from '../../../i18n';
import { openStoreForReview } from '../../../helpers/Review/openStoreForReview';
import { logEvent } from '../../../utils/firebase';
import { strings } from './strings';
// … inside the component
const t = useStrings(strings);
const onRate = useCallback(async () => {
  const opened = await openStoreForReview().catch(() => 'failed');
  logEvent('review_link_opened', { source: 'help', opened });
}, []);
// … after the "Contact Us" row
<ItemSetting leftText={t.rateApp} onPress={onRate} paddingHorizontal={20} />
```

v1.79 ships English only by decision, but the `{ en, hi }` table gets both, as every screen's does; check the row at 320 dp × fontScale 1 in both. A Tier 3 test renders Help, presses "Rate DZZLO" and asserts that `openStoreForReview` ran and the review facade never did (`src/screens/Common/Help/` has no tests yet); §9.4's config pin keeps the spec and `maybeRequestReview` out of `Help/index.js`. The three old copies of the store URLs move to `src/constants/storeLinks.js` in their own test-first change (exercise 11.10).

**Device checklist** — evidence stays out of the repos:

| # | Setup | Expected |
| --- | --- | --- |
| D1 | iOS: Xcode development build on a release iOS (not a seed), state seeded | the sheet, every time |
| D2 | D1 at AX-L (fontScale 2.143), device language Hindi | readable; probably English |
| D3 | iOS: TestFlight build | nothing, no crash; `review_requested` logged with `requested` (Firebase DebugView) |
| D4 | iPad, two windows | the sheet on the active window |
| D5 | Android: internal test track, a Gmail tester (not a Workspace account), installed from Play once | the card — quota not enforced |
| D6 | Android: internal app sharing | the card, Submit disabled |
| D7 | Android: an App Distribution APK, or the Fold AVD without a Play image | nothing; outcome `requested` or `error:<code>` (`PLAY_STORE_NOT_FOUND` expected without Play) |
| D8 | Both: Help → Rate DZZLO | iOS: the write-review page; Android: the Play listing, no chooser |
| D9 | Both: a user-visible error, then a success | no ask for 7 days |

> **After the upgrade to 0.87:** nothing here changes shape — the spec, the adapter and the package use only the documented surface. AGP 9 and compileSdk 37 arrive, so re-run the JUnit test after the bump; `review` 2.0.2 under AGP 9 is untested. On the experimental SwiftPM path, re-check `<DzzloOmsSpec/DzzloOmsSpec.h>` and `<React_RCTAppDelegate/…>` as Phase 1 says.

> **Optional Expo track (only on an Expo-paired React Native version):** `expo-store-review` 57.x / 58.x would replace `NativeStoreReview`. It needs Expo modules installed and iOS 16.4 as the floor (since 56.0.0; the app is on 15.1); its `isAvailableAsync()` returns false on TestFlight builds, and its `requestReview()` falls back to opening the store URL from the Expo config. 57.0.2 (2026-08-14) fixed presenting on the wrong scene ("Present the review prompt from the foregrounded scene"). Our own modules never move to Expo.

Sources: the store-review list in [[11-reference]] §8.6.

## 10. Release Checklist

One list for a release that adds a native module or an extension. Nothing is committed, merged, pushed or submitted without the user's word — every "submit" line is a stop-and-ask.

**Gate (both platforms)**

- [ ] `APP_ENV=testing yarn test` green locally; CI's Jest job green (it runs `yarn test` after `cp .env.ci .env.testing`).
- [ ] Red → green commits for every new module, with the mutation smoke recorded in the PR.
- [ ] Config-pin tests green: location strings (Phase 7), `<queries>` and associated domains (Phase 8), the iOS bundle-phase `APP_ENV`, extension versions, no `MYAPP_UPLOAD_` in `android/gradle.properties`.
- [ ] Codegen parses every spec (`./gradlew generateCodegenArtifactsFromSchema`; on iOS, `bundle exec pod install`).
- [ ] Native unit tests (XCTest; JUnit + Robolectric) green for every module with native logic.
- [ ] Cross-repo gate: `bash dzzlo_oms_api/scripts/release_gate.sh`.
- [ ] Device runs on the iOS simulator and the Fold AVD at 320 dp × fontScale 1, en + hi — on release builds too, because debug builds can hide New-Architecture problems. Device evidence stays out of the repo.
- [ ] Review prompt per build type (§9): an Xcode development build on a release iOS shows the sheet every time, TestFlight shows nothing; the Play internal test track shows the card, internal app sharing shows it with Submit disabled; Help → Rate DZZLO opens the store page on both.

**iOS**

- [ ] `MARKETING_VERSION` identical on every target; `CURRENT_PROJECT_VERSION` bumped.
- [ ] The bundle phase's `APP_ENV` is the intended environment (confirm in the Report navigator after archiving).
- [ ] Every new target has its App ID, profile, entitlements, registered App Group and privacy manifest.
- [ ] Every new purpose string names a shipping feature (§5).
- [ ] The App privacy label covers SDK collection; the social-media question is answered.
- [ ] Archive with Xcode 27 (iOS 26+ SDK) → TestFlight → exercise the NSE, widgets and clip from the TestFlight build. dSYM "Upload Symbols Failed" warnings for the prebuilt React frameworks are non-blocking (README:290).
- [ ] App Store Connect: pending agreements accepted by the Account Holder (README:289); App Clip card and experiences configured, if `DzzloClip` ships.
- [ ] Review notes: a demo account (email identifier), how to reach each new feature, why any background mode exists.
- [ ] Submit — **after the user says so**.

**Android**

- [ ] `versionCode` bumped; `versionName` matches iOS.
- [ ] Upload-key properties come from `~/.gradle/gradle.properties` or CI secrets.
- [ ] R8 on, keep rules reviewed, full device regression on the release build.
- [ ] `./gradlew bundleRelease` → AAB; 16 KB check on every `.so`.
- [ ] Diff the merged release manifest against the last release: every new permission has a reason, a Data safety row and, where needed, a Play declaration (FGS type + video, background location).
- [ ] Android 16 device check: edge-to-edge, and predictive back on the five `BackHandler` sites.
- [ ] Play Console: Data safety updated; declarations filed; internal testing track → production — **after the user says so**.

> **After the upgrade to 0.87:** RN 0.87 needs AGP 9 with the required opt-outs `android.builtInKotlin=false` and `android.newDsl=false` ("Starting from AGP 10.x these opt outs will be removed"), Kotlin 2.0+ (2.2.0 bundled), compileSdk and buildTools 37 (`minCompileSdk` 34), and Node ≥ 22.13.0. The Jest preset moved to `@react-native/jest-preset` in 0.85 and "must be consumed as package" in 0.87, so `jest.config.js`'s `preset: 'react-native'` changes and the custom resolver and transform entries need a re-check. iOS includes go framework-style (`#import <React/…>`) if you try the experimental SwiftPM path. Keep the upgrade checklist's library list current — `react-native-keychain` first. compileSdk 37 doesn't force targetSdk 37: raising the target is its own release, and it brings the Android 17 changes — the location-button policy (from 27 Jan 2027), `ACCESS_LOCAL_NETWORK` for LAN printers, widget bitmap memory caps, the SMS OTP hold, and the end of the large-screen orientation opt-out.

## 11. Exercises

**11.1 — Fill in the map.** Copy the §1 table into the vault and, for each phase you've built, replace every "likely" with what is actually in `Info.plist`, the entitlements, the merged release manifest and Play Console. **Produces:** a checked table.

**11.2 — The relock rule, red → green.** Write `relock.test.js` (§2) first, then `src/helpers/Auth/relock.js`, then a mutation smoke — flip `>=` to `>` and watch the boundary test fail. **Produces:** three recorded test runs.

**11.3 — Pin the release traps.** One config test that fails today on two counts — the bundle phase says `APP_ENV=testing`, and `android/gradle.properties` contains `MYAPP_UPLOAD_` — and goes green once both are fixed. It must report the key names only, never a value. **Produces:** a red run naming both lines.

**11.4 — Read the merged manifest.** After a release build (the user's step), open `android/app/build/intermediates/merged_manifest/release/processReleaseMainManifest/AndroidManifest.xml` and write one Data safety line for each data-bearing permission, starting with `AD_ID`. **Produces:** a draft Data safety sheet.

**11.5 — Prove 16 KB.** Run `zipalign -c -P 16 -v 4` on the next release APK (or an APK built from the AAB) and record the result next to the list of `.so` files each new module added. **Produces:** one pass line per library.

**11.6 — An OTA dry run (once the user approves the hosting).** Stand Hot Updater up against a test bucket, ship a copy change to a testing-channel release build, then change a spec and confirm the version rule refuses to send that bundle to the old binary. **Produces:** two device observations.

**11.7 — The review policy, red → green.** Write `maybeRequestReview.test.js` (§9.5) before the helper: every row red on `Cannot find module '../maybeRequestReview'`, then green, then two mutation smokes — `<` → `<=` in the 30-day rule turns R8 red, and deleting the once-per-version line turns R6 red. **Produces:** four recorded test runs.

**11.8 — The sheet, on purpose and not.** Seed the stored state from a `__DEV__`-only action and run D1, D3 and D4 of §9.6: a development build on the iPhone 17e simulator (iOS 27.0), the same flow from TestFlight, and an iPad with two windows. Write down whether iOS 27 still always shows the sheet to development builds — no one has reported either way yet. **Produces:** three dated device observations in the PR, screenshots kept out of the repos.

**11.9 — The card on Android.** Put a build on the internal test track, install it once from Play with a Gmail tester, then run D5, D6 (internal app sharing) and D7 (the Fold AVD). Record the `review_requested` outcome of each; whether the AVD has a Play image decides between `requested` and `error:<code>`. **Produces:** three device observations and one logcat line.

**11.10 — One home for store links.** A Jest test that walks `src/` and fails while any file outside `__tests__` folders, other than `src/constants/storeLinks.js`, contains `1553062924` or `details?id=in.vsyst.dzzlooms`. It is red today on exactly the three files of §9 (grep, 2026-09-30); it goes green once they import `STORE_LINKS`. Say in the PR that the update flow's iOS link changes storefront — from `/sg/` and `/us/` to none. **Produces:** a red run naming three files, then green.

---

**Next:** [[10-capstones]] — three end-to-end builds that pass through every checklist above; versions, sources and the review-policy map live in [[11-reference]].
