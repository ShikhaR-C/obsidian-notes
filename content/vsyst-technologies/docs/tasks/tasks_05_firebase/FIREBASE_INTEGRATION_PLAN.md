# Plan: Re-add Firebase — Crashlytics, Analytics, Performance Monitoring & Remote Config. DONE ✅

## Context

The app (`in.vsyst.dzzlooms`) previously had Firebase for phone auth (removed). The Firebase project `dzzlo-oms` config files are still present on both platforms, but all Firebase code/plugins are commented out and no `@react-native-firebase/*` packages are installed. The app runs **React Native 0.84.1** / **React 19.2.3**.

> **Note on paths:** The RN app lives under `dzzlo_oms_app/`. All `src/*`, `index.js`, `App.js`, `android/*`, `ios/*` references below are relative to that directory.
>
> **Networking:** `axios` has been removed. All HTTP is done via **RTK Query** (`@reduxjs/toolkit/query/react`) configured in `dzzlo_oms_app/src/store/apis/createApi.js` using `fetchBaseQuery` + `retry`. HTTP performance instrumentation must therefore hook into RTK Query (see Step 7).

---

## Current State

- `android/app/google-services.json` — **present**, project `dzzlo-oms`
- `ios/GoogleService-Info.plist` — **present**, project `dzzlo-oms`
- `ios/dzzlo_oms_app/AppDelegate.swift` — Firebase import & `FirebaseApp.configure()` **commented out** (lines 5, 33)
- `android/app/build.gradle` — `apply plugin: 'com.google.gms.google-services'` **commented out** (line 5)
- `android/build.gradle` — `classpath("com.google.gms:google-services:4.4.3")` **commented out** (line 19)
- `ios/Podfile` — `$RNFirebaseAsStaticFramework = true` **commented out** (line 21)
- `package.json` — **no** `@react-native-firebase/*` packages

---

## Step-by-step Implementation

### Step 1 — Install npm packages

```bash
yarn add @react-native-firebase/app @react-native-firebase/crashlytics @react-native-firebase/analytics @react-native-firebase/perf @react-native-firebase/remote-config
```

### Step 2 — Android: Enable Google Services & Firebase plugins

- **`android/build.gradle`** (line 19): Uncomment `classpath("com.google.gms:google-services:4.4.3")`
- **`android/build.gradle`**: Add Crashlytics & Perf classpaths:
  ```groovy
  classpath("com.google.firebase:firebase-crashlytics-gradle:3.0.3")
  classpath("com.google.firebase:perf-plugin:1.4.2")
  ```
- **`android/app/build.gradle`** (line 5): Uncomment `apply plugin: 'com.google.gms.google-services'`
- **`android/app/build.gradle`**: Add Crashlytics & Perf plugins:
  ```groovy
  apply plugin: 'com.google.firebase.crashlytics'
  apply plugin: 'com.google.firebase.firebase-perf'
  ```

### Step 3 — iOS: Enable Firebase in Podfile & AppDelegate

- **`ios/Podfile`** (line 21): Uncomment `$RNFirebaseAsStaticFramework = true`
- **`ios/dzzlo_oms_app/AppDelegate.swift`** (line 5): Uncomment `import Firebase`
- **`ios/dzzlo_oms_app/AppDelegate.swift`** (line 33): Uncomment `FirebaseApp.configure()`
- Run `cd ios && pod install`

### Step 4 — Create Firebase utility module

Create `src/utils/firebase.js` with helpers for all 4 services:

```js
import analytics from "@react-native-firebase/analytics";
import crashlytics from "@react-native-firebase/crashlytics";
import perf from "@react-native-firebase/perf";
import remoteConfig from "@react-native-firebase/remote-config";

// ── Analytics ──
export const logEvent = async (name, params) => {
  await analytics().logEvent(name, params);
};

export const logScreenView = async (screenName, screenClass) => {
  await analytics().logScreenView({
    screen_name: screenName,
    screen_class: screenClass,
  });
};

// ── Crashlytics ──
export const setUser = async (userId) => {
  await crashlytics().setUserId(userId);
  await analytics().setUserId(userId);
};

export const logError = (error) => {
  crashlytics().recordError(error);
};

// ── Performance Monitoring ──
export const startHttpMetric = async (url, method) => {
  const metric = await perf().newHttpMetric(url, method);
  await metric.start();
  return metric; // caller calls metric.setHttpResponseCode(200) then metric.stop()
};

export const startTrace = async (traceName) => {
  const trace = await perf().startTrace(traceName);
  return trace; // caller calls trace.stop() when done
};

// ── Remote Config ──
export const initRemoteConfig = async (defaults = {}) => {
  await remoteConfig().setDefaults(defaults);
  await remoteConfig().setConfigSettings({
    minimumFetchIntervalMillis: __DEV__ ? 0 : 3600000,
  });
  await remoteConfig().fetchAndActivate();
};

export const getRemoteValue = (key) => {
  return remoteConfig().getValue(key);
};
```

