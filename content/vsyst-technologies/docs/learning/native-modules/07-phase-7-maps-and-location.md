# Phase 7 — Maps and Location: Only If a Tanker Needs Finding

> Level: Intermediate | Time: ~60 min | Outcome: you can show, with evidence, why DZZLO ships no map and no location permission today, ship the one cheap thing worth shipping (an address link into the maps apps), and price — in money, review risk and battery — a map screen or live tanker tracking if the product ever asks for one.

---

## 1. The One Idea

A map is the most tempting native feature in a fuel-delivery business and the one most likely to cost more than it returns. Before any code, ask one question of every idea: **what does the person decide by looking at it?**

| Idea | Who looks | What they decide | Cheapest thing that answers it |
| --- | --- | --- | --- |
| "Where is this customer's site?" | Tanker driver, dealer staff | Which way to drive | A link that opens Google Maps / Apple Maps on the address — no SDK, no permission |
| "When will my diesel arrive?" | Credit customer | Wait, call, or re-plan | A status + ETA line pushed by the server ([[05-phase-5-notifications-and-live-status]]) — not a moving dot |
| "Where are my customers' sites?" | Dealer owner | Route planning, credit visits | A map screen — once someone asks for it |
| "Where is the tanker right now?" | Customer, dealer | Little that the ETA doesn't already tell them | Live tracking — the most expensive item in this course |

What the evidence says (ecosystem and product research, 2026-09-29):

- **Oil-company dealer apps ship navigation, not maps.** IndianOil For Business gives its delivery person "Call customer or navigate to his address directly from app". Doorstep-diesel apps such as Repos advertise "GPS-based fueling locations" — tracking is *their* product, not DZZLO's.
- **The value ranking** puts "navigate to the delivery address now; live tanker tracking and ETA later" at **rank 10 of 15**. The cost grid prices the two halves very differently: a navigation deep link is **T0, under a day**; live GPS tracking with a map ETA is **T3 + policy + backend, 4–8 weeks** _(est.)_, wave "later".
- **Live GPS tracking is on the explicit defer list**, alongside Siri/Gemini, App Clips and OCR: "evidence among Indian SMB and fuel users is weak, and the cost and policy burden is high".
- In the wider RN world (State of React Native 2025, 3,501 responses) 47.37 % use location and 41.04 % use maps. That keeps the libraries healthy; it doesn't make DZZLO need them.

And the app on 2026-09-29 has **no location code at all**: no geolocation package installed or imported, no location permission in the merged Android release manifest, and three iOS location purpose strings that exist only because OneSignal's Location module is linked (§3). The customer role does have `Vehicles`, `VehicleRequests` and `VehicleReports` routes, so vehicles and drivers are modelled — but nothing reads a position.

**Verdict**

- **Build now:** the address link (Exercise 5.1). Pure JS, both platforms, under a day.
- **Build when a screen needs it:** a map of customer sites with `react-native-maps` (§2) — Apple Maps on iOS (no key), Google on Android (a key, free map loads).
- **Don't build:** live tanker tracking. If it ever comes, it is its own future phase with a driver-side flow, and the customer sees it as a Live Activity / Live Update, not a map (§4).

Parity holds throughout: every recommendation here ships on iOS and Android together.

## 2. If You Show a Map

### The libraries (npm + React Native Directory, 2026-09-29)

| Library | Version (date) | Architecture | Weekly downloads | Verdict |
| --- | --- | --- | --- | --- |
| `react-native-maps` | 1.29.11 (2026-09-27) | TurboModule; Directory New-Arch ✅; README: Fabric from 1.26.1 on RN ≥ 0.81.1 | 1,305,122 | **USE** when a map screen is approved |
| `@maplibre/maplibre-react-native` | 11.4.0 (2026-09-19) | TurboModule | 184,149 | Alternative: open-source renderer, your own tiles |
| `@rnmapbox/maps` | 10.3.5 (2026-07-22) | TurboModule | 257,311 | Alternative on Mapbox's commercial terms |
| `mappls-map-react-native` (MapmyIndia) | 2.0.x | not in the Directory; New-Arch status unknown | — | India-specific data; the older MapmyIndia RN repos are marked deprecated |
| `expo-maps` | 57.0.3 | Expo module, **alpha**; needs `expo` | 141,042 | Not on RN 0.84 — no Expo SDK pairs with it |

### Which map on which platform

