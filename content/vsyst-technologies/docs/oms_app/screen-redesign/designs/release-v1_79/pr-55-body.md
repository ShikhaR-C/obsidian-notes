<!-- Testing workflow & the reasoning behind this checklist: docs/testing.md -->

## What & why

v1.79 ships the two redesigned screens — **Dealer Customers** and **Daily Summary** (both roles), everything on PR #50 with #49 and #51–#54 collapsed into it — with the two features the rest of the app does not have **switched off for this release**: every route is **portrait** and the app is **English only**. Decided by the user on 2026-09-24/25; the plan, the calls and the verdicts are in the vault: `docs/oms_app/screen-redesign/10-release-v1_79-portrait-english-plan.md`.

It is a **surface removal**, not a deletion of the machinery:

- **Orientation.** `screenOptionsFor` answers `PORTRAIT_ONLY` for a v2 route too (`ANY_ORIENTATION` stays exported as the value to restore); the manifest is back to `screenOrientation="portrait"` with no `resizeableActivity`; Info.plist is Portrait only with no `~ipad` key. Every v1 stack's portrait pin and `orientation.stacks.test.js` are unchanged. `orientation.config.test.js` is **inverted**: it now pins the 1.78 declarations, so a merge that re-unlocks the natives fails a test.
- **Language.** `LanguageProvider` gains a `locked` prop and the app root mounts `<LanguageProvider locked="EN">` — no storage read, no AppState listener, `setSetting` a no-op. The Settings language row is removed and its `strings.js`, `strings.hi.js` and `Language.test.js` deleted (`NoLanguageRow.test.js` pins the absence). `android:localeConfig`, `res/xml/locales_config.xml` and `CFBundleLocalizations` are removed; `locales.config.test.js` is **inverted** and pins that neither OS is told the app speaks Hindi.
- **Stays, dormant:** everything else under `src/i18n/`, `useStrings`, the `{ en, hi }` tables and the 12 Hindi-rendering test files (`renderScreen` still mounts the provider unlocked), the JSX-literal lint guard, `useWindowClass` / `Container` / the wide-window layouts and their 844 × 390 tests, the Android 15 text theme.
- **Version:** Android `1.79` / `104`, iOS `1.79` / build `1` — the iOS build number restarts at 1 with each marketing version in this app (1.75 shipped at 1, 1.76 and 1.77 at 4, 1.78 at 9); Android's `versionCode` keeps rising.
- **Ship order (plan §6):** the API's `release/v1_79` goes to production **first** — `api_v4/` is not on `master`, and both new screens read v4 read models with the toggle default *on*. Then the rollback rehearsal on staging (`screen_v2_dealer_customers` → `false`, foreground, v1 returns, flip back), the device pass, internal track / TestFlight, Play staged 20 % → 100 % over 48 h, 7-day watch.

**Known, on purpose:** an Android 16 display ≥ 600 dp wide (an unfolded Fold, a tablet) ignores `screenOrientation` and still rotates — exactly as 1.78 did (vault `06-all-screen-shapes-plan.md` §3.1). Phones do not rotate anywhere.

## Commits (red → green pairs, oldest first)

| #    | Commit     | Subject                                                                                     |
| ---- | ---------- | ------------------------------------------------------------------------------------------- |
| O‑1  | `ac54132b` | test(nav): screenOptionsFor answers portrait for a v2 route too — v1.79 ships portrait (red) |
|      | `b418a3b1` | feat(nav): pin every route portrait for v1.79; ANY_ORIENTATION exported for the unlock       |
| O‑2  | `f9514e7e` | test(theme): the native config declares portrait only, as in 1.78 (red)                      |
|      | `979ac12e` | chore(native): revert the orientation unlock — manifest portrait, plist Portrait, no ~ipad key |
| L‑1  | `19334d13` | test(i18n): a locked LanguageProvider renders English on a Hindi phone and ignores storage (red) |
|      | `625bb8d6` | feat(i18n): LanguageProvider locked — no storage read, no AppState listener, setSetting a no-op |
| L‑2  | `09fcf973` | test(nav): the app root mounts the provider locked to EN (red)                               |
|      | `e9cb96a4` | feat(nav): mount LanguageProvider locked="EN" in AppNavigatorContainer                       |
| L‑3  | `664197bc` | test(settings): Settings renders no language row (red)                                       |
|      | `108fa6fd` | feat(settings): remove the language row; delete its strings and its tests (verdict in the PR) |
| L‑4  | `1f643b0b` | test(i18n): neither OS is told the app speaks Hindi (red)                                    |
|      | `8418dc31` | chore(native): remove localeConfig, locales_config.xml and CFBundleLocalizations             |
| D‑1  | `50f8f1df` | docs(release): v1.79 ships portrait and English — AI.md, testing.md, v2 README, the two screen docs |
|      | `af88d913` | docs(code): comments follow v1.79 — declarations are 1.78's, the registry answers portrait, no OS language registration |
| R‑1  | `26e75f5b` | chore(release): bump v1.79 build (android 104, ios 10)                                       |
|      | `4b45cc0b` | chore(release): iOS build number starts at 1 for 1.79                                        |

