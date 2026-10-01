---
title: tasks_20 · 03 — the dealer side in dzzlo_ro_web
status: PLAN — not started (2026-10-01). No code, no branch, no commit. Execution waits for the user's "start".
---

# 03 — The dealer side in dzzlo_ro_web

The dealer manages attendance inside dzzlo_ro_web (C‑16). It gets seven new pages in a third Dashboard section, **Attendance**: Today, Staff, Devices, Outlet location, Requests, Register (with a CSV export) and Audit. Staff are the dealer's existing DZZLO users, in any dealer scope (C‑17). The dealer puts them on the attendance roster from the Staff page, and they check in with the DZZLO OMS app ([[02-app]]). Sign-in to this site stays exactly as it is today. Every page talks only to the v4 attendance module ([[01-api]]), which takes the dealer from the login. The calls go through a small v4 base beside today's DIP client: absolute URLs, the `x-co-id` header and the v4 key. In v1 only DPrimary and DAdmin manage attendance (C‑22). Other dealer users come later, through permissions written only by a new guarded v4 grant route. v1 serves DIP dealers only, because every ro-web route already waits for the DIP dealer record. No new npm dependency is needed: there is no map library, the server builds the CSV, and the browser's own `Intl` formats times for Asia/Kolkata. This is phase P3 in [[00-overview]]. It starts once [[01-api]]'s P1 contract exists, runs beside the app work, and tests against MSW fixtures of that contract until the API is live.

**Citations.** `ro-web` = `dzzlo_ro_web` `main` @ `5a66bf8` · `api` = `dzzlo_oms_api` `slave` @ `86083ca` · `app` = `dzzlo_oms_app` `slave` @ `ea7e7222`. All three were opened on 2026-10-01 with clean working trees. Paths without a repo name are ro-web. Items marked _mine_ are proposals; say so to change them.

## 1. Where it plugs in

| Piece           | Today                                                                                                                                                                                                                                                    | Attendance adds                                                                                                                                                                                                                                                           |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Routes          | One flat `DEALER_ROUTES` array of lazy pages (`src/App.js:28-57`, `:100-193`). An entry with `perm` is wrapped in `PermissionRoute` (`:316-333`).                                                                                                        | Seven entries, `/att_today` … `/att_audit`, each behind the owner-only gate (§2). Pages live in `src/pages/attendance/<Page>/<page>.js` (`CLAUDE.md:57`). Paths stay flat, like `/new_decan`.                                                                             |
| Who gets routes | Role `dealer` only (`src/App.js:312`), and only after the DIP dealer record loads (`:314`). Without it: "Dealer not registered for DIP package" (`:337-341`, `src/pages/personal/Dashboard.js:64-75`).                                                   | Nothing changes in v1 (C‑22, §2).                                                                                                                                                                                                                                         |
| Gate            | DPrimary and DAdmin always pass (`src/routes/PermissionRoute.js:27,33`). Everyone else needs `dip.enabled` (`:35-57`), then a `dip.<resource>.<action>` string (`:59-81`).                                                                               | An owner-only branch: DPrimary or DAdmin on the current membership row, and no `dip.enabled` (§2).                                                                                                                                                                        |
| Menu            | No section menu in the Navbar (`src/components/Navbar/Navbar.js:130-168`). The Dashboard has two tile sections, Transactions and Masters (`Dashboard.js:21-55`, `:77-117`; tile: `src/components/DashboardItem.js:8-104`). Every tile shows to everyone. | A third section, **Attendance**, after Masters: seven tiles, shown only to DPrimary and DAdmin (_mine_). Icons come from the Material set already in the repo (`src/components/SVG/RNVI/MaterialIcons/index.js`: `people`, `phone`, `my-location`, `message`, `preview`). |
| Data            | `src/store/dipApis/*`, `src/store/apis/dzzlooms/*`                                                                                                                                                                                                       | `src/store/apis/v4/base.js` and `src/store/apis/v4/attendance.js` (§5)                                                                                                                                                                                                    |

## 2. Permissions (C‑22)

