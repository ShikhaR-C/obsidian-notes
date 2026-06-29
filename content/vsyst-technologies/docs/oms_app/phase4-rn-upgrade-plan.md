# Phase 4: React Native 0.81.0 → 0.84.1 Upgrade Plan

**Created:** 2026-04-07
**Branch:** `chores/update-packages`
**Prerequisite:** Phases 1-3 completed

**Status:** Plan ready for execution. Requires Node.js upgrade first.

---

## Step 0: Upgrade Node.js to Latest LTS

**RN 0.84.1 requires Node >= 22.11.0. Current system Node is v22.2.0.**

### Option A: Homebrew (current setup)
```bash
brew update
brew upgrade node
node --version   # verify >= 22.11.0
```

### Option B: nvm (if you use nvm)
```bash
nvm install --lts
nvm use --lts
node --version
```

### Option C: fnm
```bash
fnm install --lts
fnm use lts-latest
node --version
```

After upgrading, update the Xcode Node path:
```bash
# Find new Node binary path
which node
# Update ios/.xcode.env.local with the new path
```

---

## Step 1: Update package.json (7 packages + engines)

### Production dependencies:
```bash
yarn add react@19.2.4 react-native@0.84.1
```

### Dev dependencies:
```bash
yarn add -D \
  @react-native/babel-preset@0.84.1 \
  @react-native/eslint-config@0.84.1 \
  @react-native/metro-config@0.84.1 \
  @react-native/typescript-config@0.84.1 \
  react-test-renderer@19.2.4
```

### Update engines field in package.json:
```json
"engines": {
  "node": ">= 22.11.0"
}
```

---

## Step 2: Rewrite MainApplication.kt (MAJOR CHANGE)

**File:** `android/app/src/main/java/in/vsyst/dzzlooms/MainApplication.kt`

RN 0.84 removes the `ReactNativeHost`/`DefaultReactNativeHost` pattern entirely. The new pattern uses `reactHost by lazy` with direct `packageList` parameter.

### Current (0.81.0):
```kotlin
package `in`.vsyst.dzzlooms

import android.app.Application
import com.facebook.react.PackageList
import com.facebook.react.ReactApplication
import com.facebook.react.ReactHost
import com.facebook.react.ReactNativeApplicationEntryPoint.loadReactNative
import com.facebook.react.ReactNativeHost
import com.facebook.react.ReactPackage
import com.facebook.react.defaults.DefaultReactHost.getDefaultReactHost
import com.facebook.react.defaults.DefaultReactNativeHost

class MainApplication : Application(), ReactApplication {

  override val reactNativeHost: ReactNativeHost =
      object : DefaultReactNativeHost(this) {
        override fun getPackages(): List<ReactPackage> =
            PackageList(this).packages.apply {
              // Packages that cannot be autolinked yet can be added manually here
            }
        override fun getJSMainModuleName(): String = "index"
        override fun getUseDeveloperSupport(): Boolean = BuildConfig.DEBUG
        override val isNewArchEnabled: Boolean = BuildConfig.IS_NEW_ARCHITECTURE_ENABLED
        override val isHermesEnabled: Boolean = BuildConfig.IS_HERMES_ENABLED
      }

  override val reactHost: ReactHost
    get() = getDefaultReactHost(applicationContext, reactNativeHost)

  override fun onCreate() {
    super.onCreate()
    loadReactNative(this)
  }
}
```

### New (0.84.1):
```kotlin
package `in`.vsyst.dzzlooms

import android.app.Application
import com.facebook.react.PackageList
import com.facebook.react.ReactApplication
import com.facebook.react.ReactHost
import com.facebook.react.ReactNativeApplicationEntryPoint.loadReactNative
import com.facebook.react.defaults.DefaultReactHost.getDefaultReactHost

class MainApplication : Application(), ReactApplication {

  override val reactHost: ReactHost by lazy {
    getDefaultReactHost(
      context = applicationContext,
      packageList =
        PackageList(this).packages.apply {
          // Packages that cannot be autolinked yet can be added manually here
        },
    )
  }

  override fun onCreate() {
    super.onCreate()
    loadReactNative(this)
  }
}
```

**What changed:**
- Removed imports: `ReactNativeHost`, `ReactPackage`, `DefaultReactNativeHost`
- Removed entire `reactNativeHost` property (the anonymous `DefaultReactNativeHost` object)
- Changed `reactHost` from `get()` custom getter to `by lazy` delegate
- `getDefaultReactHost()` now takes named `context` + `packageList` instead of `context` + `reactNativeHost`
- No more `BuildConfig` references needed

---

## Step 3: Update Gradle Version

**File:** `android/gradle/wrapper/gradle-wrapper.properties`

