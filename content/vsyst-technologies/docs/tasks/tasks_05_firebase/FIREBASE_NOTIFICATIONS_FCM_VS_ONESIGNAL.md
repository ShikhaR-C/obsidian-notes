# Notifications: FCM + Firebase In-App Messaging vs OneSignal

> Companion to `FIREBASE_INTEGRATION_PLAN.md` and `FIREBASE_ANALYTICS_PLAN.md`. The integration plan mentions "Cloud Messaging (FCM) — could replace OneSignal." This doc answers: **can it actually?** Short answer — yes for basic push, but you lose meaningful features. Use this to decide whether to drop, keep, or run both.

---

## TL;DR

**FCM + Firebase In-App Messaging (FIAM) can replace OneSignal for basic push + in-app messaging, but you'll lose meaningful features.** Only drop OneSignal if you're confident you don't need the items below.

---

## What FCM + FIAM cover well

- Raw push delivery to Android/iOS (FCM is the transport OneSignal itself uses on Android).
- Topic subscriptions, per-device tokens, scheduled sends.
- In-app banners/modals/cards triggered by Firebase Analytics events or user properties (FIAM).
- Audience targeting via Firebase user properties + Analytics events.
- Free at any scale.

## What OneSignal is genuinely better at

| Area                           | OneSignal edge                                                                                                                                                        |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dashboard / UX**             | Non-technical users (ops, support) can compose, segment, schedule, and A/B test without a Firebase console tour or BigQuery.                                          |
| **Segmentation**               | Rich built-in segment builder (tags, last-session, location, language, custom filters). FCM makes you build audiences out of Analytics properties, which is clunkier. |
| **Delivery reporting**         | Per-notification sent / delivered / clicked / converted funnel out of the box. FCM reports only _sent_; you wire click/convert yourself via Analytics.                |
| **Journeys / automation**      | Drip sequences, re-engagement workflows, time-of-day optimization, intelligent delivery. FIAM/FCM have none of this — you'd build it with Cloud Functions.            |
| **Multi-channel**              | Email, SMS, web push, in-app, live activities under one audience. Firebase is push + in-app only.                                                                     |
| **Per-user subscription mgmt** | External-user-id mapping, opt-out UI helpers, GDPR tooling — all ready.                                                                                               |
| **iOS specifics**              | Better out-of-the-box Notification Service Extension (rich media, mutable content, confirmed delivery).                                                               |
| **Templating**                 | WYSIWYG template editor with variables, localization, preview devices.                                                                                                |

---

## Rule of thumb for DZZLO OMS

- **Transactional-only notifications** (new order, payment received, invoice approved) composed by devs in code → **drop OneSignal**, use FCM + FIAM, save the dependency.
- **Ops / support ever want to blast segments, run campaigns, or see click-through** without engineering help → **keep OneSignal.** Still enable FCM for Analytics-triggered in-app messages (they don't overlap).

### Pragmatic compromise — run both

They don't conflict on either platform:

- **iOS**: OneSignal owns the APNs connection for push; FCM is only used in-process for FIAM (no token conflict).
- **Android**: OneSignal routes all pushes through FCM anyway, so adding `@react-native-firebase/messaging` doesn't duplicate delivery — it just exposes the underlying channel.

Split of responsibilities in this hybrid:

| Channel                                           | Owner                                   |
| ------------------------------------------------- | --------------------------------------- |
| Outbound push campaigns / segmented broadcasts    | OneSignal                               |
| Transactional push (order assigned, OTP, payment) | OneSignal (keep the existing code path) |
| In-app messages triggered by Analytics events     | FIAM                                    |
| Rich per-notification click/convert funnel        | OneSignal                               |
| Remote Config + A/B test integration              | Firebase                                |

---

## Decision checklist

Go through these — if you answer "yes" to **two or more of 1–5**, keep OneSignal.

1. Does anyone outside engineering need to send notifications?
2. Do you need per-campaign delivery / click / conversion reports?
3. Will you do multi-step journeys (reminder after 24h if not opened, etc.)?
4. Will you eventually add email / SMS and want one audience for all channels?
5. Do you need rich media / custom action buttons on iOS without writing a Notification Service Extension yourself?
6. Are notifications **only** transactional, triggered from your backend on business events? → **FCM alone is enough.**
7. Do you want to cut one third-party SDK to reduce app size / privacy scope? → **FCM alone is enough** (if #1–5 are all "no").

---

## If you migrate from OneSignal to FCM only

1. Add `@react-native-firebase/messaging` (the integration plan already adds `app`, `crashlytics`, `analytics`, `perf`, `remote-config` — messaging is separate).
2. iOS: enable Push Notifications + Background Modes (Remote notifications) capability; upload APNs auth key to Firebase console.
3. Android: `google-services.json` already configured → no extra work.
4. Replace `OneSignal.setExternalUserId(userId)` with:
   ```js
   import messaging from "@react-native-firebase/messaging";
   const token = await messaging().getToken();
   // POST token + user_id to your backend for targeted sends
   ```
5. Replace OneSignal's tag-based segments with Firebase user properties (`role`, `company_id`, etc. — already set up per Analytics plan §6).
6. Backend: switch send logic from OneSignal REST API to FCM HTTP v1 API (`https://fcm.googleapis.com/v1/projects/<project>/messages:send`) using a Google service account.
7. In-app messages: configure via Firebase console → Messaging → Campaigns → In-App. Trigger on any Analytics event — no app-side code needed for the campaigns themselves.
8. Verify with Firebase console → Messaging → send test to token; check `onMessage` (foreground) and `setBackgroundMessageHandler` (background) handlers fire.

## If you keep the hybrid

1. Install `@react-native-firebase/messaging` alongside OneSignal.
2. Do **not** call `messaging().getToken()` for outbound push — OneSignal manages that.
3. Use `@react-native-firebase/in-app-messaging` (FIAM is a separate package) purely for Analytics-triggered in-app UI.
4. No backend changes; OneSignal keeps sending pushes exactly as today.

---

## Files touched (if migrating)

| File                                                | Change                                                                                                    |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `package.json`                                      | Remove `react-native-onesignal`; add `@react-native-firebase/messaging` (+ optionally `in-app-messaging`) |
| `ios/Podfile.lock`                                  | Regenerated after `pod install`                                                                           |
| `ios/dzzlo_oms_app/AppDelegate.swift`               | Remove OneSignal init; FCM auto-initializes via `FirebaseApp.configure()`                                 |
| `ios/dzzlo_oms_app/Info.plist`                      | Remove OneSignal keys; ensure `UIBackgroundModes` includes `remote-notification`                          |
| `ios/OneSignalNotificationServiceExtension/*`       | Delete the whole target if not needed                                                                     |
| `android/app/build.gradle`                          | Remove OneSignal SDK dep                                                                                  |
| `android/app/src/main/AndroidManifest.xml`          | Remove OneSignal receivers / services                                                                     |
| `dzzlo_oms_app/src/utils/onesignal.js` (or similar) | Replace with `src/utils/messaging.js` that wraps `@react-native-firebase/messaging`                       |
| `dzzlo_oms_app/App.js` / `index.js`                 | Register `messaging().setBackgroundMessageHandler(...)` at top of file                                    |
| Backend send logic                                  | Switch from OneSignal REST to FCM HTTP v1                                                                 |
