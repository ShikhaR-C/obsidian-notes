# Package Update Plan - DZZLO OMS App

**Created:** 2026-04-06
**Branch:** `chores/update-packages`
**Base:** React 19.1.0 / React Native 0.81.0

---

## Executive Summary

42 packages have updates available. 20 are safe patch/minor bumps. 8 are major version upgrades with breaking changes. The project's native configs (compileSdk 36, modern Kotlin, Babel/Metro setup) are already well-positioned for most upgrades. Two config files need changes: `.eslintrc.js` (convert to flat config for ESLint 10) and `ios/Podfile` (verify iOS 14+ target for netinfo v12).

---

## Impact Analysis


| Package                                          | Current | Latest  | Breaking? | Integration Depth       | Files Affected | Phase  |
| ------------------------------------------------ | ------- | ------- | --------- | ----------------------- | -------------- | ------ |
| **@gorhom/bottom-sheet**                         | 5.2.6   | 5.2.8   | No        | Heavy (65 files)        | 0              | 1      |
| **@react-navigation/bottom-tabs**                | 7.4.6   | 7.15.9  | No        | Critical (177 files)    | 0              | 1      |
| **@react-navigation/drawer**                     | 7.5.7   | 7.9.8   | No        | Critical                | 0              | 1      |
| **@react-navigation/elements**                   | 2.6.4   | 2.9.14  | No        | Critical                | 0              | 1      |
| **@react-navigation/native**                     | 7.1.17  | 7.2.2   | No        | Critical                | 0              | 1      |
| **@react-navigation/native-stack**               | 7.3.26  | 7.14.10 | No        | Critical                | 0              | 1      |
| **@react-navigation/stack**                      | 7.4.7   | 7.8.9   | No        | Critical                | 0              | 1      |
| **@reduxjs/toolkit**                             | 2.8.2   | 2.11.2  | No        | Critical (123 files)    | 0              | 1      |
| **axios**                                        | 1.11.0  | 1.14.0  | No        | Moderate (4 files)      | 0              | 1      |
| **react-native-gesture-handler**                 | 2.28.0  | 2.31.0  | No        | Low (3 files)           | 0              | 1      |
| **react-native-onesignal**                       | 5.2.13  | 5.4.1   | No        | Moderate (1 file)       | 0              | 1      |
| **react-native-paper**                           | 5.14.5  | 5.15.0  | No        | Critical (250+ files)   | 0              | 1      |
| **react-native-reanimated**                      | 4.1.5   | 4.3.0   | No        | Low-Mod (15 files)      | 0              | 1      |
| **react-native-safe-area-context**               | 5.6.1   | 5.7.0   | No        | Low (3 files)           | 0              | 1      |
| **react-native-screens**                         | 4.15.2  | 4.24.0  | No        | Low (peer dep)          | 0              | 1      |
| **react-native-svg**                             | 15.12.1 | 15.15.4 | No        | High (165 files)        | 0              | 1      |
| **react-native-webview**                         | 13.15.0 | 13.16.1 | No        | Low-Mod (10 files)      | 0              | 1      |
| **react-redux**                                  | 9.2.0   | 9.2.0   | --        | Critical                | 0              | --     |
| **moment**                                       | 2.30.1  | 2.30.1  | --        | Moderate                | 0              | --     |
| **react-native-linear-gradient**                 | 2.8.3   | 2.8.3   | --        | Low (7 files)           | 0              | --     |
| **@babel/core**                                  | 7.25.2  | 7.29.0  | No        | Dev                     | 0              | 1      |
| **@babel/preset-env**                            | 7.25.3  | 7.29.2  | No        | Dev                     | 0              | 1      |
| **@babel/runtime**                               | 7.25.0  | 7.29.2  | No        | Dev                     | 0              | 1      |
| **@types/react**                                 | 19.1.0  | 19.2.14 | No        | Dev                     | 0              | 1      |
| **@react-native-community/cli**                  | 20.0.0  | 20.1.3  | No        | Dev                     | 0              | 1      |
| **@react-native-community/cli-platform-android** | 20.0.0  | 20.1.3  | No        | Dev                     | 0              | 1      |
| **@react-native-community/cli-platform-ios**     | 20.0.0  | 20.1.3  | No        | Dev                     | 0              | 1      |
| **@react-native-community/netinfo**              | 11.4.1  | 12.0.1  | **YES**   | Moderate (4 files)      | 0-1            | 2      |
| **@react-native-community/datetimepicker**       | 8.4.4   | 9.1.0   | **YES**   | Moderate (17 files)     | 0              | 2      |
| **react-native-device-info**                     | 14.0.4  | 15.0.2  | **YES**   | Moderate (9 files)      | 0              | 2      |
| **react-native-worklets**                        | 0.6.1   | 0.8.1   | **YES**   | Low (babel plugin only) | 0              | 2      |
| **@react-native-async-storage/async-storage**    | 2.2.0   | 3.0.2   | **YES**   | High (10 files)         | 0              | 2      |
| **react-native-html-to-pdf**                     | 0.12.0  | 1.3.0   | No (API unchanged) | Low (4 files)    | 0              | ✅ DONE |
| **prettier**                                     | 2.8.8   | 3.8.1   | **YES**   | Dev                     | all (reformat) | 3      |
| **eslint**                                       | 8.19.0  | 9.39.4  | **YES**   | Dev                     | 1 config       | ✅ DONE |
| **@types/jest**                                  | 29.5.13 | 30.0.0  | **YES**   | Dev                     | 0              | 3      |
| **jest**                                         | 29.6.3  | 30.3.0  | **YES**   | Dev                     | 0-few          | 3      |
| **typescript**                                   | 5.8.3   | 6.0.2   | **YES**   | Dev                     | 0              | 3      |
| **react**                                        | 19.1.0  | 19.2.4  | Minor     | Critical                | 0              | 4      |
| **react-native**                                 | 0.81.0  | 0.84.1  | **YES**   | Critical                | many           | 4      |
| **@react-native/babel-preset**                   | 0.81.0  | 0.84.1  | **YES**   | Dev                     | 0              | 4      |
| **@react-native/eslint-config**                  | 0.81.0  | 0.84.1  | **YES**   | Dev                     | 0              | 4      |
| **@react-native/metro-config**                   | 0.81.0  | 0.84.1  | **YES**   | Dev                     | 0              | 4      |
| **@react-native/typescript-config**              | 0.81.0  | 0.84.1  | **YES**   | Dev                     | 0              | 4      |
| **react-test-renderer**                          | 19.1.0  | 19.2.4  | Minor     | Dev                     | 0              | 4      |


