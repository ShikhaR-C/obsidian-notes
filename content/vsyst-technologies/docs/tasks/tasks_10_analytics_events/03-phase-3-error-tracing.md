# Phase 3 — Error Tracing

**Outcome:** every JS crash, render-boundary catch, API failure, and notable handled error reaches Crashlytics with full context (user, role, company, screen, breadcrumb trail) **and is localisable to an exact file/line/component fast**. Closes the two biggest gaps: **render crashes are currently dropped**, and **Hermes stack traces are unreadable without source maps**.

---

## 3.0 Strategy — locate any crash in three clicks

Goal: open a Crashlytics issue and immediately know **what** broke, **where** (file:line / component), **who** (role/company/user), and **how to reproduce** (the steps before it). Four levers, in priority order:

| Lever | What it buys | Where (this doc) |
| --- | --- | --- |
| **1. Source maps (Hermes)** | Minified bytecode frame → original `OrdersScreen.js:142`. Without this, JS stacks are useless. **Highest ROI.** | 3.7 |
| **2. Custom keys** | Filter/slice the issue list by `screen`, `role`, `company_id`, `last_endpoint`, `app_build`. Find "all crashes on NewInvoice for dealers". | 3.8 |
| **3. Breadcrumb log trail** | The exact screen/action sequence before the crash → reproduce it. | 3.2 |
| **4. Deterministic error names** | Identical failures group into ONE issue instead of scattering → triage by frequency. | 3.1, 3.3 |

