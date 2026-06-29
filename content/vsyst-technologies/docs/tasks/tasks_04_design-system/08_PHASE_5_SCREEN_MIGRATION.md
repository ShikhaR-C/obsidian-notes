# Phase 5 — Screen-by-Screen Migration

**Goal**: Convert every remaining screen and component from legacy `<Text>` + hardcoded styles to `<AppText>` + variants + semantic colors.

**Entry criteria**: Phases 1–4 complete. Foundation, typography, colors, and Android fixes in place. Lint rules active at `"warn"`.

**Exit criteria**:

- **Zero** `import { Text } from 'react-native'` in `src/screens/` or `src/components/` (exception: `src/theme/components/AppText.js` internals)
- **Zero** `fontSize` or `fontWeight` hardcoded in `StyleSheet.create` outside of `src/theme/`
- All 181 Text-using files have been touched
- All 348 `useTheme()` consumers either stay on react-native-paper's `useTheme` (fine, they still work) or migrate to `useAppTheme()` (preferred)
- The 86 direct-importers of `src/utils/Colors` have either migrated to `~/theme` or been verified as working through the shim

---

## Sequencing strategy

Migrate in **waves**, not alphabetically. Each wave is 1–2 weeks of work.

### Wave ordering rationale

- **Wave A** — shared components first. Fixing `src/components/` eliminates copied-down bugs in every consumer.
- **Wave B** — auth / startup / settings. Low traffic screens, easy to validate, and we're already touching some for theming work.
- **Wave C** — highest-impact screens (Dealer Orders, Dealer Invoices, Customer Orders). These carry the most eyeballs.
- **Wave D** — everything else.

---

## Wave A — Shared components (Phase 5.A)

Target: `src/components/` — ~256 files. Focus on reusable primitives first because every screen uses them.

### Priority list

1. `src/components/Prompt/index.js` — modal used everywhere (9 hardcoded colors)
2. `src/components/Input/CustomInput.js` — input wrapper (14 Text instances)
3. `src/components/Input/IconInput.js` — icon input (6 hardcoded colors)
4. `src/components/Input/IconLabelInput.js`
5. `src/components/Input/BS/BSheetInput.js`
6. `src/components/DatePicker/index.js` — 48 Text instances, iOS picker height concern
7. `src/components/VersionInfo/index.js` — 20 Text instances, contains a duplicate theme toggle (consolidate)
8. `src/components/NumberMeter/index.js` + `logic.js` — 14 Text instances, 10 hardcoded colors
9. `src/components/NoNetwork/Undraw.js` + siblings
10. `src/components/Error/ErrorBoundary.js`
11. `src/components/Error/RestartContext.js` — already touched in Phase 1 for nav theme
12. `src/components/SVG/RNVI/*` — vector icon wrappers (batch with grep/replace, mostly color props)
13. `src/components/SVG/psoc/*` — brand logos, already touched in Phase 3

For each component:

- Replace `<Text>` from react-native with `<AppText>` from `~/theme`
- Replace `<Text>` from react-native-paper with `<AppText>` unless the component specifically depends on Paper's features
- Lift hardcoded fontSize/fontWeight into a variant
- Remove hardcoded colors in favor of theme roles
- Convert fixed-height containers per Phase 4 rules
- Run against the test matrix

### Wave A exit

- All shared components pass the Android 2x + bold test
- Zero lint warnings in `src/components/`

---

## Wave B — Auth + Settings + Profile (Phase 5.B)

### Priority list

1. `src/screens/Login/AuthNavigator/Welcome.js` (4 hardcoded colors)
2. `src/screens/Login/AuthNavigator/Login.js` (810-line file, fixed height at 810)
3. `src/screens/Login/AuthNavigator/Register.js`
4. `src/screens/Login/AuthNavigator/OTP.js`
5. `src/screens/Login/AuthNavigator/ForgotPass.js`
6. `src/screens/StartupScreen.js`
7. `src/screens/Common/Settings/index.js` — already touched in Phase 1 for theme switching
8. `src/screens/Common/Profile/*` — all files including `SelectStateBS.js` (fixed height at 518)