- **iOS — Apple Maps, the default.** react-native-maps says it "works out-of-the-box": no key, no quota for showing a map. Underneath is MapKit: SwiftUI `Map` (iOS 14), `MKMapItemDetailViewController` place cards (iOS 18), and in iOS 26 `MKAddress` / `MKReverseGeocodingRequest`, while `CLGeocoder` is now deprecated ("Use MapKit").
- **iOS — Google, optional.** `pod 'react-native-maps/Google'`, a key passed through `GMSServices.provideAPIKey`, iOS ≥ 14. Worth it only if both platforms must look identical. They don't.
- **Android — Maps SDK for Android 20.0.0** (31 Jan 2026, minSdk 21). v19 deprecated the LEGACY renderer; v20 removed `org.apache.http.legacy`, so an app still on the legacy renderer crashes unless it declares that library itself. It needs an API key and a billing account, even though map loads are free.

### Keys, restriction and the 2025 price change

The Google key is a billing credential. Restrict it to the app's signature (package `in.vsyst.dzzlooms` plus the signing certificate) and keep its value out of git — the same move [[09-phase-9-security-privacy-and-release]] §6 makes for the upload-key passwords in `android/gradle.properties`.

Google Maps Platform changed its pricing on **1 March 2025**: the \$200 monthly credit was replaced by **per-SKU free caps** — 10,000 free events a month for Essentials SKUs, 5,000 for Pro, 1,000 for Enterprise. The mobile **"Maps SDK" (map loads on Android and iOS) is listed as unlimited.** Paid rates at the 100k–500k tier: Dynamic Maps \$7 per 1,000 (the researcher reads this as the web map-load SKU, since the mobile SDK is listed separately), Geocoding \$5, Autocomplete \$2.83. India has its own price list; a third-party summary says India-billed accounts with mostly Indian usage get **70k / 35k / 7k free events — seven times the global caps — and pay in INR. That is a third-party claim: confirm it on Google's India pricing page before budgeting on it.**
Source: https://developers.google.com/maps/billing-and-pricing/pricing

The lesson: pins are free on both platforms; **geocoding addresses is where the money goes.** Geocode each site once, server-side, and store the coordinates. Apple's Maps Server API does server-side geocoding, search and ETA with "up to 25,000 service calls per day per team" shared with MapKit JS (HTTP 429 beyond), authenticated with a JWT.

### Steps, when a map screen is approved

1. **Jest red first.** The screen's decisions — which customers get a pin, what the empty state says, what a tap opens — are Tier 3 tests against the mocked map (step 5).
2. Install: `yarn add react-native-maps`, then `cd ios && bundle exec pod install`.
3. Android key: a `<meta-data>` entry in `android/app/src/main/AndroidManifest.xml` whose value is injected from a Gradle property kept outside the repo. The entry's name, `com.google.android.geo.API_KEY`, comes from the Maps SDK docs rather than this course's research — confirm it when you build.
4. iOS: nothing to do, because Apple Maps needs no key.
5. A global mock in `jest.setup.js` — an unmocked native module throws under Jest ([[01-phase-1-foundations]]):

```js
// jest.setup.js — mirror only the exports your screens import
jest.mock('react-native-maps', () => {
  const React = require('react');
  const { View } = require('react-native');
  const MapView = props => React.createElement(View, { testID: 'map', ...props });
  return { __esModule: true, default: MapView, Marker: View };
});
```

6. Device check: pins render on the iOS simulator and the Fold AVD at 320 dp × fontScale 1, in en and hi; pin and callout colours come from `src/theme` tokens.
7. Release: re-run the 16 KB alignment check, because a map SDK brings its own `.so` files ([[09-phase-9-security-privacy-and-release]] §7).

> **After the upgrade to 0.87:** re-check react-native-maps on the React Native Directory before bumping. Its README promises Fabric support "on RN ≥ 0.81.1" and says nothing about 0.87 specifically.

## 3. Location

### The permission tiers

