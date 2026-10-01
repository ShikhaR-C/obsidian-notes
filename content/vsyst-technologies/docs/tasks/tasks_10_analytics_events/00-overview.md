# Plan: User-Activity Analytics + Error Tracing Instrumentation (DZZLO OMS App)

> **Companion to** `tasks_05_firebase/FIREBASE_ANALYTICS_PLAN.md`. That doc was the *pre-implementation* design (April 2026). The Firebase **infrastructure is now live** (see "Current State" below). This plan is the **instrumentation layer** — defining the event catalog and wiring real user-activity and error-tracing events into screens, the same way the reference app `app-kavana-l/src/config/events.ts` centralises its event names.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). ⬜ Not started in code — 0 of 4 phases: no `src/config/events.js`, no `track()`, no `setUserContext` / `logBreadcrumb`, `ErrorBoundary` still does not record (`src/components/Error/ErrorBoundary.js:127-133`), no source maps archived. The "Current State" base still holds (7 rows ✅) except its Remote Config wrappers, removed on 2026-09-27 (tasks_17), which also takes away this plan's `analytics_enabled` kill switch (`T10-N1`); the v2 screens add no events and cannot be told apart from v1 in analytics (`X-APP-4`). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

## Status roll-up (2026-10-01)

| Item | Status | What exists now (evidence) | What is left / next step |
| --- | --- | --- | --- |
| Current State (the base) | ✅ | wrappers `src/utils/firebase.js:8-74`; screen views `src/components/Error/RestartContext.js:31-45`; `rtkq_<endpoint>` trace + `api_call` `src/store/middleware/rtkQueryPerfLogger.js:21-43`; a non-fatal per rejected action `rtkQueryErrorLogger.js:63-73`; `setUser` `src/navigation/AppNavigatorContainer.js:98-103`; `tagEnv` + collection `:94-95`; the Remote Config pair removed (`ad40ed71`) | — |
| Phase 1 — catalogue + helpers | ⬜ | `src/config/events.js`, `src/utils/analytics.js`, `setUserContext` / `clearUserContext` / `logBreadcrumb` / `setScreenAttr`, `__tests__/events.test.js`: all absent (git grep: 0) | re-home the kill switch first (`T10-N1`) |
| Phase 2 — instrumentation | ⬜ | the only custom event is `api_call` (`rtkQueryPerfLogger.js:41-43`); 0 analytics calls under `src/screens/v2` and `src/components/v2` | add the two v2 screens to Slices D and F (`X-APP-4`) |
| Phase 3 — error tracing | ⬜ | `componentDidCatch` only `console.log`s (`ErrorBoundary.js:127-133`); no breadcrumbs, no custom keys beyond `proj_env` (`firebase.js:12`), no rejection tracker, no source-map archive; iOS still exports `APP_ENV=testing` (`project.pbxproj:291`); already there: JS-crash capture (`firebase.json`) and the crash-test buttons (`src/screens/Common/Settings/index.js:22,162-189`) | §3.1 first — render crashes in the v2 screens never reach Crashlytics today |
| Phase 4 — verification, kill switch, rollout | ⬜ | nothing to verify yet; the §4.3 Remote Config switch cannot be built (package removed); `AI.md` has no analytics section | `T10-N1`; console work is ❔ (the user) |

## Goal

1. **Track user activity** — every meaningful action (login, create order, record payment, generate invoice, export report, switch company, etc.) emits a named Firebase Analytics event with consistent params, so we can build funnels and usage dashboards per role.
2. **Trace errors & locate crashes efficiently** — every JS crash, render-boundary catch, API failure, and handled-but-notable error reaches Crashlytics, and we can pinpoint **what/where/who/how-to-repro** in a few clicks: readable `file:line` stacks (Hermes source maps), a filterable custom-key taxonomy (screen/role/company/build/endpoint), a breadcrumb repro trail, and deterministic grouping so one bug = one issue. Details in `03-phase-3`.

Non-goals: building dashboards in the Firebase console (separate ops task), notifications/FCM migration (covered by `tasks_05_firebase`), backend analytics.

---

## Reference pattern (what we're modelling on)

`app-kavana-l/src/config/events.ts` centralises analytics in one file:

