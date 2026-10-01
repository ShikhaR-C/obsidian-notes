---
title: tasks_20 · 04 — platform, stores and law
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start".
---

# 04 — Platform, stores and law

Part of [[00-overview]]. Siblings: [[01-api]], [[02-app]], [[03-web]], [[05-round-1-web-design]] (superseded).

Platform facts are as of 2026-10-01, tagged `[S#]` (see **Sources**). Repo facts: `app:` = `dzzlo_oms_app` `slave` @ `ea7e7222`, `api:` = `dzzlo_oms_api` `slave` @ `86083ca`. "inf" = my inference.

## 0. Summary

Every piece the design adopts exists today: fake-location flags (`isMock()`, `sourceInformation`), Play Integrity standard requests, App Attest, an attested Keystore key and a Secure Enclave key. None proves presence alone. The flags are easy to hide on rooted or jailbroken phones. So a punch counts only when the flag, the integrity check, the device signature and the server's freshness, accuracy and distance rules all pass. On iOS the server cannot prove that the punch key is hardware-bound. It trusts the key because an App Attest-verified app registered it.

**Platform changes that matter:**

- Google Play requires a precise-location declaration from **27 Jan 2027**.
- Once the app targets **API 37**, check-ins must use Android 17's system location button.
- Android now hides whether Developer options are on.

**All devices (C‑20):** every phone the app supports can check in (§3.4).

- Android 11+ uses a per-use key.
- Android 7–10 uses a key unlocked for a short window after the user confirms.
- Phones without Play services and iPhones without App Attest are accepted with a flag (C‑29).

**Law:** under DPDP the dealer is the Data Fiduciary and VSYST the Data Processor. The core duties start **13 May 2027**. The Rules' one-year minimum retention collides with C‑8.

## 1. Fake-location detection

**Android:**

- `Location.isMock()` (API 31+) marks a fix from "a test location provider". Below API 31, `isFromMockProvider()` does the same; it is deprecated from 31 [S1].
- Android 15–17 changed nothing here [S2].
- **Which mock app is chosen cannot be read:**
  - `ALLOW_MOCK_LOCATION` has been "not used anymore" since API 23 [S3].
  - The choice is an app-op held by that app [S4]. Finding it needs QUERY_ALL_PACKAGES, which Play does not permit for this [S5].
  - `DEVELOPMENT_SETTINGS_ENABLED` now returns 0: "This will always return 0 for all third-party apps" [S6]. One report dates this to Android 17 QPR1 [S7, unclear].
- **Root modules hook `isMock()`** so it returns false [S8, unclear]. Play Integrity's device label is empty when it sees "API hooking" or rooting [S10]. So check 5 (`LOCATION_FAKE`) only counts together with check 4 (`INTEGRITY_FAILED`).

**iOS:**

- `CLLocation.sourceInformation` needs iOS 15+ and may be nil [S11]. The app's floor is 15.1 [S12].
  - `isSimulatedBySoftware` means "on-device software simulation", such as Xcode GPX files.
  - `isProducedByAccessory` means a "Made for iPhone GPS dongle or CarPlay".
- **Third-party tools are not flagged.** Apple DTS: "Any third-party tool can be utilized as an external location provider, but it will not have access to set that API flag" [S13][S14].
- **App Attest has limits too.** It "can't definitively pinpoint a device with a compromised operating system" [S27].

**What neither catches:**

| Trick                                    | Caught by                               | Left over                       |
| ---------------------------------------- | --------------------------------------- | ------------------------------- |
| Mock app, Xcode GPX                      | the flag (check 5)                      | —                               |
| Rooted Android hiding the flag           | Play Integrity (check 4)                | weaker before Android 13        |
| Jailbroken iPhone, computer-driven tools | partly App Attest                       | yes                             |
| External GPS accessory                   | `isProducedByAccessory` → dealer review | —                               |
| Radio GPS spoofing                       | nothing                                 | yes                             |
| A colleague with the phone and its PIN   | nothing (C‑19 allows the PIN)           | yes — only a selfie (C‑7) helps |

## 2. Integrity

### 2.1 Play Integrity (Android)

**Verdicts** [S10]:

- `PLAY_RECOGNIZED` also carries the package, the signing-certificate digest and the `versionCode`.
- `LICENSED` comes back `UNEVALUATED` when nobody is signed in to Google Play, and `UNLICENSED` when the app was sideloaded.
- `MEETS_DEVICE_INTEGRITY` on Android 13+ is hardware-backed proof of a locked bootloader and a certified OS.
- Opt-in signals: BASIC, STRONG (patched within a year), device activity, app access risk, Play Protect, device recall (beta).

Hardware-backed verdicts have applied to everyone since May 2025 [S15]. A `GET_INTEGRITY` fix-it dialog has existed since Nov 2025 [S16]. The library is `integrity:1.6.0` [S17].

