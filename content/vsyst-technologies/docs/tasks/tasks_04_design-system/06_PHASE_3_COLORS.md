# Phase 3 — Color System

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Built only where D11 points it: v2 code holds 0 hex and 0 `rgb(` literals, enforced by a scoped ESLint block at `error`, and reads every colour as a token. The semantic MD3 role set and the fixed tokens were not built — the theme restates the legacy palette key for key so v1 cannot change — and the v1 migration steps are superseded. Of the 10 steps: 1 done, 2 to do, 6 dropped or superseded, 1 unverifiable. The review found one real contrast gap in v2 (T04-N2 in [00_README](./00_README.md)). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

**Goal**: Eliminate the 1,500+ hardcoded color strings. Everything resolves through semantic theme roles. Fixed brand colors are explicit.

**Entry criteria**: Phase 1 + Phase 2 complete. `AppText`/`AppBox` are available.

**Exit criteria**:

- Zero hardcoded hex / rgb / rgba in `src/screens/` and `src/components/` **outside of** `src/components/SVG/psoc/` (brand logos) and `src/theme/tokens/`
- `no-hardcoded-colors` ESLint rule active at `"warn"` level
- Every existing custom color key (`link`, `success`, `gray`, `antiText`, `white`, `black`) is either renamed to a semantic role or moved to `fixed.js`
- Fixed brand tokens are defined and used by SVG components
- The existing `Light` / `Dark` shape is preserved via the shim so legacy consumers keep working
- Dark/Light/Neon all render without missing colors

---

## Step 3.1 — Finalize semantic color roles

**Status (2026-10-01):** ⬜ the themes carry the legacy keys (`src/theme/tokens/palette.js:10-55`) plus `vehiclePlate` (`:64-71`); `src/theme` has 0 container, tertiary, inverse, `outlineVariant` or `scrim` roles.

Extend `src/theme/themes/light.js` and `dark.js` with the **full MD3 role set** plus app-specific extensions:

```js
colors: {
  // MD3 — primary family
  primary, onPrimary, primaryContainer, onPrimaryContainer,

  // MD3 — secondary family
  secondary, onSecondary, secondaryContainer, onSecondaryContainer,

  // MD3 — tertiary family (new for our app)
  tertiary, onTertiary, tertiaryContainer, onTertiaryContainer,

  // MD3 — error family
  error, onError, errorContainer, onErrorContainer,

  // MD3 — surfaces
  background, onBackground,
  surface, onSurface,
  surfaceVariant, onSurfaceVariant,
  surfaceContainerLowest, surfaceContainerLow, surfaceContainer,
  surfaceContainerHigh, surfaceContainerHighest,

  // MD3 — outlines
  outline, outlineVariant,

  // MD3 — inverse (snackbars, inverse UI)
  inverseSurface, inverseOnSurface, inversePrimary,

  // MD3 — utility
  shadow, scrim, surfaceTint,

  // App extensions (custom, keep minimal)
  link, onLink,
  disabled, onDisabled,
  placeholder,
}
```

## Step 3.2 — Map existing custom color keys

**Status (2026-10-01):** ❌ superseded by parity — the legacy keys are the theme's own keys, so there is nothing to alias; `colors.white` is no longer `rgba 0.7` (opaque since 2026-05-01, `0c28903a`).

| Old key                     | New semantic                                            | Notes                                                     |
| --------------------------- | ------------------------------------------------------- | --------------------------------------------------------- |
| `colors.white` (rgba 0.7)   | `colors.surfaceTint`                                    | It was a translucent overlay; surfaceTint is the MD3 role |
| `colors.black` (rgba 0.7)   | `colors.scrim`                                          | It was a backdrop; scrim is the MD3 role                  |
| `colors.gray`               | `colors.outline`                                        | Borders, dividers                                         |
| `colors.antiText`           | `colors.inverseOnSurface`                               | It was inverse text; that's literally inverseOnSurface    |
| `colors.link`               | `colors.link` (app extension)                           | Keep, but as a first-class semantic                       |
| `colors.success`            | `theme.fixed.success`                                   | Moved out of theme, into invariants                       |
| `colors.border`             | `colors.outlineVariant`                                 | Softer border                                             |
| `colors.card`               | `colors.surfaceContainer`                               | Elevated surface                                          |
| `colors.notification`       | `colors.error`                                          | Used in the notification dot/pill context                 |
| `colors.placeholder`        | `colors.onSurfaceVariant` at 60% alpha (via mix helper) | Old value failed WCAG AA in dark mode                     |
| `colors.disabled`           | `colors.disabled` (keep app extension)                  | Explicitly track it                                       |
| `colors.elevation.level0-5` | keep on theme (Paper uses it)                           |                                                           |

Update all theme objects so old keys still resolve during migration — add aliases during Phase 3, remove them in Phase 6:

```js
// src/theme/themes/light.js
colors: {
  // new semantic:
  primary: ..., onPrimary: ..., /* ... */
  // legacy aliases (marked @deprecated) — removed in Phase 6:
  white:  'rgba(255, 255, 255, 0.7)',
  black:  'rgba(0, 0, 0, 0.7)',
  gray:   '#BDBDBD',
  antiText: 'rgb(229, 229, 231)',
  // ...
}
```

