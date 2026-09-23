---
title: dzzlo-ro-web — split from dip-web (dealer-only, no superadmin)
status: SHIPPED 2026-09-22 — commit b1bd990 on main + slave_dev, private repo https://github.com/ShikhaR-C/dzzlo-ro-web (user approved both); gate PASS
---

# dzzlo-ro-web — split from dip-web

**Status: BUILT 2026-09-22.** Folder `v1_79/dzzlo-ro-web` exists and passes the §8 gate (see §11). It has **no `.git`**, nothing is committed and nothing is on GitHub — the first commit and the GitHub repo both wait for the user's explicit word. The dev server was left running on http://localhost:3001 against the local API.

## 0. Summary

`dip-web` stays as the **superadmin console**. A new project, **`dzzlo-ro-web`**, is the
dealer-facing **RO DIP-METER** web app (decantation, meter reading, inspection, and the
dealer masters: products, tanks, DUs, nozzles, tanker trucks, users). It carries **no
superadmin page, endpoint file, route, role branch, login bypass, test, fixture or doc**.

The split is a *subtraction*, not a rewrite: copy the tracked tree at `slave_dev`
(23ac5b0), delete the superadmin set and everything only it used, edit the nine shared
files that branch on the superadmin role, re-point the login rule, fix the tests, rewrite
the docs. The dealer app is roughly 45 % of dip-web by lines.

| Bucket (src/, non-test .js, at 23ac5b0)                    | Files | Lines   |
| ----------------------------------------------------------- | ----- | ------- |
| Superadmin pages + `store/apis/sadmin` — **delete**         | 49    | 16,685  |
| Files only superadmin reaches, dead once it is cut — **delete** | 87 | 8,346   |
| Firebase (dead today) + `dzzlooms/cust_msts.js` (dead today) — **delete** (D7) | 3 | 192 |
| Dealer app — **keep**                                       | 121   | 20,428  |
| Test / MSW / fixtures / setup files — keep, 2 deleted, 2 rewritten | 13 | —   |

## 1. Decisions

