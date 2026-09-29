# Phase 8 — Links, App Clips and Instant Experiences: The Customer Who Hasn't Installed Anything

> Level: Advanced | Time: ~2.5 h in the app, plus the web page and API work | Outcome: a tested route table that opens orders, invoices and customers from a link or a push on both platforms, verified Universal Links and App Links, WhatsApp and UPI links with no native code, and an honest plan for the customer who has no app — a web invoice page everywhere, and an App Clip on iOS only if it earns its cost.

---

## 1. The One Idea

A credit customer gets a WhatsApp message from their dealer: an invoice, an amount, a request to pay. They want to **see the invoice, pay it, and perhaps confirm the delivery** — and they have not installed DZZLO. Everything in this phase serves that person, and the one who *has* installed it and expects a link to open the right screen.

What exists on 2026-09-29 (audit, re-checked in the repo):

| Surface | Today | File |
| --- | --- | --- |
| iOS URL schemes | one — the Google OAuth reversed client id (value withheld); no `src` file uses Google Sign-In, so it's vestigial | `ios/dzzlo_oms_app/Info.plist:25-35` |
| Associated domains | none — the entitlements hold only `aps-environment` and the OneSignal App Group | `ios/dzzlo_oms_app/dzzlo_oms_app.entitlements` |
| iOS URL hand-over | none — the `SceneDelegate` starts React Native with `launchOptions: nil` and forwards no URL | `ios/dzzlo_oms_app/AppDelegate.swift:41-58` |
| Android intent filters | MAIN/LAUNCHER only; no `<queries>` (the merged manifest's one `<queries>` block is react-native-webview's payment intents) | `android/app/src/main/AndroidManifest.xml:22-25` |
| Navigation linking | no `linking` prop on the only `NavigationContainer` | `src/components/Error/RestartContext.js:49-57` |
| Notification tap | stores `additionalData` in Redux; navigates nowhere | `src/helpers/OneSignal/index.js:26-30` |

Nothing outside the app can open it at a screen. The ladder, cheapest rung first:

| Rung | What it is | iOS | Android | Works with no app installed? | Cost |
| --- | --- | --- | --- | --- | --- |
| 1. URL scheme `dzzlooms://` | in-app links: push, widget and shortcut taps | `CFBundleURLTypes` | an intent filter | no | under a day |
| 2. Universal Links / App Links | https links that open the app when installed, a web page otherwise | associated domains + AASA file | `autoVerify` + `assetlinks.json` | yes — the web page | 1–2 days in the app, plus the web page _(est.)_ |
| 3. App Clip | a small, install-free slice of the app from a link or QR | a `DzzloClip` target | **no twin** | yes | 10–20 days plus web/server _(est.)_ |
| 4. Android's substitute | web page + UPI intent + App Link into the app when installed | — | the browser | yes | shares rung 2's web page |

The evidence: the product ranking puts "App Clip / instant invoice view" last (**rank 15, low value**) and payment reminders with a UPI link or QR near the top (**rank 2**). myBillBook reviewers praise a plain link — "Costomer getting a link for download their invoice". And Google has shut the Android door: "Starting December 2025, Instant Apps cannot be published through Google Play, and all Google Play services Instant APIs will no longer work."
Source: https://developer.android.com/topic/google-play-instant

So: **rungs 1, 2 and 4 on both platforms first** — for parity, the web page *is* the Android answer, and it serves iPhone users without the app too. **Rung 3 only on iOS, only later**, if the web page proves too slow a path to payment.

```
WhatsApp · SMS · email · QR printed on the invoice
        │   https://<links-host>/i/<token>
        ▼
  app installed and link verified? ──yes──▶ DZZLO opens on that invoice (rung 2)
        │ no
        ▼
  iOS:     App Clip card, if DzzloClip ships (rung 3) ─ or ─ the web invoice page
  Android: the web invoice page ──▶ "Pay by UPI" (upi://pay…) ──▶ chooser of installed UPI apps
                                └─▶ "Get the app" (the Play listing)
```

`<links-host>` stands for an https host you control. The vsyst.in domain already serves the user manuals (`src/screens/Common/Help/index.js:12-13`), so a subdomain there is the natural home; choosing it is the user's call.

## 2. Deep Links and Universal / App Links

### 2.1 The route table: `src/navigation/linking.js`

No linking config exists, so this is a new file. The route names come straight from the navigators:

| Path | Dealer tree | Customer tree | Params |
| --- | --- | --- | --- |
| `orders/:orderId?` | `dealerTab` › `Orders` › `CustomerOrder` | `customerTab` › `Orders` › `DealerOrder` | optional `orderId` |
| `invoices/:ID_FIELD` | `dealerTab` › `InvoicesTab` › `Invoice` | `customerTab` › `InvoicesTab` › `Invoice` | `ID_FIELD`; query `cust_id`, `dealer_id` |
| `customers` | `dealerCustomer` › `Customers` | — (dealer only) | — |
| `daily-summary` | `dealerCustomer` › `DailySummary` | `customerDealer` › `DailySummary` | — |

