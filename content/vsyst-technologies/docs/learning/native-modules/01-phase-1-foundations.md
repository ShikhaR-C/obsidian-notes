# Phase 1 — Foundations: The New Architecture, and Your First Native Module

> Level: Easy → Intermediate | Time: ~2 h to read, ~1 day to build and device-check `NativeAppInfo` _(est.)_ | Outcome: you can say what a Turbo Module is and when this app should write one, you know why the house chose Turbo Modules over Nitro and Expo, and you have built the app's first in-house module test-first on iOS and Android.

---

## 1. The One Idea

A native module is **one typed contract with two implementations**. You write the contract once, in TypeScript, in `specs/`. Codegen turns it into an Objective-C++ protocol for iOS and an abstract Java class for Android. You fill in both sides, and JavaScript calls the result as if it were an ordinary object. Everything else in this course is detail around that sentence.

The five words you need, in the order the pieces run:

| Word | What it is | Where it shows up in this app |
| --- | --- | --- |
| **Hermes** | The JavaScript engine. RN 0.84's release is titled "Hermes V1 by Default". | `hermesEnabled=true` (`android/gradle.properties:39`), `USE_HERMES = true` (pbxproj) |
| **JSI** | The C++ interface through which the engine calls native code directly. A Turbo Module reaches JS as a JSI host object. | Invisible — codegen writes it. |
| **Turbo Module** | A native module on the New Architecture: typed by a spec, created lazily "the first time it is accessed", then kept. | None of ours yet. Twelve installed packages plus `react-native` itself ship a `codegenConfig`. |
| **Fabric** | The New Architecture renderer. A *Fabric component* is a native view with a `*NativeComponent.ts` spec. | `react-native-screens`, `react-native-svg`, `react-native-webview` … |
| **Codegen** | Reads `Native*.ts` / `*NativeComponent.ts` specs and generates the glue for both platforms. | Runs inside `bundle exec pod install` and the Gradle build. |

Since 0.82 the New Architecture is the only one: `newArchEnabled=false` "will be ignored and your app will still run using the New Architecture". Six of the app's native packages ship no `codegenConfig` and run through the interop layer — the four `@react-native-firebase/*` at 24.0.0, `react-native-device-info` and `react-native-linear-gradient`; [[02-phase-2-dependency-diet]] §4 deals with all six. Source: [RN 0.82 blog](https://reactnative.dev/blog/2025/10/08/react-native-0.82).

The shape of every module in this course, drawn with the one you build in §5:

```
 src/native/appInfo.js          JS facade: reads once, caches, normalises
        │ import
        ▼
 specs/NativeAppInfo.ts          the contract: TurboModuleRegistry.getEnforcing<Spec>('NativeAppInfo')
        │ codegen (bundle exec pod install / Gradle)
        ├──────────────────────────────────────────┐
        ▼ iOS                                       ▼ Android
 <DzzloOmsSpec/DzzloOmsSpec.h>                in.vsyst.dzzlooms.specs.NativeAppInfoSpec
   @protocol NativeAppInfoSpec                  abstract Java class; JNI glue built into libappmodules.so
   NativeAppInfoSpecJSI  (JSI glue)
        │ conforms                                  │ extends
        ▼                                           ▼
 RCTNativeAppInfo.mm   ObjC++, thin          NativeAppInfoModule.kt   thin  (+ NativeAppInfoPackage)
        │ calls                                     │ calls
        ▼                                           ▼
 AppInfoCore.swift     the logic, XCTest     AppInfoCore.kt           the logic, JUnit
```

Two rules fall out of the picture. **Sync methods run on the JS thread** — keep them tiny; void and Promise methods are dispatched to a native queue (RN 0.84.1 `RCTTurboModuleManager.mm`, `JavaTurboModule.cpp`). **The layer that touches React Native stays thin** — decisions live in a plain Swift or Kotlin class a unit test can reach without React Native, the split RN's own Swift guide documents.

### How much native code should a JS-first team write?

As little as the product allows. Since 2018–19 React Native's own policy ("Lean Core") has been to move modules *out* of core into community packages — WebView, NetInfo, AsyncStorage, Clipboard, Slider, ImageEditor. This app already lives that way: its only custom native code beyond the template is the OneSignal notification-service extension. Source: [Lean Core, RN #23313](https://github.com/facebook/react-native/issues/23313).

| Write native only when… | Otherwise, in this order |
| --- | --- |
| a platform API you need has **no maintained library** | 1. a maintained community library |
| you need an **OS extension or target** (widget, notification service extension, share extension, watch) | 2. a JS-only solution |
| a **measured** JS↔native hot path exists (per-frame calls, sensor streams, large binary buffers) | 3. a feature trade-off |
| a **small, critical library is abandoned** and cheaper to vendor than to replace | |

