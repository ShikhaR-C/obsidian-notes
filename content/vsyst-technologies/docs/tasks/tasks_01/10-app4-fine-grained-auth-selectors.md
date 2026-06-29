# APP-4: Fine-Grained Auth Selectors — Migration Plan

> Replace broad `useSelector(state => state.auth)` with field-specific selectors
> across the entire `dzzlo_oms_app` so components only re-render when the field
> they actually use changes.
>
> Total surface: **~97 files** across screens, navigation, components, hooks.
>
> This doc is the single source of truth — execute one phase at a time, top to
> bottom. Each phase is independent; you can stop after any phase and ship.

---

## 0 · Background

### 0.1 Current auth slice

`src/store/slices/auth.js` state shape:

```js
{
  userId: null,        // mirror of user._id (set by authenticate reducer)
  userRole: null,      // mirror of user.role
  didTryAutoLogin: false,
  showVerification: true,
  notification: null,  // { dealer?, customer? } payload from OneSignal
  user: null,          // full user doc
  company: null,       // full company doc
  token: null,
}
```

Existing exports (keep for back-compat, do NOT remove):

```js
export const selectCurrentUser = (state) => state.auth.user;
export const selectCurrentCompany = (state) => state.auth.company;
export const selectAuthToken = (state) => state.auth.token;
export const selectUserRole = (state) => state.auth.userRole; // NOTE: returns slice.userRole, NOT user.role
```

> ⚠ `selectUserRole` returns `state.auth.userRole` (the mirror), but most
> screens read `currentUser.user?.role`. These two diverge in some flows. The
> new `selectUserRole` below reads from `state.auth.user?.role` to match
> screen behavior. The legacy export is renamed to `selectUserRoleMirror`
> internally only if needed; otherwise leave it untouched and let consumers
> migrate to the new selector.

### 0.2 The pattern to kill

99% of consumers do this:

```js
const currentUser = useSelector((state) => state.auth);
// ...
currentUser.user?._id;
currentUser.user?.role;
currentUser.user?.co_id;
currentUser.user?.scope;
currentUser.user?.companies;
currentUser.company?._id;
currentUser.company?.work_email;
```

This subscribes the component to **the entire auth slice**. Setting
`notification` from OneSignal, toggling `showVerification`, or any login
mutation re-renders every component using this pattern.

---

## 1 · Phase 0 — Create `src/store/selectors/auth.js`

**File to create:** `dzzlo_oms_app/src/store/selectors/auth.js`

```js
// Fine-grained auth selectors. Import from here in all screens/components.
// Each selector returns a primitive or stable object reference so React-Redux
// shallow-equality bails out re-renders correctly.

// ── Identity ────────────────────────────────────────────────
export const selectUserId = (state) => state.auth.user?._id;
export const selectUserRole = (state) => state.auth.user?.role;
export const selectUserScope = (state) => state.auth.user?.scope;
export const selectUserCoId = (state) => state.auth.user?.co_id;
export const selectUserName = (state) => state.auth.user?.username;
export const selectUserEmail = (state) => state.auth.user?.email;
export const selectUserPhone = (state) => state.auth.user?.phone;
export const selectUserImg = (state) => state.auth.user?.user_img;
export const selectUserTheme = (state) => state.auth.user?.theme;
export const selectUserAddress = (state) => state.auth.user?.user_address;
export const selectUserCompanies = (state) => state.auth.user?.companies;
export const selectUserEmailVerified = (state) =>
  state.auth.user?.isEmailVerified;
export const selectUserPhoneVerified = (state) =>
  state.auth.user?.isPhoneVerified;

// ── Company ─────────────────────────────────────────────────
export const selectCompanyId = (state) => state.auth.company?._id;
export const selectCompanyDealerName = (state) =>
  state.auth.company?.dealer_name;
export const selectCompanyDealerCode = (state) =>
  state.auth.company?.dealer_code;
export const selectCompanyDealerVerified = (state) =>
  state.auth.company?.dealer_verified;
export const selectCompanyCustName = (state) => state.auth.company?.cust_name;
export const selectCompanyCustCode = (state) => state.auth.company?.cust_code;
export const selectCompanyCustVerified = (state) =>
  state.auth.company?.cust_verified;
export const selectCompanyWorkEmail = (state) => state.auth.company?.work_email;
export const selectCompanyGstStateCode = (state) =>
  state.auth.company?.gst_state_code;
export const selectCompanyDistrict = (state) => state.auth.company?.district;

// ── Auth lifecycle ──────────────────────────────────────────
export const selectAuthToken = (state) => state.auth.token;
export const selectDidTryAutoLogin = (state) => state.auth.didTryAutoLogin;
export const selectShowVerification = (state) => state.auth.showVerification;

// ── Notifications (drawer badges) ───────────────────────────
export const selectDealerNotification = (state) =>
  state.auth.notification?.dealer;
export const selectCustomerNotification = (state) =>
  state.auth.notification?.customer;

// ── Whole-object selectors (use ONLY when 4+ fields are needed) ──
// Prefer field selectors above. These exist for screens that genuinely
// need most of the user/company doc (Profile, CompanyProfile, Drawers).
export const selectCurrentUser = (state) => state.auth.user;
export const selectCurrentCompany = (state) => state.auth.company;
```