- **v1, decided (C‑22).** DIP dealers only, and only DPrimary and DAdmin manage attendance.
  - These are the two scopes that already pass every DIP check (`src/utils/permissions.js:29`).
  - Every attendance page, Audit included, is theirs alone.
  - v1 has no attendance permissions for other dealer users.
  - A DPrimary or DAdmin may also be on the roster (C‑17); the self-approval rule is in §4.
- **Read the membership row, not the top-level scope.** The owner check reads the current company's row: the `user.companies` entry whose `co_id` equals `user.co_id`, and its `scope`. This is the same rule as the API's guard ([[01-api]]). Today's DIP hooks read the top-level `user.scope` (`src/utils/Hooks/usePermissions.js:13,29`); `getUserDipEnabled` already reads the row (`:41-52`).
- **An owner-only gate.** `PermissionRoute` hard-codes DIP. A user outside the two owner scopes first needs `dip.enabled` (`PermissionRoute.js:35`), then a `dip.`-prefixed string (`usePermissions.js:18`, `src/utils/permissions.js:36-37`). Owners already pass both, so the attendance gate needs no `dip.enabled` at all. Proposed (_mine_):
  - route entries name their gate;
  - `pkg: "dip"` works exactly as today;
  - `pkg: "att"` lets DPrimary and DAdmin through, and shows the usual denial alert to everyone else;
  - one helper, `isAttOwner(user)`, serves the route gate and the Dashboard section.

  The web gate only shapes the screen. The API's guard decides, and its 403 shows as an alert.

```js
{
  path: "/att_staff",
  Component: AttStaff,
  perm: { pkg: "att", label: "Attendance staff" },
},
```

- **The DIP-dealer prerequisite.** v1 keeps attendance behind the DIP dealer record (`src/App.js:314`). Owners already pass the sign-in rule and the dealer-record read. A dealer without the record sees "Dealer not registered for DIP package". Non-DIP dealers come later.
- **Later, via a guarded v4 grant route (not v1).** Other dealer users get pages through permissions written only by a new guarded v4 grant route. Attendance permissions are not stored where older routes can write them (details: `private/_security-findings.md`, local only). The proposed shape:
  - `att.view` opens Today and Register;
  - `att.manage` opens Staff, Devices, Outlet location and Requests, and also the `att.view` pages (_mine_);
  - `att.export` adds the Register's export button.

  The web would then need four changes:
  - an Attendance card on `/edit_user` that calls the grant route;
  - a string check inside the `pkg: "att"` gate;
  - a sign-in rule that admits these users (today a user outside the owner scopes needs `dip.enabled`, `src/store/apis/dzzlooms/auth.js:20-27`);
  - attendance routes drawn from the attendance module's own answer instead of the DIP record.

## 3. Sign-in: unchanged

- **No new role means nothing new to refuse.** Staff are existing dealer users (role `dealer`, C‑17). Sign-in stays exactly as today: the rule in `src/store/apis/dzzlooms/auth.js:13-28`, and the stored-session check in `src/App.js:243-250`.
- **Staff check in from the app, not here.** A staff member who already uses ro-web keeps exactly the pages their scope and DIP access give them today. The Attendance pages stay DPrimary and DAdmin only (§2).
- **No new sign-in tests.** The existing ones (`src/pages/auth/SignIn/signin.test.js:50-219`, `src/App.test.js:36-55`) stay green.

## 4. The pages