Why those params: the Invoice screen reads `ID_FIELD`, `cust_id` and `dealer_id` (`src/screens/Common/_Invoice_/index.js:54-56`), fetches the invoice by `ID_FIELD` alone (`:86`), and runs its relation fetch only when both ids are present (`:139`) — the same three that `src/hooks/useInvoiceNavigation.js:23-33` passes today. React Navigation turns a query string into route params. `orders/<id>` is the path [[05-phase-5-notifications-and-live-status]] puts in the order push; neither Orders list (`src/screens/Dealer/Orders/index.js`, `src/screens/Customer/Orders/index.js`) reads a route param today, so opening that one order is a small Tier 3 change, red first. `daily-summary` is where Phase 6's widget tap lands. Give a stack's config an `initialRouteName` if Back should land on the stack's first screen.

Why the table is a function of the role: only one role tree is ever mounted (`AppNavigatorContainer.js` renders `NAVIGATOR_MAP[userRole]`), and both trees call their invoice screen `Invoice`. The table must describe the tree that's actually there.

**A gate the link would walk past.** Dealers with the `DOrder` or `DView` scope and customers with `COrder` or `CView` may not preview invoices — but that check lives in the navigation hook (`useInvoiceNavigation.js:16-18`), not in the Invoice screen, and both invoice stacks register an `Invoice` screen. A deep link skips the hook. Move the check into the screen (red test first, Exercise 6.5) before `invoices/:ID_FIELD` ships — and don't count on the API as the backstop: the v3 API applies protect/authorize to no routes, the known gap recorded in the [[vsyst-technologies/docs/dzzlo_ro_web/00-split-from-dip-web-plan|dzzlo-ro-web plan]].

```js
// src/navigation/linking.js
import { Linking } from 'react-native';
import { getActionFromState, getStateFromPath } from '@react-navigation/native';

export const LINK_PREFIXES = ['dzzlooms://', 'https://<links-host>'];

const SCREENS = {
  dealer: {
    dealerTab: {
      screens: {
        Orders: { screens: { CustomerOrder: 'orders/:orderId?' } },
        InvoicesTab: { screens: { Invoice: 'invoices/:ID_FIELD' } },
      },
    },
    dealerCustomer: { screens: { Customers: 'customers', DailySummary: 'daily-summary' } },
  },
  customer: {
    customerTab: {
      screens: {
        Orders: { screens: { DealerOrder: 'orders/:orderId?' } },
        InvoicesTab: { screens: { Invoice: 'invoices/:ID_FIELD' } },
      },
    },
    customerDealer: { screens: { DailySummary: 'daily-summary' } },
  },
};

export const linkingConfigFor = role => ({ screens: SCREENS[role] ?? {} });

// A link that arrives before the role drawer exists waits here (2.2).
let parked = null;
export const parkLink = url => { parked = url; };
export const takeParkedLink = () => { const url = parked; parked = null; return url; };

// The launch URL is handed out once per process: restartApp() remounts the container (2.2).
let launchUrlTaken = false;

export const buildLinking = ({ role, ready }) => ({
  prefixes: LINK_PREFIXES,
  config: linkingConfigFor(role),
  filter: url => {
    if (ready) return true;
    parkLink(url);
    return false;
  },
  getInitialURL: async () => {
    if (launchUrlTaken) return null;
    launchUrlTaken = true;
    return Linking.getInitialURL();
  },
});

export const replayParkedLink = (navigationRef, role) => {
  if (!navigationRef.isReady()) return false; // keep it parked for the next try
  const url = takeParkedLink();
  const prefix = url && LINK_PREFIXES.find(p => url.startsWith(p));
  if (!prefix) return false;
  const config = linkingConfigFor(role);
  const state = getStateFromPath(url.slice(prefix.length).replace(/^\//, ''), config);
  if (!state) return false;
  const action = getActionFromState(state, config);
  if (action) navigationRef.dispatch(action);
  else navigationRef.resetRoot(state);
  return true;
};
```

`prefixes`, `config`, `filter` and `getInitialURL` are all fields of `LinkingOptions` in the installed `@react-navigation/native` 7.2.2, and `replayParkedLink` mirrors what the library's own `useLinking.native.js` does with an incoming URL: dispatch the action, else `resetRoot`. Wire it into the one container:

```js
// src/components/Error/RestartContext.js:49 — RestartProvider gains a `linking` prop,
// built in AppNavigatorContainer as buildLinking({ role: userRole, ready })
<NavigationContainer ref={navigationRef} key={navKey} theme={theme} linking={linking}
  onReady={handleReady} onStateChange={handleStateChange}>
```

`ready` turns true when the role drawer mounts and false again when it unmounts (sign-out) — an effect in `src/navigation/Dealer/Drawer.js` and `Customer/Drawer.js` that also calls `replayParkedLink(navigationRef, role)`; if the tree isn't ready yet, the link stays parked, and Exercise 6.2 proves the timing on device. React Navigation keeps `filter` and `config` in refs refreshed on every render, so changing them after mount is safe.

### 2.2 The trap: links that arrive before the drawer exists

Two facts collide. The container mounts while `StartupScreen` shows (`AppNavigatorContainer.js`: `!didTryAutoLogin ? <StartupScreen />`), and the role drawer loads through `lazy()`. React Navigation reads the launch URL **when the container mounts** — before the tree the URL points into exists — so a cold-start link is silently dropped. The same happens to a link that arrives while someone is on the sign-in screens.

