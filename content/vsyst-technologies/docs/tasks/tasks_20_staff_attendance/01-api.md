---
title: tasks_20 · 01 — API, the attendance module in dzzlo_oms_api
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start".
---

# 01 — API: `/api/v4/attendance` in `dzzlo_oms_api`

**Summary.** The API gets a new v4 module, `/api/v4/attendance`, one route on the screens module, and seven collections on the default connection. Staff are the dealer's **existing DZZLO users** — role `dealer`, with whatever scope they hold today (C‑17). A roster record, not a role or a scope, decides who may check in. The 6 staff routes need an ACTIVE membership and an ACTIVE roster record. The 16 manager routes need a DPrimary or DAdmin membership (C‑22). A punch counts only after eight server checks: on the roster, a fresh challenge, a hardware-key signature, an integrity proof where the phone can give one, a real location, a precise and fresh fix, inside the radius, and a sensible sequence. Every phone the app supports can enrol (C‑20). Phones without Play services or App Attest are accepted with a flag (C‑29, open). No frozen file changes: `models/users.js`, `api_v4/lib/tenancy.js` and the `users` indexes stay as they are. The user approves the new server packages and their Google and Apple credentials (C‑24, [[06-package-approval-list]]).

Overview: [[00-overview]]. Siblings: [[02-app]] · [[03-web]] · [[04-platform-stores-and-law]] · [[06-package-approval-list]] · [[07-dealer-terms-and-data-processing]] · [[05-round-1-web-design]] (round 1, superseded).

## 1. Where it plugs in

| Piece          | Today (`dzzlo_oms_api` `slave` @ `86083ca`)                                                                                                                                                                                                                              | Attendance                                                                                                      |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Mount          | `dzzlo_oms.js:121` → `api_v/api4.js:7-9` → `buildV4()` (`api_v4/index.js:69-84`)                                                                                                                                                                                         | add `routes/attendance` to `routeModules` (`api_v4/index.js:26-31`)                                             |
| Chain          | `api_key_v3` (`helpers/middlewares.js:45-58`) → `protect` (`api_v3/auth.js:61-75`) → `check_user_company_status` (`helpers/middlewares.js:65-110`) → `requireRole(module.roles)` (`api_v4/lib/roles.js:26-39`) → route → `errorHandler` (`api_v4/lib/errors.js:105-134`) | unchanged; module `roles: ["dealer"]`                                                                           |
| Boot contract  | a module without `path` / `roles` / `router` stops the server (`api_v4/index.js:35-54`)                                                                                                                                                                                  | applies as is                                                                                                   |
| Tenancy        | a dealer gets `dealer_id = co_id`; `x-co-id` is honoured only for a member (`api_v4/lib/tenancy.js:42-54,64-80`)                                                                                                                                                         | **unchanged — no edit.** `dealer_id` only from `tenantOf`; a staff member's own reads add the token's `user_id` |
| Errors         | catalogue frozen (`api_v4/lib/errors.js:10-50`); success envelope `ok()` (`api_v4/lib/respond.js:18-29`)                                                                                                                                                                 | new codes (§6)                                                                                                  |
| Screens module | roles `dealer, customer`, narrowed per route (`api_v4/routes/screens.js:16-54`)                                                                                                                                                                                          | `POST /screens/attendance` narrows to `dealer` and adds the roster gate; the module's role list does not change |

## 2. Routes

How to read the table:

- Paths are under `/api/v4`. Every route is role `dealer` and sits behind the shared chain.
- **roster** = the roster gate: an ACTIVE `attendance_staff` record for this dealer and this user (§7).
- **managers** = the manager gate: DPrimary or DAdmin in this dealer (C‑22, §7).
- Every staff route also has a per-user rate limit (§9) and the minimum-build gate (C‑26 — attendance routes only).
- Lists page by cursor, like the rest of v4: the response carries `page.next` and `page.hasMore` (`api_v4/lib/cursor.js:169,212-216`), and the next request sends `cursor`.

