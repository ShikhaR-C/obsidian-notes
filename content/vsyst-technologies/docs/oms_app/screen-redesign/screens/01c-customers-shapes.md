# 01c — Customers across every window shape

> **What this is:** the per-screen answer for Customers to [[../06-all-screen-shapes-plan|06]] §4.4 Phase D — _"which cell of 06 §4.1 does this screen do anything different in?"_ — and the build plan that follows from [[../07-shape-questions-and-steps|07]] §4 for this screen. Written 2026-09-13 from three inputs given that day: the user's question _"according to 07 can we update `src/screens/v2/Dealer/Customers/index.js`"_, one reference image _"for big screen"_ (clarified: _"just check that the image shared will be the design for large height and width screen like ipad"_, and _"do not check the screen size of images shared"_ — so nothing in this page is a number read off the image), and _"landscape means larger width smaller height can be done according to plan"_.
> **Companions:** [[01-customers]] (the screen's spec, decisions 1–73), [[../05-landscape-chrome-and-keyboard|05]] §5–7 (matrix, ladder, phases), [[../07-shape-questions-and-steps|07]] §4 (steps S1–S8).
> **Status:** DECIDED and **STARTED 2026-09-13** ("check the answers and then start"). The eight calls in §5 are answered; decisions 74–76 are recorded in [[01-customers]] §2b. Build in progress: ~~wave 1 (S1 + S2 theme, S6 harness)~~ **DONE 2026-09-13 — 69 suites / 1443 tests green, uncommitted** → ~~wave 2 (S3 + S4 on Customers)~~ **DONE 2026-09-13 — 70 suites / 1489 tests green; the ladder reproduces 05 §1 exactly** → ~~wave 3 (P1 panel + shapes suite)~~ **DONE 2026-09-13 — 70 suites / 1521 tests green** → ~~S7 device pass~~ **RUN 2026-09-13** on the iPhone 17 Pro Max simulator (simtap) and the Pixel 10 Pro Fold AVD folded + unfolded, upright + on its side, 1× and 2.0 / 2.143, HALF_OPENED: the panel, the ladder, the sheet and the reset all behave as decided; **one defect found and fixed test-first — the top inset was paid twice whenever the header is hidden (rank 3 and the panel), the root already pays it**; the keyboard latch could not be observed on the AVD (Gboard floats with the hardware keyboard — check on a real Android phone); `MIN_ROWS` 3 and `PANEL_WIDTH` 360 judged and kept; iPad and 17e items still open. iPads checked the same evening (mini: decision 70 upright, panel on its side; Pro 13-inch: panel both ways, 376 pt of page background right of the 640 pane on its side — the Q2 cap, kept). Full log: `docs/screens/customers-v2.md` → Device runs, 2026-09-13. **Third wave DONE 2026-09-13 — 71 suites / 1558 tests green, seen on all four rigs:** 05 C1 drawer cap (both roles; 360 pt on the iPads and the Fold both ways, phones unchanged) and decision 78 (the legend card heads the list in `medium / tall`; shared row retired — seen on the iPad mini upright); decision 77 (Filters button in the search row on short windows) **BUILT 2026-09-14 — 71 suites / 1580 tests green; short-cell chrome 69 pt at 1× (was 105) and 92 at 2.143 (was 147); SEEN on the iPhone 17e on its side at 1×, AX-L and AX-L + keyboard (2026-09-14); Android cover-on-its-side look waits for the real phone.** **Decision 79 STARTED 2026-09-14** — the panel takes any short window with ≥ 620 usable width (a 300 pt panel there; 360 stays for tall windows): a phone on its side, an SE on its side, a Fold's cover on its side; the ladder keeps portrait + keyboard and short windows narrower than that; `PANE_MIN_WIDTH` 320 is the user's floor; the pane's rows are the phone arrangement — the name on its own line, the two tiles on the next row ("keep daily total and a/c balance tile in next row, and name above it") — because `inlineFits` (a six-em name floor) says the inline row has no room there; built and SEEN on the 17e on its side the same evening (1×: three rows, names whole, chips on one row; AX-L: the panel scrolls; keyboard: nothing hides). **Decision 80 BUILT 2026-09-14** — the pane's row is the phone's row in EVERY pane, wide ones included ("the name of customer in list can use whole row. make buttons of daily total and a/c balance align from bottom to let space for customer name. it is already like that right?" — it was true only on the narrow panes, so: "start"): the one-line inline arrangement of decision 74 is retired and `inlineFits` / `NAME_MIN_EM` go with it, `CustomerRow`'s `inline` prop becomes `pane` (it now only names the width `tilesStack` is asked of), the name takes the whole text column (≈526 pt in a 640 pt pane at 1×, where it had ≈133) and the two tiles sit under it, ending level with the tag line because `columnsAlign` gives the slack to the name — no cost in height at any text size; the side safe-area insets are KEPT in landscape ("should we use safearea in left and right when landscape mode? or should we leave it due to notch?"), since `AppNavigatorContainer` already pays all four and decision 79's arithmetic is built on the usable width; the iPad / 17 Pro Max look on its side is still to do. Everything uncommitted, awaiting the user's review of the diff. All edits uncommitted until the user has seen the diff.

---

## 1. Which cells Customers does something different in

| Cell (06 §4.1)                                            | What Customers does                                                                                                     | State                                   |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `compact / tall` — phone upright, Flip open, Split View ⅓ | today's screen: bands across, legend card, full-width list                                                              | BUILT, signed off                       |
| `medium / tall` — Fold open upright, iPad upright, Split View ½ | decision 70: `Container` 640, chips + card share one row                                                          | BUILT, device-verified                  |
| **any width / `short`** — phone on its side, Flip cover, dragged iPad window | **the panel where it fits** (decision 79: usable width ≥ 620, a 300 pt panel) — otherwise **the yield ladder** (07 S3, decision 75) with decision 77's Filters button in the search row | ladder built 2026-09-13; panel-in-short started 2026-09-14 |
| **`expanded / tall`** — iPad on its side, Fold open on its side, tri-fold | **the panel layout** — the reference image (§2)                                                              | to build — _"the design for large height and width"_ |

The ladder is not a cell of its own: it also runs in `compact / tall` at large text with the keyboard open (05 §1 case (b): zero rows at 2.143). One rule, two directions — 07 S3.

## 2. `expanded / tall` — the panel, as drawn (decision 74)

Read from the image, described in words only.

**Two columns.** A **panel on the leading edge** of fixed width in points (06 §4.2 rule 10: points, capped — never a percentage), and the **list pane** taking what is left. The page background is the panel's ground; the list sits on its own sheet with a rounded top corner where it meets the panel.

**The panel, top to bottom** — everything that is not the list, in the order the phone shows it:

1. **A header row inside the panel**: the drawer's hamburger at the left, the route title, and the reset at the right (shown only while something is applied — decision 21's rule unchanged). In this cell the navigator's full-width header is **not** drawn; the screen draws this row itself. 05 §4 already noted the header is ours (`CustomHeader`), so `headerShown: false` by window class is in our control.
2. **The search pill and the round sort button**, exactly the phone's control strip.
3. **The two filter chips on one row**, as on the phone (wrapping at large text), then the sort row under them — decision 73's full-width sort control (name at the left, direction arrow at the right). (Amended 2026-09-14 from "each a full-width row": "keep verified and has trans. filter chips in same row in panel".)
4. **The summary, stacked**: caption left, value right, three rows — count, today's total, total balance — with the balance the largest figure. This is `SummaryStrip`'s existing stacked layout, always used in the panel: the legend layout names the columns of the table under it, and here the table is beside it, not under it (decision 70 already retired the legend above `compact`).

