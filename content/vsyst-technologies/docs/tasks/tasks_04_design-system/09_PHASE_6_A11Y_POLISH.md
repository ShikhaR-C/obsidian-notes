# Phase 6 — Accessibility, Polish, and Enforcement

**Goal**: Take the shipped design system from "works" to "Apple-grade." Lock in quality with enforcement. Ship power-user features.

**Entry criteria**: Phases 1–5 complete. All screens migrated. Font scaling uncapped.

**Exit criteria**:

- WCAG AA contrast verified programmatically on every semantic color combination
- ESLint `no-hardcoded-colors` escalated to `error`
- ESLint `no-restricted-imports` for bare `<Text>` escalated to `error`
- Custom fonts (OpenSans, RobotoCondensed) optionally integrated OR formally retired from the bundle
- Redux-persist-backed theme (no more "flash of wrong theme" on cold start)
- Material You dynamic color support on Android 12+ (optional but recommended)
- An app-wide accessibility audit with screen reader (TalkBack / VoiceOver)
- Developer documentation complete
- One new "tertiary" theme added beyond the three existing ones to prove extensibility at scale

---

## Step 6.1 — WCAG contrast automation

Install `color2k` or `wcag-contrast` (small lib, ~2kb) and write a test:

```js
// src/theme/__tests__/contrast.test.js
import { hex } from "wcag-contrast";
import light from "../themes/light";
import dark from "../themes/dark";
import neon from "../themes/neon";

const PAIRS = [
  ["primary", "onPrimary"],
  ["primaryContainer", "onPrimaryContainer"],
  ["secondary", "onSecondary"],
  ["tertiary", "onTertiary"],
  ["error", "onError"],
  ["errorContainer", "onErrorContainer"],
  ["background", "onBackground"],
  ["surface", "onSurface"],
  ["surfaceVariant", "onSurfaceVariant"],
  ["inverseSurface", "inverseOnSurface"],
];

describe.each([
  ["light", light],
  ["dark", dark],
  ["neon", neon],
])("%s theme contrast", (_, theme) => {
  test.each(PAIRS)("%s vs %s meets WCAG AA (4.5:1)", (bg, fg) => {
    const ratio = hex(theme.colors[bg], theme.colors[fg]);
    expect(ratio).toBeGreaterThanOrEqual(4.5);
  });
});
```

Any failing pair either gets fixed by adjusting the palette entry or flagged as an intentional exception (e.g., `disabled` is expected to be low-contrast).

Run in CI via `yarn test`. Gating: failing = CI red.

## Step 6.2 — Escalate lint rules

```diff
// .eslintrc
- 'no-restricted-imports': ['warn', { ... }],
+ 'no-restricted-imports': ['error', { ... }],

- 'local-rules/no-hardcoded-colors': 'warn',
+ 'local-rules/no-hardcoded-colors': 'error',
```

`yarn lint` now fails CI if anyone reintroduces a bare `<Text>` or a hardcoded color outside the exempted paths.

## Step 6.3 — Custom font decision

Three options for the installed-but-unused `OpenSans_Regular.ttf`, `RCL_Light.ttf`, `RobotoCondensed_Regular.ttf`:

**Option A — Adopt OpenSans as the primary font family.**
Update `src/theme/tokens/typography.js`: change every variant's `fontFamily` from `'System'` to `'OpenSans'`. Consistent cross-platform look. Adds a tiny visual diff that needs design sign-off.

**Option B — Reserve for specific uses.**
Use `RobotoCondensed` for numeric tables (dashboards, reports) where condensed digits aid scanability. Use `System` elsewhere. Requires a new variant family.

**Option C — Retire.**
Remove the font assets from the bundle. Delete the entries from `react-native.config.js`. Shaves a few hundred KB from the APK/IPA.

**Recommendation**: Option A unless design has a strong preference otherwise. OpenSans is a solid neutral sans-serif that renders identically on both platforms, which is exactly what we want for a cross-platform OMS.

If Option A:

1. Update every variant in `typography.js`: `fontFamily: Platform.OS === 'ios' ? 'OpenSans-Regular' : 'OpenSans_Regular'` (iOS uses hyphens, Android uses underscores)
2. Rebuild iOS (`cd ios && pod install`) and Android to pick up font assets
3. Visual QA the canary screens
4. Test font scaling still works (custom fonts sometimes have different metric quirks)

## Step 6.4 — Local-first theme persistence (via `redux-persist`)

Problem: current theme is backend-only via `auth.user.theme`. On cold start / fresh install / logout, the user briefly sees the wrong theme until the user object loads.

Solution: persist the `theme` Redux slice locally via `redux-persist` (already in dependencies).

```js
// src/store/apis/index.js — add to persistConfig
const persistConfig = {
  key: "root",
  storage: AsyncStorage,
  whitelist: ["auth", "theme"], // add theme
};
```

The new `theme` slice (Phase 1.15) becomes the source of truth; backend sync still happens on login via the existing `useSet_themeMutation`.

## Step 6.5 — Consolidate theme-toggle entry points

Audit found two places that toggle theme:

- `src/screens/Common/Settings/index.js` (primary)
- `src/components/VersionInfo/index.js` (duplicate)

Remove the `VersionInfo` toggle. Keep the single source of truth in Settings.

## Step 6.6 — Accessibility audit

For each of the 20 highest-traffic screens, run through:

1. **TalkBack (Android)** — every interactive element is reachable, labeled, and has appropriate role
2. **VoiceOver (iOS)** — same
3. **Color inversion / grayscale** — UI remains navigable
4. **Reduced motion** (iOS Settings → Accessibility → Motion) — any react-native-reanimated usage must respect `AccessibilityInfo.isReduceMotionEnabled()`
5. **Contrast** — run through the `wcag-contrast` test results per screen

Any a11y bugs found get fixed. Add `accessibilityLabel`, `accessibilityRole`, `accessibilityHint` props to custom components.

## Step 6.7 — Apple-grade polish checklist

Items borrowed from Apple HIG that we should audit:

- **Spacing rhythm** — every layout uses tokens from `spacing.js`, never magic numbers. Run a grep.
- **Alignment** — titles align with body text, not with icons. Icons align with the vertical midpoint of their sibling text.
- **Consistent icon sizing** — create a `sizes` token (`iconSizes.sm/md/lg` = 16/20/24) and enforce.
- **Material elevations** — use `surfaceContainerLow/Default/High/Highest` instead of ad-hoc shadows for cards/sheets.
- **Haptic feedback on destructive actions** — `react-native-haptic-feedback` or Expo Haptics. Brief tap on delete, confirm, success.
- **Motion** — Respect user's reduced-motion setting. Use tokens from `motion.js`: `durations.fast/medium/slow`, `easings.enter/exit/standard`.
- **Tappable targets** — minimum 44×44 on iOS, 48×48dp on Android. Audit after Phase 4's minHeight migration.
- **Safe area** — verify bottom inset handled on devices with home indicators (already done via `useSafeAreaInsets` in `AppNavigatorContainer`).
- **Focus states** — forms and lists should have visible focus outlines when keyboard-navigated (for tablets + external keyboards).

## Step 6.8 — Material You dynamic color (Android 12+)

**Optional but recommended.** On Android 12+, users can set a system accent color and apps can opt into it. Install `@pchmn/expo-material3-theme` (works in bare RN despite the name) and in `ThemeProvider.js`:

```js
import { useMaterial3Theme } from "@pchmn/expo-material3-theme";

// inside AppThemeProvider:
const { theme: material3Scheme } = useMaterial3Theme();
// If Android 12+ and user has dynamic theming enabled, build a theme from material3Scheme;
// otherwise fall back to our named themes.
```

This makes the app feel native on modern Android. Opt-in via a Settings toggle: "Use system accent color."

## Step 6.9 — Tertiary theme as stress test

Add one more theme to `THEMES[]` after migration is complete. Suggested: a "high-contrast light" theme for very-low-vision users. Palette:

- Background: pure white (`#ffffff`)
- Text: pure black (`#000000`)
- Primary: navy (`#000080`)
- All roles bumped to ≥7:1 contrast

Ship it. Contrast tests pass automatically (Phase 6.1).

Success criterion: adding this theme is a **one-file change** (just create `src/theme/themes/highContrast.js`, add to `THEMES[]`). If it requires touching anything else, the architecture has a leak.

## Step 6.10 — Developer documentation (final)

Finalize `src/theme/README.md`:

1. Philosophy (why tokens, why variants, why uncapped)
2. Quickstart (`import { AppText, AppBox, useAppTheme } from '~/theme'`)
3. Variant cheat sheet
4. Color role cheat sheet
5. Spacing scale
6. How to add a theme
7. How to add a new brand color
8. Layout rules for uncapped font scaling
9. How to test at AX5 / Android 2x
10. Common pitfalls (includeFontPadding, fixed heights, nested Text)

Add a link to the new doc from `AI.md` so Claude reads it automatically.

## Step 6.11 — Figma / design handoff

Generate a design tokens file for the design team:

```sh
# one-off script in scripts/export-design-tokens.js
# reads src/theme/tokens/* and outputs a JSON compatible with Figma Tokens / Tokens Studio
```

Design team imports into Figma so mockups stay in sync with code.

## Step 6.12 — Migration retrospective

Once all phases are complete, hold a team retro. Document in `docs/todos/design-system/RETRO.md`:

- What worked
- What didn't
- Which patterns need refinement
- Open debt (screens that got minimal migration, non-text components that could use similar treatment)
- Candidate follow-ups: component library (reusable Card/ListRow primitives), dark mode preview in design, E2E test theming

---

## Phase 6 deliverables

| Artifact                       | File path                                        |
| ------------------------------ | ------------------------------------------------ |
| Contrast test suite            | `src/theme/__tests__/contrast.test.js`           |
| Lint escalation                | `.eslintrc` (error level)                        |
| Font decision + implementation | `src/theme/tokens/typography.js`                 |
| Theme persistence              | `src/store/apis/index.js` (persist whitelist)    |
| Consolidated theme toggle      | Removed from `VersionInfo/index.js`              |
| Material You integration       | `src/theme/provider/ThemeProvider.js` (optional) |
| High-contrast theme            | `src/theme/themes/highContrast.js`               |
| Developer docs                 | `src/theme/README.md` (final)                    |
| Design token export script     | `scripts/export-design-tokens.js`                |
| Retrospective                  | `docs/todos/design-system/RETRO.md`              |

## Verification

```sh
yarn test                    # contrast tests pass
yarn lint                    # zero warnings, zero errors
yarn android                 # Material You works on Android 12+
yarn ios                     # VoiceOver audit clean
```

Manual: full accessibility audit (TalkBack/VoiceOver) on top-20 screens. Contrast report exported and reviewed.
