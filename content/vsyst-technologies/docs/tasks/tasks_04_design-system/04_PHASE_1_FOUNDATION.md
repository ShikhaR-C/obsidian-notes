# Phase 1 — Foundation

**Goal**: Stand up `src/theme/`, install Restyle, wire the new provider, and ship zero visible changes.

**Entry criteria**: Design decisions locked (README), audit reviewed, architecture approved.

**Exit criteria**:

- `@shopify/restyle` installed and builds on iOS + Android
- `src/theme/` folder exists with tokens + 2 themes (light, dark) + 1 proof-of-concept theme (neon)
- `AppThemeProvider` wraps `PaperProvider` and `NavigationContainer` theme
- `src/utils/Colors/index.js` becomes a thin re-export of the new theme so existing 86 direct-import files keep compiling
- App looks **identical** to today — no visual diff
- Theme switching in `Common/Settings` still works and now accepts `'NEON'` as a fourth option

---

## Step 1.1 — Install `@shopify/restyle`

```sh
yarn add @shopify/restyle
```

No native linking. Verify with `yarn start --reset-cache && yarn ios && yarn android`.

## Step 1.2 — Create `src/theme/` skeleton

Create the folder structure from `03_ARCHITECTURE.md`:

```
src/theme/
├── tokens/
│   ├── palette.js
│   ├── fixed.js
│   ├── spacing.js
│   ├── radii.js
│   ├── elevation.js
│   ├── typography.js
│   └── motion.js
├── themes/
│   ├── light.js
│   ├── dark.js
│   ├── neon.js
│   └── index.js
├── adapters/
│   ├── toPaperTheme.js
│   └── toNavigationTheme.js
├── provider/
│   ├── ThemeProvider.js
│   ├── useAppTheme.js
│   ├── useThemeSwitcher.js
│   └── runtime.js
├── components/   (deferred to Phase 2)
├── hooks/        (deferred to Phase 2)
└── index.js
```

## Step 1.3 — Write `tokens/palette.js`

Seed the reference palette. Start by **lifting every color currently in `src/utils/Colors/index.js`** into the palette with semantic names, then add the missing MD3 tonal variants.

```js
// src/theme/tokens/palette.js — illustrative subset
export default {
  // Purples (primary family)
  purple50: "#f3e5ff",
  purple100: "#e1bfff",
  purple200: "#c28aff",
  purple300: "#a05cff",
  purple400: "#8438f3",
  purple500: "#6200ee",
  purple600: "#5300d2",
  purple700: "#3700bc",
  purple800: "#2a0099",
  purple900: "#1a0066",

  // Grays (neutral family)
  white: "#ffffff",
  gray50: "#f2f2f2",
  gray100: "#e5e5e5",
  gray200: "#d8d8d8",
  // ... through gray900
  black: "#000000",

  // Status families (red/green/amber/blue)
  red50: "#ffebee",
  red700: "#b00020",
  red900: "#4a0010",
  green500: "#6ebf33",
  amber500: "#ff9800",
  blue600: "#0000ee",

  // Transparent overlays
  scrim50: "rgba(0, 0, 0, 0.5)",
  scrim30: "rgba(0, 0, 0, 0.3)",
};
```

Every hex that currently appears in `Light` or `Dark` goes into palette with a named key. The existing `hex2rgba` and `hex_alpha` helpers move to `src/theme/utils/color.js` unchanged.

## Step 1.4 — Write `tokens/fixed.js`

Theme-invariant tokens (same value in every theme):

```js
// src/theme/tokens/fixed.js
export default {
  // Status colors (user expectation: success is always green, error is always red)
  success: "#6ebf33",
  warning: "#ff9800",
  info: "#0277bd",

  // Overlay / scrim
  backdrop: "rgba(0, 0, 0, 0.5)",

  // PSoC brand palette
  brand: {
    iocl: { primary: "#f38f1d", secondary: "#004b87" },
    nayara: { primary: "#e87722", secondary: "#231f20" },
    hpcl: { primary: "#0066b3", secondary: "#ed1c24" },
    bpcl: { primary: "#f6a800", secondary: "#1b5e20" },
    shell: { primary: "#ffd500", secondary: "#dd1d21" },
    jiobp: { primary: "#0033a0", secondary: "#f7a800" },
  },
};
```

