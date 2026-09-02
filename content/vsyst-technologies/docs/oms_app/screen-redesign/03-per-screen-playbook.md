# 03 — The per-screen playbook

**Outcome:** one screen travels from "next" to "old screen deleted" through six gated steps. Every step names its inputs, its outputs, who does it, and the gate that opens the next step. Screens are taken **one at a time**; nothing about a screen is planned before its own Step 1 session.

> Order of work inside one screen, as agreed: **plan the screen → build its API → design the screen → build the screen test-first**, then ship and retire. The two discussion sessions (Steps 1 and 3) are where features evolve; the specs and tests absorb the evolution (see [[01-tdd-workflow#1.4 How discussion sessions feed the tests|01 §1.4]]).

---

## Step 0 — Pick the next screen

Happens in the closing minutes of the previous screen's Step 5, or in a stand-alone 15-minute call. No backlog is pre-ranked; the user chooses, using this table as the tie-breaker.

| Criterion | Ask | Where the evidence lives |
| --- | --- | --- |
| User pain | Which screen do dealers/customers complain about or avoid? | support, the user's own judgement |
| Request fan-out | How many endpoints does the current screen fire on open, and are they serial? | app survey in [[00-overview#Current state|00 §Current state]]; grep `use…Query\|use…Mutation` in the screen folder |
| Duplication retired | Does replacing it also retire a `Common/` read-only twin or a cloned detail sheet? | the triplicated Orders/Invoices/Payments lists; the four `_Invoice_` clones |
| Shared components unlocked | Will this screen produce v2 components the next three screens reuse (list row, filter sheet, money cell, status chip)? | spec §6 component list of the previous screens |
| Money risk | Does it write to the ledger? | if yes: the API command needs the closed-period and idempotency tests; prefer doing one non-money screen first |
| Size | S (one read model, ≤ 2 actions) · M (one read model + commands) · L (several sheets/tabs) | L screens are split into sub-specs, each its own loop |

**Output:** the screen's name and size, the two session dates, and an empty `screens/NN-<slug>.md` copied from [[templates/screen-spec|the template]].

---

## Step 1 — Plan the screen (discussion session 1: *what*)

| | |
| --- | --- |
| **Inputs** | Figma image(s) for the screen in `designs/<slug>/`; the current screen(s) on a device; the list of endpoints the current screen uses; the template |
| **Owner** | the user decides; Fable facilitates and writes the spec live |
| **Timebox** | 60–90 min; an L screen gets one session per sub-spec |

**Agenda**

1. Purpose, roles, entry/exit points (§1) — 5 min.
2. Elements table (§2): walk the Figma frame top to bottom; for each element name the source field and whether it is derived. Anything derived becomes a named helper and a test — 25 min.
3. Actions and preconditions (§3): for each button/gesture name the rule that guards it and whether v3 already enforces it — 15 min.
4. States: loading, empty, error, offline, role variants — 5 min.
5. API shape (§5) sketched from §2/§3 in the session, including which ids the body takes (each one is a tenancy test) — 15 min.
6. Test list named (§5.3 and §6): read each line aloud; if a line cannot be named, the decision is not made yet → `it.todo` — 10 min.
7. Size, and what the screen must **not** do (scope guardrails) — 5 min.

**Outputs:** every ⛔ section filled; status "Spec agreed (date)"; open items as `it.todo` lines.
**Gate:** the user says "spec agreed". Until then nothing changes in either repo.

---

## Step 2 — Build the API (test-first)

| | |
| --- | --- |
| **Inputs** | spec §5 verbatim; the v4 foundations ([[02-foundations]]) already merged; the API ritual in [[01-tdd-workflow#1.3 The loop, per step|01 §1.3]] |
| **Owner** | Opus execution subagent under a written brief; Fable reviews the red commit before the green commit is written; the user starts it with "start API for <slug>" |
| **Approvals** | anything outside `api_v4/` and `test/api_v4/` (a v3 service change, a model field, a package) is listed in the brief and approved before the agent runs |

**Outputs:** one PR in `dzzlo_oms_api` with the red commit(s) first, fixtures under `fixtures/api_v4/` committed, flow-map row in `docs/testing.md`, mutation-smoke note in the PR body, CI green, deployed to staging.
**Gate:** PR merged **and** staging deployed **and** `yarn test:full` green in CI. The app work does not start against an unmerged API.

---

## Step 3 — Design the screen (discussion session 2: *how it looks*)

| | |
| --- | --- |
| **Inputs** | the Figma image(s); the **real** v4 fixture for this screen (so the design is reviewed against real field lengths, empty arrays, long names); the design tokens in `src/theme/`; the design checklist below |
| **Owner** | the user decides; Fable facilitates; the Figma MCP can pull frames or push refinements if a live file exists |
| **Timebox** | 45–60 min |

**Agenda**

1. Each §2 element against the frame: token for its type style and colour role; truncation/wrap rule; what it shows for the fixture's empty and long values.
2. Component inventory: which `src/components/v2/*` already exist, which this screen creates, which it must **not** create (use Paper's).
3. State frames: loading skeleton, empty, error, offline; role variants.
4. Checklist: 44 pt targets, 4.5:1 contrast in both themes, font-scale 200 % without clipping (`minHeight`, `flexShrink`, `numberOfLines`), one primary action per screen, reduced-motion respected.
5. Copy: final strings for every state and error code (the app has no i18n layer; strings live in one `strings.js` per v2 screen so they are testable and later translatable).

**Outputs:** spec §4 filled with dated decisions; §6 component list final; status "Design agreed (date)".
**Gate:** the user says "design agreed".

---

## Step 4 — Build the screen (test-first)

| | |
| --- | --- |
| **Inputs** | spec §2, §3, §4, §6; pulled fixture; the app ritual in [[01-tdd-workflow#1.3 The loop, per step|01 §1.3]]; the app foundations merged |
| **Owner** | Opus execution subagent under a brief; Fable reviews the Tier 3 red commit before the component is written; the user starts it with "start screen <slug>" |

**Outputs:** one PR in `dzzlo_oms_app`: Tier 1 → Tier 2 → Tier 3 (red commits first), the v2 screen folder, the navigator pointed at it (with the kill-switch if adopted), screenshots (light, dark, 200 % font) in the PR, `yarn test` green, CI green.
**Gate:** PR merged; `bash dzzlo_oms_api/scripts/release_gate.sh` green from the workspace root.

---

## Step 5 — Ship

1. Release gate green (fixtures fresh for both `api_v3` and `api_v4` sets).
2. Version bump + release notes row: "Screen X redesigned (v4)".
3. Staged rollout: TestFlight/internal track first; Play staged 20 % → 100 % over 48 h.
4. Watch for 7 days: Crashlytics for the v2 screen, the v4 endpoint's p95 and error rate, support tickets.
5. If the kill-switch exists: flip it once on staging to prove the fallback still renders.

**Gate:** no P1 for 7 days. The next screen's Step 1 may run during this window; its Step 4 may not.

---

## Step 6 — Retire

In the **next** release after Step 5's window closes:

1. Delete the old screen component(s) and any `Common/` twin the new screen replaced.
2. Delete app endpoints that no remaining screen imports.
3. In the API, mark the v3 routes the old screen used with a `Deprecation` header and a log line (no behaviour change).
4. Update the screens index row; close the spec's status line.
5. **Route retirement is a separate, explicit decision:** a v3 route is removed only when no app version the version gate still admits can call it. Until then v3 stays frozen and served.

---

## Cadence, parallelism, and roles

- One screen per iteration. Step 2 (API) for screen N+1 may start while screen N is in Step 4–5; two app PRs for different screens are not open at once until three screens have shipped this way.
- Sessions are the only place scope grows. A feature idea raised outside a session goes into the spec's "open items" and waits for the next session.
- Every repo-touching step waits for the user's explicit "start …" (house rule, see [[00-overview#Governance|00 §Governance]]).

| Role | Does | Does not |
| --- | --- | --- |
| **User** | decides scope, agrees specs and designs, approves anything outside the additive folders, says "start", ships | write tests after code |
| **Fable (main session)** | facilitates sessions, writes specs and briefs, reviews red commits, checks anchors and DoD, keeps the vault current | bulk implementation |
| **Opus execution subagents** | red → green → refactor inside a brief; PR bodies; mutation smoke | change scope, touch files the brief does not list |

---

## Tracking

`screens/README.md` is created with the first screen and holds one row per screen:

| Screen | Size | Spec agreed | API PR | Design agreed | App PR | Shipped in | Old screen removed | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

The spec's status line and this table are the only two places status lives; both are updated at each gate.
