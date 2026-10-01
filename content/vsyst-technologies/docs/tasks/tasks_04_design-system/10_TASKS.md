# Master Task Checklist

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Redesign decision D11 ran Phases 1–3 as foundation step F-APP-3, scoped to `src/theme/`, `src/components/v2/` and the v2 screens (no Restyle, no restyle of v1), and replaced Phase 5 with the per-screen loop. Every box now ends with `· **2026-10-01:** <mark> <evidence>`; a box is ticked `[x]` only where code proves it for that D11 scope, sometimes at another path or without Restyle, as its line says. Of the 203 original boxes: ✅ 28 · 🟡 7 · ⬜ 20 · ⏸ 5 · ❔ 7 · ❌ 136 (Phase 5's 78 and the 31 v1-file sub-items among them); 3 🆕 items are added after Phase 6. The API is not involved (app-only plan). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

Every actionable step from every phase, in execution order. Check off as done. Phase docs have the context; this file is the punch list.

Legend: `[ ]` not started · `[~]` in progress · `[x]` done · `[/]` skipped (explain)

---

## Phase 1 — Foundation

**Status (2026-10-01):** 🟡 built as F-APP-3 on 2026-09-04, without Restyle — ✅ 13 · 🟡 1 · ⬜ 6 · ❌ 4 · ⏸ 1 · ❔ 2 of 27. Detail: [04_PHASE_1_FOUNDATION.md](./04_PHASE_1_FOUNDATION.md).

- [ ] **1.1** Install `@shopify/restyle` (`yarn add @shopify/restyle`) · **2026-10-01:** ❌ Restyle rejected 2026-09-04 (02-foundations log); not in `package.json`
- [x] **1.2** Create `src/theme/` folder skeleton (tokens, themes, adapters, provider, components, hooks, lint) · **2026-10-01:** ✅ `src/theme/{tokens,themes,adapters,provider}`; primitives in `src/components/v2` (D10); lint in `eslint.config.js`
- [x] **1.3** Write `src/theme/tokens/palette.js` — lift every hex from current `Colors/index.js` into named entries · **2026-10-01:** ✅ `src/theme/tokens/palette.js:9-56`, key for key, pinned by `parity.test.js`
- [ ] **1.4** Write `src/theme/tokens/fixed.js` — success/warning/info + placeholder for brand tokens · **2026-10-01:** ⬜ no `fixed.js`, no `warning` / `info`; `success` is a palette key (`palette.js:31,54`)
- [ ] **1.4a** Extract PSoC brand colors from `src/components/SVG/psoc/**` into `fixed.brand.*` · **2026-10-01:** ❌ skipped in F-APP-3 — the SVGs hold hundreds of illustration hexes, no clean list
- [x] **1.5** Write `src/theme/tokens/typography.js` — 15 MD3 variants with correct letterSpacing · **2026-10-01:** ✅ `tokens/typography.js:8-114` — the 15 roles, verbatim legacy `fontObject` (Paper’s MD3 tracking)
- [x] **1.6** Write `src/theme/tokens/spacing.js` and `radii.js` · **2026-10-01:** ✅ both reuse `src/constants/designTokens.js` (spacing `xs`–`xl`, radii `sm`–`lg`)
- [ ] **1.6a** Write `src/theme/tokens/elevation.js` and `motion.js` (stubs OK for Phase 1) · **2026-10-01:** 🟡 `tokens/elevation.js` (the legacy levels); no `motion.js`
- [x] **1.7** Write `src/theme/themes/light.js` — map palette → semantic roles, mirror existing Light exactly · **2026-10-01:** ✅ `themes/light.js:13-25`; `parity.test.js:20-22` pins Paper output = legacy `Light`
- [x] **1.7a** Write `src/theme/themes/dark.js` — mirror existing Dark exactly · **2026-10-01:** ✅ `themes/dark.js:13-26`; `parity.test.js:24-26` pins it = legacy `Dark`
- [ ] **1.8** Write `src/theme/themes/neon.js` — proof of extensibility · **2026-10-01:** ❌ F-APP-3 “deliberately not: neon theme”
- [x] **1.9** Write `src/theme/themes/index.js` — `THEMES` array + `getThemeById` · **2026-10-01:** ✅ `themes/index.js:9` — `themes = { light, dark }` keyed by name; no array or `getThemeById`
- [x] **1.10** Write `src/theme/adapters/toPaperTheme.js` · **2026-10-01:** ✅ `adapters/toPaperTheme.js:28-44`
- [x] **1.10a** Write `src/theme/adapters/toNavigationTheme.js` · **2026-10-01:** ✅ `adapters/toNavigationTheme.js:33-44` + test — but it has no caller (1.19)
- [ ] **1.11** Write `src/theme/provider/runtime.js` (module-level theme singleton) · **2026-10-01:** ⬜ no `runtime.js`; no non-React caller needs the theme yet
- [x] **1.12** Write `src/theme/provider/ThemeProvider.js` — wraps Restyle + Paper · **2026-10-01:** ✅ `provider/ThemeProvider.js:18-34` (a context, no Restyle), mounted around `PaperProvider`
- [x] **1.13** Write `src/theme/provider/useAppTheme.js` · **2026-10-01:** ✅ `provider/useAppTheme.js:15-28` (throws outside the provider)
- [ ] **1.14** Write `src/theme/provider/useThemeSwitcher.js` · **2026-10-01:** ⬜ not built; the theme is still SYSTEM / DARK / LIGHT from Settings (`Settings/index.js:26`)
- [ ] **1.15** Create `src/store/slices/theme.js` and register in store · **2026-10-01:** ⬜ no theme slice; the theme is `auth.user.theme` (`AppNavigatorContainer.js:73-78`)
- [ ] **1.15a** Add `theme` to `redux-persist` whitelist · **2026-10-01:** ⏸ F-APP-3 deferred theme persistence; `redux-persist` is not a dependency (Q3)
- [ ] **1.16** Refactor `src/utils/Colors/index.js` into a thin re-export shim · **2026-10-01:** ❌ superseded — `utils/Colors` stays the v1 source; the tokens copy it, parity pins them
- [ ] **1.17** Delete `src/utils/Colors/defaultCombined.js` (dead code) · **2026-10-01:** ⬜ `src/utils/Colors/defaultCombined.js` still present (87 lines), 0 importers
- [x] **1.18** Wire `AppThemeProvider` into `src/navigation/AppNavigatorContainer.js` — replace lines 43–49 + 83 · **2026-10-01:** ✅ `AppNavigatorContainer.js:84-88,176-181` (memoised `toPaperTheme`, provider order)
- [ ] **1.19** Update `src/components/Error/RestartContext.js` to use `toNavigationTheme(activeTheme)` · **2026-10-01:** ⬜ `RestartProvider` still gets the Paper theme (`AppNavigatorContainer.js:179`, `RestartContext.js:52`)
- [ ] **1.20** Smoke test: `yarn ios` + `yarn android` — visual parity, Settings toggle works, Redux force-to-neon works · **2026-10-01:** ❔ parity proven in Jest; the device screenshot pair was left to the user; neon / persist parts ❌
- [ ] **1.21** `yarn lint` clean · **2026-10-01:** ❔ not run here; app CI runs Jest only (`.github/workflows/test.yml:9-29`)
- [x] **1.22** Commit: `feat(theme): scaffold design system foundation with Restyle (Phase 1)` · **2026-10-01:** ✅ `cc5413c7` → `87bde4f9` (2026-09-04), without Restyle

## Phase 2 — Typography

**Status (2026-10-01):** 🟡 `AppText`, `Box`, the type scale and the AI.md rules exist for v2 — ✅ 8 · 🟡 1 · ⬜ 2 · ❌ 11 (the canaries, D11) of 22.

- [x] **2.1** Write `src/theme/components/AppText.js` — uncapped font scaling defaults · **2026-10-01:** ✅ `src/components/v2/AppText.js:24-53`; uncapped, pinned by `AppText.test.js:91-109`
- [x] **2.2** Write `src/theme/components/AppBox.js` — Restyle `createBox` · **2026-10-01:** ✅ as `Box` (`src/components/v2/Box.js:49`) — token props on `StyleSheet`, no Restyle
- [x] **2.3** Write `src/theme/hooks/useFontScale.js` · **2026-10-01:** ✅ as `useTypeScale` (`theme/provider/useTypeScale.js:25-38`), from `useWindowDimensions().fontScale`
- [x] **2.4** Write `src/theme/hooks/useContainerMinHeight.js` · **2026-10-01:** ✅ as `lineHeightAt` / `boxHeight` (`theme/scale.js:68,86`), through `useTypeScale()`
- [ ] **2.5** Write `src/theme/components/DevFontScaleBadge.js` (dev-only) · **2026-10-01:** ⬜ no badge; tests state the scale instead (`renderScreen(ui, { fontScale })`; 31 test files at 2.143)
- [x] **2.6** Write barrel files: `src/theme/components/index.js`, `src/theme/hooks/index.js`, `src/theme/index.js` · **2026-10-01:** ✅ `src/theme/index.js`, `src/components/v2/index.js`
- [ ] **2.7** Add path alias `~/theme` → `src/theme` in babel config (if module-resolver present) · **2026-10-01:** ❌ skipped, as the step allows — no `babel-plugin-module-resolver`; relative imports (Q1)
- [x] **2.8** Verify Paper components (`<Button>`, `<Chip>`, `<Appbar.Content>`, `<Snackbar>`) pick up new MD3 typography automatically · **2026-10-01:** ✅ Paper’s `fonts` come from the tokens (`toPaperTheme.js:35-38`), pinned = legacy
- [ ] **2.9a** Canary: migrate `src/screens/Login/AuthNavigator/Login.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.9b** Canary: migrate `src/screens/Common/Settings/index.js` + wire `useThemeSwitcher` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.9c** Canary: migrate `src/screens/Common/DailySummary/component/index.js` · **2026-10-01:** ❌ D11 — replaced by the v2 `Common/DailySummary` screen, not migrated
- [ ] **2.9d** Canary: migrate `src/screens/Dealer/Orders/components/OneOrder.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.9e** Canary: migrate `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.9f** Canary: migrate `src/screens/Customer/NewPayment/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.9g** Canary: migrate `src/screens/Customer/Dealers/DealerSettings/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.9h** Canary: migrate `src/components/Prompt/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **2.10** For each canary, fix any `height: N` found on text containers · **2026-10-01:** ❌ D11 (canaries dropped); v2 follows “text sets the box” (`AI.md:72-76`)
- [ ] **2.11** Test canaries at iOS AX5 + Android 2x + bold on physical devices · **2026-10-01:** ❌ D11 (canaries dropped); v2 decision tests run at 1× and 2.143× (F-APP-7)
- [ ] **2.12** Write `src/theme/README.md` — variant cheat sheet, usage rules · **2026-10-01:** 🟡 no `src/theme/README.md`; the rules live in `docs/testing.md:420-1073` and `AI.md:46-76`
- [x] **2.12a** Add typography section to `AI.md` · **2026-10-01:** ✅ `AI.md:46-51` (colour tokens), `AI.md:65-76` (uncapped, text sets the box)
- [ ] **2.13** Add `no-restricted-imports` lint warning for bare `<Text>` from react-native · **2026-10-01:** ⬜ no bare-`Text` import rule; 0 v2 files import it (AppText wraps Paper’s `Text`)
- [x] **2.14** Commit: `feat(theme): add AppText, AppBox, uncapped font scaling (Phase 2)` · **2026-10-01:** ✅ `cc5413c7` → `87bde4f9` (primitives), `3385ec2a` → `48c7aa00` (type scale)

## Phase 3 — Color System

**Status (2026-10-01):** 🟡 the v2 colour guard exists — ✅ 2 · ⬜ 2 · ❌ 6 · ❔ 1 of 11, plus the 19 v1 hotspot files ❌ (D11).

- [ ] **3.1** Extend every theme with full MD3 color role set (primary/onPrimary/primaryContainer/onPrimaryContainer × 4 families + surface tiers + outline + inverse + utility) · **2026-10-01:** ⬜ the theme keeps the legacy keys (parity); 0 container / tertiary / inverse roles in `src/theme`
- [ ] **3.2** Add legacy aliases on theme (`white`, `black`, `gray`, `antiText`, `link`, `success`) mapped to new semantic roles · **2026-10-01:** ❌ superseded — the legacy keys are the theme’s own keys (`palette.js:10-55`); nothing to alias
- [ ] **3.3** Finalize `src/theme/tokens/fixed.js` with all fixed tokens · **2026-10-01:** ⬜ no `fixed.js` (see 1.4)
- [ ] **3.4** Extract brand colors from every SVG under `src/components/SVG/psoc/` · **2026-10-01:** ❌ skipped in F-APP-3; 1,133 hex literals remain under `src/components/SVG/`
- [ ] **3.4a** Update SVG components to reference `theme.fixed.brand.*` · **2026-10-01:** ❌ follows 3.4; the logos are v1 components (D11)
- [ ] **3.5** Migrate top-20 hardcoded-color hotspots (see `06_PHASE_3_COLORS.md` for list) · **2026-10-01:** ❌ D11 — v1 keeps 453 quoted hex (99 files) and 204 `rgb(a)(` (96 files); v2 has none
  - [ ] `src/components/Prompt/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Customer/NewOrder/components.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Common/Orders/components/FilterList.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Dealer/Payments/BSheets/AttachInvs.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Dealer/Orders/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Customer/Orders/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Common/Orders/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Common/Orders/bottomsheet/filter.js` · **2026-10-01:** ❌ D11
  - [ ] `src/components/Input/IconInput.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Dealer/ProductDates/SetProductRate.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Customer/Vehicles/vehicleComponents/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Customer/NewPayment/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js` · **2026-10-01:** ❌ D11; the file is gone — `c5e87820` (2026-06-04) folded the On A/c payment into the voucher flow (`src/screens/Customer/NewPayAck/`, v1)
  - [ ] `src/screens/Common/Reports/DailyReport/components.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Common/Payments/components/index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Common/Orders/components/newDesign.js` · **2026-10-01:** ❌ D11
  - [ ] `src/components/NumberMeter/logic.js` + `index.js` · **2026-10-01:** ❌ D11
  - [ ] `src/screens/Login/AuthNavigator/Welcome.js` · **2026-10-01:** ❌ D11
- [x] **3.6** Write `src/theme/lint/no-hardcoded-colors.js` + register in `.eslintrc` at `"warn"` · **2026-10-01:** ✅ as a scoped `no-restricted-syntax` block at `error` (`eslint.config.js:42-76`), pinned by `eslintRule.test.js`
- [ ] **3.7** Fix placeholder-contrast bugs in `CustSettings.js:91`, `SetDiscBS.js:359/389`, and similar · **2026-10-01:** ❌ D11 (v1 screens); computed: dark `placeholder` on `#121212` ≈ 6.0:1, which passes AA
- [ ] **3.8** Spot-check Paper components in all 3 themes (Button/Chip/Dialog/Snackbar/Appbar/FAB) · **2026-10-01:** ❌ superseded by `parity.test.js` — Paper’s theme is byte-identical; no third theme
- [ ] **3.9** Run `yarn lint` — document warning counts, target → 0 outside exempted paths · **2026-10-01:** ❔ lint not run here; app CI has no lint job (see `X-CI-2` in tasks_02)
- [x] **3.10** Commit: `feat(theme): semantic color system + fixed brand tokens (Phase 3)` · **2026-10-01:** ✅ in the F-APP-3 commits `cc5413c7` → `87bde4f9`

## Phase 4 — Android Clipping + Uncapped Layout Fix

**Status (2026-10-01):** 🟡 v2 is built to “text sets the box” — ✅ 2 · 🟡 1 · ⬜ 2 · ❌ 5 · ❔ 1 of 11, plus the 12 v1 fixed-height sub-items ❌ (D11); two Android items are 🆕 below.

- [ ] **4.1** Fix lineHeight ratios in `src/theme/tokens/typography.js` for display variants (1.12/1.16/1.22 → 1.26+) · **2026-10-01:** ⬜ display line heights still 44 / 52 / 64 (`typography.js:9-29`); v2 uses no display role
- [ ] **4.2** Grep for `height: [0-9]` in `src/screens` + `src/components` — build the 48+ file punch list · **2026-10-01:** ❌ D11 — no v1 punch list; v2 text containers carry no fixed `height`
- [ ] **4.3** Migrate every file in the punch list to `minHeight` + `paddingVertical` · **2026-10-01:** ❌ D11 — the listed v1 files keep fixed heights; v2 was built to F-APP-7
  - [ ] `src/screens/Customer/Payments/index.js:498` · **2026-10-01:** ❌ D11 — still `height: 40` (now line 523)
  - [ ] `src/screens/Customer/Dealers/BSheets/AddDealer.js:405` · **2026-10-01:** ❌ D11 — still `height: 40` (now line 426)
  - [ ] `src/screens/Login/AuthNavigator/Login.js:810` · **2026-10-01:** ❌ D11 — still `height: 40` (now line 833)
  - [ ] `src/screens/Common/Profile/SelectStateBS.js:518` · **2026-10-01:** ❌ D11 — still `height: 40` (now line 530)
  - [ ] `src/screens/Dealer/Orders/components/OneOrder.js:382` · **2026-10-01:** ❌ D11 — still `height: 50` (now line 376)
  - [ ] `src/screens/Common/Orders/bottomsheet/dateRange.js:416` · **2026-10-01:** ❌ D11 — still `height: 60` (now line 410)
  - [ ] `src/components/DatePicker/index.js:920` (iOS picker special case) · **2026-10-01:** ❌ D11 — still `height: 60`
  - [ ] `src/components/Input/CustomInput.js:468` · **2026-10-01:** ❌ D11 — still `height: 56`
  - [ ] `src/components/Input/IconInput.js:44` · **2026-10-01:** ❌ D11 — still `height: 48`
  - [ ] `src/components/Input/BS/BSheetInput.js:42` · **2026-10-01:** ❌ D11 — still `height: 48`
  - [ ] `src/components/Input/IconLabelInput.js:42` · **2026-10-01:** ❌ D11 — still `height: 48`
  - [ ] _(remaining ~37 files from the grep)_ · **2026-10-01:** ❌ D11 — v1 has 187 `height: N` literals in 114 files
- [ ] **4.4** Audit `flexDirection: 'row'` layouts in the top-20 text-density screens — add `flex: 1` / `numberOfLines` / `ellipsizeMode` · **2026-10-01:** ❌ D11 — the top-20 are v1; v2 rows follow the rule (`AI.md:72-76`)
- [ ] **4.5** Grep remaining `fontWeight: 'bold' | '700' | 'Bold'` — convert to variants or use 600 (semibold) · **2026-10-01:** 🟡 v2 has 3 `fontWeight: '700'` (`SortMenu.js:169`, `OrderRow.js:238,256`); v1 untouched (D11)
- [ ] **4.6** Add `adjustsFontSizeToFit` + `minimumFontScale={0.85}` to bottom-tab labels, appbar titles, chip labels · **2026-10-01:** ❌ superseded — v2 text never shrinks (`AI.md:65-71`); the header bar grows instead (`3a0b83b1`)
- [ ] **4.7** Add `dynamicTypeRamp` iOS defaults inside `AppText.js` keyed by variant · **2026-10-01:** ⬜ 0 `dynamicTypeRamp`; per-role ramps would break v2’s one-`fontScale` box maths
- [ ] **4.8** Run the full test matrix: iPhone SE (normal + largest + AX5), Pixel 4a (normal + largest + largest+bold), 2GB emulator (largest+bold) · **2026-10-01:** ❔ device-only; no low-end reference device recorded (Q5)
- [ ] **4.9** Re-run FlashList perf benchmarks for Orders/Payments/Products/Vehicles/Dealers/Customers lists · **2026-10-01:** ❌ nothing to re-check — v1 lists unchanged (D11); v2 list performance is tracked in the redesign
- [x] **4.10** Append "Layout rules for uncapped font scaling" section to `src/theme/README.md` · **2026-10-01:** ✅ in `AI.md:65-76` and `docs/testing.md:440` (“Type scale”), not `src/theme/README.md`
- [x] **4.11** Commit: `fix(theme): Android text clipping + uncapped layout migration (Phase 4)` · **2026-10-01:** ✅ F-APP-7 `3385ec2a` → `48c7aa00`, `e171d278` → `1bf9dce6`; Android theme `fe8799d5`

## Phase 5 — Screen Migration

**Status (2026-10-01):** ❌ superseded by D11 — all 78 boxes. Screens are redesigned whole through [03-per-screen-playbook](../../oms_app/screen-redesign/03-per-screen-playbook.md) (2 screens / 3 registry keys so far); several Wave B / D paths never existed in the tree.

### Wave A — Shared components

**Status (2026-10-01):** ❌ superseded by D11 (see Phase 5).

- [ ] **5.A.1** `src/components/Prompt/index.js` (touched in 3.5 — verify) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.2** `src/components/Input/CustomInput.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.3** `src/components/Input/IconInput.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.4** `src/components/Input/IconLabelInput.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.5** `src/components/Input/BS/BSheetInput.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.6** `src/components/DatePicker/index.js` + `DTBS.js` · **2026-10-01:** ❌ D11; v2 Daily Summary uses `components/v2/DateRangeSheet` instead
- [ ] **5.A.7** `src/components/VersionInfo/index.js` (also remove duplicate theme toggle) · **2026-10-01:** ❌ D11; its duplicate theme toggle is still there (6.5)
- [ ] **5.A.8** `src/components/NumberMeter/index.js` + `logic.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.9** `src/components/NoNetwork/Undraw.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.10** `src/components/Error/ErrorBoundary.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.11** `src/components/Error/RestartContext.js` (verify from Phase 1) · **2026-10-01:** ❌ D11; still receives the Paper theme (1.19)
- [ ] **5.A.12** `src/components/SVG/RNVI/**` — batch pass · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.A.13** `src/components/SVG/psoc/**` — verify from Phase 3 · **2026-10-01:** ❌ see 3.4

### Wave B — Auth / Settings / Profile

**Status (2026-10-01):** ❌ superseded by D11 (see Phase 5).

- [ ] **5.B.1** `src/screens/Login/AuthNavigator/Welcome.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.B.2** `src/screens/Login/AuthNavigator/Login.js` (verify from 2.9a) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.B.3** `src/screens/Login/AuthNavigator/Register.js` · **2026-10-01:** ❌ no such file (auth screens: `Welcome`, `Login`, `ForgotPassword`, `Dealer`, `Customer`, `BetaUser`)
- [ ] **5.B.4** `src/screens/Login/AuthNavigator/OTP.js` · **2026-10-01:** ❌ no such file
- [ ] **5.B.5** `src/screens/Login/AuthNavigator/ForgotPass.js` · **2026-10-01:** ❌ D11 — the file is `ForgotPassword.js`
- [ ] **5.B.6** `src/screens/StartupScreen.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.B.7** `src/screens/Common/Settings/index.js` (verify from 2.9b) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.B.8** `src/screens/Common/Profile/**` (all files including `SelectStateBS.js`) · **2026-10-01:** ❌ D11 — v1, never restyled

### Wave C — Core commerce

**Status (2026-10-01):** ❌ superseded by D11 (see Phase 5).

- [ ] **5.C.1** `src/screens/Dealer/Orders/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.2** `src/screens/Dealer/Orders/components/OneOrder.js` (verify from 2.9d) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.3** `src/screens/Dealer/Orders/components/OTPmodule.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.4** `src/screens/Dealer/Orders/**` rest · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.5** `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` (verify from 2.9e) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.6** `src/screens/Dealer/NewInvoice/newComp/SummaryModal.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.7** `src/screens/Dealer/NewInvoice/**` rest · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.8** `src/screens/Dealer/Payments/**` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.9** `src/screens/Customer/Orders/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.10** `src/screens/Customer/Orders/components/EmergencyOTPBS.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.11** `src/screens/Customer/Orders/**` rest · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.12** `src/screens/Customer/NewOrder/components.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.13** `src/screens/Customer/NewPayment/index.js` (verify from 2.9f) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.14** `src/screens/Customer/Dealers/DealerSettings/index.js` (verify from 2.9g) · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.15** `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js` · **2026-10-01:** ❌ D11 — no such file now: `c5e87820` (2026-06-04) folded the On A/c payment into the voucher flow (`src/screens/Customer/NewPayAck/`, v1, never restyled)
- [ ] **5.C.16** `src/screens/Customer/Dealers/BSheets/AddDealer.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.17** `src/screens/Customer/Dealers/BSheets/TCSTDSSettings.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.18** `src/screens/Customer/Payments/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.19** `src/screens/Common/Orders/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.20** `src/screens/Common/Orders/components/newDesign.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.21** `src/screens/Common/Orders/components/FilterList.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.22** `src/screens/Common/Orders/bottomsheet/filter.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.23** `src/screens/Common/Orders/bottomsheet/dateRange.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.24** `src/screens/Common/Payments/components/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.C.25** `src/screens/Common/_Voucher_/BS/index.js` · **2026-10-01:** ❌ D11 — v1, never restyled

### Wave D — Remaining

**Status (2026-10-01):** ❌ superseded by D11 (see Phase 5).

- [ ] **5.D.1** `src/screens/Dealer/Customers/CustSettings.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.2** `src/screens/Dealer/Customers/SetDiscBS.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.3** `src/screens/Dealer/ProductDates/SetProductRate.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.4** `src/screens/Dealer/Dashboard/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.5** `src/screens/Dealer/Products/**` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.6** `src/screens/Dealer/Requests/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.7** `src/screens/Dealer/Reports/**` · **2026-10-01:** ❌ no such folder (reports live in `Common/Reports`)
- [ ] **5.D.8** `src/screens/Dealer/Vehicles/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.9** `src/screens/Dealer/Drivers/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.10** `src/screens/Dealer/Users/**` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.11** `src/screens/Customer/Dashboard/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.12** `src/screens/Customer/Vehicles/**` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.13** `src/screens/Customer/Requests/**` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.14** `src/screens/Customer/Reports/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.15** `src/screens/Customer/Users/**` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.16** `src/screens/Common/Reports/DailyReport/components.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.17** `src/screens/Common/Reports/TcsTds/Render/MonthExcel.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.18** `src/screens/Common/Reports/**` rest · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.19** `src/screens/Common/DailySummary/component/index.js` (verify from 2.9c) · **2026-10-01:** ❌ replaced by the v2 `Common/DailySummary`; the v1 file stays as the toggle fallback
- [ ] **5.D.20** `src/screens/Common/Accounts/components.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.21** `src/screens/Common/RelationList/RelationCreditBS.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.22** `src/screens/Common/Dashboard/**` · **2026-10-01:** ❌ no such folder
- [ ] **5.D.23** `src/navigation/Dealer/DrawerContent.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.24** `src/navigation/Dealer/TrnTab.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.25** `src/navigation/Dealer/Main.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.26** `src/navigation/Customer/DrawerContent.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.27** `src/navigation/Customer/TrnTab.js` · **2026-10-01:** ❌ D11 — v1, never restyled
- [ ] **5.D.28** `src/navigation/Common/CustomHeader.js` · **2026-10-01:** ❌ D11; its bar now grows with the text (`3a0b83b1`, `b9cde5cd`)

### Wave exit gates

**Status (2026-10-01):** ❌ superseded by D11 (see Phase 5).

- [ ] **5.E.1** After Wave A: `grep -rn "import { Text } from 'react-native'" src/components` → only `src/theme/components/AppText.js` · **2026-10-01:** ❌ D11 (1 component file imports RN `Text`: `Input/BaseInput.js:4`; `Input/CustomInput.js` takes Paper’s `Text`)
- [ ] **5.E.2** After Wave D: same grep across `src/screens` → empty · **2026-10-01:** ❌ D11
- [ ] **5.E.3** After Wave D: `grep -rn "fontSize:" src/screens src/components` → empty · **2026-10-01:** ❌ D11 — 1,081 numeric `fontSize:` in v1 screens / components; 0 in v2
- [ ] **5.E.4** After Wave D: `yarn lint` → zero warnings from `no-restricted-imports` or `no-hardcoded-colors` · **2026-10-01:** ❌ D11; neither rule exists app-wide

## Phase 6 — Polish

**Status (2026-10-01):** 🟡 mostly open — ✅ 1 · 🟡 4 · ⬜ 8 · ⏸ 2 · ❔ 2 · ❌ 1 of 18.

- [ ] **6.1** Install `wcag-contrast` or `color2k` · **2026-10-01:** ⬜ no contrast library; a house WCAG helper would avoid a dependency (02 log rule)
- [ ] **6.1a** Write `src/theme/__tests__/contrast.test.js` · **2026-10-01:** ⬜ no `contrast.test.js` among the 20 theme test files; see T04-N2
- [ ] **6.1b** All contrast tests pass in `yarn test` · **2026-10-01:** ⬜ follows 6.1a
- [ ] **6.2** Escalate `no-restricted-imports` to `error` · **2026-10-01:** ⬜ the bare-`Text` rule does not exist (2.13)
- [ ] **6.2a** Escalate `no-hardcoded-colors` to `error` · **2026-10-01:** 🟡 `error` in the v2 scope (`eslint.config.js:49-60`); app CI runs no lint (`X-CI-2` in tasks_02)
- [ ] **6.3** Custom font decision (Option A/B/C) — implement choice · **2026-10-01:** ⏸ F-APP-3 “deliberately not: custom fonts” (Q2); Roboto Condensed already used for figures
- [ ] **6.4** Add `theme` slice to `redux-persist` whitelist (confirm from 1.15a) · **2026-10-01:** ⏸ F-APP-3 “deliberately not: redux-persist for theme”; `redux-persist` is not a dependency
- [ ] **6.5** Remove duplicate theme toggle from `src/components/VersionInfo/index.js` · **2026-10-01:** ⬜ `VersionInfo/index.js:87-98,381-385` still opens a theme modal
- [ ] **6.6** Accessibility audit — TalkBack on top-20 screens · **2026-10-01:** ❔ no TalkBack pass recorded; v2 has 29 roles, 25 labels, 2 live regions
- [ ] **6.6a** Accessibility audit — VoiceOver on top-20 screens · **2026-10-01:** ❔ no VoiceOver pass recorded (as 6.6)
- [ ] **6.6b** Reduced motion respect — audit reanimated usage · **2026-10-01:** ⬜ 0 reduce-motion reads in app code; v2 animates only its bottom sheets
- [ ] **6.7** Apple-grade polish checklist (spacing rhythm, alignment, icon sizes, elevations, haptics, motion tokens, tap targets, focus states) · **2026-10-01:** 🟡 v2: spacing tokens, 44 pt `TARGET` + hit slop; no icon-size / motion tokens, haptics, focus states
- [ ] **6.8** (Optional) Material You dynamic color via `@pchmn/expo-material3-theme` · **2026-10-01:** ⬜ not installed; Q4 open
- [ ] **6.9** Add high-contrast theme as extensibility stress test · **2026-10-01:** ⬜ two themes only (`themes/index.js:9`)
- [ ] **6.10** Finalize `src/theme/README.md` (full developer docs) · **2026-10-01:** 🟡 see 2.12
- [x] **6.10a** Update `AI.md` with theming conventions section · **2026-10-01:** ✅ `AI.md:46-51`, `AI.md:65-76`, `AI.md:155-157`
- [ ] **6.11** Write `scripts/export-design-tokens.js` for Figma handoff · **2026-10-01:** 🟡 `.design-sync/web/build.mjs` derives `tokens.css` for claude.ai/design (`d0fbd081`); no Figma Tokens JSON
- [ ] **6.12** Write `docs/todos/design-system/RETRO.md` — migration retrospective · **2026-10-01:** ❌ no app-wide migration under D11; the redesign keeps per-screen decision logs

## New — from the app v2 / API v4 review (2026-10-01)

**Status (2026-10-01):** 🆕 three items the review found; the full rows (why, evidence, size, dependencies) are in the New tasks table of [00_README.md](./00_README.md).

- [ ] **X-APP-6** Replace the 34 `border*Width: 0.5` sites in 18 v1 files — stacked rows onto `helpers/RowDivider`, outlines onto a whole-pixel width — test-first, then a device look at a fractional density · 🆕 (Phase 4)
- [ ] **T04-N1** Decide the Android Bold Text fix: React Native's Android text measurement ignores `fontWeightAdjustment`, so text tails clip on every screen · 🆕 (Phase 4)
- [ ] **T04-N2** Light-mode contrast of `success` text in v2 (≈ 2.1:1 on its own wash, ≈ 2.3:1 on white): choose a text-grade green token or accept it, and pin the result with 6.1a · 🆕 (Phase 6)

---

## Open questions (resolve before starting the phase)

**Status (2026-10-01):** Q1 and Q3 are answered by the code (both “no”); Q2 and Q4 are ⏸ open; Q5 is ❔.

- [x] **Q1** Path alias: is `babel-plugin-module-resolver` already installed? If yes use `~/theme`; if no, use relative imports. (Phase 2.7) · **2026-10-01:** ✅ answered: no — absent from `package.json` and `babel.config.js`; relative imports
- [ ] **Q2** Font decision (OpenSans adoption vs retirement) — design team sign-off required before Phase 6.3 · **2026-10-01:** ⏸ open — fonts kept out of F-APP-3; see 6.3
- [x] **Q3** Is `redux-persist` currently wired? If not, setup is added as a prerequisite sub-task to Phase 1.15a · **2026-10-01:** ✅ answered: no — `redux-persist` is not a dependency
- [ ] **Q4** Does the team want Material You dynamic color on Android 12+, or stick with named themes only? (Phase 6.8) · **2026-10-01:** ⏸ open — not raised in the redesign
- [ ] **Q5** Which low-end Android device is the reference for the 2x + bold testing? Acquire or allocate. (Phase 4.8) · **2026-10-01:** ❔ open — the recorded runs used iOS simulators and a Pixel Fold emulator

---

## Estimated effort (rough order-of-magnitude)

**Status (2026-10-01):** the estimate no longer maps to the work: Phases 1–3 landed for the v2 scope as F-APP-3 (`cc5413c7` → `87bde4f9`, both 2026-09-04) and the type scale on 2026-09-06/07; Phase 5’s 10–15 days do not apply under D11.

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
