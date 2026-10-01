# Research: Design System Foundations

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Research, April 2026 — there are no tasks here; each section now says what the code did with it. Two verdicts no longer hold: the Restyle choice (§7, §8) was reversed on 2026-09-04, and §1's `letterSpacing` "bug" was never there. The rest still describes the platform. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

All claims are cited. Research was done April 2026. Any stars / versions / issue numbers are snapshots from that date.

## 1. Material Design 3 — Type Scale (authoritative)

**Status (2026-10-01):** the built roles (`src/theme/tokens/typography.js:8-114`, app `ea7e7222`) copy the legacy `fontObject`, which is Paper's MD3 table: `titleLarge` is 22 / 28 (not 30 as below), `bodyLarge` tracks 0.15 and `displayLarge` 0. The second note's bug claim is corrected in place.

Source: [m3.material.io/styles/typography/type-scale-tokens](https://m3.material.io/styles/typography/type-scale-tokens) (fetched via WebFetch, CSS custom properties extracted directly from the page).

Fifteen type roles. Each role has a font family, size (sp/px), weight, line height, and tracking (letter spacing).

| Role             | Size | Weight | Line height | Tracking |
| ---------------- | ---- | ------ | ----------- | -------- |
| `displayLarge`   | 57   | 400    | 64          | -0.25    |
| `displayMedium`  | 45   | 400    | 52          | 0        |
| `displaySmall`   | 36   | 400    | 44          | 0        |
| `headlineLarge`  | 32   | 400    | 40          | 0        |
| `headlineMedium` | 28   | 400    | 36          | 0        |
| `headlineSmall`  | 24   | 400    | 32          | 0        |
| `titleLarge`     | 22   | 400    | 30          | 0        |
| `titleMedium`    | 16   | 500    | 24          | 0.15     |
| `titleSmall`     | 14   | 500    | 20          | 0.1      |
| `bodyLarge`      | 16   | 400    | 24          | 0.5      |
| `bodyMedium`     | 14   | 400    | 20          | 0.25     |
| `bodySmall`      | 12   | 400    | 16          | 0.4      |
| `labelLarge`     | 14   | 500    | 20          | 0.1      |
| `labelMedium`    | 12   | 500    | 16          | 0.5      |
| `labelSmall`     | 11   | 500    | 16          | 0.5      |

**Note**: M3 2024+ uses weight 475 for display/headline when Google Sans is available. Since we're using `'System'` and later `'OpenSans'`, we stay at 400 for display/headline (the published M3 fallback weight).

**Note**: React-native-paper 5.x `MD3LightTheme.fonts` ships exactly this scale (naming matches). We do **not** need to re-type the whole table; we can spread `MD3LightTheme.fonts` and only override where needed. The existing `src/utils/Colors/index.js` `fontObject` is already very close ~~but has `letterSpacing: 0` for nearly everything — a bug vs. M3. We fix this in Phase 2.~~ — _2026-10-01:_ it has carried Paper's MD3 tracking since at least 2025-09-09 (0.1–0.5 on the title, body and label roles); only `displayLarge` (0 vs −0.25) and `bodyLarge` (0.15 vs 0.5) differ from the table above, as in Paper's own MD3 fonts.

## 2. Material Design 3 — Color Roles

**Status (2026-10-01):** 🟡 still about ten roles plus the custom keys — the built theme restates the legacy palette key for key (`src/theme/tokens/palette.js:9-56`); the full MD3 set is Phase 3 Step 3.1, ⬜.

Source: [m3.material.io/styles/color/roles](https://m3.material.io/styles/color/roles).

MD3 color roles (abbreviated — full list at source). Every role has an `onX` partner for contrast.

| Role                                                     | Purpose                                            |
| -------------------------------------------------------- | -------------------------------------------------- |
| `primary` / `onPrimary`                                  | Main brand actions (buttons, FABs, active states)  |
| `primaryContainer` / `onPrimaryContainer`                | Tonal variant for less-emphasized primary surfaces |
| `secondary` / `onSecondary`                              | Secondary accents (chips, filter surfaces)         |
| `secondaryContainer` / `onSecondaryContainer`            | Tonal variant                                      |
| `tertiary` / `onTertiary`                                | Contrasting accent (complementary to primary)      |
| `tertiaryContainer` / `onTertiaryContainer`              | Tonal variant                                      |
| `error` / `onError`                                      | Error states (validation, destructive)             |
| `errorContainer` / `onErrorContainer`                    | Tonal variant for inline errors                    |
| `background` / `onBackground`                            | Full-screen background                             |
| `surface` / `onSurface`                                  | Cards, sheets, dialogs                             |
| `surfaceVariant` / `onSurfaceVariant`                    | Muted surface (form fields, dividers backgrounds)  |
| `surfaceContainerLowest/Low/Default/High/Highest`        | Elevation-stratified surfaces (MD3 Expressive)     |
| `outline` / `outlineVariant`                             | Borders, dividers                                  |
| `inverseSurface` / `inverseOnSurface` / `inversePrimary` | Inverted color scheme for contrast snackbars etc.  |
| `shadow` / `scrim`                                       | Shadow color and modal backdrop                    |
| `surfaceTint`                                            | Tinted overlay for elevated surfaces               |

The existing codebase uses only ~10 of these. Phase 3 expands to the full set, mapping all existing ad-hoc colors (`link`, `success`, `antiText`, `white`, `black`, `gray`) to semantic MD3 roles.

## 3. Apple Human Interface Guidelines — Dynamic Type

**Status (2026-10-01):** v2 follows the OS text size through React Native's one `fontScale` (`src/theme/provider/useTypeScale.js:25-38`) and treats iOS's accessibility sizes as a breakpoint (`ACCESSIBILITY_FONT_SCALE` 1.786, `src/theme/scale.js:10`); `dynamicTypeRamp` has 0 uses.

Source: Default iOS Dynamic Type point sizes at the "Large" content size category (compiled from sarunw.com, useyourloaf.com, Apple headers):

| Text style    | Default pt | Weight       |
| ------------- | ---------- | ------------ |
| `largeTitle`  | 34         | Regular      |
| `title1`      | 28         | Regular      |
| `title2`      | 22         | Regular      |
| `title3`      | 20         | Regular      |
| `headline`    | 17         | **Semibold** |
| `body`        | 17         | Regular      |
| `callout`     | 16         | Regular      |
| `subheadline` | 15         | Regular      |
| `footnote`    | 13         | Regular      |
| `caption1`    | 12         | Regular      |
| `caption2`    | 11         | Regular      |

Key Apple design-thinking we borrow:

1. **Named roles, not sizes.** A designer says "use `body`," never "use 17pt." This is exactly what MD3 already gives us, so we adopt MD3 naming (superset, 15 roles vs Apple's 11).
2. **`headline` is semibold body.** Same size as body (17pt), heavier weight. We mirror this: `titleSmall`/`titleMedium` are 14/16 with weight 500, same size class as body but heavier.
3. **Dynamic Type scales up to ~310% at AX5.** Apple's accessibility sizes (AX1–AX5) scale far beyond the normal slider. Well-designed iOS apps survive this; we will too.
4. **`dynamicTypeRamp` prop on React Native `<Text>`** (iOS only) maps directly to Apple's text styles. We use this on iOS to tie into the platform's accessibility system automatically. See [reactnative.dev/docs/text](https://reactnative.dev/docs/text).

## 4. React Native `<Text>` Props — The Accessibility Toolkit

**Status (2026-10-01):** ✅ as decided, for v2: no `allowFontScaling` or `maxFontSizeMultiplier` in the app (pinned by `AppText.test.js:91-109`); Paper's menu cap lifted with `titleMaxFontSizeMultiplier` (`SortMenu.js:120`); `adjustsFontSizeToFit` only on the Daily Summary card, an open decision (`SummaryCard.js:107-108`).

Source: [reactnative.dev/docs/text](https://reactnative.dev/docs/text) (fetched directly).

| Prop                    | Platform                   | Default         | What it does                                                                                                                          |
| ----------------------- | -------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `allowFontScaling`      | iOS + Android              | `true`          | Whether text obeys the system accessibility font scale. Default is `true`. **We keep it true everywhere** — our decision is uncapped. |
| `maxFontSizeMultiplier` | iOS + Android              | `undefined`     | Caps scaling at a multiplier (≥1). **We leave it undefined** (no cap). Alternatively set to 0 explicitly.                             |
| `adjustsFontSizeToFit`  | iOS + Android              | `false`         | Shrinks text to fit. Useful for single-line constrained components like tab labels. Use sparingly in Phase 4.                         |
| `minimumFontScale`      | iOS + Android              | `1.0`           | Floor for `adjustsFontSizeToFit`. 0.85 is a safe default when needed.                                                                 |
| `numberOfLines`         | iOS + Android              | `0`             | Truncates after N lines. Pairs with `ellipsizeMode`.                                                                                  |
| `ellipsizeMode`         | iOS + Android              | `'tail'`        | Truncation strategy. **On Android, only `'tail'` works correctly when `numberOfLines` > 1** — important gotcha.                       |
| `dynamicTypeRamp`       | **iOS only**               | `'body'`        | Binds the text to a specific iOS Dynamic Type ramp. Makes iOS accessibility "just work."                                              |
| `textBreakStrategy`     | **Android only** (API 23+) | `'highQuality'` | Line break algorithm. Default is fine.                                                                                                |

### Official guidance on global text defaults

The RN docs are explicit: **do not use `Text.defaultProps`** to style text globally. Quote:

> "The recommended way to use consistent fonts and sizes across your application is to create a component `MyAppText` that includes them and use this component across your app."

This directly validates Phase 2's `<AppText>` wrapper approach.

## 5. Android Text Clipping Bug — Diagnosis

**Status (2026-10-01):** ❔ #45660 is upstream and cannot be checked from the repos; the app has 0 `includeFontPadding` (workaround 2 holds). Two later Android findings came from device runs: Android 15 line breaking by glyph bounds (fixed app-wide, `android/app/src/main/res/values/styles.xml:9,30-32`) and Bold Text tail clipping (open — T04-N1 in [00_README](./00_README.md)).

Source: [github.com/facebook/react-native/issues/45660](https://github.com/facebook/react-native/issues/45660) (fetched April 2026, still open, last activity October 2025).

**Symptom**: On Android (reports span RN 0.73.9–0.78, Android 12/13/14), text rendered by `<Text>` has unwanted top padding. Setting `includeFontPadding: false` removes the **bottom** padding only; the top padding persists. When bold weight + large system font scale are combined, the top of capital letters and descenders on g/p/q get **clipped**, especially in fixed-height containers and buttons.

**Root cause (inferred, not fixed upstream)**: Android's native `TextView` reserves line box space based on the font's intrinsic ascent/descent metrics. When React Native maps our `fontSize` + `lineHeight` through Yoga, the computed height on Android low-end devices can be ~1–2dp short of what the rasterizer needs for the scaled bold variant of the font.

**Workarounds from the issue thread**:

1. Set `lineHeight >= fontSize * 1.35` on every Text variant. This over-reserves enough vertical space that the clip doesn't happen even at 2x system font scale. MD3 tokens already give us ~1.25x–1.4x line heights — we only need to audit and fix the edge cases.
2. **Do not** set `includeFontPadding: false` globally — it makes the clip worse on Android because it removes the safety margin the OS adds.
3. Never use `height: N` on a container holding text. Always use `minHeight: N` with vertical padding. The container should grow with its text.
4. Avoid nested `<Text>` with different `lineHeight` values — this triggers a separate RN bug that truncates the child.

All four are Phase 4 tasks.

## 6. Ignite Cookbook — Production font-scaling pattern

**Status (2026-10-01):** ❌ not adopted as written: v2 reads the scale per render (`useTypeScale`) and tests state it (`renderScreen(ui, { fontScale })`); no navigator-option hooks, no dev display.

Source: [ignitecookbook.com/docs/recipes/AccessibilityFontSizes](https://ignitecookbook.com/docs/recipes/AccessibilityFontSizes/) (the open-source RN cookbook maintained by Infinite Red).

Pattern: a `useFontScaling()` hook that returns `TextProps` (an object with `allowFontScaling`, `maxFontSizeMultiplier`, `minimumFontScale`), plus matching hooks for the different navigators (stack header, drawer, bottom tab, top tab) that return `screenOptions` pre-bound with scaling props.

We adapt this pattern but simplify: since we're uncapped globally, our hook only needs to return `{ allowFontScaling: true }` plus a `DevFontScale` display-only helper for engineers to verify layout at various `PixelRatio.getFontScale()` values during development.

## 7. `@shopify/restyle` — Our Chosen Engine

**Status (2026-10-01):** ❌ reversed on 2026-09-04 (02-foundations decision log): latest release 2.4.5 of 2025-03-19, wildcard peer dependencies, RN 0.84 / React 19 unverified — so plain tokens + Paper's MD3 theme + `AppText` / `Box` / `Screen` on `StyleSheet` were built instead; not in `package.json`.

Source: Restyle's design overview (the "enterprise design system" choice per LogRocket / State of React Native 2025 survey).

**What Restyle gives us**:

- A single typed theme object (`src/theme/themes/base.js`) with keys: `colors`, `spacing`, `borderRadii`, `textVariants`, `breakpoints`.
- `createBox<Theme>()` — a `<Box>` primitive that accepts restyle props like `bg="surface"`, `p="m"`, `borderRadius="md"`. Props are validated against the theme at compile time (typed) and at runtime (warn if missing).
- `createText<Theme>()` — a `<Text>` primitive with `variant="bodyLarge"` that pulls the full font size/weight/lineHeight/letterSpacing bundle from the theme in one prop.
- `createRestyleComponent<Theme>()` — escape hatch for custom primitives.
- `ThemeProvider` — single source of truth, switches themes by swapping the provider's `theme` prop.
- Works with React Native's StyleSheet.create — doesn't replace it, composes with it.

**How it plays with react-native-paper**:

- Paper components (Button, Chip, Dialog, Card, FAB, Appbar, etc.) stay on `PaperProvider`'s theme. No conflict.
- Restyle owns the app-layer primitives (`<AppText>`, `<AppBox>`, custom cards, list rows, headers) and typography tokens.
- Both consume from the **same `src/theme/` source of truth** — we write a small adapter (`toPaperTheme(baseTheme)`) that shapes our theme into what `PaperProvider` expects. One theme file, two consumers.

**Install**:

```sh
yarn add @shopify/restyle
```

No native code. No `pod install`. No Android rebuild. Pure JS.

## 8. Library Landscape Decision Log

**Status (2026-10-01):** what was built is closest to the "Vanilla extending Paper" row, with the variant discipline supplied by a scoped ESLint block (`eslint.config.js:42-76`) instead of Restyle's types.

Options considered before picking Restyle:

| Library                              | Verdict                                                                                                                                                                                                        |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `@shopify/restyle`                   | **Chosen.** Typed theme + variants + Box/Text primitives, composes with existing StyleSheet.create, zero native deps.                                                                                          |
| `react-native-unistyles` v3.2.3      | Strong runner-up. Excellent no-rerender perf, JSI-based. Newer (2.8k ★), requires native setup (Nitro Modules). Higher risk for a 530-file migration.                                                          |
| `tamagui`                            | Great perf and extract-to-CSS on web. But it's a full UI kit that conflicts with react-native-paper. Rejected.                                                                                                 |
| `nativewind`                         | Tailwind-for-RN. Great if team prefers utility classes. Rejected — our team is `StyleSheet.create`-native.                                                                                                     |
| `dripsy`                             | Fine, but smaller community than Restyle. Rejected.                                                                                                                                                            |
| Vanilla extending Paper              | Viable but doesn't enforce variant discipline. Would require heavy lint rules to match Restyle's compile-time safety. Rejected.                                                                                |
| `@material/material-color-utilities` | **Optional.** Google's official MD3 palette generator. Lets us generate a full tonal palette from a single source color. Useful when adding new themes (Phase 6) — we can ship with hand-tuned palettes first. |

## 9. Outside-component theme access (the `StyleSheet.create` problem)

**Status (2026-10-01):** v2 keeps layout in static `StyleSheet.create` and applies token colours inline at render from `useAppTheme()` (e.g. `CustomerRow.js:101-106`) — Pattern A without `makeStyles`; `Box` / `AppText` play Pattern B's part; Pattern C (`runtime.js`) is not built.

`StyleSheet.create` runs **once at module load**, before any React context exists. You can't call `useTheme()` inside a `StyleSheet.create` call. This is a known React Native gotcha. Two patterns address it:

**Pattern A: Styles-as-function-of-theme.** Export a function, call it inside the component:

```js
const makeStyles = theme => StyleSheet.create({...});
// inside component:
const { colors } = useTheme();
const styles = useMemo(() => makeStyles(colors), [colors]);
```

Viable but verbose and allocates a new StyleSheet per render unless memoized.

**Pattern B: Restyle's `createBox` / `createText`.** The theme lookup happens at render time inside the primitive, not at module load. `<Box bg="surface" p="m">` is the idiomatic replacement for `<View style={styles.surface}>`. This is our default.

**Pattern C: Module-level theme singleton.** For pure utility functions (error handlers, formatters) that need a color outside of React, we expose a `getActiveTheme()` function from `src/theme/runtime.js` that reads the currently active theme from a plain module variable the provider updates on switch. Not React state — a simple mutable ref. Used only where no component context exists.

All three patterns are documented in Phase 1.

## Sources

- [m3.material.io/styles/typography/type-scale-tokens](https://m3.material.io/styles/typography/type-scale-tokens)
- [m3.material.io/styles/color/roles](https://m3.material.io/styles/color/roles)
- [reactnative.dev/docs/text](https://reactnative.dev/docs/text)
- [github.com/facebook/react-native/issues/45660](https://github.com/facebook/react-native/issues/45660)
- [ignitecookbook.com/docs/recipes/AccessibilityFontSizes](https://ignitecookbook.com/docs/recipes/AccessibilityFontSizes/)
- [oss.callstack.com/react-native-paper/docs/guides/theming](http://oss.callstack.com/react-native-paper/docs/guides/theming/)
- [github.com/jpudysz/react-native-unistyles](https://github.com/jpudysz/react-native-unistyles)
- [sarunw.com/posts/scaling-custom-fonts-automatically-with-dynamic-type](https://sarunw.com/posts/scaling-custom-fonts-automatically-with-dynamic-type/)
- [useyourloaf.com/blog/supporting-dynamic-type](https://useyourloaf.com/blog/supporting-dynamic-type/)
- [callstack.com/blog/react-native-android-accessibility-tips](https://www.callstack.com/blog/react-native-android-accessibility-tips)
- [blog.logrocket.com/unistyles-vs-tamagui-cross-platform-react-native-styles](https://blog.logrocket.com/unistyles-vs-tamagui-cross-platform-react-native-styles/)