### Step 5 — Initialize Firebase services in app entry

In `index.js` or `App.js`:

```js
import crashlytics from "@react-native-firebase/crashlytics";
import perf from "@react-native-firebase/perf";
import { initRemoteConfig } from "./src/utils/firebase";

// Enable crash collection
crashlytics().setCrashlyticsCollectionEnabled(true);

// Performance monitoring auto-collects app startup, HTTP metrics, and screen traces
// No extra setup needed — it works out of the box

// Initialize Remote Config with defaults
initRemoteConfig({
  // Define your default values here, e.g.:
  // feature_new_orders: false,
  // maintenance_mode: false,
});
```

### Step 6 — Add screen tracking for Analytics

This app has **no single `NavigationContainer`** — navigation is split across role-based navigators: `src/navigation/Customer/Drawer.js`, `src/navigation/Dealer/Drawer.js`, and `src/navigation/Auth/`. Each of these contains its own `NavigationContainer`.

Add an `onStateChange` (or `onReady` + `onStateChange`) handler in **each** role navigator that owns a `NavigationContainer`:

```js
import { useRef } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import analytics from '@react-native-firebase/analytics';

const routeNameRef = useRef();

<NavigationContainer
  onReady={() => {
    routeNameRef.current = navigationRef.current?.getCurrentRoute()?.name;
  }}
  onStateChange={async () => {
    const prev = routeNameRef.current;
    const current = navigationRef.current?.getCurrentRoute()?.name;
    if (prev !== current) {
      await analytics().logScreenView({
        screen_name: current,
        screen_class: current,
      });
    }
    routeNameRef.current = current;
  }}
>
```

> Alternative: extract this into a small wrapper component (e.g. `src/navigation/withAnalytics.js`) and use it in Customer/Dealer/Auth navigators to avoid duplication.

### Step 7 — Instrument RTK Query calls with Performance Monitoring (optional)

Since `axios` is gone and **all** HTTP goes through RTK Query, the right place for custom HTTP metrics is `dzzlo_oms_app/src/store/apis/createApi.js` — specifically by wrapping `rawBaseQuery` in a perf-monitoring baseQuery that sits **inside** `retry` (so we measure each attempt, not the whole retry loop).

Current layering in `createApi.js`:

```
fetchBaseQuery  →  rawBaseQuery  →  baseQueryWithSmartRetry (retry wrapper)  →  createApi
```

Add a new wrapper between `rawBaseQuery` and the `retry` wrapper:

```js
// dzzlo_oms_app/src/store/apis/createApi.js
import perf from "@react-native-firebase/perf";

const baseQueryWithPerf = async (args, api, extraOptions) => {
  const url = typeof args === "string" ? args : args.url;
  const method = (typeof args === "object" && args.method) || "GET";
  // Resolve absolute URL for the metric label (perf requires full URL)
  const fullUrl = url.startsWith("http") ? url : `${API_URL_V}${url}`;

  const metric = await perf().newHttpMetric(fullUrl, method);
  await metric.start();
  try {
    const result = await rawBaseQuery(args, api, extraOptions);
    const status =
      result.error?.status && typeof result.error.status === "number"
        ? result.error.status
        : (result.meta?.response?.status ?? 0);
    metric.setHttpResponseCode(status);
    const contentType =
      result.meta?.response?.headers?.get?.("content-type") || "";
    if (contentType) metric.setResponseContentType(contentType);
    return result;
  } finally {
    await metric.stop();
  }
};

const baseQueryWithSmartRetry = retry(
  async (args, api, extraOptions) => {
    const result = await baseQueryWithPerf(args, api, extraOptions); // was rawBaseQuery
    if (result.error?.status >= 400 && result.error?.status < 500) {
      retry.fail(result.error);
    }
    return result;
  },
  {
    /* …unchanged… */
  },
);
```

