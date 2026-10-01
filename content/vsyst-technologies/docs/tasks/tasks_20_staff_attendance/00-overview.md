---
title: tasks_20 · 00 — staff attendance for DZZLO dealers (overview)
status: PLAN — not started (2026-10-01, round 3). No code, no branch, no commit. Execution waits for the user's "start".
---

# tasks_20 — staff attendance: own phone, at the outlet only

**Created:** 2026-10-01, from the user: "we want to create a attendence website that can let employee use only thier device in office corrdinates only. is it possible?" Round 1 (same day, "phones, new standalone site") planned a website — kept, superseded, in [[05-round-1-web-design]]. Round 2 (same day): "GPS is better proof, it can be used by dip-web dealers, we will share dzzlo_ro_web address. address coming soon." — staff check in with a **native app inside the DZZLO OMS app**; the dealer manages attendance **inside dzzlo_ro_web**. Round 3 (same day): staff are the dealer's **existing DZZLO users**, all devices are supported, and three new pieces of planning — the package approval list, the dealer terms, and the older-route fixes as tasks. Also: "no code implementation. just add plan in vault obsidian-notes" and "use agent teams".

**Scope:** three existing repos — no new repo, no new store listing, no new user role.

- `dzzlo_oms_api` — a new v4 module `/api/v4/attendance` and seven collections ([[01-api]]).
- `dzzlo_oms_app` — an **Attendance** entry inside the normal dealer app, and three small native modules: location, device key, app integrity ([[02-app]]).
- `dzzlo_ro_web` — an Attendance section for the dealer's owner and admins ([[03-web]]).

Platform facts, the Apple / Google rules and India's DPDP law are in [[04-platform-stores-and-law]]; the packages to approve in [[06-package-approval-list]]; the dealer terms and the draft data-processing clause in [[07-dealer-terms-and-data-processing]]. The fixes for the older API routes — a prerequisite — are their own task: [[vsyst-technologies/docs/tasks/tasks_21_api_security_hardening/00-overview|tasks_21 — API security hardening]].

**Source:** a read-only agent team on 2026-10-01 — `dzzlo_oms_api` `slave` @ `86083ca`, `dzzlo_oms_app` `slave` @ `ea7e7222`, `dzzlo_ro_web` `main` @ `5a66bf8`, and the platform, store and legal sources as of 2026-10-01 (URLs in 04 and 07). Every `path:line` in these notes is at those commits. The agents wrote 01–04, 06 and 07 from one shared sheet of names and decisions; this overview is the orchestrator's.

| File                                    | What                                                                                                                |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [[00-overview]]                         | this note — the answer, the flow, what it stops, phases, calls                                                      |
| [[01-api]]                              | `dzzlo_oms_api`: routes, collections, the roster, the 8 checks, verification, tests                                 |
| [[02-app]]                              | `dzzlo_oms_app`: the Attendance entry, screens, native modules, permissions, all-device support, tests, release     |
| [[03-web]]                              | `dzzlo_ro_web`: the dealer's seven pages, the roster, permissions, the v4 API base                                  |
| [[04-platform-stores-and-law]]          | fake-location detection, integrity, hardware keys (old Android too), libraries, the store checklist, DPDP           |
| [[05-round-1-web-design]]               | round 1, the website design — superseded 2026-10-01, kept as the record                                             |
| [[06-package-approval-list]]            | every new package, per repo, with an **Approved?** column for the user (C‑24)                                       |
| [[07-dealer-terms-and-data-processing]] | how the dealer terms are shown and accepted, and the draft clause text — for legal review (C‑27)                    |
| `private/_security-findings.md` (local) | security findings from the read. **Git-ignored and never built into the site** — it exists only on this Mac. See §9 |

---

## 1. Decided by the user (2026-10-01)

