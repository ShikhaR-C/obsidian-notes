# Phase 6 — Accessibility, Polish, and Enforcement

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Mostly open: of the 12 steps, 4 are partly done (lint at `error` in the v2 scope, the polish checklist, the docs, the design handoff), 4 to do, 2 deferred by F-APP-3 (custom fonts, theme persistence), 1 unverifiable (screen-reader audits) and 1 dropped (the migration retrospective). The v2 screens already carry roles, labels, live regions, 44 pt targets and uncapped text, but no contrast check exists — and the review found a light-mode contrast failure in v2 (🆕 T04-N2 in [00_README](./00_README.md)). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

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

**Status (2026-10-01):** ⬜ no contrast library and no `contrast.test.js` among the 20 theme test files. The house rule against new dependencies (02-foundations log) points to a small WCAG helper instead; `success` on light surfaces would fail today (T04-N2).

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

**Status (2026-10-01):** 🟡 the colour rule is already `error`, for the v2 scope only (`eslint.config.js:42-76`); the bare-`Text` rule does not exist; app CI runs no lint, so neither would fail CI (`X-CI-2` in tasks_02).

```diff
// .eslintrc
- 'no-restricted-imports': ['warn', { ... }],
+ 'no-restricted-imports': ['error', { ... }],

- 'local-rules/no-hardcoded-colors': 'warn',
+ 'local-rules/no-hardcoded-colors': 'error',
```

`yarn lint` now fails CI if anyone reintroduces a bare `<Text>` or a hardcoded color outside the exempted paths.

## Step 6.3 — Custom font decision

**Status (2026-10-01):** ⏸ F-APP-3 kept custom fonts out ("deliberately not"); Q2 is open. In practice Option B already happens outside the theme: Roboto Condensed draws figures in 19 files, the v2 date range bar among them (`src/components/v2/DateRangeSheet/layout.bar.js:76-80`); OpenSans has 0 uses.

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

**Status (2026-10-01):** ⏸ F-APP-3 deferred it ("deliberately not: redux-persist for theme"); the theme is still server-only (`auth.user.theme`). The dependency claim below is corrected in place.

Problem: current theme is backend-only via `auth.user.theme`. On cold start / fresh install / logout, the user briefly sees the wrong theme until the user object loads.

Solution: persist the `theme` Redux slice locally via `redux-persist` ~~(already in dependencies)~~ (_2026-10-01:_ not a dependency of the app).

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

**Status (2026-10-01):** ⬜ both remain: Settings (`src/screens/Common/Settings/index.js:26`) and `VersionInfo`'s theme modal (`src/components/VersionInfo/index.js:87-98,381-385`).

Audit found two places that toggle theme:

- `src/screens/Common/Settings/index.js` (primary)
- `src/components/VersionInfo/index.js` (duplicate)

Remove the `VersionInfo` toggle. Keep the single source of truth in Settings.

## Step 6.6 — Accessibility audit

**Status (2026-10-01):** ❔ no TalkBack or VoiceOver pass is recorded. v2 code carries 29 `accessibilityRole`, 25 `accessibilityLabel`, 13 `accessibilityState` and 2 live regions (`src/components/v2/ListStates.js:132`, `RangeSummary.js:310`); no app code reads reduce motion (⬜ item 4).

For each of the 20 highest-traffic screens, run through:

1. **TalkBack (Android)** — every interactive element is reachable, labeled, and has appropriate role
2. **VoiceOver (iOS)** — same
3. **Color inversion / grayscale** — UI remains navigable
4. **Reduced motion** (iOS Settings → Accessibility → Motion) — any react-native-reanimated usage must respect `AccessibilityInfo.isReduceMotionEnabled()`
5. **Contrast** — run through the `wcag-contrast` test results per screen

Any a11y bugs found get fixed. Add `accessibilityLabel`, `accessibilityRole`, `accessibilityHint` props to custom components.

## Step 6.7 — Apple-grade polish checklist

**Status (2026-10-01):** 🟡 v2 has spacing tokens through `Box` (`src/components/v2/Box.js:82-87`), `TARGET` 44 with hit-slop helpers (`src/theme/layout.js:35,45`); missing: icon-size and motion tokens (glyph sizes are per-screen constants), elevation by surface tiers, haptics, focus states. Safe area: the root still pads all four insets and v2 lists add the bottom one again — F-APP-8, deferred by the user on 2026-09-06.

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

**Status (2026-10-01):** ⬜ not installed; Q4 is open.

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

**Status (2026-10-01):** ⬜ two themes only (`src/theme/themes/index.js:9`).

Add one more theme to `THEMES[]` after migration is complete. Suggested: a "high-contrast light" theme for very-low-vision users. Palette:

- Background: pure white (`#ffffff`)
- Text: pure black (`#000000`)
- Primary: navy (`#000080`)
- All roles bumped to ≥7:1 contrast

Ship it. Contrast tests pass automatically (Phase 6.1).

Success criterion: adding this theme is a **one-file change** (just create `src/theme/themes/highContrast.js`, add to `THEMES[]`). If it requires touching anything else, the architecture has a leak.

## Step 6.10 — Developer documentation (final)

**Status (2026-10-01):** 🟡 no `src/theme/README.md`; items 1, 2, 8, 9 and 10 are covered in `docs/testing.md:420-1073` and `AI.md:46-76` (why tokens and uncapped text, the primitives, the type scale and its harness, pitfalls such as a line height scaled twice); the variant, colour-role and spacing sheets and "how to add a theme or a brand colour" are not written.

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

**Status (2026-10-01):** 🟡 a handoff exists in another form: `.design-sync/web/build.mjs` builds the v2 primitives for the web and derives `tokens.css` from the token modules, synced to claude.ai/design (`d0fbd081`, 2026-09-15); there is no Figma Tokens JSON export.

Generate a design tokens file for the design team:

```sh
# one-off script in scripts/export-design-tokens.js
# reads src/theme/tokens/* and outputs a JSON compatible with Figma Tokens / Tokens Studio
```

Design team imports into Figma so mockups stay in sync with code.

## Step 6.12 — Migration retrospective

**Status (2026-10-01):** ❌ no app-wide migration happens under D11; the redesign keeps decision logs per screen instead.

Once all phases are complete, hold a team retro. Document in `docs/todos/design-system/RETRO.md`:

- What worked
- What didn't
- Which patterns need refinement
- Open debt (screens that got minimal migration, non-text components that could use similar treatment)
- Candidate follow-ups: component library (reusable Card/ListRow primitives), dark mode preview in design, E2E test theming

---

## Phase 6 deliverables

**Status (2026-10-01):** 🟡 delivered in part: lint at `error` (v2 scope), developer docs (in `docs/testing.md` and `AI.md`), a design-token export (to claude.ai/design). Not delivered: contrast tests, font decision, persistence, the single theme toggle, Material You, a high-contrast theme, the retrospective.

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

**Status (2026-10-01):** ❔ not run here; device and screen-reader work.

```sh
yarn test                    # contrast tests pass
yarn lint                    # zero warnings, zero errors
yarn android                 # Material You works on Android 12+
yarn ios                     # VoiceOver audit clean
```

Manual: full accessibility audit (TalkBack/VoiceOver) on top-20 screens. Contrast report exported and reviewed.
