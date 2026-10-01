---
title: tasks_20 · 06 — new packages for approval (C‑24)
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start".
---

# 06 — New packages for approval (C‑24)

Part of [[00-overview]]. Siblings: [[01-api]], [[02-app]], [[03-web]], [[04-platform-stores-and-law]] (§6 explains the picks).

Repo facts cite `api:` = `dzzlo_oms_api` `slave` @ `86083ca`, `app:` = `dzzlo_oms_app` `slave` @ `ea7e7222`, `web:` = `dzzlo_ro_web` `main` @ `5a66bf8`. Versions and dates were read from npm and Google Maven on 2026-10-01.

## 0. Summary

The user asked for this list first: "c-24 list the plan of new packages we will approve then execute".

**Nothing below is installed until the user ticks its Approved? box.**

| Repo           | Needed                                                                                      | Optional, later or test-only                                                                                                      |
| -------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| API            | four runtime packages: one to sign in to Google for the Play Integrity check, three parsers | a typed Google client, an App Attest schema, a test-only App Attest checker                                                       |
| Android app    | two libraries: Play Integrity and androidx.biometric                                        | Play services location; the Android 17 location button (later)                                                                    |
| iOS app        | none — system frameworks only                                                               | a OneSignal pod change                                                                                                            |
| App JavaScript | none                                                                                        | a OneSignal upgrade (5.5.0+) that drops OneSignal's own location module, so no third-party location code ships next to attendance |
| dzzlo_ro_web   | none                                                                                        | —                                                                                                                                 |

Every pin is exact, so any later version needs a new tick (inf).

## 1. dzzlo_oms_api — npm

| #   | Package                                       | Pin     | License    | Maintainer       | Last release | What it does for us                                                                                    | Phase | Needs    | Tree / size                        | Alternatives                                                                                                             | Risk                   | Approved? |
| --- | --------------------------------------------- | ------- | ---------- | ---------------- | ------------ | ------------------------------------------------------------------------------------------------------ | ----- | -------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------- | --------- |
| A1  | `google-auth-library`                         | 11.1.0  | Apache-2.0 | Google           | 2026-09-16   | service-account sign-in, then one POST to `decodeIntegrityToken`                                       | P1    | Node ≥22 | 6 deps, 602 KB                     | A6 (typed client) · no package: sign Google's JWT with the existing `jsonwebtoken` (Google "strongly" advises a library) | low                    |           |
| A2  | `cbor`                                        | 10.0.12 | MIT        | hildjj and 2     | 2026-03-04   | decodes the App Attest attestation object                                                              | P1    | Node ≥20 | 1 dep (`nofilter`), 167 KB         | `cbor-x` 1.6.6 (optional native add-on, 9 optional packages) · `cborg` 6.1.3 (ESM-only) · in-house decoder               | low                    |           |
| A3  | `@peculiar/asn1-x509`                         | 2.10.0  | MIT        | PeculiarVentures | 2026-09-27   | reads certificates and their extensions; Node's `crypto` checks the signatures                         | P1    | Node ≥14 | 4 deps (shared with A4), 172 KB    | `@peculiar/x509` 2.1.0 (about 20 packages) · `pkijs` · Node's `X509Certificate` alone cannot read the custom extensions  | low                    |           |
| A4  | `@peculiar/asn1-android`                      | 2.10.0  | MIT        | PeculiarVentures | 2026-09-27   | reads the Android key description: level, challenge, `userAuthType`, `authTimeout`, boot state, app id | P1    | Node ≥14 | 3 deps (shared), 66 KB             | in-house schema on `asn1js`; Google's own verifier is Kotlin (reference only)                                            | low                    |           |
| A5  | _optional_ `@peculiar/asn1-apple`             | 2.10.0  | MIT        | PeculiarVentures | 2026-09-27   | schema for the App Attest nonce extension                                                              | P1    | Node ≥14 | 6 KB (shared deps)                 | about 10 lines on `asn1js`, already in the tree                                                                          | low; new in May 2026   |           |
| A6  | _optional_ `@googleapis/playintegrity`        | 28.1.0  | Apache-2.0 | Google           | 2026-09-24   | typed client for `decodeIntegrityToken`                                                                | P1    | Node ≥22 | about 22 more packages             | A1 alone                                                                                                                 | low                    |           |
| A7  | _test-only_ `node-app-attest` (devDependency) | 1.0.1   | MIT        | uebelack         | 2026-02-20   | second opinion in tests: our App Attest verifier must agree with it                                    | P1    | ESM-only | 3 deps (`asn1js`, `cbor`, `pkijs`) | Apple's sample data plus our own tests                                                                                   | test only; ESM in Jest |           |

