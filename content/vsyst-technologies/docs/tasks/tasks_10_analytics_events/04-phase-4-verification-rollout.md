# Phase 4 — Verification, Kill-switch & Rollout

**Outcome:** events are confirmed flowing in Firebase, instrumentation can be disabled remotely without a release, and the team has a QA checklist + dashboard handoff.

---

## 4.1 Verify with Firebase DebugView (per slice, before merge)

DebugView shows events in near-real-time for a single device — the fastest way to confirm names/params before they pollute prod.

**Enable debug mode:**

```sh
# Android
adb shell setprop debug.firebase.analytics.app in.vsyst.dzzlooms
# iOS: add launch arg -FIRDebugEnabled (Xcode scheme > Run > Arguments)
```

Then: Firebase Console → Analytics → **DebugView**, exercise the flow, confirm:
- event name matches `EVENTS` value exactly,
- params present and typed correctly (numbers are numbers),
- `role` default param attached,
- no PII in any field.

**Disable when done:**
```sh
adb shell setprop debug.firebase.analytics.app .none
```

> Use `APP_ENV=testing` builds for verification so `proj_env=testing` keeps this out of prod reporting.

---

## 4.2 Register events & params in GA4 (console, ops task)

- Mark key events as **conversions**: `order_created`, `invoice_created`, `payment_recorded`, `login_succeeded`, the three `first_*` milestones.
- Register **custom dimensions** for params you'll segment by: `role`, `company_id`, `report_type`, `order_type`, `request_type`. (GA4 won't break them out in reports until registered.)
- Register **user properties**: `role`, `company_id`, `app_version`, `user_status`, `proj_env`.

---

## 4.3 Remote Config kill-switch (already plumbed in Phase 1)

`track()` checks `analytics_enabled` (default `true`). To silence analytics in prod without a release: Firebase Console → Remote Config → set `analytics_enabled = false` → Publish. Verify `getRemoteValue('analytics_enabled')` reflects it after the next `fetchAndActivate` (hourly in prod per `firebase.js`).

Consider a parallel `crashlytics_enabled` flag if you want the same control over error reporting (wire into `setCrashlyticsCollectionEnabled`).

---

## 4.4 QA regression checklist (run on a testing build)

- [ ] Login (password + OTP) → `login_*` / `otp_*` events; `setUserContext` sets role/company.
- [ ] Create order / sales order → `order_created` / `sales_order_created` (+ `first_order_created` once).
- [ ] Create + email + PDF invoice → `invoice_created`, `invoice_emailed`, `invoice_pdf_generated`.
- [ ] Record payment → `payment_recorded` (+ `first_payment_recorded` once).
- [ ] Export Excel/PDF report → `excel_exported` / `pdf_exported`.
- [ ] Switch company → `company_switched` + subsequent events carry new `company_id`.
- [ ] Search/filter → fire on submit only, not per keystroke.
- [ ] Force render crash → `error_boundary_triggered` + Crashlytics non-fatal grouped under `ReactRenderError`, with `screen`, `role`, `company_id`, `app_build` keys.
- [ ] `crashlytics().crash()` (dev button) → fatal in console with attributes + breadcrumb trail.
- [ ] **Symbolication:** take the raw Hermes stack from that crash, run `metro-symbolicate <map-for-app_build> < stack.txt`, confirm it resolves to a real `src/**.js:line`. (This is the "locate crashes efficiently" acceptance gate.)
- [ ] Native symbols present: Android mapping uploaded for the release build; iOS dSYM uploaded (Crashlytics console shows no "missing dSYM" warning).
- [ ] Kill app, reopen offline → `network_lost` then `network_restored`; `api_error` on failed calls.
- [ ] Toggle `analytics_enabled=false` → no new analytics events (Crashlytics still works).
- [ ] `yarn test` + `yarn lint` clean.

---

## 4.5 Dashboards handoff (ops, post-merge)

Once events flow for a few days, build in GA4 / Looker Studio:
- **Activation funnel:** `login_succeeded` → `first_order_created` → `first_invoice_created` → `first_payment_recorded`, split by `role`.
- **Daily active by role / company.**
- **Feature usage:** exports, vehicle requests, search.
- **Reliability:** `api_error` rate by `endpoint`; Crashlytics crash-free-users by `role`/`app_version`.

---

## 4.6 Documentation & maintenance

- Add a short "Analytics" section to `AI.md`: "All analytics go through `src/config/events.js` + `track()`. Never call `analytics().logEvent` directly in screens. No PII in params."
- PR-review rule: any new event name must land in `EVENTS` (catalog test enforces validity).
- Keep this folder as the living spec; tick checklists as slices ship.

---

## Definition of done (whole task)

- [ ] Phases 1–3 merged; `__tests__/events.test.js` green.
- [ ] All Phase-2 slices verified in DebugView; conversions + dimensions registered in GA4.
- [ ] Render crash + fatal crash confirmed in Crashlytics with full context.
- [ ] Kill-switch verified.
- [ ] `AI.md` updated with the analytics convention.
