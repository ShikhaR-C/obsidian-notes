# React Native native modules in 2026 — technical brief for dzzlo_oms_app (RN 0.84.1, New Architecture, JS-first)

Research date: 2026-09-29. Scope: a bare React Native CLI app with only the New Architecture, built by a JS-first team working test-first. Target app: `dzzlo_oms_app` (react-native 0.84.1). The newest React Native release at research time is **0.87 (2026-08-11)**.

Source conventions:
- Web sources are linked inline.
- **[local]** marks a fact verified on the dev machine on 2026-09-29, by reading files in `v1_79/dzzlo_oms_app` (including the installed RN 0.84.1 under `node_modules`) or by running `xcodebuild -version` / `swift --version`.
- For RN source files, the matching upstream path on the `0.84-stable` branch is linked for reference. Those GitHub URLs were **not fetched**; the quoted text comes from the installed 0.84.1 copy.
- The "quotes" from web pages were extracted by a fetch tool that summarises. They are verbatim as returned, but punctuation may differ slightly from the live page.

---

## 1. What does RN 0.84 (and 0.85–0.87) require for a local (in-app) Turbo Module?

### Takeaway
On RN 0.84 a local Turbo Module has four parts:
1. One typed spec file, `specs/NativeFoo.ts`. Use TypeScript even in a JS app; Flow also works.
2. One `codegenConfig` block in the app's `package.json`.
3. An iOS class in **Objective-C++**. Swift is officially supported only behind a thin ObjC++ adapter; pure Swift is not. It is registered automatically through `ios.modulesProvider`.
4. A Kotlin class that extends the generated spec. It must be **registered by hand** through a `BaseReactPackage` in `MainApplication.kt`.

JS reaches the module with `TurboModuleRegistry.getEnforcing`. Typed events use `CodegenTypes.EventEmitter<T>`. Sync methods run on the JS thread; void and Promise methods are dispatched to a native queue.

### Cited Findings

**Release and architecture context**
- RN release dates: 0.80 = 2025-06-12, 0.81 = 2025-08-12, 0.82 = 2025-10-08, 0.83 = 2025-12-10, 0.84 = 2026-02-11 ("Hermes V1 by Default"), 0.85 = 2026-04-07 ("New Animation Backend, New Jest Preset Package"), 0.86 = 2026-06-11 ("no breaking changes"), 0.87 = 2026-08-11 ("Strict TypeScript API, Metro Update, Swift Package Manager, AGP 9 Support") — [RN blog index](https://reactnative.dev/blog)
- The app is on `react-native@0.84.1` and `react@19.2.3`. Its `android/gradle.properties` has `newArchEnabled=true` and `hermesEnabled=true`. It has no `codegenConfig` yet — [local] `dzzlo_oms_app/package.json`, `android/gradle.properties`
- Since 0.82 the New Architecture is the only one: setting `newArchEnabled=false` or `RCT_NEW_ARCH_ENABLED=0` "will be ignored and your app will still run using the New Architecture" — [RN 0.82 blog](https://reactnative.dev/blog/2025/10/08/react-native-0.82)
- 0.87 removed the `useTurboModules` feature flag (TurboModules are always on) and deprecated `RCTTurboModuleEnabled()` / `RCTEnableTurboModule()` — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87)
- 0.84 deprecated `TurboModuleProviderFunctionType` — [RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84)
- The official guides live under "Native Platform → Modules → Android and iOS / Cross-Platform with C++ / Advanced Topics" and "Components → Android & iOS / Advanced Topics". Docs version at research time: 0.87 — [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction)

**Spec file (JS/TS side)**
- The spec file name must start with `Native` (for example `specs/NativeLocalStorage.ts`). "Both TypeScript and Flow are supported." The spec extends `TurboModule` and exports `TurboModuleRegistry.getEnforcing<Spec>('NativeLocalStorage')`. `getEnforcing` throws if the module is missing; `TurboModuleRegistry.get<T>()` returns `null` instead — [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction). Verbatim spec:
  ```ts
  import type {TurboModule} from 'react-native';
  import {TurboModuleRegistry} from 'react-native';
  export interface Spec extends TurboModule {
    setItem(value: string, key: string): void;
    getItem(key: string): string | null;
    removeItem(key: string): void;
    clear(): void;
  }
  export default TurboModuleRegistry.getEnforcing<Spec>('NativeLocalStorage');
  ```
- Naming rule from the codegen docs: "Turbo Native Modules require that the spec files are prefixed with `Native`… Native Fabric Components require that the spec files are suffixed with `NativeComponent`" — [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen)
- The codegen in 0.84.1 finds spec files with the basename regex `/^(Native.+|.+NativeComponent)/`. It picks the parser **by file extension**: `.ts`/`.tsx` use the TypeScript parser, and anything else uses the Flow parser — [local] `@react-native/codegen/lib/cli/combine/combine-utils.js` line 28 and `combine-js-to-schema.js` line 31 (upstream: [combine-js-to-schema.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native-codegen/src/cli/combine/combine-js-to-schema.js))
- RN 0.84.1's generator for the iOS `ReactCodegen` podspec tracks spec files with `-name "Native*.ts" -or -name "*NativeComponent.ts"` — [local] `react-native/scripts/codegen/generate-artifacts-executor/generateReactCodegenPodspec.js` line 68
- RN 0.84.1 exports what a spec needs from the package root:
  - `codegenNativeComponent` and `TurboModuleRegistry` (`index.js` lines 198 and 328)
  - `export type {TurboModule}` (`index.js.flow` line 447)
  - the `CodegenTypes` namespace: `export * as CodegenTypes from '../Libraries/Types/CodegenTypesNamespace'` (`types/index.d.ts` line 142)

  Deep imports are therefore unnecessary — [local] `node_modules/react-native/index.js`, `index.js.flow`, `types/index.d.ts`
- In 0.87 the Strict TypeScript API became the default: "Deep imports into internal paths (e.g. `react-native/Libraries/*`) are now a type error" — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87)
- Type mapping from the Appendix table (TS → Android → iOS):

  | TS | Android | iOS |
  |---|---|---|
  | `string` | `String` | `NSString` |
  | `boolean` | `Boolean` | `NSNumber` |
  | `number` | `double` | `NSNumber` |
  | `Object` | `ReadableMap` | untyped dictionary |
  | `Array<T>` | `ReadableArray` | `NSArray` |
  | `Promise<T>` | `com.facebook.react.bridge.Promise` | `RCTPromiseResolveBlock` + `RCTPromiseRejectBlock` |
  | callbacks | `com.facebook.react.bridge.Callback` | `RCTResponseSenderBlock` |

  Unions such as `'SUCCESS'|'FAIL'` are listed too. "Object literals are strongly recommended over plain Objects" — [Appendix](https://reactnative.dev/docs/appendix)

**`codegenConfig` in `package.json`**
- Tutorial form (verbatim):
  ```json
  "codegenConfig": {
    "name": "NativeLocalStorageSpec",
    "type": "modules",
    "jsSrcsDir": "specs",
    "android": { "javaPackageName": "com.nativelocalstorage" },
    "ios": { "modulesProvider": { "NativeLocalStorage": "RCTNativeLocalStorage" } }
  }
  ```
  `ios.modulesProvider` maps the JS module name to the native ObjC class — [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction)
- The reference page documents a second, richer iOS form, `ios.modules.<Name>`, with these fields — [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen):
  - `className` ("This module's ObjC class. Or, if it's a C++-only module, its RCTModuleProvider class")
  - `unstableRequiresMainQueueSetup` ("Initialize this module on the UI Thread, before running any JavaScript")
  - `conformsToProtocols` (`RCTImageURLLoader`, `RCTURLRequestHandler`, `RCTImageDataDecoder`)

  The same page documents `ios.components.<Name>.className`. `type` accepts `modules`, `components` or `all`.
- Both iOS forms are accepted by 0.84.1: `generateRCTModuleProviders.js` reads `config.ios?.modulesProvider` (lines 71–77) and also `annotation.className` from the `modules` form (lines 91–95). RN's own `package.json` uses the `ios.modules.X.unstableRequiresMainQueueSetup` form — [local] `react-native/scripts/codegen/generate-artifacts-executor/generateRCTModuleProviders.js`, `react-native/package.json`
- Generated code locations:
  - Android app: `android/app/build/generated/source/codegen`
  - iOS: `build/generated/ios/`
  - Manual runs: `./gradlew generateCodegenArtifactsFromSchema` (Android) and `node node_modules/react-native/scripts/generate-codegen-artifacts.js --path . --outputPath ios/ --targetPlatform ios` (iOS)

  The docs do not state whether to commit generated code — [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen)

**iOS implementation (Objective-C++)**
- The docs create `RCTNativeLocalStorage.h` and `RCTNativeLocalStorage.mm`. The `.mm` is renamed from `.m` so it compiles as Objective-C++. The key parts:
  - `@interface RCTNativeLocalStorage : NSObject <NativeLocalStorageSpec>`
  - `- (std::shared_ptr<facebook::react::TurboModule>)getTurboModule:(const facebook::react::ObjCTurboModule::InitParams &)params { return std::make_shared<facebook::react::NativeLocalStorageSpecJSI>(params); }`
  - `+ (NSString *)moduleName { return @"NativeLocalStorage"; }`

  Then run `bundle exec pod install` from `ios/` to trigger codegen — [iOS guide](https://reactnative.dev/docs/turbo-native-modules-ios)
- "the `RCT_EXPORT_MODULE` macro is not required anymore, because native modules are registered using the `package.json`" — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift)
- The app's `AppDelegate.swift` (RN 0.84 template shape plus a SceneDelegate) already imports `ReactAppDependencyProvider` and sets `delegate.dependencyProvider = RCTAppDependencyProvider()` — [local] `ios/dzzlo_oms_app/AppDelegate.swift`

**Swift on iOS: officially an adapter, not pure Swift**
- The RN docs page "Use Swift in your Module" exists in versioned docs 0.79–0.87 — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift)
- The page's reason for needing ObjC++: "The core of React Native is mainly written in C++ and the interoperability between Swift and C++ is not great, despite the interoperability layer developed by Apple." — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift)
- The recommended pattern is the **adapter**: business logic in Swift, plus a thin ObjC++ `.mm` that conforms to the generated protocol and forwards calls — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift). The files are:
  - `NativeLocalStorage.swift`, declared as `@objcMembers public class NativeLocalStorage: NSObject` with `public` methods
  - `RCTNativeLocalStorage.h/.mm`, which does `#import "SampleApp-Swift.h"` and forwards, e.g. `- (NSString * _Nullable)getItem:(NSString *)key { return [storage getItemFor:key]; }`
  - `SampleApp-Bridging-Header.h`, "required for app targets; not for library authors", containing `#import <React-RCTAppDelegate/RCTDefaultReactNativeFactoryDelegate.h>`. It is registered under Build Settings → "Objective-C Bridging Header".
