# Phase 4 — Android Text Clipping Fix + Uncapped Layout Migration

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Done for v2 in a stronger form than planned — the type scale F-APP-7 makes text set the box (no fixed height on a v2 text container, pairs stack, digits never wrap), and there is no `includeFontPadding` anywhere in the app — while the v1 punch list is superseded by D11. Of the 10 steps: 2 done, 1 partly, 2 to do, 4 dropped or superseded, 1 unverifiable. The device runs found two Android problems the plan did not foresee: Android 15's bounds-based line breaking (fixed app-wide, 🆕 below) and Bold Text tail clipping (open, 🆕 T04-N1); this doc also owns the hairline sweep 🆕 X-APP-6. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Goal**: Make the app render correctly at maximum system font scale (Android 2x + bold, iOS AX5) with **zero** text clipping on low-end devices.

**Entry criteria**: Phase 2 complete. `<AppText>` shipped. `useContainerMinHeight` hook available.

**Exit criteria**:

- **Zero** `height: N` containing text in `src/screens/` or `src/components/` (excluding images, icons, and SVG viewports)
- Every text-bearing row/button/input has `minHeight` instead of `height`
- `lineHeight / fontSize >= 1.25` for every typography variant (audit `src/theme/tokens/typography.js`)
- No `includeFontPadding: false` in the codebase unless justified by a comment pointing to a specific bug
- The 15 canary screens from Phase 2 pass the AX5 + Android 2x bold test
- A physical low-end Android device (or a low-end Android emulator) is used to verify the fix

---

## Why this phase is necessary

**Status (2026-10-01):** ❔ #45660 is upstream and cannot be checked from the repos. Manifestations 2 and 3 are handled for v2 by F-APP-7; the two later findings are listed at the end of this doc.