React Navigation 7.2.2's own answers are marked unstable (`UNSTABLE_routeNamesChangeBehavior: 'lastUnhandled'` on a navigator, `UNSTABLE_UnhandledLinkingContext`) and assume one root navigator whose screens change, whereas this app swaps whole navigators. Hence park and replay: `filter` parks any link that arrives before `ready`, and the drawer's mount effect replays it. That covers the signed-out case too — the link waits through login and lands afterwards.

- **The restart trap.** `restartApp()` remounts the container by changing its `key` (`RestartContext.js:27-29`), and a remounted container asks for the initial URL again — it would re-open the launch link. `getInitialURL` hands it out once per process.
- **`launchMode="singleTask"`** is already set (`AndroidManifest.xml:19`). React Navigation's own warning asks for exactly that, so a link never starts a second copy of the app.

### 2.3 iOS: associated domains, the AASA file and the SceneDelegate

**The entitlement** — Associated Domains (iOS 9.0), the key for both Universal Links and App Clips:

```xml
<!-- ios/dzzlo_oms_app/dzzlo_oms_app.entitlements — addition -->
<key>com.apple.developer.associated-domains</key>
<array>
  <string>applinks:<links-host></string>
</array>
```

**The AASA file** at `https://<links-host>/.well-known/apple-app-site-association`, served over HTTPS "with a valid certificate and with no redirects". Apple's CDN fetches it (an alternate mode bypasses the CDN during development) and "devices check for updates approximately once per week after app installation" — so a mistake in production takes about a week to clear. The JSON layout below follows Apple's "Supporting associated domains" page; the research captured the serving rules, not the schema, so confirm the keys before shipping.

```json
{
  "applinks": {
    "details": [{
      "appIDs": ["YT955YZMZU.in.vsyst.dzzlooms"],
      "components": [{ "/": "/orders" }, { "/": "/orders/*" }, { "/": "/invoices/*" }]
    }]
  }
}
```

Only paths people send each other are claimed over https; `customers` and `daily-summary` are reached through the scheme. `/i/*` — the public invoice link — is deliberately **not** claimed yet. Opening it in the app needs an API call that turns a token into an invoice id, and no such endpoint exists; until it does, that link always shows the web page (§5). App Clips add an `appclips` entry (§4); passkeys would add a `webcredentials` entry ([[09-phase-9-security-privacy-and-release]] §3). The scheme goes in too: add `dzzlooms` to `CFBundleURLTypes`, next to the Google entry whose fate [[02-phase-2-dependency-diet]] decides.

**The SceneDelegate — the part everyone forgets.** In RN 0.84.1, `RCTLinkingManager`'s `getInitialURL` answers from the launch options only (`node_modules/react-native/Libraries/LinkingIOS/RCTLinkingManager.mm:151-163`), and URLs opened while the app runs reach JavaScript through its class methods (`:55-82`). This app starts React Native from the scene with `launchOptions: nil` (`AppDelegate.swift:56`) and forwards nothing, so on iOS **no link reaches JavaScript** — cold or warm — until the scene hands them over. Under the UIScene life cycle, URL opens arrive at the scene delegate rather than the app delegate (UIKit behaviour, not captured in the research — prove it on device):

```swift
// ios/dzzlo_oms_app/AppDelegate.swift — SceneDelegate additions (sketch)
func scene(_ scene: UIScene, willConnectTo session: UISceneSession,
           options connectionOptions: UIScene.ConnectionOptions) {
  // …existing window set-up…
  var launchOptions: [UIApplication.LaunchOptionsKey: Any] = [:]
  if let url = connectionOptions.urlContexts.first?.url {
    launchOptions[.url] = url                                 // cold start from dzzlooms://
  } else if let activity = connectionOptions.userActivities
              .first(where: { $0.activityType == NSUserActivityTypeBrowsingWeb }) {
    launchOptions[.userActivityDictionary] = [                // cold start from a Universal Link
      UIApplication.LaunchOptionsKey.userActivityType: activity.activityType,
      "UIApplicationLaunchOptionsUserActivityKey": activity,
    ]
  }
  factory.startReactNative(withModuleName: "dzzlo_oms_app", in: window, launchOptions: launchOptions)
}

func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
  guard let url = URLContexts.first?.url else { return }
  RCTLinkingManager.application(UIApplication.shared, open: url, options: [:])
}

func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
  RCTLinkingManager.application(UIApplication.shared, continue: userActivity, restorationHandler: { _ in })
}
```

The two dictionary keys are the ones `RCTLinkingManager.mm:154-160` reads. That the prebuilt factory passes these launch options through to the module in bridgeless mode is a reading of the source path, not a tested fact — the cold-start run in Exercise 6.2 settles it.

> **After the upgrade to 0.87:** no step in this phase is known to change, but re-read `getInitialURL` in the new `node_modules/react-native/Libraries/LinkingIOS/RCTLinkingManager.mm` before trusting the launch-option keys again — the SceneDelegate sketch depends on them.