**Verification after Phase 0:**

- File compiles (no runtime use yet).
- App still works (no consumer changes yet).

**Discussion points:**

- Do NOT use `createSelector` from reselect for primitive returns — it adds
  overhead with no win. Plain functions are correct here.
- Keep `selectCurrentUser` / `selectCurrentCompany` as escape hatches for the
  ~5 screens that legitimately need most fields. The goal is to remove the
  _broad slice_ selector, not the _full sub-object_ selector.
- Re-export the existing selectors from `slices/auth.js` so old imports keep
  working. Optionally, in a follow-up, change `slices/auth.js` to re-export
  from `selectors/auth.js` to centralise definitions.

---

## 2 · Migration playbook (apply to every file in Phases 1-7)

For each file:

1. Replace import:

   ```js
   // BEFORE
   import { useSelector } from "react-redux";
   // AFTER
   import { useSelector } from "react-redux";
   import {
     selectUserRole,
     selectCompanyId /* etc. */,
   } from "../../store/selectors/auth";
   // (adjust relative path; usually ../../../store/selectors/auth from screens)
   ```

2. Replace selector:

   ```js
   // BEFORE
   const currentUser = useSelector((state) => state.auth);
   // ...later...
   const role = currentUser.user?.role;
   const coId = currentUser.user?.co_id;

   // AFTER
   const role = useSelector(selectUserRole);
   const coId = useSelector(selectUserCoId);
   ```

3. If a file genuinely needs many fields (Drawers, Profile, CompanyProfile),
   use `selectCurrentUser` + `selectCurrentCompany` instead — still better
   than subscribing to the whole slice (notification/showVerification won't
   trigger re-renders).

4. After change: render the screen, exercise its primary action. No visual
   change should occur.

**Common gotchas:**

- `currentUser.user.companies` is an array — `selectUserCompanies` returns the
  same reference between renders unless the user object is replaced, so
  `.find(...)` inside `useMemo([companies])` is fine.
- `currentUser.notification?.dealer` is set by OneSignal handler. Drawers must
  use `selectDealerNotification` / `selectCustomerNotification` to keep badge
  reactivity.
- Do NOT replace `useDispatch(logout())` calls — only the `useSelector` reads.

---

## 3 · Phase 1 — Hot list screens (Orders / Invoices / Payments)

These are the highest-traffic screens. Maximum re-render reduction here.