**Where else monitoring hooks go in RTK Query:**

| Concern                                                             | Where to add it                                                                                                                      |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| HTTP latency / status / content-type (Perf)                         | Custom baseQuery wrapping `rawBaseQuery` (above) — also the existing `responseHandler` "Future seam" comment in `createApi.js:37-44` |
| Non-2xx / rejected-action logging (Crashlytics)                     | `rtkQueryErrorLogger.js` — add `crashlytics().recordError(...)` on `isRejectedWithValue(action)` (currently only handles 401 logout) |
| **Endpoint-level traces (per-endpoint latency, outcome analytics)** | **A single Redux middleware** — see below. `onQueryStarted` per-endpoint is NOT required.                                            |

#### Endpoint-level monitoring: middleware vs `onQueryStarted`

**Use a middleware.** RTK Query dispatches lifecycle actions for every endpoint — `pending`, `fulfilled`, `rejected` — each carrying `action.meta.arg.endpointName`, `action.meta.requestId`, `action.meta.requestStatus`, and `action.meta.startedTimeStamp`. One middleware covers **every** endpoint without touching endpoint definitions.

Example `dzzlo_oms_app/src/store/middleware/rtkQueryPerfLogger.js`:

```js
import { isPending, isFulfilled, isRejectedWithValue } from "@reduxjs/toolkit";
import perf from "@react-native-firebase/perf";
import analytics from "@react-native-firebase/analytics";
import crashlytics from "@react-native-firebase/crashlytics";
import { api } from "../apis/createApi";

const traces = new Map(); // requestId -> Firebase trace

const isApi = (action) =>
  action.meta?.arg?.endpointName != null &&
  (action.type.startsWith(`${api.reducerPath}/executeQuery`) ||
    action.type.startsWith(`${api.reducerPath}/executeMutation`));

export const rtkQueryPerfLogger = () => (next) => async (action) => {
  if (isApi(action)) {
    const { endpointName, requestId } = action.meta.arg;

    if (isPending(action)) {
      const trace = await perf().startTrace(`rtkq_${endpointName}`);
      traces.set(action.meta.requestId, trace);
    } else if (isFulfilled(action) || isRejectedWithValue(action)) {
      const trace = traces.get(action.meta.requestId);
      if (trace) {
        trace.putAttribute("endpoint", endpointName);
        trace.putAttribute("outcome", isFulfilled(action) ? "ok" : "err");
        await trace.stop();
        traces.delete(action.meta.requestId);
      }
      if (isRejectedWithValue(action)) {
        crashlytics().recordError(
          new Error(`RTKQ ${endpointName} failed: ${action.payload?.status}`),
        );
      }
      await analytics().logEvent("api_call", {
        endpoint: endpointName,
        status: isFulfilled(action) ? "ok" : "err",
      });
    }
  }
  return next(action);
};
```

Register it next to the existing logger in the store config (wherever `configureStore({ middleware: … })` lives).

**When to still use `onQueryStarted`** (narrow cases):

- You need the **unwrapped response body** to derive a custom trace attribute (middleware sees the serialized Redux payload, which is usually fine, but some transforms happen only in `transformResponse`).
- You want to instrument something that is **not** an HTTP round-trip — e.g. a multi-step flow that chains queries together, or a cache-update side-effect that should be part of the trace.
- You want a trace to span additional local work (optimistic UI, file I/O) before/after the network call for that **specific** endpoint.

For everything else — per-endpoint latency, success/failure counts, error logging, analytics events — the middleware above is the right call.

> **Note:** Firebase Performance Monitoring **auto-instruments** `fetch`/`XHR` on both platforms, so out-of-the-box you already get per-URL HTTP traces. The baseQuery wrapper adds custom **HTTP attributes**; the middleware adds per-**endpoint** (logical) traces keyed by RTK Query endpoint name rather than URL.

### Step 8 — Verify config files are still valid

- Confirm `google-services.json` project ID matches your Firebase console
- Confirm `GoogleService-Info.plist` bundle ID matches `in.vsyst.dzzlooms`
- If credentials have been rotated since last use, re-download from Firebase console

### Step 9 — Build & Test