### 2.4 Android: App Links and verification

```xml
<!-- android/app/src/main/AndroidManifest.xml — inside the MainActivity <activity> -->
<intent-filter android:autoVerify="true">
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="https" android:host="<links-host>" />
  <data android:path="/orders" />
  <data android:pathPrefix="/orders/" />
  <data android:pathPrefix="/invoices/" />
</intent-filter>
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <category android:name="android.intent.category.DEFAULT" />
  <category android:name="android.intent.category.BROWSABLE" />
  <data android:scheme="dzzlooms" />
</intent-filter>
```

Publish `https://<links-host>/.well-known/assetlinks.json` (standard Digital Asset Links layout; the research names the file, not its schema):

```json
[{
  "relation": ["delegate_permission/common.handle_all_urls"],
  "target": { "namespace": "android_app", "package_name": "in.vsyst.dzzlooms",
              "sha256_cert_fingerprints": ["<SHA-256 of the certificate that signs installs from Play>"] }
}]
```

With Play App Signing that certificate is the app-signing key Play Console shows, not the upload key; add the upload and debug fingerprints too if test builds must open links (Play-side detail, not from this course's research).

What recent Android changed:

- **Android 12+:** links to unverified domains open in the browser. People can approve them under "Open by default" (`Settings.ACTION_APP_OPEN_BY_DEFAULT_SETTINGS`); `DomainVerificationManager` reports the state at runtime.
- **Android 15+:** a change to `assetlinks.json` can take **up to seven days** to take effect, because verification re-runs periodically. **Dynamic App Links** (Android 15+) add a `dynamic_app_link_components` rule array — path, query and fragment matchers plus `exclude` — that can only narrow the manifest's scope; older Android ignores it.
- **`<queries>`:** [[02-phase-2-dependency-diet]] adds the https VIEW entry — without it `Linking.canOpenURL` resolves `false` on Android 11+ (RN's docs say it may reject); §3 below adds `upi` and WhatsApp.

Source: https://developer.android.com/training/app-links/verify-android-applinks

### 2.5 Push, widget and shortcut taps

[[05-phase-5-notifications-and-live-status]] adds a `path` to the order push (`{ "dealer": "NewOrder", "orderId": "…", "path": "orders/…" }`) and a Tier 1 `routeForNotification(data, role)` that returns `{ kind: 'link', path }` when one is present. This phase gives that branch somewhere to go. Today the drawers act on a tapped notification after a 900 ms `setTimeout` (`src/navigation/Dealer/DrawerContent.js:178-199`, and its Customer twin) that exists only because the navigator may not be mounted yet. A `link` result goes through the table instead, and `filter` does the waiting:

```js
// src/navigation/Dealer/DrawerContent.js — the `link` branch (the Customer twin passes 'customer')
const route = routeForNotification(data, 'dealer');
if (route?.kind === 'link') Linking.openURL(`dzzlooms://${route.path}`).catch(() => {});
```

The `legacy` branch keeps today's switch until every sender adds `path`. Because the scheme is fixed in code, a payload can't send the app to an arbitrary host, and a path the table doesn't know resolves to nothing.

**Native callers need the same URLs.** Phase 5's Live Activity calls `DzzloLinks.order(card.orderId)` and Phase 6's widget calls `DzzloLinks.dailySummary` ([[06-phase-6-widgets-shortcuts-and-intents]]) — Swift, where `linking.js` can't reach. This phase owns that helper, compiled into the app and `DzzloWidgets` targets:

```swift
// ios/Shared/DzzloLinks.swift — target membership: dzzlo_oms_app, DzzloWidgets
import Foundation

enum DzzloLinks {
  static let dailySummary = URL(string: "dzzlooms://daily-summary")!

  static func order(_ id: String) -> URL {
    let safe = id.addingPercentEncoding(withAllowedCharacters: .alphanumerics) ?? ""
    return URL(string: "dzzlooms://orders/\(safe)")!
  }
}
```

Android widget and shortcut taps use the same strings as `ACTION_VIEW` intents. A config test keeps the languages in step: it reads `DzzloLinks.swift`, takes every `dzzlooms://` string (a sample id in place of the interpolation) and asserts each one resolves through `linkingConfigFor('dealer')` or `linkingConfigFor('customer')`.

### 2.6 Tests and device checks

Red first — `src/navigation/__tests__/linking.test.js`:

```js
import { getStateFromPath } from '@react-navigation/native';
import { buildLinking, linkingConfigFor, takeParkedLink } from '../linking';

const leaf = s => { let r; while (s) { r = s.routes[s.index ?? s.routes.length - 1]; s = r.state; } return r; };

test('a dealer invoice link lands on Invoice with all three params', () => {
  const state = getStateFromPath('invoices/inv_1?cust_id=c_1&dealer_id=d_1', linkingConfigFor('dealer'));
  expect(state.routes[0].name).toBe('dealerTab');
  expect(leaf(state)).toMatchObject({
    name: 'Invoice',
    params: { ID_FIELD: 'inv_1', cust_id: 'c_1', dealer_id: 'd_1' },
  });
});

test('the same path lands in the customer tree for a customer', () => {
  expect(getStateFromPath('invoices/inv_1', linkingConfigFor('customer')).routes[0].name).toBe('customerTab');
});

test('orders, customers and daily-summary; unknown paths and no role resolve to nothing', () => {
  expect(leaf(getStateFromPath('customers', linkingConfigFor('dealer'))).name).toBe('Customers');
  expect(leaf(getStateFromPath('orders/o_1', linkingConfigFor('customer')))).toMatchObject({ name: 'DealerOrder', params: { orderId: 'o_1' } });
  expect(leaf(getStateFromPath('daily-summary', linkingConfigFor('dealer'))).name).toBe('DailySummary');
  expect(getStateFromPath('customers', linkingConfigFor('customer'))).toBeUndefined();
  expect(getStateFromPath('nope/1', linkingConfigFor('dealer'))).toBeUndefined();
  expect(getStateFromPath('invoices/inv_1', linkingConfigFor(undefined))).toBeUndefined();
});

test('a link that arrives before the drawer exists is parked, not dropped', () => {
  const { filter } = buildLinking({ role: undefined, ready: false });
  expect(filter('dzzlooms://invoices/inv_1')).toBe(false);
  expect(takeParkedLink()).toBe('dzzlooms://invoices/inv_1');
});
```

The resolution behaviour these tests assert was checked on 2026-09-30 by running the installed `@react-navigation/core` 7.17.2's `getStateFromPath` against this exact table: the dealer path resolves to `dealerTab › InvoicesTab › Invoice` with all three params, `orders/o_1` to the Orders list with `orderId`, `daily-summary` to each role's `DailySummary`, and the customer-tree `customers`, the unknown path and the role-less table all return `undefined`.

Device checks — a matrix, not a single tap:

```bash
# iOS simulator
xcrun simctl openurl booted "dzzlooms://invoices/<id>?cust_id=<c>&dealer_id=<d>"
xcrun simctl openurl booted "https://<links-host>/invoices/<id>"
# Android emulator or phone
adb shell am start -W -a android.intent.action.VIEW -d "dzzlooms://invoices/<id>" in.vsyst.dzzlooms
adb shell pm verify-app-links --re-verify in.vsyst.dzzlooms
adb shell pm get-app-links in.vsyst.dzzlooms
```

| Case | Expect |
| --- | --- |
| Warm, signed in | the invoice opens |
| Cold — app killed first | the invoice opens after auto-login |
| Signed out | the link waits through sign-in (use an **email** identifier — the house rule for OTP runs), then lands |
| `DView` / `CView` user | refused by the Invoice screen itself |
| Customer opens `…/customers` | nothing happens, no crash |
| `restartApp()` after a cold-start link | the invoice does **not** re-open |

## 3. WhatsApp and UPI Without Native Code

Both rails work from JavaScript with `Linking` and the share APIs. The only native work is declarations.

### WhatsApp

- **Chat links:** `https://wa.me/<number>?text=<url-encoded text>`, the number in full international form "without the plus sign (+) or spaces", omitting "any zeroes, brackets, or dashes". These rules come from third-party help pages — WhatsApp's own FAQ couldn't be fetched.
- **`whatsapp://send`:** the scheme alternative; whether it can carry a file is unverified ("generally it does not"). Sending a **PDF** to a chat takes the share sheet or `react-native-share` 12.3.1 (2026-05-04) — `Share.shareSingle` with `social: Share.Social.WHATSAPP` and `whatsAppNumber`; its WhatsApp Business target is Android-only ([[03-phase-3-files-share-and-pdf]]).
- **Automated messages** (order status, reminders at scale) belong on the server through the **WhatsApp Business Platform**, not in the app. It has charged **per message since July 2025**. India rates: marketing ₹0.8631, utility ₹0.1150 (effective 1 Jul 2026), authentication ₹0.1150, plus 18 % GST; utility templates delivered inside the customer-service window are free. **Sources disagree on the utility rate** — two others quote ₹0.145 — and Meta's own rate card wasn't fetched.

### UPI

- **The link format** (NPCI UPI Linking Specification 1.6, Nov 2017): `upi://pay?pa=…&pn=…` with `pa` (VPA), `pn` (payee name), `mc` (merchant code), `tid`, `tr` (transaction reference), `tn` (note), `am` (amount), `mam` (minimum amount), `cu` (currency) and `url`. "All PSP applications must mandatorily implement listening to 'UPI' links."
- **Android:** the generic intent lists every installed UPI app — from the app, and from a mobile web page in the browser. Google Pay for India: "NPCI requires that you support the generic intent call in all cases"; its package is `com.google.android.apps.nbu.paisa.user`.
- **iOS:** there is no system chooser. PSP SDKs target specific apps through app-specific schemes that must be listed in `LSApplicationQueriesSchemes` (the PSP docs' examples: `tez`, `phonepe`, `paytmmp`, `bhim`, `credpay`). The exact URL each app expects isn't in this course's research — take it from your PSP's iOS docs.
- **Status is a server fact.** Google Pay: "If the Google Pay response status is Submitted or Succeeded, you must check with your PSP or payment aggregators to ensure that the correct order amount is paid." Paytm's iOS flow confirms through its backend Transaction Status API. **Never mark an invoice paid from what an intent returns**; reconcile from the dealer's bank or PSP data.
- **Collect requests:** an NPCI circular of 29 Jul 2025 stopped **P2P** collect requests from **1 Oct 2025**; **merchant** collect continues, with explicit approval and a UPI PIN.
- **Libraries:** `react-native-upi-payment` 1.0.5 (2023) and `react-native-upi-pay` 1.0.8 (2020) are abandoned. A 20-line builder is the right size.
- **Unverified risk:** whether PSP apps refuse prefilled-amount intents to personal (non-merchant) VPAs, which many small dealers use. Test on real phones with a dealer's actual VPA before promising a "Pay" button.

### The declarations

```xml
<!-- ios/dzzlo_oms_app/Info.plist — addition -->
<key>LSApplicationQueriesSchemes</key>
<array>
  <string>whatsapp</string>
  <string>tez</string>
  <string>phonepe</string>
  <string>paytmmp</string>
  <string>bhim</string>
  <string>credpay</string>
</array>
```

```xml
<!-- android/app/src/main/AndroidManifest.xml — inside <manifest>, next to Phase 2's https entry -->
<queries>
  <intent>
    <action android:name="android.intent.action.VIEW" />
    <data android:scheme="upi" />
  </intent>
  <package android:name="com.whatsapp" />
  <package android:name="com.whatsapp.w4b" />
</queries>
```

The Android entries are an inference — the package-visibility docs weren't fetched, and `com.whatsapp.w4b` appears in the research as unconfirmed. Pin both files with a config test — booleans for `Info.plist`, per [[02-phase-2-dependency-diet]] §1's secrets rule.

### A payment reminder, designed

The dealer taps "Send reminder" on an overdue invoice. The app opens a wa.me chat with the customer's number and this text:

```
Sharma Roadways — payment reminder from <dealer name>
Invoice INV-2417 · 28 Sep 2026 · ₹1,23,456.50 due
View and pay: https://<links-host>/i/<token>
```

The https link goes in the message, not a raw `upi://` string: whether WhatsApp makes a `upi://` link tappable is unverified, while an https link always is. The web page (§5) carries the UPI button:

```
upi://pay?pa=<dealer VPA>&pn=<dealer name>&tr=INV-2417&tn=INV-2417&am=123456.50&cu=INR
```

**Money is whole paise.** `₹1,23,456.50` in the text and `am=123456.50` in the link both come from the integer `12345650` — the invoice total the API computed by rounding every line half-up in whole paise and then summing. The builder never touches a float:

```js
// src/helpers/Links/upi.js
const VPA = /^[A-Za-z0-9._-]+@[A-Za-z0-9.-]+$/;

export const paiseToAm = paise => {
  if (!Number.isSafeInteger(paise) || paise <= 0) {
    throw new RangeError('amount must be a positive whole number of paise');
  }
  return `${Math.floor(paise / 100)}.${String(paise % 100).padStart(2, '0')}`;
};

export const upiPayUri = ({ vpa, payeeName, invoiceNo, amountPaise }) => {
  if (!VPA.test(vpa)) throw new Error('not a VPA');
  const enc = encodeURIComponent;
  return `upi://pay?pa=${vpa}&pn=${enc(payeeName)}&tr=${enc(invoiceNo)}&tn=${enc(invoiceNo)}` +
    `&am=${paiseToAm(amountPaise)}&cu=INR`;
};
```

`am` as rupees with two decimals, and which fields to percent-encode, aren't spelled out in the research — confirm both against the NPCI spec and your PSP, and test on Google Pay, PhonePe and Paytm with a ₹1 invoice.

## 4. App Clips (iOS)

An App Clip is a small part of an app that runs without installing it: a card slides up after scanning a QR or App Clip Code, tapping an NFC tag, a Safari Smart App Banner, a Maps place card or a Messages link. The system removes it after a period of inactivity. It has existed since iOS 14 (`APActivationPayload`).

### The limits that shape the design

| Limit | Value |
| --- | --- |
| Size, uncompressed | 10 MB on iOS 15 and earlier; **15 MB on iOS 16**; **100 MB on iOS 17+ only when every invocation is digital** (no App Clip Codes, QR or NFC), the clip targets iOS 17+ only and expects a reliable connection |
| A QR printed on an invoice | a physical invocation — so **15 MB** |
| No runtime for | App Intents, BackgroundTasks, CallKit, Contacts, EventKit, FileProvider, HealthKit, PhotoKit, Speech and others; no background `URLSession`; no background modes |
| Reserved for the full app | in-app purchase, custom URL schemes, app extensions (except a widget extension holding only a Live Activity), `requestReview()` |
| Identity | `UIDevice.name` and `identifierForVendor` return empty strings; **no Face ID** |
| Location | never continuous; When-In-Use resets daily at 4:00 a.m. |
| Notifications | may schedule or receive them for up to 8 hours after each launch |
| Web sign-in | `ASWebAuthenticationSession` is supported |

Source: https://developer.apple.com/documentation/appclip/choosing-the-right-functionality-for-your-app-clip

### How a clip is invoked

An App Clip Code, NFC tag or QR code at a place; a link in Maps; a Smart App Banner in Safari or `SFSafariViewController`; an App Clip card in Safari or iMessage; a link shared in Messages; a preview or link in another app (iOS 17+); a link in email or on a website. A **default** experience, reached through the App Store Connect-generated link (`https://appclip.apple.com/id?p=<bundle id>&…`, since iOS 16.4 — the format is from a secondary source), needs no server. **Advanced App Clip Experiences** — tied to a physical location or to several businesses — and anything below iOS 16.4 need the website associated with the clip: `appclips:<links-host>` in associated domains plus an `appclips` entry in the AASA file. Invoking the clip from your own invoice URL means that association; check in App Store Connect which experience type your `/i/` URLs need.

### The React Native reality: `DzzloClip` is Swift

An RN clip would carry Hermes and React Native core inside a 15 MB budget — an older, undated write-up puts Hermes alone at about 3.2 MB and suggests turning Hermes off. The only RN tooling, `react-native-app-clip` 0.9.1 (2026-06-12), is an Expo config plugin that needs `npx expo prebuild` ("Bare React Native projects cannot use this plugin") and is flagged `newArchitecture: false`. So the clip is a **native SwiftUI target, `DzzloClip`, that calls the DZZLO API directly** — no React Native, no pods. A small SwiftUI clip fits the budget comfortably.

| Piece | Value |
| --- | --- |
| Target | `DzzloClip`, from Xcode's App Clip template |
| Bundle id | `in.vsyst.dzzlooms.Clip` — Apple's rule is the full app's id plus `.Clip` |
| Entitlements | the three App Clip entitlements Xcode adds — `com.apple.developer.on-demand-install-capable`, `com.apple.developer.parent-application-identifiers`, `com.apple.developer.associated-appclip-app-identifiers` (the research lists them together; check which target each lands on); associated domains `appclips:<links-host>` |
| Deployment target | iOS 16.4, the default-link floor — whether App Store Connect accepts a clip floor above the parent app's 15.1 isn't verified; the first upload will tell you |
| Pods | none — spend the 15 MB on your own code |
| Privacy manifest | its own `PrivacyInfo.xcprivacy` if it uses a required-reason API ([[09-phase-9-security-privacy-and-release]] §4) |

What the clip does, and nothing more:

1. **Read the invocation URL**, take the `/i/<token>` path, ask the API for that one invoice, and show it: dealer, invoice number, date, amount in ₹ (formatted from the paise the API sends), status.
2. **Pay** through a web checkout inside `ASWebAuthenticationSession`, which clips support. Fuel is a physical good, so in-app purchase is not allowed (**3.1.3(e)**). Whether a clip may open UPI apps directly is **unverified**: custom URL schemes are reserved for the full app, and the research left clip-to-UPI hand-off open.
3. **Hand off to the full app.** The URL is the primary hand-off: once DZZLO is installed, the same https link opens the full app as a Universal Link. For anything the clip learned (a delivery confirmation, say), App Groups let the clip and the app share a container and a keychain access group. Use a dedicated key in `group.in.vsyst.dzzlooms.shared` ([[05-phase-5-notifications-and-live-status]]) or register a separate group — separate is least-privilege, since the shared one also holds the widget snapshot. That's the user's decision. That the full app can read the clip's group container after install isn't verified here — prove it on device.

```swift
// DzzloClip/DzzloClipApp.swift — sketch
import SwiftUI

@main
struct DzzloClipApp: App {
  @State private var token: String?

  var body: some Scene {
    WindowGroup {
      InvoiceView(token: token)          // fetches from the API, renders, offers Pay
        .onContinueUserActivity(NSUserActivityTypeBrowsingWeb) { activity in
          guard let url = activity.webpageURL, url.pathComponents.count == 3,
                url.pathComponents[1] == "i" else { return }
          token = url.pathComponents[2]
        }
    }
  }
}
```

Receiving the invocation through `onContinueUserActivity` follows Apple's App Clip docs; the research captured `APActivationPayload` (iOS 14), not this handler — confirm it when you build. The clip can't import `src/theme`, so mirror the colour tokens into its asset catalogue and pin the mirror with a config test that reads `src/theme`; check the layout at 320 pt, en and hi. One optional extra: a clip may bundle a widget extension that holds only a Live Activity — enough for "your tanker is on the way" inside the 8-hour notification window.

### Submission steps

1. Build the target with its entitlements; add `appclips:<links-host>` and the AASA entry `"appclips": { "apps": ["YT955YZMZU.in.vsyst.dzzlooms.Clip"] }`.
2. The clip ships **inside** the app's archive — one upload, and TestFlight covers both.
3. In App Store Connect: the App Clip card (header image, subtitle, call to action), the default experience, and an advanced experience if the invoice URLs need one.
4. The account holder registers any new App Group and accepts pending agreements; per-target App IDs and profiles come from automatic signing ([[09-phase-9-security-privacy-and-release]] §6).

**Review clauses** (App Store Review Guidelines, fetched 2026-09-29): **2.5.16(a)** "all App Clip features and functionality must be included in the main app binary. App Clips cannot contain advertising"; **3.1.3(e)** physical goods use non-IAP payment; **5.1.1** data minimisation. Every clip feature — view the invoice, pay it — must also exist in the main app.

**Effort:** 10–20 days plus web/server work _(est.)_, with a medium-high running cost. The ecosystem verdict is **SKIP for now — use web invoice links**. Build the clip only if the web page, measured, loses customers between the link and the payment.

## 5. Android Without Instant

Play Instant is gone and nothing on Android replaces it. The substitute is the same page iPhone users without an App Clip see.

**The web invoice page** at `https://<links-host>/i/<token>`:

- **Which web app?** Neither existing one: dip-web is the superadmin console, and dzzlo-ro-web is the dealer-only RO dip-meter app whose login accepts the dealer role only ([[vsyst-technologies/docs/dzzlo_ro_web/00-split-from-dip-web-plan|dzzlo-ro-web]]). A customer invoice page is a new, small, public surface.
- **The token** is unguessable, expires, covers exactly one invoice, and is checked by the endpoint that serves the page — no GSTIN, amount or id in the URL. The v3 API's protect/authorize gap means this endpoint must do its own checking.
- **The content** is rendered by the server. The app builds invoice HTML in `src/helpers/Download/invoiceHTML/*`, but that code runs on the phone; whether the API can already produce invoice HTML or a PDF wasn't checked (an audit gap).
- **"Pay by UPI"** is the `upi://pay` link from §3. On Android the browser lists the installed UPI apps; on a desktop browser, show a QR of the same string instead.
- **"Open in the app"** needs no button: with verified App Links the OS opens DZZLO before the page loads. The page is only ever seen by people without the app — or before `/i/*` is claimed (§2.3).
- **"Get the app"** links to the Play listing, `https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms` — the URL the app already uses (`src/helpers/OneSignal/index.js:7-8`). On iPhone, Safari's Smart App Banner can invoke the clip once `DzzloClip` exists.
- **House rules apply to the page too:** 320 px wide at the default text size, en and hi, colours from the same tokens as the app, amounts formatted from whole paise.

**App Links into the installed app** are §2.4; this page is their fallback. When the resolve-token endpoint exists, add `/i/*` to the AASA file and the intent filter, plus an `i/:token` route that resolves and redirects — and the same link becomes "open in the app if installed, the web page if not" on both platforms.

**The share and camera grant change.** Android 17's docs warn that **from Android 18**, `ACTION_SEND`, `ACTION_SEND_MULTIPLE` and `ACTION_IMAGE_CAPTURE` will no longer grant URI permissions automatically: set `FLAG_GRANT_READ_URI_PERMISSION` / `FLAG_GRANT_WRITE_URI_PERMISSION` explicitly. That matters whenever the app shares an invoice PDF to WhatsApp through a `FileProvider` ([[03-phase-3-files-share-and-pdf]]). Whether `react-native-share` already sets the flags isn't verified, and the research doesn't say whether the change depends on the target SDK — read the library's Android share code before Android 18 arrives.

## 6. Exercises

**6.1 — The route table, red → green.** Write `src/navigation/__tests__/linking.test.js` (§2.6) against a stub `linking.js` that exports an empty table; watch the tests fail for the right reason; then fill in the table. **Produces:** a red run and a green run.

**6.2 — The cold-start proof.** Wire `linking` into `RestartContext.js`, add the SceneDelegate forwarding and the Android intent filters. Kill the app, fire `adb shell am start … dzzlooms://invoices/<id>` and `xcrun simctl openurl booted …`, and walk the §2.6 matrix — signed in, signed out (email identifier), killed, after `restartApp()`. **Produces:** one device observation per row, on both platforms.

**6.3 — Paise to UPI.** Test `paiseToAm` and `upiPayUri` first: `12345650 → '123456.50'`, `5 → '0.05'`, `100 → '1.00'`; `0`, `-1` and `1.5` throw; a bad VPA throws; a payee name with a space is encoded. Then write the helpers, plus a `waChatUrl` builder for the reminder (a 10-digit Indian mobile gains the `91` prefix; `+`, spaces and dashes are stripped). **Produces:** a green test file.

**6.4 — Verify an App Link.** Host `assetlinks.json` on a test host you control, install a debug build whose intent filter points at it, and run `adb shell pm verify-app-links --re-verify in.vsyst.dzzlooms`, then `adb shell pm get-app-links in.vsyst.dzzlooms`. **Produces:** the verification state before and after publishing the file, and how long it took.

**6.5 — Close the preview gate.** Tier 3 test first: a `DView` dealer who reaches the Invoice screen through a link sees the "not allowed" state and no invoice request is made. Then move the scope check from `useInvoiceNavigation.js` into the screen. **Produces:** a red test, then green.

**6.6 — The App Clip size budget (optional, throwaway).** In a scratch Xcode project — never in `dzzlo_oms_app` — add a SwiftUI App Clip target that fetches and renders one JSON invoice, archive it, and read the uncompressed clip size against 15 MB. **Produces:** one number and a keep-or-kill note for `DzzloClip`.

---

**Next:** [[09-phase-9-security-privacy-and-release]] — every entitlement, purpose string and declaration from Phases 3–8, read the way App Review and Play will read them.
