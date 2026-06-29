# Master Task Checklist

Every actionable step from every phase, in execution order. Check off as done. Phase docs have the context; this file is the punch list.

Legend: `[ ]` not started · `[~]` in progress · `[x]` done · `[/]` skipped (explain)

---

## Phase 1 — Foundation

- [ ] **1.1** Install `@shopify/restyle` (`yarn add @shopify/restyle`)
- [ ] **1.2** Create `src/theme/` folder skeleton (tokens, themes, adapters, provider, components, hooks, lint)
- [ ] **1.3** Write `src/theme/tokens/palette.js` — lift every hex from current `Colors/index.js` into named entries
- [ ] **1.4** Write `src/theme/tokens/fixed.js` — success/warning/info + placeholder for brand tokens
- [ ] **1.4a** Extract PSoC brand colors from `src/components/SVG/psoc/**` into `fixed.brand.*`
- [ ] **1.5** Write `src/theme/tokens/typography.js` — 15 MD3 variants with correct letterSpacing
- [ ] **1.6** Write `src/theme/tokens/spacing.js` and `radii.js`
- [ ] **1.6a** Write `src/theme/tokens/elevation.js` and `motion.js` (stubs OK for Phase 1)
- [ ] **1.7** Write `src/theme/themes/light.js` — map palette → semantic roles, mirror existing Light exactly
- [ ] **1.7a** Write `src/theme/themes/dark.js` — mirror existing Dark exactly
- [ ] **1.8** Write `src/theme/themes/neon.js` — proof of extensibility
- [ ] **1.9** Write `src/theme/themes/index.js` — `THEMES` array + `getThemeById`
- [ ] **1.10** Write `src/theme/adapters/toPaperTheme.js`
- [ ] **1.10a** Write `src/theme/adapters/toNavigationTheme.js`
- [ ] **1.11** Write `src/theme/provider/runtime.js` (module-level theme singleton)
- [ ] **1.12** Write `src/theme/provider/ThemeProvider.js` — wraps Restyle + Paper
- [ ] **1.13** Write `src/theme/provider/useAppTheme.js`
- [ ] **1.14** Write `src/theme/provider/useThemeSwitcher.js`
- [ ] **1.15** Create `src/store/slices/theme.js` and register in store
- [ ] **1.15a** Add `theme` to `redux-persist` whitelist
- [ ] **1.16** Refactor `src/utils/Colors/index.js` into a thin re-export shim
- [ ] **1.17** Delete `src/utils/Colors/defaultCombined.js` (dead code)
- [ ] **1.18** Wire `AppThemeProvider` into `src/navigation/AppNavigatorContainer.js` — replace lines 43–49 + 83
- [ ] **1.19** Update `src/components/Error/RestartContext.js` to use `toNavigationTheme(activeTheme)`
- [ ] **1.20** Smoke test: `yarn ios` + `yarn android` — visual parity, Settings toggle works, Redux force-to-neon works
- [ ] **1.21** `yarn lint` clean
- [ ] **1.22** Commit: `feat(theme): scaffold design system foundation with Restyle (Phase 1)`

## Phase 2 — Typography

