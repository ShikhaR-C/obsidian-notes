# Phase 2 — User-Activity Instrumentation

**Outcome:** real business events fire from screens. Roll out in small slices (auth → orders → invoices/payments → exports → engagement) so each PR is reviewable and individually shippable.

**Rule of thumb:** instrument at the **outcome** of an action (after the RTK Query mutation `.unwrap()` succeeds/fails), not on button press, so the event reflects what actually happened. The only press-time events are `*_viewed` for sub-views and pure navigation CTAs.

---

## 2.0 Where to put the call

RTK Query mutations are the natural seam. Pattern at every mutation call-site:

```js
import { EVENTS } from '../../config/events';
import { track } from '../../utils/analytics';

const onSubmit = async () => {
  try {
    const res = await createOrder(payload).unwrap();
    track(EVENTS.ORDER_CREATED, {
      order_id: res?.id,
      order_type: 'sales',
      item_count: payload.items?.length,
      amount: payload.total,           // number, not currency-formatted string
    });
  } catch (err) {
    track(EVENTS.ORDER_CREATE_FAILED, { reason: err?.status ?? 'unknown' });
    // existing error UI unchanged
  }
};
```

> Do **not** await `track()`. Do **not** put PII (names, phone, GST numbers) in params — ids and counts only.

> **On `*_viewed` events:** every catalog `*_viewed` whose screen is a **navigation route** (`new_order_viewed`, `new_sales_order_viewed`, `new_payment_viewed`, `new_invoice_viewed`, `product_dates_viewed`, `validate_user_viewed`, `report_viewed`, `daily_summary_viewed`, `settings_viewed`, `auth_screen_viewed`) is **optional** — the auto screen-view tracker in `RestartContext.js` already logs a `screen_view` for it (see `00-overview` gotcha). They appear in the tables below for completeness; implement one only if you want an explicit funnel-entry marker distinct from the raw `screen_view`. Always-implement `*_viewed` are the **sub-view** ones (bottom sheets / modals that aren't routes), e.g. `sister_company_viewed`.

---

## 2.1 Slice A — Auth funnel

Files: `src/screens/Login/AuthNavigator/{Login,Welcome,ForgotPassword,BetaUser,Customer,Dealer}.js`, plus auth API in `src/store/apis/dzzlooms/auth.js`.

| Trigger | Event | Key params |
| --- | --- | --- |
| Login screen mount | `auth_screen_viewed` | `source: SCREENS.AUTH_LOGIN` |
| Beta-user signup submit | `beta_user_submitted` | `role` |
| ValidateUser screen mount | `validate_user_viewed` | — |
| Active company selected (multi-company login) | `company_selected` | `company_id` |
| Submit credentials | `login_attempted` | `method: 'password' \| 'otp'` |
| Login mutation success | `login_succeeded` | `role` |
| Login mutation 4xx | `login_failed` | `reason: status` |
| OTP requested | `otp_requested` | — |
| OTP verified | `otp_verified` | — |
| OTP wrong | `otp_failed` | `attempt` |
| Forgot-password submit | `forgot_password_submitted` | — |
| Reset-password success | `password_reset_submitted` | — |
| User verification done (ValidateUser) | `user_verification_completed` | `method` |
| Logout | `logout` | `trigger: 'manual' \| 'auto'` |

> **Logout location (correction):** logout is **not** in Settings. Manual logout lives in the drawer (`src/navigation/{Customer,Dealer}/DrawerContent.js` ~L208–223 → `logout()` thunk); the same thunk also fires **automatically** on 401 (`rtkQueryErrorLogger.js`) and from `StartupScreen.js`. Instrument the **`logoutUser` thunk** (`src/store/slices/auth.js`) once, with a `trigger` param, so all paths are covered — and fire the event **before** `clearUserContext()` runs so it still carries the user context.

> `auth_screen_viewed` is **optional** — the `Login`/`Welcome` routes already emit a `screen_view` via the auto-tracker in `RestartContext.js` (see `00-overview` gotcha on not double-counting). Add it only if you want an explicit funnel-entry marker distinct from the raw screen_view; otherwise rely on the auto screen_view and start the funnel at `login_attempted`.

**Also wire `setUserContext`** on login success (replaces the bare `setUser` in `AppNavigatorContainer.js:73`):

```js
// AppNavigatorContainer.js — replace setUser(userId) effect body.
// All selectors below ALREADY EXIST in src/store/selectors/auth.js.
const companyId = useSelector(selectCompanyId);          // auth.company?._id
const accountVerified = useSelector(                     // role-appropriate flag
  userRole === 'dealer' ? selectCompanyDealerVerified : selectCompanyCustVerified,
);
const scope = useSelector(selectUserScope);              // auth.user?.scope

useEffect(() => {
  if (userId) {
    setOneSignalExtId(userId);
    setUserContext({ userId, role: userRole, companyId, accountVerified, scope });
  } else {
    // logout / 401 auto-logout / account deletion — stop attributing events
    // and crashes to the old user & tenant (see 00-overview risks).
    clearUserContext();
  }
}, [userId, userRole, companyId, accountVerified, scope]);
```

> No new selectors needed: `selectCompanyId`, `selectCompanyDealerVerified`, `selectCompanyCustVerified`, `selectUserScope` all exist. There is **no** `selectUserStatus` — the earlier draft was wrong; use the verified flag (see `00-overview` user-properties table). Selecting a hook conditionally as shown is fine because `userRole` is stable for the session; if you prefer, select both flags and pick in the effect.

---

## 2.2 Slice B — Orders & Sales orders

Files: `src/screens/Customer/NewOrder/index.js`, `src/screens/Dealer/NewSalesOrder/index.js`, `src/screens/Dealer/EditSalesOrder/index.js`, `src/screens/{Customer,Dealer}/Orders/...`, APIs `order_msts.js` / `so_msts.js`.

| Trigger | Event | Params |
| --- | --- | --- |
| NewOrder mount | `new_order_viewed` | `source` |
| Create order success | `order_created` (+ `first_order_created` on first) | `order_id, item_count, amount, dealer_id` |
| Create order fail | `order_create_failed` | `reason` |
| Order processed (delivery/checkout) | `order_processed` | `order_id` |
| Status change (verify/cancel) | `order_status_changed` | `order_id, from, to` |
| Order deleted | `order_deleted` | `order_id` |
| Order OTP verified | `order_otp_verified` | `order_id` |
| Emergency OTP used | `emergency_otp_used` | `order_id` |
| NewSalesOrder mount | `new_sales_order_viewed` | `source` |
| Sales order create | `sales_order_created` | `so_id, item_count, amount` |
| Sales order edit save | `sales_order_edited` | `so_id` |
| Sales order deleted | `sales_order_deleted` | `so_id` |

**Milestone pattern** (`first_order_created`): keep a persisted counter to fire exactly once.

```js
// helpers/milestones.js
import AsyncStorage from '@react-native-async-storage/async-storage';
import { track } from '../utils/analytics';

// The key MUST be account-scoped (userId + companyId): an unscoped key is
// device-wide, so on a shared device or after a company switch the milestone
// fires for the wrong account — and "first action" leaks across accounts.
export const fireFirstTime = async (storageKey, event, params) => {
  const seen = await AsyncStorage.getItem(storageKey);
  if (!seen) {
    await AsyncStorage.setItem(storageKey, '1');
    track(event, params);
  }
};
// usage after order_created (userId/companyId from the auth selectors):
fireFirstTime(`milestone_first_order_${userId}_${companyId}`, EVENTS.FIRST_ORDER_CREATED, { order_id });
```

---

## 2.3 Slice C — Invoices, Payments, Vouchers

Files: `src/screens/Dealer/NewInvoice/index.js`, `src/screens/Customer/NewPayment/index.js`, `src/screens/Dealer/NewVoucher/index.js`, `_Invoice_/EmailBS.js`, `_Voucher_/`, APIs `invs.js` / `voc_msts.js`.

> **Correction (2026-07-02 code audit):** the earlier draft said PDF generation is centralised in `src/components/Download/`. **That folder is dead code — zero external importers** (its `RNhtmlpdf.js`/`Invoice.js`/`invoiceHTML/` only import each other; the `Share`/`rn-fetch-blob` code inside is commented out or unused), and the one other `RNHTMLtoPDF` import in the app (`Reports/TcsTds/Render/index.js:5`) never calls `.convert()`. **There is no live client-side PDF / file-download / share path.** Invoices actually render as **HTML in a WebView**: `src/screens/Common/_Invoice_/Render.js` (templates from `src/helpers/Download/…`), used by the Invoice screen, `NewInvSummary`, `SummaryModal`, and `InvoiceDetailsBSM`. So instrument **`invoice_rendered {format}` once in `_Invoice_/Render.js`** (covers all callers) and treat `email_inv` as the export signal. Re-introduce PDF/download events only if a real download/share feature ships.

| Trigger | Event | Params | Where |
| --- | --- | --- | --- |
| New invoice mount | `new_invoice_viewed` | `source` | screen |
| Invoice created | `invoice_created` (+ `first_invoice_created`) | `invoice_id, line_count, amount` | `invs.js` `add_invs` |
| Invoice updated | `invoice_updated` | `invoice_id` | `invs.js` `update_invs` |
| Invoice email sent | `invoice_emailed` | `invoice_id` | `EmailBS.js` `email_inv` |
| Invoice rendered (WebView) | `invoice_rendered` | `invoice_id, format: 'Normal'\|'Detailed'\|'Excel'\|'GST'` | `_Invoice_/Render.js` (single site, all callers) |
| NewPayment mount | `new_payment_viewed` | `source` | screen |
| Payment recorded | `payment_recorded` (+ `first_payment_recorded`) | `voucher_id, amount, method` | `voc_msts.js` `add_*_voc_msts` |
| Payment failed | `payment_failed` | `reason` | mutation `.catch` |
| Payment/voucher status change | `payment_status_changed` | `voucher_id, status` | `voc_msts.js` `updateVocStatus` |
| Paytm flow start | `paytm_initiated` | `amount` | `NewPayment/Paytm.js` |
| Voucher created | `voucher_created` | `voucher_id, amount, voucher_type` | `voc_msts.js` |
| Voucher email sent | `voucher_emailed` | `voucher_id` | `voc_msts.js` `email_voc` |
| Invoices attached to payment | `invoices_attached_to_payment` | `count` | `voc_msts.js` `attachInvoices` |

---

## 2.4 Slice D — Reports & Renders

Files: `src/screens/Common/Reports/...`, `Accounts/Render/` (`index.js` + `xlsxYearAcc.js`), `DailySummary/`, `TcsTds/Render/`, vehicle reports.

> **Correction (2026-07-02 code audit):** `excel_exported` / `pdf_exported` dropped — there is **no file export**. "Excel" is an HTML render format (`Accounts/Render/index.js` picks `xlsxYearAcc(...)` HTML when `invFormat === 'Excel'` and shows it in a WebView; same pattern as `xlsxInvSummary` for invoices), and no live `RNHTMLtoPDF.convert` call exists anywhere (see §2.3). Carry a `format` param on the `*_viewed` events instead; re-add export events if a save/share feature ships.

| Trigger | Event | Params |
| --- | --- | --- |
| Report screen mount | `report_viewed` | `report_type` |
| Daily summary viewed | `daily_summary_viewed` | — |
| Account statement viewed/rendered | `account_statement_viewed` | `range_days, format: 'Normal'\|'Excel'` |
| Account statement emailed | `account_statement_emailed` | `relation_id` |

Statement/report renders are high-value activation signals — prioritise this slice for the usage dashboard. (`account_statement_emailed` → `dealer_custs.js` `email_acc`. The TCS/TDS report also has an email endpoint — `emailMonthCompanyTcsTds` in `store/apis/balance/SectionalAcc.js` — if a `tcs_tds_report_emailed` event is wanted later.)

---

## 2.5 Slice E — Relations, Products, Vehicles, Company, Users

Broken into sub-tables by domain. Files: `dealer_custs.js`, `cust_msts.js`, `dealer_msts.js`, `prod_msts.js`, `psocs.js`, `veh_msts.js`, `dvr_msts.js`, `veh_reqs.js`, `users.js`, `invites.js`, `others.js`, and the matching screens under `src/screens/{Customer,Dealer}/`.

**Relations / credit**

| Trigger | Event | Params | Endpoint |
| --- | --- | --- | --- |
| Dealer/customer added | `dealer_added` / `customer_added` | `relation_id` | `add_dealer_custs` |
| Relation discount set | `discount_set` | `relation_id, pct` | `update_dealer_custs` |
| Credit limit changed | `credit_limit_changed` | `relation_id` | `update_dealer_custs` (CreditLimitBS) |
| TCS/TDS settings saved | `tcs_tds_settings_saved` | — | `update_dealer_custs` (TCSTDSSettings) |
| Opening balance set | `opening_balance_set` | `relation_id` | `update_first_bal_dealer_custs` |

**Products / rates** (dealer)

| Trigger | Event | Params | Endpoint |
| --- | --- | --- | --- |
| ProductDates mount | `product_dates_viewed` | `source` | screen |
| Product created | `product_created` | `product_id` | `add_prod_msts` |
| Product updated | `product_updated` | `product_id` | `update_prod_msts` (UpdateProd) |
| Product rate set | `product_rate_set` | `product_id, rate` | `add_rate_msts` / `update_rate_msts` |
| Product discount set | `product_discount_set` | `product_id, pct` | `add_prod_disc` / `edit_prod_disc` |
| PSOC products imported | `psoc_products_imported` | `count` | `import_psoc_prods` |

**Vehicles / drivers** (customer)

| Trigger | Event | Params | Endpoint |
| --- | --- | --- | --- |
| Vehicle added | `vehicle_added` | `vehicle_id` | `add_veh_msts` |
| Driver added | `driver_added` | — | `add_dvr_msts` / `add_dvr_cust` |
| Driver assigned / freed | `driver_assigned` / `driver_freed` | `vehicle_id` | `replaceDriver` / `freeDriver` |
| Vehicle request created | `vehicle_request_created` | `request_type: 'hire'\|'rent'` | `add_veh_req` |
| Vehicle request accepted | `vehicle_request_accepted` | `request_type` | `accept_hire_veh_req` / `accept_own_veh_req` |

**Company / sister companies / users**

| Trigger | Event | Params | Endpoint |
| --- | --- | --- | --- |
| Company switch | `company_switched` | `company_id` → **also call `setUserContext`** | `switch_sister_*_msts` |
| Sister company viewed | `sister_company_viewed` | — | screen |
| Sister company added | `sister_company_added` | `company_id` | `add_sister_*_msts` |
| Company deleted | `company_deleted` | `company_id` | `delete_company` |
| User invited | `user_invited` | `target_role` | `add_invite` |
| Invite accepted / declined | `invite_accepted` / `invite_declined` | — | `accept_invite` / `decline_invite` |
| User added | `user_added` | `target_role` | `add_users` |
| User status changed | `user_status_changed` | `target_status` | `activate_users` / `inactivate_users` / `remove_users` |

> **Company switch must re-set context.** When the active company changes, call `setUserContext({ ..., companyId })` so subsequent events/crashes carry the new `company_id`.

---

## 2.6 Slice F — Engagement / UX

| Trigger | Event | Params | Note |
| --- | --- | --- | --- |
| Search submitted | `search_performed` | `screen, has_results` | **on submit, not per keystroke** |
| Filter applied | `filter_applied` | `screen, filter_keys` | join keys with `,` |
| Theme changed | `theme_changed` | `theme: 'DARK'\|'LIGHT'\|'SYSTEM'` | Settings |
| Pull to refresh | `pull_to_refresh` | `screen` | only on lists with heavy refetch |
| Tab switch | `tab_switched` | `from, to` | optional; can be noisy |

Throttle/guard the noisy ones; ship them last and watch event volume in DebugView before prod.

---

## 2.7 Slice G — Settings & Account

Files: `src/screens/Common/Settings/index.js`, `Settings/DeleteAccount.js`, `src/screens/Common/ContactUs/index.js`, API `others.js`.

| Trigger | Event | Params | Endpoint / source |
| --- | --- | --- | --- |
| Settings opened | `settings_viewed` | — | screen (or rely on auto screen_view) |
| Delete-account flow started | `delete_account_initiated` | — | DeleteAccount.js |
| Delete-account confirmed | `delete_account_confirmed` | — | `others.js` `delete_account` — fire the event, **then** `clearUserContext()` (stop attributing the deleted account) |
| Contact-us submitted | `contact_us_submitted` | — | `others.js` `add_contact_us` |

> **`codepush_checked` dropped (correction):** `react-native-code-push` is not in `package.json`, and `Settings/Codepush.js` is unreferenced dead code (its import would fail to resolve if mounted). Re-add the event if CodePush actually ships.

> `theme_changed` (`others.js` `set_theme`) lives in Slice F. `delete_account_confirmed` is a churn signal — mark it a conversion in GA4 (Phase 4) alongside the activation events.

## 2.8 App lifecycle (lightweight)

`app_opened` and `time_to_interactive` are **not** mutation-driven — wire them once in the startup path (`AppNavigatorContainer.js` mount effect / `StartupScreen.js`), not per screen. `time_to_interactive` pairs naturally with the existing `startTrace` perf helper. These are optional; ship after the funnels are validated.

---

## Rollout order & PR slicing

1. PR-1: Slice A (auth) + `setUserContext` wiring. ← highest signal, validates the whole pipeline.
2. PR-2: Slice B (orders).
3. PR-3: Slice C (invoices/payments).
4. PR-4: Slice D (exports).
5. PR-5: Slice E (relations/products/vehicles/company/users) — large; split further by sub-table if review gets heavy.
6. PR-6: Slices F + G (engagement, settings/account) + 2.8 lifecycle.

Each PR: verify in Firebase **DebugView** (Phase 4) before merge.

---

## Phase 2 checklist

- [ ] `setUserContext` replaces bare `setUser` on login + company switch; `clearUserContext()` fires on auth reset (manual logout, 401 auto-logout, account deletion).
- [ ] `logout` event instrumented in the `logoutUser` thunk (`src/store/slices/auth.js`) with `trigger: 'manual' | 'auto'`, fired **before** `clearUserContext()`.
- [ ] `helpers/milestones.js` `fireFirstTime` created with **account-scoped keys** (`…_${userId}_${companyId}`) and used for the 3 `first_*` events.
- [ ] All slices wired per tables: A (auth) · B (orders) · C (invoices/payments) · D (exports) · E (relations/products/vehicles/company/users) · F (engagement) · G (settings/account) · 2.8 (lifecycle).
- [ ] Every catalog event in `events.js` has a home: an instrumentation site in a slice above, in **Phase 3** (`error_boundary_triggered`, `api_error`, `network_lost`, `network_restored`), or intentionally left to `api_call` — no orphan catalog entries.
- [ ] No PII in any param (review every `track()` call).
- [ ] `search_performed` fires on submit, not keystroke.
- [ ] Each slice verified in DebugView.