---

## Phase 1: Safe Patch & Minor Updates (No Breaking Changes)

**Risk:** Low
**Estimated effort:** 1-2 hours (including testing)
**Rollback:** `git revert` the update commit

### Packages

```
@gorhom/bottom-sheet              5.2.6  -> 5.2.8
@react-navigation/bottom-tabs     7.4.6  -> 7.15.9
@react-navigation/drawer          7.5.7  -> 7.9.8
@react-navigation/elements        2.6.4  -> 2.9.14
@react-navigation/native          7.1.17 -> 7.2.2
@react-navigation/native-stack    7.3.26 -> 7.14.10
@react-navigation/stack            7.4.7  -> 7.8.9
@reduxjs/toolkit                   2.8.2  -> 2.11.2
axios                              1.11.0 -> 1.14.0
react-native-gesture-handler      2.28.0 -> 2.31.0
react-native-onesignal            5.2.13 -> 5.4.1
react-native-paper                5.14.5 -> 5.15.0
react-native-reanimated            4.1.5  -> 4.3.0
react-native-safe-area-context     5.6.1  -> 5.7.0
react-native-screens              4.15.2 -> 4.24.0
react-native-svg                 15.12.1 -> 15.15.4
react-native-webview             13.15.0 -> 13.16.1
@babel/core                        7.25.2 -> 7.29.0
@babel/preset-env                  7.25.3 -> 7.29.2
@babel/runtime                     7.25.0 -> 7.29.2
@types/react                      19.1.0 -> 19.2.14
@react-native-community/cli       20.0.0 -> 20.1.3
@react-native-community/cli-*     20.0.0 -> 20.1.3
```

