# Plan: Migrate from OneSignal → FCM + Firebase In-App Messaging (FIAM)

> Companion to `FIREBASE_INTEGRATION_PLAN.md`, `FIREBASE_ANALYTICS_PLAN.md`, and `FIREBASE_NOTIFICATIONS_FCM_VS_ONESIGNAL.md`. The comparison doc decided: **drop OneSignal if notifications are only transactional (dev-composed)**, which is the case for DZZLO OMS today. This plan is the concrete cut-over.

This plan **folds in the conclusions of `docs/learning/system-design/09-async-queues.md`** — the existing `sendNotifyToExternalIDs` fires-and-forgets to OneSignal, silently losing notifications on error, and blocks business operations waiting for OneSignal. The migration to FCM is the right moment to **also** move push delivery behind a BullMQ `notifications` queue so we fix both problems at once.

---

## 1. Current OneSignal Footprint

### Client — `dzzlo_oms_app`

| File                                                                                    | Role                                                                            |
| --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `src/helpers/OneSignal/index.js`                                                        | `OneSignal.initialize`, `requestPermission`, `Notifications.addEventListener('click')`, `setupInAppMessages` (app_version trigger → "update_app" action → open store), `OneSignal.login(externalUserId)` |
| `src/store/slices/auth.js`                                                              | `setNotification` reducer — click payload is pushed to Redux, the rest of the app reads it to deep-link |
| `src/navigation/AppNavigatorContainer.js`                                               | Calls `getResult` on app startup                                                |
| `src/constants/system.js`                                                               | `ONESIGNAL_APP_ID` constant                                                     |
| `src/types/env.d.ts`, `.env.example`                                                    | `ONESIGNAL_APP_ID`, `ONESIGNAL_REST_API_ID` env keys                            |
| `ios/OneSignalNotificationServiceExtension/*`                                           | NSE target for rich media (mutable-content)                                     |
| `ios/Podfile`, `ios/dzzlo_oms_app.entitlements`                                         | OneSignalExtension pod, app-group entitlement                                   |
| `package.json`                                                                          | `react-native-onesignal` dep                                                    |

### Server — `dzzlo_oms_api`

| File                                                                                                                               | Role                                            |
| ---------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| `api_v3/controllers/App/notification.js` (and v1/v2 clones)                                                                        | `sendNotifyToExternalIDs({ userIds, jsonData, headingData, contentData, notify })` — `fetch` POST to `https://api.onesignal.com/notifications`, `include_aliases: { external_id: userIds }`. |
| 26 callers: `api_v3/services/{order_msts,so_msts,voc_msts,invs,dealer_custs,veh_reqs}.js`, `routes/sadmin/notifs.js`, `collections/dealer_msts.js`, plus v1/v2 equivalents | Fire-and-forget `await sendNotifyToExternalIDs(...)` during business operations. |
| `.env`                                                                                                                             | `ONESIGNAL_APP_ID`, `ONESIGNAL_REST_API_ID`     |

### Known problems (from `system-design/09-async-queues.md`)

- `await sendNotifyToExternalIDs(...)` is **synchronous** inside request handlers → business op (e.g. linking a dealer customer) blocks on OneSignal latency.
- Error path is `catch (err) { console.log(...) }` — **notifications are silently lost** when OneSignal is down or the POST fails.
- No retries, no DLQ, no observability into what went out vs what failed.

### In-app messaging usage

Only **one** FIAM-equivalent flow today: prompt user to update the app when `app_version` trigger is stale. Any other in-app message needs reimplementing in FIAM.

---

## 2. Target Architecture

