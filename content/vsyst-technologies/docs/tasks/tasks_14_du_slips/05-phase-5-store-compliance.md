# Phase 5 — Store & DPDP compliance

**Runs alongside Phases 3–4 from day one.** It gates the *release*, not the code — but the manifest shape and the consent flow constrain which capture library is viable, so decide this before installing anything.

**Bottom line up front:** the picker-first design (D6) makes this feature **zero runtime permissions on Android and exactly one on iOS**, sidesteps Play's Photo & Video declaration entirely, and satisfies Apple 5.1.1(iii) by construction. The two genuinely new obligations are (a) explicit, named, withdrawable consent for the OCR hop, and (b) reconciling DPDP Rule 8(3)'s one-year minimum retention against the account-deletion both stores require.

---

## 0. Repo baseline

| Fact | Value | Implication |
| --- | --- | --- |
| `android/build.gradle:4-8` | `minSdk 24`, `compileSdk 36`, **`targetSdk 36`** | Already meets the 31 Aug 2026 Play requirement. Nothing to do. |
| `AndroidManifest.xml:3` | **only** `INTERNET` | Clean slate. No `<queries>`, no `FileProvider`, no `xmlns:tools`. |
| Merged-in library permissions | netinfo → `ACCESS_NETWORK_STATE`, `ACCESS_WIFI_STATE`; firebase → `WAKE_LOCK` | No media/camera permission today. **Keep it that way.** |
| `ios/dzzlo_oms_app/Info.plist:49-53` | three `NSLocation*` keys, all *"$(PRODUCT_NAME) needs Location access for good user experience!"* | ⚠️ **Pre-existing App Review risk** — §3f |
| `PrivacyInfo.xcprivacy` | exists; FileTimestamp `C617.1`, UserDefaults `CA92.1/1C8F.1/C56D.1`, SystemBootTime `35F9.1`, DiskSpace `85F4.1`; `NSPrivacyCollectedDataTypes` **empty** | Two edits needed — §3c/§3d |
| Pods | Firebase + OneSignal each ship their own `PrivacyInfo.xcprivacy` (confirmed on disk) | ✅ SDK side satisfied |
| `minSdk 24 < 30` | — | Photo Picker **backport** wiring is mandatory — §1.3 |

---

## 1. Android

### 1.1 Target SDK — already compliant

From **31 August 2026**, new apps and all updates must target **Android 16 / API 36**; existing apps need API 35+ to stay available to new users on newer OS. Extension available to **1 November 2026**. You are on 36.

### 1.2 The headline: use the Photo Picker and declare **no** storage permission

Android's docs: *"No runtime permissions are required. The photo picker operates within scoped access — users explicitly select which media they share with your app."*

And Play's policy forces it. **Permissions and APIs that Access Sensitive Information**: *"All user Photos are personal and sensitive data subject to the User Data policy."* Apps targeting Android 13+ may request `READ_MEDIA_IMAGES`/`READ_MEDIA_VIDEO` only *"if system pickers (like the Android Photo Picker) are not sufficient for your app to provide core functionality."*

**Attaching a slip to an order is the textbook one-shot pick.** You will not get a broad-access declaration approved, and you don't need one:

- ❌ `READ_MEDIA_IMAGES`
- ❌ `READ_MEDIA_VIDEO`
- ❌ `READ_MEDIA_VISUAL_USER_SELECTED` *(exists only to manage partial grants of the above — pointless without them)*
- ❌ `READ_EXTERNAL_STORAGE`, even with `maxSdkVersion="32"` *(the picker's `ACTION_OPEN_DOCUMENT` fallback covers API 19–29 without it)*

### 1.3 🔴 The CAMERA trap

`MediaStore.ACTION_IMAGE_CAPTURE` **does not require** `CAMERA`. **But if `CAMERA` appears anywhere in the *merged* manifest it becomes mandatory at runtime**, and the intent throws `SecurityException` until granted. `react-native-image-picker`'s README says so explicitly.

Second trap: declaring `CAMERA` **implicitly adds `android.hardware.camera` + `.autofocus` as required features**, and Play then filters your app off devices lacking them.

**Option A (recommended) — intent-based capture, zero permissions.** `ACTION_IMAGE_CAPTURE` (what `launchCamera` does). No `CAMERA` declared. Users see **zero** permission dialogs for the entire feature.

**Option B — in-app camera (`react-native-vision-camera`)** if you need live edge detection. Then `CAMERA` is unavoidable and the `uses-feature` guards become mandatory. Only if Phase 3 §2.1 finds no healthy document-scanner wrapper.

### 1.4 The manifest block (Option A)

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
          xmlns:tools="http://schemas.android.com/tools">

    <uses-permission android:name="android.permission.INTERNET" />

    <!-- Only if you ship "Save to device gallery" on API<=28.
         OMIT IT — use the share sheet instead (§1.6). -->
    <!-- <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
                          android:maxSdkVersion="28" /> -->

    <!-- DELIBERATELY ABSENT: CAMERA, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO,
         READ_MEDIA_VISUAL_USER_SELECTED, READ_EXTERNAL_STORAGE.
         Gallery = Android Photo Picker; capture = ACTION_IMAGE_CAPTURE. -->

    <!-- Defensive: if a transitive dep drags CAMERA in, keep Play distribution open -->
    <uses-feature android:name="android.hardware.camera"           android:required="false" />
    <uses-feature android:name="android.hardware.camera.any"       android:required="false" />
    <uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />

    <!-- Android 11+ package visibility -->
    <queries>
        <intent><action android:name="android.media.action.IMAGE_CAPTURE" /></intent>
        <intent>
            <action android:name="android.intent.action.SEND" />
            <data android:mimeType="image/*" />
        </intent>
        <intent>
            <action android:name="android.intent.action.VIEW" />
            <data android:mimeType="image/*" />
        </intent>
    </queries>

    <application ... >
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data android:name="android.support.FILE_PROVIDER_PATHS"
                       android:resource="@xml/file_paths" />
        </provider>

        <!-- REQUIRED because minSdk=24 (<30): pulls the backported Photo Picker -->
        <service android:name="com.google.android.gms.metadata.ModuleDependencies"
                 android:enabled="false" android:exported="false"
                 tools:ignore="MissingClass">
            <intent-filter>
                <action android:name="com.google.android.gms.metadata.MODULE_DEPENDENCIES" />
            </intent-filter>
            <meta-data android:name="photopicker_activity:0:required" android:value="" />
        </service>
    </application>
</manifest>
```

`res/xml/file_paths.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <cache-path          name="shared_slips" path="slips/" />
    <files-path          name="slips"        path="slips/" />
    <external-files-path name="capture"      path="Pictures/" />
</paths>
```

`android/app/build.gradle`: `implementation "androidx.activity:activity:1.9.+"`

> ⚠️ **On `<queries>`:** `startActivity()` works without it. `<queries>` only matters for `resolveActivity()` / `queryIntentActivities()` — which is exactly what most picker libraries call *before* launching. Omitting it produces a silent "camera won't open" bug on Android 11+.

### 1.5 FileProvider + sharing

- `FLAG_GRANT_READ_URI_PERMISSION` on `ACTION_SEND`; `setClipData(ClipData.newUri(...))` for multi-image.
- Always `content://` via `FileProvider.getUriForFile()` — a `file://` URI across a package boundary throws `FileUriExposedException` on API 24+.
- To keep a picker URI for a background upload: `takePersistableUriPermission(...)` (cap: 5,000 grants). Better: copy to your own path (Phase 3 §3.2).

### 1.6 "Download the image" — use the share sheet

| API | Mechanism | Permission |
| --- | --- | --- |
| 29+ | `MediaStore.Images` + `RELATIVE_PATH` + `IS_PENDING` | none |
| 24–28 | direct public-dir write | `WRITE_EXTERNAL_STORAGE` |
| **all** | app cache → `FileProvider` → `ACTION_SEND`/`ACTION_VIEW`, user saves from the sheet | **none** ✅ |

**Ship the share-sheet route as the default.** You then drop `WRITE_EXTERNAL_STORAGE` entirely and the whole feature runs on **zero Android runtime permissions** — the best grant rate *and* the strongest Play-review posture.

---

## 2. Google Play

### 2a. Photo & Video Permissions declaration — **not needed**

Required only if the manifest declares `READ_MEDIA_IMAGES`/`READ_MEDIA_VIDEO`. Approved use cases are apps whose *core function* is managing all of a user's photos (gallery, backup, editor). Google explicitly warns *"custom pickers are not automatically qualified."*

Timeline for the record: form live 18 Sep 2024 → action deadline 22 Jan 2025 → **full compliance mandatory 28 May 2025, after which non-compliant apps are subject to removal.** Reviews *"may require up to several weeks"* — another reason not to need one.

### 2b. Data safety form

Google's definitions: **"Collect"** = *"transmitting data from your app off a user's device."* **"Sharing"** = *"transferring user data to a third party"* — **excluding** service providers (*"an entity that processes user data on behalf of the developer and based on the developer's instructions"*).

| Field | Answer |
| --- | --- |
| Data type | **Photos and videos → Photos** (*Personal content*) |
| Collected? | **Yes** |
| Shared? | **No — if** the OCR vendor is a contracted processor acting only on your instructions. **Yes — if** it may use images for its own purposes incl. training. **Turns entirely on your DPA. Get the no-train clause in writing, then answer "No".** |
| Processed ephemerally? | **No** — you store them |
| Required or optional? | **Optional** |
| Purpose | **App functionality** |
| Encrypted in transit? | **Yes** — must hold end-to-end incl. the OCR hop and any CDN |
| Deletion requestable? | **Yes** + a working URL |

Also declare as applicable: **Personal info** (dealer name/email/phone/user IDs), **App info and performance** (Crashlytics + Perf), **Device or other IDs** (OneSignal, device-info).

⚠️ Play Console now runs **automated binary checks** against the AAB and flags undeclared data types *before* human review. An under-declared form is an active rejection risk now, not paperwork.

### 2c. Privacy policy + account deletion — both mandatory

**Privacy policy** required in Console *and* in-app; a hard prerequisite for completing the Data safety form.

**Account deletion** — in scope because you have in-app account creation. Google requires **both**:
1. *"an in-app path to delete their app accounts and associated data"* — "intuitive" and "prominent (for example, within the account settings)"
2. a **web link** that "loads without error", is "prominently featured and easily discoverable", references the app/developer name, and works **without reinstalling the app**
3. the Data deletion questions completed in the Data safety form

Deletion must remove associated data **including uploaded slip images and any share links**. Retention for *"security, fraud prevention or regulatory compliance"* is permitted but *"you must clearly inform users about your data retention practices."* And: *"If your app relies on service providers to process user data, you should delete the data from your own servers and request the service provider to do the same"* — so you need a delete path **into the OCR vendor too**.

### 2d. 🔴 The 2026 Play position on third-party AI

**Policy announcement dated 15 July 2026**, under *Policy clarifications*:

> *"**User Data requirements also apply to third-party AI integrations and developers remain responsible for ensuring compliance with this policy, including limited use, disclosure and consent.**"*

Compliance window: at least 30 days from 15 July 2026 → practically **~14 August 2026**. Filed as a clarification (no new enforcement mechanism), but it makes the User Data policy — prominent disclosure, consent, limited use, no sale — explicitly binding on your OCR vendor relationship.

**Prominent Disclosure & Consent** (assume images→OCR exceeds user expectation, because it does):
- **In the app, immediately before** the capability is used. *"The message cannot be in the app description or website."*
- States **Why** (purpose), **What** (all data types), **How** (in context of the core feature)
- Offers **at least two options** — accept and decline/defer. *"Use clear and friendly language, such as 'Agree' rather than 'Allow access'."*
- *"is not a substitute for an app's privacy policy or Data Safety section"*

**Direction of travel:** the 15 April 2026 announcement added a Contacts Permissions policy mandating the **Android Contact Picker** and made the location button the recommended minimum scope, both effective **28 October 2026**. Google is systematically converting broad permissions into system pickers. Picker-first now is future-proof.

---

## 3. Apple

### 3a. Info.plist keys

| Key | Apple's trigger | Needed? |
| --- | --- | --- |
| `NSCameraUsageDescription` | *"required if your app uses APIs that access the device's camera"* | **Yes** |
| `NSPhotoLibraryUsageDescription` | *"…read or write access to the user's photo library"* | **No** with PHPicker — *unless a pod forces it* |
| `NSPhotoLibraryAddUsageDescription` | *"…write access"* | Only if you ship "Save to Photos" |

🔴 **ITMS-90683 — the override.** Apple's scan is static, over the **whole binary including pods**:

> *"App Review checks for the use of protected resources, and rejects apps that contain code accessing those resources without a purpose string… **If you're using external libraries or SDKs, they may reference APIs that require a purpose string. While your app might not use these APIs, a purpose string is still required.**"*

`react-native-image-picker` and `react-native-vision-camera` both link `Photos.framework`. **Audit the final pod set; ship the string if any pod references PhotoKit.**

Strings (5.1.1(ii) requires them to *"clearly and completely describe your use of the data"* — never "to upload images"):

```xml
<key>NSCameraUsageDescription</key>
<string>Take photos of delivery receipts and invoices to attach them to a sales order.</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>Attach existing photos of delivery receipts and invoices from your library to a sales order.</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>Save a copy of a receipt image from an order to your Photos library.</string>
```

### 3b. PHPicker removes both the prompt and the key

Apple, in two places:

> *"Because the system manages its life cycle in a separate process, it's private by default. **The user doesn't need to explicitly authorize your app to select photos**…"*
> *"**Apps don't need to request photo library permission when using either class**… An app can't take screenshots of content and can only read the assets that the user selects."*

**Condition:** consume results via `NSItemProvider` only. The moment you touch `PHAsset`/`PHPhotoLibrary` — including `PHPickerConfiguration(photoLibrary:)`, or reading EXIF via PhotoKit — you're back to needing the key and the prompt.

**Limited access (`.limited`) cannot occur** with a PHPicker-only design. That's a large simplification: no `.limited` branch, no re-selection UI, no `presentLimitedLibraryPicker`. Preserve it by never calling `PHPhotoLibrary.requestAuthorization(for: .readWrite)`.

Apple *requires* the picker — **5.1.1(iii) Data Minimization**: *"**Where possible, use the out-of-process picker or a share sheet rather than requesting full access to protected resources like Photos or Contacts.**"*

### 3c. Privacy manifest — one wrong reason code today

Enforcement: 13 Mar 2024 warnings → **1 May 2024** *"apps that don't describe their use of required reason API… aren't accepted by App Store Connect"* (ITMS-91053) → **12 Feb 2025** valid manifests required for commonly-used third-party SDKs (ITMS-91061).

Your manifest is already ahead of the RN template (you have DiskSpace at all). But:

| Category | You have | Should be |
| --- | --- | --- |
| FileTimestamp | `C617.1` ✅ | correct for cached slip images |
| UserDefaults | `CA92.1`, `1C8F.1`, `C56D.1` ✅ | keep |
| SystemBootTime | `35F9.1` ✅ | correct |
| DiskSpace | **`85F4.1`** ⚠️ | `85F4.1` = *"display disk space information to the person using the device"* — not what you do. **Add `E174.1`** = *"check whether there is sufficient disk space to write files, or… delete files when the disk space is low."* That's the image cache/download case, and the #1 cause of ITMS-91053 in photo apps. |

Firebase and OneSignal pods ship their own manifests (confirmed on disk) — both are on Apple's mandatory list. **You still need your own**; SDK manifests only cover SDK code. Verify the aggregate via **Xcode → Product → Archive → Generate Privacy Report**.

### 3d. `NSPrivacyCollectedDataTypes` — currently empty, must change

```xml
<key>NSPrivacyCollectedDataTypes</key>
<array>
  <dict>
    <key>NSPrivacyCollectedDataType</key>
    <string>NSPrivacyCollectedDataTypePhotosorVideos</string>   <!-- lowercase "or" — exact -->
    <key>NSPrivacyCollectedDataTypeLinked</key><true/>
    <key>NSPrivacyCollectedDataTypeTracking</key><false/>
    <key>NSPrivacyCollectedDataTypePurposes</key>
    <array><string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string></array>
  </dict>
</array>
```
Keep `NSPrivacyTracking = false`.

### 3e. App Privacy nutrition label

| Field | Answer |
| --- | --- |
| Data type | **User Content → Photos or Videos** |
| Used to Track You | **No** |
| Linked to You | **Yes** — images attach to an order tied to a dealer account |
| Purpose | **App Functionality** |

You **cannot** use the optional-disclosure exemption — it requires collection *"only in infrequent cases that are not part of your app's primary functionality."* Slip attachment is core.

The OCR vendor doesn't change the label (Apple's "collect" already spans *"you and/or your third-party partners"*). It changes your §3f obligations.

