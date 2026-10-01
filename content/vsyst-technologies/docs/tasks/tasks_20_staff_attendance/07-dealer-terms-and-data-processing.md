---
title: tasks_20 · 07 — dealer terms and the data-processing clause (C‑27)
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start". The draft text is for legal review — not legal advice.
---

# 07 — Dealer terms and the data-processing clause (C‑27)

Part of [[00-overview]]. Siblings: [[01-api]] · [[02-app]] · [[03-web]] · [[04-platform-stores-and-law]].

**Asked (2026-10-01):** "c-27 plan the updates requried. how dealer terms will be shown and accepted, the text to write and we will add the clause as per the ACT."

**Source.** `api:` = `dzzlo_oms_api` `slave` @ `86083ca` · `app:` = `dzzlo_oms_app` `slave` @ `ea7e7222` · `web:` = `dzzlo_ro_web` `main` @ `5a66bf8`, all searched with `git grep` on 2026-10-01. The DPDP Act and Rules were read from MeitY's PDFs the same day (§2). Staff are existing dealer users on the attendance roster (round 3, C‑17). The D‑numbers in §6 belong to this note only.

## 0. Summary

Today a dealer accepts nothing inside DZZLO, and no acceptance is recorded anywhere. The app's dealer sign-up has no terms text, link or checkbox. dzzlo_ro_web has no sign-up at all. The API has no terms model, field or route. The Terms and Conditions on vsyst.in were drafted for Easebuzz, and the product never shows them.

This note plans:

- **three versioned documents** — the Dealer Terms, a **Data Processing Addendum (DPA)** written to the DPDP Act and Rules, and a **staff notice**;
- **an append-only acceptance record** per dealer, in a new v4 `/terms` module;
- **a server-side gate:** attendance collects nothing for a dealer until the dealer's owner (DPrimary) has accepted the current DPA.

How it plays out:

- **Existing dealers** accept as step 1 of "Turn on attendance" in dzzlo_ro_web.
- **New dealers** tick an unticked box at sign-up in the app.
- **A material new version** needs re-acceptance. Until then, new collection waits.
- **Turning attendance off** stops collection at once. The records are kept for the legal minimum, then erased.
- **Staff** see a separate notice, shown on the dealer's behalf, before their phone is set up. The same notice meets Google Play's and Apple's disclosure-and-consent rules.

§5 holds the draft texts for the lawyer, with every decision marked **[LAWYER: …]**. §6 lists the open questions D‑1 to D‑16.

## 1. What exists today