Each module costs two more languages and their build systems, a native test harness, a review at every RN minor (eight minors from 0.80 on 2025-06-12 to 0.87 on 2026-08-11 — about six a year), a privacy and store-policy check, and a store release for every change, because native code cannot ship over the air (App Review 2.5.2; Play's Device and Network Abuse policy). Plan on **zero to two thin modules** for this app, each with a JS facade, Jest tests, native unit tests and a recorded device run — and only when a trigger in the left column fires.

**The Shopify signal, read correctly.** On 2026-09-10 Shopify, React Native's best-known adopter, said it is moving its major apps to Swift and Kotlin because coding agents made building twice cheap ("LLMs changed one of the core assumptions behind our 2020 decision"). That is a verdict on *which stack a large team with native specialists picks*; the article gives no advice to other teams and still calls React Native "an excellent framework". Agents cut the cost of *writing* Swift and Kotlin, not of *owning* it — upgrade reviews, device testing and crashes in code nobody on the team reads fluently all remain. It is no reason for a JS-first team to write more modules. Source: [Shopify Engineering, 2026-09-10](https://shopify.engineering/back-to-native).

**Where `NativeAppInfo` sits on those rules — honestly.** `react-native-device-info` is maintained (15.0.2, 2026-02-21, already latest), so the library-first answer to its bug is a one-line fix (`getUniqueIdSync()`, §5.2). The module still earns its place as the course's first build: it is the smallest real module there is (ten constants, no events, no threading), it retires one of the six interop-layer packages, the app uses ten of that library's getters, and it fixes a live bug in the API's `meta` header. If you would rather not own it, ship the one-liner and skip to §6.

## 2. The choices, decided

| | **Turbo Modules** (chosen) | Nitro Modules | Expo Modules API |
| --- | --- | --- | --- |
| Authoring | TS spec in `specs/` + RN codegen. iOS class in Objective-C++; Swift only behind a thin adapter. Android Kotlin/Java extends the generated spec | TS `HybridObject` interface + its own codegen (`nitrogen`). Swift and Kotlin directly ("No Objective-C", "No Java") | Swift/Kotlin DSL (`Module`, `Function`, `AsyncFunction`, `Events`). No codegen — Nitro's comparison calls Expo modules "untyped by default" |
| Runtime dependency | none — part of React Native | `react-native-nitro-modules`; every module compiles C++ and ships `.so` files | the `expo` package, with Podfile, Gradle, AppDelegate, Metro and Babel changes (`npx install-expo-modules@latest`) |
| RN-version coupling | ships with RN; the documented surface (spec, `BaseReactPackage`, generated base classes, `getTurboModule:`, `CodegenTypes.EventEmitter<T>`) barely moved 0.82 → 0.87 _(inference from the release notes)_ | needs RN ≥ 0.75; 0.36.2 (2026-07-27) added "React Native 0.87+ support"; still 0.x, so expect breaks between minors | each Expo SDK targets exactly one RN minor — **none targets 0.84 or 0.87** (box below) |
| Registration in an app | iOS automatic through `codegenConfig.ios.modulesProvider`; Android by hand in `MainApplication.kt` | natural home is a (local) library, autolinked; can be added to an app by hand | `npx create-expo-module@latest --local` → `modules/<name>`, autolinked |
| Speed, vendor benchmark (100,000 calls) | `addNumbers` 115.86 ms · `addStrings` 179.02 ms | 7.27 ms · 29.94 ms | 434.85 ms · 429.53 ms |
| Testing | Jest with the spec mocked; XCTest / JUnit on plain classes | Jest mocking pattern not verified | `expo-modules-test-core`, TS mocks generated from Swift; Kotlin-only methods need hand mocks |
| Maturity (2026-09-29) | core; New Architecture only since 0.82 (2025-10-08) | 0.37.1 (2026-08-27), MIT, ~2.0k stars, no 1.0 | `expo` ~10.4 M downloads a week; SDK 57 current |

The benchmark row is Nitro's own page, with its own caveat: "These benchmarks only compare native method throughput in extreme cases, and do not necessarily reflect real world use-cases." Expo's counter-view — "the time spent executing the body of a native method is often orders of magnitude greater than the overhead of the method invocation" — fits an order-management app that calls a module a handful of times per screen. Sources: [Nitro comparison](https://nitro.margelo.com/docs/comparison), [Expo Modules overview](https://docs.expo.dev/modules/overview/).

**The decision (the user, 2026-09-29):**

- **Our own modules are official Turbo Modules** — TypeScript spec + codegen; Swift behind a thin Objective-C++ adapter on iOS; Kotlin + `BaseReactPackage` on Android; Fabric components the day we need a native view.
- **Nitro** is a later option **for a measured hot path only**. Nothing in this app qualifies today.
- **Expo** is one optional track, never used to author our own modules (box below). **Hot Updater** is the no-Expo route for over-the-air JS updates — [[09-phase-9-security-privacy-and-release]].
- **Specs are TypeScript only inside `specs/`**; the rest of the app stays JavaScript. TypeScript 6.0.2 is already a devDependency, Babel already strips TS in Metro and Jest, and RN 0.84.1's codegen picks its parser by file extension — a `.js` spec would be parsed as Flow.

> **Optional track — Expo modules, after the upgrade.** Expo modules are for *third-party* capabilities whose community package has died (print, location, quick actions) and the prerequisite for EAS Update — never for our own modules. The track opens only on an Expo-paired React Native version:
>
> | Expo SDK | React Native | Min iOS | Xcode |
> | --- | --- | --- | --- |
> | 55 | 0.83 | 15.1+ | 26.2+ |
> | 56 | 0.85 | 16.4+ | 26.4+ |
> | 57 | 0.86 | 16.4+ | 26.4+ |
> | 58 (`next`, preview) | 0.88.0-rc.3 | — | — |
>
> Nothing pairs with **0.84** (today) or **0.87** (the planned upgrade), and SDK 56/57 would lift the app's iOS minimum from 15.1 to 16.4. The track and its OTA half live in [[09-phase-9-security-privacy-and-release]]; the full matrix is in [[11-reference]]. Sources: [Expo SDK versions](https://docs.expo.dev/versions/latest/), [Installing Expo modules](https://docs.expo.dev/bare/installing-expo-modules/).

## 3. The toolchain as measured

Read on the dev machine and in `dzzlo_oms_app` (branch `release/v1_79`). ✅ = re-checked 2026-09-30; the rest is from the 2026-09-29 audit.

| What | Value | Where | What it means for module work |
| --- | --- | --- | --- |
| Xcode / Swift | Xcode 27.0 (27A266a), Swift 6.4 ✅ | `xcodebuild -version`, `swift --version` | a Swift 6.4 compiler… |
| Swift language mode | `SWIFT_VERSION = 5.0`, both targets ✅ | `project.pbxproj` | …in Swift 5 mode — the generated header reads "Swift version 6.4 effective-5.10". Complete concurrency checking is off: the compiler will not stop you touching UIKit off the main thread, so you must. |
| Swift ↔ Objective-C | generated header `dzzlo_oms_app-Swift.h` ✅; no bridging header (`SWIFT_OBJC_BRIDGING_HEADER` unset) | DerivedData, pbxproj | the header name the ObjC++ adapter imports — it already declares `AppDelegate`, `ReactNativeDelegate : RCTDefaultReactNativeFactoryDelegate`, `SceneDelegate`. Swift has never needed Objective-C here, and `NativeAppInfo` doesn't either (§5.6). |
| iOS deployment target · C++ | 15.1 = RN 0.84's `min_ios_version_supported` · `c++20` / `gnu++20` | pbxproj, RN `helpers.rb` | anything newer than 15.1 needs `#available`; §5.6's designated initialisers are C++20 — fields in declaration order. |
| Xcode project | `objectVersion = 54`, classic groups ✅ | pbxproj | new files join no target by themselves — add each in Xcode (a pbxproj edit; the working tree already carries an uncommitted build-number bump). |
| Pods | static libraries (40 static targets, 0 frameworks), prebuilt `React.xcframework`, RNFB forced static; `use_frameworks!` only when `USE_FRAMEWORKS` is set | `Podfile:11-43` | an in-app module compiles into the app target and never meets a linkage question. |
| Android build | AGP 8.12.0, Gradle 9.0.0, Kotlin 2.1.20, NDK 27.1.12297006, buildTools 36.0.0 ✅ | RN Gradle-plugin catalog, wrapper, `android/build.gradle:3-8` | a Kotlin-only module adds no `.so`, so the 16 KB page-size rule never touches it. |
| Android SDK levels | minSdk 24, compile/target 36 ✅ | `android/build.gradle` | anything above API 24 needs a version check (`longVersionCode` is API 28). |
| Android package · registration | `in.vsyst.dzzlooms` · `// add(MyReactNativePackage())` placeholder ✅ | `app/build.gradle:84-86`, `MainApplication.kt:16-19` | `in` is a Kotlin keyword, so package and import lines need backticks (as `MainApplication.kt:1` shows); `add(NativeAppInfoPackage())` goes at the placeholder. |
| Native test targets | iOS: app + `OneSignalNotificationServiceExtension`, no unit-test bundle. Android: no `testImplementation`, no `src/test` | pbxproj, `app/build.gradle` | §5.5 adds the first test target on each platform. |
| Codegen | no `codegenConfig`, no `specs/` ✅ | `package.json` | §5.3 adds both. |
| JS tests | Jest 30.3.0, preset `react-native`, native mocks inline in `jest.setup.js`, custom resolver; 172 suites ✅ — 174 once this phase adds `appInfo.test.js` and `appInfo.config.test.js` | `jest.config.js`, file count | a new native module means a new mock in `jest.setup.js`. |
| CI · Node | Jest only (`ubuntu-latest`, Node 22) · `engines: >= 22.11.0`, machine v26.3.0 ✅ | `.github/workflows/test.yml`, `node --version` | CI never compiles Swift or Kotlin: the device run is part of "green". 0.87 raises the Node floor to 22.13.0. |

**If `USE_FRAMEWORKS` is ever set.** The in-app module is unaffected — it lives in the app target. What changes is everything around it: a *local library* (a pod) would inherit framework linkage, untested with 0.84's prebuilt `React.framework`; the Podfile's own comment records that global static frameworks "breaks react-native-worklets / react-native-reanimated on RN 0.84"; and imports must be framework-style (`<React/…>`), which 0.87's SwiftPM path demands too. Never flip linkage as a side effect of adding a module.

## 4. The test-first workflow for native code

The house ritual (`AI.md`) does not change for native code: the failing test is committed alone as `test(scope): … (red)`, the green commit changes source and never assertions, a mutation smoke is recorded in the PR, and no test is deleted or skipped without a written verdict — see the [[vsyst-technologies/docs/oms_app/tdd-testing-guide|TDD testing guide]] for the tiers. Native code adds layers:

| Step | Layer | What "red" looks like | Tooling |
| --- | --- | --- | --- |
| a | JS facade (Tier 1) | Jest fails | `jest.mock` of the spec |
| a′ | wiring | a `*.config.test.js` fails | files read off disk |
| b | native logic | XCTest / JUnit fails (first run: does not compile) | new test targets |
| c | implementation | — | green on all of the above, both platforms |
| d | device | seen on the iOS simulator **and** the Android emulator | recorded in the PR; screenshots stay out of the repos |

**(a) Why the spec must be mocked.** In the running app, `TurboModuleRegistry` asks `global.__turboModuleProxy` for the module. Jest has no proxy, so it falls back to `NativeModules[name]` from RN's Jest mock — a fixed object (`AlertManager`, `AsyncLocalStorage`, …) that has never heard of your module — and `getEnforcing` throws `TurboModuleRegistry.getEnforcing(...): 'NativeAppInfo' could not be found. Verify that a module by this name is registered in the native binary.` (RN 0.84.1 `Libraries/TurboModule/TurboModuleRegistry.js`; RN's `jest/setup.js` has no TurboModule mock). So every module gets two mocks: a global one in `jest.setup.js`, so any suite importing the facade can load, and a per-file `jest.mock` in the facade's own test. The test targets the **facade**, never the spec.

The house precedent is `src/i18n/deviceLocale.js`: it reads native modules at call time — `NativeModules.SettingsManager` on iOS, `TurboModuleRegistry.get('I18nManager')` on Android — with `'en'` as the floor, and `deviceLocale.test.js:36-84` swaps fakes into `NativeModules` per case. `get` returns `null` where `getEnforcing` throws, which suits RN's own modules that exist on one platform only. For a module we ship on both, the course uses `getEnforcing`: a missing module is a build mistake, and the device run should fail loudly on it rather than send `unknown` for months.

**(a′) Pin the wiring.** Nothing in the import graph notices a missing `codegenConfig` or a forgotten `add(…Package())`. The house answer is a `*.config.test.js` that reads the file off disk — five exist today (`androidText`, `locales`, `orientation`, `keyboard`, `firebaseModules`). Every native module gets one.

**(b) Native unit tests.** Neither platform has a test target, and the research found no official RN guidance on unit-testing Turbo Modules. The rule is structural: every decision goes in a plain class (`AppInfoCore`) that knows nothing about React Native, and only that class is unit-tested.

| Claim | Status |
| --- | --- |
| JUnit 4.13.2 and Robolectric 4.15.1 are RN 0.84.1's own test versions (`gradle/libs.versions.toml`) | ✅ read from the installed catalog |
| The Kotlin side compiles, and §5.5's JUnit test passes | ✅ 2026-09-30, outside the repo: core, module and package compile with Kotlin 2.1.20 against react-android 0.84.1 and the generated `NativeAppInfoSpec.java`; the test's two methods pass (run against a stand-in for `org.junit` — no JUnit jar was installed). `:app:testDebugUnitTest` itself has not been run |
| A host-less XCTest bundle can compile one Swift file from the app and test it | core + test type-check ✅ (§5.6); the bundle has not been run on a simulator |
| `ReactApplicationContext(context)` can be built under Robolectric in 0.84 | **not verified** — so the course never needs it |
| iOS registration: `modulesProvider` → generated provider map → the `RCTAppDependencyProvider` that `AppDelegate.swift:20` installs | inferred from the docs and the 0.84.1 generator; §5.6's `grep` and the device run prove it |
| The ObjC++ adapter and Swift core compiling, with no bridging header (§5.6) | ✅ `swiftc -typecheck`, and `clang -fsyntax-only` with C++ modules off (§5.6); a full Xcode build has not been run |
| ESLint over `specs/*.ts`; `pod install` and Gradle codegen over a root `specs/` next to `src/` | not run — the codegen CLIs were (§5.3); run `yarn lint` and both builds |

A spec codegen cannot parse is its own red: `pod install` and the Gradle build fail on it; §5.3 has a faster check.

**(d) The device run is part of green.** CI compiles no native code. Build and exercise the module on the iOS simulator and the Android emulator in the same PR — parity is the rule: a module ships on both platforms, or the PR says what the other one gets instead.

## 5. Build it yourself: `NativeAppInfo`

`NativeAppInfo` replaces the ten constant getters the app uses from `react-native-device-info` and fixes the `uniqueId` bug. Names the later phases reuse: specs in `specs/Native<Name>.ts`, one codegen library `DzzloOmsSpec`, generated Java in `in.vsyst.dzzlooms.specs`, JS facades in `src/native/`. Prettier will reflow the compact code below; the content is what matters.

### 5.1 What it replaces

| Getter (device-info 15.0.2) | Live callers | Key | iOS | Android |
| --- | --- | --- | --- | --- |
| `getApplicationName` | `createApi.js:11` | `appName` | `CFBundleDisplayName`, else `CFBundleName` | application label |
| `getVersion` | `createApi.js:12`, `Settings/index.js:38`, `Login.js:731`, `Help/index.js:56`, `helpers/OneSignal/index.js:45` | `version` | `CFBundleShortVersionString` | `versionName` |
| `getBuildNumber` | `createApi.js:13`, `Settings:39`, `Login:732` | `buildNumber` | `CFBundleVersion` | `versionCode` (`longVersionCode` on API 28+) |
| `getSystemVersion` | `createApi.js:14`, `Settings:40`, `Login:733` | `systemVersion` | `UIDevice.systemVersion` | `Build.VERSION.RELEASE` |
| `getDeviceType` | `createApi.js:15` | `deviceType` | phone → `Handset`, pad → `Tablet` | `smallestScreenWidthDp` ≥ 600 → `Tablet`, else `Handset` |
| `getDeviceId` | `createApi.js:16` | `deviceId` | machine code (`uname`; `SIMULATOR_MODEL_IDENTIFIER` on the simulator) | `Build.BOARD` |
| `getBrand` | `createApi.js:17` | `brand` | `"Apple"` | `Build.BRAND` |
| `getUniqueId` | `createApi.js:18` | `uniqueId` | `identifierForVendor` | `Settings.Secure.ANDROID_ID` |
| `getSystemName` | `createApi.js:19` | `systemName` | `UIDevice.systemName` | `"Android"` |
| `getModel` | `Settings:41`, `Login:734` | `model` | machine code | `Build.MODEL` |

The Android column, and the iOS sources for name, versions, brand and machine code, match what device-info itself reads (`RNDeviceModule.java:249-278`, `RNDeviceInfo.m`). Two differences are deliberate — say both in the PR:

- **`model` on iOS.** device-info turns the machine code into a marketing name from a table of about 165 codes (`RNDeviceInfo.m`, counted 2026-09-30) that someone must extend every September. The API never receives `model` — only the Settings line (`Settings/index.js:204-205`) and the Login "App Info" alert show it — so `NativeAppInfo` returns the raw code. If the team wants names, copy a table into `AppInfoCore.swift` as data, with a test per device.
- **`uniqueId`.** device-info's iOS value is an ID it keeps in the Keychain, falling back to user defaults, then `identifierForVendor`, then a random UUID (`DeviceUID.m`). The header has only ever carried `{}`, so nothing on the API depends on it; `NativeAppInfo` uses `identifierForVendor` and `ANDROID_ID`. If the API later needs an ID with a particular lifetime, decide it with the API team — Keychain storage is [[09-phase-9-security-privacy-and-release]]'s subject.

`deviceType` keeps the two values this app can meet (`TARGETED_DEVICE_FAMILY = "1,2"`) and says `unknown` otherwise; device-info also knows `Tv`, `Desktop` and `Headset`.

### 5.2 Red 1 — the bug, at Tier 2

`createApi.js:10-20` builds the `meta` header once, at import, from nine getters. In device-info 15 `getUniqueId()` returns a `Promise<string>` (`privateTypes.d.ts:115-116`), and `JSON.stringify` of a Promise is `{}`, so every request has sent `"uniqueId":{}`. The Tier 2 suite asserts only `appName` and `deviceOS` (`auth.endpoints.msw.test.js:93-95`). Pin the symptom at the lowest layer that shows it — add to its "sends x-api-key, Bearer token, x-co-id and device meta headers" case:

```js
    // Every meta field is a real string: a Promise serialises to {} (device-info
    // v15 getUniqueId). The [key, type] pair names the culprit when it fails.
    for (const [key, value] of Object.entries(meta)) {
      expect([key, typeof value]).toEqual([key, 'string']);
    }
```

Red today: device-info's shipped mock makes `getUniqueId` a resolved Promise. The library-first green is one line — `uniqueId: DeviceInfo.getUniqueIdSync()` — a fine interim if `NativeAppInfo` is weeks away. The test stays either way.

### 5.3 The contract

`specs/NativeAppInfo.ts` — the only TypeScript you add. The file name must start with `Native`; `getConstants` is codegen's special method for constants:

```ts
import type {TurboModule} from 'react-native';
import {TurboModuleRegistry} from 'react-native';

export interface Spec extends TurboModule {
  getConstants(): {
    appName: string; version: string; buildNumber: string;
    systemName: string; systemVersion: string;
    brand: string; model: string; deviceId: string; deviceType: string;
    uniqueId: string;
  };
}

export default TurboModuleRegistry.getEnforcing<Spec>('NativeAppInfo');
```

The `codegenConfig` block for `package.json` — one per app, shared by every module you add later:

```json
"codegenConfig": {
  "name": "DzzloOmsSpec",
  "type": "modules",
  "jsSrcsDir": "specs",
  "android": { "javaPackageName": "in.vsyst.dzzlooms.specs" },
  "ios": { "modulesProvider": { "NativeAppInfo": "RCTNativeAppInfo" } }
}
```

`name` becomes the iOS header `<DzzloOmsSpec/DzzloOmsSpec.h>`; `modulesProvider` maps the JS name to the Objective-C class; `javaPackageName` is where the abstract Java class lands. The day the app gains a Fabric component, `type` becomes `"all"`. Source: [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction). Every generated name in this walk-through was checked on 2026-09-30 by running RN 0.84.1's own codegen CLIs, from the app's `node_modules`, on a scratch copy of this spec: iOS gets `@protocol NativeAppInfoSpec <RCTBridgeModule, RCTTurboModule>`, `NativeAppInfoSpecJSI` and a `JS::NativeAppInfo::Constants` builder taking the ten keys as `RCTRequired<NSString *>` in spec order, with `getConstants` registered as a synchronous `ObjectKind` method; Android gets `in.vsyst.dzzlooms.specs.NativeAppInfoSpec` with `protected abstract Map<String, Object> getTypedExportedConstants()`. The same first command is a quick parse check that touches neither `ios/` nor `android/`:

```sh
node node_modules/@react-native/codegen/lib/cli/combine/combine-js-to-schema-cli.js \
  "$TMPDIR/dzzlo-schema.json" specs -l DzzloOmsSpec && head -c 300 "$TMPDIR/dzzlo-schema.json"
```

### 5.4 Red 2 — the facade test and the wiring pin

`src/native/__tests__/appInfo.test.js` (Tier 1):

```js
// Tier 1 — the NativeAppInfo facade. The spec is mocked: Jest has no
// __turboModuleProxy, so the real getEnforcing('NativeAppInfo') throws.
jest.mock('../../../specs/NativeAppInfo', () => ({
  __esModule: true, default: { getConstants: jest.fn() },
}));

const NATIVE = { appName: 'Dzzlo OMS', version: '1.79', buildNumber: '104', systemName: 'Android',
  systemVersion: '16', brand: 'google', model: 'Pixel', deviceId: 'board', deviceType: 'Handset',
  uniqueId: 'a1b2c3' };

// A fresh facade and a fresh mock per case: the facade caches its first read.
const load = constants => {
  let facade, spec;
  jest.isolateModules(() => {
    spec = require('../../../specs/NativeAppInfo').default;
    spec.getConstants.mockReturnValue(constants);
    facade = require('../appInfo');
  });
  return { facade, spec };
};

it('hands back the ten native constants, read once', () => {
  const { facade, spec } = load(NATIVE);
  expect(facade.getAppInfo()).toEqual(NATIVE);
  facade.getAppInfo();
  expect(spec.getConstants).toHaveBeenCalledTimes(1);
});
it.each([undefined, null, '', '   ', 42, {}])('reads %p as "unknown"', bad => {
  expect(load({ ...NATIVE, uniqueId: bad }).facade.getAppInfo().uniqueId).toBe('unknown');
});
it('keeps the nine `meta` keys the API has always received', () => {
  expect(load(NATIVE).facade.requestMeta()).toEqual({ appName: 'Dzzlo OMS', version: '1.79',
    buildNumber: '104', systemVersion: '16', deviceType: 'Handset', deviceId: 'board',
    deviceBrand: 'google', uniqueId: 'a1b2c3', deviceOS: 'Android' });
});
```

`src/native/__tests__/appInfo.config.test.js` pins what no import graph protects, in the shape of `firebaseModules.config.test.js`. `readCode` (`src/test/sourceText.js`) strips comments, so `Help/index.js`'s commented-out `DeviceInfo.` lines do not count:

```js
import fs from 'fs';
import path from 'path';
import { readCode } from '../../test/sourceText';

const ROOT = path.resolve(__dirname, '../../..');
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');

it('declares one codegen library, registers the package by hand, mocks the spec', () => {
  expect(JSON.parse(read('package.json')).codegenConfig).toMatchObject({
    name: 'DzzloOmsSpec', type: 'modules', jsSrcsDir: 'specs',
    android: { javaPackageName: 'in.vsyst.dzzlooms.specs' },
    ios: { modulesProvider: { NativeAppInfo: 'RCTNativeAppInfo' } },
  });
  expect(read('android/app/src/main/java/in/vsyst/dzzlooms/MainApplication.kt'))
    .toMatch(/^\s*add\(NativeAppInfoPackage\(\)\)/m); // a commented-out line does not count
  expect(read('jest.setup.js')).toContain("jest.mock('./specs/NativeAppInfo'");
});
it.each(['src/store/apis/createApi.js', 'src/screens/Common/Settings/index.js',
  'src/screens/Login/AuthNavigator/Login.js', 'src/screens/Common/Help/index.js',
  'src/helpers/OneSignal/index.js'])('%s reads the facade, not device-info', rel => {
  expect(readCode(path.join(ROOT, rel))).not.toContain('react-native-device-info');
});
```

Run `APP_ENV=testing npx jest appInfo`: both files red, for the right reasons (no `../appInfo`, no `codegenConfig`). The facade test was run on 2026-09-30 with the app's Jest 30 and RN preset in a scratch copy: red with `Cannot find module '../appInfo'`, 8 of 8 green with §5.8's facade, and each of exercise 7.3's three mutations turns it red.

### 5.5 Red 3 — the native unit tests

**iOS — add the first test target.** (1) Xcode → File → New → Target… → iOS → **Unit Testing Bundle**, named `dzzlo_oms_appTests`, Swift, **no host application**; if Xcode offers a choice of testing system, pick XCTest. (2) Set its iOS Deployment Target to 15.1 and Swift Language Version to 5, matching the app. (3) Add it to the shared scheme's Test action (Product → Scheme → Edit Scheme… → Test → +). (4) In §5.6 tick **both** targets for `AppInfoCore.swift`: the bundle compiles its own copy — no host app, no pods, no Firebase start-up inside a unit test. (Hosting the app and using `@testable import dzzlo_oms_app` pulls the app's pods into the test build; untried here.)

