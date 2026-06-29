# Current State Audit

All numbers are from exhaustive `grep` / `glob` passes over the codebase at the chores/update-packages branch, April 2026.

## 1. Theming infrastructure

### Files

- `src/utils/Colors/index.js` (297 lines) — exports `Light`, `Dark`, `hex2rgba()`, `hex_alpha()`. Contains a `fontObject` with all 15 MD3 type variants, but with **bug**: `letterSpacing: 0` on variants that should have tracking (per MD3 spec: titleMedium=0.15, bodyMedium=0.25, labelSmall=0.5, etc.).
- `src/utils/Colors/defaultCombined.js` (87 lines) — exports `lightDefaultCombined`, `darkDefaultCombined`. **Dead code**: zero importers. Legacy backup.

### Provider wiring

- `App.js` is 31 lines, no Paper provider. Composition: `GestureHandlerRootView > SafeAreaProvider > Provider (redux) > AppNavigatorContainer`.
- `src/navigation/AppNavigatorContainer.js:83` — `<PaperProvider theme={theme}>` is here, not at app root.
- `src/navigation/AppNavigatorContainer.js:43-49` — theme selection:
  ```js
  const themeState = userDetails ? userDetails.theme : "SYSTEM";
  const isDarkTheme =
    themeState === "SYSTEM" ? colorScheme === "dark" : themeState === "DARK";
  const theme = isDarkTheme ? Dark : Light;
  ```
- `src/components/Error/RestartContext.js` — wraps `<NavigationContainer theme={theme}>`. Passes the **Paper** theme directly to React Navigation's container. This works by coincidence (shape overlap); Phase 1 formalizes it with `adaptNavigationTheme()`.
- `src/navigation/AppNavigatorContainer.js:86-88` — `<StatusBar barStyle={isDarkTheme ? 'light-content' : 'dark-content'} />`. Theme-aware but no `backgroundColor`.

### Theme switching UX

- `src/screens/Common/Settings/index.js` — settings screen with 3 options: `SYSTEM / DARK / LIGHT`. Calls `useSet_themeMutation` to persist to backend `user.theme`.
- `src/components/VersionInfo/index.js` — exposes a second toggle via a switch (duplicate entry point).
- **Persistence gap**: theme is backend-only. On logout / fresh install, user flashes the wrong theme until the user object loads. No AsyncStorage fallback.

### Dependency baseline (from `package.json`)

```
react-native                                 0.84.1
react-native-paper                           5.15.0
@react-navigation/native                     7.2.2
@react-navigation/bottom-tabs                7.15.9
@react-navigation/drawer                     7.9.8
@react-navigation/native-stack               7.14.10
react-native-safe-area-context               5.7.0
react-native-gesture-handler                 2.31.0
react-native-reanimated                      4.3.0
react-native-svg                             15.15.4
@react-native-async-storage/async-storage    3.0.2
react-redux                                  9.2.0
@reduxjs/toolkit                             2.11.2
```

**Not installed**: `@shopify/restyle`, `react-native-unistyles`, `tamagui`, `nativewind`, `dripsy`, `react-native-size-matters`, `@material/material-color-utilities`.

### Fonts in native bundles

- `react-native.config.js` declares `assets: ['./src/assets/fonts/']`.
- Font files present: `OpenSans_Regular.ttf`, `RCL_Light.ttf`, `RobotoCondensed_Regular.ttf` (located in `src/assets/fonts/`, `android/app/src/main/assets/fonts/`, and iOS bundle).
- **None are used** — `src/utils/Colors/index.js` `fontObject` has `fontFamily: 'System'` everywhere.

## 2. Text rendering audit

### Topline numbers

- `<Text>` instances: **2,435+** across **181 files**
- Hardcoded `fontSize` values: **547**
- Hardcoded `fontWeight` values: **291**
- `variant` prop usage on Paper `<Text>`: **0** (no file uses MD3 variants today)
- `allowFontScaling` usage: **0**
- `maxFontSizeMultiplier` usage: **0**
- `StyleSheet.create` blocks: **177 files** (133 in `src/screens/`, rest in components)
- Custom text wrappers (`AppText` / `ThemedText` / etc.): **0** (`src/constants/designTokens.js` has unused `FONT_SIZES`)

### Text-density hotspots (top 15, these are Phase 5 priorities)

