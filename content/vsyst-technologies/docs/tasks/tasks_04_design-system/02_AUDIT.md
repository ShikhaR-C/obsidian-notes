# Current State Audit

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). An April 2026 snapshot of v1, kept as history; every section now carries a 2026-10-01 re-count. D11 leaves v1 as it is, so its numbers barely moved, and the new system (`src/theme/`, `src/components/v2/`) sits beside it with none of these literals. Three claims are corrected in place: custom fonts are used, the `letterSpacing` bug was not there, and `white` is opaque since 2026-05-01. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos
>
> Re-count method (2026-10-01): regex counts over non-test `.js` files in `src/screens`, `src/components` and `src/navigation` at app `ea7e7222`, with the v2 folders and `src/components/SVG/` counted apart. The method differs from April's, so compare orders of magnitude, not single numbers.

All numbers are from exhaustive `grep` / `glob` passes over the codebase at the chores/update-packages branch, April 2026.

## 1. Theming infrastructure

**Status (2026-10-01):** the legacy setup is unchanged and still drives v1. Beside it, `src/theme/` (tokens, two themes, the Paper and navigation adapters, `ThemeProvider` / `useAppTheme`) hands Paper a byte-identical theme (`src/theme/__tests__/parity.test.js`) and v2 its tokens.

### Files

**Status (2026-10-01):** both files still exist; `src/utils/Colors/index.js` is now 299 lines and gained `withAlpha` (`0c28903a`, 2026-05-01); `defaultCombined.js` still has 0 importers. The `letterSpacing` claim is corrected below.

- `src/utils/Colors/index.js` (297 lines) — exports `Light`, `Dark`, `hex2rgba()`, `hex_alpha()`. Contains a `fontObject` with all 15 MD3 type variants~~, but with **bug**: `letterSpacing: 0` on variants that should have tracking (per MD3 spec: titleMedium=0.15, bodyMedium=0.25, labelSmall=0.5, etc.)~~ — _2026-10-01:_ those roles carry exactly that tracking (`src/utils/Colors/index.js:55,69,97`), unchanged since at least 2025-09-09.
- `src/utils/Colors/defaultCombined.js` (87 lines) — exports `lightDefaultCombined`, `darkDefaultCombined`. **Dead code**: zero importers. Legacy backup.

### Provider wiring

**Status (2026-10-01):** line numbers moved — theme selection `AppNavigatorContainer.js:73-78`, `PaperProvider` `:178`, StatusBar `:182-184`; `ThemeProvider` now wraps `PaperProvider` (`:177`). `RestartContext` still hands the Paper theme to `NavigationContainer` (`RestartContext.js:52`), so Phase 1 Step 1.19 is open.

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

**Status (2026-10-01):** unchanged — Settings offers SYSTEM / DARK / LIGHT (`src/screens/Common/Settings/index.js:26`), `VersionInfo` keeps its theme modal (`src/components/VersionInfo/index.js:87-98,381-385`), and the theme is still server-only.

- `src/screens/Common/Settings/index.js` — settings screen with 3 options: `SYSTEM / DARK / LIGHT`. Calls `useSet_themeMutation` to persist to backend `user.theme`.
- `src/components/VersionInfo/index.js` — exposes a second toggle via a switch (duplicate entry point).
- **Persistence gap**: theme is backend-only. On logout / fresh install, user flashes the wrong theme until the user object loads. No AsyncStorage fallback.

### Dependency baseline (from `package.json`)

**Status (2026-10-01):** the listed versions are unchanged. Still not installed: all seven libraries below, `@shopify/restyle` now by decision (2026-09-04); `redux-persist` is not a dependency either; `@react-native-firebase/remote-config` was removed in 1.79.

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

**Status (2026-10-01):** the three files are still bundled (`react-native.config.js`, `ios/dzzlo_oms_app/Info.plist:59-61`); the "none are used" line is corrected below.