Current state to build on (already configured — verify, don't redo):
- `firebase.json` → `crashlytics_is_error_generation_on_js_crash_enabled: true` + `crashlytics_javascript_exception_handler_chaining_enabled: true` → **RN Firebase already installs a global JS error handler** that turns unhandled JS errors into Crashlytics records and chains to the previous handler. (This changes 3.4 — see note there.)
- Android: `firebase-crashlytics-gradle:3.0.6` plugin applied. **Correction:** no `firebaseCrashlytics {}` block exists in the gradle files, so plugin defaults apply — Proguard/R8 mapping upload is default-on (relevant only if minification is enabled), but **NDK symbol upload is NOT on** (needs explicit `nativeSymbolUploadEnabled true`, see 3.7).
- iOS: Crashlytics run-script build phase present in `project.pbxproj` (verify it runs `upload-symbols`/`run` for dSYMs).
- **Hermes is enabled** (`android/gradle.properties: hermesEnabled=true`) → JS source maps are the missing piece (3.7).

---

## 3.1 Fix `ErrorBoundary` → Crashlytics (critical)

`src/components/Error/ErrorBoundary.js:127` — `componentDidCatch` only `console.log`s; the `logError` call is commented out. React render crashes never reach Crashlytics today.

```js
// ErrorBoundary.js
import { logError, logBreadcrumb } from '../../utils/firebase';
import { track } from '../../utils/analytics';
import { EVENTS } from '../../config/events';

componentDidCatch(error, errorInfo) {
  this.setState({ errorMessage: error });
  // Record a NON-fatal to Crashlytics with the React component stack as a
  // breadcrumb so the dashboard shows where in the tree it blew up.
  try {
    // Truncate the message: server/validation error messages can echo user
    // data (emails, phones, amounts) — cap it like the componentStack below.
    logBreadcrumb(`react_error_boundary: ${String(error?.message ?? error).slice(0, 200)}`);
    if (errorInfo?.componentStack) {
      logBreadcrumb(`componentStack: ${errorInfo.componentStack.slice(0, 800)}`);
    }
    // NAME the record so all render crashes group under one Crashlytics issue.
    // logError's optional 2nd arg (added in Phase 1) forwards to
    // crashlytics().recordError(err, jsErrorName), which controls grouping.
    logError(error, 'ReactRenderError');
    // name only — never the message (PII risk in analytics params)
    track(EVENTS.ERROR_BOUNDARY_TRIGGERED, { name: error?.name });
  } catch {
    /* never let logging crash the boundary */
  }
}
```

> Keep the existing `reportError` mutation in `FallbackUI` (server-side log) — these are complementary: Crashlytics for triage, the backend log for the in-app report. No behaviour change to the user-facing UI.

---

## 3.2 Breadcrumbs on navigation + key actions

A Crashlytics report is far more useful with a trail of "what the user did just before". Two cheap insertions:

**Navigation** — extend the existing screen-view handler in `src/components/Error/RestartContext.js` (it already centralises navigation state):

```js
import { logScreenView, logBreadcrumb, setScreenAttr } from '../../utils/firebase';

const handleStateChange = () => {
  const prev = routeNameRef.current;
  const current = navigationRef.getCurrentRoute()?.name ?? null;
  if (current && prev !== current) {
    logScreenView(current, current);
    logBreadcrumb(`nav: ${prev ?? '-'} -> ${current}`); // breadcrumb trail
    setScreenAttr(current);                              // crash report names the screen
  }
  routeNameRef.current = current;
};
```

**Risky actions** — drop a `logBreadcrumb('action: creating invoice')` immediately before big mutations (invoice/PDF/export). One line, no params.

---

## 3.3 Enrich the API-failure mirror

`src/store/middleware/rtkQueryErrorLogger.js:66` already records `RTKQ <endpoint> rejected: <status>`. Upgrade it from a bare message to a contextual non-fatal so failures are queryable by endpoint/status, and emit an analytics event for client-visible failures:

```js
// inside the isRejectedWithValue block, replacing the current recordError
try {
  crashlytics().setAttribute('last_failed_endpoint', String(endpoint ?? 'unknown'));
  crashlytics().log(`RTKQ ${endpoint ?? 'unknown'} -> ${status ?? 'no-status'}`);
  crashlytics().recordError(
    new Error(`RTKQ_${endpoint ?? 'unknown'}_${status ?? 'nostatus'}`),
  );
} catch { /* ignore */ }

// Surface server (5xx) and network errors as an analytics signal too — these
// are the ones that hurt UX. Skip 401/403 (handled as auth/company flow).
// EVENTS.API_ERROR is in the Phase-1 catalog (no orphan events) and track()
// keeps it behind the analytics_enabled kill-switch.
if (status === 'FETCH_ERROR' || status === 'TIMEOUT_ERROR' || Number(status) >= 500) {
  track(EVENTS.API_ERROR, { endpoint: endpoint ?? 'unknown', status: String(status) });
}
```

> Naming the `Error` deterministically (`RTKQ_<endpoint>_<status>`) makes Crashlytics **group** identical failures instead of scattering them — much better issue triage than a message with a variable suffix.

---

## 3.4 Global JS-error capture — already on; only add context (correction)

> **Correction to earlier draft.** `firebase.json` sets `crashlytics_is_error_generation_on_js_crash_enabled: true` **and** `crashlytics_javascript_exception_handler_chaining_enabled: true`. RN Firebase therefore **already installs a global `ErrorUtils` handler** that records unhandled JS errors to Crashlytics and chains to the previous handler. So a second manual `ErrorUtils.setGlobalHandler` is **not needed for capture** and risks double-recording — do **not** add one just to record.

What's still worth adding is **context immediately before the crash is recorded** — but since RNFB's handler runs last, the better hook is a lightweight **breadcrumb on every dispatched RTK action type** (cheap) and the per-action breadcrumbs from 3.2, not a competing global handler.

**Unhandled promise rejections** are the one genuine gap.

> **Correction (2026-07-02): the earlier draft's `promise/setimmediate/rejection-tracking` snippet captures NOTHING in this app.** The app runs **Hermes** (`android/gradle.properties:39`; iOS is RN 0.84 default-Hermes), and with Hermes RN uses the engine's **native** Promise — the `promise` npm polyfill is never installed (verified in `react-native/Libraries/Core/polyfillPromise.js`), and RN wires Hermes rejection tracking **only in `__DEV__`**. Enabling the polyfill's tracker would watch a Promise implementation the app doesn't use, silently capturing nothing in release. Use the Hermes API, with the polyfill path only as a non-Hermes fallback:

```js
// once, at startup
const onUnhandled = (id, error) => {
  try {
    crashlytics().log(`unhandled_rejection id=${id}`);
    logError(error, 'UnhandledRejection'); // named → groups (Phase-1 logError)
  } catch {
    /* never throw from the tracker */
  }
};

if (global?.HermesInternal?.enablePromiseRejectionTracker) {
  // Hermes — this app, release builds included (RN itself only enables this in __DEV__)
  global.HermesInternal.enablePromiseRejectionTracker({
    allRejections: true,
    onUnhandled,
    onHandled: () => {},
  });
} else {
  // JSC / promise-polyfill fallback only
  require('promise/setimmediate/rejection-tracking').enable({
    allRejections: true,
    onUnhandled,
    onHandled: () => {},
  });
}
```

---

## 3.7 Source maps & symbolication (Hermes) — the #1 localisation lever

**Problem:** Hermes is enabled, so a JS crash stack in Crashlytics looks like `Hermes bytecode @ 1:524288` — unusable. To turn that into `src/screens/Customer/NewOrder/index.js:142` you need the **Hermes source map for that exact build**, and a way to symbolicate.

There is no fully-automatic Crashlytics pipeline for RN-Hermes JS frames (unlike native), so do this:

**1. Archive the source map gradle already generates.**

> **Correction (2026-07-02):** do **NOT** run `npx react-native bundle` manually as the earlier draft said. `build-release-apk.sh` only runs `./gradlew clean && assembleRelease`; a separate bundle invocation produces a bundle/map pair that does **not** match the APK gradle packaged — symbolicating against the wrong map yields garbage. On RN 0.84 the gradle plugin **already emits the composed (bytecode→JS) Hermes map** on every release build: the default `hermesFlags` include `-output-source-map` and this app leaves `hermesFlags` at the default (`android/app/build.gradle:55` is commented out). Just archive gradle's output:

```sh
# Android — add to build-release-apk.sh AFTER ./gradlew assembleRelease
MAP=android/app/build/generated/sourcemaps/react/release/index.android.bundle.map
APP_BUILD=$(grep versionCode android/app/build.gradle | awk '{print $2}')
mkdir -p build-artifacts/sourcemaps
cp "$MAP" "build-artifacts/sourcemaps/index.android.bundle.$APP_BUILD.map"

# iOS: set SOURCEMAP_FILE in the Xcode "Bundle React Native code and images"
# phase (verified absent today — pbxproj:291, so iOS emits no JS map yet).
# ⚠️ While editing that phase: it currently hardcodes `export APP_ENV=testing`
# — fix it, or iOS prod builds keep shipping with proj_env=testing (see 4.1).
```

Store `build-artifacts/sourcemaps/*.map` per build number (CI artifact / bucket). The gradle-generated map above **is** the composed bytecode→JS map — no extra compose step needed.

**2. Tag each crash with the build so you know which map to use.** Set a custom key at startup (3.8) `app_build` = `deviceInfo.getBuildNumber()`. Then a Crashlytics issue tells you the build → pull that map.

**3. Symbolicate a stack** offline with the matching map:

```sh
npx metro-symbolicate build-artifacts/sourcemaps/index.android.bundle.<build>.map < raw-hermes-stack.txt
```

**4. Native side (partially wired — verify):**
- Android: **no `firebaseCrashlytics {}` block exists** in the gradle files (verified), so plugin defaults apply — mapping upload is default-on but only matters if R8/Proguard minification is enabled. **NDK symbols are NOT auto-uploaded**: add `firebaseCrashlytics { nativeSymbolUploadEnabled true }` to the release buildType if native-crash symbolication is wanted.
- iOS: the Crashlytics run-script phase **is** present (`"${PODS_ROOT}/FirebaseCrashlytics/run"`, pbxproj:349) — it handles dSYM upload. Confirm the Crashlytics console shows no "missing dSYM" warnings after a release build.

> Minimum viable version if a full pipeline is too much now: keep `app_build` + source-map artifacts so any single crash can be symbolicated on demand in minutes. That alone removes the "where did it crash" guesswork.

---

## 3.8 Custom-key taxonomy & grouping (slice the issue list)

Crashlytics custom keys are the second-highest lever: they make the issue list **filterable** ("all crashes on `NewInvoice` for `dealer` on build 142"). Standardise the keys set centrally so every crash carries them. Centralise in one `setCrashKeys()` helper, called from `setUserContext` + navigation:

| Key | Value source | Set where | Lets you filter by |
| --- | --- | --- | --- |
| `screen` | current route | `setScreenAttr` on nav (3.2) | crashing screen |
| `role` | `selectUserRole` | `setUserContext` | dealer vs customer |
| `company_id` | `selectCompanyId` | `setUserContext` | tenant |
| `app_version` / `app_build` | `deviceInfo` | `setUserContext` | regression window |
| `proj_env` | `PROJ_ENV` | `tagEnv` (exists) | drop test noise |
| `last_endpoint` | RTK action | error middleware (3.3) | API-triggered crashes |
| `last_action` | risky-op breadcrumb | before mutations (3.2) | flow at crash time |
| `js_engine` | `'hermes'` | once at startup | which symbolication path |

**Grouping rules (so one bug = one issue):**
- Always `recordError(error, '<StableName>')` — `ReactRenderError`, `UnhandledRejection`, `RTKQ_<endpoint>_<status>`. The 2nd arg controls the Crashlytics group; a stable name collapses duplicates.
- Never interpolate ids/dynamic strings into the error **name** (they shatter grouping) — put them in custom keys / breadcrumbs instead.
- Use Crashlytics **Velocity alerts** (console) on the named issues so a spike pages you; optionally enable **BigQuery export** for ad-hoc "crashes by screen/role" queries.

---

## 3.5 Network transitions as events

`src/components/Network/index.js` already holds the `NetInfo.addEventListener` subscription at line 19 (and `NoNetwork/Undraw.js` uses `useNetInfo`). Add the event inside that existing listener so we can correlate `api_error` spikes with connectivity — note a `prevConnectedRef` must be **added** (none exists today; the component only stores current state) so we fire only on an actual connected→disconnected (or reverse) **transition**, not every NetInfo tick. **While here, fix a pre-existing leak:** the listener's unsubscribe function is never captured — cleanup only flips a local `isMounted` flag; capture the return of `addEventListener` and call it in the effect cleanup.

```js
// src/components/Network/index.js — inside the existing NetInfo.addEventListener
const next = !!state.isConnected;
if (next !== prevConnectedRef.current) {
  prevConnectedRef.current = next;
  track(next ? EVENTS.NETWORK_RESTORED : EVENTS.NETWORK_LOST, {
    type: state.type, // wifi | cellular | none
  });
}
```

---

## 3.6 Crash-test buttons — already present & gated (no work)

`src/screens/Common/Settings/index.js` already ships two QA tools — **"Force Crash (Crashlytics Test)"** (`crashlytics().crash()`) and **"Record Non-Fatal Error"** (`crashlytics().recordError(...)`) — wrapped in `{IS_NON_PROD && (…)}` where `IS_NON_PROD = PROJ_ENV === 'development' || PROJ_ENV === 'testing'` (defined at the top of that file). So they're already hidden in production. **No change needed** — just use them in Phase 4 verification. (Earlier draft said "gate behind `__DEV__`"; that's already handled via `IS_NON_PROD`, which is the correct env-based gate here since debug builds can run the `testing` env.)

