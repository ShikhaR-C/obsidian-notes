# Phase 6 — Widgets, Shortcuts and Intents: The App Outside the App

> Level: Advanced | Time: ~3 h to read · 4–7 weeks to build on both platforms _(est.)_ | Outcome: one tested JSON snapshot feeding a Daily Summary widget on both home screens, "New order" as a control and a quick action, and an "outstanding balance" answer from Siri and Spotlight — plus an honest verdict on Android's assistants in 2026.

---

## 1. The One Idea

Everything in this phase runs where React Native is not. A widget renders in a system process from a timeline you handed over earlier. Siri runs an App Intent's Swift `perform()` while the app is cold — iOS 27 can even run it inside an extension (`ExecutionTargets`: `.main`, `.appIntentsExtension`, `.widgetKitExtension`), and the App Intents Testing framework runs intents "out-of-process". A quick action can launch the app before the JS bundle has loaded.

So one rule governs the phase: **JavaScript computes, native code only reads.** Whenever the app holds fresh, correctly rounded numbers, it writes a small JSON snapshot, and every outside surface reads it — or, once [[09-phase-9-security-privacy-and-release]] puts the auth token in shared secure storage, calls the API itself.

```
 React Native (JS) ── Daily Summary page 1 → buildSnapshot() → formatMoney(), whole paise
                   ── Customers summary    → totalBalance      ── sign-out → clearAll()
        │  NativeSharedStore.writeSnapshot('summary.json', json)                         (§2)
        ▼
 iOS  App Group group.in.vsyst.dzzlooms.shared/          Android  filesDir/summary.json
   ├─ DzzloWidgets: WidgetKit widget (§3), Control (§5)     ├─ Glance DailySummaryWidget (§4)
   ├─ App Intent "Outstanding" → Siri, Shortcuts (§7)       ├─ AppFunction, flagged off (§8)
   └─ customers.json → Spotlight IndexedEntity (§7)          └─ App Shortcuts carry no data (§6)
```

| Surface | iOS (introduced) | Android (introduced) | What DZZLO shows |
|---|---|---|---|
| Home-screen widget | WidgetKit (iOS 14) | app widget via Jetpack Glance 1.2.0 (minSdk 23) | today's ₹ sales, HSD / MS litres, orders; the dealer's outstanding; later, the last order's status |
| Lock Screen widget | accessory families (iOS 16) | Pixel Tablet; phones promised "after Android 16 (QPR1)", unconfirmed | orders and litres; money only by opt-in |
| Control / tile | Controls (iOS 18) | Quick Settings tile (API 24; add prompt API 33) | "New order" |
| Quick actions | `UIApplicationShortcutItem` (iOS 9) | App Shortcuts (API 25; pinned 26) | New order · Today · Customers |
| Voice, search, agents | App Intents (iOS 16), App Shortcut phrases, Spotlight `IndexedEntity` (iOS 18), snippets (iOS 26) | AppFunctions (API 36, Jetpack alpha); `onProvideAssistContent` (API 23) | "What's my outstanding balance in DZZLO?"; customers in Spotlight |

**Where the numbers come from** (read 2026-09-29):

- **Today** — the v2 Daily Summary (`src/screens/v2/Common/DailySummary/useScreenModel.js` → `useV4_screen_daily_summaryQuery` in `src/store/apis/v4/daily_summary.js`) returns a `summary` with `count`, `qty.{petrol, diesel}`, `productAmount` and `cashReimb`, on page 1 only. `src/helpers/DailySummary/totals.js` adds figures in integer paise and millilitres; `format.js`'s `formatMoney` prints `₹ 75,784.20` with a no-break space after the ₹.
- **Outstanding** — for a dealer, the v2 Customers summary strip's `totalBalance`, captioned "Total balance" (`src/screens/v2/Dealer/Customers/components/SummaryStrip.js:78-81`). A customer's own balance has no v2 read model yet: decide its source before a customer widget (open question for the user). The **last order** needs the Orders list — still a v1 screen — to write a `lastOrder` section: a later schema bump.

The snapshot carries the text JS already formatted plus whole paise, so **Swift and Kotlin never round**. The evidence of value is thin but real: among the business apps reviewed only Zoho ships these surfaces — Lock Screen widgets and Live Activities on iOS 16, then a Control Center widget "for creating transactions" and Siri-runnable App Shortcuts in Spotlight on iOS 18 — and no evidence of widget demand among Indian SMB users was found (gap). On Android there is a practical bonus: apps with active widgets are exempt from the Restricted standby bucket, which also protects the reminders of [[05-phase-5-notifications-and-live-status]].

Build order: `NativeSharedStore` → the widget on both platforms → quick actions → the Control → App Intents → an AppFunctions spike; capstone C in [[10-capstones]] strings the snapshot, widget and intent together. Every surface ships on both platforms, or its section says what the other gets instead.

## 2. `NativeSharedStore` — One Snapshot, Many Readers

### 2.1 The contract: `summary.json`, schema 1

```json
{
  "v": 1, "writtenAt": "2026-09-29T08:35:00Z", "role": "dealer", "lang": "en",
  "window": { "from": "2026-09-29T00:30:00Z", "to": "2026-09-30T00:30:00Z" },
  "today": { "orders": 42, "salesPaise": 7578420, "salesText": "₹ 75,784.20",
             "dieselText": "3,210.000", "petrolText": "1,050.000" },
  "outstanding": { "customers": 37, "paise": 128000000, "text": "₹ 12,80,000.00" }
}
```

The 06:00 IST shift start is 00:30 UTC; the figures are illustrative. The rules:

1. **Text is final; money also travels as whole paise.** JS formats with `formatMoney` / `formatLitres` in the user's language, and computes paise with `Math.round(rupees × 100)` — the rule `totals.js` already applies (export it, don't copy it). Native code prints. `v` bumps on any breaking change; an unknown `v` reads as "Open DZZLO".
2. **Only today.** Write while the Daily Summary shows the current shift window — never after the user picks Yesterday, Last 7 days, This month or Custom.
3. **Nothing else personal, and nothing after sign-out.** A separate `customers.json` (id + business name, dealers only) feeds Spotlight (§7); sign-out deletes both files and reloads every surface.