### Steps

1. **Create a checkpoint commit** on the current branch
2. **Update all Phase 1 packages at once:**
  ```bash
   yarn add @gorhom/bottom-sheet@^5.2.8 \
     @react-navigation/bottom-tabs@^7.15.9 \
     @react-navigation/drawer@^7.9.8 \
     @react-navigation/elements@^2.9.14 \
     @react-navigation/native@^7.2.2 \
     @react-navigation/native-stack@^7.14.10 \
     @react-navigation/stack@^7.8.9 \
     @reduxjs/toolkit@^2.11.2 \
     axios@^1.14.0 \
     react-native-gesture-handler@^2.31.0 \
     react-native-onesignal@^5.4.1 \
     react-native-paper@^5.15.0 \
     react-native-reanimated@^4.3.0 \
     react-native-safe-area-context@^5.7.0 \
     react-native-screens@^4.24.0 \
     react-native-svg@^15.15.4 \
     react-native-webview@^13.16.1
  ```
3. **Update dev dependencies:**
  ```bash
   yarn add -D @babel/core@^7.29.0 \
     @babel/preset-env@^7.29.2 \
     @babel/runtime@^7.29.2 \
     @types/react@^19.2.14 \
     @react-native-community/cli@20.1.3 \
     @react-native-community/cli-platform-android@20.1.3 \
     @react-native-community/cli-platform-ios@20.1.3
  ```
4. **Clean & rebuild:**
  ```bash
   yarn reset
   cd ios && pod install && cd ..
  ```
5. **Test**

### Testing Checklist

- App launches on iOS simulator
- App launches on Android emulator
- Navigation: drawer open/close, tab switching, stack push/pop
- Bottom sheets: open, dismiss, backdrop tap, back button (Android)
- Redux: login flow, API calls loading, state persistence
- Reanimated: drawer animations, tab transitions
- SVG icons render correctly across screens
- Paper components: buttons, text, modals, FAB, chips
- WebView: invoice rendering, help screen
- OneSignal: push notification received (if testable)
- Gesture handler: swipe drawer, scroll lists

---

## Phase 2: Moderate Major Updates (Manageable Breaking Changes)

**Risk:** Medium
**Estimated effort:** 3-4 hours
**Rollback:** `git revert` per-package commits

### 2A. @react-native-community/netinfo 11.4.1 -> 12.0.1

**Breaking change:** Requires iOS 14+ (uses `NEHotspotNetwork`).
**Impact:** ZERO code changes. RN 0.81 already targets iOS 15.1+.

**Steps:**

1. `yarn add @react-native-community/netinfo@^12.0.1`
2. `cd ios && pod install && cd ..`
3. Verify: Open the app with airplane mode on/off. Check `src/components/Network/index.js` and `src/components/NoNetwork/index.js` display correct status.

---

### 2B. @react-native-community/datetimepicker 8.4.4 -> 9.1.0

**Breaking change:** Removed `positiveButtonLabel`, `negativeButtonLabel`, `neutralButtonLabel` Android props.
**Impact:** ZERO code changes. Codebase does NOT use any of the removed props (verified by grep).

**Steps:**

1. `yarn add @react-native-community/datetimepicker@^9.1.0`
2. `cd ios && pod install && cd ..`
3. Verify: Test date pickers in `src/components/DatePicker/` on both platforms.

---

### 2C. react-native-device-info 14.0.4 -> 15.0.2

**Breaking change:** Requires Android compileSdk 34+.
**Impact:** ZERO code changes. Project already uses compileSdk 36.

**Steps:**

1. `yarn add react-native-device-info@^15.0.2`
2. `cd ios && pod install && cd ..`
3. Verify: Check `src/components/VersionInfo/index.js` displays correct app version. Check API headers in `src/store/apis/createApi.js` include device metadata.