|          | Standard (chosen)                                               | Classic                          |
| -------- | --------------------------------------------------------------- | -------------------------------- |
| Speed    | seconds to warm up (≤ 5 a minute), then a few hundred ms [S18]  | seconds [S20]                    |
| Binding  | `requestHash`, ≤ 500 bytes [S18]                                | `nonce`, 16–500 characters [S19] |
| Replay   | automatic: repeated decoding clears the verdicts [S18]          | ours                             |
| Decoding | only Google's `decodeIntegrityToken`, via service account [S18] | Google, or locally [S19]         |

**Binding:**

- `requestHash` = SHA-256(challenge ‖ payload). Google sees it in cleartext [S20], so Google gets a hash, never coordinates.
- `requestPackageName` "might be spoofed", so the server also checks `appIntegrity`: package `in.vsyst.dzzlooms` (`app:android/app/build.gradle:86`) and the certificate digest.
- The verified `versionCode` (105 today, `app:android/app/build.gradle:89`) can drive C‑26.

**Quota (C‑11):**

- Each project gets 10,000 token requests a day (classic plus standard _preparations_) and 10,000 decryptions a day. A raise takes a form and up to a week [S17].
- One decryption per punch covers ~5,000 Android staff doing IN + OUT.
- Prepare the provider only when a rostered user opens Attendance (inf).
- No official price page exists; "free" appears only in blogs (unclear).

**Low-end phones:** "Fewer devices are in the higher trust tiers" [S20]. Before Android 13 the device label may rest on software attestation. The Play Store and Play services must be present, and errors get a retry with backoff [S21]. Without them the verdict is `UNAVAILABLE`, accepted with a flag (C‑29). `LICENSED` needs a Play-signed-in account. Hence C‑21 starts log-only.

**Terms:** the API may not be used "to fingerprint or track individual users or devices" [S22]. Identity comes from our own key.

### 2.2 App Attest (iOS)

**Client flow** — iOS 14+, after `isSupported` [S23][S24]:

- **Enrolment:** `generateKey`, then `attestKey(keyId, SHA256(challenge))` with a challenge of ≥ 16 bytes.
- **Punch:** `generateAssertion(keyId, SHA256(clientData))`, where clientData is the punch payload.
- **Key life:** keys survive updates, not a reinstall, restore or new phone. Those cases re-enrol (PENDING, then dealer approval).

**Server checks:**

- **Attestation** [S25]:
  - the `x5c` chain to Apple's App Attest root;
  - the nonce SHA256(authData ‖ SHA256(challenge)) equals extension OID 1.2.840.113635.100.8.2;
  - key id = SHA256(public key);
  - RP ID = SHA256(Team ID.bundle ID);
  - counter 0;
  - production `aaguid`.
- **iOS 27 extensions:** `apple_validation_category_01` and `apple_bundle_version_01`. Apple's steps say to verify them [S25], and WWDC26 says to watch them for unexpected values [S26]. The bundle version can also feed C‑26.
- **Assertion:** the signature, a counter above the stored one, and the challenge.

**Other limits:**

- **Risk metric:** the receipt plus a DeviceCheck-key JWT returns the keys attested on the device in 30 days [S28]. Optional in v1.
- **Rate limits:** a ramp of ≤ 10 M users a day, and `attestKey` < 100 req/s [S29].
- **Unsupported phone:** "gracefully bypass the service" [S24]. Here that means `UNAVAILABLE`, accepted with a flag (C‑29).

## 3. Hardware keys and user verification

### 3.1 Android Keystore

- **Per-use key.** `setUserAuthenticationParameters(0, AUTH_BIOMETRIC_STRONG | AUTH_DEVICE_CREDENTIAL)` needs API 30. Each use goes through a BiometricPrompt CryptoObject [S30][S31].
  - Android 10 and below don't support that pair [S31]; they get a window key (§3.4).
  - Removing the lock screen destroys the key, so the phone must re-enrol [S30].
- **StrongBox or TEE.** Accept both.
  - Android's docs say "For most apps, StrongBox is not necessary"; fall back on `StrongBoxUnavailableException` [S32].
  - The Android 16 CDD mandates a TEE-backed Keystore with key attestation on handhelds. StrongBox is only "STRONGLY RECOMMENDED" [S33].
- **Attestation.** Create the key with `setAttestationChallenge` [S30]. The server checks [S34][S35]:
  - the chain reaches a Google root (a new root has signed since 1 Feb 2026 — trust both);
  - the revocation list;
  - the level is TrustedEnvironment or StrongBox;
  - the challenge;
  - `userAuthType`, `deviceLocked` and `verifiedBootState`;
  - `attestationApplicationId` (package and signing-certificate digests);
  - only the extension nearest the root.

### 3.2 iOS Secure Enclave

