# DB-7 Audit: Missing `.select()` Field Projections

> Full codebase audit of Mongoose queries missing `.select()` field projection.
> Without `.select()`, MongoDB returns all document fields — wasting network bandwidth, memory, and serialization time.
> Prioritized by request frequency and business impact.

---

## Implementation Status (2026-04-13)

**Status:** Implementation complete (11 parallel agents) — **~177 of ~184 queries fixed across 20 files.**

- All edits scoped to `dzzlooms_app/api_v3/`. `.select()` placed before `.lean()` everywhere.
- Whitelist projections used; RTK consumers verified per file.
- **Total tests run:** ~274 pass, 23 skip, 0 fail.
- **No commits made yet.**

### Per-file results

| File                                       | Queries fixed                          | Tests                                |
| ------------------------------------------ | -------------------------------------- | ------------------------------------ |
| `services/order_msts.js`                   | 13                                     | no test suite — re-read verification |
| `services/so_msts.js`                      | 7 (L765 kept non-lean — `.deleteOne()`) | 26/26 pass                           |
| `services/invs.js`                         | 8                                      | no test suite                        |
| `services/invites.js`                      | 4 + 2 chain-order bug fixes            | no test suite                        |
| `services/auth.js`                         | 3 safe reads (other 7 skipped — `.save()`/methods) | 33 pass / 4 skip          |
| `services/dealer_custs.js`                 | 6 (L158 kept non-lean — `deleteOne()`) | 34 pass / 4 skip                     |
| `services/veh_trns.js`                     | 19                                     | 8 pass                               |
| `services/voc_msts.js`                     | 10 (L489 kept non-lean — `deleteOne()`) | 29 pass / 4 skip                    |
| `services/dvr_msts.js`                     | 17                                     | covered ↓                            |
| `services/veh_msts.js`                     | 6 (L65/92 kept non-lean)               | covered ↓                            |
| `services/dealer_msts.js`                  | 5                                      | covered ↓                            |
| `services/cust_msts.js`                    | 4                                      | 124 pass / 11 skip across 6 master suites |
| `services/prod_msts.js`                    | 8                                      | (covered above)                      |
| `services/users.js`                        | 25                                     | no test suite                        |
| `services/psocs.js`                        | 16                                     | no test suite                        |
| `services/veh_reqs.js`                     | 5 of 8 (3 skipped — doc-method use)    | 28 pass / 3 skip                     |
| `services/rate_msts.js`                    | 1                                      | no test suite                        |
| `controllers/collections/prod_disc.js`     | 3                                      | no test suite                        |
| `controllers/collections/users.js`         | 1                                      | no test suite                        |
| `controllers/dbUpdates/dlr_psoc_prod.js`   | 2                                      | no test suite                        |
| `controllers/sadmin/units_hsns.js`         | 4                                      | no test suite                        |

### Not done (out of scope)

- **`helpers/newProdList.js` (1 HIGH query)** — Blocked by AI.md rule "Write ONLY inside `api_v3/`". Needs explicit authorization to edit `helpers/`.
- **7 of `auth.js` queries** — require `.save()` / instance methods; per audit doc guidance, left alone.
- **3 of `veh_reqs.js`** (L131 / L221 / L284) — same reason (document-method usage).
- **2 of `veh_msts.js`** (L65 / L92) — flagged in audit as a separate concern (DB-8 territory — needs delete after read).

### Notable RTK-driven projection expansions

- **`order_msts.js` L412 + L1024** — expanded beyond audit suggestion to cover all fields consumed by `OneOrder.js`, `newDesign.js`, `OTPmodule`, `EmergencyOTPNEW`, `NewInvoice`, `DailySummary`.
- **`invs.js` L1130 / L1132 / L1134** — expanded with full GST / PDF template fields.
- **`auth.js` L30 / L34** (`getUserCompany`) — used full whitelist; feeds `state.auth.company` consumed by 60+ screens.

