# S4 cutover — verdicts for every test rewritten or deleted (AI.md rule 4)

**The decision behind all of them** — the user, 2026-09-20 (plan 09, calls C‑1, C‑1b, C‑5, C‑8):
"current date time picker is not for range … create new date time range picker for v2 screens",
"one button but we can make it compact when showing start end date time", "introduce stepper".

One WINDOW is now chosen in one sheet and applied in one request, and a bar steps it. v1's two
date-time buttons (`DatePicker/DTBS`) are no longer mounted by this screen, so every test that drove
them is testing a control the screen does not have. The rules they pinned did not disappear: each
moved DOWN a layer, to the pure `helpers/DateRange` suites (window.test.js, window.step.test.js,
window.zone.test.js, format.test.js) or ACROSS to the component's own Tier 3 suite
(`components/v2/DateRangeSheet/__tests__/DateRangeSheet.test.js`), which is the "one layer per rule"
rule of AI.md. Nothing is less proved after this change than before it.

v1 keeps `DTBS` and v1's own screens are untouched.

## `__tests__/DailySummaryRange.test.js` — rewritten whole (11 tests → 16)

| Old test | What it pinned | Verdict |
| --- | --- | --- |
| 1 · the first request carries no range; the buttons show the IST day in 24-hour time, 00:00 → 23:59, until the server's window arrives | (a) the first body is `{ companyId, tab }`; (b) DTBS's props and 24-hour Roboto Condensed print; (c) the server's echo fills the buttons | **REWRITTEN as new 1.** (a) is unchanged and still pinned, to the letter. (b) is gone with the buttons — the bar's print is `RangeSummary.test.js` + `layout.bar.test.js`. (c) is gone by §3.6: the bar shows the WINDOW the phone holds, never the server's echo, so there is nothing to wait for |
| 2 · the range row is DTBS, v1's way — no captions, the arrow between — and the parked DateTimeRange is not mounted (its file and its suite stay) | the screen mounts DTBS; the parked `DateTimeRange.js` and its suite still exist on disk | **DELETED.** The first half asserts the control the user replaced. The second half is a guard for the removal step (S6), which deletes those two files on purpose; keeping a test that fails the moment S6 does its job would be a tripwire pointed at ourselves. `layout.test.js:344‑349` still refuses the name `DateTimeRange` in `layout.js` until then |
| 3 · a To picked at a minute is sent as that minute − 1 ms — ONE request, no cursor, even from deep in the list | (a) the minute rule; (b) one request; (c) no cursor from deep in the list | **SPLIT.** (a) is C‑1's rule and is now proved at Tier 1 (`window.test.js` — every end sends its boundary less 1 ms) and in the sheet's own suite. (b) and (c) are SCREEN facts and are kept, stronger, as new 4 (one request per Apply, exact instants) and new 9 (no request ever carries the new range with the old cursor) |
| 4 · a To whose seconds iOS kept is read as the minute its button shows | `combineIst`'s reading of a platform value | **DELETED at Tier 3.** Tier 1 `window.test.js` pins `combineIst`; the picker's own props are `DateRangeSheet.test.js`'s |
| 5 · a shift preset on the To sheet ("6 - 6 AM") is a minute, so it is sent a millisecond before it | DTBS's per-end shift button | **REPLACED by new 5.** The shift time is no longer a clock set on one end: it is the window's day start, applied to both ends at once and REMEMBERED for the next screen (C‑4). New 5 pins the request it produces and the value written to storage |
| 6 · an end-of-day To is already inclusive and is sent AS IT IS — a date button keeps 11:59 PM and moves the day | the old 11:59 PM exception (`isIstDayEnd`) | **DELETED — the behaviour is gone by decision.** C‑1, rounds 4–5: "end shows own time", no exception; Today under 12 - 12 AM now reads `→ 20 Sep, 12:00 AM`. Tier 1 pins the new rule, and `sentTo` / `isIstDayEnd` go out in S6 |
| 7 · a From change sends the From as picked, with the To the buttons show | one end changed on its own | **DELETED.** There is no "one end" any more: a window is applied whole. Custom's four fields are `DateRangeSheet.test.js`'s, the pick rules Tier 1's |
| 8 · a To picked at or before From pulls From to one minute before it | the one-minute clamp, through the screen | **DELETED at Tier 3.** `clampRange` is Tier 1 (`window.test.js`) and the fields that call it are the sheet's own suite. The screen cannot reach a broken pair: `apply` refuses a window `rangeFor` cannot read (`useDateRangeWindow.test.js`) |
| 9 · a From picked past To pushes To one minute after it | the same clamp, the other way | **DELETED**, same verdict as 8 |
| 10 · a new window is a new list: the selection goes, the chips stay in the body | selection emptied, chips kept, one request | **KEPT as new 10**, driven by a step instead of a picker, and with the request's own instants asserted |
| 11 · the picked window outlives a tab switch | the window survives a tab change | **KEPT as new 11**, unchanged in meaning |

