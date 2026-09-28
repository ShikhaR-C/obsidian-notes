# Remote Config removal — the package, the boot fetch, the mock, and the pod

**Status:** **BUILT 2026-09-27 — two commits on app `release/v1_79`, NOT pushed: red `bcfd1ebf`, green `ad40ed71` (PR #55 carries them once pushed).** Suite 160 / 3634 in 12.7 s (was 159 / 3629). Smokes green (§10). The five tasks_05 vault notes carry their "DEFERRED 2026-09-27" markers, nothing deleted (C‑3). Firebase console: the user's (C‑2). Emulator boot check: green (§10).
**Created:** 2026-09-27, from the user: "we want to remove @react-native-firebase/remote-config package. plan how to remove it."
**Scope:** One repo, `dzzlo_oms_app`. Two JS files, one Jest mock, the dependency (`package.json` + `yarn.lock`), the iOS lockfile and one Podfile comment, two doc lines, one vault line. **Nothing in the API, nothing in `dip-web`.** The other four Firebase packages (`app`, `analytics`, `crashlytics`, `perf`) stay exactly as they are, with their native config files.
**Why:** Remote Config came in with the rest of Firebase on `0fb53e29` (tasks_05 `FIREBASE_INTEGRATION_PLAN.md`) as the future feature-toggle channel. The toggle channel was then built **server-side** instead: `GET /api/v4/features` → `screen_v2_<role>_<route>` → `resolveScreen` (tasks_12; `docs/testing.md` → "The toggles"). What is left of Remote Config in the app is `initRemoteConfig({})` — **empty defaults**, then a `fetchAndActivate()` **network round-trip on every cold start** (interval 0 in dev, 1 h in release) — and `getRemoteValue`, exported and **imported by nothing** (it never has been, in any commit since `0fb53e29`). The package costs a native module on both platforms, one boot request, a mock in every Jest run and a Firebase surface nobody reads.
**Source:** app `release/v1_79` @ `bc94a345`, every file below opened 2026-09-27; PR #55 is open on that branch. Suite at that tree: **159 suites / 3629 tests, 12.3 s.** The working tree carries unrelated uncommitted work (`companyList.js`, `vocTypes.js`, `CustSettings.js`, `helpers/RowDivider/`, two test files) — this plan touches none of those files.

---

## 1. The one-paragraph answer

Remove the package and everything that exists **only** because of it: the Remote Config section of `src/utils/firebase.js`, one import and one call in `AppNavigatorContainer.js`, the mock in `jest.setup.js`, the `package.json` line — then re-run `pod install` so `Podfile.lock` drops `RNFBRemoteConfig`. **The Firebase Remote Config SDK itself stays in the binary on both platforms**, because Performance Monitoring depends on it (`Podfile.lock`: `FirebasePerformance → FirebaseRemoteConfig → FirebaseABTesting`, and `FirebaseCrashlytics → FirebaseRemoteConfigInterop`), so the Podfile's `FirebaseABTesting` modular-headers line stays and only its comment changes. What leaves is the React Native **bridge module**, its JS, and the boot fetch. One red config test — same shape as `androidText.config.test.js`, pinned off disk — says the app has no Remote Config, and keeps saying it. In the notes and docs the word is **deferred** (C‑3): nothing that planned for Remote Config is deleted; each place it is named says the package is out of the app since 2026-09 and points here.

---

## 2. Inventory — every touchpoint, and what happens to it

**REMOVE** = goes. **REGENERATE** = a tool rewrites it. **CLEAN** = a stale comment or doc line. **KEEP** = untouched, and why.

| Where                                                                                                  | Today                                                                                                                                              | Plan                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `package.json:39`                                                                                      | `"@react-native-firebase/remote-config": "24.0.0"`                                                                                                 | **REMOVE** — `yarn remove @react-native-firebase/remote-config`. Rewrites `yarn.lock`: the `@react-native-firebase/remote-config@24.0.0` block goes. The `@firebase/remote-config*` entries in `yarn.lock` **stay** — they belong to `firebase@12.10.0`, the web SDK that `@react-native-firebase/app` depends on; not ours to remove and nobody should chase them                    |
| `src/utils/firebase.js:4` and `:77–90`                                                                 | `import remoteConfig from '@react-native-firebase/remote-config'`; `initRemoteConfig(defaults)` (setDefaults → setConfigSettings → fetchAndActivate, in a try/catch); `getRemoteValue(key)` | **REMOVE** the import and the whole `// ── Remote Config ──` section. `tagEnv`, `logEvent`, `logScreenView`, `setUser`, `logError`, `startHttpMetric`, `startTrace` untouched. `getRemoteValue` has zero importers (`rg` 2026-09-27)                                                                                                                                                 |
| `src/navigation/AppNavigatorContainer.js:31` and `:92–96`                                              | `import { initRemoteConfig, setUser, tagEnv }`; in the mount effect: comment "Enable Crashlytics collection and seed Remote Config.", then `initRemoteConfig({});` | **REMOVE** the name from the import and the call; comment → "Enable Crashlytics collection." The effect keeps `runOneSignal({ dispatch })`, `crashlytics().setCrashlyticsCollectionEnabled(true)`, `tagEnv()`. Nothing else in the file mentions it                                                                                                                                   |
| `jest.setup.js:49–61`                                                                                  | `jest.mock('@react-native-firebase/remote-config', …)` — setDefaults / setConfigSettings / fetchAndActivate / getValue stubs                       | **REMOVE — in the SAME commit as the package.** A `jest.mock` of an uninstalled module that is not `{ virtual: true }` fails **every** suite at setup ("Cannot find module … from jest.setup.js"). Order inside the green commit does not matter; splitting them across commits does                                                                                                     |
| `ios/Podfile.lock` — `RNFBRemoteConfig (24.0.0)` block, `Firebase/RemoteConfig (12.10.0)` subspec, the external-source line, the checkout path, the checksum | The RN bridge pod and the umbrella subspec it pulls                                                                                                | **REGENERATE** — `cd ios && bundle exec pod install`. Expected diff: those lines go and nothing else; `FirebaseRemoteConfig`, `FirebaseRemoteConfigInterop`, `FirebaseABTesting` **stay** (pulled by `FirebasePerformance` and `FirebaseCrashlytics`). `project.pbxproj` has no Remote Config reference and is not expected to change                                                     |
| `ios/Podfile:25`                                                                                       | Comment: "Swift Firebase pods (Crashlytics, RemoteConfig, Sessions, CoreInternal) can't consume these ObjC deps as static libs without module maps" | **CLEAN** — reword: RemoteConfig is now transitive through Performance, not ours. The four `:modular_headers => true` pods stay, **including `FirebaseABTesting`** (a dependency of `FirebaseRemoteConfig`, which Performance keeps). Removing that line would break the pod build, not slim it                                                                                          |
| `android/**`                                                                                           | No explicit reference anywhere. RNFB modules are autolinked (`settings.gradle` → `autolinkLibrariesFromCommand()`); `google-services`, `crashlytics`, `firebase-perf` gradle plugins applied | **NOTHING TO EDIT.** `io.invertase.firebase.config` drops out of the generated `PackageList.java` on the next build. `com.google.firebase:firebase-config` is expected to remain on the classpath through `firebase-perf` (the Performance SDK reads its sampling settings from it) — confirm at execute with `./gradlew :app:dependencies --configuration releaseRuntimeClasspath \| rg firebase-config` |
| `firebase.json`, `ios/GoogleService-Info.plist`, `android/app/google-services.json`                     | RNFB config (crashlytics flags only) and the two Firebase project files                                                                            | **KEEP** — used by `app` / `analytics` / `crashlytics` / `perf`                                                                                                                                                                                                                                                                                                                    |
| `docs/testing.md:67`                                                                                   | "Firebase (app / analytics / crashlytics / perf / remote-config), AsyncStorage, …"                                                                 | **DEFER (C‑3)** — "Firebase (app / analytics / crashlytics / perf; remote-config deferred, tasks_17), AsyncStorage, …"                                                                                                                                                                                                                                                                                                                                                |
| `docs/todos/PRODUCTION_RELEASE_CHECKLIST.md:538`                                                       | "Crashlytics + Analytics + Remote Config + Performance plugins applied → `android/app/build.gradle:5-7`"                                           | **CLEAN** — the row was already wrong (there is no Remote Config gradle plugin; lines 5–7 are google-services, crashlytics, perf) → "google-services + Crashlytics + Performance plugins applied (Remote Config deferred — tasks_17)"                                                                                                                                                                                  |
| Vault `tasks_05_firebase/FIREBASE_INTEGRATION_PLAN.md` (DONE; lists remote-config among the five)      | The plan that added it                                                                                                                             | **DEFER (C‑3)** — nothing deleted, the DONE ✅ and every step stay as written; one line under the title: "Remote Config: **DEFERRED** 2026-09-27 — the package is out of the app (tasks_17); the toggles ride `/api/v4/features`; the Remote Config steps below stay for when it comes back"                                                                                                                                                                                                                                                             |
| Vault `tasks_05_firebase/FIREBASE_NOTIFICATIONS_*.md`                                                  | Unbuilt proposals that pencil Remote Config in as kill-switches (`push_backend`, `journey_<id>_enabled`, `push_send_enabled` …)                    | **DEFER (C‑3)** — nothing deleted; one line under each title: "Remote Config kill-switches: **DEFERRED** 2026-09-27 (tasks_17) — until Remote Config returns, a kill-switch rides `/api/v4/features` like the screen toggles". Every `push_backend` / `journey_<id>_enabled` / `*_send_enabled` design stays as written                                                                                                                                                                                                                       |
| Firebase console → Remote Config parameters / A‑B experiments                                          | Unknown from the repo. Read by nothing: defaults are `{}` and `getRemoteValue` is never called                                                     | **OUT OF REPO — the user's (C‑2: "leave firebase console to me").** Nothing in this plan touches the console. Older phones keep calling `fetchAndActivate()` and use nothing from the answer; harmless either way                                                                                                                                                                                                                       |

**Not in the table because nothing was found:** `App.js`, `index.js`, `README.md`, `AI.md`, `.env.*` / `.env.ci` / `.env.example` (no Remote Config env var), `.github/workflows/test.yml` (only `yarn install --frozen-lockfile` + `yarn test`), the two `build-*-apk.sh` scripts, `docs/screens/*`, `docs/oms_app/*` in the vault.

---

## 3. Order of work

1. **Red** — the config test in §4, committed alone: `test(firebase): the app has no Remote Config — package, module, mock, pod (red)`. 4 of its 5 cases fail on the unchanged tree.
2. **Green** — one commit: `yarn remove`, the three source/setup edits, the Podfile comment, `pod install`, the two doc lines — `chore(firebase): remove @react-native-firebase/remote-config — deferred; toggles ride /api/v4/features`.
3. **Smoke** (§4) — three mutations, each reverted; results in the commit body and the PR #55 body.
4. **Device** — `yarn build:android`, cold start on the emulator: the dev console shows `[v4] ping` / `[v4] features` and no `[firebase] initRemoteConfig` line; Crashlytics / Analytics / Perf still initialise (no new `[firebase] … failed` warnings).
5. **Vault + docs, "deferred"** — this note's status → DONE with the counts; the one-line "deferred" markers in the four tasks_05 notes and the two app docs (C‑3). No plan or section is deleted.

Where the two commits land: **`release/v1_79` (C‑1)** — PR #55 carries them.

---

## 4. Red → green

**Test:** `src/utils/__tests__/firebaseModules.config.test.js` — Tier 1, off disk, beside the module it guards. The `src/utils/__tests__/` folder exists. Same family as `androidText.config.test.js`, `locales.config.test.js`, `orientation.config.test.js`, `keyboard.config.test.js`: *config no import graph protects, pinned off disk*. Header comment says why a JS test reads `package.json`, `jest.setup.js` and `Podfile.lock`: nothing else in the suite would notice the package coming back, and one `jest.mock` of a missing module takes the whole suite down.

| #   | `it`                                                                                                                                                                                                    | Today | After |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----- | ----- |
| 1   | `package.json` dependencies whose name starts `@react-native-firebase/` are exactly `['analytics', 'app', 'crashlytics', 'perf']` — the four that stay, by name; a fifth (any fifth) must edit this test on purpose | red   | green |
| 2   | those four share one version string — RNFB requires matching versions; free, same read                                                                                                                  | green | green |
| 3   | `src/utils/firebase.js` source has no `@react-native-firebase/remote-config`, and the `require`d module exports neither `initRemoteConfig` nor `getRemoteValue` (the other three RNFB mocks make the require safe) | red   | green |
| 4   | `jest.setup.js` source has no `@react-native-firebase/remote-config`                                                                                                                                    | red   | green |
| 5   | `ios/Podfile.lock` has no `RNFBRemoteConfig` — the case that catches "forgot `pod install`"; `FirebaseRemoteConfig` is **not** asserted absent, because it stays (§1)                                    | red   | green |

No recursive walk of `src/` for stray importers: cases 1, 3 and 4 cover the only two importers that exist, and once the package is out of `package.json` any new importer fails at resolve time in Jest and in Metro. Keeps the test at a few milliseconds.

**Red run expected:** 4 / 5 red (`it` 2 green).

**Smoke, after green, each reverted:**
- (a) put the dependency line back in `package.json` → `it` 1 red;
- (b) `git stash push ios/Podfile.lock` → `it` 5 red (then `git stash pop`);
- (c) append `export const getRemoteValue = () => null;` to `firebase.js` → `it` 3 red.

Not smoked by re-inserting the mock: with the package gone, the mock crashes setup instead of failing `it` 4 — which is the point of the row in §2, and the reason the mock leaves in the green commit.

**Suite after:** 160 suites / 3634 tests (+1 / +5) at the 2026-09-27 tree; still ~12 s.

---

## 5. Test verdicts (for the PR body)

- **No test is deleted or skipped.** The `jest.mock` in `jest.setup.js` is setup, not a test; it leaves with the module it stubs.
- `__tests__/App.test.tsx` still renders the boot spinner; it never asserted on Remote Config (it only saw the mocked `fetchAndActivate` resolve `false`).
- `docs/testing.md` mock list updated so the doc matches `jest.setup.js` again.

---

## 6. Calls — answered 2026-09-27

The user, in one line: "calls - land commits in release/v1_79 branch. leave firebase console to me. all notes and docs files should update remote-config as deferred. do not delete any plan, just update deferred". Each call keeps its recommendation and carries the answer.

- **C‑1 — Where the commits land.** *Recommended:* the red commit and the green commit straight on `release/v1_79`, so PR #55 carries them (tasks_16 C‑5 put TCS there). **✅ "land commits in release/v1_79 branch."** Two commits, red then green, on `release/v1_79`; PR #55 carries them.
- **C‑2 — Firebase console.** *Recommended:* archive the Remote Config parameters after the release ships. **✅ "leave firebase console to me."** Out of this plan; the user handles the console. The §2 row says so.
- **C‑3 — Notes and docs.** *Recommended:* pointer lines in the tasks_05 notes. **✅ "all notes and docs files should update remote-config as deferred. do not delete any plan, just update deferred."** Every note and doc line that names Remote Config gets a one-line **deferred** marker dated 2026-09-27 pointing at tasks_17; no section, step or design is removed — `FIREBASE_INTEGRATION_PLAN.md` keeps its DONE ✅ and its Remote Config steps, the three notifications plans keep their kill-switch designs, `docs/testing.md` and the release checklist say "deferred" rather than dropping the word. The four §2 rows (two app docs, two vault rows) carry the wording.

---

## 7. What is deliberately NOT in this plan

- The other four `@react-native-firebase/*` packages, the three gradle plugins, `firebase.json`, the plist and the json — untouched.
- The `/api/v4/features` toggle system and `useFeaturesRefresh` — untouched; it is the reason this can go.
- Dropping `FirebaseRemoteConfig` / `FirebaseABTesting` / `FirebaseRemoteConfigInterop` from the Pods — not possible while Performance Monitoring and Crashlytics stay; the binary keeps the SDK, the app stops driving it.
- A Firebase SDK or RNFB version bump. `24.0.0` stays on the four.
- A recursive "no importer anywhere" test (§4 says why).
- Deleting or trimming any plan, section or doc line that mentions Remote Config — each is marked **deferred**, never removed (C‑3).

---

## 8. Expected diff

| File                                                  | Change                                                            |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| `package.json`                                        | −1                                                                |
| `yarn.lock`                                           | −6 (the one block)                                                |
| `src/utils/firebase.js`                               | −15 (import + section)                                            |
| `src/navigation/AppNavigatorContainer.js`             | −2, comment reworded                                              |
| `jest.setup.js`                                       | −13                                                               |
| `ios/Podfile.lock`                                    | ≈ −10 (block, subspec, source, checkout, checksum)                |
| `ios/Podfile`                                         | comment only                                                      |
| `docs/testing.md`, `docs/todos/PRODUCTION_RELEASE_CHECKLIST.md` | one line each                                            |
| `src/utils/__tests__/firebaseModules.config.test.js`  | new, ~60 lines                                                    |

## 9. What "execute" runs

```sh
# red
APP_ENV=testing npx jest src/utils/__tests__/firebaseModules.config.test.js   # expect 4 / 5 red
git commit -m 'test(firebase): the app has no Remote Config — package, module, mock, pod (red)'

# green
yarn remove @react-native-firebase/remote-config
#   edit: src/utils/firebase.js, src/navigation/AppNavigatorContainer.js, jest.setup.js,
#         ios/Podfile (comment), docs/testing.md, docs/todos/PRODUCTION_RELEASE_CHECKLIST.md
(cd ios && bundle exec pod install)
git diff --stat ios/Podfile.lock                # only RNFBRemoteConfig / Firebase/RemoteConfig lines
APP_ENV=testing npx jest src/utils/__tests__/firebaseModules.config.test.js   # 5 / 5
yarn test                                        # 160 / 3634 expected
yarn lint                                        # on the touched files
rg -n --hidden -g '!node_modules' -g '!ios/Pods' -i 'remote-config|remoteConfig|RemoteConfig' .
#   expected survivors only: yarn.lock @firebase/remote-config* (web SDK via firebase@12.10.0),
#   Podfile.lock FirebaseRemoteConfig* (via Performance/Crashlytics), the Podfile comment, the new test
git commit -m 'chore(firebase): remove @react-native-firebase/remote-config — deferred; toggles ride /api/v4/features'

# smoke (a) (b) (c) from §4, each reverted; then the device boot from §3 step 4
```

## 10. Rounds (dated)

- **2026-09-27, emulator boot (§3 step 4):** `react-native run-android --no-packager` against `emulator-5554` (Pixel_10_Pro_Fold, API 37), Metro on `APP_ENV=testing`, `adb reverse 8081`: BUILD SUCCESSFUL in 2 m 1 s (473 tasks; the RNFB config module is no longer in the generated `PackageList`). Cold start, logcat: `RNFBCrashlyticsInit: initialization successful`, `FirebaseCrashlytics: Saved version control info`, Analytics (`FA`) up, `ReactNativeJS: Running "dzzlo_oms_app"`, `App Version: 1.79`, the stored dealer session still valid (`expirationTime 11 days`), then `[v4] ping { version: v4 }` and `[v4] features { screen_v2_dealer_customers: true }` — the toggle channel that replaced Remote Config, answering. No `[firebase] … failed` warning, no `RemoteConfig` line anywhere in the log. Screen (inner display `-d 4619827259835644672`, 2076 × 2152 — the outer panel captures black while the fold is open): the dealer's Orders list with live data (Pending 4 / History 11), i.e. login, navigation and the v3 API all fine on the new binary. Metro stopped by its own PID afterwards (the "Fast Refresh disconnected" banner is that); the emulator kept its app.
- **2026-09-27, executed:** the user: "execute". HEAD had moved to `18a136e6` (the user committed the pending customers work; tree clean); every anchor in §2 re-verified there. **Red `bcfd1ebf`** — `src/utils/__tests__/firebaseModules.config.test.js`, 4 / 5 red (the four-package set, the helper, the mock, the pod; the version case green). **Green `ad40ed71`** — 9 files, +12 / −103: `yarn remove` (yarn.lock also dropped `p-defer`, `react-native-fetch-api`, `text-encoding`, `web-streams-polyfill` — pulled by nothing else), the two source edits, the mock, the Podfile comment, `pod install` (Podfile.lock: exactly the `RNFBRemoteConfig` block, the `Firebase/RemoteConfig` subspec, its source / checkout / checksum lines and the Podfile checksum; `FirebaseRemoteConfig`, `FirebaseRemoteConfigInterop`, `FirebaseABTesting` still present at 12.10.0; `project.pbxproj` unchanged), `docs/testing.md` and the release checklist say "deferred". Config test 5 / 5; `yarn test` **160 / 3634** in 12.7 s. Lint on the touched files: one error, `AppNavigatorContainer.js` `react-hooks/exhaustive-deps` (`dispatch` in the mount effect) — pre-existing at `18a136e6` (the repo carries 447 lint errors), left alone. **Smoke:** (a) dependency line back → 1 / 5 red, the four-package case; (b) pre-green Podfile.lock back → 1 / 5, the pod case; (c) `getRemoteValue` export back → 1 / 5, the helper case; each reverted, tree clean, 0 / 5. Survivors of `rg remote-config|RemoteConfig`: yarn.lock's `@firebase/remote-config*` (web SDK via `firebase@12.10.0`), Podfile.lock's `FirebaseRemoteConfig*` (via Performance / Crashlytics), the Podfile comment, `docs/testing.md`'s "deferred", the new test — as §9 expected. **Vault (C‑3):** one dated "DEFERRED 2026-09-27" line under the title of each of the five tasks_05 notes that name Remote Config (`FIREBASE_INTEGRATION_PLAN`, `FIREBASE_ANALYTICS_PLAN` — added to the four the plan listed, it names Remote Config triggers — and the three `FIREBASE_NOTIFICATIONS_*`); nothing deleted. Not pushed. Emulator boot: the entry above this one.
- **2026-09-27, calls answered:** the user: "calls - land commits in release/v1_79 branch. leave firebase console to me. all notes and docs files should update remote-config as deferred. do not delete any plan, just update deferred." C‑1 → two commits on `release/v1_79`, PR #55; C‑2 → the user's; C‑3 → every note and doc line marks Remote Config **deferred** with nothing deleted. §1, §2 (four rows), §3, §6, §7 and the green commit subject carry the answers. **Waits for "execute".**
- **2026-09-27, planned:** survey of the repo (`rg` over everything but `node_modules` / `ios/Pods`; `git log -S`): two importers, one mock, one dependency line, the iOS lock; `getRemoteValue` never imported in any commit; `initRemoteConfig` only ever called with `{}`; the toggle system found server-side in `/api/v4/features`; `Podfile.lock` shows `FirebasePerformance → FirebaseRemoteConfig → FirebaseABTesting`, so the SDK pods stay. Suite baseline 159 / 3629 in 12.3 s. Plan written; **waits for "execute" and C‑1 … C‑3.**