- **Tree.** A1–A4 bring 33 packages; 21 are new to `api:yarn.lock`, and 12 are already there (e.g. `jws`, `jwa`, `tslib`).
- **Reused, not added:**
  - `jsonwebtoken` 9.0.3 (`api:package.json:41`) signs Apple's ES256 JWT for the risk metric.
  - Node's `crypto` and `fetch` read Google's root and revocation lists.

## 2. dzzlo_oms_app — Android (Gradle)

| #   | Package                                                    | Pin            | License                             | Maintainer      | Last release | What it does for us                                                 | Phase | Needs                  | Tree / size                                                                                                | Alternatives                                                                                                                                | Risk                            | Approved? |
| --- | ---------------------------------------------------------- | -------------- | ----------------------------------- | --------------- | ------------ | ------------------------------------------------------------------- | ----- | ---------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | --------- |
| B1  | `com.google.android.play:integrity`                        | 1.6.0          | Play Integrity API Terms of Service | Google          | 2025-11-20   | standard integrity tokens bound to `requestHash`                    | P2    | minSdk 23 (app: 24)    | 257 KB AAR; Play services basement + tasks (probably already in via Firebase) and Play core-common         | none for Play verdicts; Firebase App Check rejected (its tokens are for Firebase back ends)                                                 | low; needs Play services (C‑29) |           |
| B2  | `androidx.biometric:biometric`                             | 1.1.0 (stable) | Apache-2.0                          | Google AndroidX | 2021-01-27   | one prompt for biometric or PIN: per-use key on 11+, window on 7–10 | P2    | minSdk 14              | 195 KB AAR; AndroidX core, fragment, appcompat, lifecycle (already in React Native)                        | 1.4.0-alpha07 (2026-04-22, alpha) · no package: platform `BiometricPrompt` (API 28+) plus `KeyguardManager` (more code per Android version) | low; old but stable             |           |
| B3  | _optional_ `com.google.android.gms:play-services-location` | 21.4.0         | Android SDK License                 | Google          | 2026-06-25   | fused location, often a faster first fix                            | P2    | Play services on phone | 272 KB AAR; Play services base, basement, tasks; Kotlin coroutines                                         | **no package: the framework `LocationManager`** — works on phones without Play services, which C‑29 needs anyway                            | medium: two code paths          |           |
| B4  | _later_ `androidx.core.locationbutton:locationbutton`      | 1.0.0-alpha01  | Apache-2.0                          | Google AndroidX | 2026-06-17   | Android 17's location button, which Play requires at target API 37  | Later | minSdk 24              | 91 KB AAR; appcompat, lifecycle, Kotlin — no Compose (the `-compose` artifact pulls Compose alphas; avoid) | none once the app targets API 37                                                                                                            | high today: alpha               |           |

[[02-app]] §4 plans B3 with `LocationManager` as the fallback. This list marks B3 optional: one code path on every phone is simpler, and P0 can show whether the fused fix is worth a second path.

## 3. dzzlo_oms_app — iOS (CocoaPods)

| #   | Change                                                                                                                                                                                                                                                                         | Phase | Risk                         | Approved? |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----- | ---------------------------- | --------- |
| C1  | **No new pod.** App Attest, the Secure Enclave key, location and SHA-256 all come from system frameworks (§6).                                                                                                                                                                 | —     | —                            | n/a       |
| C2  | _optional, with D1_: change the extension target's aggregate `pod 'OneSignalXCFramework'` (`app:ios/Podfile:73-74`) to `pod 'OneSignalXCFramework/OneSignal'`, then install with `ONESIGNAL_DISABLE_LOCATION=true`. `OneSignalLocation` leaves `app:ios/Podfile.lock:205,220`. | P2    | medium: push must still work |           |

## 4. dzzlo_oms_app — npm (JavaScript)

| #   | Package                                       | Pin                                        | License | Maintainer | Last release | What it does for us                                                                                       | Phase | Needs                           | Tree / size                                     | Alternatives                                                                               | Risk                                      | Approved? |
| --- | --------------------------------------------- | ------------------------------------------ | ------- | ---------- | ------------ | --------------------------------------------------------------------------------------------------------- | ----- | ------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------- | --------- |
| D1  | _optional_ `react-native-onesignal` (upgrade) | 5.5.14 (from 5.4.1, `app:package.json:54`) | MIT     | OneSignal  | 2026-09-23   | from 5.5.0, OneSignal's location module can be left out of both builds; the Always plist keys can then go | P2    | React Native ≥0.79 (app 0.84.1) | 1 dep (`invariant`); OneSignal native SDK 5.5.x | keep 5.4.1 and never call `Location.setShared(true)` — the module and the Always keys stay | medium: push is live; test both platforms |           |