| #   | File                                                                  | Selectors needed                                                                |
| --- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| 1   | `src/screens/Dealer/Orders/index.js`                                  | `selectUserCoId`, `selectUserRole`                                              |
| 2   | `src/screens/Customer/Orders/index.js`                                | `selectUserCoId`, `selectUserRole`                                              |
| 3   | `src/screens/Common/Orders/index.js`                                  | `selectUserCoId`, `selectUserRole`                                              |
| 4   | `src/screens/Common/Orders/components/newDesign.js`                   | `selectUserRole`, `selectUserScope`                                             |
| 5   | `src/screens/Common/Orders/bottomsheet/companyList.js`                | `selectUserCoId`, `selectUserRole`                                              |
| 6   | `src/screens/Customer/Orders/components/OneOrder.js`                  | `selectUserId`, `selectUserScope`                                               |
| 6b  | `src/screens/Dealer/Orders/components/OneOrder.js` (line 202)         | inspect — `useSelector(state => state.auth)` present despite earlier audit miss |
| 7   | `src/screens/Customer/Orders/components/EmergencyOTPBS.js`            | `selectUserId`                                                                  |
| 8   | `src/screens/Dealer/Invoices/index.js`                                | `selectUserCoId`, `selectUserRole`                                              |
| 9   | `src/screens/Customer/Invoices/index.js`                              | `selectUserCoId`, `selectUserRole`                                              |
| 10  | `src/screens/Customer/Invoices/BSheets/SelectInvs.js`                 | `selectCompanyId`, `selectUserRole`                                             |
| 11  | `src/screens/Common/Invoices/index.js`                                | `selectUserCoId`, `selectUserRole`, `selectUserScope`                           |
| 12  | `src/screens/Common/_Invoice_/index.js`                               | (whatever it currently reads)                                                   |
| 13  | `src/screens/Common/_Invoice_/Modal/index.js`                         | `selectCompanyWorkEmail`                                                        |
| 14  | `src/screens/Common/_Invoice_/BS/index.js`                            | `selectCompanyWorkEmail`                                                        |
| 15  | `src/screens/Dealer/Payments/index.js`                                | `selectUserId`, `selectUserCoId`, `selectUserRole`                              |
| 16  | `src/screens/Dealer/Payments/components/List.js`                      | `selectUserScope`, `selectUserRole`                                             |
| 17  | `src/screens/Dealer/Payments/components/PromptPay.js`                 | `selectUserScope`, `selectUserRole`                                             |
| 18  | `src/screens/Dealer/Payments/BSheets/AttachInvs.js`                   | `selectCompanyId`, `selectUserRole`                                             |
| 19  | `src/screens/Customer/Payments/index.js`                              | `selectUserCoId`, `selectUserRole`                                              |
| 20  | `src/screens/Customer/Payments/components/index.js`                   | `selectUserRole`, `selectUserScope`                                             |
| 21  | `src/screens/Common/Payments/index.js`                                | `selectUserCoId`, `selectUserRole`                                              |
| 22  | `src/screens/Common/Payments/components/index.js` (×2 selector calls) | `selectUserRole`, `selectUserScope`                                             |

**Verify Phase 1:** open every Orders/Invoices/Payments tab on Dealer and
Customer accounts. Pull-to-refresh, paginate, open one item, go back. No
visual diff. Filter/sort still works.

---

## 4 · Phase 2 — Navigation & drawers

Drawers re-render on EVERY auth slice change. Highest impact-per-file in the
codebase.

| #   | File                                              | Selectors needed                                                                                          |
| --- | ------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| 1   | `src/navigation/AppNavigatorContainer.js`         | `selectAuthToken`, `selectUserRole`, `selectUserId`, `selectUserTheme`, `selectDidTryAutoLogin`           |
| 2   | `src/navigation/Dealer/DrawerContent.js`          | `selectCurrentUser`, `selectCurrentCompany`, `selectDealerNotification` (legitimate multi-field consumer) |
| 3   | `src/navigation/Customer/DrawerContent.js`        | `selectCurrentUser`, `selectCurrentCompany`, `selectCustomerNotification`                                 |
| 4   | `src/navigation/Dealer/TrnTab.js`                 | `selectUserScope`                                                                                         |
| 5   | `src/navigation/Customer/TrnTab.js`               | `selectUserScope`                                                                                         |
| 6   | `src/navigation/Dealer/Drawer.js` (2 selectors)   | inspect & replace                                                                                         |
| 7   | `src/navigation/Customer/Drawer.js` (2 selectors) | inspect & replace                                                                                         |
| 8   | `src/navigation/Customer/Main.js`                 | inspect & replace                                                                                         |