- [ ] **2.1** Write `src/theme/components/AppText.js` — uncapped font scaling defaults
- [ ] **2.2** Write `src/theme/components/AppBox.js` — Restyle `createBox`
- [ ] **2.3** Write `src/theme/hooks/useFontScale.js`
- [ ] **2.4** Write `src/theme/hooks/useContainerMinHeight.js`
- [ ] **2.5** Write `src/theme/components/DevFontScaleBadge.js` (dev-only)
- [ ] **2.6** Write barrel files: `src/theme/components/index.js`, `src/theme/hooks/index.js`, `src/theme/index.js`
- [ ] **2.7** Add path alias `~/theme` → `src/theme` in babel config (if module-resolver present)
- [ ] **2.8** Verify Paper components (`<Button>`, `<Chip>`, `<Appbar.Content>`, `<Snackbar>`) pick up new MD3 typography automatically
- [ ] **2.9a** Canary: migrate `src/screens/Login/AuthNavigator/Login.js`
- [ ] **2.9b** Canary: migrate `src/screens/Common/Settings/index.js` + wire `useThemeSwitcher`
- [ ] **2.9c** Canary: migrate `src/screens/Common/DailySummary/component/index.js`
- [ ] **2.9d** Canary: migrate `src/screens/Dealer/Orders/components/OneOrder.js`
- [ ] **2.9e** Canary: migrate `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js`
- [ ] **2.9f** Canary: migrate `src/screens/Customer/NewPayment/index.js`
- [ ] **2.9g** Canary: migrate `src/screens/Customer/Dealers/DealerSettings/index.js`
- [ ] **2.9h** Canary: migrate `src/components/Prompt/index.js`
- [ ] **2.10** For each canary, fix any `height: N` found on text containers
- [ ] **2.11** Test canaries at iOS AX5 + Android 2x + bold on physical devices
- [ ] **2.12** Write `src/theme/README.md` — variant cheat sheet, usage rules
- [ ] **2.12a** Add typography section to `AI.md`
- [ ] **2.13** Add `no-restricted-imports` lint warning for bare `<Text>` from react-native
- [ ] **2.14** Commit: `feat(theme): add AppText, AppBox, uncapped font scaling (Phase 2)`

## Phase 3 — Color System

- [ ] **3.1** Extend every theme with full MD3 color role set (primary/onPrimary/primaryContainer/onPrimaryContainer × 4 families + surface tiers + outline + inverse + utility)
- [ ] **3.2** Add legacy aliases on theme (`white`, `black`, `gray`, `antiText`, `link`, `success`) mapped to new semantic roles
- [ ] **3.3** Finalize `src/theme/tokens/fixed.js` with all fixed tokens
- [ ] **3.4** Extract brand colors from every SVG under `src/components/SVG/psoc/`
- [ ] **3.4a** Update SVG components to reference `theme.fixed.brand.*`
- [ ] **3.5** Migrate top-20 hardcoded-color hotspots (see `06_PHASE_3_COLORS.md` for list)
  - [ ] `src/components/Prompt/index.js`
  - [ ] `src/screens/Customer/NewOrder/components.js`
  - [ ] `src/screens/Common/Orders/components/FilterList.js`
  - [ ] `src/screens/Dealer/Payments/BSheets/AttachInvs.js`
  - [ ] `src/screens/Dealer/Orders/index.js`
  - [ ] `src/screens/Customer/Orders/index.js`
  - [ ] `src/screens/Common/Orders/index.js`
  - [ ] `src/screens/Common/Orders/bottomsheet/filter.js`
  - [ ] `src/components/Input/IconInput.js`
  - [ ] `src/screens/Dealer/ProductDates/SetProductRate.js`
  - [ ] `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js`
  - [ ] `src/screens/Customer/Vehicles/vehicleComponents/index.js`
  - [ ] `src/screens/Customer/NewPayment/index.js`
  - [ ] `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js`
  - [ ] `src/screens/Common/Reports/DailyReport/components.js`
  - [ ] `src/screens/Common/Payments/components/index.js`
  - [ ] `src/screens/Common/Orders/components/newDesign.js`
  - [ ] `src/components/NumberMeter/logic.js` + `index.js`
  - [ ] `src/screens/Login/AuthNavigator/Welcome.js`
- [ ] **3.6** Write `src/theme/lint/no-hardcoded-colors.js` + register in `.eslintrc` at `"warn"`
- [ ] **3.7** Fix placeholder-contrast bugs in `CustSettings.js:91`, `SetDiscBS.js:359/389`, and similar
- [ ] **3.8** Spot-check Paper components in all 3 themes (Button/Chip/Dialog/Snackbar/Appbar/FAB)
- [ ] **3.9** Run `yarn lint` — document warning counts, target → 0 outside exempted paths
- [ ] **3.10** Commit: `feat(theme): semantic color system + fixed brand tokens (Phase 3)`

## Phase 4 — Android Clipping + Uncapped Layout Fix

