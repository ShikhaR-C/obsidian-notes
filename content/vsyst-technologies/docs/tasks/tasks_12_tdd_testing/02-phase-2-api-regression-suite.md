# Phase 2 — API Regression Suite (the backbone)

**Outcome:** every P0/P1 flow in the regression contract is pinned by at least one `test/api_v3`-idiom test against seeded local data; seed factories cover the missing scenarios; the flow→test map below becomes the release-gate checklist.
**Effort:** 4–8 dev-days — splittable by flow; each row of §2.1 is independently landable.

> **TDD lens:** this phase is mostly *characterization* — writing tests that pin behavior we already believe is correct, so future changes that break it go red. New tests are written one flow at a time, red-first where a gap is a genuine unknown (write the assertion you *expect*, run it, and let reality correct you).

---

## 2.1 Flow → test map (the regression contract, executable form)

This table is the deliverable. It starts as below and ends with every row ✅. Copy the final version into `docs/testing.md` and reference it from the release checklist (Phase 6).

| Flow (overview #) | Existing tests | Gap work this phase |
| --- | --- | --- |
| Auth & session (#1) | `auth/login_otp`, `auth/redux_auth`, `auth/forgot_reset_pass`, `auth/verify_email_phone` | none (verify assertions still match current contract) |
| Role/scope/bearer (#2) | ❌ | **NEW** `auth/authorization/index.test.js` (§2.2.1) |
| Company status gates (#3) | `helper/check_user_company_status.test.js`, `features/multiple_companies/*` | **NEW** route-level gate cases in §2.2.2 |
| Orders lifecycle (#4) | `collections/order_msts/index.test.js` | audit delivery-OTP coverage (`otp_by`/`otp_to`, `getOTPToken`); add `collections/order_msts/delivery_otp.test.js` if thin |
| Sales orders (#5) | `so_msts/index`, `dieselQtyLimit`, `editSalesOrder_backdate_reprice` | none |
| Invoices (#6) | `collections/invs/index.test.js` | audit GST + TCS invoice types; extend if thin |
| Vouchers & payments (#7) | `voc_msts/index`, `voc_msts/advdep` | AdvDep **drawdown** cases when tasks_07 Phase 3 (v2) lands — conditional |
| Credit engine (#8) | 🟡 scattered | **NEW** `features/credit/index.test.js` (§2.2.3) |
| Accounts/ledger (#9) | `features/accounts/index.test.js`, `features/sadmin/index.test.js` | verify fin-year rollover + month recompute parity with old `202405_v2` sadmin coverage before deleting it |
| Products/rates (#10) | `prod_msts/index` (incl. rates + `a/prodRates`), `psocs/*`, `helper/getApplicableRate.test.js`, `features/prod_disc` | none |
| Vehicles/drivers (#11) | `vehs/*`, `dvr_msts/*` | none |
| Invites/users (#12) | `invites/index`, `users/index`, `helper/bustUserCache.test.js` | none |
| Version gate (#13) | ❌ | **NEW** `features/version_gate/index.test.js` (§2.2.4) |
| getAll matrix | `getAll/active.test.js` (skips `veh_msts` GET, `counters`, `logs`; `getAll/index.test.js` is `describe.skip`) | un-skip `veh_msts`; decide `counters`/`logs` rows; delete or revive the skipped `index.test.js` (recommend delete — `active` is the maintained one) |
| DIP (#14) | ❌ — blocked | see §2.6 |

## 2.2 New test specifications

All new tests follow the exact house idiom — shown once in §2.4; only the intent is specified per suite here.

### 2.2.1 `test/api_v3/auth/authorization/index.test.js` — bearer/roles/scopes

Requires Phase 1 §1.2 (test app mounts `logging()`). Matrix to cover:

- Login via OTP (existing helper pattern: create credentials → read `OTP_Value` from Mongo → `loginOTP`) → capture the returned JWT.
- `protect`: gated route (e.g. `POST /api/v3/order_msts`) → 401 with no/garbage/expired Bearer; 200-path with valid Bearer + `x-api-key`.
- `authorize(...roles)`: customer token on a dealer-only route → 403; superadmin on `sadmin` routes → 200; customer on `sadmin` → 403.
- `scope(...)`: seeded users with distinct scopes (see §2.3 seed additions) — e.g. `CView` hitting an order-writing route → 403; `CPrimary` → success; dealer scopes mirror-cased.
- `userCache` (v3 `api_v3/auth.js`): change a user's scope in Mongo, assert stale-cache behavior within TTL and correct behavior after `bustUserCache` — extends the existing `helper/bustUserCache.test.js` to the route level.

### 2.2.2 Company-status gate — route-level

Extend `features/multiple_companies/*` or add `features/company_status/index.test.js`:

- Set seeded company `status` inactive → any gated route returns 403 `error_code: COMPANY_INACTIVE`; removed-from-company user → `NOT_IN_COMPANY` / `COMPANY_REMOVED`.
- `x-co-id` header: valid 24-hex switch honored; malformed header rejected; superadmin bypass verified.

### 2.2.3 `test/api_v3/features/credit/index.test.js` — the credit engine

The highest-value new suite. Cases (exact status codes/messages to be confirmed against `api_v3/services/order_msts.js` + `invs.js` + `voc_msts.js` while writing — plan intentionally does not guess):

- **Capped**: relation with small `max_cr_lmt` → order that fits passes; order that exceeds is rejected; outstanding recomputed after an approved payment voucher unblocks the next order.
- **Blocked vs unlimited** *(amended 2026-07-09 — tasks_08 has landed, API `bf063d4`)*: pin the **landed** contract directly — `null`/unset = unlimited (check skipped), `0` = blocked (any `balSum > 0` rejected), `>0` = capped — on both order **create and update** paths (`api_v3/services/order_msts.js` ~786/~922). Also pin `createDC` defaults: versionless/new-client create → `0` (blocked), ≤1.77 client → `null` (`services/dealer_custs.js` ~1442), and the update-path normalization (`""`→null, `0`→version-dependent, rounding). The old `0<x<1` sentinel is retired — no red→green migration flip is pending. Cross-reference `tasks_08_maxcrlmt` Phase 4 for the truthiness-hazard site list.
- **`legacy_credit_presenter`**: request with `meta` header version ≤ 1.77 sees blocked `0` rewritten to a `(0,1)` sentinel on the wire; ≥ 1.78 / web / headerless sees raw values. *(Re-verified 2026-07-09: the presenter is mounted in **both** `api_v/api2.js` and `api_v/api3.js` by `bf063d4` and self-parses `req.headers.meta` — it is already reachable through the test app **without** Phase 1 §1.2; only bearer/role/scope and version-gate cases need §1.2.)*
- **AdvDep interplay**: approved AdvDep raises `dealer_custs.adv_dep` without touching invoice outstanding (pin the tasks_07 invariant); credit checks read the right balance.
- `cr_bill_lmt` / `max_cr_days` / `cr_bill_period` enforcement — one case each.

### 2.2.4 `test/api_v3/features/version_gate/index.test.js`

- Seed the `counters` doc `doc_name: "version_gate"` (needs the `counters` re-hydration branch from Phase 1 §1.3.4, or create it inline).
- App version below `minVersion` → hard 403; between min and latest → soft header (`x-app-update-available`); missing/garbage version header → documented fallback behavior (`versionGate.js` defaults).
- The 60s in-process cache: assert a threshold change takes effect after cache expiry/bust (use the documented cache-bust mechanism rather than sleeping, if available).

## 2.3 Seed additions (`test/api_v3/temp/seed/v3/factories/`)

Keep the architecture (JSON snapshots + factories) — ⏳ Q3. Additions:

1. **Credit variants** in `relateDC_Cash_reimb.js`: today every relation ends `max_cr_lmt: null` (unlimited) — since `1169ceb` the seed **explicitly forces `null`** in `seed/v3/index.js`, because versionless creates now default to `0` (blocked) under the landed tasks_08 contract and would fail every seeded order's credit check. Parameterize so the seed world includes one **capped** relation and one **blocked** relation, using the landed semantics. Factory idiom (options-object pattern already used by factories):

   ```js
   // test/api_v3/temp/seed/v3/factories/relateDC_Cash_reimb.js — sketch
   // after existing relation creation:
   await dealer_custs.findByIdAndUpdate(cappedRelId, { max_cr_lmt: 50000 });
   await dealer_custs.findByIdAndUpdate(blockedRelId, { max_cr_lmt: 0 }); // landed tasks_08 contract: 0 = blocked (amended 2026-07-09; old 0.001 sentinel retired)
   ```
2. **Approved AdvDep voucher** — new `advDepVoucher` step inside `createSeedvouchers.js` (tasks_07 Phase 4 explicitly suggests this): create + approve one `voc_type: "AdvDep"` so a relation carries `adv_dep > 0` in the snapshot; add a linked drawdown pair when tasks_07 v2 ships.
3. **Scope-diverse users** — extend `createUsers.js` so each company has at least one restricted-scope user (`CView`/`DView`) for §2.2.1.
4. **`version_gate` counters doc** — add to `addSAspecs.js` (it already creates counters/config docs).

Every factory keeps the local-only rule: writes go through the in-process app (supertest + `db.dheader`) or direct mongoose against the memory server; snapshots land in `temp/seed/data/`.

## 2.4 House idiom — the worked example new tests copy

`test/api_v3/features/credit/index.test.js` (skeleton, exact paths/assertions per repo reality):

```js
const supertest = require("supertest");
const app = require("../../../dzzlo_oms_test");
const request = supertest(app);
const db = require("../../../database");
const { beforeAllHelper } = require("../../helper/beforeAll");
const mongoose = require("mongoose");

describe("Credit engine — order gating on max_cr_lmt", () => {
  let cust_msts_data, dealer_msts_data, dealer_custs_data, users_data, prod_msts_data;

  beforeAll(async () => {
    await db.connect();
    ({ cust_msts_data, dealer_msts_data, dealer_custs_data, users_data, prod_msts_data } =
      await beforeAllHelper({
        cust_msts_data: true,
        dealer_msts_data: true,
        dealer_custs_data: true,
        users_data: true,
        prod_msts_data: true,
      }));
  });

  afterAll(async () => {
    await db.close();
  });

  it("rejects an order that would exceed the relation's max_cr_lmt", async () => {
    const relation = dealer_custs_data.find((r) => r.max_cr_lmt > 0); // capped relation from seed §2.3.1
    const response = await request
      .post("/api/v3/order_msts")
      .set(db.dheader)
      .send({ /* order params built from seeded ids — same shape createOrders factory uses */ });
    expect(response.body.success).toBe(false);
    // exact status + error message: confirm against api_v3/services/order_msts.js when writing
  });
});
```

Rules the example encodes: import the shared test app; one memory-server per describe via `db.connect()`/`db.close()`; fixtures only via `beforeAllHelper`; auth via `db.dheader` (bearer cases per §2.2.1); assertion helpers from `helper/collections/*` for shapes.

## 2.5 Definition of done per flow — the mutation smoke

A flow row is ✅ only if breaking its business rule turns the suite red. Ritual: temporarily invert/disable the rule in the service (e.g. comment out the credit check), run the flow's suite, confirm failure, revert. Record the check in the PR description. This catches assertion-free tests — the current `App.test.tsx` disease — before they enter the backbone.

## 2.6 DIP — blocked, scoped out pending Q1

`/api/dip/v1` routes require `models/dip_models/*`, which require `helpers/db_conn.js`, which **connects to remote Atlas at import time**. DIP therefore cannot be mounted in the test app without a small refactor (lazy/injected `db_dip` connection). Decision needed (⏳ Q1): if DIP is ranked P0/P1, add a "Phase 2b — DIP harness" (connection injection + seed factories for dealers/decants/meter_reads/insps + suites); default P2 = defer, and dip-web tests mock DIP responses via MSW meanwhile.

## 2.7 Verification — how we know Phase 2 is done

- §2.1 table fully ✅ for P0/P1 rows (P2 rows explicitly deferred with a note).
- `yarn test:full` green; runtime within budget (⏳ Q10: ≤ 5 min target).
- Mutation smoke performed and recorded for each new suite.
- Seed snapshot regenerates deterministically (`yarn seed` twice → same collection counts).

## Phase 2 checklist

- [ ] Flow→test map (§2.1) committed to `docs/testing.md` and kept current in PRs
- [ ] `auth/authorization/index.test.js` — bearer/role/scope matrix
- [ ] Company-status route-level gate cases
- [ ] `features/credit/index.test.js` — capped/blocked/unlimited + presenter + AdvDep interplay
- [ ] `features/version_gate/index.test.js`
- [ ] Order delivery-OTP coverage audited (suite added if thin)
- [ ] Invoice GST/TCS coverage audited (extended if thin)
- [ ] `getAll/active.test.js` un-skips resolved; skipped `getAll/index.test.js` deleted or revived
- [ ] Seed factories: credit variants, approved AdvDep, scope-diverse users, `version_gate` doc
- [ ] Fin-year rollover / month-recompute parity confirmed vs `202405_v2` before its deletion
- [ ] DIP decision recorded (Q1) — Phase 2b spawned or deferral noted