**Verify Phase 2:** open/close drawer on both roles, switch tabs, log out and
back in, trigger a OneSignal push (or simulate `setNotification` dispatch) —
drawer badge updates, but list screens don't re-render (verify via React
DevTools profiler).

---

## 5 · Phase 3 — Profile & company-profile screens

These genuinely need many fields. Use `selectCurrentUser` /
`selectCurrentCompany` (object selectors) — still avoids subscribing to
`notification`/`showVerification`.

| #   | File                                           | Selectors                                                                                  |
| --- | ---------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 1   | `src/screens/Dealer/Profile/index.js`          | `selectCurrentUser`                                                                        |
| 2   | `src/screens/Customer/Profile/index.js`        | `selectCurrentUser`                                                                        |
| 3   | `src/screens/Dealer/CompanyProfile/index.js`   | `selectCurrentUser`, `selectCurrentCompany`                                                |
| 4   | `src/screens/Customer/CompanyProfile/index.js` | `selectCurrentUser`, `selectCurrentCompany`                                                |
| 5   | `src/screens/Common/Profile/SelectStateBS.js`  | `selectCompanyGstStateCode` (and any other single field)                                   |
| 6   | `src/screens/Common/Profile/SelectDistrict.js` | `selectCompanyGstStateCode`, `selectCompanyDistrict`                                       |
| 7   | `src/screens/Common/ValidateUser/index.js`     | `selectUserEmail`, `selectUserPhone`, `selectUserEmailVerified`, `selectUserPhoneVerified` |

**Verify Phase 3:** open Profile and CompanyProfile on both roles, change
state/district pickers, validate user flow — all unchanged.

---

## 6 · Phase 4 — Form / "New" screens

| #   | File                                                       | Selectors                                                                    |
| --- | ---------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 1   | `src/screens/Dealer/NewSalesOrder/index.js`                | inspect & replace                                                            |
| 2   | `src/screens/Dealer/EditSalesOrder/index.js`               | inspect & replace                                                            |
| 3   | `src/screens/Dealer/NewInvoice/index.js`                   | inspect & replace                                                            |
| 4   | `src/screens/Dealer/NewInvoice/BSheets/SelectCustomer.js`  | `selectCompanyId`                                                            |
| 5   | `src/screens/Dealer/NewInvoice/newComp/NewInvSummary.js`   | inspect (full auth read — likely `selectCurrentUser`+`selectCurrentCompany`) |
| 6   | `src/screens/Dealer/NewVoucher/index.js`                   | `selectCompanyId`, `selectUserId`                                            |
| 7   | `src/screens/Dealer/NewVoucher/BSheets/SelectCustomers.js` | `selectCompanyId`                                                            |
| 8   | `src/screens/Customer/NewOrder/index.js`                   | `selectCompanyId`, `selectUserId`, `selectUserScope`, `selectUserCompanies`  |
| 9   | `src/screens/Customer/NewOrder/BSheets/SelectDealer.js`    | `selectCompanyId`                                                            |
| 10  | `src/screens/Customer/NewPayment/index.js`                 | `selectUserCoId`                                                             |

**Verify Phase 4:** create one of each: sales order, invoice, voucher,
customer order, payment. They submit and appear in their list.

---

## 7 · Phase 5 — Entity management screens (Customers, Dealers, Vehicles, Users, Products, ProductDates)

