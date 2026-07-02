# Plan: User-Activity Analytics + Error Tracing Instrumentation (DZZLO OMS App)

> **Companion to** `tasks_05_firebase/FIREBASE_ANALYTICS_PLAN.md`. That doc was the *pre-implementation* design (April 2026). The Firebase **infrastructure is now live** (see "Current State" below). This plan is the **instrumentation layer** — defining the event catalog and wiring real user-activity and error-tracing events into screens, the same way the reference app `app-kavana-l/src/config/events.ts` centralises its event names.

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

| Capability | Where | Status |
| --- | --- | --- |
| Analytics/Crashlytics/Perf/RemoteConfig wrappers | `src/utils/firebase.js` | ✅ `logEvent`, `logScreenView`, `setUser`, `logError`, `startHttpMetric`, `startTrace`, `tagEnv`, `initRemoteConfig`, `getRemoteValue` |
| Auto screen-view tracking | `src/components/Error/RestartContext.js` (`NavigationContainer.onReady` / `onStateChange` → `logScreenView`) | ✅ logs route name on every navigation |
| Per-API perf trace + `api_call` event | `src/store/middleware/rtkQueryPerfLogger.js` | ✅ `rtkq_<endpoint>` trace + `api_call {endpoint, status}` — note `status` is the outcome `'ok'`/`'err'`, not an HTTP code |
| API failures → Crashlytics | `src/store/middleware/rtkQueryErrorLogger.js` | ✅ records `RTKQ <endpoint> rejected: <status>` |
| `setUser(userId)` on auth | `AppNavigatorContainer.js` | ✅ sets Crashlytics + Analytics user id |
| Env tagging + Crashlytics collection enabled | `AppNavigatorContainer.js` | ✅ `tagEnv()` (`firebase.js`) sets the `proj_env` user property / attribute; `setCrashlyticsCollectionEnabled(true)` is called directly in `AppNavigatorContainer.js:65` (not via `firebase.js`) |
| Firebase deps installed | `package.json` (`@react-native-firebase/{app,analytics,crashlytics,perf,remote-config}@24.0.0`) | ✅ |

### Gaps this plan closes

1. **No central event catalog** — the only custom event emitted is `api_call`. No business events exist.
2. **No user-action instrumentation** — orders, payments, invoices, exports, auth funnel, filters, etc. emit nothing.
3. **Render crashes are dropped** — `ErrorBoundary.componentDidCatch` (`src/components/Error/ErrorBoundary.js:127`) `console.log`s the error; the `logError` call is **commented out** → JS render crashes never reach Crashlytics.
4. **Thin error context** — `setUser` sets only the id. `role`, `company_id`, current screen, and a breadcrumb trail are not attached, so a Crashlytics report can't tell which role/company/screen produced it.
5. **Screen-view names are route-only** — nested stacks across Dealer/Customer trees can collide and there's no `role` dimension on the screen event.

---

## Architecture of the solution

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

> **Reference parity note:** `app-kavana-l` wraps analytics in a singleton class (`FirebaseAnalytics`) guarded by a build-time `REGISTER_EVENTS` flag plus a dev `analyticsLogger`. We get the equivalent with the existing `firebase.js` module + a Remote-Config `analytics_enabled` flag (runtime, no rebuild) + an optional `__DEV__` console log in `track()`. Same shape, less boilerplate.

---

## Event taxonomy (naming rules)

- **Format:** `snake_case`, `object_action` (e.g. `order_created`, `invoice_emailed`, `login_succeeded`). Matches the reference app and GA4 conventions.
- **Reserved-prefix safe:** never start a name with `firebase_`, `google_`, `ga_`.
- **Length limits (GA4):** event name ≤ 40 chars, param key ≤ 40, string value ≤ 100, ≤ 25 params/event. Keep names short.
- **Screen identifiers:** centralised in a `SCREENS` map (the reference `screenSources`) and passed as `source`/`screen` param, never free-typed.
- **Role dimension:** every event carries `role: 'dealer' | 'customer'` via the default-param injection — do not bake role into the event name (avoids `dealer_order_created` vs `customer_order_created` duplication).
- **IDs as params, not names:** `order_id`, `dealer_id`, `company_id` go in params; never interpolate ids into the event name (cardinality explosion).

### Proposed catalog (grouped — full list in `01-phase-1`)

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

- **No PII in events/params.** No names, phone numbers, emails, addresses. Use ids only. (Firebase ToS + privacy.)
- **Don't double-count screen views.** Auto tracking already fires `logScreenView` in `RestartContext.js`. Do **not** add manual `*_screen_viewed` events that duplicate it — prefer enriching the existing screen-view call (Phase 3) or only add `*_viewed` events for sub-views that aren't navigation routes (bottom sheets, modals).
- **Event volume / cost.** GA4 free tier is generous but avoid high-frequency events (scroll, keystroke). Throttle `search_performed` to submit, not per-keystroke.
- **Async fire-and-forget.** Most wrappers already swallow errors — but not all: `startHttpMetric`, `startTrace`, `getRemoteValue` have **no** try/catch (`track()` wraps its own `getRemoteValue` call, so it's safe). Never `await` analytics on a hot path (`track()` returns a non-blocking promise).
- **Remote Config kill-switch.** Gate `track()` behind an `analytics_enabled` Remote Config flag (default true) so we can disable instrumentation in prod without a release. Note it **fails open** by design (flag unreadable → analytics on).
- **Clear identity on logout / account deletion.** `setUserContext` fires on login + company switch, but default event params, user properties and the analytics/Crashlytics user id **persist after logout** — the next session on the device (or a deleted account) keeps being attributed to the old user/tenant. Phase 1 adds `clearUserContext()`; Phase 2 wires it on auth reset (manual logout, 401 auto-logout, `delete_account_confirmed`).
- **iOS builds currently hardcode `APP_ENV=testing`** in the Xcode "Bundle React Native code and images" phase (`project.pbxproj`), so `proj_env` will misclassify iOS telemetry until that's fixed (Phase 3 §3.7 touches that build phase; Phase 4 §4.1 has the verification caveat).
- **Store disclosures.** Setting an analytics user id + `role`/`company_id` properties means updating the Google Play Data Safety form and App Store privacy declarations (analytics + crash data linked to an identifier) — Phase 4 §4.6.