Exact brand hex values to be verified from the SVG files under `src/components/SVG/psoc/` in Step 1.4a.

## Step 1.5 — Write `tokens/typography.js`

Full 15-variant MD3 scale with **corrected** `letterSpacing` (fixing the bug in the current fontObject):

```js
// src/theme/tokens/typography.js
const textVariants = {
  displayLarge: {
    fontFamily: "System",
    fontSize: 57,
    fontWeight: "400",
    lineHeight: 64,
    letterSpacing: -0.25,
  },
  displayMedium: {
    fontFamily: "System",
    fontSize: 45,
    fontWeight: "400",
    lineHeight: 52,
    letterSpacing: 0,
  },
  displaySmall: {
    fontFamily: "System",
    fontSize: 36,
    fontWeight: "400",
    lineHeight: 44,
    letterSpacing: 0,
  },
  headlineLarge: {
    fontFamily: "System",
    fontSize: 32,
    fontWeight: "400",
    lineHeight: 40,
    letterSpacing: 0,
  },
  headlineMedium: {
    fontFamily: "System",
    fontSize: 28,
    fontWeight: "400",
    lineHeight: 36,
    letterSpacing: 0,
  },
  headlineSmall: {
    fontFamily: "System",
    fontSize: 24,
    fontWeight: "400",
    lineHeight: 32,
    letterSpacing: 0,
  },
  titleLarge: {
    fontFamily: "System",
    fontSize: 22,
    fontWeight: "400",
    lineHeight: 30,
    letterSpacing: 0,
  },
  titleMedium: {
    fontFamily: "System",
    fontSize: 16,
    fontWeight: "500",
    lineHeight: 24,
    letterSpacing: 0.15,
  },
  titleSmall: {
    fontFamily: "System",
    fontSize: 14,
    fontWeight: "500",
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  bodyLarge: {
    fontFamily: "System",
    fontSize: 16,
    fontWeight: "400",
    lineHeight: 24,
    letterSpacing: 0.5,
  },
  bodyMedium: {
    fontFamily: "System",
    fontSize: 14,
    fontWeight: "400",
    lineHeight: 20,
    letterSpacing: 0.25,
  },
  bodySmall: {
    fontFamily: "System",
    fontSize: 12,
    fontWeight: "400",
    lineHeight: 16,
    letterSpacing: 0.4,
  },
  labelLarge: {
    fontFamily: "System",
    fontSize: 14,
    fontWeight: "500",
    lineHeight: 20,
    letterSpacing: 0.1,
  },
  labelMedium: {
    fontFamily: "System",
    fontSize: 12,
    fontWeight: "500",
    lineHeight: 16,
    letterSpacing: 0.5,
  },
  labelSmall: {
    fontFamily: "System",
    fontSize: 11,
    fontWeight: "500",
    lineHeight: 16,
    letterSpacing: 0.5,
  },

  defaults: {
    fontFamily: "System",
    fontSize: 16,
    fontWeight: "400",
    lineHeight: 24,
    color: "onBackground",
  },
};

export default textVariants;
```

**Invariant check**: every variant has `lineHeight / fontSize >= 1.23`. This is what buys us safety when Android font scale goes to 2x (Phase 4 depends on it).

## Step 1.6 — Write `tokens/spacing.js` and `tokens/radii.js`

```js
// src/theme/tokens/spacing.js
export default { none: 0, xxs: 2, xs: 4, s: 8, m: 16, l: 24, xl: 32, xxl: 48 };

// src/theme/tokens/radii.js
export default { none: 0, xs: 2, sm: 4, md: 8, lg: 12, xl: 20, pill: 9999 };
```

These values reflect the most common hardcoded values observed in the audit (4, 8, 12, 16, 20, 24, 32).

## Step 1.7 — Write `themes/light.js` and `themes/dark.js`