| Method | Path                                        | Gate                      | Purpose                                                                                        |
| ------ | ------------------------------------------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| POST   | `/attendance/enrol/challenge`               | roster · 5 tries per code | check the enrolment code; issue an ENROL challenge                                             |
| POST   | `/attendance/enrol`                         | roster                    | verify the key attestation / App Attest, or record UNAVAILABLE; phone PENDING; notify managers |
| POST   | `/attendance/challenge`                     | roster                    | PUNCH challenge, 2 min, single use                                                             |
| POST   | `/attendance/punch`                         | roster                    | the eight checks; store the attempt                                                            |
| POST   | `/attendance/requests`                      | roster                    | manual request, with the last refusal code                                                     |
| POST   | `/screens/attendance`                       | roster · screens limiter  | the Attendance screen: site, phone state, today, own last 30 days                              |
| GET    | `/attendance/today`                         | managers                  | in, not in, open check-ins, flags                                                              |
| GET    | `/attendance/sites`                         | managers                  | the outlet site                                                                                |
| PUT    | `/attendance/sites`                         | managers                  | centre, radius, accuracy limit (one site in v1, C‑3)                                           |
| GET    | `/attendance/staff`                         | managers                  | the dealer's users with their roster state (cursor)                                            |
| POST   | `/attendance/staff`                         | managers                  | put an existing member (`user_id`) on the roster; enrolment code, shown once                   |
| PATCH  | `/attendance/staff/:id`                     | managers                  | deactivate or reactivate the roster record                                                     |
| POST   | `/attendance/staff/:id/enrolment-code`      | managers                  | new code; the old one is void                                                                  |
| GET    | `/attendance/devices`                       | managers                  | phones, states, `auth` and integrity flags (cursor)                                            |
| POST   | `/attendance/devices/:id/approve`           | managers                  | PENDING → ACTIVE; the person's other ACTIVE phone → REVOKED; notify them                       |
| POST   | `/attendance/devices/:id/revoke`            | managers                  | → REVOKED; notify them                                                                         |
| GET    | `/attendance/requests`                      | managers                  | manual requests (cursor)                                                                       |
| POST   | `/attendance/requests/:id/approve`          | managers                  | creates a MANUAL punch                                                                         |
| POST   | `/attendance/requests/:id/reject`           | managers                  | records the decision                                                                           |
| GET    | `/attendance/register?month=YYYY-MM`        | managers                  | month grid; staff rows by cursor                                                               |
| GET    | `/attendance/register/export?month=YYYY-MM` | managers                  | CSV built by the server — the only non-JSON success body                                       |
| GET    | `/attendance/audit`                         | managers                  | append-only log (cursor)                                                                       |

- **Superadmin:** no route lists superadmin, and the role gate has no implicit bypass (`api_v4/lib/roles.js:17-18`).
- **`:id`:** every `:id` is checked against the caller's own `dealer_id`.
- **Optional extra route:** `POST /attendance/staff/new`, for a person who is not yet a DZZLO user (§4).

## 3. Collections

All seven live on the default connection (`mongoose.model`), beside `users`. The precedent is the new model file `models/user_prefs.js:45` (commit `d2639ee`).

`db_dip` is not used, for two reasons:

- the test app cannot load `helpers/db_conn.js` or mount `/api/dip/v1` (`test/dzzlo_oms_test.js:26-32`);
- the roster joins `users`.

Every index is named and listed in both `test/api_v4/lib/indexes.test.js` and `scripts/perf/atlas-indexes.js`. The user builds them on Atlas first; because the collections start empty, the builds are instant.

| Collection              | Key fields                                                                                                                                                                                                                                                                                                                          | Indexes                                                                                                                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `attendance_sites`      | `dealer_id`, `centre` (GeoJSON Point `[lng, lat]`), `radius_m` 100, `accuracy_max_m` 30, `active`                                                                                                                                                                                                                                   | unique `{dealer_id}` where `active` (one site, C‑3)                                                                                     |
| `attendance_staff`      | `dealer_id`, `user_id`, `status`, `code_hash`, `code_expires_at`, `code_used_at`, `code_tries`                                                                                                                                                                                                                                      | unique `{dealer_id, user_id}`; unique `{user_id}` where ACTIVE (one roster per person in v1)                                            |
| `attendance_devices`    | `dealer_id`, `user_id`, `platform`, `public_key` (SPKI DER), `key_hash`, `match_code`, `auth` (`per_use` / `window` + `window_s`), `key` (`attested` / `unattested`, security level), `integrity` at enrolment (`AVAILABLE` / `UNAVAILABLE`), iOS App Attest key + counter + receipt, `status` PENDING / ACTIVE / REVOKED, approver | unique `{user_id}` where ACTIVE (one phone); unique `{key_hash}`                                                                        |
| `attendance_challenges` | `user_id`, `dealer_id`, `purpose` ENROL / PUNCH, `nonce_hash`, `expires_at`, `used_at`                                                                                                                                                                                                                                              | **TTL** `{expires_at}` (`expireAfterSeconds: 0`); unique `{user_id, nonce_hash}`                                                        |
| `attendance_punches`    | `dealer_id`, `user_id`, `device_id`, `type` IN / OUT, `at` (UTC), `ist_date`, fix (lat, lng, accuracy, age, flags), `distance_m`, integrity verdict (incl. `UNAVAILABLE`), `result`, `code`, `source` APP / MANUAL, `open`, `in_id`, `closed_as`                                                                                    | `{dealer_id, ist_date, user_id}`; `{user_id, at: -1}`; unique `{user_id}` where `type: "IN", open: true` (no double check-in in a race) |
| `attendance_requests`   | `dealer_id`, `user_id`, `ist_date`, `type`, `reason`, `last_code`, `status`, `decided_by/at`, `punch_id`                                                                                                                                                                                                                            | `{dealer_id, status, createdAt: -1}`                                                                                                    |
| `attendance_audit`      | `dealer_id`, `actor_id`, `action`, `target`, `before`, `after`, `at`                                                                                                                                                                                                                                                                | `{dealer_id, at: -1, _id: -1}`; append-only, no update or delete route                                                                  |