---

## How to Use This File

1. **Start with HIGH priority** — these are hot paths hit on every order operation
2. **Fix one file at a time**, test the affected endpoints after each
3. **Use whitelist pattern** — `.select("field1 field2")` is safer than `.select("-excluded")`
4. **Always pair** `.select()` before `.lean()` — reversed order negates the projection

---

## Reference Pattern (from `helpers/auth.js`)

```js
// CORRECT — .select() before .lean()
const user = await User.findOne({ _id })
  .select(
    "-resetPasswordToken -resetPasswordExpire -OTP_Value -OTP_Expire -__v",
  )
  .lean();

// CORRECT — whitelist approach (preferred)
const dealer = await DealerMaster.findById(id)
  .select("dealer_name dealer_code oil_co oil_do")
  .lean();
```

---

## HIGH Priority — Order Processing Pipeline

### File: `api_v3/services/order_msts.js` (13 queries)

| #   | Line | Query                                                           | Suggested `.select()`                                                                                    |
| --- | ---- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 1   | 518  | `OrderMaster.findOne({ _id: body._id }).lean()`                 | `.select('order_no order_status products cust_id dealer_id veh_id otp_to otp_val otp_expire')`           |
| 2   | 554  | `DriverMaster.findOne({ veh_id }).lean()`                       | `.select('name phone code email')`                                                                       |
| 3   | 555  | `User.findById(otpUserId).lean()`                               | `.select('username phone email')`                                                                        |
| 4   | 665  | `OrderMaster.findOne({ _id, order_status, otp_expire }).lean()` | `.select('otp_val')`                                                                                     |
| 5   | 701  | `veh_trns.findOne({ veh_id, cust_id }).lean()`                  | `.select('veh_id veh_status cust_id')`                                                                   |
| 6   | 816  | `OrderMaster.findById(id).lean()`                               | `.select('order_status otp_val otp_expire cust_id dealer_id products cs_reimb_amt veh_id cust_user_id')` |
| 7   | 833  | `DealerCustomer.findOne({ cust_id, dealer_id }).lean()`         | `.select('ftank_amt cust_bal max_cr_lmt adv_dep cs_reimb')`                                              |
| 8   | 913  | `OrderMaster.findById(id).lean()`                               | `.select('products order_status')`                                                                       |
| 9   | 930  | `ProdMst.find({ _id: { $in: prod_ids } }).lean()`               | `.select('_id categories')`                                                                              |
| 10  | 983  | `OrderMaster.findById(id).lean()`                               | `.select('order_status so_id otp_val otp_expire')`                                                       |
| 11  | 1024 | `OrderMaster.findById(id).lean()`                               | `.select('order_no order_status products cust_id dealer_id veh_id cust_user_id cs_reimb_amt so_id')`     |
| 12  | 1028 | `DriverMaster.findOne({ veh_id }).lean()`                       | `.select('name phone code email')`                                                                       |
| 13  | 412  | `SOMaster.find({ _id: { $in: order_soIDs } }).lean()`           | `.select('_id so_id dealer_user_id dvr_id')`                                                             |

**How to verify:**

- API: Test order create, process OTP, edit order, delete order, getOnePO endpoints
- App: Full order flow — create, OTP send/verify, edit, delete, detail view

---

### File: `helpers/newProdList.js` (1 query)

| #   | Line | Query                                             | Suggested `.select()`                  |
| --- | ---- | ------------------------------------------------- | -------------------------------------- |
| 1   | 10   | `ProdMst.find({ _id: { $in: prod_ids } }).lean()` | `.select('_id categories rates name')` |

**Why critical:** Called on every order create and order edit — one of the most frequently hit helpers.

**How to verify:**

- API: Create/edit order with multiple products. Verify product rates and categories resolve correctly.

---

### File: `api_v3/services/so_msts.js` (7 queries)

