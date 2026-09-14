# 07 — The four shape questions, answered, with the steps

> **What this is:** the four questions the user asked on **2026-09-13** about [[06-all-screen-shapes-plan]], recorded verbatim and answered from that doc, [[04-orientation-decisions]], [[05-landscape-chrome-and-keyboard]] and the code on PR #51. Written as a decision reference in the style of 04: the next person who asks "so how do we handle orientation?" gets this page, not a re-derivation.
> **Companions:** [[06-all-screen-shapes-plan]] (the plan this answers for), [[05-landscape-chrome-and-keyboard]] §5–7 (matrix, ladder, phases), [[02-foundations#F-APP-7|02 §F-APP-7]] (type scale as built), [[02-foundations#F-APP-9 — Orientation and large screens|02 §F-APP-9]] (window classes as built).
> **Status:** answers are SETTLED where they describe how the app already works (Q1, Q2 inputs 1–2, Q3 rules already built). **Steps S1–S4, S6, S8 STARTED 2026-09-13 for Customers** ("check the answers and then start") — see [[screens/01c-customers-shapes]] for the per-screen answers and the build map. The two Step 0 decisions in 06 §3 were DECIDED 2026-09-13: platform default for v1 on both Android and iPad, nothing to build.

---

## Q1 — "how do we handle orientation?"

**Answer: we don't. Orientation is not an input to any layout decision; the window's shape is.**

Two rules, both already in the code:

1. **v1 is pinned to portrait per screen and stays that way.** The eight v1 native stacks set `orientation: 'portrait'` in their shared `screenOptions` (pinned by a file-reading test). A v2 screen gets `'all'` through `screenOptionsFor` in the screen registry, tied to its rollback toggle — one flag moves both. The OS-level unlock (iOS plist lists every orientation; Android manifest `unspecified` + `resizeableActivity`) already shipped with F-APP-9.
2. **A v2 screen never asks "is this landscape".** Rotation is one of several ways a window changes shape; unfolding a Fold, iPad Split View, and a dragged iPadOS 26 window are the others. All of them reach the screen as two numbers — how wide, how tall — through `useWindowClass()`. `isLandscape` is exposed by that hook and used by zero screens, on purpose.

**Two caveats — DECIDED 2026-09-13 (user): v1 takes the platform default on both.** On a large screen it is full screen and rotates as the OS decides; no opt-out, no plist change, no v1 audit, no reordering of the redesign. Recorded for the record:

- **Android 16 ignores the per-screen pin on any display ≥ 600 dp wide** for apps targeting SDK 36 (we do). react-native-screens sets `activity.requestedOrientation`, which is exactly the API ignored. So v1 already rotates today on an unfolded Z Fold / Pixel Fold / TriFold and on Android tablets running Android 16. One manifest line (`PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`) would restore the pin until `targetSdkVersion` moves to 37. The recommendation was to add it; **not taken** — v1 rotates there as the OS decides.
- **iOS `UIRequiresFullScreen` is deprecated** and iPadOS 26 is reported to ignore it. When it goes, v1 receives arbitrary window sizes on iPad and there is no opt-out to add. **Decided:** the key stays until Apple ignores it, and the redesign order is not changed for the iPad.

---

## Q2 — "what different conditions do we check to change screen layouts?"

**Answer: four inputs, all read per render, none of them the device or the orientation.**

| #   | Input                              | Values                                                                                                                                          | What it decides                                                                                                                                                                                                                                                                                                                                             |
| --- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Width class** (`sizeClass`)      | compact < 600 · medium 600–839 · expanded ≥ 840                                                                                                 | Where chrome lives: bands across (compact); chips + summary share one row inside `Container` 640 (medium, decision 70); navigation rail on the leading edge + filters in a **side sheet** on the trailing edge (expanded). Whether the list is contained at `READABLE_WIDTH` 640. Whether a detail pane is allowed at all — **only** expanded **and** tall. |
| 2   | **Height class** (`compactHeight`) | short < 500 · tall                                                                                                                              | Short starts the ladder: header hidden while typing, filter chips collapse to one button with a count, summary card hidden, list takes the remainder. Detail stays a pushed route.                                                                                                                                                                          |
| 3   | **List budget**                    | `availableHeight = windowHeight − keyboardInset`; `listBudget = availableHeight − header − chrome`, every band measured at the live `fontScale` | While `listBudget < MIN_ROWS × rowHeight`, the next region in rank yields (card → chips → header → tabs). Search and the list never yield. Latched on state (`budget short ∧ keyboardVisible`), restored on blur — never on scroll. This is what catches "chrome grew" (text scale) when the height class alone says the window is fine.                    |
| 4   | **Content width vs text scale**    | `tilesStack(fontScale, contentWidth)`, `sortMenuWidth(...)`, `sortWrapsAt(...)`                                                                 | Whether a row's tiles stack vertically, whether the sort control drops to its own full-width row (decision 73), which word a chip shows and at what width (decision 72).                                                                                                                                                                                    |

**Explicitly never checked:** orientation, device model, hinge posture, platform. The one platform branch in the whole scheme is the keyboard-inset arithmetic (iOS subtracts `insets.bottom`, Android's value is already net of the bars — 05 §10).

**Status:** inputs 1, 2 and 4 are built and device-verified on PR #51 (`layout.js`, `useWindowClass`, decisions 70–73). Input 3 is the unbuilt part — Phases A and B in §5.

---

## Q3 — "what generalization are required in screen design?"

**Answer: one layout per screen, parameterized by cell, made of regions that know their own height and their own rank.** Concretely:

1. **One layout, not two.** A screen is designed once against the 05 §5 matrix and asks "which cell am I in?" — never "portrait or landscape?". The playbook Step 3 template gets one line: _"Which cell of 06 §4.1 does this screen do anything different in? If none, say so."_
2. **Chrome is a ranked list of hideable regions.** Every screen declares its regions and their yield rank (default: summary card 1, filter chips 2, header 3, tabs/rail 4). Search and the list are never in the list. This is what makes the ladder generic instead of per-screen.
3. **Every band and row is measurable before render.** Each component exposes its height at a given `fontScale` (`layout.js` pattern) and its stacking rule at `(fontScale, contentWidth)`. Without this the budget cannot be computed and the ladder cannot run.
4. **Hide, never shrink.** Regions leave the screen whole; the header stays 44 / 56. (M3 forbids short app bars; iOS shrinks bars itself.)
5. **Window and insets from hooks, per render.** `useWindowDimensions` / `useSafeAreaInsets` / `useWindowClass` only. No `Dimensions.get` at module scope, no hard-coded heights on chrome, `minHeight` where a floor is needed.
6. **No fixed-width text slot.** Width comes from measurement (`onLayout` reducer, decision 73), the zero-height ghost word (decision 72 amendment), or `flexGrow`. Bold Text on Android bumps weight after RN has measured, so any fixed slot clips.
7. **Horizontal becomes vertical at accessibility sizes**, never narrower and never ellipsised. `tilesStack` is the pattern; every new row component takes the same `(fontScale, contentWidth)` signature.
8. **Filters and sort are screen state, detail is a route.** State can live in a band, a bottom sheet or a side sheet without touching navigation. A route stays a route except in expanded / tall, where a pane is a later, per-screen design session (05 D3).
9. **Insets paid once; keyboard inset into list padding.** Never a `KeyboardAvoidingView` around a list. The root/list double bottom inset is fixed in the same pass (F-APP-8 stays deferred until the user raises it — this line only governs the v2 seam).
10. **Drawer width in points, capped**, not a percentage (M3 360 dp; also the drawer-flash-on-rotation trigger).
11. **Forms with 3+ inputs stay portrait.** Per-screen orientation exists precisely so that can be said. The 12 v1 form directories are the default-portrait set when they are redesigned.
12. **Tests assert decisions across shapes, never layout.** Tier 3 renders the screen at every named window preset × `fontScale` {1.0, 1.3, 2.143} and asserts which regions are shown and in which arrangement.

---

## Q4 — "to support any OS in 200 % scale and bold text what steps do we take?"

**Answer: the scale point is already covered by the harness; the remaining steps are the keyboard signal, the ladder, one house rule, and the shape harness.** Android's 200 % is `fontScale` 2.0; iOS Accessibility Large is 2.143. The 2.143 test point therefore covers both, and everything below is OS-neutral except one measured line.

### Already built (PR #51, device-verified)

- **Text sets the box** — `useTypeScale()` with a per-role ceiling; boxes derive from line height, never fixed (F-APP-7).
- **Live scale change remounts the screen subtree** (`Screen` keyed on `fontScale`), so a change in Settings does not leave stale boxes (F-APP-7 mechanism 6).
- **Reflow, not truncation:** tiles stack (`tilesStack`), header-card rows wrap, filter chips wrap, sort control drops to its own row (decision 73), chip width fixed by a ghost word (decision 72 amendment).
- **Android text tails:** theme `android:useBoundsForWidth=false` (F-APP-10 mechanism 7), so Android 15's bounds-vs-advances difference no longer clips Hindi.
- **Touch targets** stay ≥ 44 pt at every scale (decision 71).

### Steps remaining

| Step | What                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Where          | Fixes                                                                                                                              |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| S1   | `useKeyboardInset()` — `keyboardDidShow/Hide` on both platforms; iOS returns `max(0, kb − insets.bottom)`, Android returns `kb` as-is; the branch pinned by a test                                                                                                                                                                                                                                                                                                                                                                         | 05 Phase A1    | the one platform asymmetry, ~34 pt in a 390 pt window                                                                              |
| S2   | `availableHeight(height, keyboardInset)` + the budget check as pure functions beside `sizeClassOf`; exposed through `useWindowClass()`; harness gains `withKeyboard(n, fn)` and **insets as a `renderScreen` option** (today a landscape test runs on portrait insets)                                                                                                                                                                                                                                                                     | 05 A2–A5       | makes input 3 of Q2 computable and testable                                                                                        |
| S3   | **The yield ladder**, built first on Customers. When fewer than `MIN_ROWS` list rows fit, the screen hides its chrome one region at a time in a fixed order — summary card first, then the filter chips (they collapse to one button carrying a count), then the header, then the tab bar. Search and the list are never hidden. The hiding is switched on by a **state** (`room is short ∧ keyboard is open`) and switched off when the keyboard closes — it is not tied to scrolling, so nudging the list does not bring the chrome back | 05 B1          | the **zero-rows at 2.143 with the keyboard open** defect on the unmerged Customers v2, and the landscape-phone cell, with one rule |
| S4   | Keyboard inset into `listPadding`; fix the root/list double bottom inset; fix the card-vs-row `tilesStack` disagreement (card gets 316, row gets 640) **before** landscape is reachable                                                                                                                                                                                                                                                                                                                                                    | 05 B2–B3       | a latent invariant violation and 84 pt of dead space                                                                               |
| S5   | House rule, enforced in review: **no fixed-width text slot, no fixed-height chrome** (`minHeight` only)                                                                                                                                                                                                                                                                                                                                                                                                                                    | 06 §4.2 rule 3 | Bold Text on Android — RN measures the un-bolded width; iOS needs nothing, the system applies the weight                           |
| S6   | Shape harness: named `withWindow` presets `PHONE` (390 × 844), `PHONE_NARROW` (320 × 693 — the compact floor, corrected 2026-09-13), `PHONE_SIDE`, `FLIP_COVER`, `FOLD_OPEN`, `FOLD_OPEN_SIDE`, `TABLET`, `TABLET_THIRD`, `WINDOW_SHORT`, each with its own insets; every v2 Tier 3 suite runs its decisions at presets × {1.0, 1.3, 2.143}                                                                                                                                                                                                | 06 Phase E     | a screen cannot ship with a cell nobody rendered                                                                                   |
| S7   | Device pass per screen: Fold AVD cover → open → rotate → keyboard → AX-L → **Bold Text on** → fold back; 17e portrait → AX-L → keyboard → rotate; iPad full → ⅓ → ½ → dragged short → AX-L (needs the user's login)                                                                                                                                                                                                                                                                                                                        | 06 §4.5        | what tests cannot see: clipping, tails, hit areas                                                                                  |
| S8   | **Pin the constant `MIN_ROWS`** — how many list rows the ladder must make room for before it stops hiding chrome. Recommended target 3, absolute floor 2 (below about two and a half rows a list stops reading as a list). It is one number; the step exists because it should be chosen by looking at a device with the ladder running, not by arithmetic                                                                                                                                                                                 | 05 §6 open     | the ladder's threshold                                                                                                             |

**What is deliberately not a step:** an RN-level fix for Android Bold Text measurement (not ours; S5 makes it moot), a `maxFontSizeMultiplier` cap below what F-APP-7 already sets (the non-negotiable forbids caps), and any per-OS layout branch.

---

## 5. Order of work

1. ~~**Step 0 (user):** the two platform decisions in [[06-all-screen-shapes-plan]] §3.~~ ✅ **DECIDED 2026-09-13: platform default for v1 on both; nothing to build.**
2. **S1 → S2** (05 Phase A, foundation, no screen change).
3. **S3 → S4** (05 Phase B, Customers as the reference).
4. **05 Phase C** — drawer cap, side sheet, rail — for the wide cells.
5. **S6 → S7 → S8** alongside B, so the ladder is gated by the harness it needs.
6. **S5** applies from today: it is a review rule, not a build.

Every step is red → green → mutation smoke per [[01-tdd-workflow]]; no new npm packages; all repo edits by Opus builders on "start", uncommitted until the user has seen the diff ([[ask-before-commit]]).

## 6. Still open

1. ~~06 §3.1 — add the Android opt-out, or accept v1 landscape on Folds and tablets?~~ ✅ **DECIDED 2026-09-13: accept.**
2. ~~06 §3.2 — iPad `UIRequiresFullScreen`?~~ ✅ **DECIDED 2026-09-13: leave as is.**
3. ~~05 §9.2 — the 2.143 portrait-keyboard defect: its own fix or folded into S3?~~ ✅ **DECIDED 2026-09-13: folded into S3** ("yes fix defect by ladder").
4. ~~`MIN_ROWS` (S8).~~ ✅ **DECIDED 2026-09-13: starts at 3**, pinned on device with the ladder running.
5. **Customers `expanded / tall` is the panel of [[screens/01c-customers-shapes]] §2 (decision 74), not 05 §5's rail + trailing side sheet** — for this screen 05 C3 is not built and C2 is the leading panel.
