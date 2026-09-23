---
title: FigJam AI prompt — the GitHub workflow diagram
status: READY 2026-09-23 — paste into FigJam AI; mirrors 00-github-workflow.md
---

# FigJam AI prompt — the GitHub workflow diagram

**How to use:** open a new FigJam board, open the AI generate box (the ✨ in the toolbar), choose a diagram, and paste everything in the box below. If FigJam cuts the prompt short, paste **Part 1** first, then ask it to add **Part 2** to the same board.

**The board is already built:** [DZZLO OMS GitHub workflow](https://www.figma.com/board/kZ7WmRqqYzrmx5tN8ulqCE) (Figma team _Practice_, 2026-09-23). It has three rows for the everyday flow (groups 1–7), the hotfix path (A, B, C) and a cheat sheet with the naming formats, the PR-base table and the rules. Use this prompt only to regenerate it with FigJam AI.

Source of truth: [00-github-workflow](./00-github-workflow.md). Change that page first, then this prompt and the board.

---

```text
PART 1
Create a left-to-right swimlane flowchart titled "DZZLO OMS — GitHub workflow: issue to release".
Subtitle: "TDD in every repo: a failing test first, then the code. Repos: API, App, DIP-Web, RO-Web."
Use rounded rectangles for steps, diamonds for decisions, and yellow stickies for examples. Keep each shape to one short line and put examples on stickies. Draw seven horizontal lanes, top to bottom, each with its own pastel colour:

Lane 1 "Issue" (yellow)
Start circle "Something to do" → diamond "What kind?" → three boxes: "Bug (label: bug)", "Feature request (label: enhancement)", "Chore / docs (label: documentation for docs)" → all join into "Write the issue" → "Write priority P0–P3 and target release in the body" → diamond "Live in production?". Yes → red box "Hotfix (Priority P0/P1)" (starts the hotfix path). No → go to Lane 2.
Sticky: "Title: <area>: <what is wrong or what the user can do> e.g. ledger: opening balance restates from 0"

Lane 2 "Branch" (green)
Diamond "Where does it go?" → "Normal work → slave" / "Planned release → release/v1_79" / "Big epic → epic/<name>" / "Hotfix → master (what is live)" → box "Create the branch from there".
Sticky: "<type>/<issue#>-<short-name> e.g. fix/37-fy-opening-balance. Types: feature, fix, hotfix, chore, docs, test, refactor, perf"

Lane 3 "Commits: TDD" (blue)
"Write the failing test" → "Commit: test(scope): … — red" → "Write the code until it passes" → "Commit: fix/feat(scope): … — green" → "Push the branch".
Sticky: "Red before green, always. Refactor = no behaviour change, tests stay green."

PART 2
Lane 4 "Pull request" (purple)
"Open PR into the SAME branch you started from" → "Title: <type>(<scope>): <summary>" → "Body: what & why, Refs #37, tests, deploy notes, checklist" → "CI runs all tests".
Sticky: "Use Refs #37, not Closes: our PRs merge into slave, and GitHub only auto-closes on master. Never merge on a red check."

Lane 5 "Review" (orange)
"Reviewer checks: red test before code, right base, API contract, old app versions, no secrets" → diamond "Approved and CI green?". No → "Request changes" with an arrow looping back to Lane 3 "Write the failing test". Yes → go to Lane 6.
Sticky: "Comment prefixes: blocker / question / suggestion / nit"

Lane 6 "Merge" (teal)
"Merge commit (never squash)" → "Merge PR #45: <summary>" → "Delete the branch" → "Comment on the issue: ships in v1.79".

Lane 7 "Release & tag" (pink)
"Release PR release/v1_79 → slave: release: v1.6.0" → "Ask which number to bump, then bump" → diamond "Release gate PASS?". No → "Fix with a red test first" looping back to Lane 3. Yes → "Merge" → "Tag v1.6.0 + GitHub release 'v1.6.0 (2026-09-30)'" → "Fast-forward master to slave" → "Deploy" → "Close the issues" → end circle "Live".

Hotfix path: a red dashed arrow from Lane 1 "Hotfix (Priority P0/P1)" to Lane 2 "Hotfix → master", then along the same lanes: "hotfix/41-ist-dates" → red test → fix → PR → review → merge → "Tag hotfix-ist-dates (no version bump unless asked)" → "Deploy" → "Also merge back into slave".

Put a legend box at the bottom right titled "Naming":
Issue: <area>: <symptom or outcome>
Branch: <type>/<issue#>-<short-name>
Commit: <type>(<scope>): <summary> — red / — green
PR: <type>(<scope>): <summary>
Release PR: release: vX.Y.Z
Tag: vX.Y.Z (app: vX.YY) · hotfix: hotfix-<short-name>
Release title: vX.Y.Z (YYYY-MM-DD) · hotfix: hotfix(<scope>): <short-name> (YYYY-MM-DD)
```
