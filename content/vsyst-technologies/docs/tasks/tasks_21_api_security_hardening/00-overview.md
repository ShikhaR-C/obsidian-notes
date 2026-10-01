---
title: tasks_21 · 00 — legacy API hardening (overview)
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start".
---

# tasks_21 — API security hardening: the older routes

**Created:** 2026-10-01, from two sessions of the same day — the tasks_19 session: "plan the api fix as its own tasks."; and the tasks_20 session, call C‑28: "c-28 suggest fix for older api routes as tasks." One plan answers both; an earlier stub of this note was completed in place.

**Goal:** bring the older route families of `dzzlo_oms_api` — v2, v3 and the DIP v1 mount — up to the pattern v4 already follows: the API key, then sign-in, then company status, then a role check per module; the tenant taken from the sign-in, never from the request; every id a request names checked against the caller's memberships and relations; a house validator with field allow-lists; per-user rate limits. v4 is the template, not a target.

**Scope:** `dzzlo_oms_api` only. The app, `dzzlo_ro_web` and `dip-web` change only where a task says so (Waves 0 and 1 need no client release — see "Rollout").

**Ties to other plans:**

- [[vsyst-technologies/docs/tasks/tasks_20_staff_attendance/00-overview|tasks_20]] — its phase **P0b**. Staff are existing dealer users, created through the existing add-user flow, and both attendance gates trust the users' company memberships. So every older route that can create users or change memberships must be fixed **before any staff account exists** (P1).
- [[vsyst-technologies/docs/tasks/tasks_19_dip_web_superadmin_only/00-overview|tasks_19]] — its open call C‑3. The console's new "superadmin only" sign-in rule is a rule in the user interface until the sign-in-coverage, role-check, mass-assignment and tenant-isolation classes below land on the server, so tasks_19 recommends this work **before or alongside** the dip-web cut.
- [[vsyst-technologies/docs/tasks/tasks_01/02-security-hardening|tasks_01 · 02]] — the class-level list from the 2026-10-01 status review. Its IDs are reused here where a task is the same (X-SEC-1, X-SEC-2, X-SEC-4, SEC-2…SEC-5, T01-N5, T01-N6, and API-5 from tasks_01 · 04); new tasks are numbered `LEG-n`. tasks_01 · 02 may want a one-line pointer to this plan; it was not edited.

**Public / private split.** This vault is a public website, so this note names classes of weakness and fixes only. The inputs were three local-only notes — tasks_19's, tasks_01's (2026-10-01 review) and tasks_20's — and a fresh re-check of every API-side finding in the code on 2026-10-01 (read, not exercised: no request was sent to any server, no database was opened). Every finding reproduced; the pass also found more of the same classes. The specifics — each finding with its evidence, the exact routes and files of each task, who calls them in each released app build and both web apps, the red tests and the rollout per task — are in `private/_hardening-plan.md` (local only: git-ignored and never built into the site).

**Read at:** `dzzlo_oms_api` `slave` @ `86083ca` · `dzzlo_oms_app` `slave` @ `ea7e7222` (= `v1.79`) and the released tags back to `v1.69` · `dzzlo_ro_web` `main` @ `5a66bf8` · `dip-web` `slave_dev` @ `6a4276f`.

---

## 1. Classes of weakness and what "fixed" means