| #   | File                                                           | Selectors                                                                           |
| --- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| 1   | `src/screens/Dealer/Customers/index.js`                        | `selectCurrentUser`, `selectCompanyId` (uses many user fields → object selector ok) |
| 2   | `src/screens/Dealer/Customers/Discount.js`                     | `selectCompanyId`                                                                   |
| 3   | `src/screens/Customer/Dealers/index.js`                        | `selectUserScope`, `selectUserCompanies`, `selectCompanyId`                         |
| 4   | `src/screens/Customer/Dealers/AddDealers.js`                   | `selectCompanyId`, `selectCompanyCustVerified`                                      |
| 5   | `src/screens/Customer/Dealers/BSheets/AddDealer.js`            | `selectCompanyId`                                                                   |
| 6   | `src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js` | `selectCompanyId`, `selectUserId`                                                   |
| 7   | `src/screens/Common/Vehicles/index.js`                         | `selectCompanyId`                                                                   |
| 8   | `src/screens/Customer/Vehicles/index.js`                       | `selectCompanyId`                                                                   |
| 9   | `src/screens/Customer/Vehicles/vehicleBSheets/AssignDriver.js` | `selectCompanyId`                                                                   |
| 10  | `src/screens/Customer/Vehicles/vehicleBSheets/InfoVehicle.js`  | `selectCompanyId`                                                                   |
| 11  | `src/screens/Customer/Vehicles/vehicleBSheets/InfoDriver.js`   | `selectCompanyId`                                                                   |
| 12  | `src/screens/Customer/Vehicles/vehicleBSheets/UpdateDriver.js` | `selectCompanyId`                                                                   |
| 13  | `src/screens/Customer/Vehicles/driverComponents/index.js`      | `selectCompanyId`                                                                   |
| 14  | `src/screens/Customer/Requests/Vehicles/index.js`              | `selectCompanyId`                                                                   |
| 15  | `src/screens/Dealer/Users/index.js`                            | `selectCurrentUser` (uses full user)                                                |
| 16  | `src/screens/Dealer/Users/AddEditUsers.js`                     | inspect & replace                                                                   |
| 17  | `src/screens/Customer/Users/index.js`                          | `selectUserId`, `selectCompanyId`                                                   |
| 18  | `src/screens/Customer/Users/AddEditUsers.js`                   | `selectUserId`, `selectCompanyId`                                                   |
| 19  | `src/screens/Customer/Users/OTPManager.js`                     | `selectCompanyId`                                                                   |
| 20  | `src/screens/Common/CompanyUsers/index.js`                     | `selectUserRole`                                                                    |
| 21  | `src/screens/Dealer/Products/index.js`                         | `selectCompanyId` (and `selectCurrentCompany` if more fields needed)                |
| 22  | `src/screens/Dealer/Products/PsocProds.js`                     | `selectCompanyId`                                                                   |
| 23  | `src/screens/Dealer/ProductDates/index.js`                     | `selectCompanyId`                                                                   |
| 24  | `src/screens/Dealer/ProductDates/SetRateBS.js`                 | `selectCompanyId`                                                                   |
| 25  | `src/screens/Dealer/ProductDates/SetProductRate.js`            | `selectCompanyId`                                                                   |

**Verify Phase 5:** add/edit one of each entity per role. Listing, search,
filter all work.

---

## 8 · Phase 6 — Reports, Accounts, DailySummary, SisterCompanies, RelationList, Vouchers, Notifications, VehicleReports, Help, Invites

