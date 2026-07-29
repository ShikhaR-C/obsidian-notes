# Phase 7 — Tests & rollout

**Continuous** across Phases 2–6; also the release gate.

---

## 1. Starting position, per repo

| Repo | Test reality |
| --- | --- |
| `dzzlo_oms_api` | **Healthy.** 36 files, 211 `describe`, 663 `it` under `test/api_v3/`. MongoMemoryServer harness, seed factories, two established styles. |
| `dzzlo_oms_app` | 🔴 **`__tests__/App.test.tsx` is the only test in the repo** (13 lines). No `src/__tests__/`, no `__mocks__/`. `@testing-library/react-native` **is not installed**. |
| `dip-web` | 🔴 **No test runner at all** — `package.json:20` is `"test": "echo 'No test runner configured — see Phase 5'"`. `@testing-library/*` sits in devDependencies as a CRA leftover, unused. |

**Do not let this feature be the thing that finally needs a client test harness *and* pays for it under deadline.** Decide up front (§4) how much harness to buy.

---

## 2. API tests — the well-trodden path

### 2.1 The harness

`jest.config.js` sets `testEnvironment: "node"`, `testTimeout: 30000`, and `testPathIgnorePatterns: ["api_v1_test","api_v1","api_v2","202405_v2"]` — **only `test/api_v3/` runs**. Commands: `yarn test`, `yarn seed`, `yarn uproot`, `yarn test:full`.

`test/database.js`: `:44-58 connect()` (MongoMemoryServer + mongoose), `:63-72 close()`, `:77-84 clear()`, `:91 dheader = { "x-api-key": process.env["X_API_KEY_3"] }`.

`test/api_v3/helper/beforeAll/index.js:20-31` auto-discovers the newest `seed/data/v3_*` directory by lexicographic sort and throws clearly if absent. `beforeAllHelper({...})` takes 15 opt-in flags; `so_msts_data` is at `:104-108`.

⚠️ **The test app is a reduced copy** (`test/dzzlo_oms_test.js`): `express.json()` with **no limit** (`:38`), **no `api_key_v1`**, and **no `logging()` — so `req.loggedInUser` is undefined in tests**. If your authorization code reads `req.loggedInUser` rather than parsing the token directly, it will behave differently under test than in production. Use `getUserFromToken(req.headers)` (as `veh_trns.js:39-47` does) and pass a real JWT in the test.

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

The post-upload worker is where correctness is cheapest to verify and most expensive to get wrong:

- Magic-byte check: real JPEG passes; JPEG header + SVG body is **quarantined**
- Three variants produced at the right dimensions and formats; **`orig` is JPEG** (Phase 1 §4.2)
- Idempotent on repeated delivery of the same event
- `limitInputPixels` guard fires on a decompression bomb
- Mongo upsert writes authoritative `bytes`/`etag` from the event, not from the client

---

## 4. Client tests — decide the harness budget first

### 4.1 App

Currently mocked in `jest.setup.js`: **only Firebase** (app, analytics, crashlytics, perf, remote-config), all in the `{__esModule: true, default: fn}` shape.

Nothing is mocked for: `react-native-device-info` (⚠️ **called at module load** in `createApi.js:9-19`, so importing anything that pulls `createApi` will hit it), AsyncStorage (ships `jest/async-storage-mock`), NetInfo (ships `jest/netinfo-mock.js`), `@gorhom/bottom-sheet`, reanimated/worklets, webview, OneSignal, `@react-navigation/*`, `react-native-html-to-pdf`, plus whatever camera/picker library you add.

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

Current: Android `versionName 1.78` / `versionCode 103` (`android/app/build.gradle:89-90`); iOS `MARKETING_VERSION 1.78` / `CURRENT_PROJECT_VERSION 9`. The repo directory is `v1_79` and HEAD is *"Merge PR #46: release/v1.78 (Android 103 / iOS 9)"*.

⚠️ **`check_user_version()`** (`helpers/middlewares.js:112-141`, mounted `dzzlo_oms.js:75`) hard-blocks `Number(version) <= 1.68`. Old clients simply won't send slips — no shim needed. But if a v1.78 client ever receives an SO payload containing `du_slips`, confirm it ignores unknown fields gracefully (it should — RTK Query passes objects through).

### 6.3 Feature flag

The app already has `@react-native-firebase/remote-config` wired (mocked in `jest.setup.js:51-62`). **Gate the whole attach UI behind a remote-config boolean.** That gives you a kill switch that doesn't require a store release — worth a great deal on a feature that mints cloud credentials from a phone.

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

- **App:** remote-config flag off (§6.3). No store round trip.
- **API:** endpoints are additive; the only non-additive change is `.select("-du_slips")` at `invs.js:659-665`, which is safe to keep regardless.
- **Schema:** an additive optional array. Leaving it in place is harmless.
- **Storage:** objects persist. **Never delete on rollback** — GST retention (Phase 1 §4.3).

---

## 7. Release gate

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