**No other JavaScript package:**

- The three native modules use React Native's built-in codegen.
- Permissions use the built-in `PermissionsAndroid`.
- The "never install react-native-permissions" rule stands.

## 5. dzzlo_ro_web — npm

| #   | Change                                                                                                                                                                                                                                                 | Approved? |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| E1  | **No new package** (`web:package.json:5-15` unchanged). Rejected: a map library (v1 shows coordinates and an open-in-maps link), a CSV library (the server builds the CSV), a geolocation package (the browser's `navigator.geolocation`, HTTPS only). | n/a       |

## 6. System frameworks used — no package, nothing hidden

| Where   | Framework / API                                                                   | Used for                                                                 |
| ------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| iOS     | CoreLocation (`CLLocationManager`)                                                | one fix, `sourceInformation`, temporary full accuracy                    |
| iOS     | DeviceCheck (`DCAppAttestService`)                                                | App Attest                                                               |
| iOS     | Security (`SecKeyCreateRandomKey`, `SecAccessControl`)                            | the Secure Enclave key                                                   |
| iOS     | LocalAuthentication (`LAContext`)                                                 | prompt text; "no passcode set" check                                     |
| iOS     | CryptoKit                                                                         | SHA-256 of the challenge and payload                                     |
| Android | `android.location.LocationManager`                                                | one fix; `isMock()` / `isFromMockProvider()`                             |
| Android | `java.security.KeyStore` + `KeyGenParameterSpec` (Android Keystore)               | the device key and its attestation chain                                 |
| Android | `KeyguardManager`                                                                 | `isDeviceSecure()`; the confirm-credential screen on Android 7–8         |
| Android | `Settings` intents (`ACTION_BIOMETRIC_ENROLL` 30+, `ACTION_SECURITY_SETTINGS`)    | "set a screen lock"                                                      |
| Android | React Native `PermissionsAndroid`                                                 | FINE + COARSE location                                                   |
| API     | Node `crypto` (`X509Certificate`, `verify`, `createHash`, `randomBytes`), `fetch` | signature checks, hashes, challenges, Google's root and revocation lists |
| Web     | `navigator.geolocation`                                                           | "Use my current location" for the outlet (HTTPS only)                    |

## 7. Secrets and accounts

| Item                                                                                                           | Needed for                                | Where it lives                                                                                          | Phase |
| -------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------- | ----- |
| Google Cloud project, linked to DZZLO OMS in Play Console (App integrity)                                      | Play Integrity tokens and the daily quota | Google; the project number is app config, not a secret                                                  | P0c   |
| Service account in that project, allowed to decode Play Integrity tokens                                       | A1's call to `decodeIntegrityToken`       | its key is a **new API secret**, kept with the API's other secrets — never in git or this vault         | P1    |
| Apple App Attest capability on the App ID; entitlement `com.apple.developer.devicecheck.appattest-environment` | App Attest                                | Apple Developer account; the app's entitlements file. Team ID and bundle ID are API config, not secrets | P2    |
| _Optional_ Apple DeviceCheck key and key id                                                                    | the App Attest risk metric                | a new API secret, same store                                                                            | Later |
| Google's key-attestation roots and Apple's App Attest root                                                     | chain checks                              | public certificates pinned in the API repo (inf)                                                        | P1    |
| OneSignal                                                                                                      | push                                      | existing account — no change                                                                            | —     |

## 8. Node 22+ on production

- **Which packages care.** A1 and A6 declare `node >=22`; A2 needs ≥20; A3–A5 need ≥14.
- **CI** runs Node 22 (`api:.github/workflows/test.yml:20`).
- **Production is unchecked.** PM2 sets no interpreter (`api:ecosystem.config.js:4-6`), so production runs the host's default `node`.
- **Before P1 merges**, run `node -v` on the production host as the PM2 user and record the result.
- **If it is below 22**, upgrade Node (preferred). Or pin the last versions that accept older Node and move up later:
  - `google-auth-library` 10.9.1 (2026-07-23, Node ≥18);
  - `cbor` 9.0.2 (2024-01-31, Node ≥16).

## 9. Order of installation

| Phase | What                                                        |
| ----- | ----------------------------------------------------------- |
| P0    | nothing in the repos — the spike is a throwaway build       |
| P0c   | the user ticks this list                                    |
| P1    | A1–A4; A5 and A6 if ticked; A7 as a devDependency if ticked |
| P2    | B1, B2; B3 if ticked; D1 + C2 if ticked                     |
| P3    | nothing                                                     |
| P4    | nothing — store forms only                                  |
| Later | B4, before the app targets API 37                           |