```
┌──────────────────── oms_api ────────────────────┐       ┌───────── Firebase ─────────┐
│                                                 │       │                            │
│  service code ── await notifQueue.add(          │──►──► │  FCM HTTP v1               │
│                     'send-push',                │       │  (oauth via service acct)  │
│                     { userIds, heading, body }) │       │                            │
│                                                 │       │  In-App Messaging          │
│  BullMQ worker: fetch FCM tokens for userIds,   │◄──────┤  (campaigns configured     │
│    call FCM v1 batch send, retry w/ backoff,    │       │   in console, triggered    │
│    log send+delivery into `notif_logs` coll.    │       │   by Analytics events)     │
│                                                 │       │                            │
└─────────────────────────────────────────────────┘       └────────────────────────────┘
                     ▲
                     │  token upserts
                     │
┌──────────────── oms_app ──────────────────┐
│  @react-native-firebase/messaging         │
│    getToken() → POST /fcm/register        │
│    onTokenRefresh → POST /fcm/register    │
│    onMessage (foreground)                 │
│    setBackgroundMessageHandler            │
│    notifee (tap → Redux setNotification)  │
│                                           │
│  @react-native-firebase/in-app-messaging  │
│    (no app code — console-driven)         │
└───────────────────────────────────────────┘
```

Key shifts from today:
- **Server** no longer targets external user IDs via OneSignal; it sends to **FCM tokens** it stores. A new `fcm_tokens` collection maps `user_id → [tokens]`.
- **Delivery is queued.** Route handlers enqueue a `send-push` job and return immediately. A worker handles FCM with retries + DLQ.
- **Click handling** moves from OneSignal's event listener to a tiny wrapper around `@notifee/react-native` (or `messaging().onNotificationOpenedApp` for simple cases) — the downstream `dispatch(setNotification(data))` stays the same.
- **IAM** continues to cover the update-app prompt, just via Firebase console + an Analytics event as trigger (e.g. `app_version_stale`).

---

## 3. Steps — Server (`dzzlo_oms_api`)

### Step S1 — Install SDK & service account

```bash
cd dzzlo_oms_api
npm i firebase-admin bullmq ioredis
```

- In Firebase console → Project Settings → Service accounts → "Generate new private key" → download JSON.
- Store as `dzzlo_oms_api/firebase-service-account.json` (gitignored) **or** base64-inject via `FIREBASE_SERVICE_ACCOUNT_B64` env var.
- Add to `.env.example`:
  ```
  FIREBASE_SERVICE_ACCOUNT_B64=
  REDIS_HOST=
  REDIS_PORT=6379
  ```
- Remove `ONESIGNAL_APP_ID`, `ONESIGNAL_REST_API_ID` from `.env.example` (keep in running `.env` until rollout completes).

### Step S2 — Initialize admin SDK once

`dzzlo_oms_api/lib/firebaseAdmin.js`:

```js
const admin = require("firebase-admin");

if (!admin.apps.length) {
  const json = Buffer.from(
    process.env.FIREBASE_SERVICE_ACCOUNT_B64,
    "base64",
  ).toString("utf8");
  admin.initializeApp({ credential: admin.credential.cert(JSON.parse(json)) });
}

module.exports = admin;
```

### Step S3 — Add `fcm_tokens` collection + register route

Schema (Mongoose or native):
```js
{
  _id,
  user_id: ObjectId,  // indexed
  token: String,      // unique
  platform: "ios" | "android",
  app_version: String,
  updated_at: Date,
}
```
- Compound index on `user_id` (fetch all tokens for a user during send).
- Unique index on `token` (upsert-by-token).
- TTL index on `updated_at` (60 days) — FCM tokens refresh; purge stale ones to avoid sending to dead devices.

Route `POST /api/fcm/register` body `{ token, platform, app_version }` — requires auth middleware, upserts by token, sets `user_id` from session.