- `FIREBASE_EVENTS` — a frozen `as const` map of `EVENT_KEY: 'event_name'` (snake_case `object_action` names).
- `screenSources` — canonical screen identifiers passed as a `source` param so the same event from different origins is distinguishable.
- `CTA_SOURCES` — named call-to-action origins.
- `EVENT_TRIGGERS` — thresholds for milestone events (e.g. "first 5 messages sent").
- Separate maps per provider (`FACEBOOK_EVENTS`).

We replicate this structure for the OMS domain in **`src/config/events.js`** (JS, not TS — per `AI.md` the app is JS despite the tsconfig).

---

## Current State (what already exists — do NOT rebuild)

| Capability | Where | Status | 2026-10-01 |
| --- | --- | --- | --- |
| Analytics/Crashlytics/Perf~~/RemoteConfig~~ wrappers | `src/utils/firebase.js` | ✅ `logEvent`, `logScreenView`, `setUser`, `logError`, `startHttpMetric`, `startTrace`, `tagEnv`, ~~`initRemoteConfig`, `getRemoteValue`~~ | ✅ seven wrappers (`firebase.js:8-74`); the Remote Config pair removed (`ad40ed71`, tasks_17) |
| Auto screen-view tracking | `src/components/Error/RestartContext.js` (`NavigationContainer.onReady` / `onStateChange` → `logScreenView`) | ✅ logs route name on every navigation | ✅ `RestartContext.js:31-45`; v1 and v2 share route names (`X-APP-4`) |
| Per-API perf trace + `api_call` event | `src/store/middleware/rtkQueryPerfLogger.js` | ✅ `rtkq_<endpoint>` trace + `api_call {endpoint, status}` — note `status` is the outcome `'ok'`/`'err'`, not an HTTP code | ✅ `rtkQueryPerfLogger.js:21-43`; still the only custom event |
| API failures → Crashlytics | `src/store/middleware/rtkQueryErrorLogger.js` | ✅ records `RTKQ <endpoint> rejected: <status>` | ✅ `rtkQueryErrorLogger.js:63-73`, every rejected action |
| `setUser(userId)` on auth | `AppNavigatorContainer.js` | ✅ sets Crashlytics + Analytics user id | ✅ `AppNavigatorContainer.js:98-103`; sets the id on sign-in only — clearing it on sign-out is Phase 1's `clearUserContext` |
| Env tagging + Crashlytics collection enabled | `AppNavigatorContainer.js` | ✅ `tagEnv()` (`firebase.js`) sets the `proj_env` user property / attribute; `setCrashlyticsCollectionEnabled(true)` is called directly in ~~`AppNavigatorContainer.js:65`~~ `AppNavigatorContainer.js:94` (not via `firebase.js`) | ✅ `AppNavigatorContainer.js:94-95` |
| Firebase deps installed | `package.json` (~~`@react-native-firebase/{app,analytics,crashlytics,perf,remote-config}@24.0.0`~~ `@react-native-firebase/{app,analytics,crashlytics,perf}@24.0.0`) | ✅ | ✅ four packages (`package.json:35-38`); remote-config removed 2026-09-27 |

### Gaps this plan closes

**Status (2026-10-01):** ⬜ all five still open: (1) only `api_call` (`rtkQueryPerfLogger.js:41-43`); (2) no user-action events; (3) `ErrorBoundary.js:127-133`; (4) `setUser` sets only the id (`src/utils/firebase.js:41-51`); (5) route-only names (`RestartContext.js:31-45`), which now also hide v1 vs v2 (`X-APP-4`).

1. **No central event catalog** — the only custom event emitted is `api_call`. No business events exist.
2. **No user-action instrumentation** — orders, payments, invoices, exports, auth funnel, filters, etc. emit nothing.
3. **Render crashes are dropped** — `ErrorBoundary.componentDidCatch` (`src/components/Error/ErrorBoundary.js:127`) `console.log`s the error; the `logError` call is **commented out** → JS render crashes never reach Crashlytics.
4. **Thin error context** — `setUser` sets only the id. `role`, `company_id`, current screen, and a breadcrumb trail are not attached, so a Crashlytics report can't tell which role/company/screen produced it.
5. **Screen-view names are route-only** — nested stacks across Dealer/Customer trees can collide and there's no `role` dimension on the screen event.