- **The key.** P-256 only. Needs `.privateKeyUsage`; prefer `kSecAttrAccessibleWhenUnlockedThisDeviceOnly` [S36].
- **Access flags** [S37]:
  - `.userPresence`: biometry OR passcode, no enrolment needed. This is the C‑19 fallback.
  - `.biometryAny`: needs enrolment.
  - `.biometryCurrentSet`: dies when biometrics change.
  - `.devicePasscode`: passcode only.
- **No attestation.** A plain Secure Enclave key cannot be attested outside MDM's Managed Device Attestation [S38]. Hence the App Attest registration.

### 3.3 What the server can prove

| Claim                          | Android                          | iOS                       |
| ------------------------------ | -------------------------------- | ------------------------- |
| Our unmodified app             | yes — `PLAY_RECOGNIZED` + digest | yes — App Attest          |
| Installed from the store       | yes — `LICENSED`                 | no direct signal          |
| Not rooted / jailbroken        | yes on 13+, weaker before        | not definitively          |
| Key in secure hardware         | yes — attestation                | no — via the attested app |
| Biometric or PIN on every use  | 11+: yes · 7–10: a window        | no — via the attested app |
| The holder is the staff member | no — PINs get shared             | no                        |
| The fix is real GPS            | no — only "not flagged"          | no — only "not flagged"   |

### 3.4 Every supported phone (C‑20, C‑29)

The user decided "yes all device support". The app's floor is Android 7 (minSdk 24) and iOS 15.1.

| Phone        | Key                                                                                 | How the user confirms                                                                              | What the attestation shows                                |
| ------------ | ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Android 11+  | per use: `setUserAuthenticationParameters(0, STRONG \| DEVICE_CREDENTIAL)`          | `BiometricPrompt` + `CryptoObject`                                                                 | `userAuthType` = password + fingerprint, no `authTimeout` |
| Android 7–10 | a window: `setUserAuthenticationValidityDurationSeconds(n)` (API 23, deprecated 30) | the confirm-credential screen (`KeyguardManager`, API 21) or androidx `BiometricPrompt`, then sign | `authTimeout` = n seconds → `auth: window`                |
| iPhone 15.1+ | Secure Enclave, `.userPresence`                                                     | Face ID, Touch ID or passcode                                                                      | none — registered through App Attest                      |

**Android 7–10 window key:**

- **Per-use keys need biometrics here.** Before API 30, per-use keys "can only use biometric authentication". Window keys "can only use secure lock screen authentication". They unlock when the user unlocks the lock screen or passes "the confirm credential flow initiated by `KeyguardManager.createConfirmDeviceCredentialIntent`" [S30].
- **The confirm screen** takes "pin, pattern, password or biometrics if enrolled". It was deprecated in API 29 but still works [S75].
- **androidx limits.** "DEVICE_CREDENTIAL alone is unsupported prior to API 30, and BIOMETRIC_STRONG | DEVICE_CREDENTIAL is unsupported on API 28-29" [S74].
- **Weaker by design (inf).** Any lock-screen unlock inside the window also unlocks the key. So keep the window short (the proposal is 30 s), and always show the confirm screen just before signing.
- **What the server reads.** KeyMint's `AUTH_TIMEOUT` is "the time in seconds for which the key is authorized for use, after user authentication". `USER_AUTH_TYPE` is PASSWORD (1) and/or FINGERPRINT (2) [S76]. So the server records `auth: window` and the window length, and caps it.
- **Old phones may not prove the key.** Attestation "was not required until Android 8.0". A device that launched below Android 7.0 produces a software-signed chain [S34]. Such a key is recorded as `key: unattested` and flagged.

**No screen lock:**

- **Android.** A key that needs user authentication "can only be generated if secure lock screen is set up" (`KeyguardManager.isDeviceSecure()`) [S30]. The app opens `ACTION_BIOMETRIC_ENROLL` on Android 11+, which sets up a PIN "if necessary" [S77], or `ACTION_SECURITY_SETTINGS` on older phones.
- **iOS.** `deviceOwnerAuthentication` "fails with the error passcodeNotSet if the device passcode isn't enabled" [S78]. The app asks the user to set a passcode.

**No Google Play services:**

- Play Integrity reports `PLAY_SERVICES_NOT_FOUND` or `PLAY_STORE_NOT_FOUND` [S21]. The verdict becomes `UNAVAILABLE`.
- The Keystore still attests, but a non-Play phone's chain may end at the maker's own root [S34]. That key is recorded as `key: unattested`.
- Push may not arrive either (inf).

**iPhone without App Attest:**

- Apple says "Not all device types support the App Attest service" [S23]. Failures show as `isSupported == false` or `DCError.featureUnsupported` [S79].
- Every iPhone on iOS 15.1 should support it, but Apple publishes no list (unclear).
- Such a phone is recorded `UNAVAILABLE` with `key: unattested`.

**C‑29 (open):** accept with a flag (recommended) or manual requests only.