`ios/dzzlo_oms_appTests/AppInfoCoreTests.swift`:

```swift
import UIKit
import XCTest

final class AppInfoCoreTests: XCTestCase {
  private func facts(_ idiom: UIUserInterfaceIdiom = .phone, vendorId: UUID? = UUID()) -> DeviceFacts {
    DeviceFacts(systemName: "iOS", systemVersion: "27.0", idiom: idiom, machine: "iPhone99,9", vendorId: vendorId)
  }

  func testFillsEveryKeyAndNeverLeavesUniqueIdEmpty() {
    let v = AppInfoCore.values(info: [:], device: facts(vendorId: nil))
    XCTAssertEqual(Set(v.keys), ["appName", "version", "buildNumber", "systemName", "systemVersion",
                                 "brand", "model", "deviceId", "deviceType", "uniqueId"])
    XCTAssertEqual(v["uniqueId"], "unknown")
  }

  func testMapsTheIdiomToTheDeviceTypeTheApiKnows() {
    let type = { (idiom: UIUserInterfaceIdiom) in AppInfoCore.values(info: [:], device: self.facts(idiom))["deviceType"] }
    XCTAssertEqual([type(.phone), type(.pad), type(.tv)], ["Handset", "Tablet", "unknown"])
  }
}
```

```sh
xcrun simctl list devices available | grep 'iPhone 17e'      # two exist on iOS 27.0 — copy one UDID
xcodebuild test -workspace ios/dzzlo_oms_app.xcworkspace -scheme dzzlo_oms_app \
  -only-testing:dzzlo_oms_appTests -destination 'platform=iOS Simulator,id=<UDID>'
```

