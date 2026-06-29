# Plan: Firebase App Distribution — One-Command Beta Releases (Android + iOS)

## Goal

Run **one command** to build and ship a release build of the DZZLO OMS app (`in.vsyst.dzzlooms`) to testers via Firebase App Distribution — both Android (APK/AAB) and iOS (IPA) — without going through Play Console / TestFlight.

```bash
# The one command
yarn distribute                 # both platforms, testing env
yarn distribute:android         # android only
yarn distribute:ios             # ios only
yarn distribute:prod            # both, production env
```

> **Prereq:** `FIREBASE_INTEGRATION_PLAN.md` must be done first — Firebase SDK wired up, `google-services.json` / `GoogleService-Info.plist` aligned with project `dzzlo-oms`. App Distribution itself does **not** require the Firebase SDK to be integrated into the app, but the app IDs registered in the Firebase console must match the release build's package/bundle ID.

---

## Why Firebase App Distribution

| Alternative             | Pain                                                                 |
| ----------------------- | -------------------------------------------------------------------- |
| Manual APK sharing      | No install-tracking, no version management, testers miss updates    |
| TestFlight              | Apple-only, slow review for external testers, needs App Store Connect setup |
| Google Play Internal    | 24h+ propagation, Play Console review friction                       |
| **App Distribution**    | Instant, unified Android+iOS, email invites, in-app tester SDK       |

---

## Current State (relevant bits)

- Android package id: `in.vsyst.dzzlooms` (present in `android/app/google-services.json`)
- iOS bundle id: `in.vsyst.dzzlooms` (present in `ios/GoogleService-Info.plist`)
- Firebase project: `dzzlo-oms`
- Existing scripts: `dzzlo_oms_app/build-release-apk.sh`, `build-install-apk.sh`
- Release signing: Android keystore assumed configured via `android/gradle.properties` or `~/.gradle/gradle.properties` (verify before first run). iOS release signing must be configured in Xcode (automatic or manual signing with a distribution profile).

---

## Step-by-step Implementation

### Step 1 — Register apps in Firebase App Distribution

Both Android and iOS apps are already registered in the Firebase project `dzzlo-oms`. Grab the **Firebase App IDs** (not package/bundle ids) from the Firebase console:

- Firebase Console → Project Settings → **Your apps**
- Android App ID looks like: `1:1234567890:android:abcd1234ef`
- iOS App ID looks like: `1:1234567890:ios:abcd1234ef`

Save these — they're used by the distribute CLI. Store them in `.env.distribution` (gitignored) or in CI secrets.

### Step 2 — Create tester groups

Firebase Console → **App Distribution** → **Testers & Groups** → create groups:

- `qa` — internal QA testers (default for `testing` env)
- `beta` — external beta testers (for `production` pre-release)

Add tester emails to each group. Testers get an invite email the first time a build targets their group.

### Step 3 — Install Firebase CLI

```bash
# global
npm install -g firebase-tools

# or run on demand (preferred, version-pinned)
npx firebase-tools@13 <cmd>
```

Authenticate **once** on the developer machine:

```bash
firebase login
```

For CI/headless, prefer a **service account** over `firebase login:ci` (deprecated). Create one:

- Firebase Console → Project Settings → **Service accounts** → Generate new private key
- Save JSON at `~/.secrets/firebase-dzzlo-oms.json` (NOT in repo)
- Export for CLI: `export GOOGLE_APPLICATION_CREDENTIALS=~/.secrets/firebase-dzzlo-oms.json`

### Step 4 — Create `.env.distribution` (gitignored)

In `dzzlo_oms_app/.env.distribution`:

```bash
# Firebase App Distribution
FIREBASE_ANDROID_APP_ID=1:1234567890:android:abcd1234ef
FIREBASE_IOS_APP_ID=1:1234567890:ios:abcd1234ef

# Default groups to distribute to (comma-separated, no spaces)
FIREBASE_TESTER_GROUPS_TESTING=qa
FIREBASE_TESTER_GROUPS_PRODUCTION=qa,beta

# Path to service account JSON (leave empty to use `firebase login`)
GOOGLE_APPLICATION_CREDENTIALS=/Users/you/.secrets/firebase-dzzlo-oms.json

# iOS signing (used by exportArchive)
IOS_EXPORT_METHOD=ad-hoc          # or: development, app-store (App Distribution accepts ad-hoc / development / enterprise)
IOS_TEAM_ID=ABCDE12345
IOS_PROVISIONING_PROFILE=         # leave empty for automatic signing
```

Add to `.gitignore`: `.env.distribution`.

### Step 5 — iOS export options plist

Create `dzzlo_oms_app/ios/ExportOptions.plist` (ad-hoc template — xcodebuild needs this for `-exportArchive`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>ad-hoc</string>
    <key>teamID</key>
    <string>REPLACE_WITH_TEAM_ID</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>stripSwiftSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
    <key>uploadBitcode</key>
    <false/>
    <key>uploadSymbols</key>
    <true/>
</dict>
</plist>
```

> **Why ad-hoc:** App Distribution accepts `ad-hoc`, `development`, or `enterprise` signed IPAs. `app-store` signing is for App Store Connect only and will be rejected.

### Step 6 — Android distribute script

Create `dzzlo_oms_app/scripts/distribute-android.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./scripts/distribute-android.sh [development|testing|production]
ENV_ARG="${1:-testing}"
case "$ENV_ARG" in
  development|testing|production) ;;
  *) echo "❌ Invalid environment: $ENV_ARG"; exit 1 ;;
esac

# Load distribution env
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
set -a; source .env.distribution; set +a

# Pick the tester group for this env
case "$ENV_ARG" in
  production) GROUPS="$FIREBASE_TESTER_GROUPS_PRODUCTION" ;;
  *)          GROUPS="$FIREBASE_TESTER_GROUPS_TESTING"    ;;
esac

# 1) Build release APK (reuses existing logic)
export APP_ENV="$ENV_ARG"
echo "📦 [android] Building release APK for APP_ENV=$APP_ENV..."
bash ./build-release-apk.sh "$ENV_ARG"

APK_PATH="android/app/build/outputs/apk/release/app-release.apk"
[ -f "$APK_PATH" ] || { echo "❌ APK not found at $APK_PATH"; exit 1; }

# 2) Release notes from last 10 commits (strip author)
RELEASE_NOTES=$(git log -10 --pretty=format:"- %s" 2>/dev/null || echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) $ENV_ARG build")

# 3) Upload to App Distribution
echo "🚀 [android] Uploading to Firebase App Distribution → groups: $GROUPS"
npx firebase-tools@13 appdistribution:distribute "$APK_PATH" \
  --app "$FIREBASE_ANDROID_APP_ID" \
  --groups "$GROUPS" \
  --release-notes "$RELEASE_NOTES"

echo "✅ [android] Uploaded $APK_PATH"
```

> Prefer AAB for Play Console, but App Distribution only accepts **APK** for Android. Keep APK output.

### Step 7 — iOS distribute script

Create `dzzlo_oms_app/scripts/distribute-ios.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./scripts/distribute-ios.sh [development|testing|production]
ENV_ARG="${1:-testing}"
case "$ENV_ARG" in
  development|testing|production) ;;
  *) echo "❌ Invalid environment: $ENV_ARG"; exit 1 ;;
esac

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
set -a; source .env.distribution; set +a

case "$ENV_ARG" in
  production) GROUPS="$FIREBASE_TESTER_GROUPS_PRODUCTION" ;;
  *)          GROUPS="$FIREBASE_TESTER_GROUPS_TESTING"    ;;
esac

export APP_ENV="$ENV_ARG"

# Kill metro (mirrors build-release-apk.sh)
pkill -f 'react-native start' || pkill -f metro || true
lsof -ti:8081 | xargs kill -9 2>/dev/null || true

