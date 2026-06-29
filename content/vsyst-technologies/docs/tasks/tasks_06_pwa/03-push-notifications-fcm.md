# 03 — Push Notifications via FCM (FUTURE)

> Phase 3 of the PWA initiative. Adds web push notifications using Firebase Cloud Messaging.
> **Future work.** Tracked here so the design isn't lost. Do not start until Phase 1 + 2 are stable in production.

---

## TL;DR

After Phase 1/2, the app is installable and works offline. The next high-leverage capability is **server-initiated notifications** — alerting a technician that a new inspection has been assigned, or a customer has flagged an issue, even when the app isn't open.

`dip-web` already has `firebase ^9.15.0` in dependencies. FCM is the natural fit. The cross-stack `tasks_05_firebase/FIREBASE_NOTIFICATIONS_FCM_VS_ONESIGNAL.md` doc already evaluates FCM vs alternatives — read that before kicking off this phase.

Estimated effort: **3 days** including backend integration and notification UX.

---

## 1. Why FCM (Not OneSignal / Web Push API Directly)

| Option                       | Pros                                                                                       | Cons                                                                 |
| ---------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| **Raw Web Push API + VAPID** | No third-party dep                                                                         | Reimplement subscription management, payload encryption, retry logic |
| **OneSignal**                | Drop-in SDK, generous free tier                                                            | Ties analytics/segmentation to a 3rd-party vendor, more SDK weight   |
| **FCM (chosen)**             | Already a project dep; works on web + future Android via React Native; unified token model | Requires Firebase project setup; service account key on backend      |

See `tasks_05_firebase/FIREBASE_NOTIFICATIONS_FCM_VS_ONESIGNAL.md` for the full comparison.

---

## 2. Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                          dip-web (browser)                         │
│                                                                    │
│  ┌────────────────────┐         ┌──────────────────────────────┐   │
│  │ App / React UI     │         │ firebase-messaging-sw.js     │   │
│  │                    │         │ (custom service worker —     │   │
│  │  request           │         │  separate from vite-plugin-  │   │
│  │  permission +      │         │  pwa SW or merged via        │   │
│  │  get FCM token     │         │  injectManifest)             │   │
│  └─────────┬──────────┘         └─────────────┬────────────────┘   │
│            │ token                            │                    │
└────────────┼──────────────────────────────────┼────────────────────┘
             ▼                                  ▲
   ┌─────────────────────────┐                  │  push event
   │  POST /api/push/register│                  │
   │  { userId, fcmToken }   │      ┌───────────┴──────────────┐
   └─────────────┬───────────┘      │                          │
                 │                  │      Firebase Cloud      │
                 ▼                  │      Messaging           │
   ┌─────────────────────────┐      │                          │
   │  dzzlo_oms_api          │      └──────────────▲───────────┘
   │  - stores tokens        │                     │ FCM Admin SDK
   │  - sends notifications  ├─────────────────────┘
   │    via FCM Admin SDK    │   sendMulticast({tokens, notification})
   └─────────────────────────┘
```

---

## 3. Tasks

### 3.1 Frontend (`dip-web`)

- [ ] Decide: keep two SWs (Workbox + `firebase-messaging-sw.js`) or merge into one using `vite-plugin-pwa` `injectManifest` mode
- [ ] Add `firebase-messaging-sw.js` to `public/` with FCM config
- [ ] Add `requestNotificationPermission()` flow — gated behind a user action (tapping a "Enable notifications" button), never on first load
- [ ] Call `getToken()` after permission grant; POST to backend
- [ ] Foreground message handler: when app is open and a push arrives, surface as in-app toast (user has already dismissed the OS notification or it was suppressed)
- [ ] Token refresh handler: re-POST on `onTokenRefresh`
- [ ] Logout: call `deleteToken()` to stop the device receiving notifications for the logged-out user

### 3.2 Backend (`dzzlo_oms_api`)

- [ ] New collection: `push_subscriptions` ({ userId, fcmToken, deviceInfo, createdAt, lastSeenAt })
- [ ] New endpoint: `POST /api/push/register` — upsert by token
- [ ] New endpoint: `DELETE /api/push/unregister` — for explicit logout
- [ ] FCM Admin SDK setup — service account JSON in env
- [ ] Trigger points: identify the events that should send push (assignment, status change, etc.)
- [ ] Helper: `sendPushToUser(userId, payload)` — fans out to all that user's tokens
- [ ] Token cleanup job: nightly purge of tokens that returned `messaging/registration-token-not-registered`

### 3.3 UX

- [ ] "Enable notifications" prompt — when, how, and what copy
- [ ] Per-category notification preferences (assignments / status / system) — store on user profile
- [ ] Quiet hours / DND
- [ ] In-app notification center showing recent pushes (replays for users who missed the OS notification)

---

## 4. Open Questions

1. **Two SWs or one?** Workbox SW (from Phase 1) and `firebase-messaging-sw.js` can coexist (browsers allow multiple SWs at different scopes), but it's cleaner to merge. Merging requires switching `vite-plugin-pwa` from `generateSW` to `injectManifest` mode. More flexibility, more boilerplate.
2. **iOS Safari support.** Web push on iOS only works for **installed PWAs** on iOS 16.4+. Users who only bookmark the site won't get notifications. UX must guide them to install first.
3. **Notification fatigue.** What's the budget — max N pushes per day per user before we throttle?
4. **Multi-device dedup.** If a user has dip-web on phone + tablet + laptop, all three get pushed. Acceptable, or should we track "active" device and only push there?

---

## 5. Acceptance Criteria (Tentative)

- [ ] User can enable notifications via in-app button
- [ ] Test push from Firebase console arrives on the registered device
- [ ] Test push from backend arrives on the registered device
- [ ] Backend trigger (e.g. assignment created) results in a push within 5 seconds
- [ ] Foreground message renders as in-app toast, not as duplicate OS notification
- [ ] Logout removes the token; subsequent pushes do not arrive
- [ ] Works on Desktop Chrome, Android Chrome, iOS Safari (16.4+, installed PWA)

---

## 6. References

- `tasks_05_firebase/FIREBASE_NOTIFICATIONS_FCM_VS_ONESIGNAL.md` — vendor comparison
- `tasks_05_firebase/FIREBASE_NOTIFICATIONS_FCM_PLAN.md` — adjacent FCM plan (mobile)
- `tasks_05_firebase/FIREBASE_NOTIFICATIONS_CUSTOM_FEATURES_PLAN.md` — UX patterns
- FCM web docs: https://firebase.google.com/docs/cloud-messaging/js/client
- iOS web push (16.4+): https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/
- `00-overview.md` — phase context
