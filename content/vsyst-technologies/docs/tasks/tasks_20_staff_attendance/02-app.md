---
title: tasks_20 · 02 — app, staff check-in inside DZZLO OMS
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start".
---

# 02 — The app: staff check-in inside DZZLO OMS

Part of tasks_20, staff attendance. Overview: [[00-overview]]. Siblings: [[01-api]] (routes, checks, codes), [[03-web]] (the dealer's pages), [[04-platform-stores-and-law]] (store rules, DPDP), [[06-package-approval-list]] (C‑24), [[07-dealer-terms-and-data-processing]] (C‑27), [[05-round-1-web-design]] (round 1, superseded).

**Source.** `dzzlo_oms_app` `slave` @ `ea7e7222` and `dzzlo_oms_api` `slave` @ `86083ca`, read on 2026-10-01. Bare paths are the app; `api:` marks the API. Nothing here is built. This is the round-3 revision: staff are existing dealer users, and every supported phone can check in.

## 0. Summary

Staff are existing dealer users, of any scope, whom the dealer has put on the attendance roster (C‑17). They sign in as they do today (C‑18), and the dealer drawer shows them an **Attendance** item only when the server says they are on the roster.

On first use, a staff member accepts a disclosure and enters the dealer's enrolment code. The phone then creates a hardware key that signs only after fingerprint, face or PIN, and the dealer approves the phone in person.

Each punch takes one fresh GPS fix and refuses a simulated one. The app signs the payload and adds a Play Integrity token or an App Attest assertion; the API decides. Every supported phone takes part (C‑20):

- **Android 11 and later:** per-use keys.
- **Android 7–10:** a short signing window after the user confirms.
- **No Play services or no App Attest:** check-ins go through, flagged (C‑29).

Three in-house Turbo Modules, the app's first, do the native work, and no npm package is added. Location is read only at the tap, with no background location and no geofence.

## 1. Navigation: an Attendance item in the dealer drawer

- **Where.** The dealer app is a drawer (`src/navigation/Dealer/Drawer.js:74-103`) with its items in `src/navigation/Dealer/DrawerContent.js:404-579`. The bottom tabs are the three transaction types (`src/navigation/Dealer/TrnTab.js:36-40,433-469`). So Attendance goes in the drawer, like Reports.
- **Change.**
  - A route `dealerAttendance` next to `dealerReport` (`Drawer.js:95-98`).
  - A stack `DealerAttendanceNavigator` (`Attendance`, `AttendanceSetup`) in `src/navigation/Dealer/Main.js`. It is built like `DealerReportNavigator` (`:361-398`) and uses the shared portrait options (`:65-75`).
  - A `DrawerItem` (`DrawerContent.js:83-129`) at the top of the list, before Customers (`:485`).
- **Who sees it.**
  - Anyone on the roster for the current company, while the global switch is on. `useAttendanceEntry()` decides (§6).
  - Scope plays no part, so every dealer scope qualifies, managers included (this covers C‑23). Staff keep their existing screens.
  - The route is registered for everyone; anyone not on the roster who reaches it sees "Attendance is off for you".
- **Company switch** resets the cache and restarts the app (`DrawerContent.js:243-273`), so the roster is asked again.
- **A v2-only screen, switched on by the server.**
  - `register()` needs a v1 and a v2 (`src/navigation/screenRegistry.js:83-99`), so Attendance is mounted directly in its stack.
  - It never calls `resolveScreen` or `screenOptionsFor`, which throw in development for an unregistered key (`:131-143`).
  - **Global switch:** `useScreenFlag('Dealer/Attendance')` (`src/navigation/useScreenFlag.js:46-49`) reads `screen_v2_dealer_attendance`, and needs no registration. A missing key means on, so the server writes `false` before the build ships and removes it to switch attendance on.
  - **Per dealer and per user:** the roster, plus the API's list of enabled dealers ([[01-api]]).
- **Unchanged:** sign-in, the verification screen (`Drawer.js:38-48`), the Users screens and scope checks.
- **Old builds (C‑26)** have no item. The routes refuse builds below the minimum with `UPDATE_REQUIRED`.

## 2. Sign-in (C‑18)

Sign-in is unchanged: staff are dealer users with an email. They use an email or a 10-digit phone, a password, then an OTP (`src/screens/Login/AuthNavigator/Login.js:147-149`, `src/store/apis/dzzlooms/auth.js:99-121`). Requests carry `x-co-id` for the active company (`src/store/apis/createApi.js:39-42`), which is the dealer whose roster counts.

## 3. Screens

There are two new v2 screens: `src/screens/v2/Dealer/Attendance/` and `src/screens/v2/Dealer/AttendanceSetup/`.

**Phone setup**, once per phone:

1. Disclosure and consent (§5).
2. The enrolment code (48 h).
3. Location permission, and a check for a screen lock (§12).
4. The device key (one prompt) and the attestation (§4), then `POST /attendance/enrol`.
5. PENDING: the phone shows the 6-character match code that dzzlo_ro_web also shows ([[01-api]]) — "Show this phone to your dealer". It checks again when the app reopens and when the approval push arrives.

**Attendance home:**

- **Status:** not checked in, checked in since 09:02, or "No check-out".
- **Action:** one full-width Check in / Check out button.
- **Progress:** finding your location (± 18 m) → confirm it's you → sending.
- **Result:** "Checked in at 09:02 · 34 m from the pump", or a refusal and its fix.
- **Also:** "Can't check in?" for a manual request (C‑25), and the last 30 days.

**Blocking and info states**, checked on the phone before any request:

| State                                     | Kind     | The screen says or offers                                                                |
| ----------------------------------------- | -------- | ---------------------------------------------------------------------------------------- |
| Not set up, revoked or PENDING            | blocking | "Set up this phone" / "Waiting for your dealer's approval"                               |
| No screen lock (C‑20)                     | blocking | "Set a screen lock (PIN, pattern or password) to use attendance." → Settings             |
| Key gone (lock removed, phone reset)      | blocking | "Set up this phone again"                                                                |
| Location off, denied or approximate       | blocking | Settings; ask for precise or temporary full accuracy                                     |
| No Play services, or no App Attest (C‑29) | info     | "This phone can't run the security check. Your check-in counts, marked for your dealer." |
| Offline (C‑25)                            | blocking | "Check-in needs the internet" + a manual request                                         |
| Below the attendance minimum (C‑26)       | blocking | "Update DZZLO OMS" + store link (`UPDATE_REQUIRED`)                                      |

**Refusals** use the API's codes, which [[01-api]] answers with 403, 409 or 422 and an `error_code`. The numbers in the messages need `details` (see Unknowns).

| Code                | Message                                    | Fix                                           |
| ------------------- | ------------------------------------------ | --------------------------------------------- |
| `STAFF_INACTIVE`    | Attendance is off for you.                 | Ask your dealer.                              |
| `CHALLENGE_BAD`     | That took too long.                        | Tap again.                                    |
| `DEVICE_NOT_ACTIVE` | This phone is not approved.                | Set it up again; ask your dealer.             |
| `SIGNATURE_BAD`     | We couldn't confirm this phone.            | Try again, then set it up again.              |
| `INTEGRITY_FAILED`  | The security check failed.                 | Store app, phone updates, or a manual entry.  |
| `LOCATION_FAKE`     | Your location looks simulated.             | Turn off location-changing apps.              |
| `LOCATION_VAGUE`    | Location too vague (± N m, needs ± 30 m).  | Turn on Precise location; step into the open. |
| `LOCATION_STALE`    | That reading was too old.                  | Try again.                                    |
| `OUTSIDE_SITE`      | You are N m from the pump (allowed 100 m). | Move closer to the pump.                      |
| `DUPLICATE`         | Already in, or punched under 2 min ago.    | Wait, then refresh.                           |
| `NO_OPEN_CHECKIN`   | You haven't checked in yet.                | Check in first.                               |

`INTEGRITY_FAILED` means a verdict came back and failed. `UNAVAILABLE` alone is never refused (C‑29). The company gate's codes (`src/utils/errorCodes.js:34-55`) get attendance wording too.

## 4. Three native modules

These are the app's first in-house Turbo Modules, built the way [[vsyst-technologies/docs/learning/native-modules/01-phase-1-foundations|Native modules, Phase 1]] describes:

- **Specs:** in `specs/`, with one `codegenConfig` (`DzzloOmsSpec`).
- **Facades:** in `src/native/`.
- **Android:** Kotlin modules in one `BaseReactPackage`, registered at `MainApplication.kt:16-19`.
- **iOS:** Swift behind thin Objective-C++ adapters, using system frameworks only.

Hashing is native, so no JavaScript crypto library is needed.

| Module                                                      | Android                                                                                                                                                                                                                                                                                                                                                      | iOS                                                                                                                                                                                                                              | Facade (`src/native/`)                                                    |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `NativeCheckInLocation`: permission state and one fresh fix | `PermissionsAndroid`, FINE + COARSE together. `LocationManager` (GPS) on every phone; Fused `getCurrentLocation` only if the optional Play services location library is approved ([[06-package-approval-list]]) and Play services exist. `isMock()` on API 31+, `isFromMockProvider()` below. `getAccuracy()` is a 68 % radius.                              | `CLLocationManager` When-In-Use, `accuracyAuthorization`, `requestTemporaryFullAccuracyAuthorization(withPurposeKey:)`. `sourceInformation` (iOS 15+, may be nil): refuse `isSimulatedBySoftware`, flag `isProducedByAccessory`. | `checkInLocation.js` → `{ lat, lng, accuracyM, fixTimeMs, ageMs, flags }` |
| `NativeDeviceKey`: the attendance key                       | Keystore EC P-256, made with `setAttestationChallenge` (the enrol challenge); StrongBox when present, otherwise TEE. **11+:** per use, `setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG \| AUTH_DEVICE_CREDENTIAL)`, signing inside `BiometricPrompt` + `CryptoObject`. **7–10:** time-bound, `setUserAuthenticationValidityDurationSeconds` (§12). | Secure Enclave P-256 with `.privateKeyUsage` + `.userPresence` (biometrics or passcode, C‑19). The stricter alternative under C‑19 is `.biometryCurrentSet`: no passcode, and re-enrolment kills the key.                        | `deviceKey.js`: `status`, `create`, `sign`, `remove`                      |
| `NativeAppIntegrity`: a genuine app on a genuine phone      | Play Integrity **standard**: `prepareIntegrityToken`, then `request` with `requestHash` = SHA-256(challenge ‖ payload), or ‖ public key at enrolment. With no Play services: `UNAVAILABLE` plus the error code.                                                                                                                                              | App Attest: `attestKey` at enrolment, then `generateAssertion` per punch. The enrolment assertion carries the Secure Enclave public key. If `isSupported` is false: `UNAVAILABLE`, and the key is registered flagged.            | `appIntegrity.js`: `prepare`, `enrolProof`, `punchProof`                  |

One spec, in sketch:

```ts
// specs/NativeDeviceKey.ts — sketch; names fixed at build time
type NewKey = { publicKey: string; chain: string[]; auth: string } // auth: per-use | window
export interface Spec extends TurboModule {
  status(alias: string): Promise<string> // ok | missing | invalidated | no_lock
  create(alias: string, challengeB64: string): Promise<NewKey>
  sign(alias: string, payloadB64: string, title: string, reason: string): Promise<string>
  remove(alias: string): Promise<void>
}
export default TurboModuleRegistry.getEnforcing<Spec>("NativeDeviceKey")
```

**Jest.** Jest has no Turbo Module proxy, so `getEnforcing` would throw. Each spec therefore gets a global mock in `jest.setup.js` and a per-file mock in its facade test, and the screen tests mock the facades. The precedent is `src/i18n/deviceLocale.js`.

**Android libraries** (Gradle, not npm): Play Integrity and androidx.biometric; Play services location is **optional** (faster fixes where Play services exist; `LocationManager` works without it). All three are on [[06-package-approval-list]] (C‑24) for the user to approve.

## 5. Permissions and declarations

| Where                                                        | Change                                                                                                                                                                                                                 |
| ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `android/app/src/main/AndroidManifest.xml:3` (INTERNET only) | Add `ACCESS_FINE_LOCATION` + `ACCESS_COARSE_LOCATION`. The biometric permissions come with androidx.biometric. Never add background location, a location foreground service, `QUERY_ALL_PACKAGES` or the camera (C‑7). |
| `ios/dzzlo_oms_app/Info.plist:49-54`                         | **Keep the three location keys** — `OneSignalLocation` is linked (`ios/Podfile.lock:205,220`), and App Store Connect rejects the build without them — but **reword them**.                                             |
| `Info.plist`                                                 | Add `NSLocationTemporaryUsageDescriptionDictionary` (purpose key `AttendanceCheckIn`) and `NSFaceIDUsageDescription`.                                                                                                  |
| `dzzlo_oms_app.entitlements:4-11`                            | Add `com.apple.developer.devicecheck.appattest-environment` = `production`.                                                                                                                                            |
| `PrivacyInfo.xcprivacy:42-43` (empty)                        | Add `NSPrivacyCollectedDataTypePreciseLocation` (linked, App Functionality). Add a device ID too if [[04-platform-stores-and-law]] says so.                                                                            |

**Proposed wording** (English, see §8):

- **When In Use:** "DZZLO OMS uses your location only when you tap Check in or Check out, to confirm you are at your pump. It never tracks you in the background."
- **The two Always keys:** "DZZLO OMS does not use your location in the background. It reads it only when you tap Check in or Check out."
- **Temporary full accuracy:** "Your exact location confirms you are at your pump when you check in or out."
- **Face ID:** "DZZLO OMS uses Face ID to confirm it is you when you check in or out."

**In-app disclosure**, shown before any system prompt. It meets Play's User Data policy (in the app, with an affirmative action) and Apple 5.1.5 (notify, then get consent). It says:

- **What:** the location and accuracy at each tap, the phone model and OS, and the phone key.
- **When:** only at the tap.
- **Who sees it:** the dealer's owner and admins (C‑22).
- **How long:** C‑8.

It ends with "Agree and continue" / "Not now", and the enrol request carries the disclosure version. The dealer terms are in [[07-dealer-terms-and-data-processing]].

## 6. API client

- **The client.** `src/store/apis/v4/attendance.js` is built like `src/store/apis/v4/customers.js:97`.
  - It sends the commands: `enrol/challenge`, `enrol`, `challenge`, `punch`, `requests`.
  - It reads `POST /screens/attendance`: roster state, phone state, any open check-in, the site and the last 30 days.
- **The drawer item.**
  - The same read answers whether the user is on the roster (assumed, [[01-api]]).
  - `useAttendanceEntry()` caches that answer and asks again on return to the app. It deduplicates over 60 seconds, as the features map does (`src/navigation/useScreenFlag.js:55-104`).
  - The features call cannot answer per user, because it is one global map (`api:helpers/appFeatures.js:31-32`).
- **No retry.** The shared base retries 5xx and network errors (`src/store/apis/createApi.js:96-108`). Attendance mutations set `maxRetries: 0`, like the OTP calls (`src/store/apis/dzzlooms/auth.js:105,116,129,139`).
- **Idempotency key.** Enrol and punch use the challenge as the key; manual requests use a random id. A repeat gets the stored answer.
- **Integrity** is always sent: a token, an assertion, or `UNAVAILABLE` with its reason.
- **Errors** are `{ success: false, error, error_code, details? }`; the app writes its own sentence (`docs/testing.md:406-417`).
- **GPS** goes in request bodies only — never in URLs, logs or Crashlytics. The device key, not any header, is the phone's identity.

## 7. Push

- **Today:** a tap stores OneSignal's `additionalData` in `auth.notification` (`src/helpers/OneSignal/index.js:26-30`), and the dealer drawer routes on `notification.dealer` (`src/navigation/Dealer/DrawerContent.js:178-199`). The external id is the user id (`src/navigation/AppNavigatorContainer.js:98-103`).
- **New `dealer` values:**
  - `AttendanceDeviceApproved` / `AttendanceDeviceRevoked`: sent to the staff member; they open `dealerAttendance`.
  - `AttendanceDeviceWaiting`: sent to managers, to inform them only; approval happens in dzzlo_ro_web (C‑16).
  - Old builds ignore all three.
- **Sign-out** clears the push identity (`OneSignal.logout()`), so a shared phone stops getting the last user's notices (details: `private/_security-findings.md`, local only).

## 8. Strings, Hindi and the English lock (C‑10)

- **Every word in the strings tables.** All copy lives in `strings.js` + `strings.hi.js`, read through `useStrings` (`src/i18n/useStrings.js:70-78`), and ESLint refuses literal text in v2 JSX (`eslint.config.js:66-74`). That includes the drawer label, the refusals, the disclosure, and the prompt text passed to `NativeDeviceKey.sign`.
- **C‑10 (recommended): English and Hindi from day one.** 1.79 mounts `LanguageProvider locked="EN"` (`AppNavigatorContainer.js:176`; pinned by `src/navigation/__tests__/language.lock.test.js`), so the Hindi stays hidden until the lock lifts.
- **Info.plist strings stay English.** Translating them needs `CFBundleLocalizations`, which `src/i18n/__tests__/locales.config.test.js` pins absent.
- **Proposed Hindi, for review:** Attendance हाज़िरी · Check in चेक इन · Check out चेक आउट · Set up this phone इस फ़ोन को सेट करें · Waiting for your dealer's approval डीलर की मंज़ूरी का इंतज़ार है.

## 9. Design constraints

- **Baseline:** 320 dp at fontScale 1, in English and Hindi — `PHONE_NARROW` (`src/test/presets.js:98`, `docs/testing.md:760`; [[vsyst-technologies/docs/oms_app/screen-redesign/06-all-screen-shapes-plan|shapes plan]]).
- **Tokens only:** no hex colours, no literal `fontSize` (`eslint.config.js:41-77`).
- **Text sets the box:** the font scale is never capped, pairs stack at 1.786 (`src/theme/scale.js:10`), and touch targets are 44 pt (`src/theme/layout.js:35`).
- **Portrait**, like every route in 1.79.
- **Spec:** from [[vsyst-technologies/docs/oms_app/screen-redesign/templates/screen-spec|the template]].

## 10. Tests

Test-first: a red commit, then a green commit, then a mutation smoke (`AI.md:7-26`).

| Tier            | What it pins                                                                                                                                                                                                                                                                                             |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 — pure        | `attendanceEntryVisible` for all six scopes (only the roster and the switch decide) · the check-in state machine · copy for every code, plus a fallback · the canonical payload (challenge ‖ type ‖ lat ‖ lng ‖ accuracy ‖ fix time ‖ flags) against the API's vectors · the prerequisites · the facades |
| 2 — store + MSW | each endpoint's URL, body, headers and idempotency key · a 5xx on punch reaches the server once (model: `src/store/apis/dzzlooms/__tests__/auth.otpRetry.msw.test.js`) · `error_code` and `details` · roster on, off and failed (failed hides the item)                                                  |
| 3 — screens     | `renderScreen` with `authState({ scope })` (`src/test/testUtils.js:407-418`) for each scope · each phone state · each refusal and the info state · Hindi · `PHONE_NARROW` × fontScale 1 / 1.3 / 2.143, decisions only · the drawer item only for roster members                                          |

**Config tests** read off disk, like today's five `*.config.test.js`. They pin:

- FINE + COARSE and no background location;
- the reworded Info.plist keys, plus the Face ID and purpose keys;
- the App Attest entitlement and the privacy manifest;
- the codegen config and the spec mocks;
- no `react-native-permissions`, and the Firebase pin (`src/utils/__tests__/firebaseModules.config.test.js:41-43`).

**Native unit tests.** These modules add the app's first JUnit + Robolectric and XCTest targets. They cover the key mode by API level, the confirm path, the location fallback, the mock flags and `UNAVAILABLE`.

**Real-device runs** are part of green, because CI runs Jest only.

- **Android:** use an AAB on the Play Console **internal testing track**, since integrity verdicts need a Play-installed build.
  - Phones: Android 7–8, 9–10, 11 and 13+; one low-cost phone; one phone without Play services.
  - Cases: a mock-location app, approximate location only, no screen lock, and a reinstall.
- **iPhone:** use a real device.
  - Cases: Face ID, passcode only, an Xcode GPX route, and reduced accuracy.
  - Tier 3 covers "No App Attest".
- **Both:** airplane mode (C‑25), and an old build (it should show no item).

## 11. Release items

- **Play Integrity:**
  - Link a Google Cloud project in Play Console.
  - Put the project number in a new env var, in every env file and in `.env.ci` (`AI.md:227-237`).
  - The API decodes tokens with a service account (C‑24).
  - The quota is 10,000 a day (C‑11), one per enrolment or punch.
- **App Attest:** add the capability to the App ID. Check the archived entitlements, since the archive phase hard-codes its environment (`project.pbxproj:291`).
- **Store review:** a demo dealer user on the roster, a way for the reviewer to get the OTP, and a demo outlet ([[04-platform-stores-and-law]]).
- **Play precise-location declaration:** required for `ACCESS_FINE_LOCATION`. The form opens in November 2026; it is mandatory from **27 January 2027**.
- **Android 17 location button:**
  - At target API 37, one-time precise location must use the system button (`USE_LOCATION_BUTTON`, `onlyForLocationButton`).
  - That button would be the app's first Fabric component.
  - No date has been announced.
- **Store forms:** Play Data safety and the App Store privacy label.
- **Build:**
  - Bump the versions.
  - Add an AAB build (`build-release-apk.sh:39` builds APKs only).
  - Diff the merged manifest.
  - Run the 16 KB check.

## 12. All supported phones (C‑20)

The app's floor is Android 7 (minSdk 24, `android/build.gradle:4`) and iOS 15.1 (`project.pbxproj:453`). Every phone above it can check in:

| Phone                    | Key, as recorded                 | How the user confirms                                                                        | Fake-location flag                            | Integrity                               |
| ------------------------ | -------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------- | --------------------------------------- |
| Android 11+ (API 30+)    | per use · `auth: per-use`        | `BiometricPrompt` + `CryptoObject`: biometric or PIN                                         | `isMock()` (31+), `isFromMockProvider()` (30) | Play Integrity, or `UNAVAILABLE` + flag |
| Android 9–10 (API 28–29) | time-bound · `auth: window`      | `BiometricPrompt` (strong biometrics), or "Use PIN" → the confirm-credential screen          | `isFromMockProvider()`                        | the same                                |
| Android 7–8 (API 24–27)  | time-bound · `auth: window`      | the system confirm-credential screen (`KeyguardManager.createConfirmDeviceCredentialIntent`) | `isFromMockProvider()`                        | the same                                |
| iPhone, iOS 15.1+        | Secure Enclave · `.userPresence` | Face ID, Touch ID or passcode                                                                | `sourceInformation`                           | App Attest, or `UNAVAILABLE` + flag     |

- **No screen lock:** when `KeyguardManager.isDeviceSecure()` or `LAContext` finds no lock, the app asks the user to set one. No key can require authentication without a lock.
- **The window:** proposed at 30 s, tuned in P0. The attestation's `authTimeout` lets the API record `auth: window`.
- **Why Android 11 is the line:** Android 10 and lower cannot combine strong biometrics with a device credential on one key (confirmed).
- **Without Play services:** there is no Fused provider either, so `LocationManager` takes over.
- **Before Android 13:** Play's device verdict is not hardware-backed, so these phones prove less; the dealer sees the flags.

## Unknowns

1. **Roster signal.** Assumed: the read model tells a user who is not on the roster just that ([[01-api]]).
2. **Refusal numbers.** The messages need distance, radius and accuracy in `details`.
3. **Repeats.** Assumed: a punch re-sent with the same challenge gets the stored answer.
4. **Payload bytes.** The exact formats, shared as test vectors.
5. **Phone clocks.** Measure the fix age on the monotonic clock (`ageMs`).
6. **The window.** Its length, and how `auth: window` phones look in [[03-web]].
7. **Old phones.** Phones that launched before Android 8 may give no hardware-backed key chain (unclear): flag them or refuse them?
8. **Android 9–10 PIN path.** This is inferred from the documented limits; verify it on devices.
9. **C‑29.** Accept and flag (recommended), or allow manual requests only.
10. **Store forms.** Device ID, "sharing" and Apple 5.1.2(i) ([[04-platform-stores-and-law]]).
11. **Accuracy.** Android gives a 68 % radius; Apple states no confidence. P0 compares the two.
12. **Sessions.** How sessions are kept on the phone is out of scope (details: `private/_security-findings.md`, local only).

## Sources

**App** (`dzzlo_oms_app` @ `ea7e7222`):

- Dealer navigation (`src/navigation/Dealer/`): `Drawer.js:38-48,74-103` · `DrawerContent.js:83-129,178-199,243-273,404-579` · `Main.js:65-75,361-398` · `TrnTab.js:36-40,433-469`
- Shared navigation (`src/navigation/`): `screenRegistry.js:83-99,131-143` · `useScreenFlag.js:46-49,55-104` · `AppNavigatorContainer.js:98-103,176`
- Sign-in and store: `src/screens/Login/AuthNavigator/Login.js:147-149` · `src/store/apis/createApi.js:39-42,96-108` · `src/store/apis/dzzlooms/auth.js:99-139` · `src/store/apis/v4/customers.js:97`
- Helpers and copy: `src/utils/errorCodes.js:34-55` · `src/helpers/OneSignal/index.js:26-30` · `src/i18n/useStrings.js:70-78`
- Rules and docs: `eslint.config.js:41-77` · `src/test/testUtils.js:407-418` · `docs/testing.md:406-417,760`
- Native and build: `AndroidManifest.xml:3` · `android/build.gradle:4` · `MainApplication.kt:16-19` · `Info.plist:49-54` · `PrivacyInfo.xcprivacy:42-43` · `dzzlo_oms_app.entitlements:4-11` · `ios/Podfile.lock:205,220` · `project.pbxproj:291,453` · `build-release-apk.sh:39`

**API** (`dzzlo_oms_api` @ `86083ca`): `helpers/appFeatures.js:31-32`.

**Vault:** [[vsyst-technologies/docs/learning/native-modules/01-phase-1-foundations|Phase 1]] · [[vsyst-technologies/docs/learning/native-modules/07-phase-7-maps-and-location|Phase 7]] §3 · [[vsyst-technologies/docs/learning/native-modules/09-phase-9-security-privacy-and-release|Phase 9]] §2–5

**Platform** (2026-10-01; confirmed on official pages unless marked):

- Android: https://developer.android.com/reference/android/location/Location · https://developer.android.com/develop/sensors-and-location/location/permissions/runtime · https://developer.android.com/guide/topics/permissions/private-alternatives/location-button · https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder · https://developer.android.com/identity/sign-in/biometric-auth · https://developer.android.com/privacy-and-security/keystore · https://developer.android.com/privacy-and-security/security-key-attestation
- Play Integrity: https://developer.android.com/google/play/integrity/standard · https://developer.android.com/google/play/integrity/setup · https://developer.android.com/google/play/integrity/verdicts · https://developer.android.com/google/play/integrity/error-codes
- Play policy: https://support.google.com/googleplay/android-developer/answer/17033915 · https://support.google.com/googleplay/android-developer/answer/16909972 · https://support.google.com/googleplay/android-developer/answer/10144311 · https://support.google.com/googleplay/android-developer/answer/10787469
- Apple: https://developer.apple.com/documentation/corelocation/cllocationsourceinformation · https://developer.apple.com/documentation/corelocation/cllocationmanager/requesttemporaryfullaccuracyauthorization(withpurposekey:completion:) · https://developer.apple.com/documentation/security/secaccesscontrolcreateflags · https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave · https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity · https://developer.apple.com/app-store/review/guidelines/
- Unclear: the Android 7–10 confirm path in practice, attestation on pre-Android 8 phones, App Attest on the Simulator, the API 37 deadline, the Play Integrity price.