- [ ] **4.1** Fix lineHeight ratios in `src/theme/tokens/typography.js` for display variants (1.12/1.16/1.22 → 1.26+)
- [ ] **4.2** Grep for `height: [0-9]` in `src/screens` + `src/components` — build the 48+ file punch list
- [ ] **4.3** Migrate every file in the punch list to `minHeight` + `paddingVertical`
  - [ ] `src/screens/Customer/Payments/index.js:498`
  - [ ] `src/screens/Customer/Dealers/BSheets/AddDealer.js:405`
  - [ ] `src/screens/Login/AuthNavigator/Login.js:810`
  - [ ] `src/screens/Common/Profile/SelectStateBS.js:518`
  - [ ] `src/screens/Dealer/Orders/components/OneOrder.js:382`
  - [ ] `src/screens/Common/Orders/bottomsheet/dateRange.js:416`
  - [ ] `src/components/DatePicker/index.js:920` (iOS picker special case)
  - [ ] `src/components/Input/CustomInput.js:468`
  - [ ] `src/components/Input/IconInput.js:44`
  - [ ] `src/components/Input/BS/BSheetInput.js:42`
  - [ ] `src/components/Input/IconLabelInput.js:42`
  - [ ] _(remaining ~37 files from the grep)_
- [ ] **4.4** Audit `flexDirection: 'row'` layouts in the top-20 text-density screens — add `flex: 1` / `numberOfLines` / `ellipsizeMode`
- [ ] **4.5** Grep remaining `fontWeight: 'bold' | '700' | 'Bold'` — convert to variants or use 600 (semibold)
- [ ] **4.6** Add `adjustsFontSizeToFit` + `minimumFontScale={0.85}` to bottom-tab labels, appbar titles, chip labels
- [ ] **4.7** Add `dynamicTypeRamp` iOS defaults inside `AppText.js` keyed by variant
- [ ] **4.8** Run the full test matrix: iPhone SE (normal + largest + AX5), Pixel 4a (normal + largest + largest+bold), 2GB emulator (largest+bold)
- [ ] **4.9** Re-run FlashList perf benchmarks for Orders/Payments/Products/Vehicles/Dealers/Customers lists
- [ ] **4.10** Append "Layout rules for uncapped font scaling" section to `src/theme/README.md`
- [ ] **4.11** Commit: `fix(theme): Android text clipping + uncapped layout migration (Phase 4)`

## Phase 5 — Screen Migration

### Wave A — Shared components

- [ ] **5.A.1** `src/components/Prompt/index.js` (touched in 3.5 — verify)
- [ ] **5.A.2** `src/components/Input/CustomInput.js`
- [ ] **5.A.3** `src/components/Input/IconInput.js`
- [ ] **5.A.4** `src/components/Input/IconLabelInput.js`
- [ ] **5.A.5** `src/components/Input/BS/BSheetInput.js`
- [ ] **5.A.6** `src/components/DatePicker/index.js` + `DTBS.js`
- [ ] **5.A.7** `src/components/VersionInfo/index.js` (also remove duplicate theme toggle)
- [ ] **5.A.8** `src/components/NumberMeter/index.js` + `logic.js`
- [ ] **5.A.9** `src/components/NoNetwork/Undraw.js`
- [ ] **5.A.10** `src/components/Error/ErrorBoundary.js`
- [ ] **5.A.11** `src/components/Error/RestartContext.js` (verify from Phase 1)
- [ ] **5.A.12** `src/components/SVG/RNVI/**` — batch pass
- [ ] **5.A.13** `src/components/SVG/psoc/**` — verify from Phase 3

### Wave B — Auth / Settings / Profile

- [ ] **5.B.1** `src/screens/Login/AuthNavigator/Welcome.js`
- [ ] **5.B.2** `src/screens/Login/AuthNavigator/Login.js` (verify from 2.9a)
- [ ] **5.B.3** `src/screens/Login/AuthNavigator/Register.js`
- [ ] **5.B.4** `src/screens/Login/AuthNavigator/OTP.js`
- [ ] **5.B.5** `src/screens/Login/AuthNavigator/ForgotPass.js`
- [ ] **5.B.6** `src/screens/StartupScreen.js`
- [ ] **5.B.7** `src/screens/Common/Settings/index.js` (verify from 2.9b)
- [ ] **5.B.8** `src/screens/Common/Profile/**` (all files including `SelectStateBS.js`)

### Wave C — Core commerce

