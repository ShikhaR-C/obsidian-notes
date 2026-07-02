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
>
> ⚠️ **iOS caveat (2026-07-02 audit):** the Xcode "Bundle React Native code and images" phase currently **hardcodes `export APP_ENV=testing`** (`project.pbxproj:291`). Until that's fixed (Phase 3 §3.7 touches this phase), iOS builds report `proj_env=testing` regardless of the intended env — so `proj_env`-based prod/test filtering is unreliable on iOS.

---

## 4.2 Register events & params in GA4 (console, ops task)

- Mark key events as **conversions**: `order_created`, `invoice_created`, `payment_recorded`, `login_succeeded`, the three `first_*` milestones.
- Register **custom dimensions** for params you'll segment by: `role`, `company_id`, `report_type`, `order_type`, `request_type`. (GA4 won't break them out in reports until registered.)
- Register **user properties**: `role`, `company_id`, `app_version`, `account_verified`, `scope`, `proj_env`. *(Correction: the earlier draft said `user_status` — no such field exists on the user; see the 00-overview user-properties table.)*

---

## 4.3 Remote Config kill-switch (already plumbed in Phase 1)

`track()` checks `analytics_enabled` (default `true`). To silence analytics in prod without a release: Firebase Console → Remote Config → set `analytics_enabled = false` → Publish. Verify `getRemoteValue('analytics_enabled')` reflects it after the next `fetchAndActivate` (hourly in prod per `firebase.js`).

Consider a parallel `crashlytics_enabled` flag if you want the same control over error reporting (wire into `setCrashlyticsCollectionEnabled`).

---

## 4.4 QA regression checklist (run on a testing build)

- [ ] Login (password + OTP) → `login_*` / `otp_*` events; `setUserContext` sets role/company.
- [ ] Create order / sales order → `order_created` / `sales_order_created` (+ `first_order_created` once).
- [ ] Create + email + render invoice → `invoice_created`, `invoice_emailed`, `invoice_rendered` (with the correct `format` param).
- [ ] Record payment → `payment_recorded` (+ `first_payment_recorded` once).
- [ ] View account statement in Excel format → `account_statement_viewed {format: 'Excel'}`. *(No file-export events — see the Phase 2 §2.4 correction.)*
- [ ] Switch company → `company_switched` + subsequent events carry new `company_id`.
- [ ] Logout → `logout {trigger}` fires, then `clearUserContext()`: subsequent events/crashes carry **no** user id, `role`, or `company_id` (verify in DebugView).
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
- **Feature usage:** invoice/statement renders (`invoice_rendered`, `account_statement_viewed` by `format`), vehicle requests, search.
- **Reliability:** `api_error` rate by `endpoint`; Crashlytics crash-free-users by `role`/`app_version`.

---

## 4.6 Documentation & maintenance

- Add a short "Analytics" section to `AI.md`: "All analytics go through `src/config/events.js` + `track()`. Never call `analytics().logEvent` directly in screens. No PII in params."
- PR-review rule: any new event name must land in `EVENTS` (catalog test enforces validity).
- **Store disclosures:** setting the analytics user id + `role`/`company_id` properties means updating the Google Play **Data Safety** form and App Store **privacy** declarations (analytics + crash data linked to a user identifier).
- Keep this folder as the living spec; tick checklists as slices ship.

---

## Definition of done (whole task)

- [ ] Phases 1–3 merged; `__tests__/events.test.js` green.
- [ ] All Phase-2 slices verified in DebugView; conversions + dimensions registered in GA4.
- [ ] Render crash + fatal crash confirmed in Crashlytics with full context.
- [ ] Kill-switch verified.
- [ ] `AI.md` updated with the analytics convention.