## Step 3.3 — Define fixed tokens

**Status (2026-10-01):** ⬜ no `fixed.js`; `success` is a themed palette key with the same value in both schemes (`palette.js:31,54`).

Finalize `src/theme/tokens/fixed.js`. Status colors, backdrop, brand tokens. This file is imported by any component that needs a value that **must not** change per theme.

Consumers access via `theme.fixed.success`, `theme.fixed.brand.iocl.primary`, etc.

## Step 3.4 — Extract brand colors from SVG logos

**Status (2026-10-01):** ❌ skipped in F-APP-3 — the PSOC SVGs hold hundreds of illustration hexes with no clean list (02-foundations); 1,133 hex literals remain under `src/components/SVG/`.

For each brand logo in `src/components/SVG/psoc/` (IOCL, NAYARA, HPCL, BPCL, SHELL, JIO_BP):

1. Read the SVG component
2. Extract the hex values used (these are baked into `fill=` / `stroke=` props)
3. Promote the primary + secondary brand colors into `fixed.brand.<brand>` in `tokens/fixed.js`
4. Update the SVG component to reference the fixed token via `useAppTheme().fixed.brand.iocl.primary`

This makes brand colors centrally discoverable. A brand repaint is now a one-line change in `fixed.js`.

**Note**: minor tertiary colors inside the SVG paths (gradients, highlights) can stay hardcoded — we're hoisting the brand-identity colors only.

## Step 3.5 — Migrate the top-20 hardcoded-color hotspots

**Status (2026-10-01):** ❌ D11 — v1 screens are never restyled; v1 keeps 453 quoted hex literals in 99 files and 204 `rgb(a)(` in 96; v2 has none.

From the audit, these are the 20 files with the most hardcoded colors. Process them as a dedicated sprint:

1. `src/components/Prompt/index.js` (9)
2. `src/screens/Customer/NewOrder/components.js` (7)
3. `src/screens/Common/Orders/components/FilterList.js` (7)
4. `src/screens/Dealer/Payments/BSheets/AttachInvs.js` (6)
5. `src/screens/Dealer/Orders/index.js` (6)
6. `src/screens/Customer/Orders/index.js` (6)
7. `src/screens/Common/Orders/index.js` (6)
8. `src/screens/Common/Orders/bottomsheet/filter.js` (6)
9. `src/components/Input/IconInput.js` (6)
10. `src/screens/Dealer/ProductDates/SetProductRate.js` (5)
11. `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js` (5)
12. `src/screens/Customer/Vehicles/vehicleComponents/index.js` (5)
13. `src/screens/Customer/NewPayment/index.js` (5)
14. `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js` (5)
15. `src/screens/Common/Reports/DailyReport/components.js` (5)
16. `src/screens/Common/Payments/components/index.js` (5)
17. `src/screens/Common/Orders/components/newDesign.js` (5)
18. `src/components/NumberMeter/logic.js` (5)
19. `src/components/NumberMeter/index.js` (5)
20. `src/screens/Login/AuthNavigator/Welcome.js` (4)

**Migration pattern** for each file:

```js
// BEFORE
const styles = StyleSheet.create({
  card: { backgroundColor: "#ffffff", borderColor: "#d8d8d8" },
  header: { color: "rgb(59, 129, 246)" },
});

// AFTER
import { useAppTheme } from "~/theme";
const MyComponent = () => {
  const theme = useAppTheme();
  return (
    <View
      style={{
        backgroundColor: theme.colors.surface,
        borderColor: theme.colors.outlineVariant,
      }}
    >
      <Text style={{ color: theme.colors.link }}>...</Text>
    </View>
  );
};
```

Or, preferably:

```js
<AppBox bg="surface" borderColor="outlineVariant" borderWidth={1}>
  <AppText variant="titleSmall" color="link">
    ...
  </AppText>
</AppBox>
```

For styles that must live in `StyleSheet.create` (e.g., performance-critical lists), use the `makeStyles(theme)` pattern:

```js
const makeStyles = (theme) =>
  StyleSheet.create({
    card: {
      backgroundColor: theme.colors.surface,
      borderColor: theme.colors.outlineVariant,
    },
  });

const MyList = () => {
  const theme = useAppTheme();
  const styles = useMemo(() => makeStyles(theme), [theme]);
  // ...
};
```

## Step 3.6 — Write the `no-hardcoded-colors` ESLint rule

**Status (2026-10-01):** ✅ for the v2 scope, as a `no-restricted-syntax` block in `eslint.config.js:42-76` (hex, `rgb(`, literal `fontSize`, JSX copy) at `error`, pinned by `src/theme/__tests__/eslintRule.test.js`; no custom rule file; app CI runs no lint (`X-CI-2` in tasks_02).

Create `src/theme/lint/no-hardcoded-colors.js`. Skeleton:

```js
// src/theme/lint/no-hardcoded-colors.js
module.exports = {
  meta: {
    type: "suggestion",
    docs: {
      description: "Disallow hardcoded color literals outside of theme tokens",
    },
    messages: {
      hex: 'Hardcoded hex color "{{ value }}". Use theme.colors.* or theme.fixed.*.',
      rgb: 'Hardcoded rgb/rgba color "{{ value }}". Use theme.colors.* or theme.fixed.*.',
    },
  },
  create(context) {
    const filename = context.getFilename();
    if (filename.includes("src/components/SVG/psoc/")) return {};
    if (filename.includes("src/theme/tokens/")) return {};
    if (filename.includes("src/theme/themes/")) return {};

    return {
      Literal(node) {
        if (typeof node.value !== "string") return;
        if (/^#[0-9a-f]{3,8}$/i.test(node.value)) {
          context.report({
            node,
            messageId: "hex",
            data: { value: node.value },
          });
        }
        if (/^rgba?\(/i.test(node.value)) {
          context.report({
            node,
            messageId: "rgb",
            data: { value: node.value },
          });
        }
      },
    };
  },
};
```

Register it in the project's ESLint config as a local rule. Level: `"warn"` for Phase 3, `"error"` in Phase 6.

## Step 3.7 — Fix the placeholder-contrast bugs

**Status (2026-10-01):** ❌ D11 (v1 screens), and the premise does not hold: dark `placeholder` over `#121212` computes to ≈ 6.0:1, which passes AA (light over the grey background is 4.49:1). v2 draws `placeholder` in the date sheet (`CustomFields.js:151`).

The audit flagged 3+ files where `colors.placeholder` fails WCAG AA in dark mode (rgba 0.54 on near-black). The new `onSurfaceVariant` role has adequate contrast. Update the Dark theme's `placeholder` alias to point to a value computed from `onSurfaceVariant` + an appropriate alpha:

```js
// src/theme/themes/dark.js
placeholder: hex_alpha(palette.gray300, 0.7, palette.gray900),  // contrast-verified
```

Spot-check: `src/screens/Dealer/Customers/CustSettings.js:91`, `SetDiscBS.js:359/389`.

## Step 3.8 — Verify Paper components pick up new colors

**Status (2026-10-01):** ❌ superseded by `src/theme/__tests__/parity.test.js` — Paper's theme is byte-identical to the legacy one, and there is no third theme to check.

`toPaperTheme.js` already passes the full color set to Paper. Spot-check by rendering:

- `<Button mode="contained">` — uses `primary` + `onPrimary`
- `<Button mode="outlined">` — uses `outline`
- `<Chip selected>` — uses `secondaryContainer`
- `<Snackbar>` — uses `inverseSurface` + `inverseOnSurface`
- `<Appbar.Header>` — uses `surface` (MD3)
- `<Dialog>` — uses `surface` + backdrop
- `<FAB>` — uses `primaryContainer` (MD3)

## Step 3.9 — Run ESLint with warnings on

**Status (2026-10-01):** ❔ lint was not run here, and app CI has no lint job.

```sh
yarn lint
```

Expected: warnings in any file still containing a hardcoded color. Don't gate CI yet. Count the warnings; target = zero outside `SVG/psoc/` and `tokens/`.

## Step 3.10 — Create migration tracking doc

**Status (2026-10-01):** ❌ D11 — there is no v1 colour migration to track; current counts are in 02_AUDIT's review lines.

Append to `10_TASKS.md` (the master checklist) a section listing every remaining file with hardcoded colors, sorted by count. Engineers pick from the top as background cleanup. Phase 5 picks up any stragglers as part of its screen-by-screen pass.

---

## Phase 3 deliverables

**Status (2026-10-01):** 🟡 delivered: the ESLint guard (v2 scope). Not delivered: extended roles, `fixed.js`, brand tokens and SVG updates, the hotspot migration, the contrast fixes (premise doubtful), the neon theme.

| Artifact                                    | File path                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------- |
| Extended `colors` on Light/Dark/Neon themes | `src/theme/themes/{light,dark,neon}.js`                                   |
| Fixed brand tokens                          | `src/theme/tokens/fixed.js` (finalized, brand colors extracted from SVGs) |
| ESLint rule                                 | `src/theme/lint/no-hardcoded-colors.js` + config entry                    |
| Migrated top-20 hotspots                    | Listed files                                                              |
| Fixed SVG logos                             | `src/components/SVG/psoc/**` updated to use `fixed.brand.*`               |
| Contrast fixes                              | Placeholder / disabled usage fixed in flagged files                       |

## Verification

**Status (2026-10-01):** ❔ not run here; the guard's configuration is pinned in Jest on sample code, not over the v2 tree (`eslintRule.test.js:61-64`).

```sh
yarn lint                    # target: 0 hardcoded colors outside exempted paths
yarn android && yarn ios     # switch Light/Dark/Neon — no missing colors, no broken screens
```

Manual: render the Paper component gallery (Button/Chip/Dialog/Snackbar) in all three themes. Manually verify WCAG AA on the previously flagged files.