**Android — add JUnit.** In `android/app/build.gradle` → `dependencies { }`: `testImplementation("junit:junit:4.13.2")`, RN's own version. Then `android/app/src/test/java/in/vsyst/dzzlooms/appinfo/AppInfoCoreTest.kt`:

```kotlin
package `in`.vsyst.dzzlooms.appinfo

import org.junit.Assert.assertEquals
import org.junit.Test

class AppInfoCoreTest {
  private val facts = AppFacts(appName = "Dzzlo OMS", versionName = "1.79", versionCode = 104L, release = "16",
    brand = "google", model = "Pixel", board = "board", smallestWidthDp = 411, androidId = null)

  @Test fun fillsEveryKeyAndNeverLeavesUniqueIdEmpty() {
    val v = AppInfoCore.values(facts)
    assertEquals(setOf("appName", "version", "buildNumber", "systemName", "systemVersion",
      "brand", "model", "deviceId", "deviceType", "uniqueId"), v.keys)
    assertEquals(listOf("unknown", "104"), listOf(v["uniqueId"], v["buildNumber"]))
  }

  @Test fun smallestWidthDecidesHandsetOrTablet() {
    val type = { dp: Int -> AppInfoCore.values(facts.copy(smallestWidthDp = dp))["deviceType"] }
    assertEquals(listOf("unknown", "Handset", "Tablet"), listOf(type(0), type(599), type(600)))
  }
}
```

