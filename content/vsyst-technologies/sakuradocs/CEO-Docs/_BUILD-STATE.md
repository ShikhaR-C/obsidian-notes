# CEO-Docs build state — COMPLETE, 2026-08-26

Not part of the course. It is scaffolding: a record of how the course was built, what was
reconciled, and what a future editor still has to check. **Delete it, or add `_BUILD` to
`ignorePatterns` in `quartz.config.ts`, before this vault is published** — otherwise this page
and `_BUILD-SPEC.md` render as two extra pages on the site.

## What is on disk

|                                   | Count        | Words        |
| --------------------------------- | ------------ | ------------ |
| Lessons `00`–`21`                 | 22           | ~444,700     |
| Toolkit templates `C01`–`C30`     | 30           | ~96,900      |
| `index.md` + `toolkit/index.md`   | 2            | ~4,500       |
| `toolkit/vsyst-ceo-workbook.xlsx` | 14 tabs      | —            |
| **Total**                         | **54 files** | **~546,000** |

Verified on 2026-08-26, after the final pass:

- **5,778 wikilinks across CEO-Docs and COO-Docs — 0 unresolved, 0 ambiguous.**
- **0 unescaped `|` inside wiki-links in table cells** (the pipe must be `\|` inside a table row,
  or Quartz breaks the table).
- **0 spurious KaTeX math spans.** 54 unescaped `$` in 17 CEO files were being read as math
  delimiters — `$165,000 in 2026 ($153,000 at seed)` rendered as `165,000in2026(153,000`. Every
  `$` outside a code span is now `\$`. COO-Docs was clean only because the same bug was found and fixed there on 2026-08-19 (46 occurrences, 13 files) — it recurs in any new file, so check it every time.
- `npx quartz build` → **511 files parsed, 1,163 emitted, exit 0**, no broken-link warnings.
  The only remaining warnings are `isn't yet tracked by git` (these files are uncommitted) and
  KaTeX warnings from `docs/tasks` and `docs/learning`, which are pre-existing and unrelated.
- **484 `VERIFY LIVE` flags**, catalogued as a standing table in lesson 21.

`00-course-map-and-timeline.md` came in at **23,184 words** against a 12,000–18,000 target. Kept
at length deliberately: it carries the 13-row 90-day table, the 34-row rituals calendar and ~75
phase exit-criteria lines, which are reference material rather than reading. §12 gives the
one-day / one-week / one-month paths for anyone who will not read it end to end.

## Numeric reconciliations already done — do not re-litigate

| What drifted              | Wrong                                                                                                                                                                                       | Canon                                            | Where it was fixed                                                                                                                                                                                                                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Price per GSTIN per month | ₹2,500                                                                                                                                                                                      | **₹1,799**                                       | C11 is the source. Workbook `Market Map`, `Unit Economics`, `Runway & Scenarios` ARPA; C12, C13, C10, lessons 06 and 17 all re-derived                                                                                                                                                   |
| ESOP pool                 | 10%, 10,000-share cap table                                                                                                                                                                 | **7%, 75,269 options, 1,000,000 founder shares** | C20, lesson 10 §8.5; workbook `ESOP Pool` and `Cap Table & Dilution`                                                                                                                                                                                                                     |
| Assumption labels A1–A5   | Lessons 05 and 19 used the same labels for different assumptions, with 19 citing 05 as source                                                                                               | Lesson 05 owns A1–A3                             | Lesson 19 renumbered (A5→A1, A4→A2, A1→A3), 13 references updated, precedence rule added at 19 §8.2                                                                                                                                                                                      |
| Exit reserve              | C13 rule 11 and lesson 18 §10.6 require a ring-fenced reserve and "one dashboard line that shows it"; the workbook had neither, and lesson 17's dashboard table skipped from row 3 to row 5 | Reserve is a first-class line                    | Workbook `Runway & Scenarios` §B (operating reserve, exit reserve, total floor, month the floor is breached); column I now reads runway **net of** the exit reserve; the 3-month rung says it may not be spent; `CEO Dashboard` rows 3 and 4; lesson 17 §4 rows 3 and 4 written to match |