### Wave B exit

- Auth flow fully themed
- Settings screen uses `useThemeSwitcher()` hook (Phase 1 deliverable)
- Profile flow passes contrast audit

---

## Wave C — Core commerce screens (Phase 5.C)

These are the screens users spend the most time on. **Highest impact, highest risk.** Test thoroughly.

### Dealer Orders

1. `src/screens/Dealer/Orders/index.js`
2. `src/screens/Dealer/Orders/components/OneOrder.js` (fixed height at 382)
3. `src/screens/Dealer/Orders/components/OTPmodule.js` (41 Text instances)
4. All sub-components under `src/screens/Dealer/Orders/`

### Dealer Invoices (New Invoice flow)

5. `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` (55 Text instances, 5 hardcoded colors)
6. `src/screens/Dealer/NewInvoice/newComp/SummaryModal.js` (53 Text instances)
7. All `src/screens/Dealer/NewInvoice/**`

### Dealer Payments

8. `src/screens/Dealer/Payments/BSheets/AttachInvs.js`
9. All `src/screens/Dealer/Payments/**`

### Customer Orders

10. `src/screens/Customer/Orders/index.js`
11. `src/screens/Customer/Orders/components/EmergencyOTPBS.js` (32 Text instances)
12. All `src/screens/Customer/Orders/**`

### Customer New Order

13. `src/screens/Customer/NewOrder/components.js` (41 Text instances, 7 hardcoded colors)

### Customer New Payment

14. `src/screens/Customer/NewPayment/index.js` (27 Text instances, 5 hardcoded colors)

### Customer Dealers (highest text density)

15. `src/screens/Customer/Dealers/DealerSettings/index.js` (**69 Text instances** — highest in app)
16. `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js`
17. `src/screens/Customer/Dealers/BSheets/AddDealer.js` (fixed height at 405)
18. `src/screens/Customer/Dealers/BSheets/TCSTDSSettings.js`

### Customer Payments

19. `src/screens/Customer/Payments/index.js` (fixed height at 498)

### Common Orders

20. `src/screens/Common/Orders/index.js`
21. `src/screens/Common/Orders/components/newDesign.js` (52 Text instances, 5 hardcoded colors)
22. `src/screens/Common/Orders/components/FilterList.js`
23. `src/screens/Common/Orders/bottomsheet/filter.js`
24. `src/screens/Common/Orders/bottomsheet/dateRange.js` (fixed height at 416)

### Common Payments

25. `src/screens/Common/Payments/components/index.js` (29 Text instances)

### Common Vouchers

26. `src/screens/Common/_Voucher_/BS/index.js` (42 Text instances)

### Wave C exit

- All top-20 text-density files migrated and tested at AX5 / Android 2x bold
- Contrast audit passes for every screen
- FlashList performance benchmarks stable

---

## Wave D — Remaining screens (Phase 5.D)

Everything not covered by Waves A–C. Work in alphabetical order within each role folder to avoid missing anything.

### Dealer role

- `src/screens/Dealer/Customers/CustSettings.js` (55 Text instances)
- `src/screens/Dealer/Customers/SetDiscBS.js` (contrast fixes from Phase 3)
- `src/screens/Dealer/ProductDates/SetProductRate.js`
- `src/screens/Dealer/Dashboard/*`
- `src/screens/Dealer/Products/*`
- `src/screens/Dealer/Requests/*`
- `src/screens/Dealer/Reports/*`
- `src/screens/Dealer/Vehicles/*`
- `src/screens/Dealer/Drivers/*`
- `src/screens/Dealer/Users/*`

### Customer role

- `src/screens/Customer/Dashboard/*`
- `src/screens/Customer/Vehicles/vehicleComponents/index.js`
- `src/screens/Customer/Vehicles/*`
- `src/screens/Customer/Requests/*`
- `src/screens/Customer/Reports/*`
- `src/screens/Customer/Users/*`