| #    | Decision                                                                                                                   | The user's words / choice                                                                                                                                                       |
| ---- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C‑1  | Proof of presence = **GPS only** (no office tablet, no Wi-Fi)                                                              | "GPS is better proof"                                                                                                                                                           |
| C‑4  | Used by **DZZLO dealers**; tenant = dealer                                                                                 | "it can be used by dip-web dealers"                                                                                                                                             |
| C‑9  | The dealer side lives at **dzzlo_ro_web's address**                                                                        | "we will share dzzlo_ro_web address. address coming soon."                                                                                                                      |
| C‑14 | Staff check in with a **native app**                                                                                       | chosen from: native app · website only · website first, app later                                                                                                               |
| C‑15 | **Inside the DZZLO OMS app**                                                                                               | chosen over a separate small attendance app                                                                                                                                     |
| C‑16 | The dealer side **inside dzzlo_ro_web**                                                                                    | chosen over a separate site on the same address                                                                                                                                 |
| C‑17 | Staff are **existing dealer users** with the scopes that exist today — order, manager, accountant, read only — no new role | "no staff will not be new role, they will either be one of currenlty present - order, amanger, accountant, read only etc."                                                      |
| C‑18 | Staff **have email addresses** — sign-in and the user model stay as they are                                               | "staff have email addresses"                                                                                                                                                    |
| C‑20 | **All devices** — every Android the app supports (7+) and every iOS it supports (15.1+)                                    | "yes all device support"                                                                                                                                                        |
| C‑24 | A **package approval list** first; packages are installed only after the user approves them                                | "list the plan of new packages we will approve then execute" → [[06-package-approval-list]]                                                                                     |
| C‑27 | **Plan the dealer-terms update** — how shown, how accepted, the text — and the user adds the clause as per the Act         | "plan the updates requried. how dealer terms will be shown and accepted, the text to write and we will add the clause as per the ACT" → [[07-dealer-terms-and-data-processing]] |
| C‑28 | The **fixes for the older API routes** are planned as tasks                                                                | "suggest fix for older api routes as tasks" → tasks_21                                                                                                                          |
| —    | Plan only, by an agent team                                                                                                | "no code implementation. just add plan in vault obsidian-notes" · "use agent teams"                                                                                             |

---

## 2. The answer in one paragraph

**Yes.** A staff member opens the DZZLO OMS app at the pump and taps **Attendance → Check in**. The app proves three things, and the server checks all three before it records anything: **the phone** — a key made inside the phone's secure hardware when it was set up, approved in person by the dealer, and usable only after the staff member's fingerprint, face or phone PIN; **the app and the phone are genuine** — Google Play Integrity on Android, Apple App Attest on iPhone; **the place** — one fresh GPS reading, inside the outlet's circle and not marked as fake by the phone itself. A pump is outdoors, where phone GPS is typically within about 5 m, so the circle can be small. Every phone the app runs on is supported; on the oldest Androids and on phones without Google's services the protection is weaker, and the dealer sees that as a flag (§3.4). What no phone check fully stops: a colleague who holds the phone and knows its PIN, and a determined cheat on a modified phone — the integrity checks catch most of those, warning flags catch some, and the dealer's own eyes do the rest. The dealer runs everything from a new **Attendance** section in dzzlo_ro_web.

---

## 3. How it works

### 3.1 Who is who

- **Dealer** — in v1 the owner and admins only (DPrimary, DAdmin) manage attendance, in dzzlo_ro_web. Other dealer users may manage it later, through permissions written only by a guarded v4 route — attendance permissions are not stored where older routes can write them (C‑22; details: `private/_security-findings.md`, local only).
- **Staff** — the dealer's **existing DZZLO users**: order (DOrder), manager (DAdmin), accountant (DAccount), order + accountant (DOrderAccount), read only (DView) — and the owner too if the dealer wants. No new role, no new scope, no change to the user model (C‑17). They sign in as they do today (email or phone + password + OTP — C‑18) and keep the screens their scope already gives them; the **Attendance** entry appears for those on the dealer's **attendance roster**.
- **The roster decides who may check in** — not a role or a scope. A person who is not yet a DZZLO user is first added through the normal user flow with the scope the dealer picks, then put on the roster. A pump attendant added as read only (DView) can see the dealer's read-only business screens — that is the dealer's choice when picking the scope.
- **Why not a new role any more:** the user chose existing scopes. That removes the frozen-file edits round 2 needed, and the risk round 2 worried about (an unknown scope getting the full dealer app) does not arise, because no unknown scope is created.

### 3.2 Setting up — once per outlet, once per staff phone