```sh
cd android && ./gradlew :app:testDebugUnitTest --tests '*AppInfoCoreTest'
```

Both suites fail to compile — `AppInfoCore` does not exist yet. That is the one time a build failure counts as red; from the next test on, red means a failing assertion. **Robolectric** (`testImplementation("org.robolectric:robolectric:4.15.1")`) is only needed to test the code that *reads* Android — the module shell — and building a `ReactApplicationContext` under it is unverified. The safe fallback is the one taken here: no decisions in the shell, which the device run and the generated spec's debug check (§5.9) cover.

### 5.6 Green, iOS — Swift core behind an Objective-C++ adapter

Create `ios/dzzlo_oms_app/AppInfo/` and add three files (right-click the `dzzlo_oms_app` group → Add Files…). Target membership: `AppInfoCore.swift` → app **and** `dzzlo_oms_appTests`; `RCTNativeAppInfo.mm` → app; the `.h` → none.

`AppInfoCore.swift` — the logic, and the only Swift:

```swift
import Foundation
import UIKit

/// What the device says about itself, as plain values.
struct DeviceFacts {
  let systemName: String, systemVersion: String, idiom: UIUserInterfaceIdiom
  let machine: String, vendorId: UUID?
}

/// The ten NativeAppInfo constants. `values` decides (XCTest covers it); `current` only gathers facts.
public final class AppInfoCore: NSObject {
  static let unknown = "unknown"

  static func values(info: [String: Any], device: DeviceFacts) -> [String: String] {
    func text(_ value: Any?) -> String {
      guard let s = value as? String, !s.trimmingCharacters(in: .whitespaces).isEmpty else { return unknown }
      return s
    }
    let deviceType = [UIUserInterfaceIdiom.phone: "Handset", .pad: "Tablet"][device.idiom] ?? unknown
    return ["appName": text(info["CFBundleDisplayName"] ?? info["CFBundleName"]),
            "version": text(info["CFBundleShortVersionString"]),
            "buildNumber": text(info["CFBundleVersion"]),
            "systemName": text(device.systemName), "systemVersion": text(device.systemVersion),
            "brand": "Apple", "model": text(device.machine), "deviceId": text(device.machine),
            "deviceType": deviceType, "uniqueId": device.vendorId?.uuidString ?? unknown]
  }

  /// UIKit, so main thread only: the adapter calls this from -initialize, which RN runs on the main queue.
  @MainActor
  @objc public static func current() -> [String: String] {
    let device = UIDevice.current
    return values(info: Bundle.main.infoDictionary ?? [:],
                  device: DeviceFacts(systemName: device.systemName, systemVersion: device.systemVersion,
                                      idiom: device.userInterfaceIdiom, machine: machineCode(),
                                      vendorId: device.identifierForVendor))
  }

  static func machineCode() -> String {
    #if targetEnvironment(simulator)
    if let code = ProcessInfo.processInfo.environment["SIMULATOR_MODEL_IDENTIFIER"] { return code }
    #endif
    var system = utsname()
    uname(&system)
    return withUnsafePointer(to: &system.machine) {
      $0.withMemoryRebound(to: CChar.self, capacity: 1) { String(cString: $0) }
    }
  }
}
```

