# Phase 7 — Tests & rollout

**Continuous** across Phases 2–6; also the release gate.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). Not started: 0 of 15 release-gate items. §1's starting position and §2.1's test-app warning are out of date (both repos now have full harnesses, corrected in place), the kill switch in §6.3 relied on Remote Config, which app 1.79 removed (`ad40ed71`), and the versions in §6.2 moved to 1.79 (Android 105 / iOS 4). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## 1. Starting position, per repo

| Repo | Test reality |
| --- | --- |
| `dzzlo_oms_api` | **Healthy.** ~~36 files, 211 `describe`, 663 `it` under `test/api_v3/`.~~ **2026-10-01:** 56 test files under `test/api_v3/` and 29 under `test/api_v4/`; last recorded `yarn test:full` 1,664 passed / 47 skipped / 1 todo (CI run 36788793446 on PR #46, 2026-09-30). MongoMemoryServer harness, seed factories, two established styles. |
| `dzzlo_oms_app` | ~~🔴 **`__tests__/App.test.tsx` is the only test in the repo** (13 lines). No `src/__tests__/`, no `__mocks__/`. `@testing-library/react-native` **is not installed**.~~ **2026-10-01:** 173 test files, 173 suites / 3,819 tests green on CI at `ea7e7222`; `@testing-library/react-native` ^13 and `msw` ^2 installed (`package.json:76,83`); Tier 3 harness `renderScreen` (`src/test/testUtils.js:277`). |
| `dip-web` | 🔴 **No test runner at all** — `package.json:20` is `"test": "echo 'No test runner configured — see Phase 5'"`. `@testing-library/*` sits in devDependencies as a CRA leftover, unused. |

**Do not let this feature be the thing that finally needs a client test harness *and* pays for it under deadline.** Decide up front (§4) how much harness to buy.

**Note (2026-10-01):** rows corrected in place — the advice above is moot for the app, whose harness now exists, and stands for dip-web (not re-assessed); see T14-N5 in the overview.

---

## 2. API tests — the well-trodden path

### 2.1 The harness

`jest.config.js` sets `testEnvironment: "node"`, `testTimeout: 30000`, and `testPathIgnorePatterns: ["api_v1_test","api_v1","api_v2","202405_v2"]` — ~~**only `test/api_v3/` runs**~~ `test/api_v3/` and `test/api_v4/` both run (2026-10-01; the ignore list is unchanged). Commands: `yarn test`, `yarn seed`, `yarn uproot`, `yarn test:full`.

`test/database.js`: `:44-58 connect()` (MongoMemoryServer + mongoose), `:63-72 close()`, `:77-84 clear()`, `:91 dheader = { "x-api-key": process.env["X_API_KEY_3"] }`.

`test/api_v3/helper/beforeAll/index.js:20-31` auto-discovers the newest `seed/data/v3_*` directory by lexicographic sort and throws clearly if absent. `beforeAllHelper({...})` takes 15 opt-in flags; `so_msts_data` is at `:104-108`.

~~⚠️ **The test app is a reduced copy** (`test/dzzlo_oms_test.js`): `express.json()` with **no limit** (`:38`), **no `api_key_v1`**, and **no `logging()` — so `req.loggedInUser` is undefined in tests**. If your authorization code reads `req.loggedInUser` rather than parsing the token directly, it will behave differently under test than in production.~~ **2026-10-01:** the test app now mirrors production — 1 MB JSON limit, the key check, `logging()`, the version gate and the v4 hub (`test/dzzlo_oms_test.js:43,54,59,62,106`) — so `req.loggedInUser` is set in tests as in production; on v4 the tenant comes from `tenantOf(req)`. Use `getUserFromToken(req.headers)` (as `veh_trns.js:39-47` does) and pass a real JWT in the test.

### 2.2 Two established styles — prefer style (b) for new work

**(a) HTTP integration** — `test/api_v3/collections/so_msts/index.test.js` (630 lines). `beforeAll` connects → seeds → fires the request into a closure var; each `it` asserts one facet. **`beforeAll`/`afterAll` only, never `beforeEach`** (per `docs/strategy/tdd_strategy.md:223`).

**(b) Direct service unit tests** — `dieselQtyLimit.test.js` (258 lines) and `editSalesOrder_backdate_reprice.test.js` (687 lines). These use `beforeEach(db.clear)`, mock the notification module, seed inline, and assert on `ErrorResponse` instance + `statusCode` + message. `editSalesOrder_backdate_reprice.test.js:1-50` is exemplary — a header block documenting exact lines under test, locked business rules, and a numbered `FLAG F1..F5` list of characterised-but-unfixed footguns. It pins `TZ=UTC`.

Useful idioms to copy:
```js
jest.mock("../../../../api_v3/controllers/App/notification",
          () => ({ sendNotifyToExternalIDs: jest.fn() }));
const TEST_META = { version: "1.510" };   // bypasses every version shim
```
(`"1.510"` is the escape hatch honoured by `check_user_version()` at `helpers/middlewares.js:112-141`.)

### 2.3 ⚠️ A trap in the existing prop-checker

`test/api_v3/helper/collections/so_msts/index.js:1-92 so_props(ele)` is declared `async` but **never awaited** by its callers (`index.test.js:302, 400, 586`). Failures inside it produce unhandled rejections rather than test failures. **Extend it for `du_slips` if you like — guarded by `if (!!ele.du_slips)` so existing suites stay green — but do not rely on it alone to pin a new invariant.** Write real assertions.

### 2.4 The suite to write

**Status (2026-10-01):** ⬜ to do — no slip tests. If the endpoints go to v4 (T14-N1), the suite belongs in `test/api_v4/commands/`, with identities resolved by email (`test/api_v4/harness/fixtures/identities.js`).

`test/api_v3/collections/so_msts/duSlips.test.js`, style (b), with the storage adapter mocked:

| Group | Cases |
| --- | --- |
| **Presign** | happy path returns url+fields; caps at 6 slips; rejects `bytes` > 1 MB; rejects when SO is invoiced; rejects unknown SO (404) |
| 🔴 **Authorization** | **cross-dealer presign is rejected** — token for dealer A, SO belonging to dealer B; body-supplied `dealer_id` is ignored; missing/invalid token → 401 |
| **Commit** | client claim sets `claimed`, not `committed`; S3-event handler sets `committed` and overwrites `bytes`/`sha256` from the event; **handler is idempotent** — same event twice yields one row |
| **List** | returns only non-deleted, committed slips; signed URLs are generated, not stored |
| **Delete** | soft-deletes (object survives); rejects post-invoice; rejects non-`DPrimary`/`DAdmin` |
| 🔴 **Leak** | `GET` invoice detail **does not** contain `du_slips` (pins the `invs.js:659-665` fix — Phase 2 §6) |
| **Sweeper** | `pending` >24 h deleted; `claimed` >15 min → `failed` |
| **Rate limit** | presign endpoint is limited |

Also register a smoke check in `test/api_v3/getAll/active.test.js` (the `so_msts` block is at `:171-176`) if you add a plain `GET`.

`test/api_v3/temp/seed/v3/factories/createSOs.js:22-32` already accepts an `options` object spread last, so tests can inject `du_slips` without touching the factory.

Known gap for context: `docs/strategy/test_gap_analysis.md:31, 48-51` notes most suites are happy-path only and *"edge cases, error paths, and permission checks are largely missing."* This suite should not follow that pattern.

---

## 3. Lambda tests

**Status (2026-10-01):** ⬜ to do — no worker exists.

The post-upload worker is where correctness is cheapest to verify and most expensive to get wrong:

- Magic-byte check: real JPEG passes; JPEG header + SVG body is **quarantined**
- Three variants produced at the right dimensions and formats; **`orig` is JPEG** (Phase 1 §4.2)
- Idempotent on repeated delivery of the same event
- `limitInputPixels` guard fires on a decompression bomb
- Mongo upsert writes authoritative `bytes`/`etag` from the event, not from the client

---

## 4. Client tests — decide the harness budget first

### 4.1 App

**Status (2026-10-01):** ❌ the (A)/(B) choice below is superseded — (B)'s harness exists: RNTL ^13 and MSW ^2 (`package.json:76,83`), the Tier 3 `renderScreen` (`src/test/testUtils.js:277`) and native mocks in `jest.setup.js`; write the attach flow's tests at the tiers `AI.md` sets (T14-N5).

~~Currently mocked in `jest.setup.js`: **only Firebase** (app, analytics, crashlytics, perf, remote-config), all in the `{__esModule: true, default: fn}` shape.~~ **2026-10-01:** `jest.setup.js` mocks Firebase (app, analytics, crashlytics, perf — the remote-config mock left with the package), AsyncStorage, `react-native-device-info`, NetInfo, `useWindowDimensions`, the keyboard inset, the device locale, `react-native-safe-area-context`, `@gorhom/bottom-sheet` and OneSignal.

~~Nothing is mocked for: `react-native-device-info` (⚠️ **called at module load** in `createApi.js:9-19`, so importing anything that pulls `createApi` will hit it), AsyncStorage (ships `jest/async-storage-mock`), NetInfo (ships `jest/netinfo-mock.js`), `@gorhom/bottom-sheet`, reanimated/worklets, webview, OneSignal, `@react-navigation/*`, `react-native-html-to-pdf`, plus whatever camera/picker library you add.~~ **2026-10-01:** reanimated runs through the worklets jest resolver (`jest.config.js`); `react-native-image-picker` and `react-native-permissions` already have virtual stubs (`jest.setup.js:245-257`); any other camera or picker library added here needs its own mock.

**Two options:**

**(A) Minimum — pure-logic tests only, zero new dependencies.** Test the functions that need no native mocking:
- the upload queue reducer (enqueue / dequeue / backoff / persistence round-trip)
- the quality gate scoring (blur + glare thresholds), given a synthetic pixel array
- the RTK Query `query()` builders — `builder.mutation({query})` returns a plain object, testable with zero mocking
- existing seams worth covering while you're there: `buildProduct` (duplicated at `NewSalesOrder/index.js:64-77` and `EditSalesOrder/index.js:56-69`, with slightly different `emptyProd` shapes at `:54` vs `:56`), `getFilteredProdMsts`, `errorRTK`

**(B) Fuller — add `@testing-library/react-native` plus native mocks** to test the bottom sheet, the staged-upload flow, and the invoiced-gate behaviour.

**Recommendation: (A) for this feature, (B) as its own task.** The queue and the quality gate are where the real bugs live, and both are pure functions. Building a component-test harness under feature deadline is how harnesses end up bad.

`APP_ENV` must be set for `@env` resolution — that's why the scripts prefix it (`yarn test` → `test:test` → `.env.testing`).

### 4.2 dip-web

**Note (2026-10-01):** not re-assessed — dip-web is outside this review.

No runner exists. If the web half of Phase 4 is non-trivial, add **vitest** (Vite-native, minimal config) and test the endpoint builders and the signed-URL handling. If the web half is just a read-only viewer, note the gap and move on — **but write down that you chose to.**

---

## 5. Manual test matrix

The parts no unit test will catch:

| Axis | Cases |
| --- | --- |
| **Android OS** | 9, 11, 13, 14, 16 — **confirm the Photo Picker backport actually appears on 9/10** |
| **Android OEM** | Samsung, Xiaomi, Realme/Oppo, Vivo — these kill background work and have divergent camera intents |
| **iOS** | 15.1 (deployment target), latest — PHPicker multi-select, camera prompt copy |
| **Network** | full 4G · throttled 2G/EDGE · airplane mode mid-upload · **captive-portal Wi-Fi** (reports connected, no data path — the single biggest real-world failure source) |
| **Lifecycle** | background mid-upload · force-kill mid-upload · app update with a queue pending |
| **Slip condition** | fresh thermal · faded · dot-matrix · crumpled · direct sun · night forecourt lighting · under canopy glare |
| **Flow** | attach during create (staged) · attach on edit (direct) · attach then invoice · attempt attach after invoice · delete before invoice · attempt delete after invoice |
| **Role** | `DPrimary` · `DAdmin` · other dealer scopes · a customer account |
| 🔴 **Tenant** | dealer A cannot see or touch dealer B's slips — check via the API directly, not just the UI |

---

## 6. Rollout

### 6.1 Order

**Note (2026-10-01):** v1.79 shipped on 2026-10-01 without slips — steps 4–5 now mean the first release that carries them (1.80 at the earliest).

```
1. models/so_msts.js + du_slips           additive; deploy alone, verify nothing shifts
2. S3 + KMS + CloudFront + Lambda         infra only, no traffic
3. api_v3 endpoints (+ the invs.js fix)   with tests green; still no client
4. App v1.79 — internal track             a handful of real dealers, real forecourts
5. App v1.79 — staged Play rollout        5% → 20% → 50% → 100%
6. dip-web viewer                         independent of the app release
7. (separate release) OCR + re-consent    Phase 6; Apple 5.1.2(ii)
```

Steps 1–3 are **additive and reversible** — nothing reads `du_slips` until step 4. That's the safe part of the rollout, and it's most of it.

### 6.2 Versions to bump

~~Current: Android `versionName 1.78` / `versionCode 103` (`android/app/build.gradle:89-90`); iOS `MARKETING_VERSION 1.78` / `CURRENT_PROJECT_VERSION 9`. The repo directory is `v1_79` and HEAD is *"Merge PR #46: release/v1.78 (Android 103 / iOS 9)"*.~~ **2026-10-01:** Android `1.79` / `105` (`android/app/build.gradle:89-90`); iOS `1.79` / build `4` (`project.pbxproj:447,458`); app HEAD `ea7e7222`, *"Merge PR #49: release v1.79 — v4 foundations, Customers & Daily Summary v2 screens (Android 105 / iOS 4)"*.

⚠️ **`check_user_version()`** (`helpers/middlewares.js:112-141`, mounted `dzzlo_oms.js:75`) hard-blocks `Number(version) <= 1.68`. Old clients simply won't send slips — no shim needed. But if a v1.78 client ever receives an SO payload containing `du_slips`, confirm it ignores unknown fields gracefully (it should — RTK Query passes objects through).

### 6.3 Feature flag

**Status (2026-10-01):** ❌ superseded — Remote Config was removed in 1.79 (`ad40ed71`); use a house toggle (D10, `GET /api/v4/app/features`), whose key rule must first accept a non-screen key (T14-N3).

~~The app already has `@react-native-firebase/remote-config` wired (mocked in `jest.setup.js:51-62`).~~ **Gate the whole attach UI behind a ~~remote-config~~ house-toggle boolean.** That gives you a kill switch that doesn't require a store release — worth a great deal on a feature that mints cloud credentials from a phone.

### 6.4 Monitoring from day one

| Metric | Alert |
| --- | --- |
| CloudFront `BytesDownloaded` | 🔴 **800 GB/month** — the R2 switch trigger (Phase 2 §1.2) |
| Upload success rate, by OEM and by connection type | drop >5 pp week-over-week |
| Presign→commit conversion | sustained <90% means uploads are failing silently |
| Orphaned objects (sweeper output) | any sustained non-zero |
| Lambda errors / DLQ depth | any |
| S3 4xx (policy rejections) | spike = a client bug, likely content-type |
| p50/p95 upload duration | — |
| (Phase 6) human-override rate per field | step change = silent model regression |
| (Phase 6) silent-error rate | 🔴 release gate, ≪1% |

Crashlytics is already wired (`src/store/middleware/rtkQueryErrorLogger.js:65-71` records every rejection). Add breadcrumbs at capture / resize / presign / upload / commit so a field failure is diagnosable without a repro.

### 6.5 Rollback

- **App:** ~~remote-config flag off~~ house toggle off (§6.3, T14-N3). No store round trip.
- **API:** endpoints are additive; the only non-additive change is `.select("-du_slips")` at `invs.js:659-665`, which is safe to keep regardless.
- **Schema:** an additive optional array. Leaving it in place is harmless.
- **Storage:** objects persist. **Never delete on rollback** — GST retention (Phase 1 §4.3).

---

## 7. Release gate

**Status (2026-10-01):** ⬜ 0 of 15 — none done; the "Remote-config kill switch" item becomes a house-toggle check (T14-N3), and the last item waits until something ships.

- [ ] API suite green, including the cross-dealer authorization cases and the invoice-leak test
- [ ] Lambda tests green, including idempotency and the SVG-in-JPEG quarantine
- [ ] Client pure-logic tests green (queue, quality gate, query builders)
- [ ] Manual matrix §5 walked on at least: one Samsung, one Xiaomi/Realme, one iPhone
- [ ] Captive-portal Wi-Fi case explicitly tested
- [ ] **Merged** Android manifest verified — no `CAMERA`, no media permissions (Phase 5 §6)
- [ ] iOS Generate Privacy Report clean; the three stale `NSLocation*` keys resolved
- [ ] Play Data safety + deletion questions submitted; no Photo & Video declaration alert
- [ ] App Store privacy label + reviewer notes submitted
- [ ] Privacy policy updated per Phase 5 §4.5 and live at the URL in both consoles
- [ ] Remote-config kill switch verified to actually hide the UI
- [ ] CloudWatch alarms live, including the 800 GB egress alarm
- [ ] Share link: **explicit go/no-go recorded** (Phase 4 §4)
- [ ] `docs/AI_CONTEXT.md` and `docs/strategy/cross_version_edits_plan.md` updated
- [ ] This task folder's `00-overview.md` status line updated to reflect what actually shipped