- **TTL:** expired documents are removed by a background pass every 60 s, so a challenge can outlive its expiry for a while. Check 2 therefore enforces `expires_at > now` in its own query.
- **No transactions:** none are used today (`helpers/transactions.js:3-26` is never called), and the test database is a standalone server (`test/database.js:66-68`). So multi-document writes are ordered, safe to retry, and guarded by the unique indexes.
- **`dealer_coords` is NOT the geofence:** nothing validates it, and older routes can change it (details: `private/_security-findings.md`, local only). The site form may prefill from it.

## 4. Staff identity and adding people (C‑17, C‑18, C‑26)

Staff are existing dealer users. The design adds no role and no scope, and `models/users.js`, `api_v4/lib/tenancy.js` and the `users` indexes stay as they are. That removes every frozen-file edit from round 2 (`AI.md:85-90`). Staff keep the screens their scope already gives them; a DView member, for example, still sees the read-only business screens. They stay in the dealer's user lists.

| Topic             | Rule                                                                                                                                                                                                                                                                                                       |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Who may check in  | An ACTIVE `attendance_staff` record for (dealer, user). Any scope qualifies, DPrimary included. Only the manager routes write it.                                                                                                                                                                          |
| Staff routes      | Three gates: role `dealer` (hub gate); an ACTIVE membership for `tenantOf(req).co_id` (company gate, `helpers/middlewares.js:65-110`); and the roster gate. Their queries pin `dealer_id` from `tenantOf` and `user_id` from the token.                                                                    |
| Manager routes    | The membership row for `tenantOf(req).co_id` (`models/users.js:41-52`) must be DPrimary or DAdmin (§7).                                                                                                                                                                                                    |
| Sign-in (C‑18)    | Unchanged: email or phone, plus password and OTP. Email stays required.                                                                                                                                                                                                                                    |
| Old builds (C‑26) | Below a minimum build, the attendance routes answer `UPDATE_REQUIRED`. On a punch, the version Google or Apple attests decides (Play Integrity `versionCode`, App Attest `bundleVersion`), because the `meta` header comes from the app. Sign-in is not gated; old builds simply have no Attendance entry. |

**Adding people**

- **`POST /attendance/staff`** takes the `user_id` of a user with an ACTIVE membership in this dealer.
  - A non-member and an unknown id both get the same `FORBIDDEN`, so the route cannot be used to learn which ids exist (the rule of `api_v4/lib/tenancy.js:110-114`).
  - A user already on the roster gets `CONFLICT`.
- **`GET /attendance/staff`** lists the dealer's members from `users` (where `companies.co_id` is the dealer), with name, scope and roster state. No index covers that field, and round 3 adds none; that is fine at today's size (see Unknowns).
- **A person who is not yet a DZZLO user** is first added through the existing user flow — the dealer app's Users screen (`api_v3/services/users.js:29-91`) — with the scope the dealer picks.
  - That path is one of the older routes that **tasks_21** fixes. So attendance does not depend on it: roster changes, device approval and every punch run only through the guarded v4 module (details: `private/_security-findings.md`, local only).