- Clean build both platforms:
  ```bash
  cd android && ./gradlew clean && cd ..
  cd ios && pod install && cd ..
  ```
- Run on device/simulator and verify:
  - Firebase console shows the app as connected
  - Crashlytics dashboard receives a test crash (`crashlytics().crash()`)
  - Analytics dashboard shows events

---

## Files to Modify

| File                                                        | Change                                                                                                                |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `package.json`                                              | Add 5 Firebase packages (app, crashlytics, analytics, perf, remote-config)                                            |
| `android/build.gradle`                                      | Uncomment google-services classpath + add crashlytics classpath + add perf classpath                                  |
| `android/app/build.gradle`                                  | Uncomment google-services plugin + add crashlytics plugin + add perf plugin                                           |
| `ios/Podfile`                                               | Uncomment `$RNFirebaseAsStaticFramework`                                                                              |
| `ios/dzzlo_oms_app/AppDelegate.swift`                       | Uncomment Firebase import & configure                                                                                 |
| `dzzlo_oms_app/src/utils/firebase.js`                       | **New file** — helpers for analytics, crashlytics, perf monitoring, remote config                                     |
| `dzzlo_oms_app/index.js` or `App.js`                        | Initialize crashlytics, perf, and remote config                                                                       |
| `dzzlo_oms_app/src/navigation/{Customer,Dealer,Auth}/*`     | Add `onStateChange` screen-view tracking to each `NavigationContainer`                                                |
| `dzzlo_oms_app/src/store/apis/createApi.js`                 | (Optional) add `baseQueryWithPerf` wrapper for custom HTTP metrics (axios removed — RTK Query is the only HTTP layer) |
| `dzzlo_oms_app/src/store/middleware/rtkQueryErrorLogger.js` | (Optional) add `crashlytics().recordError` on rejected actions                                                        |

---

## Firebase Benefits Beyond Crashlytics & Analytics

| Service                           | What it does                                                        | Relevance to DZZLO OMS                                   |
| --------------------------------- | ------------------------------------------------------------------- | -------------------------------------------------------- |
| **Crashlytics**                   | Real-time crash reports with stack traces, device info, breadcrumbs | Essential for production stability monitoring            |
| **Google Analytics**              | User behavior, screen views, funnels, retention                     | Understand how users navigate the OMS app                |
| **Remote Config**                 | Change app behavior without releasing updates                       | Toggle features, A/B test UI, update API URLs remotely   |
| **Cloud Messaging (FCM)**         | Push notifications (you already use OneSignal — could consolidate)  | Could replace OneSignal, saving a third-party dependency |
| **Performance Monitoring**        | HTTP request latency, slow screens, app startup time                | Identify slow API calls and screens                      |
| **App Distribution**              | Beta testing distribution (replaces TestFlight/manual APK sharing)  | Easier QA builds distribution                            |
| **Dynamic Links / App Links**     | Deep linking into specific app screens                              | Useful if you share order links, invoice links, etc.     |
| **Authentication**                | Phone, email, Google, Apple sign-in                                 | You previously used this — could re-add if needed        |
| **Cloud Firestore / Realtime DB** | Real-time data sync                                                 | Could power live order status updates                    |
| **In-App Messaging**              | Show targeted messages inside the app                               | Announce features, promotions to specific user segments  |

### Recommended for immediate use:

1. **Crashlytics** — catch and fix crashes before users complain
2. **Analytics** — understand user behavior and app usage patterns
3. **Performance Monitoring** — low effort to add, high value for identifying bottlenecks
4. **Remote Config** — extremely useful for an OMS app (toggle features per client, update configs without app release)

---

## Verification

1. Build and launch on Android emulator/device → check Firebase console for connected app
2. Build and launch on iOS simulator/device → check Firebase console for connected app
3. **Crashlytics:** Trigger a test crash (`crashlytics().crash()`) → verify it appears in Crashlytics dashboard within 5 minutes
4. **Analytics:** Log a custom event → verify in DebugView (real-time) or Analytics dashboard (up to 24h delay)
5. **Performance:** Navigate through screens and make API calls → verify traces appear in Performance dashboard
6. **Remote Config:** Set a parameter in Firebase console → call `fetchAndActivate()` → verify the value is received
7. Check `adb logcat | grep Firebase` / Xcode console for Firebase initialization logs