| #   | Line | Query                                             | Suggested `.select()`                                                             |
| --- | ---- | ------------------------------------------------- | --------------------------------------------------------------------------------- |
| 1   | 21   | `OrderMaster.findById(orderId).lean()`            | `.select('products veh_id dealer_id cust_id cust_user_id cs_reimb_amt order_no')` |
| 2   | 26   | `DriverMst.findOne({ veh_id }).lean()`            | `.select('name phone code')`                                                      |
| 3   | 164  | `SOMaster.findById(id).lean()`                    | `.select('products so_status dealer_id cust_id veh_id')`                          |
| 4   | 183  | `ProdMst.find({ _id: { $in: prod_ids } }).lean()` | `.select('_id categories rates name')`                                            |
| 5   | 209  | `OrderMaster.findOne({ so_id }).lean()`           | context check needed                                                              |
| 6   | 765  | `SOMaster.findById(id)`                           | also missing `.lean()`                                                            |
| 7   | 770  | `OrderMaster.findOne({ so_id: id }).lean()`       | context check needed                                                              |

**How to verify:**

- API: Test SO create, SO detail, SO status update endpoints
- App: Sales order flow end-to-end

---

### File: `api_v3/services/invs.js` (8 queries)

| #   | Line | Query                                                       | Suggested `.select()`                              |
| --- | ---- | ----------------------------------------------------------- | -------------------------------------------------- |
| 1   | 626  | `Inv.findById(INVOICE_ID).lean()`                           | context check needed                               |
| 2   | 1011 | `month_crdrs.findOne({ dealer_id, cust_id, month }).lean()` | context check needed                               |
| 3   | 1035 | `DealerCustomer.findOne({ dealer_id, cust_id }).lean()`     | `.select('cust_bal max_cr_lmt adv_dep cs_reimb')`  |
| 4   | 1119 | `SalesOrder.find({ _id: { $in: SO } }).lean()`              | context check needed                               |
| 5   | 1125 | `ProdMst.find({ _id: prod_ids }).lean()`                    | `.select('_id name rates categories')`             |
| 6   | 1130 | `DealerMaster.findById(dealer_id).lean()`                   | `.select('dealer_name dealer_code oil_co oil_do')` |
| 7   | 1132 | `DealerCustomer.findOne({ dealer_id, cust_id }).lean()`     | context check needed                               |
| 8   | 1134 | `CustomerMaster.findById(cust_id).lean()`                   | `.select('cust_name cust_address city state')`     |

**How to verify:**

- API: Test invoice creation and detail endpoints
- App: Invoice flow — create, view detail, PDF generation

---

## MEDIUM Priority — Regular Operations

### File: `api_v3/services/dealer_custs.js` (6 queries)

| #   | Line | Query                                                | Notes                  |
| --- | ---- | ---------------------------------------------------- | ---------------------- |
| 1   | 158  | `month_crdrs.findOne({ dealer_id, cust_id, month })` | also missing `.lean()` |
| 2   | 640  | `DC.findOne({ dealer_id, cust_id }).lean()`          |                        |
| 3   | 647  | `DC.findOne({ dealer_id, cust_id }).lean()`          |                        |
| 4   | 739  | `DC.findOne({ dealer_id, cust_id }).lean()`          |                        |
| 5   | 756  | `DC.findOne(dc).lean()`                              |                        |
| 6   | 778  | `DC.findOne(dc)`                                     | also missing `.lean()` |

---

### File: `api_v3/services/veh_trns.js` (19 queries)