- **Optional — not in the sheet:** a guarded `POST /attendance/staff/new` (managers).
  - In one call it creates the user (role `dealer`, a scope from today's list, email and phone required, duplicates refused), the membership and the roster record, so dzzlo_ro_web never needs the older route.
  - Drop it if tasks_21 ships a guarded general "add user" route first.

**`attendance_config`** is one counters document holding three settings:

- the minimum app builds (C‑26);
- the integrity mode (C‑21: `log`, then `enforce`);
- the v1 list of enabled dealers (C‑22).

A new helper reads it. The helper is built like `helpers/appFeatures.js:9-12` and edited from dip-web's DB-Actions page. It is an additive helper, so it also needs the user's OK.

## 5. Enrolment, server side

1. **`POST /attendance/staff`** (managers) with `user_id` checks the membership and the roster as in §4. It then:
   - creates the roster record;
   - issues an 8-character code: cryptographic random, unambiguous alphabet, hashed, valid 48 h, 5 tries, single use;
   - writes the audit entry;
   - answers with the code, once.
2. **Sign-in.** The person signs in to DZZLO OMS as they do today. The Attendance entry appears because they are on the roster ([[02-app]]).
3. **`POST /attendance/enrol/challenge`** finds the roster record for the `tenantOf` dealer and the token's user, compares the code in constant time, and checks the expiry and the tries left. It then issues 32 random bytes, valid for 2 min.
4. **`POST /attendance/enrol`** uses up the challenge atomically and verifies the proof (table below), or records UNAVAILABLE. Then it:
   - stores the phone as PENDING, with its `auth`, `key` and `integrity` values;
   - stores a 6-character **match code** derived from the public key, which the phone and dzzlo_ro_web both show, so the dealer can match the phone in person;
   - marks the code used;
   - sends "phone waiting for approval" to the dealer's managers by OneSignal `external_id` (`api_v3/controllers/App/notification.js:9-45`). The app already sets that id to the user id (`dzzlo_oms_app` `src/navigation/AppNavigatorContainer.js:100`).
5. **Approve.** The dealer sees the phone's flags before approving. Approval revokes the person's current ACTIVE phone, activates this one, writes the audit entry and sends "phone approved". The partial unique index keeps at most one phone ACTIVE.

| Case                              | Server verifies                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Android chain (7+)                | The phone sends the Keystore EC P-256 chain, made with `setAttestationChallenge(challenge)`, and, where Play services exist, a Play Integrity token whose `requestHash` = SHA-256(challenge ‖ public key). The server checks: (1) the chain ends at a Google root — the original, or the ECDSA P-384 "Key Attestation CA1" that signs from 1 Feb 2026; (2) every signature; (3) the revocation list `android.googleapis.com/attestation/status` — old factory chains stay trusted past their dates unless revoked; (4) the first KeyDescription extension (OID 1.3.6.1.4.1.11129.2.1.17) counted from the root: the challenge matches, the security level is TrustedEnvironment or StrongBox, `verifiedBootState` is Verified with the device locked, `attestationApplicationId` (tag 709) is `in.vsyst.dzzlooms` with the Play app-signing digest, and the key is EC P-256 for signing; (5) the leaf key equals the key sent. |
| Android auth fields               | **11+:** `userAuthType` (504) covers biometric and device credential, and there is no `authTimeout` (505) → `auth: per_use`. **7–10:** `authTimeout` (505) is present → `auth: window`, `window_s` = its value, accepted up to a cap (proposal 30 s). **Either version:** if `noAuthRequired` (503) is present or `userAuthType` is missing, the key is not tied to the phone's lock — a real failure (C‑21). The app asks the person to set a screen lock first.                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| iOS (15.1+)                       | The App Attest attestation, with `clientDataHash` = SHA-256(challenge), passes Apple's steps: (1) `x5c` chains to the Apple App Attestation Root CA; (2) the nonce SHA-256(authData ‖ clientDataHash) equals extension 1.2.840.113635.100.8.2; (3) SHA-256 of the key is the key id; (4) the RP ID hash is SHA-256 of Team ID + bundle id; (5) the counter is 0; (6) `aaguid` is `appattest` + seven 0x00 bytes; (7) `credentialId` is the key id; (8) the validation-category and bundle-version values. Then an assertion over challenge ‖ the Secure Enclave public key binds that key to this app.                                                                                                                                                                                                                                                                                                                         |
| UNAVAILABLE and unattested (C‑29) | **No Play services:** no token, so `integrity: UNAVAILABLE`. **An iPhone where App Attest is unsupported:** `integrity: UNAVAILABLE` and `key: unattested`; the Secure Enclave key is then bound only by the in-person approval and the match code. **A chain that does not end at a Google hardware root:** `key: unattested`. Each is accepted with a flag and never refused on its own. Real failures follow C‑21: log-only during the pilot, then enforce.                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

## 6. Punch verification

`POST /attendance/challenge` returns 32 random bytes, valid for 2 minutes. The device key then signs one line of text:

```text
v1|<challenge>|<IN or OUT>|<lat>|<lng>|<accuracy_m>|<fix time>|<flags>
```

The server verifies the signature over the exact bytes it received, then reads the values from those same bytes, so no number is re-serialised. The checks run in order: the first failure wins, and every attempt that reaches this handler is stored.

| #   | Check                                                                               | Code                                  | Verified by                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| --- | ----------------------------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | role `dealer`; an ACTIVE membership in the tenant's dealer; an ACTIVE roster record | `STAFF_INACTIVE`                      | `req.user`, the membership row, `attendance_staff`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2   | the challenge exists, is unused, ≤ 2 min old and this user's PUNCH; then it is used | `CHALLENGE_BAD`                       | one atomic `findOneAndUpdate` with `used_at: null` and `expires_at > now` in the filter, so it works once even in parallel                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 3   | the phone is ACTIVE and this user's; the signature is valid                         | `DEVICE_NOT_ACTIVE` / `SIGNATURE_BAD` | `crypto.verify("sha256", bytes, { key, format: "der", type: "spki" }, sig)`. Node's default ECDSA encoding is DER, so no dependency is needed. An `auth: window` key proves only an unlock within its window, and the punch carries that flag.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 4   | integrity, bound to this challenge                                                  | `INTEGRITY_FAILED`                    | **Android:** Google's `decodeIntegrityToken`. `requestHash` = SHA-256(challenge ‖ payload); `requestPackageName` = `in.vsyst.dzzlooms`; `timestampMillis` within 2 min; `PLAY_RECOGNIZED` + `LICENSED` + `MEETS_DEVICE_INTEGRITY`; `versionCode` ≥ the minimum. **iOS:** decode the CBOR assertion. clientDataHash = SHA-256(challenge ‖ payload); nonce = SHA-256(authenticatorData ‖ clientDataHash). The signature over the nonce must verify with the stored App Attest key, the RP ID hash must match, the counter must rise (the new value is stored), and the embedded challenge must match. **UNAVAILABLE:** a phone enrolled UNAVAILABLE is accepted with a flag (C‑29). A phone enrolled with integrity that now reports UNAVAILABLE counts as a failure. **Real failures:** C‑21 — log-only during the pilot, then enforce. |
| 5   | the location is not marked fake                                                     | `LOCATION_FAKE`                       | the signed flags (`isMock` / `isFromMockProvider`, `isSimulatedBySoftware`) — applied to every phone, UNAVAILABLE ones too; `isProducedByAccessory` only flags                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 6   | accuracy ≤ 30 m (the site's limit); the fix is ≤ 30 s old                           | `LOCATION_VAGUE` / `LOCATION_STALE`   | the signed numbers; the age is measured with one phone clock (see Unknowns)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 7   | the distance is ≤ the radius (100 m)                                                | `OUTSIDE_SITE`                        | haversine from the site centre; `distance_m` is stored                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 8   | IN needs no open IN; OUT needs one; ≥ 2 min since the last punch                    | `DUPLICATE` / `NO_OPEN_CHECKIN`       | an IN open more than 16 h is first closed as NO_CHECKOUT, with no hours; the partial unique index stops two parallel INs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |

Proposed statuses for the new entries in `api_v4/lib/errors.js:10-50`:

- **403:** `STAFF_INACTIVE`, `DEVICE_NOT_ACTIVE`, `SIGNATURE_BAD`, `INTEGRITY_FAILED`;
- **409:** `CHALLENGE_BAD`, `DUPLICATE`, `NO_OPEN_CHECKIN`;
- **422:** `LOCATION_FAKE`, `LOCATION_VAGUE`, `LOCATION_STALE`, `OUTSIDE_SITE`;
- **426:** `UPDATE_REQUIRED`.

`error_code` is the contract (`api_v4/lib/errors.js:4-9`). The `error` text tells the person how to fix the problem.

**The 16-hour rule.** The API has no scheduler: there is no cron dependency (`package.json:30-51`) and only one PM2 app (`ecosystem.config.js:1-19`). So the rule runs lazily, at the next punch and on every Today or Register read.

## 7. The two gates and the route-table test

Both gates live in `api_v4/lib/`. They run after the role gate and before the validator, in the same order `api_v4/routes/screens.js:16-23` uses for `requireRole`. Both start from `co_id` = `tenantOf(req).co_id` and the caller's membership row for it in `req.user.companies` (the row the company gate matched). Neither ever uses the top-level `user.scope`, which follows the persisted active company (`api_v3/services/dealer_msts.js:111-130`).

- **`requireRosterMember()`** (staff routes): the membership is ACTIVE and an ACTIVE `attendance_staff` record exists for (dealer, user). Otherwise it answers `STAFF_INACTIVE` (403).
- **`requireAttendanceManager()`** (manager routes): the membership row's scope is `DPrimary` or `DAdmin` (C‑22, v1). Otherwise it answers `FORBIDDEN` (403). Superadmin gets no bypass.

**v1 has no `att.*` permission strings.** Attendance permissions are not stored where older routes can write them. Grants for other dealer users come later, through a new guarded v4 route.

Both gates trust the membership rows. The older routes that can change those rows are covered by tasks_21 (details: `private/_security-findings.md`, local only).

**The route-table test** is a new `test/api_v4/harness/attendance_routes.test.js`. It walks the module router's `stack` (Express 5 router 2.2.0: `node_modules/router/lib/layer.js:34-44`, `route.js:41-47`) and asserts:

- every route has a `requireRoleGate` (`api_v4/lib/roles.js:32`) narrowed to exactly `["dealer"]`;
- every route has exactly one of the two gates, placed before its validator — the roster gate on the 6 staff routes, the manager gate on the 16 manager routes;
- the list equals §2, so an unlisted route fails.

New cases in `roles.test.js` cover three callers. A DView member on the roster passes the staff routes and gets `FORBIDDEN` on the manager routes. A member who is not on the roster gets `STAFF_INACTIVE`. A customer gets `FORBIDDEN_ROLE`.

This adds to the boot contract (`api_v4/index.js:35-54`; `test/api_v4/harness/chain.test.js:20-42`), which checks modules, not routes.

## 8. IST date

- **Instants** are stored in server UTC.
- **`ist_date`** is the IST day of the IN, computed on each request with `istDayEnd` (`api_v3/services/ledger_window.js:67-70`, exported at `:526`), the way Daily Summary already does it (`api_v4/readmodels/dailySummary.js:8,104-107`).
  - The day starts at `istDayEnd(at)` − 86,400,000 ms; IST has no daylight saving.
  - A small v4 helper formats it as `YYYY-MM-DD`.
- **Night shifts:** an OUT takes its IN's `ist_date`.
- **Register month:** from IST midnight on the 1st, up to but not including IST midnight on the next 1st.
- **Tests:** the helper is tested under `TZ=UTC` and `TZ=Asia/Kolkata` in child processes, as `test/api_v4/lib/dailySummaryModel.test.js:340-362` does.

## 9. Rate limits, time limits, validation, logging

- **Rate limits:** per-user limiters built like `screensRateLimit` (`api_v4/lib/rateLimit.js:30-52`). They key by user, because a forecourt's phones share one IP, and answer `RATE_LIMITED`.
  - Starting numbers, which P0 tunes: enrol challenge 5 per 10 min · enrol 5 an hour · challenge and punch 10 a minute · requests 10 an hour · manager routes 120 a minute.
  - The limiters are a safety valve. The hard limits are the database rules: single-use challenges, the 2-minute gap, and 5 tries per code.
- **Time limits:** every read uses `limitFind` / `limitAggregate` (`api_v4/lib/limits.js:23-42`). The new routes are added to `test/api_v4/harness/limits.test.js`, which lists its routes by name (`:38-40`).
- **Validation:** one `defineSchema` per route and source (`api_v4/lib/validate.js:209-212,424-446`), refusing unknown keys (`:19-20`). Specific rules:
  - `month` is `YYYY-MM`;
  - `cursor` is a non-empty string (as in `api_v4/schemas/dailySummary.js:66`);
  - `user_id` is an ObjectId;
  - lat is −90..90, lng is −180..180, and accuracy is greater than 0;
  - base64 fields are capped, and the 1 MB body limit (`dzzlo_oms.js:59`) fits a certificate chain.
- **Logging:**
  - Production logs each request's URL (`helpers/middlewares.js:236-261`), so GPS travels only in request bodies.
  - Attendance bodies stay out of any request logging.
  - Tokens and attestations are not kept raw; only verdict summaries and certificate hashes are stored.
- **CSV:** a cell that starts with `=`, `+`, `-` or `@` gets a leading `'`, so a spreadsheet does not run it as a formula.

## 10. Tests (P1, the contract first)

Each step is a red `test(v4/attendance): …` commit followed by a green `feat(v4/attendance): …` commit, as `a6b3637` → `07368e7` did for Daily Summary. A mutation smoke follows, recorded in the PR (`docs/testing.md:693-700`). The house idiom is `docs/testing.md` §11 (`:469-728`) and the [[vsyst-technologies/docs/oms_api/tdd-testing-guide|API TDD guide]].

| #   | Red → green                                                                                                                                                                    | Mutation smoke               |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------- |
| 1   | route table and both gates: a roster member with DView / DOrder / DAccount passes the staff routes and is refused on manager routes; a non-roster member gets `STAFF_INACTIVE` | the roster gate on one route |
| 2   | sites; one active site                                                                                                                                                         | the radius range rule        |
| 3   | roster: add an existing member; non-member and unknown id → the same `FORBIDDEN`; the enrolment code                                                                           | the membership check         |
| 4   | enrol: Android 11+ per-use, Android 7–10 window, unattested chain, UNAVAILABLE, iOS — recorded P0 samples plus chains signed by a test root; Google and Apple mocked           | the challenge match          |
| 5   | approve / revoke; one ACTIVE phone                                                                                                                                             | the revoke-old step          |
| 6   | challenge + punch: one red case per code; every attempt stored; parallel INs → one wins; UNAVAILABLE accepted with a flag; a downgrade to UNAVAILABLE refused                  | each check in turn           |
| 7   | manual requests → MANUAL punch                                                                                                                                                 | the PENDING-only rule        |
| 8   | Today, Register, export: IST windows, NO_CHECKOUT, CSV escaping, cursor pages                                                                                                  | the 16 h rule                |
| 9   | audit pages; `/screens/attendance` (own rows only)                                                                                                                             | the `user_id` filter         |
| 10  | time limits, rate limits, version gate                                                                                                                                         | `limitFind` on one read      |
| 11  | `yarn fixtures:export:v4` gains attendance captures (`test/api_v4/temp/fixtures.captures.js`); the app and the web pull them                                                   | —                            |
| 12  | (only if chosen) `POST /attendance/staff/new`                                                                                                                                  | the duplicate-email check    |

Harness rules:

- No suite leaves the process; Google, Apple and the revocation list are mocked.
- The test database is standalone.
- Identities resolve through the seed (`test/api_v4/harness/fixtures/identities.js:17-63`). The seeded second dealer is DPrimary of its own company and DView on Dealer One (`:19`), which makes it a ready non-owner member to put on Dealer One's roster.
- Each test makes its own keys with `crypto.generateKeyPairSync("ec", { namedCurve: "P-256" })`.

## 11. New dependencies and credentials (C‑24)

The list the user approves is [[06-package-approval-list]]. Nothing is installed before that approval. The server-side candidates are:

| Need                          | Candidate (unverified)                                                                                                                   | Credential / config                                                                                                                    |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Play Integrity decode         | `google-auth-library` + an HTTPS call to `decodeIntegrityToken`, or `googleapis`                                                         | a Google Cloud project linked in Play Console; a service account (`playintegrity` scope) whose key is a server secret, never in a repo |
| ECDSA P-256, X.509 chains     | Node `crypto` (`verify`, `X509Certificate`) — none                                                                                       | pinned public roots: Google key attestation (both) and the Apple App Attestation Root CA                                               |
| X.509 extensions              | `asn1js` + `pkijs`, or `@peculiar/asn1-schema` + `@peculiar/x509` (maybe `@peculiar/asn1-android`); Node cannot read an extension by OID | —                                                                                                                                      |
| CBOR (App Attest)             | `cbor-x` or `cbor`; or an end-to-end package (`node-app-attest`, `appattest-checker-node`)                                               | Apple Team ID and bundle id (not secret)                                                                                               |
| Revocation list, Google calls | none (HTTPS, cached)                                                                                                                     | outbound HTTPS to `android.googleapis.com`, `playintegrity.googleapis.com`, `oauth2.googleapis.com`                                    |
| App signing identity          | —                                                                                                                                        | the Play app-signing certificate SHA-256, from Play Console                                                                            |

**Quota (C‑11).** Google allows 10,000 Play Integrity requests a day per Cloud project by default, and token preparations and decodes share that budget (confirmed). An Android punch costs about 2 units, so roughly 5,000 Android punches a day fit; phones without Play services cost none. Raising the quota needs the linked project and a form, and can take up to a week.

## Unknowns

- **C‑29 (open):** accept and flag UNAVAILABLE (recommended), or manual requests only. This file also puts unattested keys under C‑29.
- **Clock (differs from the sheet):** the payload's single "fix time" depends on the phone's clock. Proposal: also sign the signing time, or the fix age measured on the phone. Flag a large phone–server gap rather than refusing.
- **Attempts (differs from the sheet):** refusals made before the handler cannot be stored as punches. That covers the API key, sign-in, company status, role, rate limit and version gate.
- **Read differently:** `PATCH /attendance/staff` is read as `/attendance/staff/:id`.
- **Added beyond the sheet:**
  - the `attendance_config` document;
  - `UPDATE_REQUIRED` and the proposed statuses;
  - the match code;
  - the 30 s window cap;
  - the downgrade rule (once integrity is AVAILABLE, a later UNAVAILABLE is a failure);
  - one roster per person in v1;
  - the optional `POST /attendance/staff/new`.
- **Member list:** `GET /attendance/staff` reads `users` by membership with no index, and round 3 adds none. Measure it at P0.
- **C‑8:** dropping raw coordinates after 90 days needs either a sweep or an eighth, TTL-indexed collection. There is no scheduler.
- **Confirm at P0 with real phones:**
  - DER signatures on both platforms;
  - how per-use and window keys actually appear in Android 7–10 and 11+ chains.
- **Unclear:**
  - the confidence level of iOS `horizontalAccuracy` (Android reports 68 %);
  - which iOS versions carry Apple's bundle-version value;
  - the `timestampMillis` window (Google sets none; 2 min proposed).
- **Not verified:** the production API version. No dependency has been chosen yet.

## Sources

`dzzlo_oms_api` `slave` @ `86083ca`:

- **Mount and chain:** `dzzlo_oms.js:59,121`; `api_v/api4.js:7-9`; `api_v4/index.js:26-31,35-54,69-84`; `helpers/middlewares.js:45-58,65-110,236-261`; `api_v3/auth.js:61-75`.
- **v4 library:** `api_v4/lib/roles.js:17-18,26-39`; `tenancy.js:42-54,64-80,110-114`; `errors.js:4-9,10-50,105-134`; `respond.js:18-29`; `rateLimit.js:30-52`; `limits.js:23-42`; `validate.js:19-20,209-212,424-446`; `cursor.js:169,212-216`.
- **v4 routes:** `api_v4/routes/screens.js:16-54`; `api_v4/readmodels/dailySummary.js:8,104-107`; `api_v4/schemas/dailySummary.js:66`.
- **v3:** `api_v3/services/ledger_window.js:67-70,526`; `api_v3/services/users.js:29-91`; `api_v3/services/dealer_msts.js:111-130`; `api_v3/controllers/App/notification.js:9-45`.
- **Models and helpers:** `models/users.js:41-52`; `models/user_prefs.js:45`; `helpers/appFeatures.js:9-12`; `helpers/transactions.js:3-26`.
- **Project:** `package.json:30-51`; `ecosystem.config.js:1-19`; `AI.md:85-90`; `node_modules/router/lib/layer.js:34-44`, `route.js:41-47`.
- **Tests:** `test/dzzlo_oms_test.js:26-32`; `test/database.js:66-68`; `test/api_v4/harness/chain.test.js:20-42`; `test/api_v4/harness/limits.test.js:38-40`; `test/api_v4/lib/dailySummaryModel.test.js:340-362`; `test/api_v4/harness/fixtures/identities.js:17-63`; `docs/testing.md:469-728,693-700`.
- **Commits:** `a6b3637`, `07368e7`, `d2639ee`.

`dzzlo_oms_app` `slave` @ `ea7e7222`: `src/navigation/AppNavigatorContainer.js:100`.

Platform sources, read 2026-10-01. All are **confirmed** except the Apple root:

- Play Integrity standard requests (`requestHash` ≤ 500 bytes, decode, service account, replay): <https://developer.android.com/google/play/integrity/standard>
- Play Integrity verdicts: <https://developer.android.com/google/play/integrity/verdicts>
- Play Integrity quota: <https://developer.android.com/google/play/integrity/setup>
- Key attestation (roots incl. CA1 from 1 Feb 2026, revocation list, first extension from the root): <https://developer.android.com/privacy-and-security/security-key-attestation>
- Attestation OID, tags 503 / 504 / 505 / 709, enums: <https://source.android.com/docs/security/features/keystore/attestation>
- App Attest attestation and assertion steps: <https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server>
- Node `crypto.verify` (DER by default) and `X509Certificate`: <https://nodejs.org/api/crypto.html>
- MongoDB TTL timing: <https://www.mongodb.com/docs/manual/core/index-ttl/>
- Apple App Attestation Root CA — **found by search; fetch at "start"**: <https://www.apple.com/certificateauthority/Apple_App_Attestation_Root_CA.pem>
