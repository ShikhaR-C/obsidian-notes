# Architecture

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Built in a leaner form as foundation step F-APP-3 on 2026-09-04 (redesign decision D11): of the 13 sections, 5 exist in code (without Restyle, some at other paths), 6 in part and 2 not at all (`runtime.js`, the theme slice). The primitives live in `src/components/v2/`, and the legacy `src/utils/Colors` stays the v1 source instead of becoming a shim. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Target folder structure

**Status (2026-10-01):** 🟡 built leaner — `src/theme/{tokens (palette, typography, spacing, radii, elevation), themes (light, dark, index), adapters (both), provider (ThemeProvider, ThemeContext, useAppTheme + six scale / window hooks)}` plus `scale.js`, `layout.js`, `tint.js` and `index.js`; the components sit in `src/components/v2/` (D10). Not built: `fixed.js`, `motion.js`, `neon.js`, `useThemeSwitcher.js`, `runtime.js`, `hooks/`, `lint/`, `README.md`.

```
src/theme/
├── index.js                        # Public barrel — everything importers need
├── tokens/
│   ├── palette.js                  # Reference palette (raw colors, no semantics)
│   ├── fixed.js                    # Theme-invariant tokens (brand, status, backdrop)
│   ├── spacing.js                  # 0, xs, s, m, l, xl, xxl scale
│   ├── radii.js                    # none, xs, sm, md, lg, xl, pill
│   ├── elevation.js                # 5 levels, shared by light + dark
│   ├── typography.js               # 15 MD3 variants — size/weight/lineHeight/tracking
│   └── motion.js                   # Animation durations and easing curves
├── themes/
│   ├── light.js                    # Light theme — maps palette → semantic roles
│   ├── dark.js                     # Dark theme — maps palette → semantic roles
│   ├── neon.js                     # Example "third" theme — proves extensibility
│   └── index.js                    # export const THEMES = [light, dark, neon]
├── adapters/
│   ├── toPaperTheme.js             # Base theme → react-native-paper MD3Theme
│   └── toNavigationTheme.js        # Base theme → @react-navigation/native theme
├── provider/
│   ├── ThemeProvider.js            # Wraps Restyle + Paper + Navigation providers
│   ├── useAppTheme.js              # Typed hook — primary consumer API
│   ├── useThemeSwitcher.js         # Returns { activeTheme, setTheme, availableThemes }
│   └── runtime.js                  # Module-level getActiveTheme() for non-React callers
├── components/
│   ├── AppText.js                  # createText<BaseTheme>() wrapper, adds uncapped font scaling
│   ├── AppBox.js                   # createBox<BaseTheme>()
│   ├── AppScreen.js                # Composable screen container (SafeArea + theme background)
│   └── index.js
├── hooks/
│   ├── useFontScale.js             # PixelRatio.getFontScale() with DevFontScale overlay
│   ├── useContainerMinHeight.js    # Returns scaled minHeight for text rows
│   └── index.js
├── lint/
│   └── no-hardcoded-colors.js      # Custom ESLint rule
└── README.md                       # Developer docs (how to add a theme, how to use AppText)
```

## Token hierarchy (3-tier)

**Status (2026-10-01):** 🟡 two tiers, not three: the palette holds role names with the legacy values ("Names are roles, not hues", `src/theme/tokens/palette.js:1-6`) and v2 components read the roles through `useAppTheme()`; there is no reference tier of hues.

```
Reference tokens (palette.js)          e.g. purple600 = '#6200ee'
       ↓
System / semantic tokens (light.js)    e.g. colors.primary = palette.purple600
       ↓
Component tokens (textVariants)        e.g. textVariants.button = { color: 'onPrimary', ... }
```

Only **system tokens** are consumed by components. Components never reference `palette` directly. This is what makes adding a new theme (e.g. "neon") a one-file change: you map the same semantic keys to different palette entries.

## Base theme shape (the single source of truth)