| #   | Line    | Query                                                        |
| --- | ------- | ------------------------------------------------------------ |
| 1   | 42-44   | `VehicleTrn.find({ cust_id: { $in: customerIds } }).lean()`  |
| 2   | 49      | `DriverMaster.find({ veh_id: { $in: vIds } }).lean()`        |
| 3   | 71      | `VehicleMaster.find({ _id: { $in: vehicleIds } }).lean()`    |
| 4   | 73-75   | `VehicleTrn.find({ veh_id: { $in: vehicleIds } }).lean()`    |
| 5   | 84-86   | `DriverMaster.find({ veh_id: { $in: vehicleIds } }).lean()`  |
| 6   | 122     | `VehicleTrn.find({ cust_id }).sort("-createdAt").lean()`     |
| 7   | 128     | `VehicleMaster.find({ _id: { $in: vehIds } }).lean()`        |
| 8   | 148-150 | `DriverMaster.find({ veh_id: { $in: vehTrnvehId } }).lean()` |
| 9   | 194-198 | `VehReq.find({ veh_id, $or, req_status: "PENDING" }).lean()` |
| 10  | 205     | `VehicleMaster.findById(veh_id).lean()`                      |
| 11  | 207     | `DriverMaster.findOne({ veh_id }).lean()`                    |
| 12  | 212     | `VehicleTrn.findOne({ _id: body._id }).lean()`               |
| 13  | 214     | `DriverMaster.findOne({ veh_id: vehicleId }).lean()`         |
| 14  | 233     | `VehicleTrn.findOne({ _id: id, cust_id }).lean()`            |
| 15  | 243     | `DriverMaster.findOne({ veh_id: vehicleId }).lean()`         |
| 16  | 262     | `VehicleTrn.findOne({ _id: body._id, cust_id }).lean()`      |
| 17  | 269     | `DriverMaster.findOne({ veh_id: vehicleId }).lean()`         |
| 18  | 296-298 | `VehicleTrn.find({ veh_id: { $in: vehIds } }).lean()`        |
| 19  | 317-319 | `DriverMaster.find({ veh_id: { $in: vehTrnvehId } }).lean()` |

---

### File: `api_v3/services/voc_msts.js` (10 queries)

| #   | Line | Query                                                   |
| --- | ---- | ------------------------------------------------------- |
| 1   | 61   | `VoucherMaster.findById(VOUCHER_ID).lean()`             |
| 2   | 245  | `month_crdrs.findOne({ ... }).lean()`                   |
| 3   | 269  | `DealerCustomer.findOne({ dealer_id, cust_id }).lean()` |
| 4   | 288  | `VoucherMaster.findById(id).lean()`                     |
| 5   | 317  | `Invoices.find({ _id: { $in: vocInvsAdj } }).lean()`    |
| 6   | 489  | `VoucherMaster.findById(id)` — also missing `.lean()`   |
| 7   | 509  | `VoucherMaster.findById(_id).lean()`                    |
| 8   | 515  | `Invoices.find({ _id: { $in: inv_ids } }).lean()`       |
| 9   | 643  | `Invoices.find({ _id: { $in: inv_ids } }).lean()`       |
| 10  | 718  | `VoucherMaster.findById(id).lean()`                     |

---

### File: `api_v3/services/auth.js` (10 queries)

| #   | Line    | Query                                                              | Notes                                                     |
| --- | ------- | ------------------------------------------------------------------ | --------------------------------------------------------- |
| 1   | 30      | `CustomerMaster.findById(user_company).lean()`                     | `getUserCompany()` — called on every login/refresh        |
| 2   | 34      | `DealerMaster.findById(user_company).lean()`                       | `getUserCompany()` — called on every login/refresh        |
| 3   | 65      | `User.findById(user_id)`                                           | also missing `.lean()` — `updaterx()`                     |
| 4   | 171     | `User.findOne({ email })`                                          | `forgotPassword()` — needs `.save()` so can't `.lean()`   |
| 5   | 197-200 | `User.findOne({ resetPasswordToken, resetPasswordExpire })`        | `resetPassword()` — needs `.save()` so can't `.lean()`    |
| 6   | 290-292 | `User.findOne({ $or: [{ email }, { phone }] })`                    | `forgotPasswordPhone()` — needs `.save()`                 |
| 7   | 333-336 | `User.findOne({ resetPasswordToken, resetPasswordExpire }).lean()` | `resetPasswordPhone()` — read-only check, add `.select()` |
| 8   | 339-342 | `User.findOne({ phone, OTP_Expire })`                              | `resetPasswordPhone()` — needs `.save()`                  |
| 9   | 364-366 | `User.findOne({ $or: [{ email }, { phone }] })`                    | `emailPhoneVerify()` — needs `.save()`                    |
| 10  | 413-416 | `User.findOne({ $or: [{ email }, { phone }], OTP_Expire })`        | `emailPhoneVerifyOTP()` — needs `.save()`                 |