---

## Architecture of the solution

**Status (2026-10-01):** ⬜ none of it exists — no `src/config/events.js`, no `src/utils/analytics.js`, and `firebase.js` has none of the four new helpers.

```
src/config/events.js          ← NEW. The single source of truth (catalog).
src/utils/firebase.js         ← EXISTS. Add: setUserContext(), clearUserContext(),
                                 logBreadcrumb(), setScreenAttr(); extend
                                 logError(error, name). Existing callers unaffected.
src/utils/analytics.js        ← NEW (optional thin layer). track(EVENT, params)
                                 that injects default params (role, company_id,
                                 app_version) so call-sites stay one-liners.
```

Call-sites then read:

```js
import { EVENTS } from '../../config/events';
import { track } from '../../utils/analytics';

track(EVENTS.ORDER_CREATED, { order_type: 'sales', amount, dealer_id });
```

Cross-cutting dimensions (`role`, `company_id`, `app_version`) are injected **once** via `analytics().setDefaultEventParameters({...})` inside `setUserContext()` — Firebase then attaches them to **every** event automatically (including the existing `api_call`), so call-sites never repeat them and `track()` stays a thin wrapper. This is exactly how the reference app does it (`firebaseAnalytics.ts` → `setDefaultEventParameters({ tracking_firebase_uid, tracking_profile_user_id })`). `proj_env` stays a **user property** (set in `tagEnv`, already live). This mirrors the reference passing `source` everywhere, but centralises the cross-cutting dimensions rather than threading them per call.

> **Reference parity note:** `app-kavana-l` wraps analytics in a singleton class (`FirebaseAnalytics`) guarded by a build-time `REGISTER_EVENTS` flag plus a dev `analyticsLogger`. We get the equivalent with the existing `firebase.js` module + ~~a Remote-Config `analytics_enabled` flag (runtime, no rebuild)~~ _(2026-10-01: Remote Config left the app on 2026-09-27 — the switch needs a new home, `T10-N1`)_ + an optional `__DEV__` console log in `track()`. Same shape, less boilerplate.

---

## Event taxonomy (naming rules)

- **Format:** `snake_case`, `object_action` (e.g. `order_created`, `invoice_emailed`, `login_succeeded`). Matches the reference app and GA4 conventions.
- **Reserved-prefix safe:** never start a name with `firebase_`, `google_`, `ga_`.
- **Length limits (GA4):** event name ≤ 40 chars, param key ≤ 40, string value ≤ 100, ≤ 25 params/event. Keep names short.
- **Screen identifiers:** centralised in a `SCREENS` map (the reference `screenSources`) and passed as `source`/`screen` param, never free-typed.
- **Role dimension:** every event carries `role: 'dealer' | 'customer'` via the default-param injection — do not bake role into the event name (avoids `dealer_order_created` vs `customer_order_created` duplication).
- **IDs as params, not names:** `order_id`, `dealer_id`, `company_id` go in params; never interpolate ids into the event name (cardinality explosion).

### Proposed catalog (grouped — full list in `01-phase-1`)

**Status (2026-10-01):** ⬜ not built (Phase 1 §1.1).