### 3f. Guideline 5.1 — including the AI clause

**5.1.2(i), updated 13 November 2025, verbatim:**

> *"Unless otherwise permitted by law, you may not use, transmit, or share someone's personal data without first obtaining their permission… **You must clearly disclose where personal data will be shared with third parties, including with third-party AI, and obtain explicit permission before doing so.**… Apps that share user data without user consent or otherwise complying with data privacy laws may be removed from sale and may result in your removal from the Apple Developer Program."*

**5.1.2(ii)** — *"Data collected for one purpose may not be repurposed without further consent."* 🔴 **If photo upload ships in v1.79 and OCR arrives in v1.80, every existing user must be re-consented.**

**5.1.2(iv)** — *"Do not use information from Contacts, Photos, or other APIs that access user data to build a contact database for your own use or for sale/distribution to third parties."* ⚠️ **Live risk:** DU slips carry customer names, phones and vehicle numbers. Keep OCR output scoped to the order record; **do not build a cross-order searchable index from it.**

**5.1.1(v)** — *"If your app supports account creation, you must also offer account deletion within the app."* Required since 30 June 2022. Must delete the record, not deactivate; a web link alone is insufficient — the flow must start in-app.

**OCR consent checklist to pass 5.1.2(i):**
- [ ] **Name the vendor** in-app and in the policy. "a third-party service" is not compliance.
- [ ] **Separate, explicit opt-in** before the first image leaves. Not in ToS, not pre-ticked.
- [ ] **Withdrawable** via a settings toggle (5.1.1(ii)).
- [ ] **Not a gate** — upload and view must work with OCR declined.
- [ ] Vendor contract: **no training, no retention**, deletion propagation.