**Note:** Lines 4-6, 8-10 need `.save()` or model methods (`.getOTPToken()`, `.getResetPasswordToken()`) after the query, so they cannot use `.lean()`. Adding `.select()` is possible but risky — model methods may depend on fields not included in the projection. Lines 1-2 and 7 are pure reads and should definitely get `.select()`.

---

## LOW Priority — Admin / Setup Operations

### File: `api_v3/services/dvr_msts.js` (17 queries)

Lines: 39, 71, 74, 108, 115, 220, 222, 246, 269, 274, 287, 299, 310, 322, 348, 362, 423

All are `DriverMaster.findById()`, `DriverMaster.findOne()`, or `VehicleTrn.findOne()` without `.select()`.

---

### File: `api_v3/services/users.js` (25 queries)

Lines: 129, 262, 289, 319, 346, 371, 397, 425, 434, 438, 443, 481, 491, 501, 504, 521, 544, 550, 554, 559, 597, 607, 617, 620, 637

Mostly `User.findById().lean()` and various model `.find()` / `.findOne()` for user deletion cascades.

---

### File: `api_v3/services/psocs.js` (16 queries)

Lines: 8, 14, 22, 24, 37, 55, 75, 98, 103, 106, 120, 153, 174, 195, 220, 263

All `PSOCS.findById(id).lean()` without `.select()`.

---

### File: `api_v3/services/prod_msts.js` (8 queries)

Lines: 83, 85, 92, 121, 167, 177, 202, 236

---

### File: `api_v3/services/veh_msts.js` (8 queries)

Lines: 13, 16, 55, 65, 68, 76, 84, 92

| #   | Line | Query                                                     | Notes                               |
| --- | ---- | --------------------------------------------------------- | ----------------------------------- |
| 1   | 13   | `VehicleMaster.findOne({ veh_reg_no }).lean()`            | `createVehicle()` — existence check |
| 2   | 16   | `VehicleTrn.findOne({ veh_id, cust_id }).lean()`          | `createVehicle()` — relation check  |
| 3   | 55   | `VehicleTrn.findById(veh_trn_new._id).lean()`             | `createVehicle()` — post-create     |
| 4   | 65   | `VehicleMaster.findById(id)` — also missing `.lean()`     | `deleteVehicle()` — needs delete    |
| 5   | 68   | `OrderMaster.find({ veh_id }).lean()`                     | `deleteVehicle()` — count check     |
| 6   | 76   | `VehReq.find({ veh_id }).lean()`                          | `deleteVehicle()` — count check     |
| 7   | 84   | `VehicleTrn.find({ veh_id }).lean()`                      | `deleteVehicle()` — count check     |
| 8   | 92   | `VehicleTrn.findOne({ veh_id })` — also missing `.lean()` | `deleteVehicle()` — needs delete    |

---

### File: `api_v3/services/dealer_msts.js` (5 queries)

Lines: 48, 89, 109, 126, 129

---

### File: `api_v3/services/veh_reqs.js` (8 queries)

Lines: 18, 63, 78, 144, 151, 221, 226, 284

---

### File: `api_v3/services/cust_msts.js` (4 queries)

Lines: 96, 113, 116, 125

---

### File: `api_v3/services/invites.js` (4 queries + 2 bugs)