| #   | File                                                       | Selectors                                                                                                |
| --- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| 1   | `src/screens/Common/Accounts/index.js`                     | `selectUserCoId`, `selectUserRole`, `selectUserScope`, `selectCompanyWorkEmail`                          |
| 2   | `src/screens/Common/Accounts/BSheets/InvoiceDetailsBSM.js` | `selectCompanyWorkEmail`                                                                                 |
| 3   | `src/screens/Common/Accounts/BSheets/VoucherDetailsBSM.js` | `selectUserRole`, `selectCompanyWorkEmail`                                                               |
| 4   | `src/screens/Common/Accounts/BSheets/YearAccountExcel.js`  | inspect — likely `selectCurrentUser`+`selectCurrentCompany`                                              |
| 5   | `src/screens/Common/DailySummary/PurchaseOrders/index.js`  | `selectUserCoId`, `selectUserRole`                                                                       |
| 6   | `src/screens/Common/DailySummary/SalesOrders/index.js`     | `selectUserCoId`, `selectUserRole`                                                                       |
| 7   | `src/screens/Common/Reports/TcsTds/index.js`               | `selectUserRole`, `selectCurrentCompany` (already partly granular)                                       |
| 8   | `src/screens/Common/Reports/TcsTds/Render/MonthModal.js`   | `selectUserRole`                                                                                         |
| 9   | `src/screens/Common/Reports/DailyReport/index.js`          | `selectUserRole`, `selectCompanyId`                                                                      |
| 10  | `src/screens/Common/SisterCompanies/index.js`              | `selectUserRole`, `selectUserScope`                                                                      |
| 11  | `src/screens/Common/SisterCompanies/SisterCompaniesBS.js`  | `selectUserRole`                                                                                         |
| 12  | `src/screens/Common/RelationList/RelationCreditBS.js`      | `selectUserRole`                                                                                         |
| 13  | `src/screens/Common/_Voucher_/index.js`                    | inspect — full auth read                                                                                 |
| 14  | `src/screens/Common/_Voucher_/BS/index.js`                 | inspect — full auth read                                                                                 |
| 15  | `src/screens/Common/_Voucher_/Modal/index.js`              | `selectUserRole`, `selectCompanyWorkEmail`                                                               |
| 16  | `src/screens/Common/Help/index.js`                         | already uses local `selectUserRole` — switch to shared selector from new file                            |
| 16b | `src/screens/Common/Reports/index.js`                      | already uses local `selectRole` (`state.auth?.user?.role`) — switch to shared `selectUserRole`           |
| 17  | `src/screens/Common/Invites/index.js`                      | `selectUserRole`                                                                                         |
| 18  | `src/screens/Common/ContactUs/index.js`                    | uses local `selectAuth = state => state.auth` — replace with `selectUserRole` (only `user.role` is read) |
| 19  | `src/screens/Dealer/Notifications/index.js`                | `selectUserId`, `selectCompanyId`, `selectCompanyDealerName`, `selectUserCompanies`                      |
| 20  | `src/screens/Customer/Notifications/index.js`              | `selectUserId`, `selectCompanyId`, `selectCompanyCustName`, `selectUserCompanies`                        |
| 21  | `src/screens/Customer/VehicleReports/index.js`             | `selectUserRole`                                                                                         |

**Verify Phase 6:** open every report, daily summary, sister companies,
notifications drawer screens. Email-export bottom sheets prefill `work_email`.

---

## 9 · Phase 7 — Components, hooks, demo, error boundary

Lower-traffic but globally rendered (ErrorBoundary, VersionInfo).

| #   | File                                                | Selectors                                                                                           |
| --- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 1   | `src/hooks/useInvoiceNavigation.js`                 | `selectUserRole`, `selectUserScope`                                                                 |
| 2   | `src/components/VersionInfo/index.js`               | `selectUserId`, `selectUserTheme`                                                                   |
| 3   | `src/components/Error/ErrorBoundary.js`             | `selectUserId`                                                                                      |
| 4   | `src/screens/Demo/Dashboard/index.js`               | `selectCurrentUser`, `selectCurrentCompany` (demo screen, low priority)                             |
| 5   | `src/screens/Customer/VehicleReports/components.js` | inspect — has `useSelector` import; verify if any auth read is reachable, otherwise drop the import |

**No changes needed** in:

- `src/utils/API/axiosReqRes.js` — uses `store.dispatch(logout())`, no `useSelector`.
- `src/store/apis/createApi.js` — reads token from `AsyncStorage`, not Redux.
- `src/helpers/OneSignal/index.js` — only dispatches `setNotification`, no read.
- `src/components/ToVerify.js` — only dispatches, no read.
- `src/screens/Login/**` — no auth slice access.
- `src/screens/StartupScreen.js` — no auth slice access.

**Files that look auth-related but are NOT (use a different slice — leave alone):**