# 1) Clean & pod install
echo "🧹 [ios] Resetting JS caches..."
yarn reset || true

echo "📦 [ios] pod install..."
cd ios
pod install
cd ..

# 2) Archive + Export
SCHEME="dzzlo_oms_app"
WORKSPACE="ios/${SCHEME}.xcworkspace"
BUILD_DIR="ios/build/distribute"
ARCHIVE_PATH="$BUILD_DIR/${SCHEME}.xcarchive"
IPA_DIR="$BUILD_DIR/ipa"

rm -rf "$BUILD_DIR"
mkdir -p "$IPA_DIR"

echo "🏗  [ios] xcodebuild archive..."
xcodebuild \
  -workspace "$WORKSPACE" \
  -scheme "$SCHEME" \
  -configuration Release \
  -sdk iphoneos \
  -destination 'generic/platform=iOS' \
  -archivePath "$ARCHIVE_PATH" \
  -allowProvisioningUpdates \
  archive

echo "📤 [ios] xcodebuild -exportArchive..."
xcodebuild \
  -exportArchive \
  -archivePath "$ARCHIVE_PATH" \
  -exportOptionsPlist ios/ExportOptions.plist \
  -exportPath "$IPA_DIR" \
  -allowProvisioningUpdates

IPA_PATH=$(find "$IPA_DIR" -name "*.ipa" -type f | head -n 1)
[ -f "$IPA_PATH" ] || { echo "❌ IPA not found in $IPA_DIR"; exit 1; }

# 3) Release notes
RELEASE_NOTES=$(git log -10 --pretty=format:"- %s" 2>/dev/null || echo "- $(date -u +%Y-%m-%dT%H:%M:%SZ) $ENV_ARG build")

# 4) Upload
echo "🚀 [ios] Uploading to Firebase App Distribution → groups: $GROUPS"
npx firebase-tools@13 appdistribution:distribute "$IPA_PATH" \
  --app "$FIREBASE_IOS_APP_ID" \
  --groups "$GROUPS" \
  --release-notes "$RELEASE_NOTES"

echo "✅ [ios] Uploaded $IPA_PATH"
```

### Step 8 — Combined script

Create `dzzlo_oms_app/scripts/distribute.sh`:

```bash
#!/bin/bash
set -e

# Usage: ./scripts/distribute.sh [development|testing|production] [android|ios|both]
ENV_ARG="${1:-testing}"
TARGET="${2:-both}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

case "$TARGET" in
  android) bash "$SCRIPT_DIR/distribute-android.sh" "$ENV_ARG" ;;
  ios)     bash "$SCRIPT_DIR/distribute-ios.sh"     "$ENV_ARG" ;;
  both)
    bash "$SCRIPT_DIR/distribute-android.sh" "$ENV_ARG"
    bash "$SCRIPT_DIR/distribute-ios.sh"     "$ENV_ARG"
    ;;
  *) echo "❌ Invalid target: $TARGET (android|ios|both)"; exit 1 ;;
esac

echo "🎉 Distribution complete → env=$ENV_ARG target=$TARGET"
```

Make all three executable:

```bash
chmod +x dzzlo_oms_app/scripts/distribute.sh \
         dzzlo_oms_app/scripts/distribute-android.sh \
         dzzlo_oms_app/scripts/distribute-ios.sh
```

### Step 9 — Wire up yarn scripts

Add to `dzzlo_oms_app/package.json`:

```json
{
  "scripts": {
    "distribute":          "bash scripts/distribute.sh testing both",
    "distribute:android":  "bash scripts/distribute.sh testing android",
    "distribute:ios":      "bash scripts/distribute.sh testing ios",
    "distribute:prod":     "bash scripts/distribute.sh production both",
    "distribute:dev":      "bash scripts/distribute.sh development both"
  }
}
```

### Step 10 — Smoke test

```bash
# one-time setup
firebase login
echo "FIREBASE_ANDROID_APP_ID=..." >> dzzlo_oms_app/.env.distribution
# ... fill the rest

