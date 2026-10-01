---
title: tasks_20 · 05 — round 1, the web-only design (superseded)
status: SUPERSEDED 2026-10-01 by round 2 (00-overview) — kept for reference; nothing built
---

# Round 1 — attendance as a website (superseded)

> **SUPERSEDED 2026-10-01 (round 2).** The same day the user decided: staff check in with the **native DZZLO OMS app**, proof = **GPS only**, users = **DZZLO dealers**, dealer side **inside dzzlo_ro_web**. The current plan is [[00-overview]]. This note is kept unchanged below as the record of round 1 — and as the reference if a browser check-in is ever wanted (for example for staff without a supported phone). Its §1 browser facts were checked on 2026-10-01 and age fast.

**Status (round 1): PROPOSED 2026-10-01 — plan only.** No code, no repo, nothing built — the user: "no code implementation. just add plan in vault obsidian-notes". Building waits for the calls in §12 and the user's word "start".
**Created:** 2026-10-01, from the user: "we want to create a attendence website that can let employee use only thier device in office corrdinates only. is it possible?"
**Answered so far (2026-10-01):** employees use their **phones** (not office computers); it is a **new standalone site** (not part of DZZLO OMS).
**Scope:** One website with two sides — the **employee** side (register one phone, check in, check out, see own history) and the **HR** side (approve phones, set offices, read the register, export). Optional third page: a **screen at the office entrance** (C‑1).
**Web facts:** §1 was checked on 2026-10-01 against the sources at the end. Browsers change fast (Chrome changed its location prompt in May 2026) — re-check §1 at "start".

---

## 0. The answer in one paragraph

**Yes — with one limit.** "Only their own phone" is strong on the web: a **passkey** (Face ID / fingerprint) proves the person, and a **device key** that the browser can never export proves the phone. "Only inside the office" is **soft if it rests on GPS alone**: on Android a fake-GPS app feeds the browser a false location, and a web page cannot tell. So the plan adds one physical proof of being there — a **code that changes every 30 seconds on a screen at the office** (recommended, C‑1) or the office Wi-Fi's internet address. Then cheating needs two separate tricks at the same moment. If that is still not enough, the step after is a native app (§10), which can detect fake GPS and prove it is a genuine app on a genuine phone. A website cannot do SIM binding at all; this plan does not need it.

---

## 1. What a phone's browser can and cannot do (checked 2026-10-01)