- [ ] **5.C.1** `src/screens/Dealer/Orders/index.js`
- [ ] **5.C.2** `src/screens/Dealer/Orders/components/OneOrder.js` (verify from 2.9d)
- [ ] **5.C.3** `src/screens/Dealer/Orders/components/OTPmodule.js`
- [ ] **5.C.4** `src/screens/Dealer/Orders/**` rest
- [ ] **5.C.5** `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` (verify from 2.9e)
- [ ] **5.C.6** `src/screens/Dealer/NewInvoice/newComp/SummaryModal.js`
- [ ] **5.C.7** `src/screens/Dealer/NewInvoice/**` rest
- [ ] **5.C.8** `src/screens/Dealer/Payments/**`
- [ ] **5.C.9** `src/screens/Customer/Orders/index.js`
- [ ] **5.C.10** `src/screens/Customer/Orders/components/EmergencyOTPBS.js`
- [ ] **5.C.11** `src/screens/Customer/Orders/**` rest
- [ ] **5.C.12** `src/screens/Customer/NewOrder/components.js`
- [ ] **5.C.13** `src/screens/Customer/NewPayment/index.js` (verify from 2.9f)
- [ ] **5.C.14** `src/screens/Customer/Dealers/DealerSettings/index.js` (verify from 2.9g)
- [ ] **5.C.15** `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js`
- [ ] **5.C.16** `src/screens/Customer/Dealers/BSheets/AddDealer.js`
- [ ] **5.C.17** `src/screens/Customer/Dealers/BSheets/TCSTDSSettings.js`
- [ ] **5.C.18** `src/screens/Customer/Payments/index.js`
- [ ] **5.C.19** `src/screens/Common/Orders/index.js`
- [ ] **5.C.20** `src/screens/Common/Orders/components/newDesign.js`
- [ ] **5.C.21** `src/screens/Common/Orders/components/FilterList.js`
- [ ] **5.C.22** `src/screens/Common/Orders/bottomsheet/filter.js`
- [ ] **5.C.23** `src/screens/Common/Orders/bottomsheet/dateRange.js`
- [ ] **5.C.24** `src/screens/Common/Payments/components/index.js`
- [ ] **5.C.25** `src/screens/Common/_Voucher_/BS/index.js`

### Wave D — Remaining

- [ ] **5.D.1** `src/screens/Dealer/Customers/CustSettings.js`
- [ ] **5.D.2** `src/screens/Dealer/Customers/SetDiscBS.js`
- [ ] **5.D.3** `src/screens/Dealer/ProductDates/SetProductRate.js`
- [ ] **5.D.4** `src/screens/Dealer/Dashboard/**`
- [ ] **5.D.5** `src/screens/Dealer/Products/**`
- [ ] **5.D.6** `src/screens/Dealer/Requests/**`
- [ ] **5.D.7** `src/screens/Dealer/Reports/**`
- [ ] **5.D.8** `src/screens/Dealer/Vehicles/**`
- [ ] **5.D.9** `src/screens/Dealer/Drivers/**`
- [ ] **5.D.10** `src/screens/Dealer/Users/**`
- [ ] **5.D.11** `src/screens/Customer/Dashboard/**`
- [ ] **5.D.12** `src/screens/Customer/Vehicles/**`
- [ ] **5.D.13** `src/screens/Customer/Requests/**`
- [ ] **5.D.14** `src/screens/Customer/Reports/**`
- [ ] **5.D.15** `src/screens/Customer/Users/**`
- [ ] **5.D.16** `src/screens/Common/Reports/DailyReport/components.js`
- [ ] **5.D.17** `src/screens/Common/Reports/TcsTds/Render/MonthExcel.js`
- [ ] **5.D.18** `src/screens/Common/Reports/**` rest
- [ ] **5.D.19** `src/screens/Common/DailySummary/component/index.js` (verify from 2.9c)
- [ ] **5.D.20** `src/screens/Common/Accounts/components.js`
- [ ] **5.D.21** `src/screens/Common/RelationList/RelationCreditBS.js`
- [ ] **5.D.22** `src/screens/Common/Dashboard/**`
- [ ] **5.D.23** `src/navigation/Dealer/DrawerContent.js`
- [ ] **5.D.24** `src/navigation/Dealer/TrnTab.js`
- [ ] **5.D.25** `src/navigation/Dealer/Main.js`
- [ ] **5.D.26** `src/navigation/Customer/DrawerContent.js`
- [ ] **5.D.27** `src/navigation/Customer/TrnTab.js`
- [ ] **5.D.28** `src/navigation/Common/CustomHeader.js`