# kick it off
cd dzzlo_oms_app
yarn distribute:android    # validate Android path first (faster)
yarn distribute:ios        # then iOS
yarn distribute            # full pipeline
```

Verify:

1. Firebase Console → App Distribution → **Releases** shows the new build under each app
2. Tester in `qa` group receives an email invite (first time only)
3. Install the App Distribution tester app on device → the new release is listed

---

## Files to Create / Modify

| File                                                    | Change                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------ |
| `dzzlo_oms_app/.env.distribution`                       | **New** — Firebase app IDs, tester groups, signing config (gitignored) |
| `dzzlo_oms_app/.gitignore`                              | Add `.env.distribution`                                      |
| `dzzlo_oms_app/ios/ExportOptions.plist`                 | **New** — xcodebuild export config (ad-hoc signing)          |
| `dzzlo_oms_app/scripts/distribute.sh`                   | **New** — combined entry point                               |
| `dzzlo_oms_app/scripts/distribute-android.sh`           | **New** — build APK + upload                                 |
| `dzzlo_oms_app/scripts/distribute-ios.sh`               | **New** — archive + export IPA + upload                      |
| `dzzlo_oms_app/package.json`                            | Add `distribute*` yarn scripts                               |

No app-side code changes required. App Distribution is a **delivery** concern, orthogonal to the SDK integration in `FIREBASE_INTEGRATION_PLAN.md`.

---

## Optional: In-App Updates SDK

Firebase provides `@react-native-firebase/app-distribution` so testers get an **in-app prompt** when a newer release is available. Add later if needed:

```bash
yarn add @react-native-firebase/app-distribution
```

```js
import appDistribution from "@react-native-firebase/app-distribution";

// In dev/beta builds only
if (__DEV__ || APP_ENV !== "production") {
  const release = await appDistribution().checkForUpdate();
  if (release) await appDistribution().showUpdateDialog(release);
}
```

> Strip this module from production App Store builds — Apple rejects builds that contain the App Distribution SDK.

---

## Optional: CI/CD (GitHub Actions)

Once the local scripts work, the same scripts run on CI with two env vars instead of `.env.distribution`:

```yaml
# .github/workflows/distribute.yml (sketch)
jobs:
  distribute-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - run: yarn install --frozen-lockfile
        working-directory: dzzlo_oms_app
      - run: bash scripts/distribute-android.sh testing
        working-directory: dzzlo_oms_app
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.FIREBASE_SA_PATH }}
          FIREBASE_ANDROID_APP_ID: ${{ secrets.FIREBASE_ANDROID_APP_ID }}
          FIREBASE_TESTER_GROUPS_TESTING: qa

  distribute-ios:
    runs-on: macos-14
    steps:
      # ... check out, install Ruby/CocoaPods, import signing cert & profile,
      # then: bash scripts/distribute-ios.sh testing