- **Accept with a flag:** the punch counts, the dealer sees the flag, and the mock-location, freshness, distance and signature checks still apply.
- **Manual requests only:** stricter, but more work for dealers and staff.

## 4. Precision and outdoor accuracy

**Android 12+:**

- Request FINE and COARSE together. The user picks Approximate (~3 km²) or Precise ("usually within about 50 meters") [S39][S40].
- To upgrade, ask for both again. A downgrade restarts the app [S39]. Android 17 adds a location-access indicator [S41].
- `getAccuracy()` is the 68th-percentile radius [S1]. One fix in three lies outside its own circle; the 100 m radius absorbs that (inf).

**iOS 14+:**

- `requestTemporaryFullAccuracyAuthorization(withPurposeKey:)` needs its key in `NSLocationTemporaryUsageDescriptionDictionary`. It fails if accuracy is already full or the app is in the background. Expiry is postponed while the app is in use [S42][S43].
- `horizontalAccuracy` states no confidence level [S44].

**Outdoors:** "GPS-enabled smartphones are typically accurate to within a 4.9 m (16 ft.) radius under open sky… accuracy worsens near buildings, bridges, and trees" [S45]. The canopy is P0's main question.

## 5. React Native libraries

Versions come from the npm registry [S69]; maintenance flags from reactnative.directory [S70, unclear]. The app has no `expo` dependency, and a `git grep` at `ea7e7222` found no location code.

| Package                               | Latest · date        | Covers                                       | Gap                                      |
| ------------------------------------- | -------------------- | -------------------------------------------- | ---------------------------------------- |
| `@react-native-community/geolocation` | 3.4.0 · 2024-09-01   | TurboModule; `mocked` on Android and iOS 15+ | no temporary accuracy; unmaintained      |
| `react-native-geolocation-service`    | 5.3.1 · 2022-09-23   | Android `mocked`                             | unmaintained                             |
| `expo-location`                       | 57.0.20 · 2026-09-24 | Android `mocked` (`isMock`)                  | no iOS source info; needs `expo`         |
| `@expo/app-integrity`                 | 57.0.2 · 2026-09-11  | Play Integrity + App Attest                  | "currently in alpha"; needs `expo` [S71] |
| `@sbaiahmed1/react-native-biometrics` | 0.16.1 · 2026-09-08  | EC/RSA keys, PIN fallback                    | no attestation chain                     |
| `jail-monkey`                         | 3.0.0 · 2026-04-28   | root and mock heuristics                     | partly reads settings Android now hides  |
| `freerasp-react-native`               | 5.2.2 · 2026-09-29   | runtime protection                           | freemium; reports to Talsec              |

Also checked: `react-native-google-play-integrity` 1.1.0 (2024-06), `react-native-app-attest` 2.0.1 (2025-11) — tiny; `react-native-biometrics` 3.0.1 (2022) — stale; `react-native-keychain` 10.0.0 (2025-03) — secrets only, no signing.

**Picks — all in-house, as the sheet says:**

- `NativeCheckInLocation`: no library gives source info, temporary accuracy and the location button.
- `NativeAppIntegrity`: about four calls per platform.
- `NativeDeviceKey`: no library returns the attestation chain.
- Before API 37, a fourth piece: a Fabric view around the Jetpack location button.

## 6. Server-side verification libraries (C‑24)

The approval table, with licences, sizes, alternatives and the **Approved?** column, is [[06-package-approval-list]]. Nothing installs before the user ticks it.

**Constraints:**

- The API is CommonJS (`api:dzzlo_oms.js:1`).
- CI runs Node 22 (`api:.github/workflows/test.yml:20`), which `google-auth-library` 11 requires.

| Need                    | Pick                     | Version · date       | Why this one                                                                                                    |
| ----------------------- | ------------------------ | -------------------- | --------------------------------------------------------------------------------------------------------------- |
| Play Integrity decoding | `google-auth-library`    | 11.1.0 · 2026-09-16  | official; signs in the service account, then one POST; the typed `@googleapis/playintegrity` 28.1.0 is optional |
| CBOR (App Attest)       | `cbor`                   | 10.0.12 · 2026-03-04 | CommonJS, one small dependency; `cbor-x` adds an optional native add-on                                         |
| Certificates            | `@peculiar/asn1-x509`    | 2.10.0 · 2026-09-27  | reads the extensions; Node's `crypto` checks signatures; smaller than `@peculiar/x509`                          |
| Android key description | `@peculiar/asn1-android` | 2.10.0 · 2026-09-27  | KeyMint v300/v400 and legacy Keymaster                                                                          |

**Supporting notes:**

- **Test reference only:** `node-app-attest` 1.0.1 is ESM-only and shows no iOS 27 checks (unclear).
- **Kotlin verifier:** Google's own, `android/keyattestation`, is the reference for edge cases [S72]. The old sample is archived [S73].
- **Reused, not added:**
  - `jsonwebtoken` (`api:package.json:41`) signs Apple's risk-metric JWT.
  - Google's roots and revocation list are plain JSON over HTTPS [S34].