### Wave exit gates

- [ ] **5.E.1** After Wave A: `grep -rn "import { Text } from 'react-native'" src/components` → only `src/theme/components/AppText.js`
- [ ] **5.E.2** After Wave D: same grep across `src/screens` → empty
- [ ] **5.E.3** After Wave D: `grep -rn "fontSize:" src/screens src/components` → empty
- [ ] **5.E.4** After Wave D: `yarn lint` → zero warnings from `no-restricted-imports` or `no-hardcoded-colors`

## Phase 6 — Polish

- [ ] **6.1** Install `wcag-contrast` or `color2k`
- [ ] **6.1a** Write `src/theme/__tests__/contrast.test.js`
- [ ] **6.1b** All contrast tests pass in `yarn test`
- [ ] **6.2** Escalate `no-restricted-imports` to `error`
- [ ] **6.2a** Escalate `no-hardcoded-colors` to `error`
- [ ] **6.3** Custom font decision (Option A/B/C) — implement choice
- [ ] **6.4** Add `theme` slice to `redux-persist` whitelist (confirm from 1.15a)
- [ ] **6.5** Remove duplicate theme toggle from `src/components/VersionInfo/index.js`
- [ ] **6.6** Accessibility audit — TalkBack on top-20 screens
- [ ] **6.6a** Accessibility audit — VoiceOver on top-20 screens
- [ ] **6.6b** Reduced motion respect — audit reanimated usage
- [ ] **6.7** Apple-grade polish checklist (spacing rhythm, alignment, icon sizes, elevations, haptics, motion tokens, tap targets, focus states)
- [ ] **6.8** (Optional) Material You dynamic color via `@pchmn/expo-material3-theme`
- [ ] **6.9** Add high-contrast theme as extensibility stress test
- [ ] **6.10** Finalize `src/theme/README.md` (full developer docs)
- [ ] **6.10a** Update `AI.md` with theming conventions section
- [ ] **6.11** Write `scripts/export-design-tokens.js` for Figma handoff
- [ ] **6.12** Write `docs/todos/design-system/RETRO.md` — migration retrospective

---

## Open questions (resolve before starting the phase)

- [ ] **Q1** Path alias: is `babel-plugin-module-resolver` already installed? If yes use `~/theme`; if no, use relative imports. (Phase 2.7)
- [ ] **Q2** Font decision (OpenSans adoption vs retirement) — design team sign-off required before Phase 6.3
- [ ] **Q3** Is `redux-persist` currently wired? If not, setup is added as a prerequisite sub-task to Phase 1.15a
- [ ] **Q4** Does the team want Material You dynamic color on Android 12+, or stick with named themes only? (Phase 6.8)
- [ ] **Q5** Which low-end Android device is the reference for the 2x + bold testing? Acquire or allocate. (Phase 4.8)

---

## Estimated effort (rough order-of-magnitude)

| Phase     | Dev days  | Notes                                                    |
| --------- | --------- | -------------------------------------------------------- |
| Phase 1   | 2–3       | Scaffold, no screen changes                              |
| Phase 2   | 3–4       | Primitives + 8 canary migrations                         |
| Phase 3   | 2–3       | Color migration for 20 hotspots + ESLint rule            |
| Phase 4   | 3–5       | 48+ fixed-height fixes + test matrix on physical devices |
| Phase 5   | 10–15     | The big wave, ~180 files across 4 sub-waves              |
| Phase 6   | 2–3       | Polish + enforcement + docs                              |
| **Total** | **22–33** | Call it **4–7 weeks** with QA buffer                     |

This is wall-clock if one engineer drives it with occasional pair review. Two engineers can parallelize Phase 5 waves cleanly (one does Wave A + C, other does B + D) and compress to 3–4 weeks.