### 2.2 Spec, registration and the JavaScript side

```ts
// specs/NativeSharedStore.ts — name is 'summary.json' | 'customers.json'; native code rejects anything else
import type {TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';
export interface Spec extends TurboModule {
  writeSnapshot(name: string, json: string): Promise<void>;
  readSnapshot(name: string): Promise<string | null>;
  clearAll(): Promise<void>;
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativeSharedStore');
```

Registration is [[01-phase-1-foundations]]'s `NativeAppInfo` recipe with the name swapped: `"NativeSharedStore": "RCTNativeSharedStore"` in `codegenConfig.ios.modulesProvider`; `add(NativeSharedStorePackage())` inside `PackageList(this).packages.apply { … }` in `MainApplication.kt` (the placeholder is at lines 16-19); a `src/native/__tests__/sharedStore.config.test.js` pin beside Phase 1's `appInfo.config.test.js`, same shape; and a `jest.mock('./specs/NativeSharedStore', …)` stub in `jest.setup.js` whose three methods resolve.

Three red tests come before any Swift or Kotlin:

| Test (Tier 1) | Asserts |
|---|---|
| `src/helpers/SharedSnapshot/__tests__/buildSnapshot.test.js` | a known input yields exactly the golden fixture `src/native/__fixtures__/summary.v1.json`; text equals `formatMoney`; paise are integers; a new section merges into the previous snapshot |
| `…/shouldWriteSnapshot.test.js` | true only for the current shift window |
| `src/native/__tests__/sharedStore.test.js` | one write per new summary; a rejected write is swallowed; sign-out calls `clearAll` |

```js
// src/native/sharedStore.js — the only door screens use
import NativeSharedStore from '../../specs/NativeSharedStore';
import { buildSnapshot } from '../helpers/SharedSnapshot/buildSnapshot';

export const saveSnapshotSection = async section => {
  try {
    const previous = JSON.parse((await NativeSharedStore.readSnapshot('summary.json')) ?? 'null');
    await NativeSharedStore.writeSnapshot('summary.json', JSON.stringify(buildSnapshot(previous, section)));
  } catch (e) {
    console.warn('shared snapshot not written', e);      // a widget must never break a screen
  }
};
export const clearSharedSnapshots = () => NativeSharedStore.clearAll().catch(() => {});
```

Wiring: the Daily Summary's `useScreenModel.js` saves `{ today }` when a page-1 `summary` arrives and `shouldWriteSnapshot(window, now)` holds; the Customers screen saves `{ outstanding }`; the `logoutUser.fulfilled` path (`src/store/slices/auth.js:112`) calls `clearSharedSnapshots()` through a listener. A JS bundle that imports this spec must never reach a binary without the module — the OTA fingerprint rule in [[09-phase-9-security-privacy-and-release]] guards that.

### 2.3 iOS: Swift behind the adapter

```swift
// ios/dzzlo_oms_app/SharedStore/SharedStore.swift — plain Swift; RCTNativeSharedStore.mm beside it only forwards
import Foundation
import WidgetKit

@objcMembers public final class SharedStore: NSObject {
  public static let groupId = "group.in.vsyst.dzzlooms.shared"
  static let allowed: Set<String> = ["summary.json", "customers.json"]
  private let dir: URL?

  public init(directory: URL?) { dir = directory; super.init() }          // tests pass a temp dir
  public override convenience init() {                                     // containerURL: iOS 7.0
    self.init(directory: FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: SharedStore.groupId))
  }

  public func write(_ name: String, json: String) throws {
    guard Self.allowed.contains(name), let dir else { throw CocoaError(.fileWriteNoPermission) }
    try Data(json.utf8).write(to: dir.appendingPathComponent(name), options: .atomic)
    WidgetCenter.shared.reloadAllTimelines()                                // iOS 14.0
  }

  public func clearAll() {
    if let dir { Self.allowed.forEach { try? FileManager.default.removeItem(at: dir.appendingPathComponent($0)) } }
    WidgetCenter.shared.reloadAllTimelines()
  }
}
```

The Objective-C++ shell is Phase 1's adapter shape — `RCTNativeSharedStore.h/.mm` in the same folder, importing `<React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>` before `"dzzlo_oms_app-Swift.h"`: `+moduleName` returns `@"NativeSharedStore"`, `getTurboModule:` returns a `NativeSharedStoreSpecJSI`, and `writeSnapshot:json:resolve:reject:` calls `[_store write:name json:json error:&error]`, rejecting with `E_SHARED_STORE`. Entitlements:

```xml
<!-- dzzlo_oms_app.entitlements, inside com.apple.security.application-groups; DzzloWidgets gets only the second line -->
<string>group.in.vsyst.dzzlooms.onesignal</string>   <!-- OneSignal's, unchanged; the NSE keeps only this one -->
<string>group.in.vsyst.dzzlooms.shared</string>      <!-- new: app ↔ DzzloWidgets -->
```

The account holder registers the new group for team `YT955YZMZU`; App Groups also act as keychain access groups, which Phase 9 will use.

### 2.4 Android: a plain store and a thin shell

The Glance receiver ships inside the same APK, so it reads the app's own private `filesDir` — no content provider, no world-readable file.

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/sharedstore/SharedStore.kt — plain Kotlin, JUnit-able
package `in`.vsyst.dzzlooms.sharedstore

import android.util.AtomicFile
import java.io.File