- The Swift guide does not mention `use_frameworks!`, module maps or Swift 6 concurrency — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift)
- The app's targets build with `SWIFT_VERSION = 5.0` and have **no** `SWIFT_OBJC_BRIDGING_HEADER` set — [local] `ios/dzzlo_oms_app.xcodeproj/project.pbxproj`

**Android implementation (Kotlin)**
- The module is `class NativeLocalStorageModule(reactContext: ReactApplicationContext) : NativeLocalStorageSpec(reactContext)` with `override fun getName() = NAME` and `companion object { const val NAME = "NativeLocalStorage" }` — [Android guide](https://reactnative.dev/docs/turbo-native-modules-android)
- The package, verbatim:
  ```kotlin
  class NativeLocalStoragePackage : BaseReactPackage() {
    override fun getModule(name: String, reactContext: ReactApplicationContext): NativeModule? =
      if (name == NativeLocalStorageModule.NAME) NativeLocalStorageModule(reactContext) else null
    override fun getReactModuleInfoProvider() = ReactModuleInfoProvider {
      mapOf(NativeLocalStorageModule.NAME to ReactModuleInfo(
        name = NativeLocalStorageModule.NAME, className = NativeLocalStorageModule.NAME,
        canOverrideExistingModule = false, needsEagerInit = false,
        isCxxModule = false, isTurboModule = true))
    }
  }
  ```
  — [Android guide](https://reactnative.dev/docs/turbo-native-modules-android)
- Registration: `PackageList(this).packages.apply { add(NativeLocalStoragePackage()) }` — [Android guide](https://reactnative.dev/docs/turbo-native-modules-android). In the app, that `apply { … }` block sits inside `getDefaultReactHost(context = applicationContext, packageList = PackageList(this).packages.apply { /* add(MyReactNativePackage()) */ })` — [local] `android/app/src/main/java/in/vsyst/dzzlooms/MainApplication.kt`
- Autolinking covers npm packages. In-app modules "must manually register in `MainApplication.java/kt`" — [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction)
- `android.javaPackageName`: "Configure the package name of the Android Java codegen output" — [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen)
- 0.84 removed legacy Android classes, among them:
  - `com.facebook.react.LazyReactPackage`
  - `CxxModuleWrapper`
  - `CallbackImpl`
  - `BridgeDevSupportManager`

  — [RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84)

**C++ Turbo Modules (shared logic)**
- The pure C++ module steps, verbatim code on the page — [Pure C++ modules](https://reactnative.dev/docs/the-new-architecture/pure-cxx-modules):
  1. A spec `specs/NativeSampleModule.ts`.
  2. `codegenConfig` with `"ios": {"modulesProvider": {"NativeSampleModule": "NativeSampleModuleProvider"}}`.
  3. `shared/NativeSampleModule.h/.cpp`, subclassing `NativeSampleModuleCxxSpec<NativeSampleModule>`.
  4. Android: `android/app/src/main/jni/CMakeLists.txt` including `${REACT_ANDROID_DIR}/cmake-utils/ReactNative-application.cmake`, plus `externalNativeBuild { cmake { path "src/main/jni/CMakeLists.txt" } }` in `app/build.gradle`.
  5. An `OnLoad.cpp` `cxxModuleProvider` that returns the module or falls back to `autolinking_cxxModuleProvider(name, jsInvoker)`.
  6. iOS: `NativeSampleModuleProvider : NSObject <RCTModuleProvider>`, whose `getTurboModule:` returns `std::make_shared<facebook::react::NativeSampleModule>(params.jsInvoker)`.
- The same page advises: "Best practice is to wrap specs in a separate file rather than importing directly in your app." — [Pure C++ modules](https://reactnative.dev/docs/the-new-architecture/pure-cxx-modules)
- The C++ language option of create-react-native-library's `turbo-module` template is labelled "Experimental" — [create-react-native-library prompt.ts](https://raw.githubusercontent.com/callstack/react-native-builder-bob/main/packages/create-react-native-library/src/prompt.ts)

**Typed events (`EventEmitter<T>`)**
- Spec: `import type {TurboModule, CodegenTypes} from 'react-native';` … `readonly onKeyAdded: CodegenTypes.EventEmitter<KeyValuePair>;` — [Custom events](https://reactnative.dev/docs/the-new-architecture/native-modules-custom-events)
- iOS: the base class becomes `@interface RCTNativeLocalStorage : NativeLocalStorageSpecBase <NativeLocalStorageSpec>` and the code calls `[self emitOnKeyAdded:@{@"key": key, @"value": value}];` — [Custom events](https://reactnative.dev/docs/the-new-architecture/native-modules-custom-events)
- Android: `emitOnKeyAdded(Arguments.createMap().apply { putString("key", key); putString("value", value) })` — [Custom events](https://reactnative.dev/docs/the-new-architecture/native-modules-custom-events)
- JS: `const sub = NativeLocalStorage?.onKeyAdded(pair => …)` returns an `EventSubscription`; clean up with `sub.remove()` in the effect cleanup — [Custom events](https://reactnative.dev/docs/the-new-architecture/native-modules-custom-events)
- The events page exists in versioned docs 0.79 through 0.87. The page does not state the first RN version that supported the feature — [Custom events](https://reactnative.dev/docs/the-new-architecture/native-modules-custom-events)

**Promises and errors**
- `Promise<T>` maps to `com.facebook.react.bridge.Promise` on Android and `RCTPromiseResolveBlock`/`RCTPromiseRejectBlock` on iOS — [Appendix](https://reactnative.dev/docs/appendix)
- From 0.82 on, "Uncaught promise rejections will now raise `console.error`" (they were previously swallowed because of a bug) — [RN 0.82 blog](https://reactnative.dev/blog/2025/10/08/react-native-0.82)

**Threading and lifecycle**
- "The Native Module infrastructure lazily creates a Native Module the first time it is accessed and it keeps it around whenever the app requires it." `invalidate()` "is the best place to put all the cleanup code" — [Lifecycle](https://reactnative.dev/docs/the-new-architecture/native-modules-lifecycle)
- iOS source, RN 0.84.1 `RCTTurboModule.mm`: "Perform method invocation on a specific queue as configured by the module class. This serves as a backward-compatible support for RCTBridgeModule's methodQueue API. In the future: This methodQueue support may be removed for simplicity and consistency with Android. ObjC module methods will be always be called from JS thread. They may decide to dispatch to a different queue as needed." — [local] (upstream: [RCTTurboModule.mm](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactCommon/react/nativemodule/core/platform/ios/ReactCommon/RCTTurboModule.mm))
- iOS source, RN 0.84.1 `RCTTurboModuleManager.mm` — [local] (upstream: [RCTTurboModuleManager.mm](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactCommon/react/nativemodule/core/platform/ios/ReactCommon/RCTTurboModuleManager.mm)):
  - The invoker runs a call inline when `methodQueue_ == RCTJSThread`; otherwise it calls `dispatch_async(methodQueue_, …)`.
  - It sets `isSyncModule = methodQueue == RCTJSThread`.
  - A legacy invoker only forces `getConstants` onto the main queue (`RCTUnsafeExecuteOnMainQueueSync`) when `requiresMainQueueSetup` is set.
  - The manager also creates a serial `_sharedModuleQueue` named `"com.meta.react.turbomodulemanager.queue"`.
- Android source, RN 0.84.1 `JavaTurboModule.cpp`: `VoidKind` and `PromiseKind` methods go through `nativeMethodCallInvoker_->invokeAsync(…)`, while sync return kinds run inline. RN's queue configuration defines a background thread spec named `"native_modules"` — [local] (upstream: [JavaTurboModule.cpp](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactCommon/react/nativemodule/core/platform/android/ReactCommon/JavaTurboModule.cpp), [ReactQueueConfigurationSpec.kt](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactAndroid/src/main/java/com/facebook/react/bridge/queue/ReactQueueConfigurationSpec.kt))
- Callstack (Oskar Kwaśniewski, 2026-01-19) — [Callstack: threads in Swift TurboModules](https://www.callstack.com/tutorials/working-with-different-threads-in-swift-turbomodules):
  - "Synchronous TurboModule methods run on the JavaScript thread and must be fast"
  - "async methods are dispatched through the TurboModule manager queue"
  - "Never perform long‑running work on the JS or main thread"
  - It demonstrates `DispatchQueue.global().async` → `DispatchQueue.main.async` and resolving promises from a background queue.

**JS side in the running app and in Jest**
- RN 0.84.1 `TurboModuleRegistry.js` — [local] (upstream: [TurboModuleRegistry.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/Libraries/TurboModule/TurboModuleRegistry.js)):
  - `requireModule(name)` first tries `global.__turboModuleProxy(name)`, then falls back to `NativeModules[name]`.
  - `getEnforcing` throws: "`TurboModuleRegistry.getEnforcing(...): '${name}' could not be found. Verify that a module by this name is registered in the native binary.`"

### Inferences
- **Spec language for this JS app:** write specs as `.ts`. Codegen chooses its parser by extension, so a `.js` spec would be parsed as Flow and must carry Flow annotations. The Babel preset already strips TS in Metro and Jest; the app already has one `.ts` file and TypeScript 6 in devDependencies. The official examples are TS-first, and RN's iOS podspec generator only watches `Native*.ts` / `*NativeComponent.ts`. No `tsc` step is needed for the app to build.
- **Registration is asymmetric in an in-app module.**
  - iOS: `codegenConfig.ios.modulesProvider` → generated module-provider map → the `RCTAppDependencyProvider` the AppDelegate already installs. No AppDelegate edit should be needed. This mechanism was inferred from the docs plus the generator source and was not tested end-to-end here.
  - Android: a manual `add(FooPackage())` in `MainApplication.kt`.
  - A local library (section 7) removes the Android manual step through autolinking.
- **Swift path:** the documented Swift path for an app target is `Foo.swift` (`@objcMembers … : NSObject`) + `RCTFoo.h/.mm` + a new bridging header. The generated Swift header will be named after the product module (likely `dzzlo_oms_app-Swift.h`; not verified).
- **Threading rules for the course:**
  - Treat sync methods as JS-thread code and keep them tiny.
  - Put I/O in void or Promise methods, which run off the JS thread.
  - Hop explicitly to the main thread for UIKit or Android `View` work.
  - Do not build on iOS `methodQueue`; RN's own comment marks it as backward-compat and possibly to be removed.
- **Events:** prefer `CodegenTypes.EventEmitter<T>` over the older `NativeEventEmitter` / `RCTEventEmitter` patterns. It is typed and generated on both platforms. The docs do not explicitly deprecate the old way, so this is inference.
- **Single `codegenConfig`:** the app `package.json` has one `codegenConfig`. If the app ever holds both modules and components, use `"type": "all"` with both `modulesProvider` and `componentProvider`.

### Gaps
- The New Architecture pages fetched do not document a reject/error-code convention for Turbo Modules; the legacy native-module pages were not fetched.
- The first RN version that supports `CodegenTypes.EventEmitter` in module specs is not stated on the page; its docs start at 0.79.
- Which thread Android's `nativeMethodCallInvoker` uses in bridgeless mode is inferred from source names (`"native_modules"`) and is not documented.
- Whether any third-party docs claim pure-Swift Turbo Modules now work through Swift–C++ interop was not researched. The official docs say no.

---

## 2. Nitro Modules (Margelo / mrousavy): what they are, maturity, compatibility, when to prefer

### Takeaway
Nitro is a JSI framework with its own TypeScript-driven codegen (`nitrogen`). You write "HybridObjects" directly in Swift or Kotlin with no ObjC++ layer. It shows large micro-benchmark wins over Turbo and Expo modules.

It is still **0.x** (v0.37.1, 2026-08-27, MIT, ~2.0k GitHub stars). It adds a third-party runtime dependency (`react-native-nitro-modules`) and always compiles C++, so every Nitro module ships `.so` files on Android. For a JS-first app with low call volume, the speed does not matter much. The main pull is the Swift/Kotlin-first ergonomics, and the main cost is ecosystem risk.

### Cited Findings
- Nitro is "a framework for building powerful and fast native modules for JS". A Hybrid Object is "a native object in Nitro, implemented in either C++, Swift or Kotlin". Nitrogen is an optional code generator driven by TypeScript interfaces. Swift bridges "directly via Swift <> C++ interop" ("No Objective-C"); Kotlin goes through fbjni with coroutines ("No Java") — [What is Nitro](https://nitro.margelo.com/docs/what-is-nitro)
- Benchmarks, 100,000 calls, from Nitro's own page:

  | Call | Expo Modules | Turbo Modules | Nitro |
  |---|---|---|---|
  | `addNumbers` | 434.85 ms | 115.86 ms | 7.27 ms |
  | `addStrings` | 429.53 ms | 179.02 ms | 29.94 ms |

  The page's caveat: "These benchmarks only compare native method throughput in extreme cases, and do not necessarily reflect real world use-cases." — [Nitro comparison](https://nitro.margelo.com/docs/comparison). A search snippet names the device as iPhone 15 Pro (not re-verified) — [NitroBenchmarks](https://github.com/mrousavy/NitroBenchmarks)
- Nitro's comparison page (vendor-authored) — [Nitro comparison](https://nitro.margelo.com/docs/comparison):
  - Turbo Modules have "No direct Swift support" and "No properties". Every module is a singleton, codegen "cannot resolve imports", and they use `jsi::HostObject`.
  - Expo Modules have "No code-generator" ("all native modules are untyped by default"), "Does not allow JS callbacks to return a value", and Swift "bridges through Objective-C".
  - Nitro uses `jsi::NativeState`, and nitrogen "can properly resolve imports".

  **Contrasting vendor view:** Expo says its API has "similar performance characteristics to React Native's Turbo Modules API" and that "the time spent executing the body of a native method is often orders of magnitude greater than the overhead of the method invocation" — [Expo Modules overview](https://docs.expo.dev/modules/overview/)
- Minimum requirements: "react-native 0.75 or higher", "Xcode 16.4 or higher", "Swift 5.9 or higher", "compileSdkVersion 34 or higher", "ndkVersion 27 or higher". The page says nothing about `use_frameworks!` or Expo — [Nitro minimum requirements](https://nitro.margelo.com/docs/minimum-requirements)
- The app and machine meet these: RN 0.84.1, Xcode 27.0, Swift 6.4, compileSdk 36, NDK 27.1.12297006 — [local] `xcodebuild -version`, `swift --version`, `android/build.gradle`
- Recent releases — [Nitro releases](https://github.com/mrousavy/nitro/releases):
  - **v0.37.1 (2026-08-27)**
  - v0.37.0 (2026-08-20), which moved "Props and ComponentDescriptor into Nitro core via C++ templates" (views)
  - v0.36.5 (2026-07-31), a memory-leak fix for cyclic JVM references
  - v0.36.2 (2026-07-27), "React Native 0.87+ support"
  - There is no 1.0 release.
- Repo: MIT licence, about 2.0k stars. README: "Insanely fast native C++, Swift or Kotlin modules with a statically compiled binding layer to JSI" — [mrousavy/nitro](https://github.com/mrousavy/nitro)
- How to create a Nitro module — [How to build a Nitro Module](https://nitro.margelo.com/docs/getting-started/how-to-build-a-nitro-module):
  - Scaffold with `npx nitrogen@latest init <name>`, `npx create-react-native-library@latest`, or `npx create-nitro-module@latest`.
  - Nitro can be added "manually to your existing library/app".
  - Generated code goes to `nitrogen/generated/`.
  - Libraries depend on `react-native-nitro-modules`, declared as an optional peer dependency.
- Verbatim spec and implementations — [How to build a Nitro Module](https://nitro.margelo.com/docs/getting-started/how-to-build-a-nitro-module):
  ```ts
  export interface Math extends HybridObject<{ ios: 'swift', android: 'kotlin' }> {
    add(a: number, b: number): number
  }
  ```
  ```swift
  class HybridMath : HybridMathSpec { func add(a: Double, b: Double) throws -> Double { return a + b } }
  ```
  ```kotlin
  class HybridMath : HybridMathSpec() { override fun add(a: Double, b: Double): Double { return a + b } }
  ```
- In create-react-native-library, the `nitro-module` ("Type-safe, fast integration for native APIs to JS") and `nitro-view` types use the **`kotlin-swift`** language pair. The `turbo-module` and `fabric-view` types use **`kotlin-objc`** — [create-react-native-library prompt.ts](https://raw.githubusercontent.com/callstack/react-native-builder-bob/main/packages/create-react-native-library/src/prompt.ts)
- `use_frameworks!`: no statement in Nitro's docs. Search results surface Nitro issue #591 ("iOS build error: folly/folly-config.h file not found") and third-party reports of static-framework build problems in mixed setups. These are unverified — [nitro#591](https://github.com/mrousavy/nitro/issues/591)

### Inferences
- **For dzzlo_oms_app:** Nitro is compatible on paper. Each Nitro module adds C++ compilation and `.so` files, which pulls in 16 KB-alignment and NDK concerns (see section 6).
- **Reasons to choose Nitro for a JS-first team:**
  1. The team wants Swift/Kotlin with zero ObjC++.
  2. The API is high-frequency, such as per-frame calls, sensors, or big buffers.
  3. The team wants object-shaped APIs (properties, multiple instances) that Turbo Modules can't express.
- **Reason to stay with Turbo Modules:** it is part of core, adds no dependency, and has the strongest long-term support signal.
- **0.x status:** expect breaking changes between Nitro minors. A tutorial pinned to 0.37.x will age quickly.
- **Packaging:** a Nitro module is naturally a library, either a local library via `create-react-native-library --local` with the `nitro-module` type or a workspace package. That combination is plausible from builder-bob's options but was not tested here.

### Gaps
- Nitro's Jest mocking pattern (HybridObjects are created through `NitroModules.createHybridObject(...)`, not TurboModuleRegistry) was not verified from docs.
- No primary data on Nitro adoption (npm downloads, list of production apps). The "Apps using Nitro" resources page was not fetched.
- Compatibility with `use_frameworks!` (static or dynamic) and with RN 0.84's prebuilt `React.framework` is not documented.

---

## 3. Expo Modules API in a bare (non-Expo) React Native app

### Takeaway
The Expo Modules API has the nicest Swift/Kotlin DSL and a `create-expo-module --local` flow. In a bare app, though, it means installing the `expo` package, with Podfile, Gradle, AppDelegate, Metro and Babel changes.

**Each Expo SDK targets exactly one RN version: SDK 55 → RN 0.83, SDK 56 → RN 0.85, SDK 57 → RN 0.86. No SDK targets RN 0.84.** SDK 56/57 also require iOS 16.4+ and Xcode 26.4+. For dzzlo_oms_app on 0.84.1 (iOS min 15.1) this is not a clean option today; re-evaluate when upgrading RN to 0.85 or 0.86.

### Cited Findings
- SDK ↔ RN table — [Expo SDK versions](https://docs.expo.dev/versions/latest/):

  | Expo SDK | React Native | React | Min iOS | Min Android | Xcode |
  |---|---|---|---|---|---|
  | 57.0.0 | 0.86 | 19.2.3 | 16.4+ | 7+ | 26.4+ |
  | 56.0.0 | 0.85 | 19.2.3 | 16.4+ | 7+ | 26.4+ |
  | 55.0.0 | 0.83 | 19.2.0 | 15.1+ | — | 26.2+ |
  | 54.0.0 | 0.81 | 19.1.0 | 15.1+ | — | 16.1+ |
- "Each Expo SDK release targets a single React Native version. This is typically the latest stable version at the time of the release." and "Packages in the Expo SDK are intended to support the target React Native version for that SDK. Typically, they will not support older versions of React Native." — [Expo SDK versions](https://docs.expo.dev/versions/latest/)
- Installing into a bare app — [Installing Expo modules](https://docs.expo.dev/bare/installing-expo-modules/):
  - Automatic: `npx install-expo-modules@latest`. Caveat: "if your project deviates significantly from a default React Native project, then you need to perform manual installation."
  - Manual: `npm install expo`; add `use_expo_modules!` in the Podfile; `npx pod-install`; set the iOS deployment target to 16.4; point the AppDelegate bundle root at `.expo/.virtual-metro-entry`; use `babel-preset-expo`; extend `expo/metro-config`.
  - The page currently targets RN 0.86 / SDK 57.
- Design goals: "designed to take advantage of modern language features, to be as consistent as possible on both platforms, to require minimal boilerplate, and provide comparable performance characteristics to React Native's Turbo Modules API". "Expo Modules all support the New Architecture" — [Expo Modules overview](https://docs.expo.dev/modules/overview/)
- The DSL, verbatim — [Expo Module API](https://docs.expo.dev/modules/module-api/):
  ```swift
  public class MyModule: Module {
    public func definition() -> ModuleDefinition {
      Name("MyFirstExpoModule")
      Function("hello") { (name: String) in return "Hello \(name)!" }
      AsyncFunction("fetchData") { (url: String) in return "Data from \(url)" }
      Events("onDataReady")
    }
  }
  ```
  The Kotlin version is equivalent (`class MyModule : Module() { override fun definition() = ModuleDefinition { … } }`). JS loads the module with `requireNativeModule`. `Function` runs synchronously on the JS thread. `AsyncFunction` "always returns a Promise" and "runs on a different thread than the JavaScript runtime" unless `.runOnQueue()` is used; thrown exceptions become rejected promises.
- Local module: `npx create-expo-module@latest --local` creates `modules/my-module/` with `android/`, `ios/`, `src/`, `expo-module.config.json` and `index.ts` — [Expo modules: Get started](https://docs.expo.dev/modules/get-started/). Expo blog (Jacob Clausen, 2025-10-16): "But sometimes we need native functionality, and the available options don't fit our use case." — [Expo blog: add native code with Expo Modules](https://expo.dev/blog/how-to-add-native-code-to-your-app-with-expo-modules)
- Testing support — [Mocking native calls in Expo modules](https://docs.expo.dev/modules/mocking/), [expo-modules-test-core on npm](https://www.npmjs.com/package/expo-modules-test-core) (search snippets):
  - `expo-modules-test-core` provides native testing utilities for Expo modules and "should be included and used exclusively in tests targets".
  - `npx expo-modules-test-core generate-ts-mocks` generates TS/JS mocks from the Swift implementation.
  - Kotlin-only methods need hand-written mocks.

### Inferences
- **Options for this app:**
  - (a) Upgrade RN to 0.85 (SDK 56) or 0.86 (SDK 57) and raise the iOS minimum from 15.1 to 16.4. Xcode 27 already satisfies the Xcode 26.4+ requirement.
  - (b) Run SDK 55 on RN 0.84. This combination is unsupported and untested.
- **Cost beyond the module itself:** installing `expo` into a customised bare app touches Metro, Babel, the entry file and native entry points. The app has a custom Jest resolver and msw setup [local `jest.config.js`], so expect test-config work too.
- **Tie-in with OTA:** if the team also wants EAS Update (section 9), Expo modules become a shared prerequisite. That could justify the install, but only after an RN upgrade.

### Gaps
- Compatibility of `expo-modules-core` with this Podfile (static-library pods, RNFirebase forced static, prebuilt `React.framework`) was not verified.
- The exact Android `MainApplication` and `settings.gradle` diffs for SDK 57 were not rendered by the fetched page.
- No source reports running SDK 55 on RN 0.84.

---

## 4. Fabric native components (custom native views)

### Takeaway
A Fabric component uses the same spec-and-codegen flow as a module, with `codegenNativeComponent` in a `*NativeComponent.ts` spec.
- **iOS:** the docs path is an Objective-C++ `RCTViewComponentView` subclass. There is no documented pure-Swift path in core.
- **Android:** a Kotlin `SimpleViewManager` implements the generated `…ManagerInterface` and delegates through the generated `…ManagerDelegate`.

Per the docs, build one only to wrap a host platform view or to create a genuinely platform-specific view.

### Cited Findings
- Spec, verbatim:
  ```ts
  import type {CodegenTypes, HostComponent, ViewProps} from 'react-native';
  import {codegenNativeComponent} from 'react-native';
  type WebViewScriptLoadedEvent = { result: 'success' | 'error' };
  export interface NativeProps extends ViewProps {
    sourceURL?: string;
    onScriptLoaded?: CodegenTypes.BubblingEventHandler<WebViewScriptLoadedEvent> | null;
  }
  export default codegenNativeComponent<NativeProps>('CustomWebView') as HostComponent<NativeProps>;
  ```
  Prop helper types include `CodegenTypes.BubblingEventHandler`, `DirectEventHandler`, `WithDefault` and `Int32` — [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction)
- `codegenConfig` uses `"type": "components"` with `"ios": {"componentProvider": {"CustomWebView": "RCTWebView"}}` — [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction)
- iOS — [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction):
  - The class is `@interface RCTWebView : RCTViewComponentView` in `RCTWebView.mm`, importing codegen headers `react/renderer/components/AppSpec/{ComponentDescriptors,EventEmitters,Props,RCTComponentViewHelpers}.h`.
  - It conforms to the generated `RCTCustomWebViewViewProtocol`.
  - It overrides `updateProps:oldProps:` (cast with `std::static_pointer_cast<CustomWebViewProps const>`) and `+ componentDescriptorProvider { return concreteComponentDescriptorProvider<CustomWebViewComponentDescriptor>(); }`.
- Android — [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction):
  - `@ReactModule(name = …) class ReactWebViewManager(context: ReactApplicationContext) : SimpleViewManager<ReactWebView>(), CustomWebViewManagerInterface<ReactWebView>`
  - The delegate is `CustomWebViewManagerDelegate(this)`, returned from `getDelegate()`.
  - Props are set with `@ReactProp` setters, and events are declared in `getExportedCustomBubblingEventTypeConstants()`.
  - It is registered through `BaseReactPackage.createViewManagers(...)` and `add(ReactWebViewPackage())` in `MainApplication`.
- When to build one: "Wrap a host platform component (Android `CheckBox`, iOS `UIButton`, etc.)", "Create a unique kind of platform-specific view", "Provide direct access to native view capabilities" — [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction). The follow-up "use existing components otherwise" is the fetch tool's paraphrase, not a verified quote.
- Alternatives that allow Swift views:
  - Nitro views: Nitro v0.37.0 moved Props and ComponentDescriptor into Nitro core, and create-react-native-library offers a `nitro-view` type in `kotlin-swift` — [Nitro releases](https://github.com/mrousavy/nitro/releases), [prompt.ts](https://raw.githubusercontent.com/callstack/react-native-builder-bob/main/packages/create-react-native-library/src/prompt.ts)
  - Expo: the Expo Modules API lets you "write Swift and Kotlin to add new capabilities to your app with native modules and views" — [Expo Modules overview](https://docs.expo.dev/modules/overview/)
- The app already depends on the view libraries a line-of-business app typically needs: `react-native-svg`, `react-native-webview`, `react-native-linear-gradient`, `@shopify/flash-list`, `react-native-screens`, `@gorhom/bottom-sheet` — [local] `package.json`

### Inferences
- **For this app:** a custom Fabric component is unlikely to be needed. If one is needed and the team wants Swift, a Nitro view or an Expo view is the Swift-first route; core requires ObjC++.
- **Course scope:** teach Fabric components after Turbo Modules, as an "only when" topic. The iOS ObjC++ and C++ props surface (`Props::Shared`, component descriptors) is where JS-first teams struggle most.

### Gaps
- The "Advanced Topics (components)" page was not fetched (custom state, shadow nodes, commands).
- Whether RN core plans an official Swift path for Fabric views was not found.

---

## 5. Testing native modules test-first (Jest for JS; XCTest / JUnit + Robolectric for native; device checks)

### Takeaway
Red→green for native modules splits into three layers:
1. **Jest** on the JS wrapper, with the spec module mocked. Mocking is mandatory, because `getEnforcing` throws in Jest for unknown modules.
2. **Plain unit tests of the native logic.** Use JUnit 4 + Robolectric on Android (the same stack RN core uses) and XCTest on iOS. Put the logic in a Swift class kept apart from the RN adapter, exactly as RN's Swift adapter pattern already does.
3. **A device run** on a simulator or emulator.

The app has none of the native test scaffolding yet: no iOS unit-test target and no Android test dependencies.

### Cited Findings
- In Jest, the RN 0.84.1 `TurboModuleRegistry.getEnforcing` falls back to the mocked `NativeModules` object. It throws "`…could not be found. Verify that a module by this name is registered in the native binary.`" when the name is missing. RN's Jest `NativeModules` mock is a fixed object (`AlertManager`, `AsyncLocalStorage`, …). RN 0.84.1's `jest/setup.js` contains no `TurboModuleRegistry` mock — [local] (upstream: [TurboModuleRegistry.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/Libraries/TurboModule/TurboModuleRegistry.js), [jest/mocks/NativeModules.js](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/jest/mocks/NativeModules.js))
- The app's Jest setup — [local] `jest.config.js`, `package.json`:
  - `jest.config.js` uses `preset: 'react-native'`, `setupFiles: ['<rootDir>/jest.setup.js']`, `setupFilesAfterEnv`, a custom resolver, and a `moduleNameMapper`.
  - devDependencies: `jest@^30.3.0`, `@testing-library/react-native@^13`, `msw@^2`, `typescript@^6.0.2`.
- RN 0.85 extracted the Jest preset: "React Native's Jest preset has been extracted from `react-native` into the new `@react-native/jest-preset`". The migration is `preset: 'react-native'` → `preset: '@react-native/jest-preset'` — [RN 0.85 blog](https://reactnative.dev/blog/2026/04/07/react-native-0.85). The 0.87 notes add that `@react-native/jest-preset` "must be consumed as package" — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87). The package is not present in the app's 0.84.1 install — [local] `node_modules/@react-native/`
- RN core's own Android unit-test stack: `testImplementation(libs.junit)` (4.13.2), `libs.assertj` (3.21.0), `libs.mockito` (mockito-inline 3.12.4), `libs.mockito.kotlin` (3.2.0), `libs.robolectric` (**4.15.1**) — [local] (upstream: [ReactAndroid/build.gradle.kts](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/ReactAndroid/build.gradle.kts), [gradle/libs.versions.toml](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/gradle/libs.versions.toml))
- Robolectric runs Android tests in a simulated Android environment inside the JVM; "tests routinely run 10x faster than those on cold-started emulators" (search snippet) — [Robolectric](https://robolectric.org/), [Getting started](https://robolectric.org/getting-started/)
- The app has **no** `testImplementation` / `androidTestImplementation` entries in `android/app/build.gradle`. Its Xcode project has only an `application` target and an `app-extension` target (the OneSignal NSE), with **no unit-test bundle** — [local] `android/app/build.gradle`, `ios/dzzlo_oms_app.xcodeproj/project.pbxproj`
- RN's Swift adapter pattern puts all business logic in a plain `@objcMembers public class …: NSObject` Swift class, separate from the ObjC++ Turbo Module shell — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift)
- Library testing per RN's library guide: create-react-native-library can generate an example app (`cd example && yarn install && cd ios && pod install && yarn android / yarn ios`). The example-app choices are:
  - `vanilla` ("Classic React Native app with native code access")
  - `expo`
  - `test-app` ("Test app with app's native code abstracted")

  — [Create a library](https://reactnative.dev/docs/the-new-architecture/create-module-library), [prompt.ts](https://raw.githubusercontent.com/callstack/react-native-builder-bob/main/packages/create-react-native-library/src/prompt.ts). A local library "doesn't include a separate example app" — [builder-bob create docs](https://oss.callstack.com/react-native-builder-bob/create)
- Expo's upstream practice: native test utilities (`expo-modules-test-core`, used only in test targets), mock generation from Swift, and iOS unit tests in the expo repo CI (e.g. PR "[iOS][core][JSI] Fix two sources of flaky iOS unit tests", title only) — [Expo mocking](https://docs.expo.dev/modules/mocking/), [expo#50188](https://github.com/expo/expo/pull/50188)

### Inferences
- **A red→green recipe the course can teach:**
  1. **JS red.** Write a Jest test for a small JS wrapper, e.g. `src/native/localStorage.js`, never the spec directly. Mock the spec, either with `jest.mock('../specs/NativeFoo', () => ({ __esModule: true, default: { getItem: jest.fn(), onKeyAdded: jest.fn(() => ({ remove: jest.fn() })) } }))` or with a manual mock in `specs/__mocks__/NativeFoo.js` plus `jest.mock('../specs/NativeFoo')`. Assert the wrapper's behaviour: argument shaping, error mapping, subscription cleanup. Then turn it green.
     - A global alternative, inferred from the source: add the module to the mocked `NativeModules` object in `jest.setup.js`, since `getEnforcing` falls back to `NativeModules[name]`.
  2. **Contract check.** Run codegen in CI, e.g. `./gradlew generateCodegenArtifactsFromSchema` or the `generate-codegen-artifacts.js` script. A spec codegen can't parse fails the build, which is the red for spec mistakes.
  3. **Native red.**
     - Kotlin: keep logic in a plain Kotlin class, e.g. `LocalStore(context: Context)`, and test it with JUnit 4 + Robolectric (`ApplicationProvider.getApplicationContext()`). The RN module class stays a thin shell. Add `testImplementation` for junit, robolectric and (if needed) mockito-kotlin, using RN's own versions as the reference.
     - Swift: add a "Unit Testing Bundle" target and test the `@objcMembers` Swift class with XCTest. The ObjC++ adapter stays thin and is covered by the device run.
  4. **Device.** Build and exercise the module on the iOS simulator and the Android emulator. The team already drives these with `cdp.js` / simtap / adb, per the workspace notes.
- **Keep the RN-facing surface small.** Keeping the module shells free of logic shrinks what can only be tested on device. That is the same design RN documents for Swift.
- **Jest preset on upgrade:** after moving to RN ≥ 0.85, switch `preset` to `@react-native/jest-preset`. The app's custom `transform` and resolver entries need re-checking against the new preset.

### Gaps
- There is no official RN doc on native unit-testing Turbo Modules. Whether `ReactApplicationContext(context)` can be constructed directly under Robolectric in 0.84 was not verified.
- The 2026 status of Detox and Maestro (e2e) with RN 0.84 bridgeless was not researched.
- No public write-ups were found on how Shopify, Microsoft or Callstack structure native red→green. Only the Expo and RN core evidence above was found.

---

## 6. Build and tooling: Xcode/Swift 6, Kotlin/Gradle/AGP, 16 KB pages, codegen output, upgrade cost 0.76 → 0.87

### Takeaway
- **Machine:** Xcode 27.0 (27A266a) and Swift 6.4, but the app target is still in **Swift 5 language mode** with iOS 15.1 minimum.
- **iOS pods on disk are static libraries, not `use_frameworks!`.** `use_frameworks!` is applied only when a `USE_FRAMEWORKS` env var is set. RN core comes in as the prebuilt `React.framework` (the default since 0.84).
- **Android:** AGP 8.12.0, Gradle 9.0.0, Kotlin 2.1.20, NDK 27.1, compile/target SDK 36. RN's Gradle plugin already passes the 16 KB page-size flag to CMake.
- **Codegen output** lives in `build/` directories that are already git-ignored.
- **Upgrade churn 0.82 → 0.87** falls mostly on legacy/bridge APIs, C++ internals and toolchain bumps (AGP 9 and compileSdk 37 in 0.87), not on the documented Turbo Module surface.

### Cited Findings

**iOS toolchain and linkage (local, 2026-09-29)**
- `xcodebuild -version` → "Xcode 27.0 / Build version 27A266a". `swift --version` → "Apple Swift version 6.4 (swiftlang-6.4.0.34.1 clang-2100.3.34.1)" — [local]
- App targets use `SWIFT_VERSION = 5.0`, `IPHONEOS_DEPLOYMENT_TARGET = 15.1` and `CLANG_CXX_LANGUAGE_STANDARD = c++20 / gnu++20` — [local] `project.pbxproj`. RN 0.84.1 `min_ios_version_supported` returns `'15.1'` — [local] (upstream: [helpers.rb](https://github.com/facebook/react-native/blob/0.84-stable/packages/react-native/scripts/cocoapods/helpers.rb))
- Podfile facts — [local] `ios/Podfile`, `ios/Pods/Target Support Files/Pods-dzzlo_oms_app/*.xcconfig`, `ios/Pods/Pods.xcodeproj`:
  - It calls `use_frameworks! :linkage => linkage.to_sym` **only if `ENV['USE_FRAMEWORKS']` is set**.
  - It sets `$RNFirebaseAsStaticFramework = true`, forces `RNFB*` pods to `static_library`, and adds `:modular_headers => true` for GoogleUtilities, GoogleDataTransport, nanopb and FirebaseABTesting.
  - A comment says global `use_frameworks! :linkage => :static` "breaks react-native-worklets / react-native-reanimated on RN 0.84".
  - A `post_install` raises pods' deployment targets because "Xcode 27 rejects deployment targets below iOS 15" (the team's own note, not checked against Apple docs).
  - In the current `Pods` build, the app's linker flags list 41 static libraries (e.g. `-l"AsyncStorage"`), `libRNScreens.a` exists, and there is no `RNScreens.framework`.
  - `-framework` entries are system frameworks, vendored XCFrameworks (Firebase, OneSignal) and the prebuilt `React`.
  - **This contradicts the brief's premise of dynamic `use_frameworks!`.** The course author should confirm how the team's CI and local builds run `pod install`.
- RN 0.84 — [RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84):
  - "React Native 0.84 now ships precompiled binaries on iOS by default"; disable with `RCT_USE_PREBUILT_RNCORE=0`.
  - "Legacy Architecture code is no longer included in your iOS builds"; re-enable with `RCT_USE_PREBUILT_RNCORE=0 RCT_REMOVE_LEGACY_ARCH=0 bundle exec pod install`.
- The app README notes that dSYM warnings for `React.framework` / `ReactNativeDependencies.framework` are "an artifact of RN 0.84 prebuilt XCFrameworks", with the workaround `RCT_USE_RN_DEP=0 RCT_USE_PREBUILT_RNCORE=0 bundle exec pod install` — [local] `README.md` line 290
- 0.85 "Fixed duplicate symbol error when using `React.XCFramework`" and "Added support for clang virtual file system in `React.XCFramework`" — [RN 0.85 blog](https://reactnative.dev/blog/2026/04/07/react-native-0.85)
- 0.87 SwiftPM (experimental) — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87):
  - "It is opt-in and additive; CocoaPods remains the default and the supported path." It is set up with `npx react-native spm --deintegrate`.
  - "A community library must ship a `Package.swift`. If one does not, run `npx react-native spm scaffold`."
  - Bare angle includes must become framework-style, e.g. `#import <React/RCTAppDelegate.h>`.
  - "Do not use it in production yet."
- RN 0.84.1 already contains `generatePackageSwift.js` in its codegen executor — [local] `react-native/scripts/codegen/generate-artifacts-executor/`

**Swift 6 concurrency**
- The Swift language guide for Turbo Modules says nothing about Swift 6 concurrency — [Swift guide](https://reactnative.dev/docs/the-new-architecture/turbo-modules-with-swift)
- Swift 6 language mode turns on complete concurrency checking by default — [Hacking with Swift: complete concurrency enabled by default](https://www.hackingwithswift.com/swift/6.0/concurrency)
- Xcode 26 projects default to main-actor isolation for app code (search summary; see [SwiftLee: Swift 6.2 concurrency changes](https://www.avanderlee.com/concurrency/swift-6-2-concurrency-changes/))
- RN-adjacent Swift code hits Swift 6 diagnostics such as "Static property 'shared' is not concurrency-safe…" — [expo#37590](https://github.com/expo/expo/issues/37590)

**Android toolchain (local)**
- `android/build.gradle`: `buildToolsVersion = "36.0.0"`, `minSdkVersion = 24`, `compileSdkVersion = 36`, `targetSdkVersion = 36`, `ndkVersion = "27.1.12297006"`, `kotlinVersion = "2.1.20"`
- Gradle wrapper: `gradle-9.0.0`
- RN's `libs.versions.toml`: `agp = "8.12.0"`, `kotlin = "2.1.20"`
- `gradle.properties`: `reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64`

— [local] `android/build.gradle`, `android/gradle/wrapper/gradle-wrapper.properties`, `node_modules/@react-native/gradle-plugin/gradle/libs.versions.toml`
- 0.82 bumped Gradle from 8.x to 9.0.0 — [RN 0.82 blog](https://reactnative.dev/blog/2025/10/08/react-native-0.82)
- 0.87 AGP 9 support — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87), [RFC #1006](https://github.com/react-native-community/discussions-and-proposals/pull/1006):
  - Kotlin 2.0+ minimum (bundled 2.2.0); compileSdk/buildTools 37; `minCompileSdk` 34.
  - Required opt-outs `android.builtInKotlin=false` and `android.newDsl=false`. "Starting from AGP 10.x these opt outs will be removed."
- KSP: none of the fetched sources for Turbo Modules, Nitro or Expo modules mentions a KSP requirement. The RN docs show codegen as a Gradle task (`generateCodegenArtifactsFromSchema`) — [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen)

**16 KB page sizes (Android)**
- Current primary text: "all apps targeting Android 15 (API level 35) and higher must support 16 KB memory page sizes on 64-bit devices on Google Play. Starting February 1, 2027, if your app updates don't support 16 KB memory page sizes, you won't be able to release these updates." — [Android: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes). **Date conflict:** older third-party guidance cites 2025-11-01, extendable to 2026-05-31 — [Broadcom KB](https://knowledge.broadcom.com/external/article/411558/guidance-on-google-plays-16-kb-page-size.html). The current Android page (Feb 1, 2027 for updates) should be treated as authoritative, and checked again before the course ships.
- "If your app only uses code written in the Java programming language or in Kotlin, including all libraries or SDKs, then your app already supports 16 KB devices." — [Android: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes)
- NDK and packaging rules — [Android: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes):
  - "NDK version r28 and higher compile 16 KB-aligned by default."
  - For r27 or lower, use `-Wl,-z,max-page-size=16384 -Wl,-z,common-page-size=16384`.
  - AGP 8.5.1+ is needed for 16 KB zip alignment of uncompressed libraries.
  - Checks: `zipalign -c -P 16 -v 4 APK_NAME.apk` and `check_elf_alignment.sh APK_NAME.apk`.
- RN 0.84.1's Gradle plugin adds `-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON` to CMake arguments when absent — [local] (upstream: [NdkConfiguratorUtils.kt](https://github.com/facebook/react-native/blob/0.84-stable/packages/gradle-plugin/react-native-gradle-plugin/src/main/kotlin/com/facebook/react/utils/NdkConfiguratorUtils.kt))

**Codegen output and git**
- Output goes to `android/app/build/generated/source/codegen` and `ios/build/generated/ios/` — [Using Codegen](https://reactnative.dev/docs/the-new-architecture/using-codegen). The app's `.gitignore` already ignores `build/` (lines 7, 27) and `.cxx/` (line 33) — [local] `.gitignore`

**Upgrade cost evidence (native-relevant breaking changes)**
- 0.80 (2025-06-12): Legacy Architecture frozen, with warnings; deep imports deprecated; Strict TS API opt-in — [RN blog index](https://reactnative.dev/blog)
- 0.82 — [RN 0.82 blog](https://reactnative.dev/blog/2025/10/08/react-native-0.82):
  - New Architecture only.
  - "We will keep the interop layers in the codebase for the foreseeable future."
  - `com.facebook.react.bridge.JSONArguments` removed.
  - C++ backward-compat headers deleted (use `#include <react/bridging/CallbackWrapper.h>` / `LongLivedObject.h`).
  - Gradle 9.0.0.
- 0.83 (2025-12-10) is titled "no breaking changes" — [RN blog index](https://reactnative.dev/blog)
- 0.84 — [RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84):
  - 14 legacy Android classes removed (incl. `LazyReactPackage`, `CxxModuleWrapper`, `CallbackImpl`).
  - `JSBigString` now implements `jsi::Buffer`.
  - `RCTImage` observer API change (affects e.g. react-native-svg).
  - Node 22.11+.
- 0.85 — [RN 0.85 blog](https://reactnative.dev/blog/2026/04/07/react-native-0.85):
  - Removed C++ aliases `ShadowNode::Shared/Weak/Unshared/ListOfWeak/ListOfShared`, `SharedImageManager` and `ContextContainer::Shared`.
  - `CatalystInstanceImpl` removed; `ReactTextUpdate` made internal.
  - `RCTHostRuntimeDelegate` deprecated.
  - Jest preset extracted.
- 0.86 (2026-06-11) is titled "no breaking changes" — [RN blog index](https://reactnative.dev/blog)
- 0.87 — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87):
  - Strict TS API default; SwiftPM experimental; AGP 9 / compileSdk 37.
  - `useTurboModules` flag removed.
  - `UIBlock` / `UIManagerModule.addUIBlock` deprecated (use `UIManagerListener` or View Commands).
  - Node ≥ 22.13.0.
- The upgrade helper is the recommended diff tool — [RN 0.87 blog](https://reactnative.dev/blog/2026/08/11/react-native-0.87) → [Upgrade Helper](https://react-native-community.github.io/upgrade-helper/)

### Inferences
- **A module built strictly on the documented surface** survives 0.82 → 0.87 largely untouched. That surface is: spec + codegen, `BaseReactPackage`, the generated spec base classes, `getTurboModule:` / `RCTModuleProvider`, and `CodegenTypes.EventEmitter`. The recurring costs are:
  - toolchain bumps: Gradle 9, AGP 9 opt-outs, compileSdk 37, the Node floor;
  - iOS include hygiene: always use `#import <React/…>` framework-style includes, which SwiftPM needs from 0.87;
  - the release cadence: a new minor roughly every two months.
- **Kotlin/ObjC/Swift-only modules add no `.so`,** so 16 KB is a non-issue for them. Pure C++ Turbo Modules and every Nitro module add `.so` files. With NDK 27.1, the RN Gradle plugin's `ANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON` should cover CMake builds that go through RN's setup; verify with `check_elf_alignment.sh` on the release APK.
- **Swift 6:** keep new Swift module code compiling cleanly in Swift 5 mode with warnings visible, or opt a separate target into Swift 6 mode deliberately. RN calls into Swift from arbitrary queues (JS thread, module queue), so Swift adapter classes should avoid shared mutable state or guard it explicitly, e.g. a serial queue or `@MainActor` hops for UIKit.
- **Pod linkage:** because the app's pods are static libraries today, an **in-app** module (compiled into the app target) avoids linkage questions entirely. A **local library** becomes a pod and inherits the Podfile's linkage.

### Gaps
- There is no official RN statement on the supported Xcode range for 0.84 or on Swift 6 language mode for app targets.
- Whether `use_frameworks! :linkage => :dynamic` works with RN 0.84 prebuilt `React.framework` plus local Swift pods was not verified.
- The note that "Xcode 27 rejects deployment targets below iOS 15" and "Apps built with the iOS 27 SDK must adopt the UIScene life cycle" come from the team's own code comments [local]. Apple sources were not fetched.

---

## 7. Packaging: in-app module vs local library (`create-react-native-library --local`) vs separate package

### Takeaway
There are three rungs:
- **(a) In-app:** native files inside `ios/` and `android/app`, specs in `specs/`, one `codegenConfig` in the app `package.json`, and manual Android registration.
- **(b) Local library:** `npx create-react-native-library@latest` run inside the app creates `modules/<name>`, linked with `link:` (Yarn) or `file:` (npm) and autolinked through the `node_modules` symlink. It has its own `codegenConfig`, podspec and Gradle module, and no example app.
- **(c) Separate npm package,** scaffolded the same way and published.

For this team: start one small module in-app, and move to a local library once there are two or more modules, a Nitro module, or a reuse need.

### Cited Findings
- "If you run `create-react-native-library` in an existing project containing a `package.json`, it'll be automatically detected and you'll be asked if you want to create a local library". The library lands in `modules/`, e.g. `modules/awesome-library`. "By default, the generated library is automatically linked to the project using `link:` protocol when using Yarn and `file:` when using npm". The tool "makes use of autolinking" and "creates a symlink to the library under `node_modules` which makes autolinking work". There is a `--local` flag. The local variant "doesn't include a separate example app" — [builder-bob: create](https://oss.callstack.com/react-native-builder-bob/create)
- Types and languages — [prompt.ts](https://raw.githubusercontent.com/callstack/react-native-builder-bob/main/packages/create-react-native-library/src/prompt.ts):
  - `turbo-module` ("Integration for native APIs to JS")
  - `fabric-view`
  - `nitro-module`
  - `nitro-view`
  - `library` (plain JS)

  Languages: `kotlin-objc` for turbo-module and fabric-view, `cpp` (Experimental) for turbo-module, `kotlin-swift` for the nitro types. The prompt fields map to options including `--local`, `--type`, `--languages`, `--example` and `--react-native-version`.
- RN's own library guide — [Create a library](https://reactnative.dev/docs/the-new-architecture/create-module-library):
  - Command: `npx create-react-native-library@latest <Name>`.
  - Moving an in-app module into a library: move the specs into the library's `src`, replace its native folders, and update the `codegenConfig.name` references.
  - A sibling-folder "Local Module" setup: `yarn add ../Library` plus Metro `watchFolders`.
  - Publishing: `yarn prepare`, `yarn release`.
- Npm packages are autolinked, while in-app modules are registered manually — [Turbo Native Modules intro](https://reactnative.dev/docs/turbo-native-modules-introduction)
- Expo equivalent: `npx create-expo-module@latest --local` → `modules/<name>` — [Expo modules: Get started](https://docs.expo.dev/modules/get-started/). Nitro can be added "manually to your existing library/app", and "Nitro's template does not include an example app by default, which makes it easier to be used in monorepos" — [How to build a Nitro Module](https://nitro.margelo.com/docs/getting-started/how-to-build-a-nitro-module)
- The app uses Yarn (`yarn.lock` present), so builder-bob would link a local library with `link:` — [local]

### Inferences
- **For a first course module, in-app is the simplest to reason about.** It has no extra pod, no extra Gradle module and a single `codegenConfig`. Its costs are the manual Android `add(...)` and native files mixed into the app projects.
- **A local library gives:**
  - autolinking on both platforms;
  - a clean boundary for native unit tests, since the library's Gradle module and podspec can hold `testImplementation` and test specs without touching the app;
  - an easy later move to a separate package.

  The cost is Swift language choice: builder-bob's Turbo template is ObjC on iOS, so Swift in a local Turbo library means hand-adding the Swift adapter; the Nitro template is Swift from the start.
- **A local library is a CocoaPods pod,** so it inherits the Podfile linkage (static libraries today) and needs `bundle exec pod install` after creation.

### Gaps
- The create-react-native-library version number was not captured.
- It was not verified that a `--local` library's own `codegenConfig` is picked up by the app's codegen run on both platforms. It is very likely via autolinking, but untested here.

---

## 8. "How much native code should a JS-first team write?"

### Takeaway
The sources converge on one default: use maintained libraries, and write native code only where no maintained library covers a platform capability, or for hardware, background or extension work, or measured hot paths.

**New signal (2026-09-10):** Shopify, RN's highest-profile adopter, announced it is moving all major apps back to Swift and Kotlin, because coding agents made "build twice" cheap. That argues about *which stack a large team with native specialists should choose*. It does not argue that a JS-first RN team should write more native modules.

For a JS-first team the defensible rule is:
- zero custom native code by default;
- a small number of thin, test-covered modules when a trigger is met;
- never fork and own a large native library.

### Cited Findings
- **Lean Core (RN core team policy since 2018–2019):** RN moved components and native modules out of core into community repos — WebView, NetInfo, AsyncStorage, Clipboard, Slider, ImageEditor and others — [Lean Core umbrella issue #23313](https://github.com/facebook/react-native/issues/23313), [discussions-and-proposals #6](https://github.com/react-native-community/discussions-and-proposals/issues/6). The same direction continued with the JavaScriptCore engine moving to `@react-native-community/javascriptcore` (search summary) — [RN 0.79 blog](https://reactnative.dev/blog/2025/04/08/react-native-0.79)
- The app already relies on community native packages rather than its own native code: `@react-native-community/netinfo`, `@react-native-async-storage/async-storage`, `react-native-webview`, `react-native-device-info`, `react-native-html-to-pdf`, Firebase and OneSignal. Its only custom native code beyond the template is the OneSignal Notification Service Extension target — [local] `package.json`, `project.pbxproj`
- Shopify, "Five years of React Native at Shopify" (2025-01-13) — [Shopify Engineering](https://shopify.engineering/five-years-of-react-native-at-shopify):
  - "Instead of thinking native **or** React Native, think native **and** React Native."
  - Native is for "cutting-edge features that leverage device hardware like 2D / 3D scanning and running AI models on-device", memory-constrained surfaces (widgets, Apple Watch) and "long-running background jobs".
  - "Mobile engineers who specialize in iOS and Android are essential to building great mobile apps."
  - Reported sub-500 ms P75 screen loads.
- Shopify, "Native is now the future of mobile at Shopify" (Mustafa Ali, **2026-09-10**) — [Shopify Engineering](https://shopify.engineering/back-to-native):
  - All major apps are migrating to Swift and Kotlin.
  - "LLMs changed one of the core assumptions behind our 2020 decision, so we reevaluated our mobile stack from first principles."
  - Agents can "implement a feature on Android using the iOS version as reference, and vice versa".
  - "Native keeps us closer to platform capabilities and first-party tooling, with fewer framework and dependency layers between our code and the platform."
  - "React Native was the right choice for Shopify in 2020", and it remains "an excellent framework".
  - The Shop app went from proof of concept to published native app in 12 weeks; the Shopify app has 300+ screens.
  - The article gives no advice for other teams.
- Expo on overhead versus work: "the time spent executing the body of a native method is often orders of magnitude greater than the overhead of the method invocation" — [Expo Modules overview](https://docs.expo.dev/modules/overview/). Expo on when to write native: "But sometimes we need native functionality, and the available options don't fit our use case." — [Expo blog, 2025-10-16](https://expo.dev/blog/how-to-add-native-code-to-your-app-with-expo-modules)
- RN docs on when a native component is warranted: to wrap a host platform component, create a unique platform-specific view, or give direct access to native view capabilities — [Fabric Native Components intro](https://reactnative.dev/docs/fabric-native-components-introduction)
- Store constraint: native code ships only inside the reviewed binary. App Review 2.5.2 bars apps from downloading code "which introduces or changes features or functionality of the app" — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/). Google Play bars downloading "dex, JAR, .so files" from outside Play — [Google Play: Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/9888379)
- Cadence (a maintenance proxy): RN shipped eight minors between 2025-06-12 (0.80) and 2026-08-11 (0.87), roughly one every two months — [RN blog index](https://reactnative.dev/blog)

### Inferences
- **Decision rules for the course:**
  - **Write native when:**
    - a needed platform API has no maintained library;
    - you need an OS extension or target (widgets, notification service extensions, watch, share extension);
    - a measured JS↔native hot path exists (per-frame, sensor streams, large binary buffers);
    - a small, critical library is abandoned and cheaper to vendor than to replace.
  - **Otherwise don't:** prefer a maintained community library, then a JS-only solution, then a feature trade-off.
- **What each module costs a JS-first team:**
  - two more languages (Swift/ObjC++ and Kotlin) and their build systems;
  - a native test harness (section 5);
  - a review at every RN minor, about six per year;
  - privacy and store-policy review;
  - every change needs a store release, because OTA can't ship native code (section 9).
- **Coding agents cut the cost of writing Swift/Kotlin** (Shopify's point) but not of owning it: upgrade review, device testing and on-call for crashes in code nobody on the team reads fluently remain.
- **Implied scale for dzzlo_oms_app:** 0 custom modules today. Plan for at most one or two thin modules, each with a JS wrapper, Jest tests, native unit tests and a device check, and only when a trigger above is met.

### Gaps
- No primary 2025–2026 statement was found from the RN core team, Callstack or Software Mansion that quantifies how much custom native code typical production RN apps contain ("typical ratios"). No hiring-market data was found.
- Apple's privacy-manifest ("required reason API") obligations for new native modules were not fetched. The app has `ios/dzzlo_oms_app/PrivacyInfo.xcprivacy` [local]. RN's Swift example uses `UserDefaults`, which is believed to be a required-reason API; verify.

---

## 9. OTA updates after CodePush: options for bare RN in 2026 and store rules

### Takeaway
- **CodePush:** the hosted service ended with App Center on **2025-03-31**. Microsoft published a standalone `code-push-server` for self-hosting.
- **Options for bare RN in 2026:**
  - EAS Update, which in a bare app requires installing Expo modules plus `expo-updates`, so it inherits section 3's SDK↔RN pairing issue;
  - hosted CodePush-compatible services (Revopush, Stallion);
  - self-hosted tools (Hot Updater, Codemagic Patch, Microsoft's code-push-server).
- **Store rules:**
  - Apple 2.5.2 forbids downloaded code that changes features or functionality, while 4.7 allows HTML5/JavaScript mini apps.
  - Google Play forbids downloading dex/JAR/.so but exempts interpreted code running in a VM or interpreter.
- **Native code can never ship OTA,** so every native-module change is a store release.

### Cited Findings
- "Visual Studio App Center is scheduled for retirement on March 31, 2025." For CodePush: "We have prepared a special version of CodePush that can be integrated into your app and run independently from App Center… in this GitHub repository", linking [github.com/microsoft/code-push-server](https://github.com/microsoft/code-push-server). App Center Analytics & Diagnostics support was extended to the end of March 2027 (update dated 2026-04-15) — [Microsoft Learn: App Center retirement](https://learn.microsoft.com/en-us/appcenter/retirement)
- Codemagic's OTA survey (2026-08-19) — [Codemagic: React Native OTA tools in 2026](https://blog.codemagic.io/react-native-ota-tools-in-2026/):

  | Tool | Hosting | Pricing (vendor claims, may change) | CodePush-compatible |
  |---|---|---|---|
  | EAS Update | hosted | usage-based (MAU + bandwidth) | no |
  | Revopush | hosted | ~$500/mo tier | yes |
  | Stallion | hosted | ~$64/mo tier | yes |
  | Codemagic Patch | self-hosted, open-source | — | yes |

  - "For Patch, Revopush, and Stallion, it starts at React Native 0.76" (New Architecture support).
  - On EAS: "the bill can get hard to predict once you have a lot of users".
- EAS Update in a bare app — [Expo: Updating a bare app](https://docs.expo.dev/bare/updating-your-app/):
  - Steps: `npx install-expo-modules@latest` if Expo modules are absent, then `npx expo install expo-updates` and `npx pod-install`.
  - Android `AndroidManifest.xml` meta-data: `expo.modules.updates.EXPO_UPDATE_URL`, `…EXPO_RUNTIME_VERSION`.
  - iOS `Expo.plist`: `EXUpdatesRuntimeVersion`, `EXUpdatesURL`.
  - Use `registerRootComponent`, with module name `"main"`.
  - "EAS Update is available to anyone with an Expo account, regardless of whether you pay for EAS or use the Free plan."
- Hot Updater: "A self-hostable OTA update solution for React Native (Alternative to CodePush)". It supports the New Architecture and storage/DB back ends such as S3, Supabase, Cloudflare R2/D1 and Firebase. It has a `bare({ enableHermes: true })` build plugin for bare RN CLI apps and about 1.7k stars — [gronxb/hot-updater](https://github.com/gronxb/hot-updater)
- Apple 2.5.2: "Apps should be self-contained in their bundles… nor may they download, install, or execute code which introduces or changes features or functionality of the app, including other apps." Apple 4.7: "Apps may offer certain software that is not embedded in the binary, specifically HTML5 and JavaScript mini apps and mini games, streaming games, chatbots, and plug-ins." — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- Google Play: "an app may not download executable code (such as dex, JAR, .so files) from a source other than Google Play. This restriction does not apply to code that runs in a virtual machine or an interpreter where either provides indirect access to Android APIs (such as JavaScript in a webview or browser)." — [Google Play: Device and Network Abuse](https://support.google.com/googleplay/android-developer/answer/9888379)

### Inferences
- **For dzzlo_oms_app on RN 0.84 without Expo,** the non-Expo paths (Hot Updater, `code-push-server`, Revopush, Stallion) avoid the Expo SDK↔RN version lock. EAS Update becomes reasonable only after an RN upgrade that also makes Expo modules viable.
- **Native modules and OTA interact.** A JS bundle that calls a new or changed spec must only reach binaries that contain that native code. Every OTA tool pins updates to a binary or runtime version (EAS calls it `runtimeVersion`). The course should teach "bump the runtime/binary version whenever `specs/` or native code changes".
- **Policy framing:** Apple's text is strict (2.5.2), and its explicit JS allowance (4.7) is written for mini apps. Common industry practice treats JS-only bug fixes through OTA as acceptable, while feature changes that alter the app's purpose are a review risk. This is inference; see gaps.

### Gaps
- Apple's Developer Program License Agreement clause on interpreted code, which the industry usually cites for OTA, was not fetched. Only the App Review Guidelines were checked.
- Hot Updater's licence, current version and RN 0.84 test matrix were not captured. Pricing numbers come from a secondary source and may be outdated.
- No authoritative 2026 statement from Apple or Google specifically about React Native OTA was found.