| #   | Decision                                                                                                                                                                                            | Source                              |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| D1  | Name **`dzzlo-ro-web`** — folder `v1_79/dzzlo-ro-web`, `package.json` name, future GitHub repo `ShikhaR-C/dzzlo-ro-web`. Display name unchanged: tab title "RO DIP-METER", PWA name "DZZLO RO".   | user, 2026-09-22                    |
| D2  | **Fresh git history**: export tracked files, `git init -b main`, one first commit after the gate is green. dip-web keeps its history; no shared ancestry, no cross-repo cherry-picks.              | user                                |
| D3  | **Login = dealer role only, with a dev OTP bypass**: the two test dealer accounts (`dealer10@gmail.com`, `talentreasure2020@gmail.com`) skip OTP only when `PROJ_ENV !== "production"`; the two superadmin emails are removed; any role other than `dealer` is rejected at `transformResponse`. See §4. | user |
| D4  | **Web project only.** `dzzlo_oms_api` is not touched; it keeps serving both apps. Its CORS is `cors()` (open) and the same `x-api-key` works, so a new web origin needs no backend change.        | user                                |
| D5  | **Base = `slave_dev` tip 23ac5b0.** The two commits on `web_v4_foundations` (a80e467, 3b14992) are superadmin screen toggles and get deleted anyway, so the result is identical either way.        | mine — say so to change            |
| D6  | **Nothing goes to GitHub before explicit permission** — no `gh repo create`, no push, no PR. The first commit itself also waits for the user's word (house rule).                                 | user, 2026-09-22                    |
| D7  | **Firebase dropped.** Nothing outside `src/firebase/` imports it and `src/firebase/` is unreachable from `index.js`; the `firebase` dependency, `src/firebase/`, the eight `VITE_FIREBASE_*` vars, the `.env` shared-defaults file, and the unused `VITE_DEFAULT_DEALER` go. Not superadmin — say "keep Firebase" to keep it. | mine |
| D8  | **Endpoint rule inside shared files**: an endpoint whose only callers were superadmin pages is removed; endpoints a kept page calls stay; dealer-domain endpoints that no page calls yet (`auth_forgotPassword`, `auth_resetPassword`) stay. | mine |
| D9  | **`src/docs/` (dip-web's journals + plans) is not carried over.** It is dip-web's history; the new repo starts its own journal (`.agents/commands/journal.md` recreates the folder on first use). | mine — say so to carry it          |
| D10 | **Generated v3 fixture pipeline kept, allow-listed.** `scripts/pull_fixtures.js` copies only `auth_loginrx`, `auth_updaterx` + `fixtures.meta.json`; the OMS captures (`orders_poso`, `dealer_custs_list`, `invoices_list`, `vouchers_list`) are deleted and never pulled again. Alternative: drop the pipeline entirely. | mine |
| D11 | The hidden autofill on the "SIGN **IN**" heading (fills `talentreasure2020` + password) is gated by the same non-production rule as the OTP bypass.                                                | mine                                |
| D12 | Vite dev port **3001** so dip-web (3000) and dzzlo-ro-web can run side by side.                                                                                                                     | mine                                |
| D13 | Branch model mirrors dip-web: `main` (release) + `slave_dev` (integration), PRs target `slave_dev`. Both branches point at the first commit.                                                        | mine                                |
| D14 | In tests, the non-dealer role used for negative cases is `"user"`, so the finished repo contains **zero** occurrences of `superadmin` / `sadmin` (a grep gate, §8).                              | mine                                |

## 2. Inventory (dip-web at 23ac5b0)

### 2.1 Delete — superadmin (50 files, 16,916 lines, + 1 test)

- `src/pages/superadmin/**` — `customers/` (8), `dashboard/` (1), `db/` (4 + `AppFeatures.test.js`), `dealers/` (13), `drivers/` (2), `errlogs/` (1), `psocs/` (8), `users/` (3), `vehicles/` (2).
- `src/store/apis/sadmin/*` — `cust_msts`, `dealer_msts`, `dvr_msts`, `imp_actions`, `psocs`, `units_hsns`, `users`, `veh_msts` (8). Every URL they call is `/api/v3/...` (`sadmin/all/*`, `sadmin/actions/*`, `psocs/*`, `cust_msts`, `errors`, `notifs`, `users/a/sadmin`).

### 2.2 Delete — dead once superadmin is cut (87 files, 8,346 lines)

Computed by the reachability script in §2.5 (start at `src/index.js`, cut every edge into 2.1, list what is no longer reached). Re-run it at build time; do not trust this snapshot blindly.

- **Components**: `CardGrid/`, `Modal/` (the component — `utils/Hooks/useModal.js` stays), `Pickers/` (State + District + index), `ProgressSVG.js`, `SVG/psoc/ContainerShapes.js` (4,563 lines — `SVG/psoc/logo.js` and the seven oil-company logos stay, the Navbar uses them), `SVG/icons/close.js`.
- **Icon families** (`SVG/RNVI/`): all of `AntDesign/`, `Entypo/`, `FontAwesome/`, `FontAwesome5/`, `Fontisto/`, `MaterialCommunityIcons/`; `Feather/chevron-{down,left,right}.js`; `Ionicons/trash-outline.js`. Kept: `Custom/`, `Ionicons/refresh.js`, all of `MaterialIcons/`, `VsystIcons/`, `Zocial/`.
- **Store**: `dzzlooms/dealer_custs.js` (ledger, credit), `dzzlooms/invites.js`, `dzzlooms/others.js` (GST states / districts), `dzzlooms/prod_msts.js`, `dzzlooms/voc_msts.js` (vouchers).
- **Utils**: `credit.js`, `ledgerCheck.js` + `ledgerCheck.test.js`, `Hooks/useIsMobile.js`, `Hooks/useWindowSize.js`.
- **Docs**: `docs/mobile-list-patterns.md` (superadmin-only pattern).

### 2.3 Delete — other

- `src/firebase/index.js`, `src/firebase/methods.js`, the `firebase` dependency, `VITE_FIREBASE_*` and `VITE_DEFAULT_DEALER` in `.env.example` and `src/constants/env.js` (D7).
- `src/store/apis/dzzlooms/cust_msts.js` — unreachable today, customer master (OMS domain).
- `src/test/fixtures/generated/{orders_poso,dealer_custs_list,invoices_list,vouchers_list}.json` (D10).
- `src/docs/**` (D9).

### 2.4 Keep — the dealer app (121 files, 20,429 lines)

- **Shell**: `index.js`, `App.js` (edited), `NewApp.css`, `App.css`, `custom-theme.css`, `index.css`, `logo.svg`, `assets/fonts/*`, `constants/env.js` (edited).
- **Pages**: `auth/SignIn` (edited) + `auth/SignUp` (pre-existing, unrouted), `masters/*` (index, Products + importProds, Tanks, DUs, Nzls, TTs, Users + edit_user), `transactions/*` (Decan list/add/edit, MeterRead list/add/edit, Insps list/new/update, shared), `personal/{Dashboard (edited), Profile, Redux}`.
- **Components**: `Navbar/` (Navbar, Avatar, css), `CompanyScrollHint`, `ErrorBoundary/`, `NoNetworkBanner/`, `PullToRefresh/`, `Skeleton/`, `SVG/app/*` (tank drawings, wave), `SVG/dashboard/*` (nine dealer tiles; `Dealers.js` is already dead), `SVG/psoc/logo.js` + seven `*_HTML_SVG.js`, the kept icon families above, `Table/*` (pre-existing dead barrel, carried), new `components/DashboardItem.js` (lifted, §3.2).
- **Routes**: `PermissionRoute.js` (edited) + test.
- **Store**: `apis/createApi.js` (edited), `apis/index.js`, `dzzlooms/{auth (edited), dealer_msts (trimmed), users (trimmed)}.js`, `dipApis/{dealers,decants,insps,meter_reads}.js` (untouched — the whole `/api/dip/v1` surface), `slices/{auth,networkStatus}.js`.
- **Utils / methods**: `permissions.js` + test, `enums.js`, `refresh.js`, `reportWebVitals.js`, `socket.js` + `Hooks/useRealtimeInvalidation.js` (prepared, unused, carried), `Hooks/{themeContext,useInfiniteScroll,useModal,usePermissions (edited)}.js`, `StyleSheets/{index,cssVarSync}.js`, `methods/{colors,date,tank}.js`.
- **Test infra**: `setupTests.js`, `test/env/jsdom-fetch.js`, `test/msw/{server,handlers}.js`, `test/testUtils.js`, `test/fixtures/*.json` (+ `factories.js`, README), `test/fixtures/generated/{auth_loginrx,auth_updaterx,fixtures.meta}.json` + README.

### 2.5 Reachability script (run before and after the cut)

Put it in the scratchpad, point `ROOT` at the project's `src/`, run with `node`. Before the cut it must reproduce the counts in §0; after the cut its "dead once cut" list must be **empty** and its "already dead" list must equal the carried-over list in §10.

```js
// reach.js — import reachability over src/ with superadmin edges cut
const fs = require("fs"), path = require("path");
const ROOT = process.argv[2]; // .../dzzlo-ro-web/src  or  .../dip-web/src
const walk = (d) => fs.readdirSync(d, { withFileTypes: true }).flatMap((e) => {
  const p = path.join(d, e.name);
  return e.isDirectory() ? walk(p) : p.endsWith(".js") ? [p] : [];
});
const files = walk(ROOT);
const rel = (p) => path.relative(ROOT, p);
const isSA = (p) => /^(pages\/superadmin|store\/apis\/sadmin)\//.test(rel(p));
const isTest = (p) => /\.test\.js$|^test\/|^setupTests\.js$/.test(rel(p));
const resolve = (from, spec) => {
  if (!spec.startsWith(".")) return null;
  const base = path.resolve(path.dirname(from), spec);
  for (const c of [base, base + ".js", path.join(base, "index.js")])
    if (fs.existsSync(c) && fs.statSync(c).isFile()) return c;
  return null;
};
const RE = /(?:import|export)\s+(?:[^'"]*?\s+from\s+)?['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"]\s*\)|require\(\s*['"]([^'"]+)['"]\s*\)/g;
const edges = new Map();
for (const f of files) {
  const out = new Set();
  for (const m of fs.readFileSync(f, "utf8").matchAll(RE)) {
    const r = resolve(f, m[1] || m[2] || m[3]);
    if (r) out.add(r);
  }
  edges.set(f, out);
}
const reach = (start, cut) => {
  const seen = new Set(), st = [start];
  while (st.length) {
    const f = st.pop(); if (seen.has(f)) continue; seen.add(f);
    for (const t of edges.get(f) || []) if (!(cut && cut(t))) st.push(t);
  }
  return seen;
};
const entry = path.join(ROOT, "index.js");
const full = reach(entry, null), cutSet = reach(entry, isSA);
const nonTest = files.filter((f) => !isTest(f));
const loc = (f) => fs.readFileSync(f, "utf8").split("\n").length;
const show = (title, arr) => { console.log(`== ${title}: ${arr.length} files, ${arr.reduce((a, f) => a + loc(f), 0)} lines`); arr.forEach((f) => console.log("   ", rel(f), loc(f))); };
show("superadmin files", nonTest.filter(isSA));
show("dead once superadmin is cut", nonTest.filter((f) => full.has(f) && !cutSet.has(f) && !isSA(f)));
show("already dead today", nonTest.filter((f) => !full.has(f)));
show("kept (reachable after cut)", nonTest.filter((f) => cutSet.has(f)));
console.log("== edges from kept files INTO superadmin files (must be re-homed):");
for (const f of nonTest) if (!isSA(f)) for (const t of edges.get(f)) if (isSA(t)) console.log("   ", rel(f), "->", rel(t));
```

## 3. Edits in shared files

1. **`src/App.js`** — remove the 27 `SA*` lazy imports, `SUPERADMIN_ROUTES`, and the `user?.role === "superadmin"` branch (a non-dealer role now falls to `NotFound`, as other roles already do). `DEALER_ROUTES` untouched. In `tryLogin()`, add one guard: a stored session whose `userRole !== "dealer"` is logged out instead of restored, so no non-dealer session can ever be auto-restored.
2. **`src/pages/personal/Dashboard.js`** — it imports `DashboardItem` from `pages/superadmin/dashboard/index.js`. Lift `DashboardItem` (the exported tile: label button + optional "new" button, `fonts`/`colors` props) into **`src/components/DashboardItem.js`** unchanged, and import it from there. The only cross-edge from kept code into the superadmin tree.
3. **`src/routes/PermissionRoute.js`** — `isBypass` becomes `DIP_BYPASS_SCOPES.includes(user?.scope)` only; docblock line "DPrimary / DAdmin / superadmin always pass through" loses superadmin.
4. **`src/utils/Hooks/usePermissions.js`** — drop the two `if (user.role === "superadmin") return true;` lines and the docblocks that mention it. `getUserDipEnabled` is unchanged.
5. **`src/store/apis/dzzlooms/auth.js`** — `hasDipAccess` becomes the dealer rule in §4, applied in the `transformResponse` of both `auth_login` (loginrx, kept for the dev bypass) and `auth_loginOTP`. Two rejection messages. `updateCurr_User_Comp`, `auth_loginCredentialVerify`, `auth_forgotPassword`, `auth_resetPassword` stay (D8).
6. **`src/pages/auth/SignIn/index.js`** — `SUPERADMIN_EMAILS` → `DEV_OTP_BYPASS_EMAILS = ["dealer10@gmail.com", "talentreasure2020@gmail.com"]`; the direct-login branch runs only when `PROJ_ENV !== "production" && DEV_OTP_BYPASS_EMAILS.includes(email)` (`PROJ_ENV` from `constants/env.js`); `onHiddenClick` gated the same way (D11). Comments no longer say "superadmin".
7. **`src/store/apis/createApi.js`** — `tagTypes` shrinks to the six tags kept endpoint files reference: `decants`, `meter_reads`, `insps`, `dealers`, `users`, `dealer_msts`. Removed: `cust_msts`, `dvr_msts`, `veh_msts`, `psocs`, `hsncodes`, `units`, `errors`, `prod_msts`, `diesel_limit`, `dealer_custs`, `app_features`. `reducerPath: "dip-api"` unchanged (Redux dev page reads it).
8. **`src/store/apis/dzzlooms/dealer_msts.js`** — keep `fetch_sister_dealer_msts` and `switch_sister_dealer_msts` (Navbar); remove `update_dealer_msts`, `fetch_dealer_msts`, `fetch_one_psoc_by_dealerId`, `add_sister_dealer_msts` (superadmin callers only, D8).
9. **`src/store/apis/dzzlooms/users.js`** — keep `fetch_company_users` (Users master), `amend_prem` (edit_user), `set_theme` (Profile / theme); remove `add_users`, `update_users`, `activate_users`, `inactivate_users`, `remove_users`, `update_otp_manager`, `update_notify`, `reset_notify` (superadmin callers only, D8).
10. **`src/constants/env.js`** — drop the Firebase and `DEFAULT_DEALER` exports (D7).
11. **`package.json`** — `"name": "dzzlo-ro-web"`, `"version": "1.0.0"`, remove `firebase`; scripts unchanged. `yarn install` refreshes `yarn.lock`.
12. **`vite.config.js`** — `server.port: 3001` (D12); the Vitest block is unchanged.
13. **`.env.example`** — only `VITE_X_API_KEY`, `VITE_API_URL`, `VITE_PROJ_ENV`.
14. **`scripts/pull_fixtures.js`** — allow-list `["auth_loginrx", "auth_updaterx"]` + `fixtures.meta.json`; header comment names dzzlo-ro-web (D10).
15. **`index.html`, `public/manifest.json`** — unchanged ("RO DIP-METER", "DZZLO RO").

## 4. Login rule (D3)

Applied in `transformResponse` for `auth/loginrx` and `auth/loginOTP`:

```
role !== "dealer"                                   → throw "Only dealer accounts can sign in here"
role === "dealer" && scope ∈ {DPrimary, DAdmin}     → allow
role === "dealer" && current company allow ⊇ {"dip.enabled"} → allow
otherwise                                            → throw "DIP access not enabled for this user"   (existing text)
```

Which endpoint the page calls:

```
canBypassOtp = PROJ_ENV !== "production" && DEV_OTP_BYPASS_EMAILS.includes(email)
canBypassOtp  → POST auth/loginrx (email + password) → transformResponse rule above
otherwise     → POST auth/loginCredentialVerify → OTP input → POST auth/loginOTP → rule above
```

`PROJ_ENV` is `VITE_PROJ_ENV` (`development` | `testing` | `production`); Vitest injects `testing`, so the bypass is active in tests and one test flips it to `production` (T5). The list holds dealer test accounts only. The superadmin console keeps its own login in dip-web; a superadmin account is rejected here with the first message.

Not an access control: removing the UI does not remove API access. `/api/v3/sadmin/*` still answers any client with the key — that is the known v3 gap (protect/authorize on zero routes) tracked on the API side, unchanged by this plan.

## 5. Tests — red first, then green

Behaviour changes get a failing test before the edit (house TDD rule). On the freshly copied tree T3, T5 and T7 fail; §3 makes them pass.

| #   | File                                   | Test                                                                                                                                                         | Change    |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| T1  | `pages/auth/SignIn/signin.test.js`     | a dev-bypass test account signs in via `loginrx` with no OTP step (`PROJ_ENV=testing`) — rewrite of the superadmin direct-login test; fixture becomes a dealer | rewrite   |
| T2  | same                                   | dealer two-step OTP flow                                                                                                                                     | unchanged |
| T3  | same                                   | a non-dealer role (`"user"`, bypass scope, `dip.enabled` present) is rejected at `transformResponse` with "Only dealer accounts can sign in here"; nothing stored | **new, red first** |
| T4  | same                                   | a dealer without DIP access is rejected with "DIP access not enabled for this user" — retargeted to a bypass address (dealer)                                | edit      |
| T5  | same                                   | in `production` the bypass list is ignored: `vi.stubEnv("VITE_PROJ_ENV","production")` + `vi.resetModules()` + dynamic import; the bypass email goes to `loginCredentialVerify`, `loginrx` is never called | **new, red first** |
| T6  | same                                   | local validation before any endpoint                                                                                                                         | unchanged |
| T7  | `routes/PermissionRoute.test.js`       | replace "renders children for a superadmin" with: a non-dealer role gets no bypass — `role: "user"`, no perms → "DIP Access Not Enabled", children absent   | **replace, red first** |
| —   | `pages/superadmin/db/AppFeatures.test.js`, `utils/ledgerCheck.test.js` | deleted with their subjects                                                                                                                | delete    |
| —   | `test/fixtures/auth_loginrx.json`      | superadmin user → dealer `DPrimary` user, token `test-dealer-direct-token`                                                                                   | edit      |
| —   | `test/msw/handlers.js`                 | paths unchanged (`loginrx` handler stays for the bypass path); comment no longer says superadmin                                                             | comment   |

Expected after: **5 test files** (signin, PermissionRoute, permissions, networkStatus, errorRTK); the test count is re-baselined at build time (today: 7 files / 54 tests). Suite budget stays under one minute.

## 6. Docs inside the repo

- `CLAUDE.md` — project line: "DZZLO RO Web (RO DIP-METER) — dealer-facing DIP web app. No superadmin surface: that lives in dip-web." Remove the `Feature/` and `Welcome/` ghosts only if the line is touched anyway.
- `README.md` — title, structure tree without `superadmin/`, env table without `.env` (Firebase).
- `docs/project-overview.md` — Target Users without Superadmin; Entity Hierarchy without the Platform tier; drop "Superadmin Features".
- `docs/architecture.md` — tech stack (Vite, not CRA; no Firebase), folder tree, Data Flow step 2, Route Map: dealer + public only.
- `docs/auth-and-roles.md` — rewrite the login flow (OTP for all; dev bypass rule; the two rejection messages; roles table without superadmin; drop the stale "Only RO Admin Login" note that `signin.test.js` already flags).
- `docs/rtk-query-conventions.md` — remove the `sadmin/` section, the `sadmin` mentions in the base-URL and "where to add an endpoint" notes, and the superadmin merge-strategy line.
- `docs/component-patterns.md` — `useHasPermission` / `useIsDipEnabled` descriptions without superadmin; the `<Modal>` section now describes `useModal` + react-bootstrap `Modal` as the masters pages use it (the `components/Modal` component is gone).
- `docs/testing.md` — drop the AppFeatures worked example; fixtures section describes the allow-listed pull; template table already lists only kept files.
- `docs/README.md`, `docs/ci-code-review.md`, `REVIEW.md` — titles.
- `src/test/fixtures/README.md`, `src/test/fixtures/generated/README.md` — name + allow-list wording.
- **New `docs/adr/0002-no-superadmin-surface.md`** — why the split, what was removed, the login rule, that dip-web is the superadmin console, that the API is shared.
- Delete `docs/mobile-list-patterns.md`.
- `.agents/**`, `.github/**`, `.husky/**`, lint/prettier/commitlint configs, `.vscode/` — carried unchanged.

## 7. Repo, tooling, env, GitHub

- **Export, not copy**: `git -C dip-web archive slave_dev | tar -x -C dzzlo-ro-web` — tracked files at 23ac5b0 only (no `node_modules`, `build`, `.env*`, untracked junk).
- **Private env files**: `cp` `.env.development`, `.env.testing`, `.env.production` from dip-web into the new folder as-is (untracked, copied without being read; their Firebase lines are inert). `.env` (Firebase defaults) is not copied. `VITE_API_URL` / `VITE_X_API_KEY` stay the same — same API.
- `yarn install` after the `package.json` edit; `husky` `prepare` wires the hooks.
- **Git** (D2, D13): `git init -b main` at the end of the gate; **first commit only after the user's word**; then `git branch slave_dev`. Commit shape: the export + subtraction as one `chore(web): split dzzlo-ro-web from dip-web` commit, or red/green pairs for §5 on top — the user chooses when shown the diff.
- **GitHub** (D6): nothing until explicit permission. Then either the user creates the empty repo and gives me the URL, or permits `gh repo create ShikhaR-C/dzzlo-ro-web --private --source . --push`. `lint.yml` / `test.yml` / `review-commits.yml` need no secrets; the four `claude-*.yml.disabled` stay disabled.
- **Deployment** (later, user): new app on the host (BrowserRouter catch-all `index.html`), its own domain, the three `VITE_*` vars. No API change (open CORS, same key).

## 8. Gate — definition of done for the build

1. `grep -riE "superadmin|sadmin" .` (excluding `node_modules`, `yarn.lock`) → **zero** matches, code and docs alike (D14).
2. `node reach.js dzzlo-ro-web/src` → "dead once superadmin is cut" is empty; "superadmin files" is empty; the "already dead" list equals §10's carried-over list.
3. `yarn test` green (5 files); `npx eslint src/ --ext .js,.jsx --max-warnings 0` clean (what `lint.yml` runs).
4. `yarn start:test` boots on :3001 while dip-web can still run on :3000.
5. Browser smoke (I drive Chrome, or the user does): dealer two-step OTP login; `dealer10` direct login on the dev build; every `DEALER_ROUTES` path renders (`/`, `/product`, `/import_prod`, `/tank`, `/du`, `/nzl`, `/tt`, `/user`, `/edit_user`, `/decan`, `/new_decan`, `/edit_decan`, `/meter`, `/new_meter`, `/edit_meter`, `/insps`, `/new_insps`, `/edit_insps`, `/profile`); sister-company switch in the Navbar; theme change on Profile; logout; a superadmin login attempt shows "Only dealer accounts can sign in here".
6. `yarn build` is run by the user (house rule: never by AI); `build/assets` has no `Dlr*`, `Cust*`, `Psoc*`, `SA*` chunks.
7. A before/after size table (files, lines, bundle size) goes into this doc's BUILT note.

## 9. Execution

| Step | What                                                                                      | Who                    | Depends on |
| ---- | ----------------------------------------------------------------------------------------- | ---------------------- | ---------- |
| S0   | Export at 23ac5b0 into `v1_79/dzzlo-ro-web`, copy the three private env files, `yarn install` | me                 | "start"    |
| S1   | Delete §2.1 + §2.2 + §2.3; run `reach.js` to confirm; delete `src/docs/`                  | Sonnet builder B       | S0         |
| S2   | Edits §3 (1–15), `DashboardItem` lift                                                      | Opus builder A         | S1         |
| S3   | Tests §5: T3 / T5 / T7 red first, then green with S2; fixture + T1 / T4 edits              | Opus builder A         | S1 (same builder as S2) |
| S4   | Docs §6 + ADR 0002; `.env.example`; fixture READMEs; `pull_fixtures.js` allow-list        | Sonnet builder B       | S1 (parallel with S2/S3, disjoint files) |
| S5   | Gate §8 (1–5); collect the size table                                                      | me                     | S2–S4      |
| S6   | Show the user the diff summary → on a yes: `git init -b main`, first commit, `slave_dev`   | me, after the user's word | S5      |
| S7   | GitHub only on explicit permission (D6); this doc → BUILT; memory update                   | me, after permission   | S6         |

Builders work in the new folder itself (no git yet, so no worktree); A and B touch disjoint files. One session, two builders, roughly 1–2 hours wall clock. The reachability script and the grep gate are the two checks that make the subtraction verifiable rather than eyeballed.

## 10. Out of scope / follow-ups

- **dip-web itself**: the user keeps it as the superadmin console; removing its dealer pages is a separate plan, not started.
- **Carried over untouched, pre-existing dead code** (unreachable from `index.js` today; not superadmin): `pages/transactions/InspsAddEdit/inspsAdd.js` (1,150 lines) and `pages/transactions/InspsList/index.js` (1,325) — superseded by `inspsNew.js` / `insplist.js`; `pages/transactions/index.js` barrel; `components/Table/*`; `components/SVG/index.js`, `SVG/navIcons/hamburger.js`, `SVG/icons/{edit,trash}.js`, `SVG/dashboard/Dealers.js`; the unused icon files in `Feather/`, `Foundation/`, `Ionicons/` (all but `refresh`), `SimpleLineIcons/`; `utils/socket.js` + `Hooks/useRealtimeInvalidation.js` (prepared websocket); `pages/auth/SignUp` (linked from SignIn, no route). An optional sweep later — say so and it joins S1.
- **API-side access control**: superadmin routes stay reachable on the shared API (v3 gap); tracked with the API v4 work.
- **Vault TDD guide** for the new project: copy `docs/dip_web/tdd-testing-guide.md` with the allow-listed fixture difference — after the build.
- **`reducerPath: "dip-api"`**, the `dip-api.*` `ignoredPaths`, and the `dipApis/` folder name stay; renaming them is churn with no behaviour change.


## 11. BUILT — 2026-09-22 (gate record)

**Done as planned** (S0–S5). Export of dip-web `slave_dev` 23ac5b0 → `v1_79/dzzlo-ro-web`; private env files copied; package renamed `dzzlo-ro-web` 1.0.0, Firebase removed, `HUSKY=0 yarn install` (husky wires its hooks only once a `.git` exists → run `yarn prepare` after `git init`); S1 deletions; builder A (Opus) = §3 edits + §5 tests red-first; builder B (Sonnet) = §6 docs + ADR + `.env.example` + fixture allow-list.

| Gate §8 item | Result |
| --- | --- |
| 1 word gate | `src/`, config, scripts, `.github`, `public`: **zero** matches. Docs: only the allowed sentences (CLAUDE.md ×1, auth-and-roles ×1, project-overview Non-Goals ×1) + ADR 0002. |
| 2 reach script | superadmin 0 · deadOnceCut 0 · crossEdges 0 · kept **122 files / 20,198 lines** (121 + `components/DashboardItem.js`, minus the trimmed endpoint files) · alreadyDead 67 (= the §10 list + the six files restored below). |
| 3 tests / lint | `yarn test` **7 files / 36 tests** green (was 7/54 in dip-web, 5/32 right after S1) · `eslint --max-warnings 0` clean · Prettier clean on all 33 added/changed files (the tree has 120 pre-formatted-never files, dip-web has 125 — pre-existing). |
| 4 boot | `yarn start:dev` on **:3001**, dip-web's :3000 untouched. |
| 5 browser smoke | Chrome extension not connected → **Chrome for Testing 146 headless via CDP** (scratchpad `smoke.js`, zero deps): **27/27** — sign-in renders; dev autofill + Proceed → `auth/loginrx` only (no credVerify/OTP) → dealer session; dashboard tiles; all 20 `DEALER_ROUTES` paths render with the session kept and no console errors; `/dealers` → 404; a stored `userRole:"user"` session is dropped on load. Screenshots + `smoke-results.json` in `.device-runs/dzzlo-ro-web-split/smoke/`. Not exercised: sister-company switch and theme change (they write to the shared dev DB), a real superadmin login (no credentials; covered by test T3 with MSW). |
| 6 `yarn build` | not run (house rule: the user builds). |
| 7 size | `src/**/*.js` incl. tests and carried dead files: **333 → 202 files, 50,693 → 25,563 lines**. Diff vs the export: 4 added, 29 changed, 30 deleted entries (dirs collapsed). |

**Tests (red → green, logs in `.device-runs/dzzlo-ro-web-split/`):** T3 (non-dealer rejected even with dip.enabled) and T5 (production ignores the bypass list, own file `signin.production.test.js` with a `vi.mock` of `constants/env`) failed on the old code and pass after §3; the old "renders children for a superadmin" test failed after edit 3 (`red-permissionroute.log`) and was replaced by T7 ("gives a non-dealer role no bypass at all"); T8 added as `src/App.test.js` (non-dealer stored session dropped / dealer session restored). Test files now: signin (5), signin.production (1), PermissionRoute (6), App (2), permissions (11), networkStatus (5), errorRTK (6).

**Deviations from the plan, all small:**
- S1 was done by the orchestrator, not builder B, so both builders started from one consistent tree (no race on the superadmin files A had to read for the `DashboardItem` lift — A read them from the pristine export in the scratchpad).
- Six files the cut deleted are **restored** because carried-over dead files still import them: `SVG/RNVI/Feather/chevron-{down,left,right}.js`, `SVG/RNVI/Ionicons/trash-outline.js`, `SVG/icons/close.js`, `utils/Hooks/useWindowSize.js` (206 lines). Rule adopted: the split introduces no dangling import. dip-web already had three dangling imports inside dead files (`InspsList/index.js` → `utils/Navigation/Route` and `components/Modal/useModal`; `reportWebVitals.js` → itself); they are carried as-is.
- `src/test/msw/handlers.js` needed no edit (no superadmin wording; verified byte-identical). `AppFeatures.test.js` never existed at 23ac5b0 (it lives on `web_v4_foundations`).
- `docs/testing.md` count line updated by the orchestrator to 36 / 7 after both builders finished.
- The copied `.env.development` pointed at `http://192.168.101.38:8030`, unreachable on the current network; changed to the Mac's current address `http://192.168.29.174:8030` **in dzzlo-ro-web only** (dip-web's copy still has the old address).
- Vite logs "Failed to scan for dependencies … JSX syntax extension is not currently enabled" at start-up; identical in dip-web (the config uses `optimizeDeps.esbuild`, Vite 6 expects `optimizeDeps.esbuildOptions`); the app serves and runs regardless. Not fixed here.