### 3g. ⚠️ Pre-existing issue to fix in the same release

`ios/dzzlo_oms_app/Info.plist:49-53` declares all three `NSLocation*` keys with *"$(PRODUCT_NAME) needs Location access for good user experience!"*. If the app doesn't use location, that's an unnecessary protected-resource declaration (5.1.1(iii)) **with** a vague purpose string (5.1.1(ii)) — a classic rejection pair.

**Remove the keys if unused; rewrite the string if used.** Do it in this release, because adding new permission keys invites a fresh privacy audit of the whole plist.

---

## 4. India — DPDP Act 2023 + Rules 2025

### 4.1 Status: you are in the transition window

**DPDP Rules 2025 — G.S.R. 846(E), dated 13 November 2025**, gazette-published 14 November 2025 (`CG-DL-E-14112025-267650`). Rule 1 commencement, verbatim:

> *"(2) Rules 1, 2 and 17 to 21 shall come into force on the date of their publication… (3) **Rule 4 shall come into force one year after**… (4) **Rules 3, 5 to 16, 22 and 23 shall come into force eighteen months after** the date of publication."*

| Phase | Date | What |
| --- | --- | --- |
| Now | 13–14 Nov 2025 | Definitions; Data Protection Board machinery only |
| +12 mo | Nov 2026 | Rule 4 — Consent Manager registration |
| **+18 mo** | **~14 May 2027** | **Rules 3, 5–16** — notice, consent, security safeguards, breach reporting, retention/erasure, rights, cross-border |