| Priority | File                                                       | Text count |
| -------- | ---------------------------------------------------------- | ---------- |
| 1        | `src/screens/Customer/Dealers/DealerSettings/index.js`     | 69         |
| 2        | `src/screens/Common/Reports/DailyReport/components.js`     | 62         |
| 3        | `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js`   | 55         |
| 4        | `src/screens/Dealer/Customers/CustSettings.js`             | 55         |
| 5        | `src/screens/Dealer/NewInvoice/newComp/SummaryModal.js`    | 53         |
| 6        | `src/screens/Common/Orders/components/newDesign.js`        | 52         |
| 7        | `src/screens/Common/_Voucher_/BS/index.js`                 | 42         |
| 8        | `src/screens/Dealer/Orders/components/OTPmodule.js`        | 41         |
| 9        | `src/screens/Customer/NewOrder/components.js`              | 41         |
| 10       | `src/screens/Common/DailySummary/component/index.js`       | 36         |
| 11       | `src/screens/Customer/Orders/components/EmergencyOTPBS.js` | 32         |
| 12       | `src/screens/Common/Payments/components/index.js`          | 29         |
| 13       | `src/screens/Customer/NewPayment/index.js`                 | 27         |
| 14       | `src/screens/Common/RelationList/RelationCreditBS.js`      | 27         |
| 15       | `src/screens/Common/Accounts/components.js`                | 27         |

### Fixed-height containers (Phase 4 fix list — 48+ instances, partial)

These will **clip text** on Android when system font scale is raised:

| File                                                 | Line | Height | Context                            |
| ---------------------------------------------------- | ---- | ------ | ---------------------------------- |
| `src/screens/Customer/Payments/index.js`             | 498  | 40     | Pill with border radius 10         |
| `src/screens/Customer/Dealers/BSheets/AddDealer.js`  | 405  | 40     | —                                  |
| `src/screens/Login/AuthNavigator/Login.js`           | 810  | 40     | —                                  |
| `src/screens/Common/Profile/SelectStateBS.js`        | 518  | 40     | Scrollable list item               |
| `src/screens/Dealer/Orders/components/OneOrder.js`   | 382  | 50     | `const hght = { height: 50 }`      |
| `src/screens/Common/Orders/bottomsheet/dateRange.js` | 416  | 60     | —                                  |
| `src/components/DatePicker/index.js`                 | 920  | 60     | iOS picker height hardcoded        |
| `src/components/Input/CustomInput.js`                | 468  | 56     | Input container with label overlap |
| `src/components/Input/IconInput.js`                  | 44   | 48     | —                                  |
| `src/components/Input/BS/BSheetInput.js`             | 42   | 48     | —                                  |
| `src/components/Input/IconLabelInput.js`             | 42   | 48     | —                                  |

Phase 4 runs a grep for `height: [0-9]` across `src/screens/` and `src/components/` and migrates each to `minHeight:` with `justifyContent: 'center'` or vertical padding.

## 3. Color usage audit

### How colors are consumed

| Pattern                                                   | Files                          | Status                            |
| --------------------------------------------------------- | ------------------------------ | --------------------------------- |
| `useTheme()` from react-native-paper                      | **348 files**                  | Dominant, strong baseline         |
| Direct import of `Light` / `Dark` from `src/utils/Colors` | **86 files**                   | Needs shim during migration       |
| Hardcoded hex in StyleSheet                               | **227 files (screens)**        | **Target for Phase 3 removal**    |
| Hardcoded rgba/rgb strings                                | **~1,260 component instances** | Heavily concentrated in SVG icons |
| Inline color props on native components                   | **31 instances**               |                                   |
| Color name literals (`'white'`, `'red'`)                  | **16 instances**               |                                   |

### Hardcoded-color hotspots (top 20, Phase 3 priority)

| File                                                           | Approx count |
| -------------------------------------------------------------- | ------------ |
| `src/components/Prompt/index.js`                               | 9            |
| `src/screens/Customer/NewOrder/components.js`                  | 7            |
| `src/screens/Common/Orders/components/FilterList.js`           | 7            |
| `src/screens/Dealer/Payments/BSheets/AttachInvs.js`            | 6            |
| `src/screens/Dealer/Orders/index.js`                           | 6            |
| `src/screens/Customer/Orders/index.js`                         | 6            |
| `src/screens/Common/Orders/index.js`                           | 6            |
| `src/screens/Common/Orders/bottomsheet/filter.js`              | 6            |
| `src/components/Input/IconInput.js`                            | 6            |
| `src/screens/Dealer/ProductDates/SetProductRate.js`            | 5            |
| `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js`       | 5            |
| `src/screens/Customer/Vehicles/vehicleComponents/index.js`     | 5            |
| `src/screens/Customer/NewPayment/index.js`                     | 5            |
| `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js` | 5            |
| `src/screens/Common/Reports/DailyReport/components.js`         | 5            |
| `src/screens/Common/Payments/components/index.js`              | 5            |
| `src/screens/Common/Orders/components/newDesign.js`            | 5            |
| `src/components/NumberMeter/logic.js`                          | 5            |
| `src/components/NumberMeter/index.js`                          | 5            |
| `src/screens/Login/AuthNavigator/Welcome.js`                   | 4            |