| Page            | Route           | Who (v1)                      | Reused from ro-web                                                                                                                                                                     | v4 calls ([[01-api]])                                                                                         |
| --------------- | --------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Today           | `/att_today`    | DPrimary, DAdmin              | `TransactionListLayout` (`src/pages/transactions/shared.js:108-183`), `Table`, `Badge`, `Alert`                                                                                        | `GET /attendance/today`                                                                                       |
| Staff           | `/att_staff`    | DPrimary, DAdmin              | `MasterListLayout`, `filterBySearch` (`src/pages/masters/index.js:245-295`, `:65-73`), `Table` as in `Users/users.js:93-121`, `Modal` + `useModal` (`src/utils/Hooks/useModal.js:3-8`) | `GET`/`POST`/`PATCH /attendance/staff` · `POST /attendance/staff/:id/enrolment-code`                          |
| Devices         | `/att_devices`  | DPrimary, DAdmin              | `Table`, `Badge`, a confirm `Modal` shaped like `DeleteConfirmModal` (`src/pages/masters/index.js:146-240`), a frozen enum like `src/utils/enums.js:1-5`                               | `GET /attendance/devices` · `POST /attendance/devices/:id/approve` · `POST /attendance/devices/:id/revoke`    |
| Outlet location | `/att_outlet`   | DPrimary, DAdmin              | `TransactionFormLayout` (`src/pages/transactions/shared.js:189-298`), `Form`, `Alert`, the `my-location` icon                                                                          | `GET`/`PUT /attendance/sites`                                                                                 |
| Requests        | `/att_requests` | DPrimary, DAdmin              | `TransactionListLayout`, cards as in `DecanList/decanList.js:412-451`, a reason `Modal`                                                                                                | `GET /attendance/requests` · `POST /attendance/requests/:id/approve` · `POST /attendance/requests/:id/reject` |
| Register        | `/att_register` | DPrimary, DAdmin (export too) | the month-year select (`DecanList/decanList.js:57-71`, `:281-298`), `Table responsive`                                                                                                 | `GET /attendance/register?month=YYYY-MM` · `GET /attendance/register/export?month=YYYY-MM`                    |
| Audit           | `/att_audit`    | DPrimary, DAdmin              | `builder.infiniteQuery` + `useInfiniteScroll` (`src/store/dipApis/decants.js:25-62`, `src/utils/Hooks/useInfiniteScroll.js:17-56`)                                                     | `GET /attendance/audit` (cursor paging)                                                                       |

Other dealer users come later, through the grant route (§2).

**Today.** One row per roster member, with open check-ins first.

- **Each row** reads "IN since 09:02", "OUT 18:10 (8 h 08 m)", "not in yet", or yesterday's NO_CHECKOUT.
- **A "refused today" count** shows the last code in plain words (`OUTSIDE_SITE` → "outside the pump area").
- **A flag mark** sits on a punch that was accepted with a flag, such as one from a phone without an integrity check (C‑29) (_mine_).
- **Two counters** link to Devices (phones waiting) and Requests (pending).

Times are shown in IST (§6); no coordinates appear. The page refreshes every 60 s while open, and on focus (_mine_). The prepared socket hook stays off (`src/App.js:211-212`).

**Staff.** The page lists the dealer's existing DZZLO users, in any dealer scope (C‑17). Each row shows the person's scope, roster status and phone status. The list comes from the v4 module, not from the call the Users master uses today (details: `private/_security-findings.md`, local only).

- **"Add to attendance"** creates the roster record and shows the one-time enrolment code (single use, 48 h) in a modal, once, with the person's next steps: open DZZLO OMS with their own login → Attendance → "Set up this phone" → enter the code. The code is never stored in the browser. "New code" issues a fresh one, and the server retires the old one.
- **"Remove from attendance"** sets the roster record INACTIVE after a confirm. The person stays a DZZLO user with the same scope.
- **Being on the roster changes nothing else.** Each person keeps the screens their scope already gives them, and stays in the Users master like any other user (C‑17).
- **Not a DZZLO user yet?** Add the person first through the existing user flow, with the scope the dealer picks.
  - Today that flow is in the DZZLO OMS app: Users → "+" → the add-user form (app `src/screens/Dealer/Users/index.js:373-389`, `AddEditUsers.js:296-305`; scope picker `src/utils/Conditional/Scopes.js:99-182`).
  - ro-web has no such flow: its Users "Create New" button is a stub (`src/pages/masters/Users/users.js:79-82`).
  - [[01-api]] may propose a guarded v4 "add user" command, with a ro-web button to match. Fixes to the older routes are tasks_21.