**The list pane.** One row is one line: the avatar column with its ring and tag (as today), then the name with its caption line under it (the updated-at wording; the UNVERIFIED badge sits inline on that caption line), then the **two money pills side by side at the trailing side of the row**, then the chevron at the pane's edge. Green for today, blue for the balance — the colours carry, as decision 70 says they must. This is a third arrangement for `CustomerRow` — _inline_ — beside the two it has (tiles under the name; tiles stacked). Which arrangement the row takes is a decision the Tier 3 suite asserts per preset; the row still asks `tilesStack(fontScale, paneWidth)` inside the pane, so at accessibility sizes the pills stack under the name as they do on the phone.

> **RETIRED by [[01-customers]] decision 80 (2026-09-14).** The inline arrangement above is gone — it was the wide pane's row only, and `inlineFits` / `NAME_MIN_EM` (decision 79) went with it. In EVERY pane, wide or narrow, one row is now the PHONE'S row: the name slot across the whole text column with the status chip and the chevron on its line, the two money tiles UNDER it side by side at their `TILE_FLEX` weights (stacked where `tilesStack(fontScale, paneWidth)` says so), the tiles ending level with the tag line under the avatar because `columnsAlign` hands the slack to the name. `CustomerRow`'s prop `inline` is now `pane`, and its only job is naming the width `tilesStack` is asked of — `paneWidth(…)` in the pane, `contentWidth` elsewhere. The paragraph above is kept as the history of what the image was read as.