class SharedStore(private val dir: File, private val onChange: () -> Unit = {}) {
  fun write(name: String, json: String) {
    require(name in ALLOWED) { "not a shared snapshot: $name" }
    val file = AtomicFile(File(dir, name))                  // API 17: all-or-nothing replace
    val out = file.startWrite()
    try { out.write(json.toByteArray(Charsets.UTF_8)); file.finishWrite(out) }
    catch (e: Exception) { file.failWrite(out); throw e }
    onChange()
  }
  fun read(name: String): String? = File(dir, name).takeIf { name in ALLOWED && it.exists() }
    ?.let { AtomicFile(it).readFully().toString(Charsets.UTF_8) }
  fun clearAll() { ALLOWED.forEach { File(dir, it).delete() }; onChange() }
  companion object { val ALLOWED = setOf("summary.json", "customers.json") }
}
// NativeSharedStoreModule.kt — the shell (imports as in Phase 1, plus androidx.glance.appwidget.updateAll)
class NativeSharedStoreModule(ctx: ReactApplicationContext) : NativeSharedStoreSpec(ctx) {
  private val app = ctx.applicationContext
  private val store = SharedStore(app.filesDir) {
    CoroutineScope(Dispatchers.Default).launch { DailySummaryWidget().updateAll(app) }   // §4
  }
  override fun getName() = NAME
  override fun writeSnapshot(name: String, json: String, promise: Promise) =
    runCatching { store.write(name, json) }.fold({ promise.resolve(null) }, { promise.reject("E_SHARED_STORE", it) })
  // readSnapshot and clearAll resolve store.read(name) and store.clearAll() the same way
  companion object { const val NAME = "NativeSharedStore" }
}
```

`NativeSharedStoreSpec` is generated into the `javaPackageName` Phase 1 put in `codegenConfig`; Kotlin needs backticks around the `in` segment of that package, exactly as `MainApplication.kt:1` does.

### 2.5 One fixture, three languages

`src/native/__fixtures__/summary.v1.json` is the contract, and all three suites read it: **Jest** (`buildSnapshot` output equals it); **XCTest** (`SummarySnapshotTests` decodes it, added to the test bundle by reference; `SharedStoreTests` uses `SharedStore(directory:)` on a temp folder — an unknown name throws, a round trip holds, `clearAll` empties); **JUnit + Robolectric** (`SummarySnapshotTest` parses it through `android { sourceSets { test { resources.srcDirs += "../../src/native/__fixtures__" } } }`; `SharedStoreTest` rejects unknown names and fires `onChange` once per write). Rename one field and all three go red — the snapshot cannot drift silently. On devices:

```bash
xcrun simctl get_app_container booted in.vsyst.dzzlooms group.in.vsyst.dzzlooms.shared   # then read summary.json
adb shell run-as in.vsyst.dzzlooms cat files/summary.json                                  # debug builds
```

## 3. iOS Widgets

### 3.1 The platform (Xcode 27 SDK, verified 2026-09-30)

| API | iOS |
|---|---|
| `StaticConfiguration`, `TimelineProvider`, `WidgetCenter.reloadTimelines(ofKind:)` / `reloadAllTimelines()` | 14.0 |
| Lock Screen families `.accessoryCircular`, `.accessoryRectangular`, `.accessoryInline` | 16.0 |
| `ActivityConfiguration` (Phase 5); `if #available` inside a `WidgetBundle` | 16.1 |
| `AppIntentConfiguration`, `AppIntentTimelineProvider`, `Button(intent:)`, `containerBackground(for:)` | 17.0 |
| Controls — `ControlWidget`, `StaticControlConfiguration`, `ControlWidgetButton` | 18.0 |
| `WidgetPushHandler` — server-driven reloads; Push Notification entitlement on the extension | 26.0 |

Apple: "a daily budget typically includes from 40 to 70 refreshes" for a frequently viewed widget, and WidgetKit push "doesn't replace timeline updates". `.privacySensitive()` dates from iOS 15.0. iOS 26 adds the accented (tinted, glass) look; iOS 27 lets "widgets … be customized through App Intents and dynamic styling". Widget buttons act through App Intents and stay inactive on a locked device "unless a person authenticates". Source: https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date

### 3.2 A timeline that costs almost nothing

Two entries and `.never`: "now" with the figures, and the shift window's end saying "Shift closed — open DZZLO". The snapshot write reloads timelines (§2.3), so the widget spends almost none of its budget and never passes yesterday off as today.

```swift
// ios/DzzloWidgets/DailySummaryWidget.swift
import SwiftUI
import WidgetKit

struct SummaryEntry: TimelineEntry { let date: Date; let snapshot: SummarySnapshot?; let closed: Bool }
struct SummaryProvider: TimelineProvider {
  func placeholder(in context: Context) -> SummaryEntry { .init(date: .now, snapshot: nil, closed: false) }
  func getSnapshot(in context: Context, completion: @escaping (SummaryEntry) -> Void) {
    completion(.init(date: .now, snapshot: .loadShared(), closed: false))
  }
  func getTimeline(in context: Context, completion: @escaping (Timeline<SummaryEntry>) -> Void) {
    let snap = SummarySnapshot.loadShared()                  // nil → "Open DZZLO"
    var entries = [SummaryEntry(date: .now, snapshot: snap, closed: false)]
    if let end = snap?.windowEnd, end > .now { entries.append(.init(date: end, snapshot: snap, closed: true)) }
    completion(Timeline(entries: entries, policy: .never))
  }
}

struct DailySummaryWidget: Widget {
  var body: some WidgetConfiguration {
    StaticConfiguration(kind: "DailySummary", provider: SummaryProvider()) { entry in
      SummaryView(entry: entry).widgetURL(DzzloLinks.dailySummary)      // Phase 8 owns the URL
    }
    .configurationDisplayName("Today")
    .description("Today's sales, litres and orders.")
    .supportedFamilies([.systemSmall, .systemMedium, .accessoryRectangular, .accessoryInline])
  }
}

@main
struct DzzloWidgetsBundle: WidgetBundle {                    // Phase 5's bundle, grown; NewOrderControl is §5
  var body: some Widget { DzzloOrderLiveActivity(); DailySummaryWidget(); if #available(iOS 18.0, *) { NewOrderControl() } }
}
```

`SummarySnapshot` is one Swift file with three target memberships — app, `DzzloWidgets`, XCTest bundle — whose `loadShared()` reads the App Group container. `SummaryView` applies `containerBackground(for: .widget)` behind an `if #available(iOS 17.0, *)` check, since `DzzloWidgets` runs from 16.1.

### 3.3 Sizes, language, colour, privacy — and tests