**The substantive obligations do not legally bite until mid-May 2027.** But it's ~10 months away, CERT-In applies *today*, and retrofitting consent + retention into a photo pipeline is far more expensive than building it right. **Build to the 2027 standard now.**

⚠️ The Act's own section-by-section commencement (reportedly G.S.R. 843(E) of 13 Nov 2025) could not be verified from the primary source — `meity.gov.in` blocks HTML fetches. **Confirm with counsel.** Likewise whether s.44 (repealing IT Act s.43A / the SPDI Rules 2011) has commenced.

### 4.2 What the Rules require

**Rule 3 — Notice.** Must be *"presented and be understandable **independently of any other information**"* — a **standalone consent notice, not a ToS clause**. Minimum: an **itemised description of the personal data**, the **specified purposes**, and the link/means to **withdraw consent** *"with the ease of doing so being comparable to that with which such consent was given"*, exercise rights, and complain to the Board.

**Rule 6 — Security safeguards**, minimum: (a) **encryption, obfuscation, masking or virtual tokens**; (b) access control incl. processors'; (c) **logs, monitoring, review**; (d) backups/continuity; (e) **retain such logs and personal data for one year**; (f) **contractual security obligations flowed down to every Data Processor** ← your OCR vendor and cloud storage; (g) technical + organisational measures.

Note (a) explicitly blesses encryption — **a well-encrypted offshore bucket is arguably more compliant than an unencrypted Mumbai one.** SSE-KMS (Phase 2 §1.4) maps directly onto this.

**Rule 7 — Breach notification, two tracks.** To each affected individual *"without delay"* — nature/extent/timing, consequences *for them*, mitigation implemented, safety measures *they* can take, and a **business contact who can respond**. To the Board *"without delay"*, then a **detailed report within 72 hours**.