```

iOS CI requires importing a distribution cert + provisioning profile into the keychain (e.g. via `apple-actions/import-codesign-certs`) — out of scope for this plan.

---

## Troubleshooting

| Symptom                                                           | Fix                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `Error: HTTP Error: 403, The caller does not have permission`     | Service account lacks "Firebase App Distribution Admin" role — add it in GCP IAM    |
| `No matching provisioning profiles found`                         | Open Xcode, sign in to team, enable Automatic signing for Release, re-archive       |
| `App id 1:...:ios:... not found`                                  | Wrong `FIREBASE_IOS_APP_ID` — copy from Project Settings → iOS app → App ID          |
| Android APK uploads but testers don't get email                   | Tester already received an invite for another group; check App Distribution → Testers tab for status |
| iOS build succeeds but IPA upload fails with "invalid binary"     | `method` in `ExportOptions.plist` is `app-store` — must be `ad-hoc`/`development`/`enterprise` |
| `yarn reset` wipes too much                                       | Replace with `watchman watch-del-all` only, or skip reset on re-runs                 |

---

## Verification

1. `yarn distribute:android` completes, APK appears in Firebase Console → App Distribution → Android app → Releases
2. `yarn distribute:ios` completes, IPA appears under iOS app → Releases
3. A tester in the `qa` group installs the release via the App Distribution email link and launches it
4. Re-run `yarn distribute` — a **new** release (incremented version code / same or higher build number) appears without overwriting the previous one
5. Release notes on each release show the last 10 commit subjects

---

## Addendum — Android-only test release (no Play Store)

Quick path to push an Android **testing** build to App Distribution only — no iOS, no Play Store, no production.

### Can I upload the APK manually?

**Yes.** App Distribution accepts manual APK uploads with zero extra setup:

- Firebase Console → **App Distribution** → pick the Android app → **Releases** tab
- **Drag & drop** `android/app/build/outputs/apk/release/app-release.apk` onto the page (or click **Upload**)
- Pick tester groups (e.g. `qa`), add release notes, click **Distribute**
- Testers get an email invite / in-app notification

Requirements: the APK's `applicationId` must match the Android app registered in Firebase (`in.vsyst.dzzlooms`), and it must be **signed** (App Distribution rejects unsigned APKs — the existing `build-release-apk.sh` already handles signing via the release keystore).

Use manual upload when:

- You just want a one-off build for a specific tester
- CLI auth/service account isn't set up yet
- You want to sanity-check the flow before scripting

Use the script below for everything repeatable.

### Script: `distribute-android-test.sh`

Create `dzzlo_oms_app/scripts/distribute-android-test.sh` — a stripped-down Android-only / testing-only variant. No env argument, no iOS, no production group:

```bash
#!/bin/bash
set -e

# Android testing → Firebase App Distribution only. No Play Store.
# Usage: ./scripts/distribute-android-test.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

set -a; source .env.distribution; set +a

: "${FIREBASE_ANDROID_APP_ID:?FIREBASE_ANDROID_APP_ID missing in .env.distribution}"
GROUPS="${FIREBASE_TESTER_GROUPS_TESTING:-qa}"

export APP_ENV=testing
echo "🔧 Environment: testing (App Distribution only)"

# 1) Build signed release APK
bash ./build-release-apk.sh testing

APK_PATH="android/app/build/outputs/apk/release/app-release.apk"
[ -f "$APK_PATH" ] || { echo "❌ APK not found at $APK_PATH"; exit 1; }

# 2) Release notes from last 5 commits
RELEASE_NOTES=$(git log -5 --pretty=format:"- %s" 2>/dev/null || echo "- testing build $(date -u +%Y-%m-%dT%H:%M:%SZ)")

# 3) Upload to App Distribution
echo "🚀 Uploading $APK_PATH → App Distribution (groups: $GROUPS)"
npx firebase-tools@13 appdistribution:distribute "$APK_PATH" \
  --app "$FIREBASE_ANDROID_APP_ID" \
  --groups "$GROUPS" \
  --release-notes "$RELEASE_NOTES"

echo "✅ Test release uploaded to Firebase App Distribution."
echo "   Testers in group '$GROUPS' will get an email."
```

Make executable and wire into yarn:

```bash
chmod +x dzzlo_oms_app/scripts/distribute-android-test.sh
```

Add to `package.json`:

```json
{
  "scripts": {
    "distribute:android:test": "bash scripts/distribute-android-test.sh"
  }
}
```

Run:

```bash
yarn distribute:android:test
```

### Manual vs. scripted — quick comparison

| Flow                             | Pros                                         | Cons                                           |
| -------------------------------- | -------------------------------------------- | ---------------------------------------------- |
| **Manual console upload**        | No CLI/auth setup; good for one-offs         | Still have to build APK locally; no auto release notes; slow for repeat use |
| **`yarn distribute:android:test`** | One command; auto release notes; repeatable | Needs `firebase login` or service account once |

Both land in the same place in the Firebase Console; testers can't tell the difference.