`RCTNativeAppInfo.h` — import it only from `.mm` files; the generated spec header refuses plain Objective-C (`#error This file must be compiled as Obj-C++`):

```objc
#import <Foundation/Foundation.h>
#import <DzzloOmsSpec/DzzloOmsSpec.h>

NS_ASSUME_NONNULL_BEGIN
@interface RCTNativeAppInfo : NSObject <NativeAppInfoSpec>
@end
NS_ASSUME_NONNULL_END
```

`RCTNativeAppInfo.mm` — the adapter: conforms to the generated protocol, reads once, forwards:

```objc
#import "RCTNativeAppInfo.h"

#import <React/RCTInitializing.h>
// dzzlo_oms_app-Swift.h also declares AppDelegate.swift's ReactNativeDelegate, whose
// superclass lives here — and the header only @imports it when modules are enabled.
#import <React_RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>
#import "dzzlo_oms_app-Swift.h"

@interface RCTNativeAppInfo () <RCTInitializing>
@end

@implementation RCTNativeAppInfo {
  facebook::react::ModuleConstants<JS::NativeAppInfo::Constants> _constants;
}

+ (NSString *)moduleName { return @"NativeAppInfo"; }
// UIDevice is main-thread API. With YES, RN creates this module and calls -initialize
// on the main queue. Never read UIKit in -init: the generated provider map also
// creates one instance with [klass new], off the main thread.
+ (BOOL)requiresMainQueueSetup { return YES; }

- (void)initialize
{
  NSDictionary<NSString *, NSString *> *v = [AppInfoCore current];
  // C++20 designated initialisers: keep the spec's field order.
  _constants = facebook::react::typedConstants<JS::NativeAppInfo::Constants>({
      .appName = v[@"appName"], .version = v[@"version"], .buildNumber = v[@"buildNumber"],
      .systemName = v[@"systemName"], .systemVersion = v[@"systemVersion"], .brand = v[@"brand"],
      .model = v[@"model"], .deviceId = v[@"deviceId"], .deviceType = v[@"deviceType"],
      .uniqueId = v[@"uniqueId"],
  });
}

- (facebook::react::ModuleConstants<JS::NativeAppInfo::Constants>)constantsToExport { return _constants; }
- (facebook::react::ModuleConstants<JS::NativeAppInfo::Constants>)getConstants { return _constants; }

- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:(const facebook::react::ObjCTurboModule::InitParams &)params
{ return std::make_shared<facebook::react::NativeAppInfoSpecJSI>(params); }

@end
```

`requiresMainQueueSetup` + `initialize` + `typedConstants` is RN core's own pattern — `React/CoreModules/RCTPlatform.mm` reads `UIDevice` exactly this way. In 0.84.1's `RCTTurboModuleManager.mm` a module whose `+requiresMainQueueSetup` returns YES is created, and its `-initialize` called, on the main queue, while the generated `RCTModuleProviders.mm` makes its own provider instance with `[klass new]` on first lookup — which is why nothing touches UIKit in `-init`. No `RCT_EXPORT_MODULE`: registration comes from `package.json`.

**The bridging header — skipped on purpose.** RN's Swift guide adds `<App>-Bridging-Header.h` importing `<React-RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>` and calls it "required for app targets". `AppInfoCore.swift` needs nothing from Objective-C, and in this repo that header exists twice: a source copy (`Pods/Headers/Public/React-RCTAppDelegate/`, linked into `node_modules/react-native`) and the prebuilt copy behind `AppDelegate.swift`'s `import React_RCTAppDelegate` (verified 2026-09-30). The adapter imports the prebuilt one so only one definition is ever seen. Add a bridging header the day Swift needs an Objective-C type, pointing at the same prebuilt path. **Checked 2026-09-30, outside the repo:** `swiftc -typecheck` passes `AppInfoCore.swift` and its XCTest in Swift 5 mode against the iOS 15.1 simulator SDK, and the emitted header exports `+ (NSDictionary<NSString *, NSString *> *)current`; `clang -fsyntax-only` with C++ modules off passes this `.h`/`.mm` against the Pods' public headers, a scratch copy of the generated spec header and the real `dzzlo_oms_app-Swift.h` with `AppInfoCore` added; drop the explicit `React_RCTAppDelegate` import and the same check fails with "cannot find interface declaration for 'RCTDefaultReactNativeFactoryDelegate', superclass of 'ReactNativeDelegate'". The modules-on configuration Xcode may use could not be reproduced outside Xcode, so a full Xcode build and the device run are still the proof. Source: [RN: Use Swift in your Module](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift).