Each red commit was run red before its green: O‑1 7 failing (5 registry cases + 2 in `DailySummaryCutover.test.js`, which asserted the old `'default'` answer and was flipped in the same red commit), O‑2 5 failing, L‑1 4 failing, L‑2 1 failing, L‑3 1 failing, L‑4 3 failing.

## Mutation smokes (each reverted; tree clean)

| Pair | Break                                                   | Result                                              |
| ---- | ------------------------------------------------------- | --------------------------------------------------- |
| O‑1  | `ANY_ORIENTATION` back in the v2 arm                     | 6 red (4 registry cases + 2 Daily Summary cutover)  |
| O‑2  | manifest back to `unspecified`                           | 2 red                                               |
| O‑2  | `UIInterfaceOrientationLandscapeLeft` back on iPhone     | 1 red                                               |
| L‑1  | locked provider reads storage                            | 1 red (stored HI)                                   |
| L‑1  | locked provider registers the AppState listener          | 1 red (no-listener)                                 |
| L‑1  | `setSetting` guard dropped                               | 1 red                                               |
| L‑1  | any `locked` value locks                                 | 1 red (invalid value)                               |
| L‑2  | `locked="EN"` dropped from the app root                  | 1 red                                               |
| L‑3  | a `language-EN` testID rendered again                    | 1 red                                               |
| L‑4  | `CFBundleLocalizations` re-added                         | 1 red                                               |
| L‑4  | `android:localeConfig` re-added                          | 1 red                                               |

## Test verdicts

- **`screenRegistry.test.js` — four `'default'` assertions:** changed, not deleted. The rule "the v2 screen may rotate" is switched off for v1.79 by decision; the cases pin the switched-off answer. The SENSOR-mapping guard now pins the exported `ANY_ORIENTATION`, so the restore stays guarded.
- **`orientation.config.test.js`:** inverted. Built to fail a straight revert of the unlock; v1.79 *is* that revert, by decision. Same file, same purpose, opposite fixture (10 → 9 cases).
- **`locales.config.test.js`:** inverted. Same reasoning; pins the absence and the development region (6 → 4 cases).
- **`Settings/__tests__/Language.test.js` (11 cases in 4 describes):** deleted with the row. The behaviour they pinned — a Language row in three scripts — is not rendered in v1.79 (user, 2026-09-25, call C‑3 approved). Replaced by `NoLanguageRow.test.js`. They return from `f4b43b98` with the row.
- **`DailySummaryCutover.test.js`:** one assertion flipped from `'default'` to `'portrait'` (same verdict as the registry cases).
- **`LanguageProvider.test.js` (17 cases) and the 12 Hindi-rendering test files:** unchanged; +5 cases pin `locked`.

**Suite:** 145 suites / **3,547** tests green in 12 s (base `f4b43b98`: 144 / 3,552 — −11 `Language.test.js`, +1 `NoLanguageRow`, +5 provider `locked`, +3 `language.lock`, −1 `orientation.config`, −2 `locales.config`). ESLint: 0 errors on every touched file; the one pre-existing `react-hooks/exhaustive-deps` error in `AppNavigatorContainer.js:97` is untouched.

## Testing checklist

- [ ] Bugfix PRs contain the regression test, written first — n/a (no bugfix)
- [ ] New business flow → screen-risk note — n/a (no new flow; two screens' surface switched off)
- [x] Tier 3 decision tests written red-first (`renderScreen`) — `NoLanguageRow.test.js`
- [x] No test deleted or `.skip`'d without a written verdict — see **Test verdicts**
- [x] Suite runtime budget respected (app ≤ 2 min) — 12 s
- [ ] API contract changed? — no; fixtures untouched

## Before store submission (plan §6, the user's steps)

1. API `release/v1_79` on production; `GET /api/v4/ping` and `GET /api/v4/app/features` answer a bearer.
2. Rollback rehearsal on staging for the three `screen_v2_*` keys.
3. Device pass on release builds, both platforms: nothing rotates on a phone (Customers, Daily Summary, the date sheet, startup, login); a Hindi phone gets **English** on both v2 screens; Settings shows the theme row and **no** language row; Android's App languages list has no entry for the app; iOS Settings › Apps › Dzzlo OMS has no Language row; 200 % text on both v2 screens; the v3 screens around them.
4. Store copy: "Customers and Daily Summary redesigned." Nothing about Hindi or landscape.