**New tests that had no ancestor** (the behaviour did not exist before): 2 (a remembered 6 - 6 AM rides
the first request), 3 (the bar opens the sheet on what is applied; choosing sends nothing), 6 (Apply
unchanged and Close send nothing), 7 (five quick steps are ONE request, 300 ms after the last, with
the skeleton while it waits), 8 (`›` dimmed on a window holding today), 12–14 and 16 (what a refresh
does to a named choice, and what it does NOT do to the bar between refreshes), 15 (one sheet per
screen, the quick return included).

## `__tests__/DailySummaryShapes.test.js` — re-pointed, nothing removed

| Test | Change | Verdict |
| --- | --- | --- |
| helper `dateButtons` / `buttonsShareARow` | → `barIsOneRow`: the nearest common host of `range-bar-prev` and `range-bar-next` lays out a row | The user's rule of 2026-09-16 ("from and to date time picker should be in same row in landscape mode as well") now applies to the bar's own three controls. Same question, same mechanism, the new control |
| 1 (PHONE, 1×), 4 (1.353 and 2.143), 6c (tablet upright) | titles say "the range bar in one row" instead of "v1's buttons in one row"; the assertion is `barIsOneRow` | Renamed, not weakened: each still asserts the window's row survives that cell and that text size |
| 8 (PHONE_SIDE, WINDOW_SHORT, FOLD_OPEN_SIDE, TABLET) | `within(range-row).UNSAFE_getByType(DTBS)` → `within(range-row).getByTestId('range-bar')`; `range-arrow` → `range-bar-button` | The panel still stacks header · tabs · the window's row · card · controls, and the row is still one row. The arrow BETWEEN two buttons has no successor — there is one button now, and the `→` is inside its print (`RangeSummary`) |
| the "no From / To captions" assertions | kept as they are | Still true, and still worth asking: `strings.range.from` / `.to` are not rendered by the new bar either |

## Not touched, and why