**Devices.** Pending phones come first, each with the staff name, the phone model and OS, and the enrolment time. Two badges help the dealer judge each phone (C‑20, C‑29):

- **Lock type.**
  - `per-use`: the key needs a biometric or PIN for every punch (Android 11+ and iPhone).
  - `window`: Android 7–10, where the key stays unlocked for a short time after a biometric or PIN. It is weaker, but supported.
- **Integrity.**
  - It reads `OK` or a failed verdict; failures are logged only during the pilot (C‑21).
  - It reads `UNAVAILABLE` for an Android phone without Google Play services, or an iPhone without App Attest. Under C‑29's recommended answer such a phone is accepted and its punches carry a flag; under the alternative it can only send manual requests. The badge text says which.
- **Approve** sits behind a confirm: approve only with the person and the phone in front of you; approving a new phone revokes the old one.
- **Revoke** asks for a reason.
- **No self-approval (_mine_).** A manager on the roster (C‑17) cannot approve their own phone; another manager must. DPrimary may approve their own, and the audit marks it. [[01-api]] enforces this, and the page hides the button.

The "phone waiting" push reaches the dealer ([[02-app]]); the decision is made here.

**Outlet location.** One site per dealer in v1 (C‑3). The fields are latitude, longitude, radius (default 100 m) and accuracy limit (default 30 m).

- **"Use my current location"** is for the dealer at the pump with a phone.
  - **HTTPS only.** Elsewhere the button is disabled, with the reason shown (`window.isSecureContext`).
  - **Shows the accuracy.** It takes a fresh high-accuracy reading and shows the accuracy reported ("± 12 m").
  - **Saves only an accurate-enough reading.** Only a reading within the site's accuracy limit fills the fields and can be saved. A vaguer one is refused as "too vague — try again". The page keeps the best reading of a watch of about 20 s (_mine_).
- **Manual latitude and longitude entry**, range-checked, up to six decimals.
- **An "Open in Maps" link** carries the coordinates, so the dealer can check the spot. There is no map library in v1.

The server audits site changes. The page warns that staff will be refused while a wrong pin is saved.

**Requests.** These come from the app after a failed punch ([[02-app]]).

- **Each request shows** the staff member, the day, IN or OUT, the time asked for, the reason, and the last refusal code in plain words.
- **Approve** creates a MANUAL punch on the server. **Reject** needs a reason.
- **No self-approval:** the Devices rule applies to a manager's own request.
- **Pending first**, with a status filter.

**Register.** A month grid of staff × day, with per-person totals. Each cell shows in, out, hours, and the MANUAL, NO_CHECKOUT and flag marks.

- **The month picker** reuses the Decantation list's select, but it sends `month=YYYY-MM` and builds no time window in the browser (§6).
- **On a phone**, `Table responsive` scrolls sideways and the name column stays fixed.
- **Export** is described in §7.

**Audit.** A read-only list: approvals, revocations, codes issued, roster changes, site changes, manual punches and request decisions, with before → after where recorded. v4 pages by cursor (`page.next`, `page.hasMore`, api `api_v4/lib/cursor.js:158-172`), and the infinite query reads that cursor.

## 5. The v4 API base

- **Absolute URLs.**
  - Today's single `createApi` has the base URL `${API_URL}/api/dip/v1/`. Its `prepareHeaders` adds the login token and `x-api-key` (`src/store/apis/createApi.js:6-22`). The repo keeps one `createApi` (`CLAUDE.md:32`).
  - Add `API_URL_V4` beside `:6-7`, plus `src/store/apis/v4/base.js` with `v4Url(path)` and `unwrap`. `unwrap` reads the v4 envelope `{ success, data, page?, meta }` (api `api_v4/lib/respond.js:3-29`).
  - RTK Query leaves absolute URLs alone (`node_modules/@reduxjs/toolkit/dist/query/rtk-query.modern.mjs:82-95`, RTK 2.11.2). The app already works this way (app `src/store/apis/v4/base.js:1-45`).