**Status (2026-10-01):** 🟡 the built shape is `{ name, dark, roundness, colors, spacing, radii, typography }` (+ `mode` in dark), `src/theme/themes/light.js:13-25`; the colours are the legacy keys, not the MD3 set below; breakpoints live in `src/theme/layout.js:10` as Material window classes (600 / 840), not `tablet: 768`.

```js
// src/theme/themes/light.js — illustration (full in Phase 1)
import palette from "../tokens/palette";
import spacing from "../tokens/spacing";
import borderRadii from "../tokens/radii";
import textVariants from "../tokens/typography";

const light = {
  name: "light",
  dark: false,
  colors: {
    // Brand
    primary: palette.purple600,
    onPrimary: palette.white,
    primaryContainer: palette.purple50,
    onPrimaryContainer: palette.purple900,

    secondary: palette.purpleDeep700,
    onSecondary: palette.white,
    secondaryContainer: palette.purple100,
    onSecondaryContainer: palette.purpleDeep900,

    tertiary: palette.teal400,
    onTertiary: palette.black,
    tertiaryContainer: palette.teal50,
    onTertiaryContainer: palette.teal900,

    // Surfaces
    background: palette.gray50,
    onBackground: palette.gray900,
    surface: palette.white,
    onSurface: palette.gray900,
    surfaceVariant: palette.gray100,
    onSurfaceVariant: palette.gray700,

    // Feedback
    error: palette.red700,
    onError: palette.white,
    errorContainer: palette.red50,
    onErrorContainer: palette.red900,

    // Outlines
    outline: palette.gray400,
    outlineVariant: palette.gray200,

    // Custom (app-specific extensions)
    link: palette.blue600,
    onLink: palette.white,
  },
  spacing,
  borderRadii,
  textVariants,
  breakpoints: { phone: 0, tablet: 768 },
};

export default light;
```

## Adding a new theme

**Status (2026-10-01):** 🟡 one file and one key in `themes` (`src/theme/themes/index.js:9`) would register it, but `AppNavigatorContainer.js:77-78` resolves only SYSTEM / DARK / LIGHT, Settings offers only those (`Settings/index.js:26`), and the parity test covers two themes.

1. Create `src/theme/themes/neon.js` (or any name).
2. Export a theme object with the **exact same keys** as `light.js` / `dark.js`.
3. Add it to `THEMES` in `src/theme/themes/index.js`:
   ```js
   import light from "./light";
   import dark from "./dark";
   import neon from "./neon";
   export const THEMES = [light, dark, neon];
   ```
4. Add the theme ID to the allowed values in `src/screens/Common/Settings/index.js`'s `THEME_OPTIONS`.

Done. No other code changes. No adapters to update. Restyle's `ThemeProvider` accepts the new theme, Paper's theme is generated by `toPaperTheme(neon)`, Navigation's is generated by `toNavigationTheme(neon)`.

## Provider composition

**Status (2026-10-01):** ✅ in a simpler form — `LanguageProvider` → `ThemeProvider` (a context) → `PaperProvider` → `RestartProvider` (the `NavigationContainer`) in `src/navigation/AppNavigatorContainer.js:176-181`; the theme is picked there from `auth.user.theme` (`:73-84`), with no Redux theme slice, no Restyle provider and no navigation-theme context.

`App.js` stays slim. `src/theme/provider/ThemeProvider.js` does the heavy lifting:

```jsx
// ThemeProvider.js pseudo-code
export const AppThemeProvider = ({ children }) => {
  const activeTheme = useSelector(selectActiveTheme); // from Redux
  const paperTheme = useMemo(() => toPaperTheme(activeTheme), [activeTheme]);
  const navTheme = useMemo(() => toNavigationTheme(activeTheme), [activeTheme]);

  // Keep runtime.js in sync for non-React callers
  useEffect(() => {
    setActiveThemeRuntime(activeTheme);
  }, [activeTheme]);

  return (
    <RestyleThemeProvider theme={activeTheme}>
      <PaperProvider theme={paperTheme}>
        <NavigationThemeContext.Provider value={navTheme}>
          {children}
        </NavigationThemeContext.Provider>
      </PaperProvider>
    </RestyleThemeProvider>
  );
};
```