### Common

- `src/screens/Common/Reports/DailyReport/components.js` (62 Text instances)
- `src/screens/Common/Reports/TcsTds/Render/MonthExcel.js` (21 hardcoded colors)
- `src/screens/Common/Reports/*`
- `src/screens/Common/DailySummary/component/index.js` (36 Text instances)
- `src/screens/Common/Accounts/components.js` (27 Text instances)
- `src/screens/Common/RelationList/RelationCreditBS.js` (27 Text instances)
- `src/screens/Common/Dashboard/*`

### Navigation

- `src/navigation/Dealer/DrawerContent.js`
- `src/navigation/Dealer/TrnTab.js` (7 useTheme uses, 20+ inline rgb() strings)
- `src/navigation/Dealer/Main.js`
- `src/navigation/Customer/DrawerContent.js`
- `src/navigation/Customer/TrnTab.js`
- `src/navigation/Common/CustomHeader.js`

### Wave D exit

- Global grep for `import { Text } from 'react-native'` in `src/screens/` or `src/components/` returns only `src/theme/components/AppText.js`
- Global grep for `fontSize:` in StyleSheet.create returns zero matches
- Global grep for hex colors returns only `src/components/SVG/psoc/` and `src/theme/tokens/`

---

## Migration playbook (per file)

Apply this recipe to every file:

1. **Open the file**
2. **Replace imports**
   - `import { Text } from 'react-native'` → remove, add `import { AppText, useAppTheme, AppBox } from '~/theme'`
   - `import { Text } from 'react-native-paper'` → remove (use AppText)
3. **Replace `<Text style={...}>` with `<AppText variant="..." color="...">`**
   - Use the variant mapping table from `05_PHASE_2_TYPOGRAPHY.md`
4. **Replace hardcoded colors**
   - Hex → `theme.colors.X` or `<AppText color="X">`
   - rgba → `theme.colors.X` or `theme.fixed.backdrop` for overlays
5. **Replace `height: N`** (wrapping text) → `minHeight: N, paddingVertical: Y, justifyContent: 'center'`
6. **Audit flex rows** per Phase 4 §4.4 — add `flex: 1` / `numberOfLines` where needed
7. **Run `yarn lint`** — expect this file's warnings to drop to zero
8. **Visual diff** at default scale — must be identical to before
9. **Elevated scale test** — Android 2x + bold, iOS AX5, confirm no clipping
10. **Commit** — `refactor(theme): migrate <ScreenName> to AppText + semantic colors (APP-<ticket>)`

## Commit discipline

- One screen / component per commit (or one tightly-coupled pair — e.g., a screen + its only bottom sheet)
- Commits must compile and pass tests on their own
- Title format: `refactor(theme): migrate <screen> to design system`
- Body: mention variants used, hardcoded colors removed, fixed-height containers fixed

## Tracking

Each migrated file gets checked off in `10_TASKS.md`. Phase 5 is not "done" until every file in the audit is either migrated or explicitly marked "no text / no theme" (e.g., some API-only files in `src/store/`).

---

## Phase 5 deliverables

| Artifact                                        | Status |
| ----------------------------------------------- | ------ |
| Wave A — 13 priority shared components migrated | TBD    |
| Wave B — 8 auth/settings/profile files migrated | TBD    |
| Wave C — 26 commerce screens migrated           | TBD    |
| Wave D — remaining ~130 files migrated          | TBD    |
| Updated `10_TASKS.md` with per-file checkmarks  | TBD    |

## Verification

```sh
# After every wave:
grep -rn "import { Text } from 'react-native'" src/screens src/components  # should shrink each wave
grep -rn "fontSize:" src/screens src/components | grep -v "node_modules"    # should shrink each wave
yarn lint                                                                     # warnings trend → 0
yarn test
```

Post-wave: full AX5 + Android 2x bold walkthrough of the wave's scope. QA sign-off per wave.