| Tier | iOS | Android |
| --- | --- | --- |
| While the app is in use | `NSLocationWhenInUseUsageDescription` + a When-In-Use request | `ACCESS_COARSE_LOCATION` (about 3 km²) and/or `ACCESS_FINE_LOCATION` (about 50 m) |
| Precise vs approximate | the person can switch Precise off (iOS 14+; not re-verified in this course's research) | a person who grants only approximate gets only approximate |
| Always / background | `NSLocationAlwaysAndWhenInUseUsageDescription` + the Location updates background mode | `ACCESS_BACKGROUND_LOCATION` (API 29+) + a Play Console declaration |
| One tap, precise, this session only | — | the Android 17 location button (below) |

Play's background-location policy allows it **only when it is core functionality**, and asks for the Permissions Declaration Form, a video (aim for 30 s or less) showing the feature, the disclosure and the runtime prompt, and a **prominent in-app disclosure before the prompt** that uses the word "location" plus a background phrase such as "when the app is closed". Google evaluates one feature at a time.
Source: https://support.google.com/googleplay/android-developer/answer/9799150

### The three strings you already have

```
ios/dzzlo_oms_app/Info.plist:49-54
  NSLocationAlwaysAndWhenInUseUsageDescription
  NSLocationAlwaysUsageDescription
  NSLocationWhenInUseUsageDescription
  → all three: "$(PRODUCT_NAME) needs Location access for good user experience!"
```

They are not dead weight. `react-native-onesignal` pulls the full `OneSignalXCFramework`, including `OneSignalLocation.framework`, whose binary references `requestAlwaysAuthorization` and `requestWhenInUseAuthorization`. That trips App Store Connect's **ITMS-90683** "missing purpose string" check even though the app never asks for location; the strings went in on 2021-03-15 for exactly that reason. The fault is the wording, which fails guideline **5.1.1(ii)** ("Ensure your purpose strings clearly and completely describe your use of the data"), and [[02-phase-2-dependency-diet]] replaces it with text that tells the truth. Two rules follow:

- A config-pin test keeps all three keys present while `OneSignalLocation` is linked (Exercise 5.2), so no tidy-up can trigger ITMS-90683. `NSLocationAlwaysUsageDescription` only matters on very old iOS versions — test against the ITMS check before removing any key.
- The day a real location feature ships, the strings change again to name it: "DZZLO uses your location while a delivery is in progress, so your customer can see when the tanker will arrive." The repo checklist's proposed "delivery checkpoints" wording (`docs/todos/PRODUCTION_RELEASE_CHECKLIST.md`, item 6) would describe a feature that doesn't exist — a review risk of its own.

Android has **no** location permission in the merged release manifest; OneSignal's Android location module isn't pulled. Adding `ACCESS_*_LOCATION` is a deliberate act that brings a Data safety row ("Approximate/Precise location").

### The APIs

| Platform | API | Since | Role |
| --- | --- | --- | --- |
| iOS | `CLLocationManager` | long before the 15.1 floor | delegate API; the fallback everywhere |
| iOS | `CLLocationUpdate` (async live updates) | iOS 17 | the modern stream — gate with `if #available(iOS 17, *)` |
| iOS | `CLMonitor` (condition monitoring) | iOS 17 | geofences |
| iOS | `CLBackgroundActivitySession` | iOS 17 | keeps the app "in use" in the background, with a visible indicator |
| iOS | `CLServiceSession` | iOS 18 | session-scoped authorisation |
| Android | Fused Location Provider | Google Play services | a single fix or a stream |
| Android | location button | Android 17 (API 37) | precise location for the current session only |

The iOS deployment target is 15.1, so every iOS 17 API above needs its `CLLocationManager` fallback. minSdk 24 is no problem for the Fused provider, which comes from Play services.

**Library situation.** `@react-native-community/geolocation` 3.4.0 (2024-09-01) and `react-native-geolocation-service` 5.3.1 (2022) are flagged unmaintained, and `expo-location` 57.0.20 needs `expo`, which no SDK lets you install on RN 0.84. The ecosystem verdict for "location at capture time" is **WRAP**: a thin in-house Turbo Module in the Phase 1 pattern (`specs/NativeX.ts`, a facade in `src/native/`, Swift behind an Objective-C++ adapter, Kotlin + `BaseReactPackage`). Nothing gets named or built until a feature asks for it.

### The Android 17 location button — a policy from 27 January 2027

Android 17 adds a system location button that grants precise location for the current session only. From **27 Jan 2027**, apps targeting API 37+ whose precise-location need is "only for one-time, user-initiated actions" **must** use it (through the `onlyForLocationButton` permission flag); `ACCESS_FINE_LOCATION` stays only for features the button or COARSE can't serve. A "tag this outlet's GPS" button would be exactly that case.
Source: https://support.google.com/googleplay/android-developer/answer/16909972

### Geofencing ("the tanker has arrived")

| | iOS | Android |
| --- | --- | --- |
| Limit | 20 monitored conditions per app | 100 geofences per app per device user |
| Permission | Always (background) | FINE + BACKGROUND on Android 10+ |
| Behaviour | relaunches a terminated app when a condition changes; works only after the first unlock after a reboot | 100–150 m radius recommended; latency usually under 2 min, 2–6 min under background limits; re-register after a reboot or data clear; needs Play services |

Geofencing **forces background location on both platforms.** Skip it unless "arrived at outlet" becomes core.

## 4. Tanker Live Tracking, If Ever

This is a **future phase**, written down so the decision is made with open eyes. Nothing here is recommended for the current releases. DZZLO has no driver role today — the two role trees are Dealer and Customer — so tracking begins with a product decision about who carries the phone.

### The architecture: a server ETA, not a live map

```
driver's phone ── location FGS (Android) / background session (iOS) ──▶ DZZLO API
                                                                          │ ETA computed on the server
                     ┌────────────────────────────────────────────────────┴──────────────┐
                     ▼                                                                   ▼
     iOS Live Activity via APNs                                   Android Live Update / ongoing notification
     "Out for delivery · ETA 25 min"                              ProgressStyle segments, chip "ETA 25m"
```

Why not a map on the customer's phone? A Live Activity "can't access the network or receive location updates", so the ETA has to be worked out on the server and pushed. And Android's Live Update rules list "active food delivery tracking" as appropriate and **"package tracking" as not**: run it only while the tanker is actually moving and end it at delivery — an order that waits for days is package tracking. The surfaces themselves are built in [[05-phase-5-notifications-and-live-status]].

### Android: a foreground service of type `location`

For apps targeting Android 14+, every foreground service declares a type plus a matching permission. For `location` that means `FOREGROUND_SERVICE_LOCATION` and a granted COARSE or FINE permission — and the service **can't start from the background without `ACCESS_BACKGROUND_LOCATION`**. Start it from the visible "Start delivery" screen and the background permission, with its declaration form, stays out of the app.

```xml
<!-- android/app/src/main/AndroidManifest.xml — future sketch -->
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<application>
  <service
      android:name=".tracking.TankerTrackingService"
      android:exported="false"
      android:foregroundServiceType="location" />
</application>
```

```kotlin
// android/app/src/main/java/in/vsyst/dzzlooms/tracking/TankerTrackingService.kt — future sketch
class TankerTrackingService : Service() {
  override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    // 1. Build the ongoing notification first (Phase 5's channel, a "Stop delivery" action).
    // 2. Promote to foreground with the location type, e.g. androidx.core's
    //    ServiceCompat.startForeground(this, NOTIFICATION_ID, notification,
    //        ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION) — confirm against the FGS docs when building.
    // 3. Ask the Fused Location Provider for updates; batch fixes and POST them to the API with retries.
    return START_NOT_STICKY
  }

  override fun onBind(intent: Intent?): IBinder? = null
}
```

The logic — batching, retry, "is this fix stale?" — lives in a plain Kotlin class with JUnit + Robolectric tests; the service stays a thin shell, which is the Phase 1 rule for keeping device-only code small.

Play: apps targeting Android 14+ declare every foreground-service type in Play Console (App content) with a description, the user impact if it were deferred, **a video link** and a use case. One more warning: the summary of Play's background-location policy phrased its delivery example as "for riders, not drivers" — re-read the live policy before relying on it for a tanker driver.

### iOS: the background location mode

Add `location` to `UIBackgroundModes` (today it holds only `remote-notification`, `Info.plist:80-83`), start a `CLBackgroundActivitySession` (iOS 17) while in the foreground and recreate it after a background relaunch; below iOS 17, fall back to `CLLocationManager` background updates. Apple's own guidance: "Consider carefully whether your app really needs background location updates."

Review will read the feature against **2.5.4** ("Apps may only use background services for their intended purposes: VoIP, audio playback, location, …"), **5.1.5** ("Use Location Services in your app only when it is directly relevant to the features and services provided by the app … notify and obtain consent") and **5.1.1(ii)** purpose strings. Justify it in the review notes, with a demo account that can start a delivery.

### Build or buy

| Route | Effort | Notes |
| --- | --- | --- |
| In-house: Kotlin FGS + Swift session, Phase 1 module pattern | Android 6–10 days; iOS within 15–30 days for tracking + geofence, server included _(est.)_ | full control; you own every battery bug |
| `react-native-background-geolocation` 5.7.0 (2026-09-27, TurboModule, Transistorsoft) | 2–3 days to integrate _(est.)_, plus the licence | the Android research found a **$399 licence (iOS + Android) is needed for Android release builds**; the ecosystem research did not check the terms — read them before deciding |

The whole feature on both platforms: **4–8 weeks** _(est.)_ — T3, plus policy work and a backend — with a high running cost in review, battery complaints and support.

### Battery and OEM killers

India's top brands are among the most aggressive process killers on dontkillmyapp: Xiaomi, OnePlus and Samsung 5/5; Oppo 4/5; Vivo, realme and Tecno 3/5. Android 17 adds RAM-based memory limits whose offenders are "abruptly terminated". A driver's tracking service **will** die on some phones, so the server must treat silence as "position unknown", never as "arrived". Play prohibits asking this kind of app for a battery-optimisation exemption: open `ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS` next to an OEM-specific guide, never `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`.

## 5. Exercises

**5.1 — Address → maps apps (the one thing to ship).** Red test first, then the helper, then a device run.

```js
// src/helpers/Links/__tests__/maps.test.js — red first
import { mapsUrlFor } from '../maps';

test('iOS opens Apple Maps, Android opens Google Maps, both URL-encoded', () => {
  expect(mapsUrlFor('Plot 4, MIDC, Pune 411019', 'ios'))
    .toBe('https://maps.apple.com/?q=Plot%204%2C%20MIDC%2C%20Pune%20411019');
  expect(mapsUrlFor('शर्मा रोडवेज़, पुणे', 'android'))
    .toMatch(/^https:\/\/www\.google\.com\/maps\/search\/\?api=1&query=%E0%A4/);
});

test('no address, no link — the button hides', () => {
  expect(mapsUrlFor('   ', 'ios')).toBeNull();
  expect(mapsUrlFor(undefined, 'android')).toBeNull();
});
```

```js
// src/helpers/Links/maps.js — green
const APPLE = 'https://maps.apple.com/?q=';
const GOOGLE = 'https://www.google.com/maps/search/?api=1&query=';

export const mapsUrlFor = (address, os) => {
  const q = typeof address === 'string' ? address.trim() : '';
  if (!q) return null;
  return (os === 'ios' ? APPLE : GOOGLE) + encodeURIComponent(q);
};
```

The two URL formats come from Google's "Maps URLs" and Apple's Map Links pages, which this course's research did not capture — confirm both before shipping; the test pins whatever you confirm. The button calls `Linking.openURL(url)` and catches the rejection. Don't gate it on `Linking.canOpenURL`, which resolves `false` on Android 11+ without a `<queries>` entry (RN's docs say it may reject; see [[02-phase-2-dependency-diet]]). **Produces:** a green test, then a device observation — Apple Maps opens on the iOS simulator; Google Maps (or the browser) opens on the AVD, at 320 dp × fontScale 1.

**5.2 — The permission-string review.** Pin the location strings with a config test in the house `*.config.test.js` style (like `src/utils/__tests__/firebaseModules.config.test.js`):

```js
// src/utils/__tests__/locationStrings.config.test.js
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '../../..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');
const KEYS = [
  'NSLocationWhenInUseUsageDescription',
  'NSLocationAlwaysAndWhenInUseUsageDescription',
  'NSLocationAlwaysUsageDescription',
];

test('the location strings stay while OneSignalLocation is linked, and say something true', () => {
  const plist = read('ios/dzzlo_oms_app/Info.plist'); // booleans only: a failing toMatch would print the file
  if (read('ios/Podfile.lock').includes('OneSignalLocation')) {
    expect(KEYS.filter(key => !plist.includes(`<key>${key}</key>`))).toEqual([]); // names a missing key, nothing else
  }
  expect(plist.includes('good user experience')).toBe(false);
});

test('Android asks for no location permission', () => {
  const manifest = read('android/app/src/main/AndroidManifest.xml');
  expect(manifest).not.toMatch(/ACCESS_(FINE|COARSE|BACKGROUND)_LOCATION/);
});
```

**Produces:** a red run today (the wording still says "good user experience"), and a green run once Phase 2's truthful text lands. Record both.

**5.3 — Price the map before anyone asks.** A dealer with 300 credit customers opens a map screen 20 times a day. Count the monthly geocoding events if the app geocodes on every open (300 × 20 × 30 = 180,000) against geocoding each site once on the server (300, once). Look up which free cap the Geocoding SKU gets on the pricing page, and write the bill both ways in the vault. **Produces:** a one-paragraph cost note the product decision can cite.

---

**Next:** [[08-phase-8-instant-experiences-and-links]] — links that open the right screen, and the customer who never installs the app.