- **`systemSmall`:** sales, "Today", snapshot time. **`systemMedium`:** adds HSD / MS litres, orders and the dealer's outstanding.
- **`accessoryRectangular` / `accessoryInline`:** orders and litres; ₹ on the Lock Screen only if the user opts in (house decision), and every figure under `.privacySensitive()` so the system can redact it when locked.
- **Hindi:** labels from the extension's `Localizable.strings` (en, hi). Test the smallest family at the largest text sizes first — the widget's version of the 320 dp rule.
- **Colours and review:** the extension can't import `src/theme`, so its asset colour sets mirror the tokens, and a config pin — `src/theme/__tests__/widgetColours.config.test.js`, the house `*.config.test.js` pattern — fails on drift. Guideline 2.5.16: widgets "should be related to the content and functionality of your app"; 4.4: extensions "may not include marketing, advertising, or in-app purchases".
- **Refresh:** v1's widget refreshes by opening the app. An AppIntent-driven button — `Button(intent: RefreshSummaryIntent())`, whose `perform()` calls `WidgetCenter.shared.reloadTimelines(ofKind: "DailySummary")` — could only re-read the snapshot until Phase 9 gives the extension a token. Later, an iOS 26 `WidgetPushHandler` can reload it when the server posts invoices.

**Tests:** XCTest, red first — the fixture decodes; a missing file or `v: 2` → `nil`; `getTimeline` appends a closed entry at `windowEnd`. **Device:** a 17e and a 17 Pro Max simulator — Home Screen small and medium, Lock Screen rectangular and inline; light, dark and iOS 26 tinted; en and hi; then sign out and watch it fall back to "Open DZZLO". Optional-track alternative: `expo-widgets` (SDK 56+, iOS only) can author this widget in JSX — see §9.

## 4. Android Widgets with Glance

### 4.1 Version and cost

Jetpack Glance 1.2.0 went stable on 2026-08-26 (`glance`, `glance-appwidget`, `glance-material3`); its minSdk rose to 23 in 1.2.0-beta01, below DZZLO's 24. Glance 1.1.0 (June 2024) added generated previews (`providePreview()`, `GlanceAppWidgetManager.setWidgetPreview()`), a unit-test library (`runGlanceAppWidgetUnitTest`, `testTag`) and Material 3. The cost is real: Glance is Compose-based and this app has no Compose — the runtime, the Kotlin 2.x Compose compiler plugin, a bigger APK and longer builds _(est.)_.

```groovy
classpath("org.jetbrains.kotlin:compose-compiler-gradle-plugin:2.1.20")   // android/build.gradle, buildscript; Kotlin 2.1.20
apply plugin: "org.jetbrains.kotlin.plugin.compose"                        // android/app/build.gradle from here on
android { buildFeatures { compose = true } }
dependencies {
  implementation "androidx.glance:glance-appwidget:1.2.0"
  implementation "androidx.work:work-runtime-ktx:2.8.1"           // 2.8.1 already resolves in the graph
  testImplementation "androidx.glance:glance-appwidget-testing:1.2.0"
}
```

The plugin and testing-artifact coordinates are not verified in this course's sources — check Glance's release page and the Kotlin 2.1.20 docs before the first build. Source: https://developer.android.com/jetpack/androidx/releases/glance

### 4.2 `DailySummaryWidget`

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/widgets/DailySummaryWidget.kt (imports: androidx.glance.* and compose units)
class DailySummaryWidget : GlanceAppWidget() {
  override val sizeMode = SizeMode.Responsive(setOf(SMALL, MEDIUM))

  override suspend fun provideGlance(context: Context, id: GlanceId) {
    val s = SummarySnapshot.read(context.filesDir)                    // the fixture-tested parser
    provideContent {
      Column(GlanceModifier.fillMaxSize().padding(12.dp)
          .background(ColorProvider(R.color.widget_surface))          // res colours mirror src/theme
          .clickable(actionStartActivity<MainActivity>())) {
        if (s == null) Text(context.getString(R.string.widget_open_dzzlo))
        else {
          Text(s.salesText, style = TextStyle(fontWeight = FontWeight.Bold, fontSize = 20.sp))
          if (LocalSize.current.width >= MEDIUM.width)
            Text(context.getString(R.string.widget_litres_orders, s.dieselText, s.petrolText, s.orders))
        }
      }
    }
  }

  companion object { val SMALL = DpSize(120.dp, 60.dp); val MEDIUM = DpSize(250.dp, 110.dp) }
}

class DailySummaryWidgetReceiver : GlanceAppWidgetReceiver() { override val glanceAppWidget: GlanceAppWidget = DailySummaryWidget() }
```

```xml
<receiver android:name=".widgets.DailySummaryWidgetReceiver" android:exported="true">
  <intent-filter><action android:name="android.appwidget.action.APPWIDGET_UPDATE" /></intent-filter>
  <meta-data android:name="android.appwidget.provider" android:resource="@xml/daily_summary_widget_info" />
</receiver>
<!-- res/xml/daily_summary_widget_info.xml -->
<appwidget-provider xmlns:android="http://schemas.android.com/apk/res/android"
    android:minWidth="110dp" android:minHeight="40dp" android:resizeMode="horizontal|vertical" android:updatePeriodMillis="0"
    android:widgetCategory="home_screen" android:initialLayout="@layout/glance_default_loading_layout" />
```

Google said lock-screen widgets would reach AOSP phones "starting with the release after Android 16 (QPR1)" — unconfirmed on phones in 2026 — and every widget is eligible by default. To keep money off a lock screen, copy the provider file into `res/xml-36/` with `android:widgetCategory="home_screen|not_keyguard"`.

### 4.3 Keeping it fresh — cheaply

After a sync, `SharedStore`'s `onChange` calls `updateAll` (§2.4). On a clock, `updatePeriodMillis` below 30 minutes isn't honoured and Google recommends at most hourly — so it stays 0, and WorkManager (15-minute floor) re-renders hourly, keeping "updated 3 h ago" and "Shift closed" true. No network in v1: no token lives outside JS until Phase 9. And an active widget exempts DZZLO from the Restricted standby bucket — the cheapest reliability win in this phase.

```kotlin
class SummaryRefreshWorker(ctx: Context, p: WorkerParameters) : CoroutineWorker(ctx, p) {
  override suspend fun doWork(): Result { DailySummaryWidget().updateAll(applicationContext); return Result.success() }
}
// in DailySummaryWidgetReceiver; onDisabled calls cancelUniqueWork("daily-summary-widget")
override fun onEnabled(context: Context) { super.onEnabled(context)
  WorkManager.getInstance(context).enqueueUniquePeriodicWork("daily-summary-widget",
    ExistingPeriodicWorkPolicy.KEEP, PeriodicWorkRequestBuilder<SummaryRefreshWorker>(1, TimeUnit.HOURS).build()) }