| Class               | Fixed means                                                                                                                                                           | Tasks                                                     |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Sign-in coverage    | Every route that is not deliberately public needs a signed-in, existing user; the API key is checked the same way on every mount                                      | LEG-3, LEG-4, X-SEC-4, X-SEC-1a…1j, proved by LEG-6       |
| Role checks         | Admin endpoints need a superadmin; each sign-in surface serves only the roles it is for; writes are checked against the caller's scope on the server                  | X-SEC-2b, LEG-9, LEG-12                                   |
| Mass assignment     | Each write accepts an allow-list of fields; role, membership and company never come from the request                                                                  | LEG-5, X-SEC-1a, X-SEC-1b, X-SEC-1f (SEC-4's legacy part) |
| Tenant isolation    | The company comes from the sign-in; every id in a request is checked against the caller's memberships and relations ("not related" and "does not exist" answer alike) | X-SEC-1c…1i                                               |
| Secret exposure     | Secret fields are hidden in the model and every list has an explicit projection                                                                                       | X-SEC-2a                                                  |
| Maintenance surface | Nothing unused stays mounted                                                                                                                                          | LEG-1, LEG-14                                             |
| Sign-in hygiene     | One-time codes, rate limits, token lifetime and revocation, request logs                                                                                              | Wave 2                                                    |

---

## 2. Waves and tasks

Size: XS < ½ day · S ≈ 1 day · M 2–4 days · L 1–2 weeks · XL > 2 weeks — one developer, tests included, review and deploy waits excluded.

Gates column:

- **P1** — must land before phase P1 of tasks_20 (no staff account before it).
- **T19** — must land before or alongside the dip-web cut in tasks_19.
- **(rec.)** after a gate — recommended before that gate, not required.

### Wave 0 — emergency containment

Small changes that close the worst exposure now. Each is safe for every released app build and both web apps, as checked against the requests they send; none needs a client release.

| ID       | Task                                                                                                                                | Size | Gates    |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------- | ---- | -------- |
| LEG-1    | Remove unused maintenance routes from the older mounts                                                                              | XS   | P1 · T19 |
| LEG-2    | A switch per guard family (log-only / enforce) and a record of what each guard would refuse — the kill switch for every later guard | S    | P1 · T19 |
| LEG-3    | Sign-in checks require an existing user record                                                                                      | XS   | P1 · T19 |
| LEG-4    | The web mount's user and company routes behind sign-in                                                                              | S    | P1 · T19 |
| LEG-5    | Role, membership and verification fields are never taken from a request body                                                        | S    | P1 · T19 |
| X-SEC-2a | Secret fields never leave the server: hidden in the model, explicit projections on every user list                                  | S    | P1 · T19 |
| X-SEC-2b | Superadmin endpoints require a superadmin sign-in — the whole admin family, on every mount                                          | M    | P1 · T19 |
| LEG-6    | Route-table test: every route in every router is guarded or on a short, named public list — a ratchet that only shrinks             | M    | P1 · T19 |
| LEG-7    | The DIP mount loadable in the test app (tasks_12's Phase 2b)                                                                        | S–M  | —        |
| LEG-8    | Look-back: a read-only check of the production request logs for past use of what this wave closes (run by the user)                 | S    | — (H‑1)  |

### Wave 1 — sign-in and tenant checks on the remaining older routes

X-SEC-1 (tasks_01) split by route family. One shared rule per family serves v2, v3 and the DIP mount together. Each guard runs log-only for about a week, then enforces.

| ID       | Task                                                                                                       | Size | Gates                      |
| -------- | ---------------------------------------------------------------------------------------------------------- | ---- | -------------------------- |
| X-SEC-4  | One API-key check, applied the same way on every mount (log-only first)                                    | S    | —                          |
| X-SEC-1a | Add-user route: the caller must manage the company; role, model and company come from the caller           | M    | P1 · T19                   |
| X-SEC-1b | Membership and profile edits: field allow-lists and company-admin checks                                   | L    | P1 · T19                   |
| X-SEC-1c | Self-only writes: company switch, sister companies, invitations, account and company deletion              | M    | P1 · T19                   |
| X-SEC-1d | Company user lists and profile reads limited to members of that company                                    | S    | P1 · T19 _(rec.)_          |
| X-SEC-1e | DIP routes: dealer role, an active membership, and the dealer taken from the sign-in                       | M    | P1 _(rec.)_ · T19 _(rec.)_ |
| X-SEC-1f | Dealer and customer company records: sign-in, tenant checks, field allow-lists, slim list projections      | M    | —                          |
| X-SEC-1g | Relations, ledgers and balances: the relation checked from the signed-in side                              | L    | —                          |
| X-SEC-1h | Orders, sales orders, invoices and vouchers: record-ownership checks                                       | L    | —                          |
| X-SEC-1i | Vehicles, drivers, requests, products, rates and PSOC reads: tenant checks                                 | M    | —                          |
| X-SEC-1j | Public and semi-public routes: a role list at registration, size and rate caps on error reports            | S    | —                          |
| LEG-9    | Server-side scope checks on older write routes (read-only scopes write nothing), mirroring the app's rules | M    | P1 _(rec., H‑4)_           |

SEC-4's legacy part (input validation) is delivered inside X-SEC-1a…1j, through v4's house validator.

### Wave 2 — sign-in hygiene

| ID               | Task                                                                                                                                                               | Size | Gates             |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- | ----------------- |
| T01-N5           | One-time codes: secure generation, attempt limits, and a limiter on every route that sends or checks one — on all three sign-in mounts                             | M    | P1 _(rec.)_       |
| SEC-2 (legacy)   | Rate limits in a store shared by both servers; a generous global limiter                                                                                           | M    | —                 |
| SEC-3            | One-time codes hashed at rest                                                                                                                                      | S    | —                 |
| LEG-10           | Test-only request switches honoured only outside production                                                                                                        | S    | —                 |
| LEG-11           | Sign-in with a one-time code for every account except a short server-side list of store-review accounts                                                            | M    | after the T19 cut |
| LEG-12           | Each sign-in surface issues tokens only to the roles it serves                                                                                                     | S    | after the T19 cut |
| T01-N6           | Tokens pinned: fixed algorithm, audience and issuer; an audience per client family (the design in tasks_18's client-identification note)                           | M    | —                 |
| LEG-13           | Token revocation (a per-user token version) and a shorter lifetime with refresh ([[vsyst-technologies/docs/tasks/tasks_02_major/01-token-refresh\|tasks_02 · 01]]) | L    | —                 |
| API-5 (extended) | Request logs without personal data, with a retention rule                                                                                                          | M    | —                 |
| SEC-5            | CORS allow-list for the two web origins                                                                                                                            | S    | —                 |

### Wave 3 — retire older routes behind v4; remove dead ones

| ID     | Task                                                                                                                                 | Size              |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------- |
| LEG-14 | Remove routes no client calls, each after a 30-day check of the request logs                                                         | S                 |
| LEG-15 | Retire v2: raise the minimum app version once the builds that use it are gone, then unmount it                                       | M + adoption wait |
| LEG-16 | v4 user-management commands, then retire the older user routes — tasks_20's proposed v4 add-staff command is the first of them       | L                 |
| LEG-17 | One sign-in surface; the DIP routes as v4 modules; then retire the DIP v1 mount                                                      | L                 |
| LEG-18 | v3 route families move to v4 with the screen redesign; v3 unmounted when the minimum app version passes the last build that calls it | XL, ongoing       |

**Related, tracked elsewhere (not re-planned here):** X-SEC-3 and T01-N4 (SMS-provider calls) and X-OPS-1 (proxy hop count, needed for IP-keyed limits) in tasks_01 · 02 and · 07.

---

## 3. Order and dependencies

1. **Now, independent of every other plan:** LEG-1 first, as its own one-line hotfix; LEG-8's look-back this week (H‑1). Then LEG-2 and LEG-3 (the foundations every guard uses), LEG-5, X-SEC-2a, X-SEC-2b and LEG-4. LEG-6 lands with the first Wave 0 change; LEG-7 before any test of the DIP mount.
2. **Before tasks_19's cut** (its C‑3 — before or alongside): all of Wave 0, then X-SEC-1a, 1b and 1c. With them, role and membership can no longer be written from outside the console, and admin endpoints answer only a superadmin. X-SEC-1d and 1e are recommended too, because dzzlo_ro_web becomes the dealers' DIP surface. LEG-11 and LEG-12 change sign-in, so they follow the cut.
3. **Before tasks_20 P1** (no staff account before this): all of Wave 0, then X-SEC-1a, 1b, 1c and 1d — every route that can create a user or write a membership, and every company user list. Recommended as well: LEG-9 (H‑4), X-SEC-1e (H‑13) and T01-N5.
4. **The rest of Wave 1** family by family. Each guard goes log-only (LEG-2), and enforces once the log shows that only illegitimate requests would be refused.
5. **Wave 2** after Wave 1's gating subset. T01-N5 and SEC-2 need X-OPS-1 for IP-keyed limits (per-account limits do not). LEG-13 ships with the app release that adds token refresh.
6. **Wave 3** waits on adoption (H‑7) and follows the screen redesign. LEG-15 ends the one exception kept for the oldest supported builds.
7. **API PR #34** (the database-driven version gate) adds an endpoint to the admin family, so it merges after X-SEC-2b.

---

## 4. Testing approach

House style, as in the [[vsyst-technologies/docs/oms_api/tdd-testing-guide|API TDD guide]] and the API's `docs/testing.md` §10–§11: **red → green → mutation smoke**. The failing test comes first and is named after the symptom. Then the least code that turns it green. Then delete the line the test defends, check that the expected tests go red, and record the count in the PR.

- **Per route:** no sign-in → 401; a user of another company → 403 (the same answer as for a company that does not exist); right company, wrong role or scope → 403; right caller → 200; nothing written on any refusal. Identities come from the v4 test helper: two dealers, two customers, a superadmin, and a member with a read-only scope.
- **Compatibility:** the request bodies that each released app build and both web apps send, read from the released tags, are replayed as tests. A guard that would refuse one is either wrong or a deliberate change listed in §6.
- **The route-table test (LEG-6):** every route in every router is guarded or on a short, named public list. Routes not yet guarded sit on a committed list that the test only lets shrink; the list is empty when Wave 1 ends. A second pass sends each route a request with no sign-in and checks that nothing answers 2xx and nothing changes in the database.
- **v2:** the API's testing runbook freezes v2 with "no new tests". Its controllers also serve the DIP mount, so this work needs an exception (H‑8).
- **DIP:** tests of the DIP mount need LEG-7 first.

---

## 5. Rollout principle — old app builds keep working

- Store builds in the field keep calling the older routes. Every guard was checked against what the released builds (1.69 onward) and both web apps send: their headers, their sign-in state and their request bodies. Waves 0 and 1 need **no client release**.
- Where that evidence is only static, the guard runs **log-only** first and records what it would refuse. It enforces after a clean week. The switch goes back without a deploy.
- **One deliberate exception** is kept for the oldest supported builds, with compensating limits, until v2 is retired (LEG-15). The private plan describes it.
- Changes that users could notice are not slipped in. They are listed in §6 for the user to decide.
- Old tokens stay valid until they expire whenever token handling changes (T01-N6, LEG-13).

---

## 6. Open questions for the user

| #    | Question                                                                                                                                                                                     | Recommended                                                                                      |
| ---- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| H‑1  | Run the look-back (LEG-8) on the production request logs now? If it finds past use of what Wave 0 closes, treat that as an incident: check the data against backups, and decide whom to tell | **Yes, this week**                                                                               |
| H‑2  | Who may add users to a company: owner and admin only, or any active member (today's app shows the add button to any active member)?                                                          | **Owner and admin only**; the app hides the button for others in its next release                |
| H‑3  | Who may change another member's email or phone?                                                                                                                                              | **A company admin, only when the member belongs to no other company**; otherwise the member      |
| H‑4  | Server-side scope checks (LEG-9) before any staff account exists?                                                                                                                            | **Yes** — staff are existing dealer users with today's scopes                                    |
| H‑5  | Timing against the tasks_19 cut (its C‑3)                                                                                                                                                    | **Wave 0 + X-SEC-1a…1c before or alongside the cut**                                             |
| H‑6  | A one-time code for every sign-in, except a short server-side list of store-review accounts (LEG-11) — superadmins included?                                                                 | **Yes, in Wave 2, after the tasks_19 cut** (tasks_19 keeps superadmin sign-in unchanged for now) |
| H‑7  | When to retire v2: what share of requests still comes from the app builds that use it? (A read-only query on the request logs answers it.)                                                   | **Raise the minimum app version when the share is near zero**                                    |
| H‑8  | Approve an exception to "no new v2 tests" (recorded in the API's testing runbook)?                                                                                                           | **Yes** — the DIP mount uses the same controllers                                                |
| H‑9  | Hash one-time codes at rest (SEC-3)? Support could then no longer read a code from the database                                                                                              | **Yes, after T01-N5**, once resend and delivery reports cover support's needs                    |
| H‑10 | Where rate-limit counts live: a MongoDB-backed store (one new package to approve), Redis (new infrastructure), or per process (limits double with two servers)?                              | **MongoDB-backed**                                                                               |
| H‑11 | Should logout end the session on every device, or should only a password reset and admin actions do that?                                                                                    | **Every device** — simple and predictable                                                        |
| H‑12 | How long to keep request logs (API-5)?                                                                                                                                                       | Decide together with tasks_20's C‑8 (the same DPDP reading)                                      |
| H‑13 | DIP isolation (X-SEC-1e) before tasks_20 P1?                                                                                                                                                 | **Yes**                                                                                          |

---

## 7. Effort roll-up (rough, one developer)

| Wave                   | Tasks | Effort                                                                                                           |
| ---------------------- | ----- | ---------------------------------------------------------------------------------------------------------------- |
| 0 — containment        | 10    | about 2–3 weeks                                                                                                  |
| 1 — sign-in and tenant | 12    | about 9–11 weeks; the subset that gates tasks_19 and tasks_20 P1 is about 3 weeks (4 with the recommended tasks) |
| 2 — sign-in hygiene    | 10    | about 5–6 weeks                                                                                                  |
| 3 — retire behind v4   | 5     | months — tied to adoption of new app builds and to the screen redesign                                           |

Nothing starts before the user says **"start"**. Each task goes red → green; the user commits, pushes and merges.