- **New secrets:** a Google service-account credential, and optionally an Apple DeviceCheck key.

## 7. Store checklist

### 7.1 Google Play

| Item                         | What to do                                                                                                                                                                                                                                                                                                             | Src            |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| Permissions                  | FINE + COARSE only. No background permission or foreground service, so no background form or video. Today the manifest asks only for INTERNET (`app:android/app/src/main/AndroidManifest.xml:3`).                                                                                                                      | [S46][S47]     |
| Precise-location declaration | "All apps requesting precise location (ACCESS_FINE_LOCATION) must complete a declaration … justify why the location button or coarse location is insufficient." Form from Nov 2026; enforced **27 Jan 2027**. Use case "One time location sharing" or "Other" (inf). Coarse (~3 km²) cannot place anyone within 100 m. | [S48]          |
| Location button              | At API 37: "If your use case requires precise location (ACCESS_FINE_LOCATION) only for one-time, user-initiated actions; you must implement the use of the Android location button". The app targets 36 (`app:android/build.gradle:6`), as updates must since 31 Aug 2026; no API 37 date yet.                         | [S49][S50][S9] |
| Disclosure + consent         | The disclosure "Must be within the app itself" and "Cannot only be placed in a privacy policy"; consent "Must require affirmative user action". The enrolment step covers both.                                                                                                                                        | [S51]          |
| Data safety                  | Precise location: collected, for "App functionality" and "Fraud prevention, security, and compliance". The dealer seeing punches after a user action with disclosure and consent is not "sharing" (inf). The device key as "Device or other IDs": unclear.                                                             | [S52]          |
| App access                   | Parts "restricted based on … location" need reviewer details: a demo user on a demo dealer's roster, with a review outlet.                                                                                                                                                                                             | [S53]          |
| OneSignal                    | The app resolves 5.4.1 (`app:yarn.lock:7452`), which bundles the location module; from 5.5.0 `ONESIGNAL_DISABLE_LOCATION` drops it.                                                                                                                                                                                    | [S54]          |

### 7.2 Apple App Store

| Item                | What to do                                                                                                                                                                                                                                                                                                                                                                                                                            | Src             |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| 5.1.1(ii)           | "Ensure your purpose strings clearly and completely describe your use of the data." Today's three strings say "needs Location access for good user experience!", and two are "Always" keys (`app:ios/dzzlo_oms_app/Info.plist:49-54`). Reword all three for the check-in. Keep them while OneSignal's location module is linked (`app:ios/Podfile.lock:205,220`; see [[02-app]] §5), and drop the two Always keys once it is removed. | [S56]           |
| New keys            | `NSLocationTemporaryUsageDescriptionDictionary`; `NSFaceIDUsageDescription` ("required if your app uses APIs that access Face ID"); the App Attest capability — the entitlements hold only push and an app group (`app:ios/dzzlo_oms_app/dzzlo_oms_app.entitlements:5-10`).                                                                                                                                                           | [S43][S55][S71] |
| 5.1.1(iv), 5.1.2(i) | "if a user declines to share Location, offer the ability to manually enter an address"; the app "may not require users to enable … location services … to access functionality". Only the check-in needs location; refusal leads to a manual request.                                                                                                                                                                                 | [S56]           |
| 5.1.5               | "notify and obtain consent before collecting, transmitting, or using location data" — the enrolment disclosure.                                                                                                                                                                                                                                                                                                                       | [S56]           |
| 2.1(a)              | "include demo account info (and turn on your back-end service!)" — the same demo user and review outlet, in Review Notes.                                                                                                                                                                                                                                                                                                             | [S56]           |
| Label + manifest    | Precise Location ("three or more decimal places"), linked, App Functionality (covers "prevent fraud"). `NSPrivacyCollectedDataTypes` is empty today (`app:ios/dzzlo_oms_app/PrivacyInfo.xcprivacy:42-43`); add `NSPrivacyCollectedDataTypePreciseLocation`.                                                                                                                                                                           | [S57][S58]      |
| 3.2                 | Not an issue. The rejection targets apps "designed for a specific business or organization"; DZZLO OMS is public and multi-dealer.                                                                                                                                                                                                                                                                                                    | [S59]           |

## 8. Android developer verification

No impact on DZZLO OMS:

- "You will automatically be registered if you distribute your app through Google Play" [S60]. Play App Signing apps are claimed automatically [S61].
- Enforcement began 30 Sep 2026 in four countries and goes global in 2027. There is no India-specific date [S62].

## 9. India DPDP — input to C‑27