```

**Android 17 cap:** when targeting API 37, a widget's `RemoteViews` bitmaps and icons may use at most 1.5 × screen width × screen height × 4 bytes; going over throws `IllegalArgumentException`. Stay with text and vector icons. Source: https://developer.android.com/about/versions/17/behavior-changes-17

### 4.4 The JSX alternatives, and tests

| Route | Version (date) | New Architecture | How it renders | Verdict |
|---|---|---|---|---|
| Glance in Kotlin (above) | 1.2.0 (2026-08-26) | native | real `RemoteViews` via Compose | **build this** — 5–8 days _(est.)_ |
| react-native-android-widget | 0.22.1 (2026-08-17) | docs: "Supports the React Native new architecture"; Directory: declared true, GitHub-detected false | "render[s] the React Native views to an image", so it must know the exact size, which some launchers misreport; lists `expo` (≥ 54) as a peer — whether optional was not checked | faster (3–5 days _(est.)_), but an image-rendered widget is exactly what Android 17's bitmap cap measures _(inference)_ |
| Voltra | 2.3.2 (2026-09-22) | TurboModule clients | JSX → Glance on Android, SwiftUI on iOS | one JSX codebase; its config plugins assume prebuild, so here they'd be reproduced by hand _(inference)_ |
| expo-widgets | 57.0.22 | Expo module | Android only from SDK 58, on "a dedicated Hermes runtime" | Expo track only |

**Tests:** JUnit, red first — the shared fixture parses; a missing file, bad JSON or `v: 2` → `null`. Then Glance's unit-test library with `testTag`s on three states: small shows sales only, medium adds litres and orders, `null` shows "Open DZZLO" (take the node-matching calls from the library's reference). **Device:** the Android 16 AVD and a Samsung or Xiaomi phone — resize, dark mode, Hindi, font scale 1 and 2, then sign out. Source: https://github.com/sAleksovski/react-native-android-widget/blob/master/docs/docs/limitations.md · https://github.com/callstackincubator/voltra

## 5. Controls and Tiles

One action on both platforms: "New order". The iOS Control (iOS 18.0) lives in `DzzloWidgets`, registered behind `if #available` (§3.2); its intent opens the app and drops the route into §6's inbox:

```swift
@available(iOS 18.0, *)
struct NewOrderControl: ControlWidget {
  var body: some ControlWidgetConfiguration {
    StaticControlConfiguration(kind: "in.vsyst.dzzlooms.new-order") {
      ControlWidgetButton(action: OpenNewOrderIntent()) { Label("New order", systemImage: "fuelpump") }
    }
  }
}
@available(iOS 18.0, *)
struct OpenNewOrderIntent: AppIntent {
  static let title: LocalizedStringResource = "New order"
  static let openAppWhenRun = true            // deprecated in iOS 26: declare supportedModes with .foreground(…)
  func perform() async throws -> some IntentResult { ShortcutInbox.shared.deliver("new_order"); return .result() }
}
```

`ShortcutInbox` lives in the app target, so give `OpenNewOrderIntent` both target memberships, and confirm on a device that the app process runs it after launch.

Android's Quick Settings tile (`TileService`, API 24; `requestAddTileService()`, API 33) comes with guidance: at most two tiles, and not "just to launch the app" or to show display-only information — a "New order" tile is borderline. **Parity statement:** Android gets "New order" as an App Shortcut (§6) instead; build a tile only if dealers ask. It would be one `TileService` subclass plus:

```xml
<service android:name=".tiles.NewOrderTileService" android:exported="true" android:label="@string/tile_new_order"
    android:icon="@drawable/ic_tile_new_order" android:permission="android.permission.BIND_QUICK_SETTINGS_TILE">
  <intent-filter><action android:name="android.service.quicksettings.action.QS_TILE" /></intent-filter></service>
```

## 6. Quick Actions

| Library | Version (date) | State | On RN 0.84 |
|---|---|---|---|
| react-native-quick-actions | 0.3.13 (2019-11-24) | archived | no |
| expo-quick-actions | 6.0.2 (2026-05-27) | New-Arch Expo module, iOS and Android; "Both Apple and Android recommend a max of 4 items" | needs `expo`, and no Expo SDK pairs with 0.84 |
| @rn-org/react-native-shortcuts | 0.2.0 (2026-02-15) | ~1k downloads a week | too small to depend on |

**Recommendation:** on 0.84, a thin in-house `NativeShortcuts` (~1 day per platform _(est.)_), registered like §2.2 with `"NativeShortcuts": "RCTNativeShortcuts"` and fronted by `src/native/shortcuts.js`; if the Expo track is taken after the upgrade, swap to expo-quick-actions and delete the module. The items are **dynamic** — set after sign-in by role, cleared at sign-out — because static items can't know the role and nothing should show to a signed-out user. Keep to four or fewer, and follow Google: "Never include sensitive user info in shortcut metadata".

```ts
// specs/NativeShortcuts.ts
import type {CodegenTypes, TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';
export type ShortcutItem = {type: string; title: string};
export type ShortcutEvent = {type: string};
export interface Spec extends TurboModule {
  setItems(items: ShortcutItem[]): void;
  getInitialShortcut(): Promise<string | null>;
  readonly onShortcut: CodegenTypes.EventEmitter<ShortcutEvent>;
}
export default TurboModuleRegistry.getEnforcing<Spec>('NativeShortcuts');
```