`DailySummary.test.js` (test 25's refresh, test 31's `range-row`), `DailySummaryChrome.test.js` (the
block's contents and the quick return), `DailySummaryCutover.test.js` and `layout.test.js` all pass
unchanged: the bar kept the `range-row` testID of the row it replaced, and the refresh's contract for
a window that has NOT rolled over is what it always was — a plain refetch of the same args.

---

# S6 — the removal: verdicts for every test deleted (AI.md rule 4)

The cutover (S4) left v1's two date buttons, the picker that never shipped and
the adapter between them mounted nowhere and imported by nothing. This step
takes them out — **2 350 lines deleted**, 6 files — and with them the tests that
existed only to describe them. Nothing that is still TRUE lost its proof: where
a deleted block pinned a rule the app still has, the cases were MOVED, not
rewritten, and the new home is named below.

## Files deleted, and what went with them

| File (lines) | What it pinned | Verdict |
| --- | --- | --- |
| `screens/v2/Common/DailySummary/components/RangeButtons.js` (104) | the wrapper that drew v1's `DTBS` on this screen: no captions, the arrow between, 24-hour Roboto Condensed | **Gone with the control** (the user, 2026-09-20). It had no test of its own; what it drew was asserted through the screen, and those assertions were re-pointed at the bar in S4. v1's `DTBS.js` itself is untouched and still serves Reports and v1's Daily Summary |
| `…/components/DateTimeRange.js` (577) | the redesigned picker parked on 2026-09-16 and mounted by nobody since | **Gone: it was superseded before it ever shipped.** `components/v2/DateRangeSheet` is the redesign the user asked for, with its own suites |
| `…/components/__tests__/DateTimeRange.test.js` (788) | that component's pills, its one shared iOS sheet, Done / Cancel, the IST spinner, Hindi | **Deleted with the file.** Every RULE it stood on outlived it and is proved elsewhere: the pick and the clamp in `helpers/DateRange/__tests__/window.test.js` (`pickField`, `clampRange`) and `window.lift.test.js`; the platform pickers, their props, their theme and their language in `components/v2/DateRangeSheet/__tests__/pickers.test.js` and `DateRangeSheet.test.js`; the print in `RangeSummary.test.js` + `helpers/DateRange/__tests__/format.test.js` |
| `helpers/DailySummary/range.js` (240) | the IST arithmetic (already re-exported from `DateRange/window.js`) plus `sentTo`, `clampPicked`, `isIstDayEnd` | **The re-export was a bridge for import sites that no longer exist**; the three adapter functions turned "what a DTBS button SHOWS" into instants and carried the old 11:59 PM exception, which C-1 dropped by decision |
| `helpers/DailySummary/__tests__/range.test.js` (538) | see the block table below | **Split: moved or deleted, block by block** |
| `helpers/DailySummary/__tests__/range.zone.test.js` (103) | `defaultRange`, `istParts` and `combineIst` run in processes pinned to UTC / Los Angeles / Kiritimati | **MOVED into `helpers/DateRange/__tests__/window.zone.test.js`**, which already ran the same child-process harness for `presetRange`, `stepWindow`, `applyDayStart`, `pickField` and the print. The three cases are there verbatim, with the same expected instants, plus the `here` cross-check the file uses (27 tests now) |

## `range.test.js`, block by block

| Block | Verdict | Where it lives now |
| --- | --- | --- |
| `the constants` (3) | deleted as a duplicate | `window.test.js` → "the lift" asserts all five constants, `HOUR_MS` included |
| `istParts` (6) | **moved** | `window.lift.test.js` |
| `istInstant` (3) | **moved** | `window.lift.test.js` |
| `defaultRange` (7) | **moved** | `window.lift.test.js` (and the zone case in `window.zone.test.js`) |
| `combineIst` (8) | **moved** | `window.lift.test.js`; the field-level caller is `window.test.js` → `pickField` |
| `toBoundary` (3) | **moved**, less two prints | `window.lift.test.js`. The two `formatRangePill` assertions (`'15/09/26 18:30'`, `'17/09/26 00:00'`) went with that function: the v2 bar and sheet print in AM/PM through `helpers/DateRange/format.js`, whose `format.test.js` pins it. What the instants ARE is still asserted, now through `istParts` |
| `clampRange` (10) | **moved** | `window.lift.test.js` |
| `sentTo` (9) | **deleted — the behaviour is gone by decision** | C-1 / C-1b (rounds 4–5, 2026-09-20): every end prints its own time and sends one millisecond before it, with NO exception for an IST day end. `window.test.js` → `presetRange` / `requestRange` pins the rule that replaced it |
| `clampPicked` (8) | **deleted** | It was `clampRange` measured against `sentTo`'s reading. The clamp itself is `window.lift.test.js`; the sheet's fields call it through `pickField` |

47 tests moved into `window.lift.test.js`, 3 into `window.zone.test.js`; 20
(`sentTo`, `clampPicked`, the duplicated constants) are gone with the rule.

## Assertions removed from suites that stay

| Where | What it pinned | Verdict |
| --- | --- | --- |
| `helpers/DailySummary/__tests__/format.test.js` — the `formatRangePill` block (7) | `DD/MM/YY HH:mm` in IST, zero-padding, 24-hour, unreadable → `''` | **Gone with the function**, which only v1's pills and buttons printed through. The v2 print is `helpers/DateRange/format.test.js` (`formatClock`, `formatDate`, `formatRangeLine`), in AM/PM with the words handed in |
| `helpers/DailySummary/__tests__/index.test.js` — the `range` group | the barrel hands out twelve window names by identity | **Rewritten, not weakened**: the group is now `dateRange: ['defaultRange']`, still by identity, and "exports nothing it does not document" still holds the barrel to its list. The one surviving name is the SERVER's default day, which the endpoint's own MSW test asks this barrel for |
| `helpers/DateRange/__tests__/window.test.js` — "the Daily Summary barrel still hands out the same names" | the bridge: `summary.istParts`, `toBoundary`, `IST_OFFSET_MS`, `sentTo`, `clampPicked` all defined | **Inverted, deliberately**: it now asserts they are `undefined` and that `defaultRange` is the same function object. The test that guarded the lift now guards the removal |
| `screens/…/__tests__/strings.test.js` — "gives the date-time sheet its two buttons", the two `a11y.*Picker` lines, the `range.from` / `range.to` rows | v1 picker copy in both languages | **Gone with the keys.** The window's words are the common component's own table (`components/v2/DateRangeSheet/strings.js`), where `strings.test.js` beside it pins them in both languages |
| same file — the walk's vacuity floor | `EN_LEAVES.length > 35` | **Lowered to 30, and only that.** It is not a rule about the copy; it is the guard that says the walk found something to walk. Six leaves left the table, so the constant follows them. Every other assertion in that file is unchanged |
| `screens/…/__tests__/DailySummaryShapes.test.js` — `queryByText(strings.range.from/to)` in the panel (4 lines, 2 tests) | that the panel does NOT print "From" / "To" captions | **Gone with the keys they named** — an absence cannot be asserted through a string that no longer exists. What replaces it is positive and stronger: the panel's range row IS `range-bar` with its button, asserted in the same two tests, and the bar has no captions to hide |
| `screens/…/__tests__/layout.test.js` — `/rangeRowWidth|DateTimeRange/` | that `layout.js` mentions neither the old width rule nor the parked picker | **Half kept:** `rangeRowWidth` still may not come back. The `DateTimeRange` half named a file that no longer exists anywhere in the repo, which is a stronger guarantee than a regex over one file's source |

## Renamed, with no assertion changed

`DailySummaryChrome.test.js` test 1 and its header ("v1's buttons" → "the range
bar"), `DailySummaryShapes.test.js` test 15 ("both pills" → "its own words"),
and the comments in `layout.js`, `components/Panel.js`, `components/TabBar.js`,
`screens/…/index.js`, `helpers/DailySummary/index.js` and
`helpers/DailySummary/format.js`. Each names what the screen has now; not one
`expect` moved.