| Topic      | Rule                                                                                                                                                       | Effect                                                                                       |
| ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Roles      | A fiduciary "determines the purpose and means" (s.2(i)); a processor acts "on behalf of" one (s.2(k)) [S63]                                                | Dealer = fiduciary, VSYST = processor. VSYST's own uses would make it a fiduciary (unclear). |
| Contract   | s.8(1): the fiduciary answers for its processor; s.8(2): processors only "under a valid contract" [S63]                                                    | The C‑27 clause.                                                                             |
| Safeguards | s.8(5); r.6: encryption, access control, logs, backups, one-year logs, a contract clause with the processor [S64]                                          | Into the clause.                                                                             |
| Breach     | s.8(6): the fiduciary tells the Board and each person; r.7: people "without delay", the Board's full report "within seventy-two hours" [S64]               | Processors have no direct duty, so the clause makes VSYST alert the dealer fast.             |
| Retention  | r.8(3): personal data and logs kept "for a minimum period of one year" [S64]                                                                               | **Collides with C‑8's 90 days.**                                                             |
| Basis      | s.7(i): "for the purposes of employment or those related to safeguarding the employer from loss or liability" [S63]                                        | No DPDP consent needed; store disclosures still apply.                                       |
| Dates      | G.S.R. 846(E), 13 Nov 2025: Board rules at once; consent managers 13 Nov 2026; notice, safeguards, breach, retention and rights **13 May 2027** [S64][S65] | Comply from launch anyway (inf).                                                             |
| Penalties  | up to ₹250 crore (safeguards), ₹200 crore (breach notice) [S66]                                                                                            | —                                                                                            |

**The C‑27 clause covers (inf):**

- purpose (attendance only);
- the r.6 safeguards;
- breach alerts to the dealer;
- sub-processors (Google, Apple, OneSignal, hosting);
- retention and erasure;
- help with staff rights requests;
- audit.

## 10. Recommended approach

1. **P0:** log fixes, accuracy, flags and verdicts under a real canopy before fixing the defaults.
2. **Location:** one fresh fix. Android sends `isMock()`/`isFromMockProvider()`, accuracy and age and re-asks if approximate; iOS uses temporary full accuracy, refuses `isSimulatedBySoftware`, flags `isProducedByAccessory`.
3. **Integrity:** Play Integrity standard bound by `requestHash`, requiring `PLAY_RECOGNIZED` + `LICENSED` + `MEETS_DEVICE_INTEGRITY` — log-only, then enforced (C‑21); App Attest once, then one assertion per punch.
4. **Keys:** an attested TEE/StrongBox key with biometric or PIN per use on Android 11+, and a short window on 7–10; a Secure Enclave `.userPresence` key registered via App Attest.
5. **Server:** the §6 libraries, after the user ticks [[06-package-approval-list]] (C‑24).
6. **C‑29:** phones without Play services or App Attest are accepted with a flag (recommended).
7. **P4 stores:** Play declaration, Data safety, App access; Apple strings, plist keys, capability, label, manifest, demo account; drop OneSignal's location module (then the Always keys).
8. **Before API 37:** the location-button view with `onlyForLocationButton`.
9. **Law:** the C‑27 clause before launch; settle C‑8 against r.8(3).

## Unknowns

1. **C‑8 vs r.8(3)** — 90 days against a one-year minimum (from 13 May 2027). Likely one year with tight access, then deletion; needs a legal read.
2. **s.8(2)** — "offering of goods or services to Data Principals" fits customers more than staff; the clause is prudent anyway.
3. **Commencement** — the Act's sections 3–17 from 13 May 2027 is from law-firm summaries [S67]; a 12-month cut was proposed, not notified [S68].
4. **Production Node version** (the Google clients need 22+).
5. **Current answers** in Play Data safety and the Apple label (not readable here).
6. **OneSignal 5.4.1** — whether it shares location by default once the permission exists.
7. **Reviewers** — how Google's and Apple's reviewers pass integrity once C‑21 enforces.
8. **Staff phones** — the share on Android 7–10 (window key), without Play services, without App Attest, or failing `MEETS_DEVICE_INTEGRITY` (P0/P4 telemetry). How a window key behaves on real Android 7–10 phones (P0).
9. **API 37 deadline** — not announced (pattern: 31 Aug 2027).
10. **Smaller** — the Android build that hides Developer options [S7]; the Play Integrity price; `node-app-attest` and iOS 27; the merged Android manifest.

## Sources

Read 2026-10-01. **C** = confirmed official page; **U** = unclear.