| Need                            | Android — Chrome                                                                                                                                                   | iPhone — Safari                                                                                                                                                                                             | What the plan does                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Secure site                     | location and passkeys work only on `https://`                                                                                                                      | same                                                                                                                                                                                                        | HTTPS everywhere, local testing included                                  |
| Precise location                | since **May 2026** Chrome asks each site **Precise** or **Approximate**; approximate ≈ 1.5 km; an API for a site to say "I need precise" is announced, not shipped | Settings → Privacy & Security → Location Services → **Safari Websites** → Precise Location; off = approximate                                                                                               | refuse vague readings (§3.2) and show how to switch Precise on            |
| Remembered permission           | remembered ("allow while visiting the site")                                                                                                                       | Home Screen web apps are reported to **ask every session**                                                                                                                                                  | one extra "Allow" tap on iPhone — accepted; P0 confirms                   |
| Fake location                   | fake-GPS apps (Android's developer "mock location") feed Chrome; **a page cannot detect it** — a native app can                                                    | needs a computer and developer tools — much harder                                                                                                                                                          | the second proof, C‑1                                                     |
| Background                      | none — location only while the page is open and asks                                                                                                               | same                                                                                                                                                                                                        | location read only at the punch (also the privacy rule, §8)               |
| Storage lifetime                | the installed app shares Chrome's storage; kept unless the user clears it or the phone runs out of space                                                           | Safari tab: script storage (IndexedDB, localStorage) **deleted after 7 days of Safari use without a visit**. A **Home Screen web app has its own storage, apart from Safari, and is exempt** from that rule | iPhone users install to the Home Screen and register **inside** it (§2.2) |
| Passkeys                        | yes — synced by Google Password Manager                                                                                                                            | yes — synced by iCloud Keychain; can be shared with other people from the Passwords app                                                                                                                     | the passkey proves the **person**, not the phone (§2.1)                   |
| A key the page cannot export    | WebCrypto non-extractable key, kept in IndexedDB                                                                                                                   | same                                                                                                                                                                                                        | proves the **phone** (§2.1)                                               |
| Camera + QR                     | camera yes; built-in `BarcodeDetector` yes                                                                                                                         | camera yes; `BarcodeDetector` **no** (behind a flag, off by default, through iOS 26.5)                                                                                                                      | a small JS / WASM QR decoder inside the app                               |
| Proof the browser is untampered | none on the web                                                                                                                                                    | none                                                                                                                                                                                                        | accepted for v1; native app if needed (§10)                               |
| SIM                             | invisible to a page                                                                                                                                                | same                                                                                                                                                                                                        | not used                                                                  |

---

## 2. "Only their own phone"

### 2.1 Two keys, two jobs

Every check-in and check-out carries **two signatures over the same one-time challenge**. Either one alone is refused.

| Key                                                                             | Made by                                                                     | Proves                         | Weak on its own because                                                                                                                             |
| ------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Passkey** (WebAuthn, user verification required)                              | the phone's password manager, unlocked by Face ID / fingerprint / phone PIN | the **person** is present      | it syncs to the person's other devices (iPad, laptop), it can be shared from Apple's Passwords app, and anyone who knows the phone's PIN can use it |
| **Device key** (WebCrypto ECDSA P-256, `extractable: false`, kept in IndexedDB) | the attendance page, once, at registration                                  | **this browser on this phone** | it lives only in this browser's storage — cleared data or a removed app deletes it; a rooted phone could copy it                                    |

The server keeps only the two **public** keys. On phones the passkey's "backed up" flag will almost always say synced — that is expected and not a reason to refuse it; the device key does the binding.

### 2.2 Registering a phone

1. HR adds the employee (name, mobile, email, office). The console makes an **invite**: a link plus an **8-character code**, single use, valid 48 hours. HR sends both on WhatsApp or email.
2. **Android:** open the link in Chrome → "Install app" (optional, recommended).
   **iPhone:** open the link in Safari → Share → **Add to Home Screen** → open the app from the Home Screen. The installed app opens at its start page, not at the invite link, and it does not share Safari's storage — so the employee **types the code inside the installed app**. This is why the invite carries a code and not only a link.
3. In the app: enter the code → create the passkey (Face ID / fingerprint prompt) → the page makes the device key and asks the browser for persistent storage → it runs the §3 location check (so registration happens **at the office**) → it sends both public keys and the phone's details (OS and browser; the model on Android) → the phone is **PENDING**.
4. HR approves on the Devices page → **ACTIVE**. Rule: approve **in person**, with the employee and the phone in front of HR — this is what stops "my account on a friend's phone" (§7).
5. One **ACTIVE** phone per employee. Approving a new one revokes the old one.
6. New phone, lost phone, cleared browser data, removed app → HR revokes, sends a new invite, approves again. Every approve / reject / revoke goes to the audit log (who, when).

---

## 3. "Only inside the office"

### 3.1 The office on a map

HR drops a **pin** on a map (the middle of the building) and sets two numbers per office:

- **Radius** — how far from the pin a check-in may be. Start at **150 m**.
- **Accuracy cap** — the vaguest reading still accepted. Start at **100 m**. (A phone reports how sure it is: "within ± N m, 95 % of the time". An approximate reading is off by a kilometre or more and is refused.)

Both starting numbers are guesses until the P0 spike (§11) measures real readings at the office.

### 3.2 The rule — the server decides, never the page

- The page asks for a **fresh** reading: high accuracy on, no cached position, wait up to 20 s.
- **Accepted** only if accuracy ≤ cap **and** distance from the pin ≤ radius.
- The distance and the accuracy are **stored with every attempt**, accepted or refused — HR tunes the two numbers from real data after the first two weeks, and settles disputes from the same record.
- The reply is in plain words, with the fix: "You are 240 m from Head Office (allowed 150 m)." / "Your location is only approximate (± 1.5 km). Turn on Precise location: …" — with the steps for Android and for iPhone.

### 3.3 Flags — warn HR, never block

- **Same coordinates to six decimals on two different days** — a real GPS never repeats that exactly; a fake-GPS app with a saved pin does.
- **The same accuracy number on every punch.**
- **Impossible travel** — refused 12 km away at 9:00, accepted at the office at 9:03.

### 3.4 The second proof of being there — C‑1

GPS alone stops casual cheating, not a fake-GPS app. Pick one extra proof:

| Option                                      | How                                                                                                       | Needs                                                                      | Beats fake GPS?        | Weak spots                                                                                                                                                                   |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A. GPS only**                             | nothing extra                                                                                             | nothing                                                                    | no — flags only (§3.3) | Android fake-GPS apps                                                                                                                                                        |
| **B. + office Wi-Fi**                       | the server accepts a check-in only from the office's public internet address                              | a **static public IP** from the ISP; phones must be **on office Wi-Fi**    | yes                    | many phones stay on mobile data; the ISP may change the IPv6 prefix (serve the check-in call on an IPv4-only address, or watch the prefix); Wi-Fi down = nobody can check in |
| **C. + rotating office code** (recommended) | a screen at the entrance shows a QR and 6 digits that change every 30 s; the employee scans it in the app | one cheap Android tablet or an old phone on a stand per office, plugged in | yes                    | a friend can send a photo of the code — it dies in about 60 s, and the absent person must also fake GPS at that moment                                                       |
| **D. Kiosk scans the phone**                | the phone shows a one-time QR; a tablet with a camera at the door scans it                                | a camera tablet, and a queue at the door                                   | yes                    | queues; a screenshot sent to a friend works until it expires                                                                                                                 |

**Recommended: C.** It needs no ISP change, keeps working when the office internet is down, and costs one small tablet per office.

### 3.5 The office screen (if C‑1 = C)

- A cheap Android tablet or an old phone on a stand at the entrance, plugged in, screen always on, locked to the one page (Android screen pinning / iPad Guided Access).
- It opens the site's **screen page**; HR registers and approves it like a phone. It gets its **own secret**.
- It shows a **QR** and the same code as **6 digits**, both changing every **30 s**, computed on the tablet from its secret (the TOTP method — same idea as Google Authenticator). So it **keeps working when the office internet is down**.
- The employee scans the QR **inside the attendance app** (the page opens the camera), or types the 6 digits if the camera fails.
- The server accepts the **current code and the one before** (about 60 s), and **only for that office**.
- HR can **rotate** a screen's secret any time — at once if the tablet is lost.
- Why not the phone's own camera app: on iPhone it would open the link in Safari, which does not hold the Home Screen app's device key.

---

## 4. Check-in and check-out

### 4.1 What the employee does

Open the app → tap **Check in** → scan the office code (if C) → allow location (iPhone may ask each session) → Face ID / fingerprint → "Checked in 9:02 at Head Office". Check-out is the same button later. Below it: their own last 30 days.

### 4.2 What the server checks — in order, first failure wins

| #   | Check                                                                                            | Refusal code                      |
| --- | ------------------------------------------------------------------------------------------------ | --------------------------------- |
| 1   | signed-in employee, status ACTIVE                                                                | `EMPLOYEE_INACTIVE`               |
| 2   | the challenge exists, is unused and not older than 2 min — then mark it used                     | `CHALLENGE_BAD`                   |
| 3   | passkey signature valid, user verified, the passkey belongs to this employee                     | `PASSKEY_BAD`                     |
| 4   | device-key signature valid over the same challenge; the device is ACTIVE and this employee's     | `DEVICE_NOT_ACTIVE`               |
| 5   | accuracy ≤ the office's cap                                                                      | `LOCATION_VAGUE`                  |
| 6   | distance ≤ the radius of one of the employee's offices                                           | `OUTSIDE_OFFICE`                  |
| 7   | office code valid for that office (C) / request from an allowed IP (B)                           | `CODE_BAD` / `NOT_OFFICE_NETWORK` |
| 8   | the punch makes sense: no second check-in while one is open, at least 2 min since the last punch | `DUPLICATE`                       |

Every attempt is stored — accepted or refused, with its code — so a dispute is a lookup, not an argument.

### 4.3 Time

- **Server clock only.** The phone's clock is never used.
- Store the instant in UTC; the **attendance date is the IST date** (Asia/Kolkata) of the check-in, computed on the server per request — never from the host's own zone (the OMS API host runs UTC; the same trap waits here).
- A shift that crosses midnight belongs to the day it started.
- A check-in left open for **16 hours** is closed as **"No check-out"** — no hours counted, HR sees it — and it never blocks the next day's check-in. Hours are never invented.

### 4.4 When it fails — a manual request

"Can't check in?" → the employee writes a reason; the last refusal code is attached → HR approves or rejects → the punch shows as **MANUAL** in every report. HR can also add a manual punch directly (a reason is required). Both go to the audit log.

---

## 5. HR console

| Page          | What HR does there                                                                  |
| ------------- | ----------------------------------------------------------------------------------- |
| **Today**     | who is in, who is not, open check-ins, flagged punches                              |
| **Employees** | add, edit, deactivate; send or resend an invite                                     |
| **Devices**   | approve / reject pending phones; revoke; each phone's last punch                    |
| **Offices**   | map pin, radius, accuracy cap; screens and their secrets (C); allowed IPs (B)       |
| **Requests**  | approve / reject manual requests                                                    |
| **Register**  | month grid, employee × day: in, out, hours, MANUAL, flags; export CSV / Excel       |
| **Audit log** | every approval, revoke, manual punch and setting change — who, when, before → after |

Roles: **Owner** (everything, including HR accounts), **HR** (everything else), **Employee** (own punches only). HR signs in with a passkey, email OTP as the fallback (C‑12). The console works on a phone too.

---

## 6. Records (what is stored — not code)

| Record    | Main fields                                                                                                                                                |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Company   | name, time zone (Asia/Kolkata) — one row today (C‑4)                                                                                                       |
| Office    | name, pin (lat, lng), radius m, accuracy cap m, allowed IPs, active                                                                                        |
| Screen    | office, device public key, secret (encrypted at rest), status                                                                                              |
| Employee  | name, mobile, email, offices, role, status                                                                                                                 |
| Invite    | employee, code hash, expires at, used at                                                                                                                   |
| Device    | employee, passkey id + public key + counter, device public key, user agent, status PENDING / ACTIVE / REVOKED, approved by / at                            |
| Challenge | random value, employee, expires at, used at — deleted after minutes                                                                                        |
| Punch     | employee, device, office, IN / OUT, time (UTC), IST date, lat, lng, accuracy, distance, IP, code ok, ACCEPTED / REFUSED + code, flags, source APP / MANUAL |
| Request   | employee, date, type, reason, status, decided by / at                                                                                                      |
| Audit     | who, action, target, before, after, when                                                                                                                   |

Raw lat / lng are dropped after the retention period (C‑8); distance and result stay for the register.

---

## 7. Cheats — what stops each one

| Trick                                                                 | Stopped by                                                       | Still open                                                                                      |
| --------------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| A friend checks me in on **their own** phone                          | the device key — their phone is not mine                         | —                                                                                               |
| A friend uses **my** phone                                            | the passkey wants my face / fingerprint                          | if the friend knows my phone PIN (the passkey falls back to it) — a selfie (C‑7) would catch it |
| I register **a second phone**                                         | one ACTIVE phone per employee; HR approves each                  | —                                                                                               |
| I register **my account on a friend's phone** so they check in for me | registration at the office; HR approves in person, phone in hand | if HR approves without looking                                                                  |
| I check in **from home with a fake-GPS app**                          | the office code (C) or office Wi-Fi (B)                          | with A (GPS only): flags only                                                                   |
| A friend **sends me a photo of the office QR** and I fake GPS         | the code dies in about 60 s, and both tricks must land together  | a determined pair can still do it — flags, and a selfie (C‑7), raise the cost                   |
| I **change the phone's clock**                                        | server time only                                                 | —                                                                                               |
| Someone **replays** a captured check-in                               | one-time challenge, 2 min                                        | —                                                                                               |
| I **clear data / reinstall** to start fresh                           | the device key is gone → HR must approve again                   | —                                                                                               |
| HR **edits** a punch                                                  | audit log; manual punches are marked                             | the Owner must read the log                                                                     |
| A **modified browser / rooted phone** sends made-up data              | nothing on the web proves the browser is untampered              | the native app (§10)                                                                            |

---

## 8. Privacy (India)

- **DPDP Act 2023, s.7(i):** processing for employment is a _legitimate use_ — no consent form is needed. The rest still applies: use it only for attendance, keep it secure, delete it on time.
- Location is read **only at the moment of a punch** — never in the background, never on a timer.
- A short **notice** at registration: what is stored (punch times, the location at the punch, phone details), why, who sees it (HR, Owner), and how long (C‑8).
- Employees see **their own** punches, including the distance recorded.
- Raw coordinates are kept for the C‑8 period, then dropped; distance and result stay.
- No face data unless C‑7 says selfie — and then a photo only, no face recognition, same retention.
- Exports are personal data too: HR and Owner only.

---

## 9. Stack and hosting — proposal, confirm at "start"

| Part     | Proposal                                                                      | Why                                                                                                                               |
| -------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| API      | Node + Express + MongoDB (Atlas)                                              | the team's OMS stack                                                                                                              |
| Web      | React (Vite) PWA — one app for employees and HR, by role                      | the same shape as dzzlo-ro-web / dip-web                                                                                          |
| Passkeys | SimpleWebAuthn (server + browser packages)                                    | maintained; does the WebAuthn parsing and checks                                                                                  |
| QR       | generated on the screen page; decoded in the app by a small JS / WASM decoder | iPhone Safari has no built-in `BarcodeDetector`                                                                                   |
| Map      | Leaflet + OpenStreetMap tiles, on HR's Offices page only                      | free; light use                                                                                                                   |
| Hosting  | HTTPS; API and web on the same domain                                         | passkeys and location need HTTPS                                                                                                  |
| Domain   | the exact site address fixed **before the first registration** (C‑9)          | passkeys are tied to the domain and device keys to the exact address — changing either later means every employee registers again |

House rules carried over from OMS:

- **Every route behind sign-in and a role check**, with a test that walks the route table and fails on any route without them — this site starts guarded.
- **Every query scoped by company** (C‑4), even while there is one company.
- **Rate limits** on sign-in, invite and punch.
- **Test-first**, a red commit then a green one, as in [[vsyst-technologies/docs/oms_api/tdd-testing-guide|API TDD guide]] and [[vsyst-technologies/docs/dip_web/tdd-testing-guide|web TDD guide]]; branches and PRs as in [[vsyst-technologies/docs/github_workflow/00-github-workflow|GitHub Workflow]]. Nothing is committed or pushed without the user's word.

---

## 10. When the web is not enough — the native step

Signs: flags keep coming back, disputes, attendance drives pay. Then:

- A **native app** (React Native, like the OMS app) as a second client on the same API: Android can see a **mock location**; **Play Integrity / App Attest** prove a genuine app on a genuine phone; the location permission is remembered; an automatic check-in on arrival is possible but needs **background location** — heavier store review and battery cost, see [[vsyst-technologies/docs/learning/native-modules/07-phase-7-maps-and-location|Native modules, Phase 7 — maps and location]]. HR stays on the website.
- Or a **biometric punch machine** at the door.

---

## 11. Phases

| Phase                            | What                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Done when                                                                                                              |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **P0 — device spike** (1–2 days) | a throwaway HTTPS test page; one iPhone and one Android phone; **at the office**. (1) GPS accuracy at the entrance, at desks on each floor, in the parking, and 100 m / 200 m outside. (2) iPhone Home Screen app: how often the location prompt appears; passkey create + use; the device key still there after a restart and after 8 days unused; the camera scanning a QR. (3) Android Chrome: the Precise / Approximate prompt; the installed app; the same passkey and device-key checks. (4) Only if C‑1 = B: the office's public IPv4 / IPv6 today and after a router restart. | every row of §1 confirmed or corrected in round 2 (§14); radius and cap set from the numbers                           |
| **P1 — core**                    | registration + approval; check in / out with passkey + device key + GPS; refusal messages; manual requests; HR pages (Today, Employees, Devices, Offices, Requests, Register + export, Audit); the privacy notice                                                                                                                                                                                                                                                                                                                                                                     | an employee can register, be approved, check in and out at the office — and is refused 250 m away with a clear message |
| **P2 — second proof**            | C‑1's choice (office screen or Wi-Fi) + the §3.3 flags                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | a fake-GPS check-in from outside is refused                                                                            |
| **P3 — later, only if asked**    | shift / late rules (C‑6), leave, Hindi (C‑10), a manager view, more companies (C‑4), the native app (§10)                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | —                                                                                                                      |

Nothing is built before the user says **"start"**. Each phase is red → green; the user commits.

---

## 12. Calls — open

| #    | Question                            | Options                                                                            | Recommended                                                                                                              |
| ---- | ----------------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| C‑1  | Second proof of being in the office | A GPS only · B + office Wi-Fi · C + rotating office code · D kiosk scans the phone | **C** — no ISP change, works with the internet down, one cheap tablet per office                                         |
| C‑2  | What is recorded                    | check-in only · in + out · in + out + breaks                                       | **in + out** — gives hours worked                                                                                        |
| C‑3  | Offices                             | one · several, each with its own pin                                               | **several in the design**, start with one                                                                                |
| C‑4  | Who uses it                         | our company only · other companies later                                           | **our company, built tenant-ready** — a company id on every record and every query, so selling it later is not a rewrite |
| C‑5  | iPhone way of use                   | Home Screen app · Safari tab                                                       | **Home Screen app** — keeps the device key; costs one location tap per session                                           |
| C‑6  | Late / shift rules in v1            | none (times only) · start time + grace + late mark · full shifts                   | **none** — times only; rules in P3                                                                                       |
| C‑7  | Selfie at punch                     | no · random 1 in N · every punch                                                   | **no** for v1                                                                                                            |
| C‑8  | Keep raw coordinates for            | 90 days · 1 year · forever                                                         | **90 days**, then distance + result only                                                                                 |
| C‑9  | Site name and domain                | —                                                                                  | user — needed before P1                                                                                                  |
| C‑10 | Language                            | English · English + Hindi                                                          | **English** for v1                                                                                                       |
| C‑11 | Size                                | number of employees and offices                                                    | user — sizing only                                                                                                       |
| C‑12 | HR sign-in                          | passkey + email OTP fallback · password + OTP                                      | **passkey + email OTP**                                                                                                  |
| C‑13 | Where the code lives                | new repo name and folder                                                           | user — at "start"                                                                                                        |

---

## 13. Deliberately not in this plan

- **SIM binding** — a web page cannot see the SIM (§1).
- Background tracking, live location, route history.
- Leave, holidays, payroll, salary.
- Face recognition.
- Any change to DZZLO OMS (api, app, dip-web, dzzlo-ro-web).
- Code — plan only (user, 2026-10-01).

---

## 14. Rounds

- **2026-10-01 — round 1.** The user asked whether a website can bind a device, a location or a SIM the way an app can → device yes (passkey + a browser key), location yes but soft, SIM no. Then: an attendance website — only their own device, only office coordinates — possible? → yes, with a second proof of being there. Answers: **phones**; **new standalone site**. The static-IP / entrance-tablet question was left open → C‑1. Then: "no code implementation. just add plan in vault obsidian-notes" → this note. §1 checked against the sources below the same day.

---

## Sources (read 2026-10-01)

- Chrome for Android — Precise / Approximate location per site, May 2026: https://ppc.land/chrome-on-android-now-lets-users-share-approximate-location-with-websites/
- WebKit — Tracking Prevention (7-day cap on script-writeable storage; Home Screen web apps isolated from Safari and exempt): https://webkit.org/tracking-prevention/
- WebKit blog — Full Third-Party Cookie Blocking and More (2020-03-24; Home Screen web apps keep their data): https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/
- MagicBell — PWA iOS limitations (2026-03-20; geolocation needs permission each session): https://www.magicbell.com/blog/pwa-ios-limitations-safari-support-complete-guide
- Can I use — BarcodeDetector (not in iPhone Safari by default): https://caniuse.com/mdn-api_barcodedetector
- DPDP Act 2023, section 7 (legitimate uses; 7(i) employment): https://indiankanoon.org/doc/62814281/
- W3C Geolocation (accuracy in metres, 95 % confidence): https://www.w3.org/TR/geolocation/
- W3C WebAuthn Level 3 (user verification; backup flags): https://www.w3.org/TR/webauthn-3/