1. **The outlet.** The dealer opens Attendance → Outlet location in dzzlo_ro_web, stands at the pump and taps **Use my current location** (or types the coordinates). The circle starts at 100 m.
2. **Terms.** "Turn on attendance" starts with the dealer's owner (DPrimary) accepting the current dealer terms with the data-processing clause — an unticked box, recorded with its version, time and channel. Until then the server refuses every attendance route that collects data ([[07-dealer-terms-and-data-processing]]). Today a dealer accepts nothing inside DZZLO, so this is new for every dealer.
3. **The roster.** Attendance → Staff lists the dealer's DZZLO users. The dealer picks a person and taps **Add to attendance**. The server creates the roster entry and a **one-time enrolment code** (valid 48 h), shown once to the dealer.
4. **Set up this phone.** On the staff member's phone, signed in to DZZLO OMS: Attendance → a short notice says what is collected and why → the staff member agrees, types the enrolment code, and the phone makes its key inside its secure hardware (fingerprint / face / PIN to use it). Google's or Apple's check vouches for the app and the phone where the phone supports it. The phone is now **waiting for approval**, and the dealer gets a notification.
5. **Approval in person.** The dealer approves it in dzzlo_ro_web, with the staff member and the phone in front of them — a short **match code** shown on both screens confirms it is the same phone. The phone is **active**. One active phone per staff member — approving a new phone retires the old one. A phone with no screen lock is asked to set one first: a key that needs the owner's fingerprint or PIN cannot exist without one.

### 3.3 Checking in — each time, a few seconds

1. Tap **Attendance → Check in** (or **Check out**).
2. The app takes **one fresh GPS reading**, with the phone's own "this location is fake" flags, and asks the server for a **one-time challenge**.
3. **Google Play Integrity** (Android) or **App Attest** (iPhone) vouches for this exact request — where the phone supports it.
4. **Fingerprint / face / PIN** unlocks the phone's key, which **signs** the challenge together with the reading.
5. The server runs **eight checks** in a fixed order — on the roster and active, challenge fresh, phone active and signature valid, integrity, location not fake, location precise and fresh, inside the circle, the punch makes sense ([[01-api]]) — and answers in plain words: "Checked in 9:02 at the outlet", or the reason it refused **and how to fix it**.
6. **Every attempt that reaches the check-in step is stored**, accepted or refused (a request turned away earlier — wrong login, outdated app — is not a punch). A staff member who cannot check in sends a **manual request**; the dealer approves it, and it shows as MANUAL everywhere.

Time is the server's clock; the attendance date is the **IST** date. The phone signs how old its GPS reading is, measured on the phone, so a phone with a wrong clock is not refused — a large gap between the phone's clock and the server's is only flagged. A check-in left open for 16 hours closes as "no check-out" and never blocks the next day. App builds older than the attendance release simply have no Attendance entry; if one calls the attendance routes anyway it gets "update the app", judged by the version Google or Apple attests (C‑26).

### 3.4 What it stops — and what it doesn't

| Trick or case                                                              | Stopped by                                                                      | Still open                                                                                         |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| A colleague checks me in on **their** phone                                | the device key — their phone is not my approved phone                           | —                                                                                                  |
| I set up **a second phone**                                                | one active phone per person; the dealer approves each                           | —                                                                                                  |
| I set up **my login on a colleague's phone**                               | approval in person, phone in hand                                               | if the dealer approves without looking                                                             |
| A **fake-GPS app** on an ordinary Android phone                            | Android marks the location as mock → refused                                    | —                                                                                                  |
| Fake GPS on a **rooted** phone with tools that hide the mocking            | Play Integrity's device check fails on rooted / modified phones → refused       | a rare phone that passes both — flags and the dealer's review                                      |
| A **modified app** or an **emulator**                                      | Play Integrity / App Attest fail → refused                                      | —                                                                                                  |
| Location faked on an **iPhone** through a computer tool                    | Xcode-style simulation is flagged by iOS                                        | some third-party tools are not flagged (Apple says so) — flags + review; iPhones are rare at pumps |
| A captured request **replayed**                                            | one-time challenge, bound into the integrity check and the signature            | —                                                                                                  |
| The **phone's clock** changed                                              | server time only                                                                | —                                                                                                  |
| A **phone without Google Play services** (or an iPhone without App Attest) | no integrity answer → **accepted with a flag** the dealer sees (C‑29)           | a modified phone of that kind is not caught by integrity — the mock flag, the flags and the dealer |
| **Android 7–10**                                                           | the key opens for a short window after fingerprint / PIN, not per use — flagged | weaker than Android 11+; the dealer sees "older phone" on the device                               |
| A colleague **holds my phone and knows my PIN**                            | —                                                                               | open — a selfie at check-in would catch it (C‑7)                                                   |

**Integrity starts log-only.** For the pilot (P4), a failed integrity check is recorded and flagged but not refused, so honest staff on unusual phones are not locked out on day one. The numbers then decide when it starts refusing (C‑21). "No answer" (phones without the service) is never a refusal on its own (C‑29).

### 3.5 Why GPS works well at a pump