**Rule 8 — Retention.** The Third Schedule 3-year erasure rule **does not apply to you** — it covers e-commerce ≥2 crore users, gaming ≥50 lakh, social media ≥2 crore. But **8(3) applies to everyone**: retain personal data, traffic data and processing logs for a **minimum of one year**, *"unless further retention is required for compliance with any other law."*

🔴 **This constrains your store-mandated deletion flow.** Design deletion as: *immediate revocation of access + soft delete + audit-log retention for 1 year + hard purge at the legal floor*, and say exactly that in the privacy policy. Play explicitly permits retention for *"legitimate reasons such as… regulatory compliance"* **if disclosed**.

Note also s.8(7): erasure on withdrawal applies *"unless retention is necessary for compliance with any law"* — **and GST s.36 is exactly such a law**. Your GST duty defeats an erasure request for slips tied to a taxable supply.

**Rule 9 — Contact.** Prominently publish on website/app, and mention in **every response** to a rights request, the business contact of the DPO or an answering person.

**Rule 14 — Rights.** Publish the request mechanism and any required identifier. **Grievance response within 90 days.**

**Rule 15 / s.16 — Cross-border: a negative list, not localisation.** s.16(1): *"The Central Government **may**, by notification, restrict the transfer of personal data… to such country or territory outside India as may be so notified."* This is the inverse of GDPR adequacy — **no country has been notified.** The draft SDF localisation survived as **Rule 13(4)** but is triply dormant: applies only to notified SDFs (no list exists), only to Government-specified data categories (none specified), and doesn't commence until 2027. A fuel-dealer SaaS will not be designated.

**Penalties (Schedule, s.33):** up to **₹250 crore** — failure of reasonable security safeguards; **₹200 crore** — failure to notify a breach; ₹150 crore — SDF duties; **₹50 crore** — any other contravention. Ceilings; s.33(2) requires proportionality.

### 4.3 CERT-In — in force **today**, and the part most write-ups get wrong

**No. 20(3)/2022-CERT-In, 28 April 2022**, effective ~27 June 2022 (25 Sept 2022 for MSMEs), unamended through July 2026. You are in scope — the FAQ defines "body corporate" to include *"any company and includes a firm, sole proprietorship or other association of individuals engaged in commercial or professional activities."*

- **Report listed cyber incidents within 6 hours** of noticing (`incident@cert-in.org.in`). Annexure I expressly includes *"attacks affecting Cloud computing systems/servers/software/applications"* — **an S3 bucket compromise is reportable in 6 hours.**
- **Enable logs of all ICT systems, retain a rolling 180 days**, Direction (iv) saying *"maintained within the Indian jurisdiction."*
- **NTP sync** to NIC/NPL servers.
- Designate a **Point of Contact** (Annexure II).
- Non-compliance → IT Act s.70B(7), up to 1 year and/or ₹1 lakh.

🔴 **The correction worth recording — CERT-In FAQ (May 2022) Q35, verbatim:**

> *"**Q 35. Is it required to store copy of logs in India only?** Ans.: The logs may be stored outside India also as long as the obligation to produce logs to CERT-In is adhered to by the entities in a reasonable time."*

**The obligation is producibility, not residency.** Several well-known law-firm notes state a copy must be retained in India; that is wrong. And this governs **logs, not the slip images.**

⚠️ **The 6-hour CERT-In clock is tighter than DPDP's 72-hour Board report.** Your incident runbook must satisfy both.

### 4.4 Is in-India storage required? No — but do it anyway

**No provision reaches these images.** DPDP is a negative list with zero countries notified and doesn't bite until 2027; GST has no location rule and binds your dealer customer, not you; Companies Act Rule 3(5) covers *your own books of account*, not customer receipt photos held as a hosted service; RBI's payment-data rule binds authorised payment system operators, which you are not; CERT-In covers logs and expressly permits offshore.

**Store in `ap-south-1` anyway** — latency, procurement optics with enterprise dealer groups, pre-empting Rule 13(4) at scale, and avoiding DPA renegotiation later. It costs about the same. Defensible-by-default, not compelled.

### 4.5 Privacy-policy checklist