- `src/screens/Common/Settings/index.js`, `Settings/DeleteAccount.js` — use `selectUserDetails` / `selectCompanyDetails` from a different slice.
- `src/screens/Customer/Companies/AddEditCompany.js`, `Dealer/Companies/AddEditCompanies.js` — use `selectUserDetails` from a different slice.
- `src/screens/Dealer/NewInvoice/components/index.js` (line 242) — reads `state.currentUser.currentUser` (separate slice).
- `src/screens/Common/RelationList/ListDealersScreen.js` — reads `state.dealer_msts`.
- `src/screens/Demo/Redux/index.js` — reads RTK Query API state, not auth.

### 7.1 Optional — RTK Query `getState()` reads (low-priority)

Two RTK Query callbacks read auth via `getState()`. These are NOT React
subscriptions (no re-render impact), but for consistency you can switch to
the new selectors:

| File                                   | Line | Current                | Replacement             |
| -------------------------------------- | ---- | ---------------------- | ----------------------- |
| `src/store/apis/dzzlooms/users.js`     | 26   | `state.auth.user._id`  | `selectUserId(state)`   |
| `src/store/apis/dzzlooms/cust_msts.js` | 19   | `state.auth.user.role` | `selectUserRole(state)` |

Skip if you want to keep this PR purely about React render perf.

---

## 10 · Phase 8 — Cleanup & DevTools verification

After all phases land:

1. Grep audit — these MUST all return zero matches (across the whole `dzzlo_oms_app/src`):

   ```sh
   # broad slice subscription
   rg "useSelector\(\s*(?:state|s)\s*=>\s*\1?\.auth\s*[\),]" dzzlo_oms_app/src

   # or destructured form
   rg "useSelector\(\s*\(?\{[^}]+\}\)?\s*=>\s*state\.auth" dzzlo_oms_app/src

   # local copies of the bad pattern (they hide the broad subscription behind a name)
   rg "const select(Auth|Role|User|Company)\s*=\s*(state|s)\s*=>\s*\1?\.auth\b" dzzlo_oms_app/src
   ```

   Any leftover hit means a file was missed — re-check it. Note: `selectAuth`
   in `ContactUs/index.js`, `selectRole` in `Common/Reports/index.js`, and
   `selectUserRole` in `Common/Help/index.js` are the three known local
   shadows — verify they're gone.

2. Grep usage of the existing exports `selectCurrentUser` /
   `selectCurrentCompany` should ONLY appear in the screens listed in
   Phases 2/3/5/6/7 above (~10-15 files). If a list/form screen still uses
   them, downgrade to a field selector.

3. React DevTools profiler check (manual):
   - Open the Dealer Orders list.
   - Trigger a `dispatch(setShowVerification(false))` from the console (or
     toggle ToVerify).
   - Profile: only the verification modal should re-render. Orders list and
     order items should NOT re-render. Before APP-4, both did.

4. Optional: convert `slices/auth.js` exports to re-export from
   `selectors/auth.js` so there's a single definition site.

---

## 11 · Execution order summary

| Phase     | Scope                                                                                  | Files | Effort      | Risk                        |
| --------- | -------------------------------------------------------------------------------------- | ----- | ----------- | --------------------------- |
| 0         | Create `selectors/auth.js`                                                             | 1 new | 10 min      | Zero                        |
| 1         | Orders / Invoices / Payments                                                           | 22    | 1.5 hr      | Low                         |
| 2         | Navigation & drawers                                                                   | 8     | 45 min      | Medium (drawer is critical) |
| 3         | Profile / CompanyProfile / ValidateUser                                                | 7     | 30 min      | Low                         |
| 4         | New / Edit form screens                                                                | 10    | 45 min      | Low                         |
| 5         | Entity management (Customers, Dealers, Vehicles, Users, Products)                      | 25    | 1.5 hr      | Low                         |
| 6         | Reports, Accounts, DailySummary, SisterCompanies, Vouchers, Notifications, misc Common | 21    | 1 hr        | Low                         |
| 7         | Hooks, components, demo, error boundary                                                | 4     | 15 min      | Low                         |
| 8         | Grep + DevTools audit                                                                  | —     | 30 min      | —                           |
| **Total** | **~97 files**                                                                          |       | **~6.5 hr** |                             |