Each file imports palette + fixed + typography and produces a full semantic theme. See `03_ARCHITECTURE.md` for the `light.js` skeleton. The dark theme mirrors the same keys with dark-appropriate palette entries.

**Match the existing Light/Dark values exactly** where possible — this phase ships zero visual diff. Any refinement happens in Phase 6.

## Step 1.8 — Write `themes/neon.js` (proof of extensibility)

A third theme to prove adding one is trivial. Use electric purple + near-black surface + high-contrast neon accents. This isn't enabled in production; it's a functional test that the registry works.

```js
// src/theme/themes/neon.js — same shape as light/dark, different palette choices
import palette from '../tokens/palette';
import fixed from '../tokens/fixed';
import textVariants from '../tokens/typography';

export default {
  name: 'neon',
  dark: true,
  colors: {
    primary: '#ff00ff',
    onPrimary: '#000000',
    background: '#0a0014',
    surface: '#1a0028',
    onSurface: '#ff00ff',
    // ... all semantic keys
  },
  spacing: (/* same tokens */),
  borderRadii: (/* same tokens */),
  textVariants,
  breakpoints: { phone: 0, tablet: 768 },
  fixed,
};
```

## Step 1.9 — Write `themes/index.js`

```js
// src/theme/themes/index.js
import light from "./light";
import dark from "./dark";
import neon from "./neon";

export const THEMES = [light, dark, neon];

export const getThemeById = (id) => THEMES.find((t) => t.name === id) ?? light;
```

Adding a new theme later is literally adding a file + one entry here.

## Step 1.10 — Write `adapters/toPaperTheme.js` and `toNavigationTheme.js`

Bodies defined in `03_ARCHITECTURE.md`. These are pure functions — no state, trivially testable.

## Step 1.11 — Write `provider/runtime.js`

```js
// src/theme/provider/runtime.js
let _activeTheme = null;
export const setActiveThemeRuntime = (theme) => {
  _activeTheme = theme;
};
export const getActiveTheme = () => _activeTheme;
```

For any non-component caller (error boundaries, formatters, axios interceptors) that needs a theme value.

## Step 1.12 — Write `provider/ThemeProvider.js`

```jsx
import { ThemeProvider as RestyleThemeProvider } from "@shopify/restyle";
import { PaperProvider } from "react-native-paper";
import { useSelector } from "react-redux";
import { useMemo, useEffect } from "react";
import { useColorScheme } from "react-native";
import { getThemeById } from "../themes";
import { toPaperTheme } from "../adapters/toPaperTheme";
import { setActiveThemeRuntime } from "./runtime";

export const AppThemeProvider = ({ children }) => {
  const scheme = useColorScheme();
  const themeId = useSelector(
    (state) => state.theme?.themeId ?? state.auth?.user?.theme ?? "system",
  );

  const resolvedId =
    themeId === "system"
      ? scheme === "dark"
        ? "dark"
        : "light"
      : themeId.toLowerCase();
  const activeTheme = getThemeById(resolvedId);
  const paperTheme = useMemo(() => toPaperTheme(activeTheme), [activeTheme]);

  useEffect(() => {
    setActiveThemeRuntime(activeTheme);
  }, [activeTheme]);

  return (
    <RestyleThemeProvider theme={activeTheme}>
      <PaperProvider theme={paperTheme}>{children}</PaperProvider>
    </RestyleThemeProvider>
  );
};
```

## Step 1.13 — Write `provider/useAppTheme.js`

```js
import { useTheme } from "@shopify/restyle";
export const useAppTheme = () => useTheme();
```

Thin wrapper — lets us evolve the hook later without touching 300+ call sites.

## Step 1.14 — Write `provider/useThemeSwitcher.js`

```js
import { useDispatch, useSelector } from "react-redux";
import { THEMES } from "../themes";
import { setTheme } from "../../store/slices/theme";

export const useThemeSwitcher = () => {
  const dispatch = useDispatch();
  const activeId = useSelector((state) => state.theme.themeId);
  return {
    activeId,
    availableThemes: THEMES.map((t) => ({ id: t.name, label: t.name })),
    setTheme: (id) => dispatch(setTheme(id)),
  };
};
```