- **`x-co-id`.**
  - `prepareHeaders` also sends `getState().auth.user.co_id`, as the app does (app `src/store/apis/createApi.js:34-42`).
  - v4 uses it only for a company the user belongs to, and otherwise uses the login's company (api `api_v4/lib/tenancy.js:42-54`).
  - A sister-company switch reloads the page (`src/components/Navbar/Navbar.js:224-241`), so the header always names the company on screen.
  - Attendance uses the v4 module, which takes the dealer from the login; the web never sends a dealer id for attendance.
- **The v4 key.**
  - v4 checks its own key (api `helpers/middlewares.js:45-57`). The web sends `VITE_X_API_KEY` on every call (`createApi.js:20`).
  - The development and testing values already match (compared without printing, 2026-10-01).
  - Production's value is set on the host and is checked at P3 (§9).
- **Tags.** `att_today`, `att_staff`, `att_devices`, `att_sites`, `att_requests`, `att_register` and `att_audit` join `tagTypes` (`createApi.js:56`; `docs/rtk-query-conventions.md:126`).
  - Queries provide tags and mutations invalidate them (`REVIEW.md:19-20`). Approving a device invalidates `att_devices` and `att_today`; deciding a request also refreshes Register and Audit.
  - Hooks keep the underscore names, for example `useFetch_att_todayQuery`.
- **Errors.**
  - v4 fails with `{ success: false, error, error_code }`, and `errorRTK` already reads `error` (`createApi.js:79-87`).
  - A small map turns `error_code` into plain words: `FORBIDDEN_ROLE`, `NOT_IN_COMPANY`, `COMPANY_INACTIVE`, `UNAUTHENTICATED`, and [[01-api]]'s attendance codes.
  - On `UNAUTHENTICATED` the page offers "Sign in again". The shared base query stays untouched in v1 (_mine_; `CLAUDE.md:88`).

## 6. Time zone

The server clock decides, and the API computes `ist_date` ([[01-api]]). Today the web formats in the browser's own zone (`src/methods/date.js:53-57`) and builds month windows from local midnight (`DecanList/decanList.js:82-99`). Attendance does neither:

1. **Days and months come from the API as strings.** `ist_date`, the register's days and `month` arrive as `YYYY-MM-DD` / `YYYY-MM` and are shown as given, never parsed into a `Date`.
2. **Instants are formatted by one helper that always names the zone.** These are punch times and audit times:

```js
const IST_TIME = new Intl.DateTimeFormat("en-IN", {
  timeZone: "Asia/Kolkata",
  hour: "2-digit",
  minute: "2-digit",
})
export const istTime = (iso) => IST_TIME.format(new Date(iso))
```

3. **The default month** is today's IST month, from the same helper, not `new Date().getMonth()`.
4. **Tests pin instants either side of IST midnight.** `18:29Z` must read as 23:59, and `18:31Z` as 00:01 the next day. They run with `TZ=UTC` set before Vitest starts, because changing the zone inside a running test is not reliable.

## 7. Export

- **The server builds the CSV** (`GET /attendance/register/export?month=YYYY-MM`, [[01-api]]). The web adds no CSV or spreadsheet library (none in `package.json:5-15`; new dependencies need approval, `CLAUDE.md:84`).
- **The download.** A plain link cannot carry the login and key headers.
  - A mutation-style call fetches the file, so it is never cached, with `responseHandler: "text"`.
  - The page wraps the text in a `Blob` (`text/csv;charset=utf-8`), clicks a temporary `<a download>` on an object URL, then revokes the URL.
- **The file name.** The web names the file `attendance-<dealer code>-<YYYY-MM>.csv`. Reading the server's name from another origin would need the API to expose `Content-Disposition`.
- **Ask of [[01-api]]:** start the CSV with a UTF-8 byte-order mark, so that Excel shows Hindi names correctly.
- **The CSV is personal data.** Nothing keeps it in the store or the browser after the download (privacy duties: [[04-platform-stores-and-law]]).
- **Test:** stub `URL.createObjectURL` / `revokeObjectURL` (jsdom has neither), then assert `month` and the file name.