---

### 2D. react-native-worklets 0.6.1 -> 0.8.1

**Breaking change:** New `Shareable` type, stricter TypeScript types for animated styles.
**Impact:** LOW. No direct source imports of worklets APIs — only used as Babel plugin (`react-native-worklets/plugin`). The stricter types may surface compile errors if animated styles are passed to non-animated components.

**Steps:**

1. `yarn add react-native-worklets@^0.8.1`
2. Update alongside reanimated (already done in Phase 1).
3. `yarn reset && cd ios && pod install && cd ..`
4. Verify: Test all animations — drawer open/close, tab transitions, bottom sheet animations, input label animations.

---

### 2E. @react-native-async-storage/async-storage 2.2.0 -> 3.0.2

**Breaking change:** Complete rewrite. Scoped storage instances. Callback API removed. multi methods renamed.
**Actual impact:** LOW. Codebase uses ONLY:

- `AsyncStorage.getItem(key)` — promise-based (compatible via v3 default singleton)
- `AsyncStorage.setItem(key, value)` — promise-based (compatible)
- `AsyncStorage.removeItem(key)` — promise-based (compatible)
- NO callbacks, NO multi methods.

The v3 default export provides a backward-compatible singleton for basic `getItem`/`setItem`/`removeItem`. This should be a near drop-in upgrade.

**Files using AsyncStorage (10):**

- `src/store/slices/auth.js`
- `src/store/apis/createApi.js`
- `src/store/apis/dzzlooms/auth.js`
- `src/utils/API/axiosReqRes.js`
- `src/utils/Auth/index.js`
- `src/screens/StartupScreen.js`
- `src/screens/Demo/Dashboard/index.js`
- `src/screens/Common/Settings/Codepush.js`
- `src/screens/Login/AuthNavigator/BetaUser.js`
- `src/components/VersionInfo/index.js`

**Steps:**

1. `yarn add @react-native-async-storage/async-storage@^3.0.2`
2. `cd ios && pod install && cd ..`
3. Verify import works: `import AsyncStorage from '@react-native-async-storage/async-storage'`
4. Test: Login flow (token persistence), app restart (auto-login), beta user toggle, logout.

---

### 2F. react-native-html-to-pdf 0.12.0 -> 1.3.0 — ✅ DONE

**Breaking change:** Major version jump — but JS API is unchanged (drop-in replacement).
**Status:** COMPLETED (2026-04-07)
**Impact:** ZERO code changes. All 4 files use `RNHTMLtoPDF.convert({ html, fileName, directory })` which is unchanged.

**What changed in v1.0.0–1.3.0 (all additive):**
- New Architecture (TurboModules/Fabric) support
- JavaScript enabled in Android WebView for PDF rendering
- Build tooling updates

**Files verified (no changes needed):**

- `src/components/Download/invoiceHTML/ShowInvoice.js`
- `src/components/Download/invoiceHTML/index.js`
- `src/components/Download/RNhtmlpdf.js`
- `src/screens/Common/Reports/TcsTds/Render/index.js`

**Steps completed:**

1. ✅ Checked v1.3.0 changelog — API unchanged, import unchanged, return value unchanged.
2. ✅ `yarn add react-native-html-to-pdf@^1.3.0`
3. Pending: `cd ios && pod install && cd ..` (native rebuild)
4. Pending: Verify PDF generation from invoice and TCS/TDS report.

---

### Phase 2 Testing Checklist

- Network status indicator works (airplane mode toggle)
- Date pickers work on iOS and Android
- Device info displays in Settings screen
- All animations smooth (drawers, tabs, bottom sheets, inputs)
- Login/logout flow with token persistence
- Auto-login on app restart
- Beta user toggle persists across restart
- Invoice PDF generation and download
- TCS/TDS report PDF generation

---

## Phase 3: Significant Dev Tooling Updates (Dedicated Migration)

**Risk:** Medium-High
**Estimated effort:** 4-8 hours
**Rollback:** `git revert` per-tool commits