Route `DELETE /api/fcm/register` — unregisters on logout (pass the device's current token).

### Step S4 — Replace `sendNotifyToExternalIDs` (keep signature)

`api_v3/controllers/App/notification.js` — **keep the same function name + signature** so the 26 callers don't change:

```js
const { pushQueue } = require("../../../queues");

exports.sendNotifyToExternalIDs = async ({
  userIds,
  jsonData,
  headingData,
  contentData,
  notify,
}) => {
  if (!notify || !userIds?.length) return;
  // Enqueue — return immediately. Delivery + retry is the worker's job.
  await pushQueue.add(
    "send-push",
    { userIds, jsonData, heading: headingData, body: contentData },
    {
      attempts: 5,
      backoff: { type: "exponential", delay: 2000 },
      removeOnComplete: { count: 1000 },
      removeOnFail: false, // keep failed for DLQ inspection
    },
  );
};
```

No caller (26 files) needs to change.

### Step S5 — Worker (`workers/pushWorker.js`)

Follows the pattern from `system-design/09-async-queues.md` §Step 6:

```js
const { Worker } = require("bullmq");
const admin = require("../lib/firebaseAdmin");
const FcmToken = require("../models/FcmToken");
const NotifLog = require("../models/NotifLog");

const connection = { host: process.env.REDIS_HOST, port: +process.env.REDIS_PORT };

new Worker(
  "notifications",
  async (job) => {
    if (job.name !== "send-push") return;
    const { userIds, heading, body, jsonData } = job.data;

    const tokens = await FcmToken.find({ user_id: { $in: userIds } })
      .select("token user_id")
      .lean();
    if (!tokens.length) return { skipped: "no_tokens" };

    // sendEachForMulticast handles up to 500 tokens per call.
    const chunks = chunkArray(tokens.map((t) => t.token), 500);
    const results = [];
    for (const tks of chunks) {
      const res = await admin.messaging().sendEachForMulticast({
        tokens: tks,
        notification: { title: heading, body },
        data: stringifyValues(jsonData || {}), // FCM data payload must be string→string
        android: { priority: "high" },
        apns: { headers: { "apns-priority": "10" } },
      });
      results.push(res);

      // Purge tokens FCM says are permanently invalid.
      const dead = [];
      res.responses.forEach((r, i) => {
        if (
          r.error &&
          ["messaging/registration-token-not-registered", "messaging/invalid-argument"].includes(
            r.error.code,
          )
        ) {
          dead.push(tks[i]);
        }
      });
      if (dead.length) await FcmToken.deleteMany({ token: { $in: dead } });
    }

    await NotifLog.create({
      userIds,
      heading,
      body,
      data: jsonData,
      sent: results.reduce((n, r) => n + r.successCount, 0),
      failed: results.reduce((n, r) => n + r.failureCount, 0),
      at: new Date(),
    });
  },
  { connection, concurrency: 5 },
).on("failed", (job, err) => console.error("push job failed", job?.id, err));
```

Register in `ecosystem.config.js` as a separate PM2 app (per §Step 6 Option B) once queue traffic grows; until then, Option A (in-process) is fine.

### Step S6 — `sadmin/notifs.js` (broadcast / admin sends)

Admin broadcast endpoint that currently loops over user ids → switch to a **topic** (`/topics/all`, `/topics/dealers`, `/topics/customers`) subscribed on the client (Step C4) and use `admin.messaging().send({ topic, notification, data })`. Cuts one-to-many sends from N FCM calls to 1.

### Step S7 — Retain OneSignal briefly (dual-send)

During rollout, the function can **dual-send** (keep the OneSignal POST + enqueue FCM) behind a feature flag (Remote Config — already on the integration-plan roadmap). Once FCM delivery metrics look healthy for ~1 week, flip the flag and delete the OneSignal branch.

---

## 4. Steps — Client (`dzzlo_oms_app`)

### Step C1 — Packages

```bash
cd dzzlo_oms_app
yarn add @react-native-firebase/messaging @react-native-firebase/in-app-messaging @notifee/react-native
yarn remove react-native-onesignal
```

### Step C2 — iOS: enable FCM, delete OneSignal bits

- Xcode → Signing & Capabilities on the main target → ensure **Push Notifications** and **Background Modes → Remote notifications** are on.
- Upload the APNs auth key (`.p8`) to Firebase console → Cloud Messaging.
- `AppDelegate.swift` needs nothing new — `@react-native-firebase/messaging` auto-swizzles once `FirebaseApp.configure()` runs (already uncommented in the integration plan).
- Delete the `OneSignalNotificationServiceExtension/` target from the Xcode project (and the corresponding folder) — not needed unless/until we add rich-media pushes. If rich media is needed later, add a fresh **Notification Service Extension** using Firebase's sample.
- Remove from `ios/Podfile`: `target 'OneSignalNotificationServiceExtension'` block + any OneSignalXCFramework entries.
- Remove OneSignal app-group entitlement from `ios/dzzlo_oms_app/dzzlo_oms_app.entitlements`.

### Step C3 — Android: nothing to do

`google-services.json` is already in place (integration plan §Current State). `@react-native-firebase/messaging` auto-registers the required `<service>` and `<receiver>` via manifest merging. Remove the OneSignal `<receiver>` entries that the OneSignal SDK's merged manifest contributed — just uninstall the package.

### Step C4 — Replace `src/helpers/OneSignal/` with `src/helpers/Messaging/`

Create `src/helpers/Messaging/index.js` (same export shape so callers don't change):

```js
import messaging from "@react-native-firebase/messaging";
import notifee, { AndroidImportance } from "@notifee/react-native";
import DeviceInfo from "react-native-device-info";
import { Platform } from "react-native";
import { setNotification } from "../../store/slices/auth";
import { registerFcmToken, unregisterFcmToken } from "../../store/apis/fcm";

let didInit = false;

export const getResult = async ({ dispatch }) => {
  if (didInit) return;
  didInit = true;

  await messaging().requestPermission(); // iOS prompt + Android 13+

  // Channel for Android heads-up notifications
  await notifee.createChannel({
    id: "default",
    name: "Notifications",
    importance: AndroidImportance.HIGH,
  });

  const token = await messaging().getToken();
  await dispatch(
    registerFcmToken.initiate({
      token,
      platform: Platform.OS,
      app_version: DeviceInfo.getVersion(),
    }),
  );

  messaging().onTokenRefresh(async (newToken) => {
    await dispatch(
      registerFcmToken.initiate({
        token: newToken,
        platform: Platform.OS,
        app_version: DeviceInfo.getVersion(),
      }),
    );
  });

  // Foreground: FCM doesn't auto-display; use notifee
  messaging().onMessage(async (msg) => {
    await notifee.displayNotification({
      title: msg.notification?.title,
      body: msg.notification?.body,
      data: msg.data,
      android: { channelId: "default", pressAction: { id: "default" } },
    });
  });

  // Tap when app in background / quit state
  messaging().onNotificationOpenedApp((msg) => {
    if (msg?.data) dispatch(setNotification(msg.data));
  });
  const initial = await messaging().getInitialNotification();
  if (initial?.data) dispatch(setNotification(initial.data));

  // Tap on a foreground notif (notifee-displayed)
  notifee.onForegroundEvent(({ type, detail }) => {
    if (type === 1 /* PRESS */ && detail.notification?.data) {
      dispatch(setNotification(detail.notification.data));
    }
  });
};

export const setExtUserId = (externalUserId) => {
  // FCM does not have the concept of external user id. Tokens are already tied
  // to the user via the /fcm/register endpoint.  Kept as no-op for API parity.
};
```

Background handler must be registered **at the top of `index.js`** (before `AppRegistry`):

```js
import messaging from "@react-native-firebase/messaging";
messaging().setBackgroundMessageHandler(async (_msg) => {
  // System draws the notification automatically on Android when `notification`
  // key is present. On iOS APNs draws it. Nothing to do here unless we need
  // data-only processing.
});
```

### Step C5 — Startup wiring

`AppNavigatorContainer.js` already calls `getResult({ dispatch })`. Re-point that import from `src/helpers/OneSignal` to `src/helpers/Messaging`. No other call sites.

### Step C6 — FIAM for the "update app" prompt

- Delete `setupInAppMessages` from client code entirely.
- In Firebase console → Messaging → In-App Messaging → create a campaign:
  - Message: "A new version is available"
  - Action: open URL → the app's store URL (Android / iOS different campaigns, or one campaign with `device.platform` audience)
  - Audience: users whose `app_version` user property is less than current.
  - Trigger: Analytics event `screen_view` (fires everywhere) or `app_open`.
- `app_version` is already set as a **default event parameter + user property** per the Analytics plan §6.1 → no extra client code.
- If we need deep-link click handling, add one listener:
  ```js
  import inAppMessaging from "@react-native-firebase/in-app-messaging";
  // Optional — FIAM auto-renders; only needed if we want to intercept clicks.
  ```
  FIAM handles the store-link tap natively via the campaign's action URL; the custom `Linking.openURL` logic from the old OneSignal path is no longer needed.

### Step C7 — Logout

Call `unregisterFcmToken.initiate({ token: currentToken })` on logout **before** clearing session, then `await messaging().deleteToken()` to invalidate.

### Step C8 — Clean up constants / env

- Delete `ONESIGNAL_APP_ID` from `src/constants/system.js` and `src/types/env.d.ts`.
- Remove `ONESIGNAL_APP_ID` from `dzzlo_oms_app/.env.example`.

---

## 5. Data-payload compatibility

The Redux `setNotification` reducer currently reads `OneSignal`'s `notification.additionalData`. Keep **the same key names** in the FCM `data` payload so downstream navigation logic is unchanged.

Server-side producers already pass `jsonData` — it lands in FCM `data` directly. The worker stringifies values (FCM requires string-only in `data`); the client should `JSON.parse` any nested object strings before dispatching if the existing code did so (spot-check `setNotification` consumers).

**Important:** Both `notification` and `data` keys must be present in the FCM payload so:
- system auto-shows it when app is backgrounded/killed (`notification` key),
- `data` still flows through `onNotificationOpenedApp` + `getInitialNotification`.

---

## 6. Rollout phases

| Phase | Scope                                                                                                                | Exit gate                                                              |
| ----- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| 0     | Integration-plan Step 1-5 landed (Firebase app + analytics + crashlytics wired)                                      | App runs with Firebase initialised                                     |
| 1     | Server: `firebase-admin` init, `fcm_tokens` collection + routes, BullMQ `notifications` queue + push worker; **dual-send** (OneSignal + FCM) behind Remote Config `push_backend=both` | Logs show FCM send success rate ≥ 99% across 7 days                    |
| 2     | Client: Messaging helper, register endpoint, foreground/background handlers, `notifee` display, FIAM                | Test-device tap navigates correctly; update-app FIAM shown             |
| 3     | Flip Remote Config `push_backend=fcm_only`; monitor for 3 days                                                       | No regression in customer/dealer push experience                       |
| 4     | Delete OneSignal: server fetch branch, client package, iOS NSE target, Podfile entries, entitlements, env vars, constants | `grep -i onesignal` returns zero matches in both repos                 |
| 5     | Migrate admin broadcasts to FCM topics (`/topics/customers`, `/topics/dealers`, `/topics/all`)                       | `sadmin/notifs.js` sends via `admin.messaging().send({ topic })`       |

---

## 7. Verification

1. **Token registration:** on fresh install, `fcm_tokens` collection gets one entry with correct `user_id`, `platform`, `app_version`.
2. **Transactional push:**
   - Trigger a dealer's "new customer link" flow (calls `sendNotifyToExternalIDs` via `dealer_custs.js`).
   - Confirm BullMQ dashboard (Bull Board) shows the `send-push` job completed.
   - Confirm the target device shows the notification (foreground via notifee, background via system).
   - Tap the notification → Redux `setNotification` receives the same `data` payload shape as before → existing navigation logic fires.
3. **Failure retry:** in staging, block FCM host with iptables → confirm BullMQ retries 5× with exponential backoff → DLQ entry created. Unblock → confirm queue drains.
4. **Dead-token cleanup:** send to a device, uninstall the app, re-send → worker prunes the token from `fcm_tokens`.
5. **Admin broadcast:** subscribe test device to `/topics/dealers` → fire admin broadcast → confirm receipt.
6. **FIAM:** publish an in-app campaign with trigger `app_open` → launch app → confirm modal renders → tap action → confirm store opens. Disable campaign when done.
7. **Logout:** log out → token is deleted server-side and `messaging().deleteToken()` resolves → subsequent server send to that user has zero tokens and early-exits (`skipped: no_tokens` in `NotifLog`).

---

## 8. Files touched — summary

### Added

| File                                                  | Purpose                                     |
| ----------------------------------------------------- | ------------------------------------------- |
| `dzzlo_oms_api/lib/firebaseAdmin.js`                  | Singleton admin SDK init                    |
| `dzzlo_oms_api/models/FcmToken.js`                    | `fcm_tokens` schema                         |
| `dzzlo_oms_api/models/NotifLog.js`                    | Delivery audit log                          |
| `dzzlo_oms_api/queues/index.js`                       | BullMQ queue(s)                             |
| `dzzlo_oms_api/workers/pushWorker.js`                 | FCM sender with retry + token pruning       |
| `dzzlo_oms_api/api_v3/routes/fcm.js`                  | `POST /fcm/register`, `DELETE /fcm/register`|
| `dzzlo_oms_app/src/helpers/Messaging/index.js`        | FCM + notifee orchestration                 |
| `dzzlo_oms_app/src/store/apis/fcm.js`                 | RTK Query endpoints for register/unregister |

### Modified

| File                                                                             | Change                                                                 |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `dzzlo_oms_api/api_v3/controllers/App/notification.js` (+ v1/v2 copies)          | Body of `sendNotifyToExternalIDs` → enqueue job (signature unchanged)  |
| `dzzlo_oms_api/api_v3/routes/sadmin/notifs.js` (+ v2)                            | Admin broadcast switches to FCM topic send                             |
| `dzzlo_oms_api/.env.example`                                                     | Add `FIREBASE_SERVICE_ACCOUNT_B64`, `REDIS_HOST`, `REDIS_PORT`; remove `ONESIGNAL_*` |
| `dzzlo_oms_api/ecosystem.config.js`                                              | (Optional, Phase 2+) Separate PM2 app for worker                       |
| `dzzlo_oms_app/index.js`                                                         | Register `setBackgroundMessageHandler` at the top                      |
| `dzzlo_oms_app/src/navigation/AppNavigatorContainer.js`                          | Import from `helpers/Messaging` instead of `helpers/OneSignal`         |
| `dzzlo_oms_app/src/store/slices/auth.js`                                         | `setNotification` payload shape is unchanged — sanity-check consumers  |

### Deleted

| File / entry                                                                     | Reason                                      |
| -------------------------------------------------------------------------------- | ------------------------------------------- |
| `dzzlo_oms_app/src/helpers/OneSignal/index.js`                                   | Replaced by `helpers/Messaging`             |
| `dzzlo_oms_app/ios/OneSignalNotificationServiceExtension/*`                      | NSE target not needed until rich media      |
| `ios/Podfile` OneSignal target block                                             | —                                           |
| `ios/dzzlo_oms_app/dzzlo_oms_app.entitlements` OneSignal app-group               | —                                           |
| `src/constants/system.js` `ONESIGNAL_APP_ID` export                              | —                                           |
| `src/types/env.d.ts`, `.env.example` OneSignal keys                              | —                                           |
| `package.json` `react-native-onesignal`                                          | —                                           |

---

## 9. Why this ordering is safe

- **Server first, dual-send enabled:** server deploy is reversible (Remote Config flag flips delivery back to OneSignal only) and can't break installed clients.
- **Client next, with server already accepting tokens:** first clients upgrading simply start registering tokens; nothing else changes until the flag flips.
- **Flag flip last:** the riskiest step is the last one, gated by a week of observed parity metrics.
- **OneSignal code deleted only after flag flip is stable for 3 days** — if anything regresses, we flip back without rebuilding the app.