**iOS.** The `SceneDelegate` lives inside `AppDelegate.swift` (lines 41-58), so quick actions arrive there (`UIWindowSceneDelegate`, iOS 13) and wait in a tiny inbox until JS asks:

```swift
// ios/dzzlo_oms_app/Shortcuts/ShortcutInbox.swift — beside RCTNativeShortcuts.h/.mm
@objcMembers public final class ShortcutInbox: NSObject {
  public static let shared = ShortcutInbox()
  public static let received = Notification.Name("DzzloShortcutReceived")
  private var pending: String?
  public func deliver(_ type: String) { pending = type; NotificationCenter.default.post(name: Self.received, object: type) }
  public func takePending() -> String? { defer { pending = nil }; return pending }
}

// SceneDelegate — cold start, in scene(_:willConnectTo:options:) after startReactNative:
if let item = connectionOptions.shortcutItem { ShortcutInbox.shared.deliver(item.type) }
// SceneDelegate — warm launch, a new method:
func windowScene(_ windowScene: UIWindowScene, performActionFor shortcutItem: UIApplicationShortcutItem,
                 completionHandler: @escaping (Bool) -> Void) {
  ShortcutInbox.shared.deliver(shortcutItem.type); completionHandler(true)
}
```

The adapter (`RCTNativeShortcuts.mm`, Phase 1's shape and imports) returns `takePending()` from `getInitialShortcut`, observes `ShortcutInbox.received` and calls `emitOnShortcut:` (Phase 1's typed-event recipe), and sets `UIApplication.shared.shortcutItems` on the main queue in `setItems`.

**Android.** `ShortcutManagerCompat` (AndroidX core, already in the graph) publishes the items. Each intent targets `MainActivity`, which is already `singleTask` (`AndroidManifest.xml:19`), so a warm launch arrives through `onNewIntent`:

```kotlin
override fun setItems(items: ReadableArray) {
  val ctx = reactApplicationContext
  ShortcutManagerCompat.setDynamicShortcuts(ctx, (0 until items.size()).map { i ->
    val m = items.getMap(i)!!
    ShortcutInfoCompat.Builder(ctx, m.getString("type")!!).setShortLabel(m.getString("title")!!)
      .setIntent(Intent(ctx, MainActivity::class.java).setAction(Intent.ACTION_VIEW).putExtra(EXTRA, m.getString("type")))
      .build()
  })
}
```

`getInitialShortcut` reads — and removes — `EXTRA` from the launch intent; a `BaseActivityEventListener` catches `onNewIntent` and emits `onShortcut`.

**JavaScript** routes through one pure map, with names read from the navigators (`navigation/Dealer/Drawer.js:75-76,86`, `Dealer/TrnTab.js:92,434`, `Dealer/Main.js:203`; `Customer/Drawer.js:75-76`, `Customer/TrnTab.js:91,404`, `Customer/Main.js:205`):

```js
// src/helpers/Shortcuts/routeForShortcut.js — Tier 1
const ROUTES = {
  dealer: { new_order: ['dealerTab', { screen: 'Orders', params: { screen: 'NewSalesOrder' } }],
            today: ['dealer', { screen: 'DailySummary' }], customers: ['dealerCustomer'] },
  customer: { new_order: ['customerTab', { screen: 'Orders', params: { screen: 'NewOrder' } }],
              today: ['customer', { screen: 'DailySummary' }] },
};
export const routeForShortcut = (type, role) => ROUTES[role]?.[type] ?? null;
```

Navigate only once the container is ready (a navigation ref and its `onReady`), never on a timer; once [[08-phase-8-instant-experiences-and-links]] lands, Android shortcuts can carry a link instead of an extra. Tests, red first: the route table (unknown type or role → `null`); the facade (`src/native/shortcuts.js`) navigates once for the initial shortcut and once per event; sign-out calls `setItems([])`; XCTest for `ShortcutInbox` (deliver, then take once); Robolectric for `setItems` and the one-shot extra. Device: long-press the icon on the iOS simulator and the Android AVD — cold and warm, as each role, and signed out.

## 7. App Intents, Siri and Spotlight (iOS)

### 7.1 The types, versioned (Xcode 27 SDK, verified 2026-09-30)

| Type | iOS |
|---|---|
| `AppIntent`, `AppEntity`, `EntityQuery`, `AppShortcutsProvider`, `AppShortcut`, `OpenIntent`, `IntentDialog`, `ProvidesDialog` | 16.0 |
| `IndexedEntity`; `CSSearchableIndex.indexAppEntities(_:priority:)`, `deleteAppEntities(ofType:)`; `ControlConfigurationIntent` | 18.0 |
| `SnippetIntent` (interactive snippets); `supportedModes`, which replaces the deprecated `openAppWhenRun` | 26.0 |
| `LongRunningIntent`, `ExecutionTargets`, App Intents Testing, `IndexedEntityQuery` | 27.0 |

### 7.2 What Siri with Apple Intelligence can do for DZZLO in iOS 27

- **Who has it:** "iPhone 15 Pro and later", launching in English (Australia, Canada, Ireland, **India**, New Zealand, South Africa, UK, US); not in the EU on iPhone at launch, not in China; built with "technologies behind the Gemini AI models" on Private Cloud Compute. More languages from October (French, Japanese, Korean, Portuguese, Spanish — search snippet only). No Hindi.
- **Schemas don't cover us.** The schema domains on 2026-09-29 — Assistant, Audio, Books, Browser, Calendar, Camera, Clock, Files, Journaling, Mail, Maps, Messages, Notes, Phone, Photos, Presentation, Reader, Reminders, Spreadsheet, System and in-app search, Visual intelligence, Whiteboard, Word processor — include nothing for ordering or finance, and no source states whether Siri AI will invoke a custom, non-schema intent from free-form speech (gap). **Don't build for free-form requests.**
- **What works on any iOS 16+ iPhone, no Apple Intelligence needed:** App Shortcut phrases that name the app, plus the Shortcuts app, Spotlight, the Action button and widget/Control buttons. Per Expo's app-intents docs, phrases are compiled, must include `\(.applicationName)`, take at most one non-array parameter, and an app ships at most 10 App Shortcuts.
- **Review, guideline 2.5.11:** handle intents "without the support of an additional app"; aliases "must relate directly to your app or company name and should not be generic terms"; resolve "in the most direct way possible", with no ads in between. Source: https://developer.apple.com/documentation/appintents/app-schema-domains · https://www.macrumors.com/guide/ios-27-siri/