## 8. Tests and gates

**New tests**, red first where behaviour changes ([[vsyst-technologies/docs/dip_web/tdd-testing-guide|web TDD guide]]; ro-web has no guide of its own yet):

- **Units:**
  - `isAttOwner`: DPrimary and DAdmin pass, read from the current membership row; every other dealer scope is refused; `dip.enabled` plays no part;
  - the IST helpers;
  - the Outlet "accurate enough" rule and the lat/lng checks;
  - the badge text for `per-use`, `window` and `UNAVAILABLE`;
  - the CSV file name;
  - the `error_code` map.
- **Route table:** every `/att_*` entry in `DEALER_ROUTES` (exported from `src/App.js`) carries the owner-only gate. It is the web's twin of the API's route-table test ([[01-api]]).
- **Sign-in:** no new rule, so no new test (§3).
- **One page test per page**, using `renderWithProviders` and `makeStoreWithUser` (`src/test/testUtils.js:12-38`). Happy paths come from fixtures, and refusals from `server.use(...)`. They cover:
  - a non-owner dealer user sees the denial;
  - a 403 `FORBIDDEN_ROLE` alert;
  - Staff: existing users listed with roster status, "Add to attendance" showing the code once, and "Remove from attendance" behind a confirm;
  - Devices: the `window` and `UNAVAILABLE` badges, approve behind its confirm, and no Approve on a manager's own phone;
  - `month=YYYY-MM` sent;
  - Outlet with stubbed `navigator.geolocation` and secure-context flag (jsdom has neither).

**MSW and fixtures.**

- **A v4 block in `src/test/msw/handlers.js`** (`*/api/v4/attendance/...`, with a wildcard origin as at `:18-31`). Unhandled requests still fail (`src/setupTests.js:59`).
- **Fixtures start hand-written:** `src/test/fixtures/att_*.json` plus factories.
- **Later, the fixture pull (_mine_).** Once the API exports attendance captures, `scripts/pull_fixtures.js` would also pull an allow-listed set from `fixtures/api_v4`. Today it reads only `fixtures/api_v3`, with a two-file allow-list (`:24`, `:32`). The API already produces `fixtures/api_v4` (api `package.json:16`).

**Gates** (unchanged):

- **Lint and tests:** `npx eslint src/ --ext .js,.jsx --max-warnings 0` (`.github/workflows/lint.yml:21-22`) and `yarn test` (`test.yml:23-24`). The suite stays within 1 minute (`docs/testing.md:171`; today 36 tests in 7 files, `:27`).
- **Commits and PRs:** subjects of 72 characters or fewer, in the imperative (`review-commits.yml:33-44`); commitlint; lint-staged; the PR checklist's screen-risk note for a new business flow (`.github/PULL_REQUEST_TEMPLATE.md:5-9`).
- **The split plan's gate** ([[vsyst-technologies/docs/dzzlo_ro_web/00-split-from-dip-web-plan|ro-web split plan]] §8):
  - zero word-gate hits in code;
  - no new dead file in the reachability run;
  - a browser smoke of every `DEALER_ROUTES` path, including the seven `/att_*` paths, at 320 px and on desktop (_mine_). Run it as DPrimary, as DAdmin, and as another dealer scope (for example DView), which must see no Attendance section and a denial on every `/att_*` path;
  - the user runs `yarn build` (`CLAUDE.md:83`).

**Docs that move with the code** (`docs/README.md:26-29`):

- `docs/architecture.md` (the Route Map; its `:47` is already out of date);
- `docs/auth-and-roles.md` (the owner-only attendance gate);
- `docs/rtk-query-conventions.md` (the v4 base; its base-URL lines `:21,34,123` are out of date too);
- `docs/testing.md`;
- a new ADR 0003, "attendance runs on v4".

## 9. The address (C‑9)