**Numbers in the ADR** (49 files / 16,685 lines superadmin; 87 / 8,346 only-reachable-through-it; ≈121 / 20,428 kept) are the slave_dev export numbers; §0 above now matches them.

**Follow-ups (not done, for the user to call):**
1. **Dead-code sweep** — 67 files / 4,733 lines unreachable from `index.js` (the §10 list + the six restored files); includes `InspsAddEdit/inspsAdd.js` (1,150) and `InspsList/index.js` (1,325). One command once wanted.
2. `Navbar.js` reads `user.companies.length` unguarded (pre-existing; found by T8's seed).
3. `vite.config.js` `optimizeDeps.esbuild` → `optimizeDeps.esbuildOptions` (pre-existing, both repos).
4. dip-web `.env.development` still points at the stale LAN address.
5. `docs/ci-code-review.md` mentions HashRouter while the app uses BrowserRouter (pre-existing).
6. Prettier over the 120 never-formatted files (pre-existing; a formatting-only commit if wanted).
7. Vault: copy `docs/dip_web/tdd-testing-guide.md` for this project with the allow-listed fixture difference.

**Shipped 2026-09-22 (user chose "one commit" + "create private repo and push"):** `git init -b main`, husky wired (`yarn prepare`), single commit **b1bd990** `chore(web): split dzzlo-ro-web from dip-web (dealer-only)` made with `HUSKY=0` so lint-staged would not reformat the 120 never-formatted files into it (commit message checked with commitlint by hand); `slave_dev` at the same commit; private repo **https://github.com/ShikhaR-C/dzzlo-ro-web** created with `gh repo create --private --source=. --push`, `slave_dev` pushed too; default branch `main`. The superadmin code is nowhere in this repo's history. Still open: (c) this vault folder is uncommitted (the vault index also holds an unrelated modified file).