**Where an intent gets its data:** `perform()` runs in the app process launched in the background, or in an extension — and this app starts React Native only when a scene connects (`SceneDelegate` calls `startReactNative`), so a background intent run has no JS _(inference from `AppDelegate.swift`)_. Answers come from the App Group snapshot now, and from the API with a token in a shared Keychain item (`keychain-access-groups`, iOS 3.0) after Phase 9. Intents that should *do* something in the app hand over to JS through the §6 inbox or a Phase 8 link.

### 7.3 Worked example 1 — "What's my outstanding balance in DZZLO?"

```swift
// ios/dzzlo_oms_app/Intents/OutstandingBalanceIntent.swift — in the app target
import AppIntents

@available(iOS 16.0, *)
struct OutstandingBalanceIntent: AppIntent {
  static let title: LocalizedStringResource = "Outstanding balance"
  static let description: IntentDescription? = IntentDescription("Total outstanding across your customers, as of the last sync.")
  static let authenticationPolicy: IntentAuthenticationPolicy = .requiresAuthentication   // money: never on a locked phone
  func perform() async throws -> some IntentResult & ProvidesDialog {
    .result(dialog: IntentDialog(stringLiteral: BalanceAnswer.dialog(for: SummarySnapshot.loadShared())))
  }
}

@available(iOS 16.0, *)
struct DzzloShortcuts: AppShortcutsProvider {
  static var appShortcuts: [AppShortcut] {
    AppShortcut(intent: OutstandingBalanceIntent(),
                phrases: ["What's my outstanding balance in \(.applicationName)", "\(.applicationName) outstanding balance"])
  }
}
```

`BalanceAnswer.dialog(for:)` is the pure part, and its test goes red first: no snapshot → "Open DZZLO once to load your balances."; a snapshot → "₹ 12,80,000.00 across 37 customers, as of 2:05 PM." The amount is the snapshot's own text and the time comes from `writtenAt`, so the answer never pretends to be live; `IntentAuthenticationPolicy` (iOS 16.0) makes Siri ask for an unlock before speaking it. On iOS 26+, a `SnippetIntent` can add an interactive snippet (₹, last payment, "Share statement") later.

### 7.4 Worked example 2 — customers in Spotlight

```swift
@available(iOS 18.0, *)
struct CustomerEntity: AppEntity, IndexedEntity {
  static let typeDisplayRepresentation: TypeDisplayRepresentation = "Customer"
  static let defaultQuery = CustomerQuery()
  let id: String
  let name: String
  var displayRepresentation: DisplayRepresentation { DisplayRepresentation(title: "\(name)") }
}
@available(iOS 18.0, *)
struct CustomerQuery: EntityQuery {
  func entities(for identifiers: [String]) async throws -> [CustomerEntity] {
    CustomerCatalog.loadShared().filter { identifiers.contains($0.id) }     // reads customers.json
  }
}
```

When `SharedStore` writes `customers.json` it calls `try await CSSearchableIndex.default().indexAppEntities(CustomerCatalog.loadShared())`; sign-out calls `deleteAppEntities(ofType: CustomerEntity.self)`. Choosing a result opens the customer through an `OpenIntent` that hands the id to JS. Privacy is a house decision: business names only, dealers only, gone at sign-out.

### 7.5 Watch items, a conflict, and tests

- **`expo-app-intents` 0.0.1 (alpha, Expo SDK 58)** — Swift intent files compiled as Expo inline modules; "You cannot create App Intent types dynamically from JavaScript at runtime"; invocations wait, pending, for JS; iOS 16.4+; a bare app needs `expo`; "will frequently experience breaking changes". Our sources disagree on its publish date (2026-06-08 vs 2026-09-29) and one found no repository metadata — provenance **unverified**. Watch only. `react-native-siri-shortcut` 3.2.4 (2023-12-13) is unmaintained and not New-Arch — avoid.
- **SiriKit — CONFLICTING:** a secondary source says Apple deprecated SiriKit at WWDC26 with a 2–3-year window; Apple's WWDC26 Apple Intelligence guide says no such thing, and the SiriKit docs carried no deprecation flag on 2026-09-29. **Unverified** — either way, build on App Intents.
- **Tests:** XCTest, red first, for `BalanceAnswer.dialog(for:)` (missing, fresh and schema-2 snapshots) and `CustomerCatalog` decoding. The iOS 27 App Intents Testing framework runs "app intents, entities, enums, and query logic out-of-process — the same way Siri or Shortcuts perform them"; Xcode 27 is on this machine, so drive the intent and the query through it on an iOS 27 simulator. Device: the Shortcuts app lists "Outstanding balance"; ask Siri in English (India); search a customer in Spotlight; sign out and repeat — nothing from the old account may leak. Source: https://docs.expo.dev/versions/v58.0.0/sdk/app-intents/ · https://developer.apple.com/documentation/appintentstesting

## 8. Android: App Shortcuts, App Actions and AppFunctions

| Thing | State on 2026-09-29 |
|---|---|
| Google Assistant on phones | removal began 2026-09-04; by 2026-09-28 the Gemini app no longer offers "Switch to Google Assistant" |
| App Actions (built-in intents in `shortcuts.xml`; `actions.xml` deprecated) | the overview still presents them as current — no deprecation notice, no mention of Gemini; whether Gemini honours them is unknown (gap) |
| AppFunctions — `@AppFunction`, `@AppFunctionSerializable`, `AppFunctionService` + `@AppFunctionServiceEntryPoint`, a KSP-generated schema; callers hold `EXECUTE_APP_FUNCTIONS` | platform API 36 plus a Jetpack library the Android 17 launch post calls "currently in alpha"; "As of May 2026, AppFunctions integration with Gemini is in a private preview with trusted testers" |
| Gemini + AppFunctions in the wild | Samsung Gallery on the Galaxy S26 (Feb 2026, One UI 8.5+); a UI-automation preview for food, grocery and rideshare apps on the S26 and select Pixel 10s, US and Korea only |

