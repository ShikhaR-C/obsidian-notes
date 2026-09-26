# 10 — Release v1.79: the two redesigned screens, portrait and English (plan)

> **What this is:** the plan the user asked for on **2026-09-24** — "we have v2 screen for 2 screens. we want to deploy an app update with these two screens. as our other screens do not support hindi, orientation, etc features provided in v2 screens. how should we provide update?" · "could we disable some files updates so that we get new designs with older app structure? like orientation or language settings" · "create new branch from #50 and name it release/v1_79. then create a plan to remove orientation and language support updates added." · "just plan now, we will implement later".
> **Status:** **BUILT, PUSHED AND OPEN AS APP PR #55 — `release/v1_79` → `slave`** (2026-09-25) — 16 commits over PR #50's head `f4b43b98` (`ac54132b` … `4b45cc0b`, §5; Android 104 / iOS build 1), **145 suites / 3,547 tests** green in 12 s, ESLint 0 errors on every touched file, the four builder worktrees removed. The PR body (verdicts, smokes, the commit table, the §6 device pass) is `designs/release-v1_79/pr-55-body.md`. The user merges; nobody else does. Baseline before the work: 144 / 3,552.
> **Calls:** **all six answered by the user on 2026-09-25** (§8, the words quoted): surface removal; every native orientation declaration back to 1.78; the four deletions approved; PR base `slave`; the Daily Summary card deferred to its own round; the Android 15 text theme kept. The recommendation had been to ship both features on and set expectations instead (§9, 2026-09-24); the user chose removal, and this plan is the removal.
> **Source:** the code as read on 2026-09-24 at `f4b43b98`. API: `api_v4/` exists on **`release/v1_79` @ `292d64f` only** — `master` and `slave` (`6a7df4f`) do not have it. Every file reference below was opened that day.
> **Companions:** [[02-foundations#F-APP-9 — Orientation and large screens (2026-09-07, "plan them and add them")|02 §F-APP-9]] and [[02-foundations#F-APP-10 — Language: English and Hindi (2026-09-07)|02 §F-APP-10]] (what is being switched off, as built), [[04-orientation-decisions]] (why v1 is pinned — unchanged by this), [[03-per-screen-playbook#Step 5 — Ship|03 §Step 5]] (the ship steps this release follows), [[00-overview]] D3 / D10.

---

## 0. The change in one table

|                                | On `release/v1_79` today (= PR #50)                                                                                                          | v1.79 as planned                                                                                                     | Comes back when                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Rotation**                   | Customers and Daily Summary rotate (`orientation: 'default'` from the registry); every v1 stack pinned portrait; both platforms declare all | **Every screen portrait on a phone**, as in 1.78: the registry answers portrait for v2 too; the native declarations are 1.78's. (As in 1.78, an Android 16 display ≥ 600 dp — an unfolded Fold, a tablet — ignores the pin and still rotates; [[06-all-screen-shapes-plan]] §3.1) | One line in the registry + the two native declarations (§2.4)                      |
| **Language**                   | SYSTEM / EN / HI on the device; a Settings row; both OSes told the app speaks Hindi; the two v2 screens render Hindi                         | **English everywhere**: the provider is locked to `EN`; no Settings row; neither OS is told                          | Unlock the provider, restore the row and the two declarations (§3.5)               |
| **Text size**                  | v2 honours 200 %; v1 never capped it either (0 files with `allowFontScaling` / `maxFontSizeMultiplier`)                                      | **Unchanged** — nothing to remove                                                                                    | —                                                                                  |
| **The new design**             | Customers (dealer) and Daily Summary (both roles), on v4 read models, behind `screen_v2_*` toggles                                            | **Ships**                                                                                                            | —                                                                                  |
| **Hindi copy + strings tables** | `{ en, hi }` per screen, `useStrings`, the lint guard, 13 test files rendering in Hindi                                                     | **Stays, dormant** — resolves to `en` at runtime; tests unchanged                                                    | —                                                                                  |
| **Native, other**              | iOS SceneDelegate + Podfile deployment-target loop (Xcode 27), Android 15 text theme (`useBoundsForWidth` off)                               | **Stays** — toolchain requirements and a harmless fix                                                                | —                                                                                  |

---

## 1. What "remove" means here

**Scope: the user-facing behaviour goes back to 1.78. The machinery stays, switched off.** Two reasons, both about cost:

1. **The strings tables are the house convention, not a feature.** `AI.md` requires every v2 string in `{ en, hi }` through `useStrings`, and ESLint refuses a JSX literal under `src/{screens,components}/v2`. Deleting the Hindi halves would mean rewriting two screens, a shared sheet and their 13 Hindi test files, and writing them again the release Hindi returns. Switching the provider off costs one prop.
2. **Both features are one seam from off.** Orientation was built so that *one* place — the registry — decides who rotates (F-APP-9); language was built so that *one* provider decides the script (F-APP-10). The removal uses the seams they left.

What **goes** (user-visible or OS-visible): the v2 routes' rotation, the native orientation unlock, the Settings language row, the OS language registration, and the possibility of the app rendering Hindi. What **stays**: everything under `src/i18n/`, `useStrings`, the `strings.hi.js` files and their completeness tests, `SCRIPT_LINE_HEIGHT` in `AppText` / `useTypeScale`, `Screen`'s `fs:${fontScale}:${language}` key, the lint guard, the harness's `{ language }` / `withLanguage`, `useWindowClass`, `Container`, the wide-window layouts and the tests that run at 844 × 390 (they pin layout rules that a Fold or an iPad still reaches in portrait), the Android 15 text theme, the per-stack `orientation: 'portrait'` pins and `orientation.stacks.test.js`.

Rule kept from `AI.md`: **no test is deleted or `.skip`'d without a written verdict** — §7 lists every test this touches and its verdict.

---

## 2. Orientation

### 2.1 The seam — `src/navigation/screenRegistry.js`

`screenOptionsFor(roleRoute, features)` (line 178) returns `ANY_ORIENTATION` (`{ orientation: 'default' }`) for a route running v2 and `PORTRAIT_ONLY` for one rolled back. Every stack already spreads `orientation: 'portrait'` in its `sharedScreenOptions`; the v2 route overrides it by spreading `screenOptionsFor(...)` into its own options (`Dealer/Main.js:180`, `:205`; `Customer/Main.js:208`).

**Change:** `screenOptionsFor` returns **`PORTRAIT_ONLY` in both arms**. The lookup, the `__DEV__` throw and the release-build fallback keep their shape. `ANY_ORIENTATION` stays defined and **exported** as the value to restore, so the test that pins `'default'` → `SCREEN_ORIENTATION_UNSPECIFIED` in the installed `react-native-screens` (the auto-rotate guard) keeps guarding the restore path. The header comment records the 2026-09-24 decision and points here.

**Why not remove the call sites?** `orientation.stacks.test.js` pins that the v2 route *spreads* the registry's answer rather than hard-coding one. Keeping that means re-enabling is one file, and the registry stays the one place that knows.

### 2.2 The native declarations — back to 1.78

| File                                          | Today (F-APP-9)                                                                  | v1.79                                                                 |
| --------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `android/app/src/main/AndroidManifest.xml:18` | `android:screenOrientation="unspecified"`                                        | `android:screenOrientation="portrait"`                                |
| `AndroidManifest.xml:19`                      | `android:resizeableActivity="true"`                                              | line removed (1.78 had none)                                          |
| `AndroidManifest.xml:20`                      | `configChanges` with `orientation\|screenLayout\|screenSize\|smallestScreenSize` | **keep** — 1.78 had it too; it only stops the activity restarting     |
| `ios/dzzlo_oms_app/Info.plist:97`             | `UISupportedInterfaceOrientations`: Portrait + LandscapeLeft + LandscapeRight    | Portrait only                                                         |
| `Info.plist:103`                              | `UISupportedInterfaceOrientations~ipad`: all four                                | key removed (1.78 had none; `TARGETED_DEVICE_FAMILY = 1,2` unchanged) |

This was **C‑2 — decided 2026-09-25: revert, "all native orientation declarations"** (the whole table above, iPad key included). The alternative — keep the declarations and rely on the JS pin alone — works for every native-stack screen, but the moments no stack owns (the startup screen, the Suspense fallback, the drawer's own container, a modal outside a stack) were never run on a device with the manifest at `unspecified` and no rotating screen in sight. 1.78's declarations were nine releases of proof.

### 2.3 Tests

- `src/navigation/__tests__/screenRegistry.test.js` §"screenOptionsFor — the v2 screen is the one that may rotate" (lines 209–270): four cases flip from `'default'` to `'portrait'` — "lets the v2 screen rotate", "lets it rotate with no map at all", "follows resolveScreen exactly — one decision, two answers" (becomes "one decision, one answer — until the unlock returns"), "hands back an object a navigator can safely spread". The rolled-back, `__DEV__` and release-fallback cases are unchanged. §"honours the auto-rotate switch" (278–311) re-points its first case at the exported `ANY_ORIENTATION` instead of `screenOptionsFor(...)`, so the mapping is still pinned for the day it is used again.
- `src/theme/__tests__/orientation.config.test.js`: **inverted, not deleted.** It was written so that "a straight revert cannot pass" (its own comment, line 63). For v1.79 it pins the opposite: iPhone key `['UIInterfaceOrientationPortrait']`, no `~ipad` key, manifest `screenOrientation="portrait"`, no `resizeableActivity`, and the four `configChanges` entries kept. Purpose unchanged: a merge from the redesign stack that re-unlocks the natives fails a test. Verdict in §7.
- `src/navigation/__tests__/orientation.stacks.test.js`: **unchanged** — every stack still pins portrait, the v2 route still spreads the registry.
- No screen test changes: nothing in `src/screens/v2/**/__tests__` asserts the route's `orientation`; the 844 × 390 cases exercise `useWindowClass`, which stays.

### 2.4 Restore path (for the record)

One line in `screenOptionsFor` (`PORTRAIT_ONLY` → `ANY_ORIENTATION` in the v2 arm), the two native declarations, and the two test files back to their `f4b43b98` versions (`git checkout f4b43b98 -- <file>` for the tests and the natives). A store release either way — CodePush is off.

---

## 3. Language

### 3.1 The seam — `LanguageProvider`, mounted in `AppNavigatorContainer.js:174`

`src/i18n/LanguageProvider.js` holds the setting (`SYSTEM` default, read from `@dzzlo/language` on mount), watches the device locale on every foreground, and `resolveLanguage(setting, deviceLocale)` decides `'en' | 'hi'`. `useLanguage()` **without** a provider follows the device on purpose (`useLanguage.js:9–16`): every v2 component test renders with a `ThemeProvider` only, and `withLanguage('hi', fn)` moves the *device*. So the lock must be **in the provider the app mounts**, not in `resolveLanguage` or the no-provider fallback — either of those would turn 13 Hindi test files red for the wrong reason.

**Change:** `LanguageProvider` gains one prop, **`locked`** (`'EN'`; the type is a language setting). Locked, the provider: starts at that setting, **does not read storage**, **does not listen to `AppState`**, does not read the device locale, and its `setSetting` is a no-op. `AppNavigatorContainer` mounts `<LanguageProvider locked="EN">`. The test harness's `renderScreen` keeps mounting the provider **unlocked**, so `{ language: 'hi' }` still renders Hindi in Jest (`src/test/testUtils.js:352`).

Considered and rejected:
- `initialSetting="EN"` alone — a stored `HI` still wins on mount (`LanguageProvider.js:69–86`). Nothing in v1.79 writes the key, but a phone that ran a debug build with the row would carry one. The lock has to ignore storage.
- Not mounting the provider — the no-provider path follows the device, so a Hindi phone would still get Hindi on the two screens.
- A build constant in `languages.js` — breaks the Hindi tests, or needs a test-only override, which is a second seam.

### 3.2 The Settings row — `src/screens/Common/Settings/index.js`

The row (lines 47, 51–53, 170–200, styles `languageButtonText` at 450–455) and its two strings files go:
- remove `LANGUAGE_OPTIONS`, the `useLanguage` / `useStrings` calls, the row's JSX and its styles; the theme row above it is untouched;
- **delete** `src/screens/Common/Settings/strings.js` and `strings.hi.js` (their only consumer is the row — the file's own header says "Only this row: the rest of Settings is still v1 copy");
- **delete** `src/screens/Common/Settings/__tests__/Language.test.js` (four cases describing a row that is not rendered) and add one Tier 3 decision test in its place: Settings renders **no** `language-SYSTEM` / `language-EN` / `language-HI` testID (red against today's screen, green after the removal).

The three deletions here, plus `locales_config.xml` in §3.3, were **C‑3 — approved 2026-09-25** (every `git rm` is gated, [[00-overview#Governance|00 §Governance]]; this is the approval).

### 3.3 The OS registration — back to 1.78

| File                                           | Today (F-APP-10)                                    | v1.79                                                      |
| ---------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------- |
| `android/app/src/main/AndroidManifest.xml:11`  | `android:localeConfig="@xml/locales_config"`        | attribute removed                                          |
| `android/app/src/main/res/xml/locales_config.xml` | `<locale-config>` en + hi                        | **file deleted** (C‑3, approved)                           |
| `ios/dzzlo_oms_app/Info.plist:9`               | `CFBundleLocalizations` `[en, hi]`                  | key removed; `CFBundleDevelopmentRegion` `en` stays        |

Without these, Android 13+ does not list the app under Settings › System › Languages › App languages, and iOS shows no Language row under Settings › Apps › Dzzlo OMS — which is the point: an app that will not honour a Hindi pick must not offer one. (Verify on device, §6: if iOS still shows a Language row, the bundle carries a stray `hi.lproj`, and that goes too.)

### 3.4 Tests

- `src/i18n/__tests__/LanguageProvider.test.js`: **add** a describe "locked — v1.79 ships English only": a Hindi device renders `en`; a stored `HI` is ignored (and not cleared — the value survives for the release that unlocks); `setSetting('HI')` changes nothing and writes nothing; no `AppState` listener is registered. The existing 17 cases stay — they describe the unlocked provider `renderScreen` still uses.
- `src/navigation/__tests__/`: **add** `language.lock.test.js`, a source pin in the shape of `orientation.stacks.test.js`: `AppNavigatorContainer.js` mounts `<LanguageProvider locked="EN"`. (A render test of the container drags in OneSignal and the role navigators; the source pin is what the house already does for the stack pins.)
- `src/i18n/__tests__/locales.config.test.js`: **inverted, not deleted** — pins that Info.plist has **no** `CFBundleLocalizations`, keeps `CFBundleDevelopmentRegion` `en`, that the manifest's `<application>` has **no** `android:localeConfig`, and that `res/xml/locales_config.xml` **does not exist**. Same purpose as before: a merge that re-registers the languages fails a test. Verdict in §7.
- `src/screens/Common/Settings/__tests__/Language.test.js` → replaced by the no-row decision test (§3.2).
- **Unchanged and still green:** `languages.test.js`, `deviceLocale.test.js` (18), `useStrings.test.js`, `androidText.config.test.js`, `src/test/__tests__/testUtils.language.test.js`, and the 12 screen/component files that render in Hindi (`CustomersHindi.test.js`, `DailySummaryShapes.test.js`, `DateRangeSheet.test.js`, …) — every one mounts its own provider through `renderScreen` or moves the device with `withLanguage`, and neither path sees the app root's lock.

### 3.5 Restore path

Drop the `locked` prop in `AppNavigatorContainer`, `git checkout f4b43b98 --` the Settings screen, its two strings files and `Language.test.js`, the manifest attribute, `locales_config.xml`, the plist key and `locales.config.test.js`; delete `language.lock.test.js`; keep the provider's `locked` prop and its tests (a seam that costs nothing). One release.

---

## 4. What ships unchanged — and must

| Piece                                                                                  | Why it cannot be left out                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/store/apis/v4/`, `API_URL_V4`, the five env files                                 | Both screens read v4 read models; `useFeaturesRefresh` reads `GET /api/v4/app/features`                                                                                                                           |
| The registry, `resolveScreen`, `screenOptionsFor`, `useScreenFlag`                     | The rollback path: `screen_v2_dealer_customers` / `screen_v2_dealer_dailysummary` / `screen_v2_customer_dailysummary` set to `false` on the superadmin page returns v1 with no store release                          |
| `src/theme/`, `src/components/v2/`, `src/screens/v2/`                                  | The design                                                                                                                                                                                                        |
| iOS `SceneDelegate`, `UIApplicationSceneManifest`, the Podfile deployment-target loop  | Xcode 27 / iOS 27 SDK requirements (`AppDelegate.swift`, `Info.plist`, `Podfile` on the branch's native diff) — nothing to do with either feature                                                                  |
| `android/app/src/main/res/values/styles.xml` (`useBoundsForWidth` off) + its test      | Android 15's bounds-based line breaking wrapped Devanagari tails onto an invisible line at non-integer densities; harmless for English; needed the day Hindi returns. Pinned by `androidText.config.test.js`. **C‑6 — kept (2026-09-25)** |
| The API's `release/v1_79` on production **before** the app                             | `api_v4/` is on that branch only. A 1.79 app against today's production `master` gets a 404 on both new screens' read models — and the toggle default is *on*                                                        |

---

## 5. Commits, in order (red → green, mutation smoke each)

The branch is `release/v1_79`. Each pair is its own two commits per `AI.md`; the smoke is done, reverted, and recorded in the PR body.

| #   | Red commit                                                                                          | Green commit                                                                                                | Smoke                                                                                                         |
| --- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| O‑1 | `test(nav): screenOptionsFor answers portrait for a v2 route too — v1.79 ships portrait (red)`       | `feat(nav): pin every route portrait for v1.79; ANY_ORIENTATION exported for the unlock`                     | put `ANY_ORIENTATION` back in the v2 arm → 4 red                                                              |
| O‑2 | `test(theme): the native config declares portrait only, as in 1.78 (red)`                            | `chore(native): revert the orientation unlock — manifest portrait, plist Portrait, no ~ipad key`             | set the manifest back to `unspecified` → 2 red; re-add LandscapeLeft → 1 red                                   |
| L‑1 | `test(i18n): a locked LanguageProvider renders English on a Hindi phone and ignores storage (red)`   | `feat(i18n): LanguageProvider locked — no storage read, no AppState listener, setSetting a no-op`            | let the locked provider read storage → 1 red; let it follow the device → 1 red                                 |
| L‑2 | `test(nav): the app root mounts the provider locked to EN (red)`                                     | `feat(nav): mount LanguageProvider locked="EN" in AppNavigatorContainer`                                     | drop the prop → 1 red                                                                                         |
| L‑3 | `test(settings): Settings renders no language row (red)`                                             | `feat(settings): remove the language row; delete its strings and its tests (verdict in the PR)`              | re-render the row → 1 red                                                                                     |
| L‑4 | `test(i18n): neither OS is told the app speaks Hindi (red)`                                          | `chore(native): remove localeConfig, locales_config.xml and CFBundleLocalizations`                           | re-add `CFBundleLocalizations` → 1 red; re-add the attribute → 1 red                                           |
| D‑1 | —                                                                                                   | `docs(release): v1.79 ships portrait and English — AI.md, testing.md, v2 README, the two screen docs`        | —                                                                                                             |
| R‑1 | —                                                                                                   | `chore(release): bump v1.79 build (android 104, ios 10)`                                                     | —                                                                                                             |

Expected suite after L‑4: 144 suites (−1 `Language.test.js`, +1 `language.lock.test.js`), roughly 3,552 − 4 + 1 + 4 + 1 + 1 tests, green, still ≈ 12 s. `yarn lint` clean on every touched file (unused `ANY_ORIENTATION` is exported, so no `no-unused-vars`; the Settings screen loses two imports).

**Built 2026-09-25 — as `release/v1_79` carries it** (cherry-picked in this order from four builder worktrees; the two extra commits are marked):

| #    | Commit     | Red run                                                     | Smokes (all red, all reverted)                                                 |
| ---- | ---------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------ |
| O‑1  | `ac54132b` → `b418a3b1` | 7 failing — 5 registry cases + 2 in `DailySummaryCutover.test.js` (it asserted the old `'default'`; flipped in the same red commit) | `ANY_ORIENTATION` back in the v2 arm → 6 red                                    |
| O‑2  | `f9514e7e` → `979ac12e` | 5 failing                                                    | manifest `unspecified` → 2 red; LandscapeLeft back → 1 red                      |
| L‑1  | `19334d13` → `625bb8d6` | 4 failing                                                    | storage read → 1; AppState listener → 1; `setSetting` guard → 1; any value locks → 1 |
| L‑2  | `09fcf973` → `e9cb96a4` | 1 failing                                                    | prop dropped → 1 red                                                            |
| L‑3  | `664197bc` → `108fa6fd` | 1 failing                                                    | a `language-EN` testID rendered → 1 red                                         |
| L‑4  | `1f643b0b` → `8418dc31` | 3 failing                                                    | `CFBundleLocalizations` back → 1; `localeConfig` back → 1                       |
| D‑1  | `50f8f1df` | — | — |
| D‑1b *(extra)* | `af88d913` `docs(code)` | comments only: the eight navigator pins, the two route comments, the `orientation.stacks` header, `deviceLocale.js`, `LanguageProvider.test.js` still described the unlock / the OS registration as current | — |
| R‑1  | `26e75f5b` | — | — |
| R‑1b *(fix)* | `4b45cc0b` `chore(release): iOS build number starts at 1 for 1.79` | the bump had set `CURRENT_PROJECT_VERSION = 10` (9 + 1); the app restarts the iOS build number with each marketing version | — |

Actual suite: **145 / 3,547** — the plan's arithmetic was off because `Language.test.js` held **11** cases in four describes (the verdict said four), the provider gained **5** cases, the source pin **3**, and the two inverted config files lost 1 and 2 cases. Facts the builders taught: RN's Jest preset keeps `AppState.addEventListener` call history across tests, so a "not called" case needs `mockClear()` in its own `beforeEach`; the app-root pin reads the source through `readCode` (`src/test/sourceText.js`) so comments never count; `NoLanguageRow`'s red failure printed "Couldn't find a navigation context" instead of the element — the assertion was right, the printer was not.

**Docs (D‑1), the lines that change:**
- `AI.md` → "Layout comes from `useWindowDimensions()`…" bullet: "Orientation is per screen … a v2 route opts in via `screenOptionsFor`" gains one sentence — *v1.79 ships every route portrait; the registry's v2 arm answers `PORTRAIT_ONLY` until the unlock is decided (vault 10)*. The Hindi bullet stays as written (it is a *writing* rule) plus one sentence — *v1.79 ships English only: the app root mounts `LanguageProvider locked="EN"`; the tables and the Hindi tests are the machinery for the release that unlocks it.*
- `docs/testing.md` → "Window classes and orientation (F-APP-9)" and "Language — English and Hindi (F-APP-10)": a **status line** at the top of each ("Switched off for v1.79 — see vault 10; the mechanism below is what the harness still runs"), nothing else rewritten.
- `src/screens/v2/README.md` line 21 (orientation from the registry): same one-line status.
- `docs/screens/customers-v2.md`, `docs/screens/daily-summary-v2.md`: a "v1.79" note under the landscape / Hindi behaviour headings — the behaviour is built and tested, not reachable in this release.
- Vault: `00-overview.md` decision-log row; `02-foundations.md` one amendment line under F-APP-9 and F-APP-10 pointing here; `04-orientation-decisions.md` "Follow-on" paragraph.

---

## 6. Ship — the v1.79 sequence (03 §Step 5, made specific)

1. **API first.** Deploy the API's `release/v1_79` to production; confirm `GET /api/v4/ping` and `GET /api/v4/app/features` answer a bearer. Additive: 1.78 keeps working, the version gate admits it.
2. **Versions** (R‑1): `android/app/build.gradle` `versionName "1.79"` / `versionCode 104`; `project.pbxproj` `MARKETING_VERSION = 1.79` and `CURRENT_PROJECT_VERSION = 1` in **both** build configurations (lines 435/446 and 470/480). **The iOS build number restarts at 1 with each marketing version** (the user, 2026-09-25: "we will start with CURRENT_PROJECT_VERSION = 1 not 10"; the tags agree — 1.75 shipped at 1, 1.76 and 1.77 at 4, 1.78 at 9); Android's `versionCode` keeps rising across versions.
3. **PR** `release/v1_79` → **`slave`** (C‑4, decided 2026-09-25); body carries the §7 verdicts and the eight smokes; CI green. The user merges; the release merge `slave` → `main` follows as it did for 1.78.
4. **Rollback rehearsal on staging** (Step 5.5): flip `screen_v2_dealer_customers` to `false` on the superadmin DB-Actions page, foreground the app, v1 Customers renders (portrait, as everything now is), flip back. Same for the two Daily Summary keys. Record in the PR.
5. **Device pass, release builds, both platforms:**
   - rotate the phone on Customers, on Daily Summary, on the date sheet, on the startup screen and the login screen → **nothing rotates** on a phone; auto-rotate on. (An unfolded Fold or a tablet on Android 16 still rotates, v1 and v2 alike, exactly as 1.78 did — not a defect of this release.)
   - a phone set to Hindi (system language and, on Android 13+ / iOS, the per-app picker) → both v2 screens **English**; Settings shows the theme row and **no language row**; Android's "App languages" list does **not** contain the app; iOS Settings › Apps › Dzzlo OMS has **no Language row**;
   - 200 % text on both v2 screens (unchanged behaviour, still worth a look);
   - Android 15 emulator at 390 dpi: English wraps as before (the text theme stays);
   - the v3 screens around them: Accounts from a customer row, the drawer, logout / login.
6. **Store copy:** "Customers and Daily Summary redesigned." Nothing about Hindi or landscape — there is nothing to tell. Play: internal track → staged 20 % → 100 % over 48 h; iOS: TestFlight → release.
7. **Watch 7 days** (Step 5.4): Crashlytics filtered to `src/screens/v2/**`, the two v4 read models' p95 and error rate, support tickets. Step 6 (delete v1 Customers, v1 Daily Summary, `RelationFilterBS.js`, `Balance/Components.js`) is 1.80's, after the window.

---

## 7. Test verdicts (for the PR body)

| Test                                                              | Verdict                                                                                                                                                                                                                                                       |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `screenRegistry.test.js` — four `'default'` assertions            | **Changed, not deleted.** The rule "the v2 screen may rotate" is switched off for v1.79 (user, 2026-09-24); the cases now pin the switched-off answer. The SENSOR-mapping guard keeps pinning `ANY_ORIENTATION` so the restore is still guarded.                |
| `orientation.config.test.js`                                      | **Inverted.** Built to fail a straight revert of the native unlock; v1.79 *is* that revert, by decision. It now fails a straight re-unlock instead. Same file, same purpose, opposite fixture.                                                                 |
| `locales.config.test.js`                                          | **Inverted.** Same reasoning: it pinned the OS registration; it now pins its absence, and the development region.                                                                                                                                             |
| `Settings/__tests__/Language.test.js` (4 cases)                   | **Deleted with the row.** The behaviour they pin — a Language row in three scripts — is not rendered in v1.79. Replaced by one decision test that the row is absent. They return from `f4b43b98` with the row.                                                 |
| `LanguageProvider.test.js` — 17 existing cases                    | **Unchanged.** `renderScreen` still mounts the unlocked provider; the cases describe it. Four new cases pin `locked`.                                                                                                                                          |
| The 12 Hindi-rendering screen/component test files               | **Unchanged.** They prove the copy and the Devanagari line height, which ship dormant and must stay correct.                                                                                                                                                  |

---

## 8. Calls — all answered 2026-09-25

The user, in one line: "1. surface removal 2. revert to v1.78 all native orientation declarations 3. approved deletions 4. PR base will be slave 5. do it later 6. as recommended. update docs". Each call below keeps its recommendation and carries the answer.

- **C‑1 — Surface removal or delete the machinery?** *Recommended: surface removal* (§1). Deleting `src/i18n`, the `hi` tables, the lint guard and the Hindi tests is a rewrite of two screens now and again later, against the house rule that Hindi is written with the English. Removing the surface is one prop, one line, two native reverts. **✅ "surface removal".**
- **C‑2 — Native orientation: revert to 1.78, or keep the declarations and rely on the JS pin?** *Recommended: revert* (§2.2). 1.78's declarations are proven; the declared-all manifest with no rotating screen was never run through the moments no stack owns. **✅ "revert to v1.78 all native orientation declarations"** — the whole §2.2 table, the iPad key included.
- **C‑3 — Approve the deletions:** `res/xml/locales_config.xml`, `Settings/strings.js`, `Settings/strings.hi.js`, `Settings/__tests__/Language.test.js`. *Recommended: yes* — all four come back with `git checkout f4b43b98 --` the release Hindi returns; keeping dead files in the tree is what the release checklist calls "half-implemented infrastructure". **✅ "approved deletions".**
- **C‑4 — PR base.** PR #46 shipped 1.78 as `v1.78/may26` → `slave`, and `main` received it as "Merge PR #46: release/v1.78". *Recommended: `release/v1_79` → `slave`*, then the release merge `slave` → `main` as before. Merging it into `slave` carries #49 and #50 (its ancestors) with it, so those two can be closed as included rather than merged separately — the user's call, since the user merges. **✅ "PR base will be slave".**
- **C‑5 — The Daily Summary summary card at large text** (marked "still undecided" in `AI.md` on 2026-09-24). *Recommended: not a blocker* — ship the card as it is; decide it in its own round. Not part of this plan. **✅ "do it later"** — deferred; the card ships as it is in v1.79 and gets its own round.
- **C‑6 — Keep the Android 15 text theme?** *Recommended: keep.* It restores the pre-Android-15 line-breaking that React Native measures against; English is unaffected either way; removing it means re-finding mechanism 7 later. **✅ "as recommended".**

---

## 9. What was recommended before the removal (2026-09-24, for the record)

Asked "how should we provide update?", the advice was to ship with both features **on**: neither is imposed (landscape needs the person to rotate with auto-rotate on; Hindi needs a choice or a Hindi phone), both degrade to 1.78's behaviour (a v1 screen snaps to portrait; an untranslated screen renders English key by key), the vault decided per-screen arrival for both, and every switch-off is a store release to undo. The suggested mitigations were a caption under the language row ("Hindi on the redesigned screens; more with every update"), the store notes, and a one-time OneSignal in-app message on the existing `app_version` trigger. If one had to go, orientation (one line, nothing lost today), not language. The user chose to remove both; §1–§8 are that.

---

## 10. Rounds (dated)

- **2026-09-25, "check changes. we will start with CURRENT_PROJECT_VERSION = 1 not 10":** the bump had carried 1.78's build 9 forward to 10; the tags show the iOS build number restarting per marketing version (1.75 → 1, 1.76 and 1.77 → 4, 1.78 → 9), so 1.79's first build is 1. Fixed as `4b45cc0b` on top (no history rewrite on the open PR), pushed; PR #55 retitled "(Android 104 / iOS 1)" and its body updated; §6 step 2 and §5 record the rule.
- **2026-09-25, "push it and open the pr now targeting slave branch" → "wifi is back, try again" → "see":** the first two attempts failed — GitHub was unreachable from the machine on every path (HTTPS on its regional and US addresses, SSH on 22 and 443, IPv6) while Google answered over the same gateway; nothing was sent. On the third, `github.com` answered and the push went through in one go: `f4b43b98..26e75f5b release/v1_79 -> release/v1_79`, **app PR #55** opened against `slave` with the body from `designs/release-v1_79/pr-55-body.md`. Next, the user's: merge; API `release/v1_79` to production first; the rollback rehearsal on staging; the §6 device pass on release builds; internal track / TestFlight; Play staged rollout; the 7-day watch before Step 6 in 1.80.
- **2026-09-25, "resume" — BUILT.** Four Opus builders in parallel worktrees (the harness's own `isolation: worktree` cut them from `main`, so all four stopped at the base check as briefed; the orchestrator then created `wt-A…D` from `f4b43b98` by hand with `node_modules` symlinked and the env files copied, and re-dispatched). A = O‑1 + O‑2, B = L‑1 + L‑2, C = L‑3 + L‑4, D = D‑1; twelve commits cherry-picked in §5 order with no conflict (A and C touch the manifest and Info.plist at different lines), then D‑1, a comment-only follow-up the builders had flagged (`af88d913`), and R‑1. **145 suites / 3,547 tests green in 12 s.** Native files: the manifest is byte-identical to `main`; Info.plist differs from `main` only by the UIScene manifest. No `*.lproj` under `ios/`. **Not done: push and PR → `slave`** — GitHub answered "Couldn't connect to server" from this machine at the end of the build; the PR body (verdicts, smokes, the commit table, the §6 device pass) is written and waits in the session scratchpad. **Follow-ups found, not in scope:** (a) `docs/testing.md` → "Screen folders and strings" still says the app is "single-language today" — stale since F-APP-10; (b) [[02-foundations]] F-APP-9 decisions 1–2 still say a v2 route sets `orientation: 'all'` (it was `'default'` before this release); (c) the device checklists in `docs/screens/customers-v2.md` and `daily-summary-v2.md` list steps a v1.79 build cannot do (rotate the phone, pick Hindi) — §6 here is the v1.79 device pass; (d) the pre-existing `react-hooks/exhaustive-deps` error at `AppNavigatorContainer.js:97` is untouched.
- **2026-09-25, "start. use agent teams." then "wrap up. we will continue later":** nothing built, nothing committed — `release/v1_79` is still clean at `f4b43b98`. One thing learned for the resume: the builders can run **in parallel in isolated worktrees** — a probe worktree at `f4b43b98` with `node_modules` **symlinked** from the main checkout and the three gitignored `.env.*` files copied in ran the registry and orientation-config suites green (59 tests, 3.4 s); the probe was removed. Resume plan: four Opus builders, each in its own worktree from `f4b43b98` — **A** O‑1 + O‑2 (registry, native orientation revert), **B** L‑1 + L‑2 (the locked provider, the app root), **C** L‑3 + L‑4 (the Settings row, the OS locale registration), **D** D‑1 (the five repo docs and the vault amendments) — then cherry-pick onto `release/v1_79` in §5's order (A and C both touch `AndroidManifest.xml` and `Info.plist` at different lines), R‑1 by hand, full suite, PR → `slave`.
- **2026-09-25, the calls answered:** the user: "1. surface removal 2. revert to v1.78 all native orientation declarations 3. approved deletions 4. PR base will be slave 5. do it later 6. as recommended. update docs" → C‑1 … C‑6 closed as recorded in §8; §2.2, §3.2, §3.3, §4 and §6 carry the answers; a decision-log row added to [[00-overview]]. **Plan agreed. Nothing implemented — waits for "start".** The next step on "start" is §5's table, O‑1 first, on `release/v1_79`.
- **2026-09-24, the question:** "we have v2 screen for 2 screens. we want to deploy an app update with these two screens. as our other screens do not support hindi, orientation, etc … how should we provide update?" → the advice in §9, with the concrete levers for each feature and the ship sequence (API first — `api_v4/` is on the API's `release/v1_79` only; a store release, since the branch carries native changes; the rollback rehearsal; staged rollout).
- **2026-09-24, the follow-up:** "could we disable some files updates so that we get new designs with older app structure? like orientation or language settings" → yes: orientation is one line in the registry; language is the provider, the Settings row and two OS declarations; text size has nothing to disable; the v4 client, registry, theme and the Xcode 27 native changes are not separable.
- **2026-09-24, the ask:** "create new branch from #50 and name it release/v1_79. then create a plan to remove orientation and language support updates added." · "just plan now, we will implement later" → `release/v1_79` created at `f4b43b98` (PR #50's head; base `app_v4_foundations`), checked out, not pushed; baseline 144 / 3,552 green in 12 s; this plan written (2026-09-25, the session ran past midnight). **Nothing implemented. Waits for "start" and the C‑1 … C‑6 answers.**