| Where                | Today                                                                                                                                                                                                                                                                                                                                                                                                                                       | path:line                                                                                                                                                                                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| API — sign-up        | `POST /api/v3/auth/registerrx` creates the dealer and its first user, scope DPrimary. The body carries only `user`, `company` and `notify`. Nothing about terms is sent or stored.                                                                                                                                                                                                                                                          | `api:api_v3/routes/auth/index.js:69` · `api:api_v3/controllers/auth/app_redux.js:28-38` · `api:api_v3/services/auth.js:80-168` (DPrimary `:144`)                                                                                                                                            |
| API — data           | No terms, policy or consent model, field, collection or route anywhere in the tree. The user and dealer schemas carry no acceptance. The only "accept" flags belong to business flows: company invites and vehicle requests.                                                                                                                                                                                                                | `api:models/users.js:54-130` · `api:models/dealer_msts.js:6-75` · `api:models/invites.js:12` · `api:models/veh_reqs.js:15`                                                                                                                                                                  |
| App — Welcome        | "Create New Company ?" leads to Sign up as Customer or Dealer. Styles for a terms panel are still in the file, but nothing renders them (they arrived in `f24850de`).                                                                                                                                                                                                                                                                       | `app:src/screens/Login/AuthNavigator/Welcome.js:117-157`, `:242-264`                                                                                                                                                                                                                        |
| App — dealer sign-up | Company name, dealer code, email, phone and password, then SIGN UP. No terms text, no link, no checkbox. The mutation posts only `user` and `company`.                                                                                                                                                                                                                                                                                      | `app:src/screens/Login/AuthNavigator/Dealer.js:23-61`, `:142-154`, `:238-246` · `app:src/store/apis/dzzlooms/auth.js:75-95`                                                                                                                                                                 |
| App — elsewhere      | Settings shows Theme, Store Version and Delete Account. Help opens the user manuals, and Contact Us shows an email address. **There is no Terms or Privacy Policy link anywhere in `src/`.** The "Agreement Status" switches are the dealer–customer verification flag (`cust_verified`), not legal terms.                                                                                                                                  | `app:src/screens/Common/Settings/index.js:139-160` · `app:src/screens/Common/Help/index.js:12-13` · `app:src/screens/Common/ContactUs/index.js:152` · `app:src/screens/Dealer/Customers/CustSettings.js:1493`                                                                               |
| dzzlo_ro_web         | No terms or privacy text. Sign-in's "Sign up" link goes to `/signup`, which is not routed for a signed-out user. The SignUp page is a static form whose only button leads back to sign-in. **Dealers cannot sign up on the web.** dip-web (`slave_dev` @ `6a4276f`) has no terms text either.                                                                                                                                               | `web:src/pages/auth/SignIn/index.js:467-481` · `web:src/App.js:304-308` · `web:src/pages/auth/SignUp/index.js:8-111`                                                                                                                                                                        |
| Public website       | vsyst.in "Our Policies" carries a Privacy Policy, the Terms and Conditions, a refund policy and governing law, all in the company's name and undated. The Privacy Policy is a generic template: no location, retention, third parties or transfers abroad. vsyst.in/terms answers 404. The older policy at dzzlo-oms.web.app is dated 2021-02-11 and issued by an individual; the vault records it as the one both store listings link to.  | Sources                                                                                                                                                                                                                                                                                     |
| Vault                | Easebuzz onboarding: 05 (policy table — terms "accepted at sign-up (to be added)", app "Settings → Policies (to be added)"); 07 (the T&C — cl. 12 data and privacy, cl. 16 liability cap, cl. 19 "Continued use after the change is acceptance", cl. 20 Raipur courts, cl. 21 grievance officer, 48 h acknowledgement); 08 (governing law, naming the DPDP Act); onboarding-plan (the 2021 policy must be re-issued in the company's name). | [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/05-mandatory-policies\|05]] · [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/07-terms-and-conditions\|07]] · [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/08-governing-law-dispute-resolution\|08]] |

**Bottom line:** the published T&C rely on "By registering on or using DZZLO OMS … you accept them" (cl. 1), but no screen shows them, and nothing records who accepted what, or when.

## 2. What the law says — the sentences this plan relies on

Act = DPDP Act 2023; Rules = DPDP Rules 2025, G.S.R. 846(E) of 13 Nov 2025. Both read in full for the parts below, from the MeitY PDFs.

| Ref                              | The text (quoted)                                                                                                                                                                                                                                                                                                                                                                                      | So                                                                                                               |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| s.2(i) · s.2(k)                  | Data Fiduciary: "determines the purpose and means of processing of personal data" · Data Processor: "processes personal data on behalf of a Data Fiduciary"                                                                                                                                                                                                                                            | dealer · VSYST                                                                                                   |
| s.4(1) · s.7(i)                  | processing only "for which the Data Principal has given her consent; or (b) for certain legitimate uses" · "for the purposes of employment or those related to safeguarding the employer from loss or liability"                                                                                                                                                                                       | attendance can rest on s.7(i) — D‑4                                                                              |
| s.5(1)                           | "Every request made to a Data Principal under section 6 for consent shall be accompanied or preceded by a notice"                                                                                                                                                                                                                                                                                      | the DPDP notice is tied to consent; the stores still require one (below)                                         |
| s.8(1)                           | the Fiduciary is responsible "irrespective of any agreement to the contrary … in respect of any processing undertaken by it or on its behalf by a Data Processor"                                                                                                                                                                                                                                      | the dealer stays liable, so it needs a strong clause                                                             |
| s.8(2)                           | "may engage … a Data Processor to process personal data on its behalf for any activity related to offering of goods or services to Data Principals only under a valid contract"                                                                                                                                                                                                                        | the DPA ([[04-platform-stores-and-law]] Unknown 2: the wording fits customers better than staff)                 |
| s.8(3)                           | data "likely to be— (a) used to make a decision that affects the Data Principal" — the Fiduciary "shall ensure its completeness, accuracy and consistency"                                                                                                                                                                                                                                             | attendance feeds pay                                                                                             |
| s.8(5) · s.8(6)                  | "reasonable security safeguards to prevent personal data breach", including processing by a Data Processor · "give the Board and each affected Data Principal, intimation of such breach"                                                                                                                                                                                                              | DPA cl. 6, 7                                                                                                     |
| s.8(7)                           | erase "unless retention is necessary for compliance with any law"; "(b) cause its Data Processor to erase any personal data that was made available"                                                                                                                                                                                                                                                   | DPA cl. 9                                                                                                        |
| s.8(9) · s.8(10)                 | publish the "business contact information of … a person who is able to answer" · "an effective mechanism to redress the grievances"                                                                                                                                                                                                                                                                    | the dealer's staff contact                                                                                       |
| s.9(1)                           | "before processing any personal data of a child … obtain verifiable consent of the parent" (child = under 18, s.2(f))                                                                                                                                                                                                                                                                                  | roster 18+                                                                                                       |
| s.11(1) · s.12(1)                | access: against the Fiduciary "to whom she has previously given consent, including consent as referred to in clause (a) of section 7" · correction and erasure: of data "for the processing of which she has previously given consent, including consent as referred to in clause (a) of section 7"                                                                                                    | whether staff under s.7(i) have them is for the lawyer                                                           |
| s.13(3) · s.14(1)                | "exhaust the opportunity of redressing her grievance … before approaching the Board" · "the right to nominate"                                                                                                                                                                                                                                                                                         | the notice says: employer first                                                                                  |
| s.16(1)                          | "may, by notification, restrict the transfer of personal data … to such country or territory outside India as may be so notified"                                                                                                                                                                                                                                                                      | a negative list                                                                                                  |
| Schedule                         | up to ₹250 crore for s.8(5); up to ₹200 crore for s.8(6)                                                                                                                                                                                                                                                                                                                                               | falls on the dealer — D‑7                                                                                        |
| r.1(4) · G.S.R. 843(E)           | "Rules 3, 5 to 16, 22 and 23 shall come into force eighteen months after the date of publication" · the Act's ss.3–17 (s.6(9) a year earlier, 13 Nov 2026) and s.44(2) from the same date                                                                                                                                                                                                              | **13 May 2027**                                                                                                  |
| r.3                              | the notice must be "understandable independently", give "an itemised description of such personal data" and the purpose, and a link to withdraw consent, exercise rights and "make a complaint to the Board"                                                                                                                                                                                           | the staff notice's shape                                                                                         |
| r.6(1)                           | (a) encryption · (b) access control · (c) "logs, monitoring and review" · (d) backups · (e) logs and personal data kept "for a period of one year" · (f) "appropriate provision in the contract … between such Data Fiduciary and such a Data Processor" · (g) organisational measures                                                                                                                 | DPA cl. 6                                                                                                        |
| r.7(1) · r.7(2)                  | each affected person "without delay"; the Board a description "without delay", then a detailed report "within seventy-two hours of becoming aware of the breach"                                                                                                                                                                                                                                       | DPA cl. 7: VSYST tells the dealer within 24 h                                                                    |
| r.8(3)                           | keep "personal data, associated traffic data and other logs of the processing for a minimum period of one year from the date of such processing". Its illustration (Case 2) names a cloud provider acting as Data Processor: it "also retains the data and associated logs for at least one year"                                                                                                      | DPA cl. 9. The Third Schedule's erasure periods cover only large e-commerce, gaming and social-media fiduciaries |
| r.9 · r.14(1) · r.14(3)          | "prominently publish on its website or app … the business contact information" · publish how to exercise rights · grievances answered "within a reasonable period not exceeding ninety days"                                                                                                                                                                                                           | DPA cl. 8; privacy policy                                                                                        |
| r.15                             | transfers abroad subject to "such requirements as the Central Government may, by general or special order, specify" for foreign States                                                                                                                                                                                                                                                                 | DPA cl. 11                                                                                                       |
| CERT-In, 28 Apr 2022, (ii), (iv) | report cyber incidents "within 6 hours of noticing such incidents" · logs "for a rolling period of 180 days … within the Indian jurisdiction" (FAQ Q35 allows logs abroad if they can be produced — [[vsyst-technologies/docs/tasks/tasks_14_du_slips/05-phase-5-store-compliance\|tasks_14 · 05]] §4.3)                                                                                               | VSYST's own duty, separate from the DPA                                                                          |
| Google Play, User Data           | the disclosure "Must be within the app itself"; "Cannot be included with other disclosures unrelated to personal and sensitive user data collection"; consent "Must require affirmative user action (for example, tap to accept, tick a check-box)"; "Must not interpret navigation away from the disclosure … as consent"; permission requests "must be immediately preceded by an in-app disclosure" | the staff notice is its own screen, just before the OS location prompt                                           |
| Apple 5.1.1(i) · 5.1.5           | a privacy-policy link "within the app in an easily accessible manner" · "notify and obtain consent before collecting, transmitting, or using location data"                                                                                                                                                                                                                                            | Settings → Policies; the staff notice                                                                            |

## 3. What changes

### 3.1 Three versioned documents

| Key            | What                                                                                                                                          | Who accepts                           |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| `dealer-terms` | the T&C now on vsyst.in, re-dated. Cl. 12 points to the DPA. Cl. 19 changes so that material DPA changes need express acceptance.             | the dealer, by its owner              |
| `dealer-dpa`   | the Data Processing Addendum (§5 A): Schedule 1 Part A covers the core service, Part B covers Attendance (Part B applies only while it is on) | the dealer, by its owner              |
| `staff-notice` | the staff notice (§5 C), in English and Hindi                                                                                                 | each staff member, before phone setup |

- **Storage.** Each version is a Markdown file in the API repo, listed in a manifest: key, version, language, effective date, SHA-256. A test pins the hash of every published file, so a version can be added but never edited.
- **The website.** vsyst.in publishes the same files (D‑10, D‑11).
- **What is accepted.** The SHA-256 of the exact bytes served is what an acceptance refers to.

### 3.2 API (`dzzlo_oms_api`, v4 only — v3 stays untouched)

| Piece         | Plan                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Module        | `api_v4/routes/terms.js` → `{ path: "/terms", roles: ["dealer"], router }`, added to `routeModules` (`api:api_v4/index.js:26-31`), behind the existing chain (`:72-79`). The module shape is the house one (`api:api_v4/routes/app.js:12-16`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Routes        | `GET /terms/current` (any dealer scope): the current documents, with text, summary lines, hash and public URL, plus this dealer's status. · `POST /terms/accept` (**DPrimary only**). · `POST /terms/withdraw` (DPrimary — "Turn off attendance"). · `GET /terms/history` (DPrimary, DAdmin; cursor paging like the rest of v4).                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| Owner guard   | reads the membership row for `tenantOf(req).co_id`, as the attendance managers' guard does ([[01-api]]) — never the top-level `user.scope`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Accept        | Body: `{ docs: [{ key, version, sha256 }], screen, authority: true, channel }`. Each doc must be the current version with a matching hash; otherwise `TERMS_VERSION_STALE` (409). One record is written per doc. A repeat returns the stored record. A confirmation email goes to the owner and to `dealer_email`, with the version, time, hash and a link — through the existing SES helper (`api:helpers/sendEmail.js:2`).                                                                                                                                                                                                                                                                                                                                                         |
| Record        | a new collection, `terms_acceptances`, append-only, with no update or delete route. Fields: `dealer_id` + dealer-name and GSTIN snapshots · `user_id` + name snapshot · `scope` (from the membership row) · `event` (`ACCEPT`, `WITHDRAW`, `NOTIFIED`) · `doc_key`, `version`, `sha256` · `screen` (version of the summary and checkbox wording) · `authority_declared` · `channel` (`web`, `app-signup`, `offline`) · `ip` (`req.ip` — the API trusts one proxy, `api:dzzlo_oms.js:57`) · `user_agent` · `app_version` + `device_brand` from the app's existing `meta` header (`api:helpers/middlewares.js:112-118`; self-reported) · `language` · `at` (server time). Index `{dealer_id, doc_key, at: -1}`. Kept for the life of the account plus **[LAWYER: limitation period]**. |
| Audit         | each ACCEPT or WITHDRAW is also written to `attendance_audit` ([[01-api]]), so it shows on the dealer's Audit page. VSYST reads acceptance status through dip-web's DB-Actions page, as [[01-api]] does for `attendance_config` — no new page in v1.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Staff notice  | `/screens/attendance` returns the current notice (en + hi), with the dealer's name and staff contact filled in. The enrol command stores `notice_version`, `language` and `agreed_at` on the device record and writes an audit row. An outdated version gets `NOTICE_OUTDATED` (409).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Staff contact | a per-dealer attendance setting: name or role, plus phone or email. It is required before attendance can be on (s.8(9), r.9). [[01-api]] places it beside the site settings.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Errors        | `TERMS_NOT_ACCEPTED` (403), `TERMS_VERSION_STALE` (409), `NOTICE_OUTDATED` (409) join the frozen v4 catalogue — a listed change, like [[01-api]]'s own codes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Tests         | the route table (roles; the owner guard on accept and withdraw); a stale version or a wrong hash → 409; DAdmin → 403; a repeat accept → the same record; the gate on every collection route (§3.5) before acceptance, after a withdrawal and below the floor; read and export still open; no update or delete path on `terms_acceptances`; published hashes pinned                                                                                                                                                                                                                                                                                                                                                                                                                   |

### 3.3 dzzlo_ro_web

| Piece              | Plan                                                                                                                                                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/terms`           | a new `DEALER_ROUTES` entry (`web:src/App.js:100`). It shows the current documents (from `GET /terms/current`), this dealer's status and the history. The owner sees **Accept**. An admin sees "Only the owner of `<dealer>` can accept these terms. Ask `<owner name>` to sign in and accept."   |
| Attendance section | Until accepted, [[03-web]]'s Attendance section shows one tile: **Turn on attendance**. It opens a wizard: (1) the acceptance screen (§5 B), (2) the staff contact, (3) the outlet location (`/att_outlet`). The other `/att_*` pages send the user to the wizard until all three steps are done. |
| Banner             | a Dashboard banner for the owner when a new version needs acceptance, with its date                                                                                                                                                                                                               |
| Links              | Dealer Terms, DPA and Privacy Policy, in the footer and on the Profile page                                                                                                                                                                                                                       |
| Calls              | [[03-web]]'s v4 base: absolute URLs, `x-co-id`, the v4 key                                                                                                                                                                                                                                        |
| Tests              | the box starts unticked; Accept stays disabled until it is ticked; an admin has no Accept; the wizard runs in order; the Attendance section is hidden for other scopes; 320 px and desktop                                                                                                        |

### 3.4 App

| Piece               | Plan                                                                                                                                                                                                                                                                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Dealer sign-up      | `Dealer.js` gets the summary line, the three links and an unticked checkbox (§5 B), and SIGN UP stays disabled until it is ticked. Once `auth_signup` returns its token, the app calls `POST /api/v4/terms/accept` with the version and hash it displayed (channel `app-signup`). If that call fails, it retries at the next launch. `registerrx` does not change. |
| Settings → Policies | a new row in Settings (`app:src/screens/Common/Settings/index.js:139-160`), as Easebuzz 05 planned. It holds the Privacy Policy for everyone, the Dealer Terms and DPA for dealer users, and the staff notice for roster members. It meets Apple 5.1.1(i).                                                                                                         |
| Staff notice        | [[02-app]] §5's disclosure screen shows the API's text (§5 C), with an English / हिंदी toggle and **Agree and continue** / **Not now**. Back counts as Not now. This **changes [[02-app]] §5**, which keeps the text in the strings tables (D‑12).                                                                                                                 |
| Gate messages       | `TERMS_NOT_ACCEPTED` → "Attendance isn't switched on at `<dealer>` yet." · `NOTICE_OUTDATED` → the notice opens again.                                                                                                                                                                                                                                             |
| Builds up to 1.79   | They still sign up without the box. Those dealers accept on the web before attendance can start — the gate is on the server.                                                                                                                                                                                                                                       |
| Tests               | the box starts unticked; SIGN UP is disabled until ticked; the accept call follows sign-up and is retried; on the notice, Back is not agreement; the enrol request carries `notice_version`; strings exist in en + hi                                                                                                                                              |

### 3.5 The gate — attendance stays off until accepted

A dealer's attendance is **on** only when all of these hold:

1. the dealer is on the v1 list of enabled dealers (`attendance_config`, C‑22);
2. its latest `dealer-dpa` event is an ACCEPT of a version at or above `attendance_config.dpa_floor` (a new setting);
3. its staff contact is set.

The gate splits the attendance routes in two:

- **Collection routes** require all three. These are: add to roster, enrolment code, enrol, challenge, punch, manual request, approve device.
- **Read and export routes** (today, register, export, audit) need only a past ACCEPT, so a dealer can reach its own records even while collection is paused. After a WITHDRAW they stay open for the export window, and after that only for records the dealer asked VSYST to keep (DPA cl. 9.4, 9.5).

The gate reads one indexed record per request, with no cache, because the API runs on several servers.

| State                                | Staff (app)                                   | Dealer (web)                                             |
| ------------------------------------ | --------------------------------------------- | -------------------------------------------------------- |
| not enabled (C‑22)                   | no Attendance entry                           | no Attendance section                                    |
| enabled, not accepted                | no entry (nobody is on a roster yet)          | one tile: Turn on attendance                             |
| accepted, contact or outlet missing  | "not switched on yet"                         | wizard steps 2–3                                         |
| on                                   | normal                                        | normal                                                   |
| new version published (grace period) | normal                                        | banner: "Accept by `<date>`"                             |
| floor raised, not re-accepted        | "Attendance is paused — ask your employer"    | register and export readable; Accept to resume           |
| turned off (WITHDRAW)                | "Attendance is switched off by your employer" | read and export for **[LAWYER: 30]** days; Turn on again |

## 4. How the terms are shown and accepted

### 4.1 Who accepts — recommendation: **DPrimary only** (D‑1)

- **Authority.** The owner registered the business; `registerrx` makes that person DPrimary (`api:api_v3/services/auth.js:144`). A DAdmin is often an employee, and taking on the employer's side of a data-processing contract is an owner's decision.
- **Accountability.** One accountable person, and one clean record.
- **Scope of an acceptance.** It is per dealer (per `co_id`). An owner of several dealers accepts for each one, and the screen names the dealer and its GSTIN.
- **Admins** see the status and the history, but cannot accept.
- **Fallback.** A dealer whose owner never uses DZZLO can sign a paper copy. VSYST then records it with channel `offline` and a reference (D‑1).

### 4.2 (a) Existing dealers, after the release

1. **The API ships first,** with DPA v1 published and `dpa_floor` = v1. No dealer has accepted yet, so attendance is off everywhere — off by default.
2. **The owner opens the Dashboard** and sees **Turn on attendance**.
3. **Step 1, the acceptance screen** (§5 B). Accepting writes the record and emails a copy.
4. **Step 2, the staff contact.** Name or role, plus phone or email; staff see it in the app.
5. **Step 3, the outlet location.** Attendance is now on, and the roster and the other pages unlock.
6. **Dealers who don't want attendance** are not forced to accept in v1. Whether every dealer must accept by a date before 13 May 2027 is D‑3.

### 4.3 (b) New dealers, at sign-up

- **In the app,** the sign-up form shows the unticked box under the fields (§5 B), and SIGN UP is disabled until it is ticked.
- **Right after `registerrx`,** the app records the acceptance through v4.
- **Later,** once VSYST enables the dealer (C‑22), "Turn on attendance" skips step 1 while the accepted version is still at or above the floor. It shows "Accepted on `<date>` by `<name>`" instead.
- **A web sign-up,** if one is ever built, uses the same box.

### 4.4 (c) A new version, later

- **Material change** — new data, a new purpose, less protection, or a legal need:
  1. VSYST publishes vN+1 with an effective date at least **[LAWYER: 30]** days ahead.
  2. It emails the owner and shows the banner. Each notice is logged as a `NOTIFIED` event.
  3. vN keeps governing, and anything that needs vN+1 stays off for that dealer.
  4. When the grace period ends, `dpa_floor` is raised. Collection then pauses for dealers who have not re-accepted; reading and export stay available.
  5. After a further **[LAWYER]** period, VSYST may end Attendance for that dealer, with notice — then 4.5 applies.
- **Other changes** — contacts, a sub-processor under DPA cl. 10, a clarification: notice only, effective after **[LAWYER: 30]** days, logged as `NOTIFIED`.

### 4.5 (d) A dealer who refuses or withdraws

- **Refuses.** Attendance stays off and nothing is collected. The rest of DZZLO carries on as today. A new dealer cannot sign up without ticking the box — ordinary clickwrap.
- **Withdraws** — the owner taps **Turn off attendance**, recorded as `WITHDRAW`:
  - collection stops at once and phones are revoked;
  - staff see "switched off by your employer";
  - the dealer can read and export its records for **[LAWYER: 30]** days.
- **What happens to stored data:**
  - Records are kept at least one year from each record's date (r.8(3)), or longer if the dealer instructs it under a labour law (D‑6).
  - Access to them is restricted. Raw coordinates are reduced on the C‑8 schedule.
  - At the end, records are soft-deleted, then purged — [[vsyst-technologies/docs/tasks/tasks_14_du_slips/05-phase-5-store-compliance|tasks_14 · 05]] §4.2's pattern.
  - VSYST confirms erasure on request.
- **Turning on again** needs a fresh ACCEPT of the current version.
- **When the dealer deletes its company,** the same rules apply.

### 4.6 Where the full text lives; what the acceptance screen shows

- **Canonical copy.** The API's document files. Their hash is what was accepted.
- **Public.** One vsyst.in page per document, with an archive of every version (D‑11).
- **In the product.** dzzlo_ro_web `/terms` and the app's Settings → Policies render the API's copy and link to the public page. Each acceptance also emails a copy.
- **The screen** (§5 B):
  - the business being accepted for, and who is signed in;
  - a summary of 5–7 lines;
  - links to each full document — this exact version;
  - **one unticked checkbox** that names both documents and confirms authority;
  - **Accept and turn on Attendance**, disabled until the box is ticked, plus **Not now**.
- **What does not count as acceptance:** no pre-ticked box, no acceptance by scrolling, closing or simply using the product. The record captures the screen version as well as the documents.

### 4.7 The staff side

1. **A roster member** opens Attendance → **Set up this phone**.
2. **The staff notice** (§5 C) appears on its own screen, on the dealer's behalf, with the dealer's name and staff contact. Play forbids bundling it with other disclosures, and the notice must come before the permission prompt.
3. **The tap on Agree and continue** is the affirmative action Play and Apple 5.1.5 ask for. Back or Not now is not agreement, and nothing is read.
4. **Only then** does the OS location prompt appear, followed by the code and key steps ([[02-app]] §3).
5. **The enrol request** carries the notice version and language. The server refuses an outdated version and records the agreement in the audit log.
6. **A material change to the notice** shows it again before the next check-in.
7. **Location turned off later** in the OS settings means check-in cannot work. The staff member uses a manual request instead — Apple 5.1.1(iv) and 5.1.2(i) ([[04-platform-stores-and-law]] §7.2).
8. **Prerequisite:** OneSignal's location sharing is off before launch ([[04-platform-stores-and-law]] §7.1, Unknown 6). Otherwise the notice's "never in the background" is not guaranteed.

## 5. Draft text — DRAFT FOR LEGAL REVIEW

Placeholders: `<…>` = a value filled from DZZLO or by VSYST · **[LAWYER: …]** = a decision for the lawyer · section references in brackets.

**Before any dealer accepts,** every safeguard promised in DPA clause 6 must already be true. The older-route fixes (C‑28, P0b in [[00-overview]]) therefore come first.

> [!warning] A — Data Processing Addendum · DRAFT FOR LEGAL REVIEW — not legal advice
>
> **DZZLO Data Processing Addendum** — version `<v1>` — effective `<date>`
>
> **1. Parties and roles**
>
> **1.1** This Addendum is between **VSYST Technologies Private Limited** ("VSYST") and the dealer business that accepts it in DZZLO (the "Dealer"). It forms part of the DZZLO Terms and Conditions (the "Terms"). Where the two differ about personal data, this Addendum applies.
>
> **1.2** For the processing in Schedule 1, the Dealer is the **Data Fiduciary**: it decides the purpose and means of the processing [s.2(i)]. VSYST is the **Data Processor**: it processes that personal data on the Dealer's behalf [s.2(k)].
>
> **1.3** This Addendum is the valid contract under which the Dealer engages VSYST [s.8(2)]. The Dealer remains responsible under the Act for processing done on its behalf [s.8(1)]. VSYST is responsible to the Dealer for doing what this Addendum says.
>
> **1.4** "Act" means the Digital Personal Data Protection Act, 2023, and "Rules" the Digital Personal Data Protection Rules, 2025. Words defined there mean the same here. "Dealer Personal Data" is the personal data in Schedule 1. "Staff" are the people the Dealer puts on its attendance roster.
>
> **2. Subject matter, purpose and duration**
>
> **2.1** VSYST processes Dealer Personal Data only to provide, secure and support DZZLO for the Dealer, as described in Schedule 1.
>
> **2.2** For Attendance, the only purpose is to record when Staff start and finish work at the Dealer's outlet, and to check that each check-in was made at the outlet, at that moment, from the Staff member's own approved phone (the "Attendance Purpose").
>
> **2.3** VSYST will not use Dealer Personal Data for its own purposes. It will not sell it, use it for advertising or profiling, or use location data for anything other than the Attendance Purpose.
>
> **2.4** **[LAWYER: keep or delete]** VSYST may make statistics that identify no person and no dealer — for example, how often check-ins fail because of weak GPS — to run and improve DZZLO.
>
> **2.5** This Addendum lasts while VSYST holds Dealer Personal Data (clause 14).
>
> **3. What the Dealer does**
>
> **3.1** The Dealer confirms it has a lawful ground to process Staff personal data for the Attendance Purpose — use for the purposes of employment [s.4(1)(b), s.7(i)] **[LAWYER: or consent, s.6]**.
>
> **3.2** The Dealer puts on the roster only its own staff aged 18 or over [s.9].
>
> **3.3** The Dealer instructs VSYST to show each Staff member the notice in Schedule 3, in the DZZLO app and on the Dealer's behalf, before their phone is set up. The Dealer also tells its Staff about attendance in its own workplace rules.
>
> **3.4** The Dealer gives, in DZZLO, the business contact of a person who answers Staff questions about their data [s.8(9), r.9], and runs a way for Staff to raise grievances [s.8(10), s.13]. VSYST shows this contact to Staff in the app.
>
> **3.5** Attendance records may be used to decide matters such as pay. The Dealer keeps its roster, outlet location and decisions accurate and complete [s.8(3)], approves each phone in person, and decides manual requests fairly.
>
> **3.6** The Dealer controls who in its business can see attendance data, keeps its log-ins secret, and protects any register it downloads from DZZLO.
>
> **4. Processing only on the Dealer's instructions**
>
> **4.1** VSYST processes Dealer Personal Data only on the Dealer's documented instructions. These are this Addendum, the Terms, the settings the Dealer chooses in DZZLO (roster, outlet location and radius, approvals, decisions), and written instructions from the Dealer's owner to VSYST support.
>
> **4.2** If VSYST believes an instruction breaks the Act or another law, it will tell the Dealer and need not follow it.
>
> **4.3** If a law or a lawful order requires VSYST to process or disclose Dealer Personal Data in another way [for example r.23], VSYST will tell the Dealer first, unless the law forbids it [r.23(2)].
>
> **5. VSYST's people**
>
> **5.1** Only VSYST employees and contractors who need access to run or support DZZLO may access Dealer Personal Data. Each is bound by a written duty of confidentiality, is trained in handling personal data, and loses access when the need ends.
>
> **5.2** VSYST support opens a Dealer's attendance data only to fix a problem the Dealer reported or to keep the service secure. Each such access is logged.
>
> **6. Security safeguards [s.8(5), r.6]**
>
> VSYST takes reasonable security safeguards to prevent a personal data breach, including at least:
>
> **(a) Encryption [r.6(1)(a)]** — data travels encrypted (HTTPS) between the app, the website and VSYST's servers. Stored data is encrypted by the hosting providers **[to be confirmed]**. Attendance enrolment codes are stored only as hashes. The phone's signing key never leaves the phone; VSYST holds only the public key.
>
> **(b) Access control [r.6(1)(b)]** — only the Dealer's owner and admins see the Dealer's attendance data, and a Staff member sees only their own records. VSYST access is personal, limited and reviewed.
>
> **(c) Logs and monitoring [r.6(1)(c)]** — an append-only log of attendance actions (who approved a phone, decided a request, changed the outlet). Security logs are watched for unauthorised access. Precise locations are kept out of general request logs.
>
> **(d) Continuity [r.6(1)(d)]** — regular backups, and a tested way to restore them.
>
> **(e) Log retention [r.6(1)(e)]** — logs and personal data are kept for one year, to detect, investigate and fix unauthorised access (clause 9).
>
> **(f) Contracts [r.6(1)(f)]** — this clause, and the same duties in VSYST's contracts with its sub-processors (clause 10).
>
> **(g) Organisation [r.6(1)(g)]** — a person responsible for security; staff training; an incident response plan; code review and tests before each release; prompt fixing of vulnerabilities; checks by Google Play Integrity and Apple App Attest that the app (and, on Android, the phone) is genuine.
>
> VSYST may change these measures but will not lower the overall protection.
>
> **7. Personal data breach [s.8(6), r.7]**
>
> **7.1** VSYST will tell the Dealer about a personal data breach affecting Dealer Personal Data without delay, and in any case within **[LAWYER: 24]** hours of becoming aware of it. The Dealer must give the Data Protection Board a detailed report within 72 hours of becoming aware [r.7(2)(b)].
>
> **7.2** VSYST will give what it knows and update it as it learns more: the nature, extent, timing and location of the breach and its likely impact; the events and reasons that led to it; the measures taken or proposed to reduce the risk; any findings about who caused it; the steps to stop it happening again; and which Staff are affected [r.7(1), r.7(2)].
>
> **7.3** VSYST will help the Dealer prepare its intimation to the Board and to each affected Staff member. On the Dealer's written instruction, VSYST will send the Staff intimation in the Dealer's name, through the Staff member's DZZLO account and registered email or phone [r.7(1)].
>
> **7.4** VSYST will not report a breach of Dealer Personal Data to the Board or to Staff in the Dealer's name without the Dealer's instruction. This does not stop VSYST from meeting its own legal duties, such as reporting cyber incidents to CERT-In.
>
> **7.5** VSYST will contain and investigate each breach, keep a record of it, and share that record with the Dealer. Telling the Dealer is not an admission of fault.
>
> **8. Staff rights and grievances [s.11–s.14, r.14]**
>
> **8.1** VSYST will help the Dealer answer Staff who ask for a summary of their data [s.11]; for its correction, completion, updating or erasure [s.12]; for redress of a grievance [s.13]; or to nominate someone [s.14] — to the extent the Act gives that right for this processing **[LAWYER: ss.11–12 are framed around consent and s.7(a); confirm the position for s.7(i)]**.
>
> **8.2** The Dealer can see and export each Staff member's attendance records in DZZLO. A correction is made as a new, dated and logged entry, never by silently changing a recorded check-in.
>
> **8.3** If a Staff member contacts VSYST about attendance data, VSYST will pass the request to the Dealer within **[LAWYER: 3]** working days and tell the person that their employer will answer. VSYST will not answer it itself unless the Dealer asks.
>
> **8.4** VSYST will give the Dealer the help it needs within **[LAWYER: 7]** working days, so the Dealer can answer within the period it publishes, which may not exceed 90 days [r.14(3)].
>
> **9. Retention and erasure [s.8(7), r.6(1)(e), r.8(3)]**
>
> **9.1** VSYST keeps attendance records while the Dealer uses Attendance, subject to this clause.
>
> **9.2** The exact GPS reading of each check-in is kept for **[C‑8: one year]**. It is then reduced to the distance from the outlet and the result.
>
> **9.3** VSYST keeps personal data, the related traffic data and the logs of processing for at least one year from the date of processing [r.8(3)], even if erasure is asked for earlier, unless a law requires otherwise. During that year the data is used only for the purposes the Rules allow [r.6(1)(e), Seventh Schedule], and access to it is restricted.
>
> **9.4** If the Dealer must keep attendance registers longer under another law, it tells VSYST in writing, and VSYST keeps them for that period **[LAWYER: which laws, how long]**.
>
> **9.5** When Attendance is turned off, or this Addendum ends, VSYST stops collecting at once. The Dealer can read and export its records for **[LAWYER: 30]** days. VSYST then erases Dealer Personal Data or makes it anonymous [s.8(7)(b)], except what clauses 9.3 and 9.4 require it to keep. Records kept under 9.4 stay available to the Dealer to read and export. Records kept only under 9.3 are restricted. Each is erased when its period ends.
>
> **9.6** Erased data may remain in encrypted backups until they expire **[LAWYER and VSYST: backup cycle]**. Backups are never used to bring erased data back, except to recover from a disaster.
>
> **9.7** On request, VSYST confirms erasure in writing.
>
> **10. Sub-processors**
>
> **10.1** The Dealer allows VSYST to use the sub-processors in Schedule 2, for the purposes stated there.
>
> **10.2** VSYST uses a sub-processor only under a written contract that protects Dealer Personal Data at least as well as this Addendum, including its security safeguards [r.6(1)(f)]. VSYST remains responsible to the Dealer for its sub-processors.
>
> **10.3** VSYST will tell the Dealer at least **[LAWYER: 30]** days before a new sub-processor receives attendance data. If the Dealer objects on reasonable data-protection grounds and the parties cannot agree, the Dealer may turn off Attendance or end this Addendum without penalty.
>
> **10.4** VSYST keeps the current list at `<public URL>`.
>
> **11. Processing outside India [s.16, r.15]**
>
> **11.1** VSYST stores Dealer Personal Data in India **[to be confirmed: the database and server regions]**. Some sub-processors in Schedule 2 may process a limited part of it outside India.
>
> **11.2** VSYST will not transfer Dealer Personal Data to a country or territory the Central Government restricts under s.16(1). It will meet any requirement made under r.15 about making personal data available to a foreign State, or to an entity under its control. If such a restriction starts to apply, VSYST will stop or move that processing and tell the Dealer.
>
> **11.3** Where another Indian law protects some data more strongly, that law applies [s.16(2)].
>
> **12. Information and audit**
>
> **12.1** Once a year, or after a breach, VSYST will give the Dealer on written request the information reasonably needed to show it meets this Addendum: a description of its safeguards, the current sub-processor list, and a summary of its latest security review.
>
> **12.2** If that is not enough, or the Board or another authority requires it, the Dealer — or an independent auditor bound by confidentiality — may audit VSYST's compliance on **[LAWYER: 30]** days' written notice, at the Dealer's cost, without seeing other customers' data or VSYST's security secrets.
>
> **13. Liability and indemnity**
>
> **13.1** **[LAWYER: the cap. The Terms (cl. 16) limit liability to the fees paid in the previous 12 months, or ₹10,000. Decide whether a separate, higher cap applies to breaches of clauses 5–7 and 10.]**
>
> **13.2** **[LAWYER: indemnity. VSYST indemnifies for penalties and claims caused by its breach of this Addendum; the Dealer for those caused by its unlawful instructions or its breach of clause 3. Penalties under the Act fall on the Data Fiduciary — up to ₹250 crore for failing to take reasonable security safeguards, and up to ₹200 crore for failing to give breach intimation (the Act's Schedule).]**
>
> **13.3** Nothing here limits a liability that the law does not allow to be limited.
>
> **14. Term and termination**
>
> **14.1** This Addendum starts when the Dealer's owner accepts it in DZZLO, and lasts while VSYST holds Dealer Personal Data.
>
> **14.2** The Dealer may turn off Attendance at any time in DZZLO. That ends the Attendance part of this Addendum, and clause 9.5 applies.
>
> **14.3** Either party may end this Addendum as the Terms allow. Clauses 5, 7, 9, 12 and 13 continue while VSYST holds Dealer Personal Data.
>
> **15. Changes**
>
> **15.1** VSYST publishes each version of this Addendum with a version number and a date.
>
> **15.2** A change that adds a new kind of personal data or a new purpose, lowers the Dealer's protection, or needs the Dealer's agreement by law applies to a Dealer only after the Dealer's owner accepts it in DZZLO. Until then the earlier version continues, and anything that needs the change stays off for that Dealer **[LAWYER: what follows if it is not accepted within a set time]**.
>
> **15.3** Other changes — contact details, a sub-processor change under clause 10, a clarification — apply **[LAWYER: 30]** days after VSYST tells the Dealer.
>
> **16. Law and disputes**
>
> **16.1** This Addendum is governed by the laws of India. The courts at Raipur, Chhattisgarh have exclusive jurisdiction, as in the Terms.
>
> **16.2** Please write first to VSYST's grievance officer at `<grievance email>`. VSYST acknowledges within 48 hours.
>
> **17. Notices and acceptance**
>
> **17.1** Notices to the Dealer go to its owner's registered email and appear in DZZLO. Notices to VSYST go to `<privacy email>`.
>
> **17.2** The Dealer's owner accepts this Addendum electronically in DZZLO and confirms they are authorised to do so. VSYST records who accepted, when, from where, and the exact version **[LAWYER: confirm that electronic acceptance is enough]**.
>
> **Schedule 1 — what is processed**
>
> **Part A — the DZZLO core service** **[LAWYER: confirm VSYST's role, D‑9]**. Personal data of the Dealer's users, and of people the Dealer records in DZZLO (such as customers' contact persons), processed to run orders, invoices, payments, ledgers and reports for the Dealer. Account sign-in, security and support data are VSYST's own, under its Privacy Policy.
>
> **Part B — Attendance** (applies only while Attendance is on):
>
> | Item                 | Detail                                                                                                                                                                                                                           |
> | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | Data Principals      | Staff on the Dealer's attendance roster — existing DZZLO users of the Dealer, aged 18 or over                                                                                                                                    |
> | Identity and contact | name, mobile number and email from the DZZLO account; roster status                                                                                                                                                              |
> | The phone            | a public key made on the phone; make, model, system and app versions; how the key is unlocked (fingerprint, face or PIN — the kind only); the results of Google Play Integrity or Apple App Attest; the phone's approval history |
> | Location             | one GPS reading at each check-in or check-out — latitude, longitude, accuracy and the reading's age — and whether the phone marked it as simulated; the distance from the outlet                                                 |
> | Time                 | the server's time of each attempt; the IST date                                                                                                                                                                                  |
> | Records              | each attempt and its result (accepted, or the reason it was refused); manual requests and decisions; the monthly register; the audit log; the notice version each Staff member agreed to                                         |
> | Not collected        | fingerprints, face images or any other biometric data (the phone checks them itself); location at any other moment; contacts, photos, messages                                                                                   |
> | Operations           | collect, record, verify, compare with the outlet, store, show, export (CSV) for the Dealer, erase                                                                                                                                |
> | Who sees it          | the Dealer's owner and admins; each Staff member (own records only); VSYST support (clause 5)                                                                                                                                    |
> | How long             | clause 9                                                                                                                                                                                                                         |
>
> **Schedule 2 — sub-processors** (as of `<date>`; every row to be confirmed)
>
> | Category           | Provider                                              | Purpose                                        | Data                                                 | Where                                            |
> | ------------------ | ----------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------ |
> | Cloud hosting      | Amazon Web Services                                   | DZZLO's servers and file storage               | all service data                                     | files in India (Mumbai); servers to be confirmed |
> | Database hosting   | MongoDB Atlas                                         | the database                                   | all service data                                     | to be confirmed                                  |
> | Email              | Amazon SES                                            | sign-in codes, notices, acceptance copies      | name, email, message                                 | to be confirmed                                  |
> | SMS                | 2Factor.in                                            | one-time passwords by SMS                      | mobile number, code                                  | India                                            |
> | Push notifications | OneSignal                                             | "phone waiting for approval", "phone approved" | DZZLO user id, push token, message                   | likely outside India                             |
> | App stability      | Google Firebase (Crashlytics, Analytics, Performance) | crash reports and app performance              | DZZLO user id, device data, app events — never GPS   | likely outside India                             |
> | Android integrity  | Google Play Integrity API                             | is the app and phone genuine                   | a token carrying a hash of the request — no location | likely outside India                             |
> | iPhone integrity   | Apple App Attest                                      | is the app genuine                             | key attestation — no location                        | likely outside India                             |
>
> **[LAWYER: whether Play Integrity and App Attest are sub-processors or platform services.]**
>
> **Schedule 3 — the staff notice:** the text in C below.

> [!warning] B — The acceptance screen · DRAFT FOR LEGAL REVIEW — not legal advice
>
> **Title:** Turn on Attendance — accept the dealer terms
>
> **Accepting for:** `<dealer name>` · GSTIN `<gstin>` · signed in as `<name>` (Owner)
>
> **Summary** (version `<v>`, effective `<date>`):
>
> 1. Your business decides why staff attendance is recorded. Under India's DPDP Act you are the Data Fiduciary, and VSYST is your Data Processor.
> 2. Staff check in with the DZZLO app. Each check-in records the time, one GPS reading taken at that moment, and the phone's security checks. Nothing is tracked in the background.
> 3. VSYST uses this data only to run Attendance for you. It never sells it or uses it for advertising.
> 4. VSYST tells you about a data breach within **[LAWYER: 24]** hours, so you can report it to the Data Protection Board within 72 hours.
> 5. Records are kept for at least one year, as the DPDP Rules require, and then erased.
> 6. You name a contact for staff questions. DZZLO shows your staff a notice on your behalf before they set up a phone.
> 7. Attendance stays off until you accept. You can turn it off at any time.
>
> **Links:** Dealer Terms · Data Processing Addendum · Privacy Policy — each opens this exact version.
>
> **Checkbox (unticked):** ☐ I have read and accept the DZZLO Dealer Terms and the Data Processing Addendum (version `<v>`) for `<dealer name>`, and I am authorised to accept them for this business.
>
> **Buttons:** **Accept and turn on Attendance** (disabled until the box is ticked) · **Not now**
>
> **After accepting:** "Accepted on `<date, time IST>` by `<name>`. A copy has been emailed to `<owner email>`."
>
> **Admins:** "Only the owner of `<dealer name>` can accept these terms. Ask `<owner name>` to sign in and accept."
>
> **App sign-up (dealer), above SIGN UP:** ☐ I accept the DZZLO Dealer Terms, including the Data Processing Addendum, for this business, and I am authorised to do so. I have read the Privacy Policy. — with the three links; SIGN UP stays disabled until the box is ticked.

> [!warning] C — The staff notice (in the app, before "Set up this phone") · DRAFT FOR LEGAL REVIEW — not legal advice
>
> **Attendance at `<dealer name>` — your data**
>
> `<dealer name>` uses DZZLO to record when you start and finish work at the outlet. `<dealer name>`, your employer, is responsible for this data. VSYST Technologies Pvt. Ltd., which makes DZZLO, handles it for them.
>
> **What is recorded**
>
> - When you tap **Check in** or **Check out**: the time, and one GPS reading of where your phone is at that moment, with its accuracy.
> - Whether your phone says that location is fake.
> - Your phone: make, model, system version, app version, and a security key made on this phone. Your fingerprint or face never leaves your phone — the phone checks it and tells DZZLO only that it was confirmed.
> - A check by Google (Android) or Apple (iPhone) that the DZZLO app — and, on Android, the phone — is genuine.
> - Your check-ins, your requests, and your employer's decisions on them.
>
> **What is not recorded:** your location at any other time — there is no tracking in the background — and your contacts, photos or messages.
>
> **Why:** to keep the attendance register for `<dealer name>`, and to make sure each check-in was made at the outlet from your own approved phone.
>
> **Who sees it:** the owner and admins of `<dealer name>`. You can see your own records in the app. VSYST staff see them only to fix a problem or keep the service safe.
>
> **How long:** attendance records are kept for `<period — at least one year>`. The exact GPS reading is kept for `<C‑8 period>`; after that, only the distance from the outlet and the result are kept.
>
> **Questions and complaints:** ask `<contact name or role>` at `<contact phone or email>`. You can ask to see your records, to correct a mistake, or to make a complaint **[LAWYER: rights wording under s.7(i)]**. If your employer does not resolve your complaint, you can complain to the Data Protection Board of India.
>
> **If you do not agree:** tap **Not now**. This phone will not be set up, and no location will be read. Ask `<dealer name>` how else to record your attendance.
>
> **Consent line (above the button):** "I agree that DZZLO may read this phone's location only when I tap Check in or Check out, and send it with the phone's security checks to `<dealer name>` for attendance." **[LAWYER: a button tap, or also a checkbox]**
>
> **Agree and continue** · **Not now** · हिंदी में पढ़ें · Privacy Policy · version `<v>`

**D — Privacy-policy updates on the public website (checklist):**

- [ ] **Re-issue** the policy in VSYST Technologies Private Limited's name, versioned and dated. Retire or redirect the 2021 page at dzzlo-oms.web.app, and point both store listings at the new URL.
- [ ] **Two roles.** VSYST is the fiduciary for accounts, sign-in, security, support and analytics. It is the processor for each dealer's data, attendance included, where the dealer is the fiduciary and staff go to their employer first.
- [ ] **An attendance section:** an itemised list of the data (as in Schedule 1 Part B), when it is read (only at check-in and check-out, never in the background), why, who sees it, how long it is kept — and what is not collected (no biometrics, no background location).
- [ ] **Third parties and sub-processors,** with purpose and location (Schedule 2). Say that each protects the data as the policy does (Apple 5.1.1(i)).
- [ ] **Transfers outside India:** which services, and the s.16 / r.15 position.
- [ ] **A retention table:** attendance records (at least one year), raw coordinates (C‑8), phone keys, the audit log, request and security logs (400 days, [[vsyst-technologies/docs/tasks/tasks_18_data_archival/04-logs|tasks_18 · 04]]), accounts after Delete Account (the one-year floor), and acceptance records (the evidence of the contract).
- [ ] **A security summary** (r.6), at a high level.
- [ ] **Rights and how to use them** (r.14(1)): the means, the identifiers needed, the response period (at most 90 days, r.14(3)), nomination (s.14), the grievance step, then the Board.
- [ ] **The contact person** (s.8(9), r.9): VSYST's grievance officer at `<grievance email>`. For attendance, the employer's contact first.
- [ ] **Children:** DZZLO is not for people under 18.
- [ ] **Data breaches:** how affected people are told (r.7), in brief.
- [ ] **Changes:** versions, dates and how notice is given.
- [ ] **In the app:** a privacy link in Settings → Policies, and in App Store Connect and Play Console metadata (Apple 5.1.1(i)). Data safety and the privacy label must match the policy ([[04-platform-stores-and-law]] §7).
- [ ] **The T&C on vsyst.in:** a date and version; cl. 12 points to the DPA; cl. 19 requires express acceptance for material DPA changes; Attendance added to the service description.
- [ ] **A Hindi version** of the staff notice and of the privacy summary (the language option of s.5(3) and s.6(3)).

## 6. Open questions for the user and the lawyer

| #    | Question                                   | Options                                                   | Recommended                                                                                                               | Who          |
| ---- | ------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------ |
| D‑1  | Who accepts for the dealer                 | DPrimary only · DPrimary or DAdmin                        | **DPrimary only**, plus a signed paper copy recorded by VSYST (`offline`) for a dealer that wants one                     | user         |
| D‑2  | What one acceptance covers                 | Terms + DPA, one checkbox · two checkboxes · DPA only     | **one screen, both documents, one checkbox** naming both, with the authority statement                                    | user, lawyer |
| D‑3  | Dealers who don't use attendance           | ask only on "Turn on" · require all dealers by a date     | **only on "Turn on" in v1**; agree a date before 13 May 2027 for all dealers (Part A)                                     | user, lawyer |
| D‑4  | Basis for staff data; what "Agree" means   | s.7(i) employment · consent (s.6)                         | **s.7(i)**. The staff tap is the stores' consent to read location, not the DPDP basis — the wording must say so           | lawyer       |
| D‑5  | Breach notice, VSYST → dealer              | 12 h · 24 h · 48 h                                        | **24 h** — leaves the dealer 48 h before the Board's 72 h report                                                          | lawyer       |
| D‑6  | Retention                                  | one year · longer for labour-law registers                | at least one year (r.8(3)); longer only on the dealer's written instruction; raw coordinates per C‑8                      | lawyer, user |
| D‑7  | Liability and indemnity                    | the T&C cap · a separate data cap · an indemnity          | the lawyer's call — the ₹250 crore and ₹200 crore penalties fall on the dealer                                            | lawyer       |
| D‑8  | Sub-processor changes                      | notice only · notice + objection                          | **30 days' notice; an objection lets the dealer turn off attendance without penalty**                                     | lawyer       |
| D‑9  | VSYST's role for the core service (Part A) | processor · fiduciary · split                             | **split** — processor for the dealer's business records, fiduciary for accounts, security and support                     | lawyer       |
| D‑10 | Where the documents live                   | files in the API repo · database edited by superadmin     | **files in the API repo**, hash-pinned; the website copy generated from them                                              | user         |
| D‑11 | Public URLs                                | sections of "Our Policies" · one page per document        | **one page per document, with a version archive**; retire dzzlo-oms.web.app                                               | user         |
| D‑12 | Staff notice: text source and language     | app strings · served by the API; Hindi at launch or later | **served by the API** (changes [[02-app]] §5); **Hindi at launch** for this notice, even under 1.79's English lock (C‑10) | user         |
| D‑13 | After a material change                    | grace days; what pauses                                   | **30 days to re-accept; then new collection pauses, reading and export stay**                                             | user, lawyer |
| D‑14 | De-identified statistics (DPA 2.4)         | allow · forbid                                            | **allow**                                                                                                                 | lawyer       |
| D‑15 | Audit rights                               | information only · on-site                                | **information plus one questionnaire a year; on-site only if an authority requires it**                                   | lawyer       |
| D‑16 | Customers' acceptance of the T&C           | same mechanism · out of scope                             | **later, same mechanism**                                                                                                 | user         |

## 7. Unknowns

1. **G.S.R. 843(E)** (the Act's commencement) was read from an unofficial mirror. It matches law-firm summaries; the e-Gazette was not opened. A January 2026 proposal to shorten the timeline had not been notified, as far as the sources read show.
2. **s.16(1):** that no country is notified comes from secondary sources ([[vsyst-technologies/docs/tasks/tasks_18_data_archival/references|tasks_18 references]] L12, Aug 2026). Not re-checked.
3. **Hosting facts not in the repos:** the database and server regions, encryption at rest and the backup cycle. Known: email goes through Amazon SES (`api:helpers/sendEmail.js:2`, `api:package.json:31`); SMS OTP through 2Factor.in and hosting on EC2 behind a load balancer with MongoDB Atlas (`api:docs/runbook.md:4`); the image bucket is in `ap-south-1` (`api:api_v3/services/invoice/htmlTemplates/components.js:20`); Firebase and OneSignal are in the app (`app:package.json:35-38,54`), which sets the Firebase user id (`app:src/utils/firebase.js:45-46`).
4. **The store listings' privacy URL:** the vault (Aug 2026) says dzzlo-oms.web.app. Not checked in Play Console or App Store Connect.
5. **vsyst.in "Our Policies"** was read through a summarising fetch. Re-read the page before editing it.
6. **OneSignal 5.4.1's location sharing** ([[04-platform-stores-and-law]] Unknown 6) — it must be off before the notice ships.
7. **Where OneSignal and Firebase process data**, and whether Play Integrity and App Attest count as sub-processors.
8. **Not read:** the IT Act's rules on electronic contracts; the interim IT Act s.43A regime, which the DPDP Act's s.44(2) omits from 13 May 2027; labour-law register periods; Play's account-deletion web-link rule.
9. **Whether ss.11–12 apply** to s.7(i) processing — the text is quoted in §2; the reading is the lawyer's.

## Sources

**Law (read 2026-10-01).** C = confirmed official copy · U = unofficial mirror or summary.

- DPDP Act 2023 (MeitY) — https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf — C
- DPDP Rules 2025, G.S.R. 846(E) (MeitY, bilingual Gazette) — https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf — C; the English-only mirror matches on r.6–r.8 — https://www.dpdpa.com/DPDP_Rules_2025_English_only.pdf — U
- G.S.R. 843(E), the Act's commencement (Gazette page) — https://dpdpa.in/notification_timeline_act.pdf — U
- PIB explainer, Nov 2025 — https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/nov/doc20251117695301.pdf — C
- CERT-In Directions, 28 Apr 2022 — https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf — C
- MeitY's 12-month proposal (not notified) — https://www.mondaq.com/india/privacy-protection/1760380/compression-of-dpdp-enforcement-timeline-proposed-by-meity — U

**Stores (read 2026-10-01).**

- Google Play User Data policy — https://support.google.com/googleplay/android-developer/answer/10144311 — C
- Apple App Review Guidelines 5.1.1, 5.1.5 — https://developer.apple.com/app-store/review/guidelines/ — C

**Websites (read 2026-10-01).**

- vsyst.in "Our Policies" — https://www.vsyst.in/our-policies
- vsyst.in/terms — https://vsyst.in/terms (404)
- The 2021 privacy policy — https://dzzlo-oms.web.app

**Repos.**

- `api:` `api_v3/routes/auth/index.js:69` · `api_v3/controllers/auth/app_redux.js:28-38` · `api_v3/services/auth.js:80-168` · `models/users.js:54-130` · `models/dealer_msts.js:6-75` · `models/invites.js:12` · `models/veh_reqs.js:15` · `api_v4/index.js:26-31,72-79` · `api_v4/routes/app.js:12-16` · `dzzlo_oms.js:57` · `helpers/middlewares.js:112-118` · `helpers/sendEmail.js:2` · `package.json:31` · `docs/runbook.md:4` · `api_v3/services/invoice/htmlTemplates/components.js:20`
- `app:` `src/screens/Login/AuthNavigator/Welcome.js:117-157,242-264` · `src/screens/Login/AuthNavigator/Dealer.js:23-61,142-154,238-246` · `src/store/apis/dzzlooms/auth.js:75-95` · `src/screens/Common/Settings/index.js:139-160` · `src/screens/Common/Help/index.js:12-13` · `src/screens/Common/ContactUs/index.js:152` · `src/screens/Dealer/Customers/CustSettings.js:1493` · `src/utils/firebase.js:45-46` · `package.json:35-38,54`
- `web:` `src/pages/auth/SignIn/index.js:467-481` · `src/App.js:100,304-308` · `src/pages/auth/SignUp/index.js:8-111`

**Vault.**

- Easebuzz onboarding [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/05-mandatory-policies|05]] · [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/07-terms-and-conditions|07]] · [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/08-governing-law-dispute-resolution|08]] · [[vsyst-technologies/correspondence/IPG_Easebuzz/onboarding/onboarding-plan|onboarding-plan]]
- [[vsyst-technologies/docs/tasks/tasks_14_du_slips/05-phase-5-store-compliance|tasks_14 · 05]] §4
- [[vsyst-technologies/docs/tasks/tasks_18_data_archival/04-logs|tasks_18 · 04]]
- [[04-platform-stores-and-law]] §9
