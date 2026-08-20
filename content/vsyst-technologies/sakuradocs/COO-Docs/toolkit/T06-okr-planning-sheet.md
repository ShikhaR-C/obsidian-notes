# T06 — OKR Planning Sheet

_Toolkit · fills the exercises in [[19-planning-okrs-and-the-quarterly-rhythm|19 — Planning, OKRs and the Quarterly Rhythm]] · Owner: COO (the sheet); one owner per key result · Cadence: set at quarterly planning, confidence updated weekly, scored in week 13 · Workbook tab: `OKR Tracker` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

An **OKR** pairs a qualitative **Objective** — what you want to achieve this quarter, worth wanting, no numbers in it — with 2–4 **Key Results**: the measurable benchmarks that prove you achieved it, each with a baseline and a target ([Measure What Matters — notes](https://grahammann.net/book-notes/measure-what-matters-by-john-doerr); [OKRs and CFRs — Quantive](https://quantive.com/resources/articles/okrs-and-cfrs)). EOS calls nearly the same thing quarterly **Rocks** — the 3–7 priorities per 90 days, one owner each ([EOS — Meeting Pulse](https://www.eosworldwide.com/meeting-pulse)); this course says "rocks/OKRs" and means this sheet. The division of labour with the scorecard: **[[T05-kpi-scorecard|T05]] says whether the machine is healthy; this sheet says whether it moved** — the few deliberate changes you promised this quarter, visible and scored.

## When to use

- **From the first quarterly planning half-day** ([[19-planning-okrs-and-the-quarterly-rhythm|lesson 19]], [[T19-quarterly-plan-and-review|T19]]) — not before. Until then the weekly to-do list and the scorecard are enough; OKRs written before the cadence exists become a wish list.
- **Quarterly, company-level only** while the team is under ~8 people: 2–3 objectives, 2–4 KRs each. Personal OKRs come much later, if ever.
- Reviewed weekly (on/off track + confidence in the ops meeting), **scored once, in week 13**.

## How to fill (rules)

1. **Objective = qualitative, KRs = numbers.** "Improve onboarding" is not a key result; "activation rate 40% → 60%" is. If a KR has no baseline, measure it before committing.
2. **One owner per KR** — a name, not a team, exactly as on the scorecard.
3. **Progress computes from baseline → target:** (current − baseline) ÷ (target − baseline). Lower-is-better KRs work the same way (first-response 6 h → 2 h). The `OKR Tracker` tab does this for you.
4. **Score 0.0–1.0 at quarter end.** Around **0.7 on stretch KRs is a good quarter**; straight 1.0s mean the targets were sandbagged ([Doerr — notes](https://grahammann.net/book-notes/measure-what-matters-by-john-doerr)). At VSYST's size treat most KRs as committed (target = 1.0 expected) and allow at most one stretch KR per objective.
5. **Confidence (High / Medium / Low) updated weekly** beside on/off track. Falling confidence in week 4 is the early warning the system exists to produce; say it, don't smooth it.
6. **Not tied to pay in the early years** — the moment scores set salaries, everyone negotiates targets down ([Quantive](https://quantive.com/resources/articles/okrs-and-cfrs)); [[19-planning-okrs-and-the-quarterly-rhythm|lesson 19]] holds this rule.
7. **Every KR needs a source query,** same law as the scorecard — most KRs should simply _be_ a scorecard row with a quarter-end target.
8. Changing a KR mid-quarter is allowed once reality proves it wrong — but it is a logged decision ([[T09-decision-log-and-adr|T09]]), not a quiet edit.

## Template

One row per key result (columns identical to the `OKR Tracker` tab):

| Quarter    | Objective | Key result | Owner | Baseline | Target | Current | Progress % | Confidence   | Status             | Notes / next action |
| ---------- | --------- | ---------- | ----- | -------- | ------ | ------- | ---------- | ------------ | ------------------ | ------------------- |
| Q\_ FY\_\_ | O1 — …    | KR1 — …    |       |          |        |         |            | High/Med/Low | On track / At risk |                     |
| Q\_ FY\_\_ | O1 — …    | KR2 — …    |       |          |        |         |            |              |                    |                     |
| Q\_ FY\_\_ | O2 — …    | KR1 — …    |       |          |        |         |            |              |                    |                     |

The quarterly cycle around the sheet:

```
Week −2   COO drafts candidate objectives from: last quarter's scores, scorecard reds,
          the risk register, the CEO's 3-year picture
Week −1   The directors argue it down to 2–3 objectives x 2–4 KRs (half-day, T19 agenda)
Week 0    Commit: owners named, baselines measured, targets set; sheet frozen; T09 entry
Weekly    Ops meeting: each KR on/off track + confidence — 5 minutes, no discussion;
          off track -> issues list (T03)
Week 13   Score each KR 0.0–1.0 · retro (keep / change / drop) · feed the next draft
```

## VSYST example (illustrative)

The quarter pre-filled in the `OKR Tracker` tab — Q3 FY27 (Oct–Dec 2026), mid-quarter snapshot. Numbers are teaching examples, and note the KRs count tenants, never ₹ — subscription prices are undecided.

| Objective                                  | Key result                                                        | Owner           | Baseline → Target | Current | Confidence |
| ------------------------------------------ | ----------------------------------------------------------------- | --------------- | ----------------- | ------- | ---------- |
| O1 — Prove that dealers will pay for DZZLO | KR1 — 5 paying dealer tenants                                     | COO             | 0 → 5             | 2       | High       |
|                                            | KR2 — Activation rate 60% for new tenants                         | Support/Ops     | 40% → 60%         | 50%     | Medium     |
|                                            | KR3 — 10 pilots started via the IOCL/association channel          | Domain director | 0 → 10            | 4       | Medium     |
| O2 — Run the company on a weekly cadence   | KR1 — 13 of 13 weekly ops meetings held with an updated scorecard | COO             | 0 → 13            | 5       | High       |
|                                            | KR2 — 10 SOPs live in the vault                                   | COO             | 0 → 10            | 3       | Medium     |
|                                            | KR3 — Support first-response under 2 h median                     | Support/Ops     | 6 h → 2 h         | 4 h     | Medium     |

Reading it the way the ops meeting would: O1/KR2 and O2/KR2 are **at risk** — both drop to the issues list; nothing else gets airtime. At week 13, if KR2 lands at 55%, it scores ≈ 0.75 — a good quarter, written down as such.

## Related

Lessons [[19-planning-okrs-and-the-quarterly-rhythm|19]], [[16-metrics-dashboards-and-scorecards|16]], [[02-how-a-coo-thinks|02]] · Templates [[T19-quarterly-plan-and-review|T19]], [[T05-kpi-scorecard|T05]], [[T23-board-and-investor-update|T23]], [[T03-weekly-ops-meeting-agenda|T03]] · [[toolkit/index|COO Toolkit]]
