# Phase 2 — Typography

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Built for the v2 scope in F-APP-3 (2026-09-04) and the type scale F-APP-7 (2026-09-06/07): of the 13 steps, 6 are done, 1 partly, 2 to do and 4 dropped. `AppText` is the only text in v2 and never caps the OS text size; "text sets the box" replaced the plan's `minHeight` helper. The canary migrations were dropped — D11 never restyles a v1 screen — so the exit criteria about canaries and a codemod no longer apply. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Goal**: Ship `<AppText>` as the only way to render text. Enable uncapped font scaling. Fix the `letterSpacing` bug.

**Entry criteria**: Phase 1 complete. `src/theme/tokens/typography.js` exists with all 15 MD3 variants.

**Exit criteria**:

- `<AppText variant="...">` exists and is exported from `src/theme/components`
- `allowFontScaling={true}` (uncapped) is the default everywhere `<AppText>` is used
- `useFontScale()` hook exposes `PixelRatio.getFontScale()` with a dev overlay
- A codemod / migration doc exists so engineers can convert existing `<Text>` to `<AppText>` mechanically
- 5-10 "canary" screens migrated to `<AppText>` as proof of concept
- Paper components (`<Button>`, `<Appbar.Content>`, `<Chip>`, etc.) automatically pick up the new typography through the theme

---

## Step 2.1 — Build `<AppText>` via `createText`

**Status (2026-10-01):** ✅ without Restyle — `src/components/v2/AppText.js:24-53` renders Paper's `Text` with the role, a colour token and Hindi's line height (`:42`); it never sets `allowFontScaling` or `maxFontSizeMultiplier` (pinned by `AppText.test.js:91-109`).

```jsx
// src/theme/components/AppText.js
import { createText } from "@shopify/restyle";
import { forwardRef } from "react";

const RestyleText = createText();

const AppText = forwardRef(
  (
    {
      allowFontScaling = true,
      maxFontSizeMultiplier, // intentionally undefined = no cap
      includeFontPadding, // intentionally undefined = OS default (#45660 workaround)
      variant = "bodyMedium",
      ...rest
    },
    ref,
  ) => (
    <RestyleText
      ref={ref}
      variant={variant}
      allowFontScaling={allowFontScaling}
      maxFontSizeMultiplier={maxFontSizeMultiplier}
      {...rest}
    />
  ),
);

export default AppText;
```

Restyle's `createText` returns a themed `<Text>` that reads `variant` from `theme.textVariants` and resolves color props through `theme.colors`. No manual mapping needed.

**Why `allowFontScaling` defaults to `true`**: matches the RN default. A caller can opt out locally (e.g. for a brand logo mark that must not scale) with `allowFontScaling={false}`.

**Why `maxFontSizeMultiplier` is undefined**: this is our uncapped decision. Inheriting from parent is fine; there is no parent cap, so text scales freely.

