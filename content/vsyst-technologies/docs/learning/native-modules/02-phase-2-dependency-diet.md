# Phase 2 — Dependency Diet: Remove, Replace, Repair

> Level: Easy | Time: ~1 h to read; each job ½ h to 1 day _(est.)_ | Outcome: five packages gone, one declared, four upgraded, 75 dead files swept, and eight native-config faults fixed — each one behind a test that was red first.

---

## 1. The One Idea

Before the app gains a single new native capability, it sheds what it does not use and repairs what is quietly broken. Nothing here is large: one package, one group of files, one config key at a time. Every item runs the same loop:

```
evidence (file:line) ──► red test (fails for today's reason) ──► change ──► Jest gate ──► build + device look (if native)
```

**The gate** is the house gate: `yarn test` (= `APP_ENV=testing jest`, CI's only job) and `yarn lint`. CI compiles no native code, so any item that touches a pod, a Gradle file, a manifest or a plist also needs a build of both platforms and a look on a device. Release prep adds `bash dzzlo_oms_api/scripts/release_gate.sh` from the `v1_79/` workspace. Red commit first, green commit second, mutation smoke in the PR, nothing committed without the user's word — see the [[vsyst-technologies/docs/oms_app/tdd-testing-guide|TDD testing guide]].

**Two config suites carry most of the reds.** Both copy the shape of `src/utils/__tests__/firebaseModules.config.test.js` — read a file off disk, assert what no import graph protects — and grow by one case per item:

```js
// src/utils/__tests__/dependencies.config.test.js   (release.config.test.js starts the same way)
import fs from 'fs';
import path from 'path';

const ROOT = path.resolve(__dirname, '../../..');
const read = rel => fs.readFileSync(path.join(ROOT, rel), 'utf8');
const { dependencies } = JSON.parse(read('package.json'));

it.each(['@react-navigation/stack' /* one row per removal, added in its red commit */])(
  'the app no longer depends on %s', name => expect(dependencies[name]).toBeUndefined());
```

**The secrets rule for config tests.** A failing `toMatch` or `toContain` prints the text it read. For any file that can hold a secret — `android/gradle.properties`, `Info.plist`, the env files — assert a boolean, `expect(/…/.test(text)).toBe(false)`, so a red run prints `true`, never the value.

**Order.** Do the dead-file sweep (§3.2) first: it deletes the only importers left for several of the packages below.

## 2. The whole diet on one page

Evidence is from the 2026-09-29 audit of `release/v1_79` — audited at `4d3ad441`, line numbers re-checked at `e29f0e5d` (2026-09-30); ✅ marks the lines re-read in that re-check.

| § | Item | Evidence | Do | First red | Risk |
| --- | --- | --- | --- | --- | --- |
| 3.1 | `@react-navigation/stack` | `package.json:44` ✅, 0 importers | `yarn remove` | dependency pin | none found |
| 3.2 | 75 unreachable files, 4 phantom packages | walk from `index.js` ✅ | delete by group | `unreachable.config.test.js` | parked work; a 2026-07-05 decision |
| 3.3 | `react-native-html-to-pdf` | imported, never called — `TcsTds/Render/index.js:5` ✅ | remove | dependency pin | none at runtime |
| 3.4 | CodePush vestiges | `system.js:1-16`, `env.d.ts:8-11`, five env files ✅ | delete names and screens | `CODEPUSH_` pin | Babel throws on a half removal |
| 4.1 | `moment` → house helpers | 7 live files ✅, 0 tests | `src/helpers/LocalDate` | frozen answers | device-local vs IST |
| 4.2 | `react-native-linear-gradient` → `react-native-svg` | 3 live files ✅ | svg gradients | DrawerBackground test | visual |
| 4.3 | compat layer | 6 packages, no `codegenConfig` | Firebase → 26.4.0; two removals | version pin | two Firebase majors |
| 5.1 | `prop-types` | 13 live importers, undeclared ✅ | declare | dependency pin | none |
| 5.2 | location purpose strings | `Info.plist:49-54` ✅ | reword, keep keys | plist pin | ITMS-90683 |
| 5.3 | `<queries>` for https | none in the manifest ✅ | add | manifest pin | none |
| 5.4 | iOS archive `APP_ENV` | `project.pbxproj:291` = `testing` ✅ | agree, pin | pbxproj pin | shipping staging |
| 5.5 | R8, ABIs, AAB | `app/build.gradle:64` ✅; 106.8 MB APK | R8 on, AAB for Play | build.gradle pin | reflection-heavy SDKs |
| 5.6 | upload-key passwords in git | `android/gradle.properties:48-49` ✅, tracked | move out, rotate | boolean pin | unsigned release |
| 5.7 | extension version 1.0 vs 1.79 | pbxproj ✅ | align | pbxproj pin | none |
| 5.8 | unused Google OAuth URL scheme | `Info.plist:25-35` ✅ | remove after a Firebase check | boolean pin | an unseen user |

## 3. Remove

### 3.1 `@react-navigation/stack`

**Evidence.** Declared at `package.json:44` (`^7.8.9`); zero source and zero test importers; no installed package depends on it — the only other mention is a *devDependency* of `react-native-screens@4.24.0`; `yarn.lock:2854-2856` holds its single entry. **Do.** `yarn remove @react-navigation/stack`. **Red.** The first row of the dependency pin above. **Risk.** None found. **Verify.** `yarn test`, then a release bundle per platform — Metro resolves the whole graph, so an import nobody noticed fails here:

```sh
APP_ENV=testing npx react-native bundle --platform ios --dev false --entry-file index.js --bundle-output "$TMPDIR/ios.jsbundle"
APP_ENV=testing npx react-native bundle --platform android --dev false --entry-file index.js --bundle-output "$TMPDIR/android.jsbundle"
```

### 3.2 The 75 unreachable files and the four phantom packages

**Evidence.** A static import walk from `index.js` reaches 603 files; **75 of the 674 non-test `src` files are unreachable** — reproduced exactly on 2026-09-30 by the script below. By folder: `screens/Common` 18, `components/SVG` 9, `screens/Dealer` 6, `components/Download` 4, `components/Input` 4, `components/{DatePicker,Pickers,Search}` 3 each, then one or two in about twenty more. The four **phantom** packages — imported but not installed — appear only in dead files: `react-native-code-push` (`components/VersionInfo/index.js:25`, `screens/Common/Settings/Codepush.js:24`, `screens/Login/AuthNavigator/BetaUser.js:12`), `react-native-image-picker` and `react-native-permissions` (`components/ImagePicker/index.js`), `rn-fetch-blob` (`components/Download/Invoice.js:1`). Walking from every test file instead of `index.js` leaves the same 75 unreached: **no test imports a dead file**, so the sweep deletes no suite.

**The method — reproducible.** Save as `scripts/unreachable.js` (next to `scripts/pull_fixtures.js`) and run `node scripts/unreachable.js` from the app root:

```js
/**
 * Lists every src/ file that no static import path reaches from index.js.
 * Parsed with Babel, not grepped, so commented-out imports do not count.
 * Relative specifiers only; .ios/.android/.native variants all count as reached.
 * src/test/ (Jest helpers) and __tests__/ are out of scope.
 */
const fs = require('fs');
const path = require('path');
const { parseSync } = require('@babel/core');

const EXTS = ['.ios.js', '.android.js', '.native.js', '.js', '.ts', '.tsx', '.json'];
const isFile = f => fs.existsSync(f) && fs.statSync(f).isFile();
const targets = (from, spec) => {
  if (!spec.startsWith('.')) return [];
  const base = path.resolve(path.dirname(from), spec);
  return [base, ...EXTS.map(e => base + e), ...EXTS.map(e => path.join(base, `index${e}`))].filter(isFile);
};
const specifiers = file => {
  if (!/\.(js|ts|tsx)$/.test(file)) return [];
  const plugins = file.endsWith('.js') ? ['jsx'] : file.endsWith('.tsx') ? ['typescript', 'jsx'] : ['typescript'];
  const ast = parseSync(fs.readFileSync(file, 'utf8'),
    { babelrc: false, configFile: false, sourceType: 'unambiguous', filename: file, parserOpts: { plugins } });
  const found = [];
  const visit = node => {
    if (Array.isArray(node)) return node.forEach(visit);
    if (!node || typeof node.type !== 'string') return;
    if (node.source && /^(Import|ExportNamed|ExportAll)Declaration$|^ImportExpression$/.test(node.type)) found.push(node.source.value);
    const [arg] = node.arguments ?? [];
    if (node.type === 'CallExpression' && arg?.type === 'StringLiteral' &&
        (node.callee.type === 'Import' || node.callee.name === 'require')) found.push(arg.value);
    for (const key of Object.keys(node)) if (!/^(loc|extra|\w+Comments)$/.test(key)) visit(node[key]);
  };
  visit(ast.program);
  return found;
};

const unreachableFiles = root => {
  const reached = new Set();
  const queue = [path.join(root, 'index.js')];
  while (queue.length) {
    const file = queue.pop();
    if (!reached.has(file)) { reached.add(file); for (const s of specifiers(file)) queue.push(...targets(file, s)); }
  }
  const walk = dir => fs.readdirSync(dir, { withFileTypes: true }).flatMap(d => {
    const p = path.join(dir, d.name);
    if (d.isDirectory()) return d.name === '__tests__' || p === path.join(root, 'src', 'test') ? [] : walk(p);
    return /\.(js|ts|tsx)$/.test(d.name) && !/\.test\./.test(d.name) ? [p] : [];
  });
  const source = walk(path.join(root, 'src'));
  return { total: source.length, dead: source.filter(f => !reached.has(f)).map(f => path.relative(root, f)).sort() };
};

module.exports = { unreachableFiles };
if (require.main === module) {
  const { total, dead } = unreachableFiles(process.cwd());
  console.log(dead.join('\n'));
  console.error(`${dead.length} of ${total} src files unreachable from index.js`);
}
```

**Red.** `src/utils/__tests__/unreachable.config.test.js` — red today with the list in its failure message, green when the sweep is done, and a guard against new dead code afterwards (the walk takes about 0.35 s on the M5 Max):

```js
import path from 'path';
const { unreachableFiles } = require('../../../scripts/unreachable');

const KEEP = ['src/types/env.d.ts']; // TypeScript's view of @env: nothing imports a .d.ts

it('every src file is reachable from index.js, or kept on purpose', () => {
  expect(unreachableFiles(path.resolve(__dirname, '../../..')).dead.filter(f => !KEEP.includes(f))).toEqual([]);
});
```

**Do — in four groups, never as one blind delete** (the audit counted the 75 but did not review each; some may be parking):

| Group | Files | Action |
| --- | --- | --- |
| (a) plain dead code | old pickers, inputs, SVGs, screens, `constants/themes/*`, `utils/Colors/defaultCombined.js` … | delete; list them in the PR |
| (b) belongs to another item | `components/Download/*` (§3.3, and the `rn-fetch-blob` phantom), `Codepush.js` · `VersionInfo` · `BetaUser.js` (§3.4), `RateSetter.js` · `NumberMeter/*` (§4.2), `Calender/Example.js` (§4.1) | delete with that item |
| (c) ask the user first | `components/ImagePicker/index.js` — its two `{ virtual: true }` mocks (`jest.setup.js:245-256`) exist by the team decision of 2026-07-05, "keep them stubbed, do not install" (`docs/testing.md:80-85`); `src/notes/Testing/apiTesting.js` (a legacy note) | the user's verdict; the camera flow returns in [[04-phase-4-images-and-scanning]] |
| (d) keep | `src/types/env.d.ts` | on `KEEP`; edited in §3.4 |

**Risk.** Deleting parked work someone meant to revive — hence the groups. **Verify.** `yarn test` (the pin goes green), both release bundles (§3.1).

### 3.3 `react-native-html-to-pdf` — imported, never called

**Evidence.** 1.3.0 (2025-09-04, no release since). Its only live importer is `screens/Common/Reports/TcsTds/Render/index.js:5`, and the component never uses it — the same file also imports `Alert`, `Platform`, `Pressable` and `FAB` without using them. Three dead importers (`components/Download/RNhtmlpdf.js`, `invoiceHTML/ShowInvoice.js`, `invoiceHTML/index.js`) go in §3.2. It is a native Turbo Module — `HtmlToPdfSpec` sits in the iOS codegen output ✅ — so removal is a native change. No live code exports, saves, shares or prints a PDF today. **Do.** Delete the five unused imports; `yarn remove react-native-html-to-pdf`; `cd ios && bundle exec pod install`. **Red.** A dependency-pin row. **Risk.** None at runtime. **Verify.** `yarn test`, both release bundles, both platforms build. The feature it once promised — invoice → PDF → share — is built properly as a native module in [[03-phase-3-files-share-and-pdf]].

### 3.4 CodePush vestiges

**Evidence.** Microsoft retired App Center, CodePush included, on 2025-03-31; the RN client is archived, and the package is not installed. What remains:

- **The live leak.** `src/constants/system.js:1-16` ✅ imports `CODEPUSH_STAGING_KEY_IOS`, `CODEPUSH_PRODUCTION_KEY_IOS`, `CODEPUSH_STAGING_KEY_ANDROID` and `CODEPUSH_PRODUCTION_KEY_ANDROID` from `@env` and re-exports them. The file is live (`createApi.js` and `helpers/OneSignal` import it), so `react-native-dotenv` inlines the four values into the shipped bundle. Whether they are empty or real keys is unknown — the values were deliberately not read.
- **The declarations.** `src/types/env.d.ts:8-11` ✅; all five env files carry the four names ✅ — `.env.example` and `.env.ci` tracked, `.env.development`, `.env.testing`, `.env.production` local only.
- **The dead screen and friends.** `Settings/Codepush.js` (530 lines), `components/VersionInfo/index.js` (632), `Login/AuthNavigator/BetaUser.js` (389) — §3.2 group (b) — plus commented-out lines at `App.js:8,31`, `components/Error/ErrorBoundary.js:6,58`, `components/NoNetwork/Undraw.js:7,53,98`.

**Do — imports before names.** `AI.md`'s env rule: any name imported from `@env` must exist in every env file, or Babel throws at transform time (`safe: true`, `allowUndefined: false`). So: (1) delete the three dead files and `system.js`'s four imports and exports; (2) the four lines in `env.d.ts`; (3) the four names in `.env.example` and `.env.ci`, and in the three local env files on every machine that has them; (4) the commented-out lines. This closes release-checklist item 8, "CodePush keys present but CodePush disabled".

**Red.**

```js
it.each(['src/constants/system.js', 'src/types/env.d.ts', '.env.example', '.env.ci'])(
  '%s carries no CodePush name', rel => expect(read(rel).includes('CODEPUSH_')).toBe(false));
```

**Risk.** A half-done removal — a name gone, an import left — breaks every Jest suite at transform, which is exactly how you would notice. **Verify.** `yarn test`; CI (it runs after `cp .env.ci .env.testing`). Over-the-air updates come back without CodePush in [[09-phase-9-security-privacy-and-release]]. Source: [Microsoft Learn: App Center retirement](https://learn.microsoft.com/en-us/appcenter/retirement).

## 4. Replace

### 4.1 `moment` → house helpers

**Evidence.** moment 2.30.1 (npm has 2.31.0, 2026-09-15; its own docs call it "a legacy project, now in maintenance mode"). Seven live files ✅, no test imports it:

| File | What moment does there |
| --- | --- |
| `screens/Common/DailySummary/index.js:20-21`, `screens/Common/Reports/DailyReport/index.js:67-68` | `new Date(moment().startOf('day'))` / `endOf('day')` |
| `screens/Dealer/NewVoucher/index.js:52-55`, `screens/Customer/NewPayAck/index.js:75-78` | module-scope `lastDayPrevMonth = moment(new Date()).subtract(1, 'months').endOf('month')` |
| `screens/Dealer/ProductDates/index.js` (98-110, 218-219, 255-286, 416-461), `screens/Common/Products/components/ProductDates.js` (81-120, 266-283, 340) | month bounds as `YYYY-MM-DD`, ±30 days, today/tomorrow, `isSameOrBefore(d, 'day')` |
| `components/Calender/Calendar.js` | `startOf('month').day()`, `daysInMonth()`, ± month/week, `isoWeekday`, `set('month')`, `date()` |

**Three traps.**

1. **Device-local vs IST.** moment reads the phone's zone. The v2 date rules in `src/helpers/DateRange/window.js` are IST by design — "IST is fixed +05:30 arithmetic: no `Intl`, moment or local-time getter" (line 5) — and import-free on purpose, because `window.zone.test.js` loads it in plain Node. The replacement must stay **device-local** (moving v1 screens to IST is a product decision, not a refactor), must not live in `window.js` or be imported by it, and must not borrow its `addMonths(monthStart, n, dayStart)` (`window.js:258`), which is IST with a different signature. New home: `src/helpers/LocalDate/index.js`, import-free for the same reason. No `Intl` is needed — the only format is `YYYY-MM-DD`.
2. **Month-end clamping.** moment's `add(1, 'month')` on 31 January lands on the last day of February; `Date#setMonth` overflows into March.
3. **`lastDayPrevMonth` is computed at import** ("static per app session", `NewVoucher/index.js:52`). A session that crosses midnight on the 1st keeps the month before last as the default effective date. That is a bug, so it is test-first.

**Red first — moment's answers frozen as literals.** Run moment once in a scratch script, paste its answers, and the tests outlive moment (the four literals below were checked against moment 2.30.1 on 2026-09-30 in IST, UTC, America/Los_Angeles and Pacific/Kiritimati):

```js
// src/helpers/LocalDate/__tests__/index.test.js — answers frozen from moment 2.30.1
import { addMonths, endOfPreviousMonth, toYmd } from '..';

const local = iso => new Date(iso); // no offset in the string = the device's zone

it.each([
  ['2026-03-31T10:00', '2026-02-28T23:59:59.999'], // 31 Mar − 1 month clamps
  ['2026-01-15T10:00', '2025-12-31T23:59:59.999'], // January → last year
  ['2028-03-01T00:00', '2028-02-29T23:59:59.999'], // leap year
])('endOfPreviousMonth(%s) = %s, as moment said', (now, expected) =>
  expect(endOfPreviousMonth(local(now))).toEqual(local(expected)));

it('adds a month the way moment does: clamped, not overflowed', () =>
  expect(toYmd(addMonths(local('2026-01-31T09:00'), 1))).toBe('2026-02-28'));
```

Anything that starts from an absolute instant — an API timestamp, an ISO string with `Z` — also needs the child-process zone technique of `window.zone.test.js` ("Jest cannot change the zone of the process it runs in"). For trap 3, a source pin through `readCode` (`src/test/sourceText.js`, comments stripped) — `expect(readCode(file)).not.toMatch(/^const lastDayPrevMonth/m)` for both files — goes red today; the fix is `useState(() => endOfPreviousMonth(new Date()))` in place of `useState(new Date(lastDayPrevMonth))` (`NewVoucher:87`, `NewPayAck:118`).

**Do.** About eight helpers — `startOfDay`/`endOfDay`, month bounds, `addDays`/`addWeeks`/`addMonths`, `toYmd`, `daysInMonth`, `isoWeekday`, `isSameOrBeforeDay`, `endOfPreviousMonth` — then swap call sites file by file, with a mutation smoke per helper. `Calendar.js` hands moment objects to its two parents through `onTouchPrev/Next` and `onSwipePrev/Next` (146-178) and an ISO string with the device's offset through `onDateSelect` (248-249, moment's default `format()`): move `Calendar.js` and both `ProductDates` files in one PR, callback contract pinned first. Then `yarn remove moment` and a dependency-pin row.

**Risk.** The v1 rate calendar and payment-date flows have no screen tests. **Verify.** `yarn test`; a device look at all seven screens, once in IST and once with the phone set to another zone. Source: [Moment.js docs, project status](https://momentjs.com/docs/).

### 4.2 `react-native-linear-gradient` → `react-native-svg`

**Evidence.** 2.8.3 (2023-09-06), no `codegenConfig`, so it runs on the interop layer. Three live uses ✅: `components/Divider/index.js:21-35` (a 1-px horizontal fade, five hex literals per theme), `navigation/Common/DrawerBackground.js:54-59` (the upright drawer band, three colours top to bottom), `screens/Login/AuthNavigator/Welcome.js:101-110` (the Log In button, right to left from `{x: 1}` to `{x: 0.2}`, wrapping its text, `borderRadius: BUTTON_BORDER_RADIUS`). Two dead importers go in §3.2. `react-native-svg` 15.15.4 is already in 160 live files, and `DrawerBackground` already paints its landscape glow with `Svg` + `RadialGradient` (lines 37-51) — the pattern to copy. RN's own `backgroundImage: linear-gradient(…)` is documented as experimental, "should not be used in production" — [RN View Style Props](https://reactnative.dev/docs/view-style-props).

**Red.** `navigation/Common/__tests__/DrawerBackground.test.js` asserts `band.props.colors` has length 3 — react-native-linear-gradient's prop. Rewrite that assertion first, in the red commit, the way the same file already reads the glow's stops:

```js
const band = screen.UNSAFE_getByProps({ id: 'drawerBand' });
const offsets = band.findAll(node => node.props.offset !== undefined).map(node => node.props.offset);
expect([offsets[0], offsets[offsets.length - 1]]).toEqual(['0', '1']);
expect(offsets).toContain('0.5');
```

`Divider` and `Welcome` have no tests: add one render test each (Divider's stops; Welcome still shows "Log In" over the gradient).

**Green.** Each gradient becomes `Svg` → `Defs` → `LinearGradient` (`x1 y1 x2 y2` as fractions) → `Stop`s → a `Rect` filled `url(#id)`; keep `testID="drawer-background-linear"` on the band's wrapper so the other cases still find it. Two traps: react-native-svg also exports a `LinearGradient`, so the old default import must go; and an svg does not take `children` or clip to its parent's `borderRadius` — Welcome's button becomes a `View` with `overflow: 'hidden'` holding an absolutely filled `Svg` and then the text.

**Colours.** The house rule is tokens from `src/theme`; the Divider's hex literals predate it. Either map them to tokens in this PR — then it is a visual change and needs the device look at 320 dp × fontScale 1, en + hi — or keep this PR a pixel-for-pixel swap and open the token move as its own change. Not both at once. **Risk.** Visual only. **Verify.** `yarn test`; the drawer (upright and on its side), the Login welcome screen and any divider, on both platforms; then `yarn remove react-native-linear-gradient` and `pod install`.

### 4.3 The compat layer: six packages to zero (or four)

Six native packages ship no `codegenConfig` and run through the interop layer — in 0.84 "the Interop Layer code required for compatibility remains in place" ([RN 0.84 blog](https://reactnative.dev/blog/2026/02/11/react-native-0.84)):

| Package | Move | First red | Verify |
| --- | --- | --- | --- |
| `@react-native-firebase/{app,analytics,crashlytics,perf}` 24.0.0 (2026-04-01) | all four to 26.4.0 (2026-09-05) in one PR — two majors | a case in `firebaseModules.config.test.js`, which already pins "the four to one version": all four on `26.4.0` | `bundle exec pod install`; Settings' test buttons (`crashlytics().crash()` at `Settings/index.js:172`, `recordError` at 189); analytics and perf reach the console; the hand mocks at `jest.setup.js:3-47` follow any API change |
| `react-native-device-info` 15.0.2 | replaced by `NativeAppInfo` in [[01-phase-1-foundations]]; `yarn remove` once §3.2 has deleted its three dead importers | a dependency-pin row. Its mock (`jest.setup.js:55-57`) goes in the same commit — a `jest.mock` of an uninstalled module "takes every suite down at setup" | both platforms build; Phase 1 §5.9 |
| `react-native-linear-gradient` 2.8.3 | §4.2 | a dependency-pin row | §4.2 |

Two things are **not verified**: whether RNFB 26.x ships a `codegenConfig` (the RN Directory reports the repo's current state as Turbo; check with `grep -c codegenConfig node_modules/@react-native-firebase/app/package.json` after the upgrade), so the interop count ends at zero or four; and what the two majors break — the research did not summarise the changelogs, so read them before starting. The Podfile's RNFB lines (`$RNFirebaseAsStaticFramework`, the `static_library` hook, the modular-headers pods; `Podfile:20-43`) stay.

## 5. Repair

### 5.1 Declare `prop-types`

**Evidence.** Thirteen live files import `prop-types` (fourteen with the dead `components/Alert/CustomAlert.js`) ✅ — e.g. `components/Calender/Calendar.js`, `components/Input/BaseInput.js` — and `package.json` does not declare it. 15.8.1 is installed only because a lint plugin, `eslint-plugin-react` 7.37.5, depends on it ✅. Runtime code resting on a lint plugin's dependency. **Do.** `yarn add prop-types@^15.8.1` (the lockfile already resolves that range, `yarn.lock:7283`). **Red.** `expect(dependencies['prop-types']).toBeDefined()`. **Risk.** None. **Verify.** `yarn test`, `yarn lint`, both release bundles (§3.1).

### 5.2 The location purpose strings — keep the keys, tell the truth

**Evidence.** `Info.plist:49-54` ✅ sets `NSLocationAlwaysAndWhenInUseUsageDescription`, `NSLocationAlwaysUsageDescription` and `NSLocationWhenInUseUsageDescription` to "$(PRODUCT_NAME) needs Location access for good user experience!" — and the app target's `PRODUCT_NAME` is `dzzlo_oms_app` (pbxproj ✅), so the string would even show the project name. Nothing in `src` asks for location.

**Why they must stay.** `react-native-onesignal` pins `OneSignalXCFramework` 5.5.0, which resolves to `OneSignalComplete` and with it `OneSignalLocation` (`Podfile.lock:192-205` ✅). That binary references `requestAlwaysAuthorization` and `requestWhenInUseAuthorization`, and OneSignal's issue trackers record App Store Connect's ITMS-90683 "missing purpose string" for apps that never use location. The strings went in on 2021-03-15 for exactly that reason.

**Why they must change.** Guideline 5.1.1(ii): "Ensure your purpose strings clearly and completely describe your use of the data." "Good user experience" describes nothing. The release checklist's proposed replacement (item 6, "capture delivery checkpoints and verify on-site visits") would describe a feature the app does not have — a review risk of its own. Wording that is true today, for all three keys:

```
Dzzlo OMS does not use your location. The notification service built into the app contains optional location code, which the app never turns on.
```

It is never shown — nothing requests location — so it needs no Hindi copy until a real location feature arrives with its own strings in en + hi ([[07-phase-7-maps-and-location]]). Whether App Review accepts a "we don't use it" string is **not verified**; nor is excluding OneSignal's location component (the RN SDK's podspec depends on the whole framework), nor whether ITMS-90683 would fire with the strings gone while `OneSignalLocation` stays linked. Keep all three keys, including the old `NSLocationAlwaysUsageDescription`.

**Red** (boolean — `Info.plist` also holds the OAuth client id):

```js
const LOCATION_KEYS = ['NSLocationAlwaysAndWhenInUseUsageDescription', 'NSLocationAlwaysUsageDescription',
  'NSLocationWhenInUseUsageDescription'];
it('keeps the three location keys, worded truthfully, while OneSignalLocation is linked', () => {
  const plist = read('ios/dzzlo_oms_app/Info.plist');
  expect(read('ios/Podfile.lock').includes('OneSignalXCFramework/OneSignalLocation')).toBe(true);
  expect(LOCATION_KEYS.map(key => plist.includes(`<key>${key}</key>`))).toEqual([true, true, true]);
  expect(plist.includes('good user experience')).toBe(false);
});
```

**Verify.** An archive upload shows no ITMS-90683 warning. Sources: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), [react-native-onesignal#1298](https://github.com/OneSignal/react-native-onesignal/issues/1298).

### 5.3 `<queries>` so "update app" works on Android 11+

**Evidence.** `AndroidManifest.xml` ✅ has no `<queries>` (the merged manifest has only react-native-webview's payment queries). Three "update app" paths check `https://play.google.com/…` with `Linking.canOpenURL` and then open `market://…`: the OneSignal in-app-message button (`helpers/OneSignal/index.js:66-68`), the error screen (`components/Error/index.js:86-87`) and `components/Error/ErrorMessage.js:36-37`. RN's docs say the promise rejects without intent queries on Android 11+; RN 0.84.1's `IntentModule.kt` in fact resolves `false` when nothing visible resolves the intent ✅. So the first two silently do nothing, while `ErrorMessage.js` ignores the answer and opens `market://` anyway. The audit calls it "probably broken": no test and no device run has proved it either way.

**Do.** Inside `<manifest>`, in the shape react-native-webview's own manifest uses:

```xml
<queries>
  <intent>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https" />
  </intent>
</queries>
```

**Red.** A manifest pin (no secrets there): `expect(read('android/app/src/main/AndroidManifest.xml')).toMatch(/<queries>[\s\S]*android\.intent\.action\.VIEW[\s\S]*android:scheme="https"/)`. **Risk.** None. **Verify — on a device, before and after:** on the Android 11+ emulator, open the error screen's update link — before, nothing; after, the Play Store. Android only; the iOS paths are untouched. Source: [RN Linking docs](https://reactnative.dev/docs/linking).

### 5.4 The iOS archive ships `APP_ENV=testing`

**Evidence.** ✅ The "Bundle React Native code and images" phase at `project.pbxproj:291` runs `export APP_ENV=testing`, at HEAD and in the working tree. `README.md` (around line 238) says the opposite: "The repo ships with `export APP_ENV=production` … Production archives need no edit." An archive cut today bundles `.env.testing` — the staging API — and the README tells whoever cuts it not to check. **Do.** Agree with the release owner which value HEAD holds between releases (the README says `production`), set it, and keep the README's `sed` switch for TestFlight test builds. **Red.** `expect(read('ios/dzzlo_oms_app.xcodeproj/project.pbxproj').includes('export APP_ENV=production')).toBe(true)` — a committed `testing` then fails CI instead of reaching the store. **Risk.** The worst release mistake available here. **Verify.** On the next TestFlight build, tap the Login screen's version text: outside production its "App Info" alert adds a `PROJ_ENV | API_URL` line (`Login.js`, `BetaUserComponent`), so a production archive shows none. A later step is to move env selection into a per-configuration build setting and pin that.

### 5.5 R8 off, four ABIs, no AAB

**Evidence.** `def enableProguardInReleaseBuilds = false` (`app/build.gradle:64` ✅) feeds `minifyEnabled`; `proguard-rules.pro` is empty; `reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64` (`gradle.properties:28` ✅). The release APK built on 2026-09-29 was 106,793,519 bytes — 23 `.so` files × 4 ABIs, every one 16 KB-aligned. `build-release-apk.sh` builds only APKs (`assembleRelease` → Firebase App Distribution); the README documents `./gradlew bundleRelease`. Release-checklist items 4 and 5 are open.

**Do — two PRs.** (1) **R8:** flip the flag; add keep rules only where a build or a device run proves one missing — reflection-heavy SDKs (OneSignal, Firebase) are the named risk; run the full device regression, including Phase 1 §5.9 for `NativeAppInfo`; confirm Crashlytics still shows readable Kotlin/Java stacks through the Settings test crash (mapping upload is not covered by the research). (2) **Size:** ship Play an AAB — the audit's point is that AAB delivery or `abiFilters` drops x86/x86_64 from phone installs — and decide separately what App Distribution testers get. **Red.** `expect(/enableProguardInReleaseBuilds = true/.test(read('android/app/build.gradle'))).toBe(true)`. **Verify.** Build both, record the sizes (measure it), and re-check 16 KB alignment with `zipalign -c -P 16 -v 4 app-release.apk` ([Android: Support 16 KB page sizes](https://developer.android.com/guide/practices/page-sizes)).

### 5.6 Upload-key passwords tracked in git

**Evidence.** `android/gradle.properties` is tracked and holds the values of `MYAPP_UPLOAD_STORE_PASSWORD` and `MYAPP_UPLOAD_KEY_PASSWORD` (lines 48-49) ✅. The values are not reproduced here — never print them, in a test, a log or a PR. The upload keystore itself is untracked (`.gitignore`: `*.keystore`, `!debug.keystore`); `app/build.gradle:99-106` reads the four `MYAPP_UPLOAD_*` names as Gradle project properties.

**Do.** (1) Move the four `MYAPP_UPLOAD_*` lines to `~/.gradle/gradle.properties` on the release machine, or to CI secrets — Gradle reads project properties from there, so `build.gradle` does not change. (2) Delete them from the tracked file. (3) **Rotate**: deleting lines from HEAD leaves them in history, so treat the old passwords as known and change both (`keytool -storepasswd`, `keytool -keypasswd`). Whether the upload key itself must be replaced through Play Console depends on whether the keystore was ever exposed; the audit checked only that it is untracked now. **Red** (boolean — a failing `toMatch` here would print the passwords into CI logs):

```js
it('keeps no signing passwords in the tracked gradle.properties', () =>
  expect(/MYAPP_UPLOAD_(STORE|KEY)_PASSWORD\s*=/.test(read('android/gradle.properties'))).toBe(false));
```

**Risk.** A release machine without the moved properties skips signing silently — `build.gradle` signs only `if (project.hasProperty('MYAPP_UPLOAD_STORE_FILE'))`. **Verify.** `build-release-apk.sh` still produces a signed APK.

### 5.7 The extension says 1.0; the app says 1.79

**Evidence.** ✅ `OneSignalNotificationServiceExtension` builds as `MARKETING_VERSION = 1.0`, `CURRENT_PROJECT_VERSION = 1`; the app is 1.79 with build 2 in the working tree (1 at HEAD). App Store Connect usually warns when an extension's short version differs from its parent's _(likely — not verified)_. **Do.** Give the extension the app's two values and bump them together from now on. **Red.**

```js
it('builds the app and its extension with one version and one build number', () => {
  const pbx = read('ios/dzzlo_oms_app.xcodeproj/project.pbxproj');
  const values = key => new Set([...pbx.matchAll(new RegExp(`${key} = ([^;]+);`, 'g'))].map(m => m[1]));
  expect([values('MARKETING_VERSION').size, values('CURRENT_PROJECT_VERSION').size]).toEqual([1, 1]);
});
```

**Risk.** None — and the pin keeps the next extension ([[06-phase-6-widgets-shortcuts-and-intents]]) in step too. **Verify.** The next archive uploads without a version-mismatch warning.

### 5.8 The unused Google OAuth URL scheme

**Evidence.** ✅ `Info.plist:25-35` registers one URL scheme, a reversed Google OAuth client id (value withheld). Only Google Sign-In uses such a scheme, and no file in `src` imports it. The app has no scheme of its own and no associated domains — links arrive properly in [[08-phase-8-instant-experiences-and-links]]. **Do.** Check the Firebase console that no sign-in provider needs it (the audit's caution), then delete the `CFBundleURLTypes` block. **Red** (boolean): `expect(read('ios/dzzlo_oms_app/Info.plist').includes('com.googleusercontent.apps.')).toBe(false)`. **Risk.** Something unseen relying on it — hence the console check first, and a sign-in on a device after.

## 6. Before and after

| Package | Before (2026-09-30) | After Phase 2 | § |
| --- | --- | --- | --- |
| `@react-navigation/stack` | 7.8.9, imported by nothing | removed | 3.1 |
| `react-native-html-to-pdf` | 1.3.0, never called | removed — the real PDF module is Phase 3's | 3.3 |
| `moment` | 2.30.1, 7 live files | removed — `src/helpers/LocalDate` | 4.1 |
| `react-native-linear-gradient` | 2.8.3, interop layer | removed — `react-native-svg` 15.15.4 | 4.2 |
| `react-native-device-info` | 15.0.2, interop layer | removed — `NativeAppInfo` | 4.3 |
| `@react-native-firebase/{app,analytics,crashlytics,perf}` | 24.0.0, interop layer | 26.4.0 (codegen status unverified) | 4.3 |
| `prop-types` | 15.8.1, undeclared | declared `^15.8.1` | 5.1 |
| `react-native-code-push`, `rn-fetch-blob` | phantom imports in dead files | gone with the files | 3.2 |
| `react-native-image-picker`, `react-native-permissions` | phantom imports, virtual Jest mocks | gone — or kept, on the user's word | 3.2 |

| Measure | Before | After |
| --- | --- | --- |
| Runtime dependencies in `package.json` | 32 | 28 (five out, one in) |
| Native packages, plus `react-native` | 18 | 15 |
| Packages on the interop layer | 6 | 4, or 0 if RNFB 26.4.0 ships a `codegenConfig` |
| Unreachable `src` files | 75 of 674 | 0 beyond the `KEEP` list |
| Release APK | 106.8 MB universal, R8 off | measure it |
| Jest suites | 172 ✅ (174 once Phase 1 lands) | about 181 _(est.)_ — seven new: `dependencies.config`, `unreachable.config`, `release.config`, `LocalDate` and its zone test, the `Divider` and `Welcome` render tests; none deleted, since no test imports a dead file. Measure it, and the runtime against the 2-minute budget. |

## 7. Exercises

**7.1 — Walk the graph yourself.** Run `node scripts/unreachable.js`, sort the output into §3.2's four groups, and take group (c) to the user. _Output: the grouped list, and the user's verdict on `ImagePicker`._

**7.2 — Prove the `canOpenURL` bug before fixing it.** On the Android 11+ emulator, tap the error screen's update link with today's build (nothing happens), add the `<queries>` block, rebuild, tap again (the Play Store opens). _Output: a before/after device observation in the PR._

**7.3 — Freeze moment's answers.** In a scratch script, print moment's result for ten inputs — month ends, 29 February, 1 January, a 31st plus one month — and paste them into the `LocalDate` tests. Red (no helpers), then green. _Output: the test run._

**7.4 — Break the pin on purpose.** After §5.4 is green, set `APP_ENV=testing` in the pbxproj on a scratch branch and run `yarn test`. Confirm the failure message shows `true`/`false` and nothing from the file. Revert. _Output: the red run._

**7.5 — Weigh the release.** Build the release APK with R8 off and on, and an AAB; record the three sizes and the `zipalign -c -P 16` result. _Output: a size table in the PR._

**7.6 — Count the suite.** `yarn test` before the first item and after the last; record suites, tests and wall time. _Output: two lines in the PR description._

## Lab Notes

2026-09-30, on the dev Mac; nothing was installed, built or committed in `dzzlo_oms_app`.

- **Every pin is red today.** Each red test's predicate in §3–§5 was evaluated as a boolean against HEAD `e29f0e5d` plus the working tree: all red, each for the reason given (the version sets in §5.7 come out as `[2, 2]`).
- **The walk.** §3.2's script, run from a scratch folder against HEAD `e29f0e5d`, printed "75 of 674 src files unreachable from index.js" in 0.35 s — the same 75 files the 2026-09-29 audit counted. Walking from every test file instead left the same 75 unreached.
- **`prop-types`.** In `node_modules`, only `eslint-plugin-react` 7.37.5 lists it as a dependency; `hoist-non-react-statics` 3.3.2 lists it as a devDependency, which does not install it.
- **`canOpenURL`.** RN 0.84.1's `IntentModule.kt` resolves `intent.resolveActivity(packageManager) != null` and rejects only when an exception is thrown.
- **Purpose-string text.** The app target's `PRODUCT_NAME` is `dzzlo_oms_app`, which is what `$(PRODUCT_NAME)` expands to in today's location strings.
- **moment's answers.** `moment(new Date('2026-03-31T10:00')).subtract(1, 'months').endOf('month')` gave `2026-02-28T23:59:59.999` and 31 January plus one month gave 28 February, in all four zones tried — local wall-clock inputs make these zone-proof; absolute instants are not.