- [ ] Identity + registered address of the Data Fiduciary; **DPO or answering-person contact** (Rule 9), in-app *and* on the website
- [ ] **Itemised** data list — name *"photographs of delivery receipts uploaded by the user"* explicitly, plus anything OCR extracts
- [ ] **Specified purpose** per item + description of the service enabled
- [ ] Legal basis; which processing relies on "legitimate uses"
- [ ] **How to withdraw consent**, as easily as it was given; consequences
- [ ] **Named** processors: cloud storage, **OCR vendor by name**, Firebase, OneSignal — with an equal-protection statement (Apple 5.1.1(i))
- [ ] **Cross-border transfer** — which vendors, which regions
- [ ] **Retention schedule** — the Rule 8(3) one-year minimum, CERT-In's 180-day logs, the ~7-year GST horizon; what survives account deletion and for how long
- [ ] **Rights** — access, correction, erasure, nomination, grievance — with mechanism, identifier, and the **90-day** commitment
- [ ] **Grievance redressal** — officer name/designation/email, escalation to the Data Protection Board, appeals to TDSAT
- [ ] **Breach notification** commitment (individual without delay; Board without delay + 72 h)
- [ ] **Security measures** mapped to Rule 6(a)–(g)
- [ ] **The share link** (if shipped) — that it exists, what it exposes, default expiry, how to revoke, that it's `noindex`
- [ ] Children's data — state the service is B2B / 18+
- [ ] **Account & data deletion** — in-app path + the public web URL (same one in Play Console)
- [ ] ⚠️ Rule 3 requires the notice in **English + the Eighth Schedule languages**. Build the *notice* string table with i18n keys from day one even if you launch English + Hindi. **Scope this with counsel — it's a real product cost.**

---

## 5. Permission UX

### 5.1 The flow — it asks for almost nothing

| Step | Android | iOS |
| --- | --- | --- |
| "Attach slip" tapped | sheet: **Take photo** / **Choose from gallery** | same |
| **Gallery** | `PickVisualMedia` → **no permission, no dialog** | `PHPickerViewController` → **no permission, no dialog** |
| **Camera (Option A)** | `ACTION_IMAGE_CAPTURE` → **no permission** | `NSCameraUsageDescription` prompt — unavoidable |
| **Camera (Option B)** | rationale → `CAMERA` prompt | same |
| Before first OCR send | **Prominent disclosure sheet** (Why / What / How + Agree / Not now) | same — satisfies Apple 5.1.2(i) |

**Net: zero OS permission dialogs on Android, exactly one on iOS.** That is the maximum achievable grant rate and simultaneously the strongest review posture.

### 5.2 Rationale, and "denied forever"

Show a rationale only for `CAMERA` (Option B), never for the pickers, and **trigger it in context** on the "Take photo" tap — never at launch. Play: *"Request permissions… in context (via incremental requests)."*

Android's permanent-denial rule: *"if the user taps Deny for a specific permission more than once during your app's lifetime of installation on a device, **the user will no longer see the system permissions dialog**."* Detect via `shouldShowRequestPermissionRationale() === false` *after* a denial.

⚠️ **Do not auto-open Settings.** Android: *"respect the user's decision. **Don't link to system settings in an effort to convince the user to change their decision.**"* Apple 5.1.1(iv): *"must not attempt to manipulate, trick, or force people to consent… Where possible, provide alternative solutions for users who don't grant consent."*

**Handling:** a non-blocking inline note — *"Camera is off for DZZLO OMS. You can still choose an existing photo."* — with (a) a prominent **"Choose from gallery"** button (the working alternative that satisfies 5.1.1(iv)) and (b) a *secondary*, user-initiated **"Open Settings"**. User-initiated is fine; auto-redirect is not.

### 5.3 React Native specifics

- **`PermissionsAndroid`** (core, no dependency) covers the only Android permission you might need (`CAMERA`, Option B) — `request`, `check`, `NEVER_ASK_AGAIN`. The app's single existing usage is `src/components/Download/Invoice.js:63-84` — dead code, and it requests `WRITE_EXTERNAL_STORAGE`, which is inert at API 36.
- **`react-native-permissions`** — you probably don't need it. Worth adding only for Option B on iOS or for `RESULTS.BLOCKED` semantics without hand-rolling. It adds a Podfile `setup_permissions` step. Its docs emphasise `openPhotoPicker()` for the `.limited` case — a workflow you're deliberately avoiding, which is a good signal it's redundant here. ⚠️ Version noted as 5.6.1 (~24 July 2026) — re-check before pinning.
- ⚠️ Whatever picker/crop/FS library you add, **check it against Apple's third-party SDK list** and re-run Generate Privacy Report.
- ⚠️ `react-native-html-to-pdf@1.3.0` is unmaintained and already in your deps — audit whether it wants `WRITE_EXTERNAL_STORAGE` at API 36 before it collides with this work.

---

## 6. Pre-submission checklist