## Step 1.15 — Create `src/store/slices/theme.js`

New Redux slice dedicated to theme state. Persisted via `redux-persist` so the choice survives cold starts.

```js
import { createSlice } from "@reduxjs/toolkit";
const slice = createSlice({
  name: "theme",
  initialState: { themeId: "system" },
  reducers: {
    setTheme: (state, action) => {
      state.themeId = action.payload;
    },
  },
});
export const { setTheme } = slice.actions;
export default slice.reducer;
```

Register in `src/store/apis/index.js` alongside the existing slices. Add `theme` to the `persistConfig.whitelist` if one exists, or set up persistence if not already wired.

## Step 1.16 — Refactor `src/utils/Colors/index.js` into a shim

```js
// src/utils/Colors/index.js — after refactor
import light from "../../theme/themes/light";
import dark from "../../theme/themes/dark";
import { toPaperTheme } from "../../theme/adapters/toPaperTheme";

// Backwards-compat — preserve the old shape
export const Light = toPaperTheme(light);
export const Dark = toPaperTheme(dark);

// Keep the color utils in place
export { hex2rgba, hex_alpha } from "../../theme/utils/color";
```

All 86 direct-import files keep working unchanged. Phase 5 migrates them gradually.

## Step 1.17 — Delete `src/utils/Colors/defaultCombined.js`

It's dead code. Verified zero importers in the audit. Delete the file.

## Step 1.18 — Wire `AppThemeProvider` in `AppNavigatorContainer.js`

Replace the existing `<PaperProvider theme={theme}>` at `src/navigation/AppNavigatorContainer.js:83` with `<AppThemeProvider>`. Remove the inline theme-resolution logic (lines 43-49) — it's now in `AppThemeProvider`. Keep the StatusBar line but read `isDarkTheme` from the new `useAppTheme()` hook instead.

## Step 1.19 — Sync Navigation theme

`src/components/Error/RestartContext.js` currently passes the Paper theme directly to `<NavigationContainer>`. Change it to use `toNavigationTheme(activeTheme)`. This requires pulling `activeTheme` from `useAppTheme()`.

## Step 1.20 — Smoke test

- Run `yarn ios` + `yarn android`
- Toggle Settings → Theme → LIGHT / DARK / SYSTEM, confirm nothing visibly changed
- Set `state.theme.themeId = 'neon'` via Redux DevTools, confirm the neon theme applies (screen should glow purple) — proves extensibility
- Revert to 'light', confirm clean state
- Kill and relaunch, confirm theme choice persists (redux-persist)

## Step 1.21 — Lint pass

`yarn lint` — expect zero new errors. The shim preserves all existing imports.

---

## Phase 1 deliverables

| Artifact      | File path                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------- |
| Installed dep | `@shopify/restyle` in `package.json`                                                        |
| Token files   | `src/theme/tokens/{palette,fixed,spacing,radii,elevation,typography,motion}.js`             |
| Theme files   | `src/theme/themes/{light,dark,neon,index}.js`                                               |
| Adapters      | `src/theme/adapters/{toPaperTheme,toNavigationTheme}.js`                                    |
| Provider      | `src/theme/provider/{ThemeProvider,useAppTheme,useThemeSwitcher,runtime}.js`                |
| Redux slice   | `src/store/slices/theme.js` (registered in store)                                           |
| Shim          | `src/utils/Colors/index.js` (rewritten as re-export)                                        |
| Deletion      | `src/utils/Colors/defaultCombined.js` (removed)                                             |
| Wiring        | `src/navigation/AppNavigatorContainer.js`, `src/components/Error/RestartContext.js` updated |

## Verification

```sh
yarn lint                    # 0 errors
yarn test                    # existing tests pass
yarn android                 # boots, visually unchanged
yarn ios                     # boots, visually unchanged
```

Manual: toggle theme in settings, force neon via Redux DevTools, confirm round-trip.