**Mockup wording, not decisions.** The image spells the chips "Verified only" / "Has transactions", the sort row "Sorted by … Date", and the summary "COUNT / RECEIVED TODAY / BALANCE DUE". The built words are decision 72's state words (Verified / Unverified · Has Trans. / No Trans.), the sort name from `strings.filters.sort`, and `strings.summary` (Count / Today / Total balance), in English and Hindi. This page keeps the built words; a change to them is its own decision, if the user wants one.

### 2.1 What the panel overrides in 05 §5's `expanded / tall` column

| 05 §5 said                                            | The image says                                                        | Consequence                                                                              |
| ----------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| navigation **rail** on the leading edge               | no rail — the drawer's hamburger sits in the panel's header row       | 05 C3 (rail) is **not built** for Customers                                              |
| filters in a **side sheet on the trailing edge**      | filters, search, sort, summary and header in **one leading panel**, persistent | 05 C2 becomes "the panel", leading edge, always open in this cell                |
| summary card "top of the side sheet, or its own row"  | stacked summary at the foot of the panel                              | as 05, in the panel                                                                      |
| list contained at 640, leading pane                   | list takes the remainder (as drawn)                                   | **open — §5 Q2**                                                                         |
| detail as a second pane, later (D3)                   | not in the image; rows still push a route                             | unchanged, not scheduled                                                                 |

### 2.2 Where the panel applies

`expanded / tall` only — the 05 matrix boundary. An iPad held upright (medium) and a Fold opened upright (medium) keep decision 70, which is built and verified. See §5 Q1 before widening it.

## 3. `short` windows — the ladder, according to plan (decision 75)

Exactly 07 S3, instantiated for this screen. Regions, in yield order:

| Rank | Region on Customers        | How it yields                                                                     |
| ---- | -------------------------- | --------------------------------------------------------------------------------- |
| 1    | summary card               | hidden                                                                            |
| 2    | filter chips + sort chip   | collapse to **one button carrying the applied count** (the reset's `badgeCount`); pressing it shows the chips (a sheet, or expands them in place — builder's call, decision-tested either way) |
| 3    | the navigator header       | `navigation.setOptions({ headerShown: false })` while latched                     |
| 4    | tabs / rail                | **n/a** — Customers is in the drawer stack, not the tab stack (05 §4)             |
| —    | search, list               | never                                                                             |

**Latch:** on when `listBudget < MIN_ROWS × rowHeight(fontScale)` **and** the keyboard is open; off when the keyboard closes. Never tied to scroll. `listBudget = (windowHeight − keyboardInset) − header − chrome`, each band measured at the live `fontScale` (07 Q3 rule 3). `MIN_ROWS` starts at **3** (floor 2) and is pinned on a device with the ladder running (07 S8).

**The one product question folded in:** 05 §9.2 (zero rows at 2.143 in portrait with the keyboard open) is fixed by this rule, not separately — 07 S3 already says so; §5 Q6 asks the user to confirm.

## 4. The build, file by file

Order per 07 §5: **S1 → S2 (foundation) → S3 → S4 (Customers) → the panel (05 Phase C, reshaped by §2) → S6 alongside**. Every step red → green → mutation smoke ([[../01-tdd-workflow]]), no new packages, Opus builders on "start", uncommitted until the user has seen the diff.

### Foundation — no screen change (S1, S2, S6)