### 3A. Prettier 2.8.8 -> 3.8.1

**Breaking change:** `trailingComma` default changes from `"es5"` to `"all"`.
**Impact:** COSMETIC ONLY. Project already uses `trailingComma: 'all'` in `.prettierrc.js`. No behavioral change.

**Steps:**

1. `yarn add -D prettier@^3.8.1`
2. Run `npx prettier --write .` to reformat entire codebase
3. Commit the formatting changes separately (will be a large diff but cosmetic-only)
4. Verify: `yarn lint` passes

---

### 3B. ESLint 8.19.0 -> 9.39.4 — ✅ DONE

**Breaking change:** Legacy `.eslintrc.*` deprecated. Must use flat config `eslint.config.js`.
**Status:** COMPLETED (2026-04-07)

**Previous blockers (now resolved):**

1. ~~**Node version:** ESLint 10 requires `^20.19.0 || ^22.13.0 || >=24`, but project was on Node 22.2.0.~~ → Now on Node v24.14.1.
2. ~~**Config format:** `@react-native/eslint-config@0.81.0` only exports legacy format.~~ → v0.84.1 ships `flat.js`.

**What was done:**

1. Upgraded `eslint` from `^8.19.0` to `^9.0.0` (resolved to 9.39.4).
2. Deleted `.eslintrc.js` (legacy config).
3. Created `eslint.config.js` (flat config) using `@react-native/eslint-config/flat`.
4. Disabled `ft-flow/define-flow-type` and `ft-flow/use-flow-type` rules — project does not use Flow, and `eslint-plugin-ft-flow@2.x` uses the removed `context.getAllComments` API incompatible with ESLint 9.
5. Verified: `npx eslint src/` runs successfully. Error/warning counts unchanged from ESLint 8 (all pre-existing).

**Why ESLint 9, not 10:** `@react-native/eslint-config@0.84.1` peer dependency is `eslint: "^8.0.0 || ^9.0.0"` — does not include ESLint 10. Revisit when RN config adds ESLint 10 support.

---

### 3C. TypeScript 5.8.3 -> 6.0.2

**Breaking change:** `moduleResolution: classic` removed, strict mode enforced, es3/es5 targets deprecated.
**Impact:** ZERO code changes. Project uses `@react-native/typescript-config` which handles all settings. No deprecated options detected in `tsconfig.json`.

**Steps:**

1. `yarn add -D typescript@^6.0.2`
2. Run `npx tsc --noEmit` to verify no type errors
3. Fix any new strict-mode violations if surfaced

---

### 3D. Jest 29.6.3 -> 30.3.0

**Breaking change:** jsdom upgrade, deprecated matcher aliases removed, `--testPathPattern` renamed.
**Impact:** LOW. Config uses `preset: 'react-native'` which handles compatibility. No custom matchers or flags detected.

**Steps:**

1. `yarn add -D jest@^30.3.0 @types/jest@^30.0.0`
2. Run `yarn test:test`
3. Fix any deprecated matcher aliases if tests fail (e.g., `.toBeCalled()` -> `.toHaveBeenCalled()`)

---

### Phase 3 Testing Checklist

- ✅ `npx eslint src/` passes with ESLint 9.39.4 + flat config (349 errors, 5423 warnings — all pre-existing)
- `npx tsc --noEmit` passes with new TypeScript
- `yarn test:test` passes with new Jest
- `npx prettier --check .` passes
- App builds successfully on both platforms after tooling changes

---

## Phase 4: React & React Native Core Upgrade (Long-Term)

**Risk:** High
**Estimated effort:** 1-3 days
**Note:** This is a separate initiative. Do NOT bundle with Phase 1-3.

### Packages

```
react                  19.1.0 -> 19.2.4
react-native            0.81.0 -> 0.84.1
react-test-renderer    19.1.0 -> 19.2.4
@react-native/babel-preset        0.81.0 -> 0.84.1
@react-native/eslint-config       0.81.0 -> 0.84.1
@react-native/metro-config        0.81.0 -> 0.84.1
@react-native/typescript-config   0.81.0 -> 0.84.1
```

