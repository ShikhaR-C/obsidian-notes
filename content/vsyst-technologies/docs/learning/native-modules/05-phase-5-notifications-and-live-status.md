# Phase 5 — Notifications and Live Status: From a Push to a Living Order

> Level: Intermediate → Advanced | Time: ~3 h to read · 3–5 weeks to build on both platforms, server work included _(est.)_ | Outcome: pushes that ask at the right moment, survive India's battery killers and open the right order; reminders that fire with no signal; a live order card on the iPhone Lock Screen and in the Android 16 status bar — with an honest fallback everywhere else.

---

## 1. The One Idea

A notification is a promise the app keeps while it is not running. DZZLO makes that promise once today — at first launch, before the user knows what they will be told — and then leaves everything to OneSignal's defaults. This phase turns the promise into a ladder. You climb a rung only when the one below it holds:

```
 rung 5  LIVE STATUS      one card that changes in place ─ iOS Live Activity · Android 16 Live Update
 rung 4  LOCAL REMINDER   fires with no server, no signal ─ react-native-notify-kit
 rung 3  IN-APP MESSAGE   speaks while the app is open    ─ OneSignal IAM (already linked)
 rung 2  ACTIONABLE PUSH  levels, buttons, threads, link  ─ OneSignal payload + small native glue
 rung 1  PLAIN PUSH       arrives, and the tap lands      ─ exists today, half-finished
```

Rungs 1–4 are JavaScript, payload design and configuration. Rung 5 is where native code becomes unavoidable: a SwiftUI view in a Widget Extension on iOS, a Kotlin class that rebuilds the notification on Android.

### What the app has today (read 2026-09-29 on `release/v1_79`)