| #   | Line | Query                                             | Notes                                   |
| --- | ---- | ------------------------------------------------- | --------------------------------------- |
| 1   | 78   | `users.findById(user_id).lean()`                  | `acceptInvite()` — reads `companies`    |
| 2   | 81   | `Invites.findOne({ _id, expirationTime }).lean()` | `acceptInvite()` — reads invite fields  |
| 3   | 143  | `users.findById(user_id).lean()`                  | `declineInvite()` — reads `companies`   |
| 4   | 146  | `Invites.findOne({ _id, expirationTime }).lean()` | `declineInvite()` — reads invite fields |

---

### File: `api_v3/services/rate_msts.js` (1 query)

Line: 34 — `RateMst.find({ prod_id, dealer_id })` — also missing `.lean()`

---

### File: `api_v3/controllers/collections/prod_disc.js` (3 queries)

| #   | Line | Query                                                 | Notes                                     |
| --- | ---- | ----------------------------------------------------- | ----------------------------------------- |
| 1   | 13   | `dealer_custs.findOne({ dealer_id, cust_id }).lean()` | `addDiscProd()` — reads `products` array  |
| 2   | 42   | `dealer_custs.findOne({ dealer_id, cust_id })`        | `editProdDisc()` — also missing `.lean()` |
| 3   | 73   | `dealer_custs.findOne({ dealer_id, cust_id }).lean()` | `removeProdDisc()` — existence check only |

---

### File: `api_v3/controllers/collections/users.js` (1 query)

| #   | Line | Query                                | Notes                   |
| --- | ---- | ------------------------------------ | ----------------------- |
| 1   | 115  | `User.findById(req.body._id).lean()` | reads `companies` array |

---

### File: `api_v3/controllers/dbUpdates/dlr_psoc_prod.js` (2 queries)

| #   | Line | Query                                             | Notes           |
| --- | ---- | ------------------------------------------------- | --------------- |
| 1   | 7    | `prod_msts.findOne({ _id: req.body._id }).lean()` | admin DB update |
| 2   | 8    | `PSOCS.findOne({ _id: req.body.psoc_id }).lean()` | admin DB update |

---

### File: `api_v3/controllers/sadmin/units_hsns.js` (4 queries)

| #   | Line | Query                                            | Notes                       |
| --- | ---- | ------------------------------------------------ | --------------------------- |
| 1   | 6    | `counters.findOne({ doc_name: "units" }).lean()` | `getUnits()` — read-only    |
| 2   | 15   | `counters.findOne({ doc_name: "units" }).lean()` | `addUnit()` — read + update |
| 3   | 31   | `counters.findOne({ doc_name: "hsns" }).lean()`  | `getHSN()` — read-only      |
| 4   | 42   | `counters.findOne({ doc_name: "hsns" }).lean()`  | `addHSN()` — read + update  |

---

## Architectural Note: `helpers/advancedResults.js`

The shared pagination helper (`getResults` at line 70 and `advancedResults` middleware at line 175) uses `model.find()` without a default `.select()`. It **does** apply `.select()` if the client passes `?select=field1,field2` in the query string (lines 73-76 and 178-181), but most callers don't pass this parameter.

This is an architectural consideration rather than a per-query fix — the helper serves 15+ endpoints. Options:

1. **Per-caller approach:** Add `.select()` in each service that calls `getResults()` before passing data through
2. **Helper-level approach:** Accept a `defaultSelect` parameter in `getResults()` so callers can specify fields
3. **Leave as-is:** The `advancedResults` helper returns paginated lists where clients may need varying fields

This is related to **DB-8** (`$facet` pagination refactor) and could be addressed together.

---

## Bug: `.lean()` Before `.select()` in `invites.js`

**File:** `api_v3/services/invites.js`

`.select()` must come **before** `.lean()` for the projection to take effect. These have the wrong order:

```js
// Line 16 — BROKEN: .lean() before .select() negates projection
const invitor = await users.findById(invitor_id).lean().select("_id role");

// Line 22-25 — BROKEN: same issue
users.findOne({ ... }).lean().select("_id username email phone companies");
```