| Group | Example events |
| --- | --- |
| App lifecycle | `app_opened`, `app_foregrounded`, `time_to_interactive` |
| Auth funnel | `auth_screen_viewed`, `login_attempted`, `login_succeeded`, `login_failed`, `otp_requested`, `otp_verified`, `otp_failed`, `forgot_password_submitted`, `logout` |
| Onboarding / validation | `validate_user_viewed`, `beta_user_submitted`, `company_selected` |
| Orders | `new_order_viewed`, `order_created`, `order_create_failed`, `order_status_changed`, `order_otp_verified`, `emergency_otp_used` |
| Sales orders (dealer) | `new_sales_order_viewed`, `sales_order_created`, `sales_order_edited` |
| Invoices | `new_invoice_viewed`, `invoice_created`, `invoice_emailed`, `invoice_rendered` |
| Payments / vouchers | `new_payment_viewed`, `payment_recorded`, `payment_failed`, `paytm_initiated`, `voucher_created`, `invoices_attached_to_payment` |
| Products / rates | `product_created`, `product_rate_set`, `product_dates_viewed` |
| Relations / credit | `dealer_added`, `customer_added`, `discount_set`, `credit_limit_changed`, `tcs_tds_settings_saved` |
| Vehicles | `vehicle_added`, `driver_added`, `driver_assigned`, `vehicle_request_created` (hire/rent via param) |
| Reports / renders | `report_viewed`, `daily_summary_viewed`, `account_statement_viewed` (with `format` param for Excel-format renders) |
| Company / users | `company_switched`, `sister_company_viewed`, `user_invited`, `invite_accepted`, `user_added` |
| Engagement / UX | `search_performed`, `filter_applied`, `theme_changed`, `pull_to_refresh`, `tab_switched` |
| Settings / account | `settings_viewed`, `delete_account_initiated`, `delete_account_confirmed` |
| Activation milestones | `first_order_created`, `first_invoice_created`, `first_payment_recorded` (via `EVENT_TRIGGERS`) |
| Error-adjacent | `error_boundary_triggered`, `api_error`, `network_lost`, `network_restored` |

> **Correction (2026-07-02 code audit):** the earlier draft also had `invoice_pdf_generated`, `invoice_downloaded`, `excel_exported`, `pdf_exported`, `codepush_checked`. All dropped: there is **no live client-side PDF/file-download/share path** in the app (`src/components/Download/` is dead code with zero importers; invoices/statements render as HTML in a WebView — see Phase 2 §2.3/§2.4), and `react-native-code-push` is **not** in `package.json` (`Settings/Codepush.js` is unreferenced). `invoice_rendered {format}` replaces the invoice PDF/download events; re-add export/CodePush events only if those features ship. `api_error` added so Phase 3's middleware event has a catalog entry.

---

## User properties (set once, queryable as dimensions)

**Status (2026-10-01):** ⬜ only `proj_env` is set (`src/utils/firebase.js:12-13`); the selectors named below exist (`src/store/selectors/auth.js:6-8,21,24,27`) and `react-native-device-info` is still a dependency (`package.json:50`).

Set via `analytics().setUserProperty` + `crashlytics().setAttribute` in `setUserContext()`. **All source selectors already exist** in `src/store/selectors/auth.js` — no new selectors needed:

| Property | Source selector (exists) | Why |
| --- | --- | --- |
| `proj_env` | `PROJ_ENV` (already set in `tagEnv`) | filter dev/test noise |
| `role` | `selectUserRole` (`auth.user?.role`) | per-role funnels & crash slicing |
| `company_id` | `selectCompanyId` (`auth.company?._id`) | multi-tenant slicing |
| `app_version` | `react-native-device-info` `getVersion()` | regression triage |
| `account_verified` | `selectCompanyDealerVerified` / `selectCompanyCustVerified` (role-appropriate) | verified vs unverified behaviour |
| `scope` *(optional)* | `selectUserScope` (`auth.user?.scope`) | permission-tier slicing |

> ⚠️ There is **no** `selectUserStatus`/`user_status` on the user object (the earlier draft assumed one). `constants/userStatus.js` (`ACTIVE`/`INACTIVE`/`REMOVED`) describes *company-membership* status surfaced via the 403 `COMPANY_BLOCK_CODES` flow, not a per-user analytics dimension. Use the `*_verified` flags above for the "is this an established account" cut.

---

## Phases

| Phase | File | Outcome |
| --- | --- | --- |
| 1 | `01-phase-1-events-catalog-and-helpers.md` | `src/config/events.js` catalog + `track()` helper + extend `firebase.js` (`setUserContext`, `logBreadcrumb`). No screen edits yet — fully shippable. |
| 2 | `02-phase-2-user-activity-instrumentation.md` | Wire events at auth, orders, invoices, payments, reports/renders, company-switch, search/filter. Role-by-role rollout. |
| 3 | `03-phase-3-error-tracing.md` | **Locate crashes efficiently:** fix `ErrorBoundary` → Crashlytics (named grouping), Hermes **source maps** for readable stacks, custom-key taxonomy, breadcrumbs, unhandled-rejection capture, richer error context. |
| 4 | `04-phase-4-verification-rollout.md` | DebugView verification, kill-switch via Remote Config, QA checklist, dashboards handoff. |