- **Not known yet** ("address coming soon"). Nothing shows that ro-web is deployed today (tasks_19 · 03 §1.3). No ro-web code names its own address, so the address is host configuration.
- **Domain root (the default) needs no change.**
  - There is no Vite `base` (`vite.config.js:4-22`) and no router `basename` (`src/index.js:31`).
  - The manifest uses `start_url: "."` (`public/manifest.json:21`).
  - The host serves `index.html` for every path (`CLAUDE.md:39`).
- **A sub-path (for example `/ro/`):**
  - set Vite `base` and the router `basename`;
  - check the manifest's `start_url` and `scope`, and the root-absolute links in `index.html:5,13,14`;
  - extend the host's catch-all to the sub-path.

  The `/att_*` paths are router-relative and need nothing.

- **HTTPS** is required by "Use my current location": browsers give location only to secure pages (confirmed in round 1, [[05-round-1-web-design]] §1).
  - `http://localhost:3001` counts as secure on the desktop.
  - A phone on the LAN over plain http does not. Try the Outlet page on the HTTPS staging host, or through a local HTTPS tunnel (_mine_).
- **Build settings.** The three `VITE_*` values (`src/constants/env.js:2-4`) live on the host. The production environment flag must be exact: see [[vsyst-technologies/docs/tasks/tasks_19_dip_web_superadmin_only/03-rollout-and-dealer-migration|tasks_19 · 03]] §7.1.
- **The API needs no change for the new origin** (tasks_19 · 03 §6).
- **No link carries the address.** The enrolment code is typed into the app. If the dealer's push should open this site, the address must reach the app or the API (Unknowns).

## 10. Dependencies that need approval

v1 needs none (`CLAUDE.md:84`):

- `Intl` and `navigator.geolocation` are built into the browser;
- the server builds the CSV;
- the enrolment code is typed, so no QR library is needed.

Each of these would need the user's OK later:

| Library                                      | For                                            | Note                                         |
| -------------------------------------------- | ---------------------------------------------- | -------------------------------------------- |
| a map library (e.g. Leaflet + react-leaflet) | a draggable pin on the Outlet location page    | also a tile provider's terms and attribution |
| a spreadsheet library (e.g. SheetJS)         | `.xlsx` instead of the server's CSV            | the server could produce `.xlsx` instead     |
| a QR library                                 | the enrolment code as a QR for the app to scan | the app would need a scanner ([[02-app]])    |

Server-side dependencies are C‑24 ([[01-api]]).

## Unknowns

1. **The address (C‑9).** Root or sub-path, HTTPS, the host, and the first deploy (tasks_19 · 03 OC‑2).
2. **Who manages: resolved by decision (C‑22, 2026-10-01).** In v1 only DPrimary and DAdmin manage, Audit included. Other dealer users come later, through a new guarded v4 grant route (§2).
3. **Self-approval (_mine_).** Managers may now be on the roster (C‑17). The rule "no one approves their own phone or request, except DPrimary, with an audit mark" needs [[00-overview]]'s OK and [[01-api]] to enforce it.
4. **`UNAVAILABLE` phones (C‑29).** Accept with a flag (recommended), or allow manual requests only. The Devices badge covers both answers.
5. **Adding someone who is not a DZZLO user.** v1 sends the dealer to the app's add-user flow. A guarded v4 "add user" command, with a ro-web button, is [[01-api]]'s proposal; fixes to the older routes are tasks_21.
6. **CSV:** the byte-order mark and the file name ([[01-api]]).
7. **Where the dealer's push opens:** an app screen or this site ([[02-app]]).
8. **Language (C‑10).** ro-web has no strings layer, so v1 is English.
9. **An expired login on v4.** Each page offers "Sign in again"; a global handler would touch the shared base query (`CLAUDE.md:88`).
10. **Reading quality.** A 30 m limit may be hard to meet indoors or from a desktop browser. The P0 pilot measures it.

## Sources

**ro-web** (`dzzlo_ro_web` `main` @ `5a66bf8`):