`AppNavigatorContainer.js` becomes:

```jsx
// After refactor
const AppNavigatorContainer = () => {
  // ...existing auth logic unchanged
  return (
    <AppThemeProvider>
      <RestartProvider>
        <StatusBar barStyle={isDarkTheme ? "light-content" : "dark-content"} />
        {/* ... */}
      </RestartProvider>
    </AppThemeProvider>
  );
};
```

## Outside-component theme access

**Status (2026-10-01):** ⬜ no `runtime.js`; no non-React caller needs a theme value yet.

For utility files that run outside React (e.g., axios error handlers that need to build a toast, currency formatters that want to colorize negatives):

```js
// src/theme/provider/runtime.js
let _active = null;
export const setActiveThemeRuntime = (t) => {
  _active = t;
};
export const getActiveTheme = () => _active;

// in a non-component utility:
import { getActiveTheme } from "~/theme/provider/runtime";
const { colors } = getActiveTheme();
```

This is **not** React state. It's a plain module variable updated by an effect inside `AppThemeProvider`. Safe because there's exactly one active theme at a time and React's render phase is synchronous — the runtime snapshot is always consistent with what components see.

## `<AppText>` contract

**Status (2026-10-01):** ✅ `src/components/v2/AppText.js:24-53` — `variant`, a `color` token and any Text prop; no `dynamicTypeRamp`; a literal `fontSize` is refused by ESLint in v2 (`eslint.config.js:62-65`) instead of a dev warning; `includeFontPadding` is left alone.

```jsx
<AppText variant="bodyLarge">Hello</AppText>                    // default
<AppText variant="titleMedium" color="onSurfaceVariant">...    // override color role
<AppText variant="labelSmall" numberOfLines={1}>...             // truncate
<AppText variant="headlineSmall" dynamicTypeRamp="title1">...   // iOS Dynamic Type ramp
```

Under the hood it's `createText<BaseTheme>()` from Restyle, which reads `variant` from `theme.textVariants` and produces a native `<Text>`. We wrap it to inject:

- `allowFontScaling={true}` (uncapped, can be overridden)
- `maxFontSizeMultiplier={undefined}` (no cap, can be overridden)
- `includeFontPadding` **not set** (Android default preserved — workaround for #45660)
- Dev-only warning if someone passes `style={{ fontSize: ... }}` — enforces variant discipline

## `<AppBox>` and spacing

**Status (2026-10-01):** ✅ as `Box` (`src/components/v2/Box.js:49`) with `p` / `m` / `gap` / `bg` / `radius` props; the spacing scale is `xs 4 · sm 8 · md 16 · lg 24 · xl 32` from `src/constants/designTokens.js:1`, not the scale below.

```jsx
<AppBox bg="surface" p="m" borderRadius="md">
  <AppText variant="titleSmall">Title</AppText>
  <AppBox mt="s">
    <AppText variant="bodyMedium">Description</AppText>
  </AppBox>
</AppBox>
```

Spacing scale (`src/theme/tokens/spacing.js`): `none=0, xxs=2, xs=4, s=8, m=16, l=24, xl=32, xxl=48`. Phase 2 uses these.

## React Native Paper — adapter

**Status (2026-10-01):** ✅ `src/theme/adapters/toPaperTheme.js:28-44` — it rebuilds the legacy `Light` / `Dark` byte for byte (no MD3 base spread), pinned by `src/theme/__tests__/parity.test.js`.

`toPaperTheme.js` takes a base theme and returns a valid MD3Theme:

```js
import { MD3LightTheme, MD3DarkTheme } from "react-native-paper";

export const toPaperTheme = (base) => ({
  ...(base.dark ? MD3DarkTheme : MD3LightTheme),
  dark: base.dark,
  roundness: 4,
  colors: {
    ...(base.dark ? MD3DarkTheme.colors : MD3LightTheme.colors),
    ...base.colors, // base wins for any overlapping key
  },
  fonts: base.textVariants, // MD3 variant names match 1:1
});
```

Paper components (`<Button>`, `<Chip>`, `<Appbar>`, etc.) continue to work unchanged because the theme shape is the same as before.

## React Navigation — adapter

**Status (2026-10-01):** 🟡 built and tested (`src/theme/adapters/toNavigationTheme.js:33-44`, `card` and `text` from the legacy keys), but nothing calls it: `NavigationContainer` still gets the Paper theme (`src/components/Error/RestartContext.js:52`).

`toNavigationTheme.js`:

```js
import { DefaultTheme, DarkTheme } from "@react-navigation/native";

export const toNavigationTheme = (base) => ({
  ...(base.dark ? DarkTheme : DefaultTheme),
  dark: base.dark,
  colors: {
    primary: base.colors.primary,
    background: base.colors.background,
    card: base.colors.surface,
    text: base.colors.onSurface,
    border: base.colors.outline,
    notification: base.colors.error,
  },
});
```

## Redux theme slice (new, Phase 1)

**Status (2026-10-01):** ⬜ not built; the theme stays `auth.user.theme`. The "already installed" claim below is corrected in place.

Currently theme lives in `auth.user.theme`. We add a thin new slice for local-first behavior:

```js
// src/store/slices/theme.js
{
  themeId: 'system' | 'light' | 'dark' | 'neon',
  systemColorScheme: 'light' | 'dark',
}
```

A memoized selector `selectActiveTheme(state)` resolves `'system'` → `systemColorScheme` and returns the corresponding theme object from `THEMES`. The auth-bound `user.theme` value is mirrored into this slice on login and writes to it trigger the backend `useSet_themeMutation` as today. Decouples theming from auth without losing backend sync.

Persisted via `redux-persist` ~~(already installed)~~ (_2026-10-01:_ not a dependency; theme persistence was deferred by F-APP-3) so the theme choice survives cold starts even before the user object loads.

## Typography tokens — uncapped-aware

**Status (2026-10-01):** 🟡 the 15 roles exist (`src/theme/tokens/typography.js:8-114`) without `color` or `defaults` entries (colour is `AppText`'s prop); the invariant below fails for the display roles (1.12 / 1.16 / 1.22, Phase 4 Step 4.1, ⬜); Hindi's taller line sits on top (`SCRIPT_LINE_HEIGHT`, `src/theme/scale.js:19`).

The 15 MD3 variants in `src/theme/tokens/typography.js`:

```js
const textVariants = {
  displayLarge: {
    fontFamily: "System",
    fontSize: 57,
    fontWeight: "400",
    letterSpacing: -0.25,
    lineHeight: 64,
    color: "onBackground",
  },
  // ... etc, all 15 with correct letterSpacing (fixing the existing bug)
  defaults: {
    fontFamily: "System",
    fontSize: 16,
    fontWeight: "400",
    lineHeight: 24,
    color: "onBackground",
  },
};
```

**Critical invariant for uncapped scaling**: every variant has `lineHeight >= fontSize * 1.25`. When the user sets Android font scale to 2x, lineHeight scales proportionally and the text doesn't clip. This matches M3's ratios exactly, which is not a coincidence — M3's line heights were chosen with accessibility in mind.

## ESLint rule — `no-hardcoded-colors`

**Status (2026-10-01):** ✅ for the v2 scope, as a `no-restricted-syntax` block (`eslint.config.js:42-76`: hex, `rgb(`, literal `fontSize`, JSX copy) at `error` from day one; colour names are not banned and there is no custom rule file; app CI runs no lint (`X-CI-2` in tasks_02).

Custom rule under `src/theme/lint/` (or a shared `.eslint-rules/` folder). Blocks:

- String literals matching `/^#[0-9a-f]{3,8}$/i` in JSX or `StyleSheet.create` arguments
- String literals matching `/^rgba?\(/`
- Color name literals (`'white'`, `'black'`, `'red'`) in style contexts

Exceptions:

- Files under `src/components/SVG/psoc/` (brand logos — intentional)
- Files under `src/theme/tokens/` (definition site)

Starts as `"warn"` in Phase 3, escalates to `"error"` in Phase 6.
