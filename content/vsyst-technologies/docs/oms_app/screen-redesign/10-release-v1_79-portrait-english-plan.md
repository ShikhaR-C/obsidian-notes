# 10 — Release v1.79: the two redesigned screens, portrait and English (plan)

> **What this is:** the plan the user asked for on **2026-09-24** — "we have v2 screen for 2 screens. we want to deploy an app update with these two screens. as our other screens do not support hindi, orientation, etc features provided in v2 screens. how should we provide update?" · "could we disable some files updates so that we get new designs with older app structure? like orientation or language settings" · "create new branch from #50 and name it release/v1_79. then create a plan to remove orientation and language support updates added." · "just plan now, we will implement later".
> **Status:** **PLAN — waits for "start".** Branch **`release/v1_79`** created 2026-09-24 from PR #50's head **`f4b43b98`** (`app_screen_customers` with #51 → #52 → #53 → #54 collapsed into it), checked out, local only, **not pushed, nothing committed**. Baseline on it: **144 suites / 3,552 tests** green in 12 s.
> **Calls:** C‑1 … C‑6 in §8, each with a recommendation. The recommendation was to ship both features on and set expectations instead (§9, 2026-09-24); the user chose removal, and this plan is the removal.
> **Source:** the code as read on 2026-09-24 at `f4b43b98`. API: `api_v4/` exists on **`release/v1_79` @ `292d64f` only** — `master` and `slave` (`6a7df4f`) do not have it. Every file reference below was opened that day.
> **Companions:** [[02-foundations#F-APP-9 — Orientation and large screens (2026-09-07, "plan them and add them")|02 §F-APP-9]] and [[02-foundations#F-APP-10 — Language: English and Hindi (2026-09-07)|02 §F-APP-10]] (what is being switched off, as built), [[04-orientation-decisions]] (why v1 is pinned — unchanged by this), [[03-per-screen-playbook#Step 5 — Ship|03 §Step 5]] (the ship steps this release follows), [[00-overview]] D3 / D10.

---

## 0. The change in one table

|                                | On `release/v1_79` today (= PR #50)                                                                                                          | v1.79 as planned                                                                                                     | Comes back when                                                                    |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **Rotation**                   | Customers and Daily Summary rotate (`orientation: 'default'` from the registry); every v1 stack pinned portrait; both platforms declare all | **Every screen portrait**, as in 1.78: the registry answers portrait for v2 too; the native declarations are 1.78's | One line in the registry + the two native declarations (§2.4)                      |
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

This is **C‑2**. The alternative — keep the declarations and rely on the JS pin alone — works for every native-stack screen, but the moments no stack owns (the startup screen, the Suspense fallback, the drawer's own container, a modal outside a stack) were never run on a device with the manifest at `unspecified` and no rotating screen in sight. 1.78's declarations were nine releases of proof. Recommended: revert.

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

The three deletions are **C‑3** (every `git rm` is gated, [[00-overview#Governance|00 §Governance]]).

### 3.3 The OS registration — back to 1.78

| File                                           | Today (F-APP-10)                                    | v1.79                                                      |
| ---------------------------------------------- | --------------------------------------------------- | ---------------------------------------------------------- |
| `android/app/src/main/AndroidManifest.xml:11`  | `android:localeConfig="@xml/locales_config"`        | attribute removed                                          |
| `android/app/src/main/res/xml/locales_config.xml` | `<locale-config>` en + hi                        | **file deleted** (C‑3)                                     |
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
| `android/app/src/main/res/values/styles.xml` (`useBoundsForWidth` off) + its test      | Android 15's bounds-based line breaking wrapped Devanagari tails onto an invisible line at non-integer densities; harmless for English; needed the day Hindi returns. Pinned by `androidText.config.test.js`. **C‑6** |
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

**Docs (D‑1), the lines that change:**
- `AI.md` → "Layout comes from `useWindowDimensions()`…" bullet: "Orientation is per screen … a v2 route opts in via `screenOptionsFor`" gains one sentence — *v1.79 ships every route portrait; the registry's v2 arm answers `PORTRAIT_ONLY` until the unlock is decided (vault 10)*. The Hindi bullet stays as written (it is a *writing* rule) plus one sentence — *v1.79 ships English only: the app root mounts `LanguageProvider locked="EN"`; the tables and the Hindi tests are the machinery for the release that unlocks it.*
- `docs/testing.md` → "Window classes and orientation (F-APP-9)" and "Language — English and Hindi (F-APP-10)": a **status line** at the top of each ("Switched off for v1.79 — see vault 10; the mechanism below is what the harness still runs"), nothing else rewritten.
- `src/screens/v2/README.md` line 21 (orientation from the registry): same one-line status.
- `docs/screens/customers-v2.md`, `docs/screens/daily-summary-v2.md`: a "v1.79" note under the landscape / Hindi behaviour headings — the behaviour is built and tested, not reachable in this release.
- Vault: `00-overview.md` decision-log row; `02-foundations.md` one amendment line under F-APP-9 and F-APP-10 pointing here; `04-orientation-decisions.md` "Follow-on" paragraph.

---

## 6. Ship — the v1.79 sequence (03 §Step 5, made specific)

1. **API first.** Deploy the API's `release/v1_79` to production; confirm `GET /api/v4/ping` and `GET /api/v4/app/features` answer a bearer. Additive: 1.78 keeps working, the version gate admits it.
2. **Versions** (R‑1): `android/app/build.gradle` `versionName "1.79"` / `versionCode 104`; `project.pbxproj` `MARKETING_VERSION = 1.79` and `CURRENT_PROJECT_VERSION = 10` in **both** build configurations (lines 435/446 and 470/480).
3. **PR** `release/v1_79` → base per **C‑4**; body carries the §7 verdicts and the eight smokes; CI green.
4. **Rollback rehearsal on staging** (Step 5.5): flip `screen_v2_dealer_customers` to `false` on the superadmin DB-Actions page, foreground the app, v1 Customers renders (portrait, as everything now is), flip back. Same for the two Daily Summary keys. Record in the PR.
5. **Device pass, release builds, both platforms:**
   - rotate the phone on Customers, on Daily Summary, on the date sheet, on the startup screen and the login screen → **nothing rotates**; auto-rotate on;
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

## 8. Calls — each with a recommendation

- **C‑1 — Surface removal or delete the machinery?** *Recommended: surface removal* (§1). Deleting `src/i18n`, the `hi` tables, the lint guard and the Hindi tests is a rewrite of two screens now and again later, against the house rule that Hindi is written with the English. Removing the surface is one prop, one line, two native reverts.
- **C‑2 — Native orientation: revert to 1.78, or keep the declarations and rely on the JS pin?** *Recommended: revert* (§2.2). 1.78's declarations are proven; the declared-all manifest with no rotating screen was never run through the moments no stack owns.
- **C‑3 — Approve the deletions:** `res/xml/locales_config.xml`, `Settings/strings.js`, `Settings/strings.hi.js`, `Settings/__tests__/Language.test.js`. *Recommended: yes* — all four come back with `git checkout f4b43b98 --` the release Hindi returns; keeping dead files in the tree is what the release checklist calls "half-implemented infrastructure".
- **C‑4 — PR base.** PR #46 shipped 1.78 as `v1.78/may26` → `slave`, and `main` received it as "Merge PR #46: release/v1.78". *Recommended: `release/v1_79` → `slave`*, then the release merge `slave` → `main` as before. Merging it into `slave` carries #49 and #50 (its ancestors) with it, so those two can be closed as included rather than merged separately — the user's call, since the user merges.
- **C‑5 — The Daily Summary summary card at large text** (marked "still undecided" in `AI.md` on 2026-09-24). *Recommended: not a blocker* — ship the card as it is; decide it in its own round. Not part of this plan.
- **C‑6 — Keep the Android 15 text theme?** *Recommended: keep.* It restores the pre-Android-15 line-breaking that React Native measures against; English is unaffected either way; removing it means re-finding mechanism 7 later.

---

## 9. What was recommended before the removal (2026-09-24, for the record)

Asked "how should we provide update?", the advice was to ship with both features **on**: neither is imposed (landscape needs the person to rotate with auto-rotate on; Hindi needs a choice or a Hindi phone), both degrade to 1.78's behaviour (a v1 screen snaps to portrait; an untranslated screen renders English key by key), the vault decided per-screen arrival for both, and every switch-off is a store release to undo. The suggested mitigations were a caption under the language row ("Hindi on the redesigned screens; more with every update"), the store notes, and a one-time OneSignal in-app message on the existing `app_version` trigger. If one had to go, orientation (one line, nothing lost today), not language. The user chose to remove both; §1–§8 are that.

---

## 10. Rounds (dated)

- **2026-09-24, the question:** "we have v2 screen for 2 screens. we want to deploy an app update with these two screens. as our other screens do not support hindi, orientation, etc … how should we provide update?" → the advice in §9, with the concrete levers for each feature and the ship sequence (API first — `api_v4/` is on the API's `release/v1_79` only; a store release, since the branch carries native changes; the rollback rehearsal; staged rollout).
- **2026-09-24, the follow-up:** "could we disable some files updates so that we get new designs with older app structure? like orientation or language settings" → yes: orientation is one line in the registry; language is the provider, the Settings row and two OS declarations; text size has nothing to disable; the v4 client, registry, theme and the Xcode 27 native changes are not separable.
- **2026-09-24, the ask:** "create new branch from #50 and name it release/v1_79. then create a plan to remove orientation and language support updates added." · "just plan now, we will implement later" → `release/v1_79` created at `f4b43b98` (PR #50's head; base `app_v4_foundations`), checked out, not pushed; baseline 144 / 3,552 green in 12 s; this plan written (2026-09-25, the session ran past midnight). **Nothing implemented. Waits for "start" and the C‑1 … C‑6 answers.**
