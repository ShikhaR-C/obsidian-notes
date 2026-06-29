# Phase 3 — Color System

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

Finalize `src/theme/tokens/fixed.js`. Status colors, backdrop, brand tokens. This file is imported by any component that needs a value that **must not** change per theme.

Consumers access via `theme.fixed.success`, `theme.fixed.brand.iocl.primary`, etc.

## Step 3.4 — Extract brand colors from SVG logos

For each brand logo in `src/components/SVG/psoc/` (IOCL, NAYARA, HPCL, BPCL, SHELL, JIO_BP):

1. Read the SVG component
2. Extract the hex values used (these are baked into `fill=` / `stroke=` props)
3. Promote the primary + secondary brand colors into `fixed.brand.<brand>` in `tokens/fixed.js`
4. Update the SVG component to reference the fixed token via `useAppTheme().fixed.brand.iocl.primary`

This makes brand colors centrally discoverable. A brand repaint is now a one-line change in `fixed.js`.

**Note**: minor tertiary colors inside the SVG paths (gradients, highlights) can stay hardcoded — we're hoisting the brand-identity colors only.

## Step 3.5 — Migrate the top-20 hardcoded-color hotspots

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

The audit flagged 3+ files where `colors.placeholder` fails WCAG AA in dark mode (rgba 0.54 on near-black). The new `onSurfaceVariant` role has adequate contrast. Update the Dark theme's `placeholder` alias to point to a value computed from `onSurfaceVariant` + an appropriate alpha:

```js
// src/theme/themes/dark.js
placeholder: hex_alpha(palette.gray300, 0.7, palette.gray900),  // contrast-verified
```

Spot-check: `src/screens/Dealer/Customers/CustSettings.js:91`, `SetDiscBS.js:359/389`.

## Step 3.8 — Verify Paper components pick up new colors

`toPaperTheme.js` already passes the full color set to Paper. Spot-check by rendering:

- `<Button mode="contained">` — uses `primary` + `onPrimary`
- `<Button mode="outlined">` — uses `outline`
- `<Chip selected>` — uses `secondaryContainer`
- `<Snackbar>` — uses `inverseSurface` + `inverseOnSurface`
- `<Appbar.Header>` — uses `surface` (MD3)
- `<Dialog>` — uses `surface` + backdrop
- `<FAB>` — uses `primaryContainer` (MD3)

## Step 3.9 — Run ESLint with warnings on

```sh
yarn lint
```

Expected: warnings in any file still containing a hardcoded color. Don't gate CI yet. Count the warnings; target = zero outside `SVG/psoc/` and `tokens/`.

## Step 3.10 — Create migration tracking doc

Append to `10_TASKS.md` (the master checklist) a section listing every remaining file with hardcoded colors, sorted by count. Engineers pick from the top as background cleanup. Phase 5 picks up any stragglers as part of its screen-by-screen pass.

---

## Phase 3 deliverables

| Artifact                                    | File path                                                                 |
| ------------------------------------------- | ------------------------------------------------------------------------- |
| Extended `colors` on Light/Dark/Neon themes | `src/theme/themes/{light,dark,neon}.js`                                   |
| Fixed brand tokens                          | `src/theme/tokens/fixed.js` (finalized, brand colors extracted from SVGs) |
| ESLint rule                                 | `src/theme/lint/no-hardcoded-colors.js` + config entry                    |
| Migrated top-20 hotspots                    | Listed files                                                              |
| Fixed SVG logos                             | `src/components/SVG/psoc/**` updated to use `fixed.brand.*`               |
| Contrast fixes                              | Placeholder / disabled usage fixed in flagged files                       |

## Verification

```sh
yarn lint                    # target: 0 hardcoded colors outside exempted paths
yarn android && yarn ios     # switch Light/Dark/Neon — no missing colors, no broken screens
```

Manual: render the Paper component gallery (Button/Chip/Dialog/Snackbar) in all three themes. Manually verify WCAG AA on the previously flagged files.