Source: https://developer.android.com/ai/appfunctions · https://developer.android.com/develop/devices/assistant/overview · https://9to5google.com/2026/09/28/google-assistant-gemini-android/

**Build now.** App Shortcuts are done in §6 (Android 7.0, API 24, gets none — shortcuts start at API 25). Once the https links of [[08-phase-8-instant-experiences-and-links]] exist, publish the order on screen so "ask about this screen" gets structured context — feeding `AssistState` from a one-method setter folded into Phase 8's link module, not a new module:

```kotlin
// MainActivity.kt — onProvideAssistContent is API 23, below minSdk 24
override fun onProvideAssistContent(outContent: AssistContent) {
  super.onProvideAssistContent(outContent)
  AssistState.currentUrl?.let { outContent.webUri = Uri.parse(it) }   // e.g. https://<links-host>/orders/<id>
}
```

**Prepare, behind a flag.** An AppFunction that answers from the same snapshot the widget reads. The library is alpha and shifts between releases, so this is a shape, not compile-ready code:

```kotlin
@AppFunctionSerializable
data class OutstandingBalance(val paise: Long, val text: String, val customers: Int, val asOf: String)

class BalanceFunctions(private val context: Context) {
  @AppFunction
  suspend fun getOutstandingBalance(): OutstandingBalance? {
    val s = SummarySnapshot.read(context.filesDir) ?: return null
    return s.outstanding?.let { OutstandingBalance(it.paise, it.text, it.customers, s.writtenAt) }
  }
}
```

Ship its `AppFunctionService` with `android:enabled="@bool/app_functions_enabled"`, true only in debug builds, until Gemini access opens; exercise it with `adb shell cmd app_function …` on an Android 16 emulator.

**Honest verdict:** an AppFunction reaches only devices on Android 16+ **and** inside Gemini's preview — effectively zero DZZLO users in 2026, and no React Native or Expo library exists. A spike costs 2–3 days, the full job 5–8 _(est.)_: defer it. **Parity:** iOS gets Siri, Shortcuts and Spotlight answers; Android gets App Shortcuts and assist content now, and AppFunctions when Gemini opens up.

## 9. After the Upgrade, the Expo Track, and Exercises

> **After the upgrade to 0.87:** AGP 9 and compileSdk 37 arrive — re-check the Compose compiler plugin and Glance against AGP 9 before merging (not verified). Android 17's widget bitmap cap applies once you *target* 37, a separate decision from compiling against it. The Jest preset moves to `@react-native/jest-preset` (from 0.85); the `NativeSharedStore` and `NativeShortcuts` mocks are unaffected. If the app adopts Swift Package Manager, the `.mm` adapters switch to `<React/…>` framework-style imports.

> **Optional Expo track** (only on an Expo-paired React Native: SDK 56 ↔ 0.85, 57 ↔ 0.86, 58 preview ↔ 0.88): `expo-widgets` (stable since SDK 56, **iOS only**; Android widgets from SDK 58) authors widgets in JSX with `createWidget`, `updateSnapshot` and `updateTimeline`, but widget code "can only use @expo/ui/swift-ui components, with no React hooks, app state, or asynchronous work", its default App Group is `group.<bundle identifier>` (not our `.shared` — pick one owner), and bare apps need "manual native setup … outside CNG workflows". `expo-quick-actions` 6.0.2 replaces `NativeShortcuts`; `expo-app-intents` stays a watch item (§7.5); `@bacons/apple-targets` 5.0.0 (2026-07-17) generates Apple targets as a config plugin, which assumes prebuild _(inference)_.

### Exercises

**9.1 — The snapshot contract.** Write the fixture and its three tests (Jest golden, XCTest decode, JUnit parse), then rename one field; add the `shouldWriteSnapshot` test the same way, then show on a device that choosing "Last 7 days" leaves the widget alone. Deliverable: the red outputs, then the green ones.

**9.2 — The iOS widget on three surfaces.** Home Screen small and medium, Lock Screen rectangular; light, dark and tinted; en and hi. Deliverable: six screenshots and the `SummarySnapshotTests` report.

**9.3 — Glance, resized.** Add `DailySummaryWidget` on the Android 16 AVD; resize small ↔ medium; toggle dark mode and Hindi at font scale 1 and 2; sign out. Deliverable: screenshots and the JUnit report.

**9.4 — Quick actions, cold and warm.** On both platforms, as both roles: long-press, launch cold, launch warm, sign out. Record where each lands in a table.

**9.5 — Ask Siri, then check Spotlight.** Run "Outstanding balance" from the Shortcuts app, then by voice in English (India) on a device; find an indexed customer in Spotlight. Sign out and repeat both — the answer must be "Open DZZLO once…" and the customer must be gone.

**9.6 — AppFunction spike (optional).** Build the debug-only service on an Android 16 emulator, call it with `adb shell cmd app_function`, and record its output next to the widget's figure — they must match.

## Lab Notes

2026-09-29/30 — read-only verification; nothing was built, installed or committed:

- Xcode 27 SDK (`iPhoneOS27.0.sdk`): availability for every Apple type in this phase, and `AppIntent`'s requirement types (`description` is `IntentDescription?`) — including `IndexedEntityQuery` (27.0), `CSSearchableIndex.indexAppEntities` / `deleteAppEntities` (18.0), `Button(intent:)` (17.0) and `WidgetBundleBuilder.buildLimitedAvailability` (16.1), which is what makes `if #available` legal in the bundle.
- Android SDK `api-versions.xml`: `TileService` 24, `ShortcutManager` 25, `requestPinShortcut` 26, `requestAddTileService` 33, `onProvideAssistContent` 23, `AtomicFile` 17, `EXECUTE_APP_FUNCTIONS` and `AppFunctionManager` 36. `xcrun simctl get_app_container` accepts an App Group identifier.

**Next:** [[07-phase-7-maps-and-location]] — whether DZZLO needs maps at all, and what tanker tracking would cost.
