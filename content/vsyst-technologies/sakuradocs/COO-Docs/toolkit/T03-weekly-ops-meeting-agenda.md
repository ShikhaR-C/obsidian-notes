# T03 — Weekly Ops Meeting Agenda

_Toolkit · fills the exercises in [[08-the-operating-cadence|08 — The operating cadence]] · Owner: COO (facilitator) · Cadence: weekly, same day, same time, never skipped — moved at worst · Workbook tabs: `KPI Scorecard` (read in the meeting), `Decision Log` (written in it), `Cadence Calendar` (lists it) in [the workbook](vsyst-coo-workbook.xlsx)._

## Purpose

The weekly ops meeting is **the heartbeat of the operating system** — the one place where numbers are read, priorities checked and problems actually solved. The template is the EOS "Level 10" meeting: 90 minutes, seven fixed segments, same day and time every week, named for the goal that attendees rate it 10/10 ([EOS Worldwide — Level 10 Meeting](https://www.eosworldwide.com/level-10-meeting); [EOS Meeting Pulse](https://www.eosworldwide.com/meeting-pulse)). Its two design choices are what make it work: **numbers before opinions** (the scorecard is reported, not debated — the same principle as Amazon's weekly business review, [Commoncog](https://commoncog.com/the-amazon-weekly-business-review/)), and **two-thirds of the time on solving issues** rather than reporting status.

## When to use

- From Day 8 of the seat, every week, for as long as the company exists.
- The 90-minute form when four or more people attend; the 30-minute variant below when it is three directors and no one else.
- Department versions later (support, engineering) run 30–60 minutes on the same skeleton.

## How to fill (rules)

1. **Same day, same time, start on time, end on time.** Late arrivals do not get a recap.
2. **The scorecard is filled by Monday 10:00** ([[T05-kpi-scorecard|T05]]) — no meeting without the artefact. In the meeting each number is only "on track / off track"; anything off track drops to the issues list. No discussion in the scorecard segment.
3. Rocks / quarterly priorities ([[T06-okr-planning-sheet|T06]]): on track / off track only. Off track → issues list.
4. Headlines: one line per customer or employee headline, good or bad. Anything needing discussion → issues list.
5. To-dos: done / not done, seven-day items only; aim for 90% done. Not done twice → issues list.
6. **IDS = Identify, Discuss, Solve.** Pick the top three issues by vote, take them one at a time: identify the real issue (often not the stated one), discuss once (everyone speaks once, no repetition), solve — a to-do with an owner and a date, or a decision logged in [[T09-decision-log-and-adr|T09]]. Then the next issue. Unsolved issues carry over; the list is never wiped.
7. Conclude: recap to-dos, agree cascading messages (what the team / dealers must hear), rate the meeting 1–10; anything under 8 says why.
8. **Roles.** Facilitator (COO) keeps time and the agenda; scribe (rotates) writes to-dos, decisions and the rating in the notes; anyone can add to the issues list during the week — the list lives in the vault, not in someone's head.
9. Issues are written as one line with a proposed solution where possible ("writing vs talking" — [Mochary, The Great CEO Within](https://blas.com/the-great-ceo-within/)).

## Template

```
WEEKLY OPS MEETING — 90 min (L10 form)            Day/time: ______  Facilitator: COO  Scribe: ______

 5  Segue          one personal + one business good news each; then heads down
 5  Scorecard      T05, on/off track only — off track -> issues list
 5  Rocks          quarterly priorities (T06), on/off track only
 5  Headlines      customer + employee headlines, one line each
 5  To-do review   last week's to-dos: done / not done (target 90 %)
60  IDS            top 3 issues by vote -> Identify, Discuss, Solve, one at a time
 5  Conclude       recap to-dos · cascading messages · rating 1-10
```

Notes skeleton (one note per week in the vault, e.g. `ops-meeting/2026-08-24.md`):

```
# Ops meeting — YYYY-MM-DD    present: ___  facilitator: ___  scribe: ___  rating: __/10

## Scorecard exceptions
- <metric> off track (<value> vs goal <goal>) -> issue #__

## Rocks
- <rock> — on track / off track (owner)

## Headlines
- customer: ...      - employee: ...

## To-dos from last week
- [x] ...  - [ ] ... (carried, why)

## Issues list (running; top 3 solved today marked)
1. [SOLVED] <issue> -> to-do / decision (owner, date)
2. ...

## Decisions -> T09
- <decision> · one-way/two-way · decided by · review date

## New to-dos (7 days)
- [ ] <what> — owner — due

## Cascading messages
- tell the team / dealers: ...
```

**30-minute variant for a three-person team** (three directors, no staff yet — same order, compressed):

```
 2  Segue        3  Scorecard       2  Rocks
 3  Headlines    3  To-dos         15  IDS (top 1-2 issues)      2  Conclude
```

Keep the 30-minute form until a fourth regular attendee joins; then move to 90 without changing the skeleton. If a daily touchpoint is needed, add a 5–15 minute stand-up (shipped / blocked / next) — the Scaling Up daily huddle ([Growth Institute — Rockefeller Habits](https://blog.growthinstitute.com/scale-up-blueprint/10-rockefeller-habits-checklist)) — and keep issues out of it.

## VSYST example (illustrative)

Monday 10:30–11:00 (30-minute form; scorecard filled by 10:00 from Mongo, ERPNext and the support log). Present: the three directors. Scorecard exceptions: OTP delivery rate 95% against a 98% goal → issue; rate-confirmation rate down two weeks running → issue. Rocks: "5 paying dealer tenants" on track; "10 SOPs live" off track → issue. Headlines: one dealer asked for a Hindi invoice PDF; the IOCL contact proposed a date. To-dos: 6 of 7 done. IDS: (1) OTP dips — identify: 2Factor route change, not our code; solve: Developer raises a ticket with the vendor and adds the delivery rate to the daily alert (T18 backlog), owner Developer, due Friday; (2) SOPs — identify: nobody owns writing them; solve: each director writes one SOP by next Monday using [[T08-sop-template|T08]], logged as to-dos. Cascading message: dealers hear about the OTP fix in the WhatsApp broadcast on Wednesday. Rating 8.

## Related

Lessons [[08-the-operating-cadence|08]], [[16-metrics-dashboards-and-scorecards|16]], [[19-planning-okrs-and-the-quarterly-rhythm|19]] · Templates [[T05-kpi-scorecard|T05]], [[T06-okr-planning-sheet|T06]], [[T09-decision-log-and-adr|T09]], [[T28-weekly-business-review|T28]], [[T24-all-hands-agenda|T24]], [[T04-one-on-one-template|T04]] · [[COO-Docs/toolkit/index|COO Toolkit]]