## 10. How each install is verified

- **Small commits.** One package per commit, with its manifest and lockfile change together: `package.json` + `yarn.lock`, `build.gradle`, or `Podfile` + `Podfile.lock`.
- **Lockfile diff.** The PR shows the lockfile diff, and only the expected names may appear. For A1–A4 that is the 21 new names.
- **Licences.** `yarn licenses list` for npm; `./gradlew :app:dependencies` before and after for Android; the `Podfile.lock` diff for iOS.
- **Config test** (inf). One small test per repo lists the approved runtime packages. It fails when `package.json` gains anything not on the list.
- **CI.** API Jest on Node 22; app Jest; Android and iOS release builds; compare the AAB and IPA sizes.
- **OneSignal.** `rg 'OneSignalXCFramework/(OneSignalLocation|OneSignalComplete)' ios/Podfile.lock` must print nothing (OneSignal's own check). The merged Android manifest shows no OneSignal location entry (inf).

## 11. Rollback

- **npm (API or app).** Revert the commit (manifest + lockfile), run `yarn install --frozen-lockfile` and redeploy. The attendance version gate and the log-only switch keep users unaffected meanwhile (inf).
- **Gradle.** Revert the dependency line, rebuild, and halt the staged Play rollout.
- **CocoaPods.** Revert `Podfile` and `Podfile.lock`, then `pod install`.
- **OneSignal.** If push breaks, go back to 5.4.1 and the aggregate pod; the Always keys return with it.

## Unknowns

1. **Production Node version** (§8).
2. **Firebase overlap.** Whether Play services basement and tasks are already in the app's Gradle graph through Firebase. The dependency diff will show.
3. **androidx.biometric 1.1.0** dates from 2021. It needs device testing of the Android 9–10 window path in P0, against the 1.4.0 alphas.
4. **The location-button View artifact** needing no Compose comes from Gradle metadata; it has not been tried.
5. **`node-app-attest` under Jest**, since it is ESM-only.
6. **A6 or not** — the typed client is easier to read; A1 alone means fewer packages.
7. **Secret handling** — where the API keeps secrets today and how they rotate is out of scope here (details: `private/_security-findings.md`, local only).

## Sources

Registries read 2026-10-01. **C** = confirmed; **U** = unclear.

- npm registry, every row in §1 and §4 — https://registry.npmjs.org/google-auth-library · https://registry.npmjs.org/cbor · https://registry.npmjs.org/@peculiar/asn1-x509 · https://registry.npmjs.org/@peculiar/asn1-android · https://registry.npmjs.org/@peculiar/asn1-apple · https://registry.npmjs.org/@googleapis/playintegrity · https://registry.npmjs.org/node-app-attest · https://registry.npmjs.org/cbor-x · https://registry.npmjs.org/cborg · https://registry.npmjs.org/@peculiar/x509 · https://registry.npmjs.org/react-native-onesignal — C
- Tree counts: `npm install --package-lock-only` in a scratch folder, compared with `api:yarn.lock` — C
- Google Maven (metadata, POM licence and date, AAR manifest minSdk, Gradle module metadata) — https://dl.google.com/android/maven2/com/google/android/play/integrity/maven-metadata.xml · https://dl.google.com/android/maven2/androidx/biometric/biometric/maven-metadata.xml · https://dl.google.com/android/maven2/com/google/android/gms/play-services-location/maven-metadata.xml · https://dl.google.com/android/maven2/androidx/core/locationbutton/group-index.xml — C
- AndroidX biometric releases (stable 1.1.0, alpha 1.4.0-alpha07) — https://developer.android.com/jetpack/androidx/releases/biometric — C
- Play Integrity setup (library, quotas) — https://developer.android.com/google/play/integrity/setup — C
- Google service-account sign-in ("we strongly encourage you to use libraries") — https://developers.google.com/identity/protocols/oauth2/service-account — C
- OneSignal React Native setup (`ONESIGNAL_DISABLE_LOCATION`, modular pods) — https://documentation.onesignal.com/docs/en/react-native-sdk-setup — C
- Google's Kotlin key-attestation verifier — https://github.com/android/keyattestation — C
- Location button guide — https://developer.android.com/guide/topics/permissions/private-alternatives/location-button — C
- Repo — `api:package.json:41` · `api:.github/workflows/test.yml:20` · `api:ecosystem.config.js:4-6` · `api:yarn.lock` · `app:package.json:54` · `app:ios/Podfile:73-74` · `app:ios/Podfile.lock:205,220` · `web:package.json:5-15`.