---

## Error-context summary (what a Crashlytics report will carry after Phase 3)

| Context | Set by |
| --- | --- |
| `user_id` | `setUser` / `setUserContext` (Phase 1–2) |
| `role`, `company_id`, `app_version`, `app_build` | `setUserContext` attributes (3.8) |
| `proj_env`, `js_engine` | `tagEnv` (existing) / startup |
| `screen` | `setScreenAttr` on navigation |
| `last_endpoint`, `last_action` | RTK error middleware / risky-op breadcrumb |
| breadcrumb trail (nav + actions) | `logBreadcrumb` / `crashlytics().log` |
| component stack (render crashes) | ErrorBoundary, named `ReactRenderError` |
| **readable JS stack (file:line)** | **source map for `app_build` + `metro-symbolicate` (3.7)** |

---

## Phase 3 checklist

- [ ] `ErrorBoundary.componentDidCatch` records to Crashlytics **named `ReactRenderError`** + fires `error_boundary_triggered`.
- [ ] Navigation breadcrumbs + `screen` attribute wired in `RestartContext`.
- [ ] RTK error middleware: custom keys (`last_endpoint`) + deterministic error name + `api_error` event for 5xx/network.
- [ ] **No** duplicate `ErrorUtils` handler added (RNFB already installs one); unhandled-rejection tracking added via `HermesInternal.enablePromiseRejectionTracker` (NOT the `promise` polyfill — this is a Hermes app).
- [ ] **Source maps (3.7):** `build-release-apk.sh` archives the **gradle-generated** composed map keyed by `app_build` (no manual re-bundle); iOS `SOURCEMAP_FILE` added and the hardcoded `APP_ENV=testing` in that build phase fixed; `metro-symbolicate` verified on a sample stack.
- [ ] **Custom keys (3.8):** `setCrashKeys()` sets screen/role/company/app_build/js_engine/last_endpoint on every crash.
- [ ] Native symbol upload verified (Android mapping upload is plugin-default — add `nativeSymbolUploadEnabled true` if NDK symbolication wanted; iOS dSYM run-script present at pbxproj:349).
- [ ] Network transition events (+ capture/call the NetInfo unsubscribe — fixes a pre-existing leak).
- [ ] Confirm existing `IS_NON_PROD` crash-test buttons work for verification (already gated — no change).
- [ ] Verified end-to-end: force a render crash → Crashlytics issue shows **readable file:line** (after symbolication), grouped under `ReactRenderError`, with role/company/screen/app_build keys.