Each phase is independently shippable; stop after any phase and still have value (per the workspace convention in `tasks_05_firebase`).

---

## Risks / gotchas

**Status (2026-10-01):** still valid, with two changes: `getRemoteValue` no longer exists (struck below) and the Remote Config kill switch cannot be built as written (`T10-N1`); the iOS `APP_ENV=testing` hardcode is still there (`ios/dzzlo_oms_app.xcodeproj/project.pbxproj:291`).

- **No PII in events/params.** No names, phone numbers, emails, addresses. Use ids only. (Firebase ToS + privacy.)
- **Don't double-count screen views.** Auto tracking already fires `logScreenView` in `RestartContext.js`. Do **not** add manual `*_screen_viewed` events that duplicate it — prefer enriching the existing screen-view call (Phase 3) or only add `*_viewed` events for sub-views that aren't navigation routes (bottom sheets, modals).
- **Event volume / cost.** GA4 free tier is generous but avoid high-frequency events (scroll, keystroke). Throttle `search_performed` to submit, not per-keystroke.
- **Async fire-and-forget.** Most wrappers already swallow errors — but not all: `startHttpMetric`, `startTrace`, ~~`getRemoteValue`~~ have **no** try/catch (`track()` wraps its own `getRemoteValue` call, so it's safe). Never `await` analytics on a hot path (`track()` returns a non-blocking promise).
- **Remote Config kill-switch.** Gate `track()` behind an `analytics_enabled` Remote Config flag (default true) so we can disable instrumentation in prod without a release. Note it **fails open** by design (flag unreadable → analytics on).
- **Clear identity on logout / account deletion.** `setUserContext` fires on login + company switch, but default event params, user properties and the analytics/Crashlytics user id **persist after logout** — the next session on the device (or a deleted account) keeps being attributed to the old user/tenant. Phase 1 adds `clearUserContext()`; Phase 2 wires it on auth reset (manual logout, 401 auto-logout, `delete_account_confirmed`).
- **iOS builds currently hardcode `APP_ENV=testing`** in the Xcode "Bundle React Native code and images" phase (`project.pbxproj`), so `proj_env` will misclassify iOS telemetry until that's fixed (Phase 3 §3.7 touches that build phase; Phase 4 §4.1 has the verification caveat).
- **Store disclosures.** Setting an analytics user id + `role`/`company_id` properties means updating the Google Play Data Safety form and App Store privacy declarations (analytics + crash data linked to an identifier) — Phase 4 §4.6.

## New tasks — from the app v2 / API v4 review (2026-10-01)

| ID | Task | Why (evidence) | Project | Size | Depends on |
| --- | --- | --- | --- | --- | --- |
| X-APP-4 | 🆕 Let analytics tell a v1 render from a v2 render, and give the v2 screens their own events | Screen views log the route name only (`src/components/Error/RestartContext.js:31-45`), and v1 and v2 share it — `Customers` and `DailySummary` resolve through `resolveScreen` under one name (`src/navigation/Dealer/Main.js:53,63,175-176,203-204`; `src/navigation/Customer/Main.js:50,205-206`); `src/screens/v2` and `src/components/v2` make 0 analytics calls; the only custom event is `api_call` (`src/store/middleware/rtkQueryPerfLogger.js:41-43`). The redesign playbook's 7-day watch ("Crashlytics for the v2 screen", `oms_app/screen-redesign/03-per-screen-playbook.md:100`) and any toggle-rollback decision need it; endpoint p95 and error rate already exist client-side (`rtkq_v4_screen_*` traces, `api_call {endpoint}`) | app | S | the screen-view part stands alone; the events need Phase 1; crash attribution needs Phase 3 §3.1 + §3.7 |
| T10-N1 | 🆕 Re-home the analytics kill switch, or drop it | Phase 1 §1.3 and Phase 4 §4.3 read `analytics_enabled` through `getRemoteValue`, removed with Remote Config (`ad40ed71`, tasks_17); the D10 toggle map cannot carry it — screen keys and booleans only (API `helpers/appFeatures.js:31-38`) | app (+ API) | S | `T09-N1` (tasks_09) |