Regenerate, then check the provider map. `AppDelegate.swift:20` already installs `RCTAppDependencyProvider()`, which serves it, so iOS needs no other registration:

```sh
cd ios && bundle exec pod install
grep -n 'NativeAppInfo' build/generated/ios/ReactCodegen/RCTModuleProviders.mm   # "NativeAppInfo": "RCTNativeAppInfo"
```

### 5.7 Green, Android — Kotlin core, thin module, one registration line

`android/app/src/main/java/in/vsyst/dzzlooms/appinfo/AppInfoCore.kt` — pure Kotlin, no Android types, so plain JUnit runs it:

```kotlin
package `in`.vsyst.dzzlooms.appinfo

/** What the device and the installed package say, as plain values. */
data class AppFacts(
  val appName: String?, val versionName: String?, val versionCode: Long?, val release: String?,
  val brand: String?, val model: String?, val board: String?, val smallestWidthDp: Int,
  val androidId: String?,
)

object AppInfoCore {
  const val UNKNOWN = "unknown"

  fun values(f: AppFacts): Map<String, String> = mapOf(
    "appName" to text(f.appName), "version" to text(f.versionName),
    "buildNumber" to (f.versionCode?.toString() ?: UNKNOWN),
    "systemName" to "Android", "systemVersion" to text(f.release),
    "brand" to text(f.brand), "model" to text(f.model), "deviceId" to text(f.board),
    "deviceType" to when {
      f.smallestWidthDp <= 0 -> UNKNOWN
      f.smallestWidthDp >= 600 -> "Tablet"
      else -> "Handset"
    },
    "uniqueId" to text(f.androidId),
  )

  private fun text(value: String?): String = if (value.isNullOrBlank()) UNKNOWN else value
}
```

`NativeAppInfoModule.kt` — extends the generated `NativeAppInfoSpec`, reads the platform, lets the core decide. `Map<String, Any>` is the return type RN core's own Kotlin modules use for `getTypedExportedConstants`:

```kotlin
package `in`.vsyst.dzzlooms.appinfo

import android.os.Build
import android.provider.Settings
import com.facebook.react.bridge.ReactApplicationContext
import `in`.vsyst.dzzlooms.specs.NativeAppInfoSpec

class NativeAppInfoModule(reactContext: ReactApplicationContext) : NativeAppInfoSpec(reactContext) {
  override fun getName() = NAME
  override fun getTypedExportedConstants(): Map<String, Any> {
    val context = reactApplicationContext
    val pm = context.packageManager
    @Suppress("DEPRECATION")
    val info = runCatching { pm.getPackageInfo(context.packageName, 0) }.getOrNull()
    val code = info?.let {
      if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) it.longVersionCode
      else @Suppress("DEPRECATION") it.versionCode.toLong()
    }
    return AppInfoCore.values(AppFacts(
      appName = runCatching { context.applicationInfo.loadLabel(pm).toString() }.getOrNull(),
      versionName = info?.versionName, versionCode = code, release = Build.VERSION.RELEASE,
      brand = Build.BRAND, model = Build.MODEL, board = Build.BOARD,
      smallestWidthDp = context.resources.configuration.smallestScreenWidthDp,
      androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID),
    ))
  }

  companion object { const val NAME = "NativeAppInfo" }
}
```