Per `01_RESEARCH.md §5`, the Android text clipping bug (GitHub [#45660](https://github.com/facebook/react-native/issues/45660)) is **not fixed upstream**. Reports span RN 0.73.9 → 0.78, and we're on 0.84.1 which is still affected. The bug has three manifestations:

1. **Top/bottom trim** — ascenders/descenders of bold text clip when the native line box is shorter than the scaled glyph
2. **Fixed-height clipping** — any `height: N` container holding text truncates when text grows
3. **Horizontal overflow** — tight `flexDirection: 'row'` layouts push text off-screen when it grows

Our uncapped font scaling decision means we hit all three at the largest user settings. This phase fixes the root causes.

---

## Step 4.1 — Audit + fix `tokens/typography.js` ratios

**Status (2026-10-01):** ⬜ the display roles are still 36 / 44, 45 / 52, 57 / 64 (`src/theme/tokens/typography.js:9-29`); no v2 code uses a display role yet. `titleLarge` is 22 / 28 in code, not 30 (ratio 1.27).

Verify every variant: `lineHeight / fontSize >= 1.25`. Current values from Phase 1:

| Variant        | size | lineHeight | ratio   |
| -------------- | ---- | ---------- | ------- |
| displayLarge   | 57   | 64         | 1.12 ⚠️ |
| displayMedium  | 45   | 52         | 1.16 ⚠️ |
| displaySmall   | 36   | 44         | 1.22 ⚠️ |
| headlineLarge  | 32   | 40         | 1.25 ✅ |
| headlineMedium | 28   | 36         | 1.29 ✅ |
| headlineSmall  | 24   | 32         | 1.33 ✅ |
| titleLarge     | 22   | 30         | 1.36 ✅ |
| titleMedium    | 16   | 24         | 1.50 ✅ |
| titleSmall     | 14   | 20         | 1.43 ✅ |
| bodyLarge      | 16   | 24         | 1.50 ✅ |
| bodyMedium     | 14   | 20         | 1.43 ✅ |
| bodySmall      | 12   | 16         | 1.33 ✅ |
| labelLarge     | 14   | 20         | 1.43 ✅ |
| labelMedium    | 12   | 16         | 1.33 ✅ |
| labelSmall     | 11   | 16         | 1.45 ✅ |

The 3 display variants are borderline. **Fix**: bump their lineHeight to the safe ratio:

```js
displayLarge:   { fontSize: 57, lineHeight: 72, /* ... */ }, // was 64
displayMedium:  { fontSize: 45, lineHeight: 58, /* ... */ }, // was 52
displaySmall:   { fontSize: 36, lineHeight: 46, /* ... */ }, // was 44
```

This is a deviation from M3 but worth it for Android safety. Displays are rare and visual impact is minimal.

## Step 4.2 — Global grep for fixed-height text containers

**Status (2026-10-01):** ❌ D11 — no v1 punch list is needed; v1 has 187 `height: N` literals in 114 files (not all on text). The two `height` literals in v2 are a stepper dash and a measure-only ghost, neither holding text.

```sh
# This is the hunt list
grep -rn "height: [0-9]" src/screens src/components | grep -v "node_modules\|SVG\|Image\|svg"
```

The audit found **48+** instances. Produce a spreadsheet with columns: file, line, current height, replacement strategy. Strategies:

| Current                                              | Replacement                                                                                         |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `height: 40` on a button-like pill with Text         | `minHeight: 40, paddingVertical: 8, justifyContent: 'center'`                                       |
| `height: 48` on an input wrapper                     | `minHeight: 48, paddingVertical: 12`                                                                |
| `height: 56` on an input (Paper TextInput default)   | `minHeight: 56` (Paper's own `<TextInput>` handles scaling; wrapper just needs flex)                |
| `height: 50` on a list row                           | `minHeight: 50, flexShrink: 0` (prevent collapse in tight flex parents)                             |
| `height: 60` on a bottom sheet handle or date picker | `minHeight: 60` **or** explicitly `allowFontScaling={false}` if the container is a non-text control |

**Special case**: picker wheels, carousel items, and other components that _need_ a fixed logical height (for scroll math) should set `allowFontScaling={false}` on the labels inside. This is legitimate and commented.

## Step 4.3 — Critical components migration (from audit)

**Status (2026-10-01):** ❌ D11 — the eleven v1 files keep their fixed heights (lines moved, e.g. `src/screens/Login/AuthNavigator/Login.js:833`, `src/components/Input/IconInput.js:44`); the v2 screens were built to F-APP-7 instead.

| File                                                 | Line | Current                       | Action                                                                          |
| ---------------------------------------------------- | ---- | ----------------------------- | ------------------------------------------------------------------------------- |
| `src/screens/Customer/Payments/index.js`             | 498  | `height: 40`                  | → `minHeight: 40, paddingVertical: 8`                                           |
| `src/screens/Customer/Dealers/BSheets/AddDealer.js`  | 405  | `height: 40`                  | → `minHeight: 40, paddingVertical: 8`                                           |
| `src/screens/Login/AuthNavigator/Login.js`           | 810  | `height: 40`                  | → `minHeight: 40, paddingVertical: 8`                                           |
| `src/screens/Common/Profile/SelectStateBS.js`        | 518  | `height: 40`                  | → `minHeight: 40, paddingVertical: 8`                                           |
| `src/screens/Dealer/Orders/components/OneOrder.js`   | 382  | `const hght = { height: 50 }` | → `{ minHeight: 50, justifyContent: 'center' }`                                 |
| `src/screens/Common/Orders/bottomsheet/dateRange.js` | 416  | `height: 60`                  | → `minHeight: 60, paddingVertical: 12`                                          |
| `src/components/DatePicker/index.js`                 | 920  | `height: 60` (iOS picker)     | iOS picker is platform, keep `height`, ensure labels `allowFontScaling={false}` |
| `src/components/Input/CustomInput.js`                | 468  | `height: 56`                  | → `minHeight: 56` + ensure label overflow handled                               |
| `src/components/Input/IconInput.js`                  | 44   | `height: 48`                  | → `minHeight: 48, paddingVertical: 10`                                          |
| `src/components/Input/BS/BSheetInput.js`             | 42   | `height: 48`                  | → `minHeight: 48, paddingVertical: 10`                                          |
| `src/components/Input/IconLabelInput.js`             | 42   | `height: 48`                  | → `minHeight: 48, paddingVertical: 10`                                          |

For inputs: verify icon + text + clear button still align vertically after the change. Use `alignItems: 'center'` on the row container.

## Step 4.4 — Row layout discipline

**Status (2026-10-01):** ✅ for the v2 scope — `AI.md:72-76` ("digits never wrap; pairs stack"), applied in both v2 screens (money tiles stack by measured width, `src/screens/v2/Dealer/Customers/layout.js:171`; figures stay on one line with `numberOfLines={1}`); the top-20 v1 files are untouched by D11.

Many rows use `flexDirection: 'row'` with children that each have implicit widths (icon, label, value). When the label grows at 2x scale, it pushes the value off-screen. Fix pattern:

```jsx
// BEFORE — value gets pushed off-screen
<View style={{ flexDirection: 'row' }}>
  <Icon name="user" />
  <AppText variant="bodyMedium">{longUserName}</AppText>
  <AppText variant="labelMedium">{date}</AppText>
</View>

// AFTER — label shrinks with ellipsis, value stays visible
<AppBox flexDirection="row" alignItems="center">
  <Icon name="user" />
  <AppText variant="bodyMedium" numberOfLines={1} ellipsizeMode="tail" style={{ flex: 1, marginHorizontal: 8 }}>
    {longUserName}
  </AppText>
  <AppText variant="labelMedium" numberOfLines={1}>
    {date}
  </AppText>
</AppBox>
```

Rules of thumb for every row:

- Text that can wrap → `flex: 1`, no `numberOfLines`
- Text that must stay on one line → `flex: 1` (or `flexShrink: 1`), `numberOfLines={1}`, `ellipsizeMode="tail"`
- Side elements (icons, small labels) → `flexShrink: 0`

Apply this across the top-20 text-density files (audit §Text-density hotspots) plus the 48 fixed-height files.

## Step 4.5 — Bold-text-on-Android audit

**Status (2026-10-01):** 🟡 v2 still has three `fontWeight: '700'` literals (`src/screens/v2/Dealer/Customers/components/SortMenu.js:169`, `src/screens/v2/Common/DailySummary/components/OrderRow.js:238,256`), which the guard does not cover; v1 (289 bold or numeric weights) is untouched by D11. The OS Bold Text setting is T04-N1 below.

Every `fontWeight: 'bold'` in Android preview mode at scale 2x is a potential clip site. After Phase 2's variant migration, most bolds are gone (they're now `titleMedium` / `titleSmall` with weight 500). Remaining manual `fontWeight: 'bold'` usages need to be audited:

```sh
# Find remaining bold usages (after Phase 2 migration)
grep -rn "fontWeight: 'bold'\|fontWeight: 'Bold'\|fontWeight: '700'" src/screens src/components
```

For each:

1. Replace with the closest variant (`titleSmall` for 14px bold, `titleMedium` for 16px bold, `titleLarge` for 22px bold)
2. If the use case is a one-off accent that shouldn't be a variant, use `<AppText variant="bodyMedium" style={{ fontWeight: '600' }}>` — semibold (600) is safer than bold (700) on Android
3. Verify no `includeFontPadding: false` on the same element

## Step 4.6 — `adjustsFontSizeToFit` use cases

**Status (2026-10-01):** ❌ superseded — v2 text never shrinks (`AI.md:65-71`: only money figures in a fixed column may, never below 1×, and the Daily Summary card is undecided, `SummaryCard.js:107-108`); the header bar grows with the text instead of shrinking it (`src/navigation/Common/headerMetrics.js:33-37`, `3a0b83b1`).

For legitimately constrained components (tab labels, navigation headers, button labels in tight row layouts), use `adjustsFontSizeToFit` with a safe floor:

```jsx
<AppText
  variant="labelLarge"
  numberOfLines={1}
  adjustsFontSizeToFit
  minimumFontScale={0.85}
>
  {buttonLabel}
</AppText>
```

Candidates: bottom-tab labels, app-bar titles, chip labels. Not body text — body text should wrap.

## Step 4.7 — iOS `dynamicTypeRamp` bindings (optional polish)

**Status (2026-10-01):** ⬜ 0 uses. Caution before adopting: v2's box maths assumes one linear `fontScale` for every role (`src/theme/scale.js:68-99`), which per-role ramps would break.

On iOS specifically, set `dynamicTypeRamp` on AppText to tie into Apple's native Dynamic Type ramp. This makes iOS handle scaling more elegantly:

```jsx
// AppText forwards dynamicTypeRamp through to the underlying <Text>
// Consumers can opt in:
<AppText variant="headlineMedium" dynamicTypeRamp="title1">...
<AppText variant="bodyLarge" dynamicTypeRamp="body">...
```

Map our MD3 variants to Apple's ramps (defaults for iOS):

| Our variant                 | Apple ramp    |
| --------------------------- | ------------- |
| `displayLarge/Medium/Small` | `largeTitle`  |
| `headlineLarge`             | `title1`      |
| `headlineMedium`            | `title2`      |
| `headlineSmall`             | `title3`      |
| `titleLarge`                | `title3`      |
| `titleMedium`               | `headline`    |
| `titleSmall`                | `subheadline` |
| `bodyLarge`                 | `body`        |
| `bodyMedium`                | `callout`     |
| `bodySmall`                 | `footnote`    |
| `labelLarge`                | `subheadline` |
| `labelMedium`               | `footnote`    |
| `labelSmall`                | `caption1`    |

Hardcode these defaults inside `AppText.js` keyed by variant name. Consumers can override per-use.

## Step 4.8 — Test matrix

**Status (2026-10-01):** ❔ device-only; the recorded runs (02-foundations) used iOS simulators at AX-L (2.143×) and a Pixel Fold emulator, not a low-end phone (Q5).

For the top-20 text-density screens + the 48 fixed-height files + the 5 canary screens, run this matrix:

| Device                             | Font scale          | Bold text | Expected                                            |
| ---------------------------------- | ------------------- | --------- | --------------------------------------------------- |
| iPhone SE (small)                  | Default             | off       | Baseline                                            |
| iPhone SE                          | Largest regular     | off       | Text grows, no clip                                 |
| iPhone SE                          | AX5 (accessibility) | off       | Text very large, layouts adapt                      |
| Pixel 4a (low-end-ish)             | Default             | off       | Baseline                                            |
| Pixel 4a                           | Largest (2x)        | off       | Text grows, no clip                                 |
| Pixel 4a                           | Largest             | **ON**    | **The target of this phase** — no clip, no truncate |
| Android 2GB emulator (lowest tier) | Largest             | ON        | Same as above, plus no crash / OOM                  |

Log any issues per screen. Fix loop until all pass.

## Step 4.9 — Performance re-check

**Status (2026-10-01):** ❌ nothing to re-check: the v1 lists did not change (D11); the v2 lists' performance work lives in the redesign.

Phase 2 changed the hierarchy (Box primitives add a few more views). Phase 4 adds `minHeight` + padding which changes layout calculation slightly. Re-run the existing FlatList / FlashList perf benchmarks (commits `1326ca29` in recent history show you've already migrated to FlashList on key screens) to confirm no regression on Orders, Payments, Products, Vehicles, Dealers, Customers lists.

## Step 4.10 — Document the pattern

**Status (2026-10-01):** ✅ in `AI.md:65-76` and `docs/testing.md:440` ("Type scale — text sets the box"), not in a `src/theme/README.md`; v2 allows no `allowFontScaling={false}` exception at all.

Append to `src/theme/README.md` a "Layout rules for uncapped font scaling" section:

1. Never use `height: N` on text-bearing containers. Use `minHeight: N` + padding.
2. Rows with mixed content need `flex: 1` on the growable child and `numberOfLines` + `ellipsize` on fixed-line children.
3. `includeFontPadding: false` is banned unless the PR description explains why.
4. `allowFontScaling={false}` is allowed only for: picker wheels, brand logos, measurement-critical components.
5. `adjustsFontSizeToFit` is for tight single-line constraints only, never body text.

---

## Phase 4 deliverables

**Status (2026-10-01):** 🟡 delivered for v2: the layout rules and their docs, the row discipline, the Android 15 text theme (unplanned). Not delivered: the display line heights, the iOS ramps, the device test logs; the v1 files are superseded.

| Artifact                        | File path                              |
| ------------------------------- | -------------------------------------- |
| Updated typography line heights | `src/theme/tokens/typography.js`       |
| Fixed fixed-height containers   | 48+ files (see audit list)             |
| Fixed row layouts               | Top-20 text-density screens            |
| iOS ramp bindings               | `src/theme/components/AppText.js`      |
| Layout rules doc                | `src/theme/README.md` append           |
| Test logs                       | Phase 4 retrospective in `10_TASKS.md` |

## Verification

**Status (2026-10-01):** ❔ the device part was not run here. The grep below returns 273 lines at `ea7e7222` (209 outside `__tests__`); the two in v2 are a stepper dash and a measure-only ghost, neither holding text.

```sh
# No fixed-height text containers (excluding known exceptions)
grep -rn "height: [0-9]" src/screens src/components | grep -v "SVG\|Image\|node_modules"
# Expected: empty after phase, or only legitimate picker exceptions

yarn android
# Set device: Android Settings → Display → Font size → Largest + Bold text ON
# Walk through top-20 screens, confirm no clipping
```

Manual: full test matrix from Step 4.8 executed on at least one physical low-end Android device.

## New items from the 2026-10-01 review

**Status (2026-10-01):** 🆕 one unplanned fix that is done, and two open tasks this phase owns. The same rows sit in the New tasks table of [00_README](./00_README.md).

- 🆕 ✅ **Android 15 line breaking** — since Android 15, a TextView in an app targeting SDK 35+ breaks lines by glyph bounds while React Native measures advances, so a Hindi label measured to fit wrapped onto a hidden second line. The app theme routes `textViewStyle` to `useBoundsForWidth=false` for every React Native text (`android/app/src/main/res/values/styles.xml:9,30-32`, `fe8799d5`, 2026-09-08), pinned by `src/i18n/__tests__/androidText.config.test.js`.

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-APP-6 | 🆕 Sweep the remaining 34 `border*Width: 0.5` sites in 18 v1 files: stacked-row dividers onto `stackedRowDivider`, box outlines onto a whole-pixel width (`StyleSheet.hairlineWidth` or 1 dp); test-first per file (as `vocTypesDividers.test.js`), then a device look at a fractional density | The sub-pixel divider bug: at density 2.625 a 0.5 dp border is one device pixel, and Yoga's rounding lets the next row paint over it (`src/helpers/RowDivider/index.js:3-41`; fixed in the voucher-type and invoice-type sheets, `7233c26b`, `bc94a345`). 34 sites remain, e.g. `src/screens/Common/Accounts/index.js:725,776,807,1029,1098` and `src/screens/Customer/NewOrder/components.js:601,964,1459,1477`; 0 in v2, which draws `HAIRLINE` 1 (`src/theme/layout.js:32`) | app | M | — (`helpers/RowDivider` exists) |
| T04-N1 | 🆕 Android Bold Text (`fontWeightAdjustment`) clips text tails on every screen, v1 and v2: React Native's Android text measurement ignores the weight adjustment, so the platform draws heavier text than was measured. Decide: carry a native patch that measures with the adjustment, track an upstream fix, or accept it | Seen on the device on 2026-09-08 (02-foundations, F-APP-10 amendment: "Process" and "Und" cut on the Orders screen). The code has no reading of it: 0 `fontWeightAdjustment` in the app, and `useBoldText` is always false on Android (`src/theme/provider/useBoldText.js:2-3`); no config switch exists | app | L | React Native upstream, or a decision to carry a patch |