Change:
```
distributionUrl=https\://services.gradle.org/distributions/gradle-8.14.3-bin.zip
```
To:
```
distributionUrl=https\://services.gradle.org/distributions/gradle-9.0.0-bin.zip
```

---

## Step 4: Update AndroidManifest.xml

**File:** `android/app/src/main/AndroidManifest.xml`

Add `android:usesCleartextTraffic="${usesCleartextTraffic}"` to the `<application>` tag.

Change:
```xml
    <application
      android:name=".MainApplication"
      android:label="@string/app_name"
      android:icon="@mipmap/ic_launcher"
      android:roundIcon="@mipmap/ic_launcher_round"
      android:allowBackup="false"
      android:theme="@style/AppTheme"
      android:supportsRtl="true">
```
To:
```xml
    <application
      android:name=".MainApplication"
      android:label="@string/app_name"
      android:icon="@mipmap/ic_launcher"
      android:roundIcon="@mipmap/ic_launcher_round"
      android:allowBackup="false"
      android:theme="@style/AppTheme"
      android:usesCleartextTraffic="${usesCleartextTraffic}"
      android:supportsRtl="true">
```

---

## Step 5: Update iOS Node Binary Path

**File:** `ios/.xcode.env.local`

Change from:
```
export NODE_BINARY=/opt/homebrew/Cellar/node/22.2.0/bin/node
```
To the new Node path (run `which node` after upgrading):
```
export NODE_BINARY=/opt/homebrew/bin/node
```
(Exact path depends on how Node was upgraded)

---

## Step 6: Install & Rebuild

```bash
cd dzzlo_oms_app

# Install JS dependencies
yarn install

# Clean caches
yarn reset

# Rebuild iOS pods
cd ios && pod install && cd ..

# Clean Android build
cd android && ./gradlew clean && cd ..
```

---

## Files That Do NOT Need Changes

These files are **identical** between RN 0.81.0 and 0.84.1 (verified via [rn-diff-purge](https://github.com/react-native-community/rn-diff-purge)):
- `android/build.gradle`
- `android/gradle.properties`
- `android/settings.gradle`
- `android/app/build.gradle` (only comment changes, skipping)
- `android/app/src/main/java/.../MainActivity.kt`
- `ios/dzzlo_oms_app/AppDelegate.swift`
- `ios/Podfile` (only trivial comment removal, skipping)
- `metro.config.js`
- `babel.config.js`
- `tsconfig.json`
- `Gemfile`
- `app.json`
- `jest.config.js`
- `index.js`
- `.eslintrc.js`

---

## Package Compatibility

**All 45 dependencies are compatible with RN 0.84.1.** No additional upgrades needed beyond the 7 core packages.

| Package | Status |
|---------|--------|
| react-native-reanimated ^4.3.0 | Supports RN 0.81-0.85 |
| react-native-worklets ^0.8.1 | Supports RN 0.81-0.85 |
| react-native-gesture-handler ^2.31.0 | Compatible |
| react-native-screens ^4.24.0 | Compatible |
| @gorhom/bottom-sheet ^5.2.8 | Compatible |
| react-native-paper ^5.15.0 | Compatible |
| react-native-svg ^15.15.4 | Compatible |
| All @react-navigation/* | Compatible |
| react-native-onesignal ^5.4.1 | Requires RN >=0.76 |
| @react-native-community/cli 20.1.3 | Compatible |
| react-native-html-to-pdf ^0.12.0 | No declared peer deps, should work |
| react-native-device-info ^15.0.2 | Compatible |
| @react-native-async-storage/async-storage ^3.0.2 | Compatible |
| @react-native-community/datetimepicker ^9.1.0 | Compatible |
| @react-native-community/netinfo ^12.0.1 | Compatible |
| react-native-webview ^13.16.1 | Compatible |
| react-native-linear-gradient ^2.8.3 | Compatible |
| @reduxjs/toolkit ^2.11.2 | Pure JS, compatible |
| axios ^1.14.0 | Pure JS, compatible |
| react-redux ^9.2.0 | Compatible |
| moment ^2.30.1 | Pure JS, compatible |

---

## Verification Checklist

After all steps:
1. `yarn install` completes without errors
2. `npx tsc --noEmit` passes
3. `yarn test:test` passes
4. iOS: `yarn ios:test` — app launches in simulator
5. Android: `yarn android:test` — app launches in emulator
6. Navigation: drawer open/close, tab switching, stack push/pop
7. Animations: bottom sheet, reanimated transitions
8. Redux/API: login flow, data loading, state persistence
9. OneSignal: push notification receipt
10. PDF generation: invoice + TCS/TDS reports
11. WebView: invoice rendering, help screen
12. SVG icons render correctly
13. Paper components: buttons, text, modals, FAB, chips
