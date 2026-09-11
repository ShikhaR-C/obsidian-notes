# 06 — One plan for every screen shape

> **What this is:** the answer to the question asked on **2026-09-12** — _"we have flip phones, fold phones, tri-fold phones, Z Fold phones, iPads, all with variable font size and font weight; come up with a short and crisp plan on how to address all types of screen; what does the industry standard do currently?"_ It first restates what [[04-orientation-decisions]] and [[05-landscape-chrome-and-keyboard]] already decided, then records two platform facts those docs missed, then gives the plan.
> **Companions:** [[02-foundations#F-APP-9 — Orientation and large screens|02 §F-APP-9]] (window classes as built), [[02-foundations#F-APP-7|02 §F-APP-7]] (type scale as built), [[05-landscape-chrome-and-keyboard]] §5–7 (the matrix, the ladder, the build phases — this doc does not repeat them, it extends them).
> **Status:** PROPOSED. Nothing is built. Nothing starts before the user says "start". §3 contains two decisions that are the user's to make and that are **time-sensitive** independent of the redesign.

---

## 1. What 04 and 05 decided, in five lines

1. **v1 stays pinned to portrait forever.** 133 files read `Dimensions.get` at module scope and 518 sites do arithmetic on the result; no test would catch the breakage. Those files are deleted with their screens, never fixed. (04 Q1, settled 2026-09-10.)
2. **Nothing is designed "for landscape".** A screen reads **width class × height class** through `useWindowClass()` and lays itself out once. A phone on its side and a Fold opened sideways are both "landscape" and need opposite treatments, so orientation is not a design input. `isLandscape` is exposed and used by zero screens, on purpose. (04 Q2.)
3. **Chrome lives on the axis that has room.** Tall windows get bands across the top; wide windows get a navigation rail (destinations only) on the leading edge and a **side sheet** for filters on the trailing edge, never a rail for filters. (05 §5 matrix.)
4. **Height is a budget, not a breakpoint.** The keyboard and the text scale both shrink the list, and only one of them is a window class. Chrome yields in a fixed order — summary card, filter chips, header, tabs — until `MIN_ROWS` fit; search and the list never yield. Hide, never shrink. Latch on state, not scroll. (05 §6 ladder.)
5. **Two-pane list/detail is a tablet and foldable pattern only** (width _and_ height regular), is a navigation-model change, and is not scheduled. Filter-as-side-sheet goes first because it is screen state, not a route. (04 Q3 + amendments.)

---

## 2. What the industry does in 2026

Researched 2026-09-12. Both platforms have converged on the same two sentences: **design for the window, not the device**, and **orientation locks are being removed from large screens by the OS, not by the app.**

### Android / Material 3

- **Window size classes are the unit of design.** Width: compact < 600 / medium 600–839 / expanded 840–1199 / large 1200–1599 / extra-large ≥ 1600 dp. Height: compact < 480 / medium 480–899 / expanded ≥ 900 dp. Our `BREAKPOINTS` (600 / 840) and `COMPACT_HEIGHT` (500) sit on the first three width classes and a widened compact height. Google's canonical layouts on top of the classes are **list-detail, supporting pane, feed** — exactly the three shapes the 05 matrix reaches for.
- **Android 16 ignores orientation and resizability restrictions on any display with smallest width ≥ 600 dp** for apps targeting API 36: `screenOrientation`, `resizeableActivity`, min/max aspect ratio, and `setRequestedOrientation()` are all no-ops there. A one-line manifest property (`android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`) opts an activity out **temporarily**; Android 17 removes the opt-out for apps targeting API 37. See §3.
- **Foldables are windows with a hinge.** Jetpack WindowManager reports each hinge as a `FoldingFeature` with bounds and posture (flat / half-opened). A tri-fold reports two. Google's guidance is to treat the unfolded state as a tablet and to consult the hinge **only** when placing a two-pane split or a tabletop-mode layout; the Play large-screen quality guidelines require nothing hinge-specific beyond "state survives fold / unfold".
- **Testing standard:** the resizable emulator profile (phone → foldable → tablet → desktop at runtime) and `adb shell wm size` for arbitrary windows, plus the four postures on a real Fold.
- **Text:** Android 14 made font scaling **non-linear** (200 % setting scales body text more than headings), and Android 13's Bold Text setting is delivered as `fontWeightAdjustment`. The expectation is reflow, never truncation, with 48 dp targets kept.

### Apple

- **Size classes, two values each.** Width and height are compact or regular. Standard and Pro iPhones are compact width **even in landscape**; only Plus / Max / Air report regular. `UISplitViewController` collapses to one column automatically in compact width, which is why 04 §amendment 2 says two-pane is not a landscape-phone pattern.
- **iPadOS 26 windowing.** Every iPad app is now expected to be **resizable and to support all orientations**. `UIRequiresFullScreen` is deprecated and Apple's own wording is that it "will soon be ignored" and "support for all orientations will soon be required" (TN3192 is the migration note). A window can be any size the user drags it to, including wide-and-short, so `expanded / short` is no longer only a phone on its side.
- **Dynamic Type** runs to five accessibility sizes above the default; the standard move at `isAccessibilityCategory` is to turn horizontal rows into vertical stacks — which is what `tilesStack(fontScale, contentWidth)` already does. Bold Text is a system-level weight bump the app is expected to honour without measuring anything.

### Samsung and Motorola specifics

- **App continuity**: the running screen must survive cover → inner and back with state intact. That is a `configChanges` question, already answered (04 §mechanism).
- **Flex mode** (half-opened, tabletop): media and camera apps split at the hinge; list and form apps do nothing special. Nobody expects an order-management app to have a tabletop layout.
- **Flip cover screens** run third-party apps only when the user enables it (Samsung Labs / Good Lock; Motorola allows it by default with a warning). Industry practice is "don't crash, don't design for it".

### Cross-platform React Native practice

- `useWindowDimensions()` / `useSafeAreaInsets()` per render, never `Dimensions.get` at module scope.
- Type via a house scale hook with a per-role ceiling (`maxFontSizeMultiplier`), not raw `fontScale` multiplication.
- Layout decisions keyed to width class, tested by rendering the same screen at a fixed set of window presets. This is F-APP-7 + F-APP-9 as built.

---

## 3. Two facts 04 and 05 missed — and they are time-sensitive

Both were checked against the repo on 2026-09-12.

### 3.1 The v1 portrait pin is already dead on Android large screens

- `android/build.gradle`: `targetSdkVersion = 36`. Manifest: `screenOrientation="unspecified"`, `resizeableActivity="true"`, **no** `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY`.
- react-native-screens 4.24.0 applies a screen's `orientation` by setting `activity.requestedOrientation` (`ScreenWindowTraits.kt:79`) — the exact API Android 16 ignores on displays ≥ 600 dp wide.
- Therefore on any **Android 16 device with a ≥ 600 dp display** — every Galaxy Z Fold unfolded, the Pixel Fold unfolded, the Z TriFold unfolded, every Android tablet — **v1 rotates today.** The 518-site arithmetic in 04 Q1 is reachable in production on those devices, and the "which way it breaks depends on launch orientation" race is live. On Android 15 and below the pin still holds.

**Decision needed (user):** add the one-line opt-out to the activity now, or accept v1 in landscape on those devices. Recommendation: **add it.** It costs one manifest line, restores 04's "v1 stays pinned" on Android 16, and buys exactly one cycle — the opt-out disappears when `targetSdkVersion` moves to 37, so the redesign has a real deadline rather than an aspirational one. v2 routes are unaffected either way: they declare `'all'` and are built for it.

### 3.2 iOS still opts out of iPad multitasking, and that opt-out is going away

- `ios/dzzlo_oms_app/Info.plist`: `UIRequiresFullScreen = true`, with all four orientations listed under `~ipad`.
- On iPadOS ≤ 18 this key is what kept v1 out of Split View / Slide Over / Stage Manager windows — the same protection as the Android pin, for width instead of orientation. On iPadOS 26 it is deprecated and reported by developers as ignored in the betas; whether the shipped release honours it for existing apps must be **checked on the iPad simulator**, which needs the user's login (see [[app-screen-redesign-plan]] note).
- If it is ignored, v1 receives arbitrary window sizes on iPad and its module-scope constants are wrong from the first resize.

**Decision needed (user):** whether the iPad matters commercially before v1 is gone. If yes, the honest options are the same as Android's: none. There is no opt-out to add. The mitigation is to schedule the screens dealers actually open on an iPad earlier in the redesign order. If no, record it and move on.

---

## 4. The plan

Every device in the question is one of **nine window shapes**, and the shape — not the device — picks the layout. The plan is therefore: keep the 05 matrix, add the rows it lacks, add a third axis for text, and make the test harness enumerate the shapes so a screen cannot ship without being rendered in each.

### 4.1 Device → window cell (dp, approximate; verify on device before fixing any number)

| Device / state                              | Window ≈ (w × h)    | Width class          | Height     | Treatment (05 §5)                                        |
| ------------------------------------------- | ------------------- | -------------------- | ---------- | -------------------------------------------------------- |
| Phone upright · Flip open · Fold cover      | 390–412 × 780–950   | compact              | tall       | **today** — bands, full-width list                       |
| Phone on its side                           | 780–950 × 360–412   | medium / expanded    | **short**  | yield ladder; no rail, no card; search + list            |
| Flip cover screen (Z Flip 7, Razr)          | 350–450 × 350–490   | compact              | **short**  | ladder; best-effort only, never a design target          |
| Fold open, upright                          | 690–830 × 750–840   | medium / expanded    | tall       | `Container` 640; filters + card share a row (decision 70) |
| Fold open, on its side · Tri-fold open      | 750–1100 × 690–830  | expanded             | tall       | rail + contained list + side sheet; detail pane later    |
| iPad full screen (either way)               | 744–1366 × 744–1366 | medium / expanded    | tall       | same as Fold open                                        |
| iPad Split View ⅓ · Slide Over              | 320–375 × full      | compact              | tall       | **today's phone layout**, unchanged                      |
| iPad Split View ½                           | 500–680 × full      | compact / medium     | tall       | boundary case; `Container` handles it                    |
| iPadOS 26 free window, dragged short        | anything × < 500    | any                  | **short**  | ladder — same code path as the phone on its side         |

Three things the table makes visible:

- **Every fold state is tall.** Unfolding only ever adds width. The fold and the tri-fold are the payoff, not the problem (05 §5 said this; the table shows the tri-fold lands in the same cell).
- **The short row now has three entrants** (phone on its side, Flip cover, a dragged iPad window) and one mechanism — the ladder. Nothing device-specific is needed.
- **No new width class is needed.** M3's `large` / `extra-large` exist for a third pane and desktop-density layouts. Until a screen wants a third pane, a 13-inch iPad in landscape is `expanded` with a contained 640 pt column and a side sheet, and that is correct.

### 4.2 The third axis: text scale and weight

Text is not a window class, but it is the second pressure on every cell (05 §6: chrome above the Customers list goes 175 → 406 pt between `fontScale` 1.0 and 2.143). Rules:

1. **Scale is a budget input, not a breakpoint.** `listBudget = availableHeight − header − chrome`, with every band measured at the live `fontScale` from `layout.js`. The ladder runs whenever the budget is short, whichever axis shortened it. One rule covers a landscape phone at 1.0 and an upright phone at 2.143 with the keyboard open (05 §6).
2. **Horizontal becomes vertical at accessibility sizes**, never narrower or truncated. `tilesStack` and `sortMenuWidth` are the pattern; every new row component gets the same `(fontScale, contentWidth)` signature.
3. **Weight is a width pressure, not a height one.** Bold Text on iOS is applied by the system and costs nothing. On Android the same setting arrives as `fontWeightAdjustment`, and RN measures the un-bolded width, so fixed-width text slots clip (device finding 2026-09-08, [[android-emulator-driving]]). House rule: **no fixed-width text slot** — width comes from a measured or ghost-word technique (decision 72 amendment), or from `flexGrow`. This is a rule to keep, not a fix to make.
4. **The type-scale ceiling stays per role** (F-APP-7): headings cap lower than body, so a 2.143 window is dominated by content, not chrome. This mirrors Android 14's non-linear curve without depending on it.

### 4.3 What the hinge gets: nothing, until two-pane

- No posture library now. React Native core exposes no `FoldingFeature`; adding a native bridge for it is a mechanism a screen would have to earn.
- When the two-pane detail (05 D3) is designed, the split falls on the hinge if there is one and at the `Container` edge if there is not. Tri-fold (two hinges) uses the hinge nearest the readable-width column. That is the only hinge-aware line in the app's future, and it is deferred with D3.
- Flex / tabletop mode: explicitly **not a target**. A list or a form has no tabletop job.

### 4.4 The build order

The 05 §7 phases stand unchanged. This doc adds a Step 0 in front and a Phase E behind.

**Step 0 — platform decisions, before any build (user's call, §3).** (a) Android compat opt-out: add or accept. (b) iPad: confirm `UIRequiresFullScreen` behaviour on the iPadOS 26 simulator; decide whether iPad moves screens up the redesign order. Neither touches v2 code. Both are cheaper today than after the next release.

**Phase A → C — exactly as in 05 §7.** The keyboard signal, the ladder on Customers, the drawer cap, the side sheet, the rail.

**Phase E — the shape harness.** Extend `withWindow` in `src/test/` with named presets that _are_ the table in §4.1: `PHONE`, `PHONE_SIDE`, `FLIP_COVER`, `FOLD_OPEN`, `FOLD_OPEN_SIDE`, `TABLET`, `TABLET_THIRD`, `WINDOW_SHORT`. Each preset carries its own insets (05 A5 — until then a landscape test runs on portrait insets and is not truthful). A v2 screen's Tier 3 suite asserts its **decisions** (which regions are shown, which arrangement) across presets × `fontScale` {1.0, 1.3, 2.143}. Layout is never asserted, per `AI.md`. Rendering at each preset is the gate, not a nicety: it is the only thing that stops a screen shipping with a cell nobody looked at.

**Phase D — per-screen judgement, as in 05,** with one added line in the [[03-per-screen-playbook]] Step 3 template: _"Which cell of §4.1 does this screen do anything different in? If none, say so."_

### 4.5 The device checklist, per redesigned screen

Automated tests cover decisions. These cover the things tests cannot see. One pass per screen, at sign-off, using the two rigs already set up ([[ios-simulator-driving]], [[android-emulator-driving]]):

| Rig                              | Sequence                                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------------------------ |
| Pixel 10 Pro Fold AVD            | cover → open → rotate → open keyboard → AX-L (2.143) → Bold Text on → fold back with sheet open |
| iPhone 17e simulator             | portrait → AX-L → keyboard → rotate                                                              |
| iPad simulator (needs user login) | full → Split View ⅓ → Split View ½ → Stage Manager window dragged short → AX-L                   |
| Real Z Fold / Z Flip (when available) | the AVD sequence, plus Flip cover screen if the tester has it enabled                        |

Two items are not on any rig and are named so they are not forgotten: **Motorola Razr cover** (any app runs there by default) and **Android 16 large-screen behaviour on a real Fold**, which the AVD reproduces only if its image is Android 16 or later.

---

## 5. What this plan deliberately does not do

- Does not add a fourth or fifth width class. A third pane earns `large`; nothing does yet.
- Does not add a hinge / posture library. Deferred with two-pane (05 D3).
- Does not treat the Flip cover screen as a design target. It must not crash; it is otherwise the ladder's smallest case.
- Does not touch v1 beyond the two manifest-level decisions in §3. v1 is never audited for shape (settled 2026-09-10).
- Does not retire `CustomHeader` or adopt the native search bar (05 §3, still off the table).

## 6. Open questions

1. **§3.1 — Android compat opt-out:** add now, or accept v1 landscape on Folds and tablets until each screen is replaced?
2. **§3.2 — iPad:** does the shipped iPadOS 26 honour `UIRequiresFullScreen` for this app? Needs the iPad simulator with the user's login. And does the iPad matter commercially before v1 is gone?
3. **`MIN_ROWS`** (05 §6): 3 with a floor of 2, pending a device look — unchanged.
4. **05 §9.2** — the portrait 2.143 keyboard failure on the unmerged Customers v2: own fix or folded into Phase B? Still unanswered from 2026-09-10.

## Sources (checked 2026-09-12)

- Android 16 behaviour changes — orientation and resizability ignored on ≥ 600 dp: https://developer.android.com/about/versions/16/behavior-changes-16
- Android Developers Blog, "The future is adaptive": https://android-developers.googleblog.com/2025/01/orientation-and-resizability-changes-in-android-16.html
- Android 17 — the opt-out is removed: https://developer.android.com/about/versions/17/changes/ff-restrictions-ignored
- Adaptive apps — orientation, aspect ratio, resizability: https://developer.android.com/develop/adaptive-apps/guides/app-orientation-aspect-ratio-resizability
- Flutter's note on the same Android 17 change (useful cross-check): https://docs.flutter.dev/release/breaking-changes/android-large-screens-restrictions-ignored
- Apple Developer Forums, `UIRequiresFullScreen` deprecation (with the "will soon be ignored" wording): https://developer.apple.com/forums/thread/793406 · https://developer.apple.com/forums/thread/792735 · https://developer.apple.com/forums/thread/802069
- Repo evidence: `dzzlo_oms_app/android/build.gradle:6`, `android/app/src/main/AndroidManifest.xml:18-19`, `ios/dzzlo_oms_app/Info.plist:78-92`, `node_modules/react-native-screens/android/src/main/java/com/swmansion/rnscreens/ScreenWindowTraits.kt:79`, `src/theme/layout.js:40,51,54`.