- S1 Android `Location` — https://developer.android.com/reference/android/location/Location — C
- S2 Android 17 behaviour changes (15, 16 also read) — https://developer.android.com/about/versions/17/behavior-changes-all — C
- S3 `Settings.Secure` — https://developer.android.com/reference/android/provider/Settings.Secure — C
- S4 `AppOpsManager` — https://developer.android.com/reference/android/app/AppOpsManager — C
- S5 Play QUERY_ALL_PACKAGES — https://support.google.com/googleplay/android-developer/answer/10158779 — C
- S6 `Settings.Global` — https://developer.android.com/reference/android/provider/Settings.Global — C
- S7 Shizuku-Next issue #4 — https://github.com/rushiranpise/Shizuku-Next/issues/4 — U
- S8 HideMockLocation — https://github.com/Xposed-Modules-Repo/io.github.auag0.hidemocklocation — U
- S9 Location button — https://developer.android.com/guide/topics/permissions/private-alternatives/location-button — C
- S10 Play Integrity verdicts — https://developer.android.com/google/play/integrity/verdicts — C
- S11 `CLLocationSourceInformation` — https://developer.apple.com/documentation/corelocation/cllocationsourceinformation — C
- S12 RN 0.84.1 iOS 15.1 — https://github.com/facebook/react-native/blob/v0.84.1/packages/react-native/scripts/cocoapods/helpers.rb — C
- S13 Apple forum (DTS) — https://developer.apple.com/forums/thread/803179 — C
- S14 Apple forum (staff) — https://developer.apple.com/forums/thread/797864 — C
- S15 Play Integrity, Dec 2024 — https://android-developers.googleblog.com/2024/12/making-play-integrity-api-faster-resilient-private.html — C
- S16 Play Integrity, Nov 2025 — https://developer.android.com/blog/posts/stronger-threat-detection-simpler-integration-protect-your-growth-with-the-play-integrity-api — C
- S17 Play Integrity setup, quotas — https://developer.android.com/google/play/integrity/setup — C
- S18 Standard requests — https://developer.android.com/google/play/integrity/standard — C
- S19 Classic requests — https://developer.android.com/google/play/integrity/classic — C
- S20 Overview — https://developer.android.com/google/play/integrity/overview — C
- S21 Error codes — https://developer.android.com/google/play/integrity/error-codes — C
- S22 Terms, data safety — https://developer.android.com/google/play/integrity/terms — C
- S23 `DCAppAttestService` — https://developer.apple.com/documentation/devicecheck/dcappattestservice — C
- S24 Establishing your app's integrity — https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity — C
- S25 Validating apps — https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server — C
- S26 WWDC26 session 201 — https://developer.apple.com/videos/play/wwdc2026/201/ — C
- S27 DeviceCheck — https://developer.apple.com/documentation/devicecheck — C
- S28 Assessing fraud risk — https://developer.apple.com/documentation/devicecheck/assessing-fraud-risk — C
- S29 Preparing to use App Attest — https://developer.apple.com/documentation/devicecheck/preparing-to-use-the-app-attest-service — C
- S30 `KeyGenParameterSpec.Builder` — https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder — C
- S31 Biometric auth — https://developer.android.com/identity/sign-in/biometric-auth — C
- S32 Keystore — https://developer.android.com/privacy-and-security/keystore — C
- S33 Android 16 CDD §9.11 — https://source.android.com/docs/compatibility/16/android-16-cdd — C
- S34 Key attestation — https://developer.android.com/privacy-and-security/security-key-attestation — C
- S35 Attestation schema — https://source.android.com/docs/security/features/keystore/attestation — C
- S36 Secure Enclave keys — https://developer.apple.com/documentation/security/protecting-keys-with-the-secure-enclave — C
- S37 `SecAccessControlCreateFlags` — https://developer.apple.com/documentation/security/secaccesscontrolcreateflags — C
- S38 Managed Device Attestation (that nothing else exists: U) — https://support.apple.com/guide/deployment/managed-device-attestation-dep28afbde6a/web — C
- S39 Runtime location permission — https://developer.android.com/develop/sensors-and-location/location/permissions/runtime — C
- S40 Location accuracy — https://developer.android.com/develop/sensors-and-location/location/permissions — C
- S41 Android 17 location privacy; release 16 Jun 2026 — https://developer.android.com/blog/posts/redefining-location-privacy-new-tools-and-improvements-for-android-17 · https://developer.android.com/blog/posts/android-17-is-here — C
- S42 Temporary full accuracy — https://developer.apple.com/documentation/corelocation/cllocationmanager/requesttemporaryfullaccuracyauthorization(withpurposekey:completion:) — C
- S43 `NSLocationTemporaryUsageDescriptionDictionary` — https://developer.apple.com/documentation/bundleresources/information-property-list/nslocationtemporaryusagedescriptiondictionary — C
- S44 `horizontalAccuracy` — https://developer.apple.com/documentation/corelocation/cllocation/horizontalaccuracy — C
- S45 GPS.gov accuracy — https://www.gps.gov/gps-accuracy — C
- S46 Play permissions policy — https://support.google.com/googleplay/android-developer/answer/9888170 — C
- S47 Play background location — https://support.google.com/googleplay/android-developer/answer/9799150 — C
- S48 Play location button and declaration timeline — https://support.google.com/googleplay/android-developer/answer/17033915 — C
- S49 Play policy preview (27 Jan 2027) — https://support.google.com/googleplay/android-developer/answer/16909972 — C
- S50 Play target API — https://support.google.com/googleplay/android-developer/answer/11926878 — C
- S51 Play User Data — https://support.google.com/googleplay/android-developer/answer/10144311 — C
- S52 Play Data safety — https://support.google.com/googleplay/android-developer/answer/10787469 — C
- S53 Play App access — https://support.google.com/googleplay/android-developer/answer/9859455 — C
- S54 OneSignal RN setup (default sharing: U) — https://documentation.onesignal.com/docs/en/react-native-sdk-setup — C
- S55 `NSFaceIDUsageDescription` — https://developer.apple.com/documentation/bundleresources/information-property-list/nsfaceidusagedescription — C
- S56 App Review Guidelines (8 Jun 2026) — https://developer.apple.com/app-store/review/guidelines/ — C
- S57 App privacy details — https://developer.apple.com/app-store/app-privacy-details/ — C
- S58 Privacy manifest data types — https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacycollecteddatatypes/nsprivacycollecteddatatype — C
- S59 Apple 3.2 rejection text (2019 forum) — https://developer.apple.com/forums/thread/126794 — C
- S60 Developer verification guides — https://developer.android.com/developer-verification/guides — C
- S61 Developer verification FAQ — https://developer.android.com/developer-verification/guides/faq — C
- S62 Developer verification — https://developer.android.com/developer-verification — C
- S63 DPDP Act 2023 — https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf — C
- S64 DPDP Rules, G.S.R. 846(E) (Gazette text, unofficial mirror: U) — https://www.dpdpa.com/DPDP_Rules_2025_English_only.pdf — C
- S65 PIB press release — https://www.pib.gov.in/PressReleasePage.aspx?PRID=2190014 — C
- S66 PIB explainer — https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf — C
- S67 Mondaq, Act commencement — https://www.mondaq.com/india/privacy-protection/1759134/indias-digital-personal-data-protection-act-and-the-dpdp-rules-2025-phased-commencement-core-obligations-and-a-board-ready-compliance-strategy — U
- S68 Chambers, 12-month proposal — https://chambers.com/articles/meity-plans-to-cut-short-dpdp-compliance-timeline-and-notify-cross-border-restrictions-for-sdfs — U
- S69 npm registry — https://registry.npmjs.org/ — C
- S70 React Native Directory — https://reactnative.directory/ — U
- S71 Expo docs — https://docs.expo.dev/versions/latest/sdk/app-integrity/ · https://docs.expo.dev/versions/latest/sdk/location/ — C
- S72 `android/keyattestation` — https://github.com/android/keyattestation — C
- S73 Archived sample — https://github.com/googlesamples/android-key-attestation — C
- S74 androidx `BiometricPrompt.PromptInfo.Builder` — https://developer.android.com/reference/androidx/biometric/BiometricPrompt.PromptInfo.Builder — C
- S75 `KeyguardManager` — https://developer.android.com/reference/android/app/KeyguardManager — C
- S76 KeyMint `Tag.aidl`, `HardwareAuthenticatorType.aidl` — https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/security/keymint/aidl/android/hardware/security/keymint/Tag.aidl · https://android.googlesource.com/platform/hardware/interfaces/+/refs/heads/main/security/keymint/aidl/android/hardware/security/keymint/HardwareAuthenticatorType.aidl — C
- S77 `Settings.ACTION_BIOMETRIC_ENROLL` — https://developer.android.com/reference/android/provider/Settings — C
- S78 `LAPolicy.deviceOwnerAuthentication` — https://developer.apple.com/documentation/localauthentication/lapolicy/deviceownerauthentication — C
- S79 `DCError.Code` — https://developer.apple.com/documentation/devicecheck/dcerror-swift.struct/code — C
- Library sources read — https://github.com/michalchudziak/react-native-geolocation · https://github.com/Agontuk/react-native-geolocation-service · https://github.com/sbaiahmed1/react-native-biometrics · https://github.com/GantMan/jail-monkey · https://github.com/talsec/Free-RASP-ReactNative · https://github.com/uebelack/node-app-attest · https://github.com/PeculiarVentures/asn1-schema · https://github.com/PeculiarVentures/x509 · https://github.com/googleapis/google-api-nodejs-client · https://github.com/kriszyp/cbor-x — C
- Repo — `app:` `android/build.gradle:4-6` · `android/app/build.gradle:86,89` · `android/app/src/main/AndroidManifest.xml:3` · `ios/dzzlo_oms_app/Info.plist:49-54` · `ios/dzzlo_oms_app/PrivacyInfo.xcprivacy:42-43` · `ios/dzzlo_oms_app/dzzlo_oms_app.entitlements:5-10` · `ios/Podfile.lock:205,220` · `package.json:49,54` · `yarn.lock:7452-7453`; `api:` `dzzlo_oms.js:1` · `package.json:41` · `.github/workflows/test.yml:20`.
