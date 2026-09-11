# 05 — The landscape chrome-and-keyboard problem, and the path out

> **What this is:** the research and the plan behind one question asked on **2026-09-10** — _"if we make them landscape now, the keyboard would eat up half of the screen; the header, search and filter would cover the other half, leaving near to no space for content."_ The question was right, and the measurements below say it is worse than half.
> **Companions:** [[04-orientation-decisions]] (why v1 stays pinned; the three earlier questions), [[02-foundations#F-APP-9 — Orientation and large screens|02 §F-APP-9]] (the foundation), `dzzlo_oms_app/docs/testing.md` → "Window classes and orientation".
> **Status:** research COMPLETE, path PROPOSED. Nothing is built. Nothing starts before the user says "start".
> **Start here:** §5 (the composition matrix) and §6 (the yield ladder) are the two artifacts a screen actually uses. §1–4 are the evidence they rest on; §7 is the build order.

---

## 1. The measurement

Chrome heights computed from source constants (`ROW_TOP` 12, `SEARCH_MIN_HEIGHT` 44, `CHIP_PAD_V` 6, `TILE_PAD_V` 6, `SPACING.sm` 8, line heights from `src/theme/tokens/typography.js`), not estimated.

|                                  | @ fontScale 1.0 | @ 2.143                                  |
| -------------------------------- | --------------- | ---------------------------------------- |
| Chrome above the list, portrait  | 175             | **406** (→ 514 if the card's text wraps) |
| Chrome above the list, landscape | 191             | 298 (→ 406)                              |
| One `CustomerRow`                | 101             | 253 portrait / 190 landscape             |

**Rows that actually fit**, iPhone 14/15/16-class, header 44 (iOS), insets from `src/test/testUtils.js:69`:

| Window                             | @1.0                | @2.143                               |
| ---------------------------------- | ------------------- | ------------------------------------ |
| (a) portrait 390×844, no keyboard  | 544 pt → **5 rows** | 313 pt → **1 row** (0 if text wraps) |
| (b) portrait + keyboard 291        | 287 pt → **2 rows** | 56 pt → **ZERO**                     |
| (c) landscape 844×390, no keyboard | 134 pt → **1 row**  | 27 pt → **ZERO**                     |
| (d) landscape + keyboard 200       | **−45 pt**          | **−152 pt** (→ −260)                 |

Three readings that change what this project is:

1. **Landscape is broken before the keyboard appears.** Case (c): normal text, no keyboard, one row. The chrome (191 of 325 usable pt) has already taken the screen. The keyboard only turns a bad screen into a negative one.
2. **This is a live bug in PORTRAIT, today.** Case (b) at 2.143: **zero rows**. A user on iOS Accessibility Large, in portrait, on the shipped v2 Customers screen, who taps search, sees no results. That is on PR #51 — which is **not merged**, so no user can reach it today; it is a defect in code queued to ship, not a live bug. Orientation did not cause it; landscape would only have made it impossible to ignore.
3. **Enabling landscape trips a latent invariant violation.** `layout.js:144` states the rule: _"The CARD and the ROW both call this, and must … a window where one changes shape and the other does not is a table with a header that no longer heads it."_ But the card is handed `chromeColumn` (316 pt) and `CustomerRow` reads `contentWidth` (640 pt). At 2.143 in landscape the card stacks and the row does not — the forbidden state. It is unreachable today only because `shareChromeRow` requires `sizeClass !== 'compact'`, which is precisely the case being unlocked.

Also confirmed, smaller: the **bottom inset is double-counted** — `AppNavigatorContainer.js:133` pads `insets.bottom` (34) at the root and `index.js:339` adds `insets.bottom + spacing.md` (50) again. The last row sits 84 pt off the bottom, and the stated intent (list running under the home indicator) is defeated by the root padding.

## 2. What the platforms actually prescribe

Researched against the M3 spec, `developer.android.com`, Apple HIG and UIKit reference. The short version: **M3 has height classes but deliberately almost no height guidance**, and what exists points one way.

- **M3 height breakpoints** are compact < 480 / medium 480–899 / expanded ≥ 900 dp. Ours is `COMPACT_HEIGHT = 500` — a defensible widening, not a mismatch. Google annotates compact height as _"99.78 % of phones in landscape."_
- **Google's canonical compact-height sample** uses the height class for exactly one decision: `showTopAppBar`. **Drop the bar — not shrink it.**
- **M3's only prohibition at compact height:** _"two pane layouts are not practical."_
- **M3 forbids shrinking bars:** _"Always use the default height of the app bar… Don't make an app bar shorter than its default height."_ iOS _does_ shrink (nav 44→32, tab 49→32) but the **system** does it; you do not hand-tune it.
- **Apple's size-class table is decisive for two-pane.** Standard and Pro iPhones report **compact width even in landscape**; only Plus / Max / Air get regular. `UISplitViewController` therefore collapses automatically on most iPhones. This is why iOS 26 Mail keeps its list in landscape only on Pro Max and Air.

### The sanctioned answer for the keyboard case

Both platforms converge: **when the keyboard is open, search takes over the screen.**

|              | M3                                                                                       | Apple                                                          |
| ------------ | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Name         | _search view_ — "a full-screen modal"; **default for compact breakpoints**               | search field in a toolbar, activated                           |
| While typing | bar at top, results fill everything below                                                | field docks **above the keyboard**, results above it           |
| Chrome       | app bar replaced; nav bar covered by the keyboard _"until the search flow is completed"_ | `hidesBarsWhenVerticallyCompact`, restored by an unhandled tap |

Net budget: **one 56 pt bar + keyboard + every remaining point to results.** It removes the app bar, filter chips, sort row and summary card from the vertical budget **for exactly the interval in which none of them can be operated** — the thumbs are on the keyboard. Nothing is hidden that the user could otherwise use.

**Why departing from M3's width-only default is spec-consistent, not invention:** M3 says "docked" search from `medium` width up, but `DockedExpandedTableMinHeight = 240 dp` and a 390 pt window with a ~200 pt keyboard leaves ~190. The docked variant's own minimum exceeds the space. M3's height escape clause — _"adjust the layout when available vertical space is unusually small"_ — is the sanctioned reading.

**Android reached this first.** `IME_FLAG_NO_FULLSCREEN` documents the exact scenario: _"small screens in landscape orientation where displaying a software keyboard may occlude such a large portion of the screen that the remaining part is too small to meaningfully display the application UI."_ The OS default was fullscreen extract mode — the whole screen to the keyboard. Gboard's 2023 auto-floating landscape keyboard is the same conclusion reached again.

### Chrome binds to STATE, not to scroll

`enterAlways`, `exitUntilCollapsed` and iOS large-title collapse are all gesture-driven and instantly reversible — the wrong mechanism here. There is no scroll gesture while typing, and `enterAlways` returns the bar on _any_ downward scroll, re-stealing the height the moment the user nudges the result list. **Latch on `(compactHeight ∧ keyboardVisible)`, restore on blur.** Precedents: `hidesBarsWhenVerticallyCompact` (size-class-triggered) and M3's _"temporarily covered … until the search flow is completed."_

### Filters go in a SIDE SHEET, not the navigation rail

M3 forbids the rail for this twice: the rail's anatomy admits only destinations, a menu and a FAB; and the expanded page says _"For sorting, filtering, or secondary navigation, use tabs or other components directly in the pane."_ The right component is a **side sheet** — max 400 dp, spans the screen height, trailing edge, and M3's own example use is _"a list of actions that affect the screen's primary content, such as filters."_ Android's landscape guide: _"For a filter sheet, the sheet component can change to a side sheet."_

## 3. Decisions that are already settled by evidence

**The native header search bar is OFF THE TABLE.** React Navigation v7 documents it: _"if you specify a custom header, the native functionality such as large title, search bar etc. won't work."_ This app sets a custom `header` in **33 navigator definitions**, including `Dealer/Main.js:61` — the stack Customers lives in. Three further reasons even without that: `RNSSearchBar.mm` sets no font, so iOS text scales on **UIKit's curve, not `useTypeScale()`'s**, unalignable and un-opt-out-able (straight through the font-scale non-negotiable); the landscape placement is undocumented by Apple **and** unqueryable from JS; and the required `contentInsetAdjustmentBehavior="automatic"` hands top-inset control to UIKit, colliding with `Screen`/`Container`'s existing accounting. Revisit only as part of a separate decision to retire `CustomHeader` app-wide, and not before react-native-screens ≥ 4.27 (we are on 4.24.0, missing the 4.26.0 Android rotation fix, PR #4264).

**`CustomHeader` costs us twice in landscape.** `CustomHeader.js:52` is `height: Platform.OS === 'ios' ? 44 : 56` — a hard constant. It blocks the native search bar _and_ forfeits UIKit's automatic 44→32 compact-height shrink. The upside: because the header is ours, `headerShown: false` by window class is fully in our control, which is exactly Google's canonical compact-height move.

**Two-pane list/detail is a tablet/foldable pattern, not a landscape-phone one.** Discouraged by Android at compact height, and auto-collapsed by UIKit on every iPhone that is not a Plus/Max/Air. It stays available where width _and_ height are regular. It is not the answer here.

**A codemod keyed on `<TextInput` will not work.** Grepping `<TextInput` finds **1** file with 3+ inputs; the real number is **20**. Entry goes through wrappers — `IconLabelInput` (45 uses), `BottomSheetTextInput` (22), `IconInput` (17) — and several forms render N fields from a mapped `FORM_FIELDS` array behind one JSX tag. Any sweep keyed on the raw component misses ~95 % of the forms.

## 4. What the app looks like today

From the v1 survey — 59 screen directories: **12 forms · 31 lists · 4 detail · 12 mixed**.

- **17 of the 31 list screens put a search field above the list.** The nine transaction screens (`{Common,Customer,Dealer}/{Invoices,Orders,Payments}`) render a search row, _then_ a filter-chip row, _then_ the list — with the keyboard open by definition.
- `Common/Vehicles` and `Customer/Vehicles` use `stickyHeaderIndices={[0]}`, so the search **cannot scroll away** to reclaim height.
- **Keyboard awareness is essentially absent:** 1 screen reads real keyboard height, 1 uses an Android-only hook, 5 track a boolean, **52 directories do nothing**.
- Only 6 files use `KeyboardAvoidingView`; two use `behavior="height"`, which shrinks the form. Both `CompanyProfile` screens have **7 inputs in a bare `ScrollView`** with no keyboard handling.
- Both `TrnTab.js` files already set `tabBarHideOnKeyboard: true` — so **"chrome yields to the keyboard" is already house practice** at the navigator level. This work extends the same principle to the screen's own chrome bands. Customers is in the drawer stack, **not** the tab stack, so it has no yielding chrome at all today.
- `src/components/TabBarAnimated/` imports `Keyboard` and `KeyboardAvoidingView`, uses neither, and is referenced by no navigator. Dead code, not prior art.

## 5. The composition matrix

**This is the organising artifact.** Decided once, applied to every screen — so a screen iteration asks "which cell am I in?" rather than re-litigating layout.

### The two axes, and why neither is "orientation"

The columns are **width class × height class**, never portrait/landscape. Orientation is not a design target: a phone on its side and a fold opened in landscape are both "landscape" and need _opposite_ treatments, because one is starved of height and the other is not. The codebase already votes this way — `isLandscape` is exposed by `useWindowClass()` and used by **zero screens**.

|                   | `compact` < 600                              | `medium` 600–839                                       | `expanded` ≥ 840                                         |
| ----------------- | -------------------------------------------- | ------------------------------------------------------ | -------------------------------------------------------- |
| **tall** (≥ 500)  | phone portrait 390×844 · fold cover ~320×820 | fold open portrait ~690×840 · tablet portrait 768×1024 | fold open landscape ~840×690 · tablet landscape 1024×768 |
| **short** (< 500) | rare — Flip cover, small floating window     | small phone landscape 667×375                          | **phone landscape 844×390 ← the hard case**              |

**Only the bottom row is hard, and only one cell in it is common.** Every fold state is in the _tall_ row. That is the headline: **the fold is the payoff, not the problem** — unfolded you gain ~300 dp of width and keep your height.

### The matrix

Bands run across and eat height. Rails and sheets run down the edges and eat width. The rule is: **chrome lives on the axis that has room.**

| Region           | compact / tall                 | medium / tall                                                    | expanded / tall                                      | expanded / short (+ medium/short)                               |
| ---------------- | ------------------------------ | ---------------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| **Navigation**   | drawer + bottom tabs, as today | drawer + tabs                                                    | **navigation rail**, leading edge, destinations only | rail collapsed, or drawer only — no tabs                        |
| **Header**       | shown, full                    | shown                                                            | shown                                                | **hidden while typing** (`headerShown: false`); shown otherwise |
| **Search**       | band, full width               | band inside `Container` (640)                                    | band at top of the content pane                      | band — **never yields**                                         |
| **Filters**      | chip band                      | shares one row with the summary (**decision 70, already built**) | **side sheet**, trailing edge, persistent, ≤ 400 dp  | **button + count badge** → modal sheet                          |
| **Summary card** | card band                      | shares the row with filters                                      | top of the side sheet, or its own row                | **hidden**                                                      |
| **List**         | full width, single column      | contained at `READABLE_WIDTH` 640                                | contained 640, leading pane                          | full height, full width                                         |
| **Detail**       | pushed route                   | pushed route                                                     | **second pane — legitimate only here**               | pushed route — _never_ a pane                                   |
| **Drawer**       | 60 % (today)                   | **capped** at a fixed max                                        | capped                                               | capped                                                          |

Three cells carry the whole design:

- **`compact / tall` is today.** Pixel-identical to what was signed off. `Container` is a plain full-width View in `compact`, so nothing moves.
- **`expanded / tall` is the upside.** Rail + contained list + a real detail pane. This is the fold and the tablet, and the only cell where two-pane is sanctioned: Android calls two-pane _"not practical"_ at compact height, and Apple's size classes put standard and Pro iPhones at **compact width even in landscape**, so `UISplitViewController` collapses automatically there.
- **`expanded / short` is the fight.** Everything that can go, goes.

## 6. The yield ladder

The matrix says **where** chrome lives. It cannot say **how much survives**, because two pressures shrink the list independently and only one of them is a window class:

1. **Available height falls** — landscape, or the keyboard opening.
2. **Chrome grows** — the text scale. Between `fontScale` 1.0 and 2.143 the chrome above the Customers list goes **175 pt → 406 pt**.

A fixed `COMPACT_HEIGHT` threshold catches (1) and misses (2) entirely. Portrait 390×844 with a 291 pt keyboard leaves 553 pt of window — comfortably above 500, so **not** `compactHeight` — and yet at 2.143 the list gets 56 pt and renders **zero rows**. The threshold would say the window is fine while the screen is unusable.

So the runtime rule is a **budget**, not a breakpoint:

```
listBudget = availableHeight − headerHeight − chromeHeight
where availableHeight = windowHeight − keyboardInset

yield the next region while listBudget < MIN_ROWS × rowHeight
```

Every input is already computable: `rowHeight` and each band come from `layout.js` at the live `fontScale`, `keyboardInset` from A1, `availableHeight` from A2.

**The ladder** — the order regions surrender, derived from importance rather than assigned per screen:

| Rank | Region                 | Why it goes here                                                                                        |
| ---- | ---------------------- | ------------------------------------------------------------------------------------------------------- |
| 1    | Summary card           | Information, not a control. Nothing breaks without it.                                                  |
| 2    | Filter chips           | Collapse to one button carrying a count — the state stays legible.                                      |
| 3    | Header                 | Ours to hide, and Google's canonical compact-height move is to **drop** the top app bar, not shrink it. |
| 4    | Navigation (tabs/rail) | Already house practice — both `TrnTab.js` files set `tabBarHideOnKeyboard: true`.                       |
| —    | **Search**             | Never yields. It is why the keyboard is open.                                                           |
| —    | **List**               | Never yields. It takes the whole remainder.                                                             |

**Hide, never shrink.** M3 is explicit: _"Always use the default height of the app bar… Don't make an app bar shorter than its default height."_ iOS does compact its bars 44→32, but the system does that; you do not hand-tune it.

**Latch on state, not scroll.** `enterAlways` / `exitUntilCollapsed` / iOS large-title collapse are all gesture-driven and instantly reversible — wrong here, because there is no scroll gesture while typing and any downward nudge re-steals the height. Latch on `(budget short ∧ keyboardVisible)`, restore on blur.

**Open decision — `MIN_ROWS`.** Recommend **3** as the target with a floor of **2**: below about two and a half rows a list stops reading as a list. Needs a device look before it is fixed.

## 7. The path

Every step is red → green → mutation smoke, per [[01-tdd-workflow]]. No new npm packages.

### Phase A — the signal (foundation, no screen changes)

**A1. `useKeyboardInset()`** — a house hook under `src/theme/provider/`. RN 0.84 core ships `Keyboard` listeners and `endCoordinates.height` but **no hook**, so this is house code. The contract below is settled, read from RN 0.84.1's own Android source (§10).

- Listen to `keyboardDidShow` / `keyboardDidHide` on **both** platforms (add `keyboardWillShow`/`Hide` on iOS for animation timing).
- Return the overlap to add to content that **already pays `insets.bottom`**:
  - **iOS:** `max(0, keyboardHeight - insets.bottom)`
  - **Android:** `keyboardHeight` unchanged — RN has already subtracted the bars
- The per-platform branch exists for exactly one reason, and it is NOT "one resizes and one overlays": it is that **Android's reported height is already net of the system bars and iOS's is not**. Worth ~34 pt in a 390 pt window.
- Pin the branch with a test. It is the single most bug-prone line in the feature.

**A2. Pure arithmetic in `src/theme/layout.js`** — `availableHeight(height, keyboardInset)` and the budget check, beside `contentWidthOf` / `isCompactHeight`. React-free, so it gets a Tier-1 suite like `sizeClassOf`.

**A3. `useWindowClass()` exposes it**, so screens keep reading the window through the one hook the non-negotiable requires. This deliberately breaks `src/theme/__tests__/useWindowClass.test.js:124-134`, whose "exposes exactly the documented shape" assertion pins the key list to exactly six — that test is the change's own gate.

**A4. Harness.** `src/test/fontScale.js` gains the key in its override record (`:38`, `:54`) plus a `withKeyboard(n, fn)` beside `withFontScale`; `src/test/testUtils.js` adds it to `renderScreen`'s destructure and its `setWindow(...)` call at `:150-152`.

**A5. Insets become a `renderScreen` option.** `INITIAL_METRICS` (`testUtils.js:69`) is a frozen constant, so a `{ width: 844, height: 390 }` landscape test today runs with **portrait insets**. Until this is fixed no landscape assertion is truthful, which makes it a prerequisite for every phase below, not a nicety.

### Phase B — the yield ladder (Customers as the reference)

**B1. Implement the ladder** from §6, latched on state. Fixes the `expanded / short` cell **and** the `fontScale` 2.143 portrait failure with one rule — they are the same defect seen from two directions.

**B2. The list stops fighting the keyboard.** `listPadding` (`index.js:339`) is already the seam — `insets.bottom + spacing.md` gains the keyboard inset. Never `KeyboardAvoidingView` on a list. Fix the double-counted bottom inset in the same pass.

**B3. Fix the card/row stacking disagreement** (§1.3) _before_ landscape is enabled, since enabling it is what makes the bug reachable.

### Phase C — the wide cells

**C1. Cap the drawer width.** `Drawer.js:70` is `width: '60%'` — a percentage. Unfolded that jumps ~192 → ~414 pt, and in landscape it would be 506 pt against M3's 360 dp cap. It is also the trigger for the logged drawer-flash-on-rotation bug (`react-native-drawer-layout` springs the closed offset to the new width). Small change, unblocks every wide cell, kills a known bug.

**C2. Filters into a side sheet** for `expanded / tall`, trailing edge, ≤ 400 dp. `index.js:448` already places the same chips/card in two arrangements under decision 70 — this is that pattern extended, not a new mechanism.

**C3. Navigation rail** for `expanded / tall`, destinations only. M3 forbids filters and sort in the rail: _"For sorting, filtering, or secondary navigation, use tabs or other components directly in the pane."_

### Phase D — per-screen judgement

**D1.** Screens with 3+ inputs stay `orientation: 'portrait'`. A form has no landscape job on a phone; per-screen orientation exists precisely so that can be said. The 12 form directories are the default-portrait set.

**D2.** The 17 search-above-list screens are the population that would benefit from B1 — but only once redesigned. They are v1, and per the 2026-09-10 decision v1 is never unlocked.

**D3. Two-pane detail** is a per-screen design session, and only for `expanded / tall`. Not scheduled.

## 8. Honest limits

**Landscape on a phone will never beat portrait for search-and-browse.** Portrait with the keyboard open gives ~287 pt of list (2 rows at 1.0); landscape at its best gives ~134 pt (1 row). The goal is _usable_, not _better_.

Which raises the real product question, and it is not a technical one: **which screens have a landscape job worth doing?** A wide ledger or invoice-line table genuinely wants landscape. A list of customer names you search mostly does not. Per-screen orientation is where that call gets made, screen by screen.

## 9. Open questions

1. ~~**Does landscape need to reach v1 at all?**~~ ✅ **DECIDED by the user 2026-09-10: landscape is for redesigned v2 screens only. v1 is never unlocked.** The portrait pin in the eight v1 stacks is permanent for the life of each v1 screen; a screen gains `orientation: 'all'` only by being redesigned, through `screenOptionsFor` in the registry. This retires the "unlock a chosen subset of v1" option floated in [[04-orientation-decisions]] §What follows — no registry extension for v1-only routes is needed, and no v1 screen is audited for landscape. The 133 module-scope `Dimensions.get` files and their 518 consumption sites are therefore left exactly as they are, and are deleted rather than fixed when their screen is replaced.
2. **The portrait `fontScale` 2.143 keyboard failure** — split out as its own fix, or folded into this work? _(Asked of the user 2026-09-10; unanswered.)_ **Scope note:** this is a defect in an UNMERGED branch, not a live production bug. Customers v2 is not on `slave` (PRs #49/#50/#51 all open on 2026-09-10), so no user can reach the screen. It should be fixed before the merge queue drains, but nobody is hitting it today.

---

## 10. The keyboard contract, settled from RN 0.84.1 source

Web research stalled repeatedly, so this was answered from `node_modules/react-native/ReactAndroid/` directly — which is the authority anyway. **The model this plan started from was wrong, and the correction matters.**

**The wrong model** (stated earlier in this session): Android `adjustResize` shrinks the window, so `useWindowDimensions().height` drops there and a JS keyboard inset should be `0` on Android and the real height on iOS.

**What RN 0.84.1 actually does:**

1. **`useWindowDimensions().height` does NOT change when the keyboard opens — on either platform.** `DisplayMetricsHolder.initDisplayMetrics` sets `windowDisplayMetrics = context.resources.displayMetrics`, which tracks the _configuration_ (rotation, fold, multi-window) and not IME visibility. `ReactRootView.checkForDeviceDimensionsChanges()` re-emits from that same source, and `DeviceInfoModule` caches the last value, so nothing is emitted on keyboard show/hide. The manifest's `adjustResize` does not reach the JS `Dimensions` API.
2. **`keyboardDidShow` fires on both platforms with a real height.** On API 30+ RN uses the modern inset API (`ReactRootView.java:964`), which is correct under edge-to-edge:
   ```java
   boolean keyboardIsVisible = rootInsets.isVisible(WindowInsets.Type.ime());
   Insets imeInsets = rootInsets.getInsets(WindowInsets.Type.ime());
   Insets barInsets = rootInsets.getInsets(WindowInsets.Type.systemBars());
   int height = imeInsets.bottom - barInsets.bottom;
   ```
3. **The real asymmetry is that last line.** Android's reported height is **already net of the system bars**; iOS's `endCoordinates.height` is the raw overlap from the bottom of the screen and **includes** the home-indicator region. So combining the keyboard height with `useSafeAreaInsets().bottom` **double-counts on iOS and not on Android** — about 34 pt, in a window with 390 to spend.
4. Therefore `compactHeight` must derive from `height - keyboardInset` on **both** platforms. There is no platform where the window "already paid".

### A separate finding worth its own look

`android/build.gradle` sets **`targetSdkVersion = 36`**, so the OS enforces edge-to-edge (Android 15 enforces it for targetSdk 35+; Android 16 removed the `windowOptOutEdgeToEdgeEnforcement` escape hatch). Meanwhile RN's own `isEdgeToEdgeFeatureFlagOn` **defaults to `false`** (`WindowUtil.kt`), this app never calls `setEdgeToEdgeFeatureFlagOn()`, `react-native-edge-to-edge` is not installed, and `styles.xml` carries no opt-out. **The OS applies edge-to-edge while RN believes it is off.**

The keyboard math is unaffected (RN's path reads `Type.ime()` either way), but the mismatch plausibly explains the Android-only workaround already in the repo (`src/hooks/useKeyboardHeight.js`, consumed once by a bottom-sheet screen). Not part of this plan; flagged for its own investigation.

**Confidence:** items 1–4 are read directly from the vendored RN source and are high confidence. The Android 15/16 edge-to-edge _enforcement_ rule is from general platform knowledge and could not be re-verified here — **confirm on a device** before acting on the separate finding. iOS keyboard heights (~200 pt landscape, ~291–346 pt portrait) remain estimates and must be measured on device; the budget in §1 should be re-run with real numbers.