**The rule that produced these: the markdown owns the number, the workbook follows.** Rebuild the
xlsx with `python3 _build_ceo_workbook.py` after any change — never hand-edit it, or the script and
the file diverge and the next rebuild silently reverts you.

## Still worth checking — figures that appear in both a tab and a lesson

Not known to be wrong; not verified either.

- CAC inputs and close rate — `Unit Economics` vs C12 and lesson 06 §8
- Fixed monthly cost and burn — `Runway & Scenarios` vs C13 and lesson 08 §2
- The remaining dashboard goals and red lines — `CEO Dashboard` vs C29 and lesson 17 §4
- Comp bands — `Comp Bands` vs C20
- Board dates — `Board Calendar` vs C17 / C18
- Market universe counts — `Market Map` vs lesson 05 §6

## Findings the course rests on

- **The binding constraint is founder-weeks, not market size.** Lesson 05 §7's reverse income
  statement: **125–167 paying dealers ≈ 60 founder-weeks of onboarding.** Anything reasoning about
  growth ceilings, default-alive counts or hiring triggers must be consistent with delivery
  capacity being the ceiling, not TAM. The three unfalsified assumptions live at 05 §7, each with a
  pre-registered numeric failing result; lesson 19 §8's persist/pivot procedure uses those three.
- **At ₹1,799, early-stage CAC payback is 115 months** and matures to 18.3 against a ≤12 target;
  C13's base case runs out of cash at **month 16**, and annual prepay plus deferring the first hire
  together move that to month 19 — not past 24. This is stated in the lessons as arithmetic, not
  softened.
- **Buyback as ESOP liquidity is largely dead** post the 1 Oct 2024 deemed-dividend change
  (lesson 20 §9, C20). Phantom stock / SARs / profit share carry the weight instead.
- **ESOP double taxation** (perquisite at exercise, capital gains at sale) and the §192(1C) / 80-IAC
  deferral for eligible DPIIT startups: lesson 20 §9. C20 and lesson 10 do not contradict it.
- **Unpapered IP assignment** is the deal-breaking Indian diligence failure (lesson 20 §9); C14
  treats it as first-order.
- **vsyst.in's privacy policy is a February-2021 personal-name template** that says data is "not
  collected by me", while the company onboards a payment gateway. Flagged in the course; still true
  on the live site as of 2026-08-26.

## Mechanical checks — run all four before any publish

```bash
grep -L '^## .*Exercises' [0-9]*.md          # 00 and 21 are expected (map + reference)
grep -rn '^|.*\[\[[^]]*[^\]|[^]]*\]\]' *.md toolkit/*.md   # must be 0
grep -rn '[^\]\$' *.md toolkit/*.md          # unescaped $ becomes KaTeX math
npx quartz build                              # from the vault root
```

Basename collisions are the recurring trap: `index`, `toolkit/index`,
`00-course-map-and-timeline` and `21-reference-glossary-reading-list-and-sources` all exist in
**both** courses, so every link to one must be folder-qualified — `[[CEO-Docs/index|…]]`,
`[[COO-Docs/00-course-map-and-timeline|…]]`. Adding a file to CEO-Docs whose stem already exists in
COO-Docs silently breaks COO-Docs' links; it happened twice during this build.

## What kills long agent runs — put all three in every future prompt

1. **Do not spawn sub-agents. Work alone.** Agents that spawn their own children exhaust the
   concurrency cap at a fraction of the intended fan-out.
2. **Write the first half to disk before researching the second half.** Session limits kill agents
   mid-run; front-loaded research means the whole lesson is lost.
3. **Budget WebSearch explicitly (3–20 calls) and flag `VERIFY LIVE` rather than spend a search.**
   The session search quota, not wall-clock, is what ended three waves.

One more, for anyone resuming a killed agent: **resume points derived from `grep '^## ' | tail -1`
are a lower bound** — that returns the last _heading_, and the killed agent had often finished it.
Tell the resuming agent to read the tail of the file and finish the named section only if it is
actually cut off. Three agents correctly appended nothing because of this.