### Android build
- [ ] `targetSdkVersion 36` ✅ (re-verify after any Gradle bump)
- [ ] **Merged** manifest audited — `./gradlew :app:processReleaseManifest`, then read `app/build/intermediates/merged_manifests/release/AndroidManifest.xml`. Confirm **no** `READ_MEDIA_*`, no `READ_EXTERNAL_STORAGE`, **no unintended `CAMERA`**
- [ ] `xmlns:tools` on `<manifest>`; `<queries>` present
- [ ] `FileProvider` + `res/xml/file_paths.xml`, authority `${applicationId}.fileprovider`
- [ ] `ModuleDependencies` service present + `androidx.activity:activity:1.9.+`
- [ ] `uses-feature` camera guards `required="false"`
- [ ] Tested on Android 9 / 11 / 13 / 14 / 16 — picker backport confirmed on 9/10
- [ ] All uploads HTTPS; `usesCleartextTraffic` release value confirmed

### Play Console
- [ ] Data safety per §2b; deletion questions completed
- [ ] In-app deletion path prominent; **web deletion URL loads, names the app/developer, works without reinstall**
- [ ] Privacy policy URL in Console **and** in-app
- [ ] **No Photo & Video declaration alert** on the App content page
- [ ] In-app **prominent disclosure + consent** before any image goes to OCR (§2d) — compliance ~14 Aug 2026
- [ ] OCR vendor contract: processor-only, **no training, no retention**, deletion propagation, security flow-down (Rule 6(f))

### iOS build
- [ ] `NSCameraUsageDescription` with the specific string
- [ ] `NSPhotoLibraryUsageDescription` — omit unless a pod references PhotoKit (ITMS-90683)
- [ ] `NSPhotoLibraryAddUsageDescription` only if "Save to Photos" ships
- [ ] ⚠️ **The three `NSLocation*` keys removed or fixed** (§3g)
- [ ] `PrivacyInfo.xcprivacy`: **DiskSpace `E174.1` added**; `NSPrivacyCollectedDataTypePhotosorVideos` block added; `NSPrivacyTracking=false`
- [ ] **Product → Archive → Generate Privacy Report** clean
- [ ] PHPicker used; **no** `PHPhotoLibrary.requestAuthorization(for: .readWrite)` in app or pods
- [ ] In-app account deletion present and prominent (5.1.1(v))

### App Store Connect
- [ ] App Privacy: **User Content → Photos or Videos**, Linked = Yes, Tracking = No, Purpose = App Functionality
- [ ] Privacy policy URL in metadata **and** in-app
- [ ] Reviewer notes: demo account, a sample order, path to the attach flow, one line on OCR + explicit consent
- [ ] OCR consent: **named vendor**, separate opt-in, withdrawable, not a gate (5.1.2(i))

### India / DPDP (build now, binding ~May 2027)
- [ ] Standalone Rule 3 notice — not a ToS clause; itemised; withdrawal link; i18n scaffolding
- [ ] Withdraw-consent as easy as giving it
- [ ] Rule 6: encryption at rest + in transit, access control, access logs, backups, **1-year log retention**, processor contracts
- [ ] Breach runbook satisfying **CERT-In 6 h** *and* **DPDP without-delay + 72 h**, with all five Rule 7(1) elements
- [ ] Rule 8(3) one-year retention reconciled with the store deletion promises, and disclosed
- [ ] Grievance officer published; **90-day** SLA instrumented
- [ ] CERT-In: NTP sync to NIC/NPL, 180-day ICT logs producible, Point of Contact registered

---

## 7. Verify before submitting

1. **Play Console UI** for the Photo & Video declaration and Data safety — Google reshuffles these pages frequently.
2. **DPDP Act commencement** (G.S.R. 843(E)) — Rules verified from the Gazette PDF; the Act's section-by-section commencement was not. **Counsel.**
3. **SPDI Rules 2011 / IT Act s.43A** — whether DPDP s.44 has commenced. **Counsel.**
4. **Rule 3 language obligation** — the exact set of Eighth Schedule languages required. **Counsel.** Real product cost.
5. **`react-native-permissions` 5.6.1** — re-check before pinning.
6. **Apple App Review Guidelines** carry no last-updated stamp and are a living document. Re-check `developer.apple.com/news/` before each submission.
7. **Cross-border** — check for any general/special order under s.16 / Rule 15 naming your OCR vendor's jurisdiction before go-live.
8. **Data Protection Board appointment status** — MeitY was still advertising for Chairperson + 4 Members on 6 May 2026.