- `react-native.config.js` declares `assets: ['./src/assets/fonts/']`.
- Font files present: `OpenSans_Regular.ttf`, `RCL_Light.ttf`, `RobotoCondensed_Regular.ttf` (located in `src/assets/fonts/`, `android/app/src/main/assets/fonts/`, and iOS bundle).
- ~~**None are used**~~ — `src/utils/Colors/index.js` `fontObject` has `fontFamily: 'System'` everywhere. _2026-10-01:_ two are used outside the theme through `src/constants/fonts.js:7-13` (added 2026-03-21): Roboto Condensed in 19 files and RCL Light in 9, the v2 date range bar among them (`src/components/v2/DateRangeSheet/layout.bar.js:76-80`); OpenSans has 0 uses.

## 2. Text rendering audit

**Status (2026-10-01):** re-counted — v1 has about 2,370 `<Text` elements in about 250 files, 1,092 numeric `fontSize:` in 187 files and 289 bold or numeric `fontWeight` in 131; only 4 files import `Text` from `react-native` (the rest use Paper's). v2 has 0 numeric `fontSize`, 3 `fontWeight: '700'`, and all its text goes through `AppText` (Paper's `Menu` in `SortMenu.js` draws its own item titles).

### Topline numbers

**Status (2026-10-01):** `allowFontScaling` and `maxFontSizeMultiplier` still have 0 uses app-wide, now by rule for v2 (`AI.md:65-71`); the one multiplier prop is Paper's `titleMaxFontSizeMultiplier`, set to lift a cap (`SortMenu.js:120`); `AppText` exists (`src/components/v2/AppText.js`); `FONT_SIZES` is used by one v1 file.

- `<Text>` instances: **2,435+** across **181 files**
- Hardcoded `fontSize` values: **547**
- Hardcoded `fontWeight` values: **291**
- `variant` prop usage on Paper `<Text>`: **0** (no file uses MD3 variants today)
- `allowFontScaling` usage: **0**
- `maxFontSizeMultiplier` usage: **0**
- `StyleSheet.create` blocks: **177 files** (133 in `src/screens/`, rest in components)
- Custom text wrappers (`AppText` / `ThemedText` / etc.): **0** (`src/constants/designTokens.js` has unused `FONT_SIZES`)

### Text-density hotspots (top 15, these are Phase 5 priorities)

**Status (2026-10-01):** not re-counted — v1 files, untouched by D11; Phase 5 is superseded.

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

**Status (2026-10-01):** all eleven still carry their fixed height (lines moved, e.g. `Login.js:833`, `OneOrder.js:376`); v1 has 187 `height: N` literals in 114 files, not all on text. v2 has none on a text container.

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

**Status (2026-10-01):** v1 unchanged in kind (re-counts below); v2 has 0 hex and 0 `rgb(` literals, enforced by `eslint.config.js:42-76`.

### How colors are consumed

**Status (2026-10-01):** 225 files call Paper's `useTheme()` (233 call a `useTheme()` of either library; 0 in v2); 87 v1 files import `src/utils/Colors`, plus `src/theme/tint.js`, which borrows its colour helpers; v1 has 453 quoted hex literals in 99 files and 204 `rgb(a)(` in 96; `src/components/SVG/` holds 1,133 hex.

| Pattern                                                   | Files                          | Status                            |
| --------------------------------------------------------- | ------------------------------ | --------------------------------- |
| `useTheme()` from react-native-paper                      | **348 files**                  | Dominant, strong baseline         |
| Direct import of `Light` / `Dark` from `src/utils/Colors` | **86 files**                   | Needs shim during migration       |
| Hardcoded hex in StyleSheet                               | **227 files (screens)**        | **Target for Phase 3 removal**    |
| Hardcoded rgba/rgb strings                                | **~1,260 component instances** | Heavily concentrated in SVG icons |
| Inline color props on native components                   | **31 instances**               |                                   |
| Color name literals (`'white'`, `'red'`)                  | **16 instances**               |                                   |

### Hardcoded-color hotspots (top 20, Phase 3 priority)

**Status (2026-10-01):** not re-counted — v1 files, untouched by D11.

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

**Status (2026-10-01):** all seven keys were carried into `src/theme/tokens/palette.js:10-55` as they are (parity), so none was remapped; `white` changed on 2026-05-01 (`0c28903a`), corrected in the table.

Beyond MD3 basics, the existing `Light`/`Dark` objects add these custom keys:

| Key                  | Light value             | Dark value              | Notes                                                                  |
| -------------------- | ----------------------- | ----------------------- | ---------------------------------------------------------------------- |
| `white`              | ~~`rgba(255,255,255,0.7)`~~ `rgba(255, 255, 255)` (2026-05-01) | ~~`rgba(255,255,255,0.7)`~~ `rgba(255, 255, 255)` (2026-05-01) | **Same in both** — semantically an overlay, poorly named               |
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

**Status (2026-10-01):** unchanged — the brand SVGs keep their hex values; extraction was skipped in F-APP-3 (no clean list).

SVG brand logos in `src/components/SVG/psoc/` (IOCL, NAYARA, HPCL, BPCL, SHELL, JIO_BP) have 30–50 hardcoded hex values each. These are **intentionally theme-invariant** — moving them to `src/theme/tokens/fixed.js` as explicit brand tokens makes this intent clear.

## 4. Known accessibility gaps

**Status (2026-10-01):** the lines moved (`colors.placeholder` now at `CustSettings.js:674,699,…` and `SetDiscBS.js:273,294,315,342`), and the first row's premise does not hold: dark `placeholder` over `#121212` computes to ≈ 6.0:1, which passes AA. The review found a real gap in v2 instead — `success` text in light mode at ≈ 2.1–2.3:1 (T04-N2 in [00_README](./00_README.md)).

Spotted during the audit (not exhaustive — Phase 6 will do the full WCAG pass):

| File                                                | Line         | Issue                                                                                                                  |
| --------------------------------------------------- | ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `src/screens/Dealer/Customers/CustSettings.js`      | 91           | `color: colors.placeholder` on dark surface — placeholder is `rgba(255,255,255,0.54)`, fails WCAG AA against `#121212` |
| `src/screens/Dealer/Customers/SetDiscBS.js`         | 359, 389     | Same placeholder contrast issue in bottom sheet inputs                                                                 |
| `src/components/Prompt/index.js`                    | 98           | `subHeaderTextColor` defaults to `colors.text` but may be overridden to an unverified value                            |
| `src/screens/Dealer/ProductDates/SetProductRate.js` | ~5 locations | Heavy use of `colors.disabled` as background AND text color — likely imperceptible                                     |

## 5. Gaps summary

**Status (2026-10-01):** per-gap column added; the new system closes the gaps for v2 only, as D11 intends.

| Gap                                                      | Severity     | Phase                                 | 2026-10-01 |
| -------------------------------------------------------- | ------------ | ------------------------------------- | --- |
| No `<AppText>` wrapper → variants can't be enforced      | **Critical** | Phase 2                               | ✅ for v2 (`src/components/v2/AppText.js`); v1 untouched (D11) |
| 48+ fixed-height containers                              | **Critical** | Phase 4                               | ✅ none on v2 text; v1 keeps them (D11) |
| `allowFontScaling` never set → uncapped scaling untested | **Critical** | Phase 2                               | ✅ v2 tests state the scale — 31 test files run at 2.143× |
| 547 hardcoded `fontSize` + 291 `fontWeight`              | High         | Phase 5 (alongside Phase 2 migration) | ✅ v2 has no literal `fontSize`; v1 untouched (D11) |
| 1,500+ hardcoded colors                                  | High         | Phase 3                               | ✅ v2 has none; v1 untouched (D11) |
| Theme not extensible beyond 2 (hardcoded Light/Dark)     | High         | Phase 1                               | 🟡 themes keyed by name; still two |
| `defaultCombined.js` dead code                           | Low          | Phase 1 (delete)                      | ⬜ still present, 0 importers |
| Navigation theme relies on shape overlap                 | Medium       | Phase 1 (use `adaptNavigationTheme`)  | ⬜ still the Paper theme (`RestartContext.js:52`) |
| No local theme persistence (flash on fresh install)      | Medium       | Phase 6                               | ⏸ deferred by F-APP-3 |
| Custom fonts declared but unused                         | Low          | Phase 6                               | ⏸ premise corrected — two are used; OpenSans unused (6.3) |
| `letterSpacing: 0` bug in current `fontObject`           | Medium       | Phase 2                               | ❌ not a bug (see §1) |
| No contrast automation                                   | Medium       | Phase 6                               | ⬜ Phase 6 Step 6.1 |
| Two theme-toggle entry points (Settings + VersionInfo)   | Low          | Phase 6 consolidation                 | ⬜ still two |