| Step | File(s)                                                                  | What                                                                                                                                                                                                                              |
| ---- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1   | `src/theme/provider/useKeyboardInset.js` + test                          | `keyboardDidShow/Hide` both platforms; iOS `max(0, kb − insets.bottom)`, Android `kb`; the branch pinned by a test. `src/hooks/useKeyboardHeight.js` (Android-only, v1) is left alone.                                              |
| S2   | `src/theme/layout.js`, `src/theme/provider/useWindowClass.js`, `src/theme/index.js`, `src/theme/__tests__/useWindowClass.test.js` | `availableHeight(height, keyboardInset)` + `budgetShort(...)` as pure functions with a Tier 1 suite; `useWindowClass()` exposes `keyboardInset` and `availableHeight` — the "exactly the documented shape" test is the gate. |
| S6   | `src/test/fontScale.js`, `src/test/testUtils.js`, `jest.setup.js`         | override record gains `keyboardInset`; `withKeyboard(n, fn)`; named presets `PHONE` 390×844, `PHONE_NARROW` 320×693, `PHONE_SIDE`, `FLIP_COVER`, `FOLD_OPEN`, `FOLD_OPEN_SIDE`, `TABLET`, `TABLET_THIRD`, `WINDOW_SHORT`, each with its own insets; `renderScreen` takes `insets` / a preset (today a landscape test runs on portrait insets). |

### Customers — the screen (S3, S4, the panel)

| Step | File(s)                                                                                          | What                                                                                                                                                                                                                                 |
| ---- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| S3   | `Customers/layout.js`, `Customers/index.js`, `components/FilterChips.js`                          | `rowHeight(fontScale)` and the chrome band heights beside `tilesStack`; `MIN_ROWS`; the ladder in `index.js` latched on state; chips' collapsed "button + count" form.                                                                  |
| S4   | `Customers/index.js`, `components/SummaryStrip.js` / `CustomerRow.js`, `AppNavigatorContainer.js` (see §5 Q5) | `listPadding` gains the keyboard inset; the root/list double bottom inset resolved; the card and the row ask `tilesStack` of the **same** width in the shared row (today the card gets the half column and the row gets 640 — 05 §1.3). |
| P1   | `Customers/index.js`, `components/CustomerRow.js`, `FilterChips.js`, `SummaryStrip.js`, `Customers/layout.js` | the `expanded / tall` panel of §2: `PANEL_WIDTH` in points; the panel header row (`headerShown: false` in this cell); chips as full-width rows; summary forced stacked; ~~the row's inline arrangement~~ (retired by decision 80 — the pane's row is the phone's row).                          |
| T    | `__tests__/CustomersShapes.test.js` (new) + component suites                                     | decisions asserted at presets × `fontScale` {1.0, 1.3, 2.143}: which regions show, which arrangement — never layout.                                                                                                                 |
| V    | vault                                                                                            | decisions 74–76 into [[01-customers]] §4; 07 §5 order ticked; device log in `docs/screens/customers-v2.md`.                                                                                                                          |

Parallelism: S1, S2, S6 are independent (three builders, worktrees). S3, S4 and P1 all edit `index.js` — one builder in sequence, or S3+S4 then P1.

## 5. Decided 2026-09-13 — the user's answers, verbatim

1. **Panel at expanded only** — "1. expanded only".
2. **List pane** — "should we cap the pane. let it be in default at 640 but would vary to take one of fold screen size if half folded device." → capped at `READABLE_WIDTH` 640, or the remainder beside the panel when that is less. The fold-half refinement (the pane takes one fold half so the split lands on the hinge) needs a hinge signal the app does not have (06 §4.3: no posture library now) — recorded as the target; `paneWidth = min(READABLE_WIDTH, width − PANEL_WIDTH)` until then.
3. **Header inside the panel** — "confirm navigator header hidden as we will also collapse it in small height screen easy for customization." → `headerShown: false` in the panel cell AND at ladder rank 3; the screen draws its own header row in the panel.
4. **Sort row as built** — "sort as built. the image had space so it placed extra text."
5. **Double bottom inset** — "keep bottom inset for now." → no change to the root or the list's `insets.bottom`; only the keyboard inset is added.
6. **05 §9.2** — "yes fix defect by ladder."
7. **`MIN_ROWS`** — "MIN_ROWS starts at 3."
8. **`PANEL_WIDTH`** — "may vary check device and act accordingly. we keep min width 320dp as per real android devices in market." → starts at 360, floor 320 (pinned by a Tier 1 test), tuned in the device pass (S7).
9. **Mockup text** — "do not take texts from image it is just for reference." → decisions 69 and 72 stand; no string changes from the image.