### Why Separate

- RN 0.81 -> 0.84 spans 3 minor releases, each with potential native breaking changes
- Requires regenerating native projects or careful manual patching
- All other packages should be stable on current versions before attempting this
- React Navigation, Paper, Reanimated, etc. need to confirm 0.84 support

### Steps (High-Level)

1. Use command `npx react-native upgrade`
2. Use the [React Native Upgrade Helper](https://react-native-community.github.io/upgrade-helper/?from=0.81.0&to=0.84.1) to diff native changes
3. refer [https://react-native-community.github.io/upgrade-helper/?from=0.81.0&to=0.84.1](https://react-native-community.github.io/upgrade-helper/?from=0.81.0&to=0.84.1)
4. Apply changes to `android/` and `ios/` directories
5. Update all `@react-native/*` dev packages to 0.84.1
6. Update `react` and `react-test-renderer` to 19.2.4
7. Full clean rebuild: `yarn reset && cd ios && pod install && cd ..`
8. Test entire app thoroughly

---

## Cross-Cutting Concerns

### After Every Phase

1. **Clean metro cache:** `yarn reset`
2. **Reinstall iOS pods:** `cd ios && pod install && cd ..`
3. **Clean Android build:** `cd android && ./gradlew clean && cd ..`
4. **Test on BOTH platforms** (iOS simulator + Android emulator)
5. **Commit each phase separately** for easy rollback

### Native Rebuild Triggers

These packages require native rebuilds (pod install + gradle sync):

- async-storage, datetimepicker, netinfo, device-info, html-to-pdf, worklets, onesignal, gesture-handler, reanimated, screens, safe-area-context, svg, webview

### Stale / Consider Replacement (Future)


| Package                      | Issue                    | Alternative                         |
| ---------------------------- | ------------------------ | ----------------------------------- |
| moment                       | Maintenance mode, 300KB+ | dayjs (2KB) or date-fns             |
| react-native-linear-gradient | No updates in 3+ years   | expo-linear-gradient or RN built-in |


---

## Risk Matrix


| Risk                                          | Likelihood               | Impact | Mitigation                                                                                                                                         |
| --------------------------------------------- | ------------------------ | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Paper animations broken on RN 0.81+           | Medium                   | High   | Test thoroughly; check GitHub #4797                                                                                                                |
| async-storage v3 data migration               | Low                      | High   | v3 default singleton is backward-compatible for basic API                                                                                          |
| html-to-pdf API changed                       | ~~Medium~~ **Resolved**  | Low    | ✅ API unchanged in v1.3.0 — drop-in replacement. Only native rebuild needed.                                                                       |
| ESLint flat config not supported by RN config | ~~Medium~~ **Resolved** | Medium | ✅ Upgraded to ESLint 9.39.4 with flat config. `eslint-plugin-ft-flow` incompatibility mitigated by disabling unused Flow rules. ESLint 10 deferred until peer dep support added. |
| Worklets type errors                          | Low                      | Low    | Only babel plugin usage; no direct API calls                                                                                                       |
| Jest 30 test breakage                         | Low                      | Medium | Run codemod; fix matcher aliases                                                                                                                   |


---

## Recommended Execution Order

```
Phase 1 (safe updates)     --> commit --> test --> merge
Phase 2A-2D (easy majors)  --> commit --> test --> merge
Phase 2E (async-storage)   --> commit --> test --> merge
Phase 2F (html-to-pdf)     --> ✅ DONE (1.3.0 installed, drop-in replacement, 2026-04-07)
Phase 3A (prettier)        --> commit (formatting) --> merge
Phase 3B (eslint)          --> ✅ DONE (ESLint 9.39.4 + flat config, 2026-04-07)
Phase 3C (typescript)      --> commit --> test --> merge
Phase 3D (jest)            --> commit --> test --> merge
Phase 4 (RN upgrade)       --> separate branch --> full QA --> merge
```

