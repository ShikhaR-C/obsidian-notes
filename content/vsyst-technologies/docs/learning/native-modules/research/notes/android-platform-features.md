# Android platform capabilities a React Native business app can adopt through native code (as of 29 Sept 2026)

Scope: the Android twins of iOS App Intents/Siri, Live Activities, App Clips, widgets, Controls, PHPicker, the VisionKit scanner and MapKit, plus notifications, files, images, maps and platform plumbing. The target is dzzlo_oms_app: RN 0.84.1 (New Architecture), Kotlin 2.1.20, minSdk 24, compile/target SDK 36, package `in.vsyst.dzzlooms`, OneSignal push, portrait-only, India market.

Conventions:
- "API n" means Android SDK level n.
- **[unverified]** means I could not confirm the claim from a primary source in this session.
- Library status comes from the reactnative.directory API (`https://reactnative.directory/api/libraries?search=<name>`), queried 29 Sep 2026.
  - "dirNA" is the directory's declared `newArchitecture` flag; "ghNA" is its GitHub-detected flag.
  - Expo-monorepo packages show ghNA = false because detection doesn't run on the monorepo; Expo modules do run on the New Architecture.
- Section 1 holds the per-capability briefs: what it is, versions, building blocks, example and fallback. Section 2 covers RN integration and effort, section 3 Play policy, and section 4 India/OEM effects.

## 1. For each iOS feature (App Intents/Siri, Live Activities, App Clips, widgets, Controls, PHPicker, VisionKit scanner, MapKit), what is the closest Android twin, how close is it, and what has no twin?

### Takeaway
Close twins exist for five iOS features:
- widgets → app widgets / Jetpack Glance;
- Controls → Quick Settings tiles;
- PHPicker → Photo Picker, backported via Play services;
- VisionKit scanner → ML Kit Document Scanner;
- MapKit → Maps SDK for Android.

Live Activities has a real but narrower twin: Android 16 Live Updates (`ProgressStyle`), with `MetricStyle` added in 17. Samsung One UI 8 and Xiaomi HyperOS 3.1 render them.

Two iOS features have no production twin as of September 2026:
- **App Intents/Siri.** Google Assistant has been removed from Android phones since 4 Sep 2026. The App Actions docs don't mention Gemini. AppFunctions (API 36, Jetpack alpha) is the structural twin, but Gemini can call it only in a private preview.
- **App Clips.** Play Instant ended in Dec 2025. The practical substitute is a mobile web page plus UPI Intent, with an App Link into the app when it is installed.

### Cited Findings