| Piece | Evidence | Verdict |
|---|---|---|
| Push SDK | `react-native-onesignal` `^5.4.1` (`package.json:54`, 5.4.1 installed); pods resolve `OneSignalXCFramework` 5.5.0 incl. `OneSignalLiveActivities`, `OneSignalInAppMessages`, `OneSignalLocation` (`ios/Podfile.lock:192-203`); Android pulls `com.onesignal:notifications:5.7.6` | Keep; upgrade to 5.5.14 |
| Start-up | `src/helpers/OneSignal/index.js:20` sets `LogLevel.Verbose` unconditionally; `:22` `initialize`; `:24` `Notifications.requestPermission(true)` — run from the root container's mount effect (`src/navigation/AppNavigatorContainer.js:90-96`), so on the first cold start, **before sign-in**, and the result is never read | Prompt out of context; verbose logs in release |
| Tap handling | `:26-30` puts `additionalData` into Redux (`store/slices/auth.js:107-109`); the drawers switch on it after a 900 ms timer — dealer `Verification · NewOrder · NewPayment · NewCustomer` (`navigation/Dealer/DrawerContent.js:178-199`), customer `NewSalesOrder · NewInvoice · NewVoucher · ApprovedPayment · NewVehicleRequest` (`navigation/Customer/DrawerContent.js:178-201`) | Lands on a **list**, never on the order |
| In-app messages | `:53` trigger `app_version`; `:60-72` an `update_app` button gated by `Linking.canOpenURL('https://…')` | Silently dead on Android 11+: without a `<queries>` entry `canOpenURL` resolves `false` (RN's docs say it may reject); fix in [[02-phase-2-dependency-diet]] |
| iOS extension | Target `OneSignalNotificationServiceExtension` (bundle `in.vsyst.dzzlooms.OneSignalNotificationServiceExtension`, own Podfile target at `ios/Podfile:73-75`); `NotificationService.swift:40-68` forwards to `OneSignalExtension` and "only runs when `mutable_content` is set" | Keep untouched |
| iOS capabilities | `aps-environment` + App Group `group.in.vsyst.dzzlooms.onesignal` (`ios/dzzlo_oms_app/dzzlo_oms_app.entitlements:5-10`; the NSE carries the same group); `UIBackgroundModes = [remote-notification]` (`Info.plist:80-83`) | Keep; that group stays OneSignal's |
| Android permissions | `AndroidManifest.xml:3` declares only `INTERNET`. The merged release manifest adds `POST_NOTIFICATIONS` (line 33; OneSignal 5.7.6 and firebase-messaging 25.0.1), `RECEIVE_BOOT_COMPLETED`, 16 launcher-badge permissions (ShortcutBadger) and `FOREGROUND_SERVICE` (WorkManager 2.8.1) | Arrive by merge; `PermissionsAndroid` has **0** imports in live code |
| Tests | `jest.setup.js:224-243` — a hand stub for `initialize`, `login`, `Debug`, `Notifications`, `InAppMessages`, `User` | Extend it; never fork it |

On Android 13+ (API 33, `POST_NOTIFICATIONS`) and on iOS, OneSignal's `requestPermission` shows the system dialog. Firing it at first launch, before DZZLO has earned it, is the textbook way to collect a permanent "Don't allow".

### Why this deserves a whole phase

The evidence from comparable Indian merchant apps is about reliability, not novelty (Google Play, newest 1,000 reviews per app, fetched 2026-09-29). PhonePe Business, 1★, 2026-09-28: "voice alert setting for transactions is enabled … I have not been receiving any voice alert notifications"; another 1★, 2026-09-04: "notifications also not coming … lock screen notification is also not coming for every transaction". Payment apps sell alerts as the product (Paytm for Business: "instant SMS and push notifications for every successful payment"; Google Pay for Business: a SoundPod), and the apps your dealers already use promise "Place an indent Order with 2 clicks and get live status" (IndianOil For Business). Swiggy's designers report replacing five order notifications with one Live Activity (search snippet only; the article returned HTTP 403).

Reading: "the alert didn't come" beats every feature request in these reviews _(inference from crude keyword counts)_ — so rung 1 gets most of the care, and rung 5 ships last.

Source: https://play.google.com/store/apps/details?id=com.phonepe.app.business · https://play.google.com/store/apps/details?id=px.indianoil.in

## 2. Push Done Properly

### 2.1 Upgrade, then quieten the logs

```bash
yarn add react-native-onesignal@5.5.14     # 5.4.1 → 5.5.14 (2026-09-23), a TurboModule
cd ios && bundle exec pod install && cd ..
```

OneSignal's README says 5.4.x and later need RN ≥ 0.79; 0.84.1 qualifies. Every API named below is in the installed 5.4.1 typings (`node_modules/react-native-onesignal/dist/index.d.ts`, read 2026-09-30) — re-read that file after the upgrade. Red first: a Tier 1 test loads the helper with `global.__DEV__ = false` inside `jest.isolateModules` and expects `LogLevel.Warn`; green: `OneSignal.Debug.setLogLevel(__DEV__ ? LogLevel.Verbose : LogLevel.Warn)`.

### 2.2 Ask at the right moment

| Fact | Detail |
|---|---|
| Android `POST_NOTIFICATIONS` | Runtime permission from Android 13 (API 33). Apps targeting API 32 or lower get the prompt with their first channel, and one "Don't allow" is final until reinstall; DZZLO targets 36, so it asks itself. Pre-granted on OS upgrade for apps that already had channels. Google's advice: ask in context, e.g. when "the user submits an order"; check `areNotificationsEnabled()` (API 24) |
| iOS provisional | `UNAuthorizationOptions.provisional` (iOS 12.0) delivers quietly to Notification Centre with no dialog. OneSignal exposes it as `Notifications.registerForProvisionalAuthorization(handler)` |
| OneSignal JS | `getPermissionAsync()`, `canRequestPermission()` ("true if the device has not been prompted"), `requestPermission(fallbackToSettings)`, `permissionNative()` (iOS: NotDetermined · Denied · Authorized · Provisional · Ephemeral), `addEventListener('permissionChange', …)` |

Source: https://developer.android.com/develop/ui/views/notifications/notification-permission

The DZZLO rule (a proposal for the user to approve):

| Moment | Who | What happens |
|---|---|---|
| First launch | everyone | `initialize` only — no dialog |
| After sign-in, iOS | customers | `registerForProvisionalAuthorization` — quiet delivery |
| First order placed (customer) / first order received (dealer) | both | A DZZLO sheet names the three things we notify about, then `requestPermission(false)` |
| Settings → Notifications | both | State from `getPermissionAsync()`; "Turn on" calls `requestPermission(true)`, whose `true` falls back to the Settings app when the user already declined |

Test-first: `src/helpers/OneSignal/permission.js` exports a pure `nextPermissionStep({ os, canAsk, granted, role, hasOrdered })` returning `'none' | 'provisional' | 'explain' | 'settings'`, and a Tier 1 table test covering every row above goes red first. Then green, then one Tier 3 test per sheet decision, then delete the unconditional call at `index.js:24`. The sheet holds its layout at 320 dp × fontScale 1 in en and hi, colours from `src/theme` tokens.

### 2.3 Android channels and importance

`NotificationChannel` arrived in Android 8.0 (API 26 — verified in the SDK's `api-versions.xml`, 2026-09-30); API 24–25 devices ignore channels. The user sets importance per channel, so split by what a person would silence:

| Channel id | Carries | Importance (proposal) |
|---|---|---|
| `orders` | new order, approval needed, dispatched, delivered | high |
| `payments` | payment received / approved, invoice raised | high |
| `reminders` | local payment-due reminders (§4) | default |
| `live_status` | the ongoing card (§6) | default — never `IMPORTANCE_MIN`, which disqualifies promotion |
| `service` | daily summary ready, price-revision notes | low |

Create the channels yourself at start-up (notify-kit's `createChannel`, §4) so their names are translated into Hindi; OneSignal's REST API lets each message name its Android channel — confirm the field name in OneSignal's REST reference when you wire the server (not captured in this course's sources).

### 2.4 iOS interruption levels and Time Sensitive

`UNNotificationInterruptionLevel` (iOS 15.0): `.passive`, `.active`, `.timeSensitive` ("presents the notification immediately, lights up the screen, can play a sound, and breaks through system notification controls") and `.critical` ("bypasses the mute switch"). Critical needs the `com.apple.developer.usernotifications.critical-alerts` entitlement and Apple's prior approval, granted for health, safety, security and emergency cases — **DZZLO is not eligible**. OneSignal sets the level per message with `ios_interruption_level` = `active | time-sensitive | passive | critical`, plus an optional `ios_relevance_score` from 0 to 1.

Time Sensitive is a capability you add in Xcode with no Apple approval (secondary source: Pushwoosh). **UNVERIFIED:** the exact entitlement key string was not confirmed on an Apple page, and a string search of Xcode 27 found nothing on 2026-09-30. Add it through Signing & Capabilities → **+ Capability** → Time Sensitive Notifications, and copy the key from the `.entitlements` diff Xcode writes — never hand-type it.

Source: https://documentation.onesignal.com/docs/en/ios-focus-modes-and-interruption-levels

| DZZLO event | `ios_interruption_level` | `ios_relevance_score` |
|---|---|---|
| Order awaiting your approval (dealer) | `time-sensitive` | 1.0 |
| Credit limit crossed | `time-sensitive` | 0.9 |
| Order dispatched / delivered (customer) | `active` | 0.7 |
| Payment received | `active` | 0.6 |
| Daily summary ready | `passive` | 0.2 |

Guideline 4.5.4 says pushes "should not be used to send sensitive personal or confidential information": order numbers and statuses belong in the text; balances and outstanding amounts do not.

### 2.5 Buttons, categories and direct reply — what OneSignal covers

| Capability | Platform API (introduced) | Through OneSignal? | Native hook? |
|---|---|---|---|
| Action buttons (View · Approve · Reject) | iOS `UNNotificationCategory` (10.0); Android notification actions | Yes — the repo's NSE notes that "Setting an attachment or action buttons automatically sets [`mutable_content`] to true" (`NotificationService.swift:45-46`); the tapped button reaches JS as `event.result.actionId` on `click` | No, for "open the app on this order" |
| Act without opening the app | same | Not established in our sources | Yes — Swift/Kotlin handler plus a token readable outside JS ([[09-phase-9-security-privacy-and-release]]) |
| Direct reply (text field) | iOS `UNTextInputNotificationAction` (10.0); Android `RemoteInput` (API 20) | Not in our sources | Yes, on both |
| Order lines inside the notification | iOS `UNNotificationContentExtension` (10.0) — a new extension target | No | Yes |

Verdict: buttons that **open** the app on the right order, where the screen asks "Approve order #2417?" — a money-moving action never completes from the lock screen. Skip direct reply (DZZLO has no chat) and content extensions in v1; communication notifications don't apply either.

### 2.6 Threads, groups and badges

- **iOS threads** — `UNNotificationContent.threadIdentifier` (iOS 10.0) groups one customer's pushes; `relevanceScore` orders them in the summary.
- **iOS badge** — `setBadgeCount(_:withCompletionHandler:)` (iOS 16.0); the badge means one thing only: orders awaiting the dealer's approval. Set it from the server through OneSignal's badge fields (names: confirm in its REST reference).
- **Android groups** — one group per customer; OneSignal's JS has `removeGroupedNotifications(groupId)` and `clearAll()` for clean-up after the user acts in-app.
- **Android badges** — the 16 ShortcutBadger permissions are OEM-launcher workarounds that arrive with OneSignal. Don't promise a badge count on Android.

### 2.7 Deep links: from "a list" to "this order"

Today `{ "dealer": "NewOrder" }` opens the Orders tab. Add the order id — old app versions ignore unknown keys, so this is backward compatible:

```json
{ "dealer": "NewOrder", "orderId": "66f8c0…", "path": "orders/66f8c0…" }
```

```js
// src/helpers/OneSignal/routeForNotification.js — Tier 1, written after its test
export const routeForNotification = (data, role) => {
  if (!data || typeof data !== 'object') return null;
  const key = data[role];                       // 'dealer' | 'customer', as the drawers read it
  if (!key) return null;
  if (typeof data.path === 'string') return { kind: 'link', path: data.path };
  return { kind: 'legacy', key };               // today's drawer switch, unchanged
};
```

The `link` branch is resolved by the linking map that [[08-phase-8-instant-experiences-and-links]] adds; until that lands, `legacy` keeps today's list behaviour. That same map also retires the drawers' 900 ms `setTimeout`, which exists only because the navigator may not be mounted yet. Tests first: an unknown role → `null`; a key without `path` → `legacy`; a key with `path` → `link`.

### 2.8 FCM priority and the "no visible notification" penalty

Firebase: normal-priority messages wait while the device is in Doze; high priority can wake it, but "if FCM detects a pattern in which messages don't result in user-facing notifications, your messages may be deprioritized", judged over 7 days; `onMessageReceived` gets "several seconds". Rules for the API server (`dzzlo_oms_api`):

1. Every order, payment and approval event is a **visible** push.
2. Data-only messages only nudge caches or widgets, never carry news.
3. The app re-syncs on resume — v2 screens already do (`src/screens/v2/shared/useRefetchOnRefocus.js`).

Source: https://firebase.google.com/docs/cloud-messaging/android/message-priority

### 2.9 India's battery killers

dontkillmyapp ranks the brands that dominate Indian pockets among the most aggressive process killers:

| Rating | Brands |
|---|---|
| 5/5 | Huawei, **Xiaomi**, **OnePlus**, **Samsung** |
| 4/5 | Meizu, Asus, **Oppo** |
| 3/5 | Wiko, Lenovo, **Vivo**, **realme**, Motorola, Blackview, **Tecno** |
| 0 | AOSP/Pixel, Nokia, HTC |

The ranking carries no last-updated date and may predate One UI 8 / HyperOS 3. Xiaomi's user-side fix: enable Autostart, set Battery saver to "No restrictions", lock DZZLO in Recents.

Play forbids the easy way out: "Google Play policies prohibit apps from requesting direct exemption from Power Management features … unless the core function of the app is adversely affected" — the allowed cases are non-FCM chat/VoIP, safety, task automation and peripheral companions. DZZLO is none of them, so **never** fire `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`. What works instead:

1. Visible notifications for everything that matters (§2.8).
2. Refresh on open — the server is the truth, the push is a hint.
3. A Daily Summary widget — apps with active widgets are exempt from the Restricted standby bucket, which otherwise hits after 8 days unused on Android 13+ ([[06-phase-6-widgets-shortcuts-and-intents]]).
4. An OEM guide screen for dealers who rely on alerts: pick illustrated steps by the device's brand — `NativeAppInfo`'s `brand` constant (Android `Build.BRAND`) from [[01-phase-1-foundations]]; if brand proves too coarse, add `Build.MANUFACTURER` to the same constants — then link to `Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS` (API 23), which most apps may open. Samsung's setting name ("Never sleeping apps") is **unverified wording**. ~1–2 days _(est.)_.

Source: https://dontkillmyapp.com/ · https://developer.android.com/training/monitoring-device-state/doze-standby

### 2.10 Tests and the device checklist

Extend the existing stub — same object, new keys:

```js
// jest.setup.js — inside the existing jest.mock('react-native-onesignal', …) (lines 224-243)
Notifications: {
  requestPermission: jest.fn(() => Promise.resolve(true)),
  getPermissionAsync: jest.fn(() => Promise.resolve(false)),
  canRequestPermission: jest.fn(() => Promise.resolve(true)),
  registerForProvisionalAuthorization: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  removeGroupedNotifications: jest.fn(),
},
LiveActivities: { setupDefault: jest.fn(), startDefault: jest.fn(), exit: jest.fn() },
```

A config pin, `src/helpers/OneSignal/__tests__/push.config.test.js`, reads off disk and asserts booleans only — a failing `toMatch` would print `Info.plist` ([[02-phase-2-dependency-diet]] §1): `Info.plist` keeps `remote-notification`; both `.entitlements` files keep `group.in.vsyst.dzzlooms.onesignal`; `AndroidManifest.xml` never declares `USE_EXACT_ALARM`, `USE_FULL_SCREEN_INTENT` or `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`. CI never sees the merged manifest, so the pin guards what you declare.

> **After the upgrade to 0.87:** from 0.85 the Jest preset lives in `@react-native/jest-preset` — change `preset` in `jest.config.js`; the OneSignal stub in `jest.setup.js` is unaffected.

| Check | Android 16 AVD | Samsung / Xiaomi phone | iPhone (sim + device) |
|---|---|---|---|
| Fresh install: no dialog until the first order; deny → "Turn on" opens Settings | ☐ | ☐ | ☐ |
| Push arrives swiped away, and after 1 h idle with the screen off | ☐ | ☐ | device |
| Tap lands on the order, cold and warm | ☐ | ☐ | ☐ |
| `time-sensitive` breaks through a Focus | — | — | device |

## 3. In-App Messages

| | OneSignal In-App Messages | Firebase In-App Messaging | In-house banners |
|---|---|---|---|
| Status | Linked today (`OneSignalInAppMessages` 5.5.0 pod) | `@react-native-firebase/in-app-messaging` 26.4.0 (2026-09-05), New-Arch; no deprecation notice | JS only |
| Rendered by | the native SDK (HTML in a WebView) | the native SDK (cards, banners, modals, images) | your React components |
| Delivery | pulled at session start; a new session after ≥ 30 s in background; "delivered to all mobile Subscriptions in the target Segment, regardless of push opt-in status" | triggered by Analytics events | your API |
| Triggers | app open, session duration, time since last message, `addTrigger` from JS | Analytics events | anything |
| Cost here | 1 day config _(est.)_ | forces RNFirebase 24.0.0 → 26.x | 0.5–2 days _(est.)_ |
| Theme, 320 dp, Hindi | authored in the dashboard — outside the app's tokens | same | fully yours |

What is native and what is JS: in both SDK routes the message is drawn natively; JS only sets triggers and listens for clicks. **Verdict: OneSignal IAM** — it is already linked and needs no code, while Firebase IAM would duplicate it and drag a two-major RNFirebase upgrade along.

Steps:

1. Keep the `app_version` trigger; after sign-in add `OneSignal.InAppMessages.addTrigger('role', role)`.
2. Pull the click logic into a pure `iamAction(actionId, os)` that returns the store URL, test it red → green, and let [[02-phase-2-dependency-diet]]'s `<queries>` fix revive `update_app` on Android 11+.
3. Content: service messages only — price revisions, holiday timings, "update available". Anything promotional gets the same in-app opt-in and opt-out that guideline 4.5.4 demands for push (house rule, by analogy).
4. Hindi: author an `hi` variant of each message and target it with a `lang` trigger set from the app's language setting (house decision).

Source: https://documentation.onesignal.com/docs/en/in-app-messages-setup

## 4. Local Notifications

The old default is dead: `@notifee/react-native` stopped at 9.1.8 (2024-12-20) and its repository was archived on 2026-04-07; its README says "Notifee is no longer actively maintained" and points to expo-notifications or **react-native-notify-kit**.

| | react-native-notify-kit |
|---|---|
| Version | 10.8.0 (npm, 2026-09-29; the React Native Directory still showed 10.7.2 of 2026-09-23 that day) |
| Architecture | "TurboModules only — no legacy Bridge support"; RN ≥ 0.73 |
| API | claims 100 % compatibility with `@notifee/react-native` |
| Extras | exact-alarm fallback; foreground-service types via a config plugin |
| Maturity | repository created 2026-03-30; 214 stars, 0 open issues — young, watch it. No `ProgressStyle` / promotion support found, so §6 stays in Kotlin |

Source: https://github.com/marcocrupi/react-native-notify-kit · https://github.com/invertase/notifee

```bash
yarn add react-native-notify-kit@10.8.0
cd ios && bundle exec pod install && cd ..
```

House rule for new native packages: use the package's shipped Jest mock if it has one, else a hand stub in `jest.setup.js`.

### Exact alarms: don't

| Rule | Detail |
|---|---|
| `SCHEDULE_EXACT_ALARM` (API 31) | not pre-granted on fresh installs from Android 14 |
| `USE_EXACT_ALARM` (API 33) | auto-granted but restricted by Play policy to limited cases — DZZLO doesn't qualify |
| Inexact options | `setWindow` (≥ 10 min on Android 12+), `setAndAllowWhileIdle` |
| Doze | defers alarms to maintenance windows; `…AllowWhileIdle` fires at most once per 9 min per app |
| Restricted bucket | one alarm a day, even while charging |

A payment-due reminder is day-granular: "within a few minutes of 10:00 IST" is fine. Never ask for exact-alarm permission.

### The payment-due reminder

The pure part first (Tier 1, red before green): `src/helpers/Reminders/reminderFor.js` takes `(invoice, now)` and returns `{ id, fireAt, title, body }` or `null` — 10:00 IST on the day before the due date, `null` when that moment has passed or the invoice is paid, the id derived from the invoice id. Compute in IST explicitly; the test must pass under `TZ=UTC` too.

The facade calls Notifee's API names, which the fork keeps — confirm them against its README at install:

```js
// src/helpers/Reminders/index.js
import notifee, { AndroidImportance, TriggerType } from 'react-native-notify-kit';

export const ensureReminderChannel = t =>
  notifee.createChannel({ id: 'reminders', name: t.channelName, importance: AndroidImportance.DEFAULT });

export const scheduleReminder = ({ id, fireAt, title, body }) =>
  notifee.createTriggerNotification(
    { id, title, body, android: { channelId: 'reminders' } },
    { type: TriggerType.TIMESTAMP, timestamp: fireAt },   // no exact-alarm request, ever
  );

export const cancelReminder = id => notifee.cancelTriggerNotification(id);
```

Stale data is the real risk: an invoice paid this morning must not nag tonight. When the Payments list refreshes, cancel the reminders of every settled invoice — a Tier 2 test with MSW proves "paid → `cancelTriggerNotification`". Body text names the invoice, not the amount (house decision; a lock screen is public). Parity: identical on both platforms.

## 5. iOS Live Activities

### 5.1 The facts that shape the design

| Fact | Value |
|---|---|
| `Activity`, `NSSupportsLiveActivities` | iOS 16.1 |
| `NSSupportsLiveActivitiesFrequentUpdates`, `frequentPushesEnabled` | iOS 16.2 |
| `pushToStartToken` (start from the server) | iOS 17.2 |
| Broadcast `PushType.channel(_:)` | iOS 18.0 |
| Scheduled start (`request(…start:)`) | iOS 26.0 |
| Lifetime | "active for up to eight hours"; stays on the Lock Screen "for a maximum of 12 hours" |
| Size | static + dynamic data "can't exceed a combined size of 4 KB"; taller than 160 pt may be truncated |
| Limits | "it can't access the network or receive location updates" |
| Push | ActivityKit issues per-activity tokens; `apns-push-type: liveactivity`, topic `<bundle id>.push-type.liveactivity`; payload keys `content-state`, `stale-date`; tokens can change mid-activity |
| iOS 27 | shown in the Dynamic Island in portrait **and** landscape; `@Environment(\.isDynamicIslandLimitedInWidth)`; StandBy scales the Lock Screen view to 200 % |
| OneSignal | react-native-onesignal ≥ 5.2.0; `.p8` APNs key required — p12 certificates are not supported for Live Activities |

Source: https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities · https://developer.apple.com/videos/play/wwdc2026/223/

### 5.2 The DZZLO order card

```
┌ Lock Screen ─────────────────────────────────────────────┐
│ Order #2417 · HSD · 2,000 L                  ETA 25 min  │
│ ●━━━━━━━━●━━━━━━━━●━━━━━━━━○                              │
│ Placed    Confirmed  Dispatched  Delivered                │
└───────────────────────────────────────────────────────────┘
 Dynamic Island: compact = pump glyph + "25 min" · minimal = pump glyph
```

- **Static attributes:** `orderId`, `orderNo`, `product` (HSD | MS), `litresText` — formatted by JS with the house helpers.
- **Dynamic state:** `stage` (placed | confirmed | dispatched | delivered), `etaText`. The ETA is computed on the server — the card can neither fetch nor locate.
- **When:** start when the dealer dispatches, with placed and confirmed drawn as done. A same-day order fits the 8-hour window; an order that waits days stays an ordinary push (iOS 26 scheduled start is a later option). End at delivered.
- **Language:** the payload carries keys, not words; `DzzloWidgets` localises the labels (en, hi) — smaller payloads, correct Hindi.
- **Who starts it:** the server by push-to-start (iOS 17.2+); on iOS 16.1–17.1 the app starts it when the customer opens that order.

### 5.3 The deployment-target gate

The app targets iOS 15.1 (`IPHONEOS_DEPLOYMENT_TARGET`, every configuration in `project.pbxproj`, e.g. line 453) — RN 0.84's `min_ios_version_supported`. Live Activities need 16.1.

| Option | How | Cost |
|---|---|---|
| **A — raise the app to iOS 16.1** (recommended) | one build setting; the Podfile already lifts pods to the app minimum | iOS 15 users lose updates |
| B — keep 15.1 | `DzzloWidgets` at 16.1, `@available` gates in Swift, `Platform.Version` checks in JS | every surface carries two code paths |

**House decision, not a measurement:** no India iOS-version data was found, and DZZLO's own iOS share is unknown — the user base is described as Android-heavy. Before choosing, read DZZLO's iOS-version split in App Store Connect analytics. Note too that Expo's bare-install docs set iOS 16.4, so the optional Expo track (§7) raises the floor anyway.

### 5.4 Build it: the `DzzloWidgets` target

1. **Xcode → File → New → Target → Widget Extension**, name `DzzloWidgets`, tick "Include Live Activity". Bundle id `in.vsyst.dzzlooms.DzzloWidgets` (extensions must prefix the host's id). Team `YT955YZMZU`, automatic signing. This target also hosts Phase 6's widgets and Control.
2. **Podfile**, beside the NSE block:

   ```ruby
   target 'DzzloWidgets' do
     pod 'OneSignalXCFramework/OneSignalLiveActivities', '>= 5.0.0', '< 6.0'
   end
   ```

3. **App `Info.plist`:** `<key>NSSupportsLiveActivities</key><true/>`.
4. **App Group:** add `group.in.vsyst.dzzlooms.shared` to the app and to `DzzloWidgets` now — Phase 6's widgets read it. The account holder registers the group and uploads the `.p8` key to OneSignal; neither is a code change.
5. **The view** — OneSignal's `DefaultLiveActivityAttributes` (an `ActivityAttributes` type the SDK owns) keeps a `data: [String: AnyCodable]` dictionary in both the attributes and the `ContentState`, read with `asString()` / `asDouble()`; `onesignalWidgetURL(_:context:)` records taps. All verified in the installed pod's Swift interface (5.5.0), 2026-09-30:

   ```swift
   // ios/DzzloWidgets/DzzloOrderLiveActivity.swift
   import ActivityKit
   import SwiftUI
   import WidgetKit
   import OneSignalLiveActivities

   struct DzzloOrderLiveActivity: Widget {
     var body: some WidgetConfiguration {
       ActivityConfiguration(for: DefaultLiveActivityAttributes.self) { context in
         let card = OrderCard(context.attributes.data, context.state.data)
         OrderCardView(card: card)                                  // Lock Screen, StandBy, banner
           .activityBackgroundTint(Color("Surface"))                // asset mirrors src/theme
           .onesignalWidgetURL(DzzloLinks.order(card.orderId), context: context)
       } dynamicIsland: { context in
         let card = OrderCard(context.attributes.data, context.state.data)
         return DynamicIsland {
           DynamicIslandExpandedRegion(.leading) { Text(card.orderNo) }
           DynamicIslandExpandedRegion(.trailing) { Text(card.etaText ?? "") }
           DynamicIslandExpandedRegion(.bottom) { StageBar(step: card.stage.step) }
         } compactLeading: {
           Image(systemName: "fuelpump")
         } compactTrailing: {
           Text(card.etaText ?? card.stage.shortLabel)
         } minimal: {
           Image(systemName: "fuelpump")
         }
       }
     }
   }

   struct OrderCard {
     let orderId, orderNo: String
     let stage: OrderStage
     let etaText: String?
     init(_ a: [String: AnyCodable], _ s: [String: AnyCodable]) {
       orderId = a["orderId"]?.asString() ?? ""
       orderNo = a["orderNo"]?.asString() ?? ""
       stage = OrderStage(raw: s["stage"]?.asString())              // pure, unit-tested
       etaText = s["etaText"]?.asString()
     }
   }
   ```

   `DzzloLinks` is the URL helper that [[08-phase-8-instant-experiences-and-links]] defines. `OrderStage` lives in its own file with no OneSignal import, so the XCTest bundle can compile it.
6. **JS** — a library wrapper, so it lives in `src/helpers/`, not `src/native/`:

   ```js
   // src/helpers/OneSignal/liveActivity.js
   import { Platform } from 'react-native';
   import { OneSignal } from 'react-native-onesignal';
   import { orderCardPayload } from './orderCardPayload';     // pure, Tier 1

   const supported = () => Platform.OS === 'ios' && parseFloat(Platform.Version) >= 16.1;

   export const setupLiveStatus = () => {
     if (supported()) OneSignal.LiveActivities.setupDefault({ enablePushToStart: true, enablePushToUpdate: true });
   };

   export const startOrderCard = order => {
     if (!supported()) return false;
     const { activityId, attributes, content } = orderCardPayload(order);
     OneSignal.LiveActivities.startDefault(activityId, attributes, content);
     return true;
   };
   ```

7. **Server (`dzzlo_oms_api`):** push-to-start is `POST /apps/{app_id}/activities/activity/DefaultLiveActivityAttributes` with `event_attributes` and `event_updates`; OneSignal holds the ActivityKit tokens, so the API never touches APNs. The update and end calls follow OneSignal's Live Activity API — their endpoint and field names are not captured in this course's sources; read them from OneSignal's docs when you build.

Custom attributes are possible later: the pod exposes a public `OneSignalLiveActivityAttributes` protocol and a Swift `setup(_:options:)` (iOS 16.1), but the JS SDK only starts the default type, so a custom card means Swift start code. Stay on `DefaultLiveActivityAttributes` for v1. Source: https://documentation.onesignal.com/docs/en/cross-platform-live-activity-setup

### 5.5 Frequency and guideline 4.5.3

Guideline 4.5.3: "Do not use Apple Services to spam, phish, or send unsolicited messages to customers, including Game Center, Push Notifications, Live Activities, etc." So: one card per real order, 4–5 updates in its life, never a price promotion. `NSSupportsLiveActivitiesFrequentUpdates` is not needed at that rate. Apple's exact push budgets for Live Activities were not found (gap) — measure, don't guess.

### 5.6 Tests and the device run

| Layer | Red first | Then green |
|---|---|---|
| Jest, Tier 1 | `orderCardPayload`: stage keys map, missing ETA → no key, **serialised JSON < 3,500 bytes** (margin under 4 KB) | the pure builder |
| Jest, Tier 1 | `startOrderCard` is a no-op on Android and on iOS < 16.1 (swap `Platform.OS` / `Platform.Version` per case, as `src/i18n/__tests__/deviceLocale.test.js` does) | the wrapper |
| XCTest | `OrderStage(raw:)`: unknown or `nil` → `.placed`; `step` 0…3; labels resolve in en and hi | the enum, in a file compiled into `DzzloWidgets` and the test bundle |
| Device | layout: in-app start on the simulator (to confirm on the first run); push-to-start and updates: a physical iPhone on iOS 17.2+ | — |

Walk the card through all four stages, in light and dark, en and hi, portrait and landscape (iOS 27 shows it in both), then check the Dynamic Island's compact, minimal and expanded forms and StandBy.

## 6. Android Live Updates

### 6.1 The platform, versioned

| API | Level (SDK `api-versions.xml`, verified 2026-09-30) |
|---|---|
| `Notification.ProgressStyle` (`Segment`, `Point`), `setShortCriticalText`, `canPostPromotedNotifications()`, `hasPromotableCharacteristics()`, `FLAG_PROMOTED_ONGOING` | 36 (Android 16) |
| `setRequestPromotedOngoing`, `EXTRA_REQUEST_PROMOTED_ONGOING`, `POST_PROMOTED_NOTIFICATIONS` | **36.1** |
| `Notification.MetricStyle`, `Notification.Metric` | 37 (Android 17) |
| AndroidX `NotificationCompat.ProgressStyle` + `setRequestPromotedOngoing` + `setShortCriticalText` | in `androidx.core:core` 1.17.0 — already in the app's graph |

**CONFLICT, recorded:** OneSignal says promotion needs "Android 16 QPR1 (API 36.1)"; Google's Android 16 page says API 36.1 is **QPR2**. The SDK agrees on the number (36.1), not on the release name. Pixels showed the full treatment from QPR1 (Sep 2025): a status-bar chip, the top of the shade, the lock screen and the always-on display.

Rendering beyond Pixel: Samsung One UI 8 feeds Live Updates into the Now Bar (its beta 3 needed a developer option, "Live notifications for all apps"; whether stable One UI gates it is **unverified**), and One UI 9 adds the MetricStyle categories. Xiaomi HyperOS 3.1's Super Island renders the standard API without Xiaomi code (secondary reporting). ColorOS, OxygenOS and OriginOS were not researched.

### 6.2 The rules

- **Eligibility — all required:** `POST_PROMOTED_NOTIFICATIONS` (a normal permission, no prompt); `setRequestPromotedOngoing(true)`; ongoing, with a `contentTitle`; style Standard, BigText, Call, Progress or Metric; no custom `RemoteViews`, not a group summary, no `setColorized(true)`; channel above `IMPORTANCE_MIN`.
- **Status chip:** text from `setShortCriticalText()`; at most 96 dp wide; text under 7 characters shows whole, and if less than half fits only the icon shows — so "25 min", not "ETA 25 minutes".
- **Use:** ongoing, user-initiated, time-sensitive. Appropriate: active food delivery, rideshare, navigation. **Not** appropriate: ads, chat, alerts, **package tracking**, "quick access to app features", ambient information, activities started by other parties. Never repost an update the user dismissed.
- **Template only:** you choose the style; the system draws it.

Source: https://developer.android.com/develop/ui/views/notifications/live-update

For DZZLO that means: promote **only** from dispatched to delivered, while a tanker is actually moving. An order waiting days for a slot is "package tracking" — an ordinary push.

### 6.3 The OneSignal path: a Kotlin `NotificationServiceExtension`

OneSignal's Android Live Updates guide: a native `INotificationServiceExtension` parses a `live_notification` object in the push `data` — `key`, `event` (start | update | end), `event_attributes`, `event_updates` — re-notifies under a constant Android id and ends with `cancel(id)`; send the same collapse id across events and a short `ttl` on updates; requires OneSignal SDK 5.1.14+ and compileSdk 36; on older Android the notification "updates in place without promotion". The guide doesn't cover React Native, so this is Kotlin. Interface names below are from OneSignal core 5.7.6 (`javap`, 2026-09-30); a message's `data` reaches the app as `additionalData`, exactly as today's click handler reads `dealer` and `customer`.

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/notifications/NotificationServiceExtension.kt
package `in`.vsyst.dzzlooms.notifications

import androidx.core.app.NotificationManagerCompat
import com.onesignal.notifications.INotificationReceivedEvent
import com.onesignal.notifications.INotificationServiceExtension

class NotificationServiceExtension : INotificationServiceExtension {
  override fun onNotificationReceived(event: INotificationReceivedEvent) {
    val live = event.notification.additionalData?.optJSONObject("live_notification")
      ?: return                                      // an ordinary push: OneSignal shows it
    val update = LiveOrderUpdate.parse(live) ?: return
    event.preventDefault()                            // we draw this one ourselves
    val manager = NotificationManagerCompat.from(event.context)
    if (update.event == "end") { manager.cancel(update.androidId); return }
    if (manager.areNotificationsEnabled()) {
      manager.notify(update.androidId, LiveOrderNotification.build(event.context, update))
    }
  }
}
```

```kotlin
// LiveOrderNotification.kt — one builder, two branches
object LiveOrderNotification {
  private val STAGES = listOf("placed", "confirmed", "dispatched", "delivered")

  fun build(context: Context, u: LiveOrderUpdate): Notification {
    val step = STAGES.indexOf(u.stage).coerceAtLeast(0)
    val b = NotificationCompat.Builder(context, "live_status")
      .setSmallIcon(R.drawable.ic_stat_dzzlo)          // monochrome; add it
      .setContentTitle(u.title)                        // required for promotion
      .setContentText(u.text)
      .setOngoing(u.stage != "delivered")
      .setOnlyAlertOnce(true)
      .setContentIntent(OrderIntents.open(context, u.orderId))
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.BAKLAVA) {          // API 36
      b.setStyle(
        NotificationCompat.ProgressStyle()
          .setProgressSegments(STAGES.map { NotificationCompat.ProgressStyle.Segment(25) })
          .setProgress((step + 1) * 25),
      ).setRequestPromotedOngoing(true)                // honoured from API 36.1
        .setShortCriticalText(u.etaText)               // "25 min"
    } else {
      b.setProgress(STAGES.size - 1, step, false)      // API 24–35: a plain ongoing bar
    }
    return b.build()
  }
}
```

Whether the compat `ProgressStyle` degrades by itself below 36 was not verified, hence the explicit branch. The server repeats the title fields in every `event_updates`, so the extension stays stateless — our design choice, not OneSignal's rule. Then the manifest:

```xml
<uses-permission android:name="android.permission.POST_PROMOTED_NOTIFICATIONS" />
<application …>
  <meta-data android:name="com.onesignal.NotificationServiceExtension"
             android:value="in.vsyst.dzzlooms.notifications.NotificationServiceExtension" />
</application>
```

The key string `com.onesignal.NotificationServiceExtension` is present in OneSignal core 5.7.6 (verified 2026-09-30); the `<meta-data>` form follows OneSignal's Android docs.

### 6.4 Alternatives and the fallback

| Route | Status | Verdict |
|---|---|---|
| OneSignal + Kotlin extension (above) | documented; one push pipe | **build this** — 3–5 days _(est.)_ |
| FCM data message → build the notification locally (Kotlin `FirebaseMessagingService`, or `@react-native-firebase/messaging` 26.4.0) | works, but you would own token registration and delivery analytics that OneSignal already owns — and a handler that fails to post turns data-only pushes into FCM's deprioritised pattern | no _(opinion)_ |
| Voltra 2.3.2 (2026-09-22) | Android Live Updates merged 2026-09-28 (PRs #325, #326; ADR 0008 accepted, MetricStyle with a "compileSdk 37 floor") but **unreleased**. A freeCodeCamp handbook (2026-07-14) said no library supports Live Updates — true when written | watch item — re-check its release notes |
| react-native-notify-kit | no `ProgressStyle` / promotion support found | no |

The fallback is not an afterthought: India's Android mix in Aug 2026 was 16 = 24.11 %, 15 = 23.28 %, 13 = 13.85 %, 14 = 12.14 %, 12 = 9.41 %, 11 = 8.81 % (StatCounter). About three in four devices get the `else` branch, so build and test it first; promotion is the bonus for the ~quarter on Android 16 whose skin renders it.

Source: https://documentation.onesignal.com/docs/en/android-live-notifications · https://github.com/callstackincubator/voltra/pull/326 · https://gs.statcounter.com/android-version-market-share/mobile/india

### 6.5 Play policy limits

Live Updates need only `POST_PROMOTED_NOTIFICATIONS`, a normal permission users can switch off per app. **CONFLICT:** Google's Live Updates guide (as our research read it) names the settings deep link `Settings.ACTION_MANAGE_APP_PROMOTED_NOTIFICATIONS`, but the SDK's `api-versions.xml` (36, 36.1, 37) has no such constant — it has `Settings.ACTION_APP_NOTIFICATION_PROMOTION_SETTINGS` (API 36). Code against the SDK. No Play Console form was found; Google's usage criteria are platform guidance, and misuse costs you the user's permission. No foreground service is needed — pushes drive every update — and full-screen intents are for calling and alarm apps only.

### 6.6 Tests and the device run

```groovy
// android/app/build.gradle — RN core's own test stack as the reference versions
dependencies {
  testImplementation "junit:junit:4.13.2"
  testImplementation "org.robolectric:robolectric:4.15.1"
}
android { testOptions { unitTests { includeAndroidResources = true } } }
```

1. **Red first, JUnit + Robolectric:** `LiveOrderUpdateTest` — `parse` accepts start/update/end, rejects a missing `key`, maps one `key` to one `androidId` (Robolectric supplies the real `org.json`). Then the fallback branch at an SDK level your Robolectric supports: ongoing, title, progress `(3, step)`. Whether Robolectric 4.15.1 models API 36's `ProgressStyle` is **unverified** — prove that branch on a device.
2. **Device:** an Android 16 emulator on a **36.1+** image (the promotion setter is 36.1): start → update → end from OneSignal's dashboard; check chip, shade and lock screen. Then an API 34 emulator for the plain bar, and a Samsung / Xiaomi phone if one is at hand.

```bash
cd android && ./gradlew :app:testDebugUnitTest
```

> **After the upgrade to 0.87:** AGP 9 and compileSdk 37 arrive, so `Notification.MetricStyle` (API 37) compiles — keep it out of v1, and re-run this suite after the AGP bump.

## 7. After the Upgrade, the Expo Track, and Exercises

> **After the upgrade to 0.87:** three touch points — the Jest preset (§2.10), AGP 9 + compileSdk 37 (§6.6), and `<React/…>` framework-style imports if the app moves to Swift Package Manager. `DzzloWidgets` links OneSignal pods, not React, so SPM leaves it alone.

> **Optional Expo track** (only on an Expo-paired React Native: SDK 56 ↔ 0.85, 57 ↔ 0.86, 58 preview ↔ 0.88 — nothing pairs with 0.84 or 0.87): `expo-notifications` 57.0.21 is the migration target Notifee's README names, and SDK 58 adds forwarding to other `UNUserNotificationCenterDelegate`s plus `threadIdentifier` grouping — it could replace notify-kit for §4 while OneSignal keeps push. `expo-widgets` (stable since SDK 56, **iOS only**; Android widgets from SDK 58) can author the Live Activity in JSX with `createLiveActivity`, `start` / `update` / `end`, APNs push updates and push-to-start (17.2+), and SDK 58's `staleDate` — but pick **one** owner of the ActivityKit lifecycle: OneSignal's `startDefault` flow or expo-widgets, never both _(inference)_. `expo-live-activity` was archived on 2026-06-01 — don't adopt it. Installing Expo modules into this bare app sets the iOS deployment target to 16.4 in the current docs.

### Exercises

**7.1 — Move the prompt.** Write the `nextPermissionStep` table test (red), make it green, delete the start-up call, then fresh-install on the Android 16 AVD and on an iPhone simulator. Deliverable: the Jest output and a screen recording where no dialog appears until the first order.

**7.2 — Land on the order.** Test `routeForNotification` red → green, send a test push with `orderId` and `path` from the OneSignal dashboard, and record where a cold tap and a warm tap land.

**7.3 — Channel audit.** Create the five channels, then screenshot Settings → Apps → DZZLO → Notifications in English and Hindi. Confirm `live_status` isn't `MIN`.

**7.4 — The OEM matrix.** On one Xiaomi or Samsung phone, send three pushes — app in Recents, swiped away, after an hour idle with the screen off — and record arrival times in a table. That table is the evidence the OEM guide screen needs.

**7.5 — A reminder in airplane mode.** Schedule a reminder two minutes out from a debug screen, enable airplane mode, kill the app, and note when it fires. Then mark the invoice paid and prove the reminder is cancelled.

**7.6 — The card on the Lock Screen.** First make the `orderCardPayload` size test fail by adding line items, then remove them — the red run is the lesson. Build `DzzloWidgets`, start a card from the app on a simulator, then push-to-start one on a physical iPhone. Deliverable: screenshots of the Lock Screen, compact, minimal and expanded forms, en and hi.

**7.7 — Chip and fallback.** Drive start → update → end on an Android 16 (36.1+) emulator and on an API 34 emulator. Deliverable: a chip-and-shade screenshot, a plain-bar screenshot, and the `testDebugUnitTest` report.

## Lab Notes

2026-09-29/30 — read-only verification; nothing was built, installed or committed:

- OneSignal RN 5.4.1 typings, the `OneSignalLiveActivities` 5.5.0 Swift interface and OneSignal Android core 5.7.6 (`javap`) confirm every OneSignal call in this phase — including `setup(_:options:)` for custom attributes (iOS 16.1), `IMutableNotification.setExtender(NotificationCompat.Extender)` and `INotificationReceivedEvent.preventDefault()`.
- `androidx.core:core` 1.17.0 carries the compat `ProgressStyle` (`Segment(int)`, `Point(int)`), `setRequestPromotedOngoing` and `setShortCriticalText`; the SDK's settings deep link is `ACTION_APP_NOTIFICATION_PROMOTION_SETTINGS`, not the name our research quoted.
- The Time Sensitive entitlement key was not found in Xcode 27 by string search — it stays **unverified**.

**Next:** [[06-phase-6-widgets-shortcuts-and-intents]] — the same `DzzloWidgets` target grows a Daily Summary widget and a Control; capstone B in [[10-capstones]] runs order status → push → Live Activity + Live Update end to end.