**Fix:**

```js
// CORRECT order
const invitor = await users.findById(invitor_id).select("_id role").lean();

users.findOne({ ... }).select("_id username email phone companies").lean();
```

---

## Out of Scope: `api_v1/` and `api_v2/`

The older API versions (`api_v1/controllers/`, `api_v2/controllers/`) have **~770 additional queries** without `.select()`. These were not audited in detail since the active codebase uses `api_v3`. A future pass should cover these if those endpoints are still active.

Notable findings in `api_v1`:

- `api_v1/controllers/App/order_msts.js` line 38 — `OrderMaster.findOne()` without `.select()` (hot path)
- `api_v1/controllers/App/order_msts.js` line 53 — `DriverMaster.findOne()` without `.select()`
- `api_v1/controllers/App/contact_us.js` lines 61, 75 — `User.findById()` without `.select()`
- `api_v1/controllers/Auth/OTP/index.js` lines 145, 157 — `CustomerMaster` / `DealerMaster` without `.select()`

---

## Summary

| Priority | File                  | Missing `.select()` | Impact                       |
| -------- | --------------------- | ------------------- | ---------------------------- |
| **HIGH** | `order_msts.js`       | 13                  | Every order operation        |
| **HIGH** | `newProdList.js`      | 1                   | Every order create/edit      |
| **HIGH** | `so_msts.js`          | 7                   | Sales order lifecycle        |
| **HIGH** | `invs.js`             | 8                   | Invoice creation             |
| MEDIUM   | `dealer_custs.js`     | 6                   | Dealer-customer ops          |
| MEDIUM   | `veh_trns.js`         | 19                  | Vehicle transactions         |
| MEDIUM   | `voc_msts.js`         | 10                  | Voucher operations           |
| MEDIUM   | `auth.js` (service)   | 10                  | Login/register/OTP/reset     |
| LOW      | `dvr_msts.js`         | 17                  | Driver management            |
| LOW      | `users.js`            | 25                  | User management              |
| LOW      | `psocs.js`            | 16                  | PSOC config                  |
| LOW      | `veh_msts.js`         | 8                   | Vehicle master CRUD          |
| LOW      | `prod_msts.js`        | 8                   | Product master               |
| LOW      | `veh_reqs.js`         | 8                   | Vehicle requests             |
| LOW      | `dealer_msts.js`      | 5                   | Dealer master                |
| LOW      | `cust_msts.js`        | 4                   | Customer master              |
| LOW      | `invites.js`          | 4                   | Invite accept/decline        |
| LOW      | `rate_msts.js`        | 1                   | Rate master                  |
| LOW      | `prod_disc.js` (ctrl) | 3                   | Product discount controller  |
| LOW      | `users.js` (ctrl)     | 1                   | User controller              |
| LOW      | `dlr_psoc_prod.js`    | 2                   | Admin DB update              |
| LOW      | `units_hsns.js`       | 4                   | Admin superadmin ops         |
| ARCH     | `advancedResults.js`  | 2                   | Shared pagination helper     |
| BUG      | `invites.js`          | 2                   | `.lean()` before `.select()` |
|          | **TOTAL**             | **~184**            |                              |

### Recommended Approach

1. Fix `order_msts.js` (13) + `newProdList.js` (1) — highest ROI, directly on the order hot path
2. Fix `so_msts.js` (7) + `invs.js` (8) — completes the order-to-invoice lifecycle
3. Fix `invites.js` bug (2) — broken `.select()` due to wrong chain order
4. Fix `auth.js` lines 30, 34, 333 (3 safe reads) — hit on every login/refresh
5. Then MEDIUM files incrementally (`veh_trns.js` has 19 — largest batch)
6. LOW priority files can be batch-fixed in a single pass

**Estimated effort:** S-M (2-4 hours for HIGH + MEDIUM, including testing)
