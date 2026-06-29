# Dzzlo OMS — Design System Plan

This folder contains the full investigation, research, architecture, and phased execution plan for migrating the app to a centralized design system.

## Why this plan exists

The current theming system (`src/utils/Colors/index.js`) started as a minimal React Native Paper theme wrapper and has grown unsustainable:

- **2,435+ `<Text>` instances** scattered across 181 files with no abstraction layer
- **547 hardcoded `fontSize` values** and **291 hardcoded `fontWeight` values** in inline styles
- **1,500+ hardcoded hex / rgb / rgba strings** across 227 files
- **Zero use** of `allowFontScaling` or `maxFontSizeMultiplier` — the app is completely unaware of user accessibility font settings
- **48+ fixed-height containers** wrapping text (`height: 40/48/50/56`) that will clip when fonts grow
- **Android low-end devices** trim/clip bold text when system font size + bold accessibility are enabled (known RN bug, GitHub issue #45660, unfixed as of Oct 2025)
- **Theme switching works** (Redux `auth.user.theme` → `'SYSTEM' | 'DARK' | 'LIGHT'`) but is hardwired to two themes; adding a new palette like "neon" requires code changes in multiple places
- **`defaultCombined.js` is dead code** — legacy backup theme never imported anywhere
- **Navigation theme** is not explicitly configured (relies on Paper theme shape compatibility — fragile)
- **Custom fonts are installed** (`OpenSans_Regular`, `RCL_Light`, `RobotoCondensed_Regular`) but unused — all text uses `'System'`

See `02_AUDIT.md` for the full findings.

## Decisions locked in

| Decision                | Choice                                               | Rationale                                                                                                                                                                                                                                    |
| ----------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Theming engine**      | `@shopify/restyle` on top of react-native-paper 5.15 | Strongest enterprise design-system discipline. Typed theme, `createBox` / `createText` / `createRestyleComponent` primitives, and forced variant usage. Paper stays for its MD3 components; Restyle runs app-layer styles.                   |
| **Font scaling**        | **Uncapped** + comprehensive layout fix              | Full WCAG 1.4.4 / Apple HIG accessibility. Migrate all 48+ fixed-height containers to `minHeight`, audit every screen at AX5 / Android 200% font scale, add `flexWrap` / `flexShrink` / `numberOfLines` + `ellipsizeMode` everywhere needed. |
| **File layout**         | New `src/theme/` folder                              | Clean separation from legacy `src/utils/Colors/`. Legacy path becomes a thin re-export shim during migration so all 86 direct-import files keep compiling.                                                                                   |
| **Theme registry**      | Array-based, extensible                              | `src/theme/themes/index.js` exports `const THEMES = [light, dark, neon, ...]`. Adding a new theme = one file + one array entry. No code changes elsewhere.                                                                                   |
| **Typography variants** | MD3 naming (`bodyLarge`, `titleMedium`, etc.)        | Matches react-native-paper's built-in `variant` prop on `<Text>`. No mental model shift for anyone reading the code. Exact scale from M3: display/headline/title/body/label × large/medium/small.                                            |
| **Fixed colors**        | Separate token layer                                 | Brand colors (IOCL, NAYARA, HPCL, BPCL, SHELL, JIO_BP) + success green stay theme-invariant in `src/theme/tokens/fixed.js`.                                                                                                                  |

## How to read these docs

Read in order if you're new:

1. **[00_README.md](./00_README.md)** — this file
2. **[01_RESEARCH.md](./01_RESEARCH.md)** — external research (Apple HIG, MD3, RN docs, libraries, Android clipping bug) with sources
3. **[02_AUDIT.md](./02_AUDIT.md)** — current state of the codebase with file paths and counts
4. **[03_ARCHITECTURE.md](./03_ARCHITECTURE.md)** — the proposed `src/theme/` folder structure, token layers, and integration model
5. **[04_PHASE_1_FOUNDATION.md](./04_PHASE_1_FOUNDATION.md)** — install deps, build tokens, register themes, wire provider
6. **[05_PHASE_2_TYPOGRAPHY.md](./05_PHASE_2_TYPOGRAPHY.md)** — `<AppText>`, font variants, uncapped scaling hook
7. **[06_PHASE_3_COLORS.md](./06_PHASE_3_COLORS.md)** — semantic color roles, hardcoded-color migration, ESLint rule
8. **[07_PHASE_4_ANDROID_CLIPPING.md](./07_PHASE_4_ANDROID_CLIPPING.md)** — clipping fix, `minHeight` migration, lineHeight discipline
9. **[08_PHASE_5_SCREEN_MIGRATION.md](./08_PHASE_5_SCREEN_MIGRATION.md)** — ordered screen-by-screen migration list
10. **[09_PHASE_6_A11Y_POLISH.md](./09_PHASE_6_A11Y_POLISH.md)** — contrast audit, Apple-level polish, docs, lint enforcement
11. **[10_TASKS.md](./10_TASKS.md)** — master checklist with every actionable task tagged by phase

Each phase file contains:

- **Goal** — one sentence
- **Entry criteria** — what must be true before starting
- **Exit criteria** — how you know it's done
- **Steps** — each step small enough to do in one sitting, with file paths, function references, and verification commands

## Scope guardrails

- **No breaking changes during migration.** Legacy `src/utils/Colors/index.js` remains as a re-export shim until the final phase. Existing 348 `useTheme()` callers keep working throughout.
- **No new fonts in Phase 1.** Custom font integration (`OpenSans`, `RCL_Light`, `RobotoCondensed`) is deferred to Phase 6 unless we decide earlier. Initial migration uses `'System'` as today.
- **No Redux-persist migration for theme yet.** Theme is currently backend-only (`auth.user.theme`). Local persistence (AsyncStorage fallback so users don't flash the wrong theme on logout) is a Phase 6 task.
- **No tamagui, unistyles, nativewind, or dripsy.** Restyle was chosen; we're not mixing frameworks.