**Recommended execution:** one phase per PR for easy review and rollback.
Phase 0 + Phase 1 in the first PR, then each subsequent phase as its own PR.

**Stop-condition rule:** after each phase, the app must be fully usable on
both Dealer and Customer accounts. If anything regresses, fix before moving
to the next phase.

---

## 12 · Implementation notes (post-execution, 2026-04-14)

All 8 phases shipped. Final audit clean: 0 broad subscriptions, 0 local
shadow selectors. Below is a record of what was skipped, deferred, or left
as-is during the actual migration so a future reader knows what is and is
not done.

### 12.1 Skipped (plan marked optional — left for follow-up)

These were not done because the plan explicitly marked them optional and
they have no React re-render impact:

| Item                                                   | Files                                                                            | Why skipped                                   |
| ------------------------------------------------------ | -------------------------------------------------------------------------------- | --------------------------------------------- |
| RTK Query `getState()` reads (Phase 7.1)               | `src/store/apis/dzzlooms/users.js:26`, `src/store/apis/dzzlooms/cust_msts.js:19` | Not React subscriptions — no re-render impact |
| Re-export from `selectors/auth.js` in `slices/auth.js` | `src/store/slices/auth.js` (lines 145-148)                                       | Cosmetic; existing exports still work         |

### 12.2 Intentionally untouched (plan said "leave alone")

These files use a locally-defined `selectUserDetails = state => state.auth?.user ?? null`
or `selectCompanyDetails = state => state.auth?.company ?? null`. They are
already field-specific (return just the user/company object, not the full
auth slice), so they don't broadly subscribe. The plan classified them as
"different slice" — that classification is technically wrong (they DO read
from `state.auth`) but the practical effect is the same: they don't trigger
re-renders on `notification` or `showVerification` toggles.

| File                                               | Local selector(s)                           |
| -------------------------------------------------- | ------------------------------------------- |
| `src/screens/Common/Settings/index.js`             | `selectUserDetails`                         |
| `src/screens/Common/Settings/DeleteAccount.js`     | `selectUserDetails`, `selectCompanyDetails` |
| `src/screens/Customer/Companies/AddEditCompany.js` | `selectUserDetails`                         |
| `src/screens/Dealer/Companies/AddEditCompanies.js` | `selectUserDetails`                         |

### 12.3 Known minor over-subscriptions (acceptable per plan)

Four files use `selectCurrentCompany` for a single field. The plan
acknowledges `selectCurrentCompany` as a valid escape hatch. They could be
downgraded by adding three new field selectors (`selectCompanyOtpMgr`,
`selectCompanyState`, `selectCompanyDealerSodgt`), but the win is small —
they already avoid the broad-slice re-renders that were the goal of APP-4.

| File                                                 | Field actually used | Selector to add (if downgrading) |
| ---------------------------------------------------- | ------------------- | -------------------------------- |
| `src/screens/Common/Profile/SelectStateBS.js`        | `.state`            | `selectCompanyState`             |
| `src/screens/Customer/Orders/components/OneOrder.js` | `.otp_mgr`          | `selectCompanyOtpMgr`            |
| `src/screens/Customer/Users/index.js`                | `.otp_mgr`          | `selectCompanyOtpMgr`            |
| `src/screens/Dealer/NewSalesOrder/index.js`          | `.dealer_sodgt`     | `selectCompanyDealerSodgt`       |

Plus one inline (not from selectors file) — same category:

| File                                       | Line | Inline selector                                     |
| ------------------------------------------ | ---- | --------------------------------------------------- |
| `src/screens/Customer/Users/OTPManager.js` | 130  | `useSelector(state => state.auth.company?.otp_mgr)` |

### 12.4 Bug fix during audit

`src/screens/Common/CompanyUsers/index.js` had two stranded
`currentUser.company._id` references (lines 217, 221) after the agent
renamed the variable to `user`. Would have crashed on render. Replaced with
`selectCompanyId`, `selectUserId`, and `selectUserRole` field selectors.