### Non-standard semantic colors in current theme

Beyond MD3 basics, the existing `Light`/`Dark` objects add these custom keys:

| Key                  | Light value             | Dark value              | Notes                                                                  |
| -------------------- | ----------------------- | ----------------------- | ---------------------------------------------------------------------- |
| `white`              | `rgba(255,255,255,0.7)` | `rgba(255,255,255,0.7)` | **Same in both** — semantically an overlay, poorly named               |
| `black`              | `rgba(0,0,0,0.7)`       | `rgba(0,0,0,0.7)`       | Same issue                                                             |
| `gray`               | `#BDBDBD`               | `#424242`               |                                                                        |
| `antiText`           | `rgb(229,229,231)`      | `rgb(28,28,30)`         | Inverse text color (dark text in light, light text in dark) — misnamed |
| `link`               | `#0000EE`               | `#3478F1`               | Hyperlink blue                                                         |
| `success`            | `#6ebf33`               | `#6ebf33`               | **Same in both** — status color                                        |
| `elevation.level0-5` | Various                 | Various                 | MD3 elevation system                                                   |

Phase 3 remaps all of these to semantic MD3 roles:

- `white`/`black` → move to `surfaceTint` + `scrim`
- `gray` → split into `outline` + `outlineVariant` + `surfaceVariant`
- `antiText` → use `inverseOnSurface`
- `link` → new semantic role `colors.link` (custom extension)
- `success` → move to `fixed.success` (theme-invariant) + add `warning` / `info` siblings

### Brand / fixed colors

SVG brand logos in `src/components/SVG/psoc/` (IOCL, NAYARA, HPCL, BPCL, SHELL, JIO_BP) have 30–50 hardcoded hex values each. These are **intentionally theme-invariant** — moving them to `src/theme/tokens/fixed.js` as explicit brand tokens makes this intent clear.

## 4. Known accessibility gaps

Spotted during the audit (not exhaustive — Phase 6 will do the full WCAG pass):

| File                                                | Line         | Issue                                                                                                                  |
| --------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `src/screens/Dealer/Customers/CustSettings.js`      | 91           | `color: colors.placeholder` on dark surface — placeholder is `rgba(255,255,255,0.54)`, fails WCAG AA against `#121212` |
| `src/screens/Dealer/Customers/SetDiscBS.js`         | 359, 389     | Same placeholder contrast issue in bottom sheet inputs                                                                 |
| `src/components/Prompt/index.js`                    | 98           | `subHeaderTextColor` defaults to `colors.text` but may be overridden to an unverified value                            |
| `src/screens/Dealer/ProductDates/SetProductRate.js` | ~5 locations | Heavy use of `colors.disabled` as background AND text color — likely imperceptible                                     |

## 5. Gaps summary

| Gap                                                      | Severity     | Phase                                 |
| -------------------------------------------------------- | ------------ | ------------------------------------- |
| No `<AppText>` wrapper → variants can't be enforced      | **Critical** | Phase 2                               |
| 48+ fixed-height containers                              | **Critical** | Phase 4                               |
| `allowFontScaling` never set → uncapped scaling untested | **Critical** | Phase 2                               |
| 547 hardcoded `fontSize` + 291 `fontWeight`              | High         | Phase 5 (alongside Phase 2 migration) |
| 1,500+ hardcoded colors                                  | High         | Phase 3                               |
| Theme not extensible beyond 2 (hardcoded Light/Dark)     | High         | Phase 1                               |
| `defaultCombined.js` dead code                           | Low          | Phase 1 (delete)                      |
| Navigation theme relies on shape overlap                 | Medium       | Phase 1 (use `adaptNavigationTheme`)  |
| No local theme persistence (flash on fresh install)      | Medium       | Phase 6                               |
| Custom fonts declared but unused                         | Low          | Phase 6                               |
| `letterSpacing: 0` bug in current `fontObject`           | Medium       | Phase 2                               |
| No contrast automation                                   | Medium       | Phase 6                               |
| Two theme-toggle entry points (Settings + VersionInfo)   | Low          | Phase 6 consolidation                 |