**Why `includeFontPadding` is untouched**: per the Android clipping research (issue #45660), forcing `includeFontPadding: false` globally makes bold text clip worse on Android. Leave it alone.

## Step 2.2 — Build `<AppBox>`

**Status (2026-10-01):** ✅ as `Box` — `src/components/v2/Box.js:49`, token props (`p`, `m`, `gap`, `bg`, `radius`, `row`, `center`) on `StyleSheet`.

```jsx
// src/theme/components/AppBox.js
import { createBox } from "@shopify/restyle";
export default createBox();
```

Provides `<AppBox bg="surface" p="m" borderRadius="md" flexDirection="row" ...>` primitive for layout. Replaces most `<View style={...}>` usages over time.

## Step 2.3 — Build `useFontScale()` hook

**Status (2026-10-01):** ✅ as `useTypeScale` — `src/theme/provider/useTypeScale.js:25-38`, from `useWindowDimensions().fontScale` rather than `PixelRatio` plus a listener; a size change also remounts the screen (`src/components/v2/Screen.js:63`).

```js
// src/theme/hooks/useFontScale.js
import { useEffect, useState } from "react";
import { PixelRatio, AccessibilityInfo } from "react-native";

export const useFontScale = () => {
  const [scale, setScale] = useState(() => PixelRatio.getFontScale());

  useEffect(() => {
    const sub = AccessibilityInfo.addEventListener?.("change", () => {
      setScale(PixelRatio.getFontScale());
    });
    return () => sub?.remove?.();
  }, []);

  return scale;
};
```

Used by any component that needs to branch on current font scale (e.g., layout components that want to switch from row to column above 1.5x).

## Step 2.4 — Build `useContainerMinHeight()` helper

**Status (2026-10-01):** ✅ in another form — `lineHeightAt` / `boxHeight` (`src/theme/scale.js:68,86`: `ceil(lineHeight × fontScale)` + padding) through `useTypeScale().boxHeight`, instead of scaling a fixed base height.

```js
// src/theme/hooks/useContainerMinHeight.js
import { useFontScale } from "./useFontScale";

// Returns a minHeight that scales with user's font size preference.
// Replacement for hardcoded `height: 48` on text-bearing rows.
export const useContainerMinHeight = (baseHeight = 48) => {
  const scale = useFontScale();
  return Math.max(baseHeight, baseHeight * scale);
};
```

Phase 4 uses this extensively to migrate fixed-height containers.

## Step 2.5 — Build `<DevFontScaleBadge>`

**Status (2026-10-01):** ⬜ not built; the tests state the scale instead (`renderScreen(ui, { fontScale })`; 31 test files run at 2.143×).

A dev-only floating badge showing the current font scale and the calculated effective font sizes for debugging. Rendered only when `__DEV__` is true. Hooked into `<AppThemeProvider>` behind a dev flag.

```jsx
// src/theme/components/DevFontScaleBadge.js
import { useFontScale } from "../hooks/useFontScale";
import AppText from "./AppText";
import AppBox from "./AppBox";

export const DevFontScaleBadge = () => {
  if (!__DEV__) return null;
  const scale = useFontScale();
  return (
    <AppBox
      position="absolute"
      top={40}
      right={8}
      bg="errorContainer"
      p="xs"
      borderRadius="sm"
      zIndex={9999}
    >
      <AppText variant="labelSmall" color="onErrorContainer">
        scale: {scale.toFixed(2)}x
      </AppText>
    </AppBox>
  );
};
```

## Step 2.6 — Export barrel

**Status (2026-10-01):** ✅ `src/theme/index.js` and `src/components/v2/index.js`; there is no `~/theme` import path (Step 2.7).

```js
// src/theme/components/index.js
export { default as AppText } from "./AppText";
export { default as AppBox } from "./AppBox";
export { DevFontScaleBadge } from "./DevFontScaleBadge";

// src/theme/index.js (top-level barrel)
export * from "./components";
export * from "./hooks";
export { useAppTheme } from "./provider/useAppTheme";
export { useThemeSwitcher } from "./provider/useThemeSwitcher";
export { getActiveTheme } from "./provider/runtime";
export { THEMES } from "./themes";
```

Single import path: `import { AppText, AppBox, useAppTheme } from '~/theme';`

## Step 2.7 — Add path alias (optional but recommended)

**Status (2026-10-01):** ❌ skipped, as the step allows: `babel-plugin-module-resolver` is not installed (`babel.config.js:5-23`); v2 uses relative imports.

Babel config + jsconfig: `~/theme` → `src/theme`. Keeps imports clean across deep screen paths. `babel.config.js`:

```js
plugins: [["module-resolver", { alias: { "~/theme": "./src/theme" } }]];
```

Requires `babel-plugin-module-resolver` (check if already installed — some RN projects use it). If not desired, skip this step and use relative imports throughout.

## Step 2.8 — Update react-native-paper theme to use new typography

**Status (2026-10-01):** ✅ Paper's `fonts` come from the tokens (`src/theme/adapters/toPaperTheme.js:35-38`) and equal the legacy `fontObject` (`parity.test.js:57-69`), so nothing changed on screen; there was no `letterSpacing` bug to fix (02_AUDIT §1).

`src/theme/adapters/toPaperTheme.js` already spreads `base.textVariants` into `fonts`, so Paper's `<Button>`, `<Chip>`, `<Appbar.Content>`, `<Snackbar>`, etc. automatically pick up the new MD3 variants with correct `letterSpacing`. **This fixes the letterSpacing bug across every Paper component in the app for free.**

Verify by checking a Paper button renders with the new tracking values.

## Step 2.9 — Canary migrations (5-10 screens)

**Status (2026-10-01):** ❌ D11 — v1 screens are never restyled; the two v2 screens proved the approach. The v1 Daily Summary canary was replaced whole by the v2 `Common/DailySummary` screen.

Pick screens that collectively exercise all 15 variants. Migrate them manually from `<Text style={{ fontSize: 16, fontWeight: 'bold' }}>` to `<AppText variant="titleMedium">`. Candidates (pick at least one from each group):

| Category  | Screen                                                   | Why                                                             |
| --------- | -------------------------------------------------------- | --------------------------------------------------------------- |
| Auth      | `src/screens/Login/AuthNavigator/Login.js`               | High visibility, heavy text                                     |
| Common    | `src/screens/Common/Settings/index.js`                   | Easy win, short file, we touch it anyway for `useThemeSwitcher` |
| Common    | `src/screens/Common/DailySummary/component/index.js`     | Tables                                                          |
| Dealer    | `src/screens/Dealer/Orders/components/OneOrder.js`       | List row, contains fixed-height container (tests Phase 4 prep)  |
| Dealer    | `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` | Highest text density in Dealer                                  |
| Customer  | `src/screens/Customer/NewPayment/index.js`               | Form-heavy                                                      |
| Customer  | `src/screens/Customer/Dealers/DealerSettings/index.js`   | Highest text density in app (69 text elements)                  |
| Component | `src/components/Prompt/index.js`                         | Reused modal, migrating it pays off immediately                 |

For each canary:

1. Replace every `import { Text } from 'react-native'` with `import { AppText } from '~/theme'`
2. Convert each `<Text style={{ fontSize: X, fontWeight: Y }}>` to an `<AppText variant="...">` — use the mapping table below
3. Move layout styles to `<AppBox>` where natural
4. Remove inline `fontSize` / `fontWeight` from StyleSheet.create blocks
5. Verify visually: must look identical at `PixelRatio.getFontScale() === 1`

### Migration mapping cheat sheet

| Existing style                             | → Variant                                                                   |
| ------------------------------------------ | --------------------------------------------------------------------------- |
| `fontSize: 11`                             | `labelSmall`                                                                |
| `fontSize: 12, fontWeight: 'normal'`       | `bodySmall`                                                                 |
| `fontSize: 12, fontWeight: '500'`          | `labelMedium`                                                               |
| `fontSize: 14, fontWeight: 'normal'`       | `bodyMedium`                                                                |
| `fontSize: 14, fontWeight: '500'`          | `labelLarge` or `titleSmall` (label for buttons, title for section headers) |
| `fontSize: 16, fontWeight: 'normal'`       | `bodyLarge`                                                                 |
| `fontSize: 16, fontWeight: 'bold' / '500'` | `titleMedium`                                                               |
| `fontSize: 18, fontWeight: 'bold'`         | `titleMedium` bumped + custom override OR `titleLarge`                      |
| `fontSize: 20-22, fontWeight: 'bold'`      | `titleLarge`                                                                |
| `fontSize: 24`                             | `headlineSmall`                                                             |
| `fontSize: 28+`                            | `headlineMedium` / `headlineLarge`                                          |

Publish this table as `src/theme/README.md` for engineers.

## Step 2.10 — Audit fixed-height containers in canaries

**Status (2026-10-01):** ❌ with Step 2.9; v2 text containers carry no fixed height ("text sets the box", `AI.md:72-76`).

While migrating each canary screen, any `height: N` wrapping text gets converted to `minHeight: N` + `justifyContent: 'center'`. This is Phase 4 work "pulled forward" for the canary set to validate the approach before running it across the entire app.

## Step 2.11 — Test at elevated font scale

**Status (2026-10-01):** ❌ with Step 2.9 for the canaries; the v2 screens are checked at 1× and 2.143× in Jest (F-APP-7) and were looked at on simulators (02-foundations); a low-end Android device run is not recorded (❔).

For each canary screen, test:

- Normal scale (1.0x)
- iOS Settings → Accessibility → Display & Text Size → Larger Text → crank to max regular → relaunch app
- iOS Accessibility → Larger Text → toggle "Larger Accessibility Sizes" → crank to AX5
- Android Settings → Display → Font size → Largest (2x)
- Android Accessibility → Text and display → Bold text ON + Font size Largest

Each canary should:

- ✅ not clip text
- ✅ not overflow horizontally
- ✅ not hide content behind other components
- ✅ remain tappable (minimum 44pt touch target)

Log any issues per screen. These become Phase 4 fix tickets.

## Step 2.12 — Write dev docs

**Status (2026-10-01):** 🟡 no `src/theme/README.md`; the rules are in `docs/testing.md:420-1073` ("Theme and primitives", "Type scale", "Window classes", "Language") and `AI.md:46-76`; no variant cheat sheet was needed, as v2 names a role directly.

Create `src/theme/README.md` (developer-facing) with:

- How to import `AppText`, `AppBox`, `useAppTheme`
- The variant cheat sheet
- The rule: "Never use `<Text>` from react-native. Always `<AppText>`."
- The rule: "Never hardcode `fontSize` or `fontWeight`. Use variants."
- How to add a new theme

Add to `AI.md` (the project's AI conventions file) a new section: "Typography and theming — use `~/theme`."

## Step 2.13 — Dev lint rule (preview)

**Status (2026-10-01):** ⬜ no rule bans a bare `Text` import; today no v2 file imports one (`AppText` wraps Paper's `Text`).

Add to `.eslintrc` a warning rule:

```js
{
  'no-restricted-imports': ['warn', {
    paths: [{
      name: 'react-native',
      importNames: ['Text'],
      message: 'Use `AppText` from ~/theme instead of the bare <Text> primitive.',
    }],
  }],
}
```

Starts as `warn` — escalates to `error` in Phase 6 once the migration is complete.

---

## Phase 2 deliverables

**Status (2026-10-01):** 🟡 delivered: `AppText`, `Box` (for `AppBox`), `useTypeScale` / `boxHeight` (for `useFontScale` / `useContainerMinHeight`), both barrels, the docs in `docs/testing.md` and `AI.md`. Not delivered: the badge, `src/theme/README.md`, the lint warning; the canaries were dropped.

| Artifact                | File path                                                                         |
| ----------------------- | --------------------------------------------------------------------------------- |
| `<AppText>`             | `src/theme/components/AppText.js`                                                 |
| `<AppBox>`              | `src/theme/components/AppBox.js`                                                  |
| `<DevFontScaleBadge>`   | `src/theme/components/DevFontScaleBadge.js`                                       |
| `useFontScale`          | `src/theme/hooks/useFontScale.js`                                                 |
| `useContainerMinHeight` | `src/theme/hooks/useContainerMinHeight.js`                                        |
| Barrel exports          | `src/theme/index.js`, `src/theme/components/index.js`, `src/theme/hooks/index.js` |
| Dev docs                | `src/theme/README.md`                                                             |
| Canary screens          | 8 files migrated to `<AppText>`                                                   |
| Lint warning            | `.eslintrc` updated (warn only)                                                   |

## Verification

**Status (2026-10-01):** ❔ commands not run here; app CI runs `yarn test` only (no lint job).

```sh
yarn lint                    # new warnings on old <Text> usage
yarn test
yarn android && yarn ios     # canary screens look identical at scale 1.0
```

Manual AX5 + Android 2x font scale test on each canary screen. Any issues go into Phase 4 tracking.