Phone GPS is "typically accurate to within a 4.9 m radius under open sky", worse near buildings and trees (gps.gov) — and possibly under the canopy. Starting values: **radius 100 m, accuracy limit 30 m, reading at most 30 s old**. The P0 spike measures the real numbers at a real pump before anything is fixed.

---

## 4. What Apple and Google require

DZZLO OMS is already on both stores (App Store `id1553062924`, Google Play `in.vsyst.dzzlooms`), so the developer accounts exist and every release is already reviewed. Attendance adds:

- **Location only "while using the app"**, read at the moment of check-in — no background location, no automatic check-in on arrival (those need Google's extra declaration and video, and Apple's strict review).
- **A notice and consent inside the app** before the permission prompt (Google Play's User Data policy; Apple 5.1.5) — its text is drafted in [[07-dealer-terms-and-data-processing]].
- **Clear purpose texts** — the app's current iOS location text is too vague (Apple 5.1.1(ii)).
- **Privacy forms:** Apple's privacy label and privacy manifest; Google's Data safety — precise location, device ID.
- **A demo dealer, a demo staff login and a review outlet** for Apple's App Review (2.1(a)) and Google's "App access" — the reviewer cannot stand at a pump.
- **Google's precise-location declaration** — the form opens November 2026 and is enforced from **27 January 2027**; once the app targets Android API 37, one-time precise location must use **Android 17's location button**.
- **Play Integrity linked in Play Console** — by default 10,000 token requests (warm-ups count) and 10,000 server decodes a day: about 10,000 Android check-ins, roughly 5,000 staff checking in and out, if the app warms up once per session; more on request.

Quotes, dates and URLs: [[04-platform-stores-and-law]].

---

## 5. The law (India) and the dealer terms

The **dealer** is the employer and the **Data Fiduciary**; processing for employment is a legitimate use (DPDP Act s.7(i)). **VSYST** processes the data on the dealer's behalf — a **Data Processor** — which the Act allows only "under a valid contract" (s.8(2)). So the dealer terms get a data-processing clause, with the Rules' safeguards (r.6) and fast breach alerts, because the dealer must tell the Data Protection Board within 72 hours (r.7). The core duties apply from **13 May 2027**. How the terms are shown and accepted, what is recorded, and the draft text (the clause, the acceptance screen, the staff notice) are in [[07-dealer-terms-and-data-processing]] — **a draft for legal review**; the user adds the final clause as per the Act. Attendance stays off for a dealer until the current terms are accepted.

Location is read only at check-in, never in the background. How long raw coordinates are kept is open (C‑8): the Rules may require personal data and processing logs to be kept for at least a year (r.8(3)) — a legal reading fixes the number. Details: [[04-platform-stores-and-law]].

---

## 6. Phases

| Phase     | What                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Done when                                                                                                                                                                     |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**    | **Pilot spike at one real pump** (2–3 days, a throwaway build). Four phones: a low-cost **Android 7–10**, a low-cost Android 11/12, an Android 13+, an iPhone — plus, if one is at hand, a phone without Google Play services. Measure GPS accuracy on the forecourt, under the canopy, in the sales room, 50 m and 100 m out; a fake-GPS app (must be refused); an emulator (integrity must fail); Play Integrity and key attestation on each Android; App Attest on the iPhone; how long a whole check-in takes | radius, accuracy limit and log-only vs enforce (C‑21) set from numbers; the old-Android and no-Play-services paths seen working; evidence stays local (`v1_79/.device-runs/`) |
| **P0b**   | **Prerequisite — the older-route fixes** in [[vsyst-technologies/docs/tasks/tasks_21_api_security_hardening/00-overview\|tasks_21]], at least what it marks as gating attendance: all of Wave 0 (LEG-1…LEG-6, X-SEC-2a, X-SEC-2b) plus X-SEC-1a…1d — every route that writes the membership rows both attendance gates trust, and every company user list; LEG-9, X-SEC-1e and T01-N5 recommended                                                                                                                 | those tasks red → green and deployed                                                                                                                                          |
| **P0c**   | **Approvals** — the user ticks [[06-package-approval-list]]; the terms text goes to legal review ([[07-dealer-terms-and-data-processing]])                                                                                                                                                                                                                                                                                                                                                                        | every package to be installed is approved; the clause text is final before P4                                                                                                 |
| **P1**    | **API** — the contract first ([[01-api]]); the terms records and routes ([[07-dealer-terms-and-data-processing]])                                                                                                                                                                                                                                                                                                                                                                                                 | each route red → green, mutation smokes, v4 fixtures exported                                                                                                                 |
| **P2**    | **App** ([[02-app]]) — in parallel with P3, after P1's contract                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Tier 1–3 and config tests, native unit tests, real-device runs on both platforms, old Android included                                                                        |
| **P3**    | **dzzlo_ro_web** ([[03-web]]) — the Attendance pages and the terms acceptance                                                                                                                                                                                                                                                                                                                                                                                                                                     | tests and the repo's gates                                                                                                                                                    |
| **P4**    | **Pilot with one dealer** who has accepted the terms: integrity log-only for about two weeks, then refuse; the store declarations; then rollout                                                                                                                                                                                                                                                                                                                                                                   | refusal reasons understood; the dealer's register matches reality                                                                                                             |
| **Later** | the Android 17 location-button wrapper (needed before the app targets API 37); a selfie (C‑7); late / shift rules (C‑6); more than one site (C‑3); Hindi switched on (C‑10); pumps without internet (C‑25); attendance managers beyond the owner and admins (C‑22)                                                                                                                                                                                                                                                | —                                                                                                                                                                             |

Nothing is built before the user says **"start"**. Each phase goes red → green; the user commits, pushes and merges. Effort is not estimated here, except one figure from the vault's native-modules course: the integrity modules alone take about iOS 5–10 days plus the server side, and Android 2–4 days ([[vsyst-technologies/docs/learning/native-modules/11-reference|course reference]]).

---

## 7. Calls

### 7.1 Answered (2026-10-01)

C‑1 GPS only · C‑4 DZZLO dealers · C‑9 dzzlo_ro_web's address (the address itself is still to come) · C‑14 native app · C‑15 inside the DZZLO OMS app · C‑16 dealer side inside dzzlo_ro_web · C‑17 existing dealer users and scopes · C‑18 staff have email · C‑20 all devices · C‑24 approval list first · C‑27 plan the terms · C‑28 older-route fixes as tasks — §1.

### 7.2 No longer apply

C‑5 (iPhone Home Screen web app) · C‑12 (HR sign-in — dealers use their DZZLO login) · C‑13 (where the code lives — the three existing repos) · C‑23 (dealer-role managers checking in — every staff member is a dealer user now, so anyone on the roster can check in).

### 7.3 Open

| #    | Question                                                         | Options                                                    | Recommended                                                                                                                                                                                                                                                                                                                           | Where      |
| ---- | ---------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| C‑29 | Phones without Google Play services / iPhones without App Attest | accept with a flag · manual requests only                  | **accept with a flag** — needed for "all devices"; the same for an Android key without a hardware attestation chain; the mock-location check still applies and the dealer sees the flag. **No downgrade:** a phone that enrolled with an integrity answer and later reports none counts as a failure, or any phone could claim "none" | 01, 02, 04 |
| C‑21 | When integrity starts refusing (a real failure, not "no answer") | log-only pilot, then refuse · refuse from day one          | **log-only pilot, then refuse**                                                                                                                                                                                                                                                                                                       | 01, 04     |
| C‑8  | Keep raw coordinates for                                         | 90 days · 1 year · forever                                 | **1 year, tight access**, then distance + result only — pending a legal reading of DPDP Rules r.8(3); a TTL collection or a daily sweep does the dropping                                                                                                                                                                             | 01, 04, 07 |
| C‑19 | Phone PIN when fingerprint / face fails                          | allow · biometric only                                     | **allow** — cheap sensors, worn fingers; the dealer approves each phone                                                                                                                                                                                                                                                               | 02         |
| C‑22 | Who gets it, who manages                                         | DIP dealers · all dealers; owner + admin · any dealer user | **DIP dealers in v1; only DPrimary + DAdmin manage in v1**; other dealer users later, through a guarded v4 grant                                                                                                                                                                                                                      | 01, 03     |
| C‑26 | Old app builds                                                   | version gate on the attendance routes · none               | **version gate on the attendance routes** — judged by the version Google / Apple attests                                                                                                                                                                                                                                              | 01, 02     |
| C‑2  | What is recorded                                                 | check-in only · in + out · in + out + breaks               | **in + out**                                                                                                                                                                                                                                                                                                                          | —          |
| C‑3  | Sites per dealer                                                 | one · several                                              | **one in v1**                                                                                                                                                                                                                                                                                                                         | 01, 03     |
| C‑6  | Late / shift rules                                               | none · start time + grace · full shifts                    | **none in v1**                                                                                                                                                                                                                                                                                                                        | —          |
| C‑7  | Selfie at check-in                                               | no · sometimes · always                                    | **no in v1**                                                                                                                                                                                                                                                                                                                          | —          |
| C‑10 | Language                                                         | English · English + Hindi                                  | **English + Hindi strings from day one** — Hindi stays hidden while 1.79's English lock holds                                                                                                                                                                                                                                         | 02         |
| C‑11 | Size                                                             | dealers × staff                                            | your numbers — Play Integrity's defaults fit about 5,000 Android staff checking in and out a day; more on request                                                                                                                                                                                                                     | 04         |
| C‑25 | Pumps without internet                                           | online only + manual request · offline queue               | **online only + manual request**                                                                                                                                                                                                                                                                                                      | 01, 02     |

Also waiting on the user: the **Approved?** column in [[06-package-approval-list]], the open questions **D‑…** in [[07-dealer-terms-and-data-processing]] (for the user and their lawyer), and the questions **H‑…** in tasks_21.

### 7.4 Small items for P1 to settle between [[01-api]] and [[02-app]]

- What a refusal returns besides its code — distance, radius, accuracy and limit — so the app can print "240 m from the outlet (allowed 100 m)".
- A re-sent check-in with the same idempotency key gets the stored answer, not a second punch.
- Android 17's location button is a system-drawn view, so the later wrapper is a native view component — a fourth native piece after the three modules.
- The staff notice's text comes from the API (versioned, stored with each enrolment) rather than being built into the app, so it can change without a release — 07 recommends it; 02 §5 adjusts at P1. 07 also recommends the notice in Hindi from launch, which needs a decision on 1.79's English lock for that one screen (C‑10).
- **OneSignal's location sharing must be confirmed off** before the staff notice can truthfully say "no background location" — the app links OneSignal's location module today. Upgrading to a release that leaves the module out is the optional item in [[06-package-approval-list]]; it becomes needed if the setting cannot be confirmed.

---

## 8. Deliberately not in this plan

- **SIM binding** — not needed; the device key and the integrity checks do that job.
- **Background tracking or automatic check-in on arrival** — needs background location: strict store review and battery cost.
- **A website check-in** — round 1 is kept in [[05-round-1-web-design]] in case it is ever wanted.
- A new user role or scope for staff (decided against, C‑17).
- Leave, holidays, payroll, salary. Face recognition.
- The fixes for the older API routes themselves — planned separately in tasks_21.
- The dzzlo_ro_web address itself — the user will share it.
- Final legal text — the user and their lawyer finish the clause (07 is a draft).
- Code — plan only.

---

## 9. Security findings — kept private

The research read the API, the app and dzzlo_ro_web and found security weaknesses in **existing code, outside attendance**. This vault is a public repository published as a website, so the details are in `private/_security-findings.md` (local only — git-ignored and never built into the site), and the user was told in chat on 2026-10-01. The fixes are planned as tasks in [[vsyst-technologies/docs/tasks/tasks_21_api_security_hardening/00-overview|tasks_21]] (class-level in public, specifics in its private plan) and build on tasks_01's security IDs. What can be said here: attendance trusts only data written through the guarded v4 module, takes the dealer from the login and never from the request, and does not rely on older routes.

---

## 10. Rounds

- **2026-10-01 — round 1.** "Can a website bind a device, a location or a SIM like an app?" → device yes, location yes but soft, SIM no. Then the attendance question → a website: passkey + browser key, GPS + a rotating code on an office tablet. Answers: phones; a new standalone site. → [[05-round-1-web-design]].
- **2026-10-01 — round 2.** "native app would require permissions from apple and google right? is it still better choice?" → yes, reviewed by both — and DZZLO already has both accounts; with GPS as the proof, native is the better choice because only an app can tell a fake location. Answers: C‑1, C‑4, C‑9, C‑14, C‑15, C‑16. "use agent teams" → four read-only researchers (API, app, dzzlo_ro_web, platform), who then wrote 01–04 from one shared sheet; the orchestrator wrote this overview and the private note.
- **2026-10-01 — round 3.** Answers: C‑17 (existing dealer users and scopes — the `staff` role and its frozen-file edits are gone), C‑18 (staff have email), C‑20 (all devices — old-Android and no-Play-services paths added, C‑29 opened), C‑24 (→ [[06-package-approval-list]]), C‑27 (→ [[07-dealer-terms-and-data-processing]]), C‑28 (→ tasks_21). The same team revised 01–04 and wrote 06; two more agents wrote 07 and tasks_21.