#### 1.0 Platform baseline (the versions that gate everything below)
- Android 17 (API 37) launched on 16 June 2026 and is rolling out to Pixel 6 and later — [Android Developers Blog: "Android 17 is here"](https://android-developers.googleblog.com/2026/06/Android-17.html); [9to5Google](https://9to5google.com/2026/06/16/google-android-17-pixel-launch/)
- The Android 17 hub page already lists the Android 17 QPR1 and QPR2 betas (API 37.1 / 37.2); the page was last updated 2026-07-01 — [Android 17 hub](https://developer.android.com/about/versions/17)
- Android 16 had a Q2 2025 major release and a Q4 2025 minor release. Android 16 QPR2 is API 36.1, checked with `SDK_INT_FULL`, `VERSION_CODES_FULL` and `Build.getMinorSdkVersion()` — [Android 16 features](https://developer.android.com/about/versions/16/features)
- Android 16 QPR1 began rolling out to Pixels on 3 Sep 2025 — [9to5Google](https://9to5google.com/2025/09/03/android-16-qpr1-pixel/)
- India mobile Android version share, Aug 2026 (the remaining ~8.4 %, including Android 10-and-older and 17, isn't broken out) — [StatCounter India](https://gs.statcounter.com/android-version-market-share/mobile/india):
  - Android 16: 24.11 %
  - Android 15: 23.28 %
  - Android 13: 13.85 %
  - Android 14: 12.14 %
  - Android 12: 9.41 %
  - Android 11: 8.81 %

#### 1.1 App Intents / Siri → App Shortcuts, App Actions, AppFunctions, Assist content
- **App Shortcuts**: static and dynamic shortcuts arrived in API 25, pinned shortcuts in API 26 — [App shortcuts guide](https://developer.android.com/develop/ui/views/launch/shortcuts)
  - Use `ShortcutManager`, or `ShortcutManagerCompat` from AndroidX.
  - Static shortcuts live in `res/xml/shortcuts.xml`, referenced by `<meta-data android:name="android.app.shortcuts">` on a launcher activity.
  - Most launchers show about 4 shortcuts (`getMaxShortcutCountPerActivity()`).
  - Pinned shortcuts are unlimited; the app can disable them but not remove them.
  - "Never include sensitive user info in shortcut metadata."
- **App Actions**: `<capability>` entries in `shortcuts.xml` bind built-in intents (BIIs) to deep links, and `androidx.core:core-google-shortcuts` pushes dynamic shortcuts to Google surfaces — [App shortcuts guide](https://developer.android.com/develop/ui/views/launch/shortcuts); [App Actions overview](https://developer.android.com/develop/devices/assistant/overview)
  - As of 29 Sep 2026 the App Actions overview still presents them as current, with no deprecation notice and no mention of Gemini — [App Actions overview](https://developer.android.com/develop/devices/assistant/overview)
  - The legacy `actions.xml` is deprecated in favour of `shortcuts.xml` — [actions.xml (deprecated)](https://developers.google.com/assistant/app/legacy/action-schema)
- **Assistant removal**: Google began removing Google Assistant from Android phones, tablets, Wear OS, headphones and Android Auto on 4 Sep 2026. By 28 Sep the Gemini app no longer offers "Switch to Google Assistant" — [9to5Google, 28 Sep 2026](https://9to5google.com/2026/09/28/google-assistant-gemini-android/); [Business Today, 6 Aug 2026](https://www.businesstoday.in/amp/technology/news/story/google-assistant-to-be-replaced-by-gemini-starting-september-on-android-and-wearos-547570-2026-08-06); [Android Headlines](https://www.androidheadlines.com/2026/09/google-assistant-killed-android-gemini.html)
- **AppFunctions** is an Android 16+ (API 36) platform API with a Jetpack library, `androidx.appfunctions`, described as the mobile equivalent of MCP tools — [AppFunctions overview](https://developer.android.com/ai/appfunctions)
  - Annotate Kotlin functions with `@AppFunction` and parameter/return types with `@AppFunctionSerializable`.
  - Implement `AppFunctionService` with `@AppFunctionServiceEntryPoint`; a KSP compiler generates an XML schema.
  - Callers need `EXECUTE_APP_FUNCTIONS`; they discover and execute functions through `AppFunctionManager` (e.g. `isAppFunctionEnabled`).
  - Test with `adb shell cmd app_function …`.
  - Status: "experimental preview". "As of May 2026, AppFunctions integration with Gemini is in a private preview with trusted testers." An Early Access Program form is open.
- The Android 17 launch post calls the AppFunctions Jetpack library "currently in alpha" — [Android 17 blog](https://android-developers.googleblog.com/2026/06/Android-17.html)
- Feb 2026: the first Gemini + AppFunctions integration shipped with Samsung Gallery on the Galaxy S26, expanding to One UI 8.5+. A separate "UI automation" preview lets Gemini operate food-delivery, grocery and rideshare apps with no developer work, on the Galaxy S26 and select Pixel 10 phones, starting in the US and Korea — [Android Developers Blog, Feb 2026](https://android-developers.googleblog.com/2026/02/the-intelligent-os-making-ai-agents.html)
- **Assist API**: an activity can override `onProvideAssistContent()` to give the assistant structured context for the current screen, as a URI or schema.org JSON-LD — [Optimizing contextual content for the Assistant](https://developer.android.com/training/articles/assistant)
  - Gemini's "screen context" can infer when to use what is on screen — [Android Authority](https://www.androidauthority.com/gemini-screen-context-3625824/)
- Android 17 adds a Handoff API (`Activity.setHandoffEnabled()`, `onHandoffActivityDataRequested()`) for cross-device continuity — [Android 17 features](https://developer.android.com/about/versions/17/features)

#### 1.2 Live Activities → Live Updates
- Android 16 (API 36) added `Notification.ProgressStyle`, with `Segment` for milestones and `Point` for states, aimed at "rideshare, delivery and navigation" journeys — [Android 16 features](https://developer.android.com/about/versions/16/features)
- The full promoted Live Updates treatment arrived with Android 16 QPR1 on Pixels (Sep 2025): a status-bar chip, the top of the notification shade, the lock screen and the always-on display — [Android Authority](https://www.androidauthority.com/android-16-qpr1-live-updates-3573399/); [9to5Google](https://9to5google.com/2025/09/03/android-16-qpr1-pixel/)
- **Eligibility** (every item is required; OEMs may add criteria) — [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update):
  - Declare `android.permission.POST_PROMOTED_NOTIFICATIONS`, a normal permission with no prompt.
  - Call `setRequestPromotedOngoing(true)` or set `EXTRA_REQUEST_PROMOTED_ONGOING`.
  - The notification is ongoing and has a `contentTitle`.
  - Its style is Standard, BigText, Call, Progress or Metric.
  - No custom `RemoteViews`, not a group summary, and `setColorized(true)` isn't called.
  - The channel isn't `IMPORTANCE_MIN`.
- Checks and settings: `NotificationManager.canPostPromotedNotifications()`, `Notification.hasPromotableCharacteristics()`, `FLAG_PROMOTED_ONGOING`, and the settings deep link `Settings.ACTION_MANAGE_APP_PROMOTED_NOTIFICATIONS` — [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update)
- **Status chip** — [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update):
  - Content comes from `setShortCriticalText()`, `setWhen()` (a countdown, shown when the time is at least 2 minutes ahead) and `setUsesChronometer` / `setChronometerCountdown`.
  - Maximum width is 96 dp. Text under 7 characters is shown whole; if less than 50 % of the text fits, only the icon is shown.
- **Usage criteria**: the activity must be ongoing, user-initiated and time-sensitive — [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update)
  - Appropriate: active food delivery, rideshare, navigation, a boarding pass once boarding is imminent.
  - Not appropriate: ads, chat, alerts, **package tracking**, "quick access to app features" (use widgets or Quick Settings tiles instead), ambient information, activities started by other parties.
  - Don't repost a dismissed update; unwanted updates lead users to revoke permission.
- Updating means calling `notify()` again with the same ID. AndroidX has `NotificationCompat.Builder#setRequestPromotedOngoing` — [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update)
- Android 17 adds `MetricStyle` / `Notification.Metric`: up to three readings, aimed at health and fitness, timers and travel. Semantic colours come via `Notification.createSemanticStyleAnnotation()` — [Android 17 features](https://developer.android.com/about/versions/17/features); [Android Authority](https://www.androidauthority.com/android-17-live-updates-metric-style-template-3669117/)
- **Samsung**: One UI 8 connects the Now Bar to Android 16 Live Updates for third-party apps, showing them on the AOD, lock screen and status bar — [SamMobile](https://www.sammobile.com/news/now-bar-one-ui-9-support-three-more-types-third-party-apps/); [Android Authority, 3 Jul 2025](https://www.androidauthority.com/one-ui-8-live-updates-support-3573794/)
  - One UI 8 beta 3 required a developer option, "Live notifications for all apps", to see them.
  - One UI 9 (Android 17) adds the MetricStyle categories.
- **Xiaomi**: HyperOS 3.1's "Super Island" supports the Android 16 Live Updates API for third-party apps without Xiaomi-specific code (secondary reporting) — [Gizmochina](https://www.gizmochina.com/2026/01/30/xiaomi-hyperos-3-1-update-new-features-smarter-ui-eligible-device-list/); [Nokiapoweruser](https://nokiapoweruser.com/xiaomi-hyperos-3-1-is-here-whats-new-who-gets-it-who-doesnt/)
- **Updating from push via OneSignal** — [OneSignal: Android Live Updates](https://documentation.onesignal.com/docs/en/android-live-notifications):
  - A native `INotificationServiceExtension` class (Kotlin/Java) parses a `live_notification` object in the push `data`: `key`, `event` (start | update | end), `event_attributes` and `event_updates`.
  - It re-notifies with a constant Android notification ID and ends with `cancel(id)`. Use the same collapse ID across events and a short `ttl` on updates.
  - Requires OneSignal SDK 5.1.14+ and compileSdk 36.
  - On older OS versions the notification still "updates in place without promotion".
  - The docs don't address React Native, so native code is required.
- Version conflict: OneSignal says promotion needs "Android 16 QPR1 (API 36.1)", but Google's docs say API 36.1 is Android 16 **QPR2** — [OneSignal](https://documentation.onesignal.com/docs/en/android-live-notifications) vs [Android 16 features](https://developer.android.com/about/versions/16/features)

#### 1.3 Widgets → app widgets (RemoteViews / Jetpack Glance)
- **Jetpack Glance** 1.2.0 went stable on 26 Aug 2026 (`glance`, `glance-appwidget`, `glance-material3`). `1.3.0-alpha02` shipped 1 Jul 2026 — [Glance releases](https://developer.android.com/jetpack/androidx/releases/glance)
  - minSdk rose to API 23 in 1.2.0-beta01.
  - Version 1.1.0 (Jun 2024) added generated previews (`providePreview()`, `GlanceAppWidgetManager.setWidgetPreview()`), a unit-test library (`runGlanceAppWidgetUnitTest`, `testTag`) and Material 3 support.
  - Glance is Compose-based: the module needs `buildFeatures { compose = true }`.
- **Update frequency**: `updatePeriodMillis` values under 30 minutes (1,800,000 ms) aren't honoured — [AppWidgetProviderInfo](https://developer.android.com/reference/android/appwidget/AppWidgetProviderInfo); [Create an advanced widget](https://developer.android.com/develop/ui/views/appwidgets/advanced)
  - Google recommends updating no more than once an hour.
  - Alternatively set it to 0 and schedule updates with WorkManager.
- WorkManager periodic work has a 15-minute minimum interval — [WorkManager: define work](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work)
- **Lock-screen widgets** exist on the Pixel Tablet, and Google said AOSP tablets and phones would get them "starting with the release after Android 16 (QPR1)" — [Widgets on lock screen FAQ, Mar 2025](https://android-developers.googleblog.com/2025/03/widgets-on-lock-screen-faq.html)
  - All widgets are eligible by default. Opt out with the `not_keyguard` widget category in an `xml-36` resource folder.
  - An activity launched from the lock screen needs authentication or `android:showWhenLocked`.
- Android 17 (targeting 37) caps the memory used by a widget's `RemoteViews` bitmaps and icons at 1.5 × screen width × screen height × 4 bytes. Going over throws `IllegalArgumentException` — [Android 17 behaviour changes](https://developer.android.com/about/versions/17/behavior-changes-17)
- Apps with active widgets are exempt from the Restricted standby bucket — [App Standby Buckets](https://developer.android.com/topic/performance/appstandby)

#### 1.4 iOS Controls → Quick Settings tiles
- `TileService` arrived in Android 7.0 (API 24, which is exactly this app's minSdk) — [Quick Settings tiles](https://developer.android.com/develop/ui/views/quicksettings-tiles)
  - Declare the service with `BIND_QUICK_SETTINGS_TILE` and the `android.service.quicksettings.action.QS_TILE` intent filter.
  - Active mode uses `META_DATA_ACTIVE_TILE` plus `TileService.requestListeningState()`.
  - `StatusBarManager.requestAddTileService()` (API 33+) prompts the user to add the tile.
  - Guidance: at most 2 tiles; don't use a tile just to launch the app or to show display-only information.

#### 1.5 Notifications (channels, permission, push, background limits, in-app messages)
- **`POST_NOTIFICATIONS`** is a runtime permission from Android 13 (API 33) — [Notification permission](https://developer.android.com/develop/ui/views/notifications/notification-permission)
  - Apps targeting API 32 or lower get the system prompt when they create their first channel. One "Don't allow" is final until reinstall.
  - The permission is pre-granted on OS upgrade for apps that already have channels.
  - Ask in context, e.g. when "the user submits an order". Check `areNotificationsEnabled()`.
  - Even when notifications are denied, foreground-service notices still appear in Task Manager.
- **FCM priority** — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority):
  - Normal-priority messages are delayed while the device is in Doze.
  - High priority can wake the device, but "if FCM detects a pattern in which messages don't result in user-facing notifications, your messages may be deprioritized". FCM judges this over 7 days of behaviour.
  - `onMessageReceived` gets "several seconds".
- **Full-screen intents**: for apps targeting Android 14+, only calling or alarm apps are auto-granted `USE_FULL_SCREEN_INTENT` — [Play FGS & FSI requirements](https://support.google.com/googleplay/android-developer/answer/13392821); [Android 14 behaviour changes](https://developer.android.com/about/versions/14/behavior-changes-14)
  - The Play Console declaration opened 31 May 2024; default-grant enforcement started 22 Jan 2025.
  - Check with `NotificationManager.canUseFullScreenIntent()`.
- **Foreground service types** (each needs a `foregroundServiceType` plus a permission) — [FGS types](https://developer.android.com/develop/background-work/services/fgs/service-types):
  - `dataSync` (`FOREGROUND_SERVICE_DATA_SYNC`): limited to 6 h in every 24 h; can't start from `BOOT_COMPLETED` on 15+; Google links to "alternatives to dataSync".
  - `shortService`: about 3 minutes.
  - `location` (`FOREGROUND_SERVICE_LOCATION`): needs a granted COARSE or FINE location permission, and can't start from the background without `ACCESS_BACKGROUND_LOCATION`.
  - `connectedDevice`: needs e.g. a granted `BLUETOOTH_CONNECT`.
  - `specialUse`: needs a `PROPERTY_SPECIAL_USE_FGS_SUBTYPE` property and is reviewed in Play Console.
  - `mediaProcessing`: limited to 6 h.
- **Android 15** (targeting 35) — [Android 15 behaviour changes](https://developer.android.com/about/versions/15/behavior-changes-15):
  - After the dataSync / mediaProcessing 6-hour timeout the system calls `Service.onTimeout(int,int)`.
  - `BOOT_COMPLETED` can't start dataSync, camera or mediaPlayback foreground services.
  - `PendingIntent` background-activity launches are blocked by default.
  - TLS 1.0/1.1 are disallowed.
- **Exact alarms** — [Schedule alarms](https://developer.android.com/develop/background-work/services/alarms/schedule):
  - `SCHEDULE_EXACT_ALARM` isn't pre-granted on fresh installs on Android 14+.
  - `USE_EXACT_ALARM` (13+) is auto-granted but restricted by Play policy.
  - Use `canScheduleExactAlarms()` and `ACTION_REQUEST_SCHEDULE_EXACT_ALARM`.
  - Inexact options: `setWindow` (at least 10 minutes on 12+) and `setAndAllowWhileIdle`.
  - `setExact()` with an `OnAlarmListener` needs no permission.
- Android 17 adds a `setExactAndAllowWhileIdle()` variant that takes an `OnAlarmListener`, and `JobScheduler.getPendingJobReasonStats()` — [Android 17 features](https://developer.android.com/about/versions/17/features)
- **Doze** suspends network access, ignores wakelocks, and defers alarms (including `setExact`) and jobs to maintenance windows. `…AllowWhileIdle` alarms fire at most once every 9 minutes per app — [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby)
- **Standby buckets** are Active, Working set, Frequent, Rare and Restricted — [App Standby Buckets](https://developer.android.com/topic/performance/appstandby)
  - Restricted: jobs run once a day in a 10-minute batch, with one alarm per day, and the limits apply even while charging.
  - From Android 13 an app is moved to Restricted after 8 days of inactivity (45 days on Android 12).
  - Exempt apps include those with active widgets and those holding `USE_EXACT_ALARM` or `ACCESS_BACKGROUND_LOCATION`.
  - From Android 16, jobs started from the active bucket get a "generous runtime quota".
- **In-app messaging**:
  - OneSignal in-app messages are rendered by the native SDK (HTML/WebView) and pulled at session start. A new session begins after 30 s or more in the background. Triggers: app open, session duration, time since the last message, custom `addTrigger`. Click actions: deep link, tag, push prompt. No push permission is needed — [OneSignal IAM](https://documentation.onesignal.com/docs/en/in-app-messages-setup)
  - Firebase In-App Messaging is active, with no deprecation notice. It offers cards, banners, modals and images, triggered by Analytics events — [Firebase IAM](https://firebase.google.com/docs/in-app-messaging)

#### 1.6 App Clips → nothing on Play since Play Instant ended; use App Links and the web
- Google's notice: "Starting December 2025, Instant Apps cannot be published through Google Play, and all Google Play services Instant APIs will no longer work. Users will no longer be served Instant Apps by Play using any mechanism." Google points developers to deep links into the regular app instead — [Google Play Instant](https://developer.android.com/topic/google-play-instant)
- **App Links** — [Verify App Links](https://developer.android.com/training/app-links/verify-android-applinks):
  - Add `android:autoVerify="true"` to VIEW + BROWSABLE + DEFAULT https intent filters and publish `https://<host>/.well-known/assetlinks.json`.
  - From Android 12, links to unverified domains open in the browser.
  - Test with `adb shell pm verify-app-links --re-verify <pkg>` and `pm get-app-links`.
  - Check state at runtime with `DomainVerificationManager`; users can approve links under "Open by default" (`Settings.ACTION_APP_OPEN_BY_DEFAULT_SETTINGS`).
  - On Android 15+, changes to assetlinks.json can take up to seven days to take effect because verification is re-run periodically.
- **Dynamic App Links** (Android 15+) add a `dynamic_app_link_components` rule array to assetlinks.json, with path, query and fragment matchers and `exclude`. The rules can only narrow the manifest's scope, and older Android ignores them — [Android Developers Blog, Oct 2025](https://android-developers.googleblog.com/2025/10/dynamic-app-links-elevating-your.html); [Configure assetlinks](https://developer.android.com/training/app-links/configure-assetlinks)
- **UPI Intent** (`upi://pay?pa=…&pn=…&am=…&cu=INR&tr=…`) works from a mobile web page: the Android browser lists the installed UPI apps. Desktop web falls back to a QR code — [Razorpay: UPI Intent](https://razorpay.com/docs/payments/payment-methods/upi/upi-intent/); [Juspay: UPI Intent](https://juspay.io/in/docs/api-reference/docs/express-checkout/upi-intent)
- **WhatsApp click-to-chat**: `https://wa.me/<number>?text=<url-encoded>` opens a chat with the text pre-filled. This comes from a third-party guide; I didn't fetch WhatsApp's own FAQ — [businesschat.io guide](https://help.businesschat.io/en/articles/6517838-how-to-build-a-whatsapp-click-to-chat-url-wa-me)
- **Android developer verification**: user-facing enforcement starts 30 Sep 2026 in Brazil, Indonesia, Singapore and Thailand. Stores covered include Google Play, Galaxy Store, GetApps, and OPPO and vivo stores. It goes global on certified devices in 2027 — [Android Authority](https://www.androidauthority.com/android-sideloading-changes-timeline-3679204/); [Android developer verification](https://developer.android.com/developer-verification)

#### 1.7 Files: import, create, export, share, print, PDF
- **Storage Access Framework (SAF)** — [SAF guide](https://developer.android.com/training/data-storage/shared/documents-files):
  - `ACTION_OPEN_DOCUMENT` and `ACTION_CREATE_DOCUMENT` since API 19; `ACTION_OPEN_DOCUMENT_TREE` since API 21; `EXTRA_INITIAL_URI` sets the starting folder.
  - `takePersistableUriPermission()` survives reboots but not a file that has been moved or deleted.
  - On Android 11+, tree access can't target the storage root, the SD-card root or `Download/`, and `Android/data` and `Android/obb` are always excluded.
  - "This mechanism doesn't require any system permissions."
- **MediaStore** — [MediaStore guide](https://developer.android.com/training/data-storage/shared/media); [Android 16 behaviour changes](https://developer.android.com/about/versions/16/behavior-changes-16):
  - `MediaStore.Downloads` exists only on API 29+.
  - On Android 10+ an app needs no permission for media it owns; write with `IS_PENDING` and `RELATIVE_PATH`.
  - Declare `WRITE_EXTERNAL_STORAGE` with a `maxSdkVersion` for older devices.
  - `READ_MEDIA_IMAGES` / `READ_MEDIA_VIDEO` apply from Android 13.
  - On Android 16 with targetSdk 36, when the user grants limited access, the app's own photos are pre-selected.
- **FileProvider**: declare an `androidx.core.content.FileProvider` `<provider>` with `exported="false"` and `grantUriPermissions="true"`, plus a `FILE_PROVIDER_PATHS` XML (`files-path`, `cache-path`, `external-path`). It hands out `content://` URIs to share through `ACTION_SEND` — [FileProvider setup](https://developer.android.com/training/secure-file-sharing/setup-sharing)
- Android 17's docs warn that from Android 18, `ACTION_SEND`, `ACTION_SEND_MULTIPLE` and `ACTION_IMAGE_CAPTURE` will no longer grant URI permissions automatically. Set `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` explicitly — [Android 17 all-apps changes](https://developer.android.com/about/versions/17/behavior-changes-all)
- **Photo Picker** — [Photo Picker guide](https://developer.android.com/training/data-storage/shared/photopicker):
  - Built in on Android 13+. Android 4.4–12 get a backport through Google Play services once the manifest declares the `com.google.android.gms.metadata.ModuleDependencies` service with `photopicker_activity:0:required`.
  - Launch it with `PickVisualMedia` / `PickMultipleVisualMedia` (androidx.activity 1.7.0+); without the picker these fall back to `ACTION_OPEN_DOCUMENT`.
  - No permission is needed. Persistable grants are capped at 5,000 per app.
- Android 16 adds an embeddable photo picker (`android.widget.photopicker`); Jetpack support is described as "forthcoming" — [Android 16 features](https://developer.android.com/about/versions/16/features)
- **Printing HTML** — [Printing HTML documents](https://developer.android.com/training/printing/html-docs):
  - Build a `WebView`, wait for `onPageFinished`, then pass `WebView.createPrintDocumentAdapter(jobName)` (API 21 form) to `PrintManager.print()`.
  - Keep a reference to the WebView until the print job is created, or printing may fail.
  - The output can go to the system "Save as PDF" printer. No headers, footers or page numbers are supported.
- **expo-print** — [expo-print](https://docs.expo.dev/versions/latest/sdk/print/):
  - On Android it uses the WebView print adapter.
  - `printToFileAsync()` writes a PDF to the cache: 612×792 pt by default, with `width`/`height` options, optional `base64`, and CSS `@page` for margins.
  - `printAsync()` resolves as soon as the print dialog appears.
  - It runs in bare RN once Expo modules are installed.
- **androidx.pdf** (a viewer, plus `EditablePdfViewerFragment` for annotations and form filling) reached 1.0.0-beta01 on 26 Aug 2026 according to search results. An earlier write-up said `PdfViewerFragment` runs only on SDK 35+ — [androidx.pdf releases](https://developer.android.com/jetpack/androidx/releases/pdf) **[partly unverified]**
- **Bluetooth permissions** — [Bluetooth permissions](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions):
  - Android 12+ uses runtime permissions: `BLUETOOTH_SCAN` (add `usesPermissionFlags="neverForLocation"` to avoid needing location), `BLUETOOTH_CONNECT` and `BLUETOOTH_ADVERTISE`.
  - Keep the legacy `BLUETOOTH` / `BLUETOOTH_ADMIN` with `maxSdkVersion="30"`.
  - Android 11 and lower need `ACCESS_FINE_LOCATION` to scan.
  - `CompanionDeviceManager` (API 26+) pairs devices through a system UI without a location permission.
- **Android 17 changes for printers** (targeting 37) — [Android 17 behaviour changes](https://developer.android.com/about/versions/17/behavior-changes-17); [Android 17 blog](https://android-developers.googleblog.com/2026/06/Android-17.html):
  - `BluetoothSocket` RFCOMM `InputStream.read()` now returns -1 when the connection drops.
  - Finding or connecting to devices on the local network needs the new runtime permission `ACCESS_LOCAL_NETWORK` (NEARBY_DEVICES group), unless the app uses a system device picker.
- Android 16 first offered the local-network restriction as an opt-in compat flag (`RESTRICT_LOCAL_NETWORK`, gated on `NEARBY_WIFI_DEVICES`) — [Android 16 behaviour changes](https://developer.android.com/about/versions/16/behavior-changes-16)
- **DownloadManager** runs HTTP downloads in the background and retries after failures, connectivity changes and reboots. It offers `VISIBILITY_VISIBLE_NOTIFY_COMPLETED`, `setDestinationInExternalPublicDir` / `setDestinationInExternalFilesDir` and the `ACTION_DOWNLOAD_COMPLETE` broadcast — [DownloadManager](https://developer.android.com/reference/android/app/DownloadManager)

#### 1.8 Images: the PHPicker and VisionKit twins, camera, OCR, QR codes, uploads
- **Camera intent**: `ACTION_IMAGE_CAPTURE` needs no CAMERA permission unless the manifest declares CAMERA. If it is declared but not granted, the intent throws `SecurityException` — [Minimize permission requests](https://developer.android.com/privacy-and-security/minimize-permission-requests); [egorand.dev](https://www.egorand.dev/taking-photos-not-so-simply-how-i-got-bitten-by-action-image-capture/)
- **CameraX** — [CameraX releases](https://developer.android.com/jetpack/androidx/releases/camera):
  - Stable 1.6.2 (26 Aug 2026); minSdk 23 since 1.5.0-rc01.
  - 1.6.0 (25 Mar 2026) moved to CameraPipe and made `SessionConfig` stable.
  - 1.5.0 (Sep 2025) added low-light boost, UltraHDR, RAW and NV21 output for `ImageAnalysis`.
  - `camera-mlkit-vision` connects the camera to ML Kit. Latest alpha: 1.7.0-alpha03 (12 Aug 2026).
- **ML Kit Document Scanner** — [ML Kit Document Scanner](https://developers.google.com/ml-kit/vision/doc-scanner):
  - Provides the whole scanning UI: auto-capture, edge detection, rotation, cropping, filters, shadow and stain cleanup.
  - "No camera permission is needed from your app"; Google Play services delivers the models.
  - Options: page limit, gallery import, and `SCANNER_MODE_BASE` / `_BASE_WITH_FILTER` / `_FULL`.
  - Android only.
- **ML Kit Text Recognition v2** reads Latin, Chinese, **Devanagari**, Japanese and Korean. It returns blocks, lines, elements and symbols, each with a bounding box, confidence and language — [Text Recognition v2](https://developers.google.com/ml-kit/vision/text-recognition/v2)
- **Google code scanner** (`GmsBarcodeScanning`) — [Google code scanner](https://developers.google.com/ml-kit/vision/barcode-scanning/code-scanner):
  - No camera permission, API 23+.
  - The UI runs entirely inside Google Play services; only the result reaches the app.
  - It reads the same formats as the ML Kit barcode API, QR included. For a custom UI, use the ML Kit barcode API with CameraX.
- **GST e-invoice QR** — [Masters India](https://www.mastersindia.co/blog/signed-qr-code-e-invoicing-system/); [NIC e-invoice API FAQ](https://einv-apisandbox.nic.in/FaqsonAPI.html); [ClearTax verifier app](https://cleartax.in/s/qr-code-verify-app-e-invoicing):
  - The Invoice Registration Portal (IRP) returns a signed QR as a JWT (header.payload.signature).
  - The payload carries supplier and recipient GSTIN, invoice number, document type, date, value, line count and IRN.
  - It can be verified offline with the IRP's public key; NIC publishes a verifier app.
- **Background upload**:
  - WorkManager expedited work (`setExpedited`, `OutOfQuotaPolicy`) runs as an expedited job on Android 12+. On older versions it may run as a foreground service, which requires `getForegroundInfo()`. Quotas depend on the standby bucket and don't apply while the app is in the foreground — [WorkManager: define work](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work)
  - User-initiated data transfer jobs (Android 14+): `RUN_USER_INITIATED_JOBS`, `JobInfo.Builder.setUserInitiated(true)` and a required `JobService.setNotification()`. They are "unaffected by App Standby Buckets quotas", must be scheduled while the app is visible, and "there is currently no Jetpack library that supports UIDT jobs" — [UIDT](https://developer.android.com/develop/background-work/background-tasks/uidt)

#### 1.9 MapKit → Google Maps SDK (or MapLibre / Mappls), plus location
- **Maps SDK for Android** 20.0.0 shipped 31 Jan 2026 and needs minSdk 21 — [Maps SDK release notes](https://developers.google.com/maps/documentation/android-sdk/release-notes)
  - v19 deprecated the LEGACY renderer.
  - v20 removed `org.apache.http.legacy`, so apps still on the legacy renderer crash unless they declare that library themselves.
- **Pricing** — [Maps pricing](https://developers.google.com/maps/billing-and-pricing/pricing):
  - Free events per month: 10,000 for Essentials SKUs, 5,000 for Pro, 1,000 for Enterprise.
  - The mobile "Maps SDK" (map loads on Android/iOS) is listed as unlimited.
  - Paid rates at the 100k–500k tier: Dynamic Maps $7 per 1,000 (my reading: this is the web / JavaScript map-load SKU; the page doesn't label it web vs mobile, but it lists the mobile "Maps SDK" separately as unlimited), Geocoding $5, Autocomplete $2.83.
  - India has a separate price list.
- The $200 monthly credit was replaced by per-SKU free caps on 1 Mar 2025. Accounts billed in India with mostly Indian usage reportedly get 70k / 35k / 7k free events and pay in INR. This is a third-party summary; confirm it on Google's India page — [maps.guru](https://maps.guru/blog/google-maps-api-pricing-explained-2026); [India pricing](https://developers.google.com/maps/billing-and-pricing/india-overview); [Maps Platform India](https://mapsplatform.google.com/india/); [The Register (2024 India price cuts)](https://www.theregister.com/2024/07/19/google_maps_india_price_cuts_ola_response/)
- **Location permissions** — [Location permissions](https://developer.android.com/develop/sensors-and-location/location/permissions); [Android 17 blog](https://android-developers.googleblog.com/2026/06/Android-17.html):
  - `ACCESS_COARSE_LOCATION` gives about 3 km² accuracy; `ACCESS_FINE_LOCATION` about 50 m. If the user grants only approximate location, the app gets only approximate location.
  - `ACCESS_BACKGROUND_LOCATION` exists since API 29.
  - A location foreground service needs `foregroundServiceType="location"`.
  - Android 17 adds a system **location button** that gives precise location for the current session only.
- **Geofencing** (`GeofencingClient`) — [Geofencing](https://developer.android.com/develop/sensors-and-location/location/geofencing):
  - Up to 100 geofences per app per device user.
  - Needs FINE and BACKGROUND location on Android 10+.
  - Recommended radius: 100–150 m.
  - Latency is typically under 2 minutes, 2–6 minutes under background limits.
  - Geofences must be re-registered after a reboot or data clear; the API depends on Play services.
- **Mappls (MapmyIndia)** publishes `mappls-map-react-native` 2.0.x on npm; the older MapmyIndia RN repositories are marked deprecated — [npm](https://www.npmjs.com/package/mappls-map-react-native); [deprecated repo notice](https://github.com/mappls-api/mapmyindia-restapi-react-native-beta)

#### 1.10 Platform plumbing
- **Credential Manager** (`androidx.credentials`) covers passwords, passkeys, Sign in with Google (`googleid`: `GetGoogleIdOption` / `GetSignInWithGoogleOption`) and digital credentials — [Credential Manager](https://developer.android.com/identity/sign-in/credential-manager)
  - Passkeys need Android 9 (API 28)+ via Play services, plus Digital Asset Links.
  - It replaces legacy Google Sign-In, One Tap and Smart Lock.
- **Biometrics** — [Biometric auth](https://developer.android.com/identity/sign-in/biometric-auth):
  - `androidx.biometric` `BiometricPrompt` accepts `BIOMETRIC_STRONG` (Class 3), `BIOMETRIC_WEAK` (Class 2) and `DEVICE_CREDENTIAL`.
  - `DEVICE_CREDENTIAL` alone and `BIOMETRIC_STRONG | DEVICE_CREDENTIAL` aren't supported on API 29 and lower; use `KeyguardManager.isDeviceSecure()` there.
  - Keystore keys can require user authentication (`setUserAuthenticationRequired`, `setUserAuthenticationParameters`).
- **Play Integrity** — [Play Integrity overview](https://developer.android.com/google/play/integrity/overview):
  - Standard and classic requests both need API 23+. Standard requests need a warm-up and then answer in a few hundred milliseconds.
  - Verdicts: `requestDetails`; `appIntegrity` (`PLAY_RECOGNIZED`); `accountDetails` (`LICENSED`); `deviceIntegrity` (`MEETS_BASIC_INTEGRITY` / `MEETS_DEVICE_INTEGRITY` / `MEETS_STRONG_INTEGRITY`). STRONG on Android 13+ requires hardware-backed security and a recent security patch.
  - Optional verdicts: app access risk, Play Protect, recent device activity, device recall (beta).
  - The default quota is 10,000 requests a day, and the API needs Google Play services.
- SafetyNet Attestation has been turned off; Google's mailing list gives 31 Jan 2025 as the date it stopped working — [SafetyNet discontinuation](https://groups.google.com/g/safetynet-api-clients/c/ac_AmiRCn0U)
- **SMS Retriever** needs "no extra app permissions". The SMS must be at most 140 bytes, contain the code and include an 11-character hash derived from the package name and signing certificate — [SMS Retriever overview](https://developers.google.com/identity/sms-retriever/overview); [message format](https://developers.google.com/identity/sms-retriever/verify)
- **Android 17 OTP protection** (two variants):
  - Apps targeting 37: "standard SMS OTP messages withheld for 3 hours; apps must migrate to SMS_RETRIEVER or SMS User Consent" — [Android 17 behaviour changes](https://developer.android.com/about/versions/17/behavior-changes-17)
  - All apps: WebOTP-format messages are delayed 3 hours for apps without the receive permission — [Android 17 all-apps changes](https://developer.android.com/about/versions/17/behavior-changes-all)
- **Edge-to-edge**:
  - Android 15 enforces edge-to-edge for apps targeting 35: bars are transparent, and `setStatusBarColor`, `setNavigationBarColor` and `setDecorFitsSystemWindows` are deprecated — [Android 15 behaviour changes](https://developer.android.com/about/versions/15/behavior-changes-15)
  - Android 16 removes the `windowOptOutEdgeToEdgeEnforcement` opt-out for apps targeting 36 — [Android 16 behaviour changes](https://developer.android.com/about/versions/16/behavior-changes-16)
- **Predictive back** is on by default when targeting 36: `onBackPressed()` isn't called and `KEYCODE_BACK` isn't dispatched. Opt out with `android:enableOnBackInvokedCallback="false"`. Android 16 also adds `PRIORITY_SYSTEM_NAVIGATION_OBSERVER` — [Android 16 behaviour changes](https://developer.android.com/about/versions/16/behavior-changes-16); [Android 16 features](https://developer.android.com/about/versions/16/features)
- **React Native 0.81** (12 Aug 2025) targets Android 16 by default and adds an `edgeToEdgeEnabled` Gradle property for older Android versions. It deprecates the built-in `SafeAreaView` in favour of `react-native-safe-area-context`, and predictive back is on by default when targeting 36 — [React Native 0.81](https://reactnative.dev/blog/2025/08/12/react-native-0.81)
- **Large screens (sw ≥ 600 dp)**:
  - Android 16, targeting 36: `screenOrientation`, `resizableActivity`, min/max aspect ratio and `setRequestedOrientation()` are ignored. A temporary opt-out exists: `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` — [Android 16 behaviour changes](https://developer.android.com/about/versions/16/behavior-changes-16)
  - Android 17, targeting 37: the opt-out is removed. Games are exempt based on their Play category — [Android 17 behaviour changes](https://developer.android.com/about/versions/17/behavior-changes-17); [Android 17 blog](https://android-developers.googleblog.com/2026/06/Android-17.html)
- **Other Android 17 changes that affect apps** — [Android 17 all-apps changes](https://developer.android.com/about/versions/17/behavior-changes-all); [targeting-17 changes](https://developer.android.com/about/versions/17/behavior-changes-17); [Android 17 features](https://developer.android.com/about/versions/17/features):
  - RAM-based app memory limits; a killed process is logged with `MemoryLimiter:AnonSwap`.
  - `static final` fields can't be changed through reflection or JNI.
  - Libraries loaded with `System.load()` must be read-only.
  - Certificate Transparency and Encrypted Client Hello are on by default.
  - Keystore is limited to 50,000 keys per app.
  - A system Contact Picker gives temporary access to chosen fields without `READ_CONTACTS`.
  - Handoff API and post-quantum APK signing.

### Inferences
**Twin map** (my assessment of each pairing and its fallback down to minSdk 24):

| iOS feature | Android twin in 2026 | How close | Floor and fallback to minSdk 24 |
|---|---|---|---|
| App Intents + Siri / Shortcuts app | App Shortcuts (static, dynamic, pinned); AppFunctions for agents; `onProvideAssistContent` for screen context | Shortcuts are a close equivalent. For voice or agent queries there is **no production twin**: Assistant is gone from phones, AppFunctions is alpha with Gemini in private preview, and the App Actions docs say nothing about Gemini | Shortcuts need API 25, so Android 7.0 devices get none (share negligible; StatCounter doesn't break it out). AppFunctions needs API 36, with no fallback outside the app |
| Live Activities (+ Dynamic Island) | Live Updates: `ProgressStyle` (API 36), `MetricStyle` (API 37), status chip; Samsung Now Bar (One UI 8+); Xiaomi Super Island (HyperOS 3.1) | Medium. Layouts are system templates only, the use-case rules are strict, and there is no system-side push update: app code must rebuild the notification for every push | On API 24–35, post an ordinary ongoing notification with a `NotificationCompat` progress bar, updated in place |
| App Clips | **None** since Play Instant closed. Substitute: link → web page (invoice + UPI Intent) → App Link into the installed app, or the Play listing | No twin | The web page works in any Android browser |
| Widgets (WidgetKit) | App widgets (RemoteViews) or Jetpack Glance (API 23+); lock-screen widgets on tablets and newer AOSP | Very close; interactive widgets are long established on Android | Glance's minSdk 23 covers API 24 |
| Controls (iOS 18) | Quick Settings tiles (`TileService` API 24; add-tile prompt API 33) | Close | Below 33 there is no add prompt; explain in the app how to add the tile |
| PHPicker | Photo Picker (built in on 33+; Play-services backport down to 19) | Very close | Needs the backport manifest entry; falls back to `ACTION_OPEN_DOCUMENT` |
| VisionKit document camera | ML Kit Document Scanner (Play services, no CAMERA permission) | Very close (Android only) | Needs Play services; otherwise camera intent plus manual crop |
| VisionKit Live Text / DataScanner | ML Kit Text Recognition v2 + Google code scanner or ML Kit barcode | Close | Code scanner needs API 23+ |
| MapKit | Maps SDK for Android (API key, billing account; mobile map loads free and unlimited), MapLibre, Mappls | Functionally close; different commercial model | Maps SDK minSdk is 21 |

**Petroleum-dealer OMS examples** (design proposals, not sourced facts):
- **App Shortcuts**:
  - static: "New order", "Today's summary", "Customers", "Scan invoice QR";
  - dynamic: the last 3 customers opened;
  - pinned: one per customer ledger (e.g. "Sharma Roadways ledger");
  - all routed through the existing React Navigation deep-link map.
- **AppFunctions** (defer): `getOutstandingBalance(customerQuery) → {customer, amountPaise, asOf}` and `draftOrder(customerQuery, product: HSD|MS, litres) → DraftOrder`, which opens the app for confirmation.
  - An agent should never place a binding order silently; money rules and approvals stay in the app.
  - This is exactly the "what is my outstanding" / "order 500 L diesel" pair, but only Gemini testers could reach it in September 2026.
- **AssistContent**: publish the URL of the order on screen (`https://<domain>/orders/<id>`) plus schema.org `Order` JSON-LD, so "ask about this screen" gets structured context.
- **Live Update** (dealer side): when the tanker for a supply order is dispatched, show `ProgressStyle` segments Indent → Invoiced → Dispatched → At outlet → Decanted, with chip text such as "ETA 25m" or "Unloading".
  - Run it only while the tanker is moving; end it at delivery.
  - An order that waits for days is "package tracking", which Google says is not a Live Update.
- **Widget**: a Daily Summary widget, e.g. "Today · ₹4.2 L sales · HSD 3,210 L · MS 1,050 L · Outstanding ₹12.8 L".
  - Tapping it opens Daily Summary.
  - A configuration activity picks the company/GSTIN and the shift window.
  - Refresh on app open, on a WorkManager schedule of about an hour, and on a push after invoices are posted.
- **Quick Settings tile**: a single tile, "New order" or "Scan QR", that opens the app.
- **Customer path without installing**:
  - Share `https://<domain>/i/<token>` over WhatsApp, via the share sheet or wa.me.
  - The page shows the invoice PDF and a "Pay by UPI" button (`upi://pay…`).
  - On phones with the app, the same URL opens the invoice screen through App Links.
- **Files**:
  - "Export TCS/TDS report": `ACTION_CREATE_DOCUMENT` (CSV/PDF) to a location the user picks.
  - "Save invoice": write to `MediaStore.Downloads` (API 29+).
  - "Share invoice": FileProvider + `ACTION_SEND`, with an explicit read grant to prepare for Android 18.
- **Images**:
  - Capture DU slips (DU assumed to mean dispensing unit) and totaliser readings with the ML Kit Document Scanner, then run OCR with Text Recognition v2 (Latin digits).
  - Scan the signed e-invoice QR with the code scanner and verify the JWT against the IRP key on the server.
- **Maps**:
  - Pins for customers and outlets.
  - Track the tanker from the driver's phone with a location foreground service started while the app is visible, so no background-location permission is needed.
  - Skip geofencing unless "arrived at outlet" becomes core, because geofencing forces background location.
- **Plumbing**:
  - App Links for invoice and order URLs.
  - Biometric re-lock when the app resumes.
  - Play Integrity checks when an OTP is requested or verified, to blunt scripted OTP abuse.
  - SMS Retriever to autofill the OTP.

**Flags specific to this app**:
- targetSdk 36 already meets the 31 Aug 2026 Play deadline.
- The portrait lock is already ignored on sw ≥ 600 dp; the opt-out property works until the app targets 37.
- Moving to target 37 brings four changes:
  - `ACCESS_LOCAL_NETWORK` for Wi-Fi/LAN printers;
  - RFCOMM `read()` returning -1 for Bluetooth printers;
  - widget bitmap memory caps;
  - the location-button policy from 27 Jan 2027 (section 3).

### Gaps
- No Google statement says whether Gemini honours App Actions / BIIs after Assistant was removed on 4 Sep 2026; the App Actions docs are silent.
- No primary source found for "Android widgets in Gemini", or for any developer hook into Circle to Search or Gemini Live beyond `onProvideAssistContent`.
- Not researched: how OnePlus/OPPO (ColorOS "Live Alerts") and vivo (OriginOS) handle Live Updates. Samsung stable One UI 8: unconfirmed whether any allowlist exists (the beta used a developer toggle).
- The API levels of `PdfDocument` (believed 19) and `DownloadManager` (believed 9) weren't confirmed from the fetched pages.
- Whether `PdfViewerFragment` still needs API 35 comes only from a secondary write-up.
- The Android 17 Contact Picker's intent/API name and any backport weren't fetched.
- Lock-screen widgets on **phones**: Google's blog promised AOSP phones "after Android 16 QPR1", but I found no confirmation that Pixel phones or One UI show third-party lock-screen widgets in 2026.

## 2. Which capabilities can be driven entirely from JS through a maintained New-Architecture-ready library, and which need a Kotlin component owned by the team (widget receiver, Glance widget, WorkManager worker, AppFunction, foreground service)?

### Takeaway
**Can be driven from JS today**, through maintained libraries marked New-Architecture-ready:
- Push and local notifications: OneSignal 5.5.14, RNFirebase 26.4.0, react-native-notify-kit 10.7.2. Notifee was archived in April 2026; notify-kit is its maintained fork.
- Sharing: react-native-share 12.3.1.
- Picking and saving documents: @react-native-documents/picker 12.0.2.
- HTML → PDF and printing: expo-print 57.
- Photo picking and camera: image-picker, expo-image-picker, VisionCamera 5.2.3.
- Document scanning: react-native-document-scanner-plugin 2.0.4.
- Maps: react-native-maps 1.29.11, MapLibre 11.4.0.
- Biometrics and keychain, passkeys (react-native-passkey 3.6.2), Play Integrity (@expo/app-integrity 57), SMS Retriever.
- Home-screen widgets can be authored in JSX (react-native-android-widget 0.22.1, or Voltra on top of Glance), but the widget still runs outside the RN view tree.

**Needs Kotlin owned by the team**:
- AppFunctions: no RN library exists.
- Rendering Live Updates from push: a OneSignal `NotificationServiceExtension` or an FCM service. Voltra is only starting to cover this.
- Quick Settings tiles.
- A WorkManager upload worker: the only popular RN upload library is unmaintained.
- ML Kit OCR and code-scanner wrappers: the existing RN ML Kit wrappers aren't New-Architecture-flagged.
- Classic-Bluetooth ESC/POS printing: only a tiny New-Architecture library exists.
- Any location foreground service, unless the team pays for Transistorsoft (the Android release build needs a $399 licence).

### Cited Findings
**Library status** from the reactnative.directory API, 29 Sep 2026. Source for every row: `https://reactnative.directory/api/libraries?search=<package>`. Columns: latest version (date) · dirNA / ghNA · weekly npm downloads.

| Area | Package | Version (date) | dirNA / ghNA | Downloads/wk | Notes |
|---|---|---|---|---|---|
| Push | [react-native-onesignal](https://reactnative.directory/api/libraries?search=react-native-onesignal) | 5.5.14 (2026-09-23) | true / true | 122k | Live Updates need a native extension ([OneSignal](https://documentation.onesignal.com/docs/en/android-live-notifications)) |
| Push | [@react-native-firebase/messaging](https://reactnative.directory/api/libraries?search=%40react-native-firebase%2Fmessaging) | 26.4.0 (2026-09-05) | true / true | 642k | |
| In-app messages | [@react-native-firebase/in-app-messaging](https://reactnative.directory/api/libraries?search=%40react-native-firebase%2Fin-app-messaging) | 26.4.0 (2026-09-05) | true / true | 23k | |
| Local notifications | [react-native-notify-kit](https://reactnative.directory/api/libraries?search=react-native-notify-kit) | 10.7.2 (2026-09-23) | true / true | 23k | Notifee fork; "TurboModules only"; RN ≥ 0.73; exact-alarm fallback; foreground-service types via config plugin ([GitHub](https://github.com/marcocrupi/react-native-notify-kit)) |
| Widgets | [react-native-android-widget](https://reactnative.directory/api/libraries?search=react-native-android-widget) | 0.22.1 (2026-08-17) | true / false | 28k | Docs: "Supports the React Native new architecture"; Expo config plugin ([docs](https://saleksovski.github.io/react-native-android-widget/)) |
| Widgets + Live Updates | [voltra](https://reactnative.directory/api/libraries?search=voltra) | 2.3.2 (2026-09-22) | true / – | 19k | iOS Live Activities + Android home-screen widgets via Glance; FCM updates; dev client or bare RN, not Expo Go ([GitHub](https://github.com/callstackincubator/voltra)). Android 17 Metric ongoing-notification layout merged 28 Sep 2026 ([PR #326](https://github.com/callstackincubator/voltra/pull/326)) |
| Widgets | [expo-widgets](https://reactnative.directory/api/libraries?search=expo-widgets) | 57.0.22 | true / – | 143k | **iOS only** ([Expo docs](https://docs.expo.dev/versions/latest/sdk/widgets/)) |
| Shortcuts | [expo-quick-actions](https://reactnative.directory/api/libraries?search=expo-quick-actions) | 6.0.2 (2026-05-27) | true / false | 85k | Expo module; needs expo-modules in bare RN |
| Shortcuts | [@rn-org/react-native-shortcuts](https://reactnative.directory/api/libraries?search=react-native-shortcuts) | 0.2.0 (2026-02-15) | – / true | 1k | Small user base |
| Shortcuts | [react-native-quick-actions](https://reactnative.directory/api/libraries?search=react-native-quick-actions) | 0.3.13 (2019) | unmaintained | 14k | Avoid |
| Files | [@react-native-documents/picker](https://reactnative.directory/api/libraries?search=%40react-native-documents%2Fpicker) | 12.0.2 (2026-07-28) | – / true | 218k | Successor to react-native-document-picker (MIT) ([GitHub](https://github.com/react-native-documents/document-picker)) |
| Share | [react-native-share](https://reactnative.directory/api/libraries?search=react-native-share) | 12.3.1 (2026-05-04) | New Arch: yes | 343k | |
| Share | [expo-sharing](https://reactnative.directory/api/libraries?search=expo-sharing) | 57.0.22 (2026-09-24) | true / false | 1.6M | |
| File I/O | [react-native-blob-util](https://reactnative.directory/api/libraries?search=react-native-blob-util) | 0.25.1 (2026-09-24) | – / true | 575k | |
| File I/O | [react-native-file-access](https://reactnative.directory/api/libraries?search=react-native-file-access) | 4.0.4 (2026-09-18) | – / true | 36k | |
| Print / PDF | [expo-print](https://reactnative.directory/api/libraries?search=expo-print) | 57.0.2 (2026-09-11) | true / false | 399k | WebView-based `printToFileAsync` ([docs](https://docs.expo.dev/versions/latest/sdk/print/)) |
| Print | [react-native-print](https://reactnative.directory/api/libraries?search=react-native-print) | 0.11.0 (2023-01-22) | **unmaintained** | 10k | Avoid |
| HTML → PDF | [react-native-html-to-pdf](https://reactnative.directory/api/libraries?search=react-native-html-to-pdf) | 1.3.0 (2025-09-04) | – / true | 21k | No release for a year ([npm](https://www.npmjs.com/package/react-native-html-to-pdf)) |
| PDF view | [react-native-pdf](https://reactnative.directory/api/libraries?search=react-native-pdf) | 7.0.5 (2026-08-13) | – / true | 265k | |
| Bluetooth / LAN printer | [react-native-earl-thermal-printer](https://reactnative.directory/api/libraries?search=earl-thermal) | 2.0.1 (2026-08-10) | true / true | 63 | TurboModules; "Android 12+ Bluetooth compliance"; BLE + ESC/POS QR ([GitHub](https://github.com/Swif7ify/react-native-earl-thermal-printer)) |
| Printer | [react-native-thermal-receipt-printer](https://reactnative.directory/api/libraries?search=react-native-thermal-printer) | 1.2.0-rc.2 (2023-12-06) | – / false | 756 | Stale |
| Printer | [react-native-esc-pos-printer](https://github.com/tr3v3r/react-native-esc-pos-printer) | n/a | README: compatible with the new architecture | n/a | **Epson TM printers only** (BLE/LAN/USB/Wi-Fi) |
| BLE | [react-native-ble-plx](https://reactnative.directory/api/libraries?search=react-native-ble-plx) | 3.5.1 (2026-02-18) | true / false | 179k | BLE only (no classic SPP) |
| Classic BT | [react-native-bluetooth-classic](https://reactnative.directory/api/libraries?search=react-native-bluetooth-classic) | 1.73.0-rc.17 (2025-11-19) | – / false | 10k | RC only; not New-Arch-flagged |
| Images | [react-native-image-picker](https://reactnative.directory/api/libraries?search=react-native-image-picker) | 8.2.1 (2025-05-04) | – / true | 350k | |
| Images | [expo-image-picker](https://reactnative.directory/api/libraries?search=react-native-image-picker) | 57.0.20 (2026-09-24) | true / false | 3.1M | |
| Images | [react-native-image-crop-picker](https://reactnative.directory/api/libraries?search=react-native-image-crop-picker) | 0.51.1 (2025-10-21) | true / true | 147k | |
| Camera | [react-native-vision-camera](https://reactnative.directory/api/libraries?search=react-native-vision-camera) | 5.2.3 (2026-08-20) | "new-arch-only" | 436k | v5 is a Nitro Modules rewrite ([Margelo](https://margelo.com/blog/whats-new-in-visioncamera-v5)) |
| Camera | [react-native-camera-kit](https://reactnative.directory/api/libraries?search=react-native-camera-kit) | 18.0.1 (2026-08-03) | true / true | 45k | |
| Scanner | [react-native-document-scanner-plugin](https://reactnative.directory/api/libraries?search=react-native-document-scanner-plugin) | 2.0.4 (2026-01-02) | – / true | 59k | Whether Android uses ML Kit is **[unverified]** |
| OCR | [@react-native-ml-kit/text-recognition](https://reactnative.directory/api/libraries?search=%40react-native-ml-kit%2Ftext-recognition) | 2.0.0 (2025-09-01) | – / **false** | 27k | |
| QR | [@react-native-ml-kit/barcode-scanning](https://reactnative.directory/api/libraries?search=%40react-native-ml-kit%2Fbarcode-scanning) | 2.0.0 (2025-09-01) | – / **false** | 3k | |
| Compress | [react-native-compressor](https://reactnative.directory/api/libraries?search=react-native-compressor) | 2.0.3 (2026-07-25) | true / false | 143k | |
| Resize | [@bam.tech/react-native-image-resizer](https://reactnative.directory/api/libraries?search=image-resizer) | 3.0.11 (2024-11-25) | – / true | 50k | Last release Nov 2024 |
| Upload | [react-native-background-upload](https://reactnative.directory/api/libraries?search=react-native-background-upload) | 6.6.0 (2022-10-07) | **unmaintained**, false / false | 4k | Avoid |
| Upload | [rn-background-upload](https://reactnative.directory/api/libraries?search=react-native-background-upload) | 0.1.0 (2026-02-11) | true / true | 45 | Too new and small to depend on |
| Maps | [react-native-maps](https://reactnative.directory/api/libraries?search=react-native-maps) | 1.29.11 (2026-09-27) | true / true | 870k | README: 1.26.1+ supports Fabric on RN ≥ 0.81.1 ([GitHub](https://github.com/react-native-maps/react-native-maps)) |
| Maps | [@maplibre/maplibre-react-native](https://reactnative.directory/api/libraries?search=%40maplibre%2Fmaplibre-react-native) | 11.4.0 (2026-09-19) | true / true | 108k | |
| Maps | [@rnmapbox/maps](https://reactnative.directory/api/libraries?search=react-native-maps) | 10.3.5 (2026-07-22) | – / true | 140k | |
| Maps (India) | [mappls-map-react-native](https://www.npmjs.com/package/mappls-map-react-native) | 2.0.x | not in directory | n/a | New-Architecture status unknown |
| Location | [expo-location](https://reactnative.directory/api/libraries?search=expo-location) | 57.0.20 (2026-09-24) | true / false | 1.7M | |
| Location | [@react-native-community/geolocation](https://reactnative.directory/api/libraries?search=%40react-native-community%2Fgeolocation) | 3.4.0 (2024-09-01) | flagged unmaintained | 68k | |
| Location | [react-native-geolocation-service](https://reactnative.directory/api/libraries?search=react-native-geolocation-service) | 5.3.1 (2022) | unmaintained | 90k | |
| Location FGS | [react-native-background-geolocation](https://reactnative.directory/api/libraries?search=react-native-background-geolocation) | 5.7.0 (2026-09-27) | true / true | 37k | Android release builds need a licence ($399 iOS + Android) ([shop](https://shop.transistorsoft.com/products/react-native-background-geolocation-premium-license); [GitHub](https://github.com/transistorsoft/react-native-background-geolocation)) |
| Passkeys | [react-native-passkey](https://reactnative.directory/api/libraries?search=react-native-passkey) | 3.6.2 (2026-09-08) | true / false | 96k | |
| Google sign-in | [@react-native-google-signin/google-signin](https://reactnative.directory/api/libraries?search=%40react-native-google-signin%2Fgoogle-signin) | 16.1.5 (2026-09-03) | true / true | 499k | Free "Original" build uses the deprecated legacy SDK; the paid "Universal" build uses Credential Manager ([docs](https://react-native-google-signin.github.io/docs/install)) |
| Biometrics | [@sbaiahmed1/react-native-biometrics](https://reactnative.directory/api/libraries?search=react-native-biometrics) | 0.16.1 (2026-09-08) | true / true | 18k | |
| Keychain | [react-native-keychain](https://reactnative.directory/api/libraries?search=react-native-keychain) | 10.0.0 (2025-03-23) | true / true | 385k | |
| Integrity | [@expo/app-integrity](https://reactnative.directory/api/libraries?search=app-integrity) | 57.0.2 (2026-09-11) | true / false | 36k | Expo module |
| OTP | [@ebrimasamba/react-native-sms-retriever](https://reactnative.directory/api/libraries?search=react-native-sms-retriever) | 2.1.1 (2026-06-05) | true / true | 1.8k | |
| OTP | [react-native-otp-verify](https://reactnative.directory/api/libraries?search=react-native-otp-verify) | 1.2.0 (2026-04-03) | false / false | 20k | |
| OTP | [@eabdullazyanov/react-native-sms-user-consent](https://reactnative.directory/api/libraries?search=sms-user-consent) | 1.3.0 (2025-11-17) | – / false | 7k | |
| Edge-to-edge | [react-native-edge-to-edge](https://reactnative.directory/api/libraries?search=react-native-edge-to-edge) | 1.8.2 (2026-09-14) | – / true | 555k | |
| Shared KV store | [react-native-mmkv](https://reactnative.directory/api/libraries?search=react-native-mmkv) | 4.3.2 (2026-06-22) | true / false | 1.1M | |
| Background tasks | [react-native-background-fetch](https://reactnative.directory/api/libraries?search=react-native-background-fetch) | 4.4.2 (2026-04-15) | true / true | 63k | Periodic tasks, not uploads |

Other facts that decide JS versus Kotlin:
- **Notifee** stopped receiving updates in Dec 2024 and was archived in April 2026. Invertase's README points to react-native-notify-kit as the drop-in, New-Architecture replacement. This claim comes from the fork author's post — [dev.to (fork author)](https://dev.to/marco_crupi/notifee-is-archived-heres-a-maintained-new-architecture-drop-in-replacement-3ib5); [notify-kit README](https://github.com/marcocrupi/react-native-notify-kit)
- **AppFunctions** are Kotlin-only: `@AppFunction`, a KSP-generated schema and an `AppFunctionService` subclass. Searching for an RN or Expo AppFunctions library found nothing — [AppFunctions overview](https://developer.android.com/ai/appfunctions)
- **Glance** is built on Compose; its Gradle setup enables `buildFeatures { compose = true }` — [Glance releases](https://developer.android.com/jetpack/androidx/releases/glance)
- **UIDT jobs** have no Jetpack/WorkManager support. WorkManager expedited work on API < 31 falls back to a foreground service and needs `getForegroundInfo()` — [UIDT](https://developer.android.com/develop/background-work/background-tasks/uidt); [WorkManager](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work)
- **expo-print** works in bare React Native once Expo modules are installed — [expo-print](https://docs.expo.dev/versions/latest/sdk/print/)
- **react-native-html-to-pdf** is described as slow to maintain, needing base64 images, with inconsistent iOS/Android margins (third-party guide) — [transformy.io](https://transformy.io/guides/html-to-pdf-react/)

### Inferences
**The shared prerequisite for all "outside the RN runtime" components**: widgets, AppFunctions, Live-Update rendering from push, Quick Settings tiles and WorkManager workers all run without JS. They need a small Kotlin `SessionStore`/`SummaryStore`, readable by both JS and native code, holding the auth token and the latest Daily Summary numbers.
- react-native-mmkv 4.x or a tiny Turbo Module can do this.
- Build it once, test-first. It is 1–2 days and every native surface below depends on it.

**Split and effort.** These are my estimates, in working days, for one JS-first developer with some Kotlin, working test-first: Jest on the JS side, JUnit/Robolectric on the Kotlin side, plus the Glance test library where relevant. Add 20–30 % for device checks on Samsung, Xiaomi and Pixel.

| Capability | Recommended path | JS-only? | Kotlin the team owns | Days |
|---|---|---|---|---|
| Static + dynamic shortcuts | `shortcuts.xml` + expo-quick-actions (or a 50-line module); route through existing deep links | Almost | none, or tiny | 1–2 |
| Pinned per-customer shortcut | `ShortcutManagerCompat.requestPinShortcut` through a tiny Turbo Module | No | tiny | +0.5–1 |
| Assist content | Override in `MainActivity`, plus a JS setter module | No | small | 1 |
| AppFunctions | `AppFunctionService` calling the DZZLO API with the stored session; API 36 only | No | yes | 2–3 spike; 5–8 full. Defer until Gemini access opens |
| Live Update (tanker ETA) | OneSignal `NotificationServiceExtension` building `ProgressStyle` (API 36) with a `NotificationCompat` fallback; server-side start/update/end payloads | No (re-check Voltra's release notes) | yes | 4–6 including server |
| Home-screen widget | JSX via react-native-android-widget or Voltra, versus Glance in Kotlin | JSX path mostly | Glance path: yes | 3–5 (JSX) / 5–8 (Glance) |
| Quick Settings tile | `TileService` | No | yes | 1–2 |
| Notification hardening (channels, asking for permission in context, action buttons, grouping, OEM guidance) | OneSignal + notify-kit | Yes | none | 2–4 |
| In-app messages | OneSignal IAM, or in-house JS banners from the API | Yes | none | 0.5–2 |
| App Links | Intent filters + assetlinks.json + RN Linking; verify with adb | Configuration only | manifest only | 1–2 in the app (+ web invoice page, separate) |
| Export / save / share | @react-native-documents/picker, react-native-share, a MediaStore-Downloads helper | Mostly | tiny MediaStore module if no library covers it | 2–3 |
| Replace react-native-html-to-pdf | expo-print `printToFileAsync` (same WebView approach, maintained) | Yes | none | 1–2 |
| Fully native PDF | `PdfDocument` + Canvas layout | No | yes | 5–10 (rewrites the layout) |
| Bluetooth ESC/POS printer | Own RFCOMM (SPP) Turbo Module for classic printers (most cheap 58/80 mm printers, **[unverified]**), or earl-thermal-printer for BLE | Partly | likely | 5–8 including a printer test matrix |
| Photo Picker + camera | expo-image-picker or react-native-image-picker (whether each uses the system Photo Picker is **[unverified]**) | Yes | none | 1 |
| Document scanner | react-native-document-scanner-plugin, or a 1-day ML Kit Turbo Module | Yes / small | small | 1–2 |
| OCR (DU slips, meter readings) | ML Kit Text Recognition v2 Turbo Module (the existing RN wrapper isn't New-Arch-flagged) | No | yes | 2–4 |
| QR (e-invoice) | Google code scanner Turbo Module (no permission), or VisionCamera's code scanner | Partly | small | 1–2 (+1 server-side JWT verification) |
| Background upload | WorkManager `CoroutineWorker` + multipart; UIDT on 34+ for large, user-started uploads | No | yes | 3–5 |
| Maps (pins, routes) | react-native-maps + Maps SDK key restricted to the app's signature | Yes | none | 2–4 |
| Tanker live tracking | Own location foreground service + Fused Location, or Transistorsoft ($399) | No, or paid | yes | 6–10 own / 2–3 with the paid library |
| Biometric lock | react-native-keychain access control, or react-native-biometrics | Yes | none | 1–2 |
| Passkeys | react-native-passkey + server-side WebAuthn + assetlinks | Yes (client) | none | 5–10 including server |
| Play Integrity | @expo/app-integrity + server-side verdict decoding | Yes | none | 2–4 including server |
| SMS Retriever autofill | sms-retriever library + adding the 11-character hash to the OTP template | Yes | none | 1–2 (+ SMS template re-approval, see section 4 gaps) |

**Priority for DZZLO**, by value to dealers and customers relative to cost:
1. Notification hardening plus the OEM battery guide.
2. SMS Retriever autofill.
3. Export/share/save via SAF, MediaStore and FileProvider.
4. expo-print in place of react-native-html-to-pdf.
5. The Daily Summary widget.
6. App Links plus the web invoice page with UPI.
7. Document scanner and OCR for DU slips.
8. QR verification for e-invoices.
9. Maps and pins.
10. Live Updates for tanker ETA, once dispatch data exists.
11. AppFunctions, only after Gemini access opens.

Glance adds Compose to an RN app that has none today. That brings Compose runtime and APK-size costs and needs the Kotlin 2.x Compose compiler plugin. The JSX widget libraries avoid that, at the cost of a young dependency (react-native-android-widget is v0.x).

### Gaps
- Not fetched: whether @react-native-documents/picker supports saving/export (`ACTION_CREATE_DOCUMENT`) in the free MIT build, and which of its features are sponsor-only. Its docs pages didn't render the API details.
- Not confirmed: how react-native-share targets WhatsApp and WhatsApp Business (`Social.Whatsapp`, package `com.whatsapp.w4b`).
- Not checked: whether react-native-image-picker 8.x on Android launches `PickVisualMedia` (the Photo Picker) or `ACTION_GET_CONTENT`.
- Not checked: the Android backends of react-native-document-scanner-plugin and of VisionCamera v5's code scanner.
- Not found: which Voltra version first shipped Android `ProgressStyle` ongoing notifications.
- Not found: whether react-native-notify-kit supports `ProgressStyle` or `setRequestPromotedOngoing`. Its README excerpt didn't mention either.
- Not found: an RN library for Quick Settings tiles or for the Android 17 Contact Picker.
- Not checked: whether mappls-map-react-native supports the New Architecture (it isn't in reactnative.directory).

## 3. What Google Play policies (2026) constrain each capability (permission declaration forms, foreground-service types, background location, photo/video permissions, full-screen intent, exact alarms, target SDK, 16 KB)?

### Takeaway
DZZLO already targets API 36, so it meets the 31 Aug 2026 target-SDK rule. That rule has an extension to 1 Nov 2026.

The 16 KB page-size rule now enforces on **1 Feb 2027**, per Google's page; earlier messaging said Nov 2025 / May 2026.

**Features that bring Play Console forms**:
- a background-location or location-FGS feature;
- any foreground service, with a per-type declaration and a video;
- `READ_MEDIA_*` if the app skips the Photo Picker;
- `USE_FULL_SCREEN_INTENT` or `USE_EXACT_ALARM`, neither of which DZZLO qualifies for;
- Data safety entries for every new data type, including data collected by SDKs.

**Features that trigger no special form**:
- Photo Picker, SAF, ML Kit Document Scanner, Google code scanner, `ACTION_IMAGE_CAPTURE` without CAMERA, SMS Retriever, Live Updates (a normal permission), widgets, shortcuts, Quick Settings tiles, App Links.
- The least-policy route is to prefer these system-delegated UIs.

**New policy date**: from **27 Jan 2027**, apps targeting API 37 whose precise-location use is one-time must use Android 17's location button.

### Cited Findings
- **Target API level** — [Target API requirements](https://developer.android.com/google/play/requirements/target-sdk):
  - From 31 Aug 2026, new apps and updates must target Android 16 (API 36). Wear OS and Automotive need 35; TV and XR need 34.
  - Existing apps must target API 35+ to stay available to new users on newer Android versions.
  - Developers can request an extension to 1 Nov 2026.
- **16 KB page size** — [Page sizes guide](https://developer.android.com/guide/practices/page-sizes):
  - "Starting February 1, 2027, if your app updates don't support 16 KB memory page sizes, you won't be able to release these updates."
  - It applies to apps targeting API 35+ on 64-bit devices.
  - AGP 8.5.1+ and NDK r28+ align libraries by default. Check with `zipalign -c -P 16 -v 4`, `check_elf_alignment.sh`, or `llvm-objdump -p … | grep LOAD` (look for `align 2**14`).
  - Prebuilt `.so` files must be rebuilt. Apps with only Java/Kotlin code are unaffected.
- Earlier messaging set 1 Nov 2025 as the date. A third-party write-up is titled "…before November 2025". Search results also cite an extension to 31 May 2026 that the new official date supersedes — [Medium](https://medium.com/@ahmetatalay95/google-play-16kb-page-size-requirement-what-you-need-to-do-before-november-2025-9c85831ca11f); [Google's page (authoritative)](https://developer.android.com/guide/practices/page-sizes)
- **Foreground services** — [Play FGS & FSI requirements](https://support.google.com/googleplay/android-developer/answer/13392821); [FGS types](https://developer.android.com/develop/background-work/services/fgs/service-types):
  - Apps targeting 14+ declare each FGS type in Play Console under App content, giving a description, the user impact if it is deferred, a video link and a use case.
  - For `dataSync`, Play suggests user-initiated data-transfer jobs as the alternative.
  - `specialUse` needs a `PROPERTY_SPECIAL_USE_FGS_SUBTYPE` explanation and is reviewed.
- **Full-screen intent** — [Play FGS & FSI requirements](https://support.google.com/googleplay/android-developer/answer/13392821); [Android 14 behaviour changes](https://developer.android.com/about/versions/14/behavior-changes-14):
  - Default grant is limited to calling and alarm apps.
  - The declaration opened 31 May 2024; enforcement began 22 Jan 2025.
- **Exact alarms**: `USE_EXACT_ALARM` is subject to Play policy for limited use cases, and `SCHEDULE_EXACT_ALARM` isn't pre-granted on Android 14+ — [Schedule alarms](https://developer.android.com/develop/background-work/services/alarms/schedule)
- **Photo and video permissions** — [Photo & video permissions policy](https://support.google.com/googleplay/android-developer/answer/14115180):
  - Apps targeting 33+ "may only request the `READ_MEDIA_IMAGES` and `READ_MEDIA_VIDEO` permissions if system pickers … are not sufficient".
  - Apps that need photos only once or occasionally must use the Photo Picker.
  - A Play Console declaration is required. Full compliance became mandatory 28 May 2025.
- **Background location** — [Background location policy](https://support.google.com/googleplay/android-developer/answer/9799150):
  - Allowed only when it is core functionality.
  - Requires the Permissions Declaration Form, a video (aim for 30 s or less) showing the feature, the disclosure and the runtime prompt, and a prominent in-app disclosure before the prompt. The disclosure must use the word "location" plus a background phrase ("when the app is closed", etc.).
  - Google evaluates one feature at a time.
  - Accepted examples include real-time delivery or ride tracking. The fetched summary worded this as "for riders, not drivers"; re-read the live policy before relying on it for a tanker-driver feature.
- **Location button policy** — [Location button policy](https://support.google.com/googleplay/android-developer/answer/16909972); [Location permissions](https://developer.android.com/develop/sensors-and-location/location/permissions):
  - "If your use case requires precise location (`ACCESS_FINE_LOCATION`) only for one-time, user-initiated actions; you must implement the use of the Android location button."
  - This applies to apps targeting 37+ (using the `onlyForLocationButton` permission flag) and takes effect 27 Jan 2027.
  - `ACCESS_FINE_LOCATION` remains only for features that the button or COARSE location can't serve.
- **Battery-optimisation exemption** — [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby):
  - "Google Play policies prohibit apps from requesting direct exemption from Power Management features … unless the core function of the app is adversely affected."
  - The acceptable cases are listed in a table: non-FCM chat/VoIP, safety, task automation, and peripheral companions needing a persistent connection.
  - Most apps may still open `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS`.
- **Data safety** — [Data safety section](https://support.google.com/googleplay/android-developer/answer/10787469):
  - Declare every data type collected or shared, including location, photos/videos, files and documents, contacts, app activity, device IDs, and crash logs/diagnostics. Data collected "through any third-party libraries or SDKs" counts.
  - Also declare encryption in transit and whether users can request deletion.
  - Discrepancies can block updates or remove the app.
- **Play Integrity** defaults to 10,000 requests a day; developers can ask for more in Play Console — [Play Integrity overview](https://developer.android.com/google/play/integrity/overview)
- **Developer verification** covers apps distributed through Google Play and major OEM stores. Enforcement starts 30 Sep 2026 in Brazil, Indonesia, Singapore and Thailand and goes global in 2027 — [Android Authority](https://www.androidauthority.com/android-sideloading-changes-timeline-3679204/)
- **Live Updates** need only `POST_PROMOTED_NOTIFICATIONS`, a normal permission that users can switch off per app. Google's usage criteria are platform guidance, and misuse leads users to revoke — [Live Updates guide](https://developer.android.com/develop/ui/views/notifications/live-update)

### Inferences
**Policy matrix for the DZZLO feature set** (what each proposed feature adds):

| Feature | Manifest / runtime | Play Console form? | Data safety impact |
|---|---|---|---|
| Live Update for tanker ETA | `POST_PROMOTED_NOTIFICATIONS` (normal) | none found | none new (order data already declared, **[assumed]**) |
| Push, in-app messages | `POST_NOTIFICATIONS` (runtime 33+), merged in by OneSignal | none | device/other IDs via OneSignal/Firebase (already applicable) |
| Widget, shortcuts, QS tile, App Links | none | none | none |
| Export / share / save | none (SAF, FileProvider, MediaStore-owned files); legacy `WRITE_EXTERNAL_STORAGE` `maxSdkVersion` only if saving to Downloads on API 24–28 | none | Files kept on the device are **probably** not "collected" (inference) |
| Photo Picker / document scanner / camera intent | none; don't declare CAMERA unless using CameraX/VisionCamera | none | "Photos" (and "Files and docs" if PDFs) **if uploaded** to DZZLO servers |
| VisionCamera / CameraX custom capture | CAMERA (runtime) | none | same as above |
| Background upload | WorkManager (no permission); UIDT `RUN_USER_INITIATED_JOBS`; if a `dataSync` FGS is used, `FOREGROUND_SERVICE_DATA_SYNC` | **yes for the FGS**: declaration + video | photos/files |
| Bluetooth printer | `BLUETOOTH_CONNECT` (+ `BLUETOOTH_SCAN` with `neverForLocation` if discovering), legacy perms `maxSdkVersion=30`; `ACCESS_LOCAL_NETWORK` for LAN printers at target 37 | none found | none |
| Maps (pins only) | none (API key) | none | none |
| Tanker tracking, driver app | FINE/COARSE (runtime), `FOREGROUND_SERVICE_LOCATION`; avoid `ACCESS_BACKGROUND_LOCATION` by starting the FGS from the visible UI | **yes for the location FGS**; background location adds a declaration, video and prominent disclosure | "Approximate/Precise location" collected |
| One-tap "tag outlet GPS" | Android 17 location button when targeting 37 (policy from 27 Jan 2027) | none if the button is used | "Precise location" if stored |
| Geofencing arrival | `ACCESS_BACKGROUND_LOCATION` | **yes**: background location | location |
| OTP autofill | none (SMS Retriever) | none | none |
| Passkeys / biometrics / Play Integrity | none extra (biometric permission comes with androidx.biometric, **[unverified]**) | none | none new |

Actions for this app:
- **16 KB**: audit the release AAB now. Run `zipalign -c -P 16` and look at APK Analyzer's `lib/` for every `.so`: RN core, Hermes, VisionCamera/Nitro, MMKV, Maps, ML Kit if bundled. The Feb 2027 date gives about four months of margin, and every new native library added from this plan must be checked.
- **FSI, exact alarms and battery exemption**: stay out. DZZLO is not a calling or alarm app. Use inexact reminders, and `setExact` + `OnAlarmListener` only while the app is alive.

### Gaps
- I did not re-fetch Play's **SMS & Call Log permissions** policy. SMS Retriever avoids it entirely; adding `READ_SMS`/`RECEIVE_SMS` would trigger it.
- No Play policy text was found for **AppFunctions**, and none for Live Updates beyond platform guidance.
- Whether `RUN_USER_INITIATED_JOBS` or `POST_PROMOTED_NOTIFICATIONS` need any Play Console declaration: none found; unconfirmed.
- The exact wording of the background-location "delivery tracking" examples (riders vs drivers) comes from a fetched summary, not the verbatim page.
- No 2027 target-API date was published yet. Inference only: Google's yearly pattern suggests API 37 around 31 Aug 2027.

## 4. What do low-end Indian devices and OEM skins change about the recommended approach (battery optimisation, notification delivery, storage)?

### Takeaway
India's installed base in Aug 2026 is about 47 % Android 15–16 and about 32 % Android 11–13. So every API 33/34/36 feature needs its API 24–32 fallback, and the fallback must be built first.

The top Indian brands are rated among the most aggressive process killers on dontkillmyapp:
- 5/5: Xiaomi, OnePlus, Samsung
- 4/5: Oppo
- 3/5: Vivo, realme, Tecno

Background work and data-only pushes will be unreliable. Consequences:
- Anything important should be a **visible** notification backed by server truth.
- The app should refresh on open.
- An active widget keeps the app out of the Restricted bucket.
- Offer an OEM-specific "keep DZZLO running" guide rather than requesting battery-optimisation exemption, which Play prohibits for this app type.

Prefer system-delegated components: Photo Picker, SAF, share sheet, ML Kit scanner, code scanner, print dialog. They avoid permissions, keep memory out of the app process (Android 17 enforces RAM-based limits), and work on the Android 12–15 fleet via Play services.

### Cited Findings
- **Version mix**: India mobile, Aug 2026 — 16 = 24.11 %, 15 = 23.28 %, 13 = 13.85 %, 14 = 12.14 %, 12 = 9.41 %, 11 = 8.81 % — [StatCounter](https://gs.statcounter.com/android-version-market-share/mobile/india)
- **dontkillmyapp ranking** (worst first): Huawei, Xiaomi, OnePlus and Samsung 5/5; Meizu, Asus and Oppo 4/5; Wiko, Lenovo, Vivo, realme, Motorola, Blackview and Tecno 3/5; Sony 2/5; AOSP/Pixel, Nokia and HTC 0 — [dontkillmyapp](https://dontkillmyapp.com/)
- **Xiaomi (MIUI/HyperOS) user-side steps** — [dontkillmyapp: Xiaomi](https://dontkillmyapp.com/xiaomi):
  - enable Autostart;
  - set Battery saver to "No restrictions";
  - lock the app in Recents;
  - optionally disable MIUI optimisations.

  A library, XomaDev MIUI-autostart, can check the Autostart state.
- **FCM**: high-priority messages that don't produce user-visible notifications are deprioritised (7-day window). Normal priority waits for Doze to end — [FCM priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority)
- **Standby buckets** — [App Standby Buckets](https://developer.android.com/topic/performance/appstandby):
  - Restricted apps run jobs once a day in a 10-minute batch, with one alarm a day, even while charging.
  - Android 13+ moves an app to Restricted after 8 days unused.
  - Apps with **active widgets** are exempt.
- **Battery exemption**: requesting it directly is Play-prohibited unless the core function breaks, but most apps may send users to `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS` — [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby)
- **Expedited work** quotas depend on the standby bucket and don't apply in the foreground. UIDT jobs are exempt from bucket quotas — [WorkManager](https://developer.android.com/develop/background-work/background-tasks/persistent/getting-started/define-work); [UIDT](https://developer.android.com/develop/background-work/background-tasks/uidt)
- **Android 17 memory limits** apply to all apps and scale with device RAM; offending processes are "abruptly terminated" — [Android 17 blog](https://android-developers.googleblog.com/2026/06/Android-17.html); [all-apps changes](https://developer.android.com/about/versions/17/behavior-changes-all)
- **OEM Live Update surfaces**: Samsung One UI 8 Now Bar (a developer toggle in beta 3) and Xiaomi HyperOS 3.1 Super Island both use the standard Live Updates API — [Android Authority](https://www.androidauthority.com/one-ui-8-live-updates-support-3573794/); [Gizmochina](https://www.gizmochina.com/2026/01/30/xiaomi-hyperos-3-1-update-new-features-smarter-ui-eligible-device-list/)
- **Play-services dependencies**: the Photo Picker backport (API 19–32), ML Kit Document Scanner, Google code scanner, Play Integrity, passkeys and geofencing all rely on Google Play services, with models and UIs delivered by Play services to keep APK size down — [Photo Picker](https://developer.android.com/training/data-storage/shared/photopicker); [Doc scanner](https://developers.google.com/ml-kit/vision/doc-scanner); [Code scanner](https://developers.google.com/ml-kit/vision/barcode-scanning/code-scanner); [Play Integrity](https://developer.android.com/google/play/integrity/overview); [Credential Manager](https://developer.android.com/identity/sign-in/credential-manager); [Geofencing](https://developer.android.com/develop/sensors-and-location/location/geofencing)
- **Storage without permissions**: SAF needs no permission; `MediaStore.Downloads` needs none for owned files on API 29+; on API 24–28, `WRITE_EXTERNAL_STORAGE` with `maxSdkVersion` — [SAF](https://developer.android.com/training/data-storage/shared/documents-files); [MediaStore](https://developer.android.com/training/data-storage/shared/media)
- **Geofence latency** is 2–6 minutes under background limits and depends on Wi-Fi and network for accuracy — [Geofencing](https://developer.android.com/develop/sensors-and-location/location/geofencing)

### Inferences
**Notification delivery**:
- Treat push as best-effort on Xiaomi, OnePlus, Samsung, Oppo and Vivo.
- Every order, payment and approval event should be a visible notification: this keeps FCM priority and helps users.
- Data-only pushes should only nudge a widget or cache.
- The app must re-sync on resume, which the existing cursor/refresh design already supports.

**OEM guide screen**: detect the manufacturer (`Build.MANUFACTURER`) and show tailored, illustrated steps from dontkillmyapp (Xiaomi Autostart and "No restrictions"; Samsung "Never sleeping apps", **[unverified wording]**). Link to `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS`; never to `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`. Show it only to dealers who rely on alerts (1–2 days).

**Widgets** double as an anti-Restricted-bucket measure for dealers who don't open the app daily, a reason to ship the Daily Summary widget early.

**Live Updates reach**:
- Only Android 16+ devices (about 24 % in India), and only where the skin renders them.
- The same code posts an ordinary ongoing notification elsewhere.
- Build the ordinary one first and let promotion be a bonus.

**AppFunctions reach**: Android 16+ **and** Gemini's preview program. That is effectively zero DZZLO users in 2026.

**Low-RAM phones**:
- Downscale photos before OCR or upload; ML Kit doesn't need full resolution **[inference]**.
- Stream uploads from a file URI rather than base64 through the JS bridge.
- Generate long invoice PDFs server-side, or with the print adapter in small documents, rather than holding large WebViews or bitmaps. Android 17's memory limiter kills offenders.
- Prefer system UIs (Photo Picker, document scanner, code scanner) that run in other processes.

**Storage on budget phones**:
- Write exports to the cache, hand them to the share sheet or SAF, then delete them.
- Keep only small derived data (e.g. widget numbers) persistently.
- Downloads via MediaStore are for files the user asked to keep.

**Old-Android fallbacks to budget for**:
- API 24–28: no `MediaStore.Downloads`; use SAF or legacy storage.
- API 24–25: shortcuts need 25, pinning needs 26.
- API 24–27: no passkeys; keep OTP and password.
- API 24–32: no notification runtime prompt, and the Photo Picker comes from the Play-services backport.
- API 24–35: no `ProgressStyle`.
- Everything below 36: no AppFunctions.

### Gaps
- No India-specific data on FCM or OneSignal delivery rates by OEM.
- No data on the share of Indian devices without Google Play services (assumed small) or on the RAM distribution / Android Go share.
- dontkillmyapp's ranking has no last-updated date and may predate One UI 8 / HyperOS 3 changes.
- **India's TRAI DLT SMS-template registration** probably means adding the SMS Retriever hash to the OTP text needs a newly approved template with 2factor.in. **[unverified; not researched this session]**
- Whether stable One UI 8+ still gates third-party Live Updates behind any setting is unverified.