`NativeAppInfoPackage.kt` — the documented `BaseReactPackage` shape ([Android guide](https://reactnative.dev/docs/turbo-native-modules-android)); RN 0.84.1's `ReactModuleInfo` takes exactly these six arguments:

```kotlin
package `in`.vsyst.dzzlooms.appinfo

import com.facebook.react.BaseReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.module.model.ReactModuleInfo
import com.facebook.react.module.model.ReactModuleInfoProvider

class NativeAppInfoPackage : BaseReactPackage() {
  override fun getModule(name: String, reactContext: ReactApplicationContext): NativeModule? =
    if (name == NativeAppInfoModule.NAME) NativeAppInfoModule(reactContext) else null

  override fun getReactModuleInfoProvider() = ReactModuleInfoProvider {
    mapOf(NativeAppInfoModule.NAME to ReactModuleInfo(
      name = NativeAppInfoModule.NAME, className = NativeAppInfoModule.NAME,
      canOverrideExistingModule = false, needsEagerInit = false,
      isCxxModule = false, isTurboModule = true,
    ))
  }
}
```

`MainApplication.kt` — in-app modules are not autolinked, so register by hand where the template left its placeholder:

```kotlin
import `in`.vsyst.dzzlooms.appinfo.NativeAppInfoPackage
// …
        PackageList(this).packages.apply {
          add(NativeAppInfoPackage())
        },
```

```sh
cd android && ./gradlew generateCodegenArtifactsFromSchema
ls app/build/generated/source/codegen/java/in/vsyst/dzzlooms/specs/    # NativeAppInfoSpec.java
```

The JNI half needs nothing from you: RN's `ReactNative-application.cmake` builds app-level codegen into `libappmodules.so` whenever `generated/source/codegen/jni/CMakeLists.txt` exists. (The three Kotlin files above compile against react-android 0.84.1 — §4's table.)

### 5.8 Green, JavaScript — facade, global mock, callers

`src/native/appInfo.js`:

```js
/**
 * App and device constants from the NativeAppInfo Turbo Module (specs/NativeAppInfo.ts),
 * read once and cached for the life of the runtime. Every value is a non-empty string;
 * anything else reads 'unknown', so the `meta` header can never carry {} again.
 * Screens import this file, never the spec.
 */
import NativeAppInfo from '../../specs/NativeAppInfo';

export const UNKNOWN = 'unknown';
const KEYS = ['appName', 'version', 'buildNumber', 'systemName', 'systemVersion',
  'brand', 'model', 'deviceId', 'deviceType', 'uniqueId'];
const asText = value => (typeof value === 'string' && value.trim() !== '' ? value : UNKNOWN);
let cached = null;

export const getAppInfo = () => {
  if (cached === null) {
    const raw = NativeAppInfo.getConstants() ?? {};
    cached = Object.freeze(Object.fromEntries(KEYS.map(key => [key, asText(raw[key])])));
  }
  return cached;
};

/** The `meta` header: the nine keys createApi.js has always sent. */
export const requestMeta = () => {
  const i = getAppInfo();
  return {
    appName: i.appName, version: i.version, buildNumber: i.buildNumber,
    systemVersion: i.systemVersion, deviceType: i.deviceType, deviceId: i.deviceId,
    deviceBrand: i.brand, uniqueId: i.uniqueId, deviceOS: i.systemName,
  };
};
```

`jest.setup.js`, beside the other native mocks:

```js
// NativeAppInfo — our own Turbo Module (specs/NativeAppInfo.ts). Jest has no
// __turboModuleProxy, so without this every suite importing createApi throws.
jest.mock('./specs/NativeAppInfo', () => ({
  __esModule: true,
  default: { getConstants: jest.fn(() => ({
    appName: 'Dzzlo OMS', version: '0.0.0-jest', buildNumber: '0', systemName: 'jest',
    systemVersion: '0', brand: 'jest', model: 'jest', deviceId: 'jest',
    deviceType: 'Handset', uniqueId: 'jest-unique-id' })) },
}));
```

`src/store/apis/createApi.js` — the header reads the facade at request time instead of nine getters at import:

```diff
-import DeviceInfo from 'react-native-device-info';
+import { requestMeta } from '../../native/appInfo';
 …
-// Cache static device info at module level (these values never change at runtime)
-const STATIC_DEVICE_INFO = { appName: DeviceInfo.getApplicationName(), … };
 …
-    headers.set('meta', JSON.stringify(STATIC_DEVICE_INFO));
+    headers.set('meta', JSON.stringify(requestMeta()));
```

The other four callers swap their import for `getAppInfo()` — from `../../../native/appInfo` in the three screens, `../../native/appInfo` in `helpers/OneSignal` — e.g. Settings: `const { version: versional, buildNumber, systemVersion, model: deviceName } = getAppInfo();`. The `react-native-device-info` package and its `jest.setup.js` mock stay until [[02-phase-2-dependency-diet]] §4.3 removes them, because three dead files still import it. `yarn test`: every red is green.

### 5.9 Build and look

```sh
yarn ios        # APP_ENV=testing; or Xcode on the iPhone 17e simulator (iOS 27.0)
yarn android    # APP_ENV=testing; the Pixel 10 Pro Fold AVD
```

On both platforms, with the old build and the new one:

- **Login screen, no sign-in:** tap the `v1.79` text (`BetaUserComponent`, `Login.js:680`, hidden while the keyboard is up) — each tap opens an "App Info" alert: `v<version> (<build>) | <os> <osVersion> | <model>`, plus the env line outside production. Everything should match the device-info build except `model` on iOS (now the machine code, §5.1).
- **Settings** (signed in — use an email identifier for the OTP): the same line, `Settings/index.js:204-205`.
- **The Android debug guard, as a mutation smoke:** drop `"uniqueId"` from `AppInfoCore.values`, rebuild debug, open the app. The generated spec's `getConstants()` should throw `IllegalStateException: Native Module doesn't fill in constants: [uniqueId]` — its check runs when `ReactBuildConfig.DEBUG` (or `IS_INTERNAL_BUILD`) is true, which a debug build is expected to set (not yet observed here). A native red for free. Put the key back.

The header's shape is proven by the Tier 2 test; the device run proves the native values are real. Record both platforms in the PR, keep screenshots and logs out of the repos, and commit nothing without the user's word — red commit `test(native/app-info): … (red)`, then green, then the mutation smokes listed.

## 6. After the upgrade to 0.87

> **After the upgrade to 0.87:** what changes for this walk-through — and nothing else does.
> - **Jest preset.** From 0.85 the preset is its own package: `preset: 'react-native'` → `preset: '@react-native/jest-preset'` (0.87: it "must be consumed as package"). Re-check the two paths the app borrows from the old location — `react-native/jest/resolver.js` (`jest.resolver.js:14`) and `react-native/jest/assetFileTransformer.js` (`jest.config.js:15-17`). The spec mocks are path mocks and do not change.
> - **Android.** 0.87 supports AGP 9: compileSdk and buildTools 37, `minCompileSdk` 34, Kotlin 2.0+ (bundled 2.2.0), and two required opt-outs in `gradle.properties` — `android.builtInKotlin=false`, `android.newDsl=false` ("Starting from AGP 10.x these opt outs will be removed"). The module, the package and the `MainApplication.kt` line use only the documented surface; the `testImplementation` line is untested on AGP 9.
> - **iOS, only if you opt into SwiftPM** (experimental, "Do not use it in production yet"; CocoaPods stays the default): bare angle includes must become framework-style, `#import <React/…>`. `<React/RCTInitializing.h>` already is; re-check `<DzzloOmsSpec/DzzloOmsSpec.h>` and `<React_RCTAppDelegate/…>` — not verified under SwiftPM.
> - **TypeScript.** The Strict TypeScript API becomes the default and deep imports (`react-native/Libraries/*`) are type errors. The spec imports only `TurboModule` and `TurboModuleRegistry` from the package root — nothing to do.
> - **Flags.** 0.87 removes the `useTurboModules` flag and deprecates `RCTTurboModuleEnabled()` / `RCTEnableTurboModule()`; this module uses none of them.
> - **Node.** The floor rises to 22.13.0; `engines` says `>= 22.11.0`.
> - **Expo.** 0.87 pairs with no Expo SDK; the optional track in §2 stays closed.
>
> Sources: [RN 0.85 blog](https://reactnative.dev/blog/2026/04/07/react-native-0.85), [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87), [AGP 9 RFC #1006](https://github.com/react-native-community/discussions-and-proposals/pull/1006).

## 7. Exercises

**7.1 — Read the glue before you write against it.** Copy `specs/NativeAppInfo.ts` into a folder under `$TMPDIR`, run §5.3's schema command there, then `node node_modules/react-native/scripts/generate-specs-cli.js -p ios -s <schema> -o <out>/ios -n DzzloOmsSpec -t modules` and the same with `-p android -j in.vsyst.dzzlooms.specs`. Write down the protocol name, the JSI class, the Java package and both `IllegalStateException` messages. _Output: a short note in your scratch folder._

**7.2 — Watch `getEnforcing` throw.** Comment out the global mock in `jest.setup.js`, run `APP_ENV=testing npx jest auth.endpoints`, copy the invariant message, restore the mock. _Output: the failing run, then green._

**7.3 — Mutation-smoke the facade.** Three breaks, one at a time: `asText` returns its input; the cache is removed; `deviceBrand` reads `i.model`. Each must turn a specific test red. _Output: three red runs, recorded for the PR._

**7.4 — Native reds on purpose.** Map `.pad` to `"Handset"` in Swift and `>= 600` to `> 600` in Kotlin; run §5.5's two commands. _Output: one failing XCTest and one failing JUnit test, then both green._

**7.5 — Parity on devices.** Run §5.9 on the iPhone 17e simulator and the Android AVD, old build and new. Tabulate the four values the alert shows, per platform, before and after. _Output: a two-platform table in the PR; the only difference should be iOS `model`._

**7.6 — The free native test.** Do §5.9's Android debug-guard smoke, note the exact message, and find the line that throws it in the generated `NativeAppInfoSpec.java`. _Output: the message and the file line._