- **App shell:** `src/App.js:28-57, 100-193, 211-212, 243-250, 312-341`; `src/index.js:31`; `src/constants/env.js:2-4`.
- **Gates:** `src/routes/PermissionRoute.js:27-81`; `src/utils/permissions.js:29, 36-37`; `src/utils/Hooks/usePermissions.js:13-52`; `src/store/apis/dzzlooms/auth.js:13-28`.
- **Store:** `src/store/apis/createApi.js:6-22, 56, 79-87`; `src/store/dipApis/decants.js:25-62`.
- **UI:** `src/pages/personal/Dashboard.js:21-117`; `src/components/DashboardItem.js:8-104`; `src/components/Navbar/Navbar.js:130-168, 224-241`; `src/components/SVG/RNVI/MaterialIcons/index.js`.
- **Pages:** `src/pages/masters/index.js:65-73, 146-295`; `src/pages/masters/Users/users.js:79-82, 93-121`; `src/pages/transactions/shared.js:108-298`; `src/pages/transactions/DecanList/decanList.js:57-99, 281-298, 412-451`.
- **Helpers:** `src/utils/Hooks/useInfiniteScroll.js:17-56`; `src/utils/Hooks/useModal.js:3-8`; `src/utils/enums.js:1-5`; `src/methods/date.js:53-57`.
- **Tests:** `src/test/testUtils.js:12-38`; `src/test/msw/handlers.js:18-31`; `src/setupTests.js:59`; `src/pages/auth/SignIn/signin.test.js:50-219`; `src/App.test.js:36-55`; `scripts/pull_fixtures.js:24, 32`.
- **Build:** `vite.config.js:4-22`; `index.html:5-14`; `public/manifest.json:21`; `package.json:5-15`.
- **Repo docs:** `CLAUDE.md:32, 39, 57, 83-88`; `REVIEW.md:19-20`; `docs/README.md:26-29`; `docs/testing.md:27, 171`; `docs/rtk-query-conventions.md:21, 34, 123, 126`; `docs/architecture.md:47`.
- **CI:** `.github/workflows/lint.yml:21-22`, `test.yml:23-24`, `review-commits.yml:33-44`; `.github/PULL_REQUEST_TEMPLATE.md:5-9`.
- **RTK Query:** `node_modules/@reduxjs/toolkit/dist/query/rtk-query.modern.mjs:82-95` (RTK 2.11.2).

**api** (`dzzlo_oms_api` `slave` @ `86083ca`): `api_v4/lib/tenancy.js:42-54`; `api_v4/lib/respond.js:3-29`; `api_v4/lib/cursor.js:158-172`; `helpers/middlewares.js:45-57`; `package.json:16`.

**app** (`dzzlo_oms_app` `slave` @ `ea7e7222`): `src/store/apis/createApi.js:34-42`; `src/store/apis/v4/base.js:1-45`; `src/screens/Dealer/Users/index.js:373-389`; `src/screens/Dealer/Users/AddEditUsers.js:296-305`; `src/utils/Conditional/Scopes.js:99-182`; `src/navigation/Dealer/Main.js:337-349`.

**Vault:** [[vsyst-technologies/docs/dzzlo_ro_web/00-split-from-dip-web-plan|ro-web split plan]] §8; [[vsyst-technologies/docs/tasks/tasks_19_dip_web_superadmin_only/03-rollout-and-dealer-migration|tasks_19 · 03]] §1.3, §6, §7.1; [[05-round-1-web-design]] §1.

**Platform:**

- **Confirmed** (round 1, 2026-10-01; sources in [[05-round-1-web-design]]):
  - location is given only to secure (HTTPS) pages;
  - accuracy is reported in metres;
  - Chrome on Android lets users share approximate location per site.
- **Unclear** (standard browser APIs, not re-checked here):
  - `Intl.DateTimeFormat` `timeZone` — https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat
  - `URL.createObjectURL` — https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static
  - `window.isSecureContext` — https://developer.mozilla.org/en-US/docs/Web/API/Window/isSecureContext
  - Vite `base` — https://vite.dev/config/shared-options.html#base
  - RTK Query `responseHandler` — https://redux-toolkit.js.org/rtk-query/api/fetchBaseQuery
